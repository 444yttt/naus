from pathlib import Path
import subprocess,sys,json,time,shutil
R=Path(__file__).resolve().parent;O=R/'out/photo_final_W';B=R/'runtime/blender-4.5.9-windows-x64/blender.exe'
while True:
 try:
  d=json.loads((O/'progress.json').read_text())
  if d['state']=='renders_complete':break
 except (OSError,ValueError):pass
 time.sleep(15)
subprocess.run([sys.executable,str(R/'polish_eames_batch_W.py')],check=True)
for name in ['photo_inspect_W.py','photo_master_W.py']:
 with (O/(name+'.log')).open('w') as f:subprocess.run([str(B),'-b','--python',str(R/name)],stdout=f,stderr=subprocess.STDOUT,check=True)
source=O/'delivery/source';source.mkdir(parents=True,exist_ok=True)
shutil.copy2(O/'Harajuku_LDK_delivery_W.blend',source/'Harajuku_LDK_W.blend')
(source/'README.txt').write_text('編集用Blenderデータ。5視点のカメラと元写真の背景表示を含みます。カメラ切替時はカメラのphoto_width / photo_heightに解像度を合わせてください。\n最終画像は床反射・遮蔽・接地AOを別パスで合成しています。このblend単体のレンダーは最終JPGと同一にはなりません。家具の配置と形状は編集できます。\n',encoding='utf8')
for name in ['photo_details_W.py','photo_package_W.py']:
 subprocess.run([sys.executable,str(R/name)],check=True)
(O/'PACKAGE_READY.txt').write_text('W ready for visual QA and OneDrive upload',encoding='utf8')
print('W_FINALIZED',flush=True)
