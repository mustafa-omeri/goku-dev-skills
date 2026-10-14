# Arama Stratejileri

> Sayfalama/arama karar ağacının **arama** tarafı. Karar çerçevesi ve sayfalama için:
> [pagination-search.md](./pagination-search.md)

> Bu dosya **tek başına** okunmaz. §2.3 arama tipi, §3 değişmez kurallar ve
> §12 anti-pattern listeleri pagination-search.md içinde tanımlıdır.

## 5. Arama standardı

### 5.1 Normalizasyon (zorunlu)

Sıra: boşluk temizle → boşsa "arama yok" → azami uzunluk → **katlama**.

**Türkçe tuzağı:** locale verilmeden `toLowerCase()` çağrılırsa makinenin dil
ayarlarına göre "I" harfi "ı" olur ve veriyle eşleşmez. Unicode ayrıştırması da
noktasız i harfini i'ye çevirmediği için elle eşlenir.

Yazma tarafı (arama kolonu) ve okuma tarafı (aranan terim) **aynı** katlama
işlevini kullanmalıdır; aksi halde eşleşmez.

Kullanıcı `%` veya `_` yazdığında bunlar joker gibi davranmamalı, kaçırılmalıdır.

```java
public final class SearchTerms {
    private static final int MAX_LEN = 100;
    private SearchTerms() {}

    /** Kullanıcı girdisini arama terimine çevirir. Boşsa null döner (= filtre yok). */
    public static String normalize(String raw) {
        if (raw == null) return null;
        String s = raw.strip();
        if (s.isEmpty()) return null;
        if (s.length() > MAX_LEN) s = s.substring(0, MAX_LEN);
        return fold(s);
    }

    /**
     * Büyük/küçük harf ve Türkçe karakter duyarsız karşılaştırma için katlama.
     * Hem YAZMA tarafı (arama kolonu) hem OKUMA tarafı (aranan terim) AYNI fonksiyonu kullanır.
     * Aksan duyarlı arama isteniyorsa (ş != s) NFD adımı kaldırılır.
     */
    public static String fold(String s) {
        String t = s.replace('İ', 'i').replace('I', 'i').replace('ı', 'i')
                   .toLowerCase(Locale.ROOT);
        return Normalizer.normalize(t, Normalizer.Form.NFD).replaceAll("\\p{M}+", "");
    }

    /** LIKE joker karakterlerini kaçırır. sqlServer=true ise '[' da kaçırılır. */
    public static String escapeLike(String s, boolean sqlServer) {
        String r = s.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_");
        // Oracle'da kaçış karakterinden sonra %, _ veya kaçış dışı karakter gelirse hata verir.
        return sqlServer ? r.replace("[", "\\[") : r;
    }
}
```

`LIKE` her zaman kaçış karakteriyle kullanılır (Criteria API'de üçüncü
parametre olarak kaçış karakteri verilir). Kullanıcı `%` veya `_` yazdığında
joker gibi çalışmamalıdır.

### 5.2 Davranış

- **Global arama:** tek `search` parametresi, kodda açıkça tanımlanmış
  **aranabilir alanlarda** mantıksal VEYA ile çalışır. Tüm kolonlar taranmaz.
- **Yapısal filtreler** (durum, tarih aralığı) global aramadan ayrıdır ve VEYA ile
  değil VE ile birleşir.
- **Boş arama** tüm kayıtları döndürür.
- **Asgari uzunluk:** önek aramada 2, "içeren" aramada 3 karakter. İstemci de
  aynı kuralı uygular.
- Arama alanları ve asgari uzunluklar kod içine gömülmez, yapılandırmadan okunur.

### 5.3 Arama kolonu deseni

Aranabilir alanların katlanmış birleşimi tek bir kolonda tutulur. Böylece
sorguda büyük/küçük harf fonksiyonları kullanılmaz ve index çalışır.

- Yazma tarafı uygulama ise entity yaşam döngüsü kancasında veya alan serviste
  doldurulur.
- Veri SQL/toplu yükleme ile giriyorsa aynı mantık veritabanında tutulur
  (üretilmiş kolon veya tetikleyici). İki tarafın katlama kuralları birebir aynı olmalıdır.
- Önek arama: arama kolonu üzerine çift yönlü index; gerekirse desen operatörü eklenir.
- Mevcut veriyi doldurmak (backfill) toplu batch'lerle yapılır, tablo uzun süre kilitlenmez.

### 5.4 Veritabanına göre arama — seçim tablosu

| Veritabanı | Önek | İçeren (`%x%`) | Kelime / tam metin | Not |
|---|---|---|---|---|
| **PostgreSQL** | B-tree (`text_pattern_ops`) | **trigram + GIN** (en iyi çözüm) | vektör + GIN, `'turkish'` konfigürasyonu | Mevcut joker tabanlı standarda en az dokunan yol |
| **MySQL 8 / MariaDB** | B-tree | Index'li çözüm **yok** → arama motoru veya kabul edilmiş tarama | tam metin indeksi (InnoDB) | Trigram eşdeğeri yok |
| **Oracle** | B-tree (arama kolonu) | Index'li çözüm sınırlı → metin arama motoru veya arama motoru | Oracle Text (`CONTAINS`) | `CONTEXT` index'in senkron stratejisi bilinçli seçilir |
| **SQL Server** | B-tree | Baştaki joker index kullanmaz → arama motoru | tam metin arama (`CONTAINS`) | Tam metin yalnız önek/kelime |
| **MongoDB** | Başa çapalı desen + index | Çapasız desen index kullanmaz → Atlas Search veya arama motoru | metin index'i (koleksiyon başına 1) veya Atlas Search | Derin `skip` yavaştır; keyset kullan |
| **H2 / HSQLDB** | yalnız test | yalnız test | yalnız test | Performans/davranış doğrulaması için **kullanılmaz** — gerçek motor container ile |

Aşağıdaki alt bölümler bu seçimin uygulamasını verir. Desendir; kopyalamadan
önce sürüm ve şema adını projeye uyarla.

#### PostgreSQL

```sql
-- Bir kez (migration)
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- İçeren arama: arama kolonu zaten katlanmış olduğu için ILIKE gerekmez
CREATE INDEX CONCURRENTLY idx_item_search_trgm ON item USING gin (search_text gin_trgm_ops);

-- Önek arama
CREATE INDEX CONCURRENTLY idx_item_search_prefix ON item (search_text text_pattern_ops);

-- Sorgu
SELECT id, name, created_at
FROM item
WHERE tenant_id = :tenantId AND deleted = false
  AND search_text LIKE '%' || :escapedTerm || '%' ESCAPE '\'
ORDER BY created_at DESC, id DESC
LIMIT :size OFFSET :offset;
```

- `CREATE INDEX CONCURRENTLY` **transaction içinde çalışmaz.** Flyway'de ilgili
  migration için `executeInTransaction=false` kullan
  (bkz. §6.8). PostgreSQL kilit stratejisi gerekiyorsa
  `flyway.postgresql.transactional.lock=false` da değerlendirilir.
- Kolonu veritabanı tarafında katlamak isterseniz: `unaccent` **immutable
  değildir**, üretilmiş kolon/index için immutable bir sarmalayıcı işlev
  yazılmalıdır. Basit ve güvenli çözüm: katlamayı Java tarafında yap (§5.1).
- Kelime tabanlı arama:

```sql
ALTER TABLE doc ADD COLUMN search_tsv tsvector
  GENERATED ALWAYS AS (to_tsvector('turkish', coalesce(title,'') || ' ' || coalesce(body,''))) STORED;
CREATE INDEX CONCURRENTLY idx_doc_tsv ON doc USING gin (search_tsv);

WHERE search_tsv @@ websearch_to_tsquery('turkish', :term)
ORDER BY ts_rank(search_tsv, websearch_to_tsquery('turkish', :term)) DESC, id DESC
```

Relevance sıralaması keyset ile birlikte zordur. Bu durumda OFFSET + derinlik
sınırı veya arama motoru kullanılır.

#### MySQL 8 / MariaDB

```sql
ALTER TABLE item ADD FULLTEXT INDEX ft_item_search (name, description);

SELECT id, name FROM item
WHERE MATCH(name, description) AGAINST (:booleanTerm IN BOOLEAN MODE);
```

- `:booleanTerm` kullanıcı girdisinden üretilir. `+ - < > ( ) ~ * " @` gibi
  boolean operatörleri girdiden **temizlenir**; önek arama isteniyorsa
  terimin sonuna kendiniz `*` eklersiniz.
- InnoDB'de `innodb_ft_min_token_size` (varsayılan 3) ve durak kelime listesi
  sonuçları doğrudan etkiler. Değiştirmek index'i yeniden kurmayı gerektirir.
- Önek aramada arama kolonu üzerine normal index + `LIKE 'x%'`. Karakter
  çevirisi (collation) büyük/küçük harfe duyarsız olsa bile **Türkçe
  davranışını test et.**
- "İçeren" arama gerekiyorsa seçenekler: (a) ürün gereksinimini önek aramaya
  indirmek, (b) küçük tabloda taramayı bilinçli kabul etmek, (c) arama motoru.

#### Oracle

```sql
-- Önek: arama kolonu üzerinde normal index + LIKE 'x%'
CREATE INDEX idx_item_search ON item (search_text);

-- Kelime / önek (Oracle Text)
CREATE INDEX idx_item_name_ctx ON item (name) INDEXTYPE IS CTXSYS.CONTEXT;
SELECT id, name FROM item WHERE CONTAINS(name, :term, 1) > 0;
```

- `CONTEXT` index **transactional değildir.** Yeni/güncel kayıtlar senkronizasyon
  sonrası index'e yansır (`SYNC (ON COMMIT)`, periyodik veya manuel). Ürün
  gereksinimine göre strateji bilinçli seçilir.
- `CONTAINS` sorgu terimindeki özel karakterleri kaçır. Terimi süslü parantezle
  sarmak yaygın yöntemdir; önek için `term%`.
- Kaçış karakterinden sonra `%`, `_` ya da kaçış karakteri dışında bir karakter
  gelirse Oracle hata verir — bkz. §5.1 `escapeLike`.
- Sayfalama: 12c+ `OFFSET/FETCH`. Derinlik sınırı burada da geçerlidir.

#### SQL Server

```sql
CREATE FULLTEXT CATALOG ftc_default AS DEFAULT;
CREATE FULLTEXT INDEX ON dbo.item (name) KEY INDEX PK_item WITH CHANGE_TRACKING AUTO;

SELECT id, name FROM dbo.item WHERE CONTAINS(name, :ftTerm);   -- :ftTerm biçimi: "\"term*\"" (çift tırnaklar temizlenerek)
```

- Tam metin arama yalnızca kelime/önek içindir. Baştaki joker
  (`LIKE '%x%'`) index kullanmaz.
- `OFFSET/FETCH` için **`ORDER BY` zorunludur.**
- Önek arama için arama kolonu + normal index + `LIKE 'x%'` yeterlidir.
  `[` karakteri `LIKE` içinde özeldir → `escapeLike(..., true)`.

#### MongoDB

- Başa çapalı desen (`^term`) index kullanabilir, **çapasız desen kullanamaz.**
  Büyük/küçük harfe duyarsız arama için collation (güç 2) veya katlanmış
  `searchText` alanı kullanılır.
- `$text` index koleksiyon başına **tektir**; Türkçe için dil ayarı kontrol
  edilmelidir. Relevance veya "içeren" arama gerekiyorsa Atlas Search ya da
  arama motoru.
- `skip/limit` derinlikte OFFSET gibi yavaşlar. Keyset için `(sortKey, _id)`
  karşılaştırması kullanılır. `countDocuments` filtreli koleksiyonda pahalıdır;
  `estimatedDocumentCount` yalnızca filtre yoksa kullanılır.

### 5.5 Ne zaman ne

- Tek kolonda arama → o kolonun kendi index'i
- Birden çok kolonda global arama → tek arama kolonu (§5.3)
- Farklı tablolardaki kolonlarda arama → birleştirilmiş joker yerine arama
  kolonuna çökelme veya arama motoru

### 5.6 Arama motoru ne zaman

Şunlardan biri varsa: çok büyük veride "içeren" arama · relevance sıralaması ·
yazım hatası toleransı · öneri/otomatik tamamlama · karmaşık çok alanlı arama ·
veritabanını arama yükünden ayırma ihtiyacı.

- **Veritabanı doğruluk kaynağı olarak kalır.** Veri kuyruk deseni veya CDC
  ile aktarılır; **nihai tutarlılık kabul edilmiş olmalıdır.**
- **Yetki/kiracı filtresi** arama sorgusuna filtre olarak eklenir; yalnız
  sonuçları sonradan elemekle yetinilmez.
- **Derin sayfalama sınırı** vardır (varsayılan olarak ~10.000 belge). Bu
  sınırın ötesine inmek için kayma yerine ilerleme anahtarı ve zaman noktası
  tutarlılığı kullanılır.
- Typeahead için kenar n-gram, "içeren" için joker/n-gram alan tipi;
  Türkçe için uygun çözümleyici + aksan katlama.
- **Yeniden indeksleme** (takma ad ile kesintisiz geçiş) ve şema sürümleme
  baştan planlanır.

---

