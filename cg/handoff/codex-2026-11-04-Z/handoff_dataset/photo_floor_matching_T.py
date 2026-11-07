from pathlib import Path
import cv2,numpy as np,json,itertools
R=Path(__file__).resolve().parent;O=R/'out/photo_geometry_T';O.mkdir(exist_ok=True)
names=['u1','u2']+[f'p{i:02}' for i in range(1,15)]
# Conservative interior floor masks, normalized to photograph dimensions.
polys={
'u1':[[0,.62],[.23,.58],[.59,.57],[1,.78],[1,1],[0,1]],
'u2':[[0,.66],[.81,.64],[.81,.83],[1,.94],[1,1],[0,1]],
'p01':[[0,.72],[1,.72],[1,1],[0,1]],
'p02':[[0,.73],[.67,.73],[.67,.86],[1,.93],[1,1],[0,1]],
'p03':[[0,.72],[.15,.68],[1,.89],[1,1],[0,1]],
'p04':[[0,.81],[1,.81],[1,1],[0,1]],
'p05':[[0,.7],[1,.7],[1,1],[0,1]],
'p06':[[0,.68],[.12,.64],[1,.82],[1,1],[0,1]],
'p07':[[0,.97],[.2,.97],[.1,1],[0,1]],
'p08':[[.48,.75],[.62,.67],[.90,.67],[1,.82],[1,1],[.65,1]],
'p09':[[0,.73],[.62,.60],[1,.65],[1,1],[0,1]],
'p10':[[0,.68],[1,.68],[1,1],[0,1]],
'p11':[[0,.62],[1,.62],[1,1],[0,1]],
'p12':[[0,.69],[.63,.53],[1,.61],[1,1],[0,1]],
'p13':[[0,.75],[.235,.7],[.235,.79],[.46,.91],[.71,.72],[.82,.66],[1,.79],[1,1],[0,1]],
'p14':[[0,.65],[.2,.65],[.2,.73],[0,.81]]}
sift=cv2.SIFT_create(nfeatures=18000,contrastThreshold=.015,edgeThreshold=15)
features={};imgs={}
for n in names:
 im=cv2.imread(str(R/f'images/photos/{n}.jpg'));im=cv2.resize(im,(1600,round(im.shape[0]*1600/im.shape[1])));imgs[n]=im
 h,w=im.shape[:2];mask=np.zeros((h,w),np.uint8);cv2.fillPoly(mask,[np.rint(np.array(polys[n])*[w,h]).astype(np.int32)],255)
 k,d=sift.detectAndCompute(cv2.cvtColor(im,cv2.COLOR_BGR2GRAY),mask);features[n]=(k,d)
 print(n,len(k),flush=True)
bf=cv2.BFMatcher();edges=[]
for a,b in itertools.combinations(names,2):
 ka,da=features[a];kb,db=features[b]
 if da is None or db is None:continue
 mm=bf.knnMatch(da,db,k=2);good=[m for m,n in mm if m.distance<.65*n.distance]
 if len(good)<12:continue
 pa=np.float32([ka[m.queryIdx].pt for m in good]);pb=np.float32([kb[m.trainIdx].pt for m in good]);H,ok=cv2.findHomography(pa,pb,cv2.USAC_MAGSAC,2.5,maxIters=20000,confidence=.999)
 if H is None:continue
 yes=ok.ravel().astype(bool);count=int(yes.sum());err=np.linalg.norm(cv2.perspectiveTransform(pa[yes,None],H)[:,0]-pb[yes],axis=1)
 if count<12:continue
 # Spatial spread rejects tiny repeated knots with ill-conditioned geometry.
 ar=cv2.contourArea(cv2.convexHull(pa[yes]));br=cv2.contourArea(cv2.convexHull(pb[yes]));spread=min(ar,br)/(1600**2)
 if spread<.002:continue
 row=dict(a=a,b=b,count=count,spread=spread,median_px=float(np.median(err)),H=H.tolist(),pa=pa[yes].tolist(),pb=pb[yes].tolist())
 edges.append(row);print(a,b,count,round(spread,3),round(float(np.median(err)),2),flush=True)
 if count>=35:
  view=cv2.drawMatches(imgs[a],ka,imgs[b],kb,[m for m,y in zip(good,yes) if y][:45],None,flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)
  cv2.imwrite(str(O/f'matches_{a}_{b}.jpg'),cv2.resize(view,(1600,round(view.shape[0]*1600/view.shape[1]))))
(O/'floor_matches.json').write_text(json.dumps(edges),encoding='utf8')
