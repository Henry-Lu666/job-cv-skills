# CDP (Chrome DevTools Protocol) 设置指南

## 用途

通过 CDP 远程控制 Chrome 浏览器，实现：
- 自动登录求职站点并检查通知
- 抓取 JD 内容
- 检查邮件
- 监控投递状态

## 方案 A：专用 CDP Chrome 配置文件（推荐）

使用独立的 Chrome 用户数据目录，与日常使用的浏览器隔离。

### Windows 启动命令

```bash
"C:\Program Files\Google\Chrome\Application\chrome.exe" ^
  --remote-debugging-port=9222 ^
  --user-data-dir="C:\Temp\chrome-cdp"
```

### WSL/Linux 启动命令

```bash
google-chrome --remote-debugging-port=9222 \
  --user-data-dir=/tmp/chrome-cdp \
  --no-first-run \
  --no-default-browser-check
```

### macOS 启动命令

```bash
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --remote-debugging-port=9222 \
  --user-data-dir=/tmp/chrome-cdp \
  --no-first-run
```

## 方案 B：附加到现有 Chrome

如果你已经有一个 Chrome 实例在运行：

### Windows

1. 关闭所有 Chrome 窗口
2. 右键 Chrome 快捷方式 → 属性 → 目标后面加上：
   ```
   --remote-debugging-port=9222
   ```
3. 通过该快捷方式启动 Chrome

### macOS/Linux

```bash
# 先关闭所有 Chrome 进程
killall chrome

# 启动带调试端口的 Chrome
google-chrome --remote-debugging-port=9222
```

## 验证是否成功

Chrome 启动后，在终端运行：

```bash
curl http://localhost:9222/json/version
```

返回 JSON 格式的浏览器信息即表示成功。

## 常见问题

### 端口被占用

```bash
# 查看谁占用了 9222 端口
netstat -ano | findstr :9222  # Windows
lsof -i :9222                  # macOS/Linux

# 更换端口（修改 config.yaml 中的端口号）
```

### 连接失败

1. 确认 Chrome 以 `--remote-debugging-port` 参数启动
2. 检查防火墙是否拦截了 9222 端口
3. 如果使用 WSL2，Windows 端 Chrome 需要允许来自 WSL 的连接

### Chrome 版本兼容性

CDP 协议随 Chrome 更新而更新。建议：
- 保持 Chrome 自动更新
- 如遇到协议变更错误，升级 Hermes Agent

## Hermes 配置

在 `~/.hermes/config.yaml` 中：

```yaml
browser:
  cdp_url: http://localhost:9222
  dialog_policy: must_respond
  dialog_timeout_s: 300
```

## 安全建议

- 使用专用 Chrome 配置文件（方案 A），避免影响日常浏览器数据
- 在 CDP Chrome 中仅登录求职相关网站
- 不要在 CDP Chrome 中登录个人银行/支付等敏感账户
- 关闭 CDP Chrome 后，进程会自动终止
