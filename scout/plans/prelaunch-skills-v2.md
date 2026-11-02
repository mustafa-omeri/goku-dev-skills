# 🔭 Scout Değerlendirme Raporu: devSearch/projects/prelaunch-skills-v2

## 1. Depo Özeti ve Künye
- **Kaynak / Yol:** `C:\devSearch\projects\prelaunch-skills-v2`
- **Sahibi:** Kullanıcı Proje Havuzu (Yerel Skill Seti)
- **Analiz Tarihi:** 2026-10-26
- **Entegrasyon Tarihi:** 2026-10-26
- **Tespit Edilen Katman:** Fullstack + Tooling / Agentic
- **İncelenen Bileşenler:** 4 Bağımsız Modül (`prelaunch-audit`, `prelaunch-legal-privacy`, `prelaunch-seo-discovery`, `prelaunch-structure-trust`)
- **Teknoloji Yığını:** Node.js (Playwright, AxeBuilder), Python CLI, Markdown

---

## 2. Çekirdek Felsefe ve Mimari (Kaynak İncelemesi)

Kullanıcının projeleri canlıya (production) alırken karşılaştığı yasal riskler, ceza yaptırımları, SEO kayıpları ve altyapı eksikliklerini sistematik 20 maddelik bir çekirdek denetim ve 7 koşullu madde ile çözmeyi hedeflemektedir:

1. **Yasal Uyum ve Gizlilik:**
   - 6698 sayılı KVKK m.10 Aydınlatma Yükümlülüğü, 7499 sayılı Kanun değişikliği ile yurt dışı aktarımı standart sözleşme 5 günlük bildirim kuralı.
   - Google Consent Mode v2 varsayılan `denied` durumu ve Playwright ağ/çerez izleme denetimi.
   - 6502 ve 6563 sayılı tüketici ve elektronik ticaret mevzuatı (opt-in onaylar).
2. **SEO ve Keşfedilebilirlik:**
   - JavaScript işletilmeden ham HTML doğrulama (meta title, description, canonical, single h1).
   - sitemap.xml standartları ve ISO 8601 lastmod.
   - robots.txt AI Crawler taksonomisi (GPTBot, ClaudeBot, Google-Extended, OAI-SearchBot, PerplexityBot).
   - Gerçek HTTP 404 durumu (soft-404 engeli), favicon setleri ve llms.txt.
3. **Erişilebilirlik ve Altyapı:**
   - WCAG 2.2 AA headless axe-core taraması.
   - Core Web Vitals (LCP, CLS, TBT) lab ve RUM hedefleri.
   - Form teslimat doğrulaması ve spam koruması (turnstile/honeypot).
4. **Yapı ve Yerel Güven:**
   - Google Search Console domain mülkiyeti ve sitemap gönderimi.
   - Post-Redirect-Get (PRG) ile teşekkür sayfası ve mükerrer dönüşüm engeli.
   - Ticaret Bakanlığı 28/B tüketici yorum ve şeffaflık kuralları.

---

## 3. Bizim Sistemle Kıyaslama (Delta Analizi)

- **Mevcut Durumumuz:**
  - `git-release-workflow`: Sürüm yayınlama, tag atma ve push adımlarını yönetir.
  - `seo-growth`: Teknik SEO, anahtar kelime ve içerik stratejisi sağlar.
  - `ui-ux-pro-max` & `frontend-design`: Arayüz tasarımı ve ergonomisini sağlar.
  - **Eksik Parça:** Canlıya alma (pre-launch / go-live) anında tek bir komutla hem yasal KVKK/çerez, hem axe WCAG, hem ham HTML SEO, hem de altyapı kontrollerini yapan kapsamlı bir denetim motoru yoktu.
- **Kullanıcı Kararı (Model B):**
  - 4 ayrı skill açıp ajanın bilişsel yükünü dağıtmak yerine, tek bir süper orkestratör `.agent/skills/prelaunch-audit/` kuruldu; modüller `references/` altında toplandı.
  - Kullanıcı yorumu doğrultusunda `/prelaunch` ve `/prelaunch-update` komutları eklendi.

---

## 4. Karar: ✅ TAMAMLANDI (INTEGRATED)
`devSearch/projects/prelaunch-skills-v2` içeriği, sistemimize `.agent/skills/prelaunch-audit/` (30. skill) olarak entegre edilmiş, `/prelaunch` ve `/prelaunch-update` yetenekleri kazandırılmıştır.

---

## 5. Gerçekleştirilen Entegrasyon Adımları

1. **Skill Tanımı ve Sözleşme:**
   - `.agent/skills/prelaunch-audit/SKILL.md` oluşturuldu (55 kelimelik sözleşme uyumlu frontmatter).
2. **Modüler Referanslar:**
   - `references/legal-privacy-compliance.md` (KVKK m.10, 7499 s. Kanun, Consent Mode v2, çerezler).
   - `references/seo-and-discoverability.md` (Ham HTML, sitemap, robots AI bot taksonomisi, canonical, 404).
   - `references/trust-and-local-structure.md` (GSC, PRG teşekkür, LocalBusiness, 28/B yorum kuralları).
   - `references/regulatory-sync-protocol.md` (AI modeli ile yasal ve platform verilerini güncelleme protokolü).
3. **Otomasyon Betikleri:**
   - `scripts/consent-check.mjs`: Playwright network & cookie sniffer.
   - `scripts/axe-runner.mjs`: Headless axe-core WCAG 2.2 AA scanner.
   - `scripts/html-audit.mjs`: Ham HTML meta, title, canonical ve h1 denetleyicisi.
   - `scripts/prelaunch_checker.py`: robots.txt, sitemap, llms.txt ve prod tuzakları denetleyicisi.
   - `scripts/prelaunch_updater.py`: Mevzuat tazelik denetimi ve AI güncelleme brifingi aracı.
4. **Merkezi Sözlük ve CLI:**
   - `.agent/rules/skill-trigger-routing.md` tablosuna ve kısayollarına eklendi.
   - `bin/cli.js` içine `prelaunch-audit` tanımlandı.
   - `.agent/skills-catalog.html` yeniden derlendi.
