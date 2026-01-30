"""
画饼指数计算模块

基于五维审计模型计算项目的画饼指数
评分范围: 0-100 分（100 分表示完全不画饼）
"""
from typing import Dict, List, Any, Optional
import structlog

logger = structlog.get_logger(__name__)


class IndexCalculator:
    """画饼指数计算器"""

    # 五维权重配置
    DEFAULT_WEIGHTS = {
        "integrity": 0.30,    # 诚信审计 30%
        "fairness": 0.20,     # 公平性审计 20%
        "activity": 0.20,     # 开发力审计 20%
        "stability": 0.15,    # 财务稳定性审计 15%
        "momentum": 0.15      # 社区动能审计 15%
    }

    def __init__(self, weights: Optional[Dict[str, float]] = None):
        """
        初始化计算器

        Args:
            weights: 自定义权重配置
        """
        self.weights = weights or self.DEFAULT_WEIGHTS

        # 验证权重总和为 1.0
        total_weight = sum(self.weights.values())
        if abs(total_weight - 1.0) > 0.01:
            logger.warning(
                "权重总和不为 1.0，将自动归一化",
                total_weight=total_weight
            )
            # 归一化权重
            self.weights = {
                k: v / total_weight
                for k, v in self.weights.items()
            }

    def calculate_index(
        self,
        integrity_score: Dict[str, Any],
        fairness_score: Optional[Dict[str, Any]] = None,
        activity_score: Optional[Dict[str, Any]] = None,
        stability_score: Optional[Dict[str, Any]] = None,
        momentum_score: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        计算画饼指数

        Args:
            integrity_score: 诚信审计评分（必需）
            fairness_score: 公平性审计评分（可选）
            activity_score: 开发力审计评分（可选）
            stability_score: 财务稳定性审计评分（可选）
            momentum_score: 社区动能审计评分（可选）

        Returns:
            画饼指数结果
        """
        logger.info("开始计算画饼指数")

        # 收集所有评分
        scores = {
            "integrity": integrity_score,
            "fairness": fairness_score,
            "activity": activity_score,
            "stability": stability_score,
            "momentum": momentum_score
        }

        # 处理缺失数据
        available_scores = {}
        missing_dimensions = []

        for dimension, score_data in scores.items():
            if score_data and score_data.get("score") is not None:
                available_scores[dimension] = score_data.get("score", 0)
            else:
                missing_dimensions.append(dimension)

        # 如果没有任何评分数据
        if not available_scores:
            return {
                "promise_breaking_index": 100,  # 最高画饼指数
                "status": "no_data",
                "message": "没有任何审计数据",
                "five_dimensions": {},
                "missing_dimensions": list(scores.keys())
            }

        # 计算加权平均（仅使用可用维度）
        total_weighted_score = 0
        total_weight = 0

        for dimension, score in available_scores.items():
            weight = self.weights.get(dimension, 0)
            total_weighted_score += score * weight
            total_weight += weight

        # 归一化评分
        if total_weight > 0:
            normalized_score = total_weighted_score / total_weight
        else:
            normalized_score = 0

        # 画饼指数 = 100 - 综合评分
        # 评分越高，画饼指数越低
        promise_breaking_index = int(100 - normalized_score)

        # 判断状态
        if promise_breaking_index <= 20:
            status = "excellent"
            message = "项目非常可靠，几乎不画饼"
        elif promise_breaking_index <= 40:
            status = "good"
            message = "项目较为可靠，画饼程度较低"
        elif promise_breaking_index <= 60:
            status = "fair"
            message = "项目可靠性一般，存在一定画饼风险"
        elif promise_breaking_index <= 80:
            status = "poor"
            message = "项目可靠性较差，画饼程度较高"
        else:
            status = "critical"
            message = "项目可靠性极差，严重画饼"

        logger.info(
            "画饼指数计算完成",
            index=promise_breaking_index,
            status=status,
            available_dimensions=list(available_scores.keys()),
            missing_dimensions=missing_dimensions
        )

        return {
            "promise_breaking_index": promise_breaking_index,
            "comprehensive_score": int(normalized_score),
            "status": status,
            "message": message,
            "five_dimensions": {
                "integrity": scores.get("integrity", {}),
                "fairness": scores.get("fairness", {}),
                "activity": scores.get("activity", {}),
                "stability": scores.get("stability", {}),
                "momentum": scores.get("momentum", {})
            },
            "available_dimensions": list(available_scores.keys()),
            "missing_dimensions": missing_dimensions,
            "weights": self.weights
        }

    def calculate_with_boundary_handling(
        self,
        **kwargs
    ) -> Dict[str, Any]:
        """
        计算画饼指数（带边界情况处理）

        处理以下边界情况:
        1. 无承诺数据
        2. 无法验证的承诺
        3. 缺失某些维度的数据

        Args:
            **kwargs: 各维度评分数据

        Returns:
            画饼指数结果
        """
        # 检查是否有承诺数据
        integrity_score = kwargs.get("integrity_score", {})
        if integrity_score.get("status") == "no_promises":
            return {
                "promise_breaking_index": 100,
                "status": "no_promises",
                "message": "项目没有公开承诺，无法评估",
                "five_dimensions": {},
                "missing_dimensions": list(self.weights.keys())
            }

        # 检查是否所有承诺都无法验证
        if integrity_score.get("status") == "unverifiable":
            return {
                "promise_breaking_index": 50,
                "status": "unverifiable",
                "message": "所有承诺都无法验证，评估结果不确定",
                "five_dimensions": {"integrity": integrity_score},
                "missing_dimensions": [
                    k for k in self.weights.keys() if k != "integrity"
                ]
            }

        # 正常计算
        return self.calculate_index(**kwargs)
