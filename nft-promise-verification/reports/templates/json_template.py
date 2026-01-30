"""
JSON 格式报告模板

生成结构化的 JSON 格式报告
"""
import json
from typing import Dict, Any


class JSONTemplate:
    """JSON 格式报告模板"""

    @staticmethod
    def render(report: Dict[str, Any], indent: int = 2) -> str:
        """
        渲染 JSON 格式报告

        Args:
            report: 报告数据
            indent: 缩进空格数

        Returns:
            JSON 格式的报告字符串
        """
        return json.dumps(report, ensure_ascii=False, indent=indent)

    @staticmethod
    def render_compact(report: Dict[str, Any]) -> str:
        """
        渲染紧凑的 JSON 格式报告（无缩进）

        Args:
            report: 报告数据

        Returns:
            紧凑的 JSON 格式报告字符串
        """
        return json.dumps(report, ensure_ascii=False, separators=(',', ':'))
