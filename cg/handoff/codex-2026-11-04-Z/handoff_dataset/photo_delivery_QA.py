"""Validate native photo composites and produce a compact before/after sheet."""
from pathlib import Path
import json,hashlib,cv2,numpy as np
from PIL import Image,ImageOps,ImageDraw
import OpenEXR
R=Path(__file__).resolve().parent;O=R/'out/photo_composite_S';shots=['p09','u1','u2','p01','p13'];report=[]
for shot in shots:
 file=O/f'{shot}_full_composite.jpg';entry={'shot':shot,'complete':False}
 if not file.exists():report.append(entry);continue
 photo=Image.open(R/f'images/photos/{shot}.jpg');out=Image.open(file);entry.update(complete=True,size=list(out.size),source_size=list(photo.size),native_size_matches=out.size==photo.size)
 td=O/f'{shot}_tiles';m=json.loads((td/'manifest.json').read_text());entry['rendered_tiles']=sum(not t.get('blank') for t in m['tiles']);entry['blank_tiles']=sum(bool(t.get('blank')) for t in m['tiles'])
 pair_checks=[]
 for i,t in enumerate(m['tiles']):
  if t.get('blank'):continue
  for q in m['tiles'][i+1:]:
   if q.get('blank'):continue
   # Compare only immediate horizontal/vertical neighbours.
   tc,qc=t['core'],q['core']
   if not ((tc[1]==qc[1] and tc[2]==qc[0]) or (tc[0]==qc[0] and tc[3]==qc[1])):continue
   a,b,aa,bb=t['padded'];d,e,dd,ee=q['padded'];x0=max(a,d);y0=max(b,e);x1=min(aa,dd);y1=min(bb,ee)
   if x1<=x0 or y1<=y0:continue
   A=cv2.imread(str(td/t['file']),-1);B=cv2.imread(str(td/q['file']),-1)
   A=A[y0-b:y1-b,x0-a:x1-a].astype('float32')/65535;B=B[y0-e:y1-e,x0-d:x1-d].astype('float32')/65535
   hh=min(A.shape[0],B.shape[0]);ww=min(A.shape[1],B.shape[1]);A=A[:hh,:ww];B=B[:hh,:ww]
   keep=np.maximum(A[:,:,3],B[:,:,3])>.02
   if not np.any(keep):continue
   err=np.abs(A[:,:,:3]*A[:,:,3:4]-B[:,:,:3]*B[:,:,3:4])[keep]*255
   pair_checks.append({'tiles':[t['file'],q['file']],'mean_premultiplied_srgb_difference_8bit':float(err.mean()),'p95_difference_8bit':float(np.percentile(err,95))})
 entry['overlap_checks']=pair_checks
 exrs=list(td.glob('*passes*.exr'))
 if exrs:
  h=OpenEXR.File(str(exrs[0]),header_only=True).header();names=[v.name for v in h['channels']]
  entry['example_linear_pass_file']=exrs[0].name;entry['pass_channels']=names
 entry['sha256_jpeg']=hashlib.sha256(file.read_bytes()).hexdigest();report.append(entry)
(O/'delivery_QA.json').write_text(json.dumps(report,indent=2),encoding='utf8')
done=[r for r in report if r['complete']]
if done:
 width=2200;cellw=1040;gap=40;rows=[]
 for r in done:
  shot=r['shot'];a=Image.open(R/f'images/photos/{shot}.jpg').convert('RGB');b=Image.open(O/f'{shot}_full_composite.jpg').convert('RGB')
  h=round(a.height*cellw/a.width);row=Image.new('RGB',(width,h+85),'#f4f2ef');dr=ImageDraw.Draw(row);dr.text((40,20),shot+'  |  ORIGINAL / COMPOSITE',fill='#242422')
  row.paste(a.resize((cellw,h),Image.Resampling.LANCZOS),(40,65));row.paste(b.resize((cellw,h),Image.Resampling.LANCZOS),(1120,65));rows.append(row)
 sheet=Image.new('RGB',(width,sum(r.height for r in rows)+gap*(len(rows)-1)),'#f4f2ef');y=0
 for row in rows:sheet.paste(row,(0,y));y+=row.height+gap
 sheet.save(O/'before_after.jpg',quality=93)
print(json.dumps([{'shot':r['shot'],'complete':r['complete'],'size':r.get('size'),'overlap_mean_max':max([q['mean_premultiplied_srgb_difference_8bit'] for q in r.get('overlap_checks',[])],default=None)} for r in report],indent=2))
