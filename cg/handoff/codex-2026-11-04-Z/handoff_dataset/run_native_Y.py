from pathlib import Path
import subprocess,sys,json,time
R=Path(__file__).resolve().parent;O=R/'out_Y';B=R/'runtime/blender-4.5.9-windows-x64/blender.exe';status={'started':time.time(),'completed':[],'state':'running','description':'all-five new native renders; original photos preserved, common lighting/layout'}
def save():(O/'native_progress.json').write_text(json.dumps(status,indent=2))
for shot in ['p09','u1','u2','p01','p13']:
 for script,phase,opts in [('prepare_Y.py','prepare',[]),('render_Y.py','foreground',[]),('render_Y.py','background',['--background']),('photo_floor_reflection_Y.py','reflection',[]),('photo_contact_Y.py','contact',[])]:
  status.update(shot=shot,phase=phase);save();print('START_NATIVE',shot,phase,flush=True)
  with (O/f'{shot}_native_{phase}.log').open('w') as log:subprocess.run([str(B),'-b','--python-exit-code','1','--python',str(R/script),'--',shot]+opts,stdout=log,stderr=subprocess.STDOUT,check=True)
  logtext=(O/f'{shot}_native_{phase}.log').read_text(errors='replace')
  if any(e in logtext for e in ['Traceback (most recent call last)','SyntaxError:','Error: Python:']):raise RuntimeError('Blender Python failure: '+shot+' '+phase)
 status.update(phase='reflection_display');save();subprocess.run([sys.executable,str(R/'transform_reflection_Y.py'),shot,'full'],check=True)
 subprocess.run([sys.executable,str(R/'photo_composite_Y.py'),shot,'full'],check=True);status['completed'].append(shot);save();print('NATIVE_COMPLETE',shot,flush=True)
status.update(state='renders_complete');save();print('Y_ALL_NATIVE_RENDERED',flush=True)
