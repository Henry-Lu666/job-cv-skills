# Taleo ATS 岗位详情页访问模式

## 概述

Taleo 是 Oracle 旗下招聘管理系统（ATS），香港多家大公司使用（MTR、HSBC等）。Taleo 的岗位详情页有固定的 URL 模式，可直接访问无需搜索。

## URL 模式

```
https://{company}.taleo.net/careersection/{section}/jobdetail.ftl?job={REQ_ID}
```

- `{company}` — 公司名（如 `mtr`）
- `{section}` — 招聘栏目名（如 `mtr_external`）
- `{REQ_ID}` — 岗位编号（如 `250000Z1`）

## 已验证案例

### MTR Corporation
- 岗位页面：`https://mtr.taleo.net/careersection/mtr_external/jobdetail.ftl?job=250000Z1`
- 搜索结果页：`https://mtr.taleo.net/careersection/mtr_external/jobsearch.ftl?lang=en`
- 搜索栏支持按 Job Number 或 Keywords 搜索
- 2026-07-03 验证：browser_navigate 直接到 jobdetail.ftl 可正常渲染完整 JD（含 Requirements/Responsibilities）
- 页面为经典 ASP.NET 样式，内容静态渲染（非 SPA），browser_console 的 `document.body.innerText` 可直接提取完整内容

## 已知局限

1. **搜索结果页**：部分 Taleo 搜索页的搜索按钮可能不响应 CDP 的 browser_click（需要表单提交而非 AJAX）
2. **搜索不如直接 URL 可靠**：如果知道 Requisition ID，直接用 jobdetail.ftl 最可靠
3. **多语言版本**：切换 `lang=en` / `lang=zh` 可切换页面语言（英文版岗位数量可能不同）

## 快速提取 JD 的方法

```javascript
// browser_console 表达式
document.body.innerText.substring(0, 5000)
```

MTR Taleo 页面 body 长度约 3000+ 字符，JD 从 "Responsibilities" 标题后开始，可直接提取全文。

## 适用公司

以下香港公司已知使用 Taleo ATS：
- MTR Corporation
- HSBC（部分岗位）
- 其他使用 Oracle Taleo 的大企业

找到 Taleo 岗位时，先尝试 `https://{company}.taleo.net/careersection/.../jobdetail.ftl?job={REQ_ID}` 直接访问。
