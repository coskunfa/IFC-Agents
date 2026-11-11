"""DXF dosyasından PNG önizleme üretir.
Kullanım: python3 araclar/dxf_onizleme.py <girdi.dxf> [cikti.png]
"""
import sys
import ezdxf
from ezdxf.addons.drawing import matplotlib as ezmpl

def main():
    src = sys.argv[1]
    dst = sys.argv[2] if len(sys.argv) > 2 else src.rsplit(".", 1)[0] + ".png"
    doc = ezdxf.readfile(src)
    ezmpl.qsave(doc.modelspace(), dst, bg="#FFFFFF", dpi=200)
    print(dst)

if __name__ == "__main__":
    main()
