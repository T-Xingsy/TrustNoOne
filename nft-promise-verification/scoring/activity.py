"""
开发力审计评分模块

使用 GitHub API 分析开发活跃度
评分范围: 0-100 分（100 分表示开发非常活跃）
"""
from typing import Dict, List, Any
from datetime import datetime, timedelta
import structlog

logger = structlog.get_logger(__name__)


class ActivityScorer:
    """开发力审计评分器"""

    def __init__(self):
        """初始化评分器"""
        pass

    def calculate_score(
        self,
        commits: List[Dict[str, Any]],
        pull_requests: List[Dict[str, Any]],
        time_window_days: int = 90
    ) -> Dict[str, Any]:
        """
        计算开发力审计评分

        Args:
            commits: 提交记录列表
            pull_requests: PR 列表
            time_window_days: 时间窗口（天）

        Returns:
            包含评分和详情的字典
        """
        logger.info(
            "开始计算开发力审计评分",
            commits_count=len(commits),
            prs_count=len(pull_requests),
            time_window=time_window_days
        )

        if not commits and not pull_requests:
            return {
                "score": 0,
                "dimension": "activity",
                "status": "no_data",
                "message": "没有开发活动数据"
            }

        # 计算时间窗口内的活动
        cutoff_date = datetime.utcnow() - timedelta(days=time_window_days)

        recent_commits = [
            c for c in commits
            if self._parse_date(c.get("date")) >= cutoff_date
        ]

        recent_prs = [
            pr for pr in pull_requests
            if self._parse_date(pr.get("created_at")) >= cutoff_date
        ]

        # 计算指标
        commit_frequency = len(recent_commits) / time_window_days
        pr_frequency = len(recent_prs) / time_window_days
        active_contributors = len(set(
            c.get("author") for c in recent_commits if c.get("author")
        ))

        # 计算评分
        # 提交频率评分（每天 >= 1 次提交得满分）
        commit_score = min(100, int(commit_frequency * 100))

        # PR 频率评分（每周 >= 1 个 PR 得满分）
        pr_score = min(100, int(pr_frequency * 7 * 100))

        # 贡献者多样性评分（>= 5 个活跃贡献者得满分）
        contributor_score = min(100, int(active_contributors * 20))

        # 加权平均
        score = int(
            commit_score * 0.5 +
            pr_score * 0.3 +
            contributor_score * 0.2
        )

        # 判断状态
        if score >= 80:
            status = "excellent"
            message = "开发非常活跃"
        elif score >= 60:
            status = "good"
            message = "开发较为活跃"
        elif score >= 40:
            status = "fair"
            message = "开发活跃度一般"
        else:
            status = "poor"
            message = "开发活跃度较低"

        logger.info(
            "开发力审计评分完成",
            score=score,
            commit_freq=round(commit_frequency, 2),
            pr_freq=round(pr_frequency, 2),
            contributors=active_contributors
        )

        return {
            "score": score,
            "dimension": "activity",
            "status": status,
            "message": message,
            "details": {
                "recent_commits": len(recent_commits),
                "recent_prs": len(recent_prs),
                "commit_frequency": round(commit_frequency, 2),
                "pr_frequency": round(pr_frequency, 2),
                "active_contributors": active_contributors,
                "time_window_days": time_window_days
            }
        }

    def _parse_date(self, date_str: str) -> datetime:
        """解析日期字符串"""
        if not date_str:
            return datetime.min

        try:
            return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        except Exception:
            return datetime.min
