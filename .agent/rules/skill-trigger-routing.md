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

## Nasıl kullanılır

1. Kullanıcının isteğini **tek cümleye** indirge.
2. Aşağıdaki tablodan eşleşen skill'i bul.
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
| overcomplication, gereksiz karmaşıklık, kapsam kayması, varsayımı belirt / overengineering, scope creep, state assumptions | `karpathy-guidelines` | — |
| tasarım becerisi, daha iyi yaz, amatör mü / better code, improve quality | `karpathy-guidelines` + tasarım üçlüsü | — |
| gözlem kaydet, skill geliştir, süreç analizi, yeni skill öner / log observation, improve skill, observe task | `task-observer` | `skills/task-observer/SKILL.md` |

### A5. Prompt Makroları ve Kısayol Etiketleri (Prompt Shorthands)

Kullanıcının detaylı ve uzun prompt yazmadan doğrudan tam kapsamlı revizyon talep edebilmesi için tasarlanmış kısayollardır:

| Makro / Etiket | Açılan Skill'ler | Yürütülen Protokol |
|---|---|---|
| `[DESIGN-REFRESH]` / `[UI-POLISH]` | `frontend-design` + `ui-ux-pro-max` + `ui-styling` | Kullanıcı tek satırda revizyon ister. Ajan ek açıklama beklemeden; belirtilen sayfalarda generic AI-slop şablonlarını temizler, görsel hiyerarşi, boşluk ritmi, scanning ergonomisi ve rozet revizyonunu mevcut veri akışını bozmadan tamamlar. |
| `[DASHBOARD-POLISH]` | `ui-ux-pro-max` + `frontend-design` + `ui-styling` | Yönetim, onay ve metrik masalarının bilgi mimarisi, kart ve tablo ergonomisini profesyonel seviyeye çıkarır. |
| `commitx`, `commitle` / `[COMMITX]` | `git-release-workflow` | Peşin tam yetkili (express) sürüm yayını: commit ve push için ayrı ayrı ara onay sormadan `git add` → `git commit` → `git tag` → `git push` zincirini tek nefeste tamamlar ve doğrudan sonucu raporlar. |

---

## B. Kombinasyon senaryoları — tek kelime yetmez

| İstek tipi | Birlikte açılacak skill'ler | Sıra |
|---|---|---|
| "Bu sayfayı güzelleştir" | `ui-ux-pro-max` → `frontend-design` → (Tailwind ise) `ui-styling` | 1) yön bul 2) estetik 3) uygula |
| "Yeni dashboard yap" | `ui-ux-pro-max` → `design-system` → `frontend-design` → `ui-styling` | palet → token → estetik → kod |
| "Marka sitesi kur" | `brand` → `design-system` → `frontend-design` → `ui-styling` | kimlik → token → estetik → kod |
| "Pitch deck hazırla" | `slides` → `design-system` → (palet için) `theme-factory` | içerik → üretim → renk |
| "Kampanya görselleri" | `design` → `banner-design` → `brand` | brief → görsel → marka kontrolü |
| "Yeni özellik planla" | `doc-coauthoring` → `musgoku` | kapsam → mimari |
| "Hata düzelt ve temizle" | `musgoku` → `karpathy-guidelines` | çözüm → sadeleştirme denetimi |
| "Yayına al" | `production-docker-architect` → `git-release-workflow` | imaj → commit/tag/push |
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
| "Logo çiz" | Brief → `design`. Görsel üretimi bu setin **kapsamı dışında** (ücretli API çağrılmaz) |
| "Mock görsel / resim" mi "Banner" mı? | Arayüz kartı/içerik için gerçekçi fotoğraf/avatar → `mock-asset-provider`. Sabit ölçülü reklam/kapak → `banner-design` |
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
