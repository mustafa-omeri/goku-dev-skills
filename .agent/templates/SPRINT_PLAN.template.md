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

## Önceki Sprintfen Taşınan İşler

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