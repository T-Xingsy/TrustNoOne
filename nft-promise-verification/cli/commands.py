"""
CLI 命令实现

实现 collect, list, show, export, verify 命令
"""
import json
from typing import Dict, Any
from datetime import datetime
import structlog

logger = structlog.get_logger(__name__)


class CollectCommand:
    """collect 命令实现"""

    def __init__(self, agent, db_manager):
        self.agent = agent
        self.db_manager = db_manager

    def execute(self, args) -> Dict[str, Any]:
        """
        执行 collect 命令

        Args:
            args: 命令行参数

        Returns:
            执行结果
        """
        logger.info(
            "执行 collect 命令",
            name=args.name,
            twitter=args.twitter,
            website=args.website
        )

        # 调用 Agent 收集承诺
        result = self.agent.collect_promises(
            project_name=args.name,
            twitter_username=args.twitter,
            website_url=args.website,
            max_tweets=args.max_tweets
        )

        return result


class ListCommand:
    """list 命令实现"""

    def __init__(self, db_manager):
        self.db_manager = db_manager

    def execute(self, args) -> Dict[str, Any]:
        """
        执行 list 命令

        Args:
            args: 命令行参数

        Returns:
            执行结果
        """
        logger.info(
            "执行 list 命令",
            sort=args.sort,
            limit=args.limit
        )

        # 从数据库查询项目列表
        projects = self.db_manager.list_projects(
            sort_by=args.sort,
            limit=args.limit
        )

        return {
            "projects": projects,
            "total_count": len(projects)
        }


class ShowCommand:
    """show 命令实现"""

    def __init__(self, db_manager, agent=None):
        self.db_manager = db_manager
        self.agent = agent

    def execute(self, args) -> Dict[str, Any]:
        """
        执行 show 命令

        Args:
            args: 命令行参数

        Returns:
            执行结果
        """
        logger.info(
            "执行 show 命令",
            project_id=args.project_id
        )

        # 查询项目详情
        project = self.db_manager.get_project(args.project_id)

        if not project:
            raise ValueError(f"项目不存在: {args.project_id}")

        # 查询承诺列表
        promises = self.db_manager.get_promises_by_project(args.project_id)

        # 查询最新验证记录
        latest_verification = self.db_manager.get_latest_verification_record(
            args.project_id
        )

        # 如果有验证记录，获取验证历史
        verification_history = []
        if latest_verification:
            verification_history = self.db_manager.get_verification_records_by_project(
                args.project_id,
                limit=5  # 最近 5 条记录
            )

        # 计算五维评分（如果 agent 可用且有验证记录）
        five_dimensions_score = None
        if self.agent and latest_verification:
            try:
                network = getattr(args, 'network', 'mainnet')
                five_dimensions_score = self.agent.calculate_five_dimensions_score(
                    args.project_id,
                    network=network
                )
                logger.info(
                    "五维评分计算完成",
                    project_id=args.project_id,
                    promise_breaking_index=five_dimensions_score.get("promise_breaking_index")
                )
            except Exception as e:
                logger.warning(
                    "五维评分计算失败",
                    project_id=args.project_id,
                    error=str(e)
                )

        return {
            "project": project,
            "promises": promises,
            "promises_count": len(promises),
            "latest_verification": latest_verification,
            "verification_history": verification_history,
            "has_verification": latest_verification is not None,
            "five_dimensions_score": five_dimensions_score
        }


class ExportCommand:
    """export 命令实现"""

    def __init__(self, db_manager, agent=None, report_generator=None):
        self.db_manager = db_manager
        self.agent = agent
        self.report_generator = report_generator

    def execute(self, args) -> Dict[str, Any]:
        """
        执行 export 命令

        Args:
            args: 命令行参数

        Returns:
            执行结果
        """
        logger.info(
            "执行 export 命令",
            project_id=args.project_id,
            format=args.format
        )

        # 查询项目和承诺
        project = self.db_manager.get_project(args.project_id)
        promises = self.db_manager.get_promises_by_project(args.project_id)

        if not project:
            raise ValueError(f"项目不存在: {args.project_id}")

        # 查询最新验证记录
        latest_verification = self.db_manager.get_latest_verification_record(
            args.project_id
        )

        # 计算五维评分（如果 agent 可用且有验证记录）
        five_dimensions_score = None
        if self.agent and latest_verification:
            try:
                network = getattr(args, 'network', 'mainnet')
                five_dimensions_score = self.agent.calculate_five_dimensions_score(
                    args.project_id,
                    network=network
                )
            except Exception as e:
                logger.warning(
                    "五维评分计算失败",
                    project_id=args.project_id,
                    error=str(e)
                )

        # 如果有 report_generator，生成完整报告
        if self.report_generator and latest_verification:
            # 获取验证结果
            verification_results = []  # 从数据库加载验证结果
            
            # 构建诚信评分数据
            integrity_score = {
                "score": latest_verification.get("integrity_score", 0),
                "status": "unknown",
                "message": "",
                "details": {}
            }

            # 生成完整报告
            report = self.report_generator.generate_verification_report(
                project=project,
                promises=promises,
                verification_results=verification_results,
                integrity_score=integrity_score,
                network=getattr(args, 'network', 'mainnet'),
                five_dimensions=five_dimensions_score
            )

            export_data = report
        else:
            # 构建简单导出数据
            export_data = {
                "project": project,
                "promises": promises,
                "latest_verification": latest_verification,
                "five_dimensions_score": five_dimensions_score,
                "export_format": args.format
            }

        # 如果指定了输出文件，写入文件
        if args.output:
            self._write_to_file(export_data, args.output, args.format)
            return {"message": f"已导出到 {args.output}"}

        return export_data

    def _write_to_file(self, data: Dict, filepath: str, format: str):
        """写入文件"""
        with open(filepath, "w", encoding="utf-8") as f:
            if format == "json":
                json.dump(data, f, ensure_ascii=False, indent=2)
            elif format == "markdown":
                # 简化的 Markdown 输出
                f.write(f"# {data['project']['name']}\n\n")
                f.write(f"## 项目信息\n\n")
                f.write(f"- Twitter: {data['project'].get('twitter_username', 'N/A')}\n")
                f.write(f"- 网站: {data['project'].get('website_url', 'N/A')}\n\n")
                f.write(f"## 承诺列表\n\n")
                for promise in data['promises']:
                    f.write(f"### {promise['content']}\n\n")
                    f.write(f"- 类别: {promise['category']}\n")
                    f.write(f"- 置信度: {promise['confidence']}\n")
                    f.write(f"- 来源: {promise['source_url']}\n\n")



class VerifyCommand:
    """verify 命令实现"""

    def __init__(self, agent, db_manager, report_generator):
        """
        初始化 verify 命令

        Args:
            agent: VerificationAgent 实例
            db_manager: DatabaseManager 实例
            report_generator: ReportGenerator 实例
        """
        self.agent = agent
        self.db_manager = db_manager
        self.report_generator = report_generator

    def execute(self, args) -> Dict[str, Any]:
        """
        执行 verify 命令

        Args:
            args: 命令行参数

        Returns:
            执行结果
        """
        logger.info(
            "执行 verify 命令",
            project_id=args.project_id,
            network=args.network
        )

        # 1. 验证项目是否存在
        project = self.db_manager.get_project(args.project_id)
        if not project:
            raise ValueError(f"项目不存在: {args.project_id}")

        # 2. 执行链上验证
        logger.info("开始链上验证", project_id=args.project_id)
        verification_result = self.agent.verify_promises(
            project_id=args.project_id,
            network=args.network
        )

        # 3. 获取验证数据
        promises = self.db_manager.get_promises_by_project(args.project_id)
        verification_results = verification_result.get("verification_results", [])
        integrity_score = verification_result.get("integrity_score", {})

        # 4. 生成验证报告
        logger.info("生成验证报告", project_id=args.project_id)
        report = self.report_generator.generate_verification_report(
            project=project,
            promises=promises,
            verification_results=verification_results,
            integrity_score=integrity_score,
            network=args.network
        )

        # 5. 保存验证记录到数据库
        logger.info("保存验证记录", project_id=args.project_id)
        verification_summary = verification_result.get("verification_summary", {})

        record_id = self.db_manager.create_verification_record(
            project_id=args.project_id,
            verification_time=datetime.utcnow(),
            promise_breaking_index=100 - integrity_score.get("score", 0),
            integrity_score=integrity_score.get("score", 0),
            fairness_score=0.0,  # 暂未实现
            activity_score=0.0,  # 暂未实现
            stability_score=0.0,  # 暂未实现
            momentum_score=0.0,  # 暂未实现
            total_promises=verification_summary.get("total_promises", 0),
            fulfilled_count=verification_summary.get("fulfilled_count", 0),
            unfulfilled_count=verification_summary.get("broken_count", 0),
            unverifiable_count=verification_summary.get("unverifiable_count", 0),
            report_details=report
        )

        # 6. 更新项目的最后验证时间
        self.db_manager.update_project_last_verified_at(
            project_id=args.project_id,
            verified_at=datetime.utcnow().isoformat()
        )

        logger.info(
            "验证完成",
            project_id=args.project_id,
            record_id=record_id,
            integrity_score=integrity_score.get("score")
        )

        return {
            "project_id": args.project_id,
            "project_name": project.get("name"),
            "verification_record_id": record_id,
            "report": report,
            "integrity_score": integrity_score,
            "verification_summary": verification_summary,
            "network": args.network
        }
