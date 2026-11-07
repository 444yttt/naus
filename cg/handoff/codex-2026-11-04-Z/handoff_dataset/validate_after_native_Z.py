"""Wait for current render job, then run checks only, retaining failures."""
from pathlib import Path
import subprocess,sys,json,time
R=Path(__file__).resolve().parent;O=R/'out_Z';B=R/'runtime/blender-4.5.9-windows-x64/blender.exe'
while True:
    try: ready=json.loads((O/'native_progress.json').read_text())['state']=='renders_complete'
    except (FileNotFoundError,json.JSONDecodeError):ready=False
    if ready:break
    time.sleep(10)
for script,blender in [('verify_rug_Z.py',True),('camera_projection_consistency_Z.py',True),('photo_inspect_Z.py',True),('verify_scene_Z.py',True),('photo_contacts_check_Z.py',False),('metrics_Z.py',False),('photo_master_Z.py',True)]:
    print('VALIDATE',script,flush=True)
    with (O/f'{script}.log').open('w',encoding='utf8') as log:
        cmd=[str(B),'-b','--python-exit-code','1','--python',str(R/script)] if blender else [sys.executable,'-X','utf8',str(R/script)]
        subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT,check=True)
    text=(O/f'{script}.log').read_text(encoding='utf8',errors='replace')
    if 'Traceback (most recent call last)' in text:raise RuntimeError(script+' failed')
(O/'VALIDATION_READY.txt').write_text('Native checks finished. Visual review and acceptance assessment still required; no completion claim.\n')
print('Y_NATIVE_CHECKS_READY',flush=True)
