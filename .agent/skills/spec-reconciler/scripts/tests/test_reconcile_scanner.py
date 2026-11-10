#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Unit tests for ReconcileScanner with Dynamic RFC/PRD Discovery and Frontend Link Detection."""

import json
import tempfile
import unittest
from pathlib import Path

import sys
SCRIPTS_DIR = Path(__file__).resolve().parent.parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from reconcile_scanner import (
    ReconcileScanner,
    discover_prd_files,
    discover_rfc_files,
)


class TestReconcileScanner(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_discover_rfcs_in_root_and_docs(self):
        # 1. Root RFCs/ directory (like OCAI project)
        rfcs_dir = self.root / "RFCs"
        rfcs_dir.mkdir(parents=True)
        rfc1 = rfcs_dir / "RFC-001-Architecture.md"
        rfc1.write_text("# RFC 001\nSome spec content", encoding="utf-8")

        # 2. docs/rfc/ directory
        docs_rfc = self.root / "docs" / "rfc"
        docs_rfc.mkdir(parents=True)
        rfc2 = docs_rfc / "RFC-002-Payment.md"
        rfc2.write_text("# RFC 002\nPayment spec", encoding="utf-8")

        discovered = discover_rfc_files(self.root)
        self.assertEqual(len(discovered), 2)
        discovered_names = [p.name for p in discovered]
        self.assertIn("RFC-001-Architecture.md", discovered_names)
        self.assertIn("RFC-002-Payment.md", discovered_names)

    def test_discover_prds_in_root_and_specs(self):
        # 1. Root PRD.md
        prd1 = self.root / "PRD.md"
        prd1.write_text("# Product Requirements\nSpecs", encoding="utf-8")

        # 2. RFCs/PRD-Auth.md
        rfcs_dir = self.root / "RFCs"
        rfcs_dir.mkdir(parents=True)
        prd2 = rfcs_dir / "PRD-Auth.md"
        prd2.write_text("# Auth PRD", encoding="utf-8")

        discovered = discover_prd_files(self.root)
        self.assertEqual(len(discovered), 2)
        discovered_names = [p.name for p in discovered]
        self.assertIn("PRD.md", discovered_names)
        self.assertIn("PRD-Auth.md", discovered_names)

    def test_frontend_orphan_link_and_stub_marker_detection(self):
        fe_dir = self.root / "frontend" / "src"
        fe_dir.mkdir(parents=True)
        sample_page = fe_dir / "AdminReports.tsx"
        sample_page.write_text(
            """
import React from 'react';
import { Link } from 'react-router-dom';

export const AdminReports = () => {
  // TODO: backend bağlanacak ve API servisi açılacak
  const handleExport = () => {
    // STUB: call export endpoint
  };

  return (
    <div>
      <Link to="/api/reports/download">Download</Link>
      <Link to="/admin/reports/analytics">Analytics</Link>
      <a href="#">Placeholder</a>
    </div>
  );
};
            """,
            encoding="utf-8",
        )

        be_dir = self.root / "backend" / "src"
        be_dir.mkdir(parents=True)
        ctrl = be_dir / "UserController.java"
        ctrl.write_text(
            """
@RestController
@RequestMapping("/api/users")
public class UserController {
    @GetMapping("")
    public List<User> getUsers() { return List.of(); }
}
            """,
            encoding="utf-8",
        )

        scanner = ReconcileScanner(
            backend_path=be_dir,
            frontend_path=fe_dir,
            project_root=self.root,
        )
        scanner.scan_backend()
        scanner.scan_frontend()
        scanner.cross_analyze()

        # Check frontend calls, links, and stubs
        self.assertGreaterEqual(len(scanner.frontend_links), 2)
        self.assertGreaterEqual(len(scanner.stub_markers), 3)  # TODO, STUB, href="#"

        # Check findings
        types = [f.type for f in scanner.findings]
        self.assertIn("ORPHAN_FRONTEND_LINK", types)
        self.assertIn("STUB_BACKEND_PENDING", types)

        # Markdown report check
        report = scanner.generate_markdown_report()
        self.assertIn("APPROVAL GATE", report)
        self.assertIn("AdminReports.tsx", report)


if __name__ == "__main__":
    unittest.main()
