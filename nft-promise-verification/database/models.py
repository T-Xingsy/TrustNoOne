"""
数据模型定义

使用 Pydantic 定义所有数据实体模型
"""

from pydantic import BaseModel, Field, HttpUrl, field_validator
from typing import Optional
from datetime import datetime
from enum import Enum
import uuid


# ==================== 枚举定义 ====================

class PromiseType(str, Enum):
    """承诺类型枚举"""
    AIRDROP = "airdrop"
    FEATURE_DEVELOPMENT = "feature_development"
    PARTNERSHIP = "partnership"
    COMMUNITY_EVENT = "community_event"
    NFT_MINTING = "nft_minting"
    MARKETPLACE_LAUNCH = "marketplace_launch"
    OTHER = "other"


class VerificationStatus(str, Enum):
    """验证状态枚举"""
    PENDING = "pending"
    FULFILLED = "fulfilled"
    UNFULFILLED = "unfulfilled"
    UNVERIFIABLE = "unverifiable"


class StorageType(str, Enum):
    """存储类型枚举"""
    PROMISE_ARCHIVE = "promise_archive"
    VERIFICATION_RESULT = "verification_result"


class StorageStatus(str, Enum):
    """存储状态枚举"""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"


# ==================== 嵌套模型 ====================

class PromiseSource(BaseModel):
    """承诺来源"""
    type: str = Field(..., description="来源类型: twitter/website/whitepaper")
    url: HttpUrl = Field(..., description="来源 URL")
    published_at: datetime = Field(..., description="发布时间")
    metadata: Optional[dict] = Field(None, description="额外元数据")

    model_config = {
        "json_schema_extra": {
            "example": {
                "type": "twitter",
                "url": "https://twitter.com/BoredApeYC/status/1234567890",
                "published_at": "2023-10-15T10:30:00Z",
                "metadata": {"likes": 1500, "retweets": 300}
            }
        }
    }


class ReportDetails(BaseModel):
    """验证报告详情"""
    summary: str = Field(..., description="报告摘要")
    five_dimensions: dict = Field(..., description="五维评分详情")
    promise_analysis: list[dict] = Field(..., description="承诺分析列表")
    recommendations: list[str] = Field(..., description="建议列表")

    model_config = {
        "json_schema_extra": {
            "example": {
                "summary": "该项目画饼指数为 35 分，属于良好水平，轻度画饼。",
                "five_dimensions": {
                    "integrity": {
                        "score": 75,
                        "details": "10 条承诺中有 7 条已兑现，违约率 30%"
                    }
                },
                "promise_analysis": [],
                "recommendations": ["建议关注项目方的国库资金流向"]
            }
        }
    }


# ==================== 主要实体模型 ====================

class NFTProject(BaseModel):
    """NFT 项目实体模型"""
    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="项目唯一标识符"
    )
    name: str = Field(..., min_length=1, max_length=100, description="项目名称")
    twitter_account: Optional[str] = Field(None, description="Twitter 账号")
    website_url: Optional[HttpUrl] = Field(None, description="官网 URL")
    whitepaper_url: Optional[HttpUrl] = Field(None, description="白皮书链接")
    contract_address: Optional[str] = Field(None, description="智能合约地址")
    github_repo: Optional[str] = Field(None, description="GitHub 仓库")
    treasury_address: Optional[str] = Field(None, description="国库地址")
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="创建时间"
    )
    last_verified_at: Optional[datetime] = Field(None, description="最后验证时间")

    @field_validator('twitter_account')
    @classmethod
    def validate_twitter_account(cls, v):
        if v and not v.startswith('@'):
            return f'@{v}'
        return v

    @field_validator('contract_address', 'treasury_address')
    @classmethod
    def validate_ethereum_address(cls, v):
        if v and not v.startswith('0x'):
            raise ValueError('以太坊地址必须以 0x 开头')
        if v and len(v) != 42:
            raise ValueError('以太坊地址长度必须为 42 字符')
        return v

    @field_validator('github_repo')
    @classmethod
    def validate_github_repo(cls, v):
        if v and '/' not in v:
            raise ValueError('GitHub 仓库格式必须为 owner/repo')
        return v


class Promise(BaseModel):
    """承诺实体模型"""
    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="承诺唯一标识符"
    )
    project_id: str = Field(..., description="关联的项目 ID")
    content: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="承诺内容"
    )
    sources: list[PromiseSource] = Field(..., min_length=1, description="来源列表")
    promise_type: PromiseType = Field(..., description="承诺类型")
    target_date: Optional[datetime] = Field(None, description="目标时间")
    verification_status: VerificationStatus = Field(
        default=VerificationStatus.PENDING,
        description="验证状态"
    )
    importance_weight: float = Field(
        default=1.0,
        ge=0.1,
        le=2.0,
        description="重要性权重"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="创建时间"
    )


class VerificationRecord(BaseModel):
    """验证记录实体模型"""
    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="验证记录唯一标识符"
    )
    project_id: str = Field(..., description="关联的项目 ID")
    verification_time: datetime = Field(
        default_factory=datetime.utcnow,
        description="验证时间"
    )
    promise_breaking_index: float = Field(..., ge=0, le=100, description="画饼指数")
    integrity_score: float = Field(..., ge=0, le=100, description="诚信审计得分")
    fairness_score: float = Field(..., ge=0, le=100, description="公平性审计得分")
    activity_score: float = Field(..., ge=0, le=100, description="开发力审计得分")
    stability_score: float = Field(..., ge=0, le=100, description="财务稳定性得分")
    momentum_score: float = Field(..., ge=0, le=100, description="社区动能得分")
    total_promises: int = Field(..., ge=0, description="承诺总数")
    fulfilled_count: int = Field(..., ge=0, description="已兑现数量")
    unfulfilled_count: int = Field(..., ge=0, description="未兑现数量")
    unverifiable_count: int = Field(..., ge=0, description="无法验证数量")
    report_details: ReportDetails = Field(..., description="详细报告内容")

    @field_validator('total_promises')
    @classmethod
    def validate_total_promises(cls, v, info):
        """验证承诺总数等于各状态数量之和"""
        fulfilled = info.data.get('fulfilled_count', 0)
        unfulfilled = info.data.get('unfulfilled_count', 0)
        unverifiable = info.data.get('unverifiable_count', 0)
        if v != fulfilled + unfulfilled + unverifiable:
            raise ValueError('承诺总数必须等于各状态数量之和')
        return v


class PrivacyStorageRecord(BaseModel):
    """隐私存储记录实体模型"""
    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="存储记录唯一标识符"
    )
    project_id: str = Field(..., description="关联的项目 ID")
    storage_type: StorageType = Field(..., description="存储类型")
    storage_time: datetime = Field(
        default_factory=datetime.utcnow,
        description="存储时间"
    )
    tx_hash: Optional[str] = Field(None, description="链上交易哈希")
    privacy_address: Optional[str] = Field(None, description="隐私接收地址")
    data_hash: str = Field(
        ...,
        min_length=64,
        max_length=64,
        description="数据摘要 (SHA256)"
    )
    storage_status: StorageStatus = Field(
        default=StorageStatus.PENDING,
        description="存储状态"
    )

    @field_validator('tx_hash')
    @classmethod
    def validate_tx_hash(cls, v):
        if v and not v.startswith('0x'):
            raise ValueError('交易哈希必须以 0x 开头')
        if v and len(v) != 66:
            raise ValueError('交易哈希长度必须为 66 字符')
        return v

    @field_validator('privacy_address')
    @classmethod
    def validate_privacy_address(cls, v):
        if v and not v.startswith('0x'):
            raise ValueError('隐私地址必须以 0x 开头')
        if v and len(v) != 42:
            raise ValueError('隐私地址长度必须为 42 字符')
        return v
