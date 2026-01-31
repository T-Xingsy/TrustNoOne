# 画饼粉碎机 - 前后端 API 对接文档

## 概述

本文档描述前端与后端 API 的数据交互规范。

---

## 基础配置

### API 基础路径
```
/api/v1
```

### 通用响应格式
```json
{
    "success": true,
    "data": {},
    "message": "操作成功",
    "timestamp": 1706600000
}
```

### 错误响应格式
```json
{
    "success": false,
    "error": "ERROR_CODE",
    "message": "错误描述",
    "timestamp": 1706600000
}
```

---

## API 端点

### 1. 项目搜索

**端点**: `GET /api/v1/projects/search`

**参数**:
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| q | string | 是 | 搜索关键词（项目名/Twitter/合约地址） |
| limit | number | 否 | 返回数量，默认5 |

**响应数据**:
```json
{
    "success": true,
    "data": {
        "projects": [
            {
                "id": "azuki",
                "name": "Azuki",
                "twitter": "@AzukiEN",
                "website": "azuki.com",
                "contract": "0xed5af38865e05c81cb826c3742787055585c19f2",
                "score": 78,
                "riskLevel": "high",
                "lastVerified": "2025-01-30T00:00:00Z"
            }
        ]
    }
}
```

---

### 2. 项目详情

**端点**: `GET /api/v1/projects/{projectId}`

**路径参数**:
| 参数名 | 类型 | 说明 |
|--------|------|------|
| projectId | string | 项目ID |

**响应数据**:
```json
{
    "success": true,
    "data": {
        "project": {
            "id": "azuki",
            "name": "Azuki",
            "twitter": "@AzukiEN",
            "website": "azuki.com",
            "contract": "0xed5af38865e05c81cb826c3742787055585c19f2",
            "score": 78,
            "riskLevel": "high",
            "riskLabel": "严重画饼",
            "lastVerified": "2025-01-30T00:00:00Z",
            "dimensions": {
                "integrity": {
                    "score": 32,
                    "weight": 30,
                    "label": "诚信",
                    "level": "low",
                    "explanation": "10条承诺中仅3条兑现，诚信得分偏低"
                },
                "fairness": {
                    "score": 55,
                    "weight": 20,
                    "label": "公平性",
                    "level": "medium",
                    "explanation": "NFT分布中度集中，Top 10持有约35%"
                },
                "development": {
                    "score": 41,
                    "weight": 20,
                    "label": "开发力",
                    "level": "low",
                    "explanation": "GitHub活跃度下降，近6个月平均月提交8次"
                },
                "finance": {
                    "score": 72,
                    "weight": 15,
                    "label": "财务",
                    "level": "high",
                    "explanation": "国库资金相对稳定，当前余额127 ETH"
                },
                "momentum": {
                    "score": 58,
                    "weight": 15,
                    "label": "动能",
                    "level": "medium",
                    "explanation": "Twitter活跃度一般，周均推文约12条"
                }
            },
            "promises": [
                {
                    "id": "p1",
                    "text": "将在 2024 Q1 空投 10000 个虚拟 BEANZ 给社区持有者",
                    "source": "twitter",
                    "sourceUrl": "https://twitter.com/AzukiEN/status/123456",
                    "promisedDate": "2024-01-15T00:00:00Z",
                    "dueDate": "2024-03-31T00:00:00Z",
                    "status": "unfulfilled",
                    "statusLabel": "未兑现",
                    "type": "airdrop",
                    "typeLabel": "空投",
                    "evidence": {
                        "summary": "查询 ERC-20 转账事件，未发现针对 Azuki 持有者的 BEANZ 空投记录",
                        "txHash": null,
                        "contractAddress": "0x7E1F...3A2F",
                        "balance": "127 ETH"
                    }
                }
            ],
            "timeline": [
                {
                    "date": "2025-01-30T00:00:00Z",
                    "score": 78,
                    "integrityScore": 32,
                    "status": "verified",
                    "summary": "完成验证，画饼指数 78（高风险）"
                }
            ]
        }
    }
}
```

---

### 3. 创建验证任务

**端点**: `POST /api/v1/verifications`

**请求体**:
```json
{
    "projectName": "New Project",
    "twitter": "@project_handle",
    "website": "example.com",
    "contract": "0x..."
}
```

**响应数据**:
```json
{
    "success": true,
    "data": {
        "verificationId": "ver_123456",
        "status": "pending",
        "estimatedTime": 300
    }
}
```

---

### 4. 获取验证进度

**端点**: `GET /api/v1/verifications/{verificationId}`

**路径参数**:
| 参数名 | 类型 | 说明 |
|--------|------|------|
| verificationId | string | 验证任务ID |

**响应数据**:
```json
{
    "success": true,
    "data": {
        "verificationId": "ver_123456",
        "status": "processing",
        "progress": 65,
        "currentStep": "链上验证中...",
        "steps": [
            {"step": 1, "name": "收集承诺", "status": "completed"},
            {"step": 2, "name": "链上验证", "status": "active"},
            {"step": 3, "name": "五维评分", "status": "pending"},
            {"step": 4, "name": "生成报告", "status": "pending"}
        ],
        "thinking": [
            "已找到 3 条空投相关承诺",
            "国库地址: 0x7E1F...3A2F，当前余额: 127 ETH"
        ]
    }
}
```

**状态值**:
- `pending` - 等待中
- `processing` - 处理中
- `completed` - 已完成
- `failed` - 失败

---

### 5. 获取最近验证项目

**端点**: `GET /api/v1/projects/recent`

**参数**:
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| limit | number | 否 | 返回数量，默认10 |

**响应数据**:
```json
{
    "success": true,
    "data": {
        "projects": [
            {
                "id": "azuki",
                "name": "Azuki",
                "twitter": "@AzukiEN",
                "contract": "0xed5af38865...",
                "score": 78,
                "riskLevel": "high",
                "integrityScore": 32,
                "promisesTotal": 15,
                "promisesFulfilled": 3,
                "promisesUnfulfilled": 10
            }
        ]
    }
}
```

---

### 6. 获取统计数据

**端点**: `GET /api/v1/stats`

**响应数据**:
```json
{
    "success": true,
    "data": {
        "totalProjects": 247,
        "averageScore": 67,
        "highRiskCount": 89,
        "mediumRiskCount": 102,
        "lowRiskCount": 56
    }
}
```

---

## 前端数据结构说明

### 雷达图数据格式

五维雷达图需要以下数据结构：

```javascript
{
    dimensions: [
        { label: "诚信", score: 32, weight: 30, level: "low" },
        { label: "公平性", score: 55, weight: 20, level: "medium" },
        { label: "开发力", score: 41, weight: 20, level: "low" },
        { label: "财务", score: 72, weight: 15, level: "high" },
        { label: "动能", score: 58, weight: 15, level: "medium" }
    ]
}
```

**雷达图坐标计算**（前端自动处理）：

五边形顶点（以中心为原点，半径120）：
- 顶点1（诚信，上）: (150, 30)
- 顶点2（公平性，右上）: (264, 113)
- 顶点3（财务，右下）: (220, 247)
- 顶点4（动能，左下）: (80, 247)
- 顶点5（开发力，左上）: (36, 113)

数据点坐标计算公式：
```
x = center_x + (score / 100) * radius * cos(angle)
y = center_y + (score / 100) * radius * sin(angle)
```

---

## 风险等级映射

| score | riskLevel | riskLabel | 颜色 |
|-------|-----------|-----------|------|
| 0-49 | high | 高风险/严重画饼 | #ff2d2d |
| 50-69 | medium | 中风险/中度画饼 | #ffaa00 |
| 70-100 | low | 低风险/可信 | #00ff88 |

---

## 承诺状态映射

| status | statusLabel | 图标 | 颜色 |
|--------|-------------|------|------|
| fulfilled | 已兑现 | ✅ | #00ff88 |
| unfulfilled | 未兑现 | ❌ | #ff2d2d |
| unverifiable | 无法验证 | ❓ | #555555 |

---

## 前端页面路由

| 页面 | 路径 | 说明 |
|------|------|------|
| 首页 | index.html | 项目搜索、最近验证列表 |
| 项目详情 | project-detail.html | 五维雷达图、承诺清单 |
| 验证进度 | verification-progress.html | 实时验证进度展示 |

---

## SessionStorage 数据传递

前端使用 `sessionStorage` 在页面间传递数据：

| 键名 | 类型 | 说明 |
|------|------|------|
| viewProject | string | 要查看详情的项目名 |
| verifyProject | string | 要验证的项目名 |
| newProjectData | object(JSON) | 新项目验证数据 |

---

## 前端文件列表

```
frontend/
├── index.html                    # 首页（搜索+项目列表）
├── project-detail.html           # 项目详情页（雷达图+承诺）
├── verification-progress.html    # 验证进度页
├── FRONTEND_DESIGN.md            # 设计规范文档
└── API_DOCS.md                   # 本文档
```

---

## WebSocket 推送（可选）

验证进度支持 WebSocket 实时推送：

**连接**: `wss://api.example.com/ws/verifications/{verificationId}`

**推送消息格式**:
```json
{
    "type": "progress",
    "data": {
        "progress": 65,
        "step": 2,
        "message": "链上验证中...",
        "thinking": "国库地址: 0x7E1F...3A2F"
    }
}
```

---

## 注意事项

1. **时间格式**: 所有时间使用 ISO 8601 格式 (YYYY-MM-DDTHH:mm:ssZ)
2. **合约地址**: 返回完整地址，前端负责截断显示
3. **分页**: 列表类 API 支持 `page` 和 `pageSize` 参数
4. **缓存**: 项目详情数据前端缓存 5 分钟
5. **限流**: API 请求频率限制为 100 次/分钟/IP
