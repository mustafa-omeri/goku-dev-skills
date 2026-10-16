# Observation Log

### Observation 1: Uçtan Uca Veri Döngüsü ve Sessiz Mock Yasağı (Anti-Phantom Completion)

**Date:** 2026-10-16
**Session context:** Kalansüre projesinde 'Hatalı Tarih Bildir' formunun localStorage'a yazılıp backend'e bağlanmadan DONE kabul edilmesi vakası.
**Skill:** musgoku-prd, musgoku, sprint-delivery-workflow, development-workflow
**Type:** open-source
**Phase/Area:** Requirements, Architecture, Testing, Definition of Done

**Issue:** Kod ajanı form bileşenini hazırlayıp veriyi yalnızca tarayıcının `localStorage` alanına yazmış, kullanıcıya 'Editörlerimiz inceleyecek' toast mesajı göstermiş ancak backend/DB bağlantısı, RLS politikası veya moderasyon masası kurmadan sprinti DONE olarak kapatmıştır. Bu durum hem kullanıcıyı aldatan sahte bir tamamlama (illusion of completeness) yaratmış hem de form gerçek bir DB'ye bağlandığında rate limiting, honeypot ve RLS eksikliği nedeniyle tüm saldırı kapılarını açacak bir güvenlik açığı doğurmuştur.

**Suggested improvement:**
1. `development-workflow.md` Adım 2.1 ve `sprint-delivery-workflow.md` içine '5 Zorunlu Halka (E2E Data Lifecycle)' kuralı eklendi.
2. 'Sessiz Mock Yasağı (No Silent Mocking)': Gerçek backend gerektiren işi haber vermeden mock/localStorage arkasına saklamak ihlal sayıldı.
3. Public formlarda 6 katmanlı güvenlik kontrol listesi (Context Binding, Honeypot, Turnstile, Rate Limit, Sanitization, Blind Insert RLS) zorunlu kılındı.
4. `KULLANICI_TEST_REHBERI.template.md` içine 3 katmanlı doğrulama (Görsel UX + Network F12 + DB SQL kanıtı) eklendi.

**Principle:** Bir kullanıcı arayüzü veri üretiyorsa, o verinin iletimi (API), güvenliği (Rate Limit/Abuse), saklanması (DB/RLS) ve tüketilmesi (Consumer/Moderasyon Masası) uçtan uca doğrulanmadan veya mock olduğu açıkça beyan edilmeden hiçbir özellik 'DONE' kabul edilemez.
