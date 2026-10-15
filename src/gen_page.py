import json
d=json.load(open('/mnt/user-data/outputs/acupoints.json',encoding='utf-8'))
mers=[{"code":m["code"],"en":m["name_en"],"zs":m["name_zh_s"]} for m in d["meridians"]]
pts=[[p["id"],p["meridian"],p["number"] if p["number"]!="" else 0,p["pinyin"],p["pinyin_plain"],p["name_zh_s"],p["name_zh_t"],p["area"],
      int(p["who_2008"]),int(p["acupressure_suitable"]),int(p["pregnancy_caution"]),p["safety_note"],p["notes"],int(p["bilateral"]),
      [[q["view"],q["x"],q["y"]] for q in p["map"]["female"]],[[q["view"],q["x"],q["y"]] for q in p["map"]["male"]],p["location_plain"],p["location_anatomical"],{"t":[[t["term"],t["plain"],t["source"]] for t in p["benefits"]["traditional"]],"a":p["benefits"]["tcm_actions"],"s":[[s["condition"],s["plain"],s["pmids"]] for s in p["benefits"]["studies"]],"r":[[r["claim"],r["cite"],r["url"],r["strength"]] for r in p["benefits"]["reviews"]]},p.get("name_en","")] for p in d["points"]]
data=json.dumps({"meridians":mers,"points":pts},ensure_ascii=False,separators=(",",":"))
t=open('page_template.html',encoding='utf-8').read().replace("/*DATA*/",data).replace("/*ASSETS*/",json.dumps({**json.load(open("/home/claude/fig/assets.json")),**json.load(open("/home/claude/fig/assets_detail.json"))})).replace("/*SOURCES*/",json.dumps({s["id"]:s for s in d["content_sources"]},ensure_ascii=False))
t=t.replace('view:"front",sel:null,','view:"front",sel:"ST36",')
open('atlas.html','w',encoding='utf-8').write(t)
# preview copy with full doc for local screenshot
open('/tmp/claude-0/-home-claude/0064597b-9ab7-5400-ab73-6534a8e3bd63/scratchpad/preview.html','w',encoding='utf-8').write('<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head><body>'+t+'</body></html>')
print(len(t))
