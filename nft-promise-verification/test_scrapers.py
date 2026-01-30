#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试队友的抓取工具是否可用
"""
import os
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv()

# Windows 控制台编码修复
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')


def test_web_scraper():
    """测试 WebScraper"""
    from tools.web_scraper import WebScraper

    print("\n[Test: WebScraper]")
    print("-" * 50)

    test_url = "https://www.azuki.com"

    try:
        scraper = WebScraper(timeout=30)
        print(f"正在爬取: {test_url}")

        result = scraper.scrape_url(test_url, output_format="markdown")

        print(f"[OK] 爬取成功!")
        print(f"  - 标题: {result.get('title', 'N/A')[:50]}...")
        print(f"  - 内容长度: {len(result.get('content', ''))} 字符")
        print(f"\n内容预览:")
        print(result.get('content', '')[:500])
        print("...")
        return True

    except Exception as e:
        print(f"[FAIL] 爬取失败: {e}")
        return False


def test_twitter_scraper():
    """测试 TwitterScraper"""
    from tools.twitter_scraper import TwitterScraper

    print("\n[Test: TwitterScraper]")
    print("-" * 50)

    username = "AzukiElementals"

    try:
        scraper = TwitterScraper(delay_seconds=1.0)
        print(f"正在抓取: @{username}")

        tweets = scraper.scrape_user_tweets(username, max_tweets=5)

        print(f"[OK] 抓取成功! 获取 {len(tweets)} 条推文")
        for i, tweet in enumerate(tweets[:3], 1):
            print(f"\n  推文 {i}:")
            print(f"    - 内容: {tweet.get('text', 'N/A')[:80]}...")
            print(f"    - 时间: {tweet.get('created_at', 'N/A')}")
            print(f"    - 链接: {tweet.get('url', 'N/A')}")
        return True

    except ImportError as e:
        print(f"[FAIL] snscrape 未安装: {e}")
        print("       提示: snscrape 已停止维护，Twitter 抓取可能不可用")
        return False
    except Exception as e:
        print(f"[FAIL] 抓取失败: {e}")
        return False


def main():
    print("="*60)
    print(" Scrapers Test")
    print("="*60)

    results = {}

    # 测试 WebScraper
    results["web_scraper"] = test_web_scraper()

    # 测试 TwitterScraper
    results["twitter_scraper"] = test_twitter_scraper()

    # 总结
    print("\n" + "="*60)
    print(" Summary")
    print("="*60)

    for name, result in results.items():
        if result:
            print(f"[PASS] {name}")
        else:
            print(f"[FAIL] {name}")

    print()


if __name__ == "__main__":
    main()
