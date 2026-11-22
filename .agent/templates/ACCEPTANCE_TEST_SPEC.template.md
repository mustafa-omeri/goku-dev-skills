# <SLUG> — Birleşik Kabul Kriterleri & Gherkin Test Spesifikasyonu

> **Oluşturulma Tarihi:** <doldur: YYYY-MM-DD> · **Dil:** <doldur: tr|en> · **State Defteri:** `docs/testing/test-spec-state.json`

## 0. Test Ortamı, Mimari & Auth Sözleşmesi
- **Proje Slug:** `<doldur: proje-slug>` · **Mimari:** `<doldur: Stack özeti>`
- **Frontend / Backend URL & Port:** `<doldur: http://localhost:5173 / http://localhost:8080>`
- **Kimlik Doğrulama Tipi:** `<doldur: JWT Bearer / Session / Yok>`
- **Test Rolleri & Yetki Sınırları:** `<doldur: Roller veya 'Anonim'>`
- **Önkoşul / Seed Verisi & İzolasyon:** `<doldur: Test kullanıcıları, benzersiz veri kuralı veya seed durumu>`

## 1. Uçtan Uca Kapsam, Risk & PASS İzlenebilirlik Matrisi
| Modül | Kaynak (PRD / Kod) | Route / API Endpoint | AC ID'leri | Scenario ID'leri | Risk | Durum / PASS Ref |
|---|---|---|---|---|---|---|
| `<doldur>` | `<doldur>` | `<doldur>` | `<doldur: AC-MOD-01>` | `<doldur: SC-MOD-01>` | `P0` | `🆕 NEW` |

## 2. Modül Bazlı Acceptance Criteria & Gherkin Senaryoları

<!-- TEST-SPEC:MODULE:<doldur:modul>:BEGIN -->
### Modül 1: `<doldur: Modül Adı>`
- **AC-MOD-01:** `<doldur: Ölçülebilir kabul kriteri>`

```gherkin
# language: tr
Feature: <doldur: Özellik Adı>

  @p0-critical @smoke @happy-path
  Scenario: SC-MOD-01 <doldur: Senaryo başlığı>
    Given <doldur: Önkoşul>
    When <doldur: Eylem>
    Then <doldur: Beklenen somut sonuç>
```
<!-- TEST-SPEC:MODULE:<doldur:modul>:END -->

## 3. Çapraz Sistem & E2E Senaryoları
- `<doldur: Modüller arası E2E senaryo zinciri>`

## 4. Kapsam Dışı, Varsayımlar & Kod-Doküman Çelişkileri
- `<doldur: Tespit edilen çelişki/stub veya 'Yok'>`

## 5. Otomasyon Çalıştırma Komutları & Artımlı Takip
- **Artımlı Plan:** `python .agent/skills/test-spec-generator/scripts/test_spec_tracker.py plan --root . --state docs/testing/test-spec-state.json --json`
- **Kapsama & State Kapısı:** `python .agent/skills/test-spec-generator/scripts/check_test_spec.py --spec docs/testing/<SLUG>_ACCEPTANCE_TEST_SPEC.md --inventory docs/testing/test-inventory.json --state docs/testing/test-spec-state.json`
- **Delta Export:** `python .agent/skills/test-spec-generator/scripts/test_spec_tracker.py export-delta --spec docs/testing/<SLUG>_ACCEPTANCE_TEST_SPEC.md --state docs/testing/test-spec-state.json --out-md docs/testing/<SLUG>_DELTA_TEST_SPEC.md --out-feature specs/<SLUG>_DELTA.feature`
- **Saf `.feature` Çıktısı:** `python .agent/skills/test-spec-generator/scripts/test_spec_scanner.py --export-feature docs/testing/<SLUG>_ACCEPTANCE_TEST_SPEC.md --out specs/<SLUG>_ALL.feature`
