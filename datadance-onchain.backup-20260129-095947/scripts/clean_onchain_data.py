"""
On-Chain Data Cleaning Module

This module provides functions to clean and structure raw blockchain transaction data
into formats suitable for LLM analysis and promise verification.

Usage:
    from scripts.clean_onchain_data import clean_transaction_data

    cleaned = clean_transaction_data(raw_transactions, promise_type="airdrop")
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
from collections import defaultdict


def clean_transaction_data(
    raw_transactions: List[Dict[str, Any]],
    promise_type: str
) -> Dict[str, Any]:
    """
    Clean and structure raw transaction data

    Args:
        raw_transactions: List of raw transaction dictionaries
        promise_type: Type of promise being verified
                      Options: "airdrop", "mint", "transfer", "burn", "staking"

    Returns:
        Structured evidence dictionary:
        {
            "type": str,
            "total_transactions": int,
            "total_recipients": int,
            "total_amount": int,
            "date_range": {"start": str, "end": str},
            "evidence_strength": str,  # "strong", "moderate", "weak", "none"
            "summary": str
        }

    Example:
        >>> raw_txs = query_transaction_history(...)
        >>> cleaned = clean_transaction_data(raw_txs, "airdrop")
        >>> print(cleaned["evidence_strength"])
        'strong'
    """
    if not raw_transactions:
        return {
            "type": promise_type,
            "total_transactions": 0,
            "total_recipients": 0,
            "total_amount": 0,
            "date_range": {"start": None, "end": None},
            "evidence_strength": "none",
            "summary": f"No {promise_type} transactions found"
        }

    # Extract unique recipients
    recipients = set()
    total_amount = 0
    dates = []

    for tx in raw_transactions:
        if tx.get("to"):
            recipients.add(tx["to"])
        if tx.get("amount"):
            total_amount += tx["amount"]
        if tx.get("timestamp"):
            dates.append(tx["timestamp"])

    # Determine date range
    if dates:
        dates.sort()
        start_date = dates[0]
        end_date = dates[-1]
    else:
        start_date = None
        end_date = None

    # Assess evidence strength
    evidence_strength = _assess_evidence_strength(
        len(raw_transactions),
        len(recipients),
        promise_type
    )

    # Generate summary
    summary = _generate_summary(
        promise_type,
        len(raw_transactions),
        len(recipients),
        total_amount,
        start_date,
        end_date
    )

    return {
        "type": promise_type,
        "total_transactions": len(raw_transactions),
        "total_recipients": len(recipients),
        "total_amount": total_amount,
        "date_range": {"start": start_date, "end": end_date},
        "evidence_strength": evidence_strength,
        "summary": summary,
        "raw_transaction_count": len(raw_transactions)
    }


def _assess_evidence_strength(
    tx_count: int,
    recipient_count: int,
    promise_type: str
) -> str:
    """
    Assess the strength of on-chain evidence

    Args:
        tx_count: Number of transactions
        recipient_count: Number of unique recipients
        promise_type: Type of promise

    Returns:
        Evidence strength: "strong", "moderate", "weak", or "none"
    """
    if tx_count == 0:
        return "none"
    elif tx_count >= 100 and recipient_count >= 50:
        return "strong"
    elif tx_count >= 10 and recipient_count >= 5:
        return "moderate"
    else:
        return "weak"


def _generate_summary(
    promise_type: str,
    tx_count: int,
    recipient_count: int,
    total_amount: int,
    start_date: Optional[str],
    end_date: Optional[str]
) -> str:
    """
    Generate a human-readable summary of the evidence

    Args:
        promise_type: Type of promise
        tx_count: Number of transactions
        recipient_count: Number of recipients
        total_amount: Total amount transferred
        start_date: Start date of transactions
        end_date: End date of transactions

    Returns:
        Summary string
    """
    if tx_count == 0:
        return f"No {promise_type} activity found on-chain"

    date_str = ""
    if start_date and end_date:
        if start_date == end_date:
            date_str = f" on {start_date[:10]}"
        else:
            date_str = f" from {start_date[:10]} to {end_date[:10]}"

    return (
        f"Found {tx_count} {promise_type} transaction(s) "
        f"to {recipient_count} unique recipient(s), "
        f"totaling {total_amount:,} tokens{date_str}"
    )


def aggregate_by_date(
    transactions: List[Dict[str, Any]]
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Aggregate transactions by date

    Args:
        transactions: List of transactions

    Returns:
        Dictionary mapping dates to transaction lists

    Example:
        >>> by_date = aggregate_by_date(transactions)
        >>> print(f"Transactions on 2024-05-15: {len(by_date['2024-05-15'])}")
    """
    aggregated = defaultdict(list)

    for tx in transactions:
        if tx.get("timestamp"):
            date = tx["timestamp"][:10]  # Extract YYYY-MM-DD
            aggregated[date].append(tx)

    return dict(aggregated)


def aggregate_by_recipient(
    transactions: List[Dict[str, Any]]
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Aggregate transactions by recipient address

    Args:
        transactions: List of transactions

    Returns:
        Dictionary mapping recipient addresses to transaction lists

    Example:
        >>> by_recipient = aggregate_by_recipient(transactions)
        >>> top_recipient = max(by_recipient.items(), key=lambda x: len(x[1]))
        >>> print(f"Top recipient: {top_recipient[0]} with {len(top_recipient[1])} txs")
    """
    aggregated = defaultdict(list)

    for tx in transactions:
        if tx.get("to"):
            aggregated[tx["to"]].append(tx)

    return dict(aggregated)


def calculate_fulfillment_metrics(
    cleaned_data: Dict[str, Any],
    promised_amount: Optional[int] = None,
    promised_recipients: Optional[int] = None
) -> Dict[str, Any]:
    """
    Calculate fulfillment metrics by comparing actual vs promised

    Args:
        cleaned_data: Cleaned transaction data
        promised_amount: Promised total amount (optional)
        promised_recipients: Promised number of recipients (optional)

    Returns:
        Fulfillment metrics:
        {
            "amount_fulfillment": float,  # 0.0 to 1.0
            "recipient_fulfillment": float,  # 0.0 to 1.0
            "overall_fulfillment": float  # 0.0 to 1.0
        }

    Example:
        >>> metrics = calculate_fulfillment_metrics(
        ...     cleaned_data,
        ...     promised_amount=10000,
        ...     promised_recipients=100
        ... )
        >>> print(f"Overall fulfillment: {metrics['overall_fulfillment']:.1%}")
    """
    metrics = {
        "amount_fulfillment": None,
        "recipient_fulfillment": None,
        "overall_fulfillment": None
    }

    # Calculate amount fulfillment
    if promised_amount and promised_amount > 0:
        actual_amount = cleaned_data.get("total_amount", 0)
        metrics["amount_fulfillment"] = min(actual_amount / promised_amount, 1.0)

    # Calculate recipient fulfillment
    if promised_recipients and promised_recipients > 0:
        actual_recipients = cleaned_data.get("total_recipients", 0)
        metrics["recipient_fulfillment"] = min(actual_recipients / promised_recipients, 1.0)

    # Calculate overall fulfillment
    fulfillments = [v for v in [metrics["amount_fulfillment"], metrics["recipient_fulfillment"]] if v is not None]
    if fulfillments:
        metrics["overall_fulfillment"] = sum(fulfillments) / len(fulfillments)

    return metrics


if __name__ == "__main__":
    # Test data cleaning
    print("Testing data cleaning functions...")
    print()

    # Mock raw transactions
    mock_transactions = [
        {
            "tx_hash": "0x123...",
            "type": "airdrop",
            "from": "0xaaa...",
            "to": "0xbbb...",
            "amount": 100,
            "timestamp": "2024-05-15T10:30:00Z"
        },
        {
            "tx_hash": "0x456...",
            "type": "airdrop",
            "from": "0xaaa...",
            "to": "0xccc...",
            "amount": 100,
            "timestamp": "2024-05-15T10:31:00Z"
        },
        {
            "tx_hash": "0x789...",
            "type": "airdrop",
            "from": "0xaaa...",
            "to": "0xddd...",
            "amount": 100,
            "timestamp": "2024-05-16T09:00:00Z"
        }
    ]

    # Test cleaning
    print("1. Clean transaction data:")
    cleaned = clean_transaction_data(mock_transactions, "airdrop")
    print(f"   Type: {cleaned['type']}")
    print(f"   Total transactions: {cleaned['total_transactions']}")
    print(f"   Total recipients: {cleaned['total_recipients']}")
    print(f"   Total amount: {cleaned['total_amount']}")
    print(f"   Evidence strength: {cleaned['evidence_strength']}")
    print(f"   Summary: {cleaned['summary']}")
    print()

    # Test fulfillment metrics
    print("2. Calculate fulfillment metrics:")
    metrics = calculate_fulfillment_metrics(
        cleaned,
        promised_amount=1000,
        promised_recipients=10
    )
    print(f"   Amount fulfillment: {metrics['amount_fulfillment']:.1%}")
    print(f"   Recipient fulfillment: {metrics['recipient_fulfillment']:.1%}")
    print(f"   Overall fulfillment: {metrics['overall_fulfillment']:.1%}")
    print()

    # Test aggregation
    print("3. Aggregate by date:")
    by_date = aggregate_by_date(mock_transactions)
    for date, txs in by_date.items():
        print(f"   {date}: {len(txs)} transactions")
