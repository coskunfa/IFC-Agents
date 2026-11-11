# DNM01 konsept kat planlari - DXF uretici (CIZGI)
import math, json, sys
import ezdxf
from ezdxf.math import Matrix44, Vec3
from ezdxf.enums import TextEntityAlignment
from shapely.geometry import box, Polygon
from shapely.ops import unary_union

ROOT = '/home/user/ifc-agents'
TEMPLATE = ROOT + '/ofis-standartlari/referans-sunumlar/ref_kat-plani-cizimi_IFC-ornek.dxf'
OUT = ROOT + '/projeler/DNM01/01-cizim/taslak/DNM01_cizim_kat-planlari_v01.dxf'
OUTJSON = sys.argv[1] if len(sys.argv) > 1 else '/tmp/dnm01_data.json'

doc = ezdxf.readfile(TEMPLATE)
msp = doc.modelspace()
for e in list(msp):
    msp.delete_entity(e)
for lay in doc.layouts:
    if lay.name != 'Model':
        for e in list(lay):
            if e.dxftype() != 'VIEWPORT':
                lay.delete_entity(e)
doc.header['$INSUNITS'] = 5  # cm

DIM_LAYER = '0_IFC_Dimension'
if DIM_LAYER not in doc.layers:
    doc.layers.add(DIM_LAYER, color=3)

W, H = 1360, 1010
FLOORS = [  # key, name, dy, kot
    ('B', 'BODRUM KAT', -1810, '-3.50'),
    ('G', 'GİRİŞ KAT', 0, '±0.00'),
    ('K1', '1.KAT', 1810, '+3.50'),
]

# ---------------------------------------------------------------- blocks
def new_block(name):
    if name in doc.blocks:
        return None
    return doc.blocks.new(name)

def rect_pts(x0, y0, x1, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]

# door 100 (entrance, 20 cm wall) - same convention as IFC_DOOR_90
b = new_block('IFC_DOOR_100')
L = {'layer': '1_IFC_Door'}
b.add_lwpolyline(rect_pts(-100, -20, -95, 0), close=True, dxfattribs=L)
b.add_lwpolyline(rect_pts(-5, -20, 0, 0), close=True, dxfattribs=L)
b.add_lwpolyline([(-5, 0), (-5, 90)], dxfattribs=L)
b.add_lwpolyline(rect_pts(-9, 0, -5, 90), close=True, dxfattribs=L)
b.add_arc((-5, 0), 90, 90, 180, dxfattribs=L)

def window_block(w):
    name = f'IFC_PENCERE_{w}'
    b = new_block(name)
    if b is None:
        return name
    L = {'layer': '3_IFC_Window'}
    b.add_lwpolyline([(0, 0), (w, 0)], dxfattribs=L)
    b.add_lwpolyline([(0, 20), (w, 20)], dxfattribs=L)
    b.add_lwpolyline(rect_pts(0, 5, 5, 15), close=True, dxfattribs=L)
    b.add_lwpolyline(rect_pts(w - 5, 5, w, 15), close=True, dxfattribs=L)
    b.add_lwpolyline([(5, 8), (w - 5, 8)], dxfattribs=L)
    b.add_lwpolyline([(5, 12), (w - 5, 12)], dxfattribs=L)
    a = b.add_attdef('TİP', (w / 2, -35), dxfattribs={'layer': '0_IFC_Window_Text', 'height': 18, 'style': 'IFC_TEXT'})
    a.dxf.text = 'P-'
    a.set_placement((w / 2, -35), align=TextEntityAlignment.MIDDLE_CENTER)
    a2 = b.add_attdef('YUKSEKLIK', (w / 2, -60), dxfattribs={'layer': '0_IFC_Window_Text', 'height': 12, 'style': 'IFC_TEXT', 'flags': 1})
    a2.dxf.text = '250'
    a2.set_placement((w / 2, -60), align=TextEntityAlignment.MIDDLE_CENTER)
    return name

def shower_block(wx, wy):
    name = f'IFC_DUS_{wx}x{wy}'
    b = new_block(name)
    if b is None:
        return name
    L = {'layer': '6_IFC_Furniture_WC'}
    b.add_lwpolyline(rect_pts(0, 0, wx, wy), close=True, dxfattribs=L)
    b.add_lwpolyline(rect_pts(4, 4, wx - 4, wy - 4), close=True, dxfattribs=L)
    b.add_line((4, 4), (wx - 4, wy - 4), dxfattribs=L)
    b.add_line((4, wy - 4), (wx - 4, 4), dxfattribs=L)
    b.add_circle((wx / 2, wy / 2), 4, dxfattribs=L)
    return name

b = new_block('IFC_MUTFAK ADA_240x100')
L = {'layer': '6_IFC_Furniture_Wetspace'}
b.add_lwpolyline(rect_pts(0, 0, 240, 100), close=True, dxfattribs=L)
b.add_lwpolyline(rect_pts(0, 0, 240, 65), close=True, dxfattribs=L)  # dolap + bar cikmasi

b = new_block('IFC_BUZDOLABI_75x65')
b.add_lwpolyline(rect_pts(0, 0, 75, 65), close=True, dxfattribs=L)
b.add_line((0, 0), (75, 65), dxfattribs=L)
b.add_line((0, 65), (75, 0), dxfattribs=L)

b = new_block('IFC_SOMINE_160x40')
L = {'layer': '6_IFC_Furniture'}
b.add_lwpolyline(rect_pts(0, 0, 160, 40), close=True, dxfattribs=L)
b.add_lwpolyline(rect_pts(30, 8, 130, 32), close=True, dxfattribs=L)
b.add_line((30, 20), (130, 20), dxfattribs=L)

b = new_block('IFC_TV UNITESI_240x45')
b.add_lwpolyline(rect_pts(0, 0, 240, 45), close=True, dxfattribs=L)

b = new_block('IFC_YEMEK MASASI_240x100_8K')
b.add_lwpolyline(rect_pts(0, 0, 240, 100), close=True, dxfattribs=L)
for cx in (40, 120, 200):
    b.add_blockref('IFC_SAND2', (cx, 0), dxfattribs={'layer': '0'})  # alt sira: sirt asagi, on yuz masaya
    b.add_blockref('IFC_SAND2', (cx, 100), dxfattribs={'layer': '0', 'rotation': 180})
b.add_blockref('IFC_SAND2', (0, 50), dxfattribs={'layer': '0', 'rotation': 270})
b.add_blockref('IFC_SAND2', (240, 50), dxfattribs={'layer': '0', 'rotation': 90})

b = new_block('IFC_ASANSOR_KABIN_120x150')
L = {'layer': '1_IFC_Stair'}
b.add_lwpolyline(rect_pts(8, 15, 112, 142), close=True, dxfattribs=L)
b.add_line((8, 15), (112, 142), dxfattribs=L)
b.add_line((8, 142), (112, 15), dxfattribs=L)
b.add_lwpolyline([(20, 5), (100, 5)], dxfattribs=L)  # kabin kapisi

# ---------------------------------------------------------------- helpers
def P(pt, dy):
    return (pt[0], pt[1] + dy)

def ins(name, x, y, dy, rot=0, sx=1, sy=1, layer='0'):
    return msp.add_blockref(name, (x, y + dy), dxfattribs={'layer': layer, 'rotation': rot, 'xscale': sx, 'yscale': sy})

def pline(pts, dy, layer, close=False):
    return msp.add_lwpolyline([P(p, dy) for p in pts], close=close, dxfattribs={'layer': layer})

def mtext(txt, x, y, dy, h, layer, attach=5, rot=0):
    m = msp.add_mtext(txt, dxfattribs={'layer': layer, 'style': 'IFC_TEXT', 'char_height': h, 'attachment_point': attach, 'rotation': rot})
    m.dxf.insert = (x, y + dy)
    return m

def door(kind, Hpt, Ppt, v, dy):
    """kind: 90/80/100. Hpt: hinge end on swing-side wall face, Ppt: other end, v: swing direction."""
    name = {90: 'IFC_DOOR_90', 80: 'IFC_DOOR_80', 100: 'IFC_DOOR_100'}[kind]
    u = Vec3(Hpt[0] - Ppt[0], Hpt[1] - Ppt[1], 0).normalize()
    vv = Vec3(v[0], v[1], 0)
    m = Matrix44.ucs(ux=u, uy=vv, uz=u.cross(vv), origin=Vec3(Hpt[0], Hpt[1] + dy, 0))
    ref = msp.add_blockref(name, (0, 0), dxfattribs={'layer': '0', 'rotation': 90 if kind == 80 else 0})
    ref.transform(m)
    return ref

def window(side, a0, a1, tip, height, dy):
    w = a1 - a0
    name = window_block(w)
    if side == 'S':
        ref = ins(name, a0, 0, dy, rot=0); tp = ((a0 + a1) / 2, -35); trot = 0
    elif side == 'N':
        ref = ins(name, a1, H, dy, rot=180); tp = ((a0 + a1) / 2, H + 35); trot = 0
    elif side == 'W':
        ref = ins(name, 0, a1, dy, rot=270); tp = (-35, (a0 + a1) / 2); trot = 90
    else:
        ref = ins(name, W, a0, dy, rot=90); tp = (W + 35, (a0 + a1) / 2); trot = 90
    ref.add_auto_attribs({'TİP': tip, 'YUKSEKLIK': str(height)})
    for at in ref.attribs:
        if at.dxf.tag == 'TİP':
            at.dxf.rotation = trot
            at.set_placement((tp[0], tp[1] + dy), align=TextEntityAlignment.MIDDLE_CENTER)
        else:
            at.dxf.rotation = trot
            at.set_placement((tp[0] + (0 if side in 'SN' else (-20 if side == 'W' else 20)), tp[1] + dy + (-22 if side == 'S' else 22 if side == 'N' else 0)), align=TextEntityAlignment.MIDDLE_CENTER)
    return ref

def wardrobe(x, y, dy, length, rot):
    ins('IFC_WARDROBE', x, y, dy, rot=rot, sx=length / 100)

def room_label(name, pt, area, dy, s=2.0):
    ref = msp.add_blockref('0_IFC_ROOM_TEXT_50', (pt[0], pt[1] + 24.8 * s + dy), dxfattribs={'layer': '0', 'xscale': s, 'yscale': s})
    ref.add_auto_attribs({'ROOM_NAME': name, 'AREA': f'{area:.2f}', 'DÖŞEME:': '', 'DUVAR:': '', 'TAVAN:': ''})

def solid_hatch(poly, dy, layer, color=None):
    h = msp.add_hatch(color=256 if color is None else color, dxfattribs={'layer': layer})
    h.paths.add_polyline_path([P(p, dy) for p in list(poly.exterior.coords)[:-1]], is_closed=True)
    return h

# ---------------------------------------------------------------- geometry
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
# windows: (side, a0, a1, tip, yukseklik, mahal)
WINDOWS = {
    'B': [],
    'G': [('S', 225, 465, 'P1', 120, 'Mutfak'), ('S', 760, 1260, 'P2', 250, 'Salon (yemek)'),
          ('E', 100, 450, 'P3', 250, 'Salon (yemek/somine)'), ('E', 600, 900, 'P4', 250, 'Salon (oturma)')],
    'K1': [('S', 80, 230, 'P5', 150, 'Yatak odasi 1'), ('S', 380, 560, 'P6', 150, 'Yatak odasi 2'),
           ('S', 740, 920, 'P7', 150, 'Yatak odasi 3'), ('S', 1060, 1300, 'P8', 220, 'Ebeveyn yatak odasi'),
           ('N', 455, 555, 'P9', 150, 'Hol'), ('N', 705, 805, 'P10', 60, 'Ebeveyn banyosu (jakuzi ustu)'),
           ('N', 1110, 1230, 'P11', 120, 'Giyinme odasi')],
}
# doors: (kind, H, P, v, wall thickness, mahal)
DOORS = {
    'B': [],
    'G': [(100, (625, 990), (525, 990), (0, -1), 20, 'Ana giris (kuzey)'),
          (90, (405, 530), (315, 530), (0, -1), 10, 'Hol -> Mutfak'),
          (80, (265, 665), (185, 665), (0, 1), 10, 'Hol -> WC')],
    'K1': [(90, (290, 655), (290, 565), (-1, 0), 10, 'Hol -> Yatak odasi 1'),
           (80, (185, 665), (265, 665), (0, 1), 10, 'Yatak odasi 1 -> Banyo 1'),
           (90, (395, 555), (485, 555), (0, -1), 10, 'Hol -> Yatak odasi 2'),
           (80, (510, 340), (590, 340), (0, 1), 10, 'Yatak odasi 2 -> Banyo 2'),
           (80, (790, 340), (710, 340), (0, 1), 10, 'Yatak odasi 3 -> Banyo 3'),
           (90, (905, 555), (815, 555), (0, -1), 10, 'Hol -> Yatak odasi 3'),
           (90, (915, 665), (915, 575), (1, 0), 10, 'Hol -> Ebeveyn yatak odasi'),
           (90, (1185, 685), (1095, 685), (0, 1), 10, 'Ebeveyn -> Giyinme'),
           (80, (905, 865), (905, 785), (-1, 0), 10, 'Giyinme -> Ebeveyn banyosu')],
}
LIFT_DOOR = (320, 710, 400, 720)
EXTRA_OPEN = {  # kapisiz aciklik / surgu
    'B': [LIFT_DOOR],
    'G': [LIFT_DOOR, (670, 165, 680, 365), (670, 550, 680, 670)],
    'K1': [LIFT_DOOR, (690, 715, 700, 795)],
}
STAIR_FOOT = unary_union([box(20, 637, 130, 880), box(20, 880, 427, 990)])

ROOMS = {  # name, label point, label scale
    'B': [('BODRUM / BOŞ MAHAL', (900, 470), 2.0), ('ASANSÖR', (360, 800), 0.9)],
    'G': [('GİRİŞ HOLÜ', (580, 790), 2.0), ('WC', (200, 770), 1.4), ('ASANSÖR', (360, 800), 0.9),
          ('MUTFAK', (570, 430), 2.0), ('SALON', (1260, 255), 2.0)],
    'K1': [('HOL', (500, 645), 2.0), ('YATAK ODASI 1', (155, 535), 1.7), ('BANYO 1', (250, 760), 1.0),
           ('ASANSÖR', (360, 800), 0.9), ('YATAK ODASI 2', (368, 190), 1.3), ('BANYO 2', (617, 400), 0.8),
           ('YATAK ODASI 3', (932, 190), 1.3), ('BANYO 3', (683, 400), 0.8),
           ('EBEVEYN YATAK ODASI', (1190, 560), 1.4), ('GİYİNME ODASI', (1180, 845), 1.8),
           ('EBEVEYN BANYOSU', (790, 805), 1.2), ('WC', (640, 790), 1.1)],
}

def door_rect(Hpt, Ppt, v, t):
    xs = [Hpt[0], Ppt[0]]; ys = [Hpt[1], Ppt[1]]
    if v[1] != 0:  # horizontal wall, face at y
        y = Hpt[1]; y2 = y - v[1] * t
        return box(min(xs), min(y, y2), max(xs), max(y, y2))
    x = Hpt[0]; x2 = x - v[0] * t
    return box(min(x, x2), min(ys), max(x, x2), max(ys))

def win_rect(side, a0, a1):
    return {'S': box(a0, 0, a1, 20), 'N': box(a0, H - 20, a1, H), 'W': box(0, a0, 20, a1), 'E': box(W - 20, a0, W, a1)}[side]

def polys(g):
    if g.is_empty:
        return []
    return list(g.geoms) if hasattr(g, 'geoms') else [g]

def add_poly_outline(poly, dy, layer):
    pline([(round(x, 3), round(y, 3)) for x, y in list(poly.exterior.coords)[:-1]], dy, layer, close=True)
    for ring in poly.interiors:
        pline([(round(x, 3), round(y, 3)) for x, y in list(ring.coords)[:-1]], dy, layer, close=True)

# ---------------------------------------------------------------- stair
def draw_stair(key, dy):
    y_start = 637 if key != 'K1' else 665
    L = '1_IFC_Stair'
    outline = [(20, y_start), (130, y_start), (130, 880), (427, 880), (427, 990), (20, 990)]
    pline(outline, dy, L, close=True)
    for k in range(10):
        y = 880 - 27 * k
        if y > y_start:
            pline([(20, y), (130, y)], dy, L)
    for k in range(1, 12):
        x = 130 + 27 * k
        if x < 427:
            pline([(x, 880), (x, 990)], dy, L)
    pline([(130, 880), (20, 925)], dy, L)
    pline([(130, 880), (80, 990)], dy, L)
    T = '0_IFC_Stair_Text'
    if key in ('B', 'G'):
        # cut line (kesit/kirma cizgisi)
        pline([(20, 790), (65, 790), (72, 802), (80, 778), (87, 790), (130, 790)], dy, L)
        pline([(75, 650), (75, 775)], dy, L)
        msp.add_circle((75, 650 + dy), 5, dxfattribs={'layer': L})
        pline([(65, 755), (75, 775), (85, 755)], dy, L)
        mtext('ÇIKIŞ', 100, 700, dy, 14, T, attach=5, rot=90)
    if key == 'G':
        pline([(410, 935), (75, 935), (75, 815)], dy, L)
        msp.add_circle((410, 935 + dy), 5, dxfattribs={'layer': L})
        pline([(65, 835), (75, 815), (85, 835)], dy, L)
        mtext('İNİŞ (BODRUM)', 300, 962, dy, 14, T)
        mtext('ÇIKIŞ (1.KAT)', 300, 905, dy, 14, T)
    if key == 'K1':
        pline([(410, 935), (75, 935), (75, 690)], dy, L)
        msp.add_circle((410, 935 + dy), 5, dxfattribs={'layer': L})
        pline([(65, 710), (75, 690), (85, 710)], dy, L)
        mtext('İNİŞ', 300, 962, dy, 14, T)
    if key == 'B':
        pline([(130, 637), (130, 880), (290, 880)], dy, '2_IFC_Handrail')

# ---------------------------------------------------------------- furniture
def furniture(key, dy):
    if key == 'G':
        # mutfak
        ins('IFC_MUTFAK TEZGAH', 560, 20, dy, rot=180, sx=540 / 200)
        ins('IFC_MUTFAK TEZGAH', 80, 450, dy, rot=270, sx=370 / 200)
        ins('IFC_BUZDOLABI_75x65', 20, 452, dy, rot=0)
        ins('IFC_EVYE_1.5', 345, 25, dy, rot=180)
        ins('IFC_MUTFAK ADA_240x100', 225, 215, dy)
        ins('IFC_OCAK', 348, 250, dy)
        for x in (270, 345, 420):
            ins('IFC_BAR TABURESI', x, 340, dy, rot=180)
        # wc
        ins('IFC_KLOZET', 185, 870, dy)
        ins('IFC_VITRA_DOLAPLI LAVABO_53X60', 290, 795, dy, rot=270)
        # vestiyer
        wardrobe(430, 670, dy, 210, 90)
        # salon
        ins('IFC_TV UNITESI_240x45', 890, 945, dy)
        ins('IFC_TV', 955, 952, dy)
        ins('cube kanepe 220x761', 1010, 640, dy, rot=180)
        ins('IFC_KOLTUK TEKLI', 790, 800, dy, rot=180)
        ins('IFC_KOLTUK TEKLI', 1230, 800, dy, rot=0)
        ins('IFC_COFFE TABLE 2', 960, 830, dy)
        ins('IFC_KOLTUK 3LU', 990, 470, dy, rot=270)
        ins('IFC_KOLTUK TEKLI', 800, 420, dy, rot=180)
        ins('IFC_KOLTUK TEKLI', 1220, 420, dy, rot=0)
        ins('IFC_COFFE TABLE', 1010, 420, dy)
        ins('IFC_SOMINE_160x40', 930, 340, dy)
        mtext('ŞÖMİNE', 1010, 312, dy, 14, '0_IFC_Text_Explanation_100')
        ins('IFC_YEMEK MASASI_240x100_8K', 890, 150, dy)
    if key == 'K1':
        # yatak odasi 1
        ins('IFC_BED DOUBLE', 20, 330, dy, rot=90)
        wardrobe(20, 655, dy, 160, 0)
        # banyo 1
        ins(shower_block(90, 90), 200, 780, dy)
        ins('IFC_KLOZET', 140, 830, dy, rot=90)
        ins('IFC_VITRA_DOLAPLI LAVABO_53X60', 140, 775, dy, rot=90)
        # yatak odasi 2 / banyo 2
        ins('IFC_BED DOUBLE', 645, 175, dy, rot=270)
        wardrobe(300, 340, dy, 200, 90)
        ins(shower_block(90, 90), 555, 465, dy)
        ins('IFC_KLOZET', 522, 555, dy)
        ins('IFC_VITRA_DOLAPLI LAVABO_53X60', 500, 450, dy, rot=90)
        # yatak odasi 3 / banyo 3
        ins('IFC_BED DOUBLE', 655, 175, dy, rot=90)
        wardrobe(1005, 540, dy, 200, 270)
        ins(shower_block(90, 90), 655, 465, dy)
        ins('IFC_KLOZET', 778, 555, dy)
        ins('IFC_VITRA_DOLAPLI LAVABO_53X60', 800, 450, dy, rot=270)
        # ebeveyn
        ins('IFC_BED DOUBLE', 1015, 330, dy, rot=90)
        # giyinme
        wardrobe(915, 990, dy, 165, 0)
        wardrobe(1340, 930, dy, 245, 270)
        wardrobe(1080, 685, dy, 165, 180)
        # ebeveyn banyosu
        ins('IFC_KLOZET', 640, 685, dy, rot=180)
        ins('IFC_ SINK', 755, 685, dy, rot=180)
        ins('IFC_ SINK', 835, 685, dy, rot=180)
        ins('JAKUZI', 600, 935, dy, rot=90)
        ins(shower_block(100, 100), 805, 890, dy)
        # surgu kapi (kapali wc)
        pline(rect_pts(700, 710, 704, 760), dy, '1_IFC_Door', close=True)
        pline(rect_pts(704, 750, 708, 800), dy, '1_IFC_Door', close=True)
    # asansor kabini (tum katlar)
    ins('IFC_ASANSOR_KABIN_120x150', 300, 720, dy)
    # asansor kapisi
    pline(rect_pts(320, 712, 400, 718), dy, '1_IFC_Door', close=True)

# ---------------------------------------------------------------- dims
def dims(key, dy, walls):
    feats = {'S': [], 'N': [], 'W': [], 'E': []}
    for (side, a0, a1, *_r) in WINDOWS[key]:
        feats[side] += [a0, a1]
    if key == 'G':
        feats['N'] += [525, 625]
    # interior walls touching facade -> axis
    for (x0, y0, x1, y1) in walls:
        if x1 - x0 <= 10.01 and y0 <= 20:
            feats['S'].append((x0 + x1) / 2)
        if x1 - x0 <= 10.01 and y1 >= 990:
            feats['N'].append((x0 + x1) / 2)
        if y1 - y0 <= 10.01 and x0 <= 20:
            feats['W'].append((y0 + y1) / 2)
        if y1 - y0 <= 10.01 and x1 >= 1340:
            feats['E'].append((y0 + y1) / 2)
    DA = {'layer': DIM_LAYER}
    OV = {'dimclrd': 0, 'dimclre': 0}
    for side, vals in feats.items():
        span = W if side in 'SN' else H
        pts = sorted(set([0, span] + vals))
        if len(pts) <= 2:
            continue
        if side == 'S':
            msp.add_multi_point_linear_dim(base=(0, -110 + dy), points=[(p, dy) for p in pts], dimstyle='IFC_Dim100', override=OV, dxfattribs=DA)
        elif side == 'N':
            msp.add_multi_point_linear_dim(base=(0, H + 110 + dy), points=[(p, H + dy) for p in pts], dimstyle='IFC_Dim100', override=OV, dxfattribs=DA)
        elif side == 'W':
            msp.add_multi_point_linear_dim(base=(-110, dy), points=[(0, p + dy) for p in pts], angle=90, dimstyle='IFC_Dim100', override=OV, dxfattribs=DA)
        else:
            msp.add_multi_point_linear_dim(base=(W + 110, dy), points=[(W, p + dy) for p in pts], angle=90, dimstyle='IFC_Dim100', override=OV, dxfattribs=DA)
    msp.add_linear_dim(base=(0, -170 + dy), p1=(0, dy), p2=(W, dy), dimstyle='IFC_Dim100', override=OV, dxfattribs=DA).render()
    msp.add_linear_dim(base=(-170, dy), p1=(0, dy), p2=(0, H + dy), angle=90, dimstyle='IFC_Dim100', override=OV, dxfattribs=DA).render()

# ---------------------------------------------------------------- main loop
data = {'floors': []}
for key, fname, dy, kot in FLOORS:
    walls = WALLS[key]
    wall_union = unary_union([RING] + [box(*r) for r in walls])
    openings = [door_rect(Hh, Pp, v, t) for (_k, Hh, Pp, v, t, _m) in DOORS[key]]
    openings += [win_rect(s, a0, a1) for (s, a0, a1, *_r) in WINDOWS[key]]
    openings += [box(*r) for r in EXTRA_OPEN[key]]
    col_union = unary_union(COLUMNS)
    wall_draw = wall_union.difference(unary_union(openings)).difference(col_union)
    for p in polys(wall_draw):
        add_poly_outline(p, dy, '2_IFC_Wall')
    for c in COLUMNS:
        add_poly_outline(c, dy, '1_IFC_Concrete_Section')
        solid_hatch(c, dy, '0_IFC_Hatch_Structure')
    # rooms
    interior = box(20, 20, W - 20, H - 20).difference(wall_union)
    room_polys = polys(interior)
    rooms_out = []
    used = set()
    for rname, pt, sc in ROOMS[key]:
        from shapely.geometry import Point
        hit = [i for i, rp in enumerate(room_polys) if rp.contains(Point(pt))]
        assert len(hit) == 1, (key, rname, hit)
        i = hit[0]; used.add(i)
        rp = room_polys[i]
        stair_part = rp.intersection(STAIR_FOOT)
        if stair_part.area > 20000:
            rp = rp.difference(STAIR_FOOT)
            sp = polys(stair_part)[0]
            add_poly_outline(sp, dy, '0_IFC_Area')
            sname = 'MERDİVEN BOŞLUĞU' if key == 'K1' else 'MERDİVEN'
            rooms_out.append({'ad': sname, 'alan': round(sp.area / 1e4, 2)})
        assert rp.geom_type == 'Polygon', (rname, rp.geom_type)
        add_poly_outline(rp, dy, '0_IFC_Area')
        a = round(rp.area / 1e4, 2)
        rooms_out.append({'ad': rname, 'alan': a})
        room_label(rname, pt, a, dy, sc)
    unl = [i for i in range(len(room_polys)) if i not in used]
    assert not unl, (key, [room_polys[i].bounds for i in unl])
    draw_stair(key, dy)
    for (s, a0, a1, tip, hgt, _m) in WINDOWS[key]:
        window(s, a0, a1, tip, hgt, dy)
    for (k, Hh, Pp, v, t, _m) in DOORS[key]:
        door(k, Hh, Pp, v, dy)
    furniture(key, dy)
    dims(key, dy, walls)
    # kat basligi, kot, brut alan
    mtext(fname, W, -235, dy, 56.25, '0_IFC_Stair_Text', attach=3)
    brut = W * H / 1e4
    mtext(f'KOT {kot}   KAT BRÜT ALANI {brut:.2f} m²', W, -310, dy, 20, '0_IFC_Text_Explanation_100', attach=3)
    # kot isareti
    kp = {'B': (800, 250), 'G': (560, 600), 'K1': (330, 590)}[key]
    pline([(kp[0] - 10, kp[1] + 15), (kp[0] + 10, kp[1] + 15), (kp[0], kp[1])], dy, '0_IFC_Elevation_5', close=True)
    pline([(kp[0], kp[1] + 15), (kp[0] + 60, kp[1] + 15)], dy, '0_IFC_Elevation_5')
    mtext(kot, kp[0] + 14, kp[1] + 30, dy, 15, '0_IFC_Text_Explanation_100', attach=7)
    # kuzey oku
    cx, cy = 1640, 880
    msp.add_circle((cx, cy + dy), 40, dxfattribs={'layer': '0_IFC_Text_Explanation_100'})
    pline([(cx, cy + 50), (cx - 18, cy - 30), (cx, cy - 15), (cx + 18, cy - 30)], dy, '0_IFC_Text_Explanation_100', close=True)
    mtext('K', cx, cy + 80, dy, 25, '0_IFC_Text_Explanation_100')
    if key == 'G':
        # ana giris isareti
        pline([(560, 1215), (590, 1215), (575, 1185)], dy, '0_IFC_Text_Explanation_100', close=True)
        pline([(575, 1215), (575, 1260)], dy, '0_IFC_Text_Explanation_100')
        mtext('ANA GİRİŞ', 600, 1240, dy, 20, '0_IFC_Text_Explanation_100', attach=4)
    data['floors'].append({'key': key, 'ad': fname, 'dy': dy, 'kot': kot, 'brut': round(brut, 2), 'mahaller': rooms_out,
                           'pencereler': [dict(zip(['cephe', 'a0', 'a1', 'tip', 'yukseklik', 'mahal'], w)) for w in WINDOWS[key]],
                           'kapilar': [{'genislik': k, 'yer': m} for (k, _h, _p, _v, _t, m) in DOORS[key]]})

# ---------------------------------------------------------------- purge
def used_blocks():
    used = set()
    def walk(layout_ents):
        for e in layout_ents:
            if e.dxftype() == 'INSERT':
                n = e.dxf.name
                if n not in used:
                    used.add(n)
                    walk(doc.blocks.get(n))
            elif e.dxftype() == 'DIMENSION':
                n = e.dxf.get('geometry')
                if n and n not in used:
                    used.add(n)
                    walk(doc.blocks.get(n))
    walk(msp)
    return used

ub = used_blocks()
keep = ub | {'_Oblique', '_None'}
for blk in list(doc.blocks):
    n = blk.name
    if n.lower().startswith('*model_space') or n.lower().startswith('*paper_space'):
        continue
    if n not in keep:
        try:
            doc.blocks.delete_block(n, safe=False)
        except Exception as ex:
            print('blok silinemedi', n, ex)

# layers in use
used_layers = {'0', 'Defpoints'}
def coll(ents):
    for e in ents:
        used_layers.add(e.dxf.layer)
coll(msp)
for n in keep:
    if n in doc.blocks:
        coll(doc.blocks.get(n))
for lay in list(doc.layers):
    if lay.dxf.name not in used_layers:
        try:
            doc.layers.remove(lay.dxf.name)
        except Exception as ex:
            print('katman silinemedi', lay.dxf.name, ex)

doc.header['$CLAYER'] = '0'
for lay in doc.layers:
    lay.thaw(); lay.on()
auditor = doc.audit()
print('audit fixes', len(auditor.fixes), 'errors', len(auditor.errors))
doc.saveas(OUT)
json.dump(data, open(OUTJSON, 'w'), ensure_ascii=False, indent=1)
print('OK', OUT)
print('bloklar:', sorted(ub))
print('katmanlar:', sorted(used_layers))
