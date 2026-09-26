# SEO 优化器

## 概述

该技能为 HTML/CSS 网站提供全面的 SEO 优化功能。它分析网站的 SEO 问题，实施最佳实践，并生成涵盖所有关键 SEO 方面的优化报告，包括元标签、标题结构、图像优化、模式标记、移动优化和技术 SEO。

## 何时使用此技能

当用户请求以下内容时使用此技能：
- "分析我的网站 SEO 问题"
- "为 SEO 优化此页面"
- "生成 SEO 审计报告"
- "修复我的网站的 SEO 问题"
- "给我的页面添加适当的元标签"
- "实施模式标记"
- "生成站点地图"
- "提高我的网站的搜索引擎排名"
- 任何与 HTML/CSS 网站搜索引擎优化相关的任务

## 工作流程

### 1. 初始 SEO 分析

使用 SEO 分析器脚本进行全面分析：

```bash
python scripts/seo_analyzer.py <目录或文件>
```

此脚本分析 HTML 文件并生成详细报告，涵盖：
- 标题标签（长度、存在性、唯一性）
- 元描述（长度、存在性）
- 标题结构（H1-H6 层次结构）
- 图像 alt 属性
- Open Graph 标签
- Twitter Card 标签
- Schema.org 标记
- HTML lang 属性
- 视口和字符集元标签
- 规范 URL
- 内容长度

**输出选项**：
- 默认：人类可读的文本报告，包含问题、警告和良好实践
- `--json`：机器可读的 JSON 格式，用于程序化处理

**示例用法**：
```bash
# 分析单个文件
python scripts/seo_analyzer.py index.html

# 分析整个目录
python scripts/seo_analyzer.py ./public

# 获取 JSON 输出
python scripts/seo_analyzer.py ./public --json
```

### 2. 审查分析结果

分析器将发现结果分为三个级别：

**严重问题（🔴）** - 立即修复：
- 缺少标题标签
- 缺少元描述
- 缺少 H1 标题
- 缺少 alt 属性的图像
- 缺少 HTML lang 属性

**警告（⚠️）** - 为优化 SEO 尽快修复：
- 标题/描述长度不理想
- 多个 H1 标签
- 缺少 Open Graph 或 Twitter Card 标签
- 缺少视口元标签
- 缺少模式标记
- 标题层次结构问题

**良好实践（✅）** - 已优化：
- 正确格式化的元素
- 正确的长度
- 存在必要的标签

### 3. 优先级排序和修复问题

按优先级顺序处理问题：

#### 优先级 1：严重问题

**缺少或不良标题标签**：
```html
<!-- 在 <head> 中添加独特、描述性的标题 -->
<title>主要关键词 - 次要关键词 | 品牌名称</title>
```
- 保持 50-60 个字符
- 在开头包含目标关键词
- 每个页面保持唯一

**缺少元描述**：
```html
<!-- 在 <head> 中添加引人入胜的描述 -->
<meta name="description" content="清晰、简洁的描述，包含目标关键词并鼓励点击。150-160 个字符。">
```

**缺少 H1 或多个 H1**：
- 确保每页只有一个 H1
- H1 应描述主要主题
- 应与标题标签匹配或相关

**缺少 alt 文本的图像**：
```html
<!-- 为所有图像添加描述性 alt 文本 -->
<img src="image.jpg" alt="描述图像内容的文本">
```

**缺少 HTML Lang 属性**：
```html
<!-- 添加到开头的 <html> 标签 -->
<html lang="en">
```

#### 优先级 2：重要优化

**视口元标签**（对移动 SEO 至关重要）：
```html
<meta name="viewport" content="width=device-width, initial-scale=1.0">
```

**字符集声明**：
```html
<meta charset="UTF-8">
```

**Open Graph 标签**（用于社交媒体分享）：
```html
<meta property="og:title" content="您的页面标题">
<meta property="og:description" content="您的页面描述">
<meta property="og:image" content="https://example.com/image.jpg">
<meta property="og:url" content="https://example.com/page-url">
<meta property="og:type" content="website">
```

**Twitter Card 标签**：
```html
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="您的页面标题">
<meta name="twitter:description" content="您的页面描述">
<meta name="twitter:image" content="https://example.com/image.jpg">
```

**规范 URL**：
```html
<link rel="canonical" href="https://example.com/preferred-url">
```

#### 优先级 3：高级优化

**模式标记** - 参考 `references/schema_markup_guide.md` 获取详细实现说明。常见类型：
- 组织（主页）
- Article/BlogPosting（博客文章）
- LocalBusiness（本地企业）
- Breadcrumb（导航）
- FAQ（FAQ 页面）
- Product（电子商务）

示例实现：
```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "文章标题",
  "author": {
    "@type": "Person",
    "name": "作者名称"
  },
  "datePublished": "2024-01-15",
  "image": "https://example.com/image.jpg"
}
</script>
```

### 4. 生成或更新站点地图

修复问题后，生成 XML 站点地图：

```bash
python scripts/generate_sitemap.py <目录> <基本 URL> [输出文件]
```

**示例**：
```bash
# 为网站生成站点地图
python scripts/generate_sitemap.py ./public https://example.com

# 指定输出位置
python scripts/generate_sitemap.py ./public https://example.com ./public/sitemap.xml
```

该脚本：
- 自动查找所有 HTML 文件
- 生成正确的 URL
- 包含最后修改日期
- 估计优先级和更改频率值
- 创建格式正确的 XML 站点地图

**生成后**：
1. 将 sitemap.xml 上传到网站根目录
2. 在 robots.txt 中添加引用
3. 提交给 Google Search Console 和 Bing Webmaster Tools

### 5. 更新 robots.txt

使用 `assets/robots.txt` 中的模板并自定义：

```
User-agent: *
Allow: /

# 阻止敏感目录
Disallow: /admin/
Disallow: /private/

# 引用您的站点地图
Sitemap: https://yourdomain.com/sitemap.xml
```

将 robots.txt 放在网站根目录。

### 6. 验证和测试

实施修复后：

**本地测试**：
1. 再次运行 SEO 分析器以验证修复
2. 确保所有严重问题已解决
3. 确保未引入新问题

**在线测试**：
1. 将更改部署到生产环境
2. 使用 Google Rich Results Test 测试：https://search.google.com/test/rich-results
3. 验证模式标记：https://validator.schema.org/
4. 检查移动友好性：https://search.google.com/test/mobile-friendly
5. 在 Google Search Console 中监控

### 7. 持续优化

**定期维护**：
- 添加新页面时更新站点地图
- 保持元描述新鲜且引人入胜
- 确保新图像有 alt 文本
- 为新内容类型添加模式标记
- 在 Google Search Console 中监控问题
- 定期更新内容

## 常见优化模式

### 模式 1：新网站设置

对于全新的 HTML/CSS 网站：

1. 运行初始分析：`python scripts/seo_analyzer.py ./public`
2. 在所有页面添加基本元标签（标题、描述、视口）
3. 确保正确的标题结构（每页一个 H1）
4. 为所有图像添加 alt 文本
5. 在主页实施组织模式标记
6. 生成站点地图：`python scripts/generate_sitemap.py ./public https://yourdomain.com`
7. 使用模板创建 robots.txt
8. 部署并提交站点地图到搜索引擎

### 模式 2：现有网站审计

对于需要优化的现有网站：

1. 运行全面分析：`python scripts/seo_analyzer.py ./public`
2. 识别并按优先级排序问题（首先解决严重问题）
3. 在所有页面修复严重问题
4. 添加缺少的 Open Graph 和 Twitter Card 标签
5. 为适当页面实施模式标记
6. 更新站点地图
7. 使用分析器验证修复
8. 部署并监控

### 模式 3：单个页面优化

对于优化特定页面：

1. 分析特定文件：`python scripts/seo_analyzer.py page.html`
2. 修复识别的问题
3. 优化标题和元描述以包含目标关键词
4. 确保正确的标题层次结构
5. 为页面类型添加适当的模式标记
6. 使用分析器验证
7. 更新站点地图（如果新页面）

### 模式 4：博客文章优化

对于博客文章和文章：

1. 确保唯一的标题（50-60 个字符）包含目标关键词
2. 写引人入胜的元描述（150-160 个字符）
3. 使用单个 H1 作为文章标题
4. 使用正确的 H2/H3 层次结构进行分段
5. 为所有图像添加 alt 文本
6. 实施文章或 BlogPosting 模式（参考 `references/schema_markup_guide.md`）
7. 添加 Open Graph 和 Twitter Card 标签以用于社交媒体分享
8. 包含作者信息
9. 添加面包屑模式以用于导航

## 参考资料

### 详细指南

**`references/seo_checklist.md`**：
涵盖所有 SEO 方面的综合清单：
- 标题标签和元描述指南
- 标题结构最佳实践
- 图像优化技术
- URL 结构建议
- 内部链接策略
- 页面速度优化
- 移动优化要求
- 语义 HTML 使用
- 完整技术 SEO 清单

参考此清单获取任何 SEO 元素的详细规范。

**`references/schema_markup_guide.md`**：
实施 schema.org 结构化数据的完整指南：
- JSON-LD 实现（推荐格式）
- 10+ 常见模式类型示例
- Organization、LocalBusiness、Article、BlogPosting、FAQ、Product 等
- 每种类型的必要属性
- 最佳实践和常见错误
- 验证工具和资源

实施任何内容类型的模式标记时参考此指南。

### 脚本

**`scripts/seo_analyzer.py`**：
用于自动 SEO 分析的 Python 脚本。分析 HTML 文件以查找常见问题并生成详细报告。可输出文本或 JSON 格式。确定性和可靠的重复分析。

**`scripts/generate_sitemap.py`**：
用于生成 XML 站点地图的 Python 脚本。自动爬取目录，估计优先级和更改频率，并生成准备提交给搜索引擎的格式正确的站点地图。

### 资产

**`assets/robots.txt`**：
带有常见配置和注释的模板 robots.txt 文件。根据特定需求自定义，并放置在网站根目录。

## 关键原则

1. **用户优先**：首先为用户优化，其次为搜索引擎。良好的用户体验会带来更好的 SEO。

2. **独特内容**：每个页面应有唯一的标题、描述和 H1。重复内容会损害 SEO。

3. **移动优先**：Google 使用移动优先索引。始终包含视口元标签并确保移动响应性。

4. **可访问性 = SEO**：可访问的网站（alt 文本、语义 HTML、正确标题）排名更高。

5. **质量胜于数量**：实质性、有价值的内容比薄内容排名更高。目标是创建全面的页面。

6. **技术基础**：在高级优化之前修复关键技术问题（缺少标签、结构损坏）。

7. **结构化数据**：模式标记帮助搜索引擎理解内容，并可能导致丰富结果。

8. **定期更新**：SEO 是持续的。保持内容新鲜，监控分析，适应算法变化。

9. **自然语言**：使用自然语言为人类编写。避免关键词堆砌。

10. **验证**：始终使用测试工具在部署到生产环境前验证更改。

## 最大影响技巧

- **从关键问题开始**：首先修复缺少标题标签和元描述 - 这些影响最大
- **保持一致性**：在所有页面应用优化，而不仅仅是主页
- **使用语义 HTML**：使用正确的 HTML5 语义标签（`<header>`、`<nav>`、`<main>`、`<article>`、`<aside>`、`<footer>`）
- **优化图像**：压缩图像，使用描述性文件名，始终包含 alt 文本
- **内部链接**：使用描述性锚文本链接到相关页面
- **页面速度很重要**：加载速度快的页面排名更高
- **在移动设备上测试**：大多数搜索都是移动设备 - 确保出色的移动体验
- **监控 Search Console**：使用 Google Search Console 跟踪性能并识别问题
- **定期更新**：新鲜内容表明活跃、有价值的网站

## 快速参考命令

```bash
# 分析单个文件
python scripts/seo_analyzer.py index.html

# 分析整个网站
python scripts/seo_analyzer.py ./public

# 生成站点地图
python scripts/generate_sitemap.py ./public https://example.com

# 获取 JSON 分析输出
python scripts/seo_analyzer.py ./public --json
```
