"""Duo writing, identity, synthesis retries and subtitle turns, without AI inference."""
import sys,json,tempfile,runpy,contextlib
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import numpy as np,soundfile as sf
ROOT=Path(__file__).resolve().parent.parent;sys.path.insert(0,str(ROOT/'studio'))
from narration import DUO_ID,HOSTS,speaker_ids,reference_hashes
from batches import BatchRequest,validate_batch
import pipeline
texts=["Pourquoi chercher un coupable quand le service tombe soudainement en panne ?","Parce que cela semble simple, mais comprendre les conditions de cette panne est plus utile.","Donc on examine les informations disponibles au moment où la décision a été prise ?","Oui, puis on attribue des actions concrètes et on vérifie leur réalisation après cet incident."]
draft={'scenes':[{'title':'Un échange','text':text,'visual':'people','labels':['Faits','Actions']} for text in texts]}
config={'title':'Un incident','description':'Expliquer une analyse après incident.','duration':30,'voice':DUO_ID}
reply=SimpleNamespace(raise_for_status=lambda:None,json=lambda:{'message':{'content':json.dumps(draft)}})
items,_=validate_batch(BatchRequest(defaults={'voice':DUO_ID},csv='titre;description;voix\nUn échange;Une description suffisamment longue;\nUne autre;Une description suffisamment longue;duo\nSolo;Une description suffisamment longue;femme'))
assert [i['voice'] for i in items]==[DUO_ID,DUO_ID,HOSTS[1]]
with tempfile.TemporaryDirectory() as directory:
 out=Path(directory)
 with patch('pipeline.requests.post',return_value=reply) as calls:
  data=pipeline.scenario(config,out)
  assert calls.call_count==2 and 'MODE DUO' in calls.call_args.kwargs['json']['messages'][1]['content']
 narrated=json.loads(json.dumps(draft));narrated['scenes'][0]['text']='L’animateur demande pourquoi cette panne concerne le service et cherche une explication.'
 bad=SimpleNamespace(raise_for_status=lambda:None,json=lambda:{'message':{'content':json.dumps(narrated)}})
 with patch('pipeline.requests.post',side_effect=[bad,reply]) as calls:
  data=pipeline.scenario(config,out)
  assert calls.call_count==2 and all('animateur' not in s['text'].lower() for s in data['scenes'])
 assert [s['speaker'] for s in data['scenes']]==list(HOSTS)*2
 assert set(data['reference_sha256'])==set(HOSTS)
 assert reference_hashes(HOSTS[0])==data['reference_sha256'][HOSTS[0]]
 (out/'Request.json').write_text(json.dumps(config),encoding='utf-8')
 generated=[]
 class Model:
  @classmethod
  def from_pretrained(cls,*args,**kwargs):return cls()
  def create_voice_clone_prompt(self,ref_audio,**kwargs):return Path(ref_audio).name
  def generate_voice_clone(self,voice_clone_prompt,**kwargs):
   generated.append(voice_clone_prompt)
   return [np.sin(2*np.pi*220*np.arange(24000)/24000)*.1],24000
 torch=SimpleNamespace(set_num_threads=lambda n:None,manual_seed=lambda n:None,inference_mode=contextlib.nullcontext,bfloat16='bf16')
 with patch.dict(sys.modules,{'torch':torch,'qwen_tts':SimpleNamespace(Qwen3TTSModel=Model)}):
  with patch.object(sys,'argv',['voice.py',str(out)]):runpy.run_path(str(ROOT/'studio/voice.py'),run_name='__main__')
  assert generated==['Reference-Homme.wav','Reference-Femme.wav']*2
  generated.clear()
  with patch.object(sys,'argv',['voice.py',str(out),'2']):runpy.run_path(str(ROOT/'studio/voice.py'),run_name='__main__')
  assert generated==['Reference-Homme.wav'] and (out/'Phrase-03.first.wav').exists()
 try:speaker_ids(DUO_ID,[{'speaker':HOSTS[1]},{}]);raise AssertionError('Inconsistent speaker accepted')
 except ValueError:pass
 # Alignment keeps identities outside spoken text and uses short turn gaps.
 def recognize(model,path,text):
  words=[SimpleNamespace(word=w,start=i*.04+.08,end=(i+1)*.04+.08) for i,w in enumerate(text.split())]
  normalized=pipeline.norm(text)
  import difflib
  return words,difflib.SequenceMatcher(None,normalized,normalized,autojunk=False)
 with patch('pipeline.WhisperModel',return_value=None),patch('pipeline.recognize',side_effect=recognize):pipeline.align(out,data)
 timing=json.loads((out/'Chronologie.json').read_text(encoding='utf-8'))
 assert [t['speaker'] for t in timing]==list(HOSTS)*2
 assert abs(timing[1]['start']-timing[0]['end']-.3)<.001
 srt=(out/'Sous-titres.srt').read_text(encoding='utf-8');assert 'Animateur' not in srt and 'Animatrice' not in srt
 from renderer import Film
 for aspect in ['reel','standard']:
  for theme in ['dark','light']:
   film=Film(out,{**config,'format':aspect,'theme':theme},data);film.duration=timing[-1]['end']+1.1
   for t in timing[:2]:
    with patch.object(film,'tx',wraps=film.tx) as draw:
     assert film.frame(t['start']+.2).shape==((1920,1080,3) if aspect=='reel' else (1080,1920,3))
     assert not any(str(call.args[3]) in ['Animateur','Animatrice'] for call in draw.call_args_list)
print('OK: dialogue, CSV, fixed alternating references, retries, turn timing, subtitles and both visual formats.')
