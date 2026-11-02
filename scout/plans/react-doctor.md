# 🔭 Scout Değerlendirme Raporu: millionco/react-doctor

## 1. Depo Özeti ve Künye
- **URL:** https://github.com/millionco/react-doctor
- **Sahibi:** millionco
- **Analiz Tarihi:** 2026-10-30 13:43
- **Tespit Edilen Katman:** Frontend + Tooling / Agentic
- **Dosya Sayısı & Boyut:** 7395 dosya (~41135 KB)
- **Teknoloji Yığını:** TypeScript, Turborepo, Oxlint Plugin, ESLint Plugin, Vite Plus (`@voidzero-dev/vite-plus-core`), Fuzzing (`@react-doctor/fuzz`), Evals

## 2. Çekirdek Felsefe ve Mimari (Repo İncelemesi)
Million.js ekibi tarafından geliştirilen `react-doctor`, React projelerindeki performans darboğazlarını, gereksiz re-render'ları ve yanlış API/state yönetim desenlerini statik analiz (AST) ve linter kuralları aracılığıyla otomatik tespit eden hibrit bir tanı/reçete aracıdır.

- **Monorepo ve Kural Motoru:** Proje `@react-doctor/core`, `oxlint-plugin-react-doctor`, `eslint-plugin-react-doctor`, `@react-doctor/api` ve eval paketlerinden oluşan bir mimariye sahiptir.
- **Yüksek Hızlı Analiz:** Rust tabanlı `oxlint` ekosistemi ve `vite-plus` entegrasyonu ile AST analizini milisaniyeler seviyesinde tamamlar.
- **Kapsamlı Dokümantasyon & Araştırma:** `docs/` altında yer alan `zustand-rule-research.md`, `mobx-rule-research.md`, `react-router-rule-research.md`, `three-r3f-grading-rubric-coverage.md` ve `HOW_TO_WRITE_A_RULE.md` dosyaları; state selector optimizasyonları, 3D WebGL (Three.js/R3F) render sızıntıları ve router render cascade problemlerine dair derinlemesine teknik analizler ve AST tespit kuralları barındırmaktadır.

## 3. Bizim Sistemle Kıyaslama (Delta Analizi)
- **Mevcut Durumumuz:**
  - Havuzumuzda React tarafında `react-best-practices`, `codebase-design` ve `ui-ux-pro-max` bulunmaktadır. `react-best-practices` re-render'lar, waterfall'lar, bundle bütçesi ve micro-optimizasyonlar konusunda çok güçlü kural setlerine sahiptir.
  - Kod kalitesi ve koku denetimi için `code-review` (Martin Fowler smells) ve `diagnosing-bugs` işlemektedir.
- **Dış Repodaki Değer:**
  - Dış reponun 7000+ dosyalık devasa linter motorunu depomuza klonlamak repo ağırlığını ve bakım maliyetini gereksiz artırır.
  - Ancak deponun `docs/` klasöründeki Zustand, MobX, React Router ve özellikle Three/R3F render optimizasyon rubrikleri, bizim `react-best-practices` ve `ui-ux-pro-max` referanslarımızda bulunmayan özel kütüphane seviyesi anti-pattern reçetelerini içermektedir.
- **Kesişim & Ayrışma:**
  - Bütün CLI ve linter monoreposunu içeri almak token şişkinliği ve kütüphane bağımlılığı yaratır (duplicate & bloat).
  - Seçici olarak yalnızca "kural araştırmaları" (rule research catalog) ve "anti-pattern reçeteleri" soyutlanıp referanslarımıza işlendiğinde sıfır runtime maliyetle çok yüksek zanaat derinliği elde edilir.

## 4. Karar ve Gerekçe
**KISMEN_ALINABILIR: react-best-practices ve ui-ux-pro-max kütüphanemizi; Million.js ekibinin oxlint/eslint kural araştırmalarındaki Zustand, MobX, React Router ve Three/R3F anti-pattern katalogları ve performans teşhis rubrikleri ile cerrahi olarak zenginleştirebiliriz.**

Dış repo üretim seviyesinde linter paketleri barındırmakta olup doğrudan kopyalanması gereksiz kod yükü yaratır; ancak içerisindeki mimari teşhis kuralları React ekosistemimizdeki kural setlerini derinleştirmek için eşsiz bir kaynaktır.

## 5. Cerrahi Entegrasyon Planı / Eylem Maddeleri
1. **Hedef Skill:** `.agent/skills/react-best-practices/`
   - **Eklenecek Bölüm:** `references/state-and-routing-antipatterns.md` dosyası oluşturularak Zustand selector sızıntıları (non-primitive selector subscribes), React Router waterfall layout sorunları ve MobX observable re-render tuzakları damıtılacaktır.
2. **Hedef Skill:** `.agent/skills/ui-ux-pro-max/`
   - **Eklenecek Bölüm:** 3D/Canvas tabanlı arayüzler için `three-r3f-grading-rubric-coverage.md` temel alınarak R3F (React Three Fiber) bellek yönetimi ve requestAnimationFrame sızıntı denetim maddeleri UX kuralları listesine eklenecektir.
3. **Doğrulama Kapısı:**
   - Kural front-matter ve tetikleyici sözleşmelerinin bozulmadığını test etmek için:
     `python .agent/skills/musgoku/scripts/rules_gates.py --strict`