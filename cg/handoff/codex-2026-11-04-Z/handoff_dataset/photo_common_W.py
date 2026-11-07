"""Photo-traced receiver boundaries; include the floor reflection of the island."""
import cv2,numpy as np
from photo_common_V import floor_mask as original_floor_mask,shadow_receiver_mask as original_receiver
def floor_mask(shot,W,H):
 if shot=='u2':
  # 1428-wide source trace: glazing-floor line, actual island toe/front bottom,
  # then cabinet toe. The island's reflection below this edge IS floor.
  ref=1428;poly=[[0,698],[1180,671],[1177,718],[1306,761],[1428,744],[1428,1071],[0,1071]]
 elif shot=='p09':
  ref=1368;poly=[[0,1280],[207,1243],[538,1150],[730,1087],[783,1078],[865,1052],[1368,1137],[1368,1824],[0,1824]]
 else:return original_floor_mask(shot,W,H)
 mask=np.zeros((H,W),np.uint8);cv2.fillPoly(mask,[np.rint(np.array(poly)*W/ref).astype('int32')],255)
 return cv2.GaussianBlur(mask.astype('float32')/255,(5,5),.8)
def shadow_receiver_mask(shot,W,H):
 if shot in ['u2','p09']:return floor_mask(shot,W,H)
 return original_receiver(shot,W,H)
