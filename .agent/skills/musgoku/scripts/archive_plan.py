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


UI_TARGET_RE = re.compile(
    r"(?:src/(?:pages|components|views|screens|layouts|app|ui)/[^\s`'\"]+|\.(?:tsx|jsx|vue|svelte|astro|css|scss)\b)",
    re.IGNORECASE,
)
UI_EXPLICIT_BYPASS_RE = re.compile(
    r"(?:Salt\s+Backend|UI\s+Kapsam\s+Dışı|UI\s+Etkisi\s*:\s*Yok|Tier\s+0\s*[:\-—]\s*Bypass)",
    re.IGNORECASE,
)
UI_WIREFRAME_PRESENT_RE = re.compile(
    r"(?:\[\s*BEFORE\b.*?\[\s*AFTER\b|Before\s*->\s*After|Tel\s*Kafes|UI-PREVIEW-LOCK|ui_preview_|<div|\+---+|┌───)",
    re.IGNORECASE | re.DOTALL,
)
UI_PREVIEW_LOCK_RE = re.compile(r"\bUI-PREVIEW-LOCK\b", re.IGNORECASE)
UI_PREVIEW_FLAG_RE = re.compile(r"(?:--ui-preview\b|--ui-ux\b|--UI&UX\b)", re.IGNORECASE)


def check_ui_predesign_plan(plan_text: str) -> dict:
    """Planın UI etkileyip etkilemediğini ve Before->After Wireframe / UI-PREVIEW-LOCK durumunu denetler."""
    text = plan_text or ""
    explicit_bypass = bool(UI_EXPLICIT_BYPASS_RE.search(text))
    ui_targets = UI_TARGET_RE.findall(text)
    ui_flag = bool(UI_PREVIEW_FLAG_RE.search(text))
    ui_detected = (bool(ui_targets) or ui_flag) and not explicit_bypass

    has_preview_lock = bool(UI_PREVIEW_LOCK_RE.search(text))
    has_wireframe = bool(UI_WIREFRAME_PRESENT_RE.search(text))

    warnings: List[dict] = []
    if ui_detected and not has_wireframe:
        warnings.append(
            {
                "code": "UI-WIREFRAME-MISSING",
                "message": (
                    "Plan UI dosyası etkiliyor ancak §7.1 Before -> After Wireframe (veya --ui-preview "
                    "UI-PREVIEW-LOCK) bölümü bulunamadı. Uyarıyı susturmak için --allow-no-wireframe kullanın."
                ),
            }
        )
    elif ui_detected and ui_flag and has_preview_lock:
        # Kilit bloğunda doldurulmamış <doldur placeholder kontrolü
        lock_pos = text.upper().find("UI-PREVIEW-LOCK")
        lock_snippet = text[lock_pos : lock_pos + 600]
        if "<doldur" in lock_snippet:
            warnings.append(
                {
                    "code": "UI-PREVIEW-LOCK-INCOMPLETE",
                    "message": "--ui-preview kilidi açık ancak UI-PREVIEW-LOCK alanlarında '<doldur' yer tutucusu kaldı.",
                }
            )

    return {
        "ui_detected": ui_detected,
        "has_wireframe": has_wireframe,
        "has_preview_lock": has_preview_lock,
        "warnings": warnings,
    }


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
    allow_no_wireframe: bool = False,
) -> Path:
    """Onaylanan plan dosyasını <project_root>/docs/plans/<prefix>_<slug>_<YYYYMMDD_HHMMSS>.md olarak arşivler.

    Varsayılan olarak (move=False) kaynak dosyayı korur; böylece Antigravity IDE/CLI
    `<artifact-dir>` içindeki artifact bağlantısı bozulmaz.
    seal_handoff=True verildiğinde görevleri HANDOFF.md Gelecek Fazlar panosuna ⬜ Bekliyor olarak mühürler.
    Mühürleme öncesi plan_conflict_guard ile canlı kod ve bekleyen plan çakışmaları denetlenir;
    CRITICAL ezme varsa allow_conflicts=True verilmedikçe PlanConflictError fırlatılır.
    UI etkileyen planlarda Before->After Wireframe yoksa uyarı basar (allow_no_wireframe=True ile susturulur).
    """
    src_p = Path(plan_path).resolve()
    if not src_p.is_file():
        raise FileNotFoundError(f"Plan dosyası bulunamadı: {src_p}")

    raw_content = src_p.read_text(encoding="utf-8", errors="replace")
    if not allow_no_wireframe:
        ui_check = check_ui_predesign_plan(raw_content)
        for warn in ui_check["warnings"]:
            print(f"[WARN] [{warn['code']}] {warn['message']}", file=sys.stderr)

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
    content = raw_content
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


def archive_walkthrough(
    walkthrough_path: Path | str,
    project_root: Path | str,
    for_plan: Optional[Path | str] = None,
    slug: Optional[str] = None,
    subdir: bool = False,
    move: bool = False,
) -> Path:
    """Uygulanan plan, sprint veya geliştirme için walkthrough.md çıktısını repo içine arşivler.

    - `for_plan` verilirse: `<plan_stem>_walkthrough.md` (varsayılan `docs/plans/`, `subdir=True` ise `docs/plans/walkthrough/`).
    - `for_plan` yoksa (bağımsız sprint / geliştirme): `docs/plans/walkthrough/<slug>_<YYYYMMDD_HHMMSS>_walkthrough.md`.
    - Varsayılan `move=False` ile kaynak `<artifact-dir>/walkthrough.md` dosyası korunur.
    """
    src_p = Path(walkthrough_path).resolve()
    if not src_p.is_file():
        raise FileNotFoundError(f"Walkthrough dosyası bulunamadı: {src_p}")

    root_p = Path(project_root).resolve()
    plans_dir = root_p / "docs" / "plans"
    target_dir = (plans_dir / "walkthrough") if (subdir or not for_plan) else plans_dir
    target_dir.mkdir(parents=True, exist_ok=True)

    if for_plan:
        plan_stem = Path(for_plan).stem
        if plan_stem.endswith("_walkthrough"):
            plan_stem = plan_stem[: -len("_walkthrough")]
        filename = f"{plan_stem}_walkthrough.md"
    else:
        clean_slug = _sanitize_token(slug) if slug else "walkthrough"
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{clean_slug}_{timestamp}_walkthrough.md"

    dest_p = target_dir / filename
    dest_p.write_text(src_p.read_text(encoding="utf-8", errors="replace"), encoding="utf-8")

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
    parser.add_argument(
        "--allow-no-wireframe",
        action="store_true",
        help="UI etkileyen planda Before->After Wireframe yoksa çıkarılan [WARN] uyarısını sustur",
    )
    parser.add_argument(
        "--walkthrough",
        action="store_true",
        help="Plan yerine tamamlanan işin walkthrough.md özetini docs/plans/ veya docs/plans/walkthrough/ altına arşivle",
    )
    parser.add_argument(
        "--for-plan",
        default=None,
        help="--walkthrough modunda eşleşecek arşivli plan dosyası (<plan_stem>_walkthrough.md üretir)",
    )
    parser.add_argument(
        "--walkthrough-subdir",
        action="store_true",
        help="--walkthrough çıktısını docs/plans/walkthrough/ alt klasörüne yaz",
    )
    args = parser.parse_args()

    root_p = Path(args.root).resolve()
    if args.walkthrough:
        try:
            dest_p = archive_walkthrough(
                walkthrough_path=args.plan,
                project_root=root_p,
                for_plan=args.for_plan,
                slug=args.slug,
                subdir=args.walkthrough_subdir,
                move=args.move,
            )
        except FileNotFoundError as exc:
            print(f"[ERR] {exc}", file=sys.stderr)
            return 1
        try:
            rel = dest_p.relative_to(root_p)
        except ValueError:
            rel = dest_p
        print(f"[WALKTHROUGH-ARCHIVED] {str(rel).replace(chr(92), '/')}")
        return 0

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
            allow_no_wireframe=args.allow_no_wireframe,
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
