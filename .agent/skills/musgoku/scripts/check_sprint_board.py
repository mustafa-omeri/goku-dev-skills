#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Sprint / kanban / MVP kapisi — surec kuralinin olculebilir karsiligi.

Neden var?
----------
`sprint-delivery-workflow.md` "sprint plani ac, kartlari Gherkin ile yaz,
kanbanda tasi, ciktiyi kullanici test etsin" diyordu. **Kapisi yoktu.**
Ajan "uyguladim" diyor, kimse olcmuyor — setin kendi tespiti:
zorunlu kural olculebilir degilse kaniti olmayan yasaktir
(knowledge-base.md, 2026-10-13).

Bu kapinin asil isi **determinizm**: ayni kurali okuyan iki ajan ayni isi
farkli islememek zorundadir. Bunu metin degil, bu script saglar. Sutun adi,
kart id kipi, zorunlu alanlar ve gherkin dosyasi kuralin icinde yazilidir ve
burada **tek kere** denetlenir; sapma exit 1 doner.

Kontroller
----------
E1 zorunlu dosya eksik      SPRINT_PLAN.md, KANBAN.md veya KULLANICI_TEST_REHBERI.md yok
E2 sprint plani bicimi      `## Sprint N` + Hedef + MVP Kapsam + Kapsam Disi
E3 sutun kumesi             tam olarak 4 sabit sutun, baska sutun yok
E4 kart basligi             `### S<n>-<nn> · baslik`, id yinelenemez
E5 zorunlu alan eksik       durum/onyelik/sprint/gherkin/kapi/test/risk
E6 gherkin dosyasi yok      baslamis kart (Yapiliyor/Sinirda/Yapildi) icin
E7 gherkin icerigi          Given/When/Then ve Scenario kelimeleri yok
E8 kullanici testi yok      Yapildi kartinda `test:` alani bos / sablon
E9 kapi alani bos           `kapi:` zorunlu ve bos olamaz
E10 release plani tasima    kapaliMamis her kart release planinda olmali
E11 WIP limiti              Yapiliyor sutunu limiti asiliyor
W1 oncelik gecersizP1/P2/P3 disinda
W2 risk gecersiz            yuksek/orta/dusuk disinda
W3 MVP disi                 kart ne MVP kapsaminda ne Kapsam Disi listesinde

E1-E11 hata (exit 1) · W1-W3 uyari (exit 0) · exit 2 = arac hatasi.
**SPRINT_PLAN.md ve KANBAN.md hic yoksa kapi kapsam disidir: exit 0.**
Bu kural `delivery.py` ile 4 projeye dagitilir; henuz plan acmamis projeler
kirmizi almamalidir (check_vite_spa.py'den ogrenilen ilke).

Kullanim
--------
    python .agent/skills/musgoku/scripts/check_sprint_board.py
    python .agent/skills/musgoku/scripts/check_sprint_board.py --json
    python .agent/skills/musgoku/scripts/check_sprint_board.py --wip 2

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
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# --- sabitler: kural ile burasi tek kere konusur --------------------------------

COLUMNS = ("Bekliyor", "Yapılıyor", "Sınırdı", "Yapıldı")
COLUMN_RE = re.compile(r"^##\s+(.+?)\s*$")
CARD_RE = re.compile(r"^###\s+(S(\d+)-(\d+))\s*[·:\-—]\s*(\S.*?)\s*$")
FIELD_RE = re.compile(r"^\|\s*([^|]+?)\s*\|\s*(.*?)\s*\|\s*$")
SEPARATOR_RE = re.compile(r"^\|[\s:\-|]+\|$")

REQUIRED_FIELDS = ("durum", "oncelik", "sprint", "gherkin", "kapi", "test", "risk")
STARTED_COLUMNS = ("Yapılıyor", "Sınırdı", "Yapıldı")
DONE_COLUMN = "Yapıldı"
DONE_TEST_PLACEHOLDERS = ("", "-", "yazılacak", "yazilacak", "(yazılacak)",
                          "(yazilacak)", "todo", "tbd", "?")

PRIORITIES = ("P1", "P2", "P3")
RISKS = ("yüksek", "orta", "düşük", "yuksek", "dusuk")

GHERKIN_SCENARIO = re.compile(r"^\s*(?:Scenario|Scenario Outline)\s*:", re.MULTILINE)
# Gherkin adimlari buyuk harfle baslar; "And"/"But" ek adimdir, tek basina
# Given/When/Then yerine gecmez.
GHERKIN_STEP = re.compile(r"^\s*(Given|When|Then|And|But)\s+\S", re.MULTILINE)

SPRINT_HEADING_RE = re.compile(r"^##\s+Sprint\s+(\d+)\s*$", re.MULTILINE)


def _field_re(label: str) -> re.Pattern:
    """Sprint plani alani: hem `**Hedef**` hem `### Hedef` yazimini kabul eder.

    Iki bicim de kanitta var; hangisinin kullanildigini bilmek kapinin isi
    degil, alanin **var olmasi** kapinin isidir.
    """
    return re.compile(rf"(?:\*\*{label}\*\*|^#{{2,4}}\s+{label}\s*$)", re.MULTILINE)


SPRINT_FIELDS = (
    ("Hedef", _field_re("Hedef")),
    ("MVP Kapsam", _field_re("MVP Kapsam")),
    ("Kapsam Dışı", _field_re("Kapsam Dışı")),
)


class GateError(Exception):
    """Arac hatasi: girdi okunamadi veya yorumlanamadi."""


# --- giris ---------------------------------------------------------------------

def find_project_root() -> Path:
    env = os.environ.get("AGENTS_PROJECT_ROOT")
    if env:
        return Path(env).resolve()
    return Path(__file__).resolve().parents[4]


# --- ayristirma ----------------------------------------------------------------

def parse_card_table(lines, index):
    """Kart basligindan sonraki `| alan | deger |` satirlarini oku.

    (lines, index) -> (alanlar, sonraki_satir_indeksi)
    """
    fields = {}
    i = index
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue
        if SEPARATOR_RE.match(line):
            i += 1
            continue
        match = FIELD_RE.match(line)
        if not match:
            break
        key = match.group(1).strip().lower()
        if key in ("alan", "field", "---"):
            i += 1
            continue
        fields.setdefault(key, match.group(2).strip())
        i += 1
    return fields, i


def parse_kanban(text):
    """(sutun -> [(id, baslik, alanlar)], taninmayan_sutunlar, bozuk_basliklar)"""
    lines = text.splitlines()
    columns = {name: [] for name in COLUMNS}
    unknown_columns = []
    bad_headings = []

    current = None
    i = 0
    while i < len(lines):
        raw = lines[i]
        stripped = raw.strip()

        if raw.startswith("## "):
            name = COLUMN_RE.match(stripped).group(1).strip()
            if name in columns:
                current = name
            else:
                unknown_columns.append((i + 1, name))
                current = None
            i += 1
            continue

        if raw.startswith("### "):
            match = CARD_RE.match(stripped)
            if not match:
                if current is not None:
                    bad_headings.append((i + 1, stripped))
                i += 1
                continue
            card_id = match.group(1)
            title = match.group(4)
            fields, i = parse_card_table(lines, i + 1)
            if current is None:
                bad_headings.append((i, f"{card_id} · {title} (sütunsuz)"))
            else:
                columns[current].append((card_id, title, fields, i))
            continue

        i += 1

    return columns, unknown_columns, bad_headings


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


# Kanban `#senaryo-adi` baglantisi ASCII kebab-case yazilir; Gherkin senaryo
# basligi ise Turkce cumle olabilir ("Sablonlar dagitildi"). Karsilastirma ham
# metinle degil, ikisinin de ayni kurala gore duzlestirilmis haliyle yapilir.
_TR_FOLD = str.maketrans("çğıöşüÇĞİÖŞÜâîûÂÎÛ", "cgiosuCGIOSUaiuAIU")


def _slug(text: str) -> str:
    """Turkce harfleri ASCII'ye indirger, kalanini tek tireye indirger."""
    text = text.translate(_TR_FOLD).lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


# --- denetim -------------------------------------------------------------------

def check(root: Path, wip_limit: int = 3):
    errors = []
    warnings = []

    sprint_path = root / "SPRINT_PLAN.md"
    board_path = root / "KANBAN.md"

    # Kapsam disi: hicbir plan dosyasi yok. Dagitim global oldugu icin bu
    # yol sik olmali — yoksa henuz plan acmamis her proje kirmizi alir.
    if not sprint_path.exists() and not board_path.exists():
        return errors, warnings, {"scope": "yok", "cards": 0, "done": 0, "open": 0}

    if not sprint_path.is_file():
        errors.append(("E1", "SPRINT_PLAN.md", "dosya yok (kanban varsa plan da olmali)"))
    if not board_path.is_file():
        errors.append(("E1", "KANBAN.md", "dosya yok (plan varsa kanban da olmali)"))
    guide_path = root / "KULLANICI_TEST_REHBERI.md"
    if not guide_path.is_file():
        guide_path = root / "docs" / "KULLANICI_TEST_REHBERI.md"
    if not guide_path.is_file():
        errors.append(("E1", "KULLANICI_TEST_REHBERI.md",
                       "dosya yok (sprint planı açılmışsa kullanıcı test rehberi de olmalı: "
                       "proje kökü veya docs/KULLANICI_TEST_REHBERI.md, "
                       "şablon: .agent/templates/KULLANICI_TEST_REHBERI.template.md)"))

    # --- E2 sprint plani bicimi
    sprint_text = ""
    if sprint_path.is_file():
        sprint_text = read_text(sprint_path)
        if not SPRINT_HEADING_RE.search(sprint_text):
            errors.append(("E2", "SPRINT_PLAN.md",
                           "`## Sprint <n>` basligi yok"))
        for label, pattern in SPRINT_FIELDS:
            if not pattern.search(sprint_text):
                errors.append(("E2", "SPRINT_PLAN.md",
                               f"`{label}` alani yok "
                               "(Hedef / MVP Kapsam / Kapsam Disi zorunlu)"))

    if not board_path.is_file():
        return errors, warnings, {"scope": "eksik", "cards": 0, "done": 0, "open": 0}

    board_text = read_text(board_path)

    # --- E3 sutun kumesi
    found_headings = [m.group(1).strip() for m in
                      (COLUMN_RE.match(l.strip()) for l in board_text.splitlines()
                       if l.startswith("## ")) if m]
    for name in found_headings:
        if name not in COLUMNS:
            line = next(i + 1 for i, l in enumerate(board_text.splitlines())
                        if l.strip() == f"## {name}")
            errors.append(("E3", "KANBAN.md",
                           f"satir {line}: taninmayan sutun `{name}` "
                           f"(izin verilen: {', '.join(COLUMNS)})"))

    columns, unknown_columns, bad_headings = parse_kanban(board_text)
    for line, name in unknown_columns:
        errors.append(("E3", "KANBAN.md",
                       f"satir {line}: taninmayan sutun `{name}`"))

    for line, text in bad_headings:
        errors.append(("E4", "KANBAN.md",
                       f"satir {line}: kart basligi kipi yanlis -> {text} "
                       "(beklenen `### S<n>-<nn> · baslik`)"))

    # --- kartlar
    seen_ids = {}
    total = 0
    for column in COLUMNS:
        for card_id, title, fields, line in columns[column]:
            total += 1
            where = f"{card_id} ({column})"

            if card_id in seen_ids:
                errors.append(("E4", "KANBAN.md",
                               f"satir {line}: yinelenen kart id `{card_id}` "
                               f"(ilk geçiş: {seen_ids[card_id]})"))
            else:
                seen_ids[card_id] = line

            # E5 zorunlu alanlar
            missing = [f for f in REQUIRED_FIELDS if f not in fields or not fields[f]]
            # `kapi:` bos birakilmissa bu E5 degil E9'dur; ikisinin ayni anda
            # bildirilmesi gürültü olurdu.
            if "kapi" in fields and not fields["kapi"].strip():
                errors.append(("E9", "KANBAN.md",
                               f"satir {line}: {where} `kapi:` bos — calistirilabilir "
                               "bir komut yazilmali"))
                missing = [f for f in missing if f != "kapi"]
            if missing:
                errors.append(("E5", "KANBAN.md",
                               f"satir {line}: {where} zorunlu alan eksik -> "
                               f"{', '.join(missing)}"))
                continue

            if fields["durum"] != column:
                errors.append(("E5", "KANBAN.md",
                               f"satir {line}: {where} `durum` alani sutunla "
                               f"tutarsiz -> `{fields['durum']}`"))

            if fields["oncelik"] not in PRIORITIES:
                warnings.append(("W1", "KANBAN.md",
                                 f"satir {line}: {where} oncelik `{fields['oncelik']}` "
                                 f"(gecerli: {', '.join(PRIORITIES)})"))
            if fields["risk"].lower() not in RISKS:
                warnings.append(("W2", "KANBAN.md",
                                 f"satir {line}: {where} risk `{fields['risk']}` "
                                 "(gecerli: yuksek / orta / dusuk)"))

            # E9 kapi — yukarida bos kapi ayri kodlandi; burada yalniz
            # eksik `kapi` anahtari E5 ile zaten yakalandi.

            # E6 / E7 gherkin — yalniz baslamis kartlar icin
            if column in STARTED_COLUMNS:
                spec = fields["gherkin"].split("#")[0].strip()
                spec_path = root / spec
                if not spec or spec in ("-", "yazılacak", "yazilacak"):
                    errors.append(("E6", "KANBAN.md",
                                   f"satir {line}: {where} baslamis ama "
                                   f"`gherkin:` henuz yazilmamis"))
                elif not spec_path.is_file():
                    errors.append(("E6", "KANBAN.md",
                                   f"satir {line}: {where} gherkin dosyasi yok -> {spec}"))
                else:
                    spec_text = read_text(spec_path)
                    steps = {kw.upper() for kw in GHERKIN_STEP.findall(spec_text)}
                    has_then = "THEN" in steps
                    has_given_when = bool(steps & {"GIVEN", "WHEN"})
                    if not (GHERKIN_SCENARIO.search(spec_text)
                            and has_given_when and has_then):
                        errors.append(("E7", spec,
                                       f"{where} gherkin eksik: `Scenario:` + "
                                       "Given/When/Then adimlari gerekli"))
                    else:
                        keyword = fields["gherkin"].split("#")[1].strip() if "#" in fields["gherkin"] else ""
                        if keyword and _slug(keyword) not in {
                                _slug(m.group(1)) for m in
                                re.finditer(r"^\s*Scenario(?: Outline)?:\s*(.+?)\s*$",
                                            spec_text, re.MULTILINE)}:
                            errors.append(("E7", spec,
                                           f"{where} `#{keyword}` senaryosu dosyada bulunamadi"))

            # E8 kullanici testi — Yapildi kartinda zorunlu
            if column == DONE_COLUMN:
                if fields["test"].strip().lower() in DONE_TEST_PLACEHOLDERS:
                    errors.append(("E8", "KANBAN.md",
                                   f"satir {line}: {where} `test:` alani kullanici "
                                   "test adimi degil (bos / 'yazilacak')"))
                elif not re.search(r"[0-9]|->|→", fields["test"]):
                    warnings.append(("W4", "KANBAN.md",
                                     f"satir {line}: {where} test adimi olculur "
                                     "sonuc icermiyor"))

            # W3 MVP kapsami
            if sprint_text and card_id not in sprint_text:
                warnings.append(("W3", "KANBAN.md",
                                 f"satir {line}: {where} SPRINT_PLAN.md'de "
                                 "`MVP Kapsam` veya `Kapsam Disi` altinda gecmiyor"))

    # --- E11 WIP limiti
    doing = len(columns["Yapılıyor"])
    if doing > wip_limit:
        errors.append(("E11", "KANBAN.md",
                       f"Yapiliyor sutununda {doing} kart var, limit {wip_limit}"))

    # --- E10 release plani tasima
    open_ids = [cid for column in COLUMNS if column != DONE_COLUMN
                for cid, _t, _f, _l in columns[column]]
    release_path = root / "RELEASE_PLAN.md"
    if open_ids:
        if not release_path.is_file():
            errors.append(("E10", "RELEASE_PLAN.md",
                           f"{len(open_ids)} kapanmamis kart var ama release plani yok: "
                           + ", ".join(sorted(open_ids))))
        else:
            release_text = read_text(release_path)
            carried = [cid for cid in open_ids if cid not in release_text]
            if carried:
                errors.append(("E10", "RELEASE_PLAN.md",
                               "kapanmamis kartlar planda gecmiyor: "
                               + ", ".join(sorted(carried))))

    done = len(columns[DONE_COLUMN])
    stats = {"scope": "denetlendi", "cards": total, "done": done,
             "open": total - done, "wip": doing}
    return errors, warnings, stats


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Sprint / kanban / MVP kapisi (Gherkin + kullanici testi zorunlulugu)")
    parser.add_argument("--json", action="store_true", help="makine okunur cikti")
    parser.add_argument("--wip", type=int, default=3,
                        help="Yapiliyor sutunu limiti (varsayilan 3)")
    args = parser.parse_args(argv)

    root = find_project_root()
    if not root.is_dir():
        print(f"[HATA] proje koku bulunamadi: {root}", file=sys.stderr)
        return 2

    try:
        errors, warnings, stats = check(root, args.wip)
    except OSError as exc:
        print(f"[HATA] dosya okunamadi: {exc}", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps({
            **stats,
            "errors": [{"code": c, "file": f, "message": m} for c, f, m in errors],
            "warnings": [{"code": c, "file": f, "message": m} for c, f, m in warnings],
            "exit": 1 if errors else 0,
        }, ensure_ascii=False, indent=2))
        return 1 if errors else 0

    if stats["scope"] != "denetlendi":
        print("Kapsam disi · [OK]")
        print("  SPRINT_PLAN.md ve KANBAN.md yok — bu projede sprint plani acilmamis.")
        print(f"  Kural: .agent/rules/sprint-delivery-workflow.md · acmak icin "
              f".agent/templates/ altindaki sablonlari kopyala.")
        return 0

    print(f"Kart: {stats['cards']}  ·  Yapildi: {stats['done']}  ·  "
          f"acik: {stats['open']}  ·  Yapiliyor (WIP): {stats['wip']}/{args.wip}")
    for code, name, message in errors:
        print(f"[HATA] {code} {name}: {message}")
    for code, name, message in warnings:
        print(f"[UYARI] {code} {name}: {message}")

    if errors:
        print(f"\nSONUC: {len(errors)} hata · {len(warnings)} uyari · "
              f"sprint kapisi gecersiz")
        return 1

    print(f"\nSONUC: {stats['cards']} kart · gherkin + kapi + kullanici testi "
          f"eksiksiz · [OK]")
    return 0


if __name__ == "__main__":
    sys.exit(main())