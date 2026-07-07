# JD抓取方法 (2026-07-02 更新)

## 方法A: LinkedIn JD抓取 — 使用 `Target.createTarget` ✅

**❌ 不要 `Page.navigate` 现有tab**：在用户已登录的LinkedIn tab内执行`Page.navigate`到新URL后，JD正文不渲染(bodyLen≈1000)。LinkedIn的SPA懒加载机制在新导航后不触发JD渲染。

**✅ 用 `Target.createTarget` 创建新tab**：通过browser-level websocket创建新tab，然后导航到目标URL，JD正文完整渲染(bodyLen=8000-13000)。2026-07-02实测5/5全部成功。

**curl meta description快速分类(可用)**:
```bash
curl -sL -H "User-Agent: Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15" \
  "https://www.linkedin.com/jobs/view/{JOB_ID}" 2>/dev/null | \
  grep -oP '(?<=meta name="description" content=")[^"]*' | head -1
```
返回1-2句摘要，足够做快速分类（方向/行业判断），但**不够做9维度评估**。

**回退方案(按优先级)**:
1. 搜索Indeed/JobsDB同名岗位 — 这些平台CDP可稳定提取完整JD
2. Gmail推荐邮件中的岗位摘要
3. 用户手动在Chrome中打开复制JD

## 方法B: Indeed JD提取 ✅ 搜索页右侧面板可靠

**CDP方式可用(2026-07-01验证)**:
1. `browser_navigate` 打开搜索页: `https://hk.indeed.com/jobs?q={关键词}&l=Hong+Kong`
2. 搜索结果页右侧面板自动加载第一个岗位的JD
3. `browser_cdp(method='Runtime.evaluate')` 提取:
   ```javascript
   var t = document.body.innerText;
   var jdStart = t.indexOf('完整職位描述') || t.indexOf('Job Overview') || t.indexOf('Key Responsibilities');
   t.substring(jdStart, jdStart + 6000);
   ```
4. 07-01实测: OrbusNeich Medical bodyLen=3985, JD完整

**注意**:
- Indeed viewjob URL (`/viewjob?jk=xxx`) 被Cloudflare拦截 — 必须通过搜索页访问
- 搜索结果可能不含目标岗位（岗位已下架/未索引）— 2-5天内可能消失
- Indeed右侧面板点击结果即可加载JD，比LinkedIn可靠10倍

## 方法C: JobsDB JD抓取 ✅ CDP可用(2026-06-25起)

CDP模式下JobsDB不再被Cloudflare拦截（连接用户真实Chrome，有cookie+浏览器指纹）。

**⚠️ URL格式(2026-07-01修正)**: 
- ✅ **搜索**: `https://hk.jobsdb.com/zh/jobs?keywords={query}&salary_from=25000`（中文路径）
- ✅ **直接JD**: `https://hk.jobsdb.com/job/{JOB_ID}`（但Cloudflare会拦截详情页，建议走搜索页）
- ❌ `https://hk.jobsdb.com/hk/en/jobs?...` 返回404（旧格式已失效）
- 用户书签栏的"找工作"文件夹保存的URL通常是正确格式

提取方法:
- 用createTarget新tab → navigate到JobsDB URL → wait → scroll → extract

## 方法D: JobsDB API摘要 ✅ 可用(仅摘要)

```python
url = f"https://hk.jobsdb.com/api/jobsearch/v5/search?siteKey=HK-Main&keywords={urllib.parse.quote(keyword)}&pageSize=20&sortMode=ListedDate&jobType=fulltime&page=1&include=seodata"
```
返回字段: `title`, `companyName`, `id`, `jobUrl`, `salary`(常空), `location`(常空)
注意: `totalCount`可信，单条摘要不足以做L3全文评估。

## 方法E: curl meta description (LinkedIn/其他) ✅ 快速分类

适用于任何有 `<meta name="description">` 的岗位页面。
返回1-2句摘要，足够判断方向/行业，不够做9维度评估。

```bash
curl -sL -H "User-Agent: Mozilla/5.0 (iPhone; CPU iPhone OS 17_0)" URL | \
  grep -oP '(?<=meta name="description" content=")[^"]*' | head -1
```

## 方法F: CDP WebSocket createTarget提取（推荐）✅ 跨平台通用

> 2026-07-02验证。比Hermes browser工具可靠得多。

**原理**：通过browser-level CDP WebSocket执行`Target.createTarget`创建新tab，再用page-level WebSocket连接该tab执行`Page.navigate`+`Runtime.evaluate`。新tab继承浏览器的全局session/cookie，LinkedIn/Indeed/JobsDB都正确渲染。

**关键发现**：`Target.createTarget`创建新tab → LinkedIn JD完整渲染(bodyLen=8000+)。如果改为`Page.navigate`在现有tab上跳转 → 仅~1000chars（JD懒加载不触发）。**总是用createTarget创建新tab，不要复用现有tab。**

**适用平台**：
- **LinkedIn** ✅ 用createTarget创建新tab（bodyLen=8000-13000，JD正文完整）
- **Indeed** ✅ 搜索页可用（bodyLen=9000+）；viewjob URL仍被CF拦截
- **JobsDB** ✅ 搜索+首页推荐可用；部分详情页仍被CF拦截

```python
import json, requests, asyncio, websockets

async def extract_jd_via_new_tab(browser_ws, url, wait=6):
    """通过createTarget创建新tab → 导航 → 等待+滚动 → 提取"""
    async with websockets.connect(browser_ws, ping_interval=30) as ws:
        # 1) 创建新tab
        await ws.send(json.dumps({"id": 1, "method": "Target.createTarget", 
            "params": {"url": "about:blank"}}))
        resp = json.loads(await ws.recv())
        tab_id = resp['result']['targetId']
        
        # 2) 获取新tab的page-level websocket URL
        tabs = requests.get('http://localhost:9222/json', timeout=5).json()
        page_ws = next(t['webSocketDebuggerUrl'] for t in tabs if t['id'] == tab_id)
        
        # 3) 连接page tab并导航
        async with websockets.connect(page_ws, max_size=2**21) as page:
            pid = 1
            await page.send(json.dumps({"id": pid, "method": "Page.navigate", 
                "params": {"url": url}})); pid += 1
            try: await asyncio.wait_for(page.recv(), timeout=20)
            except: pass
            await asyncio.sleep(wait)
            
            # 4) 滚动触发懒加载
            await page.send(json.dumps({"id": pid, "method": "Runtime.evaluate",
                "params": {"expression": "window.scrollTo(0, document.body.scrollHeight)",
                           "returnByValue": True}})); pid += 1
            try: await asyncio.wait_for(page.recv(), timeout=5)
            except: pass
            await asyncio.sleep(2)
            
            # 5) 提取JD内容
            await page.send(json.dumps({"id": pid, "method": "Runtime.evaluate",
                "params": {"expression": '''JSON.stringify({
                    title: document.title,
                    bodyLen: document.body?.innerText?.length || 0,
                    jdText: (document.querySelector('.show-more-less-html__markup')?.innerText || '').substring(0,7000),
                    closed: /(no longer accepting|cannot find|filled)/i.test(document.body?.innerText||''),
                    allText: (document.body?.innerText || '').substring(0,10000)
                })''', "returnByValue": True}})); pid += 1
            resp = json.loads(await asyncio.wait_for(page.recv(), timeout=15))
            val = resp.get('result',{}).get('result',{}).get('value','{}')
            result = json.loads(val) if isinstance(val, str) else val
        
        # 6) 关闭新tab
        await ws.send(json.dumps({"id": 2, "method": "Target.closeTarget",
            "params": {"targetId": tab_id}}))
        return result
```

**注意**：
- browser-level WS 从 `http://localhost:9222/json/version` 获取（`webSocketDebuggerUrl`字段）
- page-level WS 从 `http://localhost:9222/json` 获取（每个tab独立）
- `Runtime.evaluate` **只能在工作在page-level WS上**，browser-level WS没有这个方法
- 每次创建tab后等 5-6 秒+滚动触发懒加载，不要着急提取
- 提取后必须关闭新tab，否则Chrome内存持续增长
- 建议串行操作每个岗位（createTab → extract → closeTab → next），一次处理3-5个

## 方法G: 用户书签栏URL（快捷登录入口）

用户Chrome书签栏的"找工作"文件夹保存了各平台的已登录搜索URL。这些URL的优势：
- LinkedIn书签打开后直接进入jobs搜索页，**无需重新登录**
- JobsDB书签已预设中文路径+关键词+薪资过滤
- 比手动构造URL更可靠（不需要记格式变化）

**用法**：让用户点击书签打开页面 → CDP接管该tab → 执行JD提取

## 平台可靠性排名(2026-07-02)

| 平台 | JD提取 | 搜索 | 推荐/通知铃 | 备注 |
|------|--------|------|------------|------|
| **Indeed** | ✅ WebSocket搜索页 | ✅ WebSocket | ✅ 通知铃可读 | CDP WebSocket从搜索页加载右侧面板最可靠 |
| **JobsDB** | ✅ CDP可用 | ✅ CDP+WebSocket | ✅ 首页推荐+通知铃 | 搜索页OK，部分详情页有CF |
| **LinkedIn** | ✅ CDP createTarget | ✅ CDP WebSocket(8个) | ✅ 通知铃+推荐页 | ❌ 用Page.navigate现有tab失败；✅ 用createTarget新tab成功 |
| **CTgoodJobs** | ❌ SPA问题 | ❌ SPA问题 | ❌ | 搜索表单不触发，不浪费调用 |
| **猎聘** | ⚠️ 需登录 | ⚠️ 需登录 | ❌ | CDP登录态不稳定 |

**关键发现(2026-07-02)**：用`Target.createTarget`创建新tab的方式比`Page.navigate`现有tab可靠得多。LinkedIn JD提取成功率达到100%（5/5）。原因：新tab走完整SPA渲染流程，现有tab导航时不触发JD懒加载。

## Pitfall
- LinkedIn Guest API 2026-06起不可用，返回空结果
- **🔴 不要 `Page.navigate` 现有tab到新LinkedIn URL** — 会导致bodyLen≈1000，JD不渲染
- **✅ 必须用 `Target.createTarget` 创建新tab** — 新tab走完整渲染，bodyLen=8000-13000
- Hermes `browser_navigate` 创建的new page target不继承登录session（bodyLen≈994），CDP WebSocket在已登录tab内导航则OK
- **CDP WebSocket比Hermes browser可靠** — 优先使用
- **Indeed岗位下架速度快** — 2-5天内可能消失，发现后应尽快提取
- **JobsDB 2026-06-25起CDP可用** — CDP连接用户Chrome绕过CF
- browser方式抓取时，必须用 `browser_cdp + target_id` 而不是 `browser_console`（后者可能在错误tab执行）
- **禁止用子Agent并行抓取LinkedIn(2026-06-23教训)** — 必须串行，间隔≥3秒
- 抓到的JD可能含HTML实体(`&amp;`等)，需`html.unescape()`处理
- **🔴 Google OAuth在CDP模式下被拦截(2026-07-01验证)** — 用户必须在CDP Chrome窗口中直接手动登录各平台
- **🔴 JobsDB搜索URL格式2026年7月起已变更(2026-07-01验证)** — 旧格式`/hk/en/jobs` 返回404，正确格式 `/zh/jobs`
