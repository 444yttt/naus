from pathlib import Path
import numpy as np,cv2,json
R=Path(__file__).resolve().parent;O=R/'out_Y';segments=json.loads((O/'p13_beam_segments.json').read_text());models=json.loads((O/'native_brown_diagnostic.json').read_text());rows=[]
def line_error(pts):
 v=cv2.fitLine(pts.astype('float32'),cv2.DIST_L2,0,.0001,.0001).reshape(-1);dx,dy,x,y=v;d=(pts[:,0]-x)*(-dy)+(pts[:,1]-y)*dx;return {'rms_px':float(np.sqrt((d*d).mean())),'max_px':float(abs(d).max())}
for name,ids in [('black_frame_upper_edge',[3,1,0]),('lower_glazing_gasket_edge',[28,29,32,27,30])]:
 points=np.concatenate([np.linspace(np.array(segments[i]['endpoints'])[:2],np.array(segments[i]['endpoints'])[2:],max(2,int(segments[i]['length']/12))) for i in ids]);baseline=line_error(points);row={'edge':name,'source_segment_ids':ids,'native_photo_straightness':baseline,'models':[]}
 for m in models:
  z=np.zeros(15);z[:len(m['parameters'])]=m['parameters'];f=np.exp(z[6]);cx,cy=np.array([3024/2,4032/2])+z[7:9]*3024;fy=f*np.exp(z[13]);yd=(points[:,1]-cy)/fy;xd=(points[:,0]-cx)/f-z[14]*yd;norm=np.stack([xd,yd],1);dist=np.r_[z[9:13],0];q=cv2.undistortPoints(norm[:,None,:],np.eye(3),dist).reshape(-1,2)*f;raw_affine=norm*f;raw=line_error(raw_affine);und=line_error(q);row['models'].append({'model':m['model'],'raw_affine_normalized_straightness':raw,'undistorted_straightness':und,'no_degradation_gate':und['rms_px']<=raw['rms_px']+.5 and und['max_px']<=raw['max_px']+1.,'independence':'long original-photo beam edges were not part of camera point fitting; endpoints extracted before evaluating model'})
 rows.append(row)
result={'purpose':'independent plumb-line validation: a lower fitted point RMS does not justify adding false optical curvature','edges':rows,'status':'diagnostic; production retains pinhole unless every independent edge passes'};(O/'native_lens_edge_validation.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
