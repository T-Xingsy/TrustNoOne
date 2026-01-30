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
        time_window_days: int = 30
    ) -> Dict[str, Any]:
        """
        计算社区动能审计评分

        Args:
            twitter_data: Twitter 数据（粉丝数、互动数等）
            sentiment_analysis: 情感分析结果
            time_window_days: 时间窗口（天）

        Returns:
            包含评分和详情的字典
        """
        logger.info(
            "开始计算社区动能审计评分",
            followers=twitter_data.get("followers_count", 0),
            time_window=time_window_days
        )

        if not twitter_data:
            return {
                "score": 0,
                "dimension": "momentum",
                "status": "no_data",
                "message": "没有社区数据"
            }

        # 提取指标
        followers_count = twitter_data.get("followers_count", 0)
        engagement_rate = twitter_data.get("engagement_rate", 0.0)
        growth_rate = twitter_data.get("growth_rate", 0.0)

        # 情感分析指标
        positive_ratio = sentiment_analysis.get("positive_ratio", 0.0)
        sybil_risk = sentiment_analysis.get("sybil_risk", 0.0)

        # 计算各维度评分
        # 粉丝数评分（>= 10000 得满分）
        followers_score = min(100, int(followers_count / 100))

        # 互动率评分（>= 5% 得满分）
        engagement_score = min(100, int(engagement_rate * 2000))

        # 增长率评分（>= 10% 得满分）
        growth_score = min(100, int(growth_rate * 1000))

        # 情感评分（正面情感 >= 70% 得满分）
        sentiment_score = min(100, int(positive_ratio * 100 / 0.7))

        # Sybil 风险惩罚（风险 >= 50% 扣 50 分）
        sybil_penalty = int(sybil_risk * 100)

        # 加权平均
        base_score = int(
            followers_score * 0.2 +
            engagement_score * 0.3 +
            growth_score * 0.2 +
            sentiment_score * 0.3
        )

        # 最终评分
        score = max(0, base_score - sybil_penalty)

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

        logger.info(
            "社区动能审计评分完成",
            score=score,
            followers=followers_count,
            engagement=round(engagement_rate, 4),
            sybil_risk=round(sybil_risk, 4)
        )

        return {
            "score": score,
            "dimension": "momentum",
            "status": status,
            "message": message,
            "details": {
                "followers_count": followers_count,
                "engagement_rate": round(engagement_rate, 4),
                "growth_rate": round(growth_rate, 4),
                "positive_ratio": round(positive_ratio, 4),
                "sybil_risk": round(sybil_risk, 4),
                "time_window_days": time_window_days
            }
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
