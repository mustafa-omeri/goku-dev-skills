#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Scout Dağıtım Hedefleri Yöneticisi — scout/targets.md dosyasını okuyarak

tekil veya genel dizin altındaki projeleri çözen ve delivery.py'ye aktaran modül.

Kullanım:
    python scout/targets.py         # Çözümlenen tüm hedef projeleri listeler
    python scout/targets.py --json  # JSON çıktısı verir
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

# Windows konsol Unicode çıkış desteği
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent
DEFAULT_TARGETS_MD = HERE / "targets.md"

PROJECT_MARKERS = {
    "package.json",
    "pom.xml",
    "build.gradle",
    "build.gradle.kts",
    "pyproject.toml",
    "requirements.txt",
    "Cargo.toml",
    "go.mod",
    "composer.json",
}

IGNORED_DIRS = {
    ".git", "node_modules", "target", "dist", "build", ".venv", "venv",
    "bin", "obj", "__pycache__", ".pytest_cache", "yedekler", "temp",
    ".idea", ".vscode", "coverage", ".next", ".nuxt"
}


def looks_like_project(path: Path) -> bool:
    """Belirtilen dizinin bir yazılım projesi olup olmadığını tespit eder."""
    if not path.is_dir():
        return False

    # Proje belirteci dosyaları
    if any((path / m).is_file() for m in PROJECT_MARKERS):
        return True

    # .agent klasörü veya AGENTS.md dosyası var mı
    if (path / ".agent").is_dir() or (path / "AGENTS.md").is_file():
        return True

    # .git dizini ve içinde kod klasörü var mı
    if (path / ".git").is_dir() and any((path / sub).exists() for sub in ("src", "lib", "app", "README.md")):
        return True

    return False


def detect_project_stack(path: Path) -> str:
    """Projenin teknoloji yığınını (frontend / backend / fullstack) belirler."""
    has_fe = any((path / f).exists() for f in ("package.json", "vite.config.ts", "vite.config.js", "next.config.js", "src/App.tsx", "src/App.jsx"))
    has_be = any((path / f).exists() for f in ("pom.xml", "build.gradle", "pyproject.toml", "requirements.txt", "Cargo.toml", "go.mod"))
    if has_fe and has_be:
        return "backend+frontend"
    if has_fe:
        return "frontend"
    if has_be:
        return "backend"
    return "fullstack"


def parse_targets_file(targets_path: Optional[Path] = None) -> List[Dict[str, Any]]:
    """scout/targets.md dosyasını okuyarak ham hedef tanımlarını döndürür."""
    t_file = targets_path or DEFAULT_TARGETS_MD
    if not t_file.is_file():
        return []

    raw_text = t_file.read_text(encoding="utf-8", errors="replace")
    # HTML yorum bloklarını (<!-- ... -->) temizle
    clean_text = re.sub(r"<!--.*?-->", "", raw_text, flags=re.DOTALL)
    lines = clean_text.splitlines()
    entries: List[Dict[str, Any]] = []

    for line_num, line in enumerate(lines, start=1):
        clean = line.strip()
        if not clean or clean.startswith("#") or clean.startswith(">"):
            continue

        # Tablo başlığı veya ayırıcı satırlarını atla
        if clean.startswith("|---") or re.match(r"^\|\s*Durum\s*\|", clean, re.IGNORECASE):
            continue

        enabled = None
        raw_path = ""
        notes = ""

        # Format 1: Markdown Tablo (| ON | C:/path | Not |)
        if clean.startswith("|"):
            parts = [p.strip() for p in clean.split("|")[1:-1]]
            if len(parts) >= 2:
                status_part = parts[0].upper()
                raw_path = parts[1]
                notes = parts[2] if len(parts) > 2 else ""

                if status_part in ("ON", "TRUE", "1", "YES", "EVET", "[X]"):
                    enabled = True
                elif status_part in ("OFF", "FALSE", "0", "NO", "HAYIR", "[ ]"):
                    enabled = False

        # Format 2: Liste veya Çizgi (- [x] C:/path veya - [ ] C:/path)
        elif clean.startswith("- ["):
            m = re.match(r"^-\s*\[([ xX])\]\s+(.+)$", clean)
            if m:
                enabled = (m.group(1).lower() == "x")
                raw_path = m.group(2).strip()

        # Format 3: Düz satır (ON | C:/path veya OFF | C:/path)
        elif "|" in clean:
            parts = [p.strip() for p in clean.split("|")]
            if len(parts) >= 2:
                status_part = parts[0].upper()
                if status_part in ("ON", "TRUE", "1", "YES", "EVET"):
                    enabled = True
                    raw_path = parts[1]
                    notes = parts[2] if len(parts) > 2 else ""
                elif status_part in ("OFF", "FALSE", "0", "NO", "HAYIR"):
                    enabled = False
                    raw_path = parts[1]
                    notes = parts[2] if len(parts) > 2 else ""

        if enabled is not None and raw_path:
            # Temizlik
            clean_path_str = raw_path.strip().strip("`").strip("\"'").rstrip("/\\")
            target_path = Path(clean_path_str)

            entries.append({
                "line": line_num,
                "raw_path": clean_path_str,
                "path": target_path,
                "enabled": enabled,
                "notes": notes
            })

    return entries


def discover_projects_in_directory(root: Path, max_depth: int = 3) -> List[Path]:
    """Genel bir dizin altındaki tüm projeleri özyinelemeli olarak keşfeder."""
    if not root.is_dir():
        return []

    found: List[Path] = []
    source_root = REPO_ROOT.resolve()

    def walk(current: Path, depth: int):
        if depth > max_depth or current.name in IGNORED_DIRS or current.name.startswith("."):
            return

        # Kaynak deponun kendisini atla
        try:
            if current.resolve() == source_root:
                return
        except Exception:
            pass

        if looks_like_project(current):
            found.append(current)
            return  # Proje bulundu, alt dizinlerine inme

        try:
            for child in current.iterdir():
                if child.is_dir() and child.name not in IGNORED_DIRS and not child.name.startswith("."):
                    walk(child, depth + 1)
        except (PermissionError, OSError):
            pass

    walk(root, 0)
    return found


def resolve_distribution_targets(targets_path: Optional[Path] = None) -> List[Dict[str, Any]]:
    """
    scout/targets.md dosyasındaki ON ve OFF girdilerini analiz ederek
    tüm hedef projeleri (tekil veya genel dizin altındaki) tekil liste olarak çözer.
    """
    entries = parse_targets_file(targets_path)
    if not entries:
        return []

    # Öncelik yönetimi:
    # 1. Tekil proje girdileri (doğrudan tekil olarak yazılanlar)
    # 2. Genel dizin girdileri (taranarak bulunan projeler)
    resolved_map: Dict[str, Dict[str, Any]] = {}
    source_root = REPO_ROOT.resolve()

    for entry in entries:
        p: Path = entry["path"]
        enabled: bool = entry["enabled"]

        if not p.exists():
            # Yol diskte yoksa bile devre dışı olarak listeye al
            p_id = p.name or "unknown"
            resolved_map[str(p.resolve() if p.is_absolute() else p)] = {
                "id": p_id,
                "name": p_id,
                "path": str(p),
                "enabled": False,
                "stack": "unknown",
                "profile": "fullstack",
                "notes": f"Dizin diskte bulunamadı ({entry['notes']})".strip(),
                "source_type": "missing"
            }
            continue

        resolved_p = p.resolve()
        if resolved_p == source_root:
            continue

        # Tekil Proje mi yoksa Genel Dizin mi?
        is_single = looks_like_project(resolved_p)

        if is_single:
            p_id = resolved_p.name
            resolved_map[str(resolved_p)] = {
                "id": p_id,
                "name": p_id,
                "path": str(resolved_p),
                "enabled": enabled,
                "stack": detect_project_stack(resolved_p),
                "profile": "fullstack",
                "notes": entry["notes"] or f"Tekil proje ({'Aktif' if enabled else 'Pasif'})",
                "source_type": "single"
            }
        else:
            # Genel Dizin: Altındaki projeleri keşfet
            discovered = discover_projects_in_directory(resolved_p, max_depth=3)
            for disc in discovered:
                disc_key = str(disc.resolve())
                # Eğer proje daha önce tekil olarak tanımlanmışsa, tekil tanımın enabled durumu korunur
                if disc_key in resolved_map and resolved_map[disc_key]["source_type"] == "single":
                    continue

                disc_id = disc.name
                resolved_map[disc_key] = {
                    "id": disc_id,
                    "name": disc_id,
                    "path": str(disc.resolve()),
                    "enabled": enabled,  # Genel dizinin ON/OFF durumuna göre
                    "stack": detect_project_stack(disc),
                    "profile": "fullstack",
                    "notes": f"{resolved_p.name} altından otomatik keşfedildi ({'Aktif' if enabled else 'Pasif'})",
                    "source_type": "general"
                }

    return list(resolved_map.values())


def build_delivery_config_from_targets(
    targets_path: Optional[Path] = None,
    base_config: Optional[dict] = None
) -> dict:
    """delivery.py'nin kullandığı tam konfigürasyon yapısını üretir."""
    projects = resolve_distribution_targets(targets_path)
    base = base_config or {}

    return {
        "source": base.get("source", ".agent"),
        "backupRoot": base.get("backupRoot", "yedekler"),
        "rootFiles": base.get("rootFiles", ["readme-help.md"]),
        "projects": projects
    }


def main():
    parser = argparse.ArgumentParser(description="Scout Dağıtım Hedefleri Çözümleyici")
    parser.add_argument("--targets", help="Özel targets.md yolu", default=None)
    parser.add_argument("--json", action="store_true", help="JSON çıktısı ver")
    args = parser.parse_args()

    targets_file = Path(args.targets) if args.targets else DEFAULT_TARGETS_MD
    projects = resolve_distribution_targets(targets_file)

    if args.json:
        print(json.dumps(projects, ensure_ascii=False, indent=2))
        return

    print(f"Scout Dağıtım Hedefleri: {targets_file}")
    print("=" * 70)
    print(f"{'DURUM':<8} {'TÜR':<10} {'ID':<24} {'STACK':<18} PATH")
    print("-" * 70)

    for p in projects:
        status_str = "[ON]" if p["enabled"] else "[OFF]"
        print(f"{status_str:<8} {p.get('source_type',''):<10} {p['id']:<24} {p.get('stack',''):<18} {p['path']}")

    on_count = sum(1 for p in projects if p["enabled"])
    off_count = sum(1 for p in projects if not p["enabled"])
    print("-" * 70)
    print(f"Toplam: {len(projects)} proje | {on_count} Aktif (ON) | {off_count} Pasif (OFF)")


if __name__ == "__main__":
    main()
