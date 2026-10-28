---
name: Database Migration Enforcement
description: Veritabanı şema, tablo, kolon veya entity değişikliklerinde DB_MIGRATIONS.md dosyasının güncellenmesini, geriye uyumluluk ve rollback planını zorunlu kılar.
sinif: OLCULEBILIR
kapi:
  - yigin: "Backend / Veritabanı migration"
    komut: "python .agent/skills/musgoku/scripts/check_db_migrations.py"
---

# 🗄️ Veritabanı Revizyon ve Migration Zorunluluğu

> Bu kural veritabanı veya kalıcılık katmanı içeren **tüm projelerde** (Java/Spring, Node/TS, Python, Go, Rust, .NET; Supabase, Firebase, Prisma, Drizzle, Alembic, Flyway vb.; SQL ve NoSQL) istisnasız geçerlidir. Yalnızca hiçbir veritabanı varlığı veya bağımlılığı bulunmayan salt frontend projelerinde uygulanmaz.

---

## 1. Amaç ve Kapsam

Veritabanı şeması zaman içinde geliştikçe, kod ile veritabanı arasındaki uyumsuzluklar (schema drift),
sessiz veri kayıpları ve canlı ortam kesintileri en büyük risk kaynaklarıdır.
AI kod ajanları çalıştıkları projelerde veritabanı revizyonu yaptıklarında hafıza kaybı yaşamamak,
yapılan her şema hamlesini izlenebilir kılmak ve geriye uyumluluğu garanti altına almak zorundadır.

Bu kural aşağıdaki işlemlerin tamamında ve tüm ekosistemlerde **anında** devreye girer:
- Yeni tablo, koleksiyon veya entity/model oluşturulması
- Mevcut tabloya yeni kolon eklenmesi
- Kolon tipi, boyutu, nullability (`NULL` / `NOT NULL`) veya varsayılan değerinin (`DEFAULT`) değiştirilmesi
- Kolon veya tablonun silinmesi ya da kullanımdan kaldırılması (`DEPRECATE` / `DROP`)
- İndeks (`INDEX`), benzersizlik (`UNIQUE`), yabancı anahtar (`FOREIGN KEY`) veya kısıt (`CONSTRAINT`) eklenmesi/kaldırılması
- Enum tiplerinin genişletilmesi veya değerlerinin güncellenmesi
- Veritabanı migration scripti eklenmesi veya düzenlenmesi (Supabase `supabase/migrations/*.sql`, Flyway `V...__*.sql`, Liquibase changeset, Prisma migration, Drizzle migration, Alembic revision vb.)
- Veri taşıma (data migration) ve backfill işlemleri
- Saklı yordamlar (RPC, stored procedure) ve RLS (Row Level Security) güvenlik politikalarının değiştirilmesi

---

## 2. Dosya Yapısı ve Konumu

Veritabanı revizyon kayıtları **tek bir merkezi dosyada** tutulur:

| Tercih | Dosya Yolu | Açıklama |
|---|---|---|
| **Birincil (Standart)** | `<repo-kök>/DB_MIGRATIONS.md` | Repo kökünde görünür, `HANDOFF.md` ile aynı seviyede |
| **Alternatif (Kabul)** | `<repo-kök>/docs/database/DB_MIGRATIONS.md` | Dokümantasyon dizini altında veritabanı klasörü |

- Projede dosya yoksa, `.agent/templates/DB_MIGRATIONS.template.md` şablonundan oluşturulur.
- Dosya adı ve formatı projeler arası standarttır.
- ⛔ **Eski revizyonlar ASLA silinmez.** Her yeni revizyon en üste (ters kronolojik) eklenir (append).

---

## 3. Değişiklik Sırası Protokolü

Bir veritabanı işlemi yapılırken ajan sırasıyla şu adımları işletmek **zorundadır**:

1. **Önce Şema Analizi ve Etki Değerlendirmesi:**
   - Hangi tablolar ve kolonlar etkileniyor?
   - Mevcut veriler zarar görebilir mi?
   - `NOT NULL` kolonu mevcut dolu tabloya ekleniyorsa zorunlu `DEFAULT` değeri belirlendi mi?
2. **Kodu ve Migration Dosyasını Yaz:**
   - Projenin migration aracına uygun scripti oluştur (Flyway `V...__*.sql`, Prisma `migration.sql` vb.).
   - İlgili Entity / Model sınıflarını ve DTO'ları senkronize et.
3. **`DB_MIGRATIONS.md` ve `PROJECT_BRIEF.md` Dosyalarını İkili Eşleme (Dual Mapping) ile Güncelle:**
   - Yeni revizyon kaydını `DB_MIGRATIONS.md` şablon formatına uygun olarak en üste ekle.
   - Değişiklik detay tablosunu, geriye uyumluluk notunu ve rollback scriptini eksiksiz doldur.
   - ⛔ **İkili Eşleme Zorunluluğu (Dual Mapping):** Veritabanı şeması veya altyapısı değiştiğinde canlı mimari belgesi olan `PROJECT_BRIEF.md` dosyasının §4 Veritabanı Modeli / Şema bölümünü ve frontmatter'daki `database:` listesini de eşzamanlı güncelle (Bkz: `project-brief-maintenance.md`).
4. **Test ve Doğrulama:**
   - Migration komutunu çalıştır ve başarılı uygulandığını doğrula.
   - İkili doğrulama kapılarını çalıştır:
     ```bash
     python .agent/skills/musgoku/scripts/check_db_migrations.py
     python .agent/skills/musgoku/scripts/check_project_brief.py
     ```

---

## 4. Geriye Uyumluluk ve Güvenlik İlkeleri (MUST)

- ⛔ **Dolu Tabloya Default'suz NOT NULL Kolon Yasağı:**
  Mevcut canlı tablolarda içinde veri varken `NOT NULL` kolonu `DEFAULT` değeri olmadan eklenemez.
  Önce `NULL` izinli eklenmeli veya anlamlı bir `DEFAULT` tanımlanmalıdır.
- ⛔ **Doğrudan Kolon/Tablo Silme Yasağı (Expand / Contract Deseni):**
  Canlıdaki bir kolon doğrudan silinemez veya yeniden adlandırılamaz (çift yönlü kesinti riski).
  İki aşamalı desen uygulanır:
  1. *Expand:* Yeni kolon eklenir, kod her ikisini de destekler, eski kolon `@Deprecated` işaretlenir.
  2. *Contract:* Veri senkronizasyonu tamamlandıktan sonra bir sonraki sürümde eski kolon kaldırılır.
- ⛔ **Büyük Tablolarda Kilitleme (Locking) Önlemi:**
  Büyük tablolarda indeks oluştururken veritabanına göre eşzamanlı/çevrimiçi (`CONCURRENTLY` / `ONLINE`)
  oluşturma yöntemleri tercih edilir.
- ⛔ **Geri Alma (Rollback) Planı Olmadan Revizyon Yapılamaz:**
  Her revizyon bloğu, o revizyonu tersine çeviren DDL/DML komutunu içermek zorundadır.

---

## 5. Zorunlu Revizyon Bloğu Formatı

Her revizyon girdisi şu alanları **eksiksiz** taşımak zorundadır:

```markdown
### [REV-YYYYMMDD-XX] <Kısa Başlık / Revizyon Özeti>
- **Tarih:** YYYY-MM-DD
- **Yazar / Ajan:** [Ajan veya Geliştirici Adı]
- **İşlem Türü:** [CREATE_TABLE | ADD_COLUMN | ALTER_COLUMN | DROP_COLUMN | ADD_INDEX | ADD_CONSTRAINT | DATA_MIGRATION]
- **İlgili Tablo(lar):** `tablo_adi`
- **Etkilenen Entity / Model Sınıfı:** `com.example.entity.User`
- **Migration Dosyası / Script:** `src/main/resources/db/migration/V1_2__add_status.sql`

#### Değişiklik Detay Tablosu
| Tablo | Kolon / İndeks | İşlem Türü | Eski Tip / Durum | Yeni Tip / Durum | Nullable | Default | Açıklama |
|---|---|---|---|---|---|---|---|
| `users` | `status` | ADD | - | `VARCHAR(32)` | Hayır | `'ACTIVE'` | Hesap durum bayrağı |

#### Geriye Uyumluluk ve Breaking Change Analizi
- **Mevcut Veriye Etkisi:** Mevcut kayıtlara 'ACTIVE' değeri atanacaktır, kesinti riski yoktur.
- **Breaking Change Var mı?:** Hayır.
- **Veri Dönüştürme / Backfill Gereksinimi:** Gerekmiyor.

#### Geri Alma (Rollback) Planı
```sql
ALTER TABLE users DROP COLUMN status;
```
```

---

## 6. Koruyucu Güncelleme Kuralları

Mevcut `DB_MIGRATIONS.md` dosyasını güncellerken:

- ⛔ Geçmiş revizyon bloklarını **silme veya değiştirme**.
- ✅ Yeni revizyonu daima `## 2. Revizyon Geçmişi` başlığının hemen altına ekle.
- ✅ `## 1. Proje Veritabanı Özeti` bölümündeki "Son Revizyon Numarası" ve "Son Güncelleme Tarihi" alanlarını güncelle.
- ✅ Varsa diskteki migration dosyasının (`V...__*.sql`) adını revizyonda birebir belirt.
- ✅ Veritabanı altyapısı, yeni bir tablo veya ana veri modeli değiştiğinde, kökteki canlı mimari belgesi olan `PROJECT_BRIEF.md` dosyasının §4 Veritabanı Modeli bölümü ve frontmatter'daki `database` listesi de taze tutulur (Bkz: `project-brief-maintenance.md`).

---

## 7. Kalite Kapısı ve Doğrulama

Kuralın uygulanması aşağıdaki evrensel kapı komutu ile doğrulanır:

```bash
python .agent/skills/musgoku/scripts/check_db_migrations.py
```

### Kapı Kontrolleri ve Hata Kodları

| Kod | Tür | Açıklama |
|---|---|---|
| **E1** | Hata (Exit 1) | Projede veritabanı bağımlılığı, entity/model veya migration scripti var ancak `DB_MIGRATIONS.md` bulunamadı. |
| **E2** | Hata (Exit 1) | Diskteki migration scripti `DB_MIGRATIONS.md` içinde belgelenmemiş. |
| **E3** | Hata (Exit 1) | `DB_MIGRATIONS.md` boş (<80 bayt) veya yetersiz içerik barındırıyor. |
| **E4** | Hata (Exit 1) | **Dinamik Git-Diff Koruması:** Git çalışma ağacında (staged/unstaged) veritabanı, migration veya şema dosyası değiştirildi ancak `DB_MIGRATIONS.md` aynı oturumda güncellenmedi. |
| **E5** | Hata (Exit 1) | **Dinamik Git-Diff Çift Yönlü Eşleme Koruması (Dual Mapping Guard):** Git çalışma ağacında veritabanı/migration dosyası değiştirildi ancak `PROJECT_BRIEF.md` güncellenmedi. Canlı mimari ve DB şeması eşzamanlı senkronize edilmelidir. |
| **W1** | Uyarı | Entity/Model sınıfları tespit edildi ancak dokümanda anılmamış. |
| **W2** | Uyarı | `DB_MIGRATIONS.md` içinde standart `### [REV-...]` revizyon başlığı bulunamadı. |
| **W3** | Uyarı | Kural öncesi geçmiş (legacy) migration'lar mevcut ve baseline olarak kabul edildi. |
| **W4** | Uyarı | Birden fazla `DB_MIGRATIONS.md` dosyası tespit edildi; en güncel olanı esas alındı. |

- **Brownfield / Legacy Projelerde Baseline Standardı:**
  Kural yürürlüğe girmeden önce projede mevcut olan eski migration dosyaları için `DB_MIGRATIONS.md` başlığında `Başlangıç / Baseline: 001..045` şeklinde deklarasyon yapılması yeterlidir; her eski dosya için geçmişe dönük yüzlerce blok yazma zorunluluğu yoktur. Ancak yeni eklenen veya git'te dokunulan her migration için tek tek revizyon kaydı **ZORUNLUDUR**.
- **Kapsam Dışı:** Veritabanı varlığı veya bağımlılığı bulunmayan salt frontend projelerinde kapı otomatik olarak kapsam dışı kalır (`exit 0`).

---

## 8. İhlal

Veritabanı revizyonu yapıldığı halde `DB_MIGRATIONS.md` güncellenmemişse geliştirme **tamamlanmış sayılamaz**,
kullanıcı kabul testine geçilemez ve commit onayı istenemez.

---

## Proje Bazlı Ek Kurallar

> ⛔ **Kural Ekleme ve Mükerrerlik İlkesi:**
> 1. Yukarıdaki global kurallar projeler arası standarttır ve değiştirilmez.
> 2. Projeye özgü bir veritabanı veya migration kuralı gerekirse, önce yukarıdaki global kurallarla mükerrerlik denetimi yapılır.
> 3. Yeni kural yalnızca bu başlığın altına `### <Kural Başlığı>` olarak eklenir.

### Bu Proje İçin Ek Kurallar
_(Henüz bu projeye özel ek bir kural tanımlanmamıştır.)_
