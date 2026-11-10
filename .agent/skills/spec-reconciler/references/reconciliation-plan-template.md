# 📋 Şartname, RFC ve API Eşitleme Planı (Reconciliation Plan)

> **Amaç:** Canlı kod tabanı (Backend & Frontend) ile mevcut RFC, PRD ve `docs/APIs/` dokümanları arasındaki sapmaları (drift) tespit etmek; kullanıcıya her sapma için bağlayıcı karar alanı sunarak doküman ve kod senkronizasyonunu planlamak.

---

## 1. Tarama Özeti ve Metrikler

| Kapsam | Taranan Dizin / Yol | Bulunan Varlık Sayısı |
|---|---|---|
| **Backend Servis / Controller** | `{{BACKEND_PATH}}` | {{BACKEND_COUNT}} endpoint |
| **Frontend İstemci Çağrıları** | `{{FRONTEND_PATH}}` | {{FRONTEND_COUNT}} çağrı |
| **Mevcut API Dokümantasyonu** | `docs/APIs/` | {{DOCS_API_COUNT}} kayıt |
| **Teknik Tasarım Dokümanları** | `docs/rfc/` | {{RFC_COUNT}} doküman |
| **Şartname / Ürün Tanımı** | `PRODUCT.md` / `*-prd.md` | {{PRD_STATUS}} |

---

## 2. Tespit Edilen Sapma ve Çelişki Matrisi

```ascii
[Backend Endpoint] ──?── [Frontend Call] ──?── [docs/APIs/] ──?── [RFC / PRD]
```

### 🔴 Kritik Çelişki #01: [Başlık / Modül]
- **Etkilenen Katman:** `[Backend / Frontend / Doküman]`
- **Canlı Kod Durumu:** `[Kodda uygulanan gerçek davranış ve endpoint/metot]`
- **Dokümantasyon / RFC Tanımı:** `[RFC veya docs/APIs içindeki eski/farklı tanım]`
- **PRD Kuralı:** `[Varsa PRD şartnamesindeki kural]`

#### 🛠️ Eşitleme Seçenekleri
- **[Seçenek A - Koda Uydur]:** Dokümanlar güncel kod gerçekliğine göre revize edilir.
- **[Seçenek B - Şartnameye Uydur]:** Doküman korunur; kodda düzeltme yapmak üzere `SPRINT_PLAN.md`'ye cerrahi görev açılır.

> 💬 **Kullanıcı Kararı / Comment Alanı (Lütfen seçiminizi ve varsa notunuzu buraya yazın):**
> `[Kararınız: Seçenek A mı, Seçenek B mi? Varsa yönlendirme notunuz:]`

---

### 🟡 Uyarı #02: [Başlık / Modül]
...

---

## 3. Onay Sonrası Deterministik İcra Protokolü (Post-Approval 4 Golden Rules)
Kullanıcı bu uzlaşma planını onayladığında (`proceed`, `onay`, `geliştir`, `devam et`), aşağıdaki 4 adım sırasıyla yürütülür:
1. **Plan Dosyasını Arşivleme:** Bu plan dokümanı `docs/plans/reconciliation_plan_<slug>_<YYYYMMDD_HHMMSS>.md` olarak `docs/plans/` altına taşınır ve kalıcılaştırılır.
2. **Doküman-Önce Eşitleme (Docs-Only Sync Gate):** Kod geliştirilmez; yalnızca `docs/APIs/`, `RFCs/` (sonuna `## Uygulama Gerçekliği & Revizyon Notu (As-Built)` eklenerek) ve `PRODUCT.md` dokümanları eşitlenir.
3. **HANDOFF.md Canlı Panosuna Plan Referanslı Maddeleme:** Kod değişiklikleri `HANDOFF.md` §3 canlı panosuna, 1. maddedeki plan dosyası açıkça referans verilerek (`docs/plans/...`) mühürlenir.
4. **Öncelikli Protokol Kalkanı:** Kullanıcı aksini belirtmedikçe ("kodu şimdi yaz" demedikçe), "geliştir" komutu gelse dahi önce 1, 2 ve 3. maddeler icra edilir; ardından kullanıcıya en uygun sıradaki iş önerilir.
