"""
EVM 链上查询工具

支持 Ethereum Mainnet 和 Sepolia Testnet
提供代币余额查询和合约调用功能
"""
from typing import Dict, Any, Optional
from web3 import Web3
from web3.exceptions import Web3Exception
import structlog

logger = structlog.get_logger(__name__)


class EVMTools:
    """EVM 链上查询工具集"""

    def __init__(self, rpc_manager):
        """
        初始化 EVM 工具

        Args:
            rpc_manager: RPC 节点管理器
        """
        self.rpc_manager = rpc_manager

    def get_token_balance(
        self,
        address: str,
        token_address: Optional[str] = None,
        network: str = "mainnet"
    ) -> Dict[str, Any]:
        """
        查询代币余额

        Args:
            address: 钱包地址
            token_address: ERC-20 代币合约地址（None 表示查询 ETH）
            network: 网络名称 (mainnet, sepolia)

        Returns:
            包含余额信息的字典

        Raises:
            ValueError: 地址无效
            RuntimeError: 查询失败
        """
        if not Web3.is_address(address):
            raise ValueError(f"无效的地址: {address}")

        logger.info(
            "查询代币余额",
            address=address,
            token=token_address or "ETH",
            network=network
        )

        try:
            w3 = self.rpc_manager.get_web3(network)

            if token_address is None:
                # 查询 ETH 余额
                balance_wei = w3.eth.get_balance(address)
                balance_eth = w3.from_wei(balance_wei, "ether")

                return {
                    "address": address,
                    "token": "ETH",
                    "balance": str(balance_eth),
                    "balance_wei": str(balance_wei),
                    "network": network
                }
            else:
                # 查询 ERC-20 代币余额
                if not Web3.is_address(token_address):
                    raise ValueError(f"无效的代币地址: {token_address}")

                # ERC-20 balanceOf ABI
                balance_of_abi = [{
                    "constant": True,
                    "inputs": [{"name": "_owner", "type": "address"}],
                    "name": "balanceOf",
                    "outputs": [{"name": "balance", "type": "uint256"}],
                    "type": "function"
                }]

                contract = w3.eth.contract(
                    address=Web3.to_checksum_address(token_address),
                    abi=balance_of_abi
                )

                balance = contract.functions.balanceOf(
                    Web3.to_checksum_address(address)
                ).call()

                return {
                    "address": address,
                    "token": token_address,
                    "balance": str(balance),
                    "network": network
                }

        except Web3Exception as e:
            error_msg = f"查询余额失败: {str(e)}"
            logger.error(error_msg, address=address, error=str(e))
            raise RuntimeError(error_msg) from e

        except Exception as e:
            error_msg = f"查询余额失败: {str(e)}"
            logger.error(error_msg, address=address, error=str(e))
            raise RuntimeError(error_msg) from e

    def call_contract(
        self,
        contract_address: str,
        function_name: str,
        function_abi: Dict,
        args: list = None,
        network: str = "mainnet"
    ) -> Any:
        """
        调用智能合约函数

        Args:
            contract_address: 合约地址
            function_name: 函数名称
            function_abi: 函数 ABI
            args: 函数参数列表
            network: 网络名称

        Returns:
            函数调用结果

        Raises:
            ValueError: 参数无效
            RuntimeError: 调用失败
        """
        if not Web3.is_address(contract_address):
            raise ValueError(f"无效的合约地址: {contract_address}")

        logger.info(
            "调用合约函数",
            contract=contract_address,
            function=function_name,
            network=network
        )

        try:
            w3 = self.rpc_manager.get_web3(network)

            contract = w3.eth.contract(
                address=Web3.to_checksum_address(contract_address),
                abi=[function_abi]
            )

            # 获取函数
            func = getattr(contract.functions, function_name)

            # 调用函数
            if args:
                result = func(*args).call()
            else:
                result = func().call()

            logger.info(
                "合约调用成功",
                contract=contract_address,
                function=function_name,
                result=str(result)[:100]
            )

            return result

        except Exception as e:
            error_msg = f"调用合约失败: {str(e)}"
            logger.error(
                error_msg,
                contract=contract_address,
                function=function_name,
                error=str(e)
            )
            raise RuntimeError(error_msg) from e

    def get_transaction_count(
        self,
        address: str,
        network: str = "mainnet"
    ) -> int:
        """
        查询地址的交易数量

        Args:
            address: 钱包地址
            network: 网络名称

        Returns:
            交易数量
        """
        if not Web3.is_address(address):
            raise ValueError(f"无效的地址: {address}")

        try:
            w3 = self.rpc_manager.get_web3(network)
            count = w3.eth.get_transaction_count(
                Web3.to_checksum_address(address)
            )

            logger.info(
                "查询交易数量",
                address=address,
                count=count,
                network=network
            )

            return count

        except Exception as e:
            error_msg = f"查询交易数量失败: {str(e)}"
            logger.error(error_msg, address=address, error=str(e))
            raise RuntimeError(error_msg) from e
