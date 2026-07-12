---
name: job-cdp
description: Gmail监控 + CDP多平台监控 — 邮箱岗位日报、CDP自检、求职站点通知扫描、OAuth管理。
author: Henry Lu
version: 2.0.0
license: MIT
platforms: [linux, macos, windows]
---

# 求职CDP与Gmail监控

> 自动化求职站点的通知监控和Gmail岗位邮件扫描。

---

## Gmail监控系统

**工具**: Gmail MCP（Google OAuth认证）
**功能**: 自动扫描求职相关邮件、提取岗位推荐、去重追踪表

### 邮件扫描工作流

1. 用MCP搜索最近7天的求职相关邮件
2. 识别推荐邮件（LinkedIn/JobsDB/Glassdoor/Indeed等平台的职位推送）
3. 提取每个岗位为独立记录
4. 与追踪表查重
5. 新岗位进入L2核实流程

### 邮件处理后的清理

扫描/读取邮件后，应批量移除UNREAD标签，保持收件箱与处理状态同步。

---

## Cron输出手机适配标准

所有推送至飞书/即时通讯平台的cron任务，输出格式应遵守：

```
📱 手机阅读适配：
- 用 **粗体** 分段，不用线框字符
- 用 • 无序列表，每项一行
- 结论/变化放最前面
- 单行不超过25汉字/35英文字符，公司名用简称
- 岗位名用10字内缩写
- 不用表格
- 总输出控制在25行/500字内
```

### 弹性间隔 vs 固定时间

输出型daily cron统一用弹性间隔（`every 24h`），避免固定时间cron在agent断线时连续错过。监控/检查类cron（OAuth过期、健康巡检）保留固定时间。

---

## CDP（Chrome DevTools Protocol）监控

### CDP的正确打开方式

**两步法：**
1. **从书签栏导航** — CDP Chrome的求职书签文件夹存了所有平台的已登录URL
2. **需要登录时** — Chrome密码管理器已保存密码，点击登录按钮自动填充

**反模式：** ❌ Python websockets createTarget ❌ browser_navigate高频连调用 ❌ CDP自动化OAuth

### CDP故障自检

```bash
# 一条命令自检CDP连通性+配置
curl -s --connect-timeout 3 http://localhost:9222/json/version | head -1
```

- curl返回JSON = CDP端口通
- curl超时 = Chrome没启动
- 检查config.yaml中browser.cdp_url是否配置

### 平台清单与能力

| 平台 | CDP登录态 | 可自动化操作 |
|------|-----------|------------|
| LinkedIn | ✅ 已验证 | 搜岗位、抓JD（需CDP WebSocket导航已登录tab） |
| JobsDB | ✅ 已验证 | 搜岗位、抓JD |
| Indeed | ✅ 已验证 | 搜岗位、抓JD（仅搜索页） |
| Glassdoor | ✅ 已验证 | 搜岗位、查评价 |
| CTgoodJobs | ✅ 已验证 | 搜岗位、抓JD |
| 猎聘 | ✅ 已验证 | 搜岗位、抓JD |
| 劳工处 | 不需要登录 | 搜岗位 |

### CDP扫描工作流（Stage 1扩展）

```
CDP多平台扫描:
1. 确认CDP连通
2. 先扫各平台通知铃/推荐栏—AI推荐的岗位可能比关键词搜索更精准
3. 按优先级串行扫描（防限流）:
   a. LinkedIn—搜甜蜜区关键词+通知铃
   b. JobsDB—搜关键词+首页推荐
   c. Indeed—搜关键词
   d. CTgoodJobs—搜关键词
   e. 猎聘—搜香港相关岗位
4. 每个平台提取岗位列表→去重追踪表
5. 标注来源平台
6. 新岗位进入L2核实流程
```

### CDP扫描注意事项

- **只能从"找工作"书签栏打开站点**——密码已保存在CDP Chrome profile中
- 不要用browser_click点击搜索结果（会创建新tab导致操作在错误页面）
- 每个平台3次调用预算：navigate + getTargets + evaluate
- **通知铃优先于搜索**——算法推荐的岗位往往比关键词搜索更精准

---

## 参考文件

- `references/cdp-websocket-setup.md` — CDP WebSocket配置与验证
- `references/gmail-mcp-setup.md` — Gmail MCP OAuth授权流程
