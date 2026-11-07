"""Z3: receiver masks for the two added user photos (n03/n04, 1086x1448). The traced U polygons
(960x1280 trace of the same photographs) are scaled; other shots delegate to the X chain unchanged."""
import cv2,numpy as np
from photo_common_X import floor_mask as X_floor,shadow_receiver_mask as X_receiver
from photo_common_U import POLYS
def floor_mask(shot,W,H):
    if shot not in ('n03','n04'):return X_floor(shot,W,H)
    m=np.zeros((H,W),np.uint8);cv2.fillPoly(m,[np.rint(np.array(POLYS[shot])*[W/960,H/1280]).astype(np.int32)],255)
    return cv2.GaussianBlur(m.astype('float32')/255,(5,5),.8)
def shadow_receiver_mask(shot,W,H):
    if shot in ('n03','n04'):return floor_mask(shot,W,H)
    return X_receiver(shot,W,H)
