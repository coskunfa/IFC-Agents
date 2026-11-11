# DNM01 - PDF (A4, 1/100, kat basina sayfa) + PNG onizleme
import json, sys
import ezdxf
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib import font_manager
from matplotlib.patches import Rectangle
from PIL import Image
from ezdxf.addons import acadctb
from ezdxf.addons.drawing import RenderContext, Frontend
from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
from ezdxf.addons.drawing.config import Configuration, LineweightPolicy, ColorPolicy, BackgroundPolicy

ROOT = '/home/user/ifc-agents'
BASE = ROOT + '/projeler/DNM01/01-cizim/taslak/DNM01_cizim_kat-planlari_v01'
DATA = json.load(open(sys.argv[1]))
LOGO = ROOT + '/ofis-standartlari/logolar/IFC_Architects_logo_koyu.png'

for f in ['/usr/share/fonts/truetype/crosextra/Carlito-Regular.ttf', '/usr/share/fonts/truetype/crosextra/Carlito-Bold.ttf']:
    try:
        font_manager.fontManager.addfont(f)
    except Exception:
        pass
plt.rcParams['font.family'] = 'Carlito'

def load_render_doc():
    d = ezdxf.readfile(BASE + '.dxf')
    ctb = acadctb.load(ROOT + '/ofis-standartlari/cad/IFC_CTB.ctb')
    for b in d.blocks:
        for e in list(b):
            if e.dxftype() == 'WIPEOUT':
                b.delete_entity(e)
    for lay in d.layers:
        lw = ctb.get_lineweight(lay.dxf.color)
        lay.dxf.lineweight = int(round((lw if lw else 0.13) * 100))
        if lay.dxf.plot == 0:  # basilmayan katmanlar (alan poligonu, defpoints)
            lay.off()
    return d

doc = load_render_doc()
cfg = Configuration(lineweight_policy=LineweightPolicy.ABSOLUTE, lineweight_scaling=1.0,
                    color_policy=ColorPolicy.COLOR, background_policy=BackgroundPolicy.WHITE)

def draw_model(ax, xlim, ylim, scaling=1.0):
    c = Configuration(lineweight_policy=LineweightPolicy.ABSOLUTE, lineweight_scaling=scaling,
                      color_policy=ColorPolicy.COLOR, background_policy=BackgroundPolicy.WHITE)
    Frontend(RenderContext(doc), MatplotlibBackend(ax), config=c).draw_layout(doc.modelspace(), finalize=False)
    ax.set_xlim(*xlim); ax.set_ylim(*ylim)
    ax.set_aspect('equal', adjustable='box')
    ax.axis('off')

MM = 1 / 25.4
PW, PH = 297, 210  # A4 yatay
TB_W = 68  # bilgi blogu genisligi (mm)

def title_block(fig, floor, page, npages):
    # dis cerceve
    def r(x, y, w, h, lw=0.5):
        fig.add_artist(Rectangle((x / PW, y / PH), w / PW, h / PH, fill=False, lw=lw, color='black', transform=fig.transFigure))
    r(10, 10, PW - 20, PH - 20, 0.7)
    x0 = PW - 10 - TB_W
    r(x0, 10, TB_W, PH - 20, 0.7)
    # logo
    im = Image.open(LOGO)
    lw_mm = TB_W - 10
    lh_mm = lw_mm * im.size[1] / im.size[0]
    ax = fig.add_axes([(x0 + 5) / PW, (PH - 10 - 8 - lh_mm) / PH, lw_mm / PW, lh_mm / PH])
    ax.imshow(im); ax.axis('off')
    rows = [
        ('PROJE', 'Deneme Villa'),
        ('PROJE KODU', 'DNM01'),
        ('ÇİZİM', f"{floor['ad'].replace('1.KAT', '1. KAT')} PLANI"),
        ('ÖLÇEK', '1/100'),
        ('KAĞIT', 'A4'),
        ('TARİH', '11.11.2026'),
        ('SÜRÜM', 'v01'),
        ('AŞAMA', 'KONSEPT'),
        ('DURUM', 'TASLAK - onay bekliyor'),
        ('KOT', floor['kot'] + ' m'),
        ('BRÜT ALAN', f"{floor['brut']:.2f} m²"),
        ('PAFTA', f'{page}/{npages}'),
    ]
    y = PH - 10 - 8 - lh_mm - 10
    rh = 9.2
    for k, v in rows:
        fig.add_artist(plt.Line2D([x0 / PW, (x0 + TB_W) / PW], [(y + rh - 2) / PH] * 2, lw=0.3, color='black', transform=fig.transFigure))
        fig.text((x0 + 3) / PW, (y + 3.2) / PH, k, fontsize=5.5, color='#555555', transform=fig.transFigure)
        fig.text((x0 + 26) / PW, (y + 3.0) / PH, v, fontsize=7.5, weight='bold' if k in ('ÇİZİM', 'DURUM') else 'normal', transform=fig.transFigure)
        y -= rh
    # cizgi olcek (1/100: 1 m = 10 mm)
    sx, sy = x0 + 5, 22
    for i in range(5):
        fig.add_artist(Rectangle(((sx + i * 10) / PW, sy / PH), 10 / PW, 1.6 / PH, transform=fig.transFigure,
                                 facecolor='black' if i % 2 == 0 else 'white', edgecolor='black', lw=0.4))
        fig.text((sx + i * 10) / PW, (sy + 2.8) / PH, str(i), fontsize=5, ha='center', transform=fig.transFigure)
    fig.text((sx + 50) / PW, (sy + 2.8) / PH, '5 m', fontsize=5, ha='center', transform=fig.transFigure)
    fig.text((x0 + 3) / PW, 14 / PH, 'IFC Architects  |  çizim birimi cm, kotlar m', fontsize=5, color='#555555', transform=fig.transFigure)

floors_top_down = sorted(DATA['floors'], key=lambda f: f['dy'])  # bodrum, giris, 1.kat
with PdfPages(BASE + '.pdf') as pdf:
    for n, fl in enumerate(floors_top_down, 1):
        fig = plt.figure(figsize=(PW * MM, PH * MM))
        aw, ah = PW - 20 - TB_W - 4, PH - 24  # cizim alani mm
        ax = fig.add_axes([12 / PW, 12 / PH, aw / PW, ah / PH])
        # 1/100 -> 1 mm kagit = 10 cm model
        cx, cy = 690, fl['dy'] + 470
        xl = (cx - aw * 10 / 2, cx + aw * 10 / 2)
        yl = (cy - ah * 10 / 2, cy + ah * 10 / 2)
        draw_model(ax, xl, yl, 1.0)
        title_block(fig, fl, n, len(floors_top_down))
        pdf.savefig(fig)
        plt.close(fig)
    d = pdf.infodict()
    d['Title'] = 'DNM01 Deneme Villa - Konsept kat planlari v01 (TASLAK)'
    d['Author'] = 'IFC Architects'

# PNG: 3 kat yan yana
fig = plt.figure(figsize=(25, 9.6), dpi=100)
fig.patch.set_facecolor('white')
for i, fl in enumerate(floors_top_down):
    ax = fig.add_axes([0.005 + i * 0.333, 0.06, 0.325, 0.86])
    cx, cy = 690, fl['dy'] + 470
    draw_model(ax, (cx - 1000, cx + 1000), (cy - 830, cy + 830), 2.2)
fig.text(0.5, 0.955, 'DNM01 Deneme Villa  |  Konsept kat planları  |  v01 TASLAK  |  1/100 (önizleme ölçeksiz)  |  11.11.2026',
         ha='center', fontsize=17)
fig.text(0.5, 0.02, 'Soldan sağa: BODRUM KAT (-3.50)  ·  GİRİŞ KAT (±0.00)  ·  1.KAT (+3.50).  Sayfa üstü kuzey.', ha='center', fontsize=13)
fig.savefig(BASE + '.png', dpi=100, facecolor='white')
print('ok')
