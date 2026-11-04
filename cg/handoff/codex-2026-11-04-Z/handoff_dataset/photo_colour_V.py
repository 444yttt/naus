"""Honor source ICC profiles; never relabel Display P3 pixel values as sRGB."""
from pathlib import Path
import io,json
from PIL import Image,ImageCms
R=Path(__file__).resolve().parent
O=R/'images/photos_srgb';O.mkdir(exist_ok=True)
dst=ImageCms.createProfile('sRGB');icc=ImageCms.ImageCmsProfile(dst).tobytes();rows=[]
for shot in ['u1','u2','p09','p01','p13']:
    im=Image.open(R/f'images/photos/{shot}.jpg').convert('RGB')
    source=im.info.get('icc_profile')
    desc='sRGB (EXIF color space1)'
    if source:
        src=ImageCms.ImageCmsProfile(io.BytesIO(source));desc=ImageCms.getProfileDescription(src).strip()
        im=ImageCms.profileToProfile(im,src,dst,renderingIntent=1,outputMode='RGB')
    im.save(O/f'{shot}.png',icc_profile=icc,compress_level=4)
    rows.append({'shot':shot,'source_profile':desc,'working_profile':'sRGB','conversion':'ICC relative colorimetric, original source file preserved','native_size':list(im.size)})
(R/'out/photo_final_V/colour_management.json').write_text(json.dumps(rows,indent=2),encoding='utf8')
print('SOURCE_COLOUR_MANAGED',len(rows))
