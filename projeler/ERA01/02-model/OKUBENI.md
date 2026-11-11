# ERA01 ERA Evi: Model klasörü (HACİM)

**Seviye:** KÜTLE + CEPHE · **Birim:** cm (kotlar m) · **Kapsam:** A, B, C, D blokları + arazi, tek site modeli

**Koordinat sistemi:** x, y = DXF'teki `VAZIYET PLANI` bloğunun kendi koordinatları (cm, 1:1). +Y vaziyet planında yukarı (kuzey oku yönü).
**Model z = (mutlak kot − 160.00 m) × 100.** Örnek: A blok zemin kat +1.20 = 174.15 m, modelde z = 1415 cm.
Her blok kendi grubunda (`BLOK_A` ... `BLOK_D`) yerel aks koordinatlarıyla kuruldu. Grup dönüşümü bloğu vaziyetteki yerine taşır.

## Dosyalar
| Dosya | Açıklama |
|---|---|
| `ERA01_model_site_v01.skp` | SketchUp modeli (608.8 KB). 4 blok + arazi, 7 kayıtlı sahne |
| `ERA01_model_sketchup-onizleme_v01.png` | SketchUp'ın kendi küçük resmi (model kamerası = "Perspektif K") |
| `ERA01_model_kus-bakisi_v01.png` | Kontrol görseli: kuş bakışı, güneydoğudan |
| `ERA01_model_aksonometrik_v01.png` | Kontrol görseli: kuzeybatıdan (alçak taraf, bodrumlar görünür) |
| `ERA01_model_perspektif_v01.png` | Kontrol görseli: kuzeyden, göz yüksekliğine yakın |
| `ERA01_model_kat-b2_v01.png`, `..._kat-b1_v01.png`, `..._kat-00_v01.png`, `..._kat-01_v01.png` | Kat üstten görünüşleri (üst katlar, çatı, tavan ve arazi gizli) |
| `kaynak/era01_model_dxfoku_1_inserts.py` | DXF okuma: model alanındaki blokları iç içe açar, attribute dahil (kot etiketleri) |
| `kaynak/era01_model_dxfoku_2_katlar.py` | Kat verisi: brüt alan, mahal, kolon, doğrama ve kapı çizgileri; aks etiketine göre blok yerel koordinatı |
| `kaynak/era01_model_dxfoku_3_gorunus.py` | Görünüşlerden pencere kasaları ve kotları (kontrol) |
| `kaynak/era01_model_dxfoku_4_kesit-kotlari.py` | Kesitlerdeki kot etiketlerini listeler |
| `kaynak/era01_model_gen.py` | Model üretici: kat tablosu, kalınlıklar, çatı, arazi parametreleri dosya başında |
| `kaynak/era01_arazi_noktalari.txt` | Arazi kontrol noktaları (vaziyet planı kotları; `TES` = tesviye kotu) |
| `kaynak/era01_model_pack.py`, `era01_model_png.py`, `era01_model_sketchup.py` | Veriyi SketchUp bulut oturumuna taşıma ve SketchUp kurulum kodu |
| `kaynak/era01_model_render.py`, `era01_model_kameralar.json` | Kontrol görselleri (modelle aynı geometri verisi, aynı sahne kameraları) |
| `kaynak/era01_model_rapor.json` | Üretici raporu: kat, doğrama ve çatı değerleri (makine okunur) |

Kontrol PNG'leri modelle aynı geometri verisinden üretildi (bulut aracı sahne başına görüntü vermiyor). SketchUp'taki görünüm `..._sketchup-onizleme_v01.png` ile doğrulandı.

## Kaynak çizim
- `00-girdi/ERA01_girdi_proje.dxf` (kullanıcının hazır projesi, ŞEF iş emriyle onaylı kabul, 2026-11-11). Birim cm kabul edildi (header mm diyor, ölçüler cm).
- Okunan paftalar: vaziyet ve aplikasyon planı, vaziyet kesitleri, her blok için bodrum, zemin, 1. kat ve çatı planları, 1-1 ve A-A kesitleri, 4 görünüş (GR1-GR4).
- DXF'te "E-F" adı taşıyan bloklar (E_K1_PLAN, F_BK_PLAN, E-F_STR, E-F_CATI PLANI ...) **D bloğun** kat planlarıdır. Vaziyet planında yalnız A, B, C, D blokları var. Ayrı bir E/F binası yok.

## Bloklar ve yerleşim
| Blok | Kat adedi (vaziyet) | ±0.00 | Vaziyetteki iz | Dönüş | Not |
|---|---|---|---|---|---|
| A | 1BK+Z+1N = 3 | 172.95 (subasman +1.20 = 174.15) | 20.00 × 18.00 m, x 2138–4138, y 2510–4310 | 0° | Bodrum 20×18 (havuz, spa, salon); zemin ve 1. kat güney yarıda 20×8.50; zemin katın kuzeyi bodrum üstü teras |
| B | 2BK+Z = 3 | 174.15 | 20.00 × 12.30 m, x 4738–6738, y 1955–3185 | 0° | 2. bodrum otopark 20×20.45 (ZK izinin 8.15 m kuzeyine taşar); 1. bodrum batıda A'ya, doğuda C'ye uzanır (teknik hacimler, koridorlar) |
| C | 1BK+Z = 2 | 174.36 | 7.50 × 18.00 m, x 7338–8088, y 1955–3755 | 90° | Plan çiziminde sol uç = güney (giriş) |
| D | 1BK+Z+1N = 3 | 167.25 | 12.30 × 17.70 m, döndürülmüş dikdörtgen | 66.35° | Zeminde 2 daire; bodrum kuzey yarıda (9.15 m); 1. kat güney 2/3 (10.75 m), kuzeyi teras |

Plan yönleri giriş okları ve vaziyetteki "BLOK GİRİŞİ / DAİRE GİRİŞİ" yazılarıyla eşleştirildi. D bloğun konumu vaziyet poligonunun köşelerinden (8050, 4778) ve uzun kenar yönünden (710, 1621) hesaplandı.

## Kat yükseklikleri ve kotlar (DXF kesitlerinden)
Model döşeme kaplaması üst kotu = kat kotu.

| Blok | Kat | Kat kotu | Göreli | Tavan altı (asma tavan) | Net yükseklik | Kat yüksekliği | Kaynak |
|---|---|---|---|---|---|---|---|
| A | 1. bodrum | 170.15 | −2.80 | 173.05 (varsayım) | 2.90 | 4.00 | 1-1, A-A |
| A | Zemin | 174.15 | +1.20 | 177.05 | 2.90 | 3.50 | 1-1, A-A |
| A | 1. kat | 177.65 | +4.70 | 180.55 | 2.90 | 3.50 (saçağa) | 1-1, A-A |
| A | Çatı | saçak 181.15, mahya 181.88 | +8.20 / +8.93 | | | | 1-1, A-A, çatı planı |
| B | 2. bodrum | 167.15 | −7.00 | 170.05 (varsayım) | 2.90 | 3.00 | 1-1, A-A |
| B | 1. bodrum | 170.15 | −4.00 | 173.05 (varsayım) | 2.90 | 4.00 | 1-1, A-A |
| B | Zemin | 174.15 | ±0.00 | 177.05 | 2.90 | 3.50 (saçağa) | 1-1, A-A |
| B | Çatı | saçak 177.65, mahya 179.17 | +3.50 / +5.02 | | | | 1-1, A-A, çatı planı |
| C | 1. bodrum | 170.36 | −4.00 | 173.26 | 2.90 | 4.00 | 1-1, A-A |
| C | Zemin | 174.36 | ±0.00 | 177.26 | 2.90 | 3.50 (saçağa) | 1-1, A-A |
| C | Çatı | saçak 177.86, mahya 178.75 | +3.50 / +4.39 | | | | 1-1, A-A, çatı planı |
| D | 1. bodrum | 164.25 | −3.00 | 166.65 | 2.40 | 3.00 | 1-1, A-A |
| D | Zemin | 167.25 | ±0.00 | 169.65 | 2.40 | 3.50 | 1-1, A-A |
| D | 1. kat (+ kuzey teras) | 170.75 | +3.50 | 173.65 | 2.90 | 3.50 (saçağa) | 1-1, A-A |
| D | Çatı | saçak 174.25, parapet 174.75, mahya 175.07 | +7.00 / +7.50 / +7.82 | | | | 1-1, A-A |

Döşeme paketi (DXF: kat kotu ile alttaki tavan kotu arası 60 cm): kaplama 10 (üstte) + taşıyıcı döşeme 30 + 10 cm asma tavan boşluğu + tavan 10 (alt yüzü DXF tavan kotunda). Son katta duvarlar çatı döşemesine (saçak −0.30 ... saçak) kadar.

## Pencereler (plan etiketleri TİP / GENİŞLİK / YÜKSEKLİK, görünüşlerle doğrulandı)
Kural (görünüşlerden okundu): pencere üst kasası = tavan kotu − 17 cm. Alt kotu = üst − yükseklik. 280 cm'lik doğramalarda çizimdeki alt kasa döşemenin 7 cm altına iniyor; modelde döşeme kotundan başlatıldı (net 273 cm).
Parapet = döşeme kaplaması üstünden pencere alt kasasına.

| Blok | Kat | Tip | Genişlik × yükseklik (DXF) | Parapet | Üst kasa (kattan) | Adet | Bileşen | Görünüş kontrolü |
|---|---|---|---|---|---|---|---|---|
| A | B1 | P-02 | 520 × 280 | 0 | 273 | 2 | DGR_520x280 | GR3: 170.14–172.92 |
| A | B1 | P-03 | 300 × 280 | 0 | 273 | 2 | DGR_300x280 | GR3/GR4: 170.14–172.92 |
| A | ZK | P-01 | 900 × 630 (giriş/merdiven camlı cephesi, ZK+1. kat) | 0 | 623 | 1 | DGR_900x630 | GR1: 174.11–180.37 |
| A | ZK | P-04 | 250 × 280 | 0 | 273 | 4 | DGR_250x280 | GR3: 174.11–176.89 |
| A | ZK | P-08 | 70 × 70 | 203 | 273 | 5 | DGR_70x70 | GR1/GR3: 176.20–176.89 |
| A | K1 | P-04 | 250 × 280 | 0 | 273 | 2 | DGR_250x280 | GR3: 177.59–180.37 |
| A | K1 | P-05 | 140 × 280 | 0 | 273 | 1 | DGR_140x280 | GR2: 177.59–180.37 |
| A | K1 | P-06 | 520 × 170 | 103 | 273 | 1 | DGR_520x170 | GR3: 178.68–180.37 |
| A | K1 | P-07 | 200 × 170 | 103 | 273 | 1 | DGR_200x170 | GR3: 178.68–180.37 |
| A | K1 | P-08 | 70 × 70 | 203 | 273 | 3 | DGR_70x70 | GR1/GR2: 179.67–180.37 |
| B | ZK | P-11 | 480 × 280 | 0 | 273 | 3 | DGR_480x280 | GR3: 174.08–176.88 |
| B | ZK | P-12 | 270 × 280 | 0 | 273 | 3 | DGR_270x280 | GR2: 174.08–176.88 |
| B | ZK | P-13 | 120 × 280 | 0 | 273 | 2 | DGR_120x280 | GR2/GR4 |
| B | ZK | P-14 | 100 × 280 (yan cephe kapı-pencere) | 0 | 273 | 2 | DGR_100x280 | GR2/GR4 |
| C | B1 | P-16 | 640 × 280 | 0 | 273 | 1 | DGR_640x280 | GR3: 170.29–173.09 |
| C | B1 | P-17 | 440 × 280 | 0 | 273 | 1 | DGR_440x280 | GR4: 170.29–173.09 |
| C | ZK | P-04 | 250 × 280 | 0 | 273 | 1 | DGR_250x280 | GR1: 174.29–177.09 |
| C | ZK | P-14 | 100 × 280 | 0 | 273 | 1 | DGR_100x280 | GR2: 174.29–177.09 |
| C | ZK | P-18 | 440 × 280 | 0 | 273 | 1 | DGR_440x280 | GR4: 174.29–177.09 |
| C | ZK | P-21 | 480 × 170 | 103 | 273 | 2 | DGR_480x170 | GR2: 175.39–177.09 |
| D | B1 | P-25 | 400 × 230 | 0 | 223 | 1 | DGR_400x230 | GR1: 164.18–166.48 |
| D | B1 | P-27 | 250 × 230 | 0 | 223 | 2 | DGR_250x230 | GR1/GR4 |
| D | B1 | P-28 | 200 × 230 | 0 | 223 | 4 | DGR_200x230 | GR2: 164.18–166.48 |
| D | B1 | dış kapı | 106 × 223 | 0 | 223 | 1 | DGR_KAPI_106x223 | plan |
| D | ZK | P-26 | 300 × 230 | 0 | 223 | 1 | DGR_300x230 | GR4: 167.18–169.48 |
| D | ZK | P-28 | 200 × 230 | 0 | 223 | 3 | DGR_200x230 | GR2: 167.18–169.48 |
| D | ZK | P-29 | 150 × 230 | 0 | 223 | 1 | DGR_150x230 | GR4 |
| D | ZK | P-30 | 250 × 180 | 43 | 223 | 3 | DGR_250x180 | GR1/GR4: 167.68–169.48 |
| D | ZK | P-31 | 200 × 180 | 43 | 223 | 4 | DGR_200x180 | GR2: 167.68–169.48 |
| D | ZK | P-32 | 100 × 180 | 43 | 223 | 1 | DGR_100x180 | GR1 |
| D | ZK | P-33 | 70 × 180 | 43 | 223 | 1 | DGR_70x180 | plan |
| D | ZK | daire giriş kapısı | 106 × 223 | 0 | 223 | 2 | DGR_KAPI_106x223 | plan |
| D | K1 | P-03 | 300 × 280 (terasa) | 0 | 273 | 1 | DGR_300x280 | plan |
| D | K1 | P-23 | 400 × 280 (terasa) | 0 | 273 | 1 | DGR_400x280 | plan |
| D | K1 | P-24 | 200 × 280 (terasa) | 0 | 273 | 1 | DGR_200x280 | plan |
| D | K1 | P-26 | 300 × 230 | 43 | 273 | 2 | DGR_300x230 | GR4: 171.18–173.48 |
| D | K1 | P-28 | 200 × 230 | 43 | 273 | 1 | DGR_200x230 | GR2: 171.18–173.48 |
| D | K1 | P-08 | 70 × 70 | 203 | 273 | 2 | DGR_70x70 | GR2/GR3: 172.78–173.48 |
| D | K1 | giriş kapısı | 106 × 273 | 0 | 273 | 1 | DGR_KAPI_106x273 | plan |

Doğrama: kasa 5 cm, derinlik 6 cm, dış duvarın ortasında. Bölme sayısı genişlik/150 yuvarlanarak (her bölme ≥ 100 cm, eşit). Yüksekliği 240'ı aşanlarda tek yatay kayıt ortada; P-01'de (630) iki kayıt. Cam tek yüzey (`M_DOGRAMA_CAM`, %60 saydam). Ayrıntılı kasa bölmeleri DXF görünüşlerinden farklı olabilir (ofis standardı uygulandı).

## Çatılar
| Blok | Tip | Saçak izdüşümü | Saçak kotu | Mahya kotu | Eğim (model) | Not |
|---|---|---|---|---|---|---|
| A | 4 yöne kırma | 22.20 × 9.70 m (110 cm saçak) | 181.15 | 181.88 | %10.9 | mahya x 3.75–16.25 |
| B | 4 yöne kırma | 22.20 × 14.50 m | 177.65 | 179.17 | %18.2 | |
| C | 4 yöne kırma | 20.20 × 9.70 m | 177.86 | 178.75 | %14.2 | |
| D | 4 yöne kırma, parapet içinde | 10.15 × 11.90 m (parapet içi) | 174.25 | 175.07 | %12.2 | parapet +7.50 (174.75), 20 cm; kuzey teras +3.50 (170.75) |

Model kuralı: çatı alt yüzü saçak ucunda saçak kotunda, üst yüzü mahyada mahya kotunda; paket 20 cm (düşey). Çatı döşemesi saçak −0.30 ... saçak.

## Arazi
- **Kademeli (teraslı)**, smooth yok. Parsel sınırı içinde (vaziyet planı `0_IFC_Parsel Sınırı`).
- Kontrol noktaları: vaziyet planındaki parsel köşe, yol ve proje kotları (79 nokta) + her bloğun 1.40 m dışında, 2.50 m aralıklı, en yakın "tesviye" kotunu alan halka noktaları (138 nokta). Ters mesafe ağırlıklı yüzey, 1 m ızgara.
- Kademeler: 161, 162, 163, **164.25**, 165, 166, **167.25**, 168, 169, **170.15**, **170.36**, 171, 172, **172.95**, **174.15**, **174.36**, 175, 176, 177 (kalın: blok tesviye kotları). Taban 160.00. 26 kademe cismi.
- Blok çevresindeki tesviyeler (DXF): A güney/doğu/batı 172.95, kuzey 170.15 (bodrum açık); B çevresi 174.15 (iki bodrum gömülü); C güney/doğu/batı 174.36, kuzey 170.36; D güney/batı 167.25, kuzey/doğu 164.25 (bodrum açık); D 1. kat girişi güneyde 170.75.
- Arazi, her kademenin kot aralığına giren katların izinde boşaltıldı (bloklar toprağa gömülü oturur; toprak altı bodrumlar ve B2'nin kuzey kısmı toprakla örtülü).
- Mevcut doğal zemin (blok köşe kotları, vaziyet): A 174.79 güney – 170.83/171.40 kuzey; B 175.57–176.06 güney, 172.81–173.16 kuzey; D 164.03–170.16. Proje tesviyesi esas alındı.
- İstinat duvarları, şevler, rampalar, yollar, merdivenler, bahçe duvarları modellenmedi.

## Grup ve tag yapısı
```
BLOK_A / BLOK_B / BLOK_C / BLOK_D            (tag BLOK_x; dönüşüm = vaziyetteki yer)
  x_KAT_B2 / x_KAT_B1 / x_KAT_00 / x_KAT_01  (tag KAT_B2, KAT_B1, KAT_00, KAT_01)
    TASIYICI        KOLON_* bileşen örnekleri, PERDE_* (dikdörtgen olmayan perde parçaları)
    DIS_DUVAR       DD_<blok>_<kat>_nn (kenar başına parça, doğrama boşlukları iç döngü/çentik), PARAPET_<blok>_<kat> (teras parapeti)
    IC_DUVAR        ID_<blok>_<kat>_nn
    CEPHE_KAPLAMA   CK_<blok>_<kat>_nn (20 cm, dış duvar çizgisinin dışında, boşluklar açık)
    DOSEME          DOSEME_<blok>_<kat> (merdiven boşlukları açık; alt katın taşan kısmını da örter)
    DOSEME_KAPLAMA
      DOSEME_KAPLAMA_KURU    DK_<MAHAL>, DK_TERAS_*
      DOSEME_KAPLAMA_ISLAK   DK_<MAHAL>
    TAVAN           TV_<MAHAL>
    DOGRAMA         DGR_* bileşen örnekleri (ad: <tip>_<bileşen>_<blok><kat>)
    MERDIVEN        MRD_<blok>_<kat>_KOL1/KOL2/SAHANLIK (bir üst kata çıkan merdiven)
  x_KAT_CATI (tag KAT_CATI)
    DOSEME          DOSEME_CATI_<blok>
    CATI            CATI_KIRMA_<blok>, PARAPET_CATI_D
ARAZI (tag ARAZI)   ARAZI_KADEME_<kot>_nn
```
Tag'ler: BLOK_A, BLOK_B, BLOK_C, BLOK_D, KAT_B2, KAT_B1, KAT_00, KAT_01, KAT_CATI, TASIYICI, DIS_DUVAR, IC_DUVAR, CEPHE_KAPLAMA, DOSEME, DOSEME_KAPLAMA, DOSEME_KAPLAMA_KURU, DOSEME_KAPLAMA_ISLAK, TAVAN, DOGRAMA, MERDIVEN, CATI, ARAZI. Yaprak gruplar tag'siz (Untagged), tag üst grupta.

Döşeme kaplaması alt grupları:
| Blok / kat | KURU | ISLAK |
|---|---|---|
| A B1 | HOL, SOYUNMA_ALANI, DINLENME_ALANI, KORIDOR, MERDIVEN, MAHAL | HAMAM, HAVUZ, SOK_DUS, SAUNA, BANYO, SALON_MUTFAK |
| A ZK | TERAS, YATAK_ODASI ×4, GIYINME_ODASI ×4, KORIDOR, TEMIZLIK_ODASI, MAHAL | BANYO ×4 |
| A K1 | GIYINME_ODASI ×2, YATAK_ODASI, KAT_BAHCESI, HOL, E_YATAK_ODASI, KORIDOR, DEPO, MAHAL | BANYO, E_BANYO |
| B B2 | TEKNIK_ALAN ×2, HOL, OTOPARK, MERDIVEN, MAHAL | - |
| B B1 | TERAS (B2 üstü, toprak altında), TEKNIK_ALAN ×7, KORIDOR ×2, MAHAL ×2 | WC ×2 |
| B ZK | TERAS ×3 (B1 uzantıları üstü), YATAK_ODASI, YEMEK_ALANI, KORIDOR, GIRIS_HOLU, SALON, MAHAL | MUTFAK, BANYO |
| C B1 | MESCIT, YATAK_ODASI, MERDIVEN, KORIDOR | BANYO |
| C ZK | GIRIS_HOLU, BALKON, MAHAL | WC, SALON_MUTFAK |
| D B1 | M_K_A, YATAK_ODASI ×2, SALON, KORIDOR, GIRIS_HOLU | E_BANYO, MUTFAK, BANYO |
| D ZK | YATAK_ODASI ×4, M_K_A ×2, KORIDOR ×2, GIRIS_HOLU ×2, SALON ×2 | BANYO ×2, E_BANYO ×2, MUTFAK ×2 |
| D K1 | TERAS, M_K_A, SALON, YATAK_ODASI, KORIDOR, GIRIS_HOLU | MUTFAK, BANYO, E_BANYO |

"MAHAL": DXF'te mahal poligonu olmayan, duvar sayılmayacak kadar geniş artık alan (şaft ve merdiven yanı boşluklar).

## Bileşenler
| Bileşen | Adet | | Bileşen | Adet |
|---|---|---|---|---|
| DGR_70x70 | 10 | | DGR_300x280 | 3 |
| DGR_70x180 | 1 | | DGR_400x230 | 1 |
| DGR_100x180 | 1 | | DGR_400x280 | 1 |
| DGR_100x280 | 3 | | DGR_440x280 | 2 |
| DGR_120x280 | 2 | | DGR_480x170 | 2 |
| DGR_140x280 | 1 | | DGR_480x280 | 3 |
| DGR_150x230 | 1 | | DGR_520x170 | 1 |
| DGR_200x170 | 1 | | DGR_520x280 | 2 |
| DGR_200x180 | 4 | | DGR_640x280 | 1 |
| DGR_200x230 | 8 | | DGR_900x630 | 1 |
| DGR_200x280 | 1 | | DGR_KAPI_106x223 | 3 |
| DGR_250x180 | 3 | | DGR_KAPI_106x273 | 1 |
| DGR_250x230 | 2 | | KOLON_40x20 (H270/320/330/370) | 26 |
| DGR_250x280 | 7 | | KOLON_60x20 (H270/320/330/370) | 22 |
| DGR_270x280 | 3 | | KOLON_60x40 (H270/320/330/370) | 17 |
| DGR_300x230 | 3 | | KOLON_40x40 (H320/330/370) | 6 |
| | | | KOLON_185x40 (H320/330/370) | 3 |

Toplam 46 bileşen tanımı, 146 örnek (72 doğrama, 74 kolon). Kolon bileşenleri kat yüksekliğine göre ayrı tanım (H = duvar yüksekliği). Kolonların yalnız dış duvar şeridinin içine taşan kısmı ayrı eleman; dış duvar içinde kalan kısmı duvarla bir.

## Malzemeler
M_TASIYICI #6E6E6E, M_DIS_DUVAR #A6A6A6, M_IC_DUVAR #D0D0D0, M_CEPHE_KAPLAMA #E6E6E6, M_DOSEME #8C8C8C, M_DOSEME_KAPLAMA_KURU #F2F2F2, M_DOSEME_KAPLAMA_ISLAK #DADDE0, M_TAVAN #FAFAFA, M_DOGRAMA_KASA #4A4A4A, M_DOGRAMA_CAM açık gri %60 saydam, M_MERDIVEN #BDBDBD, M_CATI #959595, M_ARAZI #C8C8C8. Doku yok.

## Sahneler
Perspektif K (model kamerası), Aksonometrik KB (paralel), Kus bakisi GD, KAT_B2 ustten, KAT_B1 ustten, KAT_00 ustten, KAT_01 ustten (paralel; üstteki kat tag'leri + KAT_CATI + TAVAN + ARAZI gizli). Stil: ARCHITECTURAL_EXTERIOR.

## Model istatistiği
| | Değer |
|---|---|
| Yaprak grup | 475 (+ 146 bileşen örneği, 46 tanım) |
| Toplam yüzey / kenar (örnekler açılmış) | 7 641 yüzey, 19 335 kenar |
| Blok başına yüzey | A 2 347, B 1 755, C 808, D 1 923, arazi 808 |
| Katı (solid) kontrolü | Tüm gruplar katı; yalnız cam yüzeyleri tek yüzey (beklenen) |
| Dosya boyutu | 608.8 KB |

## Çizimle çelişkiler ve varsayımlar
1. **D blok çatı kotu:** çatı planı başlığı "ÇATI KATI +3.50 (170.75)". Kesitler saçak +7.00 (174.25), parapet +7.50, mahya +7.82 veriyor. +3.50, zemin kat üstündeki **kuzey teras** (1. kat seviyesi) kotu. Model: teras +3.50, kırma çatı +7.00/+7.82, 1. kat yalnız güney 10.75 m.
2. **E-F adlandırması:** "E-F" blokları D bloğun planları. B bloğun bodrum brüt/net alanları DXF'te "D BLOK_B1/B2_BRUT ALAN" ve "A_B1_NET ALAN" adlarıyla duruyor. Konumlarına göre B blok olarak kullanıldı.
3. **A kesit yazım hatası:** "−3.30 (169.95)" (−3.30 + 172.95 = 169.65). Modeli etkilemiyor (temel altı).
4. **B GR1 görünüşü** A bloğa ait bir cepheyi gösteriyor (900×630 camlı cephe, 1. kat pencereleri; B tek katlı). Kullanılmadı. B pencereleri plan etiketleri ve GR2-GR4'ten.
5. A 1. kat ve C blok katlarında brüt alan poligonu yok: A 1. kat için zemin kat izi (20.00 × 8.50), C için aks/duvar sınırı (18.00 × 7.50) kullanıldı.
6. Bodrum tavan kotları (A B1, B B1, B B2) kesitlerde yazılı değil: kat kotu + 2.90 alındı.
7. **Döşeme paketi:** DXF'te 60 cm (ör. tavan +2.90, üst kat +3.50). Ofis standardı 50 cm. DXF'e uyuldu: 10 kaplama + 30 taşıyıcı + 10 boşluk + 10 tavan.
8. **Cephe kaplaması** ofis standardına göre dış duvar çizgisinin 20 cm dışına eklendi: bloklar vaziyet izine göre her yönde 20 cm büyük. Dış duvar 20 cm (planlarda ölçülen).
9. 280 cm'lik doğramalar DXF'te döşemenin 7 cm altından başlıyor. Model döşeme kotundan başlatıldı (273 cm).
10. A P-01 (900×630) zemin kattan 1. kat üst kasasına kadar tek parça. 1. kat döşeme kenarı camın arkasından geçiyor (görünüşteki ara bant ile uyumlu).
11. Atlanan doğramalar: C ZK P-20 (etiket 260, çizim 77 cm, balkon köşesi) ve P-22 (740, balkon camlaması, cephe çizgisinde değil); B B1 P-15 (240×90, toprak altı koridor, dış çizgiye oturmuyor). C ZK BALKON iç mahal gibi modellendi.
12. A 1. kat "KAT BAHÇESİ" kapalı mahal gibi modellendi (çatı ve tavan üstünde).
13. B 2. bodrumun kuzey kısmı (8.15 m) ve B 1. bodrumun batı/doğu uzantıları toprak altında. Üstleri teras döşemesi + 100 cm parapet; araziyle örtülü. Kuzeydeki otopark girişi (rampa, garaj kapısı, 167.15 kotundaki yarma) modellenmedi.
14. Teras korkulukları 100 cm dolu parapet (DXF: korkuluk h 110). D çatı parapeti 20 cm, +7.50.
15. Modellenmeyenler: iç kapılar ve iç kapı boşlukları (iç duvarlar sürekli), mobilya, korkuluk, dış merdivenler, istinat ve bahçe duvarları, rampalar, havuz çukuru, asansör, bacalar (+8.80 / +7.60 "parapet" etiketleri), saçak oluğu.
16. Merdivenler basitleştirilmiş basamaklı kütle (tek kol ya da U, 20 cm döşemeli), bir üst kata. Gerçek kol düzeni DXF'ten birebir alınmadı.
17. SALON+MUTFAK mahalleri (A B1, C ZK) adındaki "MUTFAK" nedeniyle ıslak grupta.
18. Arazi yaklaşık: ters mesafe ağırlıklı yüzey + 1 m kademe. Vaziyet ve vaziyet kesitlerindeki kotlarla ±0.5 m mertebesinde uyumlu. Parsel dışı (yollar, komşular) yok.
19. Model datumu 160.00 m (z = 0). ±0.00 kotları blok başına farklı (172.95 / 174.15 / 174.36 / 167.25).

## Açık sorular (önerilen varsayımla)
1. Cephe kaplaması standart gibi dış çizginin 20 cm dışında mı kalsın (bloklar vaziyete göre 40 cm büyük), yoksa DXF dış çizgisi bitmiş yüz mü sayılsın? **Öneri:** standart (mevcut durum).
2. D blok çatısı: saçak +7.00, mahya +7.82, 1. kat kuzeyi teras (+3.50) yorumu doğru mu? **Öneri:** evet (kesitlerle uyumlu).
3. B blok otopark girişi (kuzey, 167.15) ve Y şeklindeki rampa/yarma modele eklensin mi? **Öneri:** v02'de basit yarma + garaj kapısı boşluğu.
4. A 1. kat "KAT BAHÇESİ" açık avlu mu? **Öneri:** açık avlu (çatı, tavan ve döşeme kaplaması boşaltılır, avlu cepheleri camlı).
5. SALON+MUTFAK mahalleri kuru gruba mı alınsın? **Öneri:** kuru.
6. Arazi parsel dışına (yollar, kaldırım) genişletilsin mi? **Öneri:** hayır, gerekirse yalnız yol şeridi.
