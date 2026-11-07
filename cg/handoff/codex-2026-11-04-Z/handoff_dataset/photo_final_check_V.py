from pathlib import Path
import json,zipfile,hashlib
from PIL import Image
R=Path(__file__).resolve().parent;O=R/'out/photo_final_V';D=O/'delivery'
report=json.loads((D/'delivery_QA.json').read_text(encoding='utf8'))
assert len(report)==5
with zipfile.ZipFile(O/'Harajuku_3LDK_delivery_V.zip') as z:
    assert z.testzip() is None
    assert z.read('00_overview.jpg')==(D/'00_overview.jpg').read_bytes()
    assert len([n for n in z.namelist() if n.startswith('verification/') and n.endswith('.jpg')])==5
    for i,row in enumerate(report,1):
        shot=row['shot'];name=f'{i:02d}_{shot}'
        assert hashlib.sha256((D/f'{name}.jpg').read_bytes()).hexdigest()==row['jpeg_sha256']
        for ext in ['jpg','png']:
            p=D/f'{name}.{ext}';im=Image.open(p)
            assert im.size==tuple(row['native_size'])==Image.open(R/f'images/photos/{shot}.jpg').size
            assert im.info.get('icc_profile')
            assert z.read(p.name)==p.read_bytes()
        assert row['untouched_source_max_error_8bit']<=2
    count=len(z.namelist())
scenes=json.loads((D/'scene_delivery_QA.json').read_text())
assert len({r['shared_geometry_transform_sha256'] for r in scenes})==1
print('FINAL_VERIFIED: 5 native JPEG+PNG pairs, 5 verification views, common layout, ICC profiles, ZIP CRC')
print('ZIP',round((O/'Harajuku_3LDK_delivery_V.zip').stat().st_size/1e6,1),'MB',count,'files')
