import bpy,json,numpy as np
def hull(P):
    P=sorted(set(map(tuple,P)))
    if len(P)<3:return P
    def cr(o,a,b):return (a[0]-o[0])*(b[1]-o[1])-(a[1]-o[1])*(b[0]-o[0])
    lo=[];up=[]
    for p in P:
        while len(lo)>=2 and cr(lo[-2],lo[-1],p)<=0:lo.pop()
        lo.append(p)
    for p in reversed(P):
        while len(up)>=2 and cr(up[-2],up[-1],p)<=0:up.pop()
        up.append(p)
    return lo[:-1]+up[:-1]
S=bpy.context.scene;dg=bpy.context.evaluated_depsgraph_get()
def root(o):
    while o.parent:o=o.parent
    return o
G={
 'Linha Dining（Minotti）':lambda o,r:r.name.startswith('Linha_Dining'),
 'Torii チェア（Minotti）':lambda o,r:r.name.startswith('Torii_USER_MODEL'),
 'Ernest ソファ（Poliform）':lambda o,r:o.name.startswith(('Ernest_DEALER_FBX_module','Ernest_rear_table','Rear_table_support')),
 'Ernest テーブル（Poliform）':lambda o,r:o.name.startswith('Ernest_DEALER_FBX_table'),
 'Eames Lounge Chair（Herman Miller）':lambda o,r:o.name.startswith('SEAT-'),
 'IVRESSE（Roche Bobois）':lambda o,r:o.name.startswith('IVRESSE'),
 'Beolab 28（Bang & Olufsen）':lambda o,r:'olab' in o.name.lower() or r.name.startswith('Beolab'),
 'TV 97型クラス':lambda o,r:o.name.lower().startswith(('tv_screen','tv_panel','tv_97','tv_body')) or (o.name.startswith('TV') and 'wall' not in o.name.lower() and 'tile' not in o.name.lower()),
 'Shindo ラグ（Poliform）':lambda o,r:o.name.startswith('Shindo'),
 '植物':lambda o,r:o.name.startswith('Plant_Z5'),
 'ランプ（Panthella型）':lambda o,r:o.name.startswith('Dining_lamp_Z5'),
}
out={}
for o in S.objects:
    if o.type!='MESH' or o.hide_render:continue
    r=root(o);key=next((k for k,f in G.items() if f(o,r)),None)
    if not key:continue
    if key=='Torii チェア（Minotti）' or key=='植物' or key=='ランプ（Panthella型）':sub=r.name if key.startswith('Torii') else o.name.split('_')[2] if key=='植物' else o.name.split('_')[3]
    elif key.startswith(('Ernest','Beolab','Eames')):sub=r.name if key.startswith('Beolab') else o.name
    else:sub='all'
    ev=o.evaluated_get(dg);me=ev.to_mesh();M=o.matrix_world
    co=np.array([(M@v.co)[:] for v in me.vertices]);ev.to_mesh_clear()
    if len(co)==0:continue
    if len(co)>4000:co=co[np.random.default_rng(0).choice(len(co),4000,replace=False)]
    out.setdefault(key,{}).setdefault(sub,[]).append(co[:,:2])
res={}
for k,v in out.items():
    res[k]=[]
    for sub,arrs in v.items():
        p=np.vstack(arrs)
        if len(p)<3:continue
        res[k].append([[round(a,4),round(b,4)] for a,b in hull(p.round(4).tolist())])
json.dump(res,open('/work/plan/footprints.json','w'),ensure_ascii=False)
print('FP',{k:len(v) for k,v in res.items()})
print('NAMES_TV',[o.name for o in S.objects if o.name.upper().startswith('TV')][:20])
