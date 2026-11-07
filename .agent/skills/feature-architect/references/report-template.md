# Feature Architect — 6 Şapkalı Konsey Konsolide Plan ve Rapor Şablonu

> **Dil Kuralı:** Raporun dili, çalışılan projenin birincil dokümantasyon diline (`PRODUCT.md` / `README.md`) göre otomatik seçilir (Türkçe projede Türkçe, İngilizce projede İngilizce).
> **Kanıt ve Zero-Drop Kuralı:** Tablodaki her bulgu `gap_scanner.py` veya ajanın açıp doğruladığı dosyadan `dosya:satır` kanıtı taşır. Hiçbir uzmanın `CRITICAL` veya `HIGH` bulgusu özetlenirken silinemez; rapor sunumundan önce `python .agent/skills/feature-architect/scripts/council_merger.py --inputs docs/plans/council/<YYYY-MM-DD> --check-report <rapor.md>` kapısından `exit 0` ile geçmek zorunludur.
> **Çift Yönlü Kalıcılık (Dual-Persistence):** Bu rapor hem `<artifact-dir>/feature-architect-report.md` artifact'ı olarak üretilir, **HEM DE** hedef projenin `docs/plans/council/<YYYY-MM-DD>/feature-architect-council-report.md` ve `docs/plans/feature-architect-report.md` (veya `.agent/plans/`) konumlarına eşzamanlı yazılır.

---

## Adım 0 — Ön Onay: Motor Seçimi Sorusu (`engine_advisor.py` — Alt Ajan Destekli Ortamlarda)

Ortam alt ajan çağrısını destekliyorsa (`--subagents yes`) ve kullanıcı `--engine` bayrağı vermediyse, 6 şapka denetimine başlamadan önce kullanıcıya şu şablonla motor seçimi sorulur:

```markdown
🧭 **Motor Seçimi (`/feature-architect`)** — Proje Ölçeği: **`[small | medium | large]`** (`[X]` kaynak dosya · `[Y]` LOC · `[Z]` rota · `[P]` peer repo · `[G]` tespit edilen boşluk)
- **Analiz Gerekçesi:** `[engine_advisor.py tarafından üretilen kanıtlı gerekçe]`
1. **[Önerilen Motor — örn. Alt Ajanlı Paralel (`multi`) veya Tek Ajan Sıralı (`single`)]:** `[Açıklama]`
2. **[Alternatif Motor]:** `[Açıklama]`

6 uzmanlı konsey denetimine hangi motorla başlayalım? (`single` / `multi`)
```

---

## Nihai Konsolide Plan Raporu Şablonu (7 Ana Konsey Bölümü + İcra Sözleşmesi)

```markdown
# 🧭 [Proje Adı] — 6 Şapkalı Ürün Konseyi Denetimi ve 5 Katmanlı Mimari Tamamlama Planı

> **Hedef Dal / Sürüm:** `[örn. main / v1.2.0]` · **Tarih:** `[YYYY-MM-DD]`  
> **Konsey Orkestratörü:** Baş Hakem (Chief Council Arbiter) + 6 Uzman Şapka (`PO`, `ARCH`, `UX`, `SEO`, `GRW`, `QA`)  
> **Yürütme Motoru & İzolasyon:** `[Paralel Alt Ajanlı (Tam Kör İzolasyon) VEYA Tek Ajan Sıralı İzolasyon (Kör izolasyon zayıflatılmış)]`  
> **Görevlendirilen Skill'ler:** `feature-architect`, `council`, `doc-coauthoring`, `tdd`, `ui-polish`, `frontend-design`, `prelaunch-audit`  
> **Kalıcı Konsey Dizini:** `docs/plans/council/[YYYY-MM-DD]/` & `<artifact-dir>/feature-architect-report.md`  

---

## 1. Konsey Sağlık Karnesi ve Proje DNA'sı
- **Proje Amacı (PRD Özeti):** [Projenin temel değer önerisi ve hedef kitlesi]
- **Teknoloji & UI Yapısı:** [Frontend, Backend, DB, i18n ve Yaşayan Yüzey Modu (Light/Dark)]
- **Ağırlıklı Ham Ortalama:** `[XX.X / 100]` (`[Aktif Uzman Sayısı]` uzman üzerinden eşit ağırlık)
- **Proje Olgunluk Skoru:** **`[YY.Y / 100]`** *(Çözülmemiş CRITICAL bulgu varsa maksimum `60.0` CRITICAL tavanı uygulanır)*
- **En Zayıf Halka:** `[En düşük skorlu uzman şapka ve skoru]`
- **Kanıt Tarama Özeti:** `[stub_pages: X | stub_actions: Y | broken_routes: Z | orphan_endpoints: W | orphan_fields: V]`

| Uzman Şapka | Kod | Durum | Sağlık Skoru | Öne Çıkan Durum Özeti |
| :--- | :---: | :---: | :---: | :--- |
| **Snr. Product Owner** | `PO` | Aktif | `[0-100]` | [Kullanıcı yolculuğu ve çekirdek modül özeti] |
| **Snr. Software Architect** | `ARCH` | Aktif | `[0-100]` | [5 katmanlı mimari, yetim API/DB ve rota özeti] |
| **Principal UI/UX Specialist** | `UX` | Aktif | `[0-100]` | [16 tema, 18 dashboard, Zero-CLS 4 durum ve mobil ergonomi] |
| **Snr. Technical SEO** | `SEO` | `[Aktif / N/A]` | `[0-100 / —]` | [Semantik yapı, JSON-LD, CWV veya N/A gerekçesi] |
| **Snr. Growth & Marketing** | `GRW` | Aktif | `[0-100]` | [Onboarding hızı, mikro-metinler ve PLG büyüme kancaları] |
| **Snr. QA & Security Auditor** | `QA` | Aktif | `[0-100]` | [OWASP güvenlik temeli, RBAC/RLS ve 5 katmanlı TDD kapsamı] |

---

## 2. Tamamlama Envanteri ve 6 Fiilli Karar Matrisi (`CONNECT | FIX | REFACTOR | COMPLETE | REMOVE | DEFER`)

| Bulgu ID | Karar Fiili (`decision`) | Kategori | Önem | Modül / Konum (`dosya:satır`) | Somut Kanıt (`evidence`) | Güvenlik Ön Koşulu (`blocked_by`) | Veri & API Hazırlığı |
| :---: | :---: | :--- | :---: | :--- | :--- | :---: | :--- |
| `PO-01` | `COMPLETE` | `STUB_PAGE` | `HIGH` | `/reports` (`src/pages/Reports.tsx:42`) | `reports.underDevelopmentDesc` | — | `[Kısmen Hazır ⚠️]` |
| `ARCH-01` | `FIX` | `BROKEN_ROUTE` | `HIGH` | `/settings/api` (`src/components/Sidebar.tsx:84`) | Menüde var, Router'da yok | `QA-01` | `[Yeni API/DB Gerekli 🔴]` |
| `ARCH-02` | `CONNECT` | `ORPHAN_API_DB` | `MEDIUM` | `GET /api/v1/audit-logs` (`AuditController.java:51`) | Backend'de hazır, istemcide yok | — | `[Veri Hazır ✅]` |
| `QA-01` | `FIX` | `SECURITY` | `CRITICAL` | `DELETE /api/v1/users/:id` (`UserController.java:93`) | Sunucu tarafı RBAC kontrolü eksik | — | `[Kısmen Hazır ⚠️]` |

---

## 3. 6 Uzman Gözünden Kritik Bulgular (Ezilmemiş İzole Özetler ve 3 Kademeli Çözümler)

*(Her uzmanın kendi imzasıyla sunduğu kritik tespitler, Ezilmez Kırmızı Çizgileri ve çekirdek modüller [Profil/Ayarlar, Dashboard, Güvenlik Temeli ve OWASP uyumu] için Seçenek 1: MVP / Seçenek 2: Best-Practice / Seçenek 3: PRD Vizyoner alternatifleri burada yer alır. Hiçbir `CRITICAL` veya `HIGH` bulgu ID'si atlanamaz).*

- **PO (`snr-product-owner`):** [Bulgular + Kırmızı Çizgiler + 3 Kademeli Çekirdek Modül Önerisi]
- **ARCH (`snr-software-architect`):** [Bulgular + Kırmızı Çizgiler]
- **UX (`principal-ui-ux-specialist`):** [Bulgular + Kırmızı Çizgiler]
- **SEO (`snr-seo-specialist`):** [Bulgular + Kırmızı Çizgiler veya Kapsam Dışı Gerekçesi]
- **GRW (`snr-growth-marketing`):** [Bulgular + Kırmızı Çizgiler]
- **QA (`snr-qa-security-auditor` — Güvenlik Temeli & OWASP):** [OWASP 20 madde denetimi, RBAC/IDOR/RLS bulguları + Kırmızı Çizgiler]

---

## 4. UI/UX ve Birleşik Tema / 18 Dashboard-Theme Uyumsuzluk Raporu

### 4.1 Ekran Bazlı Görsel ve Deneyimsel Sapmalar (`ui_ux_mismatches`)
| Ekran / Bileşen | Tema / Referans Sapması | UX & CWV Etkisi | Önerilen Düzeltme |
| :--- | :--- | :--- | :--- |
| `[örn. src/pages/Dashboard.tsx]` | `[Ham dönen spinner + yatay taşan filtre]` | `[CLS zıplaması + mobilde gizli filtre]` | `[Zero-CLS kaset + flex-wrap filtre]` |

### 4.2 Birleşik Tema ve Bileşen İskeleti Sözleşmesi (`ui-polish` & `theme-skeleton-matching`)
| İskelet Boyutu | Seçilen Şablon / Kaset / Token | Kaynak / CLI Komutu |
|---|---|---|
| **1. Yaşayan Yüzey & 16 Kilitli Tema** | `[Light/Dark Living Surface + #01..#16 kilitli tema]` | `.agent/skills/frontend-design/themes/themes.css` |
| **2. 55+ Doğrulanmış Bileşen Teması** | `[logins / sidebars / navbars / menus / cards / footers / accordions ID'si]` | `python .agent/skills/frontend-design/scripts/get_component.py --list` |
| **3. 18 Doğrulanmış Dashboard Şablonu** | `[dashboard-theme-XX veya 'Kapsam Dışı']` | `.agent/skills/frontend-design/dashboard-theme/catalog.json` |
| **4. Zero-CLS Skeleton Kaseti & 4 UX Durumu** | `[Profil / Metrik Kart / Tablo Satırı / Dashboard / Form Kaseti]` | `ui-polish` & `check_design_slop.py` |
| **5. Mobil Ergonomi Kalkanı** | `[Yatay kaydırmasız flex-wrap / bottom-sheet / çift katmanlı scroll kilidi]` | `ui-polish` (W3, W4, W5) |

---

## 5. Gözden Kaçan Yeni Feature'lar (Beyond-PRD Innovation Matrix — RICE Sıralaması)

| RICE Skoru | Özellik Başlığı | Öneren Uzman(lar) | Reach / Impact / Conf / Efor | Kullanıcı & İş Değeri | Kanonik 5 Katmanlı Dilim Özeti |
| :---: | :--- | :--- | :---: | :--- | :--- |
| **`[40.5]`** | `[Örn: Aktif Oturumlar ve Cihaz İptali]` | `PO`, `QA` | `9 / 9 / 1.0 / M` | `[Çalınan oturumları anında kapatma]` | `[DB -> RPC -> API -> Security UI + Skeleton -> Audit Log]` |

---

## 6. Konsey Uzlaşı ve Çatışma Matrisi (Sinerji Kümeleri, Hibrit 3. Yol & Borda Hakemliği)

### 6.1 Sinerji Kümeleri (Yüksek Öncelikli Ortak Hedefler)
- **`[Dosya / Rota]`** (`[Baz Önem]` -> **`[Yükseltilmiş Önem]`**) · İşaret Eden Uzmanlar: `[PO, GRW, UX]` · Birleştirilen Bulgular: `[PO-01, GRW-01, UX-02]`.

### 6.2 Uzman Çatışmaları ve Hibrit Mühendislik Çözümü (Trade-off Decisions)
| Konum / Konu | Öneren Uzman & Talep | Kırmızı Çizgi Sahibi & Kısıt | Baş Hakem Hibrit 3. Yol Kararı (ve gerekirse Borda Skoru) |
| :--- | :--- | :--- | :--- |
| `[örn. Landing.tsx]` | `GRW`: İlk girişte kayıt duvarı | `SEO` & `UX`: Bot engelleme ve CLS yasağı | `[Sayfa içi yapışkan değer çubuğu — CLS=0, tam indekslenebilir]` |

---

## 7. 5 Katmanlı TDD Uygulama Yol Haritası (Fazlandırılmış Backlog & Dikiş Noktaları)

### 7.1 Kanonik 5 Katmanlı Dikey Dilim Matrisi
> ⛔ Bir katman dahi eksikse Sahte Bitti (Phantom Done) sayılır.

| Katman | Yapılacak İşlem / Değişiklik | İlgili Dosya / Şema |
|---|---|---|
| **1. DB / Şema / Migration** | `[Yeni tablo, kolon, indeks, RLS veya 'Mevcut şema yeterli']` | `[örn. migrations/024_*.sql]` |
| **2. Backend / View / RPC** | `[Repository + Service + Controller/Endpoint + OWASP RBAC/Validasyon]` | `[örn. Controller / Service]` |
| **3. İstemci API Entegrasyonu** | `[Tipli servis adaptörü, hata zarfı eşlemesi]` | `[örn. src/services/*Service.ts]` |
| **4. Arayüz / UX & Eylemler** | `[Bileşen, form, 4 UX Durumu + Zorunlu Zero-CLS Skeleton Screens UI]` | `[örn. src/pages/*.tsx]` |
| **5. Döngü Kapanışı (Admin/Yönetim)** | `[Verinin yönetim/denetim/geri alma döngüsü]` | `[örn. AdminAuditView / Settings]` |

### 7.2 TDD Kırmızı-Yeşil Dikiş Noktaları (Seams) ve Sıralı İcra Fazları
1. **🔴 Faz 1 — Dikiş Noktası & Kırmızı Test:** `[Test dosyası, genel dikiş noktası (public seam), çalıştırılacak test komutu ve beklenen FAIL kanıtı]`
2. **🟢 Faz 2 — Minimal Geçiş Kodu:** `[Yalnızca Faz 1 testini yeşile çevirecek üretim kodu ve PASS kanıtı]`
3. **🧩 Faz 3 — 5 Katman Tamamlama & `/ui-polish` İcrası:** `[Tema iskeleti, Zero-CLS kasetleri ve 375px->1440px mobil ergonomi doğrulaması]`
4. **🧹 Faz 4 — Refactor, Kapılar & Kapanış:** `[python .agent/skills/musgoku/scripts/run_all_gates.py + docs/KULLANICI_TEST_REHBERI.md + docs/kullanici-rehberi.html]`

---

## ⚡ 8. Karar ve Başlangıç Onayı (Lütfen Seçiminizi Belirtin)

Uygulamaya ve TDD kırmızı-yeşil döngüsüne geçmem için lütfen aşağıdaki 4 tercihinizi paylaşın:
1. **Öncelik ve Kapsam Seçimi:** Tamamlama envanterindeki hangi modüllerden başlayalım ve **Beyond-PRD (Bölüm 5)** listesinden dahil etmek istediğiniz yeni özellikler hangileri?
2. **Kademe Seçimi:** Hangi çözüm seviyesini uygulayalım? *(Seçenek 1: MVP / Seçenek 2: Best-Practice / Seçenek 3: PRD Vizyoner)*
3. **Tema, Bileşen ve Dashboard Seçimi:** Önerilen hangi kilitli tema (`#01..#16`), bileşen şablonları (`get_component.py`) ve dashboard mimarisini (`dashboard-theme-XX`) baz alalım?
4. **Veri & API Yaklaşımı:** Backend eksiği (`[Yeni API/DB Gerekli 🔴]`) olan maddelerde **Full-Stack (5 Katman: DB + Backend + API + UI + Döngü Kapanışı)** olarak mı örelim, yoksa tipli servis dikiş noktasıyla **`Mock-UI (YARIM — Eksik Katman HANDOFF'a kaydedilir)`** olarak mı hazırlayalım?
```
