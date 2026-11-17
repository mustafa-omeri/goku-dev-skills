#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PRD Değerlendirme Orkestratörü (review-prd) Deterministik Bağlam ve Analiz Yardımcı Motoru.

Dışarıdan verilen bir PRD dosyasını veya metnini ayrıştırır:
1. Gereksinim kimliklerini (FR/US/NFR/REQ), Gherkin senaryolarını ve başlıkları çıkarır.
2. Belirsiz/ölçülemeyen ifadeleri ("hızlı", "vb.", "uygun şekilde", "scalable" vb.) işaretler.
3. 2+ alternatif içeren mimari/ürün ikilemlerini Council Borda adayları olarak listeler.
4. Hedef projenin dokümanlarını (PROJECT_BRIEF.md, PRODUCT.md, DESIGN.md, HANDOFF.md,
   DB_MIGRATIONS.md) ve kardeş repo ipuçlarını toplayarak tek bağlam paketi üretir.
5. Değerlendirme raporunu docs/plans/prd_review_<slug>_<YYYYMMDD_HHMMSS>.md altına arşivler.
"""
import argparse
import datetime
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

REQ_ID_RE = re.compile(r"\b((?:FR|US|NFR|REQ|EPIC|AC)-[A-Z0-9-]*\d+)\b")
HEADING_RE = re.compile(r"^(#{1,4})\s+(.+)$", re.MULTILINE)
SCENARIO_RE = re.compile(r"^\s*Scenario(?: Outline)?:", re.IGNORECASE | re.MULTILINE)
GHERKIN_KW_RE = re.compile(r"^\s*(?:Feature:|Given |When |Then )", re.IGNORECASE | re.MULTILINE)

AMBIGUITY_PATTERNS = (
    (re.compile(r"\b(?:hızlı|hizli|fast|quick)\b", re.IGNORECASE), "Ölçülebilir SLA/süre eşiği (ms/sn) belirtilmemiş"),
    (re.compile(r"\b(?:kullanıcı dostu|kullanici dostu|user[- ]friendly|intuitive)\b", re.IGNORECASE), "Somut UX ölçütü/akışı tanımlanmamış"),
    (re.compile(r"\b(?:uygun şekilde|uygun sekilde|gerektiğinde|properly|appropriately)\b", re.IGNORECASE), "Kesin iş kuralı/koşulu belirsiz"),
    (re.compile(r"\b(?:vb\.|vs\.|etc\.)(?=\s|$)", re.IGNORECASE), "Açık uçlu kapsam ('vb./etc.') sınırlandırılmamış"),
    (re.compile(r"\b(?:ölçeklenebilir|olceklenebilir|scalable|seamless|sorunsuz)\b", re.IGNORECASE), "Ölçülebilir kapasite/hedef metriği eksik"),
)

COUNCIL_OPTION_RE = re.compile(
    r"\b(?:vs\.?|veya|alternatif|seçenek|secenek|option\s+[a-z0-9]|ya da)\b",
    re.IGNORECASE,
)


def _sanitize_slug(value: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9_]+", "_", value.strip().lower())
    return cleaned.strip("_") or "prd"


def analyze_prd(prd_text: str) -> Dict[str, Any]:
    """PRD metnindeki gereksinimleri, Gherkin durumunu, belirsizlikleri ve konsey adaylarını çıkarır."""
    headings = [f"{m.group(1)} {m.group(2).strip()}" for m in HEADING_RE.finditer(prd_text)]
    requirements: List[str] = []
    seen_reqs = set()
    for match in REQ_ID_RE.finditer(prd_text):
        req_id = match.group(1)
        if req_id not in seen_reqs:
            seen_reqs.add(req_id)
            requirements.append(req_id)

    scenarios = len(SCENARIO_RE.findall(prd_text))
    has_gherkin = scenarios > 0 or len(GHERKIN_KW_RE.findall(prd_text)) >= 3

    ambiguities: List[Dict[str, Any]] = []
    council_candidates: List[Dict[str, Any]] = []

    for lineno, line in enumerate(prd_text.splitlines(), 1):
        stripped = line.strip()
        if not stripped:
            continue
        for pat, reason in AMBIGUITY_PATTERNS:
            m = pat.search(stripped)
            if m:
                ambiguities.append({
                    "line": lineno,
                    "term": m.group(0),
                    "reason": reason,
                    "excerpt": stripped[:140],
                })
        if COUNCIL_OPTION_RE.search(stripped) and not stripped.startswith("#"):
            council_candidates.append({
                "line": lineno,
                "excerpt": stripped[:160],
            })

    return {
        "line_count": len(prd_text.splitlines()),
        "headings": headings[:25],
        "requirements": requirements,
        "has_gherkin": has_gherkin,
        "gherkin_scenarios": scenarios,
        "ambiguities": ambiguities[:20],
        "council_candidates": council_candidates[:15],
    }


def _extract_primary_language(project_root: Path) -> str:
    brief = project_root / "PROJECT_BRIEF.md"
    if brief.is_file():
        text = brief.read_text(encoding="utf-8", errors="replace")
        m = re.search(r"^primary_language:\s*(.+)$", text, re.MULTILINE)
        if m:
            return m.group(1).strip()
    if (project_root / "pom.xml").is_file() or (project_root / "build.gradle").is_file():
        return "Java / Spring Boot"
    if (project_root / "package.json").is_file():
        return "TypeScript / JavaScript"
    if (project_root / "pyproject.toml").is_file() or (project_root / "requirements.txt").is_file():
        return "Python"
    return "Bilinmiyor"


def collect_project_context(project_root: Path | str) -> Dict[str, Any]:
    """Hedef projedeki çekirdek dokümanları, teknoloji yığınını ve kardeş repo ipuçlarını toplar."""
    root_p = Path(project_root).resolve()
    core_docs = (
        "PROJECT_BRIEF.md",
        "PRODUCT.md",
        "DESIGN.md",
        "HANDOFF.md",
        "DB_MIGRATIONS.md",
        "SPRINT_PLAN.md",
        "KANBAN.md",
    )
    docs_status = {doc: (root_p / doc).is_file() for doc in core_docs}

    sibling_hints: List[str] = []
    try:
        fa_scripts = Path(__file__).resolve().parents[2] / "feature-architect" / "scripts"
        if fa_scripts.is_dir() and str(fa_scripts) not in sys.path:
            sys.path.insert(0, str(fa_scripts))
        from fa_engine import discovery as fa_discovery  # type: ignore

        discovered = fa_discovery.discover_peers(root_p, [])
        for peer in discovered.get("peers", []):
            if peer.get("status") in ("CONFIRMED", "CANDIDATE") and peer.get("path"):
                sibling_hints.append(f"{Path(peer['path']).name} ({peer['status']})")
    except Exception:
        pass

    return {
        "project_name": root_p.name,
        "project_root": str(root_p),
        "primary_language": _extract_primary_language(root_p),
        "docs": docs_status,
        "sibling_peers": sibling_hints,
    }


def build_review_bundle(
    project_root: Path | str,
    prd_path: Optional[Path | str] = None,
    prd_text: Optional[str] = None,
) -> Dict[str, Any]:
    """PRD analizi ve proje bağlamını birleşik inceleme paketi olarak döndürür."""
    root_p = Path(project_root).resolve()
    source_label = "inline-prompt"

    if prd_path is not None:
        prd_p = Path(prd_path)
        if not prd_p.is_absolute():
            prd_p = (root_p / prd_p).resolve()
        if not prd_p.is_file():
            raise FileNotFoundError(f"PRD dosyası bulunamadı: {prd_p}")
        prd_text = prd_p.read_text(encoding="utf-8", errors="replace")
        try:
            source_label = str(prd_p.relative_to(root_p)).replace("\\", "/")
        except ValueError:
            source_label = str(prd_p).replace("\\", "/")
    elif prd_text is None:
        raise ValueError("prd_path veya prd_text parametrelerinden biri zorunludur.")

    return {
        "prd_source": source_label,
        "prd_analysis": analyze_prd(prd_text),
        "project_context": collect_project_context(root_p),
    }


def archive_prd_review(
    report_text: str,
    project_root: Path | str,
    slug: str = "prd",
) -> Path:
    """Konsolide PRD değerlendirme raporunu docs/plans/ altına tarih-saat damgasıyla kaydeder."""
    root_p = Path(project_root).resolve()
    plans_dir = root_p / "docs" / "plans"
    plans_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    clean_slug = _sanitize_slug(slug)
    dest = plans_dir / f"prd_review_{clean_slug}_{ts}.md"
    dest.write_text(report_text, encoding="utf-8")
    return dest


def main() -> int:
    parser = argparse.ArgumentParser(
        description="PRD dosyası ile hedef proje bağlamını analiz ederek review-prd paketi üretir."
    )
    parser.add_argument("--root", default=".", help="Hedef proje kök dizini (varsayılan: .)")
    parser.add_argument("--prd", required=True, help="İncelenecek PRD markdown/text dosyasının yolu")
    parser.add_argument("--json", action="store_true", help="Çıktıyı JSON olarak yazdır")
    parser.add_argument("--archive-report", default=None, help="Mevcut rapor dosyasını docs/plans/ altına arşivle")
    parser.add_argument("--slug", default="prd", help="Arşiv dosya adı için kısa slug")
    args = parser.parse_args()

    root_p = Path(args.root).resolve()
    if args.archive_report:
        src = Path(args.archive_report).resolve()
        if not src.is_file():
            print(f"[ERR] Arşivlenecek rapor bulunamadı: {src}", file=sys.stderr)
            return 1
        dest = archive_prd_review(src.read_text(encoding="utf-8", errors="replace"), root_p, slug=args.slug)
        print(f"[ARCHIVED] {dest}")
        return 0

    try:
        bundle = build_review_bundle(root_p, prd_path=args.prd)
    except (FileNotFoundError, ValueError) as exc:
        print(f"[ERR] {exc}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(bundle, ensure_ascii=False, indent=2))
    else:
        a = bundle["prd_analysis"]
        ctx = bundle["project_context"]
        print(f"=== REVIEW-PRD BAĞLAM PAKETİ ({ctx['project_name']}) ===")
        print(f"PRD: {bundle['prd_source']} ({a['line_count']} satır)")
        print(f"Teknoloji: {ctx['primary_language']} · Kardeş Peer: {ctx['sibling_peers'] or 'Yok'}")
        print(f"Gereksinimler: {len(a['requirements'])} ({', '.join(a['requirements'][:8])})")
        print(f"Gherkin Senaryoları: {a['gherkin_scenarios']} (Var mı: {a['has_gherkin']})")
        print(f"Belirsiz İfadeler: {len(a['ambiguities'])} · Council Adayları: {len(a['council_candidates'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
