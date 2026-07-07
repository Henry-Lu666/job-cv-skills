# LinkedIn JD 全文抓取方法

## curl 抓取（推荐，guest 无需登录）

```bash
curl -s -L -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36" \
  "https://www.linkedin.com/jobs/view/{JOB_ID}" | python3 -c "
import sys, re
html = sys.stdin.read()
match = re.search(r'<div class=\"show-more-less-html__markup[^\"]*\">(.*?)</div>', html, re.DOTALL)
if match:
    text = re.sub(r'<[^>]+>', '', match.group(1))
    print(text.strip()[:3000])
else:
    print('NO_JD_FOUND')
"
```

**成功率**: LinkedIn guest view 页面 JD 全文提取率 ~95%（2026-06-10 实测 35/35 成功）。
**限速**: 连续抓取建议 0.3-0.5s 间隔，避免触发频率限制。
**截断**: JD 建议截取前 3000 字符，覆盖完整 requirements 段落。

## 已知限制

| 平台 | 问题 | 替代方案 |
|------|------|---------|
| JobsDB | Cloudflare 403，curl 和 browser 均被挡 | 用户手动打开浏览器查看 |
| LinkedIn guest search | 1周+的旧岗位搜不到（API 返回空） | browser_navigate 登录后搜索 |
| Google search via curl | 被 Google bot detection 拦截 | browser 工具搜索 |

## 从 LinkedIn 搜索页面提取 job ID

```javascript
// 在 browser_console 中执行
(() => {
    const links = document.querySelectorAll('a');
    const jobs = [];
    const seen = new Set();
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

注意 LinkedIn guest 页面 URL 格式为 `hk.linkedin.com/jobs/view/slug-4425452567`，ID 在最后一个连字符后面。
