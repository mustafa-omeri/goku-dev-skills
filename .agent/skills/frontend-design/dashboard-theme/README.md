# Dashboard Theme — Visual Reference Library & Verified Catalog

Bu klasör `frontend-design`, `ui-polish` ve `feature-architect` yetenekleri için doğrulanmış **18 adet dashboard mimari şablonunu** (`dashboard-theme-01.webp` → `dashboard-theme-18.webp`) ve makine tarafından okunabilir [`catalog.json`](./catalog.json) envanterini içerir.

## Ne Zaman Kullanılır?

1. Kullanıcı yeni bir `dashboard` istediğinde veya mevcut dashboard'u zenginleştirmek/yenilemek istediğinde,
2. `/feature-architect` komutu projede bir Dashboard eksikliği/zayıflığı tespit ettiğinde.

## Seçim ve Eşleştirme Protokolü

1. Önce [`catalog.json`](./catalog.json) dosyasından projenin veri profiline (`archetype`, `density`, `surface`, `widgets`, `best_for`) en uygun **2 veya 3 adayı** seç.
2. Seçilen adayların `.webp` görsellerini açarak projenin yaşayan yüzey moduyla (Living Surface Supremacy — Light/Dark) ve veri yoğunluğuyla uyumunu doğrula.
3. Layout'u piksel piksel kopyalama; **ızgara oranlarını, bilgi hiyerarşisini ve widget kombinasyonunu** projenin mevcut tasarım token'larıyla (`DESIGN.md`) uyarla.

## 18 Doğrulanmış Dashboard Mimarisi Özeti

| ID | Başlık | Arketip | Yüzey | Öne Çıkan Widget'lar & En Uygun Senaryo |
| :--- | :--- | :--- | :--- | :--- |
| `dashboard-theme-01` | Cloud Storage & Asset Repository Hub | `asset-repository` | Light + Dark Sidebar | Kategori kartları, klasör kutuları, son dosyalar tablosu, sağ depolama/yükleme rayı |
| `dashboard-theme-02` | Team Performance, Leaderboard & Activity Hub | `team-collaboration` | Light | 3 avatarlı KPI kartı, sıralama (leaderboard), tartışma grupları, sağ canlı aktivite akışı |
| `dashboard-theme-03` | Directory, HR & Filterable Entity Table | `operational-directory` | Light | Sol faset filtre kartı (proje/durum) + sağ sıralanabilir aksiyonlu veri tablosu |
| `dashboard-theme-04` | Multi-Stage Kanban & Workflow Board | `workflow-kanban` | Light + Indigo Rail | Rol filtre etiketleri + 4 sütunlu görev/onay Kanban panosu |
| `dashboard-theme-05` | Assessment, Survey & Questionnaire Builder | `assessment-builder` | Light | 4 adımlı sihirbaz + katlanabilir soru/kural satırları + sağ ağırlık/puanlama kartı |
| `dashboard-theme-06` | Portfolio & Multi-Project Progress Card Grid | `portfolio-grid` | Light | Durum sayaçlı filtre sekmeleri + 4×2 eşit boyutlu proje/değerlendirme ilerleme kartları |
| `dashboard-theme-07` | Diagnostic Status & Weekly Schedule Split-View | `diagnostic-scheduler` | Light | Görsel durum diyagramı + metrik kartları + sağ haftalık saat dilimli takvim matrisi |
| `dashboard-theme-08` | Personal Workspace, Welcome Hero & Daily Focus | `personal-workspace` | Light | Karşılama banner'ı + trend grafiği + radial ilerleme + sağ profil ve günlük ajanda rayı |
| `dashboard-theme-09` | Geo-Logistics, Route & Destination Overview | `geo-logistics` | Warm Light | Seviye göstergesi + özet kart + bölgesel harita ve sıralı lokasyon listesi |
| `dashboard-theme-10` | Scientific Assessment Table & Radial KPI Matrix | `assessment-results` | Light + Indigo Rail | Dikey zaman filtreleri + çok sütunlu sonuç tablosu + 4 radial KPI halkası + sağ geçmiş listesi |
| `dashboard-theme-11` | Dark Executive Funnel & Multi-Series Analytics | `executive-analytics-dark` | Dark | 5 sparkline KPI şeridi + Sankey dönüşüm hunisi + donut dağılım + çoklu alan grafiği |
| `dashboard-theme-12` | Organizational Hierarchy Tree & Score Inspector | `org-hierarchy-inspector` | Light + Dark Card | Hiyerarşik organizasyon ağacı + sağdan açılan profil ve çok halkalı skor çekmecesi |
| `dashboard-theme-13` | Enterprise Cohort, Retention & Segmentation Reports | `enterprise-reporting` | Light + Emerald Sidebar | Alt alan sekmeleri + 5'li metrik şeridi + 3 karşılaştırmalı donut + aktivite grafiği ve harita |
| `dashboard-theme-14` | Dark Telemetry, Anomaly Detection & Radar Diagnostics | `telemetry-monitoring-dark` | Dark Indigo | Anomali işaretli trend grafiği + çok eksenli radar grafiği (kültür/yetkinlik) + radial kartlar |
| `dashboard-theme-15` | System Health, Weekly Strip & Toggle Control Deck | `operational-control-deck` | Light + Purple Rail | Haftalık gün şeridi + 4 metrik kartı + 2×2 hızlı özellik aç/kapat (toggle) kontrol kartları |
| `dashboard-theme-16` | Priority Queue, Triage Table & Master-Detail Chat | `triage-master-detail` | Light + Dark Sidebar | Öncelikli kartlar + atanan/yeni kuyruk tabloları + sağ sekmeli detay ve mesajlaşma paneli |
| `dashboard-theme-17` | Dark Global Map, 7-Day Forecast & Multi-Node Monitor | `global-node-monitor-dark` | Dark | 7 günlük zaman kartları + saatlik çubuk grafik + interaktif dünya haritası ve lokasyon kartları |
| `dashboard-theme-18` | Engagement Analytics, Demographic Ring & Activity List | `engagement-analytics` | Warm Light + Dark Rail | Üst şirket/tenant seçici + vurgulu hero KPI + halka grafik + delta rozetli aktivite tablosu |
