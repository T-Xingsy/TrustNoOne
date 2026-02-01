#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
安装推荐的外部 Skills

该脚本会安装以下 skills:
1. bird - Twitter 数据抓取
2. github - GitHub 数据查询 (使用 gh CLI)
3. excel - Excel 报告生成

运行方式:
    python scripts/install_skills.py
"""
import subprocess
import sys
import os
from pathlib import Path

# 设置 Windows 控制台编码
if sys.platform == "win32":
    os.system("chcp 65001 > nul 2>&1")

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import structlog

logger = structlog.get_logger(__name__)


def run_command(cmd: list, description: str) -> bool:
    """
    运行命令并返回是否成功

    Args:
        cmd: 命令列表
        description: 命令描述

    Returns:
        是否成功
    """
    logger.info(f"执行: {description}", command=" ".join(cmd))

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300  # 5 分钟超时
        )

        if result.returncode == 0:
            logger.info(f"✓ {description} 成功")
            if result.stdout:
                print(result.stdout)
            return True
        else:
            logger.error(
                f"✗ {description} 失败",
                error=result.stderr
            )
            return False

    except subprocess.TimeoutExpired:
        logger.error(f"✗ {description} 超时")
        return False
    except Exception as e:
        logger.error(f"✗ {description} 异常", error=str(e))
        return False


def check_npm() -> bool:
    """检查 npm 是否可用"""
    try:
        result = subprocess.run(
            ["npm", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            logger.info(f"npm 版本: {result.stdout.strip()}")
            return True
        return False
    except Exception:
        return False


def check_gh_cli() -> bool:
    """检查 gh CLI 是否可用"""
    try:
        result = subprocess.run(
            ["gh", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            logger.info(f"gh CLI 版本: {result.stdout.strip()}")
            return True
        return False
    except Exception:
        return False


def install_skills():
    """安装所有推荐的 skills"""
    print("\n" + "="*60)
    print("NFT Promise Verification - Skills Installation")
    print("="*60 + "\n")

    # 检查依赖
    print("1. Checking dependencies...")
    has_npm = check_npm()
    has_gh = check_gh_cli()

    if not has_npm:
        logger.error(
            "npm not installed",
            hint="Please install Node.js and npm: https://nodejs.org/"
        )
        return False

    if not has_gh:
        logger.warning(
            "gh CLI not installed",
            hint="GitHub skill requires gh CLI: https://cli.github.com/"
        )
        print("  Skipping GitHub skill installation...\n")
    else:
        print("  [OK] Dependencies check passed\n")

    # 安装 skills
    print("2. Installing Skills...")

    skills_to_install = []

    # bird skill (Twitter)
    print("\n[1/3] Installing bird skill (Twitter data scraping)...")
    if run_command(
        ["npx", "clawdhub@latest", "install", "bird"],
        "bird skill installation"
    ):
        skills_to_install.append("bird")
    else:
        print("  [WARNING] bird skill installation failed, will use fallback")

    # github skill (如果有 gh CLI)
    if has_gh:
        print("\n[2/3] Installing github skill (GitHub data query)...")
        if run_command(
            ["npx", "clawdhub@latest", "install", "github"],
            "github skill installation"
        ):
            skills_to_install.append("github")
        else:
            print("  [WARNING] github skill installation failed, will use fallback")
    else:
        print("\n[2/3] Skipping github skill (gh CLI not installed)")

    # excel skill
    print("\n[3/3] Installing excel skill (Excel report generation)...")
    if run_command(
        ["npx", "clawdhub@latest", "install", "excel"],
        "excel skill installation"
    ):
        skills_to_install.append("excel")
    else:
        print("  [WARNING] excel skill installation failed, will use openpyxl")

    # 总结
    print("\n" + "="*60)
    print("Installation Summary")
    print("="*60)

    if skills_to_install:
        print(f"\n[SUCCESS] Successfully installed {len(skills_to_install)} skills:")
        for skill in skills_to_install:
            print(f"  - {skill}")
    else:
        print("\n[WARNING] No skills were installed")
        print("  The project will run with existing implementations")

    print("\nNotes:")
    print("  - bird skill: For Twitter data scraping")
    print("  - github skill: For GitHub activity tracking (requires gh CLI)")
    print("  - excel skill: For Excel report generation (using openpyxl)")
    print("\nNote: Even if skill installation fails, the project will work normally.")
    print("      Skill adapters will automatically fallback to original implementations\n")

    return True


if __name__ == "__main__":
    try:
        success = install_skills()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nInstallation cancelled")
        sys.exit(130)
    except Exception as e:
        logger.error("Installation script failed", error=str(e))
        sys.exit(1)
