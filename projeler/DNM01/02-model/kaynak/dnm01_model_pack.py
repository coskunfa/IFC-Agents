import json, sys, io
from PIL import Image
s = json.load(open(sys.argv[1]))
def fm(x):
    t = f"{x:.2f}".rstrip("0").rstrip(".")
    return "0" if t in ("-0", "") else t
def mesh(v, f):
    vs = ";".join(",".join(fm(c) for c in p) for p in v)
    fs = ";".join("/".join(",".join(str(i) for i in l) for l in face) for face in f)
    return vs + "|" + fs
lines = []
for g in s["solids"]:
    lines.append("M|" + g["p"] + "|" + g["n"] + "|" + g["m"] + "|" + ("1" if g.get("open") else "0") + "|" + mesh(g["v"], g["f"]))
for dn, d in s["defs"].items():
    for i, so in enumerate(d["solids"]):
        lines.append("D|" + dn + "|" + str(i) + "|" + so["m"] + "|0|" + mesh(so["v"], so["f"]))
    for gl in d["glass"]:
        lines.append("G|" + dn + "|" + ";".join(",".join(fm(c) for c in p) for p in gl))
for ins in s["insts"]:
    lines.append("I|" + ins["p"] + "|" + ins["n"] + "|" + ins["d"] + "|" + ",".join(fm(c) for c in ins["o"]) + "|" + ",".join(fm(c) for c in ins["x"]) + "|" + ",".join(fm(c) for c in ins["y"]))
data = ("\n".join(lines)).encode("utf-8")
buf = io.BytesIO(); Image.new("RGB", (8, 8), (200, 200, 200)).save(buf, "PNG")
open(sys.argv[2], "wb").write(buf.getvalue() + b"\nDNM01DATA\n" + data + b"\nDNM01END\n")
print(len(lines), len(data))
