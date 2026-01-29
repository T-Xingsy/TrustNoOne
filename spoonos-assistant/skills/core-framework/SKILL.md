---
name: SpoonOS Core Framework
description: This skill should be used when the user asks about "spoon-core APIs", "Agent classes", "LLMManager usage", "tool system", "how to create agents", "BaseAgent", "ToolCallAgent", "SpoonReactAI", "StateGraph workflows", or needs detailed information about the core framework's architecture, classes, and methods.
version: 0.1.0
---

# SpoonOS Core Framework Guide

Master the spoon-core framework APIs, agent architectures, LLM management, and tool systems for building custom AI agents.

## Framework Overview

spoon-core (package: `spoon-ai-sdk`) provides the foundational infrastructure for building AI agents. It offers:

- **Agent System**: Multiple agent patterns for different use cases
- **LLM Management**: Multi-provider LLM integration and configuration
- **Tool System**: Dynamic tool discovery, registration, and execution
- **Graph Workflows**: Complex multi-step agent orchestration
- **Identity & Security**: ERC-8004 DID integration, x402 payments
- **Memory Management**: Conversation history and context handling

## Core Modules

### 1. Agent System (`spoon_ai_sdk.agents`)

The agent system provides four main agent types, each suited for different scenarios.

#### BaseAgent

**Purpose**: Abstract base class for all agents

**Key Methods**:
```python
class BaseAgent:
    def run(self, input: str) -> str:
        """Execute agent with input, return response"""

    async def arun(self, input: str) -> str:
        """Async version of run"""

    def reset(self):
        """Reset agent state"""
```

**When to extend**: Create custom agent patterns not covered by built-in types

#### ChatBot

**Purpose**: Simple conversational agent without tools

**Use Cases**:
- Customer support chatbots
- General Q&A systems
- Conversational interfaces
- Content generation

**API**:
```python
from spoon_ai_sdk.agents import ChatBot
from spoon_ai_sdk.llm import LLMManager

llm = LLMManager(provider="openai", model="gpt-4")

agent = ChatBot(
    llm=llm,
    system_prompt="You are a helpful assistant",
    memory=True,  # Enable conversation history
    max_history=10  # Keep last 10 messages
)

response = agent.run("Hello!")
```

**Key Parameters**:
- `llm`: LLMManager instance
- `system_prompt`: System instructions for the agent
- `memory`: Enable/disable conversation history
- `max_history`: Maximum messages to retain

#### ToolCallAgent

**Purpose**: Single-turn tool execution based on user input

**Use Cases**:
- Simple tool-based queries
- Single-action commands
- Quick data retrieval
- Stateless operations

**API**:
```python
from spoon_ai_sdk.agents import ToolCallAgent
from spoon_ai_sdk.tools import ToolManager

tools = [tool1, tool2, tool3]
tool_manager = ToolManager(tools=tools)

agent = ToolCallAgent(
    llm=llm,
    tools=tool_manager.get_tools(),
    system_prompt="You are a blockchain query assistant"
)

response = agent.run("What's the balance of 0x...")
```

**Key Features**:
- Analyzes user input
- Selects appropriate tool(s)
- Executes tool(s) once
- Returns formatted response

**Limitations**: No multi-step reasoning, single tool execution cycle

#### SpoonReactAI

**Purpose**: Multi-step reasoning agent with iterative tool use

**Use Cases**:
- Complex problem solving
- Multi-step workflows
- Research and analysis
- Decision-making tasks

**API**:
```python
from spoon_ai_sdk.agents import SpoonReactAI

agent = SpoonReactAI(
    llm=llm,
    tools=tools,
    system_prompt="You are a DeFi analyst",
    max_iterations=5,  # Maximum reasoning steps
    verbose=True,  # Show reasoning process
    early_stopping=True  # Stop when answer found
)

response = agent.run("Analyze the best time to swap ETH to USDC")
```

**ReAct Pattern**:
1. **Reason**: Analyze the problem, decide next action
2. **Act**: Execute selected tool
3. **Observe**: Process tool output
4. **Repeat**: Continue until answer found or max iterations reached

**Key Parameters**:
- `max_iterations`: Maximum reasoning cycles (default: 5)
- `verbose`: Show intermediate reasoning steps
- `early_stopping`: Stop when final answer is reached

**Best Practices**:
- Set appropriate `max_iterations` based on task complexity
- Use `verbose=True` during development for debugging
- Provide clear system prompts with reasoning guidelines

#### StateGraph

**Purpose**: Complex multi-agent workflows with conditional routing

**Use Cases**:
- Multi-stage pipelines
- Conditional workflows
- Agent collaboration
- Complex orchestration

**API**:
```python
from spoon_ai_sdk.graph import StateGraph
from typing import TypedDict

# Define state schema
class AgentState(TypedDict):
    input: str
    analysis: str
    decision: str
    output: str

# Create graph
graph = StateGraph(state_schema=AgentState)

# Add nodes (agents or functions)
graph.add_node("analyze", analyze_agent)
graph.add_node("decide", decision_agent)
graph.add_node("execute", execution_agent)

# Add edges
graph.add_edge("analyze", "decide")

# Add conditional edges
def should_execute(state):
    return "execute" if state["decision"] == "proceed" else "end"

graph.add_conditional_edges("decide", should_execute)

# Set entry and end points
graph.set_entry_point("analyze")
graph.set_finish_point("end")

# Compile and run
app = graph.compile()
result = app.invoke({"input": "user query"})
```

**Key Concepts**:
- **Nodes**: Individual agents or processing functions
- **Edges**: Fixed transitions between nodes
- **Conditional Edges**: Dynamic routing based on state
- **State**: Shared data structure passed between nodes

**Advanced Features**:
- Parallel execution of independent nodes
- Checkpointing for long-running workflows
- Error handling and retry logic
- Sub-graphs for modular design

### 2. LLM Management (`spoon_ai_sdk.llm`)

#### LLMManager

**Purpose**: Unified interface for multiple LLM providers

**Supported Providers**:
- OpenAI (GPT-3.5, GPT-4, GPT-4-turbo)
- Anthropic (Claude 2, Claude 3)
- Ollama (Local models)
- Azure OpenAI
- Custom providers

**API**:
```python
from spoon_ai_sdk.llm import LLMManager

# OpenAI
llm = LLMManager(
    provider="openai",
    model="gpt-4",
    api_key="sk-...",  # Or from env: OPENAI_API_KEY
    temperature=0.7,
    max_tokens=2000,
    top_p=1.0
)

# Anthropic
llm = LLMManager(
    provider="anthropic",
    model="claude-3-opus-20240229",
    api_key="sk-ant-...",  # Or from env: ANTHROPIC_API_KEY
    temperature=0.7,
    max_tokens=4000
)

# Ollama (local)
llm = LLMManager(
    provider="ollama",
    model="llama2",
    base_url="http://localhost:11434"
)

# Generate response
response = llm.generate("What is blockchain?")

# Async generation
response = await llm.agenerate("What is blockchain?")
```

**Key Parameters**:
- `provider`: LLM provider name
- `model`: Specific model identifier
- `api_key`: API key (or use environment variables)
- `temperature`: Randomness (0.0-1.0)
- `max_tokens`: Maximum response length
- `top_p`: Nucleus sampling parameter

**Configuration Management**:
```python
from spoon_ai_sdk.llm import ConfigurationManager

# Load from config file
config = ConfigurationManager.load_config("config.json")
llm = LLMManager(**config["llm"])
```

**Best Practices**:
- Store API keys in environment variables
- Use cheaper models for development (gpt-3.5-turbo)
- Use powerful models for production (gpt-4, claude-3-opus)
- Set appropriate `max_tokens` to control costs
- Implement retry logic for API failures

### 3. Tool System (`spoon_ai_sdk.tools`)

#### BaseTool

**Purpose**: Abstract base class for all tools

**API**:
```python
from spoon_ai_sdk.tools import BaseTool
from pydantic import BaseModel, Field

class MyToolInput(BaseModel):
    """Input schema using Pydantic"""
    param1: str = Field(..., description="Description of param1")
    param2: int = Field(default=10, description="Optional param2")

class MyTool(BaseTool):
    name: str = "my_tool"
    description: str = "Clear description of what this tool does"
    args_schema: type[BaseModel] = MyToolInput

    def _run(self, param1: str, param2: int = 10) -> str:
        """Synchronous execution"""
        # Tool logic here
        return f"Result: {param1}, {param2}"

    async def _arun(self, param1: str, param2: int = 10) -> str:
        """Asynchronous execution"""
        # Async tool logic here
        return f"Result: {param1}, {param2}"
```

**Key Components**:
- `name`: Unique tool identifier
- `description`: Clear explanation for LLM to understand when to use
- `args_schema`: Pydantic model defining input parameters
- `_run()`: Synchronous execution method
- `_arun()`: Asynchronous execution method (optional)

**Tool Design Guidelines**:
1. **Clear naming**: Use descriptive, action-oriented names
2. **Detailed descriptions**: Help LLM understand when to use the tool
3. **Type safety**: Use Pydantic for input validation
4. **Error handling**: Return error messages, don't raise exceptions
5. **Documentation**: Include examples in description

#### ToolManager

**Purpose**: Manage and organize multiple tools

**API**:
```python
from spoon_ai_sdk.tools import ToolManager

# Create tool manager
tools = [tool1, tool2, tool3]
manager = ToolManager(tools=tools)

# Get all tools
all_tools = manager.get_tools()

# Get tool by name
specific_tool = manager.get_tool("tool_name")

# Add tool dynamically
manager.add_tool(new_tool)

# Remove tool
manager.remove_tool("tool_name")

# Get tool schemas (for LLM)
schemas = manager.get_tool_schemas()
```

**Features**:
- Tool registration and discovery
- Name-based tool lookup
- Schema generation for LLM
- Dynamic tool addition/removal

#### MCPTool

**Purpose**: Integrate MCP (Model Context Protocol) tools

**API**:
```python
from spoon_ai_sdk.tools import MCPTool

# Load tools from MCP server
mcp_tool = MCPTool(
    server_name="my-mcp-server",
    config_path=".mcp.json"
)

# Use with agent
agent = ToolCallAgent(
    llm=llm,
    tools=[mcp_tool]
)
```

**MCP Configuration** (`.mcp.json`):
```json
{
  "mcpServers": {
    "my-mcp-server": {
      "command": "python",
      "args": ["-m", "my_mcp_server"],
      "env": {
        "API_KEY": "${API_KEY}"
      }
    }
  }
}
```

**Benefits**:
- Dynamic tool discovery
- External tool integration
- Standardized tool protocol
- Easy tool sharing

### 4. Identity & Security

#### ERC-8004 DID Integration

**Purpose**: Decentralized identity for agents

**API**:
```python
from spoon_ai_sdk.identity import DIDManager

# Create DID
did_manager = DIDManager()
did = did_manager.create_did()

# Get DID document
did_document = did_manager.get_did_document(did)

# Sign with DID
signature = did_manager.sign(did, message)

# Verify signature
is_valid = did_manager.verify(did, message, signature)
```

**Use Cases**:
- Agent authentication
- Verifiable credentials
- Reputation systems
- Trust networks

#### x402 Payment Protocol

**Purpose**: Micropayments for agent services

**API**:
```python
from spoon_ai_sdk.payments import X402Payment

# Initialize payment handler
payment = X402Payment(
    private_key=os.getenv("PRIVATE_KEY"),
    rpc_url=os.getenv("RPC_URL")
)

# Create payment request
payment_request = payment.create_request(
    amount=0.001,  # ETH
    recipient="0x...",
    metadata={"service": "agent_query"}
)

# Process payment
tx_hash = payment.process(payment_request)
```

### 5. Memory Management

#### Conversation Memory

**API**:
```python
from spoon_ai_sdk.memory import ConversationMemory

# Create memory
memory = ConversationMemory(
    max_messages=20,  # Keep last 20 messages
    summarize=True  # Summarize old messages
)

# Add messages
memory.add_message("user", "Hello")
memory.add_message("assistant", "Hi there!")

# Get history
history = memory.get_history()

# Clear memory
memory.clear()
```

#### Vector Memory

**API**:
```python
from spoon_ai_sdk.memory import VectorMemory

# Create vector memory
memory = VectorMemory(
    embedding_model="text-embedding-ada-002",
    dimension=1536
)

# Add memories
memory.add("User prefers DeFi over NFTs")
memory.add("User's main wallet: 0x...")

# Search memories
relevant = memory.search("What does user like?", top_k=3)
```

## Common Patterns

### Pattern 1: Simple Chatbot
```python
llm = LLMManager(provider="openai", model="gpt-4")
agent = ChatBot(llm=llm, system_prompt="You are helpful")
response = agent.run("Hello")
```

### Pattern 2: Tool-Using Agent
```python
tools = [Tool1(), Tool2()]
agent = ToolCallAgent(llm=llm, tools=tools)
response = agent.run("Use tool1 with param X")
```

### Pattern 3: Reasoning Agent
```python
agent = SpoonReactAI(
    llm=llm,
    tools=tools,
    max_iterations=5
)
response = agent.run("Complex multi-step task")
```

### Pattern 4: Workflow Agent
```python
graph = StateGraph()
graph.add_node("step1", agent1)
graph.add_node("step2", agent2)
graph.add_edge("step1", "step2")
app = graph.compile()
result = app.invoke({"input": "data"})
```

## Configuration

### Environment Variables
```bash
# .env
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
ETHEREUM_RPC_URL=https://...
PRIVATE_KEY=0x...
```

### Config File
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

## Error Handling

```python
from spoon_ai_sdk.exceptions import (
    AgentExecutionError,
    ToolExecutionError,
    LLMError
)

try:
    response = agent.run(input)
except ToolExecutionError as e:
    # Handle tool errors
    logger.error(f"Tool failed: {e}")
except LLMError as e:
    # Handle LLM errors
    logger.error(f"LLM error: {e}")
except AgentExecutionError as e:
    # Handle agent errors
    logger.error(f"Agent failed: {e}")
```

## Next Steps

- **Explore Tools**: Use `toolkit-tools` skill to discover 50+ ready-made tools
- **Learn Patterns**: Use `agent-patterns` skill for design pattern deep-dives
- **MCP Integration**: Use `mcp-integration` skill for MCP server development
- **Build Blockchain Agents**: Use `blockchain-development` skill for Web3 applications

## Additional Resources

For detailed API documentation and examples:
- `references/agent-api.md` - Complete agent API reference
- `references/llm-api.md` - LLM management API reference
- `references/tool-api.md` - Tool system API reference
- `examples/` - Working code examples for each pattern
