# Veri Katmanı: JPA, ORM, Migration ve SQL Standardı

---

## 1. Spring Data JPA

### 1.1 Repository

- Veri erişimi Spring Data arayüzleriyle
- Gerekirse `@Query` ile özel sorgu
- İlişki ve cascade tanımları bilinçli seçilir
- Entity'de iş mantığı bulunmaz

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
| Migration | Şema değişikliği migration dosyasında mı |

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