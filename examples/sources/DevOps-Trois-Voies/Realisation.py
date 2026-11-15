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
        tx(d,540,123,'DEVOPS · LES TROIS VOIES',27,DIM)
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
        chapter=0 if k in [2,3,4] else 1 if k in [5,6] else 2 if k in [7,8,9] else None
        labels=['1 · LE FLUX','2 · LES RETOURS','3 · APPRENDRE']
        if chapter is not None:tx(d,540,525,labels[chapter],40,[GOLD,PINK,TEAL][chapter])
        elif k==0:tx(d,540,525,'ÇA CODE… MAIS ÇA BLOQUE.',42)
        elif k==1:tx(d,540,525,'AMÉLIORER TOUT LE SYSTÈME.',37)
        elif k==10:tx(d,540,525,'TROIS VOIES. UN MÊME SYSTÈME.',38)
        else:tx(d,540,525,'À VOUS DE JOUER.',45,GOLD)
        layer=Image.new('RGBA',(W,H));dd=ImageDraw.Draw(layer)
        if k==0:
            pipeline(layer,blocked=True)
            for j in range(4):
                p=m.spring((u-j*.24)/.45)
                if p>0:package(dd,267,1040-j*66+90*(1-p),.8)
            tx(dd,540,1260,'LE GOULOT RALENTIT TOUT LE MONDE.',31,PINK)
        elif k==1:
            for j,(name,c) in enumerate(zip(['FLUX','RETOURS','APPRENDRE'],[GOLD,PINK,TEAL])):
                p=m.spring((u-j*.2)/.5);x=205+j*335;yy=935+160*(1-p)
                if p>0:
                    block(dd,(x-145,yy-170,x+145,yy+180),outline=c)
                    if j==0:arrow(dd,(x-77,yy),(x+77,yy),c,14)
                    elif j==1:arrow(dd,(x+77,yy),(x-77,yy),c,14)
                    else:flask(dd,x,yy,.8,min(1,u))
                    tx(dd,x,yy+135,name,29,c)
            tx(dd,540,1270,'UNE MODIFICATION, DE BOUT EN BOUT.',30,DIM)
        elif k==2:
            pipeline(layer,p=m.ease((u-.4)/4.2))
            arrow(dd,(140,1195),(940,1195),GOLD,10);tx(dd,540,1290,'DE L’IDÉE À L’UTILISATEUR.',37,GOLD)
        elif k==3:
            pipeline(layer,blocked=True)
            for j in range(5):
                p=m.ease((u-.3-j*.14)/.35)
                if p>0:package(dd,267,1100-j*60,.63*p)
            tx(dd,540,1245,'PETITS LOTS · MOINS D’ATTENTE' if u<2.4 else 'LE GOULOT FREINE LA CHAÎNE.',35,GOLD)
            tx(dd,405,1100,'ATTENTE',23,PINK)
            if u>2.4:tx(dd,540,1360,'ACCÉLÉRER UNE ÉTAPE NE SUFFIT PAS.',29,DIM)
        elif k==4:
            p=m.ease((u-.25)/3.6);pipeline(layer,p=p)
            for j,x in enumerate(XS[1:]):
                if p>(j+1)/3-.03:check(dd,x,1160,.8)
            tx(dd,540,1300,'UNE PETITE MODIFICATION LIVRÉE.',34,TEAL)
        elif k==5:
            pipeline(layer,delivered=True);feedback(layer,m.ease((u-.4)/3.8))
            tx(dd,540,1265,'LE SIGNAL REVIENT VERS L’ÉQUIPE.',32,PINK)
        elif k==6:
            fixed=u>3.6;pipeline(layer,blocked=u<1.4,alert=1.4<=u<3.6,delivered=fixed)
            if u<1.4:tx(dd,405,705,'!',85,PINK)
            elif u<3.6:tx(dd,675,705,'!',85,PINK)
            if u>1.4:feedback(layer,m.ease((u-1.5)/1.8))
            if fixed:check(dd,136,1160,1.5,p=(u-3.6)/.3)
            tx(dd,540,1300,'DÉTECTER TÔT → CORRIGER VITE',35,TEAL if fixed else PINK)
        elif k==7:
            block(dd,(190,690,890,1190),outline=TEAL);flask(dd,540,925,1.6,u/1.6)
            tx(dd,540,1310,'ESSAYER · OBSERVER · APPRENDRE',35,TEAL)
        elif k==8:
            server(dd,540,758,1.2,alert=True)
            for j,(txt,c) in enumerate([('ATTENTE',GOLD),('SIGNAL TARDIF',PINK),('GARDE-FOU',TEAL)]):
                p=m.ease((u-.6-j*.55)/.45)
                if p>0:
                    x=205+j*335;yy=1040+75*(1-p);arrow(dd,(540,850),(x,yy-76),c,5)
                    block(dd,(x-142,yy-70,x+142,yy+70),outline=c);tx(dd,x,yy,txt,26,c)
            tx(dd,540,1305,'COMPRENDRE LES CONDITIONS.',34,TEAL)
            tx(dd,540,1370,'Une analyse partagée, sans chercher un coupable.',26,DIM)
        elif k==9:
            for j,(name,c,value) in enumerate([('AVANT',PINK,220),('ESSAI',TEAL,95)]):
                x=330+j*420;block(dd,(x-165,700,x+165,1160),outline=c);tx(dd,x,752,name,30,c)
                q=m.ease((u-.4-j*.65)/1.3);top=1085-value*q;block(dd,(x-51,top,x+51,1085),c,c,7)
                tx(dd,x,1122,'ERREURS',21,DIM)
            tx(dd,540,1205,'EXEMPLE ILLUSTRATIF',20,DIM)
            tx(dd,540,1250,'PETIT PÉRIMÈTRE · RÉSULTAT MESURÉ',30,TEAL)
            if u>2.8:
                q=m.ease((u-2.8)/.8);arrow(dd,(470,1370),(470+260*q,1370),TEAL,7);tx(dd,300,1370,'PARTAGER',27,TEAL)
        elif k==10:
            pipeline(layer,p=m.ease(u/2.4))
            if u>2.2:feedback(layer,m.ease((u-2.2)/2.3))
            if u>4.5:flask(dd,540,1225,.58,m.ease((u-4.5)/.8))
            tx(dd,540,1400,'LIVRER → ÉCOUTER → AMÉLIORER',34,TEAL)
        else:
            block(dd,(120,690,960,1260),outline=GOLD)
            for j,(s,c) in enumerate([('Où attend le travail ?',GOLD),('Qui reçoit le signal ?',PINK),('Que peut-on apprendre ?',TEAL)]):
                p=m.ease((u-j*1.05)/.4)
                if p>0:
                    yy=805+j*160;dd.ellipse((185,yy-14,213,yy+14),fill=c);tx(dd,248,yy+30*(1-p),s,39,c,'lm')
            tx(dd,540,1370,'CHOISISSEZ UNE PREMIÈRE AMÉLIORATION.',29,GOLD)
        m.entrance(im,layer,u-.04) if k not in [4,6,10] else im.alpha_composite(layer)
        d=ImageDraw.Draw(im)
        for j,(name,c) in enumerate(zip(['FLUX','RETOURS','APPRENDRE'],[GOLD,PINK,TEAL])):
            x=205+j*335;active=(chapter==j or k>=10);block(d,(x-145,1560,x+145,1640),outline=c if active else '#403831',r=17)
            tx(d,x,1600,name,26,c if active else DIM)
        tx(d,540,1775,'LES TROIS VOIES · GENE KIM / IT REVOLUTION',21,DIM)
        if t>self.duration-.5:im=Image.blend(self.bg,im,max(0,(self.duration-t)/.5))
        return np.asarray(im.convert('RGB'))
def main():
    p=argparse.ArgumentParser();p.add_argument('--preview',action='store_true');a=p.parse_args();f=Film();control=HERE/'Controle';control.mkdir(exist_ok=True)
    for i,s in enumerate(f.timing):
        t=s['start']+min(3,(s['end']-s['start'])/2);Image.fromarray(f.frame(t)).save(control/f'Plan-{i+1:02}.jpg',quality=92)
    start=f.starts[3] if a.preview else 0;end=min(f.duration,start+10) if a.preview else f.duration
    clip=VideoClip(frame_function=lambda t:f.frame(t+start),duration=end-start);audio=None
    if (HERE/'Narration.wav').exists():audio=AudioFileClip(str(HERE/'Narration.wav')).subclipped(start,end);clip=clip.with_audio(audio)
    target=HERE/('Essai-Visuel.mp4' if a.preview else 'DevOps-Les-Trois-Voies.mp4')
    clip.write_videofile(str(target),fps=30,codec='h264_nvenc',audio_codec='aac' if audio else None,audio_bitrate='192k',ffmpeg_params=['-cq','18','-pix_fmt','yuv420p','-movflags','+faststart'],logger=None)
    clip.close()
    if audio:audio.close()
    print('EXPORT_TERMINE',target,flush=True)
if __name__=='__main__':main()
