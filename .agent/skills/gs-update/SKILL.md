---
name: gs-update
description: Sıfır şişkinlik ve proje kuralı korumalı cerrahi skill seti güncelleme orkestratörü; kurulu olmayan skill indirmeden dağıtımı günceller. Tetikleyiciler: "/gs-update", "gs update", "[GS-UPDATE]", "goku güncelle", "skillset güncelle". Tetiklenmez: yeni proje kurulumu `ProjectInitializer`'a aittir. Tam sözlük: .agent/rules/skill-trigger-routing.md
---

# Goku Skillset Update Orchestrator

Bu yetenek, hedef projelerdeki `.agent/` skill ve kural setini cerrahi olarak güncelleyen, projenin özel kural bloğunu (`## Proje Bazlı Ek Kurallar`) koruyan ve kurulu olmayan modülleri projeye zorla indirmeyen sıfır-şişkinlik (zero-bloat) güncelleme protokolünü yürütür.

## Bağlı Kurallar ve Referanslar

- **Birincil Yetenek:** `musgoku` (`.agent/skills/musgoku/SKILL.md` ve `references/skill-set-update.md`)
- **Kurallar:** `.agent/AGENTS.md` (§4 Skill Seti Güncelleme ve §10 Proje Bazlı Ek Kurallar Koruması)

---

## 4 Aşamalı Cerrahi Güncelleme Akışı

### 1. Mevcut Kurulum ve Proje Bloğu Tespiti
- Hedef projenin `.agent/goku.json` manifestosunu ve kurulu skill listesini (`installedSkills`) kontrol et.
- `.agent/AGENTS.md` dosyasının en altındaki `## Proje Bazlı Ek Kurallar` bölümünü oku ve korunacağını teyit et.
- Değişiklikleri diske yazmadan önce önizlemek gerekirse:
  ```bash
  npx goku-dev-skills update --check
  ```

### 2. Sıfır-Şişkinlik Cerrahi Güncelleme İcrası
- Yerel kaynak paket mevcutsa hızlı çevrimdışı güncelleme, yoksa GitHub üzerinden seçici güncelleme çalıştır:
  ```bash
  npx goku-dev-skills update
  ```
  *(veya uzaktan en son sürümü çekmek için `npx goku-dev-skills update --remote`)*
- ⛔ **Sıfır Şişkinlik Garantisi:** Yalnızca projede halihazırda kurulu olan skill'ler, global kurallar ve şablonlar güncellenir; profil dışı skill'ler projeye kopyalanmaz.

### 3. Proje Bazlı Ek Kurallar ve Katalog Senkronizasyonu
- `.agent/AGENTS.md` içindeki `## Proje Bazlı Ek Kurallar` bölümünün kayıpsız korunduğunu doğrula.
- Kaynak depo (`skillSetWorks`) içindeysen `delivery.py --keep 1` ve `delivery.py --verify` ile aktif hedeflerin byte-byte eşitliğini kanıtla.

### 4. Kural ve Kapı Doğrulaması
Güncelleme sonrasında kural tablolarının ve ölçülebilir kapıların sağlamlığını doğrula:
```bash
python .agent/skills/musgoku/scripts/rules_gates.py --strict
python .agent/skills/musgoku/scripts/run_all_gates.py
```

---

## Standart Çıktı Raporu

```markdown
### 🔄 GS-UPDATE: CERRAHİ SKILLSET GÜNCELLEME RAPORU
- **Güncelleme Modu:** [Yerel Paket / Uzak GitHub (`--remote`) / Dağıtım (`delivery.py`)]
- **Güncellenen Kapsam:** [X kurulu skill · 20 kural · şablonlar]
- **Proje Kuralları Koruması:** `## Proje Bazlı Ek Kurallar` bloğu kayıpsız korundu.
- **Doğrulama Kapısı (`rules_gates.py --strict`):** ✅ `[OK]`
```
