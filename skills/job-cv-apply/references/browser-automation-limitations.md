# 浏览器自动化限制与替代方案

## 问题：Cloudflare Turnstile 拦截

JobsDB (hk.jobsdb.com) 使用 Cloudflare Turnstile 反机器人验证。Hermes 的 `browser_navigate` 工具使用 Playwright headless Chromium，会被 Turnstile 识别为自动化浏览器并拦截。

**表现**：
- 页面加载后显示「正在进行安全验证」
- 出现「请验证您是真人」复选框
- 点击复选框无效 — Turnstile 检测到 headless 环境，故意不放行
- 每次刷新都重新验证，无法绕过

**影响的站点**：
- JobsDB (hk.jobsdb.com) — 确认被拦
- 其他使用 Cloudflare Turnstile 的招聘站点同理

## 根因：Playwright 浏览器与本机 Chrome 隔离

`browser_navigate` 启动的是 Playwright 自带的 Chromium 实例，**不是**用户本机的 Chrome/Edge。

| 维度 | Playwright Chromium | 本机 Chrome |
|------|-------------------|-------------|
| Cookies | 空（每次新会话） | 用户已登录的所有站点 |
| 登录态 | 无 | JobsDB/LinkedIn 等已登录 |
| 指纹 | headless 特征明显 | 真实浏览器指纹 |
| Cloudflare | 被识别拦截 | 正常通过 |

## 方案 A：CDP 接管本机 Chrome（推荐）

Chrome DevTools Protocol (CDP) 可以让 Playwright 连接到用户**已运行的真实 Chrome**，复用所有 cookies 和登录态。

### 启动 Chrome（带调试端口）

```bash
# Windows: 创建快捷方式或 bat 文件
"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222

# 或在 WSL 中通过 cmd 启动
cmd.exe /c "start chrome --remote-debugging-port=9222"
```

### Playwright CDP 连接

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://localhost:9222")
    context = browser.contexts[0]  # 复用已有的浏览器上下文
    page = context.new_page()
    page.goto("https://hk.jobsdb.com/zh/profile/me")  # 已登录态，Cloudflare 放行
```

### 优势
- 复用用户已登录的所有站点 cookies
- Cloudflare 看到的是真实浏览器指纹，不会拦截
- 多站点（JobsDB、LinkedIn、Indeed）通用

### 限制
- 需要用户先启动带 `--remote-debugging-port` 的 Chrome
- CDP 端口暴露在 localhost，仅限本地使用
- Chrome 关闭后需重新启动

## 方案 D：半自动化混合模式（备选）

当 CDP 不可用时的降级方案：

1. **hunter agent 用 curl/API 搜索公开岗位列表**（不需要登录）
2. **匹配结果推送给用户**
3. **用户在本机 Chrome 中打开 JD 链接**
4. **用户把 JD 文本/截图贴给 agent 继续处理**

JobsDB 公开搜索 URL 格式：
```
https://hk.jobsdb.com/hk/search/jobs?q=AI+product+manager&salary=25000-35000
```

## 方案 E：LinkedIn 公开搜索（无需登录）✅ 已验证

**发现 (2026-06-03)**：LinkedIn 职位搜索页在未登录状态下可以浏览岗位列表。

### 操作步骤

1. `browser_navigate` 打开 LinkedIn Jobs 搜索页：
   ```
   https://www.linkedin.com/jobs/search/?keywords=<关键词>&location=Hong+Kong&f_TPR=r604800&f_WT=1%2C3&sortBy=DD
   ```
   - `f_TPR=r604800` = 近1周
   - `f_WT=1%2C3` = On-site + Hybrid
   - `sortBy=DD` = 按发布日期降序

2. 页面加载后会弹出「登录以查看更多职位」对话框 → `browser_click` 关闭按钮

3. 关闭后可以看到完整的岗位列表（标题、公司、地点、发布时间）

4. 用 `browser_snapshot(full=true)` 提取所有岗位信息

5. 不登录能看到 ~10-15 个岗位摘要；翻页需要登录

### 限制

- 只能看到列表页摘要，点进JD详情页需要登录
- 每个搜索词只能看第一页结果
- 建议多组关键词搜索，覆盖不同方向

### JobsDB API（无需登录）✅ 已验证

JobsDB 有公开的搜索 API，返回 JSON：

```bash
curl -s "https://hk.jobsdb.com/api/jobsearch/v5/search?siteKey=HK-Main&sourcesystem=houston&userqueryid=<关键词>&pagesize=30&page=1&sortmode=Relevance&include=seodata&classification=<分类ID>"
```

分类 ID：
- Management = 1207
- Marketing & Communications = 1205
- Sales & Retail = 1210
- General Business = 1216
- Consulting = 1204

返回字段：title, companyName, locations, salaryLabel, listingDateDisplay, teaser, id

岗位链接：`https://hk.jobsdb.com/job/<id>`

### 限制

- `sortmode=Relevance` 返回的结果偏金融/银行，不一定精准
- `sortmode=ListedDate` 返回最新但不一定相关
- API 结果数量有限（每个分类约 10-30 条）
- 建议配合 LinkedIn 公开搜索交叉使用

## 实施状态

- [ ] CDP 原型搭建（待启动）
- [ ] hunter agent 集成 CDP 连接
- [x] LinkedIn 公开搜索（已验证可用，无需登录）
- [x] JobsDB API 搜索（已验证可用，无需登录）
