#!/usr/bin/env python3
"""测试 Chainbase 导入问题"""

import sys
import os

# 添加 spoon-toolkit 到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'spoon-toolkit'))

print("Step 1: 导入 balance.mcp")
try:
    from spoon_toolkits.data_platforms.chainbase.balance import mcp as balance_mcp
    print(f"  balance_mcp type: {type(balance_mcp)}")
    print(f"  balance_mcp has _lifespan: {hasattr(balance_mcp, '_lifespan')}")
except Exception as e:
    print(f"  Error: {e}")
    import traceback
    traceback.print_exc()

print("\nStep 2: 导入 basic.mcp")
try:
    from spoon_toolkits.data_platforms.chainbase.basic import mcp as basic_mcp
    print(f"  basic_mcp type: {type(basic_mcp)}")
    print(f"  basic_mcp has _lifespan: {hasattr(basic_mcp, '_lifespan')}")
except Exception as e:
    print(f"  Error: {e}")
    import traceback
    traceback.print_exc()

print("\nStep 3: 导入 token_api.mcp")
try:
    from spoon_toolkits.data_platforms.chainbase.token_api import mcp as token_api_mcp
    print(f"  token_api_mcp type: {type(token_api_mcp)}")
    print(f"  token_api_mcp has _lifespan: {hasattr(token_api_mcp, '_lifespan')}")
except Exception as e:
    print(f"  Error: {e}")
    import traceback
    traceback.print_exc()

print("\nStep 4: 创建主服务器")
try:
    from fastmcp import FastMCP
    mcp_server = FastMCP(name="TestServer")
    print(f"  mcp_server type: {type(mcp_server)}")
except Exception as e:
    print(f"  Error: {e}")
    import traceback
    traceback.print_exc()

print("\nStep 5: 尝试 mount")
try:
    print(f"  Mounting balance_mcp (type: {type(balance_mcp)})")
    mcp_server.mount("Balance", balance_mcp)
    print("  Mount successful!")
except Exception as e:
    print(f"  Error: {e}")
    import traceback
    traceback.print_exc()
