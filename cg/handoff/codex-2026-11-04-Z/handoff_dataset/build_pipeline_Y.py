from pathlib import Path
R=Path(__file__).resolve().parent
for src,dest in [('render_X.py','render_Y.py'),('photo_floor_reflection_X.py','photo_floor_reflection_Y.py'),('photo_contact_X.py','photo_contact_Y.py')]:
 text=(R/src).read_text().replace("O=R/'out_X'","O=R/'out_Y'").replace('X_RENDERED','Y_RENDERED');(R/dest).write_text(text)
text=(R/'photo_composite_X.py').read_text().replace("O=R/'out_X'","O=R/'out_Y'")
old="refl=(unprem/(1+unprem))*opacity"
new="""display=cv2.imread(str(O/f'{shot}_{mode}_reflection_unprem_agx.png'),cv2.IMREAD_UNCHANGED)[:,:,:3].astype('float32')/65535
 if display.shape[:2]!=(H,W):display=cv2.resize(display,(W,H),interpolation=cv2.INTER_LINEAR)
 refl=lin(display)*opacity"""
assert old in text;text=text.replace(old,new);(R/'photo_composite_Y.py').write_text(text)
