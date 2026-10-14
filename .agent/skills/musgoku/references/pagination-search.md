# Pagination, Sıralama ve Arama Standardı

> Bu dosya, listenin, aramanın ve sayfalamanın **karar ağacıdır.**
> Kod yazmadan önce tespit → karar → uygulama sırasıyla izlenir.

---

## 0. Bu doküman nasıl kullanılır

1. **Projeyi tespit et** (§1)
2. **Kararları ver** (§2)
3. **Uygula:** §3 değişmez kurallar her zaman geçerlidir.
   Sayfalama için §4, index için §6, yanıt için §7, backend desenleri için §8.
   Arama için **[search-strategies.md](./search-strategies.md)**,
   iş sonu listeleri için **[pagination-checklists.md](./pagination-checklists.md)**.
4. Tespit edemediğin bilgi varsa **tahmin etme, sor** (§2.4)
5. İş bitince **Karar Kaydı**'nı doldurup çıktıya ekle
   (→ `pagination-checklists.md` §13)

### Bu konu üç dosyaya bölünmüştür

| Dosya | İçerik |
|---|---|
| **bu dosya** | tespit · karar matrisi · değişmez kurallar · sayfalama · index · yanıt · backend desenleri |
| [search-strategies.md](./search-strategies.md) | normalizasyon · arama kolonu · veritabanına göre arama çözümleri · arama motoru |
| [pagination-checklists.md](./pagination-checklists.md) | performans · frontend · test · anti-pattern · karar kaydı |

Satır sınırı aşılmaz; tek yüklemede okunabilir kalsın diye bölünmüştür.

> Kod parçaları birer **desendir.** Kopyalamadan önce projenin framework sürümüne,
> dil sürümüne ve paket yapısına uyarla.
> Projede bu standarttan farklı çalışan mevcut kod varsa **kendiliğinden yeniden
> yazma.** Farkı raporla, kullanıcıdan onay al. Yeni yazılan kod bu standarda uyar.

---

## 1. Proje tespiti

| Ne | Nereye bak |
|---|---|
| Veritabanı tipi | `application*.yml` içinde veri kaynağı adresi; sürücü bağımlılığı; NoSQL başlangıcı |
| Veritabanı sürümü | container tanımı, test imajı, dağıtım dokümanı |
| Veri erişimi | JPA · JdbcTemplate · jOOQ · MyBatis · Document |
| Şema yönetimi | Flyway (`db/migration`) · Liquibase (`db/changelog`) |
| Framework / dil sürümü | `pom.xml` · `build.gradle` · `package.json` |
| Liste ekranı tipi | Numaralı sayfa · sonsuz kaydırma · önceki/sonraki · typeahead |
| Veri hacmi | Bugün ve **12 ay sonrası** tahmin |

Bellekte çalışan test veritabanı performans doğrulaması için **kullanılmaz**;
gerçek motor container ile ayağa kaldırılır.

---

## 2. Karar matrisi

### 2.1 Veri hacmine göre başlangıç stratejisi

| Satır sayısı (12 ay) | Sayfalama | Arama |
|---|---|---|
| < 10 bin | OFFSET (`Page`) | `LIKE '%x%'` kabul edilebilir; yine de normalize + kaçış zorunlu |
| 10 bin – 1 milyon | OFFSET (derinlik sınırı + sınırlı sayaç) **veya** keyset | Index destekli arama **zorunlu** |
| > 1 milyon | **Keyset**. Numaralı sayfa şartsa derinlik sınırı + zorunlu filtre | Index destekli; "içeren" veya relevance gerekiyorsa arama motoru |

### 2.2 Ekran tipine göre strateji

| Ekran tipi | Sayfalama | Toplam sayı | Arama |
|---|---|---|---|
| Numaralı sayfa (yönetim tablosu, rapor) | OFFSET + derinlik sınırı | tam veya sınırlı | §5 |
| Sonsuz kaydırma / "daha fazla" | **Keyset (cursor)** | yok, yalnız `hasNext` | §5 |
| Önceki / sonraki (numarasız) | Keyset; geri dönüş için istemci cursor yığını tutar | yok | §5 |
| Typeahead / combobox | İlk N kayıt (≤ 10), sayfa yok | yok | önek arama, en az 2 karakter, kısa önbellek |
| Dışa aktarma / toplu indirme | Sayfalama **kullanılmaz** — akış veya asenkron iş | yok | aynı filtreler, ayrı uç nokta, ayrı yetki, ayrı hız sınırı |

### 2.3 Arama tipi

| İhtiyaç | Örnek | Çözüm ailesi |
|---|---|---|
| Önek | `ahm` → `Ahmet` | B-tree index + `LIKE 'x%'` (normalize kolonda) |
| İçeren | `met` → `Ahmet` | Trigram; yoksa arama motoru veya kabul edilmiş tarama maliyeti |
| Kelime / relevance | "kırmızı elbise" | tam metin araması veya arama motoru |
| Yazım hatası toleransı, öneri | `elbsie` → `elbise` | arama motoru |

### 2.4 Kullanıcıya sorulacak sorular

1. Üretimde hangi veritabanı ve hangi sürüm?
2. Bu ekran numaralı sayfa mı, sonsuz kaydırma mı, typeahead mi?
3. Tablonun bugünkü ve 12 ay sonraki tahmini satır sayısı?
4. Arama önek mi, içeren mi, kelime mi? Hangi kolonlarda?
5. Kullanıcı rastgele sayfaya atlamalı mı?
6. Çok kiracılı yapı veya satır bazlı yetki var mı?
7. Aynı anda tahmini eşzamanlı kullanıcı sayısı?

---

## 3. Değişmez kurallar

1. **Parametre sözleşmesi:** `page` (1 tabanlı, ≥ 1) · `size` (varsayılan 20,
   üst limit config'den) · `sort` · `search` · `cursor` (yalnız keyset).
2. **Doğrulama açık olmalı.** Framework'ün sayfalayıcı çözümleyicisi geçersiz
   değerlerde hata vermeden varsayılana düşebilir. Kendi istek DTO'nu doğrulama
   ile kullan ve geçersiz değerde **400** dön.
3. **Sıralama whitelist ile.** İstemciden gelen `sort`, kodda tanımlı alan
   eşlemesiyle çözülür. Whitelist dışı → 400. İlişki yollarına sıralama izni verilmez.
   Whitelist'teki her alan index'li olmalıdır.
4. **Deterministik sıralama:** `ORDER BY` her zaman benzersiz son anahtarla biter.
5. **Yetki ve kiracı filtresi sorgunun içinde, kimlikten gelir.** Sorgu parametresi
   veya gövdesinden alınmaz. Sayfalama sonrası bellekte uygulanmaz.
6. **Silinmiş/pasif kayıt filtresi** her sorguda uygulanır ve index'e dahil edilir.
7. **Liste için DTO projeksiyonu** — listenin ihtiyacı olmayan alanlar çekilmez.
8. **N+1 yasak.** Testte sorgu sayısı doğrulanır. Koleksiyon fetch join +
   sayfalama birlikte kullanılmaz; önce kimlikler sayfalanır, ilişkiler ikinci
   sorguda çekilir.
9. **Parametreli sorgu.** Kullanıcı girdisi sorgu metnine birleştirilmez; dinamik
   kısım yalnız whitelist'ten gelir.
10. **Sorgu zaman aşımı** tanımlanır; liste ve arama uç noktaları ölçülür.
11. **Görünüm katmanında tembel yükleme yok** (açık görünüm kapalı).
12. **Yavaş sorgu görünürlüğü** açılır; liste uç noktalarına süre ölçer eklenir.
13. **Tekrarlanabilirlik:** sayfalama/arama mantığı ortak yapıda tutulur.
14. **Yanıt ve meta tipli olur.** `Map` ile meta kurulmaz — alan adı yazımı
    derleyicide yakalanmaz, `null` değer sessizce düşer, şema kararsızlaşır.
15. **Çerçeve veri tipleri API sözleşmesine sızmaz.** Sayfa nesneleri
    servis/repository sınırında kalır; çıkış her zaman kendi zarfındadır.
    Sayfa bilgisi tek kaynaktan okunur, istek parametresinden ayrıca taşınmaz.

---

## 4. Sayfalama stratejisi

### 4.1 OFFSET (numaralı sayfa)

- Dışarıda 1 tabanlı, içeride 0 tabanlı; dönüşüm tek yerde.
- **Derinlik sınırı:** sayfa × boyut sınırı aşarsa **400** dön ve daraltmayı iste.
  Derin OFFSET, atlanan satırları da okumak demektir.
- Sıralama ve filtre kolonlarında uygun index şarttır.

### 4.2 Keyset / cursor

```sql
-- Genişletilmiş karşılaştırma (tüm anahtarlar aynı yönde)
WHERE (created_at < :lastCreatedAt OR (created_at = :lastCreatedAt AND id < :lastId))
ORDER BY created_at DESC, id DESC
```

Kurallar:

- **Boyut + 1 kayıt çek**, fazla gelen kayıt `hasNext = true` demektir. Fazlalık
  yanıta konmaz, ayrı sayaç sorgusu çalıştırılmaz.
- **Cursor opaktır:** sıralama anahtarları + kimlik, Base64URL ile kodlanır.
  İstemci içeriğine güvenilmez; sunucu tip, uzunluk ve sıralama beyaz listesini doğrular.
- **Cursor sıralamaya ve filtreye bağlıdır:** sıralama + filtre özeti cursor'a girer;
  uyuşmazsa 400.
- Sıralama kolonları boş değer alamaz; boşsa sabit değere çevrilir.
- Tüm sıralama anahtarları aynı yönde olmalıdır.
- İstemci rastgele sayfaya atlayamaz; geri dönüş istemcide cursor yığını tutar.
- Çerçevenin hazır keyset desteği sürüme bağlıdır → **§8.3.1**. Kullanmadan
  önce sürüm desteğini ve üretilen SQL'i doğrula. Destek yoksa §8.3.2'deki elle
  yazılmış desen kullanılır.

### 4.3 Toplam kayıt sayısı

| Durum | Strateji |
|---|---|
| Keyset / sonsuz kaydırma | Sayaç yok. `size+1` ile `hasNext` |
| Küçük tablo | Tam sayaç |
| Büyük tablo + numaralı sayfa | **Sınırlı sayaç:** tavan değerine kadar say; aşılırsa `totalElementsExact = false` |
| Büçük tablo, filtre yok | Tahmini sayaç veya kısa ömürlü önbellek |
| 2. sayfa ve sonrası | `includeTotal=false` ile sayaç atlanabilir |

### 4.4 Veritabanına göre sözdizimi

- PostgreSQL / MySQL / MariaDB: `LIMIT n OFFSET m`
- Oracle 12c+: `OFFSET m ROWS FETCH NEXT n ROWS ONLY` (öncesi iç içe sorgu)
- SQL Server 2012+: `ORDER BY ... OFFSET m ROWS FETCH NEXT n ROWS ONLY` — **`ORDER BY` zorunlu**

Bu not yalnız elle yazılan yerel sorgular içindir; sorgu üreticisi dialect'i kendisi çözer.

---


---

## 5. Arama standardı

Arama tarafı — normalizasyon, arama kolonu deseni, veritabanına göre çözümler
ve arama motoru kararı — **ayrı dosyada**:

**-> [search-strategies.md](./search-strategies.md)**

Konu başlıkları: `normalize` · `fold` · `escapeLike` · arama kolonu deseni ·
veritabanına göre arama çözümleri · arama motoru kararı.

`data-layer.md` §3 ile birlikte okunur.

## 6. Index ve migration kuralları

1. **Sıralama + filtre index'i:** eşitlik filtreleri önce, sıralama kolonları
   sonra, benzersiz anahtar en sonda.
2. **Silinmiş/pasif kayıt:** kısmi veya filtreli index değerlendirilir.
3. **Kapsayan index:** liste projeksiyonu dar ise yazma maliyetine göre değerlendirilir.
4. **Her sıralama alanı index'li olmalıdır.** Index'i olmayan kolon beyaz listeye girmez.
5. **Index online oluşturulur.** Büyük tabloda kilitleyen DDL çalıştırılmaz.
6. **Her index değişikliği migration dosyasındadır** ve sorgu planı çıktısı
   değişiklik açıklamasına eklenir.
7. Gereksiz veya örtüşen index biriktirilmez; her index bir yazma maliyetidir.
8. **Index'i kilitlemeden oluştur.** `CREATE INDEX CONCURRENTLY`
   (PostgreSQL) transaction içinde çalışmaz → Flyway'de o script için
   `executeInTransaction=false` kullanılır. PostgreSQL'de Flyway'ın kilit
   stratejisi de gerekirse oturum düzeyine alınabilir
   (`flyway.postgresql.transactional.lock=false`).
   Diğer motorların online DDL karşılıkları: MySQL online DDL ·
   Oracle `ONLINE` · SQL Server `WITH (ONLINE = ON)` (sürüme bağlı).

---

## 7. Yanıt formatı

Mevcut zarf korunur. Zaman damgası UTC ve offset'li ISO 8601'dir; saat dilimsiz
yerel zaman tipi kullanılmaz.

**OFFSET:**

```json
{
  "status": "success",
  "message": "...",
  "data": [ ],
  "meta": {
    "timestamp": "...",
    "pagination": {
      "mode": "OFFSET",
      "currentPage": 1,
      "totalPages": 3,
      "totalElements": 26,
      "totalElementsExact": true,
      "pageSize": 10,
      "hasNext": true,
      "hasPrevious": false
    }
  }
}
```

- Sınırlı sayaç aşıldıysa toplam alanı tavan değerini taşır ve
  `totalElementsExact` yanlış olur; istemci "10.000+" gösterir.
- `includeTotal=false` isteğinde toplam alanları yanıtta bulunmaz.

**CURSOR:**

```json
"pagination": {
  "mode": "CURSOR",
  "pageSize": 20,
  "hasNext": true,
  "nextCursor": "..."
}
```

Toplam sayı alanları **yoktur.** Son sayfada `hasNext = false` ve cursor boştur.

Hatalarda (geçersiz sayfa/boyut/sıralama/cursor, derinlik aşımı, kısa arama
terimi) mevcut hata zarfı kullanılır ve mesaj kullanıcının ne yapacağını söyler.

---

## 8. Uygulama desenleri (backend)

### 8.0 Yanıt tipleri — ortak pakette bir kez

```java
@JsonInclude(JsonInclude.Include.NON_NULL)
public record PaginationMeta(
        String mode,
        Integer currentPage,
        Integer totalPages,
        Long totalElements,
        Boolean totalElementsExact,
        int pageSize,
        boolean hasNext,
        Boolean hasPrevious,
        String nextCursor) {

    /** Sayfa nesnesi tek kaynaktır: numara, boyut ve toplam buradan okunur. */
    public static PaginationMeta offset(Page<?> p, boolean totalExact) {
        return new PaginationMeta("OFFSET", p.getNumber() + 1, p.getTotalPages(),
                p.getTotalElements(), totalExact, p.getSize(),
                p.hasNext(), p.hasPrevious(), null);
    }

    public static PaginationMeta cursor(int pageSize, boolean hasNext, String nextCursor) {
        return new PaginationMeta("CURSOR", null, null, null, null,
                pageSize, hasNext, null, nextCursor);
    }
}

public record ApiMeta(Instant timestamp, PaginationMeta pagination) { }

public record ApiResponse<T>(String status, String message, T data, ApiMeta meta) { }
```

- Meta'ya alan eklemek **yalnız bu record'u** değiştirir; servislere dokunulmaz.
- Dil/çerçeve sürümünde kayıt yoksa aynı yapı değişmez sınıf + aynı
  alanlar ile yazılır.

### 8.1 İstek DTO'su

```java
public record PageQuery(
        @Min(1) Integer page,
        @Min(1) @Max(100) Integer size,   // üst limit yapılandırmayla tutarlı olmalı
        String sort,                       // beyaz listeyle çözülür
        @Size(max = 100) String search,
        String cursor,
        Boolean includeTotal) {

    public int pageOrDefault()  { return page == null ? 1 : page; }
    public int sizeOrDefault()  { return size == null ? 20 : size; }
}
```

Controller'da doğrulama açık olmalı; derinlik kontrolü servis katmanında:

```java
if ((long) q.pageOrDefault() * q.sizeOrDefault() > maxOffset) {
    throw new BadRequestException("Çok derin sayfa. Lütfen filtre veya arama ile sonuçları daraltın.");
}
```

### 8.2 Ortak specification

```java
public final class SearchSpecs {
    public static <T> Specification<T> contains(String term, String searchTextField, boolean sqlServer) {
        if (term == null) return (root, q, cb) -> cb.conjunction();
        String pattern = "%" + SearchTerms.escapeLike(term, sqlServer) + "%";
        return (root, q, cb) -> cb.like(root.get(searchTextField), pattern, '\\');
    }
    public static <T> Specification<T> prefix(String term, String searchTextField, boolean sqlServer) {
        if (term == null) return (root, q, cb) -> cb.conjunction();
        String pattern = SearchTerms.escapeLike(term, sqlServer) + "%";
        return (root, q, cb) -> cb.like(root.get(searchTextField), pattern, '\\');
    }
}
```

Küçük/büyük harf sarmalayıcı kullanılmaz; arama kolonu zaten katlanmıştır.
Kiracı/yetki filtresi istemci verisinden değil kimlikten okunur.

### 8.3 Cursor (keyset) sorgusu

#### 8.3.1 Çerçevenin hazır kaydırma API'si — önce bunu dene

Spring Data, keyset kaydırmayı hazır sunar. **Sürüm desteğini ve üretilen
sorguyu doğrulamadan** elle sorguya geçme.

```java
// İlk pencere
Window<Item> first = repository.findBy(spec,
        q -> q.limit(size).sortBy(sort).scroll(ScrollPosition.keyset()));
boolean hasNext = first.hasNext();

// Sonraki pencere: görünür son kaydın konumundan devam
Window<Item> next = repository.findBy(spec,
        q -> q.limit(size).sortBy(sort).scroll(first.positionAt(0)));
```

- Terminal metot: `.scroll(ScrollPosition)` → `Window<T>` döner.
- Konum türleri: offset tabanlı ve **keyset** (`ScrollPosition.keyset()`).
- Specification akışında ayrıca `page(...)` ve `slice(...)` terminal metotları vardır.
- **Bilinen sınırlar (kullanmadan önce kontrol et):**
  - Metot adından türetilen (string-based) sorgu metotlarında kaydırma **henüz desteklenmiyor.**
  - `@Procedure` ile tanımlı depolanan prosedürlerde kaydırma desteklenmiyor.
  - Derleme öncesi (AOT) repository üretiminde `ScrollPosition` alan metotları
    desteklenmiyor; anahtar döndüğünde elle sorgu desenine düş.
- Sürümde yoksa §8.3.2'deki elle yazılmış desen kullanılır.

#### 8.3.2 Elle yazılmış desen

`:param is null or ...` kalıbından kaçın — planlama ve parametre tipi sorunları
çıkarabilir. İlk sayfa ve sonraki sayfa için **iki ayrı sorgu** yaz:

```java
@Query("""
    select new com.example.ItemListDto(i.id, i.name, i.createdAt)
    from Item i
    where i.tenantId = :tenantId and i.deleted = false
    order by i.createdAt desc, i.id desc
    """)
List<ItemListDto> findFirst(@Param("tenantId") Long tenantId, Pageable limit);

@Query("""
    select new com.example.ItemListDto(i.id, i.name, i.createdAt)
    from Item i
    where i.tenantId = :tenantId and i.deleted = false
      and (i.createdAt < :lastCreatedAt or (i.createdAt = :lastCreatedAt and i.id < :lastId))
    order by i.createdAt desc, i.id desc
    """)
List<ItemListDto> findAfter(@Param("tenantId") Long tenantId,
                            @Param("lastCreatedAt") Instant lastCreatedAt,
                            @Param("lastId") Long lastId,
                            Pageable limit);
```

Çağıran taraf `boyut + 1` ister → fazla kayıt `hasNext = true` demektir → fazlayı
atıp `nextCursor`'u son görünür kayıttan üretir:

```java
// return ApiResponse.success("...", visibleItems, PaginationMeta.cursor(size, hasNext, nextCursor));
```

`List` döndüren sorgu otomatik sayaç çalıştırmaz.

### 8.4 Diğer

- İlişki ön yükleme yalnız tekil ilişkilerde sayfalamayla birlikte güvenlidir.
  Koleksiyonlar için kimlik-önce deseni kullanılır.
- Yerel (native) sorgu kullanılıyorsa sıralama beyaz listesi ve parametre
  bağlama kuralları aynen geçerlidir.
- Dışa aktarma: akış + veri boyutu ipucu veya asenkron iş. Tüm veri belleğe alınmaz.
- Sınırlı sayaç için `List`/`Slice` döndüren sorgu + ayrı sayaç metodu kullanılır;
  `Page` her istekte ayrı `COUNT` çalıştırır.

---

## 9–13. Performans, frontend, test, anti-pattern ve karar kaydı

Bu bölümler **uygulama sonrasında** ve iş bitiminde kullanılır:

**-> [pagination-checklists.md](./pagination-checklists.md)**

Konu başlıkları: çok kullanıcılı yapı ve performans · frontend kuralları ·
test ve doğrulama kontrol listesi · yapılmaması gerekenler · karar kaydı şablonu.

