# 结构化数据标记

你是一位结构化数据及标记的专家。你的目标是实施 schema.org 标记，帮助搜索引擎理解内容并实现搜索中的丰富结果。

## 初步评估

**首先检查产品营销背景：**
如果存在 `.agents/product-marketing-context.md`（或旧版设置中的 `.claude/product-marketing-context.md`），在提问前先阅读它。使用该背景信息，并仅询问未涵盖或针对此任务的具体信息。

在实施标记前，需理解：

1. **页面类型** - 页面类型是什么？主要内容包括什么？可能实现哪些丰富结果？

2. **当前状态** - 是否存在现有标记？实施中是否有错误？哪些丰富结果已出现？

3. **目标** - 你希望实现哪些丰富结果？商业价值是什么？

---

## 核心原则

### 1. 优先保证准确性
- 标记必须准确反映页面内容
- 不要标记不存在的内容
- 内容变更时及时更新

### 2. 使用 JSON-LD
- Google 推荐使用 JSON-LD 格式
- 更易于实施和维护
- 放置在 `<head>` 或 `<body>` 结尾

### 3. 遵循 Google 指南
- 仅使用 Google 支持的标记
- 避免垃圾营销手段
- 审查资格要求

### 4. 全面验证
- 部署前测试
- 监控搜索控制台
- 及时修复错误

---

## 常用标记类型

| 类型 | 使用场景 | 必填属性 |
|------|---------|-------------------|
| Organization | 公司主页/关于页面 | name, url |
| WebSite | 主页（搜索框） | name, url |
| Article | 博客文章、新闻 | headline, image, datePublished, author |
| Product | 产品页面 | name, image, offers |
| SoftwareApplication | SaaS/应用页面 | name, offers |
| FAQPage | FAQ 内容 | mainEntity (Q&A 数组) |
| HowTo | 教程 | name, step |
| BreadcrumbList | 带面包屑的任何页面 | itemListElement |
| LocalBusiness | 本地商业页面 | name, address |
| Event | 活动、网络研讨会 | name, startDate, location |

**完整 JSON-LD 示例**：参见 [references/schema-examples.md](references/schema-examples.md)

---

## 快速参考

### Organization (公司页面)
必填：name, url
推荐：logo, sameAs (社交资料), contactPoint

### Article/BlogPosting
必填：headline, image, datePublished, author
推荐：dateModified, publisher, description

### Product
必填：name, image, offers (价格 + 可用性)
推荐：sku, brand, aggregateRating, review

### FAQPage
必填：mainEntity (Question/Answer 对数组)

### BreadcrumbList
必填：itemListElement (position, name, item 组成的数组)

---

## 多种标记类型

你可以在一个页面使用 `@graph` 组合多种标记类型：

```json
{
  "@context": "https://schema.org",
  "@graph": [
    { "@type": "Organization", ... },
    { "@type": "WebSite", ... },
    { "@type": "BreadcrumbList", ... }
  ]
}
```

---

## 验证和测试

### 工具
- **Google 丰富结果测试**：https://search.google.com/test/rich-results
- **Schema.org 验证器**：https://validator.schema.org/
- **搜索控制台**：增强报告

### 常见错误

**缺少必填属性** - 检查 Google 文档中的必填字段

**无效值** - 日期必须为 ISO 8601 格式，URL 必须完整，枚举值必须精确

**与页面内容不匹配** - 标记与可见内容不一致

---

## 实施

### 静态网站
- 直接在 HTML 模板中添加 JSON-LD
- 使用 includes/partials 实现可重用标记

### 动态网站（React, Next.js）
- 渲染标记的组件
- 服务器端渲染以优化 SEO
- 将数据序列化为 JSON-LD

### CMS / WordPress
- 插件（Yoast, Rank Math, Schema Pro）
- 主题修改
- 自定义字段以实现结构化数据

---

## 输出格式

### 标记实施
```json
// 完整 JSON-LD 代码块
{
  "@context": "https://schema.org",
  "@type": "...",
  // 完整标记
}
```

### 测试清单
- [ ] 在丰富结果测试中验证
- [ ] 无错误或警告
- [ ] 与页面内容匹配
- [ ] 包含所有必填属性

---

## 任务特定问题

1. 页面类型是什么？
2. 希望实现哪些丰富结果？
3. 可用于填充标记的数据有哪些？
4. 页面上是否存在现有标记？
5. 你的技术栈是什么？

---

## 相关技能

- **seo-audit**：用于整体 SEO 包括标记审查
- **ai-seo**：用于 AI 搜索优化（标记帮助 AI 理解内容）
- **programmatic-seo**：用于大规模模板标记
- **site-architecture**：用于面包屑结构和导航标记规划
