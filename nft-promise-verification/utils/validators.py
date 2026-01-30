"""
输入验证模块

使用 Pydantic 定义用户输入验证 schemas
"""

from pydantic import BaseModel, Field, HttpUrl
from typing import Optional


class ProjectInput(BaseModel):
    """项目输入验证"""
    name: str = Field(..., min_length=1, max_length=100, description="项目名称")
    twitter_account: Optional[str] = Field(None, description="Twitter 账号")
    website_url: Optional[HttpUrl] = Field(None, description="官网 URL")
    whitepaper_url: Optional[HttpUrl] = Field(None, description="白皮书链接")
    contract_address: Optional[str] = Field(None, description="智能合约地址")
    github_repo: Optional[str] = Field(None, description="GitHub 仓库")
    treasury_address: Optional[str] = Field(None, description="国库地址")
