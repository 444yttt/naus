from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parent;O=R/'out_Z';baseline=json.loads((R/'out_Y/input_audit_Y.json').read_text());rows=[]
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()
for row in baseline['inputs']:
    p=Path(row['file']);expected=row.get('expected_from_X',row.get('baseline_Y_sha256'));actual=sha(p)
    rows.append({'file':str(p),'recorded_before_Z':expected,'actual':actual,'unchanged':actual==expected})
references=[]
for name,url in [('Shindo_Natural_official_reference.jpg','https://s3.poliform.it/2025/07/Poliform_tappeti_SHINDO_finiture_1300x1740px_natural.jpg'),('Shindo_official_dimensions.svg','https://s3.poliform.it/2025/07/Poliform_tappeti_SHINDO_rettangolare.svg')]:
    p=O/name;references.append({'file':str(p),'sha256':sha(p),'source':url,'use':'unmodified official reference; not an official 3D mesh or measured PBR scan'})
result={'inputs':rows,'originals_and_prior_deliveries_unchanged':all(r['unchanged'] for r in rows),'additional_references':references,'external_expected_hashes_provided':False}
(O/'input_audit_Z.json').write_text(json.dumps(result,indent=2));assert result['originals_and_prior_deliveries_unchanged'];print('Z_INPUTS_VERIFIED',len(rows),len(references))
