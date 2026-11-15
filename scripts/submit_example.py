"""Submit one explicit example to the running local studio."""
import json,sys,os
from pathlib import Path
import requests
if __name__=='__main__':
    payload=json.loads(Path(sys.argv[1]).read_text(encoding='utf-8'))
    response=requests.post('http://127.0.0.1:'+os.getenv('STUDIO_PORT','8510')+'/api/jobs',json=payload,headers={'X-Studio-Request':'1'},timeout=10)
    response.raise_for_status()
    print(json.dumps(response.json(),ensure_ascii=False,indent=2))
