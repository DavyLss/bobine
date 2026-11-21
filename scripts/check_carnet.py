"""Carnet direction: CSV aliases, all diagram types, two formats, real short export."""
import sys,json,tempfile,os
from pathlib import Path
import numpy as np,soundfile as sf
from PIL import Image
from moviepy import VideoFileClip
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'studio'))
from renderer_carnet import CarnetFilm
from renderer import render
from batches import BatchRequest,validate_batch
from social_assets import make_thumbnail
items,_=validate_batch(BatchRequest(csv='titre;description;charte;voix\nUn carnet;Une explication suffisamment longue;carnet animé;duo'))
assert items[0]['theme']=='carnet' and items[0]['voice']=='Duo-Homme-Femme'
with tempfile.TemporaryDirectory() as directory:
 out=Path(directory)
 kinds=['flow','cycle','compare','steps','target','people','chart','question']
 data={'scenes':[{'title':'Comprendre avant de décider','text':'Un exemple concret pour comprendre.','visual':kind,'labels':['Observation','Action','Résultat']} for kind in kinds]}
 timing=[{'start':i*5,'end':i*5+4.5} for i in range(len(kinds))]
 (out/'Chronologie.json').write_text(json.dumps(timing),encoding='utf-8')
 (out/'Mots-alignes.json').write_text(json.dumps({'words':[{'cue':0,'text':'Comprendre','start':0,'end':3}]}),encoding='utf-8')
 for aspect in ['reel','standard']:
  cfg={'theme':'carnet','format':aspect,'title':'Une nouvelle explication','voice':'Duo-Homme-Femme'}
  film=CarnetFilm(out,cfg,data);film.duration=40
  for i,kind in enumerate(kinds):
   a=film.frame(i*5+.18);b=film.frame(i*5+2)
   assert a.shape==((1920,1080,3) if aspect=='reel' else (1080,1920,3))
   assert np.mean(np.abs(a.astype(float)-b.astype(float)))>.01,kind
  Image.fromarray(film.frame(2)).save(out/'Poster.jpg')
  for vertical in [True,False]:assert make_thumbnail(out,cfg,{'thumbnail_text':'Comprendre le changement'},vertical).exists()
 sf.write(out/'Narration.wav',np.sin(2*np.pi*220*np.arange(12000)/24000)*.1,24000)
 os.environ['STUDIO_VIDEO_CODEC']='libx264'
 render(out,{'theme':'carnet','format':'standard','title':'Export carnet'},data,lambda n:None)
 with VideoFileClip(str(out/'Video.mp4')) as clip:assert clip.size==[1920,1080] and clip.audio is not None
print('OK: carnet aliases, eight diagrams in two formats, movement, thumbnail palette and H.264/AAC export.')
