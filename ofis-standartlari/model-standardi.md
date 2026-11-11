# Model Standardı (SketchUp)

Ayrıntılı kurallar MODELCİ agent tanımındadır: `.claude/agents/modelci.md`. Bu dosya özetidir.

## Model seviyeleri (kullanıcı onayladı)

| Seviye | İçerik | Ne zaman |
|---|---|---|
| **M1 Kütle** | Kat kütleleri, çatı, arazi; doğrama yok | Fizibilite: imar, yerleşim, gölge |
| **M2 Kütle + Cephe** | Dış duvar, cephe kaplaması, doğrama, çatı, döşemeler | Konsept render (varsayılan) |
| **M3 Render modeli** | M2 + iç duvarlar, mahal mahal döşeme kaplaması, tavan, merdiven | İç mekân ve yakın plan render |

| Arazi | İçerik |
|---|---|
| **A0** | Arazi yok |
| **A1** | Kademeli teraslar (varsayılan) |
| **A2** | Eğimli yüzey, az üçgen, soften/smooth |

## Genel kurallar

- **İlke**: az çizgi, az yüzey, az eleman; kutu mantığı; tekrar eden eleman = bileşen.
- **Birim**: cm. Orijin çizim orijiniyle aynı.
- **Hiyerarşi**: `KAT_xx` → `TASIYICI`, `DIS_DUVAR`, `IC_DUVAR`, `CEPHE_KAPLAMA`, `DOSEME`, `DOSEME_KAPLAMA` (her mahal ayrı; `_ISLAK` / `_KURU`), `TAVAN`, `DOGRAMA`, `MERDIVEN`, `CATI`; ayrıca `ARAZI`.
- **Varsayılan ölçüler**: kat yükseklikleri ve döşeme paketi `mekan-standartlari.md` §3; cephe kaplaması 20 cm, dış duvar çizgisinin dışına.
- **Doğrama**: kutu doğrama, bölme genişliği ≥ 1.00 m, yüksek doğramada kayıt aralığı geniş (3.00 m → 1.50 m), eşit modüler bölme.
- **Renk**: yalnızca gri ve beyaz tonları; her eleman türü farklı ton (palet modelci.md içinde). Konsept malzemesi istenirse brief'te belirtilir.
