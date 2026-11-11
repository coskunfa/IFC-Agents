# Proje: ERA Evi

- **Proje kodu**: ERA01
- **Tür / konum / alan**: Çok bloklu konut sitesi (A, B, C, D bloklar + DXF'te E-F tanımları), Beykoz antetli uygulama/ruhsat seti; eğimli arazi (kotlar ~164–181 m)
- **Aşama**: Ruhsat/uygulama seti mevcut → sunum amaçlı model + boyama
- **Aktif agent'lar**: HACİM, PAFTA, DENETÇİ
- **Model detay seviyesi**: KÜTLE + CEPHE (varsayılan); olabildiğince az çizgi/yüz, hafif model
- **Boyama stili**: Konsept gri, DNM01'de yapılan tarzda (ofis referansları)
- **Teslim formatı**: SKP (model + görüntüler), JPEG (boyamalar)
- **Teslim tarihi**: -

## Brief
Kullanıcının hazır proje DXF'inden (00-girdi/ERA01_girdi_proje.dxf):
1. **HACİM**: Tüm blokların SketchUp modeli + arazi modeli. Kat yükseklikleri, pencere boyları, çatı ve cephe DXF'teki kesit/görünüşlerden okunacak, onlarla uyumlu olacak. Arazi kademeli (teraslı) olabilir, smooth gerekmez; kotlar ve eğimler yaklaşık olarak tutmalı. Minimum çizgi ve geometri.
2. **PAFTA**: Vaziyet planı boyaması + her blok için ayrı ayrı tüm kat planı boyamaları (DNM01 tarzı).
3. **DENETÇİ**: İki agent'ın çıktılarını DXF'e ve birbirine göre kontrol.

ÇİZGİ bu projede yok: DXF kullanıcının hazır projesidir, doğrudan girdi olarak (onaylı kabul) kullanılır.

## Girdiler (00-girdi/)
| Dosya | Açıklama |
|---|---|
| ERA01_girdi_proje.dxf | Tam proje seti (25 MB, model alanında 4 sıra pafta: A, B, C, D blok sıraları). Her sırada: aplikasyon/vaziyet, vaziyet kesitleri, bodrum/zemin/1. kat/çatı planları, şablon-hesaplar, kesitler, görünüşler. Birim cm kabul (header mm diyor). Planlar çoğunlukla blok (INSERT) olarak. |

## DXF ilk okuması (ŞEF)
- A Blok (±0.00 = 172.95): 1. bodrum -2.80 (170.15), zemin +1.20 (174.15), 1. kat +4.70 (177.65), çatı +8.20 (181.15). (Düzeltme: "2. bodrum -7.00 (167.15)" A'ya değil B bloğun kapalı otoparkına ait — PAFTA/HACİM tespiti)
- B Blok: 2. bodrum (otopark) -7.00 (167.15), 1. bodrum -4.00 (170.15), zemin ±0.00 (174.15), çatı katı +3.50 (177.65)
- C Blok: 1. bodrum -4.00 (170.36), zemin ±0.00 (174.36), çatı +3.50 (177.86)
- D Blok: 1. bodrum -3.00 (164.25), zemin ±0.00 (167.25), 1. kat +3.50 (170.75), çatı +3.50 (170.75) — çelişki kontrol edilmeli; DXF'te "E-F" adlı bloklar da var (D sırası içinde E/F blokları olabilir)

## Varsayımlar
- DXF birimi cm (sayfa boyutları ve ölçü yazılarından).
- Boyamada bodrum katlar da boyanır (kullanıcı "bütün blokların ayrı ayrı kat planı" dedi); otopark/teknik hacimler sade gri.
- Kuzey yönü vaziyet planındaki kuzey okuna göre.
- (HACİM soruları, 5 dk cevapsız → öneriler uygulandı) 1) Cephe kaplaması standart: DXF dış çizgisinin 20 cm dışında. 2) D blok: +3.50 (170.75) 1. kat kuzey terası; kırma çatı saçak +7.00, mahya +7.82. 3) B otopark girişi (kuzey, 167.15): v02'de basit yarma + garaj kapısı boşluğu. 4) A 1. kat "KAT BAHÇESİ" açık avlu (v02). 5) SALON+MUTFAK mahalleri kuru grupta (v02). 6) Arazi yalnız parsel içi.
- DXF hataları (bilgi): B GR1 görünüşü A blok cephesini gösteriyor (kullanılmadı); A kesitinde -3.30 (169.95) → 169.65 olmalı.
- DXF'teki "E-F" blokları D bloğun planları; sitede 4 blok (A, B, C, D).
- (PAFTA soruları, 5 dk cevapsız → öneriler uygulandı) 1) D blok 1. kat +3.50, çatı +7.00 (174.25); DXF'teki çatı kotu yazımı hatalı. 2) A zemin brüt 170.00 (şemadaki 363.96 terası kapsıyor). 3) Brüt poligonu olmayan katlarda şema "KAT BRÜTÜ": A 1. kat 170.00, C bodrum 135.00, C zemin 135.00. 4) D 1. kat brüt: DENETÇİ'nin DXF tespitine göre (129.77 olası). 5) Vaziyette sert zemin şimdilik çim ağırlıklı; kullanıcı poligon verirse yeniden boyanır.
- Boyama fontu Carlito (sistemde Calibri yok; metrik eşdeğer).
- (DENETÇİ soruları, 5 dk cevapsız → öneriler uygulandı) 1) Brüt alanlar terassız kapalı alan. 2) Numara+liste yalnız ad sığmayan yerde. 3) Pafta başlığı "MİMARİ KONSEPT PROJE". 4) Tüm paftalar A3. 5) Teras korkuluğu 110 cm ince korkuluk/cam panel. 6) B çatısı kotlara göre (%21), "%15" yazısı yok sayılır.

## Kararlar günlüğü
| Tarih | Karar | Kim söyledi |
|---|---|---|
| 2026-11-11 | Proje ERA01 – ERA Evi; aktif: HACİM + PAFTA, sonra DENETÇİ | Kullanıcı |
| 2026-11-11 | Model kesit/görünüşlere göre (kat yükseklikleri, pencereler, çatı, cephe); arazi kademeli olabilir, az çizgi | Kullanıcı |
| 2026-11-11 | Boyama: vaziyet planı + her blok ayrı ayrı tüm katlar, DNM01 tarzı | Kullanıcı |

## Açık konular
- HACİM v02 düzeltmeleri (avlu, otopark yarması, kuru grup) DENETÇİ turundan sonraki düzeltme turunda yapılacak.
