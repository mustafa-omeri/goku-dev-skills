#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Oturum Devri ve Canlı Görev Panosu (HANDOFF.md) Doğrulama Kapısı.

Kural: .agent/rules/handoff-session-continuity.md
Sınıf: OLCULEBILIR

Denetlenen Hata ve Uyarı Kodları:
  E1 - Repo kökünde yasaklı mükerrer görev dosyası (TASK.md, ACTIVE_TASK.md, TODO.md, TASKS.md).
  E2 - Kapsam içi projede <repo-kök>/HANDOFF.md eksik veya boş.
  E3 - Git çalışma ağacında uygulama kaynak kodu değiştiği halde HANDOFF.md güncellenmemiş.
  E4 - HANDOFF.md üst bilgi/özet alanında doldurulmamış şablon yer tutucusu ([YYYY-MM-DD], [Ajan Adı] vb.).
  W1 - §3 Sıradaki İşler aktif görev tablosunda tamamlanmış (✅ BİTTİ / TAMAMLANDI) satır bırakılmış.
  W2 - Git çalışma ağacında arayüz (UI) bileşeni değiştiği halde KULLANICI_TEST_REHBERI.md mevcut değil.
"""
import argparse
import re
import subprocess
import sys
from pathlib import Path
from typing import List, Tuple

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

FORBIDDEN_TASK_FILES = ("TASK.md", "ACTIVE_TASK.md", "TODO.md", "TASKS.md")

PROJECT_INDICATORS = (
    "package.json",
    "pom.xml",
    "build.gradle",
    "build.gradle.kts",
    "pyproject.toml",
    "requirements.txt",
    "Cargo.toml",
    "go.mod",
    "PROJECT_BRIEF.md",
    "HANDOFF.md",
)

APP_CODE_PREFIXES = (
    "src/",
    "app/",
    "components/",
    "pages/",
    "api/",
    "server/",
    "backend/",
    "frontend/",
    "supabase/",
    "prisma/",
)

UI_EXTENSIONS = (".tsx", ".jsx", ".vue", ".svelte")

PLACEHOLDER_PATTERNS = (
    "[YYYY-MM-DD]",
    "[Ajan Adı]",
    "[Proje Adı]",
    "[değişen dosyalar ve davranış]",
    "[çalıştırılan komutlar ve gerçek sonuç]",
)

INLINE_CODE_RE = re.compile(r"`[^`]+`")
NEXT_WORK_HEADING_RE = re.compile(
    r"^(#{2,4})\s+(?:3\.\s+)?(?:⏭️\s*)?(?:Sıradaki\s+[İi]şler|BURADAN\s+DEVAM\s+ET)\b",
    re.IGNORECASE | re.MULTILINE,
)
ANY_HEADING_RE = re.compile(r"^(#{2,3})\s+\S", re.MULTILINE)
COMPLETED_ROW_RE = re.compile(r"^\|[^|]*\|[^|]*(?:✅\s*(?:BİTTİ|TAMAMLANDI)|\[x\]\s*BİTTİ)\b", re.IGNORECASE | re.MULTILINE)


def is_in_scope(root: Path) -> Tuple[bool, str]:
    for indicator in PROJECT_INDICATORS:
        if (root / indicator).is_file():
            return True, f"proje göstergesi bulundu: {indicator}"
    for f in FORBIDDEN_TASK_FILES:
        if (root / f).is_file():
            return True, f"yasaklı görev dosyası bulundu: {f}"
    return False, "proje göstergesi veya HANDOFF.md bulunamadı (kapsam dışı)"


def _get_git_dirty_files(root: Path) -> List[str]:
    if not (root / ".git").exists():
        return []
    try:
        res = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=str(root),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=5,
        )
        if res.returncode != 0:
            return []
        dirty = []
        for raw_line in res.stdout.splitlines():
            line = raw_line.strip()
            if not line:
                continue
            parts = line.split(maxsplit=1)
            if len(parts) < 2:
                continue
            path_part = parts[1].strip()
            if " -> " in path_part:
                path_part = path_part.split(" -> ", 1)[1].strip()
            dirty.append(path_part.strip('"').replace("\\", "/"))
        return dirty
    except Exception:
        return []


def _extract_active_next_work_block(text: str) -> str:
    """§3 Sıradaki İşler / Aktif Görev Panosu bölümünü bir sonraki başlığa kadar ayıklar."""
    lines = text.splitlines()
    start_idx = None
    start_level = 2

    for idx, line in enumerate(lines):
        stripped = line.strip()
        if re.match(r"^#{2,4}\s+(?:3\.\s+)?(?:🎯\s*)?(?:Sıradaki\s+[İi]şler|Aktif\s+Sprint)", stripped, re.IGNORECASE):
            start_idx = idx
            start_level = len(stripped.split()[0])
            break

    if start_idx is None:
        return ""

    collected = []
    for line in lines[start_idx + 1:]:
        stripped = line.strip()
        m = re.match(r"^(#{2,4})\s+(.*)", stripped)
        if m:
            level = len(m.group(1))
            title_lower = m.group(2).lower()
            # Arşiv, geçmiş veya gelecek faz başlığına gelindiyse aktif panoyu bitir
            if any(k in title_lower for k in ("geçmiş", "arşiv", "tamamlanan", "gelecek", "parking", "sağlık", "nasıl test")):
                break
            if level <= start_level:
                break
        collected.append(line)
    return "\n".join(collected)


def validate_handoff(root: Path, ignore_git_diff: bool = False) -> Tuple[List[Tuple[str, str]], List[Tuple[str, str]]]:
    errors: List[Tuple[str, str]] = []
    warnings: List[Tuple[str, str]] = []

    in_scope, _reason = is_in_scope(root)
    if not in_scope:
        return errors, warnings

    # E1: Yasaklı mükerrer görev takip dosyaları
    for fname in FORBIDDEN_TASK_FILES:
        if (root / fname).is_file():
            errors.append((
                "E1",
                f"Repo kökünde yasaklı mükerrer takip dosyası bulundu: '{fname}'. "
                f"Tek gerçek kaynak HANDOFF.md (§3 Canlı Görev Panosu) olmalıdır.",
            ))

    handoff_file = root / "HANDOFF.md"
    if not handoff_file.is_file():
        errors.append((
            "E2",
            "Proje kökünde HANDOFF.md bulunamadı! (.agent/templates/HANDOFF.template.md şablonundan oluşturun)",
        ))
        return errors, warnings

    try:
        text = handoff_file.read_text(encoding="utf-8")
    except Exception as exc:
        errors.append(("E2", f"HANDOFF.md okunamadı: {exc}"))
        return errors, warnings

    if len(text.strip()) < 50:
        errors.append(("E2", "HANDOFF.md içeriği boş veya çok kısa (< 50 karakter)."))
        return errors, warnings

    # E4: Üst bilgi / özet alanında (ilk 35 satır) doldurulmamış şablon yer tutucusu kontrolü
    head_lines = text.splitlines()[:35]
    head_clean = "\n".join(INLINE_CODE_RE.sub("", ln) for ln in head_lines)
    for token in PLACEHOLDER_PATTERNS:
        if token in head_clean:
            errors.append((
                "E4",
                f"HANDOFF.md içinde doldurulmamış şablon yer tutucusu bulundu: '{token}'.",
            ))

    # W1: §3 Sıradaki İşler aktif panosunda tamamlanmış (✅ BİTTİ / TAMAMLANDI) satır kalıntısı
    active_board = _extract_active_next_work_block(text)
    if active_board and COMPLETED_ROW_RE.search(active_board):
        warnings.append((
            "W1",
            "HANDOFF.md §3 Sıradaki İşler aktif tablosunda tamamlanmış ('✅ BİTTİ' / 'TAMAMLANDI') "
            "satır bulundu. Biten işler §1'e veya arşive taşınmalıdır.",
        ))

    # E3 & W2: Git çalışma ağacı kontrolleri
    if not ignore_git_diff:
        dirty_files = _get_git_dirty_files(root)
        if dirty_files:
            handoff_dirty = "HANDOFF.md" in dirty_files
            changed_app_files = [
                f for f in dirty_files
                if f.startswith(APP_CODE_PREFIXES)
                and not f.endswith((".test.ts", ".test.tsx", ".spec.ts", ".spec.tsx", ".md"))
            ]
            if changed_app_files and not handoff_dirty:
                sample = ", ".join(changed_app_files[:3])
                errors.append((
                    "E3",
                    f"Git çalışma ağacında uygulama kaynak kodu değişti ({sample}) "
                    f"ancak HANDOFF.md güncellenmedi!",
                ))

            changed_ui_files = [
                f for f in changed_app_files
                if f.endswith(UI_EXTENSIONS)
            ]
            if changed_ui_files and not (root / "KULLANICI_TEST_REHBERI.md").is_file():
                warnings.append((
                    "W2",
                    f"Git çalışma ağacında UI bileşeni değişti ({changed_ui_files[0]}) "
                    f"ancak KULLANICI_TEST_REHBERI.md mevcut değil.",
                ))

    return errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser(description="HANDOFF.md oturum devri ve görev panosu doğrulayıcısı")
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="Proje kök dizini")
    parser.add_argument("--strict", action="store_true", help="Uyarıları da hata say")
    parser.add_argument("--ignore-git-diff", action="store_true", help="Git diff E3/W2 denetimini atla")
    args = parser.parse_args()

    root = args.root.resolve()
    in_scope, reason = is_in_scope(root)
    if not in_scope:
        print(f"[SKIP] check_handoff: {reason}")
        return 0

    errors, warnings = validate_handoff(root, ignore_git_diff=args.ignore_git_diff)
    for code, msg in warnings:
        print(f"  [WARN] [{code}] {msg}")
    for code, msg in errors:
        print(f"  [ERR]  [{code}] {msg}")

    if errors or (args.strict and warnings):
        print(f"[FAIL] check_handoff: {len(errors)} hata, {len(warnings)} uyarı.")
        return 1

    print(f"[OK] check_handoff: HANDOFF.md geçerli ({len(warnings)} uyarı).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
