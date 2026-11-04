from pathlib import Path
import json,cv2,numpy as np,OpenEXR
import sys
R=Path(__file__).resolve().parent;O=R/'out/photo_final_W';shot=sys.argv[1];meta=json.loads((O/f'{shot}_polish_roi.json').read_text())
if meta['visible_roi']:
 full=cv2.imread(str(O/f'{shot}_full_foreground.png'),-1);roi=cv2.imread(str(O/f'{shot}_polish_foreground.png'),-1)
 x,y,w,h=[meta[k] for k in ['x','y','width','height']];assert roi.shape[:2]==(h,w),(roi.shape,meta)
 full[y:y+h,x:x+w]=roi;cv2.imwrite(str(O/f'{shot}_full_foreground.png'),full);del full,roi
 old=OpenEXR.File(str(O/f'{shot}_full_passes0001.exr'));new=OpenEXR.File(str(O/f'{shot}_polish_passes0001.exr'));channels={}
 for name,ch in old.channels().items():
  a=ch.pixels.copy()
  if name in new.channels():
   b=new.channels()[name].pixels;assert b.shape[:2]==(h,w),(name,b.shape,meta);a[y:y+h,x:x+w]=b
  channels[name]=a
 temporary=O/f'{shot}_repaired_passes.exr'
 OpenEXR.File({'compression':OpenEXR.ZIP_COMPRESSION,'type':OpenEXR.scanlineimage},channels).write(str(temporary))
 # Release native EXR readers before replacing their file on Windows.
 del old,new,ch
 try:del b
 except NameError:pass
 import gc;gc.collect()
 temporary.replace(O/f'{shot}_full_passes0001.exr')
path=O/f'{shot}_refinement.json';settings=json.loads(path.read_text());settings['final_eames_surface_repair']=meta
for item in settings.get('mesh',[]):
 if item['object'].startswith('SEAT-FABRIC'):
  for key in list(item):
   if key not in ['object','original_vertices']:item.pop(key)
  item.update(surface_version=2,source_components=5,repair='interpolated visible pad envelopes; timber-covered rear skin omitted; fine relief simplified')
path.write_text(json.dumps(settings,indent=2))
print('EAMES_NATIVE_LAYER_UPDATED',shot)
