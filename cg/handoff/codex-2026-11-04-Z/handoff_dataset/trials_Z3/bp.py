import json,numpy as np,sys
def cam(n,W=1086):
    c=json.load(open(f'/work/new/{n}_camera_Z3.json'))
    return np.array(c['C']),np.array(c['R']),c['f'],tuple(c['principal_point_native_px'])
def floor(n,px,z=0.0):
    C,R,f,(cx,cy)=cam(n);out=[]
    for u,v in px:
        d=R.T@np.array([(u-cx)/f,(v-cy)/f,1.0]);t=(z-C[2])/d[2];out.append((C+t*d).round(3).tolist())
    return out
def proj(n,P):
    C,R,f,(cx,cy)=cam(n);q=(np.array(P)-C)@R.T;return (q[:,:2]/q[:,2:]*f+[cx,cy]).round(1).tolist()
if __name__=='__main__':
    n=sys.argv[1];pts=json.loads(sys.argv[2]);print(floor(n,pts))
