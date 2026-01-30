"""
官方 WebScraperTool 封装

来源: https://github.com/XSpoonAi/spoon-toolkit
功能: 抓取网页并转换为 markdown/html/text，自动清理广告和脚本
"""
import logging
from typing import Dict, Optional
import httpx
from bs4 import BeautifulSoup
from markdownify import markdownify as markdownify_func

logger = logging.getLogger(__name__)

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; SpoonAI-WebScraper/1.0; +https://github.com/XSpoonAi/spoon-toolkits)",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


class WebScraperToolOfficial:
    """
    官方网页爬取工具

    功能:
    - 抓取网页并转换为 markdown/html/text
    - 自动清理脚本、样式、广告
    - 智能截断（~100k tokens）
    - 检测付费墙（402）
    """

    def __init__(self, timeout: float = 20.0):
        """
        初始化 WebScraper

        Args:
            timeout: 请求超时时间（秒）
        """
        self.timeout = timeout
        self.headers = DEFAULT_HEADERS

    async def execute(
        self,
        url: str,
        output_format: str = "markdown",
        smart_mode: bool = True
    ) -> Dict:
        """
        执行网页爬取

        Args:
            url: 目标 URL
            output_format: 输出格式 (markdown/html/text)
            smart_mode: 是否启用智能截断

        Returns:
            包含 status, content, error 等字段的字典
        """
        if not url:
            return {
                "status": "error",
                "error": "url is required"
            }

        output_format = output_format.lower()
        if output_format not in {"markdown", "html", "text"}:
            return {
                "status": "error",
                "error": "format must be one of: markdown, html, text"
            }

        try:
            async with httpx.AsyncClient(
                headers=self.headers,
                follow_redirects=True,
                timeout=self.timeout
            ) as client:
                response = await client.get(url)

        except Exception as exc:
            logger.warning(f"WebScraper request failed for {url}: {exc}")
            return {
                "status": "error",
                "error": f"Request failed: {exc}"
            }

        # 处理 402 付费墙
        if response.status_code == 402:
            return {
                "status": "error",
                "error": "Access Denied (402). Payment Required. This page is behind a paywall."
            }

        # 处理其他错误
        if response.status_code >= 400:
            snippet = response.text[:200].replace("\n", " ")
            return {
                "status": "error",
                "error": f"Request failed with status {response.status_code}: {snippet}"
            }

        # 清理 HTML
        cleaned_html = self._clean_html(response.text)

        # 转换格式
        if output_format == "html":
            content = cleaned_html
        elif output_format == "text":
            content = self._html_to_text(cleaned_html)
        else:  # markdown
            content = self._html_to_markdown(cleaned_html)

        # 智能截断
        if smart_mode:
            content, truncated = self._apply_smart_truncate(content)
            if truncated:
                content = f"{content}\n\n[truncated for length]"

        return {
            "status": "success",
            "url": url,
            "format": output_format,
            "content": content,
            "content_length": len(content)
        }

    def _clean_html(self, html: str) -> str:
        """清理 HTML：移除脚本、样式、广告等"""
        soup = BeautifulSoup(html, "html.parser")

        # 移除不需要的标签
        for tag in soup(["script", "style", "noscript", "iframe"]):
            tag.decompose()

        # 移除广告
        ad_keywords = ("ad", "ads", "advert", "sponsor", "promo", "banner")

        def is_ad(tag) -> bool:
            if not tag.attrs:
                return False
            tokens = " ".join(
                [tag.get("id", "")] +
                [cls for cls in (tag.get("class") or [])]
            ).lower()
            return any(word in tokens for word in ad_keywords)

        for tag in soup.find_all(is_ad):
            tag.decompose()

        return str(soup)

    def _html_to_markdown(self, html: str) -> str:
        """将 HTML 转换为 Markdown"""
        markdown = markdownify_func(html, heading_style="ATX")
        return markdown.strip()

    def _html_to_text(self, html: str) -> str:
        """将 HTML 转换为纯文本"""
        soup = BeautifulSoup(html, "html.parser")
        text = soup.get_text("\n", strip=True)
        return text

    def _apply_smart_truncate(self, content: str, max_tokens: int = 100_000) -> tuple:
        """智能截断内容"""
        tokens = content.split()
        if len(tokens) <= max_tokens:
            return content, False

        truncated_content = " ".join(tokens[:max_tokens])
        return truncated_content, True

    # ========== 同步方法（兼容原有接口） ==========

    def scrape_url(
        self,
        url: str,
        output_format: str = "markdown"
    ) -> Dict:
        """
        同步版本的网页爬取（兼容队友的接口）

        Args:
            url: 目标 URL
            output_format: 输出格式

        Returns:
            包含 url, title, content, format 的字典
        """
        import asyncio

        # 运行异步方法
        result = asyncio.run(self.execute(url, output_format))

        if result["status"] == "success":
            # 提取标题
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(result["content"], "html.parser")
            title_tag = soup.find(["h1", "title"])
            title = title_tag.get_text().strip() if title_tag else "No Title"

            return {
                "url": url,
                "title": title,
                "content": result["content"],
                "format": output_format
            }
        else:
            raise RuntimeError(result.get("error", "Unknown error"))


# 同步接口的快捷类
class WebScraperOfficial:
    """同步版本的网页爬取器（兼容队友的接口）"""

    def __init__(self, timeout: float = 20.0):
        self._tool = WebScraperToolOfficial(timeout=timeout)

    def scrape_url(self, url: str, output_format: str = "markdown") -> Dict:
        """爬取网页内容（同步接口）"""
        return self._tool.scrape_url(url, output_format)
