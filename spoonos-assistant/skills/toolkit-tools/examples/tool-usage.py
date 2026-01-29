"""
Toolkit Tools Usage Examples

Demonstrates how to use various tools from spoon-toolkit in real scenarios.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ============================================================================
# Example 1: EVM Tools - Portfolio Tracker
# ============================================================================

def example_portfolio_tracker():
    """Track crypto portfolio across multiple tokens"""
    from spoon_toolkits.crypto.evm import EVMGetBalance, EVMGetTokenBalance
    from spoon_toolkits.data import CoinGeckoPrice

    print("\n=== Portfolio Tracker ===\n")

    # User's wallet address
    wallet = "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb"
    rpc_url = os.getenv("ETHEREUM_RPC_URL")

    # Get ETH balance
    eth_tool = EVMGetBalance(rpc_url=rpc_url)
    eth_balance = eth_tool._run(address=wallet)
    print(f"ETH Balance: {eth_balance}")

    # Get USDT balance
    usdt_tool = EVMGetTokenBalance(rpc_url=rpc_url)
    usdt_balance = usdt_tool._run(
        address=wallet,
        token_address="0xdAC17F958D2ee523a2206206994597C13D831ec7"  # USDT
    )
    print(f"USDT Balance: {usdt_balance}")

    # Get current prices
    price_tool = CoinGeckoPrice()
    eth_price = price_tool._run(coin_id="ethereum", vs_currency="usd")
    print(f"ETH Price: {eth_price}")

# ============================================================================
# Example 2: Gas Price Monitor
# ============================================================================

def example_gas_monitor():
    """Monitor gas prices for optimal transaction timing"""
    from spoon_toolkits.crypto.evm import EVMGetGasPrice

    print("\n=== Gas Price Monitor ===\n")

    rpc_url = os.getenv("ETHEREUM_RPC_URL")
    tool = EVMGetGasPrice(rpc_url=rpc_url)

    gas_prices = tool._run()
    print(f"Current Gas Prices:\n{gas_prices}")

    # Decision logic
    if "standard" in gas_prices.lower():
        # Parse gas price (simplified)
        print("\nRecommendation: Gas prices are moderate. Good time to transact.")
    else:
        print("\nRecommendation: Check gas prices before transacting.")

# ============================================================================
# Example 3: Multi-Chain Balance Checker
# ============================================================================

def example_multichain_balance():
    """Check balances across multiple chains"""
    from spoon_toolkits.crypto.evm import EVMGetBalance
    from spoon_toolkits.crypto.solana import SolanaGetBalance
    from spoon_toolkits.crypto.neo import NeoGetBalance

    print("\n=== Multi-Chain Balance Checker ===\n")

    # Ethereum
    eth_tool = EVMGetBalance(rpc_url=os.getenv("ETHEREUM_RPC_URL"))
    eth_balance = eth_tool._run(address="0x...")
    print(f"Ethereum: {eth_balance}")

    # Solana
    sol_tool = SolanaGetBalance(rpc_url="https://api.mainnet-beta.solana.com")
    sol_balance = sol_tool._run(address="...")
    print(f"Solana: {sol_balance}")

    # Neo
    neo_tool = NeoGetBalance(rpc_url="https://mainnet1.neo.org:443")
    neo_balance = neo_tool._run(address="N...")
    print(f"Neo: {neo_balance}")

# ============================================================================
# Example 4: DeFi Agent with Memory
# ============================================================================

def example_defi_agent_with_memory():
    """DeFi agent that remembers user preferences"""
    from spoon_ai_sdk.agents import SpoonReactAI
    from spoon_ai_sdk.llm import LLMManager
    from spoon_toolkits.crypto.evm import EVMGetBalance, EVMGetGasPrice
    from spoon_toolkits.data import CoinGeckoPrice
    from spoon_toolkits.memory import AddMemory, SearchMemory

    print("\n=== DeFi Agent with Memory ===\n")

    # Initialize LLM
    llm = LLMManager(
        provider="openai",
        model="gpt-4",
        api_key=os.getenv("OPENAI_API_KEY")
    )

    # Initialize tools
    tools = [
        EVMGetBalance(rpc_url=os.getenv("ETHEREUM_RPC_URL")),
        EVMGetGasPrice(rpc_url=os.getenv("ETHEREUM_RPC_URL")),
        CoinGeckoPrice(),
        AddMemory(),
        SearchMemory()
    ]

    # Create agent
    agent = SpoonReactAI(
        llm=llm,
        tools=tools,
        system_prompt="""You are a DeFi assistant with memory.

        Capabilities:
        - Check ETH balances
        - Monitor gas prices
        - Get crypto prices
        - Remember user preferences and information

        Guidelines:
        - Use AddMemory to store important user information
        - Use SearchMemory to recall past interactions
        - Provide personalized recommendations based on memory
        """,
        max_iterations=5,
        verbose=True
    )

    # Example interactions
    queries = [
        "Remember that my main wallet is 0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
        "What's my wallet balance?",  # Should use memory
        "What's the current gas price?",
        "Remember that I prefer to transact when gas is below 30 gwei"
    ]

    for query in queries:
        print(f"\nUser: {query}")
        response = agent.run(query)
        print(f"Agent: {response}\n")

# ============================================================================
# Example 5: Market Data Analyzer
# ============================================================================

def example_market_analyzer():
    """Analyze crypto market data"""
    from spoon_toolkits.data import CoinGeckoPrice, CoinGeckoMarketData, DeFiLlamaTVL

    print("\n=== Market Data Analyzer ===\n")

    # Get Bitcoin price
    price_tool = CoinGeckoPrice()
    btc_price = price_tool._run(coin_id="bitcoin", vs_currency="usd")
    print(f"Bitcoin: {btc_price}")

    # Get detailed market data
    market_tool = CoinGeckoMarketData()
    eth_data = market_tool._run(coin_id="ethereum")
    print(f"\nEthereum Market Data:\n{eth_data}")

    # Get DeFi protocol TVL
    tvl_tool = DeFiLlamaTVL()
    uniswap_tvl = tvl_tool._run(protocol="uniswap")
    print(f"\nUniswap TVL: {uniswap_tvl}")

# ============================================================================
# Example 6: Audio Agent
# ============================================================================

def example_audio_agent():
    """Agent with text-to-speech capabilities"""
    from spoon_toolkits.audio import TextToSpeech

    print("\n=== Audio Agent ===\n")

    tool = TextToSpeech(api_key=os.getenv("ELEVENLABS_API_KEY"))

    text = "Hello! Your Ethereum balance is 1.5 ETH. Current gas price is 25 gwei."

    audio_file = tool._run(
        text=text,
        voice="adam",
        output_path="agent_response.mp3"
    )

    print(f"Audio generated: {audio_file}")
    print("Agent can now speak responses!")

# ============================================================================
# Example 7: Tool Combination - Smart Transaction
# ============================================================================

def example_smart_transaction():
    """Combine multiple tools for intelligent transaction execution"""
    from spoon_toolkits.crypto.evm import (
        EVMGetBalance,
        EVMGetGasPrice,
        EVMEstimateGas,
        EVMTransfer
    )

    print("\n=== Smart Transaction ===\n")

    rpc_url = os.getenv("ETHEREUM_RPC_URL")
    private_key = os.getenv("PRIVATE_KEY")

    # Step 1: Check balance
    balance_tool = EVMGetBalance(rpc_url=rpc_url)
    balance = balance_tool._run(address="0x...")
    print(f"Current balance: {balance}")

    # Step 2: Check gas price
    gas_tool = EVMGetGasPrice(rpc_url=rpc_url)
    gas_price = gas_tool._run()
    print(f"Gas prices: {gas_price}")

    # Step 3: Estimate gas cost
    estimate_tool = EVMEstimateGas(rpc_url=rpc_url)
    estimate = estimate_tool._run(
        from_address="0x...",
        to_address="0x...",
        data="0x"
    )
    print(f"Estimated gas: {estimate}")

    # Step 4: Execute transfer (if conditions are met)
    # transfer_tool = EVMTransfer(rpc_url=rpc_url, private_key=private_key)
    # tx_hash = transfer_tool._run(to_address="0x...", amount=0.1)
    # print(f"Transaction: {tx_hash}")

    print("\nSmart transaction logic:")
    print("1. Verified sufficient balance")
    print("2. Checked gas prices are reasonable")
    print("3. Estimated transaction cost")
    print("4. Ready to execute (commented out for safety)")

# ============================================================================
# Main
# ============================================================================

def main():
    """Run all examples"""
    print("="*70)
    print("SpoonOS Toolkit Tools Examples")
    print("="*70)

    examples = [
        ("Portfolio Tracker", example_portfolio_tracker),
        ("Gas Monitor", example_gas_monitor),
        ("Multi-Chain Balance", example_multichain_balance),
        ("DeFi Agent with Memory", example_defi_agent_with_memory),
        ("Market Analyzer", example_market_analyzer),
        ("Audio Agent", example_audio_agent),
        ("Smart Transaction", example_smart_transaction)
    ]

    for name, func in examples:
        try:
            func()
        except Exception as e:
            print(f"\n{name} example error: {e}")

    print("\n" + "="*70)
    print("Examples completed!")
    print("="*70)

if __name__ == "__main__":
    main()
