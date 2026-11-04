# Feature Architect — Standart Tespit ve Özellik Mimari Planı Rapor Şablonu

> **Dil Kuralı:** Raporun dili, çalışılan projenin birincil dokümantasyon diline (`PRODUCT.md` / `README.md`) göre otomatik seçilir (Türkçe projede Türkçe, İngilizce projede İngilizce).
> **Kanıt Kuralı:** Tablodaki her satır `gap_scanner.py` çıktısından veya ajanın bizzat açıp doğruladığı dosyadan `dosya:satır` kanıtı taşımak zorundadır.

---

```markdown
# 🧭 [Proje Adı] — Ürün Eksik Analizi ve Özellik Mimari Planı

## 1. Yönetici Özeti ve Proje DNA'sı
- **Proje Amacı (PRD Özeti):** [Projenin temel değer önerisi ve hedef kitlesi]
- **Mevcut Teknoloji & UI Yapısı:** [Frontend, Backend, DB, i18n, UI Kütüphanesi ve Yaşayan Yüzey Modu (Light/Dark)]
- **Genel Tamamlanma Oranı:** [Aktif & Çalışan Rotalar / Toplam Menü & Rota Sayısı — gap_scanner.py verisiyle]
- **Kanıt Tarama Özeti:** `[stub_pages: X | stub_actions: Y | broken_routes: Z | orphan_endpoints: W | orphan_fields: V]`

---

## 2. Kritik Tespitler: Stub Sayfalar, Ölü Kontroller, 404 Rotaları ve Yetim Özellikler

|Kategori | Modül / Sayfa | Rota / Sembol | Mevcut Durum | Kanıt (`dosya:satır` / `i18n_key`) | RBAC (Roller) | Veri & API Hazırlığı |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Stub Sayfa** | [Örn: Raporlar] | `/reports` | Stub ("Geliştirme aşamasında") | `src/pages/Reports.tsx:42` (`reports.underDevelopmentDesc`) | Admin, Yönetici | `[Kısmen Hazır ⚠️]` (API var, filtre yok) |
| **Stub Eylem** | [Örn: Dışa Aktar] | `onExportClick` | Ölü Buton / Toast ("Yakında") | `src/features/Detail.tsx:118` (`export.comingSoon`) | Tüm Roller | `[Yeni API/DB Gerekli 🔴]` |
| **404 Rota** | [Örn: API Ayarları] | `/settings/api` | 404 (Menüde var, rota yok) | `src/components/Sidebar.tsx:84` | Sadece Admin | `[Yeni API/DB Gerekli 🔴]` |
| **Yetim API** | [Örn: Denetim İzi] | `GET /api/v1/audit-logs` | Backend'de hazır, UI'da yok | `AuditController.java:51` | Admin | `[Veri Hazır ✅]` (Sadece UI Gerekli) |
| **Yetim Alan** | [Örn: Son Giriş IP] | `User.lastLoginIp` | Şemada var, ekranda yok | `prisma/schema.prisma:28` | Tüm Roller | `[Veri Hazır ✅]` (Profilde gösterilebilir) |

---

## 3. Çekirdek Modül Denetimi ve 3 Kademeli Geliştirme Önerileri

### A. Profil ve Ayarlar Modülü (`/profile`, `/settings`)
- **Tespit Edilen UX ve Fonksiyon Eksikleri:** [Mevcut sayfadaki eksikler + burada eritilebilecek yetim backend verileri/endpoint'leri]
- **RBAC Görünürlüğü:** [Hangi sekmeler tüm kullanıcılara, hangileri yalnız Admin/Yönetici rollerine açık]
- **Seçenek 1 (Hızlı & Temiz MVP):** [Mevcut API ve verilerle hemen devreye alınacak temiz çözüm]
- **Seçenek 2 (Endüstri Best-Practice):** [Güvenlik/oturum yönetimi, bildirim matrisi, geometry-matched skeleton, empty/error state ve yatay kaydırmasız mobil sekme yapısı]
- **Seçenek 3 (PRD Vizyoner):** [Projenin iş modeline özel akıllı tercihler, aktivite/denetim zaman çizelgesi veya otomasyon kuralları]

### B. Dashboard Modülü (`/dashboard`) ve Skillset Şablon Seçimi
- **Mevcut Dashboard Eksikleri:** [Eksik KPI'lar, rol bazlı stub ekranlar, filtreleme ve aksiyon eksikleri]
- **Skillset'ten Önerilen Dashboard Mimarileri (`.agent/skills/frontend-design/dashboard-theme/catalog.json`):**
  1. **`[dashboard-theme-XX]` — [Şablon Başlığı] (`[archetype]`):** [Neden bu projenin veri yoğunluğuna ve yüzey moduna uygun olduğu + hangi yetim backend verilerini/KPI'ları hangi widget'ta eriteceği]
  2. **`[dashboard-theme-YY]` — [Şablon Başlığı] (`[archetype]`):** [Neden uygun olduğu + hangi operasyonel/analitik akışı hızlandırdığı]
  3. **`[dashboard-theme-ZZ]` — [Şablon Başlığı] (`[archetype]`):** *(Opsiyonel 3. aday)*
- **3 Kademeli İçerik Planı:**
  - **Seçenek 1 (MVP):** [Temel özet KPI kartları ve son aktiviteler]
  - **Seçenek 2 (Best-Practice):** [Mobil uyumlu yatay kaydırmasız tarih/durum filtreleri, karşılaştırmalı grafikler, tam skeleton/empty/error durumları]
  - **Seçenek 3 (PRD Vizyoner):** [Anomali/uyarı kartları, rol bazlı hızlı eylem (quick-action) merkezi ve öngörüsel özetler]

### C. Diğer Stub ve 404 Sayfaları
*(Tespit edilen her ek sayfa/modül için alt başlık açılır: Kanıt + RBAC + Veri Hazırlığı + Seçenek 1 MVP / Seçenek 2 Best-Practice / Seçenek 3 PRD Vizyoner)*

---

## ⚡ 4. Karar ve Başlangıç Onayı (Lütfen Seçiminizi Belirtin)

Uygulamaya ve otomatik `/ui-polish` sürecine geçmem için lütfen aşağıdaki 4 tercihinizi paylaşın:
1. **Öncelik Sırası:** Hangi modül veya sayfalardan başlayalım? *(Örn: Önce Dashboard ve Profil/Ayarlar, ardından diğer stub sayfalar)*
2. **Kademe Seçimi:** Hangi çözüm seviyesini uygulayalım? *(Seçenek 1: MVP / Seçenek 2: Best-Practice / Seçenek 3: PRD Vizyoner)*
3. **Dashboard Şablonu:** Skillset'ten önerilen hangi dashboard mimarisini (`dashboard-theme-XX`) baz alalım?
4. **Veri & API Yaklaşımı:** Backend eksiği (`[Yeni API/DB Gerekli 🔴]`) olan modüllerde **Full-Stack (5 Katman: DB + Backend + API + UI)** olarak mı örelim, yoksa şimdilik tipli servis dikiş noktasıyla **`Mock-UI (YARIM — Eksik Katman HANDOFF'a kaydedilir)`** olarak mı hazırlayalım?
```
