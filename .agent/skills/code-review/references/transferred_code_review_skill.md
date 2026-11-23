# Cerrahi Entegrasyon Referansı: awesome-skills/code-review-skill

> **Kaynak Repo:** `https://github.com/awesome-skills/code-review-skill`  
> **Hedef Yetenek:** `.agent/skills/code-review/`  
> **Motto:** 21.000 satırlık statik dil kılavuzları token şişkinliği nedeniyle elendi; `pr-analyzer.py` deterministik triaj matematiği ve evrensel kalite anti-pattern'leri aktarıldı.

---

## 1. Deterministik Diff Karmaşıklık ve Risk Triajı (`diff_triage.py`)

Büyük diff'lerde incelemeye başlamadan önce `scripts/diff_triage.py` koşturularak şu metrikler çıkarılır:
- **Boyut Kategorisi:** `XS (<50)`, `S (<200)`, `M (<400)`, `L (<800)`, `XL (>=800 — bölünmeli)`.
- **Karmaşıklık Skoru (`0.0 - 1.0`):** Satır hacmi (`0.4`), dosya sayısı (`0.2`), test-dışı kod oranı (`0.2`) ve dil çeşitliliği (`0.2`).
- **Otomatik Risk Bayrakları:**
  * `NO_TEST_CHANGES` (üretim kodu değişip test eklenmediyse)
  * `LOW_TEST_RATIO` (test satır oranı `< %20`)
  * `SECURITY_SENSITIVE_FILE` (`auth`, `token`, `permission`, `rbac`, `.env`)
  * `DATABASE_CHANGE` (`migration`, `*.sql`)

---

## 2. Evrensel Kod Kalitesi Anti-Pattern Kontrol Listesi

Fowler smell kataloğuna ek olarak Standartlar ekseninde şu 5 evrensel kusur taranır:

1. **TOCTOU (Time-of-Check to Time-of-Use):** `if exists(x): write(x)` gibi kontrol ile işlem arasında yarış durumu yaratan kilitsiz akışlar.
2. **No-Op State / DB Updates:** Gerçekte hiçbir alanı değiştirmeyen veya değişim yokken gereksiz `UPDATE` / `setState` tetikleyen çağrılar.
3. **Parameter Sprawl (`>= 4` konumsal argüman):** Çoklu positional parametre yerine tipli Options/DTO nesnesi ve mutually-exclusive `enableX`/`disableY` bayraklarının elenmesi.
4. **Stringly-Typed Kod:** Domain durumları (`"pending"`, `"active"`) için ham string yerine enum / union / sabit metadata kullanımı.
5. **Önem Derecesi Etiketleri (Severity Tiers):**
   - `🔴 [blocking]` — Birleştirme öncesi zorunlu (bug, güvenlik, veri kaybı)
   - `🟡 [important]` — Düzeltilmeli (mimari sapma, performans, eksik test)
   - `🟢 [nit]` — İsteğe bağlı küçük iyileştirme
   - `💡 [suggestion]` / `🎉 [praise]` — Engelleyici olmayan yapıcı not
