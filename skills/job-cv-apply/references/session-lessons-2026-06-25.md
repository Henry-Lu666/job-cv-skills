# Session Lessons — 2026-06-25

## 新增 Pitfall（待合并到SKILL.md主文件）

### 49. 🔴 JD文件名必须与追踪表链接精确匹配

**日期**: 2026-06-25
**场景**: P1岗位Madison Pearl和OX HR的JD文件已保存，但文件名与追踪表中的Obsidian链接不一致，导致用户点击链接时404。

**问题详情**:
- 实际文件: `4417121632_MadisonPearl_AI-Advisory-Consulting.md`（公司名无连字符）
- 追踪表链接: `JD库/4417121632_Madison-Pearl_AI-Advisory-Consulting.md`（有连字符）
- 同样问题: `4421924051_OXHR_Head-of-AI.md` vs `4421924051_OX-HR_Head-of-AI.md`

**规则**: 
- 公司简称中每个单词必须用连字符连接：Madison-Pearl, OX-HR, Bemis-Associates
- 保存JD后立即 `ls JD库/ | grep {ID}` 对比文件名与追踪表链接
- 不匹配则 `mv` 重命名

---

### 50. 🔴 Hermes升级后必须删 `.update_check` 缓存

**日期**: 2026-06-25
**场景**: `git pull origin main` 成功后，`hermes --version` 仍显示 "574 commits behind — run hermes update"

**根因**: 
- `~/.hermes/.update_check` 缓存了旧的检查结果
- 缓存有效期 6 小时（`_UPDATE_CHECK_CACHE_SECONDS`）
- git 实际已同步到 origin/main（`git rev-list HEAD..origin/main` = 0）
- 但 `hermes --version` 读缓存，不重新计算

**修复**: `rm ~/.hermes/.update_check`

**规则**: 每次 Hermes 升级（git pull / pip install）后主动删缓存

---

## 今日求职流程执行摘要

- Gmail 未读30封 → 2封求职相关 → 3个新线索（Human8❌/IQ-EQ❌/TMax AI⚠️CF拦截）
- P1全部3个岗位简历已就绪（Bemis已有 + Madison Pearl新生成 + OX HR新生成）
- ATS陷阱词验证：3份全部CLEAN
- 追踪表已更新
- 待用户操作：3个LinkedIn投递 + 1个JobsDB手动核实
