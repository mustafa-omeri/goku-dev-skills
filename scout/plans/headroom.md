# 🔭 Scout Değerlendirme Raporu: headroomlabs-ai/headroom

## 1. Depo Özeti ve Künye
- **URL:** `https://github.com/headroomlabs-ai/headroom`
- **Analiz Tarihi:** 2026-10-26
- **Entegrasyon Tarihi:** 2026-10-26
- **Tespit Edilen Katman:** Tooling / Agentic + Backend (Rust / Python)
- **Teknoloji Yığını:** Rust (Tokio, Axum, Tracing), Python, SQLite, SSE Stream Parser
- **Çekirdek Amaç:** AI kodlama ajanları için context penceresi şişkinliğini önleyen, prompt önbellek (prompt cache) dostu bağlam sıkıştırma proxy'si ve protokolü.

---

## 2. Çekirdek Felsefe ve Mimari (Kaynak İncelemesi)

Headroom projesinin `REALIGNMENT/00-overview.md` ve `docs/context-mode-integration-analysis.md` dokümanlarında ortaya koyduğu en kritik zihinsel model değişimi:

1. **Yanlış Zihinsel Model (Eski Yaklaşım):**
   - *"Sıkıştırma, konuşma geçmişinden nelerin silineceğini seçmektir (Dropping messages from history / rolling window summarization)."*
   - Bu yaklaşım, mesaj dizisinin başından veya ortasından mesajları kırparak LLM prompt önbelleğini (`Anthropic Prompt Cache` veya `OpenAI Cache`) her istekte patlatır (`cache-killer bug`), sistem promptunu bozar ve ajanın temel kurallarını kaybetmesine yol açar.

2. **Doğru Zihinsel Model (Headroom Realignment Prensibi):**
   - *"Passthrough kutsaldır; yalnızca canlı bölge (live zone) sıkıştırılır (type-aware, hash-keyed, position-preserving)."*
   - **Cache Hot Zone (Dokunulmaz Bölge):** System prompt, araç tanımları (`tools`), anayasal kurallar ve eski oturum dönüşleri asla dinamik olarak mutasyona uğratılmaz; önbellek vuruş oranı (`cache-hit rate`) %90+ korunur.
   - **Live Zone (Canlı Sıkıştırma Bölgesi):** Sıkıştırma yalnızca en son kullanıcı mesajı içeriği (`user message`) ve en son araç çıktısına (`tool_result`, terminal stdout/stderr) uygulanır.

3. **Pre-Context Kabul Kontrolü (Admission Control) vs In-Context Sıkıştırma:**
   - Devasa bir terminal çıktısını (örneğin binlerce satırlık `npm list`, ham log dökümü, devasa JSON) context penceresine sokup sonra LLM içinde sıkıştırmaya çalışmak en pahalı yoldur.
   - En ucuz ve doğru yöntem: upstream araç çağrısı sınırında (`tool-call boundary`) filtreleme (`grep`, `head`, `tail`, byte offset) yaparak veriyi context'e **hiç sokmamaktır**.

4. **Byte-Accurate Hata Koruma (Fatal Line Preservation):**
   - Log ve çıktı sıkıştırılırken; `FATAL`, `FAIL`, `Error:`, `Exception`, `at line X:Y` gibi hata mekanizmasını kanıtlayan satırlar byte'ı byte'ına korunur; tekrarlayan ilerleme çubukları (`[====>] 87%`), spinner'lar ve bilgi satırları elenir.

---

## 3. Bizim Sistemle Kıyaslama (Delta Analizi)

- **Mevcut Durumumuz:**
  - `karpathy-guidelines`: Gereksiz karmaşıklıktan kaçınma, cerrahi değişiklik, Caveman düzyazı sıkıştırması (`token-efficient-communication.md`) ve ADHD doğrudan eyleme odaklanma (`action-first-communication.md`) prensiplerine sahipti.
  - `HANDOFF.md` & `knowledge-base.md`: Oturumlar arası kalıcı belleği yönetiyordu.
  - **Eksik Parça:** Context window doluluk yönetimi, prompt cache koruma disiplini ve araç çıktıları üzerindeki "Live-Zone Sıkıştırma / Byte-Accurate Hata Koruma" ilkeleri sistematik bir referans dokümanına ve kurallara bağlanmamıştı.
- **Kullanıcı Kararı:**
  - Aday repolardan yalnızca `headroom` seçildi; diğer adaylar elendi.
  - Headroom'un Rust proxy kodunu harici bir bağımlılık olarak kurup bakım maliyeti yaratmak yerine; context compression zekası, prompt cache koruma disiplini ve canlı bölge sıkıştırma protokolü cerrahi olarak `karpathy-guidelines` altına entegre edildi.

---

## 4. Karar: ✅ TAMAMLANDI (INTEGRATED)
`headroomlabs-ai/headroom` projesinin çekirdek context sıkıştırma ilkeleri sistemimize `.agent/skills/karpathy-guidelines/references/context-compression-headroom.md` olarak entegre edilmiş, `SKILL.md` ve ilgili ajan kurallarına bağlanmıştır.

---

## 5. Gerçekleştirilen Entegrasyon Adımları

1. **Referans Dokümanı:**
   - `.agent/skills/karpathy-guidelines/references/context-compression-headroom.md` oluşturuldu (Live Zone, Hot Zone Dokunulmazlığı, Pre-Context Kabul Kontrolü, Byte-Accurate Hata Koruma).
2. **Skill Genişletmesi:**
   - `.agent/skills/karpathy-guidelines/SKILL.md` içine `## 7. Context Compression & Headroom Principles` bölümü eklendi.
3. **Katalog & Scout Senkronizasyonu:**
   - `scout/repos.json` güncellendi (`headroom` `status: DONE`, `verdict: AKTARILDI`).
   - `scout/generate_scout_catalog.py` çalıştırılarak `scout-catalog.html` derlendi.
   - `scout/tests/test_engine.py` (22/22 PASS) ile doğrulandı.
