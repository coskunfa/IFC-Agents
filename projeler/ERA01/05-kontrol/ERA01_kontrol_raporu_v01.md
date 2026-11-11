# Kontrol Raporu v01 (11.11.2026)
Proje: ERA01 ERA Evi · Tur 1 · Denetleyen: DENETÇİ
Sonuç: **DÜZELTME GEREKLİ** (7 HATA, 13 UYARI)

Denetlenen: `02-model/` (ERA01_model_site_v01.skp, 7 PNG, OKUBENI.md, kaynak/era01_model_rapor.json, era01_model_gen.py) ve `03-boyama/` (16 JPEG, onizleme/, OKUBENI.md, kaynak/era01_ozet.json, era01_vaziyet_donusum.json).
Referans: `00-girdi/ERA01_girdi_proje.dxf`. DXF bütün INSERT'ler açılarak okundu (PAFTA'nın `era01_dxf_duzlestir.py` aracı, çıktısı DENETÇİ scratchpad'ine yazıldı; proje klasörüne dosya eklenmedi).
Önceki rapor: yok (ilk tur).

---

## HATA (düzeltilmesi zorunlu)

- **[H1] Sorumlu: PAFTA** | Dosya: `ERA01_boyama_D-blok-1-kat_v01.jpg`, `ERA01_boyama_D-blok-kat-planlari_v01.jpg`, `kaynak/era01_ozet.json`, `OKUBENI.md` (Alanlar tablosu, Soru 4)
  Sorun: D Blok 1. kat brüt alanı **217.71 m²** yazılmış. Bu değer DXF'teki `D_K1 BRUT ALAN` poligonundan geliyor (17.70 × 12.30). Poligon 82.71 m²'lik terası da içine alıyor, yani katın tüm izi. DXF şeması `D_CK_SEMA` "KAT BRÜTÜ" **129.77 m²** veriyor (½ ölçekli şema 5.28 × 6.15 → 10.55 × 12.30 m). Bu değer kapalı kısmın dıştan dışa ölçüsü: plandaki kapalı bölüm x 99029–100084 = 10.55 m, teras 7.15 m. HACİM de 129.8 kullanmış. PAFTA A zemin katta terası hariç tutup kapalı poligonu (170.00) almış, D 1. katta terası dahil etmiş. İki kat aynı ölçütle hesaplanmamış.
  Beklenen: `BRÜT ALAN : 129.77 m²`, açık alan (teras) 82.70 m² ayrı satırda (şu anki gibi). Özet JSON ve OKUBENI aynı değere çekilsin. Kaynak olarak "DXF şema KAT BRÜTÜ (D_CK_SEMA)" yazılsın.

- **[H2] Sorumlu: PAFTA** | Dosya: `ERA01_boyama_vaziyet_v01.jpg` (D Blok)
  Sorun: D bloğun kırma çatısı zemin kat brüt izine **ortalanmış** (OKUBENI Yöntem: "saçak poligonu zemin kat brüt izine ortalanarak"). D'de çatı yalnız 1. katın kapalı kısmının (güney, 10.55 m) üstünde. Kuzeydeki 7.15 m 1. kat terası (+3.50). Paftada çatı yaklaşık 3.6 m kuzeye kaymış. Güney ucunda (+170.75 tarafı) "zemin kat izi" tonunda bir şerit kalmış, teras tarafı ise çatıyla örtülmüş. DXF çatı planı `E-F_CATI PLANI`'nda kırma çatı izi (x 101374–102339) bloğun güney ucuna yaslı. HACİM modeli de doğru konumda (1. kat güneyde, teras kuzeyde).
  Beklenen: D çatısı bloğun güney ucuna yaslansın (DXF çatı planı bütün olarak, 17.70 m iz zemin kat iziyle çakıştırılarak yerleştirilsin). Kuzeydeki 7.15 m teras olarak "zemin kat izi / teras" tonunda görünsün. A, B ve C'de ortalama doğru, onlara dokunulmasın.

- **[H3] Sorumlu: HACİM** | Dosya: `ERA01_model_site_v01.skp` (`CATI_KIRMA_A/B/C/D`), `kaynak/era01_model_gen.py` (çatı bölümü), `OKUBENI.md` (Çatılar)
  Sorun: Çatının üst yüzü saçak ucunda saçak kotunun **20 cm üstünde** başlıyor (`zt_e = ze + ROOF_T`, alt yüz = saçak kotu). Bu yüzden eğimler DXF'ten daha yatık çıkmış. DXF 1-1 kesitinde (A) eğimli üst çizgi saçak ucunda +8.20 (181.15), mahyada +8.93 (181.88). Eğim yazısı "%15", hesap 0.73 / 4.85 = %15.
  | Blok | DXF eğimi (kotlardan) | Model |
  |---|---|---|
  | A | %15.0 (yazı %15) | %10.9 |
  | B | %21.0 (yazı %15, bkz. Soru 6) | %18.2 |
  | C | %18.4 (yazı %15) | %14.2 |
  | D | ~%17 | %12.2 |
  Beklenen: Çatı üst yüzü saçak ucunda **saçak kotunda**, mahyada **mahya kotunda** olsun. Bu durumda eğim DXF'le aynı çıkar. Çatı alt yüzü son kat döşemesiyle çakışmamalı. Gerekirse çatı paketi saçakta incelir ya da çatı döşemesi DXF kesitindeki gibi saçak kotunun ~13 cm altına iner. OKUBENI Çatılar tablosu ve "Model kuralı" cümlesi güncellensin.

- **[H4] Sorumlu: HACİM** | Dosya: `ERA01_model_site_v01.skp` (`B_KAT_B2/TAVAN`, `B_KAT_B1/DOSEME_KAPLAMA`), `era01_model_gen.py` (BLOCKS["B"] B2 ceil=None), `OKUBENI.md` (kat tablosu)
  Sorun: B 2. bodrumun tavanı kat kotu + 2.90 = **170.05** varsayılmış, oysa üst kat 3.00 m yukarıda (170.15). Tavan (z 1005–1015 cm), B 1. bodrum döşeme kaplamasıyla (z 1005–1015 cm) **aynı hacmi kaplıyor**. Bu, "elemanlar çakışmaz" kuralına aykırı. Kat yüksekliği 3.00 m ve 60 cm'lik paketle 2.90 m net yükseklik de geometrik olarak mümkün değil.
  Beklenen: B B2 tavan alt kotu **169.55** (net 2.40, DXF'teki 60 cm paket kuralı, D B1'de de böyle). Tavan ve döşeme çakışması kalmasın. OKUBENI tablosu düzeltilsin. Ayrıca A B1 tavanı (173.05) DXF'te yazılı (A 1-1 / A-A kesitleri "+0.10 (173.05)"). OKUBENI'deki "varsayım" notu kaldırılsın.

- **[H5] Sorumlu: HACİM** | Dosya: `ERA01_model_site_v01.skp` (A_KAT_01 KAT_BAHCESI), `OKUBENI.md` madde 12
  Sorun: A 1. kat "KAT BAHÇESİ" kapalı mahal olarak modellenmiş (çatı ve tavan üstünde). proje.md Varsayım 4 açık avlu diyor (kararlaştırıldı). PAFTA da kat bahçesini açık alan olarak (teras tonu, net alana girmeden, 25.00 m²) göstermiş. HACİM ile PAFTA arasında tutarsızlık var.
  Beklenen (v02): Kat bahçesinin üstünde çatı ve tavan boşaltılsın. Döşeme kaplaması teras olarak `DOSEME_KAPLAMA_KURU/DK_TERAS_*` altına alınsın. Kırma çatıda avlu boşluğu açılsın (iç döngü). Avluya bakan duvarlar dış duvar ve cephe kaplaması olsun, doğramalar DXF'teki gibi.

- **[H6] Sorumlu: HACİM** | Dosya: `ERA01_model_site_v01.skp` (B_KAT_B2, ARAZI), `OKUBENI.md` madde 13
  Sorun: B kapalı otoparkın kuzey girişi (+167.15, vaziyette "KAPALI OTOPARK GİRİŞİ") modelde toprak altında kalmış: garaj kapısı ve yarma yok. proje.md Varsayım 3 (v02: basit yarma + garaj kapısı boşluğu) henüz uygulanmamış. PAFTA vaziyetinde ve B 2. bodrum paftasında giriş açık görünüyor.
  Beklenen (v02): Kuzey cephede DXF'teki konumda garaj kapısı boşluğu. 167.15 kotunda, rampa yönünde basit yarma kademesi (az yüzeyli).

- **[H7] Sorumlu: HACİM** | Dosya: `ERA01_model_site_v01.skp` (A_KAT_B1, C_KAT_00 DOSEME_KAPLAMA), `OKUBENI.md` madde 17 ve döşeme kaplaması tablosu
  Sorun: SALON+MUTFAK (A B1, C ZK) `DOSEME_KAPLAMA_ISLAK` altında. proje.md Varsayım 5 kuru grup diyor.
  Beklenen (v02): `DK_SALON_MUTFAK` → `DOSEME_KAPLAMA_KURU`. Aynı kontrolde A B1 "HAVUZ" mahallinin ıslak grupta kalması doğru, bu şekilde kalsın.

---

## UYARI (önerilen)

- **[U1] Sorumlu: PAFTA** | `A-blok-zemin-kat`, `A-blok-kat-planlari`, `D-blok-1-kat`, `D-blok-kat-planlari`
  Tefriş kuralına göre (tefris-kurallari.md "Teras / bahçe: oturma grubu ve/veya dış yemek masası") A zemin TERAS (190.00 m²) ve D 1. kat TERAS (82.70 m²) boş. Mahal yeterli olduğu için PAFTA tamamlayabilir: dış oturma grubu, yemek masası, saksılar. A kat bahçesi ve C balkon tefrişli, bunlarda sorun yok.

- **[U2] Sorumlu: PAFTA** | `A-blok-kat-planlari` (1/200 zemin), `A-blok-zemin-kat`, `A-blok-1-kat`
  Yazı çakışmaları var: üst sıradaki "BANYO 5.00 m²" yazıları duvar ve kapı çizgisinin üstüne biniyor, "TEMİZLİK ODASI" duvara taşıyor, dış "MERDİVEN 4.00 m²" yazısının yarısını kırmızı giriş üçgeni örtüyor. A 1. kat ve A zemin sağ alttaki "BANYO 4.10 m²" diğer mahal yazılarından kalın ve büyük. Yazı boyu ve kalınlığı tek tip olsun, yazılar duvarlardan uzak dursun, giriş üçgeni yazının üstüne binmesin.

- **[U3] Sorumlu: PAFTA** | Toplu paftalar (A 1. bodrum, B 1. bodrum ve zemin, D bodrum ve zemin) ve `D-blok-zemin-kat` (1/100)
  sunum-standardi §2-A (konsept gri) "numara + liste kullanılmaz" diyor. pafta.md ise yazı sığmadığında numara ve liste istiyor. Standartlar çelişiyor, bkz. Kullanıcıya soru 2.

- **[U4] Sorumlu: PAFTA** | Bütün paftalar, sağ üst başlık
  "M İ M A R İ   S U N U M   P R O J E S İ" yazılmış, aşama "SUNUM". DNM01 (referans alınan tarz) ve konsept-sunum-sablonu.md'de "M İ M A R İ   K O N S E P T   P R O J E", aşama "KONSEPT". Kullanıcıya soru 3.

- **[U5] Sorumlu: PAFTA** | `A-blok-zemin-kat` (A2), `B-blok-2-bodrum` (A2), `B-blok-1-bodrum` (A2)
  Set içinde kağıt boyutu karışık (13 A3 + 3 A2). A zemin (20.0 × 18.0 m + peyzaj bandı) ve B 2. bodrum (20.0 × 20.45 m) 1/100'de A3'e sığıyor. Yalnız B 1. bodrum (34.9 m) A3'te sıkışıyor. Ayrıca toplu paftalarda 1/250 (B) ve 1/150 (C) gibi alışılmadık ölçekler var. Öneri: A3 birliği, toplu paftalar 1/200 (B için 1/250 kalabilir). Kullanıcıya soru 4.

- **[U6] Sorumlu: PAFTA** | Toplu paftalar (`*-kat-planlari_v01.jpg`)
  sunum-standardi §2-A: "sayfa sağ altında TOPLAM KAPALI ALAN" yok. Önerilen değerler (H1 düzeltmesiyle): A 362.00 + 170.00 + 170.00 = **702.00 m²**; B 409.00 + 301.68 + 243.44 = **954.12 m²**; C 135.00 + 135.00 = **270.00 m²**; D 112.54 + 217.71 + 129.77 = **460.02 m²**.

- **[U7] Sorumlu: PAFTA** | `ERA01_boyama_vaziyet_v01.jpg`
  DXF vaziyetinde 5 adet "YAYA YOLU" etiketi var (`VAZIYET PLANI / VP_SETLER`, ör. 89692,25933 ve 90271,25794). Kapalı poligon yok ama etiketli şeritler sert zemin tonuna alınabilir. Şu an çim tonunda kalıyorlar (OKUBENI not 7).

- **[U8] Sorumlu: PAFTA** | `A-blok-zemin-kat`, `A-blok-kat-planlari`
  A zemin terası (+1.20) bodrumun üstünde. Kuzey ve doğu-batıda zemin 170.15 (bodrum açık, yaklaşık 4 m kot farkı). Paftada teras çevresi teras kotunda çim bandıyla sarılmış, korkuluk çizgisi yok. Teras kenarına korkuluk çizgisi konsun. Kuzeydeki alçak zemin ayrı tonda verilsin ya da bant yalnız güney ve giriş tarafında kalsın.

- **[U9] Sorumlu: PAFTA** | D paftaları
  Mahal adları "E. BANYO" (D bodrum) ve "E.BANYO" (D zemin, D 1. kat) diye karışık yazılmış (DXF'ten gelen tutarsızlık). Paftalarda tek yazım kullanılsın: "E. BANYO".

- **[U10] Sorumlu: HACİM** | `ARAZI` (era01_model_gen.py arazi bölümü)
  Kademe sınırları 1 m ızgaradan geldiği için testere dişi gibi kırık. Bu hem "az çizgi" ilkesine aykırı hem de render'da gürültülü görünüyor (aksonometrik ve kuş bakışı PNG'leri). Kademe poligonları sadeleştirilsin (ör. shapely `simplify` 50–100 cm + düzgün kenar). Kot uyumu ±0.5 m içinde kalmalı.

- **[U11] Sorumlu: HACİM** | `ERA01_model_site_v01.skp` (Shadow Info / North), `OKUBENI.md` koordinat notu
  Model kuzeyi tanımlanmamış (scriptlerde north/shadow ayarı yok). DXF kuzey sembolü vaziyette 21.29° döndürülmüş, gerçek kuzey vaziyet +Y'sinin yaklaşık 21° batısında (PAFTA paftalarındaki kuzey okları da buna göre). Kullanıcının render gölgeleri için SketchUp North Angle bu yöne ayarlansın. OKUBENI'deki "+Y = kuzey oku yönü" ifadesi düzeltilsin. Sahne adlarındaki yön adları da (KB/GD) yaklaşık.

- **[U12] Sorumlu: HACİM** | `PARAPET_*` (teras korkulukları)
  Teraslarda 100 cm dolu parapet var. DXF'te korkuluk 110 cm (`2_IFC_Handrail`, ör. D 1. kat terası, ince korkuluk). Öneri: 110 cm, ince (5 cm) korkuluk kütlesi ya da cam paneli (`M_DOGRAMA_CAM`). Dolu parapet render'da cepheyi ağırlaştırıyor. Kullanıcıya soru 5.

- **[U13] Sorumlu: HACİM** | `CATI_KIRMA_D`
  D çatısının parapet içi izi modelde 10.15 × 11.90 m, DXF çatı planında (`E-F_CATI PLANI`, 0_IFC_Elevation_1) kırma çatı izi 9.65 × 11.40 m (oluk/dere payı). H3 düzeltilirken bu ölçüye çekilebilir. Küçük fark.

---

## NOT (bilgi, işlem gerekmez)

- **A zemin brüt: 170.00 doğru.** DXF `A_ZK_BRUT ALAN` poligonu 20.00 × 8.50 = 170.00 m². Şemadaki "KAT BRÜTÜ 363.96" **blok konturu** (20.0 × 18.2), 190.00 m²'lik terası da içeriyor. Emsal hesabında teras düşülmüş: 363.96 − 8.97 − 3.96 − 0.20 − 190.00 = 160.83. A 1. kat şeması da 170.00. PAFTA ve HACİM 170.00 kullanmış, doğru.
- **D 1. kat:** Doğru brüt 129.77 (H1). DXF'teki tutarsızlıklar (ÇİZGİ projede yok, kullanıcının bilgisine): `D_K1 BRUT ALAN` etiketi 217.71 (terası içeriyor). D ZK şablonunda "Teras 18.58" yazıyor, plandaki karşılığı "M.K.A. 18.58" (kapalı oda). B çatısında "%15" yazısı kotlarla (177.65 → 179.17, yarım genişlik 7.25 m → %21) uyuşmuyor. A kesitinde "−3.30 (169.95)" yazım hatası var. B GR1 görünüşü A cephesini gösteriyor.
- **Kotlar DXF kesitleriyle uyumlu (HACİM ve PAFTA):** A −2.80/+1.20/+4.70, saçak +8.20, mahya +8.93 (±0.00 = 172.95). B −7.00/−4.00/±0.00, saçak +3.50, mahya +5.02 (174.15). C −4.00/±0.00, +3.50/+4.39 (174.36). D −3.00/±0.00/+3.50, tavanlar −0.60/+2.40/+6.40, saçak +7.00, parapet +7.50, mahya +7.82 (167.25). D yorumu (1. kat +3.50 kuzey terası, kırma çatı +7.00/+7.82) kesitlerle (1-1, A-A) doğrulandı, iki agentta da aynı.
- **Pencereler:** Görünüş kotları örneklem olarak kontrol edildi (A K1 P-06 parapet 103 → 178.68, D ZK üst kasa 169.48, A P-01 174.11–180.37). Model değerleri uyumlu. 280'lik doğramaların döşemeden başlatılması OKUBENI'de belirtilmiş, kabul.
- **Blok yerleşimi:** PAFTA vaziyet dönüşümü ile HACİM grup dönüşümleri aynı vaziyet koordinatına getirildi. A (2137–4137, 2510–3360), C (7338–8088, 1955–3755, 90°) ve D (köşe 8051,4778, uzun kenar 710,1621, 66.35°) 1 cm içinde örtüşüyor. B'de 10 cm y farkı var (önemsiz). Blok sayısı 4, "E-F" blokları D'nin planları. İki agent aynı yorumu yapmış.
- **Kuzey okları:** Paftalardaki kuzey okları DXF kuzey sembolü dönüşleriyle tutarlı (A/B/vaziyet 21.29°, C 291.29°, D 314.94°).
- **Net alanlar:** Bütün katların mahal adları ve alanları DXF `*_ALAN` yazılarıyla karşılaştırıldı, eksik ya da yanlış mahal yok. Net toplamlar DXF toplamlarına eşit (A B1 327.4, A ZK 150.4, A K1 122.8, B B2 376.0, B B1 258.5, B ZK 217.2, C B1 117.8, C ZK 107.1, D B1 97.2, D ZK 191.4). D 1. katta yuvarlanmış toplam 114.20, DXF toplamı 114.33: fark yuvarlamadan, kabul.
- **Ölçek:** 600 dpi'da 1/100 → 2.3622 px/cm, 1/200 → 1.1811, 1/500 → 0.4724. Doğru. Çizgi ölçek, kuzey oku, kot ve bilgi bloğu her paftada var. 16 dosyanın hepsi mevcut (vaziyet + 11 kat + 4 toplu). Tüm blokların tüm katları boyanmış. Çatı planları vaziyette kullanılmış, ayrı pafta yapılmamış (kabul).
- **Font:** PAFTA Calibri yerine metrik eşdeğeri **Carlito** kullanmış (sistemde Calibri yok). Görünüm ve satır uzunlukları aynı. Kullanıcının bilgisine. Ofiste Calibri ile yeniden üretmek gerekirse script hazır. HACİM kontrol PNG'lerindeki başlıklar ASCII ve Calibri değil, ancak bunlar yalnız kontrol amaçlı.
- **Logo:** IFC logosu sol altta (konsept şablonu düzeni). İşveren logosu yok (`00-girdi/logo/` boş).
- **Tefriş:** DXF mobilyası kullanılmış. Örneklemde ölçüler aralıkta: çift kişilik yatak 160×200, 3'lü koltuk 88×240, klozet 36×53, araç yaklaşık 4.5×1.8 m. D'deki tek kişilik yataklar 100×205 (5 cm uzun, kabul). Salonlarda oturma, TV ve yemek işlevleri var (B salon 82 m²: 10 kişilik masa; D 1. kat salon 42 m²: 8 kişilik masa ve TV ünitesi). Eksik yalnız teraslarda (U1). Grafik dil DNM01'e göre daha sade (halı vurgusu, renkli yastık detayı yok), konsept gri standardına uygun.
- **Model standardı:** Grup ve tag hiyerarşisi, bileşenler (46 tanım, 146 örnek), malzeme paleti hacim.md ile aynı. 7 641 yüzey, 608.8 KB: hafif. Döşeme paketi DXF'e göre 60 cm (standart 50). Kullanıcı "modeli kesitlere göre kur" dediği için kabul. Cephe kaplaması dış çizginin 20 cm dışında (proje.md Varsayım 1), uygulanmış. Arazi parsel içinde (Varsayım 6), kademeler blok tesviye kotlarını (164.25, 167.25, 170.15, 170.36, 172.95, 174.15, 174.36) içeriyor. Kontrol noktaları vaziyet kotlarından alınmış, yöntem ±0.5–1 m toleransına uygun. SKP içinden nokta nokta ölçüm yapılamadı, değerlendirme PNG'ler ve üretici verisiyle yapıldı.
- **Dosya adlandırma:** `ERA01_model_*_v01`, `ERA01_boyama_*_v01` ofis kuralına uygun.

---

## Kullanıcıya sorular (önerilen varsayımla)

1. **Paftalarda "BRÜT ALAN" tanımı:** Açık teras ve kat bahçesi hariç, kapalı kat alanı mı? **Öneri:** Evet, kapalı alan (A zemin 170.00, D 1. kat 129.77). Teras ve balkon ayrı "AÇIK ALAN" satırında kalsın.
2. **Konsept gri stilde mahal numarası ve liste:** Kullanılsın mı? **Öneri:** 1/100 tekil paftalarda mahal adı plan içinde kalsın. Yazı sığmayan 1/200–1/250 toplu paftalarda numara ve liste kabul edilsin (sunum-standardi §2-A'ya bu istisna not edilsin).
3. **Pafta başlığı:** "MİMARİ KONSEPT PROJE" mi, "MİMARİ SUNUM PROJESİ" mi? **Öneri:** DNM01 gibi "MİMARİ KONSEPT PROJE", aşama "KONSEPT".
4. **Kağıt boyutu:** **Öneri:** Hepsi A3. A zemin ve B 2. bodrum 1/100 A3'e alınsın, B 1. bodrum A2'de kalsın (ya da A3, 1/125).
5. **Teras korkulukları (model):** **Öneri:** 110 cm ince korkuluk ya da cam kütle, dolu parapet değil.
6. **B çatı eğimi:** DXF'te "%15" yazıyor ama saçak ve mahya kotlarından %21 çıkıyor. **Öneri:** Kotlar esas alınsın (saçak 177.65, mahya 179.17), eğim yazısı yok sayılsın.

---

## Kontrol edilenler
- Kat kotları ve kat yükseklikleri (DXF 1-1 / A-A kesitleri, 4 blok): ✓ (B B2 tavanı hariç, H4)
- Pencere boy ve parapetleri (görünüş örneklemi): ✓
- Çatı biçimi ve kotları: biçim ✓, kotlar ✓, eğim ve üst yüz ✗ (H3)
- D blok çatı yorumu (+3.50 teras, +7.00/+7.82): ✓ HACİM ve PAFTA tutarlı. Vaziyette çatının yeri ✗ (H2)
- Blok yerleşimi ve dönüşleri (HACİM ↔ PAFTA ↔ DXF): ✓
- Arazi, vaziyet kotlarıyla yaklaşık uyum ve kademeli yapı: ✓ (görsel sadeleştirme U10)
- Tüm blokların tüm katları boyalı: ✓ (11 kat + 4 toplu + vaziyet)
- Mahal adları ve net alanlar DXF ile: ✓
- Brüt alan çelişkileri: A zemin 170.00 ✓, D 1. kat ✗ (H1)
- Ölçek, px/cm, kuzey, kot, çizgi ölçek, bilgi bloğu: ✓
- Tefriş ve işlev: ✓, teraslar ✗ (U1)
- A 1. kat KAT BAHÇESİ (açık avlu kararı): PAFTA ✓, HACİM ✗ (H5, v02)
- proje.md varsayımları: 1 ✓, 2 ✓, 3 ✗ (H6), 4 ✗ (H5), 5 ✗ (H7), 6 ✓
- Ofis standartları (model hiyerarşisi, palet, hafiflik, adlandırma, font, logo): ✓ (Carlito notu, U3–U6)
- Referans boyamalara (DNM01, Yavuzselim s07/s08) benzerlik: ✓ genel dil uyumlu (sade tefriş, başlık farkı U4)
