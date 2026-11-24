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
from typing import List, Optional

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

THIS_DIR = Path(__file__).resolve().parent
if str(THIS_DIR) not in sys.path:
    sys.path.insert(0, str(THIS_DIR))

import check_handoff  # noqa: E402
import plan_conflict_guard  # noqa: E402


class PlanConflictError(RuntimeError):
    """Ön-mühürleme sırasında CRITICAL çakışma/ezme veya regresyon tespit edildiğinde fırlatılır."""

    def __init__(self, message: str, report: dict):
        super().__init__(message)
        self.report = report


def _sanitize_token(value: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9_\-]+", "_", value.strip().lower())
    return cleaned.strip("_-")


def _extract_task_ids(plan_text: str) -> List[str]:
    seen = set()
    ordered: List[str] = []
    for tid in check_handoff.PLAN_TASK_ID_RE.findall(plan_text):
        if tid not in seen:
            seen.add(tid)
            ordered.append(tid)
    return ordered


def seal_plan_to_handoff(
    archived_plan_path: Path | str,
    project_root: Path | str,
    sprint_label: str = "Planlı Backlog",
) -> Path:
    """Arşivlenen plandaki görevleri HANDOFF.md §3 Gelecek Fazlar panosuna ⬜ Bekliyor olarak idempotent mühürler."""
    root_p = Path(project_root).resolve()
    plan_p = Path(archived_plan_path).resolve()
    handoff_p = root_p / "HANDOFF.md"

    if not plan_p.is_file():
        raise FileNotFoundError(f"Plan dosyası bulunamadı: {plan_p}")
    if not handoff_p.is_file():
        raise FileNotFoundError(f"HANDOFF.md bulunamadı: {handoff_p}")

    try:
        plan_rel = str(plan_p.relative_to(root_p)).replace("\\", "/")
    except ValueError:
        plan_rel = str(plan_p).replace("\\", "/")

    plan_text = plan_p.read_text(encoding="utf-8", errors="replace")
    handoff_text = handoff_p.read_text(encoding="utf-8", errors="replace")
    safe_sprint = sprint_label.replace("|", "/").strip() or "Planlı Backlog"

    task_ids = _extract_task_ids(plan_text)
    rows_to_add: List[str] = []
    if task_ids:
        for tid in task_ids:
            if not re.search(rf"^\|\s*{re.escape(tid)}\s*\|", handoff_text, re.MULTILINE):
                rows_to_add.append(
                    f"| {tid} | Plan mühürlendi — tetikleme bekliyor ({plan_rel}) | {safe_sprint} | Planlı | `{plan_rel}` | ⬜ Bekliyor |"
                )
    elif plan_p.name not in handoff_text:
        rows_to_add.append(
            f"| PLAN-REF | Plan mühürlendi — tetikleme bekliyor ({plan_rel}) | {safe_sprint} | Planlı | `{plan_rel}` | ⬜ Bekliyor |"
        )

    if not rows_to_add:
        return handoff_p

    lines = handoff_text.splitlines()
    future_idx = None
    for idx, ln in enumerate(lines):
        if re.match(r"^#{3,4}\s+(?:📌\s*)?Gelecek\s+Fazlar", ln.strip(), re.IGNORECASE):
            future_idx = idx
            break

    if future_idx is not None:
        last_row_idx = None
        for idx in range(future_idx + 1, len(lines)):
            stripped = lines[idx].strip()
            if re.match(r"^#{2,4}\s+", stripped):
                break
            if stripped.startswith("|"):
                last_row_idx = idx
        insert_pos = (last_row_idx + 1) if last_row_idx is not None else (future_idx + 1)
        if last_row_idx is None:
            rows_to_add = [
                "| Gereksinim ID | Açıklama | Hedef Faz | Hedef Sürüm | PRD / Kaynak Ref | Durum |",
                "|---|---|---|---|---|---|",
            ] + rows_to_add
        for offset, row in enumerate(rows_to_add):
            lines.insert(insert_pos + offset, row)
        handoff_p.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return handoff_p

    # Gelecek Fazlar başlığı yoksa §3 sonuna (veya ## 4. / ### Sağlık durumu öncesine) ekle
    section_block = [
        "",
        "#### 📌 Gelecek Fazlar & Parking Lot Yol Haritası (Product Roadmap Backlog)",
        "| Gereksinim ID | Açıklama | Hedef Faz | Hedef Sürüm | PRD / Kaynak Ref | Durum |",
        "|---|---|---|---|---|---|",
    ] + rows_to_add

    anchor_idx = None
    for idx, ln in enumerate(lines):
        if re.match(r"^(?:###\s+Sağlık\s+durumu|##\s+4\.)", ln.strip(), re.IGNORECASE):
            anchor_idx = idx
            break

    if anchor_idx is not None:
        for offset, block_ln in enumerate(section_block + [""]):
            lines.insert(anchor_idx + offset, block_ln)
        handoff_p.write_text("\n".join(lines) + "\n", encoding="utf-8")
    else:
        handoff_p.write_text(handoff_text.rstrip() + "\n" + "\n".join(section_block) + "\n", encoding="utf-8")
    return handoff_p


def _inject_conflict_audit(content: str, report: dict) -> str:
    """Çakışma/tekrar/sıralama bulguları varsa arşivlenen plan içine audit bloğunu gömer."""
    if not report.get("findings"):
        return content
    section = plan_conflict_guard.format_markdown_audit_section(report)
    cleaned = re.sub(
        r"<!--\s*PRE-SEAL-CONFLICT-AUDIT:BEGIN\s*-->.*?<!--\s*PRE-SEAL-CONFLICT-AUDIT:END\s*-->\s*",
        "",
        content,
        flags=re.DOTALL | re.IGNORECASE,
    )
    anchor = re.search(r"^##\s+11\.\s+🚨", cleaned, re.MULTILINE)
    if anchor:
        idx = anchor.start()
        return cleaned[:idx].rstrip() + "\n\n" + section + "\n\n" + cleaned[idx:]
    return cleaned.rstrip() + "\n\n---\n\n" + section + "\n"


def archive_plan(
    plan_path: Path | str,
    project_root: Path | str,
    slug: Optional[str] = None,
    prefix: str = "plan",
    move: bool = False,
    seal_handoff: bool = False,
    sprint_label: str = "Planlı Backlog",
    allow_conflicts: bool = False,
    skip_conflict_check: bool = False,
) -> Path:
    """Onaylanan plan dosyasını <project_root>/docs/plans/<prefix>_<slug>_<YYYYMMDD_HHMMSS>.md olarak arşivler.

    Varsayılan olarak (move=False) kaynak dosyayı korur; böylece Antigravity IDE/CLI
    `<artifact-dir>` içindeki artifact bağlantısı bozulmaz.
    seal_handoff=True verildiğinde görevleri HANDOFF.md Gelecek Fazlar panosuna ⬜ Bekliyor olarak mühürler.
    Mühürleme öncesi plan_conflict_guard ile canlı kod ve bekleyen plan çakışmaları denetlenir;
    CRITICAL ezme varsa allow_conflicts=True verilmedikçe PlanConflictError fırlatılır.
    """
    src_p = Path(plan_path).resolve()
    if not src_p.is_file():
        raise FileNotFoundError(f"Plan dosyası bulunamadı: {src_p}")

    root_p = Path(project_root).resolve()
    conflict_report = None
    if not skip_conflict_check:
        conflict_report = plan_conflict_guard.analyze_plan_conflicts(root_p, src_p)
        if conflict_report["critical_count"] > 0 and not allow_conflicts:
            raise PlanConflictError(
                f"Ön-mühürleme sırasında {conflict_report['critical_count']} CRITICAL çakışma/ezme "
                f"tespit edildi ({conflict_report['overall_classification']}). "
                f"Bilinçli olarak devam etmek için --allow-conflicts kullanın.",
                conflict_report,
            )

    plans_dir = root_p / "docs" / "plans"
    plans_dir.mkdir(parents=True, exist_ok=True)

    clean_prefix = _sanitize_token(prefix) or "plan"
    clean_slug = _sanitize_token(slug) if slug else ""
    slug_part = f"_{clean_slug}" if clean_slug else ""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    dest_p = plans_dir / f"{clean_prefix}{slug_part}_{timestamp}.md"
    content = src_p.read_text(encoding="utf-8", errors="replace")
    if conflict_report is not None:
        content = _inject_conflict_audit(content, conflict_report)
    dest_p.write_text(content, encoding="utf-8")

    src_norm = str(src_p).replace("\\", "/").lower()
    if move and src_p != dest_p and "docs/plans/" not in src_norm:
        try:
            src_p.unlink()
        except OSError:
            pass

    if seal_handoff:
        seal_plan_to_handoff(dest_p, root_p, sprint_label=sprint_label)

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
    parser.add_argument(
        "--seal-handoff",
        action="store_true",
        help="Planı arşivledikten sonra HANDOFF.md Gelecek Fazlar panosuna ⬜ Bekliyor olarak mühürle",
    )
    parser.add_argument(
        "--sprint-label",
        default="Planlı Backlog",
        help="--seal-handoff ile yazılacak hedef faz/sprint etiketi (örn. 'Sprint 21')",
    )
    parser.add_argument(
        "--allow-conflicts",
        action="store_true",
        help="CRITICAL çakışma/ezme bulgularına rağmen mühürlemeye izin ver ve raporu plana işle",
    )
    parser.add_argument(
        "--skip-conflict-check",
        action="store_true",
        help="Ön-mühürleme çakışma ve sıralı plan ezme taramasını atla",
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
            seal_handoff=args.seal_handoff,
            sprint_label=args.sprint_label,
            allow_conflicts=args.allow_conflicts,
            skip_conflict_check=args.skip_conflict_check,
        )
    except PlanConflictError as exc:
        print(f"[BLOCKED] {exc}", file=sys.stderr)
        for f in exc.report.get("findings", []):
            print(f"  [{f['severity']}] [{f['type']}] {f['target']} -> {f['message']}", file=sys.stderr)
        return 1
    except FileNotFoundError as exc:
        print(f"[ERR] {exc}", file=sys.stderr)
        return 1

    try:
        rel = dest_p.relative_to(root_p)
    except ValueError:
        rel = dest_p
    print(f"[ARCHIVED] {str(rel).replace(chr(92), '/')}")
    if args.seal_handoff:
        print(f"[SEALED] HANDOFF.md -> '{args.sprint_label}' (⬜ Bekliyor)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
