#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Unit tests for check_design_slop.py gate checker."""

import json
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

TEST_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = TEST_DIR.parents[4]
SCRIPTS_DIR = PROJECT_ROOT / ".agent" / "skills" / "musgoku" / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import check_design_slop


class TestCheckDesignSlop(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = Path(tempfile.mkdtemp(prefix="test_design_slop_"))
        self.orig_env = os.environ.get("AGENTS_PROJECT_ROOT")
        os.environ["AGENTS_PROJECT_ROOT"] = str(self.tmp_dir)

    def tearDown(self):
        if self.orig_env is not None:
            os.environ["AGENTS_PROJECT_ROOT"] = self.orig_env
        else:
            os.environ.pop("AGENTS_PROJECT_ROOT", None)
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_out_of_scope_when_no_frontend_files(self):
        """Frontend kaynak dosyası bulunmadığında kapsam dışı dönmeli (exit 0)."""
        ret = check_design_slop.main(["--json"])
        self.assertEqual(ret, 0)

    def test_clean_code_passes(self):
        """Temiz, zanaat tabanına uygun kod exit 0 dönmeli."""
        src = self.tmp_dir / "src"
        src.mkdir()
        page = src / "Dashboard.tsx"
        page.write_text(
            """
            import React from 'react';
            export function Dashboard() {
                return (
                    <div className="p-8 bg-zinc-950 text-zinc-100">
                        <h1 className="text-3xl font-bold tracking-tight">System Status</h1>
                        <div className="grid grid-cols-3 gap-6">
                            <div className="p-4 border border-zinc-800 rounded-lg bg-zinc-900">
                                <h3>Metric A</h3>
                                <p className="font-mono tabular-nums">1,248.50</p>
                            </div>
                        </div>
                    </div>
                );
            }
            """,
            encoding="utf-8"
        )
        ret = check_design_slop.main(["--json"])
        self.assertEqual(ret, 0)

    def test_catches_nested_cards_e1(self):
        """İç içe Card bileşeni (E1) yakalanmalı ve exit 1 dönmeli."""
        src = self.tmp_dir / "src"
        src.mkdir()
        page = src / "Feed.tsx"
        page.write_text(
            """
            <Card className="p-6">
                <h2>Parent</h2>
                <Card className="p-4">
                    <p>Nested child</p>
                </Card>
            </Card>
            """,
            encoding="utf-8"
        )
        res = check_design_slop.run_checks(self.tmp_dir)
        self.assertEqual(res["exit"], 1)
        self.assertTrue(any(e["code"] == "E1" for e in res["errors"]))

    def test_card_parts_do_not_trigger_nested_card_error(self):
        """Card içinde CardHeader ve CardContent gibi parçalar (shadcn/ui) hata üretmemeli."""
        src = self.tmp_dir / "src"
        src.mkdir()
        page = src / "ShadcnCard.tsx"
        page.write_text(
            """
            <Card className="p-6">
                <CardHeader>
                    <CardTitle>Title</CardTitle>
                    <CardDescription>Description</CardDescription>
                </CardHeader>
                <CardContent>
                    <p>Body text</p>
                </CardContent>
                <CardFooter>
                    <button>Action</button>
                </CardFooter>
            </Card>
            """,
            encoding="utf-8"
        )
        res = check_design_slop.run_checks(self.tmp_dir)
        self.assertEqual(res["exit"], 0)
        self.assertFalse(any(e["code"] == "E1" for e in res["errors"]))

    def test_catches_gradient_text_e2(self):
        """Metin üzerinde gradyan (E2) yakalanmalı."""
        src = self.tmp_dir / "src"
        src.mkdir()
        page = src / "Hero.tsx"
        page.write_text(
            """
            <h1 className="bg-clip-text text-transparent bg-gradient-to-r from-purple-400 to-pink-600">
                AI Powered Magic
            </h1>
            """,
            encoding="utf-8"
        )
        res = check_design_slop.run_checks(self.tmp_dir)
        self.assertEqual(res["exit"], 1)
        self.assertTrue(any(e["code"] == "E2" for e in res["errors"]))

    def test_catches_side_accent_on_rounded_e3(self):
        """Yuvarlatılmış kartta border-l-4 yan şerit (E3) yakalanmalı."""
        src = self.tmp_dir / "src"
        src.mkdir()
        page = src / "Notice.tsx"
        page.write_text(
            """
            <div className="p-4 border-l-4 border-blue-500 rounded-lg bg-zinc-900">
                Notice box
            </div>
            """,
            encoding="utf-8"
        )
        res = check_design_slop.run_checks(self.tmp_dir)
        self.assertEqual(res["exit"], 1)
        self.assertTrue(any(e["code"] == "E3" for e in res["errors"]))

    def test_catches_block_shadow_e4(self):
        """Sıfır-blur ofset blok gölge (E4) yakalanmalı."""
        src = self.tmp_dir / "src"
        src.mkdir()
        page = src / "Button.tsx"
        page.write_text(
            """
            <button className="px-4 py-2 bg-amber-400 border-2 border-black shadow-[4px_4px_0px_#000]">
                Click me
            </button>
            """,
            encoding="utf-8"
        )
        res = check_design_slop.run_checks(self.tmp_dir)
        self.assertEqual(res["exit"], 1)
        self.assertTrue(any(e["code"] == "E4" for e in res["errors"]))

    def test_catches_gray_on_color_e5(self):
        """Renkli zemin üzerinde ham gri metin (E5) yakalanmalı."""
        src = self.tmp_dir / "src"
        src.mkdir()
        page = src / "Card.tsx"
        page.write_text(
            """
            <div className="p-6 bg-blue-900 text-slate-400">
                Subdued metadata
            </div>
            """,
            encoding="utf-8"
        )
        res = check_design_slop.run_checks(self.tmp_dir)
        self.assertEqual(res["exit"], 1)
        self.assertTrue(any(e["code"] == "E5" for e in res["errors"]))

    def test_catches_banned_fonts_e6(self):
        """Yasaklı/klişe font tanımı (E6) yakalanmalı."""
        src = self.tmp_dir / "src"
        src.mkdir()
        page = src / "style.css"
        page.write_text(
            """
            .hero-title {
                font-family: Impact, sans-serif;
            }
            """,
            encoding="utf-8"
        )
        res = check_design_slop.run_checks(self.tmp_dir)
        self.assertEqual(res["exit"], 1)
        self.assertTrue(any(e["code"] == "E6" for e in res["errors"]))

    def test_catches_eyebrow_spam_e7(self):
        """Başlık üzerinde jenerik büyük harfli süs hapı (E7) yakalanmalı."""
        src = self.tmp_dir / "src"
        src.mkdir()
        page = src / "Section.tsx"
        page.write_text(
            """
            <div>
                <span className="uppercase tracking-widest text-xs text-blue-500">WHY CHOOSE US</span>
                <h2>The Best Platform</h2>
            </div>
            """,
            encoding="utf-8"
        )
        res = check_design_slop.run_checks(self.tmp_dir)
        self.assertEqual(res["exit"], 1)
        self.assertTrue(any(e["code"] == "E7" for e in res["errors"]))

    def test_warns_missing_tabular_nums_w1(self):
        """Tabloda tabular-nums eksikliği W1 uyarısı üretmeli."""
        src = self.tmp_dir / "src"
        src.mkdir()
        page = src / "Table.tsx"
        page.write_text(
            """
            <table>
                <tbody>
                    <tr><td>Sales</td><td>$45,000</td></tr>
                </tbody>
            </table>
            """,
            encoding="utf-8"
        )
        res = check_design_slop.run_checks(self.tmp_dir)
        self.assertEqual(res["exit"], 0)
        self.assertTrue(any(w["code"] == "W1" for w in res["warnings"]))

        # --strict ile exit 1 olmalı
        ret = check_design_slop.main(["--strict", "--json"])
        self.assertEqual(ret, 1)

    def test_warns_spinner_loading_slop_w4(self):
        """Veri yüklenirken iskelet ekran yerine jenerik spinner W4 uyarısı üretmeli."""
        src = self.tmp_dir / "src"
        src.mkdir(exist_ok=True)
        page = src / "DataFeed.tsx"
        page.write_text(
            """
            import React from 'react';
            export function DataFeed({ isLoading, data }) {
                if (isLoading) return <Spinner />;
                return <div>{data.title}</div>;
            }
            """,
            encoding="utf-8"
        )
        res = check_design_slop.run_checks(self.tmp_dir)
        self.assertTrue(any(w["code"] == "W4" for w in res["warnings"]))

    def test_skeleton_screen_loading_passes_cleanly(self):
        """İskelet ekran (Skeleton) kullanan veri yükleme bileşeni temiz geçmeli."""
        src = self.tmp_dir / "src"
        src.mkdir(exist_ok=True)
        page = src / "DataFeedWithSkeleton.tsx"
        page.write_text(
            """
            import React from 'react';
            import { Skeleton } from '@/components/ui/skeleton';
            export function DataFeedWithSkeleton({ isLoading, data }) {
                if (isLoading) {
                    return (
                        <div className="space-y-4" aria-busy="true">
                            <Skeleton className="h-8 w-1/3" />
                            <Skeleton className="h-24 w-full" />
                        </div>
                    );
                }
                return <div>{data.title}</div>;
            }
            """,
            encoding="utf-8"
        )
        res = check_design_slop.run_checks(self.tmp_dir)
        self.assertFalse(any(w["code"] == "W4" for w in res["warnings"]))


if __name__ == "__main__":
    unittest.main()
