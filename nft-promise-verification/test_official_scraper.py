#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试官方 WebScraperTool
"""
import os
import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

from tools.web_scraper_official import WebScraperOfficial


def main():
    print("="*60)
    print(" Official WebScraper Test")
    print("="*60)

    scraper = WebScraperOfficial()

    # 测试多个网站
    test_urls = [
        ("https://www.azuki.com", "Azuki Official"),
        ("https://www.boredapeyachtclub.com", "BAYC Official"),
        ("https://github.com/XSpoonAi/spoon-toolkit", "GitHub Repo"),
    ]

    for url, name in test_urls:
        print(f"\n[Test: {name}]")
        print(f"URL: {url}")
        print("-" * 50)

        try:
            result = scraper.scrape_url(url, output_format="markdown")

            print(f"[OK] Success!")
            print(f"  - Title: {result.get('title', 'N/A')[:60]}...")
            print(f"  - Content Length: {result.get('content', '').__len__()} chars")
            print(f"\nContent Preview (first 300 chars):")
            print(result.get('content', '')[:300])
            print("...")

        except Exception as e:
            print(f"[FAIL] Error: {e}")

    print("\n" + "="*60)
    print(" Test Complete")
    print("="*60)


if __name__ == "__main__":
    main()
