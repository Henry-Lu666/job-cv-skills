# CDP Tab Management — Pitfalls & Workarounds

> 2026-06-25 实操验证。解决 Hermes browser 工具在 CDP 模式下的多 tab 问题。

## 核心问题

`browser_navigate` 打开页面后，`browser_console` 可能执行在 `chrome://newtab` 而不是目标页面。

**根因**：CDP supervisor 附着在特定 page target。`browser_navigate` 可能创建新 tab，但 supervisor 没切换到新 tab。

## 诊断

```javascript
// 在 browser_console 中执行
JSON.stringify({url: window.location.href, title: document.title, bodyLen: document.body?.innerText?.length})
```

如果返回 `chrome://newtab`，说明在错误的 tab 上。

## 解决方案：browser_cdp + target_id

### Step 1: 找到正确的 tab

```python
browser_cdp(method='Target.getTargets', params={})
```

返回所有 tab 列表，找到目标 URL 的 `targetId`。

### Step 2: 在正确的 tab 上执行 JS

```python
browser_cdp(
    method='Runtime.evaluate',
    params={"expression": "document.body.innerText.substring(0, 5000)", "returnByValue": True},
    target_id="<正确的targetId>"
)
```

## JobsDB 最佳实践

1. `browser_navigate` → `https://hk.jobsdb.com/job/{JOB_ID}`（直接打开岗位页）
2. `browser_cdp(method='Target.getTargets')` → 找到 JobsDB tab
3. `browser_cdp(method='Runtime.evaluate', target_id=...)` → 提取 JD

**🔴 搜索结果页的链接点击不导航（2026-07-03 验证）** — JobsDB 搜索结果的 job card 使用 SPA onclick handler，`browser_click` 点击标题 `<a>` 链接不会导航到详情页。**正确做法**：用 `Runtime.evaluate` 提取 href 属性后再 `browser_navigate` 直接打开：
```javascript
JSON.stringify([...document.querySelectorAll('article h3 a')].slice(0,5)
  .map(a=>({title:a.textContent.trim(),href:a.href})))
```
得到的 href 格式如 `https://hk.jobsdb.com/zh/job/{JOB_ID}?type=standard&ref=...`，从中提取 `{JOB_ID}` 后用 `browser_navigate` 直接打开。

**不要**：
- 点击搜索结果中的链接（SPA onclick 不会被 CDP 触发）
- 用 `browser_console`（可能在错误 tab）
- 用 `browser_click`（会触发页面跳转或什么都不发生）

## LinkedIn 特殊问题

LinkedIn JD 可能是懒加载的，即使在正确的 tab 上也可能拿不到内容。回退方案：
1. 滚动页面后再提取
2. 从 Gmail 邮件推荐中提取 JD 摘要
3. 用户手动截图

## 🔴 LinkedIn "Sign in to view more jobs" 遮罩（2026-07-01 验证）

**现象**：用户已在 CDP Chrome 的 `linkedin.com/feed` 登录，但 Hermes `browser_navigate` 打开的 LinkedIn jobs 搜索页仍显示 "Sign in to view more jobs" 遮罩。

**根因**：LinkedIn 的 session 检测是按 tab/page 粒度的。Hermes browser 工具创建的新 page target 可能不被 LinkedIn 识别为已登录会话（即使同一 Chrome 实例的其他 tab 已登录）。

**解决方案 — 用 CDP WebSocket 直接操作已登录 tab**：

```python
import json, requests, asyncio, websockets

async def extract_from_logged_in_tab():
    # 1. 找到用户已登录的 LinkedIn tab
    tabs = requests.get("http://localhost:9222/json", timeout=5).json()
    li_tab = next((t for t in tabs if 'linkedin.com/feed' in t.get('url','')), None)
    if not li_tab:
        li_tab = next((t for t in tabs if 'linkedin.com' in t.get('url','') and 'logout' not in t.get('url','')), None)
    
    ws_url = li_tab['webSocketDebuggerUrl']
    async with websockets.connect(ws_url) as ws:
        # 2. 在已登录 tab 内导航到搜索页
        nav_msg = json.dumps({'id': 1, 'method': 'Page.navigate', 
            'params': {'url': 'https://www.linkedin.com/jobs/search/?keywords=AI+transformation&location=Hong+Kong'}})
        await ws.send(nav_msg)
        await ws.recv()
        await asyncio.sleep(4)  # 等页面加载
        
        # 3. 提取页面内容
        await ws.send(json.dumps({'id': 2, 'method': 'Runtime.evaluate',
            'params': {'expression': 'document.title', 'returnByValue': True}}))
        r = json.loads(await ws.recv())
        print(r['result']['result']['value'])
```

**优点**：直接使用用户已有的登录会话，不创建新 page target，LinkedIn 识别为已登录。

**注意**：
- 导航到搜索页后会替换掉用户当前看到的页面（如 feed）。建议先通知用户。
- 每搜一次关键词需要重新 `Page.navigate` + `asyncio.sleep(4)`。
- LinkedIn 搜索结果页通常只显示约 8 个 job card，需要用 `scroll` 或精确 URL 参数获取更多。

**不要**：尝试在 CDP 浏览器中点击 Google OAuth 登录（Google 会拦截，提示"此浏览器或应用可能不安全"）。

## 🔴 Google OAuth 在 CDP Chrome 中被拦截（2026-07-01 验证）

**现象**：CDP 控制的 Chrome 中点击 "Continue with Google" 后，Google 显示 "Couldn’t sign you in — This browser or app may not be secure"。

**原因**：Google 检测到 CDP/自动化控制环境，出于安全原因阻止登录。

**解决方案**：
1. 让用户直接在 CDP Chrome 窗口中手动输入密码登录（不是通过 agent 自动化）
2. 登录后 session cookie 保留，后续所有 tab 共享登录态
3. 只要不删 `--user-data-dir` 目录，登录态永久有效

## 🔴 CDP page-level WebSocket 可能返回 HTTP 500（2026-07-03 验证）

**现象**：尝试直接 CDP 连接 `ws://localhost:9222/devtools/page/{targetId}`（页面级WS）时，webSocket 库返回 `InvalidStatus: HTTP 500`。

**根因**：Chrome DevTools 的 page-level WebSocket 可能拒绝来自非浏览器环境的连接（某些 Chrome 版本的安全策略）。

**替代方案**：
- 使用 `ws://localhost:9222/devtools/browser/{browserId}`（浏览器级WS）通过 `Target.attachToTarget` 附加到目标页面
- 或者直接用 Hermes `browser_cdp` 工具加 `target_id` 参数（不走 WebSocket）
- 或者用 `browser_navigate` 直接导航到目标URL（Hermes 内部处理连接）

**正确做法（浏览器级 WebSocket）：**
```python
import websockets, json, asyncio

async def cdp_via_browser_ws():
    async with websockets.connect('ws://localhost:9222/devtools/browser/XXXX') as ws:
        # 创建新 tab
        await ws.send(json.dumps({'id':1,'method':'Target.createTarget',
            'params':{'url':'about:blank'}}))
        resp = json.loads(await ws.recv())
        tid = resp['result']['targetId']
        
        # 附加到新 tab
        await ws.send(json.dumps({'id':2,'method':'Target.attachToTarget',
            'params':{'targetId':tid,'flatten':True}}))
        resp = json.loads(await ws.recv())
        sess = resp.get('result',{}).get('sessionId','')
        
        if not sess:
            # attachToTarget 可能返回空 sessionId — 回退到 Hermes browser 工具
            # 用 browser_navigate + browser_cdp(target_id=...) 替代
            print("⚠️ attachToTarget 失败，回退到 Hermes browser_cdp")
```

**回退方案**：当浏览器级WS + attachToTarget 也失败时，直接用 Hermes 内建工具：
```python
# 先用 browser_navigate 导航
browser_navigate(job_url)
# 再用 browser_cdp 在目标 tab 上执行 JS
browser_cdp(method='Runtime.evaluate', 
    params={"expression": "document.body.innerText.substring(0,5000)",
            "returnByValue": True},
    target_id="<tab的targetId>")
```

## 调用预算

每个平台（navigate + getTargets + evaluate）= 3 次调用。
6 个平台 = 18 次调用。
子 agent 50 次上限，最多处理 5-6 个平台。
建议：每批 3-4 个岗位，失败就跳过。
