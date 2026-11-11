# Sunum Standardı

Kaynak: `referans-sunumlar/` klasöründeki örnekler. Yeni örnek geldikçe güncellenir.
`[DOLDURULACAK]` = henüz bilgi yok. `(tahmin)` = görselden çıkarıldı, kullanıcı onayı bekliyor.

---

## 0. Font (kullanıcı kararı)
- Tüm sunum, pafta, diyagram ve tablolarda **tek font: Calibri**. Başlıklar Calibri Bold, gövde Calibri, ince başlıklar Calibri Light.
- Harf aralıklı başlıklar (`M İ M A R İ   K O N S E P T   P R O J E`) Calibri'de karakter aralığı açılarak yapılır.

## 1. Logo kuralı (tüm paftalar)

- Sağ üst köşede logo bloğu; solunda sayfa kenar boşluğundan logoya kadar uzanan **ince yatay çizgi** (koyu gri, ~1 pt).
- Hangi logo kullanılacak:
  - Projenin bir işvereni/markası varsa → **işveren logosu** (veya işveren + IFC birlikte).
  - Yoksa → **IFC logosu**: `ofis-standartlari/logolar/IFC_Architects_logo_gecici.png` (sunumdan kırpıldı; vektör/yüksek çözünürlüklü asıl dosya [DOLDURULACAK]).
- **Konsept proje sunumlarında** (IFC'nin kendi sunumu) düzen farklıdır: IFC logosu sol altta, işveren adı sol üstte yazı olarak. Bkz. `konsept-sunum-sablonu.md`.
- Referans dosyalardaki **Salt Hayat logosu yalnızca o projeye aittir**; başka projede asla kullanılmaz.
  Referansı stil örneği olarak kullan, logoyu ve proje adını taşıma.
- İşveren logosu proje klasöründe `00-girdi/logo/` altında beklenir; yoksa ŞEF kullanıcıya sorar.

---

## 2. Kat planı boyama: iki stil

| Stil | Ne zaman | Referans |
|---|---|---|
| **A: Konsept gri** | Mimari konsept proje sunumu, işverene tasarım sunumu (IFC'nin kendi sunumu) | `Yavuzselim-sayfalar/s07.jpg`, `s08.jpg` |
| **B: Dokulu / pazarlama** | Satış broşürü, pazarlama kataloğu, işveren markalı tip daire/villa sayfası | `ref_kat-plani-boyama_SaltHayat-M1-villa.jpg` |

Kullanıcı stili belirtmezse: konsept sunumda **A**, satış/pazarlama işinde **B**. Emin değilsen ŞEF kullanıcıya sorar.

### 2-A. Konsept gri stil
| Öğe | İşleniş |
|---|---|
| Duvar / kolon | Dolu siyah poşe |
| Tüm iç mahaller | **Düz açık gri** (~#D9D9D9); ıslak hacim/mutfak bir ton koyu gri (~#BDBDBD) olabilir |
| Mobilya | **Beyaz dolgulu, ince gri konturlu** sade üstten mobilya (koltuk, yemek masası, yatak, vitrifiye, mutfak); halı desenli daire vurgu |
| Mahal yazısı | Mahal içinde **BÜYÜK HARF ad** + altında küçük `xx.xx m²` (numara + liste kullanılmaz) |
| Bahçe | Açık yeşil-gri çim (~#DCE5DC), **suluboya ağaç + pembe çiçekli çalı**, gri ahşap/taş teras, şemsiye, şezlong (beyaz) |
| Bodrum çevresi | Toprak/dolgu **orta gri** düz dolgu |
| Otopark | Gri gerçekçi üstten araçlar |
| Giriş | **Kırmızı dolu üçgen** |
| Plan altı | Sağa yaslı `ZEMİN PLANI` / `BRÜT ALAN : 124.50 m²`; sayfa sağ altında `TOPLAM KAPALI ALAN` |

### 2-B. Dokulu / pazarlama stili

Referans: `referans-sunumlar/ref_kat-plani-boyama_SaltHayat-M1-villa.jpg`
Kullanıcı notu: *"Kat planı boyamasının bitmiş hali bunun gibi olmasını bekleriz."*

### Grafik dil: dokulu / fotogerçekçi üstten görünüş (düz renk DEĞİL)
| Öğe | İşleniş |
|---|---|
| Kesilen duvar / kolon | Dolu **siyah** poşe; kolonlar duvar çizgisinden belirgin |
| Yaşam, yatak, koridor, merdiven zemini | Sıcak tonlu **ahşap parke dokusu** (orta-koyu kahve, derzler görünür) |
| Islak hacim (banyo, WC, çamaşır) | Açık gri **mermer/seramik dokusu** |
| Teras, dış döşeme | Açık gri/bej **doğal taş dokusu** |
| Havuz | Açık turkuaz su, ince kenar bordürü |
| Yürüyüş yolu / avlu | Açık taş levha döşeme dokusu |
| Çakıl alanlar | Gri-beyaz **çakıl dokusu** |
| Otopark / yol | Gri granit/küp taş dokusu; bazı yerlerde **balıksırtı** desen |
| Yeşil alan | Yumuşak yeşil çim + **suluboya hissinde** üstten ağaç/çalı kümeleri, gölgeli |
| Mobilya | Gerçekçi üstten görünüş mobilya (koltuk, halı, yemek masası, yatak, mutfak tezgâhı, vitrifiye), saksı bitkileri |
| Araçlar | Gri/beyaz üstten araç görselleri (otopark varsa) |
| Gölge | Duvar ve objelerin altında hafif yumuşak gölge, sayfaya derinlik verir |
| Genel ton | Doğal, yumuşak, düşük kontrastlı; doygun/parlak renk yok |

### Yazı ve işaretler
- Her mahalde **yalnızca mahal numarası** (küçük, ince, koyu gri sans-serif). Mahal adı plan üzerine yazılmaz.
- Plan yanında **mahal listesi**: `No  Mahal adı ........ xx.xx m²`; numara+ad sola, alan sağa hizalı, iki sütun.
  Alanlar 2 ondalık, `m²` üst simge.
- Kat numaralandırması katlar arasında **devam eder** (zemin 1–6, bodrum 7–15 gibi).
- Plan başlığı her planın sağ altında: BÜYÜK HARF, ince sans-serif (örn. `ZEMİN KAT PLANI`).
- Giriş noktaları: içi boş **ince üçgen** ok, plan dışında, girişi gösterir.
- Sayfa altında sağa yaslı: **tip/blok adı** kalın (örn. `M1 TİP VİLLA`) ve altında `BRÜT ALAN  251.00 m²` (rakam kalın, büyük).

### Sayfa
- Dikey (portre) A serisi oranı (1:1.414). Referans: 1414×2000 px. Baskı için A3 dikey (tahmin).
- Beyaz zemin, geniş kenar boşlukları. Bir sayfada birden fazla kat planı kademeli yerleşebilir
  (biri sol üstte, diğeri sağ altta; mahal listeleri boş kalan köşelerde).
- Font: **Calibri** (bkz. §0).

---

## 3. Vaziyet planı boyama

Referans: `referans-sunumlar/ref_vaziyet-plani-boyama_SaltHayat-site.jpg`

### Grafik dil: render tabanlı kuş bakışı
- Zemin görseli: **3D render kuş bakışı** (HACİM modeli + render) ya da fotogerçekçi doku montajı. Yoğun çevre bağlamı
  (orman, arazi) gösterilir; kenarlara doğru **koyu vinyet** ile odak proje alanında kalır.
- Yapılar gri çatılı, gölgeli; havuzlar turkuaz; yollar açık bej/gri; parsel sınırları ince yeşil çit/bitki.

### Etiketler
- Her yapı/parsel üzerinde **blok harfi** (A, B, C1, G1-G2...): koyu renk, sade sans-serif, alt simgeli numara.
- Bina girişleri: küçük **sarı dolu üçgen**.
- Site girişleri: **sarı ok + sarı BÜYÜK HARF yazı** (`SİTE GİRİŞİ`).
- Ortak alanlar beyaz BÜYÜK HARF yazı (örn. `SOSYAL TESİS`).
- **Kuzey oku**: sağ üstte ince beyaz dikey çizgi + üstünde `K`.

### Lejant (sol alt, beyaz)
- Her konut tipi için: tipin **çizgisel ikon** silüeti + tip adı (M1, M2, B1) + `•  alan m²  •  blok listesi`.
  Örn. `M1  ⌂ • 251 m² • A-B-C-D-E-Z-A1-B1-C1`.

### Sayfa
- Dikey (portre) A oranı. Logo sağ üstte, ince çizgiyle (bkz. Logo kuralı); koyu zeminde açık renk logo/yazı.

---

## 4. Şematik diyagram dili
[DOLDURULACAK: referans diyagram bekleniyor]

## 5. Final set (PPTX / PDF)
[DOLDURULACAK: kapak, içindekiler, bölüm sayfası örnekleri bekleniyor]
- Varsayılan: portre A3 PDF; PPTX istenirse aynı sayfa düzeni.
