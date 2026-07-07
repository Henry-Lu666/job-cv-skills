# Gmail Job Scanner — Technical Reference

## Architecture (2026-06-18 更新 — 6平台覆盖)

```
Gmail (IMAP) → himalaya CLI → gmail_job_scanner.py → structured report
         ↓                                        → desktop report (~/job-search/inbox/)
  LinkedIn / JobsDB /                              → archive (raw/notes/jobs/)
  OfferToday / Indeed /
  Glassdoor / CTgoodjobs 邮件解析
         +
  JobsDB API 关键词搜索
  (8组方向关键词 × 15条)
```

Scanner覆盖6个邮件源 + 1个API源。详见 `references/gmail-job-scanner.md` 邮件发送者速查表。

## Himalaya Setup

### Installation
```bash
curl -sSL https://raw.githubusercontent.com/pimalaya/himalaya/master/install.sh | PREFIX=~/.local sh
```

### Gmail App Password Config
- File: `~/.config/himalaya/config.toml`
- Password file: `~/.config/himalaya/gmail-app-password` (chmod 600)
- **Prerequisite**: 2FA must be enabled on Google account FIRST
- Without 2FA: App Passwords page shows "您的账号不支持您正在尝试的设置"

### Config template
```toml
[accounts.personal]
email = "user@gmail.com"
display-name = "Name"
default = true

backend.type = "imap"
backend.host = "imap.gmail.com"
backend.port = 993
backend.encryption.type = "tls"
backend.login = "user@gmail.com"
backend.auth.type = "password"
backend.auth.cmd = "cat ~/.config/himalaya/gmail-app-password"

message.send.backend.type = "smtp"
message.send.backend.host = "smtp.gmail.com"
message.send.backend.port = 587
message.send.backend.encryption.type = "start-tls"
message.send.backend.login = "user@gmail.com"
message.send.backend.auth.type = "password"
message.send.backend.auth.cmd = "cat ~/.config/himalaya/gmail-app-password"

# Gmail folder aliases (REQUIRED for v1.2.0+)
folder.aliases.inbox = "INBOX"
folder.aliases.sent = "[Gmail]/Sent Mail"
folder.aliases.drafts = "[Gmail]/Drafts"
folder.aliases.trash = "[Gmail]/Trash"
```

## Pitfalls

### P1: himalaya search syntax is NOT Gmail syntax
- Correct (IMAP lowercase): `from "linkedin"`, `subject "job"`
- Wrong (Gmail): `from:linkedin.com` → parse error
- Combined: `from "linkedin" subject "job"` works but may be flaky; prefer single filter + Python-side filtering

### P2: JSON output has WARN lines mixed in
```python
output = run_himalaya(["envelope", "list", "--output", "json", ...])
start = output.find('[')
data = json.loads(output[start:])  # skip WARN lines
```

### P3: `from` field is dict, not string
```json
{"from": {"name": "领英", "addr": "messages-noreply@linkedin.com"}}
```
Helper:
```python
def get_sender_addr(env):
    frm = env.get("from", "")
    return frm.get("addr", "") if isinstance(frm, dict) else str(frm)
```

### P4: LinkedIn email noise patterns
Must skip in parser: "简单几步，轻松迈向成功", "编辑订阅", "其他订阅", "查看领英", "查看全部职位", "有符合您的搜索偏好", "您已成功订阅", "Subject:", "To:", "From:", "<strong"

### P5: JobsDB email noise patterns
Must skip: "Rate your recent employer", "apple store", "google play", "Edit frequency", "View more jobs", "[https://", lines starting with `* ` (requirement bullets, not company names)

### P6: Hong Kong district names as company
"九龙城区", "中西區", "湾仔区" etc. get misidentified as company names. Post-fix in score_job():
```python
location_names = ["九龙城区", "中西區", "湾仔区", ...]
if job.get("company", "") in location_names:
    job["location"] = job["company"]
    job["company"] = ""
```

### P7: Message IDs are folder-relative
Switching folders invalidates previously listed IDs. Always re-list after folder change.

## Email Format Patterns

### LinkedIn Job Alert Digest (领英职位订阅)
- Sender: `jobalerts-noreply@linkedin.com`
- Body: Multiple jobs separated by `----` lines
- Each block: title, company, location, then "查看职位: URL"
- URL pattern: `https://www.linkedin.com/comm/jobs/view/JOB_ID`

### LinkedIn Saved Job Reminder (立即申请)
- Sender: `jobs-noreply@linkedin.com`
- Subject: "你的名字，立即申请"XXX的YYY岗位""
- Body: Main job + "其他已保存的职位" section with additional jobs

### JobsDB Recommendations
- Sender: `noreply@e.jobsdb.com`
- Subject: "岗位名 + N new jobs"
- Body: Structured listings with title, company, location, salary

### OfferToday (BOSS直聘香港版) — 2026-06-10 新增
- Sender: `offertoday.com` 或 `zhipin` 相关域名
- Subject: 通常含"推荐"关键词
- Body: 岗位链接含 `offertoday.com` 或 `zhipin`
- ⚠️ 推荐质量偏低，容易推保险/理财马甲岗

### Indeed — 2026-06-10 新增
- Sender: `donotreply@match.indeed.com`
- Subject: 含"推荐"或"recommend"或"match"
- Body: `viewjob` 链接

### Glassdoor — 2026-06-18 修复重写
- Sender: `noreply@glassdoor.com`
- **Subject patterns**（旧版只认"推荐/recommend/alert"，全部漏掉）：
  - "X is hiring for Y. Apply Now." — 单岗位
  - "Y at X and N more jobs in Hong Kong for you. Apply Now." — 多岗位digest
  - "Machine Learning Engineer at Maxipro (Asia) and 3 more jobs..."
- **Body format (digest)**：每封邮件含5-13个岗位，格式为：
  ```
  {category}                    {company} {rating★}
  {job_title}                   ← 全小写
  {location}                    ← e.g. "hong kong", "remote"
  {time_posted} ({URL})         ← e.g. "1d (https://glassdoor.com.hk/partner/jobListing.htm?...)"
  ```
- **URL pattern**：`https://www.glassdoor.com.hk/partner/jobListing.htm?...&jobListingId=XXXXX`
- **Noise过滤**（必须跳过）：
  - 主题含 "how is your" / "search going" / "unlimited access" / "we want to know" / "secret to landing" / "one-stop shop" / "expert on" / "terminated" / "got easier"
  - Body中的invisible Unicode characters（U+200B-ZWS, U+200C-ZWNJ, U+200D-ZWJ, U+200E-LRM, U+200F-RLM, U+FEFF-BOM等）会污染company名，必须strip
- **解析函数**：`parse_glassdoor_digest(body, subject)` — 从URL位置向前回溯提取location→title→company
- **已知限制**：company名常被Unicode零宽字符覆盖导致为空，需从URL或title推断

## JobsDB API Keyword Search (Step 4)

Scanner 在邮件解析之后，额外用 JobsDB 搜索 API 做关键词补充搜索（覆盖 CTgoodjobs/劳工处同类岗位）：

```python
# 8组方向关键词
api_keywords = [
    "operations director",
    "business development director",
    "general manager Hong Kong",
    "partnership manager",
    "digital transformation manager",
    "AI product manager",
    "growth manager",
    "marketing director",
]
# 每组搜15条，去重后合并到 all_jobs
# 来源标记为 "JobsDB-API"（区别于邮件中的 "JobsDB"）
```

⚠️ 中文公司名在 JobsDB API 不返回结果，必须用英文名。

## Scoring Logic
- high keywords (AI, product manager, digital transformation, etc.): 3 points each
- medium keywords (strategy, director, operations, etc.): 1 point each
- EXCLUDED: blacklist match (insurance, trainee, assistant, L&D)
- ★★★★★ ≥6, ★★★★ 4-5, ★★★ 2-3, ★★ 1, ★ 0

## Output Locations
- Desktop report: `~/job-search/inbox/Gmail岗位扫货_YYYYMMDD.md` (format matches existing `LinkedIn岗位扫货_*.md`)
- **输出方式**：用 shell 重定向 `> "~/桌面/Gmail岗位扫货_YYYYMMDD.md"`（不用 `--save`，`--save` 只存到知识库 archive）
- stderr 重定向到临时文件查看进度：`2>/tmp/scan_stderr.txt`
- Archive（知识库备份）：`~/你的知识库路径/raw/notes/jobs/YYYY-MM-DD-email-jobs.md`（需 `--save` 参数）
- Tracking table: append new jobs (deduplicated by job ID) to `job-search-2026.md`

### 实际执行命令
```bash
python3 ~/.hermes/scripts/gmail_job_scanner.py --days 7 --output text 2>/tmp/scan_stderr.txt > "~/桌面/Gmail岗位扫货_YYYYMMDD.md"
cat /tmp/scan_stderr.txt  # 查看扫描进度和统计
```

## Cron
- Job ID: `40292eff1879`
- Schedule: daily 10:00
- Delivery: default local (user can update to feishu)
- **Prompt 已更新（2026-06-10）**：包含5步扫描说明，标注新数据源（OfferToday/Indeed/JobsDB-API）

## 邮件发送者速查表（2026-06-10 更新）

| Sender | 平台 | Scanner是否覆盖 |
|--------|------|---------------|
| jobalerts-noreply@linkedin.com | LinkedIn 订阅 | ✅ Step 1 |
| jobs-noreply@linkedin.com | LinkedIn 提醒 | ✅ Step 1 |
| noreply@e.jobsdb.com | JobsDB 推荐 | ✅ Step 2 |
| noreply@email.jobsdb.com | JobsDB 其他 | ✅ Step 2 |
| offertoday.com / zhipin | OfferToday | ✅ Step 3 |
| donotreply@match.indeed.com | Indeed | ✅ Step 3 |
| noreply@glassdoor.com / info@glassdoor.com | Glassdoor | ✅ Step 3 |
| noreply@mail3.ctgoodjobsnews.hk | CTgoodjobs 资讯 | ⚠️ 需过滤（多为营销/资讯） |
| no-reply@ctgoodjobscs.hk | CTgoodjobs 系统 | ❌ 跳过（profile提醒/welcome） |

### P8: CTgoodjobs emails are mostly newsletters (2026-06-18)
CTgoodjobs的邮件主要是营销资讯（定存排行、政府工资讯等），不是个性化职位推荐。即使scanner加了`from "ctgoodjobs"`搜索，也需subject过滤跳过非job邮件。用户需要在ctgoodjobs.hk网站上**主动订阅job alert**才能收到真正的职位推荐邮件。

过滤规则：subject含"定存/排行榜/兼職/月入/打工仔/歡迎/Welcome/檔案尚未完成"或emoji（📢💰⚽😎😍🏆）→ 跳过。

### P9: Scanner timeout when adding email sources (2026-06-18)
添加新邮件源（如Glassdoor 20封）后，逐封读取body可能导致scanner超时（>120s）。解决方案：
- `read_email()` 加 `timeout=10` 参数（默认30s太长）
- 新增源的`page_size`控制在10-20以内
- 如果仍超时，用 `--days 2` 缩小扫描窗口

### P10: Glassdoor digest Unicode pollution (2026-06-18)
Glassdoor digest邮件中company名被invisible Unicode characters（ZWS/ZWNJ/ZWJ/LRM/RLM/BOM等）污染，strip后为空。解决：
```python
text = re.sub(r'[\u200b-\u200f\u202a-\u202e\ufeff\u2060-\u2064\u2066-\u2069]', '', text).strip()
```
如果clean后仍为空，说明company名在HTML中是图片/logo而非文本，只能从URL或title推断。

| noreply@research.jobsdb.com | JobsDB 调研 | ❌ 跳过（非岗位推荐） |
| noreply@mail.apply.careers.hsbc.com | HSBC 投递确认 | ❌ 跳过（非推荐） |