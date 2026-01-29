---
name: SpoonOS Agent Patterns
description: This skill should be used when the user asks about "agent design patterns", "which agent pattern to use", "ChatBot vs ToolCallAgent", "ReAct pattern", "StateGraph workflows", "agent architecture", "multi-agent systems", or needs guidance on choosing and implementing the right agent pattern for their use case.
version: 0.1.0
---

# SpoonOS Agent Design Patterns

Master the four core agent patterns in SpoonOS and learn when to use each one.

## Overview

SpoonOS provides four agent patterns, each optimized for different scenarios:

1. **ChatBot Pattern**: Simple conversational agents
2. **ToolCall Pattern**: Single-turn tool execution
3. **ReAct Pattern**: Multi-step reasoning with tools
4. **StateGraph Pattern**: Complex multi-agent workflows

## Pattern 1: ChatBot

### When to Use
- Pure conversation without external tools
- Customer support chatbots
- Content generation
- Q&A systems
- Conversational interfaces

### Characteristics
- No tool integration
- Conversation memory
- Streaming support
- Simple and fast

### Implementation
```python
from spoon_ai_sdk.agents import ChatBot
from spoon_ai_sdk.llm import LLMManager

llm = LLMManager(provider="openai", model="gpt-4")

agent = ChatBot(
    llm=llm,
    system_prompt="You are a helpful assistant",
    memory=True,
    max_history=20
)

response = agent.run("Hello!")
```

### Best Practices
- Enable memory for conversational context
- Set appropriate max_history to control memory usage
- Use streaming for better UX
- Keep system prompts clear and concise

## Pattern 2: ToolCall

### When to Use
- Simple tool-based queries
- Single-action commands
- Quick data retrieval
- Stateless operations
- API wrappers

### Characteristics
- Single-turn execution
- Tool selection based on input
- No multi-step reasoning
- Fast and efficient

### Implementation
```python
from spoon_ai_sdk.agents import ToolCallAgent
from spoon_toolkits.crypto.evm import EVMGetBalance

tools = [EVMGetBalance(rpc_url="https://...")]

agent = ToolCallAgent(
    llm=llm,
    tools=tools,
    system_prompt="You are a blockchain query assistant"
)

response = agent.run("What's the balance of 0x...?")
```

### Best Practices
- Use for straightforward tool execution
- Provide clear tool descriptions
- Keep tool count manageable (< 10)
- Disable memory for stateless operations

## Pattern 3: ReAct (Reasoning + Acting)

### When to Use
- Complex problem solving
- Multi-step workflows
- Research and analysis
- Decision-making tasks
- Tasks requiring reasoning

### Characteristics
- Iterative reasoning loop
- Multiple tool calls
- Thought → Action → Observation cycle
- Early stopping when answer found

### Implementation
```python
from spoon_ai_sdk.agents import SpoonReactAI

agent = SpoonReactAI(
    llm=llm,
    tools=tools,
    system_prompt="You are a DeFi analyst",
    max_iterations=5,
    verbose=True,
    early_stopping=True
)

response = agent.run("Analyze the best time to swap ETH to USDC")
```

### ReAct Loop
```
1. Thought: "I need to check current ETH price"
2. Action: Use CoinGeckoPrice tool
3. Observation: "ETH is $2,500"
4. Thought: "Now I need to check gas prices"
5. Action: Use EVMGetGasPrice tool
6. Observation: "Gas is 25 gwei"
7. Thought: "I have enough information to recommend"
8. Final Answer: "Good time to swap, gas is low"
```

### Best Practices
- Set appropriate max_iterations (3-7 typical)
- Use verbose=True during development
- Provide reasoning guidelines in system prompt
- Enable early_stopping to save costs
- Monitor iteration usage

## Pattern 4: StateGraph (Workflow)

### When to Use
- Multi-agent collaboration
- Complex pipelines
- Conditional workflows
- Long-running processes
- Orchestration tasks

### Characteristics
- Graph-based execution
- Conditional routing
- Parallel execution support
- Checkpointing
- State management

### Implementation
```python
from spoon_ai_sdk.graph import StateGraph
from typing import TypedDict

class WorkflowState(TypedDict):
    input: str
    analysis: str
    decision: str
    output: str

graph = StateGraph(state_schema=WorkflowState)

# Add nodes
graph.add_node("analyze", analyze_agent)
graph.add_node("decide", decision_agent)
graph.add_node("execute", execution_agent)

# Add edges
graph.add_edge("analyze", "decide")

# Conditional routing
def router(state):
    return "execute" if state["decision"] == "proceed" else "end"

graph.add_conditional_edges("decide", router)

# Compile and run
app = graph.compile()
result = app.invoke({"input": "user query"})
```

### Best Practices
- Define clear state schema
- Use conditional edges for branching logic
- Implement error handling in nodes
- Consider checkpointing for long workflows
- Test each node independently

## Pattern Comparison

| Aspect | ChatBot | ToolCall | ReAct | StateGraph |
|--------|---------|----------|-------|------------|
| **Complexity** | Low | Low | Medium | High |
| **Tools** | No | Yes | Yes | Yes |
| **Reasoning** | No | Limited | Multi-step | Custom |
| **Iterations** | 1 | 1 | Multiple | Multiple |
| **Use Case** | Chat | Simple queries | Complex tasks | Workflows |
| **Cost** | Low | Low | Medium | Variable |
| **Latency** | Low | Low | Medium | Variable |

## Decision Tree

```
Need an AI agent?
├─ No tools needed? → ChatBot
├─ Single tool call? → ToolCallAgent
├─ Multi-step reasoning? → SpoonReactAI
└─ Complex workflow? → StateGraph
```

## Advanced Patterns

### Pattern 5: Hybrid (ReAct + Memory)
Combine ReAct with memory tools for context-aware reasoning.

```python
from spoon_toolkits.memory import AddMemory, SearchMemory

tools = [
    EVMGetBalance(),
    CoinGeckoPrice(),
    AddMemory(),
    SearchMemory()
]

agent = SpoonReactAI(llm=llm, tools=tools, max_iterations=5)
```

### Pattern 6: Multi-Agent (StateGraph)
Multiple specialized agents collaborating.

```python
# Specialized agents
analyst_agent = SpoonReactAI(llm=llm, tools=analysis_tools)
executor_agent = ToolCallAgent(llm=llm, tools=execution_tools)
validator_agent = ChatBot(llm=llm)

# Workflow
graph = StateGraph()
graph.add_node("analyze", analyst_agent)
graph.add_node("execute", executor_agent)
graph.add_node("validate", validator_agent)
```

### Pattern 7: Streaming ReAct
Stream intermediate reasoning steps.

```python
agent = SpoonReactAI(llm=llm, tools=tools, verbose=True)

for step in agent.stream("complex query"):
    print(f"Step: {step}")
```

## Real-World Examples

### Example 1: Customer Support (ChatBot)
```python
agent = ChatBot(
    llm=llm,
    system_prompt="You are a friendly support agent",
    memory=True
)
```

### Example 2: Blockchain Query (ToolCall)
```python
tools = [EVMGetBalance(), EVMGetTransaction()]
agent = ToolCallAgent(llm=llm, tools=tools)
```

### Example 3: DeFi Analyst (ReAct)
```python
tools = [EVMGetBalance(), CoinGeckoPrice(), DeFiLlamaTVL()]
agent = SpoonReactAI(llm=llm, tools=tools, max_iterations=5)
```

### Example 4: Trading Pipeline (StateGraph)
```python
graph = StateGraph()
graph.add_node("analyze_market", market_agent)
graph.add_node("check_balance", balance_agent)
graph.add_node("execute_trade", trade_agent)
graph.add_node("confirm", confirm_agent)
```

## Common Mistakes

### Mistake 1: Using ReAct for Simple Tasks
❌ Don't: Use SpoonReactAI for "What's 2+2?"
✅ Do: Use ChatBot or ToolCallAgent

### Mistake 2: Too Many Tools
❌ Don't: Give 50 tools to ToolCallAgent
✅ Do: Limit to 5-10 relevant tools

### Mistake 3: No Max Iterations
❌ Don't: Set max_iterations=100
✅ Do: Use 3-7 iterations for most tasks

### Mistake 4: Complex StateGraph for Simple Tasks
❌ Don't: Use StateGraph for single-step tasks
✅ Do: Use simpler patterns first

## Performance Optimization

### 1. Choose the Right Pattern
- Start simple (ChatBot/ToolCall)
- Add complexity only when needed
- Measure performance impact

### 2. Optimize Iterations
- Set appropriate max_iterations
- Enable early_stopping
- Monitor iteration usage

### 3. Tool Selection
- Only include necessary tools
- Group related tools
- Use tool categories

### 4. Caching
- Cache LLM responses
- Cache tool outputs
- Use memory tools

## Next Steps

- **Explore Tools**: Use `toolkit-tools` skill to discover available tools
- **MCP Integration**: Use `mcp-integration` skill for dynamic tool loading
- **Build Applications**: Use `blockchain-development` skill for complete examples

## Additional Resources

- `references/pattern-comparison.md` - Detailed pattern comparison
- `references/best-practices.md` - Pattern-specific best practices
- `examples/` - Working examples for each pattern
