from pathlib import Path
import cv2,numpy as np,json,itertools
R=Path(__file__).resolve().parent;O=R/'out/photo_geometry_T';names=['u1','u2','p01','p03','p09','p13'];fs={};imgs={};sf=cv2.SIFT_create(nfeatures=20000,contrastThreshold=.01)
# Shared orthographic floor coordinate system; camera poses are only provisional rectification guesses.
G=np.array([[220,0,100],[0,-220,3100],[0,0,1.]])
for n in names:
 c=json.loads((R/f'out/photo_composite_S/{n}_camera.json').read_text());r=np.array(c['R']);t=-r@c['C'];K=np.array([[c['f'],0,c['W']/2],[0,c['f'],c['H']/2],[0,0,1]]);H=K@np.column_stack([r[:,0],r[:,1],t]);T=G@np.linalg.inv(H)
 im=cv2.imread(str(R/f'images/photos/{n}.jpg'));im=cv2.warpPerspective(im,T,(2400,3200));imgs[n]=im
 # Bounding plan and projected source restrict image; floor segmentation added from conservative original mask.
 from photo_common_S import floor_mask
 mask=(floor_mask(n,c['W'],c['H'])*255).astype(np.uint8) if n!='p03' else np.uint8(np.indices((c['H'],c['W']))[0]>c['H']*.8)*255
 mask=cv2.warpPerspective(mask,T,(2400,3200));mask=cv2.erode(mask,np.ones((21,21),np.uint8));kp,de=sf.detectAndCompute(cv2.cvtColor(im,cv2.COLOR_BGR2GRAY),mask);fs[n]=(kp,de)
 cv2.imwrite(str(O/f'{n}_floor_rectified.jpg'),im);print(n,len(kp),flush=True)
bf=cv2.BFMatcher();edges=[]
for a,b in itertools.combinations(names,2):
 ka,da=fs[a];kb,db=fs[b];mm=bf.knnMatch(da,db,k=2);good=[m for m,n in mm if m.distance<.7*n.distance]
 if len(good)<8:continue
 pa=np.float32([ka[m.queryIdx].pt for m in good]);pb=np.float32([kb[m.trainIdx].pt for m in good]);H,ok=cv2.findHomography(pa,pb,cv2.USAC_MAGSAC,3,maxIters=20000,confidence=.999)
 if H is None:continue
 yes=ok.ravel().astype(bool);count=int(yes.sum());err=np.linalg.norm(cv2.perspectiveTransform(pa[yes,None],H)[:,0]-pb[yes],axis=1)
 print(a,b,'matches',len(good),'inliers',count,'median',round(float(np.median(err)),2),flush=True)
 if count<8:continue
 edges.append(dict(a=a,b=b,count=count,H=H.tolist(),pa=pa[yes].tolist(),pb=pb[yes].tolist()))
 view=cv2.drawMatches(imgs[a],ka,imgs[b],kb,[m for m,y in zip(good,yes) if y][:65],None,flags=2);cv2.imwrite(str(O/f'rectified_matches_{a}_{b}.jpg'),cv2.resize(view,(1400,933)))
(O/'rectified_floor_matches.json').write_text(json.dumps(edges),encoding='utf8')
