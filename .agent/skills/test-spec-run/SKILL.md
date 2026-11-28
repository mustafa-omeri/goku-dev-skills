---
name: test-spec-run
description: >-
  Mevcut test-spec-generator çıktılarını taramadan TestSprite MCP ile koşan, FAIL bulgularını sınıflandırıp frontend ve kardeş repoda otonom onaran kapalı döngü orkestratörü. Tetikleyiciler: "/test-spec-run", "testleri koş", "testsprite ile koş", "run test spec". Tetiklenmez: ilk spec üretimi test-spec-generator'a, etki bazlı smoke smoke-test'e aittir. Tam sözlük: .agent/rules/skill-trigger-routing.md
---

# Test Spec Run (`/test-spec-run` — Otonom TestSprite MCP Koşum, Triaj & Onarım Orkestratörü)

Bu yetenek, [`test-spec-generator`](../test-spec-generator/SKILL.md) (Aşama 6) ile daha önce üretilen mevcut 6 dosyayı (`*_ACCEPTANCE_TEST_SPEC.md`, `test-spec-state.json`, `test-inventory.json`, `*_DELTA.feature`) **kod tabanını baştan taramadan** (`test_spec_scanner.py` çalıştırmadan) TestSprite MCP ile koşar, `PASS/FAIL` sonuçlarını deftere işler, bulguları kök neden sınıfına göre **otonom onarır** (`fix-bug` / `tdd`) ve yalnızca onarılan senaryolarda **kredi korumalı bounded re-run** yürütür.

> 💡 **Opsiyonel Salt-Rapor Modu (`--no-fix`):** Kullanıcı açıkça *"sadece raporla / düzeltme yapma"* (`--no-fix`) derse Adım 6–7 atlanır ve yalnızca `triage` adresi raporlanır.

---

## Zorunlu Otonom Kapalı Döngü Akışı (`max_cycles = 2`)

1. **`[Adım 1].` Mevcut Defterden Delta Kontrolü (Yeniden Tarama Yok):**
   ```powershell
   python .agent/skills/test-spec-generator/scripts/test_spec_tracker.py status --state docs/testing/test-spec-state.json --json
   ```
   - `NEW + STALE + FAIL + FLAKY == 0` ise dur (*"Koşulacak delta senaryo yok — tümü PASS"*).
2. **`[Adım 2].` TestSprite Kota Kontrolü & Fallback:**
   - `testsprite_check_account_info` çağır -> Kredi/limit yoksa veya `Paused` ise **deftere dokunma** ve `python .agent/skills/smoke-test/scripts/smoke_runner.py --root . --scope sprint --mode live --testsprite-status exhausted --json` çalıştır.
3. **`[Adım 3].` Sunucu & TestSprite Plan Çevirme:**
   - Yerel UI portunu (`5173`/`4173`) ve varsa kardeş backend sağlık ucunu kontrol et; UI kapalıysa `npm run build && npm run preview` (`serverMode: "production"`).
   - `testsprite_tests/tmp/config.json` yoksa `testsprite_bootstrap` (`type: "frontend"`, `testScope: "codebase"`), plan yoksa `testsprite_generate_frontend_test_plan` çağır (varsa mevcut yapı korunur).
   - Mevcut `ACCEPTANCE_TEST_SPEC.md` ve `test-spec-state.json` üzerinden TestSprite planını güncelle:
   ```powershell
   python .agent/skills/test-spec-generator/scripts/testsprite_bridge.py to-plan --spec docs/testing/<SLUG>_ACCEPTANCE_TEST_SPEC.md --state docs/testing/test-spec-state.json --plan testsprite_tests/testsprite_frontend_test_plan.json --json
   ```
   *(Dev sunucuda `--batch 15 --batch-index 0` eklenir; eski plan `.bak` olarak korunur).*
4. **`[Adım 4].` Koşum & Sonuç Mühürleme (`record`):**
   - `testsprite_generate_code_and_execute` (`projectName`, `projectPath`, `testIds: batch_test_ids`, `serverMode`) çalıştır.
   - Sonuçları deftere işle:
   ```powershell
   python .agent/skills/test-spec-generator/scripts/test_spec_tracker.py record --state docs/testing/test-spec-state.json --import-testsprite testsprite_tests/tmp/test_results.json --runner testsprite --evidence testsprite_tests/tmp/raw_report.md
   ```
5. **`[Adım 5].` Kök Neden Sınıflandırması & Kardeş Repo Adresleme (`triage`):**
   - `FAIL` veya `FLAKY` varsa `triage` koştur:
   ```powershell
   python .agent/skills/test-spec-generator/scripts/testsprite_bridge.py triage --state docs/testing/test-spec-state.json --inventory docs/testing/test-inventory.json --report testsprite_tests/tmp/test_results.json --json
   ```
   - `triage` her `FAIL` senaryoyu 4 sınıfa ayırır: `ENV_AUTH_SEED`, `NON_UI_OBSERVABLE`, `FE_DEFECT`, `BE_PEER_DEFECT` (veya `BE_DEFECT`).
6. **`[Adım 6].` ⛔ Bulguyu Raporlayıp Durma Yasağı — Otonom Cerrahi Onarım (`fix-bug` / `tdd`):**
   `--no-fix` verilmediyse ajan ara onay beklemeden aşağıdaki sırayla ilerler:
   - **6a. `ENV_AUTH_SEED` (Öncelik 1):** Seed/RBAC/credential veya kapalı servis kök nedenini [`fix-bug`](../fix-bug/SKILL.md) ile çöz (tek kök neden birden çok `SC-*` kilidini açar).
   - **6b. `FE_DEFECT` (Birincil Repo):** `fix-bug` (Kırmızı test -> minimal düzeltme -> Yeşil + `tsc`/test) uygula.
   - **6c. `BE_PEER_DEFECT` (Kardeş Backend `peer` Repo):** Kardeş repo diskte erişilebilir ve yazılabiliyorsa ajan doğrudan kardeş repoda `fix-bug` + backend test/build/restart yürütür; her iki reponun `HANDOFF.md` ve `knowledge-base.md` dosyalarını günceller. Yalnızca sandbox/erişim engeli varsa `python .agent/skills/musgoku/scripts/sync_sibling_handoff.py` ile kardeş `HANDOFF.md`'ye yazar ve durma nedenini açıkça raporlar.
   - **6d. `NON_UI_OBSERVABLE` (`TEST BLOCKED` / API-Only / RBAC-Hidden):** ⛔ **TestSprite'a geri yollama!** Bunları hedef API/birim/Playwright-API testiyle doğrula (API kırığı varsa `fix-bug` ile çöz) ve sonucu doğrudan mühürle:
     ```powershell
     python .agent/skills/test-spec-generator/scripts/test_spec_tracker.py record --state docs/testing/test-spec-state.json --result SC-XXX=PASS --runner vitest --evidence <test-komutu-ve-cikti>
     ```
7. **`[Adım 7].` Kredi Korumalı Hedefli Re-Run (Devre Kesici: `max_cycles = 2`) & Delta Yenileme:**
   - Yalnız kodu/ortamı gerçekten onarılan `rerun_eligible_scenarios` listesi için FE build (`npm run build && preview`) / BE restart yenile, `testsprite_check_account_info` kontrol et ve alt kümeyi yeniden koş:
     ```powershell
     python .agent/skills/test-spec-generator/scripts/testsprite_bridge.py to-plan --spec docs/testing/<SLUG>_ACCEPTANCE_TEST_SPEC.md --state docs/testing/test-spec-state.json --plan testsprite_tests/testsprite_frontend_test_plan.json --scenarios SC-ADM-02,SC-ADM-04 --json
     ```
   - `testsprite_generate_code_and_execute` -> `record` tekrar koş. Maksimum **2 re-run turu** sonunda hâlâ `FAIL` kalan senaryolar varsa sonsuz döngüye girmeden son `export-delta` çalıştır, kalan `FAIL` nedenlerini ve kanıtlarını raporla (*Not: Commit/push için yine kullanıcı onayı beklenir*).
