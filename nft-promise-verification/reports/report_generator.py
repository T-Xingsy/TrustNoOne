"""
验证报告生成器

生成包含承诺清单、验证状态和证据链接的对比报告
"""
from typing import Dict, List, Any, Optional
from datetime import datetime
import structlog

logger = structlog.get_logger(__name__)


class ReportGenerator:
    """验证报告生成器"""

    def __init__(self):
        """初始化报告生成器"""
        pass

    def generate_verification_report(
        self,
        project: Dict[str, Any],
        promises: List[Dict[str, Any]],
        verification_results: List[Dict[str, Any]],
        integrity_score: Dict[str, Any],
        network: str = "mainnet",
        five_dimensions: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        生成验证报告

        Args:
            project: 项目信息
            promises: 承诺列表
            verification_results: 验证结果列表
            integrity_score: 诚信审计评分
            network: 网络名称

        Returns:
            完整的验证报告
        """
        logger.info(
            "生成验证报告",
            project_id=project.get("id"),
            promises_count=len(promises)
        )

        # 1. 生成报告头部
        report_header = self._generate_report_header(
            project,
            network
        )

        # 2. 生成承诺清单
        promise_list = self._generate_promise_list(
            promises,
            verification_results
        )

        # 3. 生成验证摘要
        verification_summary = self._generate_verification_summary(
            verification_results,
            integrity_score
        )

        # 4. 生成五维评分详情（如果提供）
        five_dimensions_details = None
        if five_dimensions:
            five_dimensions_details = self._generate_five_dimensions_details(
                five_dimensions
            )

        # 5. 生成建议列表
        recommendations = self._generate_recommendations(
            integrity_score,
            verification_results,
            five_dimensions
        )

        report = {
            "report_id": f"report_{project.get('id')}_{int(datetime.utcnow().timestamp())}",
            "generated_at": datetime.utcnow().isoformat(),
            "header": report_header,
            "promise_list": promise_list,
            "verification_summary": verification_summary,
            "five_dimensions": five_dimensions_details,
            "recommendations": recommendations
        }

        logger.info(
            "验证报告生成完成",
            report_id=report.get("report_id")
        )

        return report

    def _generate_report_header(
        self,
        project: Dict[str, Any],
        network: str
    ) -> Dict[str, Any]:
        """
        生成报告头部

        Args:
            project: 项目信息
            network: 网络名称

        Returns:
            报告头部信息
        """
        return {
            "project_id": project.get("id"),
            "project_name": project.get("name"),
            "twitter_account": project.get("twitter_account"),
            "website_url": project.get("website_url"),
            "contract_address": project.get("contract_address"),
            "treasury_address": project.get("treasury_address"),
            "network": network,
            "last_verified_at": project.get("last_verified_at")
        }

    def _generate_promise_list(
        self,
        promises: List[Dict[str, Any]],
        verification_results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        生成承诺清单

        Args:
            promises: 承诺列表
            verification_results: 验证结果列表

        Returns:
            包含验证状态的承诺清单
        """
        # 创建验证结果映射
        verification_map = {
            result.get("promise_id"): result
            for result in verification_results
        }

        promise_list = []
        for promise in promises:
            promise_id = promise.get("id")
            verification = verification_map.get(promise_id, {})

            promise_item = {
                "promise_id": promise_id,
                "content": promise.get("content"),
                "promise_type": promise.get("promise_type"),
                "sources": promise.get("sources", []),
                "target_date": promise.get("target_date"),
                "verification_status": verification.get("status", "pending"),
                "verification_message": verification.get("message", ""),
                "evidence": verification.get("evidence", {}),
                "verified_at": verification.get("verified_at")
            }

            promise_list.append(promise_item)

        return promise_list

    def _generate_verification_summary(
        self,
        verification_results: List[Dict[str, Any]],
        integrity_score: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        生成验证摘要

        Args:
            verification_results: 验证结果列表
            integrity_score: 诚信审计评分

        Returns:
            验证摘要
        """
        total = len(verification_results)
        fulfilled = sum(
            1 for r in verification_results
            if r.get("status") == "fulfilled"
        )
        broken = sum(
            1 for r in verification_results
            if r.get("status") == "broken"
        )
        unverifiable = sum(
            1 for r in verification_results
            if r.get("status") == "unverifiable"
        )

        return {
            "total_promises": total,
            "fulfilled_count": fulfilled,
            "broken_count": broken,
            "unverifiable_count": unverifiable,
            "fulfillment_rate": round(
                fulfilled / total * 100, 2
            ) if total > 0 else 0,
            "verification_rate": round(
                (fulfilled + broken) / total * 100, 2
            ) if total > 0 else 0
        }

    def _generate_five_dimensions_details(
        self,
        five_dimensions: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        生成五维评分详情

        Args:
            five_dimensions: 五维评分数据

        Returns:
            五维评分详情
        """
        promise_breaking_index = five_dimensions.get("promise_breaking_index", 0)
        comprehensive_score = five_dimensions.get("comprehensive_score", 0)
        status = five_dimensions.get("status", "unknown")
        message = five_dimensions.get("message", "")
        
        dimensions = five_dimensions.get("five_dimensions", {})
        available_dimensions = five_dimensions.get("available_dimensions", [])
        missing_dimensions = five_dimensions.get("missing_dimensions", [])
        weights = five_dimensions.get("weights", {})

        # 格式化各维度评分
        dimension_scores = {}
        dimension_names = {
            "integrity": "诚信审计",
            "fairness": "公平性审计",
            "activity": "开发力审计",
            "stability": "财务稳定性审计",
            "momentum": "社区动能审计"
        }

        for dim_key, dim_name in dimension_names.items():
            dim_data = dimensions.get(dim_key, {})
            if dim_data and dim_data.get("score") is not None:
                dimension_scores[dim_key] = {
                    "name": dim_name,
                    "score": dim_data.get("score", 0),
                    "status": dim_data.get("status", "unknown"),
                    "message": dim_data.get("message", ""),
                    "details": dim_data.get("details", {}),
                    "weight": weights.get(dim_key, 0)
                }
            else:
                dimension_scores[dim_key] = {
                    "name": dim_name,
                    "score": None,
                    "status": "no_data",
                    "message": "数据不可用",
                    "details": {},
                    "weight": weights.get(dim_key, 0)
                }

        return {
            "promise_breaking_index": promise_breaking_index,
            "comprehensive_score": comprehensive_score,
            "status": status,
            "message": message,
            "dimension_scores": dimension_scores,
            "available_dimensions": available_dimensions,
            "missing_dimensions": missing_dimensions,
            "weights": weights
        }

    def _generate_recommendations(
        self,
        integrity_score: Dict[str, Any],
        verification_results: List[Dict[str, Any]],
        five_dimensions: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """
        生成建议列表

        Args:
            integrity_score: 诚信审计评分
            verification_results: 验证结果列表
            five_dimensions: 五维评分数据（可选）

        Returns:
            建议列表
        """
        recommendations = []

        # 如果有五维评分，优先使用画饼指数生成建议
        if five_dimensions:
            promise_breaking_index = five_dimensions.get("promise_breaking_index", 0)
            status = five_dimensions.get("status", "unknown")
            
            # 根据画饼指数生成建议
            if promise_breaking_index <= 20:
                recommendations.append(
                    "✅ 项目画饼指数极低，非常可靠，几乎不画饼"
                )
            elif promise_breaking_index <= 40:
                recommendations.append(
                    "✅ 项目画饼指数较低，较为可靠，画饼程度较低"
                )
            elif promise_breaking_index <= 60:
                recommendations.append(
                    "⚠️ 项目画饼指数中等，可靠性一般，存在一定画饼风险"
                )
                recommendations.append(
                    "建议持续关注项目进展和承诺兑现情况"
                )
            elif promise_breaking_index <= 80:
                recommendations.append(
                    "⚠️ 项目画饼指数较高，可靠性较差，画饼程度较高"
                )
                recommendations.append(
                    "建议谨慎投资，密切关注项目方行为"
                )
            else:
                recommendations.append(
                    "🚨 项目画饼指数极高，可靠性极差，严重画饼"
                )
                recommendations.append(
                    "强烈建议避免投资，存在重大风险"
                )
            
            # 根据缺失维度生成建议
            missing_dimensions = five_dimensions.get("missing_dimensions", [])
            if missing_dimensions:
                dimension_names = {
                    "integrity": "诚信审计",
                    "fairness": "公平性审计",
                    "activity": "开发力审计",
                    "stability": "财务稳定性审计",
                    "momentum": "社区动能审计"
                }
                missing_names = [
                    dimension_names.get(dim, dim)
                    for dim in missing_dimensions
                ]
                recommendations.append(
                    f"注意：缺少 {', '.join(missing_names)} 数据，"
                    "评分可能不够全面"
                )
            
            # 根据各维度评分生成具体建议
            dimensions = five_dimensions.get("five_dimensions", {})
            
            # 公平性建议
            fairness = dimensions.get("fairness", {})
            if fairness.get("score") is not None and fairness.get("score", 0) < 60:
                recommendations.append(
                    "代币分布不够公平，存在中心化风险"
                )
            
            # 开发力建议
            activity = dimensions.get("activity", {})
            if activity.get("score") is not None and activity.get("score", 0) < 60:
                recommendations.append(
                    "开发活跃度较低，建议关注项目开发进度"
                )
            
            # 财务稳定性建议
            stability = dimensions.get("stability", {})
            if stability.get("score") is not None and stability.get("score", 0) < 60:
                recommendations.append(
                    "财务稳定性较差，建议关注资金流向"
                )
            
            # 社区动能建议
            momentum = dimensions.get("momentum", {})
            if momentum.get("score") is not None and momentum.get("score", 0) < 60:
                recommendations.append(
                    "社区动能较弱，建议关注社区活跃度"
                )
        else:
            # 如果没有五维评分，使用原有的诚信评分逻辑
            score = integrity_score.get("score", 0)
            status = integrity_score.get("status", "unknown")

        # 根据评分状态生成建议
        if status == "poor":
            recommendations.append(
                "⚠️ 项目诚信度较差，建议谨慎投资"
            )
            recommendations.append(
                "建议关注项目方是否有明确的承诺兑现计划"
            )
        elif status == "fair":
            recommendations.append(
                "项目诚信度一般，建议持续关注项目进展"
            )
        elif status == "good":
            recommendations.append(
                "项目诚信度良好，但仍需关注未兑现的承诺"
            )
        elif status == "excellent":
            recommendations.append(
                "✅ 项目诚信度优秀，承诺兑现情况良好"
            )

        # 根据未兑现承诺数量生成建议
        broken_count = sum(
            1 for r in verification_results
            if r.get("status") == "broken"
        )

        if broken_count > 0:
            recommendations.append(
                f"发现 {broken_count} 条未兑现承诺，建议查看详细证据"
            )

        # 根据无法验证承诺数量生成建议
        unverifiable_count = sum(
            1 for r in verification_results
            if r.get("status") == "unverifiable"
        )

        if unverifiable_count > 0:
            recommendations.append(
                f"有 {unverifiable_count} 条承诺无法通过链上数据验证，"
                "建议通过其他渠道核实"
            )

        return recommendations

    def format_report_as_text(
        self,
        report: Dict[str, Any]
    ) -> str:
        """
        将报告格式化为文本

        Args:
            report: 报告数据

        Returns:
            文本格式的报告
        """
        lines = []

        # 报告头部
        header = report.get("header", {})
        lines.append("=" * 80)
        lines.append(f"NFT 项目承诺验证报告")
        lines.append("=" * 80)
        lines.append(f"项目名称: {header.get('project_name')}")
        lines.append(f"项目 ID: {header.get('project_id')}")
        lines.append(f"Twitter: {header.get('twitter_account', 'N/A')}")
        lines.append(f"官网: {header.get('website_url', 'N/A')}")
        lines.append(f"合约地址: {header.get('contract_address', 'N/A')}")
        lines.append(f"网络: {header.get('network')}")
        lines.append(f"生成时间: {report.get('generated_at')}")
        lines.append("")

        # 验证摘要
        summary = report.get("verification_summary", {})
        lines.append("-" * 80)
        lines.append("验证摘要")
        lines.append("-" * 80)
        lines.append(f"承诺总数: {summary.get('total_promises')}")
        lines.append(f"已兑现: {summary.get('fulfilled_count')}")
        lines.append(f"未兑现: {summary.get('broken_count')}")
        lines.append(f"无法验证: {summary.get('unverifiable_count')}")
        lines.append(f"兑现率: {summary.get('fulfillment_rate')}%")
        lines.append(f"诚信审计评分: {summary.get('integrity_score')} 分")
        lines.append(f"评分状态: {summary.get('integrity_status')}")
        lines.append(f"评分说明: {summary.get('integrity_message')}")
        lines.append("")

        # 五维评分详情
        five_dimensions = report.get("five_dimensions")
        if five_dimensions:
            lines.append("-" * 80)
            lines.append("画饼指数与五维评分")
            lines.append("-" * 80)
            lines.append(f"画饼指数: {five_dimensions.get('promise_breaking_index')} 分")
            lines.append(f"综合评分: {five_dimensions.get('comprehensive_score')} 分")
            lines.append(f"评估状态: {five_dimensions.get('status')}")
            lines.append(f"评估说明: {five_dimensions.get('message')}")
            lines.append("")
            
            # 各维度评分
            dimension_scores = five_dimensions.get("dimension_scores", {})
            lines.append("各维度评分:")
            
            for dim_key in ["integrity", "fairness", "activity", "stability", "momentum"]:
                dim_data = dimension_scores.get(dim_key, {})
                name = dim_data.get("name", dim_key)
                score = dim_data.get("score")
                status = dim_data.get("status", "unknown")
                weight = dim_data.get("weight", 0)
                
                if score is not None:
                    lines.append(
                        f"  • {name}: {score} 分 "
                        f"(权重: {int(weight * 100)}%, 状态: {status})"
                    )
                else:
                    lines.append(
                        f"  • {name}: 数据不可用 "
                        f"(权重: {int(weight * 100)}%)"
                    )
            
            # 缺失维度提示
            missing_dimensions = five_dimensions.get("missing_dimensions", [])
            if missing_dimensions:
                lines.append("")
                lines.append(f"注意: 缺少 {len(missing_dimensions)} 个维度的数据")
            
            lines.append("")

        # 承诺清单
        promise_list = report.get("promise_list", [])
        lines.append("-" * 80)
        lines.append("承诺清单")
        lines.append("-" * 80)

        for i, promise in enumerate(promise_list, 1):
            status_icon = {
                "fulfilled": "✅",
                "broken": "❌",
                "unverifiable": "❓",
                "pending": "⏳"
            }.get(promise.get("verification_status"), "")

            lines.append(f"\n{i}. {status_icon} {promise.get('content')}")
            lines.append(f"   类型: {promise.get('promise_type')}")
            lines.append(f"   状态: {promise.get('verification_status')}")
            lines.append(f"   说明: {promise.get('verification_message')}")

            # 显示证据
            evidence = promise.get("evidence", {})
            if evidence:
                lines.append(f"   证据:")
                for key, value in evidence.items():
                    lines.append(f"     - {key}: {value}")

        lines.append("")

        # 建议列表
        recommendations = report.get("recommendations", [])
        if recommendations:
            lines.append("-" * 80)
            lines.append("建议")
            lines.append("-" * 80)
            for i, rec in enumerate(recommendations, 1):
                lines.append(f"{i}. {rec}")
            lines.append("")

        lines.append("=" * 80)

        return "\n".join(lines)
