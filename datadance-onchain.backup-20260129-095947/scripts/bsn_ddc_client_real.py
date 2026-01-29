"""
BSN-DDC SDK 真实实现 - HTTP API 客户端

这个文件展示如何使用 HTTP API 实现真实的 BSN-DDC SDK 调用。
替换 init_sdk.py 中的 Mock 实现。
"""

import os
import requests
from typing import Dict, Any, Optional
from datetime import datetime


class BSNDDCClient:
    """BSN-DDC SDK 客户端 - 真实实现"""

    def __init__(self, gateway_url: str, api_key: str, chain: str = "taianchain"):
        """
        初始化 BSN-DDC 客户端

        Args:
            gateway_url: BSN-DDC 网关地址
            api_key: API 密钥
            chain: 链类型 (taianchain, wuhanchain, wenchangchain, zhongyichain)
        """
        self.gateway_url = gateway_url.rstrip('/')
        self.api_key = api_key
        self.chain = chain
        self.session = requests.Session()

        # 设置默认请求头
        self.session.headers.update({
            'Content-Type': 'application/json',
            'x-api-key': self.api_key,  # BSN-DDC 使用 x-api-key 头
        })

    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        发送 HTTP 请求到 BSN-DDC API

        Args:
            method: HTTP 方法 (GET, POST, etc.)
            endpoint: API 端点
            data: 请求体数据
            params: URL 参数

        Returns:
            API 响应数据

        Raises:
            requests.HTTPError: 请求失败
        """
        url = f"{self.gateway_url}/{endpoint}"

        try:
            response = self.session.request(
                method=method,
                url=url,
                json=data,
                params=params,
                timeout=30
            )
            response.raise_for_status()
            return response.json()

        except requests.exceptions.HTTPError as e:
            error_msg = f"BSN-DDC API 错误: {e.response.status_code}"
            if e.response.text:
                error_msg += f" - {e.response.text}"
            raise Exception(error_msg) from e

        except requests.exceptions.RequestException as e:
            raise Exception(f"网络请求失败: {str(e)}") from e

    # ==================== DDC 查询接口 ====================

    def query_ddc(self, ddc_id: str, contract_address: str) -> Dict[str, Any]:
        """
        查询 DDC 详情

        Args:
            ddc_id: DDC ID
            contract_address: 合约地址

        Returns:
            DDC 详情数据
        """
        endpoint = f"ddc/{contract_address}/{ddc_id}"
        return self._make_request('GET', endpoint)

    def query_ddc_owner(self, ddc_id: str, contract_address: str) -> Dict[str, Any]:
        """
        查询 DDC 持有者

        Args:
            ddc_id: DDC ID
            contract_address: 合约地址

        Returns:
            持有者信息
        """
        endpoint = f"ddc/{contract_address}/{ddc_id}/owner"
        return self._make_request('GET', endpoint)

    def query_ddcs_by_owner(
        self,
        owner_address: str,
        contract_address: str,
        page: int = 1,
        page_size: int = 100
    ) -> Dict[str, Any]:
        """
        查询指定地址持有的所有 DDC

        Args:
            owner_address: 持有者地址
            contract_address: 合约地址
            page: 页码
            page_size: 每页数量

        Returns:
            DDC 列表
        """
        endpoint = f"ddc/{contract_address}/owner/{owner_address}"
        params = {
            'page': page,
            'pageSize': page_size
        }
        return self._make_request('GET', endpoint, params=params)

    # ==================== 交易查询接口 ====================

    def query_transactions(
        self,
        contract_address: str,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        tx_type: Optional[str] = None,
        page: int = 1,
        page_size: int = 100
    ) -> Dict[str, Any]:
        """
        查询交易历史

        Args:
            contract_address: 合约地址
            start_time: 开始时间 (ISO 8601 格式)
            end_time: 结束时间 (ISO 8601 格式)
            tx_type: 交易类型 (mint, transfer, burn)
            page: 页码
            page_size: 每页数量

        Returns:
            交易列表
        """
        endpoint = f"transactions/{contract_address}"
        params = {
            'page': page,
            'pageSize': page_size
        }

        if start_time:
            params['startTime'] = start_time
        if end_time:
            params['endTime'] = end_time
        if tx_type:
            params['type'] = tx_type

        return self._make_request('GET', endpoint, params=params)

    def query_transaction_by_hash(self, tx_hash: str) -> Dict[str, Any]:
        """
        根据交易哈希查询交易详情

        Args:
            tx_hash: 交易哈希

        Returns:
            交易详情
        """
        endpoint = f"transaction/{tx_hash}"
        return self._make_request('GET', endpoint)

    # ==================== 账户查询接口 ====================

    def query_account_balance(self, address: str) -> Dict[str, Any]:
        """
        查询账户余额

        Args:
            address: 账户地址

        Returns:
            账户余额信息
        """
        endpoint = f"account/{address}/balance"
        return self._make_request('GET', endpoint)

    def query_account_ddcs(
        self,
        address: str,
        page: int = 1,
        page_size: int = 100
    ) -> Dict[str, Any]:
        """
        查询账户持有的所有 DDC

        Args:
            address: 账户地址
            page: 页码
            page_size: 每页数量

        Returns:
            DDC 列表
        """
        endpoint = f"account/{address}/ddcs"
        params = {
            'page': page,
            'pageSize': page_size
        }
        return self._make_request('GET', endpoint, params=params)


def initialize_bsn_ddc_sdk(
    gateway_url: Optional[str] = None,
    api_key: Optional[str] = None,
    chain: str = "taianchain"
) -> BSNDDCClient:
    """
    初始化 BSN-DDC SDK 客户端

    Args:
        gateway_url: BSN-DDC 网关地址（如果为 None，从环境变量读取）
        api_key: API 密钥（如果为 None，从环境变量读取）
        chain: 链类型

    Returns:
        BSNDDCClient 实例

    Raises:
        ValueError: 缺少必需的配置参数
    """
    # 从环境变量读取配置
    gateway_url = gateway_url or os.getenv('BSN_DDC_GATEWAY_URL')
    api_key = api_key or os.getenv('BSN_DDC_API_KEY')
    chain = os.getenv('BSN_DDC_CHAIN', chain)

    # 验证必需参数
    if not gateway_url:
        raise ValueError(
            "BSN_DDC_GATEWAY_URL is required. "
            "Set it in .env file or pass as parameter."
        )

    if not api_key:
        raise ValueError(
            "BSN_DDC_API_KEY is required. "
            "Set it in .env file or pass as parameter."
        )

    # 创建客户端实例
    client = BSNDDCClient(
        gateway_url=gateway_url,
        api_key=api_key,
        chain=chain
    )

    return client


def validate_configuration() -> Dict[str, bool]:
    """
    验证 BSN-DDC 配置是否完整

    Returns:
        配置验证结果
    """
    return {
        'gateway_url_set': bool(os.getenv('BSN_DDC_GATEWAY_URL')),
        'api_key_set': bool(os.getenv('BSN_DDC_API_KEY')),
        'chain_valid': os.getenv('BSN_DDC_CHAIN', 'taianchain') in [
            'taianchain', 'wuhanchain', 'wenchangchain', 'zhongyichain'
        ]
    }


# ==================== 测试代码 ====================

if __name__ == "__main__":
    print("Testing BSN-DDC SDK (Real Implementation)...\n")

    # 验证配置
    config = validate_configuration()
    print("Configuration validation:")
    for key, value in config.items():
        status = "✓" if value else "✗"
        print(f"  {status} {key}: {value}")

    if not all(config.values()):
        print("\n✗ Configuration incomplete. Please set required environment variables:")
        if not config['gateway_url_set']:
            print("  - BSN_DDC_GATEWAY_URL")
        if not config['api_key_set']:
            print("  - BSN_DDC_API_KEY")
        exit(1)

    try:
        # 初始化 SDK
        sdk = initialize_bsn_ddc_sdk()
        print("\n✓ SDK initialized successfully")

        # 测试查询（需要真实的合约地址）
        # contract_address = "0x..."  # 替换为真实合约地址
        # result = sdk.query_transactions(contract_address, page_size=10)
        # print(f"\n✓ Query successful: {len(result.get('data', []))} transactions found")

    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        exit(1)
