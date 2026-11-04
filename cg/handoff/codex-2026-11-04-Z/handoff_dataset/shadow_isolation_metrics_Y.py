from pathlib import Path
import cv2,numpy as np,OpenEXR,json
O=Path(__file__).resolve().parent/'out_Y/shadow_audit';p=json.loads((O/'world_floor_probes.json').read_text());sets=p['probes']
key=lambda r:tuple(round(x,4) for x in r['world'][:2]);common=set(key(r) for r in sets['W'])&set(key(r) for r in sets['Y']);rows=[]
for version in ['W','Y']:
 probes=[r for r in sets[version] if key(r) in common];fields=[]
 for name in ['all','no_Eames']:
  f=OpenEXR.File(str(O/f'u2_{version}_{name}_passes0001.exr')).channels()['Shadow Catcher'].pixels[:,:,:3].astype('float32');h,w=f.shape[:2];uv=np.array([r['uv_normalized'] for r in probes],dtype='float32');xx=(uv[:,0]*w-.5).reshape(-1,1);yy=(uv[:,1]*h-.5).reshape(-1,1);fields.append(cv2.remap(f,xx,yy,cv2.INTER_LINEAR).reshape(-1,3))
 ratio=np.divide(fields[0],fields[1],out=np.ones_like(fields[0]),where=fields[1]>.05);value=ratio@np.array([.2126,.7152,.0722]);rows.append({'version':version,'same_visible_world_samples':len(probes),'mean_Eames_only_floor_shadow_ratio':float(value.mean()),'mean_shadow_deficit':float(np.maximum(1-value,0).mean()),'ratio_percentiles_5_50_95':np.percentile(value,[5,50,95]).tolist(),'ratio_mean_RGB':ratio.mean(0).tolist(),'method':'same fixed world-floor annulus visible in both cameras, full scene divided by scene with only Eames hidden; no reflected-furniture radiance in this metric','sampling':'25% radiometric diagnostic,24samples; not final native visual acceptance'})
result={'definition':p['definition'],'results':rows,'historical_mixed_shadow_reflection_ROI':'retained separately in preview_metrics.json; the annulus here tests actual incremental diffuse shadow transport, not the mirror-image region under the chair','shadow_deficit_reduced':rows[1]['mean_shadow_deficit']<rows[0]['mean_shadow_deficit']};(O/'isolated_shadow_metrics.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
