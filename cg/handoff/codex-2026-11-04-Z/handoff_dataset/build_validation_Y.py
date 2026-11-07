"""Prepare read-only Y checks; do not package or claim acceptance."""
from pathlib import Path
R=Path(__file__).resolve().parent
for name in ['photo_inspect','photo_contacts_check','photo_master','metrics','verify_scene']:
    text=(R/f'{name}_X.py').read_text(encoding='utf8')
    text=text.replace("O=R/'out_X'", "O=R/'out_Y'")
    if name=='verify_scene':
        text=text.replace("(O/'before_snapshot.json')", "(R/'out_X/before_snapshot.json')")
    text=text.replace('scene_delta_X.json','scene_delta_Y.json').replace('metrics_X.json','metrics_Y.json')
    if name=='metrics':
        text=text.replace("'X'", "'Y'").replace('X_', 'Y_').replace('near_X_', 'near_Y_')
    if name=='photo_master':
        text=text.replace('Harajuku_LDK_X.blend','Harajuku_LDK_Y.blend').replace('photo_composite_X.py','photo_composite_Y.py')
    (R/f'{name}_Y.py').write_text(text,encoding='utf8')
print('Y_VALIDATION_SCRIPTS_PREPARED')
