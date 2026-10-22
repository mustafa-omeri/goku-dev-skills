#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tek Seferlik Dağıtım Aracı — C:\\devtools\\myProjectsAreaWS altındaki projelere
stack'lerine göre profilli (frontend / backend / fullstack) .agent kurulumu yapar.

Hariç tutulan projeler (delivery.md içinde güncel yönetilenler):
  - bookmarkManagerProject
  - kalansure
  - skillSetWorks (kaynak depo)

Kullanım:
    python scripts/distribute_one_time_myprojects.py --dry-run
    python scripts/distribute_one_time_myprojects.py
    python scripts/distribute_one_time_myprojects.py --only kidsMathTeachGame
    python scripts/distribute_one_time_myprojects.py --verify
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# Ensure UTF-8 output on Windows console
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))
import delivery

CLI_PATH = HERE / "bin" / "cli.js"
README_HELP = HERE / "readme-help.md"
BACKUP_ROOT = HERE / "yedekler"

GREEN, RED, YELLOW, CYAN, DIM, BOLD, RESET = (
    "\033[32m", "\033[31m", "\033[33m", "\033[36m", "\033[2m", "\033[1m", "\033[0m"
)


def colour(text: str, code: str) -> str:
    return f"{code}{text}{RESET}" if sys.stdout.isatty() else text


KIDS_GAME_PROJECT_BLOCK = """## Proje Bazlı Ek Kurallar

> Bu bölüm **projeye özeldir** ve `.agent/` klasörüyle birlikte projeye dağıtılır.
> Altında yalnızca bu projenin kendi gereksinimi yazılır — genel kural değil.
> Bu bölüme yazarken §10'daki mükerrerlik kontrolü zorunludur.

### Bu proje için ek kurallar

_(Aşağıdakiler yalnız KidsGameV1 projesine aittir. Kök dizindeki AGENTS.md ve AI_RULES.md ana başvuru kaynağıdır.)_

### 1. Oyun Kuralları ve Mimarisi
- `src/core/contracts.ts` dondurulmuştur (`contracts-v1` etiketi).
- Oyun mantığında `Math.random` yasaktır, `createRng(seed)` kullanılır.
- PixiJS sadece `src/render/**` içindedir; çizim `Painter` portu üzerindedir.
- Katman önekleri: `bg:` `far:` `world:` `ui:`.
- Bölüm indeksi 0 tabanlıdır: tohum `20_261_001 + indeks`.

### 2. Doğrulama Kapıları
- `pnpm typecheck`
- `pnpm lint`
- `pnpm test` (birim testleri)
- `pnpm build`
- `node scripts/check-ownership.mjs`
- `node scripts/check-gherkin.mjs`
"""

TARGETS = [
    {
        "id": "kidsMathTeachGame",
        "name": "Kids Math Teach Game",
        "path": Path(r"C:\devtools\myProjectsAreaWS\educationProjectWS\kidsMathTeachGame"),
        "profile": "frontend",
        "fallback_block": KIDS_GAME_PROJECT_BLOCK,
        "notes": "PixiJS 8 · Vite 8 · Vitest · Playwright · Frontend game",
    },
    {
        "id": "learningPdfCreator",
        "name": "Learning PDF Creator",
        "path": Path(r"C:\devtools\myProjectsAreaWS\educationProjectWS\learningPdfCreator"),
        "profile": "backend",
        "notes": "Python 3.11 · FastAPI · PostgreSQL · Playwright · Soru & PDF motoru",
    },
    {
        "id": "worldCup2026",
        "name": "World Cup 2026",
        "path": Path(r"C:\devtools\myProjectsAreaWS\kalansureWS\worldCup2026"),
        "profile": "frontend",
        "notes": "React · Vite · Tailwind · Supabase JS · Lucide React",
    },
    {
        "id": "musgokuNotesProject",
        "name": "Musgoku Notes Project",
        "path": Path(r"C:\devtools\myProjectsAreaWS\memoNoteProjectWS\musgokuNotesProject"),
        "profile": "fullstack",
        "notes": "Markdown Notes · Vault Entegrasyonu · Developer Memory",
    },
    {
        "id": "testProject",
        "name": "PRD Skill Test Project",
        "path": Path(r"C:\devtools\myProjectsAreaWS\projectVersionCompareArea\prdSKILL\testProject"),
        "profile": "backend",
        "notes": "Java 21 · Spring Boot · Maven backend test projesi",
    },
    {
        "id": "MyFileSystemMCP",
        "name": "MyFileSystem MCP",
        "path": Path(r"C:\devtools\myProjectsAreaWS\toolsWS\MyFileSystemMCP"),
        "profile": "backend",
        "notes": "TypeScript · Node.js · Model Context Protocol (MCP) filesystem server",
    },
    {
        "id": "prdSKILL",
        "name": "PRD Skill CLI",
        "path": Path(r"C:\devtools\myProjectsAreaWS\toolsWS\prdSKILL"),
        "profile": "fullstack",
        "notes": "Node.js · CLI tool · PRD & Architecture spec",
    },
    {
        "id": "ProjectInitializer",
        "name": "Project Initializer CLI",
        "path": Path(r"C:\devtools\myProjectsAreaWS\toolsWS\ProjectInitializer"),
        "profile": "fullstack",
        "notes": "TypeScript · CLI tool · Project & Vault initializer",
    },
    {
        "id": "secondBrainTemplate",
        "name": "Second Brain Template",
        "path": Path(r"C:\devtools\myProjectsAreaWS\toolsWS\secondBrainTemplate"),
        "profile": "fullstack",
        "notes": "Markdown Obsidian Vault Template · CLAUDE.md anayasası",
    },
    {
        "id": "SecondBrainVaultMCP",
        "name": "Second Brain Vault MCP",
        "path": Path(r"C:\devtools\myProjectsAreaWS\toolsWS\SecondBrainVaultMCP"),
        "profile": "backend",
        "notes": "TypeScript · Node.js · Model Context Protocol (MCP) second brain server",
    },
]


def create_target_backup(agent: Path, project_id: str, stamp: str) -> Path | None:
    if not agent.is_dir():
        return None
    target = BACKUP_ROOT / f"{project_id}-agent-{stamp}"
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(agent, target, ignore=shutil.ignore_patterns("__pycache__", ".pytest_cache"))
    return target


def run_gate_check(target_path: Path) -> tuple[bool, str]:
    gate_script = target_path / ".agent" / "skills" / "musgoku" / "scripts" / "rules_gates.py"
    if not gate_script.is_file():
        return False, "rules_gates.py bulunamadı"
    res = subprocess.run(
        [sys.executable, str(gate_script), "--strict"],
        cwd=str(target_path),
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    ok = res.returncode == 0 and "[OK]" in res.stdout
    summary = res.stdout.strip().splitlines()[-1] if res.stdout.strip() else res.stderr.strip()
    return ok, summary


def distribute_project(proj: dict, dry_run: bool) -> bool:
    name = proj["name"]
    path: Path = proj["path"]
    profile = proj["profile"]
    proj_id = proj["id"]

    print()
    print(colour(f"── {name} [{proj_id}]", BOLD))
    print(colour(f"   Dizin  : {path}", DIM))
    print(colour(f"   Profil : {profile.upper()} ({proj['notes']})", CYAN))

    if not path.is_dir():
        print(colour("   ✗ Proje dizini diskte bulunamadı — ATLANDI", RED))
        return False

    agent_dir = path / ".agent"
    root_agents = path / "AGENTS.md"
    had_root_agents = root_agents.exists()
    root_agents_backup = root_agents.read_text(encoding="utf-8", errors="ignore") if had_root_agents else None

    # 1. Proje kurallarını tespit et
    block = None
    if (agent_dir / "AGENTS.md").is_file():
        block = delivery.extract_project_block(agent_dir / "AGENTS.md")
    if not block and had_root_agents:
        block = delivery.extract_project_block(root_agents)
    if not block and "fallback_block" in proj:
        block = proj["fallback_block"]

    print(colour("   Proje kuralları: " + ("VAR — korunacak" if block else "yok (placeholder konulacak)"), DIM))

    old_files, old_bytes = delivery.dir_stats(agent_dir)
    old_skills = len([d for d in (agent_dir / "skills").iterdir() if d.is_dir()]) if (agent_dir / "skills").is_dir() else 0
    print(f"   Mevcut : {old_files} dosya / {old_bytes // 1024} KB · {old_skills} skill")

    if dry_run:
        print(colour("   [DRY-RUN] Kurulum yapılmadı — önizleme başarılı", YELLOW))
        return True

    # 2. Yedek al
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_path = create_target_backup(agent_dir, proj_id, stamp)
    if backup_path:
        print(colour(f"   Yedek  : {backup_path.relative_to(HERE)}", DIM))
        # Eski .agent klasörünü temizle — profil bazlı temiz kurulum sağla
        shutil.rmtree(agent_dir)
    else:
        print(colour("   Yedek  : yok (hedefte .agent/ mevcut değildi)", DIM))

    # 3. cli.js init çalıştır
    cmd = ["node", str(CLI_PATH), "init", "-p", profile, "--dest", str(path)]
    res = subprocess.run(cmd, cwd=str(HERE), capture_output=True, text=True, encoding="utf-8")
    if res.returncode != 0:
        print(colour(f"   ✗ Kurulum başarısız: {res.stderr.strip()}", RED))
        return False

    # 4. Proje kurallarını .agent/AGENTS.md'ye geri yaz
    dest_agents = agent_dir / "AGENTS.md"
    injected = delivery.inject_project_block(dest_agents, block)
    print(colour(f"   Kurallar: {injected} (.agent/AGENTS.md)", GREEN))

    # 5. Kök dizindeki AGENTS.md:
    # - Daha önce özel bir kök AGENTS.md varsa orijinal halini KORU
    # - Daha önce yoktu ve cli.js yeni oluşturduysa proje bloğunu ona da uygula
    if had_root_agents and root_agents_backup is not None:
        root_agents.write_text(root_agents_backup, encoding="utf-8")
        print(colour("   Kök AGENTS.md: orijinal hali korundu", GREEN))
    elif not had_root_agents and root_agents.is_file():
        delivery.inject_project_block(root_agents, block)
        print(colour("   Kök AGENTS.md: yeni oluşturuldu ve kural bloğu eşitlendi", GREEN))

    # 6. readme-help.md dağıt
    if README_HELP.is_file():
        shutil.copy2(README_HELP, path / "readme-help.md")
        print(colour("   Kök dosya: readme-help.md kopyalandı", GREEN))

    # 7. Doğrulama kapısını çalıştır
    ok, summary = run_gate_check(path)
    new_files, new_bytes = delivery.dir_stats(agent_dir)
    new_skills = len([d for d in (agent_dir / "skills").iterdir() if d.is_dir()]) if (agent_dir / "skills").is_dir() else 0
    new_rules = len([f for f in (agent_dir / "rules").iterdir() if f.is_file()]) if (agent_dir / "rules").is_dir() else 0

    print(f"   Sonuç  : {new_files} dosya / {new_bytes // 1024} KB · {new_skills} skill · {new_rules} kural")
    if ok:
        print(colour(f"   ✓ Doğrulama: {summary}", GREEN))
    else:
        print(colour(f"   ✗ Doğrulama sorunu: {summary}", RED))

    return ok


def verify_project(proj: dict) -> bool:
    name = proj["name"]
    path: Path = proj["path"]
    profile = proj["profile"]
    agent_dir = path / ".agent"

    print()
    print(colour(f"── Doğrulama: {name} [{path}]", BOLD))
    if not agent_dir.is_dir():
        print(colour("   ✗ .agent/ dizini yok", RED))
        return False

    goku_json = agent_dir / "goku.json"
    if goku_json.is_file():
        data = json.loads(goku_json.read_text(encoding="utf-8"))
        print(f"   Profil : {data.get('profile')} (beklenen: {profile})")
        print(f"   Skill  : {len(data.get('installedSkills', []))} kurulu")
        print(f"   Kural  : {len(data.get('installedRules', []))} kurulu")

    ok, summary = run_gate_check(path)
    if ok:
        print(colour(f"   ✓ Kapı: {summary}", GREEN))
    else:
        print(colour(f"   ✗ Kapı hatası: {summary}", RED))
    return ok


def main():
    parser = argparse.ArgumentParser(description="myProjectsAreaWS projelere profilli tek seferlik dağıtım")
    parser.add_argument("--dry-run", action="store_true", help="Hiçbir dosyayı değiştirmeden planı göster")
    parser.add_argument("--verify", action="store_true", help="Mevcut kurulumları doğrula")
    parser.add_argument("--only", type=str, help="Yalnızca belirtilen proje id'sini çalıştır")
    args = parser.parse_args()

    targets = TARGETS
    if args.only:
        targets = [t for t in targets if t["id"].lower() == args.only.lower()]
        if not targets:
            sys.exit(f"HATA: '{args.only}' id'li proje bulunamadı.")

    print(colour("=== Goku Dev Skills — myProjectsAreaWS Dağıtım Motoru ===", BOLD))
    print(f"Hedef Proje Sayısı: {len(targets)}")
    if args.dry_run:
        print(colour("Mod: DRY-RUN (Değişiklik yapılmaz)", YELLOW))
    elif args.verify:
        print(colour("Mod: VERIFY (Yalnız doğrulama)", CYAN))
    else:
        print(colour("Mod: CANLI DAĞITIM", GREEN))

    successes = 0
    for proj in targets:
        if args.verify:
            if verify_project(proj):
                successes += 1
        else:
            if distribute_project(proj, args.dry_run):
                successes += 1

    print()
    print(colour("═" * 60, BOLD))
    status_msg = f"Tamamlanan: {successes} / {len(targets)}"
    if successes == len(targets):
        print(colour(f"✓ {status_msg} — TÜM PROJELER BAŞARILI", GREEN))
    else:
        print(colour(f"⚠ {status_msg} — BAZI PROJELERDE HATA VEYA ATLANAN VAR", YELLOW))


if __name__ == "__main__":
    main()
