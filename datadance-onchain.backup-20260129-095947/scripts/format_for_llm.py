"""
LLM Context Formatting Module

This module provides functions to format cleaned on-chain data into
optimized context strings for LLM analysis in the VerificationAgent.

Usage:
    from scripts.format_for_llm import format_verification_context

    context = format_verification_context(promise, evidence)
"""

from typing import Dict, Any, Optional, List


def format_verification_context(
    promise: Dict[str, Any],
    evidence: Dict[str, Any],
    include_analysis: bool = True
) -> str:
    """
    Format promise and evidence into LLM-friendly context

    Args:
        promise: Promise object with content and timeline
        evidence: Cleaned on-chain evidence data
        include_analysis: Whether to include preliminary analysis

    Returns:
        Formatted context string optimized for LLM

    Example:
        >>> context = format_verification_context(
        ...     promise={"content": "Q2 airdrop", "timeline": {"end_date": "2024-06-30"}},
        ...     evidence=cleaned_data
        ... )
        >>> print(context)
    """
    sections = []

    # Section 1: Promise Details
    sections.append(_format_promise_section(promise))

    # Section 2: On-Chain Evidence
    sections.append(_format_evidence_section(evidence))

    # Section 3: Preliminary Analysis (optional)
    if include_analysis:
        sections.append(_format_analysis_section(promise, evidence))

    return "\n\n".join(sections)


def _format_promise_section(promise: Dict[str, Any]) -> str:
    """Format the promise section"""
    content = promise.get("content", "Unknown promise")
    timeline = promise.get("timeline", {})

    lines = [
        "=== PROMISE ===",
        f"Content: {content}"
    ]

    # Add timeline if available
    if timeline.get("mentioned"):
        if timeline.get("end_date"):
            lines.append(f"Deadline: {timeline['end_date']}")
        if timeline.get("quarter"):
            lines.append(f"Quarter: {timeline['quarter']}")

    # Add keywords if available
    if promise.get("keywords"):
        keywords_str = ", ".join(promise["keywords"])
        lines.append(f"Keywords: {keywords_str}")

    return "\n".join(lines)


def _format_evidence_section(evidence: Dict[str, Any]) -> str:
    """Format the evidence section"""
    lines = [
        "=== ON-CHAIN EVIDENCE ==="
    ]

    # Evidence type
    lines.append(f"Type: {evidence.get('type', 'unknown')}")

    # Transaction count
    tx_count = evidence.get("total_transactions", 0)
    lines.append(f"Transactions Found: {tx_count}")

    if tx_count > 0:
        # Recipients
        recipient_count = evidence.get("total_recipients", 0)
        lines.append(f"Unique Recipients: {recipient_count}")

        # Amount
        total_amount = evidence.get("total_amount", 0)
        lines.append(f"Total Amount: {total_amount:,} tokens")

        # Date range
        date_range = evidence.get("date_range", {})
        if date_range.get("start") and date_range.get("end"):
            start = date_range["start"][:10]
            end = date_range["end"][:10]
            if start == end:
                lines.append(f"Date: {start}")
            else:
                lines.append(f"Date Range: {start} to {end}")

        # Evidence strength
        strength = evidence.get("evidence_strength", "unknown")
        lines.append(f"Evidence Strength: {strength}")

        # Summary
        if evidence.get("summary"):
            lines.append(f"\nSummary: {evidence['summary']}")
    else:
        lines.append("\nNo on-chain activity found matching the promise criteria.")

    return "\n".join(lines)


def _format_analysis_section(
    promise: Dict[str, Any],
    evidence: Dict[str, Any]
) -> str:
    """Format the preliminary analysis section"""
    lines = [
        "=== PRELIMINARY ANALYSIS ==="
    ]

    # Timing analysis
    timing_analysis = _analyze_timing(promise, evidence)
    if timing_analysis:
        lines.append(f"Timing: {timing_analysis}")

    # Quantity analysis
    quantity_analysis = _analyze_quantity(promise, evidence)
    if quantity_analysis:
        lines.append(f"Quantity: {quantity_analysis}")

    # Coverage analysis
    coverage_analysis = _analyze_coverage(promise, evidence)
    if coverage_analysis:
        lines.append(f"Coverage: {coverage_analysis}")

    # Overall assessment
    overall = _assess_overall(evidence)
    lines.append(f"\nOverall: {overall}")

    return "\n".join(lines)


def _analyze_timing(
    promise: Dict[str, Any],
    evidence: Dict[str, Any]
) -> Optional[str]:
    """Analyze timing fulfillment"""
    timeline = promise.get("timeline", {})
    date_range = evidence.get("date_range", {})

    if not timeline.get("end_date") or not date_range.get("end"):
        return None

    promised_end = timeline["end_date"]
    actual_end = date_range["end"][:10]

    if actual_end <= promised_end:
        return f"On time (completed by {actual_end})"
    else:
        return f"Delayed (completed {actual_end}, promised by {promised_end})"


def _analyze_quantity(
    promise: Dict[str, Any],
    evidence: Dict[str, Any]
) -> Optional[str]:
    """Analyze quantity fulfillment"""
    # This is a simplified analysis
    # In production, extract promised amounts from promise content
    tx_count = evidence.get("total_transactions", 0)
    total_amount = evidence.get("total_amount", 0)

    if tx_count == 0:
        return "No tokens distributed"
    elif total_amount > 0:
        return f"{total_amount:,} tokens distributed across {tx_count} transaction(s)"
    else:
        return f"{tx_count} transaction(s) found"


def _analyze_coverage(
    promise: Dict[str, Any],
    evidence: Dict[str, Any]
) -> Optional[str]:
    """Analyze coverage fulfillment"""
    recipient_count = evidence.get("total_recipients", 0)

    if recipient_count == 0:
        return "No recipients"
    else:
        # Check if promise mentions "all holders"
        content = promise.get("content", "").lower()
        if "all" in content or "every" in content:
            return f"{recipient_count} recipients (verify if this covers 'all' as promised)"
        else:
            return f"{recipient_count} recipients"


def _assess_overall(evidence: Dict[str, Any]) -> str:
    """Provide overall assessment"""
    tx_count = evidence.get("total_transactions", 0)
    strength = evidence.get("evidence_strength", "none")

    if tx_count == 0:
        return "No on-chain evidence found - likely unfulfilled"
    elif strength == "strong":
        return "Strong on-chain evidence - likely fulfilled"
    elif strength == "moderate":
        return "Moderate on-chain evidence - partially fulfilled"
    else:
        return "Weak on-chain evidence - minimally fulfilled"


def format_compact_context(
    promise: Dict[str, Any],
    evidence: Dict[str, Any],
    max_length: int = 500
) -> str:
    """
    Format a compact version of the context for token-limited scenarios

    Args:
        promise: Promise object
        evidence: Evidence data
        max_length: Maximum character length

    Returns:
        Compact context string

    Example:
        >>> compact = format_compact_context(promise, evidence, max_length=200)
    """
    content = promise.get("content", "Unknown")
    tx_count = evidence.get("total_transactions", 0)
    recipients = evidence.get("total_recipients", 0)
    amount = evidence.get("total_amount", 0)

    if tx_count == 0:
        context = f"Promise: {content}\nEvidence: None found"
    else:
        context = (
            f"Promise: {content}\n"
            f"Evidence: {tx_count} txs, {recipients} recipients, {amount:,} tokens"
        )

    # Truncate if needed
    if len(context) > max_length:
        context = context[:max_length-3] + "..."

    return context


def format_for_scoring(
    promise: Dict[str, Any],
    evidence: Dict[str, Any],
    impact_score: float,
    complexity_score: float
) -> str:
    """
    Format context specifically for the scoring phase

    Args:
        promise: Promise object
        evidence: Evidence data
        impact_score: Impact assessment score (0-100)
        complexity_score: Complexity assessment score (0-100)

    Returns:
        Formatted context for scoring

    Example:
        >>> context = format_for_scoring(promise, evidence, 85, 70)
    """
    lines = [
        "=== SCORING CONTEXT ===",
        "",
        f"Promise: {promise.get('content', 'Unknown')}",
        f"Impact Score: {impact_score}/100",
        f"Complexity Score: {complexity_score}/100",
        "",
        "Evidence Summary:",
        f"- Transactions: {evidence.get('total_transactions', 0)}",
        f"- Recipients: {evidence.get('total_recipients', 0)}",
        f"- Amount: {evidence.get('total_amount', 0):,} tokens",
        f"- Strength: {evidence.get('evidence_strength', 'unknown')}",
        "",
        "Recommendation:",
        _generate_scoring_recommendation(evidence, impact_score)
    ]

    return "\n".join(lines)


def _generate_scoring_recommendation(
    evidence: Dict[str, Any],
    impact_score: float
) -> str:
    """Generate scoring recommendation"""
    tx_count = evidence.get("total_transactions", 0)

    if tx_count == 0:
        return f"Unfulfilled promise with high impact ({impact_score}/100) - apply negative score"
    elif evidence.get("evidence_strength") == "strong":
        return f"Strong evidence of fulfillment - apply positive score based on impact"
    else:
        return f"Partial fulfillment - apply proportional score"


if __name__ == "__main__":
    # Test formatting
    print("Testing LLM context formatting...")
    print()

    # Mock data
    mock_promise = {
        "content": "Q2 2024 airdrop 1000 tokens to all holders",
        "timeline": {
            "mentioned": True,
            "end_date": "2024-06-30",
            "quarter": "Q2 2024"
        },
        "keywords": ["airdrop", "token", "holder"]
    }

    mock_evidence = {
        "type": "airdrop",
        "total_transactions": 15,
        "total_recipients": 500,
        "total_amount": 500000,
        "date_range": {
            "start": "2024-05-15T10:00:00Z",
            "end": "2024-05-15T12:00:00Z"
        },
        "evidence_strength": "strong",
        "summary": "Found 15 airdrop transactions to 500 recipients, totaling 500,000 tokens"
    }

    # Test full context
    print("1. Full verification context:")
    print("-" * 60)
    context = format_verification_context(mock_promise, mock_evidence)
    print(context)
    print("-" * 60)
    print()

    # Test compact context
    print("2. Compact context:")
    compact = format_compact_context(mock_promise, mock_evidence, max_length=200)
    print(compact)
    print()

    # Test scoring context
    print("3. Scoring context:")
    print("-" * 60)
    scoring_context = format_for_scoring(mock_promise, mock_evidence, 85, 70)
    print(scoring_context)
    print("-" * 60)
