"""Independent diagnostic overlays from final cameras and source photo lines."""
from pathlib import Path
import json,math,cv2,numpy as np
from PIL import Image,ImageDraw,ImageFont
from photo_common_V import floor_mask
R=Path(__file__).resolve().parent;O=R/'out/photo_final_V';V=O/'verification';V.mkdir(exist_ok=True)
C=json.loads((R/'out/layout_V.json').read_text(encoding='utf8'))
contacts=json.loads((O/'contact_candidates.json').read_text())['xy_m']
font=ImageFont.truetype('C:/Windows/Fonts/meiryo.ttc',24);small=ImageFont.truetype('C:/Windows/Fonts/meiryo.ttc',19)
reports=[]
def rect(cx,cy,w,h,angle):
    a=math.radians(angle);co,si=math.cos(a),math.sin(a)
    return [[cx+co*u-si*v,cy+si*u+co*v] for u,v in [(-w/2,-h/2),(w/2,-h/2),(w/2,h/2),(-w/2,h/2)]]
footprints=[]
for item in C['items']:
    if item['id']=='sofa':
        for m in item['modules']:
            x,y,xx,yy=m['rect'];footprints.append([[x,y],[xx,y],[xx,yy],[x,yy]])
    else:footprints.append(rect(*item['center'],*item['size'],item['angle']))
di=next(i for i in C['items'] if i['id']=='dining')
for item in C['chairs']['items']:footprints.append(rect(*item['center'],*item['size'],di['angle']))
for item in C['living_tables']['items']:footprints.append(item['outline_xy'])
for item in C['lounge']['chairs']:footprints.append(rect(*item['center'],*item['size'],item['angle']))
round_table=C['lounge']['table']
for centre,diameter in [(round_table['center'],round_table['diameter']),([9.05,.8],.253),([9.05,3.9],.253)]:
    footprints.append([[centre[0]+diameter/2*math.cos(a),centre[1]+diameter/2*math.sin(a)] for a in np.linspace(0,2*math.pi,48,endpoint=False)])
for shot in ['u1','u2','p09','p01','p13']:
    c=json.loads((O/f'{shot}_camera.json').read_text());W,H=c['W'],c['H'];sf=1600/W;hh=round(H*sf)
    rot=np.array(c['R']);centre=np.array(c['C'])
    def camera(p):return (np.asarray(p)-centre)@rot.T
    def project(p):
        q=camera(p);return q[:,:2]/q[:,2:]*c['f']+[W/2,H/2]
    source=cv2.imread(str(R/f'images/photos_srgb/{shot}.png'));src=cv2.resize(source,(1600,hh),interpolation=cv2.INTER_AREA)
    gray=cv2.cvtColor(src,cv2.COLOR_BGR2GRAY);fm=floor_mask(shot,1600,hh)>.95
    display=Image.open(O/f'{shot}_full_composite.png').convert('RGB').resize((1600,hh),Image.Resampling.LANCZOS);d=ImageDraw.Draw(display,'RGBA')
    def line_pixels(a,b,col,width=2):
        a=np.clip(a,-1e7,1e7).astype(int);b=np.clip(b,-1e7,1e7).astype(int)
        ok,aa,bb=cv2.clipLine((0,0,1600,hh),tuple(map(int,a)),tuple(map(int,b)))
        if ok:d.line([aa,bb],fill=col,width=width)
    def line_world(a,b,col,width=2):
        q=camera([a,b])
        if max(q[:,2])<=.03:return
        for i in [0,1]:
            if q[i,2]<.03:
                j=1-i;t=(.03-q[i,2])/(q[j,2]-q[i,2]);q[i]+=t*(q[j]-q[i])
        uv=(q[:,:2]/q[:,2:]*c['f']+[W/2,H/2])*sf
        line_pixels(uv[0],uv[1],col,width)
    # Use actual U fit controls, not stale copied T pane labels.
    controls=c.get('fit_controls') or c.get('observations') or c.get('architecture_controls')
    if 'pixels_ref1368' in controls:uv=np.array(controls['pixels_ref1368'])*W/1368
    elif 'pixels_1368' in controls:uv=np.array(controls['pixels_1368'])*W/1368
    else:uv=np.array(controls['pixels'])
    world=np.array(controls['world'])
    if shot=='p13':
        ip=np.array([[(x-24)/35.2,(473-y)/35.2,.91] for x,y in [(159,230),(194,242),(216,182),(216,120),(201,114)]])
        feet=ip[:3].copy();feet[:,2]=0
        world=np.concatenate([world,ip,feet]);uv=np.concatenate([uv,np.array([[350,1075],[630,1140],[960,1040],[949,991],[862,994],[349,1419],[628,1636],[959,1270]])*W/1368])
    pred=project(world);errors=np.linalg.norm(pred-uv,axis=1)
    for a,b in zip(uv*sf,pred*sf):
        line_pixels(a,b,(255,40,40,255),3)
        d.ellipse((a[0]-4,a[1]-4,a[0]+4,a[1]+4),fill=(0,240,255,255))
        d.ellipse((b[0]-7,b[1]-7,b[0]+7,b[1]+7),outline=(255,50,50,255),width=2)
    for i,a in enumerate(world):
        for b in world[i+1:]:
            if np.linalg.norm(a[:2]-b[:2])<1e-5 and abs(a[2]-b[2])>.5:line_world(a,b,(245,70,230,190),2)
    # Independent orientation test against long, source-photo floor seams/grain.
    vp=rot[:,0];vp=(vp[:2]/vp[2]*c['f']+[W/2,H/2])*sf
    candidates=[];ls=cv2.createLineSegmentDetector().detect(gray)[0]
    if ls is not None:
        for row in ls.reshape(-1,4):
            a,b=row[:2],row[2:];m=(a+b)/2;length=float(np.linalg.norm(b-a))
            if length<65:continue
            ix=np.rint([a,m,b]).astype(int)
            if np.any(ix[:,0]<0) or np.any(ix[:,0]>=1600) or np.any(ix[:,1]<0) or np.any(ix[:,1]>=hh) or not np.all(fm[ix[:,1],ix[:,0]]):continue
            unit=(b-a)/length;t=vp-m;t/=np.linalg.norm(t);sine=abs(unit[0]*t[1]-unit[1]*t[0]);angle=math.degrees(math.asin(min(1,sine)))
            if angle>5:continue
            candidates.append((length,.5*length*sine/sf,angle,a,b,t))
    for length,err,angle,a,b,t in sorted(candidates,key=lambda r:-r[0])[:30]:
        line_pixels(a,b,(0,220,255,220),2);m=(a+b)/2;line_pixels(m-t*length,m+t*length,(20,255,90,150),1)
    for poly in footprints:
        pp=[[x,y,0] for x,y in poly]
        for a,b in zip(pp,pp[1:]+pp[:1]):line_world(a,b,(255,170,20,190),2)
    q=camera([[x,y,0] for x,y in contacts]);valid=q[:,2]>.03
    q=q[valid];points=(q[:,:2]/q[:,2:]*c['f']+[W/2,H/2])*sf
    for x,y in points:
        if 0<=x<1600 and 0<=y<hh:d.ellipse((x-1.5,y-1.5,x+1.5,y+1.5),fill=(255,240,40,220))
    if shot=='p13':
        bp=project([[5.2,9.9,.91]])[0]*sf;x,y=bp
        d.ellipse((x-9,y-9,x+9,y+9),outline=(255,240,40,255),width=2)
        d.text((x+14,y+5),'Balance 台座基準',font=small,fill='#fff030',stroke_width=2,stroke_fill='black')
    floor_rms=float(np.sqrt(np.mean([r[1]**2 for r in candidates]))) if candidates else None
    med=float(np.median([r[2] for r in candidates])) if candidates else None
    rep={'shot':shot,'native_size':[W,H],'architecture_fit_control_count':len(errors),'architecture_fit_rms_native_px':float(np.sqrt(np.mean(errors**2))),'architecture_fit_max_native_px':float(errors.max()),'architecture_fit_rms_at_1368_width_px':float(np.sqrt(np.mean(errors**2))*1368/W),'floor_line_candidate_count':len(candidates),'floor_orientation_endpoint_rms_native_px':floor_rms,'floor_orientation_median_degrees':med,'floor_line_selection':'source-photo floor region, length >=65px at1600wide, within5degrees of predicted X vanishing direction; grain may be included. Orientation diagnostic, not absolute/surveyed position accuracy.','calibration_status':'fit residuals are in-sample observations, not independent held-out accuracy; room plan approximate','distortion':'k1=k2=0; no lens measurement, no additional photographic warp','controls_world':world.tolist(),'controls_observed_native_px':uv.tolist(),'controls_projected_native_px':pred.tolist(),'residuals_native_px':errors.tolist()}
    reports.append(rep)
    rep['camera_estimate']={key:c[key] for key in ['C','R','f','k1','k2']}
    d.rectangle((0,0,1600,166),fill=(15,20,25,225))
    d.text((22,12),f'{shot} ｜ 試作CG・投影検証（原寸 {W}×{H}）',font=font,fill='white')
    d.text((22,50),f"合わせ込み残差 RMS {rep['architecture_fit_rms_native_px']:.1f}px ／ 最大 {errors.max():.1f}px（原寸）",font=small,fill='white')
    floor_label=f'{floor_rms:.1f}px / 中央角度 {med:.2f}°' if candidates else '候補なし'
    d.text((22,81),f'床線方向の端点残差 {floor_label} ／ 選択候補 {len(candidates)}本',font=small,fill='white')
    d.text((22,112),'水色：観測線・点　赤：再投影点　紫：鉛直　橙：床面配置　黄：モデル底面候補',font=small,fill='white')
    d.text((22,139),'図面読取・写真推定。残差は独立した実測精度ではありません。橙・黄は遮蔽物の背後も表示。',font=small,fill='#dddddd')
    display.save(V/f'{shot}_verification.jpg',quality=94)
(V/'camera_validation.json').write_text(json.dumps(reports,ensure_ascii=False,indent=2),encoding='utf8')
print('CAMERA_VERIFICATION_COMPLETE',len(reports))
