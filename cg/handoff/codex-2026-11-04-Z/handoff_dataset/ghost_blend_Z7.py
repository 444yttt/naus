"""n03 presentation see-through: inside the user-marked area, the Linha table and Torii chairs are
shown at 30% opacity over the same view rendered without them (both full pipeline composites)."""
import cv2,numpy as np,json
O='out_Z7/';G='out_Z7g/'
w=cv2.imread(O+'n03_full_composite.png').astype('float32');wo=cv2.imread(G+'n03_full_composite.png').astype('float32');H,W=w.shape[:2]
poly=np.array([[118,935],[643,831],[670,970],[139,1073]],np.float32)   # user markup (screenshot 921 px wide, image top y=385) mapped to 1086x1448
area=np.zeros((H,W),np.uint8);cv2.fillPoly(area,[np.rint(poly).astype(np.int32)],1)
area=cv2.dilate(area,np.ones((41,41),np.uint8))
diff=(np.abs(w-wo).max(2)>6).astype(np.uint8)
occ=cv2.morphologyEx(diff,cv2.MORPH_CLOSE,np.ones((7,7),np.uint8))
soft=cv2.GaussianBlur(area.astype('float32'),(0,0),25.0)  # wide feather: no hard cut on the table top
m=(cv2.GaussianBlur(occ.astype('float32'),(0,0),1.5)*soft)[:,:,None]
opacity=0.25
out=w*(1-m)+(w*opacity+wo*(1-opacity))*m
out=np.clip(np.rint(out),0,255).astype(np.uint8)
cv2.imwrite(O+'n03_full_composite_seethrough.png',out,[cv2.IMWRITE_PNG_COMPRESSION,6])
cv2.imwrite(O+'n03_seethrough_mask.png',np.uint8(m[:,:,0]*255))
json.dump({'opacity_of_table_and_chairs':opacity,'area_polygon_px':poly.tolist(),'area_dilation_px':20,'feather_sigma_px':25,'note':'presentation see-through requested by the user; not a physical render of a transparent table'},open(O+'n03_seethrough.json','w'),indent=2)
print('ok',int(occ.sum()))
