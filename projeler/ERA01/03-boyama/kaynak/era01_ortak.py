# -*- coding: utf-8 -*-
"""ERA01 boyama ortak yardımcıları (PAFTA, v01): palet, cairo/numpy araçları, yazı, pafta düzeni."""
import math, os, random, pickle
from decimal import Decimal, ROUND_HALF_UP

import cairo
import numpy as np
from PIL import Image, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.abspath(os.path.join(HERE, "..", ".."))
ROOT = os.path.abspath(os.path.join(PROJ, "..", ".."))
OUT = os.path.join(PROJ, "03-boyama")
LOGO = os.path.join(ROOT, "ofis-standartlari", "logolar", "IFC_Architects_logo_koyu.png")
GEO = os.path.join(HERE, "era01_geo.pkl")

DPI = 600
PXMM = DPI / 25.4
FONT = "Carlito"  # Calibri metrik eşdeğeri (sistemde Calibri yok)
TARIH = "11.11.2026"
SURUM = "v01"
PROJE_ADI = "ERA01 ERA EVİ"


def hx(h, a=1.0):
    h = h.lstrip("#")
    return (int(h[0:2], 16) / 255, int(h[2:4], 16) / 255, int(h[4:6], 16) / 255, a)


C = dict(
    dry=hx("#DADAD8"), hall=hx("#E3E3E1"), kitchen=hx("#CFCFCC"), wet=hx("#C8CDD1"),
    stair=hx("#E7E7E5"), lift=hx("#BDBDBC"), tech=hx("#D0D0CE"), park=hx("#CDCDCB"),
    terrace=hx("#E6E2DA"), pool=hx("#CFE0E6"), poolb=hx("#B9CFD7"), sill=hx("#E8E8E6"),
    wall=hx("#383838"), col=hx("#050505"),
    line=hx("#8A8A88"), line2=hx("#A9A9A7"), fine=hx("#BDBDBB"),
    white=hx("#FFFFFF"), off=hx("#F6F5F3"),
    grass=hx("#DCE5DA"), grass2=hx("#CCD9CA"), earth=hx("#D3D2CE"), pave=hx("#D9D7D1"), paveb=hx("#BEBDB8"),
    text=hx("#2F2F2F"), text2=hx("#5A5A5A"), red=hx("#C8102E"), glass=hx("#8FA6B3"),
)


def area_dec(v):
    return Decimal(repr(v)).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)


def fmt_area(v):
    return "%.2f" % float(area_dec(v))


def load_geo():
    with open(GEO, "rb") as f:
        return pickle.load(f)


# ------------------------------------------------------------ cairo / numpy
def setc(ctx, c, a=None):
    if a is None:
        ctx.set_source_rgba(*c)
    else:
        ctx.set_source_rgba(c[0], c[1], c[2], a)


def shade(c, f):
    return (min(1, c[0] * f), min(1, c[1] * f), min(1, c[2] * f), c[3])


def path_pts(ctx, pts, close=True):
    ctx.move_to(*pts[0])
    for p in pts[1:]:
        ctx.line_to(*p)
    if close:
        ctx.close_path()


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


def mask_to_surf(mask, rgba):
    """bool maske -> premultiplied ARGB yüzey (tek renk)."""
    h, w = mask.shape
    r, g, b, a = rgba
    arr = np.zeros((h, w, 4), np.uint8)
    al = (mask.astype(np.float32) * a * 255).astype(np.uint8) if mask.dtype == bool else (mask * a).astype(np.uint8)
    arr[..., 3] = al
    arr[..., 2] = (al * r).astype(np.uint8)
    arr[..., 1] = (al * g).astype(np.uint8)
    arr[..., 0] = (al * b).astype(np.uint8)
    return np_to_surf(arr)


def alpha_surf(alpha_u8, rgb):
    """0-255 alfa dizisi -> tek renk ARGB yüzey."""
    h, w = alpha_u8.shape
    arr = np.zeros((h, w, 4), np.uint8)
    arr[..., 3] = alpha_u8
    arr[..., 2] = (alpha_u8 * rgb[0]).astype(np.uint8)
    arr[..., 1] = (alpha_u8 * rgb[1]).astype(np.uint8)
    arr[..., 0] = (alpha_u8 * rgb[2]).astype(np.uint8)
    return np_to_surf(arr)


def blur_alpha(mask, rad, dx=0, dy=0, strength=1.0):
    """Maskeyi kaydırıp bulanıklaştırır, 0-255 alfa döndürür."""
    im = Image.fromarray((mask.astype(np.uint8) * 255) if mask.dtype == bool else mask.astype(np.uint8))
    if dx or dy:
        im = im.transform(im.size, Image.AFFINE, (1, 0, -dx, 0, 1, -dy))
    im = im.filter(ImageFilter.GaussianBlur(rad))
    return (np.asarray(im).astype(np.float32) * strength).clip(0, 255).astype(np.uint8)


def ctx_mask(W, H, mat, draw, aa=False):
    """cairo ile A8 maske çizer, bool döndürür."""
    s = cairo.ImageSurface(cairo.FORMAT_A8, W, H)
    c = cairo.Context(s)
    if not aa:
        c.set_antialias(cairo.ANTIALIAS_NONE)
    c.set_matrix(mat)
    c.set_source_rgba(0, 0, 0, 1)
    draw(c)
    s.flush()
    st = s.get_stride()
    a = np.ndarray(shape=(H, st), dtype=np.uint8, buffer=s.get_data())[:, :W].copy()
    return a > 127


# ------------------------------------------------------------ yazı
def text_width(ctx, s, track=0.0):
    if track == 0:
        return ctx.text_extents(s)[4]
    return sum(ctx.text_extents(ch)[4] for ch in s) + track * (len(s) - 1)


def wtext(ctx, x, y, s, size, bold=False, color=None, anchor="c", track=0.0, halo=None):
    """Dünya (cm) koordinatında, okunur yönde yazı (eksen y yukarı). size: cm."""
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(1, -1)
    ctx.select_font_face(FONT, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD if bold else cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(size)
    w = text_width(ctx, s, track)
    cap = ctx.text_extents("H")[3]
    dx = {"c": -w / 2, "l": 0, "r": -w}[anchor]
    if halo:
        ctx.move_to(dx, cap / 2)
        ctx.text_path(s)
        setc(ctx, halo[0]); ctx.set_line_width(halo[1]); ctx.set_line_join(cairo.LINE_JOIN_ROUND); ctx.stroke()
    setc(ctx, color or C["text"])
    if track == 0:
        ctx.move_to(dx, cap / 2); ctx.show_text(s)
    else:
        xx = dx
        for ch in s:
            ctx.move_to(xx, cap / 2); ctx.show_text(ch)
            xx += ctx.text_extents(ch)[4] + track
    ctx.restore()
    return w


def wtext_width(ctx, s, size, bold=False):
    ctx.save()
    ctx.select_font_face(FONT, 0, cairo.FONT_WEIGHT_BOLD if bold else cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(size)
    w = ctx.text_extents(s)[4]
    ctx.restore()
    return w


# ------------------------------------------------------------ peyzaj öğeleri (dünya koordinatı)
def wc_blob(ctx, cx, cy, r, col, alpha, n=18, spread=1.0, rnd=random):
    for _ in range(n):
        a = rnd.uniform(0, 2 * math.pi)
        rr = rnd.uniform(0, r * 0.62) * spread
        br = rnd.uniform(r * 0.25, r * 0.5)
        ctx.arc(cx + math.cos(a) * rr, cy + math.sin(a) * rr, br, 0, 2 * math.pi)
        setc(ctx, col, alpha * rnd.uniform(0.6, 1.2)); ctx.fill()


def tree(ctx, sh, cx, cy, r, kind="green", rnd=random):
    if sh is not None:
        sh.arc(cx + r * 0.22, cy - r * 0.22, r * 0.95, 0, 2 * math.pi)
        sh.set_source_rgba(0, 0, 0, 1); sh.fill()
    cols = [hx("#9FB39A"), hx("#B6C6AF"), hx("#8AA088"), hx("#C9D5C1")]
    wc_blob(ctx, cx, cy, r, cols[2], 0.35, n=14, rnd=rnd)
    wc_blob(ctx, cx, cy, r, cols[0], 0.35, n=26, rnd=rnd)
    wc_blob(ctx, cx - r * 0.15, cy + r * 0.15, r * 0.8, cols[1], 0.35, n=20, rnd=rnd)
    wc_blob(ctx, cx - r * 0.25, cy + r * 0.25, r * 0.45, cols[3], 0.45, n=12, rnd=rnd)
    if kind == "flower":
        for _ in range(int(max(8, r * 1.3 if r < 100 else 60))):
            a = rnd.uniform(0, 2 * math.pi); rr = rnd.uniform(0, r * 0.85)
            ctx.arc(cx + math.cos(a) * rr, cy + math.sin(a) * rr, rnd.uniform(r * 0.06, r * 0.12), 0, 2 * math.pi)
            setc(ctx, rnd.choice([hx("#E7B9C6"), hx("#DDA3B5"), hx("#F0CFD8")]), 0.85); ctx.fill()
    else:
        setc(ctx, hx("#7E927C"), 0.35); ctx.set_line_width(max(1.0, r * 0.02))
        for i in range(7):
            a = 2 * math.pi * i / 7 + rnd.uniform(-0.2, 0.2)
            ctx.move_to(cx, cy); ctx.line_to(cx + math.cos(a) * r * 0.55, cy + math.sin(a) * r * 0.55); ctx.stroke()


# ------------------------------------------------------------ pafta düzeni (kağıt mm, y aşağı)
def mm(v):
    return v * PXMM


def ptx(pt):
    return pt / 72.0 * DPI


def stext(ctx, x_mm, y_mm, s, pt, bold=False, color=None, anchor="l", track_mm=0.0):
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


def north_arrow(ctx, x, y, r=7, angle_deg=0.0):
    """angle_deg: kuzeyin kağıt yukarısına göre saat yönünün tersine açısı."""
    cx, cy, R = mm(x), mm(y), mm(r)
    ctx.save()
    ctx.new_path()
    ctx.arc(cx, cy, R, 0, 2 * math.pi); setc(ctx, hx("#4A4A4A")); ctx.set_line_width(mm(0.2)); ctx.stroke()
    ctx.translate(cx, cy); ctx.rotate(-math.radians(angle_deg))
    ctx.move_to(0, -R * 1.05); ctx.line_to(-R * 0.42, R * 0.62); ctx.line_to(0, R * 0.32); ctx.close_path()
    setc(ctx, hx("#FFFFFF")); ctx.fill_preserve(); setc(ctx, hx("#2F2F2F")); ctx.set_line_width(mm(0.18)); ctx.stroke()
    ctx.move_to(0, -R * 1.05); ctx.line_to(R * 0.42, R * 0.62); ctx.line_to(0, R * 0.32); ctx.close_path()
    setc(ctx, hx("#2F2F2F")); ctx.fill()
    ctx.restore()
    a = math.radians(angle_deg)
    kx = x - math.sin(a) * (r + 3.2)
    ky = y - math.cos(a) * (r + 3.2) + 1.2
    stext(ctx, kx, ky, "K", 9, bold=True, anchor="c")


def scale_bar(ctx, x, y, olcek=100, metres=5, step=1):
    """Çizgi ölçek. olcek: 1/olcek. metres: toplam uzunluk (m), step: bölüm (m)."""
    h = 1.6
    seg = step * 1000.0 / olcek  # mm
    n = int(round(metres / step))
    ctx.new_path()
    for i in range(n):
        ctx.rectangle(mm(x + i * seg), mm(y), mm(seg), mm(h))
        setc(ctx, hx("#2F2F2F") if i % 2 == 0 else hx("#FFFFFF")); ctx.fill_preserve()
        setc(ctx, hx("#2F2F2F")); ctx.set_line_width(mm(0.15)); ctx.stroke()
    for i in range(n + 1):
        v = i * step
        stext(ctx, x + i * seg, y + h + 3.4, ("%g" % v), 6.5, anchor="c", color=C["text2"])
    stext(ctx, x + n * seg + 2, y + h + 3.4, "m", 6.5, anchor="l", color=C["text2"])
    stext(ctx, x, y - 1.6, "ÖLÇEK 1/%d" % olcek, 6.5, bold=True, anchor="l", color=C["text2"])
    return n * seg


def logo(ctx, x, y_bottom, w):
    lg = cairo.ImageSurface.create_from_png(LOGO)
    sc = mm(w) / lg.get_width()
    h = lg.get_height() * sc
    ctx.save(); ctx.translate(mm(x), mm(y_bottom) - h); ctx.scale(sc, sc)
    ctx.set_source_surface(lg, 0, 0); ctx.get_source().set_filter(cairo.FILTER_BEST); ctx.paint(); ctx.restore()
    return h / PXMM


def info_block(ctx, x_right, y, cizim, olcek):
    items = [("PROJE", PROJE_ADI), ("ÇİZİM", cizim), ("ÖLÇEK", olcek),
             ("TARİH", TARIH), ("SÜRÜM", SURUM), ("AŞAMA", "SUNUM")]
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


def new_sheet(w_mm, h_mm):
    W, H = int(round(mm(w_mm))), int(round(mm(h_mm)))
    s = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H)
    c = cairo.Context(s); c.set_source_rgb(1, 1, 1); c.paint()
    fo = cairo.FontOptions(); fo.set_antialias(cairo.ANTIALIAS_GRAY); fo.set_hint_style(cairo.HINT_STYLE_NONE)
    c.set_font_options(fo)
    return s, c


def header(ctx, w_mm, sub, sub2=None):
    stext(ctx, 15, 17, "ERA01", 13, bold=True)
    stext(ctx, 15, 23.5, "ERA EVİ", 11, track_mm=1.6, color=C["text2"])
    stext(ctx, w_mm - 15, 17, "MİMARİ SUNUM PROJESİ", 12, track_mm=2.2, anchor="r")
    stext(ctx, w_mm - 15, 23.5, sub, 10, bold=True, anchor="r")
    if sub2:
        stext(ctx, w_mm - 15, 28.5, sub2, 7.5, anchor="r", color=C["text2"])


def footer(ctx, w_mm, h_mm, cizim, olcek):
    yb = h_mm - 12
    lw = 58
    logo(ctx, 15, yb, lw)
    x0 = info_block(ctx, w_mm - 15, yb, cizim, olcek)
    hline(ctx, 15 + lw + 4, x0 - 6, yb - 0.6, 0.3)


def paste(ctx, surf, x_mm, y_mm, scale=1.0):
    ctx.save()
    ctx.translate(mm(x_mm), mm(y_mm))
    if scale != 1.0:
        ctx.scale(scale, scale)
    ctx.set_source_surface(surf, 0, 0)
    ctx.get_source().set_filter(cairo.FILTER_GOOD)
    ctx.paint(); ctx.restore()


def save_jpg(surf, path):
    arr = surf_to_np(surf)
    im = Image.fromarray(arr[:, :, [2, 1, 0]], "RGB")
    im.save(path, "JPEG", quality=92, dpi=(DPI, DPI), subsampling=0, optimize=True)
    pv = im.copy(); pv.thumbnail((2000, 2000), Image.LANCZOS)
    pdir = os.path.join(OUT, "onizleme"); os.makedirs(pdir, exist_ok=True)
    pv.save(os.path.join(pdir, os.path.basename(path).replace(".jpg", "_onizleme.png")))
    return im.size
