---
description: Proje ya da ofis genelinde token maliyet raporu
argument-hint: [proje-kodu]
---
ŞEF olarak maliyet raporu ver: $ARGUMENTS
- Proje kodu verildiyse `projeler/<KOD>/00-brief/maliyet.md`: agent bazında harcanan, bütçe, kalan; tahmin ile gerçek farkı.
- Verilmediyse `maliyet-gunlugu.md`: agent ve iş türü bazında ortalamalar; en pahalı işler ve öneriler.
Kısa tablo hâlinde ver.
