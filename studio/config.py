"""Portable paths. Runtime data and downloaded weights stay outside Git."""
import os
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
PORT=int(os.getenv('STUDIO_PORT','8510'))
DATA=Path(os.getenv('STUDIO_DATA_DIR',str(ROOT/'.local/state')))
JOBS=Path(os.getenv('STUDIO_JOBS_DIR',str(ROOT/'.local/jobs')))
MODELS=Path(os.getenv('STUDIO_MODELS_DIR',str(ROOT/'.local/models')))
VOICE=ROOT/'assets/voice'
VOICE_PYTHON=Path(os.getenv('STUDIO_VOICE_PYTHON',str(ROOT/('.venv-voice/Scripts/python.exe' if os.name=='nt' else '.venv-voice/bin/python'))))
OLLAMA_URL=os.getenv('STUDIO_OLLAMA_URL','http://127.0.0.1:11434').rstrip('/')
OLLAMA_MODEL=os.getenv('STUDIO_OLLAMA_MODEL','qwen3:4b')
