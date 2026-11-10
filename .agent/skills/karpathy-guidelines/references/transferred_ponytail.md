# Cerrahi Entegrasyon Referansı: DietrichGebert/ponytail (Ponytail 5.3)

> **Kaynak Repo:** `https://github.com/dietrichgebert/ponytail`  
> **Entegrasyon Tarihi:** 2026-11-10  
> **Hedef Yetenekler:** `.agent/skills/karpathy-guidelines/` & `.agent/skills/code-review/`  
> **Çekirdek Felsefe:** "He says nothing. He writes one line. It works." — Güvenlik, veri kaybı önleme ve erişilebilirlikten asla taviz vermeden, problemi çözen en küçük tam değişikliği üretme disiplini.

---

## 1. 6-Basamaklı Yeniden Kullanım Merdiveni (The 6-Rung Reuse Ladder)

Ajan yeni bir işlev, yardımcı fonksiyon veya bileşen yazmaya başlamadan önce problemi ve dokunduğu tüm çağrıcıları (`callers`, `tests`, `fixtures`, `exports`) derinlemesine okur. Kod yazarken aşağıdaki basamakların **ilk çalışanında durur**:

```
[1. Basamak: Var olması gerekiyor mu?]
   └─ İstenmeyen opsiyonlar, spekülatif esneklik ve aşırı soyutlamalar elenir.
[2. Basamak: Bu kod tabanında zaten var mı?]
   └─ Mevcut helper, servis veya bileşen, projenin mevcut desenleriyle yeniden kullanılır.
[3. Basamak: Standart kütüphane veya yerel platform özelliği mi?]
   └─ Stdlib veya web standartları kullanılır. (İstisna: UI katmanında DESIGN.md ve ui-polish sözleşmesi önceliklidir).
[4. Basamak: Kurulu bir bağımlılık yapıyor mu?]
   └─ Birkaç satırlık iş için asla yeni paket kurulmaz; kurulu kütüphane varsa kullanılır.
[5. Basamak: İlk bakışta anlaşılan tek bir satır olabilir mi?]
   └─ Kolay okunan, açık tek satırlık çözüm tercih edilir (anlaşılması zor code-golf değil).
[6. Basamak: Yalnızca o zaman minimum çalışan kod + 1 kanıt testi]
   └─ Dal, döngü, ayrıştırıcı, para veya güvenlik içeren mantık için en küçük çalışan kod ve 1 küçük test bırakılır.
```

> ⚠️ **Tasarım & UI İstisnası (Zanaat Tabanı Koruması):**
> Ponytail'in *"native `<input type="date">` kullan, sıfırdan UI yazma"* yaklaşımı backend ve araç kodlarında geçerlidir. Ancak kullanıcı yüzlü web arayüzlerinde `DESIGN.md`, `ui-polish` ve `frontend-design` Zanaat Tabanı (Craft Floor) kuralları esastır; estetik kaliteden ödün verilmez.

---

## 2. Bilinçli Kısayol Sözleşmesi & Borç Defteri (`shortcut:` & `/ponytail-debt`)

Bir implementasyonda bilinçli olarak basit bir çözüm tercih edildiğinde (ör. Redis yerine şimdilik bellek içi Map), bu tercih kod içinde şu katı formatla işaretlenir:

```typescript
// shortcut: <bilinen sınır / tavan (ceiling)>, <yükseltme tetikleyicisi (upgrade trigger)>
// Örnek:
// shortcut: in-memory map up to 1,000 active users, migrate to Redis when multi-instance deployed
```

### Kurallar:
1. **İki Parametre Zorunluluğu:** Her `shortcut:` yorumu hem mevcut sınırını hem de ne zaman yükseltileceğini (`when to upgrade`) belirtmek zorundadır.
2. **`no-trigger` Çürüme Riski (Rot Risk):** Yükseltme tetikleyicisi yazılmamış kısayollar ("shortcut: şimdilik böyle") teknik borç defterinde çürüme riski olarak bayraklanır.
3. **Kütük Tarama Komutu:**
   ```bash
   git grep --no-index --exclude-standard -nE '(#|//|/[*]) ?(shortcut|ponytail):'
   ```
4. **Code-Review Muafiyeti:** Beklenen yük henüz yorumda belirtilen tavanı aşmamışsa, `shortcut:` ile belgelenmiş yapılar `code-review` tarafından sahte hata (false positive) olarak raporlanmaz; Rejection Log tablosuna dahil edilir.

---

## 3. Nöbetçi Kıdemli Geliştirici Kod İncelemesi (Review & Audit Protocol)

*"Review like the senior dev who gets paged when it breaks."*

### 3.1. Diff-Dışı Çağrıcı (Untouched Callers) Taraması
- Bir fonksiyonun imzası, dönüş tipi veya davranışı değiştiğinde; yalnızca `git diff` dosyaları değil, o fonksiyonu çağıran tüm dokunulmamış dosyalar (`git grep`) taranıp doğrulanmalıdır.

### 3.2. Beklenen Yük (Expected Load) Varsayımı
- İnceleme ajanı projenin README, docker-compose veya mimari belgelerinden beklenen yükü tespit eder (tek kişilik lokal CLI/script mi, yoksa eşzamanlı binlerce istek alan çoklu process mi?).
- Yarış durumları (check-then-write race), bellek sızıntıları ve `O(n^2)` algoritmalar bu varsayılan yüke göre değerlendirilir ve raporda varsayılan yük açıkça belirtilir.

### 3.3. 4-Parçalı Somut Bulgu Formatı
Her bulgu genel/soyut tavsiyelerden ("consider refactoring...") arındırılır ve şu 4 kısa cümleden oluşur:
```markdown
[No]. **[Kısa Başlık]** (`[dosya:satır]`)
   - **What this is (Ne yapıyor):** [Kodun mevcut görevi]
   - **Problem (Hangi durumda kırılıyor):** [Hangi somut veri veya durumda hata verdiği]
   - **Fix (Cerrahi çözüm):** [En küçük çalışan düzeltme — tercihen kod silen]
   - **If we skip it (Atlanırsa ne olur):** [Düzeltilmezse canlıda yaşanacak somut arıza]
```

### 3.4. İşe Göre Bölme (Split by Job)
- Fonksiyonlar asla keyfi satır sayısına göre parçalanıp tek kullanımlık anlamsız passthrough yardımcılarına bölünmez; **yalnızca birden fazla bağımsız iş yapıyorsa işe göre (`by job`)** bölünür.

---

## 4. Yanıt Sonu Şeffaflık İmzası (`Not checked / Risk Footer`)

Ajan kritik bir kod değişikliği veya inceleme tamamladığında, yanıtın sonuna 1-2 satırlık şeffaflık notu düşer:
```markdown
- **Kontrol Edilmeyen / Kapsam Dışı:** [İncelenemeyen veya çalıştırılamayan parça]
- **Kullanıcının Bilmesi Gereken Risk:** [Canlıya alırken dikkat edilmesi gereken sınır]
```

---

## 5. Kod Yeniden Kullanım Metriği (Reuse %)

Mevcut projelerde yeni kod üretilirken uydurma yardımcılar yazmak yerine projenin kendi kodlarının yeniden kullanılma başarısı:
$$\text{Reuse \%} = \frac{\text{Kullanılan Mevcut Fonksiyon/Tip Sayısı}}{\text{Kullanılan Mevcut} + \text{Eklenen Yeni Tanımlar}} \times 100$$
Yeni kod tabanlarında gereksiz abstraction yerine mevcut kütüphanelerin çağrılması teşvik edilir.
