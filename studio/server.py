"""Local-only video studio. Run with the project's existing Python environment."""
from pathlib import Path
import copy,json,os,queue,re,subprocess,sys,threading,time,uuid
from contextlib import asynccontextmanager
from fastapi import FastAPI,HTTPException,Request
from fastapi.responses import FileResponse,JSONResponse,Response
from fastapi.staticfiles import StaticFiles
from starlette.middleware.trustedhost import TrustedHostMiddleware
import requests
from batches import VideoSettings,VideoRequest,BatchRequest,VOICES,MAX_PENDING,validate_batch,batch_summary

from config import ROOT,DATA,JOBS,MODELS,VOICE,VOICE_PYTHON,PORT,OLLAMA_URL,OLLAMA_MODEL
HERE=Path(__file__).resolve().parent
DATA.mkdir(parents=True,exist_ok=True);JOBS.mkdir(parents=True,exist_ok=True)
LOCK=threading.RLock();PENDING=queue.Queue();ACTIVE={};STATE=DATA/'state.json'
def atomic(path,data):
    temp=path.with_suffix('.tmp');temp.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8');temp.replace(path)
state=json.loads(STATE.read_text(encoding='utf-8')) if STATE.exists() else {'settings':{'theme':'dark','duration':90,'format':'reel'},'jobs':[]}
state.setdefault('batches',[])
state['settings'].setdefault('voice','Narrateur-Homme-01')
for j in state['jobs']:
    if j['status'] in ['queued','running']:
        j.update(status='interrupted',message='Le studio a été arrêté. Vous pouvez relancer cette vidéo.')
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
                    if code==0 and (JOBS/key/'Video.mp4').exists():update(key,status='done',stage='done',progress=100,message='Votre vidéo est prête.')
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
    save();threading.Thread(target=worker,daemon=True).start();yield
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
        if sum(j['status'] in ['queued','running'] for j in state['jobs'])+len(items)>MAX_PENDING:raise HTTPException(409,f'La file accepte au maximum {MAX_PENDING} vidéos en cours ou en attente.')
        jobs=[];folders=[];previous=copy.deepcopy(state)
        try:
            for index,payload in enumerate(items):
                key=uuid.uuid4().hex;folder=JOBS/key;folder.mkdir();folders.append(folder);atomic(folder/'Request.json',payload)
                job={'id':key,**payload,'status':'queued','stage':'queued','progress':0,'message':'En attente de génération.','created':time.time(),'updated':time.time()}
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
    if not re.fullmatch('[0-9a-f]{32}',key) or name not in ['Video.mp4','Poster.jpg','Narration.wav','Scenario.json','Sous-titres.srt','generation.log','Verification.json']:raise HTTPException(404)
    path=JOBS/key/name
    if not path.is_file():raise HTTPException(404,'Fichier pas encore disponible.')
    return FileResponse(path,filename=name if download else None,media_type='video/mp4' if name=='Video.mp4' else None)
@app.get('/')
def index():return FileResponse(HERE/'static/index.html')
app.mount('/static',StaticFiles(directory=HERE/'static'),name='static')
if __name__=='__main__':
    import uvicorn
    uvicorn.run(app,host='127.0.0.1',port=PORT,log_level='warning')
