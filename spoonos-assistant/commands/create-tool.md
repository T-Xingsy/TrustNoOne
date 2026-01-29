---
name: create-tool
description: Generate custom BaseTool implementation
trigger: /spoonos:create-tool
version: 0.1.0
---

# Create Tool Command

Generate a custom tool that extends BaseTool from spoon-core.

## Usage

```
/spoonos:create-tool --name <tool_name> [--params <param_list>] [--output <file_path>]
```

## Parameters

- `--name`: Tool name (required)
- `--params`: Comma-separated parameters with types (e.g., "address:str,amount:float")
- `--output`: Output file path (default: `tools/<name>_tool.py`)
- `--description`: Tool description (optional)

## Example

```
/spoonos:create-tool --name get_token_price --params "token_symbol:str,vs_currency:str" --description "Get token price from exchange"
```

Generates:
```python
from spoon_ai_sdk.tools import BaseTool
from pydantic import BaseModel, Field

class GetTokenPriceInput(BaseModel):
    token_symbol: str = Field(..., description="Token symbol")
    vs_currency: str = Field(..., description="Currency to compare against")

class GetTokenPriceTool(BaseTool):
    name: str = "get_token_price"
    description: str = "Get token price from exchange"
    args_schema: type[BaseModel] = GetTokenPriceInput

    def _run(self, token_symbol: str, vs_currency: str) -> str:
        # TODO: Implement tool logic
        return f"Price of {token_symbol} in {vs_currency}"

    async def _arun(self, token_symbol: str, vs_currency: str) -> str:
        # TODO: Implement async version
        return self._run(token_symbol, vs_currency)
```
