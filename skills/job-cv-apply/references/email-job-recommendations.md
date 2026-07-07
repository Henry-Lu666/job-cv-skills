# 邮件职位推荐提取与核实流程

> 2026-06-22 建立。从Gmail职位推荐邮件中提取岗位、评估、推荐的标准流程。

## 为什么需要这个流程

邮件推荐的岗位容易被误认为"已匹配"——标题看起来高度匹配（如"Operations Manager"、"AI Transformation"），但实际上只是邮件标题的关键词命中，不是JD匹配。

**2026-06-22教训**：从LinkedIn/Glassdoor/JobsDB推荐邮件中提取了42个岗位，按关键词排序后直接标注"重点推荐"。用户追问"都抓过JD了吗？"答案是没有。

## 数据源

| 来源 | 邮件特征 | 岗位提取方式 |
|------|----------|-------------|
| LinkedIn职位推荐 | 发件人: 领英/LinkedIn | "XX正在招聘YY" 或 职位订阅列表 |
| LinkedIn职位订阅 | 发件人: 领英职位订阅 | 邮件正文中的岗位列表+链接 |
| Glassdoor推荐 | 发件人: Glassdoor Jobs | "XX is hiring for YY. Apply Now." |
| Indeed推荐 | 发件人: Indeed | "YY @ XX" 格式 |
| JobsDB推荐 | 发件人: Jobsdb | 主题中的岗位名称 |
| CTgoodjobs | 发件人: CTgoodjobs | 主题中的岗位名称（混杂资讯） |

## 正确流程

```
Step 1: 提取岗位
  └── himalaya envelope list → 过滤求职相关 → 提取公司/岗位/日期/来源

Step 2: L1关键词初筛
  └── 按岗位标题关键词评分（score_job函数）
  └── 分类：高匹配(>=3) / 中等(0-2) / 低匹配(<0)
  └── ⚠️ 这只是粗筛，不能用于推荐

Step 3: 抓取完整JD ← 必须执行，不能跳过
  └── 从邮件中提取LinkedIn链接
  └── browser_navigate → 关弹窗 → browser_snapshot(full=true)
  └── 如果LinkedIn不可用，尝试JobsDB API或其他渠道

Step 4: 9维度匹配评估
  └── 基于完整JD进行评估
  └── 核心三维(行业+职能+技能) vs 辅助维度
  └── 输出：核心三维分数 + 综合分 + 结论

Step 5: 汇总呈现
  └── 已核实的岗位：带匹配度和结论
  └── 未核实的岗位：标"⚠️L1未核实"
  └── 已下架的岗位：标"❌已下架"
```

## 邮件中LinkedIn链接提取

LinkedIn职位订阅邮件包含完整链接，格式：
```
查看职位: https://www.linkedin.com/comm/jobs/view/{JOB_ID}/?trackingId=...
```

提取命令：
```bash
~/.local/bin/himalaya message read <ID> 2>&1 | grep -oP 'https://www\.linkedin\.com/comm/jobs/view/\d+'
```

LinkedIn Job ID 是URL中的数字部分（如 `4428817624`）。

## 实测案例（2026-06-22）

### 从邮件提取的4个岗位评估结果

| 岗位 | 公司 | 匹配度 | 结论 | 关键发现 |
|------|------|--------|------|---------|
| APAC Senior Regional Operations Manager | Uber | 85% | ✅建议投递 | SQL是must-have |
| Head of Corporate Strategy | Insurance Group | N/A | ❌已下架 | 岗位已失效 |
| AD/Senior Manager Business Transformation | Manulife | 67% | ⚠️观望 | 需支付领域专业知识 |
| Delivery Manager AI & Digital Transformation | Argyll Scott | 81% | ✅强推 | AI背景直接匹配，薪资95K |

### 关键发现
- 42个邮件推荐岗位中，只有13个高匹配（L1）
- 13个高匹配中，实际抓JD评估了4个
- 1个已下架，1个观望，2个建议投递
- **L1→L2的转化率约50%**（2/4建议投递）

## Pitfall

1. **邮件标题的岗位名称可能不完整** — LinkedIn订阅邮件的主题是搜索词+第一个岗位，不是完整列表。必须读取正文才能看到所有推荐岗位。

2. **LinkedIn链接可能过期** — 邮件中的tracking链接有时会失效。直接用Job ID访问 `https://www.linkedin.com/jobs/view/{ID}` 更可靠。

3. **Glassdoor/Indeed推荐重复率高** — 同一个岗位可能连续几天出现在推荐中。用(公司, 岗位)元组去重。

4. **CTgoodjobs邮件混杂资讯** — 很多邮件是"求职技巧"、"政府工推荐"等资讯，不是个性化岗位推荐。需过滤。

5. **岗位已下架不等于之前有误** — LinkedIn岗位随时可能关闭。邮件是历史快照，打开时可能已失效。标注"已下架"即可，不要质疑邮件数据的准确性。
