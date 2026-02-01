#!/usr/bin/env python3
"""
测试 Skill 适配器集成

验证:
1. TwitterSkillAdapter 是否能正常工作
2. GitHubSkillAdapter 是否能正常工作
3. ExcelSkillAdapter 是否能正常工作
4. Fallback 机制是否生效
"""
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from tools.skill_adapters import (
    TwitterSkillAdapter,
    GitHubSkillAdapter,
    ExcelSkillAdapter
)
from tools_config import register_tools
from llm_config import LLMManager
from config.settings import Settings
import structlog

logger = structlog.get_logger(__name__)


def test_twitter_adapter():
    """测试 Twitter Skill 适配器"""
    print("\n" + "="*60)
    print("Testing TwitterSkillAdapter")
    print("="*60)

    try:
        adapter = TwitterSkillAdapter()

        # 检查可用性
        if adapter.skill_available:
            print("[OK] bird skill is available")
        else:
            print("[INFO] bird skill not available, will use fallback (snscrape)")

        # 尝试运行（使用少量数据）
        print("\nTesting with limited data (5 tweets)...")
        result = adapter._run("elonmusk", max_tweets=5)

        if result and len(result) > 0:
            print(f"[SUCCESS] Got {len(result)} tweets")
            print(f"Sample tweet: {result[0].get('text', '')[:100]}...")
            return True
        else:
            print("[WARNING] No tweets returned")
            return False

    except Exception as e:
        print(f"[ERROR] Twitter adapter test failed: {str(e)}")
        return False


def test_github_adapter():
    """测试 GitHub Skill 适配器"""
    print("\n" + "="*60)
    print("Testing GitHubSkillAdapter")
    print("="*60)

    try:
        adapter = GitHubSkillAdapter()

        # 检查可用性
        if adapter.skill_available:
            print("[OK] gh CLI is available")
        else:
            print("[INFO] gh CLI not available")
            print("       Install from: https://cli.github.com/")
            return False

        # 尝试运行
        print("\nTesting GitHub commits query...")
        result = adapter._run(
            owner="facebook",
            repo="react",
            data_type="commits",
            limit=5
        )

        if result and len(result) > 0:
            print(f"[SUCCESS] Got {len(result)} commits")
            print(f"Sample commit: {result[0].get('message', '')[:100]}...")
            return True
        else:
            print("[WARNING] No commits returned")
            return False

    except Exception as e:
        print(f"[ERROR] GitHub adapter test failed: {str(e)}")
        return False


def test_excel_adapter():
    """测试 Excel Skill 适配器"""
    print("\n" + "="*60)
    print("Testing ExcelSkillAdapter")
    print("="*60)

    try:
        adapter = ExcelSkillAdapter()

        # 检查可用性
        if adapter.skill_available:
            print("[OK] openpyxl is available")
        else:
            print("[INFO] openpyxl not available")
            print("       Install: pip install openpyxl")
            return False

        # 测试数据
        test_data = {
            "project_name": "Test Project",
            "verification_date": "2026-02-01",
            "promise_breaking_index": 65,
            "five_dimensions": {
                "integrity": {"score": 70},
                "fairness": {"score": 60},
                "activity": {"score": 75}
            },
            "verification_results": [
                {
                    "promise_content": "Test promise 1",
                    "promise_type": "airdrop",
                    "verification_status": "FULFILLED",
                    "evidence": "Test evidence"
                }
            ]
        }

        # 生成测试报告
        output_path = project_root / "test_output.xlsx"
        print(f"\nGenerating test report to: {output_path}")

        result_path = adapter._run(
            data=test_data,
            output_path=str(output_path),
            include_charts=False
        )

        if Path(result_path).exists():
            print(f"[SUCCESS] Excel report generated: {result_path}")
            return True
        else:
            print("[ERROR] Excel file was not created")
            return False

    except Exception as e:
        print(f"[ERROR] Excel adapter test failed: {str(e)}")
        return False


def test_tool_registration():
    """测试工具注册"""
    print("\n" + "="*60)
    print("Testing Tool Registration")
    print("="*60)

    try:
        # 初始化
        settings = Settings()
        llm_manager = LLMManager(settings)
        tool_manager = register_tools(llm_manager)

        # 检查注册的工具
        tools = tool_manager.tools
        print(f"\n[SUCCESS] Registered {len(tools)} tools")

        # 列出工具名称
        tool_names = [tool.name for tool in tools]
        print("\nRegistered tools:")
        for name in tool_names:
            print(f"  - {name}")

        # 检查是否包含 skill 适配器
        skill_tools = [name for name in tool_names if "skill" in name.lower() or name in ["twitter_scraper", "github_scraper", "excel_generator"]]

        if skill_tools:
            print(f"\n[OK] Found {len(skill_tools)} skill-based tools:")
            for name in skill_tools:
                print(f"  - {name}")
        else:
            print("\n[INFO] No skill-based tools found (using original implementations)")

        return True

    except Exception as e:
        print(f"[ERROR] Tool registration test failed: {str(e)}")
        return False


def main():
    """运行所有测试"""
    print("\n" + "="*60)
    print("NFT Promise Verification - Skill Adapters Test")
    print("="*60)

    results = {}

    # 运行测试
    results["twitter"] = test_twitter_adapter()
    results["github"] = test_github_adapter()
    results["excel"] = test_excel_adapter()
    results["registration"] = test_tool_registration()

    # 总结
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    print(f"\nPassed: {passed}/{total}")

    for test_name, result in results.items():
        status = "[PASS]" if result else "[FAIL]"
        print(f"  {status} {test_name}")

    if passed == total:
        print("\n[SUCCESS] All tests passed!")
        return 0
    elif passed > 0:
        print(f"\n[WARNING] Some tests failed ({total - passed} failed)")
        return 1
    else:
        print("\n[ERROR] All tests failed")
        return 1


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\nTest cancelled")
        sys.exit(130)
    except Exception as e:
        logger.error("Test execution failed", error=str(e))
        sys.exit(1)
