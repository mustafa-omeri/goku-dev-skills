# F2 — Kreatif Yön, Hazır Varlık Elemesi ve Reddedilen Varsayılanlar Protokolü

Bu protokol, sıfır projelerde (`mode: crafted`) veya kullanıcının açıkça tasarım değişikliği istediği durumlarda (`mode: redesign`) ezbere LLM ortalaması üretmek yerine projeye özgü kreatif yön belirlemek için uygulanır.

---

## 1. İlgili Tasarım Becerilerinin Rolleri (F2 Zinciri)

1. **`canvas-design` (Felsefe ve Tipografi Kaynağı):**
   - **Rolü:** Görsel/PNG üretmek değil; projenin iş alanına özgü **1 paragraflık tasarım felsefesini (Kreatif Kuzey Yıldızı)** kurmak ve `.agent/skills/canvas-design/canvas-fonts/` altındaki küratörlü yazı tipi ailelerinden (`Instrument Serif`, `Plus Jakarta Sans`, `Bricolage Grotesque`, `IBM Plex Sans`, `Space Grotesk`, `Newsreader`, `Crimson Pro`, `JetBrains Mono` vb.) karakterli eşleşmeler seçmektir.
2. **`ui-ux-pro-max` & `frontend-design` (Çok-Kaynaklı Palet & Aday Üretici):**
   - `python .agent/skills/ui-ux-pro-max/scripts/search.py "<ürün alanı>" --design-system`
   - `python .agent/skills/frontend-design/scripts/get_palette.py --list` (10 ölçülmüş WCAG paleti)
   - `python .agent/skills/frontend-design/scripts/get_palette.py --style-themes` (88 Style Theme Color Palettes — `.agent/skills/frontend-design/themes/style-theme-palettes.md`)
   - `python .agent/skills/frontend-design/scripts/get_palette.py --style "<TEMA>" --mode <dark|light> --format css` (WCAG AA türetim köprüsü)
   - `python .agent/skills/frontend-design/scripts/get_component.py --list`
   - ⛔ **Kritik Kural:** Bu araçların çıktıları **nihai karar DEĞİLDİR**, yalnızca ham/esin adayıdır (`candidate`). Ajan mutlaka mevcut 16 kilitli tema (`themes.css`) + 88 Style Theme + önceki ölçülmüş palet kombinasyonlarından esinlenerek sentez yapar; kontrastı düşük veya jenerik (slate + neon yeşil vb.) öneriler elenir.
3. **`brand` & `theme-factory` (Koşullu):**
   - Projede `docs/brand-guidelines.md` varsa ana marka rengi ve ses tonu oradan miras alınır.
   - Kullanıcı hızlı hazır tema istediyse `theme-factory` içindeki 10 küratörlü tema da aday havuzuna eklenir.

---

## 2. Üç Alternatif Kreatif Yön Sunumu ve Tek-Taraflı Seçim Yasağı (İnsan Onayı Kapısı)

Ajan, proje kanıtına (F1) dayanarak birbirinden gerçekten farklı **3 alternatif yön** hazırlar ve kullanıcıya sunar:

| Alan | Açıklama |
|---|---|
| **Yön Adı & Kuzey Yıldızı** | İş alanına özgü somut metafor (ör. *"Endüstriyel Saha Kılavuzu"*, *"İsviçre Editoryal İndeksi"*, *"Yüksek Yoğunluklu Komut İstasyonu"*) |
| **Esin Kaynağı (Palet / Tema Provenance)** | Hangi kombinasyondan esinlenildiği (ör. `Style Theme: NORDIC NEON` / `themes.css #08 Maritime Amber` / `Palette #7 Şehir Ormanı`) + neden uygun olduğu |
| **Zemin & Renk Karakteri** | Açık/Koyu zemin tonu (OKLCH/HEX) + Birincil/İkincil vurgu renkleri ve ölçülmüş WCAG kontrast oranı (`>= 4.5:1`) |
| **Tipografi Çifti** | Display + Body (+ yalnızca kod için Mono) yazı tipi eşleşmesi ve ağırlık stratejisi |
| **Yerleşim & Yoğunluk Farkı** | Kart/tablo yoğunluğu, bilgi hiyerarşisi ve mikro-etkileşim karakteri |
| **Yerleşim Arketipi & IA** | App Shell + Collapsible Dock, Master-Detail Inspector Drawer, Multi-Density View vb. (⛔ Yalnızca token boyamak yasaktır; DOM iskeleti dönüştürülmelidir; `get_component.py` şablonları uyarlanmalıdır) |

⛔ **Tek-Taraflı Seçim Yasağı & Durma Noktası:** Ajan hiçbir zaman *"ben projeye en uygun bu kombinasyonu seçtim ve ilerliyorum"* diyerek tek başına karar alıp koda geçemez; jenerik/standart LLM refleksleriyle de ilerleyemez. Kullanıcı sunulan 3 alternatiften birini (veya mevcut baseline'da kalmayı) açıkça onaylamadan F3-F5 uygulama adımlarına geçilmez. Her adayın neden seçildiği veya elendiği `DESIGN.md` §2 ve §3 `Reddedilen Varsayılanlar` tablosunda şeffafça belgelenir.

---

## 3. Zorunlu "Reddedilen Varsayılanlar" (Rejected Defaults) Tablosu

Seçilen yön `DESIGN.md` içine işlenirken **`## 3. Reddedilen Varsayılanlar`** tablosuna en az 2 somut ret gerekçesi yazılır:
- **Örnek 1:** `search.py` çıktısındaki `Slate #0F172A + Green #22C55E` → *"Jenerik yapay zeka geliştirici paneli klişesi olduğu için reddedildi; yerine sıcak mineral/kağıt tonlu yüzey seçildi."*
- **Örnek 2:** *"Rozetlerde, kategori etiketlerinde ve kart başlıklarında `JetBrains Mono` kullanımı → Okunabilirliği düşürdüğü ve tipografi tavanını deldiği için reddedildi; mono yalnızca terminal/komut dizgeleriyle sınırlandırıldı."*
