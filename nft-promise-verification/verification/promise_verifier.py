"""
承诺验证器

匹配承诺类型与链上数据，判断承诺兑现状态
"""
from typing import Dict, List, Any, Optional
from datetime import datetime
import structlog

from database.models import PromiseType, VerificationStatus
from tools.evm_tools import EVMTools

logger = structlog.get_logger(__name__)


class PromiseVerifier:
    """承诺验证器"""

    def __init__(self, evm_tools: EVMTools):
        """
        初始化验证器

        Args:
            evm_tools: EVM 链上查询工具
        """
        self.evm_tools = evm_tools

    def verify_promise(
        self,
        promise: Dict[str, Any],
        project: Dict[str, Any],
        network: str = "mainnet"
    ) -> Dict[str, Any]:
        """
        验证单个承诺

        Args:
            promise: 承诺数据
            project: 项目数据
            network: 网络名称

        Returns:
            验证结果字典
        """
        logger.info(
            "开始验证承诺",
            promise_id=promise.get("id"),
            promise_type=promise.get("promise_type")
        )

        promise_type = promise.get("promise_type")
        promise_id = promise.get("id")

        # 根据承诺类型选择验证方法
        verification_method = self._get_verification_method(promise_type)

        if not verification_method:
            return self._create_unverifiable_result(
                promise_id,
                "不支持的承诺类型"
            )

        try:
            # 执行验证
            result = verification_method(promise, project, network)

            logger.info(
                "承诺验证完成",
                promise_id=promise_id,
                status=result.get("status")
            )

            return result

        except Exception as e:
            logger.error(
                "承诺验证失败",
                promise_id=promise_id,
                error=str(e)
            )

            return self._create_unverifiable_result(
                promise_id,
                f"验证过程出错: {str(e)}"
            )

    def verify_promises_batch(
        self,
        promises: List[Dict[str, Any]],
        project: Dict[str, Any],
        network: str = "mainnet"
    ) -> List[Dict[str, Any]]:
        """
        批量验证承诺

        Args:
            promises: 承诺列表
            project: 项目数据
            network: 网络名称

        Returns:
            验证结果列表
        """
        logger.info(
            "开始批量验证承诺",
            promises_count=len(promises),
            project_id=project.get("id")
        )

        results = []
        for promise in promises:
            result = self.verify_promise(promise, project, network)
            results.append(result)

        logger.info(
            "批量验证完成",
            total=len(results),
            fulfilled=sum(1 for r in results if r["status"] == "fulfilled"),
            broken=sum(1 for r in results if r["status"] == "broken"),
            unverifiable=sum(1 for r in results if r["status"] == "unverifiable")
        )

        return results

    def _get_verification_method(self, promise_type: str):
        """
        获取承诺类型对应的验证方法

        Args:
            promise_type: 承诺类型

        Returns:
            验证方法函数或 None
        """
        verification_methods = {
            PromiseType.AIRDROP: self._verify_airdrop,
            PromiseType.NFT_MINTING: self._verify_nft_minting,
            PromiseType.MARKETPLACE_LAUNCH: self._verify_marketplace_launch,
            # 其他类型暂时无法通过链上数据验证
            PromiseType.FEATURE_DEVELOPMENT: None,
            PromiseType.PARTNERSHIP: None,
            PromiseType.COMMUNITY_EVENT: None,
            PromiseType.OTHER: None,
        }

        return verification_methods.get(promise_type)

    def _verify_airdrop(
        self,
        promise: Dict[str, Any],
        project: Dict[str, Any],
        network: str
    ) -> Dict[str, Any]:
        """
        验证空投承诺

        检查项目国库地址是否有代币转出记录
        """
        promise_id = promise.get("id")
        treasury_address = project.get("treasury_address")

        if not treasury_address:
            return self._create_unverifiable_result(
                promise_id,
                "缺少国库地址，无法验证空投"
            )

        try:
            # 查询国库地址的交易数量
            tx_count = self.evm_tools.get_transaction_count(
                treasury_address,
                network
            )

            # 简单判断：如果有交易记录，认为可能已执行空投
            # 注意：这是简化的验证逻辑，实际应该查询具体的转账记录
            if tx_count > 0:
                return {
                    "promise_id": promise_id,
                    "status": "fulfilled",
                    "message": f"国库地址有 {tx_count} 笔交易记录，可能已执行空投",
                    "evidence": {
                        "treasury_address": treasury_address,
                        "transaction_count": tx_count,
                        "network": network
                    },
                    "verified_at": datetime.utcnow().isoformat()
                }
            else:
                return {
                    "promise_id": promise_id,
                    "status": "broken",
                    "message": "国库地址无交易记录，空投未执行",
                    "evidence": {
                        "treasury_address": treasury_address,
                        "transaction_count": 0,
                        "network": network
                    },
                    "verified_at": datetime.utcnow().isoformat()
                }

        except Exception as e:
            return self._create_unverifiable_result(
                promise_id,
                f"查询国库地址失败: {str(e)}"
            )

    def _verify_nft_minting(
        self,
        promise: Dict[str, Any],
        project: Dict[str, Any],
        network: str
    ) -> Dict[str, Any]:
        """
        验证 NFT 铸造承诺

        检查合约地址是否存在且有活动
        """
        promise_id = promise.get("id")
        contract_address = project.get("contract_address")

        if not contract_address:
            return self._create_unverifiable_result(
                promise_id,
                "缺少合约地址，无法验证 NFT 铸造"
            )

        try:
            # 查询合约地址的交易数量
            tx_count = self.evm_tools.get_transaction_count(
                contract_address,
                network
            )

            # 如果合约有交易记录，认为 NFT 已铸造
            if tx_count > 0:
                return {
                    "promise_id": promise_id,
                    "status": "fulfilled",
                    "message": f"合约地址有 {tx_count} 笔交易记录，NFT 已铸造",
                    "evidence": {
                        "contract_address": contract_address,
                        "transaction_count": tx_count,
                        "network": network
                    },
                    "verified_at": datetime.utcnow().isoformat()
                }
            else:
                return {
                    "promise_id": promise_id,
                    "status": "broken",
                    "message": "合约地址无交易记录，NFT 未铸造",
                    "evidence": {
                        "contract_address": contract_address,
                        "transaction_count": 0,
                        "network": network
                    },
                    "verified_at": datetime.utcnow().isoformat()
                }

        except Exception as e:
            return self._create_unverifiable_result(
                promise_id,
                f"查询合约地址失败: {str(e)}"
            )

    def _verify_marketplace_launch(
        self,
        promise: Dict[str, Any],
        project: Dict[str, Any],
        network: str
    ) -> Dict[str, Any]:
        """
        验证市场启动承诺

        检查合约地址的活跃度
        """
        # 市场启动的验证逻辑与 NFT 铸造类似
        # 都是检查合约是否有活动
        return self._verify_nft_minting(promise, project, network)

    def _create_unverifiable_result(
        self,
        promise_id: str,
        reason: str
    ) -> Dict[str, Any]:
        """
        创建无法验证的结果

        Args:
            promise_id: 承诺 ID
            reason: 无法验证的原因

        Returns:
            验证结果字典
        """
        return {
            "promise_id": promise_id,
            "status": "unverifiable",
            "message": reason,
            "evidence": {},
            "verified_at": datetime.utcnow().isoformat()
        }

    def calculate_verification_summary(
        self,
        verification_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        计算验证结果摘要

        Args:
            verification_results: 验证结果列表

        Returns:
            摘要统计
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
