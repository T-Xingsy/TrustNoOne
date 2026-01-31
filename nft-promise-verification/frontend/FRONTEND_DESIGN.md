# 画饼粉碎机 - 前端设计文档

## 设计概念

**视觉风格**: Matrix Terminal × Crypto Audit

```
关键词: 黑绿、终端、数据流、代码、安全检测
灵感来源: 黑客帝国、代码雨、区块链浏览器、安全审计终端
```

---

## 配色方案 (黑绿主题)

```css
/* ========== 黑绿配色系统 ========== */

/* 背景系 - 纯黑/深黑 */
--color-bg: #000000              /* 纯黑主背景 */
--color-bg-secondary: #0a0f0a    /* 淡黑次级背景 */
--color-bg-tertiary: #111a11      /* 卡片背景 */
--color-bg-elevated: #1a2a1a      /* 悬浮卡片背景 */

/* 边框系 */
--color-border: #1a3a1a           /* 深绿边框 */
--color-border-bright: #2d5a2d    /* 亮绿边框 */
--color-border-glow: #3d7a3d      /* 发光边框 */

/* 主色调 - 荧光绿阶梯 */
--color-primary: #00ff41          /* 主荧光绿 (Matrix绿) */
--color-primary-dim: #00cc33      /* 暗荧光绿 */
--color-primary-glow: rgba(0, 255, 65, 0.3)  /* 绿色光晕 */
--color-primary-subtle: rgba(0, 255, 65, 0.1)  /* 淡绿背景 */

/* 辅助色 - 蓝绿/青色 */
--color-accent: #00ff88           /* 青绿色 (链接/按钮) */
--color-accent-glow: rgba(0, 255, 136, 0.3)

/* 状态颜色 - 基于绿色明度 */
--color-danger: #cc3333           /* 高风险 - 红 (保留少量红色警告) */
--color-danger-glow: rgba(204, 51, 51, 0.3)
--color-warning: #ccaa33          /* 中风险 - 橙黄 */
--color-warning-glow: rgba(204, 170, 51, 0.3)
--color-success: #00ff41          /* 低风险/已兑现 - 荧光绿 */
--color-success-glow: rgba(0, 255, 65, 0.3)
--color-info: #00ff88             /* 信息 - 青绿 */
--color-info-glow: rgba(0, 255, 136, 0.3)

/* 文字颜色 */
--color-text-primary: #00ff41     /* 主文字 - 荧光绿 */
--color-text-secondary: #4a8a4a   /* 次要文字 - 暗绿 */
--color-text-tertiary: #2a5a2a    /* 弱化文字 */
--color-text-muted: #1a3a1a       /* 静音文字 */

/* 画饼指数渐变 - 绿→黄→红 */
--gradient-low: #00ff41           /* 低分 - 绿 */
--gradient-mid: #ccaa33           /* 中分 - 黄 */
--gradient-high: #cc3333          /* 高分 - 红 */
```

---

## 配色示例

```
┌─────────────────────────────────────────────────────────┐
│  颜色用途表                                            │
├─────────────────────────────────────────────────────────┤
│  #000000  背景 (纯黑)                                   │
│  #0a0f0a  次级背景                                      │
│  #1a3a1a  边框                                          │
│  #2d5a2d  亮边框                                        │
│  #00ff41  主绿 (文字、高亮、成功)                        │
│  #00cc33  暗绿 (次要文字)                               │
│  #00ff88  青绿 (链接、按钮)                             │
│  #4a8a4a  次级文字                                      │
│  #2a5a2a  弱化文字                                      │
│  #cc3333  危险/高风险                                    │
│  #ccaa33  警告/中风险                                    │
└─────────────────────────────────────────────────────────┘
```

---

## 字体系统

```
显示字体: Orbitron (几何感、科技感)
        - 用于标题、数字、画饼指数
        - 字重: 700/900

正文字体: JetBrains Mono (等宽、代码感)
        - 用于正文、数据、标签
        - 字重: 400/700

等宽数字: 'Orbitron' 或 'Share Tech Mono'
         - 用于画饼指数大数字
```

---

## 视觉特效 (黑绿主题)

### 背景效果
- **代码雨效果** - 绿色字符下落动画 (可选)
- **网格线背景** - 淡绿色网格 (50px)
- **扫描线** - 水平绿色扫描线

### 发光效果
- 主色调发光: `box-shadow: 0 0 20px rgba(0, 255, 65, 0.5)`
- 文字发光: `text-shadow: 0 0 10px rgba(0, 255, 65, 0.8)`
- 边框发光: `box-shadow: 0 0 15px rgba(0, 255, 65, 0.4), inset 0 0 15px rgba(0, 255, 65, 0.1)`

### 动画效果
- 闪烁光标: `_` 1秒闪烁
- 脉冲发光: 2秒呼吸效果
- 打字机效果: 文字逐个出现
- 数据流: 绿色块从右向左移动

---

## 页面结构

### 1. Landing 页面 (`index.html`)

```
┌─────────────────────────────────────────────────────────┐
│  █ 画饼粉碎机      已验证: 247    平均指数: 67    ●在线 │
├─────────────────────────────────────────────────────────┤
│                                                         │
│   > 撕碎 NFT 项目的虚假承诺                             │
│   > 用数据说话                                          │
│                                                         │
│   AI 驱动的 NFT 项目可信度评估系统                      │
│                                                         │
├─────────────────────────────────────────────────────────┤
│  █ 搜索项目...                           [验证项目]     │
│                                                         │
│  [Azuki] [BAYC] [Doodles] [Pudgy]                      │
├─────────────────────────────────────────────────────────┤
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐  │
│  │ █ Azuki      │ │ █ Moonbirds  │ │ █ Pudgy...   │  │
│  │              │ │              │ │              │  │
│  │      78     │ │      54      │ │      23      │  │
│  │   高风险     │ │   中风险     │ │   低风险     │  │
│  └──────────────┘ └──────────────┘ └──────────────┘  │
└─────────────────────────────────────────────────────────┘
```

### 2. 项目详情页 (`project-detail.html`)

```
┌─────────────────────────────────────────────────────────┐
│  ← 返回                                                 │
├─────────────────────────────────────────────────────────┤
│  █ 高画饼风险                                           │
│                                                         │
│  Azuki                                                 │
│  @AzukiEN · azuki.com · 0xed5af...                      │
│                                            ┌──────────┐ │
│                                            │          │ │
│                                            │    78    │ │
│                                            │ 严重画饼 │ │
│                                            │          │ │
│                                            └──────────┘ │
├─────────────────────────────────────────────────────────┤
│  ╔═════════════════════════════════════════════════════╗│
│  ║ 五维雷达图                                          ║│
│  ║     诚信                                            ║│
│  ║        ▲    公平                                    ║│
│  ║       ║╱                                           ║│
│  ║  开发 ╱  财务                                      ║│
│  ║       ╲                                            ║│
│  ║        ▼    动能                                    ║│
│  ╚═════════════════════════════════════════════════════╝│
├─────────────────────────────────────────────────────────┤
│  [全部] [✅已兑现] [❌未兑现] [❓无法验证]               │
│                                                         │
│  █ ❌ "将在2024 Q1空投10000个BEANZ"                     │
│    来源: Twitter | 查看推文 →                           │
│                                                         │
│  █ ✅ "Elementals将于夏季发布"                           │
│    来源: Twitter | 查看推文 →                           │
└─────────────────────────────────────────────────────────┘
```

### 3. 验证进度页 (`verification-progress.html`)

```
┌─────────────────────────────────────────────────────────┐
│  > 正在验证项目                                         │
│  > 项目: Azuki                                          │
│                                                         │
│  ████████████████████████████░░░░░  65%                │
│  > 链上验证中...                                        │
│                                                         │
│  █ ①✓ 收集承诺                                         │
│    从 Twitter、官网抓取项目公开承诺                      │
│    已找到 127 条推文                                     │
│                                                         │
│  ▶ ②➊ 链上验证 (当前)                                  │
│    查询区块链数据验证承诺兑现情况                         │
│    分析锁定事件...                                       │
│                                                         │
│  ○ ③  五维评分                                         │
│  ○ ④  生成报告                                         │
│                                                         │
│  > AI 思考过程                                          │
│  > 正在抓取 @AzukiEN 的推文...                          │
│  > 国库地址: 0x7E1F...3A2F                              │
│  > 当前余额: 127 ETH                                    │
│  > _                                                    │
│                                                         │
│  [取消验证]                                             │
└─────────────────────────────────────────────────────────┘
```

---

## 组件样式规范

### 按钮
```css
/* 主按钮 - 荧光绿 */
.btn-primary {
    background: #00ff41;
    color: #000000;
    border: 2px solid #00ff41;
    box-shadow: 0 0 20px rgba(0, 255, 65, 0.5);
}

.btn-primary:hover {
    background: #00cc33;
    box-shadow: 0 0 30px rgba(0, 255, 65, 0.8);
}
```

### 输入框
```css
/* 搜索框 */
.search-input {
    background: #0a0f0a;
    border: 2px solid #1a3a1a;
    color: #00ff41;
}

.search-input:focus {
    border-color: #00ff41;
    box-shadow: 0 0 15px rgba(0, 255, 65, 0.3);
}

.search-input::placeholder {
    color: #2a5a2a;
}
```

### 卡片
```css
/* 项目卡片 */
.card {
    background: #111a11;
    border: 2px solid #1a3a1a;
}

.card:hover {
    border-color: #00ff41;
    box-shadow: 0 0 20px rgba(0, 255, 65, 0.3);
}

.card.high-risk {
    border-left: 4px solid #cc3333;
}

.card.low-risk {
    border-left: 4px solid #00ff41;
}
```

### 进度条
```css
/* 进度条 */
.progress-bar {
    background: #1a3a1a;
}

.progress-fill {
    background: linear-gradient(90deg, #00ff41, #00ff88);
    box-shadow: 0 0 10px rgba(0, 255, 65, 0.5);
}
```

---

## 响应式断点

```css
/* Mobile First */
@media (max-width: 768px) {
  .project-header { flex-direction: column; }
  .projects-grid { grid-template-columns: 1fr; }
  .promise-card { grid-template-columns: 1fr; }
  .dimensions-grid { grid-template-columns: 1fr; }
}

/* Tablet */
@media (min-width: 769px) and (max-width: 1024px) {
  .projects-grid { grid-template-columns: repeat(2, 1fr); }
}

/* Desktop */
@media (min-width: 1025px) {
  .projects-grid { grid-template-columns: repeat(4, 1fr); }
}
```

---

## 文件结构

```
frontend/
├── index.html                    # Landing 页面
├── project-detail.html           # 项目详情页
├── verification-progress.html    # 验证进度页
└── FRONTEND_DESIGN.md            # 本文档
```

---

## 设计原则总结

1. **黑绿主导**: 所有颜色基于黑色背景 + 荧光绿文字
2. **数据可视化**: 用绿色明度表示风险程度
3. **终端美学**: 等宽字体、命令行符号、闪烁光标
4. **层次分明**: 用绿色的亮度和饱和度区分层级
5. **品牌一致**: 所有页面共享黑绿配色语言
