# 主动求职搜索工作流

> 当用户说"去XX上跑一圈"/"看看有什么岗位"/"主动出击"/"扫一遍"时，执行此流程。
>
> **注意**：除主动搜索外，还有**邮箱扫描**作为第三数据源（每日自动）。详见 `references/gmail-job-scan-workflow.md`。

## 搜索渠道优先级（2026-06-10 更新）

> **核心认知**: JobsDB/LinkedIn 只覆盖香港招聘约30-40%。大量"双休、准点下班、对内地人友好"的中资/央企/外企后台岗走内部渠道（公众号/行业群/官网）。

| 渠道 | 方式 | 发现岗位 | 核实完整 JD | 可靠性 |
|------|------|---------|------------|--------|
| **简职HK（公众号）** | 微信公众号推送 | ✅ 80%+中资/央企 | ⚠️ 需截图给agent | ✅ 对内地人最友好 |
| **CTgoodjobs** | ctgoodjobs.hk | ✅ 中高端专业岗 | ✅ 完整JD | ✅ 双休为主 |
| **劳工处互动就业** | www2.jobs.gov.hk | ✅ 政府/公营/大型企业 | ✅ 完整JD | ✅ 双休极多 |
| **Jijis** | jijis.org | ✅ 不卡经验/粤语 | ✅ 完整JD | ⚠️ 偏初级 |
| **猎聘** | liepin.com | ✅ 中资覆盖最佳 | ✅ 完整JD | ✅ 已注册 |
| **JobsDB 搜索 API** | curl JSON | ✅ 最佳数据源 | ⚠️ 仅摘要 | ✅ 稳定 |
| **Gmail 邮件** | gmail_job_scanner.py | ✅ 带链接 | ⚠️ 需点击 | ✅ 稳定 |
| **LinkedIn browser** | browser_navigate | ⚠️ ~15条摘要 | ❌ 需登录 | ⚠️ 弹窗干扰 |
| **中资官网SPA** | browser_navigate | ✅ 最全 | ✅ 完整JD | ❌ 需逐个手动 |
| **Glassdoor** | glassdoor.hk | ❌ 不抓岗位 | ✅ 查双休/文化 | ✅ 投递前必查 |
| LinkedIn Guest API | curl | ❌ 2026-06起不可用 | — | ❌ |

### 推荐工作流

```
每日自动: Gmail 扫描（LinkedIn + JobsDB 邮件）     ← 零反爬
每日手动: 简职HK公众号推送 → 截图/转发给agent分析   ← 中资捡漏
每周主动: JobsDB API × 方向关键词 × 3 页            ← curl 不被挡
          CTgoodjobs + 劳工处 首页扫描               ← 新渠道
          LinkedIn browser × 方向关键词              ← 列表摘要
          猎聘推荐列表                               ← 中资补充
每投必查: Glassdoor 看双休/加班/文化评价              ← 避坑
需要核实: 用户本机 Chrome 打开 / CDP 接管            ← 完整 JD
```

### JobsDB 搜索 API（首选数据源）

详见 `references/jobsdb-api-workflow.md`。

### LinkedIn browser 列表提取（备用）

browser_navigate 打开 LinkedIn 搜索页 → 关弹窗 → console 提取 job IDs：

```javascript
(() => {
    const links = document.querySelectorAll('a');
    const jobs = []; const seen = new Set();
    links.forEach(a => {
        if (a.href && a.href.includes('jobs/view/')) {
            const match = a.href.match(/-(\d{10})(?:\?|$)/);
            if (match && !seen.has(match[1])) {
                seen.add(match[1]);
                jobs.push({id: match[1], title: a.textContent.trim().substring(0, 60)});
            }
        }
    });
    return JSON.stringify({count: jobs.length, ids: jobs.map(j=>j.id)});
})()
```

LinkedIn URL 格式：`hk.linkedin.com/jobs/view/slug-TITLE-SLUG-4425452567?position=1&pageNum=0`
Job ID 是最后一个 `-` 后的 10 位数字。

### ❌ LinkedIn Guest API（2026-06 起不可用）

`/jobs-guest/jobs/api/seeMoreJobPostings/search` 返回空结果。**不要使用。**

### ⚠️ 替代方法：LinkedIn browser 列表搜索

browser_navigate 打开搜索页 → 关弹窗 → console 提取 job IDs → curl 抓 JD 详情。
详见 `references/jd-fetching-methods.md` 方法 B。

### ⚠️ LinkedIn JD 抓取（有 job ID 时）

```bash
curl -s -L -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" \
  "https://www.linkedin.com/jobs/view/{JOB_ID}"
```

解析: `re.search(r'<div class="show-more-less-html__markup[^"]*">(.*?)</div>', html, re.DOTALL)`
详见 `references/jd-fetching-methods.md` 方法 A。

### JobsDB API（第二数据源，已验证可用）

**已验证的完整URL格式**（2026-06-05实测通过）：

```bash
# keywords参数需URL编码，pageSize用camelCase
curl -sL "https://hk.jobsdb.com/api/jobsearch/v5/search?siteKey=HK-Main&keywords=$(python3 -c 'import urllib.parse; print(urllib.parse.quote("Operations Director"))')&pageSize=20&sortMode=ListedDate&jobType=fulltime&page=1&include=seodata" \
  -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36" \
  -H "Accept: application/json"
```

Python用法（execute_code中）：
```python
import urllib.request, urllib.parse, json
keyword = "Business Development Director"
url = f"https://hk.jobsdb.com/api/jobsearch/v5/search?siteKey=HK-Main&keywords={urllib.parse.quote(keyword)}&pageSize=20&sortMode=ListedDate&jobType=fulltime&page=1&include=seodata"
headers = {"User-Agent": "Mozilla/5.0 ...", "Accept": "application/json"}
req = urllib.request.Request(url, headers=headers)
with urllib.request.urlopen(req, timeout=15) as resp:
    data = json.loads(resp.read().decode("utf-8"))
    jobs = data.get("data", [])
    total = data.get("totalCount", 0)
```

JSON 返回结构：`title`, `companyName`（有时为null，此时 `company.name` 有值）, `id`（去重用）, `jobUrl`, `salary`, `location`

**⚠️ API字段可用性（2026-06-05实测）**：
- `salary` 和 `location` 字段**经常为空字符串**——薪资和地点需打开岗位链接确认
- `companyName` 可能为 `"Unknown"`（实际公司名藏在 `company.name` 或完全缺失）
- `jobUrl` 返回相对路径如 `/job/92552907`，需拼接 `https://hk.jobsdb.com` 前缀
- `totalCount` 可信，反映该关键词的全部结果数
- 每页最多返回 `pageSize` 条（最大值测试过20可用，30未验证）

**参数注意**：
- `keywords=` 是搜索关键词的标准参数（不要用 `userqueryid=`，返回无关结果）
- 大小写: 实测 `pagesize`（小写）和 `sortmode`（小写）可工作，`pageSize`/`sortMode`（camelCase）也可。**推荐小写**，更稳定
- `sortmode=Relevance` 按相关性排序（偏金融/银行），`sortmode=ListedDate` 按最新发布排序
- `jobtype=fulltime` 过滤全职（小写）
- 无需登录、无 Cloudflare 拦截
- 每次搜索间隔1秒，避免触发限流
- **顶层 key 是 `data`（数组），不是 `jobs`**
- **单条查询**: `...&jobid={ID}&pagesize=1&page=1` 可按 ID 获取单个岗位摘要

### Glassdoor HK（不可用）

Glassdoor 返回 HTTP 403 + Security Challenge 页面，无公开 API。**不要尝试 curl 或 browser 自动化。**

## 关键词矩阵

按用户画像（12年运营管理 + AI硕士 + BD经验），分5个方向搜索：

| 方向 | LinkedIn关键词 | JobsDB分类 |
|------|---------------|-----------|
| ①运营 | `operations manager` / `head of operations` | Management (1207) |
| ②BD | `business development director` / `head of business development` | Sales_Retail (1210) |
| ③数字化 | `digital transformation manager` / `AI product manager` | Management (1207) |
| ④综合管理 | `general manager` / `country manager` / `regional director` | Management (1207) |
| ⑤营销 | `marketing director` / `head of marketing` / `brand director` / `commercial director` | Marketing (1205) |

### LinkedIn URL 模板（browser_navigate 备用）

```
https://www.linkedin.com/jobs/search/?keywords=<KEYWORDS>&location=Hong+Kong&f_TPR=r604800&f_WT=1%2C3&sortBy=DD
```

### JobsDB API 模板

```
https://hk.jobsdb.com/api/jobsearch/v5/search?siteKey=HK-Main&keywords=<URL_ENCODED_KEYWORDS>&pageSize=20&sortMode=ListedDate&jobType=fulltime&page=1&include=seodata
```

注意：参数名大小写敏感（`pageSize` 非 `pagesize`，`sortMode` 非 `sortmode`）。

## 结果处理流程

1. **采集**：用 Guest API curl + Python解析，5-7组关键词并行搜索，汇总所有岗位
2. **去重**：按(岗位名, 公司名)元组去重；JobsDB可用`id`字段去重更精确
3. **L1评分**：用关键词匹配度打分（见下方评分规则）— ⚠️这只是粗筛，不是匹配结论
4. **L2/L3核实**：对L1评分≥3的岗位，抓取完整JD做9维度匹配评估。**跳过此步的结果禁止用"强推""值得投"等措辞**
5. **过滤**：去掉已知岗位（读现有文件去重）、黑名单岗位、overqualified 岗位
6. **分类**：核实后分为 强推(>=6) / 观望(3-5) / 坑(<3) 三档；未核实的单独标"⚠️L1未核实"
7. **呈现**：表格形式，含公司、岗位、匹配理由、核实状态、行动建议
8. **写入**：追加到现有扫货文件（不覆盖），或创建新文件

**输出文件位置**：快速交付物（岗位扫描、checklist等）保存到 `~/job-search/inbox/`（`~/桌面/`），不放知识库。命名格式：`{平台}岗位扫货_{YYYYMMDD}.md`。已有文件追加新section，不要覆盖历史数据。知识库（`wiki/projects/`）放追踪记录和规划文档。

## 评分规则

```python
def score(job_title):
    t = job_title.lower()
    s = 0
    # 高匹配（+3）
    for kw in ["operations", "business development", "general manager",
               "head of", "VP", "vice president", "channel", "retail",
               "digital transformation", "product manager", "strategy",
               "sales director", "brand director", "commercial director",
               "country manager", "regional"]:
        if kw in t: s += 3
    # 中匹配（+2）
    for kw in ["marketing director", "marketing manager", "senior manager", "AVP", "growth",
               "innovation", "consultant", "client", "account manager", "partnership",
               "managing director", "director"]:
        if kw in t: s += 2
    # 低匹配/降级（-2）
    for kw in ["officer", "executive", "coordinator", "assistant",
               "trainee", "intern"]:
        if kw in t: s -= 2
    return s
```

**分类阈值**：score >= 6 → 强推，3-5 → 观望，< 3 → 坑

## 黑名单关键词

以下直接标记为「坑」，不做分析：
- 奢侈品单店运营（Boutique Operations）→ overqualified
- 仓库管理（Warehouse Operations）→ 方向不对
- 金融Ops（Hedge Fund Operations）→ 需金融背景
- 银行网点管理（Branch Manager）→ 需银行经验
- 保险马甲（Glory/Family Heritage/Wealth）→ 保险套路
- 纯媒体投放（Media Buying）→ 不是赛道
- 纯IT项目管理（IT PMO）→ 需技术PM背景
- 矿业运营（Mining Operation）→ 方向完全不对
- 纯客服管理（Customer Service Manager）→ 方向不对

## 输出格式

**已核实的岗位**（L2/L3完成）:
```markdown
## 🎯 强推投递（已核实JD）
| # | 岗位 | 公司 | 匹配度 | 匹配理由 | 星级 |
|---|------|------|--------|---------|------|
| 1 | ... | ... | 65%    | ...     | ⭐⭐⭐⭐ |

## 👀 观望（已核实JD）
| # | 岗位 | 公司 | 匹配度 | 观望理由 |

## ⚠️ 坑
| 岗位 | 公司 | 坑在哪 |
```

**未核实的岗位**（仅L1关键词命中，需进一步核实JD）:
```markdown
## ⚠️ L1未核实 — 待抓JD
| # | 岗位 | 公司 | L1关键词 | 来源 | 下一步 |
|---|------|------|---------|------|--------|
| 1 | ... | ... | AI,BD   | Gmail | 抓JD核实 |
```

**严禁**：未核实的岗位不得使用"强推""值得投"等肯定性措辞。

## Pitfall

0. **L1 结果绝不能当"已匹配"呈现（2026-06-20 教训）** — 跑完Gmail扫描+JobsDB API后，出了一大篇带"★★★★★强推""值得投"的报告，用户问"都JD匹配了吗？"答案是没有。L1关键词粗筛只是第一步，必须紧跟L2/L3核实才能用肯定性措辞。如果时间紧做不了L3，结果必须标"⚠️未核实-L1仅关键词命中"，绝不用"强推""值得投"。正确流程：L1扫描→筛选候选→L2/L3核实→出匹配报告，不要跳步。
1. **JobsDB API 是首选数据源** — 网页被 Cloudflare 封死，但搜索 API (`/api/jobsearch/v5/search`) 完全可用，返回结构化 JSON。必须用 `keywords` 参数，不要用 `userqueryid`（后者返回无关结果）。
2. **LinkedIn Guest API 2026-06 起不可用** — 返回空结果。改用 browser 列表搜索 + console 提取 job IDs。
3. **Google/DuckDuckGo 会阻断自动化** — 搜索 `site:linkedin.com/jobs` 会弹验证码，不要用。
4. **子Agent工具路由不稳定** — 指定 `toolsets=["web"]` 或 `["browser"]` 时，子Agent可能只拿到Feishu MCP工具。复杂搜索任务建议主Agent直接用 execute_code + terminal 执行 curl。
5. **不要用子Agent搜LinkedIn/JobsDB** — 子Agent的webSearch工具无法有效搜索这两个平台。最佳实践：主Agent直接用 execute_code 跑Python脚本调API。
6. **Glassdoor完全不可用** — 返回403+Security Challenge，无公开API，不要浪费时间尝试。
7. **LinkedIn弹窗关闭后才能看到岗位** — 导航后第一步是找到关闭按钮并点击（仅browser方式需要）。
8. **JobsDB Relevance 排序偏金融** — 搜索 "business development director" 返回大量银行/保险岗位。用 `sortMode=ListedDate` 按时间排序更均匀。
9. **每次搜索只看第一页** — LinkedIn不登录无法翻页，所以要多组关键词覆盖。Guest API 可用 start=10 翻到第二页（但已不可用）。
10. **评分后必须人工过一遍** — 自动评分可能误判，最终建议需要agent结合用户画像判断。匹配度必须诚实——关键词命中 ≠ 人岗匹配。
11. **去重用 job ID** — JobsDB API 返回 `id` 字段精确去重。LinkedIn browser 用 URL 中的 10 位数字 ID。
12. **JobsDB teaser 够做 70% 粗筛** — 行业、级别、方向从 teaser 就能判断。剩下 30%（硬性要求、语言、资质）需完整 JD。