---
name: council
description: Üç aşamalı LLM konseyi ve kör hakemlik orkestratörü; mimari ikilemlerde alternatif üretip Borda skoruyla sentezler ve karar kaydı üretir. Tetikleyiciler: "/council", "llm council", "[COUNCIL]", "konsey topla", "hakemlik yap". Tetiklenmez: tek alternatifli basit kodlama `musgoku`'ya aittir. Tam sözlük: .agent/rules/skill-trigger-routing.md
---

# LLM Council Ensemble Orchestrator

Bu yetenek, 2 veya daha fazla geçerli alternatif içeren karmaşık mimari ve tasarım kararlarında kör hakemlik ve Borda sayısı oylamasıyla en uygun rotayı belirleyen 3 aşamalı konsey protokolünü yürütür.

## Orkestrasyon Akışı

1. **Aşama 1 - Alternatif Üretimi:**
   - Karar bağlamını tanımla ve en az 2-3 bağımsız, gerekçelendirilmiş mimari alternatif oluştur.
2. **Aşama 2 - Kör Hakemlik ve Borda Sıralaması:**
   - Alternatifleri tarafsız kriterlerle değerlendir:
     `python .agent/skills/karpathy-guidelines/scripts/council_ranker.py`
3. **Aşama 3 - Chairman Sentezi ve ADR Kaydı:**
   - Kazanan alternatifi seç, ödünleşimleri (trade-offs) açıkla ve kararı `docs/adr/` altına Mimari Karar Kaydı (ADR) olarak kaydet.
