# DNM01 Deneme Villa: Model klasörü (HACİM)

**Seviye:** KÜTLE + CEPHE · **Birim:** cm (kotlar m) · **Orijin:** dış duvar sol alt (GB) köşesi = 0,0 (çizimle aynı), ±0.00 = giriş kat bitmiş döşeme · **+Y = kuzey**

## Dosyalar
| Dosya | Sürüm | Açıklama |
|---|---|---|
| `DNM01_model_kutle_v01.skp` | v01 | SketchUp modeli. **Bu klasöre indirilemedi** (oturum ağı `api.sketchup.com` adresini engelliyor, 403). Bulutta kayıtlı; indirme bağlantısı ŞEF raporunda |
| `DNM01_model_sketchup-onizleme_v01.png` | v01 | SketchUp'ın kendi küçük resmi (model kamerası = Perspektif GD) |
| `DNM01_model_perspektif_v01.png` | v01 | Kontrol görseli, sahne "Perspektif GD" |
| `DNM01_model_aksonometrik_v01.png` | v01 | Kontrol görseli, sahne "Aksonometrik KB" (giriş cephesi) |
| `DNM01_model_kus-bakisi_v01.png` | v01 | Kontrol görseli, sahne "Kus bakisi" |
| `DNM01_model_kat-b1_v01.png`, `..._kat-00_v01.png`, `..._kat-01_v01.png` | v01 | Kontrol görselleri, kat üstten sahneleri (üst katlar, çatı ve tavan gizli) |
| `kaynak/dnm01_model_gen.py` | v01 | DXF'ten model verisi üreten parametrik betik (pencere kuralları, kalınlıklar, çatı parametreleri dosya başında) |
| `kaynak/dnm01_model_render.py`, `dnm01_model_pack.py`, `dnm01_model_kameralar.json` | v01 | Kontrol görseli üretimi, veri paketleme, sahne kameraları |

Kontrol PNG'leri SketchUp'tan değil, modelle **aynı geometri verisinden** ve aynı sahne kameralarından üretildi (bulut aracı sahne başına görüntü dışa aktaramıyor). SketchUp'taki görünüm `..._sketchup-onizleme_v01.png` ile doğrulandı.

## Kaynak çizim
- `00-girdi/DNM01_girdi_kullanici-revizyon_v01r.dxf` (kullanıcı onaylı revizyon; ŞEF iş emri, 2026-11-11). `01-cizim/onayli/` bu tarihte boştu.
- Mahal adları DXF içindeki `0_IFC_ROOM_TEXT_50` bloklarından, mahal sınırları `0_IFC_Area` poligonlarından alındı.

## Kotlar ve ölçüler
| Konu | Değer |
|---|---|
| Kat yüksekliği | 3.50 m (villa). Bodrum −3.50, giriş ±0.00, 1. kat +3.50 |
| Döşeme paketi | 50 cm: kaplama 10 (üstte, üst kotu = kat kotu) + taşıyıcı 30 + tavan 10 (altta). Net iç yükseklik 3.00 m |
| Duvarlar | Dış 20, iç 10 cm. Döşeme üstünden (kat kotu −0.10) üst döşeme altına (kat kotu +3.10) |
| Kolonlar | 20×40, kat başına 8, duvar yüksekliğinde (320 cm) |
| Cephe kaplaması | 20 cm, dış duvar çizgisinin dışında; giriş kat 0.00–3.50, 1. kat 3.50–6.875 (çatı alt yüzüne kadar). Bodrumda yok |
| Çatı döşemesi | 1. kat tavanı üstünde taşıyıcı döşeme +6.60/+6.90 (kaplama yok, çatı arası boş) |
| Çatı | 4 kırma, eğim %15, paket 20 cm (düşey), saçak cephe kaplaması dış yüzünden 50 cm (dış duvar çizgisinden 70 cm). Saçak ucu üst kotu **+7.00**, saçak izdüşümü 15.00 × 11.50 m |
| **Mahya kotu** | **+7.8625 m** (üst yüz; yükselme 11.50/2 × 0.15 = 86.25 cm), mahya boyu 3.50 m (x 505–855, y 505) |
| Merdiven | L merdiven, 24 rıht × 14.58 cm, basamak 27 cm, kol 110 cm; 9 düz + 3 dönen + 11 düz basamak; 20 cm döşemeli testere kesitli basit kütle (bodrum→giriş, giriş→1. kat) |
| Arazi | ±0.00'da tek yüzey, bina izdüşümü + 5 m (−5.20…18.80 × −5.20…15.30 m), bina dış duvar izi boş |

### Doğramalar (pencere yükseklikleri ŞEF varsayılanı, kullanıcıya soruluyor)
| Tip | Kat / mahal | Cephe | Genişlik | Parapet / yükseklik | Bileşen | Bölme |
|---|---|---|---|---|---|---|
| P1 | Giriş / Mutfak | G | 240 | 0 / 300 (DXF: 120) | DGR_240x300 | 2 × 112.5 net, kayıt 150 |
| P2 | Giriş / Salon | G | 500 | 0 / 300 (DXF: 250) | DGR_500x300 | 3 × 160, kayıt 150 |
| P3 | Giriş / Salon | D | 350 | 0 / 300 (DXF: 250) | DGR_350x300 | 2 × 167.5, kayıt 150 |
| P4 | Giriş / Salon | D | 300 | 0 / 300 (DXF: 250) | DGR_300x300 | 2 × 142.5, kayıt 150 |
| P5 | 1. kat / Yatak odası 1 | G | 150 | 90 / 210 (DXF: 150) | DGR_150x210 | tek bölme |
| P6, P7 | 1. kat / Yatak odası 2, 3 | G | 180 | 90 / 210 (DXF: 150) | DGR_180x210 | tek bölme |
| P8 | 1. kat / Ebeveyn yatak odası | G | 240 | 0 / 300 (DXF: 220) | DGR_240x300 | 2 bölme, kayıt 150 |
| P9 | 1. kat / Hol | K | 100 | 150 / 150 | DGR_100x150 | tek bölme |
| P10 | 1. kat / Ebeveyn banyosu | K | 100 | 150 / 150 (DXF: 60) | DGR_100x150 | tek bölme |
| P11 | 1. kat / Giyinme odası | K | 120 | 150 / 150 (DXF: 120) | DGR_120x150 | tek bölme |
| Ana giriş | Giriş / Giriş holü | K | 100 | 0 / 250 | DGR_KAPI_100x250 | kasa + kanat |

Kasa 5 cm genişlik, 6 cm derinlik, dış duvarın ortasında. Cam tek yüzey (`M_DOGRAMA_CAM`, %60 saydam). Kayıt yalnızca yüksekliği 240 cm'yi aşan doğramalarda, yüksekliğin ortasında. Bölme sayısı: genişlik/150 yuvarlanır, bölme ≥ 100 cm.
İç kapılar: boşluk 220 cm, üstünde lento (220 → döşeme altı). Kapı bloğu olan boşluklara düz kanat kutusu (`KAPI_90x220`, `KAPI_80x220`, 4 cm). Mutfak–salon (200) ve hol–salon (120) geçişleri kapısız. Boşluk altındaki eşik, döşeme kaplamasına (kuru mahal tarafına) katıldı.

## Grup ve tag yapısı
```
KAT_B1 / KAT_00 / KAT_01   (tag = grup adı)
  TASIYICI        KOLON_20x40 örnekleri
  DIS_DUVAR       DD_<kat>_<cephe>_nn  (kolonlar arası duvar parçaları, boşluklar iç döngü/çentik)
  IC_DUVAR        ID_<kat>_nn, LENTO_<kat>_nn
  CEPHE_KAPLAMA   CK_<kat>_S/N/E/W  (yalnız KAT_00, KAT_01)
  DOSEME          DOSEME_<kat>  (merdiven ve asansör boşlukları açık)
  DOSEME_KAPLAMA
    DOSEME_KAPLAMA_KURU    DK_<MAHAL>
    DOSEME_KAPLAMA_ISLAK   DK_<MAHAL>
  TAVAN           TV_<MAHAL>
  DOGRAMA         pencere / kapı bileşen örnekleri
  MERDIVEN        MRD_<kat>_KOL1, _DONUS_10/11/12, _KOL2  (KAT_B1, KAT_00)
KAT_CATI  (tag KAT_CATI)
  DOSEME          DOSEME_CATI
  CATI            CATI_KIRMA
ARAZI     (tag ARAZI)
```
Tag'ler: KAT_B1, KAT_00, KAT_01, KAT_CATI, TASIYICI, DIS_DUVAR, IC_DUVAR, CEPHE_KAPLAMA, DOSEME, DOSEME_KAPLAMA, DOSEME_KAPLAMA_KURU, DOSEME_KAPLAMA_ISLAK, TAVAN, DOGRAMA, MERDIVEN, CATI, ARAZI.

Döşeme kaplaması alt grupları:
| Kat | KURU | ISLAK |
|---|---|---|
| KAT_B1 | DK_BODRUM_BOS_MAHAL, DK_MERDIVEN | - |
| KAT_00 | DK_GIRIS_HOLU, DK_SALON | DK_WC, DK_MUTFAK |
| KAT_01 | DK_HOL, DK_YATAK_ODASI_1, _2, _3, DK_EBEVEYN_YATAK_ODASI, DK_GIYINME_ODASI | DK_BANYO_1, _2, _3, DK_EBEVEYN_BANYOSU, DK_EBEVEYN_WC |

Asansör kuyusunda kaplama ve tavan yok. Giriş ve 1. kat merdiven boşluğunda kaplama yok (1. kat merdiven boşluğunda tavan var).

## Bileşenler
| Bileşen | Adet |
|---|---|
| KOLON_20x40 | 24 |
| KAPI_80x220 | 9 |
| KAPI_90x220 | 6 |
| DGR_KAPI_100x250 | 1 |
| DGR_500x300 | 1 |
| DGR_350x300 | 1 |
| DGR_300x300 | 1 |
| DGR_240x300 | 2 |
| DGR_180x210 | 2 |
| DGR_150x210 | 1 |
| DGR_120x150 | 1 |
| DGR_100x150 | 2 |

## Malzemeler
M_TASIYICI #6E6E6E, M_DIS_DUVAR #A6A6A6, M_IC_DUVAR #D0D0D0, M_CEPHE_KAPLAMA #E6E6E6, M_DOSEME #8C8C8C, M_DOSEME_KAPLAMA_KURU #F2F2F2, M_DOSEME_KAPLAMA_ISLAK #DADDE0, M_TAVAN #FAFAFA, M_DOGRAMA_KASA #4A4A4A, M_DOGRAMA_CAM açık gri %60 saydam, M_MERDIVEN #BDBDBD, M_CATI #959595 (metal kenet yerine düz gri, doku yok), M_ARAZI #C8C8C8. Kullanılmayan malzeme ve tag temizlendi.

## Sahneler
Perspektif GD, Aksonometrik KB (paralel izdüşüm), Kus bakisi, KAT_B1 ustten, KAT_00 ustten, KAT_01 ustten (paralel, üstteki katlar + KAT_CATI + TAVAN gizli). Model kamerası = Perspektif GD. Stil: ARCHITECTURAL_EXTERIOR.

## Model istatistiği
| | Değer |
|---|---|
| Grup (yaprak katı) | 112 + 51 bileşen örneği, 12 bileşen tanımı |
| Benzersiz geometri | 1 091 yüzey (gruplar) + 192 yüzey (bileşen tanımları) |
| Görüntülenen toplam (örnekler açılmış) | 1 547 yüzey, 3 688 kenar |
| Katı (solid) kontrolü | Tüm gruplar katı; yalnız cam yüzeyleri ve arazi tek yüzey (beklenen) |
| Dosya boyutu | Bilinmiyor (dosya indirilemedi) |

## Çizimle çelişkiler ve varsayımlar
1. Pencere yükseklikleri DXF `YUKSEKLIK` değerlerinden değil, ŞEF'in mahal kuralından alındı (tablo yukarıda). P1 mutfak penceresi 0/300 oldu; DXF'te eviye önü ve tezgah üstünde 120 cm yüksekliğinde. Tezgahla çakışıyor.
2. Çatı döşemesinde 10 cm kaplama yok (çatı arası kullanılmıyor): çatı döşemesi +6.60/+6.90, saçak ucu +7.00. Çatı alt yüzü dış duvar çizgisinde +6.905, döşemeye 0.5 cm boşlukla oturuyor. Cephe kaplaması +6.875'te bitiyor; çatı altında 0–3 cm'lik kama boşluğu kalıyor (görünmez).
3. Çatı paketi 20 cm düşey alındı (eğime dik ~19.8 cm).
4. Merdivenler DXF'teki gibi bodrumdan 1. kata aynı izde üst üste. Giriş kat merdiveninin ilk basamağı, bodrum merdiveni boşluğunun üstünde (döşeme yok) başlıyor. Gerçekte bir sahanlık ya da kirişle taşınması gerekir (çizimdeki durum, modelde düzeltilmedi). Korkuluk modellenmedi.
5. Kolonlar yalnız duvar yüksekliğinde (döşeme içinden geçmiyor). Kiriş yok.
6. Giriş ve 1. kat iç duvar aksları üst üste gelmiyor (ÇİZGİ'nin notu geçerli). Modelde duvarlar döşemeye oturuyor, taşıyıcı çözüm yok.
7. Asansör kabini, mobilya, vestiyer modellenmedi. Asansör kuyusu dibi (pit) yok, bodrum döşemesi kuyuda devam ediyor.
8. Ana giriş eşiği ±0.00, arazi de ±0.00 (kot farkı yok).
9. Bodrum tamamen toprak altı kabul edildi; arazi yüzeyi bodrum duvarlarının üstünde.
