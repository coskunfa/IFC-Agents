# Kontrol Raporu v02 (11.11.2026)
Proje: ERA01 ERA Evi · Tur 2 · Denetleyen: DENETÇİ
Sonuç: **DÜZELTME GEREKLİ** (1 HATA, 4 UYARI)

Denetlenen:
- HACİM v02: `02-model/ERA01_model_site_v02.skp`, `*_v02.png`, `OKUBENI.md`, `kaynak/era01_model_rapor_v02.json`, `kaynak/era01_model_gen.py`
- PAFTA v02: `03-boyama/*_v02.jpg` (16 adet, hepsi A3 9921×7016 px, 600 dpi), `onizleme/*_v02_onizleme.png`, `OKUBENI.md`, `kaynak/era01_ozet.json`

Ölçüt: tur 1 raporu (`ERA01_kontrol_raporu_v01.md`) ve proje.md'de kesinleşen varsayımlar (DENETÇİ soruları 1–6, önerilen varsayımlarla).

---

## Önceki maddelerin durumu

| Madde | Sorumlu | Durum | Kanıt |
|---|---|---|---|
| H1 D 1. kat brüt | PAFTA | **KAPANDI** | Tekil ve toplu pafta: "BRÜT ALAN : 129.77 m²", teras 82.70 ayrı satırda. Özet JSON'da kaynak D_CK_SEMA. D toplam kapalı alan 460.02 |
| H2 Vaziyette D çatısı | PAFTA | **KAPANDI** | Kırma çatı bloğun güney ucuna yaslı (+170.75 tarafı). Kuzeydeki 7.15 m teras olarak görünüyor. HACİM modeliyle aynı |
| H3 Çatı üst yüzü ve eğim | HACİM | **KAPANDI** | Üst yüz saçakta saçak kotunda. Eğimler A %15.1, B %21.0, C %18.4, D %17.0 (DXF kotlarıyla aynı). Döşeme üstü saçak −0.13 (D −0.20). Duvar hizasında çatı alt yüzü döşemenin üstünde kalıyor (A: saçak −0.035 > −0.13), çakışma yok |
| H4 B 2. bodrum tavanı | HACİM | **KAPANDI** | Tavan 169.55, net 2.40. Kaplamayla çakışma yok. A B1 173.05 "DXF'te yazılı" olarak düzeltildi |
| H5 A kat bahçesi açık avlu | HACİM | **KAPANDI** | Brüt izde delik var (K1 brüt 145.0). Kırma çatıda 4.80 × 4.40 m boşluk (avlu net ~25 m², eksi 2 × 20 cm cephe kaplaması). Avlu duvarları dış duvar + kaplama. `DK_TERAS_A_K1` kuru grupta. Kuş bakışı ve aksonometrik PNG'lerde avlu görünüyor |
| H6 B otopark girişi | HACİM | **KAPANDI** (U-v2-1 notuyla) | Garaj kapısı boşluğu 400×230 (`DGR_GARAJ_400x230`) kuzey cephede plan x 800–1200'de, DXF'teki rampa duvarlarının arasında. PAFTA B 2. bodrumundaki girişle aynı yerde. Yarma 4.60 × 14.85 m ve rampa istinat duvarları var |
| H7 SALON+MUTFAK kuru grupta | HACİM | **KAPANDI** | A B1 ve C ZK `DOSEME_KAPLAMA_KURU` altında. HAVUZ ıslak grupta |
| U1 Teras tefrişi | PAFTA | KAPANDI | A zemin terasında oturma grubu + 6 kişilik masa, D 1. kat terasında yemek ve oturma grubu |
| U2 Yazı çakışmaları | PAFTA | KAPANDI | Yazılar tek tip (ad kalın, alan normal). Yazılar duvarlardan uzakta duruyor, yalnız sığmayan mahaller numaralı. Küçük bir kalıntı var: U-v2-3 |
| U3 Numara ve liste | PAFTA | KAPANDI | Karar 2'ye uygun: yalnız sığmayan mahaller (dar merdiven, koridor, WC) numaralı |
| U4 Başlık | PAFTA | KAPANDI | "M İ M A R İ   K O N S E P T   P R O J E", aşama KONSEPT |
| U5 Kağıt ve ölçek | PAFTA | KAPANDI | 16 paftanın hepsi A3. B'nin iki bodrumu 1/150'de (A3'e 1/100 sığmıyor; ŞEF'in bildirdiği sapma, kabul) |
| U6 Toplam kapalı alan | PAFTA | KAPANDI (değer düzeltmesi H8'de) | Dört toplu paftada sağ altta var |
| U7 Yaya yolları | PAFTA | KAPANDI | Sert zemin tonunda, lejantta var |
| U8 A terası, korkuluk, alçak bahçe | PAFTA | KAPANDI | Korkuluk çizgisi ve "ALÇAK BAHÇE −2.80 (170.15)" var |
| U9 "E. BANYO" yazımı | PAFTA | KAPANDI | Tek yazım |
| U10 Arazi sadeleştirme | HACİM | KAPANDI | 808 → 626 yüzey. Kademe sınırları düzgün (PNG'ler) |
| U11 Kuzey açısı | HACİM | KAPANDI | North Angle 338.71° (gerçek kuzey +Y'nin 21.29° batısında). PAFTA kuzey oklarıyla tutarlı |
| U12 Korkuluk | HACİM | KAPANDI | Dolu parapetler kaldırıldı. 110 cm, 4 cm cam panel (`KORKULUK_*`). PAFTA'daki çift çizgi korkulukla tutarlı |
| U13 D çatı izi | HACİM | KAPANDI | 9.65 × 11.40 m, parapet içinde |

---

## HATA (düzeltilmesi zorunlu)

- **[H8] Sorumlu: PAFTA** | Dosya: `ERA01_boyama_A-blok-1-kat_v02.jpg`, `ERA01_boyama_A-blok-kat-planlari_v02.jpg` (1. kat brüt ve TOPLAM KAPALI ALAN), `kaynak/era01_ozet.json`, `OKUBENI.md` (Alanlar tablosu)
  Sorun: A 1. kat brüt alanı **170.00 m²** yazılmış. Bu değer DXF şeması `A_K1_SEMA`'dan geliyor ve 20.00 × 8.50 m'lik bütün blok konturunu kapsıyor; KAT BAHÇESİ de içinde. DXF şablon hesabı da bunu gösteriyor: 170.00 − 9.75 (merdiven) − 0.16 (şaft) − 24.96 (kat bahçesi) = 135.13. Kesinleşen karar 1'e göre brüt alan "terassız kapalı alan". PAFTA'nın kendi kuralı da kat bahçesini AÇIK ALAN satırına alıyor (25.00 m² ayrıca yazılmış), yani 25 m² iki satırda birden sayılıyor. HACİM v02 avluyu açık modelledi, modelde A K1 brüt 145.0. A zemin katta aynı durumdaki teras brütten düşülmüş (363.96 yerine 170.00), 1. katta düşülmemiş.
  Beklenen: A 1. kat `BRÜT ALAN : 145.04 m²` (170.00 − 24.96, DXF şema değerleri). Kaynak "DXF şema KAT BRÜTÜ − KAT BAHÇESİ" yazılsın. A toplu pafta `TOPLAM KAPALI ALAN : 677.04 m²` (362.00 + 170.00 + 145.04). Özet JSON ve OKUBENI aynı değerlere çekilsin.

---

## UYARI (önerilen)

- **[U-v2-1] Sorumlu: HACİM** | `ERA01_model_site_v02.skp` (ARAZI yarma, `DGR_GARAJ_400x230`), `era01_model_gen.py` (`FOOT.append((YARMA, zc(167.25)...`)
  Otopark taban kotu 167.15 (DXF ve vaziyet "KAPALI OTOPARK GİRİŞİ +167.15"). Önündeki yarma ise 167.25'te, yani dış zemin garaj tabanından 10 cm yüksek (ters eğim, su içeri akar). Yarma 167.15'e indirilsin ya da 167.15 kademesi eklensin. Rampanın düz bırakılması (Y rampa eğimi yok) HACİM'in varsayımı olarak kabul. Kullanıcı istemedikçe eğimli rampa gerekmiyor.

- **[U-v2-2] Sorumlu: HACİM** | `02-model/OKUBENI.md`
  Belgede iç çelişkiler kalmış:
  - Madde 15 "Modellenmeyenler" listesinde hâlâ "korkuluk" ve "rampalar" yazıyor; v02'de cam korkuluk ve rampa yarması/istinat duvarları modellendi.
  - Bloklar tablosu ve Çelişkiler madde 1'de D "1. kat güney 10.75 m" yazıyor. Model brütü 129.8 m² = 10.55 × 12.30; DXF'te kapalı kısım 10.55 m.
  Metin düzeltilsin, modele dokunmaya gerek yok.

- **[U-v2-3] Sorumlu: PAFTA** | `ERA01_boyama_D-blok-kat-planlari_v02.jpg`, `ERA01_boyama_A-blok-kat-planlari_v02.jpg`
  - D zemin (1/150): D1 "GİRİŞ HOLÜ 8.50 m²" yazısı ±0.00 kot sembolü ve kapı çizgisiyle çakışıyor.
  - A zemin (1/200): dış merdivenin liste numarası "2" kırmızı giriş üçgeninin içinde kalıyor.
  Yazı ve numara kot sembolünden ve üçgenden uzaklaştırılsın.

- **[U-v2-4] Sorumlu: HACİM** | `DGR_375x280` (A avlusu batısı)
  DXF'te etiketsiz 375 cm'lik avlu doğramasının yüksekliği 280 kabul edilmiş. Avlunun öteki doğramaları (P-10 255×220, parapet 53) ile aynı cephe ritminde değil, ama planda etiket yok. HACİM'in varsayımı kabul. Kullanıcıya teslim özetinde açık konu olarak belirtilsin.

---

## NOT

- **HACİM ↔ PAFTA tutarlılığı:**
  - A avlusu: modelde açık, paftada açık alan (teras tonu, tefrişli).
  - D çatısı ve terası: çatı güneyde, teras kuzeyde (+3.50); vaziyette, D planlarında ve modelde aynı.
  - B otopark girişi: kuzey cephe, aynı aks aralığı.
  - Korkuluklar: 110 cm cam (model), çift çizgi (pafta).
  - Kotlar ve blok yerleşimi: tur 1'deki gibi tutarlı.
  - Brüt alanlar: A 1. kat dışında aynı (H8).
- **v02'de yeni geometri hatası görülmedi.** Kontrol, üretici kodu, rapor JSON'u ve PNG'ler üzerinden yapıldı: çatı ve döşeme çakışması yok, B2 tavanı düzeltildi, avlu çatı boşluğu cephe kaplaması dış yüzüne kadar açık. Model 611.8 KB, 52 bileşen tanımı, 149 örnek. Hafiflik korunmuş.
- Net alanlar ve mahal adları değişmedi (DXF ile uyumlu, tur 1). PAFTA bütün kat paftalarını A3'e almış; yalnız B'nin iki bodrumu 1/150'de. Toplu paftalar: A 1/200, B 1/250, C ve D 1/150.
- Font Carlito (Calibri metrik eşdeğeri), proje.md'ye işlenmiş.
- v01 dosyaları arşivde duruyor, silinmemiş (ofis kuralına uygun).

## Kontrol edilenler
- H1–H7 ve U1–U13 kapanış kontrolü: ✓ (13 UYARI'nın 13'ü, 7 HATA'nın 7'si kapandı)
- Kesinleşen 6 varsayımın uygulanması: 1 (brüt terassız) A 1. katta ✗ (H8), diğerleri ✓. 2 ✓, 3 ✓, 4 ✓ (B bodrumları 1/150 sapması kabul), 5 ✓, 6 ✓
- HACİM ↔ PAFTA tutarlılığı (avlu, D çatısı ve terası, otopark girişi, korkuluklar): ✓
- Ofis standartları (A3, başlık, logo, toplam kapalı alan, adlandırma, model hiyerarşisi ve palet): ✓
