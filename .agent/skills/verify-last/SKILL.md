---
name: verify-last
description: Son yapılan geliştirmeleri, çalışma ağacındaki değişiklikleri veya son commit'i cerrahi olarak denetleyen oturum doğrulama orkestratörü; derleme, tip, etkilenen katmanlar ve regresyon riskini doğrular. Tetikleyiciler: "/verify-last", "verify last", "[VERIFY-LAST]", "son geliştirmeleri denetle", "son işi doğrula", "verify recent changes", "audit last commit". Tetiklenmez: sprint hedefleri `verify-sprint`'e, tüm proje şartnamesi `verify-prd`'ye aittir. Tam sözlük: .agent/rules/skill-trigger-routing.md
---

# Verify Last (Mikro / Son Geliştirmeler & Çalışma Ağacı Denetim Orkestratörü)

Bu yetenek, anlık geliştirme oturumunda **en son yapılan değişiklikleri**, `git status` / uncommitted çalışma ağacını veya en son commit'i (`HEAD~1..HEAD`) cerrahi olarak denetler. Amaç; yapılan son rötüşün veya dilimin derleme, tip, katman bütünlüğü ve test kapılarından başarıyla geçtiğini kanıtlamaktır.

---

## Ne Zaman Kullanılır?

- Kullanıcı *"az önce yaptığımız işe bak"*, *"son geliştirmeleri denetle"*, *"/verify-last"* veya *"değişiklikleri doğrula"* dediğinde.
- Bir özellik kodlandıktan hemen sonra, commit onayı istemeden önce.
- Hızlı bir hata düzeltmesi (bugfix) veya refactoring sonrası anlık doğrulama için.

---

## 3 Aşamalı Cerrahi Denetim Protokolü

### 1. Kapsam-Duyarlı Kalite Kapısı
- `git status` ile değişen dosyaları listele.
- Kapsam ilkesine göre ilgili kapıları çalıştır:
  * Yalnızca `.agent/` veya `*.md` değiştiyse: Derleme/test atlanır.
  * `src/**`, `api/**`, `components/**` değiştiyse: `build`, `typecheck`, birim testleri zorunlu çalıştırılır.
  * Hata varsa anında raporlanır ve durulur.

### 2. Cerrahi Katman Analizi
- Yapılan son değişiklik hangi katmanlara dokundu?
  * Veritabanı (Migration) değiştiyse `DB_MIGRATIONS.md` güncellendi mi?
  * Arayüz değiştiyse WCAG kontrastı ve responsive düzen korundu mu?
  * Yeni bir endpoint/fonksiyon eklendiyse TypeScript arayüzü bağlandı mı?

### 3. Hızlı Kullanıcı Test Adımı
- Kullanıcının tarayıcıda veya konsolda bu son değişikliği 1-2 adımda gözüyle nasıl doğrulayacağını tek satırda sun.

---

## Standart Çıktı Raporu

```markdown
### ⚡ VERIFY-LAST: SON GELİŞTİRMELER DOĞRULAMA RAPORU

- **Değişen Dosyalar:** [X dosya modified, Y untracked]
- **Kalite Kapıları:**
  * Derleme (`build`): ✅ [Süre / Sonuç]
  * Tip Kontrolü (`typecheck`): ✅ 0 hata
  * İlgili Testler: ✅ X passed / 0 failed
- **Dokunulan Katmanlar:** [DB, API, UI vb.]
- **Gözle Doğrulama:**
  👉 `[URL veya Komut]` ➔ `[Beklenen Sonuç]`
```
