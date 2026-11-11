# ERA01 site model spec generator (HACIM). v04: konsept renderlara gore pencere/cati/malzeme/bahce revizyonu. v03: otopark yarmasi tabani 167.15 (U-v2-1). v02: DENETCI tur 1 duzeltmeleri (H3-H7, U10-U13).
# Input : floors.pkl (era01_model_dxfoku.py ciktisi: kat bazinda brut alan, mahal, kolon, dograma, kapi verisi,
#         blok yerel aks koordinatlari), terrain points (vaziyet plani kotlari).
# Output: spec JSON (solids + component defs + instances, cm, site coords) + rapor JSON.
# Birim cm. Model z = (kot - 160.00 m) * 100. Site x,y = VAZIYET PLANI blok koordinatlari (cm).
import sys, json, math, pickle, re
import numpy as np
from shapely.geometry import Polygon, MultiPolygon, box, Point, LineString
from shapely.ops import unary_union
from shapely.geometry.polygon import orient
from shapely import affinity

FLOORS_PKL, OUT = sys.argv[1], sys.argv[2]
D = pickle.load(open(FLOORS_PKL, "rb"))
Z0 = 160.00  # model datum (m)

# ---------------- PARAMETRELER ----------------
T_EXT, T_INT, CEPHE = 20.0, 10.0, 20.0
KAPLAMA, DOSEME, TAVAN = 10.0, 30.0, 10.0
ROOF_T = 20.0
PARAPET_H = 100.0          # teras korkulugu (dolu parapet), dosemeden
FRAME_B, FRAME_D = 5.0, 6.0
OUTDOOR = ("TERAS",)
AVLU = ("BAHCE",)          # acik avlu (kat bahcesi): brut alanda delik
RAIL_H = 110.0             # teras korkulugu (cam panel)
RAIL_T = 4.0
SKIP_TERR = {("B", "B1")}  # toprak altinda kalan cati-teras (B2 kuzey kismi)
NORTH_ANGLE = 360.0 - 21.29
# ---- v04 konsept parametreleri ----
V4_ROOF_SLOPE = 0.10        # A, B, C: dusuk egimli metal kirma cati (konsept 2, 4, 5)
V4_EAVE_EXTRA = 40.0        # DXF sacak tasmasina ek (110 -> 150 cm)
V4_ROOF_T = 15.0            # ince cati profili
V4_WIN_GROW = 1.6           # pencere genislik carpani (oda cephesi icinde)
V4_PIER = 60.0              # pencereler arasi en az tas paye
V4_ROOM_MARGIN = 30.0       # oda kosesine en az mesafe
WET_KEYS = ("BANYO", "WC", "DUS", "HAMAM", "SAUNA", "LAVABO")
# cephe malzemesi (blok, kat) -> (uzun kenar, kisa kenar); uzun = plan x yonu
FACADE = {("A", "B1"): ("M_CEPHE_TAS", "M_CEPHE_TAS"), ("A", "ZK"): ("M_CEPHE_TAS", "M_CEPHE_AHSAP"), ("A", "K1"): ("M_CEPHE_TAS", "M_CEPHE_AHSAP"),
          ("B", "B2"): ("M_CEPHE_TAS", "M_CEPHE_TAS"), ("B", "B1"): ("M_CEPHE_TAS", "M_CEPHE_TAS"), ("B", "ZK"): ("M_CEPHE_TAS", "M_CEPHE_TAS"),
          ("C", "B1"): ("M_CEPHE_TAS", "M_CEPHE_TAS"), ("C", "ZK"): ("M_CEPHE_AHSAP", "M_CEPHE_AHSAP"),
          ("D", "B1"): ("M_CEPHE_SIVA", "M_CEPHE_SIVA"), ("D", "ZK"): ("M_CEPHE_SIVA", "M_CEPHE_SIVA"), ("D", "K1"): ("M_CEPHE_TAS", "M_CEPHE_TAS")}  # SketchUp North Angle (vaziyet +Y den saat yonunde); gercek kuzey +Y nin 21.29 bati
ISLAK = ("BANYO", "WC", "MUTFAK", "CAMASIR", "HAMAM", "SAUNA", "DUS", "HAVUZ", "LAVABO")
# Blok kat tablosu (DXF kesitlerinden, m). ceil = tavan alt kotu (asma tavan) ; None -> L+2.90
BLOCKS = {
    "A": dict(ort=172.95, floors=[("B1", 170.15, 173.05), ("ZK", 174.15, 177.05), ("K1", 177.65, 180.55)],
              sacak=181.15, mahya=181.88, parapet=None,
              roof_rect=(-150, -900, 2150, 150), rot=0.0, t=(2138.0, 3365.0)),
    "B": dict(ort=174.15, floors=[("B2", 167.15, 169.55), ("B1", 170.15, None), ("ZK", 174.15, 177.05)],
              sacak=177.65, mahya=179.17, parapet=None,
              roof_rect=(-150, -1380, 2150, 150), rot=0.0, t=(4738.0, 3185.0)),
    "C": dict(ort=174.36, floors=[("B1", 170.36, 173.26), ("ZK", 174.36, 177.26)],
              sacak=177.86, mahya=178.75, parapet=None,
              roof_rect=(-150, -900, 1950, 150), rot=90.0, t=(7338.0, 1955.0)),
    "D": dict(ort=167.25, floors=[("B1", 164.25, 166.65), ("ZK", 167.25, 169.65), ("K1", 170.75, 173.65)],
              sacak=174.25, mahya=175.07, parapet=174.75,
              roof_rect=None, roof_size=(965, 1140), rot=None, t=None),
}
KAT_TAG = {"B2": "KAT_B2", "B1": "KAT_B1", "ZK": "KAT_00", "K1": "KAT_01"}

ASCII = str.maketrans("ÇĞİÖŞÜçğıöşü", "CGIOSUcgiosu")
def asc(s):
    s = s.translate(ASCII).upper()
    s = re.sub(r"[^A-Z0-9]+", "_", s).strip("_")
    return s or "MAHAL"
def rnd(v):
    return round(float(v) + 0.0, 2)
def zc(kot):
    return (kot - Z0) * 100.0

# ---------------- geometri yardimcilari ----------------
def parts(g):
    if g is None or g.is_empty: return []
    if isinstance(g, Polygon): return [g]
    out = []
    for p in getattr(g, "geoms", []): out += parts(p)
    return out

def clean(poly):
    poly = poly.buffer(0).simplify(0.5, preserve_topology=True)
    return orient(poly, 1.0)

def prism(poly, h, o, e1, e2, e3):
    poly = clean(poly)
    det = (e1[0]*(e2[1]*e3[2]-e2[2]*e3[1]) - e1[1]*(e2[0]*e3[2]-e2[2]*e3[0]) + e1[2]*(e2[0]*e3[1]-e2[1]*e3[0]))
    rings = [list(poly.exterior.coords)[:-1]] + [list(r.coords)[:-1] for r in poly.interiors]
    verts, faces = [], []
    def P(u, v, w): return [rnd(o[k] + u*e1[k] + v*e2[k] + w*e3[k]) for k in range(3)]
    ib, it = [], []
    for ring in rings:
        b, t = [], []
        for (u, v) in ring: b.append(len(verts)); verts.append(P(u, v, 0))
        for (u, v) in ring: t.append(len(verts)); verts.append(P(u, v, h))
        ib.append(b); it.append(t)
    faces.append(it)
    faces.append([list(reversed(r)) for r in ib])
    for b, t in zip(ib, it):
        n = len(b)
        for i in range(n):
            j = (i + 1) % n
            faces.append([[b[i], b[j], t[j], t[i]]])
    if det < 0:
        faces = [[list(reversed(l)) for l in f] for f in faces]
    return {"v": verts, "f": faces}

def plan_prism(poly, z0, z1):
    return prism(poly, z1 - z0, (0, 0, z0), (1, 0, 0), (0, 1, 0), (0, 0, 1))

solids, defs, insts, groups = [], {}, [], {}
def add(path, name, mat, g):
    g = dict(g); g.update({"p": path, "n": name, "m": mat}); solids.append(g)
def add_poly(path, name, mat, geom, z0, z1, minarea=20):
    ps = [p for p in parts(geom) if p.area > minarea]
    for i, p in enumerate(ps):
        add(path, name if len(ps) == 1 else f"{name}_{i+1}", mat, plan_prism(p, z0, z1))
    return len(ps)

report = {"blocks": {}, "warnings": []}

# ---------------- bilesenler ----------------
def window_def(w, h, wtag=None, htag=None):
    name = f"DGR_{int(round(wtag or w))}x{int(round(htag or h))}"
    if name in defs and abs(defs[name]["info"]["w"] - w) < 1 and abs(defs[name]["info"]["h"] - h) < 1:
        return name
    if name in defs:
        name = f"DGR_{int(round(w))}x{int(round(h))}"
        if name in defs: return name
    n = max(1, int(round(w / 150.0)))
    n = max(1, min(n, int(w // 100)))
    rows = 2 if h > 240 else 1
    if h > 450: rows = 3
    iw = (w - 2*FRAME_B - (n-1)*FRAME_B) / n
    ih = (h - 2*FRAME_B - (rows-1)*FRAME_B) / rows
    panes = []
    for i in range(n):
        for r in range(rows):
            u0 = FRAME_B + i*(iw + FRAME_B); v0 = FRAME_B + r*(ih + FRAME_B)
            panes.append((u0, v0, u0 + iw, v0 + ih))
    frame = box(0, 0, w, h)
    for p in panes: frame = frame.difference(box(*p))
    sol = prism(frame, FRAME_D, (0, 0, 0), (1, 0, 0), (0, 0, 1), (0, 1, 0)); sol["m"] = "M_DOGRAMA_KASA"
    glass = [[[u0, FRAME_D/2, v0], [u1, FRAME_D/2, v0], [u1, FRAME_D/2, v1], [u0, FRAME_D/2, v1]] for (u0, v0, u1, v1) in panes]
    defs[name] = {"solids": [sol], "glass": glass, "info": {"w": w, "h": h, "bolme": n, "kayit": rows - 1}}
    return name

def door_def(w, h, pre="DGR_KAPI"):
    name = f"{pre}_{int(round(w))}x{int(round(h))}"
    if name in defs: return name
    frame = box(0, 0, w, h).difference(box(FRAME_B, 0, w - FRAME_B, h - FRAME_B))
    sol = prism(frame, FRAME_D, (0, 0, 0), (1, 0, 0), (0, 0, 1), (0, 1, 0)); sol["m"] = "M_DOGRAMA_KASA"
    leaf = prism(box(FRAME_B, 0, w - FRAME_B, h - FRAME_B), 4.0, (0, 1.0, 0), (1, 0, 0), (0, 0, 1), (0, 1, 0)); leaf["m"] = "M_DOGRAMA_KASA"
    defs[name] = {"solids": [sol, leaf], "glass": [], "info": {"w": w, "h": h}}
    return name

def col_def(w, d, h):
    name = f"KOLON_{int(round(w))}x{int(round(d))}_H{int(round(h))}"
    if name not in defs:
        s = plan_prism(box(0, 0, w, d), 0, h); s["m"] = "M_TASIYICI"
        defs[name] = {"solids": [s], "glass": [], "info": {"w": w, "d": d, "h": h}}
    return name

# ---------------- kenar seridi (dis duvar / cephe) ----------------
def edges_of(poly):
    po = orient(poly, 1.0)
    out = []
    for ring in [po.exterior] + list(po.interiors):
      c = list(ring.coords)[:-1]
      for i in range(len(c)):
        a, b = np.array(c[i]), np.array(c[(i+1) % len(c)])
        L = float(np.linalg.norm(b - a))
        if L < 1: continue
        d = (b - a) / L
        out.append(dict(a=a, b=b, L=L, d=d, n_in=np.array([-d[1], d[0]])))
    return out

def to_edge(e, pt):
    v = np.array(pt) - e["a"]
    return float(v @ e["d"]), float(v @ e["n_in"])

def edge_rect(e, u0, u1, w0, w1):
    pts = [e["a"] + u*e["d"] + w*e["n_in"] for u, w in [(u0, w0), (u1, w0), (u1, w1), (u0, w1)]]
    return Polygon(pts)

def strips(poly, inward, depth):
    """Kenar seritleri: yatayliga yakin kenarlar koseleri sahiplenir. inward=True dis duvar, False cephe kaplamasi."""
    es = edges_of(poly)
    band = (poly.difference(poly.buffer(-depth, join_style=2)) if inward
            else poly.buffer(depth, join_style=2).difference(poly))
    own = [abs(e["d"][0]) >= abs(e["d"][1]) for e in es]
    rects = []
    for e, o in zip(es, own):
        w0, w1 = (0, depth) if inward else (-depth, 0)
        ext = 0 if inward else depth
        if o: rects.append(edge_rect(e, -ext, e["L"] + ext, w0, w1).intersection(band))
        else: rects.append(edge_rect(e, 0, e["L"], w0, w1).intersection(band))
    # sahip seritler sirayla (dis halka once), cakisma birakmadan
    acc = Polygon(); gs = []
    for r, o in zip(rects, own):
        if o:
            g = r.difference(acc); acc = unary_union([acc, g]); gs.append(g)
        else:
            gs.append(None)
    for i, (r, o) in enumerate(zip(rects, own)):
        if not o:
            g = r.difference(acc); acc = unary_union([acc, g]); gs[i] = g
    out = []
    for e, o, r, g in zip(es, own, rects, gs):
        for p in parts(g):
            if p.area < 50: continue
            us = [to_edge(e, c)[0] for c in p.exterior.coords]
            out.append((e, min(us), max(us), p))
    return out

def elev_panel(path, name, mat, e, ua, ub, w0, w1, z0, z1, openings):
    poly = box(ua, z0, ub, z1)
    for (oa, ob, oz0, oz1) in openings:
        a, b = max(oa, ua), min(ob, ub)
        if b - a > 1 and min(oz1, z1) - max(oz0, z0) > 1:
            poly = poly.difference(box(a, max(oz0, z0), b, min(oz1, z1)))
    o = (float(e["a"][0] + w0*e["n_in"][0]), float(e["a"][1] + w0*e["n_in"][1]), 0.0)
    e1 = (float(e["d"][0]), float(e["d"][1]), 0.0); e2 = (0.0, 0.0, 1.0)
    e3 = (float(e["n_in"][0]), float(e["n_in"][1]), 0.0)
    ps = [p for p in parts(poly) if p.area > 20]
    for i, pp in enumerate(ps):
        add(path, name if len(ps) == 1 else f"{name}_{chr(97+i)}", mat, prism(pp, w1 - w0, o, e1, e2, e3))
    return len(ps)

# ---------------- merdiven ----------------
def stair_mass(path, name, room, z0, z1):
    mr = room.minimum_rotated_rectangle
    c = list(mr.exterior.coords)[:4]
    a, b, d_ = np.array(c[0]), np.array(c[1]), np.array(c[3])
    v1, v2 = b - a, d_ - a
    if np.linalg.norm(v1) < np.linalg.norm(v2): v1, v2 = v2, v1; b, d_ = d_, b
    Lr, Wr = np.linalg.norm(v1), np.linalg.norm(v2)
    u, w = v1 / Lr, v2 / Wr
    H = z1 - z0
    n = max(2, int(round(H / 17.5)))
    R = H / n
    wst = 20.0
    if n * 27 <= Lr - 20 or Wr < 180:  # tek kol
        flights = [(0.0, min(Wr, 120.0), 0, n, Lr)]
    else:  # U merdiven: iki kol + sahanlik
        fw = Wr / 2.0
        n1 = n // 2
        run = max(Lr - fw, 50.0)
        flights = [(0.0, fw, 0, n1, run), (fw, Wr, n1, n, run)]
    k = 0
    for fi, (w0, w1, s0, s1, run) in enumerate(flights):
        cnt = s1 - s0
        tr = run / cnt
        pts = [(0.0, s0 * R)]
        for j in range(cnt):
            pts += [(j*tr, (s0+j+1)*R), ((j+1)*tr, (s0+j+1)*R)]
        pts += [(run, (s0+cnt)*R - wst), (wst*tr/R, s0*R - wst) if s0 > 0 else (wst*tr/R, 0.0)]
        if s0 > 0: pts = [(0.0, s0*R - wst)] + pts
        try:
            pg = Polygon(pts).buffer(0)
        except Exception:
            continue
        if fi == 1:  # ikinci kol ters yonde
            o = a + u*Lr - u*0 + w*w0
            ee1 = -u
        else:
            o = a + w*w0; ee1 = u
        oo = (float(o[0]), float(o[1]), z0)
        add(path, f"{name}_KOL{fi+1}", "M_MERDIVEN",
            prism(pg, w1 - w0, oo, (float(ee1[0]), float(ee1[1]), 0.0), (0.0, 0.0, 1.0), (float(w[0]), float(w[1]), 0.0)))
        k += 1
    if len(flights) == 2:  # sahanlik
        fw = Wr / 2.0
        land = Polygon([tuple(a + u*(Lr - fw)), tuple(a + u*Lr), tuple(a + u*Lr + w*Wr), tuple(a + u*(Lr - fw) + w*Wr)])
        zl = z0 + (n//2) * R
        add(path, f"{name}_SAHANLIK", "M_MERDIVEN", plan_prism(land, zl - wst, zl))
    return dict(riht=round(R, 1), adet=n, kol=len(flights))

# ---------------- blok kurulum ----------------
def brut_of(blk, fl, d):
    b = brut_core(blk, fl, d)
    for nm, r in d["rooms"]:
        if any(k in asc(nm) for k in AVLU):
            b = b.difference(r.buffer(0.5, join_style=2).buffer(-0.5, join_style=2))
    b = max(parts(b.buffer(0)), key=lambda p: p.area)
    b = Polygon(b.exterior, [i for i in b.interiors]).simplify(1.0)
    return orient(b, 1.0)

def brut_core(blk, fl, d):
    if blk == "A" and fl == "K1":
        return max(D["A"]["ZK"]["brut"], key=lambda p: p.area)
    if d["brut"]:
        b = max(d["brut"], key=lambda p: p.area)
    else:
        gs = [r[1] for r in d["rooms"] if not any(k in asc(r[0]) for k in OUTDOOR)] + d["cols"] + d["walls"]
        b = box(min(g.bounds[0] for g in gs), min(g.bounds[1] for g in gs), max(g.bounds[2] for g in gs), max(g.bounds[3] for g in gs))
    out = unary_union([r[1] for r in d["rooms"] if any(k in asc(r[0]) for k in OUTDOOR)])
    if not out.is_empty and b.intersection(out).area > 1e4:
        rest = [p for p in parts(b.difference(out.buffer(25, join_style=2))) if p.area > 3e4]
        if rest:
            core = max(rest, key=lambda p: p.area)
            # cekirdek: kalan parcanin dikdortgen sinirina, dis cizgiye kadar
            x0, y0, x1, y1 = core.bounds
            b = b.intersection(box(x0, y0, x1, y1).buffer(25, join_style=2)).buffer(0)
            b = max(parts(b), key=lambda p: p.area)
            # teras tarafindaki 25'lik tasmayi duvar ekseninde kes
            ox0, oy0, ox1, oy1 = out.bounds
            bx0, by0, bx1, by1 = b.bounds
            if ox0 > x0 and ox0 < bx1: b = b.intersection(box(bx0 - 1, by0 - 1, ox0 - 0.0 + 0, by1 + 1))
    return b

def win_tags(d, r, maxd=120):
    near = sorted([(t[2].distance(r), t[0], t[1]) for t in d["wtags"]])
    tip = next((v for dd, k, v in near if dd < maxd and k in ("TİP", "WINDOWTEXT")), None)
    h = next((float(v) for dd, k, v in near if dd < maxd and k == "YUKSEKLIK" and re.match(r"^\d+$", v)), None)
    w = next((float(v) for dd, k, v in near if dd < maxd and k in ("", "GENISLIK") and re.match(r"^\d+$", v)), None)
    return tip, w, h

def room_at(d, pt):
    for nm, r in d["rooms"]:
        if r.buffer(1).contains(Point(pt)):
            return nm, r
    return None, None

def v4_grow(blk, fl, d, bp, r, z0, z1, Lc, top, ht, tip):
    """Konsept v04: pencereyi oda cephesi icinde genislet, parapeti kaldir (islak hacim ve kucuk pencereler haric)."""
    if ht is None or ht < 120 or z1 - z0 > 400:
        return r, z0, z1, False
    best = None
    for e in edges_of(bp):
        us = [to_edge(e, c)[0] for c in r.exterior.coords]; ws = [to_edge(e, c)[1] for c in r.exterior.coords]
        if max(us) < -1 or min(us) > e["L"] + 1: continue
        dw = abs((min(ws) + max(ws)) / 2.0 - T_EXT / 2.0)
        if best is None or dw < best[0]: best = (dw, e, max(0.0, min(us)), min(e["L"], max(us)))
    if best is None or best[0] > 60:
        return r, z0, z1, False
    _, e, ua, ub = best
    c = (ua + ub) / 2.0
    pin = e["a"] + c * e["d"] + 70.0 * e["n_in"]
    nm, room = room_at(d, (pin[0], pin[1]))
    if nm is None or any(k in asc(nm) for k in WET_KEYS):
        return r, z0, z1, False
    us = [to_edge(e, q)[0] for q in room.exterior.coords]
    lo, hi = max(0.0, min(us)) + V4_ROOM_MARGIN, min(e["L"], max(us)) - V4_ROOM_MARGIN
    # kolonlar (cephe seridinde) engel
    for cp in d["cols"]:
        cu = [to_edge(e, q)[0] for q in cp.exterior.coords]; cw = [to_edge(e, q)[1] for q in cp.exterior.coords]
        if min(cw) > T_EXT + 40 or max(cw) < -5: continue
        if max(cu) <= c: lo = max(lo, max(cu) + 10.0)
        elif min(cu) >= c: hi = min(hi, min(cu) - 10.0)
    w0 = ub - ua
    wn = max(w0 * V4_WIN_GROW, w0 + 100.0)
    a2, b2 = max(lo, c - wn / 2.0), min(hi, c + wn / 2.0)
    a2, b2 = min(a2, ua), max(b2, ub)
    nz0 = Lc
    return edge_rect(e, a2, b2, 0.0, T_EXT), nz0, top, True

def v4_resolve(openings, fl):
    """Ayni kenarda genisleyen pencereler arasinda en az V4_PIER tas paye birak."""
    idx = [i for i, o in enumerate(openings) if o[5] == fl and o[3] == "W"]
    for i in idx:
        for j in idx:
            if i >= j: continue
            ri, rj = openings[i][0], openings[j][0]
            if ri.distance(rj) < V4_PIER and ri.buffer(V4_PIER).intersects(rj):
                inter_z = min(openings[i][2], openings[j][2]) - max(openings[i][1], openings[j][1])
                if inter_z <= 0: continue
                # ortadan bol: buyuk olani kucult
                gap = (ri.union(rj)).minimum_rotated_rectangle
                ci, cj = ri.centroid, rj.centroid
                dvec = np.array([cj.x - ci.x, cj.y - ci.y]); L = np.linalg.norm(dvec)
                if L < 1: continue
                dvec /= L
                mid = (np.array([ci.x, ci.y]) + np.array([cj.x, cj.y])) / 2.0
                cut = Polygon([tuple(mid + dvec * (-V4_PIER/2) + np.array([-dvec[1], dvec[0]]) * 200),
                               tuple(mid + dvec * (V4_PIER/2) + np.array([-dvec[1], dvec[0]]) * 200),
                               tuple(mid + dvec * (V4_PIER/2) - np.array([-dvec[1], dvec[0]]) * 200),
                               tuple(mid + dvec * (-V4_PIER/2) - np.array([-dvec[1], dvec[0]]) * 200)])
                for k in (i, j):
                    o = openings[k]
                    nr = o[0].difference(cut)
                    nr = max(parts(nr), key=lambda q: q.area) if parts(nr) else o[0]
                    openings[k] = (box(*nr.bounds), o[1], o[2], o[3], o[4], o[5])
    # moduler genislik: buyutulen pencereler 50 cm katlarina (ortalanarak) indirilir -> az bilesen tipi
    for i in idx:
        o = openings[i]
        if o[4] is None or o[4][1] is not None: continue
        x0, y0, x1, y1 = o[0].bounds
        if (x1 - x0) >= (y1 - y0):
            w = x1 - x0; wn = max(50.0, math.floor(w / 50.0) * 50.0); cx = (x0 + x1) / 2.0
            nr = box(cx - wn / 2.0, y0, cx + wn / 2.0, y1)
        else:
            w = y1 - y0; wn = max(50.0, math.floor(w / 50.0) * 50.0); cy = (y0 + y1) / 2.0
            nr = box(x0, cy - wn / 2.0, x1, cy + wn / 2.0)
        openings[i] = (nr, o[1], o[2], o[3], o[4], o[5])

lift = {}
TERR_FOOT = []
for blk, B in BLOCKS.items():
    fls = [f for f in B["floors"]]
    brut = {fl: brut_of(blk, fl, D[blk][fl]) for fl, _, _ in fls}
    brep = {"kat": [], "dograma": [], "uyari": []}
    # D blogu: konum vaziyet poligonundan
    if blk == "D":
        B["rot"] = math.degrees(math.atan2(1621.0, 710.0))
        th = math.radians(B["rot"])
        R = np.array([[math.cos(th), -math.sin(th)], [math.sin(th), math.cos(th)]])
        t = np.array([8050.0, 4778.0]) - R @ np.array([-855.0, 0.0])
        B["t"] = (float(t[0]), float(t[1]))
    levels = [L for _, L, _ in fls]
    top_slab_top = zc(B["sacak"]) - (ROOF_T if B["parapet"] else 13.0)
    # ---- dogramalar (blok bazinda, katlar arasi tekrar ayiklanir)
    openings_all = []   # (plan_rect, z0, z1, kind, comp, fl)
    for i, (fl, L, ceil) in enumerate(fls):
        d = D[blk][fl]
        Lc = zc(L)
        ceilc = zc(ceil) if ceil else Lc + 290.0
        top = ceilc - 17.0
        bd = brut[fl].boundary
        for w in d["wins"]:
            r = box(*w)
            thin = min(w[2]-w[0], w[3]-w[1]); Lw = max(w[2]-w[0], w[3]-w[1])
            dist = bd.distance(r.centroid)
            tip, wt, ht = win_tags(d, r.centroid)
            if not ((thin < 45 and dist < 40) or (ht and dist < 80 and thin < 140)):
                continue
            if wt and Lw < 0.6 * wt:
                brep["uyari"].append(f"{fl}: {tip} etiket genisligi {wt:.0f}, cizim {Lw:.0f}: atlandi"); continue
            if ht is None and thin < 20 and dist < 40 and Lw >= 100:
                ht = 280.0; tip = "P-ETIKETSIZ"
                brep["uyari"].append(f"{fl}: etiketsiz dograma 280 kabul edildi {[round(v) for v in w]}")
            if ht is None:
                brep["uyari"].append(f"{fl}: etiketsiz dograma atlandi {[round(v) for v in w]}"); continue
            # ayni yerde alt kattan gelen yuksek dograma varsa atla
            dup = False
            for (pr, oz0, oz1, kind, comp, ofl) in openings_all:
                if pr.buffer(5).intersects(r) and pr.intersection(r.buffer(5)).area > 0.3 * min(pr.area, r.area + 1) and oz1 > Lc + 50:
                    dup = True
            if dup: continue
            if ht <= top - Lc + 7:
                z0, z1 = max(Lc, top - ht), top
            else:
                z0, z1 = Lc, Lc + ht - 7.0
            r, z0, z1, grown = v4_grow(blk, fl, d, brut[fl], r, z0, z1, Lc, top, ht, tip)
            openings_all.append((r, z0, z1, "W", (tip, wt if not grown else None, ht if not grown else None, Lw), fl))
        v4_resolve(openings_all, fl)
        # dis kapilar: kapi cizgileri dis seridi kesiyorsa
        band = brut[fl].difference(brut[fl].buffer(-30, join_style=2))
        dl = [l for l in d["doors"] if l.intersects(band)]
        if dl:
            U = unary_union([l.buffer(3) for l in dl])
            for g in parts(U):
                x0, y0, x1, y1 = g.bounds
                if max(x1-x0, y1-y0) < 60: continue
                gi = g.intersection(band)
                if gi.is_empty or gi.area < 200: continue
                # pencereyle cakisiyorsa atla
                if any(pr.buffer(10).intersects(gi) for (pr, _, _, _, _, ofl) in openings_all if ofl == fl): continue
                openings_all.append((box(*gi.bounds), Lc, top, "D", None, fl))
    # ---- B otopark girisi (H6): kuzey cephede garaj kapisi boslugu
    if blk == "B":
        Lc2 = zc(167.15)
        openings_all.append((box(800, 805, 1200, 825), Lc2, Lc2 + 230.0, "G", None, "B2"))
    # ---- katlar
    for i, (fl, L, ceil) in enumerate(fls):
        d = D[blk][fl]
        kat = KAT_TAG[fl]
        root = f"BLOK_{blk}/{blk}_{kat}"
        Lc = zc(L)
        ceilc = zc(ceil) if ceil else Lc + 290.0
        last = (i == len(fls) - 1)
        Lnext = zc(fls[i+1][1]) if not last else top_slab_top + 0.0
        wall_z0 = Lc - KAPLAMA
        wall_z1 = (Lnext - KAPLAMA - DOSEME) if not last else top_slab_top - DOSEME
        bp = brut[fl]
        rooms = [(nm, r) for nm, r in d["rooms"]]
        indoor = [(nm, r.intersection(bp)) for nm, r in rooms if not any(k in asc(nm) for k in OUTDOOR + AVLU) and r.intersection(bp).area > 0.5 * r.area]
        # --- dis duvar seritleri
        ops_here = [(pr, z0, z1, kind) for (pr, z0, z1, kind, comp, ofl) in openings_all if min(z1, wall_z1) - max(z0, wall_z0) > 1]
        nwall = 0
        for k_, (e, ua, ub, p) in enumerate(strips(bp, True, T_EXT)):
            ops = []
            for (pr, z0, z1, kind) in ops_here:
                if pr.buffer(25).intersects(p):
                    us = [to_edge(e, c)[0] for c in pr.exterior.coords]
                    ws = [to_edge(e, c)[1] for c in pr.exterior.coords]
                    if min(ws) < T_EXT + 25 and max(ws) > -25:
                        ops.append((min(us), max(us), z0, z1))
            nwall += elev_panel(f"{root}/DIS_DUVAR", f"DD_{blk}_{fl}_{k_+1:02d}", "M_DIS_DUVAR", e, ua, ub, 0.0, T_EXT, wall_z0, wall_z1, ops)
        # --- parapet (D cati)
        if blk == "B" and fl == "B2":   # otopark rampasi yan istinat duvarlari (DXF B2 plani)
            for k_, (xa, xb) in enumerate([(770, 800), (1200, 1230)]):
                add(f"{root}/DIS_DUVAR", f"ISTINAT_RAMPA_B_{k_+1}", "M_DIS_DUVAR", plan_prism(box(xa, 835, xb, 1046), wall_z0, Lnext - KAPLAMA))
        # --- cephe kaplamasi
        ck_z0 = (Lc - KAPLAMA - DOSEME) if i == 0 else Lc - KAPLAMA
        ck_z1 = (Lnext - KAPLAMA) if not last else (zc(B["parapet"]) if B["parapet"] else top_slab_top)
        for k_, (e, ua, ub, p) in enumerate(strips(bp, False, CEPHE)):
            ops = []
            for (pr, z0, z1, kind) in [(pr, z0, z1, kind) for (pr, z0, z1, kind, comp, ofl) in openings_all]:
                if min(z1, ck_z1) - max(z0, ck_z0) <= 1: continue
                if pr.buffer(25).intersects(p):
                    us = [to_edge(e, c)[0] for c in pr.exterior.coords]
                    ws = [to_edge(e, c)[1] for c in pr.exterior.coords]
                    if min(ws) < 25 and max(ws) > -CEPHE - 25:
                        ops.append((min(us), max(us), z0, z1))
            fm = FACADE.get((blk, fl), ("M_CEPHE_KAPLAMA", "M_CEPHE_KAPLAMA"))
            cmat = fm[0] if abs(e["d"][0]) >= abs(e["d"][1]) else fm[1]
            elev_panel(f"{root}/CEPHE_KAPLAMA", f"CK_{blk}_{fl}_{k_+1:02d}", cmat, e, ua, ub, -CEPHE, 0.0, ck_z0, ck_z1, ops)
        # --- ic duvarlar = brut - dis serit - mahaller - kolonlar
        inner = bp.buffer(-T_EXT, join_style=2)
        cols = unary_union(d["cols"]).intersection(bp) if d["cols"] else Polygon()
        roomsU = unary_union([r for _, r in indoor]) if indoor else Polygon()
        wallmass = inner.difference(roomsU.buffer(0.5, join_style=2)).difference(cols)
        thin_parts, voids = [], []
        for p in parts(wallmass):
            if p.area < 300: continue
            core = p.buffer(-30, join_style=2)
            if core.is_empty:
                thin_parts.append(p)
            else:
                opened = core.buffer(30, join_style=2)
                thin_parts += [q for q in parts(p.difference(opened)) if q.area > 300]
                voids += [q for q in parts(opened.intersection(p)) if q.area > 5000]
        for k_, p in enumerate(thin_parts):
            add(f"{root}/IC_DUVAR", f"ID_{blk}_{fl}_{k_+1:02d}", "M_IC_DUVAR", plan_prism(p.simplify(1.0), wall_z0, wall_z1))
        # --- tasiyici: kolonlarin dis serit disinda kalan kismi
        band_in = bp.difference(inner)
        nk = 0
        for p in parts(cols.difference(band_in)):
            if p.area < 100: continue
            x0, y0, x1, y1 = p.bounds
            nk += 1
            if abs(p.area - (x1-x0)*(y1-y0)) < 20:
                w, dd = x1 - x0, y1 - y0
                if w >= dd:
                    cn = col_def(w, dd, wall_z1 - wall_z0)
                    insts.append({"p": f"{root}/TASIYICI", "n": f"{cn}_{blk}{fl}_{nk:02d}", "d": cn, "o": [rnd(x0), rnd(y0), rnd(wall_z0)], "x": (1, 0, 0), "y": (0, 1, 0)})
                else:
                    cn = col_def(dd, w, wall_z1 - wall_z0)
                    insts.append({"p": f"{root}/TASIYICI", "n": f"{cn}_{blk}{fl}_{nk:02d}", "d": cn, "o": [rnd(x1), rnd(y0), rnd(wall_z0)], "x": (0, 1, 0), "y": (-1, 0, 0)})
            else:
                add(f"{root}/TASIYICI", f"PERDE_{blk}_{fl}_{nk:02d}", "M_TASIYICI", plan_prism(p, wall_z0, wall_z1))
        # --- doseme (bu katin ve alt katin izdusumu), merdiven bosluklari
        below = brut[fls[i-1][0]] if i > 0 else None
        slab = bp if below is None else unary_union([bp, below]).buffer(0)
        holes = []
        if i > 0:
            for nm, r in indoor:
                if "MERDIVEN" in asc(nm): holes.append(r)
        slab_r = slab.difference(unary_union(holes)) if holes else slab
        add_poly(f"{root}/DOSEME", f"DOSEME_{blk}_{fl}", "M_DOSEME", slab_r, Lc - KAPLAMA - DOSEME, Lc - KAPLAMA)
        # --- teras parapeti (alt katin cikintisi)
        terr = slab.difference(bp.buffer(0.5, join_style=2))
        terr = unary_union([p for p in parts(terr) if p.area > 2e4]) if terr.area > 2e4 else Polygon()
        if not terr.is_empty and (blk, fl) not in SKIP_TERR:
            edge_band = slab.difference(slab.buffer(-RAIL_T, join_style=2))
            par = edge_band.intersection(terr)
            par = unary_union([p for p in parts(par) if p.area > 100])
            add_poly(f"{root}/DOGRAMA", f"KORKULUK_{blk}_{fl}", "M_DOGRAMA_CAM", par, Lc - KAPLAMA, Lc + RAIL_H, minarea=100)
            terr_fin = terr.difference(par)
            TERR_FOOT.append((blk, terr, Lc - KAPLAMA - DOSEME, Lc + RAIL_H))
            add_poly(f"{root}/DOSEME_KAPLAMA/DOSEME_KAPLAMA_KURU", f"DK_TERAS_{blk}_{fl}", "M_DOSEME_KAPLAMA_KURU", terr_fin, Lc - KAPLAMA, Lc, minarea=1000)
        # --- dograma bilesenleri
        for (pr, z0, z1, kind, comp, ofl) in openings_all:
            if ofl != fl: continue
            # hangi kenar
            best = None
            for e in edges_of(bp):
                us = [to_edge(e, c)[0] for c in pr.exterior.coords]; ws = [to_edge(e, c)[1] for c in pr.exterior.coords]
                if max(us) < -1 or min(us) > e["L"] + 1: continue
                dw = abs((min(ws) + max(ws)) / 2.0 - T_EXT / 2.0)
                if best is None or dw < best[0]: best = (dw, e, max(0.0, min(us)), min(e["L"], max(us)))
            if best is None or best[0] > 100:
                brep["uyari"].append(f"{fl}: dograma kenari bulunamadi"); continue
            _, e, ua, ub = best
            w = ub - ua; h = z1 - z0
            if kind == "W":
                tip, wt, ht, Lw = comp
                dn = window_def(w, h, wt if (wt and abs(wt - w) < 15) else None, ht if (ht and abs(ht - h) < 10) else None)
            elif kind == "G":
                tip = "GARAJ"; dn = door_def(w, h, "DGR_GARAJ")
            else:
                tip = "KAPI"; dn = door_def(w, h)
            dep = (T_EXT - FRAME_D) / 2.0
            o = e["a"] + ua * e["d"] + dep * e["n_in"]
            insts.append({"p": f"{root}/DOGRAMA", "n": f"{tip or 'P'}_{dn}_{blk}{fl}", "d": dn,
                          "o": [rnd(o[0]), rnd(o[1]), rnd(z0)], "x": (float(e["d"][0]), float(e["d"][1]), 0.0), "y": (float(e["n_in"][0]), float(e["n_in"][1]), 0.0)})
            brep["dograma"].append({"kat": fl, "tip": tip, "bilesen": dn, "genislik": round(w), "yukseklik": round(h),
                                    "parapet_cm": round(z0 - Lc), "ust_cm": round(z1 - Lc), "alt_kot": round(Z0 + z0/100, 2), "ust_kot": round(Z0 + z1/100, 2)})
        # --- doseme kaplamasi + tavan (mahal bazinda)
        used = {}
        tav_z1 = ceilc + TAVAN
        for nm, r in indoor + [("MAHAL", v) for v in voids]:
            key = asc(nm)
            if key in ("ASANSOR",): continue
            used[key] = used.get(key, 0) + 1
            kk = key if used[key] == 1 else f"{key}_{used[key]}"
            isl = any(k in key for k in ISLAK) and "SALON" not in key
            sub = "DOSEME_KAPLAMA_ISLAK" if isl else "DOSEME_KAPLAMA_KURU"
            mat = "M_" + sub
            fp = r.intersection(inner).buffer(0)
            if "MERDIVEN" not in key or i == 0:
                add_poly(f"{root}/DOSEME_KAPLAMA/{sub}", f"DK_{kk}", mat, fp, Lc - KAPLAMA, Lc, minarea=500)
            if tav_z1 < wall_z1 - 0.5:
                add_poly(f"{root}/TAVAN", f"TV_{kk}", "M_TAVAN", fp, ceilc, tav_z1, minarea=500)
        # --- merdiven (bir ust kata)
        st = None
        if not last:
            for nm, r in indoor:
                if "MERDIVEN" in asc(nm) and r.area > 3e4:
                    st = stair_mass(f"{root}/MERDIVEN", f"MRD_{blk}_{fl}", r, Lc, Lnext)
        brep["kat"].append({"kat": fl, "kot": L, "ust_kat_kotu": round(Z0 + Lnext/100, 2), "kat_yuksekligi_cm": round(Lnext - Lc),
                            "tavan_kotu": round(Z0 + ceilc/100, 2), "net_yukseklik_cm": round(ceilc - Lc),
                            "brut_m2": round(bp.area/1e4, 1), "mahal": len(indoor), "merdiven": st})
        lift.setdefault(blk, {})[fl] = (bp, wall_z0, Lnext)
    # ---- cati
    topfl = fls[-1][0]
    bp = brut[topfl]
    root = f"BLOK_{blk}/{blk}_KAT_CATI"
    add_poly(f"{root}/DOSEME", f"DOSEME_CATI_{blk}", "M_DOSEME", bp, top_slab_top - DOSEME, top_slab_top)
    if blk == "D":
        x0, y0, x1, y1 = bp.bounds
        rr = (x0 + T_EXT, y0 + T_EXT, x1 - T_EXT, y1 - T_EXT)
        par = bp.difference(box(*rr))
        add_poly(f"{root}/CATI", f"PARAPET_CATI_{blk}", "M_DIS_DUVAR", par, top_slab_top, zc(B["parapet"]))
        cx, cy = (rr[0] + rr[2]) / 2.0, (rr[1] + rr[3]) / 2.0
        sw, sh = B["roof_size"]
        X0, Y0, X1, Y1 = cx - sw/2.0, cy - sh/2.0, cx + sw/2.0, cy + sh/2.0
    else:
        X0, Y0, X1, Y1 = B["roof_rect"]
    # H3: ust yuz sacak ucunda sacak kotunda, mahyada mahya kotunda; paket 20 cm (duseyde)
    zt_e = zc(B["sacak"]); zr = zc(B["mahya"])
    RT = ROOF_T
    if blk != "D":   # v04: konsept dusuk egim, ince profil
        RT = V4_ROOF_T
        zr = zt_e + V4_ROOF_SLOPE * min(X1 - X0, Y1 - Y0) / 2.0
    W_, Hh = X1 - X0, Y1 - Y0
    half = min(W_, Hh) / 2.0
    slope = (zr - zt_e) / half
    if W_ >= Hh:
        r1, r2 = (X0 + half, Y0 + half), (X1 - half, Y0 + half)
        planes = [(Polygon([(X0, Y0), (X1, Y0), r2, r1]), ("y", Y0, 1)), (Polygon([(X1, Y0), (X1, Y1), r2]), ("x", X1, -1)),
                  (Polygon([(X1, Y1), (X0, Y1), r1, r2]), ("y", Y1, -1)), (Polygon([(X0, Y1), (X0, Y0), r1]), ("x", X0, 1))]
    else:
        r1, r2 = (X0 + half, Y0 + half), (X0 + half, Y1 - half)
        planes = [(Polygon([(X0, Y0), (X1, Y0), r1]), ("y", Y0, 1)), (Polygon([(X1, Y0), (X1, Y1), r2, r1]), ("x", X1, -1)),
                  (Polygon([(X1, Y1), (X0, Y1), r2]), ("y", Y1, -1)), (Polygon([(X0, Y1), (X0, Y0), r1, r2]), ("x", X0, 1))]
    # avlu bosluklari (cephe kaplamasi dis yuzune kadar)
    roof_hole = Polygon()
    if len(bp.interiors):
        roof_hole = unary_union([Polygon(r).buffer(-CEPHE, join_style=2) for r in bp.interiors])
    VV, VI, FF = [], {}, []
    def vid(x, y, z):
        k = (round(x, 1), round(y, 1), round(z, 1))
        if k not in VI: VI[k] = len(VV); VV.append([rnd(x), rnd(y), rnd(z)])
        return VI[k]
    def ztop(pl, x, y):
        ax, v0, sg = pl
        dist = (y - v0) * sg if ax == "y" else (x - v0) * sg
        return zt_e + slope * dist
    pieces = []
    for poly, pl in planes:
        for q in parts(poly.difference(roof_hole)):
            if q.area > 10: pieces.append((orient(q, 1.0), pl))
    edge_use = {}
    for q, pl in pieces:
        rings = [list(q.exterior.coords)[:-1]] + [list(r.coords)[:-1] for r in q.interiors]
        for ring in rings:
            for i in range(len(ring)):
                a2, b2 = ring[i], ring[(i+1) % len(ring)]
                k = tuple(sorted([(round(a2[0], 1), round(a2[1], 1)), (round(b2[0], 1), round(b2[1], 1))]))
                edge_use[k] = edge_use.get(k, 0) + 1
    for q, pl in pieces:
        rings = [list(q.exterior.coords)[:-1]] + [list(r.coords)[:-1] for r in q.interiors]
        FF.append([[vid(x, y, ztop(pl, x, y)) for x, y in ring] for ring in rings])
        FF.append([[vid(x, y, ztop(pl, x, y) - RT) for x, y in reversed(ring)] for ring in rings])
        for ring in rings:
            for i in range(len(ring)):
                a2, b2 = ring[i], ring[(i+1) % len(ring)]
                k = tuple(sorted([(round(a2[0], 1), round(a2[1], 1)), (round(b2[0], 1), round(b2[1], 1))]))
                if edge_use[k] > 1: continue
                za, zb = ztop(pl, *a2), ztop(pl, *b2)
                FF.append([[vid(a2[0], a2[1], za - RT), vid(b2[0], b2[1], zb - RT), vid(b2[0], b2[1], zb), vid(a2[0], a2[1], za)]])
    add(f"{root}/CATI", f"CATI_KIRMA_{blk}", "M_CATI_METAL+M_CATI_METAL+M_SACAK_ALTI_AHSAP", {"v": VV, "f": FF})
    if blk == "D":   # v04 konsept 1/3: 1. kat terasinda ahsap pergola + tas kule
        pr = f"BLOK_D/D_KAT_01/PERGOLA"
        zt = zc(170.75)
        for k_, (px, py) in enumerate([(250, -1215), (870, -1215), (250, -30), (870, -30)]):
            add(pr, f"PERGOLA_DIREK_{k_+1}", "M_AHSAP", plan_prism(box(px, py, px + 15, py + 15), zt, zt + 255))
        for k_, py in enumerate([-1215, -30]):
            add(pr, f"PERGOLA_KIRIS_{k_+1}", "M_AHSAP", plan_prism(box(245, py, 890, py + 15), zt + 255, zt + 280))
        if "PERGOLA_LATA" not in defs:
            sl = plan_prism(box(0, 0, 6, 1225), 0, 18); sl["m"] = "M_AHSAP"
            defs["PERGOLA_LATA"] = {"solids": [sl], "glass": [], "info": {}}
        for k_ in range(13):
            insts.append({"p": pr, "n": f"PERGOLA_LATA_{k_+1:02d}", "d": "PERGOLA_LATA", "o": [rnd(262 + k_ * 50), -1222.0, rnd(zt + 280)], "x": (1, 0, 0), "y": (0, 1, 0)})
        add("BLOK_D/D_KAT_01/CEPHE_KAPLAMA", "KULE_TAS_D", "M_CEPHE_TAS", plan_prism(box(935, -150, 1015, 0), zc(164.15), zc(174.25)))
        TERR_FOOT.append(("D", box(935, -150, 1015, 0), zc(164.15), zc(174.25)))
    brep["cati"] = {"tip": "kirma (4 yon)", "sacak_ucu_kotu": B["sacak"], "mahya_kotu": round(Z0 + zr / 100.0, 2), "egim_yuzde": round(slope*100, 1),
                    "sacak_izdusumu_cm": [round(W_), round(Hh)], "parapet_kotu": B["parapet"]}
    brep["ort"] = B["ort"]; brep["rot"] = round(B["rot"], 2); brep["t"] = [round(c, 1) for c in B["t"]]
    report["blocks"][blk] = brep

# ---------------- arazi ----------------
PTS = [tuple(map(float, l.split()[:3])) for l in open(sys.argv[3]).read().strip().splitlines()]
PARCEL = Polygon([(2213,7356),(2710,7275),(4207,7067),(4116,6770),(5747,6554),(6488,6442),(7015,6362),(7827,8576),(7900,8548),
                  (8478,8112),(9800,6929),(9851,7074),(9877,7054),(10593,6513),(9445,3876),(8739,1056),(8370,808),(6049,1141),
                  (3831,1459),(2918,1674),(727,2190),(1251,3991),(1576,5118)]).buffer(0)
def site_xf(blk, g):
    B = BLOCKS[blk]
    g = affinity.rotate(g, B["rot"], origin=(0, 0))
    return affinity.translate(g, B["t"][0], B["t"][1])
# blok izleri (cephe kaplamasi dahil) ve dusey uzanimlari
FOOT = []
for blk, fd in lift.items():
    for fl, (bp, z0, z1) in fd.items():
        FOOT.append((site_xf(blk, bp.buffer(CEPHE, join_style=2)), z0 - DOSEME, z1))
for blk, terr, z0, z1 in TERR_FOOT:
    FOOT.append((site_xf(blk, terr), z0, z1))
# H6: B otopark girisi onunde yarma (167.25 kademesinin ustu bosaltilir)
YARMA = site_xf("B", box(770, 815, 1230, 2300))
FOOT.append((YARMA, zc(166.00) + 1.0, 1e6))   # v03: 166 ustu bosaltilir, taban asagida 167.15'e doldurulur
FOOT = [f for f in FOOT if f]
# kontrol noktalari: vaziyet kotlari + blok cevresinde tesviye kotlari
pts = [(x, y, z) for x, y, z in PTS]
tes = [(x, y, z) for x, y, z, *r in [tuple(l.split()) for l in open(sys.argv[3]).read().strip().splitlines()] if r and r[0] == "TES"]
tes = [(float(x), float(y), float(z)) for x, y, z in tes]
ring_pts = []
for blk, fd in lift.items():
    fp = unary_union([site_xf(blk, bp) for bp, _, _ in fd.values()])
    mine = [p for p in tes if fp.distance(Point(p[0], p[1])) < 700]
    if not mine: continue
    ring = fp.buffer(CEPHE + 120, join_style=2).exterior
    Lr = ring.length
    for s in np.arange(0, Lr, 250.0):
        q = ring.interpolate(s)
        z = min(mine, key=lambda p: (p[0]-q.x)**2 + (p[1]-q.y)**2)[2]
        ring_pts.append((q.x, q.y, z))
allp = np.array(pts + ring_pts)
w_ring = np.array([1.0]*len(pts) + [3.0]*len(ring_pts))
def zfield(X, Y):
    dx = X[..., None] - allp[:, 0]; dy = Y[..., None] - allp[:, 1]
    d2 = dx*dx + dy*dy + 1.0
    w = w_ring / d2**1.5
    return (w * allp[:, 2]).sum(-1) / w.sum(-1)
GS = 100.0
from scipy import ndimage
x0, y0, x1, y1 = PARCEL.bounds
xs = np.arange(x0 - GS, x1 + 2*GS, GS); ys = np.arange(y0 - GS, y1 + 2*GS, GS)
XX, YY = np.meshgrid(xs + GS/2, ys + GS/2)
ZZ = np.zeros_like(XX)
for j in range(0, XX.shape[0], 20):
    ZZ[j:j+20] = zfield(XX[j:j+20], YY[j:j+20])
special = sorted(set([164.25, 167.25, 170.15, 170.36, 172.95, 174.15, 174.36]))
lv = [float(v) for v in range(158, 183)]
lv = sorted([v for v in lv if all(abs(v - s) > 0.45 for s in special)] + special)
inside = np.array([[PARCEL.contains(Point(XX[j, i], YY[j, i])) for i in range(XX.shape[1])] for j in range(XX.shape[0])])
zmin = float(ZZ[inside].min()); zmax = float(ZZ[inside].max())
base = math.floor(zmin) - 1.0
lv = [v for v in lv if v > base and v < zmax + 0.3]
def mask_poly(m):
    lab, n = ndimage.label(m)
    polys = []
    for k in range(1, n + 1):
        jj, ii = np.nonzero(lab == k)
        cells = [box(xs[i], ys[j], xs[i] + GS, ys[j] + GS) for j, i in zip(jj, ii)]
        polys.append(unary_union(cells))
    return unary_union(polys) if polys else Polygon()
prev_reg = PARCEL
prev = base
nter = 0
st = np.ones((3, 3), bool)
for L in lv:
    if prev == base:
        reg = PARCEL
    else:
        m = (ZZ + 0.08 >= prev)
        m = ndimage.binary_closing(m, st, iterations=2)
        m = ndimage.binary_opening(m, st, iterations=2)
        reg = mask_poly(m)
        reg = reg.buffer(150, join_style=2).buffer(-300, join_style=2).buffer(150, join_style=2).simplify(150)
        reg = reg.intersection(prev_reg).intersection(PARCEL)
        reg = unary_union([p for p in parts(reg.buffer(-80, join_style=2).buffer(80, join_style=2)) if p.area > 3e4]).intersection(prev_reg)
        reg = reg.buffer(0)
    hole = unary_union([f[0] for f in FOOT if (f[2] > zc(prev) + 50) and (f[1] < zc(L) - 1)]) if FOOT else Polygon()
    regh = reg.difference(hole)
    for p in parts(regh):
        if p.area < 2e4: continue
        p = p.simplify(10)
        if p.is_empty or p.area < 2e4: continue
        nter += 1
        add("ARAZI", f"ARAZI_KADEME_{L:.2f}_{nter:02d}", "M_ARAZI_BAHCE+M_ISTINAT_TAS+M_ISTINAT_TAS", plan_prism(p, zc(prev), zc(L)))
    prev_reg = reg if not reg.is_empty else prev_reg
    prev = L
yt = site_xf("B", unary_union([box(800, 835, 1200, 1046), box(770, 1046, 1230, 2300)])).intersection(PARCEL)  # cephe kaplamasi ve rampa duvarlariyla cakismaz
add("ARAZI", "ARAZI_YARMA_TABAN_167.15", "M_PARKE_TAS+M_ISTINAT_TAS+M_ISTINAT_TAS", plan_prism(yt, zc(166.00), zc(167.15)))
report["arazi"] = {"kademeler_m": lv, "taban_m": base, "nokta": len(pts), "tesviye_halka_noktasi": len(ring_pts),
                   "grid_cm": GS, "z_min": round(zmin, 2), "z_max": round(zmax, 2), "kademe_cismi": nter}
spec = {"solids": solids, "defs": defs, "insts": insts,
        "blocks": {b: {"rot": BLOCKS[b]["rot"], "t": BLOCKS[b]["t"]} for b in BLOCKS}, "z0_m": Z0, "north_angle": NORTH_ANGLE}
json.dump(spec, open(OUT, "w"), ensure_ascii=False)
json.dump(report, open(OUT.replace(".json", "_rapor.json"), "w"), ensure_ascii=False, indent=1, default=str)
nf = sum(len(s["f"]) for s in solids)
print(len(solids), "solids", nf, "faces", len(insts), "insts", len(defs), "defs")
for b, r in report["blocks"].items():
    print(b, [ (k["kat"], k["kat_yuksekligi_cm"], k["brut_m2"], k["mahal"]) for k in r["kat"]], len(r["dograma"]), r["uyari"][:5])
