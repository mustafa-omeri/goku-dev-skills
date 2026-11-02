# 🔭 Scout Değerlendirme Raporu: raphaelsalaja/skill

## 1. Depo Özeti ve Künye
- **URL:** https://github.com/raphaelsalaja/skill
- **Sahibi:** raphaelsalaja
- **Analiz Tarihi:** 2026-10-30 13:38
- **Tespit Edilen Katman:** Tooling / Agentic (Ajan Kuralları, UI/UX Doğrulama ve Yönerge Seti)
- **Dosya Sayısı & Boyut:** 50 dosya (~398 KB)
- **Teknoloji Yığını:** Markdown kuralları (`SKILL.md`), Vanilla JavaScript / DOM ölçüm scriptleri (`measure.js`), Standalone HTML Rapor ve İnceleme Arayüzleri (`report.html`, `viewer.html`)

## 2. Çekirdek Felsefe ve Mimari (Repo İncelemesi)
`raphaelsalaja/skill`, Claude Code ve benzeri kodlama ajanları için özel olarak tasarlanmış, arayüz (UI) geliştirme odaklı bir kural ve prosedür kütüphanesidir. İki ana gruptan oluşur:
1. **Principles (İlkeler):** `scope`, `reuse`, `restraint`, `copy`, `defaults`. Ajanın gereksiz kod üretmesini engelleyen, mevcut projeyi yeniden kullanmasını öğütleyen ve mikro-arayüz detaylarını (Title Case, em-dash yasağı, scroll/focus davranışları) kurala bağlayan prensipler.
2. **Procedures (Prosedürler):** `alignment`, `audit`, `deconstruct`, `lab`, `prototype`, `match`, `verify`, `ship`. Ajanın canlı sayfayı ölçmesi, animasyonları zaman çizelgesine dökmesi (`deconstruct`), varyant laboratuvarı kurması (`lab`) ve piksel hizalama hatalarını raporlaması (`alignment`).
3. **"The Pair" Formatı:** Projedeki her kural, katı bir `[rule-id] | bozuk satır (broken line) | düzeltilen satır (replacement)` eşleşmesine dayanır. Raporlamalarda bulgular `file:line - [rule-id]` şeklinde sunulur.

**Güçlü Yönleri:**
- `alignment` ve `audit` içindeki interaktif HTML raporları (`report.html`, `viewer.html`, `measure.js`), ajanın yaptığı CSS/hizalama denetimlerini tarayıcıda görselleştiren çok şık ve hafif bir yaklaşıma sahiptir.
- Kural çifti ("The pair") prensibi, ajanın soyut öğütler yerine somut kod satırı değişimleriyle eğitilmesini sağlar.

**Zayıf Yönleri:**
- Yalnızca basit Claude Code eklentisi seviyesindedir; test otomasyon kapıları (measurable gates), CI/CD doğrulaması, veritabanı/backend katman denetimleri veya dikey dilim mimarisi (full-stack vertical slice) barındırmaz.
- Kod tabanı derinliği ve kuralların uygulanış katılığı zayıftır (Python/AST/CLI seviyesinde doğrulama scriptleri yerine tamamen prompt yönergelerine ve birkaç statik HTML dosyasına dayanır).

## 3. Bizim Sistemle Kıyaslama (Delta Analizi)
- **Mevcut Durumumuz:** Sistemimiz (`skillSetWorks`), `ui-polish`, `frontend-design`, `ui-ux-pro-max`, `design-system`, `canvas-design`, `code-review`, `verify-last`, `verify-prd` ve `karpathy-guidelines` gibi 40'tan fazla modül ve 16 adet Python tabanlı ölçülebilir kapı (`check_design_slop.py`, `check_theme_contrast.py`, `check_handoff.py` vb.) ile donatılmıştır. 5 katmanlı dikey dilim denetimi ve katı Git/Handoff protokolleri bulunmaktadır.
- **Dış Repodaki Değer:**
  1. `measure.js` ve standalone `report.html` mantığı: Ajanın tarayıcıda sub-pixel veya 1-2px hizalama kaçaklarını interaktif bir HTML raporuna dökmesi fikri oldukça estetiktir.
  2. `The Pair` kural sözleşmesi: Kural ihlallerini `file:line - [rule-id]` formatında tek satırlık negatif/pozitif örnek çiftiyle standartlaştırma yaklaşımı.
- **Kesişim & Ayrışma:**
  - `ship` -> Bizim `commitx` / `git-release-workflow` yeteneklerimiz çok daha üstün ve güvenlidir (semantik versiyonlama, interaktif onay koruması, branch/tag otomasyonu).
  - `audit` / `verify` -> Bizim `code-review`, `verify-sprint`, `verify-last` ve `verify-prd` araçlarımız çok daha kapsamlıdır.
  - `defaults` / `copy` -> Bizim `ui-ux-pro-max` (119 UX kuralı, 74 font) ve `frontend-design` referanslarımız dış repoyu fersah fersah geride bırakmaktadır.

## 4. Karar ve Gerekçe
**KISMEN_ALINABILIR: HTML tabanlı görsel denetim raporlayıcıları ve "The Pair" kural sözleşmesi zenginleştirme amacıyla referans alınabilir.**

Bütünsel olarak depoyu içe aktarmak gereksiz şişkinlik (bloat) yaratır; çünkü mevcut sistemimiz hem backend hem frontend hem de ajan yönetiminde dış repodan katbekat olgun ve disiplinlidir. Ancak `measure.js` / `viewer.html` ile yapılan DOM görsel ölçüm deseni ve "The Pair" (bozuk kod vs temiz kod) formatı, `ui-polish` ve `code-review` becerilerimizin hata raporlama formatına cerrahi olarak enjekte edilmeye değerdir.

## 5. Cerrahi Entegrasyon Planı / Eylem Maddeleri
1. **`ui-polish` & `ui-ux-pro-max` Entegrasyonu:**
   - `measure.js` ve DOM sub-pixel hizalama denetimi kuralları incelenerek, `check_design_slop.py` veya `ui-polish` kılavuzuna "Sub-pixel & Radius Alignment Checklist" maddeleri olarak eklenebilir.
2. **`code-review` Bulguları Standardizasyonu:**
   - İnceleme bulguları raporlanırken `The Pair` kuralı esinlenerek `dosya:satir - [kural-id] | Hatalı | Düzeltilmiş` formatı opsiyonel çıktı standardı olarak uyarlanabilir.
3. **Standalone HTML Denetim Raporu Şablonu:**
   - `docs/kullanici-rehberi.html` yapımıza benzer şekilde, UI audit işlemleri için hafif bir `design-audit-report.html` şablonu değerlendirilebilir.