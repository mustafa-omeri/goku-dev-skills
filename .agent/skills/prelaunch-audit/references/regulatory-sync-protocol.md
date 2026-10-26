# Yasal Mevzuat ve Platform Referansları Güncelleme Protokolü (/prelaunch-update)

Bu protokol, `prelaunch-audit` bünyesindeki yasal para cezaları, yürürlük tarihleri ve Google/AI platform yönergelerinin zaman içinde bayatlamasını önlemek ve AI Agent modeli aracılığıyla otonom/yarı-otonom güncellenmesini sağlamak amacıyla tasarlanmıştır.

---

## 1. İzlenen Kritik Yasal ve Platform Verileri

| Konu | Takip Edilen Referans | Resmi Kaynak / Dayanak |
|------|------------------------|-------------------------|
| **KVKK İdari Para Cezaları** | Standart sözleşme bildirim ihlali (2026: 90.308 TL - 1.806.377 TL) | Hazine ve Maliye Bakanlığı Yeniden Değerleme Oranı Tebliği / KVKK Kurulu |
| **Ticaret Bakanlığı 28/B** | Tüketici değerlendirmeleri ve yorum sansürü idari cezaları | Ticari Reklam ve Haksız Ticari Uygulamalar Yönetmeliği (RG 33297) |
| **Google Consent Mode v2** | Zorunlu consent parametreleri ve CMP entegrasyonu | Google Ads & Analytics API belgeleri |
| **Erişilebilirlik (EAA / EN 301 549)** | EAA Haziran 2025 yürürlüğü ve EN 301 549 v4.1.1 OJEU atıf durumu | AB Resmî Gazetesi (OJEU) / ETSI / W3C |
| **AI Bot Belirteçleri** | GPTBot, ClaudeBot, PerplexityBot, Google-Extended direktifleri | OpenAI, Anthropic, Google Search Central dokümantasyonları |

---

## 2. /prelaunch-update Komut Akışı

Kullanıcı `/prelaunch-update` veya `prelaunch update` yazdığında AI Agent şu adımları izler:

### Adım 1: Tazelik Denetimi
```bash
python .agent/skills/prelaunch-audit/scripts/prelaunch_updater.py --check
```
Tüm referans dosyalarındaki son doğrulama tarihleri ve izlenen regex desenleri taranır.

### Adım 2: Güncelleme Brifingi Üretimi
```bash
python .agent/skills/prelaunch-audit/scripts/prelaunch_updater.py --generate-prompt
```
Model için resmi kaynaklara yönelik araştırma brifingi üretilir.

### Adım 3: Resmi Doğrulama
Model, web arama yeteneklerini veya resmi kurum veritabanlarını kullanarak:
1. İlgili yılın Yeniden Değerleme Oranı (VUK Tebliği) sonrası KVKK para cezası limitlerini,
2. Reklam Kurulu'nun güncel yorum ve yanıltıcı tüketici kararlarını,
3. Google Search Central'ın sitemap/robots/rich result politikalarını doğrular.

### Adım 4: Cerrahi Güncelleme ve Tarih Damgası
- `.agent/skills/prelaunch-audit/references/` altındaki ilgili dosyalarda hardcoded rakamlar cerrahi olarak yenilenir.
- Dosyanın başındaki `Son veri doğrulaması: <Gün Ay Yıl>` damgası güncellenir.
- Yapılan değişiklikler `HANDOFF.md` ve oturum devir raporunda açıkça listelenir.
