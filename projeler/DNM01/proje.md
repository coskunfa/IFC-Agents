# Proje: Deneme Villa

- **Proje kodu**: DNM01
- **Tür / konum / alan**: Müstakil villa, 2 kat (giriş + 1. kat), dış ölçü 13.60 × 10.10 m (~137 m²/kat)
- **Aşama**: Konsept
- **Aktif agent'lar**: ÇİZGİ, HACİM (+ DENETÇİ)
- **Model detay seviyesi**: KÜTLE + CEPHE (varsayılan)
- **Boyama stili**: (bu aşamada yok)
- **Teslim formatı**: DXF + PDF (çizim), SKP (model)
- **Teslim tarihi**: -

## Brief
Kullanıcının tek çizgi eskiz DXF'inden (00-girdi) konsept kat planları çizilecek; kullanıcı onayından sonra SketchUp modeli kurulacak.

## Girdiler (00-girdi/)
| Dosya | Açıklama |
|---|---|
| DNM01_girdi_eskiz-plan.dxf | Kullanıcı eskizi: giriş kat + 1. kat, dış duvarlar `2_IFC_Wall`, diğerleri katman 0; mahal adları yazılı; kapılar kısa çizgi işaretleri |

## Eskiz okuması
- Giriş kat: merdiven holü, WC, asansör, mutfak (ortada ada), salon (TV'li oturma, oturma, şömine hattı, yemek bölümü), mahaller arası 10 cm duvar.
- 1. kat: 4 yatak odası; merdiven yanında banyo, ortadaki iki odaya birer banyo, ebeveyn banyosu (duş, kapalı WC, jakuzi, çift lavabo) + giyinme odası.
- Eskiz DXF başlığında birim mm görünüyor ama ölçüler cm (basamak 27, duvar 20) → **cm** kabul edildi.

## Varsayımlar

## Kararlar günlüğü
| Tarih | Karar | Kim söyledi |
|---|---|---|
| 2026-11-11 | Proje ÇİZGİ + HACİM ile başlatıldı; çizim onayından sonra model | Kullanıcı |

## Açık konular
