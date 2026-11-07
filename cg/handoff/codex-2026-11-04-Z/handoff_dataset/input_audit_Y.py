from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parent;O=R/'out_Y';expected=json.loads((R/'out_X/input_sha256.json').read_text());rows=[]
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
for name,old in expected.items():
 p=Path(name)
 if not p.is_absolute():p=R.parent/p
 actual=sha(p);rows.append({'file':str(p),'expected_from_X':old,'actual':actual,'unchanged':actual==old})
for p in [*(R/'out_X').glob('*_photo_scene.blend'),R/'out_X/delivery/source/Harajuku_LDK_X.blend',R/'out_X/Harajuku_3LDK_review_X.zip']:
 rows.append({'file':str(p),'baseline_Y_sha256':sha(p),'status':'read-only X baseline recorded at start of Y'})
result={'inputs':rows,'W_originals_and_user_brief_unchanged':all(r.get('unchanged',True) for r in rows),'external_expected_hashes_provided':False};(O/'input_audit_Y.json').write_text(json.dumps(result,indent=2));assert result['W_originals_and_user_brief_unchanged'];print('INPUTS_UNCHANGED',len(rows))
