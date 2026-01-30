# Skills 架构设计 - Promise Breaker Detector

## 设计原则

基于 Promise Breaker Detector 项目的核心需求，设计以下 skills 架构：

### 核心目标
- **专注验证**：只实现验证 NFT 项目承诺所需的功能
- **使用 DDC-Market-SDK**：完全基于 DDC-Market-SDK API，不使用 ethers.js
- **模块化设计**：每个 skill 专注一个验证场景
- **LLM 友好**：输出格式化为 LLM 易于理解的上下文

---

## Skills 架构

### 1. ddc-metadata-query
**目的**：查询和分析 NFT 元数据

**核心功能**：
- 获取单个或批量 NFT 的元数据 URI
- 下载并解析元数据内容（JSON）
- 提取关键信息（名称、描述、属性、图片等）
- 对比承诺内容与实际元数据

**使用的 SDK API**：
- `getTokenURI(tokenId)` - 获取元数据 URI
- `getName()` - 获取合约名称
- `getSymbol()` - 获取合约符号

**输入参数**：
```typescript
{
  contractAddress: string;      // NFT 合约地址
  tokenIds: bigint[];           // 要查询的 token ID 列表
  promise?: {                   // 可选：承诺内容
    expectedName?: string;      // 期望的名称
    expectedDescription?: string; // 期望的描述
    expectedAttributes?: Record<string, any>; // 期望的属性
  }
}
```

**输出格式**：
```typescript
{
  contractInfo: {
    name: string;
    symbol: string;
    address: string;
  };
  tokens: Array<{
    tokenId: bigint;
    uri: string;
    metadata: {
      name: string;
      description: string;
      image: string;
      attributes: Record<string, any>;
    };
    matchesPromise?: boolean;   // 如果提供了 promise
  }>;
  summary: {
    totalQueried: number;
    successfullyParsed: number;
    matchingPromise: number;    // 如果提供了 promise
  };
  llmContext: string;           // 格式化的 LLM 上下文
}
```

**验证场景**：
- 验证 NFT 元数据是否符合项目承诺的内容
- 验证 NFT 名称、描述、属性是否一致
- 验证图片资源是否可访问

---

### 2. ddc-holder-analysis
**目的**：分析 NFT 持有者分布和统计

**核心功能**：
- 获取指定 token 的持有者
- 统计总供应量
- 分析持有者分布（需要遍历 tokenId）
- 识别大户和散户分布

**使用的 SDK API**：
- `getOwnerOf(tokenId)` - 获取持有者 hash
- `getTotalSupply()` - 获取总供应量
- `getName()`, `getSymbol()` - 获取合约信息

**输入参数**：
```typescript
{
  contractAddress: string;      // NFT 合约地址
  tokenIdRange?: {              // 可选：指定 token ID 范围
    start: bigint;
    end: bigint;
  };
  promise?: {                   // 可选：承诺内容
    expectedHolders?: number;   // 期望的持有者数量
    expectedSupply?: number;    // 期望的供应量
  }
}
```

**输出格式**：
```typescript
{
  contractInfo: {
    name: string;
    symbol: string;
    address: string;
  };
  supply: {
    total: bigint;
    analyzed: number;           // 实际分析的 token 数量
  };
  holders: {
    unique: number;             // 唯一持有者数量
    distribution: Array<{       // 持有者分布
      ownerHash: string;
      tokenCount: number;
      percentage: number;
    }>;
    topHolders: Array<{         // 前 10 大户
      ownerHash: string;
      tokenCount: number;
    }>;
  };
  matchesPromise?: {            // 如果提供了 promise
    holdersMatch: boolean;
    supplyMatch: boolean;
  };
  llmContext: string;
}
```

**验证场景**：
- 验证 NFT 持有者数量是否符合承诺
- 验证供应量是否符合承诺
- 分析持有者集中度（是否存在操纵）

---

### 3. ddc-supply-verification
**目的**：验证 NFT 铸造和供应量承诺

**核心功能**：
- 获取总供应量
- 对比承诺的铸造数量
- 计算履约率
- 生成证据强度评估

**使用的 SDK API**：
- `getTotalSupply()` - 获取总供应量
- `getName()`, `getSymbol()` - 获取合约信息

**输入参数**：
```typescript
{
  contractAddress: string;      // NFT 合约地址
  promise: {
    expectedSupply: number;     // 承诺的供应量
    deadline?: string;          // 承诺的截止日期
    description: string;        // 承诺描述
  }
}
```

**输出格式**：
```typescript
{
  contractInfo: {
    name: string;
    symbol: string;
    address: string;
  };
  supply: {
    actual: bigint;
    expected: number;
    difference: number;
  };
  verification: {
    fulfilled: boolean;
    fulfillmentRate: number;    // 履约率 (0-100)
    evidenceStrength: 'strong' | 'moderate' | 'weak' | 'none';
  };
  llmContext: string;
}
```

**验证场景**：
- 验证项目是否按承诺铸造了指定数量的 NFT
- 验证是否超发或少发
- 评估承诺兑现程度

---

### 4. ddc-membership-snapshot
**目的**：分析会员快照，验证会员权益承诺

**核心功能**：
- 获取会员快照列表
- 分析快照中的会员数量
- 对比不同时间点的快照变化
- 验证"给所有持有者"类型的承诺

**使用的 SDK API**：
- `getMemberSnapshot(snapshotId)` - 获取会员快照
- `getLatestSnapshotId()` - 获取最新快照 ID
- `isMemberInSnapshot()` - 检查是否在快照中
- `getTotalSupply()` - 获取总供应量

**输入参数**：
```typescript
{
  contractAddress: string;      // Membership 合约地址
  snapshotIds?: bigint[];       // 可选：指定快照 ID 列表
  promise?: {                   // 可选：承诺内容
    expectedMembers?: number;   // 期望的会员数量
    snapshotDate?: string;      // 快照日期
    description: string;        // 承诺描述
  }
}
```

**输出格式**：
```typescript
{
  contractInfo: {
    name: string;
    symbol: string;
    address: string;
  };
  snapshots: Array<{
    snapshotId: bigint;
    memberCount: number;
    members: string[];          // 会员 hash 列表
  }>;
  analysis: {
    latestSnapshotId: bigint;
    totalMembers: number;
    uniqueMembers: number;      // 跨快照的唯一会员数
  };
  matchesPromise?: {            // 如果提供了 promise
    memberCountMatch: boolean;
    fulfillmentRate: number;
  };
  llmContext: string;
}
```

**验证场景**：
- 验证会员数量是否符合承诺
- 验证特定时间点的会员列表
- 验证"给所有持有者空投"的承诺（通过快照）

---

## 与现有 onchain-data-query 的对比

### 现有 skill 的问题
1. **技术栈不匹配**：使用 ethers.js 而不是 DDC-Market-SDK
2. **功能覆盖不足**：只有 Transfer 事件查询，缺少元数据、持有者、供应量等关键功能
3. **验证能力弱**：缺少与承诺内容的对比和履约率计算
4. **不支持会员系统**：无法验证会员相关的承诺

### 新架构的优势
1. **完全基于 DDC-Market-SDK**：充分利用 SDK 的高级功能
2. **模块化设计**：每个 skill 专注一个验证场景，易于维护和扩展
3. **验证能力强**：内置承诺对比和履约率计算
4. **支持会员系统**：可以验证会员快照相关的承诺
5. **LLM 友好**：输出格式化为 LLM 易于理解的上下文

---

## 实施优先级

### Phase 1: 核心验证功能（高优先级）
1. **ddc-metadata-query** - 元数据查询（用户特别提到）
2. **ddc-supply-verification** - 供应量验证（最常见的承诺类型）

### Phase 2: 高级分析功能（中优先级）
3. **ddc-holder-analysis** - 持有者分析

### Phase 3: 会员系统支持（低优先级）
4. **ddc-membership-snapshot** - 会员快照分析（仅在项目使用会员系统时需要）

---

## 技术实现要点

### 1. SDK 初始化
```typescript
import { DDCNFTManager, MembershipManager } from '@ddc-market/sdk';

// 使用 JsonRpcProvider 模式（适合后端）
const ddcManager = await DDCNFTManager.init({
  walletAddress: process.env.WALLET_ADDRESS,
  provider: { type: 'jsonRpc' },
  signer: { privateKey: process.env.PRIVATE_KEY },
  debug: true,
});

// 设置合约地址
ddcManager.setContractAddress(contractAddress);
```

### 2. 错误处理
- RPC 超时：实现重试机制
- 合约不存在：返回友好的错误信息
- 元数据解析失败：记录失败的 token ID，继续处理其他 token

### 3. 性能优化
- 批量查询：使用 Promise.all 并行查询多个 token
- 缓存：缓存合约信息和元数据
- 分页：对于大量 token，实现分页查询

### 4. LLM 上下文格式化
- 使用 Markdown 格式
- 突出关键信息（履约率、证据强度）
- 提供简洁的摘要和详细的数据

---

## 下一步行动

1. **实现 ddc-metadata-query skill**（用户特别提到的元数据获取）
2. **实现 ddc-supply-verification skill**（最常见的验证场景）
3. **测试与 SpoonOS Agent 的集成**
4. **根据实际使用情况调整和优化**

---

**最后更新**: 2026-01-29
**设计者**: Promise Breaker Team
