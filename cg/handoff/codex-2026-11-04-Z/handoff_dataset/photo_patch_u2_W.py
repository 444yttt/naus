from pathlib import Path
import cv2
R=Path(__file__).resolve().parent;O=R/'out/photo_final_W'
full=cv2.imread(str(O/'u2_full_foreground.png'),cv2.IMREAD_UNCHANGED)
roi=cv2.imread(str(O/'u2_repaired_native_ROI.png'),cv2.IMREAD_UNCHANGED)
H,W=full.shape[:2];x=int(W*.10);y=H-int(H*.52)
# Blender truncates the border pixel bounds; the cropped buffer itself provides
# the exact dimensions. No resizing, sharpening or alpha cutout of the chair.
full[y:y+roi.shape[0],x:x+roi.shape[1]]=roi
cv2.imwrite(str(O/'u2_full_foreground.png'),full)
print('U2_NATIVE_ROI_REPLACED',x,y,roi.shape)
