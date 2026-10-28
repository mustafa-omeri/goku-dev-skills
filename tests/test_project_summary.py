#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Regresyon ve Bütünlük Test Paketi: summarize_project.py

Kapsam:
1. Slug Çözümleme Hiyerarşisi (PROJECT_BRIEF -> package.json -> pom.xml -> Dizin Adı).
2. Short Mod Üretimi: docs/<SLUG>_PROJECT_SUMMARY_SHORT.md üretimi ve kompakt yapısı.
3. Long Mod & Çoklu PRD Sentezi: docs/<SLUG>_PROJECT_SUMMARY_LONG.md üretimi ve tüm
   PRD dokümanlarının tek bir dokümanda konsolidasyonu.
4. Versiyonlama Damgası ve Arşivleme: Dosya mevcutken yeniden çalıştırıldığında
   v1.0 -> v1.1 sürüm artışı, tarih/saat/kullanıcı damgası ve docs/archive/ yedeği.
5. PROJECT_BRIEF.md related_docs Zorunlu Senkronizasyonu.
6. Yol Güvenlik Kapısı: /docs dışındaki dizinlerin reddedilmesi (ValueError).
7. Dil Uyumu: primary_language (tr vs en) alanına göre dil seçimi.
8. Check Bayrağı: Dosya varlık ve mod tazelik kontrolü.
"""

from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

# Proje kökünü sys.path'e ekle
HERE = Path(__file__).resolve().parent
PROJECT_ROOT = HERE.parent
SCRIPT_DIR = PROJECT_ROOT / ".agent" / "skills" / "project-summary" / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

import summarize_project  # noqa: E402


class TestProjectSummary(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp(prefix="test_proj_summary_"))
        (self.test_dir / "docs").mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_slug_resolution_hierarchy(self):
        """Slug çözümleme hiyerarşisini (brief -> pkg -> fallback) test eder."""
        # 1. Brief'ten slug alma
        brief = self.test_dir / "PROJECT_BRIEF.md"
        brief.write_text("---\ntitle: \"Deneme Projesi\"\nslug: \"kalansure\"\nprimary_language: \"tr\"\n---\n# Brief", encoding="utf-8")
        self.assertEqual(summarize_project.get_project_slug(self.test_dir), "KALANSURE")

        # 2. Package.json'dan slug alma (brief yokken)
        brief.unlink()
        pkg = self.test_dir / "package.json"
        pkg.write_text(json.dumps({"name": "@scope/super-dashboard"}), encoding="utf-8")
        self.assertEqual(summarize_project.get_project_slug(self.test_dir), "SUPER_DASHBOARD")

        # 3. Fallback klasör adı
        pkg.unlink()
        expected_fallback = summarize_project.clean_slug(self.test_dir.name)
        self.assertEqual(summarize_project.get_project_slug(self.test_dir), expected_fallback)

    def test_short_mode_generation(self):
        """Short modda doğru isimlendirme ve içerik yapısını test eder."""
        brief = self.test_dir / "PROJECT_BRIEF.md"
        brief.write_text("---\ntitle: \"Kalansure\"\nslug: \"kalansure\"\nprimary_language: \"tr\"\nrelated_docs:\n  - \"HANDOFF.md\"\n---\n## 1. Teknoloji Yığını\n- React 19\n- Supabase", encoding="utf-8")

        res = summarize_project.run_summary(mode="short", root=self.test_dir)
        self.assertEqual(res, 0)

        output_file = self.test_dir / "docs" / "KALANSURE_PROJECT_SUMMARY_SHORT.md"
        self.assertTrue(output_file.is_file(), "Short özet dosyası docs/ altında oluşturulmalı!")

        content = output_file.read_text(encoding="utf-8")
        self.assertIn('mode: "short"', content)
        self.assertIn('version: "v1.0"', content)
        self.assertIn('language: "tr"', content)
        self.assertIn("Versiyonlama Damgası:", content)
        self.assertIn("## 1. Yönetici Özeti & Ürün Amacı", content)
        self.assertIn("React 19", content)

    def test_long_mode_with_multiple_prds_and_references(self):
        """Long modda tüm PRD ve referansların tek dokümanda birleştiğini test eder."""
        # Referans dokümanları oluştur
        (self.test_dir / "PROJECT_BRIEF.md").write_text("---\ntitle: \"SuperApp\"\nslug: \"super_app\"\nprimary_language: \"tr\"\nrelated_docs:\n  - \"HANDOFF.md\"\n---\n## 1. Teknoloji Yığını\n- Java 21 / Spring Boot 3", encoding="utf-8")
        (self.test_dir / "PRODUCT.md").write_text("## Ürün Vizyonu\nKurumsal filo yönetim sistemi.", encoding="utf-8")
        (self.test_dir / "GLOSSARY.md").write_text("## Sözlük\n- `Tenant`: Organizasyon birimi", encoding="utf-8")
        (self.test_dir / "DB_MIGRATIONS.md").write_text("## Veritabanı\n- Tablo: `vehicles`", encoding="utf-8")
        (self.test_dir / "HANDOFF.md").write_text("## 1. Bu Oturumda Yapılanlar\n- Sprint 12 tamamlandı.", encoding="utf-8")

        # İki farklı PRD dokümanı ekle
        (self.test_dir / "docs" / "mobile-prd.md").write_text("# Mobil PRD\n### FR-001: Sürücü Girişi\nSürücüler mobil uygulamaya QR ile giriş yapar.", encoding="utf-8")
        (self.test_dir / "docs" / "admin-spec.md").write_text("# Admin Şartname\n### FR-002: Araç Takibi\nFilo yöneticisi araç konumlarını canlı haritada izler.", encoding="utf-8")

        res = summarize_project.run_summary(mode="long", root=self.test_dir)
        self.assertEqual(res, 0)

        output_file = self.test_dir / "docs" / "SUPER_APP_PROJECT_SUMMARY_LONG.md"
        self.assertTrue(output_file.is_file(), "Long konsolidasyon dosyası docs/ altında oluşturulmalı!")

        content = output_file.read_text(encoding="utf-8")
        self.assertIn('mode: "long"', content)
        self.assertIn("docs/mobile-prd.md", content)
        self.assertIn("docs/admin-spec.md", content)
        self.assertIn("Kurumsal filo yönetim sistemi", content)
        self.assertIn("Tenant", content)
        self.assertIn("vehicles", content)
        self.assertIn("Java 21 / Spring Boot 3", content)
        self.assertIn("## 6. Fonksiyonel & Teknik Şartname Konsolidasyonu", content)

    def test_versioning_stamp_and_archive_when_file_exists(self):
        """Mevcut dosyada sürüm artışı (v1.0 -> v1.1) ve docs/archive/ yedeğini test eder."""
        (self.test_dir / "PROJECT_BRIEF.md").write_text("---\ntitle: \"Demo\"\nslug: \"demo\"\nprimary_language: \"tr\"\nrelated_docs: []\n---\n", encoding="utf-8")

        # 1. İlk çalıştırma (v1.0)
        summarize_project.run_summary(mode="short", root=self.test_dir)
        output_file = self.test_dir / "docs" / "DEMO_PROJECT_SUMMARY_SHORT.md"
        c1 = output_file.read_text(encoding="utf-8")
        self.assertIn('version: "v1.0"', c1)

        # 2. İkinci çalıştırma (v1.1 olmalı ve arşiv oluşmalı)
        summarize_project.run_summary(mode="short", root=self.test_dir)
        c2 = output_file.read_text(encoding="utf-8")
        self.assertIn('version: "v1.1"', c2)

        # Arşiv dizinini kontrol et
        archive_dir = self.test_dir / "docs" / "archive"
        self.assertTrue(archive_dir.is_dir())
        archives = list(archive_dir.glob("DEMO_PROJECT_SUMMARY_SHORT_*.md"))
        self.assertGreaterEqual(len(archives), 1, "docs/archive/ altında yedek dosya bulunmalı!")

        # Revizyon tablosunda iki sürümün de olduğunu doğrula
        self.assertIn("v1.0", c2)
        self.assertIn("v1.1", c2)

    def test_project_brief_related_docs_sync(self):
        """PROJECT_BRIEF.md related_docs listesine dosyanın otomatik eklendiğini doğrular."""
        brief = self.test_dir / "PROJECT_BRIEF.md"
        brief.write_text("---\ntitle: \"KalanSüre\"\nslug: \"kalansure\"\nprimary_language: \"tr\"\nrelated_docs:\n  - \"HANDOFF.md\"\n---\n# Brief", encoding="utf-8")

        summarize_project.run_summary(mode="long", root=self.test_dir)

        updated_brief = brief.read_text(encoding="utf-8")
        self.assertIn("docs/KALANSURE_PROJECT_SUMMARY_LONG.md", updated_brief)

    def test_docs_path_enforcement(self):
        """docs/ dizini dışındaki yolların ValueError ile reddedildiğini test eder."""
        outside_file = self.test_dir / "KALANSURE_PROJECT_SUMMARY_LONG.md"
        with self.assertRaises(ValueError):
            summarize_project.validate_output_directory(outside_file, self.test_dir)

    def test_language_switch_en(self):
        """primary_language: en olduğunda İngilizce başlık ve meta verileri test eder."""
        brief = self.test_dir / "PROJECT_BRIEF.md"
        brief.write_text("---\ntitle: \"GlobalPortal\"\nslug: \"global_portal\"\nprimary_language: \"en\"\nrelated_docs: []\n---\n", encoding="utf-8")

        summarize_project.run_summary(mode="short", root=self.test_dir)
        output_file = self.test_dir / "docs" / "GLOBAL_PORTAL_PROJECT_SUMMARY_SHORT.md"
        content = output_file.read_text(encoding="utf-8")
        self.assertIn('language: "en"', content)
        self.assertIn("Project Executive Summary", content)

    def test_check_flag(self):
        """--check bayrağının dosya varlık durumuna göre doğru çıkış kodu verdiğini test eder."""
        brief = self.test_dir / "PROJECT_BRIEF.md"
        brief.write_text("---\ntitle: \"CheckTest\"\nslug: \"check_test\"\nprimary_language: \"tr\"\nrelated_docs: []\n---\n", encoding="utf-8")

        # Dosya yokken check 1 dönmeli
        res_missing = summarize_project.run_summary(mode="long", root=self.test_dir, check_only=True)
        self.assertEqual(res_missing, 1)

        # Dosya üretildikten sonra check 0 dönmeli
        summarize_project.run_summary(mode="long", root=self.test_dir)
        res_ok = summarize_project.run_summary(mode="long", root=self.test_dir, check_only=True)
        self.assertEqual(res_ok, 0)


if __name__ == "__main__":
    unittest.main()
