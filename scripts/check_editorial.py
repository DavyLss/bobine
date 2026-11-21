"""Editorial retries run before speech; local model calls are mocked."""
import sys,json,tempfile
from pathlib import Path
from unittest.mock import patch
from types import SimpleNamespace
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'studio'))
from pipeline import scenario,editorial_issues

def draft(texts):return {'scenes':[{'title':'Un exemple','text':text,'visual':'people','labels':['Action','Résultat']} for text in texts]}
repeated=draft(["L'équipe cherche une erreur et l'équipe partage les détails."]*3)
clean=draft(["Une alerte apparaît pendant la mise en production du service.","Camille consulte les journaux puis corrige le paramètre mal configuré.","Au prochain déploiement, vérifiez ce paramètre avec un contrôle automatique."])
assert editorial_issues(repeated['scenes'])
assert not editorial_issues(clean['scenes'])
config={'title':'Un déploiement','description':'Un exemple pédagogique.','duration':15,'voice':'Narratrice-Femme-01'}
def response(data):return SimpleNamespace(raise_for_status=lambda:None,json=lambda:{'message':{'content':json.dumps(data)}})
with tempfile.TemporaryDirectory() as directory:
 out=Path(directory)
 with patch('pipeline.requests.post',side_effect=[response(repeated),response(clean)]) as call:
  result=scenario(config,out)
  assert call.call_count==2 and result['voice']=='Narratrice-Femme-01'
  assert call.call_args.kwargs['json']['messages'][2]['role']=='assistant'
 with patch('pipeline.requests.post',side_effect=[response(clean),response(clean)]) as call:
  scenario(config,out);assert call.call_count==2,'Even a clean draft gets an editorial review'
 (out/'Scenario.json').unlink()
 with patch('pipeline.requests.post',return_value=response(repeated)) as call:
  try:scenario(config,out);raise AssertionError('Repeated script accepted')
  except ValueError:pass
  assert call.call_count==3 and not (out/'Scenario.json').exists()
print('OK: editorial review, repetitions, bounded repair, selected voice and no invalid scenario saved.')
