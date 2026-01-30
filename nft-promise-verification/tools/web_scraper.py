"""
网页爬取工具

使用 BeautifulSoup4 爬取网页内容并转换为 Markdown 格式
支持多种内容提取策略
"""
import requests
from typing import Optional, Dict
from bs4 import BeautifulSoup
import structlog
from urllib.parse import urljoin, urlparse

logger = structlog.get_logger(__name__)


class WebScraper:
    """网页爬取器"""

    def __init__(self, timeout: int = 30, user_agent: Optional[str] = None):
        """
        初始化网页爬取器

        Args:
            timeout: 请求超时时间（秒）
            user_agent: 自定义 User-Agent
        """
        self.timeout = timeout
        self.user_agent = user_agent or (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/91.0.4472.124 Safari/537.36"
        )

    def scrape_url(
        self,
        url: str,
        output_format: str = "markdown"
    ) -> Dict[str, str]:
        """
        爬取指定 URL 的内容

        Args:
            url: 目标 URL
            output_format: 输出格式 (markdown, html, text)

        Returns:
            包含 url, title, content, format 的字典

        Raises:
            ValueError: URL 无效
            RuntimeError: 爬取失败
        """
        if not url or not url.strip():
            raise ValueError("URL 不能为空")

        # 验证 URL 格式
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            raise ValueError(f"无效的 URL: {url}")

        logger.info("开始爬取网页", url=url, format=output_format)

        try:
            # 发送 HTTP 请求
            headers = {"User-Agent": self.user_agent}
            response = requests.get(
                url,
                headers=headers,
                timeout=self.timeout,
                allow_redirects=True
            )
            response.raise_for_status()

            # 解析 HTML
            soup = BeautifulSoup(response.content, "html.parser")

            # 提取标题
            title = self._extract_title(soup)

            # 提取主要内容
            content = self._extract_content(soup, output_format)

            logger.info(
                "网页爬取完成",
                url=url,
                title=title,
                content_length=len(content)
            )

            return {
                "url": url,
                "title": title,
                "content": content,
                "format": output_format
            }

        except requests.exceptions.Timeout:
            error_msg = f"请求超时: {url}"
            logger.error(error_msg, url=url)
            raise RuntimeError(error_msg)

        except requests.exceptions.RequestException as e:
            error_msg = f"网络请求失败: {str(e)}"
            logger.error(error_msg, url=url, error=str(e))
            raise RuntimeError(error_msg) from e

        except Exception as e:
            error_msg = f"爬取网页失败: {str(e)}"
            logger.error(error_msg, url=url, error=str(e))
            raise RuntimeError(error_msg) from e

    def _extract_title(self, soup: BeautifulSoup) -> str:
        """提取页面标题"""
        # 尝试多种方式提取标题
        title_tag = soup.find("title")
        if title_tag and title_tag.string:
            return title_tag.string.strip()

        h1_tag = soup.find("h1")
        if h1_tag:
            return h1_tag.get_text().strip()

        return "无标题"

    def _extract_content(
        self,
        soup: BeautifulSoup,
        output_format: str
    ) -> str:
        """提取页面主要内容"""
        # 移除不需要的标签
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()

        if output_format == "html":
            return str(soup)

        elif output_format == "text":
            return soup.get_text(separator="\n", strip=True)

        elif output_format == "markdown":
            return self._html_to_markdown(soup)

        else:
            raise ValueError(f"不支持的输出格式: {output_format}")

    def _html_to_markdown(self, soup: BeautifulSoup) -> str:
        """将 HTML 转换为 Markdown 格式"""
        lines = []

        # 处理标题
        for i in range(1, 7):
            for heading in soup.find_all(f"h{i}"):
                text = heading.get_text().strip()
                lines.append(f"{'#' * i} {text}\n")

        # 处理段落
        for p in soup.find_all("p"):
            text = p.get_text().strip()
            if text:
                lines.append(f"{text}\n")

        # 处理列表
        for ul in soup.find_all("ul"):
            for li in ul.find_all("li", recursive=False):
                text = li.get_text().strip()
                lines.append(f"- {text}")
            lines.append("")

        for ol in soup.find_all("ol"):
            for idx, li in enumerate(ol.find_all("li", recursive=False), 1):
                text = li.get_text().strip()
                lines.append(f"{idx}. {text}")
            lines.append("")

        # 处理链接
        for a in soup.find_all("a", href=True):
            text = a.get_text().strip()
            href = a["href"]
            if text and href:
                lines.append(f"[{text}]({href})")

        # 如果没有提取到任何内容，使用纯文本
        if not lines:
            return soup.get_text(separator="\n", strip=True)

        return "\n".join(lines)
