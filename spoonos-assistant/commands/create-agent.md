---
name: create-agent
description: Generate complete Agent code based on user specifications
trigger: /spoonos:create-agent
version: 0.1.0
---

# Create Agent Command

Generate a complete SpoonOS agent with specified type, tools, and configuration.

## Usage

```
/spoonos:create-agent --name <agent_name> --type <agent_type> [--tools <tool_list>] [--output <file_path>]
```

## Parameters

- `--name`: Agent name (required)
- `--type`: Agent type: chatbot, toolcall, react, graph (required)
- `--tools`: Comma-separated tool list (optional)
- `--output`: Output file path (default: `agents/<name>.py`)
- `--llm-provider`: LLM provider: openai, anthropic, ollama (default: openai)
- `--model`: LLM model (default: gpt-4)

## Examples

### Example 1: Simple ChatBot
```
/spoonos:create-agent --name my-chatbot --type chatbot
```

Generates:
```python
from spoon_ai_sdk.agents import ChatBot
from spoon_ai_sdk.llm import LLMManager
import os

llm = LLMManager(
    provider="openai",
    model="gpt-4",
    api_key=os.getenv("OPENAI_API_KEY")
)

agent = ChatBot(
    llm=llm,
    system_prompt="You are a helpful assistant",
    memory=True,
    max_history=20
)

if __name__ == "__main__":
    while True:
        user_input = input("You: ")
        if user_input.lower() in ['quit', 'exit']:
            break
        response = agent.run(user_input)
        print(f"Agent: {response}")
```

### Example 2: ToolCall Agent with EVM Tools
```
/spoonos:create-agent --name blockchain-query --type toolcall --tools evm-balance,evm-gas-price
```

Generates agent with EVMGetBalance and EVMGetGasPrice tools.

### Example 3: ReAct Agent for DeFi
```
/spoonos:create-agent --name defi-analyst --type react --tools evm-balance,coingecko-price,defillama-tvl
```

Generates SpoonReactAI agent with DeFi analysis tools.

### Example 4: StateGraph Workflow
```
/spoonos:create-agent --name trading-workflow --type graph
```

Generates StateGraph template with placeholder nodes.

## Generated Code Structure

### ChatBot Template
- LLM initialization
- ChatBot configuration
- Interactive loop
- Error handling

### ToolCall Template
- LLM initialization
- Tool imports and setup
- ToolCallAgent configuration
- Usage example

### ReAct Template
- LLM initialization
- Tool imports and setup
- SpoonReactAI configuration
- System prompt with reasoning guidelines
- Usage example

### StateGraph Template
- State schema definition
- Node functions
- Graph construction
- Edge configuration
- Compilation and execution

## Tool Mapping

Available tools (use with `--tools`):
- `evm-balance`: EVMGetBalance
- `evm-token-balance`: EVMGetTokenBalance
- `evm-transfer`: EVMTransfer
- `evm-gas-price`: EVMGetGasPrice
- `solana-balance`: SolanaGetBalance
- `neo-balance`: NeoGetBalance
- `coingecko-price`: CoinGeckoPrice
- `defillama-tvl`: DeFiLlamaTVL
- `add-memory`: AddMemory
- `search-memory`: SearchMemory

## Implementation

When this command is invoked:

1. Parse parameters
2. Validate agent type and tools
3. Generate appropriate imports
4. Create agent initialization code
5. Add system prompt based on tools
6. Generate main execution block
7. Write to output file
8. Display success message with file path

## Best Practices

- Use descriptive agent names
- Choose appropriate agent type for use case
- Select only necessary tools
- Test generated code before production use
- Customize system prompts for specific needs
- Add error handling as needed
