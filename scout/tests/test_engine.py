#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Private Scout Engine birim testleri."""

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from scout.engine import (
    parse_repo_info,
    detect_tech_stack_and_layer,
    build_directory_tree,
    safe_rmtree,
    update_repos_table,
    get_pending_repos,
    evaluate_fingerprint,
    delete_repo,
    add_new_repo,
    load_repos,
    save_repos,
    is_existing_repo,
    find_existing_repo,
    deduplicate_repos,
    canonical_repo_key,
    normalize_repo_url,
    set_repo_status
)


class TestScoutEngine(unittest.TestCase):

    def test_parse_repo_info_valid(self):
        owner, name = parse_repo_info("https://github.com/shadcn-ui/ui")
        self.assertEqual(owner, "shadcn-ui")
        self.assertEqual(name, "ui")

        owner2, name2 = parse_repo_info("https://github.com/spring-projects/spring-boot.git/")
        self.assertEqual(owner2, "spring-projects")
        self.assertEqual(name2, "spring-boot")

    def test_parse_repo_info_invalid(self):
        with self.assertRaises(ValueError):
            parse_repo_info("https://gitlab.com/user/project")
        with self.assertRaises(ValueError):
            parse_repo_info("invalid_url")

    def test_detect_tech_stack_frontend(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            pkg = tmp_path / "package.json"
            pkg.write_text(json.dumps({
                "dependencies": {
                    "react": "^18.2.0",
                    "tailwindcss": "^3.4.0"
                }
            }), encoding="utf-8")
            (tmp_path / "Button.tsx").write_text("// test", encoding="utf-8")

            res = detect_tech_stack_and_layer(tmp_path)
            self.assertIn("Frontend", res["primary_layer"])
            self.assertTrue(any("react" in d for d in res["dependencies"]))

    def test_detect_tech_stack_backend(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            (tmp_path / "pom.xml").write_text("<project></project>", encoding="utf-8")
            (tmp_path / "Dockerfile").write_text("FROM openjdk:21", encoding="utf-8")

            res = detect_tech_stack_and_layer(tmp_path)
            self.assertIn("Backend", res["primary_layer"])
            self.assertTrue(any("Maven" in s for s in res["backend_signals"]))
            self.assertTrue(any("Docker" in s for s in res["backend_signals"]))

    def test_safe_rmtree(self):
        tmp = tempfile.mkdtemp()
        p = Path(tmp) / "sub"
        p.mkdir(parents=True, exist_ok=True)
        (p / "file.txt").write_text("content", encoding="utf-8")
        self.assertTrue(safe_rmtree(Path(tmp)))
        self.assertFalse(Path(tmp).exists())

    def test_scout_catalog_html_generation(self):
        from scout.generate_scout_catalog import parse_repos_md, generate_html
        repos = parse_repos_md()
        self.assertIsInstance(repos, list)
        html_out = generate_html(repos)
        self.assertIn("Private Repo Scout & Intelligence", html_out)
        self.assertIn("shadcn-ui", html_out)
        self.assertIn("badge-private", html_out)
        self.assertIn("addRepoModal", html_out)
        self.assertIn("integrateModal", html_out)
        self.assertIn("Yeni Repo Ekle", html_out)

    def test_add_and_delete_repo_functionality(self):
        test_url = "https://github.com/test-org/dummy-repo-to-verify-add-and-del"
        
        # Test reposu ekle
        ok = add_new_repo(test_url, layer="Frontend")
        self.assertTrue(ok)

        # Pending listesinde var mı
        pending = get_pending_repos()
        urls = [p["url"] for p in pending]
        self.assertIn(test_url, urls)

        # Silme işlemi
        del_ok = delete_repo(test_url)
        self.assertTrue(del_ok)

        # Artık listede olmamalı
        repos = load_repos()
        urls_after = [r.get("url") for r in repos]
        self.assertNotIn(test_url, urls_after)

    def test_evaluate_fingerprint(self):
        mock_fp_seo = {
            "name": "super-seo-tool",
            "owner": "test-owner",
            "repo_url": "https://github.com/test-owner/super-seo-tool",
            "tech_stack": {"primary_layer": "Tooling / Agentic"},
            "readme_head": "This repository provides SEO optimization, SERP ranking strategies and keywords.",
            "total_files": 12
        }
        # Fallback mantığının doğrulanması (hızlı ve deterministik)
        layer, verdict, plan_md = evaluate_fingerprint(mock_fp_seo, use_agent=False)
        self.assertIn("ZENGINLESTIR", verdict)
        self.assertIn("SEO", verdict)
        self.assertIn("Cerrahi Entegrasyon Planı", plan_md)

    def test_is_existing_repo(self):
        # Bilinen mevcut bir reponun tüm varyasyonları
        self.assertTrue(is_existing_repo("https://github.com/shadcn-ui/ui"))
        self.assertTrue(is_existing_repo("https://github.com/shadcn-ui/ui/"))
        self.assertTrue(is_existing_repo("https://github.com/shadcn-ui/ui.git"))
        self.assertTrue(is_existing_repo("https://github.com/Shadcn-UI/ui"))
        self.assertTrue(is_existing_repo("shadcn-ui/ui"))
        self.assertTrue(is_existing_repo("http://github.com/shadcn-ui/ui"))
        self.assertTrue(is_existing_repo("git@github.com:shadcn-ui/ui.git"))
        # Var olmayan hayali repo
        self.assertFalse(is_existing_repo("https://github.com/non-existent-user-12345/non-existent-repo"))

    def test_canonical_repo_key_and_normalize_url(self):
        self.assertEqual(canonical_repo_key("https://github.com/Shadcn-UI/UI.git/"), "shadcn-ui/ui")
        self.assertEqual(canonical_repo_key("shadcn-ui/ui"), "shadcn-ui/ui")
        self.assertEqual(canonical_repo_key("git@github.com:shadcn-ui/ui.git"), "shadcn-ui/ui")
        self.assertEqual(normalize_repo_url("shadcn-ui/ui"), "https://github.com/shadcn-ui/ui")
        self.assertEqual(normalize_repo_url("https://github.com/shadcn-ui/ui.git/"), "https://github.com/shadcn-ui/ui")

    def test_deduplicate_repos(self):
        mock_repos = [
            {"id": 1, "url": "https://github.com/demo/repo", "owner": "demo", "name": "repo", "status": "DONE", "verdict": "BIZ_DAHA_IYIYIZ", "layer": "Frontend"},
            {"id": 2, "url": "https://github.com/demo/repo.git", "owner": "demo", "name": "repo", "status": "PENDING", "verdict": "-", "layer": "Belirsiz"},
            {"id": 3, "url": "https://github.com/Demo/Repo", "owner": "Demo", "name": "Repo", "status": "AKTARILDI", "verdict": "AKTARILDI", "layer": "Frontend"},
            {"id": 4, "url": "https://github.com/other/tool", "owner": "other", "name": "tool", "status": "PENDING", "verdict": "-", "layer": "Tooling"}
        ]
        cleaned, report = deduplicate_repos(mock_repos, auto_save=False)
        self.assertEqual(report["duplicates_removed"], 2)
        self.assertEqual(report["final_count"], 2)
        self.assertEqual(len(cleaned), 2)
        demo_repo = [r for r in cleaned if "demo/repo" in r["url"].lower()][0]
        self.assertEqual(demo_repo["status"], "AKTARILDI")
        self.assertEqual(demo_repo["id"], 1)
        self.assertEqual(cleaned[1]["id"], 2)

    def test_html_dedup_features(self):
        from scout.generate_scout_catalog import parse_repos_md, generate_html
        repos = parse_repos_md()
        html_out = generate_html(repos)
        self.assertIn("Mükerrer Kontrolü", html_out)
        self.assertIn("runDedupCheck", html_out)
        self.assertIn("singleRepoWarning", html_out)
        self.assertIn("bulkRepoSummaryBar", html_out)
        self.assertIn("bulkSkipDuplicates", html_out)
        self.assertIn("composerSkipDuplicates", html_out)
        self.assertIn("canonicalRepoKey", html_out)

    def test_bulk_add_and_modal_keep_open_features_in_html(self):
        from scout.generate_scout_catalog import parse_repos_md, generate_html
        repos = parse_repos_md()
        html_out = generate_html(repos)
        # Bulk ekleme ve tab bileşenleri
        self.assertIn("tabBtnBulk", html_out)
        self.assertIn("bulkRepoUrls", html_out)
        self.assertIn("bulkItemList", html_out)
        self.assertIn("bulkProgressBar", html_out)
        self.assertIn("pasteFromClipboardToBulk", html_out)
        self.assertIn("extractGithubRepos", html_out)
        self.assertIn("startBulkAdd", html_out)
        self.assertIn("singleCloseOnAdd", html_out)
        # Popup'ın kapanmasını önleyen opsiyonel checkbox ve durum koruma
        self.assertIn("Eklemeden sonra pencereyi kapat", html_out)

    def test_scout_queue_and_ordered_inspection_in_html(self):
        from scout.generate_scout_catalog import parse_repos_md, generate_html
        repos = parse_repos_md()
        html_out = generate_html(repos)
        # Kuyruk yönetimi ve sıralı inceleme bileşenleri
        self.assertIn("queueModal", html_out)
        self.assertIn("floatingQueueBar", html_out)
        self.assertIn("queueToolbarBtn", html_out)
        self.assertIn("queueItemList", html_out)
        self.assertIn("toggleQueueRepo", html_out)
        self.assertIn("startQueueScout", html_out)
        self.assertIn("moveQueueItem", html_out)
        self.assertIn("addAllPendingToQueue", html_out)

    def test_html_javascript_syntax_validity(self):
        import re, shutil, subprocess
        if not shutil.which("node"):
            self.skipTest("node CLI yüklü değil, JS sözdizimi testi atlandı.")
        from scout.generate_scout_catalog import parse_repos_md, generate_html
        repos = parse_repos_md()
        html_out = generate_html(repos)
        scripts = re.findall(r'<script>(.*?)</script>', html_out, re.DOTALL)
        self.assertTrue(len(scripts) > 0, "En az bir <script> bloğu bulunmalı")
        for idx, script in enumerate(scripts):
            res = subprocess.run(["node", "--check", "-"], input=script, encoding="utf-8", capture_output=True)
            self.assertEqual(res.returncode, 0, f"Script #{idx} sözdizimi hatası içeriyor: {res.stderr}")

    def test_set_repo_status_suspended_and_cancel_persistence(self):
        test_url = "https://github.com/test-org/dummy-repo-status-test"
        
        # 1. Repo ekle
        add_new_repo(test_url, layer="Backend")
        
        try:
            # 2. SUSPENDED durumuna al
            ok = set_repo_status(test_url, "SUSPENDED", verdict="Geliştirme askıya alındı", rebuild=False)
            self.assertTrue(ok)
            repos = load_repos()
            matched = find_existing_repo(test_url, repos)
            self.assertIsNotNone(matched)
            self.assertEqual(matched["status"], "SUSPENDED")
            self.assertIn("askıya alındı", matched.get("verdict", ""))

            # 3. CANCEL durumuna al (CANCELED alias testi)
            ok = set_repo_status(test_url, "CANCELED", verdict="Kullanımdan vazgeçildi", rebuild=False)
            self.assertTrue(ok)
            repos = load_repos()
            matched = find_existing_repo(test_url, repos)
            self.assertIsNotNone(matched)
            self.assertEqual(matched["status"], "CANCEL")

            # 4. Geçersiz durum ValueError fırlatmalı
            with self.assertRaises(ValueError):
                set_repo_status(test_url, "INVALID_STATE", rebuild=False)

            # 5. update_repos_table mevcut CANCEL veya SUSPENDED durumunu PENDING ile ezmemeli
            update_repos_table(test_url, "Backend", "PENDING", "Mevcut iptal", "plans/test.md", rebuild=False)
            repos_after = load_repos()
            matched_after = find_existing_repo(test_url, repos_after)
            self.assertEqual(matched_after["status"], "CANCEL", "CANCEL statüsü PENDING ile ezilmemeli")
        finally:
            delete_repo(test_url)

    def test_server_api_status_repo(self):
        import threading
        from urllib.request import Request, urlopen
        from urllib.error import HTTPError
        from scout.server import ThreadingHTTPServer, ScoutApiHandler
        
        test_url = "https://github.com/test-org/dummy-repo-api-status-test"
        add_new_repo(test_url, layer="Tooling / Agentic")

        server = ThreadingHTTPServer(("127.0.0.1", 0), ScoutApiHandler)
        port = server.server_address[1]
        t = threading.Thread(target=server.serve_forever, daemon=True)
        t.start()

        try:
            base_url = f"http://127.0.0.1:{port}"
            # 1. SUSPENDED durumuna al
            req = Request(
                f"{base_url}/api/repos/status",
                data=json.dumps({"url": test_url, "status": "SUSPENDED"}).encode("utf-8"),
                headers={"Content-Type": "application/json"}
            )
            with urlopen(req) as resp:
                self.assertEqual(resp.status, 200)
                data = json.loads(resp.read().decode("utf-8"))
                self.assertTrue(data.get("success"))
                matched = find_existing_repo(test_url, data.get("repos", []))
                self.assertIsNotNone(matched)
                self.assertEqual(matched["status"], "SUSPENDED")

            # 2. CANCEL durumuna al
            req2 = Request(
                f"{base_url}/api/repos/status",
                data=json.dumps({"url": test_url, "status": "CANCEL"}).encode("utf-8"),
                headers={"Content-Type": "application/json"}
            )
            with urlopen(req2) as resp:
                self.assertEqual(resp.status, 200)
                data2 = json.loads(resp.read().decode("utf-8"))
                self.assertTrue(data2.get("success"))
                matched2 = find_existing_repo(test_url, data2.get("repos", []))
                self.assertIsNotNone(matched2)
                self.assertEqual(matched2["status"], "CANCEL")

            # 3. Geçersiz durum -> HTTP 400
            req_bad = Request(
                f"{base_url}/api/repos/status",
                data=json.dumps({"url": test_url, "status": "UNKNOWN"}).encode("utf-8"),
                headers={"Content-Type": "application/json"}
            )
            with self.assertRaises(HTTPError) as ctx:
                urlopen(req_bad)
            self.assertEqual(ctx.exception.code, 400)

            # 4. Eksik identifier -> HTTP 400
            req_missing = Request(
                f"{base_url}/api/repos/status",
                data=json.dumps({"status": "SUSPENDED"}).encode("utf-8"),
                headers={"Content-Type": "application/json"}
            )
            with self.assertRaises(HTTPError) as ctx:
                urlopen(req_missing)
            self.assertEqual(ctx.exception.code, 400)
        finally:
            server.shutdown()
            server.server_close()
            delete_repo(test_url)

    def test_html_suspended_and_cancel_ui_elements(self):
        from scout.generate_scout_catalog import parse_repos_md, generate_html
        repos = parse_repos_md()
        html_out = generate_html(repos)

        # Yeni durum rozetleri ve kart sınıfları
        self.assertIn("badge-suspended", html_out)
        self.assertIn("badge-cancel", html_out)
        self.assertIn("card-suspended", html_out)
        self.assertIn("card-cancel", html_out)
        self.assertIn("verdict-suspended", html_out)
        self.assertIn("verdict-cancel", html_out)

        # Yeni sayaç ve sekme kimlikleri
        self.assertIn("suspendedBadge", html_out)
        self.assertIn("cancelBadge", html_out)
        self.assertIn("tabCountSuspended", html_out)
        self.assertIn("tabCountCancel", html_out)

        # İstemci tarafı durum değiştirme fonksiyonu ve seçim menüsü
        self.assertIn("changeRepoStatus", html_out)
        self.assertIn("status-select", html_out)



if __name__ == "__main__":
    unittest.main()
