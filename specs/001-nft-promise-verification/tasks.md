# Tasks: NFT 项目承诺验证系统（画饼识破）

**Feature**: 001-nft-promise-verification
**Input**: Design documents from `/specs/001-nft-promise-verification/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/cli-interface.md

**Tests**: 本项目不包含测试任务（未在规格中明确要求）

**Organization**: 任务按用户故事组织,每个故事可独立实现和测试

## Format: `[ID] [P?] [Story] Description`

- **[P]**: 可并行执行（不同文件,无依赖）
- **[Story]**: 任务所属用户故事（US1, US2, US3, US4）
- 包含精确的文件路径

## Path Conventions

本项目采用单项目结构,所有代码位于 `nft-promise-verification/` 目录下:
- 核心代码: `nft-promise-verification/`
- 数据库: `nft-promise-verification/database/`
- 评分模块: `nft-promise-verification/scoring/`
- 工具函数: `nft-promise-verification/utils/`
- 配置: `nft-promise-verification/config/`

---

## Phase 1: Setup (项目初始化)

**Purpose**: 创建项目结构和基础配置

- [X] T001 创建项目目录结构 nft-promise-verification/ 及子目录 (scoring/, database/, utils/, config/, tests/)
- [X] T002 创建 requirements.txt 文件,包含所有依赖 (spoon-core==0.3.6, spoon-toolkit==0.2.5, fastapi, web3, pydantic, sqlite3, snscrape, beautifulsoup4, anthropic, structlog, python-dotenv, pytest)
- [X] T003 [P] 创建 .env.example 模板文件在 nft-promise-verification/config/.env.example
- [X] T004 [P] 创建 .gitignore 文件,排除 .env, *.db, __pycache__, .pytest_cache
- [X] T005 [P] 创建 README.md 文件,包含项目概述和快速开始指南

---

## Phase 2: Foundational (核心基础设施)

**Purpose**: 必须完成的核心基础设施,阻塞所有用户故事

**⚠️ CRITICAL**: 所有用户故事工作必须等待此阶段完成

- [X] T006 创建数据库 Schema 初始化脚本 nft-promise-verification/database/init_db.py (创建 projects, promises, verification_records, privacy_storage_records 表及索引)
- [X] T007 [P] 创建 Pydantic 数据模型 nft-promise-verification/database/models.py (NFTProject, Promise, VerificationRecord, PrivacyStorageRecord, 包含所有验证器)
- [X] T008 [P] 创建数据库操作模块 nft-promise-verification/database/db.py (连接管理, CRUD 操作, 参数化查询)
- [X] T009 [P] 创建输入验证模块 nft-promise-verification/utils/validators.py (Pydantic schemas for user input)
- [X] T010 [P] 创建 LLM 配置模块 nft-promise-verification/llm_config.py (LLMManager 初始化, Claude 3.5 Sonnet 优先, GPT-4 备用)
- [X] T011 [P] 创建日志配置模块 nft-promise-verification/utils/logger.py (structlog 配置, JSON 格式输出)
- [X] T012 [P] 创建环境变量加载模块 nft-promise-verification/config/settings.py (python-dotenv + Pydantic Settings)
- [X] T013 运行数据库初始化脚本,创建 nft-promise-verification/database/promise_breaker.db

**Checkpoint**: 基础设施就绪 - 用户故事实现可以并行开始

---

## Phase 3: User Story 1 - 项目承诺收集与初步验证 (Priority: P1) 🎯 MVP

**Goal**: 用户输入 NFT 项目信息后,系统自动收集 Twitter 和官网的公开承诺,生成结构化承诺清单

**Independent Test**: 输入 "Bored Ape Yacht Club" 项目信息,验证系统能成功抓取 Twitter 和官网承诺,并以 table/json/markdown 格式展示

### 数据收集工具实现

- [X] T014 [P] [US1] 创建 Twitter 数据抓取工具 nft-promise-verification/tools/twitter_scraper.py (使用 snscrape, 包含请求延迟和错误处理)
- [X] T015 [P] [US1] 创建网页爬取工具 nft-promise-verification/tools/web_scraper.py (使用 BeautifulSoup4, 支持 markdown 格式输出)
- [X] T016 [P] [US1] 创建承诺提取工具 nft-promise-verification/tools/promise_extractor.py (使用 LLM Few-Shot Prompting, JSON 输出格式)

### 数据处理模块

- [X] T017 [P] [US1] 创建数据格式化模块 nft-promise-verification/utils/data_formatter.py (统一 Twitter 和官网数据为承诺格式)
- [X] T018 [P] [US1] 创建去重逻辑模块 nft-promise-verification/utils/deduplicator.py (完全相同文本合并, 语义相似度 >0.9 合并, 多来源记录)

### Agent 和工具配置

- [X] T019 [US1] 创建工具配置模块 nft-promise-verification/tools_config.py (注册 TwitterTool, WebScraperTool, PromiseExtractorTool)
- [X] T020 [US1] 创建 VerificationAgent 基础实现 nft-promise-verification/agent.py (SpoonReactAI 初始化, 数据收集任务编排)

### CLI 接口实现

- [X] T021 [US1] 创建 CLI 命令解析模块 nft-promise-verification/cli/parser.py (使用 argparse, 支持 collect, list, show, export, version, help 命令)
- [X] T022 [US1] 实现 collect 命令 nft-promise-verification/cli/commands.py (调用 Agent 收集承诺, 支持 --name, --twitter, --website, --output, --format 参数)
- [X] T023 [P] [US1] 实现 list 命令 nft-promise-verification/cli/commands.py (从数据库查询项目列表, 支持 --format, --sort, --limit 参数)
- [X] T024 [P] [US1] 实现 show 命令 nft-promise-verification/cli/commands.py (显示项目详情和承诺清单, 支持过滤和置信度阈值)
- [X] T025 [P] [US1] 实现 export 命令 nft-promise-verification/cli/commands.py (导出为 json/markdown 格式)

### 输出格式化

- [X] T026 [P] [US1] 创建 Table 格式输出模块 nft-promise-verification/cli/formatters.py (使用 Unicode 表格边框)
- [X] T027 [P] [US1] 创建 JSON 格式输出模块 nft-promise-verification/cli/formatters.py
- [X] T028 [P] [US1] 创建 Markdown 格式输出模块 nft-promise-verification/cli/formatters.py

### 主入口

- [X] T029 [US1] 创建 CLI 主入口 nft-promise-verification/main.py (命令路由, 环境变量加载, 错误处理)
- [X] T030 [US1] 添加 CLI 可执行权限和 shebang,创建 promise-breaker 命令别名

**Checkpoint**: User Story 1 完成 - 用户可以收集项目承诺并查看结构化清单

---

## Phase 4: User Story 2 - 链上数据验证与对比 (Priority: P2)

**Goal**: 系统自动查询项目的链上活动数据,并将这些数据与项目承诺进行对比,生成验证报告

**Independent Test**: 选择一个已收集承诺的项目,验证系统能查询链上数据并生成对比报告,显示哪些承诺已兑现/未兑现

### 链上查询工具配置

- [X] T031 [P] [US2] 配置 EVM 工具 nft-promise-verification/tools/evm_tools.py (EVMGetTokenBalance, EVMCallContract, 支持 Ethereum Mainnet 和 Sepolia Testnet)
- [X] T032 [P] [US2] 创建 RPC 节点管理模块 nft-promise-verification/utils/rpc_manager.py (多 RPC 提供商支持, 故障转移逻辑)

### 诚信审计维度实现 (30%)

- [X] T033 [US2] 实现诚信审计评分模块 nft-promise-verification/scoring/integrity.py (对比承诺与链上数据, 计算违约率, 返回 0-100 分)

### 验证逻辑实现

- [X] T034 [US2] 创建承诺验证模块 nft-promise-verification/verification/promise_verifier.py (匹配承诺类型与链上数据, 判断已兑现/未兑现/无法验证)
- [X] T035 [US2] 扩展 VerificationAgent nft-promise-verification/agent.py (添加链上验证任务编排, 调用诚信审计模块)

### 验证报告生成

- [X] T036 [US2] 创建验证报告生成模块 nft-promise-verification/reports/report_generator.py (生成对比报告, 包含承诺清单、验证状态、证据链接)
- [X] T037 [US2] 保存验证记录到数据库 nft-promise-verification/database/db.py (插入 verification_records 表, 更新 promises 表的 verification_status)

### CLI 命令扩展

- [X] T038 [US2] 实现 verify 命令 nft-promise-verification/cli/commands/verify.py (启动链上验证, 支持 --project-id, --network 参数)
- [X] T039 [US2] 扩展 show 命令显示验证结果 nft-promise-verification/cli/commands/show.py (添加验证状态和证据展示)

**Checkpoint**: User Story 2 完成 - 用户可以验证项目承诺并查看对比报告

---

## Phase 5: User Story 3 - 画饼指数计算与报告生成 (Priority: P3)

**Goal**: 系统基于五维审计模型计算项目的画饼指数 (0-100),并生成详细的验证报告

**Independent Test**: 查看一个已验证项目的画饼指数和五维评分,验证评分逻辑合理,报告内容完整清晰

### 五维审计模块实现

- [X] T040 [P] [US3] 实现公平性审计评分模块 nft-promise-verification/scoring/fairness.py (使用 TokenHolders 工具, 计算基尼系数, 判断中心化风险)
- [X] T041 [P] [US3] 实现开发力审计评分模块 nft-promise-verification/scoring/activity.py (使用 GetGitHubCommitsTool, GetGitHubPullRequestsTool, 分析开发活跃度)
- [X] T042 [P] [US3] 实现财务稳定性审计评分模块 nft-promise-verification/scoring/stability.py (使用 WalletAnalysis 工具, 识别可疑转账)
- [X] T043 [P] [US3] 实现社区动能审计评分模块 nft-promise-verification/scoring/momentum.py (使用 TwitterTool + LLM 语义分析, 识别 Sybil 攻击)

### 画饼指数计算

- [X] T044 [US3] 创建画饼指数计算模块 nft-promise-verification/scoring/index_calculator.py (五维加权计算, 处理边界情况: 无承诺/无法验证/缺失数据)
- [X] T045 [US3] 扩展 VerificationAgent nft-promise-verification/agent.py (添加五维审计任务编排, 调用所有评分模块)

### 详细报告生成

- [X] T046 [US3] 扩展报告生成模块 nft-promise-verification/reports/report_generator.py (添加五维评分详情, 画饼指数解读, 建议列表)
- [X] T047 [US3] 创建报告模板 nft-promise-verification/reports/templates/ (table, json, markdown 格式的报告模板)

### CLI 命令扩展

- [X] T048 [US3] 扩展 show 命令显示画饼指数 nft-promise-verification/cli/commands/show.py (添加五维评分和画饼指数展示)
- [X] T049 [US3] 扩展 export 命令支持完整报告 nft-promise-verification/cli/commands/export.py (包含五维评分详情的完整报告)

**Checkpoint**: User Story 3 完成 - 用户可以查看项目的画饼指数和五维评分详情

---

## Phase 6: User Story 4 - 可视化展示与历史记录 (Priority: P4)

**Goal**: 提供 Web 界面查看项目验证结果,并支持查看项目的历史验证记录和趋势

**Independent Test**: 访问前端界面,验证能看到项目列表、验证结果的可视化图表、历史记录时间线

### 后端 API 实现

- [ ] T050 [P] [US4] 创建 FastAPI 应用 nft-promise-verification/api/app.py (初始化 FastAPI, CORS 配置, 路由注册)
- [ ] T051 [P] [US4] 实现项目列表 API nft-promise-verification/api/routes/projects.py (GET /api/v1/projects, 支持分页和排序)
- [ ] T052 [P] [US4] 实现项目详情 API nft-promise-verification/api/routes/projects.py (GET /api/v1/projects/{id}, 返回项目信息和最新验证结果)
- [ ] T053 [P] [US4] 实现历史记录 API nft-promise-verification/api/routes/history.py (GET /api/v1/projects/{id}/history, 返回历史验证记录)
- [ ] T054 [P] [US4] 实现验证任务 API nft-promise-verification/api/routes/verification.py (POST /api/v1/projects/{id}/verify, 异步启动验证任务)

### 前端项目初始化

- [ ] T055 [US4] 创建 Next.js 项目 frontend/ (使用 create-next-app, TypeScript, Tailwind CSS)
- [ ] T056 [P] [US4] 配置 API 调用服务 frontend/src/services/api.ts (axios 封装, 错误处理)

### 前端页面实现

- [ ] T057 [P] [US4] 实现项目列表页面 frontend/src/pages/projects/index.tsx (显示项目卡片, 画饼指数, 最后验证时间)
- [ ] T058 [P] [US4] 实现项目详情页面 frontend/src/pages/projects/[id].tsx (显示五维评分雷达图, 承诺清单, 验证状态)
- [ ] T059 [P] [US4] 实现历史记录页面 frontend/src/pages/projects/[id]/history.tsx (显示画饼指数趋势图, 历史验证记录时间线)

### 可视化组件

- [ ] T060 [P] [US4] 创建五维评分雷达图组件 frontend/src/components/RadarChart.tsx (使用 recharts 或 chart.js)
- [ ] T061 [P] [US4] 创建画饼指数趋势图组件 frontend/src/components/TrendChart.tsx (折线图展示历史变化)
- [ ] T062 [P] [US4] 创建承诺清单组件 frontend/src/components/PromiseList.tsx (表格展示承诺内容、状态、来源)

### 报告导出功能

- [ ] T063 [US4] 实现 PDF 导出功能 nft-promise-verification/api/routes/export.py (GET /api/v1/projects/{id}/export/pdf, 使用 reportlab 或 weasyprint)
- [ ] T064 [US4] 前端添加导出按钮 frontend/src/pages/projects/[id].tsx (调用导出 API, 下载 PDF/JSON 文件)

**Checkpoint**: User Story 4 完成 - 用户可以通过 Web 界面查看验证结果和历史记录

---

## Phase 7: 隐私存储集成 (跨用户故事功能)

**Purpose**: 集成 DDC-Market-SDK (ERC-7962) 实现验证结果和承诺数据的隐私存储

- [ ] T065 [P] 创建 DDC-Market-SDK 工具封装 nft-promise-verification/tools/ddc_market_tool.py (调用 onchain-verifier skill, 数据清洗和格式化)
- [ ] T066 [P] 创建隐私存储模块 nft-promise-verification/privacy/storage.py (承诺数据存档, 验证结果存储, 分批处理 >1MB 数据)
- [ ] T067 扩展 VerificationAgent nft-promise-verification/agent.py (在数据收集后和验证完成后调用隐私存储)
- [ ] T068 保存隐私存储记录到数据库 nft-promise-verification/database/db.py (插入 privacy_storage_records 表, 记录 tx_hash 和 storage_status)

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: 跨用户故事的改进和优化

- [ ] T069 [P] 添加错误处理和用户友好提示 nft-promise-verification/utils/error_handler.py (统一错误格式, 退出码管理)
- [ ] T070 [P] 添加性能监控和日志 nft-promise-verification/utils/performance.py (记录 Agent 执行时间, 工具调用次数)
- [ ] T071 [P] 代码质量检查和重构 (确保所有函数 <50 行, 文件 <800 行, 无硬编码值)
- [ ] T072 [P] 更新 README.md 文档 (添加完整的使用示例, 常见问题解答)
- [ ] T073 [P] 创建 quickstart 验证脚本 nft-promise-verification/scripts/validate_quickstart.sh (验证 quickstart.md 中的所有步骤)
- [ ] T074 安全审查 (检查 API Key 管理, SQL 注入防护, 输入验证)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: 无依赖 - 可立即开始
- **Foundational (Phase 2)**: 依赖 Setup 完成 - **阻塞所有用户故事**
- **User Stories (Phase 3-6)**: 全部依赖 Foundational 完成
  - 用户故事之间可以并行实现（如果有足够人力）
  - 或按优先级顺序实现（P1 → P2 → P3 → P4）
- **隐私存储 (Phase 7)**: 可在任何用户故事完成后集成
- **Polish (Phase 8)**: 依赖所有期望的用户故事完成

### User Story Dependencies

- **User Story 1 (P1)**: Foundational 完成后可开始 - 无其他用户故事依赖
- **User Story 2 (P2)**: Foundational 完成后可开始 - 依赖 US1 的数据收集功能,但可独立测试
- **User Story 3 (P3)**: Foundational 完成后可开始 - 依赖 US2 的验证功能,但可独立测试
- **User Story 4 (P4)**: Foundational 完成后可开始 - 依赖 US1-3 的数据,但可独立测试

### Within Each User Story

- 数据模型 → 服务层 → API/CLI 层
- 工具实现 → Agent 集成
- 核心功能 → 扩展功能
- 每个故事完成后再进入下一个优先级

### Parallel Opportunities

- Setup 阶段所有标记 [P] 的任务可并行
- Foundational 阶段所有标记 [P] 的任务可并行（在 Phase 2 内）
- Foundational 完成后,所有用户故事可并行开始（如果团队容量允许）
- 每个用户故事内标记 [P] 的任务可并行
- 不同用户故事可由不同团队成员并行开发

---

## Parallel Example: User Story 1

```bash
# 并行启动 User Story 1 的所有数据收集工具:
Task: "创建 Twitter 数据抓取工具 nft-promise-verification/tools/twitter_scraper.py"
Task: "创建网页爬取工具 nft-promise-verification/tools/web_scraper.py"
Task: "创建承诺提取工具 nft-promise-verification/tools/promise_extractor.py"

# 并行启动 User Story 1 的所有数据处理模块:
Task: "创建数据格式化模块 nft-promise-verification/utils/data_formatter.py"
Task: "创建去重逻辑模块 nft-promise-verification/utils/deduplicator.py"

# 并行启动 User Story 1 的所有 CLI 命令:
Task: "实现 list 命令 nft-promise-verification/cli/commands/list.py"
Task: "实现 show 命令 nft-promise-verification/cli/commands/show.py"
Task: "实现 export 命令 nft-promise-verification/cli/commands/export.py"

# 并行启动 User Story 1 的所有输出格式化模块:
Task: "创建 Table 格式输出模块 nft-promise-verification/cli/formatters/table_formatter.py"
Task: "创建 JSON 格式输出模块 nft-promise-verification/cli/formatters/json_formatter.py"
Task: "创建 Markdown 格式输出模块 nft-promise-verification/cli/formatters/markdown_formatter.py"
```

---

## Implementation Strategy

### MVP First (仅 User Story 1)

1. 完成 Phase 1: Setup
2. 完成 Phase 2: Foundational（**关键 - 阻塞所有故事**）
3. 完成 Phase 3: User Story 1
4. **停止并验证**: 独立测试 User Story 1
5. 如果就绪则部署/演示

### Incremental Delivery (增量交付)

1. 完成 Setup + Foundational → 基础就绪
2. 添加 User Story 1 → 独立测试 → 部署/演示（**MVP!**）
3. 添加 User Story 2 → 独立测试 → 部署/演示
4. 添加 User Story 3 → 独立测试 → 部署/演示
5. 添加 User Story 4 → 独立测试 → 部署/演示
6. 每个故事都增加价值而不破坏之前的故事

### Parallel Team Strategy (并行团队策略)

如果有多个开发者:

1. 团队一起完成 Setup + Foundational
2. Foundational 完成后:
   - 开发者 A: User Story 1
   - 开发者 B: User Story 2
   - 开发者 C: User Story 3
3. 故事独立完成并集成

---

## Task Summary

### Total Tasks: 74

- **Phase 1 (Setup)**: 5 tasks
- **Phase 2 (Foundational)**: 8 tasks
- **Phase 3 (User Story 1 - P1)**: 17 tasks 🎯 MVP
- **Phase 4 (User Story 2 - P2)**: 9 tasks
- **Phase 5 (User Story 3 - P3)**: 10 tasks
- **Phase 6 (User Story 4 - P4)**: 15 tasks
- **Phase 7 (隐私存储)**: 4 tasks
- **Phase 8 (Polish)**: 6 tasks

### Tasks by User Story

- **User Story 1 (P1)**: 17 tasks - 承诺收集与初步验证
- **User Story 2 (P2)**: 9 tasks - 链上数据验证与对比
- **User Story 3 (P3)**: 10 tasks - 画饼指数计算与报告生成
- **User Story 4 (P4)**: 15 tasks - 可视化展示与历史记录

### Parallel Opportunities Identified

- **Setup**: 3 tasks 可并行 (T003, T004, T005)
- **Foundational**: 6 tasks 可并行 (T007-T012)
- **User Story 1**: 11 tasks 可并行 (T014-T018, T023-T028)
- **User Story 2**: 2 tasks 可并行 (T031-T032)
- **User Story 3**: 4 tasks 可并行 (T040-T043)
- **User Story 4**: 12 tasks 可并行 (T050-T062)
- **隐私存储**: 2 tasks 可并行 (T065-T066)
- **Polish**: 5 tasks 可并行 (T069-T073)

### Suggested MVP Scope

**最小可行产品 (MVP)** 应仅包含:
- Phase 1: Setup (5 tasks)
- Phase 2: Foundational (8 tasks)
- Phase 3: User Story 1 (17 tasks)

**总计**: 30 tasks

这将提供核心价值:用户可以收集 NFT 项目的承诺并查看结构化清单。

---

## Format Validation

✅ **所有任务遵循 Checklist 格式**:
- 每个任务以 `- [ ]` 开头（markdown checkbox）
- 包含任务 ID（T001-T074）
- 可并行任务标记 [P]
- 用户故事任务标记 [US1]-[US4]
- 包含精确的文件路径
- 描述清晰具体

---

## Notes

- **[P] 任务** = 不同文件,无依赖,可并行执行
- **[Story] 标签** = 将任务映射到特定用户故事,便于追溯
- 每个用户故事应该是独立可完成和可测试的
- 在每个 checkpoint 停止以独立验证故事
- 每个任务或逻辑组完成后提交
- 避免:模糊任务、同文件冲突、破坏独立性的跨故事依赖

---

**Document Version**: 1.0.0
**Generated**: 2026-01-30
**Status**: ✅ Ready for Implementation
**Next Step**: 开始 Phase 1 (Setup) 或直接进入 MVP 实现
