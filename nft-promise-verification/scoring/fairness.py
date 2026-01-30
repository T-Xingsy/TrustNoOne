"""
公平性审计评分模块

使用 TokenHolders 工具计算基尼系数，判断中心化风险
评分范围: 0-100 分（100 分表示完全公平分配）
"""
from typing import Dict, List, Any
import structlog

logger = structlog.get_logger(__name__)


class FairnessScorer:
    """公平性审计评分器"""

    def __init__(self):
        """初始化评分器"""
        pass

    def calculate_score(
        self,
        token_holders: List[Dict[str, Any]],
        total_supply: int
    ) -> Dict[str, Any]:
        """
        计算公平性审计评分

        Args:
            token_holders: 代币持有者列表 [{"address": "0x...", "balance": 100}, ...]
            total_supply: 代币总供应量

        Returns:
            包含评分和详情的字典
        """
        logger.info(
            "开始计算公平性审计评分",
            holders_count=len(token_holders),
            total_supply=total_supply
        )

        if not token_holders or total_supply == 0:
            return {
                "score": 0,
                "dimension": "fairness",
                "status": "no_data",
                "message": "没有代币持有者数据"
            }

        # 计算基尼系数
        gini_coefficient = self._calculate_gini_coefficient(
            token_holders,
            total_supply
        )

        # 计算前 10 持有者占比
        top10_percentage = self._calculate_top_holders_percentage(
            token_holders,
            total_supply,
            top_n=10
        )

        # 计算评分
        # 基尼系数越低越好（0 表示完全平等）
        # 评分公式: (1 - gini) * 100
        gini_score = int((1 - gini_coefficient) * 100)

        # 前 10 持有者占比越低越好
        # 如果前 10 持有者占比 > 50%，认为中心化风险高
        concentration_penalty = 0
        if top10_percentage > 0.5:
            concentration_penalty = int((top10_percentage - 0.5) * 100)

        # 最终评分
        score = max(0, gini_score - concentration_penalty)

        # 判断状态
        if score >= 80:
            status = "excellent"
            message = "代币分配非常公平"
        elif score >= 60:
            status = "good"
            message = "代币分配较为公平"
        elif score >= 40:
            status = "fair"
            message = "代币分配存在一定中心化风险"
        else:
            status = "poor"
            message = "代币分配高度中心化"

        logger.info(
            "公平性审计评分完成",
            score=score,
            gini=round(gini_coefficient, 4),
            top10_pct=round(top10_percentage * 100, 2)
        )

        return {
            "score": score,
            "dimension": "fairness",
            "status": status,
            "message": message,
            "details": {
                "gini_coefficient": round(gini_coefficient, 4),
                "top10_holders_percentage": round(top10_percentage * 100, 2),
                "total_holders": len(token_holders),
                "concentration_risk": "high" if top10_percentage > 0.5 else "low"
            }
        }

    def _calculate_gini_coefficient(
        self,
        token_holders: List[Dict[str, Any]],
        total_supply: int
    ) -> float:
        """
        计算基尼系数

        Args:
            token_holders: 代币持有者列表
            total_supply: 代币总供应量

        Returns:
            基尼系数 (0-1)
        """
        if not token_holders or total_supply == 0:
            return 0.0

        # 按余额排序
        sorted_holders = sorted(
            token_holders,
            key=lambda x: x.get("balance", 0)
        )

        n = len(sorted_holders)
        cumulative_balance = 0
        gini_sum = 0

        for i, holder in enumerate(sorted_holders):
            balance = holder.get("balance", 0)
            cumulative_balance += balance
            gini_sum += (2 * (i + 1) - n - 1) * balance

        if cumulative_balance == 0:
            return 0.0

        gini = gini_sum / (n * cumulative_balance)
        return abs(gini)

    def _calculate_top_holders_percentage(
        self,
        token_holders: List[Dict[str, Any]],
        total_supply: int,
        top_n: int = 10
    ) -> float:
        """
        计算前 N 持有者占比

        Args:
            token_holders: 代币持有者列表
            total_supply: 代币总供应量
            top_n: 前 N 个持有者

        Returns:
            占比 (0-1)
        """
        if not token_holders or total_supply == 0:
            return 0.0

        # 按余额降序排序
        sorted_holders = sorted(
            token_holders,
            key=lambda x: x.get("balance", 0),
            reverse=True
        )

        # 计算前 N 持有者的总余额
        top_balance = sum(
            holder.get("balance", 0)
            for holder in sorted_holders[:top_n]
        )

        return top_balance / total_supply if total_supply > 0 else 0.0
