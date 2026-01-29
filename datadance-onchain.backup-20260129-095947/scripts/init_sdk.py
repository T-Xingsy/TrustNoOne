"""
BSN-DDC SDK Initialization Module

This module provides functions to initialize and configure the BSN-DDC SDK
for querying on-chain DDC/NFT data.

Usage:
    from scripts.init_sdk import initialize_bsn_ddc_sdk

    sdk = initialize_bsn_ddc_sdk(
        gateway_url="https://your-gateway-url",
        api_key="your-api-key"
    )
"""

import os
from typing import Optional, Dict, Any


class BSNDDCClient:
    """
    BSN-DDC SDK Client wrapper

    This is a simplified wrapper around the actual BSN-DDC SDK.
    In production, replace this with the real @ddcmarket/sdk implementation.
    """

    def __init__(self, gateway_url: str, api_key: str, chain: str = "taianchain"):
        """
        Initialize BSN-DDC client

        Args:
            gateway_url: BSN-DDC gateway endpoint
            api_key: API authentication key
            chain: Target blockchain (taianchain/wuhanchain/wenchangchain/zhongyichain)
        """
        self.gateway_url = gateway_url
        self.api_key = api_key
        self.chain = chain
        self.headers = {
            "x-api-key": api_key,
            "Content-Type": "application/json"
        }

    def set_gateway_url(self, url: str) -> bool:
        """Set gateway URL"""
        self.gateway_url = url
        return True

    def set_api_key(self, key: str) -> bool:
        """Set API key"""
        self.api_key = key
        self.headers["x-api-key"] = key
        return True

    def get_config(self) -> Dict[str, Any]:
        """Get current configuration"""
        return {
            "gateway_url": self.gateway_url,
            "chain": self.chain,
            "api_key_set": bool(self.api_key)
        }


def initialize_bsn_ddc_sdk(
    gateway_url: Optional[str] = None,
    api_key: Optional[str] = None,
    chain: Optional[str] = None
) -> BSNDDCClient:
    """
    Initialize BSN-DDC SDK with configuration

    Args:
        gateway_url: BSN-DDC gateway endpoint (defaults to env var BSN_DDC_GATEWAY_URL)
        api_key: API authentication key (defaults to env var BSN_DDC_API_KEY)
        chain: Target blockchain (defaults to env var BSN_DDC_CHAIN or 'taianchain')

    Returns:
        Configured BSNDDCClient instance

    Raises:
        ValueError: If required configuration is missing

    Example:
        >>> sdk = initialize_bsn_ddc_sdk()
        >>> config = sdk.get_config()
        >>> print(config)
        {'gateway_url': 'https://...', 'chain': 'taianchain', 'api_key_set': True}
    """
    # Load from environment variables if not provided
    gateway_url = gateway_url or os.getenv('BSN_DDC_GATEWAY_URL')
    api_key = api_key or os.getenv('BSN_DDC_API_KEY')
    chain = chain or os.getenv('BSN_DDC_CHAIN', 'taianchain')

    # Validate required configuration
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

    # Validate chain
    valid_chains = ['taianchain', 'wuhanchain', 'wenchangchain', 'zhongyichain']
    if chain not in valid_chains:
        raise ValueError(
            f"Invalid chain '{chain}'. Must be one of: {', '.join(valid_chains)}"
        )

    # Initialize client
    client = BSNDDCClient(
        gateway_url=gateway_url,
        api_key=api_key,
        chain=chain
    )

    print(f"✓ BSN-DDC SDK initialized successfully")
    print(f"  Gateway: {gateway_url}")
    print(f"  Chain: {chain}")

    return client


def validate_configuration() -> Dict[str, bool]:
    """
    Validate BSN-DDC SDK configuration

    Returns:
        Dictionary with validation results

    Example:
        >>> results = validate_configuration()
        >>> if all(results.values()):
        ...     print("Configuration is valid")
    """
    results = {
        "gateway_url_set": bool(os.getenv('BSN_DDC_GATEWAY_URL')),
        "api_key_set": bool(os.getenv('BSN_DDC_API_KEY')),
        "chain_valid": os.getenv('BSN_DDC_CHAIN', 'taianchain') in [
            'taianchain', 'wuhanchain', 'wenchangchain', 'zhongyichain'
        ]
    }

    return results


if __name__ == "__main__":
    # Test initialization
    print("Testing BSN-DDC SDK initialization...")
    print()

    # Check configuration
    print("Configuration validation:")
    validation = validate_configuration()
    for key, value in validation.items():
        status = "✓" if value else "✗"
        print(f"  {status} {key}: {value}")
    print()

    # Try to initialize
    if all(validation.values()):
        try:
            sdk = initialize_bsn_ddc_sdk()
            print()
            print("SDK configuration:")
            config = sdk.get_config()
            for key, value in config.items():
                print(f"  {key}: {value}")
        except Exception as e:
            print(f"✗ Initialization failed: {e}")
    else:
        print("✗ Configuration incomplete. Please set required environment variables:")
        if not validation["gateway_url_set"]:
            print("  - BSN_DDC_GATEWAY_URL")
        if not validation["api_key_set"]:
            print("  - BSN_DDC_API_KEY")
        if not validation["chain_valid"]:
            print("  - BSN_DDC_CHAIN (optional, defaults to 'taianchain')")
