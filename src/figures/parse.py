import re, numpy as np, json, sys
def subpaths(svgfile, dark_only=False, keep_fill=None):
    s=open(svgfile).read()
    out=[]
    for m in re.finditer(r'<path [^>]*?fill="([^"]+)"[^>]*? d="([^"]+)"',s):
        fill,d=m.groups()
        if 'clip-rule' in m.group(0): continue
        if keep_fill is not None and keep_fill not in fill: continue
        if dark_only:
            nums=[float(x) for x in re.findall(r'[\d.]+',fill)]
            if nums and sum(nums)/len(nums)>50: continue
        toks=re.findall(r'[MLCZ]|-?[\d.]+',d)
        cur=[];i=0;cmd=None
        while i<len(toks):
            t=toks[i]
            if t in 'MLCZ':
                cmd=t;i+=1
                if t=='M':
                    if cur: out.append(cur)
                    cur=[('M',[float(toks[i]),float(toks[i+1])])];i+=2
                elif t=='Z': cur.append(('Z',[]))
                continue
            n={'L':2,'C':6}[cmd]
            cur.append((cmd,[float(x) for x in toks[i:i+n]]));i+=n
        if cur: out.append(cur)
    return out
def bbox(sp):
    pts=np.array([v for c,a in sp for v in zip(a[0::2],a[1::2])]) if sp else None
    return pts.min(0),pts.max(0)
if __name__=='__main__':
    for f in sys.argv[1:]:
        sps=subpaths(f); bbs=[bbox(s) for s in sps]
        xs=sorted((b[0][0],b[1][0]) for b in bbs)
        # cluster by x overlap
        groups=[]
        for a,b in xs:
            if groups and a<=groups[-1][1]+40: groups[-1][1]=max(groups[-1][1],b)
            else: groups.append([a,b])
        print(f,len(sps),'groups',[(round(a),round(b)) for a,b in groups])
        for g in groups:
            inside=[bb for bb in bbs if bb[0][0]>=g[0]-1 and bb[1][0]<=g[1]+1]
            lo=np.min([b[0] for b in inside],0); hi=np.max([b[1] for b in inside],0)
            print('  x',round(g[0]),round(g[1]),'y',round(lo[1]),round(hi[1]),'n',len(inside))
