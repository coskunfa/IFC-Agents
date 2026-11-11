# ERA01 ERA Evi: Boyama klasörü (PAFTA)

**Güncel sürüm: v02** (DENETÇİ raporu `05-kontrol/ERA01_kontrol_raporu_v01.md` düzeltme turu 1). v01 dosyaları arşiv olarak duruyor, silinmedi.
**Stil:** KONSEPT GRİ (sunum-standardi §2-A), DNM01 ile aynı dil. Başlık "MİMARİ KONSEPT PROJE", aşama KONSEPT.
**Çıktı:** 600 dpi, sRGB, JPEG q92 4:4:4. Bütün paftalar A3 yatay.
**Font:** Carlito (Calibri'nin metrik eşdeğeri; sistemde Calibri yok).
**Girdi:** `00-girdi/ERA01_girdi_proje.dxf`. Bu projede onaylı çizim kabul edildi, ÇİZGİ yok. Birim cm.

## Dosyalar (v02)
| Dosya | Ölçek | px/cm | İçerik |
|---|---|---|---|
| `ERA01_boyama_vaziyet_v02.jpg` | 1/500 | 0.4724 | Site: 4 blok çatı planı, zemin kat izleri, teraslar, yollar, yaya yolları, set/istinat duvarları, şev, rampa, açık otopark, kotlar, girişler, lejant |
| `ERA01_boyama_A-blok-1-bodrum_v02.jpg` | 1/100 | 2.3622 | A 1. bodrum (-2.80) |
| `ERA01_boyama_A-blok-zemin-kat_v02.jpg` | 1/100 | 2.3622 | A zemin (+1.20), teras tefrişi, korkuluk, alçak bahçe |
| `ERA01_boyama_A-blok-1-kat_v02.jpg` | 1/100 | 2.3622 | A 1. kat (+4.70) |
| `ERA01_boyama_A-blok-kat-planlari_v02.jpg` | 1/200 | 1.1811 | A toplu pafta, toplam kapalı alan 702.00 m² |
| `ERA01_boyama_B-blok-2-bodrum_v02.jpg` | 1/150 | 1.5748 | B 2. bodrum, otopark (-7.00) |
| `ERA01_boyama_B-blok-1-bodrum_v02.jpg` | 1/150 | 1.5748 | B 1. bodrum (-4.00) |
| `ERA01_boyama_B-blok-zemin-kat_v02.jpg` | 1/100 | 2.3622 | B zemin (±0.00) |
| `ERA01_boyama_B-blok-kat-planlari_v02.jpg` | 1/250 | 0.9449 | B toplu pafta, toplam kapalı alan 954.12 m² |
| `ERA01_boyama_C-blok-1-bodrum_v02.jpg` | 1/100 | 2.3622 | C 1. bodrum (-4.00) |
| `ERA01_boyama_C-blok-zemin-kat_v02.jpg` | 1/100 | 2.3622 | C zemin (±0.00) |
| `ERA01_boyama_C-blok-kat-planlari_v02.jpg` | 1/150 | 1.5748 | C toplu pafta, toplam kapalı alan 270.00 m² |
| `ERA01_boyama_D-blok-1-bodrum_v02.jpg` | 1/100 | 2.3622 | D 1. bodrum (-3.00) |
| `ERA01_boyama_D-blok-zemin-kat_v02.jpg` | 1/100 | 2.3622 | D zemin, D1+D2 (±0.00) |
| `ERA01_boyama_D-blok-1-kat_v02.jpg` | 1/100 | 2.3622 | D 1. kat (+3.50), teras tefrişi |
| `ERA01_boyama_D-blok-kat-planlari_v02.jpg` | 1/150 | 1.5748 | D toplu pafta, toplam kapalı alan 460.02 m² |
| `onizleme/*_v02_onizleme.png` | 2000 px | - | Kontrol önizlemeleri |

Kat paftalarında A3'e 1/100 sığmayanlar (B 2. ve 1. bodrum) 1/150'de. A zemin, 1/100'de kalsın diye peyzaj bandı kenarda kırpıldı.

## Kaynak (kaynak/)
`python3 era01_dxf_duzlestir.py` (DXF önbelleği `era01_geo.pkl`, yaklaşık 12 sn; repoda tutulmuyor) → `python3 era01_boyama.py [vaziyet] [katlar] [bloklar]`. `era01_vaziyet_donusum.py` plandan vaziyete dönüşümü üretir.
- `era01_katlar.py`: pafta çerçeveleri ve kat-INSERT eşleşmesi
- `era01_plan.py`: kat planı motoru · `era01_vaziyet.py`: vaziyet motoru · `era01_ortak.py`: palet, pafta düzeni, sürüm
- `era01_ozet.json`: kat bazında mahaller, net, açık alan, brüt (kaynağıyla), dosya ve ölçek, numaralanan mahaller, eklenen tefriş, blok toplam kapalı alanları

Gereken Python paketleri: ezdxf, pycairo, Pillow, numpy, scipy, shapely.

## Yöntem
- Duvar, kolon/perde, mahal (`0_IFC_Area`), brüt, kapı, pencere (`3_IFC_Window`), merdiven, şaft ve mobilya DXF'ten birebir alındı. Geometri kaydırılmadı.
- Duvar poşesi: mahal poligonları ile duvar ve kolon çizgileri arasındaki kapalı bölgeler raster bileşen analiziyle bulundu. Kapı açıklıkları, pencereler ve asansör boşlukları ayrı sınıflandı.
- **Mahal yazıları (v02):** Bütün paftalarda tek tip yazı boyu ve kalınlığı var: ad kalın, alan normal. Yazı kutusu mahal sınırından en az 8 cm içeride duruyor ve giriş üçgeninin 75 cm çevresine girmiyor. Ad tek satıra sığmazsa iki satıra bölünüyor. Hiçbir biçimde sığmayan mahal (çoğunlukla dar merdiven, koridor ve WC) yalnız kendisi numaralanıyor ve plan yanındaki listede yer alıyor. Diğer bütün mahallerde ad doğrudan mahalin içinde.
- Mahal adları tek yazımda: "E.BANYO" → "E. BANYO".
- Alanlar `0_IFC_Area` poligonlarından hesaplandı (0.10 m² hassasiyet).
- **Brüt alan (v02 kuralı):** Terassız kapalı kat alanı, dıştan dışa. Teras, balkon ve kat bahçesi "AÇIK ALAN" satırında ayrı gösteriliyor.
- Vaziyette blok izleri, köşe kotu sembolleri eşleştirilerek konuldu (ölçek 0.25 sabit; A ve B 0°, C 90°, D 66.35°).
  - A, B ve C çatıları zemin kat brüt izine ortalandı.
  - **D (v02):** Çatı planı bütün olarak (17.70 m iz, teras dahil) zemin kat iziyle çakıştırıldı. Kırma çatı böylece güney ucuna yaslandı; kuzeydeki 7.15 m'lik 1. kat terası "zemin kat izi / teras" tonunda görünüyor.

## Alanlar (m²)
| Kat | Net | Açık alan | Brüt (terassız) | Brüt kaynağı |
|---|---|---|---|---|
| A 1. bodrum | 327.40 | - | 362.00 | DXF brüt poligonu |
| A zemin | 150.40 | 190.00 teras | 170.00 | DXF brüt poligonu |
| A 1. kat | 122.80 | 25.00 kat bahçesi | 170.00 | DXF şema KAT BRÜTÜ |
| B 2. bodrum | 376.00 | - | 409.00 | DXF brüt poligonu |
| B 1. bodrum | 258.50 | - | 301.68 | DXF brüt poligonu |
| B zemin | 217.20 | - | 243.44 | DXF brüt poligonu |
| C 1. bodrum | 117.80 | - | 135.00 | DXF şema KAT BRÜTÜ |
| C zemin | 107.10 | 13.60 balkon | 135.00 | DXF şema KAT BRÜTÜ |
| D 1. bodrum | 97.20 | - | 112.54 | DXF brüt poligonu |
| D zemin | 191.40 | - | 217.71 | DXF kat brüt poligonu (daireler 107.93 + 109.78) |
| D 1. kat | 114.20 | 82.70 teras | **129.77** | DXF şema KAT BRÜTÜ (`D_CK_SEMA`). Plan poligonu 217.71 terası da kapsıyor, kullanılmadı |

**Toplam kapalı alan:** A 702.00 · B 954.12 · C 270.00 · D 460.02 m².

## v02'de yapılan düzeltmeler
| Madde | Yapılan |
|---|---|
| H1 | D 1. kat brüt alanı 129.77 m², teras 82.70 m² ayrı. D 1. kat ve D toplu paftası, özet ve OKUBENI buna göre güncellendi |
| H2 | Vaziyette D çatısı güney ucuna yaslandı, kuzey terası görünür |
| U1 | A zemin terasına (190 m²) ve D 1. kat terasına (82.70 m²) dış oturma grubu (3'lü 220×85, 2 tekli 80×80, sehpa 100×60), 6 kişilik dış yemek masası (180×90) ve saksılar (Ø60) eklendi. Saksılar mevcut DXF öğeleriyle çakışıyorsa konmadı. Tefriş kuralına göre teras/bahçe |
| U2 | Yazılar tek tip; duvara ve giriş üçgenine binmiyor |
| U3 / Soru 2 | Numara ve liste yalnız adı sığmayan mahalde |
| U4 / Soru 3 | Başlık "MİMARİ KONSEPT PROJE", aşama KONSEPT |
| U5 / Soru 4 | Bütün paftalar A3 |
| U6 | Toplu paftalarda sağ altta TOPLAM KAPALI ALAN |
| U7 | Vaziyette DXF'teki "YAYA YOLU" şeritleri sert zemin tonunda (#DDD6C9); lejanta eklendi |
| U8 | A zemin teras kenarına çift çizgi korkuluk eklendi; teras çevresindeki alçak zemin ayrı tonda ve "ALÇAK BAHÇE -2.80 (170.15)" kotuyla gösterildi |
| U9 | "E. BANYO" tek yazım |

## Varsayımlar ve notlar
1. **Blok sayısı:** 4 blok var: A, B, C, D. DXF'teki "E-F_..." blokları D'nin planları. A'nın tek bodrumu var; -7.00 kotu B'nin 2. bodrumuna (otopark) ait.
2. **Pencere ve doğrama** DXF planlarından birebir alındı. Tahmini pencere eklenmedi.
3. **Kuzey okları** DXF kuzey sembolüne göre konuldu: A, B ve vaziyet 21.29°, C 291.29°, D 314.94°. C ve D planları DXF paftasındaki yönleriyle verildi.
4. **Zemin bantları:** Zemin katlarda 2.5 m peyzaj bandı var. Bodrumlarda gri toprak bandı var. Üst katlar beyaz zeminde.
5. **Mahal poligonu olmayan alanlar** (asansör kuyuları vb.) gri ya da boş bırakıldı; alan toplamına girmedi.
6. **Vaziyet zemin sınıfları:** DXF'te kapalı sert zemin poligonu yok. Bölgeler çizgilerden ve etiketlerden çıkarıldı. Etiketsiz alanlar çim, ince şeritler şev taşı kabul edildi.
7. **DXF'teki tutarsızlıklar** (kullanıcının bilgisine):
   - D 1. kat ve çatı başlıklarında ikisi de +3.50 yazıyor (kesitlere göre saçak +7.00).
   - `D_K1 BRUT ALAN` poligonu 217.71 m² ve terası da içeriyor.
   - A zemin şemasındaki 363.96 m² blok konturu, terası da kapsıyor.
