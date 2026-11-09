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

    def test_warns_unlocked_modal_scroll_w5(self):
        """Modal veya Dialog konteynerinde overflow-y-auto olup overscroll-contain eksikse W5 uyarısı üretmeli."""
        src = self.tmp_dir / "src"
        src.mkdir(exist_ok=True)
        page = src / "TestModal.tsx"
        page.write_text(
            """
            import React from 'react';
            import { Dialog, DialogContent } from '@/components/ui/dialog';
            export function TestModal({ open }) {
                return (
                    <Dialog open={open}>
                        <DialogContent className="max-w-lg max-h-[85dvh] overflow-y-auto">
                            <div>Content</div>
                        </DialogContent>
                    </Dialog>
                );
            }
            """,
            encoding="utf-8"
        )
        res = check_design_slop.run_checks(self.tmp_dir)
        self.assertTrue(any(w["code"] == "W5" for w in res["warnings"]))

    def test_compliant_modal_scroll_passes_cleanly(self):
        """Modal konteynerinde overscroll-contain varsa W5 uyarısı üretilmemeli."""
        src = self.tmp_dir / "src"
        src.mkdir(exist_ok=True)
        page = src / "TestModalCompliant.tsx"
        page.write_text(
            """
            import React from 'react';
            import { Dialog, DialogContent } from '@/components/ui/dialog';
            export function TestModalCompliant({ open }) {
                return (
                    <Dialog open={open}>
                        <DialogContent className="max-w-lg max-h-[85dvh] overflow-y-auto overscroll-contain">
                            <div>Content</div>
                        </DialogContent>
                    </Dialog>
                );
            }
            """,
            encoding="utf-8"
        )
        res = check_design_slop.run_checks(self.tmp_dir)
        self.assertFalse(any(w["code"] == "W5" for w in res["warnings"]))


    def test_warns_unlocked_modal_scroll_css(self):
        """CSS dosyasında .modal seçicisinde overflow-y auto olup overscroll-behavior eksikse W5 uyarısı üretmeli."""
        src = self.tmp_dir / "src"
        src.mkdir(exist_ok=True)
        css_file = src / "modal.css"
        css_file.write_text(
            """
            .modal-content {
                max-height: 80vh;
                overflow-y: auto;
            }
            """,
            encoding="utf-8"
        )
        res = check_design_slop.run_checks(self.tmp_dir)
        self.assertTrue(any(w["code"] == "W5" for w in res["warnings"]))

    def test_compliant_modal_scroll_css_passes_cleanly(self):
        """CSS dosyasında .modal seçicisinde overscroll-behavior: contain varsa W5 uyarısı üretilmemeli."""
        src = self.tmp_dir / "src"
        src.mkdir(exist_ok=True)
        css_file = src / "modal-compliant.css"
        css_file.write_text(
            """
            .modal-content {
                max-height: 80vh;
                overflow-y: auto;
                overscroll-behavior: contain;
            }
            """,
            encoding="utf-8"
        )
        res = check_design_slop.run_checks(self.tmp_dir)
        self.assertFalse(any(w["code"] == "W5" for w in res["warnings"]))


    def test_catches_single_box_auth_slop_e12(self):
        """Tam sayfa Login/Auth ekranında dar tek-kutu (max-w-[440px] / max-w-md) olup masaüstü Split-Hero (lg:grid-cols-12 / lg:grid-cols-2 / lg:flex-row) yoksa E12 hatası üretmeli."""
        auth_dir = self.tmp_dir / "src" / "modules" / "auth"
        auth_dir.mkdir(parents=True, exist_ok=True)
        login_page = auth_dir / "LoginPage.tsx"
        login_page.write_text(
            """
            import React from 'react';
            export function LoginPage() {
                return (
                    <main className="relative flex min-h-screen items-center justify-center bg-[#ededf3] px-4 py-8">
                        <div className="relative z-10 w-full max-w-[440px]">
                            <form className="rounded-2xl bg-white p-8 shadow-sm">
                                <input type="email" />
                            </form>
                        </div>
                    </main>
                );
            }
            """,
            encoding="utf-8"
        )
        res = check_design_slop.run_checks(self.tmp_dir)
        self.assertEqual(res["exit"], 1)
        self.assertTrue(any(e["code"] == "E12" for e in res["errors"]))

    def test_allows_split_hero_auth_page_e12(self):
        """Masaüstü Split-Hero Dual-Pane (lg:grid-cols-12 veya lg:grid-cols-2) kullanan tam sayfa Login ekranı E12 hatası üretmemeli."""
        auth_dir = self.tmp_dir / "src" / "modules" / "auth"
        auth_dir.mkdir(parents=True, exist_ok=True)
        login_page = auth_dir / "LoginPage.tsx"
        login_page.write_text(
            """
            import React from 'react';
            export function LoginPage() {
                return (
                    <main className="relative flex min-h-screen items-center justify-center bg-[#ededf3] px-4 py-8">
                        <div className="relative z-10 w-full max-w-[1020px] grid grid-cols-1 lg:grid-cols-12 overflow-hidden rounded-3xl shadow-sm">
                            <aside className="hidden lg:flex lg:col-span-5 flex-col justify-between bg-[#252528] p-10 text-white">
                                <h2>Recall Memory Engine</h2>
                            </aside>
                            <section className="lg:col-span-7 bg-white p-8 sm:p-10">
                                <form><input type="email" /></form>
                            </section>
                        </div>
                    </main>
                );
            }
            """,
            encoding="utf-8"
        )
        res = check_design_slop.run_checks(self.tmp_dir)
        self.assertFalse(any(e["code"] == "E12" for e in res["errors"]))

    def test_allows_sliding_hero_auth_page_e12(self):
        """Masaüstü 50%/50% Sliding-Hero Overlay kullanan tam sayfa Login ekranı E12 hatası üretmemeli."""
        auth_dir = self.tmp_dir / "src" / "modules" / "auth"
        auth_dir.mkdir(parents=True, exist_ok=True)
        login_page = auth_dir / "LoginPage.tsx"
        login_page.write_text(
            """
            import React, { useState } from 'react';
            export function LoginPage() {
                const [phase, setPhase] = useState<'signin' | 'signup'>('signin');
                return (
                    <main className="relative flex min-h-screen items-center justify-center bg-[#ededf3] px-4 py-8">
                        <div className="card relative w-full max-w-[960px] min-h-[620px] rounded-[24px] bg-white border-8 border-white overflow-hidden shadow-2xl">
                            {/* Sliding Hero Overlay */}
                            <div className={`card-bg absolute inset-y-0 left-0 w-1/2 z-20 transition-transform duration-[650ms] ${
                                phase === 'signin' ? 'translate-x-full' : 'translate-x-0'
                            }`}>
                                <button onClick={() => setPhase(phase === 'signin' ? 'signup' : 'signin')}>Toggle</button>
                            </div>
                            {/* Left Login Form */}
                            <div className="form login absolute inset-y-0 left-0 w-1/2 p-8 max-w-md">
                                <form><input type="email" /></form>
                            </div>
                            {/* Right Signup Form */}
                            <div className="form signup absolute inset-y-0 left-1/2 w-1/2 p-8 max-w-md">
                                <form><input type="email" /></form>
                            </div>
                        </div>
                    </main>
                );
            }
            """,
            encoding="utf-8"
        )
        res = check_design_slop.run_checks(self.tmp_dir)
        self.assertFalse(any(e["code"] == "E12" for e in res["errors"]))


    def test_warns_pitch_black_sliding_hero_without_image_w6(self):
        login_page = self.tmp_dir / "src" / "modules" / "auth" / "LoginPage.tsx"
        login_page.parent.mkdir(parents=True, exist_ok=True)
        login_page.write_text(
            '''
            import React from 'react';
            export function LoginPage() {
                return (
                    <main className="relative flex min-h-screen items-center justify-center">
                        <div className="split-hero relative max-w-[960px] grid grid-cols-2">
                            <div className="form">Form Content</div>
                            {/* Slop: Flat pitch-black hero showcase with 0 images */}
                            <aside className="hero sliding-hero bg-[#252528] text-white">
                                <h3>Recall Vault</h3>
                                <div>Feature Card 1</div>
                                <div>Feature Card 2</div>
                                <div>Feature Card 3</div>
                            </aside>
                        </div>
                    </main>
                );
            }
            ''',
            encoding="utf-8"
        )
        res = check_design_slop.run_checks(self.tmp_dir)
        self.assertTrue(any(w["code"] == "W6" for w in res["warnings"]))



    def test_warns_pitch_black_split_hero_without_image_w6(self):
        login_page = self.tmp_dir / 'src' / 'modules' / 'auth' / 'LoginPage.tsx'
        login_page.parent.mkdir(parents=True, exist_ok=True)
        login_page.write_text(
            """
            import React from 'react';
            export function LoginPage() {
                return (
                    <main className="relative flex min-h-screen items-center justify-center">
                        <div className="w-full max-w-[1020px] grid grid-cols-1 lg:grid-cols-12">
                            {/* Slop: Flat pitch-black split-hero column with 0 images */}
                            <aside className="split-hero lg:col-span-5 bg-zinc-950 text-white">
                                <h3>Cloud Storage</h3>
                                <div>Feature Card 1</div>
                            </aside>
                            <div className="form lg:col-span-7">Form Content</div>
                        </div>
                    </main>
                );
            }
            """,
            encoding='utf-8'
        )
        res = check_design_slop.run_checks(self.tmp_dir)
        self.assertTrue(any(w['code'] == 'W6' for w in res['warnings']))


    def test_rejects_magic_link_or_redundant_tabs_e13(self):
        login_page = self.tmp_dir / "src" / "modules" / "auth" / "LoginPage.tsx"
        login_page.parent.mkdir(parents=True, exist_ok=True)
        login_page.write_text(
            """
            import React from 'react';
            export function LoginPage() {
                return (
                    <main className="relative flex min-h-screen items-center justify-center">
                        <div className="split-hero w-full max-w-[1020px] grid grid-cols-12">
                            <aside className="lg:col-span-5"><img src="/assets/auth/hero.jpg" /></aside>
                            <div className="lg:col-span-7">
                                {/* Redundant sub-switcher tabs: tabPassword vs tabMagicLink */}
                                <div className="tabs">
                                    <button>Şifre ile Giriş</button>
                                    <button>Magic Link ile Giriş</button>
                                </div>
                                <form><input type="email" /></form>
                            </div>
                        </div>
                    </main>
                );
            }
            """,
            encoding="utf-8"
        )
        res = check_design_slop.run_checks(self.tmp_dir)
        self.assertTrue(any(e["code"] == "E13" for e in res["errors"]))

    def test_accepts_clean_auth_credentials_page_e13(self):
        login_page = self.tmp_dir / "src" / "modules" / "auth" / "LoginPage.tsx"
        login_page.parent.mkdir(parents=True, exist_ok=True)
        login_page.write_text(
            """
            import React from 'react';
            export function LoginPage() {
                return (
                    <main className="relative flex min-h-screen items-center justify-center">
                        <div className="split-hero w-full max-w-[1020px] grid grid-cols-12">
                            <aside className="lg:col-span-5"><img src="/assets/auth/hero.jpg" /></aside>
                            <div className="lg:col-span-7">
                                <form>
                                    <input type="email" />
                                    <input type="password" />
                                    <label><input type="checkbox" /> Remember me</label>
                                    <a href="/forgot">Forgot password?</a>
                                    <button type="submit">LOGIN</button>
                                    <div>── Or ──</div>
                                    <button type="button">Google</button>
                                    <button type="button">GitHub</button>
                                </form>
                            </div>
                        </div>
                    </main>
                );
            }
            """,
            encoding="utf-8"
        )
        res = check_design_slop.run_checks(self.tmp_dir)
        self.assertFalse(any(e["code"] == "E13" for e in res["errors"]))

    def test_catches_rogue_dark_modal_header_e14(self):
        """Modal header içinde korsan karanlık gradyan (from-slate-900 via-blue-950) E14 yakalamalı."""
        modal = self.tmp_dir / "src" / "components" / "MyModal.tsx"
        modal.parent.mkdir(parents=True, exist_ok=True)
        modal.write_text(
            """
            import React from 'react';
            import { DialogHeader, DialogTitle } from '@/components/ui/dialog';
            export function MyModal() {
                return (
                    <DialogHeader className="p-6 bg-gradient-to-r from-slate-900 via-blue-950 to-slate-900 text-white border-b border-slate-800">
                        <DialogTitle>Modal Başlığı</DialogTitle>
                    </DialogHeader>
                );
            }
            """,
            encoding="utf-8"
        )
        res = check_design_slop.run_checks(self.tmp_dir)
        self.assertTrue(any(e["code"] == "E14" for e in res["errors"]))

    def test_catches_rainbow_palette_slop_e15(self):
        """Tek bir bileşende 5+ farklı kromatik Tailwind renk ailesi kullanılması E15 yakalamalı."""
        comp = self.tmp_dir / "src" / "components" / "RainbowCard.tsx"
        comp.parent.mkdir(parents=True, exist_ok=True)
        comp.write_text(
            """
            import React from 'react';
            export function RainbowCard() {
                return (
                    <div>
                        <span className="text-blue-600">Mavi</span>
                        <span className="text-indigo-600">İndigo</span>
                        <span className="text-emerald-600">Yeşil</span>
                        <span className="text-amber-600">Sarı</span>
                        <span className="text-purple-600">Mor</span>
                        <span className="text-rose-600">Kırmızı</span>
                    </div>
                );
            }
            """,
            encoding="utf-8"
        )
        res = check_design_slop.run_checks(self.tmp_dir)
        self.assertTrue(any(e["code"] == "E15" for e in res["errors"]))

    def test_catches_semantic_token_drift_e16(self):
        """Modal/dialog içinde semantik token yerine ham koyu slate-950/border-slate-700 inputu E16 yakalamalı."""
        comp = self.tmp_dir / "src" / "components" / "DarkInputModal.tsx"
        comp.parent.mkdir(parents=True, exist_ok=True)
        comp.write_text(
            """
            import React from 'react';
            export function DarkInputModal() {
                return (
                    <div className="modal-header">
                        <input className="w-full bg-slate-950/60 border border-slate-700/80 rounded-lg text-white" />
                    </div>
                );
            }
            """,
            encoding="utf-8"
        )
        res = check_design_slop.run_checks(self.tmp_dir)
        self.assertTrue(any(e["code"] == "E16" for e in res["errors"]))


if __name__ == "__main__":
    unittest.main()
