"""
财务稳定性审计评分模块

使用钱包分析工具识别可疑转账
评分范围: 0-100 分（100 分表示财务非常稳定）
"""
from typing import Dict, List, Any
from datetime import datetime, timedelta
import structlog

logger = structlog.get_logger(__name__)


class StabilityScorer:
    """财务稳定性审计评分器"""

    def __init__(self):
        """初始化评分器"""
        # 可疑转账阈值
        self.large_transfer_threshold = 0.1  # 单笔转账 > 10% 总供应量
        self.frequent_transfer_threshold = 10  # 每天 > 10 笔转账

    def calculate_score(
        self,
        transactions: List[Dict[str, Any]],
        treasury_balance: float,
        total_supply: float,
        time_window_days: int = 30
    ) -> Dict[str, Any]:
        """
        计算财务稳定性审计评分

        Args:
            transactions: 交易记录列表
            treasury_balance: 国库余额
            total_supply: 代币总供应量
            time_window_days: 时间窗口（天）

        Returns:
            包含评分和详情的字典
        """
        logger.info(
            "开始计算财务稳定性审计评分",
            transactions_count=len(transactions),
            treasury_balance=treasury_balance,
            total_supply=total_supply
        )

        if not transactions:
            return {
                "score": 50,  # 无数据时给中等分数
                "dimension": "stability",
                "status": "no_data",
                "message": "没有交易数据"
            }

        # 计算时间窗口内的交易
        cutoff_date = datetime.utcnow() - timedelta(days=time_window_days)

        recent_transactions = [
            tx for tx in transactions
            if self._parse_timestamp(tx.get("timestamp")) >= cutoff_date
        ]

        # 识别可疑转账
        large_transfers = self._identify_large_transfers(
            recent_transactions,
            total_supply
        )

        frequent_transfers = self._identify_frequent_transfers(
            recent_transactions,
            time_window_days
        )

        # 计算国库健康度
        treasury_health = self._calculate_treasury_health(
            treasury_balance,
            total_supply
        )

        # 计算评分
        # 大额转账惩罚（每个大额转账 -10 分）
        large_transfer_penalty = min(50, len(large_transfers) * 10)

        # 频繁转账惩罚（频繁转账天数 * 5 分）
        frequent_transfer_penalty = min(30, len(frequent_transfers) * 5)

        # 国库健康度评分（0-100）
        treasury_score = int(treasury_health * 100)

        # 最终评分
        score = max(0, treasury_score - large_transfer_penalty - frequent_transfer_penalty)

        # 判断状态
        if score >= 80:
            status = "excellent"
            message = "财务非常稳定"
        elif score >= 60:
            status = "good"
            message = "财务较为稳定"
        elif score >= 40:
            status = "fair"
            message = "财务稳定性一般"
        else:
            status = "poor"
            message = "财务稳定性较差，存在风险"

        logger.info(
            "财务稳定性审计评分完成",
            score=score,
            large_transfers=len(large_transfers),
            frequent_days=len(frequent_transfers),
            treasury_health=round(treasury_health, 2)
        )

        return {
            "score": score,
            "dimension": "stability",
            "status": status,
            "message": message,
            "details": {
                "recent_transactions": len(recent_transactions),
                "large_transfers_count": len(large_transfers),
                "frequent_transfer_days": len(frequent_transfers),
                "treasury_health": round(treasury_health, 2),
                "treasury_balance": treasury_balance,
                "time_window_days": time_window_days
            }
        }

    def _identify_large_transfers(
        self,
        transactions: List[Dict[str, Any]],
        total_supply: float
    ) -> List[Dict[str, Any]]:
        """识别大额转账"""
        if total_supply == 0:
            return []

        large_transfers = []
        for tx in transactions:
            amount = float(tx.get("value", 0))
            if amount / total_supply > self.large_transfer_threshold:
                large_transfers.append(tx)

        return large_transfers

    def _identify_frequent_transfers(
        self,
        transactions: List[Dict[str, Any]],
        time_window_days: int
    ) -> List[str]:
        """识别频繁转账的日期"""
        # 按日期分组统计
        daily_counts = {}
        for tx in transactions:
            timestamp = self._parse_timestamp(tx.get("timestamp"))
            date_key = timestamp.strftime("%Y-%m-%d")
            daily_counts[date_key] = daily_counts.get(date_key, 0) + 1

        # 找出频繁转账的日期
        frequent_days = [
            date for date, count in daily_counts.items()
            if count > self.frequent_transfer_threshold
        ]

        return frequent_days

    def _calculate_treasury_health(
        self,
        treasury_balance: float,
        total_supply: float
    ) -> float:
        """
        计算国库健康度

        Returns:
            健康度 (0-1)
        """
        if total_supply == 0:
            return 0.0

        # 国库余额占总供应量的比例
        treasury_ratio = treasury_balance / total_supply

        # 理想比例: 5-20%
        if 0.05 <= treasury_ratio <= 0.20:
            return 1.0
        elif treasury_ratio < 0.05:
            # 国库余额过低
            return treasury_ratio / 0.05
        else:
            # 国库余额过高（可能存在中心化风险）
            return max(0.5, 1.0 - (treasury_ratio - 0.20) / 0.30)

    def _parse_timestamp(self, timestamp: Any) -> datetime:
        """解析时间戳"""
        if not timestamp:
            return datetime.min

        try:
            if isinstance(timestamp, int):
                return datetime.fromtimestamp(timestamp)
            elif isinstance(timestamp, str):
                return datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            else:
                return datetime.min
        except Exception:
            return datetime.min
