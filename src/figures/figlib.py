import numpy as np, io, base64
from PIL import Image, ImageDraw
from parse import subpaths, bbox
S='/tmp/claude-0/-home-claude/0064597b-9ab7-5400-ab73-6534a8e3bd63/scratchpad/'
def flatten(sp, T, steps=10):
    polys=[];cur=[]
    for c,a in sp:
        if c=='M':
            if len(cur)>2: polys.append(cur)
            cur=[T(a[0],a[1])]
        elif c=='L': cur.append(T(a[0],a[1]))
        elif c=='C':
            p0=np.array(cur[-1]); p1=np.array(T(a[0],a[1])); p2=np.array(T(a[2],a[3])); p3=np.array(T(a[4],a[5]))
            for t in np.linspace(0,1,steps+1)[1:]:
                cur.append(tuple((1-t)**3*p0+3*(1-t)**2*t*p1+3*(1-t)*t**2*p2+t**3*p3))
    if len(cur)>2: polys.append(cur)
    return polys
def select(sps, x0,x1,y0,y1):
    out=[]
    for s in sps:
        lo,hi=bbox(s)
        if lo[0]>=x0-1 and hi[0]<=x1+1 and lo[1]>=y0-1 and hi[1]<=y1+1: out.append(s)
    return out
def make_T(src_x, src_y, s, dst_x, dst_y):
    return lambda x,y:((x-src_x)*s+dst_x,(y-src_y)*s+dst_y)
def path_d(sps,T):
    parts=[]
    for sp in sps:
        for c,a in sp:
            if c=='Z': parts.append('Z'); continue
            pts=[T(a[i],a[i+1]) for i in range(0,len(a),2)]
            parts.append(c+' '.join(f'{x:.1f},{y:.1f}' for x,y in pts))
    return ''.join(parts)
def line_mask(sps,T,W,H,k=2):
    m=np.zeros((H*k,W*k),bool)
    for sp in sps:
        for poly in flatten(sp,T):
            im=Image.new('1',(W*k,H*k),0); ImageDraw.Draw(im).polygon([(x*k,y*k) for x,y in poly],fill=1)
            m^=np.array(im)
    return m
def silhouette(lm, seal=None):
    from scipy import ndimage
    L=ndimage.binary_dilation(lm,iterations=3)
    if seal is not None: L|=seal
    ext=~L; lab,n=ndimage.label(ext)
    border=set(lab[0,:])|set(lab[-1,:])|set(lab[:,0])|set(lab[:,-1]); border.discard(0)
    outside=np.isin(lab,list(border))
    return ~outside
def png_b64(mask):
    im=Image.fromarray((mask*255).astype(np.uint8)).convert('L')
    b=io.BytesIO(); im.save(b,'PNG',optimize=True); return base64.b64encode(b.getvalue()).decode()
def grid_render(lm, sil, W, H, k, path, step=50, pts=None):
    rgb=np.full(lm.shape+(3,),255,np.uint8); rgb[sil]=(235,225,210); rgb[lm]=(0,0,0)
    im=Image.fromarray(rgb); d=ImageDraw.Draw(im)
    for g in range(0,max(W,H)+1,step):
        col=(255,120,120) if g%100==0 else (190,200,255)
        d.line([(g*k,0),(g*k,H*k)],fill=col); d.line([(0,g*k),(W*k,g*k)],fill=col)
        if g%100==0: d.text((g*k+2,2),str(g),fill=(200,0,0)); d.text((2,g*k+2),str(g),fill=(200,0,0))
    if pts:
        for x,y,c in pts: d.ellipse([x*k-3,y*k-3,x*k+3,y*k+3],fill=c)
    im.save(path)
