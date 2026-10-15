# SPRINT_PLAN.md — Sprint Planı

> Şablon. Kopyala, kök dosyalara taşı, `## Sprint <n>` başlığını güncelle.
> Kural: `.agent/rules/sprint-delivery-workflow.md`
> Denetim: `python .agent/skills/musgoku/scripts/check_sprint_board.py`

**Proje:** <proje adı>
**Sprint:** S<n>
**Başlangıç:** <YYYY-MM-DD>
**Bitiş:** <YYYY-MM-DD>

## Sprint Hedefi

**Hedef:** <tek cümle — sprint sonunda ne gerçekten çalışır olacak?>

Bu sprint bitince kullanıcı şunu yapabiliyor olacak: <gözlenebilir sonuç>

## MVP Kapsam

Bu sprintte **teslim edilecekler** (kanban kart id'leriyle):

- S<n>-01 — <iş>
- S<n>-02 — <iş>

## Kapsam Dışı

Bilerek bu sprintte **yapılmayacaklar** — gerekçesiyle:

- <iş> — <neden şimdi değil, ne zaman>

⛔ Bir kart ne `MVP Kapsam`'da ne `Kapsam Dışı`'nda geçmiyorsa kapı uyarır
(W3). Kapsam sürüklenmesi ilk gün görünür olsun diye bu liste boş bırakılmaz.

## Uygulama Planı (Nasıl Yapılacak? - Mimari & Teknik Adımlar)

Her kart ve iş için koda başlamadan önce teknik yaklaşım ve adım adım uygulama planı:

- **S<n>-01:** <etkilenecek dosyalar, kullanılacak mimari desenler, veri modelleri, adım adım nasıl yapılacağı>
- **S<n>-02:** <etkilenecek dosyalar, bileşen sınırları, entegrasyon adımları>

## 3. Parti Araç ve Kütüphane Araştırması (Açık Kaynak Öncelikli)

Uygulama içinde veya altyapıda kullanılacak harici bağımlılıklar:

| Araç / Paket | Lisans | Açık Kaynak mı? | Tercih Gerekçesi & Dokümantasyon |
|---|---|---|---|
| `<paket-adi>` | MIT / Apache 2.0 | Evet | <neden bu paket seçildi, popülerlik, aktif bakım, repo linki> |

⛔ **Öncelik kesinlikle açık kaynak (open-source) olmalıdır.** Tescilli/kapalı araçlar ancak açık kaynak dengi yoksa ve kullanıcı onaylarsa kullanılabilir.

## Kabul Kriterleri (Acceptance Criteria / Gherkin Referansları)

- **S<n>-01:** `specs/S<n>-01.feature` (<Senaryo: Given/When/Then>)
- **S<n>-02:** `specs/S<n>-02.feature` (<Senaryo: Given/When/Then>)

## Kullanıcı İnceleme ve Onay Durumu

- **Plan Sunum Tarihi:** <YYYY-MM-DD HH:MM>
- **Kullanıcı Geri Bildirimi / Değişiklik Talepleri:** <kullanıcının revizyonları veya "değişiklik yok">
- **Kullanıcı Onayı:** [ ] Bekliyor / [ ] Onaylandı (Onay tarihi: <YYYY-MM-DD>)

⛔ **Kullanıcı onayı alınmadan koda BAŞLANAMAZ.**

## Önceki Sprintten Taşınan İşler

`RELEASE_PLAN.md`'deki her açık kart buraya taşınır; kart id'si **korunur**,
yalnızca `KANBAN.md` içindeki `sprint` alanı değişir.

- S<n-1>-0x — <iş> — neden kapanmadı

## Bu Sprintin Kapıları

| Yığın | Komut | Not |
|---|---|---|
| <yığın> | `<komut>` | <kural dosyası> |

## Riskler ve Kararlar

| # | Risk / Karar | Etki | Önlem |
|---|---|---|---|
| 1 | <risk> | <düşük/orta/yüksek> | <önlem> |

## Taşınan Açık İşler (bu sprint kapandığında)

`RELEASE_PLAN.md` bu bölümden üretilir. Kapanmayan her kart id'si
`RELEASE_PLAN.md`'de görünmek zorundadır (kapı E10).