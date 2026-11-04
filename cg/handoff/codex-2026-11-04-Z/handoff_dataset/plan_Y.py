from pathlib import Path
import json,math,copy,difflib
import numpy as np
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parent;O=R/'out_Y';W=R/'out/photo_final_W/delivery';old=json.loads((W/'layout.json').read_text(encoding='utf8'));new=copy.deepcopy(old);change=json.loads((R/'out_X/u2_placement_X.json').read_text());di=next(i for i in new['items'] if i['id']=='dining');before=np.array(change['root_center_before'][:2]);after=np.array(change['root_center_after'][:2]);angle=math.radians(change['rotation_delta_deg']);rot=np.array([[math.cos(angle),-math.sin(angle)],[math.sin(angle),math.cos(angle)]])
di['center']=after.tolist();di['angle']=change['angle_deg']
for ch in new['chairs']['items']:ch['center']=(rot@(np.array(ch['center'])-before)+after).tolist();ch['angle']+=change['rotation_delta_deg']
(O/'layout.json').write_text(json.dumps(new,ensure_ascii=False,indent=2),encoding='utf8')
diff=''.join(difflib.unified_diff(json.dumps(old,ensure_ascii=False,indent=2).splitlines(True),json.dumps(new,ensure_ascii=False,indent=2).splitlines(True),fromfile='W/layout.json',tofile='Y/layout.json'))
(O/'layout.diff').write_text(diff,encoding='utf8')
# Use the approved plan renderer with new layout, removing the old420mm line.
src=(R/'photo_plan_map_V.py').read_text(encoding='utf8')
src=src.replace("R=Path('handoff_dataset');O=R/'out/photo_final_V';C=json.loads((R/'out/layout_V.json').read_text(encoding='utf8'))","R=Path(__file__).resolve().parent;O=R/'out_Y';C=json.loads((O/'layout.json').read_text(encoding='utf8'))")
src=src.replace("gap,a,b=min(rows,key=lambda x:x[0]);d.line([xy(a),xy(b)],fill='#dc4430',width=6)","gap,a,b=min(rows,key=lambda x:x[0])")
src=src.replace("for p in [a,b]:x,y=xy(p);d.ellipse((x-5,y-5,x+5,y+5),fill='#dc4430')",'')
src=src.replace('参考例｜原宿3LDK｜予算1,500万円','参考例｜原宿3LDK｜試作CG Y').replace('配置図 V｜試作CG・スピーカー左右対称','配置図 Y｜共通配置・スピーカー左右対称').replace('赤線：テーブル端〜カウンター端の最短距離 約420mm','テーブル短辺とアイランド端面：モデル上 約2mm').replace("O/'plan_V.png'","O/'07_plan.png'").replace("O/'clearance_V.json'","O/'clearance_Y.json'").replace('speaker pair only; other approved placements unchanged','dining table + six chairs only')
exec(compile(src,str(R/'plan_X.py'),'exec'))
