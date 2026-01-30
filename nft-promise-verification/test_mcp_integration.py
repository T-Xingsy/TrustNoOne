#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP 集成测试脚本

测试 MCPWebScraperTool 是否能正常工作并集成到项目中
"""
import os
import sys
from pathlib import Path

# Windows 控制台编码修复
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv()


def print_header(title: str):
    """打印标题"""
    print("\n" + "=" * 60)
    print(f" {title}")
    print("=" * 60)


def print_test(name: str):
    """打印测试名称"""
    print(f"\n[Test: {name}]")
    print("-" * 50)


def test_mcp_scraper_direct():
    """测试 MCP 抓取器直接调用"""
    from tools.mcp_scraper import MCPWebScraper
    import asyncio

    print_test("1. MCP Scraper Direct Import & Call")

    async def run_test():
        scraper = MCPWebScraper()
        try:
            # 测试 GitHub
            result = await scraper.fetch("https://github.com/XSpoonAi/spoon-toolkit")

            print(f"URL: {result['url']}")
            print(f"Status: {result['status']}")
            print(f"Content Length: {result.get('content_length', 0)} chars")
            print(f"Title: {result.get('title', 'N/A')}")

            if result['status'] == 'success':
                print("\n[OK] MCP Scraper 直接调用成功!")
                print(f"\nContent Preview (first 200 chars):")
                print(result.get('content', '')[:200] + "...")
                return True
            else:
                print(f"\n[FAIL] {result.get('error', 'Unknown error')}")
                return False
        finally:
            await scraper.close()

    return asyncio.run(run_test())


def test_mcp_tool_wrapper():
    """测试 MCP 工具包装器"""
    print_test("2. MCPWebScraperTool (Wrapper)")

    from tools_config import MCPWebScraperTool

    tool = MCPWebScraperTool()

    if not tool.available:
        print("[FAIL] MCP 工具不可用")
        return False

    print(f"Tool name: {tool.name}")
    print(f"Tool description: {tool.description[:80]}...")

    try:
        # 测试同步接口
        result = tool._run(
            url="https://www.boredapeyachtclub.com",
            output_format="markdown"
        )

        print(f"URL: {result['url']}")
        print(f"Status: {result['status']}")
        print(f"Content Length: {result.get('content_length', 0)} chars")

        if result['status'] == 'success':
            print("\n[OK] MCPWebScraperTool 同步调用成功!")
            return True
        else:
            print(f"\n[FAIL] {result.get('error', 'Unknown error')}")
            return False

    except Exception as e:
        print(f"[FAIL] Exception: {e}")
        return False


def test_tool_manager_integration():
    """测试工具管理器集成"""
    print_test("3. ToolManager Integration")

    from llm_config import LLMManager
    from tools_config import register_tools

    try:
        # 初始化 LLM 管理器
        llm_manager = LLMManager()

        # 注册所有工具
        tool_manager = register_tools(llm_manager)

        # 列出所有工具
        all_tools = tool_manager.get_all_tools()
        print(f"Total tools registered: {len(all_tools)}")

        for tool in all_tools:
            print(f"  - {tool.name}: {tool.__class__.__name__}")

        # 检查 MCP 工具是否注册
        mcp_tool = None
        for tool in all_tools:
            if tool.name == "mcp_web_scraper":
                mcp_tool = tool
                break

        if mcp_tool:
            print("\n[OK] MCP Web Scraper 已注册到 ToolManager!")
            return True
        else:
            print("\n[WARN] MCP Web Scraper 未找到")
            return False

    except Exception as e:
        print(f"[FAIL] {e}")
        import traceback
        traceback.print_exc()
        return False


def test_fetch_comparison():
    """对比不同抓取方式"""
    print_test("4. Fetch Methods Comparison")

    test_url = "https://github.com/XSpoonAi/spoon-toolkit"

    results = {}

    # 1. MCP 抓取
    try:
        from tools.mcp_scraper import SyncMCPWebScraper
        mcp = SyncMCPWebScraper()
        mcp_result = mcp.fetch(test_url)
        results['MCP'] = {
            'status': mcp_result.get('status'),
            'length': mcp_result.get('content_length', 0)
        }
        print(f"  MCP: {results['MCP']['status']} ({results['MCP']['length']} chars)")
    except Exception as e:
        results['MCP'] = {'status': 'error', 'error': str(e)}
        print(f"  MCP: Error - {e}")

    # 2. 官方 WebScraper
    try:
        from tools.web_scraper_official import WebScraperOfficial
        official = WebScraperOfficial()
        official_result = official.scrape_url(test_url, output_format="markdown")
        results['WebScraperOfficial'] = {
            'status': 'success',
            'length': len(official_result.get('content', ''))
        }
        print(f"  WebScraperOfficial: {results['WebScraperOfficial']['status']} ({results['WebScraperOfficial']['length']} chars)")
    except Exception as e:
        results['WebScraperOfficial'] = {'status': 'error', 'error': str(e)}
        print(f"  WebScraperOfficial: Error - {e}")

    # 3. 队友的 WebScraper
    try:
        from tools.web_scraper import WebScraper
        ws = WebScraper(timeout=30)
        ws_result = ws.scrape_url(test_url, output_format="markdown")
        results['WebScraper'] = {
            'status': 'success',
            'length': len(ws_result.get('content', ''))
        }
        print(f"  WebScraper (teammate): {results['WebScraper']['status']} ({results['WebScraper']['length']} chars)")
    except Exception as e:
        results['WebScraper'] = {'status': 'error', 'error': str(e)}
        print(f"  WebScraper (teammate): Error - {e}")

    # 判断
    success_count = sum(1 for r in results.values() if r.get('status') == 'success')
    print(f"\n  Success: {success_count}/{len(results)} methods")

    return success_count > 0


def main():
    """主测试流程"""
    print_header("MCP Integration Test")

    results = {}

    # 测试 1: 直接调用
    results["mcp_direct"] = test_mcp_scraper_direct()

    # 测试 2: 工具包装器
    results["mcp_wrapper"] = test_mcp_tool_wrapper()

    # 测试 3: ToolManager 集成
    results["tool_manager"] = test_tool_manager_integration()

    # 测试 4: 对比测试
    results["comparison"] = test_fetch_comparison()

    # 总结
    print_header("Test Summary")
    for name, result in results.items():
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} {name}")

    # 建议
    if all(results.values()):
        print("\n✓ 所有测试通过! MCP 已成功集成到项目")
        print("\n下一步:")
        print("  1. 在 agent.py 中使用 mcp_web_scraper 工具")
        print("  2. 更新 System Prompt 告知 Agent 有新工具可用")
        print("  3. 测试完整的数据收集流程")
    elif results.get("mcp_direct") or results.get("mcp_wrapper"):
        print("\n✓ MCP 基础功能可用，但集成可能需要调整")
    else:
        print("\n✗ MCP 集成失败，请检查依赖安装")

    return all(results.values())


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
