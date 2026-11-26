---
name: smoke-test
description: Etki-odaklı API ve ekran smoke test orkestratörü; değişen endpoint ve sprint kapsamındaki tüketici ekranlara hibrit ve canlı smoke koşar, TestSprite limitinde yerel E2E'ye düşer ve bulguları otomatik onarır. Tetikleyiciler: "/smoke-test", "smoke test", "etkilenen ekranları test et", "run smoke test", "api smoke test". Tetiklenmez: statik derleme denetimi verify-last'a, Gherkin spec üretimi test-spec-generator'a aittir. Tam sözlük: .agent/rules/skill-trigger-routing.md
---

# Smoke Test (`/smoke-test` — Etki-Odaklı API & Ekran Smoke Test Orkestratörü)

Bu yetenek, bir **endpoint/API geliştirmesi** veya **sprint** tamamlandığında değişen dosyaların patlama yarıçapını (`impact_mapper.py`) çıkarır; etkilenen backend API uç noktalarına, tüketici UI ekran rotalarına ve hedefli testlere **çift modlu (Seçenek A Hibrit + Seçenek B Canlı E2E)** smoke testi koşar ve bulgu yakaladığında **otonom cerrahi onarım (`fix-bug` / `tdd`)** yürütür.

---

## Ne Zaman Kullanılır?

- Kullanıcı `"/smoke-test"`, *"/smoke-test --live"*, *"etkilenen ekranları test et"* veya *"API smoke test koş"* dediğinde.
- `/verify-last` (anlık/endpoint geliştirme sonu) ve `/verify-sprint` (sprint sonu) akışlarının zorunlu çalışma zamanı / etki doğrulama adımı olarak.

---

## Çift Modlu Protokol (Seçenek A + Seçenek B & TestSprite Kota Kalkanı)

### Aşama 1: Patlama Yarıçapı ve Etki Haritası (`impact_mapper.py`)
```powershell
python .agent/skills/smoke-test/scripts/impact_mapper.py --root . --scope last --json
# Sprint kapsamı için:
python .agent/skills/smoke-test/scripts/impact_mapper.py --root . --scope sprint --json
```
- `fa_scan.run_scan_with_graph()` üzerinden `KnowledgeGraph` + frontend ters import grafiği taranarak değişen endpoint'i tüketen tüm UI rotaları (`/routes`), kırık boru hatları (`BROKEN_DATA_PIPELINE`), DTO sözleşme sapmaları (`DTO_CONTRACT_MISMATCH`) ve hedefli test dosyaları çıkarılır.
- Yalnızca `.md` / `.agent/` değiştiyse `doc_only=True` (`SKIPPED`) döner.

### Aşama 2: TestSprite Kota Kontrolü & Çift Modlu Koşum (`smoke_runner.py`)
1. **TestSprite Kota Kontrolü (Opsiyonel Bulut E2E):** Eğer projede TestSprite kullanılıyorsa önce `testsprite_check_account_info` çağrılır.
   - Kredi/limit varsa ve TestSprite `test_plan` hazırsa `test_spec_tracker.py export-delta --include-smoke` hedefleri koşturulabilir.
   - **⛔ Kota/Limit/Paused Fallback Kilidi:** TestSprite kredisi bitmişse, hesap `Paused` ise veya kota/hata dönerse sistem **asla tıkanmaz**; `--testsprite-status exhausted` ile otomatik olarak **Seçenek B Yerel Canlı E2E** motoruna geçer (`testsprite_fallback_triggered = True`).
2. **Seçenek A (Hibrit) + Seçenek B (Canlı E2E) Koşumu:**
   ```powershell
   # Varsayılan (auto: last -> hybrid, sprint veya limit fallback -> live):
   python .agent/skills/smoke-test/scripts/smoke_runner.py --root . --scope last --mode auto --json

   # Zorunlu Canlı Mod (Seçenek B):
   python .agent/skills/smoke-test/scripts/smoke_runner.py --root . --scope sprint --mode live --api-url http://localhost:8080 --ui-url http://localhost:5173 --json
   ```
   - **Katman A (Statik & Hedefli Test):** `BROKEN_DATA_PIPELINE`, `DTO_CONTRACT_MISMATCH`, `API_VERSION_SKEW` ve değişen modüle ait hedefli birim/entegrasyon testleri (`pytest` / `vitest` / `jest` / `mvn test -Dtest=...`).
   - **Katman B (Canlı HTTP & Browser UI Smoke):**
     * Etkilenen API endpoint'lerine `GET` HTTP probu (`5xx` -> `API_SMOKE_500`, `404` -> `API_SMOKE_404`).
     * Yerel Playwright ile headless UI rota kontrolü (`console.error`, `pageerror`, ağ `5xx`, beyaz ekran / boş body). Playwright kurulu değilse `pending_mcp_browser_checks` listesindeki URL'ler `chrome-devtools-mcp` (`new_page`, `navigate_page`, `list_console_messages`, `list_network_requests`, `take_snapshot`) ile taranır.

### Aşama 3: Bulunca Otonom Cerrahi Onarım (Auto-Remediation Loop)
⛔ **Bulguyu Raporlayıp Durma Yasağı:** `smoke_runner.py` herhangi bir bulgu (`FAILED`, exit `1`) döndürdüğünde:
1. **Pano Mühürleme:** Sprint içindeyse ilgili kart `KANBAN.md` üzerinde `Yapıldı`'dan `Yapılıyor`'a geri çekilir; bulgu `HANDOFF.md` §3 panosuna `1. ⏭️` sıradan eklenir.
2. **Cerrahi Onarım (`fix-bug` / `tdd` / `ui-polish`):** Ajan ara onay sormadan `remediation_skill` alanına göre kırmızı test kurar, hatayı onarır (`500` / `console.error` / `BROKEN_DATA_PIPELINE` / boş ekran).
3. **Re-Smoke & PASS Kanıtı:** `smoke_runner.py` tekrar koşulur; `0 bulgu (PASSED)` alınana kadar döngü kapatılmaz.
4. **Test Defteri Senkronu:** `docs/testing/test-spec-state.json` mevcutsa `test_spec_tracker.py record` ile `PASS`/`FAIL` sonuçları mühürlenir.

---

## Standart Çıktı Raporu (FAA AC 121-24C + `/caveman`)

```markdown
### 🔥 SMOKE-TEST: ETKİ-ODAKLI API & EKRAN DOĞRULAMA RAPORU
- **Kapsam & Mod:** `[last|sprint|all]` · `[hybrid|live]` (TestSprite Fallback: `[Evet/Hayır]`)
- **Etki Yarıçapı:** `[X] endpoint · [Y] ekran rotası · [Z] hedefli test`
- **Sonuç:** `[PASSED / FAILED / SKIPPED]` (`[N]` bulgu)
- **Otonom Onarım & Re-Smoke:** `[Onarılan bulgular veya "Temiz (0 bulgu)"]`
```
