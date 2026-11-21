"""Speaker identity shared by writing, synthesis and retries (no model dependency)."""
import hashlib
from config import voice_files
DUO_ID='Duo-Homme-Femme'
HOSTS=('Narrateur-Homme-01','Narratrice-Femme-01')
LABELS={HOSTS[0]:'Animateur',HOSTS[1]:'Animatrice'}

def speaker_ids(voice,scenes):
    if voice!=DUO_ID:
        voice_files(voice)
        return [voice]*len(scenes)
    expected=[HOSTS[i%2] for i in range(len(scenes))]
    if len(scenes)<2:raise ValueError('Le duo nécessite au moins deux répliques.')
    if any(scene.get('speaker',speaker)!=speaker for scene,speaker in zip(scenes,expected)):
        raise ValueError('L’ordre des voix du duo est incohérent avec le scénario.')
    return expected

def reference_hashes(voice):
    def digest(speaker):return hashlib.sha256(voice_files(speaker)[1].read_bytes()).hexdigest()
    return {speaker:digest(speaker) for speaker in HOSTS} if voice==DUO_ID else digest(voice)
