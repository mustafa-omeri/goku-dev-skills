---
name: project-summary
description: Projenin kısa veya kapsamlı özetini slug ile docs/ altında üreten ve PRD dokümanlarını sentezleyen orkestratör. Long modunda tüm PRD ve referans dokümanlarını tek bir belgede konsolide eder. Tetikleyiciler: "/project-summary", "/proje-ozeti", "projenin kapsamlı özetini çıkar", "proje özeti çıkar", "proje özeti", "[PROJECT-SUMMARY]", "summarize project", "project summary". Tetiklenmez: salt sprint kabul testi verify-sprint'e, PRD retrospektif denetimi verify-prd'ye aittir. Tam sözlük: .agent/rules/skill-trigger-routing.md
---

# Project Summary Orchestrator

Bu yetenek; projelerin mevcut mimarisini, ürün hedeflerini, teknoloji yığınını ve şartnamelerini hızlıca özetleyen (`short`) veya projedeki tüm PRD dokümanlarını ve referans belgelerini tek bir ana kaynakta konsolide eden (`long`) orkestrasyon motorudur.

---

## Bağlı Standartlar & Anayasal Kurallar

1. **Zorunlu Konum & Slug Deseni:**
   - Çıktı dokümanı **kesinlikle `/docs` dizini altında** ve proje slug'ı kullanılarak adlandırılır:
     - `docs/<SLUG>_PROJECT_SUMMARY_SHORT.md` (Örn: `docs/KALANSURE_PROJECT_SUMMARY_SHORT.md`)
     - `docs/<SLUG>_PROJECT_SUMMARY_LONG.md` (Örn: `docs/KALANSURE_PROJECT_SUMMARY_LONG.md`)
   - `/docs` dışına dosya yazmak yasaktır ve script/kural seviyesinde engellenir.
2. **Dil Uyumu (`primary_language`):**
   - Çıktı dili, projenin `PROJECT_BRIEF.md` dosyasındaki `primary_language` alanına göre (`tr` veya `en`) şekillenir.
3. **Mevcut Dosyalarda Versiyonlama Damgası:**
   - Doküman zaten mevcutsa; üzerine doğrudan yazılmaz. Tarih (`YYYY-MM-DD`), saat (`HH:mm:ss`), güncelleyen kullanıcı (`git config user.name` / OS kullanıcısı) ve revizyon numarası (`v1.0 ➜ v1.1`) damgalanır. Önceki sürüm `docs/archive/` altına yedeklenir ve Revizyon Geçmişi tablosu korunur.
4. **`PROJECT_BRIEF.md` Zorunlu Mimari Senkronizasyonu:**
   - Üretilen özet dokümanı, `PROJECT_BRIEF.md` frontmatter'ındaki `related_docs:` listesine otomatik eklenir ve senkron tutulur.
5. **Long Versiyonunda Tek Doküman Sentez Zorunluluğu:**
   - `long` modunda; projede tespit edilen tüm PRD belgeleri (`docs/*prd*.md`, `PRD.md`) ve referans dokümanları (`PROJECT_BRIEF.md`, `PRODUCT.md`, `GLOSSARY.md`, `DESIGN.md`, `DB_MIGRATIONS.md`, `HANDOFF.md`, `knowledge-base.md`, `docs/adr/`) incelenerek **tek bir kapsamlı ana dokümanda** sentezlenir.

---

## 4 Aşamalı İcra Protokolü

### 1. Parametre & Mod Tespiti
- Kullanıcı *"projenin kapsamlı özetini çıkar"* dediğinde varsayılan olarak **`long`** mod çalışır.
- Kullanıcı *"projenin kısa özetini çıkar"* dediğinde **`short`** mod çalışır.
- Komut satırında veya slash çağrısında:
  - `/project-summary` (varsayılan: long)
  - `/project-summary --short` veya `/project-summary --long`
  - `/proje-ozeti --short` veya `/proje-ozeti --long`

### 2. Belge Envanteri Taraması (Long Modu)
Proje kökü ve `docs/` altında şu belgeler taranır:
- Şartnameler: `docs/**/*prd*.md`, `docs/**/*spec*.md`, `PRD.md`
- Mimari & Stack: `PROJECT_BRIEF.md`, `package.json`, `pom.xml`
- Ürün & Vizyon: `PRODUCT.md`
- Terimler: `GLOSSARY.md`
- Veritabanı: `DB_MIGRATIONS.md`
- Tasarım: `DESIGN.md`
- Yaşayan Durum: `HANDOFF.md`
- Kararlar & Dersler: `knowledge-base.md`, `docs/adr/*.md`

### 3. Konsolidasyon, Versiyonlama & Arşivleme
- Dosya zaten varsa:
  - Mevcut içerik `docs/archive/<SLUG>_PROJECT_SUMMARY_<MODE>_<TIMESTAMP>.md` dosyasına yedeklenir.
  - Sürüm artırılır (`v1.0 ➜ v1.1`).
  - Tarih, saat ve kullanıcı bilgisiyle damga (`> 📌 **Versiyonlama Damgası:** ...`) vurulur.
- Otomasyon CLI aracı çalıştırılır:
  ```bash
  python .agent/skills/project-summary/scripts/summarize_project.py --mode [short|long]
  ```

### 4. Mimari Senkronizasyon ve Doğrulama
- Üretilen dokümanın `docs/` altında olduğu ve `PROJECT_BRIEF.md` `related_docs` listesine eklendiği doğrulanır:
  ```bash
  python .agent/skills/project-summary/scripts/summarize_project.py --mode [short|long] --check
  ```

---

## Standart Çıktı Raporu

İşlem tamamlandığında kullanıcıya şu rapor sunulur:

```markdown
### 📋 PROJE KONSOLİDE ÖZETİ TAMAMLANDI
- **Üretilen Dosya:** `docs/<SLUG>_PROJECT_SUMMARY_<MODE>.md`
- **Çalışma Modu:** [SHORT | LONG]
- **Sürüm & Damga:** `[v1.0 / v1.1]` · [YYYY-MM-DD HH:mm:ss] · [Kullanıcı]
- **İncelenen PRD Dokümanları:** [X adet veya "PRD bulunamadı; diğer dokümanlardan sentezlendi"]
- **Arşiv Yedeği:** [docs/archive/... veya "İlk oluşturma (arşiv gerekmedi)"]
- **PROJECT_BRIEF.md Senkronu:** ✅ `related_docs` listesine eklendi
```
