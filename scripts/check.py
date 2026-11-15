"""Offline smoke checks: no model download, user recordings or running server."""
import sys,tempfile,json,hashlib,os
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'studio'))
import numpy as np,soundfile as sf
from PIL import Image
from moviepy import VideoFileClip
from renderer import Film,render
from config import MODELS,VOICE,ROOT as CONFIG_ROOT
assert CONFIG_ROOT==ROOT
assert MODELS.is_absolute()
profile=json.loads((VOICE/'Profil.json').read_text(encoding='utf-8'))
assert hashlib.sha256((VOICE/'Reference-Homme.wav').read_bytes()).hexdigest()==profile['reference_sha256']
with tempfile.TemporaryDirectory() as directory:
    out=Path(directory)
    scenes=[{'title':'Une intention claire','text':'Comprendre le changement et vérifier son effet.','visual':kind,'labels':['Préparer','Vérifier','Apprendre']} for kind in ['flow','cycle','compare','steps','target','people','chart','question']]
    data={'scenes':scenes};timing=[{'start':i*5.,'end':i*5+4.5} for i in range(8)]
    (out/'Chronologie.json').write_text(json.dumps(timing),encoding='utf-8')
    (out/'Mots-alignes.json').write_text(json.dumps({'words':[{'cue':0,'text':'Comprendre','start':0,'end':2}]}),encoding='utf-8')
    for theme in ['dark','light']:
        for aspect in ['reel','standard']:
            config={'theme':theme,'format':aspect,'title':'Test de mise en scène'}
            film=Film(out,config,data);film.duration=40
            for t in [i*5+2.5 for i in range(8)]:
                frame=film.frame(t)
                assert frame.shape==((1920,1080,3) if aspect=='reel' else (1080,1920,3))
                assert np.isfinite(frame).all() and frame.max()>frame.min()
            print('OK :',theme,aspect,flush=True)
    sf.write(out/'Narration.wav',np.sin(2*np.pi*220*np.arange(12000)/24000)*.1,24000)
    os.environ['STUDIO_VIDEO_CODEC']='libx264'
    render(out,{'theme':'light','format':'standard','title':'Vérification export CPU'},data,lambda n:None)
    with VideoFileClip(str(out/'Video.mp4')) as clip:
        assert clip.size==[1920,1080] and abs(clip.duration-.5)<.1 and clip.audio is not None
    print('OK : export H.264/AAC CPU',flush=True)
print('OK : référence vocale et 32 plans ; aucun modèle requis.',flush=True)
