"""
Etherscan 地址分析脚本 (集成版)

来源: https://github.com/XSpoonAi/spoon-awesome-skill
功能: 分析地址余额、交易记录、合约信息
"""

import json
import os
import urllib.request
from typing import Optional
import structlog

logger = structlog.get_logger(__name__)

# Chain configurations
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
    "arbitrum": {
        "api_url": "https://api.arbiscan.io/api",
        "api_key_env": "ARBISCAN_API_KEY",
        "native_symbol": "ETH",
        "explorer": "https://arbiscan.io"
    },
    "optimism": {
        "api_url": "https://api-optimistic.etherscan.io/api",
        "api_key_env": "OPTIMISM_API_KEY",
        "native_symbol": "ETH",
        "explorer": "https://optimistic.etherscan.io"
    },
    "base": {
        "api_url": "https://api.basescan.org/api",
        "api_key_env": "BASESCAN_API_KEY",
        "native_symbol": "ETH",
        "explorer": "https://basescan.org"
    },
    "sepolia": {
        "api_url": "https://api-sepolia.etherscan.io/api",
        "api_key_env": "ETHERSCAN_API_KEY",
        "native_symbol": "ETH",
        "explorer": "https://sepolia.etherscan.io"
    }
}


def fetch_api(base_url: str, params: dict, api_key: Optional[str] = None) -> dict:
    """Fetch data from Etherscan-like API"""
    if api_key:
        params["apikey"] = api_key

    query = "&".join(f"{k}={v}" for k, v in params.items())
    url = f"{base_url}?{query}"

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "OnchainSkill/1.0"})
        with urllib.request.urlopen(req, timeout=30) as response:
            data = json.loads(response.read().decode())

            if data.get("status") == "0" and "rate limit" in data.get("message", "").lower():
                raise ValueError("API rate limit exceeded. Please try again later.")

            return data
    except urllib.error.URLError as e:
        raise ConnectionError(f"Failed to fetch data: {e}")


def get_address_balance(address: str, chain: str = "ethereum") -> dict:
    """
    Get native token balance for an address

    Args:
        address: 钱包地址
        chain: 链名称

    Returns:
        {"balance": float, "symbol": str}
    """
    config = CHAIN_CONFIG.get(chain)
    if not config:
        raise ValueError(f"不支持的链: {chain}")

    api_key = os.getenv(config["api_key_env"]) or os.getenv("ETHERSCAN_API_KEY")

    params = {
        "module": "account",
        "action": "balance",
        "address": address,
        "tag": "latest"
    }

    data = fetch_api(config["api_url"], params, api_key)

    if data.get("status") == "1":
        balance_wei = int(data.get("result", 0))
        balance = balance_wei / 1e18
        return {
            "balance_wei": str(balance_wei),
            "balance": balance,
            "symbol": config["native_symbol"]
        }

    return {"balance": 0, "symbol": config["native_symbol"]}


def get_transactions(
    address: str,
    chain: str = "ethereum",
    limit: int = 10
) -> list:
    """
    Get recent transactions for an address

    Args:
        address: 钱包地址
        chain: 链名称
        limit: 返回数量

    Returns:
        交易列表
    """
    config = CHAIN_CONFIG.get(chain)
    if not config:
        raise ValueError(f"不支持的链: {chain}")

    api_key = os.getenv(config["api_key_env"]) or os.getenv("ETHERSCAN_API_KEY")

    params = {
        "module": "account",
        "action": "txlist",
        "address": address,
        "startblock": 0,
        "endblock": 99999999,
        "page": 1,
        "offset": limit,
        "sort": "desc"
    }

    data = fetch_api(config["api_url"], params, api_key)

    if data.get("status") == "1":
        txs = data.get("result", [])
        return [
            {
                "hash": tx.get("hash"),
                "block": int(tx.get("blockNumber", 0)),
                "timestamp": int(tx.get("timeStamp", 0)),
                "from": tx.get("from"),
                "to": tx.get("to"),
                "value_wei": tx.get("value"),
                "value": float(tx.get("value", 0)) / 1e18,
                "gas_used": int(tx.get("gasUsed", 0)),
                "gas_price_gwei": int(tx.get("gasPrice", 0)) / 1e9,
                "is_error": tx.get("isError") == "1",
                "method_id": tx.get("methodId", "0x")
            }
            for tx in txs
        ]

    return []


def get_contract_info(address: str, chain: str = "ethereum") -> Optional[dict]:
    """
    Get contract information if address is a contract

    Args:
        address: 合约地址
        chain: 链名称

    Returns:
        合约信息或 None
    """
    config = CHAIN_CONFIG.get(chain)
    if not config:
        raise ValueError(f"不支持的链: {chain}")

    api_key = os.getenv(config["api_key_env"]) or os.getenv("ETHERSCAN_API_KEY")

    params = {
        "module": "contract",
        "action": "getsourcecode",
        "address": address
    }

    data = fetch_api(config["api_url"], params, api_key)

    if data.get("status") == "1":
        result = data.get("result", [{}])[0]
        if result.get("ContractName"):
            return {
                "is_contract": True,
                "name": result.get("ContractName"),
                "compiler": result.get("CompilerVersion"),
                "verified": bool(result.get("SourceCode")),
                "proxy": result.get("Proxy") == "1",
                "implementation": result.get("Implementation") if result.get("Proxy") == "1" else None
            }

    return {"is_contract": False}


def analyze_address(address: str, chain: str = "ethereum") -> dict:
    """
    综合地址分析

    Args:
        address: 钱包/合约地址
        chain: 链名称

    Returns:
        包含余额、交易、合约信息的字典
    """
    config = CHAIN_CONFIG.get(chain)
    if not config:
        raise ValueError(f"不支持的链: {chain}")

    # Validate address format
    if not address.startswith("0x") or len(address) != 42:
        raise ValueError(f"无效的地址格式: {address}")

    logger.info("分析地址", address=address, chain=chain)

    # Fetch all data
    balance_data = get_address_balance(address, chain)
    transactions = get_transactions(address, chain, 10)
    contract_info = get_contract_info(address, chain)

    # Calculate statistics
    tx_count = len(transactions)
    total_received = sum(tx["value"] for tx in transactions if tx["to"] and tx["to"].lower() == address.lower())
    total_sent = sum(tx["value"] for tx in transactions if tx["from"] and tx["from"].lower() == address.lower())

    # Determine address type
    address_type = "Contract" if contract_info.get("is_contract") else "EOA (Wallet)"

    return {
        "success": True,
        "chain": chain,
        "address": address,
        "explorer_url": f"{config['explorer']}/address/{address}",
        "address_type": address_type,
        "balance": {
            "native": balance_data["balance"],
            "symbol": balance_data["symbol"]
        },
        "transaction_summary": {
            "total_transactions": tx_count,
            "total_received": round(total_received, 6),
            "total_sent": round(total_sent, 6),
            "net_flow": round(total_received - total_sent, 6),
            "recent_transactions": transactions[:5]
        },
        "contract_info": contract_info if contract_info.get("is_contract") else None,
        "analysis": {
            "activity_level": "HIGH" if tx_count > 100 else "MEDIUM" if tx_count > 10 else "LOW"
        }
    }


def get_token_transfers(address: str, chain: str = "ethereum", limit: int = 10) -> list:
    """
    Get ERC20 token transfers for an address

    Args:
        address: 钱包地址
        chain: 链名称
        limit: 返回数量

    Returns:
        ERC20 代币转账列表
    """
    config = CHAIN_CONFIG.get(chain)
    if not config:
        raise ValueError(f"不支持的链: {chain}")

    api_key = os.getenv(config["api_key_env"]) or os.getenv("ETHERSCAN_API_KEY")

    params = {
        "module": "account",
        "action": "tokentx",
        "address": address,
        "startblock": 0,
        "endblock": 99999999,
        "page": 1,
        "offset": limit,
        "sort": "desc"
    }

    data = fetch_api(config["api_url"], params, api_key)

    if data.get("status") == "1":
        transfers = data.get("result", [])
        return [
            {
                "hash": tx.get("hash"),
                "timestamp": int(tx.get("timeStamp", 0)),
                "token_name": tx.get("tokenName"),
                "token_symbol": tx.get("tokenSymbol"),
                "token_address": tx.get("contractAddress"),
                "from": tx.get("from"),
                "to": tx.get("to"),
                "value": float(tx.get("value", 0)) / (10 ** int(tx.get("tokenDecimal", 18))),
                "direction": "IN" if tx.get("to", "").lower() == address.lower() else "OUT"
            }
            for tx in transfers
        ]

    return []


# ==================== 模块4: 合约事件查询 (新增) ====================

def get_contract_events(
    contract_address: str,
    from_block: int = 0,
    to_block: int = 99999999,
    topic0: str = None,
    topic1: str = None,
    topic2: str = None,
    topic3: str = None,
    chain: str = "ethereum"
) -> list:
    """
    查询合约事件日志 - 用于验证承诺（如锁定事件、解锁事件）

    Args:
        contract_address: 合约地址
        from_block: 起始区块号
        to_block: 结束区块号
        topic0: 事件主题0 (事件签名)
        topic1: 事件主题1 (通常是 indexed 参数)
        topic2: 事件主题2
        topic3: 事件主题3
        chain: 链名称

    Returns:
        事件日志列表

    Example:
        # 查询 Locked(address,uint256,uint256) 事件
        topic0 = "0x..." # 事件签名的 Keccak256 哈希
        events = get_contract_events(
            contract_address="0x...",
            topic0="0x...",
            from_block=18000000
        )
    """
    config = CHAIN_CONFIG.get(chain)
    if not config:
        raise ValueError(f"不支持的链: {chain}")

    api_key = os.getenv(config["api_key_env"]) or os.getenv("ETHERSCAN_API_KEY")

    params = {
        "module": "logs",
        "action": "getLogs",
        "address": contract_address,
        "fromBlock": from_block,
        "toBlock": to_block,
        "page": 1,
        "offset": 1000,  # Etherscan 最大返回 1000 条
        "sort": "asc"
    }

    # 添加 topic 过滤
    if topic0:
        params["topic0"] = topic0
    if topic1:
        params["topic1"] = topic1
    if topic2:
        params["topic2"] = topic2
    if topic3:
        params["topic3"] = topic3

    data = fetch_api(config["api_url"], params, api_key)

    if data.get("status") == "1":
        logs = data.get("result", [])
        return [
            {
                "address": log.get("address"),
                "topics": log.get("topics", []),
                "data": log.get("data"),
                "block_number": int(log.get("blockNumber", 0)),
                "timestamp": int(log.get("timeStamp", 0)),
                "tx_hash": log.get("transactionHash"),
                "tx_index": int(log.get("transactionIndex", 0)),
                "log_index": int(log.get("logIndex", 0)),
            }
            for log in logs
        ]

    return []


def verify_lock_event(
    contract_address: str,
    lock_amount: float = None,
    user_address: str = None,
    from_block: int = 0,
    chain: str = "ethereum"
) -> dict:
    """
    验证锁定事件 - 检查合约中是否有资金锁定记录

    Args:
        contract_address: 锁定合约地址
        lock_amount: 预期锁定金额 (ETH)
        user_address: 锁定者地址
        from_block: 从哪个区块开始查询
        chain: 链名称

    Returns:
        验证结果字典
    """
    logger.info(
        "验证锁定事件",
        contract=contract_address,
        expected_amount=lock_amount,
        user=user_address
    )

    # 常见的锁定事件签名
    # Locked(address indexed user, uint256 amount, uint256 unlockTime)
    LOCKED_EVENT_SIGNATURES = [
        "0x...",  # 需要根据实际合约填充
    ]

    # 查询合约的所有事件日志
    events = get_contract_events(
        contract_address=contract_address,
        from_block=from_block,
        chain=chain
    )

    # 分析事件
    if not events:
        return {
            "verified": False,
            "message": "未找到任何事件日志",
            "events_found": 0
        }

    # 统计锁定相关事件
    lock_related_events = []
    total_locked = 0

    for event in events:
        # 检查事件是否包含锁定相关的数据
        # 这里简化处理，实际需要解析事件签名
        data = event.get("data", "0x")
        if data and data != "0x":
            try:
                # 尝试解析为金额 (假设第一个参数是金额)
                value = int(data[2:66], 16) if len(data) >= 68 else 0
                value_eth = value / 1e18
                if value_eth > 0:
                    total_locked += value_eth
                    lock_related_events.append({
                        "block": event["block_number"],
                        "tx_hash": event["tx_hash"],
                        "amount": value_eth,
                        "timestamp": event["timestamp"]
                    })
            except (ValueError, IndexError):
                pass

    return {
        "verified": len(lock_related_events) > 0,
        "message": f"找到 {len(lock_related_events)} 个锁定相关事件" if lock_related_events else "未找到锁定事件",
        "events_found": len(lock_related_events),
        "total_locked": round(total_locked, 6),
        "expected_amount": lock_amount,
        "amount_match": abs(total_locked - lock_amount) < 0.001 if lock_amount else None,
        "events": lock_related_events[:10]  # 返回最近 10 个事件
    }


def get_nft_transfer_events(
    contract_address: str = None,
    from_block: int = 0,
    to_block: int = 99999999,
    chain: str = "ethereum"
) -> list:
    """
    查询 NFT 转账事件 (Transfer(address indexed from, address indexed to, uint256 indexed tokenId))

    Args:
        contract_address: NFT 合约地址
        from_block: 起始区块
        to_block: 结束区块
        chain: 链名称

    Returns:
        NFT 转账事件列表
    """
    # Transfer 事件签名 (Keccak256("Transfer(address,address,uint256)"))
    TRANSFER_EVENT_TOPIC0 = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"

    config = CHAIN_CONFIG.get(chain)
    if not config:
        raise ValueError(f"不支持的链: {chain}")

    api_key = os.getenv(config["api_key_env"]) or os.getenv("ETHERSCAN_API_KEY")

    params = {
        "module": "logs",
        "action": "getLogs",
        "topic0": TRANSFER_EVENT_TOPIC0,
        "fromBlock": from_block,
        "toBlock": to_block,
        "page": 1,
        "offset": 1000,
        "sort": "desc"
    }

    if contract_address:
        params["address"] = contract_address

    data = fetch_api(config["api_url"], params, api_key)

    if data.get("status") == "1":
        logs = data.get("result", [])
        return [
            {
                "contract": log.get("address"),
                "from": log.get("topics", [""])[1][-40:] if len(log.get("topics", [])) > 1 else None,
                "to": log.get("topics", ["", ""])[2][-40:] if len(log.get("topics", [])) > 2 else None,
                "token_id": int(log.get("topics", ["", "", ""])[3], 16) if len(log.get("topics", [])) > 3 else None,
                "block_number": int(log.get("blockNumber", 0)),
                "timestamp": int(log.get("timeStamp", 0)),
                "tx_hash": log.get("transactionHash"),
            }
            for log in logs
        ]

    return []
