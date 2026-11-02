#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Scout Dağıtım Hedefleri (targets.py) Birim Testleri."""

import tempfile
import unittest
from pathlib import Path

from scout.targets import (
    parse_targets_file,
    looks_like_project,
    detect_project_stack,
    discover_projects_in_directory,
    resolve_distribution_targets,
    build_delivery_config_from_targets
)


class TestScoutTargets(unittest.TestCase):

    def test_parse_targets_file_table_format(self):
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".md", delete=False) as f:
            f.write("""# Targets Table
| Durum | Hedef Path | Açıklama |
|---|---|---|
| ON | C:/my/active/project | Aktif Proje |
| OFF | C:/my/passive/project | Pasif Proje |
| [x] | C:/my/checked/project | Onay Kutusu |
| [ ] | C:/my/unchecked/project | Onaysız Kutu |
""")
            t_path = Path(f.name)

        try:
            entries = parse_targets_file(t_path)
            self.assertEqual(len(entries), 4)
            self.assertTrue(entries[0]["enabled"])
            self.assertIn("active", str(entries[0]["path"]).replace("\\", "/"))
            self.assertFalse(entries[1]["enabled"])
            self.assertTrue(entries[2]["enabled"])
            self.assertFalse(entries[3]["enabled"])
        finally:
            if t_path.exists():
                t_path.unlink()

    def test_parse_targets_file_list_and_line_format(self):
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".md", delete=False) as f:
            f.write("""# Targets List
ON  | C:/direct/active
OFF | C:/direct/passive
- [x] C:/checkbox/active
- [ ] C:/checkbox/passive
<!--
ON | C:/ignored/comment
-->
""")
            t_path = Path(f.name)

        try:
            entries = parse_targets_file(t_path)
            self.assertEqual(len(entries), 4)
            self.assertTrue(entries[0]["enabled"])
            self.assertFalse(entries[1]["enabled"])
            self.assertTrue(entries[2]["enabled"])
            self.assertFalse(entries[3]["enabled"])
            # HTML yorum içindeki satır okunmamalı
            paths = [str(e["path"]).replace("\\", "/") for e in entries]
            self.assertFalse(any("ignored" in p for p in paths))
        finally:
            if t_path.exists():
                t_path.unlink()

    def test_looks_like_project(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)
            # Henüz belirteç yok
            self.assertFalse(looks_like_project(p))

            # package.json ekle
            pkg = p / "package.json"
            pkg.write_text("{}", encoding="utf-8")
            self.assertTrue(looks_like_project(p))
            pkg.unlink()

            # pom.xml ekle
            pom = p / "pom.xml"
            pom.write_text("<project></project>", encoding="utf-8")
            self.assertTrue(looks_like_project(p))
            pom.unlink()

            # .agent klasörü ekle
            agent = p / ".agent"
            agent.mkdir()
            self.assertTrue(looks_like_project(p))

    def test_detect_project_stack(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)
            (p / "package.json").write_text("{}", encoding="utf-8")
            self.assertEqual(detect_project_stack(p), "frontend")

            (p / "pom.xml").write_text("<project></project>", encoding="utf-8")
            self.assertEqual(detect_project_stack(p), "backend+frontend")

    def test_discover_projects_in_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            # Alt projeler oluştur
            sub1 = root / "workspace1" / "projA"
            sub1.mkdir(parents=True)
            (sub1 / "package.json").write_text("{}", encoding="utf-8")

            sub2 = root / "workspace2" / "projB"
            sub2.mkdir(parents=True)
            (sub2 / "pom.xml").write_text("<project/>", encoding="utf-8")

            # İhmal edilen klasör
            ignored = root / "node_modules" / "submodule"
            ignored.mkdir(parents=True)
            (ignored / "package.json").write_text("{}", encoding="utf-8")

            discovered = discover_projects_in_directory(root, max_depth=3)
            discovered_names = [d.name for d in discovered]

            self.assertIn("projA", discovered_names)
            self.assertIn("projB", discovered_names)
            self.assertNotIn("submodule", discovered_names)

    def test_resolve_distribution_targets_single_and_general(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            p1 = root / "proj1"
            p1.mkdir()
            (p1 / "package.json").write_text("{}", encoding="utf-8")

            general_ws = root / "generalWS"
            p2 = general_ws / "proj2"
            p2.mkdir(parents=True)
            (p2 / "pom.xml").write_text("<project/>", encoding="utf-8")

            t_file = root / "targets.md"
            t_file.write_text(f"""| Durum | Hedef Path | Açıklama |
|---|---|---|
| ON | {p1} | Tekil Aktif |
| OFF | {general_ws} | Genel Pasif |
""", encoding="utf-8")

            resolved = resolve_distribution_targets(t_file)
            self.assertEqual(len(resolved), 2)
            by_id = {r["id"]: r for r in resolved}
            self.assertTrue(by_id["proj1"]["enabled"])
            self.assertEqual(by_id["proj1"]["source_type"], "single")
            self.assertFalse(by_id["proj2"]["enabled"])
            self.assertEqual(by_id["proj2"]["source_type"], "general")

    def test_build_delivery_config_from_targets(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            p1 = root / "sampleProj"
            p1.mkdir()
            (p1 / "package.json").write_text("{}", encoding="utf-8")

            t_file = root / "targets.md"
            t_file.write_text(f"ON | {p1}\n", encoding="utf-8")

            cfg = build_delivery_config_from_targets(t_file)
            self.assertIn("source", cfg)
            self.assertIn("backupRoot", cfg)
            self.assertIn("rootFiles", cfg)
            self.assertIn("projects", cfg)
            self.assertEqual(len(cfg["projects"]), 1)
            self.assertEqual(cfg["projects"][0]["id"], "sampleProj")
            self.assertTrue(cfg["projects"][0]["enabled"])


if __name__ == "__main__":
    unittest.main()
