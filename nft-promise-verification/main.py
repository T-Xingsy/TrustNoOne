#!/usr/bin/env python3
"""
NFT 项目承诺验证系统（画饼识破）

CLI 主入口
"""
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

import structlog
from dotenv import load_dotenv

from cli.parser import CLIParser
from cli.commands import CollectCommand, ListCommand, ShowCommand, ExportCommand, VerifyCommand
from cli.formatters import get_formatter
from config.settings import Settings
from llm_config import LLMManager
from tools_config import register_tools
from agent import VerificationAgent
from database.db import DatabaseManager
from reports.report_generator import ReportGenerator
from utils.logger import setup_logging


def main():
    """主函数"""
    # 加载环境变量
    env_path = project_root / "config" / ".env"
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
    load_dotenv()

    # 设置日志
    setup_logging()
    logger = structlog.get_logger(__name__)

    try:
        # 解析命令行参数
        parser = CLIParser()
        args = parser.parse_args()

        if not args.command:
            parser.print_help()
            sys.exit(0)

        # 初始化配置
        settings = Settings()

        # 初始化组件
        llm_manager = LLMManager(settings)
        tool_manager = register_tools(llm_manager)
        db_manager = DatabaseManager(settings.database_path)
        agent = VerificationAgent(llm_manager, tool_manager, db_manager)
        report_generator = ReportGenerator()

        # 执行命令
        result = None

        if args.command == "collect":
            command = CollectCommand(agent, db_manager)
            result = command.execute(args)
            output_format = args.output

        elif args.command == "list":
            command = ListCommand(db_manager)
            result = command.execute(args)
            output_format = args.format

        elif args.command == "show":
            command = ShowCommand(db_manager, agent)
            result = command.execute(args)
            output_format = args.format

        elif args.command == "export":
            command = ExportCommand(db_manager, agent, report_generator)
            result = command.execute(args)
            output_format = args.format

        elif args.command == "verify":
            command = VerifyCommand(agent, db_manager, report_generator)
            result = command.execute(args)
            output_format = args.format

        else:
            logger.error(f"未知命令: {args.command}")
            sys.exit(1)

        # 格式化输出
        if result:
            # verify 命令的特殊处理
            if args.command == "verify" and output_format == "text":
                # 使用 ReportGenerator 的文本格式化方法
                report = result.get("report", {})
                output = report_generator.format_report_as_text(report)
                print(output)
            else:
                formatter = get_formatter(output_format)
                output = formatter.format(result)
                print(output)

        sys.exit(0)

    except KeyboardInterrupt:
        logger.info("用户中断")
        sys.exit(130)

    except Exception as e:
        logger.error(f"执行失败: {str(e)}", error=str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
