# NFT 项目承诺验证系统（画饼识破）

> 基于 SpoonOS 框架的 NFT 项目可信度评估工具

## 📖 项目简介

NFT 项目承诺验证系统（Promise Breaker Detector）是一个自动化工具，通过收集 NFT 项目方在 Twitter、官网和白皮书中的公开承诺，并与链上实际行为进行对比，计算"画饼指数"（0-100分）来评估项目可信度。

### 核心功能

- 🔍 **承诺收集**: 自动抓取项目 Twitter、官网和白皮书中的公开承诺
- ⛓️ **链上验证**: 查询区块链数据，验证承诺是否兑现
- 📊 **五维审计**: 基于诚信、公平性、开发力、财务稳定性、社区动能五个维度评分
- 📈 **画饼指数**: 综合计算项目可信度评分（0-100分）
- 🔒 **隐私存储**: 通过 DDC-Market-SDK (ERC-7962) 实现验证结果的链上隐私存储
- 📜 **历史追踪**: 记录项目历史验证数据，追踪可信度变化趋势

## 🏗️ 技术架构

### 技术栈

- **框架**: SpoonOS 0.3.6 (AI Agent 框架)
- **语言**: Python 3.11
- **数据库**: SQLite (轻量化单文件存储)
- **区块链**: Web3.py + DDC-Market-SDK
- **LLM**: Claude 3.5 Sonnet (优先) / GPT-4 Turbo (备用)
- **前端**: Next.js + TypeScript (Phase 4)

### 架构设计

```text
┌─────────────────────────────────────────────────────────┐
│                    用户输入                              │
│          (项目名称、Twitter、官网、合约地址)              │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              VerificationAgent (SpoonReactAI)           │
│  ┌──────────────────────────────────────────────────┐  │
│  │  数据收集工具                                      │  │
│  │  - TwitterTool: 抓取 Twitter 承诺                 │  │
│  │  - WebScraperTool: 爬取官网内容                   │  │
│  │  - PromiseExtractorTool: LLM 提取承诺             │  │
│  └──────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────┐  │
│  │  链上验证工具                                      │  │
│  │  - EVMGetTokenBalance: 查询代币余额               │  │
│  │  - EVMCallContract: 调用智能合约                  │  │
│  │  - WalletAnalysis: 分析钱包交易                   │  │
│  └──────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────┐  │
│  │  五维评分模块                                      │  │
│  │  - 诚信审计 (30%): 承诺兑现率                     │  │
│  │  - 公平性审计 (20%): 代币分布基尼系数             │  │
│  │  - 开发力审计 (20%): GitHub 活跃度                │  │
│  │  - 财务稳定性 (15%): 国库资金流动                 │  │
│  │  - 社区动能 (15%): Twitter 社区活跃度             │  │
│  └──────────────────────────────────────────────────┘  │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                  SQLite 数据库                           │
│  - projects: 项目信息                                    │
│  - promises: 承诺清单                                    │
│  - verification_records: 验证记录                        │
│  - privacy_storage_records: 隐私存储记录                 │
└─────────────────────────────────────────────────────────┘
```

## 🚀 快速开始

### 环境要求

- Python 3.11+
- Conda (推荐使用 conda 虚拟环境)
- Git

### 安装步骤

1. **克隆项目**

```bash
git clone https://github.com/your-org/hackason-project.git
cd hackason-project/nft-promise-verification
```

2. **创建并激活 Conda 环境**

```bash
conda create -n hackason python=3.11
conda activate hackason
```

3. **安装依赖**

```bash
pip install -r requirements.txt
```

4. **配置环境变量**

```bash
cp config/.env.example config/.env
# 编辑 config/.env 文件，填入你的 API 密钥
```

必需的环境变量:
- `ANTHROPIC_API_KEY`: Claude API 密钥
- `OPENAI_API_KEY`: OpenAI API 密钥 (备用)
- `ETH_MAINNET_RPC_URL`: Ethereum Mainnet RPC URL
- `BSN_DDC_API_KEY`: BSN-DDC API 密钥 (用于隐私存储)

5. **初始化数据库**

```bash
python -m nft_promise_verification.database.init_db
```

### 使用示例

#### 1. 收集项目承诺

```bash
# 收集 Bored Ape Yacht Club 项目的承诺
python main.py collect \
  --name "Bored Ape Yacht Club" \
  --twitter "@BoredApeYC" \
  --website "https://boredapeyachtclub.com" \
  --contract "0xBC4CA0EdA7647A8aB7C2061c2E118A18a936f13D" \
  --format table
```

#### 2. 查看项目列表

```bash
# 查看所有已收集的项目
python main.py list --format table --sort created_at --limit 10
```

#### 3. 查看项目详情

```bash
# 查看特定项目的承诺清单
python main.py show <project-id> --format markdown
```

#### 4. 验证项目承诺

```bash
# 启动链上验证
python main.py verify <project-id> --network mainnet
```

#### 5. 导出验证报告

```bash
# 导出为 JSON 格式
python main.py export <project-id> --format json --output report.json

# 导出为 Markdown 格式
python main.py export <project-id> --format markdown --output report.md
```

## 📊 五维审计模型

### 1. 诚信审计 (30%)

评估项目承诺的兑现情况:
- 承诺总数
- 已兑现承诺数
- 未兑现承诺数
- 无法验证承诺数
- **评分公式**: `(已兑现数 / 可验证承诺数) * 100`

### 2. 公平性审计 (20%)

评估代币分布的公平性:
- 计算代币持有者的基尼系数
- 识别中心化风险（Top 10 持有者占比）
- **评分公式**: `(1 - 基尼系数) * 100`

### 3. 开发力审计 (20%)

评估项目开发活跃度:
- GitHub 提交频率
- Pull Request 数量
- 活跃贡献者数量
- **评分公式**: 基于开发活跃度指标综合计算

### 4. 财务稳定性 (15%)

评估项目财务健康度:
- 国库资金余额
- 可疑大额转账
- 资金流动趋势
- **评分公式**: 基于财务风险指标综合计算

### 5. 社区动能 (15%)

评估社区活跃度和真实性:
- Twitter 互动率
- 社区情绪分析
- Sybil 攻击检测
- **评分公式**: 基于社区活跃度和真实性综合计算

### 画饼指数计算

```
画饼指数 = 诚信审计 * 0.3 + 公平性审计 * 0.2 + 开发力审计 * 0.2
          + 财务稳定性 * 0.15 + 社区动能 * 0.15
```

**评分解读**:
- **80-100分**: 优秀 - 项目高度可信，承诺兑现率高
- **60-79分**: 良好 - 项目基本可信，存在少量未兑现承诺
- **40-59分**: 一般 - 项目可信度中等，需谨慎评估
- **20-39分**: 较差 - 项目存在较多未兑现承诺，风险较高
- **0-19分**: 极差 - 项目严重"画饼"，强烈建议规避

## 🗂️ 项目结构

```text
nft-promise-verification/
├── agent.py                 # VerificationAgent 定义
├── tools_config.py          # 工具配置
├── llm_config.py            # LLM 配置
├── main.py                  # CLI 入口
├── scoring/                 # 五维评分模块
│   ├── integrity.py         # 诚信审计
│   ├── fairness.py          # 公平性审计
│   ├── activity.py          # 开发力审计
│   ├── stability.py         # 财务稳定性审计
│   └── momentum.py          # 社区动能审计
├── database/                # 数据库模块
│   ├── models.py            # 数据模型
│   ├── db.py                # 数据库操作
│   └── init_db.py           # 数据库初始化
├── utils/                   # 工具函数
│   ├── data_formatter.py    # 数据格式化
│   ├── deduplicator.py      # 去重逻辑
│   └── validators.py        # 输入验证
├── cli/                     # CLI 命令
│   ├── commands/            # 命令实现
│   └── formatters/          # 输出格式化
├── tools/                   # 数据收集工具
├── verification/            # 验证逻辑
├── reports/                 # 报告生成
├── privacy/                 # 隐私存储
├── config/                  # 配置文件
└── tests/                   # 测试
```

## 🧪 测试

```bash
# 运行所有测试
pytest

# 运行单元测试
pytest tests/unit/

# 运行集成测试
pytest tests/integration/

# 生成测试覆盖率报告
pytest --cov=nft_promise_verification --cov-report=html
```

## 📝 开发规范

### 代码风格

- 遵循 PEP 8 规范
- 使用类型提示 (Type Hints)
- 函数长度 < 50 行
- 文件长度 < 800 行
- 所有函数必须包含 docstring

### Git 提交规范

使用 Conventional Commits 格式:

```
类型(范围): 简短描述

详细描述（可选）

关联 Issue（可选）
```

**类型**:
- `feat`: 新功能
- `fix`: 修复 Bug
- `docs`: 文档更新
- `style`: 代码格式调整
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建/工具链相关

## 🔒 安全注意事项

1. **永远不要提交 .env 文件**
2. **使用环境变量管理所有敏感信息**
3. **私钥管理**: 使用环境变量或密钥管理服务
4. **SQL 注入防护**: 所有数据库操作使用参数化查询
5. **输入验证**: 所有用户输入使用 Pydantic 模型验证

## 📄 许可证

MIT License

## 🤝 贡献指南

欢迎贡献!请遵循以下步骤:

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'feat: 添加某个功能'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📧 联系方式

- 项目主页: https://github.com/your-org/hackason-project
- Issue 追踪: https://github.com/your-org/hackason-project/issues

## 🙏 致谢

- [SpoonOS](https://github.com/spoonos) - AI Agent 框架
- [BSN-DDC](https://www.bsnbase.com/) - 区块链服务网络
- [Anthropic](https://www.anthropic.com/) - Claude LLM
- [OpenAI](https://openai.com/) - GPT-4 LLM

---

**版本**: 1.0.0
**最后更新**: 2026-01-30
**状态**: 🚧 开发中 (Phase 1 完成)
