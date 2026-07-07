# CDP 多平台扫描优化指南

> 2026-06-25 实测。核心原则：每平台只用 navigate+console，禁用 click+snapshot。

## 效率对比

| 方法 | 每平台调用 | 6平台总调用 | 可扫平台数 |
|------|-----------|------------|-----------|
| navigate+click+snapshot | 3次 | 18次 | 3-4个（受API调用上限限制） |
| **navigate+console** | **2次** | **12次** | **5-6个** |

省下的调用 = 多扫2个平台。

## 各平台 JS 提取查询

### LinkedIn
```
URL: https://www.linkedin.com/jobs/search/?keywords=AI%20transformation%20Hong%20Kong&f_TPR=r604800
JS:  JSON.stringify([...document.querySelectorAll('.job-card-container__link')].slice(0,5).map(e=>({title:e.textContent.trim(),link:e.href})))
```

### JobsDB
```
URL: https://hk.jobsdb.com/jobs-in-hong-kong?keywords=AI+transformation&sortmode=ListedDate
JS:  JSON.stringify([...document.querySelectorAll('[data-automation="jobTitle"]')].slice(0,5).map(e=>({title:e.textContent,link:e.closest('a')?.href})))
```

### Indeed
```
URL: https://hk.indeed.com/jobs?q=AI+transformation&l=Hong+Kong&sort=date
JS:  JSON.stringify([...document.querySelectorAll('.jobTitle a')].slice(0,5).map(e=>({title:e.textContent,link:e.href})))
```

### CTgoodJobs
```
URL: https://www.ctgoodjobs.hk/en/search-jobs?keyword=AI+transformation&sortBy=postedDate
JS:  JSON.stringify([...document.querySelectorAll('[data-testid="job-title"] a, .job-title a')].slice(0,5).map(e=>({title:e.textContent,link:e.href})))
```

### 猎聘
```
URL: https://www.liepin.com/zhaopin/?key=AI+%E9%A6%99%E6%B8%AF&sortType=1
JS:  JSON.stringify([...document.querySelectorAll('.job-title-box a')].slice(0,5).map(e=>({title:e.textContent.trim(),link:e.href})))
```

### 劳工处
```
URL: https://www2.jobs.gov.hk/0/cn/jobseeker/jobsearch/search/
方法: 表单网站，需 browser_snapshot 提取（无法用 console 简单提取）
注意: 中文版必须用中文关键词
```

## 失败处理

- `browser_console` 返回空 `[]` 或报错 → 跳过该平台，不重试
- `browser_navigate` 超时 → 跳过，下一个平台
- 某平台选择器变了（网站改版）→ 更新上方 JS 查询

## Cron 任务中的串行间隔

每个平台 `browser_navigate` 后等 3 秒再下一个。用 `terminal: sleep 3` 实现。

## 实测数据（2026-06-25）

- 优化前：12 API calls, 11 tool turns, 扫3平台, ~4分钟
- 优化后：14 API calls, 13 tool turns, 扫5平台, ~3.5分钟
- 调用增加但平台增加更多，效率提升 ~67%（5/3）
