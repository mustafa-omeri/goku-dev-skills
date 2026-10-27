# HANDOFF — Yeni Oturum Buradan Başlasın

> Bu dosya tek bir amaçla var: **yeni oturum, bu oturumun yaptıklarını bilsin,
> aynı hatalara düşmesin, kaldığı yerden devam etsin.**
>
> Güncel: **[YYYY-MM-DD]** · Ajan: **[Ajan Adı]**
> PRD (varsa): `docs/<feature>-prd.md` · Karar kayıtları: `knowledge-base.md`

> ⚠️ Bu dosya **yalnız repo kökünde** tutulur. Başka bir konuma kopyalanmaz.
> Kurallar: `.agent/rules/handoff-session-continuity.md` ·
> içerik sınırları: `.agent/rules/knowledge-base-management.md`

---

## 0. ⛔ ÖNCE BUNU OKU — Bu Projede Düşülen ve Kanıtlanmış Tuzaklar

> Bu bölüm **yalnız bu projeye** aittir. Tahminle doldurma; oturumda bizzat
> karşılaşılan ve çözülen somut hataları yaz.

| # | Kural & Tuzak | Somut Neden / Ne Yaşandı | Doğru Yol |
|---|---|---|---|
| 1 | _(yoksa "yeni yok" yaz)_ | | |

---

## 1. Bu Oturumda Yapılanlar (Özet)

- **Kod:** [değişen dosyalar ve davranış]
- **Test:** [çalıştırılan komutlar ve gerçek sonuç]
- **Dokümantasyon:** [güncellenen modül dokümanları]
- **Doğrulanmayan:** [çalıştırılamayan kapılar — sessizce geçilmez]

---

## 2. Güncellik Kanıtı

| Ölçüm | Değer | Nasıl ölçüldü |
|---|---|---|
| Test sayısı / sonuç | | `pnpm test` / `mvn test` çıktısı |
| Derleme / tip kontrolü | | `npx tsc --noEmit` / `mvn test-compile` |
| Migration sayısı | | DB migration log / migration dosya sayısı |
| Bundle & Chunk boyutu (frontend) | [En büyük 3 chunk: X kB, Y kB, Z kB — >500kB warning yok] | `pnpm build` terminal boyutu |

> Buradaki sayılar **tahmin değil, bizzat terminal çıktısından ölçülen** değerlerdir.


### Katman Denetimi Matrisi (Full-Stack Vertical Slice Audit)

> ⛔ Bir özellik veya sprint teslimatında tüm katmanlar doğrulanmadan "BİTTİ" yazılamaz. Eksik katman varsa durum "YARIM" işaretlenir ve §3 Sıradaki İşler tablosuna eklenir.

| Katman | Durum | Kanıt |
|---|---|---|
| 1. DB / Şema / Migration | [✅ Var / ❌ Yok / ➖ Kapsam Dışı] | [migration dosya adı veya salt UI gerekçesi] |
| 2. Backend / View / RPC | [✅ Var / ❌ Yok / ➖ Kapsam Dışı] | [view / RPC adı veya sorgu] |
| 3. API & İstemci Entegrasyonu | [✅ Var / ❌ Yok] | [hook / servis / DTO] |
| 4. UI / UX & Eylemler | [✅ Var / ❌ Yok] | [bileşen & event RPC / feedback] |
| 5. Yönetim / Giriş Formu (Döngü Kapanışı) | [✅ Var / ❌ Yok] | [form / ekran veya veri kaynağı] |

---

## 3. ⏭️ BURADAN DEVAM ET

### Önce doğrula (hemen koşturulacak komutlar)

```bash
[doğrulama komutu 1]
[doğrulama komutu 2]
```

### Sıradaki işler (Canlı Görev Panosu & RTM İzlenebilirlik Matrisi)

> 💡 Bu bölüm projenin canlı görev panosudur. Ayrı bir `TASK.md` veya `TODO.md` açılmaz; tüm aktif ve sıradaki adımlar burada takip edilir.
> ⛔ **Sprint Bitişi ≠ Proje Bitişi:** Mevcut sprint bittiğinde PRD/Yol Haritasındaki sıradaki sprinti buraya ekleyin. Biten işleri bu tabloda tutmayın, §1'e aktarın. Yalnızca tüm PRD fazları %100 bittiğinde "Açık iş yok — proje tamamlandı." yazılabilir.
>
> ⭐ **Kurumsal ID Standardı (Statik ID & Metadata Ayrımı):**
> 1. Her iş `[DOM]-[TIP]-[NO]` formatında sabit kimlik taşır (örn: `[DOM]-US-001`, `[DOM]-PL-001`, `[DOM]-BUG-001`).
> 2. ID'ye asla faz veya sürüm gömülmez (`PHASE3-01` yasaktır). Faz/sürüm değişikliğinde yalnızca `Hedef Faz` ve `Hedef Sürüm` sütunları güncellenir.
> 3. İptal edilen veya ertelenen işler silinmez; durum `Deprecated` veya `Deferred` yapılır.

#### 🎯 Aktif Sprint / Anlık Görev Panosu (WIP Maks 3)
| ID | Durum | İş / Hedef | Kapsam / PRD Referansı | Hedef Sürüm |
|---|---|---|---|---|
| [DOM]-US-001 | ⏭️ | _(bir sonraki oturumun ilk somut hedefi)_ | _(Sprint / Modül / PRD §X)_ | vX.Y.Z |
| [DOM]-TASK-002 | ⬜ | _(sıradaki iş)_ | _(Sprint / Modül / PRD §X)_ | vX.Y.Z |
| [DOM]-BUG-003 | ⬜ | _(sıradaki iş)_ | _(Hata / Regresyon Ref)_ | vX.Y.Z |

#### 📌 Gelecek Fazlar & Parking Lot Yol Haritası (Product Roadmap Backlog)
| Gereksinim ID | Açıklama | Hedef Faz | Hedef Sürüm | PRD / Kaynak Ref | Durum |
|---|---|---|---|---|---|
| [DOM]-PL-001 | _(Gelecek faz gereksinimi / özellik)_ | Phase 2+ | vX.Y.0 | `docs/*-prd.md §X` | ⬜ Bekliyor |
| [DOM]-PL-002 | _(Gelecek faz gereksinimi / özellik)_ | Phase 3+ | vX.Y.0 | `docs/*-prd.md §X` | ⬜ Bekliyor |

**YALNIZCA tüm PRD/ürün fazları %100 bittiğinde şunu yazın:**
`Açık iş yok — proje tamamlandı.`

### Sağlık durumu — dikkat gerektiren noktalar

- [Kırılgan dosya / sahte geçen test riski / bekleyen karar]

### Nasıl Test Edilir (kullanıcı)

> Her oturum ve teslimat sonunda kullanıcının çıktıyı nasıl test edeceği
> adım adım yazılır (ve `KULLANICI_TEST_REHBERI.md` güncellenir; minor rötüş/dahili değişikliklerde mevcut senaryolar referans verilir).
1. `[kullanıcı komutu veya tarayıcı URL'si]` → `[beklenen sonuç]`
2. `[bozma veya sınır testi]` → `[beklenen hata veya davranış]`

---

## 4. Bu Projede Alınan Kararlar

> Karar **gerekçesi** `knowledge-base.md`'dedir. Burada yalnız başlık ve
> referans yazılır; gerekçeyi kopyalama.

| Karar | Tarih | `knowledge-base.md` referansı |
|---|---|---|
| _(yeni karar veya "yeni yok")_ | | |

---

## 5. Ortam Bilgisi

> Yalnız **gerçekten doğrulanmış** değerleri yaz. Şüpheliyken boş bırak ve
> kullanıcıya sor.

| Parametre | Değer | Not |
|---|---|---|
| Uygulama portu | | |
| Veritabanı / port | | |
| Test hesapları | | _(gizli bilgi gerekiyorsa buraya yazma, kullanıcıdan al)_ |
| Git kuralı | ⛔ Onaysız commit/push/tag yapılmaz | |

---

## 6. Alan Modeli ve Kritik Sözleşmeler

> Bu projede en sık yanlış anlaşılan davranışlar. Genel kurallar burada
> tekrarlanmaz — yalnız proje sözleşmesi.

- [Ör. silme standardı, mutasyon HTTP metodu, rol matrisi]

---

## Güncelleme kaydı

| Tarih | Ajan | Ne güncellendi |
|---|---|---|
| YYYY-MM-DD | | |