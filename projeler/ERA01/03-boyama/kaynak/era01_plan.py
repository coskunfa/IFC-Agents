# -*- coding: utf-8 -*-
"""ERA01 kat planı boyama motoru (PAFTA, v01) - konsept gri stil, DNM01 dili.

Geometri DXF'ten birebir alınır (duvar, kolon/perde, mahal poligonu 0_IFC_Area, brüt poligonu,
kapı, pencere, merdiven, mobilya, şaft). Duvar poşesi: mahal poligonları ile duvar/kolon/brüt
çizgileri arasındaki kapalı bölgeler (raster bileşen analizi); kapı boşluğu, pencere ve
asansör/boşluk bileşenleri ayrı sınıflanır. Hiçbir geometri kaydırılmaz.
"""
import math, random, re
from decimal import Decimal

import cairo
import numpy as np
from scipy import ndimage
from shapely.geometry import Polygon, LineString, Point
from shapely.ops import polylabel, unary_union

from era01_ortak import *  # noqa

DATA = load_geo()
GEO_ALL, TOPS = DATA["geo"], DATA["tops"]

DEBUG = None
NORTH = dict(A=21.29, B=21.29, C=291.29, D=314.94)   # pafta kuzey sembolü dönüşü (CCW, derece)

WALL_L = ("2_IFC_Wall",)
COL_L = ("1_IFC_Concrete_Section",)
WIN_L = ("3_IFC_Window",)
DOOR_L = ("1_IFC_Door", "2_IFC_Door")
STAIR_L = ("1_IFC_Stair", "1_IFC_Stair_Concrete", "2_IFC_Handrail")
SHAFT_L = ("5_IFC_Mechanical_Shaft",)
EXTERIOR_WORDS = ("TERAS", "BALKON", "BAHÇE", "BAHCE")


def tcen(t):
    b = t["bb"]
    return ((b[0] + b[2]) / 2, (b[1] + b[3]) / 2)


def floor_items(k):
    f = k["frame"]
    sel = set(t["i"] for t in TOPS if t["bb"] and t["name"] in k["ins"]
              and f[0] < tcen(t)[0] < f[2] and f[1] < tcen(t)[1] < f[3])
    lv = set(t["i"] for t in TOPS if t["name"] == "0_IFC_NOTATION_LEVEL_200" and f[0] < t["x"] < f[2] and f[1] < t["y"] < f[3])
    items, levels = [], []
    def inside(g):
        if g["t"] == "T":
            x, y = g["x"], g["y"]
        else:
            pts = g["pts"] if g["t"] != "H" else [p for l in g["loops"] for p in l]
            x = (min(p[0] for p in pts) + max(p[0] for p in pts)) / 2
            y = (min(p[1] for p in pts) + max(p[1] for p in pts)) / 2
        return f[0] < x < f[2] and f[1] < y < f[3]
    for g in GEO_ALL:
        if g["top"] in sel and inside(g):
            items.append(g)
        elif g["top"] in lv and g["t"] == "T" and g["txt"].strip():
            levels.append(g)
    return items, levels


def clean_txt(s):
    s = s.replace("%%P", "±").replace("%%p", "±").replace("\\P", " ").strip()
    return re.sub(r"\s+", " ", s)


def room_kind(n):
    u = n.upper()
    if any(w in u for w in ("BANYO", "WC", "DUŞ", "DUS", "HAMAM", "SAUNA", "ÇAMAŞIR", "CAMASIR", "SOYUNMA", "LAVABO")):
        return "wet"
    if "MUTFAK" in u and "SALON" not in u:
        return "kitchen"
    if any(w in u for w in ("KORİDOR", "KORIDOR", "HOL", "ANTRE", "GİRİŞ", "GIRIS", "SAHANLIK")):
        return "hall"
    if "MERDİVEN" in u or "MERDIVEN" in u:
        return "stair"
    if "ASANSÖR" in u:
        return "lift"
    if "OTOPARK" in u or "GARAJ" in u:
        return "park"
    if any(w in u for w in ("TEKNİK", "TEKNIK", "DEPO", "KAZAN", "SIĞINAK", "SIGINAK", "M.K.A", "MKA", "MÜDAHALE", "ŞAFT")):
        return "tech"
    if any(w in u for w in EXTERIOR_WORDS):
        return "terrace"
    return "dry"


def is_number(s):
    return re.fullmatch(r"[0-9]+[.,][0-9]+", s.strip()) is not None


# ------------------------------------------------------------------ toplama
def collect(k):
    items, levels = floor_items(k)
    d = dict(areas=[], brut=[], walls=[], cols=[], colh=[], wins=[], doors=[], door_polys=[], stairs=[], shafts=[],
             furn=[], furn_closed=[], cars=[], car_closed=[], furn_hatch=[], pool=[], solid=[], names=[], ok=[], levels=levels)
    for g in items:
        lay, t = g["lay"], g["t"]
        chain = g["blk"]
        if t == "H":
            if lay == "0_IFC_Hatch_Structure":
                d["colh"] += g["loops"]
                d.setdefault("colhg", []).append(g["loops"])
            elif "OK" in chain:
                d["ok"] += g["loops"]
            elif lay.startswith("6_IFC_"):
                if g["solid"]:
                    d["furn_hatch"] += g["loops"]
            elif g["pat"] == "FLEX" or lay == "0_IFC_Hatch_2":
                d["pool"] += g["loops"]
            elif g["solid"] and lay != "2_IFC_Wall":
                d["solid"].append((lay, g["loops"], chain[-1]))
            continue
        if t == "T":
            if "ALAN" in chain[0].upper() and "BRUT" not in chain[0].upper():
                d["names"].append(g)
            continue
        pts = g["pts"]
        if lay == "0_IFC_Area" and t == "P" and len(pts) > 2:
            d["areas"].append(pts)
        elif lay == "0_IFC_Brüt_Alan" and len(pts) > 2:
            d["brut"].append(pts)
        elif lay in WALL_L:
            d["walls"].append((pts, t == "P"))
        elif lay in COL_L:
            d["cols"].append(pts)
        elif lay in WIN_L:
            d["wins"].append((pts, t == "P"))
            d.setdefault("wingrp", {}).setdefault((g["top"],) + tuple(chain), []).extend(pts)
        elif lay in DOOR_L:
            d["doors"].append((pts, t == "P", lay, g.get("ty")))
            d.setdefault("doorgrp", {}).setdefault((g["top"],) + tuple(chain), []).extend(pts)
        elif lay in STAIR_L:
            d["stairs"].append((pts, t == "P"))
        elif lay in SHAFT_L:
            d["shafts"].append((pts, t == "P"))
        elif lay == "6_IFC_Car":
            d["cars"].append((pts, t == "P"))
        elif lay.startswith("6_IFC_"):
            d["furn"].append((pts, t == "P"))
    return d


def rooms_from(d, k):
    """Mahal poligonları + DXF ad yazıları -> oda listesi (ad, alan, poligon, etiket noktası)."""
    rooms = []
    names = [(clean_txt(n["txt"]), n["x"], n["y"], n["h"]) for n in d["names"] if clean_txt(n["txt"])]
    used = set()
    for pts in d["areas"]:
        try:
            poly = Polygon(pts).buffer(0)
        except Exception:
            continue
        if poly.is_empty or poly.area < 2000:  # < 0.2 m2
            continue
        cands = []
        for j, (s, x, y, h) in enumerate(names):
            if is_number(s) or len(s) < 2 or s.upper().startswith(("DÖŞEME", "DOSEME", "TAVAN", "M²", "M2", "DUVAR")):
                continue
            if poly.contains(Point(x + len(s) * h * 0.28, y)) or poly.contains(Point(x, y)):
                cands.append((j, s, x, y, h))
        if cands:
            j, s, x, y, h = max(cands, key=lambda q: q[4])
            used.add(j)
            lp = Point(x + len(s) * h * 0.30, y - h * 0.3)
            if not poly.buffer(-10).contains(lp):
                lp = polylabel(poly if poly.geom_type == "Polygon" else max(poly.geoms, key=lambda p: p.area), 2.0)
        else:
            s = "MAHAL"
            pg = poly if poly.geom_type == "Polygon" else max(poly.geoms, key=lambda p: p.area)
            lp = polylabel(pg, 2.0)
        a = poly.area / 1e4
        s = re.sub(r"^E\.(?=\S)", "E. ", s.strip())
        rooms.append(dict(name=s.upper(), area=a, area_r=area_dec(a), poly=poly, lp=(lp.x, lp.y), kind=room_kind(s)))
    return rooms


# ------------------------------------------------------------------ ana çizim
def render_plan(k, olcek=100, txt=1.0, seed=11, band=True):
    rnd = random.Random(seed)
    S = PXMM * 100.0 / olcek / 10.0        # px / cm
    d = collect(k)
    rooms = rooms_from(d, k)
    k["_added"] = terrace_furniture(rooms, d)
    # sınırlar
    pts_all = [p for pts in d["areas"] for p in pts] + [p for w, _ in d["walls"] for p in w] + \
              [p for pts in d["cols"] for p in pts] + [p for pts in d["brut"] for p in pts]
    xs, ys = [p[0] for p in pts_all], [p[1] for p in pts_all]
    pad = 275 if (k["tip"] == "zemin" and band) else (135 if k["tip"] == "bodrum" and band else 80)
    X0, Y0, X1, Y1 = min(xs) - pad, min(ys) - pad, max(xs) + pad, max(ys) + pad
    W, H = int(math.ceil((X1 - X0) * S)), int(math.ceil((Y1 - Y0) * S))
    mat = cairo.Matrix(S, 0, 0, -S, -X0 * S, Y1 * S)
    px = lambda cm: cm * S

    def fill_polys(polys):
        def f(c):
            for pts in polys:
                path_pts(c, pts)
            c.set_fill_rule(cairo.FILL_RULE_WINDING); c.fill()
        return f

    def stroke_lines(lines, lw):
        def f(c):
            c.set_line_width(lw)
            c.set_line_cap(cairo.LINE_CAP_SQUARE)
            for pts, cl in lines:
                path_pts(c, pts, cl)
                c.stroke()
        return f

    room_polys = []
    for r in rooms:
        geoms = [r["poly"]] if r["poly"].geom_type == "Polygon" else list(r["poly"].geoms)
        for g in geoms:
            room_polys.append(list(g.exterior.coords))
    rooms_m = ctx_mask(W, H, mat, fill_polys(room_polys))
    brut_m = ctx_mask(W, H, mat, fill_polys(d["brut"])) if d["brut"] else np.zeros((H, W), bool)
    blw = max(1.2, 2.2 / S)
    barrier_lines = [(w, cl) for w, cl in d["walls"]] + [(p, True) for p in d["cols"]] + \
                    [(l, True) for l in d["colh"]]
    barrier = ctx_mask(W, H, mat, stroke_lines(barrier_lines, blw))
    def fill_hatches(c):
        for pts in d["cols"]:
            path_pts(c, pts)
        c.set_fill_rule(cairo.FILL_RULE_WINDING); c.fill()
        c.set_fill_rule(cairo.FILL_RULE_EVEN_ODD)
        for loops in d.get("colhg", []):
            for l in loops:
                path_pts(c, l)
            c.fill()
    cols_m = ctx_mask(W, H, mat, fill_hatches)
    # aday bölge: mahaller + brüt, 60 cm genişletilmiş
    base = rooms_m | brut_m
    dist_out = ndimage.distance_transform_edt(~base)
    cand = dist_out < px(60)
    free = cand & ~rooms_m & ~barrier & ~cols_m
    lab, n = ndimage.label(free)
    edge = ndimage.binary_dilation(~cand, iterations=2) & free
    ext_ids = set(np.unique(lab[edge])) - {0}
    doorm = ctx_mask(W, H, mat, stroke_lines([(p, cl) for p, cl, _, _ in d["doors"]], max(0.6, 1.0 / S)))
    winm = ctx_mask(W, H, mat, stroke_lines(d["wins"], max(0.6, 1.0 / S)))
    near_bar = ndimage.binary_dilation(barrier, iterations=2)
    doorm &= ~near_bar
    winm &= ~near_bar
    idx = np.arange(n + 1)
    dcount = ndimage.sum(doorm, lab, idx)
    wcount = ndimage.sum(winm, lab, idx)
    thick = ndimage.distance_transform_edt(free) > px(33)
    thick_ids = set(np.unique(lab[thick])) - {0}
    cls = np.zeros(n + 1, np.uint8)   # 0 yok,1 duvar,2 boşluk(kapı),3 pencere,4 asansör/boşluk,5 dış
    for i in range(1, n + 1):
        if i in ext_ids:
            cls[i] = 5
        elif i in thick_ids:
            cls[i] = 4
        elif dcount[i] >= 4:
            cls[i] = 2
        elif wcount[i] >= 4:
            cls[i] = 3
        else:
            cls[i] = 1
    cmap = cls[lab]
    # kapı açıklığı dikdörtgenleri (yay merkezi = menteşe, kapalı uç = kanada uzak uç)
    leaf_pts = [p for pts, cl, lay, ty in d["doors"] if lay == "2_IFC_Door" for p in pts]
    leaf_arr = np.array(leaf_pts) if leaf_pts else np.zeros((0, 2))
    drects = []
    for pts, cl, lay, ty in d["doors"]:
        if ty != "ARC" or len(pts) < 3:
            continue
        a, m_, b = np.array(pts[0]), np.array(pts[len(pts) // 2]), np.array(pts[-1])
        cen = circumcenter(a, m_, b)
        if cen is None:
            continue
        r = float(np.linalg.norm(a - cen))
        if r < 30 or r > 260:
            continue
        def dleaf(q):
            return float(np.min(np.linalg.norm(leaf_arr - q, axis=1))) if len(leaf_arr) else 0.0
        best = None
        for closed in (a, b):
            u = (closed - cen) / r
            v = np.array([-u[1], u[0]])
            p0 = cen - u * 3
            p1 = cen + u * (r + 3)
            hits = 0
            for ti in np.linspace(0.1, 0.9, 9):
                for tj in np.linspace(-30, 30, 7):
                    q = cen + u * (r * ti) + v * tj
                    qx, qy = int((q[0] - X0) * S), int((Y1 - q[1]) * S)
                    if 0 <= qx < W and 0 <= qy < H and cmap[qy, qx] == 2:
                        hits += 1
            score = hits + (0.5 if dleaf(closed) >= dleaf(a if closed is b else b) else 0)
            if best is None or score > best[0]:
                best = (score, [tuple(p0 + v * 38), tuple(p1 + v * 38), tuple(p1 - v * 38), tuple(p0 - v * 38)])
        drects.append(best[1])
    drect_m = ctx_mask(W, H, mat, fill_polys(drects)) if drects else np.zeros((H, W), bool)
    wrects = []
    for key, pts in d.get("wingrp", {}).items():
        xs_ = [q[0] for q in pts]; ys_ = [q[1] for q in pts]
        wrects.append([(min(xs_) - 2, min(ys_) - 2), (max(xs_) + 2, min(ys_) - 2), (max(xs_) + 2, max(ys_) + 2), (min(xs_) - 2, max(ys_) + 2)])
    wrect_m = ctx_mask(W, H, mat, fill_polys(wrects)) if wrects else np.zeros((H, W), bool)
    dg = []
    for key, pts in d.get("doorgrp", {}).items():
        xs_ = [q[0] for q in pts]; ys_ = [q[1] for q in pts]
        dg.append([(min(xs_) - 3, min(ys_) - 3), (max(xs_) + 3, min(ys_) - 3), (max(xs_) + 3, max(ys_) + 3), (min(xs_) - 3, max(ys_) + 3)])
    dg_m = ctx_mask(W, H, mat, fill_polys(dg)) if dg else np.zeros((H, W), bool)
    door_part = (cmap == 2) & ~(drect_m | dg_m)
    cmap = np.where(door_part, 1, cmap)
    win_part = (cmap == 3) & ~wrect_m
    cmap = np.where(win_part, 1, cmap)
    if DEBUG:
        dbg = np.zeros((H, W, 3), np.uint8) + 255
        pal = np.array([[255,255,255],[60,60,60],[255,160,0],[0,150,255],[200,0,200],[180,230,180]], np.uint8)
        dbg = pal[cmap]
        dbg[rooms_m] = [230,230,230]
        dbg[barrier] = [255,0,0]
        dbg[doorm] = [0,200,0]
        dbg[drect_m & ~rooms_m] = (dbg[drect_m & ~rooms_m] * 0.6).astype(np.uint8)
        from PIL import Image as _I
        _I.fromarray(dbg).save(DEBUG)
    wall_m = cmap == 1
    wall_m |= barrier & ndimage.binary_dilation(wall_m, iterations=3) & ~rooms_m
    open_m = cmap == 2
    win_m = cmap == 3
    void_m = cmap == 4
    bld = rooms_m | wall_m | open_m | win_m | void_m | cols_m | barrier & ndimage.binary_dilation(rooms_m, iterations=3)
    foot = ndimage.binary_fill_holes(bld)
    # mobilya silüeti
    flw = max(0.8, 1.6 / S)
    fl = ctx_mask(W, H, mat, stroke_lines(d["furn"], flw))
    filled = ndimage.binary_fill_holes(fl) & ~fl
    fl_lab, fn = ndimage.label(filled)
    if fn:
        sizes = ndimage.sum(filled, fl_lab, np.arange(fn + 1))
        okc = sizes < (8e4 * S * S)
        okc[0] = False
        filled = okc[fl_lab]
    furn_sil = filled | fl
    cl_ = ctx_mask(W, H, mat, stroke_lines(d["cars"], flw))
    cf = ndimage.binary_fill_holes(cl_) & ~cl_
    cfl, cn = ndimage.label(cf)
    if cn:
        sz = ndimage.sum(cf, cfl, np.arange(cn + 1)); okc = sz < (13e4 * S * S); okc[0] = False
        cf = okc[cfl]
    car_sil = cf | cl_

    # ---------------- çizim yüzeyi
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    c = cairo.Context(surf)
    c.set_matrix(mat)

    def paint_mask(mask, col):
        c.save(); c.identity_matrix()
        c.set_source_surface(mask_to_surf(mask, col), 0, 0); c.paint(); c.restore()

    def paint_alpha(alpha, rgb):
        c.save(); c.identity_matrix()
        c.set_source_surface(alpha_surf(alpha, rgb), 0, 0); c.paint(); c.restore()

    entr = []
    for loop in d["ok"]:
        P = Polygon(loop)
        if P.area <= 0:
            continue
        cx, cy = P.centroid.x, P.centroid.y
        pts = loop[:-1] if loop[0] == loop[-1] else loop
        if len(pts) >= 3:
            # en uzun kenarın karşısındaki köşe = uç
            best = None
            for i in range(len(pts)):
                a, b = pts[i], pts[(i + 1) % len(pts)]
                L = math.dist(a, b)
                if best is None or L > best[0]:
                    best = (L, a, b, pts[(i + 2) % len(pts)])
            L, a, b, apex = best
            mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
            ang = math.atan2(apex[1] - my, apex[0] - mx)
            entr.append((cx, cy, ang))

    # zemin: peyzaj bandı / bodrum: toprak bandı
    if band and k["tip"] in ("zemin", "bodrum"):
        dist_f = ndimage.distance_transform_edt(~foot)
        if k["tip"] == "zemin":
            bandm = (dist_f < px(250)) & ~foot
            # yumuşak köşe
            paint_mask(bandm, C["grass"])
            g2 = bandm & (dist_f > px(170))
            paint_alpha(blur_alpha(g2, px(40), strength=0.35), C["grass2"][:3])
            terr_polys = [list(r["poly"].exterior.coords) for r in rooms
                          if "TERAS" in r["name"] and r["poly"].geom_type == "Polygon"]
            low = None
            if terr_polys and k.get("alcak"):
                terr_m = ctx_mask(W, H, mat, fill_polys(terr_polys))
                core_m = foot & ~terr_m
                d_core = ndimage.distance_transform_edt(~core_m)
                d_terr = ndimage.distance_transform_edt(~terr_m)
                low = bandm & (d_terr < d_core - px(20))
                paint_mask(low, hx("#C9D1C5"))
                paint_alpha(blur_alpha(low & (dist_f < px(60)), px(25), strength=0.30), (0.35, 0.38, 0.33))
                yy_, xx_ = np.nonzero(low & (dist_f > px(150)))
                if len(yy_):
                    j = np.argmin(yy_)
                    k["_lowlabel"] = (X0 + xx_[j] / S, Y1 - yy_[j] / S - 60)
            paint_alpha(blur_alpha(foot, px(18), px(10), px(10), 0.30) * bandm, (0, 0, 0))
            # giriş yolu
            for (ex, ey, ang) in entr:
                ux, uy = math.cos(ang), math.sin(ang)
                # ok binaya doğru: yol ok'un gerisinde
                c.save(); c.translate(ex, ey); c.rotate(ang)
                c.rectangle(-300, -85, 300, 170); setc(c, C["pave"]); c.fill()
                c.set_line_width(0.8); setc(c, C["paveb"])
                for xx in range(-300, 1, 60):
                    c.move_to(xx, -85); c.line_to(xx, 85); c.stroke()
                c.restore()
            # ağaçlar
            sh = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); shc = cairo.Context(sh); shc.set_matrix(mat)
            trees = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); tc = cairo.Context(trees); tc.set_matrix(mat)
            ring = (dist_f > px(110)) & (dist_f < px(150))
            yy, xx = np.nonzero(ring[::7, ::7])
            pts_ring = list(zip(xx * 7, yy * 7))
            rnd.shuffle(pts_ring)
            placed = []
            for (pxx, pyy) in pts_ring:
                wx, wy = X0 + pxx / S, Y1 - pyy / S
                if any(math.dist((wx, wy), (e[0], e[1])) < 380 for e in entr):
                    continue
                if any(math.dist((wx, wy), q) < 520 for q in placed):
                    continue
                placed.append((wx, wy))
            for i, (wx, wy) in enumerate(placed):
                if i % 3 == 2:
                    tree(tc, shc, wx, wy, rnd.uniform(42, 55), "flower", rnd)
                else:
                    tree(tc, shc, wx, wy, rnd.uniform(95, 125), "green", rnd)
            sa = surf_to_np(sh)[..., 3]
            paint_alpha(blur_alpha(sa > 0, px(12), strength=0.22) * bandm, (0, 0, 0))
            c.save(); c.identity_matrix()
            # ağaçları bant ile kırp
            tarr = surf_to_np(trees)
            tarr = (tarr.astype(np.float32) * (bandm | (dist_f > 0) & (dist_f < px(250)))[..., None]).astype(np.uint8)
            c.set_source_surface(np_to_surf(tarr), 0, 0); c.paint(); c.restore()
            k["_trees"] = placed
        else:
            bandm = (dist_f < px(110)) & ~foot
            paint_mask(bandm, C["earth"])

    # mahal dolguları (hafif gradyan)
    for r in rooms:
        col = C[r["kind"]] if r["kind"] in C else C["dry"]
        geoms = [r["poly"]] if r["poly"].geom_type == "Polygon" else list(r["poly"].geoms)
        for g in geoms:
            bx0, by0, bx1, by1 = g.bounds
            gr = cairo.LinearGradient(bx0, by1, bx1, by0)
            gr.add_color_stop_rgba(0, *shade(col, 1.025))
            gr.add_color_stop_rgba(1, *shade(col, 0.975))
            path_pts(c, list(g.exterior.coords))
            for hole in g.interiors:
                path_pts(c, list(hole.coords))
            c.set_fill_rule(cairo.FILL_RULE_EVEN_ODD)
            c.set_source(gr); c.fill()
    c.set_fill_rule(cairo.FILL_RULE_WINDING)
    # havuz suyu
    if d["pool"]:
        for loop in d["pool"]:
            path_pts(c, loop)
        bx = [p[0] for l in d["pool"] for p in l]; by = [p[1] for l in d["pool"] for p in l]
        gr = cairo.LinearGradient(min(bx), max(by), max(bx), min(by))
        gr.add_color_stop_rgba(0, *C["pool"]); gr.add_color_stop_rgba(1, *C["poolb"])
        c.set_source(gr); c.fill()
    paint_mask(open_m, C["sill"])
    paint_mask(void_m, C["lift"])
    # gölgeler (duvar + mobilya)
    paint_alpha(blur_alpha(wall_m | cols_m, px(4), px(3), px(3), 0.30) * ~(wall_m | cols_m), (0, 0, 0))
    paint_alpha(blur_alpha(furn_sil | car_sil, px(5), px(4), px(4), 0.26) * ~(furn_sil | car_sil), (0, 0, 0))
    # mobilya
    paint_mask(furn_sil, C["white"])
    paint_mask(car_sil, hx("#F1F1EF"))
    for loop in d["furn_hatch"]:
        path_pts(c, loop)
    setc(c, hx("#E3D3CC")); c.fill()
    c.set_line_join(cairo.LINE_JOIN_ROUND)
    c.set_line_width(max(0.7, 1.15 / S)); setc(c, C["line"])
    for pts, cl in d["furn"]:
        path_pts(c, pts, cl); c.stroke()
    c.set_line_width(max(0.7, 1.15 / S)); setc(c, hx("#9C9C9A"))
    for pts, cl in d["cars"]:
        path_pts(c, pts, cl); c.stroke()
    # merdiven
    c.set_line_width(max(0.7, 1.1 / S)); setc(c, C["line2"])
    for pts, cl in d["stairs"]:
        path_pts(c, pts, cl); c.stroke()
    # pencere
    paint_mask(win_m, C["white"])
    c.set_line_width(max(0.6, 1.0 / S)); setc(c, hx("#7F8A92"))
    for pts, cl in d["wins"]:
        path_pts(c, pts, cl); c.stroke()
    # duvar / kolon
    paint_mask(wall_m, C["wall"])
    c.set_line_width(max(0.8, 1.6 / S)); setc(c, C["wall"])
    for pts, cl in d["walls"]:
        path_pts(c, pts, cl); c.stroke()
    paint_mask(cols_m, C["col"])
    # şaftlar
    for pts, cl in d["shafts"]:
        if cl and len(pts) >= 4:
            path_pts(c, pts); setc(c, hx("#F4F4F2")); c.fill_preserve()
            c.set_line_width(max(0.6, 1.0 / S)); setc(c, C["text2"]); c.stroke()
            bx = [p[0] for p in pts]; by = [p[1] for p in pts]
            c.move_to(min(bx), min(by)); c.line_to(max(bx), max(by))
            c.move_to(min(bx), max(by)); c.line_to(max(bx), min(by)); c.stroke()
    # kapılar
    for pts, cl, lay, ty in d["doors"]:
        if ty == "ARC":
            c.set_line_width(max(0.5, 0.9 / S)); setc(c, C["line"])
            path_pts(c, pts, False); c.stroke()
        else:
            path_pts(c, pts, cl)
            if cl and lay == "2_IFC_Door":
                setc(c, C["white"]); c.fill_preserve()
            c.set_line_width(max(0.6, 1.1 / S)); setc(c, hx("#5E5E5C")); c.stroke()

    # zemin teras korkuluğu (teras kenarı, bina dışında kalan kenarlar)
    if k["tip"] == "zemin":
        core = unary_union([r["poly"] for r in rooms if "TERAS" not in r["name"]]).buffer(45)
        for r in rooms:
            if "TERAS" in r["name"] and r["poly"].geom_type == "Polygon":
                for off, lw in ((0, 2.2), (-9, 1.0)):
                    ring = r["poly"].buffer(off).exterior if off else r["poly"].exterior
                    ln = ring.difference(core)
                    segs = [ln] if ln.geom_type == "LineString" else list(getattr(ln, "geoms", []))
                    c.set_line_width(max(lw * 1.0, (1.6 if off == 0 else 0.8) / S)); setc(c, hx("#4A4A4A"))
                    for sg in segs:
                        if sg.geom_type == "LineString" and len(sg.coords) > 1:
                            path_pts(c, list(sg.coords), False); c.stroke()
    if k.get("_lowlabel"):
        lx, ly = k["_lowlabel"]
        lab_ = "ALÇAK BAHÇE  " + k["alcak"]
        c.move_to(lx, ly); c.line_to(lx - 12 * txt, ly + 18 * txt); c.line_to(lx + 12 * txt, ly + 18 * txt); c.close_path()
        setc(c, C["white"]); c.fill_preserve(); c.set_line_width(1.0 * txt); setc(c, C["text"]); c.stroke()
        wtext(c, lx + 16 * txt, ly + 30 * txt, lab_, 15 * txt, anchor="l", color=C["text"])
    # giriş üçgeni
    tri = 55 * txt
    for (ex, ey, ang) in entr:
        c.save(); c.translate(ex, ey); c.rotate(ang)
        c.move_to(tri * 0.6, 0); c.line_to(-tri * 0.6, tri * 0.75); c.line_to(-tri * 0.6, -tri * 0.75); c.close_path()
        setc(c, C["red"]); c.fill(); c.restore()

    # mahal yazıları
    numbered = layout_labels(c, rooms, txt, [(e[0], e[1]) for e in entr])
    # kotlar
    seen = []
    for g in d["levels"]:
        s = clean_txt(g["txt"])
        m = re.match(r"([±+\-]?\d+[.,]\d+)", s)
        if not m:
            continue
        if any(math.dist((g["x"], g["y"]), q) < 150 for q in seen):
            continue
        seen.append((g["x"], g["y"]))
        kx, ky = g["x"], g["y"]
        for r in rooms:
            if abs(r["lp"][0] - kx) < 110 * txt and abs(r["lp"][1] - ky) < 70 * txt:
                ky = r["lp"][1] - 85 * txt
        kv = m.group(1)
        if not kv.startswith(("+", "-", "±")):
            kv = "+" + kv
        c.move_to(kx, ky); c.line_to(kx - 12 * txt, ky + 18 * txt); c.line_to(kx + 12 * txt, ky + 18 * txt); c.close_path()
        setc(c, C["white"]); c.fill_preserve(); c.set_line_width(1.0 * txt); setc(c, C["text"]); c.stroke()
        c.move_to(kx, ky + 18 * txt); c.line_to(kx + 75 * txt, ky + 18 * txt); c.stroke()
        wtext(c, kx + 16 * txt, ky + 30 * txt, kv, 15 * txt, anchor="l", color=C["text"])

    net = sum((r["area_r"] for r in rooms if r["kind"] != "terrace"), Decimal("0.0"))
    ext_ = sum((r["area_r"] for r in rooms if r["kind"] == "terrace"), Decimal("0.0"))
    brut = None
    if d["brut"]:
        bp = [Polygon(p).buffer(0) for p in d["brut"]]
        brut = unary_union(bp).area / 1e4
    foot_area = float(foot.sum()) / (S * S) / 1e4
    surf.flush()
    import era01_ortak as _o
    _o._KEEP.clear()
    return dict(surf=surf, ext=(X0, Y0, X1, Y1), S=S, rooms=rooms, net=net, ext_area=ext_, brut=brut,
                foot_area=foot_area, numbered=numbered, entr=entr, north=NORTH[k["blok"]],
                stats=dict(walls=int(wall_m.sum()), open=int(open_m.sum()), win=int(win_m.sum()), void=int(void_m.sum())))


def circumcenter(a, b, c):
    d = 2 * (a[0] * (b[1] - c[1]) + b[0] * (c[1] - a[1]) + c[0] * (a[1] - b[1]))
    if abs(d) < 1e-9:
        return None
    ux = ((a @ a) * (b[1] - c[1]) + (b @ b) * (c[1] - a[1]) + (c @ c) * (a[1] - b[1])) / d
    uy = ((a @ a) * (c[0] - b[0]) + (b @ b) * (a[0] - c[0]) + (c @ c) * (b[0] - a[0])) / d
    return np.array([ux, uy])


def _hspan(poly, x, y):
    """Etiket noktasından geçen yatay çizginin poligon içindeki genişliği."""
    ln = LineString([(x - 1e5, y), (x + 1e5, y)])
    it = poly.intersection(ln)
    segs = [it] if it.geom_type == "LineString" else list(getattr(it, "geoms", []))
    for sgm in segs:
        if sgm.geom_type != "LineString" or sgm.is_empty or len(sgm.coords) < 2:
            continue
        (a, _), (b, _) = sgm.coords[0], sgm.coords[-1]
        if min(a, b) - 1 <= x <= max(a, b) + 1:
            return abs(b - a)
    return 0


def layout_labels(c, rooms, txt, entr_pts=()):
    """Mahal adı + alanı mahal içine (tek tip yazı boyu). Ad hiçbir biçimde sığmazsa yalnız o mahal
    numaralanır ve paftadaki listeye girer. Yazı kutusu duvardan >= 8 cm içeride, giriş üçgenine binmez."""
    fs_n, fs_a = 24 * txt, 18 * txt
    lh = fs_n * 1.12
    obst = unary_union([Point(x, y).buffer(75 * txt) for x, y in entr_pts]) if entr_pts else None
    numbered = []
    def box(x, y, lines):
        w = max(max(wtext_width(c, l, fs_n, True) for l in lines), wtext_width(c, "000.00 m²", fs_a))
        h = len(lines) * lh + fs_a * 1.3
        return Polygon([(x - w / 2, y - h / 2), (x + w / 2, y - h / 2), (x + w / 2, y + h / 2), (x - w / 2, y + h / 2)]), h
    for r in rooms:
        pg = r["poly"] if r["poly"].geom_type == "Polygon" else max(r["poly"].geoms, key=lambda p: p.area)
        safe = pg.buffer(-8 * txt)
        if obst is not None:
            safe = safe.difference(obst)
        if safe.is_empty:
            safe = None
        variants = [[r["name"]]]
        parts = r["name"].split(" ")
        for i in range(1, len(parts)):
            variants.append([" ".join(parts[:i]), " ".join(parts[i:])])
        cands = [r["lp"]]
        try:
            big = safe if (safe is None or safe.geom_type == "Polygon") else max(safe.geoms, key=lambda p: p.area)
            if big is not None:
                q = polylabel(big, 2.0); cands.append((q.x, q.y))
        except Exception:
            pass
        done = None
        for ls in variants:
            for (x, y) in cands:
                b, h = box(x, y, ls)
                if safe is not None and safe.contains(b):
                    done = (x, y, ls, h); break
            if done:
                break
        if done:
            x, y, ls, h = done
            ytop = y + h / 2 - fs_n * 0.55
            for i, l in enumerate(ls):
                wtext(c, x, ytop - i * lh, l, fs_n, bold=True)
            wtext(c, x, ytop - (len(ls) - 1) * lh - fs_a * 1.3, "%s m²" % fmt_area(r["area"]), fs_a, color=C["text2"])
        else:
            numbered.append(r)
    for i, r in enumerate(sorted(numbered, key=lambda r: (-r["lp"][1], r["lp"][0])), 1):
        r["no"] = i
        pg = r["poly"] if r["poly"].geom_type == "Polygon" else max(r["poly"].geoms, key=lambda p: p.area)
        q = polylabel(pg, 2.0)
        c.arc(q.x, q.y, 15 * txt, 0, 2 * math.pi); setc(c, C["white"], 0.9); c.fill_preserve()
        c.set_line_width(0.8 * txt); setc(c, C["text2"]); c.stroke()
        wtext(c, q.x, q.y, str(i), 17 * txt, bold=True)
    return numbered


def _rect(cx, cy, w, h, ax):
    """ax='x': w yatay; ax='y': w düşey (90° döndürülmüş)."""
    if ax == "y":
        w, h = h, w
    return [(cx - w / 2, cy - h / 2), (cx + w / 2, cy - h / 2), (cx + w / 2, cy + h / 2), (cx - w / 2, cy + h / 2), (cx - w / 2, cy - h / 2)]


def _circle(cx, cy, r, n=28):
    return [(cx + r * math.cos(2 * math.pi * i / n), cy + r * math.sin(2 * math.pi * i / n)) for i in range(n + 1)]


def terrace_furniture(rooms, d):
    """Tefriş kuralı (Teras/bahçe): dış oturma grubu + 6 kişilik dış yemek masası + saksılar.
    Mobilya gerçek ölçüde (3'lü 220x85, tekli 80x80, sehpa 100x60, masa 180x90, sandalye 48x48, saksı Ø60)."""
    added = []
    for r in rooms:
        if "TERAS" not in r["name"] or r["poly"].geom_type != "Polygon" or r["area"] < 20:
            continue
        P = r["poly"]
        inner = P.buffer(-90)
        if inner.is_empty:
            continue
        bx0, by0, bx1, by1 = P.bounds
        ax = "x" if (bx1 - bx0) >= (by1 - by0) else "y"
        L0, L1 = (bx0, bx1) if ax == "x" else (by0, by1)
        T0, T1 = (by0, by1) if ax == "x" else (bx0, bx1)
        tm = (T0 + T1) / 2
        def at(u, v):
            return (u, v) if ax == "x" else (v, u)
        items = []
        # oturma grubu (uzun eksenin %28'i)
        u = L0 + (L1 - L0) * 0.28
        grp = []
        sx, sy = at(u, tm + 105)
        grp += [_rect(sx, sy, 220, 85, ax), _rect(*at(u, tm + 105 + 32), 220, 20, ax)]
        for du in (-150, 150):
            ax2 = "y" if ax == "x" else "x"
            cx_, cy_ = at(u + du, tm)
            grp += [_rect(cx_, cy_, 80, 80, ax), _rect(*at(u + du + (32 if du > 0 else -32), tm), 80, 16, ax2)]
        grp.append(_rect(*at(u, tm), 100, 60, ax))
        items.append(grp)
        # yemek grubu (%72)
        u = L0 + (L1 - L0) * 0.72
        grp = [_rect(*at(u, tm), 180, 90, ax)]
        for du in (-55, 0, 55):
            for dv in (-72, 72):
                grp.append(_rect(*at(u + du, tm + dv), 48, 48, ax))
        grp.append(_circle(*at(u, tm), 12))
        items.append(grp)
        # saksılar (iç köşeler)
        inb = inner.bounds
        for (px_, py_) in ((inb[0], inb[1]), (inb[2], inb[1]), (inb[0], inb[3]), (inb[2], inb[3])):
            items.append([_circle(px_, py_, 30), _circle(px_, py_, 22)])
        exist = []
        for pts, cl in d["furn"]:
            if cl and len(pts) > 3:
                try:
                    q = Polygon(pts).buffer(0)
                    if q.intersects(P):
                        exist.append(q)
                except Exception:
                    pass
        for grp in items:
            ok = all(inner.contains(Polygon(g)) or P.buffer(-30).contains(Polygon(g)) for g in grp)
            ok = ok and not any(Polygon(g).buffer(15).intersects(q) for g in grp for q in exist)
            if ok:
                for g in grp:
                    d["furn"].append((g, True))
                added.append(len(grp))
    return added
