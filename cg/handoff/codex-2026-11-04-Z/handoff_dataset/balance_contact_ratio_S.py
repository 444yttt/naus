from pathlib import Path
import OpenEXR,numpy as np
R=Path(__file__).resolve().parent;O=R/'out/photo_composite_S'
def load(stage):return OpenEXR.File(str(O/f'p13_balance_contact_{stage}_passes0001.exr')).channels()['Shadow Catcher'].pixels[:,:,:3].astype('float32')[:,:,::-1]
a=load('with');b=load('bare');ratio=np.divide(a,b,out=np.ones_like(a),where=b>=.05);ratio=np.clip(np.nan_to_num(ratio,nan=1),0,4)
np.save(O/'p13_balance_contact_ratio.npy',ratio);print('CONTACT_RATIO_SAVED',ratio.shape)
