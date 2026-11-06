---
name: verify-sprint
description: Aktif sprint ve en son tamamlanan sprint hedeflerinin kabul kriterlerini, Gherkin senaryolarını ve beş katmanlı dikey dilimini doğrulayan sprint denetim orkestratörü. Tetikleyiciler: "/verify-sprint", "verify sprint", "[VERIFY-SPRINT]", "sprinti doğrula", "sprint bitti mi", "verify active sprint", "sprint acceptance audit". Tetiklenmez: tüm projenin geçmiş retrospektif taraması `verify-prd`'ye, tek oturumluk son kod değişiklikleri `verify-last`'a aittir. Tam sözlük: .agent/rules/skill-trigger-routing.md
---

# Verify Sprint (Mezo / Aktif & Son Sprint Denetim Orkestratörü)

Bu yetenek, projenin **aktif sprinti** (`SPRINT_PLAN.md`) ve hemen öncesinde tamamlanan sprint sınırındaki kartları denetler. Amaç; sprint hedeflerinin, kart kabul kriterlerinin (Gherkin AC) ve 5 katmanlı dikey dilimin eksiksiz olduğunu kanıtlamak ve sprinti güvenle kapatmaktır.

---

## Ne Zaman Kullanılır?

- **🔒 Otonom Sprint Kapanış Kilidi (Sprint-Done Lock):** Sprint kapsamındaki son kart `Yapıldı` sütununa taşındığında veya sprintin bittiği beyan edildiğinde ajan manuel komut beklemeden **otonom olarak** tetikler.
- Kullanıcı *"bu sprint bitti mi"*, *"sprinti doğrula"*, *"/verify-sprint"* veya *"sprint kabul denetimi"* dediğinde.
- Bir sprintteki kartlar `Yapılıyor`'dan `Yapıldı`'ya taşınmadan hemen önce.
- `RELEASE_PLAN.md` hazırlanırken ve sprint kapanış devri yapılırken.

---

## Deterministik CLI Denetim Kapısı

Sprint kabul ve 5 katman bütünlüğü prompt tahminine bırakılmaz; aşağıdaki kapı ile mekanik olarak taranır:
```powershell
python .agent/skills/verify-sprint/scripts/sprint_auditor.py
# veya JSON çıktısı:
python .agent/skills/verify-sprint/scripts/sprint_auditor.py --json
```

---

## 5 Aşamalı Sprint Denetim ve Bulgu İşleme Protokolü

### 1. Kart Kabul Kriterleri (Gherkin AC) Doğrulaması
- `SPRINT_PLAN.md` ve `KANBAN.md` içindeki aktif kartların `specs/<kart-id>.feature` dosyalarını tara.
- Her senaryonun (`Given / When / Then`) karşılığı olan entegrasyon/uçtan uca testin yeşil olduğunu doğrula.
- Gherkin dosyası veya testi olmayan kartlar `Yapıldı` sütununa taşınamaz.

### 2. Kart Başına 5 Katmanlı Dikey Dilim Denetimi
Sprint kapsamındaki her özellik için 5 katmanı doğrula:
1. **DB / Migration:** Gerekli migration dosyası yazıldı ve uygulandı mı?
2. **Backend / View / RPC:** SQL view veya endpoint tipi hazır mı?
3. **API & Tip Entegrasyonu:** İstemci hook ve TypeScript tipleri bağlandı mı?
4. **UI & Kullanıcı Etkileşimi:** Arayüz bileşeni canlı veriyle çalışıyor mu?
5. **Yönetim / Giriş Formu:** Verinin sisteme giriş yolu tamamlandı mı?
*Katmanlardan biri eksikse kart `Yapıldı` olamaz; `YARIM (Eksik Katman)` işaretlenir.*

### 3. Kullanıcı Test Rehberi Adımları
- `docs/KULLANICI_TEST_REHBERI.md` kontrol edilir: Kart için kullanıcının tarayıcıda gözüyle doğrulayabileceği adımlar yazılmış mı?
- Kullanıcı test adımı sunulmadan kart kapatılamaz.

### 4. Pano & Plan Senkronizasyonu
- `KANBAN.md` WIP limiti (maksimum 3 kart) aşılmış mı?
- Kapanmayan açık kartlar `RELEASE_PLAN.md`'ye aktarılmış mı?
- `HANDOFF.md` §3 canlı görev panosu güncellenmiş mi?

### 5. Sprint Engellenme, Otonom Cerrahi Onarım ve İzlenebilirlik Protokolü (Zorunlu İcra Adımı)
⛔ **Engellenen Sprinti Raporda Bırakıp Çekilme Yasağı:** Denetim sonucunda bir kartın testi kırmızıysa veya katmanı eksikse sprint kapanışı `ENGELLENDİ` ilan edilir ve şu döngü tavizsiz işletilir:
1. **`KANBAN.md` Geri Çekme:** Eksik/başarısız kart asla `Yapıldı`'da bırakılamaz. Derhal `Yapılıyor` veya `Bekliyor` sütununa geri çekilir; durum `🔴 Kapatılamaz (YARIM)` olarak işaretlenir.
2. **`RELEASE_PLAN.md` Senkronu:** Sprint kapsamından çıkarılan veya ötelenen kartlar `RELEASE_PLAN.md` içindeki Ötelenen Kartlar bölümüne kaydedilir (`sprint-delivery-workflow.md` §2.4).
3. **`HANDOFF.md` §3 Canlı Görev Panosu:** Kapanmayan kartın eksik parçası, `HANDOFF.md` §3 tablosuna `1. ⏭️ [DOM]-US-XXX` formatıyla en üst sıradan kaydedilir.
4. **Tam Otonom Cerrahi Onarım Döngüsü (Auto-Remediation Loop - Seçenek A):**
   - Ajan ara onay sormadan bulguları cerrahi olarak çözer (`tdd` ile eksik katman inşası, `fix-bug` ile mock kalıntısı temizliği, `db-migration-enforcement` ile migration oluşturma).
   - Yeni doğrulama ve regresyon testlerini çalıştırıp yeşile (PASS) çevirir.
5. **Kalıcı İzlenebilirlik ve Denetim Kaydı (Verification & Remediation Audit Trail):**
   - Onarım tamamlandıktan sonra `SPRINT_PLAN.md` ve `RELEASE_PLAN.md` dosyalarına deterministik formatta denetim kaydı işlenir:
   ```markdown
   ### 🛡️ Sprint Doğrulama & Cerrahi Onarım İzlenebilirlik Kaydı (Audit Trail)
   - **Kart / Madde:** `[Kart ID]` · `[Madde Başlığı]` (Sprint: S[X], Madde: [Y])
   - **1. İlk Geliştirme Durumu:** ✅ Geliştirme tamamlandı, ilk birim/entegrasyon testleri yeşil (PASS).
   - **2. /verify-sprint Denetim Bulgusu:** ❌ [Tespit edilen spesifik bulgu, eksik katman veya şartname sapması].
   - **3. Planlanan ve Uygulanan Onarım:** 🛠️ [Yapılan cerrahi müdahale, açılan dosya/katman, kaldırılan mock].
   - **4. Onarım Doğrulama Testleri:** 🧪 [Çalıştırılan yeni/regresyon testleri ve komutları] -> ✅ PASS.
   - **5. İkinci Denetim Sonucu:** 🎯 Yeni `/verify-sprint` çalıştırıldı -> Sıfır bulgu (Zero Findings), kart resmen `Yapıldı` sütununa taşındı ve sprint onaylandı.
   ```
6. **İkinci Kontrol (Re-Audit) ve Kapanış:**
   - `python .agent/skills/verify-sprint/scripts/sprint_auditor.py` tekrar çalıştırılır.
   - Sıfır bulgu (Zero Findings) kanıtlandığında kart resmen `Yapıldı` yapılır ve sprint `ONAYLANDI` olarak kapatılır.

---

## Standart Çıktı Raporu

```markdown
### 📋 VERIFY-SPRINT: SPRİNT KABUL & BÜTÜNLÜK RAPORU

- **Sprint:** [Sprint Numarası / Hedefi]
- **Kart Durumu:** [X adet Yapıldı, Y adet Bekliyor / Kapatılamayan]

#### Kart Bazlı Katman Denetimi
| Kart ID | İş Başlığı | Gherkin Test | 5 Katman | Kullanıcı Testi | Sonuç |
|---|---|---|---|---|---|
| [ID] | [İş Başlığı] | ✅ Yeşil | ✅ 5/5 Tam | ✅ Yazıldı | ✅ Kapatılabilir |
| [ID] | [İş Başlığı] | ❌ Eksik | ⚠️ 3/5 (Form Yok) | ❌ Yok | 🔴 Kapatılamaz (YARIM) |

#### Sprint Kapanış Kararı: [ONAYLANDI / ENGELLENDİ]
- Engellenme gerekçesi (varsa): ...

#### Yapılan Sistem Durumu Güncellemeleri
- **KANBAN.md:** [Geri çekilen kartlar ve güncel sütun durumları]
- **RELEASE_PLAN.md:** [Ötelenen / sonraki sprinte aktarılan maddeler]
- **HANDOFF.md §3:** [Canlı panoya 1. sıradan eklenen blocker işler]

#### Önerilen Aksiyon & Onarım Menüsü
1. ⚡ **Engelleri Şimdi Çöz (Fix Blockers Now):** `tdd` veya `fix-bug` ile eksik katman veya Gherkin testini hemen tamamlayıp sprinti kapat.
2. 📋 **Kartları Devret & Sprinti Kapat (Defer & Close):** Kapanmayan kartları sonraki sprinte aktarılmış haliyle bırakıp devir raporuna geç.
```
