# Cover Letter PDF生成指南（fpdf2）

> 适用场景：用Python fpdf2库生成可被ATS系统解析的Cover Letter PDF

## 工具链

| 组件 | 推荐 | 备选 |
|------|------|------|
| PDF库 | fpdf2 (2.8.7+) | reportlab, weasyprint |
| Unicode字体 | DejaVu Sans（系统自带） | Noto Sans CJK（需安装） |
| 路径 | /usr/share/fonts/truetype/dejavu/ | apt-get install fonts-dejavu |

## 标准模板框架

```python
from fpdf import FPDF

class CLetter(FPDF):
    def footer(self):
        self.set_y(-15)
        self.set_font('DejaVu', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}/{{nb}}', align='C')

pdf = CLetter()
pdf.alias_nb_pages()
pdf.set_auto_page_break(auto=True, margin=25)
pdf.add_page()

pdf.add_font('DejaVu', '', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')
pdf.add_font('DejaVu', 'B', '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf')
```

## 正文段落策略（SOE->AI转型场景）

| 段落 | 内容 | 映射目标 |
|------|------|---------|
| 第一段 | 开场定位：12年SOE管理+AI硕士 = rare combination | 立人设 |
| 第二段 | SOE管理经验映射JD职责 | 证明匹配 |
| 第三段 | AI技术基础（论文、项目、工具链） | 证明hands-on |
| 第四段 | 差异化定位：能在大型组织推动落地 | 展示独特价值 |
| 第五段 | 收尾：期待面试 | 行动号召 |

## Pitfalls

1. 🔴 Helvetica不支持Unicode — em dash、中文等会抛异常，必须用DejaVu/Noto
2. 🔴 v2.5.2后弃用ln=True，改用new_x/new_y
3. 🟡 全文控制在1.5页A4以内
