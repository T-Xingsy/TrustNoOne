# Quick Start Guide: NFT 项目承诺验证系统

**Feature**: 001-nft-promise-verification
**Date**: 2026-01-30
**Related**: [spec.md](./spec.md) | [plan.md](./plan.md) | [data-model.md](./data-model.md)

---

## 概述

本指南帮助开发者快速搭建和运行 NFT 项目承诺验证系统，从环境配置到第一次验证任务的完整流程。

---

## 前置要求

### 系统要求
- **操作系统**: Linux (推荐 Ubuntu 20.04+) 或 WSL2
- **Python**: 3.11+ (通过 conda 管理)
- **内存**: 至少 4GB RAM
- **磁盘空间**: 至少 2GB 可用空间

### 必需的账号和密钥
1. **Twitter API** (可选，MVP 阶段使用 snscrape)
2. **Ethereum RPC 节点**:
   - Infura 账号: https://infura.io/
   - 或 Alchemy 账号: https://www.alchemy.com/
3. **OpenAI API Key** 或 **Anthropic API Key**:
   - OpenAI: https://platform.openai.com/api-keys
   - Anthropic: https://console.anthropic.com/

---

## 步骤 1: 环境配置

### 1.1 激活 Conda 环境

```bash
# 激活 hackason 环境
conda activate hackason

# 验证 Python 版本
python --version  # 应显示 Python 3.11.x
```

### 1.2 克隆项目（如果尚未克隆）

```bash
cd /home/ssszyy/code/web3/hackason-project
git checkout 001-nft-promise-verification
```

### 1.3 创建项目目录

```bash
mkdir -p nft-promise-verification
cd nft-promise-verification
```

---

## 步骤 2: 安装依赖

### 2.1 创建 requirements.txt

```bash
cat > requirements.txt << 'DEPS'
# SpoonOS Framework
spoon-core==0.3.6
spoon-toolkit==0.2.5

# Web Framework
fastapi==0.100.0
uvicorn[standard]==0.23.0

# Blockchain
web3==6.11.0

# Data Validation
pydantic==2.5.0
pydantic-settings==2.1.0

# Database
aiosqlite==0.19.0

# Twitter Scraping (MVP)
snscrape==0.7.0.20230622

# Web Scraping
beautifulsoup4==4.12.0
requests==2.31.0

# LLM
anthropic==0.7.0
openai==1.3.0

# Logging
structlog==23.2.0

# Configuration
python-dotenv==1.0.0

# Testing
pytest==7.4.0
pytest-asyncio==0.21.0
pytest-mock==3.12.0

# Utilities
python-dateutil==2.8.2
DEPS
```

### 2.2 安装依赖

```bash
conda activate hackason && pip install -r requirements.txt
```

---

## 步骤 3: 配置环境变量

### 3.1 创建 .env 文件

```bash
cat > config/.env << 'ENV'
# LLM Configuration
ANTHROPIC_API_KEY=your_anthropic_api_key_here
OPENAI_API_KEY=your_openai_api_key_here

# Ethereum RPC URLs
ETHEREUM_MAINNET_RPC_URL=https://mainnet.infura.io/v3/YOUR_INFURA_PROJECT_ID
ETHEREUM_SEPOLIA_RPC_URL=https://sepolia.infura.io/v3/YOUR_INFURA_PROJECT_ID

# Backup RPC URLs (Alchemy)
ETHEREUM_MAINNET_RPC_URL_BACKUP=https://eth-mainnet.g.alchemy.com/v2/YOUR_ALCHEMY_API_KEY
ETHEREUM_SEPOLIA_RPC_URL_BACKUP=https://eth-sepolia.g.alchemy.com/v2/YOUR_ALCHEMY_API_KEY

# Database
DATABASE_PATH=database/promise_breaker.db

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# Application
APP_ENV=development
APP_PORT=8000
ENV
```

### 3.2 替换占位符

```bash
# 使用你的实际 API Key 替换占位符
nano config/.env
```

---

## 步骤 4: 初始化数据库

### 4.1 创建数据库初始化脚本

```bash
mkdir -p database
cat > database/init_db.py << 'PYTHON'
import sqlite3
import os

def init_database():
    """初始化 SQLite 数据库"""
    db_path = os.getenv("DATABASE_PATH", "database/promise_breaker.db")
    
    # 确保目录存在
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 创建 projects 表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            twitter_account TEXT,
            website_url TEXT,
            whitepaper_url TEXT,
            contract_address TEXT,
            github_repo TEXT,
            treasury_address TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_verified_at TIMESTAMP
        )
    """)
    
    # 创建 promises 表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS promises (
            id TEXT PRIMARY KEY,
            project_id TEXT NOT NULL,
            content TEXT NOT NULL,
            sources TEXT NOT NULL,
            promise_type TEXT NOT NULL,
            target_date DATE,
            verification_status TEXT DEFAULT 'pending',
            importance_weight REAL DEFAULT 1.0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
        )
    """)
    
    # 创建 verification_records 表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS verification_records (
            id TEXT PRIMARY KEY,
            project_id TEXT NOT NULL,
            verification_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            promise_breaking_index REAL NOT NULL,
            integrity_score REAL NOT NULL,
            fairness_score REAL NOT NULL,
            activity_score REAL NOT NULL,
            stability_score REAL NOT NULL,
            momentum_score REAL NOT NULL,
            total_promises INTEGER NOT NULL,
            fulfilled_count INTEGER NOT NULL,
            unfulfilled_count INTEGER NOT NULL,
            unverifiable_count INTEGER NOT NULL,
            report_details TEXT NOT NULL,
            FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
        )
    """)
    
    # 创建 privacy_storage_records 表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS privacy_storage_records (
            id TEXT PRIMARY KEY,
            project_id TEXT NOT NULL,
            storage_type TEXT NOT NULL,
            storage_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            tx_hash TEXT,
            privacy_address TEXT,
            data_hash TEXT NOT NULL,
            storage_status TEXT DEFAULT 'pending',
            FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
        )
    """)
    
    # 创建索引
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_promises_project_id ON promises(project_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_promises_verification_status ON promises(verification_status)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_verification_records_project_id ON verification_records(project_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_verification_records_time ON verification_records(verification_time DESC)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_privacy_storage_project_id ON privacy_storage_records(project_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_privacy_storage_status ON privacy_storage_records(storage_status)")
    
    conn.commit()
    conn.close()
    
    print(f"✅ 数据库初始化成功: {db_path}")

if __name__ == "__main__":
    init_database()
PYTHON
```

### 4.2 运行初始化脚本

```bash
conda activate hackason && python database/init_db.py
```

---

## 步骤 5: 创建核心文件

### 5.1 创建 LLM 配置

```bash
cat > llm_config.py << 'PYTHON'
from spoon_core.llm import LLMManager
import os

def get_llm():
    """获取 LLM 实例"""
    # 优先使用 Claude 3.5 Sonnet
    if os.getenv("ANTHROPIC_API_KEY"):
        return LLMManager.get_llm(
            provider="anthropic",
            model="claude-3-5-sonnet-20241022",
            temperature=0.3
        )
    # 备用 OpenAI GPT-4
    elif os.getenv("OPENAI_API_KEY"):
        return LLMManager.get_llm(
            provider="openai",
            model="gpt-4-turbo-preview",
            temperature=0.3
        )
    else:
        raise ValueError("未配置 LLM API Key")
PYTHON
```

### 5.2 创建工具配置

```bash
cat > tools_config.py << 'PYTHON'
from spoon_toolkit.social import TwitterTool
from spoon_toolkit.web import WebScraperTool
from spoon_toolkit.crypto import EVMGetTokenBalance, EVMCallContract

def get_tools():
    """获取所有工具实例"""
    return [
        TwitterTool(),
        WebScraperTool(),
        EVMGetTokenBalance(),
        EVMCallContract(),
    ]
PYTHON
```

### 5.3 创建简单的 Agent

```bash
cat > agent.py << 'PYTHON'
from spoon_core.agents import ReactAgent
from llm_config import get_llm
from tools_config import get_tools

class VerificationAgent:
    """NFT 承诺验证 Agent"""
    
    def __init__(self):
        self.llm = get_llm()
        self.tools = get_tools()
        self.agent = ReactAgent(
            llm=self.llm,
            tools=self.tools,
            verbose=True,
            max_iterations=10
        )
    
    def verify_project(self, project_info: dict) -> dict:
        """验证项目"""
        prompt = f"""
        请验证以下 NFT 项目的承诺兑现情况：
        
        项目名称: {project_info['name']}
        Twitter: {project_info.get('twitter_account', 'N/A')}
        官网: {project_info.get('website_url', 'N/A')}
        合约地址: {project_info.get('contract_address', 'N/A')}
        
        任务：
        1. 收集项目承诺（Twitter、官网）
        2. 查询链上数据
        3. 对比承诺与实际行为
        4. 计算画饼指数
        
        请返回验证结果。
        """
        
        result = self.agent.run(prompt)
        return result

if __name__ == "__main__":
    agent = VerificationAgent()
    
    # 测试项目
    test_project = {
        "name": "Test NFT Project",
        "twitter_account": "@TestNFT",
        "website_url": "https://testnft.com",
        "contract_address": "0x1234567890123456789012345678901234567890"
    }
    
    result = agent.verify_project(test_project)
    print(result)
PYTHON
```

---

## 步骤 6: 运行第一次验证

### 6.1 测试 Agent

```bash
conda activate hackason && python agent.py
```

### 6.2 预期输出

```
✅ Agent 初始化成功
🔍 正在收集项目承诺...
📊 正在查询链上数据...
🧮 正在计算画饼指数...
✅ 验证完成

画饼指数: 35.0
诚信审计: 75.0
公平性审计: 60.0
开发力审计: 80.0
财务稳定性: 70.0
社区动能: 65.0
```

---

## 步骤 7: 启动 API 服务（可选）

### 7.1 创建 FastAPI 应用

```bash
cat > main.py << 'PYTHON'
from fastapi import FastAPI
from agent import VerificationAgent

app = FastAPI(title="NFT Promise Verification API")
agent = VerificationAgent()

@app.post("/api/v1/projects/{project_id}/verify")
async def verify_project(project_id: str):
    """启动项目验证"""
    # TODO: 从数据库获取项目信息
    # TODO: 调用 agent.verify_project()
    return {"task_id": "xxx", "status": "pending"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
PYTHON
```

### 7.2 启动服务

```bash
conda activate hackason && python main.py
```

### 7.3 测试 API

```bash
# 健康检查
curl http://localhost:8000/health

# 查看 API 文档
open http://localhost:8000/docs
```

---

## 常见问题

### Q1: conda activate hackason 失败
**解决方案**:
```bash
# 初始化 conda
conda init bash
source ~/.bashrc

# 重新激活
conda activate hackason
```

### Q2: Twitter 数据抓取失败
**解决方案**:
- MVP 阶段使用 snscrape，无需 Twitter API
- 如果 snscrape 被封禁，添加请求延迟：
```python
import time
time.sleep(2)  # 每次请求间隔 2 秒
```

### Q3: RPC 节点限流
**解决方案**:
- 使用多个 RPC 提供商（Infura + Alchemy）
- 实现故障转移逻辑（参考 research.md）

### Q4: LLM Token 超限
**解决方案**:
- 使用数据清洗减少 Token 消耗
- 分批处理承诺数据（每批最多 50 条）

---

## 下一步

1. ✅ 完成环境配置和第一次验证
2. ⏳ 实现五维评分模块（scoring/）
3. ⏳ 集成 DDC-Market-SDK 隐私存储
4. ⏳ 编写单元测试和集成测试
5. ⏳ 开发前端可视化界面

---

## 参考资料

- [Feature Spec](./spec.md)
- [Implementation Plan](./plan.md)
- [Data Model](./data-model.md)
- [API Contracts](./contracts/api-spec.yaml)
- [Research Document](./research.md)

---

**Document Version**: 1.0.0
**Last Updated**: 2026-01-30
**Status**: ✅ Ready for Use
