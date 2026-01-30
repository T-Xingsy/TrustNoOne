# Feature Specification: NFT 项目承诺验证系统（画饼识破）

**Feature Branch**: `001-nft-promise-verification`
**Created**: 2026-01-29
**Status**: Draft
**Input**: User description: "NFT projects often make various promises on Twitter, in whitepapers, and on their official websites, but their actual performance varies widely. Currently, there is a lack of an automated system to: Collect the project's public promises, Verify whether the promises have been fulfilled, Evaluate the project's promise-breaking index. Using the SpoonOS Framework, we can build an agent to automate the following: 1. Collect the project's public promises (from Twitter, official website, and whitepaper) 2. Query on-chain activity for each promise 3. Compare promises and actual behavior for intelligent scoring 4. Generate a promise-breaking index and performance report. The goal is to: collect project promises from Twitter and the official website; query on-chain activity within a specific time frame; compare promises and actual behavior for intelligent scoring; generate a performance report and promise-breaking index; and finally, have a visual front-end to display the verification results and save the project's verification history."

## User Scenarios & Testing *(mandatory)*

<!--
  IMPORTANT: User stories should be PRIORITIZED as user journeys ordered by importance.
  Each user story/journey must be INDEPENDENTLY TESTABLE - meaning if you implement just ONE of them,
  you should still have a viable MVP (Minimum Viable Product) that delivers value.
  
  Assign priorities (P1, P2, P3, etc.) to each story, where P1 is the most critical.
  Think of each story as a standalone slice of functionality that can be:
  - Developed independently
  - Tested independently
  - Deployed independently
  - Demonstrated to users independently
-->

### User Story 1 - 项目承诺收集与初步验证 (Priority: P1)

作为一个 NFT 投资者，我想要输入一个 NFT 项目的基本信息（项目名称、Twitter 账号、官网链接），系统能够自动收集该项目在各个渠道发布的公开承诺，并生成一份承诺清单，这样我就能快速了解项目方都做了哪些承诺。

**Why this priority**: 这是整个系统的基础功能，没有承诺数据就无法进行后续的验证和评分。这个功能可以独立交付价值，即使没有链上验证，用户也能获得一份结构化的承诺清单。

**Independent Test**: 可以通过输入一个已知的 NFT 项目（如 Bored Ape Yacht Club），验证系统是否能成功抓取其 Twitter、官网和白皮书中的承诺内容，并以结构化格式展示。

**Acceptance Scenarios**:

1. **Given** 用户在系统中输入了项目的 Twitter 账号和官网链接，**When** 用户点击"开始收集"按钮，**Then** 系统应在 5 分钟内返回一份包含至少 5 条承诺的清单
2. **Given** 系统已收集到项目承诺，**When** 用户查看承诺清单，**Then** 每条承诺应包含：承诺内容、发布时间、来源渠道、承诺类型（如：空投、路线图、功能开发等）
3. **Given** 项目的 Twitter 账号不存在或无法访问，**When** 系统尝试收集承诺，**Then** 系统应显示明确的错误提示，并继续尝试从其他渠道收集

---

### User Story 2 - 链上数据验证与对比 (Priority: P2)

作为一个 NFT 投资者，我想要系统能够自动查询项目的链上活动数据（如交易量、持有者数量、合约交互等），并将这些数据与项目承诺进行对比，这样我就能看到项目是否兑现了承诺。

**Why this priority**: 这是核心验证功能，将承诺与实际行为进行对比。虽然依赖于 P1 的承诺收集，但它提供了系统的核心价值——验证真实性。

**Independent Test**: 可以通过选择一个已收集承诺的项目，验证系统是否能查询其链上数据，并生成对比报告，显示哪些承诺已兑现、哪些未兑现。

**Acceptance Scenarios**:

1. **Given** 系统已收集到项目承诺，**When** 用户选择"开始验证"，**Then** 系统应在 10 分钟内完成链上数据查询并生成对比报告
2. **Given** 项目承诺"在 3 个月内空投代币"，**When** 系统查询链上数据，**Then** 系统应能识别是否有空投交易记录，并标记承诺状态为"已兑现"或"未兑现"
3. **Given** 链上数据查询失败（如网络问题），**When** 系统尝试验证，**Then** 系统应显示错误提示并允许用户重试

---

### User Story 3 - 画饼指数计算与报告生成 (Priority: P3)

作为一个 NFT 投资者，我想要系统能够基于承诺兑现情况，自动计算项目的"画饼指数"（promise-breaking index），并生成一份详细的验证报告，这样我就能快速评估项目的可信度。

**Why this priority**: 这是增值功能，将验证结果转化为易于理解的评分和报告。它依赖于 P1 和 P2，但提供了更高层次的洞察。

**Independent Test**: 可以通过查看一个已验证项目的画饼指数和报告，验证评分逻辑是否合理，报告内容是否完整清晰。

**Acceptance Scenarios**:

1. **Given** 系统已完成项目验证，**When** 用户查看报告，**Then** 报告应包含：画饼指数（0-100 分）、承诺兑现率、未兑现承诺列表、时间线对比图
2. **Given** 项目有 10 条承诺，其中 7 条已兑现，**When** 系统计算画饼指数，**Then** 指数应反映 70% 的兑现率，并考虑承诺的重要性权重
3. **Given** 用户查看报告，**When** 用户点击某条未兑现承诺，**Then** 系统应显示该承诺的详细信息、原始来源和验证依据

---

### User Story 4 - 可视化展示与历史记录 (Priority: P4)

作为一个 NFT 投资者，我想要通过可视化界面查看项目的验证结果，并能够查看项目的历史验证记录，这样我就能追踪项目的长期表现。

**Why this priority**: 这是用户体验增强功能，提供友好的界面和历史追踪能力。它是最后交付的功能，因为即使没有它，用户也能通过报告获取核心信息。

**Independent Test**: 可以通过访问前端界面，验证是否能看到项目列表、验证结果的可视化图表，以及历史记录的时间线展示。

**Acceptance Scenarios**:

1. **Given** 用户访问系统前端，**When** 用户查看项目列表，**Then** 应显示所有已验证项目的卡片，包含项目名称、画饼指数、最后验证时间
2. **Given** 用户选择一个项目，**When** 用户查看详情页，**Then** 应显示承诺兑现情况的可视化图表（如饼图、时间线图）
3. **Given** 项目已被验证多次，**When** 用户查看历史记录，**Then** 应显示每次验证的时间、画饼指数变化趋势图
4. **Given** 用户想要保存报告，**When** 用户点击"导出报告"，**Then** 系统应生成 PDF 或 JSON 格式的报告文件

### Edge Cases

- **多链项目处理**: 当 NFT 项目部署在多条区块链上时（如 Ethereum Mainnet、Polygon），系统应能够查询所有相关链的数据并汇总
- **承诺模糊性**: 当项目承诺表述模糊（如"即将推出"、"不久的将来"）时，系统应标记为"无法验证"并提示用户
- **数据源不可用**: 当 Twitter API 限流、官网无法访问或白皮书链接失效时，系统应记录错误并使用已有数据继续处理
- **承诺类型识别错误**: 当系统无法准确识别承诺类型时，应提供"未分类"选项并允许用户手动标注
- **链上数据延迟**: 当区块链网络拥堵导致数据查询延迟时，系统应显示进度提示并支持异步处理
- **项目更名或迁移**: 当项目更改名称或迁移合约地址时，系统应能够通过历史记录关联新旧项目
- **恶意项目**: 当项目涉嫌欺诈或已被标记为 Rug Pull 时，系统应显示警告标识
- **大量承诺**: 当项目承诺数量超过 100 条时，系统应支持分页和筛选功能

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: 系统必须能够接受用户输入的 NFT 项目基本信息，包括项目名称、Twitter 账号、官网 URL、白皮书链接和合约地址
- **FR-002**: 系统必须能够从 Twitter 抓取项目官方账号发布的推文内容，并识别其中包含承诺性质的内容
- **FR-003**: 系统必须能够从项目官网抓取文本内容，并识别其中的承诺声明
- **FR-004**: 系统必须能够解析 PDF 格式的白皮书文档，提取其中的路线图和承诺内容
- **FR-005**: 系统必须能够将收集到的承诺内容进行结构化存储，包含：承诺文本、发布时间、来源渠道、承诺类型、目标时间
- **FR-006**: 系统必须能够自动识别承诺类型，包括但不限于：代币空投、功能开发、合作伙伴、社区活动、NFT 铸造、市场上线
- **FR-007**: 系统必须能够查询以太坊区块链上的智能合约交互记录，支持 Ethereum Mainnet 和 Sepolia Testnet
- **FR-008**: 系统必须能够查询 NFT 项目的链上数据，包括：交易量、持有者数量、转账记录、合约事件日志
- **FR-009**: 系统必须能够将项目承诺与链上数据进行智能匹配，判断承诺是否已兑现
- **FR-010**: 系统必须能够计算项目的画饼指数，评分范围为 0-100 分，��数越高表示画饼程度越严重
- **FR-011**: 系统必须能够生成验证报告，包含：项目概况、承诺清单、兑现情况、画饼指数、详细分析
- **FR-012**: 系统必须能够保存项目的历史验证记录，支持查看画饼指数的时间变化趋势
- **FR-013**: 用户必须能够通过 Web 界面查看项目列表、验证结果和详细报告
- **FR-014**: 用户必须能够导出验证报告为 PDF 或 JSON 格式
- **FR-015**: 系统必须能够处理数据源不可用的情况，记录错误日志并继续处理其他数据源
- **FR-016**: 系统必须能够支持多链项目的数据查询和汇总分析
- **FR-017**: 系统必须能够在承诺表述模糊时标记为"无法验证"状态
- **FR-018**: 系统必须能够为画饼指数计算提供权重配置，不同类型的承诺具有不同的重要性权重
- **FR-019**: 系统必须能够通过 DDC-Market-SDK (ERC-7962) 将验证结果（画饼指数、验证报告）以隐私保护方式存储到链上，保护验证者身份不被项目方追溯
- **FR-020**: 系统必须能够通过 DDC-Market-SDK 将收集到的项目承诺数据（Twitter、官网、白皮书）以隐私方式存档到链上，防止项目方事后删除或修改承诺内容
- **FR-021**: 系统必须能够在数据上链前进行数据清洗，包括：格式化（统一数据结构）、去重（移除重复承诺）、结构化处理（转换为 DDC-Market-SDK 要求的输入格式）
- **FR-022**: 系统必须能够使用 spoon-toolkit 提供的工具进行数据收集，包括 TwitterTool（社交媒体）、WebScraperTool（官网爬取）、EVM 工具（链上查询）
- **FR-023**: 系统必须能够使用 spoon-core 的 Graph 工作流编排多个 Agent 协作完成验证流程
- **FR-024**: 系统必须能够使用 onchain-verifier skill 在两个关键时机调用 DDC-Market-SDK：(1) 生成验证报告后 (2) 数据收集阶段

### Key Entities

- **NFT 项目 (NFT Project)**: 代表一个 NFT 项目，包含项目名称、Twitter 账号、官网 URL、白皮书链接、合约地址、创建时间、最后验证时间
- **承诺 (Promise)**: 代表项目方做出的一个公开承诺，包含承诺文本、发布时间、来源渠道（Twitter/官网/白皮书）、承诺类型、目标时间、验证状态（已兑现/未兑现/无法验证）、重要性权重
- **链上数据 (On-chain Data)**: 代表从区块链查询到的数据，包含数据类型（交易/事件/状态）、数据内容、时间戳、区块高度、交易哈希
- **验证记录 (Verification Record)**: 代表一次完整的验证过程，包含验证时间、画饼指数、承诺总数、已兑现数量、未兑现数量、无法验证数量、详细报告内容
- **画饼指数 (Promise-Breaking Index)**: 代表项目的可信度评分，包含总分（0-100）、计算依据、五维得分（诚信审计 30%、公平性审计 25%、开发力审计 20%、财务稳定性审计 15%、社区动能审计 10%）
- **隐私存储记录 (Privacy Storage Record)**: 代表通过 DDC-Market-SDK (ERC-7962) 存储到链上的数据，包含存储类型（验证结果/承诺数据）、存储时间、链上交易哈希、隐私接收地址、数据摘要（用于验证完整性）、存储状态（待上链/已上链/失败）

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 用户能够在 5 分钟内完成一个 NFT 项目的承诺收集，系统返回至少 5 条结构化的承诺数据
- **SC-002**: 系统能够在 10 分钟内完成链上数据查询和验证对比，生成完整的验证报告
- **SC-003**: 系统的承诺识别准确率达到 80% 以上（通过人工抽样验证 100 个承诺样本）
- **SC-004**: 系统能够支持同时处理 10 个项目的验证请求，不出现性能降级
- **SC-005**: 90% 的用户能够在首次使用时成功完成项目验证流程，无需查看帮助文档
- **SC-006**: 系统的链上数据查询成功率达到 95% 以上（排除区块链网络故障）
- **SC-007**: 用户能够在 3 次点击内找到任何已验证项目的详细报告
- **SC-008**: 系统能够保存至少 1000 个项目的历史验证记录，查询响应时间不超过 2 秒
- **SC-009**: 画饼指数的计算结果与人工评估的相关性达到 0.7 以上（皮尔逊相关系数）
- **SC-010**: 系统能够支持 Ethereum Mainnet 和 Sepolia Testnet 两种网络环境

## Assumptions

- 假设 Twitter API 可以正常访问，或者可以通过 Web 爬虫方式获取推文内容
- 假设项目官网和白皮书链接在验证时是可访问的，如果不可访问则使用缓存数据
- 假设 Ethereum RPC 节点能够提供稳定的链上数据查询服务（Mainnet 和 Sepolia）
- 假设项目承诺通常使用中文或英文表述，系统需要支持双语识别
- 假设用户具备基本的 NFT 和区块链知识，了解常见的项目承诺类型
- 假设画饼指数的计算权重可以根据社区反馈进行调整和优化
- 假设系统部署在具有稳定网络连接的服务器环境中
- 假设用户主要通过 Web 浏览器访问系统，支持主流浏览器（Chrome、Firefox、Safari）

## Architecture Design *(mandatory)*

### MVP 架构：单 Agent + 多工具模式

本项目采用 **SpoonOS 框架的单 Agent 架构**，使用 `SpoonReactAI` (ReAct 模式) 配合多个专业工具完成所有验证任务。

#### Agent 设计

**VerificationAgent (NFT 承诺验证 Agent)**:
- **类型**: `SpoonReactAI` (来自 spoon-core)
- **LLM**: GPT-4 Turbo (通过 spoon-core 的 LLMManager 管理)
- **职责**:
  1. 数据收集：使用 TwitterTool 和 WebScraperTool 收集项目承诺
  2. 承诺提取：从文本中识别和分类承诺内容
  3. 链上验证：使用 EVM 工具查询链上数据，对比承诺
  4. 评分计算：计算画饼指数（0-100分）
  5. 隐私存储：使用 DDCMarketTool 将结果存储到链上

#### 工具链配置（强耦合 spoon-toolkit）

1. **数据收集工具**:
   - `TwitterTool` (spoon-toolkit): 抓取项目 Twitter 承诺和社区互动
   - `WebScraperTool` (spoon-toolkit): 爬取官网内容，支持 markdown 格式

2. **链上验证工具**:
   - `EVMGetTokenBalance` (spoon-toolkit): 查询代币余额
   - `EVMCallContract` (spoon-toolkit): 调用智能合约
   - `TokenHolders` (spoon-toolkit): 分析持有者分布（公平性审计）
   - `WalletAnalysis` (spoon-toolkit): 分析钱包资金流向（财务稳定性审计）

3. **开发活动分析工具**:
   - `GetGitHubCommitsTool` (spoon-toolkit): 获取 GitHub 提交数据（开发力审计）
   - `GetGitHubPullRequestsTool` (spoon-toolkit): 获取 PR 数据（开发力审计）
   - `GetGitHubIssuesTool` (spoon-toolkit): 获取 Issues 数据（开发力审计）

4. **隐私存储工具**:
   - `DDCMarketTool` (onchain-verifier skill): 调用 DDC-Market-SDK (ERC-7962) 进行隐私存储

#### 项目结构（基于 spoon-starter 的 react-agent 模板）

```
nft-promise-verification/
├── agent.py                    # VerificationAgent 定义（SpoonReactAI）
├── tools_config.py             # 工具配置（spoon-toolkit）
├── llm_config.py               # LLM 配置（spoon-core LLMManager）
├── scoring/
│   ├── integrity.py            # 诚信审计维度计算
│   ├── fairness.py             # 公平性审计维度计算
│   ├── activity.py             # 开发力审计维度计算
│   ├── stability.py            # 财务稳定性维度计算
│   └── momentum.py             # 社区动能维度计算
├── database/
│   ├── models.py               # SQLite 数据模型
│   ├── db.py                   # 数据库连接和操作
│   └── promise_breaker.db      # SQLite 数据库文件
├── main.py                     # 入口文件
├── config/
│   ├── .env                    # 环境变量（API keys, RPC URLs）
│   └── prompts.yaml            # System prompt 配置
├── requirements.txt            # 依赖
│   ├── spoon-core==0.3.6
│   ├── spoon-toolkit==0.2.5
│   ├── onchain-verifier
│   └── sqlite3 (Python 内置)
└── README.md
```

#### 工作流程

```
用户输入项目信息
    ↓
VerificationAgent (SpoonReactAI)
    ↓
[ReAct 循环 - 五维审计]
    ├─→ 诚信审计维度 (30%)
    │   ├─→ TwitterTool: 抓取 Twitter 承诺
    │   ├─→ WebScraperTool: 爬取官网内容
    │   ├─→ LLM 推理: 提取和分类承诺
    │   ├─→ EVMGetTokenBalance: 查询链上余额
    │   ├─→ EVMCallContract: 查询合约事件
    │   └─→ LLM 推理: 对比承诺与链上数据，计算违约率
    │
    ├─→ 公平性审计维度 (25%)
    │   ├─→ TokenHolders: 获取持有者分布
    │   └─→ LLM 推理: 计算基尼系数，判断中心化风险
    │
    ├─→ 开发力审计维度 (20%)
    │   ├─→ GetGitHubCommitsTool: 获取提交数据
    │   ├─→ GetGitHubPullRequestsTool: 获取 PR 数据
    │   └─→ LLM 推理: 分析开发活跃度，识别"PPT 项目"
    │
    ├─→ 财务稳定性维度 (15%)
    │   ├─→ WalletAnalysis: 分析国库资金流向
    │   └─→ LLM 推理: 识别可疑转账，预警"跑路"风险
    │
    ├─→ 社区动能维度 (10%)
    │   ├─→ TwitterTool: 获取推特互动数据
    │   └─→ LLM 推理: 分析语义随机性，识别 Sybil 攻击
    │
    ├─→ LLM 推理: 计算五维画饼指数
    └─→ DDCMarketTool: 隐私存储结果
    ↓
返回验证报告（包含五维评分详情）
```

#### 后续扩展路径

当 MVP 验证成功后，可以升级为 **Graph + 多 Agent 架构**：
- 使用 spoon-core 的 `StateGraph` 编排工作流
- 将单个 Agent 拆分为 5 个专业 Agent（DataCollectionAgent, PromiseExtractorAgent, VerificationAgent, ScoringAgent, PrivacyStorageAgent）
- 每个 Agent 仍使用 `SpoonReactAI` 模式

### 数据处理与格式化规范

#### 数据格式化流程

**1. Twitter 数据格式化**:
```json
// TwitterTool 原始输出
{
    "tweet_id": "1234567890",
    "text": "We will airdrop 1000 tokens to all holders by Q1 2024",
    "created_at": "2023-10-15T10:30:00Z",
    "author": "@NFTProject",
    "likes": 1500,
    "retweets": 300
}

// 格式化后（统一承诺格式）
{
    "promise_id": "uuid-generated",
    "content": "We will airdrop 1000 tokens to all holders by Q1 2024",
    "source": "twitter",
    "source_url": "https://twitter.com/NFTProject/status/1234567890",
    "published_at": "2023-10-15T10:30:00Z",
    "promise_type": "airdrop",  // LLM 识别
    "target_date": "2024-03-31",  // LLM 提取
    "metadata": {
        "engagement": {"likes": 1500, "retweets": 300}
    }
}
```

**2. 官网数据格式化**:
```json
// WebScraperTool 返回 markdown
"""
# Roadmap
## Q1 2024
- Launch NFT marketplace
- Airdrop utility tokens
"""

// 格式化后（每个承诺一条记录）
[
    {
        "promise_id": "uuid-1",
        "content": "Launch NFT marketplace",
        "source": "website",
        "source_url": "https://nftproject.com/roadmap",
        "published_at": "2023-10-01T00:00:00Z",
        "promise_type": "feature_development",
        "target_date": "2024-03-31",
        "metadata": {"section": "Roadmap > Q1 2024"}
    }
]
```

#### 去重逻辑

**去重规则**:
1. **完全相同文本**: 合并，保留所有来源
2. **语义相似度 > 0.9**: 合并，保留最早发布时间
3. **多来源相同承诺**: 合并为一条，sources 字段记录所有来源

**去重后格式**:
```json
{
    "promise_id": "uuid-generated",
    "content": "Airdrop utility tokens",
    "sources": [
        {
            "type": "twitter",
            "url": "https://twitter.com/NFTProject/status/1234567890",
            "published_at": "2023-10-15T10:30:00Z"
        },
        {
            "type": "website",
            "url": "https://nftproject.com/roadmap",
            "published_at": "2023-10-01T00:00:00Z"
        }
    ],
    "promise_type": "airdrop",
    "target_date": "2024-03-31"
}
```

#### DDC-Market-SDK 输入格式

**承诺数据存储格式**:
```json
{
    "data_type": "promise_archive",
    "project_id": "nft-project-uuid",
    "project_name": "Bored Ape Yacht Club",
    "timestamp": "2024-01-29T10:00:00Z",
    "promises": [
        {
            "promise_id": "uuid-1",
            "content": "...",
            "sources": [...],
            "promise_type": "...",
            "target_date": "..."
        }
    ],
    "data_hash": "sha256-hash",
    "signature": "eip-191-signature"
}
```

**验证结果存储格式**:
```json
{
    "data_type": "verification_result",
    "project_id": "nft-project-uuid",
    "project_name": "Bored Ape Yacht Club",
    "verification_time": "2024-01-29T12:00:00Z",
    "promise_breaking_index": 35,
    "summary": {
        "total_promises": 10,
        "fulfilled": 7,
        "unfulfilled": 2,
        "unverifiable": 1
    },
    "details": [...],
    "data_hash": "sha256-hash",
    "signature": "eip-191-signature"
}
```

**数据大小限制**:
- 单次存储上限: 1MB
- 超过限制时: 分批存储，每批最多 50 条承诺
- 使用 `data_batch_id` 关联多批数据

### 画饼指数五维计算模型

本项目采用基于**第一性原理**的五维审计模型计算画饼指数，全面评估 NFT 项目的可信度。

#### 五维模型设计

**1. 诚信审计维度 (Integrity) - 权重 30%**

**第一性原理**: "真理在时空轴上不具备矛盾性"

**逻辑推导**: 如果项目方在 t0 时刻承诺空投 x，但 t1 时刻链上仅观测到 y 且 x > y，则该系统存在"逻辑坍塌"，信用扣除。

**工具支持**:
- `TwitterTool`: 抓取 Twitter 承诺
- `WebScraperTool`: 抓取官网承诺
- `EVMGetTokenBalance`: 查询实际空投数量
- `EVMCallContract`: 查询合约事件

**计算逻辑**:
```python
def calculate_integrity_score(promises, onchain_data):
    violations = []
    for promise in promises:
        promised_amount = extract_amount(promise.content)  # x
        actual_amount = query_onchain_amount(onchain_data)  # y
        if actual_amount < promised_amount:
            violation_ratio = (promised_amount - actual_amount) / promised_amount
            violations.append(violation_ratio)

    integrity_score = 100 * (1 - mean(violations))
    return integrity_score
```

**2. 公平性审计维度 (Fairness) - 权重 25%**

**第一性原理**: "系统性风险与权力集中度成正比"

**逻辑推导**: 去中心化是 Web3 的物理屏障。通过计算财富分布的基尼系数 (Gini Coefficient)，如果 Gini > 0.7，则判定该项目方保留了随时摧毁系统的"物理开关"。

**工具支持**:
- `TokenHolders`: 获取代币持有者分布数据

**计算逻辑**:
```python
def calculate_fairness_score(token_address):
    holders_data = TokenHolders().execute(token_address, limit=1000)
    gini = calculate_gini_coefficient(holders_data)

    if gini > 0.7:
        fairness_score = 0  # 存在"物理开关"风险
    else:
        fairness_score = 100 * (1 - gini / 0.7)

    return fairness_score
```

**3. 开发力审计维度 (Activity) - 权重 20%**

**第一性原理**: "逻辑的有序堆叠是无法伪造的生命能量损耗"

**逻辑推导**: 高质量的代码提交（Commits）需要真实的开发者时间成本。通过分析 GitHub 的代码密度和 PR 频率，可以识别出项目是"长期主义"还是"PPT 割韭菜"。

**工具支持**:
- `GetGitHubCommitsTool`: 获取提交数据
- `GetGitHubPullRequestsTool`: 获取 PR 数据
- `GetGitHubIssuesTool`: 获取 Issues 数据

**计算逻辑**:
```python
def calculate_activity_score(github_repo):
    # 分析最近 3 个月的开发活动
    commits = GetGitHubCommitsTool().execute(
        owner=repo_owner,
        repo=repo_name,
        start_date=three_months_ago,
        end_date=today
    )
    prs = GetGitHubPullRequestsTool().execute(...)

    commits_count = commits['total_count']
    prs_count = prs['total_count']

    # 活跃度评分
    if commits_count > 100 and prs_count > 20:
        activity_score = 100  # 高度活跃（长期主义）
    elif commits_count > 50 and prs_count > 10:
        activity_score = 70   # 中度活跃
    elif commits_count > 10:
        activity_score = 40   # 低度活跃
    else:
        activity_score = 0    # 几乎无活动（PPT 项目）

    return activity_score
```

**4. 财务稳定性维度 (Stability) - 权重 15%**

**第一性原理**: "金钱的流向定义了组织的真实动机"

**逻辑推导**: 国库资金流向洗币协议或新个人地址是"跑路"的物理前兆；流向研发地址则是"建设"的特征。

**工具支持**:
- `WalletAnalysis`: 分析国库钱包资金流向

**计算逻辑**:
```python
def calculate_stability_score(treasury_address):
    # 分析国库地址的大额转账（>100 USD）
    balance_updates = WalletAnalysis().execute(treasury_address)

    suspicious_transfers = []
    for update in balance_updates:
        if is_mixer_address(update.to_address):
            suspicious_transfers.append(update)  # 流向洗币协议
        elif is_new_personal_address(update.to_address):
            suspicious_transfers.append(update)  # 流向新个人地址

    if len(balance_updates) == 0:
        stability_score = 50  # 无数据，中性评分
    else:
        stability_score = 100 * (1 - len(suspicious_transfers) / len(balance_updates))

    return stability_score
```

**5. 社区动能维度 (Momentum) - 权重 10%**

**第一性原理**: "真实的用户共识是随机波动的，机器人的共识是机械低熵的"

**逻辑推导**: 通过 LLM 分析推特互动的语义随机性。如果大量回复是高度重复的"Good project"，则判定为 Sybil 攻击。

**工具支持**:
- `TwitterTool`: 获取推特互动数据

**计算逻辑**:
```python
def calculate_momentum_score(project_tweet_id, llm):
    replies = TwitterTool().get_replies(project_tweet_id)

    prompt = f"""
    分析以下推特回复的真实性（0-100分）：
    {replies}

    判断标准：
    1. 语义多样性（真实用户会有不同观点）
    2. 情感随机性（真实用户情感波动）
    3. 重复模式（机器人会高度重复"Good project"）

    返回真实性评分（0-100）
    """

    momentum_score = llm.analyze(prompt)
    return momentum_score
```

#### 最终画饼指数计算公式

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
- **0-20**: 优秀（几乎不画饼，项目可信度高）
- **21-40**: 良好（轻度画饼，项目基本可信）
- **41-60**: 一般（中度画饼，需谨慎评估）
- **61-80**: 较差（重度画饼，存在较大风险）
- **81-100**: 极差（严重画饼，强烈建议规避）

#### 边界情况处理

**情况 1**: 所有承诺都"无法验证"
```python
if total_verifiable_count == 0:
    promise_breaking_index = 50  # 中性分数
    note = "所有承诺均无法验证，无法评估项目可信度"
```

**情况 2**: 项目没有做任何承诺
```python
if total_promises == 0:
    promise_breaking_index = None
    note = "项目未做任何公开承诺，无法评估"
```

**情况 3**: 缺少 GitHub 仓库信息
```python
if github_repo is None:
    activity_score = 50  # 中性分数
    note = "未提供 GitHub 仓库信息，开发力维度使用中性评分"
```

**情况 4**: 缺少国库地址信息
```python
if treasury_address is None:
    stability_score = 50  # 中性分数
    note = "未提供国库地址信息，财务稳定性维度使用中性评分"
```

### SQLite 数据库设计（轻量化方案）

#### 数据表结构

**1. projects 表（NFT 项目）**
```sql
CREATE TABLE projects (
    id TEXT PRIMARY KEY,                    -- UUID
    name TEXT NOT NULL,                     -- 项目名称
    twitter_account TEXT,                   -- Twitter 账号
    website_url TEXT,                       -- 官网 URL
    whitepaper_url TEXT,                    -- 白皮书链接
    contract_address TEXT,                  -- 合约地址
    github_repo TEXT,                       -- GitHub 仓库（owner/repo）
    treasury_address TEXT,                  -- 国库地址
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_verified_at TIMESTAMP
);
```

**2. promises 表（承诺）**
```sql
CREATE TABLE promises (
    id TEXT PRIMARY KEY,                    -- UUID
    project_id TEXT NOT NULL,               -- 关联项目
    content TEXT NOT NULL,                  -- 承诺内容
    sources TEXT NOT NULL,                  -- JSON: 来源列表
    promise_type TEXT,                      -- 承诺类型
    target_date DATE,                       -- 目标时间
    verification_status TEXT,               -- 已兑现/未兑现/无法验证
    importance_weight REAL DEFAULT 1.0,     -- 重要性权重
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id)
);
```

**3. verification_records 表（验证记录）**
```sql
CREATE TABLE verification_records (
    id TEXT PRIMARY KEY,                    -- UUID
    project_id TEXT NOT NULL,               -- 关联项目
    verification_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    promise_breaking_index REAL,            -- 画饼指数（0-100）

    -- 五维评分
    integrity_score REAL,                   -- 诚信审计得分
    fairness_score REAL,                    -- 公平性审计得分
    activity_score REAL,                    -- 开发力审计得分
    stability_score REAL,                   -- 财务稳定性得分
    momentum_score REAL,                    -- 社区动能得分

    -- 统计数据
    total_promises INTEGER,
    fulfilled_count INTEGER,
    unfulfilled_count INTEGER,
    unverifiable_count INTEGER,

    -- 详细报告（JSON）
    report_details TEXT,                    -- JSON: 详细分析

    FOREIGN KEY (project_id) REFERENCES projects(id)
);
```

**4. privacy_storage_records 表（隐私存储记录）**
```sql
CREATE TABLE privacy_storage_records (
    id TEXT PRIMARY KEY,                    -- UUID
    project_id TEXT NOT NULL,               -- 关联项目
    storage_type TEXT NOT NULL,             -- promise_archive / verification_result
    storage_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    tx_hash TEXT,                           -- 链上交易哈希
    privacy_address TEXT,                   -- 隐私接收地址
    data_hash TEXT,                         -- 数据摘要（SHA256）
    storage_status TEXT DEFAULT 'pending',  -- pending / completed / failed

    FOREIGN KEY (project_id) REFERENCES projects(id)
);
```

#### 数据库操作示例

**插入项目**:
```python
import sqlite3
import uuid
from datetime import datetime

def create_project(name, twitter_account, website_url, contract_address):
    conn = sqlite3.connect('database/promise_breaker.db')
    cursor = conn.cursor()

    project_id = str(uuid.uuid4())
    cursor.execute("""
        INSERT INTO projects (id, name, twitter_account, website_url, contract_address)
        VALUES (?, ?, ?, ?, ?)
    """, (project_id, name, twitter_account, website_url, contract_address))

    conn.commit()
    conn.close()
    return project_id
```

**保存验证记录**:
```python
def save_verification_record(project_id, scores, statistics, report_details):
    conn = sqlite3.connect('database/promise_breaker.db')
    cursor = conn.cursor()

    record_id = str(uuid.uuid4())
    promise_breaking_index = 100 - (
        scores['integrity'] * 0.30 +
        scores['fairness'] * 0.25 +
        scores['activity'] * 0.20 +
        scores['stability'] * 0.15 +
        scores['momentum'] * 0.10
    )

    cursor.execute("""
        INSERT INTO verification_records (
            id, project_id, promise_breaking_index,
            integrity_score, fairness_score, activity_score,
            stability_score, momentum_score,
            total_promises, fulfilled_count, unfulfilled_count,
            unverifiable_count, report_details
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        record_id, project_id, promise_breaking_index,
        scores['integrity'], scores['fairness'], scores['activity'],
        scores['stability'], scores['momentum'],
        statistics['total'], statistics['fulfilled'],
        statistics['unfulfilled'], statistics['unverifiable'],
        json.dumps(report_details)
    ))

    conn.commit()
    conn.close()
    return record_id
```

**查询项目历史记录**:
```python
def get_project_history(project_id):
    conn = sqlite3.connect('database/promise_breaker.db')
    cursor = conn.cursor()

    cursor.execute("""
        SELECT verification_time, promise_breaking_index,
               integrity_score, fairness_score, activity_score,
               stability_score, momentum_score
        FROM verification_records
        WHERE project_id = ?
        ORDER BY verification_time DESC
    """, (project_id,))

    records = cursor.fetchall()
    conn.close()
    return records
```

## Dependencies

### 核心框架依赖
- **SpoonOS Framework**:
  - **spoon-core** (v0.3.6): 提供 Agent 系统、LLM 管理、工具系统、Graph 工作流
  - **spoon-toolkit** (v0.2.5): 提供 50+ 区块链和 AI 工具（TwitterTool, WebScraperTool, EVM 工具等）
  - **spoon-starter** (v0.1.0): 提供项目模板和最佳实践参考

### 隐私与链上存储
- **DDC-Market-SDK** (ERC-7962):
  - 用途 1: 验证结果上链存储（优先级最高）- 将画饼指数、验证报告等敏感数据通过隐私接口存储到链上，保护验证者身份
  - 用途 2: 承诺数据的隐私存档 - 将项目承诺数据（Twitter、官网、白皮书）通过隐私接口存储，防止项目方事后删除或修改
- **onchain-verifier skill**:
  - 调用时机 1: 生成验证报告后，调用 DDC-Market-SDK 存储验证结果
  - 调用时机 2: 数据收集阶段，调用 DDC-Market-SDK 存储承诺数据
  - 功能: 在上链前对原始数据进行格式化、去重、结构化处理（数据清洗）

### 数据源与服务
- **社交媒体数据源**: 需要访问 Twitter 等社交媒体平台的公开数据（使用 spoon-toolkit 的 TwitterTool）
- **区块链数据服务**: 需要查询 Ethereum 区块链的链上数据（Mainnet 和 Sepolia Testnet），通过 Infura、Alchemy 或自建 RPC 节点
- **文档解析能力**: 需要解析 PDF 格式的白皮书文档
- **自然语言处理**: 需要识别和分类文本中的承诺内容
- **数据持久化**: 使用 **SQLite** 轻量化数据库存储项目信息、承诺数据和验证记录
  - 优势: 零配置、单文件存储、支持 JSON 字段、适合 MVP 快速开发
  - 后续可迁移至 PostgreSQL 或其他数据库
- **Web 界面**: 需要提供用户友好的可视化界面

## Clarifications *(mandatory)*

本节记录在规格澄清过程中解决的关键问题和做出的设计决策。

### Session 2026-01-29

#### Q1: 区块链网络选择 - 系统应该支持哪个区块链网络？

**背景**: 原规格文档中包含 BSN（Blockchain Service Network）相关内容，需要明确实际使用的区块链网络。

**决策**: **Ethereum Mainnet + Sepolia Testnet**

**理由**:
1. **Mainnet 用于生产环境**: 查询真实 NFT 项目的链上数据，确保验证结果的真���性和可信度
2. **Sepolia 作为测试网**: Sepolia 是以太坊官方推荐的测试网（Goerli 已于 2023 年弃用），用于开发测试和功能验证
3. **双网络支持的优势**:
   - 开发阶段可以在 Sepolia 上进行低成本测试
   - 生产环境切换到 Mainnet 无需修改核心代码
   - 便于 CI/CD 流程中的自动化测试
4. **工具链兼容性**: spoon-toolkit 的 EVM 工具原生支持以太坊网络，无需额外适配

**影响范围**:
- FR-007: 更新为支持 Ethereum Mainnet 和 Sepolia Testnet
- SC-010: 更新为支持两种以太坊网络环境
- Assumptions: 更新为依赖 Ethereum RPC 节点服务
- Dependencies: 更新为使用 Infura、Alchemy 或自建 RPC 节点
- Edge Cases: 多链项目处理示例更新为 Ethereum Mainnet 和 Polygon

#### Q2: RPC 节点配置 - 如何配置以太坊 RPC 节点？

**决策**: **支持多种 RPC 提供商，通过环境变量配置**

**配置方案**:
```bash
# .env 文件配置示例
ETHEREUM_MAINNET_RPC_URL=https://mainnet.infura.io/v3/YOUR_PROJECT_ID
ETHEREUM_SEPOLIA_RPC_URL=https://sepolia.infura.io/v3/YOUR_PROJECT_ID

# 或使用 Alchemy
ETHEREUM_MAINNET_RPC_URL=https://eth-mainnet.g.alchemy.com/v2/YOUR_API_KEY
ETHEREUM_SEPOLIA_RPC_URL=https://eth-sepolia.g.alchemy.com/v2/YOUR_API_KEY

# 或使用自建节点
ETHEREUM_MAINNET_RPC_URL=http://localhost:8545
ETHEREUM_SEPOLIA_RPC_URL=http://localhost:8546
```

**理由**:
1. **灵活性**: 支持多种 RPC 提供商，用户可根据需求选择
2. **成本控制**: Infura 和 Alchemy 提供免费额度，适合 MVP 阶段
3. **可扩展性**: 后续可轻松切换到自建节点或其他提供商
4. **安全性**: API Key 通过环境变量管理，不暴露在代码中

#### Q3: EVM 工具网络参数 - spoon-toolkit 的 EVM 工具如何指定网络？

**决策**: **通过 `network` 参数或 `rpc_url` 参数指定网络**

**使用示例**:
```python
# 方式 1: 使用预定义网络名称
from spoon_toolkit.crypto import EVMGetTokenBalance

balance_tool = EVMGetTokenBalance()
result = balance_tool.execute(
    address="0x1234...",
    token_address="0x5678...",
    network="ethereum-mainnet"  # 或 "ethereum-sepolia"
)

# 方式 2: 直接指定 RPC URL
result = balance_tool.execute(
    address="0x1234...",
    token_address="0x5678...",
    rpc_url=os.getenv("ETHEREUM_MAINNET_RPC_URL")
)
```

**理由**:
1. **一致性**: 与 spoon-toolkit 的工具接口保持一致
2. **可测试性**: 测试时可轻松切换到 Sepolia 网络
3. **环境隔离**: 开发、测试、生产环境使用不同的 RPC 配置


## Out of Scope

以下功能不在本次开发范围内：

- 用户账号系统和权限管理（初期版本不需要登录）
- 社区评论和评分功能
- 项目方申诉和反馈机制
- 实时监控和自动预警功能
- 移动端原生应用
- 多语言界面支持（初期仅支持中文）
- 与其他 NFT 分析平台的数据集成
- 项目方认证和官方标识
- 付费订阅和高级功能
