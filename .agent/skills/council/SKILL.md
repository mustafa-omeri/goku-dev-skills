---
name: council
description: Üç aşamalı LLM konseyi ve kör hakemlik orkestratörü; mimari ikilemlerde alternatif üretip Borda skoruyla sentezler ve karar kaydı üretir. Tetikleyiciler: "/council", "llm council", "[COUNCIL]", "konsey topla", "hakemlik yap". Tetiklenmez: tek alternatifli basit kodlama `musgoku`'ya aittir. Tam sözlük: .agent/rules/skill-trigger-routing.md
---

# LLM Council Ensemble Orchestrator

Bu yetenek, 2 veya daha fazla geçerli alternatif içeren karmaşık mimari, teknoloji seçimi ve tasarım kararlarında kör hakemlik ve Borda sayısı oylamasıyla en uygun rotayı belirleyen 3 aşamalı konsey protokolünü (`karpathy-guidelines` → `doc-coauthoring` → `domain-modeling`) yürütür.

## Bağlı Kurallar ve Alt Yetenekler

- **Birincil Yetenek:** `karpathy-guidelines` (`.agent/skills/karpathy-guidelines/SKILL.md` ve `references/llm-council-deliberation.md`)
- **Destekleyici Yetenekler:** `doc-coauthoring`, `domain-modeling`
- **Kurallar:** `.agent/rules/skill-trigger-routing.md` (§0 Otonom Bağlamsal Tetikleme), `.agent/rules/knowledge-base-management.md`

---

## 3 Aşamalı Konsey ve Kör Hakemlik Akışı

### 1. Aşama 1 — Körleştirilmiş Alternatif Üretimi (Blinded Options)
- Karar bağlamını, kısıtları ve başarı ölçütlerini tanımla.
- En az 2–3 bağımsız, somut mimari alternatifi **tarafsız etiketlerle** (`Option A`, `Option B`, `Option C`) oluştur; modelin kendi ilk aklına geleni kayırmasını (self-preference bias) engellemek için her seçeneğin avantajlarını, maliyetlerini ve kırılma noktalarını eşit derinlikte yaz.

### 2. Aşama 2 — Kör Hakemlik ve Borda Sıralaması (`council_ranker.py`)
- Her alternatifi güvenlik, bakım maliyeti, performans ve mevcut mimariye uyum kriterleriyle değerlendir.
- Hakem sıralamalarını (`FINAL RANKING:`) Borda skoruyla hesaplamak için deterministik sıralayıcıyı çalıştır:
  ```bash
  python .agent/skills/karpathy-guidelines/scripts/council_ranker.py --sample
  ```
  *(veya JSON hakem çıktısını `--json` ile besleyerek matematiksel Borda kazananını hesapla).*

### 3. Aşama 3 — Chairman Sentezi ve Kalıcı Karar Kaydı (ADR & KB)
- Kazanan alternatifi, elenen alternatiflerin neden seçilmediğini (**Değerlendirilen Alternatifler** boş bırakılamaz) ve kabul edilen ödünleşimleri (trade-offs) sentezle.
- Kararı `<repo-kök>/knowledge-base.md` dosyasına kalıcı karar formatında (`Karar / Karar Gerekçesi / Değerlendirilen Alternatifler / Files Changed`) işle.
- Mimari/teknoloji yığını değişiyorsa `<repo-kök>/PROJECT_BRIEF.md` (§3 Bağlayıcı Kararlar) ve gerekiyorsa `docs/adr/` altındaki ADR kaydını güncelle.

---

## Standart Çıktı Raporu

```markdown
### ⚖️ LLM COUNCIL: MİMARİ HAKEMLİK VE KARAR SENTEZİ
- **Karar Problemi:** [Çözülen mimari ikilem]
- **Değerlendirilen Seçenekler:**
  * **Option A:** [Özet + Artı/Eksi]
  * **Option B:** [Özet + Artı/Eksi]
  * **Option C:** [Özet + Artı/Eksi]
- **Borda Hakemlik Skoru:** [Kazanan ve puan dağılımı]
- **Chairman Nihai Kararı & Gerekçesi:** [Seçilen yol ve neden diğerlerinin elendiği]
- **Kalıcı Kayıt:** `knowledge-base.md` / `PROJECT_BRIEF.md` güncellendi.
```
