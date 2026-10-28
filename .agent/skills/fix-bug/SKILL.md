---
name: fix-bug
description: Sistematik altı aşamalı hata ayıklama ve kırmızı geri bildirim döngüsü orkestratörü; kök neden tespiti, regresyon testi ve cerrahi onarım sağlar. Tetikleyiciler: "/fix-bug", "fix bug", "[FIX-BUG]", "hata ayıkla", "bug çöz", "neden çalışmıyor". Tetiklenmez: yeni özellik ekleme `musgoku`'ya aittir. Tam sözlük: .agent/rules/skill-trigger-routing.md
---

# Fix Bug Ensemble Orchestrator

Bu yetenek, sisteme yeni hatalar ve regresyonlar sokmadan kök nedeni bilimsel yöntemle tespit edip çözen 6 aşamalı sistematik hata ayıklama protokolünü (`diagnosing-bugs` → `musgoku` → `karpathy-guidelines`) işletir.

## Bağlı Kurallar ve Alt Yetenekler

- **Birincil Yetenek:** `diagnosing-bugs` (`.agent/skills/diagnosing-bugs/SKILL.md`)
- **Destekleyici Yetenekler:** `musgoku`, `tdd`, `karpathy-guidelines`
- **Zorunlu Kural:** `.agent/rules/bug-diagnosis-enforcement.md` (Önce Kırmızı Geri Bildirim Döngüsü)

---

## 6 Aşamalı Cerrahi Hata Ayıklama Akışı

1. **Aşama 1 — Kırmızı Geri Bildirim Döngüsü Kurma (Zorunlu Ön Koşul):**
   - ⛔ **Tahminle Kod Değiştirme Yasağı:** Uygulama kodunda tek bir satır dahi değiştirmeden önce, hatayı deterministik olarak yeniden üreten ve başarısız olan (**RED / FAIL**) bir birim testi, entegrasyon testi veya komut satırı reprodüksiyon senaryosu kur.
2. **Aşama 2 — Kök Neden Analizi (Semptom Değil Mekanizma):**
   - Belirtiyi (`undefined` gelmesi, ekranın boş kalması vb.) bastırmak yerine verinin üretildiği noktadan tüketildiği noktaya kadar 5 katmanı (DB → View/RPC → API → State → UI) izle.
   - En az 2 hipotez kur ve log/stack trace kanıtıyla yanlış olanı ele.
3. **Aşama 3 — Cerrahi Onarım (`karpathy-guidelines`):**
   - İlgisiz kodları yeniden biçimlendirmeden, yalnızca kök nedeni gideren minimal ve odaklı düzeltmeyi uygula.
4. **Aşama 4 — Yeşil Doğrulama (Red → Green):**
   - Aşama 1'de kurulan kırmızı testin artık başarıyla geçtiğini (**GREEN / PASS**) terminal çıktısıyla kanıtla.
5. **Aşama 5 — Regresyon ve Kapı Denetimi:**
   - Mevcut test paketini ve birleşik doğrulama kapılarını çalıştırarak yan etki oluşmadığını doğrula:
     ```bash
     python .agent/skills/musgoku/scripts/run_all_gates.py
     ```
6. **Aşama 6 — Kalıcı Hafıza ve Tuzak Kaydı:**
   - Hatanın kök nedenini (`Problem / Root Cause / Solution / Files Changed`) `<repo-kök>/knowledge-base.md` dosyasına ekle.
   - Tekrarlanma riski olan proje tuzaklarını `<repo-kök>/HANDOFF.md` (§0 Tuzaklar) tablosuna işle.

---

## Standart Çıktı Raporu

```markdown
### 🐛 FIX-BUG: KÖK NEDEN VE CERRAHİ ONARIM RAPORU
- **Semptom / Gözlenen Hata:** [Ne bozuktu?]
- **Kırmızı Döngü Kanıtı (Önce):** `[Test/Komut]` → `FAIL`
- **Kök Neden (Root Cause):** [Gerçek teknik neden]
- **Cerrahi Çözüm & Değişen Dosyalar:** [Yapılan minimal değişiklik]
- **Yeşil Döngü & Regresyon Kanıtı (Sonra):** `[Test/Komut]` → `PASS` · `run_all_gates.py` → `[OK]`
- **Bilgi Tabanı Kaydı:** `knowledge-base.md` ve `HANDOFF.md` güncellendi.
```
