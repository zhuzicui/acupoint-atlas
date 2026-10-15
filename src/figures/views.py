from figlib import *
import numpy as np, json
W_=subpaths(S+'woman.svg'); M_=subpaths(S+'male.svg')
CROPS={('f','side'):(W_,288,728,0,3000), ('f','front'):(W_,1018,1784,0,3000), ('f','back'):(W_,2808,3579,0,3000),
 ('m','back'):(M_,-5,823,-10,1950), ('m','front'):(M_,1159,1984,-10,1950), ('m','side'):(M_,2597,2920,-10,1950)}
MIRROR={('m','side')}
def body_T(sps, mirror=False):
    lo=np.min([bbox(s)[0] for s in sps],0); hi=np.max([bbox(s)[1] for s in sps],0)
    s=940/(hi[1]-lo[1]); xc=(lo[0]+hi[0])/2
    if mirror: return (lambda x,y:(200-(x-xc)*s, 40+(y-lo[1])*s)), s
    return make_T(xc, lo[1], s, 200, 40), s
def body_view(sex, view):
    src,x0,x1,y0,y1=CROPS[(sex,view)]; sps=select(src,x0,x1,y0,y1); T,_=body_T(sps,(sex,view) in MIRROR); return sps,T
CHIN={'f':(43,170),'m':(44,177)}   # body-normalized vertex/chin y
def head_from_body(sex, view):
    sps,Tb=body_view(sex,view); v,c=CHIN[sex]; f=325/(c-v)
    return sps,(lambda x,y:(lambda bx,by:(200+(bx-200)*f, 40+(by-v)*f))(*Tb(x,y)))
def head_view(sex, hv):
    if sex=='f' and hv=='face':
        sps=select(W_,3805,4772,1450,3000); s=0.351; return sps, make_T(4286,1570,s,200,40)
    if sex=='f' and hv=='headside':
        sps=select(W_,3805,4772,0,1450); s=0.333; return sps,(lambda x,y:(322-(x-3838)*s, 40+(y-177)*s))
    return head_from_body(sex,{'face':'front','headside':'side','headback':'back'}[hv])
def masks(sps,T,W,H,seal_bottom=False):
    lm=line_mask(sps,T,W,H,2)
    seal=None
    if seal_bottom:
        seal=np.zeros_like(lm); seal[-3:,:]=True
    sil=silhouette(lm,seal)
    return lm,sil
if __name__=='__main__':
    for key in CROPS:
        sps,T=body_view(*key); lm,sil=masks(sps,T,400,1000)
        np.save(f'{key[0]}_{key[1]}_sil.npy',sil); np.save(f'{key[0]}_{key[1]}_lm.npy',lm)
    for sex in 'fm':
        for hv in ('face','headside','headback'):
            sps,T=head_view(sex,hv); lm,sil=masks(sps,T,400,480,True)
            np.save(f'{sex}_{hv}_sil.npy',sil); np.save(f'{sex}_{hv}_lm.npy',lm); print(sex,hv,len(sps))
