"""Parameterized original motion design, two charters and native aspect layouts."""
import json,math
from functools import lru_cache
import numpy as np
from PIL import Image,ImageDraw,ImageFilter
from moviepy import VideoClip,AudioFileClip
from narration import DUO_ID,HOSTS,LABELS
import illustrations as art
import motion as m

class Film:
    def __init__(self,out,config,data):
        self.out=out;self.config=config;self.scenes=data['scenes'];self.timing=json.loads((out/'Chronologie.json').read_text(encoding='utf-8'));self.starts=[q['start'] for q in self.timing]
        self.words=json.loads((out/'Mots-alignes.json').read_text(encoding='utf-8'))['words'];self.groups=[]
        for k in range(len(self.scenes)):
            ws=[w for w in self.words if w['cue']==k]
            for j in range(0,len(ws),3):self.groups.append(ws[j:j+3])
        self.dark=config['theme']=='dark';self.vertical=config['format']=='reel';self.W,self.H=(1080,1920) if self.vertical else (1920,1080)
        self.ink='#F4E8CC' if self.dark else '#17202B';self.muted='#A49A8C' if self.dark else '#6E7C90';self.colors=['#E4B75B','#CB4F78','#69AAA4'] if self.dark else ['#2364D2','#7753C6','#167F72']
        self.surface='#29221E' if self.dark else '#FFFFFF';self.border='#564438' if self.dark else '#DCE3EE'
        art.CREAM=self.ink;art.DIM=self.muted;art.GOLD,art.PINK,art.TEAL=self.colors;art.DARK=self.surface
        art.tx=self.tx;art.block=self.block
        yy,xx=np.mgrid[:self.H,:self.W];glow=np.exp(-((xx-self.W*.55)**2/(2*(self.W*.6)**2)+(yy-self.H*.5)**2/(2*(self.H*.4)**2)))
        base=np.array([16,17,21]) if self.dark else np.array([249,250,253]);tint=np.array([27,19,12]) if self.dark else np.array([-9,-7,-1])
        self.bg=Image.fromarray(np.clip(base+glow[...,None]*tint,0,255).astype('uint8')).convert('RGBA')
    def tx(self,d,x,y,s,size=42,c=None,anchor='mm'):m.text(d,x,y,s,size,c or self.ink,True,anchor)
    def block(self,d,xy,fill=None,outline=None,r=24,width=3):m.box(d,xy,fill or self.surface,r,outline or self.border,width)
    def lines(self,d,text,width,size):
        words=text.split();lines=[];line=''
        for word in words:
            trial=(line+' '+word).strip()
            if line and d.textlength(trial,font=m.font(size))>width:lines.append(line);line=word
            else:line=trial
        if line:lines.append(line)
        return lines
    def title(self,d,text,x,y,width,size=42):
        while any(d.textlength(w,font=m.font(size))>width for w in text.split()) and size>20:size-=2
        lines=self.lines(d,text,width,size)
        if len(lines)>3:return self.title(d,text,x,y,width,size-3)
        for j,line in enumerate(lines):self.tx(d,x,y+j*size*1.25,line,size)
    def panel(self,im,xy,color=None):
        if not self.dark:
            shadow=Image.new('RGBA',im.size);m.box(ImageDraw.Draw(shadow),(xy[0]+3,xy[1]+12,xy[2]+3,xy[3]+12),(30,50,80,30),24);im.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(13)))
        self.block(ImageDraw.Draw(im),xy,outline=color or self.border)
    def icon(self,im,x,y,index,size=1,label=''):
        d=ImageDraw.Draw(im);c=self.colors[index%3];s=label.lower()
        if any(w in s for w in ['erreur','défaut','bug','panne','problème']):
            d.polygon([(x,y-64*size),(x-68*size,y+55*size),(x+68*size,y+55*size)],fill=self.colors[1]);self.tx(d,x,y+12*size,'!',round(64*size),'#FFF8EE');return
        if any(w in s for w in ['test','vérif','valid']):
            self.block(d,(x-47*size,y-65*size,x+47*size,y+65*size),outline=c,r=10);art.check(d,x,y,1.2*size,c);return
        if any(w in s for w in ['bouton','application','interface','site']):
            self.block(d,(x-70*size,y-60*size,x+70*size,y+60*size),outline=c,r=12);d.line((x-60*size,y-25*size,x+60*size,y-25*size),fill=self.border,width=3);self.block(d,(x-40*size,y,x+40*size,y+30*size),c,c,6);return
        if any(w in s for w in ['corrig','répar']):
            d.line((x-42*size,y+50*size,x+42*size,y-40*size),fill=c,width=round(18*size));d.arc((x+12*size,y-75*size,x+75*size,y-12*size),0,270,fill=c,width=round(13*size));return
        if any(w in s for w in ['serveur','prod','exploitation']):art.server(d,x,y,size);return
        if any(w in s for w in ['code','dévelop']):art.laptop(d,x,y,size);return
        if any(w in s for w in ['équipe','client','utilis','personne']):art.person(d,x,y,size);return
        if any(w in s for w in ['livr','produit','chang']):art.package(d,x,y,1.25*size,c);return
        if index%4==0:art.package(d,x,y,1.25*size,c)
        elif index%4==1:
            # Open book: a concept that can be transferred and understood.
            d.polygon([(x,y-48*size),(x-65*size,y-63*size),(x-65*size,y+53*size),(x,y+65*size),(x+65*size,y+53*size),(x+65*size,y-63*size)],fill=c)
            d.line((x,y-48*size,x,y+65*size),fill=self.ink,width=3)
        elif index%4==2:art.person(d,x,y,size,ok=False)
        else:art.check(d,x,y,size,c)
    def visual(self,k,u):
        scene=self.scenes[k];kind=scene['visual'];labels=scene['labels'];layer=Image.new('RGBA',(1000,760));d=ImageDraw.Draw(layer);c=self.colors
        if kind in ['flow','cycle']:
            for j,label in enumerate(labels):
                x=170+j*(660/max(1,len(labels)-1));self.panel(layer,(x-140,230,x+140,535),c[j%3]);self.icon(layer,x,350,j,1.2,label);self.title(d,label,x,470,240,28)
                if j<len(labels)-1:art.arrow(d,(x+145,375),(x+660/(len(labels)-1)-145,375),self.muted,5)
            p=m.ease((u-.35)/min(3.8,max(1,self.timing[k]['end']-self.starts[k]-1)));art.package(d,170+660*p,165,.85,c[0])
            if kind=='cycle' and u>2:
                path=[(830,570),(830,645),(170,645),(170,570)];d.line(path,fill=c[1],width=6,joint='curve');q=m.ease((u-2)/2.5);d.ellipse((825-660*q,635,845-660*q,655),fill=c[1]);art.arrow(d,(170,620),(170,570),c[1],6)
        elif kind=='compare':
            for j,label in enumerate(labels[:2]):
                x=265+j*470;self.panel(layer,(x-195,150,x+195,615),c[j]);self.title(d,label,x,215,335,31);self.icon(layer,x,365,j,1.7,label)
                if u>1+j*.7:art.check(d,x,540,1.2,c[j],(u-1-j*.7)/.5)
        elif kind in ['steps','question']:
            for j,label in enumerate(labels):
                p=m.spring((u-j*.3)/.48)
                if p<=0:continue
                y=150+j*205+80*(1-p);self.panel(layer,(100,y-70,900,y+85),c[j%3]);self.tx(d,170,y+5,str(j+1),53,c[j%3]);self.title(d,label,550,y-12,610,36)
                if j<len(labels)-1:art.arrow(d,(500,y+100),(500,y+125),self.muted,5)
        elif kind=='target':
            for r,color in [(200,c[2]),(140,c[1]),(75,c[0])]:d.ellipse((500-r,330-r,500+r,330+r),fill=color)
            q=m.ease((u-.4)/1.1);art.arrow(d,(780,80),(500+180*(1-q),330-180*(1-q)),self.ink,12)
            self.title(d,labels[0],500,620,850,42)
        elif kind=='people':
            p=m.ease((u-.4)/1.3)
            for j,label in enumerate(labels[:2]):
                x=(220+60*p) if j==0 else (780-60*p);self.panel(layer,(x-150,165,x+150,555),c[j]);art.person(d,x,340,1.8);self.title(d,label,x,490,260,29)
            if p>.3:
                art.arrow(d,(440,320),(440+120*p,320),c[0],8);art.arrow(d,(560,385),(560-120*p,385),c[2],8)
            if len(labels)>2:self.title(d,labels[2],500,650,900,37)
        else: # An illustrative comparison, never fabricated numerical statistics.
            for j,label in enumerate(labels[:3]):
                x=220+j*280;p=m.ease((u-.4-j*.3)/1.1);height=(250-j*65)*p
                self.panel(layer,(x-105,170,x+105,555),c[j]);self.block(d,(x-40,510-height,x+40,510),c[j],c[j],8);self.title(d,label,x,610,250,30)
            self.tx(d,500,715,'ILLUSTRATION · SANS DONNÉES CHIFFRÉES',18,self.muted)
        return layer
    def frame(self,t):
        t=float(t);k=max(0,min(len(self.scenes)-1,int(np.searchsorted(self.starts,t,side='right')-1)));u=max(0,t-self.starts[k]);im=self.bg.copy();d=ImageDraw.Draw(im);scene=self.scenes[k]
        if self.vertical:
            self.title(d,self.config['title'].upper(),540,125,920,27);self.title(d,scene['title'],540,480,900,43)
            stage=self.visual(k,u).resize((1000,760),Image.Resampling.LANCZOS);position=(40,590)
        else:
            self.tx(d,85,82,'STUDIO / VIDÉO',24,self.muted,'lm');self.title(d,self.config['title'],350,240,550,44);self.title(d,scene['title'],350,420,560,32)
            stage=self.visual(k,u).resize((1050,798),Image.Resampling.LANCZOS);position=(780,120)
        if self.config.get('voice')==DUO_ID:
            for j,speaker in enumerate(HOSTS):
                active=scene.get('speaker')==speaker
                x=(220+j*345) if self.vertical else (85+j*265)
                y=225 if self.vertical else 320;width=295 if self.vertical else 240;height=55
                color=self.colors[j]
                self.block(d,(x,y,x+width,y+height),color if active else self.surface,color if active else self.border,r=14)
                self.tx(d,x+width/2,y+height/2,LABELS[speaker],27 if self.vertical else 24,('#17202B' if self.dark else '#FFFFFF') if active else self.muted)
        layer=Image.new('RGBA',im.size);layer.alpha_composite(stage,position);m.entrance(im,layer,u-.02)
        group=next((g for g in self.groups if g[0]['start']-.04<=t<=g[-1]['end']+.13),None)
        if group:
            caption=Image.new('RGBA',im.size);dd=ImageDraw.Draw(caption);size=57 if self.vertical else 48;limit=910 if self.vertical else 565;cx=540 if self.vertical else 350;cy=(340 if self.dark else 1510) if self.vertical else 690
            rows=[];row=[]
            for word in group:
                label=word['text'].upper() if self.dark else word['text'];width=dd.textlength(label,font=m.font(size))
                if width>limit:size=max(28,round(size*limit/width))
                trial=' '.join(v[1] for v in row+[(word,label)])
                if row and dd.textlength(trial,font=m.font(size))>limit:rows.append(row);row=[]
                row.append((word,label))
            if row:rows.append(row)
            for j,row in enumerate(rows):
                line=' '.join(v[1] for v in row);width=dd.textlength(line,font=m.font(size));y=cy+j*size*1.3
                if self.dark:self.block(dd,(cx-width/2-20,y-size*.65,cx+width/2+20,y+size*.65))
                x=cx-width/2;space=dd.textlength(' ',font=m.font(size))
                for word,label in row:
                    word_width=dd.textlength(label,font=m.font(size));active=word['start']-.02<=t<=word['end']+.05
                    if active:m.box(dd,(x-7,y-size*.61,x+word_width+7,y+size*.61),self.colors[1 if self.dark else 0],9)
                    self.tx(dd,x+word_width/2,y,label,size,'#FFF8EE' if active else self.ink);x+=word_width+space
            m.entrance(im,caption,t-group[0]['start']+.03,'caption')
        d=ImageDraw.Draw(im)
        if self.vertical:self.tx(d,540,1730,f'{k+1:02} / {len(self.scenes):02}  ·  '+('ATELIER SOMBRE' if self.dark else 'ÉDITORIAL CLAIR'),23,self.muted)
        else:self.tx(d,85,1000,f'{k+1:02} / {len(self.scenes):02} · '+('ATELIER SOMBRE' if self.dark else 'ÉDITORIAL CLAIR'),22,self.muted,'lm')
        y=self.H-70;d.line((70,y,self.W-70,y),fill=self.border,width=5);d.line((70,y,70+(self.W-140)*t/self.duration,y),fill=self.colors[k%3],width=5)
        if t>self.duration-.45:im=Image.blend(self.bg,im,max(0,(self.duration-t)/.45))
        return np.asarray(im.convert('RGB'))
def render(out,config,data,progress):
    film=Film(out,config,data);audio=AudioFileClip(str(out/'Narration.wav'));film.duration=audio.duration;last=[-1]
    def frame(t):
        pct=min(100,int(t/film.duration*100))
        if pct>=last[0]+2:last[0]=pct;progress(pct)
        return film.frame(t)
    clip=VideoClip(frame_function=frame,duration=audio.duration).with_audio(audio)
    from encoding import encoder
    codec,params=encoder()
    try:clip.write_videofile(str(out/'Video.mp4'),fps=30,codec=codec,audio_codec='aac',audio_bitrate='192k',ffmpeg_params=params,logger=None)
    finally:clip.close();audio.close()
