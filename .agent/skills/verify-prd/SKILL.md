---
name: verify-prd
description: Gherkin kabul kriterleri, beş katmanlı dikey dilim mimarisi ve Martin Fowler kod kokusu denetimiyle sprint doğrulama orkestratörü; sahte bitti durumlarını engeller. Tetikleyiciler: "/verify-prd", "verify prd", "[VERIFY-PRD]", "kabul kriterlerini doğrula", "prd denetle". Tetiklenmez: sıfırdan PRD yazımı `doc-coauthoring`'e aittir. Tam sözlük: .agent/rules/skill-trigger-routing.md
---

# Verify PRD Ensemble Orchestrator

Bu yetenek, bir sprint veya özelliğin "BİTTİ" ilan edilmeden önce gerçek kabul kriterlerini (AC), mimari dikey dilim bütünlüğünü ve kod kalitesini bağımsız olarak doğrulayan orkestrasyon zincirini işletir.

## Orkestrasyon Akışı

1. **Gherkin Kabul Kriterleri Doğrulaması:**
   - İlgili PRD / User Story dokümanındaki (`docs/prd/` veya `HANDOFF.md`) her kabul senaryosunun test karşılığını denetle.
   - Sadece birim testleri değil, gerçek kullanıcı davranışını yansıtan entegrasyon/uçtan uca akışı doğrula.

2. **5 Katmanlı Dikey Dilim (Full-Stack Vertical Slice) Denetimi:**
   - 1. Katman: DB / Şema / Migration (Gerekliyse `DB_MIGRATIONS.md`)
   - 2. Katman: Backend / View / RPC / Servis mantığı
   - 3. Katman: İstemci API Entegrasyonu & Tip Uyumu
   - 4. Katman: Arayüz / UX & Form eylemleri
   - 5. Katman: Yönetim / Veri giriş akışı (Döngü kapanışı)
   - Katmanlardan biri eksikse `SONUÇ: YARIM (Eksik Katman)` ilan edilir.

3. **Kod Kokusu ve Kapsam Sapması Taraması:**
   - Martin Fowler kod kokularını (uzun metot, büyük sınıf, sızıntılı soyutlama) ve kapsam dışı eklemeleri tara.

4. **Kullanıcı Test Rehberi ve Handoff Kaydı:**
   - `KULLANICI_TEST_REHBERI.md` güncellenmeli ve kullanıcının bizzat gözüyle test edebileceği adımlar sunulmalıdır.
