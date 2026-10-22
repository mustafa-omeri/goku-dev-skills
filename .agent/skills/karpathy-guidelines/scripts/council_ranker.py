#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""LLM Council Ranker & Deliberation Aggregator.

Andrej Karpathy'nin llm-council mimarisinden esinlenerek geliştirilen,
çoklu model/ajan değerlendirmelerinden sıralamaları ayrıştıran ve
konsensüs ortalama derecesini (Borda & Ortalama Sıralama) hesaplayan araç.

Kullanım:
    python .agent/skills/karpathy-guidelines/scripts/council_ranker.py --sample
    python .agent/skills/karpathy-guidelines/scripts/council_ranker.py input.json --json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Windows konsol UTF-8 desteği
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        try:
            _stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass


def parse_ranking_from_text(ranking_text: str) -> List[str]:
    """Modelin değerlendirme metninden 'FINAL RANKING:' bölümünü ayrıştırır.

    Numaralandırılmış satırları (örn. '1. Response A' veya '1. Option B') yakalar.
    Format bulunamazsa genel desen araması ile geri çekilir (fallback).
    """
    if not ranking_text:
        return []

    lines = ranking_text.splitlines()
    ranking_started = False
    extracted_labels: List[str] = []

    # 1. Öncelik: 'FINAL RANKING:' başlığından sonrasını ara
    for line in lines:
        cleaned = line.strip()
        if re.search(r"^final\s+ranking\s*:", cleaned, re.IGNORECASE):
            ranking_started = True
            continue

        if ranking_started:
            # Boş satırları atla
            if not cleaned:
                continue
            # Numaralandırılmış listeyi ara: '1. Response A' veya '1. Option C'
            m = re.match(r"^\d+\.\s*(?:Response|Option|Candidate|Model)?\s*([A-Za-z0-9_-]+)", cleaned, re.IGNORECASE)
            if m:
                label = m.group(1).upper()
                if label not in extracted_labels:
                    extracted_labels.append(label)
            else:
                # Sıralama formatı bittiyse dur
                if re.match(r"^[A-Z][a-z]+:", cleaned):
                    break

    if extracted_labels:
        return extracted_labels

    # 2. Fallback: Metin içinde doğrudan 'FINAL RANKING:' varsa sonrasındaki satırları tara
    if "FINAL RANKING:" in ranking_text.upper():
        parts = re.split(r"FINAL\s+RANKING\s*:", ranking_text, flags=re.IGNORECASE)
        if len(parts) >= 2:
            section = parts[1]
            matches = re.findall(r"(?:Response|Option|Candidate)\s+([A-Za-z0-9_-]+)", section, re.IGNORECASE)
            for m in matches:
                lbl = m.strip().upper()
                if lbl not in extracted_labels:
                    extracted_labels.append(lbl)
            if extracted_labels:
                return extracted_labels

    # 3. Son Fallback: Tüm metindeki 'Response X' veya 'Option X' dizilerini sırasıyla al
    general_matches = re.findall(r"\b(?:Response|Option)\s+([A-Z])\b", ranking_text, re.IGNORECASE)
    seen = set()
    for g in general_matches:
        u = g.upper()
        if u not in seen:
            seen.add(u)
            extracted_labels.append(u)

    return extracted_labels


def calculate_aggregate_rankings(peer_rankings: Dict[str, List[str]]) -> List[Dict[str, Any]]:
    """Tüm hakemlerden gelen sıralamaları birleştirerek ortalama dereceyi hesaplar.

    Args:
        peer_rankings: { 'Model 1': ['C', 'A', 'B'], 'Model 2': ['C', 'B', 'A'] }

    Returns:
        Ortalama sıralamaya göre en iyiden en kötüye sıralanmış liste.
    """
    if not peer_rankings:
        return []

    # Her adayın pozisyon listesini tut
    positions: Dict[str, List[int]] = defaultdict(list)
    first_place_votes: Dict[str, int] = defaultdict(int)

    total_judges = len(peer_rankings)

    for judge, ranking in peer_rankings.items():
        for rank_idx, candidate in enumerate(ranking):
            pos = rank_idx + 1  # 1-based index (1 en iyi)
            positions[candidate].append(pos)
            if pos == 1:
                first_place_votes[candidate] += 1

    results: List[Dict[str, Any]] = []

    for candidate, pos_list in positions.items():
        avg_pos = sum(pos_list) / len(pos_list)
        votes = len(pos_list)
        first_votes = first_place_votes.get(candidate, 0)

        results.append({
            "candidate": candidate,
            "average_rank": round(avg_pos, 2),
            "votes_count": votes,
            "first_place_votes": first_votes,
            "all_positions": pos_list
        })

    # Sıralama kuralı: Ortalama pozisyonu en düşük (1'e en yakın) olan en üstte
    results.sort(key=lambda x: (x["average_rank"], -x["first_place_votes"]))
    return results


def format_council_table(
    aggregate_results: List[Dict[str, Any]],
    deanonymize_map: Optional[Dict[str, str]] = None
) -> str:
    """Sonuçları okunabilir bir konsensüs tablosu olarak biçimlendirir."""
    if not aggregate_results:
        return "Konsensüs sonucu bulunamadı."

    header = "| Sıra | Aday | Ortalama Derece | 1.lik Oyları | Toplam Oy |"
    sep = "|---|---|---|---|---|"
    if deanonymize_map:
        header += " Açık Kimlik / Çözüm |"
        sep += "---|"

    lines = [header, sep]

    for idx, r in enumerate(aggregate_results, start=1):
        cand = r["candidate"]
        avg = f"{r['average_rank']:.2f}"
        firsts = str(r["first_place_votes"])
        votes = str(r["votes_count"])

        line = f"| **#{idx}** | {cand} | {avg} | {firsts} | {votes} |"
        if deanonymize_map:
            actual = deanonymize_map.get(cand, deanonymize_map.get(f"Option {cand}", cand))
            line += f" `{actual}` |"
        lines.append(line)

    return "\n".join(lines)


def get_sample_deliberation() -> Tuple[Dict[str, List[str]], Dict[str, str]]:
    """Örnek test verisi üretir."""
    sample_evaluations = {
        "Reviewer_Alpha": [
            "Option C provides the cleanest separation of concerns and lowest cognitive load.",
            "Option A is good but introduces unnecessary boilerplate.",
            "Option B is overly complicated.",
            "FINAL RANKING:",
            "1. Option C",
            "2. Option A",
            "3. Option B"
        ],
        "Reviewer_Beta": [
            "Option C has the best performance characteristics.",
            "Option B has too many moving parts.",
            "FINAL RANKING:",
            "1. Option C",
            "2. Option B",
            "3. Option A"
        ],
        "Reviewer_Gamma": [
            "Option A is simple, Option C is equally sound.",
            "FINAL RANKING:",
            "1. Option A",
            "2. Option C",
            "3. Option B"
        ]
    }

    parsed = {k: parse_ranking_from_text("\n".join(v)) for k, v in sample_evaluations.items()}
    mapping = {
        "A": "Zustand Store (Basit)",
        "B": "Redux Toolkit + Sagas (Aşırı Karmaşık)",
        "C": "React Context + useReducer (Doğal & Hafif)"
    }
    return parsed, mapping


def main() -> int:
    parser = argparse.ArgumentParser(description="LLM Council Consensus & Ranking Aggregator")
    parser.add_argument("input_file", nargs="?", help="Hakem değerlendirmelerini içeren JSON dosyası")
    parser.add_argument("--sample", action="store_true", help="Örnek konsensüs değerlendirmesini koşturur")
    parser.add_argument("--json", action="store_true", help="JSON formatında makine çıktısı basar")
    parser.add_argument("--mapping", help="Adayların gerçek isimlerini içeren JSON harita dosyası")

    args = parser.parse_args()

    if args.sample or not args.input_file:
        parsed_rankings, mapping = get_sample_deliberation()
        results = calculate_aggregate_rankings(parsed_rankings)

        if args.json:
            print(json.dumps({"results": results, "mapping": mapping}, ensure_ascii=False, indent=2))
            return 0

        print("=" * 70)
        print("🏛️ LLM Council Konsensüs & Hakemlik Raporu (Örnek Çalışma)")
        print("=" * 70)
        print("\nHakem Sıralamaları (Stage 2 Akran Değerlendirmesi):")
        for judge, r in parsed_rankings.items():
            print(f"  - {judge}: {' > '.join(r)}")

        print("\nBirleştirilmiş Konsensüs Tablosu (Stage 3 Chairman Girdisi):")
        print(format_council_table(results, mapping))
        print("=" * 70)
        return 0

    input_path = Path(args.input_file).resolve()
    if not input_path.exists():
        print(f"[HATA] Dosya bulunamadı: {input_path}", file=sys.stderr)
        return 1

    try:
        data = json.loads(input_path.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"[HATA] JSON okuma hatası: {e}", file=sys.stderr)
        return 1

    # data { judge_name: text_or_list }
    peer_rankings: Dict[str, List[str]] = {}
    for judge, val in data.items():
        if isinstance(val, list):
            peer_rankings[judge] = [str(x).upper() for x in val]
        elif isinstance(val, str):
            peer_rankings[judge] = parse_ranking_from_text(val)

    mapping = None
    if args.mapping:
        map_path = Path(args.mapping).resolve()
        if map_path.exists():
            mapping = json.loads(map_path.read_text(encoding="utf-8"))

    results = calculate_aggregate_rankings(peer_rankings)

    if args.json:
        print(json.dumps({"results": results, "rankings": peer_rankings}, ensure_ascii=False, indent=2))
        return 0

    print("=" * 70)
    print("🏛️ LLM Council Konsensüs & Hakemlik Raporu")
    print("=" * 70)
    print(format_council_table(results, mapping))
    print("=" * 70)
    return 0


if __name__ == "__main__":
    sys.exit(main())
