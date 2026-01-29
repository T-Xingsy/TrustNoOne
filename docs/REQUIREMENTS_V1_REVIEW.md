# 画饼识破项目需求文档审阅报告

## 📋 执行摘要

**项目名称**: 画饼识破 (Promise Breaker Detector)
**文档版本**: REQUIREMENTS_V1.md
**审阅日期**: 2026-01-28
**审阅结论**: ⚠️ 架构设计合理但存在过度设计风险，建议采用渐进式开发策略

---

## 一、整体评估

### 1.1 架构设计合理性 ⭐⭐⭐⭐☆ (4/5)

**优点**:
- ✅ Graph + ReAct 混合模式符合 SpoonOS 最佳实践
- ✅ Agent 职责划分清晰，符合单一职责原则
- ✅ 工具系统设计完整，覆盖核心功能
- ✅ 技术栈选择合理，与现有资源匹配

**问题**:
- ⚠️ **过度设计**: 5 个 Agent 对 MVP 阶段过于复杂
- ⚠️ **LLM 调用频繁**: 约 40 次调用，成本和延迟较高
- ⚠️ **缺少降级策略**: 任一环节失败导致全局失败
- ⚠️ **评分公式复杂**: 复杂性因子引入不必要的计算

### 1.2 关键发现

1. **项目已有完整的 SpoonOS 技能库**
   - 8 个 SpoonOS 框架技能（agent-development, graph-development 等）
   - 73 个可用的 Web3 工具脚本
   - 完整的示例代码和参考文档

2. **核心业务逻辑尚未实现**
   - 需要开发 5 个 Agent
   - 需要实现 9 个工具
   - 需要集成链上查询能力

3. **技术风险点**
   - Web3.py 功能有限，需补充 Etherscan API
   - BeautifulSoup 爬虫能力不足，建议改用 Playwright
   - 无错误恢复和降级机制

---

## 二、Agent 系统设计分析

### 2.1 当前设计评估

| Agent | 职责 | 必要性 | 建议 |
|-------|------|--------|------|
| GraphAgent | 主控协调 | ✅ 必须 | 保留 |
| DataCollectionAgent | 采集数据 | ✅ 必须 | 保留 |
| PromiseExtractorAgent | 提取承诺 | ⚠️ 可合并 | 合并到 DataCollection |
| VerificationAgent | 链上验证 | ✅ 核心 | 保留并优化 |
| ScoringAgent | 汇总评分 | ❌ 过于简单 | 改为函数节点 |

### 2.2 优化建议

**MVP 阶段**: 单 Agent 架构
```python
PromiseVerificationAgent (ReAct)
  ├─ TwitterScraperTool
  ├─ WebCrawlerTool
  ├─ OnChainQueryTool
  └─ FulfillmentAssessmentTool
```

**生产阶段**: 简化 Graph 架构
```python
GraphAgent
  ├─ DataAgent (采集+提取)
  └─ VerificationAgent (验证+评分)
```

### 2.3 ReAct 模式适用性

- ✅ **DataCollectionAgent**: 需要动态决策数据源
- ❌ **PromiseExtractorAgent**: 固定流程，改为函数节点
- ✅ **VerificationAgent**: 需要根据承诺类型选择策略
- ❌ **ScoringAgent**: 纯计算逻辑，改为函数节点

---

## 三、工具系统设计分析

### 3.1 工具完整性评估

**核心工具** (必须实现):
1. ✅ TwitterScraperTool - 采集推文
2. ✅ WebCrawlerTool - 爬取官网
3. ✅ OnChainQueryTool - 链上查询 (核心)
4. ✅ FulfillmentAssessmentTool - 对照评分 (核心)

**辅助工具** (可选):
5. ⚠️ ImpactAssessmentTool - 影响力评估
6. ❌ ComplexityAssessmentTool - MVP 可省略
7. ❌ PromiseExtractorTool - 改为函数
8. ❌ AggregateScoresTool - 改为函数
9. ❌ CalculatePigeonIndexTool - 改为函数

**缺失工具** (建议新增):
- ContractAddressResolverTool - 解析合约地址
- TimelineParserTool - 解析时间表达式

### 3.2 LLM 调用优化

**当前**: 约 40 次 LLM 调用
- PromiseExtractor: ~10 次
- ImpactAssessment: ~10 次
- ComplexityAssessment: ~10 次
- FulfillmentAssessment: ~10 次

**优化后**: 约 15 次 LLM 调用 (降低 62%)
- 批量提取: 1 次 (原 10 次)
- 影响力评估: 10 次
- 兑现评估: 10 次
- 省略复杂性评估

**成本估算**:
- 优化前: ~$0.40/项目
- 优化后: ~$0.15/项目

---

## 四、提示词设计分析

### 4.1 核心问题

1. **VerificationAgent 提示词过于复杂**
   - 3 个维度评分 + 复杂公式
   - 缺少 few-shot 示例
   - 负分计算逻辑不清晰

2. **评分公式不合理**
   ```python
   # 当前公式
   score = impact × (complexity / 100) × fulfillment

   # 问题: 简单承诺兑现反而得分低
   ```

### 4.2 改进建议

**简化评分公式**:
```python
# 推荐方案
score = impact × fulfillment

# 未兑现惩罚
if fulfillment < 0.3:
    score = -impact × 2.0
```

**添加 Few-shot 示例**:
- 完全兑现示例
- 未兑现示例
- 部分兑现示例

---

## 五、待讨论问题的专业建议

### 问题 1: 打分机制复杂度
**建议**: 选择方案 B (简化版)
- MVP: 影响力 × 兑现程度
- 生产: 可选添加复杂性加分

### 问题 2: 时间因素
**建议**: 选择方案 A (时间因素很重要)
- 延迟 1 个月: 0.9 倍
- 延迟 3 个月: 0.7 倍
- 延迟 6 个月: 0.5 倍

### 问题 3: 部分兑现
**建议**: 选择方案 C (LLM 判断)
- 综合考虑数量、范围、质量、时间
- 使用 few-shot 示例提高准确性

### 问题 4: 证据置信度
**建议**: 需要区分，但简化权重
- 链上证据: 1.0 (100%)
- 官方公告: 0.9 (90%)
- 媒体报道: 0.7 (70%)
- 社区反馈: 不采纳

### 问题 5: 链上数据来源
**建议**: Etherscan API + Web3.py 备用
- 主数据源: Etherscan API (免费额度充足)
- 备用: Web3.py + Alchemy
- 降级策略: 模拟数据 (标记低置信度)

### 问题 6: MVP 范围
**建议**: 强烈推荐先做 MVP
- 单 Agent ReAct 模式
- 3 个核心工具
- 简化评分公式
- CLI 界面
- 开发时间: 4-6 天

### 问题 7: 前端优先级
**建议**: 先后端 CLI，再加前端
- 第 1-3 天: 后端核心逻辑
- 第 4-5 天: 测试调试
- 第 6-7 天: 前端开发 (可选)

### 问题 8: LLM 选择
**建议**: 混合使用
- 简单任务: gpt-4o-mini
- 核心任务: gpt-4o
- ReAct 推理: gpt-4o

---

## 六、技术栈优化建议

### 6.1 后端技术栈

| 组件 | 当前 | 建议 | 理由 |
|------|------|------|------|
| Agent 框架 | SpoonOS 0.3.6 | ✅ 保持 | 符合项目定位 |
| Web 框架 | FastAPI | ✅ 保持 | 性能优秀 |
| 区块链 | Web3.py | ⚠️ 补充 Etherscan API | 功能更全 |
| 爬虫 | BeautifulSoup | ⚠️ 改用 Playwright | 支持动态内容 |

### 6.2 前端技术栈

| 组件 | 当前 | 建议 | 理由 |
|------|------|------|------|
| 框架 | Next.js 15.1 | ✅ 保持 | 现代化 |
| 状态管理 | React Hooks | ⚠️ 考虑 Zustand | 更简洁 |
| 图表库 | 无 | ➕ 添加 Recharts | 展示评分趋势 |

---

## 七、实施计划

### 7.1 MVP 开发计划 (4-6 天)

**第 1 天: 基础架构**
- [ ] 创建项目结构
- [ ] 配置 SpoonOS 环境
- [ ] 实现基础 Agent 框架

**第 2 天: 工具开发**
- [ ] TwitterScraperTool (模拟数据)
- [ ] WebCrawlerTool (模拟数据)
- [ ] OnChainQueryTool (模拟数据)

**第 3 天: 核心逻辑**
- [ ] FulfillmentAssessmentTool
- [ ] 评分算法实现
- [ ] Agent 提示词优化

**第 4 天: 集成测试**
- [ ] 端到端测试
- [ ] 调试和优化
- [ ] CLI 界面完善

**第 5-6 天: 优化和文档**
- [ ] 性能优化
- [ ] 错误处理
- [ ] 使用文档

### 7.2 生产版本计划 (后续迭代)

**阶段 1: Graph 架构升级**
- 实现 GraphAgent 主控
- 拆分为 DataAgent + VerificationAgent
- 添加并行验证能力

**阶段 2: 真实数据集成**
- 集成 Twitter API / 爬虫
- 集成 Etherscan API
- 实现降级策略

**阶段 3: 前端开发**
- Next.js 前端界面
- 实时进度展示
- 可视化报告

**阶段 4: 高级功能**
- 历史记录存储
- 项目对比分析
- 趋势预测

---

## 八、风险评估与缓解

### 8.1 技术风险

| 风险 | 影响 | 概率 | 缓解措施 |
|------|------|------|----------|
| LLM 输出不稳定 | 高 | 中 | Few-shot 示例 + 输出验证 |
| 链上查询速率限制 | 中 | 高 | 多数据源 + 降级策略 |
| Twitter 爬虫被封 | 高 | 中 | 使用官方 API + 代理池 |
| 评分算法争议 | 中 | 中 | 公开评分逻辑 + 社区反馈 |

### 8.2 项目风险

| 风险 | 影响 | 概率 | 缓解措施 |
|------|------|------|----------|
| 开发时间不足 | 高 | 中 | 先做 MVP，后续迭代 |
| 团队技能不匹配 | 中 | 低 | 使用现有技能库和示例 |
| 需求变更 | 中 | 中 | 模块化设计，易于调整 |

---

## 九、关键决策建议

### 9.1 立即决策 (影响 MVP)

1. **✅ 采用 MVP 优先策略**
   - 单 Agent 架构
   - 模拟数据
   - CLI 界面

2. **✅ 简化评分公式**
   - 去掉复杂性因子
   - score = impact × fulfillment

3. **✅ 混合使用 LLM**
   - 简单任务: gpt-4o-mini
   - 核心任务: gpt-4o

### 9.2 后续决策 (不影响 MVP)

4. **⏸️ Graph 架构升级**
   - MVP 验证后再决定

5. **⏸️ 前端开发**
   - 核心逻辑稳定后开发

6. **⏸️ 真实数据集成**
   - MVP 测试通过后集成

---

## 十、总结与建议

### 10.1 核心建议

1. **采用渐进式开发策略**
   - MVP (4-6 天) → 生产版本 (2-3 周) → 高级功能 (持续迭代)

2. **简化架构设计**
   - MVP: 单 Agent + 3 工具
   - 生产: 2 Agent + 6 工具

3. **优化 LLM 使用**
   - 批量处理
   - 混合模型
   - 结果缓存

4. **建立降级策略**
   - 多数据源备份
   - 模拟数据兜底
   - 错误恢复机制

### 10.2 优先级排序

**P0 (必须):**
- ✅ 单 Agent ReAct 架构
- ✅ 3 个核心工具
- ✅ 简化评分公式
- ✅ CLI 界面

**P1 (重要):**
- ⏸️ Graph 架构升级
- ⏸️ 真实数据集成
- ⏸️ 错误处理和降级

**P2 (可选):**
- ⏸️ 前端界面
- ⏸️ 历史记录
- ⏸️ 高级分析

### 10.3 成功指标

**MVP 阶段:**
- ✅ 能够验证 1 个项目的承诺
- ✅ 生成鸽王指数和评级
- ✅ 提供详细的评分理由
- ✅ 总耗时 < 30 秒

**生产阶段:**
- ✅ 支持真实 Twitter 和链上数据
- ✅ 评分准确率 > 80%
- ✅ 前端可视化展示
- ✅ 支持批量验证

---

## 十一、下一步行动

### 11.1 立即行动

1. **与团队讨论 MVP 范围**
   - 确认单 Agent 架构
   - 确认模拟数据策略
   - 确认开发时间表

2. **准备开发环境**
   - 安装 SpoonOS 依赖
   - 配置 LLM API Key
   - 准备测试数据

3. **开始 MVP 开发**
   - 参考 spoon-awesome-skill 示例代码
   - 实现核心 Agent 和工具
   - 编写单元测试

### 11.2 后续行动

4. **MVP 测试和优化**
   - 端到端测试
   - 性能优化
   - 用户反馈

5. **生产版本规划**
   - 根据 MVP 反馈调整架构
   - 集成真实数据源
   - 开发前端界面

---

## 附录

### A. 关键文件路径

**需求文档:**
- `/home/ssszyy/code/web3/hackason-project/docs/REQUIREMENTS_V1.md`

**SpoonOS 技能库:**
- `/home/ssszyy/code/web3/hackason-project/spoon-awesome-skill/spoonos-skills/`

**示例代码:**
- Agent: `spoonos-skills/agent-development/scripts/basic_agent.py`
- Graph: `spoonos-skills/graph-development/scripts/basic_graph.py`
- Tool: `spoonos-skills/tool-development/scripts/base_tool.py`

**配置文件:**
- `.env` - 环境变量
- `requirements.txt` - Python 依赖

### B. 参考资源

**SpoonOS 文档:**
- Agent 开发: `spoonos-skills/agent-development/README.md`
- Graph 开发: `spoonos-skills/graph-development/README.md`
- Tool 开发: `spoonos-skills/tool-development/README.md`

**Web3 工具:**
- 73 个可用脚本在 `.agent/skills/` 目录

---

**审阅完成时间**: 2026-01-28
**建议优先级**: 高
**预计 MVP 开发时间**: 4-6 天
**预计生产版本时间**: 2-3 周
