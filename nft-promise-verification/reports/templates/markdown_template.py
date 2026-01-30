"""
Markdown 格式报告模板

生成人类可读的 Markdown 格式报告
"""
from typing import Dict, List, Any


class MarkdownTemplate:
    """Markdown 格式报告模板"""

    @staticmethod
    def render(report: Dict[str, Any]) -> str:
        """
        渲染 Markdown 格式报告

        Args:
            report: 报告数据

        Returns:
            Markdown 格式的报告字符串
        """
        lines = []

        # 报告标题
        lines.append("# NFT 项目承诺验证报告")
        lines.append("")

        # 项目信息
        header = report.get("header", {})
        lines.append("## 项目信息")
        lines.append("")
        lines.append(f"- **项目名称**: {header.get('project_name', 'N/A')}")
        lines.append(f"- **项目 ID**: `{header.get('project_id', 'N/A')}`")
        lines.append(f"- **Twitter**: {header.get('twitter_account', 'N/A')}")
        lines.append(f"- **官网**: {header.get('website_url', 'N/A')}")
        lines.append(f"- **合约地址**: `{header.get('contract_address', 'N/A')}`")
        lines.append(f"- **网络**: {header.get('network', 'N/A')}")
        lines.append(f"- **生成时间**: {report.get('generated_at', 'N/A')}")
        lines.append("")

        # 验证摘要
        summary = report.get("verification_summary", {})
        lines.append("## 验证摘要")
        lines.append("")
        lines.append(f"- **承诺总数**: {summary.get('total_promises', 0)}")
        lines.append(f"- **已兑现**: {summary.get('fulfilled_count', 0)} 条")
        lines.append(f"- **未兑现**: {summary.get('broken_count', 0)} 条")
        lines.append(f"- **无法验证**: {summary.get('unverifiable_count', 0)} 条")
        lines.append(f"- **兑现率**: {summary.get('fulfillment_rate', 0)}%")
        lines.append(f"- **诚信审计评分**: {summary.get('integrity_score', 0)} 分")
        lines.append(f"- **评分状态**: {summary.get('integrity_status', 'unknown')}")
        lines.append("")

        # 五维评分
        five_dimensions = report.get("five_dimensions")
        if five_dimensions:
            lines.append("## 画饼指数与五维评分")
            lines.append("")
            lines.append(f"- **画饼指数**: {five_dimensions.get('promise_breaking_index', 0)} 分")
            lines.append(f"- **综合评分**: {five_dimensions.get('comprehensive_score', 0)} 分")
            lines.append(f"- **评估状态**: {five_dimensions.get('status', 'unknown')}")
            lines.append(f"- **评估说明**: {five_dimensions.get('message', '')}")
            lines.append("")

            # 各维度评分
            dimension_scores = five_dimensions.get("dimension_scores", {})
            lines.append("### 各维度评分")
            lines.append("")
            lines.append("| 维度 | 评分 | 权重 | 状态 |")
            lines.append("|------|------|------|------|")

            for dim_key in ["integrity", "fairness", "activity", "stability", "momentum"]:
                dim_data = dimension_scores.get(dim_key, {})
                name = dim_data.get("name", dim_key)
                score = dim_data.get("score")
                status = dim_data.get("status", "unknown")
                weight = dim_data.get("weight", 0)

                if score is not None:
                    lines.append(
                        f"| {name} | {score} 分 | {int(weight * 100)}% | {status} |"
                    )
                else:
                    lines.append(
                        f"| {name} | 数据不可用 | {int(weight * 100)}% | {status} |"
                    )

            lines.append("")

        # 承诺清单
        promise_list = report.get("promise_list", [])
        if promise_list:
            lines.append("## 承诺清单")
            lines.append("")

            for i, promise in enumerate(promise_list, 1):
                status_icon = {
                    "fulfilled": "✅",
                    "broken": "❌",
                    "unverifiable": "❓",
                    "pending": "⏳"
                }.get(promise.get("verification_status"), "")

                lines.append(f"### {i}. {status_icon} {promise.get('content')}")
                lines.append("")
                lines.append(f"- **类型**: {promise.get('promise_type')}")
                lines.append(f"- **状态**: {promise.get('verification_status')}")
                lines.append(f"- **说明**: {promise.get('verification_message')}")

                # 显示证据
                evidence = promise.get("evidence", {})
                if evidence:
                    lines.append("- **证据**:")
                    for key, value in evidence.items():
                        lines.append(f"  - {key}: `{value}`")

                lines.append("")

        # 建议列表
        recommendations = report.get("recommendations", [])
        if recommendations:
            lines.append("## 建议")
            lines.append("")
            for i, rec in enumerate(recommendations, 1):
                lines.append(f"{i}. {rec}")
            lines.append("")

        return "\n".join(lines)

