# Gmail MCP + 163 IMAP 双邮箱求职扫描工作流

> 2026-06-25 验证：Gmail MCP OAuth完成，子agent全面扫描测试成功（100+邮件，14封深度读取，158s）
> 2026-07-06 补充：agent 全量接管 Gmail + 163，统一分类/处理/报告

---

## 双邮箱架构

```
每小时 cron 任务
    │
    ├── Gmail MCP（MCP OAuth）
    │   ├── mcp_gmail_search_emails() 搜索未读
    │   ├── mcp_gmail_read_email() 读正文
    │   ├── LLM 分类（面试/拒绝/状态更新/通知/其他）
    │   └── mcp_gmail_modify_email(removeLabelIds=["UNREAD"]) 标记已读
    │
    └── 163 IMAP（Python imaplib 脚本）
        ├── imap.163.com:993 + 授权码登录
        ├── 拉取未读邮件 → LLM 分类（与 Gmail 同一引擎）
        └── imap.store(mid, "+FLAGS", "\\Seen") 标记已读
```

Gmail MCP 和 163 IMAP 共用同一个 LLM 分类引擎，输出合并报告。
163 IMAP 方案详见 `references/163-email-imap-setup.md`。

---

> 2026-06-25 验证：Gmail MCP OAuth完成，子agent全面扫描测试成功（100+邮件，14封深度读取，158s）

## 为什么用 MCP 而不是 himalaya/脚本

| 维度 | himalaya + 脚本 | Gmail MCP + 子agent |
|------|-----------------|---------------------|
| 邮件正文 | `himalaya message read <ID>` 需要先list再read | `mcp_gmail_read_email(messageId)` 一步到位 |
| 搜索 | IMAP语法（小写，有限） | Gmail原生查询语法（full power） |
| 解析 | 脚本硬编码正则，格式变了就崩 | 子agent智能理解任意格式 |
| 猎头识别 | 关键词匹配，大量误标 | LLM理解上下文，精准分类 |
| 新岗位提取 | 只能提取预定义模板 | 任意格式的推荐邮件都能提取 |
| 维护成本 | 脚本需持续更新正则 | 零维护 |

**结论**：Gmail MCP可用时，优先用MCP+子agent模式。himalaya/脚本作为备用。

## 子agent委托模式（2026-06-25验证）

### 委托方式

```
delegate_task(
  goal="全面扫描Gmail求职相关邮件...",
  toolsets=["mcp_gmail_search_emails", "mcp_gmail_read_email", "mcp_gmail_list_email_labels"]
)
```

### 搜索关键词策略（9组，覆盖全面）

子agent应分批搜索以下关键词（每组一次 search_emails 调用）：

1. **投递反馈**: `"application"`, `"position"`, `"opportunity"`
2. **面试/录用**: `"interview"`, `"resume"`, `"CV"`, `"hiring"`
3. **拒信信号**: `"reject"`, `"unfortunately"`, `"congratulations"`, `"offer"`
4. **求职平台**: `"LinkedIn"`, `"JobsDB"`, `"Glassdoor"`, `"Indeed"`
5. **特定公司**: 已投公司名列表（从追踪表提取）
6. **猎头关键词**: `"recruitment"`, `"headhunter"`, `"talent"`
7. **订阅摘要**: `"more jobs"`, `"职位订阅"`, `"new jobs"`
8. **确认邮件**: `"received your application"`, `"thank you for applying"`
9. **中文系统邮件**（🚨 必加，不可遗漏）: `"申请"`, `"拒绝"`, `"退回"`, `"您的申请"`

⚠️ **致命陷阱：LinkedIn中文系统邮件用中文标题。** LinkedIn向中国用户发送的拒绝/状态更新邮件，subject是中文「您的申请: XX公司 - 岗位」。如果只搜英文关键词(application/reject)，这封邮件**永远搜不到**。中文关键词"申请""拒绝""退回"必须出现在subject搜索条件中。

每组用 `maxResults=10`，去重后逐封读取正文。

### 输出格式要求

子agent必须输出结构化报告，包含：
1. 🔴 拒信 — 公司、日期、拒信原文摘要
2. 🟢 积极反馈 — 面试邀请、评估邀请、offer
3. 🔵 猎头联系 — 排除已知平台域名后的真正猎头
4. 📨 申请确认 — 确认投递到达
5. ⚡ 状态更新 — 简历被查看、流程推进等
6. 📋 职位推荐 — 从digest邮件提取的每个岗位

### 主agent检查要点

- [ ] 子agent是否读了邮件正文（不只看subject）
- [ ] 新发现的岗位是否已去重追踪表
- [ ] 状态变更是否需要更新追踪表
- [ ] 积极反馈是否需要用户立即行动
- [ ] 猎头判断是否排除了平台自动邮件

## 经典搜索查询示例

```
# 最近7天收件箱
query: "in:inbox newer_than:7d"

# 特定公司
query: "from:hire.lever.co newer_than:14d"

# LinkedIn推荐
query: "from:jobalerts-noreply.linkedin.com newer_than:7d"

# JobsDB推荐
query: "from:noreply@e.jobsdb.com newer_than:7d"

# 拒信信号
query: "newer_than:14d (unfortunately OR regret OR decided to pursue)"

# 面试邀请
query: "newer_than:14d (interview OR meeting OR schedule OR assessment)"
```

## 注意事项

1. **Gmail搜索语法不支持 `from:` 带域名** — 用 `"from:linkedin.com"` 可能不生效，改用发件人关键词
2. **maxResults默认20** — 求职扫描建议设10-15（每组），避免单次返回过多
3. **read_email返回的body是纯文本** — HTML邮件会被自动转为文本
4. **7天有效期** — OAuth token 7天过期，cron每天10:00检查（cron id=2168dd328fb2）
5. **子agent无追踪表记忆** — 必须在goal中传入已知投递列表用于去重
6. **🚨 处理完必须标记已读** — 对已读取并分类的邮件（拒绝/面试/状态更新），必须调用 `mcp_gmail_modify_email(messageId, removeLabelIds=["UNREAD"])` 移除未读标签。否则用户自己打开邮箱还是看到一堆未读邮件，体验极差。注意只标记你已处理完的邮件，不要无差别标记所有搜索结果。
