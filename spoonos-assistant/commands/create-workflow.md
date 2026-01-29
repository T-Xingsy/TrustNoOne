---
name: create-workflow
description: Generate StateGraph workflow code
trigger: /spoonos:create-workflow
version: 0.1.0
---

# Create Workflow Command

Generate StateGraph workflow with multiple agents and conditional routing.

## Usage

```
/spoonos:create-workflow --name <workflow_name> [--nodes <node_list>] [--output <file_path>]
```

## Parameters

- `--name`: Workflow name (required)
- `--nodes`: Comma-separated node names (e.g., "analyze,decide,execute")
- `--output`: Output file path (default: `workflows/<name>.py`)

## Example

```
/spoonos:create-workflow --name trading-pipeline --nodes "analyze,check_balance,execute,confirm"
```

Generates:
```python
from spoon_ai_sdk.graph import StateGraph
from typing import TypedDict

class TradingPipelineState(TypedDict):
    input: str
    analysis: str
    balance: str
    execution: str
    confirmation: str
    output: str

def analyze_node(state):
    # TODO: Implement analysis logic
    return {"analysis": "Analysis result"}

def check_balance_node(state):
    # TODO: Implement balance check
    return {"balance": "Balance check result"}

def execute_node(state):
    # TODO: Implement execution logic
    return {"execution": "Execution result"}

def confirm_node(state):
    # TODO: Implement confirmation logic
    return {"confirmation": "Confirmed", "output": "Final output"}

# Create workflow
graph = StateGraph(state_schema=TradingPipelineState)

# Add nodes
graph.add_node("analyze", analyze_node)
graph.add_node("check_balance", check_balance_node)
graph.add_node("execute", execute_node)
graph.add_node("confirm", confirm_node)

# Add edges
graph.add_edge("analyze", "check_balance")
graph.add_edge("check_balance", "execute")
graph.add_edge("execute", "confirm")

# Set entry and finish
graph.set_entry_point("analyze")
graph.set_finish_point("confirm")

# Compile
app = graph.compile()

if __name__ == "__main__":
    result = app.invoke({"input": "Start workflow"})
    print(result["output"])
```
