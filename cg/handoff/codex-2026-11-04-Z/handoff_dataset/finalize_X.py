from pathlib import Path
import subprocess,sys,json,time
R=Path(__file__).resolve().parent;O=R/'out_X';B=R/'runtime/blender-4.5.9-windows-x64/blender.exe'
while True:
 try:ready=json.loads((O/'progress.json').read_text())['state']=='renders_complete'
 except (FileNotFoundError,json.JSONDecodeError):ready=False
 if ready:break
 time.sleep(10)
for script,blender in [('photo_inspect_X.py',True),('verify_scene_X.py',True),('photo_master_X.py',True),('photo_details_X.py',False),('metrics_X.py',False),('package_X.py',False)]:
 print('FINALIZE',script,flush=True)
 with (O/f'{script}.log').open('w',encoding='utf8') as log:
  cmd=[str(B),'-b','--python',str(R/script)] if blender else [sys.executable,'-X','utf8',str(R/script)]
  subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT,check=True)
(O/'PACKAGE_READY.txt').write_text('X review package generated; acceptance NOT complete. See report.md.\n')
print('X_REVIEW_PACKAGE_READY',flush=True)
