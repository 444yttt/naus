from pathlib import Path
R=Path(__file__).resolve().parent
for n in ['photo_floor_reflection','photo_contact','photo_composite','photo_inspect','photo_contacts_check','photo_details','photo_master']:
 text=(R/(n+'_W.py')).read_text(encoding='utf8').replace("R/'out/photo_final_W'","R/'out_X'").replace('photo_common_W','photo_common_X').replace('photo_composite_W','photo_composite_X').replace('photo_contacts_check_W','photo_contacts_check_X')
 (R/(n+'_X.py')).write_text(text,encoding='utf8')
