---
name: Handoff Session Continuity
description: Yeni oturumda HANDOFF.md okunmadan kod yazılmasını, düzeltme yapılmamasını ve test koşulmamasını zorunlu kılar. Dosya yoksa ajanın kendisinin yazmasını emreder.
sinif: TUTUM
---

# 🔄 Oturum Köprüsü (HANDOFF) — En Yüksek Öncelik

## Konum — istisnasız

`HANDOFF.md` **yalnızca repo kökünde** bulunur.

- ⛔ `docs/`, `.agent/`, `docs/tespitler/` veya benzeri bir alt klasöre **kopyalanmaz.**
- Bir alt klasörde `HANDOFF.md` görürsen onu **okuma**, kökteki dosyayı oku.
  Alt klasördeki kopya bayat olabilir.
- Kökteki dosya yoksa aşağıdaki §3 devreye girer.

## Zorunlu akış

1. **İlk iş:** repo kökündeki `HANDOFF.md`'yi oku.
   - Kalan işlerin sırası, kanıtlanmış tuzaklar ve ortam bilgisi **yalnızca** orada durur.
2. ⛔ **Okunmadan** kod yazma, düzeltme yapma, test koşma, migration üretme.
3. ⛔ Dosya **yoksa veya boşsa** (yalnız başlık/şablon) → süreci **kendin devir al**:
   `git log`, `git status`, mevcut testler ve gerçek koddan durumu çıkar, sonra
   eksiksiz bir `HANDOFF.md` **yaz**. "Dosya yok, devam edemiyorum" deme —
   bu kuralın kendisi o dosyayı yeniden yaratmanı emreder.
4. ✅ **Her iş bittiğinde** ve **oturum kapanırken** `HANDOFF.md`'yi güncelle.
5. ⛔ `git commit` / `push` / `tag` yapma; kullanıcı açıkça istemedikçe
   değişiklikler working tree'de bırakılır.

## Güncelleme ve Raporlama Sırası

1. `knowledge-base.md`'ye bu adımda çözülen kalıcı hataları ve kararları yaz (append).
2. `HANDOFF.md`'yi güncelle (§0 tuzaklar, §1 yapılanlar, §2 kanıt metrikleri, §3 sıradaki işler, §4 kararlar, §5 ortam).
   - **Sıradaki işler kuralı:** Her iş numaralı ve tek cümlelik somut hedef olmalıdır. Açık iş kalmadıysa `Açık iş yok — proje tamamlandı.` ifadesi zorunludur.
   - **Güncellik kanıtı kuralı:** Gerçekte ölçülmüş sayılar (test sayısı, 0 typecheck hatası, chunk kB boyutları) yazılır.
3. Kullanıcıya **HANDOFF & KB RAPORU** bloğunu yanıtta açıkça göster.
4. Ancak bu blok gösterildikten sonra commit onayı iste.

Ayrıntılı format ve mükerrerlik sınırları:
[knowledge-base-management.md](./knowledge-base-management.md) ·
[.agent/AGENTS.md](../AGENTS.md)

## Bu kuralın istisnası

Bu kuralın kendisi bir uygulama hatasıdır ve düzeltilebilir. O durumda:
`HANDOFF.md` güncellenmeden, kullanıcıya **açıkça** "oturum köprüsü atlandı"
diye bildir. Gizleme.

---

## Proje Bazlı Ek Kurallar

> ⛔ **Kural Ekleme ve Mükerrerlik İlkesi:**
> 1. Yukarıdaki global kurallar projeler arası standarttır ve değiştirilmez.
> 2. Projeye özgü bir istisna veya ek oturum devir kuralı gerekirse, önce yukarıdaki global kurallarla mükerrerlik denetimi yapılır.
> 3. Yeni kural yalnızca bu başlığın altına `### <Kural Başlığı>` olarak eklenir.

### Bu Proje İçin Ek Kurallar
_(Henüz bu projeye özel ek bir kural tanımlanmamıştır.)_