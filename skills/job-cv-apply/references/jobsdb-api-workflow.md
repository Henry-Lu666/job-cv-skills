# JobsDB API 工作流

> 2026-06-10 实测通过。JobsDB 网页层被 Cloudflare 封死，但搜索 API 完全可用。

## 搜索 API

```
GET https://hk.jobsdb.com/api/jobsearch/v5/search
```

### 参数

| 参数 | 值 | 说明 |
|------|-----|------|
| `siteKey` | `HK-Main` | 固定 |
| `sourcesystem` | `houston` | 固定 |
| `keywords` | URL编码关键词 | **必须用这个，不要用 `userqueryid`**（后者返回通用结果） |
| `pagesize` | 10-30 | 每页结果数 |
| `page` | 1, 2, 3... | 翻页 |
| `sortmode` | `ListedDate` 或 `Relevance` | ListedDate=最新，Relevance=相关度（偏金融） |

### curl 示例

```bash
# 搜索
curl -s "https://hk.jobsdb.com/api/jobsearch/v5/search?siteKey=HK-Main&sourcesystem=houston&keywords=business+development+director&pagesize=30&page=1&sortmode=Relevance" \
  -H "Accept: application/json" \
  -H "User-Agent: Mozilla/5.0"

# 按 job ID 查单条
curl -s "https://hk.jobsdb.com/api/jobsearch/v5/search?siteKey=HK-Main&sourcesystem=houston&jobid=92321518&pagesize=1&page=1" \
  -H "Accept: application/json" \
  -H "User-Agent: Mozilla/5.0"
```

### JSON 响应结构

```json
{
  "totalCount": 4244,
  "data": [
    {
      "id": "92561530",
      "title": "Business Development Director",
      "companyName": "Individual House Limited",
      "salaryLabel": "$25,000 – $30,000 per month",
      "listingDateDisplay": "2m ago",
      "teaser": "Work description...",
      "bulletPoints": ["Requirement 1", "Requirement 2"],
      "locations": [{"label": "Central, Central and Western District"}],
      "classifications": [{"classification": {"description": "Sales"}}],
      "advertiser": {"description": "Company Name"},
      "employer": {"companyUrl": "https://hk.jobsdb.com/companies/..."}
    }
  ]
}
```

### 字段说明

| 字段 | 可用性 | 说明 |
|------|--------|------|
| `id` | ✅ 稳定 | Job ID，用于去重和构造详情页 URL |
| `title` | ✅ 稳定 | 岗位标题 |
| `companyName` | ⚠️ 偶尔为 null | 此时用 `advertiser.description` |
| `salaryLabel` | ⚠️ 经常为空 | 很多岗位不标薪 |
| `teaser` | ✅ 通常有 | JD 摘要，通常 100-500 字，够做 70% 粗筛 |
| `bulletPoints` | ⚠️ 经常为空 | 有时有 2-5 条要求要点 |
| `locations` | ✅ 通常有 | 数组，取 `label` 字段 |
| `classifications` | ✅ 有 | 行业分类 |

### 限制

- **无完整 JD 正文**：只有 teaser + bulletPoints，完整 JD 需打开网页（被 Cloudflare 挡）
- **详情页无法通过 API 获取**：`jobid=xxx` 参数返回的是搜索结果中的单条，不是详情页内容
- **完整 JD 的获取方式**：
  1. 用户本机 Chrome 打开 `https://hk.jobsdb.com/job/{id}`
  2. CDP 接管 Chrome（需用户先手动启动 `chrome.exe --remote-debugging-port=9222`）
  3. Gmail 邮件中的 JobsDB 推荐带链接

## 关键词搜索策略

```python
# 推荐的搜索关键词组合
searches = [
    "business development director",
    "partnership manager Hong Kong",
    "strategic partnerships",
    "operations director",
    "growth manager",
    "AI product manager",
    "digital transformation",
    "marketing director",
]
```

**注意**：`sortmode=Relevance` 容易偏金融/银行岗位。建议用 `ListedDate` 按时间排序，或两组都搜。

## 结果匹配流程

1. API 搜 4-6 组关键词 × 2-3 页
2. 用 `id` 去重
3. 用 `title` + `teaser` + `bulletPoints` 做关键词初筛
4. 初筛得分 ≥60% 的岗位：构造详情页 URL 发给用户手动核实
5. 用户贴回完整 JD 后：做 9 维度核实 + 定制简历

## 构造详情页 URL

```
https://hk.jobsdb.com/job/{id}
```

用户在本机 Chrome 打开即可（过 Cloudflare）。

## 已知 Pitfall

1. **`keywords` 和 `userqueryid` 效果完全不同** — `keywords` 返回相关结果，`userqueryid` 返回通用结果（art shop assistant 等无关岗位）。必须用 `keywords`。
2. **参数名大小写不敏感**（实测 `pagesize` 和 `pageSize` 都能用）但建议统一用文档中的写法。
3. **Relevance 排序偏金融** — 搜索 "business development director" 可能返回大量银行/保险岗位。用 `ListedDate` 或加行业过滤。
4. **teaser 够用但不完整** — 用 teaser 做 70% 的判断（行业、级别、方向），剩下 30% 需完整 JD（硬性要求、具体年限、语言要求等）。
5. **旧岗位可能已过期** — 1 周前的岗位可能已被下架，API 搜不到。
6. **无地区过滤参数（2026-06-11 实测）** — 在 `keywords` 中加 "Hong Kong" 会导致返回0结果（关键词太精确）。正确做法：用原始关键词搜索，然后在返回结果的 `locations` 字段中过滤HK（检查 `locations[].label` 或 `locations[].seoHierarchy` 是否包含 "Hong Kong"/"Kowloon"/"Central"/"Wan Chai"/"Causeway Bay"/"Quarry Bay" 等）。JobsDB 是亚太平台，会返回澳洲/新加坡/日本等非HK岗位，必须做 location 过滤。
7. **API端点不稳定（2026-06-13 实测）** — `www.jobsdb.com/api/jobsearch/v5/search` 返回404；`hk.jobsdb.com/api/jobsearch/v5/search` 返回200但 `searchMarket=UNIFIED_AU`（澳洲结果），需额外加 `siteKey=HK-Main&sourcesystem=houston` 才能切到HK。`gmail_job_scanner.py` 内置的JobsDB搜索仍正常工作（它可能使用不同的认证/参数组合）。**建议**：直接API调用时始终带 `siteKey=HK-Main`，返回后仍需检查 `solMetadata.searchMarket` 确认是HK而非AU。如果API持续返回澳洲结果，回退到 scanner 内置搜索。
