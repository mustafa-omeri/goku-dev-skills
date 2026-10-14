#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ui-ux-pro-max veri dosyalarinin butunluk denetimi.

Hedef: data/google-fonts.csv (749 KB) ve data/phosphor-icons-upstream.json (857 KB)
        ve data/google-font-licenses.json (453 KB)
"""
import csv
import io
import json
import sys
from collections import Counter
from pathlib import Path

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / ".agent" / "skills" / "ui-ux-pro-max" / "data"
problems = []
notes = []


def fail(msg):
    problems.append(msg)
    print(f"  FAIL  {msg}")


def ok(msg):
    print(f"  PASS  {msg}")


def run_audit():
    # ---------------------------------------------------------------- google-fonts
    print("=== data/google-fonts.csv ===")
    p = DATA / "google-fonts.csv"
    if not p.is_file():
        fail(f"Dosya bulunamadi: {p}")
        return False

    size = p.stat().st_size
    raw = p.read_bytes()
    print(f"  boyut: {size:,} bayt")

    if raw[:3] == b"\xef\xbb\xbf":
        fail("UTF-8 BOM var")
    else:
        ok("BOM yok")

    if b"\r\n" in raw:
        notes.append("google-fonts.csv CRL satir sonu kullaniyor")
        print("  NOTE  CRL satir sonu var")
    else:
        ok("LF satir sonu")

    try:
        text = raw.decode("utf-8")
        ok("UTF-8 cozumlemesi tam")
    except UnicodeDecodeError as e:
        fail(f"UTF-8 cozumlemesi basarisiz: {e}")
        text = raw.decode("utf-8", errors="replace")

    if not text.endswith("\n"):
        fail("son satir yarim kesik (dosya newline ile bitmiyor)")
    else:
        ok("son satir tam (newline ile bitiyor)")

    rows = list(csv.DictReader(io.StringIO(text)))
    print(f"  satir sayisi: {len(rows):,}")
    if len(rows) < 100:
        fail(f"satir sayisi beklenenden az: {len(rows)}")
    else:
        ok(f"{len(rows):,} font kaydi")

    header = list(rows[0].keys()) if rows else []
    print(f"  sutunlar ({len(header)}): {', '.join(header)}")

    key = header[0] if header else None
    if key:
        values = [r[key] for r in rows]
        dupes = [v for v, c in Counter(values).items() if c > 1]
        if dupes:
            fail(f"{key} tekrarli: {len(dupes)} farkli deger, orn. {dupes[:5]}")
        else:
            ok(f"{key} benzersiz ({len(values):,} deger)")

    empty_key = sum(1 for r in rows if not (r.get(key) or "").strip())
    if empty_key:
        fail(f"{empty_key} satir bos {key} iceriyor")
    else:
        ok(f"hicbir satir bos {key} degil")

    ragged = [i for i, r in enumerate(rows, 2) if None in r or any(v is None for v in r.values())]
    if ragged:
        fail(f"{len(ragged)} satir sutun sayisi tutarsiz, orn. {ragged[:5]}")
    else:
        ok("tum satirlar ayni sutun sayisinda")

    sample = rows[0]
    print("\n  ornek kayit:")
    for h in header:
        print(f"    {h:<22} {str(sample.get(h))[:70]}")

    for expected in ("Family", "Category", "Stroke"):
        if expected in header:
            cats = Counter(r.get(expected) for r in rows)
            ok(f"{expected} dagilimi: " + ", ".join(f"{k}={v}" for k, v in cats.most_common(5)))
        else:
            fail(f"beklenen sutun yok: {expected}")

    # ------------------------------------------------------------ phosphor icons
    print()
    print("=== data/phosphor-icons-upstream.json ===")
    p = DATA / "phosphor-icons-upstream.json"
    if not p.is_file():
        fail(f"Dosya bulunamadi: {p}")
        return False

    size = p.stat().st_size
    raw = p.read_bytes()
    print(f"  boyut: {size:,} bayt")

    if raw[:3] == b"\xef\xbb\xbf":
        fail("UTF-8 BOM var")
    else:
        ok("BOM yok")

    try:
        doc = json.loads(raw.decode("utf-8"))
        ok("JSON ayristirma tam")
    except (UnicodeDecodeError, json.JSONDecodeError) as e:
        fail(f"JSON ayristirma basarisiz: {e}")
        doc = None

    if doc is not None:
        print(f"  kok tipi: {type(doc).__name__}")
        if isinstance(doc, dict):
            print(f"  anahtarlar: {', '.join(list(doc)[:8])}")
            for k, v in doc.items():
                print(f"    {k}: {type(v).__name__} ({len(v) if hasattr(v, '__len__') else '-'})")
        elif isinstance(doc, list):
            print(f"  oge sayisi: {len(doc)}")
            print(f"  ilk oge anahtarlari: {', '.join(list(doc[0])[:10]) if doc and isinstance(doc[0], dict) else '-'}")

        items = doc if isinstance(doc, list) else None
        if isinstance(doc, dict):
            for keyname in ("icons", "data", "families", "entries"):
                if isinstance(doc.get(keyname), list):
                    items = doc[keyname]
                    print(f"  '{keyname}' listesi: {len(items)} oge")
                    break
        if items:
            names = [i.get("name") for i in items if isinstance(i, dict) and "name" in i]
            if names:
                dupes = [n for n, c in Counter(names).items() if c > 1]
                if dupes:
                    fail(f"tekrarli ikon adi: {len(dupes)}, orn. {dupes[:5]}")
                else:
                    ok(f"ikon adlari benzersiz ({len(names):,})")
            empty = sum(1 for i in items if isinstance(i, dict) and not i.get("name"))
            if empty:
                fail(f"{empty} ikonun adi bos")
            else:
                ok("hicbir ikonun adi bos degil")
            truncated = [i.get("name") for i in items if isinstance(i, dict)
                         and isinstance(i.get("svg"), str) and not i["svg"].rstrip().endswith("</svg>")]
            if truncated:
                fail(f"{len(truncated)} ikonun SVG'si yarim kesik, orn. {truncated[:5]}")
            else:
                ok("SVG gomulu ikonlarin hepsi </svg> ile kapanmis")

    # ------------------------------------------------------- google-font-licenses
    print()
    print("=== data/google-font-licenses.json (lisans butunlugu) ===")
    p = DATA / "google-font-licenses.json"
    if p.is_file():
        raw = p.read_bytes()
        print(f"  boyut: {len(raw):,} bayt")
        try:
            lic = json.loads(raw.decode("utf-8"))
            ok("JSON ayristirma tam")
            if isinstance(lic, dict):
                print(f"  kayit sayisi: {len(lic)}")
                families = set()
                for v in lic.values():
                    if isinstance(v, dict) and "family" in v:
                        families.add(v["family"])
                print(f"  kapsanan aile: {len(families)}")
        except Exception as e:
            fail(f"JSON ayristirma basarisiz: {e}")
    else:
        notes.append("google-font-licenses.json mevcut degil (opsiyonel)")

    print()
    print("=" * 58)
    print(f"SONUC: {len(problems)} sorun" if problems else "SONUC: TEMIZ")
    for x in problems:
        print(f"  - {x}")
    for n in notes:
        print(f"  NOTE: {n}")
    return len(problems) == 0


if __name__ == "__main__":
    success = run_audit()
    sys.exit(0 if success else 1)
