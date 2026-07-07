# CDP Browser Automation Patterns for Job Search

> 2026-06-25 实操验证。解决 browser_console 在错误 tab 上执行的核心问题。

## 核心问题

Hermes 的 `browser_navigate` 打开新页面后，`browser_console` 执行在 `chrome://new-tab-page/` 上，而非刚打开的页面。这是因为 CDP 创建新 tab 后，console 工具未自动切换焦点。

## 解决方案：browser_cdp + target_id

**三步模式**（每个平台/页面）：

```python
# Step 1: Navigate to the page
browser_navigate(url="https://hk.jobsdb.com/job/92924813")

# Step 2: Find the correct tab by URL/title
browser_cdp(method="Target.getTargets", params={})
# → 返回 targetInfos 列表，按 url/title 匹配找到 targetId

# Step 3: Execute JS on the correct tab
browser_cdp(
    method="Runtime.evaluate",
    target_id="88FC049326797A52E529AD2C814DE5B4",  # 从 Step 2 获取
    params={"expression": "document.body.innerText.substring(0,5000)", "returnByValue": True}
)
```

## JobsDB 提取模板

### 搜索页提取 job links
```javascript
JSON.stringify(
    [...document.querySelectorAll('article')].map(a => ({
        title: a.querySelector('h3')?.textContent?.trim(),
        company: a.querySelector('a[href*="/company/"]')?.textContent?.trim(),
        salary: a.textContent.match(/\$[\d,]+.*?month/)?.[0],
        desc: a.textContent.match(/(?:Deliver|Lead|Own|Join|Senior).*?(?=subClassification)/s)?.[0]?.trim()?.substring(0, 200),
        link: a.querySelector('a[href*="/job/"]')?.href
    })).filter(x => x.title)
)
```

### Job 详情页提取 JD
```javascript
document.body.innerText.substring(0, 5000)
```

### 提取 JD 特定元素（如果存在）
```javascript
document.querySelector('[data-automation="jobDescription"], .job-description, main')?.innerText?.substring(0, 5000)
```

## URL 格式

| 用途 | URL 格式 |
|------|---------|
| JobsDB 搜索 | `https://hk.jobsdb.com/jobs?keywords={query}&sortmode=ListedDate` |
| JobsDB 直接 JD | `https://hk.jobsdb.com/job/{JOB_ID}` |
| LinkedIn JD | `https://www.linkedin.com/jobs/view/{ID}`（CDP 无法提取 JD 内容） |

## 效率优化

| 方法 | 每岗位调用数 | 说明 |
|------|------------|------|
| browser_navigate + browser_snapshot | 2-3 次 | 简单但 snapshot 可能截断 |
| browser_navigate + browser_cdp(target_id) | 3 次 | 最可靠，推荐 |
| browser_click + browser_snapshot | 3-4 次 | 不推荐，多 tab 问题 |

## 已知限制

1. **LinkedIn JD 无法通过 CDP 提取** — body.innerText 返回 0 或空（Shadow DOM/动态加载）
2. **Chrome 高频操作会崩溃** — 连续 10+ 次 navigate+evaluate 后可能断开
3. **browser_console 始终在错误 tab** — 必须用 browser_cdp + target_id 替代

## Chrome 启动命令

```
Win+R: "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="C:\Temp\chrome-cdp"
```

WSL2 验证: `curl -s --connect-timeout 3 http://localhost:9222/json/version`

## Cron Job 优化经验

- 每平台只用 2 次调用：browser_navigate + browser_cdp(target_id)
- 失败就跳过，不要重试
- 串行，每平台间隔 3 秒
- CDP 不通时跳过浏览器扫描，只做 Gmail
