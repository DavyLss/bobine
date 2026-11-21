"""Original paper-and-ink direction: editorial headings, diagrams and a lens guide."""
from pathlib import Path
from functools import lru_cache
import math
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from renderer import Film
import illustrations as art
import motion as m

@lru_cache(maxsize=100)
def typeface(size,serif=False):
    paths=(['C:/Windows/Fonts/georgiab.ttf','/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf'] if serif else ['C:/Windows/Fonts/consola.ttf','/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf'])
    for path in paths:
        if Path(path).is_file():return ImageFont.truetype(path,max(12,round(size)))
    return m.font(size,True)

class CarnetFilm(Film):
    def __init__(self,out,config,data):
        super().__init__(out,config,data)
        self.ink='#262923';self.muted='#646B61';self.colors=['#24675F','#BB5437','#B38632']
        self.surface='#FCF9F2';self.border=self.ink;self._diagram_bounds={}
        art.CREAM=self.ink;art.DIM=self.muted;art.GOLD,art.PINK,art.TEAL=self.colors;art.DARK=self.surface
        self.bg=Image.new('RGBA',(self.W,self.H),'#F0EBE0');d=ImageDraw.Draw(self.bg)
        grid_top=510 if self.vertical else 120
        for y in range(grid_top,self.H-120,42):
            for x in range(45,self.W-30,42):d.ellipse((x,y,x+3,y+3),fill='#BDB6A9')
        baseline=self.H-175
        d.line((45,baseline,self.W-45,baseline),fill=self.ink,width=3)
        d.line((45,baseline+10,self.W-45,baseline+10),fill=self.ink,width=1)

    def tx(self,d,x,y,s,size=42,c=None,anchor='mm'):
        d.text((round(x),round(y)),str(s),font=typeface(size),fill=c or self.ink,anchor=anchor)

    def block(self,d,xy,fill=None,outline=None,r=10,width=3):
        m.box(d,xy,fill or self.surface,min(r,10),outline or self.ink,width)

    def panel(self,im,xy,color=None):
        d=ImageDraw.Draw(im);x1,y1,x2,y2=xy
        m.box(d,(x1+9,y1+11,x2+9,y2+11),self.ink,10)
        self.block(d,xy,self.surface,self.ink,10,3)
        if color:d.line((x1+16,y1+14,x1+58,y1+14),fill=color,width=5)

    def wrapped(self,d,text,width,size,serif=False):
        lines=[];line=''
        for word in str(text).split():
            test=(line+' '+word).strip()
            if line and d.textlength(test,font=typeface(size,serif))>width:lines.append(line);line=word
            else:line=test
        if line:lines.append(line)
        return lines

    def title(self,d,text,x,y,width,size=42):
        while size>17:
            lines=self.wrapped(d,text,width,size)
            if len(lines)<=3 and all(d.textlength(line,font=typeface(size))<=width for line in lines):break
            size-=2
        for j,line in enumerate(lines):self.tx(d,x,y+j*size*1.18,line,size)

    def headline(self,im,text,x,y,width,size,u):
        d=ImageDraw.Draw(im)
        while size>30:
            lines=self.wrapped(d,text,width,size,True)
            if len(lines)<=3 and all(d.textlength(line,font=typeface(size,True))<=width for line in lines):break
            size-=2
        # Reveal words in fixed lines so that the heading does not reflow mid-animation.
        count=max(0,math.ceil((u-.08)*7));used=0
        for j,line in enumerate(lines):
            words=line.split();visible=words[:max(0,count-used)];used+=len(words)
            d.text((x,y+j*size*1.18),' '.join(visible),font=typeface(size,True),fill=self.ink,anchor='la')

    def visual(self,k,u):
        if self.scenes[k]['visual']!='compare':return super().visual(k,u)
        layer=Image.new('RGBA',(1000,760));d=ImageDraw.Draw(layer)
        # Comparing two ideas does not mean both deserve a success tick.
        for j,label in enumerate(self.scenes[k]['labels'][:2]):
            x=265+j*470;self.panel(layer,(x-195,150,x+195,615),self.colors[j])
            self.title(d,label,x,215,335,31);self.icon(layer,x,365,j,1.7,label)
            self.tx(d,x,545,'A' if j==0 else 'B',36,self.colors[j])
        return layer

    def diagram(self,k,u,size):
        stage=self.visual(k,u)
        # Fixed full-state bounds prevent the camera from jumping as objects enter.
        if k not in self._diagram_bounds:self._diagram_bounds[k]=self.visual(k,10).getbbox()
        bounds=self._diagram_bounds[k]
        if bounds:stage=stage.crop(bounds)
        scale=min(size[0]/stage.width,size[1]/stage.height)
        return stage.resize((round(stage.width*scale),round(stage.height*scale)),Image.Resampling.LANCZOS)

    def guide(self,im,k,u):
        """A small optical instrument follows the diagram; no borrowed mascot."""
        d=ImageDraw.Draw(im);settle=m.ease(min(1,u/1.1));landing=math.sin(min(1,u/.8)*math.pi)*16
        target=.23 if k%2==0 else .72
        x=self.W*(.47+(target-.47)*settle)
        r=55 if self.vertical else 42;y=self.H-175-r-34-landing
        d.line((x-r*.6,y+r,x-r*1.1,y+r+34),fill=self.ink,width=5)
        d.line((x+r*.6,y+r,x+r*1.1,y+r+34),fill=self.ink,width=5)
        d.ellipse((x-r,y-r,x+r,y+r),fill=self.surface,outline=self.ink,width=4)
        d.ellipse((x-r*.65,y-r*.65,x+r*.65,y+r*.65),outline=self.colors[0],width=4)
        angle=-.6+(k%3)*.5
        d.line((x,y,x+math.cos(angle)*r*.55,y+math.sin(angle)*r*.55),fill=self.colors[1],width=4)
        d.ellipse((x-4,y-4,x+4,y+4),fill=self.ink)
        # A short pointer grows toward the explanatory diagram, then stays still.
        p=m.ease((u-.7)/.7)
        if p>0:
            end=(x+70*p,y-70*p);d.line((x+r*.8,y-r*.8,*end),fill=self.ink,width=3)

    def frame(self,t):
        t=float(t);k=max(0,min(len(self.scenes)-1,int(np.searchsorted(self.starts,t,side='right')-1)))
        u=max(0,t-self.starts[k]);scene=self.scenes[k];im=self.bg.copy();d=ImageDraw.Draw(im)
        if self.vertical:
            self.tx(d,80,82,'BOBINE / CARNET ANIMÉ',23,self.colors[0],'lm')
            self.headline(im,scene['title'],80,160,920,78,u)
            stage=self.diagram(k,u,(950,820));pos=((self.W-stage.width)//2,490)
            cx,cy,limit,size=540,1485,900,49
        else:
            self.tx(d,80,68,'BOBINE / CARNET ANIMÉ',22,self.colors[0],'lm')
            self.headline(im,scene['title'],80,160,615,67,u)
            stage=self.diagram(k,u,(1040,720));pos=(800,150)
            cx,cy,limit,size=380,680,610,40
        layer=Image.new('RGBA',im.size);layer.alpha_composite(stage,pos)
        # Distinct lateral page entrance; graphics keep animating inside the settled page.
        p=m.ease(u/.48);dx=round((1-p)*(95 if k%2==0 else -95))
        if u<.48:
            layer.putalpha(layer.getchannel('A').point(lambda a:round(a*p)))
        im.alpha_composite(layer,(dx,0))
        d=ImageDraw.Draw(im)
        group=next((g for g in self.groups if g[0]['start']-.04<=t<=g[-1]['end']+.13),None)
        if group:
            text=' '.join(word['text'] for word in group)
            while d.textlength(text,font=typeface(size))>limit and size>24:size-=2
            width=d.textlength(text,font=typeface(size));x=cx-width/2
            for word in group:
                label=word['text'];w=d.textlength(label,font=typeface(size))
                if word['start']-.02<=t<=word['end']+.05:
                    d.line((x-2,cy+size*.56,x+w+2,cy+size*.56),fill=self.colors[1],width=5)
                self.tx(d,x+w/2,cy,label,size);x+=w+d.textlength(' ',font=typeface(size))
        self.guide(im,k,u);d=ImageDraw.Draw(im)
        self.tx(d,70,self.H-90,f'NOTE {k+1:02} / {len(self.scenes):02}',23,self.muted,'lm')
        self.tx(d,self.W-70,self.H-90,'COMPRENDRE · ESSAYER',21,self.muted,'rm')
        if t>self.duration-.4:im=Image.blend(self.bg,im,max(0,(self.duration-t)/.4))
        return np.asarray(im.convert('RGB'))
