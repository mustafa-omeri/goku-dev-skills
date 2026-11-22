# Tek Dosya Test Spesifikasyonu Referans Şablonu (v2)

Bu şablon `docs/testing/<SLUG>_ACCEPTANCE_TEST_SPEC.md` dosyasının standart v2 yapısını tanımlar. Her modül `<!-- TEST-SPEC:MODULE:<mod>:BEGIN/END -->` çapaları içinde tutulur; böylece artımlı güncellemelerde değişmeyen modüllere ve `PASS` referanslarına dokunulmaz.

```markdown
# <SLUG> — Birleşik Kabul Kriterleri & Gherkin Test Spesifikasyonu

> **Oluşturulma Tarihi:** YYYY-MM-DD · **Dil:** tr/en · **State Defteri:** `docs/testing/test-spec-state.json`

## 0. Test Ortamı, Mimari & Auth Sözleşmesi
- **Proje Slug:** `<slug>` · **Mimari:** `<örn. React SPA + Spring Boot REST API>`
- **Frontend / Backend URL & Port:** `http://localhost:5173` / `http://localhost:8080`
- **Kimlik Doğrulama Tipi:** `<JWT Bearer / Session Cookie / OAuth2>`
- **Test Rolleri & Yetki Sınırları:**
  - `ADMIN`: Tüm yönetim ve kaynak oluşturma işlemlerine yetkili
  - `USER`: Yalnızca kendi kaynaklarını görüntüleyebilir
  - `GUEST`: Yalnızca public sayfalara erişebilir
- **Önkoşul / Seed Verisi & İzolasyon:** Her senaryo benzersiz veri (`uuid`/timestamp) kullanır; önceki testin artığına bağımlı olamaz.

## 1. Uçtan Uca Kapsam, Risk & PASS İzlenebilirlik Matrisi
| Modül | Kaynak (PRD / Kod) | Route / API Endpoint | AC ID'leri | Scenario ID'leri | Risk | Durum / PASS Ref |
|---|---|---|---|---|---|---|
| Auth | `PRODUCT.md` FR-001 | `/login`, `POST /api/v1/auth/login` | `AC-AUTH-01` | `SC-AUTH-01`, `SC-AUTH-02` | `P0` | `✅ PASS (testsprite @ 2be635d)` |
| Projects | `PRODUCT.md` US-002 | `/projects`, `GET /api/v1/projects`, `POST /api/v1/projects` | `AC-PROJ-01..02` | `SC-PROJ-01..03` | `P0/P1` | `🟡 STALE (Major) / 🆕 NEW` |

## 2. Modül Bazlı Acceptance Criteria & Gherkin Senaryoları

<!-- TEST-SPEC:MODULE:auth:BEGIN -->
### Modül 1: Auth (`FR-001`, `/login`, `POST /api/v1/auth/login`)
- **AC-AUTH-01:** Geçerli kimlik bilgileriyle giriş yapan kullanıcı `200` alır ve `/projects` ekranına yönlendirilir; hatalı parolada `401` döner ve formda hata mesajı görünür.

```gherkin
# language: tr
Feature: Kimlik Doğrulama (/login)

  Background:
    Given Uygulama /login sayfasında çalışmaktadır ve test kullanıcısı hazırdır

  @p0-critical @smoke @happy-path @ui @api
  Scenario: SC-AUTH-01 Geçerli kimlik bilgileriyle başarılı giriş
    Given Kullanıcı kayıtlı ve aktif bir hesaba sahiptir
    When POST /api/v1/auth/login isteği geçerli e-posta ve parola ile gönderilir
    Then Sunucu 200 döner ve kullanıcı /projects rotasına yönlendirilir

  @p0-critical @negative @validation
  Scenario Outline: SC-AUTH-02 Geçersiz giriş ve sınır değer doğrulamaları
    When "<alan>" alanına "<gecersiz_deger>" gönderilir
    Then Sunucu <http_kodu> döner ve "<hata_anahtari>" uyarısı görünür

    Examples:
      | alan     | gecersiz_deger | http_kodu | hata_anahtari       |
      | email    | gecersiz-mail  | 400       | invalid_email       |
      | password | yanlis123      | 401       | invalid_credentials |
```
<!-- TEST-SPEC:MODULE:auth:END -->

<!-- TEST-SPEC:MODULE:projects:BEGIN -->
### Modül 2: Projects (`US-002`, `/projects`, `GET /api/v1/projects`, `POST /api/v1/projects`)
- **AC-PROJ-01:** Yalnızca `ADMIN` rolü `POST /api/v1/projects` çağırabilir; yetkisiz roller `403` alır; başarılı ekleme refresh olmadan UI listesine yansır.
- **AC-PROJ-02 (Performans & Idempotency):** `GET /api/v1/projects` sayfalı (`limit<=50`) yanıtı `<300ms` sürede döner; aynı `Idempotency-Key` veya çift tıklama mükerrer kayıt oluşturmaz.

```gherkin
Feature: Proje Yönetimi (/projects)

  @p1-high @e2e @api @ui
  Scenario: SC-PROJ-01 Yönetici proje listeler ve refresh olmadan yeni proje görür
    Given Kullanıcı ADMIN rolüyle oturum açmıştır ve /projects sayfasındadır
    When GET /api/v1/projects yüklendikten sonra geçerli Türkçe karakterli ("Örnek Şube") proje eklenip POST /api/v1/projects çağrılır
    Then Sunucu 201 döner ve "Örnek Şube" kartı sayfa yenilenmeden listede görünür

  @p0-critical @security @rbac @negative
  Scenario: SC-PROJ-02 Yetkisiz kullanıcı proje oluşturamaz
    Given Kullanıcı ADMIN rolüne sahip değildir
    When POST /api/v1/projects uç noktasına istek gönderir
    Then Sunucu 403 Forbidden döner ve kayıt oluşmaz

  @p1-high @perf @pagination @idempotency
  Scenario: SC-PROJ-03 Sayfalama sınırı ve çift gönderim idempotency kontrolü
    Given Kullanıcı ADMIN rolüyle oturum açmıştır
    When GET /api/v1/projects?page=1&limit=20 çağrılır ve ardından aynı Idempotency-Key ile POST /api/v1/projects iki kez gönderilir
    Then Liste yanıtı 300ms altında en fazla 20 kayıt döner ve yalnızca tek bir yeni proje oluşturulur
```
<!-- TEST-SPEC:MODULE:projects:END -->

## 3. Çapraz Sistem & E2E Senaryoları
- **E2E-01:** `SC-AUTH-01` -> `SC-PROJ-01` (Oturum açma sonrası proje yaşam döngüsünün uçtan uca doğrulanması)

## 4. Kapsam Dışı, Varsayımlar & Kod-Doküman Çelişkileri
- Tespit edilen stub sayfalar, kırık rotalar veya dokümanla çelişen noktalar burada `@wip` / `@blocked` olarak listelenir.

## 5. Otomasyon Çalıştırma Komutları & Artımlı Takip
- **Artımlı Değişiklik Planı:** `python .agent/skills/test-spec-generator/scripts/test_spec_tracker.py plan --root . --state docs/testing/test-spec-state.json --json`
- **Kapsama & State Kapısı:** `python .agent/skills/test-spec-generator/scripts/check_test_spec.py --spec docs/testing/<SLUG>_ACCEPTANCE_TEST_SPEC.md --inventory docs/testing/test-inventory.json --state docs/testing/test-spec-state.json`
- **Delta Export (Yalnız NEW + STALE + FAIL):** `python .agent/skills/test-spec-generator/scripts/test_spec_tracker.py export-delta --spec docs/testing/<SLUG>_ACCEPTANCE_TEST_SPEC.md --state docs/testing/test-spec-state.json --out-md docs/testing/<SLUG>_DELTA_TEST_SPEC.md --out-feature specs/<SLUG>_DELTA.feature`
- **Sonuç İşleme (PASS Ref):** `python .agent/skills/test-spec-generator/scripts/test_spec_tracker.py record --state docs/testing/test-spec-state.json --import-testsprite testsprite_tests/report.md --runner testsprite`
- **Tam Saf `.feature` Çıktısı:** `python .agent/skills/test-spec-generator/scripts/test_spec_scanner.py --export-feature docs/testing/<SLUG>_ACCEPTANCE_TEST_SPEC.md --out specs/<SLUG>_ALL.feature`
```
