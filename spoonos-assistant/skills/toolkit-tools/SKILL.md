---
name: SpoonOS Toolkit Tools
description: This skill should be used when the user asks about "spoon-toolkit tools", "available blockchain tools", "EVM tools", "Solana tools", "Neo tools", "crypto tools catalog", "which tools are available", "tool categories", or needs to discover and understand the 50+ professional tools in spoon-toolkit.
version: 0.1.0
---

# SpoonOS Toolkit Tools Catalog

Explore 50+ production-ready tools for blockchain, crypto, and AI operations from spoon-toolkit.

## Overview

spoon-toolkit (package: `spoon-toolkits`) provides a comprehensive collection of professional-grade tools organized into categories:

- **Blockchain Tools**: EVM, Solana, Neo chain interactions
- **Crypto Operations**: Token transfers, swaps, balance queries
- **Data Platforms**: CoinGecko, DeFiLlama, blockchain explorers
- **Memory Tools**: Agent memory management
- **Audio Tools**: Text-to-speech, speech-to-text
- **Storage Tools**: Decentralized storage (NeoFS, IPFS)

All tools follow the `BaseTool` interface from spoon-core, making them plug-and-play with any agent.

## Installation

```bash
pip install spoon-toolkits
```

## Tool Categories

### 1. EVM Tools (`spoon_toolkits.crypto.evm`)

Tools for Ethereum and EVM-compatible chains (Polygon, BSC, Arbitrum, etc.)

#### EVMGetBalance
Get native token balance for an address.

```python
from spoon_toolkits.crypto.evm import EVMGetBalance

tool = EVMGetBalance(rpc_url="https://eth-mainnet.g.alchemy.com/v2/YOUR_KEY")
balance = tool._run(address="0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb")
# Returns: "1.234 ETH"
```

**Parameters**:
- `address`: Ethereum address (0x...)
- `rpc_url`: Optional custom RPC endpoint

**Use cases**: Portfolio tracking, balance verification, wallet monitoring

#### EVMGetTokenBalance
Get ERC-20 token balance for an address.

```python
from spoon_toolkits.crypto.evm import EVMGetTokenBalance

tool = EVMGetTokenBalance(rpc_url="https://...")
balance = tool._run(
    address="0x...",
    token_address="0xdAC17F958D2ee523a2206206994597C13D831ec7"  # USDT
)
# Returns: "1000.50 USDT"
```

**Parameters**:
- `address`: Wallet address
- `token_address`: ERC-20 token contract address
- `rpc_url`: Optional custom RPC endpoint

#### EVMTransfer
Transfer native tokens (ETH, MATIC, etc.)

```python
from spoon_toolkits.crypto.evm import EVMTransfer

tool = EVMTransfer(
    rpc_url="https://...",
    private_key=os.getenv("PRIVATE_KEY")
)
tx_hash = tool._run(
    to_address="0x...",
    amount=0.1,  # ETH
    gas_price=50  # gwei
)
# Returns: "0x... (transaction hash)"
```

**Parameters**:
- `to_address`: Recipient address
- `amount`: Amount in native token
- `gas_price`: Optional gas price in gwei

**Security**: Requires private key, use environment variables

#### EVMTokenTransfer
Transfer ERC-20 tokens.

```python
from spoon_toolkits.crypto.evm import EVMTokenTransfer

tool = EVMTokenTransfer(
    rpc_url="https://...",
    private_key=os.getenv("PRIVATE_KEY")
)
tx_hash = tool._run(
    token_address="0x...",  # Token contract
    to_address="0x...",  # Recipient
    amount=100  # Token amount
)
```

#### EVMSwapTokens
Swap tokens using DEX aggregators (Uniswap, 1inch, etc.)

```python
from spoon_toolkits.crypto.evm import EVMSwapTokens

tool = EVMSwapTokens(
    rpc_url="https://...",
    private_key=os.getenv("PRIVATE_KEY")
)
tx_hash = tool._run(
    from_token="0x...",  # Source token
    to_token="0x...",  # Destination token
    amount=100,
    slippage=0.5  # 0.5% slippage tolerance
)
```

**Parameters**:
- `from_token`: Source token address
- `to_token`: Destination token address
- `amount`: Amount to swap
- `slippage`: Slippage tolerance (%)

#### EVMGetGasPrice
Get current gas price for optimal transaction timing.

```python
from spoon_toolkits.crypto.evm import EVMGetGasPrice

tool = EVMGetGasPrice(rpc_url="https://...")
gas_price = tool._run()
# Returns: "45 gwei (standard), 60 gwei (fast), 80 gwei (instant)"
```

#### EVMEstimateGas
Estimate gas cost for a transaction.

```python
from spoon_toolkits.crypto.evm import EVMEstimateGas

tool = EVMEstimateGas(rpc_url="https://...")
estimate = tool._run(
    from_address="0x...",
    to_address="0x...",
    data="0x..."  # Transaction data
)
# Returns: "21000 gas (~$5.25 at 50 gwei)"
```

#### EVMGetTransaction
Get transaction details by hash.

```python
from spoon_toolkits.crypto.evm import EVMGetTransaction

tool = EVMGetTransaction(rpc_url="https://...")
tx_info = tool._run(tx_hash="0x...")
# Returns: JSON with transaction details
```

#### EVMGetBlockNumber
Get current block number.

```python
from spoon_toolkits.crypto.evm import EVMGetBlockNumber

tool = EVMGetBlockNumber(rpc_url="https://...")
block = tool._run()
# Returns: "18500000"
```

#### EVMCallContract
Call smart contract read-only methods.

```python
from spoon_toolkits.crypto.evm import EVMCallContract

tool = EVMCallContract(rpc_url="https://...")
result = tool._run(
    contract_address="0x...",
    function_name="balanceOf",
    function_args=["0x..."],
    abi=[...]  # Contract ABI
)
```

### 2. Solana Tools (`spoon_toolkits.crypto.solana`)

Tools for Solana blockchain interactions.

#### SolanaGetBalance
Get SOL balance for an address.

```python
from spoon_toolkits.crypto.solana import SolanaGetBalance

tool = SolanaGetBalance(rpc_url="https://api.mainnet-beta.solana.com")
balance = tool._run(address="...")
# Returns: "10.5 SOL"
```

#### SolanaGetTokenBalance
Get SPL token balance.

```python
from spoon_toolkits.crypto.solana import SolanaGetTokenBalance

tool = SolanaGetTokenBalance(rpc_url="https://...")
balance = tool._run(
    address="...",
    token_mint="..."  # Token mint address
)
```

#### SolanaTransfer
Transfer SOL to another address.

```python
from spoon_toolkits.crypto.solana import SolanaTransfer

tool = SolanaTransfer(
    rpc_url="https://...",
    private_key=os.getenv("SOLANA_PRIVATE_KEY")
)
signature = tool._run(
    to_address="...",
    amount=1.0  # SOL
)
```

#### SolanaTokenTransfer
Transfer SPL tokens.

```python
from spoon_toolkits.crypto.solana import SolanaTokenTransfer

tool = SolanaTokenTransfer(
    rpc_url="https://...",
    private_key=os.getenv("SOLANA_PRIVATE_KEY")
)
signature = tool._run(
    token_mint="...",
    to_address="...",
    amount=100
)
```

#### SolanaGetAccountInfo
Get account information.

```python
from spoon_toolkits.crypto.solana import SolanaGetAccountInfo

tool = SolanaGetAccountInfo(rpc_url="https://...")
info = tool._run(address="...")
# Returns: Account details including owner, lamports, data
```

### 3. Neo Tools (`spoon_toolkits.crypto.neo`)

Tools for Neo blockchain (N3).

#### NeoGetBlockCount
Get current block height.

```python
from spoon_toolkits.crypto.neo import NeoGetBlockCount

tool = NeoGetBlockCount(rpc_url="https://mainnet1.neo.org:443")
block_count = tool._run()
# Returns: "12345678"
```

#### NeoGetBalance
Get NEO/GAS balance for an address.

```python
from spoon_toolkits.crypto.neo import NeoGetBalance

tool = NeoGetBalance(rpc_url="https://...")
balance = tool._run(address="N...")
# Returns: "100 NEO, 50.5 GAS"
```

#### NeoInvokeContract
Invoke Neo smart contract methods.

```python
from spoon_toolkits.crypto.neo import NeoInvokeContract

tool = NeoInvokeContract(
    rpc_url="https://...",
    private_key=os.getenv("NEO_PRIVATE_KEY")
)
result = tool._run(
    contract_hash="0x...",
    method="transfer",
    params=[...]
)
```

#### NeoGetTransaction
Get transaction details.

```python
from spoon_toolkits.crypto.neo import NeoGetTransaction

tool = NeoGetTransaction(rpc_url="https://...")
tx_info = tool._run(tx_hash="0x...")
```

### 4. Data Platform Tools (`spoon_toolkits.data`)

Tools for accessing crypto market data and analytics.

#### CoinGeckoPrice
Get cryptocurrency prices from CoinGecko.

```python
from spoon_toolkits.data import CoinGeckoPrice

tool = CoinGeckoPrice()
price = tool._run(
    coin_id="bitcoin",
    vs_currency="usd"
)
# Returns: "$45,123.50 (24h change: +2.5%)"
```

**Parameters**:
- `coin_id`: CoinGecko coin identifier (bitcoin, ethereum, etc.)
- `vs_currency`: Target currency (usd, eur, etc.)

#### CoinGeckoMarketData
Get detailed market data.

```python
from spoon_toolkits.data import CoinGeckoMarketData

tool = CoinGeckoMarketData()
data = tool._run(coin_id="ethereum")
# Returns: Market cap, volume, supply, price changes, etc.
```

#### DeFiLlamaTVL
Get Total Value Locked (TVL) for DeFi protocols.

```python
from spoon_toolkits.data import DeFiLlamaTVL

tool = DeFiLlamaTVL()
tvl = tool._run(protocol="uniswap")
# Returns: "$5.2B TVL"
```

#### BlockExplorerSearch
Search transactions, addresses, blocks on blockchain explorers.

```python
from spoon_toolkits.data import BlockExplorerSearch

tool = BlockExplorerSearch(chain="ethereum")
result = tool._run(query="0x...")
# Returns: Transaction/address details from Etherscan
```

### 5. Memory Tools (`spoon_toolkits.memory`)

Tools for agent memory management.

#### AddMemory
Store information in agent memory.

```python
from spoon_toolkits.memory import AddMemory

tool = AddMemory()
result = tool._run(
    key="user_preference",
    value="Prefers DeFi over NFTs"
)
# Returns: "Memory stored successfully"
```

**Use cases**: Remember user preferences, store context, save important facts

#### SearchMemory
Search stored memories.

```python
from spoon_toolkits.memory import SearchMemory

tool = SearchMemory()
results = tool._run(query="user preference")
# Returns: Relevant memories matching the query
```

#### DeleteMemory
Remove specific memory.

```python
from spoon_toolkits.memory import DeleteMemory

tool = DeleteMemory()
result = tool._run(key="user_preference")
```

#### ListMemories
List all stored memories.

```python
from spoon_toolkits.memory import ListMemories

tool = ListMemories()
memories = tool._run()
# Returns: List of all memory keys and values
```

### 6. Audio Tools (`spoon_toolkits.audio`)

Tools for speech processing.

#### TextToSpeech
Convert text to speech using ElevenLabs.

```python
from spoon_toolkits.audio import TextToSpeech

tool = TextToSpeech(api_key=os.getenv("ELEVENLABS_API_KEY"))
audio_file = tool._run(
    text="Hello, this is a test",
    voice="adam",  # Voice ID
    output_path="output.mp3"
)
# Returns: Path to generated audio file
```

#### SpeechToText
Convert speech to text.

```python
from spoon_toolkits.audio import SpeechToText

tool = SpeechToText(api_key=os.getenv("OPENAI_API_KEY"))
text = tool._run(audio_file="input.mp3")
# Returns: Transcribed text
```

### 7. Storage Tools (`spoon_toolkits.storage`)

Tools for decentralized storage.

#### NeoFSUpload
Upload files to NeoFS.

```python
from spoon_toolkits.storage import NeoFSUpload

tool = NeoFSUpload(
    endpoint="https://...",
    wallet_key=os.getenv("NEOFS_WALLET_KEY")
)
object_id = tool._run(
    file_path="document.pdf",
    container_id="..."
)
# Returns: NeoFS object ID
```

#### NeoFSDownload
Download files from NeoFS.

```python
from spoon_toolkits.storage import NeoFSDownload

tool = NeoFSDownload(endpoint="https://...")
file_path = tool._run(
    object_id="...",
    output_path="downloaded.pdf"
)
```

#### IPFSUpload
Upload to IPFS.

```python
from spoon_toolkits.storage import IPFSUpload

tool = IPFSUpload(api_url="https://ipfs.infura.io:5001")
cid = tool._run(file_path="image.png")
# Returns: IPFS CID
```

## Tool Selection Guide

### By Use Case

**Portfolio Management**:
- EVMGetBalance, EVMGetTokenBalance
- SolanaGetBalance, SolanaGetTokenBalance
- NeoGetBalance
- CoinGeckoPrice, CoinGeckoMarketData

**DeFi Trading**:
- EVMSwapTokens
- EVMGetGasPrice (for timing)
- CoinGeckoPrice (for price data)
- DeFiLlamaTVL (for protocol analysis)

**NFT Operations**:
- EVMGetTokenBalance (ERC-721/1155)
- EVMTokenTransfer
- IPFSUpload (for metadata)

**DAO Governance**:
- EVMCallContract (read proposals)
- EVMGetTransaction (verify votes)
- AddMemory (track decisions)

**Multi-Chain Agents**:
- EVM tools for Ethereum/Polygon/BSC
- Solana tools for Solana
- Neo tools for Neo N3

### By Chain

**Ethereum/EVM**: Use `spoon_toolkits.crypto.evm.*`
**Solana**: Use `spoon_toolkits.crypto.solana.*`
**Neo**: Use `spoon_toolkits.crypto.neo.*`

## Integration Example

```python
from spoon_ai_sdk.agents import SpoonReactAI
from spoon_ai_sdk.llm import LLMManager
from spoon_toolkits.crypto.evm import EVMGetBalance, EVMGetGasPrice
from spoon_toolkits.data import CoinGeckoPrice
from spoon_toolkits.memory import AddMemory, SearchMemory

# Initialize LLM
llm = LLMManager(provider="openai", model="gpt-4")

# Select tools for DeFi agent
tools = [
    EVMGetBalance(rpc_url=os.getenv("ETH_RPC_URL")),
    EVMGetGasPrice(rpc_url=os.getenv("ETH_RPC_URL")),
    CoinGeckoPrice(),
    AddMemory(),
    SearchMemory()
]

# Create agent
agent = SpoonReactAI(
    llm=llm,
    tools=tools,
    system_prompt="You are a DeFi assistant",
    max_iterations=5
)

# Use agent
response = agent.run("What's my ETH balance and current gas price?")
```

## Best Practices

### 1. Tool Selection
- Choose only tools needed for your use case
- Avoid loading all 50+ tools unnecessarily
- Group related tools together

### 2. Configuration
- Store API keys and private keys in environment variables
- Use separate keys for development and production
- Configure RPC URLs based on network (mainnet/testnet)

### 3. Error Handling
- Tools return error messages instead of raising exceptions
- Check tool output for "Error:" prefix
- Implement retry logic for network failures

### 4. Security
- Never log or expose private keys
- Use hardware wallets for production
- Validate addresses before transactions
- Set appropriate gas limits and slippage

### 5. Cost Management
- Monitor API usage (CoinGecko, ElevenLabs, etc.)
- Use caching for repeated queries
- Batch operations when possible

## Tool Comparison

| Category | Tools Count | Chains | API Keys Required |
|----------|-------------|--------|-------------------|
| EVM | 10+ | Ethereum, Polygon, BSC, etc. | RPC URL, Private Key (for writes) |
| Solana | 5+ | Solana | RPC URL, Private Key (for writes) |
| Neo | 4+ | Neo N3 | RPC URL, Private Key (for writes) |
| Data | 4+ | N/A | CoinGecko (optional), DeFiLlama (free) |
| Memory | 4 | N/A | None |
| Audio | 2 | N/A | ElevenLabs, OpenAI |
| Storage | 3+ | NeoFS, IPFS | Wallet keys |

## Next Steps

- **Learn Patterns**: Use `agent-patterns` skill to see how to combine tools effectively
- **Build Agents**: Use `blockchain-development` skill for complete DeFi/NFT/DAO examples
- **Custom Tools**: Extend BaseTool to create your own tools

## Additional Resources

For detailed tool documentation:
- `references/evm-tools.md` - Complete EVM tools reference
- `references/solana-tools.md` - Solana tools reference
- `references/data-tools.md` - Data platform tools reference
- `examples/` - Working examples for each tool category
