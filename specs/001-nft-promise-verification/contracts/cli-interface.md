# CLI Interface Contract: Promise Breaker MVP

**Feature**: 001-nft-promise-verification
**Date**: 2026-01-29
**Status**: Approved
**Related**: [plan.md](../plan.md) | [data-model.md](../data-model.md)

---

## 概述

本文档定义 MVP 系统的 CLI 命令接口规范，遵循 Unix 哲学（简单、可组合、单一职责）。

---

## 命令结构

```bash
promise-breaker <command> [options] [arguments]
```

---

## 命令列表

### 1. `collect` - 收集项目承诺

**用途**: 从 Twitter 和官网收集指定 NFT 项目的公开承诺

**语法**:
```bash
promise-breaker collect --name <项目名称> [options]
```

**必需参数**:
- `--name, -n <string>`: 项目名称（必填）

**可选参数**:
- `--twitter, -t <string>`: Twitter 账号（不含 @）
- `--website, -w <url>`: 官网 URL
- `--contract, -c <address>`: 智能合约地址
- `--blockchain, -b <chain>`: 区块链网络（ethereum|polygon|bsc|bsn）
- `--output, -o <path>`: 输出文件路径（默认：`./data/collections/{collection_id}.json`）
- `--format, -f <format>`: 输出格式（json|table|markdown，默认：table）
- `--verbose, -v`: 显示详细日志

**示例**:
```bash
# 基本用法
promise-breaker collect --name "Bored Ape Yacht Club" --twitter "BoredApeYC"

# 完整参数
promise-breaker collect \
  --name "Bored Ape Yacht Club" \
  --twitter "BoredApeYC" \
  --website "https://boredapeyachtclub.com" \
  --contract "0xBC4CA0EdA7647A8aB7C2061c2E118A18a936f13D" \
  --blockchain "ethereum" \
  --output "./my-report.json" \
  --format "markdown" \
  --verbose

# 简写形式
promise-breaker collect -n "BAYC" -t "BoredApeYC" -w "https://boredapeyachtclub.com" -v
```

**输出格式**:

**Table 格式** (默认):
```
╔══════════════════════════════════════════════════════════════════════════════╗
║                    Promise Collection Report                                 ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ Project: Bored Ape Yacht Club                                               ║
║ Twitter: @BoredApeYC                                                         ║
║ Website: https://boredapeyachtclub.com                                       ║
║ Collection Time: 2026-01-29 10:30:00                                         ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ Total Promises: 12                                                           ║
║ By Type:                                                                     ║
║   - 代币空投: 3                                                              ║
║   - 功能开发: 5                                                              ║
║   - 合作伙伴: 2                                                              ║
║   - 社区活动: 2                                                              ║
║ By Channel:                                                                  ║
║   - Twitter: 8                                                               ║
║   - Website: 4                                                               ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ Promise Details:                                                             ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ [1] 代币空投 | Twitter | 2024-01-15                                         ║
║     "We will airdrop 1000 tokens to all holders by Q2 2024"                  ║
║     Target: Q2 2024 | Confidence: 0.95                                       ║
║     Source: https://twitter.com/BoredApeYC/status/1234567890                 ║
╠──────────────────────────────────────────────────────────────────────────────╣
║ [2] 功能开发 | Website | 2024-02-20                                         ║
║     "Our marketplace will launch in March 2024"                              ║
║     Target: March 2024 | Confidence: 0.88                                    ║
║     Source: https://boredapeyachtclub.com/roadmap                            ║
╠──────────────────────────────────────────────────────────────────────────────╣
║ ... (10 more promises)                                                       ║
╚══════════════════════════════════════════════════════════════════════════════╝

✅ Collection completed successfully!
📁 Report saved to: ./data/collections/550e8400-e29b-41d4-a716-446655440000.json
```

**JSON 格式**:
```json
{
  "collection_id": "550e8400-e29b-41d4-a716-446655440000",
  "project": {
    "project_id": "660e8400-e29b-41d4-a716-446655440001",
    "project_name": "Bored Ape Yacht Club",
    "twitter_handle": "BoredApeYC",
    "website_url": "https://boredapeyachtclub.com",
    "created_at": "2026-01-29T10:30:00Z"
  },
  "promises": [
    {
      "promise_id": "770e8400-e29b-41d4-a716-446655440002",
      "promise_text": "We will airdrop 1000 tokens to all holders by Q2 2024",
      "promise_type": "代币空投",
      "source_channel": "twitter",
      "source_url": "https://twitter.com/BoredApeYC/status/1234567890",
      "published_at": "2024-01-15T10:30:00Z",
      "target_time": "Q2 2024",
      "confidence_score": 0.95,
      "verification_status": "待验证"
    }
  ],
  "total_count": 12,
  "by_type": {
    "代币空投": 3,
    "功能开发": 5,
    "合作伙伴": 2,
    "社区活动": 2
  },
  "by_channel": {
    "twitter": 8,
    "website": 4
  },
  "collection_time": "2026-01-29T10:30:00Z",
  "errors": []
}
```

**Markdown 格式**:
```markdown
# Promise Collection Report

**Project**: Bored Ape Yacht Club
**Twitter**: @BoredApeYC
**Website**: https://boredapeyachtclub.com
**Collection Time**: 2026-01-29 10:30:00

## Summary

- **Total Promises**: 12
- **By Type**:
  - 代币空投: 3
  - 功能开发: 5
  - 合作伙伴: 2
  - 社区活动: 2
- **By Channel**:
  - Twitter: 8
  - Website: 4

## Promise Details

### [1] 代币空投 | Twitter | 2024-01-15

**Text**: "We will airdrop 1000 tokens to all holders by Q2 2024"
**Target**: Q2 2024
**Confidence**: 0.95
**Source**: https://twitter.com/BoredApeYC/status/1234567890

---

### [2] 功能开发 | Website | 2024-02-20

**Text**: "Our marketplace will launch in March 2024"
**Target**: March 2024
**Confidence**: 0.88
**Source**: https://boredapeyachtclub.com/roadmap

---

... (10 more promises)
```

**错误处理**:

| 错误代码 | 错误信息 | 退出码 |
|---------|---------|--------|
| `MISSING_REQUIRED_PARAM` | "Error: --name is required" | 1 |
| `INVALID_URL` | "Error: Invalid website URL: {url}" | 1 |
| `INVALID_CONTRACT_ADDRESS` | "Error: Invalid contract address: {address}" | 1 |
| `TWITTER_SCRAPING_FAILED` | "Warning: Failed to scrape Twitter data: {reason}" | 0 (继续) |
| `WEBSITE_SCRAPING_FAILED` | "Warning: Failed to scrape website data: {reason}" | 0 (继续) |
| `NO_PROMISES_FOUND` | "Warning: No promises found for this project" | 0 |
| `LLM_API_ERROR` | "Error: LLM API call failed: {reason}" | 2 |

---

### 2. `list` - 列出已收集的项目

**用途**: 显示所有已收集承诺的项目列表

**语法**:
```bash
promise-breaker list [options]
```

**可选参数**:
- `--format, -f <format>`: 输出格式（table|json，默认：table）
- `--sort, -s <field>`: 排序字段（name|date|count，默认：date）
- `--limit, -l <number>`: 限制显示数量（默认：10）

**示例**:
```bash
# 基本用法
promise-breaker list

# 按承诺数量排序，显示前 5 个
promise-breaker list --sort count --limit 5

# JSON 格式输出
promise-breaker list --format json
```

**输出格式** (Table):
```
╔════════════════════════════════════════════════════════════════════════════╗
║                         Collected Projects                                 ║
╠════════════════════════════════════════════════════════════════════════════╣
║ ID   │ Project Name              │ Promises │ Last Collected             ║
╠════════════════════════════════════════════════════════════════════════════╣
║ 1    │ Bored Ape Yacht Club      │ 12       │ 2026-01-29 10:30:00       ║
║ 2    │ CryptoPunks               │ 8        │ 2026-01-28 15:20:00       ║
║ 3    │ Azuki                     │ 15       │ 2026-01-27 09:45:00       ║
╚════════════════════════════════════════════════════════════════════════════╝

Total: 3 projects
```

---

### 3. `show` - 显示项目详情

**用途**: 显示指定项目的详细信息和承诺清单

**语法**:
```bash
promise-breaker show <project_id_or_name> [options]
```

**必需参数**:
- `<project_id_or_name>`: 项目 ID 或项目名称

**可选参数**:
- `--format, -f <format>`: 输出格式（table|json|markdown，默认：table）
- `--filter-type, -t <type>`: 按承诺类型过滤
- `--filter-channel, -c <channel>`: 按来源渠道过滤
- `--min-confidence <score>`: 最低置信度阈值（0.0-1.0）

**示例**:
```bash
# 使用项目名称
promise-breaker show "Bored Ape Yacht Club"

# 使用项目 ID
promise-breaker show 550e8400-e29b-41d4-a716-446655440000

# 仅显示代币空投类型的承诺
promise-breaker show "BAYC" --filter-type "代币空投"

# 仅显示高置信度承诺（>0.8）
promise-breaker show "BAYC" --min-confidence 0.8
```

---

### 4. `export` - 导出报告

**用途**: 将承诺收集结果导出为指定格式

**语法**:
```bash
promise-breaker export <project_id_or_name> --output <path> [options]
```

**必需参数**:
- `<project_id_or_name>`: 项目 ID 或项目名称
- `--output, -o <path>`: 输出文件路径

**可选参数**:
- `--format, -f <format>`: 输出格式（json|markdown|pdf，默认：json）

**示例**:
```bash
# 导出为 JSON
promise-breaker export "BAYC" --output "./reports/bayc-report.json"

# 导出为 Markdown
promise-breaker export "BAYC" --output "./reports/bayc-report.md" --format markdown

# 导出为 PDF（未来功能）
promise-breaker export "BAYC" --output "./reports/bayc-report.pdf" --format pdf
```

---

### 5. `version` - 显示版本信息

**用途**: 显示 CLI 工具的版本信息

**语法**:
```bash
promise-breaker version
```

**输出**:
```
Promise Breaker MVP v0.1.0
SpoonOS Framework: 0.3.6
Python: 3.11.7
```

---

### 6. `help` - 显示帮助信息

**用途**: 显示命令帮助信息

**语法**:
```bash
promise-breaker help [command]
```

**示例**:
```bash
# 显示所有命令
promise-breaker help

# 显示特定命令帮助
promise-breaker help collect
```

---

## 环境变量

CLI 工具支持以下环境变量配置：

| 变量名 | 描述 | 默认值 | 必需 |
|--------|------|--------|------|
| `ANTHROPIC_API_KEY` | Claude API 密钥 | - | 是 |
| `OPENAI_API_KEY` | OpenAI API 密钥（备用） | - | 否 |
| `PROMISE_BREAKER_DATA_DIR` | 数据存储目录 | `./data` | 否 |
| `PROMISE_BREAKER_LOG_LEVEL` | 日志级别 | `INFO` | 否 |
| `PROMISE_BREAKER_LLM_MODEL` | LLM 模型 | `claude-3-5-sonnet-20241022` | 否 |
| `PROMISE_BREAKER_MAX_TWEETS` | 最大推文数量 | `100` | 否 |
| `PROMISE_BREAKER_REQUEST_DELAY` | 请求延迟（秒） | `3` | 否 |

**配置文件** (`.env`):
```bash
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxx
PROMISE_BREAKER_DATA_DIR=/home/user/promise-breaker-data
PROMISE_BREAKER_LOG_LEVEL=DEBUG
PROMISE_BREAKER_MAX_TWEETS=50
```

---

## 退出码

| 退出码 | 含义 |
|--------|------|
| 0 | 成功 |
| 1 | 参数错误或验证失败 |
| 2 | 运行时错误（API 调用失败、网络错误等） |
| 3 | 配置错误（缺少 API 密钥等） |

---

## 日志输出

**日志级别**:
- `DEBUG`: 详细调试信息（包含 Agent 推理过程）
- `INFO`: 一般信息（默认）
- `WARNING`: 警告信息（数据源不可用等）
- `ERROR`: 错误信息

**日志格式**:
```
[2026-01-29 10:30:00] INFO: Starting promise collection for project: BAYC
[2026-01-29 10:30:05] INFO: Scraping Twitter data for @BoredApeYC...
[2026-01-29 10:30:15] INFO: Found 25 tweets
[2026-01-29 10:30:20] INFO: Extracting promises using LLM...
[2026-01-29 10:30:35] INFO: Identified 8 promises from Twitter
[2026-01-29 10:30:40] INFO: Scraping website: https://boredapeyachtclub.com
[2026-01-29 10:30:50] INFO: Identified 4 promises from website
[2026-01-29 10:30:55] INFO: Collection completed. Total promises: 12
[2026-01-29 10:30:55] INFO: Report saved to: ./data/collections/550e8400.json
```

---

## 性能指标

**预期性能**:
- 单个项目收集时间: 2-5 分钟
- Twitter 数据抓取: 30-60 秒
- 网页数据抓取: 10-30 秒
- LLM 承诺提取: 1-2 分钟
- 数据存储: <1 秒

---

## 合规性检查

### Constitution 原则遵循

- ✅ **Input Validation**: 所有参数使用 Pydantic 验证
- ✅ **Error Handling**: 清晰的错误信息和退出码
- ✅ **User-Friendly**: 提供多种输出格式和详细帮助
- ✅ **Security**: API 密钥通过环境变量管理

---

**Document Version**: 1.0.0
**Last Updated**: 2026-01-29
**Status**: ✅ Approved for Implementation
