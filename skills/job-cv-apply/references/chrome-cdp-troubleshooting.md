# Chrome CDP 连接故障排查

> 2026-06-25 实操总结。Hermes browser 工具通过 CDP 接管已登录 Chrome 的调试经验。

## 启动命令

必须在 Win+R 或 PowerShell 中执行，**不能粘贴到浏览器地址栏**：

```
"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir=C:\Temp\chrome-cdp
```

## 验证连通

```bash
curl -s --connect-timeout 3 http://localhost:9222/json/version
```

返回 JSON = 通；exit code 28 (timeout) = 不通。

## 常见问题

### 1. browser_navigate 用的是 Browserbase，不是本地 Chrome

**症状**：`stealth_warning: "Running WITHOUT residential proxies"` 出现，页面显示未登录状态。

**原因**：`browser.cdp_url` 未设或设错。`engine: auto` 模式下 CDP 优先，但如果 cdp_url 为空会 fallback 到 Browserbase。

**修复**：
```bash
hermes config set browser.cdp_url 'http://localhost:9222'
```
或直接编辑 `~/.hermes/config.yaml`，设 `browser.cdp_url: 'http://localhost:9222'`。

### 2. WSL2 中 localhost:9222 不通

**原因**：WSL2 默认 NAT 网络，localhost 不直通 Windows。

**修复**：`C:\Users\<user>\.wslconfig` 加：
```ini
[wsl2]
networkingMode=mirrored
```
重启 WSL：`wsl --shutdown` 再重开。

### 3. CDP 端口突然断开

**症状**：之前通的，curl 突然超时。

**原因**：Chrome 被关闭或崩溃。

**修复**：重新用启动命令打开 Chrome。验证：`curl -s http://localhost:9222/json/version`。

### 4. 登录态丢失

**原因**：`--user-data-dir` 用了随机临时目录（如 `/tmp/xxx`），Chrome 重启后目录被清空。

**修复**：用固定路径 `C:\Temp\chrome-cdp`。首次启动需手动登录各平台 + 同步 Google 账号。

### 5. 页面状态与实际 Chrome 不同步

**症状**：browser_snapshot 显示的内容和用户 Chrome 看到的不同。

**原因**：browser 工具可能操作的是不同 tab。

**修复**：用 `browser_navigate` 刷新目标 URL 同步状态。

### 6. 用户要求 agent 帮忙输入密码登录

**规则**：不要做。用户分享的密码仅供用户自己登录，agent 不在 browser 工具中输入密码，不存入 memory/skill/任何文件。用户原话："不要帮我登录，我自己登录就好"。
