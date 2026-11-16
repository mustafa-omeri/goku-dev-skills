#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Onaylanan /plan veya mimari plan dosyalarını docs/plans/ altına tarih-saat damgasıyla arşivler.

Kural: .agent/rules/development-workflow.md Adım 2.2 (Faz 0) & sprint-delivery-workflow.md §2.1.1

Kullanım:
  python .agent/skills/musgoku/scripts/archive_plan.py --plan <plan-yolu> --slug <slug>
  python .agent/skills/musgoku/scripts/archive_plan.py --plan <plan-yolu> --slug ocai-pg --root .
  python .agent/skills/musgoku/scripts/archive_plan.py --plan .agent/plans/my_plan.md --slug auth --move
"""
import argparse
import datetime
import re
import sys
from pathlib import Path
from typing import Optional

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass


def _sanitize_token(value: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9_\-]+", "_", value.strip().lower())
    return cleaned.strip("_-")


def archive_plan(
    plan_path: Path | str,
    project_root: Path | str,
    slug: Optional[str] = None,
    prefix: str = "plan",
    move: bool = False,
) -> Path:
    """Onaylanan plan dosyasını <project_root>/docs/plans/<prefix>_<slug>_<YYYYMMDD_HHMMSS>.md olarak arşivler.

    Varsayılan olarak (move=False) kaynak dosyayı korur; böylece Antigravity IDE/CLI
    `<artifact-dir>` içindeki artifact bağlantısı bozulmaz.
    """
    src_p = Path(plan_path).resolve()
    if not src_p.is_file():
        raise FileNotFoundError(f"Plan dosyası bulunamadı: {src_p}")

    root_p = Path(project_root).resolve()
    plans_dir = root_p / "docs" / "plans"
    plans_dir.mkdir(parents=True, exist_ok=True)

    clean_prefix = _sanitize_token(prefix) or "plan"
    clean_slug = _sanitize_token(slug) if slug else ""
    slug_part = f"_{clean_slug}" if clean_slug else ""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    dest_p = plans_dir / f"{clean_prefix}{slug_part}_{timestamp}.md"
    content = src_p.read_text(encoding="utf-8", errors="replace")
    dest_p.write_text(content, encoding="utf-8")

    src_norm = str(src_p).replace("\\", "/").lower()
    if move and src_p != dest_p and "docs/plans/" not in src_norm:
        try:
            src_p.unlink()
        except OSError:
            pass

    return dest_p


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Onaylı plan dosyasını docs/plans/ altına tarih-saat damgasıyla arşivler."
    )
    parser.add_argument("--plan", required=True, help="Kaynak plan markdown dosyasının yolu")
    parser.add_argument("--slug", default=None, help="Dosya adına eklenecek kısa proje/özellik slug'ı")
    parser.add_argument("--prefix", default="plan", help="Dosya adı ön eki (varsayılan: plan)")
    parser.add_argument("--root", default=".", help="Hedef proje kök dizini (varsayılan: .)")
    parser.add_argument(
        "--move",
        action="store_true",
        help="Kopyalamadan sonra kaynak dosyayı sil (artifact-dir için önerilmez)",
    )
    args = parser.parse_args()

    root_p = Path(args.root).resolve()
    try:
        dest_p = archive_plan(
            plan_path=args.plan,
            project_root=root_p,
            slug=args.slug,
            prefix=args.prefix,
            move=args.move,
        )
    except FileNotFoundError as exc:
        print(f"[ERR] {exc}", file=sys.stderr)
        return 1

    try:
        rel = dest_p.relative_to(root_p)
    except ValueError:
        rel = dest_p
    print(f"[ARCHIVED] {str(rel).replace(chr(92), '/')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
