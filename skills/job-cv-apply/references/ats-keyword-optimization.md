# ATS 关键词优化：防 HR/L&D 误判

> 2026-05-27 发现：V2 简历虽做了 AI 前置和结构优化，但保留了「人才发展」「慕课」「内训师」等词，
> 会导致 Jobsdb/猎头 ATS 算法将候选人误判为 HR/L&D 方向，推错岗位。
> 来自多 agent 交叉审核（Claude/Kimi）。

## 核心原则

**不是删掉经历，而是换一个赛道描述同一段经历。**
你做了什么没变，但用什么词描述决定了 ATS 把你归类到哪个职能。

## 高危词 → 安全词对照表

| 高危词（ATS → HR/L&D） | 安全词（ATS → Operations） | 适用场景 |
|------------------------|---------------------------|---------|
| 人才发展 / Talent Development | 全国直营营运负责人 / Head of National Direct-Sales Ops | 职位标题 |
| 培训 / training | 业务落地宣导 / business rollout | 活动描述 |
| 慕课平台 / e-learning platform | 标准化营运 SOP / operational procedures (SOPs) | 体系建设 |
| 内训师体系 / internal trainer system | 一线业务赋能机制 / frontline business enablement | 机制建设 |
| 讲师 / trainer | （删除，不需要这个词） | 角色描述 |
| 学习与发展 / L&D | （删除，不需要这个词） | 职能方向 |

## 实操替换示例

### 原始（V2 第一版，高危）
```
运营及人才发展官（650+ 人团队）
  · 从 0 到 1 搭建直营体系慕课平台及内训师体系，主导 4 次合伙人级大型培训
```

### 优化后（V2 最终版，安全）
```
全国直营营运负责人（兼业务扩张规划）
  · 从 0 到 1 建立直营体系标准化营运 SOP 及一线业务赋能机制，
    主导 4 次合伙人级大型业务落地宣导
```

### English version
```
BEFORE (dangerous): Head of Operations & Talent Development (650+ staff)
  · Built company-wide e-learning platform and internal trainer system
  · Led 4 partner-level training programs

AFTER (safe): Head of National Direct-Sales Operations
  · Established standardized operational procedures (SOPs) and frontline 
    business enablement mechanisms from scratch
  · Led 4 partner-level major business rollouts
```

## ⛔ 白字隐藏关键词（White-text ATS Hack）— 禁止使用

用户曾尝试在简历顶部用白色字体写"符合评价，建议进入下一轮"，企图欺骗ATS。

**为什么无效且有害：**
1. 现代ATS（Workday、SuccessFactors、iCIMS）会检测字体颜色=背景色，直接标记为可疑/扣分
2. 解析时会剥离格式，白字混入正文变成乱码，影响整体解析质量
3. 大企业HR看到标记会直接拒掉（诚信问题）

**正确做法**：把想塞的关键词自然融入正文——在Summary/Experience里用和JD一致的措辞。

## 为什么不能只靠求职目标

ATS 解析简历时会扫描**全文**的关键词密度。求职目标写"业务营运管理"
但工作经历里"培训""人才发展"出现 5 次——算法仍会判定你是 HR 方向。

必须全文清洗，不留一个高危词。

## 与求职定位的一致性

| 简历板块 | 主赛道 | 差异化 |
|---------|--------|--------|
| 求职目标 | 业务营运管理 / 数字化转型 | AI 落地应用 |
| 职位标题 | 全国直营营运负责人 | （纯 Ops，不沾 HR） |
| 工作描述 | SOP / 赋能 / 扩张 / 落地 | 12 年操盘经验 |
| AI 项目 | RoBERTa / 消融实验 / F1 0.67 | 技术深度 |
