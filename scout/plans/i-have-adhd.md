# 🔭 Scout Değerlendirme Raporu: ayghri/i-have-adhd

## 1. Depo Özeti ve Künye
- **URL:** [https://github.com/ayghri/i-have-adhd](https://github.com/ayghri/i-have-adhd)
- **Sahibi:** ayghri
- **Analiz Tarihi:** 2026-10-25 19:14
- **Tespit Edilen Katman:** Tooling / Agentic
- **Dosya Sayısı & Boyut:** 50 dosya (~329 KB)
- **Teknoloji Yığını:** TypeScript (`extensions/`, `scripts/`), Python (`scripts/judge.py`, `check_pi_extension.py`), Shell/PowerShell/MJS hooks (`always-on.*`), Markdown/JSONL evals dataset (`evals/`)

## 2. Çekirdek Felsefe ve Mimari (Repo İncelemesi)
`i-have-adhd`, LLM ve yapay zeka kodlama asistanlarının yanıt verme tarzını doğrudan dönüştüren bir ajanik çıktı disiplini (behavioral prompt & extension framework) sunar:
- **10 Keskin Kural (The 10 Rules):**
  1. *Lead with the next action:* Açılış cümlesi doğrudan yapılacak somut işi belirtir.
  2. *Number multi-step tasks:* Çok adımlı işler her zaman 1, 2, 3 şeklinde numaralandırılır.
  3. *End with one concrete next step:* Açık uçlu ("Başka bir şeye ihtiyacın var mı?") yerine tek bir net sonraki adım verir.
  4. *Suppress tangents:* Yan konular, gereksiz arka plan bilgileri bastırılır.
  5. *Restate state every turn:* Oturumlar arasında durum (state) kısa tek satırla hatırlatılır.
  6. *Specific time estimates:* "Biraz sürebilir" yerine net dakika tahminleri verilir.
  7. *Make wins visible:* Tamamlanan aşamalar açıkça gösterilir.
  8. *Matter-of-fact errors:* Hatalarda duygusal/özür dileyen ton yerine durum tespiti yapılır.
  9. *Cap lists to 5 items:* Bilişsel yükü düşürmek için listeler en fazla 5 madde ile sınırlandırılır.
  10. *No preamble, recap, or closers:* "Harika soru!", "Umarım yardımcı olmuştur!" gibi selamlama, özet ve kapanış lafları tamamen yasaktır.
- **Evals & Benchmark Mimarisi:** Repoda sadece prompt değil; `evals/cases.jsonl`, `evals/rubric.md` ve otomatik LLM hakemliği yapan `scripts/judge.py` bulunmaktadır. Ajanın gevezelik edip etmediğini, kuralları çiğneyip çiğnemediğini puanlayan bir test harness içerir.
- **Hook & Extension Katmanı:** Pi / OMP (`extensions/i-have-adhd.ts`) entegrasyonu ve oturum başlangıcında asistanı bu moda kilitleyen `always-on` script'leri mevcuttur.

## 3. Bizim Sistemle Kıyaslama (Delta Analizi)
- **Mevcut Durumumuz:**
  - `skillSetWorks` bünyesinde `karpathy-guidelines` (cerrahi müdahale, varsayımları yüzeye çıkarma), `no-silent-wait.md` (sessiz beklememe, net süre bildirme), `AGENTS.md` (iletişim disiplini, token tasarrufu) ve `task-observer` yer almaktadır.
  - Ancak yanıt formatı seviyesinde LLM'in bilişsel yükünü azaltan (Cognitive Load Reduction / ADHD-friendly formatting) kurallar derli toplu tek bir operasyonel kural setinde birleşmemiştir. Ajan bazen uzun giriş cümleleri (preamble) kurabilmekte ve listeleri aşırı uzatabilmektedir.
- **Dış Repodaki Değer:**
  - **10 Kuralın Sadelik ve Etkisi:** Özellikle 5 madde sınırı (list capping), açılışta doğrudan dosya ve satır aksiyonu ile başlama kuralı ve kapanış laflarının (no closers) yasaklanması ajanın çıktı kalitesini dramatik şekilde yükseltir.
  - **Eval/Judge Harness:** Çıktı formatının uyumunu denetleyen `rubric.md` ve `judge.py` değerlendirme yaklaşımı.
- **Kesişim & Ayrışma:**
  - Bizim yapımız yazılım mimarisi, TDD, CSS tasarımı ve devir teslim (handoff) konularında kat kat üstündür.
  - Bu repo ise yalnızca **çıktı formatı, bilişsel netlik ve yanıt ergonomisi** dikeyine odaklanmıştır. Bu nedenle rakip değil, iletişim katmanımızı besleyecek güçlü bir tamamlayıcıdır.

## 4. Karar ve Gerekçe
**Karar:** `ZENGINLESTIR: ADHD odaklı 10 katı çıktı biçimlendirme kuralı ve evals/judge mimarisi, Antigravity ve musgoku/karpathy iletişim kalıplarındaki dolaylı/geveze çıktıları (preamble/recap/open loop) budamak ve çıktıyı doğrudan eyleme odaklamak için güçlü bir cerrahi zenginleştirme sunmaktadır.`

**Gerekçe:** Repodaki 10 altın çıktı kuralı; ajanın konuşma tarzını, token harcamasını ve kullanıcının okuma yükünü doğrudan optimize eden kanıtlanmış bir UX/Agentic disiplinidir. Bizim `karpathy-guidelines` ve `communication_style` yönergelerimize bu 10 kuralın sentezlenmesi, çıktılarımızın "action-first" (önce eylem) kalitesini en üst düzeye çıkaracaktır.

## 5. Cerrahi Entegrasyon Planı / Eylem Maddeleri
1. **`karpathy-guidelines` ve İletişim Kurallarına Entegrasyon:**
   - `.agent/skills/karpathy-guidelines/SKILL.md` ve genel yanıt standartlarımıza "Action-First & Zero-Preamble" başlığı altında şu ilkeler enjekte edilmeli:
     - *No Preamble / No Recap:* "Harika soru", "Şimdi inceleyelim" gibi cümleler yasaklanır; doğrudan `Dosya:Satır` eylemiyle başlanır.
     - *Cap Lists to 5:* Sıralı listeler bilişsel yük için en fazla 5 madde ile sınırlandırılır.
     - *Single Concrete Next Step:* Yanıt sonu birden fazla açık uçlu soru yerine tek somut eylemle kapatılır.
2. **`task-observer` Gözlem Maddesi Olarak Eklenmesi:**
   - Ajanın gereksiz laf kalabalığını (filler words) tespit edip budaması için `task-observer` kılavuzuna "ADHD / High-Efficiency Output Formatting" deseni referans olarak eklenmeli.
3. **Doğrulama ve Rubrik:**
   - `evals/rubric.md` kriterleri kural doğrulaması için adapte edilerek yanıtların gevezelikten arındırıldığı doğrulanmalıdır.