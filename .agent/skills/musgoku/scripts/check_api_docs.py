#!/usr/bin/env python3
"""API dokumantasyonu kapisi — endpoint var, `docs/APIs/` karsiligi yok.

Neden var?
----------
`api-documentation-enforcement.md` 12 bölüm ve 30+ kontrol maddesi yaziyor ama
**hicbiri calistirilabilir degildi.** Kural "zorunlu" diyor, dosya degisse bile
kiminse `docs/APIs/` dosyasini elle bulup guncellemesi gerekiyordu. Session
devri yaziyordu, kapri yazmiyordu.

Bu script uc seyi olcer:
  1. her Spring endpoint'in `docs/APIs/` altinda yazili karsiligi var mi   (E1)
  2. endpoint varsa `docs/APIs/` dizini var mi                                (E2)
  3. controller'da @Tag, endpoint'te @Operation var mi                       (W1/W2)

Dokumantasyon *icerigi* (tarih damgasi, ornek JSON, migration guide) bu
scriptin konusu degil — o kalan TUTUM kalir ve beyanla denetlenir. Buradaki
kapi kasitli olarak **var/yok** denetler; yoksa olcumun guvenilirligi dustu.

Kontroller
----------
E1 endpoint belgelenmemis        her METHOD /path `docs/APIs/` altinda olmali
E2 docs/APIs dizini yok         endpoint varsa dokumantasyon dizini zorunlu
E3 git-diff API sapmasi          Git diff'te controller/route degisti ama docs/APIs guncellenmedi
W1 @Tag eksik                   controller sinifinda @Tag olmali
W2 @Operation eksik             endpoint metodunda @Operation olmali

E1-E3 hata (exit 1) · W1-W2 uyari · exit 2 arac hatasi
Backend projesi degilse (pom.xml yok, controller/route yok) kapsam disi: exit 0.

Kullanim
--------
    python .agent/skills/musgoku/scripts/check_api_docs.py
    python .agent/skills/musgoku/scripts/check_api_docs.py --json

Ortam
-----
AGENTS_PROJECT_ROOT   proje kokunu elle verir
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Annotation tam nitelikli de yazilabilir:
#   @org.springframework.web.bind.annotation.PostMapping("/x")
# Onek grubu olmadan bu satirlar hic gorulmuyordu (3 endpoint kayipti).
ANNOTATION_RE = re.compile(
    r"@(?:[A-Za-z_][A-Za-z0-9_]*\.)*"
    r"(GetMapping|PostMapping|PutMapping|PatchMapping|DeleteMapping|RequestMapping)\b")
CONTROLLER_RE = re.compile(
    r"@(?:[A-Za-z_][A-Za-z0-9_]*\.)*(?:RestController|Controller)\b")
# `@RestControllerAdvice` icinde `@RestController` alt dizisi gecer; ayri ele alinir.
ADVICE_RE = re.compile(
    r"@(?:[A-Za-z_][A-Za-z0-9_]*\.)*(?:RestControllerAdvice|ControllerAdvice)\b")
CLASS_RE = re.compile(r"\b(?:public\s+|abstract\s+|final\s+)*(?:class|record)\s+\w+")
STRING_RE = re.compile(r'"([^"]*)"')
DOC_ENDPOINT_RE = re.compile(
    r"\b(GET|POST|PUT|PATCH|DELETE)\b[^\n`]{0,4}(/[A-Za-z0-9_\-{}/.]*)")
DOC_URL_LINE_RE = re.compile(
    r"(?:URL|Endpoint|Adres)\s*:\s*[*_`\s]*(/[A-Za-z0-9_\-{}/.]*)", re.IGNORECASE)
DOC_METHOD_LINE_RE = re.compile(
    r"Method\s*:\s*[*_`\s]*(GET|POST|PUT|PATCH|DELETE)", re.IGNORECASE)
IGNORE_DIRS = {"target", "build", "node_modules", ".git", "out"}

METHOD_BY_ANNOTATION = {
    "GetMapping": "GET",
    "PostMapping": "POST",
    "PutMapping": "PUT",
    "PatchMapping": "PATCH",
    "DeleteMapping": "DELETE",
}


def find_project_root() -> Path:
    env = os.environ.get("AGENTS_PROJECT_ROOT")
    if env:
        return Path(env).resolve()
    return Path(__file__).resolve().parents[4]


def read_args(text: str, start: int):
    """Annotasyonun '(' ... ')' arguman govdesini dondurur (string farkindali)."""
    return read_args_span(text, start)[0]


def read_args_span(text: str, start: int):
    """(arguman govdesi, kapanis parantezinden sonraki konum)."""
    i = start
    while i < len(text) and text[i] in " \t\r\n":
        i += 1
    if i >= len(text) or text[i] != "(":
        return "", i
    depth = 0
    in_string = False
    j = i
    while j < len(text):
        ch = text[j]
        if in_string:
            if ch == "\\":
                j += 2
                continue
            if ch == '"':
                in_string = False
        elif ch == '"':
            in_string = True
        elif ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0:
                return text[i + 1:j], j + 1
        j += 1
    return "", i


def has_operation(text: str, lower: int, ann_start: int, ann_end: int) -> bool:
    """`@Operation` mapping'in USTUNDE veya ALTINDA olabilir.

    Ust sinir = onceki mapping annotasyonunun sonu. `}` karakterini sinir
    almak yanlisti: `@Operation` -> `@ApiResponses({...})` -> `@GetMapping`
    zincirinde dizi literalinin `}`'i @Operation'i pencereden cikariyordu.
    """
    if "@Operation" in text[lower:ann_start]:
        return True
    stop = len(text)
    for token in ("{", "}"):
        found = text.find(token, ann_end)
        if found != -1:
            stop = min(stop, found)
    following = ANNOTATION_RE.search(text, ann_end)
    if following:
        stop = min(stop, following.start())
    return "@Operation" in text[ann_end:stop]


def join_paths(*parts) -> str:
    joined = "/".join(p.strip() for p in parts if p and p.strip())
    joined = re.sub(r"/{2,}", "/", joined)
    if not joined.startswith("/"):
        joined = "/" + joined
    return joined.rstrip("/") or "/"


def path_to_regex(path: str):
    """`/api/v1/users/{id}` -> calistirilabilir regex."""
    pattern = re.escape(path)
    pattern = re.sub(r"\\\{[^}]*\\\}", r"[^/]+", pattern)
    return re.compile(pattern)


def scan_java(root: Path):
    """(endpointler, @Tag eksik siniflar, @Operation eksik endpointler)."""
    endpoints = []
    missing_tag = []
    missing_operation = []

    java_root = root / "src" / "main" / "java"
    if not java_root.is_dir():
        return endpoints, missing_tag, missing_operation

    for path in sorted(java_root.rglob("*.java")):
        if any(part in IGNORE_DIRS for part in path.parts):
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        class_match = CLASS_RE.search(text)
        if not class_match:
            continue
        class_pos = class_match.start()

        prefixes = []
        annotations = list(ANNOTATION_RE.finditer(text))
        prev_end = class_pos
        for index, match in enumerate(annotations):
            args, ann_end = read_args_span(text, match.end())
            # Sinif seviyesi = annotasyon `class` anahtar kelimesinden once.
            # (Argumanlardaki `{` dizi formu yuzunden `{}` kontrolu burada
            #  kullanilamaz: `@RequestMapping({"/v1/x", "/api/v1/x"})` yalan
            #  pozitif uretiyordu ve tum endpoint'ler oneksiz kaliyordu.)
            is_class_level = match.start() < class_pos

            # `@RequestMapping({"/v1/x", "/api/v1/x"})` dizi formunu da destekle:
            # argumanlardaki tum dizeler sirayla alinir.
            value_match = re.search(r"(?:value|path)\s*=\s*(.*)$", args)
            source = value_match.group(1) if value_match else args
            values = [m.group(1) for m in STRING_RE.finditer(source)] or [""]

            name = match.group(1)
            if is_class_level:
                if name == "RequestMapping":
                    prefixes = values
                prev_end = ann_end
                continue

            if name == "RequestMapping":
                methods = re.findall(r"RequestMethod\.(GET|POST|PUT|PATCH|DELETE)", args)
                if not methods:
                    prev_end = ann_end
                    continue
            else:
                methods = [METHOD_BY_ANNOTATION[name]]

            for http_method in methods:
                for value in values:
                    for base in (prefixes or [""]):
                        full_path = join_paths(base, value)
                        endpoints.append((http_method, full_path, path.name))
                        if not has_operation(text, prev_end, match.start(), ann_end):
                            missing_operation.append(
                                f"{http_method} {full_path} ({path.name})")
            prev_end = ann_end

        head = text[:class_pos]
        if CONTROLLER_RE.search(head) and not ADVICE_RE.search(head):
            if "@Tag" not in head:
                missing_tag.append(path.name)

    return endpoints, missing_tag, missing_operation


NEXT_EXPORT_RE = re.compile(
    r"\bexport\s+(?:async\s+)?function\s+(GET|POST|PUT|PATCH|DELETE)\b"
    r"|\bexport\s+const\s+(GET|POST|PUT|PATCH|DELETE)\s*="
)
FASTAPI_ROUTE_RE = re.compile(
    r"@(?:app|router)\.(get|post|put|patch|delete)\(\s*[\"']([^\"']+)[\"']",
    re.IGNORECASE,
)


def scan_multi_stack_routes(root: Path):
    """Next.js App Router (app/api/**/route.ts) ve FastAPI rotalarini tarar."""
    endpoints = []

    # 1. Next.js App Router: app/api/**/route.{ts,js,tsx,jsx} veya src/app/api/**
    for base_rel in ("app/api", "src/app/api"):
        api_dir = root / base_rel
        if not api_dir.is_dir():
            continue
        app_root = api_dir.parent  # app veya src/app
        for route_file in sorted(api_dir.rglob("route.*")):
            if route_file.suffix not in {".ts", ".js", ".tsx", ".jsx"}:
                continue
            if any(part in IGNORE_DIRS for part in route_file.parts):
                continue
            rel_dir = route_file.parent.relative_to(app_root).as_posix()
            # Next.js [id] -> {id}
            norm_route = "/" + re.sub(r"\[([^\]]+)\]", r"{\1}", rel_dir)
            text = route_file.read_text(encoding="utf-8", errors="replace")
            for m in NEXT_EXPORT_RE.finditer(text):
                method = (m.group(1) or m.group(2)).upper()
                endpoints.append((method, norm_route, route_file.name))

    # 2. FastAPI: routers/ veya app/ altindaki .py dosyalari
    for py_dir_name in ("app", "routers", "src/api"):
        py_dir = root / py_dir_name
        if not py_dir.is_dir():
            continue
        for py_file in sorted(py_dir.rglob("*.py")):
            if any(part in IGNORE_DIRS for part in py_file.parts):
                continue
            text = py_file.read_text(encoding="utf-8", errors="replace")
            for m in FASTAPI_ROUTE_RE.finditer(text):
                endpoints.append((m.group(1).upper(), join_paths(m.group(2)), py_file.name))

    return endpoints


def check_git_diff_api_drift(root: Path) -> list[str]:
    """Git calisma agacinda API controller/route degisip docs/APIs guncellenmemisse yakalar."""
    if not (root / ".git").exists():
        return []
    try:
        proc = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=str(root),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=5,
        )
        if proc.returncode != 0:
            return []

        changed_routes: list[str] = []
        docs_updated = False

        for raw_line in proc.stdout.splitlines():
            line = raw_line.strip()
            if not line:
                continue
            parts = line.split(maxsplit=1)
            if len(parts) < 2:
                continue
            file_part = parts[1].strip().strip('"')
            if " -> " in file_part:
                file_part = file_part.split(" -> ", 1)[1].strip().strip('"')
            norm = file_part.replace("\\", "/")
            norm_lower = norm.lower()

            if (
                norm_lower.startswith("docs/apis/")
                or norm_lower.endswith("api_docs.md")
                or norm_lower.endswith("openapi.yaml")
                or norm_lower.endswith("openapi.json")
                or norm_lower.endswith("swagger.json")
            ):
                docs_updated = True
                continue

            is_route = (
                (norm.endswith("Controller.java") and "src/main/java" in norm)
                or re.search(r"(?:^|/)app/api/.+/route\.(?:ts|js|tsx|jsx)$", norm)
                or (norm_lower.startswith("routers/") and norm_lower.endswith(".py"))
            )
            if is_route:
                changed_routes.append(norm)

        if docs_updated:
            return []
        return changed_routes
    except Exception:
        return []


def strip_decorators(path: str) -> str:
    return path.rstrip(".,;)`*_ \t")


def collect_doc_paths(root: Path):
    """docs/APIs altinda yazili (METHOD, path) ciftleri.

    Iki yazim desteklenir:
      a) satir ici      `POST /api/v1/auth/login`
      b) ayri satirlar  `**URL:** /api/v1/auth/login` + `**Method:** POST`
    (b) ocai'nin gercek bicimidir; yalniz (a) desteklemek 223 yanlis
    pozitif uretiyordu.
    """
    docs_dir = root / "docs" / "APIs"
    found = []
    if not docs_dir.is_dir():
        return found
    for path in sorted(docs_dir.rglob("*.md")):
        text = path.read_text(encoding="utf-8", errors="replace")
        pending = None
        for line in text.split("\n"):
            url_match = DOC_URL_LINE_RE.search(line)
            if url_match:
                pending = strip_decorators(url_match.group(1))
            method_match = DOC_METHOD_LINE_RE.search(line)
            if method_match and pending:
                found.append((method_match.group(1).upper(), pending))
                pending = None
                continue
            for method, api_path in DOC_ENDPOINT_RE.findall(line):
                found.append((method, strip_decorators(api_path)))
    return found


def canonical(path: str) -> str:
    """`/api/v1/x`, `/v1/x`, `/x` -> ayni karsilastirma anahtari.

    Projeler ayni endpoint'i `/api/v1/...` ve `/v1/...` olarak iki sekilde
    map ediyor; dokumantasyon birini yaziyorsa digerini "belgelenmemis"
    saymak yanlis pozitiftir.
    """
    path = path.split("?")[0].rstrip("/")
    path = re.sub(r"^/api(?=/)", "", path)
    path = re.sub(r"^/v\d+(?=/|$)", "", path)
    return path or "/"


def check(root: Path):
    errors = []
    warnings = []

    java_endpoints, missing_tag, missing_operation = scan_java(root)
    other_endpoints = scan_multi_stack_routes(root)
    endpoints = java_endpoints + other_endpoints
    documented = collect_doc_paths(root)
    docs_dir = root / "docs" / "APIs"

    doc_index = sorted(set((m, canonical(p)) for m, p in documented))
    code_index = sorted(set((m, canonical(p), src) for m, p, src in endpoints))

    if not endpoints:
        return errors, warnings, {"endpoints": 0, "documented": len(documented),
                                 "backend": bool(documented)}

    if not docs_dir.is_dir():
        errors.append(("E2", "docs/APIs",
                       f"{len(code_index)} endpoint var ama docs/APIs dizini yok"))
    else:
        for method, api_path, source in code_index:
            if not any(m == method and (p == api_path
                                        or bool(path_to_regex(p).search(api_path)))
                       for m, p in doc_index):
                errors.append(("E1", "docs/APIs",
                               f"{method} {api_path} belgelenmemis ({source})"))

    # E3: Git çalışma ağacında API controller/route değişti ama docs/APIs güncellenmedi
    drift_routes = check_git_diff_api_drift(root)
    if drift_routes:
        errors.append((
            "E3",
            "docs/APIs",
            f"Git calisma agacinda API rotasi/controller degisti ({', '.join(drift_routes[:2])}) "
            f"ancak docs/APIs/ dokumantasyonu guncellenmedi!",
        ))

    for name in missing_tag:
        warnings.append(("W1", name, "controller sinifinda @Tag yok"))

    # @Operation eksigi tek tek listelenmez: 200 satirlik liste uyariyi
    # gormezlestirir. Tek satirlik ozet + `--verbose` ile tam liste.
    if missing_operation:
        warnings.append(("W2", "docs/APIs",
                         f"{len(missing_operation)} endpoint metodunda @Operation yok "
                         f"(tam liste icin --verbose)"))

    return errors, warnings, {"endpoints": len(code_index),
                              "documented": len(doc_index), "backend": True}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="API dokumantasyonu kapisi")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--verbose", action="store_true",
                        help="@Operation eksiklerini tam liste olarak yaz")
    args = parser.parse_args(argv)

    root = find_project_root()
    errors, warnings, stats = check(root)

    if args.json:
        print(json.dumps({
            **stats,
            "errors": [{"code": c, "file": f, "message": m} for c, f, m in errors],
            "warnings": [{"code": c, "file": f, "message": m} for c, f, m in warnings],
            "exit": 1 if errors else 0,
        }, ensure_ascii=False, indent=2))
        return 1 if errors else 0

    if not stats["endpoints"]:
        print("Spring endpoint bulunamadi — kural bu projede kapsam disi")
        print("\nSONUC: 0 endpoint · [OK]")
        return 0

    print(f"Endpoint: {stats['endpoints']} · docs/APIs yazili referans: "
          f"{stats['documented']}")
    for code, name, message in errors:
        print(f"[HATA] {code} {name}: {message}")
    for code, name, message in warnings:
        print(f"[UYARI] {code} {name}: {message}")

    if args.verbose:
        _endpoints, _tags, missing_op = scan_java(root)
        for endpoint in missing_op:
            print(f"[UYARI] W2 @Operation yok: {endpoint}")
    if errors:
        print(f"\nSONUC: {len(errors)} hata · {len(warnings)} uyari · dokumantasyon eksik")
        return 1
    print(f"\nSONUC: {stats['endpoints']} endpoint belgelenmis · [OK]")
    return 0


if __name__ == "__main__":
    sys.exit(main())