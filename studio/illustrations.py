"""Les trois voies du DevOps : théâtre d'objets original, rendu entièrement local."""
from pathlib import Path
import argparse,json,math
import numpy as np
from PIL import Image,ImageDraw
from moviepy import VideoClip,AudioFileClip
import motion as m
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
