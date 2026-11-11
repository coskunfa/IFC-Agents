# Proje: Deneme Villa

- **Proje kodu**: DNM01
- **Tür / konum / alan**: Müstakil villa; bodrum (boş) + giriş kat + 1. kat; 1. kat üstünde 4 kırma çatı (çatı katı yok); dış ölçü 13.60 × 10.10 m (~137 m²/kat)
- **Kat yüksekliği**: 3.50 m (villa varsayılanı)
- **Aşama**: Konsept
- **Aktif agent'lar**: ÇİZGİ, HACİM, PAFTA, DENETÇİ
- **Model detay seviyesi**: KÜTLE + CEPHE (varsayılan)
- **Boyama stili**: Konsept gri (giriş kat + 1. kat; bodrum boyanmaz)
- **Teslim formatı**: DXF + PDF (çizim), SKP (model)
- **Teslim tarihi**: -

## Brief
Kullanıcının tek çizgi eskiz DXF'inden (00-girdi) konsept kat planları çizilecek; kullanıcı onayından sonra SketchUp modeli kurulacak.

## Girdiler (00-girdi/)
| Dosya | Açıklama |
|---|---|
| DNM01_girdi_eskiz-plan.dxf | Kullanıcı eskizi: giriş kat + 1. kat, dış duvarlar `2_IFC_Wall`, diğerleri katman 0; mahal adları yazılı; kapılar kısa çizgi işaretleri |

## Eskiz okuması
- Giriş kat: merdiven holü, WC, asansör, mutfak (ortada ada), salon (TV'li oturma, oturma, şömine hattı, yemek bölümü), mahaller arası 10 cm duvar.
- 1. kat: 4 yatak odası; merdiven yanında banyo, ortadaki iki odaya birer banyo, ebeveyn banyosu (duş, kapalı WC, jakuzi, çift lavabo) + giyinme odası.
- Eskiz DXF başlığında birim mm görünüyor ama ölçüler cm (basamak 27, duvar 20) → **cm** kabul edildi.

## Varsayımlar
- (5 dk içinde cevapsız, varsayılan uygulandı) Saçak 50 cm, cephe kaplaması dış yüzünden.
- (cevapsız, varsayılan) Pencere parapet/yükseklik: salon ve mutfak 0/300, ebeveyn 0/300, diğer yatak odaları 90/210, banyo-hol-giyinme 150/150.
- (cevapsız, varsayılan) Kapı yükseklikleri: iç 220, ana giriş 250.
- (cevapsız, varsayılan) Tek kesit A-A (merdiven + salon/mutfak).
- (cevapsız, varsayılan) Bodrum tamamen toprak altı, penceresiz, kaplamasız; arazi ±0.00 düz.
- Sayfa üstü = kuzey.
- Pencereler eskizde yok; ÇİZGİ konsept seviyesinde yerleştirir (salon geniş doğrama, mutfak ve yatak odalarına birer pencere, banyolara küçük pencere). Kullanıcı gerekirse değiştirecek.

- (DENETÇİ soruları S1–S10, 5 dk cevapsız → öneriler uygulandı) P1 mutfak parapet 100 / h 200; çatı kotları ÇİZGİ şeması (çatı döşemesi üstü +7.00, saçak alt +7.00 / kaplama üstü +7.20, mahya +8.06), saçak 50; buzdolabı kuzey tezgâh doğu ucu 75×65; salon 3'lü koltuk 240; klozet tablosu 36–40×53–60; yatak 2 ve 3 15 cm güneye; statik konseptte not (kiriş); ıslak hacimlere 30×30 şaft + mekanik havalandırma; salon güney/doğu önüne 3 m teras (dış yemek + oturma, boyamada); toplam kapalı alan bodrum dahil 412.10.

## Kararlar günlüğü
| Tarih | Karar | Kim söyledi |
|---|---|---|
| 2026-11-11 | Proje ÇİZGİ + HACİM ile başlatıldı; çizim onayından sonra model | Kullanıcı |
| 2026-11-11 | Proje kodu DNM01 – Deneme Villa | Kullanıcı |
| 2026-11-11 | Aynı izdüşümde bodrum kat: boş mahal (merdiven ve lift devam eder). Çatı katı yok; 1. kat üstü 4 kırma çatı | Kullanıcı |
| 2026-11-11 | Ana giriş: kuzey (üst) cephedeki işaret, merdiven holüne | Kullanıcı |
| 2026-11-11 | Mutfak-salon arası 10 cm duvar korunur, iki geniş geçiş | Kullanıcı |
| 2026-11-11 | Asansör ev tipi lift (eskizdeki kuyu ölçüsü kabul); merdiven basamak sayısı yeterli | Kullanıcı |

| 2026-11-11 | Kullanıcı v01 DXF'i düzeltti (tefriş): 00-girdi/DNM01_girdi_kullanici-revizyon_v01r.dxf → onaylı temel | Kullanıcı |
| 2026-11-11 | Çatı: 4 kırma, saçak 50 cm (kullanıcı '0,5 cm' yazdı → 50 cm yorumlandı, teyit bekleniyor), eğim %15 saçak ucundan, metal kenet, çatı arası mahal değil | Kullanıcı |
| 2026-11-11 | ÇİZGİ (v02 + çatı planı + kesit), HACİM (model), PAFTA (2 kat boyama) paralel; sonra DENETÇİ (özellikle tefriş) | Kullanıcı |

## Açık konular
- Pencere/kapı yükseklikleri, saçak, kesit, bodrum: 5 dk içinde cevap gelmedi, varsayılanlar uygulandı; kullanıcı sonradan değiştirebilir.
