# 🔍 PRD Değerlendirme ve 6 Şapkalı Konsey Raporu (`[PRD Başlığı]`)

> **Tarih:** `[YYYY-MM-DD]` · **Hedef Proje:** `[Proje Adı]` · **Teknoloji Yığını:** `[Stack]`  
> **İncelenen PRD:** `[docs/...-prd.md veya Sohbet Metni]`  
> **Nihai Hüküm:** **`[GO ✅ | CONDITIONAL GO ⚠️ | REWORK 🔴]`**  
> **Aktif Süreçler:** `review-prd`, `cognitive-counsel-framework` (`/6HAT`, `/PUSHBACK`), `council` (Borda), `feature-architect` (`fa_scan.py`), `doc-coauthoring`

---

## 1. Yönetici Özeti & Hüküm (Executive Verdict)
- **Genel Değerlendirme:** `[PRD'nin güçlü yönleri ve en kritik 2-3 riski]`
- **Hazırlık Puanı:** `[XX / 100]`
- **Neden bu hüküm verildi?:** `[GO / CONDITIONAL GO / REWORK net gerekçesi]`

---

## 2. PRD Gereksinimleri vs Mevcut Proje Gerçekliği Matrisi
> `fa_scan.py` ve `prd_review_helper.py` kanıtlarıyla mevcut kodda neyin hazır, neyin eksik olduğu:

| PRD ID / Bölüm | Gereksinim Özeti | Mevcut Kod Durumu | İlgili Dosya / Uç | Kardeş Uygulama Etkisi |
|---|---|---|---|---|
| `FR-001` | `[Özet]` | `[Hazır ✅ | Kısmen ⚠️ | Yeni 🔴 | Çelişki ❌]` | `[dosya:satır veya Yok]` | `[Yok / Kardeş Repo Adı]` |

---

## 3. 6 Şapkalı Konsey & Anti-Sycophancy Değerlendirmesi (`/6HAT` + `/PUSHBACK`)

| Şapka | Skor (`0-100`) | Kritik Bulgular, Çelişkiler & Açıklar | Önerilen Düzeltme / Somut Aksiyon |
|---|:---:|---|---|
| **`PO` (Değer & Kapsam)** | `[0-100]` | `[80/20 MVP kesiti, kapsam kayması, belirsiz ifadeler]` | `[Öneri]` |
| **`ARCH` (Mimari & Veri)** | `[0-100]` | `[DB şeması, API kontratı, kardeş repo, teknik borç]` | `[Öneri]` |
| **`UX` (Deneyim & Tasarım)** | `[0-100]` | `[DESIGN.md uyumu, Zero-CLS Skeleton, mobil ergonomi]` | `[Öneri]` |
| **`SEO` (Keşif & Web Perf)** | `[0-100 / N/A]` | `[Meta/JSON-LD veya SPA bundle/CWV etkisi]` | `[Öneri]` |
| **`GRW` (Büyüme & Ölçüm)** | `[0-100]` | `[Aktivasyon, retention, eksik telemetri olayları]` | `[Öneri]` |
| **`QA` (Red-Team & Güvenlik)** | `[0-100]` | `[OWASP, RBAC/RLS, edge case, eksik Gherkin senaryoları]` | `[Öneri]` |

### Belirsiz / Ölçülemez İfadeler ve Eksik Gherkin Senaryoları
- `[Satır X: "hızlı / kullanıcı dostu / vb." -> Önerilen somut SLA veya Gherkin Scenario]`

---

## 4. Mimari & Ürün İkilemleri Konseyi (`/council` — Borda Hakemliği)
> PRD'deki her 2+ alternatifli karar için Option A vs Option B değerlendirmesi:

| İkilem Konusu | Option A (Yalın) | Option B (Genişletilebilir) | Kazanan & Borda Gerekçesi |
|---|---|---|---|
| `[örn. Gerçek zamanlı bildirim]` | `[Polling / SSE]` | `[WebSocket]` | `[Seçilen seçenek + gerekçe]` |

---

## 5. 5 Katmanlı Dikey Dilim Fizibilitesi & Kardeş Uygulama Etkisi

| Katman | Gereken İş | Risk / Not |
|---|---|---|
| **1. DB / Şema / Migration** | `[Yeni tablolar, kolonlar, indeksler, RLS]` | `[Not]` |
| **2. Backend / View / RPC** | `[Endpoint, DTO, validasyon, RBAC]` | `[Not]` |
| **3. İstemci API Entegrasyonu** | `[Servis/hook, tip uyumu]` | `[Not]` |
| **4. Arayüz / UX & Skeleton** | `[Tema/bileşen/dashboard şablonu + Zero-CLS kasetleri]` | `[Not]` |
| **5. Döngü Kapanışı (Admin)** | `[Yönetim/moderasyon/geri bildirim ekranı]` | `[Not]` |
| **Kardeş Uygulama (Cross-Repo)** | `[Yok veya kardeş repoda yapılacaklar — v1.37.0 devir kuralı]` | `[Onayda sync_sibling_handoff.py + AI Agent sorusu]` |

---

## 6. Karar ve Sonraki Adım (Strict Approval Gate)
Değerlendirme tamamlandı; henüz hiçbir üretim koduna dokunulmadı. İlerlemek için lütfen tercihinizi belirtin:
1. **PRD Revizyonu:** Yukarıdaki kritik açıklar/belirsizlikler önce PRD dosyasına işlensin mi?
2. **`/plan` Başlatma:** Onaylanan kapsam ve seçilen Konsey opsiyonları doğrudan `/plan` (`PLAN.template.md` + `HANDOFF.md` §3) sürecine alınsın mı?
3. **Kardeş Uygulama (Varsa):** Kardeş uygulamanın `HANDOFF.md` dosyası mühürlendikten sonra geliştirmeyi bu ajan mı yapsın, kardeş uygulamadaki AI Agent mı devralsın?
