# DNM01 Deneme Villa: Çizim klasörü (ÇİZGİ)

**Seviye:** KONSEPT  ·  **Birim:** cm (kotlar m)  ·  **Orijin:** giriş katı dış duvar sol alt (GB) köşesi = 0,0  ·  **Sayfa üstü kuzey**

## Dosyalar
| Dosya | Sürüm | Durum | Açıklama |
|---|---|---|---|
| `taslak/DNM01_cizim_kat-planlari_v01.dxf` | v01 | TASLAK | AutoCAD 2018 DXF. Bodrum, giriş kat ve 1. kat model alanında alttan üste, aynı X hizasında (kat aralığı 1810 cm) |
| `taslak/DNM01_cizim_kat-planlari_v01.pdf` | v01 | TASLAK | 3 sayfa, A4 yatay, 1/100. Her kat ayrı pafta, bilgi bloğu ve IFC logosu var, çizgi kalınlıkları IFC_CTB'ye göre |
| `taslak/DNM01_cizim_kat-planlari_v01.png` | v01 | TASLAK | Önizleme, 3 kat yan yana, 2500×960 px |
| `kaynak/dnm01_cizim.py`, `kaynak/dnm01_render.py` | v01 | - | v01 üretim betikleri |
| `taslak/DNM01_cizim_kat-planlari_v02.dxf` | v02 | TASLAK | Kullanıcı revizyonu (`00-girdi/DNM01_girdi_kullanici-revizyon_v01r.dxf`) temel alındı. Bodrum, giriş, 1. kat (Y −1810 / 0 / +1810) + **ÇATI PLANI** (Y +3620) + **KESİT A-A** (model X 2700'den başlar, Y = kot cm, ±0.00 = Y 0) |
| `taslak/DNM01_cizim_kat-planlari_v02.pdf` | v02 | TASLAK | 5 sayfa, A4 yatay, 1/100: bodrum, giriş, 1. kat, çatı planı, kesit A-A |
| `taslak/DNM01_cizim_kat-planlari_v02.png` | v02 | TASLAK | Önizleme: üstte 3 kat, altta çatı planı ve kesit |
| `kaynak/dnm01_cizim_v02.py`, `kaynak/dnm01_render_v02.py` | v02 | - | v02 betikleri. Parametrik: pencere parapet/yükseklik (`PENCERE`), kapı yükseklikleri (`KAPI_H`), döşeme paketi, saçak, eğim, kesit hattı en üstte |

Onaylı dosya yok (v02 TASLAK, kullanıcı onayı bekliyor). Kullanıcı onayından sonra `onayli/` klasörüne kopyalanacak (onay tarihi: -).

## v02 değişiklik özeti (kullanıcı revizyonu onaylı, tasarım geri alınmadı)
Kullanıcının AutoCAD'de yaptığı değişiklikler aynen korundu: duvarlar değişmedi; mutfak batı duvarına alındı (L tezgâh, ocak ve eviye batıda), salon yeniden döşendi, **şömine ve "ŞÖMİNE" yazısı kaldırıldı**, 1. katta yatak/dolap yerleri değişti, ebeveyn odasına oturma grubu eklendi, salon yazısı taşındı.
ÇİZGİ düzeltmeleri:
1. Mutfak: dış duvarın **dışına taşan** `*E102` tezgâh (x −20..350, y 470..530, yalnız wipeout) silindi. Kullanıcının çizdiği tezgâh hattı `IFC_MUTFAK TEZGAH` bloklarıyla yeniden kuruldu: hol duvarı önü x 20–300 (kullanıcı ucu 297.3 → 300), batı duvarı y 80–470. Patlatılmış 8 LINE ve `*E103` silindi.
2. Patlatılmış dolaplar (15 LINE + `*E88/*E89/*E90`) tekrar `IFC_WARDROBE` bloğuna çevrildi: yatak 2 batı duvarı 535, yatak 3 doğu duvarı 535, yatak 1 batı duvarı 340 (kullanıcı 342.3 → 340, y 315–655).
3. `6_IFC_Furniture` katmanına eklenmiş 3 kullanıcı bloğu (2 koltuk, lambader) katman `0`'a alındı (ofis kuralı). Lambader bloğundaki bozuk hatch kotu (z = −159658) sıfırlandı, blok içi katmanı `6_IFC_Furniture`.
4. Mahal yazıları: BANYO 2/3 birbirine değiyordu, yatak 1/2/3 ve ebeveyn yazıları yeni dolap/yatakla çakışıyordu; mahal içinde boş alana alındı. Alanlar `0_IFC_Area`'dan yeniden yazıldı (duvar değişmediği için v01 ile aynı).
5. Pencere bloklarına gizli `PARAPET` özniteliği eklendi, `YUKSEKLIK` değerleri güncellendi (aşağıdaki tablo).
6. Kesit A-A hattı giriş kat ve 1. kat planlarına işlendi. Çatı planı ve kesit eklendi.
7. Purge: kullanılmayan bloklar (şömine, eski salon mobilyası, yemek masası, buzdolabı, `IFC_CARPET`, `*U99`, `*E*`) silindi.

## Kat yükseklikleri ve kotlar (HACİM için)
| Kat | Döşeme kotu | Kat yüksekliği | Model alanında Y kaydırması |
|---|---|---|---|
| Bodrum kat | −3.50 | 3.50 m | −1810 |
| Giriş kat | ±0.00 | 3.50 m | 0 |
| 1. kat | +3.50 | 3.50 m | +1810 |
| Çatı döşemesi üstü | +7.00 | - | (çatı planı +3620) |

Döşeme paketi 50 cm: kaplama 10 (üstte) + taşıyıcı 30 + tavan 10 (altta). Net iç yükseklik 3.00 m (her katta tavan = döşeme kotu + 3.00).
| Seviye | Kaplama üstü | Taşıyıcı üst / alt | Alttaki mahalin tavanı |
|---|---|---|---|
| Bodrum tabanı (radye) | −3.50 | −3.60 / −3.90 (temel altı −3.90, VARSAYIM) | - |
| Giriş döşemesi | ±0.00 | −0.10 / −0.40 | −0.50 (bodrum) |
| 1. kat döşemesi | +3.50 | +3.40 / +3.10 | +3.00 (giriş) |
| Çatı döşemesi | +7.00 | +6.90 / +6.60 | +6.50 (1. kat) |
Dış ölçü bütün katlarda 1360 × 1010 cm (dış duvar dış çizgisi). Dış duvar 20, iç duvar 10. Cephe kaplaması 20 cm, dış duvar çizgisinin dışında (bina dış yüzü 1400 × 1050), ±0.00'dan çatı altına. Bodrum tamamen toprak altında, tabii zemin ±0.00 düz.

## Çatı (ÇATI PLANI, HACİM ile ortak)
- 4 yöne kırma çatı, **metal kenet** kaplama, paket ~20 cm. Çatı arası mahal olarak kullanılmaz (çatı döşemesi +7.00 düz, çatı onun üstünde).
- **Saçak 50 cm, cephe kaplaması dış yüzünden** → saçak ucu dış duvar çizgisinden 70 cm dışarıda. Saçak dış çizgisi x −70..1430, y −70..1080 (**1500 × 1150**), çatı izdüşüm alanı 172.50 m².
- **Eğim %15, saçak ucundan başlar.** Mahya doğu-batı yönünde, y = 505, x 505..855 (**350 cm**). Kırma çizgileri saçak köşelerinden mahya uçlarına. Çatı yüksekliği 0.15 × 575 = 86.25 cm.
| Kot | Alt yüzey | Kaplama üstü |
|---|---|---|
| Saçak ucu | **+7.00** (= çatı döşemesi üstü hizası) | **+7.20** |
| Mahya | +7.86 (7.8625) | **+8.06** (8.0625) |
- Yeni katmanlar: `2_IFC_Roof` (ACI 30, 0.30, saçak dış çizgisi / kesitte çatı paketi), `2_IFC_Roof_Line` (ACI 41, 0.20, mahya, kırma, siluet), `2_IFC_Roof_Hidden` (ACI 252, 0.05, HIDDEN, çatı altındaki dış duvar ve kaplama çizgisi).

## Kesit A-A
- Kırık hat, bakış doğuya (kesitte kuzey solda): x = 75 (kuzeyde, merdivenin 1. kolu boyunca) → y = 600'de kırılır → x = 420 (güneyde; mutfak P1 ve yatak 2 P6 penceresi, yatak 2 kapısı). Plan noktaları (75,1240)–(75,600)–(420,600)–(420,−240).
- Kesilen duvar, döşeme, radye ve merdiven `1_IFC_Concrete_Section` + `0_IFC_Hatch_Structure` (solid). Kaplama ve tavan bantları, cephe kaplaması taraması (AR-SAND), toprak (EARTH) ve çatı paketi taraması `0_IFC_Hatch`. Görünen merdiven kolu `1_IFC_Stair`, korkuluk `2_IFC_Handrail`, tabii zemin `7_IFC_Terrain` (yeni, ACI 42, 0.30), kesit hattı `0_IFC_Section_Line` (yeni, ACI 10, 0.25, DASHDOT).
- Merdiven: 24 rıht × 14.58 cm, basamak 27 (2r+g ≈ 56). Kol 1: 9 basamak, 3 balkabağı, kol 2: 11 basamak.
- Konsept seviyesi: kesitin arkasında kalan iç duvar ve kapılar gösterilmedi. Yalnız görünen merdiven kolu ve çatı silueti (mahya üçgeni) var. Kırık hat nedeniyle çatı paketinin kesiti y = 600'de basamak yapıyor (kuzey parça batı kırmasına yakın).

## Mahal ve net alan tablosu (0_IFC_Area poligonlarından)
**Bodrum kat (−3.50)**, brüt 137.36 m²
| Mahal | Net alan (m²) |
|---|---|
| BODRUM / BOŞ MAHAL | 118.51 |
| Merdiven | 7.15 |
| Asansör (kuyu) | 1.80 |
| **Toplam net** | **127.46** |

**Giriş kat (±0.00)**, brüt 137.36 m²
| Mahal | Net alan (m²) |
|---|---|
| SALON | 64.02 |
| MUTFAK | 33.15 |
| GİRİŞ HOLÜ | 16.07 |
| Merdiven | 7.15 |
| WC | 3.08 |
| Asansör (kuyu) | 1.80 |
| **Toplam net** | **125.27** |

**1. kat (+3.50)**, brüt 137.36 m²
| Mahal | Net alan (m²) |
|---|---|
| EBEVEYN YATAK ODASI (giriş nişi dahil) | 22.39 |
| YATAK ODASI 1 | 17.14 |
| YATAK ODASI 3 | 15.24 |
| YATAK ODASI 2 | 14.97 |
| GİYİNME ODASI | 12.96 |
| HOL (koridor dahil) | 11.87 |
| EBEVEYN BANYOSU | 7.85 |
| Ebeveyn banyosu, kapalı WC | 1.50 |
| BANYO 1 (yatak odası 1'e ait) | 3.08 |
| BANYO 2 (yatak odası 2 ensuite) | 3.12 |
| BANYO 3 (yatak odası 3 ensuite) | 3.12 |
| Merdiven boşluğu | 6.84 |
| Asansör (kuyu) | 1.80 |
| **Toplam net** | **121.88** |

**Toplam brüt inşaat alanı:** 3 × 137.36 = **412.08 m²**

## Pencere ve kapı yükseklikleri (VARSAYIM, kullanıcıya soruluyor; betikte `PENCERE` tablosu)

Doğrama bloğu `IFC_PENCERE_<genişlik>`, öznitelikler TİP (görünür), YUKSEKLIK ve PARAPET (gizli, cm). Üst kot her pencerede tavan (+3.00 net).
| Tip | Kat | Mahal | Cephe | Konum (cm) | Genişlik | Parapet | Yükseklik |
|---|---|---|---|---|---|---|---|
| P1 | Giriş | Mutfak | Güney | x 225–465 | 240 | 0 | 300 |
| P2 | Giriş | Salon (yemek) | Güney | x 760–1260 | 500 | 0 | 300 |
| P3 | Giriş | Salon (yemek) | Doğu | y 100–450 | 350 | 0 | 300 |
| P4 | Giriş | Salon (oturma) | Doğu | y 600–900 | 300 | 0 | 300 |
| P5 | 1. kat | Yatak odası 1 | Güney | x 80–230 | 150 | 90 | 210 |
| P6 | 1. kat | Yatak odası 2 | Güney | x 380–560 | 180 | 90 | 210 |
| P7 | 1. kat | Yatak odası 3 | Güney | x 740–920 | 180 | 90 | 210 |
| P8 | 1. kat | Ebeveyn yatak odası | Güney | x 1060–1300 | 240 | 0 | 300 |
| P9 | 1. kat | Hol | Kuzey | x 455–555 | 100 | 150 | 150 |
| P10 | 1. kat | Ebeveyn banyosu | Kuzey | x 705–805 | 100 | 150 | 150 |
| P11 | 1. kat | Giyinme odası | Kuzey | x 1110–1230 | 120 | 150 | 150 |
Kapı yükseklikleri: iç kapılar 220, ana giriş 250, kapısız açıklıklar 220 (VARSAYIM).

Bodrumda pencere yok (boş mahal). Giriş WC, Banyo 1, Banyo 2 ve Banyo 3 iç mahal olduğu için cepheye ulaşmıyor, pencereleri yok.

## Kapılar
Ana giriş 100 (kuzey cephe, x 525–625, `IFC_DOOR_100`). Oda kapıları 90 (`IFC_DOOR_90`). WC ve banyolar 80 (`IFC_DOOR_80`). Asansör kapısı 80. Ebeveyn kapalı WC sürgü kapılı.
Kapısız açıklıklar: mutfak–salon 200 (y 165–365), hol–salon 120 (y 550–670).

## Ölçü uyarıları (v02)
| Yer | Ölçü | Neden | Öneri |
|---|---|---|---|
| Merdiven basamağı (tüm katlar) | 27 cm, üst kol bitişi x = 427 | Eskizden aynen alındı, 5 cm'nin katı değil. Basamak sayısı kullanıcı tarafından kabul edildi | 27 kalsın (kabul) ya da basamak 25/30'a çevrilsin (kol boyu değişir) |

| Mahya kotu | çatı yüksekliği 86.25 cm, mahya +8.0625 | %15 eğim ve 575 cm yarım açıklıktan hesap; plan ölçüsü değil | Kot olarak +8.06 yazıldı; eğim %15 kalsın ya da yuvarlak mahya istenirse eğim ayarlansın (ör. %14.8 → 85 cm) |
| Merdiven rıhtı | 14.58 cm (24 rıht) | 350 / 24 | Kesitte bu değerle çizildi |
| Kullanıcı tefrişi | mobilya ekleme noktaları (ör. ocak 46.5/310.8, eviye 27.7/191.7) | Kullanıcının yerleşimi, ölçü değil | Aynen bırakıldı; yalnız tezgâh ve dolap boyları 5 cm'ye oturtuldu (297.3 → 300, 342.3 → 340) |

Diğer bütün ölçüler 5 cm'nin katı. Eskiz ölçüleri en yakın 5 cm'ye yuvarlandı (kaydırmalar ≤ 2.5 cm), tasarımı bozan bir yer çıkmadı. Asansör kuyusu 120×150 eskizdeki gibi alındı (kullanıcı kabulü).

## Varsayımlar (taslakta uygulandı, onay bekliyor)
1. Duvara dik kısa çizgiler **kapı ortası** kabul edildi. Kapı açılış yönlerini ÇİZGİ seçti.
2. Giriş katında orta duvardaki iki işaret, kullanıcının "mutfak–salon iki geçiş" kararı olarak yorumlandı: mutfak–salon 200 cm, hol–salon 120 cm, ikisi de kapısız.
3. Giriş holünde asansörün yanındaki 60×210 cm orta çizgili kutu **vestiyer dolabı** olarak çizildi.
4. "Şömine hattı": oturma ve yemek bölümleri arasında, salonun ortasında serbest duran 160×40 cm şömine olarak çizildi.
5. Merdiven, eskizde dış duvardan 10 cm içerideydi. Duvara yaslandı, kol genişliği 110 cm oldu. Bodrumdan 1. kata kadar aynı L merdiven üst üste devam ediyor. Giriş katında bodruma iniş, üst kolun ucundan (x≈430) başlıyor.
6. Kolonlar kabaca yerleştirildi: 8 adet 20×40 duvar içi betonarme kolon (4 köşe ve 4 cephe ortası). Statik projeyle netleşecek, iç kolon konmadı.
7. 1. katta ebeveyn yatak odasına, koridor ucundaki bir giriş nişinden giriliyor (eskizdeki çizgiye göre). Ebeveyn banyosuna giyinme odasından giriliyor.
8. Bodrumda yalnız dış duvar, asansör kuyusu duvarları ve merdiven var. Merdivenin açık kenarına korkuluk çizildi.
9. Mobilya IFC bloklarıyla yerleştirildi. Yeni yardımcı bloklar: ada mutfak 240×100, buzdolabı, şömine, TV ünitesi, 8 kişilik yemek masası 240×100, duş 90×90 ve 100×100, asansör kabini.
10. Yeni katman `0_IFC_Dimension` (ACI 3, CTB'de en ince) ölçüler için açıldı, çünkü şablonda ölçü katmanı yok. Asansör kabini `1_IFC_Stair` katmanında.

11. (v02) Bodrum tabanı: radye 30 + kaplama 10, temel altı −3.90. Asansör kuyusu çatı döşemesine kadar boşluk; lift makine/üst boşluk ihtiyacı lift firmasıyla netleşmeli.
12. (v02) Saçak ucu alt yüzü çatı döşemesi üstü hizasında (+7.00) alındı ("eğim saçak ucundan başlar"). Kullanıcının "0,5 cm" saçak yazısı 50 cm yorumlandı.
13. (v02) Pencere ve kapı yükseklikleri ŞEF varsayılanları, kullanıcı onayı bekliyor.

## Tasarım önerileri (karar kullanıcının)
- (v02) Mutfak P1 parapet 0 / h 300, ama güney duvarı önünde 540 cm tezgâh var (x 20–560): tezgâh camın önüne geliyor. Parapet 90–105 ya da tezgâhın P1 önünde kesilmesi düşünülebilir.
- (v02) Yatak 2 ve 3'te dolap duvar boyunca 535 cm. Kapı açılışıyla çakışmıyor (kontrol edildi).
- Giriş WC, Banyo 1, 2 ve 3 penceresiz. Mekanik havalandırma ya da tesisat şaftı gerekir.
- Giriş katı iç duvarları (aks 675 / 535) ile 1. kat iç duvarları (aks 650 / 560) üst üste gelmiyor. 13.6 × 10.1 m açıklıkta iç kolon ya da kiriş gerekecek. Aksların hizalanması statik açıdan kolaylık sağlar.
- Banyo 2 ve 3'ün net ölçüsü 145×215 cm. Kullanılabilir ama dar.
- Merdivende rıht 14.58 cm (24 rıht), basamak 27 cm (2r+g ≈ 56). Konfor için basamak 28–30 cm düşünülebilir.
- Mutfağın tek penceresi güneyde. Mutfak artık batı duvarında olduğu için batı cephesine pencere eklemek tezgâhla çakışır; ışık güneyden ve salondan gelir.
