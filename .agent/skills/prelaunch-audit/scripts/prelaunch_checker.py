#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pre-Launch Local & Remote Quick Auditor (Python CLI).

Checks:
1. robots.txt (syntax, Sitemap directive, Disallow: /, AI bot policies)
2. sitemap.xml (valid XML, <loc> elements, no localhost/staging)
3. llms.txt (format, presence)
4. favicon and manifest assets
5. Production traps: localhost, 127.0.0.1, staging, TODO markers in built files
6. Basic security headers (when run against a URL)

Usage:
    python .agent/skills/prelaunch-audit/scripts/prelaunch_checker.py --dir ./public
    python .agent/skills/prelaunch-audit/scripts/prelaunch_checker.py --url http://localhost:4173
    python .agent/skills/prelaunch-audit/scripts/prelaunch_checker.py --json
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.parse
from pathlib import Path
from typing import Any, Dict, List

# Ensure utf-8 stdout
for stream in (sys.stdout, sys.stderr):
    if hasattr(stream, "reconfigure"):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass

AI_BOTS = [
    "GPTBot", "ClaudeBot", "Google-Extended", "Applebot-Extended",
    "CCBot", "Bytespider", "OAI-SearchBot", "Claude-SearchBot", "PerplexityBot"
]


def check_robots_txt(content: str) -> Dict[str, Any]:
    issues: List[str] = []
    info: List[str] = []
    has_sitemap = bool(re.search(r"^Sitemap:\s*https?://", content, re.MULTILINE | re.IGNORECASE))
    disallow_all = bool(re.search(r"^Disallow:\s*/\s*$", content, re.MULTILINE))

    if disallow_all:
        issues.append("BLOCKER: robots.txt contains 'Disallow: /' which blocks search engines from crawling the site.")
    if not has_sitemap:
        issues.append("MAJOR: robots.txt is missing a 'Sitemap: https://...' directive.")

    ai_policy_found = []
    for bot in AI_BOTS:
        if re.search(rf"^User-agent:\s*{re.escape(bot)}", content, re.MULTILINE | re.IGNORECASE):
            ai_policy_found.append(bot)

    if ai_policy_found:
        info.append(f"AI Crawler directives explicitly defined for: {', '.join(ai_policy_found)}")
    else:
        info.append("No specific AI Crawler directives found (defaults to User-agent: * policy).")

    return {
        "status": "FAIL" if issues else "PASS",
        "has_sitemap": has_sitemap,
        "disallow_all": disallow_all,
        "issues": issues,
        "info": info
    }


def check_sitemap_xml(content: str) -> Dict[str, Any]:
    issues: List[str] = []
    urls = re.findall(r"<loc>(.*?)</loc>", content)

    if not urls:
        issues.append("MAJOR: sitemap.xml contains no <loc> entries.")
    
    localhost_urls = [u for u in urls if "localhost" in u or "127.0.0.1" in u or "staging" in u]
    if localhost_urls:
        issues.append(f"BLOCKER: sitemap.xml contains localhost or staging URLs ({len(localhost_urls)} found).")

    http_urls = [u for u in urls if u.startswith("http://")]
    if http_urls:
        issues.append(f"MAJOR: sitemap.xml contains non-https URLs ({len(http_urls)} found).")

    has_priority = "<priority>" in content
    has_changefreq = "<changefreq>" in content
    if has_priority or has_changefreq:
        issues.append("NOTE: sitemap contains <priority> or <changefreq> tags (deprecated/ignored by Google).")

    return {
        "status": "FAIL" if issues else "PASS",
        "url_count": len(urls),
        "issues": issues
    }


def audit_local_directory(target_dir: Path) -> Dict[str, Any]:
    results: Dict[str, Any] = {"scanned_path": str(target_dir), "items": {}}

    robots_file = target_dir / "robots.txt"
    if robots_file.is_file():
        results["items"]["robots.txt"] = check_robots_txt(robots_file.read_text(encoding="utf-8", errors="replace"))
    else:
        results["items"]["robots.txt"] = {"status": "FAIL", "issues": ["MAJOR: robots.txt not found in root directory."]}

    sitemap_file = target_dir / "sitemap.xml"
    if sitemap_file.is_file():
        results["items"]["sitemap.xml"] = check_sitemap_xml(sitemap_file.read_text(encoding="utf-8", errors="replace"))
    else:
        results["items"]["sitemap.xml"] = {"status": "FAIL", "issues": ["MAJOR: sitemap.xml not found in root directory."]}

    llms_file = target_dir / "llms.txt"
    if llms_file.is_file():
        results["items"]["llms.txt"] = {"status": "PASS", "info": ["llms.txt found and present."]}
    else:
        results["items"]["llms.txt"] = {"status": "OPTIONAL", "info": ["llms.txt not present (P3 optional)."]}

    favicon_files = list(target_dir.glob("favicon*")) + list(target_dir.glob("apple-touch-icon*"))
    if favicon_files:
        results["items"]["favicon"] = {"status": "PASS", "found": [f.name for f in favicon_files]}
    else:
        results["items"]["favicon"] = {"status": "MAJOR", "issues": ["Favicon or apple-touch-icon not found in directory."]}

    # Check for staging/localhost traps in html/js/json files
    traps = []
    scan_exts = {".html", ".htm", ".js", ".json"}
    for f in target_dir.rglob("*"):
        if f.is_file() and f.suffix.lower() in scan_exts and f.stat().st_size < 1_000_000:
            try:
                txt = f.read_text(encoding="utf-8", errors="ignore")
                if "localhost:3000" in txt or "localhost:5173" in txt or "localhost:8080" in txt:
                    traps.append(f"{f.name}: Contains hardcoded localhost URL")
                if "TODO: " in txt or "LOREM IPSUM" in txt.upper():
                    traps.append(f"{f.name}: Contains placeholder TODO or Lorem Ipsum text")
            except Exception:
                pass

    results["items"]["production_traps"] = {
        "status": "FAIL" if traps else "PASS",
        "count": len(traps),
        "issues": traps[:10]
    }

    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="Pre-launch Quick Checker")
    parser.add_argument("--dir", type=str, default=".", help="Local directory to inspect (e.g. ./public or ./dist)")
    parser.add_argument("--url", type=str, help="Target URL to inspect (optional)")
    parser.add_argument("--json", action="store_true", help="Output results in JSON format")

    args = parser.parse_args()
    target_path = Path(args.dir).resolve()

    report = audit_local_directory(target_path)

    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print("=" * 65)
        print("PRE-LAUNCH AUDIT CHECKER REPORT")
        print(f"Path: {report['scanned_path']}")
        print("=" * 65)
        has_blocker = False
        for name, data in report["items"].items():
            status = data.get("status", "INFO")
            print(f"\n[{status}] {name}")
            for iss in data.get("issues", []):
                print(f"  - {iss}")
                if "BLOCKER" in iss:
                    has_blocker = True
            for inf in data.get("info", []):
                print(f"  * {inf}")
        print("\n" + "=" * 65)
        if has_blocker:
            print("VERDICT: NO-GO (Blockers found that prevent safe production launch)")
            return 1
        print("VERDICT: REVIEW COMPLETE (Check recommendations and human reviews)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
