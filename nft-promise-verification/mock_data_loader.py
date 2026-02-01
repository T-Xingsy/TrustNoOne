#!/usr/bin/env python3
"""
Mock 数据加载器

功能：
1. 读取 mock_projects.json 文件
2. 将数据转换为数据库格式
3. 批量导入到 SQLite 数据库
4. 支持清空现有数据重新导入

使用方法：
    python mock_data_loader.py --clear  # 清空数据库并导入
    python mock_data_loader.py          # 追加导入（跳过已存在的项目）
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import structlog

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from database.db import DatabaseManager
from database.init_db import init_database
from config.settings import settings

logger = structlog.get_logger(__name__)


class MockDataLoader:
    """Mock 数据加载器"""

    def __init__(self, db_manager: DatabaseManager):
        """
        初始化加载器

        Args:
            db_manager: 数据库管理器实例
        """
        self.db_manager = db_manager
        self.mock_file = project_root / "mock_projects.json"

    def load_mock_data(self) -> Dict[str, Any]:
        """
        从 JSON 文件加载 mock 数据

        Returns:
            包含项目列表和元数据的字典
        """
        if not self.mock_file.exists():
            raise FileNotFoundError(f"Mock 数据文件不存在: {self.mock_file}")

        with open(self.mock_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        logger.info(
            "Mock 数据加载成功",
            total_projects=data["metadata"]["total_projects"],
            total_promises=data["metadata"]["total_promises"]
        )

        return data

    def import_project(self, project_data: Dict[str, Any]) -> str:
        """
        导入单个项目到数据库

        Args:
            project_data: 项目数据字典

        Returns:
            项目 ID
        """
        # 1. 创建项目记录
        project_id = self.db_manager.create_project(
            name=project_data["name"],
            twitter_account=project_data.get("twitter_account"),
            website_url=project_data.get("website_url"),
            contract_address=project_data.get("contract_address"),
            treasury_address=project_data.get("treasury_address"),
            github_repo=project_data.get("github_repo"),
            opensea_slug=project_data.get("opensea_slug")
        )

        logger.info(
            "项目创建成功",
            project_id=project_id,
            project_name=project_data["name"]
        )

        # 2. 导入承诺数据
        promises_imported = 0
        for promise_data in project_data.get("promises", []):
            try:
                self._import_promise(promise_data, project_id)
                promises_imported += 1
            except Exception as e:
                logger.error(
                    "承诺导入失败",
                    promise_content=promise_data.get("content", "")[:50],
                    error=str(e)
                )

        logger.info(
            "承诺导入完成",
            project_id=project_id,
            promises_imported=promises_imported,
            total_promises=len(project_data.get("promises", []))
        )

        # 3. 如果有验证结果，创建验证记录
        if "expected_scores" in project_data:
            self._create_verification_record(project_data, project_id)

        return project_id

    def _import_promise(self, promise_data: Dict[str, Any], project_id: str):
        """
        导入单个承诺

        Args:
            promise_data: 承诺数据字典
            project_id: 项目 ID
        """
        # 转换日期格式
        target_date = None
        if promise_data.get("target_date"):
            target_date = datetime.fromisoformat(
                promise_data["target_date"].replace("Z", "+00:00")
            )

        # 构建承诺数据
        promise_dict = {
            "project_id": project_id,
            "content": promise_data["content"],
            "sources": promise_data.get("sources", []),
            "promise_type": promise_data.get("promise_type", "OTHER"),
            "target_date": target_date,
            "verification_status": promise_data.get("verification_status", "PENDING"),
            "importance_weight": promise_data.get("importance_weight", 1.0),
            "confidence": promise_data.get("confidence", 0.0),
            "verifiable": promise_data.get("verifiable", False)
        }

        # 创建承诺记录
        promise_id = self.db_manager.create_promise(**promise_dict)

    def _create_verification_record(
        self,
        project_data: Dict[str, Any],
        project_id: str
    ):
        """
        创建验证记录

        Args:
            project_data: 项目数据字典
            project_id: 项目 ID
        """
        expected_scores = project_data["expected_scores"]

        # 统计承诺验证状态（只统计已验证的承诺，排除 pending 状态）
        promises = project_data.get("promises", [])
        verified_promises = [
            p for p in promises
            if p.get("verification_status") != "pending"
        ]
        fulfilled_count = sum(
            1 for p in verified_promises
            if p.get("verification_status") == "fulfilled"
        )
        unfulfilled_count = sum(
            1 for p in verified_promises
            if p.get("verification_status") == "unfulfilled"
        )
        unverifiable_count = sum(
            1 for p in verified_promises
            if p.get("verification_status") == "unverifiable"
        )

        # 生成风险等级和摘要
        pbi = expected_scores.get("promise_breaking_index", 0)
        if pbi < 30:
            risk_level = "低风险"
            risk_desc = "项目整体表现良好，承诺履行率高"
        elif pbi < 60:
            risk_level = "中风险"
            risk_desc = "项目存在一定风险，部分承诺未能履行"
        else:
            risk_level = "高风险"
            risk_desc = "项目风险较高，大量承诺未能履行"

        # 构建承诺分析列表
        promise_analysis = []
        for promise in promises:
            analysis = {
                "promise_id": promise.get("id", ""),
                "content": promise.get("content", ""),
                "type": promise.get("promise_type", ""),
                "status": promise.get("verification_status", ""),
                "analysis": f"承诺类型：{promise.get('promise_type', '')}，验证状态：{promise.get('verification_status', '')}"
            }
            promise_analysis.append(analysis)

        # 生成建议列表
        recommendations = []
        if unfulfilled_count > 0:
            recommendations.append(f"项目有 {unfulfilled_count} 个未履行承诺，建议关注项目方的执行能力")
        if unverifiable_count > 0:
            recommendations.append(f"项目有 {unverifiable_count} 个无法验证的承诺，建议要求项目方提供更多证据")
        if pbi >= 60:
            recommendations.append("项目画饼指数较高，建议谨慎投资")
        elif pbi >= 30:
            recommendations.append("项目存在一定风险，建议持续关注项目进展")
        else:
            recommendations.append("项目整体表现良好，可以考虑投资")

        # 构建报告详情（符合 ReportDetails 模型）
        report_details = {
            "summary": f"{project_data['name']} 项目评估：{risk_level}（画饼指数：{pbi}）。{risk_desc}。共有 {len(promises)} 个承诺，其中 {fulfilled_count} 个已履行，{unfulfilled_count} 个未履行，{unverifiable_count} 个无法验证。",
            "five_dimensions": {
                "integrity": {
                    "score": expected_scores.get("integrity_score", 0),
                    "weight": 30
                },
                "fairness": {
                    "score": expected_scores.get("fairness_score", 0),
                    "weight": 20
                },
                "activity": {
                    "score": expected_scores.get("activity_score", 0),
                    "weight": 20
                },
                "stability": {
                    "score": expected_scores.get("stability_score", 0),
                    "weight": 15
                },
                "momentum": {
                    "score": expected_scores.get("momentum_score", 0),
                    "weight": 15
                }
            },
            "promise_analysis": promise_analysis,
            "recommendations": recommendations
        }

        # 创建验证记录
        record_dict = {
            "project_id": project_id,
            "verification_time": datetime.utcnow(),
            "promise_breaking_index": expected_scores.get("promise_breaking_index", 0),
            "integrity_score": expected_scores.get("integrity_score", 0),
            "fairness_score": expected_scores.get("fairness_score", 0),
            "activity_score": expected_scores.get("activity_score", 0),
            "stability_score": expected_scores.get("stability_score", 0),
            "momentum_score": expected_scores.get("momentum_score", 0),
            "total_promises": len(verified_promises),  # 只统计已验证的承诺
            "fulfilled_count": fulfilled_count,
            "unfulfilled_count": unfulfilled_count,
            "unverifiable_count": unverifiable_count,
            "report_details": report_details
        }

        # 调试信息
        logger.info(
            "验证记录数据",
            project_name=project_data["name"],
            total_promises=len(verified_promises),
            fulfilled=fulfilled_count,
            unfulfilled=unfulfilled_count,
            unverifiable=unverifiable_count,
            sum=fulfilled_count + unfulfilled_count + unverifiable_count
        )

        self.db_manager.create_verification_record(**record_dict)

        logger.info(
            "验证记录创建成功",
            project_id=project_id,
            promise_breaking_index=expected_scores.get("promise_breaking_index", 0)
        )

    def import_all(self, clear_existing: bool = False) -> Dict[str, Any]:
        """
        导入所有 mock 数据

        Args:
            clear_existing: 是否清空现有数据

        Returns:
            导入结果统计
        """
        # 加载 mock 数据
        data = self.load_mock_data()

        # 如果需要清空现有数据
        if clear_existing:
            logger.warning("清空现有数据库...")
            # 删除数据库文件
            if Path(self.db_manager.db_path).exists():
                Path(self.db_manager.db_path).unlink()
                logger.info("数据库文件已删除")
            # 重新初始化数据库
            init_database(self.db_manager.db_path)
            logger.info("数据库已重新初始化")

        # 导入项目
        imported_projects = []
        skipped_projects = []

        for project_data in data["projects"]:
            try:
                # 检查项目是否已存在
                existing_projects = self.db_manager.list_projects()
                if any(p["name"] == project_data["name"] for p in existing_projects):
                    logger.info(
                        "项目已存在，跳过",
                        project_name=project_data["name"]
                    )
                    skipped_projects.append(project_data["name"])
                    continue

                # 导入项目
                project_id = self.import_project(project_data)
                imported_projects.append({
                    "id": project_id,
                    "name": project_data["name"]
                })

            except Exception as e:
                logger.error(
                    "项目导入失败",
                    project_name=project_data["name"],
                    error=str(e)
                )
                skipped_projects.append(project_data["name"])

        # 返回导入结果
        result = {
            "success": True,
            "imported_count": len(imported_projects),
            "skipped_count": len(skipped_projects),
            "imported_projects": imported_projects,
            "skipped_projects": skipped_projects
        }

        logger.info(
            "Mock 数据导入完成",
            imported_count=len(imported_projects),
            skipped_count=len(skipped_projects)
        )

        return result


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="Mock 数据加载器")
    parser.add_argument(
        "--clear",
        action="store_true",
        help="清空现有数据库并重新导入"
    )
    args = parser.parse_args()

    # 初始化数据库
    db_path = project_root / "data" / "promises.db"
    db_path.parent.mkdir(parents=True, exist_ok=True)

    if not db_path.exists() or args.clear:
        if args.clear and db_path.exists():
            db_path.unlink()
        init_database(str(db_path))

    # 创建数据库管理器
    db_manager = DatabaseManager(str(db_path))

    # 创建加载器并导入数据
    loader = MockDataLoader(db_manager)
    result = loader.import_all(clear_existing=args.clear)

    # 打印结果
    print("\n" + "=" * 60)
    print("Mock 数据导入结果")
    print("=" * 60)
    print(f"✅ 成功导入: {result['imported_count']} 个项目")
    print(f"⏭️  跳过: {result['skipped_count']} 个项目")
    print("\n导入的项目:")
    for project in result["imported_projects"]:
        print(f"  - {project['name']} (ID: {project['id']})")
    if result["skipped_projects"]:
        print("\n跳过的项目:")
        for name in result["skipped_projects"]:
            print(f"  - {name}")
    print("=" * 60)


if __name__ == "__main__":
    main()
