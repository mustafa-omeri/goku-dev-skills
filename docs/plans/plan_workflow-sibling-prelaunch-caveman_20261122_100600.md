# Planlama, Kardeş Proje, Pre-Launch (404/503), Caveman+FAA AC 121-24C ve Verify-Sprint Kesin Çözüm Planı
<!-- 
  Bu dosya Antigravity IDE, Antigravity CLI (agy), Claude Code (claude), OpenCode (opencode) ve Genel CLI planlama modları (/plan) ve standart geliştirme planları için zorunlu şablondur.
  Kaynak: .agent/templates/PLAN.template.md · Kural: .agent/rules/development-workflow.md Adım 2.1 & 2.2 + .agent/rules/aviation-documentation-standard.md (FAA AC 121-24C + /caveman)
-->

> **Hedef Dal / Sürüm:** `main / v1.42.0` · **Tarih:** `2026-11-22`  
> **Görevlendirilen Skill'ler:** `musgoku`, `tdd`, `council`, `karpathy-guidelines`, `prelaunch-audit`, `prelaunch`, `verify-sprint`, `doc-coauthoring`  
> **Uygulanan Kurallar:** `aviation-documentation-standard.md`, `development-workflow.md`, `sprint-delivery-workflow.md`, `handoff-session-continuity.md`, `skill-trigger-routing.md`  
> **Kullanılan MCP'ler:** `second-brain-vault` (`bootstrap`, `get_project_state`)  
> **İlgili KANBAN Kartı:** `S4-01 .. S4-06` (`GSW-ARCH-001 .. GSW-ARCH-006`)  
> **Desteklenen Ortamlar:** `Antigravity IDE`, `Antigravity CLI (agy)`, `Claude Code (claude)`, `OpenCode (opencode)`, `Genel Terminal / CLI`  

---

## 1. [Goal Description] (Amaç & Kapsam)
Saha kullanımında tespit edilen 7 kritik süreç ve mekanik kapı açığını (`sohbet çıktısı olarak plan basma`, `/council'in .md plan üretmemesi ve kardeş proje sormaması`, `aynı/farklı dizin kardeş proje davranışı ve süreç dosyaları senkronu`, `pre-launch 404/503 özel sayfa kontrolü`, `ana ekran /caveman + FAA AC 121-24C yanıt zorunluluğu`, `tüm plan yönergelerinin FAA AC 121-24C olması`, `sprint bitiminde otomatik /verify-sprint sorusu`) hem kural/skill sözleşmelerinde hem de Python mekanik kapı betiklerinde (`sync_sibling_handoff.py`, `prelaunch_checker.py`, `check_aviation_docs.py`) kesin ve ölçülebilir şekilde kapatır.

### Kullanıcı Değer Önerisi & Kabul Kriterleri (Gherkin Senaryosu)
```gherkin
# language: tr
Feature: Fiziksel Plan Dosyası, Kardeş Proje Topolojisi, Prelaunch 404/503, Caveman+FAA Yanıt ve Verify-Sprint Kapısı

  Scenario: SC01 - /plan ve /council çıktılarının fiziksel .md dosyası olarak üretilmesi ve FAA AC 121-24C uyumu
    Given kullanıcı "/plan" veya "/council" ile mimari/uygulama planı talep eder
    When ajan planı hazırlar ve check_aviation_docs.py çalıştırılır
    Then plan sohbet ekranına ham metin olarak basılmaz, ayrı bir fiziksel ".md" dosyasında oluşturulur
    And plan içindeki tüm icra adımları FAA AC 121-24C ("[Adım N]. [Eylem] -> [Beklenen Çıktı]", "⚠️ CRITICAL:", "🚨 Ditching & Emergency Exit") formatını taşır

  Scenario: SC02 - Aynı dizin ve farklı dizin kardeş projelerde topolojiye göre sahiplik ve süreç senkronu
    Given onaylanan bir plan veya "/council" kararı kardeş projede geliştirme gerektirir
    When sync_sibling_handoff.py çalıştırılır
    Then dizin fark etmeksizin kardeş projenin "HANDOFF.md" ve süreç dosyalarına ("KANBAN.md", "SPRINT_PLAN.md", "RELEASE_PLAN.md") kaynak plan referansı ve görev maddeleri işlenir
    And aynı çalışma dizinindeyse aynı kod ajanı süreci ilerletebilir; farklı dizindeyse öncelik kardeş projenin kendi kod ajanına verilerek kullanıcıya açıkça sorulur

  Scenario: SC03 - Pre-launch denetiminde 404 ve 503 özel sayfalarının zorunlu kontrolü ve sprint sonu /verify-sprint sorusu
    Given "/prelaunch" çalıştırılır veya aktif bir sprint tamamlanır
    When prelaunch_checker.py hedef dizini tarar ve sprintteki son kart tamamlanır
    Then sistemde 404 ve 503 (Bakım/Hizmet Dışı) özel sayfaları yoksa prelaunch_checker.py MAJOR bulgu üretir
    And her sprint bittiğinde ajan otomatik olarak kullanıcıya "/verify-sprint" çalıştırmayı sorar
```

---

## 2. 🏛️ Council Deliberation & Alternatif Yaklaşımlar (2+ Seçenek İncelemesi)

| Seçenek | Yaklaşım | Avantajlar (+) | Riskler / Dezavantajlar (-) | Borda Puanı |
|---|---|---|---|:---:|
| **Option A (Yalnızca Markdown Kural Güncellemesi)** | Yalnızca `.agent/rules/*.md` ve `SKILL.md` dosyalarına metinsel uyarı eklemek; Python betiklerine dokunmamak. | Hızlı yazılır, sıfır script değişikliği. | `OLCULEBILIR` kapı desteği olmadığı için ajanlar sohbet çıktısı vermeye, 503 sayfasını atlamaya ve kardeş süreç dosyalarını unutmaya devam eder. | `1.2` |
| **Option B (Kural + Şablon + Mekanik CLI Kapı Entegrasyonu — Karpathy & Determinizm)** | Kuralları (`AGENTS.md`, `development-workflow.md`, `sprint-delivery-workflow.md`, `handoff-session-continuity.md`, `aviation-documentation-standard.md`, `council`, `prelaunch-audit`, `verify-sprint`) güncellemek **VE** `sync_sibling_handoff.py`, `prelaunch_checker.py`, `check_aviation_docs.py` betiklerine mekanik doğrulama/senkron eklemek. | Deterministik exit kodu ve CLI kanıtı üretir; aynı/farklı dizin topolojisini, kardeş `KANBAN.md`/`SPRINT_PLAN.md` senkronunu, 404/503 sayfasını ve planlarda FAA AC 121-24C formatını mekanik olarak zorlar. | 3 Python betiğinde cerrahi güncelleme ve birim testi gerektirir. | `2.8` |

- **Seçilen Yol & Gerekçe:** **Option B (2.8 Borda)** seçildi. `sprint-delivery-workflow.md` §0 ilkesi gereği *"kapısı olmayan zorunlu kural ölü kalır"*; kural güncellemeleri doğrudan mekanik Python betikleri ve regresyon testleriyle mühürlenecektir.
- **Birleşik Planlama Ekosistemi Bağlantısı:** Kullanıcı Tespitleri → Konsey Hakemliği (`council`) → Uygulama Planı (`PLAN.template.md` / FAA AC 121-24C) → TDD Kırmızı Test (`tests/`) → Mekanik Betik & Kural Güncellemesi → Katalog & 4/4 Dağıtım (`delivery.py`).

---

## 3. User Review Required (Kullanıcı İncelemesi & Kritik Kararlar)
> [!IMPORTANT]
> 1. **Sohbet Çıktısı Plan Yasağı & Fiziksel `.md` Dosyası Zorunluluğu:** `/plan` ve `/council` (uygulama/mimari plan üretirken) artık planı sohbet ekranına ham metin olarak basmayacak; her plan kendi fiziksel `.md` dosyasında (`<artifact-dir>/<plan_name>.md` ve/veya `.agent/plans/<plan_name>.md` -> onayda `docs/plans/plan_<slug>_<timestamp>.md`) üretilecek, ana ekrana yalnız `/caveman + FAA AC 121-24C` özet kartı ve dosya linki basılacaktır.
> 2. **Kardeş Proje Topoloji & Süreç Senkronu (`sync_sibling_handoff.py`):**
>    - **Aynı Dizin / Çalışma Alanı:** Aynı Kod Ajanı süreci doğrudan ilerletebilir (skill'ler projelere göre yüklendiği için).
>    - **Farklı Dizin:** Öncelik her projenin kendi Kod Ajanındadır; başlamadan önce kullanıcıya sorulur.
>    - **Dizin Fark Etmeksizin:** Her projenin kendi `HANDOFF.md` dosyasına **ve süreç dosyalarına (`KANBAN.md`, `SPRINT_PLAN.md`, `RELEASE_PLAN.md`)** gerekli referans bilgilerle geliştirme maddeleri otomatik eklenir.
> 3. **Pre-Launch 404 & 503 Özel Sayfa Kapısı (`prelaunch_checker.py`):** Madde 17 `"Özel 404, 500 ve 503 (Bakım / Hizmet Dışı) Sayfaları"` olarak güncellenecek ve `prelaunch_checker.py` içinde 404 + 503 özel sayfa/rota varlığı mekanik olarak denetlenecektir.
> 4. **Ana Ekran `/caveman` + `FAA AC 121-24C` & Plan Yönergeleri:** Ana ekran yanıtları `/caveman` + `FAA AC 121-24C` standardına bağlanacak (`skills-catalog.html` içine `/caveman` komutu eklenecek); tüm plan yönergeleri (`PLAN.template.md` dahil) `check_aviation_docs.py` (`E1-E4`) ile FAA AC 121-24C formatında denetlenecektir.
> 5. **Sprint Sonu Otomatik `/verify-sprint` Sorusu:** Her sprint bittiğinde ajan otomatik olarak kullanıcıya `/verify-sprint` çalıştırmayı soracaktır.
>
> **2-Modlu Onay Seçenekleri (Planı Nasıl İlerletelim?):**
> - **Seçenek A — Mühürle & Sıraya Al (`/seal-plan` / `"planı mühürle, kodlama yapma"`):** Planı `docs/plans/` altına arşivler, `HANDOFF.md` §3 Gelecek Fazlar (`⬜ Bekliyor`) panosuna dağıtır; **kod yazmadan durur**.
> - **Seçenek B — Onayla & Hemen Başla (`Proceed` / `"onayla ve başla"`):** Faz 0 mühürlemesini yapıp hemen Faz 1 (TDD Kırmızı Test) ile geliştirmeye başlar.

## 4. Open Questions (Açık Sorular)
Açık soru bulunmamaktadır. 7 tespitin tamamı net ve deterministik olarak kapsanmıştır.

---

## 5. 📋 Sprint, HANDOFF & KANBAN Durumu (Deterministik Görev Kimlikleri)
| Görev ID (`[DOM]-[TIP]-[NO]`) | Mevcut Durum | Hedef Durum (Proceed Sonrası) | Kapsam / KANBAN Kartı |
|---|---|---|---|
| `GSW-ARCH-001` | `Bekliyor` | `Yapılıyor` -> `Yapıldı` | `/plan` ve `/council` fiziksel `.md` plan dosyası zorunluluğu + kardeş proje sorusu |
| `GSW-ARCH-002` | `Bekliyor` | `Yapılıyor` -> `Yapıldı` | Aynı/farklı dizin kardeş proje davranışı + `HANDOFF.md` ve süreç dosyaları (`KANBAN`/`SPRINT_PLAN`/`RELEASE_PLAN`) senkronu (`sync_sibling_handoff.py`) |
| `GSW-ARCH-003` | `Bekliyor` | `Yapılıyor` -> `Yapıldı` | Pre-launch `404, 500, 503` özel sayfalar kuralı ve `prelaunch_checker.py` mekanik kontrolü |
| `GSW-ARCH-004` | `Bekliyor` | `Yapılıyor` -> `Yapıldı` | Ana ekran `/caveman` + `FAA AC 121-24C` yanıt standardı, `/caveman` slash komutu ve tüm plan yönergelerinin (`PLAN.template.md`, `check_aviation_docs.py`) FAA AC 121-24C uyumu |
| `GSW-ARCH-005` | `Bekliyor` | `Yapılıyor` -> `Yapıldı` | Her sprint bitiminde otomatik `/verify-sprint` çalıştırma sorusu protokolü |

### 5.1 🔗 Kardeş Uygulama (Cross-Repo) Etkisi & Yürütme Sahipliği
- **Etkilenen Kardeş Uygulama & Yol:** `Tek Repo / Kardeş Uygulama Etkisi Yok` *(Bu depo `skillSetWorks` merkez kural/skill dağıtım kaynağıdır; değişiklikler `python delivery.py` ile 4 hedef projeye `.agent/` olarak dağıtılır).*

---

## 6. 🏗️ 5 Katmanlı Dikey Dilim Mimarisi (Full-Stack Vertical Slice)

| Katman | Yapılacak İşlem / Değişiklik | İlgili Dosya / Şema |
|---|---|---|
| **1. DB / Şema / Migration** | Kapsam dışı (Kural ve CLI dağıtım deposu; durum ve süreç dosyaları Markdown/JSON tabanlıdır) | `HANDOFF.md`, `KANBAN.md`, `SPRINT_PLAN.md`, `RELEASE_PLAN.md` |
| **2. Backend / CLI Motor Katmanı** | 1) `sync_sibling_handoff.py`: Aynı/farklı dizin topoloji tespiti (`detect_directory_topology`) + kardeş süreç dosyaları (`KANBAN.md`, `SPRINT_PLAN.md`, `RELEASE_PLAN.md`) senkronu.<br>2) `prelaunch_checker.py`: `check_custom_error_pages` (404 & 503 özel sayfa/rota taraması).<br>3) `check_aviation_docs.py`: `PLAN.template.md` ve plan dosyalarında `E1` (Acil Çıkış Tablosu) + `E2` (`[Adım N]... -> [Beklenen Çıktı]`) kontrolü. | `.agent/skills/musgoku/scripts/sync_sibling_handoff.py`<br>`.agent/skills/prelaunch-audit/scripts/prelaunch_checker.py`<br>`.agent/skills/musgoku/scripts/check_aviation_docs.py` |
| **3. Kural & Şablon Sözleşmesi** | Anayasal kurallar, plan şablonu ve skill dosyalarının 7 maddeye göre güncellenmesi. | `.agent/AGENTS.md`<br>`.agent/templates/PLAN.template.md`<br>`.agent/rules/development-workflow.md`<br>`.agent/rules/sprint-delivery-workflow.md`<br>`.agent/rules/handoff-session-continuity.md`<br>`.agent/rules/aviation-documentation-standard.md`<br>`.agent/rules/skill-trigger-routing.md` |
| **4. Skill & Katalog Arayüzü** | `council/SKILL.md`, `prelaunch-audit/SKILL.md`, `prelaunch/SKILL.md`, `verify-sprint/SKILL.md`, `karpathy-guidelines/SKILL.md` ve `.agent/skills-catalog.html` (`/caveman` komutu dahil) güncellenmesi. | `.agent/skills/council/SKILL.md`<br>`.agent/skills/prelaunch-audit/SKILL.md`<br>`.agent/skills/verify-sprint/SKILL.md`<br>`scripts/generate_skills_catalog.py` |
| **5. Döngü Kapanışı & Dağıtım** | Birleşik kapılar (`run_all_gates.py`), 30/30 test paketi (`tests/run_all.py`) ve `delivery.py` ile 4 hedef projeye dağıtım. | `tests/test_sync_sibling_handoff.py`<br>`tests/test_prelaunch_security.py`<br>`tests/test_council_workflow_integration.py`<br>`delivery.py` |

---

## 7. 🎨 Tema ve Bileşen İskeleti Sözleşmesi (Theme & Component Skeleton Contract)
- **Durum:** `Salt Backend / CLI & Kural Dağıtım Deposu (UI Kapsam Dışı)` — `.agent/skills-catalog.html` üretimi mevcut Obsidian Command Deck token yapısını (`generate_skills_catalog.py`) birebir korur.

---

## 8. 🧪 TDD Kırmızı-Yeşil Dikiş Noktaları (Seams) ve Sıralı İcra Fazları (FAA AC 121-24C Standardı)

```ascii
[Faz 0: Plan Arşivi & Handoff] ──> [Faz 1: Kırmızı Test (FAIL)] ──> [Faz 2: CLI & Kural İnşası (PASS)] ──> [Faz 3: Katalog & Dağıtım (4/4)]
```

### 📌 Faz 0: Onay Sonrası Mühürleme (`docs/plans/`, `HANDOFF.md` §3 & Sprint Açılışı)
1. **[Adım 1 - Planı `docs/plans/` Altına Arşivle]:** `python .agent/skills/musgoku/scripts/archive_plan.py --plan C:\Users\Mustafa\.gemini\antigravity-cli\brain\a275e51e-96d6-4a12-9152-81ccfdb54866\implementation_plan.md --slug workflow-sibling-prelaunch-caveman` -> **Beklenen Çıktı:** `[ARCHIVED] docs/plans/plan_workflow_sibling_prelaunch_caveman_<YYYYMMDD_HHMMSS>.md`
2. **[Adım 2 - `HANDOFF.md` §3 Canlı Panosuna İşle]:** `GSW-ARCH-001..005` görev kimliklerini ve arşivlenen plan referansını `HANDOFF.md` §3 tablosuna kaydet -> **Beklenen Çıktı:** `python .agent/skills/musgoku/scripts/check_handoff.py` `0 hata, 0 W3 uyarısı` döner.

### 🔴 Faz 1: Dikiş Noktası & Kırmızı Test (Red Loop)
1. **[Adım 1 - Kardeş Proje Topoloji & Süreç Dosyaları Kırmızı Testi]:** `tests/test_sync_sibling_handoff.py` içine `test_directory_topology_detection_and_process_files_sync` testini ekle ve `python tests/test_sync_sibling_handoff.py` çalıştır -> **Beklenen Çıktı:** `AttributeError / AssertionError (FAIL - KIRMIZI)` (`detect_directory_topology` ve kardeş `KANBAN.md`/`SPRINT_PLAN.md`/`RELEASE_PLAN.md` senkronu henüz yok).
2. **[Adım 2 - Prelaunch 404/503 Özel Sayfa ve Plan FAA AC 121-24C Kırmızı Testi]:** `tests/test_prelaunch_security.py` içine `test_07_prelaunch_checker_detects_missing_404_503_pages` ve `tests/test_council_workflow_integration.py` içine `/council` fiziksel `.md` plan + kardeş proje sorusu + `/verify-sprint` otomatik soru + `/caveman` + `check_aviation_docs.py` E2 plan denetimi testlerini ekle; `python tests/test_prelaunch_security.py` ve `python tests/test_council_workflow_integration.py` çalıştır -> **Beklenen Çıktı:** `FAIL (KIRMIZI)` kanıtı terminalde görülür.

### 🟢 Faz 2: Minimal Geçiş Kodu (Green Loop — CLI Motorları)
1. **[Adım 1 - `sync_sibling_handoff.py` Güncellemesi]:** `detect_directory_topology()` ve `_sync_sibling_process_files()` fonksiyonlarını ekle (`HANDOFF.md` + `KANBAN.md` + `SPRINT_PLAN.md` + `RELEASE_PLAN.md` referanslı görev işleme + aynı/farklı dizin sahiplik mesajı); `python tests/test_sync_sibling_handoff.py` çalıştır -> **Beklenen Çıktı:** `Ran 5 tests ... OK (YEŞİL)`.
2. **[Adım 2 - `prelaunch_checker.py` 404/503 Kontrolü]:** `check_custom_error_pages(target_dir)` fonksiyonunu ekle (`404` ve `503`/maintenance özel sayfa/rota kontrolü); `python tests/test_prelaunch_security.py` çalıştır -> **Beklenen Çıktı:** `Ran 7 tests ... OK (YEŞİL)`.
3. **[Adım 3 - `check_aviation_docs.py` Plan Yönergeleri E1-E4 Denetimi]:** `PLAN.template.md` ve plan dosyalarını FAA AC 121-24C `E1` (Acil Çıkış tablosu) ve `E2` (`[Adım N]... -> [Beklenen Çıktı]`) kapsamına al; `python .agent/skills/musgoku/scripts/check_aviation_docs.py` çalıştır -> **Beklenen Çıktı:** `SONUC: Tüm doküman ve şablonlar FAA AC 121-24C standardına uygun · [OK]`.

### 🧩 Faz 3: Kural, Şablon, Skill ve Katalog Senkronizasyonu
1. **[Adım 1 - Kural ve Şablon Dosyalarını Güncelle]:** `.agent/AGENTS.md`, `.agent/templates/PLAN.template.md`, `.agent/rules/development-workflow.md`, `.agent/rules/sprint-delivery-workflow.md`, `.agent/rules/handoff-session-continuity.md`, `.agent/rules/aviation-documentation-standard.md`, `.agent/rules/skill-trigger-routing.md` dosyalarını güncelle -> **Beklenen Çıktı:** `python .agent/skills/musgoku/scripts/rules_gates.py --strict` `[OK]` döner.
2. **[Adım 2 - Skill Dosyalarını ve Kataloğu Güncelle]:** `council/SKILL.md`, `prelaunch-audit/SKILL.md`, `prelaunch/SKILL.md`, `prelaunch-audit/references/seo-and-discoverability.md`, `verify-sprint/SKILL.md`, `karpathy-guidelines/SKILL.md` ve `scripts/generate_skills_catalog.py` (`/caveman` slash komutu dahil) dosyalarını güncelle ve `python scripts/generate_skills_catalog.py` çalıştır -> **Beklenen Çıktı:** `.agent/skills-catalog.html` güncellenir ve `python tests/test_skills_catalog.py` `PASS` döner.

### 🧹 Faz 4: Refactor, Kapılar, Dağıtım & Kapanış
1. **[Adım 1 - Tüm Regresyon ve Birleşik Kapıları Çalıştır]:** `python .agent/skills/musgoku/scripts/run_all_gates.py` ve `python tests/run_all.py` komutlarını çalıştır -> **Beklenen Çıktı:** `30/30 TESTİN HEPSİ BAŞARIYLA GEÇTİ!` ve `0 başarısız kapı`.
2. **[Adım 2 - Hedef Projelere Dağıtım ve Parite Doğrulaması]:**
   ⚠️ CRITICAL: `python delivery.py` hedef projelerdeki `.agent/` ağacını kaynakla senkronize eder (`AGENTS.md` içindeki `## Proje Bazlı Ek Kurallar` bloğunu korur); öncesinde `--dry-run` ile hedefleri doğrula.
   `python delivery.py --dry-run && python delivery.py && python delivery.py --verify` çalıştır -> **Beklenen Çıktı:** `4/4 proje doğrulandı` ve `tests/check_agents_parity.py` `YENIDEN DAGITIM GEREKMIYOR` döner.

---

## 9. Proposed Changes (Önerilen Dosya Değişiklikleri)

### 1. Mekanik CLI Betikleri (`.agent/skills/*/scripts/`)

#### [MODIFY] [sync_sibling_handoff.py](file:///C:/devtools/myProjectsAreaWS/toolsWS/skillSetWorks/.agent/skills/musgoku/scripts/sync_sibling_handoff.py)
- **Aynı Dizin vs Farklı Dizin Topoloji Tespiti (`detect_directory_topology`):**
  - `source_root` ve `sibling_root` dizinlerinin aynı çalışma alanında / ortak ebeveyn proje grubunda olup olmadığını (`same_directory_workspace`) veya `--same-workspace` / `--different-directory` bayrağını değerlendirir.
  - Çıktıda deterministik `ownership_policy` üretir:
    * **Aynı dizin:** `"SAME_AGENT_ALLOWED: Kardeş proje aynı dizin/çalışma alanında; skill'ler projeye göre yüklendiği için aynı kod ajanı süreci doğrudan ilerletebilir."`
    * **Farklı dizin:** `"ASK_USER_PREFER_SIBLING_AGENT: Kardeş proje farklı dizinde; öncelik kardeş projenin kendi kod ajanındadır. Koda dokunmadan önce kullanıcıya sorulmalıdır."`
- **Kardeş Proje Süreç Dosyaları Senkronizasyonu (`_sync_sibling_process_files`):**
  - Dizin fark etmeksizin kardeş projenin `HANDOFF.md` dosyasına ek olarak kardeş projede `KANBAN.md`, `SPRINT_PLAN.md`, `RELEASE_PLAN.md` süreç dosyaları varsa (veya `--sync-processes` verildiğinde) görev maddesini (`task_id`, `task_title`) ve `<kaynak-proje> projesindeki <plan-yolu> plan dosyası referansına göre` bilgisini kardeş projenin süreç dosyalarına idempotent olarak ekler.

#### [MODIFY] [prelaunch_checker.py](file:///C:/devtools/myProjectsAreaWS/toolsWS/skillSetWorks/.agent/skills/prelaunch-audit/scripts/prelaunch_checker.py)
- **`check_custom_error_pages(target_dir)` Fonksiyonu:**
  - Hedef proje/dizinde özel **404** (`404.html`, `not-found.tsx`, `NotFound.tsx`, `404.tsx`, `error_page 404`) ve **503 / Bakım** (`503.html`, `503.tsx`, `maintenance.html`, `Maintenance.tsx`, `ServiceUnavailable.tsx`, `error_page 503` vb.) sayfalarının/rotalarının varlığını tarar.
  - Eksikse `results["items"]["custom_error_pages"]` altında `"MAJOR: Özel 404 ve/veya 503 (Bakım/Hizmet Dışı) sayfaları eksik (...). Canlıya çıkmadan önce 404 ve 503 özel sayfaları sisteme eklenmelidir."` bulgusu döndürür.

#### [MODIFY] [check_aviation_docs.py](file:///C:/devtools/myProjectsAreaWS/toolsWS/skillSetWorks/.agent/skills/musgoku/scripts/check_aviation_docs.py)
- **Plan Dosyalarının FAA AC 121-24C Denetimi (`E1` & `E2`):**
  - `PLAN.template.md` ve `.agent/plans/*.md` dosyalarını `is_guide` / `is_plan` kapsamına alır.
  - `E2` kontrolünü aktive eder: Plan ve rehber dosyalarının uygulama/icra adımlarında `[Adım N]... -> [Beklenen Çıktı]` (`->`) eşleşmesinin bulunmasını zorunlu kılar.

---

### 2. Anayasal Kurallar ve Plan Şablonu (`.agent/AGENTS.md`, `.agent/rules/`, `.agent/templates/`)

#### [MODIFY] [PLAN.template.md](file:///C:/devtools/myProjectsAreaWS/toolsWS/skillSetWorks/.agent/templates/PLAN.template.md)
- Tüm plan yönergelerinin **FAA AC 121-24C Dokümantasyon Standardı + `/caveman`** ile yazılmasını zorunlu kılan başlık ve yapı güncellenir.
- **§5.1 Kardeş Uygulama (Cross-Repo) Etkisi & Yürütme Sahipliği:**
  - Aynı dizin (Aynı Kod Ajanı ilerletebilir) vs Farklı dizin (Öncelik her projenin kendi kod ajanındadır, öncesinde kullanıcıya sorulur) ayrımı ve dizin fark etmeksizin her projenin kendi `HANDOFF.md` + süreçlerine (`KANBAN.md`, `SPRINT_PLAN.md`, `RELEASE_PLAN.md`) referanslı ekleme kuralı işlenir.
- **§8 TDD Kırmızı-Yeşil Dikiş Noktaları ve Sıralı İcra Fazları:**
  - Faz 0, Faz 1, Faz 2, Faz 3 ve Faz 4 adımlarının tamamı `[Adım N - Başlık]: [Eylem / Komut] -> Beklenen Çıktı: [Kanıt]` ve `⚠️ CRITICAL:` formatına dönüştürülür.

#### [MODIFY] [AGENTS.md](file:///C:/devtools/myProjectsAreaWS/toolsWS/skillSetWorks/.agent/AGENTS.md)
- **§2.3.1 Ana Ekran Yanıt Standardı (`/caveman` + `FAA AC 121-24C`):** Ana ekrana verilen tüm yanıtların `/caveman` nesir sıkıştırması + `FAA AC 121-24C` standardında olması ve tüm plan yönergelerinin FAA AC 121-24C formatında üretilmesi kuralı işlenir.
- **§2.4.1 Sprint Bitişinde Otomatik `/verify-sprint` Sorusu:** Her sprint bittiğinde ajanın otomatik olarak kullanıcıya `/verify-sprint` çalıştırmayı sorması kuralı güncellenir.
- **§4 Çoklu Araç Plan Modu (`/plan`, `/council`):** Planların sohbet çıktısı olarak verilmesi yasağı; her planın kendi fiziksel `.md` dosyasında üretilmesi ve aynı/farklı dizin kardeş proje kuralları işlenir.

#### [MODIFY] [development-workflow.md](file:///C:/devtools/myProjectsAreaWS/toolsWS/skillSetWorks/.agent/rules/development-workflow.md)
- **Adım 2.1 & Adım 2.2:**
  - ⛔ **Sohbet Çıktısı Olarak Plan Verme Yasağı (No Chat-Only Plan Rule):** `/plan`, `/council` ve plan üreten tüm akışlarda planın kendi fiziksel `.md` dosyasında (`<artifact-dir>/<plan_name>.md` ve/veya `.agent/plans/<plan_name>.md` -> onayda `docs/plans/plan_<slug>_<timestamp>.md`) verilmesi zorunluluğu.
  - Tüm plan yönergelerinin **FAA AC 121-24C Dokümantasyon Standardı** ile yazılması zorunluluğu.
  - Aynı dizin vs farklı dizin kardeş proje sahiplik matrisi ve `HANDOFF.md` + süreç dosyalarına (`KANBAN.md`, `SPRINT_PLAN.md`, `RELEASE_PLAN.md`) referanslı kayıt zorunluluğu.

#### [MODIFY] [sprint-delivery-workflow.md](file:///C:/devtools/myProjectsAreaWS/toolsWS/skillSetWorks/.agent/rules/sprint-delivery-workflow.md)
- **§2.1.1:** Fiziksel `.md` plan dosyası zorunluluğu, FAA AC 121-24C plan yönergeleri ve aynı/farklı dizin kardeş proje süreç senkronu.
- **§2.5 Sprint Sonu Otomatik `/verify-sprint` Onay Sorusu & Kapanış Kilidi:** Her sprint bittiğinde ajanın otomatik olarak kullanıcıya `"/verify-sprint çalıştırayım mı?"` sorusunu yöneltmesi ve onay sonrası `sprint_auditor.py` + Cerrahi Onarım + Audit Trail döngüsünü yürütmesi.

#### [MODIFY] [handoff-session-continuity.md](file:///C:/devtools/myProjectsAreaWS/toolsWS/skillSetWorks/.agent/rules/handoff-session-continuity.md)
- **§🔗 Çapraz-Proje (Kardeş Uygulama) Handoff, Süreç Senkronu & Topolojiye Göre Yürütme Sahipliği Protokolü:**
  1. Dizin fark etmeksizin her projenin kendi `HANDOFF.md` ve süreç dosyalarına (`KANBAN.md`, `SPRINT_PLAN.md`, `RELEASE_PLAN.md`) kaynak plan referansı ve görevlerin eklenmesi (`sync_sibling_handoff.py`).
  2. **Aynı Dizin / Çalışma Alanı:** Aynı Kod Ajanı süreci doğrudan ilerletebilir.
  3. **Farklı Dizin:** Öncelik her projenin kendi Kod Ajanındadır; başlamadan önce kullanıcıya mutlaka sorulur.

#### [MODIFY] [aviation-documentation-standard.md](file:///C:/devtools/myProjectsAreaWS/toolsWS/skillSetWorks/.agent/rules/aviation-documentation-standard.md)
- **§2 & §3:** Ana ekran yanıtlarının zorunlu olarak **`/caveman` + `FAA AC 121-24C Dokümantasyon Standardı`** birleşimiyle üretilmesi ve **tüm plan yönergelerinin (`/plan`, `/council`, `PLAN.template.md`, `docs/plans/*.md`)** istisnasız FAA AC 121-24C standardına tabi olduğu işlenir.

#### [MODIFY] [skill-trigger-routing.md](file:///C:/devtools/myProjectsAreaWS/toolsWS/skillSetWorks/.agent/rules/skill-trigger-routing.md)
- **§0, §A4 & §A5:** `/caveman` slash komutu (`karpathy-guidelines` + `aviation-documentation-standard.md`), `/plan` ve `/council` fiziksel `.md` dosya kuralı, `/verify-sprint` sprint sonu otomatik kullanıcı sorusu ve `/prelaunch` 404/503 özel sayfa kuralı güncellenir.

---

### 3. Skill Paketleri ve Katalog Üreticisi (`.agent/skills/`, `scripts/`)

#### [MODIFY] [council/SKILL.md](file:///C:/devtools/myProjectsAreaWS/toolsWS/skillSetWorks/.agent/skills/council/SKILL.md)
- **Aşama 3 & Fiziksel Plan Dosyası Zorunluluğu:** `/council` plan oluştururken yalnızca terminal/sohbet cevabı olarak plan veremez! Planı `PLAN.template.md` ve **FAA AC 121-24C Dokümantasyon Standardı** ile ayrı bir fiziksel `.md` dosyasında (`<artifact-dir>/council_plan_<slug>.md` ve/veya `.agent/plans/council_plan_<slug>.md` -> onayda `docs/plans/council_plan_<slug>_<timestamp>.md`) üretir.
- **Kardeş Proje (Cross-Repo) Topoloji ve Sahiplik Kapısı:** Karar kardeş projeyi etkiliyorsa, aynı dizin vs farklı dizin kuralına göre kullanıcıya kardeş proje geliştirme sorusunu sorar ve `sync_sibling_handoff.py` ile kardeş projenin `HANDOFF.md` + süreçlerine işler.

#### [MODIFY] [prelaunch-audit/SKILL.md](file:///C:/devtools/myProjectsAreaWS/toolsWS/skillSetWorks/.agent/skills/prelaunch-audit/SKILL.md), [prelaunch/SKILL.md](file:///C:/devtools/myProjectsAreaWS/toolsWS/skillSetWorks/.agent/skills/prelaunch/SKILL.md) & [seo-and-discoverability.md](file:///C:/devtools/myProjectsAreaWS/toolsWS/skillSetWorks/.agent/skills/prelaunch-audit/references/seo-and-discoverability.md)
- Madde 17: **`Özel Hata ve Bakım Sayfaları (404, 500, 503)`** olarak güncellenir; *"503 (Bakım / Geçici Hizmet Dışı), 404 (Sayfa Bulunamadı) ve 500 gibi özel sayfalar sistemde yoksa canlıya çıkmadan önce muhakkak sisteme eklenmeli"* kuralı ve `prelaunch_checker.py` doğrulaması eklenir.

#### [MODIFY] [verify-sprint/SKILL.md](file:///C:/devtools/myProjectsAreaWS/toolsWS/skillSetWorks/.agent/skills/verify-sprint/SKILL.md)
- **Sprint Sonu Otomatik Kullanıcı Sorusu:** Her sprint bittiğinde ajanın otomatik olarak kullanıcıya `/verify-sprint` çalıştırmayı sorması ve onay sonrası `sprint_auditor.py` + onarım döngüsünü işletmesi işlenir.

#### [MODIFY] [karpathy-guidelines/SKILL.md](file:///C:/devtools/myProjectsAreaWS/toolsWS/skillSetWorks/.agent/skills/karpathy-guidelines/SKILL.md) & [generate_skills_catalog.py](file:///C:/devtools/myProjectsAreaWS/toolsWS/skillSetWorks/scripts/generate_skills_catalog.py)
- `karpathy-guidelines/SKILL.md` §6 içine `/caveman` + `FAA AC 121-24C` ana ekran yanıt sözleşmesi işlenir.
- `generate_skills_catalog.py` içine `/caveman` slash komutu eklenir; `/plan`, `/council`, `/prelaunch` ve `/verify-sprint` katalog açıklamaları güncellenir.

---

## 10. Verification Plan (Doğrulama Planı)

### Automated Tests (Otomasyon Testleri)
```bash
# 1. Kardeş proje topoloji ve süreç dosyaları senkron testi
python tests/test_sync_sibling_handoff.py

# 2. Pre-launch 404/503 özel sayfa ve güvenlik testi
python tests/test_prelaunch_security.py

# 3. Council fiziksel .md plan, kardeş proje sorusu ve FAA AC 121-24C entegrasyon testi
python tests/test_council_workflow_integration.py

# 4. FAA AC 121-24C Dokümantasyon ve Plan Şablonu Kapısı
python .agent/skills/musgoku/scripts/check_aviation_docs.py --strict

# 5. Kural kapıları, katalog ve 30/30 tam regresyon paketi
python .agent/skills/musgoku/scripts/run_all_gates.py
python tests/run_all.py
```

### Manual Verification (Kullanıcı Doğrulama Adımları — FAA AC 121-24C Standardı)
1. **[Adım 1 - Plan ve FAA AC 121-24C Kapısı Kontrolü]:** Terminalde `python .agent/skills/musgoku/scripts/check_aviation_docs.py --strict` komutunu çalıştırın -> **Beklenen Çıktı:** `PLAN.template.md` dahil tüm rehber/şablon dosyalarının `SONUC: Tüm doküman ve şablonlar FAA AC 121-24C standardına uygun · [OK]` verdiğini görün.
2. **[Adım 2 - Kardeş Proje Topoloji & Süreç Senkronu Kontrolü]:** Terminalde `python tests/test_sync_sibling_handoff.py` komutunu çalıştırın -> **Beklenen Çıktı:** Aynı dizin vs farklı dizin sahiplik politikasının ve kardeş `HANDOFF.md` + `KANBAN.md` / `SPRINT_PLAN.md` senkronunun `OK` döndüğünü görün.
3. **[Adım 3 - Prelaunch 404/503 Özel Sayfa Denetimi]:** Terminalde `python tests/test_prelaunch_security.py` komutunu çalıştırın -> **Beklenen Çıktı:** 404 ve 503 özel sayfaları eksik olan projede `custom_error_pages` MAJOR bulgusunun yakalandığını ve sayfalar eklendiğinde `PASS` olduğunu görün.

---

## 11. 🚨 Ditching & Emergency Exit (Plan Geri Dönüş ve Acil Durum Tablosu)

| Belirti / Hata | Olası Neden | Anında Düzeltici Eylem |
|---|---|---|
| `check_aviation_docs.py` `E1` veya `E2` hatası veriyor | Plan veya şablon dosyasında `->` çıktı eşleşmesi ya da `🚨 Ditching & Emergency Exit` tablosu eksik | `python .agent/skills/musgoku/scripts/check_aviation_docs.py` çıktısındaki dosya/satıra `[Adım N]... -> [Beklenen Çıktı]` ve acil çıkış tablosunu ekleyin |
| `test_skills_catalog.py` freshness hatası (`FAIL`) veriyor | `generate_skills_catalog.py` veya `SKILL.md` güncellendi ancak `.agent/skills-catalog.html` yeniden derlenmedi | `python scripts/generate_skills_catalog.py` komutunu çalıştırarak kataloğu güncelleyin |
| `check_agents_parity.py` hedef projelerde sapma bildiriyor | `.agent/AGENTS.md` güncellendi ancak hedef projelere dağıtılmadı | `python delivery.py && python delivery.py --verify` çalıştırarak 4/4 hedef projeyi senkronize edin |
