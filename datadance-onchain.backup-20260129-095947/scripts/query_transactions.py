"""
Query Transaction History Module

This module provides functions to query on-chain transaction history
for DDC/NFT contracts, including mints, transfers, burns, and airdrops.

Usage:
    from scripts.query_transactions import query_transaction_history

    txs = query_transaction_history(
        sdk, "0xabc...", "2024-04-01", "2024-06-30", ["mint", "transfer"]
    )
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import random


def query_transaction_history(
    sdk: Any,
    contract_address: str,
    start_date: str,
    end_date: str,
    tx_types: Optional[List[str]] = None
) -> List[Dict[str, Any]]:
    """
    Query transaction history for a DDC contract within a date range

    Args:
        sdk: Initialized BSN-DDC SDK client
        contract_address: DDC contract address
        start_date: Start date (YYYY-MM-DD format)
        end_date: End date (YYYY-MM-DD format)
        tx_types: List of transaction types to filter
                  Options: ["mint", "transfer", "burn", "airdrop", "deploy"]
                  If None, returns all types

    Returns:
        List of transactions:
        [
            {
                "tx_hash": str,
                "type": str,
                "from": str,
                "to": str,
                "amount": int,
                "ddc_id": str,
                "timestamp": str,
                "block_number": int
            },
            ...
        ]

    Example:
        >>> txs = query_transaction_history(
        ...     sdk, "0xabc...", "2024-04-01", "2024-06-30", ["airdrop"]
        ... )
        >>> print(f"Found {len(txs)} airdrop transactions")
    """
    # TODO: Replace with actual BSN-DDC SDK call
    # In production: sdk.getTransactionHistory(contract_address, start_date, end_date)

    # Mock implementation for MVP
    tx_types = tx_types or ["mint", "transfer", "burn", "airdrop"]

    # Generate mock transactions
    mock_transactions = []

    # Parse dates
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    days = (end - start).days

    # Generate some mock transactions
    for i in range(min(days, 20)):  # Max 20 transactions
        tx_date = start + timedelta(days=i)
        tx_type = random.choice(tx_types)

        mock_transactions.append({
            "tx_hash": f"0x{random.randint(0, 2**256):064x}",
            "type": tx_type,
            "from": f"0x{random.randint(0, 2**160):040x}",
            "to": f"0x{random.randint(0, 2**160):040x}",
            "amount": random.randint(1, 1000),
            "ddc_id": str(random.randint(1, 10000)),
            "timestamp": tx_date.isoformat() + "Z",
            "block_number": 1000000 + i
        })

    return mock_transactions


def query_airdrop_transactions(
    sdk: Any,
    contract_address: str,
    start_date: str,
    end_date: str
) -> Dict[str, Any]:
    """
    Query and analyze airdrop transactions

    Args:
        sdk: Initialized BSN-DDC SDK client
        contract_address: DDC contract address
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)

    Returns:
        Airdrop analysis:
        {
            "total_airdrops": int,
            "total_recipients": int,
            "total_amount": int,
            "transactions": List[Dict],
            "date_range": {"start": str, "end": str}
        }

    Example:
        >>> analysis = query_airdrop_transactions(sdk, "0xabc...", "2024-04-01", "2024-06-30")
        >>> print(f"Total recipients: {analysis['total_recipients']}")
    """
    # Query airdrop transactions
    txs = query_transaction_history(
        sdk, contract_address, start_date, end_date, ["airdrop"]
    )

    # Analyze
    unique_recipients = set(tx["to"] for tx in txs)
    total_amount = sum(tx["amount"] for tx in txs)

    return {
        "total_airdrops": len(txs),
        "total_recipients": len(unique_recipients),
        "total_amount": total_amount,
        "transactions": txs,
        "date_range": {"start": start_date, "end": end_date}
    }


def query_mint_transactions(
    sdk: Any,
    contract_address: str,
    start_date: str,
    end_date: str
) -> Dict[str, Any]:
    """
    Query and analyze mint transactions

    Args:
        sdk: Initialized BSN-DDC SDK client
        contract_address: DDC contract address
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)

    Returns:
        Mint analysis:
        {
            "total_mints": int,
            "total_minted": int,
            "first_mint_date": str,
            "last_mint_date": str,
            "transactions": List[Dict]
        }

    Example:
        >>> analysis = query_mint_transactions(sdk, "0xabc...", "2024-01-01", "2024-12-31")
        >>> print(f"Total minted: {analysis['total_minted']}")
    """
    # Query mint transactions
    txs = query_transaction_history(
        sdk, contract_address, start_date, end_date, ["mint"]
    )

    if not txs:
        return {
            "total_mints": 0,
            "total_minted": 0,
            "first_mint_date": None,
            "last_mint_date": None,
            "transactions": []
        }

    # Sort by timestamp
    sorted_txs = sorted(txs, key=lambda x: x["timestamp"])

    return {
        "total_mints": len(txs),
        "total_minted": sum(tx["amount"] for tx in txs),
        "first_mint_date": sorted_txs[0]["timestamp"],
        "last_mint_date": sorted_txs[-1]["timestamp"],
        "transactions": txs
    }


def filter_transactions_by_type(
    transactions: List[Dict[str, Any]],
    tx_type: str
) -> List[Dict[str, Any]]:
    """
    Filter transactions by type

    Args:
        transactions: List of transactions
        tx_type: Transaction type to filter

    Returns:
        Filtered list of transactions

    Example:
        >>> all_txs = query_transaction_history(sdk, "0xabc...", "2024-01-01", "2024-12-31")
        >>> airdrops = filter_transactions_by_type(all_txs, "airdrop")
    """
    return [tx for tx in transactions if tx["type"] == tx_type]


if __name__ == "__main__":
    # Test transaction queries
    print("Testing transaction query functions...")
    print()

    from init_sdk import initialize_bsn_ddc_sdk

    try:
        sdk = initialize_bsn_ddc_sdk()
        print()

        # Test general transaction query
        print("1. Query all transactions:")
        txs = query_transaction_history(
            sdk, "0xabc123", "2024-04-01", "2024-06-30"
        )
        print(f"   Found {len(txs)} transactions")
        if txs:
            print(f"   First tx: {txs[0]['type']} at {txs[0]['timestamp']}")
        print()

        # Test airdrop analysis
        print("2. Analyze airdrops:")
        airdrop_analysis = query_airdrop_transactions(
            sdk, "0xabc123", "2024-04-01", "2024-06-30"
        )
        print(f"   Total airdrops: {airdrop_analysis['total_airdrops']}")
        print(f"   Recipients: {airdrop_analysis['total_recipients']}")
        print(f"   Total amount: {airdrop_analysis['total_amount']}")
        print()

        # Test mint analysis
        print("3. Analyze mints:")
        mint_analysis = query_mint_transactions(
            sdk, "0xabc123", "2024-01-01", "2024-12-31"
        )
        print(f"   Total mints: {mint_analysis['total_mints']}")
        print(f"   Total minted: {mint_analysis['total_minted']}")

    except Exception as e:
        print(f"✗ Test failed: {e}")
