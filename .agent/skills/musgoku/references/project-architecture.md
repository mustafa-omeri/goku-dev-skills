# Proje Mimarisi ve Katman Standartları

> Genel backend mimari standardı. Projeye özel paket adı, modül listesi veya
> sürüm **burada yazılmaz** — bunlar `AGENTS.md` → *Proje Bazlı Ek Kurallar*
> bölümünde veya vault'taki mimari kararda durur.

---

## 1. Mimari prensipler

- **Feature-based modular monolith**
- Katmanlar arası **keskin sorumluluk ayrımı**
- CQRS: yazma (command) ve okuma (query) ayrımı
- DDD: aggregate root, domain event, değer nesnesi
- Modüller arası iletişim yalnız servis + DTO üzerinden

---

## 1.1 Sürüm farkları — kod yazmadan önce projenin sürümünü doğrula

Bu dosya **sürümden bağımsız** yazılmıştır. Aşağıdaki farklar kodun
derlenmesini doğrudan etkiler; `pom.xml` / `build.gradle` okunmadan kod yazma.

| Konu | Dikkat |
|---|---|
| **Ad alanı** | Spring Boot 3+ ve 4 → `jakarta.*`. Boot 2'de `javax.*` |
| **Java tabanı** | Boot 3 → Java 17+ · Boot 4 → Java 17+ (27'ye kadar doğrulanmış) |
| **Servlet kabuğu** | Boot 4 → Servlet 6.1 / Tomcat 11 tabanlı |
| **Değişen özellikler** | Boot 4'te özellik bazında kaldırılan/taşınan parçalar olabilir; sürüm yükseltmesi yapılacaksa resmî geçiş kılavuzu okunur ve geçici uyumluluk modülü kullanılıp sonra kaldırılır |
| **Kayıt (record)** | Java 16+ gerektirir; eski dil seviyesinde aynı yapı değişmez sınıfla yazılır |

**Sürüm yükseltme kuralı:** Yükseltme ayrı bir iş adımıdır. Önce derleme
hatası listesi çıkarılır, sonra tek tek giderilir; davranış değişikliği
ayrıca doğrulanır. Karar `knowledge-base.md`'ye yazılır.

---

## 2. Paket yapısı (şablon)

```
src/main/java/<group>/<artifact>/
├── <Artifact>Application.java       # giriş noktası

├── core/                            # tüm modüllerin ortak kullandığı
│   ├── security/
│   │   ├── config/                  # SecurityFilterChain, AuthenticationManager, CORS, CSRF
│   │   ├── jwt/                     # token üretme, doğrulama, filtre
│   │   └── services/                # UserDetailsService ve auth servisleri
│   ├── cache/
│   │   ├── config/                  # CacheManager, TTL, provider
│   │   └── annotations/             # özel cache anotasyonları
│   ├── exception/
│   │   ├── GlobalExceptionHandler.java
│   │   └── ErrorResponse.java
│   └── config/                      # ObjectMapper, Clock, message source, global validator

├── modules/                         # iş modülleri
│   └── <module>/
│       ├── api/                     # REST controller
│       ├── service/                 # interface + impl
│       ├── repository/              # veri erişim
│       ├── model/                   # JPA entity
│       ├── dto/                     # request/response DTO
│       ├── exception/               # modüle özel hatalar
│       └── config/                  # modüle özgü konfigürasyon

└── utils/
    ├── validators/                  # ConstraintValidator uygulamaları
    └── converters/                  # Entity ↔ DTO dönüşümü
```

Frontend tarafındaki eşdeğer yapı
[`musgoku-styling-ui.md`](../skills/musgoku-styling-ui.md) ve
[`musgoku-react-component.md`](../skills/musgoku-react-component.md) içindedir.

---

## 3. Katman sorumlulukları

### `api/` — Controller

- `@RestController`, gruplama `@RequestMapping`
- Yalnız DTO kabul eder ve döndürür
- `@Valid` ile istek doğrulama
- Her public metod için JavaDoc (bkz. `spring-boot-api.md` §1)
- ⛔ Repository'yi doğrudan autowire etmez
- Hata yönetimi `GlobalExceptionHandler`'da

### `service/` — İş mantığı

- Interface ve implementation ayrı dosyalarda
- `@Transactional` yalnız yazma işlemlerinde
- İş kuralı doğrulaması ve use-case orkestrasyonu
- Yetki/tenant kontrolü **burada** yapılır, istemciden gelen değere güvenilmez
- ⛔ Doğrudan SQL yazmaz; repository metodlarını kullanır

### `repository/` — Veri erişim

- Spring Data arayüzleri (`JpaRepository` veya eşdeğeri)
- Gerekirse `@Query` ile özel sorgu
- Sorgu optimizasyonu ve N+1 önleme sorumluluğu buradadır

### `model/` — Entity

- Yalnız veri taşır; iş mantığı barındırmaz
- İlişkilerde varsayılan `FetchType.LAZY`
- Kimliksiz değer nesneleri için `record` kullanılır; JPA entity olarak kullanılmaz

### `dto/` — Veri transferi

- Doğrulama anotasyonları buradadır
- İş mantığı veya persistence anotasyonu yoktur

### `exception/` — Modül hataları

- `RuntimeException`'dan türetilir
- `errorCode` gibi alanlar taşıyabilir

---

## 4. CQRS

| Tip | Kapsam | Örnek |
|---|---|---|
| **Command** | Veri değiştiren işlem | create, update, delete, assign |
| **Query** | Veri okuyan işlem | list, get, search, filter |

Liste ve okuma tarafı DTO projection döndürür; entity'nin tamamını çekmez.

---

## 5. Modüller arası iletişim

- Yalnız `service` + `DTO` üzerinden
- ⛔ Bir modülün domain model'ine doğrudan erişim yasak
- Çapraz modül bağımlılığı azaltılır; ortak davranış `core/` veya `utils/`'e taşınır

---

## 6. İsimlendirme

| Öğe | Kural | Örnek |
|---|---|---|
| Sınıf | PascalCase | `CategoryController` |
| Metot / değişken | camelCase | `findByCompanyId` |
| Sabit | SCREAMING_SNAKE_CASE | `DEFAULT_PAGE_SIZE` |
| Paket | tamamen küçük, çok parçalı | `<group>.<modül>.<katman>` |

---

## 7. Ortam desteği

| Ortam | Amaç |
|---|---|
| `dev` | Geliştirme |
| `test` | Test / doğrulama |
| `prod` | Üretim |

Ortama özel değerler (port, host, veritabanı adı) **kod içinde sabit yazılmaz**;
ortam değişkeni veya profil dosyasından okunur.