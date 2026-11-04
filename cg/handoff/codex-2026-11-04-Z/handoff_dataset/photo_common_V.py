from photo_common_S import floor_mask
import cv2,numpy as np
def shadow_receiver_mask(shot,W,H):
 m=floor_mask(shot,W,H)
 if shot=='p13':
  top=np.zeros((H,W),np.uint8);p=np.rint(np.array([[350,1075],[630,1140],[960,1040],[949,991],[862,994]])*W/1368).astype(np.int32);cv2.fillPoly(top,[p],255)
  m=np.maximum(m,cv2.GaussianBlur(top.astype('float32')/255,(5,5),.8))
 return m
