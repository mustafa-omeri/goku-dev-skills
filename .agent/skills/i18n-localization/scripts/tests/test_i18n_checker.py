#!/usr/bin/env python3
"""i18n_checker.py kendi testleri.

Neden ayrı dosya: HANDOFF tuzak 6 — "Doğrulayıcı yalnız geçersiz girdiyi
yakalamakla kalmaz, geçerli girdiyi de test eder." Geçerli bir projeyi reddeden
denetleyici, ajanın kapıyı atlamasına yol açar; o zaman araç zararsız olmaktan
çıkar ve işe yaramaz.

Her test geçici bir proje ağacı kurar ve script'i gerçekten çalıştırır.
"""

from __future__ import annotations

import importlib.util
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent
SCRIPT = SCRIPTS / "i18n_checker.py"

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, str(SCRIPTS))
spec = importlib.util.spec_from_file_location("i18n_checker", SCRIPT)
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def make_project(tr: dict, en: dict, sources: dict[str, str]) -> Path:
    root = Path(tempfile.mkdtemp(prefix="i18n-test-"))
    write(root / "package.json", '{"name":"t"}')
    write(root / "src" / "locales" / "tr.json", json.dumps(tr, ensure_ascii=False))
    write(root / "src" / "locales" / "en.json", json.dumps(en, ensure_ascii=False))
    for rel, body in sources.items():
        write(root / "src" / rel, body)
    return root


def run(root: Path, *extra: str) -> tuple[int, str, str]:
    """Script'i gerçekten çalıştırır; stdout/stderr biçimlendirilmiş döner."""
    import io
    import contextlib
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = checker.main(["--root", str(root), *extra])
    return code, out.getvalue(), err.getvalue()


GOOD_TR = {"common": {"save": "Kaydet", "welcome": "Hoş geldin {{name}}"}, "nav": {"home": "Ana Sayfa"}}
GOOD_EN = {"common": {"save": "Save", "welcome": "Welcome {{name}}"}, "nav": {"home": "Home"}}
CLEAN_TSX = (
    "import { useTranslation } from 'react-i18next'\n"
    "export function Bar() {\n"
    "  const { t } = useTranslation()\n"
    "  return <button>{t('common.save')}</button>\n"
    "}\n"
)


class TmpMixin:
    def tearDown(self) -> None:
        if getattr(self, "root", None):
            shutil.rmtree(self.root, ignore_errors=True)


class RejectsInvalid(TmpMixin, unittest.TestCase):
    """Geçersiz projeyi REDDETMELİ."""

    def test_missing_key_is_an_error(self):
        self.root = make_project(
            GOOD_TR, GOOD_EN, {"Bar.tsx": "const x = t('common.gone')\n"},
        )
        code, _, err = run(self.root)
        self.assertEqual(code, 1, err)
        self.assertIn("E3", err)
        self.assertIn("common.gone", err)

    def test_dictionary_drift_is_an_error(self):
        self.root = make_project(
            {"common": {"save": "Kaydet", "onlyTr": "Yalnız TR"}}, GOOD_EN, {"Bar.tsx": CLEAN_TSX},
        )
        code, _, err = run(self.root)
        self.assertEqual(code, 1, err)
        self.assertIn("E1", err)

    def test_empty_translation_is_an_error(self):
        self.root = make_project(
            {"common": {"save": ""}}, {"common": {"save": "Save"}}, {"Bar.tsx": CLEAN_TSX},
        )
        code, _, err = run(self.root)
        self.assertEqual(code, 1, err)
        self.assertIn("E2", err)

    def test_placeholder_mismatch_is_an_error(self):
        self.root = make_project(
            {"common": {"welcome": "Hoş geldin {{name}}"}},
            {"common": {"welcome": "Welcome"}},
            {"Bar.tsx": CLEAN_TSX},
        )
        code, _, err = run(self.root)
        self.assertEqual(code, 1, err)
        self.assertIn("E7", err)

    def test_turkish_residue_in_foreign_dictionary_is_flagged(self):
        self.root = make_project(
            GOOD_TR, {"common": {"save": "Install KalanSüre", "welcome": "Welcome {{name}}"},
                     "nav": {"home": "Home"}},
            {"Bar.tsx": CLEAN_TSX},
        )
        code, _, err = run(self.root)
        self.assertEqual(code, 0, "E6 uyarıdır, kapıyı kırmaz")
        self.assertIn("E6", err)


class AcceptsValid(TmpMixin, unittest.TestCase):
    """Geçerli projeyi KABUL etmeli. Tuzak 6."""

    def test_clean_project_passes(self):
        self.root = make_project(GOOD_TR, GOOD_EN, {"Bar.tsx": CLEAN_TSX})
        code, out, err = run(self.root)
        self.assertEqual(code, 0, f"stdout={out}\nstderr={err}")
        self.assertIn("[OK]", out)

    def test_english_words_are_not_flagged_as_turkish(self):
        """'Trending Categories' Türkçe DEĞİLDİR — false positive regresyonu."""
        for text in ("Trending Categories", "Total Events", "Search", "Share",
                     "Update", "View All", "Settings", "Install", "Free", "Apply"):
            self.assertFalse(checker.looks_turkish(text), f"yanlış pozitif: {text!r}")

    def test_code_identifiers_are_not_flagged(self):
        """Alt-dize tuzağı: `profiles` tablo adı, `profil` köküyle eşleşmemeli."""
        for text in ("profiles", "profileImage", "categoryForm", "tagsTable",
                     "catalogue", "headers", "session"):
            self.assertFalse(checker.looks_turkish(text), f"kod tanımı sayıldı: {text!r}")

    def test_non_ui_lines_are_not_hardcode_findings(self):
        """`throw` / `console` / `new Error` satırları UI metni DEĞİLDİR."""
        src = (
            "const { t } = useTranslation()\n"
            "throw new Error('create_bot_key ham anahtar döndürmedi')\n"
            "console.warn('[PWA] Service Worker kaydı başarısız oldu:', error)\n"
            "export const x = <b>{t('common.save')}</b>\n"
        )
        self.root = make_project(GOOD_TR, GOOD_EN, {"Bar.tsx": src})
        code, _, err = run(self.root)
        self.assertEqual(code, 0, err)
        self.assertNotIn("E5", err)

    def test_backend_and_cli_folders_are_skipped(self):
        """`supabase/functions` edge backend'dır — çeviri kapsamı dışıdır."""
        self.root = make_project(
            GOOD_TR, GOOD_EN,
            {
                "Bar.tsx": CLEAN_TSX,
                "supabase/functions/x/index.ts": "throw new Error('Yalnızca POST kabul edilir.')\n",
                "scripts/check.mjs": "console.warn('Şifre bulunamadı')\n",
            },
        )
        code, _, err = run(self.root)
        self.assertEqual(code, 0, err)
        self.assertNotIn("E5", err)

    def test_routes_and_error_matching_are_not_hardcode(self):
        """Rota slug'ı ve hata mesajı eşlemesi UI metni DEĞİLDİR.

        `/kategori/:slug` çevrilirse URL her dilde değişir ve linkler kırılır.
        `m.includes('gerekçe')` bir hata sınıfını ayırt etme kuralıdır.
        """
        src = (
            "const { t } = useTranslation()\n"
            "const a = <Route path=\"/kategori/:slug\" element={<X />} />;\n"
            "const b = <Link to={`/kategori/${node.slug}`}>kategori</Link>;\n"
            "if (m.includes('gerekçe')) return t('common.save');\n"
            "const n = s.replace(/ı/g, 'i').replace(/ş/g, 's');\n"
            "export const x = <b>{t('common.save')}</b>\n"
        )
        self.root = make_project(GOOD_TR, GOOD_EN, {"Bar.tsx": src})
        code, _, err = run(self.root)
        self.assertEqual(code, 0, err)
        self.assertNotIn("E5", err)

    def test_turkish_text_is_detected(self):
        for text in ("Kaydet", "Ana Sayfa", "Hoş geldin", "Ücretsiz",
                     "Yayın Ekipleri", "Geri Sayım", "Görüntülenme"):
            self.assertTrue(checker.looks_turkish(text), f"kaçırıldı: {text!r}")

    def test_comments_do_not_count_as_hardcode(self):
        """JSX yorumundaki Türkçe UI metni raporlanmamalı."""
        src = (
            "const { t } = useTranslation()\n"
            "/**\n * Türkçe açıklama: Kaydet butonu\n */\n"
            "{/* Todo: Vazgeç davranışını düzelt */}\n"
            "export const x = <b>{t('common.save')}</b>\n"
        )
        self.root = make_project(GOOD_TR, GOOD_EN, {"Bar.tsx": src})
        code, _, err = run(self.root)
        self.assertEqual(code, 0, err)
        self.assertNotIn("E5", err)

    def test_default_value_with_existing_key_is_only_a_warning(self):
        src = "const x = t('common.save', 'Kaydet')\n"
        self.root = make_project(GOOD_TR, GOOD_EN, {"Bar.tsx": src})
        code, _, err = run(self.root)
        self.assertEqual(code, 0, "anahtar varsa kapı kırılmaz")
        self.assertIn("E4", err)

    def test_single_language_project_is_reported(self):
        root = Path(tempfile.mkdtemp(prefix="i18n-test-"))
        self.addCleanup(shutil.rmtree, root, True)
        write(root / "package.json", "{}")
        write(root / "src" / "locales" / "tr.json", json.dumps(GOOD_TR, ensure_ascii=False))
        write(root / "src" / "Bar.tsx", CLEAN_TSX)
        code, _, err = run(root)
        self.assertEqual(code, 1)
        self.assertIn("E1", err)

    def test_missing_locale_directory_is_a_tool_error(self):
        root = Path(tempfile.mkdtemp(prefix="i18n-test-"))
        self.addCleanup(shutil.rmtree, root, True)
        write(root / "package.json", "{}")
        write(root / "src" / "Bar.tsx", CLEAN_TSX)
        code, _, _ = run(root)
        self.assertEqual(code, 2, "araç hatası 2 dönmeli")


class ReportsTheRealBug(TmpMixin, unittest.TestCase):
    """Senaryo: eksik anahtarlı defaultValue — İngilizce seçilince Türkçe döner."""

    def test_default_value_hides_the_missing_key(self):
        tr = {"nav": {"home": "Ana Sayfa"}}
        en = {"nav": {"home": "Home"}}
        src = "const x = t('nav.submit', 'İçerik Gönder')\n"
        self.root = make_project(tr, en, {"Bar.tsx": src})
        code, _, err = run(self.root)
        self.assertEqual(code, 1, "sözlükler senkron olsa bile eksik anahtar hata olmalı")
        self.assertIn("nav.submit", err)
        self.assertIn("İçerik Gönder", err)


if __name__ == "__main__":
    unittest.main(verbosity=2)