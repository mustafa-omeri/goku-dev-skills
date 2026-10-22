# 🏛️ Çoklu Model & Ajan Hakemlik Protokolü (LLM Council Deliberation)

Bu kılavuz, Andrej Karpathy'nin `llm-council` mimarisinden esinlenerek, karmaşık mimari tercihlerde, belirsiz tasarım ikilemlerinde ve riskli refactoring süreçlerinde tek bir modelin önyargısına veya anlık halüsinasyonuna kapılmadan **3 Aşamalı Kör Hakemlik ve Konsensüs** (Anonymized Multi-Agent Deliberation) yürütmek için gereken standartları belirler.

---

## 1. Temel İlke ve Körleme (Blinding) Felsefesi

Tek bir modele veya ajana karmaşık bir mimari karar sorulduğunda şu riskler ortaya çıkar:
1. **Model/Sağlayıcı Önyargısı (Self-Preference Bias):** Modeller kendi ürettikleri çözümleri veya kendi şirketlerinin ekosistem araçlarını kayırmaya meyillidir.
2. **Onaylama Yanlılığı (Sycophancy):** Kullanıcının soruş şeklindeki yönlendirmeye kapılarak hatalı veya gereksiz karmaşık çözümü onaylama eğilimi.
3. **Kör Noktalar (Blind Spots):** Tek bir perspektifin gözden kaçırdığı sınır durumları (edge cases), bellek sızıntıları veya performans darboğazları.

Bu riskleri ortadan kaldırmak için **Körleme (Anonymization)** prensibi uygulanır: Alternatif çözümler tarafsız harflerle (`Option A`, `Option B`, `Option C`) etiketlenir ve kim tarafından önerildiği gizlenerek akran değerlendirmesine sunulur.

---

## 2. 3 Aşamalı Konsensüs Protokolü (3-Stage Protocol)

```
        [ Kullanıcı İsteği / Mimari İkilem ]
                         |
  +----------------------+----------------------+
  |                      |                      |
[ Aşama 1: Çözüm A ]  [ Aşama 1: Çözüm B ]  [ Aşama 1: Çözüm C ]
  (Minimal / Yerli)   (Esnek / Katmanlı)    (Hibrit / Standart)
  |                      |                      |
  +----------------------+----------------------+
                         |
       [ Körleme: Kimlikler Gizlenir ]
                         |
  +----------------------+----------------------+
  |                      |                      |
[ Hakem 1 Değerlendirmesi ] [ Hakem 2 Değerlendirmesi ] [ Hakem 3 Değerlendirmesi ]
  (Eleştiri + Sıralama)     (Eleştiri + Sıralama)       (Eleştiri + Sıralama)
  |                      |                      |
  +----------------------+----------------------+
                         |
           [ Ortalama Sıralama Hesabı ]
             (council_ranker.py)
                         |
                         v
       [ Aşama 3: Başkan Sentezi (Chairman) ]
       (En iyi parçaları birleştirip nihai kararı üretir)
```

### Aşama 1: Bağımsız İlk Seçenekler (First Opinions)
- Karar tek bir yola zorlanmaz; 2 veya 3 farklı uygulanabilir yaklaşım çıkarılır.
- **Option A (Minimalist):** Karpathy prensiplerine tam uyan, sıfır yeni bağımlılık, minimum kod.
- **Option B (Modüler/Genişletilebilir):** İleride ölçeklenebilirlik sağlayan ancak hafif soyutlama getiren yaklaşım.
- **Option C (Hibrit veya Alternatif Kütüphane):** Endüstri standardı bir yaklaşımla çözüm.

### Aşama 2: Anonim Akran Değerlendirmesi (Blind Peer Review)
- Seçenekler harflendirilir ve hakem modellere/alt-ajanlara şu sıkı formatla inceletilir:
  1. Her seçenek için ayrı ayrı: Güçlü yönler nedir? Zayıf yönler ve riskler nedir?
  2. Karpathy sadelik filtresi: "Bu seçenek gereksiz karmaşık (overcomplicated) mı?"
  3. `FINAL RANKING:` başlığı altında numaralı sıralama (`1. Option C`, `2. Option A`...).

### Aşama 3: Başkan Sentezi (Chairman Synthesis)
- Başkan Ajan/Model, tüm seçenekleri ve hakemlerin eleştirilerini alır.
- **Sentez Gücü:** Yalnızca tek bir seçeneği körü körüne seçmek yerine, *"Option A'nın sadeliği ile Option C'nin hata güvenliğini birleştiren"* üstün bir hibrit sentez üretebilir.
- Gerekçeli karar `knowledge-base.md` ve ilgili mimari karar kaydına (ADR) yazılır.

---

## 3. Akran Değerlendirme & Başkan Prompt Şablonları

### Aşama 2: Hakem Değerlendirme Prompt Şablonu

```markdown
Aşağıdaki mimari/teknik probleme yönelik anonim alternatifleri değerlendir:

Problem / Gereksinim: [Kullanıcının teknik gereksinimi]

Alternatif Çözümler:
- Option A: [Çözüm A detayı]
- Option B: [Çözüm B detayı]
- Option C: [Çözüm C detayı]

Görevin:
1. Her seçeneği tek tek incele. Güçlü yönlerini ve zayıf/riskli taraflarını açıkla.
2. Karpathy Sadelik İlkesi açısından değerlendir (Gereksiz soyutlama var mı? Kod tabanına aşırı yük getiriyor mu?).
3. Yanıtının EN SONUNDA kesinlikle şu formatta nihai sıralamanı belirt:

FINAL RANKING:
1. Option [Harf]
2. Option [Harf]
3. Option [Harf]
```

### Aşama 3: Başkan Sentezi Prompt Şablonu

```markdown
Sen teknik konseyin Başkanısın (Chairman). Aşağıdaki problem için farklı alternatifler sunuldu ve bağımsız hakemler tarafından sıralandı:

Problem: [Gereksinim]
Seçenekler: [Option A, B, C]
Hakem Değerlendirmeleri ve Sıralamaları: [Stage 2 çıktıları]
Konsensüs Özeti: [council_ranker.py çıktısı]

Görevin:
Tüm bu kolektif bilgeliği sentezleyerek uygulanacak en doğru, en yalın ve en sağlam nihai kararı üret. Gerekirse seçeneklerin en iyi parçalarını birleştir.
```

---

## 4. Kod Tabanında Ne Zaman Kullanılır?

1. **Büyük Kütüphane / Mimari Seçimleri:**
   - Örn. Durum yönetimi seçimi (Zustand vs Context vs Redux Toolkit).
   - Veritabanı veya ORM tercihi.
2. **Kritik / Yüksek Riskli Refactoring:**
   - Çok sayıda modülün bağımlı olduğu ortak bir servisin yeniden yazılması.
   - Blast Radius analizi sonucunda riskli bulunan değişiklikler.
3. **Çelişkili Hata Hipotezleri:**
   - Bir yarış durumu (race condition) veya bellek sızıntısında birden fazla kök neden hipotezi varken.

---

## 5. Doğrulama ve Sıralama Aracı: `council_ranker.py`

Akran sıralamalarının matematiksel ortalamasını ve Borda puanını hesaplamak için:

```bash
# Örnek konsensüs çalışmasını incele
python .agent/skills/karpathy-guidelines/scripts/council_ranker.py --sample

# Hakem çıktısı JSON dosyasını sırala ve tablo üret
python .agent/skills/karpathy-guidelines/scripts/council_ranker.py evaluations.json

# Gerçek isimleri yerine koyarak (de-anonymize) tablo al
python .agent/skills/karpathy-guidelines/scripts/council_ranker.py evaluations.json --mapping mapping.json
```
