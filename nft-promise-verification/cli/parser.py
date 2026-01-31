"""
CLI 命令解析模块

使用 argparse 解析命令行参数
支持 collect, list, show, export, verify, version, help 命令
"""
import argparse
import sys
from typing import List, Optional


class CLIParser:
    """CLI 命令解析器"""

    def __init__(self):
        """初始化解析器"""
        self.parser = self._create_parser()

    def _create_parser(self) -> argparse.ArgumentParser:
        """创建主解析器"""
        parser = argparse.ArgumentParser(
            prog="promise-breaker",
            description="NFT 项目承诺验证系统（画饼识破）",
            formatter_class=argparse.RawDescriptionHelpFormatter
        )

        parser.add_argument(
            "--version",
            action="version",
            version="promise-breaker 0.1.0"
        )

        # 创建子命令
        subparsers = parser.add_subparsers(
            dest="command",
            help="可用命令"
        )

        # collect 命令
        self._add_collect_command(subparsers)

        # list 命令
        self._add_list_command(subparsers)

        # show 命令
        self._add_show_command(subparsers)

        # export 命令
        self._add_export_command(subparsers)

        # verify 命令
        self._add_verify_command(subparsers)

        return parser

    def _add_collect_command(self, subparsers):
        """添加 collect 命令"""
        collect_parser = subparsers.add_parser(
            "collect",
            help="收集项目承诺"
        )

        collect_parser.add_argument(
            "--name",
            required=True,
            help="项目名称"
        )

        collect_parser.add_argument(
            "--twitter",
            help="Twitter 用户名"
        )

        collect_parser.add_argument(
            "--website",
            help="官网 URL"
        )

        collect_parser.add_argument(
            "--max-tweets",
            type=int,
            default=100,
            help="最大推文数（默认: 100）"
        )

        collect_parser.add_argument(
            "--output",
            choices=["table", "json", "markdown"],
            default="table",
            help="输出格式（默认: table）"
        )

    def _add_list_command(self, subparsers):
        """添加 list 命令"""
        list_parser = subparsers.add_parser(
            "list",
            help="列出所有项目"
        )

        list_parser.add_argument(
            "--format",
            choices=["table", "json", "markdown"],
            default="table",
            help="输出格式（默认: table）"
        )

        list_parser.add_argument(
            "--sort",
            choices=["name", "created_at", "promises_count"],
            default="created_at",
            help="排序字段（默认: created_at）"
        )

        list_parser.add_argument(
            "--limit",
            type=int,
            default=20,
            help="最大显示数量（默认: 20）"
        )

    def _add_show_command(self, subparsers):
        """添加 show 命令"""
        show_parser = subparsers.add_parser(
            "show",
            help="显示项目详情"
        )

        show_parser.add_argument(
            "project_id",
            type=str,  # 修复: int -> str (UUID)
            help="项目 ID (UUID)"
        )

        show_parser.add_argument(
            "--format",
            choices=["table", "json", "markdown"],
            default="table",
            help="输出格式（默认: table）"
        )

        show_parser.add_argument(
            "--filter-category",
            help="按类别过滤承诺"
        )

        show_parser.add_argument(
            "--min-confidence",
            type=float,
            default=0.0,
            help="最小置信度阈值（默认: 0.0）"
        )

    def _add_export_command(self, subparsers):
        """添加 export 命令"""
        export_parser = subparsers.add_parser(
            "export",
            help="导出项目数据"
        )

        export_parser.add_argument(
            "project_id",
            type=str,  # 修复: int -> str (UUID)
            help="项目 ID (UUID)"
        )

        export_parser.add_argument(
            "--format",
            choices=["json", "markdown"],
            default="json",
            help="导出格式（默认: json）"
        )

        export_parser.add_argument(
            "--output",
            help="输出文件路径（默认: 输出到标准输出）"
        )


    def _add_verify_command(self, subparsers):
        """添加 verify 命令"""
        verify_parser = subparsers.add_parser(
            "verify",
            help="验证项目承诺"
        )

        verify_parser.add_argument(
            "--project-id",
            required=True,
            help="项目 ID"
        )

        verify_parser.add_argument(
            "--network",
            default="mainnet",
            choices=["mainnet", "sepolia", "goerli"],
            help="区块链网络（默认: mainnet）"
        )

        verify_parser.add_argument(
            "--format",
            choices=["table", "json", "markdown", "text"],
            default="text",
            help="输出格式（默认: text）"
        )

    def parse_args(self, args: Optional[List[str]] = None) -> argparse.Namespace:
        """
        解析命令行参数

        Args:
            args: 参数列表（默认使用 sys.argv）

        Returns:
            解析后的参数对象
        """
        return self.parser.parse_args(args)

    def print_help(self):
        """打印帮助信息"""
        self.parser.print_help()
