import numpy as np
def U(r2): 
    with np.errstate(divide='ignore',invalid='ignore'): v=r2*np.log(r2)
    return np.nan_to_num(v)
class TPS:
    def __init__(s,src,dst,lam=1.0):
        src=np.asarray(src,float); dst=np.asarray(dst,float); n=len(src)
        K=U(((src[:,None]-src[None])**2).sum(-1))+lam*np.eye(n)
        P=np.c_[np.ones(n),src]; A=np.zeros((n+3,n+3)); A[:n,:n]=K; A[:n,n:]=P; A[n:,:n]=P.T
        b=np.zeros((n+3,2)); b[:n]=dst; s.w=np.linalg.solve(A,b); s.src=src
    def __call__(s,pts):
        pts=np.atleast_2d(np.asarray(pts,float))
        K=U(((pts[:,None]-s.src[None])**2).sum(-1)); P=np.c_[np.ones(len(pts)),pts]
        return K@s.w[:len(s.src)]+P@s.w[len(s.src):]
def pairs(old,new,mirror):
    S,D=[],[]
    for k in old:
        if k not in new: continue
        S.append(old[k]); D.append(new[k])
        if mirror and abs(old[k][0]-200)>0.5:
            S.append((400-old[k][0],old[k][1])); D.append((400-new[k][0],new[k][1]))
    return S,D
