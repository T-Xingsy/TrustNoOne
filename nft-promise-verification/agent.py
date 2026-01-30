"""
VerificationAgent 基础实现

使用 SpoonReactAI 实现数据收集任务编排和链上验证
"""
from typing import Dict, List, Optional
from spoon_core.agents.react import SpoonReactAI
from spoon_core.tools.tool_manager import ToolManager
import structlog

from .utils.data_formatter import DataFormatter
from .utils.deduplicator import Deduplicator
from .database.db import DatabaseManager
from .utils.rpc_manager import RPCManager
from .tools.evm_tools import EVMTools
from .verification.promise_verifier import PromiseVerifier
from .scoring.integrity import IntegrityScorer
from .scoring.fairness import FairnessScorer
from .scoring.activity import ActivityScorer
from .scoring.stability import StabilityScorer
from .scoring.momentum import MomentumScorer
from .scoring.index_calculator import IndexCalculator

logger = structlog.get_logger(__name__)


class VerificationAgent:
    """NFT 项目承诺验证 Agent"""

    def __init__(
        self,
        llm_manager,
        tool_manager: ToolManager,
        db_manager: DatabaseManager,
        rpc_manager: Optional[RPCManager] = None
    ):
        """
        初始化 VerificationAgent

        Args:
            llm_manager: LLM 管理器
            tool_manager: 工具管理器
            db_manager: 数据库管理器
            rpc_manager: RPC 节点管理器（可选）
        """
        self.llm_manager = llm_manager
        self.tool_manager = tool_manager
        self.db_manager = db_manager

        # 初始化 SpoonReactAI
        self.agent = SpoonReactAI(
            llm_manager=llm_manager,
            tool_manager=tool_manager,
            max_iterations=10
        )

        # 初始化数据处理模块
        self.formatter = DataFormatter()
        self.deduplicator = Deduplicator(similarity_threshold=0.9)

        # 初始化链上验证模块
        self.rpc_manager = rpc_manager or RPCManager()
        self.evm_tools = EVMTools(self.rpc_manager)
        self.promise_verifier = PromiseVerifier(self.evm_tools)

        # 初始化评分模块
        self.integrity_scorer = IntegrityScorer()
        self.fairness_scorer = FairnessScorer()
        self.activity_scorer = ActivityScorer()
        self.stability_scorer = StabilityScorer()
        self.momentum_scorer = MomentumScorer()
        self.index_calculator = IndexCalculator()

        logger.info("VerificationAgent 初始化完成")

    def collect_promises(
        self,
        project_name: str,
        twitter_username: Optional[str] = None,
        website_url: Optional[str] = None,
        max_tweets: int = 100
    ) -> Dict:
        """
        收集项目承诺

        Args:
            project_name: 项目名称
            twitter_username: Twitter 用户名
            website_url: 官网 URL
            max_tweets: 最大推文数

        Returns:
            包含项目信息和承诺列表的字典
        """
        logger.info(
            "开始收集项目承诺",
            project_name=project_name,
            twitter=twitter_username,
            website=website_url
        )

        all_promises = []

        try:
            # 1. 收集 Twitter 数据
            if twitter_username:
                twitter_promises = self._collect_twitter_promises(
                    twitter_username,
                    max_tweets
                )
                all_promises.extend(twitter_promises)

            # 2. 收集网站数据
            if website_url:
                website_promises = self._collect_website_promises(
                    website_url
                )
                all_promises.extend(website_promises)

            # 3. 去重
            deduplicated_promises = self.deduplicator.deduplicate_promises(
                all_promises
            )

            # 4. 保存到数据库
            project_id = self.db_manager.create_project(
                name=project_name,
                twitter_username=twitter_username,
                website_url=website_url
            )

            for promise in deduplicated_promises:
                self.db_manager.create_promise(
                    project_id=project_id,
                    **promise
                )

            logger.info(
                "承诺收集完成",
                project_name=project_name,
                promises_count=len(deduplicated_promises)
            )

            return {
                "project_id": project_id,
                "project_name": project_name,
                "promises": deduplicated_promises,
                "total_count": len(deduplicated_promises)
            }

        except Exception as e:
            error_msg = f"收集承诺失败: {str(e)}"
            logger.error(
                error_msg,
                project_name=project_name,
                error=str(e)
            )
            raise RuntimeError(error_msg) from e

    def _collect_twitter_promises(
        self,
        username: str,
        max_tweets: int
    ) -> List[Dict]:
        """收集 Twitter 承诺"""
        logger.info("收集 Twitter 数据", username=username)

        # 构建任务提示
        task = f"""
请使用 twitter_scraper 工具抓取 @{username} 的最近 {max_tweets} 条推文。
然后使用 promise_extractor 工具从推文中提取项目承诺。
"""

        # 执行任务
        result = self.agent.run(task)

        # 解析结果（这里简化处理，实际需要根据 SpoonReactAI 的返回格式解析）
        # 在实际实现中，需要从 agent 的执行历史中提取工具调用结果

        # 临时实现：直接调用工具
        twitter_tool = self.tool_manager.get_tool("twitter_scraper")
        tweets = twitter_tool._run(username=username, max_tweets=max_tweets)

        # 格式化推文数据
        formatted_tweets = self.formatter.format_twitter_data(tweets)

        # 提取承诺
        all_promises = []
        promise_tool = self.tool_manager.get_tool("promise_extractor")

        for tweet_data in formatted_tweets:
            promises = promise_tool._run(
                text=tweet_data["raw_content"],
                source_type="twitter",
                source_url=tweet_data["source_url"]
            )

            # 合并数据
            merged = self.formatter.merge_promise_data(
                promises,
                tweet_data
            )
            all_promises.extend(merged)

        return all_promises

    def _collect_website_promises(self, url: str) -> List[Dict]:
        """收集网站承诺"""
        logger.info("收集网站数据", url=url)

        # 爬取网页
        web_tool = self.tool_manager.get_tool("web_scraper")
        web_content = web_tool._run(url=url, output_format="markdown")

        # 格式化网页数据
        formatted_web = self.formatter.format_website_data(web_content)

        # 提取承诺
        promise_tool = self.tool_manager.get_tool("promise_extractor")
        promises = promise_tool._run(
            text=formatted_web["raw_content"],
            source_type="website",
            source_url=url
        )

        # 合并数据
        merged = self.formatter.merge_promise_data(promises, formatted_web)

        return merged

    def verify_promises(
        self,
        project_id: str,
        network: str = "mainnet"
    ) -> Dict:
        """
        验证项目承诺

        Args:
            project_id: 项目 ID
            network: 网络名称

        Returns:
            验证结果字典
        """
        logger.info(
            "开始验证项目承诺",
            project_id=project_id,
            network=network
        )

        try:
            # 1. 从数据库获取项目和承诺数据
            project = self.db_manager.get_project(project_id)
            if not project:
                raise ValueError(f"项目不存在: {project_id}")

            promises = self.db_manager.get_promises_by_project(project_id)
            if not promises:
                logger.warning("项目没有承诺数据", project_id=project_id)
                return {
                    "project_id": project_id,
                    "verification_results": [],
                    "integrity_score": {
                        "score": 0,
                        "status": "no_promises",
                        "message": "没有可验证的承诺"
                    }
                }

            # 2. 执行承诺验证
            verification_results = self.promise_verifier.verify_promises_batch(
                promises,
                project,
                network
            )

            # 3. 计算诚信审计评分
            integrity_score = self.integrity_scorer.calculate_score(
                promises,
                verification_results
            )

            # 4. 计算验证摘要
            verification_summary = self.promise_verifier.calculate_verification_summary(
                verification_results
            )

            logger.info(
                "承诺验证完成",
                project_id=project_id,
                integrity_score=integrity_score.get("score"),
                fulfilled=verification_summary.get("fulfilled_count"),
                broken=verification_summary.get("broken_count")
            )

            return {
                "project_id": project_id,
                "project_name": project.get("name"),
                "verification_results": verification_results,
                "verification_summary": verification_summary,
                "integrity_score": integrity_score,
                "network": network
            }

        except Exception as e:
            error_msg = f"验证承诺失败: {str(e)}"
            logger.error(
                error_msg,
                project_id=project_id,
                error=str(e)
            )
            raise RuntimeError(error_msg) from e

    def calculate_integrity_score(
        self,
        promises: List[Dict],
        verification_results: List[Dict]
    ) -> Dict:
        """
        计算诚信审计评分

        Args:
            promises: 承诺列表
            verification_results: 验证结果列表

        Returns:
            诚信审计评分结果
        """
        return self.integrity_scorer.calculate_score(
            promises,
            verification_results
        )

    def calculate_five_dimensions_score(
        self,
        project_id: str,
        network: str = "mainnet"
    ) -> Dict:
        """
        计算五维审计评分和画饼指数

        Args:
            project_id: 项目 ID
            network: 网络名称

        Returns:
            五维评分和画饼指数结果
        """
        logger.info(
            "开始计算五维审计评分",
            project_id=project_id
        )

        try:
            # 1. 获取项目和承诺数据
            project = self.db_manager.get_project(project_id)
            if not project:
                raise ValueError(f"项目不存在: {project_id}")

            promises = self.db_manager.get_promises_by_project(project_id)

            # 2. 获取最新验证记录
            latest_verification = self.db_manager.get_latest_verification_record(
                project_id
            )

            if not latest_verification:
                logger.warning(
                    "项目没有验证记录，先执行验证",
                    project_id=project_id
                )
                # 执行验证
                verification_result = self.verify_promises(project_id, network)
                verification_results = verification_result.get("verification_results", [])
                integrity_score = verification_result.get("integrity_score", {})
            else:
                # 使用现有验证结果
                verification_results = []  # 从数据库加载
                integrity_score = {
                    "score": latest_verification.get("integrity_score", 0),
                    "dimension": "integrity"
                }

            # 3. 计算其他维度评分（简化实现，使用 Mock 数据）
            # 实际应该从链上和 GitHub 获取真实数据

            # 公平性审计（需要代币持有者数据）
            fairness_score = None
            if project.get("contract_address"):
                # Mock 数据
                fairness_score = self.fairness_scorer.calculate_score(
                    token_holders=[],  # 实际应该查询链上数据
                    total_supply=0
                )

            # 开发力审计（需要 GitHub 数据）
            activity_score = None
            if project.get("github_repo"):
                # Mock 数据
                activity_score = self.activity_scorer.calculate_score(
                    commits=[],  # 实际应该查询 GitHub API
                    pull_requests=[]
                )

            # 财务稳定性审计（需要交易数据）
            stability_score = None
            if project.get("treasury_address"):
                # Mock 数据
                stability_score = self.stability_scorer.calculate_score(
                    transactions=[],  # 实际应该查询链上交易
                    treasury_balance=0.0,
                    total_supply=0.0
                )

            # 社区动能审计（需要 Twitter 数据）
            momentum_score = None
            if project.get("twitter_account"):
                # Mock 数据
                momentum_score = self.momentum_scorer.calculate_score(
                    twitter_data={},  # 实际应该查询 Twitter API
                    sentiment_analysis={}
                )

            # 4. 计算画饼指数
            index_result = self.index_calculator.calculate_with_boundary_handling(
                integrity_score=integrity_score,
                fairness_score=fairness_score,
                activity_score=activity_score,
                stability_score=stability_score,
                momentum_score=momentum_score
            )

            logger.info(
                "五维审计评分完成",
                project_id=project_id,
                promise_breaking_index=index_result.get("promise_breaking_index")
            )

            return {
                "project_id": project_id,
                "project_name": project.get("name"),
                "promise_breaking_index": index_result.get("promise_breaking_index"),
                "comprehensive_score": index_result.get("comprehensive_score"),
                "status": index_result.get("status"),
                "message": index_result.get("message"),
                "five_dimensions": index_result.get("five_dimensions"),
                "available_dimensions": index_result.get("available_dimensions"),
                "missing_dimensions": index_result.get("missing_dimensions"),
                "network": network
            }

        except Exception as e:
            error_msg = f"计算五维评分失败: {str(e)}"
            logger.error(
                error_msg,
                project_id=project_id,
                error=str(e)
            )
            raise RuntimeError(error_msg) from e
