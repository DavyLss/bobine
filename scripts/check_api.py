"""API boundaries without downloads or generating a job."""
import os,sys,tempfile
from pathlib import Path
from fastapi.testclient import TestClient
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'studio'))
with tempfile.TemporaryDirectory() as directory:
    os.environ.update(STUDIO_DATA_DIR=directory+'/state',STUDIO_JOBS_DIR=directory+'/jobs',STUDIO_PORT='8511')
    from server import app
    payload={'title':'Test','description':'Description du test local.','theme':'dark','format':'reel','duration':999}
    with TestClient(app) as client:
        assert client.get('/').status_code==200
        assert client.get('/static/app.js').status_code==200
        assert client.get('/api/state').json()['jobs']==[]
        assert client.post('/api/jobs',json=payload).status_code==403
        assert client.post('/api/jobs',json=payload,headers={'X-Studio-Request':'1','Origin':'http://127.0.0.1:8511'}).status_code==422
        payload['duration']=30
        assert client.post('/api/jobs',json=payload,headers={'X-Studio-Request':'1','Origin':'https://external.invalid'}).status_code==403
        assert client.get('/api/jobs/unknown/files/Video.mp4').status_code==404
        assert client.get('/api/state',headers={'Host':'external.invalid'}).status_code==400
        assert client.get('/api/state').json()['jobs']==[]
print('OK : UI, API, validation, port configurable et protection des requêtes.')
