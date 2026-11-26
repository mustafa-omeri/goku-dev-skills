# Walkthrough — Etki-Odaklı API & Ekran Smoke Test Orkestratörü (`/smoke-test`, `S2-24`)

## Yapılan Değişiklikler

1. **Patlama Yarıçapı & Etki Çözümleyici ([impact_mapper.py](file:///C:/devtools/myProjectsAreaWS/toolsWS/skillSetWorks/.agent/skills/smoke-test/scripts/impact_mapper.py)):**
   - `fa_scan.run_scan_with_graph()` üzerinden `Endpoint`, `HttpCall`, `Component` ve `Route` düğümlerini ve `KnowledgeGraph` + frontend ters import grafiğini tarar.
   - Değişen controller/endpoint/dosyalardan etkilenen API uç noktalarını, tüketici UI ekran rotalarını, kırık boru hatlarını (`BROKEN_DATA_PIPELINE`), DTO sözleşme sapmalarını (`DTO_CONTRACT_MISMATCH`), hedefli test dosyalarını ve `test-spec-state.json` delta senaryolarını deterministik çıkarır (`doc_only` değişikliklerde `SKIPPED` döner).

2. **Çift Modlu Smoke Runner ([smoke_runner.py](file:///C:/devtools/myProjectsAreaWS/toolsWS/skillSetWorks/.agent/skills/smoke-test/scripts/smoke_runner.py)):**
   - **Seçenek A (Hibrit):** Statik kontrat/KG pipeline analizi + hedefli birim/entegrasyon testleri (`pytest`/`vitest`/`jest`/`mvn`) + sunucu açıksa canlı probe.
   - **Seçenek B (Canlı E2E + TestSprite Kota Fallback):** Canlı HTTP API probe (`API_SMOKE_500`, `API_SMOKE_404`) + yerel headless browser UI smoke (Playwright veya `chrome-devtools-mcp` için `pending_mcp_browser_checks`). TestSprite kredisi bitmiş/Paused (`--testsprite-status exhausted`) durumunda otomatik olarak Seçenek B yerel canlı E2E'ye fallback yapar.

3. **Bağımsız Skill & Doğrulama Entegrasyonları:**
   - Yeni ensemble beceri: [smoke-test/SKILL.md](file:///C:/devtools/myProjectsAreaWS/toolsWS/skillSetWorks/.agent/skills/smoke-test/SKILL.md) (`/smoke-test`)
   - [verify-last/SKILL.md](file:///C:/devtools/myProjectsAreaWS/toolsWS/skillSetWorks/.agent/skills/verify-last/SKILL.md) (Aşama 2.5 + Otonom Fix Döngüsü)
   - [verify-sprint/SKILL.md](file:///C:/devtools/myProjectsAreaWS/toolsWS/skillSetWorks/.agent/skills/verify-sprint/SKILL.md) & [sprint_auditor.py](file:///C:/devtools/myProjectsAreaWS/toolsWS/skillSetWorks/.agent/skills/verify-sprint/scripts/sprint_auditor.py) (`--smoke` / `--smoke-mode`)
   - [run_all_gates.py](file:///C:/devtools/myProjectsAreaWS/toolsWS/skillSetWorks/.agent/skills/musgoku/scripts/run_all_gates.py) (`--include-smoke`)
   - Kurallar, Katalog (`52 skill, 24 slash komutu`), `bin/cli.js` (`backend`, `frontend`, `fullstack`) ve `tests/test_smoke_runner.py`.

## Doğrulama Sonuçları
- `python tests/test_smoke_runner.py`: **5/5 PASS** (etki grafiği, doc-only skip, `BROKEN_DATA_PIPELINE`, canlı HTTP `500 -> 200`, TestSprite kota fallback, `sprint_auditor --smoke`)
- `python tests/test_skills_catalog.py`: **8/8 PASS** (`52` skill, `24` slash komutu)
- `python -m unittest discover -s .agent/skills/ui-ux-pro-max/scripts/tests -p "test_skill_contracts.py"`: **11/11 PASS**
- `python tests/test_rule_gates.py`: **PASS**
- `python tests/test_cli_profiles.py`: **3/3 PASS**
- `python tests/run_all.py`: Final koşum ile doğrulanacak.
