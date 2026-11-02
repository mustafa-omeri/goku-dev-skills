# 🔭 Scout Değerlendirme Raporu: google-labs-code/stitch-skills

## 1. Depo Özeti ve Künye
- **URL:** https://github.com/google-labs-code/stitch-skills
- **Sahibi:** google-labs-code
- **Analiz Tarihi:** 2026-10-30 13:19
- **Tespit Edilen Katman:** Frontend + Tooling / Agentic
- **Dosya Sayısı & Boyut:** 87 dosya (~491 KB)
- **Teknoloji Yığını:** Agent Skills Standardı (`SKILL.md`), Stitch MCP Entegrasyonu, React/TSX Bileşen Oluşturma, Codex/Claude Code/Cursor Plugin Paketleri (`plugin.json`).

## 2. Çekirdek Felsefe ve Mimari (Repo İncelemesi)
- **Deponun Amacı:** Google Labs bünyesindeki deneysel arayüz tasarım/kodlama aracı olan Google Stitch (stitch.withgoogle.com) ile entegre çalışan; Codex, Claude Code, Cursor ve OpenCode gibi ajanlar için 3 ana eklenti altında (`stitch-design`, `stitch-build`, `stitch-utilities`) toplanmış skill koleksiyonudur.
- **Mimari:**
  - `stitch-design`: Tasarım üretimi, stil varyasyonları ve layout prompt kurallarını barındırır.
  - `stitch-build`: Tasarımın React/Tailwind/Web bileşenlerine dökülmesini sağlayan oluşturma skill'lerini içerir.
  - `stitch-utilities`: Renk eşleme, export alma, token dönüşümü gibi Stitch MCP araçlarını çağıran yardımcı fonksiyonları sunar.
- **Güçlü Yönleri:**
  - Google Stitch MCP sunucusuyla (`YOUR_STITCH_MCP_URL`) doğrudan çift yönlü konuşabilen resmi arayüz şemalarına sahiptir.
  - Farklı AI kodlama ajanları (Codex, Claude Code, Cursor, OpenCode) için paketleme ve dağıtım kılavuzları gayet temiz belgelenmiştir.
- **Zayıf Yönleri:**
  - Kendi başına bağımsız çalışamaz; dış bir bağımlılık olan Stitch MCP sunucusuna ve Stitch bulut altyapısına sıkı sıkıya bağlıdır.
  - Tasarım zanaatı açısından generic prompt direktifleri içerir. `ui-ux-pro-max` veya `frontend-design` gibi yüzlerce küratörlü renk paleti, tipografi eşleşmesi, anti-slop filtreleri veya WCAG kontrast analiz araçları bulunmaz.

## 3. Bizim Sistemle Kıyaslama (Delta Analizi)
- **Mevcut Durumumuz:**
  - `frontend-design`: Karakterli, üretim kalitesinde web arayüzü kodu üretir; anti-AI slop kuralları ve hazır şablon motoruna sahiptir.
  - `ui-ux-pro-max`: 79 UI stili, 192 ürün paleti, 74 font eşleşmesi, 119 UX kuralı ve bağımsız Python test motoruyla eksiksiz bir tasarım beynidir.
  - `design-system` & `ui-styling`: Design token mimarisi, Tailwind/shadcn uyumluluğu ve WCAG AA kontrast kapılarını otomatik çalıştırır.
- **Dış Repodaki Değer:**
  - Eğer kullanıcı bir projede Google Stitch platformunu ve onun MCP aracını kullanmak isterse, Stitch API / MCP tool çağrı formatları ve `generate-design` gibi prompt akışları rehber niteliğindedir.
- **Kesişim & Ayrışma:**
  - Deponun skill seti, mevcut zengin tasarım ekosistemimizin yanında oldukça hafif ve üçüncü parti bir Google Labs servisine bağımlı kalmaktadır. Doğrudan içe aktarmak sistemimizde gereksiz dosya kalabalığı ve harici servis bağımlılığı yaratır.

## 4. Karar ve Gerekçe
**Karar:** `KISMEN_ALINABILIR: Google Stitch ekosistemi ve MCP tabanlı UI generation iş akışları için referans prompt/şablon kütüphanesi barındırıyor; ancak kod tabanımız bağımsız, zanaat odaklı ve yerel tasarım kurallarında çok daha olgun olduğundan sadece Stitch MCP entegrasyonu ve tasarım çıktısı prompt desenleri referans olarak değerlendirilebilir.`

**Gerekçe:**
Skill havuzumuz (`skillSetWorks`) halihazırda harici bir SaaS veya Google Labs aracına ihtiyaç duymaksızın üst düzey UI/UX, token denetimi ve responsive frontend kodu üretebilmektedir. Dış repodaki 87 dosyanın topluca içeri alınması mimarimizi kirletir. Yalnızca Stitch MCP sunucusuyla çalışılmak istendiğinde kullanılabilecek prompt kalıpları veya Stitch tool çağrıları referans olarak tutulmalıdır.

## 5. Cerrahi Entegrasyon Planı / Eylem Maddeleri
1. **İçeriye Dosya Kopyalamama İlkesi (Zero Bloat):** Repo doğrudan `.agent/skills/` altına çekilmeyecek, mevcut `frontend-design`, `ui-ux-pro-max` ve `design-system` yetki alanları korunacaktır.
2. **Stitch MCP Referansı:** Kullanıcı Google Stitch ile prototipleme yapmak istediğinde `mcp` konfigürasyonuna eklenebilecek `stitch` endpoint parametreleri ve Stitch tasarım dönüştürme promptları, ihtiyaç anında `frontend-design` referans dokümanlarına mikro-not olarak iliştirilecektir.
3. **Doğrulama:** Mevcut kalite kapılarımız (`check_design_skills.py`, `check_design_contract.py`) etkilenmeden çalışmaya devam edecektir.