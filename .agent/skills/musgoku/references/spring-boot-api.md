# REST API Geliştirme ve Dokümantasyon Standardı

> Modül adı, temel URL ve örnek kayıtlar **projeye özeldir**; burada yalnız
> genel biçim ve kurallar vardır.

---

## 1. Controller kuralları

### 1.1 Yapı

```java
@RestController
@RequestMapping({ "/v1/<module>", "/api/v1/<module>" })
@Tag(name = "<Module> Management", description = "...")
public class <Module>Controller {
}
```

- Önek tek veya çift olabilir; projedeki mevcut önek **kazanır** ve yeni endpoint'ler
  onu izler. Tüm modüller aynı öneki kullanır.
- Yol önekli mi (`/api/v1/`) yoksa düz mü (`/v1/`) olup olmadığı **projeden
  doğrulanır**, bu kuralda sabit yazılmaz.

### 1.2 HTTP metotları

- ✅ **GET** — okuma
- ✅ **POST** — yazma, işlem başlatma, eylemi anlatan uç nokta
  (`/assign-company` gibi isimlendirme tercih edilir)

POST varsayılandır. Farklı HTTP metotları kullanılan bir API sözleşmesi varsa
o sözleşme esas alınır ve gerekçesi `knowledge-base.md`'ye yazılır.

### 1.3 İstek doğrulama

- Tüm istek gövdeleri `@Valid` ile doğrulanır
- Kısıt anotasyonları DTO üzerindedir: `@NotNull`, `@NotEmpty`, `@Size`, `@Email`
- Karmaşık kurallar için özel `ConstraintValidator` yazılır

### 1.4 JavaDoc zorunluluğu

Tüm public controller metotları:

```java
/**
 * <Ne yaptığı>
 * <p>Kullanım: METHOD /api/v1/<module>/<path></p>
 *
 * @param <ad> <açıklama>
 * @return <tip> <açıklama>
 * @throws <ExceptionType> <ne zaman>
 */
```

### 1.5 Sorumluluk ayrımı

- Tüm istek/yanıt işleme yalnız controller'da
- Tüm veritabanı işlem mantığı servis impl sınıflarında, repository üzerinden
- Controller ↔ servis arası veri taşıma **yalnız DTO**
- ⛔ Controller repository'yi doğrudan autowire etmez (istisna gerekçesi kaydedilir)

---

## 2. Entity kuralları

```java
@Entity
@Data                                    // Lombok; proje farklıysa proje kazanır
public class <Entity> {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Size(max = 100)
    @NotEmpty
    private String name;

    @ManyToOne(fetch = FetchType.LAZY)   // ilişkilerde varsayılan LAZY
    @JoinColumn(name = "<parent>_id")
    private <Parent> parent;
}
```

- Entity yalnız veritabanı sonuçlarını taşır
- `@Entity` · `@Id` · `@GeneratedValue` zorunlu
- Özellikler doğrulama anotasyonlarıyla işaretlenir
- Türkçe karakter ve uzunlukta veritabanı ile uyumsuzluk olmamalı

---

## 3. Yanıt zarfı (response standardı)

Projede zarf zaten varsa **mevcut zarf kullanılır**; tip uyuşmazlığı görülürse
JSON'u zorla yorumlamak yerine mevcut sarmalayıcıya uyulur. Zarf yoksa:

### 3.1 Başarılı

```json
{
  "status": "success",
  "message": "İşlem başarılı",
  "timestamp": "...",
  "data": { }
}
```

### 3.2 Sayfalı

```json
{
  "status": "success",
  "message": "...",
  "timestamp": "...",
  "data": [ ],
  "meta": { "pagination": { } }
}
```

### 3.3 Doğrulama hatası

```json
{
  "status": "error",
  "message": "Doğrulama hatası",
  "timestamp": "...",
  "errorCode": "VALIDATION_ERROR",
  "details": [
    { "field": "<alan>", "message": "<kullanıcı dostu mesaj>" }
  ]
}
```

### 3.4 Durum → HTTP eşlemesi

| status | Anlam | HTTP |
|---|---|---|
| `success` | İşlem başarılı | 200 |
| `warning` | Sonuç var ama tamamlanmadı | 200 |
| `error` | İstek reddedildi (doğrulama, iş kuralı) | 400 · 403 · 404 |
| `fail` | Sistem hatası | 500 |

Zarf **tipli sınıf/record** ile üretilir; `Map` ile elle kurulmaz.
Ayrıntı: [pagination-search.md](./pagination-search.md) §3 madde 14.

---

## 4. Swagger / OpenAPI

### Controller seviyesi

```java
@Tag(name = "<Module> Management", description = "...")
```

### Endpoint seviyesi

```java
@Operation(summary = "...", description = "... rol kısıtı dahil")
@ApiResponses(value = {
    @ApiResponse(responseCode = "200", description = "..."),
    @ApiResponse(responseCode = "400", description = "Geçersiz parametre"),
    @ApiResponse(responseCode = "401", description = "Unauthorized"),
    @ApiResponse(responseCode = "403", description = "Forbidden")
})
```

### Şartlar

- OpenAPI 3.0
- İstemciye dönen her alanın şeması tanımlı olmalı
- Şema alan adları yanıt zarfıyla birebir aynı olmalı
- Markdown dokümantasyonla senkron tutulur

---

## 5. API dokümantasyonu

Dosya yapısı, zorunlu içerik, koruyucu güncelleme ve şablon için:
[`rules/api-documentation-enforcement.md`](../../../rules/api-documentation-enforcement.md)

Burada yalnız ek olarak:

- Dokümantasyon **kod değişikliğinden önce** başlar, aynı iş adımında biter.
- Response örnekleri gerçek kodla birebir uyumlu olmalı; elle uydurulan örnek yazılmaz.
- Breaking change varsa migration guide zorunludur.

---

## 6. Hata yönetimi

- Yakalanan hata `GlobalExceptionHandler` üzerinden döner
- Kullanıcıya anlamlı mesaj, log'a teknik detay verilir
- Hata iç/dış ayrımı korunur; sarmalayıcı tip uyumsuzluğu "geçici çözüm" notuyla
  `knowledge-base.md`'ye yazılır