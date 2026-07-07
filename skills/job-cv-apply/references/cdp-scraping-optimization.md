# CDP Browser Scraping — Optimization Patterns & Pitfalls

> 2026-06-25 实测总结。基于求职监控 cron 任务的多轮调试。

## 核心优化：browser_console 替代 click+snapshot

| 方法 | 每平台调用数 | 速度 | 数据质量 |
|------|------------|------|---------|
| navigate + click + snapshot | 3次 | 慢 | 完整页面文本（需解析） |
| **navigate + console** | **2次** | **快** | **结构化 JSON（直接可用）** |

**console 提取模式：**
```javascript
// LinkedIn
JSON.stringify([...document.querySelectorAll('.job-card-container__link')]
  .slice(0,5).map(e=>({title:e.textContent.trim(),link:e.href})))

// JobsDB
JSON.stringify([...document.querySelectorAll('[data-automation="jobTitle"]')]
  .slice(0,5).map(e=>({title:e.textContent,link:e.closest('a')?.href})))

// Indeed
JSON.stringify([...document.querySelectorAll('.jobTitle a')]
  .slice(0,5).map(e=>({title:e.textContent,link:e.href})))

// JobsDB 详情页 JD 提取
document.querySelector('[data-automation="jobDescription"], .job-description, [class*="description"]')
  ?.innerText?.substring(0,5000) || document.body.innerText.substring(0,5000)
```

## Pitfall: 多 tab 管理

**问题**：`browser_navigate` 创建新 tab 后，`browser_console` 可能在 `chrome://newtab/` 上执行而非目标页面。

**根因**：CDP 的 `Target.createTarget` 创建新 tab 后，后续 `Runtime.evaluate` 不一定指向新 tab。

**解决**：每次 `browser_navigate` 在当前 tab 内导航（不创建新 tab）。如果需要打开新 URL，直接再次调用 `browser_navigate`，它会在当前活跃 tab 内跳转。

## Pitfall: Chrome 崩溃恢复

**问题**：Chrome 以 `--user-data-dir` 启动时，如果路径含空格或特殊字符，可能报"无法创建数据目录"。

**解决**：路径必须用引号包裹：`--user-data-dir="C:\Temp\chrome-cdp"`

**Cron 任务防护**：prompt 中必须写明"browser_navigate 超时30秒就跳过，不要重试"。否则子 agent 会用完全部 API 调用次数仍在重试。

## JobsDB 详情页 URL 格式

```
https://hk.jobsdb.com/job/{JOB_ID}
```

直接用这个 URL 格式可以跳过搜索步骤，减少一次调用。

## Cron 任务最优 prompt 结构

```
1. Gmail MCP 扫描（1次搜索 + N次读取 + 1次标已读）
2. CDP 连通检查（1次 terminal curl）
3. CDP 串行扫描（每平台 2次: navigate + console）
4. 去重追踪表（1次 read_file）
5. 输出报告
```

总调用量：~15次（Gmail 10 + CDP 12 + 其他 3 = ~25次，但 CDP 每平台只 2 次）
