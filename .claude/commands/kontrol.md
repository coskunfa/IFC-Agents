---
description: DENETÇİ ile projeyi kontrol ettirir, hataları ilgili agent'lara düzelttirir
argument-hint: <proje-kodu>
---
ŞEF olarak `projeler/$ARGUMENTS` projesi için kontrol döngüsünü çalıştır:
1. `denetci` agent'ını çalıştır; rapor `05-kontrol/` altına yazılsın.
2. Rapordaki HATA maddelerini sorumlu agent'lara (yalnızca `proje.md`'de aktif olanlara) iş emri olarak gönder.
3. Düzeltmeler bitince DENETÇİ'yi tekrar çalıştır. En fazla 3 tur.
4. Kullanıcıya sonuç: GEÇTİ / kalan hatalar / uyarılar ve rapor yolu.
