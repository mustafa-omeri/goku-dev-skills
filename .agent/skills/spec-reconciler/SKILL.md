---
name: spec-reconciler
description: >
  Backend ve frontend kod tabanlarını çapraz tarayarak RFC ve API dokümantasyonunu güncel koda eşitler, PRD çelişkilerini tespit eder ve kullanıcı kararıyla planlama üretir. Tetikleyiciler: "/spec-reconcile", "spec reconcile", "[SPEC-RECONCILE]", "api dokümanlarını güncelle", "rfc güncelle", "şartname çelişkisi", "reconcile specs", "sync api docs". Tetiklenmez: anlık sprint kabul denetimi `verify-sprint`'e, tekil kod incelemesi `code-review`'e aittir. Tam sözlük: .agent/rules/skill-trigger-routing.md
---

# Specification & API Reconciler (`spec-reconciler`)

Bu yetenek; backend ve frontend kod tabanlarını eşzamanlı tarayarak canlı kod ile RFC, PRD ve `docs/APIs/` dokümanları arasındaki sapmaları (**Documentation Drift / Spec Drift**) ortaya çıkarır; kullanıcıya her çelişki için karar alanı sunan etkileşimli bir uzlaşma planı üretir.

---

## Ne Zaman Kullanılır?

- Kullanıcı *"API dokümanlarını güncelle"*, *"RFC'leri koda göre eşitle"*, *"şartname çelişkilerini raporla"*, *"/spec-reconcile"* veya *"reconcile specs"* dediğinde.
- Büyük refactoring veya uzun geliştirme dönemlerinden sonra dokümanların koddan koptuğu düşünüldüğünde.
- Backend ve frontend ekiplerinin/modüllerinin API sözleşmesi kopukluklarını tespit etmek için.

---

## 4 Aşamalı Eşitleme ve Uzlaşma Protokolü

```ascii
[Backend & Frontend Kod Tabanı]
              │
              ▼ (Aşama 1: Çift Taraflı Tarama)
[Canlı API & İstemci Çağrı Matrisi]
              │
              ▼ (Aşama 2: 3-Yönlü Çelişki Taraması)
[Kod vs docs/APIs vs RFC vs PRD]
              │
              ▼ (Aşama 3: İnteraktif Karar Planı)
[Kullanıcı Comment & Seçenek Alanı (Artifact)]
              │
              ▼ (Aşama 4: Otonom İcra - Proceed)
[Doküman Güncelleme + Backlog Senkronu]
```

### Aşama 1: Çift Taraflı Kod Taraması (Cross-Repository Scan)
Ajan, deterministik CLI tarayıcısını çalıştırarak canlı rotaları ve istemci çağrılarını haritalandırır:

```powershell
# Temel tarama:
python .agent/skills/spec-reconciler/scripts/reconcile_scanner.py

# Ayrı backend ve frontend yollarıyla tarama:
python .agent/skills/spec-reconciler/scripts/reconcile_scanner.py --backend <be-path> --frontend <fe-path> --docs-api docs/APIs --rfcs docs/rfc --prd PRODUCT.md

# JSON formatında analiz çıktısı:
python .agent/skills/spec-reconciler/scripts/reconcile_scanner.py --json
```

### Aşama 2: 3-Yönlü Çelişki Analizi (Triple Drift Detection)
Tarama motoru üç temel sapma türünü sınıflandırır:
1. **Belgelenmemiş Endpoint (Docs Drift):** Kodda olan fakat `docs/APIs/` altında yer almayan endpoint'ler.
2. **Yetim Frontend Çağrısı (Contract Mismatch):** Frontend'in çağırdığı fakat backend'de karşılığı bulunmayan veya URL'i değişmiş rotalar.
3. **Şartname / Tasarım Sapması (Spec Contradiction):** PRD veya RFC'deki kural ile canlı kod davranışının ayrışması.

### Aşama 3: İnteraktif Karar Planı (Artifact Plan with User Feedback)
Ajan doğrudan koda dalıp tek taraflı varsayımda bulunmaz. Kullanıcıya özel bir plan dokümanı (`request_feedback: true`) sunar. Şablon:
`references/reconciliation-plan-template.md`

Her çelişki için:
- **Canlı Kod Davranışı**
- **Doküman / RFC Tanımı**
- **Eşitleme Seçenekleri:** `[Seçenek A: Koda Uydur]` vs `[Seçenek B: Şartnameye Uydur]`
- **💬 Kullanıcı Kararı / Comment Alanı**

---

### 🛑 ZORUNLU ONAY KAPISI (STRICT APPROVAL GATE - DURMA KURALI)
> [!CRITICAL]
> **Kullanıcı Kararı & Onayı Olmadan İcra YASAKTIR:**
> Ajan Aşama 3'te Uzlaşma Planı artifact'ını (`reconciliation_plan.md`) oluşturduktan veya Markdown raporunu sunduktan sonra **KESİNLİKLE VE İSTİSNASIZ OLARAK DURUR (`STOP CALLING TOOLS`)**.
> - Raporu hazırladığı turda **HİÇBİR** doküman (`docs/APIs/`, `RFCs/`, `PRODUCT.md`) ve **HİÇBİR** kod dosyasında tek bir satır dahi değişiklik (develop / refactor / update) **YAPILAMAZ**.
> - Ajan "bunları geliştirdim / icra ettim" şeklinde kendi kendine karar vererek peşin icraya geçemez.
> - Yalnızca kullanıcı planı inceleyip tercihlerini belirttikten sonra açık onay verdiğinde (`proceed`, `onaylıyorum`, `A seçeneklerini uygula` vb.) Aşama 4'e geçilir.

---

### Aşama 4: Otonom İcra ve Dağıtım (Plan Onayı Sonrası 4 Altın Kural)
Kullanıcı planı onayladığında veya *"onay"*, *"proceed"*, *"geliştir"*, *"devam et"* dediğinde yapı **otonom olarak aşağıdaki 4 aksiyonu sırasıyla alır**:

1. **`<plan>.md` Dosyasını Arşivleme ve Tarih-Saat Damgasıyla Taşıma:**
   - Üretilen uzlaşma planı (ör. artifact veya geçici konumdaki `<plan>.md`), proje kökündeki `docs/plans/` dizini altına taşınır/kopyalanır.
   - Dosya adı tarih-saat damgası ile adlandırılır:
     Format: `docs/plans/reconciliation_plan_<slug>_<YYYYMMDD_HHMMSS>.md` (veya `docs/plans/reconciliation_plan_<YYYYMMDD_HHMMSS>.md`).
     *(İpucu: `python .agent/skills/spec-reconciler/scripts/reconcile_scanner.py --archive-plan <plan-path> --slug <slug>` komutuyla otomatik taşınabilir).*

2. **Yalnızca Dokümanların Eşitlenmesi ve Kod Dokunulmazlığı (Docs-Only Sync Gate):**
   - Bu adımda **KESİNLİKLE KODA DOKUNULMAZ / KOD GELİŞTİRMESİ YAPILMAZ**.
   - Yalnızca ve yalnızca dokümanlar güncellenir:
     * `docs/APIs/` altındaki API dokümanları güncel parametre, şema ve response yapısıyla eşitlenir.
     * İlgili RFC dokümanlarının sonuna `## Uygulama Gerçekliği & Revizyon Notu (As-Built)` bölümü eklenir.
     * PRD (`PRODUCT.md` / `*-prd.md`) dokümanları kullanıcı tercihlerine göre senkronize edilir.
   - Kod değişiklikleri ise doğrudan koda yazılmak yerine `HANDOFF.md` §3 Canlı Görev Panosuna (ve `KANBAN.md` backlog'una) aktarılır.

3. **HANDOFF.md Canlı Panosuna Plan Referanslı Maddeleme (Traceable Plan Backlog):**
   - `HANDOFF.md` §3 Canlı Görev Panosu (veya `SPRINT_PLAN.md` / `KANBAN.md`) altına yazılacak her kod geliştirme görevi, 1. maddede `docs/plans/` altına taşınan plan dosyasına açık referans (`file:///.../docs/plans/<plan_file>.md#L...` veya `[docs/plans/<plan_file>.md]`) verilerek işaretlenir.
   - Örnek format: `🎯 1. ⏭️ [RFC-001] (docs/plans/reconciliation_plan_ocai_20261110_165000.md): /api/v1/auth/login endpoint parametre uyumu`.
   - Böylece onaylanan plan ile kod geliştirme fazı %100 izlenebilir (traceable) kalır.

4. **Öncelikli Protokol Kalkanı & Sıradaki İş Önerisi (Anti-Prompt-Drift & Next Work Suggestion):**
   - Kullanıcı aksini açıkça ve özellikle belirtmedikçe ("kodu şimdi yaz, dokümanları sonra yap" gibi açık muafiyet vermedikçe), ilk 3 madde **mutlak ve daima geçerlidir**.
   - Kullanıcıdan *"geliştir"*, *"devam et"*, *"kodu tamamla"*, *"uygula"* gibi tetikleyiciler gelse bile ajan doğrudan koda dalmaz; **önce 1, 2 ve 3. maddeleri icra eder**.
   - Dokümanlar eşitlenip kod görevleri plan referansıyla `HANDOFF.md` panosuna mühürlendikten sonra, kullanıcıya en uygun sıradaki iş (`HANDOFF.md` §3 canlı panosundaki 1 numaralı görev) önerilir ve kullanıcıdan o görevin kodlamasını başlatmak için teyit istenir.
