# onchain-verifier

链上数据查询与验证插件，专为 Promise Breaker Detector 项目设计。

## 🎯 核心功能

- ✅ 查询 NFT Transfer 事件（铸造、转账、销毁）
- ✅ 验证空投承诺（批量转账识别）
- ✅ 时间范围过滤和区块范围查询
- ✅ 数据清洗和结构化
- ✅ LLM 上下文格式化
- ✅ SpoonOS Agent 集成

## 📦 安装

### 1. 前置条件

```bash
# Node.js 18+
node --version

# Python 3.8+
python --version

# conda 环境
conda activate hackason
```

### 2. 安装依赖

```bash
cd /home/ssszyy/code/web3/hackason-project/onchain-verifier

# TypeScript 依赖
npm install ethers@6

# Python 依赖
pip install web3
```

### 3. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件
```

## 🚀 快速开始

### TypeScript 使用

```typescript
import { OnChainVerifier } from './scripts/verifier';

const verifier = new OnChainVerifier({
  rpcUrl: process.env.RPC_URL!,
  contractAddress: '0x...',
  contractABI: DDCNFT_ABI,
});

// 查询转账事件
const transfers = await verifier.queryTransferEvents({
  startTime: new Date('2024-04-01'),
  endTime: new Date('2024-06-30'),
});

console.log(`Found ${transfers.length} transfers`);
```

### Python 使用

```python
from scripts.verifier import OnChainVerifier

verifier = OnChainVerifier(
    rpc_url=os.getenv('RPC_URL'),
    contract_address='0x...',
    contract_abi=[]
)

# 验证空投承诺
result = verifier.verify_airdrop_promise(
    promise={'content': 'Q2 2024 airdrop'},
    project_address='0x...',
    start_time=datetime(2024, 4, 1),
    end_time=datetime(2024, 6, 30)
)

print(f"Fulfillment rate: {result.fulfillment_rate}%")
```

## 📚 文档

- [技能文档](skills/onchain-data-query/SKILL.md) - 完整的使用指南
- [API 参考](docs/API_REFERENCE.md) - 详细的 API 文档
- [集成示例](examples/) - 实际使用示例

## 🔧 配置

### 环境变量

```bash
# RPC 节点
RPC_URL=https://your-rpc-endpoint.com
CHAIN_ID=1

# 合约地址
NFT_CONTRACT_ADDRESS=0x...

# 可选
FALLBACK_RPC_URL=https://backup-rpc.com
DEBUG=true
```

### 支持的网络

- Ethereum Mainnet
- Polygon
- BSC
- 任何 EVM 兼容链

## 💡 使用场景

### 验证空投承诺

```typescript
const result = await verifier.verifyAirdropPromise({
  promise: {
    content: "Q2 2024 airdrop 1000 NFTs",
    expectedAmount: 1000
  },
  projectAddress: '0xProject',
  startTime: new Date('2024-04-01'),
  endTime: new Date('2024-06-30'),
});

// 结果：实际空投 500 NFT，履约率 50%
```

### 集成到 SpoonOS

```python
from scripts.verifier import OnChainQueryTool

class VerificationAgent(BaseAgent):
    tools = [OnChainQueryTool()]

    async def verify(self, project_name: str):
        result = await self.tools[0].execute(
            promise=promise,
            project_address='0x...',
            start_date='2024-04-01',
            end_date='2024-06-30'
        )
        return result
```

## 🎓 最佳实践

1. **时间范围选择**: 使用承诺的实际时间范围
2. **批量查询**: 大范围查询时分批处理
3. **错误处理**: 实现 RPC 故障转移
4. **数据缓存**: 缓存历史数据减少 RPC 调用

## 🔍 故障排除

### RPC 请求超时

```typescript
// 增加超时时间
const verifier = new OnChainVerifier({
  ...config,
  timeout: 60000, // 60 秒
});
```

### 找不到事件

```typescript
// 检查合约地址和时间范围
console.log('Contract:', verifier.contractAddress);
const block = await provider.getBlock(blockNumber);
console.log('Block time:', new Date(block.timestamp * 1000));
```

## 📖 参考资料

- [ethers.js 文档](https://docs.ethers.org/v6/)
- [DDC Market SDK](https://github.com/DataDanceChain/DDC-Market-SDK)
- [ERC-721 标准](https://eips.ethereum.org/EIPS/eip-721)

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

---

**最后更新**: 2026-01-29
**维护者**: Promise Breaker Team
