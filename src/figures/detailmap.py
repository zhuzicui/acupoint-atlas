# Extra placements of body points on the detail views (viewBox 0 0 400 480).
# hand_back = left hand seen from the back (thumb on the right); hand_palm = left hand palm (thumb on the left)
# foot_top = left foot from above (big toe on the right); foot_sole = right foot sole; foot_in = right foot inner side (toes left); foot_out = right foot outer side (toes right)
D = {}
def put(view, s):
    for tok in s.split():
        code, xy = tok.split("="); x, y = xy.split(",")
        D.setdefault(code, []).append((view, float(x), float(y)))
put("hand_back", """
LU11=326,185 LU7=238,425 LI1=252,52 LI2=247,215 LI3=247,242 LI4=258,300 LI5=252,378
TE1=120,58 TE2=115,222 TE3=113,255 TE4=180,392 TE5=178,445
SI1=70,128 SI2=90,222 SI3=98,255 SI4=116,345 SI5=124,380 SI6=135,415
HT9=93,128 PC9=185,25
""")
put("hand_palm", """
LU9=189,388 LU8=190,410 LU10=142,318
HT7=288,387 HT6=286,398 HT5=285,410 HT4=285,424 HT8=302,300
SI3=310,268 SI4=300,345
PC7=225,387 PC6=225,440 PC8=205,300 PC9=205,25
""")
put("foot_top", """
ST41=203,246 ST42=205,300 ST43=200,374 ST44=200,404 ST45=197,421
LR1=235,412 LR2=225,400 LR3=228,355 LR4=236,256
SP1=268,412 SP2=272,390 SP3=275,366 SP5=255,266
GB40=152,270 GB41=143,340 GB42=140,362 GB43=138,385 GB44=142,401
BL67=120,378 BL64=120,345 BL63=128,316
""")
put("foot_sole", "KI1=222,165")
put("foot_in", """
SP1=48,322 SP2=95,328 SP3=128,322 SP4=172,310 SP5=235,282 SP6=300,160
KI2=215,300 KI3=320,252 KI4=328,268 KI5=322,286 KI6=268,290 KI7=325,190 KI8=312,190
LR4=240,262
""")
put("foot_out", """
BL59=58,150 BL60=52,240 BL61=55,285 BL62=75,275 BL63=110,290 BL64=150,305 BL65=300,318 BL66=330,320 BL67=355,318
GB39=98,150 GB40=110,262 GB41=205,290 GB42=260,300 GB43=315,300 GB44=350,310
ST41=125,228 ST42=175,260
""")
