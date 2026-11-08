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

## 3. Onay Sonrası İcra Adımları (Next Steps Upon Approval)
1. Kullanıcı yorumları ve kararları doğrultusunda dokümanlar güncellenir.
2. İlgili RFC'lerin sonuna `## Uygulama Gerçekliği & Revizyon Notu (As-Built)` eklenir.
3. Varsa kod refactoring görevleri `HANDOFF.md` §3 canlı panosuna işlenir.
