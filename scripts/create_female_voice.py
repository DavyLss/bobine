"""Create the shared synthetic female reference entirely offline (run with voice Python)."""
import os,sys,json,hashlib
from pathlib import Path
os.environ.update(HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',HF_HUB_DISABLE_TELEMETRY='1')
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'studio'))
from config import MODELS,VOICE
import torch,soundfile as sf
from qwen_tts import Qwen3TTSModel
text="Une idée devient plus claire quand on prend le temps de l'expliquer. Ensemble, découvrons un exemple concret, étape par étape. Vous verrez, quelques mots simples peuvent tout changer."
instruction="A native French female narrator in her thirties, warm clear natural mid-range voice, metropolitan French accent, conversational educational delivery, gently expressive with natural pauses and varied intonation. Confident and friendly, calm moderate pace. Clean dry studio recording, no reverb, no music, no sound effects, no whispering, no exaggerated breathiness."
torch.set_num_threads(6);torch.manual_seed(1842)
model=Qwen3TTSModel.from_pretrained(str(MODELS/'Qwen3-TTS-1.7B-VoiceDesign'),device_map='cpu',dtype=torch.bfloat16,attn_implementation='sdpa')
with torch.inference_mode():wavs,sr=model.generate_voice_design(text=text,language='French',instruct=instruction,non_streaming_mode=True,max_new_tokens=650)
path=VOICE/'Reference-Femme.wav';sf.write(path,wavs[0],sr,subtype='PCM_16')
profile=json.loads((VOICE/'Profil.json').read_text(encoding='utf-8'))
profile.update(reference_text=text,reference_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),seed=1842,design_instruction=instruction)
(VOICE/'Profil-Femme.json').write_text(json.dumps(profile,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Female reference created:',path,flush=True)
