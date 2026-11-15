"""Les trois voies du DevOps : théâtre d'objets original, rendu entièrement local."""
from pathlib import Path
import argparse,json,math
import numpy as np
from PIL import Image,ImageDraw
from moviepy import VideoClip,AudioFileClip
import Mouvement as m
HERE=Path(__file__).resolve().parent;W,H=1080,1920
CREAM='#F4E8CC';GOLD='#E4B75B';PINK='#CB4F78';TEAL='#69AAA4';DIM='#A49A8C';DARK='#29221E'
def tx(d,x,y,s,size=42,c=CREAM,anchor='mm'):m.text(d,x,y,s,size,c,True,anchor)
def block(d,xy,fill=DARK,outline='#564438',r=24,width=3):m.box(d,xy,fill,r,outline,width)
def arrow(d,a,b,c=GOLD,w=7):
    d.line((*a,*b),fill=c,width=w);angle=math.atan2(b[1]-a[1],b[0]-a[0]);r=20
    d.polygon([b,(b[0]-r*math.cos(angle-.5),b[1]-r*math.sin(angle-.5)),(b[0]-r*math.cos(angle+.5),b[1]-r*math.sin(angle+.5))],fill=c)
def check(d,x,y,s=1,c=TEAL,p=1):
    p=m.ease(p);d.line((x-24*s,y,x-4*s,y+20*s,x-4*s+47*s*p,y+20*s-57*s*p),fill=c,width=max(3,round(9*s)))
def package(d,x,y,s=1,c=GOLD):
    rr=28*s;block(d,(x-rr,y-rr,x+rr,y+rr),c,c,round(8*s));d.line((x,y-rr,x,y+rr),fill='#74542E',width=max(2,round(5*s)))
def laptop(d,x,y,s=1):
    block(d,(x-57*s,y-42*s,x+57*s,y+35*s),'#1E3236',CREAM,8,4)
    d.line((x-72*s,y+43*s,x+72*s,y+43*s),fill=CREAM,width=round(8*s))
    tx(d,x,y-2*s,'</>',round(32*s),TEAL)
def server(d,x,y,s=1,alert=False):
    for j in range(3):
        yy=y-49*s+j*42*s;block(d,(x-50*s,yy,x+50*s,yy+32*s),'#3D4342',CREAM,6,2)
        d.ellipse((x-36*s,yy+11*s,x-25*s,yy+22*s),fill=PINK if alert else TEAL)
        d.line((x-10*s,yy+16*s,x+35*s,yy+16*s),fill=DIM,width=3)
def person(d,x,y,s=1,ok=False):
    d.ellipse((x-25*s,y-58*s,x+25*s,y-8*s),fill=CREAM)
    block(d,(x-46*s,y+1*s,x+46*s,y+60*s),TEAL,TEAL,round(23*s))
    if ok:check(d,x+53*s,y-42*s,.65)
def node(d,x,y,kind,alert=False,delivered=False):
    c=PINK if alert else '#564438';block(d,(x-91,y-105,x+91,y+105),outline=c)
    if kind==0:laptop(d,x,y)
    elif kind==1:
        block(d,(x-48,y-58,x+48,y+62),'#3A3430',CREAM,9)
        if alert:tx(d,x,y,'×',70,PINK)
        else:check(d,x,y,1.2)
    elif kind==2:server(d,x,y,alert=alert)
    else:person(d,x,y,ok=delivered)
    tx(d,x,y+145,['CODE','TESTS','PROD.','UTILISATEUR'][kind],24,DIM)
XS=[136,405,675,944]
def pipeline(im,p=None,blocked=False,alert=False,y=930,delivered=False):
    d=ImageDraw.Draw(im)
    for a,b in zip(XS,XS[1:]):arrow(d,(a+99,y),(b-101,y),DIM,5)
    for j,x in enumerate(XS):node(d,x,y,j,blocked and j==1 or alert and j==2,delivered or p is not None and p>=.99)
    if p is not None:
        x=m.mix(XS[0],XS[-1],max(0,min(1,p)));package(d,x,y-155)
def feedback(im,p,y=930):
    d=ImageDraw.Draw(im);path=[(944,775),(944,650),(136,650),(136,775)]
    d.line(path,fill='#57404A',width=6,joint='curve');arrow(d,(136,721),(136,775),PINK,6)
    # Three segments, constant speed along the return path.
    lengths=[125,808,125];dist=max(0,min(1,p))*sum(lengths)
    for a,b,length in zip(path,path[1:],lengths):
        if dist<=length:
            q=dist/length;x=m.mix(a[0],b[0],q);yy=m.mix(a[1],b[1],q);break
        dist-=length
    d.ellipse((x-16,yy-16,x+16,yy+16),fill=PINK)
def flask(d,x,y,s=1,p=1):
    points=[(x-28*s,y-90*s),(x+28*s,y-90*s),(x+28*s,y-25*s),(x+83*s,y+77*s),(x+70*s,y+92*s),(x-70*s,y+92*s),(x-83*s,y+77*s),(x-28*s,y-25*s)]
    d.polygon(points,fill='#303D3B');d.line(points+[points[0]],fill=CREAM,width=max(3,round(6*s)),joint='curve')
    pp=m.ease(p);d.polygon([(x-58*s,y+65*s),(x+58*s,y+65*s),(x+35*s,y+(65-68*pp)*s),(x-35*s,y+(65-68*pp)*s)],fill=TEAL)
    d.line((x-40*s,y-93*s,x+40*s,y-93*s),fill=CREAM,width=max(3,round(7*s)))
def background():
    yy,xx=np.mgrid[:H,:W];g=np.exp(-((xx-540)**2/(2*470**2)+(yy-850)**2/(2*630**2)))
    return Image.fromarray((np.array([16,17,21])+g[...,None]*np.array([27,19,12])).astype('uint8')).convert('RGBA')
def booking(im,x,y,w=690,h=510,button=True,error=False):
    d=ImageDraw.Draw(im);block(d,(x-w/2,y-h/2,x+w/2,y+h/2),outline=PINK if error else TEAL)
    tx(d,x,y-h/2+54,'MA RÉSERVATION',round(w*.046),TEAL)
    d.line((x-w/2+30,y-h/2+96,x+w/2-30,y-h/2+96),fill='#564438',width=3)
    tx(d,x,y-28,'SAMEDI · 14 H',round(w*.055))
    tx(d,x,y+32,'2 personnes',round(w*.039),DIM)
    if button:
        block(d,(x-w*.31,y+h*.20,x+w*.31,y+h*.38),PINK if error else TEAL,PINK if error else TEAL,12)
        tx(d,x,y+h*.29,'ERREUR' if error else 'ANNULER',round(w*.045))
def teammates(im,x1,x2,y,wall=False):
    d=ImageDraw.Draw(im);person(d,x1,y,1.35);person(d,x2,y,1.35)
    laptop(d,x1,y+175,1.15);server(d,x2,y+175,1.15)
    tx(d,x1,y-140,'DÉVELOPPEMENT',28,GOLD);tx(d,x2,y-140,'EXPLOITATION',28,TEAL)
    if wall:
        for j in range(6):block(d,(526,y-175+j*64,554,y-126+j*64),'#5B4547','#5B4547',4)
    else:arrow(d,(x1+100,y+10),(x2-100,y+10),GOLD,7);arrow(d,(x2-100,y+55),(x1+100,y+55),TEAL,7)

class Film:
    def __init__(self):
        self.scenes=json.loads((HERE/'Scenario.json').read_text(encoding='utf-8'))['scenes'];self.bg=background()
        self.timing=json.loads((HERE/'Chronologie.json').read_text(encoding='utf-8')) if (HERE/'Chronologie.json').exists() else [{'start':i*7.5,'end':i*7.5+7,'text':s['text']} for i,s in enumerate(self.scenes)]
        self.starts=[s['start'] for s in self.timing];self.duration=self.timing[-1]['end']+1.1
        if (HERE/'Narration.wav').exists():
            with AudioFileClip(str(HERE/'Narration.wav')) as a:self.duration=a.duration
        self.words=json.loads((HERE/'Mots-alignes.json').read_text(encoding='utf-8'))['words'] if (HERE/'Mots-alignes.json').exists() else []
        self.groups=[]
        for k in range(12):
            ws=[w for w in self.words if w['cue']==k]
            for j in range(0,len(ws),3):self.groups.append(ws[j:j+3])
    def frame(self,t):
        t=float(t);k=max(0,min(11,int(np.searchsorted(self.starts,t,side='right')-1)));u=max(0,t-self.starts[k]);im=self.bg.copy();d=ImageDraw.Draw(im)
        tx(d,540,123,'C’EST QUOI LE DEVOPS ?',27,DIM)
        group=next((g for g in self.groups if g[0]['start']-.04<=t<=g[-1]['end']+.13),None)
        if group:
            layer=Image.new('RGBA',(W,H));dd=ImageDraw.Draw(layer);size=57;words=[w['text'].upper() for w in group]
            widths=[dd.textlength(s,font=m.font(size)) for s in words];total=sum(widths)+19*(len(words)-1)
            if total>900:size=round(size*900/total);widths=[dd.textlength(s,font=m.font(size)) for s in words];total=sum(widths)+19*(len(words)-1)
            x=(W-total)/2;block(dd,(x-27,286,x+total+27,397),r=20)
            for word,s,width in zip(group,words,widths):
                if word['start']-.02<=t<=word['end']+.05:block(dd,(x-7,300,x+width+7,383),PINK,PINK,8)
                tx(dd,x+width/2,341,s,size);x+=width+19
            m.entrance(im,layer,t-group[0]['start']+.03,'caption')
        chapter=0 if k in [2,3,5] else 1 if k==6 else 2 if k in [7,8] else None
        titles=['ÇA MARCHE CHEZ MOI…','QUAND LES ÉQUIPES S’ISOLENT','DEV + OPS = COLLABORER','UN OBJECTIF PARTAGÉ','UN EXEMPLE CONCRET','PRÉPARER ENSEMBLE','AUTOMATISER CE QUI AIDE','RESTER RESPONSABLE APRÈS','CORRIGER ET APPRENDRE','LES OUTILS NE SUFFISENT PAS','LE SERVICE, DE BOUT EN BOUT','ET DANS VOTRE ÉQUIPE ?']
        tx(d,540,525,titles[k],36,GOLD if k in [0,4,11] else CREAM)
        layer=Image.new('RGBA',(W,H));dd=ImageDraw.Draw(layer)
        if k==0:
            for j,(name,c) in enumerate([('CHEZ MOI',TEAL),('EN LIGNE',PINK)]):
                x=295+j*490;block(dd,(x-175,730,x+175,1125),outline=c);tx(dd,x,785,name,31,c)
                if j==0:laptop(dd,x,925,1.65);check(dd,x,1060,.8)
                else:server(dd,x,925,1.65,alert=True);tx(dd,x,1060,'×',60,PINK)
            if u>1:package(dd,540,920,.8);arrow(dd,(480,920),(600,920),PINK,6)
            tx(dd,540,1305,'LE LOGICIEL DOIT AUSSI VIVRE EN LIGNE.',30,DIM)
        elif k==1:
            teammates(layer,285,795,865,True)
            tx(dd,285,1240,'NOUVEAUTÉS',32,GOLD);tx(dd,795,1240,'DISPONIBILITÉ',31,TEAL)
            tx(dd,540,1370,'SANS ÉCHANGE, LES RISQUES S’ACCUMULENT.',29,PINK)
        elif k==2:
            p=m.ease((u-.7)/1.4);teammates(layer,m.mix(250,320,p),m.mix(830,760,p),900,p<.9)
            tx(dd,540,1300,'UNE CULTURE + DES PRATIQUES + DES OUTILS',28,TEAL)
        elif k==3:
            for j,(name,c) in enumerate([('UTILE',GOLD),('RAPIDE',PINK),('FIABLE',TEAL)]):
                p=m.spring((u-j*.25)/.5);x=205+j*335;yy=930+110*(1-p)
                if p>0:
                    block(dd,(x-145,yy-150,x+145,yy+150),outline=c);tx(dd,x,yy-65,name,32,c)
                    if j==0:person(dd,x,yy+30,1)
                    elif j==1:arrow(dd,(x-70,yy+35),(x+70,yy+35),c,14)
                    else:check(dd,x,yy+35,1.55)
            tx(dd,540,1310,'LA RESPONSABILITÉ EST PARTAGÉE.',34,TEAL)
        elif k==4:
            reveal=next((w['start']-self.starts[k] for w in self.words if w['cue']==k and 'bouton' in w['text'].lower()),1.6)
            booking(layer,540,955,button=u>reveal)
            if u>reveal:
                p=m.ease((u-reveal)/.55);dd.ellipse((540-160*p,1103-53*p,540+160*p,1103+53*p),outline=GOLD,width=4)
            tx(dd,540,1330,'UN NOUVEAU BOUTON À LIVRER.',34,GOLD)
        elif k==5:
            block(dd,(338,840,742,1035),outline=GOLD);tx(dd,540,937,'ANNULER',45,GOLD)
            for j,(name,x,y,c) in enumerate([('DEV',250,725,GOLD),('OPS',830,725,TEAL),('QUALITÉ',250,1160,PINK),('SÉCURITÉ',830,1160,TEAL)]):
                p=m.ease((u-j*.4)/.4)
                if p>0:
                    arrow(dd,(x,y),(540+(x-540)*.42,937+(y-937)*.5),c,5)
                    block(dd,(x-135,y-65,x+135,y+65),outline=c);tx(dd,x,y,name,28,c)
                    if u>1.5+j*.4:check(dd,x+100,y-42,.5,c)
            tx(dd,540,1370,'ANTICIPER LES RISQUES ENSEMBLE.',32,TEAL)
        elif k==6:
            deploy=next((w['start']-self.starts[k] for w in self.words if w['cue']==k and 'déploy' in w['text'].lower()),3.0)
            p=m.ease((u-.3)/1.6)/3 if u<deploy else 1/3+2/3*m.ease((u-deploy)/1.8)
            pipeline(layer,p=p)
            tx(dd,540,1270,'TESTER → DÉPLOYER → VÉRIFIER',35,TEAL)
            tx(dd,540,1350,'Une procédure que l’on peut reproduire.',28,DIM)
        elif k==7:
            booking(layer,350,965,450,490)
            block(dd,(650,745,1005,1035),outline=TEAL);tx(dd,825,790,'SURVEILLER',27,TEAL)
            pts=[(680,965),(730,945),(775,950),(820,895),(865,918),(910,865),(975,880)]
            n=max(2,min(len(pts),int(u*2)+2));dd.line(pts[:n],fill=TEAL,width=7)
            person(dd,830,1180,1)
            if u>1.5:arrow(dd,(760,1240),(560,1240),PINK,7)
            tx(dd,540,1380,'LIVRER, PUIS OBSERVER ET ÉCOUTER.',32,TEAL)
        elif k==8:
            repair=next((w['start']-self.starts[k] for w in self.words if w['cue']==k and 'corrige' in w['text'].lower()),3.1)
            fixed=u>repair;booking(layer,540,940,error=not fixed)
            if fixed:check(dd,540,1275,1.4,p=(u-repair)/.5)
            else:tx(dd,540,1280,'SIGNAL → ÉQUIPE → CORRECTION',32,PINK)
            tx(dd,540,1390,'LE RETOUR AMÉLIORE LA SUITE.',33,TEAL)
        elif k==9:
            for j,(name,c) in enumerate([('COLLABORER',GOLD),('AUTOMATISER',PINK),('APPRENDRE',TEAL)]):
                p=m.ease((u-j*.35)/.45)
                if p>0:
                    yy=750+j*235+75*(1-p);block(dd,(180,yy-80,900,yy+80),outline=c);tx(dd,540,yy,name,46,c)
                    if j<2:arrow(dd,(540,yy+95),(540,yy+130),DIM,5)
            tx(dd,540,1390,'LES OUTILS SOUTIENNENT LE TRAVAIL COMMUN.',28,DIM)
        elif k==10:
            pipeline(layer,p=m.ease(u/2.7))
            if u>2.7:feedback(layer,m.ease((u-2.7)/2.3))
            tx(dd,540,1280,'UN LOGICIEL + UN SERVICE À FAIRE VIVRE',31,TEAL)
            tx(dd,540,1370,'AMÉLIORER EN CONTINU, ENSEMBLE.',33,GOLD)
        else:
            teammates(layer,300,780,860,False)
            block(dd,(160,1170,920,1390),outline=GOLD)
            tx(dd,540,1240,'QUEL OBSTACLE ENLEVER ?',35,GOLD)
            if u>1:tx(dd,540,1320,'Une première amélioration, ensemble.',29)
        m.entrance(im,layer,u-.04) if k not in [6,8,10] else im.alpha_composite(layer)
        d=ImageDraw.Draw(im)
        for j,(name,c) in enumerate(zip(['COLLABORER','AUTOMATISER','APPRENDRE'],[GOLD,PINK,TEAL])):
            x=205+j*335;active=(chapter==j or k>=9);block(d,(x-145,1560,x+145,1640),outline=c if active else '#403831',r=17);tx(d,x,1600,name,23,c if active else DIM)
        tx(d,540,1775,'DEVOPS EN CLAIR · SOURCES : MICROSOFT / ATLASSIAN',19,DIM)
        if t>self.duration-.5:im=Image.blend(self.bg,im,max(0,(self.duration-t)/.5))
        return np.asarray(im.convert('RGB'))
def main():
    p=argparse.ArgumentParser();p.add_argument('--preview',action='store_true');a=p.parse_args();f=Film();control=HERE/'Controle';control.mkdir(exist_ok=True)
    for i,s in enumerate(f.timing):
        t=s['start']+min(3,(s['end']-s['start'])/2);Image.fromarray(f.frame(t)).save(control/f'Plan-{i+1:02}.jpg',quality=92)
    start=f.starts[8] if a.preview else 0;end=min(f.duration,start+10) if a.preview else f.duration
    clip=VideoClip(frame_function=lambda t:f.frame(t+start),duration=end-start);audio=None
    if (HERE/'Narration.wav').exists():audio=AudioFileClip(str(HERE/'Narration.wav')).subclipped(start,end);clip=clip.with_audio(audio)
    target=HERE/('Essai-Visuel.mp4' if a.preview else 'DevOps-Cest-Quoi.mp4')
    clip.write_videofile(str(target),fps=30,codec='h264_nvenc',audio_codec='aac' if audio else None,audio_bitrate='192k',ffmpeg_params=['-cq','18','-pix_fmt','yuv420p','-movflags','+faststart'],logger=None)
    clip.close()
    if audio:audio.close()
    print('EXPORT_TERMINE',target,flush=True)
if __name__=='__main__':main()
