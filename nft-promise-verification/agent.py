"""
VerificationAgent 基础实现

使用 SpoonReactAI 实现数据收集任务编排和链上验证
集成 Spoon-Awesome-Skill 脚本用于链上数据分析

支持两种模式:
1. AI 推理模式: Agent 自主决定调用哪些工具
2. 硬编码模式: 按固定流程执行 (fallback)
"""
from typing import Dict, List, Optional
from spoon_ai.agents import SpoonReactAI
from spoon_ai.tools import ToolManager
import structlog
import asyncio
from datetime import datetime, timedelta

from utils.data_formatter import DataFormatter
from utils.deduplicator import Deduplicator
from database.db import DatabaseManager
from database.models import PromiseType, VerificationStatus
from utils.rpc_manager import RPCManager
from tools.evm_tools import EVMTools
from verification.promise_verifier import PromiseVerifier
from scoring.integrity import IntegrityScorer
from scoring.fairness import FairnessScorer
from scoring.activity import ActivityScorer
from scoring.stability import StabilityScorer
from scoring.momentum import MomentumScorer
from scoring.index_calculator import IndexCalculator

# 外部脚本集成
from external.opensea_client import get_collection_data
from external.etherscan_client import (
    analyze_address,
    get_transactions,
    get_contract_events,
    verify_lock_event,
    get_nft_transfer_events
)
from external.transaction_analyzer import analyze_transaction

logger = structlog.get_logger(__name__)


# ==================== System Prompt 定义 ====================

AGENT_SYSTEM_PROMPT = """你是 NFT Promise Verification Agent，专门用于验证 NFT 项目的承诺是否兑现。

## 你的角色

你是一个区块链数据分析师，能够：
1. 从 Twitter、官网、白皮书中提取项目承诺
2. 通过链上数据验证承诺是否兑现
3. 计算五维审计评分（诚信、公平性、开发力、财务稳定性、社区动能）
4. 生成"画饼指数"报告

## 可用的工具

### 数据收集工具
- twitter_scraper: 抓取 Twitter 账号的推文
  - 参数: username (Twitter用户名, 不含@), max_tweets (最大抓取数)
  - 用途: 收集项目方在 Twitter 上发布的承诺

- web_scraper: 爬取网页内容
  - 参数: url (目标URL), output_format (输出格式: markdown/html/text)
  - 用途: 从官网、白皮书收集承诺

- promise_extractor: 使用 LLM 从文本中提取承诺
  - 参数: text (输入文本), source_type (来源类型), source_url (来源URL)
  - 用途: 从推文、网页中结构化提取承诺

### 链上验证工具 (模块4)
- verify_lock_event: 验证合约锁定事件
  - 参数: contract_address (合约地址), expected_amount (预期锁定金额)
  - 用途: 验证"锁定 XXX ETH"类承诺

- get_contract_events: 查询合约事件日志
  - 参数: contract_address (合约地址), topic0 (事件签名), from_block (起始区块)
  - 用途: 查询任意合约事件

- get_nft_transfer_events: 查询 NFT 转账事件
  - 参数: contract_address (NFT合约地址), from_block (起始区块)
  - 用途: 验证"空投发放"类承诺

- analyze_address: 综合地址分析
  - 参数: address (钱包/合约地址), chain (链名称)
  - 用途: 获取地址余额、交易历史、合约信息

- get_transactions: 获取地址交易记录
  - 参数: address (地址), chain (链名称), limit (返回数量)
  - 用途: 追踪资金流向

### GitHub 工具 (开发力审计)
- get_github_commits: 获取 GitHub 提交记录
  - 参数: owner (仓库所有者), repo (仓库名), start_date, end_date
  - 用途: 验证"开发活动"类承诺

- get_github_pull_requests: 获取 PR 记录
  - 参数: owner, repo, start_date, end_date
  - 用途: 分析代码贡献

### 市场数据工具 (社区动能)
- get_collection_data: 获取 OpenSea NFT 集合数据
  - 参数: collection_slug (OpenSea集合标识), chain (链名称)
  - 用途: 获取地板价、交易量等市场数据

## 承诺类型与验证工具映射

| 承诺关键词 | 承诺类型 | 验证工具 |
|-----------|---------|---------|
| 锁定、lock、timelock | 资金锁定 | verify_lock_event |
| 空投、airdrop | 空投发放 | get_nft_transfer_events |
| 国库、treasury、余额 | 国库资金 | analyze_address |
| 开发、commit、功能 | 开发活动 | get_github_commits |
| OpenSea、上线 | 市场上线 | get_collection_data |
| 合作、partner | 合作关系 | web_scraper (验证官网) |

## 工作流程

当收到验证任务时，你应该：

1. **理解任务**: 分析项目信息和待验证的承诺
2. **数据收集**: 根据承诺类型选择合适的工具收集数据
3. **链上验证**: 调用链上工具验证承诺是否兑现
4. **评分计算**: 根据验证结果计算各维度得分
5. **结果输出**: 返回结构化的验证报告

## 输出格式

请以 JSON 格式输出结果，包含:
- promises: 提取的承诺列表
- verification_results: 每条承诺的验证结果
- scores: 各维度评分
- summary: 简要总结

## 注意事项

- 调用工具前先检查参数是否完整
- 如果缺少必要参数（如合约地址），在输出中说明需要用户提供
- 验证时要考虑时间范围（如"本月"需要计算时间戳）
- 对无法验证的承诺标记为 "UNVERIFIABLE"
"""


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

        # ========== System Prompt: 定义 Agent 角色和能力 ==========
        self.system_prompt = self._build_system_prompt()

        # 初始化 SpoonReactAI (带 System Prompt)
        self.agent = SpoonReactAI(
            llm_manager=llm_manager,
            tool_manager=tool_manager,
            max_iterations=15
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

        logger.info("VerificationAgent 初始化完成", mode="ai_enabled")

    def _build_system_prompt(self) -> str:
        """构建 System Prompt"""
        return AGENT_SYSTEM_PROMPT

    def _parse_datetime(self, value: Optional[str]) -> Optional[datetime]:
        """解析日期时间字符串，失败则返回 None"""
        if not value:
            return None
        if isinstance(value, datetime):
            return value
        try:
            return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        except Exception:
            return None

    def _normalize_promise_type(self, raw_type: Optional[str]) -> str:
        """标准化承诺类型到数据库枚举值"""
        if not raw_type:
            return PromiseType.OTHER.value
        raw = str(raw_type).lower()
        valid_types = {t.value for t in PromiseType}
        if raw in valid_types:
            return raw
        mapping = {
            "product_launch": PromiseType.MARKETPLACE_LAUNCH.value,
            "feature": PromiseType.FEATURE_DEVELOPMENT.value,
            "financial": PromiseType.OTHER.value,
            "community": PromiseType.COMMUNITY_EVENT.value,
            "partnership": PromiseType.PARTNERSHIP.value,
            "roadmap": PromiseType.FEATURE_DEVELOPMENT.value,
            "other": PromiseType.OTHER.value
        }
        return mapping.get(raw, PromiseType.OTHER.value)

    def _normalize_verification_status(self, raw_status: Optional[str]) -> str:
        """标准化验证状态到数据库枚举值"""
        if not raw_status:
            return VerificationStatus.PENDING.value
        raw = str(raw_status).lower()
        valid_status = {s.value for s in VerificationStatus}
        if raw in valid_status:
            return raw
        mapping = {
            "broken": VerificationStatus.UNFULFILLED.value,
            "unfulfilled": VerificationStatus.UNFULFILLED.value,
            "fulfilled": VerificationStatus.FULFILLED.value,
            "unverifiable": VerificationStatus.UNVERIFIABLE.value
        }
        return mapping.get(raw, VerificationStatus.PENDING.value)

    def _build_sources_for_db(self, promise: Dict) -> List[Dict]:
        """构建数据库需要的 sources 列表"""
        sources: List[Dict] = []
        source_items = promise.get("sources")

        if isinstance(source_items, list) and source_items:
            for src in source_items:
                src_type = (
                    src.get("type")
                    or src.get("source_type")
                    or promise.get("source_type")
                    or "website"
                )
                src_url = (
                    src.get("url")
                    or src.get("source_url")
                    or promise.get("source_url")
                )
                if not src_url or not str(src_url).startswith(("http://", "https://")):
                    continue
                published_at = self._parse_datetime(
                    src.get("published_at")
                    or src.get("created_at")
                    or promise.get("created_at")
                ) or datetime.utcnow()
                metadata = src.get("metadata") or promise.get("metadata") or {}
                sources.append({
                    "type": src_type,
                    "url": src_url,
                    "published_at": published_at.isoformat(),
                    "metadata": metadata
                })
        else:
            src_url = promise.get("source_url")
            if src_url and str(src_url).startswith(("http://", "https://")):
                published_at = self._parse_datetime(
                    promise.get("created_at")
                ) or datetime.utcnow()
                sources.append({
                    "type": promise.get("source_type") or "website",
                    "url": src_url,
                    "published_at": published_at.isoformat(),
                    "metadata": promise.get("metadata") or {}
                })

        return sources

    def _convert_promise_for_db(self, promise: Dict, project_id: str) -> Dict:
        """将承诺字典转换为数据库模型可接受的格式"""
        content = (promise.get("content") or "").strip()
        if not content:
            raise ValueError("承诺内容为空")

        sources = self._build_sources_for_db(promise)
        if not sources:
            raise ValueError("承诺缺少有效来源链接")

        target_date = self._parse_datetime(
            promise.get("target_date") or promise.get("deadline")
        )
        target_date_value = target_date.isoformat() if target_date else None

        raw_weight = promise.get("importance_weight", 1.0)
        try:
            weight = float(raw_weight)
        except (TypeError, ValueError):
            weight = 1.0

        return {
            "project_id": project_id,
            "content": content,
            "sources": sources,
            "promise_type": self._normalize_promise_type(
                promise.get("promise_type") or promise.get("category")
            ),
            "target_date": target_date_value,
            "verification_status": self._normalize_verification_status(
                promise.get("verification_status")
            ),
            "importance_weight": weight
        }

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
                twitter_account=twitter_username,
                website_url=website_url
            )

            saved_promises = []
            skipped_count = 0
            for promise in deduplicated_promises:
                try:
                    db_promise = self._convert_promise_for_db(
                        promise,
                        project_id
                    )
                    self.db_manager.create_promise(**db_promise)
                    saved_promises.append(db_promise)
                except Exception as e:
                    skipped_count += 1
                    logger.warning(
                        "承诺保存失败，已跳过",
                        error=str(e),
                        content=promise.get("content", "")[:60]
                    )

            logger.info(
                "承诺收集完成",
                project_name=project_name,
                promises_count=len(saved_promises),
                skipped_count=skipped_count
            )

            return {
                "project_id": project_id,
                "project_name": project_name,
                "promises": saved_promises,
                "total_count": len(saved_promises),
                "skipped_count": skipped_count
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

    # ==================== AI 推理模式方法 ====================

    def collect_promises_ai(
        self,
        project_name: str,
        twitter_username: Optional[str] = None,
        website_url: Optional[str] = None,
        max_tweets: int = 100
    ) -> Dict:
        """
        AI 驱动的承诺收集 - Agent 自主决定数据收集策略

        与硬编码版本不同，这里让 Agent 自主推理：
        - 是否需要抓取 Twitter？
        - 是否需要爬取官网？
        - 需要抓取多少条数据？

        Args:
            project_name: 项目名称
            twitter_username: Twitter 用户名
            website_url: 官网 URL
            max_tweets: 最大推文数

        Returns:
            包含项目信息和承诺列表的字典
        """
        logger.info(
            "开始 AI 驱动承诺收集",
            project_name=project_name,
            mode="ai_reasoning"
        )

        # 构建任务描述
        task_info = []
        task_info.append(f"项目名称: {project_name}")

        if twitter_username:
            task_info.append(f"Twitter 账号: @{twitter_username}")
        if website_url:
            task_info.append(f"官网: {website_url}")

        task_prompt = f"""# 任务: 收集 NFT 项目承诺

## 项目信息
{chr(10).join(task_info)}

## 你的任务
1. 收集该项目的公开承诺（从 Twitter、官网等来源）
2. 使用 promise_extractor 工具从收集的内容中提取结构化承诺
3. 对承诺进行去重和分类

## 输出要求
请以 JSON 格式输出，包含:
{{
  "promises": [
    {{
      "content": "承诺内容",
      "promise_type": "承诺类型 (airdrop/feature_development/partnership等)",
      "source_type": "来源类型 (twitter/website)",
      "source_url": "来源链接",
      "target_date": "目标时间 (如有)"
    }}
  ],
  "total_count": 承诺总数,
  "sources_used": ["使用的数据源列表"]
}}

## 注意
- Twitter 用户名传入时不要包含 @ 符号
- 如果 Twitter 和官网都有，优先从官网获取更详细的信息
- max_tweets 设为 {max_tweets}
"""

        try:
            # 使用 Agent 运行任务
            result = self.agent.run(task_prompt)

            # 解析 Agent 返回结果
            # 注意: 实际需要根据 SpoonReactAI 的返回格式处理
            logger.info("AI 承诺收集完成", result=str(result)[:200])

            # 创建项目记录
            project_id = self.db_manager.create_project(
                name=project_name,
                twitter_account=twitter_username,
                website_url=website_url
            )

            # TODO: 解析 result 并保存承诺到数据库

            return {
                "project_id": project_id,
                "project_name": project_name,
                "mode": "ai_reasoning",
                "raw_result": str(result)
            }

        except Exception as e:
            logger.error("AI 承诺收集失败，回退到硬编码模式", error=str(e))
            # 回退到硬编码模式
            return self.collect_promises(project_name, twitter_username, website_url, max_tweets)

    def verify_promises_ai(
        self,
        project_id: str,
        network: str = "mainnet"
    ) -> Dict:
        """
        AI 驱动的承诺验证 - Agent 自主决定验证策略

        Agent 会：
        1. 分析每条承诺的类型
        2. 自主选择合适的验证工具
        3. 综合验证结果

        Args:
            project_id: 项目 ID
            network: 网络名称

        Returns:
            验证结果字典
        """
        logger.info(
            "开始 AI 驱动承诺验证",
            project_id=project_id,
            mode="ai_reasoning"
        )

        # 获取项目和承诺数据
        project = self.db_manager.get_project(project_id)
        if not project:
            raise ValueError(f"项目不存在: {project_id}")

        promises = self.db_manager.get_promises_by_project(project_id)
        if not promises:
            return {
                "project_id": project_id,
                "error": "没有可验证的承诺"
            }

        # 格式化承诺列表
        promises_text = "\n".join([
            f"- {p.get('content', 'N/A')} (类型: {p.get('promise_type', 'unknown')})"
            for p in promises[:10]  # 限制数量避免 prompt 过长
        ])

        # 构建项目信息
        project_info = []
        if project.get("contract_address"):
            project_info.append(f"NFT 合约: {project['contract_address']}")
        if project.get("treasury_address"):
            project_info.append(f"国库地址: {project['treasury_address']}")
        if project.get("github_repo"):
            project_info.append(f"GitHub: {project['github_repo']}")
        if project.get("opensea_slug"):
            project_info.append(f"OpenSea: {project['opensea_slug']}")

        task_prompt = f"""# 任务: 验证 NFT 项目承诺

## 项目信息
- 项目名称: {project.get('name')}
{chr(10).join('- ' + info for info in project_info)}

## 待验证承诺
{promises_text}

## 你的任务
对上述承诺进行验证，自主选择合适的工具：

1. **资金锁定类**: 使用 verify_lock_event 验证合约锁定
2. **空投类**: 使用 get_nft_transfer_events 查询转账事件
3. **国库余额**: 使用 analyze_address 查询余额
4. **开发活动**: 使用 get_github_commits 查询提交
5. **市场上线**: 使用 get_collection_data 查询 OpenSea 数据

## 输出要求
请以 JSON 格式输出:
{{
  "verification_results": [
    {{
      "promise_content": "承诺内容",
      "verification_method": "使用的验证方法",
      "verification_status": "FULFILLED/UNFULFILLED/UNVERIFIABLE",
      "evidence": "验证证据",
      "verified_at": "验证时间"
    }}
  ],
  "summary": {{
    "total": 总承诺数,
    "fulfilled": 已兑现数,
    "unfulfilled": 未兑现数,
    "unverifiable": 无法验证数
  }}
}}

## 注意
- 调用链上工具时 chain 参数设为 "ethereum"
- 如果缺少必要参数（如合约地址），标记为 UNVERIFIABLE
- 验证时要考虑承诺的时间范围
"""

        try:
            # 使用 Agent 运行验证任务
            result = self.agent.run(task_prompt)

            logger.info(
                "AI 承诺验证完成",
                project_id=project_id,
                result_preview=str(result)[:200]
            )

            return {
                "project_id": project_id,
                "project_name": project.get("name"),
                "mode": "ai_reasoning",
                "raw_result": str(result)
            }

        except Exception as e:
            logger.error("AI 承诺验证失败，回退到硬编码模式", error=str(e))
            # 回退到硬编码模式
            return self.verify_promises(project_id, network)

    def full_verification_ai(
        self,
        project_name: str,
        twitter_username: Optional[str] = None,
        website_url: Optional[str] = None,
        contract_address: Optional[str] = None,
        treasury_address: Optional[str] = None,
        github_repo: Optional[str] = None,
        opensea_slug: Optional[str] = None
    ) -> Dict:
        """
        完整的 AI 驱动验证流程

        Agent 自主完成从数据收集到评分的整个流程

        Args:
            project_name: 项目名称
            twitter_username: Twitter 用户名
            website_url: 官网 URL
            contract_address: NFT 合约地址
            treasury_address: 国库地址
            github_repo: GitHub 仓库
            opensea_slug: OpenSea 集合标识

        Returns:
            完整验证报告
        """
        logger.info(
            "开始完整 AI 验证流程",
            project_name=project_name,
            mode="full_ai_reasoning"
        )

        # 构建完整任务描述
        task_prompt = f"""# 任务: NFT 项目完整验证

## 项目信息
- 项目名称: {project_name}
- Twitter: @{twitter_username if twitter_username else 'N/A'}
- 官网: {website_url if website_url else 'N/A'}
- NFT 合约: {contract_address if contract_address else 'N/A'}
- 国库地址: {treasury_address if treasury_address else 'N/A'}
- GitHub: {github_repo if github_repo else 'N/A'}
- OpenSea: {opensea_slug if opensea_slug else 'N/A'}

## 你的任务
请完成以下完整验证流程：

### 第1步: 收集承诺
从 Twitter、官网收集项目承诺

### 第2步: 验证承诺
根据承诺类型选择合适的工具验证：
- 资金锁定 → verify_lock_event
- 空投 → get_nft_transfer_events
- 国库余额 → analyze_address
- 开发活动 → get_github_commits
- 市场数据 → get_collection_data

### 第3步: 计算评分
根据验证结果计算：
- 诚信得分: 兑现承诺比例
- 公平性: NFT 持有者分布
- 开发力: GitHub 提交/PR 数量
- 财务稳定: 国库资金流向
- 社区动能: Twitter + OpenSea 数据

### 第4步: 计算画饼指数
综合五维得分计算画饼指数 (0-100)

## 输出要求
请以 JSON 格式输出完整报告:
{{
  "project_name": "项目名称",
  "promises_found": 承诺总数,
  "verification_results": [...],
  "five_dimensions": {{
    "integrity": {{"score": 得分, "details": "详情"}},
    "fairness": {{"score": 得分, "details": "详情"}},
    "activity": {{"score": 得分, "details": "详情"}},
    "stability": {{"score": 得分, "details": "详情"}},
    "momentum": {{"score": 得分, "details": "详情"}}
  }},
  "promise_breaking_index": 画饼指数(0-100),
  "status": "excellent/good/fair/poor",
  "summary": "总结"
}}
"""

        try:
            # 使用 Agent 完成完整验证
            result = self.agent.run(task_prompt)

            # 创建项目记录
            project_id = self.db_manager.create_project(
                name=project_name,
                twitter_account=twitter_username,
                website_url=website_url,
                contract_address=contract_address,
                treasury_address=treasury_address,
                github_repo=github_repo,
                opensea_slug=opensea_slug
            )

            logger.info(
                "完整 AI 验证完成",
                project_id=project_id,
                result_preview=str(result)[:500]
            )

            return {
                "project_id": project_id,
                "project_name": project_name,
                "mode": "full_ai_reasoning",
                "raw_result": str(result)
            }

        except Exception as e:
            logger.error("完整 AI 验证失败", error=str(e))
            raise RuntimeError(f"完整 AI 验证失败: {str(e)}") from e

    # ========== 辅助方法：从 Spoon-Toolkit 工具获取数据 ==========

    def _run_async(self, coro):
        """在同步上下文中运行异步函数"""
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        return loop.run_until_complete(coro)

    def _fetch_nft_holders_from_chainbase(
        self,
        contract_address: str,
        chain_id: int = 1,
        limit: int = 100
    ) -> List[Dict]:
        """
        从 Chainbase 获取 NFT 持有者数据（用于公平性审计）

        Args:
            contract_address: NFT 合约地址
            chain_id: 链 ID (1=Ethereum)
            limit: 返回数量

        Returns:
            NFT 持有者列表 [{"address": "...", "balance": ...}, ...]
        """
        try:
            tool = self.tool_manager.get_tool("get_account_nfts")
            logger.info(
                "获取 NFT 持有者数据",
                contract_address=contract_address,
                chain_id=chain_id
            )
            # 注意：这里需要获取该 NFT 合约的所有持有者
            # Chainbase API 限制，简化实现返回空列表
            # TODO: 需要调用 Chainbase token API 获取 NFT 持有者分布
            return []
        except Exception as e:
            logger.error("获取 NFT 持有者失败", error=str(e))
            return []

    def _fetch_github_activity(
        self,
        github_repo: str,
        days: int = 30
    ) -> Dict[str, List]:
        """
        从 GitHub 获取开发活动数据

        Args:
            github_repo: 仓库路径 "owner/repo"
            days: 查询最近 N 天

        Returns:
            {"commits": [...], "pull_requests": [...], "issues": [...]}
        """
        try:
            owner, repo = github_repo.split("/")
            end_date = datetime.now().strftime("%Y-%m-%d")
            start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

            result = {"commits": [], "pull_requests": [], "issues": []}

            # 获取 commits
            commits_tool = self.tool_manager.get_tool("get_github_commits")
            commits_data = self._run_async(
                commits_tool.execute(
                    owner=owner,
                    repo=repo,
                    start_date=start_date,
                    end_date=end_date
                )
            )
            if hasattr(commits_data, 'output'):
                result["commits"] = commits_data.output.get("commits_list", [])

            # 获取 PRs
            prs_tool = self.tool_manager.get_tool("get_github_pull_requests")
            prs_data = self._run_async(
                prs_tool.execute(
                    owner=owner,
                    repo=repo,
                    start_date=start_date,
                    end_date=end_date
                )
            )
            if hasattr(prs_data, 'output'):
                result["pull_requests"] = prs_data.output.get("pull_requests_list", [])

            logger.info(
                "GitHub 数据获取成功",
                repo=github_repo,
                commits=len(result["commits"]),
                prs=len(result["pull_requests"])
            )

            return result
        except Exception as e:
            logger.error("获取 GitHub 数据失败", error=str(e))
            return {"commits": [], "pull_requests": [], "issues": []}

    def _fetch_chainbase_transactions(
        self,
        address: str,
        chain_id: int = 1,
        days: int = 30,
        limit: int = 100
    ) -> List[Dict]:
        """
        从 Etherscan 获取地址交易记录

        Args:
            address: 钱包地址
            chain_id: 链 ID (1=Ethereum)
            days: 查询最近 N 天
            limit: 返回数量

        Returns:
            交易记录列表
        """
        try:
            chain = "ethereum" if chain_id == 1 else "polygon" if chain_id == 137 else "ethereum"
            txs = get_transactions(address=address, chain=chain, limit=limit)

            # 转换为项目需要的格式
            formatted_txs = []
            for tx in txs:
                formatted_txs.append({
                    "hash": tx["hash"],
                    "timestamp": tx["timestamp"],
                    "from": tx["from"],
                    "to": tx["to"],
                    "value": tx["value"],
                    "gas_used": tx["gas_used"]
                })

            logger.info(
                "Etherscan 交易记录获取成功",
                address=address,
                count=len(formatted_txs)
            )

            return formatted_txs
        except Exception as e:
            logger.error("获取交易记录失败", error=str(e))
            return []

    def _fetch_chainbase_balance(
        self,
        address: str,
        chain_id: int = 1
    ) -> float:
        """
        从 Etherscan 获取地址余额

        Args:
            address: 钱包地址
            chain_id: 链 ID (1=Ethereum)

        Returns:
            余额（ETH 单位）
        """
        try:
            chain = "ethereum" if chain_id == 1 else "polygon" if chain_id == 137 else "ethereum"
            result = analyze_address(address=address, chain=chain)

            balance = result.get("balance", {}).get("native", 0.0)

            logger.info(
                "Etherscan 余额获取成功",
                address=address,
                balance=balance
            )

            return balance
        except Exception as e:
            logger.error("获取余额失败", error=str(e))
            return 0.0

    def _fetch_opensea_collection_data(
        self,
        collection_slug: str,
        chain: str = "ethereum"
    ) -> Optional[Dict]:
        """
        从 OpenSea 获取 NFT 集合数据

        Args:
            collection_slug: OpenSea 集合标识 (如 "boredapeyachtclub")
            chain: 链名称

        Returns:
            集合数据字典
        """
        try:
            data = get_collection_data(collection_slug=collection_slug, chain=chain)

            logger.info(
                "OpenSea 数据获取成功",
                collection=collection_slug,
                floor_price=data.get("stats", {}).get("floor_price")
            )

            return data
        except Exception as e:
            logger.error("获取 OpenSea 数据失败", error=str(e))
            return None

    # ========== 模块4: 链上验证 - 合约事件查询 ==========

    def verify_contract_lock_event(
        self,
        contract_address: str,
        expected_amount: float = None,
        user_address: str = None,
        from_block: int = 0,
        chain: str = "ethereum"
    ) -> Dict:
        """
        验证合约锁定事件 - 模块4核心功能

        用于验证如"锁定 1000 ETH 到 timelock 合约"的承诺

        Args:
            contract_address: 锁定合约地址
            expected_amount: 预期锁定金额
            user_address: 锁定者地址
            from_block: 起始区块号
            chain: 链名称

        Returns:
            验证结果字典
        """
        logger.info(
            "验证合约锁定事件",
            contract=contract_address,
            expected_amount=expected_amount
        )

        return verify_lock_event(
            contract_address=contract_address,
            lock_amount=expected_amount,
            user_address=user_address,
            from_block=from_block,
            chain=chain
        )

    def query_contract_events(
        self,
        contract_address: str,
        topic0: str = None,
        topic1: str = None,
        from_block: int = 0,
        to_block: int = 99999999,
        chain: str = "ethereum"
    ) -> List[Dict]:
        """
        查询合约事件日志 - 通用事件查询

        Args:
            contract_address: 合约地址
            topic0: 事件签名（Keccak256哈希）
            topic1: 索引参数1
            from_block: 起始区块
            to_block: 结束区块
            chain: 链名称

        Returns:
            事件日志列表
        """
        logger.info(
            "查询合约事件",
            contract=contract_address,
            topic0=topic0,
            from_block=from_block
        )

        return get_contract_events(
            contract_address=contract_address,
            from_block=from_block,
            to_block=to_block,
            topic0=topic0,
            topic1=topic1,
            chain=chain
        )

    def verify_nft_transfer_activity(
        self,
        contract_address: str = None,
        from_block: int = 0,
        days: int = 30,
        chain: str = "ethereum"
    ) -> Dict:
        """
        验证 NFT 转账活动 - 用于验证"空投发放"等承诺

        Args:
            contract_address: NFT 合约地址
            from_block: 起始区块
            days: 查询最近 N 天
            chain: 链名称

        Returns:
            NFT 活动统计
        """
        # 估算区块数（以太坊约每天 7200 个区块）
        blocks_per_day = 7200
        to_block = from_block + (days * blocks_per_day)

        logger.info(
            "验证 NFT 转账活动",
            contract=contract_address,
            days=days
        )

        events = get_nft_transfer_events(
            contract_address=contract_address,
            from_block=from_block,
            to_block=to_block,
            chain=chain
        )

        # 统计活动
        unique_receivers = set()
        total_transfers = len(events)

        for event in events:
            if event.get("to") and event["to"] != "0x0000000000000000000000000000000000000000":
                unique_receivers.add(event["to"])

        return {
            "total_transfers": total_transfers,
            "unique_receivers": len(unique_receivers),
            "recent_events": events[:10]
        }

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

            # 3. 计算其他维度评分（使用 Spoon-Toolkit 工具获取真实数据）

            # ========== 公平性审计（NFT 持有者分布） ==========
            fairness_score = None
            if project.get("contract_address"):
                # 注意：NFT 项目用 NFT 持有者分布计算公平性
                # 如果项目有 ERC20 代币，可以添加 token_address 字段使用代币持有者
                nft_holders = self._fetch_nft_holders_from_chainbase(
                    contract_address=project["contract_address"],
                    chain_id=1
                )
                if nft_holders:
                    total_supply = len(nft_holders)  # 简化：用持有者数量
                    # 转换为公平性评分需要的格式
                    token_holders = [{"address": h["address"], "balance": 1} for h in nft_holders]
                    fairness_score = self.fairness_scorer.calculate_score(
                        token_holders=token_holders,
                        total_supply=total_supply
                    )
                    logger.info(
                        "公平性审计完成",
                        score=fairness_score.get("score"),
                        holders_count=len(nft_holders)
                    )

            # ========== 开发力审计（GitHub 数据） ==========
            activity_score = None
            if project.get("github_repo"):
                github_data = self._fetch_github_activity(
                    github_repo=project["github_repo"],
                    days=90  # 查询最近 90 天
                )
                if github_data["commits"] or github_data["pull_requests"]:
                    activity_score = self.activity_scorer.calculate_score(
                        commits=github_data["commits"],
                        pull_requests=github_data["pull_requests"]
                    )
                    logger.info(
                        "开发力审计完成",
                        score=activity_score.get("score"),
                        commits=len(github_data["commits"]),
                        prs=len(github_data["pull_requests"])
                    )

            # ========== 财务稳定性审计（国库资金流向） ==========
            stability_score = None
            if project.get("treasury_address"):
                # 获取交易记录
                transactions = self._fetch_chainbase_transactions(
                    address=project["treasury_address"],
                    chain_id=1,
                    days=30
                )
                # 获取国库余额
                treasury_balance = self._fetch_chainbase_balance(
                    address=project["treasury_address"],
                    chain_id=1
                )
                # NFT 项目使用国库余额作为参考，不需要代币总供应量
                total_supply = treasury_balance * 10  # 简化假设：国库占 10%

                if transactions:
                    stability_score = self.stability_scorer.calculate_score(
                        transactions=transactions,
                        treasury_balance=treasury_balance,
                        total_supply=total_supply,
                        time_window_days=30
                    )
                    logger.info(
                        "财务稳定性审计完成",
                        score=stability_score.get("score"),
                        transactions_count=len(transactions),
                        treasury_balance=treasury_balance
                    )

            # ========== 社区动能审计（Twitter + OpenSea 数据） ==========
            momentum_score = None
            twitter_data = {}
            opensea_data = {}

            # 1. 获取 Twitter 数据
            if project.get("twitter_account"):
                try:
                    twitter_tool = self.tool_manager.get_tool("twitter_scraper")
                    username = project["twitter_account"].lstrip("@")
                    tweets = twitter_tool._run(username=username, max_tweets=100)
                    if tweets:
                        total_likes = sum(t.get("likes", 0) for t in tweets)
                        total_retweets = sum(t.get("retweets", 0) for t in tweets)
                        twitter_data = {
                            "tweets_count": len(tweets),
                            "total_likes": total_likes,
                            "total_retweets": total_retweets,
                            "avg_engagement": (total_likes + total_retweets) / len(tweets) if tweets else 0
                        }
                except Exception as e:
                    logger.warning("Twitter 数据获取失败", error=str(e))

            # 2. 获取 OpenSea 数据（如果有 opensea_slug）
            if project.get("opensea_slug"):
                opensea_data = self._fetch_opensea_collection_data(
                    collection_slug=project["opensea_slug"],
                    chain="ethereum"
                )

            # 3. 计算动能评分
            if twitter_data or opensea_data:
                # 合并数据
                combined_data = {"twitter": twitter_data, "opensea": opensea_data}

                # 如果有 OpenSea 数据，使用更精确的指标
                if opensea_data:
                    stats = opensea_data.get("stats", {})
                    day_stats = opensea_data.get("day_stats", {})
                    combined_data["market_activity"] = {
                        "floor_price": stats.get("floor_price", {}).get("value", 0),
                        "total_volume": stats.get("total_volume", 0),
                        "day_volume": day_stats.get("volume", 0),
                        "day_sales": day_stats.get("sales", 0),
                        "num_owners": stats.get("num_owners", 0),
                        "liquidity_score": opensea_data.get("liquidity_score", "UNKNOWN")
                    }

                momentum_score = self.momentum_scorer.calculate_score(
                    twitter_data=combined_data.get("twitter", {}),
                    market_data=combined_data.get("market_activity"),
                    sentiment_analysis={"positive_ratio": 0.7}
                )
                logger.info(
                    "社区动能审计完成",
                    score=momentum_score.get("score"),
                    has_twitter=bool(twitter_data),
                    has_opensea=bool(opensea_data)
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
