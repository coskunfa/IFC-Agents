# -*- coding: utf-8 -*-
"""ERA01 metraj (DETAY) - DXF'teki tüm INSERT'leri (iç içe) konum + etkin blok adı ile listeler.
Dinamik (anonim *U) blokların asıl adı AcDbBlockRepBTag xdata'sından çözülür.
Çıktı: era01_metraj_inserts.pkl  -> liste: dict(top, chain, name, eff, lay, x, y, rot, sx, sy)
"""
import os, sys, pickle
import ezdxf
HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
DXF = os.path.join(PROJ, "00-girdi", "ERA01_girdi_proje.dxf")
doc = ezdxf.readfile(DXF); msp = doc.modelspace()
_eff = {}
def eff_name(name):
    if name in _eff: return _eff[name]
    out = name
    try:
        br = doc.blocks.get(name).block_record
        xd = br.get_xdata("AcDbBlockRepBTag")
        h = [v for c, v in xd if c == 1005][0]
        out = doc.entitydb[h].dxf.name
    except Exception:
        pass
    _eff[name] = out
    return out
res = []
def walk(ins, chain, parent_lay, top, depth=0):
    lay = ins.dxf.layer
    if lay == "0" and parent_lay: lay = parent_lay
    nm = ins.dxf.name
    p = ins.dxf.insert
    res.append(dict(top=top, chain=chain, name=nm, eff=eff_name(nm), lay=lay, x=p.x, y=p.y,
                    rot=ins.dxf.get("rotation", 0), sx=ins.dxf.get("xscale", 1), sy=ins.dxf.get("yscale", 1)))
    if depth > 12: return
    try:
        for e in ins.virtual_entities():
            if e.dxftype() == "INSERT":
                walk(e, chain + (nm,), lay, top, depth + 1)
    except Exception:
        pass
for i, e in enumerate(msp):
    if e.dxftype() == "INSERT":
        walk(e, (), None, i)
pickle.dump(res, open(os.path.join(HERE, "era01_metraj_inserts.pkl"), "wb"), protocol=4)
print(len(res))
