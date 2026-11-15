"""Original light editorial motion design, local rendering and unchanged Qwen audio."""
from pathlib import Path
from functools import lru_cache
import argparse,json,math,re
import numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageFilter
from moviepy import VideoClip,AudioFileClip
HERE=Path(__file__).resolve().parent
SOURCE=HERE
W,H=1080,1920;INK='#17202B';MUTED='#748091';BLUE='#2364D2';PURPLE='#7753C6';GREEN='#167F72'
COLORS=[BLUE,PURPLE,GREEN];BG='#F5F7FB'
@lru_cache(maxsize=120)
def font(size,bold=True):return ImageFont.truetype('C:/Windows/Fonts/seguibl.ttf' if bold else 'C:/Windows/Fonts/segoeui.ttf',max(10,round(size)))
def text(d,x,y,s,size=50,color=INK,bold=True,anchor='mm'):d.text((round(x),round(y)),s,font=font(size,bold),fill=color,anchor=anchor)
def ease(p):p=max(0,min(1,p));return p*p*(3-2*p)
def spring(p):p=max(0,min(1,p));return 1-(1-p)**3*math.cos(p*math.pi*2)
def mix(a,b,p):return a+(b-a)*p
def entrance(base,layer,t,kind='object'):
    """Fast anticipation, slight overshoot, damped settling; hold after landing."""
    t=float(t)
    duration=.48 if kind=='object' else .34
    if t>=duration:base.alpha_composite(layer);return
    if t<=0:return
    p=t/duration
    knots=[(0,.58 if kind=='object' else .83),(.56,1.055),(.80,.988),(1,1)]
    for (a,sa),(b,sb) in zip(knots,knots[1:]):
        if a<=p<=b:scale=mix(sa,sb,ease((p-a)/(b-a)));break
    bbox=layer.getbbox()
    if bbox is None:return
    crop=layer.crop(bbox);cx=(bbox[0]+bbox[2])/2;cy=(bbox[1]+bbox[3])/2
    angle=(-4.5 if kind=='object' else -1.2)*(1-ease(min(1,p/.8)))
    crop=crop.resize((max(1,round(crop.width*scale)),max(1,round(crop.height*scale))),Image.Resampling.BICUBIC)
    if abs(angle)>.02:crop=crop.rotate(angle,resample=Image.Resampling.BICUBIC,expand=True)
    if kind=='object' and p<.3:crop=crop.filter(ImageFilter.GaussianBlur(5*(1-p/.3)))
    alpha=ease(p/.24);crop.putalpha(crop.getchannel('A').point(lambda x:round(x*alpha)))
    dy=(155 if kind=='object' else 38)*(1-ease(min(1,p/.67)))
    base.alpha_composite(crop,(round(cx-crop.width/2),round(cy-crop.height/2+dy)))
def rgb(s):return np.array([int(s[i:i+2],16) for i in (1,3,5)],dtype=float)
def box(d,xy,fill,r=30,outline=None,width=2):d.rounded_rectangle(tuple(round(v) for v in xy),radius=r,fill=fill,outline=outline,width=width)
@lru_cache(maxsize=20)
def panel(w,h):
    im=Image.new('RGBA',(w+120,h+150));shadow=Image.new('RGBA',im.size);d=ImageDraw.Draw(shadow)
    box(d,(60,76,w+60,h+76),(27,45,70,38),30)
    im.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(24)))
    d=ImageDraw.Draw(im);box(d,(60,40,w+60,h+40),'white',30,outline='#E4E9F0')
    return im
def card(im,cx,cy,w,h):im.alpha_composite(panel(w,h),(round(cx-w/2-60),round(cy-h/2-40)))
def extrude(d,x,y,s,size,color):
    shade=tuple((rgb(color)*.62).astype(int))
    for n in range(13,0,-1):text(d,x+n*.65,y+n,s,size,shade)
    text(d,x,y,s,size,color)
def label(im,cx,cy,s,color=BLUE,size=35):
    d=ImageDraw.Draw(im);width=round(d.textlength(s,font=font(size))+54)
    box(d,(cx-width/2,cy-31,cx+width/2,cy+31),color,16);text(d,cx,cy-1,s,size,'white')
def cursor(d,x,y,p=0):
    d.polygon([(x,y),(x+5,y+62),(x+20,y+46),(x+33,y+75),(x+47,y+68),(x+32,y+40),(x+56,y+37)],fill=INK,outline='white',width=3)
    if p>0:d.ellipse((x-25*p,y-25*p,x+25*p,y+25*p),outline=BLUE,width=3)
def arrow(d,a,b,color=BLUE,width=7):
    d.line((*a,*b),fill=color,width=width);angle=math.atan2(b[1]-a[1],b[0]-a[0])
    d.polygon([b,(b[0]-23*math.cos(angle-.55),b[1]-23*math.sin(angle-.55)),(b[0]-23*math.cos(angle+.55),b[1]-23*math.sin(angle+.55))],fill=color)
def exercise(im,cx,cy,s=1,reveal=1,solved=False,dense=False,button=0):
    w,h=round(840*s),round(560*s);card(im,cx,cy,w,h);d=ImageDraw.Draw(im)
    text(d,cx-350*s,cy-222*s,'EXERCICE 01',26*s,MUTED,anchor='lm')
    text(d,cx,cy-130*s,'2 + 3 = '+('5' if solved else '?'),76*s)
    if dense:
        for j,line in enumerate(['Lire les consignes','Comprendre les étapes','Choisir une méthode']):
            box(d,(cx-330*s,cy-52*s+j*55*s,cx+330*s,cy-10*s+j*55*s),'#EDF0F5',12)
            text(d,cx,cy-30*s+j*55*s,line,27*s,MUTED,False)
    else:
        for j,x in enumerate([-232,-146,60,146,232]):
            p=ease((reveal-j*.12)/.42)
            if p>0:
                y=cy+4*s-(1-p)*65*s;r=27*s*p
                d.ellipse((cx+x*s-r,y-r,cx+x*s+r,y+r),fill=BLUE if j<2 else PURPLE)
        if solved:text(d,cx,cy+80*s,'5 jetons. Une réponse comprise.',29*s,GREEN)
    for j,value in enumerate(['4','5','6']):
        xx=cx+(j-1)*198*s;fill=GREEN if solved and j==1 else (BLUE if button and j==1 else '#EDF1F6')
        box(d,(xx-75*s,cy+155*s,xx+75*s,cy+242*s),fill,16)
        text(d,xx,cy+198*s,value,46*s,'white' if (solved or button) and j==1 else INK)
def app(im,cx,cy,s=1,solved=False):
    w,h=round(820*s),round(650*s);card(im,cx,cy,w,h);d=ImageDraw.Draw(im)
    yy=cy-h/2+33*s
    for j,c in enumerate(['#F59091','#F2CA69','#7DC6B0']):d.ellipse((cx-w/2+(25+j*22)*s,yy-6*s,cx-w/2+(37+j*22)*s,yy+6*s),fill=c)
    d.line((cx-w/2+4,yy+27*s,cx+w/2-4,yy+27*s),fill='#EDF1F6',width=2)
    text(d,cx,cy-207*s,'APPRENDRE',40*s)
    text(d,cx,cy-151*s,'Une explication. Un exercice.',24*s,MUTED,False)
    exercise(im,cx,cy+68*s,.70*s,reveal=1,solved=solved)
def rings(im,cx,cy,s=1,p=(1,1,1),labels=True):
    d=ImageDraw.Draw(im)
    for r,color,amount in [(340,GREEN,p[2]),(237,PURPLE,p[1]),(133,BLUE,p[0])]:
        if amount<=0:continue
        rr=r*s;thickness=round((91 if r==340 else 97)*s)
        if r==133:
            rr*=ease(amount);d.ellipse((cx-rr,cy-rr,cx+rr,cy+rr),fill=color)
        else:d.arc((cx-rr,cy-rr,cx+rr,cy+rr),-90,-90+359.99*min(1,amount),fill=color,width=thickness)
    if labels:
        for yy,title,amount,sz in [(cy,'POURQUOI',p[0],31),(cy-188*s,'COMMENT',p[1],30),(cy-296*s,'QUOI',p[2],30)]:
            if amount>.85:text(d,cx,yy,title,sz*s,'white')
def message(im,x,y,kind,sub,color,w=820):
    s=w/820;card(im,x,y,w,round(155*s));d=ImageDraw.Draw(im)
    box(d,(x-w/2+28*s,y-43*s,x-w/2+39*s,y+43*s),color,5)
    text(d,x-w/2+67*s,y-29*s,kind,25*s,color,anchor='lm');text(d,x-w/2+67*s,y+27*s,sub,36*s,anchor='lm')
def make_bg():
    yy,xx=np.mgrid[:H,:W];a=np.exp(-((xx-100)**2+(yy-340)**2)/(2*500**2));b=np.exp(-((xx-1050)**2+(yy-1300)**2)/(2*650**2))
    arr=np.ones((H,W,3))*np.array([248,249,252]);arr-=a[...,None]*np.array([14,7,0]);arr-=b[...,None]*np.array([3,10,5]);return Image.fromarray(np.clip(arr,0,255).astype('uint8')).convert('RGBA')
def parse_srt(path):
    def seconds(s):
        a,b,c=s.replace(',','.').split(':');return int(a)*3600+int(b)*60+float(c)
    result=[]
    for block in re.split(r'\n\s*\n',path.read_text(encoding='utf-8-sig').strip()):
        lines=block.splitlines();a,b=lines[1].split(' --> ');result.append((seconds(a),seconds(b),' '.join(lines[2:])))
    return result
class Film:
    def __init__(self):
        self.cues=parse_srt(SOURCE/'Sous-titres.srt');self.starts=[a for a,b,c in self.cues]
        self.words=json.loads((HERE/'Mots-alignes.json').read_text(encoding='utf-8'))['words'];self.groups=[]
        for k in range(12):
            ws=[w for w in self.words if w['cue']==k]
            for j in range(0,len(ws),3):self.groups.append(ws[j:j+3])
        self.bg=make_bg()
        with AudioFileClip(str(SOURCE/'Narration.wav')) as a:self.duration=a.duration
    def frame(self,t):
        k=max(0,min(11,int(np.searchsorted(self.starts,t,side='right')-1)));local=max(0,t-self.starts[k]);im=self.bg.copy();d=ImageDraw.Draw(im)
        text(d,76,124,'D’ABORD LE SENS',27,BLUE,anchor='lm');text(d,1005,124,'GOLDEN CIRCLE',24,MUTED,False,'rm')
        base=im;im=Image.new('RGBA',(W,H));d=ImageDraw.Draw(im)
        chapter=0 if k in [2,3] else 1 if k in [4,5] else 2 if k in [6,7] else None
        if chapter is not None:
            extrude(d,190,368,str(chapter+1),200,COLORS[chapter]);text(d,325,355,['Pourquoi','Comment','Quoi'][chapter],73,anchor='lm')
            text(d,325,427,['Le sens','La méthode','Le résultat'][chapter],33,MUTED,False,'lm')
        else:
            title={0:'Votre projet convainc ?',1:'Changez l’ordre.',8:'Le même projet…',9:'…un message plus clair.',10:'Du sens au résultat.',11:'À vous de jouer.'}[k]
            text(d,540,315,title,62)
        title_time=t-self.starts[{3:2,5:4,7:6}.get(k,k)]
        entrance(base,im,title_time,'title')
        im=Image.new('RGBA',(W,H));d=ImageDraw.Draw(im)
        if k==0:
            p=spring(local/.7);app(im,540,870+110*(1-p),.90)
            if local>1.0:
                q=spring((local-1)/.38);yy=1110+140*(1-q);card(im,835,yy,185,210);extrude(d,835,yy-15,'?',115,BLUE)
            label(im,540,1310,'Un produit ne dit pas tout.',BLUE,32)
        elif k==1:
            for j,(name,color) in enumerate(zip(['Pourquoi','Comment','Quoi'],COLORS)):
                p=spring((local-.18*j)/.42);y=625+j*226+230*(1-p)
                if p>0:
                    card(im,540,y,825,170);extrude(d,230,y,str(j+1),108,color);text(d,330,y-4,name,54,anchor='lm')
                    if j<2 and p>.98:arrow(d,(540,y+105),(540,y+135),MUTED,4)
        elif k==2:
            rings(im,540,890,.92,p=(ease(local/1.0),0,0),labels=False)
            if local>.8:text(d,540,890,'Pourquoi ?',34,'white')
            text(d,540,1265,'La raison d’être du projet.',40)
        elif k==3:
            card(im,540,853,860,470);label(im,540,692,'NOTRE INTENTION',BLUE,29)
            text(d,540,817,'Apprendre',66);text(d,540,898,'plus facilement.',56)
            p=ease((local-.5)/1);d.line((245,974,245+590*p,974),fill=BLUE,width=10)
            text(d,540,1232,'Pour qui ? Pour quel changement ?',35,MUTED,False)
        elif k==4:
            exercise(im,540,920,.99,reveal=max(0,local-1.1),dense=local<1.25)
            if local>1.15:label(im,540,1318,'Une question. Deux groupes de jetons.',PURPLE,29)
        elif k==5:
            solved=local>2.05;exercise(im,540,920,.99,reveal=1,solved=solved,button=local>1.5)
            p=ease((local-.6)/1.35);withdraw=ease((local-2.4)/.5)
            if local<3.0:cursor(d,mix(980,600,p)+180*withdraw,mix(1285,1140,p)+120*withdraw,max(0,1-abs(local-2.05)/.3))
            label(im,540,1318,'Essayer → recevoir un retour',PURPLE,31)
        elif k==6:
            app(im,540,900,.99,solved=True);label(im,540,1325,'Une application de formation',GREEN,32)
        elif k==7:
            app(im,540,850,.79,solved=True)
            for j,(s,color) in enumerate(zip(['Intention','Méthode','Produit'],COLORS)):
                p=ease((local-.3-j*.35)/.6)
                if p>0:
                    x=235+j*305;label(im,x,1270+60*(1-p),s,color,28)
        elif k in [8,9]:
            p=ease((local-1.2)/2) if k==8 else 1
            for j,(kind,sub,color) in enumerate(zip(['POURQUOI','COMMENT','QUOI'],['Apprendre plus facilement','Des exercices simples','Une application'],COLORS)):
                start=[1100,870,640][j];end=[640,870,1100][j]
                xx=540+(math.sin(math.pi*p)*260*(1 if j==2 else -1) if j!=1 else 0)
                if k==8 and j==1 and .15<p<.85:continue
                message(im,xx,mix(start,end,p),kind,sub,color,w=820 if k==9 else round(820-340*math.sin(math.pi*p)))
            label(im,540,1325,'Le sens → la méthode → le produit',BLUE,30)
        elif k==10:
            p=[ease((local-j*1.1)/1.05) for j in range(3)];rings(im,540,910,1.02,p=p)
            if local>3.5:label(im,540,1330,'Pourquoi → Comment → Quoi',BLUE,31)
        elif k==11:
            card(im,540,865,900,540);label(im,540,670,'VOTRE PROCHAIN PROJET',BLUE,28)
            lines=['Nous voulons aider','[qui] à [changer quoi].'];progress=int(max(0,local-.25)*20);offset=0
            for j,line in enumerate(lines):
                n=max(0,min(len(line),progress-offset));text(d,180,840+j*96,line[:n],45,anchor='lm');offset+=len(line)
            text(d,540,1285,'Écrivez votre pourquoi en une phrase.',35)
        if k in [5,7,9]:base.alpha_composite(im)
        else:entrance(base,im,local-.09)
        im=Image.new('RGBA',(W,H));d=ImageDraw.Draw(im)
        # Short groups follow the existing spoken track; no speed or voice changes.
        group=next((g for g in self.groups if g[0]['start']-.04<=t<=g[-1]['end']+.13),None)
        if group:
            size=68;widths=[d.textlength(w['text'],font=font(size)) for w in group];total=sum(widths)+23*(len(widths)-1)
            if total>910:size=round(size*910/total);widths=[d.textlength(w['text'],font=font(size)) for w in group];total=sum(widths)+23*(len(widths)-1)
            x=(W-total)/2
            for word,width in zip(group,widths):
                active=word['start']-.02<=t<=word['end']+.05
                key=any(term in word['text'].lower() for term in ['pourquoi','comment','quoi','intention','apprendre','exercices','application','résultat'])
                if active and key:box(d,(x-13,1510,x+width+13,1607),COLORS[chapter] if chapter is not None else BLUE,17)
                text(d,x+width/2,1553,word['text'],size,'white' if active and key else INK);x+=width+23
            entrance(base,im,t-group[0]['start']+.03,'caption')
        im=base;d=ImageDraw.Draw(im)
        text(d,540,1790,'D’après le modèle de Simon Sinek',24,MUTED,False)
        if t>self.duration-.55:im=Image.blend(self.bg,im,max(0,(self.duration-t)/.55))
        return np.asarray(im.convert('RGB'))
def main():
    p=argparse.ArgumentParser();p.add_argument('--preview',action='store_true');p.add_argument('--stills',action='store_true');a=p.parse_args();film=Film()
    control=HERE/'Controle';control.mkdir(exist_ok=True)
    for t in [1.7,6.5,12,17,23.8,28.7,34,39,47,53,61,68]:Image.fromarray(film.frame(t)).save(control/f'Image-{t:04.1f}.jpg',quality=93)
    if a.stills:return
    start,end=(0,10.163) if a.preview else (0,film.duration)
    audio=AudioFileClip(str(SOURCE/'Narration.wav')).subclipped(start,end)
    clip=VideoClip(frame_function=lambda t:film.frame(t+start),duration=end-start).with_audio(audio)
    target=HERE/('Essai-Apparitions.mp4' if a.preview else 'Golden-Circle-Motion-Design-V2.mp4')
    clip.write_videofile(str(target),fps=30,codec='h264_nvenc',audio_codec='aac',audio_bitrate='192k',ffmpeg_params=['-cq','18','-pix_fmt','yuv420p','-movflags','+faststart'],logger=None)
    clip.close();audio.close();print('EXPORT_TERMINE',target,flush=True)
if __name__=='__main__':main()
