from pathlib import Path
import sys,json,re,difflib,unicodedata,subprocess,traceback,hashlib
import requests,numpy as np,soundfile as sf
from faster_whisper import WhisperModel
from config import ROOT,MODELS,VOICE,VOICE_PYTHON,OLLAMA_URL,OLLAMA_MODEL,voice_files
HERE=Path(__file__).resolve().parent
def emit(stage,message,progress,**extra):print('@studio '+json.dumps(dict(stage=stage,message=message,progress=progress,**extra),ensure_ascii=False),flush=True)
def norm(s):return re.sub('[^a-z0-9]','', ''.join(c for c in unicodedata.normalize('NFD',s.lower()) if not unicodedata.combining(c)))
def stamp(s):
    ms=round(s*1000);return f'{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02},{ms%1000:03}'
def scenario(config,out):
    count=max(3,min(16,round(config['duration']/8)));budget=round((config['duration']-count*.65)*2.2)
    schema={'type':'object','properties':{'scenes':{'type':'array','minItems':count,'maxItems':count,'items':{'type':'object','properties':{'title':{'type':'string'},'text':{'type':'string'},'visual':{'type':'string','enum':['flow','cycle','compare','steps','target','people','chart','question']},'labels':{'type':'array','items':{'type':'string'},'minItems':2,'maxItems':3}},'required':['title','text','visual','labels']}}},'required':['scenes']}
    schema['properties']['scenes']['items']['properties']['text'].update(minLength=max(50,round(budget/count*5.5)),maxLength=max(220,round(budget/count*10)))
    schema['properties']['scenes']['items']['properties']['title']['maxLength']=70
    prompt=f'''Crée une vidéo pédagogique en français accessible. Sujet : {config['title']}.
Description fournie par l'utilisateur : {config['description']}
Durée cible {config['duration']} secondes, environ {budget} mots de narration AU TOTAL, {count} plans.
Ouvre par une accroche concrète, explique simplement avec un exemple, termine par une action utile. Chaque texte est prêt à être lu, sans titres, markdown ni didascalies. Ne pas inventer de chiffres ou de références. Ne pas ajouter de publicité. Respecte les relations de cause et conséquence : un test ou une observation détecte un problème mais ne le corrige pas automatiquement. Une résolution doit montrer une action corrective. Ne promets pas de supprimer tous les risques.
Chaque plan a un title court (maximum 35 caractères), text de 8 à 28 mots (répartir le budget), un visual pertinent, et 2 ou 3 labels courts (maximum 18 caractères chacun) à afficher dans l'illustration. Les labels ne sont pas des phrases de narration.
flow=élément qui traverse des étapes, cycle=retour d'information, compare=deux situations, steps=étapes successives, target=objectif atteint, people=collaboration, chart=comparaison illustrative non chiffrée, question=question/action finale.
Ne pas choisir la même illustration pour plus de deux plans. Le dernier plan utilise question. Ne fournis que le JSON conforme au schéma : {json.dumps(schema)}'''
    for attempt in range(2):
        response=requests.post(OLLAMA_URL+'/api/chat',json={'model':OLLAMA_MODEL,'messages':[{'role':'user','content':prompt}],'stream':False,'think':False,'format':schema,'keep_alive':0,'options':{'temperature':.35,'num_predict':4500,'num_ctx':8192}},timeout=(5,300))
        response.raise_for_status();data=json.loads(response.json()['message']['content']);scenes=data.get('scenes',[])
        words=sum(len(s.get('text','').split()) for s in scenes)
        if .7*budget<=words<=1.35*budget:break
        prompt+=f'\nATTENTION : la version précédente comptait {words} mots, le budget est {budget}. Réécris en visant {max(8,round(budget/count))} mots par plan. Respecte vraiment la longueur pour cette durée.'
    if len(scenes)!=count:raise ValueError('Le modèle de texte n’a pas produit le nombre de plans demandé. Relancez la génération.')
    for scene in scenes:
        scene['title']=str(scene['title']).strip()[:70];scene['text']=str(scene['text']).strip()
        if not 5<=len(scene['text'].split())<=45:raise ValueError('Un passage du scénario est trop court ou trop long. Précisez la description et relancez.')
        if scene['visual'] not in schema['properties']['scenes']['items']['properties']['visual']['enum']:raise ValueError('Illustration non reconnue.')
        scene['labels']=[str(s).strip()[:24] for s in scene['labels'][:3]]
    # Retain a practical closing composition even when the small local model ignores it.
    scenes[-1]['visual']='question'
    for scene in scenes:
        scene['text']=re.sub(r'\bsans risque\b','en limitant les risques',scene['text'],flags=re.IGNORECASE)
        scene['text']=re.sub(r'\béviter toutes les erreurs\b','réduire les erreurs',scene['text'],flags=re.IGNORECASE)
    data.update(title=config['title'],target_duration=config['duration'],voice=config.get('voice','Narrateur-Homme-01'),reference_sha256=hashlib.sha256(voice_files(config.get('voice','Narrateur-Homme-01'))[1].read_bytes()).hexdigest())
    (out/'Scenario.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8');return data
def voice(out,indices=None):
    exe=VOICE_PYTHON
    result=subprocess.run([str(exe),'-u',str(HERE/'voice.py'),str(out),*[str(i) for i in (indices or [])]],cwd=ROOT)
    if result.returncode:raise RuntimeError('La synthèse vocale locale a échoué. Le journal contient le détail.')
def recognize(model,path,text):
    segments,_=model.transcribe(str(path),language='fr',word_timestamps=True,beam_size=5,condition_on_previous_text=False)
    words=[w for segment in segments for w in segment.words if norm(w.word)]
    observed=''.join(norm(w.word) for w in words);match=difflib.SequenceMatcher(None,norm(text),observed,autojunk=False)
    return words,match
def align(out,data):
    model=WhisperModel(str(MODELS/'whisper-base'),device='cpu',compute_type='int8')
    checks=[];recognized=[];bad=[]
    for i,s in enumerate(data['scenes']):
        words,match=recognize(model,out/f'Phrase-{i+1:02}.wav',s['text']);recognized.append((words,match))
        if match.ratio()<.84 or not words:bad.append(i)
    if bad:
        emit('voice',f'Reprise de {len(bad)} passage(s) avec la même voix…',65);voice(out,bad)
        for i in bad:
            recognized[i]=recognize(model,out/f'Phrase-{i+1:02}.wav',data['scenes'][i]['text'])
    sr=24000;cursor=.25;parts=[np.zeros(round(cursor*sr))];timing=[];entries=[]
    for i,(scene,(ws,match)) in enumerate(zip(data['scenes'],recognized)):
        ratio=match.ratio();checks.append({'index':i,'agreement':ratio,'transcript':' '.join(w.word for w in ws)})
        if ratio<.84 or not ws:
            (out/'Controle-texte.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2),encoding='utf-8')
            raise ValueError(f'Le texte du passage {i+1} n’est pas suffisamment reconnu après reprise. Relancez avec une formulation plus simple.')
        audio,rate=sf.read(out/f'Phrase-{i+1:02}.wav');assert rate==sr
        left=max(0,ws[0].start-.1);right=min(len(audio)/sr,ws[-1].end+.18);clip=audio[round(left*sr):round(right*sr)].copy()
        active=clip[np.abs(clip)>.008]
        if len(active)<sr*.15:raise ValueError(f'Le passage {i+1} ne contient pas de parole exploitable.')
        clip*=np.clip(.105/np.sqrt(np.mean(active**2)),.65,1.7);peak=np.max(np.abs(clip))
        if peak>.88:clip*=.88/peak
        fade=min(round(.006*sr),len(clip)//2);clip[:fade]*=np.linspace(0,1,fade);clip[-fade:]*=np.linspace(1,0,fade);duration=len(clip)/sr
        tokens=[]
        for word in scene['text'].split():
            if norm(word):tokens.append(word)
            elif tokens:tokens[-1]+=' '+word
        mapping={a+k:b+k for a,b,n in match.get_matching_blocks() for k in range(n)};owners=[j for j,w in enumerate(ws) for _ in norm(w.word)];offset=0
        for j,word in enumerate(tokens):
            chars=[owners[mapping[n]] for n in range(offset,offset+len(norm(word))) if n in mapping];offset+=len(norm(word))
            a=ws[chars[0]].start-left if chars else duration*j/len(tokens);b=ws[chars[-1]].end-left if chars else duration*(j+1)/len(tokens)
            a=max(0,min(duration-.04,a));b=max(a+.04,min(duration,b));entries.append({'cue':i,'text':word,'start':cursor+a,'end':cursor+b})
        timing.append({'start':cursor,'end':cursor+duration,'text':scene['text']});pause=.6 if i<len(data['scenes'])-1 else 1.1
        parts.extend([clip,np.zeros(round(pause*sr))]);cursor+=duration+pause
    sf.write(out/'Narration.wav',np.concatenate(parts),sr,subtype='PCM_16')
    for name,value in [('Chronologie.json',timing),('Mots-alignes.json',{'words':entries}),('Controle-texte.json',checks)]:
        (out/name).write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf-8')
    (out/'Sous-titres.srt').write_text('\n\n'.join(f'{i+1}\n{stamp(t["start"])} --> {stamp(t["end"])}\n{t["text"]}' for i,t in enumerate(timing)),encoding='utf-8')
    return cursor
def main(out):
    config=json.loads((out/'Request.json').read_text(encoding='utf-8'))
    emit('scenario','Écriture du scénario et choix des illustrations…',5)
    data=scenario(config,out);emit('voice',f'Scénario prêt · {len(data["scenes"])} plans. Chargement de la voix…',16,scene_count=len(data['scenes']))
    voice(out);emit('alignment','Vérification de la parole et alignement des sous-titres…',65)
    duration=align(out,data);emit('render','Préparation des animations…',74,actual_duration=round(duration,2))
    from renderer import render
    render(out,config,data,lambda p:emit('render',f'Rendu vidéo · {p} % des images',74+round(p*.23)))
    emit('verify','Contrôle de la vidéo et du son…',98)
    from moviepy import VideoFileClip
    from PIL import Image
    with VideoFileClip(str(out/'Video.mp4')) as clip:
        expected=[1080,1920] if config['format']=='reel' else [1920,1080]
        assert clip.size==expected and clip.audio is not None and abs(clip.duration-duration)<.15
        a=clip.audio.to_soundarray(fps=24000);peak=float(np.max(np.abs(a)));assert np.isfinite(a).all() and .03<peak<1
        Image.fromarray(clip.get_frame(min(2,clip.duration/2))).save(out/'Poster.jpg',quality=90)
        verification={'duration':clip.duration,'size':clip.size,'fps':clip.fps,'audio_peak':peak,'reference_sha256':data['reference_sha256'],'scope':'Contrôles techniques et transcription. Le scénario IA et le naturel de la voix restent à relire et écouter avant publication.'}
    (out/'Verification.json').write_text(json.dumps(verification,ensure_ascii=False,indent=2),encoding='utf-8')
    warning=''
    emit('metadata','Titre, description, hashtags et miniatures · génération locale…',99)
    try:
        from social_assets import create
        create(out,config,data)
    except Exception as error:
        (out/'Publication-Erreur.txt').write_text(str(error),encoding='utf-8')
        warning='Vidéo prête, mais le kit de publication local a échoué. Le régénérer avant tout envoi.'
    if abs(duration-config['duration'])>max(8,config['duration']*.25):warning=(warning+' La durée réelle s’écarte de la cible ; le débit de la voix et les pauses ont été conservés.').strip()
    emit('done','Vidéo prête.',100,actual_duration=round(duration,2),warning=warning)
if __name__=='__main__':
    out=Path(sys.argv[1]).resolve()
    try:main(out)
    except Exception as e:
        (out/'error.txt').write_text(str(e),encoding='utf-8');traceback.print_exc();sys.exit(1)
