"""
Twitter Skill 适配器

使用 bird skill 替代原有的 snscrape 实现
"""
import subprocess
import json
from typing import List, Dict, Optional
from datetime import datetime
from spoon_ai.tools import BaseTool
import structlog

logger = structlog.get_logger(__name__)


class TwitterSkillAdapter(BaseTool):
    """
    Twitter 数据抓取工具 - 使用 bird skill

    替代原有的 TwitterScraper，使用社区维护的 bird skill
    优势:
    - 减少维护成本
    - 社区持续更新
    - 更好的反爬能力
    """

    name: str = "twitter_scraper"
    description: str = (
        "使用 bird skill 抓取 Twitter 账号的推文数据。"
        "输入: username (Twitter 用户名), max_tweets (最大推文数, 默认 100)"
        "输出: 推文列表，包含 id, text, created_at, url, likes, retweets 等字段"
    )
    parameters: dict = {
        "type": "object",
        "properties": {
            "username": {
                "type": "string",
                "description": "Twitter 用户名（不含 @）"
            },
            "max_tweets": {
                "type": "integer",
                "description": "最大推文数",
                "default": 100
            }
        },
        "required": ["username"]
    }

    # 声明实例属性
    skill_command: str = "npx"
    skill_available: bool = False

    model_config = {
        "arbitrary_types_allowed": True
    }

    def __init__(self, **data):
        super().__init__(**data)
        self._check_skill_availability()

    def _check_skill_availability(self) -> None:
        """检查 bird skill 是否已安装"""
        try:
            result = subprocess.run(
                ["npx", "clawdhub", "list"],
                capture_output=True,
                text=True,
                timeout=10
            )
            # 检查输出中是否包含 bird
            self.skill_available = "bird" in result.stdout or "bird" in result.stderr

            if not self.skill_available:
                logger.warning(
                    "bird skill 未安装",
                    hint="运行: npx clawdhub@latest install bird"
                )
            else:
                logger.info("bird skill 已就绪")
        except Exception as e:
            logger.warning(
                "无法检查 bird skill 可用性",
                error=str(e)
            )
            self.skill_available = False

    async def execute(self, username: str, max_tweets: int = 100) -> List[dict]:
        """
        执行 Twitter 数据抓取（异步接口）

        Args:
            username: Twitter 用户名
            max_tweets: 最大抓取推文数

        Returns:
            推文列表
        """
        return self._run(username, max_tweets)

    def _run(self, username: str, max_tweets: int = 100) -> List[dict]:
        """
        执行 Twitter 数据抓取

        Args:
            username: Twitter 用户名
            max_tweets: 最大抓取推文数

        Returns:
            推文列表
        """
        if not self.skill_available:
            # Fallback: 尝试使用原有实现
            logger.info(
                "bird skill 不可用，尝试使用原有实现",
                username=username
            )
            return self._fallback_scrape(username, max_tweets)

        if not username or not username.strip():
            raise ValueError("用户名不能为空")

        username = username.lstrip("@").strip()

        logger.info(
            "使用 bird skill 抓取 Twitter 数据",
            username=username,
            max_tweets=max_tweets
        )

        try:
            # 调用 bird skill
            # 注意: bird skill 的实际命令格式需要根据其文档调整
            result = subprocess.run(
                [
                    "npx",
                    "clawdhub@latest",
                    "run",
                    "bird",
                    "--username", username,
                    "--count", str(max_tweets),
                    "--format", "json"
                ],
                capture_output=True,
                text=True,
                timeout=120  # 2 分钟超时
            )

            if result.returncode != 0:
                error_msg = result.stderr.strip() or "未知错误"
                logger.error(
                    "bird skill 执行失败",
                    username=username,
                    error=error_msg
                )
                # 尝试 fallback
                return self._fallback_scrape(username, max_tweets)

            # 解析输出
            tweets = self._parse_skill_output(result.stdout)

            logger.info(
                "Twitter 数据抓取完成",
                username=username,
                tweets_count=len(tweets),
                method="bird_skill"
            )

            return tweets

        except subprocess.TimeoutExpired:
            logger.error(
                "bird skill 执行超时",
                username=username,
                timeout=120
            )
            return self._fallback_scrape(username, max_tweets)

        except Exception as e:
            logger.error(
                "bird skill 执行异常",
                username=username,
                error=str(e)
            )
            return self._fallback_scrape(username, max_tweets)

    def _parse_skill_output(self, output: str) -> List[Dict]:
        """
        解析 bird skill 的输出

        Args:
            output: skill 的原始输出

        Returns:
            标准化的推文列表
        """
        try:
            # 尝试解析 JSON
            raw_tweets = json.loads(output)

            # 标准化为项目需要的格式
            tweets = []
            for tweet in raw_tweets:
                tweets.append({
                    "id": tweet.get("id") or tweet.get("tweet_id"),
                    "text": tweet.get("text") or tweet.get("content") or tweet.get("tweet", ""),
                    "created_at": tweet.get("created_at") or tweet.get("date"),
                    "url": tweet.get("url") or tweet.get("permalink"),
                    "likes": tweet.get("likes") or tweet.get("favorite_count", 0),
                    "retweets": tweet.get("retweets") or tweet.get("retweet_count", 0),
                    "replies": tweet.get("replies") or tweet.get("reply_count", 0),
                })

            return tweets

        except json.JSONDecodeError:
            # 如果不是 JSON，可能是其他格式，尝试逐行解析
            logger.warning(
                "bird skill 输出不是 JSON 格式",
                output_preview=output[:200]
            )
            return []

    def _fallback_scrape(self, username: str, max_tweets: int) -> List[Dict]:
        """
        Fallback 方法：使用原有的 snscrape 实现

        当 bird skill 不可用时使用
        """
        try:
            from tools.twitter_scraper import TwitterScraper

            logger.info(
                "使用 fallback 方法抓取 Twitter",
                username=username,
                method="snscrape"
            )

            scraper = TwitterScraper(delay_seconds=1.0)
            tweets = scraper.scrape_user_tweets(
                username=username,
                max_tweets=max_tweets
            )

            return tweets

        except ImportError:
            error_msg = (
                "bird skill 不可用且 snscrape 未安装。"
                "请安装 bird skill: npx clawdhub@latest install bird"
            )
            logger.error(error_msg)
            raise RuntimeError(error_msg)

        except Exception as e:
            logger.error(
                "Fallback 抓取也失败了",
                username=username,
                error=str(e)
            )
            raise RuntimeError(f"Twitter 抓取失败: {str(e)}") from e
