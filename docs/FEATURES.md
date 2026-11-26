# FEATURES.md — skillSetWorks Ürün & Özellik Spesifikasyonu

> Bu dosya `skillSetWorks` (`goku-dev-skills`) paketinin canlı özellik envanterini ve `/verify-prd` retrospektif denetim bulgularını tutar.
> Mimari özet: [`PROJECT_BRIEF.md`](../PROJECT_BRIEF.md) · Sprint Panosu: [`KANBAN.md`](../KANBAN.md) · Oturum Devri: [`HANDOFF.md`](../HANDOFF.md)

## Çekirdek Ürün Bileşenleri

1. **Skill & Kural Kaynağı (`.agent/`):** 52 üretim yeteneği (33 çekirdek + 19 slash orkestratörü), 22 anayasal kural (12 `OLCULEBILIR`, 5 `TUTUM`, 5 `SUREC`), 20 yaşayan şablon, 56 standalone HTML/CSS bileşen teması (`component-themes/`).
2. **Ölçülebilir Doğrulama Kapıları (`.agent/skills/musgoku/scripts/` & domain scriptleri):** `rules_gates.py`, `run_all_gates.py`, `check_handoff.py`, `check_project_brief.py`, `check_sprint_board.py`, `sprint_auditor.py`, `check_design_contract.py`, `check_design_slop.py`, `check_theme_contrast.py`, `check_api_docs.py`, `check_db_migrations.py`, `check_aviation_docs.py`, `check_user_guide.py`, `archive_plan.py`, `plan_conflict_guard.py`, `sync_sibling_handoff.py`, `fa_scan.py`, `smoke_runner.py`, `test_spec_scanner.py`.
3. **Çoklu Araç Dağıtım & CLI Motoru (`bin/cli.js`, `delivery.py`, `scripts/sync_agy_global.py`):**
   - `delivery.py` ile 4 aktif projeye (`ocai`, `FEProjectv1`, `bookmarkManagerProject`, `kalansure`) SHA-256 pariteli `.agent/` dağıtımı.
   - `bin/cli.js` (`goku-dev-skills` v1.49.0): `init`, `update`, `add`, `list`, `info`, `sync-agy`, `sync-opencode`.
   - `scripts/sync_agy_global.py`: Antigravity CLI/IDE global plugin (`~/.gemini/config/plugins/goku-dev-skills/`).
4. **Katalog & Test Altyapısı (`scripts/generate_skills_catalog.py`, `tests/`):**
   - `.agent/skills-catalog.html` interaktif offline kokpiti (52 skill, 24 slash komutu).
   - `tests/run_all.py` (40 kayıtlı paket), `scout/tests/` (50 test), `pytest` (87 test) ve skill-içi `tests/` paketleri.

---

## BULGULAR (DENETİM RAPORU — 2026-11-26 13:37)

### 1. Katman Bütünlüğü Matrisi (Full-Stack Slice Audit)

> Not: `skillSetWorks` uygulama/DB kodu değil kural, skill, CLI ve dağıtım motoru üretir; Katman 1 (DB) ve Katman 2 (Backend/RPC) bu repo bağlamında **Kapsam Dışı** olup, Katman 3 (Script/CLI Motorları), Katman 4 (Katalog HTML / Çıktı / Birim Testleri) ve Katman 5 (Dağıtım / Profil / Test Rehberi Döngü Kapanışı) eksiksiz denetlenmiştir.

| Özellik / Modül (PRD / RFC) | 1. DB / Şema | 2. Backend / RPC | 3. İstemci / CLI & Script | 4. UI / Katalog & Testler | 5. Döngü Kapanışı (Dağıtım / Rehber) | Nihai Hüküm |
|---|---|---|---|---|---|---|
| Çekirdek Kural & Kapı Motoru (`S1-01..S1-05`, `run_all_gates.py`) | ➖ Kapsam Dışı | ➖ Kapsam Dışı | ✅ Var (`11 pass, 6 skip, 0 fail`) | ✅ Var | ✅ Var (`rules_gates` `[OK]`) | ✅ BİTTİ (Tam Dilim) |
| Feature Architect v2.2 & Council (`S2-01, S2-09..S2-13`) | ➖ Kapsam Dışı | ➖ Kapsam Dışı | ✅ Var (`fa_engine`, `council_merger.py`) | ✅ Var (`56/56` + `14/14` benchmark) | ✅ Var | ✅ BİTTİ (Tam Dilim) |
| UI/UX Craft, 88 Palet & Wireframe Gate (`S2-02..S2-04, S2-06, S2-18, S2-21`) | ➖ Kapsam Dışı | ➖ Kapsam Dışı | ✅ Var (`get_palette.py`, `archive_plan.py`) | ✅ Var (`test_theme_bridge` `17/17`, `test_ui_predesign_gate` `6/6`) | ✅ Var (`adaptive-overflow-card-hub` `bin/cli.js`'de eklendi) | ✅ BİTTİ (Tam Dilim) |
| Test Spec Generator v2 (`S2-14..S2-15`) | ➖ Kapsam Dışı | ➖ Kapsam Dışı | ✅ Var (`test_spec_scanner.py`, `tracker.py`) | ✅ Var (`test_test_spec_generator` PASS) | ✅ Var | ✅ BİTTİ (Tam Dilim) |
| POST-Only, Soft-Delete & Spec Reconciler (`S2-17`) | ➖ Kapsam Dışı | ➖ Kapsam Dışı | ✅ Var (`check_api_docs.py` E4/E5/W3) | ✅ Var (`reconcile_scanner` `6/6` PASS) | ✅ Var | ✅ BİTTİ (Tam Dilim) |
| Scout & `diff_triage.py` (`S2-19`) | ➖ Kapsam Dışı | ➖ Kapsam Dışı | ✅ Var (`diff_triage.py`, `50/50` scout test) | ✅ Var (`check_scout_integration` 34/34) | ✅ Var | ✅ BİTTİ (Tam Dilim) |
| Plan Çakışma Kalkanı & `/seal-plan` (`S2-20`, `S2-23`) | ➖ Kapsam Dışı | ➖ Kapsam Dışı | ✅ Var (`plan_conflict_guard.py`, `8/8` PASS) | ✅ Var (`check_handoff` `W4` / `check_sprint_board` `W5`) | ✅ Var (`specs/S2-23.feature` oluşturuldu) | ✅ BİTTİ (Tam Dilim) |
| Global Agy Plugin & OpenCode CLI (`S2-22`, `bin/cli.js`) | ➖ Kapsam Dışı | ➖ Kapsam Dışı | ✅ Var (`cmdInit`/`cmdUpdate` tüm uzantılar) | ✅ Var (`test_cli_profiles` `5/5`, `test_cli_update` `3/3`) | ✅ Var (`frontend`/`backend` profilleri senkron) | ✅ BİTTİ (Tam Dilim) |
| Sprint Doğrulama (`/verify-sprint` & `sprint_auditor.py`) | ➖ Kapsam Dışı | ➖ Kapsam Dışı | ✅ Var (`sprint_auditor.py`) | ✅ Var (`test_sprint_auditor.py` `5/5` + `run_all.py`) | ✅ Var | ✅ BİTTİ (Tam Dilim) |
| Etki-Odaklı Smoke Test (`S2-24`, `smoke-test`) | ➖ Kapsam Dışı | ➖ Kapsam Dışı | ✅ Var (`smoke_runner.py` listener izolasyonu) | ✅ Var (`skills-catalog.html` `v1.49.0`, `7/7` + `40/40`) | ✅ Var (`KULLANICI_TEST_REHBERI` §3.52) | ✅ BİTTİ (Tam Dilim) |

> ✅ **Onarım Kapanış Notu (2026-11-26):** Yukarıdaki 4 Kritik (`GSW-BUG-001..004`) ve 4 İyileştirme (`GSW-IMP-001..004`) bulgusunun tamamı TDD Kırmızı->Yeşil disipliniyle onarılmış ve `tests/run_all.py` (`40/40 PASS`), 15 alt-skill `unittest` dizini (`0` fail) ve `run_all_gates.py` (`11/11` kapsam içi `[OK]`) ile doğrulanmıştır.

### 2. Tespit Edilen Sahte Bitti (Phantom Done), Yetim Bileşenler ve Kırık/Eksik Bağlantılar

- `.agent/skills-catalog.html:4059` (`GSW-BUG-001`): Sürüm `v1.48.0` kalmış (`package.json` `v1.49.0`). `python tests/test_skills_catalog.py` (TEST 5) ve `python tests/run_all.py` bu yüzden **FAIL** veriyor (`1/37` başarısız); `KANBAN.md` `S2-24` ve `HANDOFF.md` §2'deki `37/37 PASS` beyanı sahte yeşil / bayat kayıt durumundadır.
- `.agent/skills/verify-sprint/scripts/tests/test_sprint_auditor.py:69,113` (`GSW-BUG-002`): `sprint_auditor.py` `GSW-GUIDE-001` ile `docs/kullanici-rehberi.html` zorunluluğu kazandıktan sonra test fikstürleri güncellenmediği için `test_02` ve `test_03` **FAIL (2/4)** veriyor. Test paketi `tests/run_all.py` içinde yer almadığı için yetim kalmış ve kırık olduğu gözden kaçmıştır.
- `bin/cli.js:584,622-910,2540` (`GSW-BUG-003`):
  - `COMPONENT_THEMES.menus` içinde `adaptive-overflow-card-hub` eksik (`55` vs diskte `56`).
  - `cmdUpdate()` L2540 `installedTemplates` tespiti yalnızca `.endsWith('.md')` kontrolü yaptığı için `KULLANICI_REHBERI.template.html`, `DEPLOYMENT_TARGET.template.yaml` ve `assets.template.json` şablonlarını güncellemiyor.
  - `PROFILES.frontend` (`45/52` skill, `18/22` rule, `12/20` template) ve `PROFILES.backend` (`27/52` skill, `16/22` rule, `11/20` template) içinde `verify-last`, `verify-sprint`, `spec-reconciler`, `aviation-documentation-standard.md`, `cognitive-counsel-framework.md`, `PLAN.template.md`, `ACCEPTANCE_TEST_SPEC.template.md`, `DEPLOYMENT_PLAN.template.md`, `DEPLOYMENT_TARGET.template.yaml`, `KULLANICI_REHBERI.template.html` eksik.
- `.agent/skills/smoke-test/scripts/smoke_runner.py:218-223` (`GSW-IMP-001`): `_run_playwright_ui_smoke()` içinde `for r in routes:` döngüsü her rota için aynı `page` nesnesine yeni `console`, `pageerror`, `response` listener'ı ekliyor ve temizlemiyor; çoklu rota denetiminde olaylar kümülatif mükerrer sayılır.
- `tests/test_gsap_init.py` (`GSW-IMP-003`): `tests/run_all.py` `TEST_SCRIPTS` listesinde yok (yetim test); ayrıca `brand`, `design-system`, `ui-styling` testleri yalnız `pytest` ile çalışıyor (`unittest discover` 0 test buluyor).

### 3. Doküman-Kod Sapması (Spec Drift) & Test Rehberi Denetimi

- **Dokümanda olup kodda/diskte eksik kalanlar:**
  - `KANBAN.md:43` (`GSW-BUG-004`): `S2-23` kartı `specs/S2-23.feature#gorev-ve-sprint-bazli-multi-ide-telemetriyle-token-takibi` dosyasını referans veriyor ancak `specs/S2-23.feature` diskte yok (`check_sprint_board.py` yalnızca `STARTED_COLUMNS` için kontrol ettiğinden `Bekliyor` sütununda yakalamamış).
  - `README.md:390-392`: `19 Skills` başlığı altında 18 link listelenmiş (`deployment-architect` eksik).
- **Kodda olup dokümante edilmeyenler / Bayat dokümanlar:**
  - `RELEASE_PLAN.md:7,15-39,29,97` (`GSW-IMP-002`): Sürüm `v1.1.0` kalmış (`v1.49.0`); `S2-01..S2-04`, `S2-14`, `S2-15`, `S2-18`, `S2-22` kartları §1 tablosunda eksik; `S2-07` satırında UTF-8 mojibake (`GÃ¼venliÄŸi`) var; §6 hâlâ `4 açık kart (S1-06..S1-09)` diyor.
  - `SPRINT_PLAN.md:73-78,87` (`GSW-IMP-002`): `S1-08` ve `S1-09` hâlâ `Kapsam Dışı` ve taşınan işler altında yazıyor (oysa `KANBAN.md`'de `Yapıldı`).
  - `bin/cli.js:85,576,610,2253,3325` (`GSW-IMP-004`): Hardcoded eski sayılar (`40 skills`, `50 skills`, `55 themes`).
  - `HANDOFF.md:766,772-775`: `Sağlık durumu` ve `Nasıl Test Edilir` bölümlerinde eski `v1.29.0` ve `30/30` test adımı notları kalmış.
- **`docs/KULLANICI_TEST_REHBERI.md` denetimi:** `§3.1..§3.52` güncel (`S2-24` dahil) ve `check_aviation_docs.py` `[OK]`. Ancak `§3.52` Adım 3'te beklenen `tests/run_all.py` tam yeşil durumu `GSW-BUG-001` çözülene kadar sağlanmıyor.

### 4. Düzeltme & Tamamlama Eylem Planı (Action Items)

- **🔴 Kritik (Katman Eksikleri, Kırık Test Ortamı & Sahte Bitti Düzeltmeleri):**
  1. `GSW-BUG-001` — `python scripts/generate_skills_catalog.py` çalıştırarak `.agent/skills-catalog.html`'i `v1.49.0` ile yeniden derle; `tests/test_skills_catalog.py` ve `tests/run_all.py` (37/37) tam yeşil doğrula ve 4 hedef projeye `delivery.py` senkronunu kontrol et.
  2. `GSW-BUG-002` — `.agent/skills/verify-sprint/scripts/tests/test_sprint_auditor.py` içindeki `test_02` ve `test_03` testlerini `docs/kullanici-rehberi.html` gereksinimine göre güncelle (4/4 PASS) ve `tests/run_all.py` `TEST_SCRIPTS` listesine bağla.
  3. `GSW-BUG-003` — `bin/cli.js` içinde `COMPONENT_THEMES.menus`'e `'adaptive-overflow-card-hub'` ekle, `cmdUpdate()` `installedTemplates` filtresini `.md/.html/.yaml/.json` kapsayacak şekilde düzelt, `PROFILES.frontend` ve `PROFILES.backend` listelerini çekirdek doğrulama/planlama skill (`verify-last`, `verify-sprint`, `spec-reconciler`), kural (`aviation-documentation-standard.md`, `cognitive-counsel-framework.md`) ve şablonlarıyla (`PLAN.template.md`, `KULLANICI_REHBERI.template.html`, `ACCEPTANCE_TEST_SPEC.template.md`, `DEPLOYMENT_PLAN.template.md`, `DEPLOYMENT_TARGET.template.yaml`) senkronize et ve `tests/test_cli_update.py` + `tests/test_cli_profiles.py` ile doğrula.
  4. `GSW-BUG-004` — `specs/S2-23.feature` dosyasını oluştur (`KANBAN.md:43` ve `docs/plans/council_plan_token-cost-tracking_20261125_105503.md` ile uyumlu Given-When-Then senaryosu).
- **🟡 İyileştirme (Ayarlar, Doküman Senkronu & Kalite Hijyeni):**
  1. `GSW-IMP-001` — `.agent/skills/smoke-test/scripts/smoke_runner.py` L218-223 `_run_playwright_ui_smoke` içinde listener'ları rota başına `page.remove_listener` veya yeni page oluşturarak izole et; `tests/test_smoke_runner.py`'ye çoklu rota regresyon testi ekle.
  2. `GSW-IMP-002` — `RELEASE_PLAN.md` (`v1.49.0`, eksik `S2-*` kartları, `S2-07` mojibake temizliği, §2 ve §6 tutarlılığı) ve `SPRINT_PLAN.md` (`S1-08`/`S1-09` durumu) dosyalarını `KANBAN.md` ile tam senkronize et.
  3. `GSW-IMP-003` — `tests/test_gsap_init.py`'yi `tests/run_all.py` orkestratörüne ekle ve `brand`/`design-system`/`ui-styling` `pytest` testlerini tek komutta koşturacak köprüyü netleştir.
  4. `GSW-IMP-004` — `bin/cli.js` hardcoded eski sayı yorum/metinlerini (`40 skills`, `50 skills`, `55 themes`), `README.md:392` eksik `deployment-architect` bağlantısını ve `HANDOFF.md` §3'teki eski `v1.29.0` / `30/30` metinlerini güncelle.
