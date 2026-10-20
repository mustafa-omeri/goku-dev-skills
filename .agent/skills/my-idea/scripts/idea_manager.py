#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fikir Havuzu Yöneticisi (Idea Manager).

`docs/idea/myidea.md` dosyasını analiz eder, durumları ve rating puanlarını ayrıştırır,
elenenleri filtreler ve en yüksek puanlı fikirleri listeler.

Kullanım:
    python .agent/skills/my-idea/scripts/idea_manager.py --list
    python .agent/skills/my-idea/scripts/idea_manager.py --top 3
    python .agent/skills/my-idea/scripts/idea_manager.py --to-card IDEA-002
    python .agent/skills/my-idea/scripts/idea_manager.py --to-card IDEA-002 --append
    python .agent/skills/my-idea/scripts/idea_manager.py --json
    python .agent/skills/my-idea/scripts/idea_manager.py --init
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

# UTF-8 stdout desteği (Windows cp1254 sorunlarını önler)
for stream in (sys.stdout, sys.stderr):
    if hasattr(stream, "reconfigure"):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass


def find_project_root() -> Path:
    """En yakın proje kökünü (.agent veya docs/ içeren dizin) bulur."""
    current = Path.cwd().resolve()
    for parent in [current] + list(current.parents):
        if (parent / ".agent").is_dir() or (parent / "docs").is_dir():
            return parent
    return current


def get_default_idea_file(project_root: Path) -> Path:
    """Varsayılan myidea.md dosya yolunu döner."""
    candidates = [
        project_root / "docs" / "idea" / "myidea.md",
        project_root / "docs" / "myidea.md",
        project_root / "myidea.md",
    ]
    for c in candidates:
        if c.is_file():
            return c
    return project_root / "docs" / "idea" / "myidea.md"


def get_template_file(project_root: Path) -> Path:
    """Şablon dosyasının yolunu döner."""
    candidates = [
        project_root / ".agent" / "templates" / "myidea.template.md",
        Path(__file__).resolve().parents[3] / "templates" / "myidea.template.md",
    ]
    for c in candidates:
        if c.is_file():
            return c
    return project_root / ".agent" / "templates" / "myidea.template.md"


def parse_ideas(content: str) -> list[dict]:
    """myidea.md dosya içeriğini ayrıştırarak fikir objeleri listesi döner."""
    ideas = []
    # ### IDEA-XXX: Başlık kalıbını eşle
    pattern = re.compile(r"^###\s+([A-Za-z0-9_-]+):\s*(.+)$", re.MULTILINE)
    matches = list(pattern.finditer(content))

    for i, match in enumerate(matches):
        idea_id = match.group(1).strip()
        title = match.group(2).strip()

        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(content)
        block = content[start:end]

        # Alanları çıkar
        status_match = re.search(r"-\s+\*\*Durum:\*\*\s*(.+)$", block, re.MULTILINE)
        rating_match = re.search(r"-\s+\*\*Rating:\*\*\s*`?([0-9.]+)(?:/10)?`?", block, re.MULTILINE)
        desc_match = re.search(r"-\s+\*\*Açıklama:\*\*\s*(.+)$", block, re.MULTILINE)
        value_match = re.search(r"-\s+\*\*Değer\s*/\s*Gerekçe:\*\*\s*(.+)$", block, re.MULTILINE)
        note_match = re.search(r"-\s+\*\*Ajan\s*(?:Notu|Değerlendirmesi):\*\*\s*(.+)$", block, re.MULTILINE)

        status_raw = status_match.group(1).strip() if status_match else "[NEW]"
        score = float(rating_match.group(1)) if rating_match else 0.0
        desc = desc_match.group(1).strip() if desc_match else ""
        value = value_match.group(1).strip() if value_match else ""
        note = note_match.group(1).strip() if note_match else ""

        # Elenme / Durum kontrolü (İngilizce standart + Türkçe geriye dönük uyumluluk)
        is_eliminated = any(kw in status_raw for kw in ("DROPPED", "REJECTED", "ELENDI", "ELENDİ", "⛔"))
        is_done = any(kw in status_raw for kw in ("SHIPPED", "IMPLEMENTED", "DONE", "UYGULANDI", "TAMAMLANDI", "✅"))
        is_deferred = any(kw in status_raw for kw in ("DEFERRED", "POSTPONED", "ERTELENDI", "ERTELENDİ", "⏳"))

        ideas.append({
            "id": idea_id,
            "title": title,
            "status_raw": status_raw,
            "score": score,
            "description": desc,
            "value": value,
            "agent_note": note,
            "is_eliminated": is_eliminated,
            "is_done": is_done,
            "is_deferred": is_deferred,
            "is_active": not (is_eliminated or is_done),
        })

    return ideas


def format_kanban_card(idea: dict, sprint: str = "S2", card_id: str | None = None) -> str:
    """Fikir objesinden standart KANBAN.md kart bloğu üretir."""
    score = idea.get("score", 0.0)
    priority = "P1" if score >= 8.5 else ("P2" if score >= 7.0 else "P3")
    cid = card_id or f"{sprint}-{idea.get('id', 'IDEA').replace('IDEA-', '')}"
    title = idea.get("title", "Yeni Görev")
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")

    return (
        f"### {cid} · {title}\n"
        f"| alan | değer |\n"
        f"|---|---|\n"
        f"| durum | Bekliyor |\n"
        f"| oncelik | {priority} |\n"
        f"| sprint | {sprint} |\n"
        f"| gherkin | specs/{cid}.feature#{slug} |\n"
        f"| kapi | python tests/run_all.py |\n"
        f"| test | (yazılacak) |\n"
        f"| risk | orta |\n"
    )


def convert_idea_to_card(
    idea_id: str,
    ideas: list[dict],
    sprint: str = "S2",
    append_target: Path | None = None,
) -> str | None:
    """Belirtilen fikir ID'sini bulup KANBAN kartına dönüştürür, istenirse dosyaya ekler."""
    matched = None
    for item in ideas:
        if item["id"].lower() == idea_id.lower():
            matched = item
            break
    if not matched:
        return None

    card_md = format_kanban_card(matched, sprint=sprint)

    if append_target and append_target.is_file():
        content = append_target.read_text(encoding="utf-8")
        if "## Bekliyor" in content:
            parts = content.split("## Bekliyor", 1)
            new_content = parts[0] + "## Bekliyor\n\n" + card_md + "\n" + parts[1].lstrip("\r\n")
            append_target.write_text(new_content, encoding="utf-8")
        else:
            append_target.write_text(content.rstrip() + "\n\n" + card_md + "\n", encoding="utf-8")

    return card_md


def init_idea_file(target_path: Path, template_path: Path) -> bool:
    """Yoksa docs/idea/myidea.md dosyasını şablondan oluşturur."""
    if target_path.exists():
        print(f"[BILGI] Dosya zaten mevcut: {target_path}")
        return False

    target_path.parent.mkdir(parents=True, exist_ok=True)
    if template_path.is_file():
        content = template_path.read_text(encoding="utf-8")
    else:
        content = (
            "# 💡 PROJE FİKİR HAVUZU (myidea.md)\n\n"
            "## 📌 Status Badges\n"
            "- 💡 `[NEW]` : Newly added raw idea awaiting assessment.\n"
            "- 🎯 `[RECOMMENDED]` : High-scoring idea recommended for development.\n"
            "- ⏳ `[DEFERRED]` : Deferred due to prerequisites or timing.\n"
            "- ⛔ `[DROPPED - Reason]` : Obsolete or superseded idea (archived with reason).\n"
            "- ✅ `[SHIPPED - Card/Date]` : Successfully shipped into codebase.\n\n"
            "## 🚀 Ideas List\n\n"
        )
    target_path.write_text(content, encoding="utf-8")
    print(f"[OK] Fikir havuzu dosyası oluşturuldu: {target_path}")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description="Fikir havuzu analiz ve sıralama aracı.")
    parser.add_argument("--file", "-f", type=str, help="İncelenecek myidea.md dosya yolu.")
    parser.add_argument("--list", "-l", action="store_true", help="Tüm fikirleri listele.")
    parser.add_argument("--top", "-t", type=int, default=0, help="En yüksek puanlı N fikri getir.")
    parser.add_argument("--to-card", "-c", type=str, metavar="IDEA_ID", help="Belirtilen fikir ID'sini KANBAN.md kartı formatına dönüştürür.")
    parser.add_argument("--sprint", "-s", type=str, default="S2", help="Kart için hedef sprint (varsayılan: S2).")
    parser.add_argument("--append", "-a", action="store_true", help="Üretilen kartı doğrudan KANBAN.md dosyasına ekler.")
    parser.add_argument("--json", "-j", action="store_true", help="JSON formatında çıktı ver.")
    parser.add_argument("--init", action="store_true", help="docs/idea/myidea.md dosyasını başlat.")

    args = parser.parse_args()
    project_root = find_project_root()

    idea_file = Path(args.file).resolve() if args.file else get_default_idea_file(project_root)
    template_file = get_template_file(project_root)

    if args.init:
        init_idea_file(idea_file, template_file)
        return 0

    if not idea_file.is_file():
        if args.json:
            print(json.dumps({"error": f"Fikir dosyası bulunamadı: {idea_file}", "ideas": []}))
        else:
            print(f"[UYARI] Fikir dosyası bulunamadı: {idea_file}")
            print(f"Oluşturmak için: python .agent/skills/my-idea/scripts/idea_manager.py --init")
        return 1

    content = idea_file.read_text(encoding="utf-8")
    ideas = parse_ideas(content)

    if args.to_card:
        kanban_file = project_root / "KANBAN.md" if args.append else None
        card = convert_idea_to_card(args.to_card, ideas, sprint=args.sprint, append_target=kanban_file)
        if not card:
            if args.json:
                print(json.dumps({"error": f"Fikir bulunamadı: {args.to_card}"}, ensure_ascii=False))
            else:
                print(f"[HATA] Fikir bulunamadı: {args.to_card}")
            return 1
        if args.json:
            print(json.dumps({"idea_id": args.to_card, "sprint": args.sprint, "card": card}, ensure_ascii=False, indent=2))
        else:
            print(f"============================================================")
            print(f"📋 KANBAN KARTI: {args.to_card} -> {args.sprint}")
            print(f"============================================================\n")
            print(card)
            if args.append and kanban_file and kanban_file.is_file():
                print(f"[OK] Kart {kanban_file.name} dosyasının '## Bekliyor' bölümüne eklendi.")
        return 0

    if args.top > 0:
        # Aktif ve elenmemiş fikirleri puana göre sırala
        active_ideas = [i for i in ideas if i["is_active"] and not i["is_deferred"]]
        active_ideas.sort(key=lambda x: x["score"], reverse=True)
        selected = active_ideas[: args.top]
    else:
        selected = ideas

    if args.json:
        output = {
            "file": str(idea_file),
            "total_count": len(ideas),
            "selected_count": len(selected),
            "ideas": selected,
        }
        print(json.dumps(output, ensure_ascii=False, indent=2))
        return 0

    # Formatlı terminal çıktısı
    print(f"============================================================")
    print(f"💡 FİKİR HAVUZU ANALİZİ: {idea_file.name}")
    print(f"Toplam Fikir: {len(ideas)}")
    print(f"============================================================")

    for idx, item in enumerate(selected, 1):
        status_tag = item["status_raw"]
        badge = "⛔" if item["is_eliminated"] else ("✅" if item["is_done"] else ("⏳" if item["is_deferred"] else "🎯"))
        print(f"\n{idx}. [{item['id']}] {item['title']}")
        print(f"   Durum: {badge} {status_tag} | Rating: {item['score']}/10")
        if item["description"]:
            print(f"   Açıklama: {item['description']}")
        if item["value"]:
            print(f"   Değer: {item['value']}")
        if item["agent_note"]:
            print(f"   Ajan Notu: {item['agent_note']}")

    print(f"\n============================================================")
    return 0


if __name__ == "__main__":
    sys.exit(main())
