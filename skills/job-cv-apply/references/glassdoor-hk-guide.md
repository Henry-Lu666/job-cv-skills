# Glassdoor HK 注册与使用指南

## 注册流程

1. 打开 https://www.glassdoor.com.hk/index.htm
2. 点右上角 **Sign In** / **登入**
3. 选择注册方式（Google/Facebook一键关联，或邮箱注册）
4. 绑定 WhatsApp（用于 Job Alert 推送）
5. 填写求职偏好：Job Title + Location（Hong Kong）
6. **"贡献换访问"**（Get full access）— 必须选一项才能解锁公司评价和薪资数据
   - ✅ **推荐选 "Create a job alert"** — 最省事，不暴露个人信息
   - ❌ 不推荐：Review a company / Share a salary / Rate an interview — 需写具体内容，暴露个人信息
7. 填完后解锁 12 个月全站访问

## 注册后建议

- **Profile** → 上传简历 + 填写工作经历、教育背景
- **Jobs** → 搜索岗位，设置 Job Alert（WhatsApp 推送）
- **Companies** → 搜目标公司，看员工评价、面试流程、薪资范围

## Glassdoor 核心价值

| 功能 | 用途 |
|------|------|
| 公司评价（Reviews） | 匿名看员工真实评价，判断公司文化、管理层风格 |
| 薪资数据（Salaries） | 岗位薪资透明，谈判时有底气 |
| 面试经验（Interviews） | 看其他候选人的面试流程、问题、难度 |
| Job Alert | WhatsApp 自动推送新岗位 |

## 与 JobsDB 的配合

- **JobsDB** → 投递岗位（主力渠道）
- **Glassdoor** → 调研公司底细（薪资/评价/面试经验）
- 先在 JobsDB 看到感兴趣的岗位 → 去 Glassdoor 查公司 → 决定是否投递

## 自动化限制

- ❌ `browser_navigate` → Cloudflare "Humans only" 拦截
- ❌ curl → 同样被 Cloudflare 挡
- ✅ 只能用户手动在浏览器操作
- ❌ Glassdoor 链接 (`glassdoor.com.hk/partner/jobListing.htm`) → Cloudflare Security 页面，无法通过 curl/browser 获取 JD 全文
- Job Alert 推送通过 Gmail（`noreply@glassdoor.com`），可被 himalaya 扫描

## Gmail 扫描 Glassdoor 推送（2026-06-12 验证）

Glassdoor 的 Job Alert 同时发到 Gmail 和 WhatsApp。Gmail 版可通过 himalaya 扫描：

```bash
# 列出所有 Glassdoor 邮件
himalaya envelope list --page-size 50 --output json 2>/dev/null | python3 -c "
import sys, json
raw = sys.stdin.read()
start = raw.find('[')
if start < 0: sys.exit(0)
for e in json.loads(raw[start:]):
    sender = e.get('from', {})
    addr = sender.get('addr','') if isinstance(sender, dict) else str(sender)
    if 'glassdoor' in addr.lower():
        print(f\"{e['id']}|{addr}|{e.get('subject','')}|{e.get('date','')}\")
"
```

### 邮件结构

- **发件人**: `noreply@glassdoor.com`（岗位推送）/ `info@glassdoor.com`（营销邮件，忽略）
- **Subject 格式**: `"{Job Title} at {Company} and N more jobs in Hong Kong for you. Apply Now."`
- **Body**: HTML，包含多个岗位卡片，每个有：公司名、岗位名、地点、薪资（如有）、发布天数、Glassdoor 链接
- **去重**: 同一批岗位会在连续多天的邮件中重复推送（如 06-10、06-11、06-12 推同一批），按 `jobListingId` 去重

### ⛔ Pitfall: Glassdoor Alert 关键词必须匹配求职方向

用户注册时设置的 alert 关键词是 `"Machine Learning Engineer"`，导致推送全是纯技术岗（ML Engineer、AI Engineer、Quant Analyst），与甜蜜区（BD/AI落地推行/变革管理）完全不匹配。

**必须调整为**：
- `Business Development Manager`
- `Partnership Manager`
- `Operations Director`
- `Digital Transformation`
- `AI Adoption` / `Change Enablement`

**调整方法**: Glassdoor 网站 → Jobs → Job Alerts → Edit

### ⛔ Pitfall: Glassdoor 链接无法抓取 JD 全文

Glassdoor 的 `partner/jobListing.htm` 链接被 Cloudflare 拦截，无法获取 JD 全文。

**替代方案**:
1. **公司官网**: 如 AWS → `amazon.jobs`，Arup → `arup.com/careers`，直接搜岗位名
2. **LinkedIn**: 搜 "岗位名 + 公司名 + Hong Kong"，LinkedIn guest view 通常有 JD
3. **Indeed/其他**: 作为 fallback
4. **用户手动**: 让用户在浏览器打开 Glassdoor 链接手动复制 JD

### ⛔ Pitfall: 猎头发布的岗位 JD 更难获取

Ignite Recruitment 等猎头在 Glassdoor 发布的岗位（如 "AI Software Engineer - Strategic Office - TopTier MNC"），通常：
- 不在 LinkedIn 上发布
- 猎头官网无公开岗位列表
- 搜索引擎被 CAPTCHA 拦截
→ **建议直接跳过**，除非用户手动提供 JD

## Profile 技能列表建议

与 JobsDB/LinkedIn 一致：
- Operations Management, Business Development, Team Leadership
- Digital Transformation, AI, NLP, Data Analytics
- Key Account Management, Sales Strategy, SOP Design

## 语言设置

- 普通话: Native / 母語
- 英语: Professional Working / 良好工作能力
- 粤语: Conversational (Basic) / 基础会话
