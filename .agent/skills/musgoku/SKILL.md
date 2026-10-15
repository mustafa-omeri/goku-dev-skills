---
name: musgoku
description: >-
  Global geliştirme yönlendiricisi. Backend (Java, Spring Boot, JPA, REST, WebSocket,
  güvenlik, pagination) ve frontend (React, TypeScript, i18n, bundle) taleplerini doğru
  sub-skill'e yönlendirir; kalite kapılarını ve doğrulama adımlarını tanımlar.
  Tetikleyiciler: "API yaz", "endpoint ekle", "entity oluştur", "pagination ekle",
  "güvenlik", "refactoring", "hata düzelt", "bileşen oluştur", "form ekle", "route ekle",
  "add endpoint", "create entity", "refactor", "fix bug". Tetiklenmez: tek satırlık kod
  düzeltmesi veya planlama gerektirmeyen işler. Tam sözlük:
  .agent/rules/skill-trigger-routing.md
---


# MuSGoKu — Global Geliştirme Yönlendiricisi

> Bu skill **projeler arası ortaktır.** Proje adı, paket adı, sürüm, port,
> modül listesi veya DB adı burada **bulunmaz.** Projeye özel olan tek yer
> `AGENTS.md` → "Proje Bazlı Ek Kurallar" bölümüdür.

---

## Adım 0 — Yığını tespit et (kod yazmadan önce)

Bu skill yönlendiricidir. Hangi kola gireceğini **tahmin etme**, projeyi oku:

| Ne | Nerede bak |
|---|---|
| Backend dili ve framework | `pom.xml` · `build.gradle` · `package.json` |
| Frontend yığını | `package.json` → `dependencies` |
| Aktif profiller | `src/main/resources/application-*.yml` |
| Modül/dizin yapısı | kaynak kökünün üst düzey dizinleri |

Tespit yapamazsan **kullanıcıya sor.** Tahmin yürütme.

---

## Adım 1 — Görev Yönlendirme Matrisi

### Backend

| Talep | Okunacak referans |
|---|---|
| Controller / endpoint / REST API | [references/spring-boot-api.md](./references/spring-boot-api.md) |
| Entity / DTO / Repository | [references/data-layer.md](./references/data-layer.md) |
| Sayfalama / sıralama / liste uç noktası | [references/pagination-search.md](./references/pagination-search.md) |
| **Arama** (normalizasyon, arama kolonu, DB çözümü) | [references/search-strategies.md](./references/search-strategies.md) |
| Liste performansı / test / anti-pattern | [references/pagination-checklists.md](./references/pagination-checklists.md) |
| Yeni modül / mimari karar / CQRS / sürüm farkları | [references/project-architecture.md](./references/project-architecture.md) |
| Güvenlik / JWT / yetki / loglama / performans | [references/security-logging.md](./references/security-logging.md) |
| WebSocket / gerçek zamanlı iletişim | [references/websocket.md](./references/websocket.md) |
| Refactoring / clean code / kod kalitesi | [references/clean-code-conventions.md](./references/clean-code-conventions.md) |
| **API dokümantasyonu** | [`rules/api-documentation-enforcement.md`](../../rules/api-documentation-enforcement.md) |
| **Veritabanı revizyonu & migration** | [`rules/db-migration-enforcement.md`](../../rules/db-migration-enforcement.md) |

### Frontend (Vite SPA)

| Talep | Okunacak sub-skill |
|---|---|
| UI bileşen oluşturma / düzenleme | [skills/musgoku-react-component.md](./skills/musgoku-react-component.md) |
| **Dizin / dosya yerleşimi kararı** | [references/frontend-project-structure.md](./references/frontend-project-structure.md) |
| API entegrasyonu / veri çekme / cache / liste tazeleme | [skills/musgoku-api-data-layer.md](./skills/musgoku-api-data-layer.md) |
| Form / validasyon | [skills/musgoku-forms-validation.md](./skills/musgoku-forms-validation.md) |
| Route / korumalı sayfa / yetki | [skills/musgoku-routing-auth.md](./skills/musgoku-routing-auth.md) |
| Stil / Tailwind / Shadcn / dark mode | [skills/musgoku-styling-ui.md](./skills/musgoku-styling-ui.md) → shadcn/Tailwind referans kataloğu için [`skills/ui-styling/`](../ui-styling/SKILL.md) |
| TypeScript tip kalitesi / build uyumu | [skills/musgoku-typescript-quality.md](./skills/musgoku-typescript-quality.md) |
| i18n / çeviri | [`skills/i18n-localization/`](../i18n-localization/SKILL.md) |
| React performans / re-render / bileşen kompozisyonu / kodlama standartları | [`skills/react-best-practices/`](../react-best-practices/SKILL.md) |
| Bundle / chunk / performans | [`rules/frontend-bundle-limits.md`](../../rules/frontend-bundle-limits.md) |
| Docker / prod kurulum | [`skills/production-docker-architect/`](../production-docker-architect/SKILL.md) |

### Frontend (Next.js) — yalnız yığın Next.js ise

| Talep | Okunacak sub-skill |
|---|---|
| App Router / RSC / SSR / Route Handlers | [skills/musgoku-nextjs-fullstack.md](./skills/musgoku-nextjs-fullstack.md) |
| Server Actions / tip güvenli mutasyon | [skills/musgoku-next-safe-action.md](./skills/musgoku-next-safe-action.md) |
| Shadcn + Next.js + tema | [skills/musgoku-shadcn-nextjs.md](./skills/musgoku-shadcn-nextjs.md) |

### Ortak

| Talep | Okunacak yer |
|---|---|
| Tasarım / UI/UX | [`rules/design-skills-enforcement.md`](../../rules/design-skills-enforcement.md) → `canvas-design` + `frontend-design` + `ui-ux-pro-max` |
| Hangi tasarım skill'i sahip? (çakışma şüphesi) | [`rules/design-skills-enforcement.md`](../../rules/design-skills-enforcement.md) §3 sahiplik haritası |
| Renk / font paleti seçimi (hazır tema) | [`skills/theme-factory/`](../theme-factory/SKILL.md) |
| Design token üretimi (primitive → semantic → component) | [`skills/design-system/`](../design-system/SKILL.md) |
| Marka kimliği / ton / görsel kimlik / varlık | [`skills/brand/`](../brand/SKILL.md) |
| Sunum içeriği (strateji, metin, düzen) | [`skills/slides/`](../slides/SKILL.md) |
| Sunum üretimi (HTML render + token denetimi) | [`skills/design-system/`](../design-system/SKILL.md) → "Slayt Üretimi" |
| Banner / kapak / reklam görseli (sabit px) | [`skills/banner-design/`](../banner-design/SKILL.md) |
| Logo & CIP brief'i / sosyal medya görseli | [`skills/design/`](../design/SKILL.md) |
| Poster / ölçüsüz görsel sanat | [`skills/canvas-design/`](../canvas-design/SKILL.md) |
| Git commit / release | [`rules/mandatory-git-release-workflow.md`](../../rules/mandatory-git-release-workflow.md) → `git-release-workflow` |
| Oturum devri / bilgi tabanı | [`rules/handoff-session-continuity.md`](../../rules/handoff-session-continuity.md) + [`rules/knowledge-base-management.md`](../../rules/knowledge-base-management.md) |
| PRD / gereksinim dokümanı / kapsam netleştirme | [`skills/musgoku-prd/`](../musgoku-prd/SKILL.md) |

> **Birden fazla referans gerekiyorsa hepsini oku.**
> Örn. yeni bir backend modülü: `project-architecture.md` + `spring-boot-api.md` +
> `data-layer.md`. Liste endpoint'i: `pagination-search.md` + `data-layer.md`.

---

## Adım 2 — Her Zaman Geçerli Kurallar (Always-On)

### 1. Oturum sürekliliği
Kod yazmadan önce repo kökündeki `HANDOFF.md` okunur.
→ [`rules/handoff-session-continuity.md`](../../rules/handoff-session-continuity.md)

### 2. AI çalışma tarzı
- Deneyimli kıdemli geliştirici olarak davran.
- Planı açıkça yaz; kodla onay verildikten sonra ilerle.
- Mevcut kod yapısını bozmadan geliştir; akış ve iş mantığına dokunma.

### 3. Temel prensipler
- SOLID · DRY · KISS · YAGNI · OWASP
- Yüksek kohezyon, düşük bağlantı
- Sabit yerine enum/metadata
- Tarihler ISO 8601; makineden bağımsız zaman işleme

### 4. Kod kalitesi
- ⛔ Kullanılmayan import / local değişken / dosya bırakma
- 300 satırı aşan dosyayı böl (Java), 200 satırı aşan bileşeni böl (TSX)
- Yan etkili ifadeyi atama yapmadan çağır
- Dev/prod ortamında sahte veri üretme
- Ortam değişkeni dosyasını onaysız değiştirme

### 5. Hata yönetimi
- Hata iç/dış olarak ayrıştırılır: kullanıcıya anlamlı mesaj, log'a teknik detay
- Kullanıcı işlemlerinde yetki kontrolü (token ≠ istek)
- Çözülen her kalıcı hata `knowledge-base.md`'ye yazılır

### 6. Yanıt standardı
- Tüm yanıtlar projenin mevcut zarf formatında döner; zarf yoksa
  `references/spring-boot-api.md` §3 biçimi kullanılır.
- Yanıtta hangi kapıların çalıştırıldığı açıkça yazılır.

### 7. Dokümantasyon
- Backend: her API değişikliğinde modül dokümanı güncellenir
  → [`rules/api-documentation-enforcement.md`](../../rules/api-documentation-enforcement.md)
- Frontend: her görünür metin iki dil dosyasına senkron eklenir
  → [`rules/i18n-enforcement.md`](../../rules/i18n-enforcement.md)

### 8. Best practice doğrulaması
- Yeni paket / sürüm / API belirsizliği → `context7`
- 3+ adımlı plan / güvenlik sınırı / iki yaklaşım → `sequential-thinking`
- → [`rules/mcp-usage-enforcement.md`](../../rules/mcp-usage-enforcement.md)

---

## Adım 3 — İş Akışı (özet)

1. **Tespit:** yığını, modülü ve etkilenen katmanı belirle.
2. **Okuma:** `HANDOFF.md` → ilgili referans/sub-skill → gerekirse MCP.
3. **Uygulama:** kurallara uy kod; dokümantasyonu aynı adımda güncelle.
4. **Doğrulama:** ilgili kalite kapılarını çalıştır, gerçek çıktıyı göster.
5. **Kayıt:** `knowledge-base.md` + `HANDOFF.md` güncelle.
6. **Rapor:** HANDOFF & KB rapor bloğunu göster.
7. **Onay:** commit onayı iste; onay verilirse release workflow'u kesintisiz çalıştır.

Tam akış: [`rules/development-workflow.md`](../../rules/development-workflow.md)

---

## Adım 4 — Kontrol Listesi

### Ortak

- [ ] `HANDOFF.md` okundu mu?
- [ ] Görevle ilgili referans/sub-skill okundu mu?
- [ ] Mevcut kod yapısı anlaşıldı mı?
- [ ] `knowledge-base.md`'de benzer hata var mı? (okunmadan geçilmedi mi?)
- [ ] Plan açıkça sunuldu mu?
- [ ] Kullanılmayan kod bırakılmadı mı?
- [ ] Kalite kapıları çalıştırıldı ve **gerçek çıktı** gösterildi mi?
- [ ] `HANDOFF.md` + `knowledge-base.md` güncellendi mi?
- [ ] Sonraki işler raporlandı mı (ya da "açık iş yok" denildi mi)?

### Backend

- [ ] Yanıt zarfı standart formatta mı?
- [ ] Endpoint yalnız GET/POST mu, eylemi adında belirtiyor mu?
- [ ] DTO katmanlar arası taşıma için kullanılıyor mu?
- [ ] Yetki kontrolü servis katmanında mı?
- [ ] Swagger annotation'ları ve modül dokümanı güncel mi?
- [ ] `mvn test-compile` temiz mi?
- [ ] `check-unused.ps1` → `[OK]` mi?

### Frontend

- [ ] Yığın Vite SPA mı, Next.js mi? (yanlış kavram kullanılmadı mı?)
- [ ] Tüm görünür metinler i18n anahtarından mı geliyor?
- [ ] Her iki dil dosyası senkron mu?
- [ ] React hook sırası ve erken return kurallarına uyuldu mu?
- [ ] Mutasyon sonrası ekran **refresh olmadan** doğru değeri gösteriyor mu?
- [ ] Bundle & chunk bütçesi terminal çıktısında ölçüldü mü, >500 kB (lazy) / >200 kB (entry) aşımı veya Vite uyarısı var mı?
- [ ] `npx tsc --noEmit` temiz mi?
