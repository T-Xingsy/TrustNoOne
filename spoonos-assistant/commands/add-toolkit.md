---
name: add-toolkit
description: Add spoon-toolkit tools to existing project
trigger: /spoonos:add-toolkit
version: 0.1.0
---

# Add Toolkit Command

Add tools from spoon-toolkit to an existing agent project.

## Usage

```
/spoonos:add-toolkit [--category <category>] [--tools <tool_list>] [--file <agent_file>]
```

## Parameters

- `--category`: Tool category: evm, solana, neo, data, memory, audio, storage
- `--tools`: Specific tools to add (comma-separated)
- `--file`: Agent file to modify (default: main.py)

## Examples

### Add EVM Tools
```
/spoonos:add-toolkit --category evm --file agents/my_agent.py
```

Adds:
```python
from spoon_toolkits.crypto.evm import (
    EVMGetBalance,
    EVMGetTokenBalance,
    EVMGetGasPrice,
    EVMTransfer
)

tools = [
    EVMGetBalance(rpc_url=os.getenv("ETHEREUM_RPC_URL")),
    EVMGetTokenBalance(rpc_url=os.getenv("ETHEREUM_RPC_URL")),
    EVMGetGasPrice(rpc_url=os.getenv("ETHEREUM_RPC_URL"))
]
```

### Add Specific Tools
```
/spoonos:add-toolkit --tools evm-balance,coingecko-price,add-memory
```

### Add Data Tools
```
/spoonos:add-toolkit --category data
```

Adds CoinGecko, DeFiLlama, and other data platform tools.
