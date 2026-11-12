# -*- coding: utf-8 -*-
"""ERA01 metraj (DETAY) - adım 3: Excel (openpyxl).
Girdi : era01_metraj_tablolar.json  ->  Çıktı: ../ERA01_detay_metraj_v01.xlsx
Tüm sayılar adım 2'de hesaplanır; burada yalnız tablolanır (toplamlar Python'da toplanıp değer olarak yazılır).
"""
import os, json, collections
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

HERE = os.path.dirname(os.path.abspath(__file__))
T = json.load(open(os.path.join(HERE, "era01_metraj_tablolar.json")))
OUT = os.path.join(HERE, "..", "ERA01_detay_metraj_v01.xlsx")
BL = ["A", "B", "C", "D"]

F = "Calibri"
f_n = Font(name=F, size=10); f_b = Font(name=F, size=10, bold=True); f_t = Font(name=F, size=14, bold=True)
f_i = Font(name=F, size=9, italic=True, color="555555"); f_h = Font(name=F, size=10, bold=True, color="FFFFFF")
fill_h = PatternFill("solid", fgColor="44546A"); fill_tot = PatternFill("solid", fgColor="D9E1F2")
fill_sec = PatternFill("solid", fgColor="EDEDED"); fill_warn = PatternFill("solid", fgColor="FFF2CC")
thin = Side(style="thin", color="BFBFBF"); brd = Border(left=thin, right=thin, top=thin, bottom=thin)
wrap = Alignment(wrap_text=True, vertical="top"); center = Alignment(horizontal="center", vertical="center", wrap_text=True)

wb = Workbook()
wb.remove(wb.active)
NOTLAR = T["NOTLAR"]

def tablo(ad, baslik, aciklama, cols, rows, toplam=None, uyari_key=None):
    """cols: [(anahtar, başlık, genişlik, biçim)]; toplam: toplanacak anahtarlar."""
    ws = wb.create_sheet(ad)
    ws["A1"] = baslik; ws["A1"].font = f_t
    ws["A2"] = aciklama; ws["A2"].font = f_i; ws["A2"].alignment = Alignment(wrap_text=True, vertical="top")
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=max(6, len(cols)))
    ws.row_dimensions[2].height = 42
    hr = 3
    for j, (k, h, w, fmt) in enumerate(cols, 1):
        c = ws.cell(hr, j, h); c.font = f_h; c.fill = fill_h; c.alignment = center; c.border = brd
        ws.column_dimensions[get_column_letter(j)].width = w
    ws.row_dimensions[hr].height = 32
    r = hr
    for row in rows:
        r += 1
        for j, (k, h, w, fmt) in enumerate(cols, 1):
            v = row.get(k)
            c = ws.cell(r, j, v); c.font = f_n; c.border = brd
            if fmt: c.number_format = fmt
            if isinstance(v, str) and len(v) > 30: c.alignment = wrap
        if uyari_key and row.get(uyari_key) and any(s in str(row.get(uyari_key)).upper() for s in ("DOĞRULANMALI", "VARSAYIM", "YAKLAŞIK", "BELİRSİZ")):
            for j in range(1, len(cols) + 1): ws.cell(r, j).fill = fill_warn
    last = r
    ws.auto_filter.ref = "A%d:%s%d" % (hr, get_column_letter(len(cols)), max(last, hr + 1))
    ws.freeze_panes = ws.cell(hr + 1, 1)
    if toplam and rows:
        r = last + 2
        ws.cell(r, 1, "TOPLAM (tüm satırlar; filtre uygulanırsa Excel durum çubuğundan bakınız)").font = f_b
        for j, (k, h, w, fmt) in enumerate(cols, 1):
            if k in toplam:
                s = sum((x.get(k) or 0) for x in rows if isinstance(x.get(k), (int, float)))
                c = ws.cell(r, j, round(s, 2)); c.font = f_b; c.fill = fill_tot; c.number_format = fmt or "#,##0.00"; c.border = brd
        # blok alt toplamları
        if any("blok" == k for k, *_ in cols):
            for b in BL:
                rs = [x for x in rows if x.get("blok") == b]
                if not rs: continue
                r += 1
                ws.cell(r, 1, "Blok %s toplamı" % b).font = f_b
                for j, (k, h, w, fmt) in enumerate(cols, 1):
                    if k in toplam:
                        s = sum((x.get(k) or 0) for x in rs if isinstance(x.get(k), (int, float)))
                        c = ws.cell(r, j, round(s, 2)); c.font = f_b; c.number_format = fmt or "#,##0.00"; c.border = brd
    ws.sheet_view.zoomScale = 90
    return ws

N2 = "#,##0.00"; N0 = "#,##0"

# ------------------------------------------------------------------ ÖZET verisi
def sumf(rows, key, **flt):
    out = {b: 0.0 for b in BL}
    for x in rows:
        if all((x.get(k) == v if not callable(v) else v(x.get(k))) for k, v in flt.items()):
            if x.get("blok") in out and isinstance(x.get(key), (int, float)): out[x["blok"]] += x[key]
    return out
OZ = []
def oz(bolum, kalem, birim, vals, kaynak, notu=""):
    d = dict(bolum=bolum, kalem=kalem, birim=birim, kaynak=kaynak, notu=notu)
    for b in BL: d[b] = round(vals.get(b, 0) or 0, 2)
    d["top"] = round(sum(d[b] for b in BL), 2)
    OZ.append(d)
D = T["DUVAR"]
oz("1 Duvar", "Kagir duvar – dış, brüt (boşluklu)", "m²", sumf(D, "brut", tur="Dış duvar"), "01_DUVAR: Tür = Dış duvar, 'Brüt m²'")
oz("1 Duvar", "Kagir duvar – dış, net (boşluklar düşülmüş)", "m²", sumf(D, "net", tur="Dış duvar"), "01_DUVAR: Tür = Dış duvar, 'Net m²'")
oz("1 Duvar", "Kagir duvar – iç, brüt (boşluklu)", "m²", sumf(D, "brut", tur="İç duvar"), "01_DUVAR: Tür = İç duvar, 'Brüt m²'")
oz("1 Duvar", "Kagir duvar – iç, net (boşluklar düşülmüş)", "m²", sumf(D, "net", tur="İç duvar"), "01_DUVAR: Tür = İç duvar, 'Net m²'")
for tur in ("Dış duvar", "İç duvar"):
    for t in sorted(set(x["kal_cm"] for x in D if x["tur"] == tur)):
        oz("1 Duvar", "%s %d cm – net" % (tur, t), "m²", sumf(D, "net", tur=tur, kal_cm=t), "01_DUVAR: Tür = %s, Kalınlık = %d" % (tur, t))
oz("1 Duvar", "Kagir duvar hacmi (net, bilgi)", "m³", sumf(D, "m3"), "01_DUVAR 'Net m³'")
Y = T["YUZEY"]
oz("2 Duvar yüzeyi", "İç sıva (seramik altı dahil)", "m²", sumf(Y, "siva"), "02_DUVAR_YUZEY 'İç sıva m²'")
oz("2 Duvar yüzeyi", "İç boya (DV-01 saten boya / beton üzeri boya)", "m²", sumf(Y, "boya"), "02_DUVAR_YUZEY 'Boya m²'")
oz("2 Duvar yüzeyi", "Islak hacim duvar seramiği (tavan yüksekliğine kadar)", "m²", sumf(Y, "seramik"), "02_DUVAR_YUZEY 'Seramik m²'")
C = T["CEPHE"]
oz("2 Duvar yüzeyi", "Dış cephe yüzeyi (duvar + subasman, net)", "m²", sumf(C, "net", bolum=lambda v: v in ("Dış duvar cephesi", "Subasman (perde üst bandı 172.95→174.15)")), "11_CEPHE")
Z = T["ZEMIN"]
for g in sorted(set(x["grup"] for x in Z)):
    oz("3 Zemin", "Zemin – %s" % g, "m²", sumf(Z, "alan", grup=g), "03_ZEMIN: Grup = %s" % g)
oz("3 Zemin", "Süpürgelik", "m", sumf(Z, "sup"), "03_ZEMIN 'Süpürgelik m'")
K = T["KAPI"]
for kon in ("İç", "Dış"):
    oz("4 Kapı", "Kapı – %s" % {"İç": "iç", "Dış": "dış"}[kon], "adet", {b: sum(1 for x in K if x["blok"] == b and x["konum"] == kon) for b in BL}, "KAPI: Konum = %s" % kon)
oz("4 Kapı", "Kapı boşluk alanı", "m²", {b: sum((x["gen"] or 0) * (x["yuk"] or 0) / 1e4 for x in K if x["blok"] == b) for b in BL}, "KAPI: gen × yük")
P = T["PENCERE"]
oz("5 Pencere", "Pencere/doğrama", "adet", {b: sum(x["adet"] for x in P if x["blok"] == b) for b in BL}, "PENCERE")
oz("5 Pencere", "Doğrama boşluk alanı", "m²", sumf(P, "alan"), "PENCERE 'Boşluk m²'")
oz("5 Pencere", "Cam alanı (yaklaşık)", "m²", sumf(P, "cam"), "PENCERE 'Cam m²'", "7 cm profil varsayımı")
oz("5 Pencere", "Denizlik (dış)", "m", sumf(P, "denizlik"), "PENCERE 'Denizlik m'")
oz("5 Pencere", "Eşik (döşemeye inen doğrama)", "m", sumf(P, "esik"), "PENCERE 'Eşik m'")
TV = T["TAVAN"]
for tip in sorted(set(x["tip"] for x in TV)):
    oz("6 Tavan", tip, "m²", sumf(TV, "alan", tip=tip), "06_TAVAN: Tip = %s" % tip)
BA = T["BA"]
oz("7 Betonarme", "Radye temel", "m³", sumf(BA, "m3", eleman="Radye temel"), "07_BETONARME: Radye temel")
oz("7 Betonarme", "Grobeton", "m³", sumf(BA, "m3", eleman="Grobeton (10 cm)"), "07_BETONARME")
oz("7 Betonarme", "Döşeme alanı (ara kat + çatı)", "m²", sumf(BA, "plan_m2", eleman=lambda v: v.startswith("Döşeme")), "07_BETONARME: Döşeme*")
oz("7 Betonarme", "Döşeme betonu", "m³", sumf(BA, "m3", eleman=lambda v: v.startswith("Döşeme")), "07_BETONARME: Döşeme*")
oz("7 Betonarme", "Kolon", "adet", sumf(BA, "adet", eleman="Kolon"), "07_BETONARME: Kolon (kat başına)")
oz("7 Betonarme", "Kolon betonu", "m³", sumf(BA, "m3", eleman="Kolon"), "07_BETONARME: Kolon")
oz("7 Betonarme", "Perde betonu", "m³", sumf(BA, "m3", eleman="Perde"), "07_BETONARME: Perde")
oz("7 Betonarme", "Toplam beton (grobeton hariç)", "m³", sumf(BA, "m3", eleman=lambda v: v != "Grobeton (10 cm)"), "07_BETONARME", "kiriş, merdiven, havuz teknesi hariç")
CA = T["CATI"]
for kal in ("Çatı örtüsü (METAL ÇATI) – eğik alan", "Galvanizli sac dere (parapet arkası)", "Mahya", "Kırma (köşe mahyası)", "Parapet (çatı) uzunluğu", "Yağmur iniş borusu"):
    rs = [x for x in CA if x["kalem"] == kal]
    oz("8 Çatı", kal, rs[0]["birim"], {x["blok"]: x["miktar"] for x in rs}, "08_CATI", "varsayım" if "iniş" in kal else "")
M = T["MERD"]
oz("9 Merdiven", "Merdiven rıht adedi", "adet", {b: sum(x["adet"] for x in M if x["blok"] == b) for b in BL}, "09_MERDIVEN")
oz("9 Merdiven", "Merdiven kaplaması (basamak + rıht + sahanlık)", "m²", sumf(M, "kaplama_m2"), "09_MERDIVEN")
KO = T["KORK"]
oz("9 Merdiven", "Merdiven korkuluğu (plan)", "m", sumf(KO, "uzunluk", yer="Merdiven evi"), "10_KORKULUK: Yer = Merdiven evi")
oz("10 Korkuluk", "Teras/balkon korkuluğu (110 cm)", "m", sumf(KO, "uzunluk", yer=lambda v: v != "Merdiven evi"), "10_KORKULUK")
oz("11 Cephe", "Dış duvar cephesi (net)", "m²", sumf(C, "net", bolum="Dış duvar cephesi"), "11_CEPHE")
oz("11 Cephe", "Subasman (A blok)", "m²", sumf(C, "net", bolum=lambda v: v.startswith("Subasman")), "11_CEPHE")
oz("11 Cephe", "Saçak alnı + parapet dış yüzü", "m²", sumf(C, "net", bolum="Saçak alnı + parapet dış yüzü"), "11_CEPHE")
oz("11 Cephe", "Parapet iç yüzü", "m²", sumf(C, "net", bolum="Parapet iç yüzü"), "11_CEPHE")
oz("11 Cephe", "Saçak altı", "m²", sumf(C, "net", bolum=lambda v: v.startswith("Saçak altı")), "11_CEPHE")
YA = T["YAL"]
for kal in [x["kalem"] for x in YA if x["blok"] == "A"]:
    oz("12 Yalıtım", kal, "m²", {x["blok"]: x["miktar"] for x in YA if x["kalem"] == kal}, "12_YALITIM")
AR = T["ARM"]
for tur in sorted(set(x["tur"] for x in AR)):
    oz("13 Armatür", tur, "adet", {b: sum(x["adet"] for x in AR if x["blok"] == b and x["tur"] == tur) for b in BL}, "13_ARMATUR")
HA = T["HAF"]
for kal in ("Temel kazısı (yaklaşık)", "Geri dolgu – çalışma boşluğu (yaklaşık)", "Blokaj (15 cm)"):
    oz("14 Hafriyat", kal, "m³", {x["blok"]: x["miktar"] for x in HA if x["kalem"] == kal}, "14_HAFRIYAT", "YAKLAŞIK")
for x in T["PEY"]:
    d = dict(bolum="15 Peyzaj (site)", kalem=x["kalem"], birim=x["birim"], kaynak="15_PEYZAJ", notu=x["notu"], A=None, B=None, C=None, D=None, top=x["miktar"])
    OZ.append(d)
MA = T["MAHAL"]
oz("16 Mahal", "Mahal sayısı", "adet", {b: sum(1 for x in MA if x["blok"] == b) for b in BL}, "16_MAHAL_LISTESI")
oz("16 Mahal", "Net kapalı mahal alanı", "m²", {b: sum(x["alan"] for x in MA if x["blok"] == b and not x["grup"].startswith(("Teras", "Dış merdiven"))) for b in BL}, "16_MAHAL_LISTESI (açık alanlar hariç)")
oz("16 Mahal", "Açık alan (teras/balkon/avlu/dış merdiven)", "m²", {b: sum(x["alan"] for x in MA if x["blok"] == b and x["grup"].startswith(("Teras", "Dış merdiven"))) for b in BL}, "16_MAHAL_LISTESI")

# ------------------------------------------------------------------ ÖZET sayfası
ws = wb.create_sheet("OZET")
ws["A1"] = "ERA01 ERA Evi – Detay Metrajı v01 (yalnız miktar)"; ws["A1"].font = f_t
ws["A2"] = ("Kaynak: 00-girdi/ERA01_girdi_proje.dxf (uygulama/ruhsat seti, birim cm). Hazırlayan: DETAY (ofis dijital personeli), 2026-11-11. "
            "Poz numarası ve birim fiyat yok. Sarı satırlar varsayım/yaklaşık içerir; ayrıntı ilgili sayfada ve VARSAYIMLAR sayfasında.")
ws["A2"].font = f_i; ws["A2"].alignment = Alignment(wrap_text=True, vertical="top"); ws.merge_cells("A2:J2"); ws.row_dimensions[2].height = 40
hd = ["Bölüm", "Kalem", "Birim", "A blok", "B blok", "C blok", "D blok", "TOPLAM", "Kaynak sayfa / süzgeç", "Not"]
wd = [16, 52, 8, 12, 12, 12, 12, 13, 46, 30]
for j, (h, w) in enumerate(zip(hd, wd), 1):
    c = ws.cell(3, j, h); c.font = f_h; c.fill = fill_h; c.alignment = center; c.border = brd
    ws.column_dimensions[get_column_letter(j)].width = w
r = 3; prev = None
for d in OZ:
    r += 1
    vals = [d["bolum"], d["kalem"], d["birim"], d["A"], d["B"], d["C"], d["D"], d["top"], d["kaynak"], d["notu"]]
    for j, v in enumerate(vals, 1):
        c = ws.cell(r, j, v); c.font = f_b if j == 8 else f_n; c.border = brd
        if 4 <= j <= 8: c.number_format = N0 if d["birim"] in ("adet", "rıht") else N2
        if j == 8: c.fill = fill_tot
    if any(s in (d["notu"] or "").upper() + d["kalem"].upper() for s in ("YAKLAŞIK", "VARSAYIM", "DOĞRULANMALI", "BELİRSİZ")):
        for j in (1, 2, 3, 9, 10): ws.cell(r, j).fill = fill_warn
    if d["bolum"] != prev:
        ws.cell(r, 1).font = f_b
    prev = d["bolum"]
ws.auto_filter.ref = "A3:J%d" % r
ws.freeze_panes = "D4"
# duvar kalınlık özeti (pivot)
r += 3
ws.cell(r, 1, "DUVAR KALINLIĞINA GÖRE ÖZET (kagir, m²)").font = f_b
r += 1
hd2 = ["Tür", "Kalınlık (cm)", "Uzunluk (m)", "Brüt m²", "Boşluk m²", "Net m²", "Net m³"]
for j, h in enumerate(hd2, 1):
    c = ws.cell(r, j, h); c.font = f_h; c.fill = fill_h; c.alignment = center; c.border = brd
agg = collections.defaultdict(lambda: [0, 0, 0, 0, 0])
for x in D:
    a = agg[(x["tur"], x["kal_cm"])]
    a[0] += x["uzunluk"] or 0; a[1] += x["brut"] or 0; a[2] += x["bosluk"] or 0; a[3] += x["net"] or 0; a[4] += x["m3"] or 0
for (tur, kal), a in sorted(agg.items()):
    r += 1
    for j, v in enumerate([tur, kal] + [round(z, 2) for z in a], 1):
        c = ws.cell(r, j, v); c.font = f_n; c.border = brd
        if j >= 3: c.number_format = N2
r += 1
tot = [sum(a[i] for a in agg.values()) for i in range(5)]
for j, v in enumerate(["TOPLAM", ""] + [round(z, 2) for z in tot], 1):
    c = ws.cell(r, j, v); c.font = f_b; c.fill = fill_tot; c.border = brd
    if j >= 3: c.number_format = N2
ws.sheet_view.zoomScale = 90

# ------------------------------------------------------------------ detay sayfaları
tablo("01_DUVAR", "1. Duvar metrajı (kagir) – kalınlığa göre, dış/iç, blok/kat",
      "Uzunluk = plan iz alanı / kalınlık (raster 1 cm). Brüt = uzunluk × brüt duvar yüksekliği (döşeme üstü → üst döşeme altı). Boşluk = bu sınıftaki kagir duvarda kalan pencere/kapı gen × min(yük, H). Betonarme perde/kolon 07_BETONARME'de.",
      [("blok", "Blok", 6, None), ("kat", "Kat", 11, None), ("tur", "Tür", 10, None), ("kal_cm", "Kalınlık (cm)", 9, N0), ("malzeme", "Malzeme", 18, None),
       ("uzunluk", "Uzunluk (m)", 10, N2), ("H", "Brüt yükseklik (m)", 10, N2), ("brut", "Brüt m² (boşluklu)", 11, N2), ("bosluk_adet", "Boşluk adedi", 8, N0),
       ("bosluk", "Boşluk m²", 10, N2), ("net", "Net m²", 10, N2), ("m3", "Net m³ (bilgi)", 9, N2), ("plan_m2", "Plan iz m²", 9, N2),
       ("yontem", "Hesap yöntemi / kaynak katman", 60, None), ("notu", "Not", 30, None)],
      D, toplam={"uzunluk", "brut", "bosluk", "net", "m3", "plan_m2", "bosluk_adet"}, uyari_key="notu")
tablo("02_DUVAR_YUZEY", "2. İç duvar yüzey işleri – mahal bazında (sıva, boya, ıslak hacim seramiği)",
      "Çevre = 0_IFC_Area mahal poligonu. Yükseklik = net tavan yüksekliği (kesit tavan kotu − kat kotu). Boşluk = mahale açılan pencere ve kapılar (gen × min(yük, h)). Dış cephe 11_CEPHE sayfasında.",
      [("blok", "Blok", 6, None), ("kat", "Kat", 11, None), ("mahal", "Mahal", 18, None), ("grup", "Grup", 18, None), ("cevre", "Çevre (m)", 9, N2),
       ("ht", "Tavan yük. (m)", 8, N2), ("brut", "Brüt duvar yüzü m²", 11, N2), ("bosluk_adet", "Boşluk adedi", 8, N0), ("bosluk", "Boşluk m²", 10, N2),
       ("net", "Net yüz m²", 10, N2), ("siva", "İç sıva m²", 10, N2), ("boya", "Boya m²", 10, N2), ("seramik", "Seramik m²", 10, N2), ("duvar", "Duvar malzemesi", 30, None)],
      Y, toplam={"cevre", "brut", "bosluk", "net", "siva", "boya", "seramik", "bosluk_adet"}, uyari_key="duvar")
tablo("03_ZEMIN", "3. Zemin kaplaması – mahal alanlarından, kaplama grubuna göre",
      "Alan = 0_IFC_Area poligonu (DXF yazılı alanla karşılaştırma sütunu). Malzeme ofis kütüphanesi (ZM-01/ZM-02) veya 'belirsiz'. Süpürgelik = çevre − kapı ve döşemeye inen doğrama genişlikleri.",
      [("blok", "Blok", 6, None), ("kat", "Kat", 11, None), ("mahal", "Mahal", 18, None), ("grup", "Kaplama grubu", 22, None), ("malzeme", "Zemin malzemesi", 40, None),
       ("alan", "Alan m² (poligon)", 10, N2), ("alan_yazi", "DXF yazılı alan", 9, N2), ("sup", "Süpürgelik (m)", 10, N2), ("kot", "Kat kotu (m)", 9, N2), ("notu", "Not", 30, None)],
      Z, toplam={"alan", "alan_yazi", "sup"}, uyari_key="malzeme")
tablo("KAPI", "4. Kapı tablosu",
      "Kaynak: KAPI POZU blokları (Kxx etiketi + gen/yük), 1_IFC_Door / 2_IFC_Door blokları ve yayları. 'DIN sağ/sol' = kapının açıldığı taraftan bakınca menteşe sağda/solda. Etiketsiz kapılar ayrıca işaretli.",
      [("blok", "Blok", 6, None), ("kat", "Kat", 11, None), ("etiket", "Etiket", 9, None), ("gen", "Gen. (cm)", 8, N0), ("yuk", "Yük. (cm)", 8, N0),
       ("kanat", "Kanat", 6, N0), ("tur", "Tür", 22, None), ("acilis", "Açılış", 10, None), ("mahal", "Mahal(ler)", 30, None), ("konum", "Konum", 7, None),
       ("duvar", "Duvar", 12, None), ("dxf_blok", "DXF blok", 18, None), ("kaynak", "Kaynak", 34, None), ("notu", "Not", 20, None)],
      K, toplam={"kanat"}, uyari_key="notu")
# kapı tip özeti satırları ekle
wsk = wb["KAPI"]; r = wsk.max_row + 3
wsk.cell(r, 1, "KAPI TİP ÖZETİ (etiket × ölçü × blok)").font = f_b; r += 1
hd3 = ["Etiket", "Gen×Yük", "Tür", "A", "B", "C", "D", "Toplam"]
for j, h in enumerate(hd3, 1):
    c = wsk.cell(r, j, h); c.font = f_h; c.fill = fill_h; c.border = brd
agg = collections.defaultdict(lambda: collections.Counter())
for x in K: agg[(x["etiket"], "%s×%s" % (x["gen"], x["yuk"]), x["tur"])][x["blok"]] += 1
for key, cnt in sorted(agg.items()):
    r += 1
    for j, v in enumerate(list(key) + [cnt.get(b, 0) for b in BL] + [sum(cnt.values())], 1):
        c = wsk.cell(r, j, v); c.font = f_n; c.border = brd
tablo("PENCERE", "5. Pencere / doğrama tablosu (DXF etiket ölçüleri – konsept v04 değil)",
      "Kaynak: 0_IFC_Window_Text etiketleri (TİP, GENİŞLİK, YÜKSEKLİK). Parapet: üst kasa = tavan − 17 cm kuralı (HACİM görünüş okuması). Cam ≈ boşluk − çerçeve boyu × 7 cm. Denizlik/eşik dış doğramalar için.",
      [("blok", "Blok", 6, None), ("kat", "Kat", 16, None), ("tip", "Tip", 12, None), ("gen", "Gen. (cm)", 8, N0), ("yuk", "Yük. (cm)", 8, N0), ("parapet", "Parapet (cm)", 8, N0),
       ("adet", "Adet", 6, N0), ("alan", "Boşluk m²", 9, N2), ("cam", "Cam m² (yaklaşık)", 9, N2), ("cerceve", "Çerçeve+kayıt (m)", 9, N2), ("bolme", "Düşey bölme", 7, N0),
       ("kayit", "Yatay kayıt", 7, N0), ("denizlik", "Denizlik (m)", 9, N2), ("esik", "Eşik (m)", 8, N2), ("konum", "Konum", 12, None), ("mahal", "Mahal", 18, None),
       ("duvar", "Duvar", 12, None), ("kaynak", "Kaynak", 30, None), ("notu", "Not", 34, None)],
      P, toplam={"adet", "alan", "cam", "cerceve", "denizlik", "esik"}, uyari_key="notu")
wsp = wb["PENCERE"]; r = wsp.max_row + 3
wsp.cell(r, 1, "PENCERE TİP ÖZETİ").font = f_b; r += 1
hd4 = ["Tip", "Gen×Yük (cm)", "Parapet (cm)", "A", "B", "C", "D", "Toplam adet", "Toplam m²"]
for j, h in enumerate(hd4, 1):
    c = wsp.cell(r, j, h); c.font = f_h; c.fill = fill_h; c.border = brd
agg = collections.defaultdict(lambda: [collections.Counter(), 0.0])
for x in P:
    a = agg[(x["tip"], "%d×%d" % (x["gen"], x["yuk"]), x["parapet"])]; a[0][x["blok"]] += 1; a[1] += x["alan"]
def tkey(k):
    t = k[0]
    try: return (0, int(t.split("-")[1]), k[1])
    except Exception: return (1, 0, k[1])
for key in sorted(agg, key=tkey):
    cnt, ar = agg[key]; r += 1
    for j, v in enumerate(list(key) + [cnt.get(b, 0) for b in BL] + [sum(cnt.values()), round(ar, 2)], 1):
        c = wsp.cell(r, j, v); c.font = f_n; c.border = brd
r += 1
wsp.cell(r, 1, "Tip sayısı: %d   Doğrama adedi: %d" % (len(set(x["tip"] for x in P)), len(P))).font = f_b
tablo("06_TAVAN", "6. Tavan – mahal bazında",
      "Alan = mahal net alanı. Islak hacim ve havuz salonu asma tavan (varsayım), otopark/teknik brüt beton üzeri boya, diğerleri alçı sıva + boya (DXF 'TAVAN: BOYA').",
      [("blok", "Blok", 6, None), ("kat", "Kat", 11, None), ("mahal", "Mahal", 18, None), ("grup", "Grup", 22, None), ("tip", "Tavan tipi", 46, None),
       ("alan", "Alan m²", 10, N2), ("tavan_kotu", "Tavan kotu (m)", 10, N2)], TV, toplam={"alan"}, uyari_key="tip")
tablo("07_BETONARME", "7. Betonarme – temel, döşeme, kolon, perde",
      "Kolon/perde: 1_IFC_Concrete_Section kesitleri, H = duvar brüt yüksekliği (döşeme arası). Döşeme: blok yerel koordinatında kat izlerinin birleşimi × 30 cm. Radye: tüm kat izlerinin birleşimi × kesit kalınlığı. Kiriş/merdiven/havuz teknesi yok.",
      [("blok", "Blok", 6, None), ("kat", "Kat / seviye", 16, None), ("eleman", "Eleman", 16, None), ("adet", "Adet", 6, N0), ("olcu", "Ölçü (cm)", 26, None),
       ("uzunluk", "Perde uzunluğu (m)", 9, N2), ("plan_m2", "Plan alanı m²", 10, N2), ("H", "Yükseklik/kalınlık (m)", 10, N2), ("m3", "Hacim m³", 10, N2),
       ("yontem", "Hesap yöntemi / kaynak", 70, None)], BA, toplam={"adet", "plan_m2", "m3", "uzunluk"}, uyari_key="yontem")
tablo("08_CATI", "8. Çatı – metal kırma çatı (parapet içinde, galvanizli sac dere)",
      "Ölçüler çatı planlarından (0_IFC_Elevation_1/2/3/5) ve çatı kot bloklarından. Eğik alan = izdüşüm × √(1+eğim²), eğim = (mahya − saçak) / (kısa kenar/2).",
      [("blok", "Blok", 6, None), ("kalem", "Kalem", 44, None), ("birim", "Birim", 6, None), ("miktar", "Miktar", 10, N2), ("yontem", "Hesap yöntemi / kaynak", 70, None), ("notu", "Not", 40, None)],
      CA, toplam=None, uyari_key="notu")
tablo("09_MERDIVEN", "9. Merdiven – basamak, kaplama",
      "0_IFC_Stair_Text 'M: rıht × adet / basamak' yazıları (her merdiven bir kez, alt katına yazıldı). Kol genişliği 1_IFC_Stair basamak çizgilerinden. Korkuluk 10_KORKULUK sayfasında.",
      [("blok", "Blok", 6, None), ("kat", "Kat", 20, None), ("yazi", "DXF yazısı", 16, None), ("riht", "Rıht (cm)", 8, N2), ("adet", "Rıht adedi", 8, N0),
       ("basamak_cm", "Basamak (cm)", 8, N2), ("kol", "Kol", 5, N0), ("basamak_adet", "Basamak adedi", 8, N0), ("kol_gen", "Kol gen. (cm)", 8, N0), ("h_toplam", "Kat farkı (m)", 8, N2),
       ("basamak_m2", "Basamak m²", 9, N2), ("riht_m2", "Rıht m²", 9, N2), ("sahanlik_m2", "Sahanlık m²", 9, N2), ("kaplama_m2", "Kaplama toplam m²", 10, N2),
       ("yontem", "Hesap yöntemi", 60, None), ("notu", "Not", 24, None)], M, toplam={"adet", "basamak_adet", "basamak_m2", "riht_m2", "sahanlik_m2", "kaplama_m2"}, uyari_key="notu")
tablo("10_KORKULUK", "10. Korkuluklar – teras/balkon ve merdiven",
      "Teras/balkon: mahal poligonunun bina kapalı izine 35 cm'den uzak kenarları. Merdiven: 2_IFC_Handrail çizgileri / 2.",
      [("blok", "Blok", 6, None), ("kat", "Kat", 11, None), ("yer", "Yer", 26, None), ("tur", "Tür", 40, None), ("uzunluk", "Uzunluk (m)", 10, N2),
       ("yontem", "Hesap yöntemi", 60, None), ("notu", "Not", 34, None)], KO, toplam={"uzunluk"}, uyari_key="notu")
tablo("11_CEPHE", "11. Cephe kaplaması (malzeme belirsiz – DXF görünüşlerinde malzeme yazmıyor)",
      "Dış çevre = kapalı iz sınırı (raster → vektör). Bodrumda dış perde toprak temaslı (12_YALITIM). Boşluk = dış pencere ve kapılar. Çatı satırları çatı planı ölçülerinden.",
      [("blok", "Blok", 6, None), ("kat", "Kat", 11, None), ("bolum", "Bölüm", 40, None), ("uzunluk", "Uzunluk (m)", 10, N2), ("h", "Yükseklik (m)", 9, N2),
       ("brut", "Brüt m²", 10, N2), ("bosluk", "Boşluk m²", 10, N2), ("net", "Net m²", 10, N2), ("malzeme", "Malzeme", 22, None), ("yontem", "Hesap yöntemi", 70, None)],
      C, toplam={"brut", "bosluk", "net"}, uyari_key="malzeme")
tablo("12_YALITIM", "12. Isı ve su yalıtımı (alanlar diğer kalemlerden türetildi)",
      "Kalınlık/malzeme seçilmedi (TS 825 hesabı ayrıca). Bindirme ve fire payı yok.",
      [("blok", "Blok", 6, None), ("kalem", "Kalem", 50, None), ("birim", "Birim", 6, None), ("miktar", "Miktar", 10, N2), ("yontem", "Hesap yöntemi / kaynak", 80, None), ("notu", "Not", 40, None)],
      YA, toplam=None, uyari_key="notu")
tablo("13_ARMATUR", "13. Islak hacim armatürleri ve mutfak elemanları",
      "Plan blok referansları sayıldı (6_IFC_Furniture_WC / _Wetspace; dinamik blokların asıl adı). Mahal = bloğa en yakın mahal poligonu.",
      [("blok", "Blok", 6, None), ("kat", "Kat", 11, None), ("mahal", "Mahal", 18, None), ("tur", "Armatür", 50, None), ("adet", "Adet", 7, N0), ("kaynak", "Kaynak", 50, None)],
      AR, toplam={"adet"}, uyari_key="tur")
tablo("14_HAFRIYAT", "14. Hafriyat ve dolgu (YAKLAŞIK)",
      "Doğal zemin: vaziyet 'BLOK KOSE KOTLARI' (kot hesabında kullanılan tabii zemin kotları) en küçük kareler düzlemi. Kazı tabanı: radye altı − 25 cm. 25 cm ızgara ile hacim.",
      [("blok", "Blok", 6, None), ("kalem", "Kalem", 36, None), ("birim", "Birim", 6, None), ("miktar", "Miktar", 10, N2), ("yontem", "Hesap yöntemi", 100, None), ("notu", "Not", 30, None)],
      HA, toplam=None, uyari_key="notu")
tablo("15_PEYZAJ", "15. Peyzaj – sert zemin, yeşil alan, istinat/set/bahçe duvarları (site geneli, YAKLAŞIK)",
      "Vaziyet planı (VAZIYET PLANI bloğu, ölçek ×4) çizgileri parsel içinde poligonlandı; poligon sınıfı içindeki yazıdan. Vaziyette malzeme taraması olmadığından alanlar yaklaşık.",
      [("kalem", "Kalem", 60, None), ("birim", "Birim", 6, None), ("miktar", "Miktar", 10, N2), ("yontem", "Hesap yöntemi", 90, None), ("notu", "Not", 40, None)],
      T["PEY"], toplam=None, uyari_key="notu")
tablo("16_MAHAL_LISTESI", "16. Mahal listesi",
      "Her mahal: blok, kat, ad, net alan (poligon; DXF yazılı alan yanında), zemin/duvar/tavan malzemesi (ofis kütüphanesi: ZM-01, ZM-02, DV-01), süpürgelik, net tavan yüksekliği. 'DXF etiketi' sütunu çizimdeki mahal etiketi notlarıdır.",
      [("blok", "Blok", 6, None), ("kat", "Kat", 11, None), ("kot", "Kat kotu", 8, None), ("mahal", "Mahal", 18, None), ("grup", "Grup", 20, None), ("alan", "Net alan m²", 9, N2),
       ("alan_yazi", "DXF yazılı alan", 8, N2), ("zemin", "Zemin", 34, None), ("duvar", "Duvar", 30, None), ("tavan", "Tavan", 34, None), ("sup", "Süpürgelik (m)", 9, N2),
       ("ht", "Tavan yük. (m)", 8, N2), ("dxf_not", "DXF etiketi", 30, None)], MA, toplam={"alan", "sup"}, uyari_key="zemin")
KAT = [dict(kod=k, **v) for k, v in T["KAT"].items()]
tablo("KAT_PARAMETRELERI", "Kat parametreleri (tüm yükseklik hesaplarının kaynağı)",
      "Kotlar: 02-model/kaynak/era01_model_rapor_v03.json (DXF kesitleri). Duvar alt = taşıyıcı döşeme üstü (en alt katta radye üstü = kat −0.50), duvar üst = üst döşeme altı (son katta çatı döşemesi altı).",
      [("blok", "Blok", 6, None), ("kat", "Kat", 6, None), ("kot", "Kat kotu", 9, N2), ("ust", "Üst kat kotu / çatı döşemesi üstü", 12, N2), ("tavan", "Tavan kotu", 9, N2),
       ("net_h", "Net tavan yük.", 9, N2), ("kat_h", "Kat yüksekliği", 9, N2), ("duvar_alt", "Duvar alt kotu", 9, N2), ("duvar_ust", "Duvar üst kotu", 9, N2),
       ("H_duvar", "Duvar brüt yük.", 9, N2), ("h_cephe", "Cephe yük.", 9, N2), ("top", "Son kat", 7, None), ("en_alt", "En alt kat", 7, None)], KAT)
tablo("KONTROL", "Kontroller – PAFTA özeti ve HACİM pencere tablosu ile karşılaştırma",
      "Referanslar: 03-boyama/kaynak/era01_ozet.json (net/brüt alan), 02-model/kaynak/era01_model_rapor_v03.json (75 doğrama).",
      [("kontrol", "Kontrol", 24, None), ("blok", "Blok", 6, None), ("kat", "Kat", 11, None), ("metraj", "Metraj", 10, N2), ("referans", "Referans", 10, N2),
       ("fark", "Fark", 9, N2), ("ref_kaynak", "Referans kaynağı", 40, None), ("aciklama", "Açıklama", 60, None)], T["KON"])
ws = wb.create_sheet("VARSAYIMLAR")
ws["A1"] = "Varsayımlar ve doğrulanacaklar (numaralı)"; ws["A1"].font = f_t
for j, (h, w) in enumerate([("No", 5), ("Tür", 14), ("Açıklama", 150)], 1):
    c = ws.cell(3, j, h); c.font = f_h; c.fill = fill_h; c.border = brd; ws.column_dimensions[get_column_letter(j)].width = w
for i, (tur, txt) in enumerate(NOTLAR, 1):
    for j, v in enumerate([i, tur, txt], 1):
        c = ws.cell(3 + i, j, v); c.font = f_n; c.border = brd; c.alignment = wrap
    if tur == "doğrulanmalı":
        for j in (1, 2, 3): ws.cell(3 + i, j).fill = fill_warn
ws.freeze_panes = "A4"; ws.auto_filter.ref = "A3:C%d" % (3 + len(NOTLAR))
# sıra: OZET başa
wb.move_sheet("OZET", offset=-(len(wb.sheetnames) - 1))
from openpyxl.worksheet.properties import PageSetupProperties
for w in wb.worksheets:
    w.page_setup.orientation = "landscape"; w.page_setup.paperSize = w.PAPERSIZE_A3
    w.sheet_properties.pageSetUpPr = PageSetupProperties(fitToPage=True)
    w.page_setup.fitToWidth = 1; w.page_setup.fitToHeight = 0
    w.print_title_rows = "3:3"
wb.save(OUT)
print("kaydedildi", OUT, wb.sheetnames)
