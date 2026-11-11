# DNM01 konsept kat planlari v02 - DXF uretici (CIZGI)
# Temel: kullanicinin AutoCAD revizyonu (00-girdi/DNM01_girdi_kullanici-revizyon_v01r.dxf). Tefris kullanicinindir, geri alinmaz.
# Bu betik: (1) revizyon hatalarini duzeltir, (2) cati planini, (3) kesit A-A'yi ekler.
# Parametreler asagida (PENCERE, KAPI_H, KOTLAR, CATI, KESIT). Kullanici pencere yuksekliklerini degistirirse yalniz PENCERE tablosu degisir.
import json, sys, math
import ezdxf
from ezdxf import bbox
from ezdxf.enums import TextEntityAlignment
from ezdxf.math import Matrix44
from shapely.geometry import box, Polygon, LineString, Point
from shapely.ops import unary_union

ROOT = '/home/user/ifc-agents'
SRC = ROOT + '/projeler/DNM01/00-girdi/DNM01_girdi_kullanici-revizyon_v01r.dxf'
OUT = ROOT + '/projeler/DNM01/01-cizim/taslak/DNM01_cizim_kat-planlari_v02.dxf'
OUTJSON = sys.argv[1] if len(sys.argv) > 1 else '/tmp/dnm01_v02.json'

# =============================================================== PARAMETRELER
W, H = 1360, 1010                     # dis duvar dis cizgisi (cm)
KAT_ARALIGI = 1810                    # model alaninda katlar arasi Y
FLOORS = [('B', 'BODRUM KAT', -1810, -350), ('G', 'GİRİŞ KAT', 0, 0), ('K1', '1.KAT', 1810, 350)]
ROOF_DY = 3620                        # cati plani Y kaydirmasi
KAT_H = 350                           # dosemeden dosemeye
DOS_KAPLAMA, DOS_TASIYICI, DOS_TAVAN = 10, 30, 10   # doseme paketi 50
CATI_DOSEME_UST = 700                 # cati dosemesi ustu +7.00
TEMEL_TASIYICI = 30                   # bodrum taban (radye) - VARSAYIM
CEPHE_KAPLAMA = 20                    # dis duvar cizgisinin disinda (HACIM kurali)
SACAK = 50                            # cephe kaplamasi dis yuzunden
EGIM = 0.15                           # %15
CATI_PAKET = 20                       # metal kenet cati paketi (dusey)
# Pencereler: tip -> (parapet, yukseklik) cm. KULLANICIYA SORULUYOR; simdilik SEF varsayilanlari.
PENCERE = {
    'P1': (0, 300),    # mutfak (guney)            - salon/mutfak: tavana kadar
    'P2': (0, 300),    # salon yemek (guney)
    'P3': (0, 300),    # salon (dogu)
    'P4': (0, 300),    # salon oturma (dogu)
    'P5': (90, 210),   # yatak odasi 1
    'P6': (90, 210),   # yatak odasi 2
    'P7': (90, 210),   # yatak odasi 3
    'P8': (0, 300),    # ebeveyn yatak odasi
    'P9': (150, 150),  # hol
    'P10': (150, 150), # ebeveyn banyosu
    'P11': (150, 150), # giyinme
}
KAPI_H = {'ic': 220, 'ana': 250, 'aciklik': 220}   # kapisiz aciklik: ic kapi yuksekligi (VARSAYIM)
# Kesit hatti A-A (kirik): x=75 kuzey parca (merdiven), y=600'de kirilir, x=420 guney parca (mutfak P1 / yatak 2 P6). Bakis: dogu (+x)
KESIT_PTS = [(75, 1240), (75, 600), (420, 600), (420, -240)]
KESIT_SEG = [(75, 600, 1010 + 100), (420, -100, 600)]   # (x, y0, y1)
SX0 = 2700                                                # kesit cizimi model X baslangici (u=0)

# =============================================================== GEOMETRI (v01 ile ayni; kullanici duvarlari degistirmedi)
RING = box(0, 0, W, H).difference(box(20, 20, W - 20, H - 20))
COLUMNS = [box(*r) for r in [(0, 0, 40, 20), (1320, 0, 1360, 20), (0, 990, 40, 1010), (1320, 990, 1360, 1010),
                             (655, 0, 695, 20), (655, 990, 695, 1010), (0, 505, 20, 545), (1340, 505, 1360, 545)]]
LIFT_WALLS = [(290, 710, 430, 720), (290, 720, 300, 870), (420, 720, 430, 870), (290, 870, 430, 880)]
WALLS = {
    'B': LIFT_WALLS,
    'G': [(20, 530, 670, 540), (670, 20, 680, 990), (130, 655, 300, 665), (130, 665, 140, 880),
          (290, 665, 300, 880), (130, 870, 430, 880), (290, 710, 430, 720), (420, 720, 430, 870)],
    'K1': [(290, 20, 300, 880), (20, 655, 290, 665), (130, 665, 140, 880), (130, 870, 430, 880),
           (300, 710, 430, 720), (420, 720, 430, 870), (300, 555, 1015, 565), (490, 330, 500, 555),
           (490, 330, 810, 340), (645, 20, 655, 555), (800, 340, 810, 555), (1005, 20, 1015, 555),
           (905, 565, 915, 990), (580, 675, 1340, 685), (580, 685, 590, 990), (690, 685, 700, 845),
           (590, 835, 690, 845)],
}
WINDOWS = {  # (cephe, a0, a1, tip, mahal)
    'B': [],
    'G': [('S', 225, 465, 'P1', 'Mutfak'), ('S', 760, 1260, 'P2', 'Salon (yemek)'),
          ('E', 100, 450, 'P3', 'Salon (yemek)'), ('E', 600, 900, 'P4', 'Salon (oturma)')],
    'K1': [('S', 80, 230, 'P5', 'Yatak odası 1'), ('S', 380, 560, 'P6', 'Yatak odası 2'),
           ('S', 740, 920, 'P7', 'Yatak odası 3'), ('S', 1060, 1300, 'P8', 'Ebeveyn yatak odası'),
           ('N', 455, 555, 'P9', 'Hol'), ('N', 705, 805, 'P10', 'Ebeveyn banyosu'),
           ('N', 1110, 1230, 'P11', 'Giyinme odası')],
}
DOORS = {  # (genislik, rect x0,y0,x1,y1, tur, yer)
    'B': [],
    'G': [(100, (525, 990, 625, 1010), 'ana', 'Ana giriş (kuzey)'), (90, (315, 530, 405, 540), 'ic', 'Hol -> Mutfak'),
          (80, (185, 655, 265, 665), 'ic', 'Hol -> WC')],
    'K1': [(90, (290, 565, 300, 655), 'ic', 'Hol -> Yatak odası 1'), (80, (185, 655, 265, 665), 'ic', 'Yatak odası 1 -> Banyo 1'),
           (90, (395, 555, 485, 565), 'ic', 'Hol -> Yatak odası 2'), (80, (510, 330, 590, 340), 'ic', 'Yatak odası 2 -> Banyo 2'),
           (80, (710, 330, 790, 340), 'ic', 'Yatak odası 3 -> Banyo 3'), (90, (815, 555, 905, 565), 'ic', 'Hol -> Yatak odası 3'),
           (90, (905, 575, 915, 665), 'ic', 'Hol -> Ebeveyn yatak odası'), (90, (1095, 675, 1185, 685), 'ic', 'Ebeveyn -> Giyinme'),
           (80, (905, 785, 915, 865), 'ic', 'Giyinme -> Ebeveyn banyosu')],
}
LIFT_DOOR = (320, 710, 400, 720)
EXTRA_OPEN = {'B': [LIFT_DOOR], 'G': [LIFT_DOOR, (670, 165, 680, 365), (670, 550, 680, 670)], 'K1': [LIFT_DOOR, (690, 715, 700, 795)]}
# doseme bosluklari (merdiven + asansor kuyusu), doseme kotuna gore
LIFT_VOID = box(300, 720, 420, 870)
SLAB_VOID = {
    0: unary_union([box(20, 637, 130, 880), box(20, 880, 427, 990), LIFT_VOID]),     # giris doseme: bodrum merdiveni
    350: unary_union([box(20, 665, 130, 880), box(20, 880, 427, 990), LIFT_VOID]),   # 1.kat doseme: merdiven boslugu
    700: LIFT_VOID.buffer(0),   # cati dosemesi: asansor kuyusu (lift ust kotu - VARSAYIM: kuyu cati dosemesine kadar)
}
# merdiven (plan geometrisinden): kol 1 x 20..130 y 637->880 (9 basamak 27), donus 3 balkabagi, kol 2 x 130..427 (11 basamak)
ST_Y0, ST_G, ST_N1 = 637, 27, 9
ST_RISERS = 24
ST_R = KAT_H / ST_RISERS

# =============================================================== DOKUMAN
doc = ezdxf.readfile(SRC)
msp = doc.modelspace()
doc.header['$INSUNITS'] = 5
log = []   # degisiklik listesi

def ensure_layer(name, color, linetype='Continuous'):
    if name not in doc.layers:
        doc.layers.add(name, color=color, linetype=linetype)
        log.append(f'Yeni katman {name} (ACI {color}, {linetype})')

if 'DASHDOT' not in doc.linetypes:
    doc.linetypes.add('DASHDOT', pattern=[100.0, 60.0, -15.0, 0.0, -15.0], description='Kesit hatti __ . __')
ensure_layer('0_IFC_Dimension', 3)
ensure_layer('2_IFC_Roof', 30)                 # cati sacak dis cizgisi / kesitte cati paketi (0.30)
ensure_layer('2_IFC_Roof_Line', 41)            # mahya, kirma, gorunen cati siluet (0.20)
ensure_layer('2_IFC_Roof_Hidden', 252, 'HIDDEN')   # cati altinda kalan dis duvar / cephe kaplamasi (0.05, kesikli)
ensure_layer('0_IFC_Section_Line', 10, 'DASHDOT')  # kesit hatti (0.25)
ensure_layer('7_IFC_Terrain', 42)              # tabii zemin cizgisi (0.30)
ensure_layer('0_IFC_Hatch', 250)

# --------------------------------------------------------------- yardimcilar
def rect_pts(x0, y0, x1, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]

def pline(pts, layer, close=False, dy=0, dx=0, **kw):
    return msp.add_lwpolyline([(p[0] + dx, p[1] + dy) for p in pts], close=close, dxfattribs={'layer': layer, **kw})

def mtext(txt, x, y, h, layer, attach=5, rot=0, width=None):
    m = msp.add_mtext(txt, dxfattribs={'layer': layer, 'style': 'IFC_TEXT', 'char_height': h, 'attachment_point': attach, 'rotation': rot})
    m.dxf.insert = (x, y)
    if width:
        m.dxf.width = width
    return m

def ins(name, x, y, rot=0, sx=1, sy=1, layer='0'):
    return msp.add_blockref(name, (x, y), dxfattribs={'layer': layer, 'rotation': rot, 'xscale': sx, 'yscale': sy})

def polys(g):
    if g.is_empty:
        return []
    if g.geom_type == 'Polygon':
        return [g]
    return [p for p in getattr(g, 'geoms', []) if p.geom_type == 'Polygon']

def add_poly_outline(poly, layer, dx=0, dy=0):
    pline([(round(x, 3), round(y, 3)) for x, y in list(poly.exterior.coords)[:-1]], layer, close=True, dx=dx, dy=dy)
    for ring in poly.interiors:
        pline([(round(x, 3), round(y, 3)) for x, y in list(ring.coords)[:-1]], layer, close=True, dx=dx, dy=dy)

def hatch_poly(poly, layer, pattern='SOLID', scale=1.0, angle=0, dx=0, dy=0, color=256):
    h = msp.add_hatch(color=color, dxfattribs={'layer': layer})
    if pattern != 'SOLID':
        h.set_pattern_fill(pattern, scale=scale, angle=angle)
    h.paths.add_polyline_path([(x + dx, y + dy) for x, y in list(poly.exterior.coords)[:-1]], is_closed=True, flags=1)
    for ring in poly.interiors:
        h.paths.add_polyline_path([(x + dx, y + dy) for x, y in list(ring.coords)[:-1]], is_closed=True, flags=0)
    return h

DA = {'layer': '0_IFC_Dimension'}
OV = {'dimclrd': 0, 'dimclre': 0}

def dim_chain(pts, base, horizontal=True):
    pts = sorted(set(pts))
    if horizontal:
        msp.add_multi_point_linear_dim(base=base, points=pts, dimstyle='IFC_Dim100', override=OV, dxfattribs=DA)
    else:
        msp.add_multi_point_linear_dim(base=base, points=pts, angle=90, dimstyle='IFC_Dim100', override=OV, dxfattribs=DA)

def kot_mark(x, y, txt, side=1, layer_txt='0_IFC_Text_Explanation_100', h=15, length=70):
    """Kot isareti: ucu (x,y)'de asagi bakan ucgen + yatay cizgi + yazi. side=+1 saga, -1 sola."""
    pline([(x - 10, y + 15), (x + 10, y + 15), (x, y)], '0_IFC_Elevation_5', close=True)
    pline([(x, y + 15), (x + side * length, y + 15)], '0_IFC_Elevation_5')
    mtext(txt, x + side * 14, y + 30, h, layer_txt, attach=7 if side > 0 else 9)

def kot_str(z):
    v = z / 100
    if abs(v) < 0.005:
        return '±0.00'
    return f'{v:+.2f}'

# =============================================================== 1. REVIZYON DUZELTMELERI
def del_where(pred):
    n = 0
    for e in list(msp):
        if pred(e):
            msp.delete_entity(e); n += 1
    return n

def line_in(e, layer, x0, y0, x1, y1):
    if e.dxftype() != 'LINE' or e.dxf.layer != layer:
        return False
    s, t = e.dxf.start, e.dxf.end
    return all(x0 - 1 <= p.x <= x1 + 1 and y0 - 1 <= p.y <= y1 + 1 for p in (s, t))

# 1a. dogrulama: duvarlar v01 ile ayni mi (2_IFC_Wall polyline sayisi)
assert len(msp.query('LWPOLYLINE[layer=="2_IFC_Wall"]')) == 42

# 1b. mutfak tezgahi: *E102 (dis duvar disina tasan, yalniz wipeout) + *E103 + patlatilmis 8 LINE -> IFC_MUTFAK TEZGAH bloklari
n1 = del_where(lambda e: e.dxftype() == 'INSERT' and e.dxf.name in ('*E102', '*E103'))
n2 = del_where(lambda e: line_in(e, '6_IFC_Furniture_WC', 20, 80, 297.3, 530))
assert (n1, n2) == (2, 8), (n1, n2)
ins('IFC_MUTFAK TEZGAH', 20, 530, rot=0, sx=280 / 200)     # kuzey (hol duvari) tezgah x 20..300, y 470..530 (kullanici 297.3 -> 300)
ins('IFC_MUTFAK TEZGAH', 80, 470, rot=270, sx=390 / 200)   # bati tezgah x 20..80, y 80..470
log.append('Mutfak: dis duvarin disina tasan *E102 tezgah kaldirildi; kullanicinin cizdigi L tezgah (bati duvari y 80-470 ve '
           'hol duvari onu x 20-300) IFC_MUTFAK TEZGAH bloguyla yeniden kuruldu (kuzey tezgah ucu 297.3 -> 300)')

# 1c. patlatilmis dolaplar -> IFC_WARDROBE
WARD = [  # (anon blok, kutu x0,y0,x1,y1 dunya, ekleme x,y, rot, boy, yer)
    ('*E88', (945, 1830, 1005, 2365), 1005, 2365, 270, 535, 'Yatak odası 3 (doğu duvarı)'),
    ('*E89', (300, 1830, 360, 2365), 300, 1830, 90, 535, 'Yatak odası 2 (batı duvarı)'),
    ('*E90', (20, 2122.7, 80, 2465), 80, 2465, 270, 340, 'Yatak odası 1 (batı duvarı; 342.3 -> 340)'),
]
for anon, bx, x, y, rot, L, yer in WARD:
    a = del_where(lambda e: e.dxftype() == 'INSERT' and e.dxf.name == anon)
    b = del_where(lambda e: line_in(e, '6_IFC_Furniture', *bx))
    assert a == 1 and b == 5, (anon, a, b)
    ins('IFC_WARDROBE', x, y, rot=rot, sx=L / 100)
    log.append(f'Dolap {yer}: patlatilmis 5 LINE + {anon} -> IFC_WARDROBE, boy {L} cm')

# 1d. kullanici bloklari: katman 6_IFC_Furniture uzerine eklenmis 3 insert -> katman 0 (standart); lamba blogundaki bozuk hatch kotu
for e in msp.query('INSERT[layer=="6_IFC_Furniture"]'):
    e.dxf.layer = '0'
for bn in ('A$Ced7b49cd',):
    blk = doc.blocks.get(bn)
    for e in blk:
        if e.dxf.layer == '0':
            e.dxf.layer = '6_IFC_Furniture'
        if e.dxftype() == 'HATCH':
            e.dxf.elevation = (0, 0, 0)
log.append('Kullanici bloklari (koltuk x2, lambader) katman 0 uzerine alindi; lambader blogunun ici 6_IFC_Furniture, bozuk hatch kotu (z=-159658) sifirlandi')

# 1e. mahal yazilari: BANYO 2 / BANYO 3 yazilari ust uste biniyordu -> mahal ortasina
for e in msp.query('INSERT[name=="0_IFC_ROOM_TEXT_50"]'):
    nm = {a.dxf.tag: a.dxf.text for a in e.attribs}.get('ROOM_NAME')
    if nm in ('BANYO 2', 'BANYO 3'):
        dxs = {'BANYO 2': 572.5 - 617, 'BANYO 3': 727.5 - 683}[nm]
        e.translate(dxs, 0, 0)
log.append('BANYO 2 ve BANYO 3 yazilari birbirine degiyordu; mahal ortalarina (x 572.5 / 727.5) kaydirildi')
RELABEL = {  # ad: (x, y (kat icinde, yazi merkezi), olcek) - yeni dolap/yatak yerlerine gore bos alana
    'YATAK ODASI 1': (185, None, 1.4), 'YATAK ODASI 2': (425, 380, 0.9), 'YATAK ODASI 3': (877.5, 380, 0.9),
    'EBEVEYN YATAK ODASI': (1177.5, None, 1.4),
}
for e in list(msp.query('INSERT[name=="0_IFC_ROOM_TEXT_50"]')):
    nm = e.get_attrib_text('ROOM_NAME')
    if nm in RELABEL and e.dxf.insert.y > 1500:
        s0 = e.dxf.xscale
        ax, ay = e.dxf.insert.x, e.dxf.insert.y - 24.8 * s0
        nx, ny, s1 = RELABEL[nm]
        ny = ay if ny is None else ny + 1810
        e.transform(Matrix44.chain(Matrix44.translate(-ax, -ay, 0), Matrix44.scale(s1 / s0, s1 / s0, 1), Matrix44.translate(nx, ny, 0)))
log.append('1. kat: YATAK ODASI 1/2/3 ve EBEVEYN YATAK ODASI yazilari yeni dolap ve yatak yerleriyle cakisiyordu; mahal icinde bos alana alindi')

# 1f. pencere bloklarina PARAPET ozniteligi + YUKSEKLIK guncelle
for blk in doc.blocks:
    if blk.name.startswith('IFC_PENCERE_') and not any(e.dxftype() == 'ATTDEF' and e.dxf.tag == 'PARAPET' for e in blk):
        w = int(blk.name.split('_')[-1])
        a = blk.add_attdef('PARAPET', (w / 2, -80), dxfattribs={'layer': '0_IFC_Window_Text', 'height': 12, 'style': 'IFC_TEXT', 'flags': 1})
        a.dxf.text = '0'
        a.set_placement((w / 2, -80), align=TextEntityAlignment.MIDDLE_CENTER)
for e in msp.query('INSERT'):
    if e.dxf.name.startswith('IFC_PENCERE_'):
        tip = e.get_attrib_text('TİP')
        p, h = PENCERE[tip]
        e.get_attrib('YUKSEKLIK').dxf.text = str(h)
        if not e.has_attrib('PARAPET'):
            yk = e.get_attrib('YUKSEKLIK')
            at = e.add_attrib('PARAPET', str(p), insert=yk.dxf.insert, dxfattribs={'layer': '0_IFC_Window_Text', 'height': 12, 'style': 'IFC_TEXT', 'rotation': yk.dxf.rotation})
            at.dxf.flags = 1
        else:
            e.get_attrib('PARAPET').dxf.text = str(p)
log.append('Pencere bloklarina gizli PARAPET ozniteligi eklendi; YUKSEKLIK degerleri kesit varsayimlarina guncellendi')

# =============================================================== 2. KESIT HATTI (giris ve 1.kat planlarinda)
def section_mark(dy):
    L = '0_IFC_Section_Line'
    pline([(x, y) for x, y in KESIT_PTS], L, dy=dy, ltscale=1.0)
    # uclarda kalin kisa cizgi + bakis oku (dogu)
    for (x, y), sgn in ((KESIT_PTS[0], 1), (KESIT_PTS[-1], -1)):
        pline([(x, y - sgn * 60), (x, y)], L, dy=dy, linetype='Continuous', const_width=6)
        pline([(x, y), (x + 55, y)], L, dy=dy, linetype='Continuous', const_width=3)
        pline([(x + 55, y + 12), (x + 80, y), (x + 55, y - 12)], L, close=True, dy=dy, linetype='Continuous')
        mtext('A', x - 30, y + dy, 30, '0_IFC_Stair_Text', attach=5)

for _k, _n, dy, _z in FLOORS[1:]:
    section_mark(dy)
log.append('Kesit A-A hatti giris kat ve 1. kat planlarina islendi')

# =============================================================== 3. CATI PLANI
E0, E1 = -CEPHE_KAPLAMA - SACAK, W + CEPHE_KAPLAMA + SACAK          # -70 .. 1430
N0, N1 = -CEPHE_KAPLAMA - SACAK, H + CEPHE_KAPLAMA + SACAK          # -70 .. 1080
half = min(E1 - E0, N1 - N0) / 2                                    # 575
RIDGE_Y = (N0 + N1) / 2
RIDGE_X0, RIDGE_X1 = E0 + half, E1 - half
RISE = EGIM * half
Z_SACAK_ALT = CATI_DOSEME_UST                 # egim sacak ucundan baslar: sacak ucu alt = cati dosemesi ustu
Z_SACAK_UST = Z_SACAK_ALT + CATI_PAKET
Z_MAHYA_ALT = Z_SACAK_ALT + RISE
Z_MAHYA_UST = Z_SACAK_UST + RISE

def roof_plan():
    dy = ROOF_DY
    pline(rect_pts(E0, N0, E1, N1), '2_IFC_Roof', close=True, dy=dy)
    pline(rect_pts(E0 + 4, N0 + 4, E1 - 4, N1 - 4), '2_IFC_Roof_Line', close=True, dy=dy)   # oluk / saçak ucu profili
    pline([(RIDGE_X0, RIDGE_Y), (RIDGE_X1, RIDGE_Y)], '2_IFC_Roof_Line', dy=dy)
    for c, r in (((E0, N0), (RIDGE_X0, RIDGE_Y)), ((E0, N1), (RIDGE_X0, RIDGE_Y)), ((E1, N0), (RIDGE_X1, RIDGE_Y)), ((E1, N1), (RIDGE_X1, RIDGE_Y))):
        pline([c, r], '2_IFC_Roof_Line', dy=dy)
    pline(rect_pts(0, 0, W, H), '2_IFC_Roof_Hidden', close=True, dy=dy, ltscale=0.5)
    pline(rect_pts(-CEPHE_KAPLAMA, -CEPHE_KAPLAMA, W + CEPHE_KAPLAMA, H + CEPHE_KAPLAMA), '2_IFC_Roof_Hidden', close=True, dy=dy, ltscale=0.5)
    # egim oklari (asagi yonde) + %15
    T = '0_IFC_Text_Explanation_100'
    def arrow(x0, y0, x1, y1, tx, ty, rot):
        pline([(x0, y0), (x1, y1)], T, dy=dy)
        ang = math.atan2(y1 - y0, x1 - x0)
        a1 = (x1 - 22 * math.cos(ang - 0.35), y1 - 22 * math.sin(ang - 0.35))
        a2 = (x1 - 22 * math.cos(ang + 0.35), y1 - 22 * math.sin(ang + 0.35))
        pline([a1, (x1, y1), a2], T, close=True, dy=dy)
        mtext('%15', tx, ty + dy, 20, T, attach=5, rot=rot)
    arrow(680, 400, 680, 120, 715, 260, 90)        # guney yuzu
    arrow(680, 610, 680, 890, 715, 750, 90)        # kuzey yuzu
    arrow(300, 505, 60, 505, 180, 535, 0)          # bati yuzu
    arrow(1060, 505, 1300, 505, 1180, 535, 0)      # dogu yuzu
    mtext('MAHYA', (RIDGE_X0 + RIDGE_X1) / 2, RIDGE_Y + 22 + dy, 16, T)
    mtext('METAL KENET ÇATI KAPLAMASI\\P4 YÖNE KIRMA ÇATI, EĞİM %15\\PSAÇAK 50 cm (cephe kaplaması dış yüzünden)\\PÇATI ARASI MAHAL OLARAK KULLANILMAZ',
          E0, -250 + dy, 16, T, attach=1)
    mtext('kesikli: dış duvar (iç) ve cephe kaplaması (dış) çizgisi', 680, 25 + dy, 12, T, attach=5)
    kot_mark(1180, 1080 + dy, f'SAÇAK UCU {kot_str(Z_SACAK_UST)} (kaplama üstü) / {kot_str(Z_SACAK_ALT)} (alt)', side=1, h=14, length=60)
    kot_mark(RIDGE_X1 - 40, RIDGE_Y + 50 + dy, f'MAHYA {kot_str(Z_MAHYA_UST)}', side=1, h=14, length=60)
    # olculer
    dim_chain([(x, N0 + dy) for x in (E0, -CEPHE_KAPLAMA, 0, W, W + CEPHE_KAPLAMA, E1)], (0, N0 - 100 + dy))
    msp.add_linear_dim(base=(0, N0 - 160 + dy), p1=(E0, N0 + dy), p2=(E1, N0 + dy), dimstyle='IFC_Dim100', override=OV, dxfattribs=DA).render()
    dim_chain([(E0, y + dy) for y in (N0, -CEPHE_KAPLAMA, 0, H, H + CEPHE_KAPLAMA, N1)], (E0 - 100, dy), horizontal=False)
    msp.add_linear_dim(base=(E0 - 160, dy), p1=(E0, N0 + dy), p2=(E0, N1 + dy), angle=90, dimstyle='IFC_Dim100', override=OV, dxfattribs=DA).render()
    dim_chain([(x, N1 + dy) for x in (E0, RIDGE_X0, RIDGE_X1, E1)], (0, N1 + 100 + dy))
    # baslik
    mtext('ÇATI PLANI', W, -320 + dy, 56.25, '0_IFC_Stair_Text', attach=3)
    mtext(f'SAÇAK {kot_str(Z_SACAK_UST)}   MAHYA {kot_str(Z_MAHYA_UST)}   ÇATI İZDÜŞÜM ALANI {(E1-E0)*(N1-N0)/1e4:.2f} m²', W, -395 + dy, 20, T, attach=3)
    cx, cy = 1640, 880
    msp.add_circle((cx, cy + dy), 40, dxfattribs={'layer': T})
    pline([(cx, cy + 50), (cx - 18, cy - 30), (cx, cy - 15), (cx + 18, cy - 30)], T, close=True, dy=dy)
    mtext('K', cx, cy + 80 + dy, 25, T)

roof_plan()
log.append(f'Cati plani eklendi (Y +{ROOF_DY}): sacak dis cizgisi {E1-E0}x{N1-N0}, mahya {RIDGE_X1-RIDGE_X0} cm, 4 kirma, egim oklari, kotlar')

# =============================================================== 4. KESIT A-A
def U(y):          # plan y -> kesit yatay (bakis doguya: kuzey solda)
    return H - y

def X(u):
    return SX0 + u

def to_model(poly):
    from shapely.affinity import translate
    return translate(poly, xoff=SX0)

def cut_intervals(geom, c, y0, y1):
    g = geom.intersection(LineString([(c, y0), (c, y1)]))
    out = []
    for part in ([g] if g.geom_type == 'LineString' else list(getattr(g, 'geoms', []))):
        if part.geom_type == 'LineString' and part.length > 0.5:
            ys = [p[1] for p in part.coords]
            out.append((min(ys), max(ys)))
    return sorted(out)

def opening_at(key, c, ym):
    pt = Point(c, ym)
    for (side, a0, a1, tip, _m) in WINDOWS[key]:
        r = {'S': box(a0, 0, a1, 20), 'N': box(a0, H - 20, a1, H), 'W': box(0, a0, 20, a1), 'E': box(W - 20, a0, W, a1)}[side]
        if r.buffer(0.01).contains(pt):
            p, h = PENCERE[tip]
            return ('P', p, h, tip)
    for (_w, r, tur, _yer) in DOORS[key]:
        if box(*r).buffer(0.01).contains(pt):
            return ('K', 0, KAPI_H[tur], _yer)
    for r in EXTRA_OPEN[key]:
        if box(*r).buffer(0.01).contains(pt):
            return ('A', 0, KAPI_H['aciklik'], 'açıklık')
    return None

conc = []        # kesilen tasiyici (u,z) poligonlari
thin = []        # doseme kaplama / tavan bantlari
win_cut = []     # (u0,u1,z0,z1,tip)
door_cut = []
clad_open = {'N': [], 'S': []}
cut_report = []
FLOOR_TOP = {'B': -40, 'G': 350 - 40, 'K1': CATI_DOSEME_UST - 40}   # duvar ustu = ust doseme tasiyici alti
for key, fname, dy, f in FLOORS:
    walls = unary_union([RING] + [box(*r) for r in WALLS[key]] + COLUMNS)
    z0 = f - DOS_KAPLAMA
    z1 = FLOOR_TOP[key]
    if key == 'B':
        z0 = f - DOS_KAPLAMA - TEMEL_TASIYICI
    for (c, y0, y1) in KESIT_SEG:
        for (ya, yb) in cut_intervals(walls, c, max(y0, 0), min(y1, H)):
            op = opening_at(key, c, (ya + yb) / 2)
            ua, ub = U(yb), U(ya)
            if op is None:
                conc.append(box(ua, z0, ub, z1))
                continue
            kind, p, h, tip = op
            if p > 0:
                conc.append(box(ua, z0, ub, f + p))
            conc.append(box(ua, f + p + h, ub, z1))
            if kind == 'P':
                win_cut.append((ua, ub, f + p, f + p + h, tip))
                face = 'S' if yb <= 20.01 else 'N' if ya >= H - 20.01 else None
                if face:
                    clad_open[face].append((f + p, f + p + h))
            else:
                door_cut.append((ua, ub, f, f + h, tip))
            cut_report.append(f'{fname}: {tip} kesitte (parapet {p}, h {h})')

# dosemeler
LEVELS = [(-350, 'radye'), (0, 'doseme'), (350, 'doseme'), (CATI_DOSEME_UST, 'cati')]
interior = box(20, 20, W - 20, H - 20)
for zf, tur in LEVELS:
    void = SLAB_VOID.get(zf, Polygon())
    slab_area = box(0, 0, W, H).difference(void) if tur != 'radye' else box(0, 0, W, H)
    for (c, y0, y1) in KESIT_SEG:
        for (ya, yb) in cut_intervals(slab_area, c, max(y0, 0), min(y1, H)):
            if tur == 'radye':
                conc.append(box(U(yb), zf - DOS_KAPLAMA - TEMEL_TASIYICI, U(ya), zf - DOS_KAPLAMA))
            else:
                conc.append(box(U(yb), zf - DOS_KAPLAMA - DOS_TASIYICI, U(ya), zf - DOS_KAPLAMA))
        # kaplama (ust 10) ve tavan (alt 10): ic mahallerde
        for (ya, yb) in cut_intervals(interior.intersection(slab_area), c, max(y0, 0), min(y1, H)):
            thin.append(box(U(yb), zf - DOS_KAPLAMA, U(ya), zf))
            if tur != 'radye':
                thin.append(box(U(yb), zf - 50, U(ya), zf - 40))

# merdivenler (x=75 kuzey parca): kol 1 kesilir, balkabagi T1/T2 kesilir, kol 2 gorunur
stair_vis = []
rail_vis = []
def stair_poly(zb):
    r = ST_R
    pts = [(ST_Y0, zb)]
    for k in range(1, ST_N1 + 1):
        pts += [(ST_Y0 + ST_G * (k - 1), zb + k * r), (ST_Y0 + ST_G * k, zb + k * r)]
    yT = 880 + (130 - 75) / 110 * 45          # x=75'te 1. balkabagi siniri (902.5)
    pts += [(880, zb + 10 * r), (yT, zb + 10 * r), (yT, zb + 11 * r), (990, zb + 11 * r), (990, zb + ST_N1 * r - 20), (880, zb + ST_N1 * r - 20)]
    slope = r / ST_G
    y_start = 880 - ((ST_N1 * r - 20) - (-DOS_KAPLAMA)) / slope
    pts += [(y_start, zb - DOS_KAPLAMA), (ST_Y0, zb - DOS_KAPLAMA)]
    return Polygon([(U(y), z) for y, z in pts])

for zb in (-350, 0):
    conc.append(stair_poly(zb))
    # gorunen: balkabagi T3 (12) ve kol 2 (13..23) - y 880..990 arasinda yatay basamak cizgileri
    for k in range(12, ST_RISERS):
        stair_vis.append([(U(990), zb + k * ST_R), (U(880), zb + k * ST_R)])
    stair_vis.append([(U(990), zb + 11 * ST_R), (U(990), zb + KAT_H)])
    # korkuluk (acik kenar x=130, gorunen): basamak burnu + 90
    rail_vis.append([(U(ST_Y0), zb + ST_R + 90), (U(880), zb + ST_N1 * ST_R + 90)])

CONC = unary_union([p.buffer(0) for p in conc])
for p in polys(CONC):
    add_poly_outline(to_model(p), '1_IFC_Concrete_Section')
    hatch_poly(to_model(p), '0_IFC_Hatch_Structure')
for b in thin:
    add_poly_outline(to_model(b), '0_IFC_Hatch')
for seg in stair_vis[:]:
    pline([(X(u), z) for u, z in seg], '1_IFC_Stair')
for seg in rail_vis:
    pline([(X(u), z) for u, z in seg], '2_IFC_Handrail')

# pencere ve kapi kesitleri
for (ua, ub, za, zb2, tip) in win_cut:
    um = (ua + ub) / 2
    pline([(X(um - 3), za), (X(um - 3), zb2)], '3_IFC_Window')
    pline([(X(um + 3), za), (X(um + 3), zb2)], '3_IFC_Window')
    pline([(X(ua), za), (X(ub), za)], '3_IFC_Window')
    pline([(X(ua), zb2), (X(ub), zb2)], '3_IFC_Window')
for (ua, ub, za, zb2, tip) in door_cut:
    pline(rect_pts(X(ua), za, X(ub), zb2), '1_IFC_Door', close=True)

# cephe kaplamasi (zemin +-0.00'dan cati altina), pencere bosluklari acik
def roof_under(xc, y):
    return CATI_DOSEME_UST + EGIM * min(xc - E0, E1 - xc, y - N0, N1 - y)

for face, (ua, ub), xc, yface in (('N', (-CEPHE_KAPLAMA, 0), KESIT_SEG[0][0], H + CEPHE_KAPLAMA),
                                   ('S', (H, H + CEPHE_KAPLAMA), KESIT_SEG[1][0], -CEPHE_KAPLAMA)):
    ztop = roof_under(xc, yface)
    g = box(ua, 0, ub, ztop)
    for (za, zb2) in clad_open[face]:
        g = g.difference(box(ua - 1, za, ub + 1, zb2))
    for p in polys(g):
        add_poly_outline(to_model(p), '2_IFC_Wall')
        hatch_poly(to_model(p), '0_IFC_Hatch', 'AR-SAND', scale=0.4)

# cati paketi (kesilen) + arka siluet (gorunen)
def roof_cut_poly(xc, ya, yb):
    ys = [ya + i * 5 for i in range(int((yb - ya) / 5) + 1)]
    if ys[-1] < yb:
        ys.append(yb)
    bot = [(U(y), roof_under(xc, y)) for y in ys]
    top = [(u, z + CATI_PAKET) for u, z in bot]
    return Polygon(bot + top[::-1]).simplify(0.01)

rp = unary_union([roof_cut_poly(KESIT_SEG[0][0], 600, N1), roof_cut_poly(KESIT_SEG[1][0], N0, 600)])
for p in polys(rp):
    add_poly_outline(to_model(p), '2_IFC_Roof')
    hatch_poly(to_model(p), '0_IFC_Hatch', 'ANSI31', scale=1.0)
# siluet: cati ust yuzeyinin kesit duzleminin arkasindaki en yuksek hatti (mahya ucgeni)
sil = [(U(y), Z_SACAK_UST + EGIM * min(y - N0, N1 - y)) for y in (N0, RIDGE_Y, N1)]
pline([(X(u), z) for u, z in sil], '2_IFC_Roof_Line')
# zemin
pline([(X(-320), 0), (X(-CEPHE_KAPLAMA), 0)], '7_IFC_Terrain')
pline([(X(H + CEPHE_KAPLAMA), 0), (X(H + 320), 0)], '7_IFC_Terrain')
earth = unary_union([box(-110, -450, 0, 0), box(H, -450, H + 110, 0), box(-110, -450, H + 110, -350 - DOS_KAPLAMA - TEMEL_TASIYICI)])
for p in polys(earth):
    hatch_poly(to_model(p), '0_IFC_Hatch', 'EARTH', scale=1.5)

# kesit yazilari
RT = '0_IFC_Room_Text(No)_100'
T = '0_IFC_Text_Explanation_100'
for txt, y, z in [('BODRUM (BOŞ MAHAL)', 300, -200), ('MUTFAK', 300, 150), ('HOL', 570, 250), ('YATAK ODASI 2', 300, 520)]:
    mtext(txt, X(U(y)), z, 18, RT)
mtext('ÇATI ARASI (kullanılmaz)', X(U(300)), CATI_DOSEME_UST + 28, 11, RT)
mtext('METAL KENET ÇATI KAPLAMASI, EĞİM %15', X(150), Z_MAHYA_UST + 60, 15, T, attach=4)
mtext('TABİİ ZEMİN ±0.00', X(H + 160), 14, 14, T, attach=7)
# kotlar
for z, txt in [(-350, '-3.50'), (0, '±0.00'), (350, '+3.50'), (CATI_DOSEME_UST, f'{kot_str(CATI_DOSEME_UST)} ÇATI DÖŞ. ÜSTÜ')]:
    kot_mark(X(-150), z, txt, side=-1, length=60)
kot_mark(X(N1 - N0 + E0), Z_SACAK_UST, f'{kot_str(Z_SACAK_UST)} SAÇAK UCU', side=1, length=60, h=13)
kot_mark(X(U(RIDGE_Y)), Z_MAHYA_UST, f'{kot_str(Z_MAHYA_UST)} MAHYA', side=1, length=60, h=13)
kot_mark(X(H + 150), -350 - DOS_KAPLAMA - TEMEL_TASIYICI, kot_str(-350 - DOS_KAPLAMA - TEMEL_TASIYICI) + ' TEMEL ALTI', side=1, length=60, h=13)
# kirik kesit isareti (u=410: kuzey parca x=75 | guney parca x=420)
uj = U(KESIT_SEG[0][1])
for za, zb2 in ((Z_MAHYA_UST + 20, Z_MAHYA_UST + 50), (-475, -440)):
    pline([(X(uj), za), (X(uj), zb2)], '0_IFC_Section_Line', linetype='Continuous')
mtext('kırık kesit: solda x=75 (merdiven), sağda x=420', X(uj), -480, 11, T, attach=2)
# olculer
dim_chain([(X(-230), z) for z in (-350, 0, 350, CATI_DOSEME_UST)], (X(-230), 0), horizontal=False)
wz = sorted({0, 350, CATI_DOSEME_UST} | {z for (_a, _b, za, zb2, _t) in win_cut for z in (za, zb2)})
dim_chain([(X(H + CEPHE_KAPLAMA), z) for z in wz], (X(H + 110), 0), horizontal=False)
dim_chain([(X(u), -350 - DOS_KAPLAMA - TEMEL_TASIYICI) for u in (E0, -CEPHE_KAPLAMA, 0, H, H + CEPHE_KAPLAMA, H + CEPHE_KAPLAMA + SACAK)], (X(0), -560))
msp.add_linear_dim(base=(X(0), -620), p1=(X(E0), -400), p2=(X(H + CEPHE_KAPLAMA + SACAK), -400), dimstyle='IFC_Dim100', override=OV, dxfattribs=DA).render()
mtext('KESİT A-A', X(H + 320), -700, 56.25, '0_IFC_Stair_Text', attach=3)
mtext('1/100  ·  bakış doğuya (kuzey solda)  ·  kesit hattı giriş kat ve 1. kat planlarında\\PDöşeme paketi 50 (kaplama 10 + taşıyıcı 30 + tavan 10)  ·  dış duvar 20 + cephe kaplaması 20  ·  pencere yükseklikleri VARSAYIM', X(H + 320), -775, 16, T, attach=3)
mtext('KUZEY', X(-20), -670, 16, T, attach=5)
mtext('GÜNEY', X(H + 20), -670, 16, T, attach=5)
log.append('Kesit A-A eklendi (model X ' + str(SX0) + ' baslangicli, Y = kot cm)')

# =============================================================== 5. MAHAL / ALAN KONTROLU
areas = [(Polygon([(p[0], p[1]) for p in e.get_points('xy')])) for e in msp.query('LWPOLYLINE[layer=="0_IFC_Area"]')]
data = {'floors': [], 'log': log, 'kesit': cut_report}
for key, fname, dy, f in FLOORS:
    rooms = []
    for e in msp.query('INSERT[name=="0_IFC_ROOM_TEXT_50"]'):
        p = e.dxf.insert
        s = e.dxf.xscale
        if not (dy - 400 < p.y < dy + 1400):
            continue
        pt = Point(p.x, p.y - 24.8 * s)
        hit = [a for a in areas if a.contains(pt)]
        assert len(hit) == 1, (fname, e.get_attrib_text('ROOM_NAME'))
        ext = bbox.extents([e])
        corners = [(ext.extmin.x, ext.extmin.y), (ext.extmax.x, ext.extmax.y), (ext.extmin.x, ext.extmax.y), (ext.extmax.x, ext.extmin.y)]
        inside = all(hit[0].buffer(2).contains(Point(c)) for c in corners)
        a = round(hit[0].area / 1e4, 2)
        e.get_attrib('AREA').dxf.text = f'{a:.2f}'
        rooms.append({'ad': e.get_attrib_text('ROOM_NAME'), 'alan': a, 'yazi_mahal_icinde': inside})
    data['floors'].append({'key': key, 'ad': fname, 'dy': dy, 'kot': kot_str(f), 'brut': W * H / 1e4, 'mahaller': rooms})
data['roof'] = {'dy': ROOF_DY, 'sacak_dis': [E0, N0, E1, N1], 'mahya': [RIDGE_X0, RIDGE_X1, RIDGE_Y], 'rise': RISE,
                'z_sacak_alt': Z_SACAK_ALT, 'z_sacak_ust': Z_SACAK_UST, 'z_mahya_alt': Z_MAHYA_ALT, 'z_mahya_ust': Z_MAHYA_UST,
                'izdusum': (E1 - E0) * (N1 - N0) / 1e4}
data['section'] = {'sx0': SX0, 'u0': -330, 'u1': H + 330, 'z0': -800, 'z1': 900}
data['pencere'] = {k: list(v) for k, v in PENCERE.items()}
data['merdiven'] = {'riht': ST_R, 'basamak': ST_G, 'riht_sayisi': ST_RISERS}

# mobilya - duvar cakisma kontrolu (bilgi)
clash = []
for key, fname, dy, f in FLOORS:
    walls = unary_union([RING] + [box(*r) for r in WALLS[key]])
    from shapely.affinity import translate
    walls = translate(walls, yoff=dy)
    for e in msp.query('INSERT'):
        n = e.dxf.name
        if n.startswith(('IFC_PENCERE', 'IFC_DOOR', '0_IFC_ROOM', '*D')) or not (dy - 300 < e.dxf.insert.y < dy + 1300) or e.dxf.insert.x > 1500:
            continue
        ext = bbox.extents([e])
        if not ext.has_data:
            continue
        bb = box(ext.extmin.x + 1, ext.extmin.y + 1, ext.extmax.x - 1, ext.extmax.y - 1)
        ov = bb.intersection(walls).area
        if ov > 50:
            clash.append((fname, n, round(ov), [round(v) for v in (ext.extmin.x, ext.extmin.y - dy, ext.extmax.x, ext.extmax.y - dy)]))
data['clash'] = clash

# =============================================================== 6. PURGE + KAYIT
def used_blocks():
    used = set()
    def walk(ents):
        for e in ents:
            n = e.dxf.name if e.dxftype() == 'INSERT' else (e.dxf.get('geometry') if e.dxftype() == 'DIMENSION' else None)
            if n and n not in used and n in doc.blocks:
                used.add(n)
                walk(doc.blocks.get(n))
    walk(msp)
    return used

ub = used_blocks()
keep = ub | {'_Oblique', '_None'}
removed = []
for blk in list(doc.blocks):
    n = blk.name
    if n.lower().startswith(('*model_space', '*paper_space')):
        continue
    if n not in keep:
        try:
            doc.blocks.delete_block(n, safe=False); removed.append(n)
        except Exception as ex:
            print('blok silinemedi', n, ex)
used_layers = {'0', 'Defpoints'}
for e in msp:
    used_layers.add(e.dxf.layer)
for n in keep:
    if n in doc.blocks:
        for e in doc.blocks.get(n):
            used_layers.add(e.dxf.layer)
for lay in list(doc.layers):
    if lay.dxf.name not in used_layers:
        try:
            doc.layers.remove(lay.dxf.name); removed.append('katman ' + lay.dxf.name)
        except Exception as ex:
            print('katman silinemedi', lay.dxf.name, ex)
data['purge'] = removed
doc.header['$CLAYER'] = '0'
doc.header['$LTSCALE'] = 1.0
for lay in doc.layers:
    lay.thaw(); lay.on()
aud = doc.audit()
print('audit fixes', len(aud.fixes), 'errors', len(aud.errors))
doc.saveas(OUT)
json.dump(data, open(OUTJSON, 'w'), ensure_ascii=False, indent=1)
print('OK', OUT)
print('purge:', removed)
print('clash:', clash)
for fl in data['floors']:
    print(fl['ad'], [(r['ad'], r['alan'], r['yazi_mahal_icinde']) for r in fl['mahaller']])
print(cut_report)
print('roof', data['roof'])
