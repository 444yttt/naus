"""Clean vector redraw of the Harajuku 3LDK plan (traced from floorplan_large.jpg, 800x546 px source
coordinates; 35.2 px = 1 m). No furniture. Writes SVG + high-res PNG."""
import math
S=[]
def ln(pts,w=1.0,c='#1a1a1a',dash=None,cap='square'):
    d=' '.join(f'{x:.2f},{y:.2f}' for x,y in pts)
    S.append(f'<polyline points="{d}" fill="none" stroke="{c}" stroke-width="{w}" stroke-linecap="{cap}" stroke-linejoin="miter"'+(f' stroke-dasharray="{dash}"' if dash else '')+'/>')
def rect(x0,y0,x1,y1,w=0.5,fill='none',c='#1a1a1a',dash=None):
    S.append(f'<rect x="{x0}" y="{y0}" width="{x1-x0}" height="{y1-y0}" fill="{fill}" stroke="{c}" stroke-width="{w}"'+(f' stroke-dasharray="{dash}"' if dash else '')+'/>')
def poly(pts,fill,c='#1a1a1a',w=0.5):
    S.append('<polygon points="'+' '.join(f'{x},{y}' for x,y in pts)+f'" fill="{fill}" stroke="{c}" stroke-width="{w}"/>')
def wall(pts,w=3.2):ln(pts,w,'#1a1a1a')
def iwall(pts,w=1.8):ln(pts,w,'#1a1a1a')
def glaze(a,b,off=1.6):
    dx,dy=b[0]-a[0],b[1]-a[1];L=math.hypot(dx,dy);nx,ny=-dy/L*off,dx/L*off
    ln([(a[0]+nx,a[1]+ny),(b[0]+nx,b[1]+ny)],0.45);ln([(a[0]-nx,a[1]-ny),(b[0]-nx,b[1]-ny)],0.45);ln([a,b],0.3,'#6a8fa8')
def door(hx,hy,r,a0,a1,leaf=True):
    a0r,a1r=math.radians(a0),math.radians(a1)
    x0,y0=hx+r*math.cos(a0r),hy+r*math.sin(a0r);x1,y1=hx+r*math.cos(a1r),hy+r*math.sin(a1r)
    large=1 if abs(a1-a0)>180 else 0;sweep=1 if a1>a0 else 0
    S.append(f'<path d="M{x0:.2f},{y0:.2f} A{r},{r} 0 {large} {sweep} {x1:.2f},{y1:.2f}" fill="none" stroke="#444" stroke-width="0.35" stroke-dasharray="1.2,0.8"/>')
    if leaf:ln([(hx,hy),(x1,y1)],0.6,'#333')
def text(x,y,t,size=7,anchor='middle',c='#222',w=400,rot=0):
    tr=f' transform="rotate({rot} {x} {y})"' if rot else ''
    S.append(f'<text x="{x}" y="{y}" font-family="Noto Sans CJK JP, WenQuanYi Zen Hei, sans-serif" font-size="{size}" font-weight="{w}" fill="{c}" text-anchor="{anchor}"{tr}>{t}</text>')
BL='#dde9f3'
# ---------- exterior ----------
TL=(190,12);DL=(24,473)          # diagonal FIX glazing: bottom-left corner world(0,0)=px(24,473)
wall([(12,477),(181,10),(287,10)],1.2)                       # outer skin line of the façade
glaze(DL,(192,17),1.8)                                       # diagonal FIX glazing
wall([(192,17),(196,17)]);glaze((196,17),(244,17),1.4);wall([(244,15),(283,15)],2.6);iwall([(276,15),(276,70),(251,70),(251,97)],1.2);rect(252,71,275,96,0.3,'#ececec')
wall([(283,10),(283,190),(355,190)]);wall([(372,190),(470,190),(470,165),(546,165),(546,190),(752,190),(752,468)])
iwall([(283,15),(283,10)])
for i,(a,b) in enumerate([((24,465),(60,465)),((100,465),(323,465)),((370,465),(525,465)),((572,465),(728,465))]):glaze(a,b,1.4)
wall([(752,468),(770,468)],2.0)
# balcony
ln([(12,477),(0,546)],1.0);ln([(30,540),(770,540)],1.0);ln([(30,536),(770,536)],0.4)
for x0,x1 in [(60,100),(323,370),(525,572),(728,770)]:
    rect(x0,455,x1,470,1.4,'#e6e6e6');rect(x0+3,470,x1-3,505,0.5,'#f2f2f2');rect(x0,530,x1,540,1.2,'#e6e6e6')
    ln([(x0+6,515),(x1-6,528)],0.35);ln([(x0+6,528),(x1-6,515)],0.35);rect(x0+6,515,x1-6,528,0.4)
# ---------- kitchen ----------
rect(251,97,278,115,0.8);text(264.5,109,'PS',6)
ln([(251,115),(251,255)],1.6);ln([(276,97),(276,182)],0.5);rect(253,118,275,182,0.4,'#f4f4f4')
ln([(258,120),(270,180)],0.3,'#666','1,1');ln([(258,180),(270,120)],0.3,'#666','1,1')
rect(253,188,271,213,0.6,'#f7f7f7')
for cx,cy in [(259,195),(259,206),(266,200)]:S.append(f'<circle cx="{cx}" cy="{cy}" r="2" fill="none" stroke="#333" stroke-width="0.5"/>')
rect(253,222,278,253,0.6,'none','#333','1.5,1');text(265.5,241,'R',7)
rect(215,210,233,255,0.6);ln([(215,210),(233,255)],0.4)            # tall cupboard
poly([(159,230),(194,242),(216,182),(216,120),(201,114)],'#f1f1f1',w=0.9)   # island
rect(190,178,205,206,0.4)                                          # sink
# kitchen / toilet / entrance block
iwall([(251,255),(338,255)]);iwall([(283,190),(283,255)]);iwall([(338,190),(338,300)]);iwall([(338,255),(415,255)])
iwall([(415,195),(415,303)]);iwall([(322,303),(470,303)])
ln([(310,203),(330,203)],0.5);S.append('<ellipse cx="320" cy="218" rx="7" ry="10" fill="none" stroke="#333" stroke-width="0.5"/>')   # WC
rect(290,229,298,245,0.5);door(283,255,22,-90,-30)
door(338,300,30,-90,-160);door(355,190,17,0,-90);door(415,255,22,180,240)
# SIC / laundry / fire door
rect(418,198,470,240,0.6,BL);text(444,222,'SIC',6)
rect(420,245,470,276,0.6);rect(421,246,444,270,0.4,'none','#555','1.2,0.8');text(432,262,'W',6)
rect(470,245,478,270,0.6,BL);text(474,258,'Shelf',4,rot=90)
door(455,303,24,180,270);door(422,303,15,-90,0)
text(432,298,'防火扉',4.6)
# toilet2 / powder / bath / WIC / stores
iwall([(482,195),(482,243),(516,243)]);iwall([(516,195),(516,250)]);iwall([(590,195),(590,262)]);iwall([(675,195),(675,262)]);iwall([(678,192),(678,300),(745,300)])
S.append('<ellipse cx="499" cy="215" rx="7" ry="10" fill="none" stroke="#333" stroke-width="0.5"/>')
rect(520,198,548,212,0.5);rect(560,198,588,212,0.5);ln([(518,196),(590,196)],0.4,'#555','1,1')
rect(520,245,548,262,0.6,BL);text(534,257,'Lin.',5);rect(485,247,515,262,0.9);text(500,258,'Sto.',5)
door(516,262,20,-90,-30);door(590,262,24,180,240)
rect(595,198,673,262,0.4);S.append('<rect x="645" y="205" width="27" height="50" rx="10" fill="none" stroke="#333" stroke-width="0.6"/>')
rect(680,195,745,298,0.6,BL);ln([(688,196),(688,297)],0.4,'#666','1,1');ln([(737,196),(737,297)],0.4,'#666','1,1');text(712,248,'WIC',6);text(712,256,'3.6J',5)
rect(655,262,678,290,0.9);text(666,279,'Sto.',5)
door(483,262,15,90,150,True);door(515,262,15,90,30,True)
# corridor walls & bedrooms
iwall([(470,303),(752,303)]);iwall([(355,303),(355,465)]);iwall([(490,303),(490,465)]);iwall([(612,290),(612,465)])
ln([(350,320),(350,460)],0.35,'#777','2,1');text(345,395,'Picture Rail',4.2,rot=-90,c='#555')
for x0 in [400,418]:rect(x0,308,x0+18,325,0.5,BL);text(x0+9,320,'Clo.',4.6)
for x0 in [535,552,570,588]:rect(x0,308,x0+17,325,0.5,BL);text(x0+8.5,320,'Clo.',4.4)
rect(535,300,605,307,0.4,'#f2f2f2');text(555,305.5,'Shelf',3.6);text(588,305.5,'Shelf',3.6)
door(487,303,30,90,180);door(493,303,30,90,0);door(615,290,25,0,90);door(725,300,22,90,180)
# ---------- labels ----------
for x,y,t,s in [(130,290,'Living Dining',9),(130,305,'30.3J',10),(224,192,'Kitchen',7),(224,203,'12.6J',7.5),(316,240,'Toilet',6.5),(377,226,'Entrance',7),(377,284,'Hall',7),(499,234,'Toilet',6.5),(553,227,'Powder',6),(553,236,'Room',6),(633,222,'Bath',6.5),(633,231,'1822',6),(445,264,'Laundry',5),(512,288,'Hall',7),
                (384,393,'Bedroom2',7),(384,406,'8.7J',8),(522,393,'Bedroom3',7),(522,406,'7.5J',8),(680,388,'Bedroom1',7),(680,401,'11.5J',8),(170,498,'Balcony',7),(445,498,'Balcony',7),(650,498,'Balcony',7),(508,180,'MB',6)]:text(x,y,t,s)
for x,y,r in [(36,400,-70),(74,295,-70),(112,190,-70),(150,85,-70),(218,9,0),(220,470,0),(43,479,0),(185,479,0),(265,479,0),(468,479,0),(680,479,0)]:text(x,y,'FIX',4.4,rot=r,c='#555')
# north arrow (north points left, as on the source sheet)
S.append('<circle cx="740" cy="155" r="13" fill="none" stroke="#222" stroke-width="0.6"/>');poly([(727,155),(752,150),(752,160)],'#111');text(731,147,'N',6)
# scale bar 0-5 m
for i in range(6):
    x=500+35.2*i
    if i<5:rect(x,140,x+35.2,144,0.4,'#222' if i%2==0 else '#fff')
    text(x,152,f'{i}',4.5)
text(500+35.2*5+6,152,'m',4.5,anchor='start')
svg=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="-8 -6 790 556" width="790" height="556"><rect x="-8" y="-6" width="790" height="556" fill="white"/>'+''.join(S)+'</svg>'
open('/work/plan/plan_clean.svg','w').write(svg);print('svg ok',len(S))
