# -*- coding: utf-8 -*-
"""ERA01 ERA Evi - boyama paftaları üretimi (PAFTA, v02).

Kullanım:  python3 era01_dxf_duzlestir.py   (bir kez; DXF -> era01_geo.pkl)
           python3 era01_boyama.py [vaziyet] [katlar] [bloklar]   (argümansız: hepsi)
Çıktı:     03-boyama/ERA01_boyama_*.jpg (600 dpi, sRGB, q92), onizleme/*.png, kaynak/era01_ozet.json
"""
import json, sys, time
from decimal import Decimal

from era01_ortak import *  # noqa
from era01_katlar import KATLAR
import era01_plan as PL

BRUT_SEMA = {"A-blok-1-kat": 170.00, "C-blok-1-bodrum": 135.00, "C-blok-zemin-kat": 135.00}
BLOK_ADI = dict(A="A BLOK", B="B BLOK", C="C BLOK", D="D BLOK")
OZET = {}


BRUT_OVERRIDE = {"D-blok-1-kat": (129.77, "DXF şema 'KAT BRÜTÜ' (D_CK_SEMA); plan poligonu 217.71 terası da kapsıyor")}


def brut_of(k, r):
    """Brüt alan = terassız kapalı kat alanı (dıştan dışa)."""
    if k["kod"] in BRUT_OVERRIDE:
        return BRUT_OVERRIDE[k["kod"]]
    if r["brut"] is not None:
        return r["brut"], "DXF brüt alan poligonu (0_IFC_Brüt_Alan)"
    return BRUT_SEMA[k["kod"]], "DXF şema 'KAT BRÜTÜ' (plan üzerinde brüt poligonu yok)"


def caption(c, xr, y, k, r, big=True):
    b, _ = brut_of(k, r)
    s1 = 10 if big else 8.5
    stext(c, xr, y, BLOK_ADI[k["blok"]] + " · " + k["ad"], s1, bold=True, anchor="r")
    stext(c, xr, y + 4.4, "KOT %s (%s)" % (k["kot"], k["mutlak"]), 7, anchor="r", color=C["text2"])
    yy = y + 8.6
    stext(c, xr, yy, "NET ALAN TOPLAMI : %.2f m²" % float(r["net"]), 7.5, anchor="r", color=C["text2"]); yy += 4.0
    if r["ext_area"] > 0:
        stext(c, xr, yy, "AÇIK ALAN (TERAS/BALKON/BAHÇE) : %.2f m²" % float(r["ext_area"]), 7, anchor="r", color=C["text2"]); yy += 4.0
    stext(c, xr, yy, "BRÜT ALAN : %.2f m²" % b, 7.5, bold=True, anchor="r")
    return yy + 4


def room_list(c, x, y, rooms, w=62):
    stext(c, x, y, "No", 6.5, bold=True, color=C["text2"])
    stext(c, x + 7, y, "Mahal", 6.5, bold=True, color=C["text2"])
    stext(c, x + w, y, "Net alan (m²)", 6.5, bold=True, color=C["text2"], anchor="r")
    hline(c, x, x + w, y + 1.2, 0.15)
    yy = y + 4.6
    for r in sorted(rooms, key=lambda q: q.get("no", 0)):
        stext(c, x, yy, str(r.get("no", "")), 6.5)
        stext(c, x + 7, yy, r["name"], 6.5)
        stext(c, x + w, yy, fmt_area(r["area"]), 6.5, anchor="r")
        yy += 3.6
    return yy


def plan_mm(r):
    s = r["surf"]
    return s.get_width() / PXMM, s.get_height() / PXMM


def rec(k, r, olcek, fname):
    b, src = brut_of(k, r)
    OZET.setdefault(k["kod"], dict(blok=k["blok"], kat=k["ad"], kot=k["kot"], mutlak=k["mutlak"],
                                   net=float(r["net"]), acik=float(r["ext_area"]), brut=round(b, 2), brut_kaynak=src,
                                   iz_alani_kontrol=round(r["foot_area"], 2),
                                   numarali={}, eklenen_tefris=k.get("_added", []),
                                   mahaller=[(q["name"], fmt_area(q["area"]), q["kind"]) for q in r["rooms"]],
                                   dosyalar=[]))
    OZET[k["kod"]]["dosyalar"].append(dict(dosya=fname, olcek="1/%d" % olcek, px_cm=round(r["S"], 4)))
    OZET[k["kod"]]["numarali"][fname] = [q["name"] for q in r["numbered"]]


def sheet_floor(k):
    Wm, Hm, kag = 420, 297, "A3"
    aw, ah = Wm - 30 - 78, Hm - 30 - 28
    for olcek, txt in ((100, 1.0), (150, 1.25), (200, 1.6)):
        r = PL.render_plan(k, olcek, txt)
        pw, ph = plan_mm(r)
        if pw <= aw and ph <= ah:
            break
    s, c = new_sheet(Wm, Hm)
    header(c, Wm, BLOK_ADI[k["blok"]] + " · " + k["ad"], "KOT %s (%s)" % (k["kot"], k["mutlak"]))
    px_, py_ = 15 + (aw - pw) / 2, 30 + (ah - ph) / 2
    paste(c, r["surf"], px_, py_)
    xr = Wm - 15
    north_arrow(c, xr - 9, 52, 7, r["north"])
    ycap = Hm - 30 - 34
    if r["numbered"]:
        room_list(c, xr - 66, 75, r["numbered"])
    scale_bar(c, xr - 60, ycap - 16, olcek, 5 if olcek == 100 else 10, 1 if olcek == 100 else 2)
    caption(c, xr, ycap, k, r)
    footer(c, Wm, Hm, BLOK_ADI[k["blok"]] + " " + k["ad"], "1/%d (%s)" % (olcek, kag))
    fname = "ERA01_boyama_%s_v02.jpg" % k["kod"]
    size = save_jpg(s, os.path.join(OUT, fname))
    rec(k, r, olcek, fname)
    print(fname, "1/%d" % olcek, size, "%.1fs" % (time.time() - T0), flush=True)
    del r, s, c
    import gc; gc.collect()


def sheet_block(blok):
    ks = [k for k in KATLAR if k["blok"] == blok]
    for olcek, txt in ((150, 1.25), (200, 1.6), (250, 2.0), (300, 2.4)):
        rs = [PL.render_plan(k, olcek, txt, band=True) for k in ks]
        sizes = [plan_mm(r) for r in rs]
        gap = 12
        tw = sum(w for w, h in sizes) + gap * (len(sizes) - 1)
        th = max(h for w, h in sizes)
        if tw <= 420 - 30 and th <= 297 - 36 - 30 - 26:
            break
    Wm, Hm = 420, 297
    s, c = new_sheet(Wm, Hm)
    header(c, Wm, BLOK_ADI[blok] + " · KAT PLANLARI")
    x = 15 + (390 - tw) / 2
    top = 36 + (297 - 36 - 30 - 26 - th) / 2
    fname = "ERA01_boyama_%s-blok-kat-planlari_v02.jpg" % blok
    toplam = 0.0
    for k, r, (w, h) in zip(ks, rs, sizes):
        paste(c, r["surf"], x, top + (th - h))
        caption(c, x + w, top + th + 6, k, r, big=False)
        if r["numbered"]:
            room_list(c, x + w - min(62, w), top + th + 28, r["numbered"], w=min(62, w))
        x += w + gap
        rec(k, r, olcek, fname)
        toplam += round(brut_of(k, r)[0], 2)
    north_arrow(c, Wm - 24, 52, 7, rs[0]["north"])
    scale_bar(c, Wm - 15 - 62, 78, olcek, {150: 5, 200: 10, 250: 10}.get(olcek, 15), {150: 1, 200: 2, 250: 2}.get(olcek, 3))
    stext(c, Wm - 15, Hm - 30 - 6, "TOPLAM KAPALI ALAN : %.2f m²" % toplam, 9, bold=True, anchor="r")
    OZET.setdefault("toplam_kapali_alan", {})[blok] = round(toplam, 2)
    footer(c, Wm, Hm, BLOK_ADI[blok] + " KAT PLANLARI", "1/%d (A3)" % olcek)
    size = save_jpg(s, os.path.join(OUT, fname))
    del rs, s, c
    import gc; gc.collect()
    print(fname, "1/%d" % olcek, size, "toplam %.2f" % toplam, "%.1fs" % (time.time() - T0), flush=True)


def sheet_vaziyet():
    import era01_vaziyet as VZ
    r = VZ.render(500)
    pw, ph = plan_mm(r)
    Wm, Hm = 420, 297
    s, c = new_sheet(Wm, Hm)
    header(c, Wm, "VAZİYET PLANI", "ADA 1366 · PARSEL 45")
    aw, ah = Wm - 30 - 88, Hm - 34 - 30
    px_, py_ = 15 + (aw - pw) / 2, 34 + (ah - ph) / 2
    # yuvarlatılmış kırpma
    c.save()
    c.rectangle(mm(px_), mm(py_), mm(pw), mm(ph)); c.clip()
    paste(c, r["surf"], px_, py_)
    c.restore()
    c.rectangle(mm(px_), mm(py_), mm(pw), mm(ph)); setc(c, hx("#BDBDBB")); c.set_line_width(mm(0.2)); c.stroke()
    xr = Wm - 15
    north_arrow(c, xr - 9, 52, 7, VZ.NORTH_V)
    # lejant
    x0 = xr - 78
    y = 78
    stext(c, x0, y, "LEJANT", 8, bold=True, track_mm=0.6); y += 5
    items = [("Yapı (çatı planı)", hx("#BDBDBA"), "fill"), ("Zemin kat izi / teras", hx("#E8E6E1"), "fill"),
             ("Çim / doğal eğim", C["grass"], "fill"), ("Araç yolu / rampa / açık otopark", hx("#D6D4CF"), "fill"),
             ("Şev taşı / kademeli set", hx("#DCD8CF"), "fill"), ("Yol / kaldırım (parsel dışı)", hx("#E3E2DE"), "fill"),
             ("Set / istinat / bahçe duvarı", hx("#55575A"), "line"), ("Parsel sınırı", hx("#6E8A6C"), "dash"),
             ("Bina girişi", C["red"], "tri"), ("Kot (m)", C["text2"], "kot")]
    for lab, col, kind in items:
        if kind == "fill":
            c.rectangle(mm(x0), mm(y - 2.8), mm(7), mm(3.6)); setc(c, col); c.fill_preserve()
            setc(c, hx("#9A9A98")); c.set_line_width(mm(0.1)); c.stroke()
        elif kind == "line":
            setc(c, col); c.set_line_width(mm(0.45)); c.move_to(mm(x0), mm(y - 1)); c.line_to(mm(x0 + 7), mm(y - 1)); c.stroke()
        elif kind == "dash":
            setc(c, col); c.set_line_width(mm(0.4)); c.set_dash([mm(1.6), mm(0.8)])
            c.move_to(mm(x0), mm(y - 1)); c.line_to(mm(x0 + 7), mm(y - 1)); c.stroke(); c.set_dash([])
        elif kind == "tri":
            c.move_to(mm(x0 + 5), mm(y - 1)); c.line_to(mm(x0 + 2), mm(y - 2.8)); c.line_to(mm(x0 + 2), mm(y + 0.8)); c.close_path()
            setc(c, col); c.fill()
        else:
            c.move_to(mm(x0 + 3.5), mm(y)); c.line_to(mm(x0 + 2), mm(y - 2.4)); c.line_to(mm(x0 + 5), mm(y - 2.4)); c.close_path()
            setc(c, C["white"]); c.fill_preserve(); setc(c, col); c.set_line_width(mm(0.12)); c.stroke()
        stext(c, x0 + 10, y, lab, 7, color=C["text"])
        y += 5.2
    y += 4
    stext(c, x0, y, "BLOKLAR", 8, bold=True, track_mm=0.6); y += 5
    for b in "ABCD":
        n, kat, kot = VZ.BLOK_INFO[b]
        stext(c, x0, y, n, 7.5, bold=True)
        stext(c, x0 + 16, y, kat, 7)
        stext(c, x0 + 16, y + 3.6, kot, 6.5, color=C["text2"])
        y += 9
    scale_bar(c, xr - 62, Hm - 30 - 22, 500, 25, 5)
    stext(c, xr, Hm - 30 - 6, "VAZİYET PLANI", 10, bold=True, anchor="r")
    footer(c, Wm, Hm, "VAZİYET PLANI", "1/500 (A3)")
    fname = "ERA01_boyama_vaziyet_v02.jpg"
    size = save_jpg(s, os.path.join(OUT, fname))
    OZET["vaziyet"] = dict(dosya=fname, olcek="1/500", px_cm=round(r["S"], 4), cati_kaydirma=VZ.ROOF_SHIFT)
    print(fname, size, "%.1fs" % (time.time() - T0), flush=True)


if __name__ == "__main__":
    T0 = time.time()
    args = set(a for a in sys.argv[1:] if not a.startswith("blok=")) or {"vaziyet", "katlar", "bloklar"}
    SEC = [a.split("=")[1] for a in sys.argv[1:] if a.startswith("blok=")]
    SEC = SEC[0] if SEC else "ABCD"
    oz = os.path.join(HERE, "era01_ozet.json")
    if os.path.exists(oz):
        OZET.update(json.load(open(oz)))
        for v in OZET.values():
            if isinstance(v, dict) and "dosyalar" in v:
                if v.get("blok") not in SEC:
                    continue
                v["dosyalar"] = [d for d in v["dosyalar"] if not (
                    ("katlar" in args and "blok-kat-planlari" not in d["dosya"]) or
                    ("bloklar" in args and "blok-kat-planlari" in d["dosya"]))]
    if "vaziyet" in args:
        sheet_vaziyet()
    if "katlar" in args:
        for k in KATLAR:
            if k["blok"] in SEC:
                OZET.pop(k["kod"], None)
                sheet_floor(k)
    if "bloklar" in args:
        for b in SEC:
            sheet_block(b)
    json.dump(OZET, open(oz, "w"), ensure_ascii=False, indent=1, default=str)
    print("bitti %.1fs" % (time.time() - T0))
