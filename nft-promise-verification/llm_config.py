"""
LLM 配置模块

配置和管理 LLM (Claude/GPT-4) 连接
"""

from typing import Optional
from anthropic import Anthropic
from openai import OpenAI

from ..config.settings import settings
from ..utils.logger import get_logger

logger = get_logger(__name__)


class LLMManager:
    """LLM 管理器"""

    def __init__(self):
        self.anthropic_client: Optional[Anthropic] = None
        self.openai_client: Optional[OpenAI] = None
        self._initialize_clients()

    def _initialize_clients(self) -> None:
        """初始化 LLM 客户端"""
        # 初始化 Claude 客户端
        if settings.anthropic_api_key:
            try:
                self.anthropic_client = Anthropic(
                    api_key=settings.anthropic_api_key
                )
                logger.info("Claude client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Claude client: {e}")

        # 初始化 OpenAI 客户端
        if settings.openai_api_key:
            try:
                self.openai_client = OpenAI(
                    api_key=settings.openai_api_key
                )
                logger.info("OpenAI client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {e}")

    def get_client(self, model: str = None):
        """
        获取 LLM 客户端

        Args:
            model: 模型名称,默认使用配置中的模型

        Returns:
            LLM 客户端实例
        """
        if model is None:
            model = settings.llm_model

        if "claude" in model.lower():
            if self.anthropic_client is None:
                raise ValueError("Claude client not initialized")
            return self.anthropic_client
        elif "gpt" in model.lower():
            if self.openai_client is None:
                raise ValueError("OpenAI client not initialized")
            return self.openai_client
        else:
            raise ValueError(f"Unsupported model: {model}")


# 全局 LLM 管理器实例
llm_manager = LLMManager()
