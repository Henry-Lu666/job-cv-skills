# CDP WebSocket Tab Reuse Technique

**发现时间**: 2026-07-02
**场景**: 用户已打开JobsDB tab在CDP Chrome中，agent需要搜索和提取多个岗位JD

## 核心思路

不要创建新的Hermes browser tab（会丢失登录态），而是**复用用户已在CDP Chrome中打开的tab**，通过WebSocket连接到该tab进行搜索和提取。

## 技术实现

```python
import requests, json, websockets, asyncio

# 1. 获取CDP targets
targets = requests.get('http://localhost:9222/json').json()

# 2. 找到用户已登录的JobsDB tab
jd_tab = [t for t in targets if 'jobsdb.com' in t.get('url', '')][0]
ws_url = jd_tab['webSocketDebuggerUrl']

# 3. 通过WebSocket操作该tab
async def search():
    async with websockets.connect(ws_url) as ws:
        # 导航到目标URL（在当前tab内跳转）
        await ws.send(json.dumps({
            'id': 1, 'method': 'Page.navigate',
            'params': {'url': 'https://hk.jobsdb.com/zh/job/93006769'}
        }))
        await ws.recv()
        await asyncio.sleep(5)  # 等页面加载
        
        # 提取页面内容
        await ws.send(json.dumps({
            'id': 2, 'method': 'Runtime.evaluate',
            'params': {
                'expression': 'document.body.innerText.substring(0, 5000)',
                'returnByValue': True
            }
        }))
        resp = await ws.recv()
        result = json.loads(resp)
        return result['result']['result']['value']

# ...连续操作：每次navigate到新URL，提取数据
```

## 优势

| 对比项 | Hermes browser | CDP WebSocket tab复用 |
|--------|---------------|----------------------|
| 登录态 | 新tab无登录态 | 继承用户当前session |
| CF拦截 | 可能触发 | 已绕过（用户有cookie） |
| 并发限制 | 6平台串行 | 单tab串行无额外限制 |
| 调用次数 | ~3次/平台(navigate+getTargets+evaluate) | ~2次/页面(navigate+evaluate) |

## 适用平台

| 平台 | 效果 | 说明 |
|------|------|------|
| **JobsDB** | ✅ 完美 | 搜索和详情页都可用，无CF拦截 |
| **LinkedIn** | ⚠️ 需tab存在 | 只有CDP中有LinkedIn登录tab时才可用 |
| **Indeed** | ✅ 可用 | 搜索页可用，viewjob页仍被CF拦截 |
| **CTgoodJobs** | ❌ 不可用 | SPA架构，搜索和详情都不可用 |

## 注意事项

1. **不要创建新tab** — 始终在已有tab内导航（`Page.navigate`），不要用`Target.createTarget`
2. **给页面加载时间** — 导航后等3-5秒再提取（`asyncio.sleep(5)`）
3. **检查是否导航成功** — 提取后检查`window.location.href`确认已跳转到目标页面
4. **CDP断开时跳过** — 先`curl localhost:9222/json/version`验证CDP在线
5. **复用用户浏览上下文** — 在用户已打开的tab上操作，不会影响用户体验（agent只是在同一tab内导航搜索）
