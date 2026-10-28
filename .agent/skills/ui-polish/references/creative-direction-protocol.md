# F2 — Kreatif Yön, Hazır Varlık Elemesi ve Reddedilen Varsayılanlar Protokolü

Bu protokol, sıfır projelerde (`mode: crafted`) veya kullanıcının açıkça tasarım değişikliği istediği durumlarda (`mode: redesign`) ezbere LLM ortalaması üretmek yerine projeye özgü kreatif yön belirlemek için uygulanır.

---

## 1. İlgili Tasarım Becerilerinin Rolleri (F2 Zinciri)

1. **`canvas-design` (Felsefe ve Tipografi Kaynağı):**
   - **Rolü:** Görsel/PNG üretmek değil; projenin iş alanına özgü **1 paragraflık tasarım felsefesini (Kreatif Kuzey Yıldızı)** kurmak ve `.agent/skills/canvas-design/canvas-fonts/` altındaki küratörlü yazı tipi ailelerinden (`Instrument Serif`, `Plus Jakarta Sans`, `Bricolage Grotesque`, `IBM Plex Sans`, `Space Grotesk`, `Newsreader`, `Crimson Pro`, `JetBrains Mono` vb.) karakterli eşleşmeler seçmektir.
2. **`ui-ux-pro-max` & `frontend-design` (Aday Üretici):**
   - `python .agent/skills/ui-ux-pro-max/scripts/search.py "<ürün alanı>" --design-system`
   - `python .agent/skills/frontend-design/scripts/get_palette.py --list`
   - `python .agent/skills/frontend-design/scripts/get_component.py --list`
   - ⛔ **Kritik Kural:** Bu araçların çıktıları **nihai karar DEĞİLDİR**, yalnızca ham adaydır (`candidate`). Kontrastı düşük veya jenerik (slate + neon yeşil vb.) öneriler elenir.
3. **`brand` & `theme-factory` (Koşullu):**
   - Projede `docs/brand-guidelines.md` varsa ana marka rengi ve ses tonu oradan miras alınır.
   - Kullanıcı hızlı hazır tema istediyse `theme-factory` içindeki 10 küratörlü tema aday havuzuna eklenir.

---

## 2. Üç Alternatif Kreatif Yön Sunumu (İnsan Onayı Kapısı)

Ajan, proje kanıtına (F1) dayanarak birbirinden gerçekten farklı **3 alternatif yön** hazırlar ve kullanıcıya sunar:

| Alan | Açıklama |
|---|---|
| **Yön Adı & Kuzey Yıldızı** | İş alanına özgü somut metafor (ör. *"Endüstriyel Saha Kılavuzu"*, *"İsviçre Editoryal İndeksi"*, *"Yüksek Yoğunluklu Komut İstasyonu"*) |
| **Zemin & Renk Karakteri** | Açık/Koyu zemin tonu (OKLCH/HEX) + Birincil/İkincil vurgu renkleri ve ölçülmüş WCAG kontrast oranı |
| **Tipografi Çifti** | Display + Body (+ yalnızca kod için Mono) yazı tipi eşleşmesi ve ağırlık stratejisi |
| **Yerleşim & Yoğunluk Farkı** | Kart/tablo yoğunluğu, bilgi hiyerarşisi ve mikro-etkileşim karakteri |
| **Yerleşim Arketipi & IA** | App Shell + Collapsible Dock, Master-Detail Inspector Drawer, Multi-Density View vb. (⛔ Yalnızca token boyamak yasaktır; DOM iskeleti dönüştürülmelidir; `get_component.py` şablonları uyarlanmalıdır) |

⛔ **Durma Noktası:** Kullanıcı 3 yönden birini (veya mevcut baseline'da kalmayı) seçmeden F3-F5 uygulama adımlarına geçilmez.

---

## 3. Zorunlu "Reddedilen Varsayılanlar" (Rejected Defaults) Tablosu

Seçilen yön `DESIGN.md` içine işlenirken **`## 3. Reddedilen Varsayılanlar`** tablosuna en az 2 somut ret gerekçesi yazılır:
- **Örnek 1:** `search.py` çıktısındaki `Slate #0F172A + Green #22C55E` → *"Jenerik yapay zeka geliştirici paneli klişesi olduğu için reddedildi; yerine sıcak mineral/kağıt tonlu yüzey seçildi."*
- **Örnek 2:** *"Rozetlerde, kategori etiketlerinde ve kart başlıklarında `JetBrains Mono` kullanımı → Okunabilirliği düşürdüğü ve tipografi tavanını deldiği için reddedildi; mono yalnızca terminal/komut dizgeleriyle sınırlandırıldı."*
