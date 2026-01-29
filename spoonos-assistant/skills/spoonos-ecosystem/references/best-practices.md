# SpoonOS Development Best Practices

## Project Organization

### Directory Structure

```
my-spoonos-project/
├── agents/              # Agent implementations
│   ├── __init__.py
│   ├── chatbot.py
│   └── trading_agent.py
├── tools/               # Custom tools
│   ├── __init__.py
│   └── custom_tool.py
├── config/              # Configuration files
│   ├── .env
│   ├── config.json
│   └── .mcp.json
├── tests/               # Test files
│   ├── test_agents.py
│   └── test_tools.py
├── requirements.txt     # Dependencies
└── main.py             # Entry point
```

### Configuration Management

**Use environment variables for secrets:**
```python
# .env
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
ETHEREUM_RPC_URL=https://...
PRIVATE_KEY=0x...
```

**Use config.json for application settings:**
```json
{
  "llm": {
    "provider": "openai",
    "model": "gpt-4",
    "temperature": 0.7
  },
  "agent": {
    "max_iterations": 5,
    "timeout": 30
  }
}
```

## Agent Development

### 1. Choose the Right Agent Pattern

**ChatBot**: Simple conversational agents
```python
from spoon_ai_sdk.agents import ChatBot

# Use when: No tools needed, pure conversation
agent = ChatBot(
    llm=llm,
    system_prompt="You are a helpful assistant"
)
```

**ToolCallAgent**: Single-turn tool execution
```python
from spoon_ai_sdk.agents import ToolCallAgent

# Use when: Execute tools based on user input, no multi-step reasoning
agent = ToolCallAgent(
    llm=llm,
    tools=[tool1, tool2]
)
```

**SpoonReactAI**: Multi-step reasoning with tools
```python
from spoon_ai_sdk.agents import SpoonReactAI

# Use when: Complex tasks requiring reasoning and multiple tool calls
agent = SpoonReactAI(
    llm=llm,
    tools=[tool1, tool2],
    max_iterations=5
)
```

**StateGraph**: Complex workflows with conditional logic
```python
from spoon_ai_sdk.graph import StateGraph

# Use when: Multi-agent workflows, conditional routing, complex orchestration
graph = StateGraph()
graph.add_node("step1", agent1)
graph.add_node("step2", agent2)
graph.add_conditional_edges("step1", router_function)
```

### 2. System Prompt Engineering

**Be specific and structured:**
```python
system_prompt = """You are a DeFi trading assistant with the following capabilities:

1. Check token balances across multiple chains
2. Execute token swaps with slippage protection
3. Monitor gas prices and optimize transaction timing
4. Provide market analysis using CoinGecko data

Guidelines:
- Always check balance before executing swaps
- Warn users about high gas prices
- Confirm transactions before execution
- Provide clear explanations of actions taken

Response format:
- Use bullet points for multiple items
- Include transaction hashes when available
- Explain reasoning for recommendations
"""
```

### 3. Error Handling

**Implement comprehensive error handling:**
```python
from spoon_ai_sdk.agents import SpoonReactAI
from spoon_ai_sdk.exceptions import ToolExecutionError, LLMError

try:
    response = agent.run(user_input)
except ToolExecutionError as e:
    # Handle tool-specific errors
    logger.error(f"Tool execution failed: {e}")
    response = "I encountered an error executing that action. Please try again."
except LLMError as e:
    # Handle LLM API errors
    logger.error(f"LLM error: {e}")
    response = "I'm having trouble processing your request. Please try again later."
except Exception as e:
    # Catch-all for unexpected errors
    logger.error(f"Unexpected error: {e}")
    response = "An unexpected error occurred."
```

## Tool Development

### 1. Follow BaseTool Interface

```python
from spoon_ai_sdk.tools import BaseTool
from pydantic import BaseModel, Field

class MyToolInput(BaseModel):
    """Input schema for MyTool"""
    param1: str = Field(..., description="Description of param1")
    param2: int = Field(default=10, description="Description of param2")

class MyTool(BaseTool):
    name: str = "my_tool"
    description: str = "Clear description of what this tool does"

    def _run(self, param1: str, param2: int = 10) -> str:
        """Execute the tool logic"""
        try:
            # Tool implementation
            result = self._execute_logic(param1, param2)
            return result
        except Exception as e:
            return f"Error: {str(e)}"

    def _execute_logic(self, param1: str, param2: int) -> str:
        # Actual implementation
        pass
```

### 2. Tool Naming Conventions

- Use descriptive, action-oriented names: `get_balance`, `swap_tokens`, `mint_nft`
- Prefix with category for clarity: `evm_get_balance`, `solana_transfer`
- Keep names concise but clear

### 3. Tool Documentation

```python
class EVMGetBalance(BaseTool):
    name: str = "evm_get_balance"
    description: str = """Get the native token balance for an Ethereum address.

    Use this tool when you need to:
    - Check ETH balance for an address
    - Verify account has sufficient funds
    - Monitor balance changes

    Parameters:
    - address: Ethereum address (0x...)
    - rpc_url: Optional custom RPC endpoint

    Returns: Balance in ETH as a string

    Example: evm_get_balance(address="0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb")
    """
```

## LLM Management

### 1. Provider Selection

```python
from spoon_ai_sdk.llm import LLMManager

# For production: Use reliable, powerful models
llm = LLMManager(
    provider="openai",
    model="gpt-4",
    temperature=0.7,
    max_tokens=2000
)

# For development: Use faster, cheaper models
llm = LLMManager(
    provider="openai",
    model="gpt-3.5-turbo",
    temperature=0.7
)

# For local development: Use Ollama
llm = LLMManager(
    provider="ollama",
    model="llama2",
    base_url="http://localhost:11434"
)
```

### 2. Cost Optimization

- Use cheaper models for simple tasks
- Implement caching for repeated queries
- Set appropriate max_tokens limits
- Monitor API usage and costs

```python
# Cache responses for repeated queries
from functools import lru_cache

@lru_cache(maxsize=100)
def get_cached_response(query: str) -> str:
    return agent.run(query)
```

### 3. Rate Limiting

```python
import time
from functools import wraps

def rate_limit(calls_per_minute: int):
    min_interval = 60.0 / calls_per_minute
    last_called = [0.0]

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            if elapsed < min_interval:
                time.sleep(min_interval - elapsed)
            result = func(*args, **kwargs)
            last_called[0] = time.time()
            return result
        return wrapper
    return decorator

@rate_limit(calls_per_minute=20)
def call_llm(prompt: str) -> str:
    return llm.generate(prompt)
```

## Testing

### 1. Unit Testing Tools

```python
import pytest
from my_tools import MyTool

def test_my_tool_success():
    tool = MyTool()
    result = tool._run(param1="test", param2=10)
    assert "expected" in result

def test_my_tool_error_handling():
    tool = MyTool()
    result = tool._run(param1="invalid", param2=-1)
    assert "Error" in result
```

### 2. Integration Testing Agents

```python
def test_agent_with_mock_tools():
    # Use mock tools to avoid external API calls
    mock_tool = MockTool()
    agent = ToolCallAgent(llm=llm, tools=[mock_tool])

    response = agent.run("test query")
    assert response is not None
```

### 3. Testing with Real APIs

```python
@pytest.mark.integration
def test_evm_balance_real():
    """Integration test with real blockchain"""
    tool = EVMGetBalance()
    # Use a known address with balance
    result = tool._run(address="0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb")
    assert float(result) > 0
```

## Security

### 1. API Key Management

- Never commit API keys to version control
- Use environment variables or secret management services
- Rotate keys regularly
- Use different keys for development and production

### 2. Private Key Handling

```python
# NEVER log or print private keys
# NEVER commit private keys
# Use hardware wallets for production

from eth_account import Account

# Load from environment
private_key = os.getenv("PRIVATE_KEY")
account = Account.from_key(private_key)

# Clear from memory after use
del private_key
```

### 3. Input Validation

```python
from pydantic import BaseModel, validator
import re

class AddressInput(BaseModel):
    address: str

    @validator('address')
    def validate_ethereum_address(cls, v):
        if not re.match(r'^0x[a-fA-F0-9]{40}$', v):
            raise ValueError('Invalid Ethereum address')
        return v.lower()
```

## Performance

### 1. Async Operations

```python
import asyncio
from spoon_ai_sdk.agents import SpoonReactAI

async def process_multiple_queries(queries: list[str]):
    tasks = [agent.arun(query) for query in queries]
    results = await asyncio.gather(*tasks)
    return results
```

### 2. Batch Processing

```python
def process_batch(items: list, batch_size: int = 10):
    for i in range(0, len(items), batch_size):
        batch = items[i:i + batch_size]
        # Process batch
        results = [process_item(item) for item in batch]
        yield results
```

### 3. Connection Pooling

```python
from web3 import Web3
from web3.providers import HTTPProvider

# Reuse connections
w3 = Web3(HTTPProvider(
    rpc_url,
    request_kwargs={'timeout': 60}
))
```

## Logging

### 1. Structured Logging

```python
import logging
import json

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Log structured data
logger.info(json.dumps({
    "event": "agent_execution",
    "agent_type": "SpoonReactAI",
    "iterations": 3,
    "tools_used": ["evm_balance", "coingecko_price"],
    "success": True
}))
```

### 2. Log Levels

- DEBUG: Detailed information for debugging
- INFO: General information about agent execution
- WARNING: Warning messages for potential issues
- ERROR: Error messages for failures
- CRITICAL: Critical errors requiring immediate attention

## Deployment

### 1. Environment Separation

```
development/
├── .env.development
└── config.development.json

staging/
├── .env.staging
└── config.staging.json

production/
├── .env.production
└── config.production.json
```

### 2. Health Checks

```python
def health_check():
    """Verify all services are operational"""
    checks = {
        "llm": check_llm_connection(),
        "rpc": check_rpc_connection(),
        "database": check_database_connection()
    }
    return all(checks.values()), checks
```

### 3. Monitoring

- Track agent execution times
- Monitor LLM API costs
- Log tool execution success/failure rates
- Alert on error rate thresholds

## Common Pitfalls

### 1. Overusing ReAct Agents

❌ **Don't**: Use SpoonReactAI for simple tasks
```python
# Overkill for simple queries
agent = SpoonReactAI(llm=llm, tools=[])
response = agent.run("Hello")
```

✅ **Do**: Use ChatBot for simple conversations
```python
agent = ChatBot(llm=llm)
response = agent.run("Hello")
```

### 2. Ignoring Error Handling

❌ **Don't**: Assume tools always succeed
```python
result = tool._run(param="value")
return result
```

✅ **Do**: Handle errors gracefully
```python
try:
    result = tool._run(param="value")
    return result
except Exception as e:
    logger.error(f"Tool failed: {e}")
    return "Error occurred"
```

### 3. Hardcoding Configuration

❌ **Don't**: Hardcode values
```python
llm = LLMManager(provider="openai", api_key="sk-...")
```

✅ **Do**: Use environment variables
```python
llm = LLMManager(
    provider=os.getenv("LLM_PROVIDER"),
    api_key=os.getenv("OPENAI_API_KEY")
)
```

## Summary

**Key Principles**:
1. Choose the right agent pattern for your use case
2. Implement comprehensive error handling
3. Follow security best practices
4. Test thoroughly (unit + integration)
5. Monitor and log in production
6. Optimize for performance and cost
7. Keep configuration separate from code
8. Document your tools and agents clearly

**Remember**: Start simple, iterate based on real usage, and always prioritize security and reliability.
