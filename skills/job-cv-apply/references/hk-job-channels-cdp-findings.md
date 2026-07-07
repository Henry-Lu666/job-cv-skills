# 香港求职渠道 — CDP自动化实测记录

> 2026-06-29 实测。Chrome CDP连接状态下测试各平台的自动化可行性。

## CTgoodjobs — ❌ CDP不可自动化

**问题1：搜索不跳转**
- 首页搜索表单（www.ctgoodjobs.hk/zh）输入关键词+点击搜索 → 页面不跳转
- 原因：SPA架构（React），browser_click不触发React的状态更新

**问题2：岗位详情打不开**
- AI推荐好工卡片点击后不导航到详情页
- 原因：onclick handler依赖React事件系统，CDP的DOM click无法触发
- JS提取卡片标题可行，但无URL（链接是空的）

**回退方案：**
1. 搜索用子域名URL：`https://jobs.ctgoodjobs.hk/zh/jobs?keyword={关键词}&salary_from={最低薪}`
2. 搜索结果页可提取标题+公司+薪资+地点
3. 详情页需用户手动打开

**登录状态：** Henry账号已登录

---

## 劳工处 — ⚠️ 部分可用

**搜索：✅ 可用**
- 表单交互正常：选择类别"管理/行政"(value=15) + 输入中文关键词 + 点击搜索 → 返回结果
- 结果页可用JS提取标题+薪资+地点（按行解析body.innerText）
- 排序可用JS修改select值（薪酬由多至少）

**详情页：❌ 不可用**
- 搜索结果链接是ASP.NET postback onclick handler
- CDP的browser_click无法触发postback
- 需用户手动打开详情页

**最佳搜索组合：**
- 关键词：经理 / 总监 / 运营
- 类别：管理/行政
- 薪酬下限：$20,000+
- 排序：薪酬由多至少

---

## Indeed — ⚠️ 搜索页可用

**搜索页：✅ 可用**
- `https://hk.indeed.com/jobs?keywords={query}` 可正常访问
- 可提取搜索结果列表

**详情页（viewjob）：❌ 被CF拦截**
- `https://hk.indeed.com/viewjob?jk=xxx` 触发Cloudflare验证
- 需通过搜索页右侧面板查看JD

---

## 平台CDP自动化能力总结

| 平台 | 搜索 | 详情页 | 登录态 | 备注 |
|------|------|--------|--------|------|
| LinkedIn | ✅ | ✅ (body.innerText) | ✅ | 需串行防429 |
| JobsDB | ✅ | ✅ | ✅ | CDP绕过CF |
| CTgoodjobs | ❌ (SPA) | ❌ (SPA) | ✅ | 用子域名URL搜 |
| Indeed | ✅ | ❌ (CF) | ✅ | 详情需搜索页面板 |
| Glassdoor | ✅ | ✅ | ✅ | Indeed共享登录 |
| 猎聘 | ✅ | ✅ | ✅ | 内地+香港 |
| 劳工处 | ✅ | ❌ (postback) | N/A | 中文关键词 |
| 简职HK | N/A | N/A | N/A | 微信封闭 |

## 中资/央企官网扫描计划

待执行。优先级：
1. 中银香港 BOCHK — digital transformation
2. 建银亚洲 CCB Asia — asia.ccb.com/career
3. 招商局集团 — cmhk.com
4. 华润集团 — crc.com.cn
5. 中国移动香港 — hk.chinamobile.com
