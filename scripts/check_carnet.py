"""Paper directions: CSV aliases, eight diagrams, two formats, real short exports."""
import sys,json,tempfile,os
from pathlib import Path
import numpy as np,soundfile as sf
from PIL import Image
from moviepy import VideoFileClip
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'studio'))
from renderer_carnet import CarnetFilm
from renderer_papier import PapierFilm
from renderer import render
from batches import BatchRequest,validate_batch
from social_assets import make_thumbnail
items,_=validate_batch(BatchRequest(csv='titre;description;charte;voix\nUn carnet;Une explication suffisamment longue;carnet animé;duo'))
assert items[0]['theme']=='carnet' and items[0]['voice']=='Duo-Homme-Femme'
items,_=validate_batch(BatchRequest(csv='titre;description;charte;voix\nUn collage;Une explication suffisamment longue;papier découpé;femme'))
assert items[0]['theme']=='papier' and items[0]['voice']=='Narratrice-Femme-01'
with tempfile.TemporaryDirectory() as directory:
 out=Path(directory)
 kinds=['flow','cycle','compare','steps','target','people','chart','question']
 data={'scenes':[{'title':'Comprendre avant de décider','text':'Un exemple concret pour comprendre.','visual':kind,'labels':['Observation','Action','Résultat']} for kind in kinds]}
 timing=[{'start':i*5,'end':i*5+4.5} for i in range(len(kinds))]
 (out/'Chronologie.json').write_text(json.dumps(timing),encoding='utf-8')
 (out/'Mots-alignes.json').write_text(json.dumps({'words':[{'cue':0,'text':'Comprendre','start':0,'end':3}]}),encoding='utf-8')
 for theme,cls in [('carnet',CarnetFilm),('papier',PapierFilm)]:
  for aspect in ['reel','standard']:
   cfg={'theme':theme,'format':aspect,'title':'Une nouvelle explication','voice':'Duo-Homme-Femme'}
   film=cls(out,cfg,data);film.duration=40
   for i,kind in enumerate(kinds):
    a=film.frame(i*5+.18);b=film.frame(i*5+2)
    assert a.shape==((1920,1080,3) if aspect=='reel' else (1080,1920,3))
    assert np.mean(np.abs(a.astype(float)-b.astype(float)))>.01,(theme,kind)
   Image.fromarray(film.frame(2)).save(out/'Poster.jpg')
   for vertical in [True,False]:assert make_thumbnail(out,cfg,{'thumbnail_text':'Comprendre le changement'},vertical).exists()
 sf.write(out/'Narration.wav',np.sin(2*np.pi*220*np.arange(12000)/24000)*.1,24000)
 os.environ['STUDIO_VIDEO_CODEC']='libx264'
 for theme in ['carnet','papier']:
  render(out,{'theme':theme,'format':'standard','title':'Export papier'},data,lambda n:None)
  with VideoFileClip(str(out/'Video.mp4')) as clip:assert clip.size==[1920,1080] and clip.audio is not None
print('OK: both paper directions, aliases, eight diagrams in two formats, movement, thumbnails and H.264/AAC exports.')
