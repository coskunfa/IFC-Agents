# ERA01 SketchUp kurulum kodu (Trimble SketchUp MCP build_model icinde calisir; import yok).
# Veri (v02): era01_data_v02.png (kucuk PNG + sonuna eklenmis era01_model_pack.py metni), session_files ile okunur.
raw = session_files.read_bytes("era01_data_v02.png")
a = raw.find(b"\nERA01DATA\n"); b = raw.find(b"\nERA01END\n")
lines = raw[a + 11:b].decode("utf-8").split("\n")
IN = 1.0 / 2.54
set_display_units("cm")
PAL = {"M_TASIYICI": (110, 110, 110, 255), "M_DIS_DUVAR": (166, 166, 166, 255), "M_IC_DUVAR": (208, 208, 208, 255),
       "M_CEPHE_KAPLAMA": (230, 230, 230, 255), "M_DOSEME": (140, 140, 140, 255), "M_DOSEME_KAPLAMA_KURU": (242, 242, 242, 255),
       "M_DOSEME_KAPLAMA_ISLAK": (218, 221, 224, 255), "M_TAVAN": (250, 250, 250, 255), "M_DOGRAMA_KASA": (74, 74, 74, 255),
       "M_DOGRAMA_CAM": (200, 205, 210, 102), "M_MERDIVEN": (189, 189, 189, 255), "M_CATI": (149, 149, 149, 255),
       "M_ARAZI": (200, 200, 200, 255)}
MAT = {}
for k, c in PAL.items():
    MAT[k] = get_or_create_material(k, c[0], c[1], c[2], c[3])
LAY = {}
def lay(n):
    if n not in LAY:
        L = Layer(); L.set_name(n); model.add_layers([L]); LAY[n] = L
    return LAY[n]
GR = {}
def tag_of(seg):
    if "_KAT_" in seg: return seg.split("_", 1)[1]
    return seg
def grp(path):
    if path in GR: return GR[path]
    ps = path.split("/")
    parent = model.get_entities() if len(ps) == 1 else grp("/".join(ps[:-1])).get_entities()
    g = Group(); parent.add_group(g); g.set_name(ps[-1]); g.set_layer(lay(tag_of(ps[-1])))
    GR[path] = g
    return g
def fill_mesh(ents, vs, fs):
    V = [SUPoint3D(*[float(c) * IN for c in p.split(",")]) for p in vs.split(";")]
    geom = GeometryInput(); geom.set_vertices(V)
    for face in fs.split(";"):
        loops = face.split("/")
        lp = LoopInput()
        for i in loops[0].split(","): lp.add_vertex_index(int(i))
        fi, geom = geom.add_face(lp)
        for inner in loops[1:]:
            il = LoopInput()
            for i in inner.split(","): il.add_vertex_index(int(i))
            geom = geom.face_add_inner_loop(fi, il)
    ents.fill(geom, weld_vertices=True)
def leaf(parent_ents, name, mat, vs, fs):
    g = Group(); parent_ents.add_group(g); g.set_name(name)
    fill_mesh(g.get_entities(), vs, fs)
    apply_material(g, MAT[mat]); g.set_material(MAT[mat])
    return g
DEF = {}
nS = nI = 0; errs = []
blocks = {}
for ln in lines:
    p = ln.split("|")
    try:
        if p[0] == "B":
            blocks[p[1]] = (float(p[2]), float(p[3]) * IN, float(p[4]) * IN)
        elif p[0] == "D":
            cd = DEF.get(p[1])
            if cd is None:
                cd, _ = get_or_create_definition(p[1]); DEF[p[1]] = cd
            leaf(cd.get_entities(), "KASA" if p[2] == "0" else "KANAT", p[3], p[4], p[5])
        elif p[0] == "G":
            cd = DEF[p[1]]
            pts = [SUPoint3D(*[float(c) * IN for c in q.split(",")]) for q in p[2].split(";")]
            geom = GeometryInput(); geom.set_vertices(pts)
            lp = LoopInput()
            for i in range(len(pts)): lp.add_vertex_index(i)
            geom.add_face(lp)
            g = Group(); cd.get_entities().add_group(g); g.set_name("CAM")
            g.get_entities().fill(geom, weld_vertices=True)
            apply_material(g, MAT["M_DOGRAMA_CAM"]); g.set_material(MAT["M_DOGRAMA_CAM"])
        elif p[0] == "S":
            leaf(grp(p[1]).get_entities(), p[2], p[3], p[4], p[5]); nS += 1
        elif p[0] == "I":
            cd = DEF[p[3]]
            o = [float(c) * IN for c in p[4].split(",")]
            x = [float(c) for c in p[5].split(",")]; y = [float(c) for c in p[6].split(",")]
            z = [x[1]*y[2] - x[2]*y[1], x[2]*y[0] - x[0]*y[2], x[0]*y[1] - x[1]*y[0]]
            inst = cd.create_instance(); inst.set_name(p[2])
            inst.set_transform(SUTransformation([x[0], x[1], x[2], 0, y[0], y[1], y[2], 0, z[0], z[1], z[2], 0, o[0], o[1], o[2], 1]))
            grp(p[1]).get_entities().add_instance(inst); nI += 1
    except Exception as ex:
        errs.append(p[0] + ":" + (p[2] if len(p) > 2 else "") + ":" + str(ex)[:80])
for bk, (rot, tx, ty) in blocks.items():
    path = "BLOK_" + bk
    if path in GR:
        th = math.radians(rot); c, s = math.cos(th), math.sin(th)
        GR[path].set_transform(SUTransformation([c, s, 0, 0, -s, c, 0, 0, 0, 0, 1, 0, tx, ty, 0, 1]))
session_state["built"] = True
result = {"solids": nS, "insts": nI, "defs": len(DEF), "errs": errs[:20], "nerr": len(errs)}
