# 企业ATS（Taleo/Oracle/Workday）申请表单指南

> 适用场景：MTR Taleo、领展Workday等企业级ATS系统的特殊字段处理

## 常见ATS系统类型

| 系统 | 特征 | 常见雇主 |
|------|------|---------|
| Oracle Taleo | "Other Information"页 + 多文件上传 + 必填薪资字段 | MTR |
| Workday | 向导式表单 + 自动解析简历 + 必填字段多 | 领展、Manulife |
| SAP SuccessFactors | 模块化 + eSignature | 大型跨国企业 |
| Lever/Greenhouse | 简洁表单 + 快速申请 | 科技公司 |

## Taleo特殊字段处理

### 1. "Special skills, achievements / awards"（文本框）

策略：对齐JD的三个核心Domain + 管理优势

推荐结构（150-250字，英文）：
```
- [技术成就] — 直接对JD Domain 1/2/3
- [管理成就] — 团队规模、项目体量、关键指标
- [学术成果] — 学位、论文、项目链接
```

Tips:
- 分bullet写，不要写成段落
- 每一条=一个具体的"做了什么+结果"
- 不要堆砌不相关的技能

### 2. "Community Service"（文本框）

策略：
- 没参加过该公司活动 -> 诚实写"No prior participation, but keen to contribute"
- 有其他社区服务 -> 写具体经历（支教、志愿者、行业协会）
- 参加过相关活动 -> 写具体活动名称+收获

不要编造。MTR等大公司可能有内部记录。

### 3. "Attachments"（文件上传）

文件选择策略：
- P0: Resume/CV — 必须标记为"Resume"，系统以此识别主简历
- P1: Cover Letter — 针对性定制，文件名含公司和岗位
- P2: Academic Transcript — 证明学位（尤其是转型者）
- P3: Certificates — 专业认证（如PMP、AWS等）

文件命名规范：
- 英文无空格（系统兼容）
- 含姓名+公司+文档类型
- 例：Hong_Zhangxiu_MTR_CoverLetter.pdf

Taleo特殊行为：
- 同文件名上传 = 覆盖原文件
- 必须勾选"Relevant Files"列标记哪些文件随本次申请提交
- 必选一个文件标记为"Resume"

## Pitfalls

1. 🔴 Cover Letter PDF必须可读（非扫描版） — ATS会OCR/解析PDF文本，图片式PDF无法通过关键词匹配
2. 🔴 PDF生成必须用Unicode字体 — Helvetica不支持Unicode（em dash、中文等），必须用DejaVu或Noto字体
3. 🟡 不要等到最后一步才准备附件 — 提前准备好标准版Resume + CL模板
4. 🟡 "Other Information"栏不要留空 — 这是一个展示机会，不填=浪费
5. 🔴 文件名不要有特殊字符 — 空格、括号、#号在某些ATS中会导致上传失败
