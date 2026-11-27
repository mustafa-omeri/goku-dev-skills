---
name: test-spec-run
description: >-
  Mevcut test-spec-generator çıktılarını kod tabanını baştan taramadan TestSprite MCP ile koşan, sonuçları test-spec-state.json defterine mühürleyen ve endpoint hatalarını ilgili repoya adresleyen orkestratör. Tetikleyiciler: "/test-spec-run", "testleri koş", "testsprite ile koş", "run test spec". Tetiklenmez: ilk spec üretimi test-spec-generator'a, etki bazlı smoke smoke-test'e aittir. Tam sözlük: .agent/rules/skill-trigger-routing.md
---

# Test Spec Run (`/test-spec-run` — TestSprite MCP Koşum & Hata Adresleme Orkestratörü)

Bu yetenek, [`test-spec-generator`](../test-spec-generator/SKILL.md) (Aşama 6) ile daha önce üretilen mevcut 6 dosyayı (`*_ACCEPTANCE_TEST_SPEC.md`, `test-spec-state.json`, `test-inventory.json`, `*_DELTA.feature`) **kod tabanını baştan taramadan** (`test_spec_scanner.py` çalıştırmadan) doğrudan TestSprite MCP ile koşar, `PASS/FAIL` sonuçlarını deftere işler ve endpoint hatalarını ilgili backend (`peer`) veya frontend reposuna adresler.

---

## Zorunlu İcra Akışı

1. **`[Adım 1].` Mevcut Defterden Delta Kontrolü (Yeniden Tarama Yok):**
   ```powershell
   python .agent/skills/test-spec-generator/scripts/test_spec_tracker.py status --state docs/testing/test-spec-state.json --json
   ```
   - `NEW + STALE + FAIL + FLAKY == 0` ise dur (*"Koşulacak delta senaryo yok"*).
2. **`[Adım 2].` TestSprite Kota Kontrolü & Fallback:**
   - `testsprite_check_account_info` çağır -> Kredi/limit yoksa veya `Paused` ise **deftere dokunma** ve `python .agent/skills/smoke-test/scripts/smoke_runner.py --root . --scope sprint --mode live --testsprite-status exhausted --json` çalıştır.
3. **`[Adım 3].` Sunucu & TestSprite Plan Çevirme:**
   - Yerel UI portunu (`5173`/`4173`) kontrol et; kapalıysa `npm run build && npm run preview` (`serverMode: "production"`).
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
5. **`[Adım 5].` Endpoint & Kardeş Repo Hata Adresleme (`triage`):**
   - `FAIL` veya `FLAKY` varsa mevcut `test-inventory.json` ile çaprazla:
   ```powershell
   python .agent/skills/test-spec-generator/scripts/testsprite_bridge.py triage --state docs/testing/test-spec-state.json --inventory docs/testing/test-inventory.json --report testsprite_tests/tmp/test_results.json --json
   ```
   - Endpoint takılmalarında kardeş backend (`peer`) vs frontend repo/dosya adresini açıkça raporla (otonom kod düzenlemesi yapma, `/fix-bug` öner).
6. **`[Adım 6].` Delta Yenileme:** `export-delta` çalıştır -> kalan `FAIL` senaryolar sonraki koşuma hazırlanır.
