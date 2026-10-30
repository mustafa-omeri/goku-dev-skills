# Paid Media & Reklam Bütçesi Güvenlik Sözleşmesi (Guardrails)

> **Kaynak:** `nowork-studio/notfair-plugin` Cerrahi Entegrasyonu (`plans/notfair-plugin.md`)  
> **Kapsam:** Yapay zeka ajanlarının reklam kanalları (Google Ads, Meta Ads, LinkedIn Ads vb.) ile etkileşiminde bütçe ve güvenlik sınırları.

---

## 1. Kesin Kırmızı Çizgiler (Hard Refusals)

Yapay zeka ajanları bütçe ve para harcayan reklam platformlarında otonom serbestliğe sahip değildir. Aşağıdaki eylemler **açık ve yazılı insan onayı olmaksızın ASLA çalıştırılamaz**:

1. **⛔ Bütçe Artırma Yasağı:** Günlük veya kampanya bütçesini insan onayı olmadan tek bir kuruş bile artırmak kesinlikle yasaktır.
2. **⛔ Otomatik Kampanya Yayınlama Yasağı:** Yeni oluşturulan reklam metinleri, görselleri veya hedeflemeler "DRAFT / TASLAK" modunda kaydedilmeli; doğrudan canlıya alınmamalıdır.
3. **⛔ Kredi Kartı / Ödeme Yöntemi Manipülasyonu:** Ödeme yöntemlerine dokunulamaz, faturalandırma ayarları değiştirilemez.

---

## 2. İzin Verilen Otonom Eylemler (Read-Only & Diagnostic)

Ajanlar aşağıdaki optimizasyon ve teşhis adımlarını güvenle otonom yürütebilir:

- **Arama Terimleri Raporu (Search Terms Audit):** Alakasız veya bütçe yiyen anahtar kelimeleri tespit edip negatif anahtar kelime (`Negative Keywords`) listesi önermek.
- **Dönüşüm Takibi Doğrulaması:** Google Tag Manager (GTM) ve dönüşüm piksellerinin doğru sayfada tetiklendiğini doğrulamak.
- **Reklam Metni A/B Testi Önerisi:** Düşük CTR'lı reklamlara alternatif başlık ve açıklama varyasyonları üretmek.
- **Harcama Anomalisi Tespiti:** Günlük bütçenin beklenmedik hızda tükendiği (CPC patlaması) durumları tespit edip raporlamak.

---

## 3. Güvenli Onay Protokolü

Bir bütçe veya kampanya revizyonu önerildiğinde ajan kullanıcıya şu formatta sunum yapar:

```markdown
### 📢 REKLAM REVİZYON ONAY TALEBİ
- **Kampanya Adı:** [Kampanya]
- **Mevcut Durum:** [Mevcut harcama / ROAS / CPA]
- **Önerilen Değişiklik:** [Net eylem tanımı]
- **Bütçe Etkisi:** [Tahmini maliyet / harcama sınırı]
- **Gerekçe:** [Veriye dayalı analiz]
> ⚠️ Bu işlem reklam hesabınızda harcama yaratabilir. Uygulamak için "ONAYLIYORUM" yazınız.
```
