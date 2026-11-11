# Mimari Ekosistem

Claude Code üzerinde çalışan, 1 koordinatör + 6 uzman agent'tan oluşan mimarlık ofisi sistemi.

| Agent | Görev |
|---|---|
| **ŞEF** | Koordinatör (ana oturum, `CLAUDE.md`) |
| **ÇİZGİ** | Proje çizim (DXF / AutoCAD / Revit) |
| **HACİM** | SketchUp modelleme |
| **PAFTA** | Kat planı ve vaziyet boyama (JPEG / katmanlı PSD) |
| **SUNUM** | Sunum seti, konsept proje sunumu (PDF / PPTX) |
| **DETAY** | Uygulama detayı ve malzeme |
| **DENETÇİ** | Kalite ve tutarlılık kontrolü |

## Kullanım
- `/yeni-proje KAD01 Kadıköy Konut`: proje açar ve brief'i sorar.
- "Bu projede ÇİZGİ ve HACİM'i kullan": aktif agent'ları belirler.
- `/kontrol KAD01`: DENETÇİ kontrolü ve düzeltme döngüsü.
- `/teslim KAD01`: final kontrol ve sunum seti.

Kurulum: `pip install -r araclar/requirements.txt`
