"""
Simple ChatBot Example - Pure spoon-core Usage

This example demonstrates the most basic SpoonOS agent: a conversational chatbot
that doesn't use any tools, only LLM interactions.

Use case: Customer support, general Q&A, conversational interfaces
"""

from spoon_ai_sdk.agents import ChatBot
from spoon_ai_sdk.llm import LLMManager
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_simple_chatbot():
    """Create a basic chatbot using only spoon-core"""

    # Initialize LLM
    llm = LLMManager(
        provider="openai",  # or "anthropic", "ollama"
        model="gpt-4",
        api_key=os.getenv("OPENAI_API_KEY"),
        temperature=0.7,
        max_tokens=1000
    )

    # Create chatbot with system prompt
    system_prompt = """You are a helpful AI assistant.

    Your role is to:
    - Answer questions clearly and concisely
    - Be friendly and professional
    - Admit when you don't know something
    - Ask clarifying questions when needed
    """

    agent = ChatBot(
        llm=llm,
        system_prompt=system_prompt
    )

    return agent

def main():
    """Run interactive chatbot session"""
    print("=== Simple SpoonOS ChatBot ===")
    print("Type 'quit' to exit\n")

    # Create agent
    agent = create_simple_chatbot()

    # Interactive loop
    while True:
        user_input = input("You: ").strip()

        if user_input.lower() in ['quit', 'exit', 'q']:
            print("Goodbye!")
            break

        if not user_input:
            continue

        try:
            # Get response from agent
            response = agent.run(user_input)
            print(f"Agent: {response}\n")

        except Exception as e:
            print(f"Error: {e}\n")

if __name__ == "__main__":
    main()
