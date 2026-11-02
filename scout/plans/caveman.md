# 🔭 Scout Değerlendirme Raporu: juliusbrussee/caveman

## 1. Depo Özeti ve Künye
- **URL:** https://github.com/juliusbrussee/caveman
- **Sahibi:** juliusbrussee
- **Analiz Tarihi:** 2026-10-25 19:14
- **Tespit Edilen Katman:** Tooling / Agentic
- **Dosya Sayısı & Boyut:** 1761 dosya (~21792 KB)
- **Teknoloji Yığını:** Node.js / JavaScript (ESM, `@caveman-ai/cli`), Go (`go.mod`), Shell/Hooks, MCP (`caveman-delegate-mcp.mjs`), Agent Profiles (30+ CLI/IDE ajan profili - Claude, Codex, Gemini, Cursor, Aider, Windsurf vb.)

## 2. Çekirdek Felsefe ve Mimari (Repo İncelemesi)
- **Amacı ve Özü:** Caveman ("why many token when few do trick"), yapay zeka kodlama ajanlarının gevezeliğini (fluff, corporate niceties, verbose explanations) sıfırlayarak çıktı token'larını %50-70, tüm oturum girdi/çıktı maliyetini ise %33.2 oranında düşürmeyi hedefleyen radikal bir metin sıkıştırma motorudur.
- **Teknik Yaklaşım:**
  1. **Caveman Voice / Kompresyon Seviyeleri:** `/caveman`, `/ultracave` ve `/megacave` adında üç katmanlı prompt kuralları tanımlar. Teknik terimler, kod blokları, dosya yolları, diff'ler ve kesin hata metinleri %100 korunurken; giriş, geçiş ve nezaket cümleleri budanır ("New object ref each render, so React re-renders. Wrap in useMemo.").
  2. **Geniş Ajan Adaptör Ağı (`agents/profiles/`):** 30'dan fazla yapay zeka aracına (Claude Code, Gemini CLI, Codex, Cursor, Windsurf, OpenCode, Aider vb.) tek bir CLI komutuyla (`npx @caveman-ai/cli@latest`) enjekte olan dinamik hook ve profil mimarisi barındırır.
  3. **Session Hooks ve MCP Delegasyonu:** `caveman-delegate-mcp.mjs` ve process wrapper'lar üzerinden ajanların subagent veya CLI süreçlerini hafifletip filtreleyen mekanizmalar içerir.

## 3. Bizim Sistemle Kıyaslama (Delta Analizi)
- **Mevcut Durumumuz (`skillSetWorks`):**
  - Bizim sistemimiz (`.agent/`) 28+ zanaatkar skill, sıkı mimari sözleşmeler (`AGENTS.md`, `rules/`), TDD, dikey dilim doğrulama (`Full-Stack Vertical Slice`), tasarım sistemleri ve çoklu MCP entegrasyonu barındıran tam teşekküllü bir yazılım fabrikasıdır.
  - Bizde `karpathy-guidelines` (cerrahi değişiklik, gereksiz karmaşıklıktan kaçınma), `communication_style` (öz ve doğrudan yanıtlar) ve `no-silent-wait` kuralları mevcuttur; fakat ajanların akıl yürütme dışındaki ara gevezeliklerini radikal olarak kırpan özelleşmiş bir "Token Compression & Concise Output" alt kuralı/modu doğrudan yapılandırılmamıştır.
- **Dış Repodaki Değer:**
  - Caveman'in devasa dosya boyutu (1761 dosya) ve paket yükü genel olarak gereksizdir; ancak **teknik kesinliği bozmadan doğal dili telegrafik/kısa biçime sokan sistem talimatı formülasyonu** ve **çoklu CLI ajan profil şemaları** (`agents/profiles/schema.json`) saf değer taşır.
- **Kesişim & Ayrışma:**
  - Deponun tüm installer'ını ve CLI aracını içimize almak mimarimizi kirletir ve dış bağımlılık yaratır.
  - Ancak prompt prensipleri ("Keep code exact, compress prose, no conversational padding") `karpathy-guidelines` ve `.agent/rules/` yapımıza %100 uyumludur.

## 4. Karar ve Gerekçe
**KISMEN_ALINABILIR: Token tasarrufu ve aşırı lafazanlığı önleyen "Caveman prose compression" prompt/kural tekniği ile çoklu ajan profil haritalaması, `karpathy-guidelines` ve global ajan iletişim ilkelerine cerrahi bir mod olarak eklenebilir.**

- **Gerekçe:** 21 MB'lık ve 1761 dosyalık dış reponun büyük kısmı CLI dağıtım dosyaları, build çıktıları ve çoklu araç paketleridir (`BIZ_DAHA_IYIYIZ`). Ancak token bütçesini dramatik düşüren ve bağlam penceresini (context window) koruyan "özlü anlatım / zero-fluff" çekirdek prompt kural seti zekice tasarlanmıştır. Bu teknik kural seti cerrahi olarak ayıklanıp sistemimize entegre edilmeye değerdir.

## 5. Cerrahi Entegrasyon Planı / Eylem Maddeleri
1. **`karpathy-guidelines` Skill Zenginleştirmesi:**
   - `.agent/skills/karpathy-guidelines/references/` altına `token-efficient-communication.md` referansı eklenerek; kod kalitesinden ödün vermeden açıklama metinlerini %40-60 sıkıştıran "Telegraphic / High-Density Output" prensipleri tanımlanacak.
2. **Kural Sözleşmesi Senkronizasyonu:**
   - `.agent/rules/` altındaki yanıt biçimlendirme rehberine Caveman'in "Teknik doğruluk ve kod blokları tam, gereksiz nezaket ve dolgu cümleleri sıfır" ilkesi rehber olarak işlenecek.
3. **Doğrulama ve Koruma:**
   - Mevcut doğrulama kapıları (`python -m unittest discover -p "test_*.py"`) çalıştırılarak kural eklemelerinin hiçbir sözleşmeyi bozmadığı teyit edilecek.