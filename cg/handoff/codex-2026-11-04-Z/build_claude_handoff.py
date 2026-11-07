"""Create a documented, checksummed restart package without changing source assets."""
from pathlib import Path
import json, hashlib, zipfile, datetime, shutil

ROOT=Path(__file__).resolve().parent
DATA=ROOT/'handoff_dataset'
brief=Path('C:/Users/akaay/.codex/codex-remote-attachments/01a19f51-138e-7622-817c-433434a14e62/96AFA953-CDC5-47A3-B636-A8F618220590/1-INTENT_3D_BRIEF.md')
if brief.exists():shutil.copy2(brief,DATA/'instructions_X/ORIGINAL_INTENT_3D_BRIEF.md')

def selected(p):
    rel=p.relative_to(DATA); parts=rel.parts; name=p.name
    if '__pycache__' in parts or p.suffix in ['.pyc','.blend1','.blend2']:return False
    if parts[0]=='runtime':return False
    if len(parts)==1:return True
    if parts[0] in ['models','images','calib','code','reference','instructions_X']:return True
    if parts[0]=='out_Z':
        # Full current native pass tree, but not discarded trial render payloads.
        if any(x in parts for x in ['light_trials','initial_candidate']):
            return p.suffix.lower() in ['.json','.md','.txt','.log']
        if 'initial' in name and p.suffix.lower() in ['.blend','.exr','.png','.jpg']:return False
        if 'preview' in name and p.suffix.lower() in ['.exr','.png','.jpg']:return False
        return True
    if parts[0]=='out_X':
        if p.suffix.lower() in ['.json','.md','.txt','.log','.diff','.py']:return True
        if len(parts)==2 and (name.endswith('_photo_scene.blend') or p.suffix.lower() in ['.png','.jpg']):return True
        if len(parts)>2 and parts[1]=='delivery':return p.suffix.lower() not in ['.zip','.exr','.blend']
        return False
    if parts[0]=='out_Y':
        if p.suffix.lower() in ['.json','.md','.txt','.log','.diff','.py']:return True
        if len(parts)>2 and parts[1] in ['shadow_audit','shadow_audit_final']:return True
        return False
    if parts[0]=='out':
        if len(parts)>1 and parts[1]=='photo_final_W':
            if len(parts)>2 and parts[2]=='delivery':return p.suffix.lower() not in ['.zip','.exr']
            if len(parts)==3 and name.endswith('_photo_scene.blend'):return True
            if len(parts)==3 and (name.endswith('_full_composite.png') or name.endswith('_full_reflection_coverage.png') or name.endswith('_full_alpha.png')):return True
        # Retain historical specifications, provenance and numerical records.
        return p.suffix.lower() in ['.json','.md','.txt','.log','.diff','.py']
    return False

files=[]; omitted=[]
for p in sorted(DATA.rglob('*')):
    if not p.is_file():continue
    if selected(p):files.append(p)
    else:omitted.append({'path':p.relative_to(ROOT).as_posix(),'bytes':p.stat().st_size})
files += [ROOT/'CLAUDE_HANDOFF.md',ROOT/'CLAUDE_START_HERE.md',Path(__file__).resolve()]
manifest={'created_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'purpose':'Work in progress, full handoff to Claude; not completed final delivery',
 'source_workspace':str(ROOT),'completed_native':['p09','u1','u2'],'verified_native':['p09','u1'],'unreviewed_native':['u2'],'unfinished_native':['p01','p13'],
 'portable_scope':'Current Z scenes and native passes, assets/photos, scripts, W/X baseline scenes and selected comparisons/QA. Runtime and most old trial payloads excluded; full disk history remains in source_workspace.',
 'runtime_required':'Blender 4.5.9 LTS; Python with numpy, scipy, opencv-python, Pillow, OpenEXR. Local runtime is not in ZIP.',
 'files':[],'omitted_files':omitted}
for i,p in enumerate(files):
    digest=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(4*1024*1024),b''):digest.update(b)
    manifest['files'].append({'path':p.relative_to(ROOT).as_posix(),'bytes':p.stat().st_size,'sha256':digest.hexdigest()})
manifest['included_bytes']=sum(v['bytes'] for v in manifest['files'])
mp=ROOT/'CLAUDE_PACKAGE_MANIFEST.json'
mp.write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf8')
files.append(mp)
print('SELECTED',len(files),'BYTES',manifest['included_bytes'],flush=True)
project=ROOT/'Claude_handoff_project.zip'
with zipfile.ZipFile(project,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=3,allowZip64=True) as z:
    for i,p in enumerate(files):
        z.write(p,p.relative_to(ROOT).as_posix())
        if i%200==0:print('PACKED',i,len(files),flush=True)
docs=ROOT/'Claude_handoff_documents.zip'
with zipfile.ZipFile(docs,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for p in [ROOT/'CLAUDE_HANDOFF.md',ROOT/'CLAUDE_START_HERE.md',mp]:z.write(p,p.name)
    for p in sorted((DATA/'instructions_X').glob('*.md')):z.write(p,'instructions_X/'+p.name)
print('VERIFYING_ZIP_CRC',flush=True)
for p in [project,docs]:
    with zipfile.ZipFile(p) as z:
        assert z.testzip() is None
        count=len(z.infolist())
    digest=hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
    print('VERIFIED',p.name,p.stat().st_size,count,digest,flush=True)
    (ROOT/(p.name+'.sha256')).write_text(digest+'  '+p.name+'\n',encoding='ascii')
print('HANDOFF_ARCHIVES_READY',flush=True)
