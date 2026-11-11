# Kontrol Raporu v03 (11.11.2026)
Proje: ERA01 ERA Evi · Tur 3 (kısa) · Denetleyen: DENETÇİ
Sonuç: **GEÇTİ: TESLİME HAZIR** (0 HATA, 0 açık UYARI)

Denetlenen:
- PAFTA v03: `ERA01_boyama_A-blok-1-kat_v03.jpg`, `ERA01_boyama_A-blok-kat-planlari_v03.jpg`, `ERA01_boyama_D-blok-kat-planlari_v03.jpg`, `onizleme/*_v03_onizleme.png`, `kaynak/era01_ozet.json`, `OKUBENI.md`
- HACİM v03: `ERA01_model_site_v03.skp`, `*_v03.png`, `OKUBENI.md`, `kaynak/era01_model_rapor_v03.json`, `kaynak/era01_model_gen.py`

## Tur 2 maddelerinin durumu
| Madde | Sorumlu | Durum | Kanıt |
|---|---|---|---|
| H8 A 1. kat brüt | PAFTA | **KAPANDI** | Tekil ve toplu paftada "BRÜT ALAN : 145.04 m²". Açık alan 25.00 m² ayrı satırda. Toplu paftada "TOPLAM KAPALI ALAN : 677.04 m²" (362.00 + 170.00 + 145.04). `era01_ozet.json` (brut 145.04, toplam_kapali_alan A 677.04) ve OKUBENI aynı. HACİM modelindeki 145.0 ile tutarlı |
| U-v2-1 Yarma tabanı | HACİM | **KAPANDI** | `ARAZI_YARMA_TABAN_167.15` (166.00–167.15 kütlesi), garaj tabanıyla aynı kot. Aksonometrik v03'te yarma garaj kapısına düz iniyor, ters eğim yok |
| U-v2-2 OKUBENI çelişkileri | HACİM | **KAPANDI** | "Modellenmeyenler" listesi güncellendi (korkuluk ve yarma çıkarıldı). D 1. kat kapalı kısmı her yerde 10.55 m |
| U-v2-3 Yazı çakışmaları | PAFTA | **KAPANDI** | D zemin toplu pafta: "GİRİŞ HOLÜ 8.50 / 8.70" yazıları kot sembolünden ve kapı yayından ayrık. A zemin toplu pafta: merdiven numarası "2" giriş üçgeninin solunda, çakışma yok |
| U-v2-4 375'lik doğrama h=280 | HACİM | Kabul (açık konu) | Teslim özetinde kullanıcıya varsayım olarak bildirilecek |

## PAFTA'nın sorusu: D zemin ±0.00 kot çizgileri
D zemin toplu paftada (1/150) iki ±0.00 kot sembolünün yatay çizgisi giriş holü duvarını geçip komşu mahale biraz uzanıyor. Yazılarla ya da başka sembollerle çakışma yok, okunurluk bozulmuyor ve DXF'teki sembol uzunluğu korunmuş. **Kabul edilebilir** (NOT). Bir sonraki revizyonda isteğe bağlı olarak kısaltılabilir.

## NOT
- Teslim seti:
  - Model: `02-model/ERA01_model_site_v03.skp` ve v03 görselleri. Kat üstten görünüşleri v02 PNG'leri; v03'te değişiklik yalnız arazide olduğu için geçerli.
  - Boyamalar: üç v03 pafta (A 1. kat, A toplu, D toplu) ve kalan 13 v02 pafta (vaziyet, A 1. bodrum, A zemin, B 2. bodrum, B 1. bodrum, B zemin, B toplu, C 1. bodrum, C zemin, C toplu, D 1. bodrum, D zemin, D 1. kat).
  - Önceki sürümler arşivde duruyor.
- Teslim özetinde kullanıcıya iletilecek açık konular:
  1. Font Carlito (Calibri'nin metrik eşdeğeri).
  2. A avlusunun batısındaki etiketsiz 375'lik doğrama h=280 kabul edildi.
  3. B otopark rampası düz yarma; Y rampa eğimi modellenmedi.
  4. B bodrumları 1/150.
  5. DXF'teki tutarsızlıklar (tur 1 raporu NOT bölümü).

## Kontrol edilenler
- H8 ve U-v2-1 … U-v2-4: ✓
- v03 paftaları: A3, 600 dpi, başlık "MİMARİ KONSEPT PROJE", alan değerleri özet JSON ile aynı ✓
- HACİM ↔ PAFTA brüt alanları (A 1. kat 145.04 / 145.0): ✓
- Tur 1 ve tur 2'de kapanan maddelerde geri dönüş (v03'te değişmeyen dosyalar aynı kaldı): ✓
