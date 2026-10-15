# KANBAN.md — Sprint Kanbanı

> Şablon. Kopyala, kök dosyalara taşı, kart id'lerini güncelle.
> Kural: `.agent/rules/sprint-delivery-workflow.md`
> Denetim: `python .agent/skills/musgoku/scripts/check_sprint_board.py`

**Proje:** <proje adı> · **Sprint:** S<n> · **WIP limiti:** 3

⛔ Dört sütun sabittir; adı değiştirilemez. Kart başlığı kipi
`### S<sprint>-<no> · başlık`. Yedi alanın tamamı dolu olmalı.
`Yapılıyor`'da en fazla **3** kart.

---

## Bekliyor

### S<n>-01 · <tek cümle iş tanımı>
| alan | değer |
|---|---|
| durum | Bekliyor |
| oncelik | P1 |
| sprint | S<n> |
| gherkin | specs/S<n>-01.feature#senaryo-adi |
| kapi | python .agent/skills/musgoku/scripts/check_sprint_board.py |
| test | <yazılacak> |
| risk | orta |

---

## Yapılıyor

<!-- WIP limiti 3. Aşarsa yeni kart başlatma, önce bitir. -->

---

## Sınırdı

---

## Yapıldı

<!-- Buraya kart girerken `test:` alanı gerçek bir kullanıcı adımı olmalı.
     "test edildi" / "çalışıyor" bir adım değildir. -->

### S<n>-00 · Tamamlanmış örnek kart
| alan | değer |
|---|---|
| durum | Yapıldı |
| oncelik | P1 |
| sprint | S<n> |
| gherkin | specs/S<n>-00.feature#ornek-senaryo |
| kapi | python .agent/skills/musgoku/scripts/check_sprint_board.py |
| test | Kullanıcı `python .agent/skills/musgoku/scripts/check_sprint_board.py` çalıştırır, `SONUC: ... · [OK]` satırını görür |
| risk | düşük |