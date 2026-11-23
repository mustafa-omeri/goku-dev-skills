# Veri Katmanı: JPA, ORM, Migration ve SQL Standardı

---

## 1. Spring Data JPA

### 1.1 Repository

- Veri erişimi Spring Data arayüzleriyle sağlanır.
- ⛔ **Gereksiz `@Repository` Anotasyonu Yasağı (Unnecessary @Repository):**
  * Spring Data JPA arayüzlerinde (`JpaRepository`, `CrudRepository`, `PagingAndSortingRepository` vb. extend eden interface'lerde) `@Repository` anotasyonu **KULLANILMAZ**.
  * Spring Boot (`@EnableJpaRepositories`) bu arayüzleri otomatik tespit eder, dinamik proxy (`SimpleJpaRepository`) oluşturur, IoC konteynerine kaydeder ve `JpaRepositoryFactoryBean` ile persistence exception translation (`DataAccessException`) sağlar.
  * Bu arayüzlere `@Repository` koymak fuzulidir; SonarQube (`java:S6857`), SonarLint ve IntelliJ'de `Unnecessary @Repository` uyarısı/smell'i üretir.
  * `@Repository` anotasyonu **yalnızca** `EntityManager` veya `JdbcTemplate` ile doğrudan çalışan somut DAO / Custom Impl sınıflarında (`*CustomImpl`) veya Spring Data dışı somut sınıflarda kullanılır.
- Gerekirse `@Query` ile özel sorgu yazılır.
- İlişki ve cascade tanımları bilinçli seçilir.
- Entity'de iş mantığı bulunmaz.

### 1.2 DTO

- Katmanlar arası taşımada DTO kullanılır
- Doğrulama anotasyonları DTO'dadır
- Doğrulama mantığı iş mantığından ayrıdır
- Controller'da `@Valid` ile tetiklenir
- **Doğrulama hataları özel yanıtlarla karşılanır**; ham istisna ya da boş
  gövde dönülmez. Alan bazlı hata listesi standart zarfın `details` alanına girer
- Karmaşık kurallar için özel `ConstraintValidator` yazılır

### 1.3 Transaction

- Yazma işlemlerinde `@Transactional`
- `open-in-view` kapatılır; görünüm katmanında tembel yükleme yapılmaz
- Tembel yükleme dikkatle yönetilir (`LazyInitializationException` olmamalı)
- Bağlantı havuzu kullanılır

### 1.4 Performans

- Sayfalama ve sıralama repository metotlarında uygulanır
- **N+1 sorgu yasaktır** — testte sorgu sayısı doğrulanır
- Koleksiyon fetch join + sayfalama birlikte kullanılmaz
- Sorgular optimiz edilir, gerekirse izole projeksiyon kullanılır
- Kullanıcı girdisi sorgu metnine birleştirilmez (parametreli sorgu)

---

## 2. Şema yönetimi

- DDL üretimi (`ddl-auto=update`) prod'da kullanılmaz
- Index, kolon ve kısıt değişiklikleri **yalnız migration** ile yapılır
- Migration aracı projedeki Flyway/Liquibase hangisiyse odur
- Büyük tabloda index online/concurrent oluşturulur
- Geri alma notu migration açıklamasına yazılır
- ⛔ **DB_MIGRATIONS.md Güncelleme Zorunluluğu:** Her şema, tablo, kolon, indeks veya entity revizyonunda
  repo kökündeki `DB_MIGRATIONS.md` dosyası aynı değişiklikte güncellenir.
  Ayrıntı: [db-migration-enforcement.md](../../../rules/db-migration-enforcement.md).

---

## 3. Sayfalama — özet

Sayfalama, arama, sıralama ve cursor stratejisi için:
**[pagination-search.md](./pagination-search.md)**

Kısa hatırlatma:

- Dışarıda 1 tabanlı sayfa, içeride `PageRequest.of(page - 1, size)`
- `size` üst limiti vardır, geçersiz değer **400** döner
- Sıralama whitelist ile çözülür
- `ORDER BY` benzersiz son anahtarla biter
- Yetki filtresi sorgunun **içinde** uygulanır

---

## 4. Arama — özet

- Girdi normalize edilir: boşluk temizleme → uzunluk sınırı → locale duyarlı
  küçük harfe indirme + aksan katlama
- Türkçe karakter tuzağı: `toLowerCase()` **locale verilmeden** çağrılmaz
- `LIKE` joker karakterleri (`%`, `_`, `\`) kaçırılır
- Çok kolonlu OR yerine tek bir arama kolonu tercih edilir
- Boş arama tüm kayıtları döndürür

Ayrıntılı desenler ve veritabanına göre çözümler:
[pagination-search.md](./pagination-search.md) §4.

---

## 5. Doğrulama

| Konu | Kural |
|---|---|
| N+1 | Sorgu sayısı testte assert edilir |
| Tembel yükleme | Görünüm katmanında erişim yok |
| Index | Sıralama ve filtre alanlarının index'i var mı, sorgu planı kontrol edildi mi |
| Migration | Şema değişikliği migration dosyasında ve `DB_MIGRATIONS.md` içinde belgelendi mi |

---

## 6. Özel doğrulayıcılar

- Karmaşık kurallar için özel `ConstraintValidator` yazılır
- Doğrulama mantığı iş mantığından bağımsız tutulur
- Geçici doğrulama (`@SuppressWarnings`, `if (true)`) yazılmaz

---

## 7. SQL stil rehberi

- SQL anahtar kelimeleri küçük harfle
- Tutarlı ve açıklayıcı tanımlayıcılar
- Okunabilirlik için girinti ve boşluk
- Tarihler ISO 8601
- Karmaşık mantıkta yorum: satır içi `--`, blok `/* */`

---

## 8. Tekrarlanabilirlik

Aynı mantık servisler arasında kopyalanmaz. Ortak sorgu/specification yardımcıları
tek yerde tanımlanır ve paylaşılır.

---

## 9. Soft-Delete Mimarisi ve 4 Kritik Veri Katmanı Pratiği

> Tüm projelerde silme işlemi varsayılan olarak **Soft-Delete** (`status = 'DELETED'` veya `is_deleted = true` / `deleted_at`) olarak kurgulanır ve `POST` metoduyla çalıştırılır. Fiziksel silme (`DELETE FROM` / `deleteById`) yalnızca mimari/plan aşamasında kullanıcı tarafından açıkça onaylanmış geçici tablolarda uygulanabilir (`check_api_docs.py` `W3` kapısı ile denetlenir).

### 9.1 Fiil Tabanlı (RPC) Durum Geçişi ve Optimistic Locking (`@Version`)
Soft-delete fiziksel bir yok etme değil, durum geçişidir (`ACTIVE -> DELETED`).
- Endpoint `POST /api/v1/<resource>/{id}/cancel` veya `/archive` / `/delete` olarak tanımlanır.
- Entity üzerinde `@Version private Long version;` alanı bulundurulur; Hibernate soft-delete `UPDATE` sorgusuna `WHERE id = ? AND version = ?` kısıtını otomatik ekler.
- Zaten `DELETED` olan kayda tekrar silme isteği geldiğinde idempotent olarak `200 OK` dönülür.

### 9.2 Veritabanı Seviyesinde İzolasyon (Global Query Filters) & Native SQL Kalkanı
Geliştiricinin bir sorguda `WHERE is_deleted = false` / `status != 'DELETED'` koşulunu unutması silinmiş verinin kullanıcıya sızmasına yol açar (`check_api_docs.py` `W3` kapısı `@Entity` üzerinde global filtre varlığını denetler):

1. **Hibernate 6.4+ / Spring Data JPA (`@SQLRestriction` veya `@SoftDelete`):**
   *(Not: Eski `@Where` anotasyonu Hibernate 6.4+ ile kullanımdan kaldırılmıştır).*
   ```java
   @Entity
   @Table(name = "users")
   @SQLRestriction("status <> 'DELETED'") // Tüm Entity ve COUNT sorgularının SQL AST'sine otomatik eklenir
   public class User {
       @Id
       @GeneratedValue(strategy = GenerationType.IDENTITY)
       private Long id;

       @Enumerated(EnumType.STRING)
       @Column(nullable = false, length = 20)
       private RecordStatus status = RecordStatus.ACTIVE;

       @Version
       private Long version;
   }
   ```
2. **Prisma 6+ (`$extends` Client Extensions):**
   *(Not: Eski `prisma.$use` middleware yerine Client Extensions veya `queryFragments` kullanılır).*
   ```ts
   const prisma = new PrismaClient().$extends({
     query: {
       $allModels: {
         async $allOperations({ args, query, operation }) {
           if (operation === 'findMany' || operation === 'findFirst' || operation === 'count') {
             args.where = { ...args.where, deletedAt: null };
           }
           return query(args);
         },
       },
     },
   });
   ```
3. ⛔ **Native SQL (`nativeQuery = true`) ve Alt Sorgu Kalkanı (Kritik Tuzak):**
   `@SQLRestriction` ve ORM global filtreleri **Native SQL sorgularında ve alt sorgularda (`EXISTS`, `IN`, `JOIN` subquery) ÇALIŞMAZ!**
   - Native SQL yazıldığında hem **ana sorguda** hem de **tüm alt sorgu ve JOIN'lerde** `AND t.status != 'DELETED'` (veritabanındaki kanonik büyük harf enum değeriyle; PostgreSQL büyük/küçük harf duyarlıdır) açıkça yazılmak zorundadır.

### 9.3 Unique (Benzersiz) Kısıtlama Çakışmalarını Önleme
Kullanıcı `ali@ornek.com` adresiyle kayıt olup hesabını sildiğinde (soft-delete), aynı e-posta ile tekrar kayıt olmak isterse standart `UNIQUE(email)` kısıtlaması patlar. Tablo üzerinde tam `UNIQUE(email)` kullanılmaz; veritabanı motoruna göre şu iki çözümden biri zorunludur:

1. **Çözüm 1 — Partial Unique Index (PostgreSQL, SQL Server, SQLite, Prisma `@@index` — Altın Standart):**
   Yalnızca aktif (silinmemiş) kayıtları kapsayan koşullu benzersiz indeks oluşturulur:
   ```sql
   -- PostgreSQL (Büyük tablolarda CONCURRENTLY ile kilitlemeden)
   CREATE UNIQUE INDEX CONCURRENTLY idx_users_active_email
   ON users (email)
   WHERE status != 'DELETED'; -- veya WHERE is_deleted = false / WHERE deleted_at IS NULL
   ```
   Prisma şemasında karşılığı:
   ```prisma
   @@index([email], where: "deleted_at IS NULL", unique: true, name: "idx_users_active_email")
   ```
2. **Çözüm 2 — Aktiflik Token'ı ile Composite Unique (Partial Index Desteklemeyen Motorlar: MySQL / MariaDB):**
   - ⚠️ **SQL `NULL != NULL` Tuzağı Uyarısı:** Standart SQL'de `NULL` değerler birbirine eşit sayılmaz (`NULL != NULL`). Bu yüzden `deleted_at (nullable timestamp)` üzerinde kurulan `UNIQUE (email, deleted_at)` indeksinde `deleted_at IS NULL` iken aynı e-posta ile **birden fazla aktif kayıt** açılabilir!
   - **Doğru Çözüm:** `deleted_at` (audit için nullable timestamp) yanında `deleted_token BIGINT NOT NULL DEFAULT 0` kolonu tutulur. Aktif kayıtlarda değer `0`'dır; kayıt soft-delete yapıldığında `deleted_token = id` (veya `UNIX_TIMESTAMP()`) yazılır ve indeks `UNIQUE (email, deleted_token)` olarak kurgulanır.

### 9.4 Kaskad (İlişkili) Veri Yönetimi (`deleted_by_parent` vs `409 Conflict`)
Bir ana kayıt (Müşteri, Şirket, Kategori) soft-delete yapıldığında ona bağlı alt kayıtların (Siparişler, Ürünler, Alt Bölümler) davranışı mimari/plan aşamasında şu iki seçenekten biriyle netleştirilir:

| Seçenek | Mimari Davranış | Uygulama & Restore Kuralı |
|---|---|---|
| **Seçenek A: Kaskad Soft-Delete (`deleted_by_parent`)** | Ana kayıt silindiğinde aktif alt kayıtlar da aynı `@Transactional` içinde otomatik soft-delete yapılır. | Alt tablolarda `deleted_by_parent BOOLEAN NOT NULL DEFAULT false` kolonu tutulur. Ana kayıt silinirken dolaylı silinen alt kayıtlara `deleted_by_parent = true` yazılır. **Ana kayıt `restore` edildiğinde yalnız `deleted_by_parent = true` olan alt kayıtlar geri getirilir** (daha önce kullanıcı tarafından bireysel silinmiş alt kayıtlar yanlışlıkla canlandırılmaz). |
| **Seçenek B: Aktif Alt Kayıt Koruması (`409 Conflict`)** | Altında aktif (`status = 'ACTIVE'`) kayıt bulunan ana kaydın silinmesine izin verilmez. | Servis katmanı `existsByParentIdAndStatus(id, ACTIVE)` kontrolü yapar; aktif alt kayıt varsa işlem **`409 Conflict`** (`errorCode: "ACTIVE_CHILDREN_EXIST"`) ve kullanıcı dostu açıklamayla reddedilir. |