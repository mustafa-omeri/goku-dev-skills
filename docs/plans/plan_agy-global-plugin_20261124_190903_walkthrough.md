# Walkthrough — Global Antigravity CLI Plugin (`goku-dev-skills` / `S2-22`)

## Yapılan Değişiklikler

1. **Global Senkronizasyon Motoru ([sync_agy_global.py](file:///C:/devtools/myProjectsAreaWS/toolsWS/skillSetWorks/scripts/sync_agy_global.py)):**
   - `skillSetWorks/.agent/` içeriğini `C:\Users\Mustafa\.gemini\config\plugins\goku-dev-skills\` altına tam paket (50 skill + 55 HTML tema, 20 şablon, 22 on-demand kural) olarak kurar.
   - Antigravity'nin `24.000` byte / `20.000` token kural bütçesini korumak için `rules/AGENTS.md` (`5.996` byte) kompakt tutulur (Scope Guard + Path Bridge + On-Demand Kural Haritası); 22 tam kural `references/rules/` altında tutulur.
   - `--check` (dry-run), `--minimal` (temalar hariç), `--dedupe-global-skills` ve `--uninstall` bayraklarını destekler.
2. **CLI Entegrasyonu ([bin/cli.js](file:///C:/devtools/myProjectsAreaWS/toolsWS/skillSetWorks/bin/cli.js)):**
   - `npx goku-dev-skills sync-agy` (`agy-sync`) komutu eklendi.
3. **Birim Testleri & Gherkin ([test_agy_global_plugin.py](file:///C:/devtools/myProjectsAreaWS/toolsWS/skillSetWorks/tests/test_agy_global_plugin.py), [S2-22.feature](file:///C:/devtools/myProjectsAreaWS/toolsWS/skillSetWorks/specs/S2-22.feature)):**
   - 4 birim/CLI testi TDD Red -> Green döngüsüyle yazıldı ve [tests/run_all.py](file:///C:/devtools/myProjectsAreaWS/toolsWS/skillSetWorks/tests/run_all.py) paketine eklendi.
4. **Tekilleştirme & Vault Temizliği:**
   - Gölgeleyen `C:\Users\Mustafa\.gemini\config\skills\git-release-workflow` yedeklenip (`yedekler/global-skills-git-release-workflow-...`) kaldırıldı.
   - `C:\MyBrainZarbulat\MyBrainForDev\.agent` kaldırıldı ve `tools/denetim.py` / `tools/deger-olc.py` eski haline alındı.

## Doğrulama Sonuçları

- `python -X utf8 -m unittest tests/test_agy_global_plugin.py -v` -> `4/4 OK`
- `python -X utf8 scripts/sync_agy_global.py --dedupe-global-skills` -> `[SYNCED] goku-dev-skills v1.45.0 | skills=50, templates=20, on_demand_rules=22, rules/AGENTS.md=5996B, minimal=False`
- `agy plugin validate C:\Users\Mustafa\.gemini\config\plugins\goku-dev-skills --json` -> exit `0` (`components: rules=1, skills=50`; 3 büyük `SKILL.md` gövdesi `>24KB` kesilme uyarısı mevcut)
- `agy plugin list --json` -> `goku-dev-skills` `enabled: true`, 50 skill + `AGENTS.md` aktif
- `python -X utf8 C:\MyBrainZarbulat\MyBrainForDev\tools\denetim.py` -> `636/636`, `0` bozuk, `0` yetim (`kritik sorun yok`)
