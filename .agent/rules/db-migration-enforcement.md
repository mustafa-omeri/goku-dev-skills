---
name: Database Migration Enforcement
description: Veritabanı şema, tablo, kolon veya entity değişikliklerinde DB_MIGRATIONS.md dosyasının güncellenmesini, geriye uyumluluk ve rollback planını zorunlu kılar.
sinif: OLCULEBILIR
kapi:
  - yigin: "Backend / Veritabanı migration"
    komut: "python .agent/skills/musgoku/scripts/check_db_migrations.py"
---

# 🗄️ Veritabanı Revizyon ve Migration Zorunluluğu

> Bu kural veritabanı içeren tüm backend projelerinde geçerlidir. Frontend-only projelerde uygulanmaz.

---

## 1. Amaç ve Kapsam

Veritabanı şeması zaman içinde geliştikçe, kod ile veritabanı arasındaki uyumsuzluklar (schema drift),
sessiz veri kayıpları ve canlı ortam kesintileri en büyük risk kaynaklarıdır.
AI kod ajanları çalıştıkları projelerde veritabanı revizyonu yaptıklarında hafıza kaybı yaşamamak,
yapılan her şema hamlesini izlenebilir kılmak ve geriye uyumluluğu garanti altına almak zorundadır.

Bu kural aşağıdaki işlemlerin tamamında **anında** devreye girer:
- Yeni tablo veya entity oluşturulması
- Mevcut tabloya yeni kolon eklenmesi
- Kolon tipi, boyutu, nullability (`NULL` / `NOT NULL`) veya varsayılan değerinin (`DEFAULT`) değiştirilmesi
- Kolon veya tablonun silinmesi ya da kullanımdan kaldırılması (`DEPRECATE` / `DROP`)
- İndeks (`INDEX`), benzersizlik (`UNIQUE`), yabancı anahtar (`FOREIGN KEY`) veya kısıt (`CONSTRAINT`) eklenmesi/kaldırılması
- Enum tiplerinin genişletilmesi veya değerlerinin güncellenmesi
- Veritabanı migration scripti eklenmesi (Flyway `V...__*.sql`, Liquibase changeset, Prisma migration, TypeORM vb.)
- Veri taşıma (data migration) ve backfill işlemleri

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
3. **`DB_MIGRATIONS.md` Dosyasını Aynı Değişiklikte Güncelle:**
   - Yeni revizyon kaydını şablon formatına uygun olarak en üste ekle.
   - Değişiklik detay tablosunu, geriye uyumluluk notunu ve rollback scriptini eksiksiz doldur.
4. **Test ve Doğrulama:**
   - Migration komutunu çalıştır ve başarılı uygulandığını doğrula.
   - Doğrulama kapısını çalıştır:
     `python .agent/skills/musgoku/scripts/check_db_migrations.py`

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

---

## 7. Kalite Kapısı ve Doğrulama

Kuralın uygulanması aşağıdaki kapı komutu ile doğrulanır:

```bash
python .agent/skills/musgoku/scripts/check_db_migrations.py
```

- Projede entity veya migration scripti varsa ve `DB_MIGRATIONS.md` yoksa kapı **hata verir (E1)**.
- Diskte migration scripti olup `DB_MIGRATIONS.md` içinde belgelenmemişse kapı **hata verir (E2)**.
- Dosya boşsa veya revizyon başlığı içermiyorsa kapı **hata verir (E3)**.
- Veritabanı varlığı olmayan frontend projelerinde kapı otomatik olarak **kapsam dışı kalır (exit 0)**.

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
