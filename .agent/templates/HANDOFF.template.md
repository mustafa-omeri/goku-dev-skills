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

---

## 3. ⏭️ BURADAN DEVAM ET

### Önce doğrula (hemen koşturulacak komutlar)

```bash
[doğrulama komutu 1]
[doğrulama komutu 2]
```

### Sıradaki işler

| # | Durum | İş |
|---|---|---|
| 1 | ⏭️ | _(bir sonraki oturumun ilk somut hedefi)_ |
| 2 | ⬜ | _(sıradaki iş)_ |
| 3 | ⬜ | _(sıradaki iş)_ |

**Açık iş kalmadıysa şunu yaz ve boş bırakma:**
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