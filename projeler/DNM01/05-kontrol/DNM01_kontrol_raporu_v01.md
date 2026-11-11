# Kontrol Raporu v01 (2026-11-11)
Sonuç: **DÜZELTME GEREKLİ**

Kontrol edilen sürümler:
- ÇİZGİ v02 TASLAK: `01-cizim/taslak/DNM01_cizim_kat-planlari_v02.dxf/.pdf/.png`, `01-cizim/OKUBENI.md`
- HACİM v01: `02-model/OKUBENI.md`, `02-model/*.png`, `02-model/kaynak/*` (SKP repoda yok)
- PAFTA v01: `03-boyama/DNM01_boyama_{giris-kat,1-kat,kat-planlari}_v01.jpg`, `03-boyama/OKUBENI.md`
- Temel: `00-girdi/DNM01_girdi_kullanici-revizyon_v01r.dxf`

Yöntem: DXF blok ölçüleri ve kapı menteşe/kanat geometrisi ezdxf ile ölçüldü (blok içi gerçek geometri, ölçek ve yansıma uygulanmış). Pencere konumları kullanıcı DXF'i, v02, HACİM tablosu ve boyama (0.673 px/cm önizleme ölçeğinde) arasında karşılaştırıldı. Model; OKUBENI, `dnm01_model_gen.py` parametreleri ve PNG'lerden değerlendirildi.
Önceki rapor yok (ilk kontrol).

---

## HATA (düzeltilmesi zorunlu)

- **[H1] Kapı çakışması: Yatak odası 1 kapısı ile Banyo 1 kapısı** | Sorumlu: ÇİZGİ, ardından PAFTA
  - Dosya: `DNM01_cizim_kat-planlari_v02.dxf`, 1. kat, `IFC_DOOR_90` ekleme noktası (290, 2465), dönüş 90°. Boyamalar: `DNM01_boyama_1-kat_v01.jpg`, `DNM01_boyama_kat-planlari_v01.jpg`
  - Sorun: Menteşe (290, 2460) noktasında. Açık kanat y = 2460 hattında x 210–290 aralığına yatıyor. Bu konum, Banyo 1 kapısının (`IFC_DOOR_80`, açıklık x 190–260, y 2465–2475) tam önü. Yatak odası kapısı açıkken banyoya geçilemiyor. Kapı açılışı kuralına aykırı (tefris-kurallari "Kapı açılışı mobilyaya/kapıya çarpmaz").
  - Beklenen: Yatak 1 kapısının menteşesi açıklığın güney ucuna (290, 2380) alınsın. Açık kanat y ≈ 2380 hattında kalsın, banyo kapısının önü boş olsun. PAFTA aynı düzeltmeyi boyamaya işlesin.

- **[H2] Mutfak P1: tabana kadar cam, önünde tezgâh** | Sorumlu: ÇİZGİ + HACİM (önce kullanıcı kararı, bkz. S1)
  - Dosya: v02 DXF, `IFC_PENCERE_240` P1 (x 225–465, PARAPET 0, YUKSEKLIK 300); `IFC_MUTFAK TEZGAH` (x 20–560, y 20–80). Model: `DGR_240x300`. Boyama: giriş kat.
  - Sorun: Doğrulandı. 540 cm'lik güney tezgâhı P1'in tamamının önünden geçiyor. Parapet 0 olduğu için tezgâh, dolap gövdesi ve tezgâh arkası cama dayanıyor. Çizim, model ve boyamanın üçünde de aynı çelişki var. (Kullanıcının revizyon DXF'inde P1 YUKSEKLIK 120'ydi. 0/300 değeri ŞEF varsayımından geliyor.)
  - Beklenen: Kullanıcı kararına göre P1 parapet/yükseklik değeri (öneri 100/200, üst kot +3.00 sabit) ya da tezgâhın P1 önünde kesilmesi. Karar ÇİZGİ (PENCERE tablosu + öznitelik), HACİM (`DGR_240x200` bileşeni) ve kesit A-A'ya birlikte işlensin.

- **[H3] Çatı kotları çizim ile model arasında 20 cm farklı, çatı döşemesi üstü 10 cm farklı** | Sorumlu: HACİM (çizime uyum). Kot kararı kullanıcıda, bkz. S2
  - Dosya: `01-cizim/OKUBENI.md` "Çatı" ve kesit A-A; `02-model/OKUBENI.md` "Kotlar"; `dnm01_model_gen.py` (`EAVE_Z = 700`, çatı döşemesi 660–690)
  - Sorun:
    | | ÇİZGİ v02 | HACİM v01 |
    |---|---|---|
    | Çatı döşemesi üstü | +7.00 (taşıyıcı +6.90 + 10 cm kaplama) | +6.90 (kaplama yok) |
    | Saçak ucu | alt +7.00, kaplama üstü **+7.20** | üst **+7.00** (alt +6.80) |
    | Mahya | alt +7.8625, kaplama üstü **+8.0625** | üst **+7.8625** |
    Saçak 50 cm (dış duvardan 70), plan 1500 × 1150, eğim %15, mahya x 505–855 / y 505 (350 cm) ve yükselme 86.25 iki tarafta da aynı. Model çatısı bütünüyle 20 cm aşağıda.
  - Beklenen: Çatı döşemesi üstü, saçak ve mahya kotları çizim, kesit, çatı planı ve modelde aynı olsun. Kullanıcı aksini söylemezse çizim esas alınır ve HACİM `EAVE_Z` ile çatı döşemesini güncelleyip OKUBENI'yi düzeltir.

- **[H4] Mutfakta buzdolabı çizimde yok, boyamada var (çizim ≠ boyama, tefriş eksiği)** | Sorumlu: ÇİZGİ (kullanıcı kararıyla, bkz. S3)
  - Dosya: v02 DXF (giriş kat mutfak; `IFC_BUZDOLABI_75x65` bloğu purge edilmiş); `03-boyama` giriş kat (PAFTA kuzey tezgâhın doğu ucuna, yaklaşık x 222–297, 75×65 buzdolabı eklemiş)
  - Sorun: tefris-kurallari, mutfakta "tezgâh + eviye + ocak + buzdolabı" istiyor. Kullanıcı revizyonunda buzdolabı silinmiş, v02'de de yok. Boyama çizimden farklı.
  - Beklenen: Buzdolabı v02 çizimine PAFTA'nın yerleşimiyle (kuzey tezgâh doğu ucu, x 225–300, y 465–530, ölçüler 5 cm'ye oturtularak) eklensin. Ya da kullanıcı ankastre/başka yer derse boyama buna göre düzeltilsin.

- **[H5] Salon 3'lü koltuk ölçüsü aralık dışında (246 × 93)** | Sorumlu: ÇİZGİ + PAFTA (kullanıcı tefrişi, bkz. S4)
  - Dosya: v02 DXF, giriş kat salon, `A$C8cc23e19` × 2 (bbox 926–1172 × 447–540 ve 1188–1281 × 573–819). Boyama aynı.
  - Sorun: Kontrol aralığı 3'lü koltuk 210–240 × 85–100. Ölçülen 246.0 × 93.2. Uzunluk aralığın dışında.
  - Beklenen: 240'lık 3'lü koltuk (`IFC_KOLTUK 3LU` 240 × 87.5) kullanılsın ya da kullanıcı bunu "4'lü/246" olarak onaylasın ve tablo güncellensin.

- **[H6] Klozet ölçüsü aralık dışında (36 × 53.4)** | Sorumlu: ÇİZGİ + PAFTA, ya da tablo güncellemesi (bkz. S5)
  - Dosya: v02 DXF, `IFC_KLOZET` (5 adet: giriş WC, Banyo 1/2/3, ebeveyn WC). Boyama aynı.
  - Sorun: Kontrol aralığı klozet 37 × 55–60. Blok 36.0 × 53.4. Bu blok ofis şablonundaki (`ref_kat-plani-cizimi_IFC-ornek.dxf`) bloğun aynısı, dolayısıyla tablo ile ofis bloğu çelişiyor.
  - Beklenen: Ya klozet bloğu 37 × 55 ölçüsüne getirilsin ya da kullanıcı tablodaki aralığı ofis bloğunu kapsayacak şekilde güncellesin (DENETÇİ önerisi: tablo).

- **[H7] Merdiven mahal adı ve alanı çizimde yazılı değil** | Sorumlu: ÇİZGİ
  - Dosya: v02 DXF. Bodrum, giriş ve 1. katta merdiven `0_IFC_Area` poligonları var (7.15 / 7.15 / 6.84 m²), ama `0_IFC_ROOM_TEXT_50` yazısı yok.
  - Sorun: cizim-standardi "Zorunlu içerik: mahal adı ve alanı". Boyamada "MERDİVEN 7.20 / 6.80" yazıyor, çizimde yok. Çizim ile boyama arasında mahal adı farkı var.
  - Beklenen: Üç katta da `MERDİVEN` + alan yazısı (`0_IFC_ROOM_TEXT_50`, mahal içinde boş yerde).

- **[H8] SketchUp modeli (teslim ürünü) repoda yok, doğrulanamıyor** | Sorumlu: HACİM / ŞEF
  - Dosya: `02-model/DNM01_model_kutle_v01.skp` (yok; ağ engeli, 403)
  - Sorun: proje.md teslim formatı SKP. Grup/tag yapısı, bileşenler, malzemeler ve dosya boyutu yalnız betik ve OKUBENI üzerinden kontrol edilebildi. SketchUp içindeki gerçek durum doğrulanamadı.
  - Beklenen: SKP `02-model/` altına konsun (kullanıcı bulut bağlantısından indirir ya da ağ izni verilir). Ardından DENETÇİ tag ve grup ağacını, purge durumunu ve dosya boyutunu yeniden kontrol eder.

---

## UYARI (önerilen)

- **[U1] Sorumlu: ÇİZGİ/PAFTA (kullanıcı tefrişi, bkz. S6) | Banyo 2 ve Banyo 3'e erişim dar.** Yatak 2 (bbox x 445–645, y 1860–2110) ve yatak 3 (x 655–855) ile banyo güney duvarı (y 2140) arasındaki şerit: yatak kenarında 75 cm, komodin önünde 35 cm. Banyo kapıları (x 515–585 / 715–785) bu şeride açılıyor. Yatak kenarı kuralı (≥ 60) sağlanıyor, ama banyoya giden ana geçiş 80 cm'nin altında. Öneri: iki yatak 15 cm güneye kaydırılsın (şerit 90 cm olur).
- **[U2] Sorumlu: PAFTA | Yatak odası 1 (17.14 m²) için çalışma masası yok.** tefris-kurallari "≥10 m²: (yer varsa) çalışma masası". Yatak 1'de doğu duvarı önünde x 160–290, y 2130–2370 boş. 120×60 masa sığar. Yatak 2 ve 3'te gardırop 535 cm olduğundan yer dar, eklenmese de olur. PAFTA eklerse ÇİZGİ'ye de bildirilsin (çizim ve boyama aynı kalsın).
- **[U3] Sorumlu: PAFTA (karar S9) | Bahçe/teras tefrişi yok.** Giriş kat boyamasında yalnız çim, ağaç ve giriş basamakları var. tefris-kurallari "Teras/bahçe: oturma grubu ve/veya dış yemek masası", konsept gri stil ve ref s07 ise gri ahşap/taş teras, şemsiye ve şezlong istiyor. Salonun güney ve doğu cepheleri tabana kadar camlı (P2, P3, P4).
- **[U4] Sorumlu: PAFTA | Giriş kat net alan toplamı çizimle uyuşmuyor.** Boyamada 125.40 yazıyor (yuvarlanmış değerlerin toplamı). ÇİZGİ toplamı 125.27, 0.10'a yuvarlanınca 125.30. Toplam ham değerden yuvarlansın (1. kat 121.90 ikisinde de aynı).
- **[U5] Sorumlu: PAFTA | Brüt alan 0.10 hassasiyette değil, A3 sayfada toplam kapalı alan yok.** "BRÜT ALAN : 137.36" yazılı, 137.40 olmalı (ref: 124.50 formatı). Konsept gri §2-A'ya göre A3 kat planları sayfasının sağ altında `TOPLAM KAPALI ALAN` bulunmalı (kapsam için bkz. S10).
- **[U6] Sorumlu: PAFTA | Font Calibri değil, Carlito.** Metrik olarak eşdeğer, ama standart tek font Calibri istiyor. Calibri dosyası temin edildiğinde yeniden üretilsin (font dosyası ŞEF/kullanıcıdan istenmeli).
- **[U7] Sorumlu: ŞEF / PAFTA / HACİM | Model ve boyama onaylı çizimden değil, kullanıcı revizyon DXF'inden üretildi.** `01-cizim/onayli/` boş (ŞEF iş emriyle). v02 onaylanınca, v02'deki küçük farklar (tezgâh ucu 297 → 300, dolap 342 → 340, mahal yazı konumları, pencere öznitelikleri) ve H1–H7 düzeltmeleri için boyama yeniden üretilmeli, model kontrol edilmeli.
- **[U8] Sorumlu: ÇİZGİ (bilgi), statik | Giriş kat merdiveni ile bodrum merdiveni üst üste: geometrik çakışma YOK, mesnet eksik.** Doğrulandı: üç kat aynı L merdiven, aynı izde (alan poligonu 20–427 × 637–990), katlar arası 350 cm kaydırmalı. Her noktada üst kolun altında yaklaşık 3.10–3.30 m kafa yüksekliği kalıyor. Bodruma iniş x ≈ 427'den, çıkış x 20–130 / y 637'den yapılıyor, ikisi de giriş holüne bağlanıyor. Ancak giriş ve 1. kat kollarının ilk basamakları alttaki kolun döşeme boşluğu üzerinde. Kol başına mesnet kirişi gerekir. Konsept kesitte "kiriş/statik projeye göre" notu yeterli. Model çizimle aynı (HACİM not 4).
- **[U9] Sorumlu: ÇİZGİ/kullanıcı (S7) | İç duvar aksları katlar arasında örtüşmüyor.** Doğrulandı: giriş katında K-G duvar x 675, D-B duvar y 535. 1. katta K-G duvarlar x 295 / 650 / 1010, D-B duvarlar y 560 / 680 (kat göreli). 1. kat bölmelerinin altında duvar yok, 13.60 × 10.10 açıklıkta iç kolon yok. Statik çözüm (kiriş/iç kolon) ya da aks hizalaması gerekir.
- **[U10] Sorumlu: ÇİZGİ/kullanıcı (S8) | Penceresiz ıslak hacimler.** Doğrulandı: Giriş WC (3.08), Banyo 1 (3.08), Banyo 2 (3.12), Banyo 3 (3.12) cepheye ulaşmıyor. Mekanik havalandırma ve tesisat şaftı çizimde gösterilmeli (konsept seviyede şaft kutusu ve not).
- **[U11] Sorumlu: ÇİZGİ | Kesit A-A etiket ve okunabilirlik.** Giriş kattaki "HOL" yazısı duvar çizgisiyle çakışıyor. Plandaki adı "GİRİŞ HOLÜ". Kırık kesit hattı (x 75 → x 420) yüzünden çatı paketi y = 600'de basamak yapıyor, konsept sunumda yanlış anlaşılabilir. Ya düz bir kesit hattı alınsın ya da kesitte bu basamak için açıklama notu bulunsun.
- **[U12] Sorumlu: ÇİZGİ | OKUBENI güncel değil.** Varsayım 4 (şömine) ve 9 (şömine, 8 kişilik yemek masası 240×100, buzdolabı blokları) v02'de purge edilmiş elemanları anlatıyor. "Asansör kapısı 80" yazıyor ama DXF'te asansör kapısı bloğu yok (yalnız boşluk var). Modelde `KAPI_80x220` 9 adet, DXF'te 5 adet `IFC_DOOR_80` var. Fark asansör kapıları ve sürgü olabilir, listelensin.
- **[U13] Sorumlu: ÇİZGİ | Purge eksiği.** DXF'te kullanılmayan çizgi tipleri var: `GC5102G0200$0$HIDDEN`, `( Hidden )` (kullanıcı dosyasından gelmiş). Bloklar ve katmanlar temiz (boş katman ve kullanılmayan blok yok).
- **[U14] Sorumlu: PAFTA/ÇİZGİ | Yatak 2 ve 3'te kapı kanadı ile gardırop arası 40–45 cm.** Açık kanat x = 400'de, gardırop yüzü x = 360'ta (yatak 3: 900 / 945). Menteşeli gardırop kapakları (~50 cm) açık kapıya çarpar. Sürgülü gardırop önerilir (çizimde/notta).
- **[U15] Sorumlu: HACİM | Kat sahneleri gerçek kesit değil.** `..._kat-00/01/b1_v01.png` duvarları tam yükseklikte üstten gösteriyor. Kapı ve pencere boşlukları okunmuyor. hacim.md "her kat için üstten kesit görünüşü" istiyor. Sahneler +1.20 m kesit düzlemiyle alınsın.
- **[U16] Sorumlu: HACİM | Küçük görsel konular.** Kontrol PNG başlıklarında Türkçe karakter yok ("guneydogu", "Giris kat ustten"). Aksonometrik görünüşte batı cephesinde tekil bir kısa çizgi artefaktı var (kat arası kaplama derzi olabilir). Az çizgi ilkesi açısından kontrol edilsin.
- **[U17] Sorumlu: ÇİZGİ (bilgi) | Tefriş blok katmanı.** `IFC_MUTFAK TEZGAH` bloğu `6_IFC_Furniture_WC` katmanında, `IFC_VITRA_DOLAPLI LAVABO` içinde katman `0`'da bir WIPEOUT var. İkisi de ofis şablonundan geliyor, düzeltme gerekmez. Şablon güncellenirken düşünülebilir.

---

## KULLANICIYA SORU (önerilerle)

1. **S1, Mutfak P1 penceresi** (H2): Tezgâh camın önünde. **Öneri:** P1 parapet 100 / yükseklik 200 (üst kot +3.00 aynı kalır), tezgâh korunur. Alternatif: parapet 0 kalsın, tezgâh P1 önünde (x 225–465) kesilsin.
2. **S2, Çatı** (H3): (a) Saçak 50 cm olarak teyit ediliyor mu ("0,5 cm" yazılmıştı)? (b) Kotlar hangi şemaya göre olsun? **Öneri:** ÇİZGİ şeması: çatı döşemesi üstü +7.00 (10 cm yalıtım/şap, çatı arası kullanılmasa da ısı yalıtımı gerekir), saçak alt +7.00 / kaplama üstü +7.20, mahya kaplama üstü +8.06. HACİM modeli buna göre 20 cm yükseltir.
3. **S3, Buzdolabı** (H4): Revizyonunuzda buzdolabı silinmiş. **Öneri:** Kuzey tezgâhın doğu ucunda (mutfak kapısı yanında) 75×65 boy buzdolabı. PAFTA böyle boyadı, çizime de işlensin. Ankastre/başka yer isterseniz belirtin.
4. **S4, Salon koltukları** (H5): 246 cm'lik koltuklar tablo aralığının (210–240) dışında. **Öneri:** 240'lık 3'lü koltukla değiştirilsin. Bu ölçüde ısrar ediyorsanız tefriş tablosuna "4'lü kanepe 240–260" satırı eklenir.
5. **S5, Klozet ölçüsü** (H6): Ofis bloğu `IFC_KLOZET` 36×53.4, tablo 37×55–60 diyor. **Öneri:** Tablo "Klozet 36–40 × 53–60" olarak güncellensin, blok kalsın.
6. **S6, Yatak 2/3 yerleşimi** (U1): Banyo kapısına giden geçiş 75 cm, komodin önünde 35 cm. **Öneri:** İki yatak 15 cm güneye kaydırılsın, geçiş 90 cm olur.
7. **S7, Statik / iç aks hizası** (U9): **Öneri:** Konsept aşamada kalsın, 1. kat bölmeleri altında kiriş varsayımı not edilsin. İsterseniz giriş kat mutfak/salon duvarı x 650'ye, hol/mutfak duvarı y 560'a kaydırılarak akslar hizalanır.
8. **S8, Penceresiz ıslak hacimler** (U10): **Öneri:** Mekanik havalandırma kabul edilsin. Her banyo/WC'ye 30×30 tesisat şaftı çizilsin.
9. **S9, Bahçe terası** (U3): **Öneri:** Salonun güney ve doğu cephesi önüne yaklaşık 3.00 m derinlikte sert zemin teras, dış yemek masası ve oturma grubu (boyamada, ref s07 gibi). İsterseniz ÇİZGİ teras sınırını çizime de ekler.
10. **S10, Toplam kapalı alan** (U5): A3 sayfasına yazılacak toplam kapalı alan bodrum dahil mi (412.10 m²), yalnız boyanan iki kat mı (274.70 m²)? **Öneri:** Bodrum dahil 412.10 m².

---

## Kontrol edilenler

### Tefriş: işlev (tefris-kurallari)
- Salon 64.02 m² (> 40): oturma grubu (2 × 246 koltuk, 2 tekli KL3 87×77, orta sehpa Ø135, yan sehpa), TV ünitesi 240×45 + TV, 8 kişilik yemek masası 250×100 + 8 sandalye, büfe 200×50, halı ✓ (koltuk ölçüsü → H5). Şömine kullanıcı revizyonunda kaldırılmış (tabloda "varsa") ✓
- Mutfak 33.15 m² (kapalı, iki geniş geçişle salona bağlı): L tezgâh (batı 390 + kuzey 280 + güney 540, derinlik 60) ✓, eviye 1.5 ✓, ocak ✓, ada 240×100 + 3 bar taburesi (≥ 12 m² ada) ✓, buzdolabı ✗ → H4
- Giriş holü: vestiyer 210×60 ✓
- WC (giriş): klozet + lavabo ✓
- Ebeveyn yatak odası 22.39: çift yatak 160×200 + 2 komodin 40×50 ✓, giyinme odası (12.96, 3 gardırop dizisi 165 + 165 + 245) ✓, ek oturma grubu (2 tekli + sehpa) ✓
- Yatak odası 1/2/3 (17.14 / 14.97 / 15.24): çift yatak 160×200 + 2 komodin ✓, gardırop 340 / 535 / 535 × 60 ✓, çalışma masası yok → U2
- Ebeveyn banyosu: kapalı WC (klozet, sürgü kapı) ✓, çift lavabo 2 × 80×50 ✓, duş 100×100 ✓, jakuzi 160×110 ✓
- Banyo 1/2/3: klozet + lavabo 60×53 + duş 90×90 ✓
- Bodrum: boş mahal (kullanıcı kararı), tefriş gerekmez ✓
- Teras/bahçe: tefriş yok → U3

### Tefriş: ölçü (DXF blokları ezdxf ile ölçüldü)
- Çift yatak 160×200 ✓ · Tekli koltuk 87.4×76.5 ✓ · Yemek masası (8 kişi) 250×100 ✓ · Gardırop derinliği 60 ✓ · Tezgâh derinliği 60 ✓ · Lavabo 60×53 ✓, çift lavabo 80×50 ✓ · Duş 90×90 ve 100×100 ✓
- 3'lü koltuk 246×93 ✗ (H5) · Klozet 36×53.4 ✗ (H6)

### Tefriş: geçiş ve kapılar
- Mutfak: ada ile batı tezgâhı arası 145, güney tezgâhı arası 135, kuzey tezgâhı arası 155 (≥ 100/120) ✓. Mutfak kapısı (menteşe 400,530) tezgâh ucundan 20 cm açıkta ✓
- Ana giriş, WC, mutfak, yatak 2/3, ebeveyn, giyinme ve ebeveyn banyosu kapı kanatları mobilyaya çarpmıyor ✓ (ebeveyn banyo kapısı duştan 30 cm açıkta)
- Yatak 1 ile Banyo 1 kapıları çakışıyor ✗ (H1). Banyo 2/3 erişimi 75 cm (U1). Kapı ile gardırop arası 40–45 cm (U14)
- Yatak kenarı boşlukları ≥ 60 ✓ (yatak 1 güney 75, yatak 2/3 ayak ucu 85/90, ebeveyn ayak ucu 125)
- Salon: yemek masası çevresi ≥ 90, oturma ile masa arası 166 ✓

### Tefriş: çizim ↔ boyama
- Salon, yatak odaları, banyolar, giyinme, vestiyer: boyama DXF blok konum ve ölçülerinde birebir ✓ (yatak başlık yönleri de aynı)
- Fark: boyamada buzdolabı var, çizimde yok (H4). Saksı ve halılar yalnız dekor ✓

### Tutarlılık: çizim ↔ model ↔ boyama
- Dış ölçü 1360 × 1010, dış duvar 20 / iç duvar 10, kolon 20×40 × 8 / kat: üçünde aynı ✓
- Pencereler P1–P11: konum ve genişlikler kullanıcı DXF, v02, model tablosu ve boyamada aynı ✓. Parapet ve yükseklikler v02 öznitelikleri ile modelde aynı (ŞEF varsayımı) ✓. Model bileşen adetleri (DGR_*) 11 pencere ile tutarlı ✓
- Kapılar: ana giriş 100×250, oda 90, ıslak 80. Geçişler mutfak–salon 200 (y 165–365) ve hol–salon 120 (y 550–670): çizim, model ve boyamada aynı ✓
- Mahal adları: çizim = model (DK_* grupları) = boyama ✓. Yalnız MERDİVEN çizimde yazılı değil (H7)
- Alanlar: boyamadaki tüm değerler çizim alanlarının doğru 0.10 yuvarlaması ✓ (64.02 → 64.00, 33.15 → 33.20, 14.97 → 15.00, 12.96 → 13.00, 7.85 → 7.90 ...). Net toplam (giriş) U4, brüt U5
- Kat kotları −3.50 / ±0.00 / +3.50, kat yüksekliği 350 ✓. Döşeme paketi 10 + 30 + 10, net 3.00 ✓. Bodrum radye −3.90 / −3.60 + 10 kaplama ✓ (çizim ve model betiği aynı)
- Cephe kaplaması 20 cm dışta, bodrumda yok ✓
- Çatı: saçak 50 (dış duvardan 70), 1500 × 1150, %15, mahya 350 cm aynı ✓. Kotlar farklı ✗ (H3)
- Kesit A-A ↔ model: kat ve döşeme kotları, P1/P6 yükseklikleri, merdiven 24 × 14.58 / 27, üst üste kol düzeni aynı ✓. Çatı kotu farkı H3
- Merdiven üst üste: doğrulandı, çakışma yok, mesnet notu (U8)

### Kurallar: ÇİZGİ
- Tüm DIMENSION ölçüleri 5 cm'nin katı ✓. Duvar, alan ve kolon köşelerinde 5'in katı olmayan değerler yalnız merdivende (27 cm basamak, 14.58 rıht; ölçü uyarısında listeli, kullanıcı kabulü) ✓
- IFC katmanları şablonla uyumlu ✓. Yeni katmanlar ad kuralına ve CTB'ye uygun: `0_IFC_Dimension` (ACI 3, en ince), `2_IFC_Roof` (30 → 0.30), `2_IFC_Roof_Line` (41 → 0.20), `2_IFC_Roof_Hidden` (252 → 0.05, HIDDEN), `7_IFC_Terrain` (42 → 0.30), `0_IFC_Section_Line` (10 → 0.25, DASHDOT) ✓, raporda belirtilmiş ✓
- Bloklar katman 0'da ✓, boş katman ve kullanılmayan blok yok ✓ (çizgi tipi purge → U13)
- Duvar dış 20 / iç 10 ✓. Kapı açılışları, merdiven yön oku, asansör, kat adı, kot, ana ölçü zinciri, brüt alan ✓
- PDF: 5 sayfa A4 yatay 1/100 (A4'e sığıyor) ✓. Bilgi bloğunda proje adı ve kodu, çizim adı, ölçek, kağıt, tarih, sürüm, aşama, durum (TASLAK), IFC logosu, grafik ölçek ✓
- Taslak/onay akışı: v02 TASLAK, `onayli/` boş ✓ (onay bekleniyor)

### Kurallar: HACİM (betik ve OKUBENI üzerinden; SKP yok → H8)
- Kat grupları KAT_B1 / KAT_00 / KAT_01 + KAT_CATI + ARAZI, her eleman türü ayrı grup ve tag ✓
- DOSEME_KAPLAMA mahal bazında, ISLAK (WC, banyolar, mutfak, ebeveyn WC) / KURU ayrımı ✓
- Döşeme paketi 30 + 10 + 10 ✓. Cephe kaplaması 20 cm dışta ✓. Kat yüksekliği 3.50 ✓
- Doğrama: bölmeler ≥ 100 (P1 2 × 112.5, P2 3 × 160, P3 2 × 167.5, P4 2 × 142.5) ✓, 300 cm yükseklikte kayıt 150'de ✓, aynı ölçü tek bileşen (DGR_<g>x<y>) ✓
- Gri palet hacim.md'deki değerlerle birebir ✓, doku yok ✓
- Az çizgi: 1 547 yüzey / 3 688 kenar, tüm gruplar solid ✓
- Arazi tek yüzey ±0.00 (düz arazi) ✓. Sahneler: perspektif, aksonometrik, kuş bakışı, 3 kat ✓ (kesit olmaması → U15)

### Kurallar: PAFTA
- Konsept gri stil (§2-A): açık gri mahaller, ıslak hacim soğuk gri, mutfak bir ton koyu ✓. Beyaz dolgulu ince konturlu mobilya ✓. Suluboya ağaç + pembe çalı, sakin yeşil-gri çim ✓. Kırmızı dolu giriş üçgeni ✓. Referans s07/s08 ile görsel dil uyumlu ✓ (teras eksik → U3)
- Pastel/sakin palet, doygun renk yok ✓. Kolonlar en koyu (#050505), duvarlar koyu (#383838) ✓
- Mahal yazısı BÜYÜK HARF ad + küçük `xx.xx m²`, tüm mahaller etiketli ✓
- Alanlar 0.10'a yuvarlı, iki ondalık ✓. Net toplam ve brüt her planın altında ✓ (U4, U5)
- Ölçek 1/100, 600 dpi = 2.3622 px/cm. Önizlemede ölçüm: plan genişliği ≈ 3 210 px = 1 360 cm ✓. Pencere ve duvar konumları DXF ile örtüşüyor ✓. Çizgi ölçek ve kuzey oku ✓
- Bilgi bloğu (proje, çizim adı, ölçek, tarih, sürüm, aşama) ✓, IFC Architects logosu sol altta (konsept düzen) ✓, işveren logosu yok (belirtilmedi) ✓
- Bodrum boyanmamış (proje.md kararı) ✓. JPEG sRGB, yüksek çözünürlük ✓. Font → U6

### Kalite
- Çakışan etiket: kesitteki "HOL" (U11). Planlarda mahal yazıları v02'de mobilyadan arındırılmış ✓
- Yazım hatası görülmedi ✓. Boş pafta yok ✓
