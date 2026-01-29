# BSN-DDC SDK 真实实现指南

## 📋 概述

本指南说明如何将 datadance-onchain 插件中的 Mock 实现替换为真实的 BSN-DDC SDK 调用。

---

## 🔑 第一步：获取 API 凭证

### 1. 注册 BSN-DDC 账号

访问 BSN-DDC 官方平台：
- **官网**: https://ddc.bsnbase.com
- **文档**: https://ddc.bsnbase.com/static/docs/index.html

### 2. 获取 API Key

登录后，在控制台获取以下信息：

1. **Gateway URL** (网关地址):
   - 测试环境: `https://opbningxia.bsngate.com:18602/api/[chaincode]/v1`
   - 生产环境: `https://opbningxia.bsngate.com:17602/api/[chaincode]/v1`
   - 其中 `[chaincode]` 根据链类型替换：
     - 泰安链: `taianchain`
     - 武汉链: `wuhanchain`
     - 文昌链: `wenchangchain`
     - 中移链: `zhongyichain`

2. **API Key** (在"业务信息"页面):
   - 格式: 32 位字符串
   - 示例: `a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6`

3. **用户地址** (User Address):
   - 你的 BSN-DDC 账户地址
   - 格式: 0x 开头的以太坊地址

### 3. 配置环境变量

编辑 `.env` 文件：

```bash
# BSN-DDC 配置
BSN_DDC_GATEWAY_URL=https://opbningxia.bsngate.com:18602/api/taianchain/v1
BSN_DDC_API_KEY=your_api_key_here
BSN_DDC_CHAIN=taianchain
BSN_DDC_USER_ADDRESS=0x_your_address_here

# 可选配置
DEBUG=true
```

---

## 📦 第二步：安装 SDK

### 方式 1: 使用 npm 包（推荐）

```bash
# 激活 conda 环境
conda activate hackason

# 安装 BSN-DDC SDK
npm install @ddcmarket/sdk
```

### 方式 2: 使用 Python 包装器

如果 BSN-DDC 提供 Python SDK，直接安装：

```bash
conda activate hackason
pip install bsn-ddc-sdk  # 假设存在 Python 版本
```

### 方式 3: 使用 HTTP API（当前推荐）

BSN-DDC SDK 本质上是 RESTful API，可以直接使用 Python 的 `requests` 库：

```bash
conda activate hackason
pip install requests
```

---

## 🔧 第三步：实现真实 SDK 调用

### 1. 更新 `init_sdk.py`

<function_calls>
<invoke name="Read">
<parameter name="file_path">/home/ssszyy/code/web3/hackason-project/datadance-onchain/scripts/init_sdk.py