"""
Agent Integration Example

This example demonstrates how to integrate the datadance-onchain plugin
with SpoonOS agents for the Promise Breaker Detector project.
"""

import os
import sys
from typing import Dict, Any, List

# Add scripts directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from init_sdk import initialize_bsn_ddc_sdk
from query_transactions import query_transaction_history
from clean_onchain_data import clean_transaction_data
from format_for_llm import format_verification_context


class OnChainQueryTool:
    """
    OnChainQueryTool integrated with BSN-DDC SDK

    This tool can be used in SpoonOS agents to query and verify
    on-chain evidence for promise verification.
    """

    def __init__(self):
        """Initialize the tool with BSN-DDC SDK"""
        self.sdk = initialize_bsn_ddc_sdk()
        self.name = "onchain_query"
        self.description = "Query on-chain behavior for promise verification"

    async def execute(
        self,
        contract_address: str,
        start_date: str,
        end_date: str,
        query_type: str
    ) -> Dict[str, Any]:
        """
        Execute on-chain query

        Args:
            contract_address: DDC/NFT contract address
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            query_type: Type of query (airdrop/mint/transfer/burn)

        Returns:
            Dictionary with query results and cleaned evidence
        """
        # 1. Query raw transactions
        raw_transactions = query_transaction_history(
            sdk=self.sdk,
            contract_address=contract_address,
            start_date=start_date,
            end_date=end_date,
            tx_types=[query_type]
        )

        # 2. Clean and structure data
        cleaned_evidence = clean_transaction_data(
            raw_transactions=raw_transactions,
            promise_type=query_type
        )

        # 3. Return structured result
        return {
            "found": len(raw_transactions) > 0,
            "evidence": cleaned_evidence,
            "raw_transaction_count": len(raw_transactions),
            "evidence_strength": cleaned_evidence.get("evidence_strength", "none")
        }


class VerificationAgentExample:
    """
    Example VerificationAgent using OnChainQueryTool

    This demonstrates how to integrate the tool into a SpoonOS ReAct agent
    for promise verification.
    """

    def __init__(self):
        """Initialize agent with tools"""
        self.onchain_tool = OnChainQueryTool()
        self.name = "VerificationAgent"

    async def verify_promise(
        self,
        promise: Dict[str, Any],
        contract_address: str
    ) -> Dict[str, Any]:
        """
        Verify a single promise against on-chain evidence

        Args:
            promise: Promise object with content and timeline
            contract_address: Contract address to query

        Returns:
            Verification result with score and reasoning
        """
        print(f"\n{'='*70}")
        print(f"Verifying Promise: {promise['content']}")
        print(f"{'='*70}\n")

        # Extract timeline from promise
        timeline = promise.get("timeline", {})
        start_date = timeline.get("start_date", "2024-01-01")
        end_date = timeline.get("end_date", "2024-12-31")

        # Determine query type from promise keywords
        keywords = promise.get("keywords", [])
        query_type = self._determine_query_type(keywords)

        print(f"Step 1: Query on-chain data")
        print(f"  Contract: {contract_address}")
        print(f"  Date range: {start_date} to {end_date}")
        print(f"  Query type: {query_type}")
        print()

        # Query on-chain evidence
        query_result = await self.onchain_tool.execute(
            contract_address=contract_address,
            start_date=start_date,
            end_date=end_date,
            query_type=query_type
        )

        print(f"Step 2: Analyze evidence")
        print(f"  Found: {query_result['found']}")
        print(f"  Transactions: {query_result['raw_transaction_count']}")
        print(f"  Strength: {query_result['evidence_strength']}")
        print()

        # Format context for LLM
        llm_context = format_verification_context(
            promise=promise,
            evidence=query_result['evidence']
        )

        print(f"Step 3: Format context for LLM")
        print(f"  Context length: {len(llm_context)} characters")
        print()

        # Calculate fulfillment score
        fulfillment_rate = self._calculate_fulfillment(query_result)

        print(f"Step 4: Calculate score")
        print(f"  Fulfillment rate: {fulfillment_rate:.1%}")
        print()

        # Generate verification result
        result = {
            "promise_id": promise.get("id", "unknown"),
            "promise_content": promise["content"],
            "evidence_found": query_result["found"],
            "evidence_strength": query_result["evidence_strength"],
            "fulfillment_rate": fulfillment_rate,
            "score": self._calculate_score(fulfillment_rate, impact_score=85),
            "reasoning": self._generate_reasoning(promise, query_result, fulfillment_rate),
            "llm_context": llm_context
        }

        print(f"{'='*70}")
        print(f"Verification Result:")
        print(f"  Score: {result['score']:.1f}")
        print(f"  Fulfillment: {result['fulfillment_rate']:.1%}")
        print(f"  Reasoning: {result['reasoning']}")
        print(f"{'='*70}\n")

        return result

    def _determine_query_type(self, keywords: List[str]) -> str:
        """Determine query type from promise keywords"""
        keyword_mapping = {
            "airdrop": "airdrop",
            "mint": "mint",
            "launch": "mint",
            "transfer": "transfer",
            "burn": "burn",
            "staking": "transfer"
        }

        for keyword in keywords:
            if keyword.lower() in keyword_mapping:
                return keyword_mapping[keyword.lower()]

        return "transfer"  # Default

    def _calculate_fulfillment(self, query_result: Dict[str, Any]) -> float:
        """Calculate fulfillment rate from query result"""
        if not query_result["found"]:
            return 0.0

        evidence = query_result["evidence"]
        strength = evidence.get("evidence_strength", "none")

        # Simple mapping of strength to fulfillment rate
        strength_mapping = {
            "strong": 1.0,
            "moderate": 0.7,
            "weak": 0.3,
            "none": 0.0
        }

        return strength_mapping.get(strength, 0.0)

    def _calculate_score(self, fulfillment_rate: float, impact_score: float) -> float:
        """Calculate final score"""
        if fulfillment_rate >= 0.7:
            # Fulfilled: positive score
            return impact_score * fulfillment_rate
        else:
            # Unfulfilled: negative score (penalty)
            return -impact_score * (1.0 - fulfillment_rate) * 1.5

    def _generate_reasoning(
        self,
        promise: Dict[str, Any],
        query_result: Dict[str, Any],
        fulfillment_rate: float
    ) -> str:
        """Generate human-readable reasoning"""
        if not query_result["found"]:
            return f"No on-chain evidence found for the promised {promise.get('keywords', ['activity'])[0]}. Promise appears unfulfilled."

        evidence = query_result["evidence"]
        summary = evidence.get("summary", "")

        if fulfillment_rate >= 0.9:
            return f"Strong evidence of fulfillment. {summary}"
        elif fulfillment_rate >= 0.5:
            return f"Partial fulfillment detected. {summary}"
        else:
            return f"Minimal fulfillment. {summary}"


async def main():
    """
    Main example demonstrating agent integration
    """
    print("\n" + "=" * 70)
    print("Agent Integration Example - Promise Verification")
    print("=" * 70)

    # Initialize agent
    agent = VerificationAgentExample()

    # Example promise
    promise = {
        "id": "promise_1",
        "content": "Q2 2024 airdrop to all holders",
        "timeline": {
            "mentioned": True,
            "start_date": "2024-04-01",
            "end_date": "2024-06-30",
            "quarter": "Q2 2024"
        },
        "keywords": ["airdrop", "holder"]
    }

    # Contract address (mock)
    contract_address = "0xabc123def456789"

    # Verify promise
    result = await agent.verify_promise(promise, contract_address)

    # Display final result
    print("\n" + "=" * 70)
    print("FINAL VERIFICATION RESULT")
    print("=" * 70)
    print(f"Promise: {result['promise_content']}")
    print(f"Score: {result['score']:.1f}")
    print(f"Fulfillment: {result['fulfillment_rate']:.1%}")
    print(f"Evidence: {result['evidence_strength']}")
    print(f"\nReasoning:")
    print(f"  {result['reasoning']}")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
