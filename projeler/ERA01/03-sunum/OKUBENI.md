# ERA01 ERA Evi: Sunum klasörü (SUNUM)

**Güncel set:** `ERA01_sunum_konsept-sunum_v01.pptx` (düzenlenebilir ana dosya) ve `ERA01_sunum_konsept-sunum_v01.pdf`.
**Format:** A3 yatay (420 × 297 mm), 27 sayfa, font Calibri. PPTX'te font adı Calibri yazılı. PDF bu sistemde Carlito ile üretildi (Calibri'nin metrik eşdeğeri).
**Amaç / aşama:** Mimari konsept proje sunumu. Konsept görseller geçici; kullanıcı yenileriyle değiştirecek.
**Şablon:** `ofis-standartlari/konsept-sunum-sablonu.md` (sayfa düzeni, üst/alt şerit, görsel bandı), ŞEF'in önerdiği akışa göre uyarlandı.

## Sayfa listesi
| No | Sayfa | İçerik | Kaynak dosya (sürüm) |
|---|---|---|---|
| 1 | KAPAK | Konsept görsel (sol 2/3, sağ kenarı beyaza eriyor), [İŞVEREN ADI], ERA EVİ, MİMARİ KONSEPT PROJE / KONUT PROJESİ / (11.11.2026) | G01 ← konsept-01 (webp) |
| 2 | İÇİNDEKİLER | Dikey başlık ve bölüm listesi | - |
| 3 | PROJE BİLGİLERİ | Proje alanı görseli (yer tutucu), proje bilgileri, konsept metni [DOLDURULACAK] | G00 yer tutucu |
| 4 | VAZİYET PLANI | Boyalı vaziyet paftası | `03-boyama/ERA01_boyama_vaziyet_v02.jpg` |
| 5 | SİTE GÖRSELİ | Kuş bakışı görsel bandı | G02 ← konsept-02 |
| 6 | A BLOK: GÖRSEL | Görsel bandı + 1BK+Z+1N, toplam kapalı alan 677.04 m² | G03 ← konsept-05 |
| 7 | A BLOK: KAT PLANLARI (TOPLU) | Pafta | `ERA01_boyama_A-blok-kat-planlari_v03.jpg` |
| 8 | A BLOK: 1. BODRUM | Pafta | `ERA01_boyama_A-blok-1-bodrum_v02.jpg` |
| 9 | A BLOK: ZEMİN KAT | Pafta | `ERA01_boyama_A-blok-zemin-kat_v02.jpg` |
| 10 | A BLOK: 1. KAT | Pafta | `ERA01_boyama_A-blok-1-kat_v03.jpg` |
| 11 | B BLOK: GÖRSEL | Görsel bandı + 2BK+Z, toplam kapalı alan 954.12 m² | G04 ← konsept-04 |
| 12 | B BLOK: KAT PLANLARI (TOPLU) | Pafta | `ERA01_boyama_B-blok-kat-planlari_v02.jpg` |
| 13 | B BLOK: 2. BODRUM (OTOPARK) | Pafta | `ERA01_boyama_B-blok-2-bodrum_v02.jpg` |
| 14 | B BLOK: 1. BODRUM | Pafta | `ERA01_boyama_B-blok-1-bodrum_v02.jpg` |
| 15 | B BLOK: ZEMİN KAT | Pafta | `ERA01_boyama_B-blok-zemin-kat_v02.jpg` |
| 16 | C BLOK: GÖRSEL | Görsel bandı (yer tutucu) + 1BK+Z, toplam kapalı alan 270.00 m² | G05 yer tutucu |
| 17 | C BLOK: KAT PLANLARI (TOPLU) | Pafta | `ERA01_boyama_C-blok-kat-planlari_v02.jpg` |
| 18 | C BLOK: 1. BODRUM | Pafta | `ERA01_boyama_C-blok-1-bodrum_v02.jpg` |
| 19 | C BLOK: ZEMİN KAT | Pafta | `ERA01_boyama_C-blok-zemin-kat_v02.jpg` |
| 20 | D BLOK: GÖRSEL | Görsel bandı + 1BK+Z+1N, toplam kapalı alan 460.02 m² | G06 ← konsept-01 (webp) |
| 21 | D BLOK: KAT PLANLARI (TOPLU) | Pafta | `ERA01_boyama_D-blok-kat-planlari_v03.jpg` |
| 22 | D BLOK: 1. BODRUM | Pafta | `ERA01_boyama_D-blok-1-bodrum_v02.jpg` |
| 23 | D BLOK: ZEMİN KAT | Pafta | `ERA01_boyama_D-blok-zemin-kat_v02.jpg` |
| 24 | D BLOK: 1. KAT | Pafta | `ERA01_boyama_D-blok-1-kat_v02.jpg` |
| 25 | ALAN TABLOSU | Blok/kat net, açık, brüt alanlar; blok toplamları; genel toplam 2361.18 m²; zemin altı 1320.22 / zemin üstü 1040.96 m² | `03-boyama/kaynak/era01_ozet.json` |
| 26 | ATMOSFER ESKİZİ | Tam sayfa yer tutucu | G07 yer tutucu |
| 27 | ARKA KAPAK | Taş duvar eskizi, IFC logosu, iletişim | `ofis-standartlari/sablon-gorseller/`, `logolar/` |

Pafta sayfaları (4, 7–10, 12–15, 17–19, 21–24) PAFTA'nın A3 paftalarıdır. Başlık, logo ve antet paftanın içinde olduğu için sayfaya tam oturan tek resim olarak konuldu (PPTX boyutu makul kalsın diye 600 dpi'dan 300 dpi'a küçültüldü). Bu sayfalardaki yazılar PPTX'te düzenlenemez; değişiklik gerekiyorsa pafta PAFTA'da güncellenip yeniden yerleştirilir.

## Görsel çerçeveleri ve nasıl değiştirilir
| Çerçeve (PPTX nesne adı) | Sayfa | Konum / boyut | Oran | Şimdiki görsel |
|---|---|---|---|---|
| `GORSEL_G01_kapak` | 1 | x 0, y 30 mm · 290 × 200 mm | 1.45 : 1 | konsept-01, sola yakın kırpım |
| `GORSEL_G00_proje-alani` | 3 | x 0, y 36 mm · 290 × 225 mm | 1.29 : 1 | yer tutucu (uydu görüntüsü / konum haritası) |
| `GORSEL_G02_site-kus-bakisi` | 5 | x 0, y 51.8 mm · 420 × 193.5 mm | 2.17 : 1 | konsept-02 |
| `GORSEL_G03_A-blok` | 6 | aynı bant | 2.17 : 1 | konsept-05 |
| `GORSEL_G04_B-blok` | 11 | aynı bant | 2.17 : 1 | konsept-04 (üst-alt kırpıldı) |
| `GORSEL_G05_C-blok` | 16 | aynı bant | 2.17 : 1 | yer tutucu |
| `GORSEL_G06_D-blok` | 20 | aynı bant | 2.17 : 1 | konsept-01 (yanlardan az kırpıldı) |
| `GORSEL_G07_atmosfer-eskizi` | 26 | tam sayfa · 420 × 297 mm | 1.414 : 1 | yer tutucu |

- Her çerçeve tek, gruplanmamış resim nesnesidir. PowerPoint kırpması ve maske yok: görseller önceden çerçeve oranına kırpıldı (`gorseller/` klasöründe).
- **Değiştirme:** Resme sağ tıklayın → **Resmi Değiştir** → Dosyadan. Seçim Bölmesi'nde (Giriş → Düzenle → Seç → Seçim Bölmesi) nesneler yukarıdaki adlarla görünür.
- Yeni görsel çerçeveyle aynı orandaysa (bantlar için 2.17 : 1, örn. 3200 × 1474 px) olduğu gibi oturur. Farklı orandaysa PowerPoint görseli çerçeveye sığdırırken boyutu değiştirebilir. Bu durumda **Resim Biçimi → Kırp → Doldur** ile çerçeveyi koruyun, ya da görseli önceden bu orana kırpın.
- Kapaktaki beyaza eriyen geçiş, görselin üstünde ayrı bir gradyan şekildir (`KAPAK_beyaz-gecis`). Resim değişince yerinde kalır, gerekirse silinebilir.
- Blok görsel sayfalarındaki blok adı ve toplam kapalı alan yazıları (`A_blok-ozet` vb.) düzenlenebilir metindir.

## Klasör
| Yol | İçerik |
|---|---|
| `ERA01_sunum_konsept-sunum_v01.pptx` / `.pdf` | Sunum seti |
| `gorseller/` | Çerçeve oranına kırpılmış görseller ve yer tutucular (G00–G07) |
| `onizleme/ERA01_sunum_konsept-sunum_v01_s-NN.png` | Sayfa önizlemeleri (60 dpi) |
| `kaynak/era01_sunum.py` | Üretici script (python-pptx, Pillow) |
| `kaynak/era01_sunum_sayfalar_v01.json` | Sayfa / çerçeve listesi (script çıktısı) |

Yeniden üretim: `cd kaynak && python3 era01_sunum.py`, ardından `soffice --headless --convert-to pdf ../ERA01_sunum_konsept-sunum_v01.pptx --outdir ..`.
Küçültülmüş paftalar `ERA01_ARA` ortam değişkeninin gösterdiği klasöre yazılır (varsayılan `kaynak/_ara/`, yeniden üretilebilir, repoda tutulmaz).

## Varsayımlar
1. Üst şeritte paftalarla aynı düzen kullanıldı: `ERA01` (kalın) ve `E R A  E V İ`. Şablondaki "işveren/marka adı" yerine proje adı var, çünkü işveren bilinmiyor ve 16 pafta sayfasıyla tutarlı olması gerekiyor.
2. İşveren adı, mahalle, arsa alanı, bağımsız bölüm sayısı ve konsept metni bilinmiyor. Hepsi `[DOLDURULACAK]` / `[İŞVEREN ADI]` olarak bırakıldı, metin uydurulmadı.
3. Lokasyon "Beykoz / İstanbul" (proje.md: Beykoz antetli). Ada 1366, parsel 45 ve sokak adları (Güller Sokak, Odak Çıkmazı Sokak) vaziyet paftasından alındı.
4. Kapak: şablonda karakalem eskiz var. ŞEF'in isteğine göre konsept görsel (konsept-01) kondu. Eskiz gelirse aynı çerçeveye konabilir.
5. Görsel eşleşmesi: A ← konsept-05, B ← konsept-04 ("tek katlı blok"; B ve C zemin üstünde tek katlı, B'ye verildi), D ← konsept-01. C için uygun görsel yok, yer tutucu kondu. Konsept-01 hem kapakta hem D sayfasında var (farklı kırpımla). Konsept-03 (konsept-01'in düşük çözünürlüklü kırpımı) kullanılmadı.
6. Proje alanı sayfasında uydu görüntüsü ve anahtar harita yok, yer tutucu kondu. Atmosfer eskizi sayfası şablona uygun olarak yer tutucuyla eklendi.
7. Vaziyet planı yalnız boyalı paftayla verildi (şablonun 4–6. sayfaları). Ölçülü vaziyet, imar/emsal tabloları ve otopark planı için ÇİZGİ çıktısı yok. İmar hesapları `[DOLDURULACAK]`.
8. Her blokta önce toplu kat planı paftası (toplam kapalı alan bu paftada), sonra tekil kat paftaları geliyor. Blok görsel sayfasında da toplam kapalı alan yazılı.
9. Alanlar `era01_ozet.json`'dan alındı: brüt = terassız kapalı alan. B bloğunun DXF'te geçen "çatı katı +3.50" katının boyaması yok, tabloda yer almıyor.
10. Model görselleri (02-model v03) konmadı. HACİM v04 gelince istenirse eklenir.
11. Tarih 11.11.2026 (pafta tarihleriyle aynı). Proje türü "KONUT PROJESİ".
