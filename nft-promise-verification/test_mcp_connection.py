#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP 连接测试脚本

测试 Fetcher MCP (mcp-server-fetch) 是否可用
用于网页抓取，支持动态 JavaScript 内容
"""
import asyncio
import sys
import json
from pathlib import Path

# Windows 控制台编码修复
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')


# 尝试导入 MCP 相关包
try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    MCP_AVAILABLE = True
except ImportError as e:
    MCP_AVAILABLE = False
    MCP_IMPORT_ERROR = str(e)


def print_header(title: str):
    """打印标题"""
    print("\n" + "=" * 60)
    print(f" {title}")
    print("=" * 60)


def print_test(name: str):
    """打印测试名称"""
    print(f"\n[Test: {name}]")
    print("-" * 50)


async def test_fetcher_mcp():
    """测试 Fetcher MCP 连接"""

    print_header("Fetcher MCP Connection Test")

    # 1. 检查包是否安装
    print_test("1. Check MCP Packages")
    if MCP_AVAILABLE:
        print("[OK] mcp package is installed")
    else:
        print(f"[FAIL] mcp package not found: {MCP_IMPORT_ERROR}")
        print("\n请运行: pip install mcp")
        return False

    # 检查 mcp-server-fetch (Python 模块)
    try:
        import subprocess
        result = subprocess.run(
            ["python", "-m", "mcp_server_fetch", "--help"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0 or "web requests" in result.stdout:
            print("[OK] mcp-server-fetch (Python module) is available")
        else:
            print("[WARN] mcp-server-fetch might have issues")
    except Exception as e:
        print(f"[WARN] Could not verify mcp-server-fetch: {e}")

    # 2. 测试连接到 Fetcher MCP 服务器 (Python 模块方式)
    print_test("2. Connect to Fetcher MCP Server (Python module)")

    server_params = StdioServerParameters(
        command=sys.executable,  # 使用当前 Python 解释器
        args=["-m", "mcp_server_fetch", "--user-agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"],
        env=None
    )

    try:
        async with stdio_client(server_params) as streams:
            async with ClientSession(streams[0], streams[1]) as session:
                # 初始化会话
                await session.initialize()

                # 列出可用工具
                tools = await session.list_tools()
                print(f"[OK] Connected! Found {len(tools.tools)} tools:")

                for tool in tools.tools:
                    print(f"      - {tool.name}: {tool.description[:60]}...")

                # 3. 测试抓取 Azuki.com
                print_test("3. Fetch Azuki.com (Dynamic Content)")

                try:
                    result = await session.call_tool(
                        "fetch",
                        arguments={
                            "url": "https://www.azuki.com",
                            "outputFormat": "markdown"
                        }
                    )

                    # 获取内容
                    content = ""
                    for item in result.content:
                        if hasattr(item, "text"):
                            content += item.text
                        elif isinstance(item, str):
                            content += item

                    print(f"[OK] Fetched successfully!")
                    print(f"      Content length: {len(content)} characters")
                    print(f"\n      Content preview (first 300 chars):")
                    print("      " + "-" * 50)
                    print("      " + content[:300].replace("\n", "\n      "))
                    print("      ...")

                except Exception as e:
                    print(f"[FAIL] Fetch failed: {e}")
                    return False

                # 4. 测试抓取 GitHub README
                print_test("4. Fetch GitHub README (Static Content)")

                try:
                    result = await session.call_tool(
                        "fetch",
                        arguments={
                            "url": "https://github.com/XSpoonAi/spoon-toolkit",
                            "outputFormat": "markdown"
                        }
                    )

                    content = ""
                    for item in result.content:
                        if hasattr(item, "text"):
                            content += item.text
                        elif isinstance(item, str):
                            content += item

                    print(f"[OK] Fetched successfully!")
                    print(f"      Content length: {len(content)} characters")

                    # 检查关键内容
                    if "Spoon" in content or "Toolkit" in content:
                        print("[OK] Content verification passed")

                except Exception as e:
                    print(f"[FAIL] Fetch failed: {e}")

                print_header("Test Summary")
                print("[PASS] MCP connection is working!")
                print("\n下一步: 集成到 SpoonReactAI Agent")
                return True

    except Exception as e:
        print(f"[FAIL] Connection failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_playwright_approach():
    """测试直接使用 Playwright 方式（备用方案）"""
    print_header("Playwright Direct Test (Fallback)")

    print_test("Direct Playwright Import")
    try:
        from playwright.async_api import async_playwright
        print("[OK] playwright is installed")

        print_test("Fetch Azuki.com with Playwright")
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto("https://www.azuki.com", timeout=30000)
            content = await page.inner_text("body")
            await browser.close()

            print(f"[OK] Fetched {len(content)} characters")
            print(f"      Preview: {content[:200]}...")
            return True

    except ImportError:
        print("[WARN] playwright not installed")
        print("       Install with: pip install playwright")
        print("       Then run: playwright install chromium")
        return False
    except Exception as e:
        print(f"[FAIL] {e}")
        return False


async def main():
    """主测试流程"""
    results = {}

    # 测试 MCP 方式
    results["mcp_fetch"] = await test_fetcher_mcp()

    # 如果 MCP 失败，测试 Playwright 直接方式
    if not results.get("mcp_fetch"):
        print("\n" + "!" * 60)
        print("MCP test failed, trying direct Playwright approach...")
        print("!" * 60)
        results["playwright_direct"] = await test_playwright_approach()

    # 最终总结
    print_header("Final Results")
    for name, result in results.items():
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} {name}")

    if any(results.values()):
        print("\n✓ 至少有一种方式可用，可以集成到项目")
    else:
        print("\n✗ 所有测试失败，需要安装依赖")

    return any(results.values())


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
