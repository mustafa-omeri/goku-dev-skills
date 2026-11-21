---
name: test-spec-generator
description: >-
  Tüm projeyi (kod, kardeş repo ve dokümanlar) tarayarak Gherkin senaryoları ve Acceptance Criteria maddelerini tek bir spesifikasyon dosyasında üreten ve kapsama kapısıyla doğrulayan orkestratör. Tetikleyiciler: "/test-spec", "test spec", "gherkin testleri çıkar", "kabul kriterleri üret", "generate test spec", "gherkin acceptance tests". Tetiklenmez: mevcut sprint denetimi verify-sprint'e, PRD retrospektif denetimi verify-prd'ye aittir. Tam sözlük: .agent/rules/skill-trigger-routing.md
---

# Test Spec Generator (`/test-spec`)

Bu yetenek; projenin **tüm kaynak kodunu** (rotalar, formlar, backend API uç noktaları, veritabanı modelleri, RBAC yetkileri, kardeş repo) ve **tüm dokümanlarını** (`PRODUCT.md`, `PROJECT_BRIEF.md`, `docs/*prd*`, `docs/APIs/`, `DB_MIGRATIONS.md`, `specs/*.feature`, `HANDOFF.md`) uçtan uca tarayarak **ölçülebilir Acceptance Criteria (`AC-XXX`)** ve **Gherkin (`Feature` / `Background` / `Scenario` / `Scenario Outline` / `Given-When-Then`)** senaryolarını **tek bir dosyada** (`docs/testing/<SLUG>_ACCEPTANCE_TEST_SPEC.md`) üretir.

Üretilen tek dosya; **TestSprite**, Playwright, Cucumber, Cypress veya yapay zeka tabanlı otomatik test araçlarına doğrudan girdi olarak verilecek şekilde yapılandırılmıştır.

> ⛔ **Sınır Ayrımı:**
> - Mevcut sprint kartlarının kabul denetimi: [`verify-sprint`](../verify-sprint/SKILL.md)
> - Geçmiş kod/PRD retrospektif denetimi: [`verify-prd`](../verify-prd/SKILL.md)
> - Geliştirme öncesi dış PRD analizi: [`review-prd`](../review-prd/SKILL.md)

---

## Ne Zaman Kullanılır?

- Kullanıcı `"/test-spec"`, *"tüm projeyi inceleyip Gherkin testleri ve acceptance criteria çıkar"*, *"TestSprite veya otomatik test araçları için tek bir test dosyası hazırla"* dediğinde.
- Yeni veya olgunlaşmış bir projede tüm modülleri kapsayan tek kaynak doğruluklu (`Single Source of Truth`) kabul testi spesifikasyonu gerektiğinde.

---

## 5 Aşamalı Tek-Dosya Test Spesifikasyonu Protokolü

### Aşama 1: Deterministik Kod, Kardeş Repo ve Doküman Envanteri Çıkarımı
Tek bir rota, API ucu, rol veya gereksinim maddesi dahi gözden kaçmasın diye önce deterministik tarayıcı çalıştırılır:

```powershell
python .agent/skills/test-spec-generator/scripts/test_spec_scanner.py --root . --json --out docs/testing/test-inventory.json
```
*(Ayrı backend/frontend deposu varsa `--peer <kardeş-repo-yolu>` veya dar kapsam isteniyorsa `--focus auth,orders` eklenir).*

Tarayıcı `feature-architect` (`fa_scan`) motorunu kullanarak şunları çıkarır:
- Aktif frontend rotaları (`routes`) ve varsa kırık/stub sayfalar (`gaps`)
- Backend HTTP uç noktaları (`endpoints` + `allowed_roles`) ve veri modelleri (`data_models`)
- Sistemdeki roller (`roles`)
- `PRODUCT.md`, `docs/*prd*`, `docs/APIs/`, `RFCs/`, `DB_MIGRATIONS.md` içindeki gereksinim kimlikleri (`FR-`, `US-`, `NFR-`, `REQ-`)
- Halihazırda `specs/*.feature` altında bulunan mevcut senaryolar

### Aşama 2: Derin Kaynak Kod Okuması & İş Kuralı Analizi
Envanterdeki her modül (`modules`) için ilgili route, sayfa bileşeni, form/validasyon şeması (Zod, Bean Validation), controller/servis ve API dokümanı okunarak şu gerçekler netleştirilir:
1. **Girdi & Validasyon Kuralları:** Zorunlu alanlar, karakter limitleri, tip/format kuralları, hata mesajları.
2. **Yetki & Güvenlik Sınırları (RBAC / Auth):** Hangi rolün neyi görüp neyi çağırabildiği, yetkisiz durumda beklenen `401`/`403` davranışı.
3. **Veri Kalıcılığı & Yan Etkiler:** Başarılı işlem sonrasında dönen HTTP kodu (`200`/`201`/`204`), veritabanı/UI yansıması (refresh gerekmeden güncelleme).
4. **4 UX Durumu:** `Skeleton Loading`, `Empty State`, `Error + Retry`, `Success` ve mobil kırılım.

> ⛔ **Totolojik ve Belirsiz Kriter Yasağı:** *"Kullanıcı dostu görünür"*, *"hızlı çalışır"* gibi ölçülemez ifadeler veya sahte geçer testler yazılmaz. Her Acceptance Criteria somut değer, durum kodu ve gözlenebilir çıktı içermelidir.

### Aşama 3: Tek Dosya (`ACCEPTANCE_TEST_SPEC.md`) Sentezi
Ajan, [references/test-spec-template.md](references/test-spec-template.md) ve `.agent/templates/ACCEPTANCE_TEST_SPEC.template.md` yapısına birebir uyarak **tek bir dosya** üretir:
- **Hedef Konum:** `docs/testing/<SLUG>_ACCEPTANCE_TEST_SPEC.md` (İngilizce projelerde aynı yapı `primary_language` dilinde yazılır).
- **6 Zorunlu Bölüm:**
  1. `## 0. Test Ortamı, Mimari & Auth Sözleşmesi` (Test araçlarının ihtiyaç duyduğu stack, port/base URL, test kullanıcı rolleri, auth akışı)
  2. `## 1. Uçtan Uca Kapsam ve İzlenebilirlik Matrisi` (`Modül | Kaynak | Route / Endpoint | AC ID | Scenario ID | Etiketler`)
  3. `## 2. Modül Bazlı Acceptance Criteria & Gherkin Senaryoları` (`AC-<MOD>-01..N` + ```` ```gherkin ```` blokları: `@smoke`, `@happy-path`, `@negative`, `@validation`, `@rbac`, `@api`, `@ui`)
  4. `## 3. Çapraz Sistem & E2E Senaryoları` (Çok modüllü yaşam döngüsü akışları)
  5. `## 4. Kapsam Dışı, Varsayımlar & Kod-Doküman Çelişkileri` (Stub/eksik katmanlar varsa `@wip`/`@blocked` olarak açıkça işaretlenir)
  6. `## 5. Otomasyon Çalıştırma Komutları & Dışa Aktarım`

### Aşama 4: Deterministik Kapsama ve Sözdizimi Kapısı (`check_test_spec.py`)
Üretilen dosya kaydedildikten sonra mutlaka mekanik kapı çalıştırılır:

```powershell
python .agent/skills/test-spec-generator/scripts/check_test_spec.py --spec docs/testing/<SLUG>_ACCEPTANCE_TEST_SPEC.md --inventory docs/testing/test-inventory.json
```

Kapı şunları doğrular:
- `E1..E2`: Dosya boş değil ve 6 zorunlu bölüm mevcut
- `E3`: `<doldur>`, `TODO`, `TBD` gibi şablon kalıntısı yok
- `E4`: Tüm ```` ```gherkin ```` bloklarında geçerli `Feature:`, `Scenario:`/`Scenario Outline:` ve `Given/When/Then` adımları var
- `E5`: Benzersiz `AC-...` kabul kriteri kimlikleri tanımlı
- `E6`: Envanterdeki aktif rotalar ve HTTP endpoint'lerinin (`METHOD /path`) tamamı kapsamda
- `E7`: Projede RBAC rolleri varsa Gherkin bloklarında `@rbac` / `@security` / `403` senaryoları mevcut

### Aşama 5: Opsiyonel Saf `.feature` Dışa Aktarımı (`--export-feature`)
Cucumber, Behave, Playwright-BDD gibi doğrudan `.feature` uzantısı bekleyen araçlar için tek tıkla ayıklama yapılabilir:

```powershell
python .agent/skills/test-spec-generator/scripts/test_spec_scanner.py --export-feature docs/testing/<SLUG>_ACCEPTANCE_TEST_SPEC.md --out specs/<SLUG>_ALL.feature
```

---

## Standart Çıktı Özeti

İşlem bittiğinde kullanıcıya kısa ve net rapor verilir:
- **Üretilen Tek Dosya:** `docs/testing/<SLUG>_ACCEPTANCE_TEST_SPEC.md`
- **Kapsam Özeti:** X Modül · Y Acceptance Criteria (`AC-...`) · Z Gherkin Senaryosu · N Rota & M API Endpoint (%100 kapsam)
- **Kapı Sonucu:** `check_test_spec.py` -> `[PASS]`
- *(Varsa)* **Tespit Edilen Stub / Çelişkiler:** Bölüm 4'te listelenen açık noktalar.
