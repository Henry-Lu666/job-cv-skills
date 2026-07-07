# LinkedIn JD 提取方法

## curl + Python 提取（推荐，无需登录）

LinkedIn 公开职位页（`/jobs/view/{id}`）可以在无登录状态下抓取 JD 全文。JobsDB 有 Cloudflare 保护，无法用此方法。

### 命令

```bash
curl -s -L -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36" \
  "https://www.linkedin.com/jobs/view/{JOB_ID}" 2>/dev/null | python3 -c "
import sys, re
html = sys.stdin.read()
match = re.search(r'<div class=\"show-more-less-html__markup[^\"]*\">(.*?)</div>', html, re.DOTALL)
if match:
    text = re.sub(r'<[^>]+>', '', match.group(1))
    print(text.strip()[:3000])
else:
    print('NO_JD_FOUND (html_len={})'.format(len(html)))
"
```

### 批量提取

```bash
for id in 4424500009 4400480942 4418580746; do
  echo "=== $id ==="
  curl -s -L -H "User-Agent: Mozilla/5.0 ..." "https://www.linkedin.com/jobs/view/$id" | python3 -c "..."
  echo ""
done
```

### 注意事项

- **成功率**：~80%。部分岗位需要登录或被反爬拦截（返回空HTML或login页面）
- **HTML结构**：JD在 `<div class="show-more-less-html__markup ...">` 内
- **JobsDB**：Cloudflare Turnstile 保护，curl 会被拦截（返回 5675 字节的 challenge 页面）
- **子Agent限制**：delegate_task 的子Agent可能没有 terminal 工具，无法执行 curl。JD 提取应在主 Agent 中执行
- **速率控制**：批量抓取建议每个请求间隔 1-2 秒，避免被 LinkedIn 限速

### 已验证提取成功的岗位ID

| 日期 | 岗位ID | 公司 | 结果 |
|------|--------|------|------|
| 2026-06-10 | 4424500009 | Alexis Services | ✅ 完整JD |
| 2026-06-10 | 4400480942 | Crypto.com | ✅ 完整JD |
| 2026-06-10 | 4399116815 | Adecco | ✅ 完整JD |
| 2026-06-10 | 4409666648 | Gate | ✅ 完整JD |
| 2026-06-10 | 4419027570 | Pinpoint Asia | ✅ 完整JD |
| 2026-06-10 | 4396834648 | Great Eagle | ✅ 完整JD |
| 2026-06-10 | 4418283071 | Recruit Squad | ✅ 完整JD |
| 2026-06-10 | 4331153006 | Jockey Club | ✅ 完整JD |
| 2026-06-10 | 4423903504 | HKT | ✅ 完整JD |
| 2026-06-10 | 4422332506 | Prudential | ✅ 完整JD |
| 2026-06-10 | 4403943382 | Amadeus | ✅ 完整JD |
| 2026-06-10 | 4422373513 | Hays (AI) | ✅ 完整JD |
| 2026-06-10 | 4423841667 | TakeX | ✅ 完整JD |
| 2026-06-10 | 4324666393 | Binance | ✅ 完整JD |
| 2026-06-10 | 4424625813 | Horizon Tech | ✅ 完整JD |
| 2026-06-10 | 4425963968 | HashKey | ✅ 完整JD |
| 2026-06-10 | 4418580746 | 中金公司 | ❌ 未提取到 |
| 2026-06-10 | 4418872781 | Ras Al-Khaimah | ❌ 未提取到 |
