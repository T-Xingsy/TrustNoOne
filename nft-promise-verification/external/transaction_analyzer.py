"""
Etherscan 交易分析脚本 (集成版)

来源: https://github.com/XSpoonAi/spoon-awesome-skill
功能: 分析交易详情，用于验证承诺（如资金是否真的锁定）
"""

import json
import os
import urllib.request
from datetime import datetime
from typing import Optional
import structlog

logger = structlog.get_logger(__name__)

# Chain configurations (same as etherscan_client)
CHAIN_CONFIG = {
    "ethereum": {
        "api_url": "https://api.etherscan.io/api",
        "api_key_env": "ETHERSCAN_API_KEY",
        "native_symbol": "ETH",
        "explorer": "https://etherscan.io"
    },
    "polygon": {
        "api_url": "https://api.polygonscan.com/api",
        "api_key_env": "POLYGONSCAN_API_KEY",
        "native_symbol": "POL",
        "explorer": "https://polygonscan.com"
    },
    "sepolia": {
        "api_url": "https://api-sepolia.etherscan.io/api",
        "api_key_env": "ETHERSCAN_API_KEY",
        "native_symbol": "ETH",
        "explorer": "https://sepolia.etherscan.io"
    }
}

# Common function signatures
FUNCTION_SIGNATURES = {
    "0xa9059cbb": "transfer(address,uint256)",
    "0x095ea7b3": "approve(address,uint256)",
    "0x23b872dd": "transferFrom(address,address,uint256)",
    "0x38ed1739": "swapExactTokensForTokens",
    "0x7ff36ab5": "swapExactETHForTokens",
    "0x18cbafe5": "swapExactTokensForETH",
    "0xe8e33700": "addLiquidity",
    "0xf305d719": "addLiquidityETH",
    "0xbaa2abde": "removeLiquidity",
    "0x02751cec": "removeLiquidityETH",
    "0x617ba037": "supply (Aave)",
    "0xa415bcad": "borrow (Aave)",
    "0x573ade81": "repay (Aave)",
    "0x69328dec": "withdraw (Aave)",
    "0x8d80ff0a": "lock (common lock function)",
    "0xa9059cbb": "transfer (token transfer)"
}


def fetch_api(base_url: str, params: dict, api_key: Optional[str] = None) -> dict:
    """Fetch data from Etherscan-like API"""
    if api_key:
        params["apikey"] = api_key

    query = "&".join(f"{k}={v}" for k, v in params.items())
    url = f"{base_url}?{query}"

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "TxAnalyzer/1.0"})
        with urllib.request.urlopen(req, timeout=30) as response:
            return json.loads(response.read().decode())
    except urllib.error.URLError as e:
        raise ConnectionError(f"Failed to fetch data: {e}")


def get_transaction_by_hash(tx_hash: str, chain: str = "ethereum") -> dict:
    """Get transaction details"""
    config = CHAIN_CONFIG.get(chain)
    if not config:
        raise ValueError(f"不支持的链: {chain}")

    api_key = os.getenv(config["api_key_env"]) or os.getenv("ETHERSCAN_API_KEY")

    params = {
        "module": "proxy",
        "action": "eth_getTransactionByHash",
        "txhash": tx_hash
    }

    data = fetch_api(config["api_url"], params, api_key)
    return data.get("result", {})


def get_transaction_receipt(tx_hash: str, chain: str = "ethereum") -> dict:
    """Get transaction receipt"""
    config = CHAIN_CONFIG.get(chain)
    if not config:
        raise ValueError(f"不支持的链: {chain}")

    api_key = os.getenv(config["api_key_env"]) or os.getenv("ETHERSCAN_API_KEY")

    params = {
        "module": "proxy",
        "action": "eth_getTransactionReceipt",
        "txhash": tx_hash
    }

    data = fetch_api(config["api_url"], params, api_key)
    return data.get("result", {})


def decode_function_signature(input_data: str) -> str:
    """Decode function signature from input data"""
    if not input_data or input_data == "0x":
        return "Native Transfer"

    method_id = input_data[:10].lower()
    return FUNCTION_SIGNATURES.get(method_id, f"Unknown ({method_id})")


def analyze_transaction(tx_hash: str, chain: str = "ethereum") -> dict:
    """
    综合交易分析

    Args:
        tx_hash: 交易哈希
        chain: 链名称

    Returns:
        包含交易详情、Gas 信息、功能分析的字典
    """
    config = CHAIN_CONFIG.get(chain)
    if not config:
        raise ValueError(f"不支持的链: {chain}")

    # Validate tx hash format
    if not tx_hash.startswith("0x") or len(tx_hash) != 66:
        raise ValueError(f"无效的交易哈希格式: {tx_hash}")

    logger.info("分析交易", tx_hash=tx_hash, chain=chain)

    # Fetch transaction data
    tx_data = get_transaction_by_hash(tx_hash, chain)
    if not tx_data:
        raise ValueError(f"交易未找到: {tx_hash}")

    # Fetch receipt
    receipt = get_transaction_receipt(tx_hash, chain)

    # Parse basic info
    block_number = int(tx_data.get("blockNumber", "0x0"), 16)
    value_wei = int(tx_data.get("value", "0x0"), 16)
    gas_limit = int(tx_data.get("gas", "0x0"), 16)
    gas_price_wei = int(tx_data.get("gasPrice", "0x0"), 16)
    gas_used = int(receipt.get("gasUsed", "0x0"), 16) if receipt else 0

    # Calculate fees
    tx_fee_wei = gas_used * gas_price_wei
    tx_fee_eth = tx_fee_wei / 1e18

    # Determine status
    status = receipt.get("status", "0x1") if receipt else "0x1"
    is_success = status == "0x1"

    # Parse logs
    logs = receipt.get("logs", []) if receipt else []

    # Decode function
    input_data = tx_data.get("input", "0x")
    function_name = decode_function_signature(input_data)

    return {
        "success": True,
        "chain": chain,
        "tx_hash": tx_hash,
        "explorer_url": f"{config['explorer']}/tx/{tx_hash}",
        "basic_info": {
            "block": block_number,
            "from": tx_data.get("from"),
            "to": tx_data.get("to"),
            "value": {
                "wei": str(value_wei),
                "native": value_wei / 1e18,
                "symbol": config["native_symbol"]
            },
            "status": "Success" if is_success else "Failed"
        },
        "gas_info": {
            "gas_limit": gas_limit,
            "gas_used": gas_used,
            "gas_price_gwei": gas_price_wei / 1e9,
            "tx_fee_eth": round(tx_fee_eth, 6),
            "efficiency": f"{(gas_used / gas_limit * 100):.1f}%" if gas_limit > 0 else "N/A"
        },
        "function_info": {
            "function": function_name,
            "input_data_length": len(input_data),
            "events_emitted": len(logs)
        },
        "analysis": {
            "tx_type": _classify_transaction(function_name, value_wei, logs),
            "is_lock": _is_lock_transaction(function_name, tx_data.get("to")),
            "is_transfer": _is_transfer_transaction(function_name)
        }
    }


def _classify_transaction(function_name: str, value_wei: int, logs: list) -> str:
    """Classify transaction type"""
    func_lower = function_name.lower()

    if "lock" in func_lower:
        return "Lock"
    elif "transfer" in func_lower and "from" not in func_lower:
        return "Token Transfer"
    elif "approve" in func_lower:
        return "Token Approval"
    elif "swap" in func_lower:
        return "DEX Swap"
    elif "liquidity" in func_lower:
        return "Liquidity Operation"
    elif "supply" in func_lower or "deposit" in func_lower:
        return "Lending Deposit"
    elif "borrow" in func_lower:
        return "Lending Borrow"
    elif "withdraw" in func_lower:
        return "Withdrawal"
    elif "native transfer" in func_lower.lower():
        return "Native Token Transfer"
    elif len(logs) > 5:
        return "Complex DeFi Operation"
    else:
        return "Contract Interaction"


def _is_lock_transaction(function_name: str, to_address: str = None) -> bool:
    """判断是否是锁定交易"""
    lock_keywords = ["lock", "deposit", "stake", "timelock"]
    func_lower = function_name.lower()

    for keyword in lock_keywords:
        if keyword in func_lower:
            return True

    # 检查是否是常见锁定合约
    known_lock_contracts = [
        # 可以添加已知的锁定合约地址
    ]

    if to_address and to_address.lower() in known_lock_contracts:
        return True

    return False


def _is_transfer_transaction(function_name: str) -> bool:
    """判断是否是转账交易"""
    return "transfer" in function_name.lower() and "from" not in function_name.lower()
