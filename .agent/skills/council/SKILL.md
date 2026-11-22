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

### 3. Aşama 3 — Chairman Sentezi, Fiziksel `.md` Plan Dosyası (FAA AC 121-24C) ve Kalıcı Karar Kaydı
- Kazanan alternatifi, elenen alternatiflerin neden seçilmediğini (**Değerlendirilen Alternatifler** boş bırakılamaz) ve kabul edilen ödünleşimleri (trade-offs) sentezle.
- ⛔ **Sohbet/Terminal Çıktısı Yasağı (Physical `.md` Plan Mandate):** `/council` sonucunda bir uygulama/mimari plan oluşturuluyorsa, plan **ASLA yalnızca terminal/sohbet cevabı olarak bırakılamaz**! Plan ayrı bir fiziksel `.md` dosyasında (`<artifact-dir>/council_plan_<slug>.md` veya `.agent/plans/council_plan_<slug>.md`; onayda `docs/plans/council_plan_<slug>_<timestamp>.md`) `.agent/templates/PLAN.template.md` ve **FAA AC 121-24C Dokümantasyon Standardı** ile oluşturulur; ana ekrana yalnızca `/caveman` + `FAA AC 121-24C` özeti ve plan dosya bağlantısı basılır.
- **Kardeş Proje (Cross-Repo) Sorusu ve Süreç Senkronu:** Konsey kararı veya plan kardeş proje geliştirmesi gerektiriyorsa, **aynı dizin vs farklı dizin** kuralına göre kullanıcıya açıkça kardeş proje sorusu sorulur ve `sync_sibling_handoff.py` ile dizin fark etmeksizin kardeş projenin kendi `HANDOFF.md` + süreç dosyalarına (`KANBAN.md`, `SPRINT_PLAN.md`, `RELEASE_PLAN.md`) referanslı görevler işlenir.
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

---

## 5 SDLC Temas Noktası ve Birleşik Planlama Entegrasyonu

Council (Kör Hakemlik) mekanizması izole bir araç değil; SDLC yaşam döngüsünün 5 kritik anında Kademeli Eşik Modeliyle (Tiered Threshold) devreye girer:

1. **Planlama & Tasarım (`/plan`, `/council`, Adım 2.1):**
   - 2 veya daha fazla geçerli mimari, veri modeli veya kütüphane yaklaşımı içeren işlerde `PLAN.template.md` içindeki `## 2. 🏛️ Council Deliberation` tablosunu zorunlu olarak işletir (`Option A vs Option B` Borda analizi) ve planı mutlaka ayrı bir fiziksel `.md` dosyasında + **FAA AC 121-24C Dokümantasyon Standardı** ile üretir.
   - Birleşik Planlama Ekosistemi zincirini kurar: Fikir (`my-idea`) → Şartname (`doc-coauthoring`) → Açık Keşfi (`feature-architect` / `gap_scanner.py`) → Konsey Hakemliği (`council`) → Görev Tahtası (`KANBAN.md`) → TDD Dikiş Noktası & 5 Katmanlı Dilim (`development-workflow.md` Adım 2.2).
   - Konsey kararı kardeş uygulamayı (sibling repo) etkiliyorsa, dizin fark etmeksizin `sync_sibling_handoff.py` ile kardeş `HANDOFF.md` + süreç dosyalarına (`KANBAN.md`, `SPRINT_PLAN.md`, `RELEASE_PLAN.md`) `<kaynak-proje> projesindeki <plan-yolu> plan dosyası referansına göre` işlenir; aynı dizindeyse aynı kod ajanı ilerletebilir, farklı dizindeyse öncelik kardeş projenin kendi kod ajanına verilerek koda dokunmadan önce kullanıcıya mutlaka sorulur.
2. **Teknoloji & Kütüphane Seçimi (`/council`):**
   - Yeni kütüphane veya paket seçiminde (Zustand vs Context, Tailwind v4 vs v3, Auth protokolü vb.) bağımsız hakemlik yapar ve `docs/adr/` kaydı açar.
3. **Yüksek Riskli Refactoring (Blast Radius > 3):**
   - 3'ten fazla modülü veya çekirdek tipleri etkileyen refactoring adımlarında Karpathy sadelik filtresi uygular (`karpathy-guidelines` + `codebase-design`).
4. **Çelişen Hata Hipotezleri (`diagnosing-bugs` Aşama 3):**
   - Yarış durumu (race condition), bellek sızıntısı veya stale closure gibi çelişkili 2+ kök neden hipotezi varken hangisinin önce prob edileceğini Borda skoruyla belirler.
5. **Kod İnceleme İhtilafları (`code-review` / `verify-*`):**
   - Standartlar İncelemesi (Martin Fowler smell kataloğu) ile Şartname İncelemesi (ürün gereksinimleri) çatıştığında tarafsız hakemlik ve bilinçli ödünleşim (trade-off) sentezi üretir.
