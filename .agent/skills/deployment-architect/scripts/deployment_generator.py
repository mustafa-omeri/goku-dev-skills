#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Deployment Architect & Infrastructure Generator (deployment_generator.py).

Proje kod tabanını analiz ederek:
1. Yığını (Frontend, Backend, DB, Hibrit/Çok Katmanlı) otomatik tespit eder,
2. Hedef ortama (VPS, PaaS, Cloud Container, Hibrit) uygun 5 katmanlı DEPLOYMENT_PLAN.md üretir,
3. Üretim konfigürasyonlarını (.env.production.template, Nginx, Docker Compose) ve
4. Geri alma (Rollback) & Acil durum kurtarma protokollerini oluşturur.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="latin-1", errors="replace")


def parse_target_yaml(content: str) -> Dict[str, Any]:
    """Lightweight zero-dependency YAML parser for nested deployment targets."""
    lines = content.splitlines()
    root: Dict[str, Any] = {}
    stack: List[Tuple[int, Dict[str, Any]]] = [(-1, root)]

    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        indent = len(line) - len(line.lstrip(" "))
        while len(stack) > 1 and stack[-1][0] >= indent:
            stack.pop()

        parent = stack[-1][1]

        if ":" in stripped:
            key, val = stripped.split(":", 1)
            key = key.strip()
            val = val.strip()

            if not val:
                new_dict: Dict[str, Any] = {}
                parent[key] = new_dict
                stack.append((indent, new_dict))
            else:
                # Type inference
                if val.lower() in ("true", "yes"):
                    parsed_val = True
                elif val.lower() in ("false", "no"):
                    parsed_val = False
                elif val.isdigit():
                    parsed_val = int(val)
                else:
                    parsed_val = val.strip("'\"")
                parent[key] = parsed_val

    return root


def inspect_project(root: Path) -> Dict[str, Any]:
    """Inspects project files to detect frontend, backend, database and hybrid architecture."""
    root = root.resolve()
    has_frontend = False
    frontend_type = "none"
    has_backend = False
    backend_type = "none"
    has_db = False
    db_type = "none"

    # Check package.json
    pkg_path = root / "package.json"
    if pkg_path.is_file():
        try:
            pkg = json.loads(_read_text(pkg_path))
            deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
            if any(k in deps for k in ("react", "react-dom", "vue", "svelte", "@angular/core", "vite")):
                has_frontend = True
                frontend_type = "react" if "react" in deps else ("vue" if "vue" in deps else "frontend")
            if any(k in deps for k in ("next", "nuxt")):
                has_frontend = True
                frontend_type = "nextjs"
            if any(k in deps for k in ("express", "fastify", "koa", "@nestjs/core", "hono")):
                has_backend = True
                backend_type = "node"
            if any(k in deps for k in ("pg", "mysql2", "prisma", "typeorm", "@supabase/supabase-js", "drizzle-orm")):
                has_db = True
                db_type = "postgres" if ("pg" in deps or "@supabase/supabase-js" in deps) else "relational"
        except Exception:
            pass

    # Check Java / Spring Boot
    if (root / "pom.xml").is_file() or (root / "build.gradle").is_file() or (root / "build.gradle.kts").is_file():
        has_backend = True
        backend_type = "spring-boot"
        pom_text = _read_text(root / "pom.xml") if (root / "pom.xml").is_file() else ""
        if "postgresql" in pom_text or "mysql" in pom_text or "spring-boot-starter-data-jpa" in pom_text:
            has_db = True
            db_type = "postgres" if "postgresql" in pom_text else "relational"

    # Check Python
    if (root / "requirements.txt").is_file() or (root / "pyproject.toml").is_file():
        has_backend = True
        backend_type = "python"
        req_text = _read_text(root / "requirements.txt") if (root / "requirements.txt").is_file() else ""
        if any(db in req_text for db in ("psycopg2", "asyncpg", "sqlalchemy", "pymongo")):
            has_db = True
            db_type = "postgres" if "pg" in req_text else "db"

    is_hybrid = has_frontend and has_backend and (frontend_type != backend_type)

    return {
        "has_frontend": has_frontend,
        "frontend_type": frontend_type,
        "has_backend": has_backend,
        "backend_type": backend_type,
        "has_db": has_db,
        "db_type": db_type,
        "is_hybrid": is_hybrid,
    }


def generate_deployment_plan(root: Path, target_config: Dict[str, Any]) -> Dict[str, Any]:
    """Generates the standardized 5-layer deployment plan and configuration artifacts."""
    stack = inspect_project(root)
    target_type = target_config.get("target_type", "vps")
    env = target_config.get("environment", "production")

    is_hybrid = target_type == "hybrid" or target_config.get("is_hybrid", stack["is_hybrid"])

    plan_lines: List[str] = [
        f"# DEPLOYMENT_PLAN.md — Üretim Dağıtım ve Altyapı Planı",
        f"",
        f"> **Ortam:** {env.upper()} · **Dağıtım Tipi:** {'Hibrit Dağıtım Mimarisi' if is_hybrid else target_type.upper()}",
        f"> **Tarih:** 2026-11-06 · **Sorumlu Ajan:** `deployment-architect`",
        f"",
        f"---",
        f"",
    ]

    artifacts: Dict[str, str] = {}

    # Section 1: Infrastructure
    plan_lines.extend([
        f"## 🏗️ Bölüm 1: Altyapı ve Çalışma Zamanı Mimarisi (Infrastructure & Runtime)",
        f"",
    ])

    if is_hybrid:
        fe_cfg = target_config.get("frontend", {})
        be_cfg = target_config.get("backend", {})
        db_cfg = target_config.get("database", {})

        fe_provider = str(fe_cfg.get('provider', fe_cfg.get('target', 'PaaS'))).title()
        be_runtime = str(be_cfg.get('runtime', be_cfg.get('target', 'VPS'))).title()
        db_provider = str(db_cfg.get('provider', db_cfg.get('target', 'Managed'))).title()

        plan_lines.extend([
            f"Bu proje **Hibrit / Çok Katmanlı (Polyglot)** bir mimariye sahiptir:",
            f"- **Arayüz (Frontend):** `{stack.get('frontend_type', 'client')}` katmanı -> **{fe_provider}** üzerinde (`{fe_cfg.get('domain', 'app.domain.com')}`).",
            f"- **Sunucu (Backend):** `{stack.get('backend_type', 'api')}` katmanı -> **{be_runtime}** üzerinde (`{be_cfg.get('host', 'api.domain.com')}:{be_cfg.get('port', 8080)}`).",
            f"- **Veritabanı (Database):** `{stack.get('db_type', 'postgres')}` katmanı -> **{db_provider}**.",
            f"",
            f"### Ağ, Ters Proxy ve CORS Yönlendirmesi",
            f"- Arayüz ile Backend arasındaki isteklerde `{fe_cfg.get('domain', 'app.domain.com')}` domaini Backend CORS izinli origin listesine (`ALLOWED_ORIGINS`) eklenmelidir.",
            f"- Backend önünde Nginx/Caddy ters proxy konumlandırılmalı, `/api/*` istekleri `{be_cfg.get('port', 8080)}` portuna taşınmalıdır.",
            f"",
        ])
    elif target_type == "vps":
        domain = target_config.get("domain", "app.example.com")
        port = target_config.get("app_port", 3000)
        os_name = target_config.get("os", "ubuntu-22.04")

        plan_lines.extend([
            f"- **Sunucu İşletim Sistemi:** `{os_name}`",
            f"- **Alan Adı (Domain):** `https://{domain}`",
            f"- **Uygulama Dinleme Portu:** `{port}` (iç ağ / localhost)",
            f"- **Ters Proxy:** Nginx Reverse Proxy + Let's Encrypt Certbot SSL",
            f"- **Güvenlik Duvarı (UFW):** Yalnızca `22 (SSH)`, `80 (HTTP)`, `443 (HTTPS)` dış dünyaya açıktır.",
            f"",
            f"```nginx",
            f"# /etc/nginx/sites-available/{domain}",
            f"server {{",
            f"    listen 80;",
            f"    server_name {domain};",
            f"    return 301 https://$host$request_uri;",
            f"}}",
            f"server {{",
            f"    listen 443 ssl http2;",
            f"    server_name {domain};",
            f"    ssl_certificate /etc/letsencrypt/live/{domain}/fullchain.pem;",
            f"    ssl_certificate_key /etc/letsencrypt/live/{domain}/privkey.pem;",
            f"    add_header X-Frame-Options DENY;",
            f"    add_header X-Content-Type-Options nosniff;",
            f"    location / {{",
            f"        proxy_pass http://127.0.0.1:{port};",
            f"        proxy_set_header Host $host;",
            f"        proxy_set_header X-Real-IP $remote_addr;",
            f"        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;",
            f"        proxy_set_header X-Forwarded-Proto $scheme;",
            f"    }}",
            f"}}",
            f"```",
            f"",
        ])
    else:
        plan_lines.extend([
            f"- **Platform / Container Cloud:** `{target_type.upper()}`",
            f"- **Yönetilen Ortam:** Build & Run spesifikasyonu platform manifesti ile sağlanır.",
            f"",
        ])

    # Section 2: Config Matrix
    env_template_content = (
        f"# .env.production.template — Üretim Ortam Değişkenleri\n"
        f"NODE_ENV=production\n"
        f"PORT={target_config.get('app_port', target_config.get('backend', {}).get('port', 3000))}\n"
        f"APP_URL=https://{target_config.get('domain', target_config.get('frontend', {}).get('domain', 'app.example.com'))}\n"
        f"# DATABASE_URL=postgresql://[USER]:[PASSWORD]@[HOST]:5432/[DB_NAME]?sslmode=require\n"
        f"# JWT_SECRET=[64-karakterlik-rastgele-hex-anahtar]\n"
        f"# CORS_ORIGINS=https://{target_config.get('domain', target_config.get('frontend', {}).get('domain', 'app.example.com'))}\n"
    )
    artifacts[".env.production.template"] = env_template_content

    plan_lines.extend([
        f"---",
        f"",
        f"## 🔐 Bölüm 2: Üretim Konfigürasyon ve Secret Matrisi (Production Config & Secrets)",
        f"",
        f"- `.env.production` dosyası asla versiyon kontrolüne (Git) eklenmez (`.gitignore` korumalı).",
        f"- Üretim ortamında gereken tüm değişkenler `.env.production.template` üzerinden hazırlanmalı ve güvenli secret deposuna (Vault / GitHub Secrets / Server env) girilmelidir.",
        f"",
        f"```bash",
        f"# Örnek Değişken Şablonu",
        f"NODE_ENV=production",
        f"DATABASE_URL=postgresql://user:password@host:5432/dbname",
        f"CORS_ORIGINS=https://{target_config.get('domain', target_config.get('frontend', {}).get('domain', 'app.example.com'))}",
        f"```",
        f"",
    ])

    # Section 3: Database Migration
    plan_lines.extend([
        f"---",
        f"",
        f"## 🗄️ Bölüm 3: Veritabanı Migration ve Sıfır Kesinti Stratejisi (Database Migration & Zero-Downtime)",
        f"",
        f"1. **Pre-Deploy Hook (Önce Şema, Sonra Kod):**",
        f"   - Yeni uygulama versiyonu trafiğe açılmadan önce migration scriptleri çalıştırılır.",
        f"   - Komut: `npm run db:migrate` veya `prisma migrate deploy` veya `liquibase update`.",
        f"2. **Geriye Dönük Uyumluluk Kuralı (Expand-Contract):**",
        f"   - Yeni eklenen kolonlar `NULLABLE` veya `DEFAULT` değerli olmalıdır.",
        f"   - Eski kod çalışırken yeni şemayı bozmamalı; eski kolonlar bir sonraki sürümde kaldırılmalıdır.",
        f"3. **Otomatik Yedekleme:** Dağıtım başlamadan önce anlık snapshot veya `pg_dump` yedeği alınır.",
        f"",
    ])

    # Section 4: Rollback Playbook
    plan_lines.extend([
        f"---",
        f"",
        f"## 🔄 Bölüm 4: Geri Alma ve Acil Durum Protokolü (Rollback Playbook)",
        f"",
        f"Canlıya geçiş sırasında veya hemen sonrasında kritik bir hata (500 patlaması, DB bağlantı kopması, bellek sızıntısı) oluşursa aşağıdaki sıra tavizsiz işletilir:",
        f"",
        f"### 1. Trafiği Kesme / Bakım Modu (Gerektiğinde)",
        f"- Nginx üzerinde bakım modu anahtarı aktif edilir: `touch /var/www/maintenance.flag` (503 Service Unavailable döner).",
        f"",
        f"### 2. Uygulama Kodu Rollback",
        f"- **Docker Kullanılıyorsa:** Önceki stabil imaj etiketine dönülür:",
        f"  ```bash",
        f"  docker compose -f docker-compose.prod.yml down",
        f"  docker compose -f docker-compose.prod.yml up -d --build app:v<onceki-stabil-surum>",
        f"  ```",
        f"- **Git / PM2 / Systemd Kullanılıyorsa:**",
        f"  ```bash",
        f"  git checkout tags/v<onceki-stabil-surum>",
        f"  systemctl restart app.service",
        f"  ```",
        f"",
        f"### 3. Veritabanı Rollback Stratejisi",
        f"- **Expand-Contract İlkesi:** Şema geriye uyumlu tasarlandığı için kod geri alındığında veritabanı genellikle çalışmaya devam eder.",
        f"- **Geri Alma (Down-Migration):** Eğer migration geri alınmak zorundaysa ilgili down migration işletilir veya dağıtım öncesi alınan anlık snapshot'tan geri yüklenir.",
        f"",
    ])

    # Section 5: Smoke Test & Health Check
    domain_to_check = target_config.get("domain", target_config.get("frontend", {}).get("domain", "app.example.com"))
    plan_lines.extend([
        f"---",
        f"",
        f"## 🧪 Bölüm 5: Dağıtım Sonrası Doğrulama & Smoke Test (Post-Deploy Health Check)",
        f"",
        f"1. **HTTP 200 Canlılık Testi:**",
        f"   ```bash",
        f"   curl -Iv https://{domain_to_check}/health",
        f"   ```",
        f"2. **SSL ve Güvenlik Başlıkları:**",
        f"   ```bash",
        f"   curl -s -D - https://{domain_to_check} | grep -E 'X-Frame-Options|Strict-Transport-Security'",
        f"   ```",
        f"3. **Log İzleme:** Dağıtım sonrası ilk 5 dakika boyunca hata logları taranır:",
        f"   ```bash",
        f"   docker compose logs -f --tail=100 | grep -i error",
        f"   # veya systemd: journalctl -u app.service -f -n 100",
        f"   ```",
        f"",
    ])

    return {
        "plan_markdown": "\n".join(plan_lines),
        "artifacts": artifacts,
        "is_hybrid": is_hybrid,
        "stack": stack,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Deployment Architect & Plan Generator")
    parser.add_argument("--root", default=".", help="Proje kök dizini")
    parser.add_argument("--target-file", help="DEPLOYMENT_TARGET.yaml dosya yolu")
    parser.add_argument("--json", action="store_true", help="JSON çıktı formatı")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    target_config: Dict[str, Any] = {"target_type": "vps", "environment": "production"}

    if args.target_file and Path(args.target_file).is_file():
        content = _read_text(Path(args.target_file))
        target_config = parse_target_yaml(content)

    res = generate_deployment_plan(root, target_config)
    if args.json:
        print(json.dumps({
            "is_hybrid": res["is_hybrid"],
            "stack": res["stack"],
            "plan_length": len(res["plan_markdown"]),
        }, ensure_ascii=False, indent=2))
    else:
        print(res["plan_markdown"])

    return 0


if __name__ == "__main__":
    sys.exit(main())
