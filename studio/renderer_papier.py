"""Original cut-paper theatre: torn captions, travelling props and an origami bird."""
import math
from functools import lru_cache
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from renderer_carnet import CarnetFilm,typeface
import motion as m


@lru_cache(maxsize=80)
def heading_font(size):
    for path in ['C:/Windows/Fonts/impact.ttf','/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf']:
        if Path(path).is_file():return ImageFont.truetype(path,size)
    return m.font(size,True)


def paper(d,xy,fill,shadow=True):
    x,y,r,b=map(round,xy)
    # Repeatable cut edges belong to the material, not a noise filter on the video.
    points=[(x,y+5),(x+11,y),(r-13,y+3),(r,y),(r-4,y+17),(r,b-9),
            (r-11,b),(x+15,b-3),(x,b),(x+3,b-17)]
    if shadow:d.polygon([(a+6,c+8) for a,c in points],fill='#252C2A')
    d.polygon(points,fill=fill)


class PapierFilm(CarnetFilm):
    def __init__(self,out,config,data):
        super().__init__(out,config,data)
        self.ink='#252C2A';self.muted='#5C675E';self.surface='#F5EDDA'
        self.colors=['#387A75','#B54F3D','#D2AE46']
        import illustrations as art
        art.CREAM=self.ink;art.DIM=self.muted;art.DARK=self.surface
        art.GOLD,art.PINK,art.TEAL=self.colors
        self.backgrounds=[]
        for base,seam in [('#45665E','#3C5C55'),('#876346','#79563E'),('#4D5266','#42475A')]:
            bg=Image.new('RGBA',(self.W,self.H),base);d=ImageDraw.Draw(bg)
            for x in range(0,self.W,100):
                d.polygon([(x,0),(x+12,0),(x+8,self.H),(x,self.H)],fill=seam)
            y=1440 if self.vertical else 930
            paper(d,(0,y,self.W,self.H),'#B49A73',False)
            d.line((0,y+12,self.W,y+12),fill='#786449',width=10)
            self.backgrounds.append(bg)

    def panel(self,im,xy,color=None):
        d=ImageDraw.Draw(im);paper(d,xy,self.surface)
        if color:
            x,y,r,b=xy;paper(d,(x+18,y-13,min(r-18,x+115),y+14),color,False)

    def visual(self,k,u):
        scene=self.scenes[k];kind=scene['visual'];labels=scene['labels'][:3]
        im=Image.new('RGBA',(1000,760));d=ImageDraw.Draw(im)
        if kind=='target':
            for j,r in enumerate([210,145,75]):
                p=m.ease((u-j*.18)/.65);r=max(1,r*p)
                d.ellipse((500-r+6,320-r+8,500+r+6,320+r+8),fill=self.ink)
                d.ellipse((500-r,320-r,500+r,320+r),fill=self.colors[2-j])
            p=m.ease((u-.8)/.7)
            if p:
                d.line((800-300*p,70+250*p,850-300*p,20+250*p),fill=self.ink,width=12)
                d.polygon([(800-300*p,70+250*p),(830-300*p,64+250*p),(806-300*p,39+250*p)],fill=self.surface)
            self.title(d,labels[0],500,630,850,42)
            return im
        rows=kind in ['steps','question'];n=min(len(labels),2) if kind in ['compare','people'] else len(labels)
        for j,label in enumerate(labels[:n]):
            p=m.ease((u-.12-j*.23)/.55)
            if p<=0:continue
            card=Image.new('RGBA',(1000,760));dd=ImageDraw.Draw(card)
            if rows:
                x,y=500,145+j*215;self.panel(card,(80,y-65,920,y+90),self.colors[j])
                self.tx(dd,150,y+10,str(j+1),52,self.colors[j]);self.title(dd,label,555,y-8,620,38)
            else:
                x=500 if n==1 else 180+j*(640/(n-1));y=360
                half=195 if n==2 else 140
                self.panel(card,(x-half,155,x+half,600),self.colors[j])
                if kind=='chart':
                    h=(240-j*55)*m.ease((u-.5-j*.23)/1.1)
                    paper(dd,(x-38,460-h,x+38,460),self.colors[j],False)
                else:self.icon(card,x,345,j,1.5,label)
                self.title(dd,label,x,505,half*2-32,30)
            # Each physical card drops and rotates into its final reading position once.
            card=card.rotate((1-p)*(-7 if j%2 else 7),Image.Resampling.BICUBIC,center=(x,y))
            im.alpha_composite(card,(0,round(-95*(1-p))))
        if kind in ['flow','cycle','people'] and n>1:
            p=m.ease((u-.95)/1.8);start=180;end=820
            d.line((start,85,end,85),fill=self.surface,width=4)
            paper(d,(start+(end-start)*p-23,60,start+(end-start)*p+23,110),self.colors[2])
            if kind=='cycle' and u>2.8:
                p=m.ease((u-2.8)/1.2);d.line((820,660,820-640*p,660),fill=self.surface,width=5)
        if kind=='chart':self.tx(d,500,710,'COMPARAISON ILLUSTRATIVE · SANS MESURE',18,self.surface)
        return im

    def bird(self,im,k,u):
        """A folded-paper bird points, releases a note and returns to rest."""
        bird=Image.new('RGBA',(440,380));d=ImageDraw.Draw(bird)
        p=m.ease(u/.6);gesture=m.ease((u-.7)/.5)*(1-m.ease((u-2.1)/.6))
        d.polygon([(115,300),(265,300),(315,335),(90,335)],fill='#293C37')
        d.polygon([(90,300),(125,105),(300,140),(335,300)],fill='#60A497')
        d.polygon([(125,105),(220,190),(90,300)],fill='#427C73')
        d.polygon([(125,105),(300,140),(220,190)],fill='#85B7A5')
        d.polygon([(300,140),(355,175),(303,195)],fill='#E2BD50')
        # Wing hinge rather than human hands; intentional simple cut-paper anatomy.
        d.polygon([(190,195),(95-65*gesture,235-110*gesture),(165,285)],fill='#D3E0C2')
        d.ellipse((270,151,282,163),fill=self.ink)
        d.line((165,315,165,350,142,350),fill=self.ink,width=7)
        d.line((252,315,252,350,277,350),fill=self.ink,width=7)
        if gesture>.05:
            paper(d,(22,90,103,150),'#E2BD50');d.line((40,112,83,112),fill=self.ink,width=3)
        scale=.85 if self.vertical else .65
        bird=bird.resize((round(440*scale),round(380*scale)),Image.Resampling.LANCZOS)
        x=(670 if self.vertical else 1450)+round((1-p)*130)
        y=(1140 if self.vertical else 695)+round((1-p)*50)
        im.alpha_composite(bird,(x,y))

    def frame(self,t):
        t=float(t);k=max(0,min(len(self.scenes)-1,int(np.searchsorted(self.starts,t,side='right')-1)))
        u=max(0,t-self.starts[k]);im=self.backgrounds[k%3].copy();d=ImageDraw.Draw(im)
        scene=self.scenes[k];vertical=self.vertical
        # Banner slides in, then holds; text wraps before rendering, never reflows.
        size=65 if vertical else 59;width=880 if vertical else 570
        while size>26:
            lines=[];line='';font=heading_font(size)
            for word in scene['title'].upper().split():
                trial=(line+' '+word).strip()
                if line and d.textlength(trial,font=font)>width:lines.append(line);line=word
                else:line=trial
            if line:lines.append(line)
            if len(lines)<=3 and all(d.textlength(s,font=font)<=width and s not in ['?','!',':',';'] for s in lines):break
            size-=2
        y=155 if vertical else 180;left=70;dy=round(-70*(1-m.ease(u/.45)))
        for i,line in enumerate(lines):
            yy=y+i*size*1.3+dy;w=d.textlength(line,font=font)
            paper(d,(left,yy-12,left+w+40,yy+size*1.1),'#E2BD50')
            d.text((left+20,yy+size*.48),line,font=font,fill=self.ink,anchor='lm')
        stage=self.visual(k,u)
        # Keep full canvas: cut-paper props must not change scale as they appear.
        stage=stage.resize((960,730) if vertical else (1020,775),Image.Resampling.LANCZOS)
        im.alpha_composite(stage,(60,475) if vertical else (795,85))
        self.bird(im,k,u);d=ImageDraw.Draw(im)
        group=next((g for g in self.groups if g[0]['start']-.04<=t<=g[-1]['end']+.13),None)
        if group:
            size=54 if vertical else 43;limit=880 if vertical else 640
            text=' '.join(w['text'] for w in group)
            while d.textlength(text,font=typeface(size,True))>limit and size>24:size-=2
            gap=16;total=sum(d.textlength(w['text'],font=typeface(size,True))+22 for w in group)+gap*(len(group)-1)
            while total>limit and size>20:
                size-=2;total=sum(d.textlength(w['text'],font=typeface(size,True))+22 for w in group)+gap*(len(group)-1)
            cx,cy=(540,1590) if vertical else (410,750);x=cx-total/2
            for word in group:
                w=d.textlength(word['text'],font=typeface(size,True));active=word['start']-.02<=t<=word['end']+.05
                paper(d,(x,cy-size*.64,x+w+22,cy+size*.72),'#E2BD50' if active else self.surface)
                d.text((x+11,cy),word['text'],font=typeface(size,True),fill=self.ink,anchor='lm');x+=w+22+gap
        self.tx(d,70,80,'BOBINE / PAPIER DÉCOUPÉ',22,self.surface,'lm')
        self.tx(d,70,self.H-110,f'{k+1:02} / {len(self.scenes):02} · UNE IDÉE À LA FOIS',23,self.ink,'lm')
        if t>self.duration-.35:im=Image.blend(self.backgrounds[k%3],im,max(0,(self.duration-t)/.35))
        return np.asarray(im.convert('RGB'))
