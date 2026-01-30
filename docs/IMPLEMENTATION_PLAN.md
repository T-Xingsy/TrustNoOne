# 实施计划 - onchain-verifier Skills 重构

## 项目概述

**目标**：重构 onchain-verifier 插件，使用 DDC-Market-SDK 替代 ethers.js，实现 4 个专注于验证的 skills。

**时间线**：分 3 个阶段实施

---

## Phase 1: 核心验证功能（高优先级）

### 1.1 实现 ddc-metadata-query skill

**目标**：实现元数据查询和验证功能（用户特别提到）

**任务清单**：
- [ ] 创建 skill 目录结构
  - `onchain-verifier/skills/ddc-metadata-query/`
  - `SKILL.md` - skill 文档
  - `index.ts` - skill 入口
  - `metadata-query.ts` - 核心逻辑
  - `types.ts` - 类型定义

- [ ] 实现核心功能
  - SDK 初始化和配置
  - `getTokenURI()` 调用
  - 元数据下载和解析（HTTP 请求）
  - 承诺对比逻辑
  - LLM 上下文格式化

- [ ] 编写测试
  - 单元测试：元数据解析
  - 集成测试：SDK 调用
  - Mock 测试：HTTP 请求

- [ ] 编写文档
  - API 文档
  - 使用示例
  - 故障排除指南

**预期输出**：
```typescript
// 使用示例
const result = await metadataQuery({
  contractAddress: '0x...',
  tokenIds: [BigInt(1), BigInt(2), BigInt(3)],
  promise: {
    expectedName: 'Cool NFT',
    expectedDescription: 'A cool NFT collection',
  }
});

console.log(result.summary.matchingPromise); // 2 out of 3
console.log(result.llmContext); // 格式化的 LLM 上下文
```

**依赖**：
- DDC-Market-SDK
- axios (用于 HTTP 请求)
- 环境变量配置

**预计工作量**：2-3 天

---

### 1.2 实现 ddc-supply-verification skill

**目标**：实现供应量验证功能

**任务清单**：
- [ ] 创建 skill 目录结构
  - `onchain-verifier/skills/ddc-supply-verification/`
  - 相关文件（同上）

- [ ] 实现核心功能
  - SDK 初始化
  - `getTotalSupply()` 调用
  - 履约率计算
  - 证据强度评估
  - LLM 上下文格式化

- [ ] 编写测试
  - 单元测试：履约率计算
  - 集成测试：SDK 调用

- [ ] 编写文档

**预期输出**：
```typescript
const result = await supplyVerification({
  contractAddress: '0x...',
  promise: {
    expectedSupply: 10000,
    deadline: '2024-06-30',
    description: 'Mint 10,000 NFTs by Q2 2024',
  }
});

console.log(result.verification.fulfilled); // true/false
console.log(result.verification.fulfillmentRate); // 85%
console.log(result.verification.evidenceStrength); // 'strong'
```

**依赖**：
- DDC-Market-SDK
- 环境变量配置

**预计工作量**：1-2 天

---

## Phase 2: 高级分析功能（中优先级）

### 2.1 实现 ddc-holder-analysis skill

**目标**：实现持有者分析功能

**任务清单**：
- [ ] 创建 skill 目录结构
- [ ] 实现核心功能
  - `getOwnerOf()` 批量调用
  - `getTotalSupply()` 调用
  - 持有者分布统计
  - 大户识别
  - LLM 上下文格式化

- [ ] 性能优化
  - 并行查询优化
  - 分页处理大量 token
  - 缓存机制

- [ ] 编写测试和文档

**预期输出**：
```typescript
const result = await holderAnalysis({
  contractAddress: '0x...',
  tokenIdRange: { start: BigInt(1), end: BigInt(1000) },
  promise: {
    expectedHolders: 500,
    expectedSupply: 1000,
  }
});

console.log(result.holders.unique); // 487
console.log(result.holders.topHolders); // 前 10 大户
console.log(result.matchesPromise.holdersMatch); // true/false
```

**挑战**：
- 性能：遍历大量 token 可能很慢
- 解决方案：
  - 使用 Promise.all 并行查询
  - 实现分页和进度报告
  - 添加缓存层

**预计工作量**：3-4 天

---

## Phase 3: 会员系统支持（低优先级）

### 3.1 实现 ddc-membership-snapshot skill

**目标**：实现会员快照分析功能

**任务清单**：
- [ ] 创建 skill 目录结构
- [ ] 实现核心功能
  - `getMemberSnapshot()` 调用
  - `getLatestSnapshotId()` 调用
  - 快照对比分析
  - 会员变化追踪
  - LLM 上下文格式化

- [ ] 编写测试和文档

**预期输出**：
```typescript
const result = await membershipSnapshot({
  contractAddress: '0x...',
  snapshotIds: [BigInt(1), BigInt(2)],
  promise: {
    expectedMembers: 1000,
    snapshotDate: '2024-06-30',
    description: 'Airdrop to all members',
  }
});

console.log(result.analysis.totalMembers); // 987
console.log(result.matchesPromise.memberCountMatch); // true/false
```

**注意**：
- 仅在项目使用 Membership 合约时需要
- 可以根据实际需求决定是否实施

**预计工作量**：2-3 天

---

## 技术实施细节

### 目录结构

```
onchain-verifier/
├── .claude-plugin/
│   └── plugin.json
├── skills/
│   ├── ddc-metadata-query/
│   │   ├── SKILL.md
│   │   ├── index.ts
│   │   ├── metadata-query.ts
│   │   ├── types.ts
│   │   └── __tests__/
│   ├── ddc-supply-verification/
│   │   ├── SKILL.md
│   │   ├── index.ts
│   │   ├── supply-verification.ts
│   │   ├── types.ts
│   │   └── __tests__/
│   ├── ddc-holder-analysis/
│   │   ├── SKILL.md
│   │   ├── index.ts
│   │   ├── holder-analysis.ts
│   │   ├── types.ts
│   │   └── __tests__/
│   └── ddc-membership-snapshot/
│       ├── SKILL.md
│       ├── index.ts
│       ├── membership-snapshot.ts
│       ├── types.ts
│       └── __tests__/
├── scripts/
│   ├── sdk-client.ts          # SDK 客户端封装
│   ├── llm-formatter.ts        # LLM 上下文格式化
│   └── utils.ts                # 工具函数
├── package.json
├── tsconfig.json
└── README.md
```

### 共享模块

#### sdk-client.ts
```typescript
import { DDCNFTManager, MembershipManager } from '@ddc-market/sdk';

export class SDKClient {
  private ddcManager?: DDCNFTManager;
  private membershipManager?: MembershipManager;

  async initDDCNFT(config: SDKConfig): Promise<DDCNFTManager> {
    // 初始化 DDCNFT Manager
  }

  async initMembership(config: SDKConfig): Promise<MembershipManager> {
    // 初始化 Membership Manager
  }

  // 其他共享方法
}
```

#### llm-formatter.ts
```typescript
export class LLMFormatter {
  static formatMetadataResult(result: MetadataQueryResult): string {
    // 格式化元数据查询结果为 LLM 上下文
  }

  static formatSupplyResult(result: SupplyVerificationResult): string {
    // 格式化供应量验证结果
  }

  // 其他格式化方法
}
```

---

## 环境配置

### 必需的环境变量

```bash
# .env 文件
# DDC-Market-SDK 配置
WALLET_ADDRESS=0x...
PRIVATE_KEY=your_private_key
RPC_URL=https://...          # 可选，SDK 会自动获取
CHAIN_ID=1                   # 可选，SDK 会自动获取

# 调试模式
DEBUG=true

# 可选：缓存配置
CACHE_ENABLED=true
CACHE_TTL=3600               # 缓存时间（秒）
```

### package.json 依赖

```json
{
  "dependencies": {
    "@ddc-market/sdk": "^1.0.0",
    "ethers": "^6.0.0",
    "axios": "^1.6.0",
    "dotenv": "^16.0.0"
  },
  "devDependencies": {
    "@types/node": "^20.0.0",
    "typescript": "^5.0.0",
    "jest": "^29.0.0",
    "@types/jest": "^29.0.0",
    "ts-jest": "^29.0.0"
  }
}
```

---

## 测试策略

### 单元测试
- 测试每个 skill 的核心逻辑
- Mock SDK 调用
- 测试边界条件和错误处理

### 集成测试
- 使用测试网络
- 测试实际的 SDK 调用
- 验证输出格式

### 端到端测试
- 测试与 SpoonOS Agent 的集成
- 测试完整的验证流程

---

## 风险和缓解措施

### 风险 1: SDK API 变更
**缓解**：
- 锁定 SDK 版本
- 编写适配层，隔离 SDK 依赖
- 定期检查 SDK 更新

### 风险 2: RPC 性能问题
**缓解**：
- 实现重试机制
- 使用备用 RPC
- 实现缓存层
- 分页处理大量数据

### 风险 3: 元数据不可访问
**缓解**：
- 实现超时机制
- 记录失败的 token ID
- 提供部分结果

---

## 迁移策略

### 从 onchain-data-query 迁移

1. **保留现有 skill**（短期）
   - 不删除 onchain-data-query
   - 标记为 deprecated
   - 提供迁移指南

2. **逐步迁移**（中期）
   - 先实现新 skills
   - 测试验证
   - 更新文档

3. **完全替换**（长期）
   - 删除 onchain-data-query
   - 更新所有引用
   - 清理依赖

---

## 成功指标

### Phase 1 完成标准
- [ ] ddc-metadata-query skill 可用
- [ ] ddc-supply-verification skill 可用
- [ ] 单元测试覆盖率 > 80%
- [ ] 文档完整
- [ ] 与 SpoonOS Agent 集成测试通过

### Phase 2 完成标准
- [ ] ddc-holder-analysis skill 可用
- [ ] 性能测试通过（1000 tokens < 30s）
- [ ] 文档完整

### Phase 3 完成标准
- [ ] ddc-membership-snapshot skill 可用
- [ ] 所有 skills 集成测试通过
- [ ] 完整的使用文档和示例

---

## 下一步行动

### 立即开始
1. **设置开发环境**
   - 安装 DDC-Market-SDK
   - 配置环境变量
   - 创建目录结构

2. **实现 ddc-metadata-query skill**
   - 创建基础文件
   - 实现 SDK 客户端封装
   - 实现元数据查询逻辑
   - 编写测试

3. **实现 ddc-supply-verification skill**
   - 复用 SDK 客户端
   - 实现供应量验证逻辑
   - 编写测试

### 后续计划
- Phase 2: 实现 ddc-holder-analysis
- Phase 3: 根据需求决定是否实现 ddc-membership-snapshot
- 持续优化和维护

---

**最后更新**: 2026-01-29
**制定者**: Promise Breaker Team
