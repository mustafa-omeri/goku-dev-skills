#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Yedek politikasi testleri — `--no-backup` ve `--keep` gercekten calisiyor mu?

Neden ayri bir dosya: yedekleme dagitim aracinin EN YANLIS etkisi olan
kisim. 2026-10-13'te 8 kosunun yedekleri birikip 441 MB oldu ve kullanici
el ile silmek zorunda kaldi. Bu testler, aracin kendi kendini temizlemesini
kanitlar.

Kritik kural: prune YALNIZ `<id>-agent-<YYYYMMDD-HHMMSS>` bicimli klasorleri
silebilir. Eski kaynak yedekleri (`*-cursor-rules-*`, `*-eski-*`) KALIR.
"""
import re
import sys
import tempfile
from pathlib import Path

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import delivery  # noqa: E402

failures = []


def check(label, condition, detail=""):
    print(f"  {'PASS' if condition else 'FAIL'}  {label}" + (f"  -- {detail}" if detail else ""))
    if not condition:
        failures.append(label)


def make_backup(root: Path, name: str, files: int = 2) -> Path:
    path = root / name
    path.mkdir(parents=True)
    for i in range(files):
        (path / f"f{i}.md").write_text("x" * 2048, encoding="utf-8")
    return path


def make_config(tmp: Path) -> dict:
    return {
        "backupRoot": str(tmp),
        "projects": [
            {"id": "ocai", "name": "OCAI", "path": str(tmp / "p1")},
            {"id": "FEProjectv1", "name": "FE", "path": str(tmp / "p2")},
        ],
    }


def test_keep_n():
    print("=== TEST 1: --keep N eski yedekleri siler, yenileri birakir ===")
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        config = make_config(tmp)
        for i in range(1, 6):
            make_backup(tmp, f"ocai-agent-2026101{i}-120000")
            make_backup(tmp, f"FEProjectv1-agent-2026101{i}-120000")

        removed, _freed = delivery.prune_backups(config, keep=2)

        ocai = sorted(p.name for p in tmp.glob("ocai-agent-*"))
        check("5 -> 2 yedek kaldi", len(ocai) == 2, f"{len(ocai)} kaldi")
        check("en yeniler kaldi",
              ocai == ["ocai-agent-20261014-120000", "ocai-agent-20261015-120000"],
              str(ocai))
        check("silinen sayisi dogru", removed == 6, str(removed))


def test_keep_not_enough():
    print("=== TEST 2: keep >= mevcut adet -> hicbir sey silinmez ===")
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        config = make_config(tmp)
        make_backup(tmp, "ocai-agent-20261013-100000")
        removed, freed = delivery.prune_backups(config, keep=5)
        check("silinmedi", removed == 0 and freed == 0, f"{removed} silindi")
        check("yedek duruyor", len(list(tmp.glob("ocai-agent-*"))) == 1)


def test_foreign_backups_survive():
    print("=== TEST 3: yedek olmayan klasorler ASLA silinmez ===")
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        config = make_config(tmp)
        for i in range(1, 4):
            make_backup(tmp, f"ocai-agent-2026101{i}-120000")
        # Bunlar eski kaynak yedekleri; tarih damgasi yok, silinmemeli.
        make_backup(tmp, "feproject-cursorrules-20261008.bak")
        make_backup(tmp, "ocai-cursor-rules-20261008")
        make_backup(tmp, "ui-ux-pro-max-eski-20261012")
        make_backup(tmp, "ocai-notlar")

        delivery.prune_backups(config, keep=0)

        survivors = sorted(p.name for p in tmp.iterdir() if p.is_dir())
        check("kursor yedekleri duruyor",
              "feproject-cursorrules-20261008.bak" in survivors
              and "ocai-cursor-rules-20261008" in survivors, str(survivors))
        check("eski skill yedegi duruyor", "ui-ux-pro-max-eski-20261012" in survivors)
        check("tarihsiz klasor duruyor", "ocai-notlar" in survivors)
        check("duruslu yedekler silindi", not list(tmp.glob("ocai-agent-*")))


def test_stamp_pattern():
    print("=== TEST 4: tarih damgasi deseni ===")
    for name in ("ocai-agent-20261013-125617", "FEProjectv1-agent-20260101-000000"):
        check(f"gecerli: {name}", bool(delivery.BACKUP_STAMP_RE.match(name)))
    for name in ("ocai-cursor-rules-20261008", "ui-ux-pro-max-eski-20261012",
                 "ocai-agent-20261013", "ocai-agent-abcdefgh-ijklmn"):
        check(f"gecersiz: {name}", not delivery.BACKUP_STAMP_RE.match(name))


def test_no_backup_flag_exists():
    print("=== TEST 5: --no-backup bayragi tanimli mi ===")
    parser_source = (ROOT / "delivery.py").read_text(encoding="utf-8")
    check("--no-backuclawragi var", '"--no-backup"' in parser_source)
    check("--keep bayragi var", '"--keep"' in parser_source)
    check("--prune-only bayragi var", '"--prune-only"' in parser_source)
    check("skip_backup parametreye tasindi",
          "def distribute(project: dict, source: Path, config: dict, dry: bool,"
          in parser_source.replace("\n", " ").replace("  ", " ")
          or "skip_backup: bool = False" in parser_source)


def test_create_backup():
    print("=== TEST 6: create_backup hedefte .agent yoksa None doner ===")
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        config = make_config(tmp)
        project = config["projects"][0]

        check("yokken None", delivery.create_backup(tmp / "yok", project, config,
                                                   "20261013-120000") is None)

        agent = tmp / "p1" / ".agent"
        agent.mkdir(parents=True)
        (agent / "AGENTS.md").write_text("x", encoding="utf-8")
        created = delivery.create_backup(agent, project, config, "20261013-120000")
        check("yol dogru",
              created.name == "ocai-agent-20261013-120000", str(created))
        check("icerik kopyalandi", (created / "AGENTS.md").is_file())


def main():
    test_keep_n()
    test_keep_not_enough()
    test_foreign_backups_survive()
    test_stamp_pattern()
    test_no_backup_flag_exists()
    test_create_backup()
    print()
    if failures:
        print(f"SONUC: {len(failures)} BASARISIZ: {failures}")
        return 1
    print("SONUC: tum testler gecti")
    return 0


if __name__ == "__main__":
    sys.exit(main())