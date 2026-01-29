# 项目规则 - Promise Breaker Detector (画饼识破)

## Python 环境要求

**重要**: 本项目所有 Python 代码必须在 conda 虚拟环境中执行。

### 环境配置

- **环境名称**: `hackason`
- **环境路径**: `/home/ssszyy/miniconda3/envs/hackason`
- **Python 版本**: 3.x (由 conda 环境管理)

### 执行规则

1. **每次执行 Python 脚本前必须激活环境**:
   ```bash
   conda activate hackason
   ```

2. **执行 Python 命令的标准格式**:
   ```bash
   # 方式 1: 先激活环境
   conda activate hackason && python script.py

   # 方式 2: 使用环境的 Python 解释器
   /home/ssszyy/miniconda3/envs/hackason/bin/python script.py
   ```

3. **安装依赖**:
   ```bash
   conda activate hackason && pip install -r requirements.txt
   ```

### 项目结构

```
hackason-project/
├── spoon-core/           # SpoonOS 核心框架
├── spoon-toolkit/        # SpoonOS 工具包
├── spoon-starter/        # SpoonOS 启动器
├── spoon-awesome-skill/  # SpoonOS 技能库
├── spoonos-assistant/    # SpoonOS 助手
├── datadance-onchain/    # BSN-DDC SDK 集成插件
├── docs/                 # 项目文档
│   ├── REQUIREMENTS_V1.md
│   └── REQUIREMENTS_V1_REVIEW.md
├── requirements.txt      # Python 依赖
└── .env                  # 环境变量配置
```

## 技术栈

### 后端框架
- **SpoonOS 0.3.6**: AI Agent 框架
- **FastAPI**: Web API 框架
- **Web3.py**: 区块链交互
- **BSN-DDC SDK**: 链上数据查询

### 前端框架
- **Next.js**: React 框架
- **TypeScript**: 类型安全

### 区块链
- **BSN (Blockchain Service Network)**: 中国区块链服务网络
- **支持链**: 泰安链 (FISCO BCOS)、武汉链 (Ethereum)、文昌链 (IRITA)、中移链 (EOS)

## 开发规范

### 代码风格
- Python: 遵循 PEP 8
- TypeScript: 使用 ESLint + Prettier
- 注释语言: 中文（与现有代码库保持一致）

### Git 工作流
- **重要**: 除非用户明确要求，否则不要主动执行 git commit、git push 等操作
- 分支命名: `feature/功能名`、`fix/问题描述`
- 提交信息: 使用中文，格式为 `类型: 简短描述`

### 环境变量
- 敏感信息存储在 `.env` 文件中
- 使用 `.env.example` 作为模板
- 必需的环境变量:
  - `BSN_DDC_GATEWAY_URL`: BSN-DDC 网关地址
  - `BSN_DDC_API_KEY`: BSN-DDC API 密钥
  - SpoonOS 相关配置（参考各子项目的 .env.example）

## 项目特定规则

### datadance-onchain 插件
- 位置: `/home/ssszyy/code/web3/hackason-project/datadance-onchain/`
- 用途: BSN-DDC SDK 集成，提供链上数据查询和预处理
- 当前状态: MVP 阶段，使用 Mock 实现
- 生产部署前需要: 替换 Mock 为实际 SDK 调用

### SpoonOS Agent 开发
- 使用 ReAct 模式进行工具调用
- 使用 Graph 模式进行多 Agent 编排
- 工具定义遵循 `BaseTool` 接口
- Agent 定义遵循 `BaseAgent` 接口

## 测试规范

### 单元测试
- 使用 pytest 框架
- 测试文件命名: `test_*.py`
- 测试覆盖率目标: > 80%

### 集成测试
- 测试 Agent 与工具的集成
- 测试多 Agent 协作流程
- 测试链上数据查询和处理

## 文档规范

### 代码文档
- 所有函数必须包含 docstring
- 使用类型提示 (Type Hints)
- 复杂逻辑添加行内注释

### 项目文档
- README.md: 项目概述和快速开始
- REQUIREMENTS.md: 详细需求文档
- API 文档: 使用 FastAPI 自动生成

## 安全规范

### 凭证管理
- 永远不要在代码中硬编码凭证
- 使用环境变量管理敏感信息
- .env 文件必须在 .gitignore 中

### 区块链安全
- 私钥管理: 使用环境变量或密钥管理服务
- 交易签名: 在本地完成，不传输私钥
- 金额验证: 执行交易前验证金额和接收地址

## 性能优化

### 数据处理
- 大量数据使用批量查询
- 实现数据缓存机制
- 异步处理耗时操作

### LLM 上下文优化
- 使用数据清洗减少冗余信息
- 实现紧凑模式格式化
- 控制上下文长度在合理范围

---

**最后更新**: 2026-01-29
**维护者**: Promise Breaker Team
