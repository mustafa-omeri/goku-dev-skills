# -*- coding: utf-8 -*-
"""Data Intelligence & Governance Analyzer (`data.py`).

Extracts Prisma, JPA, and SQL schema entities/columns, computes v1 orphan fields,
and audits FK index alignment, risky migration DDLs, and PII/audit governance signals.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from ..model import CoverageReport, Edge, EvidenceRef, Fact, Node, ProjectProfile, iter_repo_files
from .base import AnalyzerContext, AnalyzerResult

PRISMA_MODEL_RE = re.compile(r"^\s*model\s+(\w+)\s*\{([^}]*)\}", re.MULTILINE | re.DOTALL)
SKIP_FIELDS = {
    "id",
    "createdAt",
    "updatedAt",
    "deletedAt",
    "created_at",
    "updated_at",
    "deleted_at",
    "password",
    "passwordHash",
    "password_hash",
    "serialVersionUID",
}
JPA_FIELD_RE = re.compile(
    r"^[ \t]*private[ \t]+(?:final[ \t]+)?([A-Za-z0-9_<>, \t?]+)[ \t]+([a-z][A-Za-z0-9_]*)[ \t]*(?:=|;)",
    re.MULTILINE,
)
SQL_CREATE_TABLE_RE = re.compile(
    r"CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?(?:[A-Za-z0-9_]+\.)?[\"`]?(\w+)[\"`]?\s*\(([\s\S]*?)\)\s*;",
    re.IGNORECASE,
)
SQL_ADD_COL_RE = re.compile(
    r"ALTER\s+TABLE\s+(?:IF\s+EXISTS\s+)?(?:[A-Za-z0-9_]+\.)?[\"`]?(\w+)[\"`]?\s+ADD\s+COLUMN\s+(?:IF\s+NOT\s+EXISTS\s+)?[\"`]?(\w+)[\"`]?([^\n;]*)",
    re.IGNORECASE,
)
SQL_DROP_RE = re.compile(
    r"ALTER\s+TABLE\s+(?:IF\s+EXISTS\s+)?[\"`]?(\w+)[\"`]?\s+DROP\s+COLUMN\s+(?!IF\s+EXISTS)[\"`]?(\w+)[\"`]?"
    r"|DROP\s+TABLE\s+(?!IF\s+EXISTS)[\"`]?(\w+)[\"`]?",
    re.IGNORECASE,
)
SQL_CREATE_INDEX_RE = re.compile(
    r"CREATE\s+(?:UNIQUE\s+)?INDEX\s+(?:IF\s+NOT\s+EXISTS\s+)?[\"`]?\w+[\"`]?\s+ON\s+(?:[A-Za-z0-9_]+\.)?[\"`]?(\w+)[\"`]?\s*\(([^)]+)\)",
    re.IGNORECASE,
)
PII_COL_RE = re.compile(
    r"\b(?:national_?id|ssn|passport_?no|tax_?id|iban|birth_?date|phone_?number)\b",
    re.IGNORECASE,
)
AUDIT_RETENTION_RE = re.compile(
    r"\b(?:deleted_?at|retention_?until|anonymized_?at|audit_?log|created_?by)\b",
    re.IGNORECASE,
)


def _camel_to_snake(name: str) -> str:
    return re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", name).lower()


def _snake_to_camel(name: str) -> str:
    parts = name.split("_")
    return parts[0] + "".join(p.capitalize() for p in parts[1:])


class DataGovernanceAnalyzer:
    name = "data"
    version = "2.0.0"

    def applies(self, profile: ProjectProfile) -> tuple[bool, str]:
        if profile.schema_sources:
            kinds = ", ".join(sorted({s.kind for s in profile.schema_sources}))
            return True, f"Detected schema source(s): {kinds}"
        return False, "Stateless / DB-less project (no schema or migration files detected)"

    def analyze(self, ctx: AnalyzerContext) -> AnalyzerResult:
        applicable, reason = self.applies(ctx.profile)
        if not applicable:
            ctx.shared_state["data"] = {"v1_orphan_fields": [], "scoped_entities": set()}
            return AnalyzerResult(
                analyzer=self.name,
                version=self.version,
                applicable=False,
                applicability_reason=reason,
            )

        nodes: list[Node] = []
        edges: list[Edge] = []
        facts: list[Fact] = []
        scanned = 0
        declared_fields: list[tuple[str, str, str]] = []
        scoped_entities: set[str] = set()
        indexed_cols_by_table: dict[str, set[str]] = {}
        fk_cols: list[tuple[str, str, str, int, str]] = []

        # Collect indexed columns across all SQL files first
        for label, r in ctx.profile.all_active_roots:
            for sf in iter_repo_files(r, {".sql"}):
                txt = sf.read_text(encoding="utf-8", errors="replace")
                for im in SQL_CREATE_INDEX_RE.finditer(txt):
                    tname = im.group(1).lower()
                    cols = [c.strip().strip('"`').split()[0].lower() for c in im.group(2).split(",")]
                    if cols:
                        indexed_cols_by_table.setdefault(tname, set()).add(cols[0])

        for label, r in ctx.profile.all_active_roots:
            # 1. Prisma models
            for pf in iter_repo_files(r, {".prisma"}):
                scanned += 1
                rel = pf.relative_to(r).as_posix()
                txt = pf.read_text(encoding="utf-8", errors="replace")
                for m in PRISMA_MODEL_RE.finditer(txt):
                    entity = m.group(1)
                    body = m.group(2)
                    mline = txt[: m.start()].count("\n") + 1
                    nodes.append(Node(id=f"Entity:{entity}", kind="Entity", name=entity, file=rel, line=mline, root_label=label))
                    if re.search(r"\b(?:tenantId|tenant_id|organizationId|companyId|workspaceId)\b", body):
                        scoped_entities.add(entity)
                    for line in body.splitlines():
                        stripped = line.strip()
                        if not stripped or stripped.startswith("//") or stripped.startswith("@@"):
                            continue
                        tokens = stripped.split()
                        if len(tokens) >= 2:
                            fname = tokens[0]
                            if fname not in SKIP_FIELDS and not fname.startswith("@"):
                                declared_fields.append((entity, fname, rel))

            # 2. JPA entities
            for jf in iter_repo_files(r, {".java", ".kt"}):
                txt = jf.read_text(encoding="utf-8", errors="replace")
                if "@Entity" not in txt:
                    continue
                scanned += 1
                rel = jf.relative_to(r).as_posix()
                cls_m = re.search(r"\bclass\s+(\w+)", txt)
                entity = cls_m.group(1) if cls_m else jf.stem
                nodes.append(Node(id=f"Entity:{entity}", kind="Entity", name=entity, file=rel, line=1, root_label=label))
                for fm in JPA_FIELD_RE.finditer(txt):
                    fname = fm.group(2)
                    if fname in {"tenantId", "organizationId", "companyId", "workspaceId"}:
                        scoped_entities.add(entity)
                    if fname not in SKIP_FIELDS:
                        declared_fields.append((entity, fname, rel))

            # 3. SQL migrations
            for sf in iter_repo_files(r, {".sql"}):
                scanned += 1
                rel = sf.relative_to(r).as_posix()
                txt = sf.read_text(encoding="utf-8", errors="replace")
                lines = txt.splitlines()

                for cm in SQL_CREATE_TABLE_RE.finditer(txt):
                    tname = cm.group(1)
                    tbody = cm.group(2)
                    tline = txt[: cm.start()].count("\n") + 1
                    nodes.append(Node(id=f"Table:{tname}", kind="Table", name=tname, file=rel, line=tline, root_label=label))
                    for bline_offset, raw_bline in enumerate(tbody.splitlines()):
                        bline = raw_bline.strip().rstrip(",")
                        if not bline or bline.startswith("--"):
                            continue
                        if re.search(r"\bREFERENCES\b", bline, re.IGNORECASE):
                            col_m = re.match(r"^[\"`]?([A-Za-z_][A-Za-z0-9_]*)[\"`]?\s+", bline)
                            if col_m and not re.match(
                                r"^(?:CONSTRAINT|FOREIGN|PRIMARY|UNIQUE|CHECK|INDEX|KEY)$",
                                col_m.group(1),
                                re.IGNORECASE,
                            ):
                                fk_cols.append((tname, col_m.group(1), rel, tline + bline_offset, raw_bline.strip()[:160]))
                        fk_table_m = re.search(r"FOREIGN\s+KEY\s*\(\s*[\"`]?(\w+)[\"`]?\s*\)", bline, re.IGNORECASE)
                        if fk_table_m:
                            fk_cols.append((tname, fk_table_m.group(1), rel, tline + bline_offset, raw_bline.strip()[:160]))

                    if PII_COL_RE.search(tbody) and not AUDIT_RETENTION_RE.search(tbody):
                        pii_m = PII_COL_RE.search(tbody)
                        pii_col = pii_m.group(0) if pii_m else "pii"
                        facts.append(
                            Fact.create(
                                fact_id=f"DATA-PII-{len(facts)+1:03d}",
                                code="PII_GOVERNANCE_SIGNAL",
                                category="SECURITY",
                                fact_type="behavioral",
                                severity="MEDIUM",
                                summary=(
                                    f"Table `{tname}` (`{rel}:{tline}`) stores sensitive PII column `{pii_col}` "
                                    f"without visible retention/soft-delete/audit columns."
                                ),
                                location=f"{rel}:{tline}",
                                evidence=[
                                    EvidenceRef(
                                        kind="code",
                                        level="L1",
                                        derivation="syntax",
                                        ref=f"{rel}:{tline}",
                                        line=tline,
                                        excerpt=lines[tline - 1].strip()[:160] if tline - 1 < len(lines) else tname,
                                    )
                                ],
                            )
                        )

                for am in SQL_ADD_COL_RE.finditer(txt):
                    tname, cname, tail = am.group(1), am.group(2), am.group(3) or ""
                    aline = txt[: am.start()].count("\n") + 1
                    if cname not in SKIP_FIELDS:
                        declared_fields.append((tname, cname, rel))
                    if re.search(r"\bNOT\s+NULL\b", tail, re.IGNORECASE) and not re.search(
                        r"\bDEFAULT\b", tail, re.IGNORECASE
                    ):
                        facts.append(
                            Fact.create(
                                fact_id=f"DATA-MIG-{len(facts)+1:03d}",
                                code="RISKY_MIGRATION_DDL",
                                category="ARCHITECTURE",
                                fact_type="structural",
                                severity="HIGH",
                                summary=f"Migration `{rel}:{aline}` adds `NOT NULL` column `{tname}.{cname}` without a `DEFAULT`, risking deployment failure on populated tables.",
                                location=f"{rel}:{aline}",
                                evidence=[
                                    EvidenceRef(
                                        kind="code",
                                        level="L1",
                                        derivation="syntax",
                                        ref=f"{rel}:{aline}",
                                        line=aline,
                                        excerpt=lines[aline - 1].strip()[:160] if aline - 1 < len(lines) else "",
                                    )
                                ],
                            )
                        )

                for dm in SQL_DROP_RE.finditer(txt):
                    dline = txt[: dm.start()].count("\n") + 1
                    facts.append(
                        Fact.create(
                            fact_id=f"DATA-MIG-{len(facts)+1:03d}",
                            code="RISKY_MIGRATION_DDL",
                            category="ARCHITECTURE",
                            fact_type="structural",
                            severity="HIGH",
                            summary=f"Destructive migration statement (`DROP`) in `{rel}:{dline}` causes irreversible data loss or zero-downtime rollback failure.",
                            location=f"{rel}:{dline}",
                            evidence=[
                                EvidenceRef(
                                    kind="code",
                                    level="L1",
                                    derivation="syntax",
                                    ref=f"{rel}:{dline}",
                                    line=dline,
                                    excerpt=lines[dline - 1].strip()[:160] if dline - 1 < len(lines) else "",
                                )
                            ],
                        )
                    )

        # Missing FK index check
        for tname, fk_col, rel, fline, excerpt in fk_cols:
            if fk_col.lower() not in indexed_cols_by_table.get(tname.lower(), set()):
                facts.append(
                    Fact.create(
                        fact_id=f"DATA-IDX-{len(facts)+1:03d}",
                        code="MISSING_FK_INDEX",
                        category="PERFORMANCE",
                        fact_type="structural",
                        severity="MEDIUM",
                        summary=f"Foreign key column `{tname}.{fk_col}` (`{rel}:{fline}`) has no matching index declaration in SQL migrations.",
                        location=f"{rel}:{fline}",
                        evidence=[
                            EvidenceRef(
                                kind="code",
                                level="L1",
                                derivation="syntax",
                                ref=f"{rel}:{fline}",
                                line=fline,
                                excerpt=excerpt,
                            )
                        ],
                        attrs={"table": tname, "column": fk_col},
                    )
                )

        # Compute v1 orphan_fields against frontend UI identifiers
        fe_state = ctx.shared_state.get("frontend", {})
        ui_identifiers: set[str] = set(fe_state.get("ui_identifiers", set()))
        if not ui_identifiers:
            ident_re = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
            for fp in iter_repo_files(ctx.profile.root, {".tsx", ".jsx", ".vue", ".svelte", ".html", ".ts", ".js"}):
                ui_identifiers.update(ident_re.findall(fp.read_text(encoding="utf-8", errors="replace")))

        v1_orphans: list[dict[str, str]] = []
        for entity, field_name, source in declared_fields:
            snake = _camel_to_snake(field_name)
            camel = _snake_to_camel(field_name)
            if field_name not in ui_identifiers and snake not in ui_identifiers and camel not in ui_identifiers:
                v1_orphans.append(
                    {
                        "entity": entity,
                        "field": field_name,
                        "source": source,
                        "confidence": "candidate",
                    }
                )

        ctx.shared_state["data"] = {
            "v1_orphan_fields": v1_orphans,
            "scoped_entities": scoped_entities,
        }

        return AnalyzerResult(
            analyzer=self.name,
            version=self.version,
            applicable=True,
            applicability_reason=reason,
            nodes=nodes,
            edges=edges,
            facts=facts,
            coverage=CoverageReport(scanned_files=scanned),
        )
