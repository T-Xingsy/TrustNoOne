# Data Model: NFT 项目承诺验证系统

**Feature**: 001-nft-promise-verification
**Date**: 2026-01-30
**Related**: [spec.md](./spec.md) | [plan.md](./plan.md) | [research.md](./research.md)

---

## Overview

本文档定义了 NFT 项目承诺验证系统的核心数据模型，包括实体定义、字段规范、关系映射和验证规则。所有数据模型遵循项目宪法的不可变性原则和类型安全要求。

---

## 1. NFT Project (NFT 项目)

### 实体描述
代表一个 NFT 项目的基本信息，作为系统的核心实体。

### 字段定义

| 字段名 | 类型 | 必填 | 默认值 | 描述 | 验证规则 |
|--------|------|------|--------|------|----------|
| `id` | UUID | ✅ | auto | 项目唯一标识符 | UUID v4 格式 |
| `name` | String | ✅ | - | 项目名称 | 长度 1-100 字符 |
| `twitter_account` | String | ❌ | null | Twitter 账号 | 格式: @username 或 username |
| `website_url` | URL | ❌ | null | 官网 URL | 有效的 HTTP/HTTPS URL |
| `whitepaper_url` | URL | ❌ | null | 白皮书链接 | 有效的 HTTP/HTTPS URL 或 IPFS |
| `contract_address` | Address | ❌ | null | 智能合约地址 | 有效的以太坊地址（0x...） |
| `github_repo` | String | ❌ | null | GitHub 仓库 | 格式: owner/repo |
| `treasury_address` | Address | ❌ | null | 国库地址 | 有效的以太坊地址（0x...） |
| `created_at` | Timestamp | ✅ | now() | 创建时间 | ISO 8601 格式 |
| `last_verified_at` | Timestamp | ❌ | null | 最后验证时间 | ISO 8601 格式 |

### Pydantic 模型定义

```python
from pydantic import BaseModel, Field, HttpUrl, validator
from typing import Optional
from datetime import datetime
import uuid

class NFTProject(BaseModel):
    """NFT 项目实体模型"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="项目唯一标识符")
    name: str = Field(..., min_length=1, max_length=100, description="项目名称")
    twitter_account: Optional[str] = Field(None, description="Twitter 账号")
    website_url: Optional[HttpUrl] = Field(None, description="官网 URL")
    whitepaper_url: Optional[HttpUrl] = Field(None, description="白皮书链接")
    contract_address: Optional[str] = Field(None, description="智能合约地址")
    github_repo: Optional[str] = Field(None, description="GitHub 仓库")
    treasury_address: Optional[str] = Field(None, description="国库地址")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="创建时间")
    last_verified_at: Optional[datetime] = Field(None, description="最后验证时间")

    @validator('twitter_account')
    def validate_twitter_account(cls, v):
        if v and not v.startswith('@'):
            return f'@{v}'
        return v

    @validator('contract_address', 'treasury_address')
    def validate_ethereum_address(cls, v):
        if v and not v.startswith('0x'):
            raise ValueError('以太坊地址必须以 0x 开头')
        if v and len(v) != 42:
            raise ValueError('以太坊地址长度必须为 42 字符')
        return v

    @validator('github_repo')
    def validate_github_repo(cls, v):
        if v and '/' not in v:
            raise ValueError('GitHub 仓库格式必须为 owner/repo')
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "name": "Bored Ape Yacht Club",
                "twitter_account": "@BoredApeYC",
                "website_url": "https://boredapeyachtclub.com",
                "contract_address": "0xBC4CA0EdA7647A8aB7C2061c2E118A18a936f13D",
                "github_repo": "BoredApeYC/bayc-contracts",
                "treasury_address": "0x1234567890123456789012345678901234567890",
                "created_at": "2024-01-29T10:00:00Z"
            }
        }
```

### 关系
- 一对多: `NFTProject` → `Promise` (一个项目有多个承诺)
- 一对多: `NFTProject` → `VerificationRecord` (一个项目有多次验证记录)
- 一对多: `NFTProject` → `PrivacyStorageRecord` (一个项目有多次隐私存储记录)

---

## 2. Promise (承诺)

### 实体描述
代表项目方做出的一个公开承诺，包含承诺内容、来源、类型和验证状态。

### 字段定义

| 字段名 | 类型 | 必填 | 默认值 | 描述 | 验证规则 |
|--------|------|------|--------|------|----------|
| `id` | UUID | ✅ | auto | 承诺唯一标识符 | UUID v4 格式 |
| `project_id` | UUID | ✅ | - | 关联的项目 ID | 外键: NFTProject.id |
| `content` | String | ✅ | - | 承诺内容 | 长度 1-1000 字符 |
| `sources` | List[Source] | ✅ | - | 来源列表 | 至少包含一个来源 |
| `promise_type` | Enum | ✅ | - | 承诺类型 | 见 PromiseType 枚举 |
| `target_date` | Date | ❌ | null | 目标时间 | ISO 8601 日期格式 |
| `verification_status` | Enum | ✅ | pending | 验证状态 | 见 VerificationStatus 枚举 |
| `importance_weight` | Float | ✅ | 1.0 | 重要性权重 | 范围: 0.1-2.0 |
| `created_at` | Timestamp | ✅ | now() | 创建时间 | ISO 8601 格式 |

### 嵌套类型定义

#### Source (来源)
```python
class PromiseSource(BaseModel):
    """承诺来源"""
    type: str = Field(..., description="来源类型: twitter/website/whitepaper")
    url: HttpUrl = Field(..., description="来源 URL")
    published_at: datetime = Field(..., description="发布时间")
    metadata: Optional[dict] = Field(None, description="额外元数据")

    class Config:
        json_schema_extra = {
            "example": {
                "type": "twitter",
                "url": "https://twitter.com/BoredApeYC/status/1234567890",
                "published_at": "2023-10-15T10:30:00Z",
                "metadata": {"likes": 1500, "retweets": 300}
            }
        }
```

#### PromiseType (承诺类型枚举)
```python
from enum import Enum

class PromiseType(str, Enum):
    """承诺类型枚举"""
    AIRDROP = "airdrop"                      # 代币空投
    FEATURE_DEVELOPMENT = "feature_development"  # 功能开发
    PARTNERSHIP = "partnership"              # 合作伙伴
    COMMUNITY_EVENT = "community_event"      # 社区活动
    NFT_MINTING = "nft_minting"             # NFT 铸造
    MARKETPLACE_LAUNCH = "marketplace_launch"  # 市场上线
    OTHER = "other"                          # 其他
```

#### VerificationStatus (验证状态枚举)
```python
class VerificationStatus(str, Enum):
    """验证状态枚举"""
    PENDING = "pending"          # 待验证
    FULFILLED = "fulfilled"      # 已兑现
    UNFULFILLED = "unfulfilled"  # 未兑现
    UNVERIFIABLE = "unverifiable"  # 无法验证
```

### Pydantic 模型定义

```python
class Promise(BaseModel):
    """承诺实体模型"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="承诺唯一标识符")
    project_id: str = Field(..., description="关联的项目 ID")
    content: str = Field(..., min_length=1, max_length=1000, description="承诺内容")
    sources: list[PromiseSource] = Field(..., min_items=1, description="来源列表")
    promise_type: PromiseType = Field(..., description="承诺类型")
    target_date: Optional[datetime] = Field(None, description="目标时间")
    verification_status: VerificationStatus = Field(default=VerificationStatus.PENDING, description="验证状态")
    importance_weight: float = Field(default=1.0, ge=0.1, le=2.0, description="重要性权重")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="创建时间")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "660e8400-e29b-41d4-a716-446655440001",
                "project_id": "550e8400-e29b-41d4-a716-446655440000",
                "content": "We will airdrop 1000 tokens to all holders by Q2 2024",
                "sources": [
                    {
                        "type": "twitter",
                        "url": "https://twitter.com/BoredApeYC/status/1234567890",
                        "published_at": "2023-10-15T10:30:00Z"
                    }
                ],
                "promise_type": "airdrop",
                "target_date": "2024-06-30",
                "verification_status": "pending",
                "importance_weight": 1.5
            }
        }
```

### 关系
- 多对一: `Promise` → `NFTProject` (多个承诺属于一个项目)

---

## 3. Verification Record (验证记录)

### 实体描述
代表一次完整的验证过程，包含五维评分、画饼指数和详细报告。

### 字段定义

| 字段名 | 类型 | 必填 | 默认值 | 描述 | 验证规则 |
|--------|------|------|--------|------|----------|
| `id` | UUID | ✅ | auto | 验证记录唯一标识符 | UUID v4 格式 |
| `project_id` | UUID | ✅ | - | 关联的项目 ID | 外键: NFTProject.id |
| `verification_time` | Timestamp | ✅ | now() | 验证时间 | ISO 8601 格式 |
| `promise_breaking_index` | Float | ✅ | - | 画饼指数 | 范围: 0-100 |
| `integrity_score` | Float | ✅ | - | 诚信审计得分 | 范围: 0-100 |
| `fairness_score` | Float | ✅ | - | 公平性审计得分 | 范围: 0-100 |
| `activity_score` | Float | ✅ | - | 开发力审计得分 | 范围: 0-100 |
| `stability_score` | Float | ✅ | - | 财务稳定性得分 | 范围: 0-100 |
| `momentum_score` | Float | ✅ | - | 社区动能得分 | 范围: 0-100 |
| `total_promises` | Integer | ✅ | - | 承诺总数 | >= 0 |
| `fulfilled_count` | Integer | ✅ | - | 已兑现数量 | >= 0 |
| `unfulfilled_count` | Integer | ✅ | - | 未兑现数量 | >= 0 |
| `unverifiable_count` | Integer | ✅ | - | 无法验证数量 | >= 0 |
| `report_details` | JSON | ✅ | - | 详细报告内容 | 见 ReportDetails 结构 |

### 嵌套类型定义

#### ReportDetails (报告详情)
```python
class ReportDetails(BaseModel):
    """验证报告详情"""
    summary: str = Field(..., description="报告摘要")
    five_dimensions: dict = Field(..., description="五维评分详情")
    promise_analysis: list[dict] = Field(..., description="承诺分析列表")
    recommendations: list[str] = Field(..., description="建议列表")

    class Config:
        json_schema_extra = {
            "example": {
                "summary": "该项目画饼指数为 35 分，属于良好水平，轻度画饼。",
                "five_dimensions": {
                    "integrity": {
                        "score": 75,
                        "details": "10 条承诺中有 7 条已兑现，违约率 30%"
                    },
                    "fairness": {
                        "score": 60,
                        "details": "代币基尼系数 0.65，存在一定中心化风险"
                    }
                },
                "promise_analysis": [
                    {
                        "promise_id": "660e8400-e29b-41d4-a716-446655440001",
                        "content": "Airdrop 1000 tokens",
                        "status": "fulfilled",
                        "evidence": "链上查询到 1000 笔空投交易"
                    }
                ],
                "recommendations": [
                    "建议关注项目方的国库资金流向",
                    "建议等待更多承诺兑现后再投资"
                ]
            }
        }
```

### Pydantic 模型定义

```python
class VerificationRecord(BaseModel):
    """验证记录实体模型"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="验证记录唯一标识符")
    project_id: str = Field(..., description="关联的项目 ID")
    verification_time: datetime = Field(default_factory=datetime.utcnow, description="验证时间")
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

    @validator('total_promises')
    def validate_total_promises(cls, v, values):
        """验证承诺总数等于各状态数量之和"""
        fulfilled = values.get('fulfilled_count', 0)
        unfulfilled = values.get('unfulfilled_count', 0)
        unverifiable = values.get('unverifiable_count', 0)
        if v != fulfilled + unfulfilled + unverifiable:
            raise ValueError('承诺总数必须等于各状态数量之和')
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "id": "770e8400-e29b-41d4-a716-446655440002",
                "project_id": "550e8400-e29b-41d4-a716-446655440000",
                "verification_time": "2024-01-29T12:00:00Z",
                "promise_breaking_index": 35.0,
                "integrity_score": 75.0,
                "fairness_score": 60.0,
                "activity_score": 80.0,
                "stability_score": 70.0,
                "momentum_score": 65.0,
                "total_promises": 10,
                "fulfilled_count": 7,
                "unfulfilled_count": 2,
                "unverifiable_count": 1
            }
        }
```

### 关系
- 多对一: `VerificationRecord` → `NFTProject` (多次验证记录属于一个项目)

---

## 4. Privacy Storage Record (隐私存储记录)

### 实体描述
代表通过 DDC-Market-SDK (ERC-7962) 存储到链上的数据记录，包含存储类型、交易哈希和隐私地址。

### 字段定义

| 字段名 | 类型 | 必填 | 默认值 | 描述 | 验证规则 |
|--------|------|------|--------|------|----------|
| `id` | UUID | ✅ | auto | 存储记录唯一标识符 | UUID v4 格式 |
| `project_id` | UUID | ✅ | - | 关联的项目 ID | 外键: NFTProject.id |
| `storage_type` | Enum | ✅ | - | 存储类型 | 见 StorageType 枚举 |
| `storage_time` | Timestamp | ✅ | now() | 存储时间 | ISO 8601 格式 |
| `tx_hash` | String | ❌ | null | 链上交易哈希 | 有效的以太坊交易哈希 |
| `privacy_address` | Address | ❌ | null | 隐私接收地址 | 有效的以太坊地址 |
| `data_hash` | String | ✅ | - | 数据摘要 (SHA256) | 64 字符十六进制 |
| `storage_status` | Enum | ✅ | pending | 存储状态 | 见 StorageStatus 枚举 |

### 枚举定义

#### StorageType (存储类型枚举)
```python
class StorageType(str, Enum):
    """存储类型枚举"""
    PROMISE_ARCHIVE = "promise_archive"          # 承诺数据存档
    VERIFICATION_RESULT = "verification_result"  # 验证结果
```

#### StorageStatus (存储状态枚举)
```python
class StorageStatus(str, Enum):
    """存储状态枚举"""
    PENDING = "pending"      # 待上链
    COMPLETED = "completed"  # 已上链
    FAILED = "failed"        # 失败
```

### Pydantic 模型定义

```python
class PrivacyStorageRecord(BaseModel):
    """隐私存储记录实体模型"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="存储记录唯一标识符")
    project_id: str = Field(..., description="关联的项目 ID")
    storage_type: StorageType = Field(..., description="存储类型")
    storage_time: datetime = Field(default_factory=datetime.utcnow, description="存储时间")
    tx_hash: Optional[str] = Field(None, description="链上交易哈希")
    privacy_address: Optional[str] = Field(None, description="隐私接收地址")
    data_hash: str = Field(..., min_length=64, max_length=64, description="数据摘要 (SHA256)")
    storage_status: StorageStatus = Field(default=StorageStatus.PENDING, description="存储状态")

    @validator('tx_hash')
    def validate_tx_hash(cls, v):
        if v and not v.startswith('0x'):
            raise ValueError('交易哈希必须以 0x 开头')
        if v and len(v) != 66:
            raise ValueError('交易哈希长度必须为 66 字符')
        return v

    @validator('privacy_address')
    def validate_privacy_address(cls, v):
        if v and not v.startswith('0x'):
            raise ValueError('隐私地址必须以 0x 开头')
        if v and len(v) != 42:
            raise ValueError('隐私地址长度必须为 42 字符')
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "id": "880e8400-e29b-41d4-a716-446655440003",
                "project_id": "550e8400-e29b-41d4-a716-446655440000",
                "storage_type": "verification_result",
                "storage_time": "2024-01-29T12:05:00Z",
                "tx_hash": "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
                "privacy_address": "0x9876543210987654321098765432109876543210",
                "data_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
                "storage_status": "completed"
            }
        }
```

### 关系
- 多对一: `PrivacyStorageRecord` → `NFTProject` (多次存储记录属于一个项目)

---

## 5. 数据库 Schema (SQLite)

### 表结构定义

```sql
-- projects 表
CREATE TABLE projects (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    twitter_account TEXT,
    website_url TEXT,
    whitepaper_url TEXT,
    contract_address TEXT,
    github_repo TEXT,
    treasury_address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_verified_at TIMESTAMP
);

-- promises 表
CREATE TABLE promises (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    content TEXT NOT NULL,
    sources TEXT NOT NULL,  -- JSON 格式
    promise_type TEXT NOT NULL,
    target_date DATE,
    verification_status TEXT DEFAULT 'pending',
    importance_weight REAL DEFAULT 1.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);

-- verification_records 表
CREATE TABLE verification_records (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    verification_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    promise_breaking_index REAL NOT NULL,
    integrity_score REAL NOT NULL,
    fairness_score REAL NOT NULL,
    activity_score REAL NOT NULL,
    stability_score REAL NOT NULL,
    momentum_score REAL NOT NULL,
    total_promises INTEGER NOT NULL,
    fulfilled_count INTEGER NOT NULL,
    unfulfilled_count INTEGER NOT NULL,
    unverifiable_count INTEGER NOT NULL,
    report_details TEXT NOT NULL,  -- JSON 格式
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);

-- privacy_storage_records 表
CREATE TABLE privacy_storage_records (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    storage_type TEXT NOT NULL,
    storage_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    tx_hash TEXT,
    privacy_address TEXT,
    data_hash TEXT NOT NULL,
    storage_status TEXT DEFAULT 'pending',
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);

-- 索引优化
CREATE INDEX idx_promises_project_id ON promises(project_id);
CREATE INDEX idx_promises_verification_status ON promises(verification_status);
CREATE INDEX idx_verification_records_project_id ON verification_records(project_id);
CREATE INDEX idx_verification_records_time ON verification_records(verification_time DESC);
CREATE INDEX idx_privacy_storage_project_id ON privacy_storage_records(project_id);
CREATE INDEX idx_privacy_storage_status ON privacy_storage_records(storage_status);
```

---

## 6. 数据流转图

```
用户��入项目信息
    ↓
创建 NFTProject 实体
    ↓
数据收集阶段
    ├─→ 抓取 Twitter 推文
    ├─→ 爬取官网内容
    └─→ 解析白皮书
    ↓
创建 Promise 实体（多个）
    ↓
隐私存储（承诺数据）
    └─→ 创建 PrivacyStorageRecord (type=promise_archive)
    ↓
链上验证阶段
    ├─→ 查询链上数据
    ├─→ 对比承诺与实际行为
    └─→ 计算五维评分
    ↓
创建 VerificationRecord 实体
    ↓
隐私存储（验证结果）
    └─→ 创建 PrivacyStorageRecord (type=verification_result)
    ↓
返回验证报告
```

---

## 7. 数据验证规则总结

### 不可变性原则
- 所有数据模型使用 Pydantic 的不可变模式（`frozen=True` 可选）
- 数据转换返回新对象，不修改原对象
- 数据库操作使用参数化查询，防止 SQL 注入

### 类型安全
- 所有字段使用 Pydantic 类型提示
- 枚举类型使用 `Enum` 定义，避免魔法字符串
- 日期时间统一使用 ISO 8601 格式

### 输入验证
- 所有用户输入通过 Pydantic 模型验证
- 以太坊地址验证（0x 前缀 + 42 字符）
- URL 验证（HTTP/HTTPS 协议）
- 字符串长度限制（防止数据库溢出）

### 业务规则
- 承诺总数 = 已兑现 + 未兑现 + 无法验证
- 画饼指数范围: 0-100
- 五维评分范围: 0-100
- 重要性权重范围: 0.1-2.0

---

**Document Version**: 1.0.0
**Last Updated**: 2026-01-30
**Status**: ✅ Ready for Implementation
