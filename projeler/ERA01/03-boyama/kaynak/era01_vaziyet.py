# -*- coding: utf-8 -*-
"""ERA01 vaziyet planı boyaması (PAFTA, v01) - konsept gri / DNM01 dili, 1/500.

Taban: DXF 'VAZIYET PLANI' bloğu (A sırası, model alanı 0.25 ölçekli INSERT). Koordinatlar gerçek cm'ye
çevrilir (V = (M - insert) / 0.25). Bölgeler: vaziyet çizgileri (yol, set/istinat/bahçe duvarı, şev,
rampa, merdiven) bariyer kabul edilerek raster bileşenlere ayrılır, DXF'teki etiketlere göre
(YAYA YOLU, KALDIRIM, YOL, DOĞAL EĞİM, ŞEV TAŞI, Park, komşu parsel no...) sınıflanır.
Yapılar: her bloğun çatı planı (DXF) köşe kotu sembolleriyle hesaplanan dönüşümle yerine konur.
"""
import json, math, random, re
import cairo
import numpy as np
from scipy import ndimage
from shapely.geometry import Polygon, Point, LineString
from shapely.ops import unary_union

from era01_ortak import *  # noqa
from era01_katlar import CATI, KATLAR

DATA = load_geo()
GEO, TOPS = DATA["geo"], DATA["tops"]
VZ = [t for t in TOPS if t["name"] == "VAZIYET PLANI"][0]
INS = (VZ["x"], VZ["y"])
SC = VZ["sx"]
TR = json.load(open(os.path.join(HERE, "era01_vaziyet_donusum.json")))
NORTH_V = 21.29          # vaziyet kuzeyi (pafta kuzey sembolü, A/B sırası ile aynı yön)
DEBUG = None
ROOF_SHIFT = {}
CORES = {}
ENTR = {}


def M2V(x, y):
    return ((x - INS[0]) / SC, (y - INS[1]) / SC)


def P2V(blok, x, y):
    t = TR[blok]
    th = math.radians(t["ang"])
    mx = t["s"] * (math.cos(th) * x - math.sin(th) * y) + t["t"][0]
    my = t["s"] * (math.sin(th) * x + math.cos(th) * y) + t["t"][1]
    return M2V(mx, my)


def sub(g):
    return g["blk"][1] if len(g["blk"]) > 1 else "-"


SKIP_LAY = ("0_IFC_Notation_Section", "0_IFC_Room_Text", "0_IFC_Notation_Level", "0_IFC_Text_Explanation_50",
            "0_IFC_Stair_Text")


def collect():
    lines, texts, cars, rails, hatches, stairs, parcel = [], [], [], [], [], [], None
    for g in GEO:
        if g["top"] != VZ["i"]:
            continue
        sb = sub(g)
        if g["t"] == "T":
            x, y = M2V(g["x"], g["y"])
            texts.append(dict(s=g["txt"].replace("\\P", "\n").strip(), x=x, y=y, h=g["h"] / SC, lay=g["lay"], sub=sb))
            continue
        if g["t"] == "H":
            hatches.append((sb, g["lay"], [[M2V(*p) for p in l] for l in g["loops"]]))
            continue
        pts = [M2V(*p) for p in g["pts"]]
        if g["lay"] == "0_IFC_Parsel Sınırı" and g["t"] == "P":
            parcel = pts
            continue
        if sb in ("BLOK KESIT YERLERI", "VP_KESIT YERLERI", "VAZ ARAC NO", "VP_GORUNUS YAZILARI", "BLOK KOSE KOTLARI", "VP_YAZI"):
            continue
        if g["lay"].startswith(SKIP_LAY) and sb != "ARAZİYOLLAR_2":
            continue
        if g["lay"] == "6_IFC_Car":
            cars.append((pts, g["t"] == "P"))
            continue
        if g["lay"] == "2_IFC_Handrail":
            rails.append((pts, g["t"] == "P"))
        if g["lay"] == "1_IFC_Stair":
            stairs.append((pts, g["t"] == "P"))
        lines.append((pts, g["t"] == "P", g["lay"], sb))
    return dict(lines=lines, texts=texts, cars=cars, rails=rails, hatches=hatches, stairs=stairs, parcel=parcel)


def roof_geo(blok):
    x0, y0, x1, y1, names = CATI[blok]
    sel = set(t["i"] for t in TOPS if t["name"] in names and t["bb"] and x0 < (t["bb"][0] + t["bb"][2]) / 2 < x1
              and y0 < (t["bb"][1] + t["bb"][3]) / 2 < y1)
    out = []
    for g in GEO:
        if g["top"] in sel and g["t"] in "LP":
            out.append(([P2V(blok, *p) for p in g["pts"]], g["t"] == "P", g["lay"]))
    return out


def zk_outline(blok):
    """Zemin kat plan poligonları (mahal + brüt) -> vaziyette bina izi."""
    from era01_plan import collect as pcollect
    k = [k for k in KATLAR if k["blok"] == blok and k["tip"] == "zemin"][0]
    d = pcollect(k)
    polys, core = [], []
    for pts in d["brut"] + d["areas"]:
        try:
            polys.append(Polygon([P2V(blok, *p) for p in pts]).buffer(0))
        except Exception:
            pass
    if d["brut"]:
        core = [Polygon([P2V(blok, *p) for p in pts]).buffer(0) for pts in d["brut"]]
    else:
        from era01_plan import rooms_from
        core = [Polygon([P2V(blok, *p) for p in r["poly"].exterior.coords]).buffer(0)
                for r in rooms_from(d, k) if r["kind"] != "terrace" and r["poly"].geom_type == "Polygon"]
    ent = []
    for loop in d["ok"]:
        P = Polygon([P2V(blok, *p) for p in loop])
        if P.area > 0:
            ent.append((P.centroid.x, P.centroid.y))
    CORES[blok] = unary_union(core).buffer(30).buffer(-30)
    ENTR[blok] = ent
    return unary_union(polys)


def render(olcek=500, seed=5):
    rnd = random.Random(seed)
    S = PXMM * 100.0 / olcek / 10.0
    d = collect()
    par = Polygon(d["parcel"])
    bx0, by0, bx1, by1 = par.bounds
    X0, Y0, X1, Y1 = bx0 - 1500, by0 - 1100, bx1 + 1500, by1 + 1100
    W, H = int((X1 - X0) * S), int((Y1 - Y0) * S)
    mat = cairo.Matrix(S, 0, 0, -S, -X0 * S, Y1 * S)
    px = lambda cm: cm * S

    def stroke_lines(lines, lw):
        def f(c):
            c.set_line_width(lw)
            for it in lines:
                pts, cl = it[0], it[1]
                path_pts(c, pts, cl); c.stroke()
        return f

    def fill_poly(polys):
        def f(c):
            for pts in polys:
                path_pts(c, pts)
            c.fill()
        return f

    barrier = ctx_mask(W, H, mat, stroke_lines(d["lines"] + [(d["parcel"], True)], max(10, 2.2 / S)))
    parcel_m = ctx_mask(W, H, mat, fill_poly([d["parcel"]]))
    free = ~barrier
    lab, n = ndimage.label(free)
    # etiketler
    def at(x, y):
        qx, qy = int((x - X0) * S), int((Y1 - y) * S)
        if 0 <= qx < W and 0 <= qy < H:
            return lab[qy, qx]
        return 0
    cls = {}
    pri = dict(pave=5, road=6, ramp=4, grass=2, stone=3, park=2, nb=1)
    def setc_(i, c):
        if i and pri[c] >= pri.get(cls.get(i, "nb"), 0):
            cls[i] = c
    for t in d["texts"]:
        s = t["s"].upper()
        # yazının ortası (sol alt yerine yaklaşık merkez)
        cx = t["x"] + len(s.split("\n")[0]) * t["h"] * 0.28
        cy = t["y"] - t["h"] * 0.2
        i = at(cx, cy) or at(t["x"], t["y"])
        if "YAYA YOLU" in s or "KALDIRIM" in s:
            setc_(i, "pave")
        elif s.startswith("YOL") or "SOKAK" in s:
            if not par.contains(Point(cx, cy)):
                setc_(i, "road")
        elif s.startswith("H:"):
            setc_(i, "ramp")
        elif "DOĞAL EĞİM" in s:
            setc_(i, "grass")
        elif s == "PARK":
            setc_(i, "park")
        elif re.fullmatch(r"\d{2}", s) and t["lay"] == "NADI":
            setc_(i, "nb")
    for pts, cl in d["cars"]:
        xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
        setc_(at((min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2), "ramp")
    sizes = ndimage.sum(free, lab, np.arange(n + 1))
    # ince şeritler (şev taşı / basamak) -> taş
    dist = ndimage.distance_transform_edt(free)
    maxd = ndimage.maximum(dist, lab, np.arange(n + 1))
    inside_frac = ndimage.mean(parcel_m, lab, np.arange(n + 1))
    classes = np.zeros(n + 1, np.uint8)  # 0 dış zemin,1 çim,2 sert zemin,3 araç yolu/rampa,4 taş,5 yol,6 park(yeşil),7 komşu
    code = dict(grass=1, pave=2, ramp=3, stone=4, road=5, park=6, nb=7)
    for i in range(1, n + 1):
        if i in cls:
            classes[i] = code[cls[i]]
        elif inside_frac[i] > 0.5:
            classes[i] = 4 if maxd[i] < px(70) else 1
        else:
            classes[i] = 0
    cmap = classes[lab]
    # en büyük dış bileşen arka plan
    # ---- çizim
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    c = cairo.Context(surf); c.set_matrix(mat)

    def paint_mask(mask, col):
        c.save(); c.identity_matrix(); c.set_source_surface(mask_to_surf(mask, col), 0, 0); c.paint(); c.restore()

    def paint_alpha(alpha, rgb):
        c.save(); c.identity_matrix(); c.set_source_surface(alpha_surf(alpha, rgb), 0, 0); c.paint(); c.restore()

    COLS = {0: hx("#F1F0EC"), 1: C["grass"], 2: hx("#E4E1DA"), 3: hx("#D6D4CF"), 4: hx("#DCD8CF"), 5: hx("#E3E2DE"),
            6: hx("#E3EAE1"), 7: hx("#F1F0EC")}
    c.save(); c.identity_matrix(); setc(c, COLS[0]); c.paint(); c.restore()
    grow = ndimage.grey_dilation(cmap, size=(5, 5))   # bariyer piksellerini komşu sınıfla kapat
    cfull = np.where(barrier, grow, cmap)
    for k_, col in COLS.items():
        if k_ == 0:
            continue
        paint_mask(cfull == k_, col)
    # çimde hafif doku
    g1 = cfull == 1
    paint_alpha((blur_alpha(g1 & (dist > px(250)), px(220), strength=0.30) * g1).astype(np.uint8), C["grass2"][:3])
    # yapılar: zemin kat izi gölgesi + çatı
    foot_all = []
    roofs = {}
    for b in "ABCD":
        try:
            fo = zk_outline(b)
        except Exception:
            fo = None
        rg = roof_geo(b)
        # çatı paftası zemin paftasından farklı konumda: en büyük kapalı poligonu (saçak) zemin kat izine ortala
        big = None
        for pts, cl, lay in rg:
            if cl and len(pts) > 3:
                try:
                    P = Polygon(pts).buffer(0)
                except Exception:
                    continue
                if big is None or P.area > big.area:
                    big = P
        if big is not None and fo is not None and not fo.is_empty:
            core = fo
            ar = [r for r in KATLAR if r["blok"] == b and r["tip"] == "zemin"]
            fb = CORES[b].bounds; bb = big.bounds
            dx = (fb[0] + fb[2]) / 2 - (bb[0] + bb[2]) / 2
            dy = (fb[1] + fb[3]) / 2 - (bb[1] + bb[3]) / 2
            ROOF_SHIFT[b] = (dx, dy)
            rg = [([(x + dx, y + dy) for x, y in pts], cl, lay) for pts, cl, lay in rg]
        roofs[b] = (fo, rg)
        if fo is not None and not fo.is_empty:
            foot_all.append(fo)
    # ağaçlar (çim bileşenlerinde, sınır boyunca ve boş alanlarda)
    sh = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); shc = cairo.Context(sh); shc.set_matrix(mat)
    trees = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); tc = cairo.Context(trees); tc.set_matrix(mat)
    bld_union = unary_union(foot_all).buffer(350) if foot_all else None
    ok_tree = (cfull == 1) & (dist > px(160)) & parcel_m
    yy, xx = np.nonzero(ok_tree[::9, ::9])
    cand = list(zip(xx * 9, yy * 9)); rnd.shuffle(cand)
    placed = []
    for (qx, qy) in cand:
        wx, wy = X0 + qx / S, Y1 - qy / S
        if bld_union is not None and bld_union.contains(Point(wx, wy)):
            continue
        if any(math.dist((wx, wy), q) < 750 for q in placed):
            continue
        placed.append((wx, wy))
    for i, (wx, wy) in enumerate(placed):
        if i % 4 == 3:
            tree(tc, shc, wx, wy, rnd.uniform(120, 160), "flower", rnd)
        else:
            tree(tc, shc, wx, wy, rnd.uniform(260, 380), "green", rnd)
    # park alanlarına ağaç
    okp = (cfull == 6) & (dist > px(250))
    yy, xx = np.nonzero(okp[::11, ::11]); cand = list(zip(xx * 11, yy * 11)); rnd.shuffle(cand)
    pp = []
    for (qx, qy) in cand[:4000]:
        wx, wy = X0 + qx / S, Y1 - qy / S
        if any(math.dist((wx, wy), q) < 900 for q in pp):
            continue
        pp.append((wx, wy))
    for wx, wy in pp:
        tree(tc, shc, wx, wy, rnd.uniform(260, 360), "green", rnd)
    # duvar / set çizgileri (ince koyu gri), korkuluklar, merdiven
    c.set_line_join(cairo.LINE_JOIN_ROUND)
    for pts, cl, lay, sb in d["lines"]:
        if sb == "ARAZİYOLLAR_2":
            setc(c, hx("#A6A6A2")); c.set_line_width(max(6, 1.0 / S))
        elif lay in ("0_IFC_Elevation_5", "0_IFC_Elevation_4", "2_IFC_Wall"):
            setc(c, hx("#55575A")); c.set_line_width(max(12, 2.0 / S))
        elif lay == "0_IFC_Elevation_3":
            setc(c, hx("#B0ADA6")); c.set_line_width(max(4, 0.7 / S))
        elif lay in ("1_IFC_Stair",):
            setc(c, hx("#8E8C87")); c.set_line_width(max(5, 0.8 / S))
        else:
            setc(c, hx("#8E8C87")); c.set_line_width(max(6, 0.9 / S))
        path_pts(c, pts, cl); c.stroke()
    # araçlar
    cm_ = ctx_mask(W, H, mat, stroke_lines(d["cars"], 6))
    car_sil = ndimage.binary_fill_holes(cm_)
    paint_alpha(blur_alpha(car_sil, px(30), px(25), px(25), 0.28) * ~car_sil, (0, 0, 0))
    paint_mask(car_sil, hx("#F1F1EF"))
    setc(c, hx("#9C9C9A")); c.set_line_width(4)
    for pts, cl in d["cars"]:
        path_pts(c, pts, cl); c.stroke()
    # parsel sınırı
    c.set_line_width(max(14, 2.4 / S)); setc(c, hx("#6E8A6C")); c.set_dash([120, 60, 20, 60])
    path_pts(c, d["parcel"]); c.stroke(); c.set_dash([])
    # yapı gölgeleri
    def poly_paths(cc, geom):
        geoms = [geom] if geom.geom_type == "Polygon" else list(geom.geoms)
        for gg in geoms:
            if gg.geom_type != "Polygon":
                continue
            path_pts(cc, list(gg.exterior.coords))
            for h in gg.interiors:
                path_pts(cc, list(h.coords))
    roof_masks = {}
    for b, (fo, rg) in roofs.items():
        # çatı dış çizgisi: en büyük kapalı poligon
        best = None
        for pts, cl, lay in rg:
            if cl and len(pts) > 3:
                try:
                    P = Polygon(pts).buffer(0)
                except Exception:
                    continue
                if best is None or P.area > best.area:
                    best = P
        shape = best if best is not None else fo
        if fo is not None and best is not None:
            shape = unary_union([best, fo.buffer(0)])
        roof_masks[b] = (shape, best)
    allroof = ctx_mask(W, H, mat, lambda cc: ([poly_paths(cc, v[0]) for v in roof_masks.values()], cc.fill()))
    # ağaç gölgesi + ağaç
    sa = surf_to_np(sh)[..., 3]
    paint_alpha(blur_alpha(sa > 0, px(80), strength=0.20), (0, 0, 0))
    paint_alpha(blur_alpha(allroof, px(90), px(160), px(160), 0.42) * ~allroof, (0, 0, 0))
    for b, (shape, best) in roof_masks.items():
        fo = roofs[b][0]
        # zemin kat izi (teras vb.) açık ton
        if fo is not None and not fo.is_empty:
            poly_paths(c, fo); setc(c, hx("#E8E6E1")); c.fill()
        if best is not None:
            bx0_, by0_, bx1_, by1_ = best.bounds
            gr = cairo.LinearGradient(bx0_, by1_, bx1_, by0_)
            gr.add_color_stop_rgba(0, *hx("#C9C9C6")); gr.add_color_stop_rgba(1, *hx("#B3B3B0"))
            poly_paths(c, best); c.set_source(gr); c.fill()
        for pts, cl, lay in roofs[b][1]:
            if lay.startswith(("0_IFC_Text", "0_IFC_Notation", "0_IFC_Dimension", "0_IFC_Grid")):
                continue
            setc(c, hx("#8D8D8A")); c.set_line_width(max(5, 0.8 / S))
            path_pts(c, pts, cl); c.stroke()
        if best is not None:
            poly_paths(c, best); setc(c, hx("#5F5F5D")); c.set_line_width(max(10, 1.6 / S)); c.stroke()
    c.save(); c.identity_matrix(); c.set_source_surface(trees, 0, 0); c.paint(); c.restore()
    draw_labels(c, d, roof_masks, olcek)
    if DEBUG:
        pal = np.array([[243, 242, 239], [180, 220, 170], [230, 200, 150], [150, 150, 150], [200, 180, 140], [120, 120, 120], [150, 230, 150], [230, 230, 255]], np.uint8)
        from PIL import Image as _I
        _I.fromarray(pal[cmap]).save(DEBUG)
    return dict(surf=surf, ext=(X0, Y0, X1, Y1), S=S, texts=d["texts"], roofs=roof_masks, parcel=par, mat=mat)


BLOK_INFO = dict(A=("A BLOK", "1BK+Z+1N = 3 KAT", "±0.00 = 172.95  (SUBASMAN +1.20 = 174.15)"),
                 B=("B BLOK", "2BK+Z = 3 KAT", "±0.00 = 174.15"),
                 C=("C BLOK", "1BK+Z = 2 KAT", "±0.00 = 174.36"),
                 D=("D BLOK", "1BK+Z+1N = 3 KAT", "±0.00 = 167.25"))


def draw_labels(c, d, roofs, olcek):
    f = olcek / 100.0          # 1 mm kağıt = f*10 cm
    mmw = lambda v: v * f * 10
    # kotlar (DXF kot yazıları)
    seen = []
    for t in d["texts"]:
        if "SOKAK" in t["s"].upper():
            L = len(t["s"]) * mmw(2.6) * 0.75
            x0_ = t["x"] + len(t["s"]) * t["h"] * 0.3
            for k_ in range(-3, 4):
                seen.append((x0_ + k_ * L / 6, t["y"]))
    for t in d["texts"]:
        s = t["s"].strip()
        ok = False
        if t["sub"] == "VP_SETLER" and re.fullmatch(r"\d{3}\.\d{2}", s):
            ok = True; val = "+" + s
        elif t["sub"] == "BLOK KOSE KOTLARI" and re.fullmatch(r"\+\d{3}\.\d{2}", s):
            ok = True; val = s
        if not ok:
            continue
        x, y = t["x"], t["y"]
        if any(math.dist((x, y), q) < mmw(9) for q in seen):
            continue
        seen.append((x, y))
        tri = mmw(0.9)
        c.move_to(x, y); c.line_to(x - tri * 0.7, y + tri); c.line_to(x + tri * 0.7, y + tri); c.close_path()
        setc(c, C["white"]); c.fill_preserve(); c.set_line_width(mmw(0.12)); setc(c, C["text2"]); c.stroke()
        wtext(c, x + tri, y + tri * 1.35, val, mmw(1.7), anchor="l", color=C["text2"], halo=(C["white"], mmw(0.5)))
    # yol adları
    for t in d["texts"]:
        s = t["s"].strip().upper()
        if "SOKAK" in s:
            wtext(c, t["x"] + len(s) * t["h"] * 0.3, t["y"], s, mmw(2.6), color=hx("#7A7A76"), track=mmw(0.6))
    # site girişleri
    for t in d["texts"]:
        s = t["s"].replace("\n", " ").strip().upper()
        if s in ("ARAÇ GİRİŞİ", "YAYA GİRİŞİ", "KAPALI OTOPARK GİRİŞİ"):
            x = t["x"] + len(s) * t["h"] * 0.25
            wtext(c, x, t["y"], s, mmw(2.0), bold=True, color=C["red"], halo=(C["white"], mmw(0.6)))
    # bina girişleri (planlardaki giriş okları)
    for b, pts in ENTR.items():
        g = CORES.get(b)
        for (x, y) in pts:
            r = mmw(1.5)
            ang = math.atan2(g.centroid.y - y, g.centroid.x - x) if g is not None else 0
            c.save(); c.translate(x, y); c.rotate(ang)
            c.move_to(r * 0.7, 0); c.line_to(-r * 0.7, r * 0.8); c.line_to(-r * 0.7, -r * 0.8); c.close_path()
            setc(c, C["red"]); c.fill(); c.restore()
    # blok adları
    for b, (shape, best) in roofs.items():
        g = best if best is not None else shape
        if g is None:
            continue
        cx, cy = g.centroid.x, g.centroid.y
        name, kat, kot = BLOK_INFO[b]
        wtext(c, cx, cy + mmw(1.6), name, mmw(4.2), bold=True, color=C["text"], halo=(hx("#C2C2BF"), mmw(0.8)))
        wtext(c, cx, cy - mmw(2.6), kat, mmw(2.0), color=C["text"], halo=(hx("#C2C2BF"), mmw(0.6)))
        wtext(c, cx, cy - mmw(5.4), kot, mmw(1.8), color=C["text"], halo=(hx("#C2C2BF"), mmw(0.6)))
