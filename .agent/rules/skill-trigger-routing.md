---
name: Skill Trigger Routing
description: Hangi anahtar kelime, hangi skill'i açar. Tasarım/UI, marka, sunum, doküman, backend, frontend, git, Docker ve kalite talepleri için pozitif tetikleyici sözlüğü, kombinasyon senaryoları ve ayrım karar ağacı. Talep geldiğinde hangi skill'in açılacağına karar vermek için okunur.
sinif: OLCULEBILIR
kapi:
  - yigin: "Skill sözleşmesi / tetikleyici sözlüğü"
    komut: "cd .agent/skills/ui-ux-pro-max/scripts/tests && python -m unittest test_skill_contracts"
---

# ⛔ Skill Tetikleyici Sözlüğü

Bu dosya **tetikleyici sözlüğünün tek sahibidir.** Anahtar kelime → skill eşlemesi
burada yaşar; `SKILL.md` `description` alanları yalnız **özet** ve **atıf** taşır.

> ⚠️ **Sahiplik ile karıştırma.** Hangi konunun sahibi kim sorusu
> [`design-skills-enforcement.md`](./design-skills-enforcement.md) §3'te tanımlıdır
> ve kalıcıdır. Bu dosya **operasyöneldir**: "şu kelime hangi dosyayı açar."

## 0. Çift Kanatlı Tetikleme İlkesi (Otonom Bağlam vs. Manuel Kısayol)

Tetikleme mekanizması iki kanaldan çalışır:

### 1. Otonom (Bağlamsal) Tetikleme — Varsayılan ve Zorunlu
⛔ **Kullanıcı Sihirli Kelimesine Bağımlılık Yasağı (No Passive Waiting for Keywords):**
Ajan, kullanıcının belirli bir sihirli kelimeyi (trigger) yazmasını **asla pasifçe beklemez.** Görevin bağlamı, dokunulan dosyalar ve hedeflenen iş mantığı aşağıdaki tablodaki durumlardan birine uyuyorsa, kullanıcı o kelimeyi söylemeyi **unutsa dahi** ajan ilgili yeteneği **otonom olarak (unprompted)** devreye sokar ve yanıtta açıkça bildirir:

| Durum / Görev Bağlamı | Otomatik Devreye Giren Skill / Araç | Neden Otonom? |
|---|---|---|
| **Arayüz / UI / CSS / Görsel Değişiklik:** `.tsx`, `.jsx`, `.css`, HTML, form, modal veya buton tasarımı | `frontend-design` + `ui-ux-pro-max` + `ui-styling` | Generic AI tasarımını önlemek ve Zanaat Tabanını (Craft Floor) korumak için zorunludur. |
| **Mimari Karar / 2+ Alternatif Seçimi:** "Hangi kütüphane?", "Zustand mı Context mi?", "Nasıl bir yapı kuralım?" ikilemleri | `karpathy-guidelines` (Council Deliberation §5) | Tek model önyargısını ve kullanıcıya yaranmayı (sycophancy) kırmak için Option A vs B körlemesi zorunludur. |
| **Hata / Bug Teşhisi:** Beklenmeyen çıktı, log hatası, console error, "çalışmıyor" durumu | `diagnosing-bugs` | Koda dokunmadan önce hatayı kanıtlayan kırmızı döngü (Red Loop) zorunludur. |
| **Yeni İş Mantığı / Servis / Endpoint:** Yeni fonksiyon, API veya iş kuralı ekleme | `tdd` + `musgoku` | Körlemesine kod yazımını önlemek için önce kırmızı test (Red-Green-Refactor) esastır. |
| **Refactoring & Sadeleştirme:** Kod karmaşıklığı, uzun fonksiyonlar, ortak kod değişiklikleri | `karpathy-guidelines` + `codebase-design` | Ön etki analizi (blast radius), derin modül ve cerrahi değişiklik disiplini zorunludur. |
| **Landing Page / Web / robots.txt:** Yeni web sayfası, SEO, sitemap, crawler politikaları | `seo-growth` (`seo_checker.py`) | Arama motoru ve AI bot görünürlüğü için standart denetim esastır. |
| **Güvenlik / Yetki / Token / Hassas Veri:** Auth, role, input sanitization, API anahtarı | `security-audit` | Güvenlik kalkanı ve yetki aşımı denetimi tavizsizdir. |
| **Görev Planlama / Mimari Parçalama / "Nasıl Yapılacak?":** Yeni özellik kurgusu, mimari fazlara bölme, sprint/dilim planı, "nasıl yapacaksın?", kabul kriterleri | `doc-coauthoring` + `musgoku` + `tdd` + `sprint-delivery-workflow` + `council` | Serbest metinli yüzeysel planları (ad-hoc planning slop) ve phantom done riskini önlemek; 5 katmanlı dikey dilim, TDD dikiş noktaları, mimari alternatif konseyi ve Gherkin kriterlerini zorunlu kılmak için esastır. |
| **Antigravity Plan Modu & Proceed İcrası:** "/plan", "plan modu", "proceed", "proceed with plan", "planı uygula", "planı onayla" | `tdd` + `sprint-delivery-workflow` + `musgoku` + `development-workflow` + `council` | IDE plan modunda TDD, KANBAN, 5 katmanlı dilim ve Council Deliberation (Option A vs B) körlemesinin bypass edilmesini önlemek; kırmızı test kanıtlanmadan doğrudan üretim koduna başlanmasını engellemek için zorunludur. |
| **Eksik Sayfa / Stub / 404 / Yetim Özellik & Çekirdek Modül Zenginleştirme:** "geliştirme aşamasındaki sayfaları tamamla", "placeholder/coming soon sayfalar", "menüde olup 404'e düşen rotalar", "backend'de olup arayüzde görünmeyen yetim özellikler", "dashboard/profil/ayarları zenginleştir" | `feature-architect` (+ onay sonrası `ui-polish`, `tdd`, `musgoku`) | Uydurma tespitleri önlemek için `gap_scanner.py` kanıtı, 3 kademeli alternatif, RBAC/veri hazırlığı ve onay kapısı zorunludur. |
| **Kılavuz, Kurulum, Talimat & Nasıl Yapılır Yanıtları:** "nasıl çalıştırırım?", "kurulum adımları", setup, user guide, how-to, runbook, test adımları | `rules/aviation-documentation-standard.md` (+ `doc-coauthoring`) | Bilişsel yükü sıfırlamak, laf kalabalığını önlemek, kronolojik eylem->çıktı netliği ve acil çıkış sorun giderme tablosunu garanti etmek için zorunludur. |
| **Yeni Paket / Dokümantasyon / API İsmi:** Harici kütüphane ekleme veya API kullanımı | `context7` MCP | Sürüm farkları ve doğru API parametrelerini doğrulamak için zorunludur. |
| **3+ Adımlı Plan / Belirsiz Mantık:** Karmaşık mimari akıl yürütme veya strateji | `sequential-thinking` MCP | Düşünce zincirinin dağılmasını önlemek için zorunludur. |

### 2. Manuel (Açık) Tetikleyiciler — Kullanıcı Kısayolları
Kullanıcının belirli bir isteği doğrudan ve kestirmeden ajana bildirmesini sağlayan konfor kısayollarıdır (`commitx`, `sadeleştir`, `council`, `smell tara`, `geo`, `palet öner`). Kullanıcı bu kelimeleri yazdığında niyet kesindir ve ara müzakereye gerek kalmadan ilgili operasyon icra edilir.

---

## Nasıl kullanılır

1. Kullanıcının isteğini ve etki alanını analiz et (otonom tetikleme matrisiyle eşle).
2. Kullanıcı açık bir anahtar kelime kullandıysa aşağıdaki tablodan eşleşen skill'i bul.
3. Bulamazsan §B kombinasyon tablosuna, o da olmazsa §C ayrım ağacına bak.
4. Skill dosyasını **okumadan kod yazma** — bkz. [`always-read-skills.md`](./always-read-skills.md).
5. Yanıtta hangi skill'in devrede olduğunu **açıkça belirt.**

---

## A. Pozitif tetikleyiciler — kelime → skill

### A1. Tasarım ve UI (en sık çakışan alan)

| Tetikleyici kelime (TR / EN) | Skill | Gövde yolu |
|---|---|---|
| tasarımını incele, tasarım gözden geçir, tasarım denetle / review design, design review, critique UI | `ui-ux-pro-max` + `frontend-design` | `skills/ui-ux-pro-max/SKILL.md` |
| tasarımı yenile, arayüzü tazele, modernleştir, amatör görünüyor, UI polish, tasarımı düzelt, ekranları toparla, güzelleştir, tasarımı profesyonelleştir / refresh design, modernize UI, looks generic, amateur design, ui polish, polish ui, fix design | `ui-ux-pro-max` + `frontend-design` | aynı |
| poster, afiş, kapak görseli, manifesto, .png, .pdf çıktı / poster, art, print piece | `canvas-design` | `skills/canvas-design/SKILL.md` |
| banner, kapak banner, reklam görseli, facebook cover, linkedin banner, og image, hero görseli / banner, ad creative, cover image | `banner-design` | `skills/banner-design/SKILL.md` |
| logo, logo brief, logo fikri / logo, logo brief, logotype | `design` | `skills/design/SKILL.md` |
| kartvizit, antetli kâğıt, kurumsal kimlik, CIP, kurumsal kimlik programı / business card, letterhead, corporate identity | `design` | aynı |
| sosyal medya görseli, instagram post görseli, çok platformlu görsel / social media image, multi-platform creative | `design` | aynı |
| renk paleti, hangi renk, font seçimi, tipografi seç / color palette, which colors, font pairing | `ui-ux-pro-max` + `theme-factory` | `skills/theme-factory/SKILL.md` |
| hazır tema, tema uygula, 10 tema / apply theme, preset theme | `theme-factory` | aynı |
| design token, primitive, semantic token, component token, css değişkeni üret / design tokens, token architecture | `design-system` | `skills/design-system/SKILL.md` |
| tailwind, shadcn, dark mode, responsive düzen, erişilebilir bileşen / tailwind config, shadcn component, accessible dialog | `ui-styling` | `skills/ui-styling/SKILL.md` |
| ux kuralı, erişilebilirlik denetimi, kontrast, klavye gezinme / ux guideline, accessibility audit, contrast ratio | `ui-ux-pro-max` | `skills/ui-ux-pro-max/SKILL.md` |
| grafik tipi, chart seçimi, dashboard yerleşimi / chart type, which graph, dashboard layout | `ui-ux-pro-max` | aynı |
| mock görsel, gerçekçi resim, kart görseli, profil resmi, etkinlik görseli, avatar ekle / mock images, placeholder images, realistic avatars, test data visuals | `mock-asset-provider` | `skills/mock-asset-provider/SKILL.md` |
| tur hazırla, tour hazırla, desing tour, ürün turu, onboarding turu, adım adım rehber, ipucu balonu / onboarding tour, product tour, guided tour, walkthrough, coachmarks | `onboarding-tour` | `skills/onboarding-tour/SKILL.md` |
| /ui-polish --skeleton, skeleton ekle, iskelet ekran entegre et, kaset yapısıyla skeleton, skeleton screen / add skeleton, skeleton loading, wireframe skeleton, ui-polish skeleton | `ui-polish` + `ui-styling` | `skills/ui-polish/SKILL.md` §2.1 |
| /ui-polish --<theme-name>, tema kilitle, sliding-hero, sliding-hero-auth-switcher-login, pinned theme | `ui-polish` + `frontend-design` | `skills/ui-polish/SKILL.md` §0.1 |
| gsap, gsap ekle, scrollsmoother, smooth scroll, autoscroll, otoskrol, pürüzsüz kaydırma / gsap, scrollsmoother, smooth scroll, autoscroll, smooth momentum | `ui-ux-pro-max` + `frontend-design` | `skills/ui-ux-pro-max/scripts/gsap_init.py` + `references/gsap-integration-guide.md` |
| diyagram, mimari şema, şema çiz, akış diyagramı, c4 şeması, er şeması, sequence diyagramı, wardley map, sankey / diagram, architecture diagram, sequence diagram, er diagram, flowchart, wardley | `diagram-design` | `skills/diagram-design/SKILL.md` |

### A2. Marka, sunum, doküman

| Tetikleyici kelime (TR / EN) | Skill | Gövde yolu |
|---|---|---|
| marka, marka tonu, görsel kimlik, kurumsal dil, marka kılavuzu / brand voice, visual identity, brand guidelines, style guide | `brand` | `skills/brand/SKILL.md` |
| marka dokümanı yaz / write brand doc | `brand` + `doc-coauthoring` | — |
| sunum, deck, pitch deck, slayt / presentation, deck, slide, keynote | `slides` (içerik) + `design-system` (üretim) | `skills/slides/SKILL.md` |
| sunum html'e dönüşsün, chart.js, slayt üret / render deck, generate slides | `design-system` | `skills/design-system/SKILL.md` |
| doküman yaz, proposal, spec, PRD, karar dokümanı, RFC / write doc, technical spec, write prd, decision doc | `doc-coauthoring` | `skills/doc-coauthoring/SKILL.md` |
| kullanım kılavuzu, user manual, nasıl yapılır, how-to, setup rehberi, aviation standard, safety card, runbook, talimat yaz / user manual, how-to guide, setup instructions, safety card standard, runbook | `rules/aviation-documentation-standard.md` | `rules/aviation-documentation-standard.md` |
| seo, teknik seo, geo, yapay zeka araması, ai search, eeat, topic cluster, hreflang, meta tag, sitemap, robots.txt, schema markup, arama motoru optimizasyonu, gtm stratejisi, ürün lansmanı, büyüme pazarlaması, dönüşüm optimizasyonu / seo optimization, technical seo, geo, ai search, eeat, topic cluster, meta description, schema markup, gtm strategy, product launch, growth marketing, cro, copywriting framework | seo-growth | skills/seo-growth/SKILL.md |

### A3. Kod ve mimari

| Tetikleyici kelime (TR / EN) | Skill | Gövde yolu |
|---|---|---|
| endpoint, controller, servis, entity, repository, dto, modül ekle, API yaz / add endpoint, create service, new entity | `musgoku` | `skills/musgoku/SKILL.md` |
| pagination, sayfalama, cursor, arama / add pagination, keyset, cursor page | `musgoku` → `references/pagination-search.md` | aynı |
| WebSocket, gerçek zamanlı, canlı veri / websocket, realtime | `musgoku` → `references/websocket.md` | aynı |
| güvenlik, yetki, jwt, auth, loglama / security, authorization, audit log | `musgoku` → `references/security-logging.md` | aynı |
| refactoring, hata düzelt, clean code, sadeleştir / refactor, fix bug, simplify | `musgoku` + `karpathy-guidelines` | `skills/karpathy-guidelines/SKILL.md` |
| react bileşen, component oluştur, props, state / react component, create component | `musgoku` → `skills/musgoku-react-component.md` | — |
| react performans, re-render, waterfall engelleme, compound component, react kodlama / react best practices, react performance, eliminate waterfalls, composition patterns | `react-best-practices` | `skills/react-best-practices/SKILL.md` |
| form, validasyon, zod, şema / form, validation, zod schema | `musgoku` → `skills/musgoku-forms-validation.md` | — |
| route, korumalı sayfa, yetkilendirme, guard / route, protected page, guard | `musgoku` → `skills/musgoku-routing-auth.md` | — |
| veri çekme, cache, liste tazeleme, query / fetch data, caching, invalidate | `musgoku` → `skills/musgoku-api-data-layer.md` | — |
| typescript hatası, tip kalitesi, any, strict / ts error, type quality | `musgoku` → `skills/musgoku-typescript-quality.md` | — |
| bundle, chunk, tree-shaking, build büyüklüğü / bundle size, chunk limit | `rules/frontend-bundle-limits.md` | — |
| i18n, çeviri, çok dil, locale, rtl / translate, multi-language, rtl | `i18n-localization` | `skills/i18n-localization/SKILL.md` |
| hardcoded metin, çeviri eksik, untranslated string / hardcoded string | `i18n-localization` + `rules/i18n-enforcement.md` | - |
| dil değiştir, İngilizceye geçince Türkçe kalıyor, çeviri görünmüyor, eksik anahtar / missing translation key, locale switch | `i18n-localization` + `rules/i18n-enforcement.md` | - |
| IDE arayüzü, kod editörü, terminal paneli, komut paleti, split pane / ide-like ui, code editor, command palette | `web-ide-ux-architect` | `skills/web-ide-ux-architect/SKILL.md` |
| tdd, test güdümlü, önce test yaz, kırmızı yeşil döngüsü, dikey dilim / test driven development, red green refactor, vertical slice | `tdd` | `skills/tdd/SKILL.md` |
| kod mimarisi, modül tasarımı, derin modül, dikiş noktası, seam, silme testi / codebase design, deep modules, module design, architectural seam | `codebase-design` | `skills/codebase-design/SKILL.md` |
| domain model, terimler sözlüğü, glossary, adr hazırla, iş kavramı, ubiquitous language / domain modeling, ubiquitous language, glossary sync, adr decision | `domain-modeling` | `skills/domain-modeling/SKILL.md` |

### A4. Teslim ve kalite

| Tetikleyici kelime (TR / EN) | Skill | Gövde yolu |
|---|---|---|
| hata ayıkla, bug çöz, neden çalışmıyor, kök neden, log incele / diagnose bug, debug issue, root cause, reproduce bug | `diagnosing-bugs` | `skills/diagnosing-bugs/SKILL.md` |
| kod inceleme, code review, smell tara, standart denetimi, şartname kontrolü / code review, review code, smell audit, standards review, spec review | `code-review` | `skills/code-review/SKILL.md` |
| commit, sürüm yayınla, release, tag, gönder, push, commitx, commitle / commit, tag, release, publish, commitx | `git-release-workflow` | `skills/git-release-workflow/SKILL.md` |
| docker, prod imajı, docker compose, deploy, konteyner / production image, containerize | `production-docker-architect` | `skills/production-docker-architect/SKILL.md` |
| api dokümantasyonu, swagger güncel mi / api docs, openapi | `rules/api-documentation-enforcement.md` | — |
| veritabanı revizyonu, migration, yeni tablo, yeni kolon, db şeması / db migration, schema change, add column, new table | `rules/db-migration-enforcement.md` + `musgoku` | — |
| oturum devri, handoff, nerede kaldık / session handoff, where we left off | `rules/handoff-session-continuity.md` | — |
| overcomplication, gereksiz karmaşıklık, varsayımı belirt, llm council, akran incelemesi, hakemlik, caveman, kısa konuş, token tasarrufu, nesir sıkıştırma / overengineering, simplify, surface assumptions, llm council, peer review, council deliberation, caveman, prose compression, token efficient | `karpathy-guidelines` | `skills/karpathy-guidelines/SKILL.md` |
| tasarım becerisi, daha iyi yaz, amatör mü / better code, improve quality | `karpathy-guidelines` + tasarım üçlüsü | — |
| gözlem kaydet, skill geliştir, süreç analizi, yeni skill öner / log observation, improve skill, observe task | `task-observer` | `skills/task-observer/SKILL.md` |
| fikirlerime bak, fikirlerimi incele, fikir havuzu, yeni fikir seç, ne yapabiliriz, myidea, my idea / review ideas, idea backlog, brainstorm ideas | `my-idea` | `skills/my-idea/SKILL.md` |
| güvenlik denetimi, security audit, güvenlik açığı tara, vulnerability scan, pen test, sızma testi, güvenlik incelemesi, yetki aşımı kontrolü / security audit, vulnerability scan, pen test, security review, audit security, exploit check | `security-audit` | `skills/security-audit/SKILL.md` |
| /goku-skills-update, /gs-update, Goku skill güncelle, skill update, GS update, GS güncelle, goku update, skillset güncelle, skill'leri güncelle, goku skills update, ajan yeteneklerini güncelle / update skills, goku update, update skill set, upgrade skills, sync skills | `musgoku` | `skills/musgoku/SKILL.md` |
| prelaunch, canlıya al, go live, yayına alma kontrolü, consent check, axe audit, /prelaunch, /prelaunch-update / prelaunch audit, go live checklist, prelaunch checklist | `prelaunch-audit` | `skills/prelaunch-audit/SKILL.md` |
| projenin kapsamlı özetini çıkar, proje özeti çıkar, proje özeti, /project-summary, /proje-ozeti, project summary, summarize project / project summary, summarize project | `project-summary` | `skills/project-summary/SKILL.md` |
| /feature-architect, [FEATURE-ARCHITECT], feature architect, --mode=council, --mode=complete, --engine=multi, ürün konseyi, 6 uzman ile incele, eksik sayfaları tamamla, projedeki eksikleri bul, stub sayfaları tamamla, placeholder sayfaları geliştir, geliştirme aşamasındaki sayfaları tamamla, 404 rotalarını düzelt, yetim özellikleri bağla, dashboard zenginleştir, profil ve ayarları zenginleştir / complete features, product council, six-hat council, find missing pages, fix stub pages, orphan features, enrich dashboard | `feature-architect` | `skills/feature-architect/SKILL.md` |
| /deploy-plan, deployment planı, vps kurulumu, prod config hazırla, rollback planı, hibrit dağıtım, deploy plan / deployment plan, deploy architect, vps setup, rollback playbook, hybrid deployment | `deployment-architect` | `skills/deployment-architect/SKILL.md` |
| /spec-reconcile, [SPEC-RECONCILE], spec reconcile, api dokümanlarını güncelle, rfc güncelle, şartname çelişkisi, spec reconcile, api drift / sync api docs, reconcile specs, api drift | `spec-reconciler` | `skills/spec-reconciler/SKILL.md` |

### A5. Bağlayıcı Oturum Slash Komutları ve Prompt Makroları (Ensemble Slash Commands)

Yapay zeka asistanlarının tekil ve birbirinden kopuk araçlar çalıştırmasını engellemek; **birbirini zorunlu kılan becerileri tek bir oturum komutunda zincirlemek** ve geliştiricinin tek kelimeyle tam teşekküllü kalite protokollerini başlatmasını sağlamak için tasarlanmıştır:

| Slash Komut / Makro | Bağlanan Beceriler (Ensemble) | Yürütülen Bağlayıcı Protokol & Kanıt | Gövde yolu |
|---|---|---|---|
| **Antigravity Plan Modu & Proceed İcrası:** "/plan", "plan modu", "proceed", "proceed with plan", "planı uygula", "planı onayla" | `tdd` + `sprint-delivery-workflow` + `musgoku` + `development-workflow` + `council` | IDE plan modunda TDD, KANBAN, 5 katmanlı dilim ve Council Deliberation (Option A vs B) körlemesinin bypass edilmesini önlemek; kırmızı test kanıtlanmadan doğrudan üretim koduna başlanmasını engellemek için zorunludur. |
| **`/verify-prd`** / `/prd-verify` / `[VERIFY-PRD]` | `doc-coauthoring` + `code-review` + Katman Bütünlüğü (5-Layer Vertical Slice) | **Tüm Proje & PRD Retrospektif Güven Motoru:** Şartnamedeki kabul kriterlerini (Gherkin AC), geçmişten bugüne tüm özelliklerin 5 Katmanlı Dikey Dilimini (DB migration, View/RPC, Client API, UI UX, Admin Formu), Sahte Bitti (Phantom Done) ve mock kalıntılarını tarar. | `skills/verify-prd/SKILL.md` |

| **`/verify-sprint`** / `[VERIFY-SPRINT]` | `sprint-delivery-workflow` + `tdd` + `sprint_auditor.py` + Katman Bütünlüğü | **Sprint Kapanış Kilidi, Otonom Doğrulama & Cerrahi Onarım Motoru:** Sprintteki son kart tamamlandığında veya talep edildiğinde otonom tetiklenir; Gherkin kabul kriterlerini (`specs/*.feature`), 5 katmanlı dikey dilimi ve kullanıcı test adımlarını tarar. Bulgu varsa kartları geri çeker, otonom cerrahi onarım (`tdd`/`fix-bug`) yapar ve kalıcı Audit Trail işler. | `skills/verify-sprint/SKILL.md` |

| **`/verify-last`** / `[VERIFY-LAST]` | `musgoku` + `development-workflow` + Kapsam-Duyarlı Kapılar | **Son Geliştirmeler Cerrahi Doğrulama Motoru:** Anlık çalışma ağacındaki uncommitted değişiklikleri veya son commit'i (`HEAD~1..HEAD`) derleme, tip, etkilenen katmanlar ve kullanıcı gözle testiyle hızla doğrular. | `skills/verify-last/SKILL.md` |
| **`/ui-polish`** / **`/ui-polish --skeleton`** / `[UI-POLISH]` / `[DESIGN-REFRESH]` | `ui-polish` (Master Orchestrator) + 16 UI/UX Becerisi (`canvas-design`, `frontend-design`, `ui-ux-pro-max`, `design-system`, `ui-styling`, `brand`, `banner-design`, `mock-asset-provider`, `onboarding-tour` vb.) | **Master Design & 16-Theme Orkestratörü:** 16 kilitli temayı (`themes.css`), geometry-matched skeleton shimmer motorunu ve standart `rehber_design.md` sözleşmesini hayata geçirir; 55 hazır bileşen temasını koordine eder, 6 satırlık Ön Uçuş Makbuzu basar, 375px mobil dönüşümü ve 10-noktalı canlı fix loop'u işletir. | `skills/ui-polish/SKILL.md` |
| **`/check-security`** | `security-audit` + `development-workflow` (Halka 2 Kalkanı) + `prelaunch-audit` | **Güvenlik & İstismar Savunması:** OWASP zafiyet avcılığı, public form kalkanı (Turnstile, Rate-limit, RLS) ve secrets/env sızıntı denetimi. | `skills/check-security/SKILL.md` |
| **`/fix-bug`** | `diagnosing-bugs` → `musgoku` → `karpathy-guidelines` | **Kırmızı Döngü & Hata Teşhisi:** Kod yazmadan önce hatayı kanıtlayan kırmızı test/kanıt döngüsü kurar, cerrahi onarım yapar, Karpathy gereksiz kod ve yan etki temizliği işletir. | `skills/fix-bug/SKILL.md` |
| **`/council`** | `karpathy-guidelines` (Council) → `doc-coauthoring` (ADR) | **3 Aşamalı Konsey Hakemliği:** Mimari ikilem ve riskli refactoring kararlarında 3 aşamalı anonim körleme (Blind Review & Chairman Synthesis) ve ADR mimari karar kaydı üretir. | `skills/council/SKILL.md` |
| **`/prelaunch`** | `prelaunch-audit` (Orkestratör) + 4 Referans Modülü | **Canlıya Alma Kalite Denetimi:** 20 maddelik tam kontrol listesi (KVKK m.10, Consent Mode v2, ham HTML SEO, WCAG 2.2 AA, robots, sitemap) ve GO/NO-GO karar raporu üretir. | `skills/prelaunch/SKILL.md` |
| **`/prelaunch-update`** | `prelaunch-audit` (`scripts/prelaunch_updater.py`) | **Mevzuat & Platform Güncellemesi:** İdari para cezaları, KVKK bildirim limitleri ve Google Search kurallarını resmi kaynaklardan sorgulayıp cerrahi günceller. | `skills/prelaunch/SKILL.md` |
| **`/seo-apply`** / `[SEO-APPLY]` | `seo-growth` → `frontend-design` + `seo_checker.py` | **Uçtan Uca SEO & GEO Uygulama:** Kod tabanına bizzat girer; semantik meta başlık/açıklama, canonical, OpenGraph, JSON-LD Schema.org, AI crawler `robots.txt`, `sitemap.xml` ve `/llms.txt` dosyalarını üretip `seo_checker.py` ile doğrular. | `skills/seo-apply/SKILL.md` |
| **`/commitx`** / `commitle` / `[COMMITX]` | `git-release-workflow` | **Peşin Tam Yetkili Sürüm Yayını:** Doğrulama kapılarını çalıştırır; ara onay sormadan `git add` → `git commit` → `git tag` → `git push` zincirini tek nefeste tamamlar. | `skills/commitx/SKILL.md` |
| **`/goku-skills-update`** / **`/gs-update`** / `"GS güncelle"` | `gs-update` (`musgoku`) | **Sıfır-Şişkinlik Skill Senkronu:** Kullanıcıya workspace veya global kapsamını sorarak proje kuralını korur ve kurulu olmayan becerileri indirmeden cerrahi güncelleme yapar. | `skills/gs-update/SKILL.md` |
| **`/project-summary`** / `/proje-ozeti` / `"projenin kapsamlı özetini çıkar"` | `project-summary` (`doc-coauthoring` + `domain-modeling` + `codebase-design`) | **Proje Konsolide Özeti & PRD Sentez Motoru:** Projenin kısa (`short`) veya kapsamlı (`long`) özetini çıkarır. Long modunda projedeki tüm PRD ve referans dokümanlarını tek bir `docs/<SLUG>_PROJECT_SUMMARY_LONG.md` dosyasında konsolide eder; dil uyumu, versiyonlama damgası ve `PROJECT_BRIEF.md` senkronizasyonunu zorunlu kılar. | `skills/project-summary/SKILL.md` |
| **`/feature-architect`** / `[FEATURE-ARCHITECT]` | `feature-architect` (`gap_scanner.py` + `engine_advisor.py` + `council_merger.py` + 6 Şapka) → `frontend-design` (`dashboard-theme/catalog.json`) → `ui-polish` → `tdd` + `musgoku` | **Global Otonom Ürün Denetçisi, 6 Şapkalı Strateji Konseyi ve Tamamlayıcısı:** Çalıştığı projedeki stub/placeholder sayfaları, ölü kontrolleri, 404 rotalarını, yetim backend uç nokta/alanlarını ve zayıf Dashboard/Profil/Ayarlar ekranlarını `gap_scanner.py` kanıtıyla tarar; `engine_advisor.py` ile proje ölçeğine göre tek veya alt ajanlı 6 uzman konseyini (`PO`, `ARCH`, `UX`, `SEO`, `GRW`, `QA`) çalıştırır, `council_merger.py` Zero-Drop kapısıyla RICE öncelikli konsolide rapor sunar ve onay sonrası 5 katmanlı TDD + `/ui-polish` ile inşa eder. | `skills/feature-architect/SKILL.md` |
| **`/deploy-plan`** / `[DEPLOY-PLAN]` | `deployment-architect` (`deployment_generator.py`) + `production-docker-architect` + `prelaunch` | **Üretim Dağıtım & Altyapı Orkestratörü:** Proje yığınını ve hedef ortamı (VPS, PaaS, Cloud Container, Hibrit) analiz eder; 5 katmanlı DEPLOYMENT_PLAN.md, .env.production.template, ters proxy, pre-deploy migration hook ve acil durum rollback playbook üretir. | `skills/deployment-architect/SKILL.md` |
| **`/spec-reconcile`** / `[SPEC-RECONCILE]` / `"api dokümanlarını güncelle"` | `spec-reconciler` (`reconcile_scanner.py`) + `doc-coauthoring` + `verify-prd` | **Global Çapraz Kod & Şartname Eşitleme Motoru:** Backend ve frontend kod tabanlarını çapraz tarar; `docs/APIs/` ve RFC belgelerini güncel kod gerçekliğine göre eşitler, PRD çelişkilerinde kullanıcıya seçenek ve comment alanı açan interaktif uzlaşma planı (Artifact) sunar. | `skills/spec-reconciler/SKILL.md` |

---

## B. Kombinasyon senaryoları — tek kelime yetmez

| İstek tipi | Birlikte açılacak skill'ler | Sıra |
|---|---|---|
| "Bu sayfayı güzelleştir" | `ui-ux-pro-max` → `frontend-design` → (Tailwind ise) `ui-styling` | 1) yön bul 2) estetik 3) uygula |
| "Yeni dashboard yap" | `ui-ux-pro-max` → `design-system` → `frontend-design` → `ui-styling` | palet → token → estetik → kod |
| "Marka sitesi kur" | `brand` → `design-system` → `frontend-design` → `ui-styling` | kimlik → token → estetik → kod |
| "Pitch deck hazırla" | `slides` → `design-system` → (palet için) `theme-factory` | içerik → üretim → renk |
| "Kampanya görselleri" | `design` → `banner-design` → `brand` | brief → görsel → marka kontrolü |
| "Ürün lansmanı ve SEO planı" | `seo-growth` → `brand` → `doc-coauthoring` | SEO & GTM stratejisi → marka dili → spec |
| "Yeni özellik planla" | `doc-coauthoring` → `musgoku` | kapsam → mimari |
| "Hata düzelt ve temizle" | `musgoku` → `karpathy-guidelines` | çözüm → sadeleştirme denetimi |
| "Mimari tercih ve alternatif seçimi" | `karpathy-guidelines` → `doc-coauthoring` | 3 aşamalı konsey körlemesi (council) → ADR karar kaydı |
| "Yayına al" | `production-docker-architect` → `git-release-workflow` | imaj → commit/tag/push |
| "Fikir havuzundan iş seç" | `my-idea` → `doc-coauthoring` → `sprint-delivery-workflow` → `tdd` → `musgoku` | re-rating & seçim → spec → sprint kartı → test → kodlama |
| "Eksik/stub sayfaları bul ve tamamla" | `feature-architect` → `tdd` → `musgoku` → `ui-polish` | 6-sektör tarama → onay → kırmızı test → 5 katmanlı inşa & 18 dashboard-theme / 55 component-theme parlatma |
| "Genel kod talebi" | `musgoku` (yönlendirici) → ilgili alt tablo | — |

---

## C. Ayrım karar ağacı — belirsiz durumlar

Bunlar en sık yanlış yönlendirilen durumlardır. Karar kuralı **sahiplik
haritasından** gelir ([`design-skills-enforcement.md`](./design-skills-enforcement.md) §3).

| Belirsizlik | Karar |
|---|---|
| "Doğrula / Test et / Bitti mi" — hangi seviye? | Anlık son değişiklik / uncommitted ➔ `/verify-last` · Aktif/son sprint ➔ `/verify-sprint` · Tüm proje / PRD kabulü ➔ `/verify-prd` |
| "Eksik mi, bitti mi, ham fikir mi?" | Kodda/menüde stub, 404, yetim API veya zayıf Dashboard/Profil/Ayarlar (prospektif) ➔ `/feature-architect` · Tamamlandı denen işlerin 5 katman denetimi (retrospektif) ➔ `/verify-prd` · `docs/idea/myidea.md` fikir havuzu ➔ `my-idea` |

| "Tasarım yap" — ne tür? | Sabit px ölçü varsa `banner-design` · `.png/.pdf` çıktı varsa `canvas-design` · web arayüzü ise `frontend-design` + `ui-ux-pro-max` |
| "Poster" mi "banner" mı? | Ölçüsüz sanat → `canvas-design`. Platform ölçüsü (1080×1080, 820×312) → `banner-design` |
| "Palet" mi "token" mı? | Hazır tema seçimi → `theme-factory`. Ürüne özel palet → `ui-ux-pro-max`. Üç katmanlı token → `design-system` |
| "Tailwind" mi "shadcn" mi? | Token üretimi `design-system`'de. Tailwind/shadcn **kod tarafı** `ui-styling`'de. Prensip `musgoku-styling-ui.md`'de |
| "Sunum" mu "belge" mi? | HTML deck → `slides` + `design-system`. Markdown doküman → `doc-coauthoring` |
| "Marka dokümanı" | İçerik → `brand`. Yazma süreci → `doc-coauthoring` |
| "SEO & Growth" mu "Brand" mi? | Arama motoru, meta, schema, indexing, GTM, lansman kanalları, CRO → `seo-growth`. Marka tonu, visual identity, logo, kurumsal kimlik → `brand`. |
| "SEO & Growth" mu "Doc-coauthoring" mi? | SEO mimarisi, anahtar kelime, dağıtım kanalı, landing page metin formülü → `seo-growth`. PRD, RFC, teknik spec yazım süreci → `doc-coauthoring`. |
| "Logo çiz" | Brief → `design`. Görsel üretimi bu setin **kapsamı dışında** (ücretli API çağrılmaz) |
| "Mock görsel / resim" mi "Banner" mı? | Arayüz kartı/içerik için gerçekçi fotoğraf/avatar → `mock-asset-provider`. Sabit ölçülü reklam/kapak → `banner-design` |
| "Güvenlik incelemesi" mi "Kod inceleme (code-review)" mi? | Kod kokuları (smell) ve PRD şartname uygunluğu → `code-review`. Güvenlik zafiyetleri, yetki aşımı, sızma testi, boundary violation, token/injection açıkları → `security-audit`. |
| "Ürün turu / onboarding" mi "UI tasarımı" mı? | Adım adım spotlight, rehberli tur ve ipucu balonu → `onboarding-tour`. Sayfa, form ve bileşenin kendi yerleşimi → `frontend-design` + `ui-styling` |
| Tasarım skill'i mi, kod skill'i mi? | Görsel karar varsa tasarım seti. Veri akışı/mimari varsa `musgoku`. İkisi de varsa **ikisi** |

---

## D. Tetiklenmeme kuralları

| Durum | Davranış |
|---|---|
| Tek satır düzeltme, dosya adı, yorum | Hiçbir skill açma. Yanıtta bunu **açıkça belirt** ([`always-read-skills.md`](./always-read-skills.md) §İstisna) |
| Salt bilgi sorusu ("JWT nedir") | Kod yazılmıyorsa skill açma |
| İstemci olmayan ortam (cron, CI, batch) | Soru sorulamaz; sessiz varsayım yalnız dokümanda Varsayım Kaydı'nda |
| Kullanıcı skill'i **reddettiyse** | Yerine geçme. Gerekçeni yaz, alternatif öner |

---

## D.1. Doğrulama Sonrası Bulgu Triyaj ve Onarım Yönlendirme Matrisi (Post-Verification Remediation Matrix)

Doğrulama yetenekleri (`/verify-prd`, `/verify-sprint`, `/verify-last`) bir eksiklik, kırık kapı veya mimari sapma tespit ettiğinde bulguları pasif metin olarak bırakmaz; aşağıdaki matrise göre deterministik şekilde sınıflandırır ve ilgili onarım becerisine bağlar:

| Bulgu Türü (Finding Type) | Tespit Eden Seviye | Öncelik | İlgili Onarım Becerisi | Yürütülecek Cerrahi Protokol & Kural |
|---|---|---|---|---|
| **Sahte Bitti (Phantom Done) & Mock Kalıntıları:** Hardcoded dummy array'ler, bağlanmamış API mock'ları, ölü butonlar | `/verify-prd`, `/verify-sprint` | 🔴 Blocker (P0) | [`fix-bug`](../skills/fix-bug/SKILL.md) | Önce kırmızı test döngüsü kur, sahte mock'u sil, gerçek API/RPC bağlantısını sağla (`bug-diagnosis-enforcement.md`). |
| **Eksik Katman (Vertical Slice Gap):** View/RPC, İstemci hook veya Admin Giriş Formu yokluğu | `/verify-prd`, `/verify-sprint` | 🔴 Blocker / Major (P1) | [`tdd`](../skills/tdd/SKILL.md) + [`musgoku`](../skills/musgoku/SKILL.md) | Dikiş noktasında (`seam`) kırmızı test yaz, eksik katmanı minimal kodla inşa et (Full-stack 5 katman dilimi). |
| **Veritabanı & Şema Eksikliği:** Eksik migration, tablo, kolon, indeks veya açık RLS politikası | `/verify-prd`, `/verify-sprint`, `/verify-last` | 🔴 Blocker (P0) | [`db-migration-enforcement`](./db-migration-enforcement.md) + [`musgoku`](../skills/musgoku/SKILL.md) | Yeni migration (`*.sql`) yaz, `DB_MIGRATIONS.md` ve `PROJECT_BRIEF.md` ikili eşlemesini eşzamanlı güncelle. |
| **Arayüz Kalitesi & Skeleton Yokluğu:** Skeleton screens wireframe eksikliği, WCAG kontrast veya AI-slop | `/verify-prd`, `/verify-last` | 🟡 Major (P1) | [`ui-polish`](../skills/ui-polish/SKILL.md) + [`frontend-design`](../skills/frontend-design/SKILL.md) | Gri tonlu Skeleton screens kaset yapısını ekle, `DESIGN.md` sözleşmesi ve WCAG 2.2 AA kontrastını sağla. |
| **Doküman-Kod Sapması (Spec Drift):** Halüsinasyonlu veya kodla çelişen dokümantasyon kartları | `/verify-prd` | 🟡 Major / Minor (P2) | [`doc-coauthoring`](../skills/doc-coauthoring/SKILL.md) | `PRODUCT.md` / `docs/*-prd.md` ve `docs/kullanici-rehberi.html` dosyalarını gerçek kod tabanıyla senkronize et. |
| **Yetim Responsive Bileşenler:** Mount edilmemiş mobil/tablet barları veya dead code | `/verify-prd` | 🟡 Major (P1) | [`ui-styling`](../skills/ui-styling/SKILL.md) + [`frontend-design`](../skills/frontend-design/SKILL.md) | Yetim bileşenleri ana ekrana mount et veya gereksizse temizle, 3 Cihaz Ergonomisini sağla. |
| **Eksik Kullanıcı Test Senaryoları:** Gözle doğrulama adımı bulunmayan özellikler | `/verify-prd`, `/verify-sprint`, `/verify-last` | 🟡 Major (P1) | [`development-workflow`](./development-workflow.md) | `docs/KULLANICI_TEST_REHBERI.md` dosyasına adım adım gözle test akışlarını ekle. |
| **Kalite Kapısı Hatası:** `run_all_gates.py`, derleme (`build`), tip (`tsc`), lint veya kural kapısı | `/verify-last` | 🔴 Blocker (P0) | [`fix-bug`](../skills/fix-bug/SKILL.md) / `Auto-heal` | Belge senkron hatası ise Auto-heal ile tamamla; derleme/tip hatası ise cerrahi onar. |

---

## E. Sözleşme kuralları

Her `SKILL.md` `description` alanı şu kalıbı taşır:

```yaml
description: >
  <Ne yaptığı: 1 cümle.> Tetikleyiciler: "<TR örnek>", "<EN örnek>", ... .
  <Ne zaman TETİKLENMEZ: hangi skill'e devredilir.> Tam sözlük:
  .agent/rules/skill-trigger-routing.md
```

| Kural | Değer |
|---|---|
| Uzunluk | 25-70 kelime. 70'i aşan description seçim penceresini şişirir |
| Tetikleyici dili | Hem Türkçe hem İngilizce örnek cümle |
| Negatif tetikleyici | Her skill en az bir tane "bunun için X'e git" ifadesi |
| Araç adı / dosya yolu | `description` içinde **yok** (globallik ilkesi) |
| Atıf | Her description merkezi sözlüğe atıf yapar |

Bu sözleşme otomatik doğrulanır:
`skills/ui-ux-pro-max/scripts/tests/test_skill_contracts.py` →
`SkillDescriptionContract`.

---

## F. İnteraktif Skill & Mimari Kataloğu (`.agent/skills-catalog.html`)

Kullanıcının tüm skill'leri, sorumluluk sınırlarını, config gereksinimlerini ve tetikleyicilerini tarayıcıda görsel olarak inceleyebilmesi ve arayabilmesi için `.agent/skills-catalog.html` dosyası tutulur.

- **Konum:** Kesinlikle `.agent/skills-catalog.html` altında yaşar (proje kökünü kirletmez).
- **Zorunlu Güncelleme:** Her yeni skill, config veya mimari yapı eklendiğinde `python scripts/generate_skills_catalog.py` çalıştırılarak katalog güncellenmelidir.
- **Doğrulama Kapısı:** `tests/test_skills_catalog.py` ve `test_skill_contracts.py` kapıları kataloğun bayat kalmasını veya herhangi bir skill'in katalogdan eksik kalmasını engeller.

---

## G. Tasarım Fiilleri Yönlendirme Matrisi (24 Design Verbs)

Kullanıcının arayüz üzerindeki niyetini doğrudan eyleme dönüştüren 24 standart tasarım fiili ve yönlendirme kuralları:

| Fiil (Verb) | Kategori | Tetikleyiciler (TR / EN) | Sahip Skill & Eylem |
|---|---|---|---|
| `shape [hedef]` | Build | UX planla, kullanıcı akışı çıkar, ekranı kurgula / shape UX, plan UI flow | `frontend-design` + `ui-ux-pro-max` (kod öncesi UX kurgusu) |
| `document` | Build | tasarım sistemini belgele, DESIGN.md üret, token haritası çıkar / document design, extract DESIGN.md | `design-system` + `brand` (kod tabanından token/stil dokümanı üretir) |
| `extract [hedef]` | Build | token çıkar, bileşeni ayır, stilleri değişkene bağla / extract tokens, extract component | `design-system` + `ui-styling` (inline stilleri token'a dönüştürür) |
| `critique [hedef]` | Evaluate | tasarımı eleştir, tasarım incelemesi, UX critique / critique UI, review design | `ui-ux-pro-max` + `frontend-design` (Zanaat Tabanı + Yüzey Modu P0/P1/P2 analizi) |
| `audit [hedef]` | Evaluate | teknik denetim, erişilebilirlik testi, kontrast denetle / audit a11y, technical UI audit | `ui-ux-pro-max` + `musgoku` (`check_bundle_limits`, a11y) |
| `polish [hedef]` | Refine | son cila, arayüzü parlat, mikro ritim, UI polish / polish UI, final quality pass | `frontend-design` + `ui-styling` (boşluk, hizalama, mikro zanaat) |
| `bolder [hedef]` | Refine | daha cesur yap, güçlendir, sönük kalmış / make bolder, amplify design | `frontend-design` (mevcut marka dili içinde güçlendirme; yeni stil uydurmaz) |
| `quieter [hedef]` | Refine | sakinleştir, göz yoruyor, cırtlak, gürültüyü azalt / make quieter, tone down, reduce noise | `frontend-design` (doygunluğu düşürme, kontrastı yumuşatma, dinginleştirme) |
| `distill [hedef]` | Refine | sadeleştir, fazlalıkları at, özüne indir / distill design, strip complexity | `frontend-design` (süs ve dekoratif kutuları ayıklama, yalınlaştırma) |
| `harden [hedef]` | Refine | sağlamlaştır, uç durumları bağla, prod kalitesi / harden UI, handle edge cases | `frontend-design` + `ui-styling` (4 UX Durumu + klavye odağı + safe-area) |
| `onboard [hedef]` | Refine | tur ekle, ürün turu hazırla, ipucu balonu / onboard flow, product tour | `onboarding-tour` (Driver.js / Joyride rehberli tur ve coachmark) |
| `animate [hedef]` | Enhance | animasyon ekle, hareket kat, mikro etkileşim / animate UI, add motion | `frontend-design` + `ui-styling` (150-250ms hızlı mikro geçişler, exponential ease) |
| `colorize [hedef]` | Enhance | renklendir, renk kat, hiyerarşik renk / colorize UI, add strategic color | `theme-factory` + `ui-styling` (semantik durum ve vurgu renkleri) |
| `typeset [hedef]` | Enhance | tipografiyi düzelt, fontları ayarla, satır dengesi / typeset, improve typography | `frontend-design` + `ui-ux-pro-max` (65-75ch, text-wrap: balance, -0.02em tracking) |
| `layout [hedef]` | Enhance | yerleşimi düzelt, boşlukları ayarla, hizala / fix layout, adjust spacing rhythm | `frontend-design` (mt > mb ritmi, negatif alan, ızgara dengesi) |
| `delight [hedef]` | Enhance | zarafet kat, mikro detay ekle, tarayıcı yüzeyleri / add delight, polish details | `frontend-design` (`::selection`, `caret-color`, `tabular-nums`, mikro zanaat) |
| `overdrive [hedef]` | Enhance | sınırları zorla, deneysel yap, cesur kompozisyon / overdrive, push limits | `frontend-design` + `canvas-design` (deneysel ve sıra dışı görsel kompozisyon) |
| `clarify [hedef]` | Fix | metinleri netleştir, buton etiketlerini düzelt, hata mesajı / clarify copy, fix labels | `frontend-design` (eyleme dayalı net dil, anlaşılır hata ve rehberlik) |
| `adapt [hedef]` | Fix | responsive uyarla, mobilde düzelt, tablete uyarla / adapt responsive, fix mobile | `frontend-design` + `ui-styling` (3 Cihaz Ergonomisi + adaptif bottom sheet) |
| `optimize [hedef]` | Fix | performansı artır, render optimize et, layout shift / optimize UI, fix performance | `react-best-practices` + `ui-styling` (CLS, memoization, lazy loading) |
| `generate [n] [öğe]` | Iterate | varyasyon üret, 3 alternatif sun / generate variants, alternative styles | `frontend-design` + `theme-factory` (aynı öğe için 2-3 alternatif stil varyasyonu) |

---

## Proje Bazlı Ek Kurallar

> ⛔ **Kural Ekleme ve Mükerrerlik İlkesi:**
> 1. Yukarıdaki global kurallar projeler arası standarttır ve değiştirilmez.
> 2. Projeye özgü bir tetikleyici gerekiyorsa, önce yukarıdaki tablolarla
>    mükerrerlik denetimi yapılır.
> 3. Yeni tetikleyici yalnızca bu başlığın altına `### <Kural Başlığı>` olarak
>    eklenir — global tablolara değil.

### Bu Proje İçin Ek Kurallar
_(Henüz bu projeye özel ek bir tetikleyici tanımlanmamıştır.)_
