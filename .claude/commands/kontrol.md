---
description: DENETÇİ ile kontrol (hızlı ya da tam), hataları ilgili agent'lara düzelttirir
argument-hint: <proje-kodu> [hızlı|tam]
---
ŞEF olarak `projeler/$ARGUMENTS` için kontrol (mod verilmediyse hızlı):
1. Tahmini maliyeti söyle ve onay al (DENETÇİ yalnız kullanıcı isterse çalışır).
2. `denetci` agent'ını ilgili modda çalıştır; rapor `08-kontrol/`.
3. HATA maddelerini sorumlu agent'lara (yalnız brief'te aktif olanlara) iş emri olarak gönder. TASARIM kararı gerektirenleri kullanıcıya sor.
4. Düzeltmeden sonra yalnız ilgili maddeleri hızlı modda yeniden kontrol ettir. En fazla 2 tur.
5. Sonuç, kalan hatalar, rapor yolu, harcanan maliyet.
