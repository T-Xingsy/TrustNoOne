"""
Table 格式报告模板

使用 Unicode 表格边框生成终端友好的报告
"""
from typing import Dict, List, Any


class TableTemplate:
    """Table 格式报告模板"""

    # Unicode 表格边框字符
    BORDER_TOP_LEFT = "┌"
    BORDER_TOP_RIGHT = "┐"
    BORDER_BOTTOM_LEFT = "└"
    BORDER_BOTTOM_RIGHT = "┘"
    BORDER_HORIZONTAL = "─"
    BORDER_VERTICAL = "│"
    BORDER_CROSS = "┼"
    BORDER_T_DOWN = "┬"
    BORDER_T_UP = "┴"
    BORDER_T_RIGHT = "├"
    BORDER_T_LEFT = "┤"

    @staticmethod
    def render(report: Dict[str, Any]) -> str:
        """
        渲染 Table 格式报告

        Args:
            report: 报告数据

        Returns:
            Table 格式的报告字符串
        """
        lines = []

        # 报告标题
        lines.append(TableTemplate._render_title("NFT 项目承诺验证报告"))
        lines.append("")

        # 项目信息
        header = report.get("header", {})
        lines.append(TableTemplate._render_section_title("项目信息"))
        lines.append(TableTemplate._render_key_value_table([
            ("项目名称", header.get("project_name", "N/A")),
            ("项目 ID", header.get("project_id", "N/A")),
            ("Twitter", header.get("twitter_account", "N/A")),
            ("官网", header.get("website_url", "N/A")),
            ("合约地址", header.get("contract_address", "N/A")),
            ("网络", header.get("network", "N/A")),
            ("生成时间", report.get("generated_at", "N/A"))
        ]))
        lines.append("")

        # 验证摘要
        summary = report.get("verification_summary", {})
        lines.append(TableTemplate._render_section_title("验证摘要"))
        lines.append(TableTemplate._render_key_value_table([
            ("承诺总数", summary.get("total_promises", 0)),
            ("已兑现", f"{summary.get('fulfilled_count', 0)} 条"),
            ("未兑现", f"{summary.get('broken_count', 0)} 条"),
            ("无法验证", f"{summary.get('unverifiable_count', 0)} 条"),
            ("兑现率", f"{summary.get('fulfillment_rate', 0)}%"),
            ("诚信审计评分", f"{summary.get('integrity_score', 0)} 分"),
            ("评分状态", summary.get("integrity_status", "unknown"))
        ]))
        lines.append("")

        # 五维评分
        five_dimensions = report.get("five_dimensions")
        if five_dimensions:
            lines.append(TableTemplate._render_section_title("画饼指数与五维评分"))
            lines.append(TableTemplate._render_key_value_table([
                ("画饼指数", f"{five_dimensions.get('promise_breaking_index', 0)} 分"),
                ("综合评分", f"{five_dimensions.get('comprehensive_score', 0)} 分"),
                ("评估状态", five_dimensions.get("status", "unknown")),
                ("评估说明", five_dimensions.get("message", ""))
            ]))
            lines.append("")

            # 各维度评分表格
            dimension_scores = five_dimensions.get("dimension_scores", {})
            lines.append(TableTemplate._render_dimensions_table(dimension_scores))
            lines.append("")

        # 承诺清单
        promise_list = report.get("promise_list", [])
        if promise_list:
            lines.append(TableTemplate._render_section_title("承诺清单"))
            lines.append(TableTemplate._render_promises_table(promise_list))
            lines.append("")

        # 建议列表
        recommendations = report.get("recommendations", [])
        if recommendations:
            lines.append(TableTemplate._render_section_title("建议"))
            for i, rec in enumerate(recommendations, 1):
                lines.append(f"{i}. {rec}")
            lines.append("")

        return "\n".join(lines)

    @staticmethod
    def _render_title(title: str) -> str:
        """渲染标题"""
        width = 80
        padding = (width - len(title) - 2) // 2
        line = TableTemplate.BORDER_HORIZONTAL * width

        return f"{TableTemplate.BORDER_TOP_LEFT}{line}{TableTemplate.BORDER_TOP_RIGHT}\n" \
               f"{TableTemplate.BORDER_VERTICAL}{' ' * padding}{title}{' ' * (width - padding - len(title))}{TableTemplate.BORDER_VERTICAL}\n" \
               f"{TableTemplate.BORDER_BOTTOM_LEFT}{line}{TableTemplate.BORDER_BOTTOM_RIGHT}"

    @staticmethod
    def _render_section_title(title: str) -> str:
        """渲染章节标题"""
        return f"\n{'═' * 80}\n{title}\n{'═' * 80}"

    @staticmethod
    def _render_key_value_table(items: List[tuple]) -> str:
        """渲染键值对表格"""
        if not items:
            return ""

        # 计算最大键长度
        max_key_len = max(len(str(k)) for k, v in items)
        col_width = max(max_key_len + 2, 20)

        lines = []

        # 表格顶部
        lines.append(
            f"{TableTemplate.BORDER_TOP_LEFT}"
            f"{TableTemplate.BORDER_HORIZONTAL * col_width}"
            f"{TableTemplate.BORDER_T_DOWN}"
            f"{TableTemplate.BORDER_HORIZONTAL * (78 - col_width)}"
            f"{TableTemplate.BORDER_TOP_RIGHT}"
        )

        # 表格内容
        for key, value in items:
            key_str = str(key).ljust(col_width - 2)
            value_str = str(value)

            lines.append(
                f"{TableTemplate.BORDER_VERTICAL} {key_str} "
                f"{TableTemplate.BORDER_VERTICAL} {value_str}"
            )

        # 表格底部
        lines.append(
            f"{TableTemplate.BORDER_BOTTOM_LEFT}"
            f"{TableTemplate.BORDER_HORIZONTAL * col_width}"
            f"{TableTemplate.BORDER_T_UP}"
            f"{TableTemplate.BORDER_HORIZONTAL * (78 - col_width)}"
            f"{TableTemplate.BORDER_BOTTOM_RIGHT}"
        )

        return "\n".join(lines)

    @staticmethod
    def _render_dimensions_table(dimension_scores: Dict[str, Any]) -> str:
        """渲染五维评分表格"""
        lines = []
        lines.append("各维度评分:")
        lines.append("")

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

        return "\n".join(lines)

    @staticmethod
    def _render_promises_table(promise_list: List[Dict[str, Any]]) -> str:
        """渲染承诺清单表格"""
        lines = []

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

        return "\n".join(lines)

