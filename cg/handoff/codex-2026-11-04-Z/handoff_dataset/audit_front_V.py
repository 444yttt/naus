import bpy
from pathlib import Path
R=Path(__file__).resolve().parent;bpy.ops.wm.open_mainfile(filepath=str(R/'out/3d_R/Harajuku_LDK_R.blend'))
root=bpy.data.objects['Beolab28_OFFICIAL_0']
for o in root.children:
 if 'fabric' in o.name:
  vv=[o.matrix_local@v.co for v in o.data.vertices];print('FABRIC meanXY',sum(v.x for v in vv)/len(vv),sum(v.y for v in vv)/len(vv))
