from pathlib import Path
R=Path(__file__).resolve().parent
code=(R/'metrics_X.py').read_text().split('for shot in shots:')[0];exec(compile(code,str(R/'metrics_X.py'),'exec'))
old=image(W/'u2_full_composite.png');new=image(O/'u2_full_composite.png');photo=image(R/'images/photos_srgb/u2.png')
result={'wood_W':wood_stats(old,json.loads((W/'u2_camera.json').read_text())),'wood_X':wood_stats(new,json.loads((O/'u2_camera.json').read_text()))}
h,w=new.shape[:2];covw=cv2.imread(str(W/'u2_full_reflection_coverage.png'),0);covx=cv2.imread(str(O/'u2_full_reflection_coverage.png'),0);aa=cv2.imread(str(O/'u2_full_alpha.png'),0);zone=np.zeros((h,w),'uint8');zone[int(h*.60):int(h*.82),int(w*.09):int(w*.30)]=1;mask=(zone>0)&(covx>55)&(covw>55)&(aa<2)
result['floor']={k:float(luminance(im)[mask].mean()) for k,im in [('W',old),('X',new),('photo_same_pixels',photo)]}
print(json.dumps(result,indent=2));(O/'early_u2_metrics.json').write_text(json.dumps(result,indent=2))
