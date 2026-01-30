"""
MCP 网页抓取工具

使用 Model Context Protocol (MCP) 和 mcp-server-fetch
支持动态内容抓取，绕过简单的反爬机制
"""
import asyncio
import sys
import logging
from typing import Dict, Optional, List
from datetime import datetime

try:
    from mcp import ClientSession
    from mcp.client.stdio import stdio_client, StdioServerParameters
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False

logger = logging.getLogger(__name__)


class MCPWebScraper:
    """
    MCP 协议的网页抓取器

    使用 mcp-server-fetch 提供的 fetch 工具
    优势:
    - 使用标准 MCP 协议
    - 可与 SpoonReactAI Agent 集成
    - 支持自定义 User-Agent
    """

    def __init__(
        self,
        user_agent: Optional[str] = None,
        timeout: int = 30
    ):
        """
        初始化 MCP Web Scraper

        Args:
            user_agent: 自定义 User-Agent
            timeout: 请求超时时间（秒）
        """
        if not MCP_AVAILABLE:
            raise ImportError(
                "MCP 包未安装，请运行: pip install mcp mcp-server-fetch"
            )

        self.user_agent = user_agent or (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
        self.timeout = timeout
        self._session: Optional[ClientSession] = None
        self._stdio_context = None

    async def _get_session(self) -> ClientSession:
        """获取或创建 MCP 会话"""
        if self._session is None:
            # 配置服务器参数
            server_params = StdioServerParameters(
                command=sys.executable,
                args=[
                    "-m", "mcp_server_fetch",
                    "--user-agent", self.user_agent
                ],
                env=None
            )

            # 创建 stdio 连接
            self._stdio_context = stdio_client(server_params)
            streams = await self._stdio_context.__aenter__()

            # 创建会话
            self._session = ClientSession(streams[0], streams[1])
            await self._session.initialize()

            logger.info("MCP session created successfully")

        return self._session

    async def fetch(
        self,
        url: str,
        output_format: str = "markdown"
    ) -> Dict:
        """
        抓取网页内容

        Args:
            url: 目标 URL
            output_format: 输出格式 (markdown/text/html)

        Returns:
            包含 url, title, content, format, status 的字典
        """
        session = await self._get_session()

        try:
            logger.info(f"Fetching URL: {url}")

            # 调用 MCP fetch 工具
            result = await session.call_tool(
                "fetch",
                arguments={
                    "url": url,
                    "outputFormat": output_format
                }
            )

            # 解析响应
            content = ""
            for item in result.content:
                if hasattr(item, "text"):
                    content += item.text
                elif isinstance(item, str):
                    content += item

            # 检查是否是错误响应
            if "Failed to fetch" in content or "status code 403" in content:
                return {
                    "url": url,
                    "status": "error",
                    "error": content.strip(),
                    "format": output_format
                }

            # 提取简单的标题
            title = self._extract_title(content)

            return {
                "url": url,
                "title": title,
                "content": content,
                "format": output_format,
                "status": "success",
                "content_length": len(content),
                "fetched_at": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Fetch failed for {url}: {e}")
            return {
                "url": url,
                "status": "error",
                "error": str(e),
                "format": output_format
            }

    def _extract_title(self, content: str) -> str:
        """从内容中提取标题"""
        # 尝试提取 Markdown 标题
        lines = content.split("\n")
        for line in lines[:10]:  # 只检查前10行
            line = line.strip()
            if line.startswith("# "):
                return line[2:].strip()
            elif line.strip().startswith("title>") and "<title>" in line:
                # HTML title 标签
                import re
                match = re.search(r'<title>(.*?)</title>', content, re.IGNORECASE)
                if match:
                    return match.group(1).strip()
        return "No Title"

    async def fetch_multiple(
        self,
        urls: List[str],
        output_format: str = "markdown"
    ) -> List[Dict]:
        """
        批量抓取多个 URL

        Args:
            urls: URL 列表
            output_format: 输出格式

        Returns:
            抓取结果列表
        """
        results = []
        for url in urls:
            result = await self.fetch(url, output_format)
            results.append(result)
        return results

    async def close(self):
        """关闭 MCP 会话"""
        if self._session:
            try:
                await self._session.close()
            except Exception:
                pass
            self._session = None

        if self._stdio_context:
            try:
                await self._stdio_context.__aexit__(None, None, None)
            except Exception:
                pass
            self._stdio_context = None

        logger.info("MCP session closed")

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()


# 同步包装器（兼容现有接口）
class SyncMCPWebScraper:
    """同步版本的 MCP 网页抓取器"""

    def __init__(self, **kwargs):
        self._scraper = MCPWebScraper(**kwargs)
        self._loop = None
        self._initialized = False

    def _ensure_initialized(self):
        """确保初始化"""
        if not self._initialized:
            try:
                self._loop = asyncio.get_event_loop()
                if self._loop.is_running():
                    # 如果在已运行的循环中，创建新任务
                    pass
            except RuntimeError:
                self._loop = asyncio.new_event_loop()
                asyncio.set_event_loop(self._loop)

            # 初始化 MCP 会话
            asyncio.run(self._scraper._get_session())
            self._initialized = True

    def fetch(self, url: str, output_format: str = "markdown") -> Dict:
        """同步抓取网页"""
        return asyncio.run(self._scraper.fetch(url, output_format))

    def fetch_multiple(self, urls: List[str], output_format: str = "markdown") -> List[Dict]:
        """同步批量抓取"""
        return asyncio.run(self._scraper.fetch_multiple(urls, output_format))

    def close(self):
        """关闭连接"""
        if self._loop:
            self._loop.run_until_complete(self._scraper.close())


# 测试函数
async def _test_mcp_scraper():
    """测试 MCP 抓取器"""
    scraper = MCPWebScraper()
    try:
        # 测试 GitHub
        print("Testing GitHub...")
        result = await scraper.fetch("https://github.com/XSpoonAi/spoon-toolkit")
        print(f"Status: {result['status']}")
        print(f"Content length: {result.get('content_length', 0)}")
        print(f"Preview: {result.get('content', '')[:200]}...")
    finally:
        await scraper.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(_test_mcp_scraper())
