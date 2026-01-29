---
name: scaffold-project
description: Create full project scaffolding with templates
trigger: /spoonos:scaffold-project
version: 0.1.0
---

# Scaffold Project Command

Create a complete SpoonOS project structure with templates.

## Usage

```
/spoonos:scaffold-project --name <project_name> [--template <template_type>]
```

## Parameters

- `--name`: Project name (required)
- `--template`: Template type: defi, nft, dao, chatbot (default: defi)
- `--output-dir`: Output directory (default: current directory)

## Templates

### DeFi Template
```
my-defi-project/
├── agents/
│   ├── portfolio_manager.py
│   └── trading_bot.py
├── tools/
│   └── custom_tools.py
├── config/
│   ├── .env.example
│   ├── config.json
│   └── .mcp.json
├── tests/
│   └── test_agents.py
├── requirements.txt
├── README.md
└── main.py
```

### NFT Template
```
my-nft-project/
├── agents/
│   ├── marketplace_monitor.py
│   └── minting_bot.py
├── tools/
│   └── nft_tools.py
├── config/
├── tests/
├── requirements.txt
└── main.py
```

### DAO Template
```
my-dao-project/
├── agents/
│   ├── governance_assistant.py
│   └── treasury_manager.py
├── tools/
│   └── dao_tools.py
├── config/
├── tests/
├── requirements.txt
└── main.py
```

## Example

```
/spoonos:scaffold-project --name my-defi-bot --template defi
```

Creates complete DeFi project with:
- Pre-configured agents
- Tool setup
- Configuration files
- Tests
- Documentation
