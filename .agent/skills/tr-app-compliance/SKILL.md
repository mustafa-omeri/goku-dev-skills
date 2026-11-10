---
name: tr-app-compliance
description: >-
  Türkiye mevzuatına (KVKK, ETK, 5651, TKHK, FSEK) uyumluluk denetimi yapar; ödeme adımları, ticari ileti onayı ve loglama kurallarını doğrular. Tetikleyiciler: "/tr-compliance", "türkiye mevzuatı", "kvkk denetimi", "yer sağlayıcı", "turkish compliance", "legal compliance scan". Tetiklenmez: global GDPR ve WCAG denetimi `prelaunch-audit`'e aittir. Tam sözlük: .agent/rules/skill-trigger-routing.md
---

# Türkiye Dijital Mevzuat ve Uygulama Uyum Denetçisi

Bu skill, Türkiye pazarında yayında olan web/mobil uygulamaların idari para cezası ve yasal yaptırımlarla karşılaşmaması için mimari, kod ve metin düzeyinde uyumluluk kontrolü sağlar.

## Tetikleyiciler
`/tr-compliance`, `[TR-COMPLIANCE]`, "türkiye mevzuatı", "kvkk denetimi", "yer sağlayıcı bildirimi", "5651 log", "hukuki risk tara", "tkhk abonelik", "etk ret linki"

## Temel Denetim Kuralları
1. **Ödeme ve Abonelik (TKHK):** Yenileme şartları ödeme butonunun üzerinde net olmalı.
2. **Ticari İleti (ETK):** Pazarlama e-postalarında Unsubscribe, MERSİS, açık adres zorunlu.
3. **Telif (FSEK):** Uyar-Kaldır (3 gün) için ihbar kanalı zorunlu.
4. **Yer Sağlayıcı (5651):** BTK bildirimi ve trafik logu zorunlu.
5. **Aydınlatma (KVKK m.10):** Açık rızadan bağımsız, önceden işaretlenmemiş aydınlatma.
6. **Yurt Dışı Aktarım (KVKK m.9/12):** Font ve CDN'ler yerel (self-hosted).

## Mekanik Kontrol
Kod tabanını taramak için:
```bash
python .agent/skills/tr-app-compliance/scripts/compliance_checker.py --dir .
```
Nginx log kontrolü için:
```bash
python .agent/skills/tr-app-compliance/scripts/compliance_checker.py --dir . --nginx-conf /etc/nginx/nginx.conf
```

