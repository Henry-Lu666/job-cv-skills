# 批量JD匹配工作流（Cron Agent参考）

## 触发场景
- 定时Cron任务扫描追踪表中待核实岗位
- 用户说"做一遍匹配"、"JD匹配补全"
- 追踪表中有多个Hunter 60%+岗位未核实

## 优先级排序
1. ②数字化方向（实测匹配度最高）
2. ④BD方向
3. ③运营方向
4. ⑤出海方向
5. ①AI PM方向（直接批量标⚠️，除非JD写"operations background welcome"）

## CDP批量提取流程（每个岗位3次调用）

```
Step 1: browser_cdp(Target.createTarget, url=<岗位URL>)  — 或 browser_navigate
Step 2: sleep 4秒
Step 3: browser_cdp(Runtime.evaluate, target_id=<tabId>)  — 必须用target_id不能用browser_console
        expression: (() => {
          const body = document.body?.innerText || '';
          const closed = body.includes('No longer accepting') || 
                        body.includes('已停止接受') || 
                        body.includes('无法加载页面');
          return JSON.stringify({
            url: window.location.href,
            title: document.title,
            bodyLen: body.length,
            closed,
            jd: body.substring(0, 6000)
          });
        })()
Step 4: browser_cdp(Target.closeTarget, params={"targetId": "<tabId>"})  — 用createTarget时才需要
```

**bodyLen判断标准（2026-06-27验证）**：
- ≥3000：通常包含完整JD ✅
- 2000-3000：可能只提取到部分JD，需检查是否包含"Responsibilities"/"Requirements"等关键词
- <2000：JD正文缺失，需回退 ⚠️
- <200：页面未加载或登录墙 ❌

## 关闭检测（必须先做）
- `closed=true` → 直接在追踪表标❌，不提取全文，不保存JD文件
- `bodyLen < 200` → 页面未加载或登录墙，跳过
- `jd`包含"无法加载页面" → 岗位ID无效/已删除

## JobsDB岗位搜索
当只有公司名+岗位名（没有JobsDB ID）时：
```
browser_cdp(Page.navigate, url="https://hk.jobsdb.com/jobs?keywords={公司名+关键词}&sortmode=ListedDate")
→ 从搜索结果中提取job ID → navigate到详情页
```

## 9维度评估要点
- 核心三维（行业+职能+技能）< 5/9 → 不投
- 5-6/9 → P2
- ≥ 7/9 → P1
- JD要求特定行业经验（保险/金融/航空/奢侈品）→ 行业壁垒，直接降级
- JD要求粤语流利 → 用户只有基础听，硬伤

## 追踪表更新规则
- 已关闭/已删除 → 在未核实列标`→❌`加备注"已关闭"
- 不匹配 → 标`→❌`加硬伤说明
- 新进P1/P2 → 更新岗位池表格+添加JD文件链接
- JD链接格式：`[📄JD+中文](JD库/{JobsDB_ID}_{Company-Hyphenated}_{Role-Hyphenated}.md)`

## 06-26 实测数据
- 待核实12个 → 已关闭5个 + 不匹配5个 + 新进P1:1个 + 新进P2:2个
- 旧岗位（2-4周）关闭率约40-50%
- 保险/金融行业壁垒率100%（AIA 2个岗位都要求8+年行业经验）
- 工程/基建行业与用户背景零交叉（Taylor Dunn）

## Hunter 60%+批量标记工作流（2026-06-27验证）

当追踪表中有大量（30-80个）未标记的Hunter 60%+岗位时，不需要逐个抓取JD。按类别批量标记：

| 类别 | 判断条件 | 标记 |
|------|---------|------|
| ①AI PM方向 | 方向列含"①AI PM" | →❌PM硬门槛 |
| 加密/Web3公司 | 公司名含OKX/HashKey/OSL/BTSE/Crypto.com | →❌加密行业 |
| 已在❌区域 | 同公司+岗位已在"已核实<50%"部分 | →❌已在不投区(X/9) |
| 已在P2 | 同公司+岗位已在P2部分 | →✅已在P2 |
| 已有JD文件 | JD库中存在对应文件 | →⚠️已有JD待评估 |
| 行业壁垒 | 奢侈品/半导体/医疗/保险(低级) | →❌XX行业 |
| 待核实 | 以上都不匹配 | →⚠️需L2核实 |

**批量更新方法**：`execute_code`中逐行处理tracking table，按company+score+direction匹配，用字符串替换批量更新后`write_file`写回。

**06-27实测**：75个未标记 → 42个批量标记 + 14个逐个核实 + 19个按行业标记 = 0个剩余

## 平台特定注意事项

| 平台 | JD提取方式 | CF风险 | 备注 |
|------|-----------|--------|------|
| LinkedIn | ❌ CDP不可用(bodyLen≈994) | N/A | curl meta description快速分类(见下) |
| JobsDB | body.innerText via CDP | 无（CDP绕过） | 直接JD URL最稳定 |
| Indeed | 搜索页右侧面板 | viewjob URL被CF拦截 | ⚠️ 很多HK岗位仅LinkedIn发布，Indeed搜不到 |
| CTgoodJobs | body.innerText via CDP | 无 | |
| 猎聘 | body.innerText via CDP | 无 | 以内地岗位为主 |

## LinkedIn JD获取：curl meta description（2026-07-01验证）

LinkedIn CDP提取bodyLen≈994（JD正文不渲染），Indeed/JobsDB上很多HK岗位搜不到。
**最实用方案**：curl meta description做快速分类（1-2句摘要）。

```bash
curl -sL -H "User-Agent: Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15" \
  "https://www.linkedin.com/jobs/view/{ID}" 2>/dev/null | \
  grep -oP '(?<=meta name="description" content=")[^"]*' | head -1
```

返回示例："Posted 6:18 PM. Description: Amazon Web Services (AWS)..."
**分类能力**：足够判断方向+行业，不够做9维度评估。
**完整JD获取**：需用户手动在Chrome中打开复制，或搜索Indeed/JobsDB同名岗位。
**并行子agent抓JD的教训**：3个子agent同时用CDP访问Indeed会互相冲突（共享Chrome实例），仅产出stub文件。正确做法：主agent串行抓取，或最多1个子agent用CDP。
