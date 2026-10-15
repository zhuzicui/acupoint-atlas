"""Detail views: ear, hand (back/palm), foot (top/sole/inner/outer). All viewBox 0 0 400 480."""
import numpy as np, io, base64, json
from PIL import Image
from parse import subpaths, bbox
from figlib import select, path_d, line_mask, silhouette, make_T, S
from skel import skeleton_path
W,H=400,480
def fit_T(sps, pad=24, mirror=False, box=None):
    if box is None:
        lo=np.min([bbox(s)[0] for s in sps],0); hi=np.max([bbox(s)[1] for s in sps],0)
    else: lo,hi=np.array(box[0],float),np.array(box[1],float)
    sw,sh=hi-lo; s=min((W-2*pad)/sw,(H-2*pad)/sh)
    cx,cy=(lo+hi)/2
    if mirror: return lambda x,y:(200-(x-cx)*s, 240+(y-cy)*s)
    return lambda x,y:(200+(x-cx)*s, 240+(y-cy)*s)
EAR=subpaths(S+'ear.svg',dark_only=True); FOOT=subpaths(S+'foot.svg',dark_only=True)
FOOT=[s for s in FOOT if not (bbox(s)[0][0]<1 and bbox(s)[1][0]>5900)]  # drop page rect
def dedupe(sps):
    seen=set(); out=[]
    for s in sps:
        key=repr(s)
        if key in seen: continue
        seen.add(key); out.append(s)
    return out
EAR=dedupe(EAR); FOOT=dedupe(FOOT)
HAND=dedupe(subpaths(S+'handnew.svg',keep_fill='38.998413%'))
VIEWS={
 'hand_back':('fill', select(HAND,420,2600,450,3250), {}),
 'hand_palm':('fill', select(HAND,2900,5100,450,3250), {}),
 'ear':      ('fill', select(EAR,380,1440,630,2360), {}),
 'foot_top': ('fill', select(FOOT,775,1390,200,1715), {}),
 'foot_sole':('fill', select(FOOT,2640,3270,220,1740), {}),
 'foot_in':  ('fill', select(FOOT,3965,5550,340,1400), {}),
 'foot_out': ('fill', select(FOOT,430,1900,2025,3070), {}),
}
def vector_asset(name):
    mode,sps,opt=VIEWS[name]; T=fit_T(sps,**opt)
    d=path_d(sps,T); return {'d':d,'mode':'fill','sil':None,'h':H}, sps, T
def hand_assets():
    im=Image.open(S+'handhi-1.png').convert('RGBA'); a=np.array(im.convert('L'))
    out={}
    for name,(x0,x1) in {'hand_back':(0,im.width//2),'hand_palm':(im.width//2,im.width)}.items():
        sub=a[:,x0:x1]; ys,xs=np.where(sub<245); lo=(xs.min()+x0,ys.min()); hi=(xs.max()+x0,ys.max())
        crop=im.crop((lo[0]-10,lo[1]-10,hi[0]+10,hi[1]+10))
        # fit into 400x480 with pad 24
        sw,sh=crop.size; s=min((W-48)/sw,(H-48)/sh); nw,nh=int(sw*s),int(sh*s)
        crop=crop.resize((nw,nh),Image.LANCZOS)
        # make white transparent-ish: convert near-white to alpha
        arr=np.array(crop).astype(int); lum=arr[:,:,:3].mean(2); alpha=np.clip((248-lum)*12,0,255).astype(np.uint8)
        arr[:,:,3]=np.minimum(arr[:,:,3],alpha); crop=Image.fromarray(arr.astype(np.uint8))
        canvas=Image.new('RGBA',(W,H),(0,0,0,0)); ox,oy=(W-nw)//2,(H-nh)//2; canvas.paste(crop,(ox,oy))
        b=io.BytesIO(); canvas.save(b,'WEBP',quality=82);
        out[name]={'img':base64.b64encode(b.getvalue()).decode(),'mode':'image','h':H,'d':'','sil':None}
        # transform from hi-res png pixel coords to view coords for reference
        out[name+'_T']=(lo[0]-10,lo[1]-10,s,ox,oy)
    return out
if __name__=='__main__':
    A={}
    for n in VIEWS: A[n]=vector_asset(n)[0]; print(n,len(A[n]['d']))
    json.dump(A,open('assets_detail.json','w'))
