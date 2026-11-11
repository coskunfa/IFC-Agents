# Model Standardı (SketchUp)

Ayrıntılı kurallar HACİM agent tanımındadır: `.claude/agents/hacim.md`. Bu dosya özetidir.

- **İlke**: az çizgi, az yüzey, az eleman; kutu mantığı; tekrar eden eleman = bileşen.
- **Birim**: cm. Orijin çizim orijiniyle aynı.
- **Hiyerarşi**: `KAT_xx` → `TASIYICI`, `DIS_DUVAR`, `IC_DUVAR`, `CEPHE_KAPLAMA`, `DOSEME`, `DOSEME_KAPLAMA` (her mahal ayrı; `_ISLAK` / `_KURU`), `TAVAN`, `DOGRAMA`, `MERDIVEN`, `CATI`; ayrıca `ARAZI`.
- **Varsayılan ölçüler**:
  - Villa kat yüksekliği 3.50 m, apartman 3.00 m
  - Döşeme 50 cm, döşeme kaplaması 10 cm, tavan 10 cm
  - Cephe kaplaması 20 cm
- **Doğrama**: kutu doğrama, bölme genişliği ≥ 1.00 m, yüksek doğramada kayıt aralığı geniş (3.00 m → 1.50 m), eşit modüler bölme.
- **Arazi**: kademeli ya da az üçgenli yumuşatılmış yüzey; model şişirilmez.
- **Renk**: yalnızca gri ve beyaz tonları; her eleman türü farklı ton (palet hacim.md içinde).
- **Detay seviyesi**: varsayılan KÜTLE + CEPHE.
