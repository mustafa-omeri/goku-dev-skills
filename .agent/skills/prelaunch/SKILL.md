---
name: prelaunch
description: Yirmi maddelik canlıya alma denetimi ve GO/NO-GO karar orkestratörü; KVKK, Consent Mode, ham HTML SEO ve erişilebilirliği doğrular. Tetikleyiciler: "/prelaunch", "prelaunch audit", "[PRELAUNCH]", "canlıya al", "yayına alma kontrolü". Tetiklenmez: geliştirme aşamasındaki birim testleri `tdd`'ye aittir. Tam sözlük: .agent/rules/skill-trigger-routing.md
---

# Prelaunch Audit Orchestrator

Bu yetenek, bir ürün veya web uygulamasının canlı ortama (production) çıkmadan önce 20 maddelik yasal, teknik, SEO ve erişilebilirlik gereksinimlerini denetleyip kesin GO / NO-GO kararı üreten denetim orkestrasyonunu yürütür.

## Orkestrasyon Akışı

1. **Yasal ve Gizlilik Denetimi:**
   - KVKK / GDPR aydınlatma metni, çerez politikası ve Google Consent Mode v2 entegrasyonu.
2. **SEO & İndekslenme Denetimi:**
   - `robots.txt`, `sitemap.xml`, ham HTML meta etiketleri ve bot erişim kuralları.
3. **Erişilebilirlik ve Güvenlik:**
   - WCAG 2.2 AA kontrast ve klavye erişilebilirliği, güvenlik başlıkları (CSP, HSTS).
4. **Mekanik Doğrulama:**
   - `python .agent/skills/prelaunch-audit/scripts/prelaunch_checker.py` çalıştırarak eksiksiz 20 madde raporunu üret.
