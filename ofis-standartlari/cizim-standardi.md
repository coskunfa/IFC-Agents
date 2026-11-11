# Çizim Standardı (AutoCAD / DXF)

Kaynak: `referans-sunumlar/ref_kat-plani-cizimi_IFC-ornek.dxf` (AutoCAD 2018 formatı, önizleme `..._onizleme.png`).
ÇİZGİ ve DETAY yeni çizime başlarken **bu dosyanın katman, yazı stili, ölçü stili ve blok tanımlarını şablon olarak kullanır**
(ezdxf ile dosyayı açıp model alanını boşaltarak, ya da tabloları kopyalayarak). Böylece katman renkleri ve stiller birebir aynı olur.

## Birim ve yerleşim
- Birim: **cm** (90'lık kapı bloğu = 90 birim). Kotlar metre (±0.00).
- Katlar model alanında **alt alta** dizilir (alttan üste: B1, ZEMİN, 1. KAT...). Katlar arasında boşluk bırakılır, aynı X hizasında.
- Her katın sağ altında kat adı: `ZEMİN KAT`, `1.KAT`, `B1 KAT` (MTEXT, katman `0_IFC_Stair_Text`, yükseklik 56.25).
- Halihazır/imar haritası katmanları (`B_*`, `Y_*`, `S_*`, `EĞRİ_*`, `SINIR_*`, `N_*`, `HID_*`, `HAT_*`) haritadan gelir; **değiştirilmez**, vaziyet planında altlık olarak kalır.

## IFC katman sistemi
Ad kuralı: `<grup no>_IFC_<Eleman>`. Grup numarası elemanın türünü gösterir.

| Katman | Renk (ACI) | İçerik |
|---|---|---|
| `0_IFC_Hatch` | 250 | Genel tarama |
| `0_IFC_Hatch_Structure` | 251 | Taşıyıcı (betonarme) tarama/dolgu |
| `0_IFC_Area` | 100 | Mahal alan sınırı poligonları (alan hesabı için) |
| `0_IFC_Room_Text(No)_50` / `_100` | 12 | Mahal adı / no / alan yazısı (1/50, 1/100) |
| `0_IFC_Text_Explanation_50` / `_100` | 231 | Açıklama yazıları |
| `0_IFC_Stair_Text` | 221 | Merdiven yazısı, kat başlıkları |
| `0_IFC_Window_Text` | 60 | Doğrama etiketleri (blok öznitelikleri) |
| `0_IFC_Elevation_5` | 252 | Kot işaretleri |
| `1_IFC_Concrete_Section` | 50 | Kesilen betonarme (kolon, perde) |
| `1_IFC_Stair` | 210 | Merdiven (çizgi kalınlığı 0.13) |
| `1_IFC_Stair_Concrete` | 252 | Merdiven betonu (gizli çizgi) |
| `1_IFC_Door` | 83 | Kapı |
| `2_IFC_Wall` | 130 | Duvarlar |
| `2_IFC_Door` | 83 | Kapı (duvar grubu) |
| `2_IFC_Handrail` | 181 | Korkuluk / küpeşte |
| `3_IFC_Window` | 136 | Pencere / doğrama |
| `6_IFC_Furniture` | 35 | Mobilya |
| `6_IFC_Furniture_WC` | 64 | Vitrifiye |
| `6_IFC_Furniture_Wetspace` | 64 | Islak hacim donatısı |
| `6_IFC_Furniture_MKA` | 35 | Alternatif mobilya (dondurulmuş) |
| `6_IFC_People` | 35 | İnsan figürleri |
| `6_IFC_Car` | 253 | Araçlar |
| `7_IFC_Tree` | 88 | Ağaç / peyzaj |

- Çizgi kalınlıkları katmanda **Default**; baskı kalınlığı renk üzerinden **plot style** ile verilir: `ofis-standartlari/cad/IFC_CTB.ctb`.
- CTB'de tüm renkler **nesne rengiyle** basılır (siyaha zorlanmaz), screen %100, çizgi tipi nesneden alınır.
- Yeni katman ya da renk seçerken çizgi kalınlığı aşağıdaki CTB eşlemesine göre seçilir:

| ACI | Baskı kalınlığı | Kullanıldığı katman |
|---|---|---|
| 50 | **0.40** | `1_IFC_Concrete_Section` (kesilen betonarme) |
| 130 | **0.30** | `2_IFC_Wall` |
| 251 | 0.18 | `0_IFC_Hatch_Structure` |
| 210, 221 | 0.15 | `1_IFC_Stair`, `0_IFC_Stair_Text` |
| 12, 60, 83, 88, 136, 231, 250, 253 | 0.10 | mahal yazısı, doğrama yazısı, kapı, ağaç, pencere, açıklama, tarama, araç |
| 35, 64, 181 | 0.09 | mobilya, vitrifiye, korkuluk |
| 100, 252 | 0.05 | alan poligonu, kot / gizli merdiven |
| 1, 3–7 | 0 (en ince) | genel |

Diğer kalın renkler: 0.30 → 22, 23, 30, 42, 54, 61, 75, 80, 89, 92, 110, 120, 133, 137, 140, 142, 150, 165, 173, 192, 193, 214, 232, 236, 244; 0.25 → 10; 0.20 → 41.
- Bloklar katman `0` üzerinde eklenir; blok içindeki elemanlar kendi IFC katmanlarındadır.

## Yazı ve ölçü stilleri
Not: Sunumlarda font Calibri'dir; **AutoCAD çizimlerinde ofis stilleri korunur** (kullanıcı kararı).

| Stil | Font | Kullanım |
|---|---|---|
| `IFC_TEXT` | Arial Narrow (ARIALN.TTF) | Genel yazılar |
| `IFC_TEXT_DIM` | romans.shx | Ölçü yazıları |

| Ölçü stili | Yazı/ok boyu | Ölçek |
|---|---|---|
| `IFC_Dim50` | 10 | 1/50 |
| `IFC_Dim100` | 20 | 1/100 |
| `IFC_Dim200` | 40 | 1/200 |
| `IFC_Dim200_2` | yazı 80, ok yok | 1/200 büyük yazı |
Ok tipi: eğik çizgi (`_Oblique`). Yazı boyu = 2 mm × ölçek.

## Blok kütüphanesi (örnek dosyada mevcut)
`IFC_DOOR_90`, `IFC_SURGU KAPI_80`, `BALKON KAPI_90`, `IFC_KLOZET`, `IFC_VITRA_DOLAPLI LAVABO_53X60`, `IFC_EVYE_1.5`,
`IFC_KOLTUK 3LU`, `IFC_KOLTUK TEKLI`, `IFC_COFFE TABLE`, `IFC_BAR TABURESI`, `IFC_SAKSI`, `IFC_TREE2`, `IFC_SAND2`, `ARABA_2`, `YK_140` ...
- Pencereler **dinamik blok**, öznitelikleri: `TİP` (örn. `P-`), `YUKSEKLIK` (örn. `250`).
- Yeni çizimde önce bu bloklar kullanılır; yoksa aynı katman mantığıyla yeni blok üretilir.

## Vaziyet altlığı
- Tercih edilen: kullanıcının verdiği halihazır harita / aplikasyon DWG-DXF'i.
- **Bazen yalnızca PDF gelir.** Bu durumda ÇİZGİ PDF'i (vektörse vektörden, değilse görüntüden) bilinen bir ölçüyle (parsel kenarı, ölçek çubuğu, imar durumundaki ölçü) ölçekleyerek altlık DXF'i çıkarır. Ölçek referansını ve tahmini hata payını `01-cizim/OKUBENI.md` ve `proje.md` → Varsayımlar bölümüne yazar. DENETÇİ bu altlığı "doğrulanmalı" olarak işaretler.

## Zorunlu içerik
Duvar, kolon/perde, doğrama, merdiven (yön oku), mahal adı ve alanı, kat başlığı, kotlar, ana ölçü zincirleri.
Vaziyette ayrıca kuzey oku, cadde adları, parsel sınırı, bloklar arası mesafeler.
