---
name: onchain-data-query
description: 查询和验证链上 NFT 数据，用于 Promise Breaker Detector 项目的承诺验证。支持查询 NFT 转账、空投记录、交易历史等，并提供数据清洗和 LLM 上下文格式化功能。
---

# 链上数据查询与验证技能

本技能提供完整的链上数据查询和验证能力，专为 Promise Breaker Detector 项目设计，用于验证 NFT 项目的承诺是否兑现。

## 🎯 核心功能

### 1. NFT 事件查询
- 查询 Transfer 事件（转账、铸造、销毁）
- 按时间范围过滤
- 按地址过滤（from/to）
- 获取事件详情（区块号、时间戳、交易哈希）

### 2. 空投验证
- 识别空投交易（从零地址或项目方地址批量转出）
- 统计空投接收者数量
- 计算空投代币总量
- 验证是否符合承诺的空投计划

### 3. 数据分析
- 统计 NFT 持有者分布
- 分析交易活跃度
- 计算履约率（实际 vs 承诺）
- 生成证据强度评估

### 4. LLM 集成
- 格式化数据为 LLM 友好的上下文
- 生成初步分析报告
- 提供紧凑模式（节省 token）

## 🚀 快速开始

### 前置条件

```bash
# 1. 激活 conda 环境
conda activate hackason

# 2. 安装依赖
cd /home/ssszyy/code/web3/hackason-project/onchain-verifier
npm install ethers@6
# 或使用 Python 包装器
pip install web3
```

### 基础使用

#### 1. 初始化查询客户端

```typescript
import { OnChainVerifier } from './scripts/verifier';

// 初始化（使用 DDC 链或其他 EVM 链）
const verifier = new OnChainVerifier({
  rpcUrl: process.env.RPC_URL,
  contractAddress: '0x...', // NFT 合约地址
  contractABI: DDCNFT_ABI,   // 从 DDC Market SDK 获取
});
```

#### 2. 查询 NFT 转账事件

```typescript
// 查询特定时间范围的转账
const transfers = await verifier.queryTransferEvents({
  startTime: new Date('2024-04-01'),
  endTime: new Date('2024-06-30'),
  eventType: 'all', // 'mint' | 'transfer' | 'burn' | 'all'
});

console.log(`找到 ${transfers.length} 条转账记录`);
```

#### 3. 验证空投承诺

```typescript
// 承诺：Q2 2024 空投 1000 个 NFT 给所有持有者
const promise = {
  content: "Q2 2024 airdrop 1000 NFTs to all holders",
  deadline: "2024-06-30",
  expectedAmount: 1000,
  expectedRecipients: "all holders"
};

// 查询实际空投数据
const airdropData = await verifier.verifyAirdropPromise({
  promise,
  projectAddress: '0x...', // 项目方地址
  startTime: new Date('2024-04-01'),
  endTime: new Date('2024-06-30'),
});

console.log(`
  承诺: ${promise.content}
  实际空投: ${airdropData.totalAmount} 个 NFT
  接收者: ${airdropData.uniqueRecipients} 人
  履约率: ${airdropData.fulfillmentRate}%
  证据强度: ${airdropData.evidenceStrength}
`);
```

#### 4. 生成 LLM 上下文

```typescript
// 格式化为 LLM 友好的验证上下文
const context = await verifier.formatForLLM({
  promise,
  onchainData: airdropData,
  mode: 'full', // 'full' | 'compact' | 'scoring'
});

// 可以直接传给 VerificationAgent
await verificationAgent.verify(context);
```

## 📚 详细 API

### OnChainVerifier 类

#### 构造函数

```typescript
constructor(config: {
  rpcUrl: string;           // RPC 节点 URL
  contractAddress: string;  // NFT 合约地址
  contractABI: any[];       // 合约 ABI
  chainId?: number;         // 链 ID（可选）
})
```

#### 方法

##### queryTransferEvents()

查询 Transfer 事件。

```typescript
async queryTransferEvents(params: {
  startTime?: Date;         // 开始时间
  endTime?: Date;           // 结束时间
  startBlock?: number;      // 开始区块（优先于时间）
  endBlock?: number;        // 结束区块
  from?: string;            // 发送方地址
  to?: string;              // 接收方地址
  eventType?: 'mint' | 'transfer' | 'burn' | 'all';
}): Promise<TransferEvent[]>
```

**返回值**:
```typescript
interface TransferEvent {
  from: string;
  to: string;
  tokenId: bigint;
  blockNumber: number;
  transactionHash: string;
  timestamp: number;
  eventType: 'mint' | 'transfer' | 'burn';
}
```

##### verifyAirdropPromise()

验证空投承诺。

```typescript
async verifyAirdropPromise(params: {
  promise: Promise;
  projectAddress: string;
  startTime: Date;
  endTime: Date;
  minBatchSize?: number;    // 最小批量大小（默认 5）
}): Promise<AirdropVerification>
```

**返回值**:
```typescript
interface AirdropVerification {
  totalAmount: number;
  uniqueRecipients: number;
  transactions: TransferEvent[];
  fulfillmentRate: number;
  evidenceStrength: 'strong' | 'moderate' | 'weak' | 'none';
  summary: string;
}
```

##### getContractStatistics()

获取合约统计信息。

```typescript
async getContractStatistics(): Promise<{
  totalSupply: number;
  totalMinted: number;
  totalBurned: number;
  uniqueHolders: number;
  activeHolders: number;
}>
```

##### formatForLLM()

格式化数据为 LLM 上下文。

```typescript
async formatForLLM(params: {
  promise: Promise;
  onchainData: AirdropVerification;
  mode: 'full' | 'compact' | 'scoring';
}): Promise<string>
```

## 🔧 配置

### 环境变量

创建 `.env` 文件：

```bash
# RPC 节点配置
RPC_URL=https://your-rpc-endpoint.com
CHAIN_ID=1

# 合约地址
NFT_CONTRACT_ADDRESS=0x...

# 可选：备用 RPC（用于故障转移）
FALLBACK_RPC_URL=https://backup-rpc.com

# 调试模式
DEBUG=true
```

### 网络配置

支持的网络：
- Ethereum Mainnet
- Polygon
- BSC
- DDC Chain（如果提供 RPC）
- 任何 EVM 兼容链

## 💡 使用场景

### 场景 1: 验证空投承诺

```typescript
// 项目承诺：2024 Q2 空投 1000 NFT
const result = await verifier.verifyAirdropPromise({
  promise: {
    content: "Q2 2024 airdrop 1000 NFTs",
    deadline: "2024-06-30",
    expectedAmount: 1000
  },
  projectAddress: '0xProjectWallet',
  startTime: new Date('2024-04-01'),
  endTime: new Date('2024-06-30'),
});

// 结果：实际空投 500 NFT，履约率 50%
```

### 场景 2: 验证持有者奖励

```typescript
// 项目承诺：每月给持有者空投奖励
const monthlyAirdrops = [];

for (let month = 1; month <= 12; month++) {
  const startDate = new Date(2024, month - 1, 1);
  const endDate = new Date(2024, month, 0);

  const airdrop = await verifier.verifyAirdropPromise({
    promise: { content: `${month}月持有者奖励` },
    projectAddress: '0xProject',
    startTime: startDate,
    endTime: endDate,
  });

  monthlyAirdrops.push({
    month,
    fulfilled: airdrop.totalAmount > 0,
    recipients: airdrop.uniqueRecipients
  });
}

// 分析：12 个月中有 8 个月兑现承诺
```

### 场景 3: 集成到 SpoonOS Agent

```python
from onchain_verifier import OnChainVerifier
from spoonos import BaseTool

class OnChainQueryTool(BaseTool):
    name = "onchain_query"
    description = "查询链上数据验证项目承诺"

    def __init__(self):
        self.verifier = OnChainVerifier(
            rpc_url=os.getenv('RPC_URL'),
            contract_address=os.getenv('NFT_CONTRACT_ADDRESS')
        )

    async def execute(self, promise: dict, time_range: dict):
        result = await self.verifier.verify_airdrop_promise(
            promise=promise,
            start_time=time_range['start'],
            end_time=time_range['end']
        )

        return {
            "found": result['totalAmount'] > 0,
            "evidence": result,
            "fulfillment_rate": result['fulfillmentRate']
        }
```

## 🎓 最佳实践

### 1. 时间范围选择

```typescript
// ✅ 好的做法：使用承诺的时间范围
const result = await verifier.queryTransferEvents({
  startTime: promise.startDate,
  endTime: promise.deadline,
});

// ❌ 避免：查询过大的时间范围
const result = await verifier.queryTransferEvents({
  startTime: new Date('2020-01-01'), // 太早
  endTime: new Date(),                // 到现在
});
```

### 2. 批量查询优化

```typescript
// ✅ 好的做法：分批查询大量数据
async function queryLargeTimeRange(start: Date, end: Date) {
  const chunks = splitTimeRange(start, end, 30); // 按月分割
  const results = [];

  for (const chunk of chunks) {
    const events = await verifier.queryTransferEvents(chunk);
    results.push(...events);
    await sleep(1000); // 避免 RPC 限流
  }

  return results;
}
```

### 3. 错误处理

```typescript
// ✅ 好的做法：处理 RPC 错误和重试
try {
  const result = await verifier.queryTransferEvents(params);
} catch (error) {
  if (error.code === 'TIMEOUT') {
    // 使用备用 RPC
    verifier.switchToFallbackRPC();
    return await verifier.queryTransferEvents(params);
  }
  throw error;
}
```

### 4. 数据缓存

```typescript
// ✅ 好的做法：缓存历史数据
const cacheKey = `transfers_${contractAddress}_${startBlock}_${endBlock}`;
let events = cache.get(cacheKey);

if (!events) {
  events = await verifier.queryTransferEvents(params);
  cache.set(cacheKey, events, { ttl: 3600 }); // 缓存 1 小时
}
```

## 🔍 故障排除

### 问题 1: RPC 请求超时

**症状**: `Error: timeout of 30000ms exceeded`

**解决方案**:
```typescript
// 增加超时时间或减小查询范围
const verifier = new OnChainVerifier({
  ...config,
  timeout: 60000, // 60 秒
});

// 或分批查询
const events = await queryInBatches(startBlock, endBlock, 1000);
```

### 问题 2: 找不到事件

**症状**: 返回空数组但确定有交易

**解决方案**:
```typescript
// 1. 检查合约地址是否正确
console.log('Contract:', verifier.contractAddress);

// 2. 检查时间范围是否正确
const block = await verifier.provider.getBlock(blockNumber);
console.log('Block timestamp:', new Date(block.timestamp * 1000));

// 3. 检查事件签名是否匹配
const filter = contract.filters.Transfer();
console.log('Filter topics:', filter.topics);
```

### 问题 3: 内存溢出

**症状**: `JavaScript heap out of memory`

**解决方案**:
```typescript
// 使用流式处理大量数据
async function* streamTransferEvents(params) {
  const batchSize = 1000;
  let currentBlock = params.startBlock;

  while (currentBlock <= params.endBlock) {
    const events = await verifier.queryTransferEvents({
      startBlock: currentBlock,
      endBlock: Math.min(currentBlock + batchSize, params.endBlock)
    });

    yield* events;
    currentBlock += batchSize + 1;
  }
}

// 使用
for await (const event of streamTransferEvents(params)) {
  processEvent(event);
}
```

## 📖 参考资料

### ��关文档
- [ethers.js 文档](https://docs.ethers.org/v6/)
- [DDC Market SDK](https://github.com/DataDanceChain/DDC-Market-SDK)
- [ERC-721 标准](https://eips.ethereum.org/EIPS/eip-721)

### 示例代码
- `examples/basic_query.ts` - 基础查询示例
- `examples/airdrop_verification.ts` - 空投验证示例
- `examples/spoonos_integration.py` - SpoonOS 集成示例

### 工具脚本
- `scripts/verifier.ts` - 核心验证器实现
- `scripts/event_parser.ts` - 事件解析器
- `scripts/data_formatter.ts` - 数据格式化器

---

**最后更新**: 2026-01-29
**维护者**: Promise Breaker Team
