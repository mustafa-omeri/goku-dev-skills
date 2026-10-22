#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""LLM Council Ranker Birim Test Paketi."""

import sys
import unittest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from council_ranker import (
    calculate_aggregate_rankings,
    format_council_table,
    get_sample_deliberation,
    parse_ranking_from_text,
)


class TestCouncilRanker(unittest.TestCase):

    def test_parse_strict_final_ranking(self):
        text = """Here is my review of the choices.
Option A is simple and maintainable.
Option B introduces excessive abstractions.
Option C has unnecessary dependencies.

FINAL RANKING:
1. Option A
2. Option C
3. Option B
"""
        ranking = parse_ranking_from_text(text)
        self.assertEqual(ranking, ["A", "C", "B"])

    def test_parse_fallback_ranking(self):
        text = """Overall, Response C is strongest, followed by Response B, and lastly Response A."""
        ranking = parse_ranking_from_text(text)
        self.assertEqual(ranking, ["C", "B", "A"])

    def test_parse_empty_text(self):
        ranking = parse_ranking_from_text("")
        self.assertEqual(ranking, [])

    def test_calculate_unanimous_ranking(self):
        peer_rankings = {
            "Judge1": ["A", "B", "C"],
            "Judge2": ["A", "B", "C"],
            "Judge3": ["A", "B", "C"],
        }
        res = calculate_aggregate_rankings(peer_rankings)
        self.assertEqual(len(res), 3)
        self.assertEqual(res[0]["candidate"], "A")
        self.assertEqual(res[0]["average_rank"], 1.0)
        self.assertEqual(res[0]["first_place_votes"], 3)
        self.assertEqual(res[1]["candidate"], "B")
        self.assertEqual(res[1]["average_rank"], 2.0)
        self.assertEqual(res[2]["candidate"], "C")
        self.assertEqual(res[2]["average_rank"], 3.0)

    def test_calculate_split_decision_and_tie_breaker(self):
        peer_rankings = {
            "Judge1": ["X", "Y"],
            "Judge2": ["Y", "X"],
        }
        res = calculate_aggregate_rankings(peer_rankings)
        # Both X and Y have average rank 1.5, 1 first place vote
        self.assertEqual(len(res), 2)
        self.assertEqual(res[0]["average_rank"], 1.5)
        self.assertEqual(res[1]["average_rank"], 1.5)

    def test_format_council_table_with_mapping(self):
        results = [
            {"candidate": "A", "average_rank": 1.25, "first_place_votes": 3, "votes_count": 4},
            {"candidate": "B", "average_rank": 2.50, "first_place_votes": 1, "votes_count": 4},
        ]
        mapping = {"A": "Option Alpha (Lightweight)", "B": "Option Beta (Heavy)"}
        table = format_council_table(results, mapping)
        self.assertIn("Option Alpha (Lightweight)", table)
        self.assertIn("| **#1** | A | 1.25 | 3 | 4 |", table)

    def test_sample_deliberation(self):
        parsed, mapping = get_sample_deliberation()
        self.assertEqual(len(parsed), 3)
        results = calculate_aggregate_rankings(parsed)
        # Option C should be ranked #1
        self.assertEqual(results[0]["candidate"], "C")
        self.assertLess(results[0]["average_rank"], 2.0)


if __name__ == "__main__":
    unittest.main()
