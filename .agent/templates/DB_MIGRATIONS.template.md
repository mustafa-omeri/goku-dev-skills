# DB_MIGRATIONS.md — Veritabanı Revizyon ve Şema Değişiklik Günlüğü

> Bu dosya veritabanı şeması, tablolar, kolonlar, indeksler, kısıtlar (constraints) veya
> entity modellerinde yapılan tüm değişiklikleri kronolojik olarak kayıt altına alır.
> İlgili kural: `.agent/rules/db-migration-enforcement.md`
> Bu dosya her DB işleminde **anında ve zorunlu olarak** güncellenir. Eski revizyonlar asla silinmez.

---

## 1. Proje Veritabanı Özeti
- **Veritabanı Motoru:** [MySQL / PostgreSQL / SQLite / Oracle / MongoDB vb.]
- **Migration Aracı / Yöntemi:** [Flyway / Liquibase / Prisma / TypeORM / JPA / Manuel SQL]
- **Migration Dosyaları Dizini:** [Örn: `src/main/resources/db/migration/` veya `prisma/migrations/`]
- **Son Revizyon Numarası:** [Örn: REV-20261016-01 veya V1.2.0]
- **Son Güncelleme Tarihi:** [YYYY-MM-DD]

---

## 2. Revizyon Geçmişi (Ters Kronolojik — En Yeni En Üstte)

### [REV-YYYYMMDD-01] <Kısa Başlık / Revizyon Özeti>
- **Tarih:** YYYY-MM-DD
- **Yazar / Ajan:** [Ajan veya Geliştirici Adı]
- **İşlem Türü:** [CREATE_TABLE | ADD_COLUMN | ALTER_COLUMN | DROP_COLUMN | ADD_INDEX | ADD_CONSTRAINT | DATA_MIGRATION]
- **İlgili Tablo(lar):** `[tablo_adi]`
- **Etkilenen Entity / Model Sınıfı:** `[EntityName.java / ModelName.ts]`
- **Migration Dosyası / Script:** `[src/main/resources/db/migration/V...__aciklama.sql]` (varsa)

#### Değişiklik Detay Tablosu
| Tablo | Kolon / İndeks | İşlem Türü | Eski Tip / Durum | Yeni Tip / Durum | Nullable | Default | Açıklama |
|---|---|---|---|---|---|---|---|
| `tablo_adi` | `ornek_kolon` | ADD | - | `VARCHAR(255)` | Hayır | `''` | Kolon işlevi |

#### Geriye Uyumluluk ve Breaking Change Analizi
- **Mevcut Veriye Etkisi:** [Örn: Tablo doluysa NOT NULL alan için default değer sağlandı mı? Veri kaybı riski var mı?]
- **Breaking Change Var mı?:** [Evet / Hayır — Varsa geçiş / iki aşamalı Expand/Contract stratejisi]
- **Veri Dönüştürme / Backfill Gereksinimi:** [Gerekiyor / Gerekmiyor — Varsa script veya adımlar]

#### Geri Alma (Rollback) Planı
```sql
-- Bu revizyonu geri almak için çalıştırılacak DDL/DML komutları:
ALTER TABLE tablo_adi DROP COLUMN ornek_kolon;
```

---
