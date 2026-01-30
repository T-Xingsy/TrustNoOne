"""
报告模板模块

提供 Table、JSON、Markdown 三种格式的报告模板
"""
from .table_template import TableTemplate
from .json_template import JSONTemplate
from .markdown_template import MarkdownTemplate

__all__ = [
    "TableTemplate",
    "JSONTemplate",
    "MarkdownTemplate"
]
