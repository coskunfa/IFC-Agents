# ERA01 ERA Evi: Detay metrajı v01 (DETAY)

**Tarih:** 2026-11-11 · **Kapsam:** kullanıcının onayladığı 16 kalem, yalnız miktar (poz numarası ve birim fiyat yok) · **Birimler:** m, m², m³, adet. Kotlar m.
**Girdi:** `00-girdi/ERA01_girdi_proje.dxf` (uygulama/ruhsat seti, birim cm). Planlar INSERT içinde; ezdxf `virtual_entities` ile düzleştirildi. "E-F_*" blokları D bloğun planlarıdır.

## Dosyalar
| Dosya | İçerik |
|---|---|
| `ERA01_detay_metraj_v01.xlsx` | Ana çıktı. OZET sayfasında tüm kalemler blok bazında ve genel toplam, ayrıca duvar kalınlığı özeti. Her kalemin ayrı sayfası var (01_DUVAR … 16_MAHAL_LISTESI, KAPI, PENCERE). Destek sayfaları: KAT_PARAMETRELERI, KONTROL, VARSAYIMLAR. Başlık satırları sabit, filtreli, font Calibri. Sarı satırlar varsayım, yaklaşık ya da belirsiz değer içerir |
| `onizleme/ERA01_metraj_duvar_<blok>_<kat>.png` | Duvar sınıflandırmasının kontrol görüntüleri (11 kat). Renkler: açık mavi 10, mavi 15, turuncu 20, kırmızı 25, mor 30, koyu gri 40+ cm kagir duvar; yeşil betonarme; açık yeşil teras kenar bandı; pembe mahal poligonu olmayan kapalı alan (duvar sayılmadı); mavi daire pencere etiketi ucu; kırmızı kare kapı etiketi |
| `kaynak/era01_metraj_0_duzlestir.py` | DXF düzleştirme (PAFTA'nın `era01_dxf_duzlestir.py` kopyası) → `era01_metraj_geo.pkl` |
| `kaynak/era01_metraj_0b_blokreferanslari.py` | İç içe blok referansları. Dinamik (*U) blokların asıl adı da çözülür → `era01_metraj_inserts.pkl` |
| `kaynak/era01_katlar.py` | Kat paftası çerçeveleri ve INSERT adları (PAFTA'dan) |
| `kaynak/era01_metraj_1_katlar.py` | Kat başına ham veri: mahaller, kapalı iz, duvar sınıfları, kolon ve perde, doğrama ve kapı etiketleri, merdiven, korkuluk, armatür → `era01_metraj_katlar.pkl` + önizlemeler |
| `kaynak/era01_metraj_2_hesap.py` | Bütün miktarlar ve varsayım listesi → `era01_metraj_tablolar.json` |
| `kaynak/era01_metraj_3_excel.py` | Excel üretimi |

Yeniden üretmek için `kaynak/` içinde sırayla 0, 0b, 1, 2, 3 numaralı scriptleri çalıştırın. Büyük ara dosyalar (`era01_metraj_geo.pkl` 10.6 MB, `era01_metraj_inserts.pkl`) depoda tutulmadı; 0 ve 0b numaralı scriptler bunları yaklaşık 1 dakikada yeniden üretir. `era01_metraj_katlar.pkl` ve `era01_metraj_tablolar.json` duruyor; Excel adımı yalnız JSON dosyasını okur.

## Yöntem (kalem kalem)
1. **Duvar.** Ölçüm, kat planı 1 cm'lik rastere çizilerek yapıldı. Mürekkep katmanları: 2_IFC_Wall, 3_IFC_Window, 1/2_IFC_Door (yaylar hariç), 1_IFC_Concrete_Section, 0_IFC_Area, 5_IFC_Mechanical_Shaft ve 0_IFC_Brüt_Alan. Dış bölge, raster kenarından dolgu ile bulundu. Kapalı iz = yapı izi − teras, balkon ve avlu mahalleri − teras kenar bandı. Duvar izi = yapı izi − mahaller − şaftlar − betonarme. Bazı duvarlar yalnız mahal poligonları arasındaki boşluk olarak çizili (özellikle D blok). Bu yöntem onları da yakalar.
   - **Kalınlık:** disk çaplı morfolojik açma ile sınıflandı (12.5/17.5/22.5/27.5/35/45 cm eşikleri, 10/15/20/25/30/40/50 cm sınıfları). Köşe ve birleşim kırpıntıları komşu sınıfa katıldı. Dış duvardaki 10 cm'lik doğrama kasa şeritleri baskın dış sınıfa (20 cm) katıldı.
   - **Uzunluk** = sınıfın plan alanı / kalınlık.
   - **Dış/iç ayrımı:** dışa ya da açık mahale "kalınlık + 3 cm"den yakın olan duvar dış duvardır.
   - **Yükseklik:** brüt duvar yüksekliği taşıyıcı döşeme üstünden üst döşeme altına kadardır. Ara katta (kat kotu − 0.10) → (üst kat kotu − 0.40). En alt katta başlangıç radye üstüdür (kat − 0.50, kesit 1-1). Son katta bitiş çatı döşemesi altıdır. Kat bazında değerler KAT_PARAMETRELERI sayfasında.
   - **Boşluk düşümü:** brüt = uzunluk × H, boşluklar dahil. Net = brüt − Σ(genişlik × min(yükseklik, H)). Bu düşüm o kattaki, o sınıftaki kagir duvarda kalan tüm pencere ve kapılar için yapıldı. Betonarmedeki boşluk duvardan düşülmedi.
2. **Duvar yüzeyleri.** Mahal poligonu çevresi × net tavan yüksekliği (2.90 / 2.40 m), mahale açılan boşluklar düşülerek. Islak hacimlerde seramik tavana kadar gider; seramik altı sıva iç sıva satırında sayıldı. Otopark ve teknik hacimlerde sıva yok, yalnız boya var. Dış cephe 11. kalemde.
3. **Zemin.** 0_IFC_Area poligon alanları kullanıldı; DXF'te yazılı alanlarla 0.01 m² içinde tutuyor. Gruplar: ıslak, mutfak, kuru, sirkülasyon, servis, merdiven, otopark, teknik, havuz, açık alan. Malzemeler ofis kütüphanesinden: ZM-01 seramik/granit, ZM-02 lamine parke. Süpürgelik = çevre − kapı genişlikleri − döşemeye inen doğrama genişlikleri.
4. **Kapı.** 77 adet KAPI POZU etiketi okundu (Kxx, gen/yük). A_K1_KAPI POZU bloğu iki kez yerleştirilmiş, tekrarı ayıklandı. Tür ve kanat sayısı kapı bloğundan, açılış yönü kapı yayından (DIN sağ/sol), mahaller en yakın poligonlardan alındı. Bunlara 6 etiketsiz kapı eklendi: 5 iç kapı ve HACİM v02'deki garaj kapısı. Toplam 84 kapı.
5. **Pencere.** 0_IFC_Window_Text etiketlerinden tip, genişlik ve yükseklik okundu. 75 etiket var. P-01 iki katta etiketli; tabloda bir kez sayıldı. A 1. kat avlusundaki etiketsiz 375×280 doğrama eklendi. Sonuç: 75 doğrama, 34 tip.
   - Parapet = (net tavan yüksekliği − 17) − pencere yüksekliği. Bu kural HACİM'in görünüş okumasından alındı.
   - Cam alanı yaklaşıktır (7 cm profil varsayımı).
   - Denizlik: parapetli dış pencereler. Eşik: döşemeye inen dış doğramalar.
6. **Tavan.** Mahal net alanı kullanıldı. Islak hacim ve havuz için asma tavan, otopark ve teknik hacimler için brüt beton üzeri boya, diğer mahaller için alçı sıva + boya alındı.
7. **Betonarme.**
   - Kolon ve perde: 1_IFC_Concrete_Section poligonları. Perde ölçütü L ≥ 6t ya da L/U şekil. Yükseklik = duvar brüt yüksekliği.
   - Döşeme: blok yerel koordinatında "bu katın kapalı izi ∪ üst katın tüm izi" alanı × 30 cm. Çatı döşemesi çatı planındaki döşeme dış izinden alındı (150 cm saçak konsolu dahil).
   - Radye: tüm kat izlerinin birleşimi × kesit kalınlığı (A, C, D 50 cm, B 100 cm).
8. **Çatı.** DXF çatı planları, parapet içinde gizli dereli metal kırma çatı gösteriyor. Ölçüler 0_IFC_Elevation_1/2/3/5 poligonlarından, saçak, mahya ve parapet kotları çatı kot bloklarından alındı.
   - Eğik alan = izdüşüm × √(1 + eğim²). Eğim kotlardan: A %15.1, B %21.0, C %18.4, D %17.0.
   - Saçak/dere = örtü çevresi ("GALVANİZLİ SAC DERE").
   - Mahya = |a − b|. Kırma uzunluğu geometriden hesaplandı.
   - Yağmur iniş adedi bir öneri varsayımıdır.
9. **Merdiven.** 0_IFC_Stair_Text "M: rıht × adet / basamak" yazıları kullanıldı; her merdiven bir kez sayıldı. Kol genişliği basamak çizgilerinden ölçüldü. Kaplama = basamak + rıht + sahanlık.
10. **Korkuluk.** Teras, balkon ve avlu poligonlarının kapalı ize 35 cm'den uzak kenarları teras korkuluğu sayıldı (110 cm cam panel kararı). Merdiven korkuluğu = merdiven mahallindeki 2_IFC_Handrail çizgileri / 2.
11. **Cephe.**
   - Dış çevre, kapalı izin vektöre çevrilmiş sınırından alındı. Zemin üstü katlarda tüm çevre × kat yüksekliği; son katta çatı döşemesi altına kadar.
   - Bodrumda dış çevredeki betonarme perde toprak temaslı sayıldı. Kagir kısım açık cephedir; B 1. bodrum tamamen gömülü.
   - A bodrum perdesinin üst 1.20 m'si subasman olarak ayrı satırda.
   - Çatıda ayrı satırlar: saçak alnı + parapet dış yüzü, parapet iç yüzü, saçak altı.
   - Malzeme: DXF görünüşlerinde yazmıyor, tüm cephe "malzeme belirsiz".
12. **Yalıtım.** Alanlar 1, 7, 8 ve 11. kalemlerden türetildi: dış duvar (mantolama), saçak ve parapet, toprak temaslı perde, radye altı ve yanı, çatı döşemesi, çatı örtüsü altı, teras, bahçe altı döşeme, ıslak hacim (zemin + 30 cm).
13. **Armatür.** 6_IFC_Furniture_WC ve _Wetspace blok referansları dinamik blokların asıl adıyla sayıldı. Her armatüre en yakın mahal atandı.
14. **Hafriyat (yaklaşık).** Doğal zemin, vaziyetteki blok köşe kotlarından en küçük kareler düzlemi olarak alındı. Kazı tabanı = radye altı − 25 cm. Kazı alanı = yapı izi + 1.0 m. Hacim 25 cm'lik ızgarayla hesaplandı. Geri dolgu = 1 m'lik çalışma şeridi.
15. **Peyzaj (yaklaşık).** Vaziyet çizgileri parsel içinde poligonlandı; sınıf, poligon içindeki yazıdan verildi (YAYA YOLU, ARAÇ, DOĞAL EĞİM, tesviye notları). Parsel alanı toplamı 4799.86 m² ile birebir tutuyor. Duvarlar, etiketlerin 6 m yakınındaki çift çizgi şeritleri olarak alındı; yükseklik iki yandaki kot yazılarının farkından. Ayrıca taralı (ANSI31) 30 cm'lik duvar kesitleri ölçüldü: 209 m.
16. **Mahal listesi.** 110 mahal: blok, kat, kot, ad, net alan, DXF'te yazılı alan, zemin/duvar/tavan malzemesi, süpürgelik, tavan yüksekliği, DXF etiket notu.

## Kontroller (KONTROL sayfası)
- **Net mahal alanları** era01_ozet.json ile katta ±0.2 m² içinde tutuyor. Tek fark A zemin katta: −4.10 m². Ozet, bina dışındaki giriş merdivenini (3.96 m²) net alana katmış. Metrajda bu merdiven "dış merdiven" grubunda.
- **Kapalı brüt toplamı** 2348.67 m², referans 2361.18 m². Fark −12.5 m²:
  - C zemin kat şeması (135.00) 13.6 m²'lik balkonu kapalı alana katmış; metrajda kapalı iz 119.69 m².
  - B 2. bodrumda +1.8 m² var; diğer katlarda fark ±0.9 m² içinde (raster toleransı).
  - D 1. kat 129.90 m², DENETÇİ'nin 129.77 tespitiyle tutarlı.
- **Pencere:** 75 doğrama, HACİM v03 de 75. Tip bazında farklar KONTROL sayfasında listeli:
  - HACİM'in okumadığı etiketli pencereler: P-09, P-15, P-19, P-20, P-22.
  - HACİM'in D blok kapılarını (4) ve garajı doğrama sayması; metrajda bunlar KAPI tablosunda.
  - P-01'in iki katta etiketli olması.
  - Tip sayısı 34. İş emrindeki "≈28" HACİM'in okuduğu tiplerdir.

## Varsayımlar ve doğrulanacaklar
Tam ve numaralı liste Excel'in **VARSAYIMLAR** sayfasındadır (41 madde). Öne çıkanlar:
1. **Duvar malzemesi** (gazbeton/tuğla/bims) DXF'te yok, "kagir (malzeme belirsiz)" yazıldı. Kalınlıklar plan çizgilerinden ölçüldü; ±%3 tolerans var.
2. **Döşeme ve radye:** döşeme 30 cm ve 60 cm paket HACİM'den alındı; kiriş çizimde yok. Radye kalınlıkları (A, C, D 50, B 100 cm) kesit kotlarından okundu. Statik proje ile doğrulanmalı.
3. **Malzemeler:** DXF'teki bütün mahal etiketlerinde "DÖŞEME: SERAMİK / TAVAN: BOYA" yazıyor; şablon değeri gibi görünüyor. Kesitlerde ise PARKE ve SERAMİK ayrı yazılı. Yaşam ve yatak mahallerine ofis tercihi ZM-02 parke uygulandı.
4. **A avlusu:** A 1. kat KAT BAHÇESİ açık avlu kabul edildi (karar v02). Çatı planında avlu boşluğu çizili değil.
5. **Çatı eğimi ve inişler:** eğimler kotlardan hesaplandı, DXF'teki "%15" yazıları kullanılmadı. Yağmur iniş adedi bir öneri.
6. **Cephe malzemesi belirsiz.** Bodrumda açık/gömülü bölünme, perde/kagir ayrımına dayanan bir yaklaşım.
7. **Hafriyat ve peyzaj yaklaşık.** Vaziyette sert zemin ve yeşil alan taraması yok. Peyzaj duvarı uzunluk ve yükseklikleri düşük güvenli.
8. **Etiketsiz kapılar** (D mutfaklar, B yatak–salon) ve garaj kapısının ölçüleri. A blokta ayrı dış kapı yok: giriş P-01 camı içinde.
9. **Belirsiz tanımlar:** M.K.A. kısaltması; hamam içindeki 2.3×2.3 m'lik blok; 55×22 cm'lik ıslak hacim bloğu; P-09'un iç cam bölme, P-15'in ışıklık doğraması sayılması.
10. **Hesaplanmayanlar:** mutfak tezgah arası seramik; merdiven ve havuz teknesi betonarmesi; şev, iksa ve arazi genel tesviyesi; B otopark rampası yarması.
