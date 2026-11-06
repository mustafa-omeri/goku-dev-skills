# Feature Architect — 4 Fazlı 6 Şapkalı Konsey Protokolü (`council-protocol.md`)

Bu doküman, `/feature-architect` çağrıldığında devreye giren **6 Şapkalı Strateji Konseyi (The Six-Hat Council)**, **Dinamik Motor Seçim Kapısı (`engine_advisor.py`)** ve **Ezilmezlik / Zero-Drop Konsolidasyonu (`council_merger.py`)** protokolünün bağlayıcı çalışma kılavuzudur.

---

## 1. 6 Uzman Şapka (The Six-Hat Council)

| Sıra | Dosya | `agent_id` | Önek | Temel Denetim Odağı |
| :---: | :--- | :--- | :---: | :--- |
| 1 | [`agents/01-snr-product-owner.md`](../agents/01-snr-product-owner.md) | `snr-product-owner` | `PO` | PRD vs. kod farkları, çekirdek modüller, kullanıcı yolculuğu, RICE önceliklendirme |
| 2 | [`agents/02-snr-software-architect.md`](../agents/02-snr-software-architect.md) | `snr-software-architect` | `ARCH` | Kanonik 5 katmanlı mimari, yetim API/DB kolonları, kırık rotalar, performans |
| 3 | [`agents/03-principal-ui-ux-specialist.md`](../agents/03-principal-ui-ux-specialist.md) | `principal-ui-ux-specialist` | `UX` | Living Surface, 16 tema, 55+ bileşen, 18 dashboard-theme, Zero-CLS 4 durum, mobil UX |
| 4 | [`agents/04-snr-seo-specialist.md`](../agents/04-snr-seo-specialist.md) | `snr-seo-specialist` | `SEO` | Semantik HTML5, indeksleme, Soft-404, JSON-LD, Core Web Vitals, pSEO (`N/A` destekli) |
| 5 | [`agents/05-snr-growth-marketing.md`](../agents/05-snr-growth-marketing.md) | `snr-growth-marketing` | `GRW` | AARRR hunisi, Aha! Moment / onboarding hızı, dönüşüm metinleri, PLG büyüme kancaları |
| 6 | [`agents/06-snr-qa-security-auditor.md`](../agents/06-snr-qa-security-auditor.md) | `snr-qa-security-auditor` | `QA` | OWASP 20 madde, RBAC/IDOR/RLS, uçtan uca validasyon, 5 katmanlı TDD dikiş noktaları |

> **Daraltılmış Şapka Seçimi (`--hats`):** Kullanıcı `/feature-architect --hats po,arch,ux` gibi alt küme belirtirse yalnızca seçilen şapkalar çalıştırılır; belirtilmezse 6 şapkanın tamamı çalışır.

---

## 2. Faz 1 — Ortak Röntgen (`context-snapshot.json`) ve Motor Seçim Kapısı

### 2.1 Ortak Röntgen (Shared Context Snapshot)
6 uzmandan hiçbiri çalışmaya başlamadan önce ana orkestratör projeyi tek seferde tarar ve çıktıyı `docs/plans/council/<YYYY-MM-DD>/context-snapshot.json` dosyasına yazar:
1. Deterministik kanıt taraması:
   ```bash
   python .agent/skills/feature-architect/scripts/gap_scanner.py --root . --json
   ```
2. `PRODUCT.md` / `README.md` / PRD özeti, `PROJECT_BRIEF.md` teknoloji yığını, `DESIGN.md` yüzey modu (Light/Dark) ve `HANDOFF.md` açık işler özeti bu snapshot içine eklenir.

### 2.2 Motor Seçim Kapısı (`engine_advisor.py`)
Varsayılan yürütme motoru **Tek Ajan (`single`)** modudur; ancak ortam alt ajan (`subagent`) desteklediğinde proje ölçeği deterministik olarak ölçülür:

```bash
python .agent/skills/feature-architect/scripts/engine_advisor.py --root . --subagents yes --format json
```

*(Alt ajan aracına sahip olmayan bir terminal ortamındaysan `--subagents no` verilir).*

| Ölçek Boyutu | `0` Puan | `1` Puan | `2` Puan |
| :--- | :---: | :---: | :---: |
| Kaynak dosya sayısı (`source_files`) | `< 150` | `150 – 400` | `> 400` |
| Kod satırı (`loc`) | `< 15.000` | `15.000 – 50.000` | `> 50.000` |
| Tanımlı rota (`routes`) | `< 20` | `20 – 60` | `> 60` |
| Ek repo (`peers`) | `0` | `1` | `>= 2` |
| Tespit edilen boşluk (`gaps`) | `< 15` | `15 – 40` | `> 40` |

- **Sınıflandırma:** Toplam `>= 6` -> **`large`** (Öneri: `multi`) · `3 – 5` -> **`medium`** (Öneri: `single`) · `<= 2` -> **`small`** (Öneri: `single`).
- **Karar Akışı:**
  1. Kullanıcı komutta açıkça `--engine=single` veya `--engine=multi` verdiyse soru sorulmaz; seçilen motor doğrudan uygulanır.
  2. Ortam alt ajan **desteklemiyorsa** (`--subagents no`) soru sorulmaz; doğrudan `single` motoruyla ilerlenir ve raporda *"Kör izolasyon zayıflatılmış (Tek Ajan Sıralı Mod)"* beyanı basılır.
  3. Ortam alt ajan **destekliyorsa** (`--subagents yes`, `ask_user: true`) ajan 6 şapka denetimine başlamadan önce `engine_advisor.py` çıktısındaki metrikleri ve öneriyi göstererek kullanıcıya **`single` (Tek Ajan) mı yoksa `multi` (Alt Ajanlı Paralel) mı** ilerlemek istediğini sorar (`engine-advice.json` dosyası konsey klasörüne kaydedilir).

---

## 3. Faz 2 — Araç Bazlı Alt Ajan İcra Matrisi ve Körlük Disiplini

| Geliştirme Ortamı | `multi` Motoru İcrası | `single` Motoru İcrası | Kör İzolasyon |
| :--- | :--- | :--- | :--- |
| **Antigravity IDE / Antigravity CLI (`agy`)** | Yerleşik alt ajan çağrısı × 6 paralel; her alt ajana yalnız `context-snapshot.json` + kendi `agents/0X-*.md` dosyası + şema verilir | Sabit sırayla (`01` -> `06`) her şapka okunup JSON dosyası diske yazılır | `multi`: **Tam** · `single`: Zayıflatılmış |
| **Claude Code (`claude`)** | Paralel alt ajan / görev aracı × 6; aynı izole girdi paketi | Sabit sırayla (`01` -> `06`) JSON üretimi | `multi`: **Tam** · `single`: Zayıflatılmış |
| **OpenCode (`opencode`)** | Alt ajan (subagent) × 6 paralel veya eşzamanlı görev | Sabit sırayla (`01` -> `06`) JSON üretimi | `multi`: **Tam** · `single`: Zayıflatılmış |
| **Genel Terminal / CLI (Alt ajansız)** | Desteklenmez (`--subagents no` -> otomatik `single`) | Sabit sırayla (`01` -> `06`) JSON üretimi; rapora dürüst körlük uyarısı basılır | Zayıflatılmış (Dürüstçe beyan edilir) |

### Tek Ajan (`single`) Sıralı İzolasyon Kuralları
1. Şapkalar her zaman `01` -> `06` sırasıyla tek tek ele alınır.
2. Her şapka turunda yalnızca `context-snapshot.json` ve o şapkanın `agents/0X-*.md` dosyası baz alınır; bir önceki şapkanın ürettiği JSON dosyası tekrar okunmaz ve önceki şapkanın bulgularına uyum sağlamak için eleştiri törpülenmez.
3. Üretilen her JSON anında `docs/plans/council/<YYYY-MM-DD>/0X-<agent_id>.json` yoluna kaydedilir.
4. Nihai raporda şeffaflık gereği şu not zorunludur: *"Yürütme Motoru: Tek Ajan Sıralı İzolasyon — tüm şapkalar aynı model bağlamında sırayla üretildiği için kör izolasyon zayıflatılmıştır."*

---

## 4. Faz 3 — Ezilmezlik, Baş Hakem ve Zero-Drop Kapısı (`council_merger.py`)

6 uzmanın JSON çıktıları diske yazıldıktan sonra **Baş Hakem (Chief Council Arbiter)** serbest metin yazmadan önce deterministik birleştiriciyi çalıştırır:

```bash
python .agent/skills/feature-architect/scripts/council_merger.py --inputs docs/plans/council/<YYYY-MM-DD> --output docs/plans/council/<YYYY-MM-DD>/merged.json
```

### Birleştirme ve Hakem Kuralları
1. **Sağlık Skoru, En Zayıf Halka ve `CRITICAL` Tavanı:**
   - Aktif (`applicable`) uzmanlar eşit ağırlıkla (`1.0`) ortalanır; `not_applicable` uzmanlar (örn. dahili araçta SEO) paydadan çıkarılır.
   - En düşük puanlı uzman **En Zayıf Halka** olarak karnede ayrıca vurgulanır.
   - Çözülmemiş tek bir `CRITICAL` bulgu dahi varsa **Proje Olgunluk Skoru en fazla `60.0` olabilir** (`critical_cap_applied: true`).
2. **Sinerji Kümeleme (`synergy_clusters`):**
   - 2 veya daha fazla uzmanın aynı normalize dosya/uç konumunda bildirdiği bulgular **"Yüksek Öncelikli Ortak Hedef"** altında birleştirilir ve önem derecesi bir kademe yükseltilir (`MEDIUM -> HIGH`, `HIGH -> CRITICAL`).
3. **Çatışma Çözüm Masası (`conflict_candidates` -> Hibrit 3. Yol):**
   - Bir uzmanın önerisi başka bir uzmanın `non_negotiable_constraints` kırmızı çizgisiyle aynı konumda kesiştiğinde hiçbir uzman görüşü silinmez.
   - Baş Hakem her iki kırmızı çizgiyi de koruyan **Hibrit Mühendislik Çözümü (3. Yol)** üretir. Eğer 2+ geçerli hibrit mimari alternatif doğarsa `python .agent/skills/karpathy-guidelines/scripts/council_ranker.py --sample` protokolündeki Borda oylamasıyla kazanan hibrit yol seçilir.
4. **Beyond-PRD RICE Sıralaması (`features_ranked`):**
   - Yeni özellik önerileri `RICE = (reach * impact_score * confidence) / effort_puanı` (`S=1, M=2, L=3, XL=5`) formülüyle puanlanır; birden fazla uzmanın önerdiği aynı başlıklı özellikler birleştirilip ortak imzayla en üste taşınır.
5. **Zorunlu Zero-Drop Doğrulama Kapısı (`--check-report`):**
   - Baş Hakem konsolide Markdown raporunu yazdıktan sonra, hiçbir `CRITICAL` veya `HIGH` bulgu kimliğinin (`PO-01`, `QA-01` vb.) özetlenirken düşürülmediğini kanıtlamak için şu kapıyı çalıştırmak **ZORUNLUDUR**:
   ```bash
   python .agent/skills/feature-architect/scripts/council_merger.py --inputs docs/plans/council/<YYYY-MM-DD> --check-report docs/plans/council/<YYYY-MM-DD>/feature-architect-council-report.md
   ```
   - Komut `exit 2` dönerse eksik bulgu ID'leri rapora eklenmeden kullanıcıya sunulamaz!

---

## 5. Kalıcı Konsey Dizin Yapısı (Dual-Persistence)

Her konsey çalışmasında çıktılar hem IDE/araç artifact dizinine (`<artifact-dir>/feature-architect-report.md`) hem de hedef projenin versiyon kontrolündeki konsey klasörüne yazılır:

```text
docs/plans/council/<YYYY-MM-DD>/
├── context-snapshot.json                 # Faz 1: gap_scanner + PRD/BRIEF/DESIGN özeti
├── engine-advice.json                    # engine_advisor.py ölçek ve motor önerisi
├── 01-snr-product-owner.json             # Şapka 1 izole çıktısı
├── 02-snr-software-architect.json        # Şapka 2 izole çıktısı
├── 03-principal-ui-ux-specialist.json    # Şapka 3 izole çıktısı
├── 04-snr-seo-specialist.json            # Şapka 4 izole çıktısı
├── 05-snr-growth-marketing.json          # Şapka 5 izole çıktısı
├── 06-snr-qa-security-auditor.json       # Şapka 6 izole çıktısı
├── merged.json                           # council_merger.py deterministik birleşimi
└── feature-architect-council-report.md   # Zero-Drop kapısından geçmiş nihai konsolide rapor
```
*(Ayrıca en güncel rapor `docs/plans/feature-architect-report.md` veya `.agent/plans/feature-architect-report.md` konumuna da senkron kopyalanır).*
