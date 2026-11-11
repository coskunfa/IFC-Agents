# DNM01 Deneme Villa: Çizim klasörü (ÇİZGİ)

**Seviye:** KONSEPT  ·  **Birim:** cm (kotlar m)  ·  **Orijin:** giriş katı dış duvar sol alt (GB) köşesi = 0,0  ·  **Sayfa üstü kuzey**

## Dosyalar
| Dosya | Sürüm | Durum | Açıklama |
|---|---|---|---|
| `taslak/DNM01_cizim_kat-planlari_v01.dxf` | v01 | TASLAK | AutoCAD 2018 DXF. Bodrum, giriş kat ve 1. kat model alanında alttan üste, aynı X hizasında (kat aralığı 1810 cm) |
| `taslak/DNM01_cizim_kat-planlari_v01.pdf` | v01 | TASLAK | 3 sayfa, A4 yatay, 1/100. Her kat ayrı pafta, bilgi bloğu ve IFC logosu var, çizgi kalınlıkları IFC_CTB'ye göre |
| `taslak/DNM01_cizim_kat-planlari_v01.png` | v01 | TASLAK | Önizleme, 3 kat yan yana, 2500×960 px |
| `kaynak/dnm01_cizim.py`, `kaynak/dnm01_render.py` | v01 | - | Üretim betikleri (v02 revizyonu için) |

Onaylı dosya yok. Kullanıcı onayından sonra `onayli/` klasörüne kopyalanacak (onay tarihi: -).

## Kat yükseklikleri ve kotlar (HACİM için)
| Kat | Döşeme kotu | Kat yüksekliği | Model alanında Y kaydırması |
|---|---|---|---|
| Bodrum kat | −3.50 | 3.50 m | −1810 |
| Giriş kat | ±0.00 | 3.50 m | 0 |
| 1. kat | +3.50 | 3.50 m | +1810 |
| Çatı başlangıcı | +7.00 | - | - |

**Çatı (HACİM'e not):** Çatı katı yok. 1. katın üstünde **4 kırma çatı** var (dört yöne eğimli kırma çatı). Çatı planı çizilmedi; eğim, saçak ve mahya kotu kullanıcıdan alınacak.
Dış ölçü bütün katlarda 1360 × 1010 cm. Dış duvar 20 cm, iç duvar 10 cm. Döşeme kalınlığı gösterilmedi.

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

## Pencereler (eskizde yoktu, ÇİZGİ yerleştirdi; kullanıcı değiştirebilir)
Doğrama bloğu `IFC_PENCERE_<genişlik>`, öznitelikler TİP (görünür) ve YUKSEKLIK (gizli, doğrama yüksekliği cm, konsept değeri).
| Tip | Kat | Mahal | Cephe | Konum (cm) | Genişlik | Yükseklik |
|---|---|---|---|---|---|---|
| P1 | Giriş | Mutfak (eviye önü) | Güney | x 225–465 | 240 | 120 |
| P2 | Giriş | Salon (yemek) | Güney | x 760–1260 | 500 | 250 |
| P3 | Giriş | Salon (yemek/şömine) | Doğu | y 100–450 | 350 | 250 |
| P4 | Giriş | Salon (oturma) | Doğu | y 600–900 | 300 | 250 |
| P5 | 1. kat | Yatak odası 1 | Güney | x 80–230 | 150 | 150 |
| P6 | 1. kat | Yatak odası 2 | Güney | x 380–560 | 180 | 150 |
| P7 | 1. kat | Yatak odası 3 | Güney | x 740–920 | 180 | 150 |
| P8 | 1. kat | Ebeveyn yatak odası | Güney | x 1060–1300 | 240 | 220 |
| P9 | 1. kat | Hol (ek, ışık için) | Kuzey | x 455–555 | 100 | 150 |
| P10 | 1. kat | Ebeveyn banyosu (jakuzi üstü) | Kuzey | x 705–805 | 100 | 60 |
| P11 | 1. kat | Giyinme odası | Kuzey | x 1110–1230 | 120 | 120 |

Bodrumda pencere yok (boş mahal). Giriş WC, Banyo 1, Banyo 2 ve Banyo 3 iç mahal olduğu için cepheye ulaşmıyor, pencereleri yok.

## Kapılar
Ana giriş 100 (kuzey cephe, x 525–625, `IFC_DOOR_100`). Oda kapıları 90 (`IFC_DOOR_90`). WC ve banyolar 80 (`IFC_DOOR_80`). Asansör kapısı 80. Ebeveyn kapalı WC sürgü kapılı.
Kapısız açıklıklar: mutfak–salon 200 (y 165–365), hol–salon 120 (y 550–670).

## Ölçü uyarıları
| Yer | Ölçü | Neden | Öneri |
|---|---|---|---|
| Merdiven basamağı (tüm katlar) | 27 cm, üst kol bitişi x = 427 | Eskizden aynen alındı, 5 cm'nin katı değil. Basamak sayısı kullanıcı tarafından kabul edildi | 27 kalsın (kabul) ya da basamak 25/30'a çevrilsin (kol boyu değişir) |

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

## Tasarım önerileri (karar kullanıcının)
- Giriş WC, Banyo 1, 2 ve 3 penceresiz. Mekanik havalandırma ya da tesisat şaftı gerekir.
- Giriş katı iç duvarları (aks 675 / 535) ile 1. kat iç duvarları (aks 650 / 560) üst üste gelmiyor. 13.6 × 10.1 m açıklıkta iç kolon ya da kiriş gerekecek. Aksların hizalanması statik açıdan kolaylık sağlar.
- Banyo 2 ve 3'ün net ölçüsü 145×215 cm. Kullanılabilir ama dar.
- Merdivende rıht yaklaşık 15 cm, basamak 27 cm (2r+g ≈ 57). Konfor için basamak 28–30 cm düşünülebilir.
- Mutfağın tek penceresi güneyde. Batı cephesine ikinci bir pencere eklenebilir.
