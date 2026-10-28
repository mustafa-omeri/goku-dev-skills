---
name: check-security
description: OWASP güvenlik denetimi, public form koruması ve yetki aşımı kontrol orkestratörü; gizli anahtar ve ortam değişkeni sızıntılarını doğrular. Tetikleyiciler: "/check-security", "check security", "[CHECK-SECURITY]", "güvenlik açığı tara", "güvenlik denetimi". Tetiklenmez: kod kokusu taraması `code-review`'e aittir. Tam sözlük: .agent/rules/skill-trigger-routing.md
---

# Check Security Ensemble Orchestrator

Bu yetenek, web ve sunucu uygulamalarında güvenlik sınır ihlallerini, herkese açık form (public form) kötüye kullanımını, yetki aşımı (IDOR / BOLA / RLS) açıklarını ve gizli anahtar sızıntılarını denetleyen güvenlik orkestrasyonunu yürütür (`security-audit` + `development-workflow` + `prelaunch-audit`).

## Bağlı Kurallar ve Alt Yetenekler

- **Birincil Yetenek:** `security-audit` (`.agent/skills/security-audit/SKILL.md`)
- **Destekleyici Yetenekler:** `prelaunch-audit`, `musgoku` (`references/security-logging.md`)
- **Kurallar:** `.agent/rules/development-workflow.md` (Adım 2.1 Halka 2 — Public Form 6 Katmanlı Güvenlik Sözleşmesi)

---

## 4 Halkalı Güvenlik Denetim Protokolü

### 1. Halka 1 — İstemci, DOM ve XSS Güvenliği
- Tehlikeli `innerHTML`, `dangerouslySetInnerHTML`, `eval()`, doğrulanmamış URL yönlendirmeleri (`javascript:` şeması) ve güvensiz `iframe` yapılarını tara.
- Tarayıcıda hassas token veya kişisel verinin (PII) `localStorage` veya konsol loglarına sızmadığını doğrula.

### 2. Halka 2 — Public Form Abuse & Bot Savunması (6 Katmanlı Kalkan)
Herkese açık veri toplayan her formda (geri bildirim, iletişim, bülten, başvuru, raporlama) şu 6 katmanın varlığını denetle:
1. **Context Binding:** Kayıt geçerli bir üst kaynağa (`event_id`, `tenant_id` vb.) bağlı mı?
2. **Honeypot:** Botlar için görünmez tuzak alanı (`website_url` vb.) var mı?
3. **Challenge:** Cloudflare Turnstile / Captcha doğrulaması aktif mi?
4. **Rate Limiting:** IP veya oturum bazlı hız sınırlaması (Edge/Backend) var mı?
5. **Input Sanitization:** Zod/Bean Validation ile uzunluk sınırı ve HTML/script temizliği yapılıyor mu?
6. **Blind Insert RLS:** Anonim kullanıcı yalnızca `INSERT` yapabiliyor mu (`SELECT`/`UPDATE`/`DELETE` kapalı mı)?

### 3. Halka 3 — Backend, Veritabanı ve Yetkilendirme (AuthZ / RLS)
- Supabase / PostgreSQL tablolarında **Row Level Security (RLS)** politikalarının açık olduğunu ve kiracı izolasyonunun (`tenant_id` / `user_id`) sunucu tarafında zorlandığını doğrula.
- Parametrik olmayan ham SQL birleştirmelerini (SQL Injection) ve yetki kontrolsüz uç noktaları (IDOR / BOLA) tara.

### 4. Halka 4 — Secret, Credential ve Ortam Değişkeni Sızıntısı
- Kaynak kodda, istemci paketlerinde (`VITE_*`, `NEXT_PUBLIC_*`) veya git çalışma ağacında özel anahtar (`service_role`, `SECRET_KEY`, veritabanı parolası) sızıntısı olmadığını doğrula.
- Birleşik doğrulama kapılarını çalıştır:
  ```bash
  python .agent/skills/musgoku/scripts/run_all_gates.py
  ```

---

## Standart Çıktı Raporu

```markdown
### 🛡️ CHECK-SECURITY: GÜVENLİK DENETİM KARNESİ
- **Halka 1 (İstemci & XSS):** [✅ Temiz / ❌ Bulgu]
- **Halka 2 (Public Form 6 Katmanlı Kalkan):** [✅ Tam Uyumlu / ➖ Kapsam Dışı / ❌ Eksik Katman: ...]
- **Halka 3 (Yetkilendirme, IDOR & DB RLS):** [✅ Temiz / ❌ Bulgu]
- **Halka 4 (Secret & Env Sızıntısı):** [✅ Temiz / ❌ Bulgu]
- **Kritik Bulgular ve Onarım Önerileri:** [Varsa ciddiyet derecesi (CRITICAL/HIGH/MEDIUM) ve dosya:satır]
```
