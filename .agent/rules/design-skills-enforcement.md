---
name: Mandatory Design Skills
description: Tasarım, UI/UX ve görsel yerleşim taleplerinde canvas-design, frontend-design ve ui-ux-pro-max skillerinin birlikte okunmasını zorunlu kılar; ayrıca 12 skill'in sahiplik (tek sahip) haritasını tanımlar.
sinif: OLCULEBILIR
kapi:
  - yigin: "Tasarım / skill sahipliği"
    komut: "python .agent/skills/musgoku/scripts/check_design_skills.py"
---

# ⛔ Zorunlu Tasarım Skilleri

## 1. Zorunlu üçlü

Tasarım, UI/UX, görsel yerleşim, spacing, CSS stillendirme, bileşen veya sayfa
tasarımı (dashboard, kart, tablo, grafik, form, modal) ile ilgili **herhangi
bir talepte** aşağıdaki üç skill **birlikte** okunur ve uygulanır:

1. `canvas-design` — kompozisyon, negatif alan, derinlik, zanaat standardı
2. `frontend-design` — karakterli tipografi, renk paleti, generic "AI slop"
   kalıplarından kaçınma
3. `ui-ux-pro-max` — stil/palet/font/UX/grafik referans kütüphanesi

## 2. Zorunlu akış

1. Tasarım talebi geldiğinde **kodlamaya başlamadan** bu üç skill'i oku.
2. Generic hazır şablonlar ve sıradan renkler yerine ferah, profesyonel ve
   hiyerarşik görsel dil uygula.
3. Yanıtın başlangıcında bu üç skill'in ve kullanılan MCP araçlarının
   **aktif devrede olduğunu** açıkça belirt.

## 3. Sahiplik haritası — her konunun tek sahibi vardır

Tasarım alanına giren 12 skill'in sorumluluk sınırı şudur. **Bir konuyu iki
skill sahiplenmez.** Çakışma şüphesinde bu tabloya bak ve doğru olanı aç.

| Konu | Sahip skill |
|------|-------------|
| Ölçüsüz görsel sanat (poster, manifesto, `.png`/`.pdf`), font seti | `canvas-design` |
| Estetik yönelim, AI-slop kaçınma, UI kodu disiplini | `frontend-design` |
| Stil / palet / UX / stack önerisi (aranabilir veri) | `ui-ux-pro-max` |
| Hazır renk-font paleti (artifact teması) | `theme-factory` |
| Token üretimi (primitive → semantic → component) | `design-system` |
| Token'ı Tailwind/shadcn tarafına bağlama, stil uygulaması | `ui-styling` |
| Marka içeriği (ton, görsel kimlik, mesaj, varlık) | `brand` |
| Doküman yazma süreci (PRD, spec, karar) | `doc-coauthoring` |
| Sunum **stratejisi, metni, düzeni** | `slides` |
| Sunum/slayt **üretimi** (HTML render + token denetimi) | `design-system` |
| Sabit px ölçülü banner / kapak / reklam görseli | `banner-design` |
| Logo & CIP **brief'i**, sosyal medya görseli akışı, yönlendirme | `design` |
| IDE benzeri uygulama arayüzü | `web-ide-ux-architect` (kapsam dışı ilan eder) |

**Kapsam dışı ilan edilen:** `web-ide-ux-architect`

**Tipik hatalar ve doğrusu:**

- Sunum isteği → içerik için `slides`, render için `design-system`. İkisini birden
  "sahip" gösterme.
- "Poster yap" → `canvas-design`; "web hero banner yap" → `banner-design`
  (ölçüsüz sanat ≠ sabit px reklam).
- Palet sorusu → hazır tema `theme-factory`, ürüne özel palet `ui-ux-pro-max`,
  token `design-system`. Üçü farklı iş yapar.
- Marka dokümanı → içerik `brand`, yazma süreci `doc-coauthoring`.

## 4. Kapsam

Bu kural yalnız **görsel ve yapısal** tasarım işlerinde geçerlidir.
Yalnız renk değişikliği, tek bir metin düzeltmesi veya logik hatası için
üç skill'in tamamını okumak gerekmez — bu durumda hangisinin devrede olduğunu
belirtip geç.

`brand`, `slides`, `banner-design`, `design`, `doc-coauthoring` üçlüye **dahil
değildir**; bunlar UI kodu üretmez, çıktı/strateji üretir. Onlar kendi
kapsam sınırı bölümünde tanımlıdır.

---

## Proje Bazlı Ek Kurallar

> ⛔ **Kural Ekleme ve Mükerrerlik İlkesi:**
> 1. Yukarıdaki global kurallar projeler arası standarttır ve değiştirilmez.
> 2. Projeye özgü bir tasarım/UI kuralı gerekirse, önce yukarıdaki global kurallarla mükerrerlik denetimi yapılır.
> 3. Yeni kural yalnızca bu başlığın altına `### <Kural Başlığı>` olarak eklenir.

### Bu Proje İçin Ek Kurallar
_(Henüz bu projeye özel ek bir kural tanımlanmamıştır.)_