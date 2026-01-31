"""
日志配置模块

使用 structlog 配置结构化日志
"""

import structlog
import logging
import sys
from typing import Any


def configure_logging(log_level: str = "INFO", log_format: str = "json") -> None:
    """
    配置日志系统

    Args:
        log_level: 日志级别 (DEBUG, INFO, WARNING, ERROR)
        log_format: 日志格式 (json, console)
    """
    # 设置标准库 logging 级别
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, log_level.upper())
    )

    # 配置 structlog
    processors = [
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    # 根据格式选择渲染器
    if log_format == "json":
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer())

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> Any:
    """获取 logger 实例"""
    return structlog.get_logger(name)


# 别名，保持向后兼容
setup_logging = configure_logging
