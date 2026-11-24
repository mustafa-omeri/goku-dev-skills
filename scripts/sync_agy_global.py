#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Syncs skillSetWorks/.agent into an Antigravity CLI global plugin (~/.gemini/config/plugins/goku-dev-skills)."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

REPO_ROOT = Path(__file__).resolve().parent.parent
SRC_AGENT = REPO_ROOT / ".agent"
DEFAULT_PLUGIN_DEST = Path.home() / ".gemini" / "config" / "plugins" / "goku-dev-skills"
DEFAULT_GLOBAL_SKILLS = Path.home() / ".gemini" / "config" / "skills"
DEFAULT_BACKUP_DIR = REPO_ROOT / "yedekler"
MAX_RULE_BYTES = 24000


def read_package_version() -> str:
    """Return the package version from package.json, falling back to 1.45.0."""
    pkg = REPO_ROOT / "package.json"
    if pkg.is_file():
        try:
            return str(json.loads(pkg.read_text(encoding="utf-8")).get("version", "1.45.0"))
        except Exception:
            pass
    return "1.45.0"


def build_plugin_manifest(version: str) -> Dict[str, object]:
    """Return the Antigravity plugin.json manifest dictionary."""
    return {
        "name": "goku-dev-skills",
        "displayName": "Goku Dev Skills",
        "version": version,
        "description": (
            "Fullstack AI engineering skills, 6-hat strategy council, TDD vertical slices, "
            "UI/UX craft floor, security & pre-launch audits (with on-demand rules and templates)."
        ),
        "author": {"name": "Mustafa Ömeri"},
        "repository": "https://github.com/mustafa-omeri/goku-dev-skills",
        "license": "MIT",
    }


def build_compact_global_agents_md(plugin_root: Path, rule_names: List[str]) -> str:
    """Build a <24 KB compact global router, scope guard, and path bridge for Antigravity CLI."""
    root_posix = plugin_root.resolve().as_posix()
    rules_list = "\n".join(f"- `{name}` -> `{root_posix}/references/rules/{name}`" for name in sorted(rule_names))
    content = f"""# Goku Dev Skills — Global Antigravity Router

> Compact global entrypoint for the `goku-dev-skills` plugin (`< 24 KB` budget safe).
> Full rule specifications live on-demand under `{root_posix}/references/rules/` so non-relevant rules never bloat context.

## 1. Scope Guard & Constitution Priority (Zero Clutter)

1. **Workspace Precedence:** If the current repository has `.agent/`, `.agents/`, or a domain-specific root constitution (`AGENTS.md` / `CLAUDE.md`, e.g. an Obsidian Second Brain Vault), **local workspace rules win**. Never overwrite or contradict a project's own root `AGENTS.md` / `CLAUDE.md`.
2. **Software-Scope Enforcement:** Heavy SDLC artifacts (`HANDOFF.md`, `KANBAN.md`, `SPRINT_PLAN.md`, `DB_MIGRATIONS.md`, `docs/kullanici-rehberi.html`) and stack gates (`check_api_docs.py`, `check_db_migrations.py`, `check_vite_spa.py`, `check_bundle_limits.py`) apply **only** to software projects or when the user explicitly triggers a planning/sprint workflow (`/plan`, `/verify-sprint`, `/feature-architect`). Do **not** inject these files into notes, vaults, or quick single-file scripts unprompted.

## 2. Path Bridge (Projects Without Local `.agent/`)

When the current working directory does **not** contain a local `./.agent/` folder:
- Resolve skill scripts referenced as `.agent/skills/<skill>/scripts/...` from:
  `{root_posix}/skills/<skill>/scripts/...`
- Resolve templates referenced as `.agent/templates/<file>` from:
  `{root_posix}/templates/<file>`
- Resolve full rules referenced as `.agent/rules/<file>` from:
  `{root_posix}/references/rules/<file>`

## 3. Core Non-Negotiable Principles

- **MCP-First:** Query `second-brain-vault` (`bootstrap`, `get_project_state`, `ask`) before scanning local history files; use `context7` for library/API docs and `sequential-thinking` for 3+ step or ambiguous architecture decisions.
- **Plan Before Code (`/plan`, `/council`):** Never write production code without a physical `.md` plan (when planning is triggered) and explicit user approval (`Proceed` vs `/seal-plan`). Use `council_ranker.py` when 2+ valid architectural options exist.
- **TDD & 5-Layer Vertical Slice:** Write failing seam tests before implementation; verify DB/API/Client/UI/Loop-Closure completeness (never claim "done" on mock-only UI).
- **UI Craft Floor:** For UI/frontend tasks, read `frontend-design` / `ui-ux-pro-max` / `ui-styling`, use Skeleton screens for data loading, and run `check_design_slop.py` when applicable.
- **Strict Git Approval:** Never run `git commit` or `git push` without explicit user approval.
- **Concise Output:** Use `/caveman` + `FAA AC 121-24C` (`[Step N]. [Action] -> [Expected Output]`, `⚠️ CRITICAL:` before destructive steps).

## 4. On-Demand Rule Lookup Table (`references/rules/`)

Read only the rule file relevant to the current action before editing:
{rules_list}
"""
    encoded = content.encode("utf-8")
    if len(encoded) >= MAX_RULE_BYTES:
        raise ValueError(f"Generated rules/AGENTS.md is {len(encoded)} bytes, exceeds {MAX_RULE_BYTES} cap.")
    return content


def copy_skills_tree(src_skills: Path, dst_skills: Path, minimal: bool) -> int:
    """Copy all skills from src_skills to dst_skills, returning the skill count."""
    count = 0
    for skill_dir in sorted(d for d in src_skills.iterdir() if d.is_dir()):
        ignore_dirs = ["__pycache__", ".pytest_cache"]
        ignore_files = ["*.pyc"]
        if minimal and skill_dir.name == "frontend-design":
            ignore_dirs.append("component-themes")
        if minimal and skill_dir.name == "ui-ux-pro-max":
            ignore_files.extend(["phosphor-icons-upstream.json", "google-font-licenses.json"])
        shutil.copytree(
            skill_dir,
            dst_skills / skill_dir.name,
            ignore=shutil.ignore_patterns(*ignore_dirs, *ignore_files),
        )
        count += 1
    return count


def dedupe_global_skills(
    global_skills_dir: Path,
    installed_skill_names: set[str],
    backup_dir: Path,
    dry_run: bool,
) -> List[str]:
    """Back up and remove skills in global_skills_dir that are shadowed by the plugin."""
    if not global_skills_dir.is_dir():
        return []
    removed: List[str] = []
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    for entry in sorted(d for d in global_skills_dir.iterdir() if d.is_dir()):
        if entry.name not in installed_skill_names:
            continue
        removed.append(entry.name)
        if not dry_run:
            backup_dir.mkdir(parents=True, exist_ok=True)
            shutil.copytree(entry, backup_dir / f"global-skills-{entry.name}-{stamp}")
            shutil.rmtree(entry)
    return removed


def sync_plugin(
    dest: Path,
    minimal: bool = False,
    dry_run: bool = False,
    dedupe: bool = False,
    global_skills_dir: Path = DEFAULT_GLOBAL_SKILLS,
    backup_dir: Path = DEFAULT_BACKUP_DIR,
) -> Dict[str, object]:
    """Sync skillSetWorks/.agent into an Antigravity CLI plugin directory."""
    src_skills = SRC_AGENT / "skills"
    src_rules = SRC_AGENT / "rules"
    src_templates = SRC_AGENT / "templates"

    skill_names = sorted(d.name for d in src_skills.iterdir() if d.is_dir())
    rule_files = sorted(f for f in src_rules.glob("*.md") if f.is_file())
    template_files = sorted(f for f in src_templates.iterdir() if f.is_file())
    version = read_package_version()
    agents_md = build_compact_global_agents_md(dest, [r.name for r in rule_files])

    if not dry_run:
        staging = dest.parent / f".{dest.name}.staging"
        if staging.exists():
            shutil.rmtree(staging)
        staging.mkdir(parents=True, exist_ok=True)
        try:
            manifest = build_plugin_manifest(version)
            (staging / "plugin.json").write_text(
                json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
            )
            (staging / "rules").mkdir(parents=True, exist_ok=True)
            (staging / "rules" / "AGENTS.md").write_text(agents_md, encoding="utf-8")

            ref_rules_dir = staging / "references" / "rules"
            ref_rules_dir.mkdir(parents=True, exist_ok=True)
            for rf in rule_files:
                shutil.copy2(rf, ref_rules_dir / rf.name)

            tmpl_dir = staging / "templates"
            tmpl_dir.mkdir(parents=True, exist_ok=True)
            for tf in template_files:
                shutil.copy2(tf, tmpl_dir / tf.name)

            copy_skills_tree(src_skills, staging / "skills", minimal=minimal)

            if dest.exists():
                shutil.rmtree(dest)
            dest.parent.mkdir(parents=True, exist_ok=True)
            staging.rename(dest)
        except Exception:
            if staging.exists():
                shutil.rmtree(staging, ignore_errors=True)
            raise

    deduped = (
        dedupe_global_skills(global_skills_dir, set(skill_names), backup_dir, dry_run=dry_run)
        if dedupe
        else []
    )

    return {
        "dest": str(dest),
        "version": version,
        "minimal": minimal,
        "dry_run": dry_run,
        "skills": len(skill_names),
        "rules_on_demand": len(rule_files),
        "templates": len(template_files),
        "agents_md_bytes": len(agents_md.encode("utf-8")),
        "deduped_global_skills": deduped,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Sync skillSetWorks/.agent as a global Antigravity CLI plugin."
    )
    parser.add_argument("--dest", type=Path, default=DEFAULT_PLUGIN_DEST, help="Target plugin directory")
    parser.add_argument("-m", "--minimal", action="store_true", help="Exclude heavy component themes")
    parser.add_argument("--check", "--dry-run", dest="dry_run", action="store_true", help="Dry-run without writing")
    parser.add_argument("--dedupe-global-skills", action="store_true", help="Back up and remove shadowed skills in ~/.gemini/config/skills")
    parser.add_argument("--global-skills-dir", type=Path, default=DEFAULT_GLOBAL_SKILLS, help="Global skills directory")
    parser.add_argument("--backup-dir", type=Path, default=DEFAULT_BACKUP_DIR, help="Backup directory for dedupe")
    parser.add_argument("--uninstall", action="store_true", help="Remove the installed global plugin directory")
    args = parser.parse_args()

    if args.uninstall:
        if args.dest.exists():
            if not args.dry_run:
                shutil.rmtree(args.dest)
            print(f"[UNINSTALLED] {args.dest} (dry_run={args.dry_run})")
        else:
            print(f"[INFO] Plugin not found at {args.dest}")
        return 0

    summary = sync_plugin(
        dest=args.dest,
        minimal=args.minimal,
        dry_run=args.dry_run,
        dedupe=args.dedupe_global_skills,
        global_skills_dir=args.global_skills_dir,
        backup_dir=args.backup_dir,
    )
    mode = "DRY-RUN" if summary["dry_run"] else "SYNCED"
    print(
        f"[{mode}] goku-dev-skills v{summary['version']} -> {summary['dest']} | "
        f"skills={summary['skills']}, templates={summary['templates']}, "
        f"on_demand_rules={summary['rules_on_demand']}, "
        f"rules/AGENTS.md={summary['agents_md_bytes']}B, minimal={summary['minimal']}"
    )
    if summary["deduped_global_skills"]:
        print(f"[DEDUPED] Removed shadowed global skills (backed up): {summary['deduped_global_skills']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
