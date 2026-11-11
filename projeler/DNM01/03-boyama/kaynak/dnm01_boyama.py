# -*- coding: utf-8 -*-
"""DNM01 Deneme Villa - konsept gri kat planı boyaması (PAFTA, v01).

Girdi : 00-girdi/DNM01_girdi_kullanici-revizyon_v01r.dxf (cm; giriş kat y 0..1010, 1. kat +1810)
Çıktı : 03-boyama/DNM01_boyama_giris-kat_v01.jpg, _1-kat_v01.jpg, _kat-planlari_v01.jpg
Ölçek : 1/100, 600 dpi  ->  2.3622 px/cm (gerçek)
Geometri (duvar, kolon, mahal poligonu, kapı, merdiven, pencere) DXF'ten birebir alınır;
mobilya DXF blok konum/ölçülerinde PAFTA tarafından vektörle yeniden çizilir.
Kullanım: python3 dnm01_boyama.py
"""
import math, os, random
from decimal import Decimal, ROUND_HALF_UP

import cairo
import ezdxf
import numpy as np
from ezdxf import bbox as ezbbox
from ezdxf import path as ezpath
from PIL import Image, ImageFilter
from shapely.geometry import Point, Polygon

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.abspath(os.path.join(HERE, "..", ".."))
ROOT = os.path.abspath(os.path.join(PROJ, "..", ".."))
DXF = os.path.join(PROJ, "00-girdi", "DNM01_girdi_kullanici-revizyon_v01r.dxf")
OUT = os.path.join(PROJ, "03-boyama")
LOGO = os.path.join(ROOT, "ofis-standartlari", "logolar", "IFC_Architects_logo_koyu.png")

DPI = 600
PXMM = DPI / 25.4            # px / mm (kağıt)
S = PXMM / 10.0              # px / cm (gerçek), 1/100 -> 2.3622
FONT = "Carlito"             # Calibri metrik eşdeğeri
random.seed(7)

# ---------------------------------------------------------------- palet
def hx(h, a=1.0):
    h = h.lstrip("#")
    return (int(h[0:2], 16) / 255, int(h[2:4], 16) / 255, int(h[4:6], 16) / 255, a)

C = dict(
    dry=hx("#DADAD8"), hall=hx("#E3E3E1"), kitchen=hx("#CFCFCC"), wet=hx("#C8CDD1"),
    stair=hx("#E7E7E5"), lift=hx("#BDBDBC"),
    wall=hx("#383838"), col=hx("#050505"),
    line=hx("#8A8A88"), line2=hx("#A9A9A7"), fine=hx("#BDBDBB"),
    white=hx("#FFFFFF"), off=hx("#F6F5F3"), off2=hx("#EEEDEA"),
    rug=hx("#E9E5DE"), rugb=hx("#D6CFC4"),
    sand=hx("#DDD5C8"), sage=hx("#C6CFC9"), taupe=hx("#D3CABD"), blush=hx("#E3D3CC"),
    grass=hx("#DCE5DA"), grass2=hx("#CCD9CA"), grass3=hx("#E7EDE4"),
    pave=hx("#D5D4CF"), paveb=hx("#BEBDB8"),
    text=hx("#2F2F2F"), text2=hx("#5A5A5A"), red=hx("#C8102E"),
    water=hx("#D5E3E8"), glass=hx("#8FA6B3"), dark=hx("#5E6164"),
)

# ---------------------------------------------------------------- DXF okuma
doc = ezdxf.readfile(DXF)
msp = doc.modelspace()

FLOORS = {
    "giris": dict(y0=-100, y1=1100, dy=0, name="GİRİŞ KAT PLANI", kot="±0.00"),
    "kat1": dict(y0=1700, y1=2900, dy=1810, name="1. KAT PLANI", kot="+3.50"),
}


def in_floor(fl, ymin, ymax):
    f = FLOORS[fl]
    return ymin >= f["y0"] and ymax <= f["y1"]


def ent_pts(e):
    return [(p[0], p[1]) for p in e.get_points("xy")]


def flat_paths(e):
    """Varlığı WCS çoklu çizgilerine çevirir (OCS/ayna dahil)."""
    out = []
    try:
        p = ezpath.make_path(e)
        for sp in p.sub_paths():
            pts = [(v.x, v.y) for v in sp.flattening(0.5)]
            if len(pts) > 1:
                out.append(pts)
    except Exception:
        pass
    return out


def area_dec(s):
    return Decimal(s).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)


def collect(fl):
    d = dict(walls=[], cols=[], areas=[], doors=[], stairs=[], doorrects=[], windows=[])
    labels = []
    for e in msp:
        t, lay = e.dxftype(), e.dxf.layer
        if t == "LWPOLYLINE":
            pts = ent_pts(e)
            ys = [p[1] for p in pts]
            if not in_floor(fl, min(ys), max(ys)):
                continue
            if lay == "2_IFC_Wall":
                d["walls"].append(pts)
            elif lay == "1_IFC_Concrete_Section":
                d["cols"].append(pts)
            elif lay == "0_IFC_Area":
                d["areas"].append(pts)
            elif lay in ("1_IFC_Stair", "2_IFC_Handrail"):
                d["stairs"] += flat_paths(e)
            elif lay == "1_IFC_Door":
                d["doorrects"].append(pts)
        elif t == "CIRCLE" and lay == "1_IFC_Stair":
            cy = e.dxf.center.y
            if FLOORS[fl]["y0"] < cy < FLOORS[fl]["y1"]:
                d["stairs"] += flat_paths(e)
        elif t == "INSERT":
            bb = ezbbox.extents(e.virtual_entities())
            if not bb.has_data or not in_floor(fl, bb.extmin.y, bb.extmax.y):
                continue
            n = e.dxf.name
            box = (bb.extmin.x, bb.extmin.y, bb.extmax.x, bb.extmax.y)
            if n.startswith("IFC_DOOR"):
                for v in e.virtual_entities():
                    for pl in flat_paths(v):
                        d["doors"].append((v.dxftype(), pl))
            elif n.startswith("IFC_PENCERE"):
                d["windows"].append(box)
            elif n == "0_IFC_ROOM_TEXT_50":
                at = {a.dxf.tag: a.dxf.text for a in e.attribs}
                labels.append((e.dxf.insert.x, e.dxf.insert.y, at.get("ROOM_NAME", ""), at.get("AREA", "")))
    # mahal eşleme
    rooms = []
    for pts in d["areas"]:
        poly = Polygon(pts)
        nm, ar = None, None
        for (x, y, n, a) in labels:
            if poly.contains(Point(x, y)):
                nm, ar = n, a
        if nm is None:
            nm, ar = "MERDİVEN", "%.2f" % (poly.area / 1e4)
        calc = poly.area / 1e4
        assert abs(calc - float(ar)) < 0.011, (nm, calc, ar)
        rooms.append(dict(name=nm, area=ar, poly=pts, shp=poly))
    d["rooms"] = rooms
    return d


# ---------------------------------------------------------------- cairo yardımcıları
def setc(ctx, c, a=None):
    if a is None:
        ctx.set_source_rgba(*c)
    else:
        ctx.set_source_rgba(c[0], c[1], c[2], a)


def shade(c, f):
    return (min(1, c[0] * f), min(1, c[1] * f), min(1, c[2] * f), c[3])


def poly_path(ctx, pts):
    ctx.move_to(*pts[0])
    for p in pts[1:]:
        ctx.line_to(*p)
    ctx.close_path()


def rrect(ctx, x, y, w, h, r):
    r = max(0, min(r, w / 2, h / 2))
    ctx.new_sub_path()
    ctx.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    ctx.arc(x + r, y + h - r, r, math.pi / 2, math.pi)
    ctx.arc(x + r, y + r, r, math.pi, 1.5 * math.pi)
    ctx.arc(x + w - r, y + r, r, 1.5 * math.pi, 2 * math.pi)
    ctx.close_path()


def fill_stroke(ctx, fill, stroke=None, lw=0.8):
    if fill is not None:
        setc(ctx, fill)
        if stroke is None:
            ctx.fill()
            return
        ctx.fill_preserve()
    if stroke is not None:
        setc(ctx, stroke)
        ctx.set_line_width(lw)
        ctx.stroke()
    else:
        ctx.new_path()


def lgrad(x0, y0, x1, y1, c0, c1):
    g = cairo.LinearGradient(x0, y0, x1, y1)
    g.add_color_stop_rgba(0, *c0)
    g.add_color_stop_rgba(1, *c1)
    return g


def surf_to_np(surf):
    surf.flush()
    w, h, st = surf.get_width(), surf.get_height(), surf.get_stride()
    a = np.ndarray(shape=(h, st), dtype=np.uint8, buffer=surf.get_data())
    return a[:, : w * 4].reshape(h, w, 4).copy()


_KEEP = []


def np_to_surf(arr):
    h, w = arr.shape[:2]
    st = cairo.ImageSurface.format_stride_for_width(cairo.FORMAT_ARGB32, w)
    buf = np.zeros((h, st), dtype=np.uint8)
    buf[:, : w * 4] = arr.reshape(h, w * 4)
    s = cairo.ImageSurface.create_for_data(memoryview(buf), cairo.FORMAT_ARGB32, w, h, st)
    _KEEP.append(buf)
    return s


def blur(surf, rad):
    arr = surf_to_np(surf)
    im = Image.fromarray(arr, "RGBA").filter(ImageFilter.GaussianBlur(rad))
    return np_to_surf(np.asarray(im))


class Layer:
    """Plan ile aynı dönüşüme sahip ayrı yüzey (gölge, ağaç)."""

    def __init__(self, W, H, mat):
        self.s = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
        self.c = cairo.Context(self.s)
        self.c.set_matrix(mat)


# ---------------------------------------------------------------- yazı
def wtext(ctx, x, y, s, size, bold=False, color=None, anchor="c", track=0.0, light=False):
    """Dünya (cm) koordinatında, ters çevrilmemiş yazı. size: cm (= kağıt mm x10)."""
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(1, -1)
    ctx.select_font_face(FONT, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD if bold else cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(size)
    w = text_width(ctx, s, track)
    cap = ctx.text_extents("H")[3]
    dx = {"c": -w / 2, "l": 0, "r": -w}[anchor]
    setc(ctx, color or C["text"])
    xx = dx
    for ch in s:
        ctx.move_to(xx, cap / 2)
        ctx.show_text(ch)
        xx += ctx.text_extents(ch)[4] + track
    ctx.restore()
    return w


def text_width(ctx, s, track=0.0):
    if track == 0:
        return ctx.text_extents(s)[4]
    return sum(ctx.text_extents(ch)[4] for ch in s) + track * (len(s) - 1)


# ---------------------------------------------------------------- mobilya (yerel koordinat:
# merkez orijin, genişlik x, derinlik y, SIRT +y, ÖN -y). place(): theta = bakış yönü
# 0 = güney(-y), 90 = doğu, 180 = kuzey, 270 = batı.
class place:
    def __init__(self, ctx, cx, cy, th):
        self.ctx, self.a = ctx, (cx, cy, th)

    def __enter__(self):
        self.ctx.save()
        self.ctx.translate(self.a[0], self.a[1])
        self.ctx.rotate(math.radians(self.a[2]))
        return self.ctx

    def __exit__(self, *a):
        self.ctx.restore()


LW = 0.75    # ana kontur (cm dünya = 0.075 mm kağıt)
LWF = 0.45   # ince detay


def soft_fill(ctx, w, d, c=None):
    c = c or C["white"]
    return lgrad(0, d / 2, 0, -d / 2, shade(c, 0.965), c)


def sofa(ctx, w, d):
    arm, back = 17, 19
    rrect(ctx, -w / 2, -d / 2, w, d, 9)
    fill_stroke(ctx, C["off"], C["line"], LW)
    rrect(ctx, -w / 2 + 1, d / 2 - back, w - 2, back - 1, 8)
    ctx.set_source(lgrad(0, d / 2, 0, d / 2 - back, C["off2"], C["off"]))
    ctx.fill_preserve(); setc(ctx, C["line2"]); ctx.set_line_width(LWF); ctx.stroke()
    for sx in (-1, 1):
        x = -w / 2 + 1 if sx < 0 else w / 2 - arm - 1
        rrect(ctx, x, -d / 2 + 1, arm, d - 2, 8)
        fill_stroke(ctx, C["off2"], C["line2"], LWF)
    n = 3
    iw = (w - 2 * arm - 4) / n
    for i in range(n):
        x = -w / 2 + arm + 2 + i * iw
        rrect(ctx, x + 1, -d / 2 + 3, iw - 2, d - back - 5, 7)
        ctx.set_source(lgrad(0, d / 2 - back, 0, -d / 2, hx("#F3F2EF"), C["white"]))
        ctx.fill_preserve(); setc(ctx, C["line2"]); ctx.set_line_width(LWF); ctx.stroke()
        # dikiş izi
        ctx.move_to(x + 8, -d / 2 + 9); ctx.line_to(x + iw - 8, -d / 2 + 9)
        setc(ctx, C["fine"]); ctx.set_line_width(0.3); ctx.stroke()
    # yastıklar
    for (px, ang, col) in ((-w / 2 + arm + 26, -14, C["sand"]), (-w / 2 + arm + 58, 8, C["sage"]),
                           (w / 2 - arm - 30, 12, C["sand"])):
        with place(ctx, px, d / 2 - back - 7, ang):
            rrect(ctx, -21, -8, 42, 16, 6)
            ctx.set_source(lgrad(0, 8, 0, -8, shade(col, 0.95), col))
            ctx.fill_preserve(); setc(ctx, C["line2"]); ctx.set_line_width(LWF); ctx.stroke()
            ctx.move_to(-15, 0); ctx.curve_to(-5, 2, 5, -2, 15, 0)
            setc(ctx, shade(col, 0.85)); ctx.set_line_width(0.35); ctx.stroke()
    # koltuk kolunda örtü
    with place(ctx, w / 2 - arm / 2 - 1, -4, 0):
        rrect(ctx, -arm / 2 - 3, -22, arm + 6, 44, 3)
        fill_stroke(ctx, C["taupe"], C["line2"], LWF)
        for k in (-14, -8, 8, 14):
            ctx.move_to(-arm / 2 - 2, k); ctx.line_to(arm / 2 + 2, k)
        setc(ctx, shade(C["taupe"], 0.88)); ctx.set_line_width(0.35); ctx.stroke()


def armchair(ctx, w, d, pillow=C["blush"]):
    arm, back = 13, 15
    rrect(ctx, -w / 2, -d / 2, w, d, 14)
    fill_stroke(ctx, C["off"], C["line"], LW)
    rrect(ctx, -w / 2 + 2, d / 2 - back, w - 4, back - 2, 10)
    fill_stroke(ctx, C["off2"], C["line2"], LWF)
    for sx in (-1, 1):
        x = -w / 2 + 2 if sx < 0 else w / 2 - arm - 2
        rrect(ctx, x, -d / 2 + 3, arm, d - 6, 9)
        fill_stroke(ctx, C["off2"], C["line2"], LWF)
    rrect(ctx, -w / 2 + arm + 3, -d / 2 + 4, w - 2 * arm - 6, d - back - 6, 10)
    ctx.set_source(lgrad(0, d / 2, 0, -d / 2, hx("#F1F0ED"), C["white"]))
    ctx.fill_preserve(); setc(ctx, C["line2"]); ctx.set_line_width(LWF); ctx.stroke()
    with place(ctx, 4, d / 2 - back - 6, 10):
        rrect(ctx, -16, -7, 32, 14, 6)
        fill_stroke(ctx, pillow, C["line2"], LWF)


def round_table(ctx, r, deco=True):
    ctx.arc(0, 0, r, 0, 2 * math.pi)
    g = cairo.RadialGradient(-r * 0.3, r * 0.3, r * 0.1, 0, 0, r)
    g.add_color_stop_rgba(0, *C["white"]); g.add_color_stop_rgba(1, *hx("#F1F0EC"))
    ctx.set_source(g); ctx.fill_preserve(); setc(ctx, C["line"]); ctx.set_line_width(LW); ctx.stroke()
    ctx.arc(0, 0, r - 3.5, 0, 2 * math.pi); setc(ctx, C["fine"]); ctx.set_line_width(0.35); ctx.stroke()
    if deco and r > 40:
        # tepsi, kitaplar, vazo
        ctx.arc(-r * 0.25, r * 0.15, r * 0.28, 0, 2 * math.pi)
        fill_stroke(ctx, hx("#EEEAE3"), C["line2"], LWF)
        ctx.arc(-r * 0.25, r * 0.15, r * 0.09, 0, 2 * math.pi)
        fill_stroke(ctx, hx("#B9C4B4"), C["line2"], 0.35)
        with place(ctx, r * 0.32, -r * 0.2, 18):
            rrect(ctx, -14, -10, 28, 20, 1); fill_stroke(ctx, hx("#E4DED4"), C["line2"], LWF)
            rrect(ctx, -11, -7, 22, 14, 1); fill_stroke(ctx, hx("#F4F2EE"), C["line2"], 0.35)
    elif deco:
        ctx.arc(0, 0, r * 0.35, 0, 2 * math.pi)
        fill_stroke(ctx, hx("#E9E4DB"), C["line2"], 0.35)


def square_table(ctx, w, lamp=True):
    rrect(ctx, -w / 2, -w / 2, w, w, 3)
    fill_stroke(ctx, C["white"], C["line"], LW)
    if lamp:
        ctx.arc(0, 0, w * 0.26, 0, 2 * math.pi)
        fill_stroke(ctx, hx("#F5F1E9"), C["line2"], LWF)
        ctx.arc(0, 0, w * 0.09, 0, 2 * math.pi)
        fill_stroke(ctx, hx("#E2DACB"), C["line2"], 0.35)


def rug(ctx, x0, y0, x1, y1, col=None, round_=False):
    col = col or C["rug"]
    if round_:
        cx, cy, r = (x0 + x1) / 2, (y0 + y1) / 2, (x1 - x0) / 2
        ctx.arc(cx, cy, r, 0, 2 * math.pi); fill_stroke(ctx, col, C["rugb"], 0.5)
        for k in (6, 14):
            ctx.arc(cx, cy, r - k, 0, 2 * math.pi)
            setc(ctx, C["rugb"]); ctx.set_line_width(0.35); ctx.stroke()
        return
    rrect(ctx, x0, y0, x1 - x0, y1 - y0, 2)
    fill_stroke(ctx, col, C["rugb"], 0.5)
    rrect(ctx, x0 + 7, y0 + 7, x1 - x0 - 14, y1 - y0 - 14, 1)
    setc(ctx, C["rugb"]); ctx.set_line_width(0.4); ctx.stroke()
    rrect(ctx, x0 + 11, y0 + 11, x1 - x0 - 22, y1 - y0 - 22, 1)
    setc(ctx, C["rugb"], 0.6); ctx.set_line_width(0.3); ctx.stroke()


def dining_chair(ctx, w=47, d=54):
    rrect(ctx, -w / 2 + 2, -d / 2 + 2, w - 4, d - 12, 11)
    ctx.set_source(lgrad(0, d / 2, 0, -d / 2, hx("#F2F1EE"), C["white"]))
    ctx.fill_preserve(); setc(ctx, C["line"]); ctx.set_line_width(LW); ctx.stroke()
    ctx.move_to(-w / 2 + 3, d / 2 - 12)
    ctx.curve_to(-w / 4, d / 2 - 2, w / 4, d / 2 - 2, w / 2 - 3, d / 2 - 12)
    ctx.curve_to(w / 4, d / 2 - 7, -w / 4, d / 2 - 7, -w / 2 + 3, d / 2 - 12)
    fill_stroke(ctx, C["off2"], C["line"], LWF)


def dining(ctx, x0, y0, x1, y1, chairs):
    for (cx, cy, th) in chairs:
        with place(ctx, cx, cy, th):
            dining_chair(ctx)
    rrect(ctx, x0, y0, x1 - x0, y1 - y0, 6)
    ctx.set_source(lgrad(x0, y1, x1, y0, C["white"], hx("#F2F1ED")))
    ctx.fill_preserve(); setc(ctx, C["line"]); ctx.set_line_width(LW); ctx.stroke()
    rrect(ctx, x0 + 3, y0 + 3, x1 - x0 - 6, y1 - y0 - 6, 4)
    setc(ctx, C["fine"]); ctx.set_line_width(0.3); ctx.stroke()
    cy = (y0 + y1) / 2
    rrect(ctx, x0 + 45, cy - 14, x1 - x0 - 90, 28, 2)
    fill_stroke(ctx, hx("#ECE8E1"), C["line2"], 0.35)
    for (cx, _, th) in chairs:
        py = y0 + 17 if th == 180 else y1 - 17
        ctx.arc(cx, py, 11, 0, 2 * math.pi); fill_stroke(ctx, C["white"], C["line2"], 0.35)
        ctx.arc(cx, py, 7, 0, 2 * math.pi); setc(ctx, C["fine"]); ctx.set_line_width(0.3); ctx.stroke()
    mx = (x0 + x1) / 2
    for dx, r in ((-28, 8), (0, 10), (26, 7)):
        ctx.arc(mx + dx, cy, r, 0, 2 * math.pi)
        fill_stroke(ctx, hx("#F7F5F1"), C["line2"], 0.4)
    for dx in (-28, 0, 26):
        leaves(ctx, mx + dx, cy, 6, n=5)


def leaves(ctx, cx, cy, r, n=7, cols=None):
    cols = cols or [hx("#9DAE98"), hx("#8DA08A"), hx("#B3C0AC")]
    for i in range(n):
        a = 2 * math.pi * i / n + random.uniform(-0.3, 0.3)
        with place(ctx, cx + math.cos(a) * r * 0.45, cy + math.sin(a) * r * 0.45, math.degrees(a) + 90):
            ctx.save(); ctx.scale(r * 0.32, r * 0.62)
            ctx.arc(0, 0, 1, 0, 2 * math.pi); ctx.restore()
            setc(ctx, random.choice(cols), 0.85); ctx.fill()


def plant(ctx, cx, cy, r):
    ctx.arc(cx, cy, r * 0.62, 0, 2 * math.pi)
    fill_stroke(ctx, hx("#E4E0D8"), C["line"], LWF)
    leaves(ctx, cx, cy, r * 1.25, n=9)
    leaves(ctx, cx, cy, r * 0.8, n=6, cols=[hx("#A8B8A2"), hx("#BFCBB8")])


def bed(ctx, w, l, throw=C["taupe"]):
    # yerel: genişlik x, boy y, başlık +y
    rrect(ctx, -w / 2 - 3, -l / 2, w + 6, l, 4)
    fill_stroke(ctx, C["off"], C["line"], LW)
    rrect(ctx, -w / 2 - 5, l / 2 - 9, w + 10, 9, 3)
    fill_stroke(ctx, hx("#E7E4DF"), C["line"], LWF)
    # yorgan
    top = l / 2 - 60
    rrect(ctx, -w / 2 - 1, -l / 2 + 2, w + 2, top + l / 2 - 2, 5)
    ctx.set_source(lgrad(-w / 2, top, w / 2, -l / 2, C["white"], hx("#F1F0ED")))
    ctx.fill_preserve(); setc(ctx, C["line2"]); ctx.set_line_width(LWF); ctx.stroke()
    # kıvrım izleri
    setc(ctx, C["fine"]); ctx.set_line_width(0.35)
    for (ax, ay, bx, by) in ((-w * 0.3, top - 25, -w * 0.05, top - 55), (w * 0.15, top - 15, w * 0.35, top - 70),
                             (-w * 0.38, -l * 0.05, -w * 0.15, -l * 0.18)):
        ctx.move_to(ax, ay); ctx.curve_to(ax + 8, ay - 10, bx - 6, by + 12, bx, by); ctx.stroke()
    # katlanmış çarşaf bandı
    rrect(ctx, -w / 2 - 1, top - 3, w + 2, 14, 3)
    fill_stroke(ctx, hx("#FAFAF8"), C["line2"], LWF)
    ctx.move_to(-w / 2 + 2, top + 4); ctx.curve_to(-w / 4, top + 6, w / 4, top + 2, w / 2 - 2, top + 4)
    setc(ctx, C["fine"]); ctx.set_line_width(0.3); ctx.stroke()
    # yastıklar
    pw = (w - 18) / 2
    for sx in (-1, 1):
        x = -pw - 3 if sx < 0 else 3
        rrect(ctx, x, l / 2 - 46, pw, 33, 9)
        ctx.set_source(lgrad(0, l / 2 - 13, 0, l / 2 - 46, hx("#F4F3F0"), C["white"]))
        ctx.fill_preserve(); setc(ctx, C["line2"]); ctx.set_line_width(LWF); ctx.stroke()
        rrect(ctx, x + 5, l / 2 - 41, pw - 10, 23, 7)
        setc(ctx, C["fine"]); ctx.set_line_width(0.3); ctx.stroke()
    # dekor yastık
    with place(ctx, 0, l / 2 - 52, 0):
        rrect(ctx, -20, -7, 40, 14, 6); fill_stroke(ctx, C["sage"], C["line2"], LWF)
    # ayak ucunda şal
    rrect(ctx, -w / 2 - 6, -l / 2 + 10, w + 12, 30, 3)
    fill_stroke(ctx, throw, C["line2"], LWF)
    setc(ctx, shade(throw, 0.88)); ctx.set_line_width(0.35)
    for k in (16, 34):
        ctx.move_to(-w / 2 - 5, -l / 2 + k); ctx.line_to(w / 2 + 5, -l / 2 + k); ctx.stroke()


def nightstand(ctx, w, d):
    rrect(ctx, -w / 2, -d / 2, w, d, 3)
    fill_stroke(ctx, C["white"], C["line"], LW)
    ctx.arc(0, 1, min(w, d) * 0.28, 0, 2 * math.pi)
    fill_stroke(ctx, hx("#F6F2EA"), C["line2"], LWF)
    ctx.arc(0, 1, min(w, d) * 0.1, 0, 2 * math.pi)
    fill_stroke(ctx, hx("#E1D9CA"), C["line2"], 0.3)


def wardrobe(ctx, w, d):
    rrect(ctx, -w / 2, -d / 2, w, d, 1.5)
    fill_stroke(ctx, hx("#F7F7F5"), C["line"], LW)
    n = max(2, round(w / 55))
    setc(ctx, C["line2"]); ctx.set_line_width(LWF)
    for i in range(1, n):
        x = -w / 2 + i * w / n
        ctx.move_to(x, -d / 2); ctx.line_to(x, -d / 2 + 6); ctx.stroke()
    ctx.move_to(-w / 2, -d / 2 + 2.5); ctx.line_to(w / 2, -d / 2 + 2.5); ctx.stroke()
    ctx.set_dash([4, 3]); ctx.set_line_width(0.35); setc(ctx, C["fine"])
    ctx.move_to(-w / 2 + 4, 4); ctx.line_to(w / 2 - 4, 4); ctx.stroke(); ctx.set_dash([])
    # askılar
    setc(ctx, C["fine"]); ctx.set_line_width(0.3)
    x = -w / 2 + 8
    while x < w / 2 - 6:
        ctx.move_to(x, 4 - 17); ctx.line_to(x + 1.5, 4 + 17); ctx.stroke()
        x += random.uniform(5, 9)


def low_unit(ctx, w, d, tv=0):
    rrect(ctx, -w / 2, -d / 2, w, d, 2)
    fill_stroke(ctx, C["white"], C["line"], LW)
    setc(ctx, C["line2"]); ctx.set_line_width(LWF)
    n = max(2, round(w / 60))
    for i in range(1, n):
        x = -w / 2 + i * w / n
        ctx.move_to(x, -d / 2 + 3); ctx.line_to(x, d / 2 - 3); ctx.stroke()
    if tv:
        rrect(ctx, -tv / 2, d / 2 - 9, tv, 4.5, 1)
        fill_stroke(ctx, hx("#4C4D4F"), None)
    # dekor
    ctx.arc(w / 2 - 22, -2, 7, 0, 2 * math.pi); fill_stroke(ctx, hx("#F2EEE7"), C["line2"], 0.4)
    leaves(ctx, w / 2 - 22, -2, 7, n=5)
    rrect(ctx, -w / 2 + 12, -8, 26, 16, 1); fill_stroke(ctx, hx("#E6E0D6"), C["line2"], 0.35)


def arc_lamp(ctx, shade_c, base_c, r=34):
    ctx.move_to(*base_c)
    mx, my = (shade_c[0] + base_c[0]) / 2 + 25, (shade_c[1] + base_c[1]) / 2 - 25
    ctx.curve_to(mx, my, mx, my, shade_c[0] + r * 0.6, shade_c[1] + r * 0.6)
    setc(ctx, C["line"]); ctx.set_line_width(1.0); ctx.stroke()
    ctx.arc(base_c[0], base_c[1], 13, 0, 2 * math.pi)
    fill_stroke(ctx, hx("#E3E1DD"), C["line"], LWF)
    ctx.arc(shade_c[0], shade_c[1], r, 0, 2 * math.pi)
    g = cairo.RadialGradient(shade_c[0], shade_c[1], 2, shade_c[0], shade_c[1], r)
    g.add_color_stop_rgba(0, *hx("#FFFDF8")); g.add_color_stop_rgba(1, *hx("#F1EDE5"))
    ctx.set_source(g); ctx.fill_preserve(); setc(ctx, C["line"]); ctx.set_line_width(LWF); ctx.stroke()
    ctx.arc(shade_c[0], shade_c[1], 6, 0, 2 * math.pi); fill_stroke(ctx, hx("#E5DED0"), C["line2"], 0.3)


def counter(ctx, x0, y0, x1, y1, front):
    """front: 'n','s','e','w' tezgâh ön yüzü."""
    ctx.rectangle(x0, y0, x1 - x0, y1 - y0)
    ctx.set_source(lgrad(x0, y1, x1, y0, hx("#F7F7F6"), hx("#EFEFED")))
    ctx.fill_preserve(); setc(ctx, C["line"]); ctx.set_line_width(LW); ctx.stroke()
    setc(ctx, C["line2"]); ctx.set_line_width(0.4)
    if front in "ew":
        fx = x1 - 3 if front == "e" else x0 + 3
        ctx.move_to(fx, y0); ctx.line_to(fx, y1); ctx.stroke()
    else:
        fy = y1 - 3 if front == "n" else y0 + 3
        ctx.move_to(x0, fy); ctx.line_to(x1, fy); ctx.stroke()


def sink_double(ctx, w, d):
    rrect(ctx, -w / 2, -d / 2, w, d, 3); fill_stroke(ctx, hx("#E8EBED"), C["line"], LWF)
    bw = (w - 14) * 0.6
    rrect(ctx, -w / 2 + 5, -d / 2 + 5, bw, d - 12, 4); fill_stroke(ctx, hx("#DCE1E4"), C["line2"], LWF)
    ctx.arc(-w / 2 + 5 + bw / 2, -1, 2.2, 0, 2 * math.pi); fill_stroke(ctx, None, C["line2"], 0.4)
    rrect(ctx, -w / 2 + 9 + bw, -d / 2 + 5, w - 14 - bw, d - 12, 4); fill_stroke(ctx, hx("#DCE1E4"), C["line2"], LWF)
    ctx.arc(-w / 2 + 5 + bw, d / 2 - 4, 2, 0, 2 * math.pi); fill_stroke(ctx, hx("#C9CED1"), None)
    ctx.move_to(-w / 2 + 5 + bw, d / 2 - 4); ctx.line_to(-w / 2 + 5 + bw - 8, d / 2 - 14)
    setc(ctx, C["line"]); ctx.set_line_width(1.2); ctx.stroke()


def hob(ctx, w, d):
    rrect(ctx, -w / 2, -d / 2, w, d, 3)
    ctx.set_source(lgrad(-w / 2, d / 2, w / 2, -d / 2, hx("#6F7275"), hx("#5D6063")))
    ctx.fill_preserve(); setc(ctx, C["line"]); ctx.set_line_width(LWF); ctx.stroke()
    for (x, y, r) in ((-w / 4, d / 4, 8), (w / 4, d / 4, 6.5), (-w / 4, -d / 4, 6.5), (w / 4, -d / 4, 9)):
        ctx.arc(x, y, r, 0, 2 * math.pi); setc(ctx, hx("#A3A6A9")); ctx.set_line_width(0.45); ctx.stroke()
        ctx.arc(x, y, r * 0.55, 0, 2 * math.pi); ctx.stroke()


def fridge(ctx, w, d):
    rrect(ctx, -w / 2, -d / 2, w, d, 2)
    ctx.set_source(lgrad(-w / 2, d / 2, w / 2, -d / 2, hx("#F4F5F6"), hx("#E6E8E9")))
    ctx.fill_preserve(); setc(ctx, C["line"]); ctx.set_line_width(LW); ctx.stroke()
    ctx.move_to(0, -d / 2); ctx.line_to(0, d / 2 - 4); setc(ctx, C["line2"]); ctx.set_line_width(LWF); ctx.stroke()
    for sx in (-1, 1):
        ctx.move_to(sx * 4, -d / 2 + 1); ctx.line_to(sx * 4, -d / 2 + 14)
        setc(ctx, C["line"]); ctx.set_line_width(1.0); ctx.stroke()


def island(ctx, x0, y0, x1, y1):
    rrect(ctx, x0, y0, x1 - x0, y1 - y0, 2)
    ctx.set_source(lgrad(x0, y1, x1, y0, hx("#FDFDFC"), hx("#EEEDEA")))
    ctx.fill_preserve(); setc(ctx, C["line"]); ctx.set_line_width(LW); ctx.stroke()
    setc(ctx, hx("#DCDAD5")); ctx.set_line_width(0.35)
    for k in range(4):     # taş damarı
        sx = x0 + 20 + k * 55
        ctx.move_to(sx, y0 + 4); ctx.curve_to(sx + 25, y0 + 35, sx + 5, y1 - 40, sx + 40, y1 - 4); ctx.stroke()
    ctx.move_to(x0, y1 - 28); ctx.line_to(x1, y1 - 28)
    setc(ctx, C["line2"]); ctx.set_line_width(0.4); ctx.stroke()
    # meyve kasesi
    ctx.arc(x0 + 60, (y0 + y1) / 2 - 10, 14, 0, 2 * math.pi); fill_stroke(ctx, C["white"], C["line2"], 0.45)
    for (dx, dy, c) in ((-4, 3, "#E7C9A9"), (5, 2, "#D9DDB4"), (0, -5, "#E5C3B5")):
        ctx.arc(x0 + 60 + dx, (y0 + y1) / 2 - 10 + dy, 4, 0, 2 * math.pi); fill_stroke(ctx, hx(c), None)


def stool(ctx, r=18):
    ctx.arc(0, 0, r, 0, 2 * math.pi)
    ctx.set_source(lgrad(0, r, 0, -r, hx("#F1F0ED"), C["white"]))
    ctx.fill_preserve(); setc(ctx, C["line"]); ctx.set_line_width(LW); ctx.stroke()
    ctx.arc(0, 0, r + 1, math.radians(35), math.radians(145))
    setc(ctx, C["line"]); ctx.set_line_width(2.6); ctx.stroke()


def toilet(ctx):
    # yerel: rezervuar +y (duvar)
    rrect(ctx, -18, 10, 36, 17, 4); fill_stroke(ctx, C["white"], C["line"], LW)
    ctx.save(); ctx.translate(0, -6); ctx.scale(17, 22); ctx.arc(0, 0, 1, 0, 2 * math.pi); ctx.restore()
    fill_stroke(ctx, C["white"], C["line"], LW)
    ctx.save(); ctx.translate(0, -7); ctx.scale(11.5, 15); ctx.arc(0, 0, 1, 0, 2 * math.pi); ctx.restore()
    fill_stroke(ctx, hx("#EEF2F4"), C["line2"], LWF)
    rrect(ctx, -5, 17, 10, 5, 2); fill_stroke(ctx, hx("#E2E6E8"), C["line2"], 0.35)


def vanity(ctx, w, d, n=1):
    rrect(ctx, -w / 2, -d / 2, w, d, 2); fill_stroke(ctx, C["white"], C["line"], LW)
    for i in range(n):
        cx = -w / 2 + (i + 0.5) * w / n
        ctx.save(); ctx.translate(cx, -2); ctx.scale(min(20, w / n * 0.36), d * 0.3)
        ctx.arc(0, 0, 1, 0, 2 * math.pi); ctx.restore()
        fill_stroke(ctx, hx("#EEF2F4"), C["line2"], LWF)
        ctx.arc(cx, -2, 1.6, 0, 2 * math.pi); fill_stroke(ctx, hx("#B9BFC3"), None)
        ctx.move_to(cx, d / 2 - 3); ctx.line_to(cx, d / 2 - 12)
        setc(ctx, C["line"]); ctx.set_line_width(1.3); ctx.stroke()
    if n == 1:
        ctx.arc(w / 2 - 9, d / 2 - 10, 3.5, 0, 2 * math.pi); fill_stroke(ctx, hx("#E9E3D8"), C["line2"], 0.3)


def shower(ctx, w, d, glass_sides):
    """glass_sides: dünya-yerel kenarlar listesi ('n','s','e','w') - yerel çerçevede."""
    ctx.rectangle(-w / 2, -d / 2, w, d)
    ctx.set_source(lgrad(-w / 2, d / 2, w / 2, -d / 2, hx("#EAEFF1"), hx("#DCE3E7")))
    ctx.fill_preserve(); setc(ctx, C["line2"]); ctx.set_line_width(LWF); ctx.stroke()
    setc(ctx, hx("#CBD3D8")); ctx.set_line_width(0.3)
    k = -w / 2 + 15
    while k < w / 2:
        ctx.move_to(k, -d / 2); ctx.line_to(k, d / 2); ctx.stroke(); k += 15
    k = -d / 2 + 15
    while k < d / 2:
        ctx.move_to(-w / 2, k); ctx.line_to(w / 2, k); ctx.stroke(); k += 15
    ctx.rectangle(-8, -2, 16, 4); fill_stroke(ctx, hx("#B7C0C6"), None)
    setc(ctx, C["glass"]); ctx.set_line_width(1.4)
    for sd in glass_sides:
        if sd == "s":
            ctx.move_to(-w / 2, -d / 2 + 1); ctx.line_to(w / 2, -d / 2 + 1)
        if sd == "n":
            ctx.move_to(-w / 2, d / 2 - 1); ctx.line_to(w / 2, d / 2 - 1)
        if sd == "w":
            ctx.move_to(-w / 2 + 1, -d / 2); ctx.line_to(-w / 2 + 1, d / 2)
        if sd == "e":
            ctx.move_to(w / 2 - 1, -d / 2); ctx.line_to(w / 2 - 1, d / 2)
        ctx.stroke()
    ctx.arc(w / 2 - 12, d / 2 - 12, 7, 0, 2 * math.pi); fill_stroke(ctx, hx("#F2F5F6"), C["line2"], 0.4)


def jacuzzi(ctx, w, d):
    rrect(ctx, -w / 2, -d / 2, w, d, 10); fill_stroke(ctx, C["white"], C["line"], LW)
    rrect(ctx, -w / 2 + 9, -d / 2 + 9, w - 18, d - 18, 26)
    g = cairo.RadialGradient(0, 0, 5, 0, 0, w / 2)
    g.add_color_stop_rgba(0, *hx("#E3EDF1")); g.add_color_stop_rgba(1, *hx("#CFDDE3"))
    ctx.set_source(g); ctx.fill_preserve(); setc(ctx, C["line2"]); ctx.set_line_width(LWF); ctx.stroke()
    for (x, y) in ((-w / 2 + 20, 0), (w / 2 - 20, 0), (0, -d / 2 + 16), (0, d / 2 - 16)):
        ctx.arc(x, y, 2.4, 0, 2 * math.pi); fill_stroke(ctx, hx("#B3C2C9"), None)
    rrect(ctx, -w / 2 + 12, -14, 16, 28, 6); fill_stroke(ctx, hx("#F4F4F2"), C["line2"], 0.4)


def lift(ctx, x0, y0, x1, y1):
    ctx.rectangle(x0, y0, x1 - x0, y1 - y0)
    fill_stroke(ctx, hx("#F1F1F0"), C["line"], LW)
    ctx.rectangle(x0 + 5, y0 + 5, x1 - x0 - 10, y1 - y0 - 10)
    setc(ctx, C["line2"]); ctx.set_line_width(0.4); ctx.stroke()


# ---------------------------------------------------------------- peyzaj
def wc_blob(ctx, cx, cy, r, col, alpha, n=18, spread=1.0):
    for _ in range(n):
        a = random.uniform(0, 2 * math.pi)
        rr = random.uniform(0, r * 0.62) * spread
        br = random.uniform(r * 0.25, r * 0.5)
        ctx.arc(cx + math.cos(a) * rr, cy + math.sin(a) * rr, br, 0, 2 * math.pi)
        setc(ctx, col, alpha * random.uniform(0.6, 1.2)); ctx.fill()


def tree(ctx, sh, cx, cy, r, kind="green"):
    # gölge
    sh.arc(cx + r * 0.22, cy - r * 0.22, r * 0.95, 0, 2 * math.pi)
    sh.set_source_rgba(0, 0, 0, 1); sh.fill()
    if kind == "green":
        cols = [hx("#9FB39A"), hx("#B6C6AF"), hx("#8AA088"), hx("#C9D5C1")]
    else:
        cols = [hx("#A8B7A0"), hx("#BCC8B4"), hx("#97A890"), hx("#CBD5C4")]
    wc_blob(ctx, cx, cy, r, cols[2], 0.35, n=14)
    wc_blob(ctx, cx, cy, r, cols[0], 0.35, n=26)
    wc_blob(ctx, cx - r * 0.15, cy + r * 0.15, r * 0.8, cols[1], 0.35, n=20)
    wc_blob(ctx, cx - r * 0.25, cy + r * 0.25, r * 0.45, cols[3], 0.45, n=12)
    if kind == "flower":
        for _ in range(int(r * 1.3)):
            a = random.uniform(0, 2 * math.pi); rr = random.uniform(0, r * 0.85)
            ctx.arc(cx + math.cos(a) * rr, cy + math.sin(a) * rr, random.uniform(2.5, 5.5), 0, 2 * math.pi)
            setc(ctx, random.choice([hx("#E7B9C6"), hx("#DDA3B5"), hx("#F0CFD8")]), 0.85); ctx.fill()
    else:
        # dal izleri
        setc(ctx, hx("#7E927C"), 0.35); ctx.set_line_width(1.0)
        for i in range(7):
            a = 2 * math.pi * i / 7 + random.uniform(-0.2, 0.2)
            ctx.move_to(cx, cy); ctx.line_to(cx + math.cos(a) * r * 0.55, cy + math.sin(a) * r * 0.55); ctx.stroke()


# ---------------------------------------------------------------- mobilya listeleri (DXF blok konumları)
def furniture_giris(ctx, sh):
    items = []
    # mutfak tezgâhları (L: batı duvarı + kuzey dönüşü; güneyde pencere altı tezgâh)
    items.append(("counter", (20, 20, 560, 80, "n")))
    items.append(("counter", (20, 80, 80, 470, "e")))
    items.append(("counter", (20, 470, 222, 530, "s")))
    items.append(("fridge", (259.5, 497.5, 75, 65, 0)))           # EKLENDİ
    items.append(("sink", (53, 192, 98, 50, 90)))                   # IFC_EVYE_1.5
    items.append(("hob", (51, 311, 50, 56, 90)))                    # IFC_OCAK
    items.append(("island", (225, 215, 465, 315)))
    for x in (270, 345, 420):
        items.append(("stool", (x, 337, 0)))
    # WC
    items.append(("toilet", (185, 842, 0)))
    items.append(("vanity", (263.5, 795, 60, 53, 270, 1)))
    # giriş holü vestiyer
    items.append(("wardrobe", (460, 775, 210, 60, 90)))
    items.append(("plant", (648, 962, 17)))
    # salon - oturma
    items.append(("rug", (878, 562, 1176, 836)))
    items.append(("sofa", (1049, 494, 246, 94, 180)))
    items.append(("sofa", (1234.5, 696, 246, 93, 270)))
    items.append(("armchair", (802.5, 633.5, 87, 77, 90)))
    items.append(("armchair", (802.5, 803.5, 87, 77, 90)))
    items.append(("rtable", (829.5, 718.5, 25.5)))
    items.append(("rtable", (1049.3, 701.3, 67.5)))
    items.append(("stable", (1203, 515, 60)))
    items.append(("lamp", ((1101, 742), (1225, 878))))
    items.append(("lowunit", (1010, 967.5, 240, 45, 0, 110)))       # TV ünitesi + TV
    items.append(("plant", (712, 960, 22)))
    items.append(("plant", (1306, 52, 24)))
    # salon - yemek
    chairs = [(x, 140, 180) for x in (981.5, 1041.5, 1101.5, 1161.5)] + \
             [(x, 254, 0) for x in (981.5, 1041.5, 1101.5, 1161.5)]
    items.append(("dining", (947, 147, 1197, 247, chairs)))
    items.append(("lowunit", (816, 214, 200, 50, 90, 0)))           # büfe *U101
    lifts = [(308, 725, 412, 862)]
    draw_items(ctx, sh, items)
    return lifts


def furniture_kat1(ctx, sh):
    items = []
    # YATAK ODASI 1
    items.append(("rug", (92, 1868, 262, 2102)))
    items.append(("bed", (120, 1985, 160, 200, 90)))
    items.append(("night", (50, 1880, 50, 40, 0)))
    items.append(("night", (50, 2090, 50, 40, 0)))
    items.append(("wardrobe", (50, 2294, 342, 60, 90)))
    # YATAK ODASI 2
    items.append(("rug", (383, 1868, 553, 2102)))
    items.append(("bed", (545, 1985, 160, 200, 270)))
    items.append(("night", (620, 1880, 50, 40, 0)))
    items.append(("night", (620, 2090, 50, 40, 0)))
    items.append(("wardrobe", (330, 2097.5, 535, 60, 90)))
    # YATAK ODASI 3
    items.append(("rug", (727, 1868, 897, 2102)))
    items.append(("bed", (755, 1985, 160, 200, 90)))
    items.append(("night", (685, 1880, 50, 40, 0)))
    items.append(("night", (685, 2090, 50, 40, 0)))
    items.append(("wardrobe", (975, 2097.5, 535, 60, 270)))
    # EBEVEYN YATAK ODASI
    items.append(("rug", (1087, 2022, 1267, 2258)))
    items.append(("rugr", (1112, 1850, 1262, 2000)))
    items.append(("bed", (1115, 2140, 160, 200, 90)))
    items.append(("night", (1045, 1995, 50, 40, 0)))
    items.append(("night", (1045, 2285, 50, 40, 0)))
    items.append(("armchair", (1102.5, 1931, 87, 76, 0)))
    items.append(("armchair", (1273, 1931, 87, 76, 0)))
    items.append(("rtable", (1187.5, 1904.5, 25.5)))
    # GİYİNME ODASI
    items.append(("wardrobe", (997.5, 2770, 165, 60, 0)))
    items.append(("wardrobe", (1310, 2617.5, 245, 60, 270)))
    items.append(("wardrobe", (997.5, 2525, 165, 60, 180)))
    # EBEVEYN BANYOSU + WC
    items.append(("jacuzzi", (680, 2745, 160, 110, 0)))
    items.append(("shower", (855, 2750, 100, 100, 0, "ws")))
    items.append(("vanity", (795, 2520, 160, 50, 180, 2)))
    items.append(("toilet", (640, 2521, 180)))
    # BANYO 1
    items.append(("shower", (245, 2635, 90, 90, 0, "ws")))
    items.append(("toilet", (167, 2640, 90)))
    items.append(("vanity", (166.5, 2585, 60, 53, 90, 1)))
    # BANYO 2
    items.append(("shower", (600, 2320, 90, 90, 0, "ws")))
    items.append(("toilet", (522, 2339, 0)))
    items.append(("vanity", (618.5, 2235, 60, 53, 270, 1)))
    # BANYO 3
    items.append(("shower", (700, 2320, 90, 90, 0, "es")))
    items.append(("toilet", (778, 2339, 0)))
    items.append(("vanity", (681.5, 2235, 60, 53, 90, 1)))
    # hol
    items.append(("plant", (562, 2780, 15)))
    lifts = [(308, 2535, 412, 2672)]
    draw_items(ctx, sh, items)
    return lifts


def shadow_shape(sh, kind, a):
    o = 5.0
    sh.save(); sh.translate(o, -o)
    sh.set_source_rgba(0, 0, 0, 1)
    if kind in ("counter",):
        x0, y0, x1, y1 = a[:4]; sh.rectangle(x0, y0, x1 - x0, y1 - y0); sh.fill()
    elif kind == "island":
        x0, y0, x1, y1 = a; sh.rectangle(x0, y0, x1 - x0, y1 - y0); sh.fill()
    elif kind == "dining":
        x0, y0, x1, y1, ch = a; sh.rectangle(x0, y0, x1 - x0, y1 - y0); sh.fill()
        for (cx, cy, th) in ch:
            sh.rectangle(cx - 21, cy - 25, 42, 50); sh.fill()
    elif kind in ("rtable",):
        sh.arc(a[0], a[1], a[2], 0, 2 * math.pi); sh.fill()
    elif kind == "stool":
        sh.arc(a[0], a[1], 18, 0, 2 * math.pi); sh.fill()
    elif kind == "plant":
        sh.arc(a[0], a[1], a[2], 0, 2 * math.pi); sh.fill()
    elif kind == "stable":
        sh.rectangle(a[0] - a[2] / 2, a[1] - a[2] / 2, a[2], a[2]); sh.fill()
    elif kind == "lamp":
        sh.arc(a[0][0], a[0][1], 34, 0, 2 * math.pi); sh.fill()
    elif kind in ("rug", "rugr"):
        pass
    elif kind == "toilet":
        with place(sh, a[0], a[1], a[2]):
            rrect(sh, -18, -28, 36, 55, 12); sh.fill()
    else:
        cx, cy, w, d, th = a[:5]
        with place(sh, cx, cy, th):
            rrect(sh, -w / 2, -d / 2, w, d, 6); sh.fill()
    sh.restore()


def draw_items(ctx, sh, items):
    for kind, a in items:
        if kind in ("rug", "rugr"):
            rug(RUGCTX[0], *a, round_=(kind == "rugr"))
            continue
        shadow_shape(sh, kind, a)
        if kind == "counter":
            counter(ctx, *a)
        elif kind == "island":
            island(ctx, *a)
        elif kind == "dining":
            dining(ctx, *a)
        elif kind == "rug":
            rug(ctx, *a)
        elif kind == "rugr":
            rug(ctx, *a, round_=True)
        elif kind == "rtable":
            with place(ctx, a[0], a[1], 0):
                round_table(ctx, a[2])
        elif kind == "stable":
            with place(ctx, a[0], a[1], 0):
                square_table(ctx, a[2])
        elif kind == "stool":
            with place(ctx, a[0], a[1], a[2]):
                stool(ctx)
        elif kind == "plant":
            plant(ctx, *a)
        elif kind == "lamp":
            arc_lamp(ctx, *a)
        elif kind == "toilet":
            with place(ctx, a[0], a[1], a[2]):
                toilet(ctx)
        else:
            cx, cy, w, d, th = a[:5]
            with place(ctx, cx, cy, th):
                if kind == "sofa":
                    sofa(ctx, w, d)
                elif kind == "armchair":
                    armchair(ctx, w, d)
                elif kind == "bed":
                    # bed yerel: başlık +y. place theta=bakış yönü (ayak ucu)
                    bed(ctx, w, d)
                elif kind == "night":
                    nightstand(ctx, w, d)
                elif kind == "wardrobe":
                    wardrobe(ctx, w, d)
                elif kind == "lowunit":
                    low_unit(ctx, w, d, tv=a[5])
                elif kind == "fridge":
                    fridge(ctx, w, d)
                elif kind == "sink":
                    sink_double(ctx, w, d)
                elif kind == "hob":
                    hob(ctx, w, d)
                elif kind == "vanity":
                    vanity(ctx, w, d, n=a[5])
                elif kind == "shower":
                    shower(ctx, w, d, a[5])
                elif kind == "jacuzzi":
                    jacuzzi(ctx, w, d)


# ---------------------------------------------------------------- mahal yazıları (konum: DXF'te boş zemin)
LABELS = {
    "giris": {
        "SALON": (1050, 372), "MUTFAK": (567, 262), "GİRİŞ HOLÜ": (582, 770), "WC": (190, 777),
        "ASANSÖR": (360, 793), "MERDİVEN": (278, 935),
    },
    "kat1": {
        "HOL": (680, 2430), "YATAK ODASI 1": (185, 2245), "YATAK ODASI 2": (430, 2200),
        "YATAK ODASI 3": (880, 2200), "BANYO 1": (245, 2571), "BANYO 2": (545, 2262),
        "BANYO 3": (755, 2262), "EBEVEYN YATAK ODASI": (1178, 2398), "GİYİNME ODASI": (1098, 2650),
        "EBEVEYN BANYOSU": (768, 2620), "WC": (640, 2598), "ASANSÖR": (360, 2603), "MERDİVEN": (278, 2745),
    },
}
DISPLAY = {"EBEVEYN BANYOSU": ["EBEVEYN", "BANYOSU"], "YATAK ODASI 2": ["YATAK", "ODASI 2"],
           "YATAK ODASI 3": ["YATAK", "ODASI 3"]}


def room_color(n):
    if n in ("WC",) or n.startswith("BANYO") or "BANYO" in n:
        return C["wet"]
    if n == "MUTFAK":
        return C["kitchen"]
    if n in ("HOL", "GİRİŞ HOLÜ"):
        return C["hall"]
    if n == "MERDİVEN":
        return C["stair"]
    if n == "ASANSÖR":
        return C["lift"]
    return C["dry"]


# ---------------------------------------------------------------- plan çizimi
RUGCTX = [None]
EXT = {"giris": (-320, -320, 1680, 1320), "kat1": (-40, 1770, 1400, 2860)}


def render_plan(fl):
    d = collect(fl)
    X0, Y0, X1, Y1 = EXT[fl]
    W, H = int(round((X1 - X0) * S)), int(round((Y1 - Y0) * S))
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    ctx = cairo.Context(surf)
    ctx.translate(-X0 * S, Y1 * S)
    ctx.scale(S, -S)
    mat = ctx.get_matrix()
    ctx.set_line_join(cairo.LINE_JOIN_ROUND); ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    dy = FLOORS[fl]["dy"]
    bx0, by0, bx1, by1 = 0, dy, 1360, dy + 1010

    # 1) peyzaj (yalnız giriş kat)
    if fl == "giris":
        B = 250
        gx0, gy0, gx1, gy1 = bx0 - B, by0 - B, bx1 + B, by1 + B
        gl = Layer(W, H, mat)
        g = gl.c
        g.rectangle(gx0, gy0, gx1 - gx0, gy1 - gy0); setc(g, C["grass"]); g.fill()
        for _ in range(260):
            x, y = random.uniform(gx0, gx1), random.uniform(gy0, gy1)
            g.arc(x, y, random.uniform(25, 80), 0, 2 * math.pi)
            setc(g, random.choice([C["grass2"], C["grass3"]]), random.uniform(0.15, 0.35)); g.fill()
        gs = blur(gl.s, 9)
        ctx.save(); ctx.rectangle(gx0, gy0, gx1 - gx0, gy1 - gy0); ctx.clip()
        ctx.save(); ctx.identity_matrix(); ctx.set_source_surface(gs, 0, 0); ctx.paint(); ctx.restore()
        ctx.restore()
        ctx.rectangle(gx0, gy0, gx1 - gx0, gy1 - gy0); setc(ctx, hx("#A7ACA4")); ctx.set_line_width(1.0); ctx.stroke()
        # giriş sert zemin: sahanlık + basamak taşları
        ctx.rectangle(470, by1, 210, 95)
        ctx.set_source(lgrad(470, by1 + 95, 680, by1, hx("#DAD9D4"), hx("#CFCEC9")))
        ctx.fill_preserve(); setc(ctx, C["paveb"]); ctx.set_line_width(0.6); ctx.stroke()
        setc(ctx, C["paveb"]); ctx.set_line_width(0.35)
        for k in range(1, 4):
            ctx.move_to(470 + k * 52.5, by1); ctx.line_to(470 + k * 52.5, by1 + 95); ctx.stroke()
        for yy in (by1 + 115, by1 + 180):
            rrect(ctx, 500, yy, 150, 48, 2)
            ctx.set_source(lgrad(500, yy + 48, 650, yy, hx("#DCDBD6"), hx("#CFCEC9")))
            ctx.fill_preserve(); setc(ctx, C["paveb"]); ctx.set_line_width(0.6); ctx.stroke()
        # yapı gölgesi
        bl = Layer(W, H, mat)
        bl.c.rectangle(bx0 + 30, by0 - 30, 1360, 1010); bl.c.set_source_rgba(0, 0, 0, 1); bl.c.fill()
        bs = blur(bl.s, 22)
        ctx.save(); ctx.identity_matrix(); ctx.set_source_rgba(*hx("#3A3F38", 0.30))
        ctx.mask_surface(bs, 0, 0); ctx.restore()
        # (mask opaklık için ikinci geçiş yerine düşük alfa renk)
    # 2) zemin dolguları
    ctx.rectangle(0, dy, 1360, 1010); setc(ctx, C["dry"]); ctx.fill()
    for r in d["rooms"]:
        c = room_color(r["name"])
        xs = [p[0] for p in r["poly"]]; ys = [p[1] for p in r["poly"]]
        poly_path(ctx, r["poly"])
        ctx.set_source(lgrad(min(xs), max(ys), max(xs), min(ys), shade(c, 1.022), shade(c, 0.975)))
        ctx.fill()
    # kapı boşlukları (duvar içi eşik) - açık gri
    # 3) duvar gölgesi zemine
    wl = Layer(W, H, mat)
    for pts in d["walls"] + d["cols"]:
        wl.c.save(); wl.c.translate(6, -6); poly_path(wl.c, pts); wl.c.restore()
        wl.c.set_source_rgba(0, 0, 0, 1); wl.c.fill()
    ws = blur(wl.s, 7)
    ctx.save(); ctx.rectangle(20, dy + 20, 1320, 970); ctx.clip()
    ctx.identity_matrix(); ctx.set_source_rgba(0.15, 0.15, 0.14, 0.20); ctx.mask_surface(ws, 0, 0)
    ctx.restore()
    # 4) mobilya (+ gölge katmanı)
    fl_layer = Layer(W, H, mat)       # mobilya ayrı katmanda çizilir, gölgeden sonra bindirilir
    sh = Layer(W, H, mat)
    RUGCTX[0] = ctx
    lifts = (furniture_giris if fl == "giris" else furniture_kat1)(fl_layer.c, sh.c)
    shs = blur(sh.s, 9)
    ctx.save(); ctx.identity_matrix(); ctx.set_source_rgba(0.18, 0.17, 0.15, 0.26); ctx.mask_surface(shs, 0, 0); ctx.restore()
    ctx.save(); ctx.identity_matrix(); ctx.set_source_surface(fl_layer.s, 0, 0); ctx.paint(); ctx.restore()
    for lb in lifts:
        lift(ctx, *lb)
    # 5) merdiven çizgileri
    setc(ctx, hx("#8E8E8C")); ctx.set_line_width(0.6)
    for pl in d["stairs"]:
        ctx.move_to(*pl[0])
        for p in pl[1:]:
            ctx.line_to(*p)
        ctx.stroke()
    # 6) kapılar
    for (t, pl) in d["doors"]:
        if t == "ARC":
            ctx.move_to(*pl[0])
            for p in pl[1:]:
                ctx.line_to(*p)
            setc(ctx, hx("#9A9A98")); ctx.set_line_width(0.5); ctx.stroke()
        else:
            xs = [p[0] for p in pl]; ys = [p[1] for p in pl]
            w_, h_ = max(xs) - min(xs), max(ys) - min(ys)
            if min(w_, h_) < 0.6 and max(w_, h_) > 30:    # kanat çizgisi (tek çizgi)
                ctx.move_to(*pl[0])
                for p in pl[1:]:
                    ctx.line_to(*p)
                setc(ctx, C["line"]); ctx.set_line_width(0.9); ctx.stroke()
                continue
            poly_path(ctx, pl)
            if max(w_, h_) > 30:      # kapı kanadı
                fill_stroke(ctx, C["white"], C["line"], 0.6)
            else:                     # kasa
                fill_stroke(ctx, hx("#6E6E6C"), None)
    for pts in d["doorrects"]:
        poly_path(ctx, pts); fill_stroke(ctx, C["white"], C["line"], 0.6)
    # 7) duvar, kolon, pencere
    for pts in d["walls"]:
        poly_path(ctx, pts); setc(ctx, C["wall"]); ctx.fill()
    for pts in d["cols"]:
        poly_path(ctx, pts); setc(ctx, C["col"]); ctx.fill()
    for (x0, y0, x1, y1) in d["windows"]:
        ctx.rectangle(x0, y0, x1 - x0, y1 - y0); setc(ctx, C["white"]); ctx.fill()
        setc(ctx, hx("#4A4A4A")); ctx.set_line_width(0.7)
        if x1 - x0 > y1 - y0:
            for yy in (y0 + 0.4, y1 - 0.4):
                ctx.move_to(x0, yy); ctx.line_to(x1, yy); ctx.stroke()
            ctx.set_line_width(0.5); setc(ctx, C["glass"])
            for yy in ((y0 + y1) / 2 - 2, (y0 + y1) / 2 + 2):
                ctx.move_to(x0 + 1, yy); ctx.line_to(x1 - 1, yy); ctx.stroke()
            setc(ctx, hx("#4A4A4A")); ctx.set_line_width(0.7)
            for xx in (x0 + 0.4, x1 - 0.4):
                ctx.move_to(xx, y0); ctx.line_to(xx, y1); ctx.stroke()
        else:
            for xx in (x0 + 0.4, x1 - 0.4):
                ctx.move_to(xx, y0); ctx.line_to(xx, y1); ctx.stroke()
            ctx.set_line_width(0.5); setc(ctx, C["glass"])
            for xx in ((x0 + x1) / 2 - 2, (x0 + x1) / 2 + 2):
                ctx.move_to(xx, y0 + 1); ctx.line_to(xx, y1 - 1); ctx.stroke()
            setc(ctx, hx("#4A4A4A")); ctx.set_line_width(0.7)
            for yy in (y0 + 0.4, y1 - 0.4):
                ctx.move_to(x0, yy); ctx.line_to(x1, yy); ctx.stroke()
    # 8) ağaçlar (giriş kat bahçesi)
    if fl == "giris":
        tl = Layer(W, H, mat); ts = Layer(W, H, mat)
        for (x, y, r, k) in ((-135, 1130, 110, "green"), (1490, 1135, 104, "green"), (1490, -125, 112, "green"),
                             (-140, -135, 108, "green"), (-165, 420, 92, "green"), (1515, 525, 82, "green"),
                             (405, 1105, 44, "flower"), (752, 1110, 40, "flower"), (1180, -160, 48, "flower"),
                             (95, -175, 42, "flower"), (-170, 790, 46, "flower"), (1525, 975, 44, "flower")):
            tree(tl.c, ts.c, x, y, r, k)
        tss = blur(ts.s, 14)
        ctx.save(); ctx.identity_matrix(); ctx.set_source_rgba(0.2, 0.25, 0.2, 0.22); ctx.mask_surface(tss, 0, 0); ctx.restore()
        tls = blur(tl.s, 1.6)
        ctx.save(); ctx.identity_matrix(); ctx.set_source_surface(tls, 0, 0); ctx.paint(); ctx.restore()
        # giriş üçgeni (kırmızı, dolu)
        ctx.move_to(575, by1 + 30); ctx.line_to(549, by1 + 72); ctx.line_to(601, by1 + 72); ctx.close_path()
        setc(ctx, C["red"]); ctx.fill()
    # 9) kot işareti
    kx, ky = (560, 615) if fl == "giris" else (330, 2415)
    ctx.move_to(kx - 10, ky); ctx.line_to(kx + 10, ky); ctx.line_to(kx, ky - 15); ctx.close_path()
    fill_stroke(ctx, C["white"], C["text2"], 0.6)
    ctx.move_to(kx, ky); ctx.line_to(kx + 62, ky); setc(ctx, C["text2"]); ctx.set_line_width(0.6); ctx.stroke()
    wtext(ctx, kx + 14, ky + 11, FLOORS[fl]["kot"], 18, color=C["text2"], anchor="l")
    # 10) mahal yazıları
    NAME, AREA = 26, 20
    for r in d["rooms"]:
        n = r["name"]
        x, y = LABELS[fl][n]
        a = area_dec(r["area"])
        lines = DISPLAY.get(n, [n])
        small = n in ("ASANSÖR", "MERDİVEN", "WC") or n.startswith("BANYO")
        ns, as_ = (NAME * 0.82, AREA * 0.9) if small else (NAME, AREA)
        if n == "ASANSÖR":
            ns, as_ = 16, 15
        lh = ns * 1.08
        tot = lh * len(lines) + as_ * 1.15
        yy = y + tot / 2 - lh / 2
        if n == "MERDİVEN":   # merdiven çizgileri üstünde zemin rengi hale
            ctx.select_font_face(FONT, 0, 1); ctx.set_font_size(ns)
            tw = text_width(ctx, n) + 16
            rrect(ctx, x - tw / 2, y - tot / 2 - 4, tw, tot + 8, 4); setc(ctx, C["stair"], 0.92); ctx.fill()
        for ln in lines:
            wtext(ctx, x, yy, ln, ns, bold=True, color=C["text"])
            yy -= lh
        wtext(ctx, x, yy - (as_ * 0.15), "%.2f m²" % a, as_, color=C["text2"])
    return surf, d, (X0, Y0, X1, Y1)


# ---------------------------------------------------------------- pafta düzeni (kağıt mm)
def mm(v):
    return v * PXMM


def ptx(pt):
    return pt / 72.0 * DPI


def stext(ctx, x_mm, y_mm, s, pt, bold=False, color=None, anchor="l", track_mm=0.0, light=False):
    ctx.save()
    ctx.select_font_face(FONT, 0, cairo.FONT_WEIGHT_BOLD if bold else cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(ptx(pt))
    tr = mm(track_mm)
    w = text_width(ctx, s, tr)
    x = mm(x_mm) - {"l": 0, "c": w / 2, "r": w}[anchor]
    setc(ctx, color or C["text"])
    for ch in s:
        ctx.move_to(x, mm(y_mm)); ctx.show_text(ch)
        x += ctx.text_extents(ch)[4] + tr
    ctx.restore()
    return w / PXMM


def hline(ctx, x0, x1, y, lw=0.25, col=None):
    setc(ctx, col or hx("#4A4A4A")); ctx.set_line_width(mm(lw))
    ctx.move_to(mm(x0), mm(y)); ctx.line_to(mm(x1), mm(y)); ctx.stroke()


def north_arrow(ctx, x, y, r=7):
    cx, cy, R = mm(x), mm(y), mm(r)
    ctx.new_path()
    ctx.arc(cx, cy, R, 0, 2 * math.pi); setc(ctx, hx("#4A4A4A")); ctx.set_line_width(mm(0.2)); ctx.stroke()
    ctx.move_to(cx, cy - R * 1.05); ctx.line_to(cx - R * 0.42, cy + R * 0.62); ctx.line_to(cx, cy + R * 0.32); ctx.close_path()
    setc(ctx, hx("#FFFFFF")); ctx.fill_preserve(); setc(ctx, hx("#2F2F2F")); ctx.set_line_width(mm(0.18)); ctx.stroke()
    ctx.move_to(cx, cy - R * 1.05); ctx.line_to(cx + R * 0.42, cy + R * 0.62); ctx.line_to(cx, cy + R * 0.32); ctx.close_path()
    setc(ctx, hx("#2F2F2F")); ctx.fill()
    stext(ctx, x, y - r - 2.2, "K", 9, bold=True, anchor="c")


def scale_bar(ctx, x, y):
    """1/100: 1 m = 10 mm. 0-1-2-3-4-5 m."""
    h = 1.6
    ctx.new_path()
    for i in range(5):
        ctx.rectangle(mm(x + i * 10), mm(y), mm(10), mm(h))
        setc(ctx, hx("#2F2F2F") if i % 2 == 0 else hx("#FFFFFF")); ctx.fill_preserve()
        setc(ctx, hx("#2F2F2F")); ctx.set_line_width(mm(0.15)); ctx.stroke()
    for i in range(6):
        stext(ctx, x + i * 10, y + h + 3.4, str(i), 6.5, anchor="c", color=C["text2"])
    stext(ctx, x + 52, y + h + 3.4, "m", 6.5, anchor="l", color=C["text2"])
    stext(ctx, x, y - 1.6, "ÖLÇEK 1/100", 6.5, bold=True, anchor="l", color=C["text2"])


def logo(ctx, x, y_bottom, w):
    lg = cairo.ImageSurface.create_from_png(LOGO)
    sc = mm(w) / lg.get_width()
    h = lg.get_height() * sc
    ctx.save(); ctx.translate(mm(x), mm(y_bottom) - h); ctx.scale(sc, sc)
    ctx.set_source_surface(lg, 0, 0); ctx.get_source().set_filter(cairo.FILTER_BEST); ctx.paint(); ctx.restore()
    return h / PXMM


def info_block(ctx, x_right, y, cizim, olcek):
    items = [("PROJE", "DNM01 DENEME VİLLA"), ("ÇİZİM", cizim), ("ÖLÇEK", olcek),
             ("TARİH", "11.11.2026"), ("SÜRÜM", "v01"), ("AŞAMA", "KONSEPT")]
    # sağdan sola yerleştir
    ctx.select_font_face(FONT, 0, 1); ctx.set_font_size(ptx(7.5))
    widths = [max(text_width(ctx, v), 1) / PXMM for _, v in items]
    gap = 6
    x = x_right - sum(widths) - gap * (len(items) - 1)
    x0 = x
    for (k, v), w in zip(items, widths):
        stext(ctx, x, y - 4.2, k, 5.5, color=hx("#8A8A8A"), track_mm=0.25)
        stext(ctx, x, y, v, 7.5, bold=True, color=C["text"])
        x += w + gap
    return x0


def plan_caption(ctx, x_right, y, title, net, brut):
    stext(ctx, x_right, y, title, 10, bold=True, anchor="r")
    stext(ctx, x_right, y + 4.6, "NET ALAN TOPLAMI : %s m²" % net, 7.5, anchor="r", color=C["text2"])
    stext(ctx, x_right, y + 8.6, "BRÜT ALAN : %s m²" % brut, 7.5, bold=True, anchor="r")


def paste_plan(ctx, surf, x_mm, y_mm):
    ctx.save(); ctx.set_source_surface(surf, mm(x_mm), mm(y_mm)); ctx.paint(); ctx.restore()


def net_total(d):
    return sum(area_dec(r["area"]) for r in d["rooms"])


def new_sheet(w_mm, h_mm):
    W, H = int(round(mm(w_mm))), int(round(mm(h_mm)))
    s = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H)
    c = cairo.Context(s); c.set_source_rgb(1, 1, 1); c.paint()
    fo = cairo.FontOptions(); fo.set_antialias(cairo.ANTIALIAS_GRAY); fo.set_hint_style(cairo.HINT_STYLE_NONE)
    c.set_font_options(fo)
    return s, c


def header(ctx, w_mm, sub):
    stext(ctx, 15, 17, "DNM01", 13, bold=True)
    stext(ctx, 15, 23.5, "DENEME VİLLA", 11, bold=False, track_mm=1.6, color=C["text2"])
    stext(ctx, w_mm - 15, 17, "MİMARİ KONSEPT PROJE", 12, track_mm=2.2, anchor="r")
    stext(ctx, w_mm - 15, 23.5, sub, 10, bold=True, anchor="r")


def footer(ctx, w_mm, h_mm, cizim, olcek):
    yb = h_mm - 12
    lw = 58
    logo(ctx, 15, yb, lw)
    x0 = info_block(ctx, w_mm - 15, yb, cizim, olcek)
    hline(ctx, 15 + lw + 4, x0 - 6, yb - 0.6, 0.3)


def save_jpg(surf, path):
    arr = surf_to_np(surf)
    im = Image.fromarray(arr[:, :, [2, 1, 0]], "RGB")
    im.save(path, "JPEG", quality=92, dpi=(DPI, DPI), subsampling=0, optimize=True)
    pv = im.copy(); pv.thumbnail((2000, 2000))
    pdir = os.path.join(OUT, "onizleme"); os.makedirs(pdir, exist_ok=True)
    pv.save(os.path.join(pdir, os.path.basename(path).replace(".jpg", "_onizleme.png")))
    return im.size


def main():
    plans = {}
    for fl in ("giris", "kat1"):
        plans[fl] = render_plan(fl)
        print("plan", fl, plans[fl][0].get_width(), plans[fl][0].get_height())
    BRUT = "137.36"
    out = {}
    # --- tek kat paftaları: A4 yatay 297x210, 1/100
    for fl, fname, sub in (("giris", "DNM01_boyama_giris-kat_v01.jpg", "GİRİŞ KAT PLANI"),
                           ("kat1", "DNM01_boyama_1-kat_v01.jpg", "1. KAT PLANI")):
        surf, d, (X0, Y0, X1, Y1) = plans[fl]
        s, c = new_sheet(297, 210)
        header(c, 297, sub)
        pw, ph = (X1 - X0) / 10, (Y1 - Y0) / 10
        dy = FLOORS[fl]["dy"]
        if fl == "giris":
            px, py = 16, 27
        else:
            # bina merkezini giriş kat paftasıyla aynı yere getir
            px = 16 + (0 - EXT["giris"][0]) / 10 - (0 - X0) / 10
            py = 27 + (EXT["giris"][3] - 1010) / 10 - (Y1 - (dy + 1010)) / 10
        paste_plan(c, surf, px, py)
        # sağ sütun
        bx_right = px + (1360 - X0) / 10
        colx = 297 - 15
        bottom_bld = py + (Y1 - dy) / 10
        plan_caption(c, colx, bottom_bld - 12, FLOORS[fl]["name"], "%.2f" % net_total(d), BRUT)
        north_arrow(c, colx - 8, 52)
        scale_bar(c, colx - 52, bottom_bld - 26)
        footer(c, 297, 210, FLOORS[fl]["name"], "1/100 (A4)")
        save_jpg(s, os.path.join(OUT, fname))
        out[fname] = (s.get_width(), s.get_height())
        del s, c
    # --- iki kat bir arada: A3 yatay 420x297
    s, c = new_sheet(420, 297)
    header(c, 420, "KAT PLANLARI")
    gs, gd, ge = plans["giris"]; ks, kd, ke = plans["kat1"]
    bld_bottom = 192.0                       # bina güney yüzü (mm, sayfa üstünden)
    gx = 24
    gxb = gx + (0 - ge[0]) / 10              # giriş kat bina batı yüzü
    gy = bld_bottom - (ge[3] - 0) / 10 + 101.0
    gy = bld_bottom - (ge[3] - 1010) / 10 - 101.0
    paste_plan(c, gs, gx, gy)
    kxb = gxb + 136 + 25 + 25 + 22          # 1. kat bina batı yüzü
    kx = kxb - (0 - ke[0]) / 10
    ky = bld_bottom - (ke[3] - (1810 + 1010)) / 10 - 101.0
    paste_plan(c, ks, kx, ky)
    cap_y = bld_bottom + 25 + 9
    plan_caption(c, gxb + 136 + 25, cap_y, "GİRİŞ KAT PLANI", "%.2f" % net_total(gd), BRUT)
    plan_caption(c, kxb + 136, cap_y, "1. KAT PLANI", "%.2f" % net_total(kd), BRUT)
    north_arrow(c, kxb + 136 - 7, bld_bottom - 101 - 22)
    scale_bar(c, kxb, cap_y - 3)
    footer(c, 420, 297, "KAT PLANLARI", "1/100 (A3)")
    fname = "DNM01_boyama_kat-planlari_v01.jpg"
    save_jpg(s, os.path.join(OUT, fname))
    out[fname] = (s.get_width(), s.get_height())
    for k, v in out.items():
        print(k, v)
    for fl in plans:
        d = plans[fl][1]
        print(fl, [(r["name"], r["area"], str(area_dec(r["area"]))) for r in d["rooms"]], net_total(d))


if __name__ == "__main__":
    main()
