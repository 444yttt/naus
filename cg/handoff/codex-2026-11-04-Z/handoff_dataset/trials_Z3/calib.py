import numpy as np,OpenEXR,cv2,json
R='/work/hj/handoff_dataset/'
def lin(v):v=v/255.;return np.where(v<=.04045,v/12.92,((v+.055)/1.055)**2.4)
def proj(c,P):
    q=(np.array(P)-np.array(c['C']))@np.array(c['R']).T;pp=c.get('principal_point_native_px',[c['W']/2,c['H']/2]);return q[:,:2]/q[:,2:]*c['f']+pp,q[:,2]
def load(shot):
    if shot=='u1':c=json.load(open(R+'out_Z2/u1_camera.json'));ph=cv2.imread(R+'images/photos_srgb/u1.png')[:,:,::-1]
    else:c=json.load(open(R+f'out_Z3/{shot}_camera_Z3.json'));ph=cv2.imread(R+f'out_Z3/{shot}_src.jpg')[:,:,::-1]
    cg=OpenEXR.File(f'/work/trial/calib_{shot}.exr').channels();k=[k for k in cg if k.endswith('R') or k=='RGB' or k=='RGBA'];
    img=cg['RGBA'].pixels[:,:,:3] if 'RGBA' in cg else np.stack([cg['R'].pixels,cg['G'].pixels,cg['B'].pixels],-1)
    return c,lin(ph.astype('float32')),img.astype('float32')
out={}
for shot in ['u1','n03','n04']:
    c,ph,cg=load(shot);H,W=ph.shape[:2];h,w=cg.shape[:2]
    pts=[[x,y,0] for x in np.arange(3.5,8.6,0.05) for y in np.arange(0.6,4.4,0.05)]
    ceil=[[x,y,2.7] for x in np.arange(3,9,0.25) for y in np.arange(1,6,0.25)]
    rows={}
    for name,P in [('floor',pts),('ceiling',ceil)]:
        uv,z=proj(c,P);ok=(z>0)&(uv[:,0]>5)&(uv[:,0]<W-5)&(uv[:,1]>5)&(uv[:,1]<H-5)
        uv=uv[ok];pv=ph[uv[:,1].astype(int),uv[:,0].astype(int)];cv=cg[(uv[:,1]*h/H).astype(int),(uv[:,0]*w/W).astype(int)]
        rows[name]=(pv,cv)
    pv,cv=rows['floor'];cl=cv@[.2126,.7152,.0722];
    lit=cl>np.percentile(cl,75);shade=cl<np.percentile(cl,35)
    pl=pv@[.2126,.7152,.0722]
    r={'P_lit_shade':float(pl[lit].mean()/pl[shade].mean()),'C_lit_shade':float(cl[lit].mean()/cl[shade].mean()),
       'A_floor_shade_rgb':(pv[shade].mean(0)/cv[shade].mean(0)).tolist()}
    pc,cc=rows['ceiling'];r['A_ceiling_rgb']=(pc.mean(0)/cc.mean(0)).tolist();r['n_ceiling']=len(pc);r['n_floor']=int(len(pv))
    out[shot]=r;print(shot,json.dumps({k:(np.round(v,3).tolist() if isinstance(v,list) else round(v,3) if isinstance(v,float) else v) for k,v in r.items()}))
for n in ['n03','n04']:
    S=2.5*(out[n]['P_lit_shade']-1)/(out[n]['C_lit_shade']-1)
    gf=np.array(out[n]['A_floor_shade_rgb'])/np.array(out['u1']['A_floor_shade_rgb']);gc=np.array(out[n]['A_ceiling_rgb'])/np.array(out['u1']['A_ceiling_rgb'])
    print(n,'sun strength',round(S,2),'gain floor',gf.round(3),'gain ceiling',gc.round(3))
