"""Portable paths. Runtime data and downloaded weights stay outside Git."""
import os,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
local_file=ROOT/'.local/config.json'
local=json.loads(local_file.read_text(encoding='utf-8-sig')) if local_file.is_file() else {}
def setting(name,default):return os.getenv(name,local.get(name,default))
PORT=int(setting('STUDIO_PORT','8510'))
DATA=Path(setting('STUDIO_DATA_DIR',str(ROOT/'.local/state')))
JOBS=Path(setting('STUDIO_JOBS_DIR',str(ROOT/'.local/jobs')))
MODELS=Path(setting('STUDIO_MODELS_DIR',str(ROOT/'.local/models')))
VOICE=ROOT/'assets/voice'
VOICE_PYTHON=Path(setting('STUDIO_VOICE_PYTHON',str(ROOT/('.venv-voice/Scripts/python.exe' if os.name=='nt' else '.venv-voice/bin/python'))))
OLLAMA_URL=setting('STUDIO_OLLAMA_URL','http://127.0.0.1:11434').rstrip('/')
OLLAMA_MODEL=setting('STUDIO_OLLAMA_MODEL','qwen3:4b')
