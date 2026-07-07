# Gmail求职监控系统

## 架构

```
Cron (每30分钟)
    ↓
gmail_job_agent.py
    ↓
├── 扫描新邮件（7天窗口，himalaya IMAP）
├── 智能分类（读取正文准确识别）
├── 更新 application_tracker.json
├── 重要邮件立即通知（拒绝/面试/猎头）
└── 生成进度报告 → ~/.hermes/job-search/reports/
```

## 快捷命令

```bash
gmail-job scan [days]           # 扫描，默认7天
gmail-job search <keyword>      # 搜索主题/发件人
gmail-job company <name>        # 搜索特定公司
gmail-job report [days]         # 生成进度报告
gmail-job tracker               # 查看进度表JSON
```

## 邮件分类逻辑

| 分类 | 触发条件 | 通知方式 |
|------|----------|----------|
| 🟢 积极 | 面试/录用/shortlisted关键词 | 立即通知 |
| 🔴 拒绝 | 遗憾/未能进入/unfortunately（读取正文） | 立即通知 |
| 🔵 猎头 | recruitment/talent acquisition/headhunt | 立即通知 |
| ⚪ 通知 | 其他求职相关 | 静默记录 |

**关键改进**: 对含"申请/应聘/application"等关键词的邮件，会读取正文进行二次分类，避免漏判拒绝信（如汇丰案例）。

## 邮件驱动的岗位发现流程

从职位推荐邮件中提取岗位的完整流程：

1. **提取LinkedIn ID**: 从邮件正文中用正则提取 `https://www.linkedin.com/com/jobs/view/(\d+)`
2. **抓取JD**: `browser_navigate` 打开LinkedIn页面 → 关闭登录弹窗 → 提取JD内容
3. **9维度评估**: 基于用户画像进行匹配评估
4. **更新追踪表**: 写入 `application_tracker.json`

## 状态文件

- `~/.hermes/job-search/application_tracker.json` — 求职进度表
- `~/.hermes/job-search/gmail_state.json` — 已处理邮件ID（防重复）
- `~/.hermes/job-search/reports/` — 每日进度报告
- `~/.hermes/job-search/README.md` — 系统文档

## 已知限制

1. 正文读取增加延迟（每封需额外himalaya调用）
2. 只扫描INBOX文件夹
3. 历史搜索最多200封
4. 分类依赖关键词匹配，可能有误判

## Cron任务

任务名: Gmail求职监控Agent (job_id: ab847a6ee41e)
频率: every 30m
脚本: `~/.hermes/scripts/gmail_job_agent.py --days 7`
