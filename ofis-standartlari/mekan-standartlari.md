# Mekân Standartları

Proje tipine göre mahal alanları, alana göre olması gereken işlev ve mobilyalar, otopark ve kat ölçüleri.
Kullananlar: ANALİZ (ihtiyaç programı), PROJECİ (plan), GRAFİKER (tefriş), HESAPÇI (alan tablosu), DENETÇİ (kontrol).

**Değer türleri:** İşaretsiz değerler kullanıcının verdiği kesin kurallardır. `(öneri)` işaretliler kullanıcı onayı bekler.
DENETÇİ kesin kurala aykırılığı **HATA**, öneriye aykırılığı **UYARI** sayar.

## 1. Proje tipleri

| Kod | Tip | Örnek |
|---|---|---|
| **V** | Villa / müstakil konut | DNM01, ERA01 |
| **K** | Konut, orta-üst segment (apartman, site) | |
| **S** | Sosyal / toplu konut | |

## 2. Otopark

| | V | K | S |
|---|---|---|---|
| Park yeri | **300 × 600** | 250 × 500 (öneri) | **250 × 500** |
| Manevra yolu (dik park) | 600 (öneri) | 600 (öneri) | 550 (öneri) |
| Rampa eğimi | ≤ %15 (öneri) | ≤ %15 (öneri) | ≤ %15 (öneri) |
| Araç sayısı | Brief'ten; yoksa daire başına 2 (öneri) | Otopark yönetmeliği | Otopark yönetmeliği |

## 3. Kat yükseklikleri ve döşeme

| | V | K | S |
|---|---|---|---|
| Kat yüksekliği (döşeme üstü - döşeme üstü) | 3.50 m | 3.00 m | 3.00 m (öneri) |
| Döşeme paketi | 50 cm (30 + 10 + 10) | 50 cm | 40 cm (öneri) |
| Net iç yükseklik | 3.00 m | 2.50 m | 2.60 m (öneri) |

## 4. Minimum mahal alanları, net m²  (öneri)

| Mahal | V | K | S |
|---|---|---|---|
| Salon (yemek dahil) | 40 | 25 | 18 |
| Mutfak | 15 | 10 | 7 |
| Ebeveyn yatak odası | 18 | 14 | 12 |
| Yatak odası | 12 | 10 | 9 |
| Ebeveyn banyosu | 8 | 5 | — |
| Banyo | 5 | 4.5 | 3.5 |
| WC | 2 | 1.8 | 1.5 |
| Giyinme odası | 6 | — | — |

## 5. Alana göre olması gerekenler

### Salon
| Net alan | Oturma | Yemek | Ek |
|---|---|---|---|
| < 20 m² | 3'lü + 1 tekli (4 kişi) | Yok (mutfakta) | TV ünitesi |
| 20–30 m² | 3'lü + 2 tekli (5 kişi) | 4 kişilik | TV ünitesi |
| 30–45 m² | 3'lü + 2'li + 1 tekli ya da L köşe (6–7 kişi) | 6 kişilik | TV ünitesi |
| 45–60 m² | L / U oturma (7–8 kişi) | 6–8 kişilik | TV + okuma köşesi |
| > 60 m² | İki oturma grubu (8+ kişi) | 8–10 kişilik | TV + şömine ya da bar/okuma köşesi |

Satırlardaki kişi sayıları (öneri); "oturma + TV + yemek" üçlüsünün 25 m² üstünde bulunması kesin kural.

### Diğer mahaller
| Mahal | Koşul | Olması gerekenler |
|---|---|---|
| Mutfak | Açık | Tezgâh (L/U/düz) + eviye + ocak + buzdolabı; ≥ 12 m² ise ada veya kahvaltı masası |
| Mutfak | Kapalı | Tezgâh + eviye + ocak + buzdolabı + (yer varsa) kahvaltı masası |
| Ebeveyn yatak odası | | Çift kişilik yatak 160–180×200 + 2 komodin + gardırop ya da giyinme odası |
| Yatak odası | ≥ 10 m² | Yatak + komodin + gardırop + (yer varsa) çalışma masası |
| Yatak odası | < 10 m² | Tek kişilik yatak 90–100×200 + gardırop |
| Banyo | | Klozet + lavabo + duş (≥ 90×90) ya da küvet |
| Ebeveyn banyosu | | Klozet + tek ya da çift lavabo + duş ve/veya küvet |
| WC | | Klozet + lavabo |
| Çamaşır odası | | Çamaşır makinesi + kurutma + tezgâh/dolap |
| Giriş holü | | Vestiyer / ayakkabılık |
| Teras / bahçe | | Oturma grubu ve/veya dış yemek masası; havuz varsa şezlong |
| Otopark | | Bölüm 2'deki ölçüde araç + manevra alanı |

## 6. Mobilya ölçüleri (kontrol aralıkları, cm)

| Mobilya | Ölçü |
|---|---|
| Çift kişilik yatak | 160×200 – 180×200 |
| Tek kişilik yatak | 90×200 – 100×200 |
| 3'lü koltuk | 210–240 × 85–100 |
| Tekli koltuk | 75–95 × 75–95 |
| Yemek masası 4 / 6 / 8 kişilik | 120–140×80 / 160–200×90–100 / 220–260×95–110 |
| Gardırop derinliği | 60 |
| Mutfak tezgâhı derinliği | 60–65 |
| Klozet | 36–40 × 53–60 (ofis bloğu IFC_KLOZET 36×53.4) |
| Lavabo | 50–80 × 45–55 |

## 7. Geçiş açıklıkları

- Mobilya arası ana geçiş ≥ 80 cm, yatak kenarı ≥ 60 cm.
- Mutfak tezgâh önü ≥ 100 cm, karşılıklı tezgâhta ≥ 120 cm.
- Kapı açılışı mobilyaya ya da başka kapıya çarpmaz.

## 8. Alan tanımları

| Terim | Tanım |
|---|---|
| Net alan | Mahalin duvar içi alanı (`0_IFC_Area` poligonu) |
| Brüt kat alanı | Katın kapalı kısmının dıştan dışa alanı; **açık teras, balkon ve avlu hariç** (ERA01 kararı) |
| Açık alan | Teras, balkon, avlu; ayrı satırda yazılır |
| Toplam kapalı alan | Bütün katların brüt alanları toplamı |

Bir projede farklı tanım istenirse brief'e yazılır.

## 9. Eksik ya da yanlış olduğunda

1. Mahal yeterliyse GRAFİKER tefrişi tamamlar ve raporlar.
2. Mahal yetersizse ya da tasarım kararı gerekiyorsa: ŞEF kullanıcıya **TASARIM sorusu** olarak sorar.
