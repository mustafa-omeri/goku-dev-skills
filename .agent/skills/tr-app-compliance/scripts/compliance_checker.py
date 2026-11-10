#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Compliance Scanner (CLI).
Checks for:
1. Google Fonts CDN usage (KVKK compliance).
2. Subscription/Renewal text in checkout files.
3. Unsubscribe/MERSIS/Address in email templates.
4. Nginx Real-IP configuration (when Nginx config provided).
"""

import argparse
import os
import re
from pathlib import Path

def scan_files(root_dir: str):
    print(f"[*] Scanning {root_dir} for compliance issues...")
    
    # 1. Font Check
    font_pattern = re.compile(r"fonts\.(googleapis|gstatic)\.com")
    
    # 2. Subscription/Renewal Check
    sub_pattern = re.compile(r"(otomatik yenileme|abonelik periyodu|iptal şartları)", re.IGNORECASE)
    
    # 3. Email Check
    email_pattern = re.compile(r"(unsubscribe|abonelikten çık|mersis|açık adres)", re.IGNORECASE)

    for path in Path(root_dir).rglob('*'):
        if path.is_file() and path.suffix in ['.html', '.tsx', '.jsx', '.js', '.css', '.md']:
            try:
                content = path.read_text(encoding='utf-8')
                
                # Font check
                if font_pattern.search(content):
                    print(f"[WARN] External Font CDN found in {path}")

                # Subscription check
                if path.name in ['checkout.tsx', 'pricing.tsx'] and not sub_pattern.search(content):
                    print(f"[FAIL] Subscription/Renewal notice missing in {path}")

                # Email check
                if 'email' in str(path) and not email_pattern.search(content):
                    print(f"[FAIL] Unsubscribe/Künye missing in {path}")
            except Exception as e:
                pass

def check_nginx(nginx_path: str):
    print(f"[*] Checking Nginx config at {nginx_path}")
    if os.path.exists(nginx_path):
        content = Path(nginx_path).read_text()
        if "real_ip_header CF-Connecting-IP" not in content:
            print("[FAIL] Cloudflare Real-IP configuration missing in Nginx config.")
        else:
            print("[PASS] Cloudflare Real-IP detected.")
    else:
        print("[ERROR] Nginx config file not found.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir", default=".")
    parser.add_argument("--nginx-conf")
    args = parser.parse_args()
    
    scan_files(args.dir)
    if args.nginx_conf:
        check_nginx(args.nginx_conf)

