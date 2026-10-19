---
name: domain-modeling
description: İş alanı modelleme ve ortak dil (ubiquitous language) yönetimi; GLOSSARY.md sözlüğünü kodla senkronize tutar ve mimari karar kayıtları (ADR) üretir. Tetikleyiciler: "domain model", "terimler sözlüğü", "glossary", "domain modeling", "ubiquitous language", "adr decision". Tetiklenmez: teknik PRD ve RFC süreç yönetimi `doc-coauthoring` kapsamındadır. Tam sözlük: .agent/rules/skill-trigger-routing.md
---

# Domain Modeling (İş Alanı Modelleme)

Tasarım ve geliştirme yaparken projenin iş alanı modelini (domain model) aktif olarak inşa edin ve keskinleştirin. Bu skill terimleri sorgulama, uç senaryoları türetme, `GLOSSARY.md` sözlüğünü canlı tutma ve mimari kararları (ADR) netleştirme disiplinidir.

## Dosya Yapısı

Tek bağlamlı projeler:
```
/
├── GLOSSARY.md
├── docs/
│   └── adr/
│       ├── 0001-siparis-state-makinesi.md
│       └── 0002-postgres-yazma-modeli.md
└── src/
```

Çoklu bağlamlı (bounded contexts) projelerde kökte `GLOSSARY-MAP.md` yer alır ve her bağlamın sözlüğü kendi dizinindedir.

*Dosyalar tembelce (lazily) oluşturulur: İlk iş kavramı kesinleştiğinde `GLOSSARY.md`, ilk mimari karar alındığında `docs/adr/` oluşturulur.*

## Oturum Esnasında Zorunlu Davranışlar

### 1. Terimleri Sözlüğe Karşı Sorgulayın (Challenge Against the Glossary)
Kullanıcı `GLOSSARY.md`'deki tanımlarla çelişen bir terim kullandığında anında yüzeye çıkarın: "Sözlüğünüz 'iptal' terimini X olarak tanımlıyor ancak siz Y anlamında kullanıyorsunuz. Hangisi geçerli?"

### 2. Muğlak Dili Netleştirin (Sharpen Fuzzy Language)
Aşırı yüklenmiş veya belirsiz ifadeler yerine kanonik terim önerin: "'Hesap' diyorsunuz; Müşteri'yi mi yoksa Kullanıcı'yı mı kastediyorsunuz? İkisi farklı kavramlardır."

### 3. Somut Senaryoları Tartışın
Kavram sınırlarını zorlayan uç senaryolar (edge cases) türeterek sınırları netleştirin.

### 4. Kodla Çapraz Doğrulama Yapın (Cross-reference with Code)
Kullanıcının beyanı ile mevcut kod tabanının davranışı çelişiyorsa hemen uyarın: "Kod tüm siparişi iptal ediyor ancak siz kısmi iptal olabileceğini söylediniz. Hangisi doğru?"

### 5. GLOSSARY.md'yi Canlı Güncelleyin (Update Inline)
Bir kavram netleştiği anda `GLOSSARY.md`'yi güncelleyin; oturum sonuna ertelemeyin. Format kuralları için [references/GLOSSARY-FORMAT.md](references/GLOSSARY-FORMAT.md) dosyasına bakın.
*Not: `GLOSSARY.md` saf iş kavramlarını içerir; teknik uygulama detayları, kütüphane isimleri veya geçici notlar buraya yazılmaz.*

### 6. Mimari Kararları (ADR) Yalnızca 3 Kriter Sağlandığında Önerin

Bir ADR yalnızca şu **3 şartın tamamı** sağlandığında açılır:
1. **Geri Dönüşü Zor (Hard to reverse):** İleride fikri değiştirmenin maliyeti yüksektir.
2. **Bağlamsız Okuyucu İçin Şaşırtıcı (Surprising without context):** Gelecekte kodu okuyan biri "Neden böyle yapmışlar?" diyecektir.
3. **Gerçek Bir Ödünleşimin Sonucu (Real trade-off):** Gerçek alternatifler vardı ve belirli gerekçelerle biri seçildi.

Bu 3 şarttan biri eksikse ADR açılmaz. Format için [references/ADR-FORMAT.md](references/ADR-FORMAT.md) dosyasına bakın.
