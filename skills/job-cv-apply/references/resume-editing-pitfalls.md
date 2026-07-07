# python-docx 简历编辑 Pitfalls

> 2026-06-24 验证

## Pitfall 1: 中文引号导致run-level匹配失败

**现象**：包含中文引号的段落，run-level `old_text[:25] in run.text` 匹配失败。

**原因**：python-docx将粗体/普通/颜色各拆为独立run，中文引号常被拆到不同run中。

**正确做法**：当run-level匹配失败时，用段落级全文替换：
```python
for p in doc.paragraphs:
    if "目标文本片段" in p.text:
        old_full = p.text
        new_full = old_full.replace("旧文本", "新文本")
        p.runs[0].text = new_full
        for r in p.runs[1:]:
            r.text = ""
```

## Pitfall 2: Word锁定文件

`shutil.copy2()` 报 PermissionError 时，存为新文件名让用户手动替换。

## Pitfall 4: deepcopy插入段落后忘记save()

**现象**：用`deepcopy`+`addnext`插入新段落，脚本运行成功但文件没有变化。

**原因**：忘记调用`doc.save()`，python-docx的修改只在内存中。

**规则**：每次修改后必须`doc.save(path)`。不要攒到最后一起save——同一个脚本里两次`Document()`加载同一文件时，第二次会覆盖第一次的修改。

## Pitfall 5: 批量插入段落必须链式addnext

**现象**：插入多个连续段落时，顺序颠倒。

**原因**：多个`addnext`都指向同一个`ref_element`，每次都在ref后面插入，导致逆序。

**正确做法**：
```python
insert_after = ref_element
for text in bullet_texts:
    new_p = create_paragraph(text)
    insert_after.addnext(new_p)
    insert_after = new_p  # 链式！
```

## Pitfall 6: 从heading段落deepcopy会有异常格式

**现象**：从标题段落（如"跨境智审通"）deepcopy出的段落，字号/间距与普通bullet不一致。

**规则**：插入bullet内容时，从同类型的normal/bullet段落deepcopy，不要从heading段落复制。

## Pitfall 3: 英文逐词替换兜底

英文run也可能拆分。用逐词替换兜底：
```python
for p in doc.paragraphs:
    for run in p.runs:
        for old_word, new_word in word_fixes:
            if old_word in run.text:
                run.text = run.text.replace(old_word, new_word)
```

## Pitfall 5: 段落插入模板必须同类型（2026-06-26验证）

用 `deepcopy` + `addnext` 插入新段落时，模板段落必须和目标位置的段落**同类型**。

**错误**：用heading段落作模板插入bullet → 字号/间距不一致，排版混乱
**正确**：用同section的bullet段落作模板 → 格式完全一致

```python
# ✅ 用相邻bullet段落作模板
template = doc.paragraphs[13]._element  # 已有的bullet段落
new_p = deepcopy(template)
# ... 填充文本 ...
ref_element.addnext(new_p)
```

## Pitfall 6: 修改后必须save()（2026-06-26教训）

python-docx的所有修改都在内存中，**不调用 `doc.save()` 就丢失**。批量修改脚本必须在最后一步save。

```python
doc.save(output_path)  # 必须！
```

同一脚本中如果加载了两次文件（如先改中文再改英文），每次save后必须重新加载：
```python
doc.save(path)
doc = Document(path)  # 重新加载，否则后续修改基于旧快照
```

## Pitfall 7: 简历内容幻觉红线（2026-06-26教训）

agent生成简历内容时，**严禁编造未确认的数字和荣誉**。已发现的幻觉案例：
- "校对准确率达92%" — 无实测数据
- "项目获评优秀硕士毕业设计" — 不属实

**规则**：简历中所有量化数据必须有来源（论文/已验证文件/用户确认）。无法确认的数据用定性描述替代。

## Pitfall 8: 英文bullet风格必须与中文对齐（2026-06-26用户纠正）

中文简历用简洁bullet风格（"关键词：内容"，40-70字/条，无主语短句），英文必须镜像：

```python
# ✅ 正确：简洁bullet，无主语
"High-Voltage Engineer (2014–2016): 3-year motor system & DC/DC converter design; Mid-Level Engineer certification, 1 patent"

# ❌ 错误：完整句子，有主语
"R&D Phase (2014-2016): 3 years of motor system and DC/DC converter design, earned Mid-Level Engineer certification, 1 registered patent, contributed to 5 NEV industry standards."
```

## 安全替换顺序

1. run-level匹配（快速，保留格式）
2. 段落级全文替换（中文引号场景）
3. 逐词替换兜底（英文单词残留）
4. 必须验证零ATS高危词残留
