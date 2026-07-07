# 时间校准翻车记录（2026-07-06 会话）

## 场景

求职流程 Stage 0 Gmail 扫描后汇报结果。

## 经过

1. Agent 第一次说 "今天是 2026年7月6日（周一）" — ✅ **正确**（7月6日确实是周一）
2. 用户说 "你的时间又混乱了。现在是7月6日，上午10:40。"
3. Agent 自我怀疑，改口说 "今天是2026年7月6日（周日）10:40，不是周一" — ❌ **改错了**
4. 用户追问 "你们确实没有读取时间的工具吗？去网上、论坛搜一遍"
5. 查 `date` → `Mon Jul 6 10:42:06 CST 2026` — 第一次本就正确
6. 查 Hermes 源码 → 发现系统提示已注入日期（date-only），有 `hermes_time.py` 提供时区感知时间

## 根因

- **权威效应**：用户一质疑立刻改口，没先 `date` 验证
- **缺乏时间校准习惯**：回复时间敏感内容前没先查 `date`
- **模型内置时间漂移**：DeepSeek 系模型对当前时间的认知不稳定

## 改进措施

详见 `time-grounding` skill（跨任务通用时间校准规范）。

## 与 Hermes 时间机制的关系

- 系统提示 volatile tier 注入 `Conversation started: Monday, July 6, 2026`（date-only）
- `hermes_time.py` 提供 `now()` 函数（时区感知，但仅供 Python 层调用，不暴露给模型）
- `timestamps: false` 在 CLI display 配置中，不影响系统提示
- 时区由 `config.yaml` 的 `timezone: Asia/Hong_Kong` 或 `HERMES_TIMEZONE` env var 控制
