---
name: verify-last
description: Son yapılan geliştirmeleri, çalışma ağacındaki değişiklikleri veya son commit'i cerrahi olarak denetleyen oturum doğrulama orkestratörü; derleme, tip, etkilenen katmanlar ve regresyon riskini doğrular. Tetikleyiciler: "/verify-last", "verify last", "[VERIFY-LAST]", "son geliştirmeleri denetle", "son işi doğrula", "verify recent changes", "audit last commit". Tetiklenmez: sprint hedefleri `verify-sprint`'e, tüm proje şartnamesi `verify-prd`'ye aittir. Tam sözlük: .agent/rules/skill-trigger-routing.md
---

# Verify Last (Mikro / Son Geliştirmeler & Çalışma Ağacı Denetim Orkestratörü)

Bu yetenek, anlık geliştirme oturumunda **en son yapılan değişiklikleri**, `git status` / uncommitted çalışma ağacını veya en son commit'i (`HEAD~1..HEAD`) cerrahi olarak denetler. Amaç; yapılan son rötüşün veya dilimin derleme, tip, katman bütünlüğü, canlı mimari (`PROJECT_BRIEF.md`) ve oturum devri (`HANDOFF.md`) kapılarından eksiksiz geçtiğini kanıtlamaktır.

---

## Ne Zaman Kullanılır?

- Kullanıcı *"az önce yaptığımız işe bak"*, *"son geliştirmeleri denetle"*, *"/verify-last"* veya *"değişiklikleri doğrula"* dediğinde.
- Bir özellik kodlandıktan hemen sonra, commit onayı istemeden önce.
- Hızlı bir hata düzeltmesi (bugfix) veya refactoring sonrası anlık doğrulama için.

---

## 3 Aşamalı Cerrahi Denetim Protokolü

### 1. Birleşik Kapsam-Duyarlı Kalite Kapısı (`run_all_gates.py`)
- `git status --short` ile değişen dosyaları listele.
- Projedeki tüm ölçülebilir kural kapılarını tek komutla çalıştır:
  ```bash
  python .agent/skills/musgoku/scripts/run_all_gates.py
  ```
- Kapsam ilkesine göre (`AGENTS.md` §3.3):
  * Yalnızca `.agent/` veya `*.md` değiştiyse: Uygulama derleme/test adımları atlanır (`SKIPPED`).
  * `src/**`, `api/**`, `components/**`, `supabase/**` değiştiyse: `build`, `typecheck` ve ilgili birim testleri zorunlu çalıştırılır.
  * Hata varsa anında raporlanır ve düzeltilir.

### 2. Cerrahi Katman ve İkili Eşleme (Dual Mapping) Analizi
- Yapılan son değişiklik hangi katmanlara dokundu?
  * **Veritabanı / Migration değiştiyse:** Hem `DB_MIGRATIONS.md` hem de `PROJECT_BRIEF.md` güncellendi mi? (`check_db_migrations.py` E4/E5 ve `check_project_brief.py` E4).
  * **Bağımlılık veya Edge Function / Altyapı değiştiyse:** `PROJECT_BRIEF.md` güncellendi mi? (`check_project_brief.py` E3/E6).
  * **API rotası / Controller değiştiyse:** `docs/APIs/` güncellendi mi? (`check_api_docs.py` E1/E3).
  * **Arayüz (UI/CSS) değiştiyse:** `DESIGN.md` sözleşmesi, WCAG kontrastı ve anti-slop kuralları korundu mu? (`check_design_contract.py`, `check_design_slop.py`, `check_theme_contrast.py`).
  * **Uygulama kodu değiştiyse:** `HANDOFF.md` ve gerekiyorsa `docs/KULLANICI_TEST_REHBERI.md` güncellendi mi? (`check_handoff.py` E3/W2).

### 3. Hızlı Kullanıcı Test Adımı
- Kullanıcının tarayıcıda veya konsolda bu son değişikliği 1-2 adımda gözüyle nasıl doğrulayacağını net olarak sun.

---

## Standart Çıktı Raporu

```markdown
### ⚡ VERIFY-LAST: SON GELİŞTİRMELER DOĞRULAMA RAPORU

- **Değişen Dosyalar:** [X dosya modified, Y untracked]
- **Birleşik Kalite Kapıları (`run_all_gates.py`):**
  * Kural & Mimari Kapıları: ✅ [X geçti · Y kapsam dışı · 0 başarısız]
  * Derleme (`build`): ✅ [Süre / Sonuç veya Kapsam Dışı]
  * Tip Kontrolü (`typecheck`): ✅ [0 hata veya Kapsam Dışı]
  * İlgili Testler: ✅ [X passed / 0 failed]
- **Dokunulan Katmanlar & Senkron:** [DB ↔ DB_MIGRATIONS.md + PROJECT_BRIEF.md, API ↔ docs/APIs, UI ↔ DESIGN.md, Handoff ↔ HANDOFF.md]
- **Gözle Doğrulama:**
  👉 `[URL veya Komut]` ➔ `[Beklenen Sonuç]`
```
