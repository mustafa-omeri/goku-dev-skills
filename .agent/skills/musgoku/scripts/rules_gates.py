#!/usr/bin/env python3
"""Kural sinifi ve kapı denetleyicisi — "zorunlu" ile "olculebilir" ayrimi.

Neden var?
----------
Bir kural dosyasi "zorunlu", "asla", "istisnasiz" diyebilir ama **calistirilabilir
kapisi olmayabilir.** Ajan o kuralin kendi sozune dayanip "uyguladim" diyor,
kimse olcemiyor. Bu, `t(key, 'Turkce')` sessiz dil sizintisinin **kural katmanindaki**
hali: ayni hata, farkli katman.

Bu script kural setini uc sinifa boler ve sinifi **dosyanin ustunde** bildirir:

    OLCULEBILIR  kapisi var  -> script + exit tablosu   -> `kapi:` altinda yazilir
    TUTUM        kapisi yok  -> ajan beyani            -> KB'ye yazilir
    SUREC        kapisi yok  -> skill akisi            -> `kapi:` yazilmaz

Kontroller
----------
E1 sinif bildirilmemis        her kural `sinif:` bildirmeli
E2 gecersiz sinif            sadece uc degerden biri
E3 kapisiz olculebilir       OLCULEBILIR kuralda en az bir `kapi` olmali
E4 olmayan script yolu        kapi komutundaki dosya yolu cozumlenmeli
E5 sinif/capi celiskisi      TUTUM veya SUREC kuralda `kapi` yazilamaz
E6 bos kapi girdisi          `kapi` girisinde `yigin`/`komut` bos olamaz
E7 AGENTS.md tablosu bayat   uretilen tablo kaynakla ayni mi (drift)
E8 is akisi tablosu bayat    development-workflow.md tablosu bayat mi
W1 kapisiz tutum kurali      TUTUM kural govdesinde script yolu gostermeli degil

E1-E8 hata (exit 1) · W1 uyari (exit 0) · exit 2 = arac hatasi
`--strict` ile uyarilar da hata sayilir.

Kullanim
--------
    python .agent/skills/musgoku/scripts/rules_gates.py
    python .agent/skills/musgoku/scripts/rules_gates.py --json
    python .agent/skills/musgoku/scripts/rules_gates.py --emit-table

Ortam
-----
AGENTS_PROJECT_ROOT   proje kokunu elle verir (yoksa script konumundan aranir)
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

CLASSES = ("OLCULEBILIR", "TUTUM", "SUREC")

BEGIN_MARK = "<!-- GATE-TABLE:BEGIN -->"
END_MARK = "<!-- GATE-TABLE:END -->"

# Komut icinde geçen, depo-relative olmasi gereken dosya yollari. Yalnizca
# taninmis dosya uzantili belirtecler denetlenir; `npx tsc --noEmit` gibi
# kabuk komutlarinin yolu cozumlenmez.
PATH_RE = re.compile(r"[A-Za-z0-9_./\\-]+\.(?:py|ps1|md|json|ts|tsx|js|cjs|sh|ya?ml)\b")

TABLE_HEADER = ("| Yığın | Zorunlu komut | Ayrıntı |\n|---|---|---|")


class GateError(Exception):
    """Arac hatasi: girdi okunamadi veya yorumlanamadi."""


@dataclass
class Gate:
    yigin: str = ""
    komut: str = ""

    @property
    def valid(self) -> bool:
        return bool(self.yigin.strip()) and bool(self.komut.strip())


@dataclass
class Rule:
    path: Path
    stem: str
    name: str = ""
    description: str = ""
    sinif: str = ""
    gates: list = field(default_factory=list)
    body: str = ""


# --- front matter ---------------------------------------------------------------

def _unquote(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        return value[1:-1]
    return value


def _split_kv(line: str):
    if ":" not in line:
        return None, None
    key, _, value = line.partition(":")
    return key.strip(), _unquote(value)


def parse_front_matter(path: Path) -> Rule:
    """Dosyanin YAML front matter blokunu cozer. Mini parser, bagimlilik yok."""
    raw = path.read_text(encoding="utf-8")
    if raw.startswith("\ufeff"):
        raw = raw[1:]
    lines = raw.split("\n")

    if not lines or lines[0].strip() != "---":
        raise GateError(f"{path.name}: front matter yok (ilk satir '---' olmali)")

    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end = i
            break
    if end is None:
        raise GateError(f"{path.name}: front matter kapatilmamis")

    scalars = {}
    gates = []
    current = None
    in_kapi = False

    for line in lines[1:end]:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        indented = line[:1] in (" ", "\t")

        if not indented:
            key, value = _split_kv(stripped)
            if key is None:
                raise GateError(f"{path.name}: front matter satiri bozuk -> {stripped!r}")
            in_kapi = key == "kapi"
            if not in_kapi:
                scalars[key] = value
                current = None
            continue

        if not in_kapi:
            # `kapi:` anahtarindan sonra gelen girisler kapidir; diger
            # anahtarlarin alt girisleri yok sayilir.
            continue

        if stripped.startswith("- "):
            current = Gate()
            gates.append(current)
            key, value = _split_kv(stripped[2:].strip())
            if key is not None and key in ("yigin", "komut"):
                setattr(current, key, value)
            continue

        key, value = _split_kv(stripped)
        if current is not None and key in ("yigin", "komut"):
            setattr(current, key, value)

    return Rule(
        path=path,
        stem=path.stem,
        name=scalars.get("name", ""),
        description=scalars.get("description", ""),
        sinif=scalars.get("sinif", ""),
        gates=gates,
        body="\n".join(lines[end + 1:]),
    )


def collect_rules(rules_dir: Path):
    """Kural dosyalarini ada gore sirali dondurur (deterministik cikti icin)."""
    return [parse_front_matter(p) for p in sorted(rules_dir.glob("*.md"))]


# --- dogrulama ------------------------------------------------------------------

def _resolve_paths(command: str, project_root: Path):
    """Komut icindeki depo-relative dosya yollarini dondurur."""
    return [m.group(0).replace("\\", "/") for m in PATH_RE.finditer(command)]


def validate(rules_dir: Path, agents_path: Path, workflow_path: Path,
             project_root: Path, check_tables: bool = True):
    """(hatalar, uyarilar) dondurur. hata/uyari: (kod, dosya, mesaj)."""
    errors = []
    warnings = []

    rules = collect_rules(rules_dir)

    for rule in rules:
        if not rule.sinif:
            errors.append(("E1", rule.stem,
                           "sinif bildirilmemis (OLCULEBILIR | TUTUM | SUREC)"))
            continue

        if rule.sinif not in CLASSES:
            errors.append(("E2", rule.stem,
                           f"gecersiz sinif: {rule.sinif!r} (gecerli: {', '.join(CLASSES)})"))
            continue

        if rule.sinif == "OLCULEBILIR":
            if not rule.gates:
                errors.append(("E3", rule.stem,
                               "sinif OLCULEBILIR ama kapi tanimlanmamis"))
            for gate in rule.gates:
                if not gate.valid:
                    errors.append(("E6", rule.stem,
                                   "bos kapi girdisi (yigin ve komut dolu olmali)"))
                    continue
                for rel in _resolve_paths(gate.komut, project_root):
                    if not (project_root / rel).exists():
                        errors.append(("E4", rule.stem,
                                       f"kapi komutundaki yol cozumlenemiyor: {rel}"))
        else:
            if rule.gates:
                errors.append(("E5", rule.stem,
                               f"sinif {rule.sinif} ama kapi tanimlanmis; "
                               "kapi yalnizca OLCULEBILIR kuralda olabilir"))
            if rule.sinif == "TUTUM" and re.search(r"\.agent/skills/\S+/scripts/\S+",
                                                   rule.body):
                warnings.append(("W1", rule.stem,
                                 "sinif TUTUM ama govdede script yolu var; "
                                 "kapisi varsa sinif OLCULEBILIR olmali"))

    if check_tables:
        for path, link_prefix, code in (
            (agents_path, "rules/", "E7"),
            (workflow_path, "./", "E8"),
        ):
            if not path.exists():
                errors.append((code, path.name, "tablo kaynagi bulunamadi"))
                continue
            expected = render_table(rules, link_prefix)
            found = extract_table(path.read_text(encoding="utf-8"))
            if found is None:
                errors.append((code, path.name,
                               f"uretilmis tablo isaretleri yok ({BEGIN_MARK} / {END_MARK})"))
            elif found != expected:
                errors.append((code, path.name,
                               "uretilmis tablo bayat; yenilemek icin: "
                               "python .agent/skills/musgoku/scripts/rules_gates.py --emit-table"))

    return errors, warnings


def extract_table(text: str):
    """Isaretler arasindaki tabloyu dondurur ( satir sonu normalizasyonlu)."""
    if BEGIN_MARK not in text or END_MARK not in text:
        return None
    start = text.index(BEGIN_MARK) + len(BEGIN_MARK)
    end = text.index(END_MARK)
    return text[start:end].replace("\r\n", "\n").strip("\n").strip()


def render_table(rules, link_prefix: str) -> str:
    """Kaynak kurallardan AGENTS.md / is akisi tablosunu uretir."""
    rows = []
    for rule in sorted(rules, key=lambda r: r.stem):
        if rule.sinif != "OLCULEBILIR":
            continue
        for gate in rule.gates:
            if not gate.valid:
                continue
            rows.append(f"| {gate.yigin} | `{gate.komut}` | "
                        f"[`{rule.stem}.md`]({link_prefix}{rule.stem}.md) |")
    return "\n".join([TABLE_HEADER] + rows)


def render_attitude_list(rules) -> str:
    """Kapisiz kurallari sinifina gore listeler."""
    rows = []
    for rule in sorted(rules, key=lambda r: (r.sinif, r.stem)):
        if rule.sinif in ("OLCULEBILIR", ""):
            continue
        rows.append(f"| `{rule.stem}.md` | {rule.sinif} |")
    return "\n".join(["| Kural | Sınıf |", "|---|---|"] + rows)


# --- giris noktasi ---------------------------------------------------------------

def find_project_root() -> Path:
    env = os.environ.get("AGENTS_PROJECT_ROOT")
    if env:
        return Path(env).resolve()
    # .agent/skills/<skill>/scripts/<file> -> proje koku 4 seviye yukarida
    return Path(__file__).resolve().parents[4]


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Kural sinifi ve kapi denetleyicisi")
    parser.add_argument("--json", action="store_true", help="makine okunur cikti")
    parser.add_argument("--strict", action="store_true", help="uyarilari da hata say")
    parser.add_argument("--emit-table", action="store_true",
                        help="AGENTS.md icin uretilmis tabloyu yaz")
    parser.add_argument("--emit-attitude", action="store_true",
                        help="kapisiz kural listesini yaz")
    parser.add_argument("--no-table-check", action="store_true",
                        help="tablo drift kontrolunu atla")
    args = parser.parse_args(argv)

    project_root = find_project_root()
    rules_dir = project_root / ".agent" / "rules"
    agents_path = project_root / ".agent" / "AGENTS.md"
    workflow_path = rules_dir / "development-workflow.md"

    if not rules_dir.is_dir():
        print(f"[HATA] kural dizini bulunamadi: {rules_dir}", file=sys.stderr)
        return 2

    try:
        rules = collect_rules(rules_dir)
    except GateError as exc:
        print(f"[HATA] {exc}", file=sys.stderr)
        return 2

    if args.emit_table:
        print(render_table(rules, "rules/"))
        return 0
    if args.emit_attitude:
        print(render_attitude_list(rules))
        return 0

    errors, warnings = validate(rules_dir, agents_path, workflow_path,
                                project_root, check_tables=not args.no_table_check)

    if args.json:
        print(json.dumps({
            "errors": [{"code": c, "file": f, "message": m} for c, f, m in errors],
            "warnings": [{"code": c, "file": f, "message": m} for c, f, m in warnings],
            "rules": len(rules),
            "measurable": sum(1 for r in rules if r.sinif == "OLCULEBILIR"),
            "exit": 1 if errors or (args.strict and warnings) else 0,
        }, ensure_ascii=False, indent=2))
        return 1 if errors or (args.strict and warnings) else 0

    counts = {c: sum(1 for r in rules if r.sinif == c) for c in CLASSES}
    print(f"Kural dosyasi: {len(rules)}  |  olculebilir: {counts['OLCULEBILIR']}  "
          f"tutum: {counts['TUTUM']}  surec: {counts['SUREC']}")

    for code, name, message in errors:
        print(f"[HATA] {code} {name}: {message}")
    for code, name, message in warnings:
        print(f"[UYARI] {code} {name}: {message}")

    failed = bool(errors) or (args.strict and bool(warnings))
    if failed:
        print(f"\nSONUC: {len(errors)} hata · {len(warnings)} uyari · kapilar gecersiz")
        return 1

    print(f"\nSONUC: {len(rules)} kural · {counts['OLCULEBILIR']} olculebilir kapili · "
          f"{counts['TUTUM'] + counts['SUREC']} kapisiz beyan akisi · [OK]")
    return 0


if __name__ == "__main__":
    sys.exit(main())