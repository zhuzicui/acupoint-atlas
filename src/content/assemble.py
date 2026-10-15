import json, benefits as B
from loc_a import LOC_A; from loc_b import LOC_B; from loc_c import LOC_C; from loc_d import LOC_D
loc={}
for blk in (LOC_A,LOC_B,LOC_C,LOC_D):
  for ln in blk.strip().split('\n'):
    c,a,p=ln.split('|'); loc[c]={'anatomical':a.strip(),'plain':p.strip()}
ind,act,pm=B.load()
out={'sources':B.SOURCES,'points':{i:{'location':loc[i],**B.benefits_for(i,ind,act,pm)} for i in loc}}
json.dump(out,open('content.json','w'),ensure_ascii=False,indent=1)
print(len(out['points']))
