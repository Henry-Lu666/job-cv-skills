# CDP Browser 求职站点巡检流程

> 适用场景：求职监控Agent（cron job）、手动CDP巡检
> 更新日期：2026-07-06
> 背景：用户反复纠正——必须从"找工作"书签栏打开站点，不得手动导航到登录页

## 🔴 第一原则

**Chrome CDP profile (`C:\Temp\chrome-cdp`) 的"找工作"书签夹已存所有站点密码。**
**唯一操作：点书签 → 等页面加载 → 读内容 → 关Tab。** 不做任何登录操作。

## 巡检顺序

| 序号 | 站点 | 书签URL | 检查内容 |
|------|------|---------|---------|
| 1 | JobsDB | hk.jobsdb.com | 新消息、申请状态变更 |
| 2 | LinkedIn | linkedin.com/feed | InMail、申请反馈、新推荐 |
| 3 | 猎聘 | c.liepin.com | 新岗位推送、消息 |
| 4 | 劳工处 | www2.jobs.gov.hk | 最新职位推荐 |
| 5 | OfferToday | offertoday.com/hk/recommend | 推荐岗位列表 |
| 6 | BOSS直聘 | zhipin.com | 沟通状态、新消息 |
| 7 | Manulife Workday | manulife.wd3.myworkdayjobs.com | 申请状态 |
| 8 | LexisNexis Workday | relx.wd3.myworkdayjobs.com | 申请状态 |

## 执行步骤

### Step 0: 检查CDP是否在线
```bash
curl -s http://localhost:9222/json/version
```
- 失败 → 跳过所有浏览器步骤，只做Gmail通道
- 成功 → 继续

### Step 1: 逐个巡检（循环）
``` 
for each site in bookmarks:
    browser_navigate(bookmark_url)   # 必须用书签URL，不是手动输入
    wait page loaded (3-5s)
    browser_snapshot                  # 检查页面内容
    check for new messages/updates
    close tab
```

### Step 2: 如有新通知
- 截图保存证据
- 在报告中标注具体的通知内容

### Step 3: 补充Gmail通道
- 用Gmail MCP搜索求职相关邮件
- 交叉比对投递追踪表

## 常见错误（避免！）

1. ❌ 手动输入 `https://hk.jobsdb.com` → 走到登录页
   ✅ 从书签栏打开已存密码的URL

2. ❌ CDP离线时强行走浏览器步骤 → 报错浪费时间
   ✅ 离线就跳过，只做Gmail

3. ❌ 填登录表单/点登录按钮
   ✅ 密码已存，不需要任何登录操作
