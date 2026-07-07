# Gmail 求职邮件扫描工作流

> **⚠️ 2026-06-22 更新**: 此文档描述的旧脚本 `gmail_job_scanner.py` 已被 `gmail_job_agent.py` 替代。
> 新Agent详见 `references/gmail-monitoring-agent.md`。
> 快捷命令: `gmail-job scan` / `gmail-job search 汇丰` / `gmail-job report`

> 通过 Himalaya CLI 读取 Gmail 中的 LinkedIn/JobsDB 推荐邮件，自动提取岗位并匹配评分。

## 前置条件

- Himalaya CLI 已安装 (`~/.local/bin/himalaya --version`)
- Gmail 已配置 (`~/.config/himalaya/config.toml`，App Password 认证)
- **推荐脚本**: `~/.hermes/scripts/gmail_job_agent.py`（新Agent）
- 旧脚本: `~/.hermes/scripts/gmail_job_scanner.py`（已废弃，保留不删）

## 邮件来源识别

| 发件人地址 | 平台 | 邮件类型 | 解析器 |
|-----------|------|---------|--------|
| jobalerts-noreply@linkedin.com | LinkedIn | 职位订阅摘要（多岗位digest） | parse_linkedin_subscription |
| jobs-noreply@linkedin.com | LinkedIn | 保存职位提醒（"立即申请"） | parse_linkedin_reminder |
| noreply@e.jobsdb.com | JobsDB | 每日推荐（"N new jobs"主题） | parse_jobsdb_recommendations |
| messages-noreply@linkedin.com | LinkedIn | 连接请求/消息（跳过） | — |
| noreply@research.jobsdb.com | JobsDB | 调查问卷（跳过） | — |

## 邮件格式解析要点

### LinkedIn 职位订阅（领英职位订阅）

- 主题: `公司名+岗位名`（如"汇丰Senior AI Solution Lead"）
- 正文: 用 `-{20,}` 分隔线分割各岗位块
- 每块结构: 岗位名 → 公司名 → 地点 → "查看职位: URL"
- LinkedIn Job ID 提取: `/jobs/view/(\d+)`
- 需过滤的噪音行: "职位订阅", "管理职位订阅", "编辑订阅", "其他订阅", "查看领英", "<strong", "Subject:", "To:", "From:"

### LinkedIn 保存职位提醒（领英）

- 主题: `你的名字，立即申请"XXX的YYY岗位"`
- 正文: 主岗位 + "其他已保存的职位" 区块
- 每个岗位: 标题 → 公司 → 地点 → "查看职位: URL"

### JobsDB 推荐邮件

- 主题: `岗位名 + N new jobs`
- 正文: 每个岗位用空行分隔，结构: 标题 → 公司 → 地点 → 薪资 → 描述要点
- URL 格式: `https://url.jobsdb.com/ss/c/...`（跟踪链接，非直链）
- 需过滤的噪音: "View more jobs", "Rate your recent employer", "apple store", "google play", "Edit frequency", "View job recommendations"

## 执行命令

### 新Agent（推荐）

```bash
# 扫描最近7天（默认）
gmail-job scan

# 扫描最近30天
gmail-job scan 30

# 搜索特定公司
gmail-job search 汇丰
gmail-job company HSBC

# 生成进度报告
gmail-job report

# 查看求职进度表
gmail-job tracker
```

### 旧脚本（已废弃，保留兼容）

```bash
# 基本扫描（最近7天）
python3 ~/.hermes/scripts/gmail_job_scanner.py --days 7 --output text

# 保存报告到知识库
python3 ~/.hermes/scripts/gmail_job_scanner.py --days 7 --output text --save

# JSON 输出（供下游处理）
python3 ~/.hermes/scripts/gmail_job_scanner.py --days 7 --output json
```

输出路径: `~/你的知识库路径/raw/notes/jobs/YYYY-MM-DD-email-jobs.md`

## ⚠️ 脚本超时时的回退方案

`gmail_job_scanner.py` 可能因网络/API问题超时(60s+)。此时用 himalaya CLI 直接搜索：

```bash
# 1. 列出最近邮件（JSON）
~/.local/bin/himalaya envelope list --folder INBOX --page-size 100 --output json

# 2. Python过滤求职相关邮件（见 references/himalaya-email-commands.md）
# 3. 读取特定邮件: ~/.local/bin/himalaya message read <ID>
```

**关键**: 即使脚本超时，也不能跳过邮箱检查。himalaya直接读取是可靠的回退路径。
详见 `references/himalaya-email-commands.md`。

## 评分逻辑

- high 关键词匹配: +3 分/个 (AI, product manager, digital transformation, operations manager, business development, NLP, etc.)
- medium 关键词匹配: +1 分/个 (strategy, director, consultant, key account, automotive, IoT, etc.)
- exclude 关键词命中: 直接 EXCLUDED (insurance agent, trainee, intern, L&D, etc.)
- 分档: ≥6 ★★★★★强推 / ≥4 ★★★★值得投 / ≥2 ★★★可考虑 / ≥1 ★★观望 / 0 ★低匹配

## Pitfall

1. **himalaya JSON 输出混有 WARN 行** — 用 `raw.find('[')` 提取 JSON 数组起始位置再解析
2. **himalaya `from` 字段是 dict** — `{"name": "领英", "addr": "jobalerts-noreply@linkedin.com"}`，不能当 string 用
3. **himalaya 搜索语法是小写 IMAP 风格** — `from "linkedin"` 不是 `from:linkedin.com`（Gmail语法）
4. **JobsDB 邮件 footer 噪音多** — "View more jobs", "Rate your recent employer", "apple store" 等会被误解析为岗位，必须在 parse_jobsdb_recommendations 中过滤
5. **LinkedIn 邮件中 `<strong class="...">` 标签** — HTML 残留会混入解析结果，需过滤以 `<strong` 开头的行
6. **同一岗位可能出现在多封邮件中** — 必须按 job_id 或 (title, company) 元组去重