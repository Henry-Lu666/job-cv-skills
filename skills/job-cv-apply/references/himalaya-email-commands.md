# Himalaya 邮箱命令参考

> 当 `gmail_job_scanner.py` 超时或不可用时，用 himalaya CLI 直接操作邮箱。

## 前置条件

- himalaya 已安装: `~/.local/bin/himalaya`
- Gmail IMAP 已配置: `~/.config/himalaya/config.toml`

## 常用命令

### 列出收件箱邮件

```bash
# 纯文本格式（人读）
~/.local/bin/himalaya envelope list --folder INBOX --page-size 30

# JSON格式（程序解析）
~/.local/bin/himalaya envelope list --folder INBOX --page-size 50 --output json
```

**JSON字段说明**:
- `id`: 邮件ID（数字），用于后续读取
- `from`: **dict类型** `{"name": "显示名", "addr": "邮箱地址"}`，不是字符串
- `subject`: 邮件主题
- `date`: 日期字符串，如 `"2026-06-18 08:57+00:00"`

### 读取邮件内容

```bash
# 读取指定ID的邮件
~/.local/bin/himalaya message read <ID>

# 示例：读取ID=844的邮件
~/.local/bin/himalaya message read 844
```

**输出格式**: 包含 From/To/Subject 头部 + HTML/纯文本正文。正文在 `<#part type=text/html>` 和 `<#/part>` 之间。

### 搜索特定公司/岗位的邮件

```python
# Python解析模式（在execute_code或terminal中）
import json, subprocess

result = subprocess.run(
    ["~/.local/bin/himalaya", "envelope", "list", "--folder", "INBOX", 
     "--page-size", "100", "--output", "json"],
    shell=True, capture_output=True, text=True, timeout=30
)

# 跳过WARN行，找到JSON开始位置
json_start = result.stdout.find("[")
if json_start != -1:
    envelopes = json.loads(result.stdout[json_start:])
    
    # 搜索特定公司
    target = "hsbc"
    for e in envelopes:
        subj = e.get("subject", "") if isinstance(e.get("subject"), str) else ""
        frm = str(e.get("from", ""))  # from是dict，必须str()
        if target in (subj + frm).lower():
            print(f"ID: {e['id']}, Subject: {subj}, Date: {e.get('date','')}")
```

### 按关键词过滤邮件

```bash
# 用himalaya搜索功能（如果支持）
~/.local/bin/himalaya envelope list --folder INBOX --page-size 100 --output json 2>/dev/null | \
  python3 -c "
import json, sys
data = json.load(sys.stdin)
keywords = ['hsbc', 'hang seng', '恒生', '汇丰', 'interview', 'offer', 'unfortunately', 'regret']
for e in data:
    subj = e.get('subject','') if isinstance(e.get('subject'), str) else ''
    frm = str(e.get('from',''))
    text = (subj + frm).lower()
    if any(kw in text for kw in keywords):
        print(f\"ID:{e['id']} | {e.get('date','')} | {subj[:60]}\")
"
```

## 求职反馈邮件识别关键词

### 积极信号
- interview, shortlisted, next step, moving forward, offer, congratulat
- 面试, 复试, 进入下一轮, 初筛通过, 录用, 邀请

### 拒绝信号
- unfortunately, regret, not moving forward, other candidates, not selected
- 很遗憾, 未能进入, 不合适, 暂不考虑, 已招满

### 已知求职相关发件人
linkedin, jobsdb, indeed, hsbc, hang seng, 恒生, prudential, aia,
manulife, morgan mckinley, hays, robert walters, randstad,
recruit, hazel, recruitment, hr@, careers@, talent@,
noreply@e.jobsdb.com, jobalerts@linkedin.com, noreply@mail.apply.careers.hsbc.com

## Pitfalls

1. **`from`字段是dict不是字符串** — 直接拼接`e['from']`会TypeError。必须用`str(e.get('from',''))`或分别取`e['from']['addr']`。

2. **himalaya输出可能包含WARN行** — JSON解析前需跳过非JSON行。用`output.find("[")`定位JSON开始位置。

3. **邮件ID是会话级的** — 不同的himalaya调用可能返回不同ID。每次操作前重新获取ID列表。

4. **page-size限制** — 默认只返回10-30封邮件。查历史邮件需设`--page-size 100`或更大。
