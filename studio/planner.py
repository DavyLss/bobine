"""Local bulk publication planner and streamed imports; no remote call before dispatch."""
import copy,json,math,shutil,subprocess,threading,time,uuid
from datetime import datetime,timezone
from pathlib import Path
from typing import Literal
from fastapi import HTTPException,Request
from pydantic import BaseModel,ConfigDict,Field
from starlette.concurrency import run_in_threadpool
from PIL import Image
import imageio_ffmpeg
import integrations,publishing
from social_assets import PublicationText,save_text

MAX_UPLOAD=500*1024*1024
ACTIVE={'waiting','overdue','dispatching','submitted','needs_attention'}
class PlanItem(BaseModel):
    model_config=ConfigDict(extra='forbid')
    job_id:str=Field(pattern=r'^[0-9a-f]{32}$')
    at:datetime|None=None
    metadata:PublicationText
class PlanBatch(BaseModel):
    model_config=ConfigDict(extra='forbid')
    platforms:list[Literal['youtube','instagram','tiktok']]=Field(min_length=1,max_length=3)
    items:list[PlanItem]=Field(min_length=1,max_length=50)
class PlanDate(BaseModel):
    at:datetime

def timestamp(value):
    if value is None:return time.time()
    if value.tzinfo is None:raise HTTPException(422,'La date doit inclure son fuseau horaire.')
    stamp=value.timestamp()
    if stamp<time.time()-5:raise HTTPException(422,'Choisir une date future.')
    return stamp

def public(plan):return {k:v for k,v in plan.items() if k!='accounts'}

def convert_import(folder,source):
    from moviepy import VideoFileClip
    try:
        with VideoFileClip(str(source),audio=False) as clip:
            duration=float(clip.duration);w,h=clip.size
            if not math.isfinite(duration) or not 0<duration<=600 or not 0<w<=8192 or not 0<h<=8192:raise ValueError('Durée maximale : 10 minutes ; dimensions maximales : 8192 px.')
            Image.fromarray(clip.get_frame(min(.1,duration/2))).convert('RGB').save(folder/'Poster.jpg',quality=90)
        result=subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-nostdin','-hide_banner','-loglevel','error','-y','-i',str(source),'-map','0:v:0','-map','0:a:0?','-map_metadata','-1','-map_chapters','-1','-vf',"scale='min(1920,iw)':'min(1920,ih)':force_original_aspect_ratio=decrease:force_divisible_by=2",'-c:v','libx264','-preset','fast','-crf','20','-pix_fmt','yuv420p','-r','30','-c:a','aac','-b:a','192k','-movflags','+faststart',str(folder/'Video.mp4')],capture_output=True,timeout=1800,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
        if result.returncode:raise ValueError('Vidéo illisible ou conversion MP4 impossible.')
        return duration,w,h
    except (OSError,subprocess.TimeoutExpired) as error:raise ValueError('Impossible de traiter cette vidéo dans le délai prévu.') from error

def install(app,s):
    s.state.setdefault('publication_plans',[])
    for plan in s.state['publication_plans']:
        if plan['status']=='dispatching':plan.update(status='needs_attention',message='Studio arrêté pendant un envoi. Contrôler les reçus avant toute autre action.')
        elif plan['status']=='waiting' and plan['at']<time.time():plan.update(status='overdue',message='Échéance dépassée pendant l’arrêt. Reprogrammer pour autoriser l’envoi.')
    s.IMPORT_LOCK=threading.Lock()

    @app.get('/api/publications')
    def listing():
        with s.LOCK:
            library=[]
            for job in s.state['jobs']:
                if job['status']!='done':continue
                p=s.JOBS/job['id']/'Publication.json'
                meta=json.loads(p.read_text(encoding='utf-8')) if p.exists() else None
                used=[name for name,target in publishing.load_report(s.JOBS/job['id'])['targets'].items() if target.get('post_id') or target.get('publish_attempted')]
                library.append({'used_platforms':used,'id':job['id'],'title':job['title'],'format':job['format'],'source':job.get('source','studio'),'metadata':meta})
            return {'plans':[public(p) for p in s.state['publication_plans']],'library':library,'enabled':integrations.load().get('enabled',False)}

    @app.post('/api/imports',status_code=201)
    async def upload(request:Request,filename:str='video.mp4'):
        suffix=Path(filename).suffix.lower()
        if suffix not in ['.mp4','.mov','.m4v','.webm','.mkv']:raise HTTPException(422,'Importer un MP4, MOV, M4V, WebM ou MKV.')
        if not s.IMPORT_LOCK.acquire(blocking=False):raise HTTPException(409,'Un import est déjà en cours. Attendre sa fin.')
        key=uuid.uuid4().hex;folder=s.JOBS/key;registered=False
        try:
            folder.mkdir();source=folder/('Source'+suffix);size=0
            with source.open('wb') as output:
                async for chunk in request.stream():
                    size+=len(chunk)
                    if size>MAX_UPLOAD:raise HTTPException(413,'500 Mo maximum par vidéo.')
                    output.write(chunk)
            if not size:raise HTTPException(422,'Fichier vide.')
            duration,w,h=await run_in_threadpool(convert_import,folder,source)
            title=Path(filename.replace('\\','/')).stem[:95].strip() or 'Vidéo importée'
            if len(title)<3:title='Vidéo '+title
            job={'id':key,'title':title,'description':'Vidéo importée depuis le poste.','theme':'dark','format':'reel' if h>w else 'standard','duration':round(duration),'actual_duration':duration,'status':'done','stage':'done','progress':100,'source':'import','created':time.time(),'updated':time.time(),'message':'Import et conversion MP4 terminés. Compléter les textes avant publication.'}
            s.atomic(folder/'Request.json',job)
            with s.LOCK:s.state['jobs'].insert(0,job);s.save();registered=True
            source.unlink()
            return job
        except ValueError as error:raise HTTPException(422,str(error)) from error
        finally:
            # This UUID folder belongs exclusively to this upload; user paths are never used.
            if not registered and folder.exists():
                if folder.resolve().parent!=s.JOBS.resolve():raise RuntimeError('Import cleanup path outside job directory.')
                shutil.rmtree(folder)
            s.IMPORT_LOCK.release()

    @app.post('/api/publications/plans',status_code=201)
    def create(body:PlanBatch):
        with s.LOCK:
            config=integrations.load();missing=integrations.missing(config,body.platforms)
            if missing:raise HTTPException(422,' '.join(missing))
            if len(set(i.job_id for i in body.items))!=len(body.items):raise HTTPException(422,'Une vidéo ne peut apparaître qu’une fois dans le lot.')
            if sum(p['status'] in ACTIVE for p in s.state['publication_plans'])+len(body.items)>500:raise HTTPException(409,'500 publications actives maximum.')
            stamps=[]
            for i,item in enumerate(body.items,1):
                job=s.find(item.job_id);out=s.JOBS/item.job_id
                if job['status']!='done' or not(out/'Video.mp4').is_file():raise HTTPException(422,f'Vidéo {i} : export non disponible.')
                if job['format']!='reel' and any(p!='youtube' for p in body.platforms):raise HTTPException(422,f'Vidéo {i} : format standard disponible pour YouTube seul ; importer une vidéo verticale pour Instagram/TikTok.')
                if item.job_id in s.SOCIAL_ACTIVE or any(p['job_id']==item.job_id and p['status'] in ACTIVE for p in s.state['publication_plans']):raise HTTPException(409,f'Vidéo {i} : préparation, envoi ou planification déjà active.')
                record=publishing.load_report(out)
                if any(record['targets'].get(p,{}).get('post_id') or record['targets'].get(p,{}).get('publish_attempted') for p in body.platforms):raise HTTPException(409,f'Vidéo {i} : un reçu ou une tentative existe déjà pour un réseau choisi. Contrôler les envois pour éviter un doublon.')
                stamps.append(timestamp(item.at))
            plans=[]
            for item,stamp in zip(body.items,stamps):
                job=s.find(item.job_id);save_text(s.JOBS/item.job_id,job,item.metadata.model_dump())
                plans.append({'id':uuid.uuid4().hex,'job_id':item.job_id,'title':item.metadata.title,'platforms':list(dict.fromkeys(body.platforms)),'at':stamp,'created':time.time(),'status':'waiting','message':'En attente de l’heure prévue.','accounts':publishing.account_ids(config)})
            s.state['publication_plans'].extend(plans);s.save()
            return {'plans':[public(p) for p in plans]}

    def find_plan(key):
        plan=next((p for p in s.state['publication_plans'] if p['id']==key),None)
        if not plan:raise HTTPException(404,'Planification introuvable.')
        return plan

    @app.delete('/api/publications/plans/{key}')
    def cancel(key:str):
        with s.LOCK:
            plan=find_plan(key)
            if plan['status'] not in ['waiting','overdue','error']:raise HTTPException(409,'Cet envoi est déjà engagé. Contrôler les reçus et le réseau concerné.')
            plan.update(status='cancelled',message='Planification annulée ; fichiers conservés.');s.save();return public(plan)

    @app.patch('/api/publications/plans/{key}')
    def reschedule(key:str,body:PlanDate):
        with s.LOCK:
            plan=find_plan(key)
            if plan['status'] not in ['waiting','overdue']:raise HTTPException(409,'Seule une publication en attente peut être déplacée.')
            plan.update(at=timestamp(body.at),status='waiting',message='Nouvelle date enregistrée.');s.save();return public(plan)


def tick(s):
    with s.LOCK:
        dirty=False
        for plan in s.state['publication_plans']:
            if plan['status']!='submitted':continue
            report=s.find(plan['job_id']).get('publication',{});targets=report.get('targets',{})
            statuses=[targets.get(p,{}).get('status','pending') for p in plan['platforms']]
            if all(v=='published' for v in statuses):plan.update(status='published',message='Publication confirmée sur tous les réseaux.');dirty=True
            elif any(v in ['error','uncertain','interrupted'] for v in statuses) or report.get('status')=='failed':
                details=' ; '.join(p+' : '+targets.get(p,{}).get('message','') for p in plan['platforms'] if targets.get(p,{}).get('status') in ['error','uncertain','interrupted'])
                plan.update(status='needs_attention',message=details or report.get('message','Contrôler les reçus avant toute nouvelle tentative.'));dirty=True
        for plan in sorted(s.state['publication_plans'],key=lambda p:(p['at'],p['created'])):
            if plan['status']!='waiting' or plan['at']>time.time():continue
            if not integrations.load().get('enabled'):continue
            if plan['job_id'] in s.SOCIAL_ACTIVE:continue
            if time.time()-plan['at']>300:
                plan.update(status='overdue',message='Échéance dépassée de plus de 5 minutes. Reprogrammer pour autoriser l’envoi.');dirty=True;continue
            plan.update(status='dispatching',message='Transmission à la file d’envoi.');s.save()
            try:
                s.queue_social(plan['job_id'],'publish',plan['platforms'],'now',plan['accounts'],plan_id=plan['id'])
                plan.update(status='submitted',message='Envoi engagé ; en attente des confirmations.');dirty=True
            except HTTPException as error:plan.update(status='error',message=str(error.detail));dirty=True
            except Exception as error:plan.update(status='needs_attention',message=integrations.clean_error(error));dirty=True
        if dirty:s.save()

def worker(s):
    while True:
        try:tick(s)
        except Exception as error:
            import logging
            logging.getLogger(__name__).warning('Planner check interrupted (%s)',type(error).__name__)
        time.sleep(2)
