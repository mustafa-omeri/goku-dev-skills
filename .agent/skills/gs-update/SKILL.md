---
name: gs-update
description: Sıfır şişkinlik ve proje kuralı korumalı cerrahi skill seti güncelleme orkestratörü; kullanıcıya workspace veya global kapsamını sorarak kurulu olmayan skill indirmeden dağıtımı günceller. Tetikleyiciler: "/goku-skills-update", "/gs-update", "gs update", "[GS-UPDATE]", "[GOKU-SKILLS-UPDATE]", "goku güncelle", "skillset güncelle", "goku skills update". Tetiklenmez: yeni proje kurulumu `ProjectInitializer`'a aittir. Tam sözlük: .agent/rules/skill-trigger-routing.md
---

# Goku Skillset Update Orchestrator (`/goku-skills-update`)

Bu yetenek, hedef projelerdeki `.agent/` skill ve kural setini cerrahi olarak güncelleyen, projenin özel kural bloğunu (`## Proje Bazlı Ek Kurallar`) koruyan, kurulu olmayan modülleri projeye zorla indirmeyen ve kullanıcının isteğine göre **Mevcut Çalışma Alanı (Workspace)** veya **Tüm Hedef Projeler (Global Dağıtım)** kapsamını yöneten sıfır-şişkinlik (zero-bloat) güncelleme protokolünü yürütür.

## Bağlı Kurallar ve Referanslar

- **Birincil Yetenek:** `musgoku` (`.agent/skills/musgoku/SKILL.md` ve `references/skill-set-update.md`)
- **Kurallar:** `.agent/AGENTS.md` (§4 Skill Seti Güncelleme ve §10 Proje Bazlı Ek Kurallar Koruması)
- **Dağıtım Motoru:** `npx goku-dev-skills update --global` (veya kaynak depoda `delivery.py`)

---

## 🧭 Kullanıcı Kapsam Seçimi Protokolü (Interactive Scope Selection)

Kullanıcı `/goku-skills-update` (veya `/gs-update`) komutunu tetiklediğinde, ajan varsayımda bulunmadan kullanıcıya güncelleme kapsamını sorar:

```markdown
🤖 **Goku Dev Skills Güncelleme Protokolü Devrede**

Hangi kapsamda güncelleme yapmak istersiniz?

1. **[1] Mevcut Çalışma Alanı (Workspace):**
   * Yalnızca aktif projedeki `.agent/` klasörünü cerrahi olarak en son sürüme günceller.
   * `AGENTS.md` içindeki `## Proje Bazlı Ek Kurallar` bloğunu harfiyen korur.
   * Yalnızca projede önceden kurulu skill'leri yeniler (sıfır şişkinlik / zero-bloat).
   * Komut: `npx goku-dev-skills update` (veya uzaktan çekmek için `--remote`).

2. **[2] Global Dağıtım (Tüm Hedef Projeler / Targets):**
   * Kaynak depodaki (`skillSetWorks`) güncel motoru `delivery.md` listesindeki tüm projelere (`ocai`, `FEProjectv1`, `bookmarkManagerProject`, `kalansure` vb.) dağıtır.
   * Dağıtım eşitliğini kanıtlar.
   * Komut: `npx goku-dev-skills update --global`.

3. **[3] Topyekûn Güncelleme (Workspace + Global):**
   * Hem mevcut çalışma alanı testlerini doğrular hem de tüm hedef projelere anında dağıtımı tamamlar.
```

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
Kullanıcının seçtiği kapsama göre ilgili adımı işlet:
- **Kapsam 1 (Mevcut Workspace):**
  ```bash
  npx goku-dev-skills update
  # veya uzaktan en son GitHub main sürümünü çekmek için:
  npx goku-dev-skills update --remote
  ```
- **Kapsam 2 (Global Dağıtım / Targets):**
  ```bash
  npx goku-dev-skills update --global
  ```
- **Kapsam 3 (Topyekûn):**
  Önce kaynak testlerini ve kapılarını doğrula, ardından tüm hedeflere dağıt:
  ```bash
  python .agent/skills/musgoku/scripts/run_all_gates.py
  npx goku-dev-skills update --global
  ```

⛔ **Sıfır Şişkinlik Garantisi:** Yalnızca projede halihazırda kurulu olan skill'ler, global kurallar ve şablonlar güncellenir; profil dışı skill'ler projeye kopyalanmaz.

### 3. Proje Bazlı Ek Kurallar ve Katalog Senkronizasyonu
- `.agent/AGENTS.md` içindeki `## Proje Bazlı Ek Kurallar` bölümünün kayıpsız korunduğunu doğrula.
- Hedef projelerin byte-byte eşitliğini `delivery.py` doğrulama moduyla kanıtla.

### 4. Kural ve Kapı Doğrulaması
Güncelleme sonrasında kural tablolarının ve ölçülebilir kapıların sağlamlığını doğrula:
```bash
python .agent/skills/musgoku/scripts/rules_gates.py --strict
python .agent/skills/musgoku/scripts/run_all_gates.py
```

---

## Standart Çıktı Raporu

```markdown
### 🔄 GOKU-SKILLS-UPDATE: CERRAHİ GÜNCELLEME RAPORU
- **Kapsam:** [Mevcut Workspace / Global Dağıtım / Topyekûn]
- **Güncelleme Modu:** [Yerel Paket / Uzak GitHub (`--remote`) / Dağıtım (`--global`)]
- **Güncellenen Varlıklar:** [X kurulu skill · 20 kural · şablonlar]
- **Proje Kuralları Koruması:** `## Proje Bazlı Ek Kurallar` bloğu kayıpsız korundu.
- **Doğrulama Kapısı (`rules_gates.py --strict`):** ✅ `[OK]`
- **Birleşik Kapılar (`run_all_gates.py`):** ✅ `[OK]`
```
