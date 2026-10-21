# Güvenlik, Loglama ve Performans Standardı

> 🛡️ **Güvenlik Otoritesi ve Zafiyet Denetimi:**
> Bu dosya Spring Boot ve backend tarafında güvenli kod yazımı, loglama ve performans için yapıcı kodlama standartlarını tanımlar.
> Sistem ve kod tabanlarında sızma testi, güvenlik açığı avcılığı, yetki aşımı (privilege escalation), token/session istismarı ve boundary violation denetimi için sistemin tek yetkili güvenlik otoritesi **`.agent/skills/security-audit/`** skill'idir.

---

## 1. Kimlik doğrulama ve yetkilendirme

### 1.1 JWT

- Kimlik doğrulama filtre zinciri ile yapılır
- İmzalama için güçlü anahtar; anahtar ortam değişkeninden okunur, **koda gömülmez**
- Belgeçelen ömrü uygun tanımlanır
- Yük içinde gerekli roller/izinler taşınır
- Korumalı her istekte doğrulanır
- Uzun oturumlar için yenileme belirteci kullanılır
- İstemci tarafında belirteç güvenli saklanır

### 1.2 Framework güvenliği

- Güvenlik yapılandırması merkezîdir
- Roller ve izinler açıkça tanımlanır
- Metot seviyesinde yetki kontrolü kullanılır
- Parolalar modern bir hash algoritmasıyla saklanır

### 1.3 Genel

- Tüm kullanıcı girdileri doğrulanır ve temizlenir
- Hassas veri şifrelenir
- OWASP güvenli kodlama rehberi izlenir
- Bağımlılıklar düzenli güncellenir
- CORS açıkça tanımlanır; üretimde `*` kullanılmaz

### 1.4 Yetki kontrolü — zorunlu desen

⛔ **Token ≠ istek.** Token'ın varlığı, istenen kaydın kullanıcıya ait olduğunu
göstermez.

| Kural | Açıklama |
|---|---|
| Kiracı/kullanıcı kapsamı kimlikten gelir | İstek parametresinden veya gövdesinden **alınmaz** |
| Kontrol servis katmanında yapılır | Sorgu başlamadan önce filtre uygulanır |
| Alan seviyesinde kontrol | Toplu işlemlerde kayıt bazında yetki doğrulanır |
| Yetkisiz durum net ayrılır | Kimlik yoksa 401, yetki yoksa 403 |
| Roller kod ile tanımlanır | Serbest metin rol karşılaştırması yapılmaz |

### 1.5 Hata ve sızdırmama

- Kullanıcıya anlamlı mesaj verilir; teknik detay **log'a** yazılır
- Stack trace, sorgu, kimlik bilgisi veya sistem yolu yanıta sızmaz
- Şifre, belirteç ve kişisel veri hiçbir seviyede loglanmaz

---

## 2. Loglama

### 2.1 Çerçeve ve seviyeler

SLF4J + uygun arka uç. Seviye sırası:
`ERROR` > `WARN` > `INFO` > `DEBUG`

| Seviye | Ne zaman |
|---|---|
| `ERROR` | İş durduruldu, kullanıcı etkileniyor |
| `WARN` | Beklenmeyen ama işleyen durum, geçici çözüm |
| `INFO` | İş akışı olayı, durum değişimi |
| `DEBUG` | Geliştirme detayı; üretimde kapalı |

### 2.2 Kurallar

- Yapılandırılmış log: olay tipi, varlık kimliği, kullanıcı, istek kimliği,
  zaman damgası
- İstek izleme için korelasyon kimliği
- Hassas veri loglanmaz
- Uygulama metrikleri ve izleme açık bırakılır
- Metrikler için sağlık uçları etkin

---

## 3. Performans

### 3.1 Async ve önbellek

- Engelleyici olmayan işler asenkron yürütülür (`@Async`); asenkron işlemde
  hata yutulmaz, zincir sonunda ele alınır
- Spring Cache soyutlaması üzerinden önbellek stratejileri uygulanır
- Toplu işlemlerde veritabanı erişimi gruplanır (batch)
- Veritabanı indekslemesi ve sorgu optimizasyonu ayrıca değerlendirilir
- Eşzamanlı işlemler doğru yönetilir (kilit sırası, yarış koşulu)

### 3.2 Yanıt başlıkları

| Başlık | Kullanım |
|---|---|
| `max-age=..., public` | Genel içerik |
| `no-cache, no-store, must-revalidate` | Önbellek yok |
| `private` | Yalnız istemci önbelleği |
| `no-transform` | Dönüşüm yok |
| `immutable` | Değişmeyen içerik |
| `stale-while-revalidate` | Arka planda tazeleme |

### 3.3 Veritabanı

- Sorgu optimizasyonu ve uygun index
- N+1 sorgu önleme
- Toplu işlemlerde batch
- Eşzamanlı işlemlerin doğru yönetimi

### 3.4 Sayfalama performansı

Sayfa boyutu sınırları ve stratejisi için:
**[pagination-search.md](./pagination-search.md)**

### 3.5 Hız sınırı ve kısıtlama

- İstek penceresi ve pencere içi istek sayısı yapılandırmadan okunur
- Liste/arama ile dışa aktarma uç noktaları ayrı sınırlara sahiptir
- Değerler projeye göre belirlenir; makul başlangıç: 15 dakika / 100 istek

### 3.6 Gözlemlenebilirlik

- Uygulama metrikleri
- Yavaş sorgu eşiği
- Liste uç noktalarında süre ölçer
- Hedef değer belirlenir ve yük testiyle doğrulanır

---

## 4. Kontrol listesi

- [ ] Kimlik doğrulama filtre zinciri kurulu
- [ ] Merkezî güvenlik yapılandırması var
- [ ] Metot seviyesinde yetki kontrolü var
- [ ] Parola hash algoritması modern
- [ ] Girdi doğrulama ve temizleme yapılıyor
- [ ] CORS açıkça tanımlı, üretimde `*` yok
- [ ] Güvenlik başlıkları ayarlı
- [ ] Hız sınırı uygulanıyor
- [ ] Yapılandırılmış loglama ve korelasyon kimliği var
- [ ] Hassas veri loglanmıyor
- [ ] İzleme açık
- [ ] Bağımlılıklar güncel
- [ ] Yetki kontrolü sorgu içinde, kimlikten gelen kapsamla yapılıyor