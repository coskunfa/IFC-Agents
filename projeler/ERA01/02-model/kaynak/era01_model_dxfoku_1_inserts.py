import ezdxf, sys, pickle, collections
from ezdxf import disassemble
from ezdxf.math import Matrix44
doc = ezdxf.readfile(sys.argv[1]); msp = doc.modelspace()
SKIPN=("BEYKOZ ANTET","HESAPLAR","ATIKSU DETAY","KANAL PROJESI","BAGIMSIZ BOLUM LSITESI","KOT HESABI","TOPRAK ALTI HESABI","ZEMIN ALTI HESABI","OK")
def walk(entities, M, ents, depth=0):
    for e in entities:
        t=e.dxftype(); lay=e.dxf.get('layer','0')
        if lay.startswith('6_IFC') or t in ("HATCH","SOLID","WIPEOUT","IMAGE","POINT","MULTILEADER"): continue
        try:
            if t=="INSERT":
                m = e.matrix44() @ M if False else e.matrix44() * M
                for a in e.attribs:
                    p=M.transform(a.dxf.insert)
                    ents.append(("T",a.dxf.layer,(p.x,p.y),a.dxf.text,a.dxf.get('height',0), a.dxf.tag))
                if depth<12:
                    walk(doc.blocks[e.dxf.name], m, ents, depth+1)
            elif t=="DIMENSION":
                continue
            elif t in ("TEXT","MTEXT","ATTDEF"):
                if t=="ATTDEF": continue
                s=e.plain_text() if t=="MTEXT" else e.dxf.text
                p=M.transform(e.dxf.insert)
                ents.append(("T",lay,(p.x,p.y),s,e.dxf.get('char_height',None) or e.dxf.get('height',0),""))
            elif t in ("LWPOLYLINE","POLYLINE","LINE","ARC","CIRCLE"):
                c=e.copy(); c.transform(M)
                pr=disassemble.make_primitive(c, max_flattening_distance=3)
                vs=[(v.x,v.y) for v in pr.vertices()]
                cl = (t=="LWPOLYLINE" and e.closed) or (t=="POLYLINE" and e.is_closed) or t=="CIRCLE"
                if 2<=len(vs)<3000: ents.append(("L",lay,vs,t,cl))
        except Exception as ex:
            pass
out=[]
for ins in msp.query("INSERT"):
    nm=ins.dxf.name
    if nm.startswith("*U") or nm in SKIPN or nm.startswith("0_IFC_NOT"): continue
    ents=[]
    walk([ins], Matrix44(), ents)
    out.append((nm, ents))
    print(nm, len(ents))
pickle.dump(out, open("plans.pkl","wb"))
