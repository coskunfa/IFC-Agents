# ERA01 ERA Evi: Boyama klasörü (PAFTA)

**Stil:** KONSEPT GRİ (sunum-standardi §2-A), DNM01 boyamalarıyla aynı dil · **Çözünürlük:** 600 dpi, sRGB, JPEG q92 4:4:4 · **Font:** Carlito (Calibri'nin metrik eşdeğeri; sistemde Calibri yok)
**Girdi:** `00-girdi/ERA01_girdi_proje.dxf`. Bu projede onaylı çizim kabul edildi, ÇİZGİ yok. Birim cm.

## Dosyalar
| Dosya | Kağıt / ölçek | px/cm | İçerik |
|---|---|---|---|
| `ERA01_boyama_vaziyet_v01.jpg` | A3 yatay, 1/500 | 0.4724 | Tüm site: 4 blok çatı planı, zemin kat izleri, yollar, set/istinat duvarları, şev, rampa, açık otopark, kotlar, girişler, lejant |
| `ERA01_boyama_A-blok-1-bodrum_v01.jpg` | A3, 1/100 | 2.3622 | A Blok 1. bodrum (-2.80) |
| `ERA01_boyama_A-blok-zemin-kat_v01.jpg` | A2, 1/100 | 2.3622 | A Blok zemin kat (+1.20) |
| `ERA01_boyama_A-blok-1-kat_v01.jpg` | A3, 1/100 | 2.3622 | A Blok 1. kat (+4.70) |
| `ERA01_boyama_A-blok-kat-planlari_v01.jpg` | A3, 1/200 | 1.1811 | A Blok toplu pafta |
| `ERA01_boyama_B-blok-2-bodrum_v01.jpg` | A2, 1/100 | 2.3622 | B Blok 2. bodrum, kapalı otopark (-7.00) |
| `ERA01_boyama_B-blok-1-bodrum_v01.jpg` | A2, 1/100 | 2.3622 | B Blok 1. bodrum (-4.00) |
| `ERA01_boyama_B-blok-zemin-kat_v01.jpg` | A3, 1/100 | 2.3622 | B Blok zemin kat (±0.00) |
| `ERA01_boyama_B-blok-kat-planlari_v01.jpg` | A3, 1/250 | 0.9449 | B Blok toplu pafta |
| `ERA01_boyama_C-blok-1-bodrum_v01.jpg` | A3, 1/100 | 2.3622 | C Blok 1. bodrum (-4.00) |
| `ERA01_boyama_C-blok-zemin-kat_v01.jpg` | A3, 1/100 | 2.3622 | C Blok zemin kat (±0.00) |
| `ERA01_boyama_C-blok-kat-planlari_v01.jpg` | A3, 1/150 | 1.5748 | C Blok toplu pafta |
| `ERA01_boyama_D-blok-1-bodrum_v01.jpg` | A3, 1/100 | 2.3622 | D Blok 1. bodrum (-3.00) |
| `ERA01_boyama_D-blok-zemin-kat_v01.jpg` | A3, 1/100 | 2.3622 | D Blok zemin kat, D1+D2 (±0.00) |
| `ERA01_boyama_D-blok-1-kat_v01.jpg` | A3, 1/100 | 2.3622 | D Blok 1. kat (+3.50) |
| `ERA01_boyama_D-blok-kat-planlari_v01.jpg` | A3, 1/200 | 1.1811 | D Blok toplu pafta |
| `onizleme/*_onizleme.png` | 2000 px | - | Kontrol önizlemeleri |

PSD istenmediği için üretilmedi.

## Kaynak (kaynak/)
`python3 era01_dxf_duzlestir.py` (DXF'teki bütün INSERT'leri açar ve `era01_geo.pkl` önbelleğini yazar, yaklaşık 12 sn. Önbellek repoda tutulmuyor.) → `python3 era01_vaziyet_donusum.py` (isteğe bağlı) → `python3 era01_boyama.py [vaziyet] [katlar] [bloklar] [blok=ABCD]`.
- `era01_katlar.py`: hangi pafta çerçevesi ve hangi INSERT'lerin hangi kata ait olduğu
- `era01_plan.py`: kat planı motoru · `era01_vaziyet.py`: vaziyet motoru · `era01_ortak.py`: palet ve pafta düzeni
- `era01_ozet.json`: kat bazında mahal alanları, net/brüt değerleri ve dosya-ölçek kayıtları

Gereken Python paketleri: ezdxf, pycairo, Pillow, numpy, scipy, shapely.

## Yöntem
- Duvar, kolon/perde (`1_IFC_Concrete_Section`, `0_IFC_Hatch_Structure`), mahal poligonu (`0_IFC_Area`), brüt poligon, kapı, pencere (`3_IFC_Window`), merdiven, şaft ve mobilya DXF'ten birebir alındı. Geometri kaydırılmadı.
- Duvar poşesi şöyle çıkarıldı: mahal poligonları ile duvar ve kolon çizgileri arasındaki kapalı bölgeler raster bileşen analiziyle bulundu. Kapı açıklıkları (kapı bloğu sınırı ve kanat yayı), pencereler (pencere bloğu sınırı) ve asansör kuyusu gibi boşluklar ayrı sınıflandı.
- Mahal adı ve alanı: ad DXF'teki mahal yazısından, alan `0_IFC_Area` poligonundan hesaplandı (0.10 m² hassasiyet). Bir katta tek bir mahal adı bile sığmazsa o katın bütün mahalleri numaralandı ve plan yanına liste kondu (D zemin kat 1/100, toplu paftalarda bazı katlar).
- Mobilya: DXF tefrişi kullanıldı (beyaz dolgu, ince gri kontur, yumuşak gölge). Ekleme yapılmadı.
- Vaziyet: zemin kat izi ve giriş okları, plan ve vaziyetteki köşe kotu sembolleri eşleştirilerek yerleştirildi (ölçek 0.25 sabit; A ve B 0°, C 90°, D 66.35°; B'de kalan sapma ±30 cm). Çatı planları ayrı paftada durduğu için saçak poligonu zemin kat brüt izine ortalanarak konuldu.

## Alanlar (net = kapalı mahaller; teras/balkon/kat bahçesi ayrı)
| Kat | Net toplam | Açık alan | Brüt | Brüt kaynağı |
|---|---|---|---|---|
| A 1. bodrum | 327.40 | - | 362.00 | DXF brüt poligonu |
| A zemin | 150.40 | 190.00 (teras) | 170.00 | DXF brüt poligonu |
| A 1. kat | 122.80 | 25.00 (kat bahçesi) | 170.00 | DXF şema "KAT BRÜTÜ" |
| B 2. bodrum | 376.00 | - | 409.00 | DXF brüt poligonu |
| B 1. bodrum | 258.50 | - | 301.68 | DXF brüt poligonu |
| B zemin | 217.20 | - | 243.44 | DXF brüt poligonu |
| C 1. bodrum | 117.80 | - | 135.00 | DXF şema "KAT BRÜTÜ" |
| C zemin | 107.10 | 13.60 (balkon) | 135.00 | DXF şema "KAT BRÜTÜ" |
| D 1. bodrum | 97.20 | - | 112.54 | DXF brüt poligonu |
| D zemin | 191.40 | - | 217.71 | DXF kat brüt poligonu (daire brütleri 107.93 + 109.78) |
| D 1. kat | 114.20 | 82.70 (teras) | 217.71 | DXF brüt poligonu (bkz. Soru 4) |

Net toplam, yuvarlanmış mahal alanlarının toplamıdır.

## Varsayımlar ve notlar
1. **Blok sayısı:** Vaziyette 4 blok var: A, B, C, D. DXF'teki "E-F_..." blokları D Blok'a ait (D Blok ikiz konut D1/D2). Ayrı bir E ya da F bloğu yok.
2. **Kat listesi:** A Blok'ta tek bodrum var (-2.80). "-7.00 (167.15)" kotu B Blok 2. bodrumuna (kapalı otopark) ait; proje.md'deki "A 2. bodrum" ifadesi düzeltilmeli. Çatı planları ayrı kat paftası yapılmadı, vaziyette çatı görünümü olarak kullanıldı.
3. **Pencere ve doğrama** DXF planlarından (`*_DOGRAMA` blokları) birebir alındı. Tahmini pencere eklenmedi.
4. **Plan yönü:** C ve D planları DXF paftasındaki yönleriyle verildi (C 270° döndürülmüş). Kuzey oku her paftada DXF'teki kuzey sembolünün dönüşüne göre konuldu: A ve B 21.29°, C 291.29°, D 314.94°, vaziyet 21.29°.
5. **Peyzaj bandı:** Zemin katlarda bina çevresinde 2.5 m çim bandı, giriş yolu ve suluboya ağaçlar var. Bodrumlarda 1.1 m orta gri toprak bandı, üst katlar beyaz zeminde.
6. **Mahal poligonu olmayan alanlar** (asansör kuyuları, A 1. bodrum güneydoğu köşesi, A 1. kat asansör önü) asansör grisi ya da boş bırakıldı. Bunlar alan toplamına girmez.
7. **Vaziyet zemin sınıfları:** DXF'te yaya yolu ve sert zemin için kapalı poligon yok. Bölgeler çizgilerden ve etiketlerden çıkarıldı. Etiketi olmayan parsel içi alanlar çim, ince şeritler şev taşı kabul edildi. Bu yüzden blok önlerindeki yaya yollarının bir kısmı çim tonunda kalmış olabilir.
8. **A zemin kat "TERAS 190.00 m²"** havuz salonunun üstündeki teras olarak taş tonunda boyandı. Net toplama girmedi.
9. **Alan karşılaştırması:** DXF mahal yazılarındaki alanlar (örn. 20.07) poligonlardan hesaplanan değerlerle uyumlu. Paftalarda 0.10 m²'ye yuvarlanmış değerler var (20.10).
10. Tefriş DXF'teki gibi bırakıldı. Gözle yapılan kontrolde mahal işlevlerinde belirgin eksik görülmedi, ama ayrıntılı tefriş-kuralları denetimi yapılmadı.

## Açık sorular (önerilen varsayımla)
1. D Blok 1. kat ve çatı paftası başlıklarında ikisi de "+3.50 (170.75)" yazıyor; çatı kotunun +7.00 (174.25) olması bekleniyor. Öneri: 1. kat +3.50 doğru, çatı kotu DXF'te düzeltilsin.
2. A zemin kat şemasında "KAT BRÜTÜ 363.96", plan brüt poligonunda "170.00" yazıyor. Öneri: paftada plan poligonu (170.00) kullanıldı; şema terası da kapsıyor olabilir.
3. A 1. kat, C 1. bodrum ve C zemin planlarında brüt poligon yok. Öneri: şema "KAT BRÜTÜ" değerleri kullanıldı (170.00 / 135.00 / 135.00).
4. D 1. kat brüt poligonu 217.71 m² (zemin katla aynı), D çatı katı şeması ise 129.77 m² veriyor. Kat 82.70 m² teras içeriyor. Öneri: 217.71 gösterildi; doğru değer ÇİZGİ/kullanıcı tarafından teyit edilsin.
5. Vaziyette yaya yolu ve sert zemin sınırları DXF'te kapalı poligon olarak yok. Öneri: şimdilik çim ağırlıklı bırakıldı. İstenirse sert zemin poligonları DXF'e eklenince yeniden boyanır.
