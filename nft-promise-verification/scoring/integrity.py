"""
诚信审计评分模块

对比承诺与链上数据，计算违约率
评分范围: 0-100 分（100 分表示完全兑现承诺）
"""
from typing import List, Dict, Any
import structlog

logger = structlog.get_logger(__name__)


class IntegrityScorer:
    """诚信审计评分器"""

    def __init__(self):
        """初始化评分器"""
        pass

    def calculate_score(
        self,
        promises: List[Dict],
        verification_results: List[Dict]
    ) -> Dict[str, Any]:
        """
        计算诚信审计评分

        Args:
            promises: 承诺列表
            verification_results: 验证结果列表

        Returns:
            包含评分和详情的字典
        """
        logger.info(
            "开始计算诚信审计评分",
            promises_count=len(promises),
            results_count=len(verification_results)
        )

        if not promises:
            return {
                "score": 0,
                "dimension": "integrity",
                "status": "no_promises",
                "message": "没有可验证的承诺"
            }

        # 统计验证结果
        total_verifiable = 0
        fulfilled_count = 0
        broken_count = 0
        unverifiable_count = 0

        for promise in promises:
            if not promise.get("verifiable", False):
                unverifiable_count += 1
                continue

            total_verifiable += 1

            # 查找对应的验证结果
            result = self._find_verification_result(
                promise,
                verification_results
            )

            if result:
                status = result.get("status", "unverified")
                if status == "fulfilled":
                    fulfilled_count += 1
                elif status == "broken":
                    broken_count += 1

        # 计算评分
        if total_verifiable == 0:
            score = 50  # 无法验证时给中等分数
            status = "unverifiable"
            message = "所有承诺都无法验证"
        else:
            # 评分公式: (已兑现数 / 可验证总数) * 100
            fulfillment_rate = fulfilled_count / total_verifiable
            score = int(fulfillment_rate * 100)

            if score >= 80:
                status = "excellent"
                message = "项目诚信度优秀"
            elif score >= 60:
                status = "good"
                message = "项目诚信度良好"
            elif score >= 40:
                status = "fair"
                message = "项目诚信度一般"
            else:
                status = "poor"
                message = "项目诚信度较差"

        logger.info(
            "诚信审计评分完成",
            score=score,
            status=status,
            fulfilled=fulfilled_count,
            broken=broken_count,
            unverifiable=unverifiable_count
        )

        return {
            "score": score,
            "dimension": "integrity",
            "status": status,
            "message": message,
            "details": {
                "total_promises": len(promises),
                "verifiable_promises": total_verifiable,
                "fulfilled_count": fulfilled_count,
                "broken_count": broken_count,
                "unverifiable_count": unverifiable_count,
                "fulfillment_rate": round(
                    fulfilled_count / total_verifiable * 100, 2
                ) if total_verifiable > 0 else 0
            }
        }

    def _find_verification_result(
        self,
        promise: Dict,
        verification_results: List[Dict]
    ) -> Dict:
        """
        查找承诺对应的验证结果

        Args:
            promise: 承诺数据
            verification_results: 验证结果列表

        Returns:
            验证结果或空字典
        """
        promise_id = promise.get("id")
        if not promise_id:
            return {}

        for result in verification_results:
            if result.get("promise_id") == promise_id:
                return result

        return {}

    def calculate_violation_rate(
        self,
        promises: List[Dict],
        verification_results: List[Dict]
    ) -> float:
        """
        计算违约率

        Args:
            promises: 承诺列表
            verification_results: 验证结果列表

        Returns:
            违约率 (0-1)
        """
        total_verifiable = sum(
            1 for p in promises if p.get("verifiable", False)
        )

        if total_verifiable == 0:
            return 0.0

        broken_count = sum(
            1 for r in verification_results
            if r.get("status") == "broken"
        )

        return broken_count / total_verifiable
