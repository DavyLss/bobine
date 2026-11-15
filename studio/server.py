"""Local-only video studio. Run with the project's existing Python environment."""
from pathlib import Path
import copy,json,os,queue,re,subprocess,sys,threading,time,uuid
from contextlib import asynccontextmanager
from fastapi import FastAPI,HTTPException,Request
from fastapi.responses import FileResponse,JSONResponse,Response
from fastapi.staticfiles import StaticFiles
from starlette.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import HTMLResponse,RedirectResponse
from pydantic import BaseModel,Field
from typing import Literal
import requests
import integrations,publishing
from social_assets import PublicationText
from batches import VideoSettings,VideoRequest,BatchRequest,VOICES,MAX_PENDING,validate_batch,batch_summary

from config import ROOT,DATA,JOBS,MODELS,VOICE,VOICE_PYTHON,PORT,OLLAMA_URL,OLLAMA_MODEL
HERE=Path(__file__).resolve().parent
DATA.mkdir(parents=True,exist_ok=True);JOBS.mkdir(parents=True,exist_ok=True)
LOCK=threading.RLock();PENDING=queue.Queue();ACTIVE={};STATE=DATA/'state.json'
SOCIAL_PENDING=queue.Queue();SOCIAL_ACTIVE=set()
def atomic(path,data):
    temp=path.with_suffix('.tmp');temp.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8');temp.replace(path)
state=json.loads(STATE.read_text(encoding='utf-8')) if STATE.exists() else {'settings':{'theme':'dark','duration':90,'format':'reel'},'jobs':[]}
state.setdefault('batches',[])
state['settings'].setdefault('voice','Narrateur-Homme-01')
for j in state['jobs']:
    if j['status'] in ['queued','running']:
        j.update(status='interrupted',message='Le studio a été arrêté. Vous pouvez relancer cette vidéo.')
    if j.get('publication',{}).get('status') in ['queued','preparing','sending','uploading']:
        j['publication'].update(status='interrupted',message='Envoi interrompu. Contrôler les reçus avant une reprise manuelle.')
def save():atomic(STATE,state)
def find(key):
    job=next((j for j in state['jobs'] if j['id']==key),None)
    if job is None:raise HTTPException(404,'Vidéo introuvable.')
    return job
def update(key,**values):
    with LOCK:
        j=find(key);j.update(values);j['updated']=time.time();save()
def worker():
    while True:
        key=PENDING.get()
        process=None
        try:
            with LOCK:
                job=find(key)
                if job['status']!='queued':continue
                update(key,status='running',stage='scenario',message='Préparation du scénario…',progress=2)
                process=subprocess.Popen([sys.executable,'-u',str(HERE/'pipeline.py'),str(JOBS/key)],cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,encoding='utf-8',errors='replace',env={**os.environ,'PYTHONIOENCODING':'utf-8'},creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
                ACTIVE[key]=process
            with (JOBS/key/'generation.log').open('a',encoding='utf-8') as log:
                for line in process.stdout:
                    log.write(line);log.flush()
                    if line.startswith('@studio '):
                        try:event=json.loads(line[8:])
                        except json.JSONDecodeError:continue
                        if not isinstance(event,dict):continue
                        with LOCK:
                            if find(key)['status']=='running':update(key,**{k:v for k,v in event.items() if k in ['stage','message','progress','actual_duration','scene_count','warning']})
            code=process.wait()
            with LOCK:
                if find(key)['status']=='running':
                    if code==0 and (JOBS/key/'Video.mp4').exists():
                        update(key,status='done',stage='done',progress=100,message='Votre vidéo est prête.')
                        if find(key).get('auto_publish'):
                            try:queue_social(key,'publish',find(key)['publish_platforms'],find(key).get('publish_mode','queue'),find(key).get('publish_accounts'))
                            except HTTPException as error:update(key,publication={'status':'blocked','message':str(error.detail),'targets':{}})
                    else:
                        error=(JOBS/key/'error.txt').read_text(encoding='utf-8') if (JOBS/key/'error.txt').exists() else 'La génération a été interrompue. Consultez le journal pour le détail.'
                        update(key,status='failed',message=error[-1500:])
        except Exception as e:
            update(key,status='failed',message=str(e))
        finally:
            # Never release the queue while a pipeline is still alive after a reader/log error.
            if process is not None and process.poll() is None:process.communicate()
            ACTIVE.pop(key,None);PENDING.task_done()

@asynccontextmanager
async def lifespan(app):
    save();threading.Thread(target=worker,daemon=True).start();threading.Thread(target=social_worker,daemon=True).start();yield
app=FastAPI(lifespan=lifespan)
app.add_middleware(TrustedHostMiddleware,allowed_hosts=['127.0.0.1','localhost','testserver'])
@app.middleware('http')
async def local_write(request:Request,call_next):
    if request.method in ['POST','PUT','PATCH','DELETE']:
        if request.headers.get('x-studio-request')!='1':return JSONResponse({'detail':'Requête locale attendue.'},403)
        origin=request.headers.get('origin')
        if origin and origin not in [f'http://127.0.0.1:{PORT}',f'http://localhost:{PORT}']:return JSONResponse({'detail':'Origine refusée.'},403)
    return await call_next(request)
@app.get('/api/state')
def get_state():
    with LOCK:
        snapshot=copy.deepcopy(state)
        snapshot['batches']=[batch_summary(batch,snapshot['jobs']) for batch in snapshot['batches']]
        snapshot['voices']=VOICES
        return snapshot
@app.get('/api/health')
def health():
    try:
        result=requests.get(OLLAMA_URL+'/api/tags',timeout=2);result.raise_for_status();llm=any(m['name']==OLLAMA_MODEL for m in result.json()['models'])
    except requests.RequestException:llm=False
    voice=(VOICE/'Reference-Homme.wav').exists() and (MODELS/'Qwen3-TTS-1.7B-Base/model.safetensors').exists()
    voice=voice and VOICE_PYTHON.is_file()
    whisper=(MODELS/'whisper-base/model.bin').is_file()
    return {'llm':llm,'voice':voice,'whisper':whisper,'ready':llm and voice and whisper}
@app.post('/api/jobs',status_code=201)
def create(body:VideoRequest):
    return enqueue([body.model_dump()],body.model_dump(include=set(VideoSettings.model_fields)))[0]

def enqueue(items,settings,batch=None):
    """Persist the whole submission before exposing any item to the single worker."""
    with LOCK:
        config=integrations.load() if any(item.get('auto_publish') for item in items) else None
        if config:
            for item in items:
                if item.get('auto_publish'):
                    missing=integrations.missing(config,item['publish_platforms'])
                    if missing:raise HTTPException(422,' '.join(missing))
        if sum(j['status'] in ['queued','running'] for j in state['jobs'])+len(items)>MAX_PENDING:raise HTTPException(409,f'La file accepte au maximum {MAX_PENDING} vidéos en cours ou en attente.')
        jobs=[];folders=[];previous=copy.deepcopy(state)
        try:
            for index,payload in enumerate(items):
                key=uuid.uuid4().hex;folder=JOBS/key;folder.mkdir();folders.append(folder);atomic(folder/'Request.json',payload)
                job={'id':key,**payload,'status':'queued','stage':'queued','progress':0,'message':'En attente de génération.','created':time.time(),'updated':time.time()}
                if payload.get('auto_publish'):job['publish_accounts']=publishing.account_ids(config)
                if batch:job.update(batch_id=batch['id'],batch_index=index+1)
                jobs.append(job)
            state['jobs'][0:0]=jobs
            if batch:state['batches'].insert(0,batch)
            state['settings']=settings;save()
        except Exception:
            state.clear();state.update(previous)
            for folder in folders:
                for child in folder.iterdir():child.unlink()
                folder.rmdir()
            raise
        for job in jobs:PENDING.put(job['id'])
        return copy.deepcopy(jobs)

def batch_items(body):
    try:return validate_batch(body)
    except ValueError as error:raise HTTPException(422,str(error)) from error

@app.get('/api/batches/template.csv')
def csv_template():
    content='titre;description;charte;duree;format;voix\r\nC’est quoi le DevOps ?;Expliquer la collaboration avec un exemple concret.;;;;\r\nLes trois voies du DevOps;Expliquer le flux, le feedback et l’apprentissage continu.;light;60;reel;Narrateur-Homme-01\r\n'
    return Response('\ufeff'+content,media_type='text/csv; charset=utf-8',headers={'Content-Disposition':'attachment; filename="modele-videos.csv"'})

@app.post('/api/batches/preview')
def preview_batch(body:BatchRequest):
    items,lines=batch_items(body)
    return {'items':items,'lines':lines,'total':len(items)}

@app.post('/api/batches',status_code=201)
def create_batch(body:BatchRequest):
    items,_=batch_items(body)
    batch={'id':uuid.uuid4().hex,'name':body.name.strip() or f'Lot de {len(items)} vidéos','created':time.time(),'defaults':body.defaults.model_dump()}
    jobs=enqueue(items,body.defaults.model_dump(),batch)
    return batch_summary(batch,jobs)

def find_batch(key):
    batch=next((batch for batch in state['batches'] if batch['id']==key),None)
    if batch is None:raise HTTPException(404,'Lot introuvable.')
    return batch

@app.post('/api/batches/{key}/cancel-pending')
def cancel_pending(key:str):
    with LOCK:
        batch=find_batch(key)
        for job in state['jobs']:
            if job.get('batch_id')==key and job['status']=='queued':job.update(status='cancelled',message='Annulée avant génération.',updated=time.time())
        save();return batch_summary(batch,state['jobs'])

@app.post('/api/batches/{key}/retry',status_code=201)
def retry_batch(key:str):
    with LOCK:
        batch=find_batch(key)
        jobs=sorted((job for job in state['jobs'] if job.get('batch_id')==key and job['status'] in ['failed','interrupted']),key=lambda job:job['batch_index'])
        if not jobs:raise HTTPException(409,'Aucun échec à relancer dans ce lot.')
        items=[VideoRequest.model_validate({field:job.get(field,'Narrateur-Homme-01') for field in VideoRequest.model_fields}).model_dump() for job in jobs]
        new={'id':uuid.uuid4().hex,'name':('Reprise · '+batch['name'])[:120],'created':time.time(),'defaults':batch['defaults']}
        return batch_summary(new,enqueue(items,new['defaults'],new))
@app.post('/api/jobs/{key}/cancel')
def cancel(key:str):
    with LOCK:
        job=find(key)
        if job['status'] not in ['queued','running']:raise HTTPException(409,'Cette génération est déjà terminée.')
        process=ACTIVE.get(key)
        update(key,status='cancelled',message='Génération annulée. Les fichiers intermédiaires sont conservés.')
        if process and process.poll() is None:
            if os.name=='nt':subprocess.run(['taskkill','/PID',str(process.pid),'/T','/F'],capture_output=True,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
            else:process.terminate()
    return {'ok':True}
@app.get('/api/jobs/{key}/files/{name}')
def file(key:str,name:str,download:bool=False):
    with LOCK:find(key)
    if not re.fullmatch('[0-9a-f]{32}',key) or name not in ['Video.mp4','Poster.jpg','Narration.wav','Scenario.json','Sous-titres.srt','generation.log','Verification.json','Publication.json','Publication.txt','Miniature-Reel.jpg','Miniature-YouTube.jpg']:raise HTTPException(404)
    path=JOBS/key/name
    if not path.is_file():raise HTTPException(404,'Fichier pas encore disponible.')
    return FileResponse(path,filename=name if download else None,media_type='video/mp4' if name=='Video.mp4' else None)

def queue_social(key,action,platforms=None,mode='queue',accounts=None):
    with LOCK:
        job=find(key)
        if job['status']!='done':raise HTTPException(409,'Attendre la fin de la vidéo.')
        if key in SOCIAL_ACTIVE:raise HTTPException(409,'Une préparation ou un envoi est déjà en cours pour cette vidéo.')
        if action=='publish':
            if job['format']!='reel':raise HTTPException(422,'Sélectionner une vidéo au format Reel pour ces publications.')
            missing=integrations.missing(integrations.load(),platforms or [])
            if missing:raise HTTPException(422,' '.join(missing))
            if not (JOBS/key/'Publication.json').is_file():raise HTTPException(422,'Générer le kit local avant publication.')
        report=publishing.public_report(publishing.load_report(JOBS/key));report.update(status='queued',message='Préparation locale en attente.' if action=='prepare' else 'Envoi en attente.');update(key,publication=report)
        SOCIAL_ACTIVE.add(key)
        SOCIAL_PENDING.put((key,action,platforms,mode,accounts));return report

def social_worker():
    while True:
        try:task=SOCIAL_PENDING.get(timeout=30)
        except queue.Empty:
            if not integrations.load().get('enabled'):continue
            with LOCK:
                candidates=sorted((job for job in state['jobs'] if job.get('publication',{}).get('status') in ['submitted','needs_attention'] and time.time()-job.get('publication',{}).get('last_checked',0)>60 and job['id'] not in SOCIAL_ACTIVE),key=lambda job:job.get('publication',{}).get('last_checked',0))[:3]
                for job in candidates:
                    SOCIAL_ACTIVE.add(job['id']);SOCIAL_PENDING.put((job['id'],'refresh',None,'queue',None))
            continue
        key,action,platforms,mode,accounts=task
        try:
            out=JOBS/key
            changed=lambda report:update(key,publication=report)
            if action=='prepare':
                update(key,publication={**find(key).get('publication',{}),'status':'preparing','message':'Création locale des textes et miniatures…'})
                from social_assets import create
                create(out)
                report=publishing.public_report(publishing.load_report(out));report.update(message='Kit local prêt.',status=publishing.summarize(report));changed(report)
            elif action=='publish':publishing.run(out,platforms,mode,changed,accounts)
            else:publishing.refresh(out,changed)
        except Exception as error:
            report=publishing.public_report(publishing.load_report(JOBS/key));report.update(status='failed',message=integrations.clean_error(error,integrations.load()));update(key,publication=report)
        finally:
            with LOCK:SOCIAL_ACTIVE.discard(key)
            SOCIAL_PENDING.task_done()

class PublishInput(BaseModel):
    platforms:list[Literal['youtube','instagram','tiktok']]=Field(min_length=1,max_length=3)
    mode:Literal['queue','now']='queue'

@app.get('/api/social/settings')
def social_settings():return integrations.public_settings()

@app.put('/api/social/settings')
def save_social_settings(body:integrations.SettingsInput):return integrations.save_settings(body)

@app.post('/api/social/test/{service}')
def test_social(service:str):
    try:return integrations.test_connection(service)
    except (ValueError,RuntimeError,KeyError) as error:raise HTTPException(422,integrations.clean_error(error,integrations.load())) from error

@app.post('/api/social/youtube/connect')
def youtube_connect():
    try:return integrations.youtube_authorize()
    except (ValueError,RuntimeError) as error:raise HTTPException(422,str(error)) from error

@app.post('/api/social/instagram/long-lived')
def instagram_long_lived():
    try:return integrations.instagram_exchange()
    except (ValueError,RuntimeError) as error:raise HTTPException(422,integrations.clean_error(error,integrations.load())) from error

@app.get('/api/social/youtube/callback')
def youtube_callback(code:str='',state:str='',error:str=''):
    try:
        if error:raise ValueError('Autorisation Google refusée. Relancer depuis le studio.')
        integrations.youtube_callback(code,state)
        return RedirectResponse('/?youtube=connected#publication-settings',status_code=303,headers={'Referrer-Policy':'no-referrer'})
    except (ValueError,RuntimeError) as failure:
        import html
        return HTMLResponse('<h1>Connexion YouTube interrompue</h1><p>'+html.escape(integrations.clean_error(failure,integrations.load()))+'</p><a href="/#publication-settings">Retour au studio</a>',status_code=400,headers={'Referrer-Policy':'no-referrer'})

@app.get('/api/jobs/{key}/social')
def get_social(key:str):
    with LOCK:
        job=copy.deepcopy(find(key));out=JOBS/key
        metadata=json.loads((out/'Publication.json').read_text(encoding='utf-8')) if (out/'Publication.json').exists() else None
        return {'metadata':metadata,'publication':job.get('publication',publishing.public_report(publishing.load_report(out))),'busy':key in SOCIAL_ACTIVE}

@app.post('/api/jobs/{key}/social/prepare',status_code=202)
def prepare_social(key:str):return queue_social(key,'prepare')

@app.put('/api/jobs/{key}/social/metadata')
def edit_social(key:str,body:PublicationText):
    with LOCK:
        job=find(key)
        if job['status']!='done' or key in SOCIAL_ACTIVE:raise HTTPException(409,'Attendre la fin de la préparation ou de l’envoi.')
        from social_assets import save_text
        return save_text(JOBS/key,job,body.model_dump())

@app.post('/api/jobs/{key}/social/publish',status_code=202)
def publish_social(key:str,body:PublishInput):
    return queue_social(key,'publish',list(dict.fromkeys(body.platforms)),body.mode)

@app.post('/api/jobs/{key}/social/refresh',status_code=202)
def refresh_social(key:str):return queue_social(key,'refresh')

@app.get('/api/social/guide')
def social_guide():return FileResponse(ROOT/'docs/PUBLICATION.md',media_type='text/plain; charset=utf-8')
@app.get('/')
def index():return FileResponse(HERE/'static/index.html')
app.mount('/static',StaticFiles(directory=HERE/'static'),name='static')
if __name__=='__main__':
    import uvicorn
    uvicorn.run(app,host='127.0.0.1',port=PORT,log_level='warning')
