#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Walkthrough (.md) arsivleme ve 3 kalite kapisinda zero-false-positive birim testleri."""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJECT_ROOT = HERE.parent
MUSGOKU_SCRIPTS = PROJECT_ROOT / ".agent" / "skills" / "musgoku" / "scripts"
if str(MUSGOKU_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(MUSGOKU_SCRIPTS))

import archive_plan  # noqa: E402
import check_aviation_docs  # noqa: E402
import check_handoff  # noqa: E402
import plan_conflict_guard  # noqa: E402


class TestWalkthroughArchive(unittest.TestCase):
    def test_archive_walkthrough_with_for_plan_uses_same_stem_suffix(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            plan_dir = root / "docs" / "plans"
            plan_dir.mkdir(parents=True)
            archived_plan = plan_dir / "council_plan_auth_20261124_120000.md"
            archived_plan.write_text("# Plan\n- Task: AUTH-001, AUTH-002\n", encoding="utf-8")

            src_wt = root / "brain_walkthrough.md"
            src_wt.write_text("# Walkthrough\n- Completed AUTH-001, AUTH-002\n", encoding="utf-8")

            dest = archive_plan.archive_walkthrough(
                walkthrough_path=src_wt,
                project_root=root,
                for_plan=archived_plan,
            )
            self.assertEqual(dest, plan_dir / "council_plan_auth_20261124_120000_walkthrough.md")
            self.assertTrue(dest.is_file())
            self.assertTrue(src_wt.is_file())  # move=False kaynak dosyayi korur

    def test_archive_walkthrough_for_sprint_uses_walkthrough_subdir(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            src_wt = root / "walkthrough.md"
            src_wt.write_text("# Sprint 21 Walkthrough\nAll done.\n", encoding="utf-8")

            dest = archive_plan.archive_walkthrough(
                walkthrough_path=src_wt,
                project_root=root,
                slug="sprint-21",
                subdir=True,
            )
            self.assertEqual(dest.parent, root / "docs" / "plans" / "walkthrough")
            self.assertRegex(dest.name, r"^sprint-21_\d{8}_\d{6}_walkthrough\.md$")
            self.assertTrue(dest.is_file())

    def test_gates_ignore_walkthrough_files_no_false_positives(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "package.json").write_text('{"name": "demo"}', encoding="utf-8")
            (root / "HANDOFF.md").write_text(
                "# HANDOFF\n\n## 1. Özet\nTamam.\n\n## 2. Kanıt\n1/1 PASS\n\n## 3. ⏭️ BURADAN DEVAM ET\n"
                "#### 🎯 Aktif Sprint / Anlık Görev Panosu (WIP Maks 3)\n| ID | Durum | İş | Ref | Sürüm |\n|---|---|---|---|---|\n| — | — | Yok | — | — |\n",
                encoding="utf-8",
            )
            wt_dir = root / "docs" / "plans" / "walkthrough"
            wt_dir.mkdir(parents=True)
            wt1 = root / "docs" / "plans" / "plan_demo_20261124_120000_walkthrough.md"
            wt1.write_text(
                "# Walkthrough\n1. Ran test\n#### [NEW] `src/pages/DemoPage.tsx`\n- AUTH-001, AUTH-002 done.\n",
                encoding="utf-8",
            )
            wt2 = wt_dir / "sprint_21_20261124_120000_walkthrough.md"
            wt2.write_text("# Sprint Walkthrough\n1. Step without emergency table.\n", encoding="utf-8")

            eviction_warnings = check_handoff._check_plan_eviction(root, (root / "HANDOFF.md").read_text(encoding="utf-8"))
            self.assertEqual(eviction_warnings, [])

            q_data = plan_conflict_guard._collect_queued_plans_and_backlog(root)
            self.assertEqual(q_data["checked_plans"] if "checked_plans" in q_data else q_data["queued_plans"], [])

            errs1, _ = check_aviation_docs.check_file(wt1)
            errs2, _ = check_aviation_docs.check_file(wt2)
            self.assertEqual(errs1, [])
            self.assertEqual(errs2, [])

    def test_cli_archive_plan_walkthrough_flag(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "docs" / "plans").mkdir(parents=True)
            plan_p = root / "docs" / "plans" / "plan_login_20261124_100000.md"
            plan_p.write_text("# Plan\n", encoding="utf-8")
            wt_p = root / "walkthrough.md"
            wt_p.write_text("# Walkthrough\nDone.\n", encoding="utf-8")

            res = subprocess.run(
                [
                    sys.executable,
                    str(MUSGOKU_SCRIPTS / "archive_plan.py"),
                    "--plan", str(wt_p),
                    "--walkthrough",
                    "--for-plan", str(plan_p),
                    "--root", str(root),
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
            )
            self.assertEqual(res.returncode, 0, msg=res.stderr)
            self.assertTrue((root / "docs" / "plans" / "plan_login_20261124_100000_walkthrough.md").is_file())


if __name__ == "__main__":
    unittest.main(verbosity=2)
