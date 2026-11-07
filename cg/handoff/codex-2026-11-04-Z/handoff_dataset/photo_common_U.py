from photo_common_S import floor_mask as old_floor_mask
import numpy as np,cv2
POLYS={
'n01':[[0,830],[438,739],[507,713],[960,808],[960,1280],[0,1280]],
'n02':[[0,758],[539,745],[656,748],[707,828],[960,1260],[960,1280],[0,1280]],
'n03':[[0,813],[25,798],[355,732],[400,742],[910,801],[960,803],[960,1280],[0,1280]],
'n04':[[0,1280],[178,787],[214,725],[702,718],[702,727],[753,750],[855,741],[855,783],[960,831],[960,1280]]}
def floor_mask(shot,W,H):
 if shot not in POLYS:return old_floor_mask(shot,W,H)
 mask=np.zeros((H,W),np.uint8);cv2.fillPoly(mask,[np.rint(np.array(POLYS[shot])*[W/960,H/1280]).astype(np.int32)],255)
 return cv2.GaussianBlur(mask.astype('float32')/255,(5,5),.8)
