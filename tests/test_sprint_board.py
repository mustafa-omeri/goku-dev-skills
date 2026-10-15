#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""check_sprint_board.py kapisinin regresyon testi.

Kapsam:
  1. Gercek depo temiz mi?      (bu deponun kendi SPRINT_PLAN/KANBAN'i)
  2. Gecersiz fixture yakalanir mi?   (E1..E11)
  3. **Gecerli** fixture kirmizi aliyor mu?   (yanlis pozitif kontrolu)

Ucuncu bolum olmadan bu birim testi sadece "kirmizi isik yandi" demek olur.
Bir dogrulayici gecerli bir projeyi reddederse ajan onu susturur ve kapi
degerini kaybeder (2026-10-13 dersi: "uyari guvenilirligi her katmanda gecerli").
"""
import sys
import tempfile
from pathlib import Path

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / ".agent" / "skills" / "musgoku" / "scripts"
sys.path.insert(0, str(SCRIPTS))

import check_sprint_board as gate  # noqa: E402

failures = []


def check(label, condition, detail=""):
    print(f"  {'PASS' if condition else 'FAIL'}  {label}" + (f"  -- {detail}" if detail else ""))
    if not condition:
        failures.append(label)


def codes(entries):
    return {code for code, _name, _message in entries}


# --- fixture --------------------------------------------------------------------

GOOD_FEATURE = """# language: tr
Feature: Ornek

  Scenario: Kart bittigi zaman kapi yesil olur
    Given kanban dosyasi hazir
    When kapı çalıştırılır
    Then sifir hata doner
"""

GOOD_SPRINT = """# SPRINT_PLAN.md

## Sprint 1

### Hedef

**Hedef:** kapinin yesil olmasi

### MVP Kapsam
- S1-01 — ornek kart

### Kapsam Dışı
- S1-09 — ornek tasima
"""


def good_card(card_id="S1-01", column="Yapıldı", spec="specs/S1-01.feature",
              test="Kullanıcı kapıyı koşar, 9 kart görür ve SONUC: 1 kart · [OK] yazar"):
    return f"""### {card_id} · Örnek kart
| alan | değer |
|---|---|
| durum | {column} |
| oncelik | P1 |
| sprint | S1 |
| gherkin | {spec} |
| kapi | python .agent/skills/musgoku/scripts/check_sprint_board.py |
| test | {test} |
| risk | düşük |
"""


def make_project(tmp: Path, cards: dict, sprint=GOOD_SPRINT, release=None,
                 write_sprint=True, write_board=True):
    (tmp / "specs").mkdir(parents=True, exist_ok=True)
    (tmp / "specs" / "S1-01.feature").write_text(GOOD_FEATURE, encoding="utf-8")
    if write_sprint:
        (tmp / "SPRINT_PLAN.md").write_text(sprint, encoding="utf-8")
    if write_board:
        body = "\n".join(f"## {name}\n\n{cards.get(name, '')}\n"
                         for name in gate.COLUMNS)
        (tmp / "KANBAN.md").write_text(body, encoding="utf-8")
    if release is not None:
        (tmp / "RELEASE_PLAN.md").write_text(release, encoding="utf-8")
    return tmp


def run(tmp: Path, wip=3):
    return gate.check(tmp, wip_limit=wip)


# --- 1. gercek depo --------------------------------------------------------------

def test_real_repo_is_clean():
    print("=== TEST 1: bu deponun sprint belgeleri kapiyi gecmesi ===")
    errors, warnings, stats = gate.check(ROOT)
    check("kapı kapsam disi degil", stats["scope"] == "denetlendi", stats["scope"])
    check("sprint kapisi hata yok", not errors,
          "; ".join(f"{c} {n}: {m}" for c, n, m in errors[:3]))
    check("sprint kapisi uyari yok", not warnings,
          "; ".join(f"{c} {n}" for c, n, _m in warnings[:3]))
    check("kart sayisi beklenen", stats["cards"] >= 5, f"{stats['cards']} kart")
    check("acik kart release planinda", stats["open"] >= 1,
          f"{stats['open']} acik kart")


# --- 2. gecersiz fixture --------------------------------------------------------

def test_invalid_is_caught():
    print("=== TEST 2: gecersiz girdi yakalaniyor mu ===")

    # E1 plan dosyalari eksik
    with tempfile.TemporaryDirectory() as d:
        tmp = make_project(Path(d), {}, write_sprint=False)
        errors, _w, _s = run(tmp)
        check("E1 plan dosyasi eksik", "E1" in codes(errors), str(sorted(codes(errors))))

    # E2 sprint plani bicimi bozuk
    with tempfile.TemporaryDirectory() as d:
        tmp = make_project(Path(d), {"Yapıldı": good_card()},
                           sprint="# SPRINT\n\nHicbir baslik yok.\n")
        errors, _w, _s = run(tmp)
        check("E2 sprint plani bicimi", "E2" in codes(errors), str(sorted(codes(errors))))

    # E3 taninmayan sutun
    with tempfile.TemporaryDirectory() as d:
        tmp = make_project(Path(d), {"Yapıldı": good_card()})
        text = (tmp / "KANBAN.md").read_text(encoding="utf-8")
        (tmp / "KANBAN.md").write_text(text + "\n## Blocked\n\n### S1-05 · takili\n",
                                       encoding="utf-8")
        errors, _w, _s = run(tmp)
        check("E3 taninmayan sutun", "E3" in codes(errors), str(sorted(codes(errors))))

    # E4 bozuk kart basligi
    with tempfile.TemporaryDirectory() as d:
        tmp = make_project(Path(d), {"Yapıldı": "### kart basligi kipi yok\n"})
        errors, _w, _s = run(tmp)
        check("E4 bozuk kart basligi", "E4" in codes(errors), str(sorted(codes(errors))))

    # E4 yinelenen kart id
    with tempfile.TemporaryDirectory() as d:
        card = good_card(spec="specs/S1-01.feature", test="çıktı 3 kart görür")
        tmp = make_project(Path(d), {"Yapıldı": card, "Bekliyor": card})
        errors, _w, _s = run(tmp)
        check("E4 yinelenen kart id", "E4" in codes(errors), str(sorted(codes(errors))))

    # E5 zorunlu alan eksik
    with tempfile.TemporaryDirectory() as d:
        broken = good_card().replace("| risk | düşük |\n", "")
        tmp = make_project(Path(d), {"Yapıldı": broken})
        errors, _w, _s = run(tmp)
        check("E5 zorunlu alan eksik", "E5" in codes(errors), str(sorted(codes(errors))))

    # E5 durum sutunla tutarsiz
    with tempfile.TemporaryDirectory() as d:
        bad = good_card().replace("| durum | Yapıldı |", "| durum | Bekliyor |")
        tmp = make_project(Path(d), {"Yapıldı": bad})
        errors, _w, _s = run(tmp)
        check("E5 durum sutunla tutarsiz", "E5" in codes(errors), str(sorted(codes(errors))))

    # E6 gherkin dosyasi yok
    with tempfile.TemporaryDirectory() as d:
        tmp = make_project(Path(d), {"Yapıldı": good_card(spec="specs/olmayan.feature")})
        errors, _w, _s = run(tmp)
        check("E6 gherkin dosyasi yok", "E6" in codes(errors), str(sorted(codes(errors))))

    # E7 gherkin icerigi eksik
    with tempfile.TemporaryDirectory() as d:
        tmp = make_project(Path(d), {"Yapıldı": good_card()})
        (tmp / "specs" / "S1-01.feature").write_text(
            "# language: tr\nFeature: Ornek\n\n  Yalniz metin, adim yok.\n", encoding="utf-8")
        errors, _w, _s = run(tmp)
        check("E7 gherkin icerigi eksik", "E7" in codes(errors), str(sorted(codes(errors))))

    # E8 Yapildi kartinda kullanici testi yok
    with tempfile.TemporaryDirectory() as d:
        tmp = make_project(Path(d), {"Yapıldı": good_card(test="yazılacak")})
        errors, _w, _s = run(tmp)
        check("E8 kullanici testi yok", "E8" in codes(errors), str(sorted(codes(errors))))

    # E9 bos kapi alani
    with tempfile.TemporaryDirectory() as d:
        bad = good_card().replace(
            "| kapi | python .agent/skills/musgoku/scripts/check_sprint_board.py |",
            "| kapi | |")
        tmp = make_project(Path(d), {"Yapıldı": bad})
        errors, _w, _s = run(tmp)
        check("E9 kapi alani bos", "E9" in codes(errors), str(sorted(codes(errors))))

    # E10 release plani kapanmamis karti tasimiyor
    with tempfile.TemporaryDirectory() as d:
        tmp = make_project(Path(d), {"Yapıldı": good_card(),
                                     "Bekliyor": good_card("S1-07", "Bekliyor")},
                           release="# RELEASE_PLAN\n\nTasma yok.\n")
        errors, _w, _s = run(tmp)
        check("E10 release plani tasimiyor", "E10" in codes(errors), str(sorted(codes(errors))))

    # E11 WIP limiti
    with tempfile.TemporaryDirectory() as d:
        tmp = make_project(Path(d), {"Yapılıyor": good_card("S1-01", "Yapılıyor",
                                                             "specs/S1-01.feature",
                                                             "ara çıktı 1 kart")})
        errors, _w, _s = run(tmp, wip=0)
        check("E11 WIP limiti", "E11" in codes(errors), str(sorted(codes(errors))))


# --- 3. gecerli fixture ---------------------------------------------------------

def test_valid_is_accepted():
    print("=== TEST 3: gecerli girdi kirmizi ALMAMALI ===")

    # Plan dosyalari hic yok -> kapsam disi, exit 0
    with tempfile.TemporaryDirectory() as d:
        tmp = Path(d)
        errors, _w, stats = run(tmp)
        check("kapsam disi kabul", not errors and stats["scope"] == "yok",
              f"scope={stats['scope']}")

    # Temiz proje -> sifir hata
    with tempfile.TemporaryDirectory() as d:
        tmp = make_project(Path(d), {"Yapıldı": good_card()})
        errors, warnings, stats = run(tmp)
        check("temiz proje hatasiz", not errors,
              "; ".join(f"{c}: {m}" for c, _n, m in errors[:3]))
        check("temiz proje uyarisiz", not warnings,
              "; ".join(f"{c}: {m}" for c, _n, m in warnings[:3]))
        check("kart sayisi 1", stats["cards"] == 1, str(stats))

    # Acik kart release planinda tasinmis -> kabul
    with tempfile.TemporaryDirectory() as d:
        tmp = make_project(
            Path(d),
            {"Yapıldı": good_card(),
             "Bekliyor": good_card("S1-07", "Bekliyor", "specs/S1-01.feature",
                                    "(yazılacak)")},
            release="# RELEASE_PLAN\n\n| S1-07 | neden | S2 | düşük |\n")
        errors, _w, _s = run(tmp)
        check("tasinmis acik kart kabul", not errors,
              "; ".join(f"{c}: {m}" for c, _n, m in errors[:3]))

    # Turkce senaryo basligi, ASCII kebab-case baglanti ile eslesir
    with tempfile.TemporaryDirectory() as d:
        tmp = make_project(
            Path(d),
            {"Yapıldı": good_card(spec="specs/S1-01.feature#kart-bittigi-zaman-kapi-yesil-olur")})
        errors, _w, _s = run(tmp)
        check("TR senaryo basligi + ASCII baglanti", not errors,
              "; ".join(f"{c}: {m}" for c, _n, m in errors[:3]))

    # WIP limiti tam sinirda -> kabul
    with tempfile.TemporaryDirectory() as d:
        tmp = make_project(Path(d), {"Yapılıyor": good_card("S1-01", "Yapılıyor",
                                                             "specs/S1-01.feature",
                                                             "ara çıktı 1 kart")},
                           release="# RELEASE_PLAN\n\n| S1-01 | neden | S2 | düşük |\n")
        errors, _w, stats = run(tmp, wip=1)
        check("WIP tam sinirda kabul", not errors and stats["wip"] == 1,
              "; ".join(f"{c}: {m}" for c, _n, m in errors[:2]))


# --- 4. uyari seviyesi ----------------------------------------------------------

def test_warnings_do_not_fail():
    print("=== TEST 4: uyarilar kapiyi kirmizi YAPMAMALI ===")

    # Gecersiz oncelik ve risk -> uyari, hata degil
    with tempfile.TemporaryDirectory() as d:
        bad = (good_card()
               .replace("| oncelik | P1 |", "| oncelik | P9 |")
               .replace("| risk | düşük |", "| risk | belirsiz |"))
        tmp = make_project(Path(d), {"Yapıldı": bad})
        errors, warnings, _s = run(tmp)
        check("W1 oncelik uyarisi", "W1" in codes(warnings), str(sorted(codes(warnings))))
        check("W2 risk uyarisi", "W2" in codes(warnings), str(sorted(codes(warnings))))
        check("uyari hata degil", not errors, str(sorted(codes(errors))))

    # MVP kapsaminda gecmeyen kart -> W3
    with tempfile.TemporaryDirectory() as d:
        tmp = make_project(Path(d), {"Yapıldı": good_card("S1-42")},
                           sprint="# SPRINT\n\n## Sprint 1\n\n**Hedef:** x\n\n"
                                  "**MVP Kapsam**\n- S1-01 — a\n\n**Kapsam Dışı**\n- S1-09 — b\n")
        _errors, warnings, _s = run(tmp)
        check("W3 MVP disi kart", "W3" in codes(warnings), str(sorted(codes(warnings))))


def main():
    print("=" * 60)
    print("check_sprint_board.py Kapi Testi")
    print("=" * 60)
    test_real_repo_is_clean()
    test_invalid_is_caught()
    test_valid_is_accepted()
    test_warnings_do_not_fail()

    print("\n" + "=" * 60)
    if failures:
        print(f"SONUC: {len(failures)} KONTROL BASARISIZ")
        for f in failures:
            print(f"  - {f}")
        return 1
    print("SONUC: TUM KONTROLLER PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())