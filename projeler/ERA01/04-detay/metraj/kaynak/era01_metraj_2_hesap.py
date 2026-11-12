# -*- coding: utf-8 -*-
"""ERA01 metraj (DETAY) - adım 2: miktarlar.

Girdi : era01_metraj_katlar.pkl (adım 1), era01_metraj_geo.pkl (vaziyet, çatı planları),
        02-model/kaynak/era01_model_rapor_v03.json (kat kotları, HACİM pencere tablosu),
        03-boyama/kaynak/era01_ozet.json (PAFTA mahal/brüt alanları, kontrol için)
Çıktı : era01_metraj_tablolar.json (Excel adımı bunu okur)

Birimler: uzunluk m, alan m², hacim m³. Kotlar m. Hesaplar 2 ondalık.
"""
import os, sys, re, math, json, pickle, collections
from shapely.geometry import Polygon, Point, LineString, MultiPolygon, box
from shapely.ops import unary_union, polygonize
from shapely import affinity
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
R = pickle.load(open(os.path.join(HERE, "era01_metraj_katlar.pkl"), "rb"))
GEO = pickle.load(open(os.path.join(HERE, "era01_metraj_geo.pkl"), "rb"))
G = GEO["geo"]
RAP = json.load(open(os.path.join(PROJ, "02-model", "kaynak", "era01_model_rapor_v03.json")))
OZ = json.load(open(os.path.join(PROJ, "03-boyama", "kaynak", "era01_ozet.json")))

r2 = lambda v: None if v is None else round(float(v), 2)
BLOKLAR = ["A", "B", "C", "D"]
KATSIRA = {"B2": 0, "B1": 1, "ZK": 2, "K1": 3}
KATAD = {"B2": "2. Bodrum", "B1": "1. Bodrum", "ZK": "Zemin kat", "K1": "1. Kat"}

# ------------------------------------------------------------------ kat parametreleri
KAPL, DOS, ROOF_T = 0.10, 0.30, 0.30          # kaplama+şap, taşıyıcı döşeme, çatı döşemesi (HACİM paketi, OKUBENI)
RADYE = {"A": 0.50, "B": 1.00, "C": 0.50, "D": 0.50}   # kesit 1-1 kotlarından (radye üst = kat −0.50)
RADYE_UST = 0.50                              # en alt kat kotu − radye üstü (kesit: −0.50)
GROBLOK = 0.25                                # grobeton 10 + blokaj 15 (ATIKSU DETAY yazıları; varsayım)
KAT = {}
for b in BLOKLAR:
    kl = RAP["blocks"][b]["kat"]
    for i, k in enumerate(kl):
        kod = [c for c, v in R.items() if v["blok"] == b and v["kat"] == k["kat"]][0]
        top = (i == len(kl) - 1)
        en_alt = (i == 0)
        base = k["kot"] - (RADYE_UST if en_alt else KAPL)
        tepe = k["ust_kat_kotu"] - ROOF_T if top else k["ust_kat_kotu"] - KAPL - DOS
        KAT[kod] = dict(blok=b, kat=k["kat"], kot=k["kot"], ust=k["ust_kat_kotu"], tavan=k["tavan_kotu"],
                        net_h=round(k["tavan_kotu"] - k["kot"], 2), kat_h=round(k["ust_kat_kotu"] - k["kot"], 2),
                        top=top, en_alt=en_alt, bodrum=k["kat"].startswith("B"),
                        H_duvar=round(tepe - base, 2), duvar_alt=round(base, 2), duvar_ust=round(tepe, 2),
                        h_cephe=round((k["ust_kat_kotu"] - ROOF_T - k["kot"]) if top else (k["ust_kat_kotu"] - k["kot"]), 2))
KODS = sorted(R, key=lambda c: (R[c]["blok"], KATSIRA[R[c]["kat"]]))

# ------------------------------------------------------------------ mahal sınıfları ve malzemeler
def grup(ad, dis):
    a = ad.upper().replace("İ", "I").replace("Ş", "S").replace("Ö", "O").replace("Ü", "U").replace("Ç", "C").replace("Ğ", "G")
    if dis:
        if "MERDIVEN" in a: return "dis_merdiven"
        return "teras"
    if any(k in a for k in ("BANYO", "WC", "DUS", "HAMAM", "SAUNA", "SOYUNMA")): return "islak"
    if a == "MUTFAK": return "mutfak"
    if "MERDIVEN" in a: return "merdiven"
    if "OTOPARK" in a: return "otopark"
    if "TEKNIK" in a: return "teknik"
    if "HAVUZ" in a: return "havuz"
    if any(k in a for k in ("HOL", "KORIDOR")): return "sirkulasyon"
    if any(k in a for k in ("TEMIZLIK", "DEPO")): return "servis"
    return "kuru"

GRUPAD = {"islak": "Islak hacim", "mutfak": "Mutfak", "kuru": "Kuru (yaşam/yatak)", "sirkulasyon": "Sirkülasyon (hol/koridor)",
          "servis": "Servis (depo/temizlik)", "merdiven": "Merdiven evi", "otopark": "Otopark", "teknik": "Teknik hacim",
          "havuz": "Havuz salonu", "teras": "Teras/balkon/avlu (açık)", "dis_merdiven": "Dış merdiven (bina girişi)"}
MALZ = {  # zemin, duvar, tavan, süpürgelik var mı, sıva var mı
    "islak": ("ZM-01 Seramik/granit 60x120", "Seramik (tavan yüksekliğine kadar)", "Asma tavan, suya dayanıklı alçı levha + boya (varsayım)", False, True),
    "mutfak": ("ZM-01 Seramik/granit 60x120 (varsayım)", "DV-01 Saten boya (tezgah arası seramik ayrıca)", "Alçı sıva + boya (DXF: TAVAN BOYA)", True, True),
    "kuru": ("ZM-02 Lamine parke", "DV-01 Saten boya", "Alçı sıva + boya (DXF: TAVAN BOYA)", True, True),
    "sirkulasyon": ("ZM-01 Seramik/granit 60x120 (DXF: SERAMİK)", "DV-01 Saten boya", "Alçı sıva + boya (DXF: TAVAN BOYA)", True, True),
    "servis": ("ZM-01 Seramik/granit 60x120 (DXF: SERAMİK)", "DV-01 Saten boya", "Alçı sıva + boya (DXF: TAVAN BOYA)", True, True),
    "merdiven": ("Malzeme belirsiz (DXF: SERAMİK; doğal taş/granit olabilir)", "DV-01 Saten boya", "Alçı sıva + boya (DXF: TAVAN BOYA)", True, True),
    "otopark": ("Beton yüzey sertleştirici / epoksi (varsayım)", "Perde/blok üzeri boya (varsayım, sıva yok)", "Brüt beton üzeri boya (varsayım)", False, False),
    "teknik": ("Beton yüzey sertleştirici / epoksi (varsayım)", "Perde/blok üzeri boya (varsayım, sıva yok)", "Brüt beton üzeri boya (varsayım)", False, False),
    "havuz": ("Malzeme belirsiz (havuz çevresi seramik/doğal taş; havuz teknesi ayrıca)", "Malzeme belirsiz (nem dayanımlı)", "Asma tavan, nem dayanımlı (varsayım)", False, True),
    "teras": ("Malzeme belirsiz (dış mekan seramik/deck)", "-", "-", False, False),
    "dis_merdiven": ("Malzeme belirsiz (dış merdiven)", "-", "-", False, False),
}
ISLAK_TAVAN = ("islak", "havuz")

# ------------------------------------------------------------------ yardımcılar
NOTLAR = []          # numaralı varsayım/doğrulanacak listesi
def note(txt, tur="varsayım"):
    for i, (t, x) in enumerate(NOTLAR):
        if x == txt: return i + 1
    NOTLAR.append((tur, txt)); return len(NOTLAR)

def wdir(w):
    return w

# P-01 (900x630, ZK+1. kat galeri) iki katta da etiketli: doğrama tablosunda bir kez, yüzey düşümünde katlara bölünür
def opening_h(w, kod, cap):
    """bu katta düşülecek boşluk yüksekliği (m)."""
    h = (w["yuk"] or 0) / 100.0
    if w.get("tip") == "P-01":
        h = KAT[kod]["kat_h"] if R[kod]["kat"] == "ZK" else (6.30 - KAT["A-blok-zemin-kat"]["kat_h"])
    return min(h, cap)

# kat başına doğramalar: pencere etiketleri + kapılar
def kat_openings(kod):
    v = R[kod]; ops = []
    for w in v["wins"]:
        ops.append(dict(cins="pencere", tip=w["tip"], gen=(w["gen"] or 0) / 100.0, yuk=(w["yuk"] or 0) / 100.0, dis=w["dis"],
                        mahal=w["mahal_i"], kal=w["duvar_kal"], mal=w["duvar_mal"], raw=w))
    for d in v["doors"]:
        ops.append(dict(cins="kapı", tip=d["kod"], gen=(d["gen"] or 0) / 100.0, yuk=(d["yuk"] or 0) / 100.0, dis=d["dis"],
                        mahal=d["mahal_i"], kal=d["duvar_kal"], mal=d["duvar_mal"], raw=d))
    for d in v["doors_extra"]:
        if d["dis"] and d["pencere_icinde"]: continue           # kapı-pencere kanadı, pencere boşluğu içinde
        if d["blok"] == "CIFT KANAT" and kod == "A-blok-1-kat":
            ops.append(dict(cins="pencere", tip="P-ETIKETSIZ", gen=3.75, yuk=2.80, dis=True, mahal=d["mahal_i"], kal=d["duvar_kal"],
                            mal=d["duvar_mal"], raw=d, etiketsiz=True))
            continue
        if d["dis"]:   # pencere ile eşleşmeyen dış kanatlar da kapı-pencere kabul (C ZK)
            continue
        g = d["gen_tahmin"] or (90 if "90" in d["blok"] else 80)
        ops.append(dict(cins="kapı", tip="etiketsiz", gen=g / 100.0, yuk=2.20, dis=False, mahal=d["mahal_i"], kal=d["duvar_kal"],
                        mal=d["duvar_mal"], raw=d, etiketsiz=True))
    if kod == "B-blok-2-bodrum":
        ops.append(dict(cins="kapı", tip="GARAJ", gen=4.00, yuk=2.30, dis=True, mahal=[i for i, r in enumerate(v["rooms"]) if r["ad"] == "OTOPARK"],
                        kal=None, mal="betonarme", raw={}, etiketsiz=True))
    return ops

OPS = {kod: kat_openings(kod) for kod in KODS}
note("A blok 1. kat KAT BAHÇESİ batı kenarındaki etiketsiz çift kanatlı doğrama 375×280 kabul edildi (HACİM v03 kabulü; DXF'te etiket yok).", "doğrulanmalı")
note("C blok zemin kat ve A blok 1. kattaki etiketsiz dış kapı kanatları (TEK/ÇİFT KANAT, BALKON KAPI blokları) komşu pencere (P-10, P-18, P-19, P-22) boşluğunun içinde kapı-pencere kanadı sayıldı; ayrıca düşülmedi.")
note("Etiketsiz iç kapılar (D blok bodrum ve zemin kat mutfak–salon arası 'TEK KANAT' blokları, B zemin kat yatak–salon IFC_DOOR_90): genişlik yay yarıçapından ya da blok adından, yükseklik 220 cm kabul.", "doğrulanmalı")
note("B blok 2. bodrum garaj kapısı 400×230: DXF'te etiket yok, HACİM v02 ölçüsü (rampa duvarları arası).", "doğrulanmalı")

def area_on_floor(o, kod, cap):
    return o["gen"] * opening_h(o["raw"] if o["cins"] == "pencere" and not o.get("etiketsiz") else {"yuk": o["yuk"] * 100}, kod, cap)

# ================================================================== 1. DUVAR
T_DUVAR = []
for kod in KODS:
    v = R[kod]; k = KAT[kod]
    H = k["H_duvar"]
    # sınıf başına boşluk düşümü
    ded = collections.defaultdict(float); dedn = collections.defaultdict(int)
    for o in OPS[kod]:
        if o["mal"] != "kagir" or o["kal"] is None: continue
        if o["cins"] == "pencere" and not o.get("etiketsiz"):
            hh = opening_h(o["raw"], kod, H)
        else:
            hh = min(o["yuk"], H)
        tur = "dis" if o["dis"] else "ic"
        ded[(tur, o["kal"])] += o["gen"] * hh; dedn[(tur, o["kal"])] += 1
    # dış duvar 10 cm sınıfı = pencere/kapı-pencere kasa bölgesi (duvar yüzü ile cam arası ince şerit): baskın dış sınıfa katılır
    walls_ = [dict(w) for w in v["walls"]]
    dd_ = collections.defaultdict(float)
    for w in walls_:
        if w["tur"] == "dis" and w["kal"] > 10: dd_[w["kal"]] += w["uzunluk_m"]
    dom = max(dd_, key=dd_.get) if dd_ else 20
    for w in walls_:
        if w["tur"] == "dis" and w["kal"] == 10:
            w["uzunluk_m"] = w["plan_m2"] / (dom / 100.0) if False else w["uzunluk_m"]
            w["kal"] = dom; w["birlesen"] = True
    mrg = collections.OrderedDict()
    for w in walls_:
        key_ = (w["tur"], w["kal"])
        if key_ in mrg:
            mrg[key_]["uzunluk_m"] += w["uzunluk_m"]; mrg[key_]["plan_m2"] += w["plan_m2"]; mrg[key_]["birlesen"] = True
        else: mrg[key_] = w
    for key_ in list(ded):
        if key_[0] == "dis" and key_[1] == 10:
            ded[("dis", dom)] += ded.pop(key_); dedn[("dis", dom)] += dedn.pop(key_)
    for w in sorted(mrg.values(), key=lambda w: (w["tur"], w["kal"])):
        L = w["uzunluk_m"]
        if L < 0.30: continue
        brut = L * H
        d = ded.get((w["tur"], w["kal"]), 0.0)
        net = max(0.0, brut - d)
        T_DUVAR.append(dict(blok=v["blok"], kat=KATAD[v["kat"]], kod=kod, tur="Dış duvar" if w["tur"] == "dis" else "İç duvar",
                            malzeme="Kagir (malzeme belirsiz)", kal_cm=w["kal"], uzunluk=r2(L), H=H, brut=r2(brut), bosluk=r2(d),
                            bosluk_adet=dedn.get((w["tur"], w["kal"]), 0), net=r2(net), m3=r2(net * w["kal"] / 100.0),
                            plan_m2=r2(w["plan_m2"]),
                            yontem="2_IFC_Wall + 0_IFC_Area raster (1 cm): duvar izi = kapalı iz − mahaller − şaftlar − betonarme; kalınlık sınıfı morfolojik açma; L = iz alanı / kalınlık; H = %.2f − %.2f" % (k["duvar_ust"], k["duvar_alt"]),
                            notu=("kısa parça (<2 m): köşe/birleşim veya niş olabilir" if L < 2 else "") + (" ; 10 cm'lik doğrama kasa şeritleri bu sınıfa katıldı" if w.get("birlesen") else "")))
    # boşluğu olup sınıf satırı bulunmayan
    for (tur, kal), d in ded.items():
        if not any(w["tur"] == tur and w["kal"] == kal and w["uzunluk_m"] >= 0.30 for w in mrg.values()):
            T_DUVAR.append(dict(blok=v["blok"], kat=KATAD[v["kat"]], kod=kod, tur="Dış duvar" if tur == "dis" else "İç duvar",
                                malzeme="Kagir", kal_cm=kal, uzunluk=0, H=H, brut=0, bosluk=r2(d), bosluk_adet=dedn[(tur, kal)], net=0, m3=0, plan_m2=0,
                                yontem="boşluk bu sınıfa düştü ama sınıf izi yok", notu="doğrulanmalı"))
note("Duvar kalınlıkları plan çizgilerinden ölçüldü (sınıflar 10/15/20/25/30/40/50 cm; eşikler 12.5/17.5/22.5/27.5/35/45). Duvar malzemesi (gazbeton/tuğla/bims) DXF'te yazmıyor: 'kagir (malzeme belirsiz)'.", "doğrulanmalı")
note("Duvar brüt yüksekliği = taşıyıcı döşeme üstü → üst döşeme altı. Ara katlarda kat kotu −0.10 (kaplama+şap) → üst kat kotu −0.40 (kaplama 10 + döşeme 30); en alt katta radye üstü (kat −0.50, kesit 1-1) başlangıç; son katta çatı döşemesi altı (HACİM: çatı döşemesi üstü = saçak −0.13, kalınlık 30). Kiriş sarkması çizimde yok, düşülmedi.")
note("Boşluk düşümü: kagir duvardaki tüm pencere ve kapılar genişlik × min(yükseklik, duvar yüksekliği) olarak düşüldü; betonarme perdedeki boşluklar duvardan düşülmedi. Lento/söve ayrıca hesaplanmadı.")
note("Raster yöntemiyle duvar birleşim/köşe bölgeleri en yakın sınıfa katıldı; 25–50 cm'lik kısa parçalar çoğunlukla tesisat duvarı, köşe dolgusu veya niştir. Toplam duvar uzunluklarında ±%3 ölçüm toleransı beklenir.")

# ================================================================== 2. DUVAR YÜZEYLERİ (mahal bazında)
T_YUZEY = []; ROOMQ = {}
for kod in KODS:
    v = R[kod]; k = KAT[kod]
    for i, r in enumerate(v["rooms"]):
        g = grup(r["ad"], r["dis"])
        ht = k["net_h"]
        if r["dis"]:
            ROOMQ[(kod, i)] = dict(grup=g); continue
        per = r["cevre"]
        ops = [o for o in OPS[kod] if i in (o["mahal"] or [])]
        bos = 0.0; kapi_gen = 0.0
        for o in ops:
            if o["cins"] == "pencere" and not o.get("etiketsiz"):
                hh = opening_h(o["raw"], kod, ht)
            else:
                hh = min(o["yuk"], ht)
            bos += o["gen"] * hh
            if o["cins"] == "kapı" or (o["cins"] == "pencere" and (o["raw"].get("yuk") or 0) >= 270 or o.get("etiketsiz")):
                kapi_gen += o["gen"]
        brut = per * ht
        net = max(0.0, brut - bos)
        zem, duv, tav, sup, siva = MALZ[g]
        sup_m = max(0.0, per - kapi_gen) if sup else 0.0
        q = dict(blok=v["blok"], kat=KATAD[v["kat"]], kod=kod, mahal=r["ad"], grup=GRUPAD[g], cevre=r2(per), ht=ht, brut=r2(brut), bosluk=r2(bos),
                 bosluk_adet=len(ops), net=r2(net),
                 siva=r2(net if siva else 0), boya=r2(net if g not in ("islak",) and siva else (net if g in ("otopark", "teknik") else 0)),
                 seramik=r2(net if g == "islak" else 0), sup=r2(sup_m), alan=r2(r["alan_pol"]), zemin=zem, duvar=duv, tavan=tav)
        if g == "havuz": q["boya"] = 0.0
        T_YUZEY.append(q); ROOMQ[(kod, i)] = dict(q, g=g)
note("İç duvar yüzeyi = mahal poligonu (0_IFC_Area) çevresi × net tavan yüksekliği (DXF kesit: tavan kotu − kat kotu; 2.90 / 2.40 m) − mahale açılan pencere/kapı boşlukları. Kolon ve perde yüzleri çevreye dahildir.")
note("Islak hacimlerde duvar seramiği tavan yüksekliğine kadar (asma tavan altı); seramik altı sıva 'iç sıva' satırında ayrıca sayıldı, boya yok. Mutfak tezgah arası seramik hesaplanmadı (tezgah boyları çizimde ölçüsüz).")
note("Otopark ve teknik hacimlerde sıva yok, perde/blok üzeri boya kabul edildi. Havuz salonu duvar kaplaması belirsiz (boya yazılmadı).", "doğrulanmalı")

# ================================================================== 3. ZEMİN + 16. MAHAL LİSTESİ
T_ZEMIN = []; T_MAHAL = []
for kod in KODS:
    v = R[kod]; k = KAT[kod]
    for i, r in enumerate(v["rooms"]):
        g = grup(r["ad"], r["dis"])
        zem, duv, tav, sup, siva = MALZ[g]
        q = ROOMQ.get((kod, i), {})
        T_ZEMIN.append(dict(blok=v["blok"], kat=KATAD[v["kat"]], kod=kod, mahal=r["ad"], grup=GRUPAD[g], malzeme=zem, alan=r2(r["alan_pol"]),
                            alan_yazi=r["alan_yazi"], sup=q.get("sup", 0.0), kot=k["kot"],
                            notu=("kapalı alan dışı (" + r.get("dis_neden", "açık alan") + ")" if r["dis"] else "")))
        T_MAHAL.append(dict(blok=v["blok"], kat=KATAD[v["kat"]], kot="%.2f" % k["kot"], mahal=r["ad"], grup=GRUPAD[g], alan=r2(r["alan_pol"]),
                            alan_yazi=r["alan_yazi"], zemin=zem, duvar=duv, tavan=tav, sup=q.get("sup", 0.0) if not r["dis"] else 0.0,
                            ht=(k["net_h"] if not r["dis"] else None), dxf_not=", ".join(r["notlar"])))
note("Zemin malzemeleri ofis kütüphanesinden (ZM-01 seramik/granit ıslak ve servis, ZM-02 lamine parke yaşam/yatak). DXF mahal etiketlerinin tamamında 'DÖŞEME: SERAMİK / TAVAN: BOYA' yazıyor (şablon değeri olabilir); kesitlerde PARKE ve SERAMİK ayrı yazılı. Yaşam/yatak mahallerinde parke kabul edildi.", "doğrulanmalı")
note("SALON+MUTFAK mahalleri kuru grupta (HACİM/PAFTA kararı v02); MUTFAK mahalleri seramik kabul. M.K.A. kısaltmasının anlamı çizimde yok; tefrişi (yatak/dolap) nedeniyle kuru grupta.", "doğrulanmalı")
note("Süpürgelik = mahal çevresi − kapı genişlikleri − döşemeye inen doğrama genişlikleri; ıslak hacim (seramik duvar), otopark, teknik, havuz ve açık alanlarda yok. Merdiven kollarındaki eğik süpürgelik dahil değil.")

# ================================================================== 6. TAVAN
T_TAVAN = []
for kod in KODS:
    v = R[kod]
    for i, r in enumerate(v["rooms"]):
        if r["dis"]: continue
        g = grup(r["ad"], r["dis"])
        tip = ("Asma tavan (suya/neme dayanıklı alçı levha) + boya" if g in ISLAK_TAVAN else
               "Brüt beton üzeri boya" if g in ("otopark", "teknik") else "Alçı sıva + boya")
        T_TAVAN.append(dict(blok=v["blok"], kat=KATAD[v["kat"]], kod=kod, mahal=r["ad"], grup=GRUPAD[g], tip=tip, alan=r2(r["alan_pol"]),
                            tavan_kotu=KAT[kod]["tavan"]))
note("Tavan: ıslak hacim ve havuz salonu asma tavan (kullanıcı varsayımı); diğerleri DXF etiketine göre boya (alçı sıva + boya). HACİM döşeme paketinde tüm mahallerde 10 cm asma tavan boşluğu var; tüm katlarda asma tavan isteniyorsa bu sayfadaki tüm alanlar asma tavan olur.", "doğrulanmalı")

# ================================================================== KAPI ve PENCERE tabloları
T_KAPI = []; T_PENC = []
def rn(kod, L): return " / ".join(R[kod]["rooms"][i]["ad"] for i in (L or []))
for kod in KODS:
    v = R[kod]; k = KAT[kod]
    for d in v["doors"]:
        blk = d.get("blok") or ""
        kanat = 2 if ("CIFT" in blk or (d["gen"] or 0) >= 150) else 1
        tur = ("Sürgülü" if "SURGU" in blk else "Çift kanat" if kanat == 2 else "Tek kanat (menteşeli)")
        if (d["gen"] or 0) >= 300: tur = "Geniş açıklık (tip DXF'te yok)"
        T_KAPI.append(dict(blok=v["blok"], kat=KATAD[v["kat"]], kod=kod, etiket=d["kod"], gen=d["gen"], yuk=d["yuk"], kanat=kanat, tur=tur,
                           acilis=(d.get("el") or ("sürgü" if "SURGU" in blk else "belirsiz")), mahal=rn(kod, d["mahal_i"]),
                           konum="Dış" if d["dis"] else "İç", duvar=("%s cm kagir" % d["duvar_kal"] if d["duvar_kal"] else d["duvar_mal"]),
                           dxf_blok=blk, kaynak="KAPI POZU etiketi (Kxx, gen/yük) + 1_IFC_Door bloğu/yayı", notu=""))
    for o in OPS[kod]:
        if o["cins"] == "kapı" and o.get("etiketsiz"):
            T_KAPI.append(dict(blok=v["blok"], kat=KATAD[v["kat"]], kod=kod, etiket=o["tip"], gen=round(o["gen"] * 100), yuk=round(o["yuk"] * 100),
                               kanat=1, tur=("Garaj kapısı (seksiyonel varsayım)" if o["tip"] == "GARAJ" else "Tek kanat (etiketsiz)"),
                               acilis=(o["raw"].get("el") or "belirsiz"), mahal=rn(kod, o["mahal"]), konum="Dış" if o["dis"] else "İç",
                               duvar=o["mal"] if o["kal"] is None else "%s cm kagir" % o["kal"], dxf_blok=o["raw"].get("blok", ""),
                               kaynak=("HACİM v02 (DXF'te yok)" if o["tip"] == "GARAJ" else "1_IFC_Door bloğu, etiket yok"), notu="ölçü doğrulanmalı"))
note("Kapı açılış yönü kapı yayından okundu: 'DIN sağ/sol' = kapının açıldığı taraftan bakınca menteşe sağda/solda. Sürgülü kapılarda yay yok.")
note("A blokta ayrı dış kapı etiketi yok: bina girişi P-01 (900×630) cam cephesi içinde, 1. kat avlu kapıları P-10 ve etiketsiz avlu doğraması içinde kabul edildi. Dış kapı sınıfı: kapı kasası kapalı iz sınırına ≤ 25 cm.", "doğrulanmalı")
note("Kapı yükseklikleri etiketteki 220 cm; KAPI POZU etiketlerinde kanat/kasa tipi yazmıyor (yalnız Kxx ve gen/yük).", "doğrulanmalı")

HACIM_W = []
for b in BLOKLAR:
    for d in RAP["blocks"][b]["dograma"]:
        HACIM_W.append((b, d["kat"], d["tip"], d["genislik"], d["yukseklik"]))

def bolme(gen, yuk):
    n = max(1, round(gen / 150.0)); kay = 1 if yuk > 240 else 0
    if yuk > 500: kay = 2
    return n, kay
PROFIL = 0.07
for kod in KODS:
    v = R[kod]; k = KAT[kod]
    for o in OPS[kod]:
        if o["cins"] != "pencere": continue
        w = o["raw"]; tip = o["tip"]
        gen, yuk = round(o["gen"] * 100), round(o["yuk"] * 100)
        if tip == "P-01" and v["kat"] == "K1":
            continue   # ZK'da sayıldı
        top_kasa = k["net_h"] * 100 - 17
        par = max(0, round(top_kasa - yuk)) if yuk < top_kasa else 0
        if tip == "P-01": par = 0
        n, kay = bolme(gen, yuk)
        alan = gen * yuk / 1e4
        cer = (2 * (gen + yuk) + (n - 1) * yuk + kay * gen) / 100.0
        cam = max(0.0, alan - cer * PROFIL)
        dis = o["dis"]
        T_PENC.append(dict(blok=v["blok"], kat=KATAD[v["kat"]] + (" + 1. Kat (galeri)" if tip == "P-01" else ""), kod=kod, tip=tip,
                           gen=gen, yuk=yuk, parapet=par, adet=1, alan=r2(alan), cam=r2(cam), cerceve=r2(cer), bolme=n, kayit=kay,
                           denizlik=r2(gen / 100.0 if par > 0 and dis else 0), esik=r2(gen / 100.0 if par == 0 and dis else 0),
                           konum=("Dış" if dis else "İç (bölme camı)"), mahal=rn(kod, o["mahal"]),
                           duvar=("%s cm kagir" % o["kal"] if o["kal"] else o["mal"]),
                           kaynak=("0_IFC_Window_Text etiketi (TİP/GEN/YÜK)" if not o.get("etiketsiz") else "HACİM v03 kabulü (etiketsiz)"),
                           notu=("P-20: HACİM etiket 260, çizim 77 uyarısı" if tip == "P-20" else "A 1. kat avlu batı kenarı, etiketsiz, çift kanatlı (HACİM 375×280 kabulü)" if tip == "P-ETIKETSIZ" else "")))
note("Pencere ölçüleri DXF etiketlerinden (0_IFC_Window_Text: tip, genişlik, yükseklik); konsept v04'teki büyütülmüş pencereler kullanılmadı. Parapet = (net tavan yüksekliği − 17 cm) − pencere yüksekliği (HACİM görünüş kuralı); 280'lik doğramalar döşemeden başlar (parapet 0).")
note("Cam alanı yaklaşık: boşluk alanı − çerçeve uzunluğu × 7 cm görünür profil (bölme sayısı = genişlik/150 yuvarlak, yükseklik > 240 ise 1 yatay kayıt, P-01'de 2). Sistem detayına göre düzeltilmeli.", "doğrulanmalı")
note("Denizlik = parapeti olan dış pencerelerin genişliği (dış denizlik; iç denizlik aynı uzunluk); eşik = döşemeye inen dış doğramaların genişliği.")
note("P-09 (A blok bodrum, 175×220) dış cepheye 4 m uzak: sauna/koridor iç cam bölmesi kabul edildi (CAM KAPI bloğu ile).", "doğrulanmalı")
note("P-15 (B blok 1. bodrum, 240×90) bir ışıklığa (mahal poligonu olmayan kapalı alan) bakıyor; dış doğrama sayıldı.", "doğrulanmalı")

# ================================================================== 11. CEPHE + 12 (dış duvar kısmı)
# çatı planlarından (DXF 0_IFC_Elevation_*) ölçüler: bina izi, döşeme dış (saçak), parapet dış/iç, çatı örtüsü
CATI = {
    "A": dict(bina=(20.00, 8.50), doseme=(23.00, 10.50), parapet_dis=(23.20, 10.70), parapet_ic=(22.60, 10.10), ortu=(22.20, 9.70),
              sacak=181.15, parapet_kot=181.75, mahya=181.88, mahya_L=12.50, kaynak="A_CATI PLANI + A BLOK CATI KOTLARI"),
    "B": dict(bina=(20.00, 12.30), doseme=(23.00, 15.30), parapet_dis=(23.20, 15.50), parapet_ic=(22.60, 14.90), ortu=(22.20, 14.50),
              sacak=177.65, parapet_kot=178.63, mahya=179.17, mahya_L=7.70, kaynak="D_CATI PLANI (B blok) + B BLOK CATI KOTLARI"),
    "C": dict(bina=(18.00, 7.50), doseme=(21.00, 10.50), parapet_dis=(21.20, 10.70), parapet_ic=(20.60, 10.10), ortu=(20.20, 9.70),
              sacak=177.86, parapet_kot=178.46, mahya=178.75, mahya_L=10.50, kaynak="C_CATI PLANI + C BLOK CATI KOTLARI"),
    "D": dict(bina=(10.55, 12.30), doseme=(10.95, 12.70), parapet_dis=(10.95, 12.70), parapet_ic=(10.15, 11.90), ortu=(9.65, 11.40),
              sacak=174.25, parapet_kot=174.85, mahya=175.07, mahya_L=11.40 - 9.65, kaynak="E-F_CATI PLANI + D BLOK CATI KOTLARI"),
}
TOPKOD = {"A": "A-blok-1-kat", "B": "B-blok-zemin-kat", "C": "C-blok-zemin-kat", "D": "D-blok-1-kat"}
AVLU_A = 24.96
note("A blok çatı planında KAT BAHÇESİ üstünde boşluk çizili değil; proje kararı (açık avlu, v02) esas alındı: çatı örtüsü, çatı döşemesi ve yalıtımdan 24.96 m² (eğimli 25.2 m²) düşüldü. Avlu kapalıysa bu değerler eklenmeli.", "doğrulanmalı")

T_CEPHE = []
SOIL = {}   # kod -> (uzunluk, yükseklik)
for kod in KODS:
    v = R[kod]; k = KAT[kod]; b = v["blok"]
    perde_L = sum(val for c in v["cevre"] for key, val in c["dagilim"].items() if key.startswith("perde"))
    diger_L = sum(val for c in v["cevre"] for key, val in c["dagilim"].items() if key.startswith("diger"))
    tot = perde_L + diger_L
    if k["bodrum"]:
        if kod == "B-blok-1-bodrum":
            acik, toprak = 0.0, tot
            yon = "B 1. bodrum tamamen gömülü (OKUBENI: çevre tesviye 174.15); kagir dış duvarlar da toprak temaslı sayıldı"
        else:
            acik, toprak = diger_L, perde_L
            yon = "bodrum: dış çevrede betonarme perde = toprak temaslı, kagir/kolon = açık cephe"
    else:
        acik, toprak = tot, 0.0
        yon = "zemin üstü kat: tüm dış çevre cephe"
    hc = k["h_cephe"]
    ops = [o for o in OPS[kod] if o["dis"]]
    bos = 0.0
    for o in ops:
        if o["cins"] == "pencere" and not o.get("etiketsiz"):
            bos += o["gen"] * opening_h(o["raw"], kod, hc)
        else:
            bos += o["gen"] * min(o["yuk"], hc)
    brut = acik * hc
    T_CEPHE.append(dict(blok=b, kat=KATAD[v["kat"]], kod=kod, bolum="Dış duvar cephesi", uzunluk=r2(acik), h=hc, brut=r2(brut), bosluk=r2(bos),
                        net=r2(max(0, brut - bos)), malzeme="Malzeme belirsiz", yontem=yon + "; h = %s" % ("kat kotu → çatı döşemesi altı" if k["top"] else "kat yüksekliği")))
    SOIL[kod] = (toprak, k["kat_h"])
    if kod == "A-blok-1-bodrum":
        sub = perde_L
        T_CEPHE.append(dict(blok=b, kat=KATAD[v["kat"]], kod=kod, bolum="Subasman (perde üst bandı 172.95→174.15)", uzunluk=r2(sub), h=1.20,
                            brut=r2(sub * 1.20), bosluk=0, net=r2(sub * 1.20), malzeme="Malzeme belirsiz",
                            yontem="A tesviye 172.95, zemin kat 174.15: bodrum perdesinin üst 1.20 m'si açıkta (güney/doğu/batı)"))
        SOIL[kod] = (toprak, 172.95 - 170.15)
    if k["top"]:
        c = CATI[b]
        pd = 2 * (c["parapet_dis"][0] + c["parapet_dis"][1])
        alt = k["ust"] - ROOF_T
        hb = c["parapet_kot"] - alt
        T_CEPHE.append(dict(blok=b, kat="Çatı", kod=kod, bolum="Saçak alnı + parapet dış yüzü", uzunluk=r2(pd), h=r2(hb), brut=r2(pd * hb), bosluk=0,
                            net=r2(pd * hb), malzeme="Malzeme belirsiz", yontem="%s: parapet dış çevresi × (parapet kotu %.2f − çatı döşemesi altı %.2f)" % (c["kaynak"], c["parapet_kot"], alt)))
        pi = 2 * (c["parapet_ic"][0] + c["parapet_ic"][1])
        hpi = c["parapet_kot"] - (k["ust"])
        T_CEPHE.append(dict(blok=b, kat="Çatı", kod=kod, bolum="Parapet iç yüzü", uzunluk=r2(pi), h=r2(hpi), brut=r2(pi * hpi), bosluk=0,
                            net=r2(pi * hpi), malzeme="Malzeme belirsiz (dere arkası)", yontem="parapet iç çevresi × (parapet kotu − çatı döşemesi üstü %.2f)" % k["ust"]))
        sa = c["doseme"][0] * c["doseme"][1] - c["bina"][0] * c["bina"][1]
        if sa > 1:
            T_CEPHE.append(dict(blok=b, kat="Çatı", kod=kod, bolum="Saçak altı (döşeme konsolu alt yüzü)", uzunluk=None, h=None, brut=r2(sa), bosluk=0,
                                net=r2(sa), malzeme="Malzeme belirsiz", yontem="çatı döşemesi dış izi − bina izi (çatı planı)"))
    if v["parapet_m"] > 0.5:
        T_CEPHE.append(dict(blok=b, kat=KATAD[v["kat"]], kod=kod, bolum="Teras/balkon kenar bandı (20 cm, yükseklik çizimde yok)", uzunluk=r2(v["parapet_m"]), h=None,
                            brut=None, bosluk=None, net=None, malzeme="-", yontem="plan: teras mahali ile brüt çizgisi arası 20 cm bant (raster)"))
note("Cephe: zemin üstü katlarda tüm dış çevre (kapalı iz sınırı, avlu ve teras kenarları dahil) × kat yüksekliği; son katta çatı döşemesi altına kadar; çatı döşemesi alnı + parapet ayrı satır. Bodrumda dış çevredeki betonarme perde toprak temaslı, kagir kısım açık cephe kabul edildi (A, C, D bodrumların açık kuzey cepheleri ile tutarlı).")
note("DXF görünüşlerinde cephe malzemesi yazmıyor (yalnız 'ÇATI EĞİMİ %15', 'ŞEV TAŞI'): tüm cephe 'malzeme belirsiz'. Bilgi: ofis standardı CP-01 mantolama + dekoratif sıva; HACİM v04 konsept dağılımı taş/ahşap/bej sıva.", "doğrulanmalı")
note("Kısmen gömülü duvarlarda (eğimli arazi kenarı) toprak çizgisi ayrıca izlenmedi; bodrum yan cephelerinin açık/gömülü bölünmesi yaklaşık.", "doğrulanmalı")

# ================================================================== 7. BETONARME
T_BA = []
# kolon / perde
for kod in KODS:
    v = R[kod]; k = KAT[kod]; H = k["H_duvar"]
    for kind in ("Kolon", "Perde"):
        cs = [c for c in v["cols"] if c["perde"] == (kind == "Perde")]
        if not cs: continue
        A = sum(c["alan_m2"] for c in cs)
        dims = collections.Counter("%dx%d" % (c["t"], c["L"]) if kind == "Kolon" else "t≈%d cm" % (round(c["t_ort"] / 5) * 5) for c in cs)
        T_BA.append(dict(blok=v["blok"], kat=KATAD[v["kat"]], kod=kod, eleman=kind, adet=len(cs), plan_m2=r2(A), H=H, m3=r2(A * H),
                         uzunluk=r2(sum(c["alan_m2"] / (c["t_ort"] / 100.0) for c in cs)) if kind == "Perde" else None,
                         olcu=", ".join("%s ×%d" % (k_, n) for k_, n in sorted(dims.items())),
                         yontem="1_IFC_Concrete_Section kapalı poligonları; perde: uzun kenar ≥ 6 × kısa kenar veya L/U şekilli; perde kalınlığı ≈ 2A/çevre, uzunluk = A/t; H = duvar brüt yüksekliği"))
# döşemeler: blok yerel koordinatında kat izleri
def pl(kod, which="Fc_poly"):
    p = R[kod][which]
    return p.buffer(0)
def outs(kod):
    return unary_union([r["poly"] for r in R[kod]["rooms"] if r["dis"] and not r["ad"].upper().startswith("MERD")] or [Polygon()])
FOOT = {}
for b in BLOKLAR:
    ks = [c for c in KODS if R[c]["blok"] == b]
    ks.sort(key=lambda c: KATSIRA[R[c]["kat"]])
    allfoot = unary_union([pl(c, "F_poly") for c in ks]).buffer(0)
    FOOT[b] = allfoot
    rad = allfoot.area / 1e4
    T_BA.append(dict(blok=b, kat="Temel", kod="", eleman="Radye temel", adet=None, plan_m2=r2(rad), H=RADYE[b], m3=r2(rad * RADYE[b]),
                     uzunluk=None, olcu="kalınlık %.2f m" % RADYE[b],
                     yontem="tüm katların yapı izlerinin birleşimi (temel konsolu yok kabul); kalınlık: %s blok 1-1 kesiti kotları" % b))
    T_BA.append(dict(blok=b, kat="Temel", kod="", eleman="Grobeton (10 cm)", adet=None, plan_m2=r2(rad), H=0.10, m3=r2(rad * 0.10), uzunluk=None,
                     olcu="", yontem="radye alanı × 0.10 (varsayım)"))
    for j, c in enumerate(ks):
        k = KAT[c]
        if k["top"]:
            cc = CATI[b]
            a = cc["doseme"][0] * cc["doseme"][1] - (AVLU_A if b == "A" else 0)
            T_BA.append(dict(blok=b, kat="Çatı döşemesi", kod=c, eleman="Döşeme (çatı)", adet=None, plan_m2=r2(a), H=ROOF_T, m3=r2(a * ROOF_T),
                             uzunluk=None, olcu="", yontem="çatı planı döşeme dış izi %.2f×%.2f%s" % (cc["doseme"][0], cc["doseme"][1], " − avlu 24.96" if b == "A" else "")))
        else:
            up = ks[j + 1]
            u = unary_union([pl(c, "Fc_poly"), pl(up, "F_poly")]).buffer(0)
            a = u.area / 1e4
            T_BA.append(dict(blok=b, kat=KATAD[R[c]["kat"]] + " üstü", kod=c, eleman="Döşeme (ara kat)", adet=None, plan_m2=r2(a), H=DOS, m3=r2(a * DOS),
                             uzunluk=None, olcu="", yontem="bu katın kapalı izi ∪ üst katın tüm izi (teras/avlu dahil), blok yerel koordinatı"))
note("Betonarme döşeme kalınlığı 30 cm (HACİM döşeme paketi: kaplama 10 + döşeme 30 + asma tavan boşluğu 10 + tavan 10), çatı döşemesi 30 cm. Kiriş ve kolon başlıkları çizimde yok. Statik proje ile doğrulanmalı.", "doğrulanmalı")
note("Radye kalınlıkları kesit 1-1 kotlarından: A, C, D 50 cm (kat −0.50 / −1.00), B 100 cm (−7.50 / −8.50). Radye alanı = yapı izi (taşma payı yok). A bodrumdaki havuz teknesi (kesitte −4.30/−4.80 kotları) ayrıca hesaplanmadı.", "doğrulanmalı")
note("Merdiven betonarmesi ve asansör/ışıklık perdeleri (mahal poligonu olmayan kapalı alanlar) hesaplanmadı.")

# ================================================================== 8. ÇATI
T_CATI = []
for b in BLOKLAR:
    c = CATI[b]; a, bb_ = c["ortu"]
    run = min(a, bb_) / 2.0
    rise = c["mahya"] - c["sacak"]
    s = rise / run
    k_ = math.sqrt(1 + s * s)
    plan = a * bb_ - (AVLU_A if b == "A" else 0)
    hip = 4 * math.sqrt(2 * run * run + rise * rise)
    T_CATI += [
        dict(blok=b, kalem="Çatı örtüsü (METAL ÇATI) – eğik alan", birim="m²", miktar=r2(plan * k_),
             yontem="örtü izdüşümü %.2f×%.2f%s = %.2f m² × √(1+%.3f²) = ×%.4f" % (a, bb_, " − avlu 24.96" if b == "A" else "", plan, s, k_), notu="eğim kotlardan %%%.1f (DXF yazısı %%15)" % (s * 100)),
        dict(blok=b, kalem="Çatı örtüsü – plan izdüşümü", birim="m²", miktar=r2(plan), yontem=c["kaynak"], notu=""),
        dict(blok=b, kalem="Saçak/dere hattı (örtü çevresi)", birim="m", miktar=r2(2 * (a + bb_)), yontem="2×(%.2f+%.2f)" % (a, bb_), notu=""),
        dict(blok=b, kalem="Galvanizli sac dere (parapet arkası)", birim="m", miktar=r2(2 * (a + bb_)), yontem="DXF yazısı 'GALVANİZLİ SAC DERE'; örtü çevresi", notu="iç oluk"),
        dict(blok=b, kalem="Mahya", birim="m", miktar=r2(abs(a - bb_)), yontem="çatı planı 0_IFC_Elevation_1 mahya çizgisi (|a−b|)", notu=""),
        dict(blok=b, kalem="Kırma (köşe mahyası)", birim="m", miktar=r2(hip), yontem="4 × √(2·%.3f² + %.2f²)" % (run, rise), notu=""),
        dict(blok=b, kalem="Parapet (çatı) uzunluğu", birim="m", miktar=r2(2 * ((c["parapet_dis"][0] + c["parapet_ic"][0]) / 2 + (c["parapet_dis"][1] + c["parapet_ic"][1]) / 2)),
             yontem="parapet eksen çevresi; parapet kotu %.2f" % c["parapet_kot"], notu="parapet üstü harpuşta = aynı uzunluk"),
        dict(blok=b, kalem="Yağmur iniş borusu", birim="adet", miktar=4 + 2 * (1 if max(a, bb_) > 15 else 0),
             yontem="öneri: her köşe 1 + 15 m'yi aşan uzun kenarlara 1 ara iniş", notu="VARSAYIM – çizimde iniş yok; TS EN 12056-3 hesabı ile doğrulanmalı"),
    ]
    if b == "A":
        T_CATI.append(dict(blok=b, kalem="Avlu çevresi iç saçak/dere (açık avlu kabulü)", birim="m", miktar=r2(2 * (4.80 + 4.40)),
                           yontem="HACİM v02 avlu boşluğu 4.80×4.40", notu="avlu kapalıysa yok"))
    if b == "D":
        T_CATI.append(dict(blok=b, kalem="Teras pergolası (DXF E-F_CATI PLANI: 22 lata 6.95 m)", birim="m", miktar=r2(22 * 6.95),
                           yontem="0_IFC_Elevation_5 5 cm'lik şeritler", notu="malzeme belirsiz"))
note("Çatı eğimleri DXF kotlarından (saçak/mahya): A %15.1, B %21.0, C %18.4, D %17.0; DXF'teki '%15' yazıları kotlarla uyuşmuyor (B kararı: kotlar esas).", "doğrulanmalı")
note("Çatılar DXF'te parapet içinde gizli dereli metal kırma çatı: saçak/oluk = örtü çevresindeki galvanizli sac dere. Yağmur iniş adedi çizimde yok: öneri varsayımı.", "doğrulanmalı")

# ================================================================== 9. MERDİVEN + 10. KORKULUK
T_MERD = []; seen = set()
for kod in KODS:
    v = R[kod]; k = KAT[kod]
    for s in v["stairs"]:
        key = (v["blok"], s["riht"], s["adet"])
        if key in seen: continue
        seen.add(key)
        w = (s["kol_gen"] or 120) / 100.0
        kol = 1
        for kk in RAP["blocks"][v["blok"]]["kat"]:
            if kk.get("merdiven") and kk["merdiven"]["adet"] == s["adet"]: pass
        # merdivenin alt katı: kat yüksekliği = rıht × adet
        hh = s["riht"] * s["adet"] / 100.0
        alt = [c for c in KODS if R[c]["blok"] == v["blok"] and abs(KAT[c]["kat_h"] - hh) < 0.05]
        alt = alt[0] if alt else kod
        hm = [kk["merdiven"] for kk in RAP["blocks"][v["blok"]]["kat"] if kk["kat"] == R[alt]["kat"] and kk.get("merdiven")]
        kol = hm[0]["kol"] if hm else 1
        nb = s["adet"] - kol
        mah = [r for r in R[alt]["rooms"] if r["ad"].upper().startswith("MERD") and not r["dis"]]
        mah_a = mah[0]["alan_pol"] if mah else None
        basamak_a = nb * s["basamak"] / 100.0 * w
        riht_a = s["adet"] * s["riht"] / 100.0 * w
        # korkuluk: merdiven mahali içindeki 2_IFC_Handrail çizgileri (iki katın planı)
        T_MERD.append(dict(blok=v["blok"], kat="%s → %s" % (KATAD[R[alt]["kat"]], "üst kat"), yazi=s["yazi"], riht=s["riht"], adet=s["adet"],
                           basamak_cm=s["basamak"], kol=kol, basamak_adet=nb, kol_gen=s["kol_gen"], h_toplam=r2(hh),
                           basamak_m2=r2(basamak_a), riht_m2=r2(riht_a), sahanlik_m2=r2(max(0, (mah_a or 0) - basamak_a)) if mah_a else None,
                           kaplama_m2=r2(basamak_a + riht_a + max(0, (mah_a or 0) - basamak_a)) if mah_a else r2(basamak_a + riht_a),
                           yontem="0_IFC_Stair_Text 'M: rıht×adet/basamak'; kol genişliği = 1_IFC_Stair basamak çizgisi boyu (en sık); sahanlık = alt kat MERDİVEN mahali − basamak izdüşümü",
                           notu=("kol genişliği bulunamadı, 120 kabul" if not s["kol_gen"] else "")))
note("Merdiven kaplaması = basamak (yatay) + rıht + sahanlık; sahanlık alt kattaki MERDİVEN mahal alanından basamak izdüşümü düşülerek bulundu (üst kattaki merdiven boşluğu sayılmadı). Kol sayısı HACİM raporundan. Malzeme belirsiz (DXF: SERAMİK).", "doğrulanmalı")
note("D blokta bina içi merdiven yok (bağımsız daireler); A zemin kat giriş merdiveni (dış, 3.96 m²) peyzaj/dış merdiven olarak zemin tablosunda.")

T_KORK = []
for kod in KODS:
    v = R[kod]
    fc = v["Fc_poly"].buffer(0)
    for r in v["rooms"]:
        if not r["dis"] or r["ad"].upper().startswith("MERD"): continue
        bnd = r["poly"].exterior
        free = bnd.difference(fc.buffer(35)).length / 100.0
        T_KORK.append(dict(blok=v["blok"], kat=KATAD[v["kat"]], kod=kod, yer=r["ad"] + " (%.1f m²)" % r["alan_pol"], tur="Teras/balkon korkuluğu (110 cm cam panel – proje kararı)",
                           uzunluk=r2(free), yontem="mahal poligonu çevresi − kapalı izin 35 cm yakınındaki kenarlar", notu=("avlu: bina duvarları ile çevrili" if free < 1 else "")))
    # merdiven korkulukları: merdiven mahali içindeki/yakınındaki 2_IFC_Handrail
    stairs_p = [r["poly"].buffer(30) for r in v["rooms"] if r["ad"].upper().startswith("MERD") and not r["dis"]]
    if stairs_p:
        sp = unary_union(stairs_p)
        L = sum(h["geom"].intersection(sp).length for h in v["handrail"]) / 100.0
        if L > 0.5:
            T_KORK.append(dict(blok=v["blok"], kat=KATAD[v["kat"]], kod=kod, yer="Merdiven evi", tur="Merdiven korkuluğu/küpeşte (plan)",
                               uzunluk=r2(L / 2.0), yontem="2_IFC_Handrail çizgileri (merdiven mahali +30 cm) toplam boy / 2 (çift çizgi)",
                               notu="plan uzunluğu; kol boyunca eğik boy ≈ ×1.13"))
note("Teras korkuluğu = teras/balkon poligonunun bina dışında kalan serbest kenarları (110 cm cam panel, proje kararı 5). A zemin kat terasının doğu/batı kenarları tesviye 172.95'e 1.20 m kot farkıyla bakıyor; korkuluğa dahil.")
note("Merdiven korkuluğu plan çizgilerinden (çift çizgi varsayımıyla /2); eğik boy için ×1.13 (rıht 16.66 / basamak 30).", "doğrulanmalı")

# ================================================================== 12. YALITIM
T_YAL = []
for b in BLOKLAR:
    cep = sum(x["net"] for x in T_CEPHE if x["blok"] == b and x["bolum"] in ("Dış duvar cephesi", "Subasman (perde üst bandı 172.95→174.15)") and x["net"])
    T_YAL.append(dict(blok=b, kalem="Dış duvar ısı yalıtımı (mantolama, CP-01)", birim="m²", miktar=r2(cep), yontem="11_CEPHE: dış duvar cephesi + subasman, net (boşluklar düşülmüş)",
                      notu="kalınlık TS 825'e göre (İstanbul 2. bölge) – doğrulanmalı"))
    par = sum(x["net"] for x in T_CEPHE if x["blok"] == b and x["bolum"].startswith(("Saçak alnı", "Parapet iç")) and x["net"])
    T_YAL.append(dict(blok=b, kalem="Saçak alnı + parapet yalıtımı (ısı köprüsü)", birim="m²", miktar=r2(par), yontem="11_CEPHE çatı satırları", notu=""))
    soil = sum(SOIL[c][0] * SOIL[c][1] for c in KODS if R[c]["blok"] == b)
    radk = FOOT[b].length / 100.0
    T_YAL.append(dict(blok=b, kalem="Toprak temaslı perde su yalıtımı + koruma (bodrum)", birim="m²", miktar=r2(soil),
                      yontem="dış çevredeki perde boyu × gömülü yükseklik (" + ", ".join("%s %.1f m × %.2f" % (KATAD[R[c]['kat']], SOIL[c][0], SOIL[c][1]) for c in KODS if R[c]["blok"] == b and SOIL[c][0] > 0) + ")", notu="ısıtılan hacimlerde XPS ısı yalıtımı aynı alan"))
    T_YAL.append(dict(blok=b, kalem="Radye yan yüzü su yalıtımı", birim="m²", miktar=r2(radk * RADYE[b]), yontem="yapı izi çevresi %.1f m × radye %.2f" % (radk, RADYE[b]), notu=""))
    T_YAL.append(dict(blok=b, kalem="Radye altı su yalıtımı", birim="m²", miktar=r2(FOOT[b].area / 1e4), yontem="radye alanı (07_BETONARME)", notu="bindirme payı hariç"))
    T_YAL.append(dict(blok=b, kalem="Zemine oturan döşeme ısı yalıtımı (XPS)", birim="m²", miktar=r2(FOOT[b].area / 1e4), yontem="radye alanı", notu="otopark/teknik hacim ısıtılmıyorsa düşülmeli"))
    c = CATI[b]; top = TOPKOD[b]
    a_heat = R[top]["Fc_m2"]
    T_YAL.append(dict(blok=b, kalem="Çatı döşemesi üstü ısı yalıtımı", birim="m²", miktar=r2(a_heat), yontem="son kat kapalı izi (Fc)", notu=""))
    cat_e = [x for x in T_CATI if x["blok"] == b and x["kalem"].startswith("Çatı örtüsü (METAL")][0]["miktar"]
    T_YAL.append(dict(blok=b, kalem="Çatı örtüsü altı su yalıtımı (membran/su yalıtım örtüsü)", birim="m²", miktar=cat_e, yontem="08_CATI eğik alan", notu=""))
    # teras / bahçe altı döşemeler
    ks = sorted([cc for cc in KODS if R[cc]["blok"] == b], key=lambda cc: KATSIRA[R[cc]["kat"]])
    ter = 0.0; det = []
    for j, cc in enumerate(ks):
        for r in R[cc]["rooms"]:
            if r["dis"] and not r["ad"].upper().startswith("MERD") and j > 0:
                ter += r["alan_pol"]; det.append("%s %s %.1f" % (KATAD[R[cc]["kat"]], r["ad"], r["alan_pol"]))
    T_YAL.append(dict(blok=b, kalem="Teras/balkon su + ısı yalıtımı", birim="m²", miktar=r2(ter), yontem="kapalı hacim üstündeki teras/balkon/avlu mahalleri: " + "; ".join(det), notu=""))
    gom = 0.0; det = []
    for j, cc in enumerate(ks[:-1]):
        up = ks[j + 1]
        rest = R[cc]["Fc_poly"].buffer(0).difference(R[up]["F_poly"].buffer(10))
        a_ = rest.area / 1e4
        if a_ > 1:
            gom += a_; det.append("%s üstü %.1f" % (KATAD[R[cc]["kat"]], a_))
    T_YAL.append(dict(blok=b, kalem="Toprak altı/bahçe altı döşeme su yalıtımı (üstü açık bodrum döşemesi)", birim="m²", miktar=r2(gom),
                      yontem="alt kat kapalı izi − üst kat izi: " + ("; ".join(det) if det else "yok"), notu="üstü peyzaj (bahçe/sert zemin) – doğrulanmalı"))
    isl = sum(x["alan"] for x in T_ZEMIN if x["blok"] == b and x["grup"] == GRUPAD["islak"])
    islp = sum(x["cevre"] for x in T_YUZEY if x["blok"] == b and x["grup"] == GRUPAD["islak"])
    T_YAL.append(dict(blok=b, kalem="Islak hacim su yalıtımı (zemin + 30 cm duvar dönüşü)", birim="m²", miktar=r2(isl + islp * 0.30),
                      yontem="ıslak mahal zemin %.2f + çevre %.2f × 0.30" % (isl, islp), notu="duş bölgesinde 200 cm duvar yalıtımı ayrıca (duş yerleri planlarda var)"))
note("Yalıtım alanları diğer kalemlerden türetildi; kalınlık/malzeme (TS 825, İstanbul 2. derece gün bölgesi) seçilmedi. Bindirme ve fire payı yok.", "doğrulanmalı")

# ================================================================== 13. ARMATÜR
T_ARM = []
def arm_tur(f):
    t = f["tur"]; m = f["mahal"] or ""; g = grup(m, False)
    if t.startswith("Lavabo/eviye"):
        return "Mutfak eviyesi" if g in ("mutfak", "kuru") and "BANYO" not in m and "WC" not in m else "Lavabo"
    if t == "Tezgah":
        return "Lavabo tezgahı" if g == "islak" and "SAUNA" not in m else ("Sauna oturma tezgahı" if "SAUNA" in m else "Mutfak tezgahı")
    if t == "Tezgah (L)":
        return "Mutfak tezgahı (L)" if g != "islak" else "Tezgah (soyunma)"
    if t.startswith("Tanımsız") and "A$C6efea695" in t: return "Tanımsız (hamam içi, 2.3×2.3 m blok – kurna/göbek taşı olabilir)"
    if t.startswith("Tanımsız") and "A$C0D101AED" in t: return "Tanımsız (55×22 cm, ıslak hacim – batarya/havlupan olabilir)"
    return t
for kod in KODS:
    v = R[kod]
    c = collections.Counter((arm_tur(f), f["mahal"]) for f in v["fix"])
    for (t, m), n in sorted(c.items()):
        if t.startswith("Tanımsız (A$C"): continue
        if t.startswith("Tanımsız blok"):
            t = "Tanımsız blok (mutfak cihazı olabilir)"
        T_ARM.append(dict(blok=v["blok"], kat=KATAD[v["kat"]], kod=kod, tur=t, mahal=m, adet=n,
                          kaynak="6_IFC_Furniture_WC / _Wetspace blok referansları (etkin blok adı)"))
note("Armatürler plan bloklarından sayıldı (IFC_KLOZET, IFC_VITRA_DOLAPLI LAVABO, IFC_ SINK, IFC_DUS (KAPILI), IFC_DUS KOSE, IFC_LINEER SUZGEC, IFC_MUTFAK EVYE2, IFC_EVYE_1.5, IFC_OCAK, IFC_CAMASIR MAKINESI). Küvet ve pisuvar yok. 'IFC_ SINK' bloğu ıslak hacimde lavabo, mutfakta eviye sayıldı.", "doğrulanmalı")

# ================================================================== 14. HAFRİYAT
T_HAF = []
KOSE = {"A": ("A-blok-zemin-kat", "A KOSE KOTLARI"), "B": ("B-blok-zemin-kat", "B KOSE KOTLARI"),
        "C": ("C-blok-zemin-kat", "C KOSE KOTLARI"), "D": ("D-blok-zemin-kat", "D KOSE KOTLARI")}
for b in BLOKLAR:
    zk, nm = KOSE[b]
    anc = R[zk]["anc"]
    T = [e for e in G if e["t"] == "T" and e["blk"] and e["blk"][0] == nm and re.fullmatch(r"\d{3}\.\d{2}", e["txt"].strip())]
    pts = [(e["x"] - anc[0], e["y"] - anc[1], float(e["txt"])) for e in T]
    A_ = np.array([[p[0], p[1], 1] for p in pts]); z = np.array([p[2] for p in pts])
    coef, *_ = np.linalg.lstsq(A_, z, rcond=None)
    ks = sorted([cc for cc in KODS if R[cc]["blok"] == b], key=lambda cc: KATSIRA[R[cc]["kat"]])
    bod = [cc for cc in ks if R[cc]["kat"].startswith("B")]
    kaz = FOOT[b].buffer(100)   # 1.0 m çalışma payı
    # ızgara 25 cm
    x0, y0, x1, y1 = kaz.bounds
    st = 25.0
    vol = 0.0; area_c = 0.0; geri = 0.0; dmax = 0
    for x in np.arange(x0 + st / 2, x1, st):
        for y in np.arange(y0 + st / 2, y1, st):
            p = Point(x, y)
            if not kaz.contains(p): continue
            # bu noktanın altındaki en alt kat
            lo = None
            for cc in ks:
                if R[cc]["F_poly"].buffer(0).contains(p) or R[cc]["F_poly"].buffer(100).contains(p):
                    lo = cc; break
            if lo is None: lo = ks[0]
            base = KAT[lo]["kot"] - RADYE_UST - RADYE[b] - GROBLOK if KAT[lo]["en_alt"] else KAT[lo]["kot"] - RADYE_UST - 0.50 - GROBLOK
            ng = coef[0] * x + coef[1] * y + coef[2]
            d = ng - base
            if d > 0:
                vol += d * (st / 100) ** 2; area_c += (st / 100) ** 2; dmax = max(dmax, d)
                if not FOOT[b].contains(p):
                    geri += d * (st / 100) ** 2
    T_HAF.append(dict(blok=b, kalem="Temel kazısı (yaklaşık)", birim="m³", miktar=r2(vol),
                      yontem="kazı alanı = yapı izi + 1.0 m çalışma payı (%.1f m²); doğal zemin = köşe kotlarından düzlem (%s: %s); taban = radye altı − 0.25 (grobeton+blokaj); en derin %.2f m" % (
                          kaz.area / 1e4, nm, ", ".join(e["txt"] for e in T), dmax), notu="YAKLAŞIK"))
    T_HAF.append(dict(blok=b, kalem="Geri dolgu – çalışma boşluğu (yaklaşık)", birim="m³", miktar=r2(geri),
                      yontem="kazı alanının yapı izi dışındaki 1.0 m'lik şeridi, doğal zemin kotuna kadar", notu="YAKLAŞIK; tesviye kotuna göre ± değişir"))
    T_HAF.append(dict(blok=b, kalem="Blokaj (15 cm)", birim="m³", miktar=r2(FOOT[b].area / 1e4 * 0.15), yontem="radye alanı × 0.15 (ATIKSU DETAY değeri, varsayım)", notu=""))
note("Hafriyat yaklaşıktır: doğal zemin blok köşe kotlarından (vaziyet 'KOSE KOTLARI') düzlem kabulü; şev, iksa ve arazi genel tesviyesi (yarma/dolgu, B otopark rampa yarması) hesaplanmadı. HACİM arazi noktaları doğal/proje kotlarını karışık içerdiği için kullanılmadı.", "doğrulanmalı")

# ================================================================== 15. PEYZAJ (vaziyet planı)
T_PEY = []
VZ = [e for e in G if e["top"] == 367]   # A sırası VAZIYET PLANI (ölçek 0.25)
S = 4.0
par = Polygon([p for e in VZ if e["lay"] == "0_IFC_Parsel Sınırı" and e["t"] == "P" for p in e["pts"]])
lines = []
for e in VZ:
    if e["t"] in "LP" and e["lay"] not in ("0_IFC_Notation_Level_200", "6_IFC_Car", "0_IFC_Text_Explanation_50", "0_IFC_Text_Explanation_100",
                                           "0_IFC_Notation_Section_100", "0_IFC_Notation_Section_50", "0_IFC_Room_Text(No)_50"):
        pts = e["pts"] + ([e["pts"][0]] if e["t"] == "P" else [])
        if len(pts) > 1: lines.append(LineString(pts))
    if e["t"] == "H":
        for l in e["loops"]: lines.append(LineString(l + [l[0]]))
lines.append(par.exterior)
faces = [f for f in polygonize(unary_union(lines)) if f.representative_point().within(par)]
TX = [e for e in VZ if e["t"] == "T" and e["txt"].strip()]
cls_area = collections.Counter(); walls = []
for f in faces:
    a = f.area * S * S / 1e4
    th = 2 * f.area / f.length * S  # cm
    txt = " | ".join(e["txt"].strip() for e in TX if f.contains(Point(e["x"], e["y"])))
    u = txt.upper()
    if "BLOK" in u and "KAT" in u: c = "Bina izi (vaziyet)"
    elif th < 10 and f.length * S / 2 > 150: c = "Duvar hattı (çift çizgi şeridi)"
    elif "YAYA YOLU" in u or "GİRİŞİ" in u or "M:" in txt: c = "Sert zemin – yaya yolu/giriş/merdiven"
    elif "H:" in txt or "ARAÇ" in u: c = "Sert zemin – araç yolu/rampa"
    elif "DOĞAL EĞİM" in u: c = "Yeşil – doğal eğim (şev)"
    elif "TESVİYE" in u or "TESVIYE" in u: c = "Yeşil/bahçe – tesviye alanı (malzeme belirsiz)"
    elif th < 70: c = "Sınıflanamayan dar parça (basamak/bordür)"
    else: c = "Sınıflanamayan alan (etiketsiz)"
    cls_area[c] += a
    if c == "Duvar hattı (çift çizgi şeridi)":
        walls.append(f)
MSL = [e for e in TX if e["txt"].strip().startswith("M:")]
walls = [f for f in walls if min([f.representative_point().distance(Point(e["x"], e["y"])) for e in MSL] + [1e9]) * S / 100 > 6]
for c, a in sorted(cls_area.items(), key=lambda x: -x[1]):
    T_PEY.append(dict(kalem=c, birim="m²", miktar=r2(a), yontem="vaziyet planı (VAZIYET PLANI, ölçek ×4) çizgilerinin parsel içinde poligonlanması; sınıf = poligondaki yazı",
                      notu="YAKLAŞIK – vaziyette malzeme taraması yok"))
T_PEY.append(dict(kalem="Parsel net alanı (kontrol)", birim="m²", miktar=r2(par.area * S * S / 1e4), yontem="0_IFC_Parsel Sınırı", notu="DXF: 4799.86"))
# istinat/set/bahçe duvarları: etiket → en yakın dar poligon(lar)
WL = [e for e in TX if re.search(r"İstinat Duvarı|Set Duvarı|Bahçe Duvarı|ŞEV TAŞI", e["txt"])]
KOT = [(e["x"], e["y"], float(e["txt"])) for e in TX if re.fullmatch(r"1[5-9]\d\.\d{2}", e["txt"].strip())]
wtype = collections.defaultdict(list)
for f in walls:
    rp = f.representative_point()
    lab = min(WL, key=lambda e: rp.distance(Point(e["x"], e["y"]))) if WL else None
    dlab = rp.distance(Point(lab["x"], lab["y"])) * S / 100 if lab else 1e9
    t = lab["txt"].strip() if lab and dlab < 6 else "Duvar (etiketsiz)"
    L = f.length * S / 2 / 100.0
    # yükseklik tahmini: duvarın iki yanında 4 m içindeki en yakın kot yazıları farkı
    mrr = f.minimum_rotated_rectangle; cc = list(mrr.exterior.coords)
    e1 = (cc[1][0] - cc[0][0], cc[1][1] - cc[0][1]); e2 = (cc[2][0] - cc[1][0], cc[2][1] - cc[1][1])
    ax = e1 if math.hypot(*e1) >= math.hypot(*e2) else e2
    nrm = (-ax[1], ax[0]); nl = math.hypot(*nrm) or 1; nrm = (nrm[0] / nl, nrm[1] / nl)
    side = {1: [], -1: []}
    for (x, y, z) in KOT:
        dx, dy = x - rp.x, y - rp.y
        dist = math.hypot(dx, dy) * S / 100
        if dist < 8:
            sgn = 1 if dx * nrm[0] + dy * nrm[1] > 0 else -1
            side[sgn].append((dist, z))
    h = None
    if side[1] and side[-1]:
        h = abs(min(side[1])[1] - min(side[-1])[1])
    wtype[t].append((L, h))
for t, lst in sorted(wtype.items()):
    L = sum(x[0] for x in lst)
    hs = [x for x in lst if x[1] is not None and x[1] > 0.05]
    hm = (sum(x[0] * x[1] for x in hs) / sum(x[0] for x in hs)) if hs else None
    T_PEY.append(dict(kalem="%s – uzunluk" % t, birim="m", miktar=r2(L), yontem="vaziyette duvar hattı çift çizgi şeritleri (<10 cm) yarı çevresi, merdiven yazılarına 6 m'den uzak; tür = 6 m içindeki en yakın etiket", notu="YAKLAŞIK – düşük güven, doğrulanmalı"))
    if hm:
        T_PEY.append(dict(kalem="%s – ort. görünen yükseklik (kot farkı)" % t, birim="m", miktar=r2(hm), yontem="duvarın iki yanında 8 m içindeki en yakın kot yazılarının farkı (uzunlukla ağırlıklı, %d/%d parça)" % (len(hs), len(lst)), notu="YAKLAŞIK, temel hariç – doğrulanmalı"))
        T_PEY.append(dict(kalem="%s – yüzey (uzunluk × ort. yükseklik)" % t, birim="m²", miktar=r2(L * hm), yontem="tek yüz", notu="YAKLAŞIK"))
# taralı (ANSI31) duvar kesitleri: kesin ölçü
hh = []
for e in VZ:
    if e["t"] == "H" and e["lay"] == "0_IFC_Elevation_5" and e.get("pat") == "ANSI31":
        for l in e["loops"]:
            p = Polygon(l).buffer(0)
            if p.area > 0: hh.append(p)
if hh:
    Lh = sum(p.length * S / 2 / 100 for p in hh); Ah = sum(p.area * S * S / 1e4 for p in hh)
    T_PEY.append(dict(kalem="Taralı istinat/set duvarı kesitleri (vaziyet, ~30 cm) – uzunluk", birim="m", miktar=r2(Lh),
                      yontem="0_IFC_Elevation_5 ANSI31 taramaları: %d parça, plan alanı %.1f m², ort. kalınlık %.0f cm" % (len(hh), Ah, Ah / Lh * 100), notu="çizimden ölçüldü; hangi etiketli duvarlarla örtüştüğü doğrulanmalı"))
# peyzaj merdivenleri
ms = [e["txt"].strip() for e in TX if e["txt"].strip().startswith("M:")]
tot_r = 0
for m_ in ms:
    mm = re.match(r"M:\s*([\d.]+)\s*x\s*(\d+)\s*/\s*([\d.]+)", m_)
    if mm: tot_r += int(mm.group(2))
T_PEY.append(dict(kalem="Peyzaj merdivenleri (%d adet)" % len(ms), birim="rıht", miktar=tot_r, yontem="vaziyet 'M: rıht×adet/basamak' yazıları: " + "; ".join(ms), notu="engelli platformu notu var"))
hr = [e for e in VZ if e["lay"] == "2_IFC_Handrail" and e["t"] in "LP"]
hL = sum(LineString(e["pts"] + ([e["pts"][0]] if e["t"] == "P" else [])).length for e in hr) * S / 100 / 2
T_PEY.append(dict(kalem="Peyzaj korkuluğu (duvar üstü)", birim="m", miktar=r2(hL), yontem="vaziyet 2_IFC_Handrail toplam boy / 2 (çift çizgi varsayımı)", notu="YAKLAŞIK"))
note("Peyzaj alanları vaziyet çizgilerinin poligonlanmasıyla ve poligon içindeki yazıya göre sınıflandı; vaziyette sert/yumuşak zemin taraması olmadığı için 'yaklaşık'. 'Tesviye alanı' poligonları bahçe kabul edildi; sert zemin olabilir.", "doğrulanmalı")
note("İstinat/set/bahçe duvarı yükseklikleri iki yandaki kot yazılarının farkından; temel ve parapet payı yok.", "doğrulanmalı")

# ================================================================== KONTROL
T_KON = []
for kod in KODS:
    v = R[kod]; o = OZ[kod]
    net = sum(r["alan_pol"] for r in v["rooms"] if not r["dis"])
    dism = sum(r["alan_pol"] for r in v["rooms"] if r["dis"])
    T_KON.append(dict(kontrol="Net kapalı mahal alanı", blok=v["blok"], kat=KATAD[v["kat"]], metraj=r2(net), referans=o["net"], ref_kaynak="03-boyama era01_ozet.json (net)",
                      fark=r2(net - o["net"]), aciklama=("ozet net değeri bina dışındaki giriş merdivenini (3.96) içeriyor" if abs(net - o["net"]) > 1 else "uyumlu")))
    T_KON.append(dict(kontrol="Kapalı brüt iz (Fc)", blok=v["blok"], kat=KATAD[v["kat"]], metraj=r2(v["Fc_m2"]), referans=o["brut"], ref_kaynak=o.get("brut_kaynak", ""),
                      fark=r2(v["Fc_m2"] - o["brut"]), aciklama=("şema KAT BRÜTÜ balkonu (13.6) içeriyor" if kod == "C-blok-zemin-kat" else "raster ölçüm toleransı" if abs(v["Fc_m2"] - o["brut"]) < 1.5 else "incele")))
bt = sum(v["Fc_m2"] for v in R.values())
T_KON.append(dict(kontrol="Toplam kapalı brüt", blok="Tümü", kat="", metraj=r2(bt), referans=2361.18, ref_kaynak="ŞEF iş emri / era01_ozet.json", fark=r2(bt - 2361.18),
                  aciklama="C zemin balkonu (13.6) referansta kapalı sayılmış; kalan fark raster toleransı"))
# pencere sayısı
nm = len(T_PENC); nh = len(HACIM_W)
hc = collections.Counter((b, t) for b, k, t, g_, y in HACIM_W)
mc = collections.Counter((x["blok"], x["tip"]) for x in T_PENC)
T_KON.append(dict(kontrol="Pencere/doğrama adedi", blok="Tümü", kat="", metraj=nm, referans=nh, ref_kaynak="HACİM era01_model_rapor_v03.json (dograma)", fark=nm - nh,
                  aciklama="aşağıdaki tip farkları"))
for key in sorted(set(hc) | set(mc)):
    if hc.get(key, 0) != mc.get(key, 0):
        T_KON.append(dict(kontrol="Doğrama tipi farkı", blok=key[0], kat="", metraj=mc.get(key, 0), referans=hc.get(key, 0), ref_kaynak="HACİM v03", fark=mc.get(key, 0) - hc.get(key, 0),
                          aciklama={"P-01": "HACİM P-01'i ZK'da bir kez saydı; metrajda da bir kez (galeri)",
                                    "P-09": "HACİM okumadı; DXF'te etiketli (iç cam bölme)", "P-15": "HACİM okumadı; DXF'te etiketli (ışıklık)",
                                    "P-19": "HACİM okumadı; DXF'te etiketli", "P-20": "HACİM 'etiket 260, çizim 77' diye atladı; metrajda etiket ölçüsü",
                                    "P-22": "HACİM okumadı; DXF'te etiketli (740×280)", "GARAJ": "metrajda KAPI tablosunda",
                                    "KAPI": "HACİM D blok dış kapılarını doğrama saydı; metrajda KAPI tablosunda (K01)",
                                    "P-ETIKETSIZ": "aynı doğrama (A 1. kat avlu 375×280)"}.get(key[1], "")))
tipler = len(set(x["tip"] for x in T_PENC))
T_KON.append(dict(kontrol="Pencere tip sayısı", blok="Tümü", kat="", metraj=tipler, referans=28, ref_kaynak="ŞEF iş emri (≈28 tip)", fark=tipler - 28, aciklama="P-01…P-33 + etiketsiz avlu doğraması"))
nk = len(T_KAPI)
T_KON.append(dict(kontrol="Kapı adedi", blok="Tümü", kat="", metraj=nk, referans=77, ref_kaynak="DXF KAPI POZU etiketleri (A_K1 bloğu iki kez yerleşik, tekrar ayıklandı)", fark=nk - 77,
                  aciklama="fark = etiketsiz kapılar + garaj kapısı"))

OUT = dict(KAT=KAT, DUVAR=T_DUVAR, YUZEY=T_YUZEY, ZEMIN=T_ZEMIN, MAHAL=T_MAHAL, TAVAN=T_TAVAN, KAPI=T_KAPI, PENCERE=T_PENC, CEPHE=T_CEPHE,
           BA=T_BA, CATI=T_CATI, MERD=T_MERD, KORK=T_KORK, YAL=T_YAL, ARM=T_ARM, HAF=T_HAF, PEY=T_PEY, KON=T_KON, NOTLAR=NOTLAR, CATI_OLCU=CATI)
json.dump(OUT, open(os.path.join(HERE, "era01_metraj_tablolar.json"), "w"), ensure_ascii=False, indent=1, default=str)
print("ok", {k: len(v) for k, v in OUT.items() if isinstance(v, list)})
