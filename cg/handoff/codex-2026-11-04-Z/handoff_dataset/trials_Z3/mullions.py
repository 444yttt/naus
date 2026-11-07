import numpy as np,cv2,sys,json
sys.path.insert(0,'/work/new');from bp import cam
def plan_lum(n,x0,x1,y0,y1,res=0.005):
    C,R,f,(cx,cy)=cam(n);img=cv2.imread(f'/work/new/{n}_src.jpg').astype('float32')/255
    X,Y=np.meshgrid(np.arange(x0,x1,res),np.arange(y0,y1,res))
    q=(np.stack([X,Y,np.zeros_like(X)],-1)-C)@R.T
    u=(q[...,0]/q[...,2]*f+cx).astype('float32');v=(q[...,1]/q[...,2]*f+cy).astype('float32')
    ok=(q[...,2]>0)&(u>0)&(u<1085)&(v>0)&(v<1447)
    L=cv2.remap(img,u,v,cv2.INTER_LINEAR).mean(2);L[~ok]=np.nan;return X,Y,L
def profile(n,box,slopes,res=0.005):
    X,Y,L=plan_lum(n,*box,res=res);best=None
    for s in slopes:
        foot=X-s*Y;bins=np.arange(box[0]-1,box[1],0.01);idx=np.digitize(foot,bins)
        v=np.bincount(idx[~np.isnan(L)],L[~np.isnan(L)],minlength=len(bins)+1);c=np.bincount(idx[~np.isnan(L)],minlength=len(bins)+1)
        p=np.where(c>200,v/np.maximum(c,1),np.nan)
        hp=p-cv2.GaussianBlur(np.nan_to_num(p,nan=np.nanmean(p)).reshape(1,-1),(0,0),8).ravel()
        score=np.nanstd(hp)
        if best is None or score>best[0]:best=(score,s,bins,hp)
    return best
for n,box in [('n03',(3.0,9.0,0.4,4.4)),('n04',(3.0,8.6,0.4,4.4))]:
    sc,s,bins,hp=profile(n,box,np.arange(0.08,0.30,0.01))
    mins=[(round(bins[i-1],2),round(float(hp[i]),3)) for i in range(2,len(hp)-2) if not np.isnan(hp[i]) and hp[i]<-0.03 and hp[i]==np.nanmin(hp[max(0,i-8):i+9])]
    print(n,'best slope',round(s,2),'mullion shadow feet (X at Y=0, depth):',mins)
print('--- horizontal stripes (profile vs Y, lit columns only)')
for n,box in [('n03',(4.4,5.2,0.2,4.8)),('n04',(5.7,7.0,0.2,4.8))]:
    X,Y,L=plan_lum(n,*box,res=0.005)
    p=np.nanmean(L,axis=1);yy=Y[:,0];hp=p-cv2.GaussianBlur(np.nan_to_num(p,nan=np.nanmean(p)).reshape(-1,1),(0,0),10).ravel()
    d=np.gradient(cv2.GaussianBlur(np.nan_to_num(p).reshape(-1,1),(0,0),3).ravel())
    print(n,'dark bands Y:',[(round(yy[i],2),round(float(hp[i]),3)) for i in range(5,len(hp)-5) if hp[i]<-0.02 and hp[i]==hp[max(0,i-10):i+11].min()],'strongest lit->shade edge Y:',round(yy[np.argmin(d)],2))
