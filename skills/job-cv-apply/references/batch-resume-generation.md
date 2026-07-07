# 批量定制简历生成流程

> 2026-07-01 更新为V4 base（V3内推版已废弃，不再作为定制base）

## 适用场景

P1/P2岗位池中有多个"❌待出"岗位，需要批量生成定制简历。

## 前置条件

- V4 base简历已确认：`您的姓名的简历_2026.V4.docx`（WPS制作，简洁bullet风格）
- 每个岗位的方向已确定（BD/AI落地/数字化）

## 流程

### Step 1: V4段落索引（2026-06-28验证）

| 索引 | 内容 | 可定制 |
|------|------|--------|
| Table 1 run[2] | 意向岗位（中文求职目标） | ✅ |
| para[13] | 中文自我评价（~287字） | ✅ |
| para[110] | 英文Job Target | ✅ |
| para[114] | 英文自我评价（~539字符） | ✅ |

⚠️ **V4 Table 1 run拆分**：python-docx打开后，Table 1单元格文本被拆为3个run：`run[0]='意向岗位'`、`run[1]='：'`、`run[2]=实际内容`。直接赋值`p.runs[2].text`，不要用字符串匹配搜索run。

### Step 2: 定义每个岗位的定制数据

```python
positions = [
    {
        "name": "公司简称-岗位方向",  # 用于文件名
        "cn_target": "AI 落地推行 / 变革管理 / 业务赋能",
        "cn_self": "中文自我评价...",
        "en_target": "AI Transformation Specialist / Change Management / Business Enablement",
        "en_self": "English self-assessment...",
    },
    # ...更多岗位
]
```

自我评价定制规则（参考 `resume-customization-by-direction.md`）：

已验证方向（2026-07-02）：

| 方向 | 求职目标关键词 | 自我评价侧重 |
|------|--------------|------------|
| 战略运营/CEO办公室 | 战略运营 / CEO 办公室支持 / 跨区域协调 | 战略规划+高管汇报+KPI体系+跨区域协调 |
| BD销售/APAC Sales Director | 业务拓展 / APAC 销售管理 / 战略合作伙伴 | B2B大客户+渠道管理+战略销售规划 |
| 商业规划/数字PMO | 商业规划 / 数字PMO / 战略运营管理 | GTM策略+跨部门协调+治理框架+PMO |
| AI落地推行 | AI 落地推行 / 变革管理 / 业务赋能 | SOP推行+推动AI采用+变革管理 |
| BD战略合作 | 业务拓展 / 战略合作 / 客户管理 | B2B大客户+渠道管理+合作伙伴 |
| 数字化转型 | 数字化转型 / 流程优化 / 业务运营 | SOP标准化+跨区域协调+标准制定 |

### 内容优先三步法（2026-07-02验证）

不要边写代码边想内容。正确顺序：

1. **先定方向** — 确定每个岗位的方向标签（2个方向/3个方向/战略运营等）
2. **先写内容** — 在一个数据结构里定义好所有文本
3. **再写代码** — 数据驱动循环生成

```python
positions = [
    {
        "company": "CompanyA",
        "role": "Target-Role",
        "cn_target": "求职目标中文",
        "en_target": "Job Target English",
        "cn_self": "中文自我评价（~287字）",
        "en_self": "English self-assessment（~539 chars）",
    },
    # 所有岗位内容定义完毕后，再写循环修改代码
]
```

**好处**：内容审查和代码调试分离，一处改内容不影响逻辑，批量扩展只需加数据条目。

### Step 3: 批量生成（直接索引法，更高效）

```python
import shutil, os
from docx import Document

base_path = "/your/personal/folder/个人简历/您的姓名的简历_2026.V4.docx"
output_dir = "/your/personal/folder/个人简历/"

for pos in positions:
    fname = f"您的姓名的简历_2026_V4-{pos['name']}.docx"
    dst = os.path.join(output_dir, fname)
    shutil.copy2(base_path, dst)
    
    doc = Document(dst)
    
    # 1. Table 1 - 中文求职目标（run[2]直接赋值）
    t1 = doc.tables[1]
    for row in t1.rows:
        for cell in row.cells:
            if '意向岗位' in cell.text:
                for p in cell.paragraphs:
                    if len(p.runs) >= 3:
                        p.runs[2].text = pos['cn_target']
    
    # 2-4. 直接段落索引修改（更高效）
    doc.paragraphs[13].runs[0].text = pos['cn_self']
    for r in doc.paragraphs[13].runs[1:]:
        r.text = ''
    
    doc.paragraphs[110].runs[0].text = pos['en_target']
    for r in doc.paragraphs[110].runs[1:]:
        r.text = ''
    
    doc.paragraphs[114].runs[0].text = pos['en_self']
    for r in doc.paragraphs[114].runs[1:]:
        r.text = ''
    
    doc.save(dst)
```

### Step 4: 验证

```python
for pos in positions:
    doc = Document(os.path.join(output_dir, f"您的姓名的简历_2026_V4-{pos['name']}.docx"))
    table1 = doc.tables[1]
    for row in table1.rows:
        for cell in row.cells:
            if '意向岗位' in cell.text:
                assert pos['cn_target'] in cell.text
    assert len(doc.paragraphs[13].text) > 50  # 自我评价非空
    assert len(doc.paragraphs[114].text) > 50  # 英文自我评价非空
```

## Pitfall

- **V4 Table 1 run拆分**：`run[0]='意向岗位'`, `run[1]='：'`, `run[2]=实际内容`。直接赋值`p.runs[2].text`（2026-06-28验证）
- **runs[0]赋值后必须清空runs[1:]** — 否则新旧文本拼接在一起
- **段落索引可能因版本偏移** — 先打印确认再修改
- **不要改工作经历段落** — 保持base版通用措辞，只改求职目标+自我评价
- **必须doc.save()** — 不save等于没改（2026-06-26教训）
- **英文bullet风格**：无主语短句，keyword: content格式，不用完整句子（2026-06-26用户纠正）
- **自我评价长度**：中文~287字，英文~539字符。不要超太多
