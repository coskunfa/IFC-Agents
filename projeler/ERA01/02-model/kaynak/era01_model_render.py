# ERA01 kontrol gorselleri: spec verisinden kucuk z-buffer rasterlastirici (SketchUp sahne kameralariyla ayni).
import sys, json, math
import numpy as np
import shapely
from shapely.geometry import Polygon
from PIL import Image, ImageDraw, ImageFont

spec = json.load(open(sys.argv[1]))
outdir = sys.argv[2]
cams = json.load(open(sys.argv[3]))
PAL = {"M_TASIYICI": "#6E6E6E", "M_DIS_DUVAR": "#A6A6A6", "M_IC_DUVAR": "#D0D0D0", "M_CEPHE_KAPLAMA": "#E6E6E6",
       "M_DOSEME": "#8C8C8C", "M_DOSEME_KAPLAMA_KURU": "#F2F2F2", "M_DOSEME_KAPLAMA_ISLAK": "#DADDE0", "M_TAVAN": "#FAFAFA",
       "M_DOGRAMA_KASA": "#4A4A4A", "M_DOGRAMA_CAM": "#BFC4C8", "M_MERDIVEN": "#BDBDBD", "M_CATI": "#959595", "M_ARAZI": "#C8C8C8"}

items = []
BX = {}
for b, t in spec["blocks"].items():
    th = math.radians(t["rot"]); c, s_ = math.cos(th), math.sin(th)
    BX["BLOK_" + b] = (c, s_, t["t"][0], t["t"][1])
def bx(path, p):
    k = path.split("/")[0]
    if k not in BX: return list(p)
    c, s_, tx, ty = BX[k]
    return [c*p[0] - s_*p[1] + tx, s_*p[0] + c*p[1] + ty, p[2]]
for g in spec["solids"]:
    V = [bx(g["p"], v) for v in g["v"]]
    for f in g["f"]:
        items.append((g["p"], g["m"], [[V[i] for i in l] for l in f], 1.0))
for ins in spec["insts"]:
    d = spec["defs"][ins["d"]]
    o = np.array(ins["o"], float); x = np.array(ins["x"], float); y = np.array(ins["y"], float); z = np.cross(x, y)
    tr = lambda p, _p=ins['p']: bx(_p, list(o + p[0]*x + p[1]*y + p[2]*z))
    for s in d["solids"]:
        V = s["v"]
        for f in s["f"]:
            items.append((ins["p"], s["m"], [[tr(V[i]) for i in l] for l in f], 1.0))
    for gl in d["glass"]:
        items.append((ins["p"], "M_DOGRAMA_CAM", [[tr(p) for p in gl]], 0.45))

def hexrgb(h):
    return np.array([int(h[i:i+2], 16) / 255 for i in (1, 3, 5)])

# triangulate faces once
tris = []  # (path, mat, alpha, normal, [tri arrays], loops)
for path, m, loops, alpha in items:
    P = [np.array(l, float) for l in loops]
    o = P[0]
    n = np.zeros(3)
    for i in range(len(o)):  # Newell
        a, b = o[i], o[(i+1) % len(o)]
        n += np.array([(a[1]-b[1])*(a[2]+b[2]), (a[2]-b[2])*(a[0]+b[0]), (a[0]-b[0])*(a[1]+b[1])])
    if np.linalg.norm(n) < 1e-9:
        continue
    n /= np.linalg.norm(n)
    if n[2] < -0.9:
        continue
    u = o[1] - o[0]; u /= np.linalg.norm(u); v = np.cross(n, u)
    to2 = lambda p: ((p - o[0]) @ u, (p - o[0]) @ v)
    poly = Polygon([to2(p) for p in P[0]], [[to2(p) for p in h] for h in P[1:]])
    if len(P[0]) == 3 and len(P) == 1:
        T = [P[0]]
    elif len(P[0]) == 4 and len(P) == 1:
        T = [P[0][[0, 1, 2]], P[0][[0, 2, 3]]]
    else:
        T = []
        for t in shapely.constrained_delaunay_triangles(poly.buffer(0)).geoms:
            cs = list(t.exterior.coords)[:3]
            T.append(np.array([o[0] + a*u + b*v for a, b in cs]))
    tris.append((path, m, alpha, n, T, P))

LIGHT = np.array([0.45, -0.6, 0.75]); LIGHT /= np.linalg.norm(LIGHT)

def render(cam, fn):
    Wp, Hp = int(cam.get("w", 16) * 100), int(cam.get("h", 10) * 100)
    hide = cam.get("hide", [])
    eye = np.array(cam["eye"], float); tgt = np.array(cam["target"], float)
    fwd = tgt - eye; fwd /= np.linalg.norm(fwd)
    up0 = np.array(cam.get("up", [0, 0, 1]), float)
    right = np.cross(fwd, up0); right /= np.linalg.norm(right)
    up = np.cross(right, fwd)
    persp = cam.get("persp", True)
    def proj(p):
        r = p - eye
        dz = r @ fwd
        if persp:
            return np.stack([(r @ right) / dz, (r @ up) / dz, dz], -1)
        return np.stack([r @ right, r @ up, dz], -1)
    sel = [t for t in tris if not any((seg == h or seg.endswith("_" + h)) for h in hide for seg in t[0].split("/"))]
    # bounds
    allp = np.concatenate([np.concatenate(t[5]) for t in sel if t[1] != "M_ARAZI" or cam.get("ground_bounds")])
    pp = proj(allp)
    x0, x1, y0, y1 = pp[:, 0].min(), pp[:, 0].max(), pp[:, 1].min(), pp[:, 1].max()
    s = min(Wp * 0.9 / (x1 - x0), Hp * 0.86 / (y1 - y0))
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    def scr(q):
        return np.stack([Wp/2 + (q[..., 0] - cx) * s, Hp/2 - (q[..., 1] - cy) * s + Hp*0.02, q[..., 2]], -1)
    zbuf = np.full((Hp, Wp), np.inf); img = np.ones((Hp, Wp, 3))
    glass = []
    def raster(T3, col, alpha, target_img):
        for t in T3:
            q = scr(proj(t))
            if persp and (q[:, 2] <= 1).any():
                continue
            xa, xb = int(max(0, math.floor(q[:, 0].min()))), int(min(Wp - 1, math.ceil(q[:, 0].max())))
            ya, yb = int(max(0, math.floor(q[:, 1].min()))), int(min(Hp - 1, math.ceil(q[:, 1].max())))
            if xa > xb or ya > yb:
                continue
            X, Y = np.meshgrid(np.arange(xa, xb + 1) + 0.5, np.arange(ya, yb + 1) + 0.5)
            (ax_, ay_, az_), (bx_, by_, bz_), (cx_, cy_, cz_) = q
            den = (by_ - cy_) * (ax_ - cx_) + (cx_ - bx_) * (ay_ - cy_)
            if abs(den) < 1e-12:
                continue
            l1 = ((by_ - cy_) * (X - cx_) + (cx_ - bx_) * (Y - cy_)) / den
            l2 = ((cy_ - ay_) * (X - cx_) + (ax_ - cx_) * (Y - cy_)) / den
            l3 = 1 - l1 - l2
            inside = (l1 >= -1e-6) & (l2 >= -1e-6) & (l3 >= -1e-6)
            if persp:
                Z = 1.0 / (l1 / az_ + l2 / bz_ + l3 / cz_)
            else:
                Z = l1 * az_ + l2 * bz_ + l3 * cz_
            zb = zbuf[ya:yb+1, xa:xb+1]
            m = inside & (Z < zb)
            if alpha < 1:
                sub = img[ya:yb+1, xa:xb+1]
                sub[m] = sub[m] * (1 - alpha) + col * alpha
            else:
                zb[m] = Z[m]
                img[ya:yb+1, xa:xb+1][m] = col
    for path, m, alpha, n, T, P in sel:
        if alpha < 1:
            glass.append((path, m, alpha, n, T, P)); continue
        c = P[0].mean(0)
        view = (c - eye) if persp else fwd
        nn = n if np.dot(n, view) < 0 else -n
        shade = 0.62 + 0.38 * max(0.0, float(nn @ LIGHT))
        raster(T, np.clip(hexrgb(PAL[m]) * shade, 0, 1), 1.0, img)
    # edges (depth tested)
    edge_px = []
    for path, m, alpha, n, T, P in sel:
        if m == "M_ARAZI":
            pass
        for l in P:
            k = len(l)
            for i in range(k):
                a, b = l[i], l[(i+1) % k]
                L = np.linalg.norm(b - a)
                ns = max(2, int(L / 3))
                ts = np.linspace(0, 1, ns)[:, None]
                pts = a + (b - a) * ts
                q = scr(proj(pts))
                if persp and (q[:, 2] <= 1).any():
                    continue
                xi = q[:, 0].astype(int); yi = q[:, 1].astype(int)
                ok = (xi >= 0) & (xi < Wp) & (yi >= 0) & (yi < Hp)
                xi, yi, zz = xi[ok], yi[ok], q[ok, 2]
                best = np.full(len(xi), np.inf)
                for dx in (-1, 0, 1):
                    for dy in (-1, 0, 1):
                        xx = np.clip(xi + dx, 0, Wp - 1); yy = np.clip(yi + dy, 0, Hp - 1)
                        best = np.minimum(best, zbuf[yy, xx])
                tol = (cam["edge_tol"] if "edge_tol" in cam else (2.0 if not persp else 0.004 * zz)) + 1.0
                vis = zz <= best + tol
                edge_px.append((xi[vis], yi[vis]))
    for path, m, alpha, n, T, P in glass:
        raster(T, hexrgb(PAL[m]), alpha, img)
    for xi, yi in edge_px:
        img[yi, xi] = img[yi, xi] * 0.25
    im = Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8))
    if cam.get("title"):
        dr = ImageDraw.Draw(im)
        try:
            ft = ImageFont.truetype("DejaVuSans.ttf", 22)
        except Exception:
            ft = ImageFont.load_default()
        dr.text((16, 12), cam["title"], fill=(30, 30, 30), font=ft)
    im.save(fn)

for c in cams:
    render(c, f"{outdir}/{c['file']}")
    print("ok", c["file"])
