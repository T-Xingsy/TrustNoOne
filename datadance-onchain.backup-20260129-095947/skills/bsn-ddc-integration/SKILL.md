---
name: bsn-ddc-integration
description: Provides comprehensive guidance on integrating BSN-DDC SDK for on-chain data querying and preprocessing in the Promise Breaker Detector project. Covers SDK initialization, DDC/NFT data queries, transaction history retrieval, and data cleaning for LLM context preparation.
---

# BSN-DDC SDK Integration Guide

This skill provides guidance on using the BSN-DDC SDK (@ddcmarket/sdk) to query on-chain DDC/NFT data and preprocess it for the Promise Breaker Detector project's verification agents.

## Overview

The BSN-DDC SDK is the official toolkit for China's Blockchain Service Network (BSN) Distributed Digital Certificate (DDC) platform. DDC is similar to NFT and represents digital assets on blockchain.

**Core Capabilities**:
- Query DDC/NFT details and ownership
- Retrieve transaction history (mint, transfer, burn)
- Account management and authorization
- Support for multiple open consortium chains

**Important**: The SDK does NOT include data cleaning functionality. You must implement data preprocessing separately.

## Quick Start

### 1. SDK Initialization

Use the `init_sdk.py` script to configure the SDK:

```python
from scripts.init_sdk import initialize_bsn_ddc_sdk

# Initialize with environment variables
sdk = initialize_bsn_ddc_sdk(
    gateway_url=os.getenv('BSN_DDC_GATEWAY_URL'),
    api_key=os.getenv('BSN_DDC_API_KEY')
)
```

**Required Configuration**:
- `BSN_DDC_GATEWAY_URL`: Gateway endpoint (obtain from ddc.bsnbase.com)
- `BSN_DDC_API_KEY`: API token (found in "Business Information" section)

### 2. Query DDC Data

Use `query_ddc.py` to retrieve DDC information:

```python
from scripts.query_ddc import query_ddc_details

# Query DDC details
ddc_info = query_ddc_details(
    sdk=sdk,
    ddc_id="12345",
    contract_address="0x..."
)

# Returns: {
#   "owner": "0x...",
#   "metadata": {...},
#   "token_uri": "https://...",
#   "created_at": "2024-01-15"
# }
```

### 3. Query Transaction History

Use `query_transactions.py` to retrieve on-chain evidence:

```python
from scripts.query_transactions import query_transaction_history

# Query transactions in date range
transactions = query_transaction_history(
    sdk=sdk,
    contract_address="0x...",
    start_date="2024-04-01",
    end_date="2024-06-30",
    tx_types=["mint", "transfer", "airdrop"]
)

# Returns: [
#   {
#     "tx_hash": "0x123...",
#     "type": "mint",
#     "from": "0x...",
#     "to": "0x...",
#     "amount": 1000,
#     "timestamp": "2024-05-15T10:30:00Z"
#   },
#   ...
# ]
```

## Data Preprocessing for LLM

### 4. Clean On-Chain Data

Use `clean_onchain_data.py` to structure raw blockchain data:

```python
from scripts.clean_onchain_data import clean_transaction_data

# Clean raw transactions
cleaned_data = clean_transaction_data(
    raw_transactions=transactions,
    promise_type="airdrop"
)

# Returns: {
#   "type": "airdrop",
#   "total_recipients": 500,
#   "total_amount": 500000,
#   "date_range": {"start": "2024-05-01", "end": "2024-05-31"},
#   "evidence_strength": "strong"
# }
```

### 5. Format for LLM Context

Use `format_for_llm.py` to prepare optimized context:

```python
from scripts.format_for_llm import format_verification_context

# Format for VerificationAgent
context = format_verification_context(
    promise={
        "content": "Q2 2024 airdrop 1000 tokens to all holders",
        "timeline": {"end_date": "2024-06-30"}
    },
    evidence=cleaned_data
)

# Returns formatted string:
# """
# Promise: Q2 2024 airdrop 1000 tokens to all holders
# Expected: 1000 tokens per holder by 2024-06-30
#
# On-Chain Evidence:
# - Airdrop Date: 2024-05-15
# - Recipients: 500 addresses
# - Total Distributed: 500,000 tokens (500 per holder)
# - Transaction: 0x123...
#
# Analysis:
# - Timing: On time (within Q2)
# - Amount: 50% of promised (500 vs 1000 per holder)
# - Coverage: Partial (500 holders vs "all holders")
#
# Conclusion: Partially fulfilled (50%)
# """
```

## Integration with OnChainQueryTool

### Example: Integrate into SpoonOS Tool

```python
from spoon_ai import BaseTool
from scripts.init_sdk import initialize_bsn_ddc_sdk
from scripts.query_transactions import query_transaction_history
from scripts.clean_onchain_data import clean_transaction_data

class OnChainQueryTool(BaseTool):
    name: str = "onchain_query"
    description: str = "Query on-chain behavior for promise verification"

    def __init__(self):
        super().__init__()
        self.sdk = initialize_bsn_ddc_sdk()

    async def execute(
        self,
        contract_address: str,
        start_date: str,
        end_date: str,
        query_type: str
    ):
        # 1. Query raw transactions
        raw_txs = query_transaction_history(
            sdk=self.sdk,
            contract_address=contract_address,
            start_date=start_date,
            end_date=end_date,
            tx_types=[query_type]
        )

        # 2. Clean and structure data
        cleaned = clean_transaction_data(
            raw_transactions=raw_txs,
            promise_type=query_type
        )

        # 3. Return structured evidence
        return {
            "found": len(raw_txs) > 0,
            "evidence": cleaned,
            "raw_count": len(raw_txs)
        }
```

## Supported Chains

BSN-DDC SDK supports multiple open consortium chains:

1. **Taian Chain** (泰安链) - Based on FISCO BCOS
2. **Wuhan Chain** (武汉链) - Based on Ethereum
3. **Wenchang Chain** (文昌链) - Based on IRITA
4. **CMChain** (中移链) - Based on EOS

Configure the chain in `.env`:
```bash
BSN_DDC_CHAIN=taianchain  # or wuhanchain, wenchangchain, zhongyichain
```

## Common Use Cases

### Use Case 1: Verify Airdrop Promise

```python
# Promise: "Q2 2024 airdrop to all holders"
# 1. Query airdrop transactions in Q2
txs = query_transaction_history(
    sdk, contract, "2024-04-01", "2024-06-30", ["airdrop"]
)

# 2. Clean data
evidence = clean_transaction_data(txs, "airdrop")

# 3. Format for LLM
context = format_verification_context(promise, evidence)

# 4. Pass to VerificationAgent for scoring
```

### Use Case 2: Verify Token Launch

```python
# Promise: "Launch token in Q1 2024"
# 1. Query mint/deploy transactions
txs = query_transaction_history(
    sdk, contract, "2024-01-01", "2024-03-31", ["mint", "deploy"]
)

# 2. Check if token was launched
launched = len(txs) > 0
launch_date = txs[0]["timestamp"] if launched else None
```

### Use Case 3: Verify Holder Benefits

```python
# Promise: "Staking rewards for holders"
# 1. Query holder list
holders = query_ddc_holders(sdk, contract)

# 2. Query reward distributions
rewards = query_transaction_history(
    sdk, contract, start_date, end_date, ["transfer"]
)

# 3. Match holders with rewards
fulfilled = match_holders_with_rewards(holders, rewards)
```

## Best Practices

### 1. Error Handling

Always handle SDK errors gracefully:

```python
try:
    data = query_ddc_details(sdk, ddc_id, contract)
except SDKConnectionError:
    # Fallback to alternative data source
    data = query_from_backup_source()
except SDKAuthError:
    # Check API key configuration
    raise ConfigurationError("Invalid BSN-DDC API key")
```

### 2. Rate Limiting

Implement rate limiting to avoid API throttling:

```python
import time

def query_with_rate_limit(sdk, *args, **kwargs):
    time.sleep(0.5)  # 500ms delay between requests
    return sdk.query(*args, **kwargs)
```

### 3. Data Caching

Cache query results to reduce API calls:

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def cached_query_ddc(ddc_id, contract):
    return query_ddc_details(sdk, ddc_id, contract)
```

### 4. Context Length Optimization

Keep LLM context concise:

```python
# Good: Summarized evidence
context = f"Airdrop: {count} recipients, {amount} tokens on {date}"

# Bad: Full transaction details
context = f"Transactions: {json.dumps(all_transactions)}"
```

## Troubleshooting

### Issue: SDK Connection Failed

**Solution**: Check gateway URL and network connectivity
```bash
curl -I $BSN_DDC_GATEWAY_URL
```

### Issue: Authentication Error

**Solution**: Verify API key in BSN-DDC portal
- Login to ddc.bsnbase.com
- Navigate to "Business Information"
- Copy the correct API token

### Issue: No Transactions Found

**Solution**:
1. Verify contract address is correct
2. Check date range covers the promise timeline
3. Ensure the chain is correctly configured

### Issue: Data Format Mismatch

**Solution**: Update `clean_onchain_data.py` to handle new transaction formats

## Reference Files

For detailed implementation, see:
- `references/api-reference.md` - Complete API documentation
- `references/data-structures.md` - Data format specifications
- `examples/basic_usage.py` - Basic SDK usage examples
- `examples/agent_integration.py` - Full integration example

## Related Resources

- **Official GitHub**: https://github.com/BSN-DDC
- **Documentation**: https://github.com/BSN-DDC/docs
- **Portal**: https://ddc.bsnbase.com
- **SegmentFault Guide**: https://segmentfault.com/a/1190000043025944

---

**Note**: This skill is specifically designed for the Promise Breaker Detector project. Adapt the examples to your specific use case and chain configuration.
