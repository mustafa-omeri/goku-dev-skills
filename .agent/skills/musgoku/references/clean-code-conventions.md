# Clean Code ve Kodlama Sözleşmeleri

---

## 1. İsimlendirme

| Öğe | Kural | Örnek |
|---|---|---|
| Sınıf | PascalCase | `CategoryController` |
| Metot / değişken | camelCase | `findByCompanyId` |
| Sabit | SCREAMING_SNAKE_CASE | `DEFAULT_PAGE_SIZE` |
| Paket | küçük harf, çok parçalı | `<group>.<modül>.<katman>` |
| Boolean | okunur cümle biçiminde ön ek olmadan (`enabled`, `isActive` — projede hangisi varsa onu kullan) | |
| Test | üretilen şeyi tanımlayan ad | `shouldReturnEmptyPageWhenSearchMissing` |

## 2. Boyut sınırları

| Birim | Sınır | Aşılırsa |
|---|---|---|
| Java dosyası | 300 satır | Modül veya katman bölünür |
| React/TSX bileşeni | 200 satır | Alt bileşenlere veya hook'a çıkarılır |
| Metot | ~40 satır | Ara adımlara bölünür |
| Parametre sayısı | 3-4 | Nesne geçirilir |

## 3. Temel prensipler

- **SOLID** · **DRY** · **KISS** · **YAGNI** · **OWASP**
- Yüksek kohezyon, düşük bağlantı
- Sabit yerine enum
- Kullanılmayan kod bırakma → [`rules/no-unused-code.md`](../../../rules/no-unused-code.md)
- Yorum yazmak yerine ismiyle anlat; yorum **neden** sorusunu yanıtlar, ne'yi değil
- Ölü kod "ileride lazım olur" gerekçesiyle bırakılmaz; gerekçe kaydedilirse de
  teslim edilen kapsamın dışına alınır

## 4. Düzenlenmiş kod kalitesi kuralları

### Kesinlikle yapılacak

- Metotun **amacını** belirten bir yorum/başlık
- Boş şablon, geçici iskelet, `TODO` bırakılmış kod çalışma zamanına konmaz
- Üretim ve geliştirme ortamında sahte veri üretilmez
- Ortam değişkeni dosyası onaysız değiştirilmez
- Geçici çözüm ("geçici" kod, susturma, sahte encoder, devre dışı bırakılmış test)
  yorumla değil, `knowledge-base.md` kaydıyla işaretlenir

### Kesinlikle yapılmayacak

- Kullanılmayan import / değişken / dosya / export bırakmak
- Yorum satırlarıyla ölü kod gizlemek
- Aynı mantığı iki yerde kopyalamak
- İş mantığını entity içine koymak
- Hata yutma (boş `catch`) — en az loglanır
- Erken çıkış yerine iç içe koşullu zincir kurmak
- Aynı değerin birden fazlı kopyasını ("türetilmiş durum") taşımak —
  tek kaynak tutulur, kalan yerlerden okunur

### Yapılabilir ama dikkat

| Konu | Not |
|---|---|
| Testi devre dışı bırakmak | Çözüm değil, ertelemedir. KB'ye yazılır ve geçici olarak işaretlenir |
| Sınıf genişletmek | Önce yeni modül/sınıf ayrımı düşünülür |
| Refactoring | Ayrı adımda yapılır, davranış değişmez; hata ayıklama ile karıştırılmaz |

---

## 5. Async ve hata yönetimi

- Async işlemde `Promise.then()` zinciri yerine `async/await` kullanılır
- Tüm method mantığı `try/catch` kapsamındadır
- Yakalanan hata merkezî işleyiciye bırakılır; kullanıcıya anlamlı mesaj,
  log'a teknik detay verilir
- Asenkron işlemde hata yutulmaz; zincir sonunda ele alınır

## 6. Yorum ve dokümantasyon

| Ne | Nerede |
|---|---|
| **Ne** yaptığı | İsimden ve tip belirtisinden okunmalı; gereksiz yorum yazma |
| **Neden** öyle yapıldı | Kod yanında kısa yorum — kural, istisna, geçici çözüm gerekçesi |
| Genel yapı | Modül düzeyinde özet dosya |
| API | Modül dokümanı + Swagger (bkz. `rules/api-documentation-enforcement.md`) |
| Karar | `knowledge-base.md` |

## 7. Geliştirme sırası

1. Görevi analiz et, etkilenen katmanı belirle
2. İlgili skill/referansı oku
3. Planı açıkça yaz, kodla
4. Kalite kapılarını çalıştır
5. `knowledge-base.md` + `HANDOFF.md` güncelle
6. Doğrulanmış sonucu raporla