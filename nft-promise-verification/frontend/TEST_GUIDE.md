# 前端 URL 参数修复 - 测试指南

## 📋 修改概述

已将项目名称传递方式从 `sessionStorage` 改为 **URL 参数**，解决了"无论验证哪个项目都跳转到 Azuki"的问题。

## 🔧 修改的文件

1. **index.html** - 4处修改
2. **verification-progress.html** - 2处修改
3. **project-detail.html** - 1处修改

---

## ✅ 测试场景

### **场景1：验证已存在的项目**

**步骤**：
1. 打开 `index.html`
2. 在搜索框输入 "Moonbirds"
3. 点击"验证项目"按钮

**预期结果**：
- ✅ 跳转到 `project-detail.html?project=Moonbirds`
- ✅ 显示 Moonbirds 项目的详情
- ✅ URL 中包含 `?project=Moonbirds`

---

### **场景2：验证新项目**

**步骤**：
1. 打开 `index.html`
2. 在搜索框输入 "TestProject"（不存在的项目）
3. 点击"验证项目"按钮

**预期结果**：
- ✅ 跳转到 `verification-progress.html?project=TestProject`
- ✅ 验证进度页面显示 "TestProject"
- ✅ 验证完成后跳转到 `project-detail.html?project=TestProject`

---

### **场景3：点击项目卡片**

**步骤**：
1. 打开 `index.html`
2. 点击首页上的任意项目卡片（例如 Azuki）

**预期结果**：
- ✅ 跳转到 `project-detail.html?project=Azuki`
- ✅ 显示 Azuki 项目的详情

---

### **场景4：使用搜索下拉列表**

**步骤**：
1. 打开 `index.html`
2. 在搜索框输入 "Moon"
3. 从下拉列表中点击 "Moonbirds"

**预期结果**：
- ✅ 跳转到 `project-detail.html?project=Moonbirds`
- ✅ 显示 Moonbirds 项目的详情

---

### **场景5：刷新验证进度页面**

**步骤**：
1. 开始验证任意项目（例如 "Moonbirds"）
2. 在验证进度页面（`verification-progress.html?project=Moonbirds`）按 F5 刷新

**预期结果**：
- ✅ 页面刷新后仍然显示 "Moonbirds"
- ✅ 不会跳转到 Azuki
- ✅ URL 参数保持不变

---

### **场景6：刷新项目详情页面**

**步骤**：
1. 打开任意项目详情页（例如 `project-detail.html?project=Moonbirds`）
2. 按 F5 刷新页面

**预期结果**：
- ✅ 页面刷新后仍然显示 Moonbirds 的详情
- ✅ 不会跳转到 Azuki
- ✅ URL 参数保持不变

---

### **场景7：直接访问项目详情页**

**步骤**：
1. 在浏览器地址栏直接输入：`project-detail.html?project=Pudgy%20Penguins`
2. 按回车

**预期结果**：
- ✅ 显示 Pudgy Penguins 项目的详情
- ✅ 不需要经过首页

---

### **场景8：分享项目链接**

**步骤**：
1. 复制项目详情页的 URL（例如 `project-detail.html?project=Moonbirds`）
2. 在新标签页中打开这个 URL

**预期结果**：
- ✅ 直接显示 Moonbirds 项目的详情
- ✅ 不需要重新验证

---

### **场景9：错误处理 - 无参数访问**

**步骤**：
1. 直接访问 `verification-progress.html`（不带参数）

**预期结果**：
- ✅ 弹出提示："验证会话已过期，请返回首页重新验证"
- ✅ 自动跳转回 `index.html`

---

### **场景10：错误处理 - 项目详情页无参数**

**步骤**：
1. 直接访问 `project-detail.html`（不带参数）

**预期结果**：
- ✅ 弹出提示："项目信息丢失，请返回首页重新选择"
- ✅ 自动跳转回 `index.html`

---

## 🐛 已知问题检查

### **问题1：中文项目名称编码**

**测试**：验证包含中文的项目名称
- URL 应该正确编码（例如 `%E4%B8%AD%E6%96%87`）
- 页面应该正确解码并显示中文

### **问题2：特殊字符处理**

**测试**：验证包含特殊字符的项目名称（例如 `Project & Test`）
- URL 应该正确编码（例如 `Project%20%26%20Test`）
- 页面应该正确解码并显示

---

## 📊 测试结果记录

| 场景 | 状态 | 备注 |
|------|------|------|
| 场景1：验证已存在的项目 | ⬜ 待测试 | |
| 场景2：验证新项目 | ⬜ 待测试 | |
| 场景3：点击项目卡片 | ⬜ 待测试 | |
| 场景4：使用搜索下拉列表 | ⬜ 待测试 | |
| 场景5：刷新验证进度页面 | ⬜ 待测试 | |
| 场景6：刷新项目详情页面 | ⬜ 待测试 | |
| 场景7：直接访问项目详情页 | ⬜ 待测试 | |
| 场景8：分享项目链接 | ⬜ 待测试 | |
| 场景9：错误处理 - 无参数访问 | ⬜ 待测试 | |
| 场景10：错误处理 - 项目详情页无参数 | ⬜ 待测试 | |

---

## 🚀 快速测试命令

如果您使用本地服务器（例如 Python 的 http.server），可以使用以下命令：

```bash
# 进入前端目录
cd /home/ssszyy/code/web3/hackason-project/nft-promise-verification/frontend

# 启动本地服务器
python3 -m http.server 8000

# 然后在浏览器中访问：
# http://localhost:8000/index.html
```

---

## 📝 测试完成后

如果所有测试通过，请：
1. ✅ 标记所有场景为"通过"
2. ✅ 提交代码到 Git
3. ✅ 更新项目文档

如果发现问题，请记录：
- 问题描述
- 复现步骤
- 预期结果 vs 实际结果
- 浏览器版本和环境信息
