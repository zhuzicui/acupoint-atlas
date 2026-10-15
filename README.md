# Acupoint Atlas 穴位图

An interactive map of acupressure points in Chinese and English: 361 WHO standard points, Yintang, 15 head-and-neck extra points and 69 auricular (ear) points, each with a plain-language "how to find it", traditional uses and sourced research evidence. Type a symptom (e.g. *nausea*, *headache*) to find the points linked to it.

## Layout

| Path | What it is |
|---|---|
| `app/index.html` | The whole app in one self-contained page (data and figures embedded). Open it in any browser. |
| `data/acupoints.json` | The dataset for your own app: names (简体/繁體/pinyin), meridian, locations, benefits with sources, map coordinates for every view. |
| `data/acupoints.csv`, `data/acupoints.xlsx` | The same data as a flat table (one row per point). |
| `assets/` | Clean line-art hand drawings (SVG + transparent PNG). |
| `src/` | Build scripts: `build.py` writes the dataset, `gen_page.py` fills `page_template.html` to produce the app. |
| `src/figures/` | Figure tracing and point-placement scripts (body, head, hand, foot, ear views). |
| `src/content/` | Location descriptions (`loc_*.py`), benefits assembly (`benefits.py`) and the assembled `content.json`. |

## Data model (acupoints.json)

Each point has: `id` (WHO code such as `ST36`, or `EAR-Shenmen`), `name_zh_s`, `name_zh_t`, `pinyin`, `meridian`, `area`, `location_plain`, `location_anatomical`, safety flags (`acupressure_suitable`, `pregnancy_caution`, `safety_note`), `benefits` (`traditional`, `tcm_actions`, `studies` with PubMed IDs, `reviews` with verified citations) and `map` positions per view for the female and male figures.

Views use a 400×1000 box (body) or 400×480 box (head, hand, foot, ear). Bilateral points are stored for one side; mirror with `x = 400 − x` on the front/back/face/head-back views.

## Sources

- Point codes, names and locations: WHO *Standard Acupuncture Point Locations in the Western Pacific Region* (2008); GB/T 12346-2021. Location text rewritten in plain language.
- Ear points: names and zones per GB/T 13734 耳穴名称与定位.
- Traditional indications and TCM actions: AcuKG knowledge graph (Li et al., *JAMIA* 2025, doi:10.1093/jamia/ocaf179), compiled from the WHO standard and Acufinder; normalised and glossed. The AcuKG repository has no licence file — check before commercial use.
- Clinical studies: PubMed IDs of trials that used a point for a condition (via AcuKG). Systematic reviews: Cochrane and meta-analysis citations, verified.
- Body figures traced from the author's female/male, hand, foot and ear templates (not included in this repository).

## Rebuilding

```
cd src && python3 build.py ../data && python3 gen_page.py
```

`build.py` expects `content/content.json` and `figures/newmap.json`; to regenerate those, run `content/assemble.py` (needs the AcuKG CSVs) and `figures/build_map.py`.

**Disclaimer:** for orientation and education only. It is not medical advice; consult a qualified practitioner.
