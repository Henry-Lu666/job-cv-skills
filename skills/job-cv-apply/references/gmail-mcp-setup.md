# Gmail MCP 授权设置指南

## 前置条件

- 一个 Gmail 账号
- Hermes Agent 已安装
- MCP 功能可用

## 授权方式：OAuth 2.0

### 步骤 1：Google Cloud Console 创建项目

1. 访问 https://console.cloud.google.com/
2. 创建新项目（或选择已有项目）
3. 进入 **API 和服务** → **凭据**
4. 点击 **创建凭据** → **OAuth 客户端 ID**
5. 应用类型选择 **桌面应用**
6. 下载 JSON 凭证文件，重命名为 `credentials.json`

### 步骤 2：启用 Gmail API

1. 在 Google Cloud Console 进入 **API 和服务** → **库**
2. 搜索 **Gmail API** 并启用

### 步骤 3：配置 OAuth 同意屏幕

1. 进入 **API 和服务** → **OAuth 同意屏幕**
2. 选择 **外部** 用户类型
3. 填写必填信息（应用名称、支持邮箱）
4. 添加测试用户（你的 Gmail 地址）
5. 添加作用域：`https://mail.google.com/`（读写全部邮件）
6. 发布应用（选择"测试中"即可）

### 步骤 4：配置 Hermes

将 `credentials.json` 放入 `~/.gmail-mcp/` 目录：

```bash
mkdir -p ~/.gmail-mcp
cp /path/to/credentials.json ~/.gmail-mcp/credentials.json
```

在 `~/.hermes/config.yaml` 中添加 MCP 配置：

```yaml
mcp_servers:
  gmail:
    autoApprove: []
    command: npx
    args:
      - -y
      - @gmail-mcp/gmail-mcp-server
    env:
      CREDENTIALS_PATH: ~/.gmail-mcp/credentials.json
      TOKEN_PATH: ~/.gmail-mcp/token.json
```

### 步骤 5：首次授权

启动 Hermes 时会自动触发 OAuth 授权流程：
1. 终端输出一个授权 URL
2. 在浏览器中打开该 URL
3. 使用你的 Gmail 账号登录并授权
4. 复制授权码回到终端粘贴

授权成功后，`~/.gmail-mcp/token.json` 会自动生成，后续不再需要手动授权。

## 注意事项

- Token 有效期通常为 7 天，过期后会自动刷新
- 如遇到授权错误，删除 `token.json` 重新授权
- 测试用户最多 100 人（测试阶段）
- 如果使用 Gemini/GWS 企业版，需联系管理员开启 API 访问

## 安全提醒

- `credentials.json` 和 `token.json` 包含敏感信息，不要提交到版本控制
- 建议在 `.gitignore` 中添加 `credentials.json` 和 `token.json`
- 定期检查 Google Cloud Console 中的 API 用量
