"""Native YouTube/Instagram publication and Buffer TikTok, with durable receipts."""
import base64,hashlib,json,time,uuid
from pathlib import Path
from urllib.parse import urlparse
import requests
import integrations as api
from social_assets import write_json,tiktok_video

PLATFORMS=['youtube','instagram','tiktok']

def account_ids(config):
    return {'youtube':config.get('youtube_channel_id',''),'instagram':config.get('instagram_user_id',''),'tiktok':config.get('buffer_tiktok_channel','')}

def allowed(config,platform):
    current=api.load()
    if not current.get('enabled'):raise ValueError('Les envois ont été désactivés dans les réglages.')
    if account_ids(current)[platform]!=account_ids(config)[platform]:raise ValueError('Le compte de destination a changé pendant la préparation. Envoi arrêté.')

def public_report(record):
    return {key:({p:{k:v for k,v in target.items() if not k.endswith('_session')} for p,target in value.items()} if key=='targets' else value) for key,value in record.items()}

def load_report(out):
    path=Path(out)/'Publishing.json'
    return json.loads(path.read_text(encoding='utf-8')) if path.exists() else {'status':'not_sent','targets':{},'assets':{}}

def summarize(record):
    values=[target['status'] for target in record['targets'].values()]
    if not values:return record.get('status','not_sent')
    if all(value=='published' for value in values):return 'published'
    if any(value in ['uncertain','interrupted'] for value in values):return 'needs_attention'
    if any(value=='error' for value in values):return 'partial' if any(value in ['published','submitted','processing','scheduled','sending'] for value in values) else 'failed'
    return 'submitted'

def save(out,record,changed):
    record['updated']=time.time();write_json(Path(out)/'Publishing.json',record);changed(public_report(record))

def cloud_upload(path,config,progress=lambda message:None):
    path=Path(path);video=path.suffix=='.mp4';kind='video' if video else 'image'
    total=path.stat().st_size
    if not total:raise ValueError('Fichier média vide.')
    with path.open('rb') as source:digest=hashlib.file_digest(source,'sha256').hexdigest()
    params={'public_id':'local-video-studio/'+path.parent.name+'/'+digest,'timestamp':str(int(time.time())),'overwrite':'false'}
    signed='&'.join(f'{key}={value}' for key,value in sorted(params.items()))+config['cloudinary_api_secret']
    params.update(signature=hashlib.sha1(signed.encode()).hexdigest(),api_key=config['cloudinary_api_key'])
    endpoint=f"https://api.cloudinary.com/v1_1/{config['cloudinary_cloud_name']}/{kind}/upload"
    upload_id=uuid.uuid4().hex;chunk_size=10*1024*1024;position=0;result={}
    with path.open('rb') as source:
        while position<total:
            chunk=source.read(chunk_size);headers={}
            if video:headers={'X-Unique-Upload-Id':upload_id,'Content-Range':f'bytes {position}-{position+len(chunk)-1}/{total}'}
            result,_=api.request_json('POST',endpoint,config,data=params,files={'file':(path.name,chunk,'video/mp4' if video else 'image/jpeg')},headers=headers,timeout=(10,180))
            position+=len(chunk);progress(f'Transfert Cloudinary · {round(position/total*100)} %')
    url=result.get('secure_url','')
    if urlparse(url).scheme!='https' or urlparse(url).hostname!='res.cloudinary.com':raise RuntimeError('Cloudinary ne retourne pas d’URL publique HTTPS attendue.')
    return {'url':url,'public_id':result.get('public_id'),'cloud':config['cloudinary_cloud_name'],'sha256':digest}

def hosted(out,filename,config,record,changed):
    cached=record['assets'].get(filename)
    with (Path(out)/filename).open('rb') as source:digest=hashlib.file_digest(source,'sha256').hexdigest()
    if cached and cached.get('cloud')==config['cloudinary_cloud_name'] and cached.get('sha256')==digest:return cached['url']
    record['message']='Transfert du média vers Cloudinary.';save(out,record,changed)
    def progress(message):record['message']=message;save(out,record,changed)
    asset=cloud_upload(Path(out)/filename,config,progress);record['assets'][filename]=asset;save(out,record,changed);return asset['url']

def youtube_upload(out,text,config,target,persist):
    allowed(config,'youtube')
    path=Path(out)/'Video.mp4';total=path.stat().st_size;token=api.youtube_token(config);headers={'Authorization':'Bearer '+token}
    if target.get('post_id'):return
    if target.get('youtube_session'):
        session=api.protect(base64.b64decode(target['youtube_session']),True).decode()
        if urlparse(session).scheme!='https' or urlparse(session).hostname!='www.googleapis.com':raise ValueError('Session YouTube locale invalide.')
        response=requests.put(session,headers={**headers,'Content-Range':f'bytes */{total}','Content-Length':'0'},data=b'',timeout=(10,60),allow_redirects=False)
        if response.status_code in [200,201]:
            target.update(post_id=response.json()['id'],status='processing',url='https://www.youtube.com/watch?v='+response.json()['id']);persist();youtube_thumbnail(out,config,target,persist,headers);return
        if response.status_code!=308:raise RuntimeError('Session YouTube non récupérable. Vérifier la chaîne avant toute nouvelle tentative.')
        offset=int(response.headers.get('Range','bytes=0--1').split('-')[-1])+1 if response.headers.get('Range') else 0
    else:
        body={'snippet':{'title':text['platforms']['youtube']['title'],'description':text['platforms']['youtube']['description'],'tags':[s.lstrip('#') for s in text['hashtags']],'categoryId':'27','defaultLanguage':'fr'},'status':{'privacyStatus':config['youtube_privacy'],'selfDeclaredMadeForKids':config['youtube_made_for_kids'],'containsSyntheticMedia':config['ai_disclosure']}}
        response=requests.post('https://www.googleapis.com/upload/youtube/v3/videos',params={'uploadType':'resumable','part':'snippet,status'},headers={**headers,'X-Upload-Content-Type':'video/mp4','X-Upload-Content-Length':str(total)},json=body,timeout=(10,60),allow_redirects=False)
        if response.status_code not in [200,201]:raise RuntimeError(f'YouTube refuse la session d’envoi (HTTP {response.status_code}). Vérifier OAuth, autorisations et quota.')
        session=response.headers.get('Location','')
        if urlparse(session).scheme!='https' or urlparse(session).hostname!='www.googleapis.com':raise RuntimeError('Adresse de session YouTube inattendue.')
        target['youtube_session']=base64.b64encode(api.protect(session.encode())).decode();persist();offset=0
    with path.open('rb') as source:
        source.seek(offset)
        while offset<total:
            allowed(config,'youtube')
            chunk=source.read(8*1024*1024)
            response=requests.put(session,headers={**headers,'Content-Type':'video/mp4','Content-Range':f'bytes {offset}-{offset+len(chunk)-1}/{total}'},data=chunk,timeout=(10,180),allow_redirects=False)
            if response.status_code in [200,201]:
                target.update(post_id=response.json()['id'],status='processing',url='https://www.youtube.com/watch?v='+response.json()['id']);persist();break
            if response.status_code!=308:raise RuntimeError(f'Envoi YouTube interrompu (HTTP {response.status_code}). La session est conservée pour contrôle/reprise.')
            received=response.headers.get('Range')
            if not received:raise RuntimeError('YouTube ne confirme pas les octets reçus. Reprendre après contrôle de la session.')
            confirmed=int(received.split('-')[-1])+1
            if confirmed<=offset or confirmed>total:raise RuntimeError('Position de reprise YouTube incohérente.')
            offset=confirmed;source.seek(offset);target['message']=f'Transfert YouTube · {round(offset/total*100)} %';persist()
    if not target.get('post_id'):raise RuntimeError('YouTube ne confirme pas la fin du transfert.')
    youtube_thumbnail(out,config,target,persist,headers)

def youtube_thumbnail(out,config,target,persist,headers):
    try:
        with (Path(out)/'Miniature-YouTube.jpg').open('rb') as image:
            response=requests.post('https://www.googleapis.com/upload/youtube/v3/thumbnails/set',params={'videoId':target['post_id'],'uploadType':'media'},headers={**headers,'Content-Type':'image/jpeg'},data=image,timeout=(10,60),allow_redirects=False)
        target['thumbnail_status']='applied' if response.status_code==200 else 'unsupported'
        if response.status_code!=200:target['warning']='Miniature personnalisée refusée par YouTube : vérifier les droits de la chaîne et les limites Shorts. Le fichier JPG reste disponible.'
    except requests.RequestException:target['warning']='Vidéo reçue par YouTube ; envoi de la miniature non confirmé.'
    persist()

def instagram_publish(out,text,config,target,record,changed):
    api.refresh_instagram(config)
    base=f"https://graph.instagram.com/{config['instagram_version']}";headers={'Authorization':'Bearer '+config['instagram_token']}
    def persist():save(out,record,changed)
    if not target.get('container_id'):
        video_url=hosted(out,'Video.mp4',config,record,changed);cover=hosted(out,'Miniature-Reel.jpg',config,record,changed)
        data,_=api.request_json('POST',base+'/'+config['instagram_user_id']+'/media',config,headers=headers,json={'media_type':'REELS','video_url':video_url,'cover_url':cover,'caption':text['platforms']['instagram']['caption'],'share_to_feed':True,'is_ai_generated':config['ai_disclosure']})
        target.update(container_id=data['id'],status='processing',message='Instagram prépare le Reel.');persist()
    data,_=api.request_json('GET',base+'/'+target['container_id'],config,headers=headers,params={'fields':'status_code'})
    status=data.get('status_code')
    if status in ['ERROR','EXPIRED']:raise RuntimeError('Le conteneur Instagram est '+status+'. Vérifier le média et les limites dans Meta.')
    if status=='PUBLISHED':
        target.update(status='published',message='Instagram confirme la publication du conteneur.');persist();return
    if status!='FINISHED':target.update(status='processing',message='Préparation du Reel par Instagram.');persist();return
    if target.get('publish_attempted'):
        target.update(status='uncertain',message='Une demande de publication existe déjà. Vérifier Instagram avant de renvoyer.');persist();return
    allowed(config,'instagram')
    target.update(publish_attempted=True,status='sending');persist()
    data,_=api.request_json('POST',base+'/'+config['instagram_user_id']+'/media_publish',config,headers=headers,json={'creation_id':target['container_id']})
    target.update(post_id=data['id'],status='published',message='Reel publié sur Instagram.');persist()
    try:
        data,_=api.request_json('GET',base+'/'+target['post_id'],config,headers=headers,params={'fields':'permalink'})
        target['url']=data.get('permalink','');persist()
    except RuntimeError:pass

def buffer_publish(out,text,config,target,record,mode,changed):
    if config.get('tiktok_cover',True):
        record['message']='Préparation locale de la copie TikTok avec couverture de 0,6 s.';save(out,record,changed);tiktok_video(out);filename='TikTok.mp4';offset=300
    else:filename='Video.mp4';offset=2000
    url=hosted(out,filename,config,record,changed)
    payload={'text':text['platforms']['tiktok']['caption'],'channelId':config['buffer_tiktok_channel'],'schedulingType':'automatic','mode':'shareNow' if mode=='now' else 'addToQueue','needsApproval':False,'saveToDraft':False,'aiAssisted':True,'metadata':{'tiktok':{'isAiGenerated':config['ai_disclosure']}},'assets':[{'video':{'url':url,'metadata':{'thumbnailOffset':offset}}}]}
    allowed(config,'tiktok')
    target.update(status='sending',publish_attempted=True);save(out,record,changed)
    result=api.buffer_query('mutation Publish($input: CreatePostInput!) { createPost(input:$input) { ... on PostActionSuccess { post { id status externalLink } } ... on MutationError { message } } }',{'input':payload},config)['createPost']
    if not result.get('post'):
        target['publish_attempted']=False
        raise RuntimeError(result.get('message','Buffer refuse le post.'))
    post=result['post'];waiting=post['status'] in ['draft','needs_approval','error']
    target.update(post_id=post['id'],status='published' if post['status']=='sent' else 'error' if waiting else 'scheduled',remote_status=post['status'],url=post.get('externalLink') or '',message='Buffer nécessite une intervention : '+post['status'] if waiting else 'Transmis à Buffer ; publication TikTok à confirmer.');save(out,record,changed)

def run(out,platforms,mode,changed=lambda record:None,expected_accounts=None):
    out=Path(out);config=api.load();missing=api.missing(config,platforms)
    if missing:raise ValueError(' '.join(missing))
    ids=account_ids(config)
    if expected_accounts and any(expected_accounts.get(p)!=ids[p] for p in platforms):raise ValueError('Un compte de destination a changé depuis la création de la vidéo. Vérifier les réglages avant un nouvel envoi manuel.')
    text=json.loads((out/'Publication.json').read_text(encoding='utf-8'));record=load_report(out)
    for platform in platforms:
        previous=record['targets'].get(platform,{})
        if previous and previous.get('account_id')!=ids[platform]:raise ValueError('Le compte '+platform+' diffère du reçu existant. Aucun doublon ou changement de destination automatique.')
        resumable=platform=='youtube' and previous.get('youtube_session')
        if previous.get('publish_attempted') and not previous.get('post_id') and not resumable:
            previous.update(status='uncertain',message='Un envoi précédent peut avoir abouti. Contrôler le réseau avant toute nouvelle publication.');save(out,record,changed);continue
        if previous.get('post_id') or (previous.get('status') in ['uncertain','interrupted','published'] and not resumable):continue
        target=record['targets'].setdefault(platform,{'account_id':ids[platform],'status':'pending'})
        target['message']='Préparation de l’envoi.';record.update(status='sending',message='Envoi vers '+platform);save(out,record,changed)
        try:
            if platform=='youtube':youtube_upload(out,text,config,target,lambda:save(out,record,changed))
            elif platform=='instagram':instagram_publish(out,text,config,target,record,changed)
            else:buffer_publish(out,text,config,target,record,mode,changed)
        except Exception as error:
            ambiguous=target.get('publish_attempted') or target.get('youtube_session')
            target.update(status='uncertain' if ambiguous else 'error',message=api.clean_error(error,config));save(out,record,changed)
    record.update(status=summarize(record),message='État des envois enregistré. Un envoi accepté ne vaut pas confirmation de publication.');save(out,record,changed);return public_report(record)

def refresh(out,changed=lambda record:None):
    out=Path(out);record=load_report(out);config=api.load()
    if not config.get('enabled'):return public_report(record)
    text=json.loads((out/'Publication.json').read_text(encoding='utf-8'))
    for platform,target in record['targets'].items():
        if target.get('status') not in ['submitted','scheduled','processing'] and not(platform=='instagram' and target.get('status')=='uncertain' and target.get('container_id')) and not(target.get('post_id') and target.get('status')=='error'):continue
        if target.get('account_id')!=account_ids(config)[platform]:continue
        try:
            if platform=='youtube' and target.get('post_id'):
                data,_=api.request_json('GET','https://www.googleapis.com/youtube/v3/videos',config,headers={'Authorization':'Bearer '+api.youtube_token(config)},params={'part':'status','id':target['post_id']})
                if not data.get('items'):raise ValueError('Vidéo YouTube absente de cette chaîne.')
                status=data['items'][0]['status'];target['remote_status']=status.get('uploadStatus');target['visibility']=status.get('privacyStatus')
                if status.get('uploadStatus') in ['rejected','failed','deleted']:target.update(status='error',message='YouTube signale un refus ou un échec de traitement.')
                elif status.get('uploadStatus')=='processed':target.update(status='published',message='Vidéo disponible sur YouTube · visibilité '+str(status.get('privacyStatus')))
            elif platform=='instagram':instagram_publish(out,text,config,target,record,changed)
            elif platform=='tiktok' and target.get('post_id'):
                post=api.buffer_query('query Status($input: PostInput!) { post(input:$input) { id status externalLink } }',{'input':{'id':target['post_id']}},config)['post']
                target.update(remote_status=post['status'],url=post.get('externalLink') or target.get('url',''))
                target['status']='published' if post['status']=='sent' else 'error' if post['status'] in ['error','draft','needs_approval'] else 'scheduled'
                target['message']='Publication TikTok confirmée par Buffer.' if post['status']=='sent' else 'État Buffer : '+post['status']
        except Exception as error:
            if target.get('publish_attempted') and not target.get('post_id'):
                target.update(status='uncertain')
            target['message']=api.clean_error(error,config)
    record.update(status=summarize(record),last_checked=time.time());save(out,record,changed);return public_report(record)
