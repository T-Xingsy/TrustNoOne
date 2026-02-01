#!/usr/bin/env python3
"""
NFT 承诺验证演示脚本

功能：
1. 交互式输入项目信息（或使用预设项目）
2. 从数据库查询项目数据
3. 生成五维评分和画饼指数
4. 输出详细的验证报告

使用方法：
    # 交互式模式
    python demo.py

    # 使用预设项目
    python demo.py --project "Azuki"

    # 指定输出格式
    python demo.py --project "Moonbirds" --format json

    # 导出报告到文件
    python demo.py --project "PixelmonNFT" --output report.md
"""

import sys
from pathlib import Path
from typing import Optional, Dict, Any
import structlog

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from database.db import DatabaseManager
from database.init_db import init_database
from reports.report_generator import ReportGenerator
from config.settings import settings

logger = structlog.get_logger(__name__)


class DemoRunner:
    """演示脚本运行器"""

    def __init__(self, db_manager: DatabaseManager):
        """
        初始化运行器

        Args:
            db_manager: 数据库管理器实例
        """
        self.db_manager = db_manager
        self.report_generator = ReportGenerator()

    def list_available_projects(self) -> list[Dict[str, Any]]:
        """
        列出所有可用的项目

        Returns:
            项目列表
        """
        projects = self.db_manager.list_projects()
        return projects

    def get_project_by_name(self, project_name: str) -> Optional[Dict[str, Any]]:
        """
        根据项目名称获取项目信息

        Args:
            project_name: 项目名称

        Returns:
            项目信息字典，如果不存在则返回 None
        """
        projects = self.db_manager.list_projects()
        for project in projects:
            if project["name"].lower() == project_name.lower():
                return self.db_manager.get_project(project["id"])
        return None

    def generate_report(
        self,
        project_id: str,
        format: str = "text"
    ) -> Dict[str, Any]:
        """
        生成项目验证报告

        Args:
            project_id: 项目 ID
            format: 输出格式（text/json/markdown）

        Returns:
            报告数据
        """
        # 1. 获取项目信息
        project = self.db_manager.get_project(project_id)
        if not project:
            raise ValueError(f"项目不存在: {project_id}")

        # 2. 获取承诺列表
        promises = self.db_manager.get_promises_by_project(project_id)

        # 3. 获取最新的验证记录
        verification_record = self.db_manager.get_latest_verification_record(project_id)

        if not verification_record:
            logger.warning(
                "项目没有验证记录，将生成基础报告",
                project_id=project_id
            )
            # 生成基础报告（没有验证结果）
            report = self._generate_basic_report(project, promises)
        else:
            # 生成完整报告（包含验证结果和五维评分）
            report = self._generate_full_report(
                project,
                promises,
                verification_record
            )

        # 4. 格式化输出
        if format == "json":
            import json
            return {"report": report, "formatted": json.dumps(report, indent=2, ensure_ascii=False)}
        elif format == "markdown":
            formatted = self.report_generator.format_report_as_markdown(report)
            return {"report": report, "formatted": formatted}
        else:  # text
            formatted = self.report_generator.format_report_as_text(report)
            return {"report": report, "formatted": formatted}

    def _generate_basic_report(
        self,
        project: Dict[str, Any],
        promises: list[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        生成基础报告（没有验证结果）

        Args:
            project: 项目信息
            promises: 承诺列表

        Returns:
            报告数据
        """
        return {
            "report_id": f"report_{project['id']}_basic",
            "generated_at": "2026-01-31T00:00:00Z",
            "header": {
                "project_name": project["name"],
                "twitter_account": project.get("twitter_account"),
                "website_url": project.get("website_url"),
                "contract_address": project.get("contract_address")
            },
            "promise_list": promises,
            "verification_summary": {
                "total": len(promises),
                "fulfilled": 0,
                "unfulfilled": 0,
                "unverifiable": 0,
                "pending": len(promises)
            },
            "message": "该项目尚未进行验证，请先运行验证流程"
        }

    def _generate_full_report(
        self,
        project: Dict[str, Any],
        promises: list[Dict[str, Any]],
        verification_record: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        生成完整报告（包含验证结果和五维评分）

        Args:
            project: 项目信息
            promises: 承诺列表
            verification_record: 验证记录

        Returns:
            报告数据
        """
        # 从验证记录中提取报告详情
        report_details = verification_record.get("report_details", {})
        
        # 计算兑现率
        total = verification_record["total_promises"]
        fulfilled = verification_record["fulfilled_count"]
        fulfillment_rate = (fulfilled / total * 100) if total > 0 else 0
        
        # 获取画饼指数和综合评分
        pbi = verification_record["promise_breaking_index"]
        comprehensive_score = 100 - pbi
        
        # 构建完整报告
        report = {
            "report_id": f"report_{project['id']}_{verification_record['id']}",
            "generated_at": verification_record["verification_time"],
            "header": {
                "project_name": project["name"],
                "project_id": project["id"],
                "twitter_account": project.get("twitter_account"),
                "website_url": project.get("website_url"),
                "contract_address": project.get("contract_address"),
                "treasury_address": project.get("treasury_address"),
                "github_repo": project.get("github_repo"),
                "opensea_slug": project.get("opensea_slug"),
                "network": project.get("network")
            },
            "promise_list": promises,
            "verification_summary": {
                "total_promises": total,
                "fulfilled_count": fulfilled,
                "broken_count": verification_record["unfulfilled_count"],
                "unverifiable_count": verification_record["unverifiable_count"],
                "fulfillment_rate": round(fulfillment_rate, 2),
                "integrity_score": verification_record["integrity_score"],
                "integrity_status": self._get_score_status(verification_record["integrity_score"]),
                "integrity_message": f"诚信审计得分 {verification_record['integrity_score']} 分"
            },
            "five_dimensions": {
                "promise_breaking_index": pbi,
                "comprehensive_score": comprehensive_score,
                "status": self._get_risk_level(pbi),
                "message": f"画饼指数 {pbi} 分，综合评分 {comprehensive_score} 分",
                "dimension_scores": {
                    "integrity": {
                        "name": "诚信审计",
                        "score": verification_record["integrity_score"],
                        "weight": 0.30,
                        "status": self._get_score_status(verification_record["integrity_score"])
                    },
                    "fairness": {
                        "name": "公平性审计",
                        "score": verification_record["fairness_score"],
                        "weight": 0.20,
                        "status": self._get_score_status(verification_record["fairness_score"])
                    },
                    "activity": {
                        "name": "开发力审计",
                        "score": verification_record["activity_score"],
                        "weight": 0.20,
                        "status": self._get_score_status(verification_record["activity_score"])
                    },
                    "stability": {
                        "name": "财务稳定性",
                        "score": verification_record["stability_score"],
                        "weight": 0.15,
                        "status": self._get_score_status(verification_record["stability_score"])
                    },
                    "momentum": {
                        "name": "社区动能",
                        "score": verification_record["momentum_score"],
                        "weight": 0.15,
                        "status": self._get_score_status(verification_record["momentum_score"])
                    }
                }
            },
            "recommendations": report_details.get("recommendations", self._generate_recommendations(verification_record))
        }

        return report

    def _get_score_status(self, score: float) -> str:
        """
        根据分数获取状态标签

        Args:
            score: 分数（0-100）

        Returns:
            状态标签
        """
        if score >= 80:
            return "excellent"
        elif score >= 60:
            return "good"
        elif score >= 40:
            return "fair"
        elif score >= 20:
            return "poor"
        else:
            return "critical"

    def _get_risk_level(self, promise_breaking_index: float) -> Dict[str, str]:
        """
        根据画饼指数获取风险等级

        Args:
            promise_breaking_index: 画饼指数（0-100）

        Returns:
            风险等级信息
        """
        if promise_breaking_index <= 20:
            return {"level": "low", "label": "可信/几乎不画饼", "color": "#00ff88"}
        elif promise_breaking_index <= 40:
            return {"level": "low-medium", "label": "较可靠/轻度画饼", "color": "#88ff00"}
        elif promise_breaking_index <= 60:
            return {"level": "medium", "label": "一般/中度画饼", "color": "#ffaa00"}
        elif promise_breaking_index <= 80:
            return {"level": "high", "label": "较差/严重画饼", "color": "#ff6600"}
        else:
            return {"level": "critical", "label": "极差/极度画饼", "color": "#ff2d2d"}

    def _generate_recommendations(
        self,
        verification_record: Dict[str, Any]
    ) -> list[str]:
        """
        生成建议列表

        Args:
            verification_record: 验证记录

        Returns:
            建议列表
        """
        recommendations = []

        # 根据画饼指数给出建议
        pbi = verification_record["promise_breaking_index"]
        if pbi > 60:
            recommendations.append("⚠️ 该项目画饼指数较高，建议谨慎投资")
            recommendations.append("🔍 建议深入调查项目方的历史记录和团队背景")
        elif pbi > 40:
            recommendations.append("⚡ 该项目存在一定风险，建议持续关注项目进展")
        else:
            recommendations.append("✅ 该项目整体表现良好，承诺兑现率较高")

        # 根据各维度得分给出建议
        if verification_record["integrity_score"] < 50:
            recommendations.append("📉 诚信审计得分较低，项目方承诺兑现率不佳")

        if verification_record["fairness_score"] < 50:
            recommendations.append("⚖️ 公平性审计得分较低，NFT 分配可能存在问题")

        if verification_record["activity_score"] < 50:
            recommendations.append("💻 开发力审计得分较低，项目开发活跃度不足")

        if verification_record["stability_score"] < 50:
            recommendations.append("💰 财务稳定性得分较低，项目资金管理存在风险")

        if verification_record["momentum_score"] < 50:
            recommendations.append("📊 社区动能得分较低，社区活跃度和市场热度下降")

        return recommendations

    def interactive_mode(self):
        """交互式模式"""
        print("\n" + "=" * 60)
        print("🔍 NFT 承诺验证演示系统")
        print("=" * 60)

        # 列出可用项目
        projects = self.list_available_projects()
        if not projects:
            print("\n❌ 数据库中没有项目数据")
            print("💡 请先运行: python mock_data_loader.py --clear")
            return

        print("\n可用项目:")
        for i, project in enumerate(projects, 1):
            print(f"  {i}. {project['name']}")

        # 选择项目
        while True:
            try:
                choice = input("\n请选择项目编号（或输入 q 退出）: ").strip()
                if choice.lower() == 'q':
                    return

                index = int(choice) - 1
                if 0 <= index < len(projects):
                    selected_project = projects[index]
                    break
                else:
                    print("❌ 无效的编号，请重新输入")
            except ValueError:
                print("❌ 请输入有效的数字")

        # 选择输出格式
        print("\n输出格式:")
        print("  1. 文本格式（text）")
        print("  2. JSON 格式（json）")
        print("  3. Markdown 格式（markdown）")

        format_choice = input("\n请选择格式（默认: text）: ").strip() or "1"
        format_map = {"1": "text", "2": "json", "3": "markdown"}
        output_format = format_map.get(format_choice, "text")

        # 生成报告
        print(f"\n⏳ 正在生成 {selected_project['name']} 的验证报告...")
        try:
            result = self.generate_report(selected_project["id"], format=output_format)
            print("\n" + "=" * 60)
            print(result["formatted"])
            print("=" * 60)

            # 询问是否导出到文件
            export = input("\n是否导出到文件？(y/n): ").strip().lower()
            if export == 'y':
                filename = input("请输入文件名（��认: report.txt）: ").strip() or "report.txt"
                output_path = project_root / filename
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(result["formatted"])
                print(f"✅ 报告已导出到: {output_path}")

        except Exception as e:
            logger.error("报告生成失败", error=str(e))
            print(f"\n❌ 报告生成失败: {e}")


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="NFT 承诺验证演示脚本")
    parser.add_argument(
        "--project",
        type=str,
        help="项目名称（例如: Azuki）"
    )
    parser.add_argument(
        "--format",
        type=str,
        choices=["text", "json", "markdown"],
        default="text",
        help="输出格式"
    )
    parser.add_argument(
        "--output",
        type=str,
        help="输出文件路径"
    )
    args = parser.parse_args()

    # 初始化数据库
    db_path = project_root / "data" / "promises.db"
    if not db_path.exists():
        print("❌ 数据库不存在，请先运行: python mock_data_loader.py --clear")
        sys.exit(1)

    db_manager = DatabaseManager(str(db_path))
    runner = DemoRunner(db_manager)

    # 如果指定了项目名称，直接生成报告
    if args.project:
        project = runner.get_project_by_name(args.project)
        if not project:
            print(f"❌ 项目不存在: {args.project}")
            print("\n可用项目:")
            for p in runner.list_available_projects():
                print(f"  - {p['name']}")
            sys.exit(1)

        print(f"⏳ 正在生成 {args.project} 的验证报告...")
        result = runner.generate_report(project["id"], format=args.format)

        # 输出或保存报告
        if args.output:
            output_path = Path(args.output)
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(result["formatted"])
            print(f"✅ 报告已导出到: {output_path}")
        else:
            print("\n" + "=" * 60)
            print(result["formatted"])
            print("=" * 60)
    else:
        # 交互式模式
        runner.interactive_mode()


if __name__ == "__main__":
    main()
