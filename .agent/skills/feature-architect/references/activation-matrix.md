# Feature Architect v2 — Bağlam-Duyarlı Şapka Aktivasyon Matrisi (`activation-matrix.md`)

`review_units.py` betiği, Canonical Knowledge Graph (`knowledge-graph.json`) içindeki düğümleri mantıksal inceleme birimlerine (`review_units`) ayırır ve her birimde 6 uzmanın rolünü (`lead`, `support`, `skip`) belirler:

| İnceleme Birimi Yüzeyi (`surface`) | `PO` | `ARCH` | `UX` | `SEO` | `GRW` | `QA` |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Halka Açık Web / Landing (`public`)** | `lead` | `support` | `lead` | `lead` | `lead` | `support` |
| **Kimlik Doğrulamalı Uygulama (`authenticated`)** | `lead` | `lead` | `lead` | `skip` | `support` | `lead` |
| **Salt Backend / API / CLI (`internal`)** | `lead` | `lead` | `skip` | `skip` | `skip` | `lead` |

- **`lead`:** Birimi derinlemesine inceler ve birincil bulgu/karar üretir.
- **`support`:** Yalnızca kendi uzmanlık sınırına giren kesişimleri denetler.
- **`skip`:** Birimle ilgisi olmayan şapka zorlama bulgu üretmez (`not_applicable`).
