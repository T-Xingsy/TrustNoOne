---
name: SpoonOS Ecosystem Understanding
description: This skill should be used when the user asks about "SpoonOS ecosystem", "difference between spoon-core and spoon-toolkit", "which SpoonOS library to use", "spoon-starter vs spoon-core", "how to choose SpoonOS components", "SpoonOS architecture", or needs guidance on selecting the right library for their AI agent project.
version: 0.1.0
---

# SpoonOS Ecosystem Understanding

## Overview

SpoonOS provides a three-tier architecture for building AI agents in Web3 environments. Understanding the relationship and purpose of each library enables effective development decisions.

**Three Core Libraries:**
- **spoon-core**: Framework foundation layer
- **spoon-toolkit**: Professional tools collection
- **spoon-starter**: Quick-start templates and examples

## Architecture Layers

### Layer 1: spoon-core (Framework Foundation)

**Package**: `spoon-ai-sdk` v0.3.6

**Purpose**: Provides the core infrastructure for building AI agents.

**Core Components**:
- Agent system (BaseAgent, ToolCallAgent, SpoonReactAI, SpoonReactMCP)
- LLM management (ChatBot, LLMManager, ConfigurationManager)
- Tool system (BaseTool, ToolManager, MCPTool)
- Graph workflows (StateGraph for multi-step orchestration)
- MCP protocol support (dynamic tool discovery)
- Identity system (ERC-8004 DID integration)

**Use when**:
- Building custom agent architectures
- Implementing new agent patterns
- Creating framework-level abstractions
- Developing core infrastructure

### Layer 2: spoon-toolkit (Professional Tools)

**Package**: `spoon-toolkits` v0.2.5

**Purpose**: Provides 50+ production-ready tools for blockchain and AI operations.

**Tool Categories**:
- **Blockchain**: EVM tools, Solana tools, Neo tools
- **Memory**: Add/search/delete memory operations
- **Audio**: Speech-to-text, text-to-speech
- **Storage**: IPFS, Arweave integration
- **DeFi**: Token swaps, balance queries, transaction monitoring
- **NFT**: Minting, metadata management, marketplace integration

**Use when**:
- Need pre-built blockchain functionality
- Require professional-grade tools
- Want to avoid reimplementing common operations
- Building production applications quickly

### Layer 3: spoon-starter (Templates & Examples)

**Package**: `spoon-starter` v0.1.0

**Purpose**: Provides working examples and project templates.

**Contents**:
- Complete agent examples (ChatBot, ToolCall, ReAct, Graph patterns)
- Configuration templates (.env, config.json)
- Best practice demonstrations
- Integration examples (MCP, blockchain, DID)

**Use when**:
- Starting a new project
- Learning SpoonOS patterns
- Need reference implementations
- Want to copy proven structures

## Dependency Relationships

```
spoon-starter
    ├── depends on: spoon-core
    └── depends on: spoon-toolkit

spoon-toolkit
    └── depends on: spoon-core

spoon-core
    └── standalone (no SpoonOS dependencies)
```

**Key insight**: spoon-starter demonstrates how to use both core and toolkit together.

## Library Comparison

| Aspect | spoon-core | spoon-toolkit | spoon-starter |
|--------|------------|---------------|---------------|
| **Purpose** | Framework infrastructure | Ready-to-use tools | Templates & examples |
| **Abstraction** | Low-level APIs | High-level tools | Complete applications |
| **Flexibility** | Maximum | Moderate | Minimal (copy & adapt) |
| **Learning Curve** | Steep | Moderate | Gentle |
| **Use Case** | Custom frameworks | Production apps | Quick starts |
| **Code Volume** | Write more | Write less | Copy & modify |
| **Dependencies** | None (within SpoonOS) | Requires core | Requires both |

## Selection Guide

### Choose spoon-core when:
- Building custom agent architectures
- Need maximum flexibility and control
- Implementing novel agent patterns
- Creating reusable abstractions
- Developing framework extensions

**Example scenarios**:
- "I need an agent with custom reasoning logic"
- "I want to implement a new agent pattern"
- "I need fine-grained control over LLM interactions"

### Choose spoon-toolkit when:
- Building production applications
- Need blockchain functionality quickly
- Want battle-tested tools
- Require professional-grade features
- Focus on business logic, not infrastructure

**Example scenarios**:
- "I need to query EVM balances and execute swaps"
- "I want to add memory capabilities to my agent"
- "I need NFT minting functionality"

### Choose spoon-starter when:
- Starting a new project
- Learning SpoonOS development
- Need working reference code
- Want proven project structures
- Prefer copying over building from scratch

**Example scenarios**:
- "Show me a complete ReAct agent example"
- "I need a project template for a DeFi agent"
- "How do I structure my configuration files?"

## Development Workflow

### Recommended Approach

**For beginners**:
1. Start with spoon-starter examples
2. Copy relevant template to your project
3. Modify configuration and business logic
4. Add toolkit tools as needed
5. Gradually learn core APIs for customization

**For experienced developers**:
1. Review spoon-starter for patterns
2. Use spoon-toolkit for common operations
3. Use spoon-core for custom logic
4. Combine all three as needed

**For framework developers**:
1. Focus on spoon-core APIs
2. Reference toolkit implementations
3. Contribute back to ecosystem

### Typical Project Structure

```python
# Import from all three layers
from spoon_ai.agents import SpoonReactAI  # core
from spoon_ai.chat import ChatBot  # core
from spoon_toolkits.evm import EVMBalanceTool  # toolkit
# Copy configuration patterns from starter

# Combine in your application
agent = SpoonReactAI(
    llm=ChatBot(llm_provider="openai"),
    available_tools=ToolManager([
        EVMBalanceTool(),  # From toolkit
        MyCustomTool()  # Your own tool using core
    ])
)
```

## Common Patterns

### Pattern 1: Pure Core Development
Use only spoon-core for maximum control.

**When**: Custom agent architectures, novel patterns
**Complexity**: High
**Flexibility**: Maximum

### Pattern 2: Core + Toolkit (Recommended)
Use core for agent structure, toolkit for functionality.

**When**: Production applications, balanced approach
**Complexity**: Moderate
**Flexibility**: High

### Pattern 3: Starter-Based Development
Copy from starter, modify as needed.

**When**: Quick prototypes, learning, standard use cases
**Complexity**: Low
**Flexibility**: Moderate

## Integration Points

### How Libraries Work Together

**spoon-core provides**:
- Agent base classes
- Tool interfaces
- LLM abstractions
- Graph workflow system

**spoon-toolkit extends**:
- Implements BaseTool for blockchain operations
- Uses core's ToolManager
- Follows core's tool schema

**spoon-starter demonstrates**:
- How to instantiate core agents
- How to integrate toolkit tools
- How to configure everything together

## Version Compatibility

**Current versions**:
- spoon-core: 0.3.6 (spoon-ai-sdk)
- spoon-toolkit: 0.2.5 (spoon-toolkits)
- spoon-starter: 0.1.0

**Compatibility**: All three libraries are designed to work together. Use matching or compatible versions.

## Additional Resources

### Reference Files

For detailed information, consult:
- **`references/detailed-comparison.md`** - In-depth library comparison with code examples
- **`references/best-practices.md`** - Development best practices and patterns
- **`references/migration-guide.md`** - Upgrading between versions

### Example Files

Working examples in `examples/`:
- **`simple-chatbot.py`** - Minimal core-only example
- **`toolkit-integration.py`** - Core + toolkit example
- **`starter-template/`** - Complete project structure from starter

## Quick Decision Tree

```
Need to build an AI agent?
├─ Learning SpoonOS? → Use spoon-starter
├─ Standard use case? → Use spoon-starter + spoon-toolkit
├─ Production app? → Use spoon-core + spoon-toolkit
└─ Custom framework? → Use spoon-core only
```

## Summary

**Remember**:
- spoon-core = Foundation (always needed)
- spoon-toolkit = Tools (use for productivity)
- spoon-starter = Templates (use for learning/quick starts)

**Most projects use**: spoon-core + spoon-toolkit
**Beginners start with**: spoon-starter
**Advanced developers focus on**: spoon-core

Choose based on project needs, experience level, and desired flexibility.
