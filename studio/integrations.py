"""Local API settings, protected secrets, Google OAuth and read-only connection checks."""
import base64,ctypes,json,os,re,secrets,threading,time
from pathlib import Path
from urllib.parse import urlencode
from typing import Literal
import requests
from pydantic import BaseModel,ConfigDict,Field,SecretStr
from config import DATA,PORT

LOCK=threading.RLock();FILE=DATA/'integrations.json';PENDING_OAUTH={}
SECRET_KEYS=['youtube_client_secret','youtube_refresh_token','youtube_access_token','instagram_token','instagram_app_secret','buffer_token','cloudinary_api_key','cloudinary_api_secret']
DEFAULTS={'enabled':False,'youtube_client_id':'','youtube_privacy':'public','youtube_made_for_kids':False,'instagram_user_id':'','instagram_version':'v27.0','buffer_organization_id':'','buffer_tiktok_channel':'','buffer_channels':[],'cloudinary_cloud_name':'','ai_disclosure':True,'tiktok_cover':True}

class SettingsInput(BaseModel):
    model_config=ConfigDict(extra='forbid')
    enabled:bool=False
    youtube_client_id:str=Field(default='',max_length=250)
    youtube_client_secret:SecretStr|None=None
    youtube_privacy:Literal['public','unlisted','private']='public'
    youtube_made_for_kids:bool=False
    instagram_user_id:str=Field(default='',pattern=r'^\d{0,30}$')
    instagram_version:str=Field(default='v27.0',pattern=r'^v\d{1,2}\.0$')
    instagram_token:SecretStr|None=None
    instagram_app_secret:SecretStr|None=None
    buffer_token:SecretStr|None=None
    buffer_organization_id:str=Field(default='',pattern=r'^(?:[a-f0-9]{24})?$')
    buffer_tiktok_channel:str=Field(default='',pattern=r'^(?:[a-f0-9]{24})?$')
    cloudinary_cloud_name:str=Field(default='',pattern=r'^[a-zA-Z0-9_-]{0,100}$')
    cloudinary_api_key:SecretStr|None=None
    cloudinary_api_secret:SecretStr|None=None
    ai_disclosure:bool=True
    tiktok_cover:bool=True

def protect(raw,decrypt=False):
    """DPAPI binds Windows credentials to this user's session; no extra package."""
    if os.name!='nt':return raw
    from ctypes import wintypes
    class Blob(ctypes.Structure):_fields_=[('size',wintypes.DWORD),('data',ctypes.POINTER(ctypes.c_ubyte))]
    source=(ctypes.c_ubyte*len(raw)).from_buffer_copy(raw);incoming=Blob(len(raw),source);outgoing=Blob()
    function=ctypes.windll.crypt32.CryptUnprotectData if decrypt else ctypes.windll.crypt32.CryptProtectData
    if not function(ctypes.byref(incoming),None,None,None,None,1,ctypes.byref(outgoing)):raise OSError('Protection Windows des identifiants indisponible.')
    try:return ctypes.string_at(outgoing.data,outgoing.size)
    finally:ctypes.windll.kernel32.LocalFree(outgoing.data)

def load():
    with LOCK:
        stored=json.loads(FILE.read_text(encoding='utf-8')) if FILE.exists() else {}
        config={**DEFAULTS,**stored.get('settings',{})}
        if stored.get('secrets'):
            raw=base64.b64decode(stored['secrets'])
            if stored.get('protection')=='windows-dpapi':raw=protect(raw,True)
            config.update(json.loads(raw))
        env={'buffer_token':'BUFFER_API_KEY','instagram_token':'INSTAGRAM_ACCESS_TOKEN','cloudinary_cloud_name':'CLOUDINARY_CLOUD_NAME','cloudinary_api_key':'CLOUDINARY_API_KEY','cloudinary_api_secret':'CLOUDINARY_API_SECRET'}
        for field,name in env.items():
            if os.environ.get(name):config[field]=os.environ[name]
        return config

def store(config):
    with LOCK:
        FILE.parent.mkdir(parents=True,exist_ok=True)
        private={key:config[key] for key in SECRET_KEYS if config.get(key)}
        payload={'settings':{key:value for key,value in config.items() if key not in SECRET_KEYS},'protection':'windows-dpapi' if os.name=='nt' else 'file-permissions','secrets':base64.b64encode(protect(json.dumps(private).encode())).decode()}
        temporary=FILE.with_suffix('.tmp');temporary.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')
        if os.name!='nt':temporary.chmod(0o600)
        temporary.replace(FILE)

def save_settings(body):
    with LOCK:
        config=load();values=body.model_dump()
        old_client=config.get('youtube_client_id')
        for key,value in values.items():
            if isinstance(value,SecretStr):
                if value.get_secret_value().strip():config[key]=value.get_secret_value().strip()
            elif key not in SECRET_KEYS:config[key]=value
        if old_client!=config['youtube_client_id']:
            for key in ['youtube_refresh_token','youtube_access_token','youtube_expires_at','youtube_channel_name']:config.pop(key,None)
        store(config);return public_settings(config)

def public_settings(config=None):
    config=config or load();result={key:value for key,value in config.items() if key not in SECRET_KEYS and not key.startswith('youtube_access')}
    result['credentials']={key:bool(config.get(key)) for key in SECRET_KEYS}
    result['youtube_connected']=bool(config.get('youtube_refresh_token'))
    result['protection']='Windows DPAPI' if os.name=='nt' else 'Fichier local, permissions 0600 (non chiffré)'
    result['youtube_redirect_uri']=f'http://127.0.0.1:{PORT}/api/social/youtube/callback'
    result['ready']={platform:not missing(config,[platform]) for platform in ['youtube','instagram','tiktok']}
    return result

def missing(config,platforms):
    needs=[]
    if not config.get('enabled'):needs.append('Activer les envois dans les réglages de publication.')
    if 'youtube' in platforms and not (config.get('youtube_client_id') and config.get('youtube_client_secret') and config.get('youtube_refresh_token') and config.get('youtube_channel_id')):needs.append('Connecter YouTube par OAuth et tester la chaîne.')
    if 'instagram' in platforms and not(config.get('instagram_token') and config.get('instagram_user_id')):needs.append('Renseigner et tester le compte professionnel Instagram.')
    if 'tiktok' in platforms and not(config.get('buffer_token') and config.get('buffer_tiktok_channel')):needs.append('Renseigner Buffer et choisir le canal TikTok.')
    if {'instagram','tiktok'}&set(platforms) and not all(config.get(key) for key in ['cloudinary_cloud_name','cloudinary_api_key','cloudinary_api_secret']):needs.append('Renseigner Cloudinary pour les URL publiques Instagram/TikTok.')
    return needs

def clean_error(message,config=None):
    message=str(message)
    for key in SECRET_KEYS:
        secret=(config or {}).get(key)
        if secret:message=message.replace(secret,'[secret masqué]')
    return re.sub(r'(access_token|refresh_token|client_secret)=[^&\s]+',r'\1=[masqué]',message)[:800]

def request_json(method,url,config=None,**kwargs):
    try:
        response=requests.request(method,url,timeout=kwargs.pop('timeout',(10,60)),allow_redirects=False,**kwargs)
        data=response.json()
    except (requests.RequestException,ValueError) as error:raise RuntimeError('Réponse réseau indisponible ou illisible. Vérifier la connexion avant toute nouvelle publication.') from error
    if not 200<=response.status_code<300:
        error=data.get('error',{});message=error.get('message') if isinstance(error,dict) else data.get('error_description',str(error))
        raise RuntimeError(clean_error(f'API HTTP {response.status_code} : {message or "vérifier les autorisations et quotas"}',config))
    return data,response

def buffer_query(query,variables=None,config=None):
    config=config or load()
    data,_=request_json('POST','https://api.buffer.com',config,headers={'Authorization':'Bearer '+config.get('buffer_token','')},json={'query':query,'variables':variables or {}})
    if data.get('errors'):raise RuntimeError(clean_error('; '.join(e.get('message','Erreur Buffer') for e in data['errors']),config))
    return data['data']

def discover_buffer():
    with LOCK:
        config=load()
        if not config.get('buffer_token'):raise ValueError('Renseigner la clé Buffer et enregistrer les réglages.')
        orgs=buffer_query('query { account { organizations { id } } }',config=config)['account']['organizations']
        channels=[]
        for org in orgs:
            result=buffer_query('query Channels($input: ChannelsInput!) { channels(input:$input) { id name displayName service isQueuePaused } }',{'input':{'organizationId':org['id']}},config)
            channels.extend({**channel,'organization_id':org['id']} for channel in result['channels'] if channel['service']=='tiktok')
        config['buffer_channels']=channels;store(config)
        return channels

def youtube_authorize():
    config=load()
    if not(config.get('youtube_client_id') and config.get('youtube_client_secret')):raise ValueError('Enregistrer le Client ID et le secret OAuth Google.')
    nonce=secrets.token_urlsafe(32);verifier=secrets.token_urlsafe(64)
    import hashlib
    challenge=base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).decode().rstrip('=')
    redirect=public_settings(config)['youtube_redirect_uri']
    with LOCK:
        for key,value in list(PENDING_OAUTH.items()):
            if time.time()-value['created']>600:PENDING_OAUTH.pop(key,None)
        PENDING_OAUTH[nonce]={'created':time.time(),'verifier':verifier,'redirect':redirect,'client':config['youtube_client_id']}
    url='https://accounts.google.com/o/oauth2/v2/auth?'+urlencode({'client_id':config['youtube_client_id'],'redirect_uri':redirect,'response_type':'code','scope':'https://www.googleapis.com/auth/youtube.upload https://www.googleapis.com/auth/youtube.readonly','access_type':'offline','prompt':'consent','state':nonce,'code_challenge':challenge,'code_challenge_method':'S256'})
    return {'url':url}

def youtube_callback(code,state):
    with LOCK:pending=PENDING_OAUTH.pop(state,None)
    config=load()
    if not pending or time.time()-pending['created']>600 or pending['client']!=config.get('youtube_client_id'):raise ValueError('Connexion expirée ou état OAuth invalide. Relancer la connexion depuis le studio.')
    data,_=request_json('POST','https://oauth2.googleapis.com/token',config,data={'client_id':config['youtube_client_id'],'client_secret':config['youtube_client_secret'],'code':code,'redirect_uri':pending['redirect'],'grant_type':'authorization_code','code_verifier':pending['verifier']})
    if not data.get('refresh_token'):raise ValueError('Google ne fournit pas de refresh token. Réautoriser avec consentement hors ligne.')
    config.update(youtube_refresh_token=data['refresh_token'],youtube_access_token=data['access_token'],youtube_expires_at=time.time()+data.get('expires_in',3600));store(config)
    return test_connection('youtube')

def youtube_token(config):
    if config.get('youtube_access_token') and config.get('youtube_expires_at',0)>time.time()+90:return config['youtube_access_token']
    data,_=request_json('POST','https://oauth2.googleapis.com/token',config,data={'client_id':config['youtube_client_id'],'client_secret':config['youtube_client_secret'],'refresh_token':config['youtube_refresh_token'],'grant_type':'refresh_token'})
    config.update(youtube_access_token=data['access_token'],youtube_expires_at=time.time()+data.get('expires_in',3600))
    with LOCK:
        current=load()
        if current.get('youtube_client_id')==config.get('youtube_client_id') and current.get('youtube_refresh_token')==config.get('youtube_refresh_token'):
            current.update({key:config[key] for key in ['youtube_access_token','youtube_expires_at']});store(current)
    return config['youtube_access_token']

def test_connection(platform):
    config=load()
    if platform=='youtube':
        data,_=request_json('GET','https://www.googleapis.com/youtube/v3/channels',config,headers={'Authorization':'Bearer '+youtube_token(config)},params={'part':'snippet','mine':'true'})
        if len(data.get('items',[]))!=1:raise ValueError('Aucune chaîne YouTube unique associée à cette autorisation.')
        item=data['items'][0];config.update(youtube_channel_name=item['snippet']['title'],youtube_channel_id=item['id']);store(config)
        return {'message':'YouTube connecté : '+item['snippet']['title']}
    if platform=='instagram':
        data,_=request_json('GET',f"https://graph.instagram.com/{config['instagram_version']}/me",config,headers={'Authorization':'Bearer '+config.get('instagram_token','')},params={'fields':'user_id,username'})
        if isinstance(data.get('data'),list):
            if len(data['data'])!=1:raise ValueError('Plusieurs comptes Instagram retournés : préciser le compte professionnel.')
            data=data['data'][0]
        identifier=str(data.get('user_id') or data.get('id') or '')
        if not identifier.isdigit():raise ValueError('Identifiant Instagram professionnel absent.')
        config.update(instagram_user_id=identifier,instagram_username=data.get('username',''));store(config)
        return {'message':'Instagram connecté : '+data.get('username',identifier),'user_id':identifier}
    if platform=='buffer':return {'channels':discover_buffer(),'message':'Canaux TikTok récupérés depuis Buffer.'}
    if platform=='cloudinary':
        _,_=request_json('GET',f"https://api.cloudinary.com/v1_1/{config.get('cloudinary_cloud_name','')}/ping",config,auth=(config.get('cloudinary_api_key',''),config.get('cloudinary_api_secret','')))
        return {'message':'Cloudinary connecté. Aucun média envoyé pendant ce test.'}
    raise ValueError('Service inconnu.')

def instagram_exchange():
    config=load()
    if not config.get('instagram_app_secret') or not config.get('instagram_token'):raise ValueError('Enregistrer le jeton court et le secret de l’application Instagram.')
    data,_=request_json('GET','https://graph.instagram.com/access_token',config,params={'grant_type':'ig_exchange_token','client_secret':config['instagram_app_secret'],'access_token':config['instagram_token']})
    config.update(instagram_token=data['access_token'],instagram_expires_at=time.time()+data.get('expires_in',60*86400),instagram_refreshed_at=time.time());store(config)
    return {'message':'Jeton Instagram longue durée enregistré.','expires_at':config['instagram_expires_at']}

def refresh_instagram(config):
    if config.get('instagram_expires_at',0)>time.time()+7*86400:return
    if not config.get('instagram_expires_at') or time.time()-config.get('instagram_refreshed_at',0)<86400:return
    previous_token=config['instagram_token']
    data,_=request_json('GET','https://graph.instagram.com/refresh_access_token',config,params={'grant_type':'ig_refresh_token','access_token':previous_token})
    config.update(instagram_token=data['access_token'],instagram_expires_at=time.time()+data.get('expires_in',60*86400),instagram_refreshed_at=time.time())
    with LOCK:
        current=load()
        if current.get('instagram_token')==previous_token:
            current.update({key:config[key] for key in ['instagram_token','instagram_expires_at','instagram_refreshed_at']});store(current)
