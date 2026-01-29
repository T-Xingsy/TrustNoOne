---
name: init-starter
description: Copy examples from spoon-starter repository
trigger: /spoonos:init-starter
version: 0.1.0
---

# Init Starter Command

Copy example code from spoon-starter repository to your project.

## Usage

```
/spoonos:init-starter [--example <example_name>] [--output-dir <directory>]
```

## Parameters

- `--example`: Example name: chatbot, react, neofs, x402, all (default: all)
- `--output-dir`: Output directory (default: examples/)

## Available Examples

### streaming_chatbot.py
Simple streaming chatbot with conversation memory.

### x402_react_agent_demo.py
ReAct agent with x402 payment integration.

### neofs_agent_demo.py
Agent with NeoFS decentralized storage.

### mcp_integration_demo.py
Example of MCP server integration.

## Example

```
/spoonos:init-starter --example chatbot
```

Copies streaming_chatbot.py to examples/ directory.

```
/spoonos:init-starter --example all
```

Copies all examples from spoon-starter.

## Post-Copy Steps

1. Review copied examples
2. Install dependencies: `pip install -r requirements.txt`
3. Configure .env file
4. Customize for your needs
5. Run examples to verify setup
