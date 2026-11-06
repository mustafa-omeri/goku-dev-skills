#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Unit tests for deployment-architect deployment_generator.py at its public seam."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

HERE = Path(__file__).resolve().parent
SCRIPTS_DIR = HERE.parent
sys.path.insert(0, str(SCRIPTS_DIR))


def _load_generator():
    import deployment_generator  # noqa: E402
    return deployment_generator


class DeploymentGeneratorSeamTests(unittest.TestCase):
    """Tests stack detection, hybrid multi-tier deployment plan generation, and rollback protocol."""

    def test_01_detects_hybrid_stack_react_frontend_springboot_backend(self):
        gen = _load_generator()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            # Frontend sub-project or root
            (root / "package.json").write_text(
                json.dumps({
                    "name": "frontend-app",
                    "dependencies": {"react": "^18.2.0", "react-dom": "^18.2.0"}
                }),
                encoding="utf-8",
            )
            # Backend pom.xml (Spring Boot)
            (root / "pom.xml").write_text(
                "<project><dependencies><dependency><groupId>org.springframework.boot</groupId>"
                "<artifactId>spring-boot-starter-web</artifactId></dependency></dependencies></project>",
                encoding="utf-8",
            )
            stack = gen.inspect_project(root)
            self.assertTrue(stack["has_frontend"])
            self.assertEqual(stack["frontend_type"], "react")
            self.assertTrue(stack["has_backend"])
            self.assertEqual(stack["backend_type"], "spring-boot")
            self.assertTrue(stack["is_hybrid"])

    def test_02_generates_vps_deployment_plan_with_nginx_and_rollback(self):
        gen = _load_generator()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "package.json").write_text(
                json.dumps({"name": "monolith-app", "dependencies": {"express": "^4.18.0"}}),
                encoding="utf-8",
            )
            target_config = {
                "environment": "production",
                "target_type": "vps",
                "os": "ubuntu-22.04",
                "domain": "api.example.com",
                "app_port": 3000,
                "database": "postgres",
            }
            res = gen.generate_deployment_plan(root, target_config)
            plan = res["plan_markdown"]
            self.assertIn("Bölüm 1: Altyapı ve Çalışma Zamanı Mimarisi", plan)
            self.assertIn("Nginx", plan)
            self.assertIn("Bölüm 2: Üretim Konfigürasyon", plan)
            self.assertIn("Bölüm 3: Veritabanı Migration", plan)
            self.assertIn("Bölüm 4: Geri Alma ve Acil Durum Protokolü (Rollback Playbook)", plan)
            self.assertIn("Expand-Contract", plan)
            self.assertIn("Bölüm 5: Dağıtım Sonrası Doğrulama & Smoke Test", plan)
            self.assertIn(".env.production.template", res["artifacts"])

    def test_03_generates_hybrid_plan_react_paas_backend_vps(self):
        gen = _load_generator()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "package.json").write_text(
                json.dumps({"name": "client-portal", "dependencies": {"react": "^18.0.0"}}),
                encoding="utf-8",
            )
            (root / "pom.xml").write_text(
                "<project><dependencies><dependency><groupId>org.springframework.boot</groupId>"
                "<artifactId>spring-boot-starter-web</artifactId></dependency></dependencies></project>",
                encoding="utf-8",
            )
            target_config = {
                "environment": "production",
                "target_type": "hybrid",
                "frontend": {"target": "paas", "provider": "vercel", "domain": "app.example.com"},
                "backend": {"target": "vps", "host": "api.example.com", "port": 8080, "runtime": "docker-compose"},
                "database": {"target": "managed", "provider": "supabase-postgres"},
            }
            res = gen.generate_deployment_plan(root, target_config)
            plan = res["plan_markdown"]
            self.assertIn("Hibrit Dağıtım Mimarisi", plan)
            self.assertIn("Vercel", plan)
            self.assertIn("api.example.com", plan)
            self.assertIn("Supabase", plan)
            self.assertIn("CORS", plan)

    def test_04_parse_declarative_target_yaml(self):
        gen = _load_generator()
        yaml_content = """
target_type: hybrid
environment: production
frontend:
  target: paas
  provider: vercel
backend:
  target: vps
  port: 8080
database:
  target: managed
  provider: postgres
"""
        config = gen.parse_target_yaml(yaml_content)
        self.assertEqual(config["target_type"], "hybrid")
        self.assertEqual(config["frontend"]["target"], "paas")
        self.assertEqual(config["backend"]["port"], 8080)


if __name__ == "__main__":
    unittest.main()
