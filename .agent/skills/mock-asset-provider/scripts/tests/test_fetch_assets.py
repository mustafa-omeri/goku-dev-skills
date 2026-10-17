#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Unit tests for fetch_assets.py in mock-asset-provider."""

import unittest
from pathlib import Path
import sys

# Add parent directory to sys.path to import fetch_assets
SCRIPT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPT_DIR))

import fetch_assets


class TestFetchAssets(unittest.TestCase):
    def test_generate_portrait_urls_women(self):
        urls = fetch_assets.generate_portrait_urls(gender="women", count=3, seed="test-seed")
        self.assertEqual(len(urls), 3)
        for u in urls:
            self.assertTrue(u.startswith("https://randomuser.me/api/portraits/women/"))

    def test_generate_portrait_urls_men(self):
        urls = fetch_assets.generate_portrait_urls(gender="men", count=2, seed="test-seed")
        self.assertEqual(len(urls), 2)
        for u in urls:
            self.assertTrue(u.startswith("https://randomuser.me/api/portraits/men/"))

    def test_generate_event_urls(self):
        urls = fetch_assets.generate_event_urls(count=2, seed="event-test", width=800, height=600)
        self.assertEqual(len(urls), 2)
        self.assertEqual(urls[0], "https://picsum.photos/seed/event-test-0/800/600")
        self.assertEqual(urls[1], "https://picsum.photos/seed/event-test-1/800/600")

    def test_generate_avatar_urls(self):
        urls = fetch_assets.generate_avatar_urls(style="avataaars", count=2, seed="user")
        self.assertEqual(len(urls), 2)
        self.assertEqual(urls[0], "https://api.dicebear.com/7.x/avataaars/svg?seed=user-0")

    def test_get_assets_dispatcher(self):
        p_urls = fetch_assets.get_assets("portraits", count=1)
        self.assertEqual(len(p_urls), 1)
        e_urls = fetch_assets.get_assets("events", count=1)
        self.assertEqual(len(e_urls), 1)
        a_urls = fetch_assets.get_assets("avatars", count=1)
        self.assertEqual(len(a_urls), 1)


if __name__ == "__main__":
    unittest.main()
