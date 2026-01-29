# 🚀 BSN-DDC SDK 真实实现完整指南

## 📋 目录

1. [获取 API 凭证](#获取-api-凭证)
2. [配置环境变量](#配置环境变量)
3. [安装依赖](#安装依赖)
4. [替换 Mock 实现](#替换-mock-实现)
5. [测试真实调用](#测试真实调用)
6. [常见问题](#常见问题)

---

## 🔑 获取 API 凭证

### 步骤 1: 注册 BSN-DDC 账号

1. 访问 BSN-DDC 官方平台: https://ddc.bsnbase.com
2. 点击"注册"创建账号
3. 完成实名认证（可能需要）

### 步骤 2: 创建应用

1. 登录后进入"控制台"
2. 点击"创建应用"
3. 填写应用信息：
   - 应用名称: `Promise Breaker Detector`
   - 应用类型: `数据查询`
   - 选择链: `泰安链` (或其他支持的链)

### 步骤 3: 获取 API Key

在应用详情页面，你会看到：

```
Gateway URL: https://opbningxia.bsngate.com:18602/api/taianchain/v1
API Key: a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6
User Address: 0x1234567890abcdef1234567890abcdef12345678
```

**重要**:
- 测试环境端口: `18602`
- 生产环境端口: `17602`
- API Key 只显示一次，请妥善保存

---

## ⚙️ 配置环境变量

### 步骤 1: 复制配置模板

```bash
cd /home/ssszyy/code/web3/hackason-project/datadance-onchain
cp .env.example .env
```

### 步骤 2: 编辑 .env 文件

```bash
# 使用你喜欢的编辑器
nano .env
# 或
vim .env
```

### 步骤 3: 填入真实凭证

```bash
# BSN-DDC 配置
BSN_DDC_GATEWAY_URL=https://opbningxia.bsngate.com:18602/api/taianchain/v1
BSN_DDC_API_KEY=你的_API_KEY_这里
BSN_DDC_CHAIN=taianchain
BSN_DDC_USER_ADDRESS=0x你的地址这里

# 可选配置
DEBUG=true
```

**支持的链类型**:
- `taianchain` - 泰安链 (FISCO BCOS)
- `wuhanchain` - 武汉链 (Ethereum)
- `wenchangchain` - 文昌链 (IRITA)
- `zhongyichain` - 中移链 (EOS)

### 步骤 4: 验证配置

```bash
# 激活 conda 环境
conda activate hackason

# 测试配置
python scripts/bsn_ddc_client_real.py
```

预期输出：
```
Testing BSN-DDC SDK (Real Implementation)...

Configuration validation:
  ✓ gateway_url_set: True
  ✓ api_key_set: True
  ✓ chain_valid: True

✓ SDK initialized successfully
```

---

## 📦 安装依赖

### 方式 1: 使用 requirements.txt（推荐）

```bash
# 激活 conda 环境
conda activate hackason

# 安装依赖
pip install requests python-dotenv
```

### 方式 2: 手动安装

```bash
conda activate hackason
pip install requests==2.31.0
pip install python-dotenv==1.0.0
```

### 验证安装

```bash
python -c "import requests; print(f'requests {requests.__version__}')"
```

---

## 🔄 替换 Mock 实现

### 方案 A: 使用新的真实实现文件（推荐）

我已经创建了 `bsn_ddc_client_real.py`，包含完整的真实实现。

**在你的代码中使用**:

```python
# 旧的 Mock 实现
# from scripts.init_sdk import initialize_bsn_ddc_sdk

# 新的真实实现
from scripts.bsn_ddc_client_real import initialize_bsn_ddc_sdk

# 使用方式完全相同
sdk = initialize_bsn_ddc_sdk()
```

### 方案 B: 直接替换 init_sdk.py

如果你想保持原有的导入路径，可以：

```bash
# 备份原文件
mv scripts/init_sdk.py scripts/init_sdk_mock.py

# 使用真实实现
cp scripts/bsn_ddc_client_real.py scripts/init_sdk.py
```

### 更新其他脚本

需要更新以下文件以使用真实的 SDK 调用：

1. **query_ddc.py** - 查询 DDC 详情
2. **query_transactions.py** - 查询交易历史

让我为你展示如何更新这些文件...

---

## 🧪 测试真实调用

### 测试 1: 验证 SDK 初始化

```bash
conda activate hackason
python scripts/bsn_ddc_client_real.py
```

### 测试 2: 查询真实数据

创建测试脚本 `test_real_query.py`:

```python
import os
from dotenv import load_dotenv
from scripts.bsn_ddc_client_real import initialize_bsn_ddc_sdk

# 加载环境变量
load_dotenv()

# 初始化 SDK
sdk = initialize_bsn_ddc_sdk()

# 测试查询（需要真实的合约地址）
contract_address = "0x..."  # 替换为真实合约地址

try:
    # 查询交易历史
    result = sdk.query_transactions(
        contract_address=contract_address,
        page=1,
        page_size=10
    )

    print(f"✓ 查询成功!")
    print(f"  找到 {len(result.get('data', []))} 条交易")

    # 打印第一条交易
    if result.get('data'):
        first_tx = result['data'][0]
        print(f"\n第一条交易:")
        print(f"  哈希: {first_tx.get('txHash')}")
        print(f"  类型: {first_tx.get('type')}")
        print(f"  时间: {first_tx.get('timestamp')}")

except Exception as e:
    print(f"✗ 查询失败: {str(e)}")
```

运行测试:

```bash
conda activate hackason
python test_real_query.py
```

---

## ❓ 常见问题

### Q1: 如何获取测试用的合约地址？

**A**: 有几种方式：

1. **在 BSN-DDC 控制台创建测试合约**:
   - 登录控制台
   - 进入"合约管理"
   - 点击"部署合约"
   - 选择"DDC 721"或"DDC 1155"
   - 部署后获得合约地址

2. **使用示例合约地址**（如果 BSN 提供）:
   - 查看 BSN-DDC 文档的"快速开始"部分
   - 通常会提供测试合约地址

3. **查询已有项目的合约**:
   - 如果你的项目已经部署了 NFT 合约
   - 使用该合约地址进行查询

### Q2: API 调用失败，返回 401 错误

**A**: 检查以下几点：

1. **API Key 是否正确**:
   ```bash
   echo $BSN_DDC_API_KEY
   ```

2. **API Key 是否过期**:
   - 登录控制台检查 API Key 状态
   - 如果过期，重新生成

3. **请求头是否正确**:
   - 确保使用 `x-api-key` 头
   - 检查 `bsn_ddc_client_real.py` 中的头设置

### Q3: 如何切换测试环境和生产环境？

**A**: 修改 `.env` 文件中的 Gateway URL：

```bash
# 测试环境（端口 18602）
BSN_DDC_GATEWAY_URL=https://opbningxia.bsngate.com:18602/api/taianchain/v1

# 生产环境（端口 17602）
BSN_DDC_GATEWAY_URL=https://opbningxia.bsngate.com:17602/api/taianchain/v1
```

### Q4: 查询返回空数据怎么办？

**A**: 可能的原因：

1. **合约地址错误**: 检查地址格式（0x 开头）
2. **时间范围不对**: 调整 `start_time` 和 `end_time`
3. **合约没有交易**: 使用有交易记录的合约测试
4. **权限不足**: 确认 API Key 有查询权限

### Q5: 如何处理分页查询？

**A**: 使用循环获取所有数据：

```python
def query_all_transactions(sdk, contract_address):
    """查询所有交易（处理分页）"""
    all_transactions = []
    page = 1
    page_size = 100

    while True:
        result = sdk.query_transactions(
            contract_address=contract_address,
            page=page,
            page_size=page_size
        )

        transactions = result.get('data', [])
        if not transactions:
            break

        all_transactions.extend(transactions)

        # 检查是否还有更多数据
        total = result.get('total', 0)
        if len(all_transactions) >= total:
            break

        page += 1

    return all_transactions
```

### Q6: 如何调试 API 调用？

**A**: 启用调试模式：

```python
import logging

# 启用 requests 库的调试日志
logging.basicConfig(level=logging.DEBUG)

# 或者在 .env 中设置
DEBUG=true
```

---

## 📚 API 参考

### 常用端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `/ddc/{contract}/{id}` | GET | 查询 DDC 详情 |
| `/ddc/{contract}/{id}/owner` | GET | 查询 DDC 持有者 |
| `/transactions/{contract}` | GET | 查询交易历史 |
| `/transaction/{hash}` | GET | 查询交易详情 |
| `/account/{address}/balance` | GET | 查询账户余额 |
| `/account/{address}/ddcs` | GET | 查询账户 DDC |

### 响应格式

成功响应:
```json
{
  "code": 0,
  "message": "success",
  "data": {
    // 具体数据
  }
}
```

错误响应:
```json
{
  "code": 1001,
  "message": "Invalid API key",
  "data": null
}
```

---

## 🎯 下一步

1. ✅ 获取 API 凭证
2. ✅ 配置环境变量
3. ✅ 测试 SDK 初始化
4. ⏭️ 更新 query_ddc.py 使用真实调用
5. ⏭️ 更新 query_transactions.py 使用真实调用
6. ⏭️ 集成到 VerificationAgent
7. ⏭️ 端到端测试

---

**需要帮助？**

- BSN-DDC 官方文档: https://ddc.bsnbase.com/static/docs/index.html
- 技术支持: support@bsnbase.com
- 开发者社区: https://forum.bsnbase.com

---

**最后更新**: 2026-01-29
