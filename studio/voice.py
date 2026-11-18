"""Separate existing Qwen environment; fixed speaker reference for every scene."""
from pathlib import Path
import os,sys,json,shutil
os.environ.update(HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',HF_HUB_DISABLE_TELEMETRY='1')
import torch,numpy as np,soundfile as sf
from qwen_tts import Qwen3TTSModel
from config import ROOT,MODELS,VOICE,voice_files
OUT=Path(sys.argv[1]);selected={int(s) for s in sys.argv[2:]}
request=json.loads((OUT/'Request.json').read_text(encoding='utf-8'))
profile_path,reference_path=voice_files(request.get('voice','Narrateur-Homme-01'))
profile=json.loads(profile_path.read_text(encoding='utf-8'))
scenes=json.loads((OUT/'Scenario.json').read_text(encoding='utf-8'))['scenes'];torch.set_num_threads(6)
model=Qwen3TTSModel.from_pretrained(str(MODELS/'Qwen3-TTS-1.7B-Base'),device_map='cpu',dtype=torch.bfloat16,attn_implementation='sdpa')
prompt=model.create_voice_clone_prompt(ref_audio=str(reference_path),ref_text=profile['reference_text'],x_vector_only_mode=False)
for i,scene in enumerate(scenes):
    if selected and i not in selected:continue
    path=OUT/f'Phrase-{i+1:02}.wav'
    if selected and path.exists():shutil.copy2(path,path.with_suffix('.first.wav'))
    torch.manual_seed(1300+i+(100 if selected else 0))
    settings=profile['settings'].copy();settings.update(max_new_tokens=max(110,len(scene['text'].split())*9+45),temperature=.7,top_p=.95,subtalker_temperature=.8)
    with torch.inference_mode():wavs,sr=model.generate_voice_clone(text=scene['text'],language='French',voice_clone_prompt=prompt,**settings)
    a=np.asarray(wavs[0],dtype=np.float32)
    if not np.isfinite(a).all():raise ValueError('Audio non valide.')
    sf.write(path,a,sr,subtype='PCM_16')
    print('@studio '+json.dumps({'stage':'voice','progress':65 if selected else round(17+47*(i+1)/len(scenes)),'message':f'Narration · passage {i+1} sur {len(scenes)}'+(' · reprise' if selected else '')},ensure_ascii=False),flush=True)
