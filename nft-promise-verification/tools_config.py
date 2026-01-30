"""
工具配置模块

注册和配置 SpoonOS 工具
- TwitterTool
- WebScraperTool
- PromiseExtractorTool
"""
from typing import List
from spoon_core.tools.base import BaseTool
from spoon_core.tools.tool_manager import ToolManager
import structlog

from .tools.twitter_scraper import TwitterScraper
from .tools.web_scraper import WebScraper
from .tools.promise_extractor import PromiseExtractor

logger = structlog.get_logger(__name__)


class TwitterTool(BaseTool):
    """Twitter 数据抓取工具"""

    name = "twitter_scraper"
    description = (
        "抓取 Twitter 账号的推文数据。"
        "输入: username (Twitter 用户名), max_tweets (最大推文数, 默认 100)"
        "输出: 推文列表，包含 id, text, created_at, url 等字段"
    )

    def __init__(self):
        super().__init__()
        self.scraper = TwitterScraper(delay_seconds=1.0)

    def _run(self, username: str, max_tweets: int = 100) -> List[dict]:
        """
        执行 Twitter 数据抓取

        Args:
            username: Twitter 用户名
            max_tweets: 最大抓取推文数

        Returns:
            推文列表
        """
        try:
            tweets = self.scraper.scrape_user_tweets(
                username=username,
                max_tweets=max_tweets
            )
            return tweets
        except Exception as e:
            logger.error(
                "Twitter 工具执行失败",
                username=username,
                error=str(e)
            )
            raise


class WebScraperTool(BaseTool):
    """网页爬取工具"""

    name = "web_scraper"
    description = (
        "爬取网页内容并转换为指定格式。"
        "输入: url (目标 URL), output_format (输出格式: markdown/html/text, 默认 markdown)"
        "输出: 包含 url, title, content, format 的字典"
    )

    def __init__(self):
        super().__init__()
        self.scraper = WebScraper(timeout=30)

    def _run(
        self,
        url: str,
        output_format: str = "markdown"
    ) -> dict:
        """
        执行网页爬取

        Args:
            url: 目标 URL
            output_format: 输出格式

        Returns:
            网页内容字典
        """
        try:
            content = self.scraper.scrape_url(
                url=url,
                output_format=output_format
            )
            return content
        except Exception as e:
            logger.error(
                "网页爬取工具执行失败",
                url=url,
                error=str(e)
            )
            raise


class PromiseExtractorTool(BaseTool):
    """承诺提取工具"""

    name = "promise_extractor"
    description = (
        "使用 LLM 从文本中提取项目承诺。"
        "输入: text (输入文本), source_type (来源类型: twitter/website/whitepaper), "
        "source_url (来源 URL), confidence_threshold (置信度阈值, 默认 0.7)"
        "输出: 承诺列表，每个承诺包含 content, category, confidence 等字段"
    )

    def __init__(self, llm_manager):
        super().__init__()
        self.extractor = PromiseExtractor(llm_manager)

    def _run(
        self,
        text: str,
        source_type: str,
        source_url: str,
        confidence_threshold: float = 0.7
    ) -> List[dict]:
        """
        执行承诺提取

        Args:
            text: 输入文本
            source_type: 来源类型
            source_url: 来源 URL
            confidence_threshold: 置信度阈值

        Returns:
            承诺列表
        """
        try:
            promises = self.extractor.extract_promises(
                text=text,
                source_type=source_type,
                source_url=source_url,
                confidence_threshold=confidence_threshold
            )
            return promises
        except Exception as e:
            logger.error(
                "承诺提取工具执行失败",
                source_type=source_type,
                error=str(e)
            )
            raise


def register_tools(llm_manager) -> ToolManager:
    """
    注册所有工具到 ToolManager

    Args:
        llm_manager: LLM 管理器实例

    Returns:
        配置好的 ToolManager 实例
    """
    tool_manager = ToolManager()

    # 注册工具
    twitter_tool = TwitterTool()
    web_scraper_tool = WebScraperTool()
    promise_extractor_tool = PromiseExtractorTool(llm_manager)

    tool_manager.register_tool(twitter_tool)
    tool_manager.register_tool(web_scraper_tool)
    tool_manager.register_tool(promise_extractor_tool)

    logger.info(
        "工具注册完成",
        tools_count=len(tool_manager.get_all_tools())
    )

    return tool_manager
