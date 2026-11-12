# -*- coding: utf-8 -*-
"""ERA01 düzeltme turu 2 (v03): yalnız etkilenen paftaları üretir, özeti birleştirir.
H8: A 1. kat brüt 145.04 (kat bahçesi hariç). Kot/etiket ve numara/giriş üçgeni çakışmaları.
Kullanım: python3 era01_v03.py   (önce era01_dxf_duzlestir.py)"""
import json, os, time
import era01_ortak as O
O.SURUM = "v03"
import era01_boyama as B
B.SURUM_ = "v03"
B.T0 = time.time()
from era01_katlar import KATLAR

oz = os.path.join(B.HERE, "era01_ozet.json")
old = json.load(open(oz))
B.OZET.clear()
B.sheet_floor([k for k in KATLAR if k["kod"] == "A-blok-1-kat"][0])
B.sheet_block("A")
B.sheet_block("D")
new = B.OZET
for kod, v in new.items():
    if kod == "toplam_kapali_alan":
        old.setdefault(kod, {}).update(v)
        continue
    o = old.get(kod, {})
    regen = set(os.path.basename(d["dosya"]).replace("_v03.jpg", "") for d in v["dosyalar"])
    keep = [d for d in o.get("dosyalar", []) if d["dosya"].rsplit("_v", 1)[0] not in regen]
    num = {f: n for f, n in o.get("numarali", {}).items() if f.rsplit("_v", 1)[0] not in regen}
    num.update(v["numarali"])
    v["dosyalar"] = keep + v["dosyalar"]
    v["numarali"] = num
    old[kod] = v
old["surum_notu"] = "v03: A-blok-1-kat, A-blok-kat-planlari, D-blok-kat-planlari; diğerleri v02"
json.dump(old, open(oz, "w"), ensure_ascii=False, indent=1, default=str)
print("bitti", time.time() - B.T0)
