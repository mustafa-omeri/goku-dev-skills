# `/test-spec-run` — TestSprite MCP ile Otomatik Koşum & PASS Mühürleme Planı

> **Hedef Dal / Sürüm:** `main` · **Tarih:** `2026-11-27`
> **Standart:** `FAA AC 121-24C Dokümantasyon Standardı + /caveman`
> **Görevlendirilen Skill'ler:** `council`, `karpathy-guidelines` (`council_ranker.py`), `test-spec-generator`, `smoke-test`, `tdd`
> **Kullanılan MCP'ler:** `second-brain-vault` (`bootstrap`), `TestSprite` (şema incelemesi: `testsprite_bootstrap`, `testsprite_generate_frontend_test_plan`, `testsprite_generate_code_and_execute`, `testsprite_check_account_info`)
> **İlgili KANBAN Kartı:** Yeni Kart (`TSG-FEAT-001`)
> **Desteklenen Ortamlar:** `Antigravity IDE`, `Antigravity CLI (agy)`, `Claude Code (claude)`, `OpenCode (opencode)`

---

## 1. Amaç & Kapsam

`/test-spec-generator` sonrası 3 manuel adım var:
1. Testleri TestSprite ile koş.
2. Raporu `record` ile `test-spec-state.json` defterine yaz.
3. Sonraki değişimde yalnız delta'yı koş.

Hedef: Bu 3 adımı **tek komutla** (`/test-spec-run`) TestSprite MCP üzerinden otomatik yapmak.

### Neden `/smoke-test` bu işi görmüyor? (Kod kanıtı)

| Konu | `/smoke-test` (bugün) | İhtiyaç |
|---|---|---|
| Ne test edilir | Değişen dosyaların etki yüzeyi (`impact_mapper.py`) | Spec'teki `SC-*` Gherkin senaryoları |
| TestSprite | Yalnız kota kontrolü; `smoke_runner.py` MCP çağıramaz ([smoke_runner.py#L301-L311](file:///C:/devtools/myProjectsAreaWS/toolsWS/skillSetWorks/.agent/skills/smoke-test/scripts/smoke_runner.py#L301-L311)) | `generate_code_and_execute` ile gerçek koşum |
| Canlı probe | Yalnız `GET` + konsol/boş ekran | Senaryo bazlı E2E (form, RBAC, 403...) |
| Defter | `record` yalnız metinde geçiyor | `SC-*` → `PASS/FAIL` mühürleme |

Sonuç: `/smoke-test` **fallback** olarak kalır, ana iş için uygun değil.

### Kritik teknik boşluk (bugünkü kod)

- [`parse_testsprite_report`](file:///C:/devtools/myProjectsAreaWS/toolsWS/skillSetWorks/.agent/skills/test-spec-generator/scripts/test_spec_tracker.py#L639-L653) **aynı satırda** hem `SC-*` hem `PASS/FAIL` arıyor.
- TestSprite kendi plan dosyasını ve kendi test kimliklerini (`TC001`...) üretir; raporda durum genelde ayrı satırdadır.
- Bu yüzden bugünkü komut büyük olasılıkla `Recorded 0 results` döner. Köprü bu boşluğu kapatır.

### Kabul Kriterleri

```gherkin
Feature: /test-spec-run TestSprite otomatik koşum
  Scenario: Delta senaryolar TestSprite ile koşulup defter güncellenir
    Given docs/testing/test-spec-state.json içinde NEW durumunda 59 senaryo vardır
    And yerel uygulama sunucusu çalışmaktadır ve TestSprite kredisi vardır
    When kullanıcı "/test-spec-run" komutunu verir
    Then TestSprite planı yalnız delta SC-* senaryolarından oluşur
    And testsprite_generate_code_and_execute koşulur
    And "test_spec_tracker.py status" çıktısında NEW sayısı 0 olur, her senaryo PASS veya FAIL olur

  Scenario: TestSprite kotası bittiğinde dürüst fallback
    Given testsprite_check_account_info kredi yok veya Paused döner
    When kullanıcı "/test-spec-run" komutunu verir
    Then defterdeki SC-* durumları değiştirilmez
    And smoke_runner.py --mode live --testsprite-status exhausted koşulur
    And raporda "TestSprite ATLANDI — defter güncellenmedi" yazar
```

---

## 2. 🏛️ Council Deliberation

| Seçenek | Yaklaşım | Avantajlar (+) | Riskler (-) | Ort. Derece |
|---|---|---|---|:---:|
| **Option A** | `/smoke-test`'e `--spec` modu ekle | Mevcut komut, yeni isim yok | `smoke_runner.py`'a ikinci sorumluluk; etki-odaklı amacı bulanıklaşır; Python MCP çağıramaz, yine ajan akışı gerekir | 2.25 |
| **Option B** | `test-spec-generator` içine **Aşama 6** + tek köprü dosyası `testsprite_bridge.py`; komut `/test-spec-run` | SC-ID, defter, `export-delta`, `record` zaten burada; tek yeni dosya; tek sahip | Yeni tetik kelimesi ekleniyor | **1.25** ✅ |
| **Option C** | Ayrı tam orkestratör skill (`/acceptance-run`): sunucu yaşam döngüsü, otonom onarım, CI | En çok otomasyon | Mükerrer skill; onaysız kod onarımı riski; over-engineering | 2.50 |

**Borda (4 hakem: Bakım, Mimari Uyum, Risk, Hedef Tamlığı):** B = 3 birincilik · C = 1 birincilik (yalnız Hedef Tamlığı) · A = 0.

- **Seçilen Yol:** **Option B.**
- **A neden elendi:** `smoke-test` değişen dosya odaklı; Gherkin defteri ona ait değil. İki sahip = drift.
- **C neden elendi:** Kullanıcı açıkça "over-engineering yapma" dedi. Otonom onarım ve sunucu yönetimi şu an ihtiyaç değil.
- **Kabul edilen ödünleşim:** FAIL çıkan senaryolar otomatik onarılmaz; rapor + `/fix-bug` önerisi verilir.

---

## 3. User Review Required

> [!IMPORTANT]
> - **TestSprite plan JSON şeması doğrulanmadı.** Köprü, TestSprite'ın ürettiği `testsprite_tests/testsprite_frontend_test_plan.json` dosyasını SC-* senaryolarıyla yeniden yazacak. Dosya formatı Faz 1 Adım 1'de FEProjectv1'deki **gerçek dosyadan** doğrulanacak; tahminle kod yazılmayacak.
> - **Dev sunucu limiti:** TestSprite `development` modda frontend testlerini **15 ile sınırlıyor**. 59 senaryo için ya `npm run build && npm run preview` (`serverMode: production`) ya da 15'lik partiler gerekir. Varsayılan: production preview, olmazsa 15'lik parti.
> - **Otonom onarım YOK.** FAIL'ler raporlanır; onarım kullanıcı onayıyla `/fix-bug`.
>
> **2-Modlu Onay:**
> - **Seçenek A — Mühürle (`/seal-plan`):** Plan `docs/plans/`'a arşivlenir, kod yazılmaz.
> - **Seçenek B — Onayla & Başla (`Proceed`):** Faz 0 → Faz 1 TDD.

## 4. Open Questions

1. FEProjectv1 tam yolu nedir ve içinde daha önce TestSprite koşturuldu mu (`testsprite_tests/tmp/config.json` var mı)? Faz 1 Adım 1 için gerçek plan/rapor dosyası lazım.
2. Kardeş backend `../ocai` endpoint senaryoları da TestSprite **backend** testi olarak koşulsun mu? (Varsayılan: hayır, yalnız frontend; `--type backend` sonra eklenir.)
3. Plugin kopyası (`C:/Users/Mustafa/.gemini/config/plugins/goku-dev-skills/skills/`) bu değişiklik sonrası `/gs-update` ile mi senkronlansın?

---

## 5. 📋 Görev Kimlikleri

| Görev ID | Mevcut | Hedef | Kapsam |
|---|---|---|---|
| `GSW-FEAT-027` | `Bekliyor` | `Yapılıyor` | `testsprite_bridge.py` (`to-plan` + `triage` ile `peer` repo/endpoint hata adresleme) |
| `GSW-BUG-006` | `Bekliyor` | `Yapılıyor` | `parse_testsprite_report` blok bazlı + `test_results.json` + `sc_map.json` eşleme |
| `GSW-DOCS-001` | `Bekliyor` | `Yapılıyor` | SKILL.md Aşama 6, routing tetikleri, `smoke-test` referansı, katalog ve plugin senkronu |

### 5.1 Kardeş Uygulama Etkisi
- `Tek Repo / Kardeş Uygulama Etkisi Yok` (değişiklik yalnız `skillSetWorks` skill setinde). FEProjectv1 yalnız doğrulama ortamı.

### 5.2 Ön-Mühürleme Çakışma Matrisi

| Hedef | Sınıflandırma | İlgili | Önlem |
|---|---|---|---|
| `test_spec_tracker.py::parse_testsprite_report` | `ENRICHED_SUPERSET` | Canlı kod | Eski tek-satır davranışı fallback olarak korunur |
| `smoke-test/SKILL.md` Aşama 2 | `SHARED_SURFACE_OVERWRITE` | Canlı doküman | Yalnız `export-delta` cümlesi `/test-spec-run`'a yönlendirilir |
| `testsprite_bridge.py` | `NEW_CLEAN` | — | — |

---

## 6. 🏗️ Katman Haritası (Araç/CLI işi)

| Katman | İşlem | Dosya |
|---|---|---|
| **1. DB / Şema** | Kapsam dışı (defter şeması `test-spec-state@1` değişmez) | — |
| **2. Backend / Script** | `to-plan`, `parse-report` | `scripts/testsprite_bridge.py`, `scripts/test_spec_tracker.py` |
| **3. Entegrasyon** | TestSprite MCP çağrı sırası (ajan akışı) | `SKILL.md` Aşama 6 |
| **4. Arayüz** | Salt CLI — `Tier 0: UI Kapsam Dışı` | — |
| **5. Döngü Kapanışı** | `record` → `status` → `export-delta` yenilenir | Mevcut tracker komutları |

## 7. Tema & UI
- `Salt Backend / UI Kapsam Dışı` · `Tier 0`.

---

## 8. `/test-spec-run` Çalışma Akışı (Hedef Davranış)

```text
/test-spec-run
  │
  ├─[1] test_spec_tracker.py status ──► NEW+STALE+FAIL+FLAKY = 0 ? ──► "Koşulacak senaryo yok" → DUR
  │
  ├─[2] MCP testsprite_check_account_info
  │        └─ kredi yok / Paused ──► smoke_runner.py --mode live --testsprite-status exhausted
  │                                  → "TestSprite ATLANDI — defter güncellenmedi" → DUR
  │
  ├─[3] Port kontrolü (5173 / 4173). Kapalıysa: npm run build && npm run preview (daemon)
  │
  ├─[4] test_spec_tracker.py export-delta  ──► DELTA.feature (yalnız NEW/STALE/FAIL/FLAKY)
  │
  ├─[5] testsprite_tests/tmp/config.json yoksa ──► MCP testsprite_bootstrap (type=frontend, testScope=codebase)
  │     plan dosyası yoksa ──► MCP testsprite_generate_frontend_test_plan
  │
  ├─[6] testsprite_bridge.py to-plan ──► plan JSON'u SC-* senaryolarıyla yeniden yaz
  │                                     + testsprite_tests/sc_map.json + .bak yedeği
  │
  ├─[7] MCP testsprite_generate_code_and_execute(testIds=[SC-...], serverMode=production)
  │        (dev modda: 15'lik partiler halinde tekrar)
  │
  ├─[8] test_spec_tracker.py record --import-testsprite <rapor> --runner testsprite
  │        └─ eşleşen 0 ise: "HATA: rapor eşlenemedi" (sessiz PASS yok)
  │
  └─[9] status + export-delta yenile ──► Rapor: PASS / FAIL listesi + "/fix-bug önereyim mi?"
```

### 📌 Faz 0: Onay Sonrası Mühürleme
1. **[Adım 1 - Arşiv]:** `python .agent/skills/musgoku/scripts/archive_plan.py --plan <plan-yolu> --slug test_spec_run --allow-no-wireframe` -> **Beklenen Çıktı:** `[ARCHIVED] docs/plans/plan_test_spec_run_<ts>.md`
2. **[Adım 2 - HANDOFF §3]:** Bölüm 5 görevlerini işle -> **Beklenen Çıktı:** `check_handoff.py` 0 hata.
3. **[Adım 3 - Karar Kaydı]:** Council kararını `knowledge-base.md`'ye `Karar / Gerekçe / Değerlendirilen Alternatifler / Files Changed` formatında ekle -> **Beklenen Çıktı:** Yeni karar bloğu dosya sonunda.

### 🔴 Faz 1: Spike + Kırmızı Test
1. **[Adım 1 - Format Spike]:** FEProjectv1'de bir kez `testsprite_bootstrap` + `testsprite_generate_frontend_test_plan` çalıştır (ya da mevcut dosyayı al); plan JSON ve sonraki rapor dosyasını `scripts/tests/fixtures/` altına anonim kopyala -> **Beklenen Çıktı:** `fixtures/testsprite_plan.json`, `fixtures/testsprite_report.md` gerçek formatta.
2. **[Adım 2 - Kırmızı Testler]:** `scripts/tests/test_testsprite_bridge.py` yaz:
   - `to-plan`: 3 senaryolu delta feature → plan JSON'da 3 kayıt, her başlıkta `SC-*`.
   - `parse-report`: fixture rapordan ≥1 `PASS` ve ≥1 `FAIL` eşleşir (durum ayrı satırda).
   - Eşleşme 0 ise boş sözlük + uyarı döner (sessiz PASS yok).
   `python -m pytest .agent/skills/test-spec-generator/scripts/tests -q` -> **Beklenen Çıktı:** **KIRMIZI (FAIL)**.

### 🟢 Faz 2: Minimal Kod
1. **[Adım 1 - Köprü]:** `testsprite_bridge.py` (`to-plan`, ~120 satır, yalnız stdlib). Mevcut `scanner.export_feature_file` ile senaryoları al, TestSprite plan şemasına çevir, `sc_map.json` yaz -> **Beklenen Çıktı:** `to-plan` testleri YEŞİL.
2. **[Adım 2 - Parser]:** `parse_testsprite_report`'u blok bazlı yap: test başlığı satırından sonraki durum satırını bağla; `TC###` → `sc_map.json` üzerinden `SC-*`'a çevir; eski tek-satır davranışı fallback -> **Beklenen Çıktı:** tüm testler YEŞİL.

### 🧩 Faz 3: Dokümantasyon & Tetik
1. **[Adım 1 - SKILL.md]:** `test-spec-generator/SKILL.md`'ye **Aşama 6: `/test-spec-run`** (Bölüm 8 akışı) ve tetikler: `"/test-spec-run"`, `"testleri koş"`, `"testsprite ile koş"`, `"run test spec"` -> **Beklenen Çıktı:** Frontmatter `description` güncel.
2. **[Adım 2 - Routing]:** `skill-trigger-routing.md` satır 146 ve 177'ye aynı tetikleri ekle -> **Beklenen Çıktı:** `Select-String "test-spec-run"` 2+ eşleşme.
3. **[Adım 3 - smoke-test]:** `smoke-test/SKILL.md` satır 32'deki `export-delta` cümlesini "Gherkin defter koşumu `/test-spec-run`'a aittir" yönlendirmesine çevir -> **Beklenen Çıktı:** Tek sahip.

### 🧹 Faz 4: Canlı Doğrulama & Kapanış
1. **[Adım 1 - Uçtan Uca]:** FEProjectv1'de `/test-spec-run` -> **Beklenen Çıktı:** `test_spec_tracker.py status` → `NEW: 0`, `PASS + FAIL = 59` (veya ilk parti 15).
2. **[Adım 2 - Kapı]:** `check_test_spec.py --spec ... --inventory ... --state ...` -> **Beklenen Çıktı:** `[PASS]`, `E8_STATE_DRIFT` yok.
3. **[Adım 3 - Kapılar]:** `python .agent/skills/musgoku/scripts/run_all_gates.py` -> **Beklenen Çıktı:** `[OK]`.

---

## 9. Proposed Changes

### test-spec-generator
#### [NEW] `.agent/skills/test-spec-generator/scripts/testsprite_bridge.py`
- `to-plan --spec <md> --state <json> --plan testsprite_tests/testsprite_frontend_test_plan.json [--batch 15]`: delta SC-* senaryolarını TestSprite plan kaydına çevirir; `.bak` yedeği ve `sc_map.json` yazar; parti sayısını basar.

#### [NEW] `.agent/skills/test-spec-generator/scripts/tests/test_testsprite_bridge.py` + `tests/fixtures/`
- Faz 1 kırmızı testleri, gerçek formattan alınmış fixture'lar.

#### [MODIFY] `.agent/skills/test-spec-generator/scripts/test_spec_tracker.py`
- `parse_testsprite_report`: blok bazlı parse + `sc_map.json` eşleme. `record` 0 eşleşmede uyarı basar ve exit `2` döner. Patlama yarıçapı: yalnız `--import-testsprite` yolu.

#### [MODIFY] `.agent/skills/test-spec-generator/SKILL.md`
- Aşama 6 + yeni tetikler.

### Routing & smoke-test
#### [MODIFY] `.agent/rules/skill-trigger-routing.md` — satır 146, 177.
#### [MODIFY] `.agent/skills/smoke-test/SKILL.md` — satır 31-32 yönlendirme.

**Toplam:** 2 yeni dosya (+fixture), 4 değişen dosya. Yeni bağımlılık yok.

---

## 10. Verification Plan

### Automated Tests
```powershell
# 1. Kırmızı (Faz 1) ve Yeşil (Faz 2)
python -m pytest .agent/skills/test-spec-generator/scripts/tests -q

# 2. Köprü kuru koşum
python .agent/skills/test-spec-generator/scripts/testsprite_bridge.py to-plan --spec docs/testing/FEPROJECTV1_ACCEPTANCE_TEST_SPEC.md --state docs/testing/test-spec-state.json --plan testsprite_tests/testsprite_frontend_test_plan.json

# 3. Birleşik kapılar
python .agent/skills/musgoku/scripts/run_all_gates.py
```

### Manual Verification
1. **[Adım 1 - Komut]:** FEProjectv1'de `/test-spec-run` yaz -> **Beklenen Çıktı:** Sırasıyla kota kontrolü, delta export, TestSprite koşumu, record satırları görünür.
2. **[Adım 2 - Defter]:** `python .agent/skills/test-spec-generator/scripts/test_spec_tracker.py status --state docs/testing/test-spec-state.json` -> **Beklenen Çıktı:** `NEW` azalır, `PASS`/`FAIL` dolar.
3. **[Adım 3 - Delta]:** Komutu tekrar ver -> **Beklenen Çıktı:** Yalnız `FAIL` senaryolar koşulur; `PASS`'ler tekrar koşulmaz.

---

## 11. 🚨 Ditching & Emergency Exit

| Belirti / Hata | Olası Neden | Anında Düzeltici Eylem |
|---|---|---|
| `Recorded 0 results` / exit 2 | TestSprite rapor formatı fixture'dan farklı | Yeni raporu `fixtures/`'a ekle, parser testini kırmızıya düşür, düzelt |
| TestSprite yalnız 15 test koştu | Dev sunucu modu | `npm run build && npm run preview` + `serverMode: production`, ya da `--batch 15` ile kalan partileri koş |
| TestSprite planı bozuldu | `to-plan` yazımı hatalı | `testsprite_tests/testsprite_frontend_test_plan.json.bak` dosyasını geri kopyala |
| `testsprite_check_account_info` Paused | Kredi/hesap sorunu | Fallback otomatik; defter değişmez. Kredi yenilenince komutu tekrar ver |
| `E8_STATE_DRIFT` | `record` sonrası spec elle değişti | `test_spec_tracker.py sync --root . --spec <md> --state <json>` |
