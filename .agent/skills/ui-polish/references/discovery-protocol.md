# F1 — Proje Keşfi ve Baseline Çıkarma Protokolü (Discovery & Baseline Extraction)

Bu protokol, `/ui-polish` çalıştırıldığında ezbere karar verilmesini önlemek ve mevcut projelerin tasarımını bozmadan önce kanıt toplamak için uygulanır.

---

## 1. Mod Tespiti (Karar Ağacı)

Ajan tek satır CSS veya bileşen kodu değiştirmeden önce projenin durumunu tespit eder:

| Koşul | Aktif Mod | Ajanın Davranışı |
|---|---|---|
| Proje kökünde `DESIGN.md` **yok** VE projede çalışan/mevcut bir arayüz **var** (Brownfield) | **`Baseline Çıkarma Modu` (`mode: baseline`)** | ⛔ **Mevcut UI değiştirilmez!** Projenin mevcut renkleri, fontları, yüzeyleri ve bileşenleri analiz edilerek `<repo-kök>/DESIGN.md` (`mode: baseline`) olarak belgelenir. Yalnızca kullanıcı açıkça `"tasarımı değiştir"`, `"yeniden tasarla"`, `--redesign` veya `[OVERDRIVE]` derse F2 (Yeni Yön Seçimi) aşamasına geçilir. |
| Proje kökünde `DESIGN.md` **yok** VE proje sıfırdan kuruluyor (Greenfield) veya kullanıcı açıkça yeni tasarım istedi | **`Keşif & Tasarım Modu` (`mode: crafted`)** | F1 Keşif → F2 3 Alternatif Kreatif Yön → Kullanıcı Seçimi → F3 Token Üretimi → F4-F7 Uygulama akışı işletilir. |
| Proje kökünde `DESIGN.md` **var** VE kullanıcı normal `/ui-polish` çağırdı | **`İyileştirme Modu` (`Refinement`)** | Mevcut `DESIGN.md` sözleşmesi **korunur**. Token'lara ve kreatif kuzey yıldızına sadık kalınarak zanaat kusurları (kontrast, hiyerarşi, 4 UX durumu, responsive ergonomi, anti-slop) giderilir. |
| Proje kökünde `DESIGN.md` **var** VE kullanıcı açıkça `"tasarımı değiştir / yeniden tasarla"` dedi | **`Yeniden Tasarım Modu` (`mode: redesign`)** | `PRODUCT.md` korunur; eski `DESIGN.md` anti-referans kabul edilerek F1 → F2 (3 yeni yön) → Kullanıcı Seçimi ile yeni `DESIGN.md` yazılır. |

---

## 2. Kanıt Toplama Adımları (Zorunlu Okuma ve Tarama)

1. **Ürün ve Mimari Bağlamı Oku:**
   - Varsa `<repo-kök>/PRODUCT.md`, `<repo-kök>/PROJECT_BRIEF.md`, `<repo-kök>/README.md` ve `docs/brand-guidelines.md` (`brand` skill kapsamı) dosyalarını oku.
   - Kullanıcı kitlesini, temel kullanıcı görevini ve teknik yığını (`package.json`, Tailwind sürümü, shadcn/ui varlığı veya saf CSS) çıkar.
2. **Mevcut Token ve Stil Envanterini Çıkar:**
   - Mevcut CSS değişkenlerini (`:root`, `[data-theme]`, `.dark`), kullanılan `font-family` bildirimlerini, `border-radius` ve `spacing` değerlerini tara.
   - `python .agent/skills/musgoku/scripts/check_design_slop.py` ve `python .agent/skills/musgoku/scripts/check_theme_contrast.py` komutlarıyla mevcut ihlalleri ölç.
3. **Ekran Envanteri ve Yüzey Modu Sınıflaması:**
   - Projedeki her ekranı/sekmesini 4 yüzey modundan birine ata:
     * `Operate` (Görev/Uygulama/Dashboard)
     * `Persuade` (Pazarlama/Landing)
     * `Read` (Dokümantasyon/Katalog/Referans)
     * `Experience` (Portfolyo/Galeri)
4. **Görsel Kanıt (Multi-Viewport Ekran Görüntüsü):**
   - Çalışan arayüzü `chrome-devtools-mcp` ile `1440px` (Masaüstü), `834px` (Tablet) ve `390px` (Mobil) genişliklerinde incele.

---

## 3. F1 Çıktısı

Toplanan tüm kanıtlar `DESIGN.md` dosyasının **`## 0. Proje Kanıtı (Project Evidence)`** bölümüne yazılır. Bu bölüm doldurulmadan F2 veya F3 aşamasına geçilemez.
