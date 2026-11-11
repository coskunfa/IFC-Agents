# -*- coding: utf-8 -*-
"""ERA01 - DXF'teki tüm INSERT'leri özyinelemeli açıp düz geometri listesine çevirir (DETAY metraj kopyası; kaynak 03-boyama/kaynak/era01_dxf_duzlestir.py).
Çıktı: kaynak/era01_geo.pkl  (her öğe: dict(t, lay, pts|txt, blk))
t: 'L' çoklu çizgi (açık), 'P' kapalı poligon, 'H' tarama sınırları, 'T' yazı
blk: en dış (model alanı) INSERT adı > ... > iç blok adı zinciri
"""
import os, pickle, sys, math
import ezdxf
from ezdxf import path as ezpath
HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
DXF = os.path.join(PROJ, "00-girdi", "ERA01_girdi_proje.dxf")
OUT = os.path.join(HERE, "era01_metraj_geo.pkl")
sys.setrecursionlimit(10000)
doc = ezdxf.readfile(DXF)
msp = doc.modelspace()
res = []

def lay_of(e, parent_lay):
    l = e.dxf.layer
    return parent_lay if (l == "0" and parent_lay) else l

def add_path(e, lay, chain):
    t = e.dxftype()
    try:
        if t == "HATCH":
            p = ezpath.make_path(e)
            loops = [[(v.x, v.y) for v in sp.flattening(1.0)] for sp in p.sub_paths()]
            loops = [l for l in loops if len(l) > 2]
            if loops:
                pat = e.dxf.pattern_name if e.dxf.hasattr("pattern_name") else ""
                res.append(dict(t="H", lay=lay, loops=loops, blk=chain, pat=pat, solid=bool(e.dxf.solid_fill)))
            return
        p = ezpath.make_path(e)
        closed = False
        if t == "LWPOLYLINE": closed = e.closed
        elif t == "POLYLINE": closed = e.is_closed
        elif t in ("CIRCLE", "ELLIPSE"): closed = True
        for sp in p.sub_paths():
            pts = [(v.x, v.y) for v in sp.flattening(0.8)]
            if len(pts) > 1:
                res.append(dict(t="P" if closed else "L", lay=lay, pts=pts, blk=chain, ty=t))
    except Exception as ex:
        pass

def walk(entities, parent_lay, chain, depth=0):
    for e in entities:
        t = e.dxftype()
        try:
            lay = lay_of(e, parent_lay)
        except Exception:
            continue
        if t == "INSERT":
            name = e.dxf.name
            try:
                walk(e.virtual_entities(), lay, chain + (name,), depth + 1)
            except Exception as ex:
                pass
            # öznitelikler
            for a in getattr(e, "attribs", []):
                try:
                    res.append(dict(t="T", lay=lay, txt=a.dxf.text, x=a.dxf.insert.x, y=a.dxf.insert.y, h=a.dxf.height, blk=chain + (name,)))
                except Exception:
                    pass
        elif t in ("LINE", "LWPOLYLINE", "POLYLINE", "ARC", "CIRCLE", "ELLIPSE", "SPLINE", "HATCH"):
            add_path(e, lay, chain)
        elif t == "TEXT" or t == "ATTRIB":
            try:
                res.append(dict(t="T", lay=lay, txt=e.dxf.text, x=e.dxf.insert.x, y=e.dxf.insert.y, h=e.dxf.height, blk=chain, rot=e.dxf.get("rotation", 0)))
            except Exception:
                pass
        elif t == "MTEXT":
            try:
                res.append(dict(t="T", lay=lay, txt=e.plain_text(), x=e.dxf.insert.x, y=e.dxf.insert.y, h=e.dxf.char_height, blk=chain, rot=e.dxf.get("rotation", 0)))
            except Exception:
                pass
        elif t in ("DIMENSION", "MULTILEADER", "LEADER", "SOLID", "3DFACE", "POINT", "ATTDEF", "WIPEOUT", "MLINE", "ACAD_TABLE", "IMAGE", "OLE2FRAME", "VIEWPORT", "REGION"):
            if t in ("SOLID",):
                try:
                    v = [e.dxf.vtx0, e.dxf.vtx1, e.dxf.vtx3, e.dxf.vtx2]
                    res.append(dict(t="P", lay=lay, pts=[(p.x, p.y) for p in v], blk=chain, ty=t))
                except Exception:
                    pass
            # ölçü/lider vb. boyamada kullanılmaz
        else:
            pass

TOPS = []
from ezdxf import bbox as ezbbox
cache = ezbbox.Cache()
for i, e in enumerate(msp):
    start = len(res)
    walk([e], None, ())
    for r in res[start:]:
        r["top"] = i
    if e.dxftype() == "INSERT":
        b = ezbbox.extents([e], cache=cache)
        TOPS.append(dict(i=i, name=e.dxf.name, x=e.dxf.insert.x, y=e.dxf.insert.y, rot=e.dxf.rotation, sx=e.dxf.xscale,
                         bb=(b.extmin.x, b.extmin.y, b.extmax.x, b.extmax.y) if b.has_data else None))
print(len(res))
with open(OUT, "wb") as f:
    pickle.dump(dict(geo=res, tops=TOPS), f, protocol=4)
