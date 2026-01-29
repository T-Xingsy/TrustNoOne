"""
On-Chain Verifier - Python 包装器

用于 SpoonOS Agent 集成的 Python 接口
通过子进程调用 TypeScript 实现
"""

import os
import json
import subprocess
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass


@dataclass
class TransferEvent:
    """转账事件"""
    from_address: str
    to_address: str
    token_id: int
    block_number: int
    transaction_hash: str
    timestamp: int
    event_type: str  # 'mint' | 'transfer' | 'burn'


@dataclass
class AirdropVerification:
    """空投验证结果"""
    total_amount: int
    unique_recipients: int
    transactions: List[TransferEvent]
    fulfillment_rate: float
    evidence_strength: str  # 'strong' | 'moderate' | 'weak' | 'none'
    summary: str


class OnChainVerifier:
    """链上数据验证器 - Python 接口"""

    def __init__(
        self,
        rpc_url: str,
        contract_address: str,
        contract_abi: List[Dict],
        chain_id: Optional[int] = None
    ):
        """
        初始化验证器

        Args:
            rpc_url: RPC 节点 URL
            contract_address: NFT 合约地址
            contract_abi: 合约 ABI
            chain_id: 链 ID（可选）
        """
        self.rpc_url = rpc_url
        self.contract_address = contract_address
        self.contract_abi = contract_abi
        self.chain_id = chain_id

        # 验证 Node.js 环境
        self._check_nodejs()

    def query_transfer_events(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        start_block: Optional[int] = None,
        end_block: Optional[int] = None,
        from_address: Optional[str] = None,
        to_address: Optional[str] = None,
        event_type: str = 'all'
    ) -> List[TransferEvent]:
        """
        查询 Transfer 事件

        Args:
            start_time: 开始时间
            end_time: 结束时间
            start_block: 开始区块
            end_block: 结束区块
            from_address: 发送方地址
            to_address: 接收方地址
            event_type: 事件类型 ('mint' | 'transfer' | 'burn' | 'all')

        Returns:
            转账事件列表
        """
        params = {
            'action': 'queryTransferEvents',
            'config': self._get_config(),
            'params': {
                'startTime': start_time.isoformat() if start_time else None,
                'endTime': end_time.isoformat() if end_time else None,
                'startBlock': start_block,
                'endBlock': end_block,
                'from': from_address,
                'to': to_address,
                'eventType': event_type,
            }
        }

        result = self._call_typescript(params)
        return [self._parse_transfer_event(e) for e in result]

    def verify_airdrop_promise(
        self,
        promise: Dict[str, Any],
        project_address: str,
        start_time: datetime,
        end_time: datetime,
        min_batch_size: int = 5
    ) -> AirdropVerification:
        """
        验证空投承诺

        Args:
            promise: 承诺对象
            project_address: 项目方地址
            start_time: 开始时间
            end_time: 结束时间
            min_batch_size: 最小批量大小

        Returns:
            空投验证结果
        """
        params = {
            'action': 'verifyAirdropPromise',
            'config': self._get_config(),
            'params': {
                'promise': promise,
                'projectAddress': project_address,
                'startTime': start_time.isoformat(),
                'endTime': end_time.isoformat(),
                'minBatchSize': min_batch_size,
            }
        }

        result = self._call_typescript(params)
        return self._parse_airdrop_verification(result)

    def format_for_llm(
        self,
        promise: Dict[str, Any],
        onchain_data: AirdropVerification,
        mode: str = 'full'
    ) -> str:
        """
        格式化为 LLM 上下文

        Args:
            promise: 承诺对象
            onchain_data: 链上数据
            mode: 格式模式 ('full' | 'compact' | 'scoring')

        Returns:
            格式化的上下文字符串
        """
        params = {
            'action': 'formatForLLM',
            'config': self._get_config(),
            'params': {
                'promise': promise,
                'onchainData': {
                    'totalAmount': onchain_data.total_amount,
                    'uniqueRecipients': onchain_data.unique_recipients,
                    'fulfillmentRate': onchain_data.fulfillment_rate,
                    'evidenceStrength': onchain_data.evidence_strength,
                    'summary': onchain_data.summary,
                },
                'mode': mode,
            }
        }

        return self._call_typescript(params)

    # ==================== 私有方法 ====================

    def _get_config(self) -> Dict[str, Any]:
        """获取配置"""
        return {
            'rpcUrl': self.rpc_url,
            'contractAddress': self.contract_address,
            'contractABI': self.contract_abi,
            'chainId': self.chain_id,
        }

    def _call_typescript(self, params: Dict[str, Any]) -> Any:
        """
        调用 TypeScript 实现

        Args:
            params: 参数

        Returns:
            执行结果
        """
        # 获取脚本路径
        script_dir = os.path.dirname(os.path.abspath(__file__))
        ts_script = os.path.join(script_dir, 'verifier_cli.ts')

        # 调用 ts-node
        try:
            result = subprocess.run(
                ['ts-node', ts_script],
                input=json.dumps(params),
                capture_output=True,
                text=True,
                check=True
            )

            return json.loads(result.stdout)

        except subprocess.CalledProcessError as e:
            raise Exception(f"TypeScript execution failed: {e.stderr}")

        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse TypeScript output: {e}")

    def _check_nodejs(self):
        """检查 Node.js 环境"""
        try:
            subprocess.run(
                ['node', '--version'],
                capture_output=True,
                check=True
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            raise Exception(
                "Node.js not found. Please install Node.js 18+ to use this tool."
            )

        try:
            subprocess.run(
                ['ts-node', '--version'],
                capture_output=True,
                check=True
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            raise Exception(
                "ts-node not found. Please install: npm install -g ts-node typescript"
            )

    def _parse_transfer_event(self, data: Dict[str, Any]) -> TransferEvent:
        """解析转账事件"""
        return TransferEvent(
            from_address=data['from'],
            to_address=data['to'],
            token_id=int(data['tokenId']),
            block_number=data['blockNumber'],
            transaction_hash=data['transactionHash'],
            timestamp=data['timestamp'],
            event_type=data['eventType']
        )

    def _parse_airdrop_verification(
        self,
        data: Dict[str, Any]
    ) -> AirdropVerification:
        """解析空投验证结果"""
        transactions = [
            self._parse_transfer_event(t)
            for t in data.get('transactions', [])
        ]

        return AirdropVerification(
            total_amount=data['totalAmount'],
            unique_recipients=data['uniqueRecipients'],
            transactions=transactions,
            fulfillment_rate=data['fulfillmentRate'],
            evidence_strength=data['evidenceStrength'],
            summary=data['summary']
        )


# ==================== SpoonOS 工具集成 ====================

from spoonos import BaseTool


class OnChainQueryTool(BaseTool):
    """链上查询工具 - SpoonOS 集成"""

    name: str = "onchain_query"
    description: str = "查询链上数据验证项目承诺"

    def __init__(self):
        super().__init__()
        self.verifier = OnChainVerifier(
            rpc_url=os.getenv('RPC_URL'),
            contract_address=os.getenv('NFT_CONTRACT_ADDRESS'),
            contract_abi=self._load_abi()
        )

    async def execute(
        self,
        promise: Dict[str, Any],
        project_address: str,
        start_date: str,
        end_date: str
    ) -> Dict[str, Any]:
        """
        执行链上查询

        Args:
            promise: 承诺对象
            project_address: 项目方地址
            start_date: 开始日期 (ISO 格式)
            end_date: 结束日期 (ISO 格式)

        Returns:
            验证结果
        """
        from datetime import datetime

        result = self.verifier.verify_airdrop_promise(
            promise=promise,
            project_address=project_address,
            start_time=datetime.fromisoformat(start_date),
            end_time=datetime.fromisoformat(end_date)
        )

        return {
            "found": result.total_amount > 0,
            "evidence": {
                "total_amount": result.total_amount,
                "unique_recipients": result.unique_recipients,
                "fulfillment_rate": result.fulfillment_rate,
                "evidence_strength": result.evidence_strength,
                "summary": result.summary
            },
            "fulfillment_rate": result.fulfillment_rate
        }

    def _load_abi(self) -> List[Dict]:
        """加载合约 ABI"""
        # 从 DDC Market SDK 加载 ABI
        abi_path = os.path.join(
            os.path.dirname(__file__),
            '../node_modules/@ddcmarket/sdk/dist/esm/abi/DDCNFT.json'
        )

        if os.path.exists(abi_path):
            with open(abi_path, 'r') as f:
                return json.load(f)

        # 如果找不到，使用最小 ABI
        return [
            {
                "anonymous": False,
                "inputs": [
                    {"indexed": True, "name": "from", "type": "address"},
                    {"indexed": True, "name": "to", "type": "address"},
                    {"indexed": True, "name": "tokenId", "type": "uint256"}
                ],
                "name": "Transfer",
                "type": "event"
            }
        ]


# ==================== 测试代码 ====================

if __name__ == "__main__":
    print("Testing On-Chain Verifier (Python Wrapper)...\n")

    # 测试配置
    verifier = OnChainVerifier(
        rpc_url=os.getenv('RPC_URL', 'https://eth-mainnet.g.alchemy.com/v2/demo'),
        contract_address='0x...',  # 替换为实际合约地址
        contract_abi=[]  # 使用最小 ABI
    )

    print("✓ Verifier initialized")
    print("\nTo test with real data:")
    print("1. Set RPC_URL environment variable")
    print("2. Set NFT_CONTRACT_ADDRESS environment variable")
    print("3. Run: python verifier.py")
