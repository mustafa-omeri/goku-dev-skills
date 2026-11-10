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

### Aşama 4: Otonom İcra ve Dağıtım (Settlement Upon Explicit Approval Only)
Kullanıcı kararlarını girip plana açık onay verdiğinde (`proceed` / `onay`):
1. **API Dokümanları:** `docs/APIs/` altındaki ilgili modül dosyaları güncel parametre, şema ve response yapısıyla cerrahi güncellenir.
2. **RFC Belgeleri:** İlgili RFC'lerin altına `## Uygulama Gerçekliği & Revizyon Notu (As-Built)` bölümü eklenir.
3. **PRD / Şartname:** Alınan kararlara göre senkronize edilir.
4. **Kod Düzeltme İhtiyacı Varsa:** İlgili işler `HANDOFF.md` §3 canlı panosuna ve `KANBAN.md`'ye aktarılır.
