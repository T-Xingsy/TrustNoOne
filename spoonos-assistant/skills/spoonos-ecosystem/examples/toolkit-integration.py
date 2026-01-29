"""
Toolkit Integration Example - spoon-core + spoon-toolkit

This example demonstrates how to combine spoon-core agents with spoon-toolkit tools
to create a blockchain-aware AI agent.

Use case: DeFi agents, blockchain query bots, crypto portfolio managers
"""

from spoon_ai_sdk.agents import SpoonReactAI
from spoon_ai_sdk.llm import LLMManager
from spoon_ai_sdk.tools import ToolManager

# Import tools from spoon-toolkit
from spoon_toolkits.crypto.evm import (
    EVMGetBalance,
    EVMGetGasPrice,
    EVMGetTokenBalance
)
from spoon_toolkits.data.coingecko import CoinGeckoPrice
from spoon_toolkits.memory import AddMemory, SearchMemory

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_defi_agent():
    """Create a DeFi agent with blockchain tools"""

    # Initialize LLM
    llm = LLMManager(
        provider="openai",
        model="gpt-4",
        api_key=os.getenv("OPENAI_API_KEY"),
        temperature=0.7
    )

    # Initialize tools from spoon-toolkit
    tools = [
        # EVM blockchain tools
        EVMGetBalance(
            rpc_url=os.getenv("ETHEREUM_RPC_URL")
        ),
        EVMGetGasPrice(
            rpc_url=os.getenv("ETHEREUM_RPC_URL")
        ),
        EVMGetTokenBalance(
            rpc_url=os.getenv("ETHEREUM_RPC_URL")
        ),

        # Market data tools
        CoinGeckoPrice(),

        # Memory tools for context
        AddMemory(),
        SearchMemory()
    ]

    # Create tool manager
    tool_manager = ToolManager(tools=tools)

    # System prompt for DeFi agent
    system_prompt = """You are a DeFi assistant with access to blockchain data and market information.

    Your capabilities:
    - Check ETH and token balances for any address
    - Monitor gas prices for optimal transaction timing
    - Get real-time cryptocurrency prices
    - Remember user preferences and past interactions

    Guidelines:
    - Always verify addresses before querying
    - Warn about high gas prices (>50 gwei)
    - Provide context with price data (24h change, market cap)
    - Remember important user information for future interactions

    When users ask about balances or prices:
    1. Use the appropriate tool to fetch data
    2. Present information clearly with units
    3. Offer relevant insights or recommendations
    """

    # Create ReAct agent with tools
    agent = SpoonReactAI(
        llm=llm,
        tools=tool_manager.get_tools(),
        system_prompt=system_prompt,
        max_iterations=5,  # Allow up to 5 reasoning steps
        verbose=True  # Show reasoning process
    )

    return agent

def example_queries():
    """Example queries to demonstrate agent capabilities"""
    return [
        "What's the ETH balance of 0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb?",
        "What's the current gas price on Ethereum?",
        "What's the current price of Bitcoin?",
        "Remember that my main wallet is 0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
        "What's my wallet balance?" # Uses memory from previous interaction
    ]

def main():
    """Run DeFi agent with example queries"""
    print("=== SpoonOS DeFi Agent (core + toolkit) ===\n")

    # Create agent
    agent = create_defi_agent()

    # Run example queries
    examples = example_queries()

    print("Running example queries:\n")
    for i, query in enumerate(examples, 1):
        print(f"\n{'='*60}")
        print(f"Query {i}: {query}")
        print('='*60)

        try:
            response = agent.run(query)
            print(f"\nAgent Response:\n{response}\n")

        except Exception as e:
            print(f"Error: {e}\n")

    # Interactive mode
    print("\n" + "="*60)
    print("Interactive mode - Type your own queries (or 'quit' to exit)")
    print("="*60 + "\n")

    while True:
        user_input = input("You: ").strip()

        if user_input.lower() in ['quit', 'exit', 'q']:
            print("Goodbye!")
            break

        if not user_input:
            continue

        try:
            response = agent.run(user_input)
            print(f"\nAgent: {response}\n")

        except Exception as e:
            print(f"Error: {e}\n")

if __name__ == "__main__":
    main()
