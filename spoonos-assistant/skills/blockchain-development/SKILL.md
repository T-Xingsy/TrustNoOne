---
name: SpoonOS Blockchain Development
description: This skill should be used when the user asks about "building blockchain agents", "DeFi agent development", "NFT agent", "DAO agent", "Web3 development with SpoonOS", "blockchain security", "smart contract interaction", or needs guidance on building production-ready blockchain applications with SpoonOS.
version: 0.1.0
---

# SpoonOS Blockchain Development Guide

Build production-ready blockchain agents for DeFi, NFT, and DAO applications with SpoonOS.

## Overview

SpoonOS provides comprehensive tools for blockchain development across multiple chains:
- **EVM Chains**: Ethereum, Polygon, BSC, Arbitrum, Optimism
- **Solana**: High-performance blockchain
- **Neo**: N3 smart economy platform

## Application Types

### 1. DeFi Agents

#### Portfolio Manager
Track and manage crypto portfolios across multiple chains.

```python
from spoon_ai_sdk.agents import SpoonReactAI
from spoon_ai_sdk.llm import LLMManager
from spoon_toolkits.crypto.evm import EVMGetBalance, EVMGetTokenBalance
from spoon_toolkits.data import CoinGeckoPrice, CoinGeckoMarketData

llm = LLMManager(provider="openai", model="gpt-4")

tools = [
    EVMGetBalance(rpc_url=os.getenv("ETH_RPC")),
    EVMGetTokenBalance(rpc_url=os.getenv("ETH_RPC")),
    CoinGeckoPrice(),
    CoinGeckoMarketData()
]

agent = SpoonReactAI(
    llm=llm,
    tools=tools,
    system_prompt="""You are a portfolio management assistant.

    Capabilities:
    - Track balances across tokens
    - Get real-time prices
    - Calculate portfolio value
    - Provide market insights

    Guidelines:
    - Always verify addresses
    - Show prices with 24h changes
    - Calculate total portfolio value in USD
    - Warn about significant price movements
    """,
    max_iterations=5
)
```

#### Trading Bot
Automated trading with gas optimization.

```python
from spoon_toolkits.crypto.evm import (
    EVMGetGasPrice,
    EVMSwapTokens,
    EVMGetBalance
)

tools = [
    EVMGetGasPrice(rpc_url=os.getenv("ETH_RPC")),
    EVMSwapTokens(
        rpc_url=os.getenv("ETH_RPC"),
        private_key=os.getenv("PRIVATE_KEY")
    ),
    EVMGetBalance(rpc_url=os.getenv("ETH_RPC")),
    CoinGeckoPrice()
]

agent = SpoonReactAI(
    llm=llm,
    tools=tools,
    system_prompt="""You are a trading assistant.

    Trading Rules:
    - Only trade when gas < 30 gwei
    - Check balance before swaps
    - Use 0.5% slippage tolerance
    - Confirm all trades with user
    - Never trade without explicit approval

    Risk Management:
    - Maximum 10% of portfolio per trade
    - Stop loss at -5%
    - Take profit at +15%
    """,
    max_iterations=7
)
```

#### Yield Optimizer
Find and optimize yield farming opportunities.

```python
from spoon_toolkits.data import DeFiLlamaTVL

tools = [
    DeFiLlamaTVL(),
    EVMGetBalance(rpc_url=os.getenv("ETH_RPC")),
    CoinGeckoPrice()
]

agent = SpoonReactAI(
    llm=llm,
    tools=tools,
    system_prompt="""You are a yield farming advisor.

    Analysis:
    - Compare APYs across protocols
    - Consider TVL and security
    - Calculate impermanent loss risk
    - Factor in gas costs

    Recommendations:
    - Prioritize audited protocols
    - Diversify across platforms
    - Monitor for rug pulls
    - Rebalance quarterly
    """
)
```

### 2. NFT Agents

#### NFT Marketplace Monitor
Track NFT prices and sales.

```python
from spoon_toolkits.crypto.evm import EVMGetTokenBalance, EVMCallContract

tools = [
    EVMGetTokenBalance(rpc_url=os.getenv("ETH_RPC")),
    EVMCallContract(rpc_url=os.getenv("ETH_RPC")),
    CoinGeckoPrice()
]

agent = SpoonReactAI(
    llm=llm,
    tools=tools,
    system_prompt="""You are an NFT marketplace assistant.

    Capabilities:
    - Check NFT ownership
    - Get floor prices
    - Track sales volume
    - Analyze trends

    Insights:
    - Compare prices across marketplaces
    - Identify undervalued NFTs
    - Track whale movements
    - Alert on significant sales
    """
)
```

#### NFT Minting Bot
Automated NFT minting with rarity analysis.

```python
from spoon_toolkits.storage import IPFSUpload

tools = [
    IPFSUpload(api_url="https://ipfs.infura.io:5001"),
    EVMCallContract(rpc_url=os.getenv("ETH_RPC")),
    EVMGetGasPrice(rpc_url=os.getenv("ETH_RPC"))
]

agent = SpoonReactAI(
    llm=llm,
    tools=tools,
    system_prompt="""You are an NFT minting assistant.

    Workflow:
    1. Upload metadata to IPFS
    2. Check gas prices
    3. Mint NFT on contract
    4. Verify minting success

    Best Practices:
    - Validate metadata format
    - Optimize gas timing
    - Verify contract address
    - Confirm transaction
    """
)
```

### 3. DAO Agents

#### Governance Assistant
Help with DAO governance and voting.

```python
from spoon_toolkits.crypto.evm import EVMCallContract, EVMGetTransaction
from spoon_toolkits.memory import AddMemory, SearchMemory

tools = [
    EVMCallContract(rpc_url=os.getenv("ETH_RPC")),
    EVMGetTransaction(rpc_url=os.getenv("ETH_RPC")),
    AddMemory(),
    SearchMemory()
]

agent = SpoonReactAI(
    llm=llm,
    tools=tools,
    system_prompt="""You are a DAO governance assistant.

    Capabilities:
    - Read proposals
    - Check voting power
    - Track voting history
    - Analyze proposal outcomes

    Guidance:
    - Summarize proposals clearly
    - Explain voting implications
    - Track member participation
    - Remember past decisions
    """
)
```

#### Treasury Manager
Manage DAO treasury and funds.

```python
tools = [
    EVMGetBalance(rpc_url=os.getenv("ETH_RPC")),
    EVMGetTokenBalance(rpc_url=os.getenv("ETH_RPC")),
    EVMTransfer(
        rpc_url=os.getenv("ETH_RPC"),
        private_key=os.getenv("DAO_PRIVATE_KEY")
    ),
    CoinGeckoPrice()
]

agent = SpoonReactAI(
    llm=llm,
    tools=tools,
    system_prompt="""You are a DAO treasury manager.

    Responsibilities:
    - Monitor treasury balances
    - Track token holdings
    - Execute approved transfers
    - Report financial status

    Security:
    - Require multi-sig approval
    - Verify recipient addresses
    - Log all transactions
    - Alert on large movements
    """
)
```

## Multi-Chain Development

### Cross-Chain Agent
Operate across multiple blockchains.

```python
from spoon_toolkits.crypto.evm import EVMGetBalance
from spoon_toolkits.crypto.solana import SolanaGetBalance
from spoon_toolkits.crypto.neo import NeoGetBalance

tools = [
    EVMGetBalance(rpc_url=os.getenv("ETH_RPC")),
    SolanaGetBalance(rpc_url=os.getenv("SOL_RPC")),
    NeoGetBalance(rpc_url=os.getenv("NEO_RPC")),
    CoinGeckoPrice()
]

agent = SpoonReactAI(
    llm=llm,
    tools=tools,
    system_prompt="""You are a multi-chain portfolio manager.

    Supported Chains:
    - Ethereum (EVM)
    - Solana
    - Neo N3

    Features:
    - Unified balance view
    - Cross-chain price comparison
    - Total portfolio value
    - Chain-specific insights
    """
)
```

## Security Best Practices

### 1. Private Key Management
```python
# ✅ Good: Use environment variables
private_key = os.getenv("PRIVATE_KEY")

# ❌ Bad: Hardcode keys
private_key = "0x123..."  # NEVER DO THIS
```

### 2. Address Validation
```python
from web3 import Web3

def validate_address(address: str) -> bool:
    return Web3.is_address(address)

# Always validate before transactions
if not validate_address(user_address):
    return "Invalid address"
```

### 3. Transaction Confirmation
```python
system_prompt = """
Before executing any transaction:
1. Show transaction details
2. Request explicit user confirmation
3. Verify all parameters
4. Check gas costs
5. Only proceed after "yes" or "confirm"
"""
```

### 4. Gas Limits
```python
# Set reasonable gas limits
EVMTransfer(
    rpc_url=rpc_url,
    private_key=private_key,
    gas_limit=21000  # Standard transfer
)
```

### 5. Slippage Protection
```python
# Use appropriate slippage for swaps
EVMSwapTokens(
    rpc_url=rpc_url,
    private_key=private_key,
    slippage=0.5  # 0.5% slippage
)
```

## Error Handling

### Robust Error Handling
```python
from spoon_ai_sdk.exceptions import ToolExecutionError

try:
    response = agent.run(user_input)
except ToolExecutionError as e:
    if "insufficient funds" in str(e).lower():
        response = "Insufficient balance for this transaction"
    elif "gas price" in str(e).lower():
        response = "Gas price too high, try again later"
    elif "invalid address" in str(e).lower():
        response = "Invalid address provided"
    else:
        response = f"Transaction failed: {e}"
```

## Testing

### Test with Testnets
```python
# Use testnet RPCs for development
ETH_TESTNET_RPC = "https://goerli.infura.io/v3/YOUR_KEY"
SOL_TESTNET_RPC = "https://api.devnet.solana.com"

tools = [
    EVMGetBalance(rpc_url=ETH_TESTNET_RPC),
    SolanaGetBalance(rpc_url=SOL_TESTNET_RPC)
]
```

### Mock Tools for Unit Tests
```python
class MockEVMGetBalance(BaseTool):
    name: str = "evm_get_balance"
    description: str = "Mock balance tool"

    def _run(self, address: str) -> str:
        return "1.5 ETH"  # Mock response

# Use in tests
agent = ToolCallAgent(llm=llm, tools=[MockEVMGetBalance()])
```

## Deployment

### Production Checklist
- [ ] Use mainnet RPCs
- [ ] Secure private key storage
- [ ] Enable logging
- [ ] Set up monitoring
- [ ] Implement rate limiting
- [ ] Add error alerts
- [ ] Test with small amounts first
- [ ] Have emergency stop mechanism

### Environment Configuration
```bash
# .env.production
ETHEREUM_RPC_URL=https://eth-mainnet.g.alchemy.com/v2/YOUR_KEY
PRIVATE_KEY=0x...  # Use hardware wallet or KMS
OPENAI_API_KEY=sk-...

# Monitoring
SENTRY_DSN=https://...
LOG_LEVEL=INFO
```

## Performance Optimization

### 1. Caching
```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_token_price(token_id: str) -> float:
    tool = CoinGeckoPrice()
    return tool._run(coin_id=token_id, vs_currency="usd")
```

### 2. Batch Operations
```python
# Batch balance checks
addresses = ["0x...", "0x...", "0x..."]
balances = [get_balance(addr) for addr in addresses]
```

### 3. Async Operations
```python
import asyncio

async def check_multiple_chains():
    eth_task = agent.arun("Check ETH balance")
    sol_task = agent.arun("Check SOL balance")

    eth_result, sol_result = await asyncio.gather(eth_task, sol_task)
    return eth_result, sol_result
```

## Real-World Examples

### Example 1: DeFi Dashboard
Complete portfolio tracking and management system.

### Example 2: NFT Sniper Bot
Automated NFT purchasing based on rarity and price.

### Example 3: DAO Voting Bot
Automated governance participation based on rules.

### Example 4: Yield Aggregator
Multi-protocol yield optimization.

## Common Patterns

### Pattern 1: Check Before Execute
```python
# Always check balance before transfer
balance = get_balance_tool._run(address)
if balance < amount:
    return "Insufficient balance"
transfer_tool._run(to_address, amount)
```

### Pattern 2: Gas Optimization
```python
# Check gas before transaction
gas_price = get_gas_tool._run()
if gas_price > 50:  # gwei
    return "Gas too high, wait for lower prices"
```

### Pattern 3: Multi-Step Verification
```python
# Verify → Confirm → Execute
details = get_transaction_details()
confirmation = ask_user_confirmation(details)
if confirmation == "yes":
    execute_transaction()
```

## Next Steps

- **Explore Tools**: Use `toolkit-tools` skill for available blockchain tools
- **Learn Patterns**: Use `agent-patterns` skill for agent design
- **MCP Integration**: Use `mcp-integration` skill for dynamic tools

## Additional Resources

- `references/defi-patterns.md` - DeFi development patterns
- `references/nft-development.md` - NFT agent development
- `references/dao-development.md` - DAO agent development
- `references/security-guide.md` - Blockchain security best practices
- `examples/` - Complete application examples
