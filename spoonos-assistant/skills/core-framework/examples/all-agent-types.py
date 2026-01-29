"""
Core Framework Examples - Demonstrating all agent types

This file shows how to use each agent type from spoon-core with practical examples.
"""

from spoon_ai_sdk.agents import ChatBot, ToolCallAgent, SpoonReactAI
from spoon_ai_sdk.graph import StateGraph
from spoon_ai_sdk.llm import LLMManager
from spoon_ai_sdk.tools import BaseTool
from pydantic import BaseModel, Field
from typing import TypedDict
import os

# Initialize LLM (shared across examples)
llm = LLMManager(
    provider="openai",
    model="gpt-4",
    api_key=os.getenv("OPENAI_API_KEY")
)

# ============================================================================
# Example 1: ChatBot - Simple Conversation
# ============================================================================

def example_chatbot():
    """Simple conversational agent without tools"""
    print("\n=== Example 1: ChatBot ===\n")

    agent = ChatBot(
        llm=llm,
        system_prompt="You are a friendly assistant who loves to help",
        memory=True,
        max_history=10
    )

    # Conversation with memory
    print("User: Hello!")
    response1 = agent.run("Hello!")
    print(f"Agent: {response1}\n")

    print("User: What's my name?")
    response2 = agent.run("My name is Alice. What's my name?")
    print(f"Agent: {response2}\n")

    print("User: What did I just tell you?")
    response3 = agent.run("What did I just tell you?")
    print(f"Agent: {response3}\n")

# ============================================================================
# Example 2: ToolCallAgent - Single Tool Execution
# ============================================================================

# Define a simple tool
class CalculatorInput(BaseModel):
    operation: str = Field(..., description="Operation: add, subtract, multiply, divide")
    a: float = Field(..., description="First number")
    b: float = Field(..., description="Second number")

class CalculatorTool(BaseTool):
    name: str = "calculator"
    description: str = "Perform basic arithmetic operations (add, subtract, multiply, divide)"
    args_schema: type[BaseModel] = CalculatorInput

    def _run(self, operation: str, a: float, b: float) -> str:
        operations = {
            "add": lambda x, y: x + y,
            "subtract": lambda x, y: x - y,
            "multiply": lambda x, y: x * y,
            "divide": lambda x, y: x / y if y != 0 else "Error: Division by zero"
        }

        if operation not in operations:
            return f"Error: Unknown operation '{operation}'"

        result = operations[operation](a, b)
        return f"Result: {a} {operation} {b} = {result}"

def example_tool_call_agent():
    """Agent that executes tools based on user input"""
    print("\n=== Example 2: ToolCallAgent ===\n")

    tools = [CalculatorTool()]

    agent = ToolCallAgent(
        llm=llm,
        tools=tools,
        system_prompt="You are a math assistant. Use the calculator tool to solve problems.",
        return_intermediate_steps=True
    )

    print("User: What is 15 multiplied by 7?")
    response = agent.run("What is 15 multiplied by 7?")
    print(f"Agent: {response}\n")

    # Show intermediate steps
    if agent.last_execution:
        print("Tool calls made:")
        for call in agent.last_execution.tool_calls:
            print(f"  - {call.tool}: {call.input}")

# ============================================================================
# Example 3: SpoonReactAI - Multi-Step Reasoning
# ============================================================================

class WeatherInput(BaseModel):
    city: str = Field(..., description="City name")

class WeatherTool(BaseTool):
    name: str = "get_weather"
    description: str = "Get current weather for a city"
    args_schema: type[BaseModel] = WeatherInput

    def _run(self, city: str) -> str:
        # Mock weather data
        weather_data = {
            "New York": "Sunny, 72°F",
            "London": "Rainy, 15°C",
            "Tokyo": "Cloudy, 20°C"
        }
        return weather_data.get(city, f"Weather data not available for {city}")

class RecommendationInput(BaseModel):
    weather: str = Field(..., description="Weather description")

class RecommendationTool(BaseTool):
    name: str = "get_recommendation"
    description: str = "Get activity recommendation based on weather"
    args_schema: type[BaseModel] = RecommendationInput

    def _run(self, weather: str) -> str:
        if "sunny" in weather.lower():
            return "Great day for outdoor activities! Consider a picnic or hiking."
        elif "rainy" in weather.lower():
            return "Stay indoors. Good time for reading or watching movies."
        else:
            return "Moderate weather. Indoor or outdoor activities both work."

def example_react_agent():
    """Agent with multi-step reasoning"""
    print("\n=== Example 3: SpoonReactAI ===\n")

    tools = [WeatherTool(), RecommendationTool(), CalculatorTool()]

    agent = SpoonReactAI(
        llm=llm,
        tools=tools,
        system_prompt="You are a helpful assistant. Use tools to answer questions.",
        max_iterations=5,
        verbose=True,
        early_stopping=True
    )

    print("User: What's the weather in London and what should I do today?")
    response = agent.run("What's the weather in London and what should I do today?")
    print(f"\nFinal Answer: {response}\n")

    # Show reasoning trace
    if agent.last_execution:
        print(f"Iterations used: {agent.last_execution.iterations_used}")
        print(f"Stopped early: {agent.last_execution.stopped_early}")

# ============================================================================
# Example 4: StateGraph - Multi-Agent Workflow
# ============================================================================

class WorkflowState(TypedDict):
    input: str
    weather: str
    calculation: str
    recommendation: str
    output: str

def example_state_graph():
    """Complex workflow with multiple agents"""
    print("\n=== Example 4: StateGraph ===\n")

    # Define workflow nodes
    def get_weather_node(state):
        """Node 1: Get weather"""
        city = state["input"]
        weather_tool = WeatherTool()
        weather = weather_tool._run(city)
        return {"weather": weather}

    def calculate_node(state):
        """Node 2: Some calculation"""
        calc_tool = CalculatorTool()
        result = calc_tool._run("multiply", 10, 5)
        return {"calculation": result}

    def recommend_node(state):
        """Node 3: Get recommendation"""
        rec_tool = RecommendationTool()
        recommendation = rec_tool._run(state["weather"])
        return {"recommendation": recommendation}

    def summarize_node(state):
        """Node 4: Summarize results"""
        output = f"""
        Weather: {state['weather']}
        Calculation: {state['calculation']}
        Recommendation: {state['recommendation']}
        """
        return {"output": output.strip()}

    # Create graph
    graph = StateGraph(state_schema=WorkflowState)

    # Add nodes
    graph.add_node("weather", get_weather_node)
    graph.add_node("calculate", calculate_node)
    graph.add_node("recommend", recommend_node)
    graph.add_node("summarize", summarize_node)

    # Add edges
    graph.add_edge("weather", "calculate")
    graph.add_edge("calculate", "recommend")
    graph.add_edge("recommend", "summarize")

    # Set entry and finish points
    graph.set_entry_point("weather")
    graph.set_finish_point("summarize")

    # Compile and run
    app = graph.compile()

    print("Running workflow for: Tokyo")
    result = app.invoke({"input": "Tokyo"})
    print(f"\nWorkflow Output:\n{result['output']}\n")

# ============================================================================
# Main
# ============================================================================

def main():
    """Run all examples"""
    print("="*70)
    print("SpoonOS Core Framework Examples")
    print("="*70)

    try:
        example_chatbot()
    except Exception as e:
        print(f"ChatBot example error: {e}")

    try:
        example_tool_call_agent()
    except Exception as e:
        print(f"ToolCallAgent example error: {e}")

    try:
        example_react_agent()
    except Exception as e:
        print(f"SpoonReactAI example error: {e}")

    try:
        example_state_graph()
    except Exception as e:
        print(f"StateGraph example error: {e}")

    print("="*70)
    print("Examples completed!")
    print("="*70)

if __name__ == "__main__":
    main()
