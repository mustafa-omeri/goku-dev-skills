# Feature Architect — Skillset Dashboard Eşleştirme Protokolü

Bu referans, `/feature-architect` çalışırken projedeki bir Dashboard eksikliğini veya revizyon ihtiyacını `.agent/skills/frontend-design/dashboard-theme/catalog.json` içindeki **18 doğrulanmış dashboard şablonuyla** nasıl eşleştireceğini tanımlar.

---

## 1. Üç Adımlı Eşleştirme Algoritması

### Adım 1: Proje Veri Profilini ve Yaşayan Yüzeyi Çıkar
Projeyi tararken şu 3 parametreyi belirle:
1. **Yaşayan Yüzey Modu (`surface`):** Mevcut uygulama kabuğu açık zeminli (`light`) mi, koyu zeminli (`dark`) mi? (`.agent/rules/design-skills-enforcement.md` §2.5 **Yaşayan Yüzey Önceliği** gereği açık zeminli bir projeye kullanıcı istemedikçe koyu tema dayatılmaz; koyu şablon seçilse dahi projenin yüzey token'larına uyarlanır).
2. **Birincil Veri Şekli (`archetype`):**
   - Çoklu proje / değerlendirme kartları ve ilerleme yüzdeleri ➔ `portfolio-grid` (`dashboard-theme-06`), `personal-workspace` (`dashboard-theme-08`)
   - Sıralanabilir kullanıcı / çalışan / kayıt dizini ve faset filtreler ➔ `operational-directory` (`dashboard-theme-03`)
   - Çok sütunlu analiz sonuçları, skor tabloları ve radial halkalar ➔ `assessment-results` (`dashboard-theme-10`)
   - Kurumsal kohort, tutundurma (retention), departman kıyaslama ve çoklu donut ➔ `enterprise-reporting` (`dashboard-theme-13`), `engagement-analytics` (`dashboard-theme-18`)
   - Çok eksenli radar grafiği (yetkinlik/kültür), anomali trendi ve telemetri ➔ `telemetry-monitoring-dark` (`dashboard-theme-14`)
   - Üst yönetim dönüşüm hunisi (Sankey/Funnel) ve çoklu zaman serisi ➔ `executive-analytics-dark` (`dashboard-theme-11`)
   - Organizasyon şeması / hiyerarşi ağacı ve sağdan açılan skor çekmecesi ➔ `org-hierarchy-inspector` (`dashboard-theme-12`)
   - Öncelikli kuyruk, destek/onay tablosu ve master-detail inceleme ➔ `triage-master-detail` (`dashboard-theme-16`)
   - Görev / iş akışı aşamaları ➔ `workflow-kanban` (`dashboard-theme-04`)
   - Anket / soru / kural oluşturucu sihirbazı ➔ `assessment-builder` (`dashboard-theme-05`)
   - Takım liderlik tablosu ve canlı aktivite akışı ➔ `team-collaboration` (`dashboard-theme-02`)
   - Dosya, belge ve medya havuzu ➔ `asset-repository` (`dashboard-theme-01`)
   - Sistem sağlığı, haftalık şerit ve hızlı özellik aç/kapat (toggle) ➔ `operational-control-deck` (`dashboard-theme-15`)
   - Takvim / randevu matrisi ve durum teşhisi ➔ `diagnostic-scheduler` (`dashboard-theme-07`)
   - Coğrafi dağılım ve çoklu lokasyon/şube izleme ➔ `geo-logistics` (`dashboard-theme-09`), `global-node-monitor-dark` (`dashboard-theme-17`)
3. **Eritilecek Yetim Veriler (`orphan_endpoints` & `orphan_fields`):** Backend'de hazır olup arayüzde gösterilmeyen verilerin hangi widget tipine (KPI kartı, halka grafik, radar grafik, sağ aktivite akışı, master-detail çekmece) oturduğunu eşle.

### Adım 2: Görsel Doğrulama
`catalog.json` içinden seçilen 2 veya 3 adayın `.webp` dosyalarını (`read_file` ile) incele; önerilen widget'ların görseldeki yerleşimle birebir örtüştüğünü teyit et.

### Adım 3: Kullanıcıya Gerekçeli Sunum ve Onay Sonrası Uyarlama
- Raporun **3.B** bölümünde seçilen 2–3 şablonu `id`, `title`, `archetype`, uygunluk gerekçesi ve hangi yetim/PRD verilerini hangi widget'ta göstereceğiyle birlikte listele.
- Kullanıcı şablonu seçtikten sonra:
  1. Şablonun **ızgara oranlarını ve bilgi hiyerarşisini** (`layout` + `widgets`) baz al.
  2. Renkleri ve tipografiyi şablondan kopyalamak yerine projenin mevcut `DESIGN.md` token'larından (`--bg-surface`, `--text-primary`, `--accent-primary`) uygula.
  3. Sayısal metriklerde `tabular-nums`, mobilde (375px) yatay kaydırmasız filtreler (`flex-wrap` veya bottom-sheet) ve tüm kart/tablolarda geometry-matched `.skeleton` kasetlerini zorunlu olarak kodla.
