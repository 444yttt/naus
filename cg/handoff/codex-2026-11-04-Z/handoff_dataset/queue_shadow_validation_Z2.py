"""Final Z diffuse-shadow comparison; kept separate from dark-wood reflection."""
from pathlib import Path
import json,subprocess,sys,time,shutil
R=Path(__file__).resolve().parent;O=R/'out_Z2';D=O/'shadow_audit';D.mkdir(exist_ok=True)
for p in (R/'out_Y/shadow_audit').glob('u2_W_*'):shutil.copy2(p,D/p.name)
script=(R/'shadow_separation_Y.py').read_text(encoding='utf8').replace("out_Y/shadow_audit'","out_Z2/shadow_audit'")
script=script.replace('allprobes={}',"allprobes={'W':json.loads((R/'out_Y/shadow_audit/world_floor_probes.json').read_text())['probes']['W']}")
script=script.replace("[('W',R/'out/photo_final_W'),('Y',R/'out_Y')]","[('Z2',R/'out_Z2')]")
script=script.replace("'sun_first_hit':obj.name if h else None,'sun_blocked_by_Eames':h and obj.name.startswith('SEAT-')","'sun_first_hit':None,'sun_blocked_by_Eames':None")
(R/'shadow_separation_final_Z2.py').write_text(script,encoding='utf8')
with (D/'render.log').open('w') as log:
    subprocess.run([str(R/'runtime/blender-4.5.9-windows-x64/blender.exe'),'-b','--python-exit-code','1','--python',str(R/'shadow_separation_final_Z2.py')],stdout=log,stderr=subprocess.STDOUT,check=True)
metric=(R/'shadow_isolation_metrics_Y.py').read_text(encoding='utf8').replace("out_Y/shadow_audit'","out_Z2/shadow_audit'").replace("['W','Y']","['W','Z2']").replace("sets['Y']","sets['Z2']")
(R/'shadow_isolation_final_metrics_Z2.py').write_text(metric,encoding='utf8')
subprocess.run([sys.executable,str(R/'shadow_isolation_final_metrics_Z2.py')],check=True)
print('Z2_FINAL_SHADOW_DIAGNOSTIC_READY',flush=True)
