#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Unit tests for check_bundle_limits.py gate script."""

import json
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

# musgoku/scripts dizinini sys.path'e ekle
TEST_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = TEST_DIR.parents[4]
SCRIPTS_DIR = PROJECT_ROOT / ".agent" / "skills" / "musgoku" / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import check_bundle_limits


class TestCheckBundleLimits(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = Path(tempfile.mkdtemp(prefix="test_bundle_limits_"))
        self.orig_env = os.environ.get("AGENTS_PROJECT_ROOT")
        os.environ["AGENTS_PROJECT_ROOT"] = str(self.tmp_dir)

    def tearDown(self):
        if self.orig_env is not None:
            os.environ["AGENTS_PROJECT_ROOT"] = self.orig_env
        else:
            os.environ.pop("AGENTS_PROJECT_ROOT", None)
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_out_of_scope_when_no_package_json(self):
        """package.json olmayan projede kapsam dışı dönmeli (exit 0)."""
        ret = check_bundle_limits.main(["--json"])
        self.assertEqual(ret, 0)

    def test_passes_when_chunks_within_limits(self):
        """Tüm chunk'lar bütçe sınırları dahilindeyse exit 0 dönmeli."""
        pkg = self.tmp_dir / "package.json"
        pkg.write_text('{"name": "test-app", "scripts": {"build": "vite build"}}', encoding="utf-8")

        dist_assets = self.tmp_dir / "dist" / "assets"
        dist_assets.mkdir(parents=True, exist_ok=True)

        # 50 KB dummy chunk
        chunk = dist_assets / "index-abc123.js"
        chunk.write_bytes(b"console.log('hello');\n" * 2000)

        ret = check_bundle_limits.main(["--json"])
        self.assertEqual(ret, 0)

    def test_fails_when_raw_chunk_exceeds_limit(self):
        """Chunk ham boyutu limiti aşarsa exit 1 dönmeli."""
        pkg = self.tmp_dir / "package.json"
        pkg.write_text('{"name": "test-app", "scripts": {"build": "vite build"}}', encoding="utf-8")

        dist_assets = self.tmp_dir / "dist" / "assets"
        dist_assets.mkdir(parents=True, exist_ok=True)

        # 600 KB dummy chunk (default limit 500 KB)
        chunk = dist_assets / "heavy-vendor.js"
        chunk.write_bytes(b"x = 1;\n" * 105000)

        ret = check_bundle_limits.main(["--json"])
        self.assertEqual(ret, 1)

    def test_fails_when_entry_gzip_exceeds_limit(self):
        """Entry chunk gzip boyutu 200 KB'ı aşarsa exit 1 dönmeli."""
        pkg = self.tmp_dir / "package.json"
        pkg.write_text('{"name": "test-app", "scripts": {"build": "vite build"}}', encoding="utf-8")

        dist_assets = self.tmp_dir / "dist" / "assets"
        dist_assets.mkdir(parents=True, exist_ok=True)

        # Rastgele / sıkıştırılamayan veri ile 250 KB gzip oluştur
        chunk = dist_assets / "index-bloat.js"
        chunk.write_bytes(os.urandom(260 * 1024))

        ret = check_bundle_limits.main(["--json"])
        self.assertEqual(ret, 1)

    def test_respects_vite_config_chunk_limit(self):
        """vite.config.ts içindeki chunkSizeWarningLimit değerine saygı göstermeli."""
        pkg = self.tmp_dir / "package.json"
        pkg.write_text('{"name": "test-app", "scripts": {"build": "vite build"}}', encoding="utf-8")

        vite_cfg = self.tmp_dir / "vite.config.ts"
        vite_cfg.write_text('export default { build: { chunkSizeWarningLimit: 800 } };', encoding="utf-8")

        limit = check_bundle_limits.detect_chunk_limit(self.tmp_dir)
        self.assertEqual(limit, 800.0)

    def test_chunk_warning_regex_pattern(self):
        """Vite sarı uyarı metinlerini yakalamalı."""
        sample_warning = "(!) Some chunks are larger than 600 kB after minification."
        self.assertTrue(bool(check_bundle_limits.CHUNK_WARN_PATTERN.search(sample_warning)))

        sample_clean = "✓ built in 5.2s"
        self.assertFalse(bool(check_bundle_limits.CHUNK_WARN_PATTERN.search(sample_clean)))


if __name__ == "__main__":
    unittest.main()
