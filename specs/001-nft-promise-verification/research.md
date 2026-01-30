# Research Document: NFT 项目承诺验证系统技术调研

**Feature**: 001-nft-promise-verification
**Date**: 2026-01-29
**Status**: Completed
**Related**: [plan.md](./plan.md) | [spec.md](./spec.md)

---

## 研究目标

解决实施计划中标记为 "NEEDS CLARIFICATION" 的技术决策点，为 MVP 开发提供明确的技术方案。

---

## 1. Twitter 数据获取方式

### 问题陈述
需要从 Twitter 抓取 NFT 项目的公开推文内容，识别其中的承诺性质内容。Twitter 官方 API 有访问限制和成本问题，需要评估最佳方案。

### 方案对比

#### 方案 A: Twitter Official API v2 (Tweepy)
**优点**:
- 官方支持，数据质量高
- 结构化数据，易于解析
- 符合 Twitter 服务条款

**缺点**:
- 免费层级限制严格（每月 500,000 推文读取）
- 需要开发者账号审核（可能需要数天）
- 历史推文访问受限（免费层仅 7 天）
- 成本较高（Basic 层 $100/月）

**适用场景**: 生产环境，需要长期稳定服务

#### 方案 B: snscrape (Web Scraping)
**优点**:
- 完全免费，无 API 限制
- 可访问历史推文（无时间限制）
- 无需开发者账号
- Python 库成熟，易于集成

**缺点**:
- 违反 Twitter 服务条款（法律风险）
- 可能被 Twitter 封禁 IP
- HTML 结构变化可能导致失效
- 数据质量依赖解析准确性

**适用场景**: MVP 阶段，快速原型验证

#### 方案 C: Nitter (开源 Twitter 前端)
**优点**:
- 开源，可自建实例
- 无需 API 密钥
- RSS 订阅支持

**缺点**:
- 需要维护 Nitter 实例
- 公共实例不稳定
- 数据获取速度较慢

**适用场景**: 隐私敏感场景

### 决策

**选择方案 B (snscrape) 用于 MVP 阶段**

**理由**:
1. **MVP 优先**: 快速验证产品概念，无需等待 API 审核
2. **成本控制**: 避免早期开发阶段的 API 费用
3. **功能完整性**: 需要访问历史推文（项目早期承诺）
4. **技术成熟度**: snscrape 在社区中广泛使用，文档完善

**风险缓解**:
- 添加请求延迟（2-5 秒），避免触发反爬虫机制
- 使用代理池轮换 IP（可选）
- 在生产环境迁移至官方 API

**替代方案被拒绝的原因**:
- 方案 A: MVP 阶段无法承担 $100/月成本，且审核时间不可控
- 方案 C: 维护成本高，数据获取效率低

---

## 2. SpoonOS React Agent 最佳实践

### 问题陈述
需要了解 SpoonOS 0.3.6 中 React Agent 的实现模式、工具定义规范和错误处理策略。

### 研究发现

#### SpoonOS 架构概览
- **核心框架**: spoon-core (基于 LangChain)
- **工具包**: spoon-toolkit (预定义工具集)
- **启动器**: spoon-starter (快速启动模板)

#### React Agent 实现模式

**工具定义规范** (基于 BaseTool):
```python
from spoon_core.tools import BaseTool
from pydantic import BaseModel, Field

class ToolInput(BaseModel):
    """工具输入参数定义"""
    param1: str = Field(description="参数描述")

class CustomTool(BaseTool):
    name = "tool_name"
    description = "工具功能描述（Agent 用于决策）"
    args_schema = ToolInput

    def _run(self, param1: str) -> str:
        """同步执行逻辑"""
        pass

    async def _arun(self, param1: str) -> str:
        """异步执行逻辑（推荐）"""
        pass
```

**Agent 初始化模式**:
```python
from spoon_core.agents import ReactAgent
from spoon_core.llm import LLMManager

llm = LLMManager.get_llm("openai", model="gpt-4")
tools = [TwitterScraperTool(), WebScraperTool(), PromiseExtractorTool()]

agent = ReactAgent(
    llm=llm,
    tools=tools,
    verbose=True,
    max_iterations=10,
    early_stopping_method="generate"
)

result = agent.run("收集 Bored Ape Yacht Club 的项目承诺")
```

**错误处理策略**:
1. **工具级错误**: 在 `_run` 方法中捕获异常，返回错误信息字符串
2. **Agent 级错误**: 使用 `try-except` 包裹 `agent.run()`
3. **超时控制**: 设置 `max_iterations` 和工具内部超时

### 决策

**采用 SpoonOS React Agent 标准模式**

**关键实践**:
1. 所有工具继承 `BaseTool`，使用 Pydantic 定义输入
2. 工具描述清晰具体，帮助 Agent 正确选择工具
3. 异步实现 `_arun` 方法，提升并发性能
4. 工具内部处理异常，返回结构化错误信息
5. 使用 `verbose=True` 便于调试和日志记录

---

## 3. 承诺识别策略

### 问题陈述
需要设计 LLM prompt 来识别文本中的承诺性质内容，并进行分类（空投、功能开发、合作伙伴等）。

### 研究发现

#### Few-Shot Prompting 策略

**Prompt 结构**:
```
你是一个专业的 NFT 项目承诺识别专家。请从以下文本中提取所有承诺性质的内容。

承诺定义：项目方对未来行动或结果的明确声明，包括但不限于：
- 代币空投
- 功能开发
- 合作伙伴
- 社区活动
- NFT 铸造
- 市场上线

示例 1:
输入: "We will airdrop 1000 tokens to all holders by Q2 2024"
输出: {
  "promise_text": "airdrop 1000 tokens to all holders",
  "promise_type": "代币空投",
  "target_time": "Q2 2024",
  "confidence": 0.95
}

示例 2:
输入: "Our marketplace is coming soon!"
输出: {
  "promise_text": "marketplace is coming soon",
  "promise_type": "市场上线",
  "target_time": "未指定",
  "confidence": 0.70
}

现在请分析以下文本：
{input_text}

请以 JSON 数组格式返回所有识别到的承诺。
```

#### 承诺类型分类

基于 spec.md FR-006 定义的类型：
1. **代币空投** (Token Airdrop)
2. **功能开发** (Feature Development)
3. **合作伙伴** (Partnership)
4. **社区活动** (Community Event)
5. **NFT 铸造** (NFT Minting)
6. **市场上线** (Marketplace Launch)
7. **其他** (Other)

### 决策

**使用 Few-Shot Prompting + JSON 输出格式**

**理由**:
1. **准确性**: Few-shot examples 提供明确的识别标准
2. **结构化**: JSON 输出便于后续处理和存储
3. **可扩展**: 易于添加新的承诺类型
4. **置信度**: 包含 confidence 字段，便于过滤低质量结果

**实现细节**:
- 使用 GPT-4 或 Claude 3.5 Sonnet（更强的指令遵循能力）
- 设置 `temperature=0.3`（平衡创造性和一致性）
- 使用 `response_format={"type": "json_object"}` 确保 JSON 输出
- 对模糊承诺（如"即将推出"）标记 `confidence < 0.7`

---

## 4. 数据存储方案

### 问题陈述
MVP 阶段需要选择合适的数据存储方案，平衡开发速度和功能需求。

### 方案对比

#### 方案 A: JSON 文件存储
**优点**:
- 零配置，开发速度快
- 易于调试和查看数据
- 无需额外依赖

**缺点**:
- 并发写入问题
- 查询性能差（需要加载整个文件）
- 无事务支持

**适用场景**: MVP 阶段，数据量 <100 个项目

#### 方案 B: SQLite
**优点**:
- 轻量级，无需独立服务
- 支持 SQL 查询
- 事务支持

**缺点**:
- 需要设计数据库 schema
- 并发写入限制
- 迁移成本（相比 JSON）

**适用场景**: 中等规模，需要复杂查询

#### 方案 C: PostgreSQL/MongoDB
**优点**:
- 生产级性能
- 完整的并发支持
- 丰富的查询功能

**缺点**:
- 需要独立服务
- 配置复杂
- MVP 阶段过度设计

**适用场景**: 生产环境，大规模数据

### 决策

**选择方案 B (SQLite) 用于 MVP**

**理由**:
1. **SQL 查询能力**: 支持复杂的历史记录查询和统计分析
2. **事务支持**: 确保数据一致性，特别是在验证记录写入时
3. **JSON 字段支持**: SQLite 3.9+ 支持 JSON 字段，可存储复杂数据结构
4. **零配置**: 单文件存储，无需独立数据库服务
5. **满足规模**: 支持 1000+ 项目的历史记录存储（spec.md SC-008）

**数据库 Schema**:
```sql
-- projects 表
CREATE TABLE projects (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    twitter_account TEXT,
    website_url TEXT,
    contract_address TEXT,
    github_repo TEXT,
    treasury_address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- promises 表
CREATE TABLE promises (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    content TEXT NOT NULL,
    sources TEXT NOT NULL,  -- JSON: 来源列表
    promise_type TEXT,
    target_date DATE,
    verification_status TEXT,
    FOREIGN KEY (project_id) REFERENCES projects(id)
);

-- verification_records 表
CREATE TABLE verification_records (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    verification_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    promise_breaking_index REAL,
    integrity_score REAL,
    fairness_score REAL,
    activity_score REAL,
    stability_score REAL,
    momentum_score REAL,
    report_details TEXT,  -- JSON 格式
    FOREIGN KEY (project_id) REFERENCES projects(id)
);

-- privacy_storage_records 表
CREATE TABLE privacy_storage_records (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    storage_type TEXT NOT NULL,
    storage_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    tx_hash TEXT,
    privacy_address TEXT,
    data_hash TEXT,
    storage_status TEXT DEFAULT 'pending',
    FOREIGN KEY (project_id) REFERENCES projects(id)
);
```

**迁移路径**:
- MVP 使用 SQLite（满足 1000+ 项目需求）
- 生产环境可迁移至 PostgreSQL（如需更高并发）

---

## 5. LLM 选择

### 问题陈述
需要选择合适的 LLM 作为 Agent 的推理引擎和承诺识别工具。

### 方案对比

#### 方案 A: OpenAI GPT-4
**优点**:
- 推理能力强
- 指令遵循准确
- API 稳定

**缺点**:
- 成本较高（$0.03/1K tokens 输入，$0.06/1K tokens 输出）
- 响应速度较慢（2-5 秒）

**适用场景**: 需要高质量推理的场景

#### 方案 B: Anthropic Claude 3.5 Sonnet
**优点**:
- 推理能力与 GPT-4 相当
- 更长的上下文窗口（200K tokens）
- 更好的中文支持

**缺点**:
- 成本略高（$0.003/1K tokens 输入，$0.015/1K tokens 输出）
- API 可用性（需要 VPN）

**适用场景**: 需要处理长文本的场景

#### 方案 C: 本地模型 (Llama 3, Qwen)
**优点**:
- 零 API 成本
- 数据隐私

**缺点**:
- 推理能力弱于商业模型
- 需要 GPU 资源
- 部署复杂

**适用场景**: 成本敏感或隐私要求高的场景

### 决策

**选择方案 B (Claude 3.5 Sonnet) 作为主要 LLM**

**理由**:
1. **中文支持**: 项目承诺可能包含中文内容
2. **长上下文**: 处理完整网页和多条推文
3. **成本效益**: 输入 token 成本低（$0.003 vs $0.03）
4. **推理质量**: 与 GPT-4 相当的承诺识别准确性

**备选方案**: OpenAI GPT-4（当 Claude API 不可用时）

**成本估算** (单个项目):
- 输入: ~10K tokens (推文 + 网页内容)
- 输出: ~2K tokens (承诺清单)
- 成本: $0.03 + $0.03 = $0.06/项目

---

## 6. 隐私存储方案 (DDC-Market-SDK)

### 问题陈述
需要将验证结果和承诺数据以隐私保护方式存储到链上，防止验证者身份被项目方追溯，同时确保数据不可篡改。

### 方案对比

#### 方案 A: IPFS + 加密
**优点**:
- 去中心化存储
- 成本低

**缺点**:
- 无隐私保护（地址可追溯）
- 数据可能被删除
- 需要自行实现加密逻辑

**适用场景**: 公开数据存储

#### 方案 B: DDC-Market-SDK (ERC-7962)
**优点**:
- 隐私接收地址（验证者身份保护）
- 链上存储（不可篡改）
- 标准化接口（ERC-7962）
- onchain-verifier skill 已封装

**缺点**:
- 需要 gas 费用
- 数据大小限制（1MB）

**适用场景**: 敏感数据的隐私存储

### 决策

**选择方案 B (DDC-Market-SDK) 用于验证结果和承诺数据存储**

**理由**:
1. **隐私保护**: 验证者身份不会被项目方追溯，避免报复
2. **防篡改**: 链上存储确保承诺数据和验证结果不可修改
3. **可验证性**: 任何人都可以通过链上数据验证报告真实性
4. **标准化**: ERC-7962 标准接口，便于集成

**调用时机**:
1. **数据收集阶段**: 将项目承诺数据（Twitter、官网、白皮书）存储到链上
2. **生成验证报告后**: 将画饼指数、验证报告等结果存储到链上

**数据格式**:
```python
# 承诺数据存储
{
    "data_type": "promise_archive",
    "project_id": "uuid",
    "promises": [...],
    "timestamp": "2024-01-29T10:00:00Z",
    "data_hash": "sha256-hash",
    "signature": "eip-191-signature"
}

# 验证结果存储
{
    "data_type": "verification_result",
    "project_id": "uuid",
    "promise_breaking_index": 35,
    "verification_time": "2024-01-29T12:00:00Z",
    "summary": {...},
    "details": [...],
    "data_hash": "sha256-hash",
    "signature": "eip-191-signature"
}
```

**数据清洗流程**:
1. 格式化：统一数据结构
2. 去重：移除重复承诺
3. 结构化：转换为 DDC-Market-SDK 要求的输入格式
4. 分批：超过 1MB 时分批存储

---

## 7. 五维审计模型设计

### 问题陈述
需要设计一个全面、可解释的评分模型来计算项目的画饼指数，不能仅依赖承诺兑现率。

### 研究发现

#### 第一性原理方法论
基于物理世界的不可伪造特征设计评分维度：
1. **时间轴不可逆**: 承诺与实际行为的时间对比
2. **资金流向可追踪**: 国库资金的真实动机
3. **代码提交需成本**: 真实的开发者时间投入
4. **财富分布可量化**: 去中心化程度的物理屏障
5. **语义随机性可检测**: 真实用户 vs 机器人

### 决策

**采用五维审计模型（诚信、公平性、开发力、财务稳定性、社区动能）**

**维度设计**:

1. **诚信审计维度 (30%)**
   - 原理: "真理在时空轴上不具备矛盾性"
   - 工具: TwitterTool, WebScraperTool, EVMGetTokenBalance, EVMCallContract
   - 计算: 承诺违约率 = (未兑现承诺数 / 可验证承诺数)

2. **公平性审计维度 (25%)**
   - 原理: "系统性风险与权力集中度成正比"
   - 工具: TokenHolders
   - 计算: 基尼系数 (Gini Coefficient)，Gini > 0.7 判定为中心化风险

3. **开发力审计维度 (20%)**
   - 原理: "逻辑的有序堆叠是无法伪造的生命能量损耗"
   - 工具: GetGitHubCommitsTool, GetGitHubPullRequestsTool, GetGitHubIssuesTool
   - 计算: 代码提交频率和 PR 质量分析

4. **财务稳定性维度 (15%)**
   - 原理: "金钱的流向定义了组织的真实动机"
   - 工具: WalletAnalysis
   - 计算: 识别可疑转账（流向洗币协议或新个人地址）

5. **社区动能维度 (10%)**
   - 原理: "真实的用户共识是随机波动的，机器人的共识是机械低熵的"
   - 工具: TwitterTool + LLM 语义分析
   - 计算: 推特互动的语义随机性评分

**最终公式**:
```python
promise_breaking_index = 100 - (
    integrity_score * 0.30 +
    fairness_score * 0.25 +
    activity_score * 0.20 +
    stability_score * 0.15 +
    momentum_score * 0.10
)
```

**指数解读**:
- 0-20: 优秀（几乎不画饼）
- 21-40: 良好（轻度画饼）
- 41-60: 一般（中度画饼）
- 61-80: 较差（重度画饼）
- 81-100: 极差（严重画饼）

---

## 8. 区块链网络选择

### 问题陈述
原规格文档中包含 BSN（Blockchain Service Network）相关内容，需要明确实际使用的区块链网络。

### 决策

**选择 Ethereum Mainnet + Sepolia Testnet**

**理由**:
1. **Mainnet 用于生产环境**: 查询真实 NFT 项目的链上数据
2. **Sepolia 作为测试网**: 以太坊官方推荐的测试网（Goerli 已弃用）
3. **双网络支持优势**:
   - 开发阶段在 Sepolia 上低成本测试
   - 生产环境切换到 Mainnet 无需修改核心代码
   - 便于 CI/CD 流程中的自动化测试
4. **工具链兼容性**: spoon-toolkit 的 EVM 工具原生支持以太坊网络

**RPC 节点配置**:
```bash
# .env 配置
ETHEREUM_MAINNET_RPC_URL=https://mainnet.infura.io/v3/YOUR_PROJECT_ID
ETHEREUM_SEPOLIA_RPC_URL=https://sepolia.infura.io/v3/YOUR_PROJECT_ID

# 或使用 Alchemy
ETHEREUM_MAINNET_RPC_URL=https://eth-mainnet.g.alchemy.com/v2/YOUR_API_KEY
ETHEREUM_SEPOLIA_RPC_URL=https://eth-sepolia.g.alchemy.com/v2/YOUR_API_KEY
```

**工具使用示例**:
```python
from spoon_toolkit.crypto import EVMGetTokenBalance

balance_tool = EVMGetTokenBalance()
result = balance_tool.execute(
    address="0x1234...",
    token_address="0x5678...",
    network="ethereum-mainnet"  # 或 "ethereum-sepolia"
)
```

---

## 9. 其他技术决策

### 网页解析库

**决策**: BeautifulSoup4 + requests

**理由**:
- 成熟稳定，文档完善
- 易于处理 HTML 结构
- 轻量级，无需浏览器引擎

**替代方案被拒绝**:
- Selenium: 过重，MVP 不需要 JavaScript 渲染
- Scrapy: 框架过于复杂，MVP 不需要分布式爬虫

### 日志系统

**决策**: Python logging 模块 + structlog

**理由**:
- 标准库，无额外依赖
- structlog 提供结构化日志（便于调试）
- 支持多种输出格式（文件、控制台）

### 配置管理

**决策**: python-dotenv + Pydantic Settings

**理由**:
- 环境变量管理符合 12-Factor App 原则
- Pydantic 提供类型验证和默认值
- 易于在不同环境间切换

---

## 技术栈总结

| 组件 | 技术选择 | 版本 | 理由 |
|------|---------|------|------|
| Agent 框架 | SpoonOS (SpoonReactAI) | 0.3.6 | 项目要求，成熟的 ReAct Agent 实现 |
| LLM | Claude 3.5 Sonnet | latest | 中文支持好，长上下文，成本效益高 |
| Twitter 数据 | snscrape | latest | 免费，无 API 限制，适合 MVP |
| 网页解析 | BeautifulSoup4 | 4.12+ | 轻量级，易用 |
| 数据验证 | Pydantic | 2.x | 类型安全，与 SpoonOS 集成 |
| 存储 | SQLite | 3.9+ | 支持 JSON 字段，零配置，满足 1000+ 项目需求 |
| 隐私存储 | DDC-Market-SDK (ERC-7962) | latest | 隐私保护，防篡改，标准化接口 |
| 区块链网络 | Ethereum Mainnet + Sepolia | N/A | 生产 + 测试双网络支持 |
| RPC 提供商 | Infura / Alchemy | N/A | 免费额度，稳定可靠 |
| 测试 | pytest | 7.x+ | Python 标准测试框架 |
| 日志 | structlog | 23.x+ | 结构化日志，便于调试 |
| Web 框架 | FastAPI | 0.100+ | 高性能，自动生成 OpenAPI 文档 |
| 前端框架 | Next.js | 14.x | App Router，SSR/SSG 支持 |
| 前端语言 | TypeScript | 5.x | 类型安全，减少运行时错误 |
| 前端样式 | Tailwind CSS | 3.x | 实用优先，快速构建响应式界面 |

---

## 风险与缓解

| 风险 | 影响 | 概率 | 缓解措施 |
|------|------|------|---------|
| snscrape 被 Twitter 封禁 | 高 | 中 | 添加请求延迟，准备迁移至官方 API |
| LLM API 成本超预算 | 中 | 低 | 使用 token 计数，设置每日限额 |
| 承诺识别准确率低 | 高 | 中 | 迭代优化 prompt，添加人工审核 |
| DDC-Market-SDK gas 费用高 | 中 | 中 | 批量存储，优化数据大小 |
| Ethereum RPC 节点限流 | 中 | 低 | 使用多个 RPC 提供商，实现故障转移 |
| 五维审计数据不完整 | 中 | 中 | 缺失数据使用中性评分（50分） |

---

## 下一步行动

1. ✅ 完成技术调研
2. ⏳ 进入 Phase 1：设计数据模型和 API 契约
3. ⏳ 实现核心工具（TwitterScraperTool、WebScraperTool、PromiseExtractorTool）
4. ⏳ 实现五维审计评分模块
5. ⏳ 集成 DDC-Market-SDK 隐私存储
6. ⏳ 实现 React Agent 编排逻辑
7. ⏳ 编写单元测试和集成测试
8. ⏳ 开发前端可视化界面

---

**Document Version**: 2.0.0
**Last Updated**: 2026-01-29
**Reviewed By**: AI Agent
**Status**: ✅ Approved for Phase 1
**Changes from v1.0.0**:
- 更新数据存储方案：JSON 文件 → SQLite
- 新增隐私存储方案：DDC-Market-SDK (ERC-7962)
- 新增五维审计模型设计
- 新增区块链网络选择：Ethereum Mainnet + Sepolia Testnet
- 更新技术栈总结和风险评估

