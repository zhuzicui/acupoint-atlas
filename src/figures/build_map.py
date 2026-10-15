import sys, json, numpy as np
sys.path.insert(0,'/home/claude/acu')
import mapdata as MD
from tps import TPS, pairs
import landmarks_old as LO, landmarks_new as LN
from scipy import ndimage
OLD={'front':LO.FB,'back':LO.FB,'side':LO.SIDE,'face':LO.FACE,'headside':LO.HSIDE,'headback':LO.HBACK}
NEW={('f','front'):LN.F_FB,('f','back'):LN.F_FB,('f','side'):LN.F_SIDE,('m','front'):LN.M_FB,('m','back'):LN.M_FB,('m','side'):LN.M_SIDE,
     ('f','face'):LN.F_FACE,('m','face'):LN.M_FACE,('f','headside'):LN.F_HSIDE,('m','headside'):LN.M_HSIDE,('f','headback'):LN.F_HBACK,('m','headback'):LN.M_HBACK}
MIRV={'front','back','face','headback'}
ARMPTS={'front':[f'LU{i}' for i in range(3,12)]+[f'PC{i}' for i in range(2,10)]+[f'HT{i}' for i in range(2,10)],
        'side':[f'LI{i}' for i in range(1,16)]+[f'TE{i}' for i in range(1,15)]+[f'SI{i}' for i in range(1,9)]}
def arm_map(p, old, new):
    (A,ha),(B,hb)=old,new; A=np.array(A,float); B=np.array(B,float); p=np.array(p,float)
    best=None
    for i in range(len(A)-1):
        a,b=A[i],A[i+1]; v=b-a; L=np.dot(v,v); u=np.clip(np.dot(p-a,v)/L,0,1)
        q=a+u*v; dist=np.linalg.norm(p-q)
        if best is None or dist<best[0]: best=(dist,i,u)
    _,i,u=best; a,b=A[i],A[i+1]; v=(b-a)/np.linalg.norm(b-a); n=np.array([v[1],-v[0]])
    u_raw=np.dot(p-a,b-a)/np.dot(b-a,b-a)
    d=np.dot(p-(a+u*(b-a)),n); hwo=ha[i]+(ha[i+1]-ha[i])*u
    c,e=B[i],B[i+1]; w=(e-c)/np.linalg.norm(e-c); m=np.array([w[1],-w[0]]); hwn=hb[i]+(hb[i+1]-hb[i])*u
    along=(u_raw-u)*np.linalg.norm(e-c)  # extrapolation beyond ends
    return tuple(c+u*(e-c)+w*along+m*d*hwn/hwo)
def old_placements():
    out={}
    for code,(v,x,y) in MD.P.items():
        pl=[(v,x,y)]+list(MD.EXTRA_SPOTS.get(code,[]))
        if v in MD.HEAD2BODY: pl+= [(MD.HEAD2BODY[a],*MD.to_body(b,c)) for a,b,c in list(pl)]
        out[code]=pl
    return out
def snap(sil,x,y,inset=2.0,k=2):
    H,W=sil.shape; xi,yi=int(round(x*k)),int(round(y*k))
    if 0<=xi<W and 0<=yi<H and sil[yi,xi]:
        # also keep a little away from edge
        return x,y
    dist,(iy,ix)=ndimage.distance_transform_edt(~sil,return_indices=True)
    xi=min(max(xi,0),W-1); yi=min(max(yi,0),H-1)
    nx,ny=ix[yi,xi]/k,iy[yi,xi]/k
    dx,dy=nx-x,ny-y; L=(dx*dx+dy*dy)**.5 or 1
    return nx+dx/L*inset, ny+dy/L*inset
OVR={('f','ST8','face'):(116,118),('m','ST8','face'):(114,120),('f','GB29','side'):(205,497),('m','GB29','side'):(215,537)}
def build():
    OP=old_placements(); res={'f':{},'m':{}}; moved={'f':[],'m':[]}
    for sex in 'fm':
        T={v:TPS(*pairs(OLD[v],NEW[(sex,v)],v in MIRV),lam=0.5) for v in OLD}
        SIL={v:np.load(f'{sex}_{v}_sil.npy') for v in ('front','back','side')}
        for code,pl in OP.items():
            new=[]
            for v,x,y in pl:
                if v in ARMPTS and code in ARMPTS[v]: nx,ny=arm_map((x,y),LN.ARM_OLD[v],LN.ARM_NEW[(sex,v)])
                else: nx,ny=T[v]([(x,y)])[0]
                if (sex,code,v) in OVR: nx,ny=OVR[(sex,code,v)]
                if v in SIL:
                    sx,sy=snap(SIL[v],nx,ny)
                    if abs(sx-nx)+abs(sy-ny)>0.5: moved[sex].append((code,v,round(abs(sx-nx)+abs(sy-ny),1)))
                    nx,ny=sx,sy
                new.append([v,round(float(nx),1),round(float(ny),1)])
            res[sex][code]=new
    return res,moved
if __name__=='__main__':
    res,moved=build()
    json.dump(res,open('newmap.json','w'))
    for s in 'fm': print(s,len(moved[s]),'snapped:',sorted(moved[s],key=lambda t:-t[2])[:25])
