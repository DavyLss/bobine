"""Shared validation for manual batches and CSV imports (no uploads on disk)."""
import csv,io,unicodedata
from typing import Literal
from pydantic import BaseModel,ConfigDict,Field,ValidationError,field_validator,model_validator

VOICE_ID='Narrateur-Homme-01'
VOICES=[{'id':VOICE_ID,'name':'Narrateur homme · français','description':'Voix synthétique masculine de référence'},{'id':'Narratrice-Femme-01','name':'Narratrice femme · français','description':'Voix synthétique féminine de référence'}]
MAX_BATCH=500
MAX_PENDING=500

class VideoSettings(BaseModel):
    model_config=ConfigDict(extra='forbid')
    theme:Literal['dark','light']='dark'
    duration:int=Field(default=90,ge=15,le=180)
    format:Literal['reel','standard']='reel'
    voice:Literal['Narrateur-Homme-01','Narratrice-Femme-01']=VOICE_ID
    auto_publish:bool=False
    publish_platforms:list[Literal['youtube','instagram','tiktok']]=Field(default_factory=list,max_length=3)
    publish_mode:Literal['queue','now']='queue'

    @model_validator(mode='after')
    def publication_options(self):
        if len(self.publish_platforms)!=len(set(self.publish_platforms)):raise ValueError('Réseau de publication en double.')
        return self

class VideoRequest(VideoSettings):
    title:str=Field(min_length=3,max_length=120)
    description:str=Field(min_length=10,max_length=6000)

    @field_validator('title','description',mode='before')
    @classmethod
    def trim(cls,value):
        return value.strip() if isinstance(value,str) else value

class BatchRequest(BaseModel):
    model_config=ConfigDict(extra='forbid')
    name:str=Field(default='',max_length=120)
    defaults:VideoSettings=Field(default_factory=VideoSettings)
    items:list[dict]=Field(default_factory=list,max_length=MAX_BATCH)
    csv:str|None=Field(default=None,max_length=1_000_000)

    @model_validator(mode='after')
    def one_source(self):
        if bool(self.items)==(self.csv is not None):
            raise ValueError('Fournir soit une liste de vidéos, soit un CSV.')
        return self

def normalize(value):
    return ''.join(c for c in unicodedata.normalize('NFD',value.strip().lower()) if not unicodedata.combining(c))

HEADERS={'title':'title','titre':'title','description':'description','theme':'theme','charte':'theme','direction':'theme','duration':'duration','duree':'duration','format':'format','voice':'voice','voix':'voice','auto_publish':'auto_publish','publication_auto':'auto_publish','publish_platforms':'publish_platforms','reseaux':'publish_platforms','publish_mode':'publish_mode','mode_publication':'publish_mode'}
ALIASES={
    'theme':{'dark':'dark','sombre':'dark','atelier sombre':'dark','light':'light','clair':'light','editorial clair':'light'},
    'format':{'reel':'reel','reels':'reel','9:16':'reel','standard':'standard','16:9':'standard'},
    'voice':{normalize(VOICE_ID):VOICE_ID,'homme':VOICE_ID,'narrateur homme':VOICE_ID,'narratrice-femme-01':'Narratrice-Femme-01','femme':'Narratrice-Femme-01','narratrice femme':'Narratrice-Femme-01'},
}

def csv_rows(content):
    content=content.lstrip('\ufeff')
    if '\x00' in content:raise ValueError('Le fichier doit être un CSV texte UTF-8.')
    try:dialect=csv.Sniffer().sniff(content[:8192],delimiters=',;\t')
    except csv.Error:dialect=csv.excel
    reader=csv.reader(io.StringIO(content,newline=''),dialect,strict=True)
    try:
        header=next(reader,[])
        columns=[HEADERS.get(normalize(value)) for value in header]
        if not header:raise ValueError('Le CSV est vide.')
        if None in columns:raise ValueError('Colonne inconnue : '+', '.join(h for h,c in zip(header,columns) if c is None))
        if len(columns)!=len(set(columns)):raise ValueError('Le CSV contient des colonnes en double.')
        if not {'title','description'}<=set(columns):raise ValueError('Colonnes obligatoires : titre et description.')
        rows=[];previous_line=reader.line_num
        for row in reader:
            line=previous_line+1;previous_line=reader.line_num
            if not any(value.strip() for value in row):continue
            if len(row)!=len(columns):raise ValueError(f'Ligne {line} : nombre de cellules incorrect (utiliser des guillemets autour des textes contenant le séparateur).')
            rows.append((line,dict(zip(columns,row))))
            if len(rows)>MAX_BATCH:raise ValueError(f'Un lot contient au maximum {MAX_BATCH} vidéos.')
        if not rows:raise ValueError('Le CSV ne contient aucune vidéo.')
        return rows
    except csv.Error as error:raise ValueError(f'Ligne {reader.line_num} : CSV mal formé ({error}).') from error

def validate_batch(body):
    rows=csv_rows(body.csv) if body.csv is not None else list(enumerate(body.items,1))
    items=[];errors=[]
    for line,row in rows:
        values=body.defaults.model_dump()
        for key,value in row.items():
            if isinstance(value,str):value=value.strip()
            if value=='' and key in values:continue
            if key=='publish_platforms' and isinstance(value,str):value=[s.strip().lower() for s in value.split('|') if s.strip()]
            if key=='auto_publish' and isinstance(value,str):value={'oui':True,'non':False}.get(normalize(value),value)
            if key in ALIASES and isinstance(value,str):value=ALIASES[key].get(normalize(value),value)
            values[key]=value
        try:items.append(VideoRequest.model_validate(values).model_dump())
        except ValidationError as error:
            fields=', '.join(dict.fromkeys(str(e['loc'][0]) if e['loc'] else 'publication_auto / réseaux / format' for e in error.errors()))
            errors.append(f'Ligne {line} : vérifier {fields}. Durée entière de 15 à 180 s ; charte dark/light ; format reel/standard ; voix Narrateur-Homme-01/Narratrice-Femme-01. Titre de 3 à 120 caractères, description de 10 à 6 000 caractères.')
    if errors:raise ValueError('\n'.join(errors))
    return items,[line for line,_ in rows]

def batch_summary(batch,jobs):
    ordered=sorted((job for job in jobs if job.get('batch_id')==batch['id']),key=lambda job:job['batch_index'])
    counts={status:sum(job['status']==status for job in ordered) for status in ['queued','running','done','failed','cancelled','interrupted']}
    total=len(ordered);finished=total-counts['queued']-counts['running']
    status='running' if counts['running'] else 'queued' if counts['queued'] else 'done' if counts['done']==total else 'finished'
    progress=round((finished*100+sum(job['progress'] for job in ordered if job['status']=='running'))/total) if total else 0
    return {**batch,'job_ids':[job['id'] for job in ordered],'counts':counts,'total':total,'finished':finished,'progress':progress,'status':status}
