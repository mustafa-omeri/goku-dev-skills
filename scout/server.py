#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Private Scout Web Server & Local API.

scout-catalog.html arayüzü üzerinden tek tıkla repos.json içine
yeni repo eklenmesini, anlık durum güncellemelerini, doğrudan
scout tetiklenmesini, toplu incelemeyi ve silme işlemlerini
sağlayan hafif yerel servis.

Kullanım:
    python scout/server.py
    python scout/server.py --port 5055
"""

from __future__ import annotations

import argparse
import json
import sys
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

# Windows Unicode çıkış desteği
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

SCOUT_DIR = Path(__file__).resolve().parent
CATALOG_HTML = SCOUT_DIR / "scout-catalog.html"
REPOS_JSON = SCOUT_DIR / "repos.json"

# Proje kök dizinini sys.path'e ekle (python scout/server.py veya python server.py için)
if str(SCOUT_DIR.parent) not in sys.path:
    sys.path.insert(0, str(SCOUT_DIR.parent))
if str(SCOUT_DIR) not in sys.path:
    sys.path.insert(0, str(SCOUT_DIR))

try:
    from scout.engine import (
        add_new_repo,
        scout_repo,
        scout_and_evaluate_repo,
        delete_repo,
        get_pending_repos,
        update_repos_table,
        parse_repo_info,
        is_existing_repo,
        find_existing_repo,
        deduplicate_repos,
        canonical_repo_key,
        normalize_repo_url,
        set_repo_status,
        start_repo_transfer,
        complete_repo_transfer
    )
except ImportError:
    from engine import (
        add_new_repo,
        scout_repo,
        scout_and_evaluate_repo,
        delete_repo,
        get_pending_repos,
        update_repos_table,
        parse_repo_info,
        is_existing_repo,
        find_existing_repo,
        deduplicate_repos,
        canonical_repo_key,
        normalize_repo_url,
        set_repo_status,
        start_repo_transfer,
        complete_repo_transfer
    )

try:
    from scout.generate_scout_catalog import parse_repos_md, build_catalog
except ImportError:
    try:
        from generate_scout_catalog import parse_repos_md, build_catalog
    except ImportError:
        try:
            from scout.generate_scout_catalog import parse_repos_md, main as build_catalog
        except ImportError:
            from generate_scout_catalog import parse_repos_md, main as build_catalog


class ScoutApiHandler(BaseHTTPRequestHandler):

    def _send_cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def _send_json(self, data: dict, status: int = HTTPStatus.OK):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self._send_cors_headers()
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(HTTPStatus.NO_CONTENT)
        self._send_cors_headers()
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path in ("/", "/index.html", "/catalog"):
            # En güncel HTML'i derleyip sun
            build_catalog()
            if not CATALOG_HTML.is_file():
                self.send_error(HTTPStatus.NOT_FOUND, "Catalog not found")
                return

            body = CATALOG_HTML.read_bytes()
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self._send_cors_headers()
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        if path == "/api/status":
            repos = parse_repos_md()
            self._send_json({
                "status": "online",
                "total_repos": len(repos),
                "pending_count": sum(1 for r in repos if (r.get("status") or "").upper() == "PENDING"),
                "planned_count": sum(1 for r in repos if (r.get("status") or "").upper() in ("PLANNED", "TO_INTEGRATE")),
                "transferring_count": sum(1 for r in repos if (r.get("status") or "").upper() == "TRANSFERRING"),
                "transferred_count": sum(1 for r in repos if (r.get("status") or "").upper() in ("TRANSFERRED", "AKTARILDI")),
                "rejected_count": sum(1 for r in repos if (r.get("status") or "").upper() in ("REJECTED", "ELENDI")),
                "suspended_count": sum(1 for r in repos if (r.get("status") or "").upper() in ("SUSPENDED", "ASKIDA")),
                "cancel_count": sum(1 for r in repos if (r.get("status") or "").upper() in ("CANCEL", "CANCELED", "CANCELLED", "IPTAL")),
                "repos": repos
            })
            return

        if path == "/api/repos":
            repos = parse_repos_md()
            self._send_json({"repos": repos})
            return

        if path == "/api/repos/dedup":
            cleaned, report = deduplicate_repos(auto_save=False)
            self._send_json({"status": "ok", "report": report})
            return

        if path == "/api/targets":
            try:
                from scout.targets import parse_targets_file, resolve_distribution_targets
            except ImportError:
                from targets import parse_targets_file, resolve_distribution_targets
            raw_entries = parse_targets_file()
            resolved = resolve_distribution_targets()
            self._send_json({
                "status": "ok",
                "raw_targets": [{
                    "path": str(e["path"]),
                    "raw_path": e["raw_path"],
                    "enabled": e["enabled"],
                    "notes": e.get("notes", "")
                } for e in raw_entries],
                "resolved_projects": resolved
            })
            return

        self._send_json({"error": "Endpoint bulunamadı"}, status=HTTPStatus.NOT_FOUND)

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path

        content_len = int(self.headers.get("Content-Length", 0))
        raw_body = self.rfile.read(content_len).decode("utf-8", errors="replace")

        try:
            payload = json.loads(raw_body) if raw_body else {}
        except json.JSONDecodeError:
            self._send_json({"error": "Geçersiz JSON gövdesi"}, status=HTTPStatus.BAD_REQUEST)
            return

        # 1. Yeni Repo Ekle
        if path == "/api/repos":
            url = payload.get("url", "").strip()
            layer = payload.get("layer", "Belirsiz").strip()
            skip_build = bool(payload.get("skip_build", False))

            if not url:
                self._send_json({"error": "Repo URL'si zorunludur."}, status=HTTPStatus.BAD_REQUEST)
                return

            try:
                owner, name = parse_repo_info(url)
                norm_url = normalize_repo_url(url)
            except ValueError as e:
                self._send_json({"error": str(e)}, status=HTTPStatus.BAD_REQUEST)
                return

            try:
                existing = find_existing_repo(url)
                already_exists = existing is not None
                ok = add_new_repo(url, layer=layer, rebuild=not skip_build)
                if not skip_build:
                    build_catalog()
                repos = parse_repos_md()
                action_text = f"güncellendi (zaten kayıtlıydı, Durum: {existing.get('status', '-')})." if already_exists else "başarıyla repos.json'a eklendi."
                self._send_json({
                    "success": True,
                    "is_update": already_exists,
                    "is_duplicate": already_exists,
                    "existing_status": existing.get("status") if existing else None,
                    "existing_verdict": existing.get("verdict") if existing else None,
                    "canonical_url": norm_url,
                    "message": f"'{norm_url}' {action_text}",
                    "repos": repos
                })
            except Exception as e:
                self._send_json({"error": f"Eklenirken hata oluştu: {e}"}, status=HTTPStatus.INTERNAL_SERVER_ERROR)
            return

        # 1b. Toplu Repo Ekle (Bulk Add API - Mükerrer Filtreli)
        if path == "/api/repos/bulk":
            urls = payload.get("urls", [])
            default_layer = payload.get("layer", "Belirsiz").strip()
            skip_duplicates = bool(payload.get("skip_duplicates", True))

            if not urls or not isinstance(urls, list):
                self._send_json({"error": "En az bir repo URL'si gereklidir."}, status=HTTPStatus.BAD_REQUEST)
                return

            results = []
            seen_in_batch = set()

            for item in urls:
                u = item.get("url", "").strip() if isinstance(item, dict) else str(item).strip()
                l = item.get("layer", default_layer).strip() if isinstance(item, dict) else default_layer
                if not u:
                    continue
                try:
                    owner, name = parse_repo_info(u)
                    norm_url = normalize_repo_url(u)
                    key = canonical_repo_key(owner, name)

                    # Gelen liste içinde mükerrer mi?
                    if key in seen_in_batch:
                        results.append({
                            "url": norm_url,
                            "success": True,
                            "is_update": True,
                            "skipped": True,
                            "reason": "Toplu liste içinde mükerrer"
                        })
                        continue
                    seen_in_batch.add(key)

                    existing = find_existing_repo(u)
                    existed = existing is not None

                    if existed and skip_duplicates:
                        results.append({
                            "url": norm_url,
                            "success": True,
                            "is_update": True,
                            "skipped": True,
                            "existing_status": existing.get("status"),
                            "reason": f"Zaten kayıtlı (Durum: {existing.get('status')})"
                        })
                        continue

                    add_new_repo(u, layer=l, rebuild=False)
                    results.append({
                        "url": norm_url,
                        "success": True,
                        "is_update": existed,
                        "skipped": False
                    })
                except Exception as ex:
                    results.append({"url": u, "success": False, "error": str(ex)})

            build_catalog()
            repos = parse_repos_md()
            self._send_json({
                "success": True,
                "total": len(results),
                "added_count": sum(1 for r in results if r["success"] and not r.get("is_update") and not r.get("skipped")),
                "updated_count": sum(1 for r in results if r["success"] and r.get("is_update") and not r.get("skipped")),
                "skipped_count": sum(1 for r in results if r.get("skipped")),
                "failed_count": sum(1 for r in results if not r["success"]),
                "results": results,
                "repos": repos
            })
            return

        # 1c. Mükerrer Kayıtları Temizle (Deduplicate API)
        if path == "/api/repos/dedup":
            try:
                cleaned, report = deduplicate_repos(auto_save=True)
                build_catalog()
                repos = parse_repos_md()
                self._send_json({
                    "success": True,
                    "report": report,
                    "repos": repos
                })
            except Exception as e:
                self._send_json({"error": f"Mükerrer temizleme hatası: {e}"}, status=HTTPStatus.INTERNAL_SERVER_ERROR)
            return

        # 2. Şimdi Tara & İncele (Scout Now)
        if path == "/api/scout-now":
            url = payload.get("url", "").strip()
            if not url:
                self._send_json({"error": "Repo URL'si zorunludur."}, status=HTTPStatus.BAD_REQUEST)
                return

            try:
                parse_repo_info(url)
                # İncelemeyi çalıştırıp değerlendir
                res = scout_and_evaluate_repo(url)
                if "error" in res:
                    self._send_json({"error": res["error"]}, status=HTTPStatus.INTERNAL_SERVER_ERROR)
                    return

                build_catalog()
                repos = parse_repos_md()
                self._send_json({
                    "success": True,
                    "message": f"'{url}' başarıyla incelendi ve karara bağlandı.",
                    "result": res,
                    "repos": repos
                })
            except Exception as e:
                self._send_json({"error": f"İnceleme sırasında hata: {e}"}, status=HTTPStatus.INTERNAL_SERVER_ERROR)
            return

        # 3. Tüm Bekleyenleri Tara (Scout All Pending)
        if path == "/api/scout-all":
            try:
                pending = get_pending_repos()
                if not pending:
                    self._send_json({"success": True, "message": "İncelenecek bekleyen repo bulunamadı.", "processed": 0})
                    return

                results = []
                for item in pending:
                    url = item.get("url", "")
                    if url:
                        res = scout_and_evaluate_repo(url)
                        results.append(res)

                build_catalog()
                repos = parse_repos_md()
                self._send_json({
                    "success": True,
                    "message": f"{len(results)} repo başarıyla incelendi.",
                    "processed": len(results),
                    "results": results,
                    "repos": repos
                })
            except Exception as e:
                self._send_json({"error": f"Toplu inceleme hatası: {e}"}, status=HTTPStatus.INTERNAL_SERVER_ERROR)
            return

        # 3b. Belirli Bir Sıraya Göre Kuyruk Tara (Scout Custom Queue)
        if path == "/api/scout-queue":
            urls = payload.get("urls", [])
            if not urls or not isinstance(urls, list):
                self._send_json({"error": "En az bir repo URL'si gereklidir."}, status=HTTPStatus.BAD_REQUEST)
                return

            results = []
            for u in urls:
                url_str = u.strip() if isinstance(u, str) else u.get("url", "").strip()
                if not url_str:
                    continue
                try:
                    res = scout_and_evaluate_repo(url_str)
                    results.append(res)
                except Exception as ex:
                    results.append({"url": url_str, "error": str(ex)})

            build_catalog()
            repos = parse_repos_md()
            self._send_json({
                "success": True,
                "message": f"{len(results)} repo belirlenen sırayla incelendi.",
                "processed": len(results),
                "results": results,
                "repos": repos
            })
            return

        # 4. Repo Sil (Delete Repo)
        if path == "/api/delete-repo":
            identifier = payload.get("id") or payload.get("url")
            if not identifier:
                self._send_json({"error": "Silinecek ID veya URL belirtilmelidir."}, status=HTTPStatus.BAD_REQUEST)
                return

            try:
                ok = delete_repo(identifier)
                if not ok:
                    self._send_json({"error": "Belirtilen repo bulunamadı veya silinemedi."}, status=HTTPStatus.NOT_FOUND)
                    return

                build_catalog()
                repos = parse_repos_md()
                self._send_json({
                    "success": True,
                    "message": "Repo listeden ve plandan başarıyla silindi.",
                    "repos": repos
                })
            except Exception as e:
                self._send_json({"error": f"Silme hatası: {e}"}, status=HTTPStatus.INTERNAL_SERVER_ERROR)
            return

                # 4b. Aktarımı Başlat (Start Transfer: status -> TRANSFERRING)
        if path == "/api/repos/transfer/start":
            identifier = payload.get("id") or payload.get("url")
            target_skill = payload.get("target_skill", "").strip()
            notes = payload.get("notes", "").strip()

            if not identifier:
                self._send_json({"error": "ID veya URL belirtilmelidir."}, status=HTTPStatus.BAD_REQUEST)
                return
            if not target_skill:
                self._send_json({"error": "Hedef skill/modül belirtilmelidir."}, status=HTTPStatus.BAD_REQUEST)
                return

            try:
                res = start_repo_transfer(identifier, target_skill=target_skill, notes=notes, rebuild=True)
                if not res.get("success"):
                    self._send_json({"error": res.get("error", "Aktarım başlatılamadı.")}, status=HTTPStatus.NOT_FOUND)
                    return
                build_catalog()
                repos = parse_repos_md()
                self._send_json({
                    "success": True,
                    "message": res.get("message", "Aktarım süreci başlatıldı."),
                    "repo": res.get("repo"),
                    "repos": repos
                })
            except Exception as e:
                self._send_json({"error": f"Aktarım başlatma hatası: {e}"}, status=HTTPStatus.INTERNAL_SERVER_ERROR)
            return

        # 4c. Aktarımı Tamamla (Complete Transfer: status -> TRANSFERRED)
        if path == "/api/repos/transfer/complete":
            identifier = payload.get("id") or payload.get("url")
            target_skill = payload.get("target_skill", "").strip()
            transferred_to = payload.get("transferred_to", "").strip()
            notes = payload.get("notes", "").strip()

            if not identifier:
                self._send_json({"error": "ID veya URL belirtilmelidir."}, status=HTTPStatus.BAD_REQUEST)
                return
            if not transferred_to:
                self._send_json({"error": "Aktarılan dosya veya modül yolu (transferred_to) belirtilmelidir."}, status=HTTPStatus.BAD_REQUEST)
                return

            try:
                res = complete_repo_transfer(
                    identifier,
                    target_skill=target_skill or "Genel",
                    transferred_to=transferred_to,
                    notes=notes,
                    rebuild=True
                )
                if not res.get("success"):
                    self._send_json({"error": res.get("error", "Aktarım tamamlanamadı.")}, status=HTTPStatus.NOT_FOUND)
                    return
                build_catalog()
                repos = parse_repos_md()
                self._send_json({
                    "success": True,
                    "message": res.get("message", "Aktarım başarıyla tamamlandı."),
                    "repo": res.get("repo"),
                    "repos": repos
                })
            except Exception as e:
                self._send_json({"error": f"Aktarım tamamlama hatası: {e}"}, status=HTTPStatus.INTERNAL_SERVER_ERROR)
            return

        # 5. Sisteme Entegre Et (Mark Integrated)
        if path == "/api/integrate":
            url = payload.get("url", "").strip()
            notes = payload.get("notes", "Sisteme dahil edildi.")
            if not url:
                self._send_json({"error": "Repo URL'si zorunludur."}, status=HTTPStatus.BAD_REQUEST)
                return

            try:
                update_repos_table(
                    repo_url=url,
                    layer=payload.get("layer", ""),
                    status="DONE",
                    verdict=f"AKTARILDI: {notes}",
                    plan_file=payload.get("plan_file", "")
                )
                build_catalog()
                repos = parse_repos_md()
                self._send_json({
                    "success": True,
                    "message": f"'{url}' sisteme aktarıldı olarak güncellendi.",
                    "repos": repos
                })
            except Exception as e:
                self._send_json({"error": f"Entegrasyon güncelleme hatası: {e}"}, status=HTTPStatus.INTERNAL_SERVER_ERROR)
            return

        # 6. Repo Durumunu Güncelle (Set Status: PENDING / DONE / SUSPENDED / CANCEL)
        if path in ("/api/repos/status", "/api/status-repo"):
            identifier = payload.get("id") or payload.get("url")
            new_status = (payload.get("status") or "").strip().upper()
            verdict = payload.get("verdict")
            if not identifier:
                self._send_json({"error": "ID veya URL belirtilmelidir."}, status=HTTPStatus.BAD_REQUEST)
                return
            if not new_status:
                self._send_json({"error": "Yeni durum (status) belirtilmelidir."}, status=HTTPStatus.BAD_REQUEST)
                return

            if new_status in ("CANCELED", "CANCELLED"):
                new_status = "CANCEL"
            valid_statuses = ("PENDING", "DONE", "SUSPENDED", "CANCEL")
            if new_status not in valid_statuses:
                self._send_json({"error": f"Geçersiz durum '{new_status}'. Geçerli durumlar: {', '.join(valid_statuses)}"}, status=HTTPStatus.BAD_REQUEST)
                return

            try:
                ok = set_repo_status(identifier, new_status, verdict=verdict, rebuild=True)
                if not ok:
                    self._send_json({"error": "Belirtilen repo bulunamadı."}, status=HTTPStatus.NOT_FOUND)
                    return
                build_catalog()
                repos = parse_repos_md()
                self._send_json({
                    "success": True,
                    "message": f"Repo durumu '{new_status}' olarak güncellendi.",
                    "status": new_status,
                    "repos": repos
                })
            except Exception as e:
                self._send_json({"error": f"Durum güncelleme hatası: {e}"}, status=HTTPStatus.INTERNAL_SERVER_ERROR)
            return

        # 5. Dağıtım Hedefini Aç/Kapat (Toggle Target API)
        if path == "/api/targets/toggle":
            target_path_str = payload.get("path", "").strip()
            enabled_val = payload.get("enabled")
            if not target_path_str or enabled_val is None:
                self._send_json({"error": "path ve enabled alanları zorunludur."}, status=HTTPStatus.BAD_REQUEST)
                return

            try:
                targets_file = SCOUT_DIR / "targets.md"
                if not targets_file.is_file():
                    self._send_json({"error": "scout/targets.md dosyası bulunamadı."}, status=HTTPStatus.NOT_FOUND)
                    return

                content = targets_file.read_text(encoding="utf-8")
                lines = content.splitlines()
                updated = False
                new_status = "ON" if enabled_val else "OFF"
                norm_target = target_path_str.replace("\\", "/").rstrip("/").lower()

                new_lines = []
                for line in lines:
                    clean = line.strip()
                    # 1. Tablo biçimi (| ON/OFF | path | ...)
                    if clean.startswith("|") and not clean.startswith("|---"):
                        parts = line.split("|")
                        if len(parts) >= 3:
                            path_in_col = parts[2].strip().replace("\\", "/").rstrip("/").lower()
                            if path_in_col == norm_target:
                                parts[1] = f" {new_status} "
                                line = "|".join(parts)
                                updated = True
                    # 2. Düz çizgi biçimi (ON/OFF | path)
                    elif "|" in clean:
                        parts = line.split("|")
                        if len(parts) >= 2:
                            path_in_col = parts[1].strip().replace("\\", "/").rstrip("/").lower()
                            if path_in_col == norm_target:
                                parts[0] = f"{new_status}  "
                                line = "|".join(parts)
                                updated = True
                    # 3. Liste biçimi (- [x] path)
                    elif clean.startswith("- ["):
                        m = re.match(r"^-\s*\[[ xX]\]\s+(.+)$", clean)
                        if m:
                            path_in_col = m.group(1).strip().replace("\\", "/").rstrip("/").lower()
                            if path_in_col == norm_target:
                                mark = "x" if enabled_val else " "
                                line = re.sub(r"-\s*\[[ xX]\]", f"- [{mark}]", line)
                                updated = True
                    new_lines.append(line)

                if updated:
                    targets_file.write_text("\n".join(new_lines) + "\n", encoding="utf-8")

                try:
                    from scout.targets import resolve_distribution_targets
                except ImportError:
                    from targets import resolve_distribution_targets
                self._send_json({
                    "success": True,
                    "updated": updated,
                    "message": f"'{target_path_str}' durumu {new_status} olarak güncellendi.",
                    "resolved_projects": resolve_distribution_targets()
                })
            except Exception as e:
                self._send_json({"error": f"Hedef güncelleme hatası: {e}"}, status=HTTPStatus.INTERNAL_SERVER_ERROR)
            return

        self._send_json({"error": "Bilinmeyen POST rotası"}, status=HTTPStatus.NOT_FOUND)

    def log_message(self, format, *args):
        # Sessiz ve temiz konsol logu
        sys.stdout.write(f"[Scout Server] {self.address_string()} - {format % args}\n")


def run_server(port: int = 5055):
    server_address = ("", port)
    httpd = ThreadingHTTPServer(server_address, ScoutApiHandler)
    print("=" * 60)
    print("🚀 Scout Local Dashboard & API Server Başlatıldı!")
    print(f"👉 Tarayıcınızda açın: http://localhost:{port}")
    print("👉 repos.json dosyasına doğrudan web üzerinden repo ekleyebilirsiniz.")
    print("Durdurmak için Ctrl+C tuşlayın.")
    print("=" * 60)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[OK] Sunucu durduruldu.")
        httpd.server_close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scout Web Server")
    parser.add_argument("--port", type=int, default=5055, help="Sunucu portu (varsayılan: 5055)")
    args = parser.parse_args()
    run_server(args.port)
