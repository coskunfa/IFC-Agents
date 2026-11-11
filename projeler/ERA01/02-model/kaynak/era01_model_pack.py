# spec JSON -> SketchUp build_model icin satir tabanli metin (cm, 1 ondalik)
import json, sys
s = json.load(open(sys.argv[1]))
def fm(x):
    t = f"{x:.1f}".rstrip("0").rstrip(".")
    return "0" if t in ("-0", "") else t
def mesh(v, f):
    return ";".join(",".join(fm(c) for c in p) for p in v) + "|" + ";".join("/".join(",".join(str(i) for i in l) for l in face) for face in f)
L = []
for b, t in s["blocks"].items():
    L.append(f"B|{b}|{fm(t['rot'])}|{fm(t['t'][0])}|{fm(t['t'][1])}")
for dn, d in s["defs"].items():
    for i, so in enumerate(d["solids"]):
        L.append(f"D|{dn}|{i}|{so['m']}|" + mesh(so["v"], so["f"]))
    for gl in d["glass"]:
        L.append(f"G|{dn}|" + ";".join(",".join(fm(c) for c in p) for p in gl))
for g in s["solids"]:
    L.append(f"S|{g['p']}|{g['n']}|{g['m']}|" + mesh(g["v"], g["f"]))
for ins in s["insts"]:
    L.append(f"I|{ins['p']}|{ins['n']}|{ins['d']}|" + ",".join(fm(c) for c in ins["o"]) + "|" + ",".join(fm(c) for c in ins["x"]) + "|" + ",".join(fm(c) for c in ins["y"]))
txt = "\n".join(L)
open(sys.argv[2], "w").write(txt)
n = int(sys.argv[3]) if len(sys.argv) > 3 else 60000
chunks, cur = [], []
size = 0
for line in L:
    if size + len(line) > n and cur:
        chunks.append("\n".join(cur)); cur = []; size = 0
    cur.append(line); size += len(line) + 1
if cur: chunks.append("\n".join(cur))
for i, c in enumerate(chunks):
    open(f"{sys.argv[2]}.{i:02d}", "w").write(c)
print(len(L), "satir", len(txt), "bayt", len(chunks), "parca")
