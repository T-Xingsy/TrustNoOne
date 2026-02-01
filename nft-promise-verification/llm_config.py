"""
LLM 配置模块

配置和管理 LLM (Claude/GPT-4/DeepSeek) 连接
"""

from typing import Optional
from anthropic import Anthropic
from openai import OpenAI
import os

# 简单日志，避免依赖 structlog
def _log(level, msg, **kwargs):
    print(f"[{level.upper()}] {msg}")


class LLMManager:
    """LLM 管理器"""

    def __init__(self, settings_obj=None):
        self.anthropic_client: Optional[Anthropic] = None
        self.openai_client: Optional[OpenAI] = None
        self.deepseek_client: Optional[OpenAI] = None
        self._initialize_clients()

    def _initialize_clients(self) -> None:
        """初始化 LLM 客户端"""
        # 获取 API keys
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        openai_key = os.getenv("OPENAI_API_KEY")
        deepseek_key = os.getenv("DEEPSEEK_API_KEY")

        # 初始化 Claude 客户端
        if anthropic_key:
            try:
                self.anthropic_client = Anthropic(api_key=anthropic_key)
                _log("info", "Claude client initialized successfully")
            except Exception as e:
                _log("error", f"Failed to initialize Claude client: {e}")

        # 初始化 OpenAI 客户端
        if openai_key:
            try:
                self.openai_client = OpenAI(api_key=openai_key)
                _log("info", "OpenAI client initialized successfully")
            except Exception as e:
                _log("error", f"Failed to initialize OpenAI client: {e}")

        # 初始化 DeepSeek 客户端 (使用 OpenAI 兼容接口)
        if deepseek_key:
            try:
                self.deepseek_client = OpenAI(
                    api_key=deepseek_key,
                    base_url="https://api.deepseek.com"
                )
                _log("info", "DeepSeek client initialized successfully")
            except Exception as e:
                _log("error", f"Failed to initialize DeepSeek client: {e}")

    def get_client(self, model: str = None):
        """
        获取 LLM 客户端

        Args:
            model: 模型名称,默认使用配置中的模型

        Returns:
            LLM 客户端实例
        """
        if model is None:
            model = os.getenv("LLM_MODEL", "gpt-4")

        if "claude" in model.lower():
            if self.anthropic_client is None:
                raise ValueError("Claude client not initialized")
            return self.anthropic_client
        elif "deepseek" in model.lower():
            if self.deepseek_client is None:
                raise ValueError("DeepSeek client not initialized. Please set DEEPSEEK_API_KEY")
            return self.deepseek_client
        elif "gpt" in model.lower():
            if self.openai_client is None:
                raise ValueError("OpenAI client not initialized")
            return self.openai_client
        else:
            # 默认使用 DeepSeek
            if self.deepseek_client:
                return self.deepseek_client
            raise ValueError(f"Unsupported model: {model}")

    def chat(self, prompt: str, model: str = None, **kwargs) -> str:
        """
        发送聊天请求

        Args:
            prompt: 提示词
            model: 模型名称
            **kwargs: 其他参数

        Returns:
            LLM 响应文本
        """
        client = self.get_client(model)

        if model is None:
            model = os.getenv("LLM_MODEL", "deepseek-chat")

        # 判断使用哪种客户端
        if "claude" in model.lower():
            response = client.messages.create(
                model=model,
                max_tokens=kwargs.get("max_tokens", 4096),
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
        else:
            # OpenAI / DeepSeek 兼容格式
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=kwargs.get("max_tokens", 4096),
                temperature=kwargs.get("temperature", 0.7)
            )
            return response.choices[0].message.content


# 全局 LLM 管理器实例
llm_manager = LLMManager()
