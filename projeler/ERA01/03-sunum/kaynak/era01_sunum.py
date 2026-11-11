# -*- coding: utf-8 -*-
"""ERA01 ERA Evi: konsept proje sunumu (SUNUM agent).

Üretir: ../ERA01_sunum_konsept-sunum_v01.pptx (A3 yatay, düzenlenebilir)
        ../gorseller/  (görsel çerçevelerine kırpılmış render ve yer tutucu görseller)
Kullanım: python3 era01_sunum.py   (sonra PDF: soffice --headless --convert-to pdf)

Görsel çerçeveleri tekil resim nesneleridir (gruplanmamış, PPTX kırpması yok):
render önceden PIL ile çerçeve oranına kırpılır, böylece PowerPoint'te
"Resmi Değiştir" ile yeni görsel aynı çerçeveye oturur.
"""
import json
import os
import sys

from PIL import Image, ImageDraw, ImageFont
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Emu, Mm, Pt
from lxml import etree

SURUM = "v01"
TARIH = "11.11.2026"

BURADA = os.path.dirname(os.path.abspath(__file__))
SUNUM = os.path.dirname(BURADA)
PROJE = os.path.dirname(SUNUM)
KOK = os.path.dirname(os.path.dirname(PROJE))
STD = os.path.join(KOK, "ofis-standartlari")
BOYAMA = os.path.join(PROJE, "03-boyama")
RENDER = os.path.join(PROJE, "00-girdi", "render")
GORSEL = os.path.join(SUNUM, "gorseller")
ARA = os.environ.get("ERA01_ARA", os.path.join(BURADA, "_ara"))  # küçültülmüş paftalar (tekrar üretilebilir)
os.makedirs(GORSEL, exist_ok=True)
os.makedirs(ARA, exist_ok=True)

LOGO = os.path.join(STD, "logolar", "IFC_Architects_logo_koyu.png")
TAS_DUVAR = os.path.join(STD, "sablon-gorseller", "arka-kapak_tas-duvar-eskiz.png")
FONT = "Calibri"
PIL_FONT = "/usr/share/fonts/truetype/crosextra/Carlito-Regular.ttf"
PIL_FONT_B = "/usr/share/fonts/truetype/crosextra/Carlito-Bold.ttf"

SIYAH = RGBColor(0x3C, 0x3C, 0x3C)
GRI = RGBColor(0x7A, 0x7A, 0x7A)
ACIK_GRI = RGBColor(0xBF, 0xBF, 0xBF)
KIRMIZI = RGBColor(0xC0, 0x00, 0x00)

W_MM, H_MM = 420.0, 297.0
ML = 15.0          # sol/sağ kenar boşluğu (paftalarla aynı: 72 px / 2000 px * 420 mm)
MR = W_MM - ML

# Görsel bandı (şablon: sayfa genişliğinde, yüksekliğin ~%65'i, dikeyde ortalı)
BANT_ORAN = 1600 / 737          # 2.171 : 1  (konsept-02 ve konsept-05 ile aynı oran)
BANT_H = W_MM / BANT_ORAN       # 193.46 mm
BANT_Y = (H_MM - BANT_H) / 2    # 51.77 mm
# Kapak görseli (sol ~2/3)
KAPAK_W, KAPAK_H = 290.0, 200.0
KAPAK_Y = 30.0

ozet = json.load(open(os.path.join(BOYAMA, "kaynak", "era01_ozet.json"), encoding="utf-8"))
TOPLAM = ozet["toplam_kapali_alan"]

# ---------------------------------------------------------------- görseller
def kirp_oran(src, oran, hedef, odak_x=0.5, odak_y=0.5, maks_w=None):
    """src görselini oran (w/h) çerçevesine merkezden (odakla) kırpar, JPEG kaydeder."""
    im = Image.open(src).convert("RGB")
    w, h = im.size
    if w / h > oran:
        nw, nh = round(h * oran), h
    else:
        nw, nh = w, round(w / oran)
    x0 = round((w - nw) * odak_x)
    y0 = round((h - nh) * odak_y)
    im = im.crop((x0, y0, x0 + nw, y0 + nh))
    if maks_w and im.size[0] > maks_w:
        im = im.resize((maks_w, round(maks_w / oran)), Image.LANCZOS)
    im.save(hedef, quality=92, subsampling=0)
    return hedef


def yer_tutucu(hedef, oran, satirlar, px_w=2400):
    """İnce gri çerçeveli yer tutucu görsel (resim nesnesi olarak yerleşir, değiştirilebilir)."""
    px_h = round(px_w / oran)
    im = Image.new("RGB", (px_w, px_h), (238, 238, 238))
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, px_w - 1, px_h - 1), outline=(170, 170, 170), width=4)
    fb = ImageFont.truetype(PIL_FONT_B, round(px_w * 0.022))
    fr = ImageFont.truetype(PIL_FONT, round(px_w * 0.016))
    y = px_h / 2 - px_w * 0.03
    for i, s in enumerate(satirlar):
        f = fb if i == 0 else fr
        tw = d.textlength(s, font=f)
        d.text(((px_w - tw) / 2, y), s, font=f, fill=(120, 120, 120))
        y += px_w * (0.034 if i == 0 else 0.024)
    im.save(hedef, quality=92)
    return hedef


def pafta(ad):
    """Boyama paftasını 300 dpi'a (4961 px) küçültür; PPTX boyutu makul kalsın diye."""
    src = os.path.join(BOYAMA, ad)
    hedef = os.path.join(ARA, ad.replace(".jpg", "_300dpi.jpg"))
    if not os.path.exists(hedef) or os.path.getmtime(hedef) < os.path.getmtime(src):
        im = Image.open(src).convert("RGB")
        im.resize((4961, round(4961 * im.size[1] / im.size[0])), Image.LANCZOS).save(
            hedef, quality=85, subsampling=0)
    return hedef


R01 = os.path.join(RENDER, "ERA01_girdi_konsept-01_D-blok-sokak.webp")
R02 = os.path.join(RENDER, "ERA01_girdi_konsept-02_kus-bakisi-site.jpg")
R04 = os.path.join(RENDER, "ERA01_girdi_konsept-04_tek-katli-blok-teras.jpg")
R05 = os.path.join(RENDER, "ERA01_girdi_konsept-05_A-blok-havuz.jpg")

G = {}
G["kapak"] = kirp_oran(R01, KAPAK_W / KAPAK_H, os.path.join(GORSEL, "ERA01_sunum_G01_kapak.jpg"), odak_x=0.30)
G["site"] = kirp_oran(R02, BANT_ORAN, os.path.join(GORSEL, "ERA01_sunum_G02_site-kus-bakisi.jpg"))
G["A"] = kirp_oran(R05, BANT_ORAN, os.path.join(GORSEL, "ERA01_sunum_G03_A-blok.jpg"))
G["B"] = kirp_oran(R04, BANT_ORAN, os.path.join(GORSEL, "ERA01_sunum_G04_B-blok.jpg"), odak_y=0.45)
G["C"] = yer_tutucu(os.path.join(GORSEL, "ERA01_sunum_G05_C-blok_yer-tutucu.jpg"), BANT_ORAN,
                    ["GÖRSEL: C BLOK", "IFC tarafından eklenecek  (oran 2.17 : 1, 420 × 193.5 mm)"])
G["D"] = kirp_oran(R01, BANT_ORAN, os.path.join(GORSEL, "ERA01_sunum_G06_D-blok.jpg"), odak_x=0.35)
G["alan"] = yer_tutucu(os.path.join(GORSEL, "ERA01_sunum_G00_proje-alani_yer-tutucu.jpg"), 290 / 225,
                       ["PROJE ALANI: UYDU GÖRÜNTÜSÜ / KONUM HARİTASI", "IFC tarafından eklenecek  (oran 1.29 : 1, 290 × 225 mm)"])
G["eskiz"] = yer_tutucu(os.path.join(GORSEL, "ERA01_sunum_G07_atmosfer-eskizi_yer-tutucu.jpg"), W_MM / H_MM,
                        ["ATMOSFER ESKİZİ (KARAKALEM)", "IFC tarafından eklenecek  (tam sayfa, 420 × 297 mm)"])

# ---------------------------------------------------------------- pptx yardımcıları
prs = Presentation()
prs.slide_width = Mm(W_MM)
prs.slide_height = Mm(H_MM)
BOS = prs.slide_layouts[6]
SAYFALAR = []   # (no, başlık, içerik, görsel çerçevesi)


def font_ayarla(run, boyut, kalin=False, renk=SIYAH, aralik=None, hafif=False):
    f = run.font
    f.name = FONT
    f.size = Pt(boyut)
    f.bold = kalin
    f.color.rgb = renk
    rpr = run._r.get_or_add_rPr()
    for tag in ("a:ea", "a:cs"):
        el = rpr.find(qn(tag))
        if el is None:
            el = etree.SubElement(rpr, qn(tag))
        el.set("typeface", FONT)
    if aralik is not None:
        rpr.set("spc", str(int(aralik * 100)))
    rpr.set("lang", "tr-TR")


def metin(slide, x, y, w, h, satirlar, hiza=PP_ALIGN.LEFT, dikey=MSO_ANCHOR.TOP, ad=None,
          satir_arasi=None, iki_yana=False):
    """satirlar: [(metin, boyut, kalin, renk, aralik), ...] her biri ayrı paragraf."""
    tb = slide.shapes.add_textbox(Mm(x), Mm(y), Mm(w), Mm(h))
    if ad:
        tb.name = ad
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = dikey
    for i, s in enumerate(satirlar):
        yazi, boyut = s[0], s[1]
        kalin = s[2] if len(s) > 2 else False
        renk = s[3] if len(s) > 3 else SIYAH
        aralik = s[4] if len(s) > 4 else None
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = PP_ALIGN.JUSTIFY if iki_yana else hiza
        if satir_arasi:
            p.line_spacing = satir_arasi
        r = p.add_run()
        r.text = yazi
        font_ayarla(r, boyut, kalin, renk, aralik)
    return tb


def efekt_yok(shp):
    """Tema gölgesini kapatır (boş effectLst)."""
    spPr = shp._element.spPr
    if spPr.find(qn("a:effectLst")) is None:
        el = etree.SubElement(spPr, qn("a:effectLst"))
        ln = spPr.find(qn("a:ln"))
        if ln is not None:
            ln.addnext(el)
    style = shp._element.find(qn("p:style"))   # tema efekt referansı (gölge) kaldırılır
    if style is not None:
        shp._element.remove(style)


def cizgi(slide, x1, y1, x2, y2, kalinlik=0.75, renk=SIYAH, ad=None):
    ln = slide.shapes.add_connector(1, Mm(x1), Mm(y1), Mm(x2), Mm(y2))
    ln.line.width = Pt(kalinlik)
    ln.line.color.rgb = renk
    if ad:
        ln.name = ad
    efekt_yok(ln)
    return ln


def resim(slide, yol, x, y, w, h=None, ad=None):
    pic = slide.shapes.add_picture(yol, Mm(x), Mm(y), Mm(w), Mm(h) if h else None)
    if ad:
        pic.name = ad
    return pic


def ust_serit(slide, bolum):
    # Paftalarla aynı başlık düzeni (03-boyama paftaları: ERA01 / E R A  E V İ)
    metin(slide, ML, 12.2, 120, 8, [("ERA01", 16, True, SIYAH)], ad="UST_proje")
    metin(slide, ML, 19.0, 120, 8, [("ERA EVİ", 13, False, GRI, 6)], ad="UST_isveren")
    metin(slide, MR - 200, 12.0, 200, 8, [("MİMARİ KONSEPT PROJE", 15.5, False, SIYAH, 6.5)],
          hiza=PP_ALIGN.RIGHT, ad="UST_baslik")
    metin(slide, MR - 200, 19.4, 200, 8, [(bolum, 13, True, SIYAH)], hiza=PP_ALIGN.RIGHT, ad="UST_bolum")


def alt_serit(slide):
    lw = 57.5
    pic = resim(slide, LOGO, ML, 278.3, lw, ad="ALT_logo")
    cy = pic.top + pic.height  # logonun alt çizgisi
    cizgi(slide, ML + lw + 4.5, Emu(cy).mm - 0.6, W_MM * 0.85, Emu(cy).mm - 0.6, 0.6, ad="ALT_cizgi")


def yeni(bolum=None, serit=True):
    s = prs.slides.add_slide(BOS)
    bg = s.background.fill
    bg.solid()
    bg.fore_color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
    if serit:
        ust_serit(s, bolum)
        alt_serit(s)
    return s


def beyaz_gecis(slide, x, y, w, h, yon=0, ad=None):
    """Görselin kenarını beyaza eriten gradyan dikdörtgen (görselden ayrı şekil; maske değil).
    yon: 0 = soldan sağa (sağ kenar beyaz)."""
    shp = slide.shapes.add_shape(1, Mm(x), Mm(y), Mm(w), Mm(h))
    if ad:
        shp.name = ad
    shp.line.fill.background()
    spPr = shp._element.spPr
    for el in spPr.findall(qn("a:solidFill")):
        spPr.remove(el)
    grad = etree.fromstring(
        '<a:gradFill xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" rotWithShape="1">'
        '<a:gsLst><a:gs pos="0"><a:srgbClr val="FFFFFF"><a:alpha val="0"/></a:srgbClr></a:gs>'
        '<a:gs pos="100000"><a:srgbClr val="FFFFFF"/></a:gs></a:gsLst>'
        f'<a:lin ang="{yon * 60000}" scaled="0"/></a:gradFill>')
    geom = spPr.find(qn("a:prstGeom"))
    geom.addnext(grad)
    efekt_yok(shp)
    return shp


def kayit(slide, baslik, icerik, cerceve="-"):
    SAYFALAR.append((len(prs.slides), baslik, icerik, cerceve))


def bant_gorsel(slide, yol, ad):
    return resim(slide, yol, 0, BANT_Y, W_MM, BANT_H, ad=ad)


def pafta_sayfasi(dosya, baslik):
    s = prs.slides.add_slide(BOS)
    resim(s, pafta(dosya), 0, 0, W_MM, H_MM, ad="PAFTA_" + dosya.replace("ERA01_boyama_", "").replace(".jpg", ""))
    kayit(s, baslik, f"Pafta (PAFTA): 03-boyama/{dosya}")
    return s


# ---------------------------------------------------------------- 1 KAPAK
s = yeni(serit=False)
resim(s, G["kapak"], 0, KAPAK_Y, KAPAK_W, KAPAK_H, ad="GORSEL_G01_kapak")
beyaz_gecis(s, KAPAK_W - 45, KAPAK_Y - 0.5, 45.5, KAPAK_H + 1, ad="KAPAK_beyaz-gecis")
metin(s, 300, 166, 110, 80, [
    ("[İŞVEREN ADI]", 30, False, GRI),
    ("ERA EVİ", 20, True, SIYAH),
    ("", 12),
    ("MİMARİ KONSEPT PROJE", 16, False, SIYAH),
    ("KONUT PROJESİ", 13, False, SIYAH),
    (f"({TARIH})", 12, False, SIYAH),
], ad="KAPAK_metin", satir_arasi=1.05)
kayit(s, "KAPAK", "Konsept görsel (sol 2/3, sağ kenarı beyaza eriyen), işveren / proje adı / tarih",
      "G01 kapak: 290 × 200 mm (1.45 : 1)")

# ---------------------------------------------------------------- 2 İÇİNDEKİLER
s = yeni(bolum="")
tb = metin(s, 0, 0, 200, 40, [("İÇİNDEKİLER", 66, True, RGBColor(0x40, 0x40, 0x40))],
           dikey=MSO_ANCHOR.MIDDLE, ad="ICINDEKILER_baslik")
tb.rotation = 270
# döndürülmüş kutuyu yerleştir: merkez (x=120 mm, y=148 mm)
tb.left = Mm(120 - 100)
tb.top = Mm(150 - 20)
liste = ["PROJE BİLGİLERİ", "VAZİYET PLANI", "SİTE GÖRSELİ",
         "A BLOK: GÖRSEL VE KAT PLANLARI", "B BLOK: GÖRSEL VE KAT PLANLARI",
         "C BLOK: GÖRSEL VE KAT PLANLARI", "D BLOK: GÖRSEL VE KAT PLANLARI",
         "ALAN TABLOSU", "ATMOSFER ESKİZİ"]
metin(s, 160, 128, 220, 100, [("-     " + x, 18, False, SIYAH) for x in liste], ad="ICINDEKILER_liste",
      satir_arasi=1.15)
kayit(s, "İÇİNDEKİLER", "Dikey başlık + bölüm listesi")

# ---------------------------------------------------------------- 3 PROJE BİLGİLERİ
s = yeni(bolum="PROJE BİLGİLERİ")
resim(s, G["alan"], 0, 36, 290, 225, ad="GORSEL_G00_proje-alani")
px = 302
metin(s, px, 40, MR - px, 10, [("PROJE BİLGİLERİ", 14, True, SIYAH)], ad="BILGI_baslik")
bilgi = [
    ("LOKASYON", "Beykoz / İstanbul"),
    ("MAHALLE", "[DOLDURULACAK]"),
    ("ADA / PARSEL", "1366 ADA  45 PARSEL"),
    ("SOKAK", "Güller Sokak, Odak Çıkmazı Sokak"),
    ("ARSA ALANI", "[DOLDURULACAK] m²"),
    ("BLOK ADEDİ", "4 BLOK (A, B, C, D)"),
    ("BAĞIMSIZ BÖLÜM", "[DOLDURULACAK]"),
    ("TOPLAM KAPALI ALAN", f"{sum(TOPLAM.values()):.2f} m²"),
]
tb = s.shapes.add_textbox(Mm(px), Mm(49), Mm(MR - px), Mm(60))
tb.name = "BILGI_tablo"
tf = tb.text_frame
tf.word_wrap = True
tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
for i, (k, v) in enumerate(bilgi):
    p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
    p.space_after = Pt(2)
    r = p.add_run(); r.text = k + ": "; font_ayarla(r, 11, True)
    r = p.add_run(); r.text = v; font_ayarla(r, 11, False, KIRMIZI if "DOLDURULACAK" in v else SIYAH)
konsept = [
    "[DOLDURULACAK: Proje tanıtım / konsept metni. İşveren ve konsept fikirleri verildiğinde, ofisin "
    "önceki sunumlarındaki (Yavuzselim) metinle aynı dil, ton ve üslupta 3–4 paragraf olarak yazılacak.]",
    "[Paragraf 2: yerleşim ve topoğrafya kararları.]",
    "[Paragraf 3: blokların kurgusu, açık alanlar ve peyzaj.]",
    "[Paragraf 4: malzeme ve mimari dil.]",
]
tb = metin(s, px, 118, MR - px, 140, [(t, 11, False, GRI) for t in konsept], iki_yana=True,
           ad="BILGI_konsept-metni", satir_arasi=1.1)
for p in tb.text_frame.paragraphs:
    p.space_after = Pt(6)
kayit(s, "PROJE BİLGİLERİ", "Proje alanı görsel yer tutucusu, proje bilgileri, konsept metni [DOLDURULACAK]",
      "G00 proje alanı (yer tutucu): 290 × 225 mm (1.29 : 1)")

# ---------------------------------------------------------------- 4 VAZİYET
pafta_sayfasi("ERA01_boyama_vaziyet_v02.jpg", "VAZİYET PLANI")

# ---------------------------------------------------------------- 5 SİTE GÖRSELİ
s = yeni(bolum="SİTE GÖRSELİ")
bant_gorsel(s, G["site"], "GORSEL_G02_site-kus-bakisi")
kayit(s, "SİTE GÖRSELİ (KUŞ BAKIŞI)", "Sayfa genişliğinde görsel bandı", "G02 site: 420 × 193.5 mm (2.17 : 1)")

# ---------------------------------------------------------------- BLOKLAR
BLOK = {
    "A": dict(kat="1BK+Z+1N = 3 KAT", kot="±0.00 = 172.95", gorsel="G03",
              paftalar=[("A-blok-kat-planlari_v03", "KAT PLANLARI (TOPLU)"),
                        ("A-blok-1-bodrum_v02", "1. BODRUM KAT PLANI"),
                        ("A-blok-zemin-kat_v02", "ZEMİN KAT PLANI"),
                        ("A-blok-1-kat_v03", "1. KAT PLANI")]),
    "B": dict(kat="2BK+Z = 3 KAT", kot="±0.00 = 174.15", gorsel="G04",
              paftalar=[("B-blok-kat-planlari_v02", "KAT PLANLARI (TOPLU)"),
                        ("B-blok-2-bodrum_v02", "2. BODRUM KAT PLANI (OTOPARK)"),
                        ("B-blok-1-bodrum_v02", "1. BODRUM KAT PLANI"),
                        ("B-blok-zemin-kat_v02", "ZEMİN KAT PLANI")]),
    "C": dict(kat="1BK+Z = 2 KAT", kot="±0.00 = 174.36", gorsel="G05",
              paftalar=[("C-blok-kat-planlari_v02", "KAT PLANLARI (TOPLU)"),
                        ("C-blok-1-bodrum_v02", "1. BODRUM KAT PLANI"),
                        ("C-blok-zemin-kat_v02", "ZEMİN KAT PLANI")]),
    "D": dict(kat="1BK+Z+1N = 3 KAT", kot="±0.00 = 167.25", gorsel="G06",
              paftalar=[("D-blok-kat-planlari_v03", "KAT PLANLARI (TOPLU)"),
                        ("D-blok-1-bodrum_v02", "1. BODRUM KAT PLANI"),
                        ("D-blok-zemin-kat_v02", "ZEMİN KAT PLANI"),
                        ("D-blok-1-kat_v02", "1. KAT PLANI")]),
}
GORSEL_AD = {"A": "A-blok", "B": "B-blok", "C": "C-blok_yer-tutucu", "D": "D-blok"}
for b, d in BLOK.items():
    s = yeni(bolum=f"{b} BLOK")
    bant_gorsel(s, G[b], f"GORSEL_{d['gorsel']}_{b}-blok")
    yb = BANT_Y + BANT_H + 5
    tb = s.shapes.add_textbox(Mm(MR - 250), Mm(yb), Mm(250), Mm(16))
    tb.name = f"{b}_blok-ozet"
    tf = tb.text_frame; tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    p = tf.paragraphs[0]; p.alignment = PP_ALIGN.RIGHT
    r = p.add_run(); r.text = f"{b} BLOK"; font_ayarla(r, 16, True)
    r = p.add_run(); r.text = f"     {d['kat']}     {d['kot']}"; font_ayarla(r, 12, False, GRI)
    p = tf.add_paragraph(); p.alignment = PP_ALIGN.RIGHT
    r = p.add_run(); r.text = f"TOPLAM KAPALI ALAN : {TOPLAM[b]:.2f} m²"; font_ayarla(r, 14, True)
    kayit(s, f"{b} BLOK: GÖRSEL", f"Blok görseli + {d['kat']}, toplam kapalı alan {TOPLAM[b]:.2f} m²",
          f"{d['gorsel']} {b} blok: 420 × 193.5 mm (2.17 : 1)")
    for kod, ad in d["paftalar"]:
        pafta_sayfasi(f"ERA01_boyama_{kod}.jpg", f"{b} BLOK: {ad}")

# ---------------------------------------------------------------- ALAN TABLOSU
s = yeni(bolum="ALAN TABLOSU")
anahtarlar = [k for k in ozet if isinstance(ozet[k], dict) and "kat" in ozet[k]]
satirlar = []
for b in "ABCD":
    ks = [k for k in anahtarlar if ozet[k]["blok"] == b]
    for k in ks:
        o = ozet[k]
        satirlar.append(("kat", b, o["kat"].replace(" PLANI", ""), f"{o['kot']} ({o['mutlak']})",
                         o["net"], o["acik"], o["brut"]))
    satirlar.append(("ara", b, f"{b} BLOK TOPLAM KAPALI ALAN", "", sum(ozet[k]["net"] for k in ks),
                     sum(ozet[k]["acik"] for k in ks), TOPLAM[b]))
genel_brut = sum(TOPLAM.values())
genel_net = sum(ozet[k]["net"] for k in anahtarlar)
genel_acik = sum(ozet[k]["acik"] for k in anahtarlar)
zemin_alti = sum(ozet[k]["brut"] for k in anahtarlar if "BODRUM" in ozet[k]["kat"])
zemin_ustu = genel_brut - zemin_alti
satirlar.append(("genel", "", "GENEL TOPLAM", "", genel_net, genel_acik, genel_brut))

bas = ["BLOK", "KAT", "KOT (MUTLAK)", "NET ALAN (m²)", "AÇIK ALAN (m²)", "BRÜT ALAN (m²)"]
gen = [24, 92, 52, 42, 42, 42]  # mm
tx, ty = ML, 38.0
satir_h = 8.6
tbl_shape = s.shapes.add_table(len(satirlar) + 1, len(bas), Mm(tx), Mm(ty), Mm(sum(gen)),
                               Mm(satir_h * (len(satirlar) + 1)))
tbl_shape.name = "ALAN_tablosu"
tbl = tbl_shape.table
# varsayılan tablo stilini kaldır (sade, ince çizgili)
tblPr = tbl._tbl.tblPr
tblPr.set("firstRow", "0"); tblPr.set("bandRow", "0")
for el in tblPr.findall(qn("a:tableStyleId")):
    tblPr.remove(el)
for i, g in enumerate(gen):
    tbl.columns[i].width = Mm(g)


def hucre(c, yazi, boyut=9.5, kalin=False, hiza=PP_ALIGN.LEFT, dolgu=None, renk=SIYAH):
    c.text = ""
    tf = c.text_frame
    p = tf.paragraphs[0]; p.alignment = hiza
    r = p.add_run(); r.text = yazi; font_ayarla(r, boyut, kalin, renk)
    c.margin_left = c.margin_right = Mm(1.8)
    c.margin_top = c.margin_bottom = Mm(0.6)
    c.vertical_anchor = MSO_ANCHOR.MIDDLE
    tcPr = c._tc.get_or_add_tcPr()
    for el in list(tcPr):
        if el.tag in (qn("a:lnL"), qn("a:lnR"), qn("a:lnT"), qn("a:lnB"), qn("a:solidFill"), qn("a:noFill")):
            tcPr.remove(el)
    for kenar in ("a:lnL", "a:lnR", "a:lnT", "a:lnB"):
        ln = etree.SubElement(tcPr, qn(kenar), w=str(int(Pt(0.5))))
        sf = etree.SubElement(ln, qn("a:solidFill"))
        etree.SubElement(sf, qn("a:srgbClr"), val="9A9A9A")
    if dolgu:
        sf = etree.SubElement(tcPr, qn("a:solidFill"))
        etree.SubElement(sf, qn("a:srgbClr"), val=dolgu)
    else:
        etree.SubElement(tcPr, qn("a:noFill"))


for j, t in enumerate(bas):
    hucre(tbl.cell(0, j), t, 10, True, PP_ALIGN.LEFT if j < 3 else PP_ALIGN.RIGHT, "E6E6E6")
for i, (tip, b, kat, kot, net, acik, brut) in enumerate(satirlar, start=1):
    tbl.rows[i].height = Mm(satir_h)
    kalin = tip != "kat"
    dolgu = {"kat": None, "ara": "F2F2F2", "genel": "D9D9D9"}[tip]
    vals = [b if tip == "kat" else "", kat, kot, f"{net:.2f}", f"{acik:.2f}" if acik else "-", f"{brut:.2f}"]
    for j, v in enumerate(vals):
        hucre(tbl.cell(i, j), v, 11, kalin, PP_ALIGN.LEFT if j < 3 else PP_ALIGN.RIGHT, dolgu)
tbl.rows[0].height = Mm(satir_h)

# sağ özet
ox = 315
metin(s, ox, 40, MR - ox, 10, [("ÖZET", 14, True)], ad="ALAN_ozet-baslik")
oz = [("ZEMİN ALTI KAPALI ALAN (BODRUMLAR)", zemin_alti), ("ZEMİN ÜSTÜ KAPALI ALAN", zemin_ustu),
      ("TOPLAM KAPALI ALAN", genel_brut), ("AÇIK ALAN (TERAS / BALKON / KAT BAHÇESİ)", genel_acik)]
tb = s.shapes.add_textbox(Mm(ox), Mm(50), Mm(MR - ox), Mm(50)); tb.name = "ALAN_ozet"
tf = tb.text_frame; tf.word_wrap = True
tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
for i, (k, v) in enumerate(oz):
    p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
    p.space_after = Pt(5)
    r = p.add_run(); r.text = k + " : "; font_ayarla(r, 11, i == 2)
    r = p.add_run(); r.text = f"{v:.2f} m²"; font_ayarla(r, 11, True)
notlar = [
    "NOTLAR",
    "Brüt alan: terassız kapalı kat alanı, dıştan dışa (kat planı paftalarıyla aynı).",
    "Teras, balkon ve kat bahçesi AÇIK ALAN sütununda ayrı gösterilmiştir.",
    "A 1. kat brüt alanı: kat brütü 170.00 − kat bahçesi 24.96 = 145.04 m².",
    "D 1. kat brüt alanı DXF kat şemasından (129.77 m²); 82.70 m² teras ayrıdır.",
    "Kaynak: 03-boyama/kaynak/era01_ozet.json (PAFTA).",
    "İmar hesapları (emsal, TAKS/KAKS, arsa alanı): [DOLDURULACAK]",
]
tb = metin(s, ox, 112, MR - ox, 90, [(n, 10, i == 0, SIYAH if i == 0 else GRI) for i, n in enumerate(notlar)],
           ad="ALAN_notlar")
for p in tb.text_frame.paragraphs:
    p.space_after = Pt(3)
kayit(s, "ALAN TABLOSU", "Blok/kat net, açık ve brüt alanları; blok toplamları, genel toplam, zemin altı/üstü özeti")

# ---------------------------------------------------------------- ATMOSFER ESKİZİ
s = yeni(serit=False)
resim(s, G["eskiz"], 0, 0, W_MM, H_MM, ad="GORSEL_G07_atmosfer-eskizi")
kayit(s, "ATMOSFER ESKİZİ", "Tam sayfa karakalem eskiz (yer tutucu)", "G07 eskiz (yer tutucu): 420 × 297 mm (tam sayfa)")

# ---------------------------------------------------------------- ARKA KAPAK
s = yeni(serit=False)
im = Image.open(TAS_DUVAR); oran = im.size[0] / im.size[1]
dw = 105
resim(s, TAS_DUVAR, (W_MM - dw) / 2, 95, dw, ad="ARKA_tas-duvar")
dh = dw / oran
lw = 68
resim(s, LOGO, (W_MM - lw) / 2, 95 + dh + 14, lw, ad="ARKA_logo")
ly = 95 + dh + 14 + lw * 137 / 1504 + 10
iletisim = [("İLETİŞİM", 9.5, True)]
for t in ["Adres: Burhaniye Mah. Bahçeler Sk. No:4, 34676", "Üsküdar/İstanbul", "t: (0216) 362 17 02",
          "f: (0216) 362 17 03"]:
    iletisim.append((t, 9, False, GRI))
iletisim.append(("www.ifcmimarlik.com", 9, True))
tb = metin(s, (W_MM - 120) / 2, ly, 120, 40, iletisim, hiza=PP_ALIGN.CENTER, ad="ARKA_iletisim")
for p in tb.text_frame.paragraphs:
    p.space_after = Pt(2)
kayit(s, "ARKA KAPAK", "Taş duvar eskizi, IFC logosu, iletişim (ofis sabit sayfası)")

# ---------------------------------------------------------------- kaydet
cikti = os.path.join(SUNUM, f"ERA01_sunum_konsept-sunum_{SURUM}.pptx")
prs.save(cikti)
json.dump(SAYFALAR, open(os.path.join(BURADA, f"era01_sunum_sayfalar_{SURUM}.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print(cikti, len(prs.slides), "sayfa")
for r in SAYFALAR:
    print(r)
