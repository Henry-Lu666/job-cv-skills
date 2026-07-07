# CDP 浏览器子 Agent 工作流陷阱

> 2026-06-25 实操验证。总结通过 `delegate_task` + browser 工具批量抓取 JD 时遇到的所有问题。

## 问题全景

| 问题 | 根因 | 解决方案 |
|------|------|---------|
| 子 Agent 超时（600s/50次调用） | 每个JD需5-10次调用 | 每个子Agent最多3个岗位 |
| browser_console 在错误 tab 执行 | Target.createTarget 不切换焦点 | 用 browser_navigate 同 tab 导航 |
| Chrome 崩溃/CDP 断开 | 高负载+并行操作 | 串行+间隔3-5秒+CDP预检 |
| LinkedIn JD 不加载 | 未登录或需滚动 | 先手动登录+scroll后提取 |
| JobsDB Cloudflare 拦截 | bot 检测 | CDP 模式自动绕过 |
| 岗位已关闭 | 未检测关闭标记 | 先查 "已停止接受" |

## 推荐子 Agent Prompt 模板

```
抓取以下N个岗位的完整JD，保存到JD库，执行9维度评估。

**重要规则：**
- browser_navigate 超时30秒就跳过该岗位，不要重试
- 不要用 Target.createTarget 创建新tab，始终在同一个tab中用 browser_navigate 导航
- browser_console 提取失败时用 browser_snapshot(full=true) 兜底
- 某岗位搜不到标❌搜不到，不要编造

[岗位列表...]

操作步骤（每个岗位）：
1. browser_navigate 打开页面（超时30秒跳过）
2. browser_scroll 向下滚动一次
3. browser_console 提取JD文本
4. 保存到 JD库/{ID}_{公司简称}_{岗位简称}.md
5. 9维度评估
6. 等3秒再做下一个
```

## 批次策略

| 岗位数 | 建议子Agent数 | 每个子Agent | 预计耗时 |
|--------|-------------|------------|---------|
| 1-3 | 1 | 全部 | 3-5分钟 |
| 4-6 | 2 | 各2-3个 | 5-8分钟 |
| 7-10 | 3-4 | 各2-3个 | 8-12分钟 |
| 10+ | 分批执行 | 每批3个 | 每批5分钟 |

## CDP 健康检查

操作前必须验证：
```bash
curl -s --connect-timeout 3 http://localhost:9222/json/version
```

返回空或超时 = CDP 断开，暂停所有子 Agent，等用户重启 Chrome。

## JD 提取 Selector 优先级

| 平台 | Selector | 备注 |
|------|----------|------|
| LinkedIn | `.show-more-less-html__markup` | 需登录 |
| JobsDB | `[data-automation="jobDescription"]` | CDP绕CF |
| Indeed | `.jobsearch-jobDescriptionText` | |
| CTgoodJobs | `.job-description` | |
| 猎聘 | `.job-intro-container` | |

通用兜底：`document.body.innerText.substring(0, 5000)`
