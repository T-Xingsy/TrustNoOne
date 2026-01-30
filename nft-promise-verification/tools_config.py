"""
工具配置模块

注册和配置 SpoonOS 工具
- TwitterTool
- WebScraperTool
- MCPWebScraperTool (新增: MCP 协议抓取)
- PromiseExtractorTool
- Chainbase 链上数据工具
- GitHub 开发力审计工具
"""
from typing import List
from spoon_ai.tools import BaseTool, ToolManager
import structlog
import sys

from .tools.twitter_scraper import TwitterScraper
from .tools.web_scraper import WebScraper
from .tools.mcp_scraper import SyncMCPWebScraper
from .tools.promise_extractor import PromiseExtractor

# Spoon-Toolkit 官方工具
try:
    from spoon_toolkits.data_platforms.chainbase import (
        GetAccountBalanceTool,
        GetAccountTransactionsTool,
        GetAccountTokensTool,
        GetAccountNFTsTool,
        GetTokenMetadataTool
    )
    CHAINBASE_AVAILABLE = True
except ImportError:
    CHAINBASE_AVAILABLE = False

try:
    from spoon_toolkits.github import (
        GetGitHubCommitsTool,
        GetGitHubPullRequestsTool,
        GetGitHubIssuesTool
    )
    GITHUB_AVAILABLE = True
except ImportError:
    GITHUB_AVAILABLE = False

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


class MCPWebScraperTool(BaseTool):
    """
    MCP 协议网页抓取工具

    使用 Model Context Protocol (MCP) 和 mcp-server-fetch
    相比 WebScraperTool 的优势:
    - 使用标准 MCP 协议
    - 可与 SpoonReactAI 无缝集成
    - 支持 JavaScript 渲染后的内容
    """

    name = "mcp_web_scraper"
    description = (
        "使用 MCP 协议抓取网页内容（支持动态内容）。"
        "输入: url (目标 URL), output_format (输出格式: markdown/text/html, 默认 markdown)"
        "输出: 包含 url, title, content, format, status 的字典"
        "注意: 某些网站可能有反爬保护，返回 403"
    )

    def __init__(self):
        super().__init__()
        try:
            self.scraper = SyncMCPWebScraper()
            self.available = True
        except ImportError as e:
            logger.warning(
                "MCP Web Scraper 不可用",
                error=str(e),
                hint="pip install mcp mcp-server-fetch"
            )
            self.scraper = None
            self.available = False

    def _run(
        self,
        url: str,
        output_format: str = "markdown"
    ) -> dict:
        """
        执行 MCP 网页抓取

        Args:
            url: 目标 URL
            output_format: 输出格式

        Returns:
            网页内容字典
        """
        if not self.available:
            raise RuntimeError(
                "MCP Web Scraper 不可用，请安装: pip install mcp mcp-server-fetch"
            )

        try:
            content = self.scraper.fetch(
                url=url,
                output_format=output_format
            )

            # 检查是否成功
            if content.get("status") == "error":
                error_msg = content.get("error", "Unknown error")
                if "403" in error_msg:
                    logger.warning(
                        "网页返回 403 (反爬保护)",
                        url=url
                    )
                raise RuntimeError(f"抓取失败: {error_msg}")

            return content
        except Exception as e:
            logger.error(
                "MCP 网页抓取工具执行失败",
                url=url,
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

    # ========== 原有工具 ==========
    twitter_tool = TwitterTool()
    web_scraper_tool = WebScraperTool()
    mcp_web_scraper_tool = MCPWebScraperTool()  # 新增: MCP 网页抓取
    promise_extractor_tool = PromiseExtractorTool(llm_manager)

    tool_manager.register_tool(twitter_tool)
    tool_manager.register_tool(web_scraper_tool)
    tool_manager.register_tool(mcp_web_scraper_tool)  # 注册 MCP 工具
    tool_manager.register_tool(promise_extractor_tool)

    # ========== Chainbase 链上数据工具 ==========
    if CHAINBASE_AVAILABLE:
        chainbase_balance_tool = GetAccountBalanceTool()
        chainbase_txs_tool = GetAccountTransactionsTool()
        chainbase_tokens_tool = GetAccountTokensTool()
        chainbase_nfts_tool = GetAccountNFTsTool()
        chainbase_metadata_tool = GetTokenMetadataTool()

        tool_manager.register_tool(chainbase_balance_tool)
        tool_manager.register_tool(chainbase_txs_tool)
        tool_manager.register_tool(chainbase_tokens_tool)
        tool_manager.register_tool(chainbase_nfts_tool)
        tool_manager.register_tool(chainbase_metadata_tool)

        logger.info("Chainbase 工具注册成功")
    else:
        logger.warning(
            "Chainbase 工具不可用，请安装 spoon-toolkit: "
            "pip install spoon-toolkit"
        )

    # ========== GitHub 开发力审计工具 ==========
    if GITHUB_AVAILABLE:
        github_commits_tool = GetGitHubCommitsTool()
        github_prs_tool = GetGitHubPullRequestsTool()
        github_issues_tool = GetGitHubIssuesTool()

        tool_manager.register_tool(github_commits_tool)
        tool_manager.register_tool(github_prs_tool)
        tool_manager.register_tool(github_issues_tool)

        logger.info("GitHub 工具注册成功")
    else:
        logger.warning(
            "GitHub 工具不可用，请安装 spoon-toolkit: "
            "pip install spoon-toolkit"
        )

    logger.info(
        "工具注册完成",
        tools_count=len(tool_manager.get_all_tools())
    )

    return tool_manager
