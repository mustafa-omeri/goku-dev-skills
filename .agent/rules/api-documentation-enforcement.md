---
name: API Documentation Enforcement
description: Backend API değişikliklerinde docs/APIs altındaki dokümantasyonun güncellenmesini, Swagger/OpenAPI uyumunu, breaking change ve kalite kontrol kurallarını zorunlu kılar.
sinif: OLCULEBILIR
kapi:
  - yigin: "Backend / API dokümantasyonu"
    komut: "python .agent/skills/musgoku/scripts/check_api_docs.py"
---

# 📄 API Dokümantasyonu Zorunluluğu

> Bu kural **backend projesinde** geçerlidir. Frontend-only projede uygulanmaz.

---

## 1. Dosya yapısı

```
docs/APIs/
├── [module-name]-API-Docs.md          # her modül için ayrı dosya
├── unified-api-response-structure.md  # response format standartı
├── README.md                          # genel rehber
└── CHANGELOG.md                       # tüm değişikliklerin kronolojik listesi
```

- Modül adı küçük harfle yazılır.
- Dosya yoksa **oluşturulur**; atlanmaz.
- Modül adları ve dosya adları **projeye özeldir** — burada yazılmaz.

## 2. Değişiklik sırası

1. **Önce** `docs/APIs/` altındaki ilgili dosyayı bul veya oluştur
2. **Sonra** kodu değiştir
3. **Hemen** dokümantasyonu aynı değişiklik içinde güncelle
4. **Son olarak** test et ve dokümantasyonun kodu yansıttığını doğrula

## 3. Değişiklik öncesi kontrol listesi

- [ ] Hangi endpoint değişiyor?
- [ ] Response yapısı değişiyor mu?
- [ ] Yeni alan ekleniyor mu?
- [ ] Parametre değişikliği var mı?
- [ ] Authorization gereksinimleri değişiyor mu?
- [ ] Breaking change var mı?
- [ ] Yanıt zarfı formatına uygun mu?

## 4. Zorunlu içerik

- [ ] Tarih damgası (`YYYY-MM-DD`)
- [ ] Endpoint (`METHOD /api/v1/path`)
- [ ] Değişiklik açıklaması (ne ve neden)
- [ ] Authorization gereksinimleri (hangi roller erişir)
- [ ] Query / path parametreleri (varsa)
- [ ] Request örneği (geçerli JSON)
- [ ] Response örneği (standart zarf formatında, gerçek kodla uyumlu)
- [ ] Yeni alanların açıklaması
- [ ] Breaking change varsa açıkça belirtilmiş **ve** migration guide var
- [ ] Hata yanıtları (400 · 401 · 403 · 404 · 500)

## 5. Koruyucu güncelleme

Mevcut dokümanı güncellerken:

- ⛔ Mevcut detayları **silme**
- ✅ Yalnız **değişen** kısımları güncelle
- ✅ Tüm açıklamaları ve örnekleri **koru**
- ✅ Yeni bilgiyi mevcut yapıya uygun şekilde **ekle**
- ✅ Dokümantasyon yapısını ve formatını **bozma**
- ✅ Değişmeyen diğer endpoint'lerin dokümantasyonuna ** dokunma

**Örnek koruma stratejisi:**

````markdown
## Son Güncelleme: YYYY-MM-DD

### <N>. <Endpoint Adı>

**Tarih:** YYYY-MM-DD
**Endpoint:** `POST /api/v1/<module>/<path>`

<Açıklama>

**Authorization:** <roller>

**Özel Kurallar:**
- <bu endpoint'e özgü kural>

**Request:**
```json
{ "field": "value" }
```

**Response:**
```json
{
  "status": "success",
  "message": "...",
  "timestamp": "...",
  "data": { }
}
```

// ... mevcut diğer endpoint'ler korunur ...
````

## 6. Modül dokümanı şablonu

````markdown
# <Module Name> API Documentation

## 📝 Son Değişiklikler

### <N>. <Endpoint/Feature Adı>

**Tarih:** YYYY-MM-DD
**Endpoint:** `METHOD /api/v1/path`

[Açıklama]

**Authorization:** ROL1, ROL2

**Query Parameters:**
- `param1` (optional): Açıklama
- `param2` (required): Açıklama

**Request Body:**
```json
{ "field1": "value1" }
```

**Response:**
```json
{
  "status": "success",
  "message": "İşlem başarılı",
  "timestamp": "...",
  "data": { },
  "meta": { }
}
```

**Error Responses:**
- 400: Doğrulama hatası
- 401: Unauthorized
- 403: Forbidden
- 404: Bulunamadı
- 500: Sunucu hatası

---

## Overview
[Modül hakkında genel açıklama]

## Base URL
- Development: `<geliştirme adresi>`
- Production: `<üretim adresi>`

## Authentication
Tüm endpoint'ler kimlik doğrulama ister:
```
Authorization: Bearer <token>
```

## Endpoints
[Detaylı endpoint listesi — "Son Değişiklikler" bölümünden sonra gelir]
````

> Adresler ve yollar **projeye özeldir**; bu şablon yer tutucu kullanır.

---

## 7. Swagger / OpenAPI

### 7.1 Controller seviyesi

```java
@Tag(name = "<Module> Management", description = "...")
```

### 7.2 Endpoint seviyesi

```java
@Operation(
    summary = "...",
    description = "... rol kısıtı dahil"
)
@ApiResponses(value = {
    @ApiResponse(responseCode = "200", description = "..."),
    @ApiResponse(responseCode = "400", description = "Geçersiz parametre"),
    @ApiResponse(responseCode = "401", description = "Unauthorized"),
    @ApiResponse(responseCode = "403", description = "Forbidden")
})
```

### 7.3 Şartlar

- **OpenAPI 3.0** Specification
- İstemciye dönen **her alanın** şeması tanımlı olmalı
- Şema alan adları yanıt zarfıyla **birebir aynı** olmalı
- Markdown dokümantasyonla **senkron** tutulmalı

### 7.4 Şartnamede bulunması gerekenler

| Bölüm | İçerik |
|---|---|
| API metadata | başlık, açıklama, sürüm |
| Server configuration | geliştirme ve üretim adresleri |
| Path definitions | her endpoint için metot, özet, parametreler, istek gövdesi şeması, yanıt şemaları (200/400/401/403/404/500) |
| Schema definitions | istek DTO'ları, yanıt DTO'ları, ortak yanıt zarfı |

### 7.5 Erişim

Swagger UI ve ham şema JSON'u **çalışan ortamın adresi** üzerinden sunulur
(`/swagger-ui.html`, `/v3/api-docs` gibi). Bu adresler ortam yapılandırmasından
gelir; koda gömülmez ve bu kuralda sabit yazılmaz.

---

## 8. Breaking change protokolü

### 8.1 Deprecation bildirimi

````markdown
### <Endpoint Adı> - DEPRECATED

**Tarih:** YYYY-MM-DD
**Durum:** ⚠️ DEPRECATED — Bu endpoint YYYY-MM-DD tarihinde kaldırılacaktır.

**Yeni Endpoint:** `METHOD /api/v1/new-path`

**Migration Guide:**
- Eski endpoint: `/api/v1/old-path`
- Yeni endpoint: `/api/v1/new-path`
- Değişiklikler: [Açıklama]
````

### 8.2 Migration guide

````markdown
## Migration Guide: <Feature Name>

**Tarih:** YYYY-MM-DD

### Değişiklikler

1. **Endpoint Değişikliği**
   - Eski: `POST /api/v1/old-endpoint`
   - Yeni: `POST /api/v1/new-endpoint`

2. **Request Body Değişikliği**
   ```json
   // Eski format
   { "oldField": "value" }
   // Yeni format
   { "newField": "value" }
   ```

3. **Response Değişikliği**
   ```json
   // Eski
   { "oldResponse": "value" }
   // Yeni
   { "newResponse": "value" }
   ```

### Zaman Çizelgesi
- Deprecation Date: YYYY-MM-DD
- Removal Date: YYYY-MM-DD (en az 3 ay sonra)
````

### 8.3 Sürümleme stratejisi

| Sürüm | Ne zaman | Nasıl |
|---|---|---|
| Major | Breaking change | Yol öneki değişir (`/api/v2/`) |
| Minor | Yeni özellik | Dokümantasyonda belirtilir |
| Patch | Hata düzeltme | Dokümantasyonda belirtilir |

Mevcut API sürümü `/api/v1/` önekiyle belirlenir.

---

## 9. Kalite kontrolü

Her dokümantasyon güncellemesi sonrası:

### Dokümantasyon

- [ ] Tarih damgası eklendi mi?
- [ ] Endpoint bilgisi doğru mu?
- [ ] Authorization gereksinimleri belirtildi mi?
- [ ] Request/response örnekleri geçerli JSON mu?
- [ ] Yanıt örnekleri gerçek kodla uyumlu mu?
- [ ] Tüm yeni alanlar dokümante edildi mi?
- [ ] Breaking change belirtildi mi? (varsa)
- [ ] Migration guide hazırlandı mı? (breaking change varsa)

### Kod

- [ ] Swagger annotation'ları güncel mi?
- [ ] Controller'da `@Operation` var mı?
- [ ] Yanıt tipleri doğru mu?
- [ ] Hata yönetimi dokümante edildi mi?

### Test

- [ ] Test senaryoları güncel mi?
- [ ] Entegrasyon testleri çalışıyor mu?
- [ ] Yanıt formatı test edildi mi?

### Diğer

- [ ] Mevcut dokümantasyon korundu mu?
- [ ] Yalnız değişen kısımlar güncellendi mi?
- [ ] Dokümantasyon yapısı bozulmadı mı?

---

## 10. Yapılacak / yapılmayacak

### ✅ Yap

- **Koruyucu güncelleme** — mevcut dokümanı koru, yalnız değişeni güncelle
- **Detaylı açıklama** — her değişiklik anlaşılır biçimde belgelenir
- **Tarih damgası** — her güncellemeye tarih
- **Örnek koruma** — mevcut request/response örnekleri korunur
- **Yapısal bütünlük** — dokümantasyon yapısı bozulmaz
- **Zarf uyumu** — tüm yanıtlar standart zarf formatında gösterilir
- **Swagger senkronu** — annotation'lar dokümantasyonla senkron
- **Breaking change görünürlüğü** — belirtilir ve migration guide hazırlanır

### ❌ Yapma

- Mevcut detayları **silme**
- Tüm dokümantasyonu **yeniden yazma**
- Yalnız bir kısmını güncelleme
- Mevcut yapıyı **bozma**
- Mevcut örnekleri **kaybetme**
- Zarf formatından **sapma**
- Swagger annotation'larını güncellemeyi **unutma**
- Breaking change'i **gizleme**

---

## 11. Uygulama mekanizması

Kural ihlal edilirse:

1. **İş durdurulur** — dokümantasyon tamamlanmadan kod teslim edilmez.
2. **Kullanıcıya açık uyarı** verilir; eksik bölüm adıyla birlikte.
3. Dokümantasyon güncellemesi zorunlu kılınır.
4. İnceleme noktaları: her API değişikliğinde, commit öncesi, kod incelemesinde.

---

## 12. İhlal

Dokümantasyon eksikse iş **tamamlanmış sayılmaz.** Eksikse önce dokümanı
tamamla, sonra `knowledge-base.md`'ye not düş. Sessizce geçme.

---

## Proje Bazlı Ek Kurallar

> ⛔ **Kural Ekleme ve Mükerrerlik İlkesi:**
> 1. Yukarıdaki global kurallar projeler arası standarttır ve değiştirilmez.
> 2. Projeye özgü bir istisna veya ek API dokümantasyon kuralı gerekirse, önce yukarıdaki global kurallarla mükerrerlik denetimi yapılır.
> 3. Yeni kural yalnızca bu başlığın altına `### <Kural Başlığı>` olarak eklenir.

### Bu Proje İçin Ek Kurallar
_(Henüz bu projeye özel ek bir kural tanımlanmamıştır.)_