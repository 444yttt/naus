"""Restore the previously accepted rug footprint behind common furniture."""
from pathlib import Path
R=Path(__file__).resolve().parent
s=(R/'plan_Y.py').read_text(encoding='utf8').replace("O=R/'out_Y'","O=R/'out_Z'").replace('Y/layout.json','Z/layout.json').replace('試作CG Y','試作CG Z').replace('配置図 Y','配置図 Z').replace('clearance_Y.json','clearance_Z.json')
s=s.replace("(O/'layout.json').write_text", "new['rug']['enabled']=True;new['rug']['status']='restored per latest user request; same earlier provisional footprint'\n(O/'layout.json').write_text")
needle="exec(compile(src,str(R/'plan_X.py'),'exec'))"
insertion="""src=src.replace(\"for i in C['items']:\", \"r=C['rug']['rect'];poly([[r[0],r[1]],[r[2],r[1]],[r[2],r[3]],[r[0],r[3]]],(202,189,165,180))\\nfor i in C['items']:\")
src=src.replace(\"'納品合成は元の撮影写真を使用'\",\"'納品合成は元の撮影写真を使用','Shindo Natural：4000×3500（前案の仮寸法）'\")
exec(compile(src,str(R/'plan_Z.py'),'exec'))"""
assert needle in s
s=s.replace(needle,insertion)
exec(compile(s,str(R/'plan_Z.py'),'exec'))
