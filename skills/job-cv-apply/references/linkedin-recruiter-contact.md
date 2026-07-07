# LinkedIn 招聘官联系流程

## 触发场景
用户已通过LinkedIn快速申请投递，想补充Cover Letter或跟进时。

## 查找招聘官
1. 用登录态浏览器打开LinkedIn岗位页 `https://www.linkedin.com/jobs/view/{ID}`
2. 页面右侧会显示"Posted by {Name}" — 那就是recruiter/hiring manager
3. Guest curl无法获取此信息（LinkedIn需登录）

## 不要做的事
- ❌ 不要用delegate_task去搜（会卡200+秒）
- ❌ 不要用Google搜"ByteDance recruiter LinkedIn"（Google+LinkedIn组合反爬严格）
- ❌ 不要建议用户发邮件补CL（ATS系统回执邮箱不接收附件）

## 正确流程
1. 告诉用户在LinkedIn登录态打开链接
2. 找到recruiter名字后，点Connect
3. 在Connect附言中写简短自我介绍（3-4句）
4. 如果有InMail选项，用更正式的版本

## 消息模板（英文，短版Connect附言）

```
Hi [Name], I recently applied for the [Role] at [Company]. With [N] years of [核心经验] plus an MSc in Applied AI, I'm excited about this opportunity. Would love to connect!
```

## 消息模板（英文，长版InMail）

```
Subject: [Role] Application

Hi [Name],

I recently applied for the [Role] at [Company] through LinkedIn and wanted to briefly introduce myself directly.

I bring [N] years of [核心经验] — [1-2句具体成就]. Combined with my MSc in Applied AI (ongoing, HK), I bridge [JD核心需求1] with [JD核心需求2].

I'm particularly excited about [公司/方向specific] and would welcome the chance to discuss.

Best regards,
[Full Name]
```

## 消息模板（中文版，recruiter是中文名时）

```
[姓名]您好，

我刚通过LinkedIn申请了[公司]的[岗位]一职，冒昧直接联系。

我有[N]年[行业]BD与运营管理经验，曾[核心成就]。目前正在香港攻读应用人工智能硕士，能够将业务策略与AI落地结合。

非常期待[方向]的机会，希望能进一步沟通。

此致
[姓名]
```

## 关键原则
- 短 > 长（Connect附言限300字符，InMail也别超200词）
- 数据 > 形容词（"12年经验" > "丰富的经验"）
- 不要附简历（LinkedIn Connect不支持附件）
- 如果对方7天没回复，不要重复加——LinkedIn会标记spam
