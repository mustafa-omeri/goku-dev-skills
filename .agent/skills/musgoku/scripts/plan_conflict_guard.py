#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Ön-Mühürleme (/seal-plan) ve Sprint/Kanban Plan Çakışma, Tekrar & Ezme Kalkanı.

Kural: .agent/rules/development-workflow.md Adım 2.2 · handoff-session-continuity.md · sprint-delivery-workflow.md
Amaç:
  1. Yeni planın / kartın canlı kod tabanı ve tamamlanan işlerle kıyaslanması:
     - ALREADY_DONE_EXACT           : Birebir aynı dosya/endpoint/kapsam zaten canlıda/Yapıldı'da var.
     - ENRICHED_SUPERSET            : Mevcut kod üzerine yeni katman/güvenlik/UX ekliyor ([NEW] -> [MODIFY] uyarısı).
     - SIMPLIFIED_SUBSET_REGRESSION : Canlıda daha zengin/korumalı yapı varken sade/eksik planla ezme riski (CRITICAL).
  2. Bekleyen sıralı mühürlü planlar (docs/plans/, HANDOFF.md §3, KANBAN.md) arası ezme tespiti:
     - DOUBLE_NEW_COLLISION         : İki bekleyen plan aynı dosyayı/tabloyu [NEW] ile oluşturuyor (CRITICAL).
     - MODIFY_DELETE_CLOBBER        : Biri [NEW]/[MODIFY] yaparken diğeri [DELETE] ediyor (CRITICAL).
     - SHARED_SURFACE_OVERWRITE     : İki bekleyen plan aynı dosya, endpoint, rota veya DB tablosuna dokunuyor (WARNING).
     - SEQUENTIAL_ORDER_DEPENDENCY  : Yeni plan, henüz canlıda olmayan ama bekleyen Plan A'nın [NEW] dosyasını [MODIFY] ediyor.
     - BACKLOG_SEMANTIC_DUPLICATE   : KANBAN/HANDOFF kuyruğunda farklı ID ile aynı hedef/başlık bekliyor.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

THIS_DIR = Path(__file__).resolve().parent
if str(THIS_DIR) not in sys.path:
    sys.path.insert(0, str(THIS_DIR))

PLAN_TASK_ID_RE = re.compile(
    r"\b([A-Z0-9]{2,10}-(?:FEAT|TASK|BUG|US|PL|ARCH|PO|UX|QA|GRW|MIG|DB|INFRA|SEC|AUTH|DOCS|OPT|DEL|CI|HYG|REP|DASH|RBAC|FE|BE)-[0-9]{2,4}|S\d+-\d+)\b"
)

FILE_ACTION_HEADING_RE = re.compile(
    r"^#{2,5}\s+\[(NEW|MODIFY|DELETE)\]\s+`?([^\s`<>\"'|\)]+)`?",
    re.IGNORECASE | re.MULTILINE,
)

ENDPOINT_RE = re.compile(
    r"\b(GET|POST|PUT|PATCH|DELETE)\s+(/api/[A-Za-z0-9_/{}/.:-]+|/v[0-9]+/[A-Za-z0-9_/{}/.:-]+)",
    re.IGNORECASE,
)
FETCH_ENDPOINT_RE = re.compile(
    r"""(?:fetch|axios\.\w+|apiClient\.\w+|api\.\w+)\s*\(\s*[`"'](/api/[A-Za-z0-9_/{}/.:-]+|/v[0-9]+/[A-Za-z0-9_/{}/.:-]+)[`"']""",
    re.IGNORECASE,
)

ROUTE_RE = re.compile(
    r"""(?:route\s*[:=]\s*|path\s*[:=]\s*|`)(/[a-z][a-z0-9_/-]{1,48})(?:[`"'\s,]|$)""",
    re.IGNORECASE,
)

DB_TABLE_RE = re.compile(
    r"\b(?:CREATE\s+TABLE(?:\s+IF\s+NOT\s+EXISTS)?|ALTER\s+TABLE|DROP\s+TABLE)\s+(?:public\.)?`?\"?([a-zA-Z_][a-zA-Z0-9_]*)\"?`?",
    re.IGNORECASE,
)

TEMPLATE_PLACEHOLDERS = ("yol/yeni_dosya.ext", "yol/mevcut_dosya.ext", "yol/silinecek_dosya.ext", "<doldur")

RICHNESS_PATTERNS: Dict[str, re.Pattern[str]] = {
    "rls": re.compile(r"\b(?:ROW LEVEL SECURITY|RLS|WITH CHECK|USING\s*\()\b", re.IGNORECASE),
    "turnstile_bot": re.compile(r"\b(?:turnstile|captcha|honeypot)\b", re.IGNORECASE),
    "rate_limit": re.compile(r"\b(?:rate[-_\s]?limit|rateLimit|429)\b", re.IGNORECASE),
    "validation": re.compile(r"\b(?:zod|z\.object|@valid|jakarta\.validation|schema)\b", re.IGNORECASE),
    "idempotency": re.compile(r"\b(?:idempotency-key|idempotency|@version|optimistic\s+lock)\b", re.IGNORECASE),
    "skeleton_ui": re.compile(r"\b(?:skeleton|zero-cls|shimmer|animate-pulse)\b", re.IGNORECASE),
    "migration_sql": re.compile(r"\b(?:CREATE TABLE|ALTER TABLE|supabase/migrations|db/migration)\b", re.IGNORECASE),
    "tests_gherkin": re.compile(r"\b(?:Scenario:|Given |When |Then |unittest|vitest|pytest)\b", re.IGNORECASE),
}

SKIP_DIRS = {
    ".git",
    "node_modules",
    "dist",
    "build",
    "target",
    ".next",
    ".venv",
    "venv",
    "__pycache__",
    ".pytest_cache",
    ".agent",
    "docs",
    "yedekler",
    "coverage",
}

CODE_EXTENSIONS = {
    ".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs",
    ".py", ".java", ".kt", ".sql", ".prisma", ".vue", ".svelte", ".go", ".rs",
}

_TR_FOLD = str.maketrans("çğıöşüÇĞİÖŞÜâîûÂÎÛ", "cgiosuCGIOSUaiuAIU")
STOP_WORDS = {
    "ve", "ile", "icin", "olan", "bir", "bu", "icin", "plani", "plan", "ekle", "eklensin",
    "olustur", "yaz", "yeni", "mevcut", "guncelle", "revize", "yap", "edilsin", "and",
    "the", "for", "with", "add", "create", "update", "new", "feature", "task", "kart",
    "ekrani", "sayfasi", "servisi", "modulu", "uygulama", "gelistir", "gelistirme",
}


def normalize_path(raw: str) -> str:
    cleaned = raw.strip().strip("`\"'(),;")
    cleaned = cleaned.replace("\\", "/")
    while cleaned.startswith("./"):
        cleaned = cleaned[2:]
    return cleaned


def tokenize(text: str) -> Set[str]:
    folded = text.translate(_TR_FOLD).lower()
    raw_tokens = re.findall(r"[a-z0-9]{3,}", folded)
    return {t for t in raw_tokens if t not in STOP_WORDS}


def jaccard(a: Set[str], b: Set[str]) -> float:
    if not a or not b:
        return 0.0
    inter = len(a & b)
    union = len(a | b)
    return round(inter / union, 3) if union else 0.0


def _strip_audit_and_ditching_sections(text: str) -> str:
    """Önceki mühürleme çakışma audit bloğunu analiz dışı bırakır (kendini tekrar yakalamasın)."""
    cleaned = re.sub(
        r"<!--\s*PRE-SEAL-CONFLICT-AUDIT:BEGIN\s*-->.*?<!--\s*PRE-SEAL-CONFLICT-AUDIT:END\s*-->",
        "",
        text,
        flags=re.DOTALL | re.IGNORECASE,
    )
    cleaned = re.split(r"^##\s+(?:11\.\s+🚨|⚠️\s+Ön-Mühürleme)", cleaned, maxsplit=1, flags=re.MULTILINE)[0]
    return cleaned


def _extract_richness_signals(text: str) -> Set[str]:
    signals: Set[str] = set()
    for name, pat in RICHNESS_PATTERNS.items():
        if pat.search(text):
            signals.add(name)
    return signals


def _normalize_endpoint(method: str, path: str) -> str:
    norm_path = re.sub(r"\{[^}]+\}|\$\{[^}]+\}", "{id}", path.strip())
    norm_path = norm_path.rstrip("/") or "/"
    return f"{method.upper()} {norm_path}"


@dataclass
class PlanFootprint:
    plan_ref: str
    title: str
    task_ids: List[str] = field(default_factory=list)
    file_actions: Dict[str, Set[str]] = field(
        default_factory=lambda: {"NEW": set(), "MODIFY": set(), "DELETE": set()}
    )
    endpoints: Set[str] = field(default_factory=set)
    routes: Set[str] = field(default_factory=set)
    db_tables: Set[str] = field(default_factory=set)
    richness_signals: Set[str] = field(default_factory=set)
    title_tokens: Set[str] = field(default_factory=set)

    @property
    def all_files(self) -> Set[str]:
        return self.file_actions["NEW"] | self.file_actions["MODIFY"] | self.file_actions["DELETE"]

    def to_summary(self) -> Dict[str, Any]:
        return {
            "plan_ref": self.plan_ref,
            "title": self.title,
            "task_ids": self.task_ids,
            "files": {k: sorted(v) for k, v in self.file_actions.items()},
            "endpoints": sorted(self.endpoints),
            "routes": sorted(self.routes),
            "db_tables": sorted(self.db_tables),
            "richness_signals": sorted(self.richness_signals),
        }


def extract_plan_footprint(plan_text: str, plan_ref: str = "inline-plan") -> PlanFootprint:
    body = _strip_audit_and_ditching_sections(plan_text)
    title = plan_ref
    m_title = re.search(r"^#\s+(.+)$", body, re.MULTILINE)
    if m_title:
        title = m_title.group(1).strip()

    task_ids: List[str] = []
    seen_ids: Set[str] = set()
    for tid in PLAN_TASK_ID_RE.findall(body):
        if tid not in seen_ids:
            seen_ids.add(tid)
            task_ids.append(tid)

    file_actions: Dict[str, Set[str]] = {"NEW": set(), "MODIFY": set(), "DELETE": set()}
    for m in FILE_ACTION_HEADING_RE.finditer(body):
        action = m.group(1).upper()
        fpath = normalize_path(m.group(2))
        if not fpath or any(ph in fpath for ph in TEMPLATE_PLACEHOLDERS):
            continue
        file_actions[action].add(fpath)

    endpoints: Set[str] = set()
    for m in ENDPOINT_RE.finditer(body):
        endpoints.add(_normalize_endpoint(m.group(1), m.group(2)))

    routes: Set[str] = set()
    for m in ROUTE_RE.finditer(body):
        r = m.group(1).strip().rstrip("/")
        if r and not r.startswith(("/api", "/v1", "/v2")) and "." not in r:
            routes.add(r)

    db_tables: Set[str] = set()
    for m in DB_TABLE_RE.finditer(body):
        db_tables.add(m.group(1).lower())

    richness_signals = _extract_richness_signals(body)
    title_tokens = tokenize(title + " " + " ".join(sorted(file_actions["NEW"] | file_actions["MODIFY"])))

    return PlanFootprint(
        plan_ref=plan_ref,
        title=title,
        task_ids=task_ids,
        file_actions=file_actions,
        endpoints=endpoints,
        routes=routes,
        db_tables=db_tables,
        richness_signals=richness_signals,
        title_tokens=title_tokens,
    )


def scan_live_codebase(root: Path) -> Dict[str, Any]:
    """Canlı kod tabanındaki dosyaları, endpoint'leri, DB tablolarını ve zenginlik sinyallerini çıkarır."""
    files: Dict[str, Dict[str, Any]] = {}
    endpoints: Dict[str, List[str]] = {}
    db_tables: Dict[str, List[str]] = {}
    routes: Dict[str, List[str]] = {}

    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".git")]
        for fname in filenames:
            ext = Path(fname).suffix.lower()
            if ext not in CODE_EXTENSIONS:
                continue
            full_p = Path(dirpath) / fname
            try:
                rel_p = full_p.relative_to(root).as_posix()
                content = full_p.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue

            sig = _extract_richness_signals(content)
            if ext == ".sql" or "migrations" in rel_p:
                sig.add("migration_sql")
            files[rel_p] = {
                "signals": sig,
                "lines": len(content.splitlines()),
            }

            for m in ENDPOINT_RE.finditer(content):
                ep = _normalize_endpoint(m.group(1), m.group(2))
                endpoints.setdefault(ep, []).append(rel_p)
            for m in FETCH_ENDPOINT_RE.finditer(content):
                ep = _normalize_endpoint("ANY", m.group(1))
                endpoints.setdefault(ep, []).append(rel_p)
            for m in DB_TABLE_RE.finditer(content):
                tbl = m.group(1).lower()
                db_tables.setdefault(tbl, []).append(rel_p)
            for m in ROUTE_RE.finditer(content):
                r = m.group(1).strip().rstrip("/")
                if r and not r.startswith(("/api", "/v1", "/v2")) and "." not in r:
                    routes.setdefault(r, []).append(rel_p)

    return {
        "files": files,
        "endpoints": endpoints,
        "db_tables": db_tables,
        "routes": routes,
    }


def _collect_done_history(root: Path) -> Dict[str, Any]:
    """HANDOFF.md §1/Tamamlananlar ve KANBAN.md Yapıldı kartlarını toplar."""
    done_ids: Set[str] = set()
    done_items: List[Dict[str, Any]] = []

    handoff_p = root / "HANDOFF.md"
    if handoff_p.is_file():
        htext = handoff_p.read_text(encoding="utf-8", errors="replace")
        # §1 (bir sonraki ## 2. / ## 3. vb. başlığa kadar)
        m_sec1 = re.search(r"^##\s+1\b.*?(?=^##\s+\d+|\Z)", htext, re.DOTALL | re.MULTILINE)
        sec1 = m_sec1.group(0) if m_sec1 else ""
        for line in sec1.splitlines():
            for tid in PLAN_TASK_ID_RE.findall(line):
                done_ids.add(tid)
            if line.strip().startswith(("-", "*")):
                done_items.append({"source": "HANDOFF.md §1", "title": line.strip(), "tokens": tokenize(line)})

        for line in htext.splitlines():
            if "✅" in line and ("Tamamlandı" in line or "BİTTİ" in line or "DONE" in line):
                for tid in PLAN_TASK_ID_RE.findall(line):
                    done_ids.add(tid)
                done_items.append({"source": "HANDOFF.md (Tamamlanan)", "title": line.strip(), "tokens": tokenize(line)})

    kanban_p = root / "KANBAN.md"
    if kanban_p.is_file():
        ktext = kanban_p.read_text(encoding="utf-8", errors="replace")
        in_done = False
        for line in ktext.splitlines():
            s = line.strip()
            if s.startswith("## "):
                in_done = s.lower() == "## yapıldı"
                continue
            if in_done and s.startswith("### "):
                for tid in PLAN_TASK_ID_RE.findall(s):
                    done_ids.add(tid)
                done_items.append({"source": "KANBAN.md (Yapıldı)", "title": s, "tokens": tokenize(s)})

    return {"done_ids": done_ids, "done_items": done_items}


def _collect_queued_plans_and_backlog(root: Path, exclude_plan: Optional[Path] = None) -> Dict[str, Any]:
    """Henüz tamamlanmamış (Bekliyor / Yapılıyor) planları ve KANBAN/HANDOFF maddelerini toplar."""
    exclude_res = exclude_plan.resolve() if exclude_plan else None
    done_hist = _collect_done_history(root)
    done_ids = done_hist["done_ids"]

    handoff_p = root / "HANDOFF.md"
    handoff_text = handoff_p.read_text(encoding="utf-8", errors="replace") if handoff_p.is_file() else ""

    completed_plan_names: Set[str] = set()
    for line in handoff_text.splitlines():
        if "✅" in line and ("Tamamlandı" in line or "BİTTİ" in line):
            for m in re.findall(r"([A-Za-z0-9_.\-]+\.md)", line):
                completed_plan_names.add(Path(m).name)

    queued_plans: List[PlanFootprint] = []
    seen_paths: Set[Path] = set()
    for pdir in (root / "docs" / "plans", root / ".agent" / "plans"):
        if not pdir.is_dir():
            continue
        for pfile in sorted(pdir.rglob("*.md")):
            resolved = pfile.resolve()
            if resolved in seen_paths or (exclude_res and resolved == exclude_res):
                continue
            lower_parts = [part.lower() for part in pfile.parts]
            if "archive" in lower_parts or "walkthrough" in lower_parts or "walkthrough" in pfile.name.lower():
                continue
            if pfile.name in completed_plan_names:
                continue
            seen_paths.add(resolved)
            try:
                content = pfile.read_text(encoding="utf-8", errors="replace")
                rel = pfile.relative_to(root).as_posix()
            except Exception:
                continue
            fp = extract_plan_footprint(content, plan_ref=rel)
            # Plandaki tüm görev ID'leri Yapıldı/Tamamlandı listesinde ise bu plan artık kuyrukta değil
            if fp.task_ids and all(tid in done_ids for tid in fp.task_ids):
                continue
            queued_plans.append(fp)

    # Açık KANBAN kartları (Bekliyor / Yapılıyor / Sınırdı)
    open_kanban_cards: List[Dict[str, Any]] = []
    kanban_p = root / "KANBAN.md"
    if kanban_p.is_file():
        col = None
        for line in kanban_p.read_text(encoding="utf-8", errors="replace").splitlines():
            s = line.strip()
            if s.startswith("## "):
                col = s[3:].strip()
                continue
            if col in ("Bekliyor", "Yapılıyor", "Sınırdı") and s.startswith("### "):
                ids = PLAN_TASK_ID_RE.findall(s)
                files_in_title = {normalize_path(m) for m in re.findall(r"`([^`]+\.[a-z]{1,6})`", s)}
                open_kanban_cards.append({
                    "id": ids[0] if ids else s,
                    "column": col,
                    "title": s,
                    "tokens": tokenize(s),
                    "files": files_in_title,
                })

    # HANDOFF §3 açık satırlar
    open_handoff_rows: List[Dict[str, Any]] = []
    for line in handoff_text.splitlines():
        s = line.strip()
        if s.startswith("|") and ("⬜" in s or "⏭️" in s or "Bekliyor" in s or "Yapılıyor" in s):
            parts = [p.strip() for p in s.strip("|").split("|")]
            if parts and parts[0] not in ("ID", "Gereksinim ID", "---"):
                open_handoff_rows.append({
                    "id": parts[0],
                    "raw": s,
                    "tokens": tokenize(s),
                })

    return {
        "queued_plans": queued_plans,
        "open_kanban_cards": open_kanban_cards,
        "open_handoff_rows": open_handoff_rows,
        "done_history": done_hist,
    }


def _add_finding(
    findings: List[Dict[str, Any]],
    ftype: str,
    severity: str,
    target: str,
    message: str,
    recommendation: str,
    related_ref: str = "",
) -> None:
    findings.append({
        "type": ftype,
        "severity": severity,
        "target": target,
        "message": message,
        "recommendation": recommendation,
        "related_ref": related_ref,
    })


def analyze_plan_conflicts(root: Path | str, plan_path: Path | str) -> Dict[str, Any]:
    """Verilen planı canlı kod, tamamlanan işler ve kuyruktaki bekleyen planlarla kıyaslar."""
    root_p = Path(root).resolve()
    plan_p = Path(plan_path).resolve()
    if not plan_p.is_file():
        raise FileNotFoundError(f"Plan dosyası bulunamadı: {plan_p}")

    try:
        plan_rel = plan_p.relative_to(root_p).as_posix()
    except ValueError:
        plan_rel = plan_p.as_posix()

    fp = extract_plan_footprint(plan_p.read_text(encoding="utf-8", errors="replace"), plan_ref=plan_rel)
    live = scan_live_codebase(root_p)
    queue_data = _collect_queued_plans_and_backlog(root_p, exclude_plan=plan_p)
    queued_plans: List[PlanFootprint] = queue_data["queued_plans"]
    done_hist = queue_data["done_history"]

    findings: List[Dict[str, Any]] = []
    live_files: Dict[str, Dict[str, Any]] = live["files"]

    # 1. Canlı Kod Kıyaslaması: NEW / MODIFY hedefleri
    for action in ("NEW", "MODIFY"):
        for fpath in sorted(fp.file_actions[action]):
            if fpath not in live_files:
                continue
            live_meta = live_files[fpath]
            live_sigs: Set[str] = live_meta["signals"]
            plan_sigs: Set[str] = fp.richness_signals
            live_only = live_sigs - plan_sigs
            plan_only = plan_sigs - live_sigs

            if action == "NEW":
                if len(live_only) >= 2 or (len(live_sigs) >= 3 and len(plan_sigs) < len(live_sigs)):
                    _add_finding(
                        findings,
                        "SIMPLIFIED_SUBSET_REGRESSION",
                        "CRITICAL",
                        fpath,
                        f"`{fpath}` canlı kodda daha zengin ({sorted(live_sigs)}) halde mevcut; yeni plan `[NEW]` ile daha sade/korumasız ({sorted(plan_sigs)}) şekilde ezme riski taşıyor.",
                        f"`[NEW]` etiketini kaldırıp `[MODIFY]` yapın ve canlıdaki korumaları ({', '.join(sorted(live_only))}) planda koruyun.",
                        related_ref=fpath,
                    )
                elif plan_only or fp.db_tables:
                    _add_finding(
                        findings,
                        "ENRICHED_SUPERSET",
                        "WARNING",
                        fpath,
                        f"`{fpath}` canlı kodda zaten var; ancak yeni plan ek katman/özellik ({sorted(plan_only or fp.db_tables)}) ekleyerek zenginleştiriyor.",
                        f"Sıfırdan oluşturmak (`[NEW]`) yerine `[MODIFY] {fpath}` olarak mevcut kodu genişletin.",
                        related_ref=fpath,
                    )
                else:
                    _add_finding(
                        findings,
                        "ALREADY_DONE_EXACT",
                        "WARNING",
                        fpath,
                        f"`{fpath}` ve hedef yüzeyler canlı kodda zaten mevcut (birebir tekrar şüphesi).",
                        "Özellik zaten geliştirilmişse planı kapatın veya yalnızca fark varsa `[MODIFY]` kapsamını netleştirin.",
                        related_ref=fpath,
                    )
            else:
                # MODIFY durumunda sadeleştirme / ezme regresyonu sinyali var mı?
                if len(live_only) >= 3 and not plan_only and re.search(r"\b(?:sade|basit|yeniden yaz|rewrite|simple)\b", fp.title, re.IGNORECASE):
                    _add_finding(
                        findings,
                        "SIMPLIFIED_SUBSET_REGRESSION",
                        "CRITICAL",
                        fpath,
                        f"`{fpath}` üzerinde `[MODIFY]` işlemi canlıdaki zengin katmanları ({sorted(live_only)}) kaybetme riski taşıyor.",
                        f"Mevcut korumaları ({', '.join(sorted(live_only))}) silmediğinizi Gherkin senaryosuyla doğrulayın.",
                        related_ref=fpath,
                    )

    # Canlı Endpoint & Tablo & Tamamlanan İş Çakışması (Dosya adı farklı olsa bile)
    matched_files = fp.all_files & set(live_files.keys())
    if not matched_files:
        for ep in sorted(fp.endpoints):
            ep_any = _normalize_endpoint("ANY", ep.split(" ", 1)[1])
            matched_refs = live["endpoints"].get(ep) or live["endpoints"].get(ep_any)
            if matched_refs:
                _add_finding(
                    findings,
                    "ALREADY_DONE_EXACT",
                    "WARNING",
                    ep,
                    f"API uç noktası `{ep}` canlı kodda (`{matched_refs[0]}`) zaten tanımlı.",
                    f"Yeni plan mevcut endpoint'i genişletiyorsa `{matched_refs[0]}` dosyasını `[MODIFY]` olarak hedefleyin.",
                    related_ref=matched_refs[0],
                )

    for item in done_hist["done_items"]:
        sim = jaccard(fp.title_tokens, item["tokens"])
        if sim >= 0.65 and not findings:
            _add_finding(
                findings,
                "ALREADY_DONE_EXACT",
                "WARNING",
                fp.title,
                f"Plan başlığı/kapsamı tamamlanmış işle yüksek örtüşme gösteriyor (Jaccard={sim}): `{item['title'][:80]}`.",
                "Daha önce tamamlanan bu işin birebir tekrarı mı yoksa yeni faz zenginleştirmesi mi olduğunu netleştirin.",
                related_ref=item["source"],
            )

    # 2. Bekleyen Sıralı Planlarla Çakışma & Ezme (Queued Plan-vs-Plan Clobber)
    queued_new_files: Dict[str, str] = {}
    for qp in queued_plans:
        for f in qp.file_actions["NEW"]:
            queued_new_files.setdefault(f, qp.plan_ref)

        # DOUBLE_NEW_COLLISION
        for f in sorted(fp.file_actions["NEW"] & qp.file_actions["NEW"]):
            _add_finding(
                findings,
                "DOUBLE_NEW_COLLISION",
                "CRITICAL",
                f,
                f"Bekleyen `{qp.plan_ref}` planı da `{f}` dosyasını `[NEW]` olarak oluşturuyor; iki plan sırayla kodlanırken birbirini ezer.",
                f"İlk planı baz alıp ikinci planda `[MODIFY] {f}` kullanın veya iki planı birleştirin.",
                related_ref=qp.plan_ref,
            )

        # MODIFY_DELETE_CLOBBER
        clobber_del = (fp.file_actions["DELETE"] & (qp.file_actions["NEW"] | qp.file_actions["MODIFY"])) | (
            (fp.file_actions["NEW"] | fp.file_actions["MODIFY"]) & qp.file_actions["DELETE"]
        )
        for f in sorted(clobber_del):
            _add_finding(
                findings,
                "MODIFY_DELETE_CLOBBER",
                "CRITICAL",
                f,
                f"`{f}` dosyasında `[MODIFY/NEW]` ile `[DELETE]` çelişiyor (karşı plan: `{qp.plan_ref}`).",
                "Silme ve değiştirme kararını tek planda uzlaştırın.",
                related_ref=qp.plan_ref,
            )

        # SHARED_SURFACE_OVERWRITE (Aynı dosya MODIFY, aynı Endpoint, aynı DB Tablo, aynı Rota)
        shared_mod_files = (fp.file_actions["MODIFY"] & qp.file_actions["MODIFY"]) - clobber_del
        for f in sorted(shared_mod_files):
            _add_finding(
                findings,
                "SHARED_SURFACE_OVERWRITE",
                "WARNING",
                f,
                f"Bekleyen `{qp.plan_ref}` planı da `{f}` dosyasını `[MODIFY]` ediyor; sıralı geliştirme sırasında kod ezme riski var.",
                f"İkinci plan geliştirilirken `{qp.plan_ref}` içindeki değişiklikler korunarak birleştirilmelidir.",
                related_ref=qp.plan_ref,
            )

        for ep in sorted(fp.endpoints & qp.endpoints):
            _add_finding(
                findings,
                "SHARED_SURFACE_OVERWRITE",
                "WARNING",
                ep,
                f"Bekleyen `{qp.plan_ref}` planı da `{ep}` endpoint'ini değiştiriyor (sözleşme ezme riski).",
                f"`{ep}` request/response DTO sözleşmesini iki plan arasında uzlaştırın.",
                related_ref=qp.plan_ref,
            )

        for tbl in sorted(fp.db_tables & qp.db_tables):
            _add_finding(
                findings,
                "SHARED_SURFACE_OVERWRITE",
                "WARNING",
                tbl,
                f"Bekleyen `{qp.plan_ref}` planı da `{tbl}` DB tablosuna migration planlıyor.",
                "Migration sırasını ve kolon şemasını çakışmayacak şekilde hizalayın.",
                related_ref=qp.plan_ref,
            )

        # Aynı görev ID çakışması
        shared_ids = set(fp.task_ids) & set(qp.task_ids)
        for tid in sorted(shared_ids):
            _add_finding(
                findings,
                "BACKLOG_SEMANTIC_DUPLICATE",
                "WARNING",
                tid,
                f"Görev ID `{tid}` bekleyen `{qp.plan_ref}` planında da kullanılıyor.",
                "Her plan için benzersiz `[DOM]-[TIP]-[NO]` ID atayın.",
                related_ref=qp.plan_ref,
            )

    # SEQUENTIAL_ORDER_DEPENDENCY: Yeni plan [MODIFY] X diyor ama X canlıda yok, bekleyen Plan A'da [NEW] X
    for f in sorted(fp.file_actions["MODIFY"]):
        if f not in live_files and f in queued_new_files:
            dep_plan = queued_new_files[f]
            _add_finding(
                findings,
                "SEQUENTIAL_ORDER_DEPENDENCY",
                "WARNING",
                f,
                f"`{f}` henüz canlı kodda yok; ancak bekleyen `{dep_plan}` planında `[NEW]` olarak oluşturulacak. Bu plan `{dep_plan}` tamamlanmadan başlatılamaz.",
                f"Geliştirme sırası kilidi: Önce `{dep_plan}`, ardından bu plan çalıştırılmalıdır.",
                related_ref=dep_plan,
            )

    # Açık KANBAN kartlarıyla semantik tekrar kontrolü
    for card in queue_data["open_kanban_cards"]:
        if card["id"] in fp.task_ids:
            continue
        sim = jaccard(fp.title_tokens, card["tokens"])
        shared_f = fp.all_files & card["files"]
        if sim >= 0.65 or shared_f:
            _add_finding(
                findings,
                "BACKLOG_SEMANTIC_DUPLICATE",
                "WARNING",
                card["id"],
                f"KANBAN.md `{card['column']}` sütunundaki `{card['id']}` kartı ile yüksek çakışma (Jaccard={sim}, dosya={sorted(shared_f)}).",
                "Mükerrer kart açmak yerine mevcut KANBAN kartını güncelleyin veya kapsamları ayırın.",
                related_ref="KANBAN.md",
            )

    priority_order = [
        "SIMPLIFIED_SUBSET_REGRESSION",
        "DOUBLE_NEW_COLLISION",
        "MODIFY_DELETE_CLOBBER",
        "ENRICHED_SUPERSET",
        "ALREADY_DONE_EXACT",
        "SHARED_SURFACE_OVERWRITE",
        "SEQUENTIAL_ORDER_DEPENDENCY",
        "BACKLOG_SEMANTIC_DUPLICATE",
    ]
    found_types = {f["type"] for f in findings}
    overall = next((t for t in priority_order if t in found_types), "NEW_CLEAN")
    critical_count = sum(1 for f in findings if f["severity"] == "CRITICAL")
    warning_count = sum(1 for f in findings if f["severity"] == "WARNING")

    return {
        "plan_ref": plan_rel,
        "overall_classification": overall,
        "critical_count": critical_count,
        "warning_count": warning_count,
        "footprint": fp.to_summary(),
        "findings": findings,
    }


def analyze_queue(root: Path | str) -> Dict[str, Any]:
    """Kuyruktaki tüm bekleyen planlar ve açık KANBAN kartları arasındaki çakışmaları tarar."""
    root_p = Path(root).resolve()
    queue_data = _collect_queued_plans_and_backlog(root_p)
    queued_plans: List[PlanFootprint] = queue_data["queued_plans"]
    queue_findings: List[Dict[str, Any]] = []

    for i in range(len(queued_plans)):
        for j in range(i + 1, len(queued_plans)):
            p1 = queued_plans[i]
            p2 = queued_plans[j]
            for f in sorted(p1.file_actions["NEW"] & p2.file_actions["NEW"]):
                _add_finding(
                    queue_findings,
                    "DOUBLE_NEW_COLLISION",
                    "CRITICAL",
                    f,
                    f"`{p1.plan_ref}` ve `{p2.plan_ref}` aynı `{f}` dosyasını `[NEW]` olarak tanımlıyor.",
                    "Birini `[MODIFY]` yapın veya iki planı birleştirin.",
                    related_ref=f"{p1.plan_ref} <-> {p2.plan_ref}",
                )
            for f in sorted((p1.file_actions["MODIFY"] & p2.file_actions["MODIFY"])):
                _add_finding(
                    queue_findings,
                    "SHARED_SURFACE_OVERWRITE",
                    "WARNING",
                    f,
                    f"`{p1.plan_ref}` ve `{p2.plan_ref}` aynı `{f}` dosyasını `[MODIFY]` ediyor.",
                    "Sıralı geliştirme sırasında ikinci plan ilkini ezmemeli.",
                    related_ref=f"{p1.plan_ref} <-> {p2.plan_ref}",
                )
            for ep in sorted(p1.endpoints & p2.endpoints):
                _add_finding(
                    queue_findings,
                    "SHARED_SURFACE_OVERWRITE",
                    "WARNING",
                    ep,
                    f"`{p1.plan_ref}` ve `{p2.plan_ref}` aynı `{ep}` endpoint'ine dokunuyor.",
                    "Endpoint sözleşmesini hizalayın.",
                    related_ref=f"{p1.plan_ref} <-> {p2.plan_ref}",
                )

    return {
        "checked_plans": [p.plan_ref for p in queued_plans],
        "open_kanban_cards": len(queue_data["open_kanban_cards"]),
        "critical_count": sum(1 for f in queue_findings if f["severity"] == "CRITICAL"),
        "warning_count": sum(1 for f in queue_findings if f["severity"] == "WARNING"),
        "findings": queue_findings,
    }


def analyze_kanban_duplicates(root: Path | str) -> List[Dict[str, Any]]:
    """KANBAN.md açık kartları arasında aynı dosya/yüzey veya semantik tekrarları bulur."""
    root_p = Path(root).resolve()
    queue_data = _collect_queued_plans_and_backlog(root_p)
    cards = queue_data["open_kanban_cards"]
    done_items = queue_data["done_history"]["done_items"]
    dups: List[Dict[str, Any]] = []

    for i in range(len(cards)):
        for j in range(i + 1, len(cards)):
            c1, c2 = cards[i], cards[j]
            sim = jaccard(c1["tokens"], c2["tokens"])
            shared_f = c1["files"] & c2["files"]
            if sim >= 0.65 or shared_f:
                dups.append({
                    "card_a": c1["id"],
                    "card_b": c2["id"],
                    "similarity": sim,
                    "shared_files": sorted(shared_f),
                    "message": (
                        f"KANBAN açık kartları `{c1['id']}` ve `{c2['id']}` aynı hedefi/yüzeyi paylaşıyor "
                        f"(Jaccard={sim}, ortak dosya={sorted(shared_f)})."
                    ),
                })

    for c in cards:
        for d in done_items:
            sim = jaccard(c["tokens"], d["tokens"])
            if sim >= 0.80:
                dups.append({
                    "card_a": c["id"],
                    "card_b": d["source"],
                    "similarity": sim,
                    "shared_files": [],
                    "message": (
                        f"Açık KANBAN kartı `{c['id']}` tamamlanmış `{d['title'][:60]}` maddesiyle "
                        f"birebir benzer (Jaccard={sim})."
                    ),
                })
    return dups


def format_markdown_audit_section(report: Dict[str, Any]) -> str:
    """Arşivlenen planın içine mühürlenecek FAA AC 121-24C çakışma tablosu üretir."""
    findings = report.get("findings", [])
    lines = [
        "<!-- PRE-SEAL-CONFLICT-AUDIT:BEGIN -->",
        "## ⚠️ Ön-Mühürleme Çakışma, Tekrar ve Sıralı Plan Ezme Analizi (Pre-Seal Conflict Audit)",
        f"- **Genel Sınıflandırma:** `{report['overall_classification']}` "
        f"(Kritik: `{report['critical_count']}` · Uyarı: `{report['warning_count']}`)",
        "",
    ]
    if not findings:
        lines.append("✅ **Temiz (NEW_CLEAN):** Canlı kod ve bekleyen planlarla çakışma tespit edilmedi.")
    else:
        lines.extend([
            "| Seviye | Sınıflandırma | Hedef | Tespit & İlgili Kaynak | Önerilen Eylem |",
            "|---|---|---|---|---|",
        ])
        for f in findings:
            badge = "🔴 CRITICAL" if f["severity"] == "CRITICAL" else "🟡 WARNING"
            msg = f["message"].replace("|", "/")
            rec = f["recommendation"].replace("|", "/")
            lines.append(f"| {badge} | `{f['type']}` | `{f['target']}` | {msg} | {rec} |")
    lines.append("<!-- PRE-SEAL-CONFLICT-AUDIT:END -->")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Plan Ön-Mühürleme ve Kuyruk Çakışma/Ezme Kalkanı")
    parser.add_argument("--root", default=".", help="Proje kök dizini")
    parser.add_argument("--plan", default="", help="Denetlenecek tekil plan dosyası")
    parser.add_argument("--check-queue", action="store_true", help="Bekleyen tüm planları ve KANBAN kartlarını çapraz tara")
    parser.add_argument("--json", action="store_true", help="JSON çıktısı ver")
    parser.add_argument("--strict", action="store_true", help="Uyarıları da exit 1 say")
    args = parser.parse_args()

    root_p = Path(args.root).resolve()
    if args.plan:
        try:
            report = analyze_plan_conflicts(root_p, args.plan)
        except FileNotFoundError as exc:
            print(f"[ERR] {exc}", file=sys.stderr)
            return 2
        if args.json:
            print(json.dumps(report, ensure_ascii=False, indent=2))
        else:
            print(f"Plan Çakışma Analizi ({report['plan_ref']}): {report['overall_classification']}")
            print(f"  Kritik: {report['critical_count']} · Uyarı: {report['warning_count']}")
            for f in report["findings"]:
                print(f"  [{f['severity']}] [{f['type']}] {f['target']} -> {f['message']}")
        has_fail = report["critical_count"] > 0 or (args.strict and report["warning_count"] > 0)
        return 1 if has_fail else 0

    if args.check_queue:
        q_report = analyze_queue(root_p)
        k_dups = analyze_kanban_duplicates(root_p)
        payload = {**q_report, "kanban_duplicates": k_dups}
        if args.json:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            print(f"Kuyruk Taraması ({len(q_report['checked_plans'])} bekleyen plan, {q_report['open_kanban_cards']} açık kart):")
            for f in q_report["findings"]:
                print(f"  [{f['severity']}] [{f['type']}] {f['target']} -> {f['message']}")
            for d in k_dups:
                print(f"  [WARNING] [BACKLOG_SEMANTIC_DUPLICATE] {d['message']}")
            if not q_report["findings"] and not k_dups:
                print("  [OK] Sıralı plan ve backlog kuyruğunda çakışma yok.")
        has_fail = q_report["critical_count"] > 0 or (args.strict and (q_report["warning_count"] > 0 or bool(k_dups)))
        return 1 if has_fail else 0

    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
