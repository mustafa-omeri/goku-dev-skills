#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Private Repo Scout HTML Kataloğu Üreticisi (Link-Panosu Tasarımı).

repos.json içindeki verileri ve scout planlarını okuyarak link-panosu.html
estetiğinde (organik kağıt tonları, iki kolonlu sticky composer, zengin kartlar,
gelişmiş pano ayrıştırma motoru) tam teşekküllü bir dashboard üretir.
"""

from datetime import datetime
import json
import re
from pathlib import Path
import sys
from typing import Any, Dict, List

# Windows Unicode çıkış desteği
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        try:
            _stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

SCOUT_DIR = Path(__file__).resolve().parent
REPOS_JSON = SCOUT_DIR / "repos.json"
CATALOG_HTML = SCOUT_DIR / "scout-catalog.html"


def _extract_plan_summary(plan_text: str) -> Dict[str, str]:
    if not plan_text:
        return {"tech_stack": "", "core_value": "", "delta_to_us": "", "action_plan": ""}

    summary = {
        "tech_stack": "",
        "core_value": "",
        "delta_to_us": "",
        "action_plan": ""
    }

    # 1. Teknoloji Yigini
    tech_m = re.search(r"-\s+\*\*Teknoloji\s+Y[ıi]g[ıi]n[ıi]:\*\*\s*(.+)", plan_text, re.I)
    if tech_m:
        summary["tech_stack"] = tech_m.group(1).strip()

    # 2. Bolum 2: Ne Yapar & Cekirdek Felsefe
    sec2_m = re.search(r"##\s+2\.[^\r\n]+[\r\n]+([\s\S]*?)(?=##\s+3\.|\Z)", plan_text)
    if sec2_m:
        raw_lines = [l.strip() for l in sec2_m.group(1).splitlines() if l.strip() and not l.strip().startswith("---")]
        clean = []
        for l in raw_lines:
            l_clean = re.sub(r"^[-*]\s+(\*\*([^*]+)\*\*:\s*)?", "", l)
            l_clean = re.sub(r"\*\*([^*]+)\*\*", r"\1", l_clean)
            if len(l_clean) > 25 and not l_clean.startswith("1.") and not l_clean.startswith("2."):
                clean.append(l_clean)
                if len(clean) >= 2:
                    break
        summary["core_value"] = " ".join(clean)[:260]

    # 3. Bolum 3: Bizim Sisteme Degeri (Delta Analizi)
    delta_m = re.search(r"-\s+\*\*D[ıi]s\s+Repodaki\s+Deger:\*\*\s*([\s\S]*?)(?=-\s+\*\*|[\r\n]{2,}|##|\Z)", plan_text, re.I)
    if delta_m:
        val = re.sub(r"\s+", " ", delta_m.group(1).strip())
        val = re.sub(r"\*\*([^*]+)\*\*", r"\1", val)
        summary["delta_to_us"] = val[:240]
    else:
        sec3_m = re.search(r"##\s+3\.[^\r\n]+[\r\n]+([\s\S]*?)(?=##\s+4\.|\Z)", plan_text)
        if sec3_m:
            lines = [l.strip() for l in sec3_m.group(1).splitlines() if l.strip().startswith("-") or l.strip().startswith("*")]
            if lines:
                val = re.sub(r"^[-*]\s+(\*\*([^*]+)\*\*:\s*)?", "", lines[-1])
                summary["delta_to_us"] = re.sub(r"\*\*([^*]+)\*\*", r"\1", val)[:240]

    # 4. Bolum 5: Cerrahi Entegrasyon Eylemleri / Hedef
    sec5_m = re.search(r"##\s+5\.[^\r\n]+[\r\n]+([\s\S]*?)(?=##|\Z)", plan_text)
    if sec5_m:
        acts = []
        for l in sec5_m.group(1).splitlines():
            l_str = l.strip()
            if re.match(r"^(\d+\.|\*|-)\s+", l_str):
                clean_act = re.sub(r"^(\d+\.|\*|-)\s+(\*\*([^*]+)\*\*:\s*)?", r"\3: ", l_str)
                clean_act = re.sub(r"\*\*([^*]+)\*\*", r"\1", clean_act).strip().strip(": ")
                acts.append(clean_act)
                if len(acts) >= 2:
                    break
        summary["action_plan"] = " • ".join(acts)[:260]

    return summary

def parse_repos_md() -> List[Dict[str, Any]]:
    """repos.json dosyasını okur ve UI için zenginleştirilmiş liste döner."""
    if not REPOS_JSON.is_file():
        return []

    try:
        content = REPOS_JSON.read_text(encoding="utf-8")
        data = json.loads(content)
    except Exception as e:
        print(f"[!] repos.json okunamadı: {e}", file=sys.stderr)
        return []

    repos: List[Dict[str, Any]] = []
    for item in data:
        plan_file = item.get("plan_file", "")
        plan_title = Path(plan_file).stem if plan_file else ""
        plan_content = ""
        if plan_file:
            plan_path = SCOUT_DIR / plan_file
            if plan_path.is_file():
                plan_content = plan_path.read_text(encoding="utf-8", errors="replace")

        repos.append({
            "id": item.get("id", len(repos) + 1),
            "url": item.get("url", ""),
            "name": item.get("name", item.get("url", "").split("/")[-1]),
            "owner": item.get("owner", ""),
            "layer": item.get("layer", "Belirsiz"),
            "status": item.get("status", "PENDING").upper(),
            "progress": item.get("progress", 0),
            "target_skill": item.get("target_skill", ""),
            "transferred_to": item.get("transferred_to", ""),
            "history": item.get("history", []),
            "verdict": item.get("verdict", "-"),
            "plan_file": plan_file,
            "plan_title": plan_title,
            "plan_content": plan_content,
            "date": item.get("date", "-"),
            "summary": _extract_plan_summary(plan_content)
        })
    return repos


def generate_html(repos: List[Dict[str, Any]]) -> str:
    """Link-Panosu estetiğinde şık, modern ve çift kolonlu Scout Kataloğu HTML'i derler."""
    total = len(repos)
    pending_count = sum(1 for r in repos if r["status"] == "PENDING")
    transferring_count = sum(1 for r in repos if r["status"] == "TRANSFERRING")
    planned_count = sum(1 for r in repos if r["status"] == "PLANNED")
    transferred_count = sum(1 for r in repos if r["status"] == "TRANSFERRED")
    rejected_count = sum(1 for r in repos if r["status"] == "REJECTED")
    done_count = sum(1 for r in repos if r["status"] == "DONE")
    suspended_count = sum(1 for r in repos if r["status"] == "SUSPENDED")
    cancel_count = sum(1 for r in repos if r["status"] in ("CANCEL", "CANCELED", "CANCELLED"))
    better_count = sum(1 for r in repos if r["status"] == "REJECTED" or "BIZ_DAHA_IYIYIZ" in r["verdict"].upper() or "DAHA IYIYIZ" in r["verdict"].upper())
    enrich_count = sum(1 for r in repos if r["status"] in ("PLANNED", "TRANSFERRING", "TRANSFERRED") or "ZENGINLESTIR" in r["verdict"].upper() or "KABUL" in r["verdict"].upper() or "AKTARILDI" in r["verdict"].upper())

    fe_count = sum(1 for r in repos if "FRONTEND" in r["layer"].upper())
    be_count = sum(1 for r in repos if "BACKEND" in r["layer"].upper())
    tooling_count = sum(1 for r in repos if "TOOLING" in r["layer"].upper() or "AGENTIC" in r["layer"].upper())

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    repos_json = json.dumps(repos, ensure_ascii=False)

    template = """<!doctype html>
<html lang="tr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>🔭 Private Repo Scout & Intelligence Board</title>
  <style>
    :root {
      --ink: #183b37;
      --muted: #6b7b77;
      --line: #dce5df;
      --green: #22765f;
      --mint: #e7f2d9;
      --paper: #f7f8f3;
      --surface: #ffffff;
      --surface-hover: #f0f5ee;
      --amber: #b45309;
      --amber-bg: #fef3c7;
      --rose: #b91c1c;
      --rose-bg: #fef2f2;
      --sky: #0369a1;
      --sky-bg: #e0f2fe;
      --radius-sm: 8px;
      --radius-md: 12px;
      --radius-lg: 16px;
      --radius-xl: 20px;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      background: var(--paper);
      color: var(--ink);
      font: 14.5px/1.55 system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
    }
    button, input, textarea, select { font: inherit; }
    button, a, input, textarea, select { outline-offset: 3px; }
    button { cursor: pointer; }
    button:disabled { opacity: .45; cursor: not-allowed; }
    button {
      border: 1px solid var(--line);
      background: #fff;
      border-radius: 11px;
      padding: 9px 15px;
      color: var(--ink);
      font-weight: 600;
      display: inline-flex;
      gap: 7px;
      align-items: center;
      justify-content: center;
      transition: background .15s, transform .15s, border-color .15s;
    }
    button:hover:not(:disabled) { background: var(--surface-hover); }
    button:active:not(:disabled) { transform: translateY(1px); }
    svg {
      width: 18px;
      height: 18px;
      fill: none;
      stroke: currentColor;
      stroke-width: 1.75;
      stroke-linecap: round;
      stroke-linejoin: round;
      flex: none;
    }
    .primary {
      background: var(--ink);
      border-color: var(--ink);
      color: white;
    }
    .primary:hover:not(:disabled) {
      background: #27544a;
      border-color: #27544a;
    }
    .btn-green {
      background: var(--green);
      border-color: var(--green);
      color: white;
    }
    .btn-green:hover:not(:disabled) { background: #1c634f; }
    .btn-rose {
      background: #fff;
      border-color: #fca5a5;
      color: var(--rose);
    }
    .btn-rose:hover:not(:disabled) { background: var(--rose-bg); }
    .quiet {
      background: transparent;
      border-color: transparent;
    }
    .quiet:hover:not(:disabled) { background: rgba(24, 59, 55, 0.05); }
    .small {
      font-size: 12.5px;
      padding: 6px 11px;
      border-radius: 9px;
    }
    header {
      max-width: 1380px;
      margin: auto;
      padding: 22px 32px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      border-bottom: 1px solid var(--line);
    }
    .brand {
      display: flex;
      align-items: center;
      gap: 11px;
      font-weight: 750;
      font-size: 19px;
      letter-spacing: -.5px;
      text-decoration: none;
      color: var(--ink);
    }
    .brand-icon {
      display: grid;
      place-items: center;
      background: var(--ink);
      color: var(--mint);
      width: 38px;
      height: 38px;
      border-radius: 12px;
    }
    .brand-badge {
      font-size: 11px;
      background: var(--mint);
      color: var(--green);
      padding: 2px 7px;
      border-radius: 6px;
      font-weight: 700;
      letter-spacing: 0.5px;
    }
    .header-right {
      display: flex;
      align-items: center;
      gap: 14px;
    }
    .local {
      font-size: 12px;
      color: var(--muted);
      display: flex;
      align-items: center;
      gap: 7px;
      background: #fff;
      padding: 6px 12px;
      border-radius: 20px;
      border: 1px solid var(--line);
    }
    .dot {
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: #94a3b8;
      transition: background .3s;
    }
    .dot.online {
      background: #52a175;
      box-shadow: 0 0 0 3px rgba(82, 161, 117, 0.2);
    }
    main {
      max-width: 1380px;
      margin: auto;
      padding: 34px 32px 60px;
    }
    .intro {
      display: flex;
      align-items: flex-end;
      justify-content: space-between;
      gap: 20px;
      margin-bottom: 28px;
    }
    .eyebrow {
      font-size: 11px;
      letter-spacing: 2px;
      font-weight: 700;
      color: var(--green);
      margin-bottom: 6px;
      text-transform: uppercase;
    }
    h1 {
      font-size: clamp(26px, 3.5vw, 38px);
      letter-spacing: -1.4px;
      line-height: 1.15;
      margin: 0 0 8px;
      color: var(--ink);
    }
    .intro p {
      margin: 0;
      color: var(--muted);
      font-size: 14.5px;
    }
    .counter-group {
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
    }
    .counter {
      font-size: 12px;
      white-space: nowrap;
      background: #fff;
      border: 1px solid var(--line);
      border-radius: 30px;
      padding: 8px 14px;
      color: var(--muted);
    }
    .counter b { color: var(--ink); font-weight: 700; }
    .counter b.green { color: var(--green); }
    .counter b.amber { color: var(--amber); }

    /* İki Kolonlu Workspace Düzeni */
    .workspace {
      display: grid;
      grid-template-columns: 360px 1fr;
      gap: 28px;
      align-items: start;
    }

    /* Sol Kolon: Sticky Composer */
    .composer {
      background: white;
      border: 1px solid var(--line);
      border-radius: var(--radius-xl);
      padding: 22px;
      position: sticky;
      top: 24px;
      box-shadow: 0 6px 20px rgba(23, 58, 47, 0.04);
    }
    .section-title {
      display: flex;
      align-items: center;
      gap: 8px;
      margin: 0 0 4px;
      font-size: 17px;
      letter-spacing: -.4px;
      font-weight: 700;
    }
    .hint {
      font-size: 12.5px;
      color: var(--muted);
      margin-bottom: 14px;
    }
    .input-wrap {
      margin: 12px 0 10px;
      position: relative;
    }
    textarea {
      width: 100%;
      height: 175px;
      resize: vertical;
      min-height: 120px;
      max-height: 460px;
      border: 1px solid #cfdcd3;
      background: #fafcf8;
      border-radius: var(--radius-md);
      padding: 12px 14px;
      color: var(--ink);
      font: 12.5px/1.7 ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
    }
    textarea:focus {
      outline: 2px solid #9dcba9;
      border-color: transparent;
      background: #fff;
    }
    textarea::placeholder { color: #8c9b91; }
    .form-select {
      width: 100%;
      padding: 9px 12px;
      border: 1px solid #cfdcd3;
      background: #fafcf8;
      border-radius: var(--radius-sm);
      color: var(--ink);
      font-size: 13px;
      margin-bottom: 10px;
    }
    .form-select:focus {
      outline: 2px solid #9dcba9;
      border-color: transparent;
    }
    .toggle {
      display: flex;
      align-items: flex-start;
      gap: 8px;
      font-size: 12px;
      color: var(--muted);
      cursor: pointer;
      margin-bottom: 14px;
    }
    input[type=checkbox] {
      accent-color: var(--green);
      margin: 3px 0 0;
      flex: none;
    }
    .composer-actions {
      display: flex;
      gap: 7px;
    }
    .composer-actions .primary { flex: 1; }

    /* Composer Canlı Önizleme */
    .preview {
      border-top: 1px solid var(--line);
      margin-top: 16px;
      padding-top: 14px;
      font-size: 12px;
    }
    .preview-count {
      display: flex;
      align-items: center;
      gap: 7px;
      color: var(--green);
      font-weight: 650;
      font-size: 12.5px;
    }
    .preview-list {
      max-height: 145px;
      overflow-y: auto;
      margin: 8px 0 0;
      padding-left: 18px;
      color: var(--muted);
      font-size: 12px;
    }
    .preview-list li {
      overflow-wrap: anywhere;
      margin-bottom: 4px;
    }
    .status-msg {
      margin-top: 14px;
      font-size: 12px;
      color: var(--green);
      min-height: 18px;
      line-height: 1.4;
    }
    .status-msg.error { color: var(--rose); }
    .status-msg.info { color: var(--sky); }
    .composer-note {
      margin-top: 16px;
      padding: 12px 14px;
      border-radius: 10px;
      background: #f2f6ed;
      font-size: 11.5px;
      color: #62715e;
      line-height: 1.5;
    }
    .composer-note strong {
      color: #3b4e36;
      display: block;
      margin-bottom: 3px;
    }

    /* Sağ Kolon: Board */
    .board-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 12px;
      margin-bottom: 14px;
      flex-wrap: wrap;
    }
    .board-header h2 {
      margin: 0;
      font-size: 19px;
      letter-spacing: -.4px;
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .board-toolbar {
      display: flex;
      gap: 6px;
      align-items: center;
      flex-wrap: wrap;
    }

    /* Filtre Hapları */
    .filter-tabs {
      display: flex;
      gap: 4px;
      background: #eaefe9;
      padding: 3px;
      border-radius: 10px;
      overflow-x: auto;
    }
    .tab-btn {
      border: none;
      background: transparent;
      padding: 6px 11px;
      border-radius: 7px;
      font-size: 12px;
      font-weight: 600;
      color: var(--muted);
      white-space: nowrap;
    }
    .tab-btn:hover { background: rgba(255, 255, 255, 0.5); color: var(--ink); }
    .tab-btn.active {
      background: #fff;
      color: var(--ink);
      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
    }
    .search-wrap {
      position: relative;
      margin-bottom: 18px;
    }
    .search {
      width: 100%;
      border: 1px solid var(--line);
      background: white;
      border-radius: 11px;
      padding: 10px 14px 10px 40px;
      color: var(--ink);
      font-size: 13.5px;
      transition: border-color .15s, outline .15s;
    }
    .search:focus {
      outline: 2px solid #9dcba9;
      border-color: transparent;
    }
    .search-wrap svg {
      position: absolute;
      left: 13px;
      top: 11px;
      color: var(--muted);
    }

    /* Repo Kartları Izgarası (Grid View) */
    .grid {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 14px;
    }
    .card {
      background: #fff;
      border: 1px solid var(--line);
      border-radius: var(--radius-lg);
      padding: 18px;
      min-width: 0;
      animation: appear .2s ease-out;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      transition: transform .15s, box-shadow .15s, border-color .15s;
    }
    .card:hover {
      border-color: #cbd8cf;
      box-shadow: 0 4px 14px rgba(24, 59, 55, 0.05);
    }
    .card-top {
      display: flex;
      align-items: center;
      gap: 10px;
      margin-bottom: 10px;
    }
    .favicon {
      border-radius: 10px;
      background: var(--mint);
      color: var(--green);
      height: 38px;
      width: 38px;
      display: grid;
      place-items: center;
      font-size: 16px;
      font-weight: 800;
      flex: none;
    }
    .card-meta {
      min-width: 0;
      flex: 1;
    }
    .domain {
      font-size: 11.5px;
      color: var(--muted);
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      display: block;
    }
    .card h3 {
      font-size: 15.5px;
      margin: 1px 0 0;
      letter-spacing: -.3px;
      overflow-wrap: anywhere;
      color: var(--ink);
    }
    .card h3 a {
      color: inherit;
      text-decoration: none;
    }
    .card h3 a:hover { color: var(--green); text-decoration: underline; }
    .badge-group {
      display: flex;
      gap: 5px;
      flex-wrap: wrap;
      margin: 8px 0 10px;
    }
    .badge {
      display: inline-flex;
      align-items: center;
      gap: 4px;
      padding: 2.5px 8px;
      border-radius: 6px;
      font-size: 11px;
      font-weight: 600;
      line-height: 1.3;
    }
    .badge-private {
      background: #f1f5f9;
      color: #475569;
      border: 1px solid #e2e8f0;
    }
    .badge-layer {
      background: #eef2ff;
      color: #4338ca;
    }
    .badge-pending {
      background: var(--amber-bg);
      color: var(--amber);
    }
    .badge-done {
      background: var(--mint);
      color: var(--green);
    }
    .badge-better {
      background: #ecfdf5;
      color: #047857;
      border: 1px solid #a7f3d0;
      font-weight: 700;
    }
    .badge-enrich {
      background: var(--sky-bg);
      color: var(--sky);
      border: 1px solid #bae6fd;
    }
    .badge-reject {
      background: var(--rose-bg);
      color: var(--rose);
    }
    /* Yeni Rozet ve Kart Stilleri */
    .tab-btn b {
      font-size: 11px;
      padding: 1px 6px;
      border-radius: 10px;
      background: rgba(0,0,0,0.06);
      margin-left: 4px;
      font-weight: 700;
    }
    .tab-btn.active b {
      background: rgba(255,255,255,0.25);
      color: #fff;
    }
    .badge-to-integrate {
      background: #ecfdf5;
      color: #047857;
      border: 1px solid #a7f3d0;
      font-weight: 700;
    }
    .badge-planned {
      background: #e0f2fe;
      color: #0369a1;
      border: 1px solid #bae6fd;
      font-weight: 700;
    }
    .badge-transferring {
      background: #f3e8ff;
      color: #7e22ce;
      border: 1px solid #d8b4fe;
      font-weight: 700;
      animation: pulseGlow 1.8s infinite ease-in-out;
    }
    .badge-transferred {
      background: #eff6ff;
      color: #1d4ed8;
      border: 1px solid #bfdbfe;
      font-weight: 700;
    }
    .badge-rejected {
      background: #f1f5f9;
      color: #475569;
      border: 1px solid #cbd5e1;
      font-weight: 700;
    }
    @keyframes pulseGlow {
      0%, 100% { box-shadow: 0 0 0 0 rgba(168, 85, 247, 0.4); }
      50% { box-shadow: 0 0 0 4px rgba(168, 85, 247, 0.15); }
    }
    .card-transferring {
      border-color: #c084fc !important;
      box-shadow: 0 4px 14px rgba(147, 51, 234, 0.08) !important;
      background: linear-gradient(180deg, #faf5ff 0%, #ffffff 100%) !important;
    }
    .card-transferred {
      border-color: #93c5fd !important;
      box-shadow: 0 4px 14px rgba(37, 99, 235, 0.06) !important;
    }
    .badge-partial {
      background: #f0fdfa;
      color: #0f766e;
      border: 1px solid #99f6e4;
      font-weight: 700;
    }
    .badge-tech {
      background: #f8fafc;
      color: #64748b;
      border: 1px solid #e2e8f0;
      font-family: var(--font-mono, monospace);
      font-size: 10.5px;
    }
    .badge-suspended {
      background: #fef3c7;
      color: #92400e;
      border: 1px solid #fde68a;
      font-weight: 700;
    }
    .badge-cancel {
      background: #fee2e2;
      color: #991b1b;
      border: 1px solid #fecaca;
      font-weight: 700;
    }
    .card-suspended {
      border-color: #fde68a !important;
      background: linear-gradient(180deg, #fffdfa 0%, #ffffff 100%) !important;
    }
    .card-cancel {
      border-color: #fecaca !important;
      background: linear-gradient(180deg, #fffbfb 0%, #ffffff 100%) !important;
      opacity: 0.88;
    }
    .card-cancel h3 a {
      text-decoration: line-through;
      color: #991b1b;
    }
    .card-to-integrate {
      border-color: #86efac !important;
      box-shadow: 0 4px 12px rgba(16, 185, 129, 0.08) !important;
    }
    .verdict-box {
      background: #f8fafc;
      border: 1px solid #e2e8f0;
      border-left: 3.5px solid #94a3b8;
      border-radius: 8px;
      padding: 9px 12px;
      margin: 10px 0 11px;
      font-size: 12px;
      line-height: 1.45;
    }
    .verdict-box.verdict-to-integrate {
      background: #f0fdf4;
      border-color: #bbf7d0;
      border-left-color: #16a34a;
      color: #14532d;
    }
    .verdict-box.verdict-partial {
      background: #f0fdfa;
      border-color: #99f6e4;
      border-left-color: #0d9488;
      color: #134e4a;
    }
    .verdict-box.verdict-transferred {
      background: #eff6ff;
      border-color: #bfdbfe;
      border-left-color: #2563eb;
      color: #1e3a8a;
    }
    .verdict-box.verdict-better {
      background: #f8fafc;
      border-color: #e2e8f0;
      border-left-color: #64748b;
      color: #334155;
    }
    .verdict-box.verdict-suspended {
      background: #fffbeb;
      border-color: #fde68a;
      border-left-color: #d97706;
      color: #78350f;
    }
    .verdict-box.verdict-cancel {
      background: #fef2f2;
      border-color: #fecaca;
      border-left-color: #dc2626;
      color: #7f1d1d;
    }
    .status-select-wrap {
      display: inline-flex;
      align-items: center;
      position: relative;
    }
    .status-select {
      appearance: none;
      -webkit-appearance: none;
      background: #ffffff;
      border: 1px solid var(--line, #dce5df);
      border-radius: 6px;
      padding: 2px 20px 2px 8px;
      font-size: 11px;
      font-weight: 600;
      color: var(--ink, #183b37);
      cursor: pointer;
      transition: border-color 0.15s, box-shadow 0.15s, background-color 0.15s;
      background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='10' height='10' viewBox='0 0 24 24' fill='none' stroke='%236b7b77' stroke-width='2.5' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='6 9 12 15 18 9'%3E%3C/polyline%3E%3C/svg%3E");
      background-repeat: no-repeat;
      background-position: right 6px center;
    }
    .status-select:hover {
      border-color: var(--green, #22765f);
    }
    .status-select:focus {
      outline: none;
      border-color: var(--green, #22765f);
      box-shadow: 0 0 0 2px rgba(34, 118, 95, 0.15);
    }
    .status-select.sel-pending {
      background-color: var(--amber-bg, #fef3c7);
      color: var(--amber, #92400e);
      border-color: #fde68a;
    }
    .status-select.sel-planned {
      background-color: #e0f2fe;
      color: #0369a1;
      border-color: #bae6fd;
    }
    .status-select.sel-transferring {
      background-color: #f3e8ff;
      color: #7e22ce;
      border-color: #d8b4fe;
    }
    .status-select.sel-transferred {
      background-color: #eff6ff;
      color: #1d4ed8;
      border-color: #bfdbfe;
    }
    .status-select.sel-rejected {
      background-color: #f1f5f9;
      color: #475569;
      border-color: #cbd5e1;
    }
    .status-select.sel-done {
      background-color: #ecfdf5;
      color: #047857;
      border-color: #a7f3d0;
    }
    .status-select.sel-suspended {
      background-color: #fffbeb;
      color: #b45309;
      border-color: #fde68a;
    }
    .status-select.sel-cancel, .status-select.sel-canceled, .status-select.sel-cancelled {
      background-color: #fef2f2;
      color: #dc2626;
      border-color: #fecaca;
    }
    /* İlerleme Çubuğu Stilleri */
    .repo-progress-container {
      display: flex;
      align-items: center;
      gap: 7px;
      margin: 6px 0 10px;
      padding: 4px 8px;
      background: #fafcf8;
      border: 1px solid #e2ebe4;
      border-radius: 8px;
    }
    .repo-progress-track {
      flex: 1;
      height: 6px;
      background: #e2e8e4;
      border-radius: 3px;
      overflow: hidden;
    }
    .repo-progress-bar {
      height: 100%;
      border-radius: 3px;
      transition: width .3s ease;
      background: #10b981;
    }
    .repo-progress-bar.bar-transferring {
      background: linear-gradient(90deg, #a855f7 0%, #7e22ce 100%);
    }
    .repo-progress-bar.bar-planned {
      background: #0284c7;
    }
    .repo-progress-bar.bar-transferred {
      background: #2563eb;
    }
    .repo-progress-bar.bar-rejected {
      background: #94a3b8;
    }
    .repo-progress-pct {
      font-size: 11px;
      font-weight: 750;
      color: var(--ink);
      font-family: var(--font-mono, monospace);
    }
    /* Denetim İzi & Audit Trail Kutusu */
    .audit-trail-box {
      margin-top: 10px;
      padding: 9px 12px;
      background: #f8fafc;
      border: 1px solid #e2e8f0;
      border-left: 3.5px solid #6366f1;
      border-radius: 8px;
      font-size: 11.5px;
      line-height: 1.45;
    }
    .audit-trail-title {
      font-weight: 700;
      font-size: 11px;
      color: #4338ca;
      margin-bottom: 4px;
      display: flex;
      align-items: center;
      justify-content: space-between;
    }
    .audit-trail-row {
      display: flex;
      gap: 6px;
      align-items: baseline;
      color: #334155;
    }
    .audit-trail-badge {
      display: inline-block;
      padding: 1px 6px;
      border-radius: 4px;
      font-size: 10px;
      font-weight: 700;
      background: #e0e7ff;
      color: #3730a3;
      white-space: nowrap;
    }
    .verdict-box-title {
      font-weight: 700;
      font-size: 12px;
      margin-bottom: 3px;
      display: flex;
      align-items: center;
      gap: 6px;
    }
    .verdict-box-detail {
      font-size: 11.5px;
      opacity: 0.95;
      overflow-wrap: anywhere;
    }
    .card-summary-section {
      display: flex;
      flex-direction: column;
      gap: 7px;
      margin-bottom: 14px;
      padding: 9px 11px;
      background: #fafaf9;
      border: 1px solid #f0f0ee;
      border-radius: 8px;
      font-size: 11.5px;
      line-height: 1.45;
    }
    .summary-item {
      display: flex;
      gap: 6px;
      align-items: flex-start;
    }
    .summary-label {
      font-weight: 700;
      color: var(--ink);
      white-space: nowrap;
      flex-shrink: 0;
      font-size: 11px;
    }
    .summary-text {
      color: #44403c;
      overflow-wrap: anywhere;
    }
    .btn-integrate {
      background: var(--mint) !important;
      color: var(--green) !important;
      font-weight: 700;
      border: 1px solid #a7f3d0 !important;
    }
    .btn-integrate:hover {
      background: #a7f3d0 !important;
    }
    .card-desc {
      font-size: 12px;
      color: var(--muted);
      margin-bottom: 14px;
      line-height: 1.5;
      max-height: 48px;
      overflow: hidden;
      text-overflow: ellipsis;
      display: -webkit-box;
      -webkit-line-clamp: 2;
      -webkit-box-orient: vertical;
      background: #fafcf8;
      padding: 6px 9px;
      border-radius: 8px;
      border: 1px solid #edf2ec;
    }
    .card-bottom {
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 6px;
      margin-top: auto;
      padding-top: 11px;
      border-top: 1px solid #eef1eb;
      flex-wrap: wrap;
    }
    .card-actions-left {
      display: flex;
      gap: 5px;
      align-items: center;
      flex-wrap: wrap;
    }
    .icon-btn {
      padding: 6px;
      border-color: transparent;
      background: transparent;
      border-radius: 8px;
      color: var(--muted);
    }
    .icon-btn:hover { background: #f0f5ee; color: var(--ink); }
    .icon-btn.delete:hover { color: var(--rose); background: var(--rose-bg); }
    .open {
      font-size: 12px;
      color: var(--green);
      text-decoration: none;
      display: flex;
      align-items: center;
      gap: 4px;
      font-weight: 650;
    }
    .open:hover { text-decoration: underline; }

    /* Tablo Görünümü (List View) */
    .table-container {
      background: #fff;
      border: 1px solid var(--line);
      border-radius: var(--radius-lg);
      overflow-x: auto;
    }
    table {
      width: 100%;
      border-collapse: collapse;
      font-size: 13px;
      text-align: left;
    }
    th {
      padding: 12px 16px;
      background: #f7f9f5;
      color: var(--muted);
      font-weight: 650;
      font-size: 11.5px;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      border-bottom: 1px solid var(--line);
    }
    td {
      padding: 12px 16px;
      border-bottom: 1px solid #edf2ec;
      vertical-align: middle;
    }
    tr:last-child td { border-bottom: none; }
    tr:hover td { background: #fafcf8; }

    /* Boş Durum (Empty State) */
    .empty {
      grid-column: 1 / -1;
      border: 1px dashed #cbd9cd;
      border-radius: var(--radius-xl);
      min-height: 280px;
      display: flex;
      align-items: center;
      justify-content: center;
      text-align: center;
      padding: 28px;
      background: #f3f6ee;
    }
    .empty-mark {
      display: grid;
      place-items: center;
      background: #e3edd8;
      width: 56px;
      height: 56px;
      border-radius: 17px;
      margin: 0 auto 14px;
      color: var(--green);
    }
    .empty h3 { margin: 0 0 6px; font-size: 17px; }
    .empty p { font-size: 12.5px; max-width: 320px; margin: auto; color: var(--muted); }

    /* İnceleme Sırası & Kuyruk Stilleri */
    .floating-queue-bar {
      position: fixed;
      bottom: 24px;
      left: 50%;
      transform: translateX(-50%);
      background: var(--ink);
      color: white;
      border-radius: 16px;
      padding: 10px 18px;
      box-shadow: 0 16px 36px rgba(24, 59, 55, 0.32);
      z-index: 95;
      display: flex;
      align-items: center;
      gap: 14px;
      max-width: 92vw;
      width: 780px;
      animation: appear .25s cubic-bezier(0.16, 1, 0.3, 1);
    }
    .queue-bar-content {
      display: flex;
      justify-content: space-between;
      align-items: center;
      width: 100%;
      gap: 14px;
      flex-wrap: wrap;
    }
    .queue-bar-left {
      display: flex;
      align-items: center;
      gap: 12px;
      min-width: 0;
      flex: 1;
    }
    .queue-icon-badge {
      font-size: 18px;
      background: rgba(255, 255, 255, 0.12);
      width: 36px;
      height: 36px;
      border-radius: 10px;
      display: grid;
      place-items: center;
      flex: none;
    }
    .queue-chips {
      display: flex;
      gap: 5px;
      overflow-x: auto;
      max-width: 360px;
      padding: 2px 0;
    }
    .queue-chip {
      background: rgba(255, 255, 255, 0.15);
      color: #fff;
      padding: 2px 8px;
      border-radius: 6px;
      font-size: 11px;
      font-weight: 600;
      white-space: nowrap;
    }
    .queue-chip b { color: var(--mint); }
    .queue-bar-actions {
      display: flex;
      gap: 7px;
      align-items: center;
      flex: none;
    }
    .badge-queued {
      background: var(--mint);
      color: var(--green);
      border: 1px solid #b7e3c4;
      cursor: pointer;
      font-weight: 700;
    }
    .badge-queued:hover { background: #d7edd8; }
    .badge-queue-add {
      background: #f1f5f9;
      color: #475569;
      border: 1px dashed #cbd5e1;
      cursor: pointer;
    }
    .badge-queue-add:hover { background: #e2e8f0; color: var(--ink); }
    .queue-item-list {
      max-height: 340px;
      overflow-y: auto;
      display: flex;
      flex-direction: column;
      gap: 7px;
      margin-top: 10px;
    }
    .queue-item {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 9px 12px;
      background: #fafcf8;
      border: 1px solid var(--line);
      border-radius: 10px;
      gap: 10px;
      transition: background .15s;
    }
    .queue-item:hover { background: #f0f5ee; }
    .queue-item-rank {
      font-weight: 800;
      font-size: 12px;
      color: var(--green);
      background: var(--mint);
      width: 26px;
      height: 26px;
      border-radius: 7px;
      display: grid;
      place-items: center;
      flex: none;
    }
    .queue-item-info {
      flex: 1;
      min-width: 0;
      font-size: 12.5px;
    }
    .queue-item-controls {
      display: flex;
      gap: 4px;
      align-items: center;
      flex: none;
    }

    /* Modal Stilleri */
    .modal-overlay {
      position: fixed;
      inset: 0;
      background: rgba(24, 59, 55, 0.45);
      backdrop-filter: blur(4px);
      z-index: 100;
      display: none;
      place-items: center;
      padding: 20px;
      opacity: 0;
      transition: opacity .2s;
    }
    .modal-overlay.active {
      display: grid;
      opacity: 1;
    }
    .modal {
      background: #fff;
      border: 1px solid var(--line);
      border-radius: var(--radius-xl);
      width: 100%;
      max-width: 620px;
      max-height: 90vh;
      display: flex;
      flex-direction: column;
      box-shadow: 0 20px 40px rgba(24, 59, 55, 0.15);
      animation: modalPop .2s cubic-bezier(0.16, 1, 0.3, 1);
    }
    .modal-header {
      padding: 18px 22px;
      border-bottom: 1px solid var(--line);
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    .modal-header h3 {
      margin: 0;
      font-size: 17px;
      letter-spacing: -.3px;
    }
    .modal-body {
      padding: 22px;
      overflow-y: auto;
      font-size: 13.5px;
    }
    .modal-footer {
      padding: 14px 22px;
      border-top: 1px solid var(--line);
      display: flex;
      justify-content: flex-end;
      gap: 8px;
      background: #fafcf8;
      border-radius: 0 0 var(--radius-xl) var(--radius-xl);
    }

    /* Modal İçi Tablar */
    .add-tabs {
      display: flex;
      gap: 6px;
      margin-bottom: 16px;
      border-bottom: 1px solid var(--line);
      padding-bottom: 10px;
    }
    .add-tab-btn {
      padding: 6px 12px;
      border-radius: 8px;
      font-size: 12.5px;
      font-weight: 600;
      border: 1px solid transparent;
      background: transparent;
      color: var(--muted);
    }
    .add-tab-btn.active {
      background: var(--surface-hover);
      color: var(--ink);
      border-color: var(--line);
    }
    .form-group {
      margin-bottom: 14px;
    }
    .form-label {
      display: block;
      font-size: 12px;
      font-weight: 650;
      margin-bottom: 5px;
      color: var(--ink);
    }
    .form-input {
      width: 100%;
      padding: 9px 12px;
      border: 1px solid #cfdcd3;
      border-radius: 9px;
      font-size: 13px;
      background: #fafcf8;
      color: var(--ink);
    }
    .form-input:focus {
      outline: 2px solid #9dcba9;
      border-color: transparent;
      background: #fff;
    }
    .form-hint {
      display: block;
      font-size: 11px;
      color: var(--muted);
      margin-top: 4px;
    }

    /* Toplu Ekleme Progress & Liste */
    .bulk-progress-wrap {
      margin-top: 14px;
      padding: 12px;
      background: #f2f6ed;
      border-radius: 10px;
      display: none;
    }
    .progress-track {
      width: 100%;
      height: 6px;
      background: #dce5df;
      border-radius: 3px;
      overflow: hidden;
      margin: 8px 0;
    }
    .progress-bar {
      width: 0%;
      height: 100%;
      background: var(--green);
      transition: width .2s;
    }
    .bulk-item-list {
      max-height: 170px;
      overflow-y: auto;
      border: 1px solid var(--line);
      border-radius: 9px;
      padding: 6px;
      margin-top: 10px;
      background: #fff;
    }
    .bulk-item-row {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 5px 8px;
      border-radius: 6px;
      font-size: 11.5px;
      margin-bottom: 2px;
    }
    .bulk-item-row:hover { background: #f7f9f5; }

    /* Markdown Plan Önizleyici */
    .markdown-body {
      font-family: inherit;
      line-height: 1.6;
      color: var(--ink);
    }
    .markdown-body h1, .markdown-body h2, .markdown-body h3 {
      margin-top: 1.2em;
      margin-bottom: 0.5em;
      letter-spacing: -.3px;
    }
    .markdown-body pre {
      background: #183b37;
      color: #e7f2d9;
      padding: 12px 14px;
      border-radius: 10px;
      overflow-x: auto;
      font: 12px/1.6 ui-monospace, monospace;
    }
    .markdown-body code {
      background: #eef2eb;
      padding: 2px 5px;
      border-radius: 5px;
      font-size: 12px;
      color: var(--ink);
    }
    .markdown-body pre code {
      background: transparent;
      color: inherit;
      padding: 0;
    }

    /* Toast Bildirim */
    #toast {
      position: fixed;
      bottom: 25px;
      left: 50%;
      transform: translate(-50%, 15px);
      background: var(--ink);
      color: white;
      border-radius: 12px;
      padding: 11px 20px;
      opacity: 0;
      pointer-events: none;
      transition: .2s;
      font-size: 13px;
      z-index: 999;
      max-width: 90vw;
      box-shadow: 0 10px 25px rgba(24, 59, 55, 0.25);
    }
    #toast.show {
      opacity: 1;
      transform: translate(-50%, 0);
    }

    /* Animasyonlar & Responsive */
    @keyframes appear {
      from { opacity: 0; transform: translateY(6px); }
      to { opacity: 1; transform: translateY(0); }
    }
    @keyframes modalPop {
      from { opacity: 0; transform: scale(.97); }
      to { opacity: 1; transform: scale(1); }
    }
    @media (max-width: 980px) {
      .workspace { grid-template-columns: 310px 1fr; gap: 20px; }
      .grid { grid-template-columns: 1fr; }
    }
    @media (max-width: 720px) {
      header { padding: 18px 20px; }
      main { padding: 24px 20px; }
      .workspace { grid-template-columns: 1fr; }
      .composer { position: static; }
      .intro { flex-direction: column; align-items: flex-start; }
      .counter-group { width: 100%; }
    }
    @media (prefers-reduced-motion: reduce) {
      *, *:before, *:after { animation: none !important; transition: none !important; }
    }
  </style>
</head>
<body>

  <!-- SVG İkon Kütüphanesi -->
  <svg hidden aria-hidden="true"><defs>
    <symbol id="i-link" viewBox="0 0 24 24"><path d="M10 13a5 5 0 0 0 7 0l3-3a5 5 0 0 0-7-7l-2 2M14 11a5 5 0 0 0-7 0l-3 3a5 5 0 0 0 7 7l2-2"/></symbol>
    <symbol id="i-plus" viewBox="0 0 24 24"><path d="M12 5v14M5 12h14"/></symbol>
    <symbol id="i-copy" viewBox="0 0 24 24"><rect x="8" y="8" width="12" height="13" rx="2"/><path d="M16 8V3H3v13h5"/></symbol>
    <symbol id="i-arrow" viewBox="0 0 24 24"><path d="M7 17 17 7M7 7h10v10"/></symbol>
    <symbol id="i-trash" viewBox="0 0 24 24"><path d="M3 6h18M9 6V3h6v3M6 6l1 15h10l1-15M10 10v7M14 10v7"/></symbol>
    <symbol id="i-search" viewBox="0 0 24 24"><circle cx="10" cy="10" r="6"/><path d="m15 15 6 6"/></symbol>
    <symbol id="i-check" viewBox="0 0 24 24"><path d="m5 12 4 4L19 6"/></symbol>
    <symbol id="i-download" viewBox="0 0 24 24"><path d="M12 3v12m-5-5 5 5 5-5M4 16v5h16v-5"/></symbol>
    <symbol id="i-bolt" viewBox="0 0 24 24"><path d="M13 2 3 14h9l-1 8 10-12h-9l1-8z"/></symbol>
    <symbol id="i-eye" viewBox="0 0 24 24"><path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z"/><circle cx="12" cy="12" r="3"/></symbol>
    <symbol id="i-file" viewBox="0 0 24 24"><path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/><polyline points="14 2 14 8 20 8"/></symbol>
    <symbol id="i-grid" viewBox="0 0 24 24"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></symbol>
    <symbol id="i-table" viewBox="0 0 24 24"><path d="M12 3v18M3 9h18M3 15h18"/><rect width="18" height="18" x="3" y="3" rx="2"/></symbol>
    <symbol id="i-list-ordered" viewBox="0 0 24 24"><line x1="10" x2="21" y1="6" y2="6"/><line x1="10" x2="21" y1="12" y2="12"/><line x1="10" x2="21" y1="18" y2="18"/><path d="M4 6h1v4"/><path d="M4 10h2"/><path d="M6 18H4c0-1 2-2 2-3s-1-1.5-2-1"/></symbol>
  </defs></svg>

  <!-- Üst Başlık (Header) -->
  <header>
    <a href="#" class="brand">
      <span class="brand-icon"><svg><use href="#i-link"/></svg></span>
      <span>scout kataloğu<span style="font-weight:400;color:#93a18e">.</span></span>
      <span class="brand-badge badge-private">ÖZEL RADAR</span>
    </a>
    <div class="header-right">
      <div class="local" title="Scout Yerel HTTP API Servisi">
        <span class="dot" id="serverDot"></span>
        <span id="serverStatusText">Yerel API aranıyor...</span>
      </div>
      <button class="small quiet" onclick="runDedupCheck()" title="Mükerrer Repo Denetimi ve Temizleme">
        <svg><use href="#i-check"/></svg><span id="dedupBtnLabel">Mükerrer Kontrolü</span>
      </button>
      <button class="small" onclick="openAddModal('single')" title="Modal ile Ekle">
        <svg><use href="#i-plus"/></svg>Yeni Repo Ekle
      </button>
    </div>
  </header>

  <!-- Ana İçerik -->
  <main>
    <div class="intro">
      <div>
        <div class="eyebrow">ÖZEL REPO RADARI · PRIVATE SCOUT & INTELLIGENCE</div>
        <h1>Ajan yeteneklerini tek merkezden keşfet.</h1>
        <p>Metni yapıştır, repolar ayrılsın. Otomatik tara, parmak izini çıkar ve karara bağla.</p>
      </div>
      <div class="counter-group">
        <div class="counter" onclick="setFilter('all')" style="cursor:pointer;" title="Tüm repoları listele"><b id="totalBadge" class="green">0</b> toplam repo</div>
        <div class="counter" onclick="setFilter('transferring')" style="cursor:pointer;" title="Aktarım süreci başlamış repoları filtrele"><b id="transferringBadge" style="color:#7e22ce;">0</b> 🚀 aktarılıyor</div>
        <div class="counter" onclick="setFilter('planned')" style="cursor:pointer;" title="İncelenmiş, aktarım bekleyen adayları filtrele"><b id="plannedBadge" style="color:var(--mint, #059669);">0</b> ✨ aktarım bekliyor</div>
        <div class="counter" onclick="setFilter('transferred')" style="cursor:pointer;" title="Sisteme aktarılmış repoları filtrele"><b id="transferredBadge" style="color:#2563eb;">0</b> ✅ aktarıldı</div>
        <div class="counter" onclick="setFilter('rejected')" style="cursor:pointer;" title="Elenen repoları filtrele"><b id="rejectedBadge" style="color:#64748b;">0</b> 🛡️ elendi</div>
        <div class="counter" onclick="setFilter('pending')" style="cursor:pointer;" title="Henüz incelenmemiş repoları filtrele"><b id="pendingBadge" class="amber">0</b> bekleyen</div>
        <div class="counter" onclick="setFilter('suspended')" style="cursor:pointer;" title="Askıya alınmış repoları filtrele"><b id="suspendedBadge" style="color:#d97706;">0</b> askıda</div>
        <div class="counter" onclick="setFilter('cancel')" style="cursor:pointer;" title="İptal edilmiş repoları filtrele"><b id="cancelBadge" style="color:#dc2626;">0</b> iptal</div>
      </div>
    </div>

    <!-- İki Kolonlu Workspace (Link-Panosu Mimari) -->
    <div class="workspace">
      
      <!-- SOL: Sticky Composer / Hızlı Ekleme Panosu -->
      <section class="composer" aria-labelledby="compose-title">
        <h2 class="section-title" id="compose-title">
          <svg><use href="#i-plus"/></svg>Kataloğa Ekle
        </h2>
        <p class="hint">Tek link, repo listesi veya link içeren serbest metin.</p>

        <div class="input-wrap">
          <textarea id="composerInput" spellcheck="false" placeholder="GitHub linklerini veya 'owner/repo' satırlarını yapıştırın...&#10;&#10;Örnekler:&#10;https://github.com/shadcn-ui/ui&#10;astral-sh/uv&#10;* [React](https://github.com/facebook/react)&#10;repo1 https://github.com/repo2"></textarea>
        </div>

        <div class="form-group">
          <label class="form-label" for="composerLayer">Mimari Katman</label>
          <select id="composerLayer" class="form-select">
            <option value="Belirsiz">🔍 Otomatik Algıla (Belirsiz)</option>
            <option value="Frontend">🎨 Frontend (React / UI / Tasarım)</option>
            <option value="Backend">⚙️ Backend (Java / Spring / Node)</option>
            <option value="Tooling / Agentic">🤖 Tooling / Agentic (Ajan Kuralları / CLI)</option>
          </select>
        </div>

        <label class="toggle">
          <input type="checkbox" id="composerAutoAdd" checked>
          Yapıştırınca otomatik ekle ve sırayla kaydet
        </label>
        <label class="toggle">
          <input type="checkbox" id="composerSkipDuplicates" checked>
          Mükerrerleri Atla (Zaten kayıtlı olanları tekrar ekleme)
        </label>

        <div class="composer-actions">
          <button class="primary" id="composerSubmitBtn" onclick="submitComposerRepos()" disabled>
            <svg><use href="#i-plus"/></svg><span id="composerSubmitLabel">Repoları Ekle</span>
          </button>
          <button class="quiet small" onclick="clearComposerInput()">Temizle</button>
        </div>

        <!-- Canlı Önizleme -->
        <div id="composerPreview" class="preview" hidden>
          <div class="preview-count">
            <svg><use href="#i-check"/></svg><span id="composerPreviewCount"></span>
          </div>
          <ul id="composerPreviewList" class="preview-list"></ul>
        </div>

        <div id="composerStatus" class="status-msg" role="status" aria-live="polite">
          Hazır. Ctrl+V / ⌘V ile yapıştırıp başlayabilirsin.
        </div>

        <div class="composer-note">
          <strong>Biçim Bağımsız Ayrıştırıcı:</strong>
          Satır sonu, boşluk, virgül veya bitişik yapıştırılan tüm GitHub linkleri ve Markdown bağlantıları kusursuz algılanır. Aynı adres ikinci kez eklenmez.
        </div>
      </section>

      <!-- SAĞ: Board / Repolar -->
      <section aria-labelledby="board-title">
        <div class="board-header">
          <h2 id="board-title">
            Repolarım <span id="shownCount" style="font-size:12px;color:var(--muted);font-weight:400"></span>
          </h2>
          <div class="board-toolbar">
            <div class="filter-tabs">
              <button class="tab-btn active" data-filter="all" onclick="setFilter('all')">Hepsi (<b id="tabCountAll">0</b>)</button>
              <button class="tab-btn" data-filter="transferring" onclick="setFilter('transferring')" title="Aktarım süreci başlamış repolar">🚀 Aktarılıyor (<b id="tabCountTransferring">0</b>)</button>
              <button class="tab-btn" data-filter="planned" onclick="setFilter('planned')" title="İncelenmiş, aktarım bekleyen zenginleştirme adayları">✨ Aktarım Bekleyen (<b id="tabCountPlanned">0</b>)</button>
              <button class="tab-btn" data-filter="transferred" onclick="setFilter('transferred')" title="Mevcut skill havuzumuza aktarılmış repolar">✅ Aktarıldı (<b id="tabCountTransferred">0</b>)</button>
              <button class="tab-btn" data-filter="rejected" onclick="setFilter('rejected')" title="Bizim standartlarımız üstün olduğu için elenenler">🛡️ Elendi (<b id="tabCountRejected">0</b>)</button>
              <button class="tab-btn" data-filter="pending" onclick="setFilter('pending')" title="Henüz incelenmemiş repolar">⏳ Bekleyen (<b id="tabCountPending">0</b>)</button>
              <button class="tab-btn" data-filter="suspended" onclick="setFilter('suspended')" title="Askıya alınmış repolar">⏸️ Askıda (<b id="tabCountSuspended">0</b>)</button>
              <button class="tab-btn" data-filter="cancel" onclick="setFilter('cancel')" title="İptal edilmiş repolar">🚫 İptal (<b id="tabCountCancel">0</b>)</button>
            </div>
            <button class="small" id="queueToolbarBtn" onclick="openQueueModal()" title="İnceleme Sırası & Önceliklendirme">
              <svg><use href="#i-list-ordered"/></svg>
              <span>Sıra (<b id="queueCountBadge">0</b>)</span>
            </button>
            <button class="small" id="scoutAllBtn" onclick="scoutAllPending()" title="Tüm Bekleyenleri İncele">
              <svg><use href="#i-bolt"/></svg><span class="btn-label">Tümünü Tara</span>
            </button>
            <button class="small quiet" id="viewToggleBtn" onclick="toggleView()" title="Görünümü Değiştir">
              <svg id="viewIcon"><use href="#i-table"/></svg>
            </button>
            <button class="small" onclick="exportData()" title="JSON Olarak Dışa Aktar">
              <svg><use href="#i-download"/></svg>
            </button>
          </div>
        </div>

        <div class="search-wrap">
          <svg><use href="#i-search"/></svg>
          <input type="search" id="searchInput" class="search" aria-label="Katalogda ara" placeholder="Repo adı, sahip, katman veya karar ara…" oninput="handleSearch()">
        </div>

        <!-- Kart Grid Görünümü -->
        <div class="grid" id="repoGrid"></div>

        <!-- Tablo Görünümü (Gizli Başlar) -->
        <div class="table-container" id="repoTableWrap" style="display:none;">
          <table>
            <thead>
              <tr>
                <th>Repo</th>
                <th>Katman</th>
                <th>Durum</th>
                <th>Karar / Not</th>
                <th style="text-align:right;">İşlemler</th>
              </tr>
            </thead>
            <tbody id="repoTableBody"></tbody>
          </table>
        </div>
      </section>

    </div>
  </main>

  <!-- DOCK: Yüzen İnceleme Sırası Çubuğu (Scout Queue Dock) -->
  <div class="floating-queue-bar" id="floatingQueueBar" style="display:none;">
    <div class="queue-bar-content">
      <div class="queue-bar-left">
        <span class="queue-icon-badge">🎯</span>
        <div>
          <div style="font-size:12.5px; font-weight:700;">
            İnceleme Sırası: <span id="queueBarCount" style="color:var(--mint);">0</span> repo seçildi
          </div>
          <div class="queue-chips" id="queueBarChips"></div>
        </div>
      </div>
      <div class="queue-bar-actions">
        <button class="small" onclick="openQueueModal()" title="Sıralamayı Düzenle">
          <svg><use href="#i-list-ordered"/></svg>Sırayı Düzenle
        </button>
        <button class="small btn-green" id="startQueueBtn" onclick="startQueueScout()">
          <svg><use href="#i-bolt"/></svg>Bu Sırayla İncele
        </button>
        <button class="small quiet" onclick="clearQueue()" title="Kuyruğu Temizle" style="color:#fff;">
          &times;
        </button>
      </div>
    </div>
  </div>

  <!-- MODAL: İnceleme Sırası & Önceliklendirme Modalı -->
  <div class="modal-overlay" id="queueModal" onclick="closeQueueModal(event)">
    <div class="modal" style="max-width:680px;" onclick="event.stopPropagation()">
      <div class="modal-header">
        <h3>🎯 İnceleme Sırası ve Önceliklendirme</h3>
        <button class="quiet icon-btn" onclick="closeQueueModal()">&times;</button>
      </div>
      <div class="modal-body">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px; flex-wrap:wrap; gap:8px;">
          <span style="font-size:12.5px; color:var(--muted);">
            Repoları ▲ ve ▼ butonlarıyla istediğiniz önceliğe göre sıralayın.
          </span>
          <button class="small quiet" onclick="addAllPendingToQueue()">+ Tüm Bekleyenleri Al</button>
        </div>

        <!-- İlerleme Çubuğu -->
        <div class="bulk-progress-wrap" id="queueProgressWrap" style="display:none; margin-bottom:14px;">
          <div style="display:flex; justify-content:space-between; font-size:12px; font-weight:600;">
            <span id="queueProgressStatusText">İnceleniyor...</span>
            <span id="queueProgressPct">0%</span>
          </div>
          <div class="progress-track">
            <div class="progress-bar" id="queueProgressBar"></div>
          </div>
        </div>

        <div class="queue-item-list" id="queueItemList"></div>
      </div>
      <div class="modal-footer" style="justify-content:space-between;">
        <button type="button" class="btn-rose small" onclick="clearQueue()">Kuyruğu Temizle</button>
        <div style="display:flex; gap:8px;">
          <button type="button" class="quiet" onclick="closeQueueModal()">Kapat</button>
          <button type="button" class="btn-green" id="modalStartQueueBtn" onclick="startQueueScout()">
            ⚡ Sıralı İncelemeyi Başlat
          </button>
        </div>
      </div>
    </div>
  </div>

  <!-- MODAL: Gelişmiş Ekleme Modalı (Test Uyumluluğu İçin) -->
  <div class="modal-overlay" id="addRepoModal" onclick="closeAddModal(event)">
    <div class="modal" onclick="event.stopPropagation()">
      <div class="modal-header">
        <h3><svg style="display:inline;vertical-align:-3px;"><use href="#i-plus"/></svg> Yeni Repo Ekle</h3>
        <button class="quiet icon-btn" onclick="closeAddModal()">&times;</button>
      </div>
      <div class="modal-body">
        <div class="add-tabs">
          <button class="add-tab-btn active" id="tabBtnSingle" onclick="switchAddTab('single')">🔗 Tekli Ekle</button>
          <button class="add-tab-btn" id="tabBtnBulk" onclick="switchAddTab('bulk')">📋 Toplu Ekle (Pano)</button>
        </div>

        <!-- 1. Tekli Ekleme -->
        <div id="singleAddContainer">
          <form id="addRepoForm" onsubmit="submitNewRepo(event)">
            <div class="form-group">
              <label class="form-label" for="newRepoUrl">GitHub Repo URL</label>
              <input type="text" id="newRepoUrl" class="form-input" placeholder="https://github.com/owner/repo" required autocomplete="off" oninput="checkSingleRepoDuplicate(this.value)">
              <div id="singleRepoWarning" style="display:none;margin-top:6px;padding:8px 10px;background:rgba(245,158,11,0.12);border:1px solid rgba(245,158,11,0.3);border-radius:6px;font-size:12px;color:var(--amber);"></div>
            </div>
            <div class="form-group">
              <label class="form-label" for="newRepoLayer">Mimari Katman</label>
              <select id="newRepoLayer" class="form-select">
                <option value="Belirsiz">🔍 Otomatik Algıla</option>
                <option value="Frontend">Frontend</option>
                <option value="Backend">Backend</option>
                <option value="Tooling / Agentic">Tooling / Agentic</option>
              </select>
            </div>
            <label class="toggle">
              <input type="checkbox" id="singleCloseOnAdd">
              Eklemeden sonra pencereyi kapat
            </label>
            <div class="modal-footer" style="padding:14px 0 0; background:none;">
              <button type="button" class="quiet" onclick="closeAddModal()">Vazgeç</button>
              <button type="submit" class="primary" id="submitAddBtn">Kaydet</button>
            </div>
          </form>
        </div>

        <!-- 2. Toplu Ekleme -->
        <div id="bulkAddContainer" style="display:none;">
          <div class="form-group">
            <label class="form-label" for="bulkRepoUrls">Toplu Repo Bağlantıları</label>
            <textarea id="bulkRepoUrls" class="form-input" style="height:120px;" placeholder="Her satıra bir link veya yapıştırılan serbest metin..." oninput="refreshBulkPreview()"></textarea>
            <div id="bulkRepoSummaryBar" style="display:none;margin-top:6px;padding:7px 10px;background:var(--card);border:1px solid var(--border);border-radius:6px;font-size:12px;"></div>
          </div>
          <div class="form-group">
            <label class="form-label" for="bulkRepoLayer">Katman</label>
            <select id="bulkRepoLayer" class="form-select">
              <option value="Belirsiz">🔍 Otomatik Algıla</option>
              <option value="Frontend">Frontend</option>
              <option value="Backend">Backend</option>
              <option value="Tooling / Agentic">Tooling / Agentic</option>
            </select>
          </div>
          <label class="toggle" style="margin-top:4px;">
            <input type="checkbox" id="bulkSkipDuplicates" checked>
            Mükerrerleri Atla (Zaten kayıtlı olanları tekrar ekleme)
          </label>
          <div class="bulk-progress-wrap" id="bulkProgressBarWrap">
            <div style="display:flex;justify-content:space-between;font-size:11.5px;font-weight:600;">
              <span id="bulkProgressStatusText">Ekleniyor...</span>
              <span id="bulkProgressPct">0%</span>
            </div>
            <div class="progress-track">
              <div class="progress-bar" id="bulkProgressBar"></div>
            </div>
          </div>
          <div class="bulk-item-list" id="bulkItemList"></div>
          <div class="modal-footer" style="padding:14px 0 0; background:none; margin-top:12px;">
            <button type="button" class="quiet" onclick="pasteFromClipboardToBulk()">Panodan Yapıştır</button>
            <button type="button" class="primary" id="bulkSubmitBtn" onclick="startBulkAdd()">Sırayla Ekle</button>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- MODAL: Aktarımı Başlat Modalı (Phase 1: TRANSFERRING %50) -->
  <div class="modal-overlay" id="startTransferModal" onclick="closeStartTransferModal(event)">
    <div class="modal" onclick="event.stopPropagation()">
      <div class="modal-header">
        <h3 id="startTransferTitle">🚀 Aktarım Sürecini Başlat</h3>
        <button class="quiet icon-btn" onclick="closeStartTransferModal()">&times;</button>
      </div>
      <div class="modal-body">
        <p style="margin-top:0;font-size:13px;color:var(--muted);">
          Bu repodaki kazanımları yerel skill veya kural setimize aktarmak üzere süreci başlatın. Durum <code>TRANSFERRING</code> (%50) olarak güncellenecek ve işlem kaydı açılacaktır.
        </p>
        <div class="form-group">
          <label class="form-label" for="startTargetSkill">Hedef Skill / Alan</label>
          <input type="text" id="startTargetSkill" class="form-input" placeholder="Örn: ui-polish, musgoku, check-security, frontend-design...">
        </div>
        <div class="form-group">
          <label class="form-label" for="startTransferNotes">Başlangıç Notu / Yapılacaklar</label>
          <input type="text" id="startTransferNotes" class="form-input" placeholder="Örn: Skeleton kaset yapısı ve CSS kuralları aktarılacak...">
        </div>
      </div>
      <div class="modal-footer">
        <button type="button" class="quiet" onclick="closeStartTransferModal()">Vazgeç</button>
        <button type="button" class="btn-green" id="confirmStartTransferBtn" onclick="confirmStartTransfer()">🚀 Aktarımı Başlat (%50)</button>
      </div>
    </div>
  </div>

  <!-- MODAL: Aktarımı Tamamla Modalı (Phase 2: TRANSFERRED %100) -->
  <div class="modal-overlay" id="completeTransferModal" onclick="closeCompleteTransferModal(event)">
    <div class="modal" onclick="event.stopPropagation()">
      <div class="modal-header">
        <h3 id="completeTransferTitle">✅ Aktarımı Tamamla & Kapat</h3>
        <button class="quiet icon-btn" onclick="closeCompleteTransferModal()">&times;</button>
      </div>
      <div class="modal-body">
        <p style="margin-top:0;font-size:13px;color:var(--muted);">
          Kod ve kural aktarımı bittiğinde nereye aktarıldığını kaydedin. Durum <code>TRANSFERRED</code> (%100) olarak işaretlenecektir.
        </p>
        <div class="form-group">
          <label class="form-label" for="completeTargetSkill">Hedef Skill</label>
          <input type="text" id="completeTargetSkill" class="form-input" placeholder="Örn: ui-polish">
        </div>
        <div class="form-group">
          <label class="form-label" for="completeTransferredTo">Aktarılan Dosya / Yol (transferred_to)</label>
          <input type="text" id="completeTransferredTo" class="form-input" placeholder="Örn: .agent/skills/ui-polish/SKILL.md">
        </div>
        <div class="form-group">
          <label class="form-label" for="completeTransferNotes">Tamamlama Notu</label>
          <input type="text" id="completeTransferNotes" class="form-input" placeholder="Örn: 16 kilitli tema ve skeleton kasetleri entegre edildi.">
        </div>
      </div>
      <div class="modal-footer">
        <button type="button" class="quiet" onclick="closeCompleteTransferModal()">Vazgeç</button>
        <button type="button" class="btn-green" id="confirmCompleteTransferBtn" onclick="confirmCompleteTransfer()">✅ Aktarımı Tamamla (%100)</button>
      </div>
    </div>
  </div>

  <!-- MODAL: Denetim İzi & İşlem Geçmişi (Audit Trail) Modalı -->
  <div class="modal-overlay" id="historyModal" onclick="closeHistoryModal(event)">
    <div class="modal" style="max-width:680px;" onclick="event.stopPropagation()">
      <div class="modal-header">
        <h3 id="historyModalTitle">📜 İşlem ve Entegrasyon Geçmişi</h3>
        <button class="quiet icon-btn" onclick="closeHistoryModal()">&times;</button>
      </div>
      <div class="modal-body">
        <div id="historyModalList" style="display:flex; flex-direction:column; gap:9px;"></div>
      </div>
      <div class="modal-footer">
        <button type="button" class="primary" onclick="closeHistoryModal()">Kapat</button>
      </div>
    </div>
  </div>

  <!-- MODAL: Entegrasyon Modalı (Geriye Dönük) -->
  <div class="modal-overlay" id="integrateModal" onclick="closeIntegrateModal(event)">
    <div class="modal" onclick="event.stopPropagation()">
      <div class="modal-header">
        <h3>🚀 Sisteme Aktar & Entegre Et</h3>
        <button class="quiet icon-btn" onclick="closeIntegrateModal()">&times;</button>
      </div>
      <div class="modal-body">
        <p style="margin-top:0;font-size:13px;color:var(--muted);">
          Bu repodaki değerli kabiliyetleri yerel kural ve skill setimize aktardığınızı işaretleyin.
        </p>
        <div class="form-group">
          <label class="form-label" for="integrateNotes">Entegrasyon Notu</label>
          <input type="text" id="integrateNotes" class="form-input" placeholder="Örn: Rules altına eklendi, yeni skill üretildi...">
        </div>
      </div>
      <div class="modal-footer">
        <button type="button" class="quiet" onclick="closeIntegrateModal()">Vazgeç</button>
        <button type="button" class="btn-green" id="confirmIntegrateBtn" onclick="confirmIntegrate()">Aktarıldı Olarak İşaretle</button>
      </div>
    </div>
  </div>

  <!-- MODAL: Plan Görüntüleyici -->
  <div class="modal-overlay" id="planModal" onclick="closePlanModal(event)">
    <div class="modal" style="max-width:760px;" onclick="event.stopPropagation()">
      <div class="modal-header">
        <h3 id="planModalTitle">İnceleme Planı</h3>
        <button class="quiet icon-btn" onclick="closePlanModal()">&times;</button>
      </div>
      <div class="modal-body markdown-body" id="planModalContent"></div>
      <div class="modal-footer">
        <button type="button" class="quiet" onclick="copyPlanContent()">Metni Kopyala</button>
        <button type="button" class="primary" onclick="closePlanModal()">Kapat</button>
      </div>
    </div>
  </div>

  <!-- Toast Mesajı -->
  <div id="toast" role="status" aria-live="polite"></div>

  <!-- JavaScript Mantık Çekirdeği -->
  <script>
    'use strict';

    let reposData = __REPOS_JSON__;
    let currentFilter = 'all';
    let currentView = 'grid';
    let isServerOnline = false;
    let activeModalPlan = '';
    let activeIntegrateUrl = '';
    let toastTimer = null;
    let detectedComposerRepos = [];
    let detectedBulkRepos = [];
    let isBulkRunning = false;
    let scoutQueue = [];
    let isQueueRunning = false;

    const API_BASE = window.location.protocol.startsWith('http') ? '' : 'http://localhost:5055';

    function $(id) { return document.getElementById(id); }

    function icon(name) {
      const el = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
      const use = document.createElementNS(el.namespaceURI, 'use');
      use.setAttribute('href', '#i-' + name);
      el.append(use);
      el.setAttribute('aria-hidden', 'true');
      return el;
    }

    function showToast(message, type = 'info', duration = 3200) {
      const toast = $('toast');
      toast.innerHTML = message;
      toast.classList.add('show');
      clearTimeout(toastTimer);
      toastTimer = setTimeout(() => toast.classList.remove('show'), duration);
    }

    async function copyText(text) {
      try {
        if (!navigator.clipboard?.writeText) throw new Error('fallback');
        await navigator.clipboard.writeText(text);
        showToast('📋 Adres panoya kopyalandı.');
      } catch {
        const area = document.createElement('textarea');
        area.value = text;
        area.style.cssText = 'position:fixed;opacity:0';
        document.body.append(area);
        area.select();
        let ok = false;
        try { ok = document.execCommand('copy'); } catch {}
        area.remove();
        showToast(ok ? '📋 Adres panoya kopyalandı.' : 'Kopyalama engellendi.');
      }
    }

    function copyRepoCmd(url) {
      const cmd = `scout ${url}`;
      copyText(cmd);
      showToast(`📋 Komut kopyalandı: <code>${cmd}</code>`);
    }

    /* Link-Panosu Pano Ayrıştırma ve Normalizasyon Motoru */
    function trimEnd(raw) {
      let s = raw.replace(/[\\u200B-\\u200D\\uFEFF]/g, '');
      let prev;
      do {
        prev = s;
        s = s.replace(/[.,;:!?…]+$/u, '');
        for (const [open, close] of [['(', ')'], ['[', ']'], ['{', '}']]) {
          while (s.endsWith(close) && s.split(close).length > s.split(open).length) {
            s = s.slice(0, -1);
          }
        }
      } while (s !== prev);
      return s;
    }

    function extractGithubRepos(rawText = '', html = '') {
      const found = new Map();
      const add = (o, n) => {
        if (!o || !n) return;
        n = n.replace(/\\.git$/i, '').replace(/[/?#].*$/, '').trim();
        const reserved = ['settings', 'explore', 'topics', 'trending', 'collections', 'features', 'pricing', 'security', 'enterprise', 'customer-stories', 'readme'];
        if (reserved.includes(o.toLowerCase()) || reserved.includes(n.toLowerCase())) return;
        const url = `https://github.com/${o}/${n}`;
        const k = url.toLowerCase();
        if (!found.has(k)) {
          found.set(k, { url, owner: o, name: n });
        }
      };

      let scan = (rawText || '').slice(0, 500000);

      // Markdown bağlantılarını önce çöz: [Title](https://github.com/owner/repo)
      scan = scan.replace(/\\[([^\\]\\n]*)\\]\\((<?(?:https?:\\/\\/|www\\.)[^\\s]*?)(?:\\s+"[^"]*")?\\)(?=\\s|$|[.,;!?])/gi, (all, label, target) => {
        const cleanTarget = target.replace(/^<|>$/g, '');
        const m = cleanTarget.match(/(?:https?:\\/\\/)?(?:www\\.)?github\\.com\\/([a-zA-Z0-9._-]+)\\/([a-zA-Z0-9._-]+)/i);
        if (m) add(m[1], m[2]);
        return ' ';
      });

      // HTML kaynağı yapıştırılmışsa DOMParser ile ayrıştır
      if (/<a\\b[^>]*href\\s*=/i.test(scan) && !html) {
        html = scan;
        scan = new DOMParser().parseFromString(scan, 'text/html').body.textContent || '';
      }

      // Bitişik URL'leri ve açık HTTP linklerini tanı
      const NL = String.fromCharCode(10);
      scan = scan
        .replace(/(https?:\\/\\/|git@github\\.com:)/gi, (m) => NL + m)
        .replace(/[,;\\s]+/g, NL);

      const lines = scan.split(/[\\r\\n]+/);
      const regex = /(?:https?:\\/\\/)?(?:www\\.)?github\\.com\\/([a-zA-Z0-9._-]+)\\/([a-zA-Z0-9._-]+)|git@github\\.com:([a-zA-Z0-9._-]+)\\/([a-zA-Z0-9._-]+)/gi;

      for (let line of lines) {
        line = trimEnd(line.trim());
        if (!line) continue;
        let foundMatch = false;
        let m;
        regex.lastIndex = 0;
        while ((m = regex.exec(line)) !== null) {
          add(m[1] || m[3], m[2] || m[4]);
          foundMatch = true;
        }
        if (!foundMatch) {
          const shortMatch = line.match(/^([a-zA-Z0-9._-]+)\\/([a-zA-Z0-9._-]+)$/);
          if (shortMatch) add(shortMatch[1], shortMatch[2]);
        }
      }

      if (html) {
        try {
          const doc = new DOMParser().parseFromString(html, 'text/html');
          for (const a of doc.querySelectorAll('a[href]')) {
            const href = a.getAttribute('href') || '';
            const m = href.match(/github\\.com\\/([a-zA-Z0-9._-]+)\\/([a-zA-Z0-9._-]+)/i);
            if (m) add(m[1], m[2]);
          }
        } catch {}
      }

      return [...found.values()];
    }


    /* Mükerrer Repo Ayrıştırma & Tekilleştirme Araçları */
    function canonicalRepoKey(urlOrOwner, name) {
      if (name !== undefined && name !== null) {
        return `${String(urlOrOwner).trim().toLowerCase()}/${String(name).trim().replace(/\.git$/i, "").toLowerCase()}`;
      }
      const raw = String(urlOrOwner || "").trim();
      const m = raw.match(/(?:https?:\/\/)?(?:www\.)?github\.com\/([a-zA-Z0-9._-]+)\/([a-zA-Z0-9._-]+)|git@github\.com:([a-zA-Z0-9._-]+)\/([a-zA-Z0-9._-]+)|^([a-zA-Z0-9._-]+)\/([a-zA-Z0-9._-]+)$/i);
      if (m) {
        const o = m[1] || m[3] || m[5];
        const n = (m[2] || m[4] || m[6]).replace(/\.git$/i, "");
        return `${o.toLowerCase()}/${n.toLowerCase()}`;
      }
      return raw.toLowerCase().replace(/\.git$/i, "").replace(/\/$/, "");
    }

    function findExistingRepoInCatalog(urlOrKey) {
      const target = canonicalRepoKey(urlOrKey);
      return reposData.find(r => canonicalRepoKey(r.url) === target || canonicalRepoKey(r.owner, r.name) === target);
    }

    function isRepoExisting(urlOrKey) {
      return !!findExistingRepoInCatalog(urlOrKey);
    }

    function checkSingleRepoDuplicate(url) {
      const warnBox = $('singleRepoWarning');
      const submitBtn = $('submitAddBtn');
      if (!warnBox) return;
      if (!url || !url.trim()) {
        warnBox.style.display = 'none';
        warnBox.innerText = '';
        if (submitBtn) submitBtn.innerText = 'Kaydet';
        return;
      }
      const existing = findExistingRepoInCatalog(url);
      if (existing) {
        warnBox.style.display = 'block';
        const lastHist = (existing.history && existing.history.length > 0) ? existing.history[existing.history.length - 1] : null;
        const histInfo = lastHist ? `<div style="margin-top:4px;font-size:11px;opacity:0.9;"><strong>Son İşlem:</strong> ${lastHist.action} &middot; ${lastHist.date || ''} (${lastHist.note || 'Not yok'})</div>` : '';
        const targetInfo = existing.target_skill ? `<div style="font-size:11px;opacity:0.9;"><strong>Hedef Skill:</strong> <code>${existing.target_skill}</code> ${existing.transferred_to ? `&rarr; <code>${existing.transferred_to}</code>` : ''}</div>` : '';
        const progressInfo = (existing.progress !== undefined) ? `<span style="display:inline-block;padding:1px 6px;border-radius:4px;background:rgba(0,0,0,0.08);font-weight:700;">%${existing.progress}</span>` : '';

        warnBox.innerHTML = `
          <div style="font-weight:700;margin-bottom:3px;display:flex;align-items:center;justify-content:space-between;">
            <span>⚠️ Bu repo zaten kayıtlı! (#${existing.id} ${existing.owner}/${existing.name})</span>
            ${progressInfo}
          </div>
          <div style="font-size:11.5px;line-height:1.45;">
            <div><strong>Durum:</strong> <code>${existing.status}</code> &nbsp;&middot;&nbsp; <strong>Karar:</strong> <code>${existing.verdict || "-"}</code></div>
            ${targetInfo}
            ${histInfo}
          </div>
        `;
        if (submitBtn) submitBtn.innerText = '⚠️ Zaten Kayıtlı (Yine de Güncelle)';
      } else {
        warnBox.style.display = 'none';
        warnBox.innerText = '';
        if (submitBtn) submitBtn.innerText = 'Kaydet';
      }
    }

    function refreshBulkPreview() {
      const text = $('bulkRepoUrls')?.value || '';
      const summaryBar = $('bulkRepoSummaryBar');
      const list = $('bulkItemList');
      const repos = extractGithubRepos(text);

      if (!summaryBar || !list) return;

      if (repos.length === 0) {
        summaryBar.style.display = 'none';
        list.replaceChildren();
        return;
      }

      const newRepos = repos.filter(r => !isRepoExisting(r.url));
      const dupeRepos = repos.filter(r => isRepoExisting(r.url));

      summaryBar.style.display = 'block';
      summaryBar.innerHTML = `📋 <strong>${repos.length}</strong> repo tespit edildi &nbsp;·&nbsp; <span style="color:var(--green);font-weight:600;">🟢 ${newRepos.length} yeni</span> &nbsp;·&nbsp; <span style="color:var(--amber, #f59e0b);font-weight:600;">🟡 ${dupeRepos.length} mükerrer (kayıtlı)</span>`;

      list.replaceChildren();
      repos.forEach((r, idx) => {
        const div = document.createElement('div');
        div.className = 'bulk-item-row';
        div.id = `bulkRow_${idx}`;
        const isDupe = isRepoExisting(r.url);
        div.innerHTML = `<span>${idx + 1}. <strong>${r.owner}</strong>/${r.name}</span><span id="bulkBadge_${idx}" style="font-size:11px;font-weight:600;color:${isDupe ? 'var(--amber, #f59e0b)' : 'var(--green)'}">${isDupe ? '🟡 Mükerrer (Kayıtlı)' : '🟢 Yeni'}</span>`;
        list.append(div);
      });
    }

    async function runDedupCheck() {
      const btn = $('dedupBtnLabel');
      if (btn) btn.innerText = 'Taranıyor...';

      if (isServerOnline) {
        try {
          const res = await fetch(`${API_BASE}/api/repos/dedup`, { method: 'POST' });
          const data = await res.json();
          if (res.ok && data.success) {
            const report = data.report || {};
            if (report.duplicates_removed > 0) {
              reposData = data.repos;
              updateStats();
              render();
              showToast(`🧹 ${report.duplicates_removed} adet mükerrer repo temizlendi! Kalan: ${report.final_count}`, 'success');
            } else {
              showToast(`✅ Mükerrer repo bulunamadı. Toplam ${report.final_count || reposData.length} kayıt tekil.`, 'info');
            }
            if (btn) btn.innerText = 'Mükerrer Kontrolü';
            return;
          }
        } catch {}
      }

      const seen = new Map();
      const dupes = [];
      reposData.forEach(r => {
        const k = canonicalRepoKey(r.url);
        if (seen.has(k)) {
          dupes.push({ current: r, original: seen.get(k) });
        } else {
          seen.set(k, r);
        }
      });

      if (dupes.length > 0) {
        showToast(`⚠️ ${dupes.length} mükerrer repo tespit edildi. Sunucu açıkken tek tıkla temizlenebilir.`, 'warning');
      } else {
        showToast(`✅ Mükerrer repo bulunamadı. Tüm ${reposData.length} kayıt tekil.`, 'info');
      }
      if (btn) btn.innerText = 'Mükerrer Kontrolü';
    }

    /* Sol Kolon: Composer Olayları */
    function refreshComposerPreview() {
      const inputVal = $('composerInput').value;
      detectedComposerRepos = extractGithubRepos(inputVal);

      const newRepos = detectedComposerRepos.filter(r => !isRepoExisting(r.url));

      const submitBtn = $('composerSubmitBtn');
      const submitLabel = $('composerSubmitLabel');
      const previewBox = $('composerPreview');
      const previewCount = $('composerPreviewCount');
      const previewList = $('composerPreviewList');
      const statusBox = $('composerStatus');

      if (detectedComposerRepos.length > 0) {
        previewBox.hidden = false;
        previewCount.textContent = `${detectedComposerRepos.length} repo tespit edildi · ${newRepos.length} yeni`;
        previewList.replaceChildren();

        detectedComposerRepos.slice(0, 15).forEach(r => {
          const li = document.createElement('li');
          const isExist = isRepoExisting(r.url);
          li.innerHTML = `<strong>${r.owner}</strong>/${r.name} ${isExist ? '<span style="color:var(--muted);font-size:10.5px;">(kayıtlı)</span>' : '<span style="color:var(--green);font-weight:600;font-size:10.5px;">(yeni)</span>'}`;
          previewList.append(li);
        });
        if (detectedComposerRepos.length > 15) {
          const li = document.createElement('li');
          li.textContent = `ve ${detectedComposerRepos.length - 15} repo daha…`;
          previewList.append(li);
        }

        submitBtn.disabled = !isServerOnline || detectedComposerRepos.length === 0;
        submitLabel.textContent = `Repoları Ekle (${detectedComposerRepos.length})`;
      } else {
        previewBox.hidden = true;
        submitBtn.disabled = true;
        submitLabel.textContent = 'Repoları Ekle';
      }
    }

    async function submitComposerRepos() {
      if (detectedComposerRepos.length === 0) return;
      if (!isServerOnline) {
        showToast('⚠️ Yerel sunucu aktif değil. Terminalde python scout/server.py çalıştırın.', 'error');
        return;
      }

      const layer = $('composerLayer').value;
      const statusBox = $('composerStatus');
      const btn = $('composerSubmitBtn');
      const skipDuplicates = $('composerSkipDuplicates')?.checked ?? true;

      const targetRepos = skipDuplicates ? detectedComposerRepos.filter(r => !isRepoExisting(r.url)) : detectedComposerRepos;

      if (targetRepos.length === 0) {
        showToast(`ℹ️ Tespit edilen tüm repolar (${detectedComposerRepos.length}) zaten kayıtlı (mükerrer).`, 'info');
        statusBox.className = 'status-msg';
        statusBox.innerText = 'Tüm repolar zaten kayıtlıydı (mükerrer atlandı).';
        return;
      }

      btn.disabled = true;
      btn.innerText = '⏳ Kaydediliyor...';
      statusBox.className = 'status-msg info';
      statusBox.innerText = `${targetRepos.length} repo sunucuya aktarılıyor...`;

      let added = 0;
      let updated = 0;
      let errors = 0;

      for (let i = 0; i < targetRepos.length; i++) {
        const repo = targetRepos[i];
        const isLast = (i === targetRepos.length - 1);
        try {
          const res = await fetch(`${API_BASE}/api/repos`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              url: repo.url,
              layer: layer,
              skip_build: !isLast
            })
          });
          const data = await res.json();
          if (res.ok && data.success) {
            if (data.is_update) updated++; else added++;
            if (data.repos) reposData = data.repos;
          } else {
            errors++;
          }
        } catch {
          errors++;
        }
      }

      updateStats();
      render();

      const msg = `✅ ${added} repo eklendi, ${updated} güncellendi${errors ? `, ${errors} hata` : ''}.`;
      statusBox.className = errors ? 'status-msg error' : 'status-msg';
      statusBox.innerText = msg;
      showToast(msg, 'success');

      $('composerInput').value = '';
      refreshComposerPreview();
      btn.disabled = false;
      btn.innerHTML = '<svg><use href="#i-plus"/></svg><span id="composerSubmitLabel">Repoları Ekle</span>';
    }

    function clearComposerInput() {
      $('composerInput').value = '';
      refreshComposerPreview();
      $('composerStatus').className = 'status-msg';
      $('composerStatus').innerText = 'Giriş alanı temizlendi.';
      $('composerInput').focus();
    }

    /* Pano / Yapıştırma Olayı */
    $('composerInput').addEventListener('paste', (e) => {
      if (!e.clipboardData) return;
      const text = e.clipboardData.getData('text/plain') || '';
      const html = e.clipboardData.getData('text/html') || '';
      
      e.preventDefault();
      const repos = extractGithubRepos(text, html);
      const cleanUrls = repos.map(r => r.url).join(String.fromCharCode(10));
      const cur = $('composerInput').value.trim();
      $('composerInput').value = cur ? (cur + String.fromCharCode(10) + cleanUrls) : (cleanUrls || text);

      refreshComposerPreview();

      if ($('composerAutoAdd').checked && repos.length > 0) {
        submitComposerRepos();
      }
    });

    $('composerInput').addEventListener('input', refreshComposerPreview);

    /* Modal İşlemleri */
    function openAddModal(tab = 'single') {
      $('addRepoModal').classList.add('active');
      switchAddTab(tab);
    }
    function closeAddModal(e) {
      if (isBulkRunning) return;
      $('addRepoModal').classList.remove('active');
    }
    function switchAddTab(tab) {
      if (tab === 'bulk') {
        $('singleAddContainer').style.display = 'none';
        $('bulkAddContainer').style.display = 'block';
        $('tabBtnSingle').classList.remove('active');
        $('tabBtnBulk').classList.add('active');
      } else {
        $('singleAddContainer').style.display = 'block';
        $('bulkAddContainer').style.display = 'none';
        $('tabBtnSingle').classList.add('active');
        $('tabBtnBulk').classList.remove('active');
      }
    }

    async function submitNewRepo(e) {
      e.preventDefault();
      const urlInput = $('newRepoUrl');
      const url = urlInput.value.trim();
      const layer = $('newRepoLayer').value;
      const closeOnAdd = $('singleCloseOnAdd').checked;
      if (!url) return;

      const submitBtn = $('submitAddBtn');
      submitBtn.disabled = true;

      try {
        const res = await fetch(`${API_BASE}/api/repos`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ url, layer })
        });
        const data = await res.json();
        if (res.ok && data.success) {
          reposData = data.repos;
          updateStats();
          render();
          showToast(`✅ ${url} başarıyla eklendi!`, 'success');
          urlInput.value = '';
          if (closeOnAdd) closeAddModal();
        } else {
          showToast(`❌ Hata: ${data.error || 'Eklenemedi'}`, 'error');
        }
      } catch (err) {
        showToast(`❌ Sunucu hatası: ${err.message}`, 'error');
      } finally {
        submitBtn.disabled = false;
      }
    }

    async function pasteFromClipboardToBulk() {
      try {
        const text = await navigator.clipboard.readText();
        $('bulkRepoUrls').value = text;
        refreshBulkPreview();
        const repos = extractGithubRepos(text);
        showToast(`📋 ${repos.length} repo algılandı.`, 'info');
      } catch {
        showToast('Panoya erişilemedi. Lütfen Ctrl+V ile yapıştırın.', 'error');
      }
    }

    async function startBulkAdd() {
      const text = $('bulkRepoUrls').value;
      const repos = extractGithubRepos(text);
      if (repos.length === 0) {
        showToast('⚠️ Geçerli bir repo bulunamadı.', 'info');
        return;
      }

      isBulkRunning = true;
      const wrap = $('bulkProgressBarWrap');
      const bar = $('bulkProgressBar');
      const pct = $('bulkProgressPct');
      const statusText = $('bulkProgressStatusText');
      const list = $('bulkItemList');
      const layer = $('bulkRepoLayer').value;

      wrap.style.display = 'block';
      list.replaceChildren();

      repos.forEach((r, idx) => {
        const div = document.createElement('div');
        div.className = 'bulk-item-row';
        div.id = `bulkRow_${idx}`;
        div.innerHTML = `<span>${idx + 1}. <strong>${r.owner}</strong>/${r.name}</span><span id="bulkBadge_${idx}">⏳ Sırada</span>`;
        list.append(div);
      });

      const skipDupes = $('bulkSkipDuplicates')?.checked ?? true;
      let added = 0;
      let updated = 0;
      let skippedCount = 0;

      for (let i = 0; i < repos.length; i++) {
        const r = repos[i];
        const isLast = (i === repos.length - 1);
        const p = Math.round(((i + 1) / repos.length) * 100);
        bar.style.width = p + '%';
        pct.innerText = p + '%';
        statusText.innerText = `İşleniyor (${i + 1}/${repos.length}): ${r.owner}/${r.name}`;

        const badge = $(`bulkBadge_${i}`);
        const isDupe = isRepoExisting(r.url);

        if (isDupe && skipDupes) {
          if (badge) {
            badge.innerText = '⏭️ Atlandı (Mükerrer)';
            badge.style.color = 'var(--amber, #f59e0b)';
          }
          skippedCount++;
          continue;
        }

        if (badge) badge.innerText = '🔄 Ekleniyor...';

        try {
          const res = await fetch(`${API_BASE}/api/repos`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url: r.url, layer, skip_build: !isLast })
          });
          const data = await res.json();
          if (badge) {
            badge.innerText = data.is_update ? 'ℹ️ Güncellendi' : '✅ Eklendi';
            badge.style.color = 'var(--green)';
          }
          if (data.repos) reposData = data.repos;
        } catch {
          if (badge) {
            badge.innerText = '❌ Hata';
            badge.style.color = 'var(--rose)';
          }
        }
      }

      isBulkRunning = false;
      statusText.innerText = '✅ Toplu ekleme tamamlandı!';
      updateStats();
      render();
      showToast('✅ Toplu repolar kataloğa işlendi.', 'success');
    }

    /* Kart & Tablo Render */
    function setFilter(filter) {
      currentFilter = filter;
      document.querySelectorAll('.filter-tabs .tab-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.filter === filter);
      });
      render();
    }

    function toggleView() {
      currentView = currentView === 'grid' ? 'table' : 'grid';
      const iconUse = $('viewIcon').querySelector('use');
      if (currentView === 'grid') {
        iconUse.setAttribute('href', '#i-table');
        $('repoGrid').style.display = 'grid';
        $('repoTableWrap').style.display = 'none';
      } else {
        iconUse.setAttribute('href', '#i-grid');
        $('repoGrid').style.display = 'none';
        $('repoTableWrap').style.display = 'block';
      }
      render();
    }

    function handleSearch() {
      render();
    }

    function getFilteredRepos() {
      const q = ($('searchInput')?.value || '').trim().toLowerCase();
      return reposData.filter(r => {
        const v = (r.verdict || '').toUpperCase();
        const st = (r.status || 'PENDING').toUpperCase();
        const isSuspended = st === 'SUSPENDED';
        const isCancel = ['CANCEL', 'CANCELED', 'CANCELLED'].includes(st);
        const isTransferring = st === 'TRANSFERRING';
        const isTransferred = st === 'TRANSFERRED' || (!isSuspended && !isCancel && v.includes('AKTARILDI'));
        const isBetter = st === 'REJECTED' || (!isSuspended && !isCancel && (v.includes('DAHA_IYIYIZ') || v.includes('DAHA IYIYIZ')));
        const isCandidate = v.includes('ZENGINLESTIR') || v.includes('KISMEN_ALINABILIR') || v.includes('KABUL');
        const isPlanned = st === 'PLANNED' || (st === 'DONE' && isCandidate && !isTransferred);

        if (currentFilter === 'pending' && st !== 'PENDING' && st !== 'ANALYZED') return false;
        if (currentFilter === 'transferring' && !isTransferring) return false;
        if ((currentFilter === 'planned' || currentFilter === 'to_integrate') && !isPlanned) return false;
        if (currentFilter === 'transferred' && !isTransferred) return false;
        if ((currentFilter === 'rejected' || currentFilter === 'better') && !isBetter) return false;
        if (currentFilter === 'suspended' && !isSuspended) return false;
        if (currentFilter === 'cancel' && !isCancel) return false;
        if (currentFilter === 'done' && st !== 'DONE' && !isTransferred && !isBetter && !isPlanned) return false;

        if (q) {
          const s = r.summary || {};
          const histText = (r.history || []).map(h => `${h.action || ''} ${h.note || ''} ${h.target_skill || ''}`).join(' ');
          const str = `${r.name} ${r.owner} ${r.layer} ${r.status} ${r.verdict} ${r.target_skill || ''} ${r.transferred_to || ''} ${r.url} ${s.core_value || ''} ${s.delta_to_us || ''} ${s.action_plan || ''} ${s.tech_stack || ''} ${histText}`.toLowerCase();
          return str.includes(q);
        }
        return true;
      });
    }

    function render() {
      const filtered = getFilteredRepos();
      $('shownCount').textContent = `(${filtered.length} repo)`;

      // 1. Grid Render
      const grid = $('repoGrid');
      grid.replaceChildren();

      if (filtered.length === 0) {
        const empty = document.createElement('div');
        empty.className = 'empty';
        empty.innerHTML = `
          <div>
            <div class="empty-mark"><svg style="width:26px;height:26px;"><use href="#i-search"/></svg></div>
            <h3>Eşleşen repo bulunamadı</h3>
            <p>Farklı bir arama yapabilir veya soldaki panelden yeni bir repo ekleyebilirsiniz.</p>
          </div>`;
        grid.append(empty);
      } else {
        filtered.forEach(r => {
          const card = document.createElement('article');
          card.className = 'card';

          const initial = (r.name || r.owner || 'G')[0].toUpperCase();
          const st = (r.status || 'PENDING').toUpperCase();
          const isSuspended = st === 'SUSPENDED';
          const isCancel = ['CANCEL', 'CANCELED', 'CANCELLED'].includes(st);
          const isTransferring = st === 'TRANSFERRING';
          const v = (r.verdict || '').toUpperCase();
          const isTransferred = st === 'TRANSFERRED' || (!isSuspended && !isCancel && v.includes('AKTARILDI'));
          const isBetter = st === 'REJECTED' || (!isSuspended && !isCancel && (v.includes('DAHA_IYIYIZ') || v.includes('DAHA IYIYIZ')));
          const isEnrich = !isSuspended && !isCancel && (v.includes('ZENGINLESTIR') || v.includes('KABUL'));
          const isPartial = !isSuspended && !isCancel && (v.includes('KISMEN_ALINABILIR') || v.includes('KISMEN'));
          const isPlanned = st === 'PLANNED' || (st === 'DONE' && (isEnrich || isPartial) && !isTransferred);

          const qIdx = scoutQueue.findIndex(q => q.url.toLowerCase() === r.url.toLowerCase());
          const isQueued = qIdx !== -1;

          // İlerleme yüzdesi
          let pct = (r.progress !== undefined && r.progress !== null) ? Number(r.progress) : 0;
          if (pct === 0) {
            if (isTransferred) pct = 100;
            else if (isTransferring) pct = 50;
            else if (isPlanned) pct = 25;
          }
          let barColorClass = 'bar-planned';
          if (isTransferring) barColorClass = 'bar-transferring';
          else if (isTransferred) barColorClass = 'bar-transferred';
          else if (isBetter) barColorClass = 'bar-rejected';

          // Durum Rozeti
          let stateBadge = '';
          if (isSuspended) {
            stateBadge = '<span class="badge badge-suspended">⏸️ Askıda</span>';
          } else if (isCancel) {
            stateBadge = '<span class="badge badge-cancel">🚫 İptal</span>';
          } else if (isTransferring) {
            stateBadge = '<span class="badge badge-transferring">🚀 Aktarılıyor</span>';
          } else if (isTransferred) {
            stateBadge = '<span class="badge badge-transferred">✅ Sisteme Aktarıldı</span>';
          } else if (isPlanned) {
            if (isPartial) stateBadge = '<span class="badge badge-partial">🧩 Aktarım Bekliyor (Kısmen)</span>';
            else stateBadge = '<span class="badge badge-planned">✨ Aktarım Bekliyor</span>';
          } else if (isBetter) {
            stateBadge = '<span class="badge badge-rejected">🛡️ Elendi (Biz Daha İyiyiz)</span>';
          } else if (st === 'PENDING') {
            stateBadge = '<span class="badge badge-pending">⏳ İnceleme Bekliyor</span>';
          } else {
            stateBadge = '<span class="badge badge-done">İncelendi</span>';
          }

          // Karar Kutusu
          let verdictBoxClass = 'verdict-better';
          let verdictIcon = '🛡️';
          let verdictTitle = 'İnceleme Tamamlandı';
          if (isSuspended) {
            verdictBoxClass = 'verdict-suspended';
            verdictIcon = '⏸️';
            verdictTitle = 'Askıya Alındı';
          } else if (isCancel) {
            verdictBoxClass = 'verdict-cancel';
            verdictIcon = '🚫';
            verdictTitle = 'İptal Edildi';
          } else if (isTransferring) {
            verdictBoxClass = 'verdict-transferred';
            verdictIcon = '🚀';
            verdictTitle = 'Aktarım Süreci Devam Ediyor';
          } else if (isTransferred) {
            verdictBoxClass = 'verdict-transferred';
            verdictIcon = '✅';
            verdictTitle = 'Sisteme Aktarıldı';
          } else if (isPlanned && isEnrich) {
            verdictBoxClass = 'verdict-to-integrate';
            verdictIcon = '💎';
            verdictTitle = 'Zenginleştirme Kararı (Aktarım Bekliyor)';
          } else if (isPlanned && isPartial) {
            verdictBoxClass = 'verdict-partial';
            verdictIcon = '🧩';
            verdictTitle = 'Kısmen Alınabilir (Aktarım Bekliyor)';
          } else if (isBetter) {
            verdictBoxClass = 'verdict-better';
            verdictIcon = '🛡️';
            verdictTitle = 'Biz Daha İyiyiz (Elendi)';
          } else if (st === 'PENDING') {
            verdictBoxClass = '';
            verdictIcon = '⏳';
            verdictTitle = 'Henüz İncelenmedi';
          }

          const rawVerdict = r.verdict && r.verdict !== '-' ? r.verdict : '';
          const verdictDetail = rawVerdict.includes(':') ? rawVerdict.split(':').slice(1).join(':').trim() : rawVerdict;

          const s = r.summary || {};
          const hasSummary = Boolean(s.core_value || s.delta_to_us || s.action_plan);

          if (isTransferring) {
            card.classList.add('card-transferring');
          } else if (isPlanned) {
            card.classList.add('card-to-integrate');
          } else if (isTransferred) {
            card.classList.add('card-transferred');
          }
          if (isSuspended) {
            card.classList.add('card-suspended');
          }
          if (isCancel) {
            card.classList.add('card-cancel');
          }

          // Son audit trail
          const historyArr = r.history || [];
          const lastHist = historyArr.length > 0 ? historyArr[historyArr.length - 1] : null;

          card.innerHTML = `
            <div>
              <div class="card-top">
                <div class="favicon">${initial}</div>
                <div class="card-meta">
                  <span class="domain">${r.owner}</span>
                  <h3><a href="${r.url}" target="_blank" rel="noopener noreferrer">${r.name}</a></h3>
                </div>
                <button class="icon-btn delete" onclick="deleteRepo('${r.id}')" title="Repoyu Sil">
                  <svg><use href="#i-trash"/></svg>
                </button>
              </div>

              <div class="badge-group">
                <span class="badge badge-layer">${r.layer}</span>
                ${stateBadge}
                <div class="status-select-wrap">
                  <select class="status-select sel-${st.toLowerCase()}" onchange="changeRepoStatus('${r.id}', this.value)" title="Durumu Değiştir">
                    <option value="PENDING" ${st === 'PENDING' ? 'selected' : ''}>⏳ Beklemede</option>
                    <option value="PLANNED" ${st === 'PLANNED' ? 'selected' : ''}>✨ Aktarım Bekliyor</option>
                    <option value="TRANSFERRING" ${st === 'TRANSFERRING' ? 'selected' : ''}>🚀 Aktarılıyor</option>
                    <option value="TRANSFERRED" ${st === 'TRANSFERRED' ? 'selected' : ''}>✅ Aktarıldı</option>
                    <option value="REJECTED" ${st === 'REJECTED' ? 'selected' : ''}>🛡️ Elendi</option>
                    <option value="SUSPENDED" ${st === 'SUSPENDED' ? 'selected' : ''}>⏸️ Askıda</option>
                    <option value="CANCEL" ${['CANCEL', 'CANCELED', 'CANCELLED'].includes(st) ? 'selected' : ''}>🚫 İptal</option>
                  </select>
                </div>
                ${(st === 'PENDING') ? (isQueued 
                  ? `<button type="button" class="badge badge-queued" onclick="toggleQueueRepo('${r.url}')" title="Sıradan Çıkar">🎯 #${qIdx + 1} Sırada &times;</button>`
                  : `<button type="button" class="badge badge-queue-add" onclick="toggleQueueRepo('${r.url}')" title="İnceleme Sırasına Al">+ Sırala</button>`) : ''}
                ${s.tech_stack ? `<span class="badge badge-tech" title="${s.tech_stack}">⚙️ ${s.tech_stack.split(',')[0].slice(0, 30)}</span>` : ''}
                ${r.target_skill ? `<span class="badge badge-layer" style="background:#f5f3ff; color:#6d28d9;" title="Hedef Skill">🎯 ${r.target_skill}</span>` : ''}
              </div>

              <!-- İlerleme Çubuğu -->
              <div class="repo-progress-container" title="İlerleme Oranı: %${pct}">
                <div class="repo-progress-track">
                  <div class="repo-progress-bar ${barColorClass}" style="width: ${pct}%;"></div>
                </div>
                <span class="repo-progress-pct">%${pct}</span>
              </div>

              ${rawVerdict ? `
              <div class="verdict-box ${verdictBoxClass}">
                <div class="verdict-box-title">
                  <span>${verdictIcon}</span>
                  <span>${verdictTitle}</span>
                </div>
                <div class="verdict-box-detail">${verdictDetail}</div>
              </div>` : ''}

              ${hasSummary ? `
              <div class="card-summary-section">
                ${s.core_value ? `
                <div class="summary-item">
                  <span class="summary-label">🎯 Ne Yapar:</span>
                  <span class="summary-text">${s.core_value}</span>
                </div>` : ''}
                ${s.delta_to_us ? `
                <div class="summary-item">
                  <span class="summary-label">⚡ Sistem Değeri:</span>
                  <span class="summary-text">${s.delta_to_us}</span>
                </div>` : ''}
                ${s.action_plan ? `
                <div class="summary-item">
                  <span class="summary-label">🛠️ Eylem / Hedef:</span>
                  <span class="summary-text">${s.action_plan}</span>
                </div>` : ''}
              </div>` : ''}

              <!-- Denetim İzi & Audit Trail -->
              ${lastHist ? `
              <div class="audit-trail-box">
                <div class="audit-trail-title">
                  <span>📜 Son İşlem / Denetim İzi</span>
                  <button type="button" class="quiet small" style="padding:1px 6px; font-size:10.5px; color:#4338ca;" onclick="openHistoryModal(${r.id})">Tüm İzi Gör (${historyArr.length})</button>
                </div>
                <div class="audit-trail-row">
                  <span class="audit-trail-badge">${lastHist.action}</span>
                  <span style="font-size:10.5px; color:var(--muted);">${lastHist.date || ''}</span>
                  <span style="font-size:11px; overflow-wrap:anywhere;">${lastHist.note || ''}</span>
                </div>
                ${r.transferred_to ? `<div style="font-size:11px; margin-top:3px; color:#1d4ed8;"><strong>Aktarılan Yer:</strong> <code>${r.transferred_to}</code></div>` : ''}
              </div>` : ''}
            </div>

            <div class="card-bottom">
              <div class="card-actions-left">
                <button class="small btn-green" onclick="scoutRepo('${r.url}')" title="Şimdi Derin İncele">
                  <svg><use href="#i-bolt"/></svg>${(st !== 'PENDING') ? 'Tekrar İncele' : 'İncele'}
                </button>
                ${(st === 'PENDING') ? (isQueued
                  ? `<button class="small badge-queued" onclick="toggleQueueRepo('${r.url}')" title="Sıradan Çıkar">Sırada &times;</button>`
                  : `<button class="small" onclick="toggleQueueRepo('${r.url}')" title="İnceleme Sırasına Al">+ Sıraya Al</button>`) : ''}
                ${r.plan_content ? `
                  <button class="small btn-plan" onclick="viewPlan(${r.id})" title="İnceleme Raporunu / Planını Oku">
                    <svg><use href="#i-file"/></svg>Planı Gör
                  </button>` : ''}
                ${(isPlanned && !isTransferring && !isTransferred) ? `
                  <button class="small btn-integrate" onclick="openStartTransferModal('${r.url}', ${r.id}, '${r.name}')" title="Aktarım Sürecini Başlat">
                    <svg><use href="#i-arrow"/></svg>Aktarımı Başlat
                  </button>` : ''}
                ${isTransferring ? `
                  <button class="small btn-green" style="background:#7e22ce; border-color:#7e22ce;" onclick="openCompleteTransferModal('${r.url}', ${r.id}, '${r.name}', '${r.target_skill || ''}')" title="Aktarımı Tamamla ve Kapat">
                    <svg><use href="#i-check"/></svg>Aktarımı Tamamla
                  </button>` : ''}
                ${(isTransferred || historyArr.length > 0) ? `
                  <button class="small quiet" onclick="openHistoryModal(${r.id})" title="İşlem ve Denetim İzi Geçmişini İncele">
                    📜 İzi Gör
                  </button>` : ''}
              </div>
              <button class="icon-btn" onclick="copyRepoCmd('${r.url}')" title="scout komutunu kopyala">
                <svg><use href="#i-copy"/></svg>
              </button>
            </div>
          `;
          grid.append(card);
        });
      }

      // 2. Tablo Render
      const tbody = $('repoTableBody');
      tbody.replaceChildren();
      filtered.forEach(r => {
        const tr = document.createElement('tr');
        const st = (r.status || 'PENDING').toUpperCase();
        const isSuspended = st === 'SUSPENDED';
        const isCancel = ['CANCEL', 'CANCELED', 'CANCELLED'].includes(st);
        const isTransferring = st === 'TRANSFERRING';
        const v = (r.verdict || '').toUpperCase();
        const isTransferred = st === 'TRANSFERRED' || (!isSuspended && !isCancel && v.includes('AKTARILDI'));
        const isBetter = st === 'REJECTED' || (!isSuspended && !isCancel && (v.includes('DAHA_IYIYIZ') || v.includes('DAHA IYIYIZ')));
        const isCandidate = v.includes('ZENGINLESTIR') || v.includes('KISMEN_ALINABILIR') || v.includes('KABUL');
        const isPlanned = st === 'PLANNED' || (st === 'DONE' && isCandidate && !isTransferred);

        let tableBadge = '<span class="badge badge-pending">Beklemede</span>';
        if (isSuspended) tableBadge = '<span class="badge badge-suspended">⏸️ Askıda</span>';
        else if (isCancel) tableBadge = '<span class="badge badge-cancel">🚫 İptal</span>';
        else if (isTransferring) tableBadge = '<span class="badge badge-transferring">🚀 Aktarılıyor</span>';
        else if (isTransferred) tableBadge = '<span class="badge badge-transferred">✅ Aktarıldı</span>';
        else if (isPlanned) tableBadge = '<span class="badge badge-planned">✨ Aktarım Bekliyor</span>';
        else if (isBetter) tableBadge = '<span class="badge badge-rejected">🛡️ Elendi</span>';
        else if (st === 'DONE') tableBadge = '<span class="badge badge-done">İncelendi</span>';

        let pct = (r.progress !== undefined && r.progress !== null) ? Number(r.progress) : 0;
        if (pct === 0) {
          if (isTransferred) pct = 100;
          else if (isTransferring) pct = 50;
          else if (isPlanned) pct = 25;
        }

        const s = r.summary || {};
        const historyArr = r.history || [];
        const lastHist = historyArr.length > 0 ? historyArr[historyArr.length - 1] : null;

        tr.innerHTML = `
          <td>
            <strong>${r.name}</strong><br>
            <small style="color:var(--muted);">${r.owner}</small>
            ${r.target_skill ? `<div style="font-size:10.5px;color:#6d28d9;margin-top:2px;">🎯 ${r.target_skill}</div>` : ''}
          </td>
          <td><span class="badge badge-layer">${r.layer}</span></td>
          <td>
            <div style="display:flex; flex-direction:column; gap:4px; align-items:flex-start;">
              <div style="display:flex; align-items:center; gap:5px;">
                ${tableBadge}
                <span style="font-size:10.5px;font-weight:700;color:var(--ink);">%${pct}</span>
              </div>
              <select class="status-select sel-${st.toLowerCase()}" style="font-size:10px; padding:1px 16px 1px 4px;" onchange="changeRepoStatus('${r.id}', this.value)" title="Durumu Değiştir">
                <option value="PENDING" ${st === 'PENDING' ? 'selected' : ''}>⏳ Beklemede</option>
                <option value="PLANNED" ${st === 'PLANNED' ? 'selected' : ''}>✨ Aktarım Bekliyor</option>
                <option value="TRANSFERRING" ${st === 'TRANSFERRING' ? 'selected' : ''}>🚀 Aktarılıyor</option>
                <option value="TRANSFERRED" ${st === 'TRANSFERRED' ? 'selected' : ''}>✅ Aktarıldı</option>
                <option value="REJECTED" ${st === 'REJECTED' ? 'selected' : ''}>🛡️ Elendi</option>
                <option value="SUSPENDED" ${st === 'SUSPENDED' ? 'selected' : ''}>⏸️ Askıda</option>
                <option value="CANCEL" ${['CANCEL', 'CANCELED', 'CANCELLED'].includes(st) ? 'selected' : ''}>🚫 İptal</option>
              </select>
            </div>
          </td>
          <td>
            <div style="font-size:12px; line-height:1.4;">
              <strong>${r.verdict ? r.verdict.split(':')[0] : '-'}</strong>
              <div style="color:#57534e; margin-top:2px; max-width:420px;">${s.core_value || (r.verdict ? r.verdict.split(':').slice(1).join(':') : '-')}</div>
              ${lastHist ? `<div style="font-size:11px;color:#4338ca;margin-top:3px;">📜 <strong>${lastHist.action}:</strong> ${lastHist.note || ''}</div>` : ''}
              ${r.transferred_to ? `<div style="font-size:10.5px;color:#1d4ed8;">&rarr; <code>${r.transferred_to}</code></div>` : ''}
            </div>
          </td>
          <td style="text-align:right; white-space:nowrap;">
            <button class="small btn-green" onclick="scoutRepo('${r.url}')">${(st !== 'PENDING') ? 'Tekrar İncele' : 'İncele'}</button>
            ${r.plan_content ? `<button class="small" onclick="viewPlan(${r.id})">Plan</button>` : ''}
            ${(isPlanned && !isTransferring && !isTransferred) ? `<button class="small btn-integrate" onclick="openStartTransferModal('${r.url}', ${r.id}, '${r.name}')">🚀 Aktar</button>` : ''}
            ${isTransferring ? `<button class="small btn-green" style="background:#7e22ce;border-color:#7e22ce;" onclick="openCompleteTransferModal('${r.url}', ${r.id}, '${r.name}', '${r.target_skill || ''}')">✅ Tamamla</button>` : ''}
            ${historyArr.length > 0 ? `<button class="small quiet" onclick="openHistoryModal(${r.id})">📜 İzi Gör</button>` : ''}
            <button class="small" onclick="copyRepoCmd('${r.url}')">Kopyala</button>
            <button class="icon-btn delete" onclick="deleteRepo('${r.id}')"><svg><use href="#i-trash"/></svg></button>
          </td>
        `;
        tbody.append(tr);
      });
    }

    function updateStats() {
      const total = reposData.length;
      const pending = reposData.filter(r => r.status === 'PENDING' || r.status === 'ANALYZED').length;
      const transferring = reposData.filter(r => r.status === 'TRANSFERRING').length;
      const transferred = reposData.filter(r => {
        const v = (r.verdict || '').toUpperCase();
        return r.status === 'TRANSFERRED' || v.includes('AKTARILDI');
      }).length;
      const rejected = reposData.filter(r => {
        const v = (r.verdict || '').toUpperCase();
        return r.status === 'REJECTED' || (v.includes('DAHA_IYIYIZ') || v.includes('DAHA IYIYIZ'));
      }).length;
      const planned = reposData.filter(r => {
        const v = (r.verdict || '').toUpperCase();
        const isT = r.status === 'TRANSFERRED' || v.includes('AKTARILDI');
        const isC = v.includes('ZENGINLESTIR') || v.includes('KISMEN_ALINABILIR') || v.includes('KABUL');
        return r.status === 'PLANNED' || (r.status === 'DONE' && isC && !isT);
      }).length;
      const suspended = reposData.filter(r => r.status === 'SUSPENDED').length;
      const cancel = reposData.filter(r => ['CANCEL', 'CANCELED', 'CANCELLED'].includes(r.status)).length;

      if ($('totalBadge')) $('totalBadge').textContent = total;
      if ($('transferringBadge')) $('transferringBadge').textContent = transferring;
      if ($('plannedBadge')) $('plannedBadge').textContent = planned;
      if ($('toIntegrateBadge')) $('toIntegrateBadge').textContent = planned;
      if ($('transferredBadge')) $('transferredBadge').textContent = transferred;
      if ($('rejectedBadge')) $('rejectedBadge').textContent = rejected;
      if ($('betterBadge')) $('betterBadge').textContent = rejected;
      if ($('pendingBadge')) $('pendingBadge').textContent = pending;
      if ($('suspendedBadge')) $('suspendedBadge').textContent = suspended;
      if ($('cancelBadge')) $('cancelBadge').textContent = cancel;

      if ($('tabCountAll')) $('tabCountAll').textContent = total;
      if ($('tabCountTransferring')) $('tabCountTransferring').textContent = transferring;
      if ($('tabCountPlanned')) $('tabCountPlanned').textContent = planned;
      if ($('tabCountToIntegrate')) $('tabCountToIntegrate').textContent = planned;
      if ($('tabCountTransferred')) $('tabCountTransferred').textContent = transferred;
      if ($('tabCountRejected')) $('tabCountRejected').textContent = rejected;
      if ($('tabCountBetter')) $('tabCountBetter').textContent = rejected;
      if ($('tabCountPending')) $('tabCountPending').textContent = pending;
      if ($('tabCountSuspended')) $('tabCountSuspended').textContent = suspended;
      if ($('tabCountCancel')) $('tabCountCancel').textContent = cancel;
    }

    /* Sunucu Eylemleri */
    async function scoutRepo(url) {
      if (!isServerOnline) {
        showToast('⚠️ Yerel sunucu aktif değil. python scout/server.py çalıştırın.', 'error');
        return;
      }
      const repoName = url.split('/').pop();
      showToast(`🤖 AI Agent <strong>${repoName}</strong> reposunu derinlemesine inceliyor ve plan hazırlıyor...`, 'info', 35000);
      try {
        const res = await fetch(`${API_BASE}/api/scout-now`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ url })
        });
        const data = await res.json();
        if (res.ok && data.success) {
          reposData = data.repos;
          updateStats();
          render();
          showToast(`✅ <strong>${repoName}</strong> AI Agent tarafından incelendi ve karara bağlandı!`, 'success', 6000);
        } else {
          showToast(`❌ Hata: ${data.error || 'İnceleme başarısız'}`, 'error');
        }
      } catch (err) {
        showToast(`❌ İletişim hatası: ${err.message}`, 'error');
      }
    }

    async function scoutAllPending() {
      if (!isServerOnline) {
        showToast('⚠️ Yerel sunucu aktif değil. python scout/server.py çalıştırın.', 'error');
        return;
      }
      const pending = reposData.filter(r => r.status === 'PENDING');
      if (pending.length === 0) {
        showToast('Tüm repolar zaten incelenmiş.', 'info');
        return;
      }
      showToast(`🤖 AI Agent ${pending.length} bekleyen repoyu sırayla inceliyor ve rapor hazırlıyor...`, 'info', 35000);
      try {
        const res = await fetch(`${API_BASE}/api/scout-all`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' }
        });
        const data = await res.json();
        if (res.ok && data.success) {
          reposData = data.repos;
          updateStats();
          render();
          showToast('✅ Tüm bekleyen repolar incelendi!', 'success');
        }
      } catch (err) {
        showToast(`❌ Hata: ${err.message}`, 'error');
      }
    }

    async function changeRepoStatus(id, newStatus) {
      const repo = reposData.find(r => String(r.id) === String(id));
      if (!repo) return;
      const oldStatus = repo.status;
      if (oldStatus === newStatus) return;

      // İyimser UI güncellemesi
      repo.status = newStatus;
      updateStats();
      render();

      if (!isServerOnline) {
        showToast('⚠️ Yerel sunucu aktif değil. python scout/server.py çalıştırın.', 'error');
        return;
      }

      try {
        const res = await fetch(`${API_BASE}/api/repos/status`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ id, status: newStatus })
        });
        const data = await res.json();
        if (res.ok && data.success) {
          if (data.repos) {
            reposData = data.repos;
          }
          updateStats();
          render();
          const labelMap = {
            'PENDING': '⏳ Beklemede',
            'DONE': '✅ İncelendi',
            'SUSPENDED': '⏸️ Askıda',
            'CANCEL': '🚫 İptal'
          };
          showToast(`📌 <strong>${repo.name}</strong> durumu <strong>${labelMap[newStatus] || newStatus}</strong> olarak kaydedildi.`, 'success', 3500);
        } else {
          repo.status = oldStatus;
          updateStats();
          render();
          showToast(`❌ Durum güncellenemedi: ${data.error || 'Sunucu hatası'}`, 'error');
        }
      } catch (err) {
        repo.status = oldStatus;
        updateStats();
        render();
        showToast(`❌ İletişim hatası: ${err.message}`, 'error');
      }
    }

    async function deleteRepo(id) {
      if (!confirm('Bu repoyu katalogdan silmek istediğinize emin misiniz?')) return;
      try {
        const res = await fetch(`${API_BASE}/api/delete-repo`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ id })
        });
        const data = await res.json();
        if (res.ok && data.success) {
          reposData = data.repos;
          updateStats();
          render();
          showToast('🗑️ Repo katalogdan silindi.', 'success');
        }
      } catch (err) {
        showToast(`Hata: ${err.message}`, 'error');
      }
    }

    let activeTransferData = { url: '', id: null, name: '', target_skill: '' };

    function openStartTransferModal(url, id, name) {
      activeTransferData = { url, id, name, target_skill: '' };
      $('startTransferTitle').textContent = `🚀 Aktarımı Başlat: ${name}`;
      $('startTargetSkill').value = '';
      $('startTransferNotes').value = '';
      $('startTransferModal').classList.add('active');
      $('startTargetSkill').focus();
    }
    function closeStartTransferModal(e) {
      $('startTransferModal').classList.remove('active');
    }
    async function confirmStartTransfer() {
      const targetSkill = $('startTargetSkill').value.trim();
      const notes = $('startTransferNotes').value.trim() || 'Aktarım süreci başlatıldı.';
      const btn = $('confirmStartTransferBtn');
      btn.disabled = true;
      btn.innerText = 'Başlatılıyor...';

      try {
        const res = await fetch(`${API_BASE}/api/repos/transfer/start`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            id: activeTransferData.id,
            url: activeTransferData.url,
            target_skill: targetSkill,
            notes: notes
          })
        });
        const data = await res.json();
        if (res.ok && data.success) {
          if (data.repos) reposData = data.repos;
          updateStats();
          render();
          closeStartTransferModal();
          showToast(`🚀 <strong>${activeTransferData.name}</strong> aktarımı başlatıldı (%50)!`, 'success', 4000);
        } else {
          showToast(`❌ Hata: ${data.error || 'Aktarım başlatılamadı'}`, 'error');
        }
      } catch (err) {
        showToast(`❌ İletişim hatası: ${err.message}`, 'error');
      } finally {
        btn.disabled = false;
        btn.innerText = '🚀 Aktarımı Başlat (%50)';
      }
    }

    function openCompleteTransferModal(url, id, name, target_skill = '') {
      activeTransferData = { url, id, name, target_skill };
      $('completeTransferTitle').textContent = `✅ Aktarımı Tamamla: ${name}`;
      $('completeTargetSkill').value = target_skill || '';
      $('completeTransferredTo').value = '';
      $('completeTransferNotes').value = '';
      $('completeTransferModal').classList.add('active');
      $('completeTransferredTo').focus();
    }
    function closeCompleteTransferModal(e) {
      $('completeTransferModal').classList.remove('active');
    }
    async function confirmCompleteTransfer() {
      const targetSkill = $('completeTargetSkill').value.trim();
      const transferredTo = $('completeTransferredTo').value.trim();
      const notes = $('completeTransferNotes').value.trim() || 'Aktarım tamamlandı.';
      const btn = $('confirmCompleteTransferBtn');
      btn.disabled = true;
      btn.innerText = 'Kaydediliyor...';

      try {
        const res = await fetch(`${API_BASE}/api/repos/transfer/complete`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            id: activeTransferData.id,
            url: activeTransferData.url,
            target_skill: targetSkill,
            transferred_to: transferredTo,
            notes: notes
          })
        });
        const data = await res.json();
        if (res.ok && data.success) {
          if (data.repos) reposData = data.repos;
          updateStats();
          render();
          closeCompleteTransferModal();
          showToast(`✅ <strong>${activeTransferData.name}</strong> sisteme başarıyla aktarıldı (%100)!`, 'success', 4500);
        } else {
          showToast(`❌ Hata: ${data.error || 'Aktarım tamamlanamadı'}`, 'error');
        }
      } catch (err) {
        showToast(`❌ İletişim hatası: ${err.message}`, 'error');
      } finally {
        btn.disabled = false;
        btn.innerText = '✅ Aktarımı Tamamla (%100)';
      }
    }

    function openHistoryModal(id) {
      const repo = reposData.find(r => String(r.id) === String(id));
      if (!repo) return;
      $('historyModalTitle').textContent = `📜 ${repo.owner}/${repo.name} &middot; İşlem Geçmişi`;
      const list = $('historyModalList');
      list.replaceChildren();

      const historyArr = repo.history || [];
      if (historyArr.length === 0) {
        list.innerHTML = `<div style="text-align:center; padding:24px; color:var(--muted); font-size:13px;">Bu repo için kayıtlı bir işlem geçmişi bulunmuyor.</div>`;
      } else {
        historyArr.slice().reverse().forEach((h, idx) => {
          const item = document.createElement('div');
          item.style.cssText = 'padding:10px 14px; background:#f8fafc; border:1px solid #e2e8f0; border-radius:10px; font-size:12.5px;';
          item.innerHTML = `
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:5px;">
              <span class="audit-trail-badge" style="font-size:11px;">${h.action || 'İŞLEM'}</span>
              <span style="font-size:11.5px; color:var(--muted);">${h.date || '-'}</span>
            </div>
            <div style="margin-bottom:3px;"><strong>Durum:</strong> <code>${h.status || '-'}</code></div>
            ${h.note ? `<div style="color:#334155; margin-bottom:3px;"><strong>Not:</strong> ${h.note}</div>` : ''}
            ${h.target_skill ? `<div><strong>Hedef Skill:</strong> <code>${h.target_skill}</code></div>` : ''}
            ${h.transferred_to ? `<div style="color:#1d4ed8;"><strong>Aktarılan Yol:</strong> <code>${h.transferred_to}</code></div>` : ''}
          `;
          list.append(item);
        });
      }
      $('historyModal').classList.add('active');
    }
    function closeHistoryModal(e) {
      $('historyModal').classList.remove('active');
    }

    function openIntegrateModal(url) {
      const repo = reposData.find(r => r.url.toLowerCase() === url.toLowerCase());
      if (repo) {
        openStartTransferModal(url, repo.id, repo.name);
        return;
      }
      activeIntegrateUrl = url;
      $('integrateModal').classList.add('active');
      $('integrateNotes').focus();
    }
    function closeIntegrateModal() {
      $('integrateModal').classList.remove('active');
    }
    async function confirmIntegrate() {
      const notes = $('integrateNotes').value.trim() || 'Sisteme dahil edildi.';
      try {
        const res = await fetch(`${API_BASE}/api/integrate`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ url: activeIntegrateUrl, notes })
        });
        const data = await res.json();
        if (res.ok && data.success) {
          reposData = data.repos;
          updateStats();
          render();
          closeIntegrateModal();
          showToast('✅ Repo sisteme aktarıldı olarak kaydedildi!', 'success');
        }
      } catch (err) {
        showToast(`Hata: ${err.message}`, 'error');
      }
    }

    function viewPlan(id) {
      const r = reposData.find(x => x.id === id);
      if (!r || !r.plan_content) {
        showToast('Bu repo için henüz bir inceleme planı bulunmuyor.', 'info');
        return;
      }
      activeModalPlan = r.plan_content;
      $('planModalTitle').textContent = `📋 ${r.owner}/${r.name} İnceleme Planı`;
      
      // Basit markdown render
      let html = r.plan_content
        .replace(/^### (.*$)/gim, '<h3>$1</h3>')
        .replace(/^## (.*$)/gim, '<h2>$1</h2>')
        .replace(/^# (.*$)/gim, '<h1>$1</h1>')
        .replace(/\\*\\*(.*?)\\*\\*/gim, '<strong>$1</strong>')
        .replace(/\\*(.*?)\\*/gim, '<em>$1</em>')
        .replace(/`([^`]+)`/gim, '<code>$1</code>')
        .replace(/```([\\s\\S]*?)```/gim, '<pre><code>$1</code></pre>')
        .replace(/\\n/gim, '<br>');

      $('planModalContent').innerHTML = html;
      $('planModal').classList.add('active');
    }
    function closePlanModal() {
      $('planModal').classList.remove('active');
    }
    function copyPlanContent() {
      if (activeModalPlan) copyText(activeModalPlan);
    }

    function exportData() {
      const blob = new Blob([JSON.stringify(reposData, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `scout-catalog-${new Date().toISOString().slice(0, 10)}.json`;
      document.body.append(a);
      a.click();
      a.remove();
      setTimeout(() => URL.revokeObjectURL(url), 1000);
      showToast('💾 Katalog JSON formatında indirildi.', 'info');
    }

    /* İnceleme Sırası & Kuyruk Mantığı */
    function toggleQueueRepo(url) {
      const idx = scoutQueue.findIndex(q => q.url.toLowerCase() === url.toLowerCase());
      if (idx !== -1) {
        scoutQueue.splice(idx, 1);
        showToast('Kuyruktan çıkarıldı.', 'info', 1800);
      } else {
        const repo = reposData.find(r => r.url.toLowerCase() === url.toLowerCase());
        if (repo) {
          scoutQueue.push(repo);
          showToast(`🎯 <strong>${repo.name}</strong> #${scoutQueue.length} sıraya alındı.`, 'success', 2200);
        }
      }
      renderQueue();
      render();
    }

    function addAllPendingToQueue() {
      const pending = reposData.filter(r => r.status === 'PENDING');
      if (pending.length === 0) {
        showToast('Bekleyen repo bulunmuyor.', 'info');
        return;
      }
      scoutQueue = [...pending];
      showToast(`🎯 ${pending.length} bekleyen repo sıraya alındı.`, 'success');
      renderQueue();
      render();
    }

    function clearQueue() {
      if (isQueueRunning) return;
      scoutQueue = [];
      showToast('İnceleme sırası temizlendi.', 'info', 1800);
      renderQueue();
      render();
    }

    function moveQueueItem(index, direction) {
      if (isQueueRunning) return;
      const targetIdx = index + direction;
      if (targetIdx < 0 || targetIdx >= scoutQueue.length) return;
      const temp = scoutQueue[index];
      scoutQueue[index] = scoutQueue[targetIdx];
      scoutQueue[targetIdx] = temp;
      renderQueue();
      render();
    }

    function removeQueueItem(index) {
      if (isQueueRunning) return;
      scoutQueue.splice(index, 1);
      renderQueue();
      render();
    }

    function openQueueModal() {
      renderQueue();
      $('queueModal').classList.add('active');
    }

    function closeQueueModal(e) {
      if (isQueueRunning) return;
      $('queueModal').classList.remove('active');
    }

    function renderQueue() {
      const count = scoutQueue.length;
      $('queueCountBadge').textContent = count;
      $('queueBarCount').textContent = count;

      // Floating Dock görünürlüğü
      const dock = $('floatingQueueBar');
      if (count > 0 && !isQueueRunning) {
        dock.style.display = 'flex';
      } else if (!isQueueRunning) {
        dock.style.display = 'none';
      }

      // Dock Chips
      const chips = $('queueBarChips');
      chips.replaceChildren();
      scoutQueue.slice(0, 4).forEach((r, idx) => {
        const chip = document.createElement('span');
        chip.className = 'queue-chip';
        chip.innerHTML = `<b>#${idx + 1}</b> ${r.name}`;
        chips.append(chip);
      });
      if (count > 4) {
        const more = document.createElement('span');
        more.className = 'queue-chip';
        more.textContent = `+${count - 4} repo`;
        chips.append(more);
      }

      // Modal Listesi
      const list = $('queueItemList');
      list.replaceChildren();

      if (count === 0) {
        list.innerHTML = `
          <div style="text-align:center; padding:32px 16px; color:var(--muted); font-size:13px;">
            Henüz sıraya eklenmiş repo yok.<br>
            Yukarıdaki <strong>+ Tüm Bekleyenleri Al</strong> butonuna basabilir veya kartlardaki <strong>+ Sırala</strong> butonunu kullanabilirsiniz.
          </div>`;
        $('modalStartQueueBtn').disabled = true;
        $('startQueueBtn').disabled = true;
      } else {
        $('modalStartQueueBtn').disabled = !isServerOnline || isQueueRunning;
        $('startQueueBtn').disabled = !isServerOnline || isQueueRunning;

        scoutQueue.forEach((r, idx) => {
          const div = document.createElement('div');
          div.className = 'queue-item';
          div.id = `qItem_${idx}`;
          div.innerHTML = `
            <div class="queue-item-rank">#${idx + 1}</div>
            <div class="queue-item-info">
              <strong>${r.owner}/${r.name}</strong>
              <span class="badge badge-layer" style="margin-left:6px;">${r.layer}</span>
              <div style="font-size:11px; color:var(--muted); margin-top:2px;" id="qStatus_${idx}">Beklemede</div>
            </div>
            <div class="queue-item-controls">
              <button class="small icon-btn" onclick="moveQueueItem(${idx}, -1)" ${idx === 0 || isQueueRunning ? 'disabled' : ''} title="Yukarı taşı">▲</button>
              <button class="small icon-btn" onclick="moveQueueItem(${idx}, 1)" ${idx === count - 1 || isQueueRunning ? 'disabled' : ''} title="Aşağı taşı">▼</button>
              <button class="small icon-btn delete" onclick="removeQueueItem(${idx})" ${isQueueRunning ? 'disabled' : ''} title="Sıradan çıkar">&times;</button>
            </div>
          `;
          list.append(div);
        });
      }
    }

    async function startQueueScout() {
      if (scoutQueue.length === 0) return;
      if (!isServerOnline) {
        showToast('⚠️ Yerel sunucu aktif değil. python scout/server.py çalıştırın.', 'error');
        return;
      }

      isQueueRunning = true;
      const total = scoutQueue.length;
      openQueueModal();

      const wrap = $('queueProgressWrap');
      const bar = $('queueProgressBar');
      const pct = $('queueProgressPct');
      const statusText = $('queueProgressStatusText');

      wrap.style.display = 'block';
      $('modalStartQueueBtn').disabled = true;
      $('startQueueBtn').disabled = true;

      let completed = 0;
      let errors = 0;

      for (let i = 0; i < total; i++) {
        if (!isQueueRunning) {
          statusText.innerText = '⏹️ Sıralı inceleme durduruldu.';
          break;
        }

        const repo = scoutQueue[i];
        const p = Math.round(((i) / total) * 100);
        bar.style.width = p + '%';
        pct.innerText = p + '%';
        statusText.innerText = `İnceleniyor (${i + 1}/${total}): ${repo.owner}/${repo.name}...`;

        const itemStatus = $(`qStatus_${i}`);
        if (itemStatus) {
          itemStatus.innerText = '🤖 AI Agent inceliyor ve entegrasyon planı hazırlıyor...';
          itemStatus.style.color = 'var(--mint)';
        }

        showToast(`🔍 (#${i + 1}/${total}) <strong>${repo.name}</strong> analiz ediliyor...`, 'info', 4000);

        try {
          const res = await fetch(`${API_BASE}/api/scout-now`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url: repo.url })
          });
          const data = await res.json();
          if (res.ok && data.success) {
            completed++;
            if (itemStatus) {
              const v = data.result?.verdict?.split(':')[0] || 'Karar verildi';
              itemStatus.innerText = '✅ ' + v;
              itemStatus.style.color = 'var(--green)';
            }
            if (data.repos) {
              reposData = data.repos;
              updateStats();
              render();
            }
          } else {
            errors++;
            if (itemStatus) {
              itemStatus.innerText = '❌ Hata: ' + (data.error || 'Başarısız');
              itemStatus.style.color = 'var(--rose)';
            }
          }
        } catch (err) {
          errors++;
          if (itemStatus) {
            itemStatus.innerText = '❌ İletişim hatası';
            itemStatus.style.color = 'var(--rose)';
          }
        }
      }

      bar.style.width = '100%';
      pct.innerText = '100%';
      statusText.innerText = `✅ Sıralı inceleme tamamlandı! ${completed} başarılı, ${errors} hata.`;
      showToast(`🎉 Sıralı inceleme bitti! ${completed} repo karara bağlandı.`, 'success', 5000);

      isQueueRunning = false;
      scoutQueue = scoutQueue.filter(q => {
        const live = reposData.find(r => r.url.toLowerCase() === q.url.toLowerCase());
        return live && live.status === 'PENDING';
      });

      renderQueue();
      render();
    }

    /* Sunucu Durum Kontrolü */
    async function checkServerStatus() {
      const dot = $('serverDot');
      const text = $('serverStatusText');
      try {
        const res = await fetch(`${API_BASE}/api/status`);
        if (res.ok) {
          isServerOnline = true;
          dot.className = 'dot online';
          text.textContent = 'Yerel Sunucu Bağlı (5055)';
          $('scoutAllBtn').disabled = false;
        } else {
          throw new Error();
        }
      } catch {
        isServerOnline = false;
        dot.className = 'dot';
        text.textContent = 'Yerel Sunucu Çevrimdışı';
      }
      refreshComposerPreview();
    }

    // Başlangıç Yüklemesi
    updateStats();
    render();
    checkServerStatus();
    setInterval(checkServerStatus, 5000);
  </script>
</body>
</html>"""

    # Şablon içindeki veri yerleşimlerini bağla
    html_out = template.replace("__REPOS_JSON__", repos_json)
    return html_out


def build_catalog() -> Path:
    """repos.json'u okur, yeni HTML dosyasını yazar."""
    repos = parse_repos_md()
    html_content = generate_html(repos)
    CATALOG_HTML.write_text(html_content, encoding="utf-8")
    print(f"[*] {len(repos)} repo kaydı scout/repos.json üzerinden okundu.")
    print(f"[+] Private Scout Kataloğu derlendi: {CATALOG_HTML}")
    return CATALOG_HTML


# Geriye dönük uyumluluk alias
main = build_catalog


if __name__ == "__main__":
    build_catalog()
