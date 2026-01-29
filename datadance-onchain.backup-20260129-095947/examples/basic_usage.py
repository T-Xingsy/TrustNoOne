"""
Basic Usage Example for BSN-DDC SDK Integration

This example demonstrates the basic workflow of using the datadance-onchain plugin
to query and process on-chain data.
"""

import os
import sys

# Add scripts directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from init_sdk import initialize_bsn_ddc_sdk
from query_ddc import query_ddc_details, query_ddc_holders
from query_transactions import query_transaction_history, query_airdrop_transactions
from clean_onchain_data import clean_transaction_data, calculate_fulfillment_metrics
from format_for_llm import format_verification_context


def main():
    """
    Basic usage example
    """
    print("=" * 70)
    print("BSN-DDC SDK Integration - Basic Usage Example")
    print("=" * 70)
    print()

    # Step 1: Initialize SDK
    print("Step 1: Initialize BSN-DDC SDK")
    print("-" * 70)
    try:
        sdk = initialize_bsn_ddc_sdk()
        print("✓ SDK initialized successfully")
    except Exception as e:
        print(f"✗ Failed to initialize SDK: {e}")
        print("\nPlease ensure you have set the following environment variables:")
        print("  - BSN_DDC_GATEWAY_URL")
        print("  - BSN_DDC_API_KEY")
        return
    print()

    # Step 2: Query DDC Details
    print("Step 2: Query DDC Details")
    print("-" * 70)
    ddc_id = "12345"
    contract_address = "0xabc123def456"

    ddc_info = query_ddc_details(sdk, ddc_id, contract_address)
    print(f"DDC ID: {ddc_info['ddc_id']}")
    print(f"Owner: {ddc_info['owner']}")
    print(f"Created: {ddc_info['created_at']}")
    print(f"Token URI: {ddc_info['token_uri']}")
    print()

    # Step 3: Query Transaction History
    print("Step 3: Query Transaction History")
    print("-" * 70)
    start_date = "2024-04-01"
    end_date = "2024-06-30"

    transactions = query_transaction_history(
        sdk,
        contract_address,
        start_date,
        end_date,
        tx_types=["airdrop", "mint", "transfer"]
    )
    print(f"Found {len(transactions)} transactions")
    if transactions:
        print(f"First transaction: {transactions[0]['type']} at {transactions[0]['timestamp']}")
        print(f"Last transaction: {transactions[-1]['type']} at {transactions[-1]['timestamp']}")
    print()

    # Step 4: Analyze Airdrop Transactions
    print("Step 4: Analyze Airdrop Transactions")
    print("-" * 70)
    airdrop_analysis = query_airdrop_transactions(
        sdk,
        contract_address,
        start_date,
        end_date
    )
    print(f"Total airdrops: {airdrop_analysis['total_airdrops']}")
    print(f"Unique recipients: {airdrop_analysis['total_recipients']}")
    print(f"Total amount: {airdrop_analysis['total_amount']:,} tokens")
    print()

    # Step 5: Clean Transaction Data
    print("Step 5: Clean and Structure Data")
    print("-" * 70)
    cleaned_data = clean_transaction_data(
        airdrop_analysis['transactions'],
        promise_type="airdrop"
    )
    print(f"Evidence strength: {cleaned_data['evidence_strength']}")
    print(f"Summary: {cleaned_data['summary']}")
    print()

    # Step 6: Calculate Fulfillment Metrics
    print("Step 6: Calculate Fulfillment Metrics")
    print("-" * 70)
    # Assume promise was: "Airdrop 10,000 tokens to 100 holders"
    metrics = calculate_fulfillment_metrics(
        cleaned_data,
        promised_amount=10000,
        promised_recipients=100
    )
    if metrics['amount_fulfillment'] is not None:
        print(f"Amount fulfillment: {metrics['amount_fulfillment']:.1%}")
    if metrics['recipient_fulfillment'] is not None:
        print(f"Recipient fulfillment: {metrics['recipient_fulfillment']:.1%}")
    if metrics['overall_fulfillment'] is not None:
        print(f"Overall fulfillment: {metrics['overall_fulfillment']:.1%}")
    print()

    # Step 7: Format for LLM
    print("Step 7: Format Context for LLM")
    print("-" * 70)
    promise = {
        "content": "Q2 2024 airdrop 10,000 tokens to 100 holders",
        "timeline": {
            "mentioned": True,
            "end_date": "2024-06-30",
            "quarter": "Q2 2024"
        },
        "keywords": ["airdrop", "token", "holder"]
    }

    llm_context = format_verification_context(promise, cleaned_data)
    print(llm_context)
    print()

    print("=" * 70)
    print("✓ Basic usage example completed successfully!")
    print("=" * 70)


if __name__ == "__main__":
    main()
