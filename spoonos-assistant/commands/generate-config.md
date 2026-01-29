---
name: generate-config
description: Generate configuration files (.env, config.json, .mcp.json)
trigger: /spoonos:generate-config
version: 0.1.0
---

# Generate Config Command

Generate configuration files for SpoonOS projects.

## Usage

```
/spoonos:generate-config [--type <config_type>] [--output-dir <directory>]
```

## Parameters

- `--type`: Config type: env, config, mcp, all (default: all)
- `--output-dir`: Output directory (default: current directory)

## Generated Files

### .env Template
```bash
# LLM API Keys
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Blockchain RPCs
ETHEREUM_RPC_URL=https://eth-mainnet.g.alchemy.com/v2/YOUR_KEY
POLYGON_RPC_URL=https://polygon-mainnet.g.alchemy.com/v2/YOUR_KEY
SOLANA_RPC_URL=https://api.mainnet-beta.solana.com
NEO_RPC_URL=https://mainnet1.neo.org:443

# Private Keys (NEVER COMMIT)
PRIVATE_KEY=0x...

# API Keys
COINGECKO_API_KEY=your_key
ELEVENLABS_API_KEY=your_key
```

### config.json Template
```json
{
  "llm": {
    "provider": "openai",
    "model": "gpt-4",
    "temperature": 0.7,
    "max_tokens": 2000
  },
  "agent": {
    "type": "react",
    "max_iterations": 5,
    "verbose": false
  },
  "tools": {
    "enabled": ["evm_balance", "coingecko_price"],
    "mcp_config": ".mcp.json"
  }
}
```

### .mcp.json Template
```json
{
  "mcpServers": {
    "blockchain-tools": {
      "command": "python",
      "args": ["-m", "my_mcp_servers.blockchain"],
      "env": {
        "ETHEREUM_RPC_URL": "${ETHEREUM_RPC_URL}"
      }
    }
  }
}
```
