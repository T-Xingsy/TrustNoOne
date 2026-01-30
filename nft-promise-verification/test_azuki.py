#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Azuki 项目测试脚本

独立测试脚本，不影响原有代码
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
import structlog

# 加载环境变量
load_dotenv()

# 配置日志
structlog.configure(
    processors=[
        structlog.dev.ConsoleRenderer()  # 使用控制台渲染器，更简单
    ],
    logger_factory=structlog.PrintLoggerFactory(),
)
logger = structlog.get_logger(__name__)


def test_deepseek_connection():
    """测试 DeepSeek 连接"""
    from llm_config import LLMManager

    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        logger.error("DEEPSEEK_API_KEY 未设置！")
        return False

    try:
        llm = LLMManager()
        response = llm.chat(
            prompt="请用一句话介绍 Azuki NFT 项目。",
            model="deepseek-chat",
            max_tokens=100
        )
        logger.info("DeepSeek connected successfully", response=response)
        print(f"\n[OK] DeepSeek Response: {response}\n")
        return True
    except Exception as e:
        logger.error("DeepSeek 连接失败", error=str(e))
        return False


def test_promise_extractor():
    """测试承诺提取"""
    from llm_config import LLMManager

    test_text = """
    Azuki 官方宣布:
    1. 将在 2024 年 Q1 空投 10000 个 NFT 给社区
    2. 锁定 500 ETH 用于国库
    3. GitHub 仓库将保持每月至少 20 次提交
    """

    try:
        llm = LLMManager()
        prompt = f"""请从以下文本中提取 NFT 项目承诺，以 JSON 格式输出:

文本:
{test_text}

输出格式:
[
  {{"content": "承诺内容", "type": "承诺类型", "target": "目标"}}
]
"""

        response = llm.chat(prompt=prompt, model="deepseek-chat", max_tokens=500)
        logger.info("Promise extraction test", response=response)
        print(f"[OK] Extracted Promises:\n{response}\n")
        return True
    except Exception as e:
        logger.error("承诺提取失败", error=str(e))
        return False


def test_etherscan_connection():
    """测试 Etherscan 连接"""
    from external.etherscan_client import analyze_address

    # Azuki 官方合约地址
    contract_address = "0xED5AF388653567Af2F388E6224dC7C4b3241C544"

    api_key = os.getenv("ETHERSCAN_API_KEY")
    if not api_key:
        logger.warning("ETHERSCAN_API_KEY 未设置，跳过链上数据测试")
        return None

    try:
        result = analyze_address(address=contract_address, chain="ethereum")
        logger.info(
            "Etherscan connected successfully",
            address=contract_address,
            balance=result.get("balance", {}).get("native", 0)
        )
        print(f"[OK] Contract Balance: {result.get('balance', {}).get('native', 0)} ETH\n")
        return True
    except Exception as e:
        logger.error("Etherscan 连接失败", error=str(e))
        return False


def test_opensea_connection():
    """测试 OpenSea 连接"""
    from external.opensea_client import get_collection_data

    api_key = os.getenv("OPENSEA_API_KEY")
    if not api_key:
        logger.warning("OPENSEA_API_KEY 未设置，跳过 OpenSea 测试")
        return None

    try:
        result = get_collection_data(collection_slug="azuki", chain="ethereum")
        logger.info("OpenSea connected successfully", slug="azuki")
        print(f"[OK] OpenSea data retrieved\n")
        return True
    except Exception as e:
        logger.error("OpenSea 连接失败", error=str(e))
        return False


def main():
    """主测试流程"""
    print("\n" + "="*60)
    print(" Azuki NFT Promise Verification - Test Script")
    print("="*60 + "\n")

    # 检查环境变量
    deepseek_key = os.getenv("DEEPSEEK_API_KEY")
    etherscan_key = os.getenv("ETHERSCAN_API_KEY")

    print("[Environment Check]")
    print(f"  - DEEPSEEK_API_KEY: {'[OK] Set' if deepseek_key else '[X] Not set'}")
    print(f"  - ETHERSCAN_API_KEY: {'[OK] Set' if etherscan_key else '[X] Not set'}")
    print()

    results = {}

    # 1. 测试 DeepSeek
    print("[Test 1: DeepSeek Connection]")
    print("-" * 40)
    results["deepseek"] = test_deepseek_connection()

    # 2. 测试承诺提取
    if results.get("deepseek"):
        print("\n[Test 2: Promise Extraction]")
        print("-" * 40)
        results["promise_extractor"] = test_promise_extractor()

    # 3. 测试 Etherscan
    print("\n[Test 3: Etherscan On-chain Data]")
    print("-" * 40)
    results["etherscan"] = test_etherscan_connection()

    # 4. 测试 OpenSea
    print("\n[Test 4: OpenSea Market Data]")
    print("-" * 40)
    results["opensea"] = test_opensea_connection()

    # 总结
    print("\n" + "="*60)
    print(" Test Summary")
    print("="*60)

    for name, result in results.items():
        if result is True:
            print(f"[PASS] {name}")
        elif result is False:
            print(f"[FAIL] {name}")
        else:
            print(f"[SKIP] {name}")

    print("\nTip: Set these API Keys for full testing:")
    print("  - DEEPSEEK_API_KEY")
    print("  - ETHERSCAN_API_KEY")
    print("  - OPENSEA_API_KEY (optional)")
    print()


if __name__ == "__main__":
    main()
