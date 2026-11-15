"""Original dark object theatre. Local Pillow/MoviePy rendering; preserved Qwen voice."""
from pathlib import Path
import argparse,json,math
import numpy as np
from PIL import Image,ImageDraw,ImageFilter
from moviepy import VideoClip,AudioFileClip
import Moteur as m
HERE=Path(__file__).resolve().parent
W,H=m.W,m.H
CREAM='#F4E8CC';GOLD='#E4B75B';PINK='#CB4F78';TEAL='#69AAA4';DIM='#A49A8C'
m.INK=CREAM;m.MUTED=DIM;m.BLUE=GOLD;m.PURPLE=PINK;m.GREEN=TEAL;m.COLORS=[GOLD,PINK,TEAL]

def tx(d,x,y,s,size=46,color=CREAM,anchor='mm'):m.text(d,x,y,s,size,color,True,anchor)
def block(d,xy,fill='#29221E',outline='#564438',r=28,width=3):m.box(d,xy,fill,r,outline,width)
def bg():
    yy,xx=np.mgrid[:H,:W];g=np.exp(-((xx-540)**2/(2*460**2)+(yy-860)**2/(2*600**2)))
    a=np.array([16,17,21])+g[...,None]*np.array([27,19,12]);return Image.fromarray(a.astype('uint8')).convert('RGBA')
def target(im,x,y,s=1,p=1):
    d=ImageDraw.Draw(im)
    for r,c in [(164,'#6D4F2D'),(116,GOLD),(66,'#29221E'),(24,CREAM)]:
        rr=r*s;d.ellipse((x-rr,y-rr,x+rr,y+rr),fill=c)
    q=m.ease(p);xx=x+210*s*(1-q);yy=y-160*s*(1-q)
    d.line((xx+4*s,yy-4*s,xx+130*s,yy-130*s),fill=CREAM,width=max(2,round(12*s)))
    d.polygon([(xx,yy),(xx+39*s,yy-10*s),(xx+10*s,yy-39*s)],fill=PINK)
def book(im,x,y,s=1,p=1):
    d=ImageDraw.Draw(im);opening=m.ease(p);w=160*s*max(.08,opening);h=115*s
    d.polygon([(x,y-h+18*s),(x-w,y-h),(x-w,y+h),(x,y+h+18*s),(x+w,y+h),(x+w,y-h)],fill=CREAM)
    d.line((x,y-h+18*s,x,y+h+18*s),fill='#B9A987',width=max(2,round(7*s)))
    for j in range(4):
        yy=y-60*s+j*37*s
        d.line((x-w*.8,yy-8*s,x-w*.18,yy),fill='#B7A98A',width=max(2,round(5*s)))
        d.line((x+w*.18,yy,x+w*.8,yy-8*s),fill='#B7A98A',width=max(2,round(5*s)))
def phone(im,x,y,s=1,p=1):
    d=ImageDraw.Draw(im);w,h=126*s,218*s
    block(d,(x-w,y-h,x+w,y+h),CREAM,'#877E6E',round(29*s),max(2,round(5*s)))
    block(d,(x-w+16*s,y-h+24*s,x+w-16*s,y+h-26*s),'#203437','#203437',round(14*s))
    d.line((x-35*s,y-h+12*s,x+35*s,y-h+12*s),fill='#877E6E',width=max(2,round(5*s)))
    book(im,x,y-65*s,.43*s,1)
    for j in range(3):
        yy=y+38*s+j*36*s;block(d,(x-81*s,yy,x+81*s,yy+19*s),'#45615D','#45615D',5)
        if p>j*.3:block(d,(x-81*s,yy,x-81*s+162*s*m.ease((p-j*.3)/.4),yy+19*s),TEAL,TEAL,5)
def plinth(im,x,y,label,icon,color,s=1,p=1):
    d=ImageDraw.Draw(im);block(d,(x-145*s,y-170*s,x+145*s,y+190*s),outline=color,r=round(30*s))
    icon(im,x,y-18*s,.58*s,p);tx(d,x,y+142*s,label,round(28*s),color)
def clarity(im,t):
    d=ImageDraw.Draw(im);block(d,(340,1534,740,1666),r=23)
    tx(d,540,1562,'DU SENS AU RÉSULTAT',21,DIM)
    for j in range(12):
        x=385+j*26;h=14+j*2.4;on=j<int(min(12,t/65.6*12))
        block(d,(x,1629-h,x+17,1629),[GOLD,PINK,TEAL][j//4] if on else '#403831',outline=None,r=3)
class Film(m.Film):
    def __init__(self):super().__init__();self.bg=bg()
    def frame(self,t):
        t=float(t);k=max(0,min(11,int(np.searchsorted(self.starts,t,side='right')-1)));u=max(0,t-self.starts[k]);im=self.bg.copy();d=ImageDraw.Draw(im)
        tx(d,540,123,'LE SENS AVANT LE PRODUIT',25,DIM)
        # A compact spoken heading gives the whole central stage to the objects.
        group=next((g for g in self.groups if g[0]['start']-.04<=t<=g[-1]['end']+.13),None)
        if group:
            layer=Image.new('RGBA',(W,H));dd=ImageDraw.Draw(layer);words=[w['text'].upper() for w in group];size=58
            widths=[dd.textlength(w,font=m.font(size)) for w in words];total=sum(widths)+19*(len(words)-1)
            if total>900:size=round(size*900/total);widths=[dd.textlength(w,font=m.font(size)) for w in words];total=sum(widths)+19*(len(words)-1)
            x=(W-total)/2;block(dd,(x-28,286,x+total+28,397),r=20)
            for w,s,ww in zip(group,words,widths):
                active=w['start']-.02<=t<=w['end']+.05
                if active:block(dd,(x-8,299,x+ww+8,384),PINK,PINK,8)
                tx(dd,x+ww/2,341,s,size);x+=ww+19
            m.entrance(im,layer,t-group[0]['start']+.03,'caption')
        layer=Image.new('RGBA',(W,H));dd=ImageDraw.Draw(layer)
        if k==0:
            phone(layer,540,920,1.25,min(1,u/1.3))
            if u>.8:
                p=m.spring((u-.8)/.4);block(dd,(730,669+90*(1-p),898,824+90*(1-p)),outline=PINK);tx(dd,814,746+90*(1-p),'?',104,PINK)
            tx(dd,540,1285,'Un produit… mais pour quoi faire ?',36)
        elif k==1:
            for j,(s,icon,c) in enumerate(zip(['POURQUOI','COMMENT','QUOI'],[target,book,phone],[GOLD,PINK,TEAL])):
                p=m.spring((u-j*.24)/.48)
                if p>0:plinth(layer,205+j*335,920+180*(1-p),s,icon,c,.94,min(1,u))
            tx(dd,540,1270,'1. LE SENS    2. LA MÉTHODE    3. LE PRODUIT',26,DIM)
        elif k==2:
            target(layer,540,900,1.4,u/.8);tx(dd,540,1260,'POURQUOI',50,GOLD)
        elif k==3:
            book(layer,540,880,1.6,u/.8)
            target(layer,820,1040,.52,(u-.5)/.6)
            tx(dd,540,1230,'APPRENDRE PLUS FACILEMENT',39,GOLD)
            tx(dd,540,1302,'L’intention précède l’application.',30,DIM)
        elif k in [4,5]:
            block(dd,(139,649,941,1196),outline=PINK)
            tx(dd,540,737,'2 + 3 = '+('5' if k==5 and u>1.8 else '?'),84)
            offset=u if k==4 else 4+u
            for j,xx in enumerate([290,390,590,690,790]):
                p=m.spring((offset-.4-j*.15)/.5)
                if p>0:
                    yy=900+105*(1-p);r=35;dd.ellipse((xx-r,yy-r,xx+r,yy+r),fill=GOLD if j<2 else PINK)
            if k==5 and u>1.8:
                q=m.ease((u-1.8)/.3);dd.line((468,1062,520,1110,520+112*q,1110-110*q),fill=TEAL,width=16)
            else:tx(dd,540,1091,'COMPTER • ESSAYER • COMPRENDRE',29,DIM)
            tx(dd,540,1290,'DES EXERCICES SIMPLES',43,PINK)
        elif k in [6,7]:
            phone(layer,540,905,1.55,min(1,u/1.5) if k==6 else 1)
            tx(dd,540,1297,'UNE APPLICATION DE FORMATION',35,TEAL)
            if k==7:
                for j,(icon,c) in enumerate([(target,GOLD),(book,PINK)]):
                    p=m.spring((u-j*.35)/.5)
                    if p>0:icon(layer,230+j*620,840+100*(1-p),.53,1)
        elif k in [8,9]:
            p=m.ease((u-.7)/1.6) if k==8 else 1
            for j,(s,icon,c) in enumerate(zip(['POURQUOI','COMMENT','QUOI'],[target,book,phone],[GOLD,PINK,TEAL])):
                start=[875,540,205][j];end=[205,540,875][j]
                if j==1 and .12<p<.88:continue
                x=m.mix(start,end,p);yy=920+(-260 if j==0 else 260 if j==2 else 0)*math.sin(math.pi*p)
                plinth(layer,x,yy,s,icon,c,.90,1)
            tx(dd,540,1430,'COMMENCER PAR CE QUI COMPTE.',38,GOLD)
        elif k==10:
            for j,(r,c,s) in enumerate([(320,TEAL,'QUOI'),(220,PINK,'COMMENT'),(120,GOLD,'POURQUOI')]):
                p=m.ease((u-(2-j)*.7)/.65)
                if p>0:
                    rr=r*p;dd.ellipse((540-rr,930-rr,540+rr,930+rr),fill=c)
            if u>1.5:
                tx(dd,540,930,'POURQUOI',29,'#1A1714');tx(dd,540,760,'COMMENT',26);tx(dd,540,658,'QUOI',27)
            tx(dd,540,1340,'LE SENS → LA MÉTHODE → LE RÉSULTAT',30)
        else:
            block(dd,(120,650,960,1170),outline=GOLD)
            book(layer,540,796,.72,1)
            lines=['Nous voulons aider','[qui] à [changer quoi].'];n=int(max(0,u-.2)*22)
            for j,line in enumerate(lines):
                tx(dd,540,965+j*70,line[:max(0,n)],43);n-=len(line)
            tx(dd,540,1300,'ÉCRIVEZ VOTRE POURQUOI.',44,GOLD)
        if k in [5,7,9]:im.alpha_composite(layer)
        else:m.entrance(im,layer,u-.04)
        clarity(im,t);d=ImageDraw.Draw(im)
        tx(d,540,1775,'GOLDEN CIRCLE · D’APRÈS SIMON SINEK',21,DIM)
        if t>self.duration-.5:im=Image.blend(self.bg,im,max(0,(self.duration-t)/.5))
        return np.asarray(im.convert('RGB'))
def main():
    p=argparse.ArgumentParser();p.add_argument('--preview',action='store_true');a=p.parse_args();f=Film();control=HERE/'Controle';control.mkdir(exist_ok=True)
    for t in [1.7,6.5,12,17,23.8,28.7,34,39,47,53,61,68]:Image.fromarray(f.frame(t)).save(control/f'Image-{t:04.1f}.jpg',quality=92)
    end=10.163 if a.preview else f.duration
    audio=AudioFileClip(str(HERE/'Narration.wav')).subclipped(0,end)
    clip=VideoClip(frame_function=f.frame,duration=end).with_audio(audio)
    dest=HERE/('Essai-Atelier-Sombre.mp4' if a.preview else 'Golden-Circle-Atelier-Sombre-Voix-Fixe.mp4')
    clip.write_videofile(str(dest),fps=30,codec='h264_nvenc',audio_codec='aac',audio_bitrate='192k',ffmpeg_params=['-cq','18','-pix_fmt','yuv420p','-movflags','+faststart'],logger=None)
    clip.close();audio.close();print('EXPORT_TERMINE',dest,flush=True)
if __name__=='__main__':main()
