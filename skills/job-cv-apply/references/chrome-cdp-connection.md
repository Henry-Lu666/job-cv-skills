# Chrome CDP 连接 — Hermes 接管已登录 Chrome（2026-06-25 实操验证）

> 用途：让 Hermes browser 工具操作用户已登录的 Chrome，跳过 LinkedIn/JobsDB 等登录墙。

## 技术原理

Chrome DevTools Protocol (CDP)。Chrome 以 `--remote-debugging-port=9222` 启动后暴露调试接口，
Hermes 通过 CDP 连接，操作的就是用户的真实 Chrome（含所有 cookie/登录态/密码填充）。

## 启动步骤（Windows 端）

### 1. 关闭所有 Chrome 窗口

必须完全关闭，否则 `--remote-debugging-port` 不生效。

### 2. 启动 Chrome

**方法 A：Win+R（推荐）**

按 `Win+R`，粘贴以下命令，回车：
```
"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir=C:\Temp\chrome-cdp
```

**方法 B：PowerShell**
```powershell
& "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir=C:\Temp\chrome-cdp
```

**方法 C：桌面快捷方式（一次性创建）**
- 右键桌面 → 新建 → 快捷方式
- 目标: `"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir=C:\Temp\chrome-cdp`
- 命名: "Chrome CDP"

### 3. 首次使用：同步登录态

首次用 `--user-data-dir=C:\Temp\chrome-cdp` 启动时是空白 profile：
1. 登录 Google 账号 → 同步书签、密码、扩展
2. 手动登录 LinkedIn、JobsDB 等常用求职网站
3. 后续启动同一 `--user-data-dir` 路径，登录态自动保留

### ⚠️ 关于 `--user-data-dir`

| 配置 | 效果 |
|------|------|
| 不加 `--user-data-dir` | 使用系统默认 profile（所有登录态保留） |
| `--user-data-dir=C:\Temp\chrome-cdp` | 使用固定路径 profile（首次需登录，后续保留） |
| `--user-data-dir=<随机临时目录>` | ❌ 每次空白，登录态丢失 |

**建议用固定路径** `C:\Temp\chrome-cdp`，好处是隔离了调试浏览器和日常浏览器的 profile，避免调试操作污染日常浏览数据。

## WSL / Hermes 端

### 验证 CDP 连通

```bash
curl -s http://localhost:9222/json/version
```

应返回 Chrome 版本和 WebSocket URL。如果超时：
- 确认 Chrome 已以 `--remote-debugging-port=9222` 启动
- WSL2 需要 `.wslconfig` 中配置 `networkingMode=mirrored`（让 localhost 直通 Windows）
- 或用 Windows IP：`curl -s http://$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}'):9222/json/version`

### 配置 Hermes

在 `~/.hermes/config.yaml` 中设置：
```yaml
browser:
  cdp_url: 'http://localhost:9222'
```

### 连接并使用

```
/browser connect
```

连接后，`browser_navigate`、`browser_click` 等工具直接操作用户 Chrome。

## 已知 Pitfalls

### P1: 输入命令到浏览器地址栏而非终端

用户曾将整个 Chrome 启动命令粘贴到浏览器地址栏，导致 DNS 错误。
**正确做法**：`Win+R` 或 PowerShell 中执行。

### P2: browser 工具显示状态与实际 Chrome 不一致

CDP 连接后，browser 工具可能控制 Chrome 中的一个标签页，但用户在看另一个标签页。
可能出现：browser 工具显示 "Sign in"，但用户实际 Chrome 已登录。

**解决**：`browser_navigate` 刷新目标页面，browser 工具会同步到最新状态。

### P3: LinkedIn 登录需要 Google 密码填充

LinkedIn 通过 Google 登录时，Chrome 的密码管理器会自动填充。
但如果用的是新 profile（`--user-data-dir=C:\Temp\chrome-cdp`），需先同步 Google 密码。
首次同步后，后续登录自动填充。

### P4: JobsDB Cloudflare 拦截在 CDP 模式下解除

普通 `browser_navigate`（Browserbase）访问 JobsDB 触发 CF 验证。
CDP 连接用户 Chrome 后，CF 不再拦截（因为用的是真实浏览器指纹+已有 cookie）。

### P5: CDP 端口断开后需重启 Chrome

如果 `curl localhost:9222/json/version` 超时，说明 Chrome 已关闭或 CDP 端口失效。
需重新以 `--remote-debugging-port=9222` 启动 Chrome。

### P6: stealth_warning 可忽略

browser 工具返回中可能包含 `"stealth_warning": "Running WITHOUT residential proxies"`，
这是 Browserbase 的通用提示，在 CDP 模式下**无意义**，可忽略。判断是否真正连接成功，
看页面标题和内容，不看这个字段。

## 求职场景价值

| 场景 | 无 CDP | 有 CDP |
|------|--------|--------|
| LinkedIn 投递 | ❌ 登录墙 | ✅ 直接操作 |
| JobsDB 核实 | ❌ Cloudflare 拦截 | ✅ 正常访问 |
| 申请表填写 | ❌ 需手动 | ✅ 自动填写（含密码填充） |
| Glassdoor | ❌ 需登录 | ✅ 直接访问 |

## 代码位置

- `tools/browser_tool.py` — `_get_cdp_override()` CDP URL 解析
- `tools/browser_cdp_tool.py` — `browser_cdp` 原始 CDP 命令工具
- `hermes_cli/browser_connect.py` — CDP 连接核心逻辑（如存在）
