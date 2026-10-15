import numpy as np, cv2, json
S='/tmp/claude-0/-home-claude/0064597b-9ab7-5400-ab73-6534a8e3bd63/scratchpad/'
sil=cv2.imread(S+'palm_sil.png',0)
ys,xs=np.where(sil>0); lo=np.array([xs.min()-25,ys.min()-25]); hi=np.array([xs.max()+25,ys.max()+25])
sw,sh=hi-lo; s=min(352/sw,432/sh); ox,oy=(400-sw*s)/2,(480-sh*s)/2
T=lambda x,y:((x-lo[0])*s+ox,(y-lo[1])*s+oy); inv=lambda X,Y:((X-ox)/s+lo[0],(Y-oy)/s+lo[1])
YC=468; ycut=int(inv(0,YC)[1])
if ycut+2>sil.shape[0]: sil=np.vstack([sil,np.zeros((ycut+2-sil.shape[0],sil.shape[1]),np.uint8)])
sil[ycut:,:]=0
# keep the wrist straight: below view y=380 clamp each row to the span measured at y=380
ry0=int(inv(0,372)[1]); ry1=int(inv(0,412)[1]); best=None
for ry in range(ry0,ry1):
    r=np.where(sil[ry]>0)[0]
    if len(r) and (best is None or r.max()-r.min()<best[0]): best=(r.max()-r.min(),r.min(),r.max())
xa,xb=best[1]+6,best[2]-6
r=np.where(sil[ry0]>0)[0]; ha,hb=r.min(),r.max()
for ry in range(ry0,ycut):
    t=min(1.0,(ry-ry0)/max(1,(ry1-ry0))); t=t*t*(3-2*t)
    la=int(ha+(xa-ha)*t); lb=int(hb+(xb-hb)*t)
    sil[ry,:]=0; sil[ry,la:lb+1]=255
sil=cv2.morphologyEx(sil,cv2.MORPH_OPEN,np.ones((9,9),np.uint8))
cs,_=cv2.findContours(sil,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE); c=max(cs,key=cv2.contourArea)
c=cv2.approxPolyDP(c,2.0,True)[:,0,:].astype(float); pts=[T(*p) for p in c]
def smooth(pts):
    n=len(pts); P=lambda i:pts[i%n]; d=f"M{pts[0][0]:.1f},{pts[0][1]:.1f}"
    for i in range(n):
        p0,p1,p2,p3=P(i-1),P(i),P(i+1),P(i+2)
        if abs(p1[1]-YC)<3 or abs(p2[1]-YC)<3: d+=f"L{p2[0]:.1f},{p2[1]:.1f}"; continue
        c1=(p1[0]+(p2[0]-p0[0])/6,p1[1]+(p2[1]-p0[1])/6); c2=(p2[0]-(p3[0]-p1[0])/6,p2[1]-(p3[1]-p1[1])/6)
        d+=f"C{c1[0]:.1f},{c1[1]:.1f} {c2[0]:.1f},{c2[1]:.1f} {p2[0]:.1f},{p2[1]:.1f}"
    return d+"Z"
outline=smooth(pts)
top=np.full(400,np.nan)
for X in range(400):
    x=int(inv(X,0)[0]); col=np.where(sil[:,x]>0)[0] if 0<=x<sil.shape[1] else []
    if len(col): top[X]=T(0,col.min())[1]
def rowspan(y,xl,xr):
    ry=int(inv(0,y)[1]); a0=max(0,int(inv(xl,0)[0])); a1=min(sil.shape[1],int(inv(xr,0)[0])); row=np.where(sil[ry,a0:a1]>0)[0]
    return (T(row.min()+a0,0)[0],T(row.max()+a0,0)[0]) if len(row) else None
FING=[(62,100),(110,154),(156,200),(202,252)]
creases=[]
for i,(xl,xr) in enumerate(FING):
    seg=top[xl:xr]; ty=np.nanmin(seg)
    wl=np.nanmax(top[xl-4:xl+6]) if i>0 else np.nan; wr=np.nanmax(top[xr-6:xr+4]) if i<3 else np.nan
    wy=np.nanmax([wl,wr]); L=wy-ty
    for f in (0.30,0.62):
        y=ty+f*L; sp=rowspan(y,xl,xr)
        if sp: a,b=sp[0]+2,sp[1]-2; creases.append(f"M{a:.1f},{y:.1f} Q{(a+b)/2:.1f},{y+4:.1f} {b:.1f},{y:.1f}")
    y=wy+0.1*L; sp=rowspan(y,xl-10,xr+10)
    if sp:
        a,b=max(sp[0],xl-8)+3,min(sp[1],xr+8)-3; creases.append(f"M{a:.1f},{y:.1f} Q{(a+b)/2:.1f},{y-6:.1f} {b:.1f},{y:.1f}")
creases+=["M296,228 Q306,240 312,254","M104,268 C140,255 185,240 218,247","M106,296 C140,286 190,272 245,268","M252,250 C237,300 212,345 202,395","M118,322 C130,352 150,376 170,392","M124,390 Q183,400 241,390","M127,404 Q183,414 239,404"]
cre="".join(creases)
svg=f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 480" width="800" height="960">
<path d="{outline}" fill="#ECE5DA" stroke="#3B3631" stroke-width="2.2" stroke-linejoin="round"/>
<path d="{cre}" fill="none" stroke="#3B3631" stroke-width="1.4" stroke-linecap="round"/>
</svg>'''
open('hand_palm_lineart.svg','w').write(svg); json.dump({'outline':outline,'creases':cre},open('palm_paths.json','w'))
