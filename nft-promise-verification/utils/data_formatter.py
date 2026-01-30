"""
数据格式化模块

统一 Twitter 和官网数据为标准承诺格式
遵循不可变数据模式
"""
from typing import List, Dict, Any
from datetime import datetime
import structlog

logger = structlog.get_logger(__name__)


class DataFormatter:
    """数据格式化器"""

    @staticmethod
    def format_twitter_data(tweets: List[Dict]) -> List[Dict]:
        """
        格式化 Twitter 数据为承诺格式

        Args:
            tweets: Twitter 推文列表

        Returns:
            格式化后的承诺数据列表（新对象）
        """
        formatted_promises = []

        for tweet in tweets:
            formatted = {
                "raw_content": tweet.get("text", ""),
                "source_type": "twitter",
                "source_url": tweet.get("url", ""),
                "source_id": str(tweet.get("id", "")),
                "created_at": tweet.get("created_at", ""),
                "metadata": {
                    "likes": tweet.get("likes", 0),
                    "retweets": tweet.get("retweets", 0),
                    "replies": tweet.get("replies", 0),
                }
            }
            formatted_promises.append(formatted)

        logger.info(
            "Twitter 数据格式化完成",
            input_count=len(tweets),
            output_count=len(formatted_promises)
        )

        return formatted_promises

    @staticmethod
    def format_website_data(web_content: Dict) -> Dict:
        """
        格式化网页数据为承诺格式

        Args:
            web_content: 网页内容字典

        Returns:
            格式化后的承诺数据（新对象）
        """
        formatted = {
            "raw_content": web_content.get("content", ""),
            "source_type": "website",
            "source_url": web_content.get("url", ""),
            "source_id": web_content.get("url", ""),
            "created_at": datetime.now().isoformat(),
            "metadata": {
                "title": web_content.get("title", ""),
                "format": web_content.get("format", "markdown"),
            }
        }

        logger.info(
            "网页数据格式化完成",
            url=web_content.get("url", "")
        )

        return formatted

    @staticmethod
    def merge_promise_data(
        extracted_promises: List[Dict],
        raw_data: Dict
    ) -> List[Dict]:
        """
        合并提取的承诺和原始数据

        Args:
            extracted_promises: LLM 提取的承诺列表
            raw_data: 原始数据（格式化后的）

        Returns:
            完整的承诺数据列表（新对象）
        """
        merged_promises = []

        for promise in extracted_promises:
            merged = {
                # 承诺内容
                "content": promise.get("content", ""),
                "category": promise.get("category", "other"),
                "confidence": promise.get("confidence", 0.0),
                "deadline": promise.get("deadline"),
                "verifiable": promise.get("verifiable", False),

                # 来源信息
                "source_type": raw_data.get("source_type", ""),
                "source_url": promise.get("source_url", ""),
                "source_id": raw_data.get("source_id", ""),
                "created_at": raw_data.get("created_at", ""),

                # 元数据
                "metadata": raw_data.get("metadata", {}),

                # 验证状态（初始值）
                "verification_status": "pending",
                "verification_result": None,
            }
            merged_promises.append(merged)

        logger.info(
            "承诺数据合并完成",
            promises_count=len(merged_promises)
        )

        return merged_promises

    @staticmethod
    def normalize_promise_format(promise: Dict) -> Dict:
        """
        标准化承诺格式（确保所有必需字段存在）

        Args:
            promise: 承诺数据

        Returns:
            标准化后的承诺数据（新对象）
        """
        normalized = {
            "content": promise.get("content", ""),
            "category": promise.get("category", "other"),
            "confidence": float(promise.get("confidence", 0.0)),
            "deadline": promise.get("deadline"),
            "verifiable": bool(promise.get("verifiable", False)),
            "source_type": promise.get("source_type", ""),
            "source_url": promise.get("source_url", ""),
            "source_id": promise.get("source_id", ""),
            "created_at": promise.get("created_at", ""),
            "metadata": promise.get("metadata", {}),
            "verification_status": promise.get(
                "verification_status",
                "pending"
            ),
            "verification_result": promise.get("verification_result"),
        }

        return normalized
