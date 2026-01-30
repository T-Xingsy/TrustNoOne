"""
Twitter 数据抓取工具

使用 snscrape 库抓取 Twitter 账号的推文数据
包含请求延迟和错误处理机制
"""
import time
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import structlog

logger = structlog.get_logger(__name__)


class TwitterScraper:
    """Twitter 数据抓取器"""

    def __init__(self, delay_seconds: float = 1.0):
        """
        初始化 Twitter 抓取器

        Args:
            delay_seconds: 请求之间的延迟时间（秒）
        """
        self.delay_seconds = delay_seconds
        self.last_request_time = 0.0

    def _rate_limit(self) -> None:
        """实施速率限制"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time

        if time_since_last < self.delay_seconds:
            sleep_time = self.delay_seconds - time_since_last
            time.sleep(sleep_time)

        self.last_request_time = time.time()

    def scrape_user_tweets(
        self,
        username: str,
        max_tweets: int = 100,
        days_back: int = 365
    ) -> List[Dict]:
        """
        抓取指定用户的推文

        Args:
            username: Twitter 用户名（不含 @）
            max_tweets: 最大抓取推文数
            days_back: 向前追溯的天数

        Returns:
            推文列表，每条推文包含 id, text, created_at, url 等字段

        Raises:
            ValueError: 用户名无效
            RuntimeError: 抓取失败
        """
        if not username or not username.strip():
            raise ValueError("用户名不能为空")

        username = username.lstrip("@").strip()
        logger.info(
            "开始抓取 Twitter 数据",
            username=username,
            max_tweets=max_tweets,
            days_back=days_back
        )

        try:
            # 计算时间范围
            since_date = datetime.now() - timedelta(days=days_back)
            since_str = since_date.strftime("%Y-%m-%d")

            # 使用 snscrape 抓取推文
            # 注意: snscrape 在某些环境下可能不稳定，需要错误处理
            import snscrape.modules.twitter as sntwitter

            query = f"from:{username} since:{since_str}"
            tweets = []

            self._rate_limit()

            for i, tweet in enumerate(
                sntwitter.TwitterSearchScraper(query).get_items()
            ):
                if i >= max_tweets:
                    break

                tweets.append({
                    "id": tweet.id,
                    "text": tweet.rawContent,
                    "created_at": tweet.date.isoformat(),
                    "url": tweet.url,
                    "likes": tweet.likeCount,
                    "retweets": tweet.retweetCount,
                    "replies": tweet.replyCount,
                })

                # 每抓取一条推文后延迟
                if i < max_tweets - 1:
                    self._rate_limit()

            logger.info(
                "Twitter 数据抓取完成",
                username=username,
                tweets_count=len(tweets)
            )
            return tweets

        except ImportError:
            error_msg = "snscrape 库未安装，请运行: pip install snscrape"
            logger.error(error_msg)
            raise RuntimeError(error_msg)

        except Exception as e:
            error_msg = f"抓取 Twitter 数据失败: {str(e)}"
            logger.error(
                error_msg,
                username=username,
                error=str(e)
            )
            raise RuntimeError(error_msg) from e
