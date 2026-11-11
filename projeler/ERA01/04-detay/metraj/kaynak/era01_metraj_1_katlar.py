# -*- coding: utf-8 -*-
"""ERA01 metraj (DETAY) - adım 1: kat planlarından ham veri.

Girdi : era01_metraj_geo.pkl (era01_metraj_0_duzlestir.py), era01_metraj_inserts.pkl (era01_metraj_0b_...)
Çıktı : era01_metraj_katlar.pkl (makine okunur ham veri) + ../onizleme/ERA01_metraj_duvar_<kat>.png

Her kat için (DXF birimi cm, blok yerel koordinatı = HACİM'in aks çapası; 02-model/kaynak/era01_model_dxfoku_2_katlar.py):
  * mahaller      : 0_IFC_Area kapalı poligonları + 0_IFC_ROOM_TEXT_50 yazıları (ad, yazılı alan)
  * kapalı iz (Fc): 1 cm raster. Mürekkep = 2_IFC_Wall + 3_IFC_Window + 1/2_IFC_Door (yaylar hariç)
                    + 1_IFC_Concrete_Section + 0_IFC_Area + 5_IFC_Mechanical_Shaft çizgileri.
                    Kenardan taşma (flood) ile dış bölge bulunur; geri kalan = yapı izi F.
                    Fc = F − (TERAS/BALKON/KAT BAHÇESİ mahalleri)
  * duvar bölgesi : W = F − mahaller − şaftlar (boşluklar W içinde kalır = boşluklu brüt duvar izi)
                    kagir = W − betonarme (1_IFC_Concrete_Section); 80 cm'den kalın kütleler (mahal poligonu
                    çizilmemiş hol/rüzgarlık) duvar sayılmaz, ayrı raporlanır.
  * kalınlık      : morfolojik açma (disk çapı 12.5/17.5/22.5/27.5/35/45 cm) -> sınıf 10/15/20/25/30/40/50 cm.
                    Uzunluk = sınıf plan alanı / sınıf kalınlığı.
  * dış/iç        : dış bölgeye (dış + teras/avlu mahalleri) kalınlık+3 cm'den yakın kagir piksel = dış duvar.
  * doğramalar    : 0_IFC_Window_Text etiketleri (TİP, GENİŞLİK, YÜKSEKLİK), KAPI POZU etiketleri (Kxx, gen/yük)
  * kolon/perde   : 1_IFC_Concrete_Section poligon birleşimi -> parça; boyut, alan, dış çevreye değiyor mu
  * merdiven      : 0_IFC_Stair_Text "M: rıht x adet / basamak" + 1_IFC_Stair basamak çizgisi boyu (kol genişliği)
  * korkuluk      : 2_IFC_Handrail çizgileri (plan)
  * armatürler    : 6_IFC_Furniture_WC / _Wetspace blok referansları (etkin blok adı) + bulunduğu mahal
"""
import os, sys, re, math, pickle, json, collections
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
from shapely.geometry import Polygon, Point, LineString, MultiPolygon, box
from shapely.ops import unary_union
import contourpy

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from era01_katlar import KATLAR
OUTDIR = os.path.join(HERE, "..", "onizleme")
os.makedirs(OUTDIR, exist_ok=True)

GEO = pickle.load(open(os.path.join(HERE, "era01_metraj_geo.pkl"), "rb"))
G = GEO["geo"]
INS = pickle.load(open(os.path.join(HERE, "era01_metraj_inserts.pkl"), "rb"))

# HACİM çapaları (blok yerel koordinat orijini, DXF model alanı)
ANC = {"A-blok-1-bodrum": (94875, 26684), "A-blok-zemin-kat": (98944, 26684), "A-blok-1-kat": (103020, 27598),
       "B-blok-2-bodrum": (94839, 22410), "B-blok-1-bodrum": (99752, 23172), "B-blok-zemin-kat": (103107, 23172),
       "C-blok-1-bodrum": (94915, 18651), "C-blok-zemin-kat": (97415, 18651),
       "D-blok-1-bodrum": (94961, 14353), "D-blok-zemin-kat": (97584, 14353), "D-blok-1-kat": (99884, 14353)}
KATKISA = {"A-blok-1-bodrum": "B1", "A-blok-zemin-kat": "ZK", "A-blok-1-kat": "K1", "B-blok-2-bodrum": "B2",
           "B-blok-1-bodrum": "B1", "B-blok-zemin-kat": "ZK", "C-blok-1-bodrum": "B1", "C-blok-zemin-kat": "ZK",
           "D-blok-1-bodrum": "B1", "D-blok-zemin-kat": "ZK", "D-blok-1-kat": "K1"}
DIS_MAHAL = ("TERAS", "BALKON", "KAT BAHÇESİ")
SINIF = [10, 15, 20, 25, 30, 40, 50]          # nominal duvar kalınlıkları (cm)
SINIR = [12.5, 17.5, 22.5, 27.5, 35, 45]      # sınıflar arası eşikler (cm)
MAX_DUVAR = 80                                # bundan kalın kagir kütle = çizilmemiş mahal

def first_pt(e):
    if "pts" in e: return e["pts"][0]
    if "loops" in e: return e["loops"][0][0]
    return (e.get("x", 0), e.get("y", 0))

def in_frame(p, fr):
    return fr[0] <= p[0] <= fr[2] and fr[1] <= p[1] <= fr[3]

def is_num(s):
    return re.fullmatch(r"[\d.,]+", s.strip() or "x") is not None

def kat_ents(K):
    fr = K["frame"]
    ins = set(K["ins"])
    E = [e for e in G if e["blk"] and e["blk"][0] in ins and in_frame(first_pt(e), fr)]
    KP = [e for e in G if e["blk"] and e["blk"][0].endswith("KAPI POZU") and in_frame(first_pt(e), fr)]
    return E, KP

def local(p, anc):
    return (p[0] - anc[0], p[1] - anc[1])

def poly_ok(pts):
    if len(pts) < 3: return None
    p = Polygon(pts).buffer(0)
    return p if p.area > 1 else None

def mahaller(E, anc):
    polys = []
    for e in E:
        if e["lay"] == "0_IFC_Area" and e["t"] == "P":
            p = poly_ok([local(q, anc) for q in e["pts"]])
            if p is not None: polys.append(p)
    # yinelenenleri ayıkla
    uniq = []
    for p in polys:
        if not any(abs(p.area - q.area) < 1 and p.centroid.distance(q.centroid) < 1 for q in uniq): uniq.append(p)
    T = [e for e in E if e["t"] == "T" and any("ROOM_TEXT" in b for b in e["blk"])]
    rooms = []
    for p in uniq:
        inside = [e for e in T if p.contains(Point(local((e["x"], e["y"]), anc)))]
        names = [e["txt"].strip() for e in inside if e["txt"].strip() and not is_num(e["txt"]) and ":" not in e["txt"]
                 and e["txt"].strip() not in ("m²", "m2")]
        nums = [float(e["txt"].replace(",", ".")) for e in inside if is_num(e["txt"]) and e["txt"].count(".") <= 1 and e["txt"].strip() not in (".",)]
        fin = [e["txt"].strip() for e in inside if ":" in e["txt"]]
        # yazı yüksekliği en büyük olan ad
        nm = names[0] if names else "?"
        rooms.append(dict(ad=nm, alan_yazi=(nums[0] if nums else None), alan_pol=p.area / 1e4,
                          cevre=p.length / 100, poly=p, notlar=sorted(set(fin))))
    return rooms

def raster(E, anc, lays, bb, fill=False, skiparc=True, only=None):
    X0, Y0, Wd, Ht = bb
    im = Image.new("1", (Wd, Ht), 0); dr = ImageDraw.Draw(im)
    for e in E:
        if e["lay"] not in lays or e["t"] not in "LP": continue
        if only and not only(e): continue
        if skiparc and e.get("ty") == "ARC": continue
        pts = [(q[0] - anc[0] - X0, Ht - 1 - (q[1] - anc[1] - Y0)) for q in e["pts"]]
        if len(pts) < 2: continue
        if e["t"] == "P" and fill and len(pts) > 2: dr.polygon(pts, fill=1, outline=1)
        elif e["t"] == "P": dr.line(pts + [pts[0]], fill=1, width=1)
        else: dr.line(pts, fill=1, width=1)
    return np.array(im, bool)

def poly_raster(polys, bb):
    X0, Y0, Wd, Ht = bb
    im = Image.new("1", (Wd, Ht), 0); dr = ImageDraw.Draw(im)
    for p in polys:
        for g in getattr(p, "geoms", [p]):
            dr.polygon([(x - X0, Ht - 1 - (y - Y0)) for x, y in g.exterior.coords], fill=1, outline=1)
            for h in g.interiors:
                dr.polygon([(x - X0, Ht - 1 - (y - Y0)) for x, y in h.coords], fill=0, outline=0)
    return np.array(im, bool)

def opening(mask, D):
    """disk çaplı açma: çap D'den ince kısımları siler."""
    r = D / 2.0
    dt = ndi.distance_transform_edt(mask)
    core = dt >= r
    if not core.any(): return np.zeros_like(mask)
    d2 = ndi.distance_transform_edt(~core)
    return (d2 <= r) & mask

def mask_to_polys(mask, bb):
    X0, Y0, Wd, Ht = bb
    gen = contourpy.contour_generator(z=mask.astype(float), name="serial")
    lines = gen.lines(0.5)
    rings = []
    for L in lines:
        if len(L) < 4: continue
        pts = [(X0 + c[0], Y0 + (Ht - 1 - c[1])) for c in L]
        pg = Polygon(pts)
        if pg.is_valid and pg.area > 2: rings.append(pg)
        elif pg.area > 2: rings.append(pg.buffer(0))
    # dış halkalar ve delikler: alanı büyükten küçüğe, içerilen = delik
    rings.sort(key=lambda p: -p.area)
    res = []
    for r in rings:
        placed = False
        for i, (outer, holes) in enumerate(res):
            if outer.contains(r.representative_point()):
                # çift içerilme: deliğin içindeki ada
                if any(h.contains(r.representative_point()) for h in holes):
                    continue
                holes.append(r); placed = True; break
        if not placed: res.append((r, []))
    out = []
    for outer, holes in res:
        p = outer
        for h in holes: p = p.difference(h)
        out.append(p)
    return unary_union(out).simplify(1.5)

def window_tags(E, anc):
    circ = [e for e in E if e["lay"] == "0_IFC_Window_Text" and e.get("ty") == "CIRCLE"]
    T = [e for e in E if e["t"] == "T"]
    leaders = [e for e in E if e["lay"] == "0_IFC_Window_Text" and e["t"] == "L"]
    out = []
    for c in circ:
        xs = [p[0] for p in c["pts"]]; ys = [p[1] for p in c["pts"]]
        cx, cy = (max(xs) + min(xs)) / 2, (max(ys) + min(ys)) / 2; r = (max(xs) - min(xs)) / 2
        same = [e for e in T if e["blk"] == c["blk"] and math.hypot(e["x"] - cx, e["y"] - cy) < 110]
        tip = [e["txt"].strip() for e in same if re.match(r"^P-\d+", e["txt"].strip()) and math.hypot(e["x"] - cx, e["y"] - cy) < r * 2.2]
        nums = [e for e in same if is_num(e["txt"]) and math.hypot(e["x"] - cx, e["y"] - cy) > r * 1.5]
        # leader: dairenin merkezinden çıkan çizgi, uzak ucu = doğrama
        tgt = None
        for L in leaders:
            if L["blk"] != c["blk"]: continue
            a, b = L["pts"][0], L["pts"][-1]
            da, db = math.hypot(a[0] - cx, a[1] - cy), math.hypot(b[0] - cx, b[1] - cy)
            if min(da, db) <= r * 1.3:
                tgt = b if db > da else a; break
        if tgt is None: tgt = (cx, cy)
        # genişlik / yükseklik: lider doğrultusuna dik eksende sol = genişlik, sağ = yükseklik (etiket bloğu düzeni)
        w = h = None
        if len(nums) >= 2:
            vx, vy = tgt[0] - cx, tgt[1] - cy; n = math.hypot(vx, vy) or 1
            # etiket yerel x ekseni: lider aşağı bakarken (+x sağ). Genel: sağ vektör = (−vy, vx) döndürülmüş
            rx, ry = vy / n * -1, vx / n  # sağa dik (lider aşağı (0,-1) iken (1,0))
            rx, ry = -vy / n, vx / n
            nums_s = sorted(nums, key=lambda e: (e["x"] - cx) * rx + (e["y"] - cy) * ry)
            w, h = float(nums_s[0]["txt"]), float(nums_s[-1]["txt"])
        elif len(nums) == 1:
            w = float(nums[0]["txt"])
        out.append(dict(tip=tip[0] if tip else "?", gen=w, yuk=h, etiket=local((cx, cy), anc), hedef=local(tgt, anc)))
    return out

def door_tags(KP, anc):
    T = [e for e in KP if e["t"] == "T"]
    ks = [e for e in T if re.match(r"^K\d+", e["txt"].strip())]
    out = []
    for k in ks:
        sz = [e for e in T if re.match(r"^\d+/\d+$", e["txt"].strip()) and math.hypot(e["x"] - k["x"], e["y"] - k["y"]) < 45]
        sz = min(sz, key=lambda e: math.hypot(e["x"] - k["x"], e["y"] - k["y"])) if sz else None
        p = local((k["x"], k["y"]), anc)
        if any(o["kod"] == k["txt"].strip() and math.hypot(o["poz"][0] - p[0], o["poz"][1] - p[1]) < 5 for o in out):
            continue  # aynı bloğun ikinci kez yerleştirilmesi (A_K1_KAPI POZU iki kez)
        g, y = (map(float, sz["txt"].split("/")) if sz else (None, None))
        out.append(dict(kod=k["txt"].strip(), gen=g, yuk=y, poz=p))
    return out

def door_inserts(K, anc):
    fr = K["frame"]; ins = set(K["ins"])
    out = []
    for x in INS:
        if not x["chain"] or x["chain"][0] not in ins or not in_frame((x["x"], x["y"]), fr): continue
        nm = x["eff"]
        if re.search(r"DOOR|KAPI|KANAT", nm, re.I) and "POZU" not in nm:
            p = local((x["x"], x["y"]), anc)
            if any(o["ad"] == nm and math.hypot(o["poz"][0] - p[0], o["poz"][1] - p[1]) < 3 for o in out): continue
            out.append(dict(ad=nm, poz=p, rot=x["rot"], sx=x["sx"]))
    return out

FIXRX = [("KLOZET", "Klozet"), ("LAVABO", "Lavabo"), ("SINK", "Lavabo/eviye (SINK)"), ("DUS KOSE", "Duş (köşe)"),
         ("DUS", "Duş (kabinli)"), ("SUZGEC", "Lineer süzgeç"), ("EVYE", "Mutfak eviyesi"), ("OCAK", "Ocak"),
         ("CAMASIR", "Çamaşır makinesi yeri"), ("TUTUNMA", "Tutunma barı"), ("L TEZGAH", "Tezgah (L)"),
         ("MUTFAK TEZGAH", "Tezgah"), ("KUVET", "Küvet"), ("PISUVAR", "Pisuvar")]

def fixtures(K, anc, rooms):
    fr = K["frame"]; ins = set(K["ins"])
    laynm = FIXLAY
    out = []
    for x in INS:
        if not x["chain"] or x["chain"][0] not in ins or not in_frame((x["x"], x["y"]), fr): continue
        L = laynm.get(x["name"], {})
        top = max(L, key=L.get) if L else ""
        nm = x["eff"]
        if not (top.startswith("6_IFC_Furniture_W") or re.search("KLOZET|LAVABO|DUS|EVYE|SINK", nm)): continue
        tur = None
        for k, v in FIXRX:
            if k in nm.upper(): tur = v; break
        if tur is None: tur = "Tanımsız blok (" + nm + ")"
        p = local((x["x"], x["y"]), anc)
        # blok içeriği kutusu -> merkez (ekleme noktası köşede olabilir)
        bbx = FIXBB.get(x["name"])
        rm = None
        best = 1e9
        for r in rooms:
            dd = r["poly"].distance(Point(p))
            if dd < best: best, rm = dd, r["ad"]
        if any(o["blok"] == x["name"] and math.hypot(o["poz"][0] - p[0], o["poz"][1] - p[1]) < 3 for o in out): continue
        out.append(dict(tur=tur, ad=nm, blok=x["name"], katman=top, poz=p, mahal=rm, mahal_uzaklik=round(best, 1)))
    return out

FIXLAY = collections.defaultdict(collections.Counter)
FIXBB = {}
for e in G:
    if e["blk"]: FIXLAY[e["blk"][-1]][e["lay"]] += 1

def stairs(E, anc):
    T = [e for e in E if e["t"] == "T" and e["lay"] == "0_IFC_Stair_Text" and e["txt"].strip().startswith("M:")]
    tl = [e for e in E if e["lay"] in ("1_IFC_Stair",) and e["t"] == "L" and len(e["pts"]) == 2]
    out = []
    for t in T:
        m = re.match(r"M:\s*([\d.]+)\s*x\s*(\d+)\s*/\s*([\d.]+)", t["txt"].strip())
        if not m: continue
        p = local((t["x"], t["y"]), anc)
        if any(math.hypot(o["poz"][0] - p[0], o["poz"][1] - p[1]) < 5 for o in out): continue
        # yakındaki basamak çizgileri (aynı blok zinciri, 4 m içinde): en sık boy = kol genişliği
        lens = []
        for L in tl:
            a, b = L["pts"]
            mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
            if L["blk"][0] == t["blk"][0] and math.hypot(mx - t["x"], my - t["y"]) < 400:
                lens.append(round(math.hypot(b[0] - a[0], b[1] - a[1]) / 5) * 5)
        c = collections.Counter(l for l in lens if l >= 80)
        wdt, nl = (c.most_common(1)[0] if c else (None, 0))
        out.append(dict(yazi=t["txt"].strip(), riht=float(m.group(1)), adet=int(m.group(2)), basamak=float(m.group(3)),
                        kol_gen=wdt, basamak_cizgi=nl, poz=p, blok=t["blk"][0]))
    return out

def run():
    RES = {}
    for K in KATLAR:
        kod = K["kod"]; anc = ANC[kod]
        E, KP = kat_ents(K)
        rooms = mahaller(E, anc)
        # tuval
        pts = [local(q, anc) for e in E if e["lay"] in ("2_IFC_Wall", "0_IFC_Area", "1_IFC_Concrete_Section") and e["t"] in "LP" for q in e["pts"]]
        xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
        X0, Y0 = int(min(xs)) - 60, int(min(ys)) - 60
        Wd, Ht = int(max(xs) - X0) + 60, int(max(ys) - Y0) + 60
        bb = (X0, Y0, Wd, Ht)
        ink = raster(E, anc, {"2_IFC_Wall", "3_IFC_Window", "1_IFC_Door", "2_IFC_Door", "1_IFC_Concrete_Section",
                              "0_IFC_Area", "5_IFC_Mechanical_Shaft", "0_IFC_Brüt_Alan"}, bb)
        lab, n = ndi.label(~ink)
        border = np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))
        ext = np.isin(lab, border[border > 0])
        F = ~ext
        brut_pol0 = [poly_ok([local(q, anc) for q in e["pts"]]) for e in E if e["lay"] == "0_IFC_Brüt_Alan" and e["t"] == "P"]
        brut_pol0 = [p for p in brut_pol0 if p is not None]
        bu = unary_union(brut_pol0) if brut_pol0 else None
        for r in rooms:
            r["dis"] = r["ad"].upper().startswith(DIS_MAHAL)
            # brüt poligonu varsa ve mahal büyük ölçüde dışındaysa (ör. A ZK giriş merdiveni) dış mahal say
            if bu is not None and not r["dis"] and r["poly"].difference(bu.buffer(5)).area > 0.5 * r["poly"].area:
                r["dis"] = True; r["dis_neden"] = "brüt poligonu dışında"
        room_m = poly_raster([r["poly"] for r in rooms], bb)
        out_m = poly_raster([r["poly"] for r in rooms if r["dis"]], bb)
        in_m = room_m & ~out_m
        shaft = raster(E, anc, {"5_IFC_Mechanical_Shaft"}, bb, fill=True)
        conc = raster(E, anc, {"1_IFC_Concrete_Section"}, bb, fill=True)
        brut_pol = brut_pol0
        W = F & ~room_m & ~shaft
        W = ndi.binary_opening(W, structure=np.ones((3, 3)))  # 1-2 cm'lik kırpıntıları at
        concW = conc & F
        kag = W & ~conc
        # çok kalın kütle (çizilmemiş mahal) ayıkla
        blob = opening(kag, MAX_DUVAR)
        blob = ndi.binary_dilation(blob, iterations=3) & kag
        kag2 = kag & ~blob
        # kalınlık sınıfları
        # teras/avlu kenarı bandı: hem gerçek dışa hem dış mahale 30 cm'den yakın, iç mahale 30 cm'den uzak
        d_ext = ndi.distance_transform_edt(~ext); d_out = ndi.distance_transform_edt(~out_m); d_in = ndi.distance_transform_edt(~in_m)
        par = W & (d_ext <= 30) & (d_out <= 30) & (d_in > 30)
        par_kag = par & kag2
        kag2 = kag2 & ~par
        cls = np.zeros(kag2.shape, np.uint8)  # 0 = en ince sınıf
        for i, D in enumerate(SINIR):
            o = opening(kag2, D)
            cls[o] = i + 1
        # köşe/birleşim kırpıntıları: boyu < max(100, 3t) olan kalın sınıf parçaları komşu sınıfa katılır
        for i in range(len(SINIF) - 1, 0, -1):
            labc, nc = ndi.label(kag2 & (cls == i))
            if nc == 0: continue
            sl = ndi.find_objects(labc)
            for j, s_ in enumerate(sl, 1):
                comp = labc[s_] == j
                ar = comp.sum(); t = SINIF[i]
                if ar / t < max(100, 3 * t):
                    pad = tuple(slice(max(0, a.start - 3), a.stop + 3) for a in s_)
                    cm = (labc[pad] == j)
                    ring = ndi.binary_dilation(cm, iterations=2) & ~cm & kag2[pad]
                    nb = cls[pad][ring]
                    nb = nb[nb != i]
                    if nb.size:
                        new_c = np.bincount(nb).argmax()
                        sub = cls[pad]; sub[cm] = new_c; cls[pad] = sub
        # dış komşuluk
        extz = ext | out_m
        dext = ndi.distance_transform_edt(~extz)
        Fc = F & ~out_m & ~par
        walls = []
        for i, t in enumerate(SINIF):
            m = kag2 & (cls == i)
            if not m.any(): continue
            dis = m & (dext <= t + 3)
            ic = m & ~dis
            for tur, mm in (("dis", dis), ("ic", ic)):
                a = mm.sum() / 1e4
                if a > 0.005:
                    walls.append(dict(tur=tur, kal=t, plan_m2=a, uzunluk_m=a / (t / 100.0)))
        # kolon / perde (vektör)
        cpolys = [poly_ok([local(q, anc) for q in e["pts"]]) for e in E if e["lay"] == "1_IFC_Concrete_Section" and e["t"] == "P"]
        cu = unary_union([p for p in cpolys if p is not None])
        Fc_poly = mask_to_polys(Fc, bb)
        F_poly = mask_to_polys(F, bb)
        extpoly = F_poly.buffer(0)
        cols = []
        for pc in getattr(cu, "geoms", [cu]):
            if pc.is_empty or pc.area < 50: continue
            mrr = pc.minimum_rotated_rectangle
            cc = list(mrr.exterior.coords)
            s1 = math.hypot(cc[1][0] - cc[0][0], cc[1][1] - cc[0][1]); s2 = math.hypot(cc[2][0] - cc[1][0], cc[2][1] - cc[1][1])
            L, T_ = max(s1, s2), min(s1, s2)
            tkal = 2 * pc.area / pc.length if pc.length else T_  # ince parçalar için ortalama kalınlık ~ 2A/P
            perde = (L >= 6 * T_) or (pc.area / (L * T_) < 0.8 and L > 150)
            dis = pc.buffer(4).intersects(Polygon(extpoly.exterior) .exterior) if hasattr(extpoly, "exterior") else False
            if not hasattr(extpoly, "exterior"):
                dis = any(pc.buffer(4).intersects(gg.exterior) for gg in extpoly.geoms)
            cols.append(dict(alan_m2=pc.area / 1e4, L=round(L), t=round(T_), t_ort=round(tkal, 1), perde=bool(perde),
                             dis_cevre=bool(dis), merkez=(pc.centroid.x, pc.centroid.y), poly=pc))
        # dış çevre parçaları: her 10 cm'de bir örnek, içerideki malzeme (perde mi?)
        perde_m = poly_raster([c["poly"] for c in cols if c["perde"]], bb)
        cevre = []
        for gg in getattr(Fc_poly, "geoms", [Fc_poly]):
            for ring in [gg.exterior] + list(gg.interiors):
                Ltot = ring.length
                nseg = max(1, int(Ltot / 10))
                cnt = collections.Counter()
                for k in range(nseg):
                    pt = ring.interpolate((k + 0.5) * Ltot / nseg)
                    # içeri doğru 6 cm: perde mi
                    ix, iy = int(round(pt.x - X0)), int(round(Ht - 1 - (pt.y - Y0)))
                    hit = perde_m[max(0, iy - 6):iy + 7, max(0, ix - 6):ix + 7].any()
                    # teras/avlu komşusu mu
                    nxt = out_m[max(0, iy - 6):iy + 7, max(0, ix - 6):ix + 7].any()
                    cnt[("perde" if hit else "diger", "teras" if nxt else "acik")] += Ltot / nseg
                cevre.append(dict(uzunluk=Ltot / 100, dagilim={"%s|%s" % k: v / 100 for k, v in cnt.items()}))
        wt = window_tags(E, anc)
        dt = door_tags(KP, anc)
        di = door_inserts(K, anc)
        fx = fixtures(K, anc, rooms)
        st = stairs(E, anc)
        # korkuluk çizgileri (plan)
        hr = []
        for e in E:
            if e["lay"] == "2_IFC_Handrail" and e["t"] in "LP" and len(e["pts"]) >= 2:
                pts_ = [local(q, anc) for q in e["pts"]]
                ls = LineString(pts_ + ([pts_[0]] if e["t"] == "P" else []))
                hr.append(dict(blk=e["blk"][0], uzunluk=ls.length / 100, geom=ls))
        # şaft alanı
        shaft_a = shaft.sum() / 1e4
        RES[kod] = dict(kod=kod, blok=K["blok"], kat=KATKISA[kod], ad=K["ad"], anc=anc, bb=bb,
                        rooms=rooms, walls=walls, cols=cols, Fc_m2=Fc.sum() / 1e4, F_m2=F.sum() / 1e4,
                        Fc_poly=Fc_poly, F_poly=F_poly, brut_pol=[p.area / 1e4 for p in brut_pol],
                        brut_poly=brut_pol, W_m2=W.sum() / 1e4, conc_m2=concW.sum() / 1e4, kagir_m2=kag2.sum() / 1e4,
                        blob_m2=blob.sum() / 1e4, parapet_m2=par.sum() / 1e4,
                        parapet_m=(par.sum() / 1e4) / 0.20 if par.any() else 0.0, shaft_m2=shaft_a, cevre=cevre, wins=wt, doors=dt, door_ins=di,
                        fix=fx, stairs=st, handrail=hr)
        # önizleme
        img = np.full((Ht, Wd, 3), 255, np.uint8)
        img[room_m] = (245, 240, 215); img[out_m] = (215, 235, 205); img[shaft] = (190, 190, 240)
        pal = {10: (120, 170, 255), 15: (40, 120, 230), 20: (250, 170, 60), 25: (220, 60, 40), 30: (150, 30, 140), 40: (60, 60, 60), 50: (0, 0, 0)}
        for i, t in enumerate(SINIF):
            img[kag2 & (cls == i)] = pal[t]
        img[concW] = (40, 150, 70); img[blob] = (255, 0, 255); img[par] = (150, 220, 150)
        im = Image.fromarray(img)
        dr = ImageDraw.Draw(im)
        for w in wt:
            x, y = w["hedef"]; dr.ellipse([x - X0 - 12, Ht - 1 - (y - Y0) - 12, x - X0 + 12, Ht - 1 - (y - Y0) + 12], outline=(0, 0, 255), width=3)
        for d_ in dt:
            x, y = d_["poz"]; dr.rectangle([x - X0 - 10, Ht - 1 - (y - Y0) - 10, x - X0 + 10, Ht - 1 - (y - Y0) + 10], outline=(255, 0, 0), width=3)
        sc = 1600 / max(Wd, Ht)
        im = im.resize((max(1, int(Wd * sc)), max(1, int(Ht * sc))), Image.LANCZOS)
        im.save(os.path.join(OUTDIR, "ERA01_metraj_duvar_%s_%s.png" % (K["blok"], KATKISA[kod])))
        print(kod, "F %.1f Fc %.1f brut %s | W %.1f kagir %.1f beton %.1f blob %.1f | mahal %d pencere %d kapı %d/%d fix %d merd %d" % (
            F.sum() / 1e4, Fc.sum() / 1e4, [round(b, 2) for b in RES[kod]["brut_pol"]], W.sum() / 1e4, kag2.sum() / 1e4,
            concW.sum() / 1e4, blob.sum() / 1e4, len(rooms), len(wt), len(dt), len(di), len(fx), len(st)))
        for w in walls: print("    duvar %s %d cm: %.2f m² plan, %.1f m" % (w["tur"], w["kal"], w["plan_m2"], w["uzunluk_m"]))
    pickle.dump(RES, open(os.path.join(HERE, "era01_metraj_katlar.pkl"), "wb"), protocol=4)

if __name__ == "__main__":
    run()
