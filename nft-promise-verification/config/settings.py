"""
环境变量加载模块

使用 pydantic-settings 加载和验证环境变量
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional


class Settings(BaseSettings):
    """环境变量配置"""

    # LLM 配置
    anthropic_api_key: Optional[str] = Field(None, alias="ANTHROPIC_API_KEY")
    openai_api_key: Optional[str] = Field(None, alias="OPENAI_API_KEY")
    llm_model: str = Field("claude-3-5-sonnet-20241022", alias="LLM_MODEL")

    # 区块链配置
    eth_mainnet_rpc_url: Optional[str] = Field(None, alias="ETH_MAINNET_RPC_URL")
    eth_sepolia_rpc_url: Optional[str] = Field(None, alias="ETH_SEPOLIA_RPC_URL")

    # DDC-Market-SDK 配置
    bsn_ddc_gateway_url: Optional[str] = Field(None, alias="BSN_DDC_GATEWAY_URL")
    bsn_ddc_api_key: Optional[str] = Field(None, alias="BSN_DDC_API_KEY")

    # 数据库配置
    database_path: str = Field("./database/promise_breaker.db", alias="DATABASE_PATH")

    # 日志配置
    log_level: str = Field("INFO", alias="LOG_LEVEL")
    log_format: str = Field("json", alias="LOG_FORMAT")

    # API 服务配置
    api_port: int = Field(8000, alias="API_PORT")
    api_host: str = Field("0.0.0.0", alias="API_HOST")

    # 开发配置
    dev_mode: bool = Field(True, alias="DEV_MODE")
    debug: bool = Field(False, alias="DEBUG")

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False
    }


# 全局配置实例
settings = Settings()
