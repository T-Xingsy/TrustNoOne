# SpoonOS Assistant

A comprehensive Claude Code plugin for SpoonOS development that helps you understand the ecosystem, generate code, and build AI agents.

## Overview

SpoonOS Assistant provides intelligent support for working with the SpoonOS ecosystem:
- **spoon-core**: Core AI agent framework
- **spoon-toolkit**: Professional blockchain and crypto tools (50+ tools)
- **spoon-starter**: Quick-start templates and examples

## Features

### 🧠 Knowledge Skills (6)
- **spoonos-ecosystem**: Understand the three-library architecture and choose the right tools
- **core-framework**: Master Agent APIs, LLM management, and tool systems
- **toolkit-tools**: Explore 50+ blockchain tools (EVM, Solana, Neo, etc.)
- **agent-patterns**: Learn 4 agent design patterns (ChatBot, ToolCall, ReAct, Graph)
- **mcp-integration**: Configure MCP servers and dynamic tool discovery
- **blockchain-development**: Build DeFi, NFT, and DAO agents with security best practices

### ⚡ Code Generation Commands (7)
- `/spoonos:create-agent`: Generate complete Agent code
- `/spoonos:create-tool`: Create custom BaseTool implementations
- `/spoonos:generate-config`: Generate .env, config.json, .mcp.json templates
- `/spoonos:scaffold-project`: Create full project scaffolding (DeFi, NFT, DAO templates)
- `/spoonos:add-toolkit`: Add spoon-toolkit tools to existing projects
- `/spoonos:create-workflow`: Generate StateGraph workflow code
- `/spoonos:init-starter`: Copy examples from spoon-starter

### 🤖 Intelligent Agents (4)
- **spoonos-architect**: Analyzes requirements and recommends architecture
- **code-generator**: Generates complete, production-ready code
- **toolkit-advisor**: Recommends the best tools from spoon-toolkit
- **config-validator**: Validates configurations and suggests fixes

## Installation

### Option 1: Local Development
```bash
# Clone or copy the plugin to your project
cp -r spoonos-assistant ~/.claude/plugins/

# Or use it directly in your project
cc --plugin-dir ./spoonos-assistant
```

### Option 2: Project-Specific
```bash
# Copy to your project's .claude-plugin directory
mkdir -p .claude-plugin
cp -r spoonos-assistant .claude-plugin/
```

## Quick Start

### 1. Understand the Ecosystem
Ask Claude about SpoonOS:
```
"Explain the difference between spoon-core, spoon-toolkit, and spoon-starter"
"Which library should I use for building a DeFi agent?"
```

### 2. Generate Code
Use commands to quickly generate code:
```
/spoonos:create-agent --name trading-agent --type react --tools evm-balance,evm-swap
/spoonos:scaffold-project --name my-defi-bot --template defi
```

### 3. Get Architecture Advice
Describe your needs and let the architect agent help:
```
"I want to build an agent that monitors NFT prices and sends alerts"
"How do I create a DAO governance agent with voting capabilities?"
```

## Usage Examples

### Example 1: Create a Simple Chatbot
```
/spoonos:create-agent --name my-chatbot --type chatbot
```

### Example 2: Build a Blockchain Query Agent
```
/spoonos:create-agent --name neo-agent --type toolcall --tools neo-block-count,neo-balance
```

### Example 3: Scaffold a DeFi Project
```
/spoonos:scaffold-project --name defi-trader --template defi
```

### Example 4: Add Memory Tools
```
/spoonos:add-toolkit --category memory --tools add-memory,search-memory
```

## Configuration

Create `.claude/spoonos-assistant.local.md` to customize behavior:

```markdown
# SpoonOS Assistant Configuration

## Default Settings
- Default LLM Provider: openai
- Default Agent Type: react
- Code Style: detailed (with comments)
- Auto-generate tests: false
- Auto-generate docs: true

## Code Paths
- spoon-core path: /path/to/spoon-core
- spoon-toolkit path: /path/to/spoon-toolkit
- spoon-starter path: /path/to/spoon-starter
```

## Components

### Skills
Located in `skills/` directory:
- `spoonos-ecosystem/`: Ecosystem overview and library comparison
- `core-framework/`: Core framework APIs and patterns
- `toolkit-tools/`: Toolkit tools catalog and usage
- `agent-patterns/`: Agent design patterns and best practices
- `mcp-integration/`: MCP configuration and server development
- `blockchain-development/`: Blockchain agent development guide

### Commands
Located in `commands/` directory:
- `create-agent.md`: Agent code generation
- `create-tool.md`: Custom tool generation
- `generate-config.md`: Configuration file generation
- `scaffold-project.md`: Project scaffolding
- `add-toolkit.md`: Add toolkit tools
- `create-workflow.md`: Workflow generation
- `init-starter.md`: Copy starter examples

### Agents
Located in `agents/` directory:
- `spoonos-architect.md`: Architecture design and recommendations
- `code-generator.md`: Intelligent code generation
- `toolkit-advisor.md`: Tool selection and recommendations
- `config-validator.md`: Configuration validation

## Development

### Project Structure
```
spoonos-assistant/
├── .claude-plugin/
│   └── plugin.json          # Plugin manifest
├── skills/                   # Knowledge skills
│   ├── spoonos-ecosystem/
│   ├── core-framework/
│   ├── toolkit-tools/
│   ├── agent-patterns/
│   ├── mcp-integration/
│   └── blockchain-development/
├── commands/                 # Code generation commands
│   ├── create-agent.md
│   ├── create-tool.md
│   ├── generate-config.md
│   ├── scaffold-project.md
│   ├── add-toolkit.md
│   ├── create-workflow.md
│   └── init-starter.md
├── agents/                   # Intelligent agents
│   ├── spoonos-architect.md
│   ├── code-generator.md
│   ├── toolkit-advisor.md
│   └── config-validator.md
├── scripts/                  # Helper scripts
└── README.md
```

## Contributing

Contributions are welcome! Please:
1. Follow the existing code style
2. Add tests for new features
3. Update documentation
4. Submit pull requests

## License

MIT License - see LICENSE file for details

## Support

- GitHub Issues: [Report bugs or request features]
- Documentation: [Link to docs]
- Community: [Link to community]

## Changelog

### v0.1.0 (Initial Release)
- 6 knowledge skills covering the entire SpoonOS ecosystem
- 7 code generation commands for rapid development
- 4 intelligent agents for architecture, code generation, and validation
- Comprehensive documentation and examples
