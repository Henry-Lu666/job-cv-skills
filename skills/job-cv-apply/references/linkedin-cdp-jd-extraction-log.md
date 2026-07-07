# LinkedIn JD CDP Extraction Log

> 实测记录：哪些LinkedIn岗位页能通过CDP提取JD，哪些不能。
> 用于诊断LinkedIn前端渲染问题的模式。

## 2026-07-02 新发现：Target.createTarget vs Page.navigate

**核心发现**：提取LinkedIn JD时，**创建新tab vs 导航现有tab**的结果截然不同：

| 方式 | LinkedIn JD bodyLen | 成功率 | 说明 |
|------|-------------------|--------|------|
| `Page.navigate` 在已渲染的现有tab上跳转新URL | ~1000 | ❌ 100%失败 | JD正文不渲染（SPA懒加载未触发） |
| `Target.createTarget` 创建全新tab再导航 | 8000-13000 | ✅ 100%成功 | 新tab走完整渲染流程 |
| Hermes `browser_navigate`（创建新page target） | ~1000 | ❌ 失败 | 新建的target不继承登录session |

**原因**：LinkedIn的JD内容通过SPA懒加载机制动态渲染。`Page.navigate` 在已加载的SPA上下文中跳转时，部分渲染钩子未被触发。`Target.createTarget` 创建的tab走完整初始化流程，JD正确渲染。

**实操规则**：
1. 用browser-level websocket（从 `/json/version` 获取）执行 `Target.createTarget`
2. 从 `/json` 获取新tab的page-level websocket URL
3. 连接page-level websocket执行 `Page.navigate` + wait(5-6s) + scroll + `Runtime.evaluate`
4. 完成后 `Target.closeTarget`

## 2026-06-26 旧记录（使用Hermes browser工具 + Page.navigate现有tab）

| 岗位 | LinkedIn ID | bodyLen | JD提取 | 备注 |
|------|-------------|---------|--------|------|
| Bemis — Global DT Lead | 4432228052 | 6990 | ✅ 成功 | JD完整可见，含Role Purpose |
| Madison Pearl — AI Advisory | 4417121632 | 1001 | ❌ 失败 | 只有页眉，JD区域空白（现有tab导航） |
| OX HR — Head of AI | 4421924051 | — | ❌ 失败 | 同上 |
| AIA — Transformation Office Lead | 4430220339 | ~1000 | ❌ 失败 | 只有页眉+页脚 |
| Link REIT — Sr Mgr AI Solution | 4432561598 | ~900 | ❌ 失败 | 同上 |

**旧记录的成功率：1/5 (20%) 但根因是用了错误的方法**

## 2026-07-02 新记录（使用createTarget方式）

| 岗位 | LinkedIn ID | bodyLen | JD提取 | 方法 |
|------|-------------|---------|--------|------|
| Appnovation — BD Director, APAC | 4432577310 | 9571 | ✅ JD完整 | 页面已存在（用户打开过），直接提取 |
| Shangri-La — Sr Mgr Strategy & Trans | 4426308270 | 8353 | ✅ JD完整 | 页面已存在，直接提取 |
| EPAM — Delivery Manager (AI) | 4403735362 | 10710 | ✅ JD完整 | createTarget新tab |
| OLIVER — Dir MarTech GenAI | 4404426296 | 13389 | ✅ JD完整 | createTarget新tab |
| M Moser — Leader AI Tech Team | 4405634231 | 4715 | ✅ JD完整 | createTarget新tab |

**新记录成功率：5/5 (100%)** — 用createTarget方式时全部成功

## 2026-07-03 新发现：createTarget也可能失败

| 岗位 | LinkedIn ID | bodyLen | 方法 | 结果 |
|------|-------------|---------|------|------|
| Sentient Labs — Director of Ops/Strategy | 4397717839 | 0 | createTarget新tab | ❌ attachToTarget返回空session_id，bodyLen=0 |
| Sentient Labs — Director of Ops/Strategy | 4397717839 | 990 | 现有tab Page.navigate | ❌ 仅导航栏+页脚（LinkedIn登录墙） |

**结论**：createTarget不再是100%成功。失败可能原因：
- Chrome版本/CDP协议版本不兼容（当前Chrome 149）
- browser-level WS连接后attachToTarget返回空session_id（偶发）
- 页面加载超时或SPA初始化失败

**规则更新**：
1. 先尝试createTarget（有机会成功）
2. 失败后立即尝试现有tab navigate（概率低但值得试）
3. 都失败 → curl meta description快速分类
4. 仍然不行 → 标记"需用户手动打开JD"
5. **不要多次重试同一个链接**，成本高收益低

## 回退方案优先级

1. `Target.createTarget` 创建新tab → 导航 → 等待 → 滚动 → 提取（有概率成功，非100%）
2. 现有tab `Page.navigate` — bodyLen≈1000但可拿到基本信息（公司/岗位/地点/时间/申请人数）
3. curl LinkedIn `<meta description>` 标签做快速分类
4. Gmail推荐邮件中的岗位摘要
5. 用户手动复制JD

## 诊断方法

```javascript
// 快速检查JD是否渲染
JSON.stringify({
  bodyLen: document.body?.innerText?.length || 0,
  hasJD: /(Key Responsibilities|About the role|About the job|核心职责)/i.test(document.body?.innerText||''),
  url: window.location.href,
  title: document.title
})
```
如果 bodyLen < 2000 或 hasJD = false → 提取失败，立即回退到其他方法。
