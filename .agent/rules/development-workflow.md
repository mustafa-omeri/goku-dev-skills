---
name: MuSGoKu Development Workflow
description: Her geliştirme talebinde doğru sırada skill okuma, MCP kullanımı, kalite kontrolü, devir güncellemesi ve kullanıcı onayı adımlarını tanımlar.
sinif: SUREC
---

# 🔀 MuSGoKu Geliştirme İş Akışı

---

## Adım 0 — Oturum Köprüsü

- Kod yazmadan, düzeltme yapmadan veya test koşmadan önce repo kökündeki
  `HANDOFF.md` dosyasını oku.
- Projenin iş kavramları ve ortak dili için varsa `GLOSSARY.md` dosyasını oku.
- Dosya yoksa veya boşsa kendin yaz.
- ⛔ **Mükerrer Görev Dosyası Yasağı (Anti-Task-File Proliferation):** `TASK.md`, `ACTIVE_TASK.md`, `TODO.md` gibi ad-hoc takip dosyaları AÇILMAZ. Kullanıcı talep etse dahi, tek kaynağın `HANDOFF.md` (§3 Sıradaki İşler & Aktif Görev) olduğu nazikçe ve güvenle beyan edilir.
- Ayrıntı: [handoff-session-continuity.md](./handoff-session-continuity.md)

---

## Adım 1 — Talebi analiz et ve skill seç

Genel matris ve yönlendirme:
[`.agent\skills\musgoku\SKILL.md`](../skills/musgoku/SKILL.md)

Backend için ayrıntılı matris `references\` altındaki dosyaların içindedir.

---

## Adım 2 — Best practice doğrulaması (MCP)

| Durum | MCP |
|---|---|
| Kütüphane API'si değişmiş olabilir | `context7` → `resolve-library-id` → `query-docs` |
| Karmaşık mimari karar, güvenlik sınırı | `sequential-thinking` |
| 2+ alternatifli mimari karar, kütüphane seçimi, teknoloji ikilemleri | `council` / `karpathy-guidelines` (3 Aşamalı Kör Hakemlik & Borda Skoru) |
| UI testi / ekran incelemesi | tarayıcı/ekran aracı (proje yapısına göre) |
| Dosya arama / proje keşfi | dosya sistemi aracı |

Tetikleyici tablosu ve sınırlar: [mcp-usage-enforcement.md](./mcp-usage-enforcement.md)

---

## Adım 2.1 — Uygulama Planı, 3. Parti Açık Kaynak Araştırması ve Kullanıcı İnceleme/Onay Kapısı

⛔ **KESİN VE NET KURAL:** İster bir sprint planı dahilinde olsun, ister sprint dışı küçük dilimlere (slice'lara) veya task listesine bölünmüş olsun:
**"Ne yapılacağı" (what) bilinse dahi, "nasıl yapılacağı" (how) planlanmadan DOĞRUDAN KODA BAŞLAMAK KESİNLİKLE YASAKTIR.**

⛔ **Serbest Metin Plan Yasağı ve Otonom Beceri Devreye Alma (Anti-Adhoc-Planning Slop):**
Kullanıcı işin nasıl yapılacağını sorduğunda, mimari plan istendiğinde veya yeni bir özellik geliştirme bağlamına girildiğinde; ajanın skillset kurallarından ve şablonlarından kopuk, ad-hoc, serbest metinli yüzeysel bir yapılacaklar listesi çıkarması **KESİNLİKLE YASAKTIR**.
Ajan kullanıcının herhangi bir hatırlatma yapmasını beklemeden; `doc-coauthoring` (mimari plan ve şartname kurgusu), `musgoku` (5 katmanlı dikey dilim mimarisi), `tdd` (test odaklı faz ve dikiş noktası planlama) ve (varsa) `sprint-delivery-workflow` (Gherkin kabul kriterleri & Kanban kartları) yeteneklerini **otonom olarak (unprompted)** devreye sokar ve planını bu standart yapı taşlarıyla sunar.

Geliştirmeye başlamadan önce ajan sırasıyla şu adımları işletmek zorundadır:

1. **Detaylı Uygulama Planı ("Nasıl Yapılacak?"):**
   - 🏛️ **Mimari Alternatifler ve Konsey Eşiği (Council Deliberation Threshold):**
     * **Eşik Kuralı (Tiered Threshold):** Geliştirilecek özellik veya modül için 2 veya daha fazla geçerli mimari yaklaşım, kütüphane seçimi veya veri modeli alternatifi varsa (örn. Zustand vs Context vs Redux, REST vs GraphQL, CSS Grid vs Flexbox layout omurgası, yeni DB şeması/ORM modeli), ajanın tek bir alternatifi dayatması **YASAKTIR**.
     * **Körleme & Borda Oylaması:** Planda en az `Option A (Yalın/Minimalist)`, `Option B (Genişletilebilir)` ve gerekiyorsa `Option C (Hibrit)` alternatifleri çıkarılır; `council_ranker.py` / Kör Hakemlik mantığıyla artı/eksi ve Borda skoru analizi sunulur.
     * **Eşik Altı İstisnası (Trivial Bypass):** Tek alternatifli basit bug fix'ler, tek bileşenli CSS/UI rötuşları, rutin CRUD tekrarları veya typo düzeltmeleri için Konsey toplanmaz; doğrudan `musgoku` + `tdd` icra edilir.
     * **Birleşik Planlama Ekosistemi (Unified Planning Integration):** Planlama adımı izole bir ada değildir; Fikir Havuzu (`my-idea`) → Ürün Açığı Keşfi (`feature-architect` / `gap_scanner.py`) → Şartname & PRD (`doc-coauthoring`) → Mimari Alternatif Konseyi (`council`) → Görev Tahtası (`sprint-delivery-workflow.md` / `KANBAN.md`) → Uygulama Planı (`/plan`, `PLAN.template.md`) → TDD Dikiş Noktası & 5 Katmanlı Dilim (`development-workflow.md` Adım 2.2) zinciriyle birbirine mantıksal olarak bağlanır.
   - **5 Katmanlı Dikey Dilim (Full-Stack Vertical Slice):** DB Şeması/Migration → Backend View/RPC → İstemci API Entegrasyonu → Arayüz/UX → Döngü Kapanışı / Admin Formu.
   - **TDD Dikiş Noktaları (Seams) ve Kırmızı-Yeşil Fazları:** Hangi dikiş noktasında kırmızı test yazılacak, minimal geçiş kodu ne olacak.
   - **Gherkin Kabul Kriterleri:** `Feature` ve `Scenario` (`Given ... When ... Then ...`) somut test adımları.
   - **WIP Uyumlu Faz / Kart Dökümü:** `KANBAN.md` ve `SPRINT_PLAN.md` yapısına oturacak aşamalar (WIP limiti maksimum 3).
   - Değişecek, oluşturulacak veya silinecek dosyalar, modül sınırları, state yönetimi ve veri akışı adımları çıkarılır.

2. ⛔ **Uçtan Uca Veri Döngüsü (E2E Data Lifecycle) ve 5 Zorunlu Halka:**
   Veri üreten veya toplayan her özellik (form, bildirim, geri bildirim, kayıt vb.) için şu 5 halka planda eksiksiz tanımlanmalıdır:
   - **Halka 1 (Üretim & UI):** Form alanları, tip kontrolü, UX durumları (submitting, success, error).
   - **Halka 2 (Güvenlik & İstismar Kalkanı):** Public/anonim veri girişlerinde bot koruması (Honeypot / Turnstile), hız limiti (Rate Limiting), girdi sanitizasyonu (Zod) ve sınır ihlali denetimi (`security-audit` Guidance Mode — `WEB-PROTOCOL-AND-AUTH.md` & `CLIENT-SIDE.md`).
   - **Halka 3 (İletim & API):** Verinin taşındığı endpoint, DTO/şema doğrulaması ve HTTP durum kodları (201 Created, 400 Bad Request, 429 Too Many Requests).
   - **Halka 4 (Kalıcılık & Yetkilendirme):** Veritabanı tablosu, kolon kısıtları, migration dosyası ve RLS (Row Level Security) kuralları (ör. Anonim kullanıcılar için Strict Blind Insert: `FOR INSERT WITH CHECK (true)`, `FOR SELECT USING (false)`).
   - **Halka 5 (Tüketim & Döngü Kapanışı - Loop Closure):** "Kullanıcıya 'Editörlerimiz inceleyecek' denip verinin unutulması yasaktır." Bu veriyi hangi rol (`content_approver`, `admin`), hangi ekrandan veya mekanizmayla (moderasyon masası, webhook, e-posta) karşılayacak?

3. ⛔ **Sessiz Mock Yasağı (No Silent Mocking - Anti-Phantom Rule):**
   - Ajanın gerçek bir backend/DB gerektiren özelliği kullanıcıya bildirmeden sessizce `localStorage`, `sessionStorage` veya in-memory state arkasına bağlayıp "bitti / çalışıyor" demesi **AĞIR İHLAL (Violation)** sayılır.
   - Eğer sprint veya task kapsamında bilinçli olarak yalnızca UI prototip yapılıyorsa:
     1. Kod içinde açıkça `// TODO: MOCK - NOT CONNECTED TO BACKEND` yazılmalıdır.
     2. Arayüzde veya dev modunda açık bir "Demo/Mock Modu" uyarısı yer almalıdır.
     3. Planda ve KANBAN kartında durum "Mock Prototip" olarak beyan edilmeli, kullanıcı onayı alınmadan asla "Tamamlandı / Canlı Özellik" olarak sunulmamalıdır.

4. **Kabul Kriterleri (Acceptance Criteria & Derin Gherkin):**
   - Yalnızca ekrandaki toast mesajını değil, ağ yanıtını (`HTTP 201`) ve veritabanı kaydını kapsayan derin kabul kriterleri belirlenir.

5. **3. Parti Araç ve Kütüphane Araştırması:**
   - Görevde harici bir kütüphane, araç, servis veya paket kullanılacaksa önceden araştırılır.
   - ⛔ **Açık Kaynak (Open-Source) Önceliği Zorunludur:** Kapalı kaynak veya tescilli araçlar yerine öncelikle aktif geliştirilen, güvenilir lisanslı (MIT, Apache 2.0, BSD) açık kaynaklı alternatifler tercih edilir ve gerekçesi plana eklenir.

6. ⛔ **UX Durumları ve 3 Cihaz Ergonomisi Planı (Responsive Viewport Contract):**
   - Görev bir arayüz, sayfa veya bileşen içeriyorsa planda şu 3 unsur açıkça tanımlanmalıdır:
     1. **4 UX Durumu:** Loading (kaset yapısını taklit eden zorunlu Skeleton Screen UI; veri yüklemede spinner yasaktır, spinner yalnız form submit butonunda kullanılır), Empty (açıklayıcı ikon+CTA), Error (inline+çözüm) ve Action Feedback (toast/optimistic).
     2. **3 Cihaz Ergonomisi:** Mobil (< 768px - tek sütun / Thumb Zone / Bottom Nav / kart listesi), Tablet (768px-1024px - 2 sütun / Split-View / dokunmatik aralıklar), Masaüstü (> 1024px - çok sütunlu zengin ızgara).
     3. **Modal / Popup Davranışı:** Sayfa token'larıyla uyum, mobilde alttan açılan Bottom Sheet (Drawer) adaptasyonu ve `max-h-[85dvh]` kaydırma/klavye koruması.

7. ⛔ **Ön Etki Analizi ve Patlama Yarıçapı Protokolü (Pre-Edit Impact Analysis & Blast Radius Scan - Sıfır Regresyon):**
   Paylaşılan bir fonksiyon, sınıf, interface, bileşen (React/Vue/TSX component), DTO, enum, API endpoint'i veya veritabanı tablosunu/kolonunu değiştirmeden önce ajan:
   1. İlgili sembolün adını kod tabanında aramakla (`grep` / codebase search),
   2. Bu sembolü çağıran veya referans veren tüm dosyaları (patlama yarıçapını / blast radius) listelemekle,
   3. Değişikliğin çağıran dosyaları kırıp kırmayacağını analiz etmekle ve kırıyorsa, tüm çağıranları **aynı çoklu-dosya düzenleme bloğunda (aynı işlemde)** güncellemekle YÜKÜMLÜDÜR.
   4. "Derleyici zaten yakalar" diyerek körlemesine düzenleme yapmak yasaktır; semantik, tip ve çalışma zamanı (runtime) sözleşmeleri korunmalıdır.

8. ⛔ **Dikiş Noktaları (Seams) ve Hata Teşhis / TDD Protokolü:**
   - Testler yalnızca önceden belirlenen genel arayüz dikiş noktalarında (`seam`) yazılır; iç uygulama detaylarına bağlanamaz.
   - Hata ayıklama veya çökme düzeltmelerinde kod değiştirmeden önce [`bug-diagnosis-enforcement.md`](./bug-diagnosis-enforcement.md) gereğince hatayı kanıtlayan kırmızı geri bildirim döngüsü (Aşama 1) zorunludur.
   - Kod incelemelerinde [`code-review`](../skills/code-review/SKILL.md) iki eksenli (Standartlar vs Şartname) paralel denetim işletilir; sızma testi, zafiyet avcılığı ve güvenlik sınır denetimlerinde [`security-audit`](../skills/security-audit/SKILL.md) devreye girer.

9. **Kullanıcıya Sunum, Değişiklik/Review Şansı ve Açık Onay:**
   - Hazırlanan plan kullanıcıya sunulur.
   - Kullanıcıya planı inceleme, revize etme veya değişiklik talep etme fırsatı verilir.
   - ⛔ **Kullanıcıdan açık onay ("onay", "başla", "uygun" vb.) alınmadan Adım 3 (Geliştir) aşamasına KESİNLİKLE GEÇİLEMEZ.**

---

## Adım 2.2 — Antigravity IDE Plan Modu (`/plan`) ve Proceed İcra Protokolü (Proceed Execution Protocol)

Antigravity IDE içinde planlama modunda (`/plan` veya Plan Mode) çalışırken, sistemin IDE'nin yerleşik `<PLAN>` promptu ile codebase kurallarımız arasında tam deterministik bir köprü kurması ZORUNLUDUR:

1. **Zorunlu Plan Şablonu (`.agent/templates/PLAN.template.md`):**
   - Kullanıcı `/plan` komutu verdiğinde veya plan istendiğinde, ajan IDE'nin beklediği alanları (`Goal Description`, `User Review Required`, `Open Questions`, `Proposed Changes`, `Verification Plan`) eksiksiz karşılayan, ancak **TDD Kırmızı-Yeşil Dikiş Noktaları**, **5 Katmanlı Dikey Dilim Mimarisi** ve **Sprint/KANBAN Durumunu** içeren standart [`.agent/templates/PLAN.template.md`](../templates/PLAN.template.md) şablonuna göre plan üretir.
   - ⛔ **Serbest Metin ve TDD'siz Plan Yasağı:** TDD fazları, dikiş noktası (`seam`) ve 5 katmanlı dilim içermeyen bir plan artifact'ı üretmek **AĞIR İHLALDİR (Anti-Adhoc-Planning Slop)**.

2. ⛔ **PROCEED İCRA PROTOKOLÜ (Proceed Execution Protocol — Kırmızı Test Kanıtı Olmadan Koda Başlama Yasağı):**
   Kullanıcı plandaki "Proceed" butonuna bastığında, "planı uygula", "onaylıyorum", "devam et" veya benzeri bir onay verdiğinde; ajan **ASLA VE KESİNLİKLE** doğrudan kaynak kod (`src/**`) yazmaya başlayamaz! Plan dokümanında tanımlanan 5 fazı sırasıyla işletmek zorundadır:
   - **Faz 1 (Gherkin & KANBAN Başlangıcı):** `specs/<kart-id>.feature` senaryosu hazırlanır (veya doğrulanır); `KANBAN.md` kartı `Bekliyor`'dan `Yapılıyor`'a çekilir (WIP kontrolü yapılır).
   - **Faz 2 (KIRMIZI TEST KANITI - Red Loop):** Önceden belirlenen dikiş noktasında (`seam`) başarısız olan test dosyası (`*.test.ts`, `*Test.java` vb.) yazılır. Test komutu terminalde çalıştırılır ve testin **KIRMIZI (FAIL)** olduğu çıktı ile kanıtlanır. Test yazılmadan ve fail ettiği gösterilmeden üretim koduna geçmek **SİSTEMATİK YASAKTIR**.
   - **Faz 3 (MİNİMAL YEŞİL KOD - Green Loop):** Yalnızca o kırmızı testi yeşile çevirecek kadar minimal üretim kodu yazılır (spekülatif/hayali kod eklenmez). Test tekrar çalıştırılır ve **YEŞİL (PASS)** olduğu kanıtlanır.
   - **Faz 4 (5 Katman Tamamlama & UX Durumları):** Varsa DB, View/RPC, API ve UI katmanları bağlanır. Sayfa ve veri yükleme durumlarında **Skeleton Screens UI** uygulanır (spinner yasaktır).
   - **Faz 5 (Refactor & Kapanış):** Kod sadeleştirilir, ölçülebilir kalite kapıları (`run_all_gates.py`) çalıştırılır, kullanıcı test adımları `docs/KULLANICI_TEST_REHBERI.md`'ye eklenir ve KANBAN kartı `Yapıldı`'ya taşınır.

---

## Adım 3 — Geliştir

1. İlgili skill'leri oku ve kurallarına uy.
2. ⛔ **TDD Kırmızı → Yeşil Döngüsü (Red-Green-Refactor):** Yeni iş mantığı, servis, endpoint, yardımcı fonksiyon veya veri dönüşümü geliştirirken doğrudan üretim kodunu yazmak YASAKTIR (`tdd` skill'i devreye girer):
   - **Aşama 1 (Kırmızı Test):** Önceden belirlenen dikiş noktasında (`seam`) başarısız olan test yazılır ve testin kırmızıya düştüğü çalıştırılarak kanıtlanır. Dahili/private metotlar mock'lanmaz; genel arayüzün davranışı test edilir.
   - **Aşama 2 (Minimal Geçiş Kodu):** Yalnızca o testi yeşile çevirecek kadar minimal üretim kodu yazılır (spekülatif kod veya geleceğe dönük hayali yapılar eklenmez).
   - **Aşama 3 (Yeşil Doğrulama):** Test çalıştırılır ve yeşile döndüğü kanıtlanır. Döngü başına tek dikey dilim (tracer bullet) ilerlenir.
3. Kodu yaz — DRY, guard clauses, erken return, tip güvenliği.
4. Frontend projesi ise i18n anahtarlarını **her iki dil dosyasına** ekle.
5. Backend projesi ise API dokümantasyon dosyasını aynı değişiklikte güncelle.
6. Veritabanı şeması, tablo, kolon veya entity revizyonu yapıldıysa `DB_MIGRATIONS.md` dosyasını VE canlı mimari belgesi olan `PROJECT_BRIEF.md` (Veritabanı Modeli / Şema) dosyasını eşzamanlı (İkili Eşleme - Dual Mapping) güncelle.
7. Yeni paket/bağımlılık (`package.json`, `pom.xml`, `requirements.txt`), yeni altyapı bileşeni veya sunucusuz işlev (Edge Function, worker, Lambda) eklendiyse `PROJECT_BRIEF.md` dosyasını aynı değişiklikte güncelle.
8. Mevcut kodun akışını ve iş mantığını bozma; refactor'ı ayrı adımda yap (`code-review` ve `codebase-design` ilkeleriyle).
9. Frontend projesinde yeni veya güncellenen bir arayüz (sayfa, dashboard, form, tablo, bileşen) üretiliyorsa; `frontend-design`, `ui-ux-pro-max` ve (Tailwind ise) `ui-styling` kurallarına uymak zorunludur. Tekdüze "AI-slop" arayüzler testler geçse dahi teslim edilemez (bkz. `sprint-delivery-workflow.md` §6.1).

---

## Adım 4 — Kalite kapıları

Kapılar `.agent\AGENTS.md` §3'ün kaynağıdır; buradaki tablo **üretilir** ve
bayatlığı `rules_gates.py` hata olarak raporlar. Kaynak: kural dosyalarının
front matter `sinif:` / `kapi:` alanları.

<!-- GATE-TABLE:BEGIN -->
| Yığın | Zorunlu komut | Ayrıntı |
|---|---|---|
| Backend / API dokümantasyonu | `python .agent/skills/musgoku/scripts/check_api_docs.py` | [`api-documentation-enforcement.md`](./api-documentation-enforcement.md) |
| Backend / Veritabanı migration | `python .agent/skills/musgoku/scripts/check_db_migrations.py` | [`db-migration-enforcement.md`](./db-migration-enforcement.md) |
| Tasarım / sözleşme ve DESIGN.md uyumu | `python .agent/skills/musgoku/scripts/check_design_contract.py` | [`design-skills-enforcement.md`](./design-skills-enforcement.md) |
| Tasarım / skill sahipliği | `python .agent/skills/musgoku/scripts/check_design_skills.py` | [`design-skills-enforcement.md`](./design-skills-enforcement.md) |
| Tasarım / zanaat tabanı ve anti-slop | `python .agent/skills/musgoku/scripts/check_design_slop.py` | [`design-skills-enforcement.md`](./design-skills-enforcement.md) |
| Tasarım / tema kontrastı ve WCAG uyumu | `python .agent/skills/musgoku/scripts/check_theme_contrast.py` | [`design-skills-enforcement.md`](./design-skills-enforcement.md) |
| Frontend / bundle bütçesi | `python .agent/skills/musgoku/scripts/check_bundle_limits.py` | [`frontend-bundle-limits.md`](./frontend-bundle-limits.md) |
| Proje Yönetimi / Oturum Devri ve Görev Panosu | `python .agent/skills/musgoku/scripts/check_handoff.py` | [`handoff-session-continuity.md`](./handoff-session-continuity.md) |
| Frontend / i18n | `python .agent/skills/i18n-localization/scripts/i18n_checker.py` | [`i18n-enforcement.md`](./i18n-enforcement.md) |
| TypeScript / React | `npx tsc --noEmit` | [`no-unused-code.md`](./no-unused-code.md) |
| Java / Spring derleme | `mvn clean compile -DskipTests` | [`no-unused-code.md`](./no-unused-code.md) |
| Java / kullanılmayan kod | `pwsh -NoProfile -File .agent/skills/musgoku/scripts/check-unused.ps1` | [`no-unused-code.md`](./no-unused-code.md) |
| Proje Mimarisi / Canlı Brief | `python .agent/skills/musgoku/scripts/check_project_brief.py` | [`project-brief-maintenance.md`](./project-brief-maintenance.md) |
| Skill sözleşmesi / tetikleyici sözlüğü | `cd .agent/skills/ui-ux-pro-max/scripts/tests && python -m unittest test_skill_contracts` | [`skill-trigger-routing.md`](./skill-trigger-routing.md) |
| Sprint / kanban / MVP | `python .agent/skills/musgoku/scripts/check_sprint_board.py` | [`sprint-delivery-workflow.md`](./sprint-delivery-workflow.md) |
| Frontend / Vite SPA | `python .agent/skills/musgoku/scripts/check_vite_spa.py` | [`vite-spa-enforcement.md`](./vite-spa-enforcement.md) |
<!-- GATE-TABLE:END -->

**Kapısız iki ölçüm** (ölçülebilir değil, gözle bakılır):

| Ölçüm | Sınır |
|---|---|
| Dosya boyutu | Java 300 LOC · React/TSX 200 satır |
| Kural setinin kendisi | `python .agent/skills/musgoku/scripts/rules_gates.py --strict` → `[OK]` |

Ayrıntı: [no-unused-code.md](./no-unused-code.md) ·
[AGENTS.md §3](../AGENTS.md)

### Kapsam-Duyarlı Kapı Çalıştırma İlkesi (Scope-Aware Verification)

⛔ **Körlemesine Test Koşturma Yasağı:**
Yukarıdaki ölçülebilir kapı komutları (`npm run build`, `pnpm test`, `npx tsc`, `mvn clean compile`, `test:e2e`) **yalnızca ilgili etki alanındaki dosyalar değiştiğinde** çalıştırılır:

1. **Uygulama Kodu Değiştiğinde (`src/**`, `components/**`, `api/**`, `package.json`, `pom.xml` vb.):**
   - İlgili derleme (`build`), tip (`typecheck`), birim ve e2e test komutları **ZORUNLUDUR**.
2. **Yalnızca Ajan Kuralları veya Dokümantasyon Değiştiğinde (`.agent/**`, `*.md`, `docs/**`, `.gitignore`):**
   - Uygulama build'i (`npm run build`, `pnpm build`), testleri (`pnpm test`, `mvn test`) ve e2e testler **ÇALIŞTIRILMAZ (ATLANIR / SKIPPED)**. Kaynak kod değişmediği için testlerin kırılma riski yoktur; çalıştırmak gereksiz token, CPU ve zaman israfıdır.
   - Varsa yalnızca ilgili kural kapısı (`python .agent/skills/musgoku/scripts/rules_gates.py` vb.) çalıştırılır.
   - Devir raporunda dürüstçe beyan edilir: *"Uygulama Testleri: Kapsam dışı (Yalnızca .agent/ ve dokümantasyon değişti)"*.

---

## Adım 4.1 — Kullanıcı Test Edilebilirliği ve Test Rehberi (docs/KULLANICI_TEST_REHBERI.md)

1. **Her çıktı test edilebilir olmalı:** Her geliştirme, düzeltme veya sprint teslimatında
   çıktı kullanıcı tarafından test edilebilir olmalıdır.
2. **Rehber güncellemesi:** `docs/KULLANICI_TEST_REHBERI.md` dosyası yoksa
   `.agent/templates/KULLANICI_TEST_REHBERI.template.md` şablonundan oluşturulur; varsa
   bu adımda yapılan işin tarayıcıda veya konsolda nasıl adım adım test edileceği rehbere eklenir.
3. ⛔ **Otomasyon Yeşilliği Yanılgısına Düşme (Kritik Ders):**
   Otomasyon testlerinin (`pnpm test`, `typecheck`, `test:e2e`, `mvn test`) yeşil olması,
   kodun syntax ve birim düzeyinde çalıştığını kanıtlar; ancak kullanıcının kendi gözüyle
   tarayıcıda bu özellikleri adım adım nasıl doğrulayacağını göstermez.
   `docs/KULLANICI_TEST_REHBERI.md` güncellenmeden veya kullanıcıya adım adım test yöntemi
   sunulmadan teslimat tamamlanmış sayılamaz ve commit onayına geçilemez!
4. 💡 **İstisna (Minor Rötüş & Dahili Değişiklikler):**
   Mevcut kullanıcı akışını, ekran bileşenlerini veya kabul senaryolarını değiştirmeyen minor rötüşlar
   (CSS boşluk/renk ince ayarı, dahili refactoring, tip güvenliği/düzeltmesi, typo, kod içi yorum)
   için rehbere gereksiz satır eklenmez ve dosya işlemi yapılmaz.
   Bu durumda commit onayında ve devir raporunda:
   *"Kullanıcı Test Rehberi: Güncelleme gerekmedi (Minor rötüş / mevcut senaryolar geçerli)"*
   olarak beyan edilir ve gerekiyorsa rehberdeki hangi mevcut adımın geçerli olduğu belirtilir.
5. ⛔ **Veri Toplayan/Üreten Özelliklerde 3 Katmanlı Doğrulama Zorunluluğu:**
   Bir form, bildirim veya veri akışı teslim edildiğinde rehber ve test adımları yalnızca ekrandaki başarı mesajıyla (toast/modal) sınırlı kalamaz; şu 3 katmanı içermek **zorundadır**:
   - **Katman 1 (Görsel UX):** Form alanlarını doldur, gönder, başarı toast/bildirimini ve formun temizlendiğini gör.
   - **Katman 2 (Ağ / Network Doğrulaması):** Tarayıcı F12 Geliştirici Araçları → Network sekmesinde giden HTTP isteğinin (API / Supabase REST) `201 Created` veya `200 OK` döndüğünü ve giden payload'u doğrula.
   - **Katman 3 (Veritabanı Kalıcılık Doğrulaması):** Veritabanı sorgusuyla (`SELECT ... FROM ... ORDER BY created_at DESC LIMIT 1;`) veya Admin panelinde yeni satırın oluştuğunu kanıtla. DB kanıtı sunulmayan hiçbir veri toplama özelliği "DONE" kabul edilemez.
6. ⛔ **UI/UX Kalite Kapısı ve Anti-Slop Kontrolü:**
   Yeni veya güncellenen bir sayfa, tablo veya form teslim edilirken; tasarımın `frontend-design` ve `ui-ux-pro-max` standartlarını karşıladığı, tekdüze gri kutulardan kaçınıldığı, net görsel hiyerarşi ve durum rozetleri sağlandığı rehberde gözle doğrulanmalıdır. Gözle profesyonel görünmeyen arayüz tamamlanmış sayılamaz.
7. ⛔ **3 Cihaz Ergonomisi ve Adaptif Modal Doğrulaması (Responsive UX Verification):**
   Arayüz veya modal içeren her teslimatta, kullanıcının bizzat gözüyle test edebilmesi için `docs/KULLANICI_TEST_REHBERI.md` içine şu 3 senaryonun eklenmesi zorunludur:
   - **Mobil (375px/414px F12 Cihaz Simülasyonu):** Tek sütun akışı, başparmakla butonlara erişim, formların yatay taşmaması ve açılan modalın alttan gelen Bottom Sheet (Drawer) olarak açılıp parmakla kaydırılabilmesi.
   - **Tablet (768px – 1024px iPad Simülasyonu):** 2 sütunlu dengeli düzen veya split-view, dokunmatik buton aralıkları, katlanabilir sidebar.
   - **Masaüstü (> 1024px):** Çok sütunlu zengin yerleşim, ortalanmış modal dialog ve hover durumları.

8. ⛔ **Sahte Bitti (Phantom Done) ve Katman Bütünlüğü Denetimi:**
   Otomasyon veya mock testlerinin yeşil olmasına aldanarak teslimatı "Bitti" ilan etmek AĞIR İHLALDİR. 5 Katmanlı Dikey Dilim (1. DB Şeması & Migration, 2. View/RPC/Sorgu, 3. API & İstemci Entegrasyonu, 4. Arayüz & Eylem/İzleme, 5. Yönetim/Admin Giriş Formu) doğrulanmadan hiçbir veri tabanlı iş tamamlanamaz. Herhangi bir katman eksikse teslimat "YARIM (Eksik Katman: ...)" olarak raporlanır ve eksik parça `HANDOFF.md` §3 Sıradaki İşler tablosuna kaydedilir (bkz. `sprint-delivery-workflow.md` §6.2).

---

## Adım 4.2 — İnteraktif Özellik ve Kullanım HTML Rehberi (docs/kullanici-rehberi.html)

1. **Kalıcı ve Detaylı Özellik Dokümantasyonu:** Her gerekli ve anlamlı geliştirme sonrasında, geliştirilen veya revize edilen tüm özelliklerin mimari yapılışını ve adım adım kullanımını anlatan `docs/kullanici-rehberi.html` (veya İngilizce projelerde `docs/user-guide.html`) dosyası güncellenir (yoksa `.agent/templates/KULLANICI_REHBERI.template.html` şablonundan oluşturulur).
2. **Her Özellikte 4 Zorunlu Bölüm:**
   - **1. Ne İşe Yarar / Amaç:** İş değeri, hangi problemi çözdüğü ve kullanıcının ne kazandığı.
   - **2. Nasıl Yapıldı? (5 Katmanlı Dikey Dilim):**
     * *Veritabanı:* Tablo, kolon, migration veya entity detayları.
     * *Backend / API / RPC:* Endpoint metodu, URL, request/response yapısı, güvenlik filtreleri.
     * *İstemci Entegrasyonu:* Servis çağrısı, store/state yönetimi, query/cache.
     * *Arayüz / UI Bileşenleri:* Bileşen ağacı, form validasyonu, kullanıcı etkileşimleri.
     * *Skeleton Screens UI:* Veri yüklenirken gösterilen gri tonlu wireframe/kaset yapısı.
   - **3. Nasıl Kullanılır? (Adım Adım Kullanım Playbook'u):**
     * Sayfa veya ekran rotası (`/ornek-sayfa`).
     * Tıklanacak buton ve menülerin tam metinleri (örn. `"Yeni Ekle"` -> `"Kaydet"`).
     * Form alanlarına girilecek veriler ve doğrulama ipuçları.
     * Başarılı akış ve beklenen sonuç.
   - **4. Arayüz ve UX Durumları:**
     * Skeleton screens yükleme durumu.
     * Normal / dolu verili durum.
     * Boş durum (Empty state).
     * Hata ve yeniden dene (Error & Retry) durumu.
3. 💡 **İstisna (Minor Rötüş & Dahili Değişiklikler):**
   Mevcut kullanıcı akışını, ekran bileşenlerini veya kabul senaryolarını değiştirmeyen minor rötüşlar (CSS boşluk/renk ince ayarı, dahili refactoring, tip güvenliği/düzeltmesi, typo) için HTML rehberine satır eklenmez. Raporda *"Özellik HTML Rehberi: Güncelleme gerekmedi (Minor rötüş / mevcut senaryolar geçerli)"* beyan edilir.

---

## Adım 4.3 — Doğrulama Bulgularının Yönetimi ve Yaşam Döngüsü (VFRLP)

1. ⛔ **Bulguların Pasif Metin Olarak Bırakılması veya Doğrudan Koda Dalıp Bulguları Unutma Yasağı (Anti-Passive Audit & Zero-Loss Rule):**
   `/verify-prd`, `/verify-sprint` veya `/verify-last` çalıştırıldığında tespit edilen eksik katmanlar, Sahte Bitti (Phantom Done) durumları, kırık testler, kalite kapısı hataları veya şartname sapmaları ASLA sadece sohbete Markdown çıktısı basılarak bırakılamaz! Aynı şekilde kullanıcı onarımı onayladığında ajan doğrudan koda dalıp 4-6. bulguları sohbet geçmişinde unutmaya terk edemez; önce **Faz 0 (Sıfır-Kayıplı Dosya Dağıtımı)**, ardından **Faz 1..N (Dilimli Cerrahi Onarım)** yürütülür.
2. 📖 **Tarih Damgalı 4 Bölümlü PRD Senkronizasyonu (`## BULGULAR` Audit Trail):**
   `/verify-prd` denetiminde projenin `PRODUCT.md`, `docs/*-prd.md` veya `docs/FEATURES.md` dokümanı altına `## BULGULAR (DENETİM RAPORU — [YYYY-MM-DD HH:mm])` ana başlığı açılarak yalnızca özet tablo değil, raporun **4 ana bölümünün tamamı** hiçbir madde kırpılmadan kalıcı olarak işlenir:
   - `### 1. Katman Bütünlüğü Matrisi (Full-Stack Slice Audit)`: `| Özellik / Modül (PRD / RFC) | 1. DB / Şema | 2. Backend / RPC | 3. İstemci API | 4. UI & Skeleton | 5. Döngü Kapanışı | Nihai Hüküm |`
   - `### 2. Tespit Edilen Sahte Bitti (Phantom Done), Yetim Bileşenler ve Kırık/Eksik Bağlantılar`
   - `### 3. Doküman-Kod Sapması (Spec Drift) & Test Rehberi Denetimi`
   - `### 4. Düzeltme & Tamamlama Eylem Planı (Action Items — 🔴 Kritik & 🟡 İyileştirme)`
   Böylece ürün şartnamesi ile gerçek kod durumu arasındaki tüm bulgular kalıcı olarak mühürlenir.
3. 🔄 **Sıfır-Kayıplı Durum Kalıcılığı (HANDOFF §0/§3, KANBAN & RELEASE):**
   - **`HANDOFF.md` §3 & RTM:** Tespit edilen tüm `🔴 Kritik` ve `🟡 İyileştirme` maddelerine deterministik `[DOM]-[TIP]-[NO]` (`[DOM]-BUG-XXX` / `[DOM]-US-XXX`) kimliği verilir. WIP limitini (maks 3) koruyarak ilk 3 kritik iş `🎯 Aktif Sprint / Anlık Görev Panosu`na (`1. ⏭️`, `2. ⬜`, `3. ⬜`), kalan **tüm** Kritik ve İyileştirme maddeleri ise hemen altındaki `📌 Gelecek Fazlar & Parking Lot / Sıradaki Dilimler (RTM)` tablosuna eksiksiz kaydedilir (`AGENTS.md` §2.4 & `handoff-session-continuity.md` §2). Yeni yakalanan sistemik hatalar `§0 Tuzaklar` ve `knowledge-base.md` dosyalarına işlenir.
   - **`KANBAN.md`:** Kabul kriteri yeşil olmayan veya katmanı eksik olan kartlar `Yapıldı` sütununda tutulamaz; derhal `Yapılıyor` veya `Bekliyor` sütununa geri çekilir ve durumu `🔴 Kapatılamaz (YARIM)` yapılır.
   - **`RELEASE_PLAN.md`:** Kapanmayan veya ötelenen kartlar sürüm planına aktarılır.
4. 🛠️ **Auto-heal (Otomatik Belge Senkronu):**
   Saf dokümantasyon senkron açıkları (DB şeması değiştiğinde `PROJECT_BRIEF.md` / `DB_MIGRATIONS.md`, API eklendiğinde `docs/APIs/`, kod değiştiğinde `HANDOFF.md` güncelliği) ajan tarafından ara onay sormadan otomatik tamamlanır (**Auto-heal**).
5. ⚡ **Dilimli Cerrahi Onarım ve Eylem Menüsü (Faz 1..N):**
   Raporun hemen altında kullanıcıya net iki seçenek sunulur:
   - **1. Anında Dilimli Cerrahi Onarım (Fix Now — Faz 1..N):** Faz 0 ile mühürlenen `🔴 Kritik` maddeleri (3'erli WIP dilimleriyle) ve ardından `🟡 İyileştirme` maddelerini ilgili cerrahi yeteneklerle (`fix-bug`, `tdd`, `db-migration-enforcement`, `ui-polish`, `doc-coauthoring`) sırayla çöz.
   - **2. Görev Panosunda Bırak (Plan Next):** Bulguları PRD `## BULGULAR` ve `HANDOFF.md` üzerinde planlı tutarak oturumu güvenle devret.
   - **3. Standartlar ve Şartname Çatışmasında Konsey Hakemliği:** Kod incelemesinde (`code-review`) veya retrospektif denetimlerde standart kurallar ile şartname gereksinimleri arasında bir mimari ihtilaf doğarsa, `council` hakemliği ile bilinçli ödünleşim (trade-off) sentezi üretilir ve `knowledge-base.md` / `docs/adr/` kaydına bağlanır.

---

## Adım 5 — Devir ve bilgi tabanı güncellemesi

1. `knowledge-base.md`'ye bu adımda alınan kararlar
   (`Karar / Gerekçe / Alternatifler`) ve çözülen hatalar
   (`Problem / Root Cause / Solution`) yaz.
2. `HANDOFF.md`'yi güncelle:
   §1 güncellik kanıtı · §2 nerede kaldık · §3 sıradaki iş ·
   §3.1 nasıl test edilir (kullanıcı) · §4 yeni ders · §5 yeni karar · §6 ortam bilgisi
3. Yanıtta `### 📝 OTURUM DEVİR & BİLGİ TABANI GÜNCELLEMESİ` bloğunu göster.
4. Açık iş kalmadıysa bunu açıkça yaz.
5. ⛔ **"Sıradaki İş" Terminoloji ve Tekillik İlkesi (Anti-Conflict Next Work Rule):**
   - **İcra Edilen İşe "Sıradaki İş" Başlığı Koyma Yasağı:** Oturumda veya yanıtta icra edilip tamamlanan çalışmalara ASLA `### Sıradaki İş: ...` başlığı verilemez. Başlık daima **"İcra Edilen Görev / Tamamlanan Geliştirme: [İş Tanımı]"** olmalıdır. Aksi halde kullanıcı o işin henüz yapılmadığını ve sırada beklediğini düşünerek çelişkiye düşer.
   - **Yanıt Boyunca Tek ve Tutarlı "Sıradaki İş" Beyanı:** Bir yanıtta "Sıradaki İş" veya "Sıradaki İşler" ifadesi YALNIZCA VE YALNIZCA bir sonraki oturumda/adımda başlanacak açık işleri ifade eder. Yanıt içerisinde aynı veya çelişkili iki farklı "sıradaki iş" bilgisi yer alamaz.
   - **Devir Raporunda Tekillik:** Devir raporu bloğunda sıradaki işler tek bir maddede (`- **Sıradaki İşler (Canlı Görev Panosu):** 1. ⏭️ ..., 2. ⬜ ...`) sunulur; `HANDOFF.md` altında mükerrer `* Sıradaki İş:` açılmaz.

Ayrıntı: [knowledge-base-management.md](./knowledge-base-management.md)

---

## Adım 6 — Kullanıcı onayı

- Değişiklikleri listele (`git status`).
- Önerilen commit mesajı ve yeni semantik tag'i göster.
- **Kullanıcı test adımlarını sun:** Kullanıcının teslimatı bizzat gözüyle test edebilmesi için
  `docs/KULLANICI_TEST_REHBERI.md` dosyasındaki ilgili adımları ve test komutlarını göster
  (minor rötüş ise güncelleme gerekmediğini ve geçerli mevcut senaryoyu belirt).
- ⛔ Onay olmadan commit yapma.
- ✅ Onay verilirse `git-release-workflow` skill'iyle **kesintisiz** yürüt.

### Onay ne demektir, ne demek değil

**Onay sayılanlar** (uygulamaya devam et):

| Yönlendirme | Etki |
|---|---|
| "devam" · "devam edelim" · "ekliyorum" · "yapıyorum" · "güncelliyorum" · "güncellemeye bağlıyorum" | İstenen işi **tümüyle** bitir, arada sorma |
| "commit yap" · "onaylıyorum" · "evet" · "commitleyebilirsin" | Commit + tag + push aşamasına geç |

**Onay sayılmayanlar:**

| İfade | Neden |
|---|---|
| "devam et" gibi genel ifadeler, **commit** için | Uygulamaya devam ≠ commit izni. Commit ayrıca sorulur. |
| "bir de şunu düzelt" | Yeni iş tanımı; önceki işin commit iznini içermez |

### Uygulama sırasında sorma

- Uygulama adımlarında her değişiklik için ayrı onay **sorulmaz**.
- Ancak **kapsam dışına çıkılacaksa**, bir karar geri alınacaksa veya
  projede kararlaşmış bir kural çiğnenecekse **önce sor**.
- `git commit` / `tag` / `push` bu istisnadır: **her zaman ayrıca onay gerekir.**

Ayrıntı: [no-unauthorized-commit.md](./no-unauthorized-commit.md) ·
[mandatory-git-release-workflow.md](./mandatory-git-release-workflow.md)

---

## Her zaman geçerli kurallar

1. Oturum köprüsü — `HANDOFF.md` okunmadan kod yazılmaz.
2. Tasarım/UI talebi → üç tasarım skill'i birlikte okunur.
3. Frontend projesi → i18n ve bundle bütçesi kuralları atlanmaz.
4. Backend projesi → `mvn test-compile` ve API dokümantasyonu atlanmaz.
5. Mevcut kodun akışı ve iş mantığı bozulmadan revize edilir.
6. Entegrasyon testi kapatmak kural değildir; "test devre dışı bırakıldı" notunu
   `knowledge-base.md`'ye yaz ve geçici çözüm olarak işaretle.
7. "Sıradaki İş" terminolojisi tutarlılığı — yapılan işe "Sıradaki İş" başlığı verilmez; devir raporundaki sıradaki işler tekil ve kesin kaynaktır.

---

## Proje Bazlı Ek Kurallar

> ⛔ **Kural Ekleme ve Mükerrerlik İlkesi:**
> 1. Yukarıdaki global kurallar projeler arası standarttır ve değiştirilmez.
> 2. Projeye özgü bir geliştirme akışı kuralı gerekirse, önce yukarıdaki global kurallarla mükerrerlik denetimi yapılır.
> 3. Yeni kural yalnızca bu başlığın altına `### <Kural Başlığı>` olarak eklenir.

### Bu Proje İçin Ek Kurallar
_(Henüz bu projeye özel ek bir kural tanımlanmamıştır.)_