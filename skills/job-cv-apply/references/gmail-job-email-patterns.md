# Gmail Job Email Patterns

> Quick reference for parsing LinkedIn and JobsDB job alert emails.
> Full technical details: see `gmail-job-scanner.md`

## LinkedIn 职位订阅 (jobalerts-noreply@linkedin.com)

Subject: "公司名+岗位名" or subscription confirmation
Body structure:
```
[separator line ----]
Job Title Line
Company Name
Location
查看职位: https://www.linkedin.com/comm/jobs/view/JOB_ID
[separator line ----]
Next job block...
```

## LinkedIn 保存职位提醒 (jobs-noreply@linkedin.com)

Subject: "你的名字，立即申请"XXX的YYY岗位""
Body structure:
```
Main job title + company + location
查看职位: URL

其他已保存的职位
[separator ----]
Second job title + company + location
查看职位: URL
```

## JobsDB Recommendations (noreply@e.jobsdb.com)

Subject: "Job Title + N new jobs"
Body structure:
```
Hi YourName, we've got new job recommendations...

[logo image]
Job Title
Company Name
Location, District
$XX,000 – $YY,000 per month
* Bullet point requirement 1
* Bullet point requirement 2

[logo image]
Next Job Title
...
```

## Noise Patterns to Skip

### LinkedIn
- "简单几步，轻松迈向成功" (CTA button)
- "编辑订阅" / "其他订阅"
- "查看领英上的全部职位"
- "查看全部职位"
- "有符合您的搜索偏好" / "您已成功订阅"
- "该公司正在热招中"
- "使用简历和职业档案申请"
- Lines containing: Subject:, To:, From:, <strong, midToken, otpToken, trk=, eid=, lipi=

### JobsDB
- "Rate your recent employer"
- "apple store" / "google play"
- "Edit frequency"
- "View more jobs"
- "Recently posted"
- Lines starting with "* " (requirement bullets, not company names)
- Lines starting with "[" or "http" (URL tracking blocks)
- "%%str_to_replace_open_tracking%%"

### Both
- Any line that looks like email metadata (Subject:, To:, From:)
- HTML tags: <strong>, <a href=...>

## Glassdoor Job Alerts (noreply@glassdoor.com) — 2026-06-12, updated 2026-06-24

Subject: "{Job Title} at {Company} and N more jobs in Hong Kong for you. Apply Now."
Body: HTML with zero-width joiner characters (‌​‍‎‏﻿) as anti-scraping noise.

**⚠️ 关键发现（2026-06-24实测）**：himalaya渲染后的文本结构中，**公司名在URL行闭括号之后，且是下一个job的公司名，不是当前job的**。

himalaya渲染后的实际文本结构：
```
[header: Job alert: {Keyword}Your job listings for {Date}{First Company} {Rating} ★]
{Job Title 1}
{Location 1}
{Nd} (https://glassdoor.com...jobListingId={ID1})  {Company 2} {Rating} ★   ← Company 2是下一job的公司
{Job Title 2}
{Location 2 or "easy apply"}
{Nd} (https://glassdoor.com...jobListingId={ID2})  {Company 3} {Rating} ★
...
{Job Title N}
{Location N}
{Nd} (https://glassdoor.com...jobListingId={IDN})  see more jobs (...)
```

**解析算法**：
1. Pass 1: 找所有 `Nd (URL...jobListingId=XXX) company rating ★` 行
2. Pass 2: 对于URL行N，**公司名**来自URL行N-1的after-paren（第一个job从header提取）
3. **Job title**在URL行前2行，**Location**在URL行前1行
4. 跳过"easy apply"等badge行
5. `re.search(r'(\d+)d\s*\((https://[^)]*jobListingId=(\d+)[^)]*)\)\s*(.*)', line)` 提取URL和after_paren
6. 公司名 = `re.sub(r'\d+\.?\d*\s*★?\s*$', '', after_paren).strip()`

**⚠️ _read_email_body pitfall**：`himalaya message read`返回的HTML被清理后，如果用`" ".join(lines)`会把所有行合并成一行，破坏解析结构。必须用`"\n".join(lines)`保留换行。同时需过滤零宽字符行：`re.match(r'^[\s\u200b-\u200f\ufeff\u2060\u00ad]+$', clean)`。

**Key fields to extract**:
- `jobListingId` (in URL param): unique ID for dedup across days
- Company name + rating
- Job title
- Salary (if present)
- Posted time (relative)

**Noise to skip**:
- Zero-width chars: strip `‌​‍‎‏﻿` (U+200C, U+200B, U+200E, U+200F, U+FEFF)
- "Create job alerts for related roles" section
- "Want more listings" CTA
- Footer: privacy policy, unsubscribe links, address
- `info@glassdoor.com` emails (marketing, not job alerts)

**Dedup**: Same `jobListingId` appears in consecutive days' emails. Dedup on jobListingId.

**JD fetching**: Glassdoor links are Cloudflare-blocked. Use company career sites or LinkedIn as fallback. See `glassdoor-hk-guide.md`.

## LinkedIn 职位订阅正文提取（2026-06-24新增）

LinkedIn推荐邮件正文结构（himalaya渲染后）：
```
[header: 职位订阅: {keyword} - {location}   N个新职位符合您的偏好]
---
{Job Title}
{Company}
{Location}
查看职位: https://www.linkedin.com/comm/jobs/view/{JOB_ID}
---
{Next Job Title}
...
```

**解析算法**：用 `re.split(r'-{10,}', body)` 按分隔线分割，每块提取：
1. 找URL: `re.search(r'(https://www\.linkedin\.com/comm/jobs/view/\d+)', block)`
2. 提取job_id: `re.search(r'jobs/view/(\d+)', url)`
3. 逐行跳过无关行（"查看职位"/"该公司正在热招"/"使用简历"/http开头），第一个有效行=title，第二个=company，第三个=location

## Indeed 邮件提取

URL模式: `https://hk.indeed.com/viewjob?jk={hex_id}`
Job title和company在URL前3行中逆序提取。

## JobsDB 邮件提取

URL模式: `https://hk.jobsdb.com/job/{numeric_id}`
提取逻辑同Indeed。

## 猎头分类修复（2026-06-24）

**问题**：`RECRUITER_KEYWORDS`含"招聘""人才""recruitment"等宽泛词，LinkedIn推荐邮件正文（如"招聘专员消息可提升2倍"）触发误标。

**修复**：
1. 关键词收紧：去掉宽泛词，改为精准猎头信号：
   - "看了你的简历"/"看了你的资料"/"reviewed your profile"
   - "your profile caught"/"your background"
   - "想和你聊聊"/"would like to discuss"/"would like to connect"
   - "有合适的机会"/"suitable opportunity"
   - "猎头"/"headhunter"/"executive search"/"staffing"
2. 平台排除：`_classify_email`和`_classify_email_with_body`新增`from_addr`参数。已知平台域名列表`JOB_PLATFORM_DOMAINS_FOR_CLASSIFY`（linkedin.com/jobsdb.com/glassdoor.com/ctgoodjobsnews.hk/ctgoodjobs.hk/indeed.com/领英/jobs-listings@）的邮件永远不标猎头。

## 聚合推荐邮件识别

**判断方法**：`_is_recommendation_email(subject)` 检查subject是否包含：
- `and \d+ more jobs` / `\d+ new jobs` / `\d+ more jobs`
- `\d+ 个新职位` / `\d+ 个新工作`
- `job alert` / `职位订阅` / `recommendations`

**处理流程**：
1. 读取邮件正文（`_read_email_body`，保留换行）
2. 根据from_addr分发到对应平台解析器
3. 每个提取的岗位创建独立tracker记录（ID格式：`{email_id}_job_{job_id}`）