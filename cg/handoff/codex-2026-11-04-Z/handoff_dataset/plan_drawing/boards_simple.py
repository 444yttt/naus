import json,math,subprocess,re
from PIL import Image,ImageDraw,ImageFont
FP=json.load(open('/work/plan/footprints.json'))
base=open('/work/plan/plan_clean.svg').read()
def P(x,y):return 24+35.2*x,473-35.2*y
STY={'Shindo ラグ（Poliform）':('#e9dfcf','#b9a98e',0),'Linha Dining（Minotti）':('#8f8a83','#3a3a3a',2),'Torii チェア（Minotti）':('#d6d9dc','#555',3),
 'Ernest ソファ（Poliform）':('#f3eee5','#6b6458',3),'Ernest テーブル（Poliform）':('#2f2925','#111',4),'Eames Lounge Chair（Herman Miller）':('#7a4e33','#3a2617',3),
 'IVRESSE（Roche Bobois）':('#f4f2ee','#444',4),'TV 97型クラス':('#151515','#000',4),'Beolab 28（Bang & Olufsen）':('#333','#000',4),'植物':('#7fa66a','#3d5f2e',5),'ランプ（Panthella型）':('#ffffff','#444',6)}
def furniture_svg():
    out=[]
    for k,(f,c,z) in sorted(STY.items(),key=lambda kv:kv[1][2]):
        for poly in FP.get(k,[]):
            pts=' '.join('%.2f,%.2f'%P(x,y) for x,y in poly)
            out.append(f'<polygon points="{pts}" fill="{f}" stroke="{c}" stroke-width="0.6" fill-opacity="{0.85 if k.startswith("Shindo") else 1}"/>')
    return ''.join(out)
CAMS={}
for s in ['u1','u2','p09','p01','p13']:CAMS[s]=json.load(open(f'/work/hj/handoff_dataset/out_Z5/{s}_camera.json'))
for s in ['n03','n04']:CAMS[s]=json.load(open(f'/work/hj/handoff_dataset/out_Z3/{s}_camera_Z3.json'))
ORDER=[('01','u1','リビング・テレビ壁'),('02','u2','リビングからダイニング'),('03','p09','窓際からリビング'),('04','p01','ダイニング'),('05','p13','キッチン'),('09','n03','ダイニングからリビング'),('10','n04','TV側コーナーからリビング')]
def cam_svg(s,num,big=True):
    c=CAMS[s];x,y=c['C'][:2];fw=c['R'][2];yaw=math.atan2(fw[1],fw[0]);hf=math.atan(c['W']/2/c['f'])
    L=2.6 if big else 1.0;cx,cy=P(x,y)
    a,b=P(x+L*math.cos(yaw+hf),y+L*math.sin(yaw+hf)),P(x+L*math.cos(yaw-hf),y+L*math.sin(yaw-hf))
    g=f'<polygon points="{cx:.2f},{cy:.2f} {a[0]:.2f},{a[1]:.2f} {b[0]:.2f},{b[1]:.2f}" fill="#e3342f" fill-opacity="{0.28 if big else 0.18}" stroke="#e3342f" stroke-width="0.5"/>'
    t=P(x+0.55*math.cos(yaw),y+0.55*math.sin(yaw))
    g+=f'<polygon points="{cx:.2f},{cy:.2f} {P(x+0.5*math.cos(yaw+0.35),y+0.5*math.sin(yaw+0.35))[0]:.2f},{P(x+0.5*math.cos(yaw+0.35),y+0.5*math.sin(yaw+0.35))[1]:.2f} {t[0]:.2f},{t[1]:.2f} {P(x+0.5*math.cos(yaw-0.35),y+0.5*math.sin(yaw-0.35))[0]:.2f},{P(x+0.5*math.cos(yaw-0.35),y+0.5*math.sin(yaw-0.35))[1]:.2f}" fill="#e3342f"/>'
    g+=f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="5.2" fill="#e3342f" stroke="white" stroke-width="0.8"/><text x="{cx:.2f}" y="{cy+2.1:.2f}" font-family="Noto Sans CJK JP, WenQuanYi Zen Hei, sans-serif" font-size="5.6" font-weight="700" fill="white" text-anchor="middle">{num}</text>'
    return g
def render(svg,out,w):
    open('/tmp/_p.svg','w').write(svg);subprocess.run(['rsvg-convert','-w',str(w),'/tmp/_p.svg','-o',out],check=True)
FUR=furniture_svg()
def plan_with(cams):
    return base.replace('</svg>',''.join(cams)+'</svg>')
font=lambda s:ImageFont.truetype('/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc',s)
import os;os.makedirs('/work/plan/out',exist_ok=True)
# master plan
render(plan_with([cam_svg(s,n,False) for n,s,_ in ORDER]),'/work/plan/out/_master.png',4000)
pm=Image.open('/work/plan/out/_master.png').convert('RGB');W=pm.size[0]+1300
board=Image.new('RGB',(W,pm.size[1]+260),'white');d=ImageDraw.Draw(board)
d.text((80,60),'参考例・原宿3LDK ／ 試作CG　カメラ位置',font=font(72),fill='#222')
d.text((80,160),'図面は販売図（ラスタ）からのトレース。寸法は概算で、発注用の実測図ではありません。',font=font(36),fill='#666')
board.paste(pm,(0,260))
x0=pm.size[0]+40;y=320
d.text((x0,y),'視点（カメラ）',font=font(46),fill='#222');y+=80
for n,s,t in ORDER:
    d.ellipse((x0,y,x0+50,y+50),fill='#e3342f');d.text((x0+25,y+25),n,font=font(28),fill='white',anchor='mm');d.text((x0+70,y+5),t,font=font(36),fill='#333');y+=70
board.save('/work/plan/out/00_plan_cameras.png');print('master',board.size)
# per-view boards
R='/work/hj/handoff_dataset/out_Z6/'
for n,s,t in ORDER:
    render(plan_with([cam_svg(s,n,True)]),'/work/plan/out/_p.png',2400)
    pl=Image.open('/work/plan/out/_p.png').convert('RGB');im=Image.open(R+f'{s}_full_composite.png').convert('RGB')
    im=im.resize((2400,round(im.size[1]*2400/im.size[0])),Image.LANCZOS)
    b=Image.new('RGB',(2400,im.size[1]+pl.size[1]+150),'white');dd=ImageDraw.Draw(b)
    b.paste(im,(0,0));dd.text((60,im.size[1]+40),f'{n}　{t}',font=font(60),fill='#222');b.paste(pl,(0,im.size[1]+150))
    b.save(f'/work/plan/out/{n}_{s}_view_plan.jpg',quality=94);print(n,b.size)
