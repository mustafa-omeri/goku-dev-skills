---
name: prelaunch-update
description: Mevzuat idari para cezaları ve platform kuralları dinamik senkron orkestratörü; resmi kaynakları tarayarak denetim maddelerini günceller. Tetikleyiciler: "/prelaunch-update", "prelaunch update", "[PRELAUNCH-UPDATE]", "mevzuat güncelle", "ceza güncelle". Tetiklenmez: canlıya alma denetimi `prelaunch`'a aittir. Tam sözlük: .agent/rules/skill-trigger-routing.md
---

# Prelaunch Update Orchestrator

Bu yetenek, prelaunch denetiminde kullanılan KVKK/GDPR idari para cezası limitlerini, güncel yasal emsal kararları ve arama motoru / reklam platformu kurallarını dinamik olarak güncel tutan protokolü işletir.

## Orkestrasyon Akışı

1. **Kaynak Taraması:**
   - Resmi veri kaynaklarını ve güncel mevzuat tebliğlerini incele.
2. **Dinamik Senkronizasyon:**
   - `python .agent/skills/prelaunch-audit/scripts/prelaunch_updater.py` çalıştırarak ceza miktarlarını ve kural referanslarını güncelle.
3. **Dokümantasyon Güncellemesi:**
   - Değişen katsayı ve maddeleri `prelaunch-audit` referans dokümanlarına yansıt.
