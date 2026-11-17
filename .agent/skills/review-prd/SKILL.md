---
name: review-prd
description: >-
  Dışarıdan verilen PRD dokümanını mevcut proje kod tabanı, 6 Şapkalı Konsey, Borda hakemliği ve 5 katmanlı mimariyle değerlendirip tek konsolide rapor üreten orkestratör. Tetikleyiciler: "/review-prd", "prd incele", "prd değerlendir", "review prd", "evaluate prd". Tetiklenmez: tamamlanmış kodun retrospektif denetimi verify-prd'ye, sıfırdan yazım doc-coauthoring'e aittir. Tam sözlük: .agent/rules/skill-trigger-routing.md
---

# PRD Değerlendirme & Konsey Orkestratörü (`/review-prd`)

Bu yetenek; kullanıcının elindeki yeni veya dışarıdan gelen bir PRD dokümanını (`docs/*-prd.md`, taslak şartname veya sohbet metni), **mevcut proje kod tabanına ve kurumsal standartlara karşı** tek seferde uçtan uca inceler ve **hepsini içeren tek, detaylı konsolide değerlendirme raporu** üretir.

> ⛔ **Sınır Ayrımı:**
> - Geliştirme **öncesi** yeni/taslak PRD incelemesi: **`review-prd`** (bu skill).
> - Geliştirme **sonrası** tamamlanan işlerin retrospektif kod denetimi: [`verify-prd`](../verify-prd/SKILL.md).
> - Sıfırdan doküman yazımı: [`doc-coauthoring`](../doc-coauthoring/SKILL.md).

---

## Ne Zaman Kullanılır?

- Kullanıcı `"/review-prd"`, *"elimdeki PRD'yi incele"*, *"bu PRD'yi projeye göre değerlendir"*, *"review prd"* veya *"evaluate prd"* dediğinde.
- Yeni bir özellik/modül kodlanmadan önce mevcut mimari, veritabanı, UI token'ları ve kardeş uygulama üzerindeki etkisini ölçmek için.

---

## 3 Aşamalı Birleşik İnceleme Akışı (Tek Konsolide Çıktı)

Kullanıcı `/review-prd` çalıştırdığında aşağıdaki **3 aşamanın tamamı kesintisiz işletilir** ve sonucu tek bir kapsamlı raporda (`references/prd-review-template.md`) birleştirilir:

### Aşama 1: Proje Gerçekliği Taraması + 6 Şapka & Anti-Sycophancy Süzgeci
1. **Deterministik PRD & Bağlam Paketi:**
   ```bash
   python .agent/skills/review-prd/scripts/prd_review_helper.py --root . --prd <prd-dosya-yolu> --json
   ```
   *(PRD doğrudan sohbette metin olarak verildiyse, `PRD` içeriğindeki `FR`/`US` maddeleri, belirsiz ifadeler ve `PROJECT_BRIEF.md`, `PRODUCT.md`, `DESIGN.md`, `HANDOFF.md` dosyaları doğrudan okunur).*
2. **Mevcut Kod Tabanı & Kardeş Repo Taraması (`feature-architect`):**
   ```bash
   python .agent/skills/feature-architect/scripts/fa_scan.py --root . --out-dir docs/plans/prd-review-scan --format json
   ```
   - PRD'de istenen her gereksinimin mevcut projede karşılığı var mı etiketlenir: `[Hazır ✅]`, `[Kısmen ⚠️]`, `[Yeni Geliştirme 🔴]` veya `[Mevcut Kodla Çelişiyor ❌]`.
   - Kardeş uygulama (`--peer` / otomatik keşif) etkileniyorsa belirtilir.
3. **6 Şapkalı Konsey & Anti-Sycophancy (`/6HAT` + `/PUSHBACK`):**
   - `cognitive-counsel-framework.md` ("Onaylama, Sına" + 6 görünmez filtre: `REDTEAM`, `80/20`, `KILLCRITIC`, `TRUTHMODE`, `LINDYMODE`, `ELI5`) ve `feature-architect/agents/01..06` bakış açılarıyla PRD sınanır:
     * **`PO`:** Kapsam kayması, 80/20 MVP kesiti, ölçülebilir iş değeri, belirsiz ifadeler.
     * **`ARCH`:** Mevcut mimariyle uyum, veri modeli/migration etkisi, API sözleşmesi, kardeş repo bağımlılıkları.
     * **`UX`:** Akış sürtünmesi, `DESIGN.md` uyumu, 16 tema / 55+ bileşen / 18 dashboard eşleşmesi, Zero-CLS Skeleton ve 375px mobil ergonomi.
     * **`SEO`:** Public rotalar varsa teknik SEO/meta/JSON-LD; Auth-arkası SPA ise bundle/CWV etkisi.
     * **`GRW`:** Onboarding, aktivasyon, elde tutma ve ölçüm olayları.
     * **`QA`:** Edge case'ler, OWASP 20 madde güvenlik temeli, RLS/RBAC sınırları, eksik Gherkin (`Given-When-Then`) kabul kriterleri.

### Aşama 2: Mimari & Ürün İkilemleri Konseyi (`/council` + Borda Hakemliği)
- PRD içindeki belirsiz veya 2+ geçerli yaklaşım barındıran her kritik tercih (örn. *state yönetimi, gerçek zamanlı iletişim WebSocket vs SSE, senkron vs kuyruk, tek repo vs kardeş repo değişikliği*) için tarafsız `Option A`, `Option B`, gerekirse `Option C` çıkarılır.
- Deterministik Borda hakemliği (`council_ranker.py`) mantığıyla puanlanır ve gerekçeli kazanan seçenek belirlenir:
  ```bash
  python .agent/skills/karpathy-guidelines/scripts/council_ranker.py --sample
  ```

### Aşama 3: 5 Katmanlı Fizibilite, Tek Konsolide Rapor & `/plan` Köprüsü
1. Aşama 1 ve Aşama 2 çıktıları [references/prd-review-template.md](references/prd-review-template.md) şablonuna birebir oturtularak **tek bir detaylı konsolide rapor** üretilir.
2. Rapor kalıcı olarak proje içi `docs/plans/prd_review_<slug>_<YYYYMMDD_HHMMSS>.md` konumuna kaydedilir (`prd_review_helper.py --archive-report`).
3. ⛔ **Strict Approval Gate (Koda Dokunma Yasağı):** Rapor sunulduğunda **hiçbir üretim koduna dokunulmaz**. Kullanıcıya **GO / CONDITIONAL GO / REWORK** hükmü ve net karar soruları sunulur.
4. **Onay Sonrası Akış:** Kullanıcı *"devam et / plana çevir / onayla"* dediğinde raporun onaylanan maddeleri doğrudan `/plan` (`PLAN.template.md` + `archive_plan.py` + `HANDOFF.md` §3 + varsa `sync_sibling_handoff.py` & AI Agent sahiplik sorusu) akışına aktarılır.
