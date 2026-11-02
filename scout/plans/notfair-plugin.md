# 🔭 Scout Değerlendirme Raporu: nowork-studio/notfair-plugin

## 1. Depo Özeti ve Künye
- **URL:** https://github.com/nowork-studio/notfair-plugin
- **Sahibi:** nowork-studio
- **Analiz Tarihi:** 2026-10-30 13:39
- **Tespit Edilen Katman:** Tooling / Agentic + Marketing Ops
- **Dosya Sayısı & Boyut:** 287 dosya (~1595 KB)
- **Teknoloji Yığını:** Python (`google-auth`, `google-auth-httplib2`, `requests`), Markdown Tabanlı Agentic İş Akışları (Claude Code Plugin / Cursor MCP yapısı), GA4, GSC, Google/Meta/X/LinkedIn/TikTok Ads API entegrasyonları.

## 2. Çekirdek Felsefe ve Mimari (Repo İncelemesi)
- **Temel Amaç:** AI ajanlarına (Claude Code, Cursor, Codex vb.) kuru prompt şablonları vermek yerine deterministik, denetlenebilir ve kategorize edilmiş pazarlama/SEO/reklam operasyon iş akışları (`WORKFLOW.md`, `operating-contract.md`, `evals/`, `agents/`) sunmak.
- **Mimari Yapı:** 
  - Her yetenek kategorisinde (SEO, GEO/AEO, Analytics, Paid Ads, CRM/CMS) bir `SKILL.md` ve detaylandırılmış `WORKFLOW.md` bulunur.
  - Python bağımlılıkları ağırlıklı olarak Google API (OAuth, GA4, Search Console) yetkilendirmesi ve REST sorguları için kullanılmıştır.
  - Harici barındırılan bir MCP servisi (NotFair hosted MCP) üzerinden OAuth ve üçüncü taraf platform (WordPress, GoHighLevel, Meta, TikTok) operasyonları yönetilmektedir.
- **Güçlü Yönleri:**
  - Salt SEO değil; GEO (Generative Engine Optimization - ChatGPT, Perplexity, Gemini, Claude kaynak atıfı) ve çok kanallı paid media optimizasyonunda somut kabul kriterleri ve onay sınırları tanımlamış.
  - GA4 ve Google Search Console üzerinde dönem karşılaştırmalı veri analizi ve düşüş teşhisi (traffic drop diagnosis) protokolleri oldukça yapısal.
- **Zayıf / Riskli Yönleri:**
  - Barındırılan kapalı bir MCP (`mcp-connection.md`) ve dış SaaS (WordPress, GoHighLevel) bağımlılıkları barındırması; self-contained ve zero-trust çalışan yerel ajan mimarimize doğrudan uymamaktadır.
  - 48 adet parçalı skill repo boyutunu ve token yükünü şişirmektedir (şişkinlik riski).

## 3. Bizim Sistemle Kıyaslama (Delta Analizi)
- **Mevcut Durumumuz:**
  - `seo-growth`: Kapsamlı teknik SEO, JSON-LD, OpenGraph, GEO/AEO stratejileri, E-E-A-T, topic clustering ve CRO formüllerine zaten sahibiz.
  - `seo-apply`: Meta etiketler ve yapısal veri şemalarını otonom ve hatasız biçimde kod tabanına uygulayabilen orkestratörümüz aktiftir.
  - `prelaunch` / `prelaunch-audit`: Canlıya çıkış öncesi 20 maddelik mevzuat, KVKK, Consent Mode v2 ve temel arama motoru denetimlerini başarıyla yürütmektedir.
  - `banner-design` & `brand`: Reklam boyutları, art direction ve marka kimliği tarafında zaten yerel zanaat standartlarımız mevcuttur.
- **Dış Repodaki Değer:**
  - **GEO/AEO Alıntı Optimizasyonu:** AI arama motorlarının (Perplexity, ChatGPT Search, Gemini) içerikten alıntı yapma kriterlerine dönük pratik metrikler/kontrol listeleri.
  - **GA4 & Search Console Teşhis Akışı:** Organik trafik kayıplarında (`traffic drop`) Google Search Console ve GA4 dönem verilerini çapraz doğrulama senaryoları.
  - **Paid Media Onay ve Bütçe Güvenlik Sözleşmesi:** Ajanların reklam bütçelerine dokunurken aşmaması gereken kesin kırmızı çizgiler (`operating-contract.md`).
- **Kesişim & Ayrışma:**
  - Repodaki 48 yeteneğin büyük kısmı bizim `seo-growth`, `brand` ve `banner-design` skill'lerimizle örtüşmektedir.
  - Tüm repoyu indirmek veya plugin olarak eklemek ciddi token kirliliği ve harici servis bağımlılığı yaratır; ancak içerisindeki denetim matrisleri cerrahi olarak ayıklanmaya değerdir.

## 4. Karar ve Gerekçe
**Karar:** `KISMEN_ALINABILIR: GA4/GSC denetim iş akışları, reklam kanalı harcama analiz modelleri ve GEO doğrulama kontrol listeleri mevcut seo-growth ve prelaunch yeteneklerimize zenginleştirme referansı olarak cerrahi biçimde entegre edilebilir; harici barındırılan MCP veya CRM/SaaS bağımlılıkları dışarıda tutulmalıdır.`

**Gerekçe:** Depo bütünüyle içeri alınamayacak kadar harici platformlara (barındırılan MCP, SaaS CRM) bağımlıdır ve mevcut skill setimizin derinliği zaten kod üretimi ve teknik mimaride üstündür. Ancak içerisindeki analitik teşhis protokolleri ve AEO alıntı kriterleri, mevcut `seo-growth` ve `prelaunch-audit` kütüphanelerimizi güçlendirebilecek değerli operasyonel kalıplar sunmaktadır.

## 5. Cerrahi Entegrasyon Planı / Eylem Maddeleri
1. **`seo-growth` Referans Zenginleştirmesi:**
   - NotFair reposundaki GEO/AEO alıntı kriterleri ve Perplexity/ChatGPT kaynak gösterim optimizasyon maddeleri `seo-growth/references/` altına ek bir bilgi notu olarak dahil edilmeli.
2. **Trafik Düşüşü & Analitik Teşhis Kontrol Listesi:**
   - Search Console ve GA4 dönem karşılaştırma algoritması ve "organik trafik düşüş teşhis matrisi" `seo-growth` operasyon adımlarına cerrahi olarak enjekte edilmeli.
3. **Kapsam Dışı Bırakılacaklar:**
   - NotFair hosted MCP bağlantıları, WordPress REST API CRUD modülleri, GoHighLevel CRM entegrasyonları ve platforma özgü reklam yönetim yetenekleri (bütçe riski ve yerel repo prensiplerimiz gereği) kesinlikle projeye dahil edilmeyecektir.