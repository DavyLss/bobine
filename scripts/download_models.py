"""Download pinned public weights once; generation uses only local files."""
import json,sys
from pathlib import Path
from huggingface_hub import snapshot_download
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'studio'))
from config import MODELS

if __name__=='__main__':
    for model in json.loads((ROOT/'models.json').read_text(encoding='utf-8'))['models']:
        print('Téléchargement :',model['repo'],model['revision'],flush=True)
        snapshot_download(repo_id=model['repo'],revision=model['revision'],local_dir=MODELS/model['directory'],ignore_patterns=['*.md','.gitattributes','*.msgpack','*.h5'])
    print('Modèles locaux prêts dans',MODELS)
