from pathlib import Path
import subprocess,sys,json,time
R=Path(__file__).resolve().parent;O=R/'out_Y';B=R/'runtime/blender-4.5.9-windows-x64/blender.exe';status={'started':time.time(),'completed':[],'state':'running'}
def save():(O/'preview_progress.json').write_text(json.dumps(status,indent=2))
for shot in ['p09','u1','u2','p01','p13']:
 for script,phase,opts in [('prepare_Y.py','prepare',[]),('render_Y.py','foreground',['--preview']),('render_Y.py','background',['--background','--preview']),('photo_floor_reflection_Y.py','reflection',['--preview']),('photo_contact_Y.py','contact',['--preview'])]:
  status.update(shot=shot,phase=phase);save();print('START',shot,phase,flush=True)
  with (O/f'{shot}_preview_{phase}.log').open('w') as log:subprocess.run([str(B),'-b','--python',str(R/script),'--',shot]+opts,stdout=log,stderr=subprocess.STDOUT,check=True)
 status.update(phase='reflection_display');save();subprocess.run([sys.executable,str(R/'transform_reflection_Y.py'),shot,'preview'],check=True)
 subprocess.run([sys.executable,str(R/'photo_composite_Y.py'),shot,'preview'],check=True);status['completed'].append(shot);save();print('PREVIEW_COMPLETE',shot,flush=True)
status.update(state='previews_complete');save();print('Y_PREVIEWS_RENDERED',flush=True)
