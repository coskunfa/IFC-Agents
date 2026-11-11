# DNM01 Deneme Villa: Boyama klasörü (PAFTA)

**Stil:** KONSEPT GRİ (sunum-standardi §2-A) · **Ölçek:** 1/100 · **Çözünürlük:** 600 dpi → **2.3622 px/cm** (gerçek ölçü) · **Font:** Carlito (Calibri metrik eşdeğeri; sistemde Calibri yok)

## Dosyalar
| Dosya | Sürüm | Kağıt | Piksel | Açıklama |
|---|---|---|---|---|
| `DNM01_boyama_giris-kat_v01.jpg` | v01 | A4 yatay, 1/100 | 7016×4961 | Giriş kat + 2.5 m peyzaj bandı |
| `DNM01_boyama_1-kat_v01.jpg` | v01 | A4 yatay, 1/100 | 7016×4961 | 1. kat |
| `DNM01_boyama_kat-planlari_v01.jpg` | v01 | A3 yatay, 1/100 | 9921×7016 | İki kat bir arada |
| `onizleme/*_onizleme.png` | v01 | - | 2000 px | Kontrol önizlemesi |
| `kaynak/dnm01_boyama.py` | v01 | - | - | Üretim betiği (`python3 kaynak/dnm01_boyama.py`; ezdxf, pycairo, Pillow, shapely, numpy) |

JPEG: sRGB, kalite 92, 4:4:4, 600 dpi etiketli. PSD istenmedi.

## Girdi
`00-girdi/DNM01_girdi_kullanici-revizyon_v01r.dxf` (kullanıcı onaylı). Duvar, kolon, mahal poligonu (`0_IFC_Area`), kapı, merdiven ve pencere geometrisi DXF'ten birebir alındı. Mobilya, DXF blok konum ve ölçülerinde PAFTA tarafından vektörle yeniden çizildi. Bodrum boyanmadı.

## Alanlar (0_IFC_Area, 0.10 m²'ye yuvarlanmış)
**Giriş kat:** Salon 64.00 · Mutfak 33.20 · Giriş holü 16.10 · Merdiven 7.20 · WC 3.10 · Asansör 1.80 → **Net toplam 125.40 m²** (yuvarlanmış değerlerin toplamı; ham toplam 125.27) · **Brüt 137.36 m²**

**1. kat:** Ebeveyn yatak odası 22.40 · Yatak odası 1 17.10 · Yatak odası 3 15.20 · Yatak odası 2 15.00 · Giyinme odası 13.00 · Hol 11.90 · Ebeveyn banyosu 7.90 · WC 1.50 · Banyo 1 3.10 · Banyo 2 3.10 · Banyo 3 3.10 · Merdiven 6.80 · Asansör 1.80 → **Net toplam 121.90 m²** (ham 121.88) · **Brüt 137.36 m²**

## Palet
Kuru mahal #DADAD8 · hol/koridor #E3E3E1 · mutfak #CFCFCC · ıslak hacim (soğuk gri) #C8CDD1 · merdiven #E7E7E5 · asansör kuyusu #BDBDBC · duvar #383838 · kolon #050505 · çim #DCE5DA · giriş üçgeni #C8102E. Mahal dolgularında %2-3 gradyan, duvar ve mobilya altında yumuşak gölge.

## Varsayımlar ve notlar
1. Mutfak tezgâhı: DXF'te `*E102` bloğu dış duvarın dışında (x −350..20). Boyamada tezgâh mutfak içinde gösterildi: batı duvarı boyunca 20..80 × 80..470 (eviye + ocak), kuzey dönüşü 20..297 × 470..530 (kullanıcının çizgileri), güneyde pencere altı tezgâh 20..560 × 20..80 (DXF'te duruyor, korundu). DXF düzeltmesi ÇİZGİ'nin işi.
2. Buzdolabı DXF'te yoktu (tefriş kuralı). Kuzey tezgâhın doğu ucuna 75×65 buzdolabı eklendi.
3. Peyzaj bandı yalnız giriş katında (referans s07/s08'de üst kat planında bahçe yok). 1. kat beyaz zeminde.
4. Dekoratif öğeler eklendi (mobilya değil): salonda 2, giriş holünde 1, 1. kat holünde 1 saksı bitkisi; salon ve yatak odalarında halı.
5. "Yatak odası 2/3" ve "Ebeveyn banyosu" adları sığsın diye iki satıra bölündü (numaralandırma gerekmedi).
