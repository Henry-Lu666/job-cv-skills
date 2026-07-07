# Browser Connect for Job Applications

> 2026-06-25 验证

## 问题

LinkedIn/JobsDB 等求职网站需要登录态才能：
- 投递简历（LinkedIn Apply 弹登录墙）
- 查看完整 JD（JobsDB 被 Cloudflare 拦截）
- 填写申请表（自动填充已有信息）

Hermes 内置的 `browser_navigate` 使用独立浏览器实例（无 cookie），无法访问已登录的网站。

## 解决方案：`/browser connect`（CDP）

Hermes 内置 `/browser connect` 命令，通过 Chrome DevTools Protocol (CDP) 连接用户已登录的 Chrome。

### 操作步骤（Windows + WSL2）

**Step 1: 关闭所有 Chrome 窗口**

**Step 2: 用调试模式重启 Chrome**
```powershell
# PowerShell（保留所有登录态和 cookie）
& "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222
```
- 不加 `--user-data-dir` → 使用默认 profile → 所有登录态保留
- 加了 `--user-data-dir` → 创建新 profile → 无登录态（不要这样做）

**Step 3: 在 Hermes CLI 中连接**
```
/browser connect
```

**Step 4: 验证**
```
/browser status
```

### WSL2 网络注意

WSL2 中 `localhost:9222` 可能无法到达 Windows Chrome。解决方案：

```bash
# 方法 1: 检查 WSL2 网络模式
cat /etc/resolv.conf | grep nameserver
# 如果输出是 Windows IP（如 172.x.x.x），用这个 IP
export BROWSER_CDP_URL="http://172.x.x.x:9222"

# 方法 2: 如果启用了 mirrored networking（.wslconfig）
# localhost 直接可用，不需要额外配置
```

Windows 防火墙可能需要放行 9222 端口入站。

## 技术细节

- Hermes 源码: `hermes_cli/browser_connect.py` + `tools/browser_tool.py`
- 默认 CDP 端口: 9222
- 连接后 `BROWSER_CDP_URL` 环境变量被设置
- 所有 `browser_*` 工具自动使用已连接的 Chrome
- `/browser connect` 支持自定义 URL: `/browser connect ws://host:port/devtools/browser/xxx`

## 局限

- Chrome 必须在 Windows 上运行（WSL2 中无 GUI Chrome 需要额外配置）
- 同一时间只能有一个 CDP 连接
- Chrome 关闭后连接断开，需要重新启动调试模式
