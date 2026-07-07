# python-docx 段落插入最佳实践

> 2026-06-26 从简历审计工具项目插入实战中提炼

## 插入新段落的标准流程

### Step 1: 选择模板段落
从**紧邻插入位置**的段落复制XML元素（不是从文档开头找style），确保spacing/indent/numbering完全一致。

### Step 2: 清除旧runs，写入新内容
```python
for child in list(new_p):
    if child.tag.endswith('}r'):
        new_p.remove(child)
new_run = etree.SubElement(new_p, qn('w:r'))
orig_rpr = template_elem.findall(qn('w:r'))[0].find(qn('w:rPr'))
if orig_rpr is not None:
    new_run.append(deepcopy(orig_rpr))
new_t = etree.SubElement(new_run, qn('w:t'))
new_t.set(qn('xml:space'), 'preserve')
new_t.text = bullet_text
```

### Step 3: 链式插入多段落
```python
insert_after = ref_element
for text in bullets:
    new_p = build_para(template_elem, text)
    insert_after.addnext(new_p)
    insert_after = new_p
```

### Step 4: save + 重新open验证
每次insert后必须save并重新读取验证字符数和格式。

## Pitfalls

| # | 问题 | 修复 |
|---|------|------|
| 1 | 新段落139字符 vs 邻近68字符 | 中文60-80字符，太长拆2条 |
| 2 | 从heading段落复制模板 | 标题用标题模板，bullet用bullet模板 |
| 3 | 忘记doc.save() | 每次insert后立即save |
| 4 | 新项目塞进已有项目下 | 新项目=独立title+desc+bullets |
| 5 | 中英文区域混用索引 | 英文区域需重新定位参考段落 |

## 删除段落
多段落删除从后往前（reverse order）避免索引偏移。
