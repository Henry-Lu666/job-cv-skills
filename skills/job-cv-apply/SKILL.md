---
name: job-cv-apply
description: 求职全链路自动化流水线 — Gmail扫描→JD抓取→9维匹配→SMART方案→简历定制→Cover Letter→PPT→模拟面试→投递追踪。6阶段管线，含研究/SMART/多AI交叉/PPT/模拟/修正全流程。
author: Henry Lu
version: 1.0.0
license: MIT
platforms: [linux, macos, windows]
---

# 求职辅助 Agent — 全链路自动化

> 一条流水线跑完求职全流程：从扫邮箱到模拟面试。
> 本skill为公开版，个人数据已脱敏。`your-xxx-path` 为占位符。

---

## Pipeline 总览

| 阶段 | 内容 | 技能/参考 |
|------|------|----------|
| 6A | 公司深度调研（并行搜索+核实） | `deep-research` skill |
| 6B | SMART痛点逆向工程（2-3个痛点） | `references/smart-pain-point-framework.md` |
| 6C | 多AI交叉迭代（至少2轮） | `references/multi-ai-feedback.md` |
| 6D | PPT大纲+演讲稿 | `references/research-to-smart-ppt-workflow.md` |
| 6E | PPT多路生成+融合 | 7页，每页≤50字，演讲稿放备注栏 |
| **6F** | **多轮深度模拟（PPT之后！）** | **`interview-simulation` skill + `personality-receipt` skill** |
| **6G** | **修正锚点卡+画句号清单** | 根据模拟暴露的问题修正 |

**⚠️ 顺序铁律：PPT做完才能模拟。**

---

## 场景触发词

```
准备面试 | 模拟面试 | 帮我准备XX公司面试 | 咖啡面 | networking | 
简历 | 改简历 | 投递 | 已投 | 扫邮箱 | 看邮件岗位 | 批量抓JD | 
做匹配 | 出简历 | cover letter | 面试PPT | 痛点分析 | 模拟 | role play
```

---

## 场景14: 面试准备（SMART痛点逆向工程）

### Step 0: 判断会面类型

| 类型 | 策略 |
|------|------|
| 正式面试（有HR/有JD/办公室） | SMART痛点逆向工程 |
| 非正式咖啡会面（咖啡厅/创始人面） | 人物画像+锚点卡 |
| 关键区别 | 正式面试展示能力匹配；咖啡会面让对面放心"这人靠谱" |

### SMART 方案框架

从JD反推公司痛点，每个痛点的方案结构：

| 要素 | 说明 |
|------|------|
| **S**pecific | 具体要做什么，不是"提升效率"而是"建立XX体系" |
| **M**easurable | 可量化指标（"周期缩短30%"、"利润-15%→+8%"） |
| **A**chievable | 基于你的经历证明可做到（引用真实案例） |
| **R**elevant | 直接对齐JD核心诉求 |
| **T**ime-bound | 明确时间线（"90天诊断→6个月落地"） |

每个SMART方案输出面试话术（中英文各一版，30秒可讲完）。

---

## 面试模拟方法论

> 详见独立 skill: `interview-simulation`
> 人格适配: `personality-receipt`

### 五步循环

```
① 设角色 → ② 你回答 → ③ STAR反馈 → ④ 你修正 → ⑤ 判定推进
```

### STAR反馈框架

| 维度 | 考什么 | 10分标准 |
|------|--------|---------|
| **S** 结构完整性 | 有层次还是碎片？ | 三步走/三段式，有时间轴/角色/成本 |
| **T** 真实感 | 有不可编造的细节吗？ | "喝茶""倒数前三"这种做过才有的细节 |
| **A** 直击核心 | 回答表层还是深层焦虑？ | 绕过表面问题答真正需求 |
| **R** 可落地 | 有约束条件吗？ | "3-5家试点""大概一周" |

### 七轮递进模型

| 轮次 | 类型 | 面试官潜台词 | 策略 |
|------|------|-------------|------|
| 1️⃣ | 摸底 | "你从哪里开始？" | 反问而非盲答 |
| 2️⃣ | 选择 | "你怎么做决策？" | 给标准而非选边 |
| 3️⃣ | 专业盲区 | "这行你懂吗？" | **转折点**—承认不懂+说怎么学 |
| 4️⃣ | 工作风格 | "你适合什么角色？" | 清晰的做事节奏 |
| 5️⃣ | 身份质疑 | "你凭什么？" | **高光**—不可编造的细节 |
| 6️⃣ | 方案执行 | "具体怎么做？" | 从"帮你做"到"教你做" |
| 7️⃣ | 边界认知 | "你会吹AI吗？" | 不该用AI的场景比该用更有说服力 |

---

## 前置准备

使用本 skill 前需要完成以下配置：

### Gmail 授权
- 参考 `references/gmail-mcp-setup.md` 完成 OAuth 2.0 授权
- 配置完成后可通过 Gmail MCP 自动扫描求职邮件

### Chrome CDP 设置
- 参考 `references/chrome-cdp-setup-guide.md` 启动调试模式 Chrome
- 用于自动登录求职站点、抓取 JD、检查通知

### 简历与知识库路径
替换 `config.yaml` 中的占位符为你的实际路径：

```yaml
resume_path: "your-resume-path/your-resume.docx"
knowledge_base: "your-kb-path/"
chrome_user_data: "your-chrome-user-data-path/"
chrome_debug_port: 9222
gmail_credentials: "~/.gmail-mcp/credentials.json"

```yaml
# config.yaml — 按需修改
resume_path: "your-resume-path/your-resume.docx"
resume_v4_path: "your-resume-path/your-resume-v4.docx"
knowledge_base: "your-kb-path/"
chrome_user_data: "your-chrome-user-data-path/"
chrome_debug_port: 9222
```

---

## 安装

```bash
# 安装本skill
npx skills add your-username/job-cv-apply

# 依赖skill
npx skills add your-username/interview-simulation
npx skills add your-username/personality-receipt
```

---

## 参考文件

- `references/smart-pain-point-framework.md` — SMART方案模板与痛点模式库
- `references/research-to-smart-ppt-workflow.md` — 研究→PPT全流程
- `references/multi-ai-feedback.md` — 多AI交叉迭代方法论
- `references/star-stories.md` — STAR故事库
- `templates/anchor-card.md` — 锚点卡模板
- `examples/honwell-full-preparation.md` — 完整案例（脱敏版）
