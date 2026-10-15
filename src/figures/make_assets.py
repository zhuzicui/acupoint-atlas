import json, numpy as np
from views import body_view, head_view
from figlib import path_d, png_b64
from skel import skeleton_path
from scipy import ndimage
A={}
for sex in 'fm':
    for v in ('front','back','side','face','headside','headback'):
        body=v in ('front','back','side')
        sps,T=body_view(sex,v) if body else head_view(sex,v)
        W,H=400,(1000 if body else 480)
        if sex=='f' and v!='headback': d=path_d(sps,T); mode='fill'
        else: d,_=skeleton_path(sps,T,W,H); mode='stroke'
        sil=None
        if body:
            m=np.load(f'{sex}_{v}_sil.npy')
            m=ndimage.binary_erosion(m,iterations=2)
            sil=png_b64(m)
        A[f'{sex}_{v}']={'d':d,'mode':mode,'sil':sil,'h':H}
        print(sex,v,mode,len(d),len(sil or ''))
json.dump(A,open('assets.json','w'))
