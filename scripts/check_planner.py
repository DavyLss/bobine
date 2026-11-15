"""Offline import and planning checks: real short MP4, no remote publication."""
import json,os,sys,tempfile,time,uuid,subprocess,shutil
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from datetime import datetime,timezone
from fastapi.testclient import TestClient
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'studio'))
with tempfile.TemporaryDirectory() as directory:
    root=Path(directory);os.environ.update(STUDIO_DATA_DIR=str(root/'state'),STUDIO_JOBS_DIR=str(root/'jobs'),STUDIO_PORT='8512')
    import server as s,planner
    from moviepy import ColorClip
    clip=ColorClip((160,284),color=(30,45,60),duration=.3);source=root/'sample.mp4';clip.write_videofile(str(source),fps=10,codec='libx264',audio=False,logger=None);clip.close()
    config={'enabled':True,'youtube_client_id':'client','youtube_client_secret':'secret','youtube_refresh_token':'refresh','youtube_channel_id':'channel'}
    headers={'X-Studio-Request':'1'};client=TestClient(s.app)
    with patch.object(s.integrations,'load',return_value=config):
        assert client.post('/api/imports?filename=a.mp4',content=source.read_bytes()).status_code==403
        assert client.post('/api/imports?filename=file.exe',content=b'no',headers=headers).status_code==422
        imported=client.post('/api/imports?filename=Example.mp4',content=source.read_bytes(),headers=headers)
        assert imported.status_code==201,imported.text
        job=imported.json();assert job['source']=='import' and job['format']=='reel' and job['status']=='done'
        out=s.JOBS/job['id'];assert (out/'Video.mp4').is_file() and (out/'Poster.jpg').is_file() and not (out/'Source.mp4').exists()
        before=set(s.JOBS.iterdir())
        assert client.post('/api/imports?filename=broken.mp4',content=b'invalid file',headers=headers).status_code==422
        with patch.object(planner,'MAX_UPLOAD',8):assert client.post('/api/imports?filename=large.mp4',content=b'x'*9,headers=headers).status_code==413
        assert set(s.JOBS.iterdir())==before
        meta={'title':'Une explication utile','description':'Une description suffisamment longue pour publier.','hashtags':['#Video','#Exemple','#Apprentissage'],'thumbnail_text':'Une idée claire'}
        at=time.time()+3600;iso=lambda t:datetime.fromtimestamp(t,timezone.utc).isoformat()
        payload={'platforms':['youtube'],'items':[{'job_id':job['id'],'at':iso(at),'metadata':meta}]}
        result=client.post('/api/publications/plans',json=payload,headers=headers);assert result.status_code==201,result.text
        plan=result.json()['plans'][0];assert 'accounts' not in plan
        assert client.post('/api/publications/plans',json=payload,headers=headers).status_code==409
        assert client.post(f"/api/jobs/{job['id']}/social/publish",json={'platforms':['youtube'],'mode':'now'},headers=headers).status_code==409
        assert client.put(f"/api/jobs/{job['id']}/social/metadata",json=meta,headers=headers).status_code==409
        captured=[]
        with patch.object(s,'queue_social',side_effect=lambda *args,**kwargs:captured.append((args,kwargs))):
            planner.tick(s);assert not captured
            with patch.object(planner,'time',SimpleNamespace(time=lambda:at+1)):
                planner.tick(s);planner.tick(s)
            assert len(captured)==1 and captured[0][1]['plan_id']==plan['id'] and captured[0][0][3]=='now'
        s.find(job['id'])['publication']={'status':'published','targets':{'youtube':{'status':'published'}}}
        planner.tick(s);assert s.state['publication_plans'][0]['status']=='published'
        assert client.delete('/api/publications/plans/'+plan['id'],headers=headers).status_code==409
        # Clone only test fixture files to exercise another independent publication.
        key=uuid.uuid4().hex;folder=s.JOBS/key;folder.mkdir()
        for name in ['Video.mp4','Poster.jpg']:shutil.copyfile(out/name,folder/name)
        other={**job,'id':key};s.state['jobs'].append(other)
        late={'platforms':['youtube'],'items':[{'job_id':key,'at':iso(at),'metadata':meta}]}
        second=client.post('/api/publications/plans',json=late,headers=headers).json()['plans'][0]
        with patch.object(planner,'time',SimpleNamespace(time=lambda:at+301)),patch.object(s,'queue_social') as dispatch:
            planner.tick(s);dispatch.assert_not_called()
        assert s.state['publication_plans'][1]['status']=='overdue'
        moved=client.patch('/api/publications/plans/'+second['id'],json={'at':iso(at+7200)},headers=headers);assert moved.status_code==200
        assert client.delete('/api/publications/plans/'+second['id'],headers=headers).status_code==200
        naive={**late,'items':[{**late['items'][0],'at':'2030-01-01T12:00:00'}]}
        assert client.post('/api/publications/plans',json=naive,headers=headers).status_code==422
        # Interrupted dispatches never become automatic resends after restart.
        s.state['publication_plans']=[{**second,'status':'waiting','at':1},{**plan,'status':'dispatching'}];s.save()
    code="import sys;sys.path.insert(0,sys.argv[1]);import server;assert [p['status'] for p in server.state['publication_plans']]==['overdue','needs_attention']"
    subprocess.run([sys.executable,'-c',code,str(ROOT/'studio')],env=os.environ.copy(),check=True)
print('OK: real video import, limits, cleanup, scheduling gate, receipts, deduplication, moves, cancellation and restart safety.')
