import numpy as np, cv2
from skimage.morphology import skeletonize
from figlib import line_mask
def skeleton_path(sps,T,W,H,k=4,eps=0.7):
    lm=line_mask(sps,T,W,H,k)
    sk=skeletonize(lm).astype(np.uint8)*255
    cs,_=cv2.findContours(sk,cv2.RETR_LIST,cv2.CHAIN_APPROX_NONE)
    parts=[]
    for c in cs:
        if len(c)<6: continue
        a=cv2.approxPolyDP(c,eps*k/2,False)[:,0,:]/k
        parts.append('M'+' '.join(f'{x:.1f},{y:.1f}' for x,y in a))
    return ''.join(parts), lm
