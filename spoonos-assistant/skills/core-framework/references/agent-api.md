# Agent API Reference

Complete API documentation for all agent classes in spoon-core.

## BaseAgent

Abstract base class for all agents.

### Class Definition
```python
class BaseAgent(ABC):
    """Base class for all SpoonOS agents"""

    def __init__(
        self,
        llm: LLMManager,
        system_prompt: str = "",
        memory: bool = False,
        **kwargs
    ):
        """
        Initialize base agent.

        Args:
            llm: LLMManager instance for LLM interactions
            system_prompt: System instructions for the agent
            memory: Enable conversation history
            **kwargs: Additional agent-specific parameters
        """
```

### Methods

#### run()
```python
def run(self, input: str, **kwargs) -> str:
    """
    Execute agent with input and return response.

    Args:
        input: User input string
        **kwargs: Additional execution parameters

    Returns:
        Agent response as string

    Raises:
        AgentExecutionError: If execution fails
    """
```

#### arun()
```python
async def arun(self, input: str, **kwargs) -> str:
    """
    Async version of run().

    Args:
        input: User input string
        **kwargs: Additional execution parameters

    Returns:
        Agent response as string

    Raises:
        AgentExecutionError: If execution fails
    """
```

#### reset()
```python
def reset(self) -> None:
    """
    Reset agent state, clear memory, reset counters.
    """
```

### Properties

```python
@property
def llm(self) -> LLMManager:
    """Get LLM manager instance"""

@property
def memory(self) -> Optional[ConversationMemory]:
    """Get conversation memory if enabled"""
```

## ChatBot

Simple conversational agent without tools.

### Class Definition
```python
class ChatBot(BaseAgent):
    """Conversational agent for chat interactions"""

    def __init__(
        self,
        llm: LLMManager,
        system_prompt: str = "You are a helpful assistant",
        memory: bool = True,
        max_history: int = 10,
        streaming: bool = False
    ):
        """
        Initialize ChatBot.

        Args:
            llm: LLMManager instance
            system_prompt: System instructions
            memory: Enable conversation history
            max_history: Maximum messages to retain
            streaming: Enable streaming responses
        """
```

### Example Usage
```python
from spoon_ai_sdk.agents import ChatBot
from spoon_ai_sdk.llm import LLMManager

llm = LLMManager(provider="openai", model="gpt-4")

agent = ChatBot(
    llm=llm,
    system_prompt="You are a friendly assistant",
    memory=True,
    max_history=20
)

# Single interaction
response = agent.run("Hello!")

# Streaming response
for chunk in agent.stream("Tell me a story"):
    print(chunk, end="", flush=True)
```

### Methods

#### stream()
```python
def stream(self, input: str) -> Iterator[str]:
    """
    Stream response chunks.

    Args:
        input: User input

    Yields:
        Response chunks as strings
    """
```

## ToolCallAgent

Single-turn tool execution agent.

### Class Definition
```python
class ToolCallAgent(BaseAgent):
    """Agent that executes tools based on user input"""

    def __init__(
        self,
        llm: LLMManager,
        tools: list[BaseTool],
        system_prompt: str = "",
        return_intermediate_steps: bool = False,
        max_tool_calls: int = 1
    ):
        """
        Initialize ToolCallAgent.

        Args:
            llm: LLMManager instance
            tools: List of available tools
            system_prompt: System instructions
            return_intermediate_steps: Include tool execution details
            max_tool_calls: Maximum tools to call per run
        """
```

### Example Usage
```python
from spoon_ai_sdk.agents import ToolCallAgent
from spoon_toolkits.crypto.evm import EVMGetBalance

tools = [EVMGetBalance()]

agent = ToolCallAgent(
    llm=llm,
    tools=tools,
    system_prompt="You are a blockchain query assistant",
    return_intermediate_steps=True
)

response = agent.run("What's the balance of 0x...")

# Access intermediate steps
if agent.last_execution:
    print(agent.last_execution.tool_calls)
    print(agent.last_execution.tool_outputs)
```

### Properties

```python
@property
def tools(self) -> list[BaseTool]:
    """Get list of available tools"""

@property
def last_execution(self) -> Optional[ExecutionTrace]:
    """Get details of last execution"""
```

## SpoonReactAI

Multi-step reasoning agent with iterative tool use.

### Class Definition
```python
class SpoonReactAI(BaseAgent):
    """ReAct pattern agent for complex reasoning"""

    def __init__(
        self,
        llm: LLMManager,
        tools: list[BaseTool],
        system_prompt: str = "",
        max_iterations: int = 5,
        early_stopping: bool = True,
        verbose: bool = False,
        return_intermediate_steps: bool = False
    ):
        """
        Initialize SpoonReactAI.

        Args:
            llm: LLMManager instance
            tools: List of available tools
            system_prompt: System instructions
            max_iterations: Maximum reasoning cycles
            early_stopping: Stop when answer found
            verbose: Print reasoning steps
            return_intermediate_steps: Include execution trace
        """
```

### Example Usage
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

response = agent.run("Analyze the best time to swap ETH")

# Access reasoning trace
for step in agent.last_execution.steps:
    print(f"Thought: {step.thought}")
    print(f"Action: {step.action}")
    print(f"Observation: {step.observation}")
```

### Execution Trace

```python
class ReActStep:
    thought: str  # Agent's reasoning
    action: str  # Tool to execute
    action_input: dict  # Tool parameters
    observation: str  # Tool output

class ExecutionTrace:
    steps: list[ReActStep]
    final_answer: str
    iterations_used: int
    stopped_early: bool
```

### Methods

#### get_execution_trace()
```python
def get_execution_trace(self) -> ExecutionTrace:
    """
    Get detailed execution trace.

    Returns:
        ExecutionTrace with all reasoning steps
    """
```

## StateGraph

Complex workflow orchestration with conditional routing.

### Class Definition
```python
class StateGraph:
    """Graph-based workflow orchestration"""

    def __init__(
        self,
        state_schema: Optional[type[TypedDict]] = None
    ):
        """
        Initialize StateGraph.

        Args:
            state_schema: TypedDict defining state structure
        """
```

### Example Usage
```python
from spoon_ai_sdk.graph import StateGraph
from typing import TypedDict

# Define state
class WorkflowState(TypedDict):
    input: str
    analysis: str
    decision: str
    output: str

# Create graph
graph = StateGraph(state_schema=WorkflowState)

# Add nodes
def analyze(state):
    # Analysis logic
    return {"analysis": "..."}

def decide(state):
    # Decision logic
    return {"decision": "proceed"}

graph.add_node("analyze", analyze)
graph.add_node("decide", decide)

# Add edges
graph.add_edge("analyze", "decide")

# Conditional routing
def route_decision(state):
    if state["decision"] == "proceed":
        return "execute"
    return "end"

graph.add_conditional_edges("decide", route_decision)

# Set entry/exit
graph.set_entry_point("analyze")
graph.set_finish_point("end")

# Compile and run
app = graph.compile()
result = app.invoke({"input": "user query"})
```

### Methods

#### add_node()
```python
def add_node(
    self,
    name: str,
    func: Callable[[dict], dict]
) -> None:
    """
    Add a node to the graph.

    Args:
        name: Unique node identifier
        func: Function that processes state
    """
```

#### add_edge()
```python
def add_edge(
    self,
    from_node: str,
    to_node: str
) -> None:
    """
    Add a fixed edge between nodes.

    Args:
        from_node: Source node name
        to_node: Destination node name
    """
```

#### add_conditional_edges()
```python
def add_conditional_edges(
    self,
    from_node: str,
    router: Callable[[dict], str]
) -> None:
    """
    Add conditional routing from a node.

    Args:
        from_node: Source node name
        router: Function that returns next node name based on state
    """
```

#### compile()
```python
def compile(self) -> CompiledGraph:
    """
    Compile graph into executable application.

    Returns:
        CompiledGraph ready for execution
    """
```

### CompiledGraph

```python
class CompiledGraph:
    def invoke(self, input: dict) -> dict:
        """Execute graph with input"""

    async def ainvoke(self, input: dict) -> dict:
        """Async execution"""

    def stream(self, input: dict) -> Iterator[dict]:
        """Stream intermediate states"""
```

## Agent Comparison

| Feature | ChatBot | ToolCallAgent | SpoonReactAI | StateGraph |
|---------|---------|---------------|--------------|------------|
| **Tools** | No | Yes | Yes | Yes (per node) |
| **Reasoning** | No | Limited | Multi-step | Custom |
| **Iterations** | 1 | 1 | Multiple | Multiple |
| **Complexity** | Low | Low | Medium | High |
| **Use Case** | Chat | Simple queries | Complex tasks | Workflows |
| **Async** | Yes | Yes | Yes | Yes |
| **Streaming** | Yes | No | No | Yes |

## Best Practices

### 1. Choose the Right Agent

- **ChatBot**: Pure conversation, no tools needed
- **ToolCallAgent**: Single tool execution, simple queries
- **SpoonReactAI**: Complex reasoning, multiple tool calls
- **StateGraph**: Multi-agent workflows, conditional logic

### 2. System Prompts

```python
# Good: Specific and structured
system_prompt = """You are a DeFi assistant.

Capabilities:
- Check balances
- Execute swaps
- Monitor gas prices

Guidelines:
- Always verify addresses
- Warn about high gas
- Confirm before transactions
"""

# Bad: Vague and unstructured
system_prompt = "You are helpful"
```

### 3. Error Handling

```python
try:
    response = agent.run(input)
except AgentExecutionError as e:
    logger.error(f"Agent failed: {e}")
    response = "I encountered an error"
```

### 4. Memory Management

```python
# Enable memory for conversational agents
agent = ChatBot(llm=llm, memory=True, max_history=20)

# Disable for stateless agents
agent = ToolCallAgent(llm=llm, tools=tools, memory=False)
```

### 5. Verbose Mode

```python
# Enable during development
agent = SpoonReactAI(llm=llm, tools=tools, verbose=True)

# Disable in production
agent = SpoonReactAI(llm=llm, tools=tools, verbose=False)
```

## See Also

- `llm-api.md` - LLM management API
- `tool-api.md` - Tool system API
- `../examples/` - Working code examples
