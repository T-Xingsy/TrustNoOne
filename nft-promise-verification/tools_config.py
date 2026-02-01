"""
工具配置模块

注册和配置 SpoonOS 工具
- TwitterTool (使用 bird skill)
- WebScraperTool
- MCPWebScraperTool (MCP 协议抓取)
- PromiseExtractorTool
- Chainbase 链上数据工具
- GitHub 开发力审计工具 (使用 gh CLI skill)
- Excel 报告生成工具 (使用 excel skill)
"""
from typing import List, Any
from spoon_ai.tools import BaseTool, ToolManager
import structlog
import sys

from tools.twitter_scraper import TwitterScraper
from tools.web_scraper import WebScraper
from tools.mcp_scraper import SyncMCPWebScraper
from tools.promise_extractor import PromiseExtractor

# Skill 适配器
from tools.skill_adapters import (
    TwitterSkillAdapter,
    GitHubSkillAdapter,
    ExcelSkillAdapter
)

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
except Exception as e:
    print(f"Warning: Chainbase tools not available: {e}")
    CHAINBASE_AVAILABLE = False

try:
    from spoon_toolkits.github import (
        GetGitHubCommitsTool,
        GetGitHubPullRequestsTool,
        GetGitHubIssuesTool
    )
    GITHUB_AVAILABLE = True
except Exception as e:
    print(f"Warning: GitHub tools not available: {e}")
    GITHUB_AVAILABLE = False

logger = structlog.get_logger(__name__)


class TwitterTool(BaseTool):
    """Twitter 数据抓取工具"""

    name: str = "twitter_scraper"
    description: str = (
        "抓取 Twitter 账号的推文数据。"
        "输入: username (Twitter 用户名), max_tweets (最大推文数, 默认 100)"
        "输出: 推文列表，包含 id, text, created_at, url 等字段"
    )
    parameters: dict = {
        "type": "object",
        "properties": {
            "username": {
                "type": "string",
                "description": "Twitter 用户名"
            },
            "max_tweets": {
                "type": "integer",
                "description": "最大推文数",
                "default": 100
            }
        },
        "required": ["username"]
    }

    # 声明额外的实例属性
    scraper: Any = None

    model_config = {
        "arbitrary_types_allowed": True
    }

    def __init__(self, **data):
        super().__init__(**data)
        self.scraper = TwitterScraper(delay_seconds=1.0)

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

    name: str = "web_scraper"
    description: str = (
        "爬取网页内容并转换为指定格式。"
        "输入: url (目标 URL), output_format (输出格式: markdown/html/text, 默认 markdown)"
        "输出: 包含 url, title, content, format 的字典"
    )
    parameters: dict = {
        "type": "object",
        "properties": {
            "url": {
                "type": "string",
                "description": "目标 URL"
            },
            "output_format": {
                "type": "string",
                "description": "输出格式",
                "enum": ["markdown", "html", "text"],
                "default": "markdown"
            }
        },
        "required": ["url"]
    }

    # 声明额外的实例属性
    scraper: Any = None

    model_config = {
        "arbitrary_types_allowed": True
    }

    def __init__(self, **data):
        super().__init__(**data)
        self.scraper = WebScraper(timeout=30)

    async def execute(
        self,
        url: str,
        output_format: str = "markdown"
    ) -> dict:
        """
        执行网页爬取（异步接口）

        Args:
            url: 目标 URL
            output_format: 输出格式

        Returns:
            包含 url, title, content, format 的字典
        """
        return self._run(url, output_format)

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

    name: str = "promise_extractor"
    description: str = (
        "使用 LLM 从文本中提取项目承诺。"
        "输入: text (输入文本), source_type (来源类型: twitter/website/whitepaper), "
        "source_url (来源 URL), confidence_threshold (置信度阈值, 默认 0.7)"
        "输出: 承诺列表，每个承诺包含 content, category, confidence 等字段"
    )
    parameters: dict = {
        "type": "object",
        "properties": {
            "text": {
                "type": "string",
                "description": "输入文本"
            },
            "source_type": {
                "type": "string",
                "description": "来源类型",
                "enum": ["twitter", "website", "whitepaper"]
            },
            "source_url": {
                "type": "string",
                "description": "来源 URL"
            },
            "confidence_threshold": {
                "type": "number",
                "description": "置信度阈值",
                "default": 0.7
            }
        },
        "required": ["text", "source_type", "source_url"]
    }

    # 声明额外的实例属性
    extractor: Any = None

    model_config = {
        "arbitrary_types_allowed": True
    }

    def __init__(self, llm_manager=None, **data):
        super().__init__(**data)
        self.extractor = PromiseExtractor(llm_manager)

    async def execute(
        self,
        text: str,
        source_type: str,
        source_url: str,
        confidence_threshold: float = 0.7
    ) -> List[dict]:
        """
        执行承诺提取（异步接口）

        Args:
            text: 输入文本
            source_type: 来源类型
            source_url: 来源 URL
            confidence_threshold: 置信度阈值

        Returns:
            承诺列表
        """
        return self._run(text, source_type, source_url, confidence_threshold)

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

    name: str = "mcp_web_scraper"
    description: str = (
        "使用 MCP 协议抓取网页内容（支持动态内容）。"
        "输入: url (目标 URL), output_format (输出格式: markdown/text/html, 默认 markdown)"
        "输出: 包含 url, title, content, format, status 的字典"
        "注意: 某些网站可能有反爬保护，返回 403"
    )
    parameters: dict = {
        "type": "object",
        "properties": {
            "url": {
                "type": "string",
                "description": "目标 URL"
            },
            "output_format": {
                "type": "string",
                "description": "输出格式",
                "enum": ["markdown", "text", "html"],
                "default": "markdown"
            }
        },
        "required": ["url"]
    }

    # 声明额外的实例属性
    scraper: Any = None
    available: bool = False

    model_config = {
        "arbitrary_types_allowed": True
    }

    def __init__(self, **data):
        super().__init__(**data)
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

    async def execute(
        self,
        url: str,
        output_format: str = "markdown"
    ) -> dict:
        """
        执行 MCP 网页抓取（异步接口）

        Args:
            url: 目标 URL
            output_format: 输出格式

        Returns:
            网页内容字典
        """
        return self._run(url, output_format)

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
    # 收集所有工具到列表
    tools = []

    # ========== 核心工具 ==========

    # 1. Twitter 抓取 - 使用 Skill 适配器（推荐）
    try:
        twitter_skill = TwitterSkillAdapter()
        tools.append(twitter_skill)
        logger.info("Twitter Skill 适配器已注册 (使用 bird skill)")
    except Exception as e:
        logger.warning("Twitter Skill 适配器注册失败，回退到原有实现", error=str(e))
        twitter_tool = TwitterTool()
        tools.append(twitter_tool)

    # 2. 网页抓取工具
    web_scraper_tool = WebScraperTool()
    mcp_web_scraper_tool = MCPWebScraperTool()
    tools.extend([
        web_scraper_tool,
        mcp_web_scraper_tool
    ])

    # 3. 承诺提取工具
    promise_extractor_tool = PromiseExtractorTool(llm_manager)
    tools.append(promise_extractor_tool)

    # ========== Skill 增强工具 ==========

    # 4. GitHub 工具 - 使用 Skill 适配器
    try:
        github_skill = GitHubSkillAdapter()
        tools.append(github_skill)
        logger.info("GitHub Skill 适配器已注册 (使用 gh CLI)")
    except Exception as e:
        logger.warning("GitHub Skill 适配器注册失败", error=str(e))

    # 5. Excel 报告生成 - 使用 Skill 适配器
    try:
        excel_skill = ExcelSkillAdapter()
        tools.append(excel_skill)
        logger.info("Excel Skill 适配器已注册")
    except Exception as e:
        logger.warning("Excel Skill 适配器注册失败", error=str(e))

    # ========== Chainbase 链上数据工具 ==========
    if CHAINBASE_AVAILABLE:
        chainbase_balance_tool = GetAccountBalanceTool()
        chainbase_txs_tool = GetAccountTransactionsTool()
        chainbase_tokens_tool = GetAccountTokensTool()
        chainbase_nfts_tool = GetAccountNFTsTool()
        chainbase_metadata_tool = GetTokenMetadataTool()

        tools.extend([
            chainbase_balance_tool,
            chainbase_txs_tool,
            chainbase_tokens_tool,
            chainbase_nfts_tool,
            chainbase_metadata_tool
        ])

        logger.info("Chainbase MCP 工具注册成功")
    else:
        logger.warning(
            "Chainbase 工具不可用，请安装 spoon-toolkit: "
            "pip install spoon-toolkit"
        )

    # ========== 原有 GitHub 开发力审计工具 (保留作为 Fallback) ==========
    if GITHUB_AVAILABLE:
        github_commits_tool = GetGitHubCommitsTool()
        github_prs_tool = GetGitHubPullRequestsTool()
        github_issues_tool = GetGitHubIssuesTool()

        tools.extend([
            github_commits_tool,
            github_prs_tool,
            github_issues_tool
        ])

        logger.info("原有 GitHub 工具已注册 (作为 Fallback)")
    else:
        logger.warning(
            "原有 GitHub 工具不可用，请安装 spoon-toolkit: "
            "pip install spoon-toolkit"
        )

    # 使用工具列表创建 ToolManager
    tool_manager = ToolManager(tools=tools)

    logger.info(
        "工具注册完成",
        tools_count=len(tools)
    )

    return tool_manager
