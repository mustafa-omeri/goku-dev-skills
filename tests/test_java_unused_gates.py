#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Java/Spring Boot kullanilmayan kod, gereksiz @Autowired ve run_all_gates entegrasyon testleri."""
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = ROOT / ".agent" / "skills" / "musgoku" / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import run_all_gates  # noqa: E402


class TestJavaUnusedGates(unittest.TestCase):
    def test_run_all_gates_executes_check_unused_when_pom_exists(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root = Path(tmp)
            (tmp_root / "pom.xml").write_text("<project/>", encoding="utf-8")
            script_dir = tmp_root / ".agent" / "skills" / "musgoku" / "scripts"
            script_dir.mkdir(parents=True)
            (script_dir / "check-unused.ps1").write_text(
                'Write-Host "[FAIL] 1 kullanilmayan kod"\nexit 1\n',
                encoding="utf-8",
            )

            summary = run_all_gates.run_gates(tmp_root, include_slow=False)
            java_gates = [r for r in summary["results"] if "Java" in r["name"]]
            self.assertTrue(java_gates, "pom.xml varken Java kapisi calismali")
            self.assertEqual(java_gates[0]["status"], "FAIL")
            self.assertEqual(summary["failed_count"], 1)

    def test_run_all_gates_skips_java_gate_without_pom(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root = Path(tmp)
            summary = run_all_gates.run_gates(tmp_root, include_slow=False)
            java_gates = [r for r in summary["results"] if "Java" in r["name"]]
            if java_gates:
                self.assertEqual(java_gates[0]["status"], "SKIPPED")

    def test_run_all_gates_include_slow_runs_mvn_clean_test_compile(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root = Path(tmp)
            (tmp_root / "pom.xml").write_text("<project/>", encoding="utf-8")
            seen_cmds = []

            def fake_run(cmd, cwd=None, capture_output=True, text=True, encoding="utf-8", errors="replace"):
                seen_cmds.append(list(cmd))
                return subprocess.CompletedProcess(cmd, 0, stdout="BUILD SUCCESS", stderr="")

            with mock.patch.object(run_all_gates.subprocess, "run", side_effect=fake_run):
                summary = run_all_gates.run_gates(tmp_root, include_slow=True)

            mvn_cmds = [c for c in seen_cmds if any("mvn" in str(x).lower() for x in c)]
            self.assertTrue(mvn_cmds, "--include-slow pom.xml varken mvn clean test-compile kosturmali")
            self.assertTrue(
                any("test-compile" in " ".join(str(x) for x in c) and "clean" in " ".join(str(x) for x in c) for c in mvn_cmds),
                f"mvn clean test-compile beklenirdi, gorulen: {mvn_cmds}",
            )
            self.assertEqual(summary["failed_count"], 0)

    def test_check_unused_detects_redundant_autowired_unused_test_field_and_dead_class(self):
        pwsh = shutil.which("pwsh")
        if not pwsh:
            self.skipTest("pwsh yuklu degil")

        check_unused = SCRIPTS_DIR / "check-unused.ps1"
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root = Path(tmp)
            (tmp_root / "pom.xml").write_text("<project/>", encoding="utf-8")
            main_pkg = tmp_root / "src" / "main" / "java" / "com" / "example"
            test_pkg = tmp_root / "src" / "test" / "java" / "com" / "example"
            main_pkg.mkdir(parents=True)
            test_pkg.mkdir(parents=True)

            # 1. Gereksiz constructor param @Autowired + kullanilmayan @Slf4j
            (main_pkg / "SampleService.java").write_text(
                """package com.example;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

@Slf4j
@Service
public class SampleService {
    private final HelperBean helper;
    public SampleService(@Autowired HelperBean helper,
                         @Autowired(required = false) OptionalBean opt) {
        this.helper = helper;
    }
    public String run() { return helper.toString(); }
}
""",
                encoding="utf-8",
            )
            # 2. Spring bean referanssiz olsa da olu sinif sayilmamali
            (main_pkg / "HelperBean.java").write_text(
                """package com.example;
import org.springframework.stereotype.Component;
@Component
public class HelperBean {}
""",
                encoding="utf-8",
            )
            (main_pkg / "OptionalBean.java").write_text(
                """package com.example;
public class OptionalBean {}
""",
                encoding="utf-8",
            )
            # 3. Referanssiz olu DTO sinifi (Spring annotation yok, baska dosyada kullanilmiyor)
            (main_pkg / "DeadUnusedDto.java").write_text(
                """package com.example;
public class DeadUnusedDto {
    private String name;
}
""",
                encoding="utf-8",
            )
            # 4. Test sinifinda package-private kullanilmayan @Autowired alani
            (test_pkg / "SampleServiceIT.java").write_text(
                """package com.example;
import org.springframework.beans.factory.annotation.Autowired;
class SampleServiceIT {
    @Autowired
    JdbcTemplate unusedPackagePrivateField;
}
""",
                encoding="utf-8",
            )

            res = subprocess.run(
                [pwsh, "-NoProfile", "-File", str(check_unused), "-StaticOnly", "-ProjectRoot", str(tmp_root)],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
            out = res.stdout + "\n" + res.stderr
            self.assertEqual(res.returncode, 1, f"Bulgu varken exit 1 beklenirdi. Cikti:\n{out}")
            self.assertIn("SampleService.java", out)
            self.assertIn("@Autowired", out)
            self.assertIn("SampleServiceIT.java", out)
            self.assertIn("unusedPackagePrivateField", out)
            self.assertIn("DeadUnusedDto.java", out)
            self.assertIn("@Slf4j", out)
            self.assertNotIn("HelperBean.java", out)

    def test_rules_and_skills_require_mvn_clean_test_compile(self):
        targets = [
            ROOT / ".agent" / "rules" / "no-unused-code.md",
            ROOT / ".agent" / "rules" / "development-workflow.md",
            ROOT / ".agent" / "skills" / "commitx" / "SKILL.md",
        ]
        for path in targets:
            text = path.read_text(encoding="utf-8")
            self.assertNotIn("mvn clean compile -DskipTests", text, f"{path.name} halen testleri atlayan compile yaziyor")
            self.assertIn("test-compile", text, f"{path.name} test-compile icermeli")


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestJavaUnusedGates)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
