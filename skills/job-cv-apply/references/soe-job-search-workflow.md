# 中资企业招聘搜索工作流

> 当用户说"搜中资"/"看看中资官网"/"国企招聘"/"央企香港"时，执行此流程。
> 最后验证: 2026-06-10

---

## 搜索渠道（按可靠性排序）

| 渠道 | 方法 | 可自动化? | 覆盖质量 |
|------|------|----------|---------|
| **JobsDB API** | curl `keywords=公司英文名` | ✅ 完全自动 | ⚠️ 部分中资不发JobsDB |
| **Gmail 邮件** | gmail_job_scanner.py | ✅ 每日cron | ⚠️ 仅LinkedIn/JobsDB推送的 |
| **猎聘** | 用户手动浏览 + agent分析 | ⚠️ 半自动 | ✅ 中资覆盖最佳 |
| **公司官网SPA** | browser_navigate + 交互 | ❌ 需逐个手动 | ✅ 最全 |
| **微信公众号** | 用户手动 | ❌ 完全手动 | ✅ 内部渠道 |

---

## JobsDB API 搜索中资公司

用英文公司名搜索（中文名不返回结果）：

```bash
# 示例：搜索东方海外
curl -s "https://hk.jobsdb.com/api/jobsearch/v5/search?siteKey=HK-Main&sourcesystem=houston&keywords=Orient+Overseas&pagesize=15&page=1&sortmode=ListedDate" \
  -H "Accept: application/json" -H "User-Agent: Mozilla/5.0"
```

### 中资公司英文名对照表

| 中文名 | 英文搜索词 | 行业 |
|--------|-----------|------|
| 携程 | Trip.com / Ctrip | 科技/旅游 |
| 华为 | Huawei | 科技/通信 |
| 腾讯 | Tencent | 科技 |
| 阿里巴巴 | Alibaba | 科技 |
| 字节跳动 | ByteDance | 科技 |
| 小米 | Xiaomi | 科技 |
| 联想 | Lenovo | 科技 |
| 比亚迪 | BYD | 新能源汽车 |
| 宁德时代 | CATL | 新能源 |
| 东方海外 | Orient Overseas | 航运 |
| 中远海运 | COSCO Shipping | 航运 |
| 招商局 | China Merchants | 综合 |
| 华润 | China Resources | 综合 |
| 利丰 | Li & Fung | 供应链 |
| 中国移动 | China Mobile | 电信 |
| 中国电信 | China Telecom | 电信 |
| 数码通 | SmarTone | 电信 |
| 恒基 | Henderson Land | 地产 |
| 新世界 | New World Dev | 地产 |
| 中旅 | China Travel | 旅游 |
| 复星 | Fosun | 综合 |
| 国泰 | Cathay Pacific | 航空 |

### 过滤规则

搜索结果中，只保留：
1. `companyName` 实际包含目标公司名的（排除猎头/第三方代招）
2. 岗位标题含 Manager/Director/Head/VP/Senior/Lead 的
3. 排除银行/保险类（除非用户明确要求）

---

## 中资官网 SPA 搜索

大部分中资官网是 SPA，curl 只能拿到空壳 HTML。需要 browser 交互：

1. `browser_navigate` 打开招聘页
2. 选择 location = Hong Kong
3. 截取岗位列表
4. 用 `browser_console` 提取结构化数据

### 已知可访问的 SPA 招聘页

| 公司 | URL | 备注 |
|------|-----|------|
| Trip.com | https://careers.trip.com/global/job-list | 185+全球岗位 |
| 华为 | https://career.huawei.com/reccampportal/portal5/ | 需选地区 |
| 阿里巴巴 | https://talent.alibaba.com/ | 需选location |
| 腾讯 | https://careers.tencent.com/ | 需选location |
| 小米 | https://hr.xiaomi.com/ | 门店岗为主 |

### 已知不可访问的（2026-06-10）

- 中金公司 CICC: 521 Cloudflare
- 华润集团: 567 反爬
- 中国海外: 403 Cloudflare
- 字节跳动: 超时
- 中银/工银/人寿: 404 URL已变

---

## 猎聘中资搜索

用户已有猎聘账号，求职期望已设好：
- 方向: 产品经理/运营总监/数字化转型
- 地点: 香港首选+深圳其次
- 薪资: 25-45K×13

猎聘是中资岗位最佳聚合平台，建议定期登录查看推荐。
Agent 可通过 Gmail 推荐邮件获取猎聘岗位（如有订阅）。

---

## Pitfall

1. **中文公司名在 JobsDB API 不返回结果** — 必须用英文名搜索
2. **JobsDB 搜索结果包含第三方猎头** — 需过滤 `companyName` 是否匹配目标公司
3. **SPA 网站的 API 端点通常在 JS bundle 中** — 可以用 `browser_console` 查找，但每个站点不同
4. **中资很多岗位走内部渠道** — JobsDB/LinkedIn 覆盖有限，猎聘+微信公众号是补充
5. **不要尝试 curl 中资官网详情页** — 大部分有反爬保护
