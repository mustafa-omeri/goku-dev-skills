#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pre-Launch Regulatory & Platform Reference Updater (/prelaunch-update).

Scans `.agent/skills/prelaunch-audit/references/` for hardcoded regulatory
figures, verification dates, and platform policy citations.

Enables the AI agent to:
1. Verify freshness of legal metrics (KVKK fines, GDPR, EAA, Google updates).
2. Generate structured web research prompts to check official updates.
3. Apply surgical patches to keep the skill's reference guidelines current.

Usage:
    python .agent/skills/prelaunch-audit/scripts/prelaunch_updater.py --check
    python .agent/skills/prelaunch-audit/scripts/prelaunch_updater.py --generate-prompt
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

# Ensure utf-8 stdout
for stream in (sys.stdout, sys.stderr):
    if hasattr(stream, "reconfigure"):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass

SKILL_DIR = Path(__file__).resolve().parents[1]
REFERENCES_DIR = SKILL_DIR / "references"

TRACKED_REGULATORY_TARGETS = [
    {
        "id": "kvkk_fines",
        "name": "KVKK İdari Para Cezaları & 7499 s. Kanun Bildirim İhlali",
        "pattern": r"(\d{2,3}\.\d{3}\s*TL\s*-\s*\d{1,2}\.\d{3}\.\d{3}\s*TL)",
        "source": "Resmî Gazete / KVKK Yeniden Değerleme Oranı Tebliği",
        "file": "legal-privacy-compliance.md"
    },
    {
        "id": "reklam_kurulu_28b",
        "name": "Reklam Kurulu Tüketici Değerlendirmeleri (m.28/B) Cezaları",
        "pattern": r"(\d{1,2}\.\d{3}\.\d{3}\s*TL)",
        "source": "Ticaret Bakanlığı / Reklam Kurulu Kararları (RG 33297)",
        "file": "trust-and-local-structure.md"
    },
    {
        "id": "google_consent_mode",
        "name": "Google Consent Mode v2 Sinyalleri & Uygulama Şartları",
        "pattern": r"(ad_storage|analytics_storage|ad_user_data|ad_personalization)",
        "source": "Google Ads Developer Documentation / Tag Manager Help",
        "file": "legal-privacy-compliance.md"
    },
    {
        "id": "eaa_en301549",
        "name": "EAA (Avrupa Erişilebilirlik Yasası) & EN 301 549 v4.1.1 Durumu",
        "pattern": r"(EN 301 549 v4\.1\.1|European Accessibility Act)",
        "source": "OJEU / ETSI / W3C WCAG 2.2",
        "file": "legal-privacy-compliance.md"
    },
    {
        "id": "google_search_features",
        "name": "Google Search Features & Rich Result Değişiklikleri",
        "pattern": r"(FAQ rich result|sitelinks search box|breadcrumb)",
        "source": "Google Search Central Documentation Updates",
        "file": "seo-and-discoverability.md"
    }
]


def check_freshness() -> dict:
    results = {"status": "OK", "files": [], "findings": []}
    if not REFERENCES_DIR.is_dir():
        return {"status": "ERROR", "message": f"References directory not found: {REFERENCES_DIR}"}

    date_regex = re.compile(r"Son veri doğrulaması:\s*([^\n\r]+)")

    for md_file in sorted(REFERENCES_DIR.glob("*.md")):
        text = md_file.read_text(encoding="utf-8", errors="replace")
        m = date_regex.search(text)
        last_date = m.group(1).strip() if m else "Belirtilmemiş"
        
        file_info = {
            "file": md_file.name,
            "last_verified": last_date,
            "tracked_matches": []
        }

        for target in TRACKED_REGULATORY_TARGETS:
            if target["file"] == md_file.name:
                matches = re.findall(target["pattern"], text)
                if matches:
                    file_info["tracked_matches"].append({
                        "name": target["name"],
                        "matches": matches[:3],
                        "official_source": target["source"]
                    })

        results["files"].append(file_info)

    return results


def generate_update_prompt() -> str:
    freshness = check_freshness()
    lines = [
        "## AI Agent İçin /prelaunch-update Araştırma ve Güncelleme Özeti",
        "",
        "Aşağıdaki resmi ve yasal referanslar internetten veya en güncel resmi kaynaklardan teyit edilmelidir:",
        ""
    ]
    for target in TRACKED_REGULATORY_TARGETS:
        lines.append(f"### {target['name']}")
        lines.append(f"- **Hedef Dosya:** `.agent/skills/prelaunch-audit/references/{target['file']}`")
        lines.append(f"- **Resmi Kaynak:** {target['source']}")
        lines.append(f"- **Aranacak Konu:** {target['name']} son yürürlük tarihi, yeniden değerleme oranı ve resmi tebliğ güncellemeleri.")
        lines.append("")
    lines.extend([
        "### Güncelleme Prosedürü:",
        "1. Yukarıdaki konularla ilgili Resmî Gazete, KVKK.gov.tr, Ticaret Bakanlığı ve Google Search Central duyurularını araştırın.",
        "2. Eğer idari para cezası alt/üst sınırları veya Google kuralları değişmişse, ilgili referans dosyasındaki rakamı güncelleyin.",
        "3. İlgili markdown dosyasının başındaki `Son veri doğrulaması: <Tarih>` satırını bugünün tarihiyle güncelleyin.",
        "4. Yapılan cerrahi değişiklikleri devir raporunda beyan edin."
    ])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Pre-Launch Reference Updater Helper")
    parser.add_argument("--check", action="store_true", help="Check verification freshness")
    parser.add_argument("--generate-prompt", action="store_true", help="Generate AI update prompt")
    parser.add_argument("--json", action="store_true", help="Output in JSON")

    args = parser.parse_args()

    if args.generate_prompt:
        print(generate_update_prompt())
        return 0

    report = check_freshness()
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
        return 0

    print("=" * 65)
    print("PRE-LAUNCH REGULATORY & PLATFORM REFERENCES FRESHNESS")
    print("=" * 65)
    for f in report.get("files", []):
        print(f"\n[DOSYA] {f['file']}")
        print(f"  Son Doğrulama Tarihi: {f['last_verified']}")
        if f["tracked_matches"]:
            print("  İzlenen Yasal / Platform Maddeleri:")
            for m in f["tracked_matches"]:
                print(f"    - {m['name']} -> {m['matches']} (Kaynak: {m['official_source']})")
    print("\n" + "=" * 65)
    print("Mevzuat veya platform güncellemesi yapmak için:")
    print("  python .agent/skills/prelaunch-audit/scripts/prelaunch_updater.py --generate-prompt")
    return 0


if __name__ == "__main__":
    sys.exit(main())
