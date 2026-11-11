# DNM01 SketchUp model spec generator (HACIM). Reads user-revised DXF, builds a JSON spec of
# solids (vertices + face loops, cm, world coords) and component definitions/instances.
import sys, json, math
import ezdxf
from shapely.geometry import Polygon, box, Point, MultiPolygon
from shapely.ops import unary_union
from shapely.geometry.polygon import orient

DXF = sys.argv[1]
OUT = sys.argv[2]

# ---------------- PARAMETERS (kullanici degistirebilir) ----------------
KAT_H = 350.0
KAPLAMA, DOSEME, TAVAN = 10.0, 30.0, 10.0
CEPHE = 20.0
ROOF_EAVE = 50.0          # saçak, cephe kaplaması dış yüzünden
ROOF_SLOPE = 0.15
ROOF_T = 20.0             # çatı paketi (düşey)
EAVE_Z = 700.0            # saçak ucu üst kotu
GROUND_MARGIN = 500.0
INT_OPEN_H = 220.0        # iç kapı / geçiş boşluk yüksekliği
MAIN_DOOR_H = 250.0
# mahal -> (parapet, yukseklik)
WIN_RULES = [
    (("SALON", "MUTFAK"), (0, 300)),
    (("EBEVEYN YATAK",), (0, 300)),
    (("YATAK ODASI",), (90, 210)),
    (("BANYO", "HOL", "GİYİNME", "WC"), (150, 150)),
]
ISLAK_KEYS = ("WC", "BANYO", "MUTFAK")
FLOORS = [  # name, y offset in dxf, level (finish top)
    ("KAT_B1", -1810.0, -350.0),
    ("KAT_00", 0.0, 0.0),
    ("KAT_01", 1810.0, 350.0),
]
W, D = 1360.0, 1010.0
T_EXT, T_INT = 20.0, 10.0
FRAME_B, FRAME_D = 5.0, 6.0   # doğrama kasa genişliği / derinliği

ASCII = str.maketrans("ÇĞİÖŞÜçğıöşü", "CGIOSUcgiosu")
def asc(s):
    return s.translate(ASCII).replace(" / ", "_").replace(" ", "_").replace("/", "_")

doc = ezdxf.readfile(DXF)
msp = doc.modelspace()

def rnd(v):
    return round(float(v) + 0.0, 2)

# ---------------- geometry helpers ----------------
def clean(poly):
    poly = poly.simplify(0.01, preserve_topology=True)
    return orient(poly, 1.0)

def parts(g):
    if g.is_empty:
        return []
    if isinstance(g, Polygon):
        return [g]
    out = []
    for p in getattr(g, "geoms", []):
        out += parts(p)
    return out

def prism(poly, h, o, e1, e2, e3):
    """2D poly in (u,v); extrude w 0..h. world = o + u e1 + v e2 + w e3."""
    poly = clean(poly)
    det = (e1[0]*(e2[1]*e3[2]-e2[2]*e3[1]) - e1[1]*(e2[0]*e3[2]-e2[2]*e3[0]) + e1[2]*(e2[0]*e3[1]-e2[1]*e3[0]))
    rings = [list(poly.exterior.coords)[:-1]] + [list(r.coords)[:-1] for r in poly.interiors]
    verts, faces = [], []
    def P(u, v, w):
        return [rnd(o[k] + u*e1[k] + v*e2[k] + w*e3[k]) for k in range(3)]
    idx_b, idx_t = [], []
    for ring in rings:
        b, t = [], []
        for (u, v) in ring:
            b.append(len(verts)); verts.append(P(u, v, 0))
        for (u, v) in ring:
            t.append(len(verts)); verts.append(P(u, v, h))
        idx_b.append(b); idx_t.append(t)
    top = [idx_t[0]] + idx_t[1:]
    bot = [list(reversed(idx_b[0]))] + [list(reversed(r)) for r in idx_b[1:]]
    faces.append(top); faces.append(bot)
    for b, t in zip(idx_b, idx_t):
        n = len(b)
        for i in range(n):
            j = (i + 1) % n
            faces.append([[b[i], b[j], t[j], t[i]]])
    if det < 0:
        faces = [[list(reversed(l)) for l in f] for f in faces]
    return {"v": verts, "f": faces}

def plan_prism(poly, z0, z1):
    return prism(poly, z1 - z0, (0, 0, z0), (1, 0, 0), (0, 1, 0), (0, 0, 1))

solids = []   # {"p": path, "n": name, "m": material, ...geom}
def add(path, name, mat, g):
    g = dict(g); g.update({"p": path, "n": name, "m": mat}); solids.append(g)

defs = {}     # name -> {"solids":[{m, v, f}], "faces":[{m, v, f(single loops)}]}
insts = []    # {"p", "n", "d", "o", "x", "y"}

# ---------------- read DXF per floor ----------------
def in_floor(pts, off):
    ys = [p[1] - off for p in pts]
    return min(ys) > -200 and max(ys) < 1250

def poly_pts(e):
    return [(float(v[0]), float(v[1])) for v in e.vertices_in_wcs()]

floor_data = {}
for fname, off, L in FLOORS:
    fd = {"walls": [], "cols": [], "areas": [], "texts": [], "wins": [], "doors": [], "doorpl": [], "stair": None}
    for e in msp.query("LWPOLYLINE"):
        pts = poly_pts(e)
        if not in_floor(pts, off):
            continue
        pts = [(x, y - off) for x, y in pts]
        lay = e.dxf.layer
        if lay == "2_IFC_Wall": fd["walls"].append(Polygon(pts).buffer(0))
        elif lay == "1_IFC_Concrete_Section": fd["cols"].append(Polygon(pts).buffer(0))
        elif lay == "0_IFC_Area": fd["areas"].append(Polygon(pts).buffer(0))
        elif lay == "1_IFC_Door": fd["doorpl"].append(Polygon(pts).buffer(0))
    for e in msp.query("INSERT"):
        p = e.ocs().to_wcs(e.dxf.insert)
        x, y = float(p[0]), float(p[1]) - off
        if not (-200 < y < 1250):
            continue
        nm = e.dxf.name
        if nm.startswith("0_IFC_ROOM_TEXT"):
            at = {a.dxf.tag: a.dxf.text for a in e.attribs}
            fd["texts"].append((x, y, at.get("ROOM_NAME", "")))
        elif nm.startswith("IFC_PENCERE_"):
            at = {a.dxf.tag: a.dxf.text for a in e.attribs}
            w = float(nm.split("_")[-1])
            fd["wins"].append({"x": x, "y": y, "rot": round(e.dxf.rotation) % 360, "w": w, "tip": at.get("TİP", ""), "h_dxf": float(at.get("YUKSEKLIK", 0) or 0)})
        elif nm.startswith("IFC_DOOR_"):
            fd["doors"].append({"x": x, "y": y, "w": float(nm.split("_")[-1])})
    floor_data[fname] = fd

FOOT = box(0, 0, W, D)
INNER = box(T_EXT, T_EXT, W - T_EXT, D - T_EXT)
BAND = FOOT.difference(INNER)

def room_name_of(fd, poly):
    for x, y, n in fd["texts"]:
        if poly.contains(Point(x, y)):
            return n
    return None

report = {"floors": {}, "warnings": []}

def win_rule(room):
    if room:
        for keys, val in WIN_RULES:
            for k in keys:
                if k in room:
                    return val
    return None

def side_of(rect):
    x0, y0, x1, y1 = rect.bounds
    if y1 <= T_EXT + 0.01: return "S"
    if y0 >= D - T_EXT - 0.01: return "N"
    if x1 <= T_EXT + 0.01: return "W"
    if x0 >= W - T_EXT - 0.01: return "E"
    return None

def along(rect, side):
    x0, y0, x1, y1 = rect.bounds
    return (x0, x1) if side in "SN" else (y0, y1)

# elevation mapping per side: returns (o, e1, e2, e3) for a panel whose thickness spans [t0,t1]
# (in the perpendicular world axis); u = world along coordinate, v = world z
def elev_frame(side, t0):
    if side in "SN":
        return (0, t0, 0), (1, 0, 0), (0, 0, 1), (0, 1, 0)
    return (t0, 0, 0), (0, 1, 0), (0, 0, 1), (1, 0, 0)

def elev_panel(path, name, mat, side, a, b, t0, t1, z0, z1, openings):
    poly = box(a, z0, b, z1)
    for (oa, ob, oz0, oz1) in openings:
        poly = poly.difference(box(oa, oz0, ob, oz1))
    o, e1, e2, e3 = elev_frame(side, t0)
    ps = parts(poly)
    for i, pp in enumerate(ps):
        add(path, name if len(ps) == 1 else f"{name}_{chr(97+i)}", mat, prism(pp, t1 - t0, o, e1, e2, e3))

# ---------------- component definitions ----------------
def window_def(w, h):
    name = f"DGR_{int(w)}x{int(h)}"
    if name in defs:
        return name
    n = max(1, int(round(w / 150.0)))
    n = max(1, min(n, int(w // 100)))
    rows = 2 if h > 240 else 1
    iw = (w - 2*FRAME_B - (n-1)*FRAME_B) / n
    ih = (h - 2*FRAME_B - (rows-1)*FRAME_B) / rows
    panes = []
    for i in range(n):
        for r in range(rows):
            u0 = FRAME_B + i*(iw + FRAME_B); v0 = FRAME_B + r*(ih + FRAME_B)
            panes.append((u0, v0, u0 + iw, v0 + ih))
    frame = box(0, 0, w, h)
    for p in panes:
        frame = frame.difference(box(*p))
    sol = prism(frame, FRAME_D, (0, 0, 0), (1, 0, 0), (0, 0, 1), (0, 1, 0))
    sol["m"] = "M_DOGRAMA_KASA"
    glass = []
    for (u0, v0, u1, v1) in panes:
        y = FRAME_D / 2
        glass.append([[u0, y, v0], [u1, y, v0], [u1, y, v1], [u0, y, v1]])
    defs[name] = {"solids": [sol], "glass": glass, "info": {"w": w, "h": h, "bolme": n, "kayit": rows - 1, "pane_w": round(iw, 1)}}
    return name

def entrance_def(w, h):
    name = f"DGR_KAPI_{int(w)}x{int(h)}"
    if name in defs:
        return name
    frame = box(0, 0, w, h).difference(box(FRAME_B, 0, w - FRAME_B, h - FRAME_B))
    sol = prism(frame, FRAME_D, (0, 0, 0), (1, 0, 0), (0, 0, 1), (0, 1, 0)); sol["m"] = "M_DOGRAMA_KASA"
    leaf = prism(box(FRAME_B, 0, w - FRAME_B, h - FRAME_B), 4.0, (0, 1.0, 0), (1, 0, 0), (0, 0, 1), (0, 1, 0)); leaf["m"] = "M_DOGRAMA_KASA"
    defs[name] = {"solids": [sol, leaf], "glass": [], "info": {"w": w, "h": h}}
    return name

def door_def(w, h):
    name = f"KAPI_{int(w)}x{int(h)}"
    if name in defs:
        return name
    leaf = prism(box(0, 0, w, h), 4.0, (0, 0, 0), (1, 0, 0), (0, 0, 1), (0, 1, 0)); leaf["m"] = "M_DOGRAMA_KASA"
    defs[name] = {"solids": [leaf], "glass": [], "info": {"w": w, "h": h}}
    return name

col_def = "KOLON_20x40"
defs[col_def] = {"solids": [dict(plan_prism(box(0, 0, 40, 20), 0, 320), m="M_TASIYICI")], "glass": [], "info": {}}

def place_in_wall(path, name, dname, side, a, b, z, depth_off):
    """local x along opening, local y inward, origin at outer-left (seen from outside)."""
    if side == "S": o, x, y = (a, depth_off, z), (1, 0, 0), (0, 1, 0)
    elif side == "N": o, x, y = (b, D - depth_off, z), (-1, 0, 0), (0, -1, 0)
    elif side == "E": o, x, y = (W - depth_off, a, z), (0, 1, 0), (-1, 0, 0)
    else: o, x, y = (depth_off, b, z), (0, -1, 0), (1, 0, 0)
    insts.append({"p": path, "n": name, "d": dname, "o": [rnd(c) for c in o], "x": x, "y": y})

# ---------------- per floor ----------------
for fname, off, L in FLOORS:
    fd = floor_data[fname]
    rep = {"rooms": [], "windows": [], "doors": [], "passages": []}
    walls_u = unary_union(fd["walls"])
    cols_u = unary_union(fd["cols"])
    ext_w = walls_u.intersection(BAND)
    int_w = walls_u.difference(BAND)
    w_z0, w_z1 = L - KAPLAMA, L + KAT_H - DOSEME - KAPLAMA   # walls stand on slab top, up to slab underside
    if fname == "KAT_01":
        w_z1 = L + KAT_H - DOSEME - KAPLAMA - KAPLAMA  # roof slab 660..690 (no finish) -> walls to 660
        w_z1 = 660.0
    # rooms
    rooms = []
    for a in fd["areas"]:
        n = room_name_of(fd, a)
        if n is None:
            n = "MERDIVEN"
        if n == "WC" and fname == "KAT_01":
            n = "EBEVEYN WC"
        rooms.append({"name": n, "poly": a})
    # overlap checks
    ov = unary_union([r["poly"] for r in rooms]).intersection(walls_u.union(cols_u)).area
    if ov > 1: report["warnings"].append(f"{fname}: mahal-duvar cakismasi {ov:.1f} cm2")
    # exterior gaps
    ext_gaps = parts(BAND.difference(walls_u).difference(cols_u))
    ext_gaps = [g for g in ext_gaps if g.area > 50]
    # interior gaps
    int_gaps = parts(INNER.difference(int_w).difference(unary_union([r["poly"] for r in rooms])))
    int_gaps = [g for g in int_gaps if g.area > 100]
    path = fname
    # ---- columns
    for i, c in enumerate(fd["cols"]):
        x0, y0, x1, y1 = c.bounds
        if (x1 - x0) >= (y1 - y0):
            insts.append({"p": f"{path}/TASIYICI", "n": f"KOLON_{fname[4:]}_{i+1:02d}", "d": col_def, "o": [rnd(x0), rnd(y0), rnd(w_z0)], "x": (1, 0, 0), "y": (0, 1, 0)})
        else:
            insts.append({"p": f"{path}/TASIYICI", "n": f"KOLON_{fname[4:]}_{i+1:02d}", "d": col_def, "o": [rnd(x1), rnd(y0), rnd(w_z0)], "x": (0, 1, 0), "y": (-1, 0, 0)})
    # ---- exterior openings
    openings = {"S": [], "N": [], "E": [], "W": []}   # (a,b, z0rel, z1rel, kind)
    door_gap_polys = []
    for g in ext_gaps:
        sd = side_of(g)
        a, b = along(g, sd)
        # window match
        win = None
        for wv in fd["wins"]:
            if wv["rot"] == 0: wa, wb, ws = wv["x"], wv["x"] + wv["w"], "S"
            elif wv["rot"] == 180: wa, wb, ws = wv["x"] - wv["w"], wv["x"], "N"
            elif wv["rot"] == 90: wa, wb, ws = wv["y"], wv["y"] + wv["w"], "E"
            else: wa, wb, ws = wv["y"] - wv["w"], wv["y"], "W"
            if ws == sd and abs(wa - a) < 1 and abs(wb - b) < 1:
                win = wv
        door = None
        for dv in fd["doors"]:
            if g.buffer(1).contains(Point(dv["x"], dv["y"])):
                door = dv
        cx, cy = g.centroid.x, g.centroid.y
        inward = {"S": (0, 40), "N": (0, -40), "E": (-40, 0), "W": (40, 0)}[sd]
        room = None
        for r in rooms:
            if r["poly"].contains(Point(cx + inward[0], cy + inward[1])):
                room = r["name"]
        if win:
            rule = win_rule(room)
            par, hh = rule if rule else (90, win["h_dxf"])
            openings[sd].append((a, b, par, par + hh, "W"))
            dn = window_def(b - a, hh)
            place_in_wall(f"{path}/DOGRAMA", f"{win['tip']}_{dn}", dn, sd, a, b, L + par, (T_EXT - FRAME_D) / 2)
            rep["windows"].append({"tip": win["tip"], "mahal": room, "cephe": sd, "aralik": [a, b], "genislik": b - a, "parapet": par, "yukseklik": hh, "dxf_yukseklik": win["h_dxf"], "bilesen": dn})
        elif door:
            openings[sd].append((a, b, -KAPLAMA, MAIN_DOOR_H, "D"))
            dn = entrance_def(b - a, MAIN_DOOR_H)
            place_in_wall(f"{path}/DOGRAMA", f"GIRIS_{dn}", dn, sd, a, b, L, (T_EXT - FRAME_D) / 2)
            door_gap_polys.append(g)
            rep["doors"].append({"tip": "ANA GIRIS", "cephe": sd, "aralik": [a, b], "yukseklik": MAIN_DOOR_H, "bilesen": dn})
        else:
            report["warnings"].append(f"{fname}: eslesmeyen dis bosluk {g.bounds}")
    # ---- exterior walls (stretches between columns)
    stretches = parts(BAND.difference(cols_u))
    for i, s in enumerate(stretches):
        sd = side_of(s)
        x0, y0, x1, y1 = s.bounds
        a, b = along(s, sd)
        t0, t1 = (y0, y1) if sd in "SN" else (x0, x1)
        ops = [(oa, ob, L + z0, L + z1) for (oa, ob, z0, z1, k) in openings[sd] if oa >= a - 0.01 and ob <= b + 0.01]
        elev_panel(f"{path}/DIS_DUVAR", f"DD_{fname[4:]}_{sd}_{i+1:02d}", "M_DIS_DUVAR", sd, a, b, t0, t1, w_z0, w_z1, ops)
    # ---- cladding (above ground floors only)
    if L >= 0:
        cz0 = L
        cz1 = L + KAT_H if fname == "KAT_00" else EAVE_Z + ROOF_SLOPE * ROOF_EAVE - ROOF_T
        pan = {"S": (-CEPHE, W + CEPHE, -CEPHE, 0), "N": (-CEPHE, W + CEPHE, D, D + CEPHE),
               "W": (0, D, -CEPHE, 0), "E": (0, D, W, W + CEPHE)}
        for sd, (a, b, t0, t1) in pan.items():
            ops = []
            for (oa, ob, z0, z1, k) in openings[sd]:
                ops.append((oa, ob, L + max(z0, 0), L + z1))
            elev_panel(f"{path}/CEPHE_KAPLAMA", f"CK_{fname[4:]}_{sd}", "M_CEPHE_KAPLAMA", sd, a, b, t0, t1, cz0, cz1, ops)
    # ---- interior walls
    for i, p in enumerate(parts(int_w)):
        add(f"{path}/IC_DUVAR", f"ID_{fname[4:]}_{i+1:02d}", "M_IC_DUVAR", plan_prism(p, w_z0, w_z1))
    # ---- interior gaps: doors / passages, lintels, threshold to rooms
    gap_to_room = {}
    for i, g in enumerate(int_gaps):
        x0, y0, x1, y1 = g.bounds
        thin_y = (y1 - y0) < (x1 - x0)
        wdt = (x1 - x0) if thin_y else (y1 - y0)
        has_door = None
        for dv in fd["doors"]:
            if g.buffer(1).contains(Point(dv["x"], dv["y"])):
                has_door = dv
        for dp in fd["doorpl"]:
            if g.buffer(1).intersects(dp):
                has_door = has_door or {"w": wdt}
        # adjacent rooms
        adj = [r for r in rooms if r["poly"].buffer(0.5).intersects(g) and r["poly"].buffer(0.5).intersection(g).area > 1]
        names = [r["name"] for r in adj]
        add(f"{path}/IC_DUVAR", f"LENTO_{fname[4:]}_{i+1:02d}", "M_IC_DUVAR", plan_prism(g, L + INT_OPEN_H, w_z1))
        if has_door:
            dn = door_def(round(wdt), INT_OPEN_H)
            if thin_y:
                insts.append({"p": f"{path}/DOGRAMA", "n": f"{dn}_{fname[4:]}_{i+1:02d}", "d": dn, "o": [rnd(x0), rnd(y0 + (y1 - y0 - 4) / 2), rnd(L)], "x": (1, 0, 0), "y": (0, 1, 0)})
            else:
                insts.append({"p": f"{path}/DOGRAMA", "n": f"{dn}_{fname[4:]}_{i+1:02d}", "d": dn, "o": [rnd(x0 + (x1 - x0 + 4) / 2), rnd(y0), rnd(L)], "x": (0, 1, 0), "y": (-1, 0, 0)})
            rep["doors"].append({"genislik": round(wdt), "mahaller": names, "bilesen": dn})
        else:
            rep["passages"].append({"genislik": round(wdt), "mahaller": names})
        # threshold kaplama: prefer dry room, skip shaft/stair
        cand = [r for r in adj if r["name"] not in ("ASANSÖR", "MERDIVEN")]
        dry = [r for r in cand if not any(k in r["name"] for k in ISLAK_KEYS)]
        tgt = (dry or cand or [None])[0]
        if tgt is not None:
            gap_to_room.setdefault(id(tgt), []).append(g)
    for g in door_gap_polys:
        for r in rooms:
            if r["poly"].buffer(0.5).intersection(g).area > 1:
                gap_to_room.setdefault(id(r), []).append(g)
                break
    # ---- slab
    holes = []
    if fname != "KAT_B1":
        for r in rooms:
            if r["name"] in ("ASANSÖR", "MERDIVEN"):
                holes.append(r["poly"])
    slab = FOOT.difference(unary_union(holes)) if holes else FOOT
    for i, p in enumerate(parts(slab)):
        add(f"{path}/DOSEME", f"DOSEME_{fname[4:]}" + ("" if i == 0 else f"_{i}"), "M_DOSEME", plan_prism(p, L - KAPLAMA - DOSEME, L - KAPLAMA))
    # ---- floor finish + ceiling
    used = {}
    for r in rooms:
        n = r["name"]
        if n == "ASANSÖR":
            continue
        if n == "MERDIVEN" and fname != "KAT_B1":
            pass
        key = asc(n)
        used[key] = used.get(key, 0) + 1
        if used[key] > 1: key = f"{key}_{used[key]}"
        islak = any(k in n for k in ISLAK_KEYS)
        sub = "DOSEME_KAPLAMA_ISLAK" if islak else "DOSEME_KAPLAMA_KURU"
        mat = "M_DOSEME_KAPLAMA_ISLAK" if islak else "M_DOSEME_KAPLAMA_KURU"
        if not (n == "MERDIVEN" and fname != "KAT_B1"):
            fp = unary_union([r["poly"]] + gap_to_room.get(id(r), []))
            for j, p in enumerate(parts(fp)):
                add(f"{path}/DOSEME_KAPLAMA/{sub}", f"DK_{key}" + ("" if j == 0 else f"_{j}"), mat, plan_prism(p, L - KAPLAMA, L))
        tz1 = (w_z1)
        if n != "MERDIVEN" or fname == "KAT_01":
            add(f"{path}/TAVAN", f"TV_{key}", "M_TAVAN", plan_prism(r["poly"], tz1 - TAVAN, tz1))
        rep["rooms"].append({"mahal": n, "grup": f"DK_{key}", "islak": islak, "alan_m2": round(r["poly"].area / 1e4, 2)})
    # ---- stair (B1 and 00): L stair from y=637 (flight1, x 20..130), winders, flight2 x 130..427
    if fname in ("KAT_B1", "KAT_00"):
        R = KAT_H / 24.0
        y0, tr, wst = 637.0, 27.0, 20.0
        pts = [(y0, 0.0)]
        for k in range(1, 10):
            pts += [(y0 + tr*(k-1), k*R), (y0 + tr*k, k*R)]
        pts += [(y0 + tr*9, 9*R - wst), (y0 + wst*tr/R, 0.0)]
        add(f"{path}/MERDIVEN", f"MRD_{fname[4:]}_KOL1", "M_MERDIVEN", prism(Polygon(pts), 110.0, (20.0, 0, L), (0, 1, 0), (0, 0, 1), (1, 0, 0)))
        wedges = [([(130, 880), (20, 880), (20, 925)], 10), ([(130, 880), (20, 925), (20, 990), (80, 990)], 11), ([(130, 880), (80, 990), (130, 990)], 12)]
        for pp, k in wedges:
            add(f"{path}/MERDIVEN", f"MRD_{fname[4:]}_DONUS_{k}", "M_MERDIVEN", plan_prism(Polygon(pp), L + k*R - R - wst, L + k*R))
        x0 = 130.0
        pts = [(x0, 12*R - wst), (x0, 13*R)]
        for j in range(11):
            pts += [(x0 + tr*j, (13+j)*R), (x0 + tr*(j+1), (13+j)*R)]
        pts = [pts[0]] + pts[1:]
        pts += [(x0 + tr*11, 23*R - wst)]
        add(f"{path}/MERDIVEN", f"MRD_{fname[4:]}_KOL2", "M_MERDIVEN", prism(Polygon(pts), 110.0, (0, 880.0, L), (1, 0, 0), (0, 0, 1), (0, 1, 0)))
        rep["merdiven"] = {"riht": round(R, 2), "basamak": tr, "rıht_sayisi": 24}
    rep["int_gaps"] = len(int_gaps); rep["ext_gaps"] = len(ext_gaps)
    report["floors"][fname] = rep

# ---------------- roof slab + hip roof ----------------
add("CATI/DOSEME", "DOSEME_CATI", "M_DOSEME", plan_prism(FOOT, 660.0, 690.0))
e = CEPHE + ROOF_EAVE
X0, Y0, X1, Y1 = -e, -e, W + e, D + e
half = (Y1 - Y0) / 2
rise = ROOF_SLOPE * half
ZR = EAVE_Z + rise
r1 = (X0 + half, Y0 + half); r2 = (X1 - half, Y0 + half)
top = [[X0, Y0, EAVE_Z], [X1, Y0, EAVE_Z], [X1, Y1, EAVE_Z], [X0, Y1, EAVE_Z], [r1[0], r1[1], ZR], [r2[0], r2[1], ZR]]
bot = [[a, b, c - ROOF_T] for a, b, c in top]
v = top + bot
A, B, C, Dd, R1, R2 = range(6)
f = [[[A, B, R2, R1]], [[B, C, R2]], [[C, Dd, R1, R2]], [[Dd, A, R1]]]
f += [[[6+i for i in reversed(l[0])]] for l in f]
for (p, q) in [(A, B), (B, C), (C, Dd), (Dd, A)]:
    f.append([[p+6, q+6, q, p]])
add("CATI/CATI", "CATI_KIRMA", "M_CATI", {"v": v, "f": f})
report["roof"] = {"saçak_ucu": [X0, Y0, X1, Y1], "mahya_kotu_cm": round(ZR, 2), "mahya_boyu_cm": r2[0] - r1[0], "yukselme_cm": round(rise, 2)}

# ---------------- ground ----------------
g0 = -CEPHE - GROUND_MARGIN
gpoly = box(g0, g0, W + CEPHE + GROUND_MARGIN, D + CEPHE + GROUND_MARGIN).difference(FOOT)
gpoly = orient(gpoly, 1.0)
ext = list(gpoly.exterior.coords)[:-1]; hole = list(gpoly.interiors[0].coords)[:-1]
verts = [[x, y, 0.0] for x, y in ext] + [[x, y, 0.0] for x, y in hole]
add("ARAZI", "ARAZI_ZEMIN", "M_ARAZI", {"v": verts, "f": [[list(range(len(ext))), list(range(len(ext), len(ext) + len(hole)))]], "open": True})

spec = {"solids": solids, "defs": defs, "insts": insts}
json.dump(spec, open(OUT, "w"), ensure_ascii=False)
json.dump(report, open(OUT.replace(".json", "_rapor.json"), "w"), ensure_ascii=False, indent=1, default=str)
print(len(solids), "solids", len(insts), "insts", len(defs), "defs")
print(json.dumps(report["warnings"], ensure_ascii=False))
for fn, r in report["floors"].items():
    print(fn, "ext", r["ext_gaps"], "int", r["int_gaps"], "doors", len(r["doors"]), "pass", r["passages"])
print(report["roof"])
