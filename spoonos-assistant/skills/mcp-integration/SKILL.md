---
name: SpoonOS MCP Integration
description: This skill should be used when the user asks about "MCP configuration", "Model Context Protocol", "how to use MCP servers", ".mcp.json setup", "dynamic tool discovery", "MCP server development", "integrating external tools", or needs guidance on configuring and using MCP with SpoonOS agents.
version: 0.1.0
---

# SpoonOS MCP Integration Guide

Learn how to configure and use Model Context Protocol (MCP) servers with SpoonOS for dynamic tool discovery and integration.

## What is MCP?

Model Context Protocol (MCP) is a standardized protocol for:
- Dynamic tool discovery
- External tool integration
- Standardized tool interfaces
- Tool sharing across applications

## Benefits of MCP

1. **Dynamic Loading**: Tools are discovered at runtime
2. **Modularity**: Add/remove tools without code changes
3. **Standardization**: Consistent tool interface
4. **Sharing**: Reuse tools across projects
5. **Flexibility**: Easy integration with external services

## MCP Configuration

### .mcp.json File

Create `.mcp.json` in your project root:

```json
{
  "mcpServers": {
    "blockchain-tools": {
      "command": "python",
      "args": ["-m", "my_mcp_servers.blockchain"],
      "env": {
        "ETHEREUM_RPC_URL": "${ETHEREUM_RPC_URL}",
        "API_KEY": "${API_KEY}"
      }
    },
    "data-tools": {
      "command": "python",
      "args": ["-m", "my_mcp_servers.data"],
      "env": {
        "COINGECKO_API_KEY": "${COINGECKO_API_KEY}"
      }
    }
  }
}
```

### Configuration Fields

- **command**: Executable to run (python, node, etc.)
- **args**: Command arguments
- **env**: Environment variables (use ${VAR} for substitution)

## Using MCP with SpoonOS

### Basic Usage

```python
from spoon_ai_sdk.agents import ToolCallAgent
from spoon_ai_sdk.llm import LLMManager
from spoon_ai_sdk.tools import MCPTool

# Initialize LLM
llm = LLMManager(provider="openai", model="gpt-4")

# Load MCP tools
mcp_tool = MCPTool(
    server_name="blockchain-tools",
    config_path=".mcp.json"
)

# Create agent with MCP tools
agent = ToolCallAgent(
    llm=llm,
    tools=[mcp_tool],
    system_prompt="You are a blockchain assistant"
)

# Use agent
response = agent.run("What's the ETH balance of 0x...?")
```

### Multiple MCP Servers

```python
# Load tools from multiple servers
blockchain_tools = MCPTool(server_name="blockchain-tools", config_path=".mcp.json")
data_tools = MCPTool(server_name="data-tools", config_path=".mcp.json")

# Combine with regular tools
from spoon_toolkits.memory import AddMemory

agent = SpoonReactAI(
    llm=llm,
    tools=[blockchain_tools, data_tools, AddMemory()],
    max_iterations=5
)
```

## Creating MCP Servers

### Server Structure

```python
# my_mcp_servers/blockchain.py

from spoon_ai_sdk.mcp import MCPServer, MCPTool
from pydantic import BaseModel, Field

class BalanceInput(BaseModel):
    address: str = Field(..., description="Ethereum address")

class BalanceTool(MCPTool):
    name: str = "get_eth_balance"
    description: str = "Get ETH balance for an address"
    args_schema: type[BaseModel] = BalanceInput

    def _run(self, address: str) -> str:
        # Implementation
        return f"Balance: 1.5 ETH"

# Create server
server = MCPServer(name="blockchain-tools")
server.add_tool(BalanceTool())

if __name__ == "__main__":
    server.run()
```

### Server Best Practices

1. **Clear Tool Names**: Use descriptive, action-oriented names
2. **Detailed Descriptions**: Help LLM understand when to use tools
3. **Type Safety**: Use Pydantic for input validation
4. **Error Handling**: Return error messages, don't raise exceptions
5. **Documentation**: Include examples in descriptions

## MCP vs Static Tools

| Aspect | MCP Tools | Static Tools |
|--------|-----------|--------------|
| **Loading** | Runtime | Compile-time |
| **Configuration** | .mcp.json | Code |
| **Flexibility** | High | Medium |
| **Sharing** | Easy | Requires packaging |
| **Debugging** | Harder | Easier |
| **Performance** | Slight overhead | Direct |

## When to Use MCP

### Use MCP When:
- Tools change frequently
- Multiple projects share tools
- External services integration
- Plugin architecture needed
- Dynamic tool discovery required

### Use Static Tools When:
- Tools are stable
- Single project
- Performance critical
- Simpler debugging needed
- Tight integration required

## Common MCP Patterns

### Pattern 1: Blockchain MCP Server
```json
{
  "mcpServers": {
    "blockchain": {
      "command": "python",
      "args": ["-m", "blockchain_mcp"],
      "env": {
        "ETH_RPC": "${ETHEREUM_RPC_URL}",
        "SOL_RPC": "${SOLANA_RPC_URL}"
      }
    }
  }
}
```

### Pattern 2: Data Platform MCP Server
```json
{
  "mcpServers": {
    "data": {
      "command": "python",
      "args": ["-m", "data_mcp"],
      "env": {
        "COINGECKO_KEY": "${COINGECKO_API_KEY}",
        "DEFILLAMA_KEY": "${DEFILLAMA_API_KEY}"
      }
    }
  }
}
```

### Pattern 3: Custom Business Logic
```json
{
  "mcpServers": {
    "business": {
      "command": "python",
      "args": ["-m", "my_company.mcp_server"],
      "env": {
        "DATABASE_URL": "${DATABASE_URL}",
        "API_KEY": "${COMPANY_API_KEY}"
      }
    }
  }
}
```

## Environment Variables

### .env File
```bash
# Blockchain RPCs
ETHEREUM_RPC_URL=https://eth-mainnet.g.alchemy.com/v2/YOUR_KEY
SOLANA_RPC_URL=https://api.mainnet-beta.solana.com

# API Keys
COINGECKO_API_KEY=your_key
DEFILLAMA_API_KEY=your_key

# Private Keys (for write operations)
PRIVATE_KEY=0x...
```

### Loading Environment Variables
```python
from dotenv import load_dotenv
import os

load_dotenv()

# Variables are automatically substituted in .mcp.json
```

## Debugging MCP

### Enable Verbose Logging
```python
import logging

logging.basicConfig(level=logging.DEBUG)

mcp_tool = MCPTool(
    server_name="blockchain-tools",
    config_path=".mcp.json",
    verbose=True
)
```

### Test MCP Server Directly
```bash
# Run server standalone
python -m my_mcp_servers.blockchain

# Test with curl
curl -X POST http://localhost:8000/tools
```

### Common Issues

**Issue 1: Server Not Starting**
- Check command and args in .mcp.json
- Verify Python module exists
- Check environment variables

**Issue 2: Tools Not Discovered**
- Verify server is running
- Check tool registration
- Review server logs

**Issue 3: Environment Variables Not Substituted**
- Ensure .env file exists
- Check variable names match
- Use ${VAR} syntax in .mcp.json

## Advanced MCP Features

### Tool Categories
```python
server = MCPServer(name="blockchain-tools")

# Add tools with categories
server.add_tool(EVMBalanceTool(), category="evm")
server.add_tool(SolanaBalanceTool(), category="solana")

# Filter by category
evm_tools = server.get_tools(category="evm")
```

### Tool Versioning
```python
class BalanceTool(MCPTool):
    name: str = "get_balance"
    version: str = "1.0.0"
    description: str = "Get balance (v1.0.0)"
```

### Tool Dependencies
```python
class SwapTool(MCPTool):
    name: str = "swap_tokens"
    dependencies: list[str] = ["get_balance", "get_gas_price"]
```

## MCP Server Examples

### Example 1: Simple MCP Server
```python
from spoon_ai_sdk.mcp import MCPServer, MCPTool

server = MCPServer(name="simple-tools")

@server.tool(name="hello", description="Say hello")
def hello_tool(name: str) -> str:
    return f"Hello, {name}!"

server.run()
```

### Example 2: Blockchain MCP Server
```python
from spoon_ai_sdk.mcp import MCPServer
from web3 import Web3

server = MCPServer(name="blockchain")

@server.tool(name="get_balance", description="Get ETH balance")
def get_balance(address: str) -> str:
    w3 = Web3(Web3.HTTPProvider(os.getenv("ETH_RPC")))
    balance = w3.eth.get_balance(address)
    return f"{w3.from_wei(balance, 'ether')} ETH"

server.run()
```

## Integration with SpoonOS Agents

### With ToolCallAgent
```python
mcp_tools = MCPTool(server_name="blockchain", config_path=".mcp.json")
agent = ToolCallAgent(llm=llm, tools=[mcp_tools])
```

### With SpoonReactAI
```python
mcp_tools = MCPTool(server_name="blockchain", config_path=".mcp.json")
agent = SpoonReactAI(llm=llm, tools=[mcp_tools], max_iterations=5)
```

### With StateGraph
```python
mcp_tools = MCPTool(server_name="blockchain", config_path=".mcp.json")

def node_with_mcp(state):
    agent = ToolCallAgent(llm=llm, tools=[mcp_tools])
    result = agent.run(state["input"])
    return {"output": result}

graph.add_node("mcp_node", node_with_mcp)
```

## Best Practices

1. **Organize by Domain**: Group related tools in same server
2. **Clear Naming**: Use descriptive server and tool names
3. **Environment Variables**: Never hardcode secrets
4. **Error Handling**: Return informative error messages
5. **Documentation**: Document each tool thoroughly
6. **Testing**: Test servers independently
7. **Versioning**: Version your MCP servers
8. **Monitoring**: Log tool usage and errors

## Next Steps

- **Build Agents**: Use `agent-patterns` skill to combine MCP with agent patterns
- **Explore Tools**: Use `toolkit-tools` skill to see available tools
- **Build Applications**: Use `blockchain-development` skill for complete examples

## Additional Resources

- `references/mcp-protocol.md` - MCP protocol specification
- `references/server-development.md` - MCP server development guide
- `examples/` - Working MCP server examples
