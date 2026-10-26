---
name: check-security
description: OWASP güvenlik denetimi, public form koruması ve yetki aşımı kontrol orkestratörü; gizli anahtar ve ortam değişkeni sızıntılarını doğrular. Tetikleyiciler: "/check-security", "check security", "[CHECK-SECURITY]", "güvenlik açığı tara", "güvenlik denetimi". Tetiklenmez: kod kokusu taraması `code-review`'e aittir. Tam sözlük: .agent/rules/skill-trigger-routing.md
---

# Check Security Ensemble Orchestrator

Bu yetenek, web uygulamalarında güvenlik sınır ihlallerini, form kötüye kullanımını ve yetki aşımı açıklarını denetleyen güvenlik orkestrasyonunu yürütür.

## Orkestrasyon Akışı

1. **Halka 1 - İstemci & DOM Güvenliği:**
   - XSS, tehlikeli innerHTML / dangerouslySetInnerHTML kullanımı ve güvenli olmayan iframe yapılarını tara.
2. **Halka 2 - Public Form Abuse & Bot Savunması:**
   - Herkese açık formlarda (kayıt, giriş, iletişim) Cloudflare Turnstile / Captcha ve hız sınırlaması (rate-limiting) denetimi.
3. **Halka 3 - Backend & Yetkilendirme:**
   - Satır Düzeyi Güvenlik (RLS), JWT/Session kontrolleri ve SQL Injection risklerini incele.
4. **Halka 4 - Secret & Environment Denetimi:**
   - Kod tabanında, git geçmişinde veya dağıtım dosyalarında gizli API anahtarı, şifre veya hassas credential sızıntısı olmadığını doğrula.
