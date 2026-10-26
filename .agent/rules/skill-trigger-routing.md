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

### A2. Marka, sunum, doküman

| Tetikleyici kelime (TR / EN) | Skill | Gövde yolu |
|---|---|---|
| marka, marka tonu, görsel kimlik, kurumsal dil, marka kılavuzu / brand voice, visual identity, brand guidelines, style guide | `brand` | `skills/brand/SKILL.md` |
| marka dokümanı yaz / write brand doc | `brand` + `doc-coauthoring` | — |
| sunum, deck, pitch deck, slayt / presentation, deck, slide, keynote | `slides` (içerik) + `design-system` (üretim) | `skills/slides/SKILL.md` |
| sunum html'e dönüşsün, chart.js, slayt üret / render deck, generate slides | `design-system` | `skills/design-system/SKILL.md` |
| doküman yaz, proposal, spec, PRD, karar dokümanı, RFC / write doc, technical spec, write prd, decision doc | `doc-coauthoring` | `skills/doc-coauthoring/SKILL.md` |
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
| overcomplication, gereksiz karmaşıklık, varsayımı belirt, llm council, akran incelemesi, hakemlik / overengineering, simplify, surface assumptions, llm council, peer review, council deliberation | `karpathy-guidelines` | `skills/karpathy-guidelines/SKILL.md` |
| tasarım becerisi, daha iyi yaz, amatör mü / better code, improve quality | `karpathy-guidelines` + tasarım üçlüsü | — |
| gözlem kaydet, skill geliştir, süreç analizi, yeni skill öner / log observation, improve skill, observe task | `task-observer` | `skills/task-observer/SKILL.md` |
| fikirlerime bak, fikirlerimi incele, fikir havuzu, yeni fikir seç, ne yapabiliriz, myidea, my idea / review ideas, idea backlog, brainstorm ideas | `my-idea` | `skills/my-idea/SKILL.md` |
| güvenlik denetimi, security audit, güvenlik açığı tara, vulnerability scan, pen test, sızma testi, güvenlik incelemesi, yetki aşımı kontrolü / security audit, vulnerability scan, pen test, security review, audit security, exploit check | `security-audit` | `skills/security-audit/SKILL.md` |
| Goku skill güncelle, skill update, GS update, GS güncelle, goku update, skillset güncelle, skill'leri güncelle, goku skills update, ajan yeteneklerini güncelle / update skills, goku update, update skill set, upgrade skills, sync skills | `musgoku` | `skills/musgoku/SKILL.md` |
| prelaunch, canlıya al, go live, yayına alma kontrolü, consent check, axe audit, /prelaunch, /prelaunch-update / prelaunch audit, go live checklist, prelaunch checklist | `prelaunch-audit` | `skills/prelaunch-audit/SKILL.md` |

### A5. Bağlayıcı Oturum Slash Komutları ve Prompt Makroları (Ensemble Slash Commands)

Yapay zeka asistanlarının tekil ve birbirinden kopuk araçlar çalıştırmasını engellemek; **birbirini zorunlu kılan becerileri tek bir oturum komutunda zincirlemek** ve geliştiricinin tek kelimeyle tam teşekküllü kalite protokollerini başlatmasını sağlamak için tasarlanmıştır:

| Slash Komut / Makro | Bağlanan Beceriler (Ensemble) | Yürütülen Bağlayıcı Protokol & Kanıt |
|---|---|---|
| **`/verify-prd`** | `doc-coauthoring` + `code-review` + Katman Bütünlüğü (5-Layer Vertical Slice) | **"Bitti ama doğru mu bitti?" Güven Motoru:** Şartnamedeki kabul kriterlerini (Gherkin AC), 5 Katmanlı Dikey Dilimi (DB migration, View/RPC, Client API, UI UX, Admin Formu) ve kapsam sapmalarını (Scope Creep) denetleyip kanıt tablosu üretir. |
| **`/ui-polish`** / `[UI-POLISH]` / `[DESIGN-REFRESH]` | `ui-ux-pro-max` → `frontend-design` → `ui-styling` + `check_design_slop.py` | **Tasarım & Zanaat Üçlüsü:** 79 stil ve 192 palet seçimi, generic AI-slop temizliği, tipografi hiyerarşisi, boşluk ritmi ve deterministik kontrast/WCAG doğrulaması. |
| **`/check-security`** | `security-audit` + `development-workflow` (Halka 2 Kalkanı) + `prelaunch-audit` | **Güvenlik & İstismar Savunması:** OWASP zafiyet avcılığı, public form kalkanı (Turnstile, Rate-limit, RLS) ve secrets/env sızıntı denetimi. |
| **`/fix-bug`** | `diagnosing-bugs` → `musgoku` → `karpathy-guidelines` | **Kırmızı Döngü & Hata Teşhisi:** Kod yazmadan önce hatayı kanıtlayan kırmızı test/kanıt döngüsü kurar, cerrahi onarım yapar, Karpathy gereksiz kod ve yan etki temizliği işletir. |
| **`/council`** | `karpathy-guidelines` (Council) → `doc-coauthoring` (ADR) | **3 Aşamalı Konsey Hakemliği:** Mimari ikilem ve riskli refactoring kararlarında 3 aşamalı anonim körleme (Blind Review & Chairman Synthesis) ve ADR mimari karar kaydı üretir. |
| **`/prelaunch`** | `prelaunch-audit` (Orkestratör) + 4 Referans Modülü | **Canlıya Alma Kalite Denetimi:** 20 maddelik tam kontrol listesi (KVKK m.10, Consent Mode v2, ham HTML SEO, WCAG 2.2 AA, robots, sitemap) ve GO/NO-GO karar raporu üretir. |
| **`/prelaunch-update`** | `prelaunch-audit` (`scripts/prelaunch_updater.py`) | **Mevzuat & Platform Güncellemesi:** İdari para cezaları, KVKK bildirim limitleri ve Google Search kurallarını resmi kaynaklardan sorgulayıp cerrahi günceller. |
| **`/seo-apply`** / `[SEO-APPLY]` | `seo-growth` → `frontend-design` + `seo_checker.py` | **Uçtan Uca SEO & GEO Uygulama:** Kod tabanına bizzat girer; semantik meta başlık/açıklama, canonical, OpenGraph, JSON-LD Schema.org, AI crawler `robots.txt`, `sitemap.xml` ve `/llms.txt` dosyalarını üretip `seo_checker.py` ile doğrular. |
| **`/commitx`** / `commitle` / `[COMMITX]` | `git-release-workflow` | **Peşin Tam Yetkili Sürüm Yayını:** Doğrulama kapılarını çalıştırır; ara onay sormadan `git add` → `git commit` → `git tag` → `git push` zincirini tek nefeste tamamlar. |
| **`/gs-update`** / `"GS güncelle"` | `musgoku` | **Sıfır-Şişkinlik Skill Senkronu:** Proje kuralını koruyarak ve gereksiz dosya indirmeden ajan becerilerini cerrahi olarak en son sürüme senkronlar. |

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
| "Genel kod talebi" | `musgoku` (yönlendirici) → ilgili alt tablo | — |

---

## C. Ayrım karar ağacı — belirsiz durumlar

Bunlar en sık yanlış yönlendirilen durumlardır. Karar kuralı **sahiplik
haritasından** gelir ([`design-skills-enforcement.md`](./design-skills-enforcement.md) §3).

| Belirsizlik | Karar |
|---|---|
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
