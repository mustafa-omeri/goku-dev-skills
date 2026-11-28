---
name: test-spec-generator
description: >-
  Tüm projeyi (kod, kardeş repo, dokümanlar) artımlı tarayıp Gherkin/AC üreten, PASS defterini (test-spec-state.json) koruyan, TestSprite MCP (/test-spec-run) koşup endpoint hatalarını ilgili repoya adresleyen orkestratör. Tetikleyiciler: "/test-spec", "/test-spec-run", "test spec", "gherkin testleri çıkar", "testsprite ile koş", "generate test spec", "run test spec". Tetiklenmez: sprint denetimi verify-sprint'e, PRD denetimi verify-prd'ye aittir. Tam sözlük: .agent/rules/skill-trigger-routing.md
---

# Test Spec Generator v2 (`/test-spec`)

Bu yetenek; projenin **tüm kaynak kodunu** (rotalar, formlar, backend API uç noktaları, veritabanı modelleri, RBAC yetkileri, kardeş repo) ve **tüm dokümanlarını** (`PRODUCT.md`, `PROJECT_BRIEF.md`, `docs/*prd*`, `docs/APIs/`, `DB_MIGRATIONS.md`, `docs/specs/*.feature`, `HANDOFF.md`) tarayarak **ölçülebilir Acceptance Criteria (`AC-XXX`)** ve **Gherkin (`Feature` / `Background` / `Scenario` / `Scenario Outline` / `Given-When-Then`)** senaryolarını **tek bir dosyada** (`docs/testing/<SLUG>_ACCEPTANCE_TEST_SPEC.md`) üretir.

v2 ile birlikte yetenek **kademeli / artımlı (incremental)** çalışır: daha önce üretilmiş ve `PASS` almış senaryoları gereksiz yere baştan üretmez; `raw_hash` vs `contract_hash` ayrımıyla yalnızca **Major** değişikliklerde ilgili modülü cerrahi olarak günceller, eski `PASS` referanslarını `STALE` durumuna çekerek korur ve **TestSprite / Playwright / Cucumber** için hedefli delta dışa aktarımı (`export-delta`) sunar.

> ⛔ **Sınır Ayrımı:**
> - Mevcut sprint kartlarının kabul denetimi: [`verify-sprint`](../verify-sprint/SKILL.md)
> - Geçmiş kod/PRD retrospektif denetimi: [`verify-prd`](../verify-prd/SKILL.md)
> - Geliştirme öncesi dış PRD analizi: [`review-prd`](../review-prd/SKILL.md)

---

## Ne Zaman Kullanılır?

- Kullanıcı `"/test-spec"`, *"tüm projeyi inceleyip Gherkin testleri ve acceptance criteria çıkar"*, *"TestSprite veya otomatik test araçları için tek bir test dosyası hazırla"* dediğinde.
- Mevcut spesifikasyonda kod/doküman değişikliği sonrası yalnızca etkilenen testlerin güncellenmesi ve önceki `PASS` referanslarının korunması gerektiğinde.

---

## Kademeli (Incremental-First) 5 Aşamalı Protokol

### Aşama 1: Değişiklik Planı ve Envanter Çıkarımı (`plan` vs Bootstrap)
Her çalıştırmada önce artımlı takip motoru koşturulur:

```powershell
# Mevcut test-spec-state.json varsa Major vs Minor fark analizi (Fast-path SHA-256 + KG impact):
python .agent/skills/test-spec-generator/scripts/test_spec_tracker.py plan --root . --state docs/testing/test-spec-state.json --json

# Tam envanter çıktısı gerekirse (ilk kurulum / --peer / --focus):
python .agent/skills/test-spec-generator/scripts/test_spec_scanner.py --root . --json --out docs/testing/test-inventory.json
```
*(Ayrı backend/frontend deposu varsa `--peer <kardeş-repo-yolu>`, zorla modül güncellemek için `--force-module <mod>` eklenir).*

**Sınıflandırma Kuralları (Sıfır Gereksiz Yeniden Üretim):**
- **`NO_OP` / `UNCHANGED` (`SKIP`):** Dosyaların `raw_hash` değeri değişmediyse tarama atlanır; mevcut senaryolar ve `PASS` referansları aynen korunur.
- **`MINOR` (`KEEP`):** Yalnızca CSS/stil, yorum satırı, whitespace, log veya iç yardımcı düzenlemesi (`raw_hash !=`, ama `contract_hash ==`) varsa senaryolar **yeniden üretilmez**, `PASS` durumu korunur.
- **`MAJOR` (`ADD` / `UPDATE` / `DEPRECATE`):** Yeni rota/endpoint/rol/gereksinim eklendiyse, DTO/validasyon/rol kontratı veya KG `impact()` bağımlılığı değiştiyse yalnız etkilenen modül güncellenir. Önceki `PASS` senaryosu `STALE` işaretlenir (`last_pass_ref` kanıtı korunur).

### Aşama 2: Derin Kaynak Kod Okuması & Best Practices Test Tasarımı
Yalnızca **`BOOTSTRAP`** veya **`MAJOR`** işaretlenen modüller için ilgili kaynak kod ve dokümanlar derinlemesine okunur; senaryolar şu mühendislik standartlarıyla tasarlanır:
1. **Risk-Tabanlı Öncelik Katmanlama:** Her senaryoya risk etiketi verilir: `@p0-critical` (Auth, RBAC, ödeme, `DELETE`), `@p1-high` (ana CRUD/E2E), `@p2-medium` (liste/filtre/ayarlar), `@p3-low` (yardımcı görünümler).
2. **Performans, Optimizasyon & Eşzamanlılık (`@perf`, `@sla`, `@pagination`, `@idempotency`, `@concurrency`):**
   - Liste uç noktaları için p95 gecikme hedefi, sayfalama (`limit/pageSize`) üst sınırı ve N+1 regresyon koruması.
   - Mutasyon (`POST`/`PUT`) işlemlerinde çift gönderim **idempotency** ve eşzamanlı düzenleme (`409 Conflict`) senaryoları.
   - Frontend state mutasyonlarında **refresh gerektirmeden UI yansıma** ve **Zero-CLS Skeleton** yükleme durumu.
3. **Sistematik Sınır Değer & Denklik Bölümlendirmesi:** `Scenario Outline` + `Examples` ile min/max uzunluk, boş/null, yetkisiz rol (`401`/`403`), XSS/SQLi ve **Türkçe UTF-8 karakter (`çğıöşüİ`)** girdileri test edilir.
4. **Anti-Flakiness & İzolasyon:** Senaryolar birbirinin bıraktığı veriye bağımlı olamaz; her `Scenario` bağımsız `Background`/benzersiz veri üretir, sabit uyku süresi yerine deterministik API/DOM durumu bekler.

> ⛔ **Totolojik ve Belirsiz Kriter Yasağı:** *"Kullanıcı dostu görünür"*, *"hızlı çalışır"* gibi ölçülemez ifadeler yazılmaz. Her Acceptance Criteria somut değer, durum kodu ve gözlenebilir çıktı içermelidir.

### Aşama 3: Tek Dosya Yazımı veya Cerrahi Modül Yamalama (`patch-module` + `sync`)
- **İlk Kurulum (`BOOTSTRAP`):** [references/test-spec-template.md](references/test-spec-template.md) ve `.agent/templates/ACCEPTANCE_TEST_SPEC.template.md` şablonuna birebir uyularak `docs/testing/<SLUG>_ACCEPTANCE_TEST_SPEC.md` üretilir.
- **Artımlı Güncelleme (`INCREMENTAL`):** Dokunulmayan modüllere ASLA dokunulmaz! Her modül `<!-- TEST-SPEC:MODULE:<mod>:BEGIN --> ... <!-- TEST-SPEC:MODULE:<mod>:END -->` çapaları içinde yaşar; yalnızca `MAJOR` modülün içeriği cerrahi olarak yamalanır ve `next_seq` sayacı monotonik korunur:

```powershell
python .agent/skills/test-spec-generator/scripts/test_spec_tracker.py patch-module --spec docs/testing/<SLUG>_ACCEPTANCE_TEST_SPEC.md --module <mod> --content-file <yeni_modul_md>
python .agent/skills/test-spec-generator/scripts/test_spec_tracker.py sync --root . --spec docs/testing/<SLUG>_ACCEPTANCE_TEST_SPEC.md --state docs/testing/test-spec-state.json
```

### Aşama 4: Deterministik Kapsama, Sözdizimi ve State Kapısı (`check_test_spec.py`)
```powershell
python .agent/skills/test-spec-generator/scripts/check_test_spec.py --spec docs/testing/<SLUG>_ACCEPTANCE_TEST_SPEC.md --inventory docs/testing/test-inventory.json --state docs/testing/test-spec-state.json
```
Denetlenen kurallar:
- `E1..E7`: Zorunlu 6 bölüm, zero-placeholder, geçerli Gherkin (`Feature`/`Scenario`/`Given-When-Then`), `AC-` ID, aktif rota + `METHOD /path` kapsaması, RBAC senaryosu.
- `E8_STATE_DRIFT`: Spec dosyası ile `test-spec-state.json` tam senkron olmalı.
- `E9_STALE_PASS_CLAIM`: Kontratı değişen (`MAJOR`) senaryo hâlâ güncel `PASS` gösterilemez.
- `E10_DUPLICATE_SCENARIO_ID`: Mükerrer `SC-*` kimliği yasaktır.
- `W1..W2`: Negatif/validasyon ve `@perf`/`@pagination`/`@idempotency` kapsama uyarıları.

### Aşama 5: PASS Sonucu İşleme (`record`) ve Delta / Saf `.feature` Dışa Aktarımı
TestSprite, Playwright, Cucumber, JUnit veya manuel doğrulama sonuçları state defterine mühürlenir ve sonraki koşumlarda yalnızca değişen/başarısız testler (`NEW + STALE + FAIL + FLAKY`) dışa aktarılabilir:

```powershell
# 1. PASS/FAIL sonucunu kanıtıyla kaydet (veya --import-testsprite / --import-junit / --import-playwright / --import-cucumber):
python .agent/skills/test-spec-generator/scripts/test_spec_tracker.py record --state docs/testing/test-spec-state.json --result SC-AUTH-01=PASS --runner testsprite --evidence testsprite_tests/report.md

# 2. Yalnızca çalıştırılması gereken Delta paketini çıkar (+ opsiyonel --include-smoke):
python .agent/skills/test-spec-generator/scripts/test_spec_tracker.py export-delta --spec docs/testing/<SLUG>_ACCEPTANCE_TEST_SPEC.md --state docs/testing/test-spec-state.json --out-md docs/testing/<SLUG>_DELTA_TEST_SPEC.md --out-feature docs/specs/<SLUG>_DELTA.feature

# 3. Tam paketi tek saf .feature dosyasına ayıkla:
python .agent/skills/test-spec-generator/scripts/test_spec_scanner.py --export-feature docs/testing/<SLUG>_ACCEPTANCE_TEST_SPEC.md --out docs/specs/<SLUG>_ALL.feature
```

---

### Aşama 6: TestSprite MCP ile Otomatik Koşum, Mühürleme & Hata Adresleme (`/test-spec-run`)

Kullanıcı `/test-spec-run`, *"testleri koş"* veya *"testsprite ile koş"* dediğinde, `/test-spec` sonrası 3 adımı (TestSprite koş → `record` işle → sonraki delta'yı hazırla) otomatik yürütür:

1. `[Adım 1].` **Delta Kontrolü:** `python .agent/skills/test-spec-generator/scripts/test_spec_tracker.py status --state docs/testing/test-spec-state.json --json` çalıştır -> `NEW + STALE + FAIL + FLAKY == 0` ise dur (*"Koşulacak delta senaryo yok"*).
2. `[Adım 2].` **Kota Kontrolü & Fallback:** TestSprite MCP `testsprite_check_account_info` çağır -> Kredi/limit yoksa veya `Paused` ise **deftere dokunma** ve `python .agent/skills/smoke-test/scripts/smoke_runner.py --root . --scope sprint --mode live --testsprite-status exhausted --json` koş (*"TestSprite ATLANDI — defter güncellenmedi"*).
3. `[Adım 3].` **Sunucu & Delta Export:** Yerel UI portunu (`5173`/`4173`) kontrol et; kapalıysa `npm run build && npm run preview` (`serverMode: "production"`, 15 test limitinden kaçınmak için) başlat. Ardından `export-delta` çalıştır.
4. `[Adım 4].` **TestSprite Başlatma & Plan Çevirme:** `testsprite_tests/tmp/config.json` yoksa `testsprite_bootstrap` (`type: "frontend"`, `testScope: "codebase"`), plan yoksa `testsprite_generate_frontend_test_plan` çağır. Sonra delta `SC-*` senaryolarını TestSprite planına yaz:
   ```powershell
   python .agent/skills/test-spec-generator/scripts/testsprite_bridge.py to-plan --spec docs/testing/<SLUG>_ACCEPTANCE_TEST_SPEC.md --state docs/testing/test-spec-state.json --plan testsprite_tests/testsprite_frontend_test_plan.json --json
   ```
   *(Sunucu `development` modundaysa `--batch 15 --batch-index 0` ile partilere böl; orijinal plan `.bak` olarak korunur ve `sc_map.json` üretilir).*
5. `[Adım 5].` **TestSprite Koşumu & Defter Mühürleme:** `testsprite_generate_code_and_execute` (`projectName`, `projectPath`, `testIds: batch_test_ids`, `serverMode`) çalıştır -> ardından `record` ile sonuçları işle:
   ```powershell
   python .agent/skills/test-spec-generator/scripts/test_spec_tracker.py record --state docs/testing/test-spec-state.json --import-testsprite testsprite_tests/tmp/test_results.json --runner testsprite --evidence testsprite_tests/tmp/raw_report.md
   ```
   *(0 sonuç eşleşirse exit `2` döner; sessiz `PASS` kesinlikle yazılmaz).*
6. `[Adım 6].` **Kök Neden Triajı, Otonom Onarım & Kardeş Repo Müdahalesi (`triage` + `fix-bug`):** `FAIL` veya `FLAKY` senaryolar varsa çalıştır:
   ```powershell
   python .agent/skills/test-spec-generator/scripts/testsprite_bridge.py triage --state docs/testing/test-spec-state.json --inventory docs/testing/test-inventory.json --report testsprite_tests/tmp/test_results.json --json
   ```
   - ⛔ **Otonom Kapalı Döngü (`--no-fix` yoksa):** Ajan bulguyu raporlayıp durmaz; `failure_class` sonucuna göre sırayla `ENV_AUTH_SEED` → `FE_DEFECT` → (erişilebilirse) `BE_PEER_DEFECT` için ara onay sormadan `fix-bug` işletir, her iki reponun `HANDOFF.md` / `knowledge-base.md` dosyasını günceller (sandbox engeli varsa `sync_sibling_handoff.py` ile devreder). `NON_UI_OBSERVABLE` senaryolar TestSprite'a geri yollanmaz; hedef API/birim testiyle doğrulanıp `record` edilir.
7. `[Adım 7].` **Hedefli Re-Run (Maks 2 Tur) & Delta Yenileme:** Yalnız onarılan `rerun_eligible_scenarios` alt kümesi `to-plan --scenarios ...` ile TestSprite'ta tekrar koşulur (kota bitmişse `smoke_runner.py` fallback); sonda `export-delta` ile defter mühürlenir.

---

## Standart Çıktı Özeti

İşlem bittiğinde kullanıcıya kısa ve net rapor verilir:
- **Çalışma Modu:** `BOOTSTRAP` | `NO_OP` | `INCREMENTAL` | `RUN (TestSprite)`
- **Tek Dosya & Defter:** `docs/testing/<SLUG>_ACCEPTANCE_TEST_SPEC.md` + `docs/testing/test-spec-state.json`
- **Durum Dağılımı:** `PASS` (korunan) · `STALE` (re-test gereken) · `NEW` · `FAIL` · `FLAKY`
- **Kapı & Triaj Sonucu:** `check_test_spec.py` -> `[PASS]` · `FAIL` varsa repo/dosya/endpoint adresleme listesi
