"""
输出格式化模块

支持 table, json, markdown 三种输出格式
"""
import json
from typing import Dict, List, Any


class TableFormatter:
    """Table 格式输出"""

    @staticmethod
    def format(data: Dict[str, Any]) -> str:
        """格式化为表格"""
        if "projects" in data:
            return TableFormatter._format_projects(data["projects"])
        elif "promises" in data:
            return TableFormatter._format_promises(data)
        else:
            return str(data)

    @staticmethod
    def _format_projects(projects: List[Dict]) -> str:
        """格式化项目列表"""
        lines = []
        lines.append("┌" + "─" * 78 + "┐")
        lines.append(f"│ {'ID':<5} │ {'项目名称':<20} │ {'承诺数':<10} │ {'创建时间':<20} │")
        lines.append("├" + "─" * 78 + "┤")

        for project in projects:
            lines.append(
                f"│ {project['id']:<5} │ {project['name']:<20} │ "
                f"{project.get('promises_count', 0):<10} │ "
                f"{project.get('created_at', 'N/A'):<20} │"
            )

        lines.append("└" + "─" * 78 + "┘")
        return "\n".join(lines)

    @staticmethod
    def _format_promises(data: Dict) -> str:
        """格式化承诺列表"""
        lines = []
        project = data['project']
        promises = data['promises']
        latest_verification = data.get('latest_verification')
        
        # 项目信息
        lines.append(f"\n项目: {project['name']}")
        lines.append(f"Twitter: {project.get('twitter_account', 'N/A')}")
        lines.append(f"网站: {project.get('website_url', 'N/A')}\n")
        
        # 验证摘要
        if latest_verification:
            lines.append("=" * 80)
            lines.append("最新验证结果")
            lines.append("=" * 80)
            lines.append(f"验证时间: {latest_verification.get('verification_time', 'N/A')}")
            lines.append(f"诚信评分: {latest_verification.get('integrity_score', 0):.2f} 分")
            lines.append(f"承诺总数: {latest_verification.get('total_promises', 0)}")
            lines.append(f"已兑现: {latest_verification.get('fulfilled_count', 0)}")
            lines.append(f"未兑现: {latest_verification.get('unfulfilled_count', 0)}")
            lines.append(f"无法验证: {latest_verification.get('unverifiable_count', 0)}")
            lines.append("")
        
        # 五维评分
        five_dimensions_score = data.get('five_dimensions_score')
        if five_dimensions_score:
            lines.append("=" * 80)
            lines.append("画饼指数与五维评分")
            lines.append("=" * 80)
            lines.append(f"画饼指数: {five_dimensions_score.get('promise_breaking_index', 0)} 分")
            lines.append(f"综合评分: {five_dimensions_score.get('comprehensive_score', 0)} 分")
            lines.append(f"评估状态: {five_dimensions_score.get('status', 'unknown')}")
            lines.append(f"评估说明: {five_dimensions_score.get('message', '')}")
            lines.append("")
            
            # 各维度评分
            five_dims = five_dimensions_score.get('five_dimensions', {})
            lines.append("各维度评分:")
            
            dimension_names = {
                "integrity": "诚信审计",
                "fairness": "公平性审计",
                "activity": "开发力审计",
                "stability": "财务稳定性审计",
                "momentum": "社区动能审计"
            }
            
            for dim_key, dim_name in dimension_names.items():
                dim_data = five_dims.get(dim_key, {})
                score = dim_data.get("score")
                status = dim_data.get("status", "unknown")
                
                if score is not None:
                    lines.append(f"  • {dim_name}: {score} 分 (状态: {status})")
                else:
                    lines.append(f"  • {dim_name}: 数据不可用")
            
            lines.append("")
        
        # 承诺列表
        lines.append("┌" + "─" * 118 + "┐")
        lines.append(
            f"│ {'ID':<5} │ {'承诺内容':<35} │ {'类型':<12} │ "
            f"{'验证状态':<10} │ {'来源':<12} │ {'目标日期':<15} │"
        )
        lines.append("├" + "─" * 118 + "┤")

        for promise in promises:
            content = promise["content"][:33] + ".." if len(promise["content"]) > 35 else promise["content"]
            promise_type = promise.get("promise_type", "N/A")[:10]
            verification_status = promise.get("verification_status", "pending")
            
            # 状态图标
            status_icon = {
                "fulfilled": "✅",
                "broken": "❌",
                "unverifiable": "❓",
                "pending": "⏳"
            }.get(verification_status, "")
            
            status_display = f"{status_icon} {verification_status}"[:10]
            source_type = promise.get("source_type", "N/A")[:10]
            target_date = promise.get("target_date", "N/A")[:13] if promise.get("target_date") else "N/A"
            
            lines.append(
                f"│ {promise.get('id', 'N/A'):<5} │ {content:<35} │ "
                f"{promise_type:<12} │ {status_display:<10} │ "
                f"{source_type:<12} │ {target_date:<15} │"
            )

        lines.append("└" + "─" * 118 + "┘")
        
        # 验证历史
        verification_history = data.get('verification_history', [])
        if verification_history and len(verification_history) > 1:
            lines.append("\n" + "=" * 80)
            lines.append("验证历史（最近 5 次）")
            lines.append("=" * 80)
            for record in verification_history:
                lines.append(
                    f"{record.get('verification_time', 'N/A')[:19]} | "
                    f"评分: {record.get('integrity_score', 0):.2f} | "
                    f"已兑现: {record.get('fulfilled_count', 0)} | "
                    f"未兑现: {record.get('unfulfilled_count', 0)}"
                )
        
        return "\n".join(lines)


class JSONFormatter:
    """JSON 格式输出"""

    @staticmethod
    def format(data: Dict[str, Any]) -> str:
        """格式化为 JSON"""
        return json.dumps(data, ensure_ascii=False, indent=2)


class MarkdownFormatter:
    """Markdown 格式输出"""

    @staticmethod
    def format(data: Dict[str, Any]) -> str:
        """格式化为 Markdown"""
        if "projects" in data:
            return MarkdownFormatter._format_projects(data["projects"])
        elif "promises" in data:
            return MarkdownFormatter._format_promises(data)
        else:
            return json.dumps(data, ensure_ascii=False, indent=2)

    @staticmethod
    def _format_projects(projects: List[Dict]) -> str:
        """格式化项目列表"""
        lines = ["# 项目列表\n"]

        for project in projects:
            lines.append(f"## {project['name']}")
            lines.append(f"- **ID**: {project['id']}")
            lines.append(f"- **承诺数**: {project.get('promises_count', 0)}")
            lines.append(f"- **创建时间**: {project.get('created_at', 'N/A')}")
            lines.append("")

        return "\n".join(lines)

    @staticmethod
    def _format_promises(data: Dict) -> str:
        """格式化承诺列表"""
        lines = []
        project = data['project']
        promises = data['promises']
        latest_verification = data.get('latest_verification')
        
        # 项目标题
        lines.append(f"# {project['name']}\n")
        
        # 项目信息
        lines.append("## 项目信息\n")
        lines.append(f"- **Twitter**: {project.get('twitter_account', 'N/A')}")
        lines.append(f"- **网站**: {project.get('website_url', 'N/A')}")
        lines.append(f"- **合约地址**: {project.get('contract_address', 'N/A')}")
        lines.append(f"- **国库地址**: {project.get('treasury_address', 'N/A')}")
        lines.append("")
        
        # 验证摘要
        if latest_verification:
            lines.append("## 最新验证结果\n")
            lines.append(f"- **验证时间**: {latest_verification.get('verification_time', 'N/A')}")
            lines.append(f"- **诚信评分**: {latest_verification.get('integrity_score', 0):.2f} 分")
            lines.append(f"- **画饼指数**: {latest_verification.get('promise_breaking_index', 0):.2f}")
            lines.append(f"- **承诺总数**: {latest_verification.get('total_promises', 0)}")
            lines.append(f"- **已兑现**: {latest_verification.get('fulfilled_count', 0)}")
            lines.append(f"- **未兑现**: {latest_verification.get('unfulfilled_count', 0)}")
            lines.append(f"- **无法验证**: {latest_verification.get('unverifiable_count', 0)}")
            
            # 计算兑现率
            total = latest_verification.get('total_promises', 0)
            fulfilled = latest_verification.get('fulfilled_count', 0)
            if total > 0:
                fulfillment_rate = (fulfilled / total) * 100
                lines.append(f"- **兑现率**: {fulfillment_rate:.2f}%")
            lines.append("")
        
        # 承诺列表
        lines.append("## 承诺清单\n")
        
        for i, promise in enumerate(promises, 1):
            verification_status = promise.get("verification_status", "pending")
            
            # 状态图标
            status_icon = {
                "fulfilled": "✅",
                "broken": "❌",
                "unverifiable": "❓",
                "pending": "⏳"
            }.get(verification_status, "")
            
            lines.append(f"### {i}. {status_icon} {promise['content']}\n")
            lines.append(f"- **类型**: {promise.get('promise_type', 'N/A')}")
            lines.append(f"- **验证状态**: {verification_status}")
            
            if promise.get('target_date'):
                lines.append(f"- **目标日期**: {promise['target_date']}")
            
            # 显示来源
            sources = promise.get('sources', [])
            if sources:
                lines.append(f"- **来源**:")
                for source in sources:
                    if isinstance(source, dict):
                        source_type = source.get('source_type', 'unknown')
                        source_url = source.get('source_url', '#')
                        lines.append(f"  - [{source_type}]({source_url})")
            
            lines.append("")
        
        # 验证历史
        verification_history = data.get('verification_history', [])
        if verification_history and len(verification_history) > 1:
            lines.append("## 验证历史\n")
            lines.append("| 验证时间 | 诚信评分 | 已兑现 | 未兑现 | 无法验证 |")
            lines.append("|---------|---------|--------|--------|----------|")
            
            for record in verification_history:
                verification_time = record.get('verification_time', 'N/A')[:19]
                integrity_score = record.get('integrity_score', 0)
                fulfilled = record.get('fulfilled_count', 0)
                unfulfilled = record.get('unfulfilled_count', 0)
                unverifiable = record.get('unverifiable_count', 0)
                
                lines.append(
                    f"| {verification_time} | {integrity_score:.2f} | "
                    f"{fulfilled} | {unfulfilled} | {unverifiable} |"
                )
            lines.append("")
        
        return "\n".join(lines)


def get_formatter(format_type: str):
    """获取格式化器"""
    formatters = {
        "table": TableFormatter,
        "json": JSONFormatter,
        "markdown": MarkdownFormatter
    }

    formatter = formatters.get(format_type)
    if not formatter:
        raise ValueError(f"不支持的格式: {format_type}")

    return formatter
