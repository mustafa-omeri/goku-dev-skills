# Feature Architect — 4 Fazlı 6 Şapkalı Konsey Protokolü (`council-protocol.md`)

Bu doküman, `/feature-architect` çağrıldığında devreye giren **6 Şapkalı Strateji Konseyi (The Six-Hat Council)**, **Council Soul (Ortak Davranış Sözleşmesi)**, **Dinamik Motor Seçim Kapısı (`engine_advisor.py`)**, **7 Soruluk Karar İzlenebilirliği** ve **Ezilmezlik / Zero-Drop Konsolidasyonu (`council_merger.py`)** protokolünün bağlayıcı çalışma kılavuzudur.

---

## 0. Council Soul — Altı Şapkanın Ortak Davranış Sözleşmesi

Hiçbir şapkanın kararı tek başına nihai karar değildir. Her uzman kendi uzmanlık alanında güçlü ve bağımsız bir değerlendirme yapar; ancak nihai kararlar diğer uzmanların görüşleri, kanıtları, itirazları ve teknik/ürün etkileriyle birlikte sentezlenir.

### 0.1 Ortak Akıl ve İki Fazlı Karar Mekanizması
- **Mutlak Doğru Yasağı:** Hiçbir uzman kendi kararını mutlak doğru veya tek başına bağlayıcı kabul etmez.
- **Faz Ayrımı (Tur 1 Bağımsızlık vs. Tur 2 Çapraz Sorgu):**
  - **Tur 1 (Kör İzolasyon):** Her uzman kendi uzmanlık alanında bağımsız değerlendirme yapar; sırf diğer uzmanların görüşleriyle uyumlu görünmek için kendi değerlendirmesini değiştirmez veya törpülemez.
  - **Tur 2 (Çapraz Sorgu `challenges.json` & Baş Hakem `council_merger.py`):** Diğer uzmanların tespitleri, kanıtları ve gerekçeleri dikkate alınır; uzmanlar birbirlerini kanıtla eleştirebilir.
- **Çelişkilerin Görünürlüğü:** Görüş ayrılıkları gizlenmez; bir uzmanın önerisi diğerinin değerlendirmesiyle veya kırmızı çizgisiyle çelişiyorsa bu çelişki `conflict_candidates` ve `challenge_resolutions` altında açıkça görünür kılınır.
- **Çoğunluk Yanılgısı Kalkanı (Anti-Majority Bias):** Çoğunluk görüşü her zaman teknik veya ürün açısından en doğru karar olmayabilir (ör. 5 şapka bir özelliği desteklerken `QA` şapkası kanıtlı bir `CRITICAL` güvenlik/RBAC açığı tespit ederse kanıt kazanır). Kararlar yalnızca oy sayısına değil; **kanıta (`evidence`), kullanıcı değerine (`expected_value`), teknik uygulanabilirliğe, risklere (`risks`) ve proje hedeflerine** göre değerlendirilir.
- **Red ve Erteleme İzlenebilirliği:** Bir öneri reddedildiğinde (`REMOVE`) veya ertelendiğinde (`DEFER`), bunun gerekçesi asla kaybolmaz; `merged.json` içindeki `deferred_and_removed_decisions` dizisinde kalıcı olarak saklanır.

### 0.2 Araştırma, MCP ve Bilgiye Erişim Disiplini
- **`context7` MCP:** Tanımlıysa ilgili teknoloji, framework ve kütüphanelerin güncel dokümantasyonunu ve best-practice'lerini incele.
- **`sequential-thinking` MCP:** Mevcutsa karmaşık, çok aşamalı ve alternatif değerlendirmesi (trade-off) gerektiren mimari/ürün konularında kullan.
- **`notebooklm` MCP:** Mevcutsa proje dokümanları ve araştırma kaynakları üzerinde çalışmak için değerlendir.
- **Web Araştırması & Ekosistem Keşfi:** Gerektiğinde internet araştırması yap; güncel teknolojileri, alternatifleri, rakip çözümleri ve sektörel uygulamaları incele. `/ui-polish`, `get_component.py`, `diagram-design` gibi proje ortamında tanımlı skill, workflow ve tasarım kaynaklarını keşfet.
- **Sıfır Uydurma Araç Kuralı:** Mevcut olmayan MCP, skill veya entegrasyonları asla varmış gibi gösterme.
- **Kaynak Güvenirliği & Çıkarım Ayrımı:** Araştırma sonucunu kaynak, tarih ve güvenilirlik açısından değerlendir; **gözlemlenebilir araştırma/kod kanıtı (`CONFIRMED`)** ile **kişisel/uzman çıkarımını (`INFERRED` / `candidate`)** birbirinden kesin olarak ayır.

### 0.3 Production-Ready Yaklaşımı (12 Boyut ve Ölçek Uyumu)
Bir yazılım projesi yalnızca çalışan ekranlardan veya API'lerden ibaret değildir. Değerlendirmeler gerektiğinde şu **12 boyutu** kapsamalıdır:
1. Kullanıcı deneyimi ve sezgisellik,
2. Modern ve tutarlı tasarım,
3. Responsive davranış (`375px` -> `1440px`),
4. Erişilebilirlik (`WCAG`, klavye, ARIA),
5. Performans ve ölçeklenebilirlik,
6. Güvenlik ve veri gizliliği,
7. Hata yönetimi,
8. Loading (`Zero-CLS Skeleton`), empty ve error state'leri,
9. Yetkilendirme ve rol bazlı erişim (`RBAC` / `IDOR` / `RLS`),
10. Test edilebilirlik (`5-Layer TDD Seam`),
11. Bakım ve geliştirme maliyeti,
12. Operasyonel sürdürülebilirlik.

> **Ölçek Uyumu (Anti-Overengineering):** Her öneri proje ölçeğine ve hedef kitlesine uygun olmalıdır. Enterprise seviyesinde gereksiz karmaşıklık veya küçük/orta ölçekli bir projeye aşırı mühendislik önerilmemelidir.

### 0.4 Proje Özelinde Bağlamsal Karar Verme (Contextual Trade-Off)
Popüler veya güncel bir yaklaşımın kullanılması tek başına yeterli gerekçe değildir. Aşağıdaki ikilemlerin hiçbiri evrensel olarak doğru değildir:
- *Pagination* yerine *Load More* veya *Load More* yerine *Infinite Scroll*,
- *Modal* yerine *Drawer* veya *Tab* yerine *Ayrı Sayfa*,
- *Monolith* yerine *Microservices*,
- *Yeni servis/tablo açmak* yerine *mevcut servisin/şemanın geliştirilmesi*.

Uzmanlar her karar için **kullanıcı profili, kullanım sıklığı, veri hacmi, teknik maliyet, erişilebilirlik ve iş hedeflerini** değerlendirmeli ve neden diğer alternatifin elendiğini (`rejected_alternatives`) açıklamalıdır.

### 0.5 Mevcut Yapıyı Koruma ve Geliştirme
- Önce mevcut projeyi ve mimariyi anla; çalışan özellikleri gereksiz yere yeniden tasarlama.
- Mevcut component, servis, API ve tasarım sistemlerini yeniden kullanma potansiyelini incele.
- Yeni bir çözüm önermeden önce **mevcut çözümün neden yeterli olmadığını (`rejected_alternatives`)** kanıtla açıkla.
- Tasarım sistemi (`DESIGN.md`, `themes.css`) varsa onu temel al; her ekranda farklı bir tasarım dili oluşturma.
- Yeni teknoloji veya kütüphane öneriyorsan mevcut yapıya sağlayacağı gerçek katkıyı ve bakım maliyetini belirt.

### 0.6 Kanıt, Eleştiri ve Kalite Standardı
- Her önemli tespit gözlemlenebilir kanıta (`dosya:satır`, `context-snapshot.json`, `knowledge-graph.json`) dayanmalıdır; varsayımlar doğrulanmış bulgu gibi sunulamaz.
- Aynı problem farklı başlıklarla veya farklı dizilerde (`audits[]`, `ui_ux_mismatches[]`, `new_features[]`) tekrar tekrar raporlanamaz (`V5` kapısı).
- Hiçbir uzman sırf rapor dolu görünsün diye bulgu üretmek zorunda hissetmemelidir; temiz modülde boş dizi döndürmek esastır.
- Önerilerin **beklenen faydası (`expected_value`), maliyeti (`effort`) ve riski (`risks`)** birlikte değerlendirilmelidir.

---

## 1. 6 Uzman Şapka ve Ortak Karar Sürecindeki Rol Dağılımı

| Sıra | Dosya | `agent_id` | Önek | Konsey Kararına Temel Katkısı |
| :---: | :--- | :--- | :---: | :--- |
| 1 | [`agents/01-snr-product-owner.md`](../agents/01-snr-product-owner.md) | `snr-product-owner` | `PO` | **Kullanıcı ihtiyacı, ürün değeri, iş hedefi ve öncelik** (PRD uyumu, çekirdek modüller, RICE) |
| 2 | [`agents/02-snr-software-architect.md`](../agents/02-snr-software-architect.md) | `snr-software-architect` | `ARCH` | **Mimari doğruluk, teknik uygulanabilirlik, ölçeklenebilirlik** (5 katmanlı mimari, DTO/DB/API sözleşmesi) |
| 3 | [`agents/03-principal-ui-ux-specialist.md`](../agents/03-principal-ui-ux-specialist.md) | `principal-ui-ux-specialist` | `UX` | **Kullanılabilirlik, tasarım kalitesi ve etkileşim** (Living Surface, 16 tema, 55+ bileşen, Zero-CLS 4 durum) |
| 4 | [`agents/04-snr-seo-specialist.md`](../agents/04-snr-seo-specialist.md) | `snr-seo-specialist` | `SEO` | **Organik erişilebilirlik, arama görünürlüğü, teknik SEO ve Web Performansı** (Semantik HTML5, CWV, Bundle bütçesi) |
| 5 | [`agents/05-snr-growth-marketing.md`](../agents/05-snr-growth-marketing.md) | `snr-growth-marketing` | `GRW` | **Edinim, aktivasyon, dönüşüm, büyüme ve gelir potansiyeli** (AARRR, Aha! Moment, elde tutma döngüleri) |
| 6 | [`agents/06-snr-qa-security-auditor.md`](../agents/06-snr-qa-security-auditor.md) | `snr-qa-security-auditor` | `QA` | **Kalite, güvenlik, risk, test kapsamı ve üretim güvenilirliği** (OWASP, RBAC/IDOR/RLS, 5 katmanlı TDD) |

> **Çok-Şapkalı Ortak Değerlendirme Kuralı:** Bir konu birden fazla şapkanın alanına giriyorsa her uzman kendi merceğinden katkı sunar ve `synergy_clusters` altında birleştirilir. Örneğin yeni bir **Onboarding** akışında `PO` kullanıcı ihtiyacını, `UX` etkileşimi, `GRW` aktivasyonu, `ARCH` teknik uygulanabilirliği, `QA` ise güvenlik ve kalite risklerini değerlendirir.

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

## 4. Faz 3 — Ezilmezlik, Baş Hakem, V1–V8 Anti-Slop Kapıları ve 2. Tur Çapraz Sorgu (`council_merger.py`)

6 uzmanın JSON çıktıları diske yazıldıktan sonra **Baş Hakem (Chief Council Arbiter)** serbest metin yazmadan önce deterministik birleştiriciyi çalıştırır:

```bash
python .agent/skills/feature-architect/scripts/council_merger.py --inputs docs/plans/council/<YYYY-MM-DD> --project-root . --kg docs/plans/council/<YYYY-MM-DD>/project-knowledge-graph.json --challenges docs/plans/council/<YYYY-MM-DD>/challenges.json --output docs/plans/council/<YYYY-MM-DD>/merged.json
```

### Birleştirme, V1–V11 Kanıt Yönetişimi, 7 Soruluk Karar İzlenebilirliği ve Hakem Kuralları
1. **Sağlık Skoru, `health_score_rationale`, 4 Eksenli Hazırlık Radarı ve `CRITICAL` Tavanı:**
   - Aktif (`applicable`) uzmanlar eşit ağırlıkla (`1.0`) ortalanır; `not_applicable` uzmanlar (örn. web arayüzü olmayan CLI aracında SEO) paydadan çıkarılır (`not_applicable` olduğunda `health_score: null` ve bulgu dizileri boş olmalıdır).
   - Aktif her uzman puanının neden kırıldığını `health_score_rationale` (min 20 karakter) alanında somut bulgu sayılarıyla açıklar.
   - Tekil skor yanında **4 Eksenli Hazırlık Radarı (`readiness_axes`)** hesaplanır: `product_depth` (`PO` + `GRW`), `architecture_contract_integrity` (`ARCH`), `ux_operational_readiness` (`UX` + `SEO`) ve `security_quality_assurance` (`QA`).
   - En düşük puanlı uzman **En Zayıf Halka** olarak karnede ayrıca vurgulanır.
   - Çözülmemiş tek bir `CRITICAL` bulgu dahi varsa **Proje Olgunluk Skoru en fazla `60.0` olabilir** (`critical_cap_applied: true`).
2. **V1–V11 Kanıt Yönetişimi ve Anti-Slop Kapıları (`governance`):**
   - **V1 (`HALLUCINATED_EVIDENCE_PATH`):** `--project-root` verildiğinde diskte var olmayan `dosya:satır` referansı taşıyan halüsinasyon bulgular `rejected_finding_ids` listesine alınarak elenir.
   - **V2 (`UNREACHABLE_LEGACY_COMPONENT`):** `--kg` (`project-knowledge-graph.json`) verildiğinde aktif hiçbir `Route` düğümünden erişilemeyen ölü/legacy bileşenler için açılan `STUB_PAGE` bulguları 6 şapkanın tamamında otomatik olarak **`REMOVE`** kararına çevrilir.
   - **V4 (`GENERIC_BOILERPLATE_CONSTRAINT`):** Projeye özgü dosya/sözleşme referansı içermeyen klişe kısıtlar bayraklanır.
   - **V5 (`CROSS_SECTION_DUPLICATE_FEATURE` / `CROSS_SECTION_DUPLICATE_MISMATCH`):** 6 şapkanın tamamında aynı raporda `audits[]` içinde yer alan bir sorunun `ui_ux_mismatches[]` veya `new_features[]` altında tekrar edilmesi engellenir ve mükerrer kayıtlar bastırılır.
   - **V6 (6 Şapka Yetki Sınırı ve Anti-Slop Kapıları):** `PO_BOUNDARY_TECHNICAL_ARCHITECTURE`, `PO_BOUNDARY_VISUAL_THEME`, `ARCH_BOUNDARY_VISUAL_STYLING`, `FABRICATED_METRIC_CLAIM` (kanıtsız `%XX artırır` metrik iddiaları), `SEO_PROTECTED_ROUTE_INDEXING` (korumalı rotalara indeks önerisi) ve `QA_CLIENT_ONLY_SECURITY_FIX` (sunucu doğrulaması olmadan salt istemci güvenlik yaması) uyarılarıyla tüm 6 şapka denetlenir.
   - **V7 (6 Karar Fiili Sınıflandırması — `decision`):** Her bulguya deterministik olarak `CONNECT | FIX | REFACTOR | COMPLETE | REMOVE | DEFER` fiillerinden biri atanır.
   - **V8 (Zero-Drop Kapısı):** Hiçbir `CRITICAL` veya `HIGH` bulgu kimliği konsolide raporda düşürülemez.
   - **V9 (`V9_UNADDRESSED_SNAPSHOT_DEFECTS`):** `--snapshot` (`context-snapshot.json`) verildiğinde doğrulanmış (`confirmed`) `CRITICAL`/`HIGH` kusurların 6 şapka tarafından ele alınıp alınmadığı denetlenir; atlanan kusurlar açıkça bayraklanır.
   - **V10 (`V10_PHANTOM_DONE_LOCALSTORAGE_PROPOSAL`):** Çok-kullanıcılı özelliklerde `localStorage`/`sessionStorage` ile sahte kalıcılık önerilmesi reddedilir.
   - **V11 (`V11_WEB_PERF_BAILOUT`):** Web/SPA projelerinde (`BUNDLE_BUDGET_RISK` veya `EAGER_SUBROUTER_BUNDLE` varken) `SEO` şapkasının `"not_applicable"` dönerek performans denetiminden kaçması engellenir.
   - **Konsey Klasörü Toplu Denetimi (`--audit-council-dir`):** Mevcut bir `docs/plans/council/<YYYY-MM-DD>/` klasöründeki `01..06-*.json` çıktıları, rol/önek uyumu, V1–V11 ihlalleri ve `/council` Borda hakemlik adayları `python .agent/skills/feature-architect/scripts/council_merger.py --audit-council-dir docs/plans/council/<YYYY-MM-DD>` komutuyla tek seferde denetlenebilir.
3. **2. Tur Çapraz Sorgu (`Round 2 Challenge Round` — `challenges.json`):**
   - `ARCH` şapkası, `PO` veya `UX` tarafından `COMPLETE` (sıfırdan geliştirme) önerilen bir akışın Backend'de hazır karşılığı varsa bunu kanıtıyla **`CONNECT`** kararına dönüştürür (`challenge_resolutions`).
   - `QA` şapkası, aynı konumda `CRITICAL` bir güvenlik/RBAC açığı varsa ilgili bulguya `blocked_by: ["QA-xx"]` güvenlik ön koşulu ekler.
4. **Sinerji Kümeleme (`synergy_clusters`):**
   - 2 veya daha fazla uzmanın aynı normalize dosya/uç konumunda bildirdiği bulgular **"Yüksek Öncelikli Ortak Hedef"** altında birleştirilir ve önem derecesi bir kademe yükseltilir (`MEDIUM -> HIGH`, `HIGH -> CRITICAL`).
5. **Çatışma Çözüm Masası (`conflict_candidates` -> Hibrit 3. Yol):**
   - Bir uzmanın önerisi başka bir uzmanın `non_negotiable_constraints` kırmızı çizgisiyle aynı konumda kesiştiğinde hiçbir uzman görüşü silinmez.
   - Baş Hakem her iki kırmızı çizgiyi de koruyan **Hibrit Mühendislik Çözümü (3. Yol)** üretir. Eğer 2+ geçerli hibrit mimari alternatif doğarsa `python .agent/skills/karpathy-guidelines/scripts/council_ranker.py --sample` protokolündeki Borda oylamasıyla kazanan hibrit yol seçilir.
6. **Beyond-PRD RICE Sıralaması (`features_ranked`):**
   - Yeni özellik önerileri `RICE = (reach * impact_score * confidence) / effort_puanı` (`S=1, M=2, L=3, XL=5`) formülüyle puanlanır; birden fazla uzmanın önerdiği aynı başlıklı özellikler birleştirilip ortak imzayla en üste taşınır.
7. **7 Soruluk Karar İzlenebilirliği ve Red/Erteleme Kaydı (`decision_traceability_log` & `deferred_and_removed_decisions`):**
   - `council_merger.py`, her bulgu ve özellik önerisi için **7 Soruluk Karar İzlenebilirliği Matrisi (`decision_traceability_log`)** üretir:
     1. **Hangi problem çözülüyor?** (`problem_solved`)
     2. **Hangi kanıtlar bu kararı destekliyor?** (`supporting_evidence`)
     3. **Hangi uzmanlar destekliyor, hangileri itiraz ediyor / blokluyor?** (`supporting_agents` & `objecting_or_blocking_agents`)
     4. **Alternatifler neden elendi?** (`rejected_alternatives`)
     5. **Beklenen kullanıcı ve iş değeri nedir?** (`expected_user_business_value`)
     6. **Teknik ve operasyonel riskleri nelerdir?** (`technical_operational_risks`)
     7. **Karar kesin mi, koşullu mu, yoksa araştırma mı gerektiriyor?** (`decision_certainty`: `FINAL | CONDITIONAL | RESEARCH_REQUIRED`)
   - Reddedilen (`REMOVE`) veya ertelenen (`DEFER`) hiçbir önerinin gerekçesi kaybolmaz; `deferred_and_removed_decisions` altında kalıcı olarak arşivlenir.
8. **Zorunlu Zero-Drop Doğrulama Kapısı (`--check-report`):**
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
