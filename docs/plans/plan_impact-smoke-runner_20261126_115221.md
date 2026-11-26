# Etki-Odaklı API & Ekran Smoke Test Orkestratörü (`/smoke-test`) Uygulama Planı
<!--
  Kaynak: .agent/templates/PLAN.template.md · Standart: FAA AC 121-24C + /caveman
  Ortam: skillSetWorks (.agent/ tek gerçek kaynak)
-->

> **Hedef Dal / Sürüm:** `main / v1.49.0` · **Tarih:** `2026-11-26`  
> **Standart:** `FAA AC 121-24C Dokümantasyon Standardı + /caveman`  
> **Görevlendirilen Skill'ler:** `smoke-test` *(yeni)*, `verify-last`, `verify-sprint`, `feature-architect` (`fa_scan` / `graph.py`), `test-spec-generator`, `fix-bug`, `tdd`, `musgoku`  
> **Kullanılan MCP'ler:** `second-brain-vault` (`bootstrap`, `get_project_state`), `sequential-thinking`, `TestSprite` *(kota kontrolü & opsiyonel koşum)*, `chrome-devtools-mcp` *(canlı tarayıcı fallback)*  
> **İlgili KANBAN Kartı:** `S2-08` · `GSW-FEAT-024` (Yeni Kart)  
> **Desteklenen Ortamlar:** `Antigravity IDE`, `Antigravity CLI (agy)`, `Claude Code (claude)`, `OpenCode (opencode)`, `Genel Terminal / CLI`

---

## 1. [Goal Description] (Amaç & Kapsam)

Mevcut skillsetimizde `feature-architect` (`fa_scan` + `KnowledgeGraph.impact()` / `consumers()`) etki grafiğini çıkarabiliyor, `test-spec-generator` (`test_spec_tracker.py`) kontrat değişiminde `STALE` / `@smoke` delta paketi ayıklayabiliyor; ancak **bir sprint veya endpoint/özellik geliştirmesi bittiğinde** etkilenen API uç noktalarına ve tüketici ekran rotalarına **otomatik olarak smoke test koşup çalışma zamanı bulgularını (HTTP 500, zarf bozulması, `console.error`, ağ 4xx/5xx, beyaz ekran, kırık boru hattı) yakalayan ve bulduğunda otonom düzelten** bir yürütme halkası yoktur.

Bu planla:
1. Bağımsız **`/smoke-test`** ensemble skill'i (`.agent/skills/smoke-test/`) kurulur (`impact_mapper.py` + `smoke_runner.py`).
2. **Çift Modlu Çalışma (Seçenek A + Seçenek B)** desteklenir:
   - **Seçenek A (Hibrit):** Statik kontrat/KG pipeline analizi + etkilenen hedefli birim/entegrasyon testleri + sunucu ayaktaysa canlı probe.
   - **Seçenek B (Zorunlu Canlı E2E + TestSprite Kota Kalkanı):** Canlı HTTP API probe + Headless UI browser smoke (Playwright / `chrome-devtools-mcp`). TestSprite kredisi varsa/uygunsa TestSprite da koşturulur; **TestSprite limiti bittiğinde veya `Paused`/hata durumunda sistem kesinlikle Seçenek B yerel canlı E2E motoruna otomatik fallback yapar** (sıfır dış bağımlılık kilidi).
3. **`/verify-last`** (anlık/API geliştirme sonu) ve **`/verify-sprint`** (sprint sonu) protokollerine zorunlu Smoke Test aşaması olarak bağlanır.
4. **Bulunca Otonom Fix (`Auto-Remediation Loop`):** Smoke testi bulgu yakaladığında raporlayıp durmaz; kartı `KANBAN.md`'de geri çeker, `HANDOFF.md` §3'e işler, `fix-bug`/`tdd` ile cerrahi onarımı yapar ve re-audit ile `0 bulgu (PASS)` kanıtlanana kadar döngüyü kapatır.

### Kullanıcı Değer Önerisi & Kabul Kriterleri (Gherkin Senaryosu)
```gherkin
# language: tr
Feature: Etki-Odaklı API ve Ekran Smoke Test Orkestratörü

  Scenario: Endpoint değişikliğinde etkilenen API ve tüketici ekranların tespit edilip test edilmesi
    Given Backend controller dosyasında bir endpoint değiştirilmiş veya eklenmiştir
    When Ajan "/verify-last" veya "/smoke-test" çalıştırır
    Then impact_mapper.py KnowledgeGraph üzerinden değişen endpoint'i ve onu çağıran tüm UI ekran rotalarını çıkarır
    And smoke_runner.py Seçenek A (statik kontrat + hedefli testler) ve Seçenek B (canlı HTTP + headless UI) kontrollerini yürütür

  Scenario: TestSprite kota/limit durumunda Seçenek B yerel canlı E2E fallback'inin çalışması
    Given TestSprite hesabı Paused, kredisiz veya limit hatası vermektedir
    When "/smoke-test --live" veya "/verify-sprint" canlı doğrulama başlatır
    Then Sistem TestSprite engeline takılmadan otomatik olarak Seçenek B (yerel HTTP API probe + Playwright/Chrome DevTools UI smoke) çalıştırır
    And Çalışma zamanı bulguları eksiksiz JSON/rapor çıktısına yazılır

  Scenario: Smoke test bulgusu yakalandığında otonom cerrahi onarım döngüsü
    Given smoke_runner.py canlı API 500, UI console.error veya BROKEN_DATA_PIPELINE bulgusu döndürmüştür
    When Doğrulama protokolü bulguyu işler
    Then İlgili KANBAN kartı "Yapıldı" sütunundan geri çekilir ve HANDOFF.md §3'e yazılır
    And Ajan ara onay sormadan fix-bug / tdd ile hatayı onarır ve smoke_runner.py ile sıfır bulgu (PASS) doğrulaması yapar
```

---

## 2. 🏛️ Council Deliberation & Alternatif Yaklaşımlar

| Seçenek | Yaklaşım | Avantajlar (+) | Riskler / Dezavantajlar (-) | Borda Puanı |
|---|---|---|---|:---:|
| **Option A (Saf Hibrit / Statik+Unit)** | Yalnız git diff + KG + birim test; sunucu yoksa atlar | Çok hızlı (~2 sn), dış araç gerektirmez | Canlıda CORS, runtime 500, React crash veya beyaz ekranı yakalayamaz | `2.0` |
| **Option B (Yalnız Zorunlu Canlı E2E / TestSprite)** | Her adımda mutlaka sunucu açıp TestSprite/Playwright koşar | Gerçek tarayıcı + ağ kanıtı verir | TestSprite kredi limiti dolduğunda veya doc-only değişiklikte süreci kilitler | `2.1` |
| **Option C (Çift Modlu A+B + TestSprite Kota Fallback — SEÇİLEN)** | `hybrid` (Option A) her kod/API değişiminde otomatik + `live` (Option B) zorunlu/kapsamlı canlı E2E; TestSprite limitinde yerel Playwright/Chrome DevTools/HTTP fallback | Hem hız hem gerçek runtime garantisi; TestSprite kotasından tamamen bağımsız | İki execution motorunu tek JSON şemasında birleştirmek dikkatli arayüz ister | **`2.9`** |

- **Seçilen Yol & Gerekçe:** Kullanıcı kararı gereği **Option C (Seçenek A + Seçenek B birlikte + TestSprite limitinde kesin Seçenek B yerel E2E fallback)** seçilmiştir. `fa_scan` ve `test_spec_tracker` yeniden kullanılarak kod tekrarı sıfırlanır.

---

## 3. User Review Required (Kullanıcı İncelemesi & Kritik Kararlar)

> [!IMPORTANT]
> **Onay Gerektiren Tasarım Kararları:**
> 1. **Kural Sayısı & Test Uyumu:** `tests/test_rule_gates.py` line 61 (`len(rules) == 22`) sabit sayım yaptığı için `.agent/rules/` altına **23. yeni bir kural dosyası açılmayacaktır**. Smoke kuralları mevcut `sprint-delivery-workflow.md`, `development-workflow.md` ve `skill-trigger-routing.md` içine entegre edilecektir.
> 2. **`run_all_gates.py` Hız Koruması:** `run_all_gates.py` hızlı statik kapı (~2 sn) olarak kalacak; ağır/canlı `smoke_runner.py` koşumu `/verify-last`, `/verify-sprint` ve `/smoke-test` orkestrasyonlarında çalışacaktır (ancak `run_all_gates.py --include-smoke` bayrağı opsiyonel olarak eklenecektir).
> 3. **Kısayol Netleştirme:** Önceki mesajınızda *"2. '/verify-sprint' ve '/verify-sprint' sonunda olsun ayrıca '/smoke-test' de olsun"* ifadesindeki tekrarın **`/verify-last` ve `/verify-sprint`** (artı bağımsız **`/smoke-test`**) olduğunu varsayarak ikisine de entegre ediyorum; farklı bir tercih varsa belirtin.
>
> **2-Modlu Onay Seçenekleri:**
> - **Seçenek A — Mühürle & Sıraya Al (`/seal-plan`):** Planı `docs/plans/`'a arşivler, `HANDOFF.md` + `KANBAN.md` backlog'una ekler, kod yazmaz.
> - **Seçenek B — Onayla & Hemen Başla (`Proceed` / `"onay"`):** Faz 0 arşivlemeden hemen sonra Faz 1 (TDD Kırmızı Test) ile uygulamaya geçer.

---

## 4. Open Questions (Açık Sorular)
- Yok (yalnız §3 madde 3'teki `/verify-last` + `/verify-sprint` teyidi: `Proceed` derseniz ikisine birden entegre edilir).

---

## 5. 📋 Sprint, HANDOFF & KANBAN Durumu (Deterministik Görev Kimlikleri)

| Görev ID (`[DOM]-[TIP]-[NO]`) | Mevcut Durum | Hedef Durum (Proceed Sonrası) | Kapsam / KANBAN Kartı |
|---|---|---|---|
| `GSW-FEAT-024` | `Bekliyor` | `Yapılıyor` → `Yapıldı` | `S2-08` · `impact_mapper.py` + `smoke_runner.py` (Seçenek A+B + TestSprite Fallback) |
| `GSW-FEAT-025` | `Bekliyor` | `Yapılıyor` → `Yapıldı` | `S2-09` · `/smoke-test` skill + `/verify-last` & `/verify-sprint` + Auto-Fix entegrasyonu |
| `GSW-TEST-026` | `Bekliyor` | `Yapılıyor` → `Yapıldı` | `S2-10` · `test_smoke_runner.py`, katalog, `bin/cli.js` profil & `sync_agy_global.py` |

### 5.1 🔗 Kardeş Uygulama (Cross-Repo) Etkisi & Yürütme Sahipliği
`Tek Repo / Kardeş Uygulama Etkisi Yok` *(Not: `skillSetWorks` dağıtım reposudur; değişiklik onaylanıp testler geçtikten sonra yalnızca kullanıcı talebiyle `delivery.py` / `sync_agy_global.py` çalıştırılır.)*

### 5.2 🛡️ Ön-Mühürleme Çakışma, Tekrar ve Sıralı Plan Ezme Matrisi (Pre-Seal Conflict Check)

| Hedef / Yüzey | Sınıflandırma | İlgili Canlı Dosya / Bekleyen Plan | Alınacak Önlem |
|---|---|---|---|
| `.agent/skills/smoke-test/*` | `NEW_CLEAN` | Yok (yeni skill dizini) | `[NEW]` olarak sıfırdan oluşturulur |
| `.agent/skills/verify-last/SKILL.md` | `ENRICHED_SUPERSET` | Canlı dosya mevcut | `[MODIFY]` — mevcut 4 aşama korunur, Smoke aşaması + Auto-Fix eklenir |
| `.agent/skills/verify-sprint/SKILL.md` & `sprint_auditor.py` | `ENRICHED_SUPERSET` | Canlı dosya mevcut | `[MODIFY]` — `--smoke` bayrağı ve canlı smoke aşaması eklenir |
| `scripts/generate_skills_catalog.py` & `bin/cli.js` | `ENRICHED_SUPERSET` | Canlı dosya mevcut | `[MODIFY]` — `smoke-test` ve `/smoke-test` kayıtları eklenir |

---

## 6. 🏗️ 5 Katmanlı Dikey Dilim Mimarisi (Skillset / Meta-Tooling Uyarlaması)

| Katman | Yapılacak İşlem / Değişiklik | İlgili Dosya / Şema |
|---|---|---|
| **1. Envanter & Etki Grafiği (Blast Radius)** | `git diff` / `SPRINT_PLAN` + `fa_scan.run_scan_with_graph()` + `test-spec-state.json` birleşimiyle etkilenen API, UI rotası, modül ve test hedeflerini çıkar | `.agent/skills/smoke-test/scripts/impact_mapper.py` |
| **2. Çift Modlu Yürütme Motoru (A+B)** | **Mod A (Hibrit):** Statik kontrat (`BROKEN_DATA_PIPELINE`, `DTO_CONTRACT_MISMATCH`, `check_api_docs.py`) + hedefli unit/integration test + açık sunucu probu. **Mod B (Canlı E2E + TestSprite Fallback):** HTTP probe + Playwright/Chrome DevTools headless UI smoke + sunucu auto-boot/teardown + TestSprite kredi fallback | `.agent/skills/smoke-test/scripts/smoke_runner.py` |
| **3. Orkestrasyon & Auto-Fix Protokolü** | `/smoke-test` skill'i; `/verify-last` ve `/verify-sprint` içine gömülü Smoke kapısı; bulguda `KANBAN` geri çekme + `HANDOFF` yazma + `fix-bug`/`tdd` otomatik onarım + re-audit döngüsü | `.agent/skills/smoke-test/SKILL.md`, `verify-last/SKILL.md`, `verify-sprint/SKILL.md`, `sprint_auditor.py` |
| **4. Yönlendirme, Katalog & CLI Dağıtımı** | Tetikleyici sözlüğü, geliştirme/sprint kuralları, HTML katalog, `bin/cli.js` profil manifestleri (`frontend`, `backend`, `fullstack`) ve global Antigravity CLI plugin senkronu | `skill-trigger-routing.md`, `sprint-delivery-workflow.md`, `development-workflow.md`, `generate_skills_catalog.py`, `bin/cli.js` |
| **5. Regresyon & Sözleşme Kapısı** | Kırmızı → Yeşil TDD test paketi (`test_smoke_runner.py`), `test_skill_contracts.py`, `test_skills_catalog.py`, `test_rule_gates.py`, `tests/run_all.py` | `tests/test_smoke_runner.py`, `tests/run_all.py` |

---

## 7. 🎨 Tema ve Bileşen İskeleti Sözleşmesi

`Tier 0: Salt Meta-Tooling / CLI & Skillset — UI Kapsam Dışı`  
*(Not: `.agent/skills-catalog.html` güncellemesi mevcut `scripts/generate_skills_catalog.py` jeneratörü üzerinden otomatik üretilecektir.)*

---

## 8. 🧪 TDD Kırmızı-Yeşil Dikiş Noktaları (Seams) ve Sıralı İcra Fazları (FAA AC 121-24C)

### 📌 Faz 0: Onay Sonrası Mühürleme (`docs/plans/`, `HANDOFF.md` §3 & Sprint Açılışı)
1. **[Adım 1 - Ön-Mühürleme Çakışma Kalkanı & Arşiv]:** `python .agent/skills/musgoku/scripts/archive_plan.py --plan <plan-yolu> --slug impact-smoke-runner` -> **Beklenen Çıktı:** `plan_conflict_guard.py` temiz geçer ve `docs/plans/plan_impact_smoke_runner_<TS>.md` oluşur.
2. **[Adım 2 - `HANDOFF.md` §3 & `KANBAN.md` Güncelle]:** `GSW-FEAT-024..026` görevlerini `HANDOFF.md` §3 ve `KANBAN.md`'ye işle -> **Beklenen Çıktı:** `check_handoff.py` ve `check_sprint_board.py` exit `0`.

### 🔴 Faz 1: Dikiş Noktası & Kırmızı Test (Red Loop)
1. **[Adım 1 - Kırmızı Test Yaz & Koştur]:** `tests/test_smoke_runner.py` içinde (a) mock Spring Controller + React Route üzerinde `impact_mapper.py` blast-radius tespiti, (b) yerel Python HTTP test sunucusu + kırık `/api/v1/fail` (`500`) endpoint'i üzerinde `smoke_runner.py --mode live` ile `API_SMOKE_500` bulgu yakalama, (c) TestSprite `quota_exhausted/Paused` simülasyonunda Seçenek B fallback doğrulama testlerini yazıp `python tests/test_smoke_runner.py` çalıştır -> **Beklenen Çıktı:** Henüz kod yazılmadığı için testler **KIRMIZI (FAIL / ImportError)** verir.

### 🟢 Faz 2: Minimal Geçiş Kodu (`impact_mapper.py` & `smoke_runner.py`)
1. **[Adım 1 - `impact_mapper.py` Yaz]:** `fa_scan.run_scan_with_graph()` + `git status/diff` + `KANBAN.md` + `test-spec-state.json` okuyarak etkilenen API endpoint, UI rota ve test dosyalarını çıkaran modülü yaz -> **Beklenen Çıktı:** Impact testi **YEŞİL**.
2. **[Adım 2 - `smoke_runner.py` Yaz]:** Seçenek A (`hybrid`), Seçenek B (`live`), otomatik port/server keşfi (`discovery.py`), HTTP API probe, yerel Playwright/Headless UI probe + Chrome DevTools MCP yönerge çıktısı ve TestSprite kota fallback mantığını yaz; `python tests/test_smoke_runner.py` çalıştır -> **Beklenen Çıktı:** Tüm smoke runner testleri **YEŞİL (PASS)**.

### 🧩 Faz 3: Skill, Kural, Katalog & CLI Entegrasyonu
1. **[Adım 1 - `/smoke-test` Skill & Mevcut Doğrulama Skill Güncellemeleri]:** `.agent/skills/smoke-test/SKILL.md` (25-70 kelimelik sözleşmeli description ile) oluştur; `verify-last/SKILL.md`, `verify-sprint/SKILL.md`, `sprint_auditor.py` ve `run_all_gates.py` entegrasyonlarını yap -> **Beklenen Çıktı:** `test_skill_contracts.py` **PASS**.
2. **[Adım 2 - Yönlendirme, Katalog & CLI]:** `skill-trigger-routing.md`, `sprint-delivery-workflow.md`, `development-workflow.md`, `scripts/generate_skills_catalog.py`, `bin/cli.js` güncelle ve `python scripts/generate_skills_catalog.py` çalıştır -> **Beklenen Çıktı:** `test_skills_catalog.py` ve `test_rule_gates.py` **PASS**.

### 🧹 Faz 4: Tam Regresyon, Global Plugin Senkronu & Kapanış
1. **[Adım 1 - Tüm Repo Test Paketi & Global Plugin Check]:** `python tests/run_all.py` ve `python scripts/sync_agy_global.py` (kullanıcı onayıyla) çalıştır -> **Beklenen Çıktı:** Tüm testler `PASS`, global plugin `goku-dev-skills` senkron, `docs/KULLANICI_TEST_REHBERI.md` güncel.

---

## 9. Proposed Changes (Önerilen Dosya Değişiklikleri)

### Bileşen 1: Yeni `/smoke-test` Becerisi ve Etki-Odaklı Smoke Motoru

#### [NEW] `.agent/skills/smoke-test/SKILL.md`
- **Amaç:** `/smoke-test` bağımsız ensemble becerisinin protokolünü, Seçenek A (Hibrit) + Seçenek B (Canlı E2E + TestSprite Kota Fallback) akışını ve **Bulunca Otonom Cerrahi Onarım (`fix-bug`/`tdd`)** döngüsünü tanımlar.
- **Sözleşme Uyumu:** `description` alanı 25-70 kelime aralığında, `Tetikleyiciler:` (TR+EN) ve `Tetiklenmez:` bölümlerini içerir ve `.agent/rules/skill-trigger-routing.md`'ye atıf yapar.
- **Chrome DevTools MCP Köprüsü:** Eğer hedef ortamda Python/Node Playwright kurulu değilse, `smoke_runner.py --json` çıktısındaki `browser_targets` (etkilenen URL listesi) üzerinde ajanın doğrudan `chrome-devtools-mcp` (`new_page` → `navigate_page` → `list_console_messages` → `list_network_requests` → `take_snapshot`) araçlarıyla canlı UI smoke koşması protokolünü içerir.

#### [NEW] `.agent/skills/smoke-test/scripts/impact_mapper.py`
- **Amaç:** Değişikliklerin patlama yarıçapını (blast radius) deterministik çıkarır.
- **Ana Fonksiyonlar:**
  ```python
  def resolve_changed_files(root: Path, since_ref: str = "HEAD", scope: str = "last") -> list[str]:
      """scope='last': git status --porcelain + HEAD~1..HEAD; scope='sprint': SPRINT_PLAN/KANBAN + recent diff."""

  def map_impact(
      root: Path,
      *,
      scope: str = "last",          # "last" | "sprint" | "all"
      peers: list[str] | None = None,
      endpoint_filter: list[str] | None = None,
      route_filter: list[str] | None = None,
  ) -> dict[str, Any]:
      """fa_scan.run_scan_with_graph() -> KnowledgeGraph.consumers() & impact() ile
      etkilenen endpoint'leri, tüketici UI rotalarını, broken_pipelines bulgularını,
      ilgili test dosyalarını ve test-spec-state.json STALE/FAIL/@smoke senaryolarını döner."""
  ```
- **Çıktı Sözleşmesi:**
  - `affected_endpoints`: `[{method, path, file, line, changed_directly}]`
  - `affected_screens`: `[{route, component, file, consumer_of_endpoint}]`
  - `affected_test_files`: Değişen modül/dosya adına göre eşleşen `*.test.*`, `*.spec.*`, `*Test.java`, `test_*.py` dosyaları
  - `broken_pipelines`: `KnowledgeGraph` üzerinden tespit edilen `BROKEN_DATA_PIPELINE` ve `ApiContractAnalyzer` (`DTO_CONTRACT_MISMATCH`, `API_VERSION_SKEW`) bulguları
  - `delta_scenarios`: `docs/testing/test-spec-state.json` varsa `STALE / FAIL / NEW / @smoke` senaryo ID'leri

#### [NEW] `.agent/skills/smoke-test/scripts/smoke_runner.py`
- **Amaç:** Etki haritası üzerinden Seçenek A + Seçenek B smoke koşumunu icra eden tek CLI motoru.
- **CLI Arayüzü:**
  ```powershell
  python .agent/skills/smoke-test/scripts/smoke_runner.py \
    --root . \
    --scope last|sprint|all \
    --mode auto|hybrid|live \
    --api-url http://localhost:8080 \
    --ui-url http://localhost:5173 \
    --start-cmd "..." \
    --testsprite-status ok|exhausted|paused|skip \
    --json
  ```
- **Çalışma Akışı:**
  1. **Katman 0 — Etki Çözümleme (`impact_mapper.map_impact`):** Değişiklik salt `.md`/`.agent/` ise `SKIPPED` (exit `0`).
  2. **Katman A — Statik Kontrat & Hedefli Testler (Seçenek A — Her Zaman Çalışır):**
     - `BROKEN_DATA_PIPELINE`, `DTO_CONTRACT_MISMATCH`, `API_VERSION_SKEW` kontrolü (`fa_scan`).
     - API dosyası değiştiyse `check_api_docs.py` kontrolü.
     - Tespit edilen `affected_test_files` (veya stack test komutu: `npx vitest run <files>`, `pnpm test -- <files>`, `mvn test -Dtest=...`, `pytest <files>`) hedefli koşulur.
  3. **Katman B — Canlı Runtime Smoke (Seçenek B — HTTP Probe + Browser E2E + TestSprite Kota Kalkanı):**
     - **TestSprite Kota Kontrolü:** `--testsprite-status` veya TestSprite MCP `testsprite_check_account_info` sonucu `credits <= 0` / `Paused` / hata ise **`testsprite_fallback_triggered = True`** kaydedilir ve sistem durmadan **Seçenek B Yerel Canlı E2E** motorunu zorunlu çalıştırır.
     - **Sunucu Keşfi & Opsiyonel Auto-Boot:** `discovery.py` portlarından (`5173`, `3000`, `8080`, `8000` vb.) açık socket probe edilir. `--mode live` iken sunucu kapalıysa ve `--start-cmd` verilmişse geçici arka plan process'i başlatılır, healthcheck beklenir ve `finally` bloğunda temiz kapatılır (`--start-cmd` yoksa `RUNTIME_SERVER_UNAVAILABLE` bulgusu üretilir; `--mode hybrid` modunda ise sunucu kapalıysa `WARN` olarak düşülüp Seçenek A sonuçlarıyla raporlanır).
     - **HTTP API Smoke Probe (`urllib.request`):** Etkilenen `GET` (ve güvenli/read-only veya tanımlı smoke payload'lu) endpoint'lere istek atılır; `5xx` yanıt, beklenmeyen `404` (route handler yokluğu), bozuk JSON veya `unified-api-response-structure` sapması `API_SMOKE_FAIL` bulgusu üretir.
     - **Headless Browser UI Smoke:** Etkilenen UI rotalarına (`affected_screens`) yerel Playwright (`playwright` Python/Node) varsa otomatik headless gezinme yapılır; `page.on("pageerror")`, `console.error`, `response.status >= 400`, boş `document.body.innerText` (beyaz ekran) ve uzun süre takılı kalan skeleton kontrol edilir. Playwright yoksa JSON çıktısında `pending_mcp_browser_checks` listesi üretilir ve ajan `chrome-devtools-mcp` ile aynı rotaları tarar.
  4. **State Senkronu:** `docs/testing/test-spec-state.json` mevcutsa `test_spec_tracker.record_execution_results` ile `PASS`/`FAIL` sonuçları işlenir.
- **Exit Kodları:** `0` = PASS veya SKIPPED (`0` bulgu) · `1` = Bulgu tespit edildi (`FAILED`) · `2` = Araç/argüman hatası.

---

### Bileşen 2: `/verify-last`, `/verify-sprint` ve `run_all_gates.py` Entegrasyonu

#### [MODIFY] `.agent/skills/verify-last/SKILL.md`
- Mevcut Aşama 2 (`Cerrahi Katman ve İkili Eşleme`) sonrasında **Aşama 2.5 — Etki-Odaklı Smoke & Kontrat Doğrulaması (`smoke_runner.py --scope last --mode auto`)** eklenir.
- Aşama 4 (`Bulgu Yönetimi ve Auto-Heal`) içine **Otonom Cerrahi Onarım Zorunluluğu** eklenir: smoke test bulgu yakalarsa ara onay sormadan `fix-bug` / `tdd` ile düzeltip `smoke_runner.py` tekrar koşulur (`0 bulgu` alınmadan commit onayına gidilemez).

#### [MODIFY] `.agent/skills/verify-sprint/SKILL.md` & `.agent/skills/verify-sprint/scripts/sprint_auditor.py`
- `sprint_auditor.py` içine `--smoke` ve `--smoke-mode` (`auto|hybrid|live`) opsiyonel argümanları eklenir; varsayılan (bayraksız) çağrıda `run_all_gates.py` hızı korunur, `--smoke` verildiğinde `smoke_runner.py --scope sprint --mode live` çağrılıp sonuçları `findings` dizisine birleştirir.
- `verify-sprint/SKILL.md` Aşama 2.5 olarak **Sprint Etki-Odaklı Canlı Smoke Testi (`--scope sprint --mode live`)** eklenir (TestSprite limiti varsa otomatik Seçenek B yerel E2E fallback ile). Aşama 5 (`Auto-Remediation Loop`) smoke bulgularını da kapsar ve `Audit Trail` içine smoke sonucu işlenir.

#### [MODIFY] `.agent/skills/musgoku/scripts/run_all_gates.py`
- `--include-smoke` bayrağı eklenir (varsayılan `False` — hızlı kapıları yavaşlatmaz; `--include-smoke` verildiğinde `smoke_runner.py --scope last --mode hybrid` koşar).

---

### Bileşen 3: Kurallar, Tetikleyici Sözlüğü, Katalog ve CLI Profilleri

#### [MODIFY] `.agent/rules/skill-trigger-routing.md`
- §0 Otonom Tetikleme matrisine: API/Endpoint veya sprint bitişinde `smoke-test` (`smoke_runner.py`) tetiklemesi eklenir.
- §A4 / §A5 tablolarına `/smoke-test` (`[SMOKE-TEST]`, `"smoke test koş"`, `"etkilenen ekranları test et"`) ensemble komutu eklenir.
- §D.1 Post-Verification Remediation Matrix tablosuna `/smoke-test` bulgu türleri (`API_SMOKE_500`, `UI_CONSOLE_ERROR`, `BROKEN_DATA_PIPELINE`) ve otonom `fix-bug` yönlendirmesi eklenir.

#### [MODIFY] `.agent/rules/sprint-delivery-workflow.md` & `.agent/rules/development-workflow.md`
- `sprint-delivery-workflow.md` §2.5 ve `development-workflow.md` Adım 4.3'e `/verify-sprint` ve `/verify-last` sonunda `smoke_runner.py` (Seçenek A + Seçenek B + TestSprite Kota Fallback + Otonom Fix) zorunluluğu işlenir.

#### [MODIFY] `scripts/generate_skills_catalog.py` & `.agent/skills-catalog.html`
- `CATEGORIES["Oturum Komutları (Ensemble)"]` içine `"smoke-test"` eklenir.
- `SLASH_COMMANDS` listesine `/smoke-test` komutu eklenir.
- `DOMAINS_MAP` içinde `"accept"` (`Kabul & Doğrulama`) alanına `"/smoke-test"` eklenir.
- `CONFIG_METADATA["smoke-test"]` kaydı eklenir ve `python scripts/generate_skills_catalog.py` ile `.agent/skills-catalog.html` yeniden derlenir.

#### [MODIFY] `bin/cli.js`
- `SKILLS_MANIFEST` içine `'smoke-test'` eklenir.
- `PROFILES.frontend.skills` ve `PROFILES.backend.skills` içine `'smoke-test'` eklenir (`PROFILES.fullstack` otomatik olarak `Object.keys(SKILLS_MANIFEST)` alır).

---

### Bileşen 4: Regresyon Testleri

#### [NEW] `tests/test_smoke_runner.py`
- **Kapsanan Senaryolar:**
  1. `test_impact_mapper_traces_changed_endpoint_to_ui_screen`: Geçici fullstack projede `ProjectController.java` değiştiğinde `impact_mapper.py`'nin hem `/api/v1/projects` endpoint'ini hem onu çağıran `/projects` UI rotasını bulduğunu kanıtlar.
  2. `test_hybrid_mode_catches_broken_pipeline_and_passes_doc_only`: Doc-only projede `SKIPPED` (`exit 0`), kırık client-backend eşleşmesinde `BROKEN_DATA_PIPELINE` (`exit 1`) döndüğünü kanıtlar.
  3. `test_live_mode_catches_api_500_and_passes_200`: Python `http.server` üzerinde sahte API açıp `500` dönen endpoint'te `API_SMOKE_500` bulgusu yakaladığını, fix sonrası `200` döndüğünde `PASS` (`exit 0`) verdiğini kanıtlar.
  4. `test_testsprite_quota_limit_falls_back_to_option_b_live`: `--testsprite-status exhausted` verildiğinde durmadan Seçenek B yerel canlı smoke koşup `testsprite_fallback_triggered=True` raporladığını kanıtlar.
  5. `test_sprint_auditor_with_smoke_flag`: `sprint_auditor.py --smoke` çağrısının smoke bulgusunu sprint denetim raporuna dahil ettiğini doğrular.

#### [MODIFY] `tests/run_all.py`
- `TEST_SCRIPTS` listesine `("Test Smoke Runner", HERE / "test_smoke_runner.py")` eklenir.

---

## 10. Verification Plan (Doğrulama Planı)

### Automated Tests (Otomasyon Testleri)
```powershell
# 1. Yeni smoke runner birim & canlı HTTP/impact testleri
python tests/test_smoke_runner.py

# 2. Skill sözleşme & description testleri
cd .agent/skills/ui-ux-pro-max/scripts/tests && python -m unittest test_skill_contracts

# 3. Katalog üretimi & tazelik kapısı
python scripts/generate_skills_catalog.py
python tests/test_skills_catalog.py

# 4. Kural kapıları & CLI profilleri & Global plugin check
python tests/test_rule_gates.py
python tests/test_cli_profiles.py
python tests/test_agy_global_plugin.py

# 5. Tüm skillSetWorks regresyon paketi
python tests/run_all.py
```

### Manual Verification (Kullanıcı Doğrulama Adımları — FAA AC 121-24C Standardı)
1. **[Adım 1 - Katalog Görünümü]:** `.agent/skills-catalog.html` dosyasını tarayıcıda açıp `Kabul & Doğrulama` hub'ına tıkla -> **Beklenen Çıktı:** `/smoke-test` komutu ve `smoke-test` kartı tüm kullanım örnekleriyle görünür.
2. **[Adım 2 - Canlı Proje Üzerinde `/smoke-test`]:** Bir backend/frontend projesinde (`ocai` veya `FEProjectv1`) `python .agent/skills/smoke-test/scripts/smoke_runner.py --root . --scope last --mode auto` çalıştır -> **Beklenen Çıktı:** Değişen endpoint ve etkilenen ekran rotaları listelenir, Seçenek A/B sonuçları ve varsa bulgular raporlanır.
3. **[Adım 3 - TestSprite Limit Fallback Doğrulaması]:** Aynı komutu `--mode live --testsprite-status exhausted` ile çalıştır -> **Beklenen Çıktı:** TestSprite engeline takılmadan Seçenek B yerel canlı probe/browser smoke çalışır.

---

## 11. 🚨 Ditching & Emergency Exit (Plan Geri Dönüş ve Acil Durum Tablosu)

| Belirti / Hata | Olası Neden | Anında Düzeltici Eylem |
|---|---|---|
| `test_rule_gates.py` 22 kural hatası veriyor | `.agent/rules/` içine yanlışlıkla yeni `.md` kural dosyası eklendi | Yeni kural dosyası eklemeyin; kuralları mevcut `skill-trigger-routing.md` / `sprint-delivery-workflow.md` içine yazın |
| `test_skill_contracts.py` FAIL | `smoke-test/SKILL.md` description <25 veya >70 kelime ya da geçersiz script yolu | `description` kelime sayısını 25-70 arasına çekin, `Tetikleyiciler:` / `Tetiklenmez:` ve `.agent/rules/skill-trigger-routing.md` atfını doğrulayın |
| `test_skills_catalog.py` FAIL | `generate_skills_catalog.py` içindeki `CATEGORIES` / `DOMAINS_MAP` / `CONFIG_METADATA` eksik veya HTML bayat | `python scripts/generate_skills_catalog.py` komutunu çalıştırıp eksik metadata alanını tamamlayın |
| Canlı UI Smoke Playwright bulamıyor | Hedef makinede `playwright` Python/Node paketi kurulu değil | `smoke_runner.py` otomatik `pending_mcp_browser_checks` döner; ajan `chrome-devtools-mcp` ile aynı URL'leri tarar veya `pip install playwright` kurulur |
