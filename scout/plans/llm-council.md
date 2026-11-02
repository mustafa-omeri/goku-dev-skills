# 🔭 Scout Değerlendirme Raporu: karpathy/llm-council

## 1. Depo Özeti ve Künye
- **URL:** https://github.com/karpathy/llm-council
- **Sahibi:** Andrej Karpathy
- **Analiz Tarihi:** 2026-10-22
- **Entegrasyon Tarihi:** 2026-10-22
- **Tespit Edilen Katman:** Backend + Tooling / Agentic (Hafif React UI)
- **Dosya Sayısı:** 39 dosya (~510 KB)
- **Teknoloji Yığını:** Python (FastAPI, async httpx, OpenRouter API), React + Vite, uv

---

## 2. Çekirdek Felsefe ve Mimari (Repo İncelemesi)

Kullanıcının tek bir LLM'e soru sorması yerine, farklı sağlayıcılardan oluşan bir "LLM Konseyi" (LLM Council - örn. GPT, Claude, Gemini, Grok) kurularak 3 aşamalı bir kolektif akıl yürütme (ensemble deliberation) yürütülür:

1. **Aşama 1: Bağımsız İlk Yanıtlar (First Opinions):**
   - Kullanıcı sorgusu paralel olarak konseydeki tüm modellere iletilir (`asyncio.gather`).
   - Her model diğerlerinin cevabını görmeden bağımsız bir çözüm/yanıt üretir.

2. **Aşama 2: Anonimleştirilmiş Akran İncelemesi (Blind Peer Review & Cross-Ranking):**
   - Tüm modellerin yanıtları harf etiketleriyle anonimleştirilir (`Response A`, `Response B`, `Response C`...).
   - Hiçbir modele hangi cevabın kime ait olduğu söylenmez; böylece marka kayırmacılığı (self-preference / provider bias) engellenir.
   - Her model diğerlerinin yanıtlarını doğruluk, derinlik ve mantık hataları açısından eleştirir ve kesin bir formatta sıralar (`FINAL RANKING: 1. Response C, 2. Response A...`).
   - Sistem matematiksel ortalama sıralamayı (`calculate_aggregate_rankings`) hesaplar.

3. **Aşama 3: Başkan Sentezi (Chairman Synthesis):**
   - Belirlenen Başkan Model (Chairman LLM), Aşama 1'deki tüm ham yanıtları ve Aşama 2'deki akran eleştirileri ile sıralamalarını inceler.
   - Çelişkileri ve halüsinasyonları ayıklar; konseyin ortak aklını temsil eden tek, sağlam ve dengeli nihai sentezi üretir.

---

## 3. Bizim Sistemle Kıyaslama (Delta Analizi)

- **Mevcut Durumumuz:**
  - `karpathy-guidelines`: Karpathy'nin cerrahi değişiklik, basitlik, varsayımları yüzeye çıkarma prensipleri sistemimizde tanımlıdır.
  - `code-review`: Standartlar ve Şartname eksenlerinde alt ajan denetimi yapmaktadır.
  - `doc-coauthoring`: Mimari kararlar ve RFC dokümanları hazırlamaktadır.
- **Dış Repodaki Değer:**
  - Karpathy'nin geliştirdiği **3 Aşamalı Anonim Akran İncelemesi (Blind Cross-Evaluation)** protokolü, karmaşık mimari ikilemlerde, riskli refactoring kararlarında ve hata ayıklama hipotezlerinde tarafsız ve üst düzey bir konsensüs mekanizması sunmaktadır.
  - Modellerin kendi yanıtlarını kayırmasını engelleyen körleme (blinding) tekniği son derece zarif ve etkilidir.
- **Entegrasyon Durumu:**
  - Dış OpenRouter API bağımlılığı elenerek, Antigravity IDE alt-ajanları ve çoklu hipotez taramalarında çalışan sıfır-bağımlılık Python aracı (`scripts/council_ranker.py`) ve derinlemesine rehber (`references/llm-council-deliberation.md`) olarak `.agent/skills/karpathy-guidelines/` yeteneğimiz zenginleştirilmiştir.

---

## 4. Karar: ✅ TAMAMLANDI (INTEGRATED)
Bu deponun sunduğu 3 aşamalı anonim konsensüs ve akran değerlendirmesi protokolü, `.agent/skills/karpathy-guidelines/` altına başarıyla entegre edilmiştir.

---

## 5. Gerçekleştirilen Entegrasyon Adımları

1. **Rehber ve Standart:**
   - `.agent/skills/karpathy-guidelines/references/llm-council-deliberation.md` dosyası oluşturuldu.
   - 3 Aşamalı Konsey Protokolü (First Opinions → Blind Peer Review → Chairman Synthesis) ve Stage 2 / Stage 3 prompt kalıpları belgelendi.
2. **Doğrulama ve Sıralama Aracı:**
   - `.agent/skills/karpathy-guidelines/scripts/council_ranker.py` aracı yazıldı. Hakem çıktılarından `FINAL RANKING:` ayrıştırması, Borda puanı ve ortalama sıralama hesaplamaları sağlandı.
3. **Birim Testleri:**
   - `.agent/skills/karpathy-guidelines/scripts/tests/test_council_ranker.py` oluşturuldu (7 test PASS).
4. **Sözleşme & Kural Senkronizasyonu:**
   - `karpathy-guidelines/SKILL.md` güncellendi (51 kelime sözleşmesi tam uyumlu).
   - `.agent/rules/skill-trigger-routing.md` tablosuna `llm council`, `akran incelemesi` tetikleyicileri ve "Mimari tercih ve alternatif seçimi" senaryosu işlendi.
5. **Doğrulama Kapıları & Dağıtım:**
   - `test_skill_contracts.py` (11/11 PASS)
   - `test_council_ranker.py` (7/7 PASS)
   - `tests/run_all.py` (11/11 PASS)
   - 100 pytest testi PASS
   - `delivery.py --verify` ile 4 hedef projede 804 dosya byte-byte eşitlendi.
