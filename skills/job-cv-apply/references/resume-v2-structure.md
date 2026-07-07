# 简历 V2 结构与生成工作流

> 2026-05-27 从 V1 生成 V2 的完整工作流与决策记录

## V2 最终改动（含 ATS 优化版）

| 改动 | 效果 |
|------|------|
| +求职目标 | 「业务营运管理 / 数字化转型 / AI 落地应用 · 香港」——营运为主，AI 为辅 |
| 重写自我评价 | 原"四大支柱" → 一段话："12年全链路操盘 × AI全链路动手能力" |
| AI项目前置 | 硕士毕设从项目经历移到工作经历之前 |
| +技术栈新区 | Python/PyTorch/RoBERTa/消融实验/多模型编排/数据管线 |
| 工作经历+GMV | 6000台 → "≈¥2.4亿 GMV" |
| **🔴 ATS 关键词洗白** | 去掉「人才发展/慕课/内训师/培训」→ 换成「营运SOP/业务赋能/落地宣导」（详见 references/ats-keyword-optimization.md） |
| 整合早期经历 | 2014–2020 研发+用户运营合并为一条 |

## V2 结构顺序

```
求职目标 → 个人优势 → AI项目经历 → 技术栈 → 工作经历 → 教育 → 技能
（中英双语，分两段，中间用 page break）
```

## ⚠️ ATS 关键词红线

以下词会让 ATS 将你归类为 HR/L&D，**简历中绝对不能出现**：
- 人才发展 / Talent Development
- 慕课 / 培训 / 内训师 / 讲师
- e-learning / training / trainer
- 学习与发展 / L&D

替代词：营运 SOP / 业务赋能 / 业务落地宣导 / enablement / rollout

## 生成方法

### 方式1：python-docx 从零构建（本次使用）

```python
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.oxml.ns import qn

doc = Document()
# 页面设置 A4
section = doc.sections[0]
section.page_width = Cm(21.0)
section.page_height = Cm(29.7)
# … 逐段构建内容
doc.save('V2.docx')
```

### 方式2：解包→编辑XML→重新打包（适合微调）

```bash
python ~/.hermes/skills/claude-code/docx/scripts/office/unpack.py input.docx unpacked/
# 编辑 unpacked/word/document.xml
python ~/.hermes/skills/claude-code/docx/scripts/office/pack.py unpacked/ output.docx --original input.docx
```

## python-docx 踩坑

1. **段落边框 (w:pBdr) 位置**: 必须在设置 `paragraph_format` 之前加到 `pPr`，否则 schema 顺序错误。
   ```python
   p = doc.add_paragraph()
   pPr = p._element.get_or_add_pPr()
   pBdr = OxmlElement('w:pBdr')
   # … 构建 border …
   pPr.insert(1, pBdr)       # 在 pStyle (index 0) 之后，其他元素之前
   p.paragraph_format.space_before = Pt(14)  # 之后才设 format
   ```
2. **zoom 属性**: python-docx 生成的 settings.xml 有 `<w:zoom w:val="bestFit"/>` 但缺少 `w:percent` 属性，严格验证会报错。修复：给 zoom 加 `w:percent="100"`。
3. **中文字体**: 必须同时设 `run.font.name` 和 `run._element.rPr.rFonts.set(qn('w:eastAsia'), name)`。
4. **表格宽度**: 必须用 `WidthType.DXA`，不能用 `PERCENTAGE`（Google Docs 不兼容）。
5. **A4 尺寸**: `page_width = Cm(21.0)`, `page_height = Cm(29.7)`。

## V2 内容原则

- 一句话定位（不是并列四段）
- AI 能力前置（区别于纯管理简历）
- 技术栈独立成区（HR 可快速扫描）
- 数据加商业价值换算（GMV、留存率提升）
- 英文版精简（不要直译长句）
