#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Unit tests for summarize_project.py with Dynamic RFC/PRD Discovery and Project Description."""

import tempfile
import unittest
from pathlib import Path

import sys
SCRIPTS_DIR = Path(__file__).resolve().parent.parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from summarize_project import (
    find_all_prds,
    find_all_rfcs,
    get_project_description,
    run_summary,
)


class TestSummarizeProject(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)

        # Temel docs/ dizini
        (self.root / "docs").mkdir(parents=True)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_find_all_rfcs_and_prds_in_root_rfcs(self):
        # 1. Kök dizinde RFCs/ klasörü
        rfcs_dir = self.root / "RFCs"
        rfcs_dir.mkdir(parents=True)
        (rfcs_dir / "RFC-001-Core.md").write_text("# RFC 001", encoding="utf-8")
        (rfcs_dir / "PRD-Auth-Module.md").write_text("# PRD Auth", encoding="utf-8")

        # 2. Kökte PRD.md
        (self.root / "PRD.md").write_text("# Main PRD", encoding="utf-8")

        discovered_rfcs = find_all_rfcs(self.root)
        self.assertEqual(len(discovered_rfcs), 1)
        self.assertEqual(discovered_rfcs[0].name, "RFC-001-Core.md")

        discovered_prds = find_all_prds(self.root)
        self.assertEqual(len(discovered_prds), 2)
        prd_names = [p.name for p in discovered_prds]
        self.assertIn("PRD-Auth-Module.md", prd_names)
        self.assertIn("PRD.md", prd_names)

    def test_project_description_extraction(self):
        brief = self.root / "PROJECT_BRIEF.md"
        brief.write_text(
            """---
title: "Sample Project"
description: "Bu proje yapay zeka destekli otonom bir test platformudur."
slug: "SAMPLE_APP"
---
# Sample
""",
            encoding="utf-8",
        )

        refs = {"brief": brief}
        desc = get_project_description(self.root, refs, "SAMPLE_APP")
        self.assertEqual(desc, "Bu proje yapay zeka destekli otonom bir test platformudur.")

    def test_run_summary_generates_documents_with_description_and_rfcs(self):
        # Setup files
        brief = self.root / "PROJECT_BRIEF.md"
        brief.write_text(
            """---
title: "Test Platform"
description: "Modern mikroservis orkestrasyon motoru."
slug: "TEST_PLATFORM"
primary_language: "tr"
related_docs: []
---
## 1. Teknoloji Yığını
- Java 21, Spring Boot
""",
            encoding="utf-8",
        )

        rfcs_dir = self.root / "RFCs"
        rfcs_dir.mkdir(parents=True)
        (rfcs_dir / "RFC-001-Ingestion.md").write_text("# RFC 001\nData Ingestion Spec", encoding="utf-8")

        # Run short summary
        ret_short = run_summary(mode="short", root=self.root)
        self.assertEqual(ret_short, 0)
        short_file = self.root / "docs" / "TEST_PLATFORM_PROJECT_SUMMARY_SHORT.md"
        self.assertTrue(short_file.is_file())
        short_content = short_file.read_text(encoding="utf-8")
        self.assertIn('description: "Modern mikroservis orkestrasyon motoru."', short_content)
        self.assertIn("Modern mikroservis orkestrasyon motoru.", short_content)

        # Run long summary
        ret_long = run_summary(mode="long", root=self.root)
        self.assertEqual(ret_long, 0)
        long_file = self.root / "docs" / "TEST_PLATFORM_PROJECT_SUMMARY_LONG.md"
        self.assertTrue(long_file.is_file())
        long_content = long_file.read_text(encoding="utf-8")
        self.assertIn('description: "Modern mikroservis orkestrasyon motoru."', long_content)
        self.assertIn("İncelenen RFC Dokümanları", long_content)
        self.assertIn("RFC-001-Ingestion.md", long_content)


if __name__ == "__main__":
    unittest.main()
