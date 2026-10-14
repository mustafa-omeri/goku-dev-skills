# Sayfalama ve Arama — Kontrol Listeleri

> Sayfalama/arama karar ağacının **uygulama sonrası** bölümleri.
> Karar çerçevesi: [pagination-search.md](./pagination-search.md)
> Arama çözümleri: [search-strategies.md](./search-strategies.md)

## 9. Çok kullanıcılı yapı ve performans

1. **Bağlantı havuzu** boyutu bilinçli seçilir; toplam havuz veritabanı üst
   sınırını aşmaz. Çok büyük havuz veritabanını yavaşlatır.
2. **Önbellek:** tek düğüm için yerel, çok düğüm için paylaşımlı sağlayıcı.
   **Önbellek anahtarı kiracı/yetki kapsamını içerir.** Kullanıcıya özel veri
   kullanıcıdan bağımsız anahtarla önbelleğe alınmaz.
3. **Okuma kopyası** ağır liste ve arama sorgularına yönlendirilebilir; kabul
   edilebilir gecikme varsa.
4. **Hız sınırı** liste/arama ve dışa aktarma uç noktalarında ayrı ayrı uygulanır.
5. **Zaman aşımı ve devre kesici** tanımlanır.
6. **Gözlemlenebilirlik:** p95/p95 süre, yavaş sorgu, hata oranı ölçülür; hedef
   değer belirlenir ve yük testiyle doğrulanır.
7. **Eşzamanlı yazma:** OFFSET'te liste sayfaları kayabilir; keyset bunu çözer.
   Numaralı sayfada kabul edilmiş davranıştır ama istemci tekrar eden kimlikleri
   göstermemelidir.

---

## 10. Frontend kuralları

**Ortak**

- Veri çekme için bir sorgu kütüphanesi kullan; sorgu anahtarına sayfa/cursor,
  boyut, sıralama, arama ve filtreleri koy.
- **Arama gecikmesi:** yazarken her tuşta istek atma. 300–500 ms.
- **İstek iptali:** yeni arama gelince önceki istek iptal edilir; aksi halde
  eski cevap yenisinin üstüne yazılır.
- Arama veya filtre değişince sayfa başa döner.
- **Durumlar:** yükleniyor, boş sonuç, hata, "çok derin sayfa" mesajı hepsi vardır.
- Yetkilendirme hatasında merkezi akış token yeniler ve bekleyen istekleri
  **tek seferlik** yenilemeyle tekrar dener; liste isteği bu akışı atlamaz.
- Tüm kaydı çekip istemcide sayfalama/filtreleme yapma.
- Kullanıcı boyut seçebiliyorsa seçenekler sunucu üst limitini aşmaz.

**Numaralı sayfa**

- Sayfa, arama ve sıralama **URL sorgu parametrelerine** yazılır; paylaşılabilir
  ve geri tuşu doğru çalışır.
- Sayfa geçişinde önceki veri gösterilir, sonraki sayfa önden getirilir.
  Sorgu kütüphanesinin önceki veriyi tutan yer tutucusu kullanılır
  (TanStack Query v5 örneği: `placeholderData: keepPreviousData`).
- Toplam kesin değilse "10.000+" gösterilir; son sayfaya atlama kapatılır.
- Silme sonrası mevcut sayfa toplam sayfayı aşarsa son geçerli sayfaya gidilir.

**Sonsuz kaydırma / önceki-sonraki**

- Sonsuz sayfalama için sorgu kütüphanesinin sonsuz sorgu mekanizması kullanılır.
  TanStack Query v5 örneği:

```tsx
const {
  data, fetchNextPage, hasNextPage, isFetchingNextPage, status,
} = useInfiniteQuery({
  queryKey: ['items', { search, filters, sort }],
  queryFn: ({ pageParam, signal }) => fetchItems({ ...params, cursor: pageParam, signal }),
  initialPageParam: null as string | null,
  getNextPageParam: (lastPage) => lastPage.meta?.pagination?.nextCursor ?? null,
})
```

  `hasNextPage` yanlışsa yükleme durur.
- Tetikleyici gözlemci ile olur; kaydırma olayı dinlenmez.
- Gelen kayıtlar kimlik ile tekilleştirilir.
- Bellek için sayfa sayısı sınırı veya sanal liste kullanılır.
- "Önceki" gerekiyorsa istemci önceki konumları yığında tutar.
- Filtre/arama/sıralama değişince konum ve birikmiş sayfalar sıfırlanır.
- `signal` sorgu fonksiyonuna geçirilir; yeni istek geldiğinde önceki istek
  iptal edilir (yarış koşulu engellenir).

**Typeahead**

- Boyut ≤ 10, en az 2 karakter, kısa gecikme, kısa süreli önbellek, iptal
- Klavye gezinmesi ve erişilebilirlik öznitelikleri

---

## 11. Test ve doğrulama

- [ ] **Gerçek motor ile test:** üretimdeki tip ve sürüm, container ile.
      Bellekte çalışan veritabanıyla performans doğrulaması yapılmaz.
- [ ] **Veri hacmi:** en az 100 bin satırla (hedef hacmin önemli bir kısmı)
      sorgu planı alınır; index'in **kullanıldığı** doğrulanır.
- [ ] **Sorgu sayısı:** N+1 olmadığı testte doğrulanır.
- [ ] **Sınır durumları:**
  - `page=0`, negatif sayfa, `size=0`, üst limiti aşan boyut → 400
  - Beyaz listede olmayan sıralama → 400
  - Boş / yalnız boşluk içeren arama → tüm kayıtlar
  - Joker karakteri içeren arama → joker gibi çalışmaz
  - Türkçe büyük/küçük harf ve aksan eşleşmesi beklenen gibi
  - Çok uzun arama terimi → kırpılır veya 400
  - Aynı sıralama değerine sahip kayıtlarda sayfalar arası **tekrar/atlama yok**
  - Derinlik sınırı aşımı → 400
  - Cursor: son sayfa, boş sonuç, bozuk veya başka filtreye ait cursor → 400
  - Farklı kiracı/kullanıcı başkasının kaydını göremiyor
- [ ] **Yanıt sözleşmesi testi:** alan adları ve tipleri assert edilir
      (OFFSET ve CURSOR ayrı). Meta alanı içinde harita/nesne tipli alan bulunmaz.
- [ ] **Yük testi:** beklenen eşzamanlı kullanıcı sayısının üzerinde; p95 süre,
      hata oranı, havuz bekleyen bağlantı sayısı ve veritabanı yükü izlenir.
- [ ] **Frontend:** gecikme, iptal, sayfa sıfırlama, URL senkronu, boş/hata
      durumları, yetkilendirme yenileme akışı.
- [ ] **Migration:** index'ler migration ile geliyor, online oluşturuluyor,
      geri alma notu var.

---

## 12. Yapılmaması gerekenler

- Joker arama ile büyük/küçük harf fonksiyonunu birleştirmek (index'i devre dışı bırakır)
- Locale vermeden küçük/büyük harf çağırmak
- Joker karakterlerini kaçırmadan arama desenine vermek
- İstemciden gelen sıralamayı doğrudan çözümleyiciye geçirmek
- Benzersiz son anahtarı olmayan sıralama
- Sınırsız boyut veya sınırsız sayfa derinliği
- Büyük tabloda her istekte filtreli tam sayım
- Liste için varlığın tamamını çekmek, hevesli ilişkiler
- Koleksiyon ön yükleme + sayfalama birlikte
- Yetki filtresini sorgudan sonra bellekte uygulamak
- Kiracı/kullanıcı bilgisini istek parametresinden almak
- Kullanıcıya özel veriyi kullanıcıdan bağımsız önbellek anahtarıyla saklamak
- Her arama için tüm kolonlarda birleştirilmiş joker araması
- Üretimde şema otomatik güncelleme, kilitleyen index oluşturma
- Tüm veriyi çekip istemcide sayfalamak
- Dışa aktarmayı normal liste uç noktasıyla sayfa sayfa çekmek
- Arama motorunda sınırı aşan kayma ile derine inmek
- Meta/sayfalama bilgisini harita ile elle kurmak
- Sayfa nesnesini doğrudan JSON olarak döndürmek
- Sayfa numarasını hem istek parametresinden hem sayfa nesnesinden taşımak
- Her serviste aynı meta kurma kodunu kopyalamak

---

## 13. Karar Kaydı (iş sonunda çıktıya eklenecek şablon)

```markdown
## Pagination/Arama Karar Kaydı
- Modül / ekran:
- Veritabanı (tip + sürüm) ve tespit kaynağı:
- Veri hacmi (bugün / 12 ay):
- Ekran tipi: numaralı | sonsuz kaydırma | önceki-sonraki | typeahead | export
- Sayfalama: OFFSET | KEYSET  (gerekçe)
- Sayaç stratejisi: tam | sınırlı | tahmini | yok
- Arama tipi: önek | içeren | kelime/relevance | yok — aranabilir alanlar:
- Arama çözümü: (ör. arama kolonu + trigram GIN | tam metin | arama servisi)
- Sıralama beyaz listesi ve index'ler:
- Eklenen migration'lar:
- Önbellek / hız sınırı / replika kararları:
- Doğrulama: sorgu planı özeti, test edilen hacim, yük testi sonucu
- Standarttan sapmalar ve nedenleri:
- Kullanıcıya sorulan / onay bekleyen konular:
```
