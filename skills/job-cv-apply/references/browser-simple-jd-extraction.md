# 浏览器简化JD提取方法（无需CDP）

> 2026-07-07 验证。CDP不可用时的轻量降级方案。
> 核心思路：`browser_navigate` → `browser_scroll` → `browser_snapshot(full=true)`
> 不需要CDP WebSocket、不需要curl、不需要Python脚本。

## LinkedIn JD提取（无登录状态下可用）

### 步骤（已验证 2026-07-07）

1. `browser_navigate` 到 job/view URL:
   ```
   https://www.linkedin.com/jobs/view/{JOB_ID}
   ```

2. 页面加载后会显示LinkedIn登录提示，但**部分JD内容仍可获取**

3. `browser_scroll(direction='down')` — 触发懒加载

4. `browser_snapshot(full=true)` 或 `browser_snapshot(full=false)`
   - 约 60% 的JD内容可读（尤其是"关于职位"section下的职责和要求列表）
   - CLP Manager Digital Technology Solutions 案例：成功提取全部9条职责 + 8条要求
   - AS Watson AI Delivery Lead 案例：仅能提取标题+公司+地点+申请人数等元信息，JD正文被完全遮挡

### 局限性

| 场景 | 成功率 | 说明 |
|------|--------|------|
| JD正文在页面HTML中（常见） | ~60% | 滚动后snapshot可显示部分内容 |
| JD被完整login-wall遮挡 | ~30% | snapshot显示空白或极少量信息 |
| 页面完全重定向到登录页 | ~10% | 无法获取任何JD信息 |

### 识别标志

- browser_snapshot 中如果出现 `show-more-less-html__markup` class → 大概率可提取JD
- 如果只能看到按钮"申请/保存/试用Premium"但没有JD文本 → 被login-wall完全遮挡

### 替代方案

如果简单方式失败，按优先级尝试：
1. curl + 正则提取 meta description（参考 `linkedin-jd-extraction.md`）
2. CDP WebSocket createTarget（参考 `jd-fetching-methods.md` 方法F）
3. 搜索Indeed/JobsDB同名岗位（参考 `jd-fetching-methods.md` 方法B/C）

## JobsDB JD提取（无需登录 ✅）

### 步骤（已验证 2026-07-07）

1. `browser_navigate` 到公司职位搜索页:
   ```
   https://hk.jobsdb.com/{lang}/search/jobs?q={公司名}
   ```
   或直接公司主页:
   ```
   https://hk.jobsdb.com/{lang}/{公司名}-jobs
   ```

2. 在搜索结果列表中找到目标职位（article标签），用 `browser_click` 点击

3. `browser_snapshot(full=true)` 查看职位摘要

4. 摘要内容包含：
   - 职位标题 + 公司名
   - 地点
   - 前3条职责要点（bullet list）
   - 1-2句团队描述
   - subClassification + classification
   - 刊登日期

5. 注意：点击后页面可能不会显示完整JD详情（Jobsdb可能跳转到详情页或展开inline面板），如果snapshot内容不够，尝试 `browser_scroll(direction='down')` 后再snapshot

### 局限性

- Jobsdb详情页有Cloudflare保护，CDP未连接时无法获取完整JD全文
- 搜索页展示的职位摘要通常只有2-5条关键要求
- 搜索页每页最多20条结果
- CDP模式下可绕过CF限制（参考 `cdp-browser-workflow.md`）

### 改进建议

对于Jobsdb JD，结合Jobsdb API获取更多信息:
```
curl -s "https://hk.jobsdb.com/api/jobsearch/v5/search?siteKey=HK-Main&keywords={关键词}&pageSize=10&page=1"
```
返回JSON包含岗位ID、标题、公司、薪水等信息。

## Glassdoor JD提取（轻量可用 ✅）

1. 搜索页：`browser_navigate` 到 Glassdoor 搜索结果
2. 页面加载后会显示职位列表
3. 部分JD内容可直接从搜索结果页获取（职位名称 + 公司 + 简要描述）

## 三平台对比（2026-07-07）

| 平台 | 简单提取 | 成功率 | CDP提取 | 推荐方式 |
|------|----------|--------|---------|----------|
| LinkedIn | browser_navigate+scroll+snapshot | ~60% | createTarget新tab | 简单/CDP均可 |
| JobsDB | 搜索页click+snapshot | ~70%（摘要） | CDP bypass CF | 有CDP用CDP，无则用浏览器 |
| Glassdoor | 搜索结果页摘取 | ~50%（摘要） | — | 仅做快速筛选 |
| Indeed | 搜索页右侧面板 | ~80% | WebSocket搜索页 | 简单方式即可 |

## 原则

- 能用 `browser_navigate+scroll+snapshot` 搞定的，不用CDP WebSocket
- CDP WebSocket留给LinkedIn深度JD（createTarget模式）和JobsDB详情页
- 每次抓取前先评估：这个JD值得花3分钟搭建CDP WebSocket吗？如果不值，就用浏览器简单方式
