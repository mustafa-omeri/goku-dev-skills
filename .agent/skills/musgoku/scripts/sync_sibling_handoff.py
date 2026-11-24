#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Kardeş Uygulama (Cross-Repo Sibling) HANDOFF.md Senkronizasyon Motoru.

Bir projede /plan, /feature-architect, /spec-reconcile veya /council ile
hazırlanan ve onaylanan plan sonucunda kardeş uygulamada geliştirme yapılacaksa;
kardeş uygulamanın repo kökündeki HANDOFF.md §3 canlı görev panosuna kaynak
proje plan referansını, sözleşme özetini ve görev satırlarını idempotent işler.

Kullanım:
  python .agent/skills/musgoku/scripts/sync_sibling_handoff.py ^
    --sibling-root ../backend-repo ^
    --source-root . ^
    --plan docs/plans/plan_feature_20261117.md ^
    --task-id BE-API-001 ^
    --task-title "Yeni endpoint ekle" ^
    --summary "POST /api/v1/items sözleşmesi uygulanacak"
"""
import argparse
import datetime
import re
import sys
from pathlib import Path
from typing import Any, Dict, Optional

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

THIS_DIR = Path(__file__).resolve().parent
if str(THIS_DIR) not in sys.path:
    sys.path.insert(0, str(THIS_DIR))

import check_handoff  # noqa: E402


DEFAULT_FALLBACK_HANDOFF = """# HANDOFF — {project_name}

> Güncel: **{today}** · Ajan: **Antigravity (Cross-Repo Sync)**
> Karar kayıtları: `knowledge-base.md`

---

## 0. ⛔ ÖNCE BUNU OKU — Bu Projede Düşülen ve Kanıtlanmış Tuzaklar

| # | Kural & Tuzak | Somut Neden / Ne Yaşandı | Doğru Yol |
|---|---|---|---|
| 1 | yeni yok | | |

---

## 1. Bu Oturumda Yapılanlar (Özet)

- **Kod:** Henüz işlem yapılmadı (kardeş uygulamadan devir alındı).
- **Test:** Bekliyor.
- **Dokümantasyon:** Kardeş uygulama plan referansı eklendi.
- **Doğrulanmayan:** Yok.

---

## 3. ⏭️ BURADAN DEVAM ET

### Sıradaki işler (Canlı Görev Panosu & RTM İzlenebilirlik Matrisi)

#### 🎯 Aktif Sprint / Anlık Görev Panosu (WIP Maks 3)
| ID | Durum | İş / Hedef | Kapsam / PRD Referansı | Hedef Sürüm |
|---|---|---|---|---|
"""


def validate_sibling_root(sibling_root: Path | str, source_root: Path | str) -> Path:
    """Kardeş repo kök dizinini ve kaynak repodan ayrıklığını doğrular."""
    sib_p = Path(sibling_root).resolve()
    src_p = Path(source_root).resolve()

    if not sib_p.is_dir():
        raise ValueError(f"Kardeş uygulama dizini bulunamadı: {sib_p}")
    if sib_p == src_p:
        raise ValueError(f"Kardeş uygulama yolu aktif projeyle aynı olamaz: {sib_p}")

    in_scope, _ = check_handoff.is_in_scope(sib_p)
    has_git = (sib_p / ".git").exists()
    if not in_scope and not has_git:
        raise ValueError(
            f"Hedef dizin geçerli bir proje kökü göstergesi (.git, package.json, pom.xml, HANDOFF.md vb.) taşımıyıyor: {sib_p}"
        )
    return sib_p


def _build_initial_handoff(sibling_root: Path, template_path: Optional[Path] = None) -> str:
    """Kardeş repoda HANDOFF.md yoksa şablondan yer tutucusuz temiz dosya oluşturur."""
    today = datetime.date.today().isoformat()
    project_name = sibling_root.name

    candidates = []
    if template_path is not None:
        candidates.append(Path(template_path))
    candidates.append(sibling_root / ".agent" / "templates" / "HANDOFF.template.md")
    candidates.append(THIS_DIR.parents[2] / "templates" / "HANDOFF.template.md")

    chosen = next((c for c in candidates if c.is_file()), None)
    if chosen is None:
        return DEFAULT_FALLBACK_HANDOFF.format(project_name=project_name, today=today)

    raw = chosen.read_text(encoding="utf-8", errors="replace")
    replacements = {
        "[YYYY-MM-DD]": today,
        "[Ajan Adı]": "Antigravity (Cross-Repo Sync)",
        "[Proje Adı]": project_name,
        "[değişen dosyalar ve davranış]": "Henüz yok (kardeş uygulamadan devir alındı)",
        "[çalıştırılan komutlar ve gerçek sonuç]": "Bekliyor",
        "[güncellenen modül dokümanları]": "HANDOFF.md (§3 Cross-Repo Devir)",
        "[çalıştırılamayan kapılar — sessizce geçilmez]": "Yok",
    }
    text = raw
    for token, value in replacements.items():
        text = text.replace(token, value)

    # Şablondaki örnek [DOM]-... satırlarını temizle ki yalnızca gerçek görevler kalsın
    cleaned_lines = [
        ln for ln in text.splitlines()
        if not re.match(r"^\|\s*\[DOM\]-(?:US|TASK|BUG|PL)-\d+", ln.strip())
    ]
    return "\n".join(cleaned_lines) + "\n"


def _sanitize_cell(value: str) -> str:
    return value.replace("|", "/").replace("\n", " ").strip()


def _upsert_table_row(text: str, task_id: str, row_line: str) -> str:
    """§3 görev tablosunda aynı ID varsa günceller, yoksa tablo sonuna ekler."""
    lines = text.splitlines()
    row_pattern = re.compile(rf"^\|\s*{re.escape(task_id)}\s*\|")
    for idx, line in enumerate(lines):
        if row_pattern.match(line.strip()):
            lines[idx] = row_line
            return "\n".join(lines) + ("\n" if text.endswith("\n") else "")

    # Aktif Sprint veya Sıradaki işler başlığı altındaki ilk Markdown tablosunu bul
    board_start = None
    for idx, line in enumerate(lines):
        if re.match(
            r"^#{2,4}\s+(?:🎯\s*)?(?:Aktif\s+Sprint|Sıradaki\s+[İi]şler|3\.\s+⏭️)",
            line.strip(),
            re.IGNORECASE,
        ):
            board_start = idx
            if "Aktif Sprint" in line:
                break

    if board_start is not None:
        table_sep_idx = None
        last_table_row_idx = None
        for idx in range(board_start + 1, len(lines)):
            stripped = lines[idx].strip()
            if re.match(r"^#{2,4}\s+", stripped) and idx > board_start + 1 and table_sep_idx is not None:
                break
            if stripped.startswith("|---") or re.match(r"^\|[\s:-]+\|", stripped):
                table_sep_idx = idx
                last_table_row_idx = idx
            elif table_sep_idx is not None and stripped.startswith("|"):
                last_table_row_idx = idx
            elif table_sep_idx is not None and stripped == "":
                break

        if last_table_row_idx is not None:
            lines.insert(last_table_row_idx + 1, row_line)
            return "\n".join(lines) + "\n"

        # Başlık var ama tablo yoksa başlığın hemen altına tablo aç
        insert_pos = board_start + 1
        table_block = [
            "| ID | Durum | İş / Hedef | Kapsam / PRD Referansı | Hedef Sürüm |",
            "|---|---|---|---|---|",
            row_line,
        ]
        for offset, tbl_ln in enumerate(table_block):
            lines.insert(insert_pos + offset, tbl_ln)
        return "\n".join(lines) + "\n"

    # §3 başlığı hiç yoksa sona ekle
    suffix = [
        "",
        "## 3. ⏭️ BURADAN DEVAM ET",
        "",
        "#### 🎯 Aktif Sprint / Anlık Görev Panosu (WIP Maks 3)",
        "| ID | Durum | İş / Hedef | Kapsam / PRD Referansı | Hedef Sürüm |",
        "|---|---|---|---|---|",
        row_line,
    ]
    return text.rstrip() + "\n" + "\n".join(suffix) + "\n"


UI_WIREFRAME_NOTE = (
    "[UI-ÖN-TASARIM ZORUNLU] Kardeş repo frontend kodlamadan önce kendi DESIGN.md sözleşmesine göre "
    "Before -> After Wireframe (veya --ui-preview / --ui-ux ile 1:1 gerçek ekran kilidi) onayına sunulmalıdır."
)


def _upsert_context_note(
    text: str,
    source_name: str,
    plan_ref: str,
    task_id: str,
    task_title: str,
    summary: str,
    today: str,
    ui_wireframe_expected: bool = False,
) -> str:
    """Kaynak proje plan referansı ve sözleşme notunu idempotent olarak işler."""
    begin_marker = f"<!-- XREPO:{task_id}:BEGIN -->"
    end_marker = f"<!-- XREPO:{task_id}:END -->"

    summary_line = _sanitize_cell(summary) if summary else "Detaylar kaynak planda belirtilmiştir."
    note_lines = [
        begin_marker,
        f"- **[{task_id}]** `{source_name}` projesindeki `{plan_ref}` plan dosyası referansına göre:",
        f"  - **Görev:** {_sanitize_cell(task_title)}",
        f"  - **Kapsam & Sözleşme Özeti:** {summary_line}",
    ]
    if ui_wireframe_expected:
        note_lines.append(f"  - **UI Ön-Tasarım Zorunluluğu:** {UI_WIREFRAME_NOTE}")
    note_lines.extend([
        f"  - **Aktarım Tarihi:** {today}",
        end_marker,
    ])
    note_block = "\n".join(note_lines)

    pattern = re.compile(
        rf"{re.escape(begin_marker)}.*?{re.escape(end_marker)}",
        re.DOTALL,
    )
    if pattern.search(text):
        return pattern.sub(note_block, text, count=1)

    section_heading = "#### 🔗 Kardeş Uygulama Plan & Sözleşme Devri (Cross-Repo Handoff)"
    if section_heading in text:
        return text.replace(section_heading, f"{section_heading}\n{note_block}", 1)

    # §3 altında Gelecek Fazlar veya Sağlık durumu öncesine ekle
    anchor_patterns = (
        r"^####\s+📌\s+Gelecek\s+Fazlar",
        r"^###\s+Sağlık\s+durumu",
        r"^###\s+Nasıl\s+Test\s+Edilir",
    )
    lines = text.splitlines()
    for idx, line in enumerate(lines):
        if any(re.match(pat, line.strip(), re.IGNORECASE) for pat in anchor_patterns):
            lines.insert(idx, "")
            lines.insert(idx, note_block)
            lines.insert(idx, section_heading)
            return "\n".join(lines) + "\n"

    return text.rstrip() + f"\n\n{section_heading}\n{note_block}\n"


def detect_directory_topology(
    sibling_root: Path | str,
    source_root: Path | str,
    workspace_mode: str = "auto",
) -> Dict[str, Any]:
    """Kardeş projenin aktif projeyle aynı dizin/workspace altında mı yoksa farklı dizinde mi olduğunu saptar.

    - Aynı dizin (aynı üst workspace / monorepo / eş düzey klasör):
      `SAME_AGENT_ALLOWED` — skill'ler projeye göre yüklendiği için aynı kod ajanı süreci ilerletebilir.
    - Farklı dizin (bağımsız dizin / ayrı çalışma alanı):
      `ASK_USER_PREFER_SIBLING_AGENT` — öncelik kardeş projenin kendi kod ajanındadır; öncesinde kullanıcıya sorulmalıdır.
    """
    sib_p = Path(sibling_root).resolve()
    src_p = Path(source_root).resolve()

    mode = (workspace_mode or "auto").strip().lower()
    if mode == "same":
        same_dir = True
    elif mode == "different":
        same_dir = False
    else:
        # Monorepo (biri diğerinin altında) veya aynı workspace ebeveyn dizini altında yan yana
        same_parent = sib_p.parent == src_p.parent
        nested = (src_p in sib_p.parents) or (sib_p in src_p.parents)
        same_dir = bool(same_parent or nested)

    if same_dir:
        policy = "SAME_AGENT_ALLOWED"
        guidance = (
            "Kardeş proje aynı dizin/çalışma alanında: skill'ler projeye göre yüklendiği için "
            "aynı kod ajanı süreci ilerletebilir."
        )
    else:
        policy = "ASK_USER_PREFER_SIBLING_AGENT"
        guidance = (
            "Kardeş proje farklı dizinde: öncelik her projenin kendi kod ajanındadır; "
            "kardeş projede geliştirmeye başlamadan önce kullanıcıya açıkça sorulmalıdır."
        )

    return {
        "same_directory": same_dir,
        "workspace_mode": mode,
        "ownership_policy": policy,
        "guidance": guidance,
    }


def _next_sprint_card_id(kanban_text: str, sprint_plan_text: str = "") -> tuple[str, str]:
    """KANBAN.md için çakışmasız ve check_sprint_board.py uyumlu S<n>-<nn> kart ID'si üretir."""
    matches = re.findall(r"\bS(\d+)-(\d+)\b", kanban_text + "\n" + sprint_plan_text)
    if not matches:
        return "S1-01", "S1"
    max_sprint = max(int(s) for s, _ in matches)
    nums_in_sprint = [int(n) for s, n in matches if int(s) == max_sprint]
    next_num = (max(nums_in_sprint) + 1) if nums_in_sprint else 1
    return f"S{max_sprint}-{next_num:02d}", f"S{max_sprint}"


def _sync_sibling_process_files(
    sib_p: Path,
    source_name: str,
    plan_ref: str,
    task_id: str,
    task_title: str,
    summary: str,
    ui_wireframe_expected: bool = False,
) -> list[str]:
    """Dizin fark etmeksizin kardeş projedeki süreç dosyalarına (KANBAN, SPRINT_PLAN, RELEASE_PLAN) görev ve plan referansını ekler."""
    synced: list[str] = []
    kanban_p = sib_p / "KANBAN.md"
    sprint_p = sib_p / "SPRINT_PLAN.md"
    release_p = sib_p / "RELEASE_PLAN.md"

    kanban_text = kanban_p.read_text(encoding="utf-8", errors="replace") if kanban_p.is_file() else ""
    sprint_text = sprint_p.read_text(encoding="utf-8", errors="replace") if sprint_p.is_file() else ""

    if re.match(r"^S\d+-\d+$", task_id):
        card_id = task_id
        sprint_tag = task_id.split("-")[0]
    else:
        card_id, sprint_tag = _next_sprint_card_id(kanban_text, sprint_text)

    ref_note = f"{source_name} projesindeki `{plan_ref}` plan dosyası referansına göre"
    safe_title = _sanitize_cell(task_title)
    safe_summary = _sanitize_cell(summary) if summary else ref_note
    ui_tag = " [UI-ÖN-TASARIM ZORUNLU]" if ui_wireframe_expected else ""

    if kanban_p.is_file() and task_id not in kanban_text:
        ui_row = (
            f"| ui_on_tasarim | [UI-ÖN-TASARIM ZORUNLU] Koddan önce DESIGN.md + Before -> After Wireframe (--ui-preview / --ui-ux) onayı |\n"
            if ui_wireframe_expected
            else ""
        )
        card_block = (
            f"\n### {card_id} · {task_id}: {safe_title}\n"
            f"| alan | değer |\n"
            f"|---|---|\n"
            f"| durum | Bekliyor |\n"
            f"| oncelik | P1 |\n"
            f"| sprint | {sprint_tag} |\n"
            f"| gherkin | specs/{card_id}.feature |\n"
            f"| kapi | python .agent/skills/musgoku/scripts/check_handoff.py |\n"
            f"| test | (yazılacak) — {ref_note}{ui_tag} |\n"
            f"{ui_row}"
            f"| risk | orta |\n"
        )
        m_bekliyor = re.search(r"^##\s+Bekliyor\s*$", kanban_text, re.MULTILINE)
        if m_bekliyor:
            pos = m_bekliyor.end()
            updated_kanban = kanban_text[:pos] + "\n" + card_block + kanban_text[pos:]
        else:
            updated_kanban = kanban_text.rstrip() + "\n\n## Bekliyor\n" + card_block
        kanban_p.write_text(updated_kanban.rstrip() + "\n", encoding="utf-8")
        synced.append("KANBAN.md")

    if sprint_p.is_file() and task_id not in sprint_text:
        mvp_line = f"- {card_id} · `{task_id}`: {safe_title} ({ref_note} — {safe_summary}){ui_tag}"
        m_mvp = re.search(r"^(?:#{2,4}\s+MVP\s+Kapsam|\*\*MVP\s+Kapsam\*\*).*$", sprint_text, re.MULTILINE)
        if m_mvp:
            pos = m_mvp.end()
            updated_sprint = sprint_text[:pos] + f"\n{mvp_line}" + sprint_text[pos:]
        else:
            updated_sprint = sprint_text.rstrip() + f"\n\n### MVP Kapsam\n{mvp_line}\n"
        sprint_p.write_text(updated_sprint.rstrip() + "\n", encoding="utf-8")
        synced.append("SPRINT_PLAN.md")

    if release_p.is_file():
        release_text = release_p.read_text(encoding="utf-8", errors="replace")
        if task_id not in release_text:
            rel_row = f"| {card_id} | {task_id}: {safe_title} ({ref_note}) | {sprint_tag} | orta |"
            m_rel = re.search(r"^##\s+2\.\s+Taşınan.*$", release_text, re.MULTILINE)
            if m_rel:
                lines = release_text.splitlines()
                insert_idx = len(lines)
                for idx, ln in enumerate(lines):
                    if re.match(r"^##\s+2\.", ln.strip()):
                        for j in range(idx + 1, len(lines)):
                            if lines[j].strip().startswith("|"):
                                insert_idx = j + 1
                            elif lines[j].strip().startswith("## "):
                                break
                        break
                lines.insert(insert_idx, rel_row)
                updated_release = "\n".join(lines) + "\n"
            else:
                updated_release = release_text.rstrip() + f"\n\n| Kart | Neden | Yeni sprint | Risk |\n|---|---|---|---|\n{rel_row}\n"
            release_p.write_text(updated_release, encoding="utf-8")
            synced.append("RELEASE_PLAN.md")

    return synced


def sync_sibling_handoff(
    sibling_root: Path | str,
    source_root: Path | str,
    plan_ref: str,
    task_id: str,
    task_title: str,
    summary: str = "",
    target_version: str = "Planlı",
    template_path: Optional[Path | str] = None,
    workspace_mode: str = "auto",
    ui_wireframe_expected: bool = False,
) -> Dict[str, Any]:
    """Kardeş uygulamanın HANDOFF.md ve süreç dosyalarına kaynak plan referansı ve görev yazar."""
    src_p = Path(source_root).resolve()
    sib_p = validate_sibling_root(sibling_root, src_p)
    topology = detect_directory_topology(sib_p, src_p, workspace_mode=workspace_mode)

    clean_task_id = task_id.strip()
    if not clean_task_id:
        raise ValueError("task_id boş olamaz.")
    clean_plan_ref = plan_ref.strip().replace("\\", "/")
    if not clean_plan_ref:
        raise ValueError("plan_ref boş olamaz.")

    handoff_path = sib_p / "HANDOFF.md"
    created = not handoff_path.is_file() or len(handoff_path.read_text(encoding="utf-8", errors="replace").strip()) < 50
    if created:
        text = _build_initial_handoff(sib_p, Path(template_path) if template_path else None)
    else:
        text = handoff_path.read_text(encoding="utf-8", errors="replace")

    today = datetime.date.today().isoformat()
    source_name = src_p.name
    ref_cell = f"{source_name} projesindeki `{clean_plan_ref}` plan dosyası referansına göre"
    if ui_wireframe_expected:
        ref_cell += " [UI-ÖN-TASARIM ZORUNLU]"
    row_line = (
        f"| {_sanitize_cell(clean_task_id)} | ⏭️ | {_sanitize_cell(task_title)} "
        f"| {_sanitize_cell(ref_cell)} | {_sanitize_cell(target_version)} |"
    )

    updated = _upsert_table_row(text, clean_task_id, row_line)
    updated = _upsert_context_note(
        updated,
        source_name=source_name,
        plan_ref=clean_plan_ref,
        task_id=clean_task_id,
        task_title=task_title,
        summary=summary,
        today=today,
        ui_wireframe_expected=ui_wireframe_expected,
    )
    handoff_path.write_text(updated, encoding="utf-8")

    synced_process_files = _sync_sibling_process_files(
        sib_p=sib_p,
        source_name=source_name,
        plan_ref=clean_plan_ref,
        task_id=clean_task_id,
        task_title=task_title,
        summary=summary,
        ui_wireframe_expected=ui_wireframe_expected,
    )

    errors, warnings = check_handoff.validate_handoff(sib_p, ignore_git_diff=True)
    return {
        "sibling_root": str(sib_p),
        "handoff_path": str(handoff_path),
        "created": created,
        "task_id": clean_task_id,
        "topology": topology,
        "synced_process_files": synced_process_files,
        "ui_wireframe_expected": bool(ui_wireframe_expected),
        "errors": errors,
        "warnings": warnings,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Kardeş uygulamanın HANDOFF.md ve süreç dosyalarına kaynak plan referansı ve görevleri yazar."
    )
    parser.add_argument("--sibling-root", required=True, help="Kardeş uygulama repo kök dizini")
    parser.add_argument("--source-root", default=".", help="Kaynak proje kök dizini (varsayılan: .)")
    parser.add_argument("--plan", required=True, help="Kaynak projedeki onaylı plan dosya yolu")
    parser.add_argument("--task-id", required=True, help="Deterministik görev ID ([DOM]-[TIP]-[NO])")
    parser.add_argument("--task-title", required=True, help="Kardeş uygulamada yapılacak işin kısa başlığı")
    parser.add_argument("--summary", default="", help="Sözleşme / API / DTO / şema değişiklik özeti")
    parser.add_argument("--version", default="Planlı", help="Hedef sürüm (varsayılan: Planlı)")
    parser.add_argument(
        "--workspace-mode",
        choices=["auto", "same", "different"],
        default="auto",
        help="Aynı dizin / farklı dizin sahiplik kipi (varsayılan: auto)",
    )
    parser.add_argument(
        "--ui-wireframe-expected",
        action="store_true",
        help="Kardeş projede kodlamadan önce DESIGN.md + Before->After Wireframe onayı istendiğini işaretle",
    )
    args = parser.parse_args()

    try:
        res = sync_sibling_handoff(
            sibling_root=args.sibling_root,
            source_root=args.source_root,
            plan_ref=args.plan,
            task_id=args.task_id,
            task_title=args.task_title,
            summary=args.summary,
            target_version=args.version,
            workspace_mode=args.workspace_mode,
            ui_wireframe_expected=args.ui_wireframe_expected,
        )
    except ValueError as exc:
        print(f"[ERR] {exc}", file=sys.stderr)
        return 1

    if res["errors"]:
        for code, msg in res["errors"]:
            print(f"[ERR] {code}: {msg}", file=sys.stderr)
        return 1

    action = "oluşturuldu ve işlendi" if res["created"] else "güncellendi"
    proc_info = ", ".join(res["synced_process_files"]) if res["synced_process_files"] else "HANDOFF.md"
    print(f"[OK] Kardeş HANDOFF.md {action}: {res['handoff_path']} ({res['task_id']}) | Süreçler: {proc_info}")
    print(f"[TOPOLOGY] {res['topology']['ownership_policy']}: {res['topology']['guidance']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
