#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Skills Catalog Doğrulama Kapısı ve Bütünlük Testi.

Bu test iki kritik kuralı garanti altına alır:
1. `skills-catalog.html` projenin kökünde değil, `.agent/skills-catalog.html` altında yaşamalıdır.
2. Her yeni skill ve yapı eklendiğinde `.agent/skills-catalog.html` güncellenmiş olmalıdır.
   Eğer bir skill eklenir veya açıklaması değiştirilir de katalog yeniden üretilmezse,
   bu kapı kırmızıya döner (exit 1).
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJECT_ROOT = HERE.parent
AGENT_DIR = PROJECT_ROOT / ".agent"
SKILLS_DIR = AGENT_DIR / "skills"
CATALOG_PATH = AGENT_DIR / "skills-catalog.html"
ROOT_CATALOG = PROJECT_ROOT / "skills-catalog.html"
GENERATOR_SCRIPT = PROJECT_ROOT / "scripts" / "generate_skills_catalog.py"
DELIVERY_MD = PROJECT_ROOT / "delivery.md"

sys.path.insert(0, str(PROJECT_ROOT))

for stream in (sys.stdout, sys.stderr):
    if hasattr(stream, "reconfigure"):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass

failures: list[str] = []


def check(label: str, cond: bool, detail: str = "") -> None:
    status = "PASS" if cond else "FAIL"
    msg = f"  {status}  {label}"
    if detail:
        msg += f"  -- {detail}"
    print(msg)
    if not cond:
        failures.append(label)


def run_tests() -> bool:
    print("=" * 60)
    print("Skills Catalog (.agent/skills-catalog.html) Doğrulama Kapısı")
    print("=" * 60)

    # TEST 1: Dosya konumu (.agent altında olmalı, kökte olmamalı)
    print("\n=== TEST 1: Dosya Konumu ===")
    check(".agent/skills-catalog.html mevcut", CATALOG_PATH.is_file(), str(CATALOG_PATH))
    check("Kökte skills-catalog.html YOK (kirlilik önlendi)", not ROOT_CATALOG.is_file())

    # TEST 2: delivery.md rootFiles kontrolü
    print("\n=== TEST 2: Dağıtım Yapılandırması ===")
    text = DELIVERY_MD.read_text(encoding="utf-8")
    match = re.search(r"```json\s*(\{.*?\})\s*```", text, re.DOTALL)
    check("delivery.config JSON bloğu var", bool(match))
    if match:
        cfg = json.loads(match.group(1))
        check("skills-catalog.html rootFiles listesinde DEĞİL", "skills-catalog.html" not in cfg.get("rootFiles", []))

    # TEST 3: Tüm skill'ler katalogda listeleniyor mu?
    print("\n=== TEST 3: Skill Kapsamı ve Eksiksizlik ===")
    catalog_content = CATALOG_PATH.read_text(encoding="utf-8") if CATALOG_PATH.is_file() else ""
    skill_dirs = sorted([d.name for d in SKILLS_DIR.iterdir() if (d / "SKILL.md").is_file()])
    check(f"Taranan skill sayısı: {len(skill_dirs)}", len(skill_dirs) >= 20)

    missing_skills = []
    for skill_name in skill_dirs:
        # data-name="{name}" veya "name": "{name}"
        if f'data-name="{skill_name}"' not in catalog_content and f'"{skill_name}"' not in catalog_content:
            missing_skills.append(skill_name)
    check("Tüm skill'ler katalogda mevcut", len(missing_skills) == 0, f"Eksikler: {missing_skills}")

    # TEST 4: Kategorizasyon (hiçbir skill 'Diğer' kategorisinde kalmamalı)
    print("\n=== TEST 4: Kategori Bütünlüğü ===")
    from scripts.generate_skills_catalog import CATEGORIES
    all_categorized = set()
    for cat_name, s_list in CATEGORIES.items():
        all_categorized.update(s_list)
    uncategorized = set(skill_dirs) - all_categorized
    check("Tüm skill'ler geçerli bir kategoriye atanmış", len(uncategorized) == 0, f"Kategorisiz: {uncategorized}")

    # TEST 5: Güncellik ve Bayatlık Denetimi (Freshness Check)
    print("\n=== TEST 5: Güncellik ve Freshness Kapısı ===")
    res = subprocess.run([sys.executable, str(GENERATOR_SCRIPT), "--check"], capture_output=True, text=True)
    check(
        "Katalog güncel (generate_skills_catalog.py --check)",
        res.returncode == 0,
        f"Çıkış: {res.stdout.strip()} {res.stderr.strip()}" if res.returncode != 0 else "Freshness onaylandı"
    )

    # TEST 6: Slash Komutları ve Özel Metadata Bütünlüğü
    print("\n=== TEST 6: Slash Komutları ve Metadata Bütünlüğü ===")
    from scripts.generate_skills_catalog import CATEGORIES, CONFIG_METADATA, SLASH_COMMANDS
    cmd_names = [c["command"] for c in SLASH_COMMANDS]
    check("/spec-reconcile slash komutu mevcut", "/spec-reconcile" in cmd_names)
    check("/deploy-plan slash komutu mevcut", "/deploy-plan" in cmd_names)

    missing_config = [s for s in skill_dirs if s not in CONFIG_METADATA]
    check("Tüm skill'lerin CONFIG_METADATA kaydı var (sıfır kaçak)", len(missing_config) == 0, f"Eksikler: {missing_config}")

    ensemble_skills = CATEGORIES.get("Oturum Komutları (Ensemble)", [])
    bound_slash_skills = set()
    for c in SLASH_COMMANDS:
        bound_slash_skills.update(c.get("skills", []))
    missing_ensemble = [s for s in ensemble_skills if s not in bound_slash_skills]
    check("Tüm oturum komutları (Ensemble) bir slash komutuna bağlı", len(missing_ensemble) == 0, f"Bağlanmamış: {missing_ensemble}")

    print("\n" + "=" * 60)
    if failures:
        print(f"SONUÇ: {len(failures)} KONTROL BAŞARISIZ: {failures}")
        return False
    print("SONUÇ: TÜM SKILLS CATALOG KONTROLLERİ BAŞARIYLA GEÇTİ!")
    return True


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
