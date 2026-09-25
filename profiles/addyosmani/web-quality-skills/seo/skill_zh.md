# SEO优化

基于Lighthouse SEO审计和Google搜索指南的搜索引擎优化。重点关注技术SEO、页面优化和结构化数据。

## 基于证据的审计工作流程

当渲染页面可用时：

1.  当该功能可用时，运行实时Lighthouse SEO和Agentic Browsing检查；使用Chrome DevTools MCP，使用`lighthouse_audit`。使用结果定位渲染页面的失败。
2.  检查Lighthouse无法自行建立的信号：响应头、重定向、`robots.txt`、站点地图覆盖率、页面模板中规范一致性、结构化数据资格，以及当用户提供访问权限时搜索控制台证据。
3.  将技术爬取/索引发现与内容质量和权威性分开。不要编造排名因素权重或承诺排名变化。
4.  修复源代码并重新运行相同的检查。对于索引或排名结果，报告搜索引擎验证仍然悬而未决。

如果实时工具不可用，请使用特定类别的Lighthouse CLI输出以及直接源和HTTP检查。Lighthouse SEO分数涵盖技术检查的有用子集；它不是排名预测。

| 区域 | 此技能可以验证的内容 |
|------|----------------------|
| 爬取和索引控制 | 技术配置和一致性 |
| 渲染元数据和语义 | 存在性、有效性以及页面模板问题 |
| 结构化数据 | 语法和资格信号，但不保证丰富结果 |
| 核心网络价值 | 链接到核心网络价值技能的测量字段/实验室证据 |
| 内容有用性和权威性 | 审查质量，但不要分配合成排名百分比 |

---

## 技术SEO

### 爬取能力

**robots.txt:**
```text
# /robots.txt
User-agent: *
Allow: /

# 禁止管理/私有区域
Disallow: /admin/
Disallow: /api/
Disallow: /private/

# 不要阻止渲染所需的资源
# ❌ Disallow: /static/

Sitemap: https://example.com/sitemap.xml
```

**Meta robots:**
```html
<!-- 默认：可索引，可跟随 -->
<meta name="robots" content="index, follow">

<!-- 不索引特定页面 -->
<meta name="robots" content="noindex, nofollow">

<!-- 可索引但不要跟随链接 -->
<meta name="robots" content="index, nofollow">

<!-- 控制片段 -->
<meta name="robots" content="max-snippet:150, max-image-preview:large">
```

**规范URL:**
```html
<!-- 防止重复内容问题 -->
<link rel="canonical" href="https://example.com/page">

<!-- 自引用规范（推荐） -->
<link rel="canonical" href="https://example.com/current-page">

<!-- 用于分页内容 -->
<link rel="canonical" href="https://example.com/products">
<!-- 或者使用 rel="prev" / rel="next" 用于显式分页 -->
```

### XML站点地图

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

**站点地图最佳实践:**
- 每个站点地图最多50,000个URL或50MB
- 对于大型网站使用站点地图索引
- 仅包含规范、可索引的URL
- 内容更改时更新`lastmod`
- 提交到Google搜索控制台

### URL结构

```
✅ 良好URL:
https://example.com/products/blue-widget
https://example.com/blog/how-to-use-widgets

❌ 差劲URL:
https://example.com/p?id=12345
https://example.com/products/item/category/subcategory/blue-widget-2024-sale-discount
```

**URL指南:**
- 使用连字符，不要使用下划线
- 全部小写
- 保持简短（< 75个字符）
- 自然包含目标关键词
- 尽可能避免参数
- 始终使用HTTPS

### HTTPS & 安全

```html
<!-- 确保所有资源使用HTTPS -->
<img src="https://example.com/image.jpg">

<!-- 不使用: -->
<img src="http://example.com/image.jpg">
```

**用于SEO信任信号的 安全头:**
```
Strict-Transport-Security: max-age=31536000; includeSubDomains
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
```

---

## 页面SEO

### 标题标签

```html
<!-- ❌ 缺失或通用 -->
<title>Page</title>
<title>Home</title>

<!-- ✅ 描述性，包含主要关键词 -->
<title>Blue Widgets for Sale | Premium Quality | Example Store</title>
```

**标题标签指南:**
- 仅使用50-60个字符作为粗略的检查代理，而不是通过/失败限制。Google会根据渲染设备的宽度截断标题链接，因此当工具支持时请预览宽度。
- 自然地在开头描述页面主题
- 每个页面唯一
- 当有助于用户区分结果时添加品牌
- 适当时候采用行动导向

将标题链接重写与截断分开。即使`<title>`很短，Google也可能根据可见页面标题、标题、锚文本和其他来源构建不同的标题链接；调查准确性和一致性，而不是自动缩短它。参见[Google的标题链接指南](https://developers.google.com/search/docs/appearance/title-link)。

### 元描述

```html
<!-- ❌ 缺失或重复 -->
<meta name="description" content="">

<!-- ✅ 有吸引力且唯一 -->
<meta name="description" content="Shop premium blue widgets with free shipping. 30-day returns. Rated 4.9/5 by 10,000+ customers. Order today and save 20%.">
```

**元描述指南:**
- 仅使用150-160个字符作为检查代理。片段取决于查询和设备，Google可能会选择页面内容而不是元描述。
- 自然使用页面主题
- 有吸引力的行动号召
- 每个页面唯一
- 与页面内容匹配

### 标题结构

```html
<!-- ❌ 差劲结构 -->
<h2>Welcome to Our Store</h2>
<h4>Products</h4>
<h1>Contact Us</h1>

<!-- ✅ 正确的层次结构 -->
<h1>Blue Widgets - Premium Quality</h1>
  <h2>Product Features</h2>
    <h3>Durability</h3>
    <h3>Design</h3>
  <h2>Customer Reviews</h2>
  <h2>Pricing</h2>
```

**标题指南:**
- 使主要页面标题描述性，层次结构明确；不要因为有效的HTML包含多个`<h1>`而失败页面
- 逻辑层次结构（不要跳过级别）
- 自然包含关键词
- 描述性，不是通用

### 图片SEO

```html
<!-- ❌ 差劲的图片SEO -->
<img src="IMG_12345.jpg">

<!-- ✅ 优化后的图片 -->
<img src="blue-widget-product-photo.webp"
     alt="Blue widget with chrome finish, side view showing control panel"
     width="800"
     height="600"
     loading="lazy">
```

**图片指南:**
- 包含关键词的描述性文件名
- 描述图片内容的替代文本
- 压缩并适当大小
- WebP/AVIF带回退
- 懒加载折叠以下图片

### 内部链接

```html
<!-- ❌ 非描述性 -->
<a href="/products">Click here</a>
<a href="/widgets">Read more</a>

<!-- ✅ 描述性锚文本 -->
<a href="/products/blue-widgets">Browse our blue widget collection</a>
<a href="/guides/widget-maintenance">Learn how to maintain your widgets</a>
```

**链接指南:**
- 包含关键词的描述性锚文本
- 链接到相关的内部页面
- 每个页面合理的链接数量
- 及时修复损坏的链接
- 使用面包屑导航层次结构

---

## 结构化数据（JSON-LD）

当用户请求模式标记或审计发现结构化数据问题时，请阅读[结构化数据参考](references/STRUCTURED-DATA.md)。它包含组织、文章、产品、常见问题解答和面包屑示例以及验证链接。

* **描述可见、准确的内容。** 不要仅为了获得丰富结果而添加类型或声称。
* **使用最具体的适用类型。** 保持标识符和绝对URL在渲染之间稳定。
* **验证渲染输出。** 通过语法并不保证搜索引擎资格或显示。

## 代理浏览和AI可发现性

将这些概念分开：

* **Lighthouse代理浏览** 衡量帮助助手理解和与渲染页面交互的技术信号。当前检查包括面向代理的可访问性树、可选的`llms.txt`和WebMCP注册、模式和表单覆盖率（当存在时）。
* **搜索索引和排名** 取决于搜索引擎系统，不能从代理浏览分数中推断。
* **AI摄取或引用** 是产品特定的。技术可浏览的页面或有效的`llms.txt`文件并不能证明AI产品会摄取、排名或引用它。

优先考虑语义HTML、描述性标签、可爬取内容、准确元数据和清晰的页面结构，因为它们有利于人类、搜索引擎和代理。仅在应用程序有有用的操作要暴露且用户希望集成时才添加WebMCP工具；使用Lighthouse验证工具名称、描述、模式和表单注释。

### 爬取控制是产品特定的

分别审计每个记录的用户代理，而不是应用“AI机器人”规则：

| 控制 | 记录目的 | 阻止的效果 |
|------|----------|----------|
| `OAI-SearchBot` | ChatGPT搜索发现 | 防止页面内容被包含在ChatGPT摘要和片段中；链接和标题可能通过第三方发现显示 |
| `PerplexityBot` | Perplexity搜索索引 | 防止该爬取器索引被阻止的内容用于搜索结果 |
| `Claude-SearchBot` / `Claude-User` | Claude搜索索引 / 用户导向检索 | 可能降低搜索可见性 / 防止用户导向请求的检索 |
| `Google-Extended` | 控制某些Gemini训练和内容Google爬取的接地使用 | 不影响Google搜索包含或排名 |

训练控制（如`GPTBot`和`ClaudeBot`）与搜索和用户获取控制不同。`GoogleOther`是一个通用爬取器，不是AI搜索可见性开关。在供应商维护的文档中验证当前名称和后果：[OpenAI](https://help.openai.com/en/articles/12627856-publishers-and-developers-faq)、[Perplexity](https://docs.perplexity.ai/docs/resources/perplexity-crawlers)、[Anthropic](https://privacy.anthropic.com/en/articles/8896518-does-anthropic-crawl-data-from-the-web-and-how-can-site-owners-block-the-crawler)和[Google](https://developers.google.com/crawling/docs/crawlers-fetchers/google-common-crawlers)。

### `llms.txt` 是可选的

`llms.txt`是一个实验性提案，不是跨供应商发现标准。Lighthouse可以验证`/llms.txt`的可用性和形状，但这并不能证明目标产品会读取它。仅在用户请求或记录的消费者支持时添加一个；不要在爬取能力、语义HTML、准确元数据和有用内容之前推荐它。永远不要将其视为排名或引用因素，不要复制站点地图，或重新组织内容仅为了提高此审计。

---

## 移动SEO

### 响应式设计

```html
<!-- ❌ 不适合移动设备 -->
<meta name="viewport" content="width=1024">

<!-- ✅ 响应式视口 -->
<meta name="viewport" content="width=device-width, initial-scale=1">
```

### 点击目标

```css
/* ❌ 移动设备太小 */
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
/* ❌ 移动设备太小 */
body {
  font-size: 10px;
}

/* ✅ 不需要缩放即可阅读 */
body {
  font-size: 16px;
  line-height: 1.5;
}
```

---

## 国际SEO

### Hreflang标签

```html
<!-- 用于多语言网站 -->
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

## SEO审计清单

### 关键
- [ ] 启用HTTPS
- [ ] robots.txt允许爬取
- [ ] 重要页面没有`noindex`
- [ ] 标题标签存在且唯一
- [ ] 主要页面标题描述性且层次结构逻辑

### 高优先级
- [ ] 元描述存在
- [ ] 提交站点地图
- [ ] 设置规范URL
- [ ] 响应式移动设备
- [ ] 核心网络价值通过

### 中优先级
- [ ] 实现结构化数据
- [ ] 内部链接策略
- [ ] 图片替代文本
- [ ] 描述性URL
- [ ] 面包屑导航
- [ ] 当代理访问重要时审查代理浏览失败

### 持续
- [ ] 在搜索控制台中修复爬取错误
- [ ] 内容更改时更新站点地图
- [ ] 监控排名变化
- [ ] 检查损坏的链接
- [ ] 审查搜索控制台洞察

---

## 工具

| 工具 | 使用 |
|------|------|
| Google搜索控制台 | 监控索引，修复问题 |
| Google PageSpeed Insights | 性能+核心网络价值 |
| 丰富结果测试 | 验证结构化数据 |
| 实时Lighthouse审计（Chrome DevTools MCP: `lighthouse_audit`） | 代理的渲染SEO和代理浏览检查 |
| Lighthouse CLI | SEO审计回退 |
| Screaming Frog | 爬取分析 |

## 参考

- [Google搜索中心](https://developers.google.com/search)
- [Schema.org](https://schema.org/)
- [核心网络价值](../core-web-vitals/SKILL.md)
- [Web质量审计](../web-quality-audit/SKILL.md)
