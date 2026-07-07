# Gmail求职监控Agent

> 2026-06-22 部署，替代旧 `job_feedback_scanner.py`
> 最后更新: 2026-06-22

---

## 为什么替换旧脚本

旧脚本 `job_feedback_scanner.py` 只查最近2小时邮件，汇丰拒绝信（6月18日）完全漏掉。新Agent查7天窗口+读正文分类+状态追踪。

## 架构

```
Cron任务(每30分钟)
    ↓
gmail_job_agent.py
    ↓
├── 扫描新邮件(7天窗口)
├── 读取正文进行智能分类
├── 更新进度表
├── 重要邮件立即通知
└── 生成进度报告
```

## 快捷命令

```bash
gmail-job scan          # 扫描最近7天
gmail-job scan 30       # 扫描最近30天
gmail-job search 汇丰    # 搜索特定公司
gmail-job company HSBC  # 搜索特定公司(英文)
gmail-job report        # 生成进度报告
gmail-job tracker       # 查看求职进度表
```

## 核心脚本

- **Agent**: `~/.hermes/scripts/gmail_job_agent.py`
- **快捷命令**: `~/.local/bin/gmail-job`
- **状态文件**: `~/.hermes/job-search/gmail_state.json`
- **进度表**: `~/.hermes/job-search/application_tracker.json`
- **报告**: `~/.hermes/job-search/reports/`

## 分类逻辑

| 分类 | 触发条件 | 通知方式 |
|------|---------|---------|
| 🟢 积极 | 面试/录用关键词 | 立即通知 |
| 🔴 拒绝 | 遗憾/未能进入等 | 立即通知 |
| 🔵 猎头 | recruitment/talent acquisition | 立即通知 |
| ⚪ 通知 | 其他求职相关 | 静默记录 |

## himalaya回退方案

如果Agent脚本超时，直接用himalaya CLI：

```bash
# 列出最近邮件
~/.local/bin/himalaya envelope list --folder INBOX --page-size 100 --output json

# 读取指定邮件
~/.local/bin/himalaya message read <ID>

# 搜索特定公司
~/.local/bin/himalaya envelope list --page-size 200 --output json | python3 -c "
import json, sys
data = json.load(sys.stdin)
for e in data:
    subj = e.get('subject', '') if isinstance(e.get('subject'), str) else ''
    if '关键词' in subj.lower():
        print(f'{e.get(\"id\",\"\")} | {subj[:60]}')
"
```

## Pitfall

1. **from字段是dict不是str** — himalaya JSON中`from`字段格式为`{"name":"...", "addr":"..."}`，拼接时需`str(e.get('from',''))`
2. **正文读取提升分类准确率** — 申请相关邮件（主题含"申请"/"应聘"）需读正文才能准确分类拒绝/积极
3. **进度表≠正式追踪表** — application_tracker.json是辅助文件，正式追踪表是`投递追踪.md`
