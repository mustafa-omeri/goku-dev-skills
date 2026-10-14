#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""google-fonts.csv'yi runtime yoluyla dogrular: search.py sonuclari CSV'de var mi?

Yapisal dogrulama (BOM, satir sayisi, tekillik) verinin "okunabilir" oldugunu
gosterir. Bu test ise "dogru okunuyor" oldugunu gosterir: search.py'nin dondurdugu
her aile CSV'de gercekten bulunmali.
"""
import csv
import io
import json
import subprocess
import sys
from pathlib import Path

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / ".agent" / "skills" / "ui-ux-pro-max"
DATA = SKILL / "data"
SEARCH = SKILL / "scripts" / "search.py"

QUERIES = [
    "sans serif popular variable",
    "serif luxury elegant",
    "monospace code terminal",
    "display bold heading",
    "handwriting script casual",
    "variable font axes",
]

failures = []


def check(label, cond, detail=""):
    print(f"  {'PASS' if cond else 'FAIL'}  {label}" + (f"  -- {detail}" if detail else ""))
    if not cond:
        failures.append(label)


def search(query, domain, n=5):
    out = subprocess.run(
        [sys.executable, str(SEARCH), query, "--domain", domain, "-n", str(n)],
        capture_output=True, text=True, encoding="utf-8", cwd=str(SKILL),
    )
    return out.stdout if out.returncode == 0 else ""


def run_audit():
    # CSV'deki aile kumesi
    csv_file = DATA / "google-fonts.csv"
    if not csv_file.is_file():
        check("google-fonts.csv dosyasi mevcut", False, str(csv_file))
        return False

    rows = list(csv.DictReader(io.StringIO(
        csv_file.read_text(encoding="utf-8"))))
    families = {r["Family"] for r in rows}
    print(f"CSV: {len(families):,} aile\n")

    print("=== search.py --domain google-fonts sonuclari CSV'de mi ===")
    total_hits = 0
    for q in QUERIES:
        out = search(q, "google-fonts")
        found = [ln.split("**Family:** ")[1].strip()
                 for ln in out.splitlines() if ln.startswith("- **Family:**")]
        total_hits += len(found)
        unknown = [f for f in found if f not in families]
        check(f"'{q}' -> {len(found)} sonuc, hepsi CSV'de",
              bool(found) and not unknown,
              (f"CSV disi: {unknown}" if unknown else ""))

    print(f"  toplam {total_hits} aile dogrulandi")

    print()
    print("=== --design-system ciktisindaki font linki gercekten var mi ===")
    out = subprocess.run(
        [sys.executable, str(SEARCH), "saas analytics dashboard",
         "--design-system", "-f", "markdown"],
        capture_output=True, text=True, encoding="utf-8", cwd=str(SKILL),
    )
    md = out.stdout
    css2 = [ln for ln in md.splitlines() if "fonts.googleapis.com/css2?family=" in ln]
    check("design-system css2 font linki uretti", bool(css2),
          css2[0].strip()[:74] if css2 else "link yok")

    if css2:
        import re as _re
        url = css2[0].split("https://", 1)[-1]
        picked = [f.replace("+", " ") for f in _re.findall(r"family=([^:&\s]+)", url)]
        check(f"linkteki {len(picked)} aile CSV'de var",
              len(picked) >= 1 and all(p in families for p in picked),
              f"ayristirilan: {picked} | CSV disi: {[p for p in picked if p not in families]}")

    out2 = search("display bold heading", "google-fonts", n=3)
    specimen = [ln for ln in out2.splitlines() if "fonts.google.com/specimen/" in ln]
    check("google-fonts domaini specimen linki veriyor", bool(specimen),
          specimen[0].strip()[:74] if specimen else "link yok")
    if specimen:
        slug = specimen[0].strip().rsplit("/", 1)[-1]
        check(f"specimen slug'i CSV'de ({slug})", slug in families)

    print()
    print("=== icons domain: katalog butunlugu ===")
    icons_csv_file = DATA / "icons.csv"
    if icons_csv_file.is_file():
        icons_csv = list(csv.DictReader(io.StringIO(
            icons_csv_file.read_text(encoding="utf-8"))))
        out = search("decorative icon aria hidden", "icons", n=4)
        found = [ln.split("**Icon Name:** ")[1].strip()
                 for ln in out.splitlines() if ln.startswith("- **Icon Name:**")]
        names = {r.get("Icon Name") for r in icons_csv}
        check(f"icons.csv {len(icons_csv)} satir", len(icons_csv) > 50)
        check("icons sonuclari icons.csv icinde", all(f in names for f in found),
              f"{len(found)} sonuc")

    upstream_file = DATA / "phosphor-icons-upstream.json"
    if upstream_file.is_file() and icons_csv_file.is_file():
        manifest = json.loads(upstream_file.read_text(encoding="utf-8"))
        upstream = {i["name"] for i in manifest["icons"]}
        curated = {r["Icon Name"] for r in icons_csv if r.get("Library") == "Phosphor"}
        check(f"Phosphor katalog: {manifest['iconCount']} ikon upstream, "
              f"{len(curated)} kurator", True)
        missing = {c for c in curated if not c.startswith("icon-")} - upstream
        check("kuratorlu Phosphor satirlari upstream manifest'te var",
              not missing, f"eksik: {sorted(missing)[:5]}")

    print()
    print("=" * 58)
    print(f"SONUC: {len(failures)} sorun -> {failures}" if failures else "SONUC: TEMIZ")
    return len(failures) == 0


if __name__ == "__main__":
    success = run_audit()
    sys.exit(0 if success else 1)
