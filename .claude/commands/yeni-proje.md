---
description: Yeni proje klasörü açar, brief'i doldurur, iş programını onaya sunar
argument-hint: <proje-kodu> <proje adı>
---
ŞEF olarak yeni proje başlat: $ARGUMENTS

1. `projeler/_sablon/` klasörünü `projeler/<KOD>_<ad-kisa>/` olarak kopyala; `00-brief/` dosyalarına kodu ve adı yaz.
2. Kullanıcıdan dosyalarını `01-girdi/` klasörüne koymasını iste.
3. Kullanıcıya tek mesajda sor: proje tipi (V/K/S), aşama (A0-A4), istenen ürünler, bütçe. Ürünlere göre **agent öner**; kullanıcı seçsin.
4. Yalnız seçilen agent'ların ★ zorunlu maddelerini `brief.md`'den sor; eksik zorunlu madde varsa listele.
5. `is-programi.md`'yi yaz (adımlar, tarih, tahmini maliyet, her agent için kısa görev tanımı) ve onaya sun. Kilometre taşlarını `ofis-takvimi.md`'ye ekle.
6. Onay gelince ilk adımla (genelde DAĞITICI) başla.
