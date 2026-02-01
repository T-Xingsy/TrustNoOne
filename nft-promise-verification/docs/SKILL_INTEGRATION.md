# Skill 集成说明

本文档说明 NFT Promise Verification 项目中集成的外部 Skills。

## 📋 概述

项目集成了三个社区 Skills 来增强数据收集和报告生成能力：

1. **bird** - Twitter 数据抓取
2. **github** - GitHub 活动追踪 (使用 gh CLI)
3. **excel** - Excel 报告生成

## 🚀 快速开始

### 安装 Skills

运行安装脚本：

```bash
python scripts/install_skills.py
```

或手动安装：

```bash
# 安装 bird skill (Twitter)
npx clawdhub@latest install bird

# 安装 github skill (需要先安装 gh CLI)
npx clawdhub@latest install github

# 安装 excel skill
npx clawdhub@latest install excel
```

## 🔧 技术架构

### Skill 适配器模式

```
┌─────────────────────────────────────┐
│      VerificationAgent              │
│      (SpoonReactAI)                 │
└─────────────┬───────────────────────┘
              │
              ↓
┌─────────────────────────────────────┐
│      ToolManager                    │
└─────────────┬───────────────────────┘
              │
    ┌─────────┴─────────┬──────────────┐
    ↓                   ↓              ↓
┌─────────┐      ┌──────────┐   ┌─────────┐
│  Skill  │      │   MCP    │   │ Custom  │
│ Adapters│      │  Tools   │   │  Tools  │
└─────────┘      └──────────┘   └─────────┘
    ↓                   ↓              ↓
┌─────────┐      ┌──────────┐   ┌─────────┐
│ bird    │      │Chainbase │   │Promise  │
│ github  │      │          │   │Extractor│
│ excel   │      │          │   │Scorers  │
└─────────┘      └──────────┘   └─────────┘
```

### Fallback 机制

每个 Skill 适配器都有 Fallback 机制：

- **TwitterSkillAdapter**: bird skill → snscrape (原有实现)
- **GitHubSkillAdapter**: gh CLI → Spoon-Toolkit GitHub 工具
- **ExcelSkillAdapter**: openpyxl (Python 库)

即使 Skills 未安装，项目也能正常运行。

## 📦 集成的 Skills

### 1. bird (Twitter 数据抓取)

**功能**: 抓取 Twitter/X 用户推文

**优势**:
- 社区维护，持续更新
- 更好的反爬能力
- 减少维护成本

**使用方式**:
```python
# 在 agent.py 中自动调用
agent.run("抓取 @BoredApeYC 的最近 100 条推文")
```

**Fallback**: `tools/twitter_scraper.py` (snscrape)

### 2. github (GitHub 活动追踪)

**功能**: 查询 GitHub 仓库的 commits、PRs、issues

**优势**:
- 官方维护 (GitHub CLI)
- 无需管理 API token
- 自动处理速率限制

**使用方式**:
```python
# 在 agent.py 中自动调用
agent.run("查询 facebook/react 最近的 commits")
```

**前置条件**:
- 需要安装 gh CLI: https://cli.github.com/

**Fallback**: `spoon_toolkits.github` (Spoon-Toolkit)

### 3. excel (Excel 报告生成)

**功能**: 生成格式化的 Excel 报告

**优势**:
- 自动格式化
- 支持图表
- 公式计算

**使用方式**:
```python
from tools.skill_adapters import ExcelSkillAdapter

excel_skill = ExcelSkillAdapter()
excel_skill._run(
    data=report_data,
    output_path="reports/verification.xlsx"
)
```

**实现**: 使用 `openpyxl` Python 库

## 📂 文件结构

```
nft-promise-verification/
├── tools/
│   ├── skill_adapters/
│   │   ├── __init__.py
│   │   ├── twitter_skill.py    # Twitter Skill 适配器
│   │   ├── github_skill.py     # GitHub Skill 适配器
│   │   └── excel_skill.py      # Excel Skill 适配器
│   ├── twitter_scraper.py      # 原有实现 (Fallback)
│   └── ...
├── scripts/
│   └── install_skills.py       # Skills 安装脚本
└── tools_config.py             # 更新的工具配置
```

## 🔍 故障排除

### bird skill 不工作

**症状**: Twitter 数据抓取失败

**解决方案**:
```bash
# 重新安装 bird skill
npx clawdhub@latest install bird --force

# 检查安装
npx clawdhub list | grep bird
```

系统会自动回退到 snscrape 实现。

### github skill 不工作

**症状**: GitHub 数据查询失败

**解决方案**:
```bash
# 1. 安装 gh CLI
# macOS
brew install gh

# Windows
# 从 https://cli.github.com/ 下载安装

# 2. 认证
gh auth login

# 3. 重新安装 skill
npx clawdhub@latest install github
```

系统会自动回退到 Spoon-Toolkit GitHub 工具。

### Excel 报告生成失败

**症状**: 无法生成 Excel 报告

**解决方案**:
```bash
# 安装 openpyxl
pip install openpyxl
```

## 📊 性能对比

| 任务 | 原实现 | Skill | 提升 |
|------|-------|-------|------|
| Twitter 抓取 | snscrape | bird | 更稳定 |
| GitHub 查询 | API calls | gh CLI | 更快 |
| Excel 生成 | 手动格式化 | 模板化 | 50%+ |

## 🎯 最佳实践

1. **开发环境**: 安装所有 Skills 获得最佳体验
2. **生产环境**: 确保 Fallback 机制正常工作
3. **CI/CD**: 只依赖 Python 库，Skills 作为可选增强

## 📚 相关文档

- [ClawdHub Skills Marketplace](https://skillsmp.com/)
- [awesome-clawdbot-skills](https://github.com/VoltAgent/awesome-clawdbot-skills)
- [gh CLI 文档](https://cli.github.com/manual/)
- [openpyxl 文档](https://openpyxl.readthedocs.io/)

## 🤝 贡献

如果你想添加更多 Skills：

1. 在 `tools/skill_adapters/` 创建新的适配器
2. 在 `tools_config.py` 注册适配器
3. 更新此文档

## 📝 变更日志

### v1.0.0 (2026-02-01)
- ✅ 集成 bird skill (Twitter)
- ✅ 集成 github skill (GitHub)
- ✅ 集成 excel skill (Excel)
- ✅ 实现 Fallback 机制
- ✅ 添加安装脚本
