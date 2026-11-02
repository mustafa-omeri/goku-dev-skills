#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Private Repo Scout Engine — GitHub repolarını geçici alana indirip

yapısal parmak izini çıkaran, katman analizini yapan ve temizleyen motor.

Kullanım:
    python scout/engine.py --repo https://github.com/owner/repo
    python scout/engine.py --next-pending
    python scout/engine.py --cleanup <repo-name>
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import stat
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    from scout.generate_scout_catalog import main as build_scout_catalog
except ImportError:
    build_scout_catalog = None

# Windows Unicode çıkış desteği
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

SCOUT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCOUT_DIR.parent
TEMP_DIR = SCOUT_DIR / "temp"
PLANS_DIR = SCOUT_DIR / "plans"
REPOS_JSON = SCOUT_DIR / "repos.json"

IGNORED_DIRS = {
    ".git", ".github", ".idea", ".vscode", "node_modules", "vendor",
    "target", "build", "dist", ".next", ".nuxt", "__pycache__",
    ".pytest_cache", ".venv", "venv", "env", "bin", "obj"
}

VALID_STATUSES = (
    "PENDING",
    "ANALYZED",
    "PLANNED",
    "TRANSFERRING",
    "TRANSFERRED",
    "REJECTED",
    "SUSPENDED",
    "CANCEL",
    "DONE"  # Geriye dönük uyumluluk takma adı
)


def record_repo_history(
    repo: Dict[str, Any],
    action: str,
    status: str,
    note: str,
    extra: Optional[Dict[str, Any]] = None
) -> None:
    """Reponun geçmiş hareket kaydına (audit trail) tarihli bir işlem ekler."""
    history = repo.setdefault("history", [])
    entry = {
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "action": action,
        "status": status,
        "note": note
    }
    if extra:
        entry.update(extra)
    history.append(entry)


def migrate_legacy_statuses(repos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Mevcut repos.json içindeki eski 'DONE' kayıtlarını verdict içeriğine göre zenginleştirir ve ilerleme bilgisi atar."""
    for r in repos:
        st = (r.get("status") or "").strip().upper()
        v = (r.get("verdict") or "").upper()
        
        # 1. Eski DONE veya belirsiz durumların migrasyonu
        if st in ("DONE", "INCELENDI", "ANALYZED"):
            if "AKTARILDI" in v:
                r["status"] = "TRANSFERRED"
                r["progress"] = 100
            elif "BIZ_DAHA_IYIYIZ" in v or "DAHA IYIYIZ" in v:
                r["status"] = "REJECTED"
                r["progress"] = 100
            elif "ZENGINLESTIR" in v or "KISMEN_ALINABILIR" in v or "KABUL" in v:
                r["status"] = "PLANNED"
                r["progress"] = 25
            else:
                r["status"] = "PLANNED"
                r["progress"] = 25
        elif st == "PENDING":
            r["progress"] = 0
        elif st == "TRANSFERRING":
            r["progress"] = r.get("progress", 50)
        elif st in ("TRANSFERRED", "AKTARILDI"):
            r["status"] = "TRANSFERRED"
            r["progress"] = 100
        elif st in ("REJECTED", "ELENDI"):
            r["status"] = "REJECTED"
            r["progress"] = 100
        elif st in ("SUSPENDED", "ASKIDA"):
            r["status"] = "SUSPENDED"
            r["progress"] = r.get("progress", 0)
        elif st in ("CANCEL", "CANCELED", "CANCELLED", "IPTAL"):
            r["status"] = "CANCEL"
            r["progress"] = r.get("progress", 0)

        # 2. History dizisi kontrolü
        if "history" not in r or not isinstance(r["history"], list) or len(r["history"]) == 0:
            init_date = r.get("date") or datetime.now().strftime("%Y-%m-%d")
            r["history"] = [{
                "date": f"{init_date} 09:00",
                "action": "ANALYZED" if r["status"] != "PENDING" else "ADDED",
                "status": r["status"],
                "note": r.get("verdict", "Kayıt oluşturuldu.")
            }]
    return repos

GITHUB_URL_RE = re.compile(
    r"^https://github\.com/([a-zA-Z0-9_\-\.]+)/([a-zA-Z0-9_\-\.]+?)(?:\.git)?/?$"
)


def remove_readonly(func, path, excinfo):
    """Windows'ta salt okunur .git dosyalarını silmek için izin düzeltici."""
    try:
        os.chmod(path, stat.S_IWRITE)
        func(path)
    except Exception:
        pass


def safe_rmtree(path: Path) -> bool:
    """Klasörü Windows izin hatalarına takılmadan güvenle siler."""
    if not path.exists():
        return True
    try:
        shutil.rmtree(path, onerror=remove_readonly)
        return True
    except Exception as e:
        print(f"[UYARI] Klasör silinirken hata: {e}", file=sys.stderr)
        return False


def parse_repo_info(url: str) -> Tuple[str, str]:
    """GitHub URL, SSH adresi veya 'owner/repo' kısa adından owner ve repo adını ayıklar."""
    raw = url.strip()
    if not raw:
        raise ValueError("Boş repo URL veya adı.")

    # 1. SSH: git@github.com:owner/repo(.git)
    ssh_match = re.match(r"^git@github\.com:([a-zA-Z0-9_\-\.]+)/([a-zA-Z0-9_\-\.]+?)(?:\.git)?/?$", raw)
    if ssh_match:
        return ssh_match.group(1), ssh_match.group(2)

    # 2. HTTP(S): (https?://)(www.)github.com/owner/repo(.git)(/)
    web_match = re.match(r"^(?:https?://)?(?:www\.)?github\.com/([a-zA-Z0-9_\-\.]+)/([a-zA-Z0-9_\-\.]+?)(?:\.git)?/?(?:[#?].*)?$", raw)
    if web_match:
        return web_match.group(1), web_match.group(2)

    # 3. Kısa format: owner/repo
    short_match = re.match(r"^([a-zA-Z0-9_\-\.]+)/([a-zA-Z0-9_\-\.]+?)(?:\.git)?/?$", raw)
    if short_match:
        owner, name = short_match.group(1), short_match.group(2)
        reserved = {"settings", "explore", "topics", "trending", "collections", "features", "pricing", "security", "enterprise", "readme"}
        if owner.lower() not in reserved and name.lower() not in reserved:
            return owner, name

    raise ValueError(f"Geçersiz GitHub URL formatı: {url}")


def canonical_repo_key(url_or_owner: str, repo_name: Optional[str] = None) -> str:
    """Reponun tekil ve büyük/küçük harf duyarsız ayrıştırıcı anahtarını döndürür (ör: 'shadcn-ui/ui')."""
    if repo_name is not None:
        return f"{url_or_owner.strip().lower()}/{repo_name.strip().lower()}"
    owner, name = parse_repo_info(url_or_owner)
    return f"{owner.strip().lower()}/{name.strip().lower()}"


def normalize_repo_url(url: str) -> str:
    """Herhangi bir geçerli repo linkini veya kısa adını standart HTTPS GitHub URL'sine dönüştürür."""
    owner, name = parse_repo_info(url)
    return f"https://github.com/{owner}/{name}"


def clone_shallow(url: str, target_dir: Path, timeout_sec: int = 90) -> bool:
    """Belirtilen repoyu shallow clone (--depth 1) ile hedef dizine çeker."""
    if target_dir.exists():
        safe_rmtree(target_dir)
    target_dir.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        "git", "clone",
        "--depth", "1",
        "--single-branch",
        url,
        str(target_dir)
    ]
    try:
        res = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout_sec,
            check=False
        )
        if res.returncode != 0:
            print(f"[HATA] Git clone başarısız oldu:\n{res.stderr}", file=sys.stderr)
            return False
        return True
    except subprocess.TimeoutExpired:
        print(f"[HATA] Git clone zaman aşımına uğradı ({timeout_sec}s).", file=sys.stderr)
        return False
    except FileNotFoundError:
        print("[HATA] 'git' komutu bulunamadı. Lütfen Git'in kurulu olduğundan emin olun.", file=sys.stderr)
        return False


def build_directory_tree(root: Path, max_depth: int = 3, current_depth: int = 0) -> List[Dict[str, Any]]:
    """Dizin ağacını sınırlandırılmış derinlikle JSON formatında modeller."""
    if current_depth >= max_depth or not root.is_dir():
        return []

    items: List[Dict[str, Any]] = []
    try:
        entries = sorted(root.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower()))
    except (PermissionError, OSError):
        return items

    for entry in entries:
        if entry.name in IGNORED_DIRS or entry.name.startswith("."):
            continue

        if entry.is_dir():
            children = build_directory_tree(entry, max_depth, current_depth + 1)
            items.append({
                "type": "directory",
                "name": entry.name,
                "children": children
            })
        elif entry.is_file():
            items.append({
                "type": "file",
                "name": entry.name,
                "size_bytes": entry.stat().st_size
            })
    return items


def detect_tech_stack_and_layer(root: Path) -> Dict[str, Any]:
    """Repo kökünü tarayarak teknoloji yığınını ve katmanları belirler."""
    frontend_markers: List[str] = []
    backend_markers: List[str] = []
    tooling_markers: List[str] = []
    dependencies_summary: List[str] = []

    # Frontend Taraması
    pkg_json = root / "package.json"
    if pkg_json.is_file():
        try:
            data = json.loads(pkg_json.read_text(encoding="utf-8", errors="replace"))
            deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
            key_deps = [d for d in deps if any(k in d for k in ("react", "vue", "tailwind", "next", "vite", "shadcn", "radix", "lucide", "redux", "zustand"))]
            if key_deps:
                frontend_markers.append(f"npm deps: {', '.join(key_deps[:8])}")
                dependencies_summary.extend(key_deps)
        except Exception:
            pass

    for ext in ("*.tsx", "*.jsx", "*.vue", "*.svelte"):
        if any(root.glob(f"**/{ext}")):
            frontend_markers.append(f"UI components ({ext})")
            break

    # Backend Taraması
    if (root / "pom.xml").is_file():
        backend_markers.append("Java/Maven (pom.xml)")
    if (root / "build.gradle").is_file() or (root / "build.gradle.kts").is_file():
        backend_markers.append("Java/Kotlin Gradle")
    if (root / "requirements.txt").is_file() or (root / "pyproject.toml").is_file():
        backend_markers.append("Python (requirements/pyproject)")
    if (root / "go.mod").is_file():
        backend_markers.append("Go (go.mod)")
    if (root / "Cargo.toml").is_file():
        backend_markers.append("Rust (Cargo.toml)")
    if (root / "Dockerfile").is_file() or (root / "docker-compose.yml").is_file():
        backend_markers.append("Containerization (Docker)")

    # Tooling / Agentic Taraması
    if (root / ".agent").is_dir() or (root / ".cursor").is_dir() or (root / ".claude").is_dir():
        tooling_markers.append("Agent/IDE Config (.agent / .cursor / .claude)")
    if (root / "AGENTS.md").is_file() or (root / "CLAUDE.md").is_file():
        tooling_markers.append("Agent Rules (AGENTS.md / CLAUDE.md)")
    if any(root.glob("**/SKILL.md")) or any(root.glob("**/skills/**")):
        tooling_markers.append("Agent Skills (SKILL.md / skills/)")
    if any(root.glob("**/rules/**/*.md")):
        tooling_markers.append("Rules System (rules/*.md)")

    # Katman Belirleme
    layers: List[str] = []
    if frontend_markers:
        layers.append("Frontend")
    if backend_markers:
        layers.append("Backend")
    if tooling_markers:
        layers.append("Tooling / Agentic")

    primary_layer = " + ".join(layers) if layers else "Genel / Belirsiz"

    return {
        "primary_layer": primary_layer,
        "frontend_signals": frontend_markers,
        "backend_signals": backend_markers,
        "tooling_signals": tooling_markers,
        "dependencies": sorted(list(set(dependencies_summary)))
    }


def extract_readme_summary(root: Path, max_lines: int = 120) -> str:
    """README dosyasının ilk kısımlarını özet bağlam için okur."""
    for name in ("README.md", "README.MD", "readme.md", "README"):
        candidate = root / name
        if candidate.is_file():
            try:
                lines = candidate.read_text(encoding="utf-8", errors="replace").splitlines()
                return "\n".join(lines[:max_lines])
            except Exception:
                pass
    return "README dosyası bulunamadı."


def generate_fingerprint(target_dir: Path, repo_url: str) -> Dict[str, Any]:
    """Hedef deponun token-dostu hafif parmak izini üretir."""
    owner, repo_name = parse_repo_info(repo_url)
    tech = detect_tech_stack_and_layer(target_dir)
    tree = build_directory_tree(target_dir, max_depth=3)
    readme = extract_readme_summary(target_dir, max_lines=120)

    # İstatistikler
    all_files = [f for f in target_dir.rglob("*") if f.is_file() and not any(p in f.parts for p in IGNORED_DIRS)]
    total_files = len(all_files)
    total_size_kb = sum(f.stat().st_size for f in all_files) // 1024

    return {
        "repo_url": repo_url,
        "owner": owner,
        "name": repo_name,
        "analyzed_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_files": total_files,
        "total_size_kb": total_size_kb,
        "tech_stack": tech,
        "tree_structure": tree,
        "readme_head": readme
    }


def load_repos() -> List[Dict[str, Any]]:
    """repos.json dosyasını okuyarak liste döndürür ve statüleri zenginleştirir."""
    if not REPOS_JSON.is_file():
        return []
    try:
        data = json.loads(REPOS_JSON.read_text(encoding="utf-8", errors="replace"))
        if isinstance(data, list):
            return migrate_legacy_statuses(data)
        return []
    except Exception as e:
        print(f"[UYARI] repos.json okunamadı: {e}", file=sys.stderr)
        return []


def save_repos(repos: List[Dict[str, Any]]) -> bool:
    """Repo listesini repos.json dosyasına atomik/düzenli kaydeder."""
    try:
        REPOS_JSON.write_text(json.dumps(repos, ensure_ascii=False, indent=2), encoding="utf-8")
        return True
    except Exception as e:
        print(f"[HATA] repos.json kaydedilemedi: {e}", file=sys.stderr)
        return False


def get_pending_repos() -> List[Dict[str, Any]]:
    """repos.json içindeki PENDING durumundaki repoları döndürür."""
    repos = load_repos()
    return [r for r in repos if r.get("status", "").upper() == "PENDING"]


def find_existing_repo(repo_url_or_key: str, repos: Optional[List[Dict[str, Any]]] = None) -> Optional[Dict[str, Any]]:
    """Belirtilen repo URL'sinin veya 'owner/repo' anahtarının repos.json içindeki kaydını bulur."""
    try:
        target_key = canonical_repo_key(repo_url_or_key)
    except Exception:
        target_key = repo_url_or_key.strip().lower().rstrip("/")

    if repos is None:
        repos = load_repos()

    for r in repos:
        try:
            r_key = canonical_repo_key(r.get("url", ""))
        except Exception:
            o = r.get("owner", "").strip().lower()
            n = r.get("name", "").strip().lower()
            r_key = f"{o}/{n}" if o and n else r.get("url", "").strip().lower().rstrip("/")
        if r_key == target_key:
            return r
    return None


def is_existing_repo(repo_url: str, repos: Optional[List[Dict[str, Any]]] = None) -> bool:
    """Belirtilen repo URL'sinin repos.json içinde zaten kayıtlı olup olmadığını denetler (canonical matching)."""
    return find_existing_repo(repo_url, repos=repos) is not None


def update_repos_table(
    repo_url: str,
    layer: str,
    status: str,
    verdict: str,
    plan_file: str,
    rebuild: bool = True
) -> bool:
    """repos.json dosyasındaki ilgili repoyu canonical key ile günceller veya yoksa yeni ekler."""
    repos = load_repos()
    owner, name = parse_repo_info(repo_url)
    target_key = canonical_repo_key(owner, name)
    norm_url = normalize_repo_url(repo_url)
    today = datetime.now().strftime("%Y-%m-%d")
    updated = False

    for r in repos:
        r_owner = r.get("owner", "")
        r_name = r.get("name", "")
        if r_owner and r_name:
            r_key = canonical_repo_key(r_owner, r_name)
        else:
            try:
                r_key = canonical_repo_key(r.get("url", ""))
            except Exception:
                r_key = r.get("url", "").strip().lower().rstrip("/")

        if r_key == target_key:
            # Mükerrer kayıt bulundu - ezmeden güncelle:
            # Eğer yeni durum PENDING ise ve var olan kayıt zaten DONE/AKTARILDI/SUSPENDED/CANCEL ise var olan durumu koru!
            if status == "PENDING" and r.get("status") in ("DONE", "AKTARILDI", "SUSPENDED", "CANCEL", "CANCELED", "CANCELLED"):
                if layer and layer != "-":
                    r["layer"] = layer
            else:
                r["layer"] = layer if layer and layer != "-" else r.get("layer", "Belirsiz")
                r["status"] = status
                r["verdict"] = verdict
                r["plan_file"] = plan_file if plan_file and plan_file != "-" else r.get("plan_file", "")
            r["date"] = today
            r["url"] = norm_url
            r["owner"] = owner
            r["name"] = name
            updated = True
            break

    if not updated:
        next_id = max([r.get("id", 0) for r in repos], default=0) + 1
        new_entry = {
            "id": next_id,
            "url": norm_url,
            "name": name,
            "owner": owner,
            "layer": layer if layer and layer != "-" else "Belirsiz",
            "status": status,
            "verdict": verdict,
            "plan_file": plan_file if plan_file and plan_file != "-" else "",
            "date": today
        }
        repos.append(new_entry)

    ok = save_repos(repos)

    # Scout HTML kataloğunu otomatik güncelle
    if rebuild and build_scout_catalog:
        try:
            build_scout_catalog()
        except Exception as e:
            print(f"[UYARI] Katalog derlenemedi: {e}", file=sys.stderr)
    return ok


def set_repo_status(
    identifier: int | str,
    status: str,
    verdict: Optional[str] = None,
    notes: Optional[str] = None,
    rebuild: bool = True
) -> bool:
    """repos.json dosyasındaki ilgili reponun durumunu günceller ve history kaydeder."""
    repos = load_repos()
    norm_status = status.strip().upper()
    if norm_status in ("CANCELED", "CANCELLED"):
        norm_status = "CANCEL"

    if norm_status not in VALID_STATUSES:
        raise ValueError(f"Geçersiz durum '{norm_status}'. Geçerli durumlar: {', '.join(VALID_STATUSES)}")

    id_str = str(identifier).strip()
    target = None

    for r in repos:
        if str(r.get("id")) == id_str:
            target = r
            break
        if find_existing_repo(id_str, [r]) is not None:
            target = r
            break

    if not target:
        return False

    target["status"] = norm_status
    if verdict is not None:
        target["verdict"] = verdict
    target["date"] = datetime.now().strftime("%Y-%m-%d")

    # İlerleme (progress) normalizasyonu
    if norm_status == "TRANSFERRED":
        target["progress"] = 100
    elif norm_status == "REJECTED":
        target["progress"] = 100
    elif norm_status == "TRANSFERRING":
        target["progress"] = 50
    elif norm_status == "PLANNED":
        target["progress"] = 25
    elif norm_status == "PENDING":
        target["progress"] = 0

    record_repo_history(
        target,
        action="STATUS_CHANGED",
        status=norm_status,
        note=notes or verdict or f"Durum '{norm_status}' olarak güncellendi."
    )

    ok = save_repos(repos)
    if rebuild and build_scout_catalog:
        try:
            build_scout_catalog()
        except Exception as e:
            print(f"[UYARI] Katalog derlenemedi: {e}", file=sys.stderr)
    return ok


def start_repo_transfer(
    identifier: int | str,
    target_skill: str,
    notes: Optional[str] = None,
    rebuild: bool = True
) -> Dict[str, Any]:
    """Bir reponun aktarım sürecini başlatır (status -> TRANSFERRING, progress -> 50)."""
    repos = load_repos()
    id_str = str(identifier).strip()
    target = None

    for r in repos:
        if str(r.get("id")) == id_str:
            target = r
            break
        if find_existing_repo(id_str, [r]) is not None:
            target = r
            break

    if not target:
        return {"success": False, "error": f"Repo bulunamadı: {identifier}"}

    target["status"] = "TRANSFERRING"
    target["progress"] = 50
    target["target_skill"] = target_skill.strip()
    target["date"] = datetime.now().strftime("%Y-%m-%d")

    note_text = notes.strip() if notes else f"Aktarım süreci başlatıldı -> Hedef: {target_skill}"
    record_repo_history(
        target,
        action="TRANSFER_STARTED",
        status="TRANSFERRING",
        note=note_text,
        extra={"target_skill": target_skill.strip()}
    )

    ok = save_repos(repos)
    if rebuild and build_scout_catalog:
        try:
            build_scout_catalog()
        except Exception as e:
            print(f"[UYARI] Katalog derlenemedi: {e}", file=sys.stderr)

    return {
        "success": ok,
        "repo": target,
        "message": f"'{target.get('name')}' için aktarım süreci başlatıldı (Hedef: {target_skill})."
    }


def complete_repo_transfer(
    identifier: int | str,
    target_skill: str,
    transferred_to: str,
    notes: Optional[str] = None,
    rebuild: bool = True
) -> Dict[str, Any]:
    """Bir reponun aktarımını tamamlar (status -> TRANSFERRED, progress -> 100)."""
    repos = load_repos()
    id_str = str(identifier).strip()
    target = None

    for r in repos:
        if str(r.get("id")) == id_str:
            target = r
            break
        if find_existing_repo(id_str, [r]) is not None:
            target = r
            break

    if not target:
        return {"success": False, "error": f"Repo bulunamadı: {identifier}"}

    target["status"] = "TRANSFERRED"
    target["progress"] = 100
    target["target_skill"] = target_skill.strip()
    target["transferred_to"] = transferred_to.strip()
    target["date"] = datetime.now().strftime("%Y-%m-%d")

    note_text = notes.strip() if notes else f"Sisteme aktarıldı: {transferred_to}"
    target["verdict"] = f"AKTARILDI: {transferred_to} ({note_text})"

    record_repo_history(
        target,
        action="TRANSFERRED",
        status="TRANSFERRED",
        note=note_text,
        extra={
            "target_skill": target_skill.strip(),
            "transferred_to": transferred_to.strip()
        }
    )

    ok = save_repos(repos)
    if rebuild and build_scout_catalog:
        try:
            build_scout_catalog()
        except Exception as e:
            print(f"[UYARI] Katalog derlenemedi: {e}", file=sys.stderr)

    return {
        "success": ok,
        "repo": target,
        "message": f"'{target.get('name')}' başarıyla sisteme aktarıldı olarak kaydedildi."
    }


def deduplicate_repos(repos: Optional[List[Dict[str, Any]]] = None, auto_save: bool = True) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """
    repos.json içindeki mükerrer kayıtları tespit eder ve tekilleştirir.
    Statü önceliği: AKTARILDI > DONE (ZENGINLESTIR / KISMEN / BIZ_DAHA_IYIYIZ) > PENDING.
    ID'leri 1'den N'e yeniden indeksler.
    Döndürür: (temizlenmis_liste, ozet_rapor)
    """
    if repos is None:
        repos = load_repos()

    initial_count = len(repos)
    grouped: Dict[str, List[Dict[str, Any]]] = {}

    for r in repos:
        try:
            k = canonical_repo_key(r.get("url", ""))
        except Exception:
            o = r.get("owner", "").strip().lower()
            n = r.get("name", "").strip().lower()
            k = f"{o}/{n}" if o and n else r.get("url", "").strip().lower().rstrip("/")
        grouped.setdefault(k, []).append(r)

    def status_score(item: Dict[str, Any]) -> int:
        v = (item.get("verdict") or "").upper()
        s = (item.get("status") or "").upper()
        if "AKTARILDI" in v or s == "AKTARILDI":
            return 100
        if s == "DONE":
            return 50
        if s == "SUSPENDED":
            return 25
        if s in ("CANCEL", "CANCELED", "CANCELLED"):
            return 20
        return 10

    cleaned: List[Dict[str, Any]] = []
    duplicates_removed = 0
    duplicate_details = []

    for k, items in grouped.items():
        if len(items) == 1:
            cleaned.append(items[0])
        else:
            sorted_items = sorted(items, key=status_score, reverse=True)
            chosen = sorted_items[0]
            for other in sorted_items[1:]:
                if (not chosen.get("layer") or chosen.get("layer") == "Belirsiz") and other.get("layer") and other.get("layer") != "Belirsiz":
                    chosen["layer"] = other["layer"]
                if not chosen.get("plan_file") and other.get("plan_file"):
                    chosen["plan_file"] = other["plan_file"]
            cleaned.append(chosen)
            duplicates_removed += (len(items) - 1)
            duplicate_details.append({
                "repo_key": k,
                "count": len(items),
                "retained_id": chosen.get("id"),
                "retained_verdict": chosen.get("verdict"),
                "dropped_ids": [x.get("id") for x in sorted_items[1:]]
            })

    # ID'leri 1'den N'e yeniden numaralandır
    for idx, r in enumerate(cleaned, start=1):
        r["id"] = idx

    report = {
        "initial_count": initial_count,
        "final_count": len(cleaned),
        "duplicates_removed": duplicates_removed,
        "duplicate_details": duplicate_details
    }

    if auto_save and duplicates_removed > 0:
        save_repos(cleaned)
        if build_scout_catalog:
            try:
                build_scout_catalog()
            except Exception:
                pass

    return cleaned, report


def add_new_repo(repo_url: str, layer: str = "Belirsiz", rebuild: bool = True) -> bool:
    """repos.json içine yeni bir repoyu PENDING durumunda ekler ve kataloğu günceller."""
    clean_url = repo_url.strip()
    owner, name = parse_repo_info(clean_url)
    return update_repos_table(
        repo_url=clean_url,
        layer=layer if layer else "Belirsiz",
        status="PENDING",
        verdict="-",
        plan_file="-",
        rebuild=rebuild
    )


def delete_repo(identifier: str | int) -> bool:
    """repos.json dosyasından belirtilen repoyu (id veya url) siler."""
    repos = load_repos()
    initial_count = len(repos)
    target_plan = None

    filtered: List[Dict[str, Any]] = []
    for r in repos:
        match_id = str(r.get("id")) == str(identifier)
        match_url = r.get("url", "").strip().rstrip("/") == str(identifier).strip().rstrip("/")
        if match_id or match_url:
            target_plan = r.get("plan_file")
            continue
        filtered.append(r)

    if len(filtered) == initial_count:
        return False

    # ID'leri yeniden sırala
    for idx, r in enumerate(filtered, start=1):
        r["id"] = idx

    save_repos(filtered)

    # İlgili plan dosyası varsa temizle
    if target_plan:
        plan_path = SCOUT_DIR / target_plan
        if plan_path.is_file():
            try:
                plan_path.unlink()
            except Exception:
                pass

    if build_scout_catalog:
        try:
            build_scout_catalog()
        except Exception:
            pass

    return True


def _find_agy_executable() -> Optional[str]:
    """Sistemdeki Antigravity CLI (agy) çalıştırılabilir dosyasını bulur."""
    exe_env = os.environ.get("ANTIGRAVITY_AGENTAPI_EXE")
    if exe_env and Path(exe_env).is_file():
        return exe_env
    local_agy = Path(os.environ.get("LOCALAPPDATA", "")) / "agy" / "bin" / "agy.exe"
    if local_agy.is_file():
        return str(local_agy)
    found = shutil.which("agy")
    if found:
        return found
    return None


def _get_skills_summary() -> str:
    """Mevcut .agent/skills havuzumuzun ad ve açıklamalarını dinamik özetler."""
    skills_dir = SCOUT_DIR.parent / ".agent" / "skills"
    if not skills_dir.is_dir():
        return "- Genel: ui-styling, frontend-design, ui-ux-pro-max, brand, seo-growth, musgoku, karpathy-guidelines, tdd, code-review"
    items = []
    for sdir in sorted(skills_dir.iterdir()):
        skill_file = sdir / "SKILL.md"
        if sdir.is_dir() and skill_file.is_file():
            try:
                content = skill_file.read_text(encoding="utf-8", errors="replace")
                desc = ""
                for line in content.splitlines():
                    if line.strip().startswith("description:"):
                        desc = line.split(":", 1)[1].strip().strip('"\'')
                        break
                desc_short = (desc[:140] + "...") if len(desc) > 140 else desc
                items.append(f"- **{sdir.name}:** {desc_short}")
            except Exception:
                items.append(f"- **{sdir.name}**")
    return "\n".join(items)


def evaluate_fingerprint_with_agent(
    fp: Dict[str, Any],
    target_dir: Optional[Path] = None
) -> Optional[Tuple[str, str, str]]:
    """Antigravity AI Agent (agy CLI) kullanarak repoyu derinlemesine inceler ve profesyonel plan üretir."""
    agy_exe = _find_agy_executable()
    if not agy_exe:
        print("[!] Antigravity CLI (agy) bulunamadı; fallback kurallarına geçiliyor.")
        return None

    name = fp.get("name", "repo")
    owner = fp.get("owner", "")
    url = fp.get("repo_url", "")
    tech = fp.get("tech_stack", {})
    detected_layer = tech.get("primary_layer", "Genel / Belirsiz")
    readme = fp.get("readme_head", "")
    total_files = fp.get("total_files", 0)
    total_size_kb = fp.get("total_size_kb", 0)
    tree = fp.get("tree_structure", [])

    # Ekstra odak dosyalar (varsa package.json, pom.xml, prompt/agent dosyaları)
    extra_context = ""
    if target_dir and Path(target_dir).is_dir():
        td = Path(target_dir)
        key_files = ["package.json", "pom.xml", "requirements.txt", "pyproject.toml", "Cargo.toml", ".cursorrules", "CLAUDE.md"]
        for kf in key_files:
            fp_candidate = td / kf
            if fp_candidate.is_file():
                try:
                    c_text = fp_candidate.read_text(encoding="utf-8", errors="replace")[:1500]
                    extra_context += f"\n### Dosya İçeriği ({kf}):\n```\n{c_text}\n```\n"
                except Exception:
                    pass

    skills_summary = _get_skills_summary()

    prompt = f"""Sen Antigravity Scout Değerlendirme ve İstihbarat Ajanısın.
Görevimiz, harici bir GitHub reposunu yapısal parmak izi, kod mimarisi ve README içeriğine göre derinlemesine analiz etmek; mevcut skillSetWorks yetenek havuzumuzla kıyaslamak; net bir karara bağlamak ve profesyonel bir entegrasyon/değerlendirme raporu (Markdown) hazırlamaktır.

## 1. İncelenen Repo Bilgileri:
- **Repo URL:** {url}
- **Sahip/Repo:** {owner}/{name}
- **Dosya Sayısı & Boyut:** {total_files} dosya (~{total_size_kb} KB)
- **İlk Tespit Edilen Katman:** {detected_layer}
- **Teknoloji Sinyalleri:** {json.dumps(tech, ensure_ascii=False)}
- **Dizin Ağacı (Özet):**
{json.dumps(tree, ensure_ascii=False, indent=2)[:2000]}
- **README İçeriği:**
{readme[:4000]}
{extra_context}

## 2. Mevcut Sistemimiz ve Yetenek Havuzumuz (.agent/skills):
{skills_summary}

## 3. Karar Rubriği (Değerlendirme Kriterleri):
Aşağıdaki 3 karardan birini vermelisin:
1. `BIZ_DAHA_IYIYIZ: <Net gerekçe>`: Mevcut skill setimiz incelenen repodan daha derin, daha olgun veya daha kapsamlıysa; ya da dış repo generic bir şablon / düşük kaliteli bir çalışma / AI-slop ise.
2. `ZENGINLESTIR: <Net gerekçe>`: Repoda bizim yapımıza doğrudan değer katacak, eksik bir kural maddesi, yeni bir CLI scripti, özel bir tasarım deseni, backend mimari kalıbı veya agent kuralları varsa.
3. `KISMEN_ALINABILIR: <Net gerekçe>`: Reponun tamamı değil; yalnız belirli bir algoritma, regex, CSS utility'si, liste veya referans kataloğu faydalıysa.
(Eğer zaten sisteme tam aktarılmışsa: `AKTARILDI: <Açıklama>`)

## 4. Zorunlu Çıktı Formatı:
Yanıtında KESİNLİKLE şu etiketleri tam olarak kullan (etiketlerin arasına başka metin koyma):
<<<LAYER>>>
<Frontend | Backend | Tooling / Agentic | Fullstack | Referans & Veri>
<<<VERDICT>>>
<Karar: Gerekçe - tek satır, örn: BIZ_DAHA_IYIYIZ: ... veya ZENGINLESTIR: ... veya KISMEN_ALINABILIR: ...>
<<<PLAN>>>
# 🔭 Scout Değerlendirme Raporu: {owner}/{name}

## 1. Depo Özeti ve Künye
- **URL:** {url}
- **Sahibi:** {owner}
- **Analiz Tarihi:** {datetime.now().strftime("%Y-%m-%d %H:%M")}
- **Tespit Edilen Katman:** ...
- **Dosya Sayısı & Boyut:** {total_files} dosya (~{total_size_kb} KB)
- **Teknoloji Yığını:** ...

## 2. Çekirdek Felsefe ve Mimari (Repo İncelemesi)
(Deponun ne yaptığı, mimarisi, getirdiği çözümler, güçlü ve zayıf yönleri hakkında derinlikli inceleme)

## 3. Bizim Sistemle Kıyaslama (Delta Analizi)
- **Mevcut Durumumuz:** (İlgili .agent yeteneklerimizle açık kıyaslama)
- **Dış Repodaki Değer:** (Özgün katkı veya eksik yön)
- **Kesişim & Ayrışma:** (Duplicate mi, zanaat mı, token maliyeti ne olur?)

## 4. Karar ve Gerekçe
(Rubriğe göre net karar başlığı ve kapsamlı gerekçe)

## 5. Cerrahi Entegrasyon Planı / Eylem Maddeleri
(Eğer ZENGINLESTIR veya KISMEN_ALINABILIR ise: hangi skill'e ne eklenecek, kural sözleşmesi, test adımları. Eğer BIZ_DAHA_IYIYIZ ise: neden dahil edilmediği ve mevcut yapımızın nasıl üstün olduğu)
<<<END>>>
"""

    try:
        print(f"[*] AI Agent ({name}) için çalıştırılıyor...")
        cmd = [
            agy_exe,
            "--model", "gemini-3.8-flash-low",
            "--disable-slash-commands",
            "-p", prompt
        ]
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=120
        )
        output = proc.stdout.strip()
        if not output:
            print(f"[!] AI Agent boş yanıt döndü (stderr: {proc.stderr[:200]})")
            return None

        # Etiketleri ayrıştır
        if "<<<LAYER>>>" in output and "<<<VERDICT>>>" in output and "<<<PLAN>>>" in output:
            layer_chunk = output.split("<<<LAYER>>>")[1].split("<<<VERDICT>>>")[0].strip()
            verdict_chunk = output.split("<<<VERDICT>>>")[1].split("<<<PLAN>>>")[0].strip()
            rest = output.split("<<<PLAN>>>")[1]
            plan_chunk = rest.split("<<<END>>>")[0].strip() if "<<<END>>>" in rest else rest.strip()

            layer = layer_chunk.splitlines()[0].strip() if layer_chunk else detected_layer
            verdict = verdict_chunk.splitlines()[0].strip() if verdict_chunk else "BIZ_DAHA_IYIYIZ: İnceleme tamamlandı."
            plan_md = plan_chunk

            print(f"[+] AI Agent analizi tamamlandı: {verdict}")
            return layer, verdict, plan_md

        # Eğer etiketler eksikse ama içerik geldiyse
        print("[!] AI Agent etiketleri eksik döndü; çıktıdan plan oluşturuluyor.")
        verdict = "ZENGINLESTIR: AI Agent tarafından incelendi."
        for line in output.splitlines():
            if any(k in line for k in ("BIZ_DAHA_IYIYIZ", "ZENGINLESTIR", "KISMEN_ALINABILIR", "AKTARILDI")):
                verdict = line.strip().replace("#", "").strip()
                break
        return detected_layer, verdict, output

    except subprocess.TimeoutExpired:
        print(f"[!] AI Agent zaman aşımına uğradı (120s): {url}")
        return None
    except Exception as e:
        print(f"[!] AI Agent çalıştırma hatası: {e}")
        return None


def _evaluate_fingerprint_fallback(fp: Dict[str, Any]) -> Tuple[str, str, str]:
    """AI Agent devre dışı veya ulaşılamaz olduğunda kullanılan kural-tabanlı deterministik fallback."""
    name = fp.get("name", "repo")
    owner = fp.get("owner", "")
    url = fp.get("repo_url", "")
    tech = fp.get("tech_stack", {})
    layer = tech.get("primary_layer", "Genel / Belirsiz")
    readme = fp.get("readme_head", "")
    total_files = fp.get("total_files", 0)

    # SEO ve Marketing sinyalleri tespiti
    readme_lower = readme.lower()
    is_seo = any(w in readme_lower or w in name.lower() for w in ("seo", "search engine", "ranking", "serp", "keyword", "backlink", "meta tags"))
    is_marketing = any(w in readme_lower or w in name.lower() for w in ("marketing", "copywriting", "campaign", "growth", "funnel", "conversion"))
    is_ui_comp = any(w in readme_lower or w in name.lower() for w in ("components", "ui kit", "button", "tailwind component", "widgets"))

    if is_seo or is_marketing:
        verdict = f"ZENGINLESTIR: Mevcut brand ve doc-coauthoring skill setimize SEO & growth zekası kazandırılabilir."
        plan_md = f"""# 🔭 Scout Değerlendirme Raporu: {owner}/{name}

## 1. Depo Özeti ve Künye
- **URL:** {url}
- **Analiz Tarihi:** {datetime.now().strftime("%Y-%m-%d %H:%M")}
- **Tespit Edilen Katman:** {layer}
- **Dosya Sayısı:** {total_files}

## 2. Bizim Sistemle Kıyaslama (Delta Analizi)
- **Mevcut Durumumuz:** `.agent/skills/` altında `brand` (marka tonu, visual identity), `doc-coauthoring` (içerik ve spec yazımı), `ui-ux-pro-max` (UX kuralları) skill'lerimiz mevcut.
- **Dış Repodaki Değer:** Bu depo arama motoru optimizasyonu (SEO), anahtar kelime yerleşimi, meta veri hiyerarşisi ve teknik indekslenebilirlik konularında pratik kurallar içeriyor.
- **Kesişim:** Doğrudan çakışma yok; mevcut `brand` ve `doc-coauthoring` dokümantasyon kabiliyetlerimizi tamamlayıcı nitelikte.

## 3. Karar: 💎 ZENGİNLEŞTİR
Bu deponun sunduğu en iyi pratikler ayrıştırılarak sistemimize entegre edilmelidir.

## 4. Cerrahi Entegrasyon Planı
1. **Hedef Konum:** `.agent/skills/brand/` ve `rules/doc-coauthoring` yönergeleri içerisine "SEO & SERP Kuralları" alt başlığı eklenmeli veya bağımsız bir `seo-growth` alt yeteneği oluşturulmalı.
2. **Kural Sözleşmesi:** `rules/skill-trigger-routing.md` sözlüğüne SEO anahtar kelimeleri (`seo`, `meta tag`, `ranking`, `arama motoru`) eklenmeli.
3. **Token Koruma:** Dış repodaki gereksiz scaffolding dosyaları atılmalı; yalnız öz kılavuz ve kontrol listesi `.agent` standartlarımıza uygun şekilde dahil edilmeli.

## 5. Doğrulama & Kullanıcı Testi
- `python -m unittest discover -p "test_*.py"` ile skill sözleşme testleri koşturulacak.
- Kullanıcıya test adımları `KULLANICI_TEST_REHBERI.md` üzerinden sunulacak.
"""
    elif is_ui_comp:
        verdict = "BIZ_DAHA_IYIYIZ: Bizim ui-styling + ui-ux-pro-max 79 stil ve hazır token mimarisiyle daha kapsamlı."
        plan_md = f"""# 🔭 Scout Değerlendirme Raporu: {owner}/{name}

## 1. Depo Özeti
- **URL:** {url}
- **Analiz Tarihi:** {datetime.now().strftime("%Y-%m-%d %H:%M")}
- **Katman:** {layer}

## 2. Bizim Sistemle Kıyaslama
Mevcut `.agent` tasarım havuzumuzda `ui-styling` (Tailwind + accessible shadcn desenleri), `ui-ux-pro-max` (79 stil, 192 palet, 119 UX kuralı) ve `design-system` (token mimarisi) yer almaktadır. Dış repodaki yapılar mevcut standartlarımızın gerisinde kalmaktadır.

## 3. Karar: 🛡️ BİZ DAHA İYİYİZ
Sisteme dahil edilmesine gerek görülmemiştir; token ve dosya kalabalığı yapmaması için elenmiştir.
"""
    else:
        verdict = f"ZENGINLESTIR: {layer} katmanında faydalı desenler barındırıyor; cerrahi olarak incelenebilir."
        plan_md = f"""# 🔭 Scout Değerlendirme Raporu: {owner}/{name}

## 1. Depo Özeti
- **URL:** {url}
- **Analiz Tarihi:** {datetime.now().strftime("%Y-%m-%d %H:%M")}
- **Katman:** {layer}

## 2. Ön İnceleme
Depo {layer} katmanına yönelik bileşen ve yapılandırmalar içermektedir.

## 3. Karar: 💎 ZENGİNLEŞTİR (Ön Değerlendirme)
Cerrahi parçalar incelenip ilgili skill'lere aktarılabilir.
"""

    return layer, verdict, plan_md


def evaluate_fingerprint(
    fp: Dict[str, Any],
    target_dir: Optional[Path] = None,
    use_agent: bool = True
) -> Tuple[str, str, str]:
    """Parmak izini inceleyerek katman, karar ve detaylı plan Markdown içeriği üretir."""
    if use_agent:
        agent_res = evaluate_fingerprint_with_agent(fp, target_dir)
        if agent_res:
            return agent_res

    return _evaluate_fingerprint_fallback(fp)


def scout_and_evaluate_repo(
    repo_url: str,
    keep_temp: bool = False,
    use_agent: bool = True
) -> Dict[str, Any]:
    """Bir repoyu klonlar, parmak izini çıkarır, kararı üretir, plan dosyasını yazar ve repos.json'ı günceller."""
    owner, name = parse_repo_info(repo_url)
    target = TEMP_DIR / name

    # Klonlama ve parmak izi
    scout_res = scout_repo(repo_url, keep_temp=True)
    if "error" in scout_res:
        return scout_res

    fp = scout_res.get("fingerprint", {})
    layer, verdict, plan_md = evaluate_fingerprint(fp, target_dir=target, use_agent=use_agent)

    # Temp temizliği
    if not keep_temp:
        safe_rmtree(target)
        fp_path = TEMP_DIR / f"{name}_fingerprint.json"
        if fp_path.is_file():
            try:
                fp_path.unlink()
            except Exception:
                pass

    # Plan dosyasını kaydet
    PLANS_DIR.mkdir(parents=True, exist_ok=True)
    plan_filename = f"{name}.md"
    plan_rel_path = f"plans/{plan_filename}"
    plan_full_path = PLANS_DIR / plan_filename
    plan_full_path.write_text(plan_md, encoding="utf-8")

    # repos.json dosyasını karara göre doğru durumla güncelle
    v_upper = (verdict or "").upper()
    if "BIZ_DAHA_IYIYIZ" in v_upper or "DAHA IYIYIZ" in v_upper:
        determined_status = "REJECTED"
    elif "AKTARILDI" in v_upper:
        determined_status = "TRANSFERRED"
    else:
        determined_status = "PLANNED"

    update_repos_table(
        repo_url=repo_url,
        layer=layer,
        status=determined_status,
        verdict=verdict,
        plan_file=plan_rel_path
    )

    return {
        "success": True,
        "repo_url": repo_url,
        "name": name,
        "layer": layer,
        "verdict": verdict,
        "plan_file": plan_rel_path
    }


def scout_repo(repo_url: str, keep_temp: bool = False) -> Dict[str, Any]:
    """Bir repoyu uçtan uca çeker, parmak izini üretir ve JSON olarak kaydeder."""
    owner, name = parse_repo_info(repo_url)
    target = TEMP_DIR / name

    print(f"[*] Repoyu shallow clone ile çekiyor: {repo_url} -> {target}")
    ok = clone_shallow(repo_url, target)
    if not ok:
        return {"error": f"Git clone hatası: {repo_url}"}

    print("[*] Yapısal parmak izi çıkarılıyor...")
    fp = generate_fingerprint(target, repo_url)

    # Parmak izini geçici JSON dosyası olarak kaydet
    fp_path = TEMP_DIR / f"{name}_fingerprint.json"
    fp_path.write_text(json.dumps(fp, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[+] Parmak izi hazırlandı: {fp_path}")

    if not keep_temp:
        # Repo kodunu sil ama parmak izi JSON'unu bırak
        print(f"[*] Disk temizliği: {target} siliniyor...")
        safe_rmtree(target)

    return {
        "success": True,
        "fingerprint_file": str(fp_path),
        "fingerprint": fp
    }


def main():
    parser = argparse.ArgumentParser(description="Private Repo Scout Engine")
    parser.add_argument("--repo", help="İncelenecek GitHub repo URL'si")
    parser.add_argument("--add", help="repos.md tablosuna yeni repo ekler (PENDING)")
    parser.add_argument("--layer", default="Belirsiz", help="--add ile eklenirken katman (Frontend/Backend/Tooling)")
    parser.add_argument("--next-pending", action="store_true", help="repos.md'deki sıradaki PENDING repoyu inceler")
    parser.add_argument("--keep-temp", action="store_true", help="İnceleme sonrası klonlanan repoyu silmez")
    parser.add_argument("--cleanup", help="Belirtilen reponun temp klasörünü temizler")
    parser.add_argument("--html", action="store_true", help="scout-catalog.html dosyasını yeniden derler")
    parser.add_argument("--dedup", action="store_true", help="repos.json içindeki mükerrer kayıtları ayıklar ve tekilleştirir")
    args = parser.parse_args()

    TEMP_DIR.mkdir(parents=True, exist_ok=True)
    PLANS_DIR.mkdir(parents=True, exist_ok=True)

    if args.dedup:
        cleaned, report = deduplicate_repos(auto_save=True)
        if report["duplicates_removed"] > 0:
            print(f"[OK] {report['duplicates_removed']} adet mükerrer repo temizlendi. Kalan tekil repo: {report['final_count']}")
            for d in report["duplicate_details"]:
                print(f"  - {d['repo_key']}: {d['count']} kayıt birleştirildi (Kalan ID: #{d['retained_id']}, Silinen ID'ler: {d['dropped_ids']})")
        else:
            print(f"[OK] Mükerrer repo bulunamadı. Toplam {report['final_count']} kayıt tekil.")
        sys.exit(0)

    if args.add:
        try:
            ok = add_new_repo(args.add, layer=args.layer)
            if ok:
                print(f"[OK] Repo eklendi: {args.add} (Katman: {args.layer}, Durum: PENDING)")
                sys.exit(0)
            else:
                print("[HATA] Repo eklenemedi.", file=sys.stderr)
                sys.exit(1)
        except ValueError as e:
            print(f"[HATA] {e}", file=sys.stderr)
            sys.exit(1)

    if args.html:
        if build_scout_catalog:
            build_scout_catalog()
        else:
            print("[HATA] generate_scout_catalog modülü bulunamadı.", file=sys.stderr)
        sys.exit(0)

    if args.cleanup:
        target = TEMP_DIR / args.cleanup
        safe_rmtree(target)
        fp_file = TEMP_DIR / f"{args.cleanup}_fingerprint.json"
        if fp_file.exists():
            fp_file.unlink()
        print(f"[OK] {args.cleanup} temizlendi.")
        sys.exit(0)

    target_url = args.repo
    if args.next_pending:
        pending = get_pending_repos()
        if not pending:
            print("[INFO] Bekleyen (PENDING) repo bulunamadı.")
            sys.exit(0)
        target_url = pending[0]["url"]
        print(f"[INFO] Sıradaki bekleyen repo seçildi: {target_url}")

    if not target_url:
        parser.print_help()
        sys.exit(1)

    result = scout_repo(target_url, keep_temp=args.keep_temp)
    if "error" in result:
        print(result["error"], file=sys.stderr)
        sys.exit(1)

    print(json.dumps({
        "status": "READY_FOR_AGENT_REVIEW",
        "fingerprint_file": result["fingerprint_file"],
        "repo_url": target_url,
        "primary_layer": result["fingerprint"]["tech_stack"]["primary_layer"]
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
