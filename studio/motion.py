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
def font(size,bold=True):
    import os
    candidates=[os.getenv('STUDIO_FONT_BOLD' if bold else 'STUDIO_FONT',''),
        'C:/Windows/Fonts/seguibl.ttf' if bold else 'C:/Windows/Fonts/segoeui.ttf',
        '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf' if bold else '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf']
    for path in candidates:
        if path and Path(path).is_file():return ImageFont.truetype(path,max(10,round(size)))
    raise RuntimeError('Police absente : définir STUDIO_FONT et STUDIO_FONT_BOLD avec des fichiers TTF locaux.')
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
