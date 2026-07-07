# 中资/央企香港官网扫描结果 (2026-06-29 ~ 07-03)

> 来源：求职渠道全景图 Batch 1-3 扫描 + 07-03全量中资盘查

## 扫描状态总览

### 第一批（06-29 ~ 07-01）

| 公司 | 招聘URL | 状态 | 备注 |
|------|---------|------|------|
| 招商局集团 | cmhk.zhiye.com | ❌ SPA(北森) | 有海外招聘板块(BusinessType=4)，需手动访问 |
| 中银香港 BOCHK | bochk.pageuppeople.com/802 | ❌ 404/WAF | 网站已迁移，Incapsula+hCaptcha拦截 |
| 中银香港 BOCHK | bochk.pageuppeople.com | ❌ SAML认证 | 需要BOCHK内部AD FS认证 |

### 第二批全面中资盘查（07-03）

| 优先级 | 企业 | 方法 | 结果 | 匹配岗位 |
|--------|------|------|------|---------|
| 🥇 招商局集团 | cmhk.zhiye.com (北森) | ❌ SPA反爬 | LinkedIn/JobsDB均无匹配 |
| 🥇 华润集团 | LinkedIn搜"china resources" HK | 仅1结果：建材科技研发岗 | ❌ |
| 🥇 中远海运 | LinkedIn/JobsDB搜"cosco" | 无匹配管理岗 | ❌ |
| 🥇 **中国外运 Sinotrans** | **JobsDB公司搜索** | **14个在招岗位** | ✅ **市場經理（產品與營銷）** 37min前发布 |
| 🥇 中国移动香港 | LinkedIn搜 | 3个合约初级岗 | ❌ |
| 🥈 中国建筑国际 | 官网无公开入口 | — | ❌ |
| 🥈 华润置地/招商蛇口 | 地产行业BD/运营岗 | 公开渠道无匹配 | ❌ |
| 🥈 中旅集团/中国电信国际 | LinkedIn/JobsDB | 无匹配 | ❌ |
| 🥉 建银亚洲 | 银行行业壁垒确认 | 不推荐尝试 | ❌ |
| ❌ 中金/海通/国泰君安 | 金融PM硬门槛 | 不推荐尝试 | ❌ |
| ❌ 中石油/石化/电网 | 行业壁垒极高 | 不推荐尝试 | ❌ |

## 中国外运 Sinotrans — 唯一有实质收获的中资

**扫描方法：** JobsDB搜索 `Sinotrans OR 中远 OR 华润 OR 招商局` → 14个结果集中在Sinotrans

**高潜力岗位：**

| 岗位 | 发布 | 地点 | 薪资 | 匹配评估 |
|------|------|------|------|---------|
| **市場經理（產品與營銷）** | **37分钟前** | 青衣 | $25K+双薪+奖金 | ⚠️偏Marketing方向，需看JD判断。但物流行业+运营经验可迁移 |
| Sales Manager (Warehouse/Office Leasing) | 16日前 | 青衣 | — | ❌偏地产销售 |

**Sinotrans其他岗位：** HR/Admin/IT为主，均不匹配

**核心发现：** 中资企业最有效的扫描方式不是逐个官网访问（北森SPA+PageUp WAF），而是：
1. JobsDB搜公司名 → Sinotrans有14个结果
2. LinkedIn搜公司名 → 华润仅1个结果
3. Indeed搜公司名 → 华润物流34个基础岗

**策略结论：** 后续中资盘查用JobsDB/LinkedIn公司搜索替代官网爬取。官网SPA系统（北森/PageUp）不值得反复尝试。

## 核心策略建议

1. **不再逐个访问中资官网** — 北森/PageUp/WAF阻挡率100%，每次尝试浪费10+工具调用
2. **替代方案：JobsDB公司搜索 + LinkedIn公司搜索** — 用公司名称做关键词，已验证Sinotrans有效
3. **简职HK公众号仍是中资岗位最佳信息源** — 覆盖未在公开渠道发布的岗位
4. **P2已14个岗位全齐，建议优先投递** — 比新渠道开发产出更确定

## BOCHK Google Snippets提取的岗位 (2026-07-01)

从Google索引片段提取，链接已失效(404/WAF)：

| # | 岗位 | 部门 | 匹配度 |
|---|------|------|--------|
| 1 | Business Technology Manager (Sr Mgr/Mgr/AM) | IT Dept | ⚠️ 需核实 |
| 2 | Technical Lead & Application Development Manager | IT Dept | ❌ 偏技术 |
| 3 | Marketing Manager | 个人金融及财富管理部 | ❌ 不匹配 |
| 4 | (Senior) Technology Risk Manager (Cyber Security) | — | ❌ 技术安全 |
| 5 | (Senior) Technology Risk Manager (2nd line) | — | ❌ 风控 |
| 6 | Credit Control Manager | 个人银行风险部 | ❌ 银行风控 |
| 7 | Assistant Project Manager | Bank-wide Operation | ⚠️ 层级偏低 |
| 8 | Segment Manager (Cross Border) | — | ⚠️ 需核实 |
| 9 | Senior/Assistant Corporate Service Manager | — | ⚠️ 需核实 |
| 10 | Legal Counsel (PQE 4-6) | 法律合规部 | ❌ 法律 |

## 招商局网站结构

- 平台：北森(Beisen) zhiye.com
- PortalId: ad6df64e-8702-483f-a2ec-c44deefceec4
- 导航：首页 / 关于我们 / 社会招聘(BusinessType=1) / 校园招聘(2) / **海外招聘(4)** / 实习(3)
- 搜索支持：KeyWords(关键词) + LocId(地点)
- 反爬机制：SPA + API动态加载，curl返回HTML壳页面
