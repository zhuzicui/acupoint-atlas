import json, csv, unicodedata, sys
from points_data import MERIDIANS, EXTRA_HN, AREA
import mapdata as MD
sys.path.insert(0, "/home/claude/fig"); from detailmap import D as DETAIL
from ear_points import EAR_POINTS, EAR_SRC
sys.path.insert(0, "/home/claude/ind"); from benefits import GLOSS
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

S2T = dict(zip(
 "丝丰临乡云仑仓会侠关兑养冲劳华却历厉厌厘参台后听哑处复头孙宾带库归悬扬攒机条来极枢气沟泺泽浆涌渊渎温满灵犊玑环盖纲经结络维缩肠肾胆脉脑荣营虚贞辄辅边门间阙阳阴际隐顶颅颊颔颧风飞鱼鸠龈钟长窦窍筑仆户强横内鬓车宫聪当颈",
 "絲豐臨鄉雲崙倉會俠關兌養衝勞華卻歷厲厭釐參臺後聽啞處復頭孫賓帶庫歸懸揚攢機條來極樞氣溝濼澤漿湧淵瀆溫滿靈犢璣環蓋綱經結絡維縮腸腎膽脈腦榮營虛貞輒輔邊門間闕陽陰際隱頂顱頰頷顴風飛魚鳩齦鐘長竇竅築僕戶強橫內鬢車宮聰當頸"))
WORD = {"昆仑": "崑崙", "大钟": "大鍾"}

def s2t(s):
    for k, v in WORD.items():
        s = s.replace(k, v)
    return "".join(S2T.get(c, c) for c in s)

def plain(p):
    return "".join(c for c in unicodedata.normalize("NFD", p) if unicodedata.category(c) != "Mn").replace("'", "")

PREG = {"LI4", "SP6", "GB21", "BL31", "BL32", "BL33", "BL34", "BL60", "BL67"}
NOTES = {
 "GV29": "Not a meridian point in WHO 2008, where it is extra point EX-HN3; GV29 in China GB/T 12346-2006/2021.",
 "EX-Anmian": "Not in WHO 2008; widely used extra point (between TE17 and GB20).",
 "GV26": "Also called Rénzhōng 人中.",
 "TE1": "TE (WHO) = SJ / TB / TW in other texts.",
 "BL45": "Traditional and simplified characters identical (譩譆).",
}
SAFETY = {
 "ST9": "Over the carotid artery: do not press firmly.",
 "CV22": "Suprasternal notch: press gently, never inward on the windpipe.",
 "EX-HN7": "On the eye socket next to the eyeball: needling point, not for self-pressing.",
 "EX-HN9": "Inside the nostril: not suitable for acupressure.",
 "EX-HN10": "On the tongue: not suitable for acupressure.",
 "EX-HN11": "Under the tongue: not suitable for acupressure.",
 "EX-HN12": "Under the tongue: not suitable for acupressure.",
 "EX-HN13": "Under the tongue: not suitable for acupressure.",
}
NO_PRESS = {"EX-HN7","EX-HN9","EX-HN10","EX-HN11","EX-HN12","EX-HN13"}
def rec(pid, meridian, num, alt, py, hz, who, men="", mzh=""):
    return {"id": pid, "meridian": meridian, "number": num, "alt_code": alt,
            "pinyin": py, "pinyin_plain": plain(py), "name_zh_s": hz, "name_zh_t": s2t(hz),
            "meridian_en": men, "meridian_zh": mzh,
            "body_region": "Head & neck" if pid in AREA else "", "area": AREA.get(pid, ""),
            "who_2008": who, "acupressure_suitable": pid not in NO_PRESS,
            "pregnancy_caution": pid in PREG, "safety_note": SAFETY.get(pid, ""),
            "notes": NOTES.get(pid, "")}

pts, mers = [], []
for code, alt, en, zh, zh_py, block in MERIDIANS:
    rows = [r.split("|") for r in block.strip().split("\n")]
    mers.append({"code": code, "alt_code": alt, "name_en": en, "name_zh_s": zh,
                 "name_zh_t": s2t(zh), "name_pinyin": zh_py, "point_count": len(rows)})
    for i, (py, hz, eng) in enumerate(rows, 1):
        pid = f"{code}{i}"
        a = "EX-HN3" if pid == "GV29" else f"{alt}{i}"
        pts.append(rec(pid, code, i, a, py, hz, pid != "GV29", en, zh))
ex = [r.split("|") for r in EXTRA_HN.strip().split("\n")]
mers.append({"code": "EX-HN", "alt_code": "", "name_en": "Extra points: head & neck", "name_zh_s": "经外奇穴（头颈部）",
             "name_zh_t": "經外奇穴（頭頸部）", "name_pinyin": "Jīngwài Qíxué (Tóujǐngbù)", "point_count": len(ex)})
for pid, py, hz, who in ex:
    num = int(pid.split("HN")[1]) if "HN" in pid else ""
    pts.append(rec(pid, "EX-HN", num, "", py, hz, who == "1", "Extra points: head & neck", "经外奇穴"))

NM = json.load(open("/home/claude/fig/newmap.json"))
CT = json.load(open("/home/claude/ind/content.json", encoding="utf-8"))
for p in pts:
    f, m = NM["f"][p["id"]], NM["m"][p["id"]]
    p["map_view"] = f[0][0]
    p["map_x_female"], p["map_y_female"] = f[0][1], f[0][2]
    p["map_x_male"], p["map_y_male"] = m[0][1], m[0][2]
    p["bilateral"] = MD.bilateral(p["id"])
    c = CT["points"][p["id"]]
    p["location_plain"] = c["location"]["plain"]; p["location_anatomical"] = c["location"]["anatomical"]
    p["indications"] = "; ".join(t["term"] + (f" ({t['plain']})" if t["plain"] else "") for t in c["traditional"])
    p["indications_source"] = "textbook" if p["id"] in CT["points"] and c["traditional"] and c["traditional"][0]["source"] == "textbook" else ("acukg" if c["traditional"] else "")
    p["tcm_actions"] = "; ".join(c["actions"])
    p["studies"] = "; ".join(f"{s['condition']} (PMID {', '.join(s['pmids'])})" for s in c["studies"])
    p["reviews"] = " | ".join(f"{r['claim']} — {r['cite']}" for r in c["reviews"])
    p["_content"] = c
    p["_placements"] = {"female": [{"view": v, "x": x, "y": y} for v, x, y in f], "male": [{"view": v, "x": x, "y": y} for v, x, y in m]}

# ---- auricular points ----
EAR_ROWS = [r.split("|") for r in EAR_POINTS.strip().split("\n")]
mers.append({"code": "EAR", "alt_code": "", "name_en": "Auricular (ear) points", "name_zh_s": "耳穴", "name_zh_t": "耳穴", "name_pinyin": "Ěrxué", "point_count": len(EAR_ROWS)})
for i, (pid, py, hz, en, zone, xy, locp, ind) in enumerate(EAR_ROWS, 1):
    x, y = [float(v) for v in xy.split(",")]
    p = {"id": pid, "meridian": "EAR", "number": i, "alt_code": "", "pinyin": py, "pinyin_plain": plain(py), "name_zh_s": hz, "name_zh_t": s2t(hz),
         "name_en": en, "meridian_en": "Auricular (ear) points", "meridian_zh": "耳穴", "body_region": "Head & neck", "area": "Ear",
         "who_2008": False, "acupressure_suitable": True, "pregnancy_caution": False, "safety_note": "", "notes": f"Ear zone: {zone}. Standard: GB/T 13734 耳穴名称与定位.",
         "map_view": "ear", "map_x_female": x, "map_y_female": y, "map_x_male": x, "map_y_male": y, "bilateral": True,
         "location_plain": locp, "location_anatomical": f"Auricle, {zone}.",
         "tcm_actions": "", "studies": "", "reviews": ""}
    trad = [{"term": t.strip(), "plain": GLOSS.get(t.strip(), ""), "source": "ear-standard"} for t in ind.split(";")]
    p["indications"] = "; ".join(t["term"] + (f" ({t['plain']})" if t["plain"] else "") for t in trad)
    p["indications_source"] = "ear-standard"
    p["_content"] = {"traditional": trad, "actions": [], "studies": [], "reviews": []}
    p["_placements"] = {"female": [{"view": "ear", "x": x, "y": y}], "male": [{"view": "ear", "x": x, "y": y}]}
    pts.append(p)
# ---- detail-view placements (hand, foot) for body points ----
for p in pts:
    for v, x, y in DETAIL.get(p["id"], []):
        for sex in ("female", "male"): p["_placements"][sex].append({"view": v, "x": x, "y": y})

MAPINFO = {
 "note": "Schematic positions for drawing points on the female and male body figures. For orientation only; use location descriptions to find points.",
 "views": {"front": "0 0 400 1000, anterior", "back": "0 0 400 1000, posterior",
           "side": "0 0 400 1000, lateral, facing right",
           "face": "0 0 400 480, front of head & neck", "headside": "0 0 400 480, head lateral facing right",
           "headback": "0 0 400 480, back of head & neck",
           "hand_back": "0 0 400 480, left hand seen from the back (thumb on the right)", "hand_palm": "0 0 400 480, right palm (thumb on the right)",
           "foot_top": "0 0 400 480, left foot from above (big toe on the right)", "foot_sole": "0 0 400 480, right sole", "foot_in": "0 0 400 480, right foot inner side (toes left)", "foot_out": "0 0 400 480, right foot outer side (toes right)",
           "ear": "0 0 400 480, right ear"},
 "detail_views": "Hand, foot and ear views are traced from 'hand.ai', 'foot.ai' and 'ear.ai'; they are the same for both figures and show one side only (no mirroring).",
 "figures": "Coordinates fit the figures traced from 'woman body.ai' (female) and 'male body.ai' (male). Head points also carry a placement in the matching body view.",
 "bilateral": "Points with bilateral=true are stored for one side only in front/back/face/headback; draw the other side at x = 400 - x."}
out = sys.argv[1]
with open(f"{out}/acupoints.json", "w", encoding="utf-8") as f:
    json.dump({"version": "0.6", "map_info": MAPINFO, "content_sources": CT["sources"] + [EAR_SRC], "meridians": mers, "points": [{**{k: v for k, v in p.items() if not k.startswith("map_") and k not in ("_placements", "_content", "indications", "indications_source", "tcm_actions", "studies", "reviews")}, "bilateral": p["bilateral"], "map": p["_placements"], "benefits": {"traditional": p["_content"]["traditional"], "tcm_actions": p["_content"]["actions"], "studies": p["_content"]["studies"], "reviews": p["_content"]["reviews"]}} for p in pts]}, f, ensure_ascii=False, indent=1)
with open(f"{out}/acupoints.csv", "w", encoding="utf-8-sig", newline="") as f:
    flds=[k for k in pts[0] if k not in ('_placements','_content')]; w = csv.DictWriter(f, fieldnames=flds, extrasaction='ignore'); w.writeheader(); w.writerows(pts)

HEAD = {"id": "Code", "meridian": "Meridian", "number": "No.", "alt_code": "Alt. code",
        "pinyin": "Pinyin", "pinyin_plain": "Pinyin (no tones)", "name_zh_s": "中文 (简体)",
        "name_zh_t": "中文 (繁體)", "meridian_en": "Meridian (EN)",
        "meridian_zh": "经络", "who_2008": "In WHO 2008", "pregnancy_caution": "Pregnancy caution",
        "notes": "Notes", "body_region": "Body region", "area": "Area", "acupressure_suitable": "OK to press", "safety_note": "Safety note", "map_view": "Map view", "map_x_female": "Map x (F)", "map_y_female": "Map y (F)", "map_x_male": "Map x (M)", "map_y_male": "Map y (M)", "bilateral": "Both sides", "location_plain": "How to find it", "location_anatomical": "Location (anatomical)", "indications": "Traditional indications", "indications_source": "Indications source", "tcm_actions": "TCM actions", "studies": "Clinical studies (PubMed)", "reviews": "Systematic reviews"}
wb = Workbook()
hf, fill = Font(bold=True, color="FFFFFF"), PatternFill("solid", fgColor="2F5D50")
def sheet(ws, keys, heads, data, widths):
    ws.append(heads)
    for c in ws[1]: c.font, c.fill = hf, fill
    for d in data: ws.append([("Yes" if d[k] is True else "No" if d[k] is False else d[k]) for k in keys])
    for i, wd in enumerate(widths, 1): ws.column_dimensions[get_column_letter(i)].width = wd
    ws.freeze_panes = "B2"; ws.auto_filter.ref = ws.dimensions
ws = wb.active; ws.title = "Points"
k = [x for x in pts[0] if x not in ("_placements","_content")]; sheet(ws, k, [HEAD[x] for x in k], pts, [11,9,5,9,16,16,11,11,24,16,13,8,10,9,10,40,50,10,9,9,9,9,10,70,60,70,12,50,60,80])
ws2 = wb.create_sheet("Meridians")
mk = list(mers[0]); sheet(ws2, mk, ["Code","Alt. code","English","中文 (简体)","中文 (繁體)","Pinyin","Points"], mers, [8,9,28,16,16,28,8])
ws3 = wb.create_sheet("About")
for line in [
 "Acupressure points dataset v0.2 — 361 WHO standard points + GV29 Yintang + 15 head & neck extra points (377 rows)",
 "",
 "Codes & numbering: WHO Standard Acupuncture Point Locations in the Western Pacific Region (2008); matches GB/T 12346-2021.",
 "Chinese names: standard names (simplified); traditional forms converted for Taiwan/HK users.",
 "Point names: Chinese + pinyin only (no English translations). Meridian names keep their standard English terms.",
 "Head & neck: Body region / Area columns tag every point on the head, face and neck. Points at the base of the skull (e.g. GB20, BL10, GV16) are tagged Neck, following WHO.",
 "Extra points EX-HN1–15 from WHO 2008 (EX-HN3 = GV29 Yintang, not duplicated) + Anmian 安眠 (not in WHO 2008).",
 "OK to press = No for points inside the nose/mouth or beside the eyeball.",
 "Pregnancy caution: points traditionally avoided in pregnancy (LI4, SP6, GB21, BL31–34, BL60, BL67). Not exhaustive.",
 "Map view / Map x / Map y (F = female figure, M = male figure): schematic position on the body map (see JSON map_info). Both sides = mirror the point to the other side.",
 "How to find it: plain-language location written for this app (1 cun = thumb-width; 1.5 cun = 2 finger-widths; 2 cun = 3 finger-widths; 3 cun = 4 finger-widths). Location (anatomical): WHO-2008-style description, rewritten.",
 "Traditional indications: from the AcuKG knowledge graph (Li et al., JAMIA 2025; doi 10.1093/jamia/ocaf179), compiled from the WHO standard and Acufinder; terms normalised, plain-English gloss in brackets. Source = textbook for points not in AcuKG (standard textbooks).",
 "Clinical studies: PubMed IDs of trials that used the point for that condition (from AcuKG). A study is not proof of benefit. Systematic reviews: verified Cochrane / meta-analysis citations for the most-used points.",
 "Auricular (ear) points: 69 points named per GB/T 13734 耳穴名称与定位, positioned by ear zone on the right-ear drawing; indications from standard auricular textbooks (code EAR-…, no WHO code).",
 "Hand/foot detail views: body points on the hand and foot carry extra map placements (JSON map[]) on the hand_back, hand_palm, foot_top, foot_sole, foot_in, foot_out views.",
 "Not yet included: extra points on the body/limbs, ear points, body-region tags outside head & neck, location descriptions, indications/symptoms.",
 "Verify against the WHO 2008 book / GB/T 12346-2021 before publishing.",
]: ws3.append([line])
ws3.column_dimensions["A"].width = 120; ws3["A1"].font = Font(bold=True, size=13)
wb.save(f"{out}/acupoints.xlsx")
print(len(pts), "points")
