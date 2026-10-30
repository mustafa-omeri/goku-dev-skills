# AGENTS.md — Global Ajan Sözleşmesi

> Bu dosya **projeler arası ortaktır**. Proje adı, proje yolu, port, DB adı,
> teknoloji sürümü veya şirket/müşteri bilgisi **buraya yazılmaz.**
> Projeye özel olan tek istisna en sondaki "Proje Bazlı Ek Kurallar" bölümüdür.

---

## 0. Okuma Sırası (atlanmaz)

| # | Ne | Nerede |
|---|-----|--------|
| 1 | Oturum devri — nerede kaldık, sıradaki iş, düşülen tuzaklar | `<repo-kök>\HANDOFF.md` |
| 2 | Geliştirici profili ve kanıtlı ders kütüphanesi | `DEV_BRIEF.md` (varsa), yoksa vault `profile\` + `projects\_STANDARTLAR\decisions\` |
| 3 | Canlı proje mimarisi, teknoloji yığını ve bağlayıcı kararlar | `<repo-kök>\PROJECT_BRIEF.md` (varsa) |
| 4 | Ürün gerçeği ve kısıtlar (varsa) | `<repo-kök>\PRODUCT.md` |
| 5 | İş alanı terimleri ve ortak dil sözlüğü (varsa) | `<repo-kök>\GLOSSARY.md` |
| 6 | Tasarım dili ve token sözleşmesi (UI/UX işlerinde) | `<repo-kök>\DESIGN.md` |
| Projenin kısa/uzun kapsamlı konsolide özeti | docs/<SLUG>_PROJECT_SUMMARY_SHORT.md veya docs/<SLUG>_PROJECT_SUMMARY_LONG.md |
| Özelliklerin adım adım yapılışını ve kullanımını anlatan HTML rehberi | docs/kullanici-rehberi.html (veya docs/user-guide.html) |
| Kullanıcının bizzat gözüyle doğrulayacağı manuel test senaryoları | docs/KULLANICI_TEST_REHBERI.md |
| 7 | Vault kararları (salt okunur) | `<vault>\CLAUDE.md`, `<vault>\profile\`, `<vault>\projects\_STANDARTLAR\decisions\` |
| 8 | Proje kararları | `<vault>\projects\<proje-slug>\` |
| 9 | Bu dizindeki kurallar | `.agent\rules\` (bkz. `trigger-rule-action.md`) |

**Okuma kanıtı:** koda geçmeden önce geçerli kararları başlıklarıyla özetle ya da
*"bu iş için geçerli bir karar bulamadım"* de. Hatırladığını yazma, uydurma.

**Öncelik:** proje kökündeki `AGENTS.md` → bu dosya → `DEV_BRIEF.md`.
Çelişmede proje kökü kazanır. Hiçbirinde olmayan bilgiyi uydurma — sor.

---

## 1. Yazma — tek hedef

| Ne zaman | Nereye |
|---|---|
| Çözdüğün kalıcı hata | `<repo-kök>\knowledge-base.md` |
| Verdiğin kalıcı karar | `<repo-kök>\knowledge-base.md` |
| Durum, sıradaki iş, tuzaklar | `<repo-kök>\HANDOFF.md` |
| Teknoloji, stack, DB, altyapı veya yeni modül revizyonu | `<repo-kök>\PROJECT_BRIEF.md` (makro mimari omurga) |
| DB revizyonu (şema, tablo, kolon) | `<repo-kök>\DB_MIGRATIONS.md` |
| Ürün gerçeği (kitle, amaç, kısıtlar) | `<repo-kök>\PRODUCT.md` |
| İş alanı kavramı ve terimler | `<repo-kök>\GLOSSARY.md` |
| Mimari karar kaydı (ADR) | `docs/adr/` |
| Tasarım dili, token'lar ve kurallar | `<repo-kök>\DESIGN.md` |
| Projenin kısa/uzun kapsamlı konsolide özeti | docs/<SLUG>_PROJECT_SUMMARY_SHORT.md veya docs/<SLUG>_PROJECT_SUMMARY_LONG.md |
| Özelliklerin adım adım yapılışını ve kullanımını anlatan HTML rehberi | docs/kullanici-rehberi.html (veya docs/user-guide.html) |
| Kullanıcının bizzat gözüyle doğrulayacağı manuel test senaryoları | docs/KULLANICI_TEST_REHBERI.md |

- ⛔ Başka hiçbir yere yazma. Bu dosyaların **tek ve zorunlu yeri repo köküdür** (veya DB dokümantasyonu için `docs/database/DB_MIGRATIONS.md`, ADR için `docs/adr/`, özellik HTML rehberi için `docs/kullanici-rehberi.html`, kullanıcı test rehberi için `docs/KULLANICI_TEST_REHBERI.md`).
- ⛔ `knowledge-base.md`'yi baştan sona okuma; yalnız yaz (append). Boyutu büyüyebilir.
- ⛔ Vault'a hiçbir şey yazma. Vault salt okunur; kalıcı kararları Kütüphaneci taşır.
- ⛔ "Dosyada zaten var" dediğin kuralı ikinci kez yazma — terfi öner.
- ⛔ `TASK.md`, `ACTIVE_TASK.md`, `TODO.md` gibi mükerrer takip dosyaları açma. Kullanıcı talep etse dahi tek kaynağın `HANDOFF.md` olduğunu belirtip durumu oradan yönet (bkz. `handoff-session-continuity.md`).

Formatlar ve "ne yazılır / ne yazılmaz" listesi:
[`.agent\rules\knowledge-base-management.md`](rules/knowledge-base-management.md),
[`.agent\rules\handoff-session-continuity.md`](rules/handoff-session-continuity.md),
[`.agent\rules\design-skills-enforcement.md`](rules/design-skills-enforcement.md),
[`.agent\rules\db-migration-enforcement.md`](rules/db-migration-enforcement.md)
ve [`.agent\rules\project-brief-maintenance.md`](rules/project-brief-maintenance.md).

Şablonlar (ilk kez oluşturulurken kopyalanır, sonra dosyanın kendisi güncellenir):
[`templates\HANDOFF.template.md`](templates/HANDOFF.template.md) ·
[`templates\knowledge-base.template.md`](templates/knowledge-base.template.md) ·
[`templates\PROJECT_BRIEF.template.md`](templates/PROJECT_BRIEF.template.md) ·
[`templates\DB_MIGRATIONS.template.md`](templates/DB_MIGRATIONS.template.md) ·
[`templates\PRODUCT.template.md`](templates/PRODUCT.template.md) ·
[`templates\GLOSSARY.template.md`](templates/GLOSSARY.template.md) ·
[`templates\DESIGN.template.md`](templates/DESIGN.template.md) ·
[`templates\KULLANICI_REHBERI.template.html`](templates/KULLANICI_REHBERI.template.html)

---

## 2. Her oturumun sonunda zorunlu adımlar

1. Doğrulama kapılarını çalıştır (aşağıdaki kapılar).
2. `docs/KULLANICI_TEST_REHBERI.md` dosyasını güncelle (yoksa `docs/` altında `.agent/templates/KULLANICI_TEST_REHBERI.template.md` şablonundan oluştur).
   Kullanıcının bizzat gözüyle tarayıcıda veya konsolda özellikleri adım adım nasıl doğrulayacağını yaz.
   ⛔ **Otomasyon Yeşilliği Yanılgısına Düşme:** Otomasyon testlerinin (unit, typecheck, e2e, lint, build) yeşil
   olması kodun çalıştığını kanıtlar; kullanıcının çıktıyı gözüyle nasıl doğrulayacağını göstermez.
   Kullanıcı test adımları sunulmadan iş bitti sayılamaz ve commit onayına geçilemez.
   💡 **İstisna (Minor Rötüş & Dahili Değişiklikler):** Mevcut kullanıcı akışını, ekran bileşenlerini veya kabul senaryolarını değiştirmeyen minor rötüşlar (CSS boşluk/renk ince ayarı, dahili refactoring, tip düzeltmesi, typo) için rehbere gereksiz satır ekleme/dosya işlemi yapılmaz; raporda *"Güncelleme gerekmedi (Minor rötüş / mevcut senaryolar geçerli)"* beyan edilir.
3. 📖 **İnteraktif Özellik ve Kullanım HTML Rehberi (`docs/kullanici-rehberi.html`):**
   Projelerde her gerekli/anlamlı geliştirme sonrasında, tüm özelliklerin tek tek nasıl yapıldığını ve nasıl kullanıldığını detaylıca anlatan interaktif HTML rehberini oluştur veya güncelle (yoksa `.agent/templates/KULLANICI_REHBERI.template.html` şablonundan oluştur; İngilizce projeler için `docs/user-guide.html`).
   Her özellik kartı 4 zorunlu bölümü içermelidir:
   - 🎯 **Amaç & Katma Değer:** Ne işe yarar, hangi problemi çözer?
   - 🏗️ **Nasıl Yapıldı? (5 Katmanlı Dilim Mimarisi):** DB/Entity, Backend API/Endpoint/RPC, İstemci Entegrasyonu, UI Bileşenleri & State, Skeleton Screens UI.
   - 🚀 **Nasıl Kullanılır? (Playbook):** Sayfa rotası, menü adımları, buton etiketleri, form alanları ve doğrulama akışı.
   - 📱 **Arayüz Durumları:** Skeleton screens yükleme durumu, dolu durum, boş durum (empty state) ve hata/yeniden dene akışı.
   💡 **İstisna (Minor Rötüş & Dahili Değişiklikler):** Kullanıcı akışını veya özellik yeteneğini değiştirmeyen dahili düzeltmeler için rehbere ekleme yapılmaz; raporda *"Güncelleme gerekmedi (Minor rötüş / mevcut senaryolar geçerli)"* beyan edilir.
4. ⛔ **Sahte Bitti (Phantom Done) ve Katman Bütünlüğü Denetimi:**
   Bir özellik veya sprint için "BİTTİ / TAMAMLANDI" beyanında bulunabilmek için yalnızca birim/mock testlerinin yeşil olması ASLA YETMEZ. Veri odaklı veya sunucu/istemci etkileşimli her özellikte 5 Katmanlı Dikey Dilim (Full-Stack Vertical Slice: 1. DB/Şema/Migration → 2. Backend/View/RPC → 3. İstemci API Entegrasyonu → 4. Arayüz/UX & Eylemler → 5. Yönetim/Döngü Kapanışı) eksiksiz kanıtlanmalıdır:
   - Sadece UI bileşeni ve TypeScript/Java tipi yazıp veritabanı şemasını (tablo/kolon/migration) açmamak,
   - Mock verili testlerin yeşil olmasına aldanıp gerçek view/endpoint bağlantısını kurmamak (canlıda view'da kolon yoksa `undefined` döner ve bileşen sessizce hiç çizilmez),
   - Verinin sisteme nasıl gireceğini (admin formu, submission ekranı, döngü kapanışı) yapmadan özelliği tamamlandı saymak,
   - Arayüz/UX katmanında sunucudan/API'den veri çeken ekranlarda kaset yapısını taklit eden gri tonlu İskelet Ekranları (Skeleton screens UI) yazmayıp jenerik spinner veya donuk/boş ekran bırakmak
   **AĞIR İHLAL (Phantom Done)** sayılır. Katmanlardan biri eksikse iş "BİTTİ" ilan edilemez; durum açıkça **"YARIM (Eksik Katman: ...)"** olarak kaydedilir ve eksik parça `HANDOFF.md` §3 Sıradaki İşler tablosuna ilk sıradan eklenir.
5. Bağımlılık (paket/kütüphane), DB şeması, yeni servis/sunucusuz işlev (Edge Function, worker) veya mimari karar revizyonu yapıldıysa `PROJECT_BRIEF.md` dosyasını güncelle (yoksa `.agent/templates/PROJECT_BRIEF.template.md` şablonundan oluştur).
   ⛔ **Sahte 'Stabil' Beyanı Yasağı (Anti-Lazy Stabil Declaration):** Git çalışma ağacında bağımlılık manifesti (`package.json`, `pom.xml`, `requirements.txt`), veritabanı şeması/migration'ı (`*.sql`, `schema.prisma`, entity'ler) veya altyapı işlevi (Edge Function, worker) değiştiği halde raporda `PROJECT_BRIEF.md: Değişiklik yok / stabil` yazmak **AĞIR İHLALDIR**. Canlı mimari şema senkronize edilmelidir; `check_project_brief.py` (E3, E4) ve `check_db_migrations.py` (E5) kapıları bu durumu otomatik tespit ederek işlemi bloke eder.
6. Veritabanı revizyonu (tablo, kolon, indeks, entity) yapıldıysa `DB_MIGRATIONS.md` dosyasını güncelle (yoksa `.agent/templates/DB_MIGRATIONS.template.md` şablonundan oluştur).
7. `knowledge-base.md`'ye bu adımda çözülen hataları ve verilen kararları **yaz**.
8. `HANDOFF.md`'yi güncelle: kanıt metrikleri, katman denetimi matrisi, nerede kaldık, **sıradaki iş**,
   varsa yeni düşülen hata ve "Nasıl Test Edilir (kullanıcı)" bölümü.
9. ⛔ **"Sıradaki İş" Terminoloji ve Tekillik İlkesi (Anti-Conflict Next Work Rule):**
   - **İcra Edilen İşe "Sıradaki İş" Başlığı Koyma Yasağı:** Oturumda veya yanıtta tamamlanan/geliştirilen adımları anlatırken ASLA `### Sıradaki İş: [İş]` başlığı kullanılamaz! Bu bölümler daima **"İcra Edilen Görev / Yapılan Geliştirme: [İş Tanımı]"** olmalıdır. Çünkü kullanıcı o işi henüz yapılmamış, sırada bekleyen iş zannederek çelişkiye düşer.
   - **Yanıt Boyunca Tek ve Tutarlı "Sıradaki İş" Beyanı:** Bir yanıtta "Sıradaki İş(ler)" ifadesi YALNIZCA VE YALNIZCA bir sonraki oturumda/adımda başlanacak açık işleri ifade eder. Yanıt içerisinde aynı veya çelişkili iki farklı "sıradaki iş" bilgisi yer alamaz.
   - **Devir Raporunda Tekillik:** Devir raporu bloğunda sıradaki işler tek bir maddede (`- **Sıradaki İşler (Canlı Görev Panosu):** 1. ⏭️ ..., 2. ⬜ ...`) sunulur; `HANDOFF.md` altında mükerrer `* Sıradaki İş:` açılmaz.
10. Kullanıcıya şeffaf rapor ver — aşağıdaki blok **zorunludur**.
11. Commit istenmedikçe `git commit` / `push` / `tag` **yapma**.

```markdown
### 📝 OTURUM DEVİR & BİLGİ TABANI GÜNCELLEMESİ (HANDOFF & KB RAPORU)
- **Kullanıcı Test Rehberi:** [docs/KULLANICI_TEST_REHBERI.md güncellendi mi? Eklenen test senaryoları/adımları veya "Güncelleme gerekmedi (Minor rötüş / mevcut senaryolar geçerli)"]
- **Özellik HTML Rehberi:** [docs/kullanici-rehberi.html güncellendi mi? Eklenen özellikler ve mimari/kullanım detayları veya "Güncelleme gerekmedi (Minor rötüş / mevcut senaryolar geçerli)"]
- **Katman Bütünlüğü (Full-Stack Slice):** [5 Katman doğrulandı mı? (DB, View/RPC, API, UI, Admin/Giriş Formu) veya "Salt UI/İstemci (DB bağımlılığı yok)" veya "YARIM (Eksik: ...)"]
- **PROJECT_BRIEF.md:** [Güncellendi mi? (Stack/DB/Karar revizyonu) veya "Değişiklik yok / stabil"]
- **knowledge-base.md:** [Eklenen hata/karar başlıkları ve kısa özeti (yoksa "yeni yok")]
- **DB Migrations:** [DB_MIGRATIONS.md güncellendi mi? Eklenen revizyonlar veya "DB değişikliği yok / kapsam dışı"]
- **HANDOFF.md:**
  * Güncellik Kanıtı: [Ölçülen gerçek sayılar — test, assert, derleme, chunk boyutları]
  * Nerede Kaldık: [Tamamlanan adım ve durum]
  * Bu Projede Düşülen Hatalar: [Yeni ders/tuzak veya "yeni yok"]
  * Bu Projede Alınan Kararlar: [Yeni karar veya "yeni yok"]
- **Sıradaki İşler (Canlı Görev Panosu):** [Varsa numaralı liste (1. ⏭️ ..., 2. ⬜ ...). Yalnızca mevcut sprint bittiyse PRD/Yol Haritasına göre sıradaki hedefi belirtin (örn. "Mevcut sprint tamamlandı. PRD'ye göre sıradaki: Sprint X"). YALNIZCA tüm PRD ve ürün fazları %100 bittiğinde "Açık iş yok — proje tamamlandı" yazılabilir.]
- **Kullanılan MCP:** [context7 / sequential-thinking — ne için kullanıldı veya "kullanılmadı"]
- **Aktif skill'ler:** [Okunan skill adları]
```

> 💡 **Rapor Çıktı Tetikleme Politikası:** Bu blok varsayılan olarak yalnızca **görev bitiminde (commit öncesi)**
> ve **oturum kapanışında** üretilir (`[disabled, disabled, disabled, enabled, enabled]`).
> Ara kodlama ve test adımlarında token tasarrufu için basılmaz. Ayarlar ve detaylar için: `readme-help.md`.

---

## 3. Doğrulama kapıları — "bitti" demeden önce

Bu bölümdeki her kural **üç sınıftan birindedir** ve sınıfı kural dosyasının
front matter'ında `sinif:` alanıyla **yazılıdır.** Ajan hangi kuralı
doğrulayabileceğini bu alandan görür:

| Sınıf | Anlamı | Doğrulama |
|---|---|---|
| `OLCULEBILIR` | Ölçülebilir | Aşağıdaki komut çalıştırılır, exit kodu okunur |
| `TUTUM` | Ölçülemez | Ajan beyanı; `knowledge-base.md`'ye yazılır |
| `SUREC` | Akış | Skill adımları izlenir; kapı yoktur |

⛔ **"zorunlu" yazan bir kural `OLCULEBILIR` değilse, onu uyguladığını
kanıtlayamazsın — sadece beyan edersin.** Bu ayrım gizli değildir.

### 3.1 Ölçülebilir kapılar

> ⛔ Bu tablo **elle yazılmaz.** Kaynak kural dosyalarının front matter'ıdır.
> `python .agent/skills/musgoku/scripts/rules_gates.py --emit-table` ile üretilir;
> bayatlık `rules_gates.py` tarafından **hata** olarak raporlanır.

<!-- GATE-TABLE:BEGIN -->
| Yığın | Zorunlu komut | Ayrıntı |
|---|---|---|
| Backend / API dokümantasyonu | `python .agent/skills/musgoku/scripts/check_api_docs.py` | [`api-documentation-enforcement.md`](rules/api-documentation-enforcement.md) |
| Backend / Veritabanı migration | `python .agent/skills/musgoku/scripts/check_db_migrations.py` | [`db-migration-enforcement.md`](rules/db-migration-enforcement.md) |
| Tasarım / sözleşme ve DESIGN.md uyumu | `python .agent/skills/musgoku/scripts/check_design_contract.py` | [`design-skills-enforcement.md`](rules/design-skills-enforcement.md) |
| Tasarım / skill sahipliği | `python .agent/skills/musgoku/scripts/check_design_skills.py` | [`design-skills-enforcement.md`](rules/design-skills-enforcement.md) |
| Tasarım / zanaat tabanı ve anti-slop | `python .agent/skills/musgoku/scripts/check_design_slop.py` | [`design-skills-enforcement.md`](rules/design-skills-enforcement.md) |
| Tasarım / tema kontrastı ve WCAG uyumu | `python .agent/skills/musgoku/scripts/check_theme_contrast.py` | [`design-skills-enforcement.md`](rules/design-skills-enforcement.md) |
| Frontend / bundle bütçesi | `python .agent/skills/musgoku/scripts/check_bundle_limits.py` | [`frontend-bundle-limits.md`](rules/frontend-bundle-limits.md) |
| Proje Yönetimi / Oturum Devri ve Görev Panosu | `python .agent/skills/musgoku/scripts/check_handoff.py` | [`handoff-session-continuity.md`](rules/handoff-session-continuity.md) |
| Frontend / i18n | `python .agent/skills/i18n-localization/scripts/i18n_checker.py` | [`i18n-enforcement.md`](rules/i18n-enforcement.md) |
| TypeScript / React | `npx tsc --noEmit` | [`no-unused-code.md`](rules/no-unused-code.md) |
| Java / Spring derleme | `mvn clean compile -DskipTests` | [`no-unused-code.md`](rules/no-unused-code.md) |
| Java / kullanılmayan kod | `pwsh -NoProfile -File .agent/skills/musgoku/scripts/check-unused.ps1` | [`no-unused-code.md`](rules/no-unused-code.md) |
| Proje Mimarisi / Canlı Brief | `python .agent/skills/musgoku/scripts/check_project_brief.py` | [`project-brief-maintenance.md`](rules/project-brief-maintenance.md) |
| Skill sözleşmesi / tetikleyici sözlüğü | `cd .agent/skills/ui-ux-pro-max/scripts/tests && python -m unittest test_skill_contracts` | [`skill-trigger-routing.md`](rules/skill-trigger-routing.md) |
| Sprint / kanban / MVP | `python .agent/skills/musgoku/scripts/check_sprint_board.py` | [`sprint-delivery-workflow.md`](rules/sprint-delivery-workflow.md) |
| Frontend / Vite SPA | `python .agent/skills/musgoku/scripts/check_vite_spa.py` | [`vite-spa-enforcement.md`](rules/vite-spa-enforcement.md) |
<!-- GATE-TABLE:END -->

Ek kapı (tek kural dosyasına bağlı değildir):

| Kapsam | Komut |
|---|---|
| Kural setinin kendisi | `python .agent/skills/musgoku/scripts/rules_gates.py --strict` → `[OK]` |

### 3.2 Ölçülemeyen kurallar

> ⛔ Bu tablo **elle yazılmaz.** `rules_gates.py --emit-attitude` ile üretilir.

| Kural | Sınıf |
|---|---|
| `bug-diagnosis-enforcement.md` | SUREC |
| `development-workflow.md` | SUREC |
| `mandatory-git-release-workflow.md` | SUREC |
| `no-unauthorized-commit.md` | SUREC |
| `trigger-rule-action.md` | SUREC |
| `always-read-skills.md` | TUTUM |
| `knowledge-base-management.md` | TUTUM |
| `mcp-usage-enforcement.md` | TUTUM |
| `no-silent-wait.md` | TUTUM |

### 3.3 Kapsam-Duyarlı Doğrulama İlkesi (Scope-Aware Verification)

⛔ **Körlemesine Test Koşturma Yasağı:**
Yukarıdaki ölçülebilir kapı komutları (`npm run build`, `npx tsc`, `mvn clean compile`, `pnpm test`, `test:e2e`) **yalnızca ilgili etki alanındaki dosyalar değiştiğinde** çalıştırılır:

1. **Uygulama Kodu Değiştiğinde (`src/**`, `components/**`, `api/**`, `package.json`, `pom.xml` vb.):**
   - İlgili derleme (`build`), tip (`typecheck`), birim ve e2e test komutları **ZORUNLUDUR**.
2. **Yalnızca Ajan Kuralları veya Dokümantasyon Değiştiğinde (`.agent/**`, `*.md`, `docs/**`, `.gitignore`):**
   - Uygulama build'i (`npm run build`, `pnpm build`), testleri (`pnpm test`, `mvn test`) ve e2e testler **ÇALIŞTIRILMAZ (ATLANIR / SKIPPED)**. Kaynak kod değişmediği için testlerin kırılma riski yoktur; çalıştırmak gereksiz token, CPU ve zaman israfıdır.
   - Varsa yalnızca ilgili kural kapısı (`python .agent/skills/musgoku/scripts/rules_gates.py` vb.) çalıştırılır.
   - Devir raporunda dürüstçe beyan edilir: *"Uygulama Testleri: Kapsam dışı (Yalnızca .agent/ ve dokümantasyon değişti)"*.

⛔ **Bir şeyi doğrulamadıysan "yaptım" deme.** Test/build çalıştırılmadıysa
"çalıştırılmadı" de. Uydurma kanıt, kanıtsız başarıdan kötüdür.

⛔ **Sessizce bekleme.** ~30 saniyeyi aşan her iş için önce tek satır yaz:
ne yapıyorum, en fazla kaç dakika sürecek. Bekleme döngüsü kurma; sunucu
başlatma asenkron olsun, bekleyerek değil **kısa sağlık kontrolü** yaparak ilerle.
Ayrıntı: [`rules/no-silent-wait.md`](rules/no-silent-wait.md).

---

## 4. Skill ve kural kullanımı

- Kod yazmadan önce `.agent/skills/` altındaki ilgili skill'i oku.
- Yönlendirme: [`.agent\skills\musgoku\SKILL.md`](skills/musgoku/SKILL.md)
- Kurallar dizini tek kaynaktır: [`.agent\rules/`](rules/) — `trigger-rule-action.md` hepsini bağlar.
- 💡 **Otonom Bağlamsal Tetikleme (Autonomous Activation):** Ajan, kullanıcının belirli bir sihirli kelimeyi (trigger) yazmasını **pasifçe beklemez.** Görevin bağlamı (UI değişikliği, 2+ alternatifli mimari ikilem, bug çözümü, SEO, güvenlik, görev planlama/parçalama vb.) ilgili alana girdiği anda kullanıcı o kelimeyi unutsa dahi ilgili skill'i (`karpathy-guidelines` Council, `diagnosing-bugs`, tasarım üçlüsü, `seo-growth`, `security-audit`, `doc-coauthoring` + `musgoku` + `tdd`) **otonom olarak** devreye alır. (Bkz. [`rules/skill-trigger-routing.md`](rules/skill-trigger-routing.md) §0).
- Yeni iş mantığı, servis veya endpoint geliştirmede `tdd` (kırmızı → yeşil döngüsü); hata ayıklamada ise `bug-diagnosis-enforcement` (önce kırmızı geri bildirim döngüsü) tavizsiz uygulanır.
- Tasarım/UI taleplerinde `canvas-design` + `frontend-design` + `ui-ux-pro-max`
  birlikte okunur; hangi konunun sahibi olduğunu `design-skills-enforcement.md`
  §3 sahiplik haritasından doğrula.
- Skill seti güncelleme taleplerinde (`/goku-skills-update`, `/gs-update`, "Goku skill güncelle", "skill update", "GS update", "GS güncelle", "goku update", "skillset güncelle" vb.) `gs-update` / `musgoku` cerrahi güncelleme protokolü ([`references/skill-set-update.md`](skills/musgoku/references/skill-set-update.md)) işletilir: kullanıcıya kapsam (Mevcut Workspace vs Global Dağıtım vs Her İkisi) sorulur; `npx goku-dev-skills update` (veya `--remote` / `delivery.py`) çalıştırılır; proje kural bloğu korunur, kurulu olmayan skill'ler indirilmez.

---

## 5. Git kuralları

- ⛔ Kullanıcı açık onay vermeden `git commit` / `tag` / `push` **çalıştırma.**
- 💡 **Peşin Yetki (`commitx`, `commitle`):** Kullanıcı doğrudan eylem olarak `commitx` veya `commitle` yazdığında bu talep peşin açık onaydır; ajan ara onay (commit/push ayrımı) sormadan add, commit, tag ve push adımlarını tek seferde tamamlar.
- Onay sonrası tüm commit/release adımları `git-release-workflow` skill'iyle,
  **kesintisiz** yürütülür; her komut için ayrı onay istenmez.
- Ayrıntı: [`no-unauthorized-commit.md`](rules/no-unauthorized-commit.md),
  [`mandatory-git-release-workflow.md`](rules/mandatory-git-release-workflow.md).

---

## 6. Best practice doğrulaması (MCP)

| MCP | Ne zaman zorunlu |
|---|---|
| `context7` | Yeni paket ekliyorsan · sürüm farkı kararı · API ismi/parametresi yazıyorsan · hata mesajı docs ile ilgiliyse |
| `sequential-thinking` | 3+ adımlı plan · iki yaklaşım arasında seçim · güvenlik/yetki sınırı · belirsiz mimari karar |

Kullanmadıysan **"kullanmadım" de.** Ayrıntı ve sınır listesi:
[`mcp-usage-enforcement.md`](rules/mcp-usage-enforcement.md).

---

## 7. Tasarım kuralları

- Tasarım/UI/UX taleplerinde üç tasarım skill'i (`canvas-design`,
  `frontend-design`, `ui-ux-pro-max`) birlikte okunur ve yanıtta devrede
  oldukları belirtilir.
- Tasarım alanındaki 12 skill'in **sahiplik sınırı**
  [`rules\design-skills-enforcement.md`](rules/design-skills-enforcement.md) §3'te
  tanımlıdır. Bir konuyu iki skill sahiplenmez — çakışmada o tabloya bak.
- Generic/AI-slop çıktı kabul edilmez.
- **İskelet Ekranlar (Skeleton screens UI) Kesin Zorunluluktur:** Bir web sitesinde veya mobil uygulamada içerikler sunucudan yüklenirken gerçek verilerin yerine gösterilen, sayfanın genel yerleşimini (wireframe/kaset yapısını) taklit eden gri tonlu görsel taslakların (Skeleton screens) sunulması zorunludur. AI ajanları bu kuralı ASLA ATLAYAMAZ; veri yükleme durumlarında jenerik spinner veya boş ekran kullanılamaz (spinner yalnız form submit butonlarında geçerlidir). Ayrıntı: [`design-skills-enforcement.md`](rules/design-skills-enforcement.md) §2.2.1.
- Ayrıntı: [`design-skills-enforcement.md`](rules/design-skills-enforcement.md).

---

## 8. Frontend kuralları (yalnız frontend projesinde geçerli)

- Vite SPA / React projelerinde Next.js konseptleri kullanılmaz.
  Ayrıntı: [`vite-spa-enforcement.md`](rules/vite-spa-enforcement.md).
- Bundle ve chunk bütçesi ihlal edilmez.
  Ayrıntı: [`frontend-bundle-limits.md`](rules/frontend-bundle-limits.md).
- UI metni hardcode yazılmaz.
  Ayrıntı: [`i18n-enforcement.md`](rules/i18n-enforcement.md).

---

## 9. Güvenlik sınırı

- Tıbbi/hukuki/finansal risk doğuracak konularda veya güvenlik açığını
  kapatacak kod değişikliklerinde gerekçeyi kullanıcıya açıkça bildir.
- Şifre, token, kişisel veri asla loglanmaz, asla kaynak koda gömülmez.

---

## 10. Bu dosyaya ve kural dosyalarına kural ekleme kuralı (agent için)

⛔ **Global kurallar (bu dosyanın 0–9. bölümleri ve `.agent/rules/*.md` dosyalarının ana içeriği) en üsttedir, projeler arası ortaktır ve değiştirilmez.**

Proje için yeni veya istisnai bir kural gerekiyorsa:

1. **Önce mükerrerlik kontrolü yap:** Bu dosyada veya `.agent\rules/` altında
   aynı amaca hizmet eden bir kural varsa **kesinlikle yenisini ekleme**;
   *"zaten var, şurada"* de ve mevcut kuralı uygula.
2. **Kural dosyasının en altına ekle:** Yalnızca ilgili kural dosyasının (veya bu dosyanın)
   **en altında** yer alan `## Proje Bazlı Ek Kurallar` başlığı altına `### <Kural Başlığı>` olarak ekle.
3. **Global hiyerarşiyi bozma:** Global bölümlerin yapısını, sırasını, numaralandırmasını
   veya üslubunu asla değiştirme.

---

## Proje Bazlı Ek Kurallar

> Bu bölüm **projeye özeldir** ve `.agent/` klasörüyle birlikte projeye dağıtılır.
> Altında yalnızca bu projenin kendi gereksinimi yazılır — genel kural değil.
> Bu bölüme yazarken §10'daki mükerrerlik kontrolü zorunludur.

### Bu proje için ek kurallar

_(Aşağıdakiler yalnız **skillSetWorks** deposuna aittir. Genel kural değildir;
eklenen kural zaten kapsamı karşılıyorsa §10 gereği yazılmaz.)_

### Depo ne yapar, ne yapmaz

Bu depo **uygulama kodu içermez.** Yalnız projeler arası ortak ajan çalışma
kurallarını ve skill'leri üretir ve dağıtır. Buraya build çıktısı, uygulama
kodu, port, veritabanı adı veya proje mimarisi yazılmaz. Yazılacak tek şey ajan
kuralı, skill veya dağıtım tanımıdır.

### Tek gerçek kaynak ve dağıtım yönü

`skillSetWorks/.agent/` **tek gerçek kaynaktır.** Hedef projelerdeki `.agent/`
kopyaları türetilmiş çıktıdır. Bir kural ya da skill değişikliği:

1. **Burada** yapılır (`skillSetWorks/.agent/…`)
2. `python delivery.py --verify` ile hedeflerin eşit olduğu kanıtlanır
3. `python delivery.py` ile dağıtılır

⛔ Hedef projede `.agent/` altında yapılan değişiklik bir sonraki dağıtımda
**kaybolur** — çünkü dağıtım hedef ağacı önce siler. Bu yüzden hedef projede
`.agent/` içine elle yazma yapma; kural gerekiyorsa burada tanımla.
Hedefte korunması gereken tek şey `AGENTS.md → ## Proje Bazlı Ek Kurallar`
bölümüdür ve dağıtım onu otomatik korur.

### Değişiklik sonrası zorunlu doğrulama kapıları

```bash
# 1. Sözleşme + çekirdek test paketi (173 test)
cd .agent/skills/ui-ux-pro-max/scripts/tests && python -m unittest discover -p "test_*.py"

# 2. pytest paketleri (ui-styling 64 · design-system 2 · brand 21)
cd ../../ui-styling/scripts && python -m pytest tests -q
cd ../../design-system/scripts && python -m pytest tests -q
cd ../../brand/scripts && python -m pytest tests -q
```

`pytest` gerekir (`pip install pytest pytest-cov pytest-mock`). Bu kapı
koşturulmadan "bitti" deme.

⛔ Test koşumu `__pycache__`, `.pytest_cache` ve `.coverage` klasörleri
bırakır. Bunlar dağıtıma **girmez** (`delivery.py` filtreler), ama kaynak
ağacında birikirse `tree_index` sayımlarını bozar. Yeni skill eklerken
`delivery.py` → `copy_tree` → `ignore_patterns` listesini gözden geçir.

### Git

Bu depo bir git deposu **değildir** (`git status` çalışmaz). Hedef projelerde
`.agent/` izleme durumu **projeden projeye değişir ve bilinçlidir**:

- `ocai`, `FEProjectv1` → `.agent/` izleniyor
- `bookmarkManagerProject` → `.gitignore` yalnız `AGENTS.md` + `rules/` +
  `templates/` izliyor (`.agent/skills/` hariç, gerekçe `.gitignore` yorumunda)
- `kalansure` → `.agent/` **tamamen** ignore'da

⛔ **Bu depodan git komutu çalıştırılmaz ve hedef projelerde commit yapılmaz.**
Commit kararı kullanıcının, proje başına ayrı ayrı verilir. `delivery.py`
zaten hiçbir git komutu çağırmaz.

### Yeni skill ekleme sırası

1. `skillSetWorks/.agent/skills/<yeni-skill>/` altına ekle
2. `rules/skill-trigger-routing.md` §A tablosuna satır ekle (yoksa
   `test_dictionary_exists_and_lists_every_skill` kırmızıya döner)
3. `SKILL.md` `description` alanını sözleşmeye göre yaz:
   25-70 kelime · `Tetikleyiciler:` · `Tetiklenmez:` · TR + EN örnek ·
   araç/proje adı yok · sözlük atfı zorunlu
4. `python scripts/generate_skills_catalog.py` çalıştırarak `.agent/skills-catalog.html` dosyasını güncelle
   (her yeni skill veya yapı eklendiğinde zorunlu; `test_skills_catalog.py` bayatlığı yakalar)
5. Yukarıdaki doğrulama kapılarını koştur (`python tests/run_all.py` ve sözleşme testleri)
6. `python delivery.py --dry-run` → hedefleri kontrol et
7. `python delivery.py` → dağıt
8. `delivery.md` §6 çalışma kaydını güncelle

### Ajan bulma tuzağı

Çalışma alanında bu repo dışında da `.agent/` klasörü olan
projeler bulunabilir. Bu depo yalnız `delivery.md` config'inde
listelenen yollara dağıtım yapar — diskte başka `.agent/` olması onları
kapsam dışı bırakmaz.