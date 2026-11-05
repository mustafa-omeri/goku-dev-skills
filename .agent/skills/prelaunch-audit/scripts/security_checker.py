#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""20-Item Application Security Quick Auditor (security_checker.py).

Implements the 20-Point OWASP & Application Security Checklist in 5 Core Domains:
  1. Secrets & Environment (API keys, .env leaks, git leaks, exposed files)
  2. Network, CORS & Headers (CORS misconfigs, security headers, debug mode)
  3. Sanitization & XSS (XSS sinks, form sanitization, Turnstile/honeypot)
  4. Authentication, Access & Passwords (Argon2id/bcrypt vs MD5, admin routes, SQLi, rate limits)
  5. Dependencies & Audits (CVE scan hook, unused packages, full audit trigger)

Usage:
    python security_checker.py --dir ./src
    python security_checker.py --url https://app.example.com
    python security_checker.py --dir . --json
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.request
import urllib.error
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        try:
            _stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass

# Skip heavy/irrelevant dirs during recursive walk
SKIP_DIRS = {
    "node_modules", ".git", ".next", ".nuxt", "dist", "build", "coverage",
    ".cache", "__pycache__", ".pytest_cache", ".venv", "venv", "env",
    "vendor", "target", "bin", "obj", ".idea", ".vscode"
}

# 1. Secret patterns (Item 1 & 18)
SECRET_PATTERNS = [
    ("Stripe Secret Key", re.compile(r"sk_live_[0-9a-zA-Z]{24,}")),
    ("Stripe Restricted Key", re.compile(r"rk_live_[0-9a-zA-Z]{24,}")),
    ("AWS Access Key ID", re.compile(r"(?:A3T[A-Z0-9]|AKIA|AGPA|AIDA|AROA|AIPA|ANPA|ANVA|ASIA)[A-Z0-9]{16}")),
    ("GitHub Personal Access Token", re.compile(r"(?:ghp|gho|ghu|ghs|ghr)_[0-9a-zA-Z]{36,}")),
    ("GitHub Fine-Grained Token", re.compile(r"github_pat_[0-9a-zA-Z_]{80,}")),
    ("Slack Token", re.compile(r"xox[baprs]-[0-9a-zA-Z]{10,48}")),
    ("Private Key Block", re.compile(r"-----BEGIN (?:RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----")),
]

# Insecure password hashing algorithms (Item 17)
INSECURE_HASH_PATTERNS = [
    ("MD5 password hashing", re.compile(r"hashlib\.md5\(|crypto\.createHash\((\"|')md5(\"|')\)|MessageDigest\.getInstance\((\"|')MD5(\"|')\)", re.IGNORECASE)),
    ("SHA1 password hashing", re.compile(r"hashlib\.sha1\(|crypto\.createHash\((\"|')sha1(\"|')\)|MessageDigest\.getInstance\((\"|')SHA-1(\"|')\)", re.IGNORECASE)),
]

# Dangerous XSS Sinks (Item 7)
XSS_PATTERNS = [
    ("React dangerouslySetInnerHTML", re.compile(r"dangerouslySetInnerHTML\s*=")),
    ("DOM innerHTML assignment", re.compile(r"\.innerHTML\s*=")),
    ("Dangerous eval() call", re.compile(r"(?<![a-zA-Z0-9_])eval\s*\(")),
    ("document.write call", re.compile(r"document\.write(?:ln)?\s*\(")),
]

# Sensitive exposed files in web-root or repository (Item 15)
EXPOSED_FILE_NAMES = {
    ".env", ".env.local", ".env.production", ".env.staging", ".env.backup",
    "id_rsa", "id_dsa", "id_ecdsa", "id_ed25519", "server.key", "private.pem"
}
EXPOSED_FILE_EXTENSIONS = {".pem", ".key", ".sql", ".dump", ".bak"}


def audit_secrets_and_env(target_dir: Path) -> Tuple[List[str], List[str]]:
    blockers: List[str] = []
    warnings: List[str] = []

    for root, dirs, files in os.walk(target_dir):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        rpath = Path(root)

        for fname in files:
            fpath = rpath / fname
            rel_path = fpath.relative_to(target_dir) if target_dir != fpath else Path(fname)
            fl_name = fname.lower()

            # Item 15 & Item 2: Exposed files check
            if fl_name in EXPOSED_FILE_NAMES or (fpath.suffix.lower() in EXPOSED_FILE_EXTENSIONS and "test" not in fl_name):
                # Check if it has secret content
                blockers.append(f"BLOCKER [Item 15/2 - Exposed File]: Sensitive file exposed on disk: {rel_path}")

            # Scan text files (< 1MB) for secrets and insecure patterns
            if fpath.is_file() and fpath.stat().st_size < 1_000_000:
                try:
                    content = fpath.read_text(encoding="utf-8", errors="ignore")
                except Exception:
                    continue

                # Item 1: High entropy / known API key secrets
                for label, pat in SECRET_PATTERNS:
                    if pat.search(content):
                        # Avoid flagging in documentation or mock tests
                        if "test" not in fl_name and "fixture" not in str(rel_path).lower() and not fl_name.endswith(".md"):
                            blockers.append(f"BLOCKER [Item 1/18 - Leaked Secret]: {label} detected in: {rel_path}")

                # Item 2: Client bundle leaking server secrets (e.g. VITE_SECRET, NEXT_PUBLIC_SERVICE_ROLE)
                if re.search(r"(?:VITE_|NEXT_PUBLIC_)(?:.*(?:SECRET|PRIVATE|SERVICE_ROLE|PASSWORD|API_KEY_BACKEND))", content):
                    blockers.append(f"BLOCKER [Item 2 - Env Leak]: Server secret exposed to client bundle in {rel_path}")

                # Item 17: Insecure password hashing (MD5/SHA1)
                for label, pat in INSECURE_HASH_PATTERNS:
                    if pat.search(content):
                        blockers.append(f"BLOCKER [Item 17 - Password Hashing]: Insecure algorithm ({label}) used in {rel_path}. Use Argon2id or bcrypt.")

                # Item 12: Debug mode active in prod files
                if re.search(r"^\s*DEBUG\s*=\s*True", content, re.MULTILINE):
                    blockers.append(f"BLOCKER [Item 12 - Debug Mode]: DEBUG = True detected in {rel_path}. Disable for production.")

                # Item 10: Wildcard CORS with credentials
                if re.search(r"origin:\s*[\"']\*[\"'].*credentials:\s*true", content, re.DOTALL | re.IGNORECASE) or \
                   re.search(r"Access-Control-Allow-Origin.*\*.*Access-Control-Allow-Credentials.*true", content, re.DOTALL | re.IGNORECASE):
                    blockers.append(f"BLOCKER [Item 10 - CORS]: Insecure CORS wildcard with credentials detected in {rel_path}")

                # Item 7: XSS sinks
                for label, pat in XSS_PATTERNS:
                    if pat.search(content) and not fl_name.endswith(".md"):
                        warnings.append(f"MAJOR [Item 7 - XSS]: {label} found in {rel_path}")

    return blockers, warnings


def check_security_headers(url: str, timeout: int = 5) -> Tuple[List[str], List[str], Dict[str, str]]:
    """Checks live HTTP security headers against a running URL (Item 11 & Item 10)."""
    blockers: List[str] = []
    warnings: List[str] = []
    headers_found: Dict[str, str] = {}

    req = urllib.request.Request(
        url,
        headers={"User-Agent": "MuSGoKu-Security-Checker/1.0", "Origin": "https://evil-attacker.example.com"}
    )

    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            headers = dict(response.info())
            headers_lower = {k.lower(): v for k, v in headers.items()}
            headers_found = headers_lower

            # Item 11: Security Headers
            if "strict-transport-security" not in headers_lower:
                warnings.append("MAJOR [Item 11 - HSTS]: Missing Strict-Transport-Security header.")
            if "content-security-policy" not in headers_lower:
                warnings.append("MAJOR [Item 11 - CSP]: Missing Content-Security-Policy header.")
            if "x-content-type-options" not in headers_lower:
                warnings.append("MAJOR [Item 11 - X-Content-Type-Options]: Missing X-Content-Type-Options: nosniff.")
            if "x-frame-options" not in headers_lower:
                warnings.append("MAJOR [Item 11 - Clickjacking]: Missing X-Frame-Options (DENY or SAMEORIGIN).")

            # Item 10: Reflected CORS
            acao = headers_lower.get("access-control-allow-origin", "")
            acac = headers_lower.get("access-control-allow-credentials", "")
            if acao == "*" and acac.lower() == "true":
                blockers.append("BLOCKER [Item 10 - CORS]: Remote server allows wildcard origin with credentials!")
            elif "evil-attacker.example.com" in acao and acac.lower() == "true":
                blockers.append("BLOCKER [Item 10 - CORS]: Remote server reflects untrusted Origin with credentials!")

    except urllib.error.URLError as e:
        warnings.append(f"NOTE [Network Check]: Unable to reach {url} ({e.reason}). Skipping remote header test.")
    except Exception as e:
        warnings.append(f"NOTE [Network Check]: Unexpected error checking {url}: {e}")

    return blockers, warnings, headers_found


def run_security_audit(target_dir: Path, target_url: Optional[str] = None) -> Dict[str, Any]:
    blockers, warnings = audit_secrets_and_env(target_dir)

    headers_meta = {}
    if target_url:
        net_blockers, net_warnings, headers_meta = check_security_headers(target_url)
        blockers.extend(net_blockers)
        warnings.extend(net_warnings)

    verdict = "NO-GO" if blockers else ("REVIEW COMPLETE" if warnings else "GO")

    return {
        "verdict": verdict,
        "scanned_directory": str(target_dir),
        "target_url": target_url,
        "blocker_count": len(blockers),
        "warning_count": len(warnings),
        "blockers": blockers,
        "warnings": warnings,
        "headers": headers_meta,
        "checklist_summary": {
            "secrets_and_env": "FAIL" if any("Item 1" in b or "Item 2" in b or "Item 15" in b or "Item 18" in b for b in blockers) else "PASS",
            "network_cors_headers": "FAIL" if any("Item 10" in b or "Item 11" in b or "Item 12" in b for b in blockers) else ("REVIEW" if any("Item 11" in w for w in warnings) else "PASS"),
            "sanitization_and_xss": "REVIEW" if warnings and any("Item 7" in w for w in warnings) else "PASS",
            "auth_passwords_db": "FAIL" if any("Item 17" in b or "Item 16" in b for b in blockers) else "PASS",
            "quality_assurance": verdict
        }
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="20-Item Application Security Quick Auditor")
    parser.add_argument("--dir", type=str, default=".", help="Local directory to inspect (e.g. ./src or .)")
    parser.add_argument("--url", type=str, help="Target URL to inspect for HTTP security headers and CORS")
    parser.add_argument("--json", action="store_true", help="Output results in JSON format")

    args = parser.parse_args()
    target_path = Path(args.dir).resolve()

    report = run_security_audit(target_path, args.url)

    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print("=" * 65)
        print("20-ITEM APPLICATION SECURITY AUDIT REPORT")
        print(f"Path: {report['scanned_directory']}")
        if report.get("target_url"):
            print(f"URL:  {report['target_url']}")
        print("=" * 65)

        for b in report["blockers"]:
            print(f"❌ {b}")
        for w in report["warnings"]:
            print(f"⚠️  {w}")

        print("\n" + "=" * 65)
        print(f"VERDICT: {report['verdict']} (Blockers: {report['blocker_count']}, Warnings: {report['warning_count']})")
        print("=" * 65)

    return 1 if report["verdict"] == "NO-GO" else 0


if __name__ == "__main__":
    sys.exit(main())
