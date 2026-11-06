# Feature Architect — Standart Tespit ve Özellik Mimari Planı Rapor Şablonu

> **Dil Kuralı:** Raporun dili, çalışılan projenin birincil dokümantasyon diline (`PRODUCT.md` / `README.md`) göre otomatik seçilir (Türkçe projede Türkçe, İngilizce projede İngilizce).
> **Kanıt Kuralı:** Tablodaki her satır `gap_scanner.py` çıktısından veya ajanın bizzat açıp doğruladığı dosyadan `dosya:satır` kanıtı taşımak zorundadır.
> **Çift Yönlü Kalıcılık (Dual-Persistence Zorunluluğu):** Bu rapor hem Antigravity IDE arayüzünde görüntülenebilmesi için `<artifact-dir>/feature-architect-report.md` artifact'ı olarak üretilir, **HEM DE** projenin Git reposunda kalıcı olarak saklanması için `docs/plans/feature-architect-report.md` (veya `.agent/plans/`) yoluna eşzamanlı olarak yazılır.

---

```markdown
# 🧭 [Proje Adı] — Ürün Eksik Analizi ve Özellik Mimari Planı

> **Hedef Dal / Sürüm:** `[örn. main / v1.2.0]` · **Tarih:** `[YYYY-MM-DD]`  
> **Denetçi / Görevli:** Kıdemli Ürün Yöneticisi (PM), UX Mimarı & Full-Stack Başmühendis  
> **Görevlendirilen Skill'ler:** `feature-architect`, `doc-coauthoring`, `council`, `tdd`, `ui-polish`, `frontend-design`  
> **Kullanılan MCP'ler:** `context7`, `myFilesystem` (veya "kullanılmadı")  
> **Kalıcı Plan Konumu:** `docs/plans/feature-architect-report.md` & `<artifact-dir>/feature-architect-report.md`  

---

## 1. Yönetici Özeti ve Proje DNA'sı
- **Proje Amacı (PRD Özeti):** [Projenin temel değer önerisi ve hedef kitlesi]
- **Mevcut Teknoloji & UI Yapısı:** [Frontend, Backend, DB, i18n, UI Kütüphanesi ve Yaşayan Yüzey Modu (Light/Dark)]
- **Genel Tamamlanma Oranı:** [Aktif & Çalışan Rotalar / Toplam Menü & Rota Sayısı — gap_scanner.py verisiyle]
- **Kanıt Tarama Özeti:** `[stub_pages: X | stub_actions: Y | broken_routes: Z | orphan_endpoints: W | orphan_fields: V]`

---

## 2. Kritik Tespitler: Stub Sayfalar, Ölü Kontroller, 404 Rotaları ve Yetim Özellikler

| Kategori | Modül / Sayfa | Rota / Sembol | Mevcut Durum | Kanıt (`dosya:satır` / `i18n_key`) | RBAC (Roller) | Veri & API Hazırlığı |
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

### B. Dashboard Modülü (`/dashboard`) ve Analitik Paneli
- **Mevcut Dashboard Eksikleri:** [Eksik KPI'lar, rol bazlı stub ekranlar, filtreleme ve aksiyon eksikleri]
- **Seçenek 1 (MVP):** [Temel özet KPI kartları ve son aktiviteler]
- **Seçenek 2 (Best-Practice):** [Mobil uyumlu yatay kaydırmasız tarih/durum filtreleri, karşılaştırmalı grafikler, tam skeleton/empty/error durumları]
- **Seçenek 3 (PRD Vizyoner):** [Anomali/uyarı kartları, rol bazlı hızlı eylem (quick-action) merkezi ve öngörüsel özetler]

### C. Diğer Stub ve 404 Sayfaları
*(Tespit edilen her ek sayfa/modül için alt başlık: Kanıt + RBAC + Veri Hazırlığı + Seçenek 1 / Seçenek 2 / Seçenek 3)*

---

## 4. 🏛️ Council Deliberation & Alternatif Yaklaşımlar (Borda Puanı)
> [!NOTE]
> Modüller için önerilen kademeler ve mimari alternatifler `council` standartlarına göre kör hakemlik ve Borda skoru ile analiz edilmiştir:

| Seçenek / Kademe | Yaklaşım & Kapsam | Avantajlar (+) | Riskler / Dezavantajlar (-) | Borda Puanı |
|---|---|---|---|:---:|
| **Option A (Seçenek 1 - Yalın MVP)** | Mevcut API/DB ile hızlı, sıfır-slop yalın ekranlar. | [Hızlı teslim, sıfır DB riski] | [İleri seviye analitik ve otomasyon eksik kalır] | [örn. 2.1] |
| **Option B (Seçenek 2 - Best-Practice)** | Tam skeleton UI, güvenlik sekmeleri, gelişmiş filtreler (Önerilen). | [Kusursuz UX, kurumsal SaaS standartları] | [Bir miktar daha fazla bileşen kodu] | [örn. 2.8] |
| **Option C (Seçenek 3 - PRD Vizyoner)** | Akıllı öngörüsel kartlar, anomali tespiti, otomasyon. | [Maksimum rekabet avantajı, derinlik] | [Ek backend/algoritma geliştirme ihtiyacı] | [örn. 1.6] |

- **Önerilen Yol & Gerekçe:** [Council değerlendirmesi sonucu öne çıkan seçenek ve gerekçesi]

---

## 5. 🎨 Birleşik Tema ve Bileşen İskeleti Sözleşmesi (`ui-polish` & `theme-skeleton-matching`)
> ⛔ **SIFIR AI-SLOP KURALI:** Ezbere bileşen veya keyfi renk yazmak yasaktır; CLI araçlarıyla doğrulanmış şablonlar mühürlenmiştir:

| İskelet Boyutu | Seçilen Şablon / Kaset / Token | Kaynak / CLI Komutu |
|---|---|---|
| **1. Yaşayan Yüzey & 16 Kilitli Tema** | `[Light/Dark Living Surface + #01..#16 kilitli tema]` | `.agent/skills/frontend-design/themes/themes.css` |
| **2. 55+ Doğrulanmış Bileşen Teması** | `[logins / sidebars / navbars / menus / cards / footers / accordions ID'si]` | `python .agent/skills/frontend-design/scripts/get_component.py --list` |
| **3. 18 Doğrulanmış Dashboard Şablonu** | `[dashboard-theme-XX veya 'Kapsam Dışı']` | `.agent/skills/frontend-design/dashboard-theme/catalog.json` |
| **4. Zero-CLS Skeleton Kaseti & 4 UX Durumu** | `[Profil / Metrik Kart / Tablo Satırı / Dashboard / Form Kaseti]` | `ui-polish` & `check_design_slop.py` |
| **5. Mobil Ergonomi Kalkanı** | `[Yatay kaydırmasız flex-wrap / bottom-sheet / çift katmanlı scroll kilidi]` | `ui-polish` (W3, W4, W5) |

---

## 6. 🏗️ 5 Katmanlı Dikey Dilim Mimarisi (Full-Stack Vertical Slice)
> ⛔ Bir katman dahi eksikse Sahte Bitti (Phantom Done) sayılır.

| Katman | Yapılacak İşlem / Değişiklik | İlgili Dosya / Şema |
|---|---|---|
| **1. DB / Şema / Migration** | [Yeni tablo, kolon, RLS veya 'Kapsam dışı / Salt UI'] | `[örn. supabase/migrations/024_*.sql veya Mevcut]` |
| **2. Backend / View / RPC** | [Endpoint, DTO, servis, controller veya 'Kapsam dışı'] | `[örn. RPC / Controller]` |
| **3. İstemci API Entegrasyonu** | [Fetch/Axios istemcisi, tip tanımları, API fonksiyonu] | `[örn. src/modules/.../api.ts]` |
| **4. Arayüz / UX & Eylemler** | [Bileşen, form, 4 UX Durumu + Zorunlu Zero-CLS Skeleton Screens UI] | `[örn. src/modules/.../Component.tsx]` |
| **5. Döngü Kapanışı (Admin/Yönetim)** | [Verinin onay/yönetim ekranı veya 'Kullanıcı döngüsü'] | `[örn. UserMenu / AdminPage]` |

---

## 7. 🧪 TDD Kırmızı-Yeşil Dikiş Noktaları (Seams) ve Sıralı İcra Fazları
> ⛔ **PROCEED İCRA KURALI (MANDATORY):** Kullanıcı onay verdiğinde doğrudan kaynak koduna geçilemez; sırasıyla aşağıdaki fazlar icra edilir:

### 🔴 Faz 1: Dikiş Noktası & Kırmızı Test (Red Loop)
- **Test Dosyası:** `[örn. tests/.../feature.test.ts]`
- **Test Edilen Dikiş Noktası (Public Seam):** `[Dahili detaylar değil, genel bileşen/servis davranışı]`
- **Çalıştırılacak Test Komutu:** `[örn. npx vitest run tests/.../feature.test.ts]`
- **Beklenen Başarısızlık Kanıtı:** Testin çalıştırılarak **KIRMIZI (FAIL)** olduğunun terminalde kanıtlanması zorunludur.

### 🟢 Faz 2: Minimal Geçiş Kodu (Green Loop)
- **Üretim Kod Dosyası:** `[örn. src/.../FeatureComponent.tsx]`
- **Kapsam:** Yalnızca Faz 1'deki testi yeşile döndürecek minimal kod yazılır (spekülatif kod eklenmez).
- **Çalıştırılacak Test Komutu:** `[örn. npx vitest run tests/.../feature.test.ts]`
- **Beklenen Başarı Kanıtı:** Testin **YEŞİL (PASS)** olduğunun kanıtlanması.

### 🧩 Faz 3: 5 Katman Tamamlama, Tema İskeleti & `/ui-polish` İcrası
- Varsa API, DB ve UI katmanları bağlanır; seçilen `component-themes/` veya `dashboard-theme/` şablonu projenin yaşayan yüzey token'larıyla uygulanır.
- `/ui-polish` Ön Uçuş Makbuzu basılır; veri yükleme durumlarında **Zero-CLS Skeleton Screens UI** uygulanır.
- 3 Cihaz ergonomisi (Mobil <768px, Tablet 768-1024px, Masaüstü >1024px) ve çift katmanlı scroll kilidi doğrulanır.

### 🧹 Faz 4: Refactor, Kapılar & Kapanış
- Kod temizliği (`code-review` & `codebase-design` standartları).
- Zorunlu kapıların çalıştırılması: `python .agent/skills/musgoku/scripts/rules_gates.py`.
- Kullanıcı test senaryosunun `docs/KULLANICI_TEST_REHBERI.md` ve interaktif `docs/kullanici-rehberi.html` dosyalarına işlenmesi.

---

## ⚡ 8. Karar ve Başlangıç Onayı (Lütfen Seçiminizi Belirtin)

Uygulamaya ve TDD döngüsüne geçmem için lütfen aşağıdaki 4 tercihinizi paylaşın:
1. **Öncelik Sırası:** Hangi modül veya sayfalardan başlayalım? *(Örn: Önce Ayarlar ve Profil/Güvenlik, ardından Analitik/Insights)*
2. **Kademe Seçimi:** Hangi çözüm seviyesini uygulayalım? *(Seçenek 1: MVP / Seçenek 2: Best-Practice / Seçenek 3: PRD Vizyoner)*
3. **Tema, Bileşen ve Dashboard Seçimi:** Skillset'ten önerilen hangi kilitli tema (`#01..#16`), bileşen şablonları (`get_component.py`) ve dashboard mimarisini (`dashboard-theme-XX`) baz alalım?
4. **Veri & API Yaklaşımı:** Backend eksiği (`[Yeni API/DB Gerekli 🔴]`) olan modüllerde **Full-Stack (5 Katman: DB + Backend + API + UI)** olarak mı örelim, yoksa şimdilik tipli servis dikiş noktasıyla **`Mock-UI (YARIM — Eksik Katman HANDOFF'a kaydedilir)`** olarak mı hazırlayalım?
```
