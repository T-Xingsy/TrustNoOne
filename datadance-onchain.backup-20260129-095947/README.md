# datadance-onchain

BSN-DDC SDK integration plugin for the Promise Breaker Detector project. Provides on-chain data querying and preprocessing capabilities for NFT/DDC verification.

## Overview

This Claude Code plugin integrates the BSN-DDC SDK (@ddcmarket/sdk) to enable:
- **On-chain data querying**: Query DDC/NFT transactions, ownership, and history
- **Data cleaning**: Structure raw blockchain data for analysis
- **LLM context preparation**: Format data optimally for AI agents
- **SpoonOS integration**: Ready-to-use tools for promise verification agents

## Features

- ✅ BSN-DDC SDK initialization and configuration
- ✅ DDC/NFT data queries (details, holders, transactions)
- ✅ Transaction history retrieval (mint, transfer, burn, airdrop)
- ✅ Data cleaning and structuring
- ✅ LLM-optimized context formatting
- ✅ SpoonOS agent integration examples
- ✅ Support for multiple blockchain networks

## Installation

### 1. Prerequisites

- Python 3.8+
- Claude Code CLI
- BSN-DDC account (register at https://ddc.bsnbase.com)

### 2. Install Plugin

```bash
# Copy plugin to your project
cp -r datadance-onchain /path/to/your/project/

# Or use Claude Code plugin directory
cp -r datadance-onchain ~/.claude/plugins/
```

### 3. Configure Environment

```bash
# Copy example configuration
cp .env.example .env

# Edit .env with your credentials
nano .env
```

Required configuration:
- `BSN_DDC_GATEWAY_URL`: Your BSN-DDC gateway endpoint
- `BSN_DDC_API_KEY`: Your API authentication key

### 4. Install Dependencies

```bash
# Install Python dependencies (if needed)
pip install python-dotenv
```

## Quick Start

### Using the Skill

Ask Claude Code:
```
How do I use BSN-DDC SDK to query on-chain data?
```

The `bsn-ddc-integration` skill will provide comprehensive guidance.

### Running Examples

```bash
# Basic usage example
cd datadance-onchain/examples
python basic_usage.py

# Agent integration example
python agent_integration.py
```

### Using Scripts Directly

```python
from scripts.init_sdk import initialize_bsn_ddc_sdk
from scripts.query_transactions import query_transaction_history
from scripts.clean_onchain_data import clean_transaction_data

# Initialize SDK
sdk = initialize_bsn_ddc_sdk()

# Query transactions
txs = query_transaction_history(
    sdk, "0xcontract...", "2024-04-01", "2024-06-30", ["airdrop"]
)

# Clean data
evidence = clean_transaction_data(txs, "airdrop")
print(evidence)
```

## Project Structure

```
datadance-onchain/
├── .claude-plugin/
│   └── plugin.json          # Plugin manifest
├── skills/
│   └── bsn-ddc-integration/
│       ├── SKILL.md          # Main skill documentation
│       ├── references/       # Detailed API references
│       └── examples/         # Code examples
├── scripts/
│   ├── init_sdk.py           # SDK initialization
│   ├── query_ddc.py          # DDC data queries
│   ├── query_transactions.py # Transaction history
│   ├── clean_onchain_data.py # Data cleaning
│   └── format_for_llm.py     # LLM context formatting
├── examples/
│   ├── basic_usage.py        # Basic usage example
│   └── agent_integration.py  # SpoonOS agent integration
├── .env.example              # Configuration template
└── README.md                 # This file
```

## Usage in Promise Breaker Detector

### Integration with OnChainQueryTool

```python
from scripts.init_sdk import initialize_bsn_ddc_sdk
from scripts.query_transactions import query_transaction_history
from scripts.clean_onchain_data import clean_transaction_data

class OnChainQueryTool(BaseTool):
    name: str = "onchain_query"
    description: str = "Query on-chain behavior for promise verification"

    def __init__(self):
        super().__init__()
        self.sdk = initialize_bsn_ddc_sdk()

    async def execute(self, contract_address, start_date, end_date, query_type):
        # Query raw transactions
        raw_txs = query_transaction_history(
            self.sdk, contract_address, start_date, end_date, [query_type]
        )

        # Clean and structure
        evidence = clean_transaction_data(raw_txs, query_type)

        return {
            "found": len(raw_txs) > 0,
            "evidence": evidence
        }
```

### Integration with VerificationAgent

```python
from scripts.format_for_llm import format_verification_context

class VerificationAgent(SpoonReactAI):
    async def verify_promise(self, promise, contract_address):
        # 1. Query on-chain data
        query_result = await self.onchain_tool.execute(...)

        # 2. Format for LLM
        context = format_verification_context(promise, query_result['evidence'])

        # 3. Pass to LLM for scoring
        score = await self.llm.achat(context)

        return score
```

## Supported Blockchains

- **Taian Chain** (泰安链) - Based on FISCO BCOS
- **Wuhan Chain** (武汉链) - Based on Ethereum
- **Wenchang Chain** (文昌链) - Based on IRITA
- **CMChain** (中移链) - Based on EOS

Configure in `.env`:
```bash
BSN_DDC_CHAIN=taianchain  # or wuhanchain, wenchangchain, zhongyichain
```

## API Reference

### SDK Initialization

```python
initialize_bsn_ddc_sdk(gateway_url, api_key, chain)
```

### Query Functions

```python
# Query DDC details
query_ddc_details(sdk, ddc_id, contract_address)

# Query holders
query_ddc_holders(sdk, contract_address, limit)

# Query transactions
query_transaction_history(sdk, contract, start_date, end_date, tx_types)

# Query airdrops
query_airdrop_transactions(sdk, contract, start_date, end_date)
```

### Data Processing

```python
# Clean data
clean_transaction_data(raw_transactions, promise_type)

# Calculate metrics
calculate_fulfillment_metrics(cleaned_data, promised_amount, promised_recipients)

# Format for LLM
format_verification_context(promise, evidence, include_analysis)
```

## Configuration

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `BSN_DDC_GATEWAY_URL` | Yes | BSN-DDC gateway endpoint |
| `BSN_DDC_API_KEY` | Yes | API authentication key |
| `BSN_DDC_CHAIN` | No | Target blockchain (default: taianchain) |
| `DEBUG` | No | Enable debug logging (default: false) |

### Obtaining Credentials

1. Register at https://ddc.bsnbase.com
2. Navigate to "Business Information"
3. Copy your Gateway URL and API Key
4. Add to `.env` file

## Troubleshooting

### SDK Connection Failed

**Problem**: Cannot connect to BSN-DDC gateway

**Solution**:
1. Verify `BSN_DDC_GATEWAY_URL` is correct
2. Check network connectivity
3. Ensure API key is valid

### Authentication Error

**Problem**: 403 Forbidden or authentication failed

**Solution**:
1. Verify `BSN_DDC_API_KEY` in BSN-DDC portal
2. Ensure key has not expired
3. Check key permissions

### No Transactions Found

**Problem**: Query returns empty results

**Solution**:
1. Verify contract address is correct
2. Check date range covers the expected period
3. Ensure correct blockchain is configured
4. Try different transaction types

## Development

### Running Tests

```bash
# Test SDK initialization
python scripts/init_sdk.py

# Test DDC queries
python scripts/query_ddc.py

# Test transaction queries
python scripts/query_transactions.py

# Test data cleaning
python scripts/clean_onchain_data.py

# Test LLM formatting
python scripts/format_for_llm.py
```

### Adding New Features

1. Add new script to `scripts/`
2. Update `SKILL.md` with usage examples
3. Add tests to script's `__main__` block
4. Update this README

## Resources

- **BSN-DDC Official**: https://ddc.bsnbase.com
- **GitHub Organization**: https://github.com/BSN-DDC
- **Documentation**: https://github.com/BSN-DDC/docs
- **SegmentFault Guide**: https://segmentfault.com/a/1190000043025944

## License

MIT

## Contributing

This plugin is specifically designed for the Promise Breaker Detector project. For contributions or issues, please contact the project team.

## Support

For questions or issues:
1. Check the `bsn-ddc-integration` skill documentation
2. Review examples in `examples/`
3. Consult BSN-DDC official documentation
4. Contact the Promise Breaker Detector team

---

**Note**: This plugin provides mock implementations for MVP development. Replace mock functions with actual BSN-DDC SDK calls in production.
