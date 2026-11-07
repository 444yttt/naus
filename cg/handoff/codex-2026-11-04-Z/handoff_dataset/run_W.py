from pathlib import Path
import subprocess,sys,json,time
R=Path(__file__).resolve().parent;O=R/'out/photo_final_W';B=R/'runtime/blender-4.5.9-windows-x64/blender.exe'
status={'started':time.time(),'completed':[],'state':'running'}
def save(): (O/'progress.json').write_text(json.dumps(status,indent=2))
for shot in ['u2','u1','p09','p01','p13']:
 for script,phase in [('photo_scene_W.py','foreground'),('photo_scene_W.py','background'),('photo_floor_reflection_W.py','reflection'),('photo_contact_W.py','contact')]:
  status.update(shot=shot,phase=phase);save();print('START',shot,phase,flush=True)
  with (O/f'{shot}_{phase}.log').open('w') as log:
   subprocess.run([str(B),'-b','--python',str(R/script),'--',shot]+(['--background'] if phase=='background' else []),stdout=log,stderr=subprocess.STDOUT,check=True)
 status.update(phase='composite');save()
 subprocess.run([sys.executable,str(R/'photo_composite_W.py'),shot,'full'],check=True)
 status['completed'].append(shot);save();print('COMPLETE',shot,flush=True)
status.update(state='renders_complete');save()
print('W_ALL_RENDERED',flush=True)
