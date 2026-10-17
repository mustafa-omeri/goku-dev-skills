# Observation Log

### Observation 1: Uçtan Uca Veri Döngüsü ve Sessiz Mock Yasağı (Anti-Phantom Completion)

**Date:** 2026-10-16
**Session context:** Kalansüre projesinde 'Hatalı Tarih Bildir' formunun localStorage'a yazılıp backend'e bağlanmadan DONE kabul edilmesi vakası.
**Skill:** musgoku-prd, musgoku, sprint-delivery-workflow, development-workflow
**Type:** open-source
**Phase/Area:** Requirements, Architecture, Testing, Definition of Done

**Issue:** Kod ajanı form bileşenini hazırlayıp veriyi yalnızca tarayıcının `localStorage` alanına yazmış, kullanıcıya 'Editörlerimiz inceleyecek' toast mesajı göstermiş ancak backend/DB bağlantısı, RLS politikası veya moderasyon masası kurmadan sprinti DONE olarak kapatmıştır. Bu durum hem kullanıcıyı aldatan sahte bir tamamlama (illusion of completeness) yaratmış hem de form gerçek bir DB'ye bağlandığında rate limiting, honeypot ve RLS eksikliği nedeniyle tüm saldırı kapılarını açacak bir güvenlik açığı doğurmuştur.

**Suggested improvement:**
1. `development-workflow.md` Adım 2.1 ve `sprint-delivery-workflow.md` içine '5 Zorunlu Halka (E2E Data Lifecycle)' kuralı eklendi.
2. 'Sessiz Mock Yasağı (No Silent Mocking)': Gerçek backend gerektiren işi haber vermeden mock/localStorage arkasına saklamak ihlal sayıldı.
3. Public formlarda 6 katmanlı güvenlik kontrol listesi (Context Binding, Honeypot, Turnstile, Rate Limit, Sanitization, Blind Insert RLS) zorunlu kılındı.
4. `KULLANICI_TEST_REHBERI.template.md` içine 3 katmanlı doğrulama (Görsel UX + Network F12 + DB SQL kanıtı) eklendi.

**Principle:** Bir kullanıcı arayüzü veri üretiyorsa, o verinin iletimi (API), güvenliği (Rate Limit/Abuse), saklanması (DB/RLS) ve tüketilmesi (Consumer/Moderasyon Masası) uçtan uca doğrulanmadan veya mock olduğu açıkça beyan edilmeden hiçbir özellik 'DONE' kabul edilemez.

---

### Observation 2: Kapsam-Duyarlı Doğrulama (Scope-Aware Verification vs. Blind Test Execution)

**Date:** 2026-10-16
**Session context:** Projelerde yalnızca `.agent/` (skill/kural) veya `*.md` dosyaları commitlemek istendiğinde bile ajanın körlemesine `pnpm test`, `pnpm build`, `test:e2e` koşturması.
**Skill:** mandatory-git-release-workflow, development-workflow, AGENTS.md
**Type:** open-source
**Phase/Area:** Verification, Git Release, Resource Efficiency

**Issue:** Kod ajanı yalnızca markdown dokümanı veya `.agent/` kuralları değiştiği durumlarda dahi, kuraldaki genel "doğrulama kapılarını çalıştır" ifadesini mekanik biçimde yorumlayarak tüm uygulamanın build, typecheck ve e2e test pipeline'ını baştan sona koşturmaktadır. Bu durum 2-3 dakikalık boş bekleme süresine, devasa token/context tüketimine ve kaynak israfına yol açmaktadır.

**Suggested improvement:**
1. `AGENTS.md` §3.3 ve `development-workflow.md` Adım 4'e "Kapsam-Duyarlı Doğrulama İlkesi" eklendi.
2. `mandatory-git-release-workflow.md` ve `git-release-workflow/SKILL.md` içine kural bağlandı: Kaynak kod (`src/**`, `package.json`, `pom.xml`) değişmemişse, uygulama build/test adımları çalıştırılmaz (atlanır / skipped).
3. Raporlarda dürüst beyan kuralı getirildi: *"Uygulama Testleri: Kapsam dışı (Yalnızca dokümantasyon / .agent değişti)"*.

**Principle:** Değişikliğin etki alanında olmayan bir testi çalıştırmak güvenlik sağlamaz; yalnızca zaman, CPU ve token israfı üretir. Doğrulama kapıları etki alanına duyarlı (scope-aware) olmalıdır.

---

### Observation 3: Adaptif Viewport, UX Durumları ve Modal Standartları (Responsive UX Ergonomics & Adaptive Modals)

**Date:** 2026-10-17
**Session context:** UI geliştirme süreçlerinde UX durumlarının (Loading, Empty, Error, Feedback) unutulması, her çözünürlüğün (özellikle Mobil ve Tablet farkının) kullanıcı tarafından her defasında ayrı ayrı talep edilmek zorunda kalınması ve açılan modalların mobilde responsive olmayıp klavye/scroll taşması yaratması vakası.
**Skill:** design-skills-enforcement, frontend-design, ui-styling, development-workflow, task-observer
**Type:** open-source
**Phase/Area:** UI/UX, Responsive Design, Component Architecture, Acceptance Criteria

**Issue:** Tasarım kuralları ve prompt makroları (`[UI-POLISH]`, `[DESIGN-REFRESH]`) estetik zanaata odaklanırken; arayüzün dinamik durumları (loading skeleton, empty state, inline error, feedback toast) ve cihaz kullanım ergonomisi atlanmaktaydı. Ajanlar "responsive" kavramını sadece grid'i tek sütuna büzüştürmek olarak uyguluyor; tabletin 2 sütunlu/split-view ergonomisi ile mobilin başparmak (Thumb Zone) gereksinimlerini göz ardı ediyordu. Ayrıca masaüstü modal dialog'ları mobilde ortalanmış dar bir kutu olarak bırakılıyor, klavye açılınca inputlar altında kalıyor ve taşmalar oluşuyordu.

**Suggested improvement:**
1. `design-skills-enforcement.md`: §2.1 prompt makroları genişletildi (`[UX-POLISH]`, `[RESPONSIVE-POLISH]`), §2.2 'Zorunlu 4 UX Durumu Sözleşmesi', §2.3 '3 Katmanlı Çözünürlük & Cihaz Ergonomisi Sözleşmesi' ve §2.4 'Adaptif Modal & Dialog Standartları' (Masaüstü: Dialog, Mobil: Bottom Sheet / Drawer) eklendi.
2. `development-workflow.md`: Adım 2.1 uygulama planına ve Adım 4.1 test edilebilirliğe 3 cihaz ergonomisi (Mobil, Tablet, Masaüstü) ve modal doğrulama zorunluluğu bağlandı.
3. `KULLANICI_TEST_REHBERI.template.md`: §3.3 manuel test adımlarına Masaüstü (>1024px), Tablet (768px-1024px) ve Mobil (375px Bottom Sheet) kabul kriterleri eklendi.
4. `ui-styling/SKILL.md` & `frontend-design/SKILL.md`: Adaptif Responsive Dialog (`useMediaQuery` ile Masaüstü Dialog ↔ Mobil Drawer) ve Tablet Split-View hazır kalıpları eklendi.

**Principle:** Tasarım sadece masaüstünde başlayıp dar ekranda büzüşen bir şey değildir. Mobil (Bottom Sheet, Thumb Zone, tek sütun), Tablet (Split-View, 2-sütun) ve Masaüstü (Multi-column) üçlüsü kullanıcı belirtmeden otomatik uygulanmalı; modallar mobilde asla ortalanmış küçük pencere olarak kalmamalı, alt çekmeceye (drawer) dönüşmelidir.


