# onchain-verifier 改进分析报告

## 执行摘要

本报告分析了 `onchain-verifier` 插件的当前状态，并基于 DDC-Market-SDK 的功能和 Promise Breaker Detector 项目的需求，提出了全面的改进方案。

**核心发现**：
- ✅ 当前实现：1 个 skill（onchain-data-query），使用 ethers.js
- ❌ 问题：未使用 DDC-Market-SDK，功能覆盖率仅约 15%
- ✅ 解决方案：设计 4 个新 skills，完全基于 DDC-Market-SDK

---

## 当前状态分析

### 现有 Skill: onchain-data-query

**位置**：`onchain-verifier/skills/onchain-data-query/`

**功能**：
- 查询 NFT Transfer 事件
- 验证空投承诺
- 生成 LLM 上下文

**技术栈**：
- 使用 ethers.js 的 `OnChainVerifier` 类
- 直接调用 RPC 查询事件

**问题**：
1. **未使用 DDC-Market-SDK**：项目依赖 DDC-Market-SDK，但 skill 使用 ethers.js
2. **功能覆盖不足**：
   - ❌ 无元数据查询（用户特别提到）
   - ❌ 无持有者分析
   - ❌ 无供应量验证
   - ❌ 无会员快照支持
3. **验证能力弱**：缺少与承诺内容的深度对比

---

## DDC-Market-SDK 功能分析

### 可用的查询 API

| API | 功能 | 用途 |
|-----|------|------|
| `getTokenURI(tokenId)` | 获取元数据 URI | **元数据查询**（用户需求） |
| `getOwnerOf(tokenId)` | 获取持有者 hash | 持有者分析 |
| `getTotalSupply()` | 获取总供应量 | 供应量验证 |
| `getName()` | 获取合约名称 | 合约信息 |
| `getSymbol()` | 获取合约符号 | 合约信息 |
| `getMemberSnapshot(id)` | 获取会员快照 | 会员分析 |
| `getLatestSnapshotId()` | 获取最新快照 ID | 会员分析 |
| `isMemberInSnapshot()` | 检查会员状态 | 会员验证 |

### 覆盖率对比

| 功能类别 | DDC-Market-SDK 支持 | 当前实现 | 覆盖率 |
|---------|-------------------|---------|--------|
| 元数据查询 | ✅ | ❌ | 0% |
| 持有者分析 | ✅ | ❌ | 0% |
| 供应量查询 | ✅ | ❌ | 0% |
| 事件查询 | ⚠️ (需要 ethers.js) | ✅ | 100% |
| 会员快照 | ✅ | ❌ | 0% |
| **总体** | - | - | **~15%** |

---

## 改进方案

### 新 Skills 架构

设计 4 个专注于验证的 skills，完全基于 DDC-Market-SDK：

#### 1. ddc-metadata-query ⭐ 高优先级
**目的**：查询和验证 NFT 元数据（用户特别提到）

**核心功能**：
- 获取 token 元数据 URI
- 下载并解析元数据 JSON
- 对比承诺内容
- 生成 LLM 上下文

**使用的 SDK API**：
- `getTokenURI(tokenId)`
- `getName()`, `getSymbol()`

**验证场景**：
- 验证 NFT 元数据是否符合承诺
- 验证名称、描述、属性一致性
- 验证图片资源可访问性

---

#### 2. ddc-supply-verification ⭐ 高优先级
**目的**：验证 NFT 铸造和供应量承诺

**核心功能**：
- 获取总供应量
- 计算履约率
- 评估证据强度
- 生成 LLM 上下文

**使用的 SDK API**：
- `getTotalSupply()`
- `getName()`, `getSymbol()`

**验证场景**：
- 验证铸造数量是否符合承诺
- 检测超发或少发
- 评估承诺兑现程度

---

#### 3. ddc-holder-analysis ⭐ 中优先级
**目的**：分析 NFT 持有者分布

**核心功能**：
- 获取持有者信息
- 统计持有者分布
- 识别大户和散户
- 生成 LLM 上下文

**使用的 SDK API**：
- `getOwnerOf(tokenId)`
- `getTotalSupply()`
- `getName()`, `getSymbol()`

**验证场景**：
- 验证持有者数量
- 分析持有者集中度
- 检测潜在操纵

---

#### 4. ddc-membership-snapshot ⭐ 低优先级
**目的**：分析会员快照，验证会员权益

**核心功能**：
- 获取会员快照
- 分析会员数量变化
- 验证"给所有持有者"承诺
- 生成 LLM 上下文

**使用的 SDK API**：
- `getMemberSnapshot(snapshotId)`
- `getLatestSnapshotId()`
- `isMemberInSnapshot()`
- `getTotalSupply()`

**验证场景**：
- 验证会员数量
- 验证特定时间点的会员列表
- 验证空投对象

---

## 实施计划

### Phase 1: 核心验证功能（2-4 周）
1. **ddc-metadata-query** - 2-3 天
   - 用户特别提到的元数据获取
   - 最高优先级

2. **ddc-supply-verification** - 1-2 天
   - 最常见的验证场景
   - 实现简单

### Phase 2: 高级分析功能（1-2 周）
3. **ddc-holder-analysis** - 3-4 天
   - 需要性能优化
   - 批量查询处理

### Phase 3: 会员系统支持（1 周）
4. **ddc-membership-snapshot** - 2-3 天
   - 仅在需要时实施
   - 依赖项目是否使用会员系统

---

## 技术要点

### 1. SDK 初始化
```typescript
import { DDCNFTManager } from '@ddc-market/sdk';

// JsonRpcProvider 模式（适合后端）
const manager = await DDCNFTManager.init({
  walletAddress: process.env.WALLET_ADDRESS,
  provider: { type: 'jsonRpc' },
  signer: { privateKey: process.env.PRIVATE_KEY },
  debug: true,
});

manager.setContractAddress(contractAddress);
```

### 2. 共享模块
- **sdk-client.ts**：SDK 客户端封装
- **llm-formatter.ts**：LLM 上下文格式化
- **utils.ts**：工具函数

### 3. 性能优化
- 并行查询：`Promise.all`
- 缓存机制：缓存合约信息和元数据
- 分页处理：处理大量 token

### 4. 错误处理
- RPC 超时：重试机制
- 合约不存在：友好错误信息
- 元数据解析失败：记录失败 token，继续处理

---

## 预期收益

### 功能覆盖率提升
- **当前**：~15%（仅事件查询）
- **改进后**：~85%（元数据、供应量、持有者、会员）

### 验证能力提升
- **当前**：基础的事件统计
- **改进后**：
  - 元数据内容验证
  - 供应量履约率计算
  - 持有者分布分析
  - 会员快照对比

### 技术栈统一
- **当前**：ethers.js（与项目依赖不一致）
- **改进后**：DDC-Market-SDK（与项目依赖一致）

### 用户体验提升
- **当前**：单一验证维度
- **改进后**：多维度验证，更全面的证据

---

## 风险和缓解

### 风险 1: SDK API 变更
**缓解**：
- 锁定 SDK 版本
- 编写适配层
- 定期检查更新

### 风险 2: RPC 性能问题
**缓解**：
- 重试机制
- 备用 RPC
- 缓存层
- 分页处理

### 风险 3: 元数据不可访问
**缓解**：
- 超时机制
- 记录失败 token
- 提供部分结果

---

## 下一步行动

### 立即开始（本周）
1. ✅ 完成需求分析和架构设计
2. ⏭️ 设置开发环境
   - 安装 DDC-Market-SDK
   - 配置环境变量
   - 创建目录结构

3. ⏭️ 实现 ddc-metadata-query skill
   - 创建基础文件
   - 实现 SDK 客户端
   - 实现元数据查询
   - 编写测试

### 短期目标（2 周内）
- 完成 Phase 1（ddc-metadata-query + ddc-supply-verification）
- 单元测试覆盖率 > 80%
- 与 SpoonOS Agent 集成测试

### 中期目标（1 个月内）
- 完成 Phase 2（ddc-holder-analysis）
- 性能优化和测试
- 完整文档

### 长期目标（按需）
- Phase 3（ddc-membership-snapshot）
- 持续优化和维护

---

## 附录

### 相关文档
- [Skills 架构设计](./SKILLS_ARCHITECTURE_DESIGN.md) - 详细的 skills 设计
- [实施计划](./IMPLEMENTATION_PLAN.md) - 详细的实施步骤
- [DDC-Market-SDK API 文档](../DDC-Market-SDK/API_DOCUMENTATION.md) - SDK API 参考

### 环境配置
```bash
# .env 文件
WALLET_ADDRESS=0x...
PRIVATE_KEY=your_private_key
DEBUG=true
CACHE_ENABLED=true
CACHE_TTL=3600
```

### 依赖安装
```bash
cd onchain-verifier
npm install @ddc-market/sdk ethers axios dotenv
npm install -D typescript @types/node jest ts-jest
```

---

**报告日期**: 2026-01-29
**分析者**: Promise Breaker Team
**状态**: ✅ 分析完成，等待实施
