"""Z4 Ernest finish (user: 'darker, slightly stronger grain'): Z2 recipe with a darker, more
neutral base and stronger grain. Trials K(Z2)/M/N/O/P at native crops of p09 and n04 (/work/trial)."""
import ernest_wood_Z2 as ew
P=dict(ew.P);P.update(base_scale=0.65,grain_contrast=3.2,bump=.09);BASE=(0.0125,0.0095,0.0078)
def build():
    ew.P.update(P);ew.BASE=BASE;ma=ew.build();ma.name='Ernest_dark_wood_grain_Z4';return ma
