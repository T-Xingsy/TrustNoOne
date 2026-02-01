"""
GitHub Skill 适配器

使用 github skill (gh CLI) 替代原有的 API 实现
"""
import subprocess
import json
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from spoon_ai.tools import BaseTool
import structlog

logger = structlog.get_logger(__name__)


class GitHubSkillAdapter(BaseTool):
    """
    GitHub 数据查询工具 - 使用 gh CLI

    替代原有的 GitHub API 调用，使用 github skill
    优势:
    - 官方维护，稳定可靠
    - 无需管理 API token
    - 已处理速率限制
    """

    name: str = "github_scraper"
    description: str = (
        "使用 gh CLI 查询 GitHub 仓库数据。"
        "输入: owner (仓库所有者), repo (仓库名称), data_type (数据类型: commits/prs/issues), "
        "start_date (开始日期, 可选), end_date (结束日期, 可选)"
        "输出: 对应的 GitHub 数据列表"
    )
    parameters: dict = {
        "type": "object",
        "properties": {
            "owner": {
                "type": "string",
                "description": "仓库所有者"
            },
            "repo": {
                "type": "string",
                "description": "仓库名称"
            },
            "data_type": {
                "type": "string",
                "description": "数据类型",
                "enum": ["commits", "prs", "issues"],
                "default": "commits"
            },
            "start_date": {
                "type": "string",
                "description": "开始日期 (YYYY-MM-DD)",
                "default": None
            },
            "end_date": {
                "type": "string",
                "description": "结束日期 (YYYY-MM-DD)",
                "default": None
            },
            "limit": {
                "type": "integer",
                "description": "返回数量限制",
                "default": 100
            }
        },
        "required": ["owner", "repo", "data_type"]
    }

    # 声明实例属性
    skill_available: bool = False

    model_config = {
        "arbitrary_types_allowed": True
    }

    def __init__(self, **data):
        super().__init__(**data)
        self._check_skill_availability()

    def _check_skill_availability(self) -> None:
        """检查 gh CLI 是否可用"""
        try:
            result = subprocess.run(
                ["gh", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            self.skill_available = result.returncode == 0

            if not self.skill_available:
                logger.warning(
                    "gh CLI 未安装",
                    hint="访问: https://cli.github.com/ 或运行: npx clawdhub@latest install github"
                )
            else:
                logger.info("gh CLI 已就绪")
        except Exception as e:
            logger.warning(
                "无法检查 gh CLI 可用性",
                error=str(e)
            )
            self.skill_available = False

    async def execute(
        self,
        owner: str,
        repo: str,
        data_type: str = "commits",
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: int = 100
    ) -> List[dict]:
        """
        执行 GitHub 数据查询（异步接口）

        Args:
            owner: 仓库所有者
            repo: 仓库名称
            data_type: 数据类型 (commits/prs/issues)
            start_date: 开始日期
            end_date: 结束日期
            limit: 返回数量限制

        Returns:
            GitHub 数据列表
        """
        return self._run(owner, repo, data_type, start_date, end_date, limit)

    def _run(
        self,
        owner: str,
        repo: str,
        data_type: str = "commits",
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: int = 100
    ) -> List[dict]:
        """
        执行 GitHub 数据查询

        Args:
            owner: 仓库所有者
            repo: 仓库名称
            data_type: 数据类型
            start_date: 开始日期
            end_date: 结束日期
            limit: 返回数量限制

        Returns:
            GitHub 数据列表
        """
        if not self.skill_available:
            logger.error(
                "gh CLI 不可用",
                hint="请安装 GitHub CLI: https://cli.github.com/"
            )
            raise RuntimeError(
                "gh CLI 不可用，请安装: https://cli.github.com/ "
                "或使用 github skill: npx clawdhub@latest install github"
            )

        if not owner or not repo:
            raise ValueError("owner 和 repo 不能为空")

        logger.info(
            "使用 gh CLI 查询 GitHub 数据",
            owner=owner,
            repo=repo,
            data_type=data_type,
            start_date=start_date,
            end_date=end_date
        )

        try:
            if data_type == "commits":
                return self._get_commits(owner, repo, start_date, end_date, limit)
            elif data_type == "prs":
                return self._get_prs(owner, repo, start_date, end_date, limit)
            elif data_type == "issues":
                return self._get_issues(owner, repo, limit)
            else:
                raise ValueError(f"不支持的数据类型: {data_type}")

        except Exception as e:
            logger.error(
                "GitHub 数据查询失败",
                owner=owner,
                repo=repo,
                data_type=data_type,
                error=str(e)
            )
            raise

    def _get_commits(
        self,
        owner: str,
        repo: str,
        start_date: Optional[str],
        end_date: Optional[str],
        limit: int
    ) -> List[Dict]:
        """获取 commit 数据"""
        try:
            # 构建 gh 命令
            cmd = [
                "gh", "repo", "view", f"{owner}/{repo}",
                "--json", "commits",
                "--jq", f".commits[:{limit}]"
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode != 0:
                error_msg = result.stderr.strip()
                raise RuntimeError(f"gh CLI 执行失败: {error_msg}")

            # 解析 JSON
            raw_commits = json.loads(result.stdout)

            # 过滤日期范围
            if start_date or end_date:
                raw_commits = self._filter_by_date(
                    raw_commits,
                    start_date,
                    end_date,
                    date_key="committedDate"
                )

            # 标准化格式
            commits = []
            for commit in raw_commits:
                commits.append({
                    "hash": commit.get("oid"),
                    "message": commit.get("messageHeadline"),
                    "author": commit.get("author", {}).get("name"),
                    "date": commit.get("committedDate"),
                    "url": commit.get("url")
                })

            logger.info(
                "GitHub commits 查询完成",
                owner=owner,
                repo=repo,
                count=len(commits)
            )

            return commits

        except Exception as e:
            logger.error("获取 commits 失败", error=str(e))
            raise

    def _get_prs(
        self,
        owner: str,
        repo: str,
        start_date: Optional[str],
        end_date: Optional[str],
        limit: int
    ) -> List[Dict]:
        """获取 PR 数据"""
        try:
            cmd = [
                "gh", "pr", "list", "-R", f"{owner}/{repo}",
                "--limit", str(limit),
                "--json", "number,title,author,state,createdAt,mergedAt,url",
                "--jq", "."
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode != 0:
                error_msg = result.stderr.strip()
                raise RuntimeError(f"gh CLI 执行失败: {error_msg}")

            # 解析 JSON
            raw_prs = json.loads(result.stdout)

            # 过滤日期范围
            if start_date or end_date:
                raw_prs = self._filter_by_date(
                    raw_prs,
                    start_date,
                    end_date,
                    date_key="createdAt"
                )

            # 标准化格式
            prs = []
            for pr in raw_prs:
                prs.append({
                    "number": pr.get("number"),
                    "title": pr.get("title"),
                    "author": pr.get("author", {}).get("login"),
                    "state": pr.get("state"),
                    "created_at": pr.get("createdAt"),
                    "merged_at": pr.get("mergedAt"),
                    "url": pr.get("url")
                })

            logger.info(
                "GitHub PRs 查询完成",
                owner=owner,
                repo=repo,
                count=len(prs)
            )

            return prs

        except Exception as e:
            logger.error("获取 PRs 失败", error=str(e))
            raise

    def _get_issues(self, owner: str, repo: str, limit: int) -> List[Dict]:
        """获取 issue 数据"""
        try:
            cmd = [
                "gh", "issue", "list", "-R", f"{owner}/{repo}",
                "--limit", str(limit),
                "--json", "number,title,author,state,createdAt,url",
                "--jq", "."
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode != 0:
                error_msg = result.stderr.strip()
                raise RuntimeError(f"gh CLI 执行失败: {error_msg}")

            # 解析 JSON
            raw_issues = json.loads(result.stdout)

            # 标准化格式
            issues = []
            for issue in raw_issues:
                issues.append({
                    "number": issue.get("number"),
                    "title": issue.get("title"),
                    "author": issue.get("author", {}).get("login"),
                    "state": issue.get("state"),
                    "created_at": issue.get("createdAt"),
                    "url": issue.get("url")
                })

            logger.info(
                "GitHub issues 查询完成",
                owner=owner,
                repo=repo,
                count=len(issues)
            )

            return issues

        except Exception as e:
            logger.error("获取 issues 失败", error=str(e))
            raise

    def _filter_by_date(
        self,
        items: List[Dict],
        start_date: Optional[str],
        end_date: Optional[str],
        date_key: str = "date"
    ) -> List[Dict]:
        """根据日期范围过滤数据"""
        if not start_date and not end_date:
            return items

        filtered = []
        for item in items:
            date_str = item.get(date_key)
            if not date_str:
                continue

            try:
                item_date = datetime.fromisoformat(date_str.replace("Z", "+00:00"))

                # 检查起始日期
                if start_date:
                    start = datetime.fromisoformat(start_date)
                    if item_date < start:
                        continue

                # 检查结束日期
                if end_date:
                    end = datetime.fromisoformat(end_date)
                    if item_date > end:
                        continue

                filtered.append(item)

            except Exception as e:
                logger.warning(
                    "日期解析失败，跳过此项",
                    date_str=date_str,
                    error=str(e)
                )
                continue

        return filtered
