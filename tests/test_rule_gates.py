#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Kural sinifi / kapi denetleyicilerinin regresyon testi.

Kapsam:
  1. Gercek depo temiz mi?        (rules_gates, check_design_skills, check_api_docs)
  2. Uretilen tablolar bayat mi?  (drift testi)
  3. Her hata kodu gercekten tetikleniyor mu?  (gectersiz fixture)

Ikinci bolum olmadan bu birim testi sadece "kirmizi isik yandi" demek olur.
Bir dogrulayici yanlis pozitif uretiyorsa ajan onu susturur ve kapi degerini
kaybeder (2026-10-13 dersi: "uyari guvenilirligi her katmanda gecerli").
"""
import sys
import tempfile
import json
from pathlib import Path

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / ".agent" / "skills" / "musgoku" / "scripts"
sys.path.insert(0, str(SCRIPTS))

import check_api_docs  # noqa: E402
import check_design_skills  # noqa: E402
import check_vite_spa  # noqa: E402
import rules_gates  # noqa: E402

RULES = ROOT / ".agent" / "rules"
AGENTS = ROOT / ".agent" / "AGENTS.md"
WORKFLOW = RULES / "development-workflow.md"

failures = []


def check(label, condition, detail=""):
    print(f"  {'PASS' if condition else 'FAIL'}  {label}" + (f"  -- {detail}" if detail else ""))
    if not condition:
        failures.append(label)


def codes(entries):
    return {code for code, _name, _message in entries}


# --- 1. gercek depo ------------------------------------------------------------

def test_repo_is_clean():
    print("=== TEST 1: gercek depo kurallari temiz mi ===")
    errors, warnings = rules_gates.validate(RULES, AGENTS, WORKFLOW, ROOT)
    check("rules_gates hata yok", not errors, "; ".join(f"{c} {n}" for c, n, _ in errors[:4]))
    check("rules_gates uyari yok", not warnings,
          "; ".join(f"{c} {n}" for c, n, _ in warnings[:4]))

    rules = rules_gates.collect_rules(RULES)
    check("20 kural dosyasi", len(rules) == 20, f"{len(rules)} bulundu")
    check("her kural sinif bildiriyor", all(r.sinif for r in rules))
    measurable = [r for r in rules if r.sinif == "OLCULEBILIR"]
    check("olculebilir kuralin kapisi var",
          all(r.gates for r in measurable), f"{len(measurable)} olculebilir kural")
    check("olculebilir olmayan kuralin kapisi yok",
          all(not r.gates for r in rules if r.sinif != "OLCULEBILIR"))

    design_errors, design_warnings, rows = check_design_skills.check(ROOT)
    check("sahiplik tablosu hatasiz", not design_errors,
          "; ".join(f"{c} {m}" for c, _n, m in design_errors[:3]))
    check("sahiplik tablosu dolu", rows >= 10, f"{rows} satir")


def test_generated_tables_match():
    print("=== TEST 2: uretilen tablolar kaynakla ayni mi ===")
    rules = rules_gates.collect_rules(RULES)
    for path, prefix in ((AGENTS, "rules/"), (WORKFLOW, "./")):
        expected = rules_gates.render_table(rules, prefix)
        found = rules_gates.extract_table(path.read_text(encoding="utf-8"))
        check(f"{path.name} tablosu guncel", found == expected,
              "bayat" if found is not None else "isaret yok")

    attitude = rules_gates.render_attitude_list(rules)
    text = AGENTS.read_text(encoding="utf-8")
    start = text.index("### 3.2")
    body = text[start:text.index("⛔ **Bir şeyi doğrulamadıysan", start)]
    check("AGENTS.md kapisiz kural listesi guncel", attitude in body)


# --- 2. gecersiz fixture -------------------------------------------------------

GOOD_RULE = """---
name: Ornek Kural
description: Test icin gecerli kural.
sinif: OLCULEBILIR
kapi:
  - yigin: "Test / ornek"
    komut: "python .agent/skills/ornek/scripts/kapi.py"
---

# Ornek

Govde metni.
"""


def make_project(tmp: Path, rule_text: str) -> Path:
    rules_dir = tmp / ".agent" / "rules"
    rules_dir.mkdir(parents=True)
    (tmp / ".agent" / "skills" / "ornek" / "scripts").mkdir(parents=True)
    (tmp / ".agent" / "skills" / "ornek" / "scripts" / "kapi.py").write_text(
        "# ornek kapi\n", encoding="utf-8")
    (rules_dir / "ornek.md").write_text(rule_text, encoding="utf-8")
    return rules_dir


def run_validate(tmp: Path, rule_text: str):
    rules_dir = make_project(tmp, rule_text)
    agents = tmp / ".agent" / "AGENTS.md"
    workflow = rules_dir / "ornek.md"
    agents.write_text(f"AGENTS\n\n{rules_gates.BEGIN_MARK}\n|rules|\n"
                      f"{rules_gates.END_MARK}\n", encoding="utf-8")
    return rules_gates.validate(rules_dir, agents, workflow, tmp,
                                check_tables=False)


def expect(label, rule_text, code):
    with tempfile.TemporaryDirectory() as tmpdir:
        errors, warnings = run_validate(Path(tmpdir), rule_text)
        found = codes(errors) | codes(warnings)
        check(label, code in found, f"beklenen {code}, gelen {sorted(found) or 'yok'}")


def test_invalid_rules_are_caught():
    print("=== TEST 3: her hata kodu gercekten tetikleniyor mu ===")
    expect("E1 sinif bildirilmemis", GOOD_RULE.replace("sinif: OLCULEBILIR\n", ""), "E1")
    expect("E2 gecersiz sinif",
           GOOD_RULE.replace("sinif: OLCULEBILIR", "sinif: ZORUNLU"), "E2")
    expect("E3 olculebilir ama kapisiz",
           GOOD_RULE.split("kapi:")[0] + "---\n\n# Ornek\n", "E3")
    expect("E4 olmayan script yolu",
           GOOD_RULE.replace("ornek/scripts/kapi.py", "olmayan/scripts/kapi.py"), "E4")
    expect("E5 tutum ama kapi tanimli",
           GOOD_RULE.replace("sinif: OLCULEBILIR", "sinif: TUTUM"), "E5")
    expect("E6 bos kapi girdisi",
           GOOD_RULE.replace('komut: "python .agent/skills/ornek/scripts/kapi.py"',
                             'komut: ""'), "E6")
    expect("W1 tutum kurali govdede script yolu gostermeli degil",
           "---\nname: X\ndescription: d\nsinif: TUTUM\n---\n\n"
           "Govde: python .agent/skills/ornek/scripts/kapi.py calistirilir.\n", "W1")


def test_stale_table_is_caught():
    print("=== TEST 4: bayat tablo hata olarak raporlaniyor mu ===")
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        rules_dir = make_project(tmp, GOOD_RULE)
        agents = tmp / ".agent" / "AGENTS.md"
        workflow = tmp / "workflow-fixture.md"
        workflow.write_text("", encoding="utf-8")
        stale = (f"{rules_gates.BEGIN_MARK}\n| bayat | tablo |\n{rules_gates.END_MARK}")
        agents.write_text(stale, encoding="utf-8")
        errors, _warnings = rules_gates.validate(rules_dir, agents, workflow, tmp)
        check("E7 bayat AGENTS.md tablosu", "E7" in codes(errors))

        workflow.write_text(
            f"{rules_gates.BEGIN_MARK}\n"
            f"{rules_gates.render_table(rules_gates.collect_rules(rules_dir), './')}\n"
            f"{rules_gates.END_MARK}", encoding="utf-8")
        agents.write_text(
            f"{rules_gates.BEGIN_MARK}\n"
            f"{rules_gates.render_table(rules_gates.collect_rules(rules_dir), 'rules/')}\n"
            f"{rules_gates.END_MARK}", encoding="utf-8")
        errors, _warnings = rules_gates.validate(rules_dir, agents, workflow, tmp)
        check("guncel tablo hata uretmiyor", not errors,
              "; ".join(f"{c} {n}" for c, n, _ in errors[:3]))


# --- 3. design ownership -------------------------------------------------------

def test_design_ownership_violations():
    print("=== TEST 5: sahiplik celiskisi yakalaniyor mu ===")
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        rule = tmp / ".agent" / "rules" / "design-skills-enforcement.md"
        rule.parent.mkdir(parents=True)
        for skill in ("canvas-design", "frontend-design", "ui-ux-pro-max",
                      "design-system"):
            (tmp / ".agent" / "skills" / skill).mkdir(parents=True)

        base = ("---\nname: D\ndescription: d\nsinif: OLCULEBILIR\n---\n\n"
                "## 3. Sahiplik haritasi\n\n"
                "| Konu | Sahip skill |\n|---|---|\n"
                "| Palet | `ui-ux-pro-max` |\n"
                "| Sunum | `design-system` |\n"
                "| Cizgi kalitesi | `canvas-design` |\n"
                "| Tipografi | `frontend-design` |\n\n")

        rule.write_text(base, encoding="utf-8")
        errors, _warnings, rows = check_design_skills.check(tmp)
        check("gecerli tablo kabul edildi", not errors and rows == 4,
              "; ".join(m for _c, _n, m in errors[:3]))

        rule.write_text(base + "| Palet | `theme-factory` |\n", encoding="utf-8")
        errors, _warnings, _rows = check_design_skills.check(tmp)
        check("D2 ayni konu iki sahip", "D2" in codes(errors))

        rule.write_text(base.replace("| Sunum | `design-system` |",
                                     "| Sunum | `olmayan-skill` |"), encoding="utf-8")
        errors, _warnings, _rows = check_design_skills.check(tmp)
        check("D3 diskte olmayan skill", "D3" in codes(errors))

        rule.write_text(base.replace("## 3. Sahiplik haritasi", "## 4. Başka"),
                        encoding="utf-8")
        errors, _warnings, _rows = check_design_skills.check(tmp)
        check("D1 tablo basligi kayboldu", "D1" in codes(errors))


# --- 4. api docs ---------------------------------------------------------------

CONTROLLER = """package a;

@RestController
@RequestMapping({ "/v1/thing", "/api/v1/thing" })
public class ThingController {
    @GetMapping("/{id}")
    public String get() { return ""; }

    @PostMapping("")
    public String create() { return ""; }
}
"""


def make_java_project(tmp: Path, doc: str = "") -> Path:
    java = tmp / "src" / "main" / "java" / "a"
    java.mkdir(parents=True)
    (java / "ThingController.java").write_text(CONTROLLER, encoding="utf-8")
    if doc is not None:
        docs = tmp / "docs" / "APIs"
        docs.mkdir(parents=True)
        (docs / "thing.md").write_text(doc, encoding="utf-8")
    return tmp


def test_api_docs_violations():
    print("=== TEST 6: API dokumantasyonu kapisi ===")
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = make_java_project(Path(tmpdir), doc=None)
        errors, _warnings, stats = check_api_docs.check(tmp)
        check("E2 docs/APIs dizini yok", "E2" in codes(errors))
        check("endpoint sayisi dogru", stats["endpoints"] == 2, str(stats["endpoints"]))

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = make_java_project(Path(tmpdir),
                                doc="- **URL:** `/api/v1/thing/{id}`\n- **Method:** GET\n")
        errors, _warnings, _stats = check_api_docs.check(tmp)
        check("ayri satirli format tanindi, POST eksik", "E1" in codes(errors),
              "; ".join(m for _c, _n, m in errors[:2]))

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = make_java_project(Path(tmpdir),
                                doc="- **URL:** `/api/v1/thing/{id}`\n- **Method:** GET\n"
                                    "- **URL:** `/api/v1/thing`\n- **Method:** POST\n")
        errors, warnings, _stats = check_api_docs.check(tmp)
        check("alias (/v1 ve /api/v1) tek sayildi", not errors,
              "; ".join(m for _c, _n, m in errors[:2]))
        check("@Operation uyarisi ozet olarak tek satir", len(warnings) <= 2,
              f"{len(warnings)} uyari")

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = make_java_project(Path(tmpdir), doc="GET /api/v1/thing/42\n")
        errors, _warnings, _stats = check_api_docs.check(tmp)
        check("satir ici format tanindi", "E1" in codes(errors),
              "POST belgelenmemis olmali")


def make_vite_project(tmp: Path, next_dep=False, files=None) -> Path:
    deps = {"react": "^19.0.0", "react-router-dom": "^7.0.0"}
    if next_dep:
        deps["next"] = "^15.0.0"
    else:
        deps["vite"] = "^6.0.0"
    (tmp / "package.json").write_text(
        json.dumps({"name": "x", "dependencies": deps}), encoding="utf-8")
    src = tmp / "src"
    src.mkdir(parents=True, exist_ok=True)
    for name, body in (files or {"App.tsx": "export const App = () => null;\n"}).items():
        (src / name).write_text(body, encoding="utf-8")
    return tmp


def test_vite_spa_gate():
    print("=== TEST 7: Vite SPA kapisi ===")
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = make_vite_project(Path(tmpdir))
        errors, warnings, stats = check_vite_spa.check(tmp)
        check("temiz Vite projesi kabul", not errors and stats["stack"] == "vite",
              "; ".join(m for _c, _n, m in errors[:2]))

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = make_vite_project(Path(tmpdir), files={
            "App.tsx": 'import Link from "next/link";\nexport const A = () => <Link/>;\n'})
        errors, _w, _s = check_vite_spa.check(tmp)
        check("E3 next/ importu", "E3" in codes(errors))

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = make_vite_project(Path(tmpdir), files={
            "App.tsx": '"use client";\nexport const A = () => null;\n'})
        errors, _w, _s = check_vite_spa.check(tmp)
        check("E4 use client direktifi", "E4" in codes(errors))

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = make_vite_project(Path(tmpdir))
        (tmp / "next.config.ts").write_text("export default {};", encoding="utf-8")
        errors, _w, _s = check_vite_spa.check(tmp)
        check("E2 next.config dosyasi", "E2" in codes(errors))

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = make_vite_project(Path(tmpdir), next_dep=True)
        errors, _w, stats = check_vite_spa.check(tmp)
        check("Next.js projesi kapsam disi", not errors and stats["stack"] == "next")

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = make_vite_project(Path(tmpdir), files={
            "App.tsx": "export const A = () => import.meta.env.VITE_X;\n",
            "util.test.ts": "process.env.FOO = 1;\n"})
        errors, warnings, _s = check_vite_spa.check(tmp)
        check("W1 yalniz uyari, kapiyi kirmaz", not errors and not warnings,
              "; ".join(f"{c} {n}" for c, n, _ in warnings[:2]))

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = make_vite_project(Path(tmpdir), files={
            "App.tsx": "export const A = () => process.env.VITE_X;\n"})
        errors, warnings, _s = check_vite_spa.check(tmp)
        check("W1 process.env yakalandi", "W1" in codes(warnings) and not errors)


def test_w1_canary_on_real_rule():
    """W1 uyarisi gercek kural dosyasinda da tutuyor mu?

    Fixture ile test yeterli degil: 2026-10-13'te W1 yalniz fixture'da
    tetikleniyordu, gercek depoda hicbir kural bu duruma dusmuyordu.
    Bu test gercek kural dosyasini GECICI olarak bozar, kapıyı kosturur ve
    geri alir. Kanıt: gate, kural seti üzerinde calisiyor.
    """
    print("=== TEST 8: W1 gercek kural dosyasinda tutuyor mu ===")
    target = RULES / "no-silent-wait.md"
    original = target.read_text(encoding="utf-8")
    anchor = "## Proje Bazlı Ek Kurallar"
    injected = original.replace(
        anchor,
        "python .agent/skills/musgoku/scripts/check-unused.ps1\n\n" + anchor,
        1)
    check(" enjeksiyon metni bulundu", injected != original)
    if injected == original:
        return
    try:
        target.write_text(injected, encoding="utf-8")
        # Tablo drift'i bu testin konusu degil (TEST 2 bakıyor); kapıyı
        # sadece kural sinfi tarafında ölç.
        errors, warnings = rules_gates.validate(RULES, AGENTS, WORKFLOW, ROOT,
                                                check_tables=False)
        hit = [f"{c} {n}" for c, n, _ in warnings if c == "W1"]
        check("W1 gercek dosyada uyari uretti", bool(hit), "; ".join(hit) or "uyari yok")
        check("W1 kapiyi kirmadi (hata degil)", "W1" not in codes(errors),
              "; ".join(f"{c} {n}" for c, n, _ in errors[:2]))
    finally:
        target.write_text(original, encoding="utf-8")

    errors, warnings = rules_gates.validate(RULES, AGENTS, WORKFLOW, ROOT)
    check("geri alma sonrasi depo temiz", not errors and not warnings)


def main():
    test_repo_is_clean()
    test_generated_tables_match()
    test_invalid_rules_are_caught()
    test_stale_table_is_caught()
    test_design_ownership_violations()
    test_api_docs_violations()
    test_vite_spa_gate()
    test_w1_canary_on_real_rule()

    print()
    if failures:
        print(f"SONUC: {len(failures)} BASARISIZ: {failures}")
        return 1
    print("SONUC: tum testler gecti")
    return 0


if __name__ == "__main__":
    sys.exit(main())