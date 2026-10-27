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

1. **İlk iş:** repo kökündeki `HANDOFF.md`'yi ve canlı mimari haritasını (`PROJECT_BRIEF.md`) oku.
   - Kalan işlerin sırası, kanıtlanmış tuzaklar ve ortam bilgisi `HANDOFF.md`'de; projenin dili, kütüphaneleri ve bağlayıcı kararları `PROJECT_BRIEF.md`'de yer alır.
2. ⛔ **Okunmadan** kod yazma, düzeltme yapma, test koşma, migration üretme.
3. ⛔ Dosya **yoksa veya boşsa** (yalnız başlık/şablon) → süreci **kendin devir al**:
   `git log`, `git status`, mevcut testler ve gerçek koddan durumu çıkar, sonra
   eksiksiz bir `HANDOFF.md` **yaz**. "Dosya yok, devam edemiyorum" deme —
   bu kuralın kendisi o dosyayı yeniden yaratmanı emreder.
4. ✅ **Her iş bittiğinde** ve **oturum kapanırken** `HANDOFF.md`'yi ve gerekiyorsa (stack/DB/karar değişimi) `PROJECT_BRIEF.md`'yi güncelle.
5. ⛔ `git commit` / `push` / `tag` yapma; kullanıcı açıkça istemedikçe
   değişiklikler working tree'de bırakılır.

## Güncelleme ve Raporlama Sırası

1. `knowledge-base.md`'ye bu adımda çözülen kalıcı hataları ve kararları yaz (append).
2. `HANDOFF.md`'yi güncelle (§0 tuzaklar, §1 yapılanlar, §2 kanıt metrikleri, §3 sıradaki işler, §4 kararlar, §5 ortam).
   - **Sıradaki işler kuralı (Canlı Görev Panosu, RTM & Kapsam Ayrımı):**
     * Canlı görev panosu tablosunda (`| ID | Durum | İş / Hedef | Kapsam / PRD Referansı | Hedef Sürüm |`) her zaman bir sonraki oturumun başlayacağı somut 1-3 hedef (1. ⏭️ ..., 2. ⬜ ...) listelenir.
     * ⭐ **Kurumsal ID Standardı ve Deterministik RTM Sözleşmesi:**
       1. Her iş ve gereksinim `[DOM]-[TIP]-[NO]` hiyerarşisinde sabit bir kimlik taşır (örn: `KS-US-039`, `BM-PL-001`, `OCAI-BUG-045`, `GSW-FR-001`).
       2. **Statik ID & Metadata Kuralı:** Faz ve versiyon bilgisi ID'ye kodlanamaz (`PHASE3-01`, `V2.2-A` vb. yasaktır). Faz/sürüm değişikliklerinde yalnızca `Hedef Faz` ve `Hedef Sürüm` metadata sütunları güncellenir; ID asla değişmez.
       3. ⛔ **Devir Raporunda Keyfi Harf/Madde Uydurma Yasağı:** Oturum devir raporundaki `Sıradaki İşler (Canlı Görev Panosu)` bölümünde ajanlar serbest harflerle (`A`, `B`, `C`...) veya numarasız/başlıksız listeler türetemez. Raporlanan her backlog maddesi `HANDOFF.md` veya PRD'deki sabit ID'yi (`[DOM]-PL-XXX` veya `[DOM]-US-XXX`) referans almak zorundadır.
       4. **Deprecation Kuralı:** İptal edilen veya ötelenen gereksinimler tablodan silinmez; durumu `Deprecated` veya `Deferred` yapılır, numara korunur ve boş bırakılmaz.
     * ⛔ **Sprint Bitişi ≠ Ürün/Proje Bitişi:** "Mevcut sprint / görev bitti" ile "tüm proje tamamlandı" kesinlikle birbirine karıştırılamaz! Üzerinde çalışılan sprint veya özellik bittiğinde, PRD veya Yol Haritasındaki (Backlog) sıradaki sprint/özellik canlı panoya taşınır.
     * ⛔ **Biten İşlerin Sıradaki Bölümünü Kirletmesi Yasağı:** Tamamlanan işler `Sıradaki` bölümünde `✅ BİTTİ` olarak biriktirilmez; doğrudan `§1 Yapılanlar` veya `Geçmiş Sprintler Arşivi`ne aktarılır. `Sıradaki` tablosu yalnızca geleceğe ait açık işleri barındırır.
     * `Açık iş yok — proje tamamlandı.` ifadesi **yalnızca ve yalnızca** PRD ve yol haritasındaki tüm fazlar %100 bittiğinde yazılabilir.
   - **Güncellik kanıtı kuralı:** Gerçekte ölçülmüş sayılar (test sayısı, 0 typecheck hatası, chunk kB boyutları) yazılır.
   - ⛔ **Katman Bütünlüğü & Sahte Bitti Yasağı:** Bir sprint veya özelliğin 'BİTTİ / TAMAMLANDI' olarak kaydedilebilmesi için Katman Denetimi Matrisinde (DB, View/RPC, İstemci, UI, Yönetim/Admin Formu) hiçbir '❌ Yok' veya '⚠️ Yarım' bulunmaması şarttır. Herhangi bir katmanı eksik veya TODO olan bir iş için 'BİTTİ' yazılamaz; durum açıkça 'YARIM (Eksik Katman: ...)' olarak belirtilmeli ve eksik katman §3 Sıradaki İşler tablosuna ilk sıradan kaydedilmelidir.
3. Kullanıcıya **HANDOFF & KB RAPORU** bloğunu yanıtta açıkça göster.
4. Ancak bu blok gösterildikten sonra commit onayı iste.

## ⛔ Tek Gerçek Kaynak & Mükerrer Görev Dosyası Yasağı (Anti-Task-File Proliferation)

`HANDOFF.md` projenin görev durumu, aktif adımları ve oturum köprüsü için **tek ve mutlak kaynaktır**.

1. ⛔ **Mükerrer Dosya Yasağı:** `TASK.md`, `ACTIVE_TASK.md`, `TODO.md`, `TASKS.md` veya benzeri geçici ad-hoc görev takip dosyaları **üretilmez, oluşturulmaz ve projeye eklenmez**.
2. ⛔ **Kullanıcı Talep Ettiğinde Ajanın Tutumu (Assertive & Transparent):**
   Kullanıcı sohbetteki çıktı belirsizliğinden, alışkanlıktan veya anlık güvensizlikten dolayı "bana bir TASK.md aç", "TODO.md oluştur", "aktif işleri şuraya yaz" dese dahi; ajan pasif kalarak mükerrer dosya açmaz!
   Kullanıcıya açık, kendinden emin ve dürüst bir dille şunu beyan eder:
   > *"Görev takibini ve oturum hafızasını tek bir kaynakta (`HANDOFF.md` §3 Sıradaki İşler & Aktif Görev) tutarlı şekilde yönetiyoruz. Mükerrer bir dosya (`TASK.md` vb.) oluşturmak bağlam bölünmesine yol açar; bu nedenle ayrı bir dosyaya gerek yoktur. Anlık durumu ve sıradaki adımları doğrudan `HANDOFF.md` üzerinden takip edip güncelliyorum."*
3. 🧹 **Mevcut Projedeki Artık Dosyalar:** Eğer projede daha önceden kalma bir `TASK.md` veya `TODO.md` varsa, ajan bunu fark ettiğinde içeriğindeki açık maddeleri `HANDOFF.md`'ye taşımayı ve artık dosyayı temizlemeyi (silmeyi) kullanıcıya önerir.

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
