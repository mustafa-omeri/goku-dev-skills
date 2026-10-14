# Design Routing Guide

Hangi tasarım skill'i hangi işin sahibi.

## Skill envanteri

| Skill | Sahibi olduğu konu | Ana dosyalar |
|-------|-------------------|--------------|
| `design` | Yönlendirme + logo/CIP brief + sosyal görsel | SKILL.md + 3 script + 11 reference |
| `brand` | Marka içeriği: ton, görsel kimlik, mesaj, varlık | SKILL.md + 11 reference + 4 script |
| `design-system` | Token üretimi + sunum render/doğrulama | SKILL.md + 7 reference + 9 script |
| `ui-styling` | Tailwind/shadcn kod katmanı | SKILL.md + 6 reference + 2 script |
| `ui-ux-pro-max` | Aranabilir stil/palet/UX/stack veritabanı | SKILL.md + veri + `search.py` |
| `frontend-design` | Estetik yönelim, AI-slop kaçınma, kod disiplini | SKILL.md + `themes/` |
| `theme-factory` | Hazır renk/font paleti (artifact teması) | SKILL.md + 10 tema |
| `canvas-design` | Ölçüsüz görsel sanat (poster, manifesto) | SKILL.md + font seti |
| `slides` | Sunum stratejisi, metni, düzeni | SKILL.md + 5 reference |
| `banner-design` | Sabit px ölçülü banner/kapak/reklam | SKILL.md + 1 reference |
| `doc-coauthoring` | Doküman yazma süreci | SKILL.md |
| `web-ide-ux-architect` | IDE benzeri arayüz (kapsam dışı ilan eder) | SKILL.md |

## İş tipine göre yönlendirme

### Marka kimliği → `brand`
- Marka renkleri ve tipografi tanımı
- Logo kullanım kuralları
- Marka tonu ve kişilik
- Varlık organize etme, doğrulama, onay
- Mesaj çerçevesi
- Marka tutarlılık denetimi

### Token sistemi → `design-system`
- Token JSON'u oluşturma
- CSS değişkeni üretme
- Bileşen spesifikasyonu
- Token'ları Tailwind config'e bağlama
- Kodda token kullanımını doğrulama
- Durum ve varyant dokümantasyonu

### Uygulama → `ui-styling`
- shadcn/ui bileşeni ekleme
- Tailwind sınıflarıyla stil verme
- Dark mode uygulama
- Responsive düzen kurma
- Erişilebilir bileşen kurma

### Estetik yön → `frontend-design` + `ui-ux-pro-max`
- "Bu sayfa neden amatör görünüyor?" → `frontend-design`
- "Bu ürün için hangi stil/palet?" → `ui-ux-pro-max`
- Hazır palet seçimi → `theme-factory`

### Logo brief → `design` (Logo bölümü)
- Logo brief üretimi (55+ stil, 30 palet, 25 sektör)
- Stil / palet / sektör araması
- Brief'i harici görsel aracına aktarma

⛔ Bu paket logo **görseli üretmez**; brief üretir.

### Kurumsal kimlik (CIP) → `design` (CIP bölümü)
- Teslimat listesi brief'i (50+ teslimat)
- Sektör/stil analizi
- Mockup hazırlama (manuel veya harici araç)
- Mockup'lardan HTML sunum

### Sunum → `slides` + `design-system`
- Strateji, metin, düzen, sıralama → `slides`
- HTML render + token doğrulama → `design-system`

### Banner → `banner-design`
- Sosyal medya kapakları (Facebook, X, LinkedIn, YouTube, Instagram)
- Reklam banner'ları (Google Ads, Meta Ads)
- Web hero banner ve header
- Baskı banner ve kapakları
- 22 art-direction stili

### İkon → `ui-ux-pro-max` (seçim) + `design` (rehber)
- Hazır ikon seti önerisi → `ui-ux-pro-max --domain icons`
- Özel SVG yazım rehberi → `design/references/icon-design.md`

### Görsel sanat → `canvas-design`
- Poster, manifesto, ölçüsüz kompozisyon
- Font seti (`canvas-fonts/`)

### Doküman → `doc-coauthoring`
- PRD, spec, karar dokümanı yazma süreci
- Marka dokümanının **içeriği** `brand`'de, **yazılış süreci** burada

## Soru tipine göre

| Soru | Skill |
|------|-------|
| "Bu rengin ne olmalı?" | `theme-factory` (hazır palet) / `ui-ux-pro-max` (ürüne göre palet) |
| "X için token nasıl yaparım?" | `design-system` |
| "Buton bileşenini nasıl kurarım?" | `ui-styling` |
| "Bu tasarım markaya uygun mu?" | `brand` |
| "Dark mode nasıl eklenir?" | `ui-styling` |
| "Logomun stili ne olmalı?" | `design` (Logo Brief) |
| "Kartvizit mockup brief'i çıkar" | `design` (CIP Brief) |
| "Pitch deck hazırla" | `slides` + `design-system` |
| "Facebook kapak görseli yap" | `banner-design` |
| "Google reklam banner'ı yap" | `banner-design` |
| "Web sitesi hero görseli yap" | `banner-design` |
| "Ayar ikonu lazım" | `ui-ux-pro-max --domain icons` |
| "Poster yap" | `canvas-design` |
| "Bu sayfa amatör görünüyor" | `frontend-design` |

## Çoklu skill akışları

### Yeni proje kurulumu
```
1. brand → Kimliği tanımla (renk, tipografi, ton)
2. design-system → Token'ları üret (primitive → semantic → component)
3. ui-styling → Uygula (Tailwind yapılandır, bileşenleri ekle)
4. frontend-design → Estetik kontrol (slop temizle)
```

### Tasarım sistemi göçü
```
1. brand → Mevcut kimliği denetle
2. design-system → Token mimarisine oturt
3. ui-styling → Kodda hardcoded değerleri değiştir
```

### Bileşen üretimi
```
1. design-system → Şekillere/varyantlara bak
2. ui-styling → shadcn/ui + Tailwind ile kur
3. frontend-design → Estetik kontrol
```

### Marka paketi
```
1. design → Logo brief
2. design → CIP brief + mockup hazırlama
3. brand → Marka dokümanı (docs/brand-guidelines.md)
4. design-system → Token'ları brand'den türet
5. slides + design-system → Sunum
```

## Bağımlılık zinciri

```
brand (marka kaynağı)
    ↓ renk, tipografi
design-system (token)
    ↓ token, şekil
ui-styling (bileşen)
    ↓ bileşen
Uygulama kodu
```

Yan kollar: `ui-ux-pro-max` (öneri) → `design-system` / `theme-factory` (palet)
→ `slides` → `design-system` (render)

## Hızlı komutlar

**Marka:**
```bash
node ../brand/scripts/inject-brand-context.cjs
node ../brand/scripts/sync-brand-to-tokens.cjs
node ../brand/scripts/validate-asset.cjs <path>
```

**Token:**
```bash
node ../design-system/scripts/generate-tokens.cjs -c tokens.json
node ../design-system/scripts/validate-tokens.cjs -d src/
```

**Öneri (stil/palet/UX):**
```bash
python ../ui-ux-pro-max/scripts/search.py "<sorgu>" --design-system
python ../ui-ux-pro-max/scripts/search.py "<sorgu>" --domain ux
```

**Bileşen:**
```bash
npx shadcn@latest add button card input
```

**Brief:**
```bash
python ../design/scripts/logo/search.py "tech startup" --design-brief -p "Marka"
python ../design/scripts/cip/search.py "consulting" --cip-brief -b "Marka"
```

## Ne zaman tek skill yeter

| Gereken | Skill |
|---------|-------|
| Sadece marka tonu/guideline | `brand` |
| Sadece token | `design-system` |
| Sadece Tailwind/shadcn | `ui-styling` |
| Sadece stil önerisi | `ui-ux-pro-max` |
| Sadece hazır tema | `theme-factory` |
| Sadece poster | `canvas-design` |
| Sadece banner | `banner-design` |
| Sadece deck metni | `slides` |

`design` yalnızca iş **birden fazla alanı** kapsadığında veya brief gerektiğinde
devreye girer.
