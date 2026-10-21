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
| UI testi / ekran incelemesi | tarayıcı/ekran aracı (proje yapısına göre) |
| Dosya arama / proje keşfi | dosya sistemi aracı |

Tetikleyici tablosu ve sınırlar: [mcp-usage-enforcement.md](./mcp-usage-enforcement.md)

---

## Adım 2.1 — Uygulama Planı, 3. Parti Açık Kaynak Araştırması ve Kullanıcı İnceleme/Onay Kapısı

⛔ **KESİN VE NET KURAL:** İster bir sprint planı dahilinde olsun, ister sprint dışı küçük dilimlere (slice'lara) veya task listesine bölünmüş olsun:
**"Ne yapılacağı" (what) bilinse dahi, "nasıl yapılacağı" (how) planlanmadan DOĞRUDAN KODA BAŞLAMAK KESİNLİKLE YASAKTIR.**

Geliştirmeye başlamadan önce ajan sırasıyla şu adımları işletmek zorundadır:

1. **Detaylı Uygulama Planı ("Nasıl Yapılacak?"):**
   - Değişecek, oluşturulacak veya silinecek dosyalar,
   - Mimari yaklaşım, tasarım desenleri ve bileşen sınırları,
   - Varsa state yönetimi, veri akışı ve endpoint bağlantı adımları çıkarılır.

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
     1. **4 UX Durumu:** Loading (skeleton/spinner), Empty (açıklayıcı ikon+CTA), Error (inline+çözüm) ve Action Feedback (toast/optimistic).
     2. **3 Cihaz Ergonomisi:** Mobil (< 768px - tek sütun / Thumb Zone / Bottom Nav / kart listesi), Tablet (768px-1024px - 2 sütun / Split-View / dokunmatik aralıklar), Masaüstü (> 1024px - çok sütunlu zengin ızgara).
     3. **Modal / Popup Davranışı:** Sayfa token'larıyla uyum, mobilde alttan açılan Bottom Sheet (Drawer) adaptasyonu ve `max-h-[85dvh]` kaydırma/klavye koruması.

8. ⛔ **Dikiş Noktaları (Seams) ve Hata Teşhis / TDD Protokolü:**
   - Testler yalnızca önceden belirlenen genel arayüz dikiş noktalarında (`seam`) yazılır; iç uygulama detaylarına bağlanamaz.
   - Hata ayıklama veya çökme düzeltmelerinde kod değiştirmeden önce [`bug-diagnosis-enforcement.md`](./bug-diagnosis-enforcement.md) gereğince hatayı kanıtlayan kırmızı geri bildirim döngüsü (Aşama 1) zorunludur.
   - Kod incelemelerinde [`code-review`](../skills/code-review/SKILL.md) iki eksenli (Standartlar vs Şartname) paralel denetim işletilir; sızma testi, zafiyet avcılığı ve güvenlik sınır denetimlerinde [`security-audit`](../skills/security-audit/SKILL.md) devreye girer.

9. **Kullanıcıya Sunum, Değişiklik/Review Şansı ve Açık Onay:**
   - Hazırlanan plan kullanıcıya sunulur.
   - Kullanıcıya planı inceleme, revize etme veya değişiklik talep etme fırsatı verilir.
   - ⛔ **Kullanıcıdan açık onay ("onay", "başla", "uygun" vb.) alınmadan Adım 3 (Geliştir) aşamasına KESİNLİKLE GEÇİLEMEZ.**

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
6. Veritabanı şeması, tablo, kolon veya entity revizyonu yapıldıysa `DB_MIGRATIONS.md` dosyasını aynı değişiklikte güncelle.
7. Mevcut kodun akışını ve iş mantığını bozma; refactor'ı ayrı adımda yap (`code-review` ve `codebase-design` ilkeleriyle).
8. Frontend projesinde yeni veya güncellenen bir arayüz (sayfa, dashboard, form, tablo, bileşen) üretiliyorsa; `frontend-design`, `ui-ux-pro-max` ve (Tailwind ise) `ui-styling` kurallarına uymak zorunludur. Tekdüze "AI-slop" arayüzler testler geçse dahi teslim edilemez (bkz. `sprint-delivery-workflow.md` §6.1).

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
| Tasarım / skill sahipliği | `python .agent/skills/musgoku/scripts/check_design_skills.py` | [`design-skills-enforcement.md`](./design-skills-enforcement.md) |
| Tasarım / zanaat tabanı ve anti-slop | `python .agent/skills/musgoku/scripts/check_design_slop.py` | [`design-skills-enforcement.md`](./design-skills-enforcement.md) |
| Tasarım / tema kontrastı ve WCAG uyumu | `python .agent/skills/musgoku/scripts/check_theme_contrast.py` | [`design-skills-enforcement.md`](./design-skills-enforcement.md) |
| Frontend / bundle bütçesi | `python .agent/skills/musgoku/scripts/check_bundle_limits.py` | [`frontend-bundle-limits.md`](./frontend-bundle-limits.md) |
| Frontend / i18n | `python .agent/skills/i18n-localization/scripts/i18n_checker.py` | [`i18n-enforcement.md`](./i18n-enforcement.md) |
| TypeScript / React | `npx tsc --noEmit` | [`no-unused-code.md`](./no-unused-code.md) |
| Java / Spring derleme | `mvn clean compile -DskipTests` | [`no-unused-code.md`](./no-unused-code.md) |
| Java / kullanılmayan kod | `pwsh -NoProfile -File .agent/skills/musgoku/scripts/check-unused.ps1` | [`no-unused-code.md`](./no-unused-code.md) |
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

## Adım 4.1 — Kullanıcı Test Edilebilirliği ve Test Rehberi (KULLANICI_TEST_REHBERI.md)

1. **Her çıktı test edilebilir olmalı:** Her geliştirme, düzeltme veya sprint teslimatında
   çıktı kullanıcı tarafından test edilebilir olmalıdır.
2. **Rehber güncellemesi:** Proje kökündeki `KULLANICI_TEST_REHBERI.md` dosyası yoksa
   `.agent/templates/KULLANICI_TEST_REHBERI.template.md` şablonundan oluşturulur; varsa
   bu adımda yapılan işin tarayıcıda veya konsolda nasıl adım adım test edileceği rehbere eklenir.
3. ⛔ **Otomasyon Yeşilliği Yanılgısına Düşme (Kritik Ders):**
   Otomasyon testlerinin (`pnpm test`, `typecheck`, `test:e2e`, `mvn test`) yeşil olması,
   kodun syntax ve birim düzeyinde çalıştığını kanıtlar; ancak kullanıcının kendi gözüyle
   tarayıcıda bu özellikleri adım adım nasıl doğrulayacağını göstermez.
   `KULLANICI_TEST_REHBERI.md` güncellenmeden veya kullanıcıya adım adım test yöntemi
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
   Arayüz veya modal içeren her teslimatta, kullanıcının bizzat gözüyle test edebilmesi için `KULLANICI_TEST_REHBERI.md` içine şu 3 senaryonun eklenmesi zorunludur:
   - **Mobil (375px/414px F12 Cihaz Simülasyonu):** Tek sütun akışı, başparmakla butonlara erişim, formların yatay taşmaması ve açılan modalın alttan gelen Bottom Sheet (Drawer) olarak açılıp parmakla kaydırılabilmesi.
   - **Tablet (768px – 1024px iPad Simülasyonu):** 2 sütunlu dengeli düzen veya split-view, dokunmatik buton aralıkları, katlanabilir sidebar.
   - **Masaüstü (> 1024px):** Çok sütunlu zengin yerleşim, ortalanmış modal dialog ve hover durumları.

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

Ayrıntı: [knowledge-base-management.md](./knowledge-base-management.md)

---

## Adım 6 — Kullanıcı onayı

- Değişiklikleri listele (`git status`).
- Önerilen commit mesajı ve yeni semantik tag'i göster.
- **Kullanıcı test adımlarını sun:** Kullanıcının teslimatı bizzat gözüyle test edebilmesi için
  `KULLANICI_TEST_REHBERI.md` dosyasındaki ilgili adımları ve test komutlarını göster
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

---

## Proje Bazlı Ek Kurallar

> ⛔ **Kural Ekleme ve Mükerrerlik İlkesi:**
> 1. Yukarıdaki global kurallar projeler arası standarttır ve değiştirilmez.
> 2. Projeye özgü bir geliştirme akışı kuralı gerekirse, önce yukarıdaki global kurallarla mükerrerlik denetimi yapılır.
> 3. Yeni kural yalnızca bu başlığın altına `### <Kural Başlığı>` olarak eklenir.

### Bu Proje İçin Ek Kurallar
_(Henüz bu projeye özel ek bir kural tanımlanmamıştır.)_