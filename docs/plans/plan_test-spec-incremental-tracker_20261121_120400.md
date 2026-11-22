# `test-spec-generator` v2 — Kademeli Takip, PASS Referans Defteri & Performans Optimizasyonu Uygulama Planı

> **Hedef Dal / Sürüm:** `main` / `v1.41.0` · **Tarih:** `2026-11-21`  
> **Görevlendirilen Skill'ler:** `test-spec-generator` (v2 yükseltme), `feature-architect` (`fa_scan.py`, `graph.py` `impact()`, `cache.py` SHA-256 deseni), `tdd`, `codebase-design`, `council`, `musgoku`  
> **Kullanılan MCP'ler:** `second-brain-vault` (mimari dersler: Ders E UI yansıma, Ders H UTF-8), `sequential-thinking` (3 aşamalı artımlı mimari tasarım)  
> **İlgili KANBAN Kartı:** `S2-15` (`[GSW]-TSPEC-002`)  
> **Desteklenen Ortamlar:** `Antigravity IDE`, `Antigravity CLI (agy)`, `Claude Code (claude)`, `OpenCode (opencode)`, `Genel Terminal / CLI`

---

## 1. Goal Description (Amaç & Kapsam)

### Mevcut v1.40.0 Sınırları
v1.40.0 sürümündeki `/test-spec` her çalıştırmada tüm projeyi sıfırdan tarıyor ve tek dosyanın tamamını yeniden yazmaya yönlendiriyor:
1. **Gereksiz Yeniden Üretim & Token/Süre İsrafı:** Değişmeyen modüllerin test case'leri her turda baştan yazılır.
2. **Major vs Minor Değişiklik Körlüğü:** CSS/yorum değişikliği (`MINOR`) ile yeni zorunlu alan / endpoint / rol / validasyon değişikliği (`MAJOR`) ayırt edilemez.
3. **PASS Referans ve Tarihçe Kaybı:** Daha önce TestSprite, Playwright, Cucumber, JUnit veya manuel testte `PASS` almış senaryoların hangi commit ve kontrat sürümünde geçtiği tutulmaz.
4. **Sığ Non-Functional Kapsam:** Performans SLA'ları (`p95`), sayfalama/N+1 sınırları, idempotency, eşzamanlılık (`409 Conflict`), sınır değer analizi ve flaky-test önleme desenleri eksik kalır.

### v2 Neyi Başarır?
1. **Kademeli & Artımlı Takip Defteri (`docs/testing/test-spec-state.json`):** Çift katmanlı parmak izi (`raw_hash` + `contract_hash`) ile değişmeyen yüzeyleri `SKIP`, kozmetik değişiklikleri `MINOR (KEEP)`, davranış/kontrat değişikliklerini `MAJOR (ADD / UPDATE / DEPRECATE)` olarak deterministik sınıflandırır.
2. **PASS Referans Defteri (Execution Reference Ledger):** Her `SC-<MOD>-<NN>` senaryosu için `NEW | PASS | STALE | FAIL | FLAKY | DEPRECATED` yaşam döngüsü tutar; `PASS` kayıtlarını `verified_commit + verified_contract_hash + runner + evidence_ref` ile mühürler. Major değişiklik olursa önceki PASS kaydını `last_pass_ref` altında koruyarak senaryoyu `STALE` işaretler.
3. **Delta Export & Cerrahi Modül Yamalama:**
   - Ana dosyada (`ACCEPTANCE_TEST_SPEC.md`) yalnızca `MAJOR` etkilenen modüller `<!-- TEST-SPEC:MODULE:<mod>:BEGIN/END -->` çapalarıyla cerrahi olarak güncellenir.
   - `export-delta` ile TestSprite / Playwright / Cucumber için yalnızca **`NEW + STALE + FAIL`** (+ isteğe bağlı `--include-smoke`) senaryolarını içeren hedefli delta dosyası üretilir.
4. **Best Practices & Performans/Optimizasyon Zenginleştirmesi:** Risk-tabanlı önceliklendirme (`@p0-critical`..`@p3-low`), `@perf` / `@sla` / `@pagination` / `@idempotency` / `@concurrency` şablonları, Boundary Value & Equivalence Partitioning (`Scenario Outline`), UI refresh'siz yansıma (Ders E), Türkçe UTF-8 (Ders H) ve flaky-önleme kuralları + genişletilmiş kapı (`E8..E10`, `W2`).

---

## 2. 🏛️ Council Deliberation & Alternatif Yaklaşımlar

| Seçenek | Yaklaşım | Avantajlar (+) | Riskler / Dezavantajlar (-) | Borda Puanı |
|---|---|---|---|:---:|
| **Option A (Minimal)** | Yalnızca `git diff --name-only` ile değişen dosyaları listele | Az kod | PASS geçmişi tutulamaz; CSS ile Major kontrat ayrılamaz | `1.3` |
| **Option B (Önerilen)** | Git-dostu `docs/testing/test-spec-state.json` defteri + `test_spec_tracker.py` (2 katmanlı `raw_hash`/`contract_hash`, KG `impact()`, PASS referans & çoklu rapor adaptörleri, cerrahi modül yama, `export-delta`) | Sıfır harici bağımlılık, git'te incelenebilir JSON diff, gerçek Major/Minor ayrımı, %70-90 token & koşum tasarrufu | `test_spec_tracker.py` + `check_test_spec.py` v2 entegrasyonu gerektirir | **`2.9`** |
| **Option C (Ağır Altyapı)** | SQLite veritabanı + ayrı web test yönetim paneli | Zengin sorgu | Binary git conflict üretir, overengineering | `1.1` |

- **Seçilen Yol:** **Option B**

---

## 3. Onaylanan Kullanıcı Tercihleri
1. **State Dosyası Konumu:** `docs/testing/test-spec-state.json` (git'te takip edilen, takım/CI/ajanlar arası ortak defter).
2. **Delta Export (`export-delta`):** Varsayılan yalnızca `NEW + STALE + FAIL` (+ `FLAKY`); `--include-smoke` ile `@smoke` etiketli `PASS` testleri eklenebilir.
3. **Rapor Adaptörleri:** CLI `record` + `TestSprite`, `JUnit XML`, `Playwright JSON` ve `Cucumber JSON`.

---

## 4. Proposed Changes (Önerilen Dosya Değişiklikleri)
- **[NEW]** `.agent/skills/test-spec-generator/scripts/test_spec_tracker.py` (`plan`, `sync`, `patch-module`, `record`, `export-delta`, `status` + rapor adaptörleri)
- **[MODIFY]** `.agent/skills/test-spec-generator/scripts/test_spec_scanner.py` (`raw_hash`, `contract_hash`, `risk_tier`, `kg_impact_map` ve `only_scenario_ids` filtresi)
- **[MODIFY]** `.agent/skills/test-spec-generator/scripts/check_test_spec.py` (`--state`, `E8_STATE_DRIFT`, `E9_STALE_PASS_CLAIM`, `E10_DUPLICATE_SCENARIO_ID`, `W2_MISSING_PERF_OR_IDEMPOTENCY`)
- **[MODIFY]** `.agent/skills/test-spec-generator/SKILL.md`, `references/test-spec-template.md`, `.agent/templates/ACCEPTANCE_TEST_SPEC.template.md`
- **[MODIFY]** `scripts/generate_skills_catalog.py` & `.agent/skills-catalog.html`
- **[MODIFY]** `tests/test_test_spec_generator.py` (7 yeni v2 testi)
- **[NEW]** `specs/S2-15.feature` + `KANBAN.md`, `SPRINT_PLAN.md`, `HANDOFF.md`, `PROJECT_BRIEF.md`, `docs/KULLANICI_TEST_REHBERI.md`

---

## 5. Verification Plan
```powershell
python tests/test_test_spec_generator.py
python tests/test_skills_catalog.py
python -m unittest discover -s .agent/skills/ui-ux-pro-max/scripts/tests
python tests/test_rule_gates.py
python .agent/skills/verify-sprint/scripts/sprint_auditor.py
python .agent/skills/musgoku/scripts/run_all_gates.py
```

---

## 6. 🚨 Ditching & Emergency Exit (Geri Dönüş ve Acil Durum Tablosu)

| Belirti / Hata | Olası Neden | Anında Düzeltici Eylem |
|---|---|---|
| `CSS/yorum değişikliği MAJOR sayılıyor` | `contract_hash` ham satırları dahil etmiş | `contract_hash` yalnızca rota, endpoint, rol, validasyon sinyali ve gereksinim metnini hash'leyecek şekilde süzülür. |
| `patch-module diğer modülleri bozdu` | `BEGIN/END` çapaları eksik veya yanlış modül adı verilmiş | `<!-- TEST-SPEC:MODULE:<mod>:BEGIN/END -->` etiketlerini kontrol et; gerekirse git ile geri al. |
| `E8_STATE_DRIFT` veya `E9_STALE_PASS_CLAIM` | Spec güncellendi ancak `sync` çalıştırılmadı | `python .agent/skills/test-spec-generator/scripts/test_spec_tracker.py sync --root . --spec <spec> --state docs/testing/test-spec-state.json` çalıştır. |
