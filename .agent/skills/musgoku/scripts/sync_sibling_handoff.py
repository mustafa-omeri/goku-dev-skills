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


def _upsert_context_note(
    text: str,
    source_name: str,
    plan_ref: str,
    task_id: str,
    task_title: str,
    summary: str,
    today: str,
) -> str:
    """Kaynak proje plan referansı ve sözleşme notunu idempotent olarak işler."""
    begin_marker = f"<!-- XREPO:{task_id}:BEGIN -->"
    end_marker = f"<!-- XREPO:{task_id}:END -->"

    summary_line = _sanitize_cell(summary) if summary else "Detaylar kaynak planda belirtilmiştir."
    note_block = "\n".join([
        begin_marker,
        f"- **[{task_id}]** `{source_name}` projesindeki `{plan_ref}` plan dosyası referansına göre:",
        f"  - **Görev:** {_sanitize_cell(task_title)}",
        f"  - **Kapsam & Sözleşme Özeti:** {summary_line}",
        f"  - **Aktarım Tarihi:** {today}",
        end_marker,
    ])

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


def sync_sibling_handoff(
    sibling_root: Path | str,
    source_root: Path | str,
    plan_ref: str,
    task_id: str,
    task_title: str,
    summary: str = "",
    target_version: str = "Planlı",
    template_path: Optional[Path | str] = None,
) -> Dict[str, Any]:
    """Kardeş uygulamanın HANDOFF.md dosyasına kaynak plan referansı ve görev yazar."""
    src_p = Path(source_root).resolve()
    sib_p = validate_sibling_root(sibling_root, src_p)

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
    )
    handoff_path.write_text(updated, encoding="utf-8")

    errors, warnings = check_handoff.validate_handoff(sib_p, ignore_git_diff=True)
    return {
        "sibling_root": str(sib_p),
        "handoff_path": str(handoff_path),
        "created": created,
        "task_id": clean_task_id,
        "errors": errors,
        "warnings": warnings,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Kardeş uygulamanın HANDOFF.md dosyasına kaynak plan referansı ve görevleri yazar."
    )
    parser.add_argument("--sibling-root", required=True, help="Kardeş uygulama repo kök dizini")
    parser.add_argument("--source-root", default=".", help="Kaynak proje kök dizini (varsayılan: .)")
    parser.add_argument("--plan", required=True, help="Kaynak projedeki onaylı plan dosya yolu")
    parser.add_argument("--task-id", required=True, help="Deterministik görev ID ([DOM]-[TIP]-[NO])")
    parser.add_argument("--task-title", required=True, help="Kardeş uygulamada yapılacak işin kısa başlığı")
    parser.add_argument("--summary", default="", help="Sözleşme / API / DTO / şema değişiklik özeti")
    parser.add_argument("--version", default="Planlı", help="Hedef sürüm (varsayılan: Planlı)")
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
        )
    except ValueError as exc:
        print(f"[ERR] {exc}", file=sys.stderr)
        return 1

    if res["errors"]:
        for code, msg in res["errors"]:
            print(f"[ERR] {code}: {msg}", file=sys.stderr)
        return 1

    action = "oluşturuldu ve işlendi" if res["created"] else "güncellendi"
    print(f"[OK] Kardeş HANDOFF.md {action}: {res['handoff_path']} ({res['task_id']})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
