"""Fresh checks for the rug revision. Covered feet do not require floor mirrors."""
from pathlib import Path
R=Path(__file__).resolve().parent
for name in ['photo_inspect','verify_scene','metrics','photo_master','camera_projection_consistency']:
    text=(R/f'{name}_Y.py').read_text(encoding='utf8').replace("O=R/'out_Y'","O=R/'out_Z'")
    text=text.replace('scene_delta_Y.json','scene_delta_Z.json').replace('metrics_Y.json','metrics_Z.json').replace('Harajuku_LDK_Y.blend','Harajuku_LDK_Z.blend').replace('photo_composite_Y.py','photo_composite_Z.py')
    if name=='photo_inspect':text=text.replace("'no_rug':not any(o.name.startswith('Shindo') for o in S.objects)","'rug_present':any(o.name.startswith('Shindo') for o in S.objects)")
    (R/f'{name}_Z.py').write_text(text,encoding='utf8')
text=(R/'validate_after_native_Y.py').read_text(encoding='utf8').replace("O=R/'out_Y'","O=R/'out_Z'")
for name in ['photo_inspect','verify_scene','photo_contacts_check','metrics','photo_master']:text=text.replace(f'{name}_Y.py',f'{name}_Z.py')
text=text.replace("('photo_inspect_Z.py',True)","('verify_rug_Z.py',True),('camera_projection_consistency_Z.py',True),('photo_inspect_Z.py',True)")
(R/'validate_after_native_Z.py').write_text(text,encoding='utf8')
print('Z_VALIDATION_PREPARED')
