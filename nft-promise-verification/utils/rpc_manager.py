"""
RPC 节点管理模块

支持多 RPC 提供商和故障转移
"""
from typing import Dict, List, Optional
from web3 import Web3
from web3.exceptions import Web3Exception
import structlog

logger = structlog.get_logger(__name__)


class RPCManager:
    """RPC 节点管理器"""

    # 默认 RPC 端点配置
    DEFAULT_RPCS = {
        "mainnet": [
            "https://eth-mainnet.g.alchemy.com/v2/demo",
            "https://mainnet.infura.io/v3/9aa3d95b3bc440fa88ea12eaa4456161",
            "https://cloudflare-eth.com",
        ],
        "sepolia": [
            "https://eth-sepolia.g.alchemy.com/v2/demo",
            "https://sepolia.infura.io/v3/9aa3d95b3bc440fa88ea12eaa4456161",
        ]
    }

    def __init__(self, custom_rpcs: Optional[Dict[str, List[str]]] = None):
        """
        初始化 RPC 管理器

        Args:
            custom_rpcs: 自定义 RPC 端点配置
        """
        self.rpcs = custom_rpcs or self.DEFAULT_RPCS
        self._web3_instances: Dict[str, Web3] = {}
        self._current_rpc_index: Dict[str, int] = {}

        logger.info(
            "RPC 管理器初始化",
            networks=list(self.rpcs.keys())
        )

    def get_web3(self, network: str = "mainnet") -> Web3:
        """
        获取 Web3 实例

        Args:
            network: 网络名称

        Returns:
            Web3 实例

        Raises:
            ValueError: 网络不支持
            RuntimeError: 所有 RPC 节点都不可用
        """
        if network not in self.rpcs:
            raise ValueError(
                f"不支持的网络: {network}. "
                f"支持的网络: {list(self.rpcs.keys())}"
            )

        # 如果已有可用实例，直接返回
        if network in self._web3_instances:
            w3 = self._web3_instances[network]
            if self._test_connection(w3):
                return w3
            else:
                # 当前实例不可用，尝试故障转移
                logger.warning(
                    "当前 RPC 节点不可用，尝试故障转移",
                    network=network
                )
                del self._web3_instances[network]

        # 尝试连接到可用的 RPC 节点
        rpc_urls = self.rpcs[network]
        start_index = self._current_rpc_index.get(network, 0)

        for i in range(len(rpc_urls)):
            index = (start_index + i) % len(rpc_urls)
            rpc_url = rpc_urls[index]

            try:
                w3 = Web3(Web3.HTTPProvider(rpc_url))

                if self._test_connection(w3):
                    self._web3_instances[network] = w3
                    self._current_rpc_index[network] = index

                    logger.info(
                        "成功连接到 RPC 节点",
                        network=network,
                        rpc_url=rpc_url[:50] + "..."
                    )

                    return w3

            except Exception as e:
                logger.warning(
                    "RPC 节点连接失败",
                    network=network,
                    rpc_url=rpc_url[:50] + "...",
                    error=str(e)
                )
                continue

        # 所有 RPC 节点都不可用
        error_msg = f"所有 RPC 节点都不可用: {network}"
        logger.error(error_msg, network=network)
        raise RuntimeError(error_msg)

    def _test_connection(self, w3: Web3) -> bool:
        """
        测试 Web3 连接是否可用

        Args:
            w3: Web3 实例

        Returns:
            是否可用
        """
        try:
            # 尝试获取最新区块号
            w3.eth.block_number
            return True
        except Exception:
            return False

    def add_rpc(self, network: str, rpc_url: str):
        """
        添加自定义 RPC 端点

        Args:
            network: 网络名称
            rpc_url: RPC URL
        """
        if network not in self.rpcs:
            self.rpcs[network] = []

        if rpc_url not in self.rpcs[network]:
            self.rpcs[network].append(rpc_url)

            logger.info(
                "添加 RPC 端点",
                network=network,
                rpc_url=rpc_url[:50] + "..."
            )

    def get_available_networks(self) -> List[str]:
        """获取支持的网络列表"""
        return list(self.rpcs.keys())

    def get_current_rpc_url(self, network: str) -> Optional[str]:
        """
        获取当前使用的 RPC URL

        Args:
            network: 网络名称

        Returns:
            RPC URL 或 None
        """
        if network not in self._current_rpc_index:
            return None

        index = self._current_rpc_index[network]
        return self.rpcs[network][index]
