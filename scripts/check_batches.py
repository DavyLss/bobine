"""Real API + subprocess queue regression checks, without running AI models."""
import os,sys,tempfile,json,time,subprocess
from pathlib import Path
from fastapi.testclient import TestClient
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'studio'))

with tempfile.TemporaryDirectory() as directory:
    root=Path(directory)
    os.environ.update(STUDIO_DATA_DIR=str(root/'state'),STUDIO_JOBS_DIR=str(root/'jobs'),STUDIO_PORT='8512')
    import server
    from batches import BatchRequest,validate_batch
    defaults={'theme':'light','duration':45,'format':'standard','voice':'Narrateur-Homme-01'}
    headers={'X-Studio-Request':'1','Origin':'http://127.0.0.1:8512'}
    fake=root/'fake_pipeline.py'
    fake.write_text('''import sys,json,time
from pathlib import Path
out=Path(sys.argv[1]);request=json.loads((out/'Request.json').read_text(encoding='utf-8'))
events=out.parent.parent/'events.txt'
with events.open('a',encoding='utf-8') as f:f.write('start '+request['title']+'\\n')
print('@studio '+json.dumps({'stage':'render','progress':50,'message':'Test de file'}),flush=True)
print('@studio invalid-json-from-a-library',flush=True)
print('@studio []',flush=True)
time.sleep(1.5 if request['title']=='Bloquant' else .15)
if request['title'].startswith('FAIL'):(out/'error.txt').write_text('Échec simulé',encoding='utf-8')
else:(out/'Video.mp4').write_bytes(b'fake-test-export')
with events.open('a',encoding='utf-8') as f:f.write('end '+request['title']+'\\n')
sys.exit(1 if request['title'].startswith('FAIL') else 0)
''',encoding='utf-8')
    real_popen=subprocess.Popen
    def fake_popen(command,**kwargs):
        assert Path(command[2]).name=='pipeline.py'
        return real_popen([sys.executable,'-u',str(fake),command[3]],**kwargs)
    server.subprocess.Popen=fake_popen
    def post(client,path,payload):return client.post(path,json=payload,headers=headers)
    def wait_finished(client,key):
        limit=time.monotonic()+15
        while time.monotonic()<limit:
            snapshot=client.get('/api/state').json()
            batch=next(batch for batch in snapshot['batches'] if batch['id']==key)
            if batch['finished']==batch['total']:return snapshot,batch
            time.sleep(.03)
        raise AssertionError('File bloquée')
    with TestClient(server.app) as client:
        # BOM, French aliases, semicolon, quotes and a multiline description.
        csv='\ufefftitre;description;charte;duree;format;voix\r\nAlpha;"Une description, avec ; séparateur\net retour à la ligne";;;;\r\nBeta;Une autre description claire;sombre;60;9:16;homme\r\n'
        body={'csv':csv,'defaults':defaults,'name':'Lot CSV'}
        preview=post(client,'/api/batches/preview',body)
        assert preview.status_code==200,preview.text
        items=preview.json()['items'];assert items[0]['duration']==45 and items[0]['theme']=='light' and items[0]['format']=='standard'
        assert items[1]['duration']==60 and items[1]['theme']=='dark' and items[1]['voice']=='Narrateur-Homme-01'
        assert client.get('/api/state').json()['jobs']==[]
        assert not list(server.JOBS.iterdir())
        for invalid in [csv.replace(';60;', ';999;'),csv.replace(';homme',';voix-inconnue'),'title,title,description\na,b,Longue description','titre;description\nCourt','titre;description\n"non fermé;texte','titre;description\n'+'Titre;Description assez longue\n'*51]:
            response=post(client,'/api/batches',{'csv':invalid,'defaults':defaults})
            assert response.status_code==422,(invalid,response.text)
            assert client.get('/api/state').json()['jobs']==[]
            assert not list(server.JOBS.iterdir())
        assert post(client,'/api/batches',{'items':[{'title':'  ','description':'Description assez longue'}]}).status_code==422
        assert post(client,'/api/batches',{'items':[{'title':'Titre','description':'Description assez longue'}],'csv':csv}).status_code==422
        assert client.post('/api/batches',json=body).status_code==403
        # Disk failures must not expose a partially enqueued lot.
        real_atomic=server.atomic
        calls=[0]
        def fail_second_request(path,data):
            if path.name=='Request.json':
                calls[0]+=1
                if calls[0]==2:raise OSError('Disque indisponible (test)')
            return real_atomic(path,data)
        server.atomic=fail_second_request
        try:
            server.enqueue(items,defaults,{'id':'test-storage','name':'Test','created':0,'defaults':defaults})
            raise AssertionError('Échec de stockage attendu')
        except OSError:pass
        finally:server.atomic=real_atomic
        assert not server.state['jobs'] and not server.state['batches'] and server.PENDING.empty()
        assert not list(server.JOBS.iterdir())
        server.state['jobs']=[{'status':'queued'} for _ in range(99)]
        assert post(client,'/api/batches',body).status_code==409
        server.state['jobs']=[]
        assert not list(server.JOBS.iterdir())
        template=client.get('/api/batches/template.csv');assert template.status_code==200 and 'text/csv' in template.headers['content-type']
        assert len(validate_batch(BatchRequest(csv=template.content.decode('utf-8-sig')))[0])==2
        # Actual subprocess ordering, including failure recovery, with a second lot.
        first=post(client,'/api/batches',{'defaults':defaults,'items':[{'title':title,'description':'Une description suffisamment longue.'} for title in ['Premier','FAIL deuxième','Troisième']]}).json()
        second=post(client,'/api/batches',body).json()
        snapshot,summary=wait_finished(client,second['id'])
        events=(root/'events.txt').read_text(encoding='utf-8').splitlines()
        assert events==[event+' '+title for title in ['Premier','FAIL deuxième','Troisième','Alpha','Beta'] for event in ['start','end']],events
        failed=next(batch for batch in snapshot['batches'] if batch['id']==first['id'])
        assert failed['status']=='finished' and failed['counts']['done']==2 and failed['counts']['failed']==1 and failed['progress']==100
        assert summary['status']=='done' and summary['counts']['done']==2
        assert snapshot['settings']==defaults
        # Restart representation keeps metadata; previously active items become interrupted.
        persisted=json.loads(server.STATE.read_text(encoding='utf-8'));assert len(persisted['batches'])==2
        retry=post(client,f"/api/batches/{first['id']}/retry",{});assert retry.status_code==201
        assert retry.json()['total']==1
        wait_finished(client,retry.json()['id'])
        # Cancelling pending jobs does not terminate the running video of the lot.
        lot=post(client,'/api/batches',{'items':[{'title':title,'description':'Une vidéo du test d’annulation.'} for title in ['Bloquant','À annuler 1','À annuler 2']]}).json()
        limit=time.monotonic()+5
        while time.monotonic()<limit and not any(job.get('batch_id')==lot['id'] and job['status']=='running' for job in server.state['jobs']):time.sleep(.02)
        result=post(client,f"/api/batches/{lot['id']}/cancel-pending",{})
        assert result.status_code==200 and result.json()['counts']['cancelled']==2 and result.json()['counts']['running']==1
        time.sleep(.1)
        assert 'À annuler' not in (root/'events.txt').read_text(encoding='utf-8')
        # Single video remains backward compatible and gets the explicit fixed voice.
        job=post(client,'/api/jobs',{'title':'Une seule','description':'Une description suffisamment longue.'})
        assert job.status_code==201 and job.json()['voice']=='Narrateur-Homme-01'
        limit=time.monotonic()+10
        while time.monotonic()<limit and server.find(job.json()['id'])['status'] in ['queued','running']:time.sleep(.03)
        assert server.find(job.json()['id'])['status']=='done'
    server.subprocess.Popen=real_popen
    # A service restart preserves batches and exposes interrupted work for retry.
    restart=root/'restart';restart.mkdir()
    state=json.loads(server.STATE.read_text(encoding='utf-8'))
    for job in state['jobs'][:2]:job['status']='queued'
    (restart/'state.json').write_text(json.dumps(state),encoding='utf-8')
    code="import sys;sys.path.insert(0,sys.argv[1]);import server;assert all(j['status']=='interrupted' for j in server.state['jobs'][:2]);assert len(server.get_state()['batches'])==len(server.state['batches'])"
    subprocess.run([sys.executable,'-c',code,str(ROOT/'studio')],env={**os.environ,'STUDIO_DATA_DIR':str(restart)},check=True)
print('OK : CSV, atomicité de validation, réglages, FIFO séquentiel, poursuite après échec, reprise et annulation du lot.')
