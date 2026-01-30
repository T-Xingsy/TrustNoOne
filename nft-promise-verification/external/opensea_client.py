"""
OpenSea 集合数据脚本 (集成版)

来源: https://github.com/XSpoonAi/spoon-awesome-skill
功能: 获取 NFT 集合的地板价、交易量、持有者数等数据
"""

import json
import urllib.request
import urllib.error
from typing import Optional
import structlog

logger = structlog.get_logger(__name__)

OPENSEA_API_V2 = "https://api.opensea.io/api/v2"


def fetch_json(url: str, api_key: str = None) -> dict:
    """Fetch JSON from URL with optional API key"""
    headers = {
        "Accept": "application/json",
        "User-Agent": "NFT-Promise-Verification/1.0"
    }

    if api_key:
        headers["X-API-KEY"] = api_key

    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=30) as response:
            return json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        if e.code == 401:
            logger.warning("OpenSea API key 无效，尝试使用公开数据")
            return fetch_json(url, api_key=None)
        elif e.code == 404:
            raise ValueError(f"集合未找到: {url}")
        raise ConnectionError(f"API error: {e.code} - {e.reason}")
    except urllib.error.URLError as e:
        raise ConnectionError(f"获取数据失败: {e}")


def get_collection_stats(collection_slug: str, api_key: str = None) -> dict:
    """Get collection statistics from OpenSea"""
    url = f"{OPENSEA_API_V2}/collections/{collection_slug}/stats"
    data = fetch_json(url, api_key)

    if not data:
        raise ValueError(f"未找到集合统计数据: {collection_slug}")

    return data


def get_collection_info(collection_slug: str, api_key: str = None) -> dict:
    """Get collection information from OpenSea"""
    url = f"{OPENSEA_API_V2}/collections/{collection_slug}"
    data = fetch_json(url, api_key)

    if not data:
        raise ValueError(f"集合未找到: {collection_slug}")

    return data


def get_collection_data(collection_slug: str, chain: str = "ethereum", api_key: str = None) -> dict:
    """
    获取 NFT 集合的全面数据

    Args:
        collection_slug: OpenSea 集合标识 (如 "boredapeyachtclub")
        chain: 链名称 (默认 "ethereum")
        api_key: OpenSea API key (可选)

    Returns:
        包含集合信息、统计数据、24小时数据的字典
    """
    logger.info("获取 OpenSea 集合数据", collection=collection_slug)

    # Fetch collection info
    try:
        info = get_collection_info(collection_slug, api_key)
    except Exception as e:
        logger.warning(f"获取集合信息失败: {e}")
        info = {}

    # Fetch collection stats
    try:
        stats = get_collection_stats(collection_slug, api_key)
    except Exception as e:
        logger.warning(f"获取统计数据失败: {e}")
        stats = {}

    # Parse and format data
    total_stats = stats.get("total", {})
    intervals = stats.get("intervals", [])

    # Get 24h stats if available
    day_stats = {}
    for interval in intervals:
        if interval.get("interval") == "one_day":
            day_stats = interval
            break

    return {
        "success": True,
        "collection": {
            "name": info.get("name", collection_slug),
            "slug": collection_slug,
            "description": (info.get("description", "")[:500] + "...") if info.get("description") else "N/A",
            "image_url": info.get("image_url"),
            "banner_image_url": info.get("banner_image_url"),
            "external_url": info.get("project_url"),
            "discord_url": info.get("discord_url"),
            "twitter_username": info.get("twitter_username"),
            "contracts": info.get("contracts", []),
            "created_date": info.get("created_date"),
            "owner": info.get("owner"),
            "category": info.get("category"),
            "total_supply": info.get("total_supply", 0)
        },
        "stats": {
            "floor_price": {
                "value": total_stats.get("floor_price", 0),
                "currency": total_stats.get("floor_price_symbol", "ETH")
            },
            "total_volume": total_stats.get("volume", 0),
            "total_sales": total_stats.get("sales", 0),
            "num_owners": total_stats.get("num_owners", 0),
            "average_price": total_stats.get("average_price", 0),
            "market_cap": total_stats.get("market_cap", 0)
        },
        "day_stats": {
            "volume": day_stats.get("volume", 0),
            "volume_change": day_stats.get("volume_change", 0),
            "sales": day_stats.get("sales", 0),
            "sales_change": day_stats.get("sales_change", 0),
            "average_price": day_stats.get("average_price", 0)
        },
        "chain": chain,
        "liquidity_score": _calculate_liquidity_score(total_stats, day_stats)
    }


def _calculate_liquidity_score(total_stats: dict, day_stats: dict) -> str:
    """Calculate a simple liquidity score based on volume and sales"""
    daily_volume = day_stats.get("volume", 0)
    daily_sales = day_stats.get("sales", 0)

    if daily_sales >= 100 and daily_volume >= 10:
        return "HIGH"
    elif daily_sales >= 20 and daily_volume >= 2:
        return "MEDIUM"
    elif daily_sales >= 5:
        return "LOW"
    else:
        return "VERY LOW"
