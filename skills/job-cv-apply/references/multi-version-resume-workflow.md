# 多版本简历批量生成工作流

> 2026-06-09 首次验证：从 V3 base 批量生成 5 份定制简历

## 工作流概述

当多个岗位需要投递，且方向差异较大（运营 vs 品牌 vs BD）时，需要从同一份 base 简历生成多份定制版本。

## 深层定制模式（跨方向，2026-06-12 验证）

当岗位方向差异大（如 AI落地推行 vs BD vs 战略合作），仅改求职目标+摘要不够，需要逐段改写：

### 改写范围

| 段落 | 中文索引 | 英文索引 | 改什么 |
|------|---------|---------|--------|
| 求职目标 | 2 | 56 | 方向关键词 |
| 个人优势 | 4 | 58 | 核心能力描述、差异化定位 |
| AI项目-背景 | 7 | — | 技术语言 vs 业务语言 |
| AI项目-方法论 | 8 | 61 | 技术细节 vs 方案设计 |
| AI项目-成果 | 9 | 62 | F1数据 vs 商业成果 |
| AI项目-价值 | 10 | 63 | 落地经验/治理/C-suite对接 |
| 技术栈 | 12-13 | 65-66 | 工具排序（JD关心的前置） |
| 工作经历各bullet | 17-36 | 69-93 | 措辞对齐JD关键词 |

### 段落索引获取

```python
from docx import Document
doc = Document(template_path)
for i, p in enumerate(doc.paragraphs):
    if p.text.strip():
        first_run = p.runs[0] if p.runs() else None
        print(f"{i:3d} | bold={first_run.bold} size={first_run.font.size} | {p.text[:80]}")
```

### set_para_text（跨run安全替换）

当段落文本跨多个 run 时，逐 run 替换容易遗漏。`set_para_text()` 清空所有 run 后在首 run 上设置新文本，保留首 run 的格式：

```python
def set_para_text(para, new_text):
    if not para.runs:
        para.text = new_text
        return
    first_run = para.runs[0]
    fmt = {
        'bold': first_run.bold, 'italic': first_run.italic,
        'font_size': first_run.font.size, 'font_name': first_run.font.name,
    }
    if first_run.font.color and first_run.font.color.rgb:
        fmt['color'] = first_run.font.color.rgb
    for r in para.runs:
        r.text = ''
    para.runs[0].text = new_text
    for k, v in fmt.items():
        setattr(para.runs[0].font if 'font' not in k else para.runs[0], k, v)
    # Restore bold/italic/size/name/color individually
    para.runs[0].bold = fmt['bold']
    para.runs[0].italic = fmt['italic']
    para.runs[0].font.size = fmt['font_size']
    para.runs[0].font.name = fmt['font_name']
    if 'color' in fmt:
        para.runs[0].font.color.rgb = fmt['color']
```

### 批量生成函数

```python
import shutil

def create_cv(template_path, output_path, cn_changes, en_changes):
    """cn_changes/en_changes: {段落索引: 新文本}"""
    shutil.copy2(template_path, output_path)
    doc = Document(output_path)
    for i, p in enumerate(doc.paragraphs):
        if i in cn_changes:
            set_para_text(p, cn_changes[i])
        elif i in en_changes:
            set_para_text(p, en_changes[i])
    doc.save(output_path)
    return output_path
```

### JD驱动改写策略

| JD关键词类型 | 简历应对 |
|-------------|---------|
| change enablement / rollout / adoption | 个人优势加「变革推行」「adoption指标追踪」|
| C-suite / executive / stakeholder | 工作经历加「面向管理层汇报」「executive-ready」|
| GTM / pipeline / partner | 强调客户开发、销售管道、合作伙伴网络 |
| governance / SteerCo / cadence | 补「统筹跨部门治理会议」「追踪决策执行」|
| metrics / insights / analytics | 包装现有数据为「adoption指标追踪与分析」|
| playbook / toolkit / template | 「SOP框架」→「adoption playbook与激活工具包」|
| Microsoft Copilot / PowerBI | 技术栈前置Microsoft工具，后移PyTorch |

### 旧CV作为细节来源

当V3缺少某类经历的细节时，读取旧版简历（如2023年`你的简历_繁体.docx`）提取被删减但对特定JD高度相关的内容。旧CV通常用表格存储（`doc.tables[0]`），不是段落。

## 安全操作模式

### ✅ 安全：copy + 纯文本替换

```python
import shutil
from docx import Document

SRC = "~/你的简历路径/你的简历.docx"
OUT_DIR = os.path.expanduser("~/你的简历路径/定制版")

def generate_resume(version_key, target_cn, target_en, summary_old_cn, summary_new_cn, summary_old_en, summary_new_en):
    out_name = f"你的姓名的简历_2026_{version_key}.docx"
    out_path = os.path.join(OUT_DIR, out_name)
    shutil.copy2(SRC, out_path)
    doc = Document(out_path)

    # 1. 替换求职目标
    for para in doc.paragraphs:
        for run in para.runs:
            if "求职目标：业务营运管理 / 数字化转型 / AI 落地应用 · 香港" in run.text:
                run.text = run.text.replace(
                    "求职目标：业务营运管理 / 数字化转型 / AI 落地应用 · 香港",
                    target_cn
                )
            if "Job Target: Business Operations Management / Digital Transformation / AI Implementation · Hong Kong" in run.text:
                run.text = run.text.replace(
                    "Job Target: Business Operations Management / Digital Transformation / AI Implementation · Hong Kong",
                    target_en
                )

    # 2. 替换个人优势摘要
    for para in doc.paragraphs:
        for run in para.runs:
            if summary_old_cn in run.text:
                run.text = run.text.replace(summary_old_cn, summary_new_cn)
            if summary_old_en in run.text:
                run.text = run.text.replace(summary_old_en, summary_new_en)

    doc.save(out_path)
    return out_path
```

### ❌ 危险操作（会破坏排版）

- `doc.add_paragraph()` — 改变段落结构
- 修改 `run.font.name / size / color` — 破坏样式
- 修改 `paragraph_format` — 破坏间距
- ~~操作 XML 元素~~ → 改用 docx skill unpack→edit→pack 流程（安全，见 `references/deep-resume-xml-editing.md`）
- 直接修改原始 V3 文件 — 不可逆

## 替换粒度建议

| 替换内容 | 位置 | 影响 | 风险 |
|----------|------|------|------|
| 求职目标（中英文） | 简历顶部 | 定位方向 | ✅ 低 |
| 个人优势摘要（中英文） | 求职目标下方 | 强调重点 | ✅ 低 |
| 工作经历 bullet 顺序 | 工作经历段落 | 相关性排序 | ❌ 高（不动） |
| 技能排序 | 技能区 | 关键词匹配 | ❌ 高（不动） |

**原则**：只替换求职目标和摘要，工作经历的 bullet 重新排序留给用户手动做（见修改对照表）。

## 归类原则

不同公司的同一类岗位用同一份简历：

| 方向 | 归类标准 | 示例 |
|------|---------|------|
| 战略增长 | Strategy / Growth / Operations | 某媒体公司, Lalamove |
| 区域总经理 | Regional GM / Regional Ops | MiniMax, Uber |
| 品牌营销 | Brand Marketing / Head of Branding | Manulife, Bupa |
| 商务拓展 | BD / Strategic Partnerships | HashKey, Sotheby's |

## 命名规范

```
你的姓名的简历_2026_V3-{公司简称}-{岗位方向}.docx
```

示例：
- `你的姓名的简历_2026_V3-公司A-方向A.docx`
- `你的姓名的简历_2026_V3-公司B-方向B.docx`
- `你的姓名的简历_2026_V3-公司C-方向C.docx`

## 验证清单

生成后必须验证：
1. 替换是否生效（`python-docx` 读取目标段落确认）
2. 文件大小合理（不应与 V3 差异太大）
3. 中英文都已替换（不能只替换了中文没替换英文）
4. 原始 V3 未被修改（`ls -la` 确认时间戳未变）

## 验证脚本

```python
from docx import Document
import os

for v in versions:
    path = os.path.join(out_dir, f"你的姓名的简历_2026_{v}.docx")
    doc = Document(path)
    for p in doc.paragraphs:
        t = p.text
        if "求职目标" in t or "Job Target" in t:
            print(f"[{v}] TARGET: {t[:80]}")
        if "12 年" in t and "全链路" in t:
            print(f"[{v}] CN_SUMMARY: ...{t[10:90]}...")
        if "12 years" in t and "end-to-end" in t:
            print(f"[{v}] EN_SUMMARY: ...{t[10:100]}...")
```