"""
社区动能审计评分模块

使用 Twitter 数据 + LLM 语义分析，识别 Sybil 攻击
评分范围: 0-100 分（100 分表示社区动能非常强）
"""
from typing import Dict, List, Any
from datetime import datetime, timedelta
import structlog

logger = structlog.get_logger(__name__)


class MomentumScorer:
    """社区动能审计评分器"""

    def __init__(self):
        """初始化评分器"""
        pass

    def calculate_score(
        self,
        twitter_data: Dict[str, Any],
        sentiment_analysis: Dict[str, Any],
        market_data: Dict[str, Any] = None,
        time_window_days: int = 30
    ) -> Dict[str, Any]:
        """
        计算社区动能审计评分

        Args:
            twitter_data: Twitter 数据（粉丝数、互动数等）
            sentiment_analysis: 情感分析结果
            market_data: OpenSea 市场数据（可选）
            time_window_days: 时间窗口（天）

        Returns:
            包含评分和详情的字典
        """
        logger.info(
            "开始计算社区动能审计评分",
            has_twitter=bool(twitter_data),
            has_market=bool(market_data),
            time_window=time_window_days
        )

        # 如果没有任何数据
        if not twitter_data and not market_data:
            return {
                "score": 0,
                "dimension": "momentum",
                "status": "no_data",
                "message": "没有社区数据"
            }

        # ========== Twitter 维度评分 ==========
        twitter_score = 0
        if twitter_data:
            # 提取指标
            followers_count = twitter_data.get("followers_count", 0)
            engagement_rate = twitter_data.get("engagement_rate", 0.0)
            growth_rate = twitter_data.get("growth_rate", 0.0)

            # 情感分析指标
            positive_ratio = sentiment_analysis.get("positive_ratio", 0.0)
            sybil_risk = sentiment_analysis.get("sybil_risk", 0.0)

            # 计算各维度评分
            followers_score = min(100, int(followers_count / 100))
            engagement_score = min(100, int(engagement_rate * 2000))
            growth_score = min(100, int(growth_rate * 1000))
            sentiment_score = min(100, int(positive_ratio * 100 / 0.7))
            sybil_penalty = int(sybil_risk * 100)

            twitter_score = max(0, int(
                followers_score * 0.2 +
                engagement_score * 0.3 +
                growth_score * 0.2 +
                sentiment_score * 0.3
            ) - sybil_penalty)

        # ========== 市场活跃度评分 ==========
        market_score = 0
        if market_data:
            floor_price = market_data.get("floor_price", 0)
            day_volume = market_data.get("day_volume", 0)
            day_sales = market_data.get("day_sales", 0)
            liquidity_score = market_data.get("liquidity_score", "UNKNOWN")

            # 地板价评分（>= 1 ETH 得满分）
            floor_score = min(100, int(floor_price * 100))

            # 交易量评分（>= 100 ETH 得满分）
            volume_score = min(100, int(day_volume * 10))

            # 交易次数评分（>= 50 次/天 得满分）
            sales_score = min(100, int(day_sales * 2))

            # 流动性评分
            liquidity_map = {"HIGH": 100, "MEDIUM": 70, "LOW": 40, "VERY LOW": 10, "UNKNOWN": 50}
            liquidity_bonus = liquidity_map.get(liquidity_score, 50)

            market_score = int(
                floor_score * 0.3 +
                volume_score * 0.3 +
                sales_score * 0.2 +
                liquidity_bonus * 0.2
            )

        # ========== 综合评分 ==========
        # Twitter 占 60%，市场数据占 40%
        if twitter_data and market_data:
            score = int(twitter_score * 0.6 + market_score * 0.4)
        elif twitter_data:
            score = twitter_score
        else:
            score = market_score

        # 判断状态
        if score >= 80:
            status = "excellent"
            message = "社区动能非常强"
        elif score >= 60:
            status = "good"
            message = "社区动能较强"
        elif score >= 40:
            status = "fair"
            message = "社区动能一般"
        else:
            status = "poor"
            message = "社区动能较弱"

        details = {}
        if twitter_data:
            details["twitter"] = {
                "followers_count": twitter_data.get("followers_count", 0),
                "engagement_rate": twitter_data.get("engagement_rate", 0),
                "tweets_count": twitter_data.get("tweets_count", 0)
            }
        if market_data:
            details["market"] = {
                "floor_price": market_data.get("floor_price", 0),
                "day_volume": market_data.get("day_volume", 0),
                "day_sales": market_data.get("day_sales", 0),
                "liquidity_score": market_data.get("liquidity_score", "UNKNOWN")
            }

        logger.info(
            "社区动能审计评分完成",
            score=score,
            twitter_score=twitter_score,
            market_score=market_score,
            status=status
        )

        return {
            "score": score,
            "dimension": "momentum",
            "status": status,
            "message": message,
            "details": details
        }

    def analyze_sentiment(
        self,
        tweets: List[Dict[str, Any]],
        llm_manager
    ) -> Dict[str, Any]:
        """
        使用 LLM 分析推文情感

        Args:
            tweets: 推文列表
            llm_manager: LLM 管理器

        Returns:
            情感分析结果
        """
        if not tweets:
            return {
                "positive_ratio": 0.0,
                "negative_ratio": 0.0,
                "neutral_ratio": 0.0,
                "sybil_risk": 0.0
            }

        # 简化实现：统计关键词
        positive_keywords = ["great", "awesome", "love", "amazing", "excellent"]
        negative_keywords = ["scam", "rug", "fake", "bad", "terrible"]

        positive_count = 0
        negative_count = 0
        neutral_count = 0

        for tweet in tweets:
            text = tweet.get("text", "").lower()

            has_positive = any(kw in text for kw in positive_keywords)
            has_negative = any(kw in text for kw in negative_keywords)

            if has_positive and not has_negative:
                positive_count += 1
            elif has_negative and not has_positive:
                negative_count += 1
            else:
                neutral_count += 1

        total = len(tweets)
        if total == 0:
            return {
                "positive_ratio": 0.0,
                "negative_ratio": 0.0,
                "neutral_ratio": 0.0,
                "sybil_risk": 0.0
            }

        # 检测 Sybil 攻击（简化实现：检查重复内容）
        unique_texts = set(tweet.get("text", "") for tweet in tweets)
        duplicate_ratio = 1.0 - (len(unique_texts) / total)

        return {
            "positive_ratio": positive_count / total,
            "negative_ratio": negative_count / total,
            "neutral_ratio": neutral_count / total,
            "sybil_risk": duplicate_ratio
        }
