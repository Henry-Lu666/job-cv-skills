# 求职全链路自动化 · Skills 套件 v2.0

一条流水线跑完求职全流程：从扫邮箱到模拟面试。

## 架构总览

### 6大技能模块

| Skill | 定位 | 大小 | 功能 |
|-------|------|------|------|
| `job-core` | 📌 基准 | 核心规则 | 红线铁律、甜蜜区定位、双视角决策框架 |
| `job-pipeline` | 🔄 管线 | 流程骨架 | Stage 0-5全流程定义、平台限制清单、关键教训 |
| `job-cdp` | 📡 监控 | 自动化扫描 | Gmail+CDP多平台通知监控、OAuth管理 |
| `job-interview` | 🎯 面试 | 面试准备 | SMART痛点逆向工程、STAR故事、薪资谈判、PPT生成、咖啡会面策略 |
| `jd-inspector` | 🛠 工具 | JD审查 | 门槛审查、坑点扫描、9维度评分 |
| `interview-simulation` | 🎭 模拟 | 面试模拟 | 五步循环+STAR反馈+七轮递进+四种面试官类型 |

> 旧版 `job-cv-apply` 单体skill（v1.0）已拆分为以上6个正交模块。每个可独立使用，也可组合成完整求职流水线。

### 其他模块

| Skill | 功能 |
|-------|------|
| `personality-receipt` | 人格小票—上传聊天记录生成AI专属使用说明书 |

---

## 快速开始

```bash
# 将对应skill目录复制到Hermes skills目录
cp -r skills/job-core ~/.hermes/skills/productivity/
cp -r skills/job-pipeline ~/.hermes/skills/productivity/
cp -r skills/job-cdp ~/.hermes/skills/productivity/
cp -r skills/job-interview ~/.hermes/skills/productivity/
cp -r skills/jd-inspector ~/.hermes/skills/productivity/
cp -r skills/interview-simulation ~/.hermes/skills/productivity/
```

---

## 前置准备

### 1. Gmail授权
在 Google Cloud Console 创建项目 → 启用 Gmail API → 配置 OAuth 2.0 凭据 → 配置 Gmail MCP。

### 2. Chrome CDP设置
- 创建专用 Chrome 配置文件
- 以 `--remote-debugging-port=9222` 启动
- 登录求职站点，保存密码到书签文件夹
- 配置 `browser.cdp_url` 为 `http://localhost:9222`

### 3. 简历与知识库路径
在Hermes配置中设置你的简历路径：
```yaml
resume_path: "your-resume-path/your-resume.docx"
resume_v4_path: "your-resume-path/your-resume-v4.docx"
knowledge_base: "your-kb-path/"
chrome_debug_port: 9222
```

---

## 工作流程

### 日常巡检（"走一遍"）

```
Stage 0: 时间校准 → date确认
Stage 1: Gmail+CDP扫描 → 发现新岗位
Stage 2: JD提取 → 门槛审查 → 9维度评估
Stage 3: 简历定制 → 生成定制版→ 用户确认→ 投递
Stage 4: 追踪表更新 → 投后追踪
Stage 5: 汇总报告 → 决策清单
```

### 面试全链路准备

```
公司深度调研（多Agent并行调研 + 5角色对抗验证）
  → SMART痛点逆向工程（从JD反推公司痛点×你的经验）
  → 多AI交叉迭代（至少2轮独立AI对照验证）
  → PPT设计大纲 → ppt-master自动生成面试PPT
  → 多轮面试模拟（interview-simulation）
  → 修正锚点卡 + 画句号清单
```

其中ppt-master支持自动提取公司官网品牌色、双版本交付（暖色+降级白）、演讲稿自动生成。

---

## 方法论亮点

**SMART痛点逆向工程** — 从JD反推公司痛点，用你的经历证明能解决。
**STORM 5角色对抗分析** — 学者/历史学家/实践者/经济学家/怀疑者，5视角3组对抗→观点对撞→输出修正清单。覆盖文档审计、面试叙事验证、公司调研结论交叉验证。
**双视角决策法** — 实践者视角（落地执行）+ 经济学家视角（资源配置），双视角交叉验证。
**9维度评估** — 核心三维（行业+职能+技能）满9分，综合20分，量化匹配度。
**七轮递进模拟** — 面试官心理变化路径：从"考你"到"跟你一起想"。
**渠道杠杆原则** — 内推权重≥匹配度分数，评估时综合考虑。
**调研→PPT→模拟全链路** — deep-research多Agent调研 + STORM 5角色验证 → SMART痛点 → ppt-master生成PPT → interview-simulation多轮模拟，一站式前置准备。

---

## License

MIT
