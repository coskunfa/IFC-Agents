# Brief: [PROJE ADI]

ŞEF bu formu kullanıcıyla doldurur. **★ işaretli maddeler zorunludur; eksikse ilgili agent başlamaz.**
Yalnız seçilen agent'ların bölümleri doldurulur.

## 1. Genel ★
| Madde | Değer |
|---|---|
| ★ Proje kodu / adı | [KOD] / [AD] |
| ★ Proje tipi | V villa · K konut (orta-üst) · S sosyal/toplu konut · diğer: |
| ★ Aşama | A0 Fizibilite · A1 Konsept · A2 Avan · A3 Ruhsat · A4 Uygulama |
| ★ İstenen ürünler | (örn. kat planları, model, boyamalar, sunum, metraj) |
| ★ Aktif agent'lar | (ŞEF önerir, kullanıcı seçer) |
| ★ Teslim formatı | DXF · PDF · SKP · JPEG · PSD · PPTX · XLSX |
| ★ Bütçe (token) | örn. 30 $ |
| Teslim tarihi | |
| Konum, ada-parsel | |
| İşveren | |

## 2. Tasarım girdileri (kullanıcı) ★
| Dosya (`01-girdi/`) | Ne | Not |
|---|---|---|
| | | |

**Kaynak önceliği** ★ (birden fazla kaynak varsa): örn. "Plan ve kotlar DXF'ten; pencere, çatı ve malzeme konsept renderdan."

## 3. Agent bölümleri

### ANALİZ
- ★ Mod: arsa / imar / program
- ★ İmar durumu ya da imar değerleri (TAKS, KAKS, çekmeler, yükseklik) veya belgesi
- ★ (program) Hedef: tip, yaklaşık adet ya da toplam alan
- Alternatif sayısı:

### DAĞITICI
- Ek bir şey gerekmez; girdi listesi yeterli.

### PROJECİ
- ★ Mod: eskiz / altlık
- ★ (eskiz) Plan eskizi ya da DXF, en az bir gerçek ölçü, kat listesi
- ★ (altlık) Kullanıcının detaylı DXF'i; hangi bloklar ve katlar
- Duvar kalınlıkları (yoksa dış 20 / iç 10), pencere yerleri:

### MODELCİ
- ★ Seviye: M1 / M2 / M3 · ★ Arazi: A0 / A1 / A2
- ★ Kat yükseklikleri ya da kesit (yoksa `mekan-standartlari.md` §3)
- ★ Çatı tipi ve kotları (ya da kesit/görünüş)
- ★ (M2, M3) Pencere ölçüleri ve parapetleri (ya da görünüş)
- ★ (A1, A2) Halihazır / kot verisi
- Malzeme: gri palet (varsayılan) / konsept malzemesi:

### GRAFİKER
- ★ Boyanacak katlar ve vaziyet
- ★ Stil: konsept gri / dokulu
- ★ Brüt alan tanımı: standart (teras, balkon, avlu hariç) / farklı:
- İşveren logosu, peyzaj tercihi:

### HESAPÇI
- ★ Mod: genel / alan / kaba / detay
- ★ (kaba) Kalem listesi, boşluk düşümü, duvar yüksekliği tanımı
- ★ Hangi sürüme göre: çizim / konsept model
- Poz ve birim fiyat: yok / var

### SUNUM
- ★ Amaç ve aşama (örn. işveren konsept sunumu)
- ★ İşveren adı, proje tarihi
- ★ Konsept metni ya da anahtar fikirler
- ★ Görsel listesi (render, eskiz)
- Çıktı: PPTX / PSD / PDF

### DENETÇİ
- Mod: yok (varsayılan) / hızlı / tam
