from pathlib import Path
import subprocess,sys,json,time
R=Path(__file__).resolve().parent;O=R/'out/photo_final_W';B=R/'runtime/blender-4.5.9-windows-x64/blender.exe'
if (O/'POLISH_V2_DONE.txt').exists():sys.exit(0)
for shot in ['u1','u2','p09','p01','p13']:
 if (O/f'{shot}_polish_v2_done.txt').exists():continue
 (O/'polish_progress.json').write_text(json.dumps({'shot':shot,'phase':'native cushion surface','state':'running'}))
 meta=O/f'{shot}_polish_roi.json'
 current=meta.exists() and json.loads(meta.read_text()).get('surface_version')==2
 if not current or not all((O/f'{shot}_{suffix}').exists() for suffix in ['polish_foreground.png','polish_passes0001.exr']):
  with (O/f'{shot}_eames_polish.log').open('w') as f:subprocess.run([str(B),'-b','--python',str(R/'photo_polish_eames_W.py'),'--',shot],stdout=f,stderr=subprocess.STDOUT,check=True)
 subprocess.run([sys.executable,str(R/'photo_patch_eames_W.py'),shot],check=True)
 (O/'polish_progress.json').write_text(json.dumps({'shot':shot,'phase':'reflection updated geometry','state':'running'}))
 with (O/f'{shot}_polished_reflection.log').open('w') as f:subprocess.run([str(B),'-b','--python',str(R/'photo_floor_reflection_W.py'),'--',shot,'--repair-only'],stdout=f,stderr=subprocess.STDOUT,check=True)
 subprocess.run([sys.executable,str(R/'photo_composite_W.py'),shot,'full'],check=True)
 (O/f'{shot}_polish_v2_done.txt').write_text('Native and reflected layers updated from the same v2 geometry')
(O/'polish_progress.json').write_text(json.dumps({'state':'complete','surface_version':2}));(O/'POLISH_V2_DONE.txt').write_text('Common original-envelope cushion surface v2 repair complete')
print('EAMES_ALL_VIEWS_POLISHED',flush=True)
