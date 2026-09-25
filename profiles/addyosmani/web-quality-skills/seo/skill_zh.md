# SEO 优化

基于 Lighthouse SEO 审计和 Google 搜索指南的搜索引擎优化。重点在于技术 SEO、页面优化和结构化数据。

## 以证据为基础的审计工作流

当渲染后的页面可用时：

1. 当该功能可用时，运行实时的 Lighthouse SEO 和智能浏览检查；使用 Chrome DevTools MCP 时，使用 `lighthouse_audit`。利用结果定位渲染页面的失败问题。
2. 检查 Lighthouse 无法自行建立的信号：响应头、重定向、`robots.txt`、站点地图覆盖率、页面模板中规范 URL 的一致性、结构化数据适用性，以及当用户提供访问权限时的 Search Console 证据。
3. 将技术爬取/索引发现与内容质量和权威性区分开来。不要编造排名因素权重或承诺排名变化。
4. 修复源问题并重跑相同的检查。对于索引或排名结果，报告搜索引擎验证仍待完成。

如果实时工具不可用，使用分类特定的 Lighthouse CLI 输出以及源文件和 HTTP 的直接检查。Lighthouse SEO 评分涵盖了一部分有用的技术检查，但并非排名预测。

| 领域 | 该技能可验证的内容 |
|------|----------------------------|
| 爬取和索引控制 | 技术配置与一致性 |
| 渲染元数据与语义 | 存在性、有效性和页面模板问题 |
| 结构化数据 | 语法和适用性信号，而非保证丰富结果 |
| Core Web Vitals | 链接至 Core Web Vitals 技能中测得的字段/实验室证据 |
| 内容实用性与权威性 | 审查质量，但不得分配人工合成的排名百分比 |

---

## 技术 SEO

### 可爬取性

**robots.txt：**
```text
# /robots.txt
User-agent: *
Allow: /

# 屏蔽管理/私有区域
Disallow: /admin/
Disallow: /api/
Disallow: /private/

# 不要屏蔽渲染所需的资源
# ❌ Disallow: /static/

Sitemap: https://example.com/sitemap.xml
```

**Meta robots：**
```html
<!-- 默认：可被索引、可跟随 -->
<meta name="robots" content="index, follow">

<!-- 禁止特定页面索引 -->
<meta name="robots" content="noindex, nofollow">

<!-- 可被索引但不跟随链接 -->
<meta name="robots" content="index, nofollow">

<!-- 控制片段 -->
<meta name="robots" content="max-snippet:150, max-image-preview:large">
```

**规范 URL：**
```html
<!-- 防止重复内容问题 -->
<link rel="canonical" href="https://example.com/page">

<!-- 自引用规范 URL（推荐） -->
<link rel="canonical" href="https://example.com/current-page">

<!-- 针对分页内容 -->
<link rel="canonical" href="https://example.com/products">
<!-- 或使用 rel="prev" / rel="next" 进行显式分页 -->
```

### XML 站点地图

```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://example.com/</loc>
    <lastmod>2024-01-15</lastmod>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
  </url>
  <url>
    <loc>https://example.com/products</loc>
    <lastmod>2024-01-14</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
  </url>
</urlset>
```

**站点地图最佳实践：**
- 每个站点地图最多 50,000 个 URL 或 50MB
- 对于大型网站，使用站点地图索引
- 仅包含规范、可被索引的 URL
- 内容更新时更新 `lastmod`
- 提交至 Google Search Console

### URL 结构

```
✅ 良好 URL：
https://example.com/products/blue-widget
https://example.com/blog/how-to-use-widgets

❌ 不佳 URL：
https://example.com/p?id=12345
https://example.com/products/item/category/subcategory/blue-widget-2024-sale-discount
```

**URL 指南：**
- 使用连字符，而非下划线
- 仅使用小写
- 保持简短（少于 75 个字符）
- 自然包含目标关键词
- 尽量避免参数
- 始终使用 HTTPS

### HTTPS 与安全

```html
<!-- 确保所有资源使用 HTTPS -->
<img src="https://example.com/image.jpg">

<!-- 不使用： -->
<img src="http://example.com/image.jpg">
```

**用于 SEO 信任信号的 security headers：**
```
Strict-Transport-Security: max-age=31536000; includeSubDomains
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
```

---

## 页面 SEO

### 标题标签

```html
<!-- ❌ 缺失或过于通用 -->
<title>Page</title>
<title>Home</title>

<!-- ✅ 具有描述性并包含主要关键词 -->
<title>Blue Widgets for Sale | Premium Quality | Example Store</title>
```

**标题标签指南：**
- 仅以 50–60 个字符作为粗略的 linting 代理，而非通过/失败限制。Google 会根据渲染设备的宽度截断标题链接，因此当工具支持时，请预览宽度。
- 在页面主题处自然描述页面内容
- 每个页面唯一
- 当有助于用户区分结果时添加品牌
- 在适当情况下采用行动导向

将标题链接改写与截断分开处理。即使 `<title>` 较短，Google 也可能根据可见页面标题、标题、锚文本和其他来源构建不同的标题链接；因此应调查准确性和一致性，而非自动缩短。参见 [Google 的标题链接指南](https://developers.google.com/search/docs/appearance/title-link)。

### Meta 描述

```html
<!-- ❌ 缺失或重复 -->
<meta name="description" content="">

<!-- ✅ 具有吸引力和唯一性 -->
<meta name="description" content="购买优质蓝色元件，享受免费配送。支持 30 天退换。10,000+  customers 评分 4.9/5。立即下单，立享 20% 优惠。">
```

**Meta 描述指南：**
- 仅以大约 150–160 个字符作为 linting 代理。摘要取决于查询和设备，且 Google 可能选择页面内容而非 Meta 描述。
- 自然使用页面主题
- 具有吸引力的行动号召
- 每个页面唯一
- 与页面内容匹配

### 标题结构

```html
<!-- ❌ 结构不佳 -->
<h2>Welcome to Our Store</h2>
<h4>Products</h4>
<h1>Contact Us</h1>

<!-- ✅ 结构合理 -->
<h1>Blue Widgets - Premium Quality</h1>
  <h2>Product Features</h2>
    <h3>Durability</h3>
    <h3>Design</h3>
  <h2>Customer Reviews</h2>
  <h2>Pricing</h2>
```

**标题指南：**
- 使主要页面标题具有描述性且层级明确；不要仅因有效 HTML 包含多个 `<h1>` 就判定页面不合格
- 逻辑层级（不要跳级）
- 自然包含关键词
- 具有描述性，而非通用性

### 图像 SEO

```html
<!-- ❌ 图像 SEO 不佳 -->
<img src="IMG_12345.jpg">

<!-- ✅ 优化后的图像 -->
<img src="blue-widget-product-photo.webp"
     alt="带有铬质饰面的蓝色元件，侧视图显示控制面板"
     width="800"
     height="600"
     loading="lazy">
```

**图像指南：**
- 包含关键词的描述性文件名
- Alt 文本描述图像内容
- 经过压缩并正确尺寸
- 使用 WebP/AVIF 并附带回退方案
- 懒加载下方图像

### 内部链接

```html
<!-- ❌ 锚文本描述不准确 -->
<a href="/products">Click here</a>
<a href="/widgets">Read more</a>

<!-- ✅ 描述性锚文本 -->
<a href="/products/blue-widgets">浏览我们的蓝色元件系列</a>
<a href="/guides/widget-maintenance">学习如何维护您的元件</a>
```

**链接指南：**
- 包含关键词的描述性锚文本
- 链接至相关的内部页面
- 每页合理的链接数量
- 及时修复断链
- 使用面包屑导航体现层级

---

## 结构化数据（JSON-LD）

当用户请求 schema 标记或审计发现结构化数据问题时，阅读 [结构化数据参考](references/STRUCTURED-DATA.md)。其中包含 Organization、Article、Product、FAQ 和 Breadcrumb 示例以及验证链接。

* **描述可见、准确的内容。** 不要仅为了获得丰富结果而添加类型或声明。
* **使用最具体适用的类型。** 保持标识符和绝对 URL 在渲染过程中稳定。
* **验证渲染输出。** 语法通过并不保证搜索引擎适用性或显示效果。

## 智能浏览与 AI 可发现性

将以下概念分开理解：

* **Lighthouse 智能浏览**测量有助于助手理解并与渲染页面交互的技术信号。当前检查包括面向代理的无障碍树、可选的 `llms.txt`，以及存在时的 WebMCP 注册、模式和表单覆盖。
* **搜索索引与排名**取决于搜索引擎系统，无法从智能浏览评分中推断。
* **AI 摄取或引用**是产品特定的。技术可浏览的页面或有效的 `llms.txt` 文件并不能证明 AI 产品会摄取、排名或引用它。

优先采用语义 HTML、描述性标签、可抓取内容、准确的元数据以及清晰的页面结构，因为这既有益于用户、搜索引擎和智能体。仅在应用有可暴露的有用操作且用户希望进行该集成时，才添加 WebMCP 工具；使用 Lighthouse 验证工具名称、描述、模式和表单标注。

### 爬虫控制具有产品特定性

不要统一应用“AI 机器人”规则，而是逐一审计每个文档中记录的用户代理：

| 控制 | 文档中记录的目的 | 阻塞后的效果 |
|---------|--------------------|--------------------|
| `OAI-SearchBot` | ChatGPT 搜索发现 | 阻止页面内容被包含在 ChatGPT 摘要和片段中；链接和标题仍可能通过第三方发现显示 |
| `PerplexityBot` | Perplexity 搜索索引 | 阻止该爬虫对阻止的内容进行搜索结果索引 |
| `Claude-SearchBot` / `Claude-User` | Claude 搜索索引 / 用户定向检索 | 可能降低搜索可见性 / 防止针对用户定向请求的检索 |
| `Google-Extended` | 控制 Google 爬虫对特定 Gemini 训练和地面场景内容的访问 | 不影响 Google 搜索收录或排名 |

诸如 `GPTBot` 和 `ClaudeBot` 之类的训练控制在搜索和用户获取控制方面是不同的。`GoogleOther` 是通用爬虫，而非 AI 搜索可见性开关。请在供应商维护的文档中核实当前名称和后果：[OpenAI](https://help.openai.com/en/articles/12627856-publishers-and-developers-faq)、[Perplexity](https://docs.perplexity.ai/docs/resources/perplexity-crawlers)、[Anthropic](https://privacy.anthropic.com/en/articles/8896518-does-anthropic-crawl-data-from-the-web-and-how-can-site-owners-block-the-crawler) 和 [Google](https://developers.google.com/crawling/docs/crawlers-fetchers/google-common-crawlers)。

### `llms.txt` 为可选

`llms.txt` 是实验性提案，而非跨供应商的发现标准。Lighthouse 可以验证 `/llms.txt` 的存在和结构，但这并不能表明目标产品会读取它。仅在用户请求或已记录的消费端支持时才添加它；不要将其置于可爬取性、语义 HTML、准确元数据和实用内容之前进行推荐。切勿将其视为排名或引用因素，也不得重复站点地图，或仅为此审计重新组织内容。

---

## 移动端 SEO

### 响应式设计

```html
<!-- ❌ 不便于移动端 -->
<meta name="viewport" content="width=1024">

<!-- ✅ 响应式视口 -->
<meta name="viewport" content="width=device-width, initial-scale=1">
```

### 点击目标

```css
/* ❌ 移动端太小 */
.small-link {
  padding: 4px;
  font-size: 12px;
}

/* ✅ 足够的点击目标 */
.mobile-friendly-link {
  padding: 12px;
  font-size: 16px;
  min-height: 48px;
  min-width: 48px;
}
```

### 字体大小

```css
/* ❌ 移动端太小 */
body {
  font-size: 10px;
}

/* ✅ 无需缩放即可阅读 */
body {
  font-size: 16px;
  line-height: 1.5;
}
```

---

## 国际 SEO

### hreflang 标签

```html
<!-- 针对多语言网站 -->
<link rel="alternate" hreflang="en" href="https://example.com/page">
<link rel="alternate" hreflang="es" href="https://example.com/es/page">
<link rel="alternate" hreflang="fr" href="https://example.com/fr/page">
<link rel="alternate" hreflang="x-default" href="https://example.com/page">
```

### 语言声明

```html
<html lang="en">
<!-- 或 -->
<html lang="es-MX">
```

---

## SEO 审计清单

### 关键
- [ ] 启用 HTTPS
- [ ] robots.txt 允许爬取
- [ ] 重要页面无 `noindex`
- [ ] 标题标签存在且唯一
- [ ] 主要页面标题具有描述性且层级逻辑

### 高优先级
- [ ] 包含 Meta 描述
- [ ] 已提交站点地图
- [ ] 已设置规范 URL
- [ ] 支持移动端响应式
- [ ] Core Web Vitals 通过

### 中优先级
- [ ] 已实现结构化数据
- [ ] 内部链接策略
- [ ] 图像 Alt 文本
- [ ] 描述性 URL
- [ ] 面包屑导航
- [ ] 当智能体访问重要时，审查智能浏览失败情况

### 持续进行
- [ ] 在 Search Console 中修复爬取错误
- [ ] 内容更新时更新站点地图
- [ ] 监控排名变化
- [ ] 检查断链
- [ ] 审查 Search Console 洞察

---

## 工具

| 工具 | 用途 |
|------|-----|
| Google Search Console | 监控索引，修复问题 |
| Google PageSpeed Insights | 性能 + Core Web Vitals |
| Rich Results Test | 验证结构化数据 |
| 实时 Lighthouse 审计（Chrome DevTools MCP：`lighthouse_audit`） | 面向智能体的渲染 SEO 和智能浏览检查 |
| Lighthouse CLI | SEO 审计备用方案 |
| Screaming Frog | 爬取分析 |

## 参考资料

- [Google Search Central](https://developers.google.com/search)
- [Schema.org](https://schema.org/)
- [Core Web Vitals](../core-web-vitals/SKILL.md)
- [Web Quality Audit](../web-quality-audit/SKILL.md)
