---
name: gs-update
description: Sıfır şişkinlik ve proje kuralı korumalı cerrahi skill seti güncelleme orkestratörü; kurulu olmayan skill indirmeden dağıtımı günceller. Tetikleyiciler: "/gs-update", "gs update", "[GS-UPDATE]", "goku güncelle", "skillset güncelle". Tetiklenmez: yeni proje kurulumu `ProjectInitializer`'a aittir. Tam sözlük: .agent/rules/skill-trigger-routing.md
---

# Goku Skillset Update Orchestrator

Bu yetenek, projelerdeki `.agent/` skill ve kural setini cerrahi olarak güncelleyen, projenin özel kural bloğunu (`## Proje Bazlı Ek Kurallar`) koruyan ve kurulu olmayan modülleri projeye zorla indirmeyen güncelleme protokolünü yürütür.

## Orkestrasyon Akışı

1. **Mevcut Durum Tespiti:**
   - Projenin `AGENTS.md` dosyasındaki projeye özel kuralları oku ve yedekle.
   - Kurulu skill listesini tara.
2. **Cerrahi Güncelleme:**
   - `npx goku-dev-skills update` komutuyla yalnızca kurulu skill'leri güncelle.
3. **Kural Bloğunu Restore Etme:**
   - Projeye özel kural bloğunun yeni `AGENTS.md` dosyasının en altına eksiksiz aktarıldığını doğrula.
4. **Doğrulama:**
   - `python .agent/skills/musgoku/scripts/rules_gates.py --strict` ile kural bütünlüğünü onayla.
