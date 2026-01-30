# Implementation Plan: NFT 项目承诺验证系统（画饼识破）

**Branch**: `001-nft-promise-verification` | **Date**: 2026-01-30 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-nft-promise-verification/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

本项目旨在构建一个基于 SpoonOS 框架的 NFT 项目承诺验证系统，通过自动化收集项目方在 Twitter、官网和白皮书中的公开承诺，并与链上实际行为进行对比，计算"画饼指数"（0-100分）来评估项目可信度。

**核心技术方案**：
- 采用 **单 Agent + 多工具** 架构（SpoonReactAI）
- 使用 **五维审计模型**（诚信、公平性、开发力、财务稳定性、社区动能）
- 通过 **DDC-Market-SDK (ERC-7962)** 实现验证结果的隐私存储
- 使用 **SQLite** 轻量化数据库存储项目信息和历史记录
- 支持 **Ethereum Mainnet 和 Sepolia Testnet** 双网络环境

## Technical Context

**Language/Version**: Python 3.11 (conda 环境: hackason)
**Primary Dependencies**:
- SpoonOS Framework: spoon-core (v0.3.6), spoon-toolkit (v0.2.5), spoon-starter (v0.1.0)
- Web Framework: FastAPI (API 服务)
- Blockchain: Web3.py, DDC-Market-SDK (ERC-7962)
- LLM: GPT-4 Turbo (通过 spoon-core LLMManager)
- Frontend: Next.js + TypeScript (Phase 4)

**Storage**: SQLite (轻量化数据库，单文件存储，支持 JSON 字段)
**Testing**: pytest (Python 单元测试和集成测试)
**Target Platform**: Linux server (开发环境: WSL2)
**Project Type**: Web application (backend + frontend)
**Performance Goals**:
- 承诺收集: 5 分钟内完成单个项目
- 链上验证: 10 分钟内完成验证对比
- 并发处理: 支持 10 个项目同时验证
- 查询响应: <2 秒（历史记录查询）

**Constraints**:
- Twitter API 限流: 需要处理 API 限流和降级方案
- RPC 节点稳定性: 依赖 Infura/Alchemy 免费额度
- LLM Token 限制: 需要数据清洗和紧凑格式化
- 数据大小限制: DDC-Market-SDK 单次存储上限 1MB

**Scale/Scope**:
- MVP 阶段: 支持 100 个项目验证
- 数据库容量: 至少 1000 个项目历史记录
- 承诺识别准确率: >80%
- 链上查询成功率: >95%

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Verify compliance with [Promise Breaker Detector Constitution v1.0.0](../../.specify/memory/constitution.md):

- [x] **Immutability First**: 所有数据转换使用不可变模式（数据格式化、去重逻辑均返回新对象）
- [x] **File Organization**: 按功能/领域组织文件（scoring/, database/, tools_config.py），每个文件 <800 行
- [x] **Error Handling**: 所有异步操作（Twitter 抓取、链上查询、DDC 存储）都有 try-catch 和用户友好错误提示
- [x] **Input Validation**: 所有用户输入（项目信息、地址）使用 Pydantic 模型验证
- [x] **Code Quality**: 函数 <50 行（五维评分函数独立），无深层嵌套，无硬编码值（使用 .env）
- [x] **Security**: 无硬编码密钥（API keys 在 .env），所有输入验证，SQLite 使用参数化查询
- [x] **Python Environment**: 所有 Python 代码使用 `hackason` conda 环境
- [x] **Git Workflow**: 使用 Conventional Commits 格式，中文提交信息

**Violations** (if any, must be justified in Complexity Tracking section):
- 无违规项。本项目架构完全符合宪法要求。

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
nft-promise-verification/          # 新建项目目录
├── agent.py                        # VerificationAgent 定义（SpoonReactAI）
├── tools_config.py                 # 工具配置（spoon-toolkit）
├── llm_config.py                   # LLM 配置（spoon-core LLMManager）
├── main.py                         # 入口文件
├── scoring/                        # 五维评分模块
│   ├── __init__.py
│   ├── integrity.py                # 诚信审计维度计算
│   ├── fairness.py                 # 公平性审计维度计算
│   ├── activity.py                 # 开发力审计维度计算
│   ├── stability.py                # 财务稳定性维度计算
│   └── momentum.py                 # 社区动能维度计算
├── database/                       # 数据库模块
│   ├── __init__.py
│   ├── models.py                   # SQLite 数据模型（Pydantic）
│   ├── db.py                       # 数据库连接和操作
│   └── promise_breaker.db          # SQLite 数据库文件（运行时生成）
├── utils/                          # 工具函数
│   ├── __init__.py
│   ├── data_formatter.py           # 数据格式化（Twitter、官网数据）
│   ├── deduplicator.py             # 去重逻辑
│   └── validators.py               # 输入验证（Pydantic schemas）
├── config/                         # 配置文件
│   ├── .env                        # 环境变量（API keys, RPC URLs）
│   ├── .env.example                # 环境变量模板
│   └── prompts.yaml                # System prompt 配置
├── tests/                          # 测试目录
│   ├── unit/                       # 单元测试
│   │   ├── test_scoring.py
│   │   ├── test_data_formatter.py
│   │   └── test_deduplicator.py
│   ├── integration/                # 集成测试
│   │   ├── test_agent.py
│   │   └── test_database.py
│   └── fixtures/                   # 测试数据
│       └── sample_promises.json
├── requirements.txt                # Python 依赖
│   # spoon-core==0.3.6
│   # spoon-toolkit==0.2.5
│   # fastapi
│   # web3
│   # pydantic
│   # pytest
└── README.md                       # 项目说明

frontend/                           # 前端项目（Phase 4）
├── src/
│   ├── components/                 # React 组件
│   ├── pages/                      # Next.js 页面
│   └── services/                   # API 调用服务
└── tests/
```

**Structure Decision**:
- 采用 **Web application** 结构（backend + frontend 分离）
- Backend 使用 Python + SpoonOS 框架，按功能模块组织（scoring/, database/, utils/）
- Frontend 使用 Next.js + TypeScript（Phase 4 实现）
- 所有文件遵循 <800 行限制，复杂逻辑拆分为独立模块

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
