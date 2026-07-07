# 求职全链路自动化 · Skills 套件

一条流水线跑完求职全流程：从扫邮箱到模拟面试。

## 包含的 Skills

| Skill | 功能 | 单独可用 |
|-------|------|---------|
| `job-cv-apply` | 6阶段求职管线：调研→SMART→PPT→模拟→修正→投递追踪 | ✅ |
| `interview-simulation` | 多轮深度面试模拟：五步循环+STAR反馈+七轮递进 | ✅ |
| `personality-receipt` | 人格小票：上传聊天记录生成AI专属使用说明书 | ✅ |

三个 skill 可独立使用，也可组合使用。`job-cv-apply` 的 Stage 6F 会自动调用其余两个。

## 安装

```bash
# 方法一：通过 npx 安装（推荐）
npx skills add your-username/job-cv-apply
npx skills add your-username/interview-simulation
npx skills add your-username/personality-receipt

# 方法二：手动复制
# 将 skills/ 下的对应目录复制到 ~/.hermes/skills/productivity/
```

## 前置准备（首次使用前必做）

### 1. Gmail 授权
```
参考 skills/job-cv-apply/references/gmail-mcp-setup.md
→ 在 Google Cloud Console 创建项目
→ 启用 Gmail API
→ 配置 OAuth 2.0 凭据
→ 首次运行自动触发授权
```

### 2. Chrome CDP 启动
```
参考 skills/job-cv-apply/references/chrome-cdp-setup-guide.md
→ 创建专用 Chrome 配置文件
→ 以 --remote-debugging-port=9222 启动
→ 登录求职站点，保存密码
→ 后续 CDP 自动使用已保存的会话
```

### 3. 配置路径

在 `~/.hermes/config.yaml` 或 skill 的 `SKILL.md` 中替换占位符：

```yaml
resume_path: "your-resume-path/your-resume.docx"
knowledge_base: "your-kb-path/"
chrome_user_data: "your-chrome-user-data-path/"
chrome_debug_port: 9222
gmail_credentials: "~/.gmail-mcp/credentials.json"
```

## 快速开始

安装 + 配置完成后，说一句话就能启动：

| 你说 | 发生什么 |
|------|---------|
| "扫邮箱" | Gmail 扫描 → 列出新岗位通知 |
| "准备面试 XX公司" | 调研→SMART方案→PPT→模拟 全流程 |
| "模拟面试" | 加载 interview-simulation skill，直接进入角色扮演 |
| "人格小票" | 从你的自我介绍生成一页热敏小票风格的性格画像 |
| "走一遍" | 完整求职日常：扫邮箱→看岗位→投递→追踪 |

## 依赖关系

```
job-cv-apply
├── deep-research skill    （Stage 6A：公司调研）
├── interview-simulation   （Stage 6F：面试模拟）
│   └── personality-receipt（模拟时适配用户沟通模式）
└── 工具链
    ├── Gmail MCP          （邮件扫描）
    ├── Chrome CDP          （浏览器自动化）
    └── python-docx         （简历生成）
```

## 文件结构

```
skills/job-cv-apply/
├── SKILL.md                    ← 主文件（脱敏版）
├── references/                 ← 方法论参考（66个文件）
│   ├── gmail-mcp-setup.md      ← Gmail 授权指南
│   ├── chrome-cdp-setup-guide.md ← CDP 设置指南
│   ├── smart-pain-point-framework.md
│   ├── star-stories.md
│   ├── multi-version-resume-workflow.md
│   └── ...
├── templates/
│   └── coffee-meeting-anchor-card.md
├── examples/
│   └── full-preparation-case.md
└── scripts/
    └── generate_cover_letter_pdf.py

skills/interview-simulation/
└── SKILL.md

skills/personality-receipt/
└── SKILL.md
```

## 方法论亮点

- **STAR 反馈框架**：S(结构)/T(真实感)/A(直击核心)/R(可落地)，四维评分卡
- **七轮递进模型**：从摸底到边界认知，还原面试官心理变化路径
- **SMART 痛点逆向工程**：从 JD 反推公司真实痛点，用方案证明"这份工作需要你"
- **笔记本法**/人话起手式/数字触发框架/问1答1：现场可用的沟通工具箱

## 许可证

MIT
