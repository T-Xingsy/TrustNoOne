# Detailed Library Comparison

## In-Depth Analysis of SpoonOS Libraries

This document provides comprehensive comparison of spoon-core, spoon-toolkit, and spoon-starter with code examples and use case analysis.

## Architecture Deep Dive

### spoon-core: Framework Layer

**Philosophy**: Provide flexible, extensible infrastructure for AI agent development.

**Key Design Principles**:
- Abstraction over concrete implementations
- Pluggable LLM providers
- Tool-agnostic agent system
- Graph-based workflow orchestration
- Protocol-first approach (MCP support)

**Core APIs**:

#### Agent System
```python
from spoon_ai.agents import BaseAgent, ToolCallAgent, SpoonReactAI

# BaseAgent: Foundation for all agents
class CustomAgent(BaseAgent):
    async def run(self, prompt: str) -> str:
        # Custom agent logic
        pass

# ToolCallAgent: Agent with tool execution
agent = ToolCallAgent(
    name="my_agent",
    llm=ChatBot(),
    available_tools=ToolManager([...])
)

# SpoonReactAI: ReAct pattern implementation
react_agent = SpoonReactAI(
    llm=ChatBot(),
    available_tools=ToolManager([...]),
    max_steps=10
)
```

#### LLM Management
```python
from spoon_ai.chat import ChatBot
from spoon_ai.llm import LLMManager

# Simple ChatBot interface
chatbot = ChatBot(
    llm_provider="openai",  # or "anthropic", "deepseek", "gemini"
    model_name="gpt-4.1",
    temperature=0.7
)

# Advanced LLM management
llm_manager = LLMManager()
llm_manager.register_provider("openai", OpenAIProvider())
llm_manager.register_provider("anthropic", AnthropicProvider())
```

#### Tool System
```python
from spoon_ai.tools import BaseTool, ToolManager

# Define custom tool
class WeatherTool(BaseTool):
    name: str = "get_weather"
    description: str = "Get weather for a location"
    parameters: dict = {
        "type": "object",
        "properties": {
            "location": {"type": "string"}
        },
        "required": ["location"]
    }

    async def execute(self, location: str) -> str:
        # Tool implementation
        return f"Weather in {location}: Sunny"

# Manage tools
tool_manager = ToolManager([WeatherTool(), ...])
```

#### Graph Workflows
```python
from spoon_ai.graph import StateGraph

# Define workflow state
class WorkflowState(TypedDict):
    input: str
    result: str

# Create graph
graph = StateGraph(WorkflowState)

# Add nodes
graph.add_node("process", process_node)
graph.add_node("validate", validate_node)

# Add edges
graph.add_edge("process", "validate")
graph.set_entry_point("process")
graph.set_finish_point("validate")

# Compile and run
workflow = graph.compile()
result = await workflow.invoke({"input": "data"})
```

### spoon-toolkit: Tools Layer

**Philosophy**: Provide production-ready, battle-tested tools for common operations.

**Key Design Principles**:
- Implement BaseTool interface from core
- Focus on blockchain and AI operations
- Professional-grade error handling
- Comprehensive parameter validation
- Well-documented APIs

**Tool Categories**:

#### EVM Tools
```python
from spoon_toolkits.evm import (
    EVMBalanceTool,
    EVMTransferTool,
    EVMSwapTool,
    EVMContractCallTool
)

# Query balance
balance_tool = EVMBalanceTool()
result = await balance_tool.execute(
    address="0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
    rpc_url="https://eth-mainnet.g.alchemy.com/v2/..."
)

# Execute swap
swap_tool = EVMSwapTool()
result = await swap_tool.execute(
    from_token="ETH",
    to_token="USDC",
    amount="1.0",
    slippage=0.5
)
```

#### Solana Tools
```python
from spoon_toolkits.solana import (
    SolanaBalanceTool,
    SolanaTransferTool,
    SolanaTokenTool
)

# Query SOL balance
balance_tool = SolanaBalanceTool()
result = await balance_tool.execute(
    address="7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU"
)
```

#### Memory Tools
```python
from spoon_toolkits.memory import (
    AddMemoryTool,
    SearchMemoryTool,
    DeleteMemoryTool
)

# Add memory
add_tool = AddMemoryTool()
await add_tool.execute(
    content="User prefers dark mode",
    tags=["preference", "ui"]
)

# Search memory
search_tool = SearchMemoryTool()
results = await search_tool.execute(
    query="user preferences",
    limit=10
)
```

#### Audio Tools
```python
from spoon_toolkits.audio import (
    SpeechToTextTool,
    TextToSpeechTool
)

# Transcribe audio
stt_tool = SpeechToTextTool()
text = await stt_tool.execute(
    audio_file="recording.mp3"
)

# Generate speech
tts_tool = TextToSpeechTool()
audio = await tts_tool.execute(
    text="Hello, world!",
    voice="en-US-Neural2-A"
)
```

### spoon-starter: Templates Layer

**Philosophy**: Provide working examples and project templates for quick starts.

**Key Design Principles**:
- Complete, runnable examples
- Best practice demonstrations
- Clear configuration patterns
- Progressive complexity (simple → advanced)
- Copy-and-modify approach

**Example Categories**:

#### Simple ChatBot
```python
# examples/01_simple_chatbot/main.py
from spoon_ai.chat import ChatBot
from dotenv import load_dotenv

load_dotenv()

async def main():
    chatbot = ChatBot(
        llm_provider="openai",
        model_name="gpt-4.1"
    )

    response = await chatbot.chat("Hello!")
    print(response)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

#### ToolCall Agent
```python
# examples/02_toolcall_agent/main.py
from spoon_ai.agents import ToolCallAgent
from spoon_ai.chat import ChatBot
from spoon_ai.tools import ToolManager
from spoon_toolkits.evm import EVMBalanceTool

async def main():
    agent = ToolCallAgent(
        name="blockchain_agent",
        llm=ChatBot(llm_provider="openai"),
        available_tools=ToolManager([
            EVMBalanceTool()
        ])
    )

    response = await agent.run(
        "What's the ETH balance of 0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb?"
    )
    print(response)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

#### ReAct Agent
```python
# examples/03_react_agent/main.py
from spoon_ai.agents import SpoonReactAI
from spoon_ai.chat import ChatBot
from spoon_ai.tools import ToolManager
from spoon_toolkits.evm import EVMBalanceTool, EVMSwapTool

async def main():
    agent = SpoonReactAI(
        name="defi_agent",
        llm=ChatBot(llm_provider="openai"),
        available_tools=ToolManager([
            EVMBalanceTool(),
            EVMSwapTool()
        ]),
        max_steps=10
    )

    response = await agent.run(
        "Check my ETH balance and swap 0.1 ETH to USDC if balance > 1 ETH"
    )
    print(response)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

#### Graph Workflow
```python
# examples/04_graph_workflow/main.py
from spoon_ai.graph import StateGraph
from spoon_ai.chat import ChatBot
from typing import TypedDict

class WorkflowState(TypedDict):
    query: str
    analysis: str
    result: str

async def analyze_node(state: WorkflowState) -> WorkflowState:
    chatbot = ChatBot(llm_provider="openai")
    analysis = await chatbot.chat(f"Analyze: {state['query']}")
    return {**state, "analysis": analysis}

async def execute_node(state: WorkflowState) -> WorkflowState:
    # Execute based on analysis
    result = f"Executed based on: {state['analysis']}"
    return {**state, "result": result}

async def main():
    graph = StateGraph(WorkflowState)
    graph.add_node("analyze", analyze_node)
    graph.add_node("execute", execute_node)
    graph.add_edge("analyze", "execute")
    graph.set_entry_point("analyze")
    graph.set_finish_point("execute")

    workflow = graph.compile()
    result = await workflow.invoke({"query": "Process data"})
    print(result)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

## Use Case Comparison

### Use Case 1: Simple Q&A Bot

**With spoon-core only**:
```python
from spoon_ai.chat import ChatBot

chatbot = ChatBot(llm_provider="openai")
response = await chatbot.chat("What is blockchain?")
```
**Complexity**: Low
**Code**: ~5 lines
**Flexibility**: High

**With spoon-starter**:
```bash
cp -r spoon-starter/examples/01_simple_chatbot my-project
cd my-project
# Modify .env and run
python main.py
```
**Complexity**: Minimal
**Code**: Copy & modify
**Flexibility**: Moderate

### Use Case 2: Blockchain Query Agent

**With spoon-core only**:
```python
# Need to implement custom blockchain tools
class EVMBalanceTool(BaseTool):
    # ~50 lines of implementation
    pass

agent = ToolCallAgent(
    llm=ChatBot(),
    available_tools=ToolManager([EVMBalanceTool()])
)
```
**Complexity**: High
**Code**: ~100+ lines
**Flexibility**: Maximum

**With spoon-core + spoon-toolkit**:
```python
from spoon_ai.agents import ToolCallAgent
from spoon_ai.chat import ChatBot
from spoon_toolkits.evm import EVMBalanceTool

agent = ToolCallAgent(
    llm=ChatBot(),
    available_tools=ToolManager([EVMBalanceTool()])
)
```
**Complexity**: Low
**Code**: ~10 lines
**Flexibility**: High

**With spoon-starter**:
```bash
cp -r spoon-starter/examples/blockchain_agent my-project
# Already configured with toolkit
```
**Complexity**: Minimal
**Code**: Copy & modify
**Flexibility**: Moderate

### Use Case 3: Complex DeFi Agent

**With spoon-core only**:
- Implement all blockchain tools from scratch
- Build custom agent logic
- Handle all error cases
**Effort**: Very High (weeks)

**With spoon-core + spoon-toolkit**:
- Use toolkit's EVM/Solana tools
- Focus on business logic
- Leverage tested implementations
**Effort**: Moderate (days)

**With spoon-starter**:
- Copy DeFi template
- Modify configuration
- Add custom logic
**Effort**: Low (hours)

## Performance Comparison

### Initialization Time

**spoon-core only**:
- Minimal dependencies
- Fast startup
- ~100ms initialization

**spoon-core + spoon-toolkit**:
- Additional tool imports
- Moderate startup
- ~300ms initialization

**spoon-starter**:
- Same as core + toolkit
- Template overhead minimal
- ~300ms initialization

### Runtime Performance

All three approaches have similar runtime performance since:
- Toolkit tools use core's BaseTool interface
- Starter templates use same underlying code
- Performance depends on LLM and tool execution, not library choice

### Memory Usage

**spoon-core only**: ~50MB base
**spoon-core + spoon-toolkit**: ~100MB (loaded tools)
**spoon-starter**: Same as core + toolkit

## Maintenance Comparison

### Update Frequency

**spoon-core**: Stable, infrequent updates (framework changes)
**spoon-toolkit**: Regular updates (new tools, bug fixes)
**spoon-starter**: Frequent updates (new examples, patterns)

### Breaking Changes

**spoon-core**: Rare, well-documented
**spoon-toolkit**: Occasional (tool API changes)
**spoon-starter**: Minimal impact (examples are independent)

### Migration Effort

**spoon-core**: High (framework changes affect everything)
**spoon-toolkit**: Moderate (tool-specific changes)
**spoon-starter**: Low (copy new examples as needed)

## Ecosystem Integration

### With External Tools

**spoon-core**: Implement BaseTool interface
**spoon-toolkit**: Use alongside toolkit tools
**spoon-starter**: Examples show integration patterns

### With MCP Servers

**spoon-core**: Native MCP support (SpoonReactMCP)
**spoon-toolkit**: MCP-compatible tools
**spoon-starter**: MCP integration examples

### With Blockchain Networks

**spoon-core**: Implement custom integrations
**spoon-toolkit**: Pre-built EVM, Solana, Neo tools
**spoon-starter**: Network configuration examples

## Decision Matrix

| Criteria | spoon-core | spoon-toolkit | spoon-starter |
|----------|------------|---------------|---------------|
| **Learning Curve** | Steep | Moderate | Gentle |
| **Development Speed** | Slow | Fast | Fastest |
| **Flexibility** | Maximum | High | Moderate |
| **Code Reusability** | High | Very High | Low (copy-based) |
| **Maintenance** | High effort | Moderate | Low |
| **Production Ready** | Requires work | Yes | Requires customization |
| **Best For** | Frameworks | Applications | Prototypes |

## Recommended Combinations

### Beginner Path
1. Start with spoon-starter examples
2. Understand patterns and structure
3. Gradually explore core APIs
4. Add toolkit tools as needed

### Production Path
1. Use spoon-core for agent structure
2. Use spoon-toolkit for functionality
3. Reference spoon-starter for patterns
4. Build custom tools when needed

### Framework Path
1. Deep dive into spoon-core
2. Study toolkit implementations
3. Contribute to ecosystem
4. Create reusable abstractions

## Summary

**Choose based on**:
- **Time constraints**: starter > toolkit > core
- **Flexibility needs**: core > toolkit > starter
- **Experience level**: starter (beginner) > toolkit (intermediate) > core (advanced)
- **Project type**: starter (prototype) > toolkit (production) > core (framework)

**Most common combination**: spoon-core + spoon-toolkit
**Fastest start**: spoon-starter
**Maximum control**: spoon-core only
