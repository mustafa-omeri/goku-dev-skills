# RELEASE_PLAN.md — Release Planı

> Şablon. Kopyala, kök dosyalara taşı, açık kart id'lerini yaz.
> Kural: `.agent/rules/sprint-delivery-workflow.md`
> Denetim: `python .agent/skills/musgoku/scripts/check_sprint_board.py`

**Proje:** <proje adı> · **Sürüm:** v<x.y.z> · **Sprint:** S<n>
**Sorumlu:** <ad>

---

## 1. Bu Sürümde Ne Çıkıyor

| Kart | İş | Kullanıcıya ne kazandırır | Kapanış kanıtı |
|---|---|---|---|
| S<n>-01 | <iş> | <kazanım> | <ölçülebilir sonuç: "4/4 · 348 dosya byte-byte"> |

## 2. Taşınan Açık İşler (bu sürüme girmiyor)

⛔ **Kapanmamış her kart id'si bu tabloda olmak zorundadır** (kapı E10).
Kart "unutulursa" kapı kızar. Kart id'si **korunur**; yalnızca
`KANBAN.md` içindeki `sprint` alanı bir sonraki sprinte çevrilir.

| Kart | Neden bu sürüme girmedi | Yeni sprint | Risk (taşınırsa) |
|---|---|---|---|
| S<n>-03 | <gerekçe> | S<n+1> | <düşük/orta/yüksek> |

### Kapsam dışı bırakılanlar (bilinçli karar)

| Konu | Karar | Gerekçe | Ne zaman ele alınacak |
|---|---|---|---|
| <konu> | <karar> | <gerekçe> | <koşul veya tarih> |

## 3. Kalite Kapıları (bu sürüm için)

| Kapı | Komut | Beklenen sonuç |
|---|---|---|
| <yığın> | `<komut>` | `[OK]` |

## 4. Kullanıcı Test Planı

Her kart için kullanıcının yapacağı adım `KANBAN.md → test:` alanındadır.
Genel yöntem: `KULLANICI_TEST_REHBERI.md`.

| Kart | Kullanıcı ne yapar? | Göreceği sonuç |
|---|---|---|
| S<n>-01 | <adım> | <gözlenebilir çıktı> |

## 5. Risk ve Geri Dönüş

- **Geri alınabilir mi?** <evet/hayır> — nasıl?
- **Bu sürümü kim doğrular?** <ad>

## 6. Sürüm Notu (kullanıcıya ne söyleniyor)

- **Yeni:** <kullanıcıya görünen değişiklik>
- **Düzeltilen:** <davranış değişikliği>
- **Bilinmeyen davranış değişikliği:** <yoksa "yoktur" yaz — uydurma>
- **Kapsam dışı:** <bu sürümde olmayanlar>