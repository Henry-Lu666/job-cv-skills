# Cron Prompt 与 Reference 文档同步（元 Pitfall）

> 2026-07-06 教训：Gmail 监控 reference 文档已含中文关键词和标记已读指令，但 cron prompt 未同步更新，导致 ZEEKR 拒绝邮件被遗漏

## 问题描述

`job-cv-apply` skill 的 reference 文档可能正确描述了某个流程，但实际运行的 cron job prompt 却是旧版本。cron 每次执行时读取的是自己 prompt 里的指令，不会自动加载 reference 文档。

## 如何发现不同步

- 用户反馈某个邮件/事件没被捕获
- 或者你手动检查 cron prompt 发现它与 reference 文档有差异

## 已知需要同步的关键 cron

| cron job_id | 名称 | 对应的 reference 文档 |
|-------------|------|----------------------|
| ab847a6ee41e | 求职监控Agent（每60分钟） | gmail-mcp-scan-workflow.md |
| d52930346b30 | 求职-每日响应追踪（09:00） | gmail-mcp-scan-workflow.md |

## 修复流程

1. 用 `cronjob(action='list')` 查看 cron prompt
2. 对比对应 reference 文档，找出差异
3. 用 `cronjob(action='update', job_id='xxx', prompt='...')` 更新 prompt
4. 关键检查项：Gmail 搜索关键词（必须含中文"申请""拒绝""退回"）、处理后标记已读、输出格式

## 触发条件

每次更新以下 reference 文档时，必须检查对应的 cron prompt：
- `gmail-mcp-scan-workflow.md` → 检查求职监控类 cron
- `gmail-job-scan-workflow.md` → 检查邮箱岗位日报类 cron
- `163-email-imap-setup.md` → 新增 163 IMAP 脚本后需创建对应 cron
