# 深度简历编辑：docx XML 操作指南

> 2026-06-23 验证：从 V3 base 生成内推版（新增项目+扩充经历+增强AI能力描述）

## 适用场景

当 python-docx 的纯文本替换不够用时（需要**新增段落、插入项目、调整结构**），使用 docx skill 的 unpack→edit XML→pack 流程。

python-docx 的 `add_paragraph()` 会破坏自定义样式和编号，已被标记为危险操作。XML 操作保留所有原有格式。

## 工作流

### Step 1: Unpack

```bash
python3 ~/.hermes/skills/claude-code/docx/scripts/office/unpack.py \
  "简历路径.docx" /tmp/resume_unpacked/
```

输出：`word/document.xml`（主内容）+ 其他 XML 文件。

### Step 2: 定位插入点

在 `document.xml` 中搜索标记文本，找到 `</w:p>` 边界：

```python
marker = "目标文本内容"
pos = xml.find(marker)
end_para = xml.find("</w:p>", pos)
insert_after = end_para + len("</w:p>")
```

**关键**：用**唯一的、不会出现在新增内容中的**标记文本。如果标记出现在多个位置，用更长的上下文字符串。

### Step 3: 构造 XML 段落

从原文档中**复制一个相邻段落的 XML 结构**作为模板，修改文本内容。保持：
- `<w:rPr>` 格式属性一致（字体、颜色、字号）
- `<w:pPr>` 段落属性一致（缩进、间距、大纲级别）
- `<w:numPr>` 编号属性（如果是列表项）

模板结构：
```xml
<w:p w14:paraId="UNIQUE_ID">
  <w:pPr>
    <w:numPr>...</w:numPr>           <!-- 列表项才有 -->
    <w:spacing .../>
    <w:ind .../>
    <w:jc w:val="left"/>
    <w:outlineLvl w:val="1"/>
    <w:rPr>...</w:rPr>
  </w:pPr>
  <w:r>
    <w:rPr>...</w:rPr>
    <w:t>新文本内容</w:t>
  </w:r>
</w:p>
```

### Step 4: 插入

```python
xml = xml[:insert_after] + new_paragraph_xml + xml[insert_after:]
```

### Step 5: Pack

```bash
python3 ~/.hermes/skills/claude-code/docx/scripts/office/pack.py \
  /tmp/resume_unpacked/ "输出路径.docx" --original "原始简历.docx"
```

验证：`Paragraphs: N → N+X (+X)` 表示新增成功。

### Step 6: 验证

```bash
# 用 read_file 提取文本确认内容正确
# 检查新增段落位置、中英文同步
```

## Pitfalls

### 🔴 双语文件必须独立更新中英文

V3 简历有中文和英文两个独立区域（英文在文档后半部分）。新增内容时必须：
1. 在中文区域找到标记 → 插入中文版
2. **另找**英文区域的对应标记 → 插入英文版
3. 两个区域的标记文本**完全不同**（中文 vs 英文），不能用同一个 marker

**2026-06-23 教训**：中文"高压工程师"和英文"High-Voltage Engineer"是不同的 marker，需要分别定位。

### 🔴 多次插入时标记会漂移

每次插入后文档长度变化，后续 marker 的绝对位置偏移。两种安全策略：
1. **从后往前插入**：先插文档后部的内容，再插前部的（不影响前部 marker 位置）
2. **每次重新搜索 marker**：插入后重新 `xml.find(marker)` 获取新位置

**2026-06-23 实践**：用了策略2，每次 find 都在上次编辑后的 xml 上搜索，成功。

### 🔴 插入后检查相邻段落顺序

新增段落插入到 `</w:p>` 之后，可能把原本紧跟的段落挤开。
**2026-06-23 教训**：英文版插入2017轮岗段落时，"Awarded Intermediate Engineer..." 段落原本紧跟高压工程师段落，插入后被挤到了2017段落后面。位置关系变得不合理。

**解决方案**：插入前检查插入点前后的段落内容，确认逻辑顺序正确。如果需要在A和B之间插入C，插入后验证顺序是 A→C→B。

### 🔴 w14:paraId 必须唯一

每个 `<w:p>` 的 `w14:paraId` 必须是文档内唯一的8位十六进制值。用明显的前缀（如 `BOC00001`、`20A7B001`）避免与原有 ID 冲突。pack 工具会自动修复无效的 paraId，但显式唯一更安全。

### XML 特殊字符

| 字符 | XML 写法 |
|------|----------|
| & | `&amp;` |
| < | `&lt;` |
| > | `&gt;` |
| " | `&quot;` |
| ' | `&#x2019;` |
| " | `&#x201C;` |
| " | `&#x201D;` |
| — | `&#x2014;` |
| · | `&#xB7;` |

## 与浅层定制的对比

| 维度 | 浅层定制（python-docx） | 深度编辑（XML） |
|------|----------------------|----------------|
| 替换文本 | ✅ 安全 | ✅ 安全 |
| 新增段落 | ❌ 破坏样式 | ✅ 保留格式 |
| 调整顺序 | ❌ 高风险 | ⚠️ 需验证 |
| 新增项目/章节 | ❌ 不可行 | ✅ 可行 |
| 学习成本 | 低 | 中（需理解XML结构） |
| 适用场景 | 定制版简历 | 内推版/结构性修改 |

## 实际案例：V3→内推版修改清单

| # | 修改 | 中文marker | 英文marker | 位置 |
|---|------|-----------|-----------|------|
| 1 | 个人优势增强 | `12 年新能源汽车全链路...` | `12 years of end-to-end...` | 替换(非插入) |
| 2 | 新增中银项目 | `验证小样本场景 AI 可落地性` | `Delivered brand benchmarking...` | ABSA段落后 |
| 3 | 新增2017轮岗 | `参与 5 项行业标准制定` | `3 years of motor system...` | 高压工程师段落后 |
| 4 | 技术栈增强 | `多模型编排（Claude / Kimi...` | `Multi-Model Orchestration...` | 替换(非插入) |

新增段落数：+10（中文5 + 英文5）

## 高级技巧：段落移动

当插入新段落导致相邻段落顺序错乱时（如pitfall中"Awarded Intermediate Engineer"被挤到2017轮岗后面），需要**移动段落**：

```python
# 1. 找到需要移动的段落完整边界
pos_content = xml.find("Awarded ")  # 段落内的特征文本
para_start = xml.rfind("<w:p ", 0, pos_content)
para_end = xml.find("</w:p>", pos_content) + len("</w:p>")
target_para = xml[para_start:para_end]

# 2. 从原位置删除
xml = xml[:para_start] + xml[para_end:]

# 3. 在新位置插入（目标位置的 <w:p 之前）
target_pos = xml.find("Pivoting (2017)")  # 目标位置的特征文本
target_start = xml.rfind("<w:p ", 0, target_pos)
xml = xml[:target_start] + target_para + "\n    " + xml[target_start:]

# 4. 验证顺序
pos_hv = xml.find("High-Voltage")
pos_aw = xml.find("Awarded ")
pos_2017 = xml.find("Pivoting (2017)")
assert pos_hv < pos_aw < pos_2017, "顺序错误!"
```

## Pitfalls（续）

### 🔴 文本被拆分到多个 `<w:r>` run 中

**2026-06-23 验证**：docx 的 XML 中，一个段落的文本经常被拆成多个 `<w:r>` 元素，每个有不同的格式属性（粗体、颜色、字号等）。例如：

```xml
<w:r><w:rPr><w:b/></w:rPr><w:t>Iterative Delivery &amp; Rapid Pivoting (2017):</w:t></w:r>
<w:r><w:rPr><w:b w:val="0"/></w:rPr><w:t>Rotated responsibilities every 3 months...</w:t></w:r>
```

**影响**：不能搜索跨 run 的长字符串。`xml.find("Pivoting (2017):Rotated")` 会失败，因为冒号和 "Rotated" 在不同的 run 中。

**对策**：
- 搜索时用**单个 run 内的短文本**作为 marker（如 `"Pivoting (2017)"` 或 `"Rotated responsibilities"`）
- 需要检查跨 run 内容时，先找 `<w:p>` 边界，再提取段落内所有 `<w:t>` 拼接

### 🔴 run 之间的空格丢失

当冒号 `:` 在一个 run 的末尾，下一个 run 以 `Rotated` 开头时，视觉上看起来有空格（因为 run 之间有换行），但实际 XML 中没有空格字符。

**2026-06-23 案例**：`Pivoting (2017):</w:t>` + `>Rotated responsibilities` → 显示为 "2017):Rotated"（缺空格）

**修复**：在第二个 run 的 `<w:t>` 上加 `xml:space="preserve"` 并补空格：
```python
old = '>Rotated responsibilities every 3 months'
new = ' xml:space="preserve"> Rotated responsibilities every 3 months'
xml = xml.replace(old, new)
```

### 🔴 用户手动编辑后的工作流（"看简中后，修正英文"）

用户经常在 Word 中手动编辑简历（调整排版、修正内容），然后让 agent review 并同步中英文。用户原话："看简中后，修正英文"。

正确流程：
1. 重新 unpack 用户修改后的文件（不要用旧的 unpack 目录）
2. 用 `read_file` 提取全文，逐行对比中英文版本
3. 找出中文已改但英文未同步的地方
4. 只修改需要同步的部分，不要覆盖用户的排版调整

**2026-06-23 案例**：
- 中文四头架构从 "方面抽取 + 情感分类 + 营销洞察多标签 + 槽位填充" 改为 "产品BIO + 情感分类 + 营销BIO + 营销洞察多标签"
- 英文版需同步：`aspect extraction + sentiment classification + multi-label marketing insights + slot filling` → `Product BIO + Sentiment Classification + Marketing BIO + Marketing Insight Multi-label`
- 英文段落顺序问题：2017轮岗段落插入后，"Awarded Intermediate Engineer..." 被挤到错误位置，需要移动

### XML `&amp;` 替换陷阱

搜索 XML 中的 `&` 时必须用 `&amp;`，但**替换时也要保持 `&amp;`**：
```python
# 正确
xml.replace("aspect extraction + sentiment classification", "Product BIO + Sentiment Classification")

# 如果目标文本含 &，必须转义
xml.replace("R&amp;D", "R&amp;D")  # 不变
xml.replace("old text", "new text with &amp; sign")  # & 必须写成 &amp;
```
