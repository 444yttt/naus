"""Initialize W camera inputs; rendering scripts are maintained in place."""
from pathlib import Path
import shutil
R=Path(__file__).resolve().parent;V=R/'out/photo_final_V';W=R/'out/photo_final_W';W.mkdir(exist_ok=True)
for shot in ['u1','u2','p09','p01','p13']:
 shutil.copy2(V/f'{shot}_camera.json',W/f'{shot}_camera.json')
print('W camera inputs ready; V deliveries preserved')
