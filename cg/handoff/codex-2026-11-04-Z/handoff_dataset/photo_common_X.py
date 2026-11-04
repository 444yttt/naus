import cv2,numpy as np
from photo_common_W import floor_mask,shadow_receiver_mask as W_receiver
def shadow_receiver_mask(shot,W,H):
 m=W_receiver(shot,W,H)
 if shot=='u2':ref=1368;poly=[[1135,535],[1256,552],[1368,531],[1368,712],[1254,730],[1133,685]]
 elif shot=='p13':ref=1368;poly=[[350,1075],[862,994],[949,991],[960,1040],[959,1270],[628,1636],[349,1419]]
 else:return m
 a=np.zeros((H,W),'uint8');cv2.fillPoly(a,[np.rint(np.array(poly)*W/ref).astype('int32')],255)
 return np.maximum(m,cv2.GaussianBlur(a.astype('float32')/255,(5,5),.8))
