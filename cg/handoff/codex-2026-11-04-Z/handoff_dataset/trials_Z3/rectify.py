import numpy as np,cv2,sys
sys.path.insert(0,'/work/new');from bp import cam
def rectify(n,x0,x1,y0,y1,res=0.01):
    C,R,f,(cx,cy)=cam(n);img=cv2.imread(f'/work/new/{n}_src.jpg')
    X,Y=np.meshgrid(np.arange(x0,x1,res),np.arange(y1,y0,-res))
    P=np.stack([X,Y,np.zeros_like(X)],-1)-C;q=P@R.T
    u=(q[...,0]/q[...,2]*f+cx).astype('float32');v=(q[...,1]/q[...,2]*f+cy).astype('float32')
    out=cv2.remap(img,u,v,cv2.INTER_LINEAR,borderValue=(255,255,255));out[q[...,2]<=0]=255
    for gx in np.arange(np.ceil(x0),x1,1.0):
        c=int((gx-x0)/res);cv2.line(out,(c,0),(c,out.shape[0]),(0,0,255),1);cv2.putText(out,f'X{gx:.0f}',(c+2,15),0,.4,(0,0,255),1)
    for gy in np.arange(np.ceil(y0),y1,1.0):
        r=int((y1-gy)/res);cv2.line(out,(0,r),(out.shape[1],r),(255,0,0),1);cv2.putText(out,f'Y{gy:.0f}',(2,r-2),0,.4,(255,0,0),1)
    return out
n=sys.argv[1];cv2.imwrite(f'/work/rv/{n}_plan.png',rectify(n,*map(float,sys.argv[2:6])))
