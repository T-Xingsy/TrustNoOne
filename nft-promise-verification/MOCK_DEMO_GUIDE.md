# NFT 承诺验证 Mock 数据演示指南

## 📋 概述

本指南介绍如何使用 Mock 数据模拟 NFT 承诺验证应用的完整流程，包括数据导入、命令行演示和 API 接口使用。

## 🎯 Mock 数据说明

系统预设了 3 个典型的 NFT 项目，覆盖不同风险等级：

### 1. **Azuki**（可信项目）
- **画饼指数**: 20
- **综合评分**: 80
- **风险等级**: 可信/几乎不画饼
- **特点**: 承诺兑现率高（80%+），活跃的开发和社区

### 2. **Moonbirds**（一般项目）
- **画饼指数**: 50
- **综合评分**: 50
- **风险等级**: 一般/中度画饼
- **特点**: 承诺兑现率中等（50-60%），部分承诺延期

### 3. **PixelmonNFT**（画饼项目）
- **画饼指数**: 80
- **综合评分**: 20
- **风险等级**: 较差/严重画饼
- **特点**: 承诺兑现率低（20-30%），多个重要承诺未兑现

## 🚀 快速开始

### 步骤 1: 激活 Conda 环境

```bash
conda activate hackason
```

### 步骤 2: 导入 Mock 数据

```bash
cd /home/ssszyy/code/web3/hackason-project/nft-promise-verification

# 清空数据库并导入 Mock 数据
python mock_data_loader.py --clear
```

**预期输出**:
```
============================================================
Mock 数据导入结果
============================================================
✅ 成功导入: 3 个项目
⏭️  跳过: 0 个项目

导入的项目:
  - Azuki (ID: xxx-xxx-xxx)
  - Moonbirds (ID: xxx-xxx-xxx)
  - PixelmonNFT (ID: xxx-xxx-xxx)
============================================================
```

### 步骤 3: 运行演示脚本

#### 方式 1: 交互式模式

```bash
python demo.py
```

**交互流程**:
1. 选择项目（输入编号 1-3）
2. 选择输出格式（text/json/markdown）
3. 查看生成的验证报告
4. 可选：导出报告到文件

#### 方式 2: 命令行模式

```bash
# 生成 Azuki 的文本报告
python demo.py --project "Azuki" --format text

# 生成 Moonbirds 的 JSON 报告
python demo.py --project "Moonbirds" --format json

# 生成 PixelmonNFT 的 Markdown 报告并导出
python demo.py --project "PixelmonNFT" --format markdown --output pixelmon_report.md
```

## 🌐 API 接口使用

### 启动 API 服务器

```bash
cd /home/ssszyy/code/web3/hackason-project/nft-promise-verification

# 方式 1: 使用 uvicorn 直接运行
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# 方式 2: 使用 Python 运行
python api/main.py
```

**服务器启动后**:
- API 文档: http://localhost:8000/docs
- 交互式 API 测试: http://localhost:8000/redoc

### API 端点说明

#### 1. 获取项目列表

```bash
curl http://localhost:8000/api/v1/projects?limit=10&offset=0
```

**响应示例**:
```json
{
  "success": true,
  "total": 3,
  "limit": 10,
  "offset": 0,
  "projects": [
    {
      "id": "xxx-xxx-xxx",
      "name": "Azuki",
      "twitter_account": "AzukiOfficial",
      "promise_breaking_index": 20,
      "comprehensive_score": 80,
      "risk_level": {
        "level": "low",
        "label": "可信/几乎不画饼",
        "color": "#00ff88"
      }
    }
  ]
}
```

#### 2. 搜索项目

```bash
curl "http://localhost:8000/api/v1/projects/search?q=Azuki&limit=5"
```

#### 3. 获取项目详情

```bash
curl http://localhost:8000/api/v1/projects/{project_id}
```

**响应包含**:
- 项目基本信息
- 五维评分（诚信、公平性、开发力、财务、动能）
- 承诺清单
- 验证历史
- 风险评估和建议

#### 4. 获取项目报告

```bash
# JSON 格式
curl http://localhost:8000/api/v1/projects/{project_id}/report?format=json

# 文本格式
curl http://localhost:8000/api/v1/projects/{project_id}/report?format=text

# Markdown 格式
curl http://localhost:8000/api/v1/projects/{project_id}/report?format=markdown
```

#### 5. 获取统计数据

```bash
curl http://localhost:8000/api/v1/stats
```

**响应示例**:
```json
{
  "success": true,
  "total_projects": 3,
  "verified_projects": 3,
  "average_promise_breaking_index": 50.0,
  "average_comprehensive_score": 50.0,
  "risk_distribution": {
    "low": 1,
    "low-medium": 0,
    "medium": 1,
    "high": 0,
    "critical": 1
  }
}
```

## 📊 前端对接

### 修改前端代码

将前端的 `projects-data.js` 替换为 API 调用：

```javascript
// 原来的 Mock 数据
// const projects = [...];

// 改为从 API 获取
async function fetchProjects() {
    const response = await fetch('http://localhost:8000/api/v1/projects');
    const data = await response.json();
    return data.projects;
}

async function fetchProjectDetail(projectId) {
    const response = await fetch(`http://localhost:8000/api/v1/projects/${projectId}`);
    const data = await response.json();
    return data;
}
```

### 前端页面更新

1. **首页（index.html）**:
   - 调用 `/api/v1/projects` 获取项目列表
   - 显示项目卡片（名称、画饼指数、风险等级）

2. **项目详情页（project-detail.html）**:
   - 调用 `/api/v1/projects/{id}` 获取详细信息
   - 渲染五维雷达图
   - 显示承诺清单和验证结果

3. **搜索功能**:
   - 调用 `/api/v1/projects/search?q={keyword}` 实现实时搜索

## 🔧 高级用法

### 添加自定义 Mock 项目

编辑 `mock_projects.json` 文件，添加新的项目数据：

```json
{
  "projects": [
    {
      "name": "YourProject",
      "twitter_account": "YourTwitter",
      "website_url": "https://yourproject.com",
      "contract_address": "0x...",
      "promises": [
        {
          "content": "承诺内容",
          "promise_type": "NFT_MINTING",
          "target_date": "2024-12-31",
          "confidence": 0.9,
          "verification_status": "FULFILLED",
          ...
        }
      ],
      "expected_scores": {
        "promise_breaking_index": 30,
        "integrity_score": 70,
        ...
      }
    }
  ]
}
```

然后重新导入数据：

```bash
python mock_data_loader.py --clear
```

### 清空数据库

```bash
# 删除数据库文件
rm data/promises.db

# 重新导入
python mock_data_loader.py --clear
```

### 追加导入（不清空现有数据）

```bash
python mock_data_loader.py
```

## 📝 数据结构说明

### 承诺类型（promise_type）

- `AIRDROP`: 空投
- `FEATURE_DEVELOPMENT`: 功能开发
- `PARTNERSHIP`: 合作关系
- `COMMUNITY_EVENT`: 社区活动
- `NFT_MINTING`: NFT 铸造
- `MARKETPLACE_LAUNCH`: 市场启动
- `OTHER`: 其他

### 验证状态（verification_status）

- `PENDING`: 待验证
- `FULFILLED`: 已兑现
- `UNFULFILLED`: 未兑现
- `UNVERIFIABLE`: 无法验证

### 风险等级

| 画饼指数 | 风险等级 | 标签 | 颜色 |
|---------|---------|------|------|
| 0-20 | low | 可信/几乎不画饼 | #00ff88 |
| 21-40 | low-medium | 较可靠/轻度画饼 | #88ff00 |
| 41-60 | medium | 一般/中度画饼 | #ffaa00 |
| 61-80 | high | 较差/严重画饼 | #ff6600 |
| 81-100 | critical | 极差/极度画饼 | #ff2d2d |

## 🐛 故障排除

### 问题 1: 数据库不存在

**错误信息**: `数据库不存在，请先运行: python mock_data_loader.py --clear`

**解决方案**:
```bash
python mock_data_loader.py --clear
```

### 问题 2: Conda 环境未激活

**错误信息**: `ModuleNotFoundError: No module named 'xxx'`

**解决方案**:
```bash
conda activate hackason
pip install -r requirements.txt
```

### 问题 3: API 服务器无法启动

**错误信息**: `Address already in use`

**解决方案**:
```bash
# 查找占用 8000 端口的进程
lsof -i :8000

# 杀死进程
kill -9 <PID>

# 或使用其他端口
uvicorn api.main:app --port 8001
```

### 问题 4: CORS 错误

**错误信息**: `Access to fetch at 'http://localhost:8000' from origin 'xxx' has been blocked by CORS policy`

**解决方案**: API 已配置允许所有来源，如果仍有问题，检查浏览器控制台的具体错误信息。

## 📚 相关文档

- [项目需求文档](../docs/REQUIREMENTS_V1.md)
- [API 文档](http://localhost:8000/docs)（需先启动 API 服务器）
- [前端设计文档](../frontend/FRONTEND_DESIGN.md)

## 💡 使用建议

1. **演示流程**:
   - 先导入 Mock 数据
   - 使用 demo.py 查看文本报告
   - 启动 API 服务器
   - 在浏览器中访问 API 文档测试接口
   - 前端对接 API

2. **开发流程**:
   - 使用 Mock 数据进行前端开发
   - 完成前端功能后，替换为真实的数据收集和验证逻辑
   - 保留 Mock 数据用于测试和演示

3. **测试场景**:
   - Azuki: 测试高分项目的展示
   - Moonbirds: 测试中等风险项目的警告提示
   - PixelmonNFT: 测试高风险项目的风险提示和建议

## 🎉 总结

通过本指南，你可以：
- ✅ 快速导入 Mock 数据
- ✅ 使用命令行工具生成报告
- ✅ 启动 API 服务器提供接口
- ✅ 前端对接 API 实现完整演示

Mock 数据系统提供了完整的端到端演示能力，无需真实的区块链数据和 LLM 调用，非常适合开发、测试和演示使用。

---

**最后更新**: 2026-01-31
**维护者**: Promise Breaker Team
