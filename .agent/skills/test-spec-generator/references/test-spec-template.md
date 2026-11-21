# Tek Dosya Test Spesifikasyonu Referans Şablonu

Bu şablon `docs/testing/<SLUG>_ACCEPTANCE_TEST_SPEC.md` dosyasının standart yapısını tanımlar. TestSprite ve otomatik test araçları bu dosyayı tek başına okuyarak tüm sistemi test edebilmelidir.

```markdown
# <SLUG> — Birleşik Kabul Kriterleri & Gherkin Test Spesifikasyonu

> **Oluşturulma Tarihi:** YYYY-MM-DD · **Dil:** tr/en · **Kaynak Envanter:** `docs/testing/test-inventory.json`

## 0. Test Ortamı, Mimari & Auth Sözleşmesi
- **Proje Slug:** `<slug>` · **Mimari:** `<örn. React SPA + Spring Boot REST API>`
- **Frontend / Backend URL & Port:** `http://localhost:5173` / `http://localhost:8080`
- **Kimlik Doğrulama Tipi:** `<JWT Bearer / Session Cookie / OAuth2>`
- **Test Rolleri & Yetki Sınırları:**
  - `ADMIN`: Tüm yönetim ve kaynak oluşturma işlemlerine yetkili
  - `USER`: Yalnızca kendi kaynaklarını görüntüleyebilir
  - `GUEST`: Yalnızca public sayfalara erişebilir
- **Önkoşul / Seed Verisi:** `<varsa başlangıç test verisi gereksinimi>`

## 1. Uçtan Uca Kapsam ve İzlenebilirlik Matrisi
| Modül | Kaynak (PRD / Kod) | Route / API Endpoint | AC ID'leri | Scenario ID'leri | Etiketler |
|---|---|---|---|---|---|
| Auth | `PRODUCT.md` FR-001, `AuthController.java` | `/login`, `POST /api/v1/auth/login` | `AC-AUTH-01` | `SC-AUTH-01`, `SC-AUTH-02` | `@smoke @negative` |

## 2. Modül Bazlı Acceptance Criteria & Gherkin Senaryoları

### Modül 1: `<Modül Adı>` (`FR-001`, `/route`, `METHOD /api/...`)
- **AC-MOD-01:** `<Ölçülebilir, somut girdi/çıktı ve durum kodu içeren kabul kriteri>`
- **AC-MOD-02:** `<Yetki/validasyon/UX durumu kabul kriteri>`

```gherkin
# language: tr
Feature: <Modül Adı>

  Background:
    Given Uygulama çalışır durumdadır ve test verisi hazırdır

  @smoke @happy-path @ui @api
  Scenario: SC-MOD-01 <Başarılı uçtan uca akış>
    Given <Başlangıç durumu ve rol>
    When <Kullanıcı veya API eylemi>
    Then <Beklenen HTTP kodu, veri kalıcılığı ve ekran çıktısı>

  @negative @validation
  Scenario Outline: SC-MOD-02 <Hatalı girdi ve sınır değer doğrulamaları>
    Given <Form veya endpoint>
    When "<alan>" alanına "<gecersiz_deger>" gönderilir
    Then Sunucu <http_kodu> döner ve "<hata_anahtari>" mesajı görünür

    Examples:
      | alan  | gecersiz_deger | http_kodu | hata_anahtari |
      | email | gecersiz-mail  | 400       | invalid_email |

  @security @rbac @negative
  Scenario: SC-MOD-03 <Yetkisiz rol erişimi engellenir>
    Given Kullanıcı yetkisiz bir rolle oturum açmıştır
    When Korumalı işleme istek gönderir
    Then Sunucu 403 Forbidden döner ve veri değişmez
```

## 3. Çapraz Sistem & E2E Senaryoları
- **E2E-01:** `SC-AUTH-01` -> `SC-MOD-01` (Oturum açma sonrası ana iş akışının uçtan uca doğrulanması)

## 4. Kapsam Dışı, Varsayımlar & Kod-Doküman Çelişkileri
- Tespit edilen stub sayfalar, kırık rotalar veya dokümanla çelişen noktalar burada `@wip` / `@blocked` olarak listelenir.

## 5. Otomasyon Çalıştırma Komutları & Dışa Aktarım
- **Kapsama Kapısı:** `python .agent/skills/test-spec-generator/scripts/check_test_spec.py --spec docs/testing/<SLUG>_ACCEPTANCE_TEST_SPEC.md --inventory docs/testing/test-inventory.json`
- **Tek `.feature` Dosyasına Aktarım:** `python .agent/skills/test-spec-generator/scripts/test_spec_scanner.py --export-feature docs/testing/<SLUG>_ACCEPTANCE_TEST_SPEC.md --out specs/<SLUG>_ALL.feature`
```
