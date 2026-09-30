---
name: blog-schema
description: 生成包含 Article/BlogPosting、Person、Organization、BreadcrumbList、ImageObject 以及可选的 FAQPage 的完整 JSON-LD 结构化数据标记。符合 Google 要求，并会警告已弃用的类型。当用户输入“schema”、“blog schema”、“json-ld”、“structured data”、“schema markup”或“generate schema”时使用。
---

# 博客模式：JSON-LD 结构化数据生成

使用 @graph 模式为博客文章生成完整、经过验证的 JSON-LD 模式标记。将多种模式类型组合到一个 `<script>` 标签中，并为实体链接提供稳定的 @id 引用。

## 工作流程

### 第 1 步：读取内容

读取博客文章并提取所有与模式相关的数据：
- **标题**（头条）
- **作者**（姓名、职位、社交链接、资质）
- **日期**（datePublished、dateModified / lastUpdated）
- **描述**（元描述）
- **常见问题解答（FAQ）部分**（问题和答案对）
- **图片**（封面图片 URL、尺寸、替代文本；内联图片）
- **组织信息**（网站名称、URL、标志）
- **字数**（根据内容长度估算）
- **标签/分类**（用于 BreadcrumbList 分类）
- **Slug**（从文件名或 frontmatter 获取）

### 第 2 步：生成 BlogPosting 模式

在适用情况下，完成带有推荐属性的 BlogPosting：

```json
{
  "@type": "BlogPosting",
  "@id": "{siteUrl}/blog/{slug}#article",
  "headline": "简洁的文章标题",
  "description": "简洁的页面特定元描述",
  "datePublished": "YYYY-MM-DD",
  "dateModified": "YYYY-MM-DD",
  "author": { "@id": "{siteUrl}/author/{author-slug}#person" },
  "publisher": { "@id": "{siteUrl}#organization" },
  "image": { "@id": "{siteUrl}/blog/{slug}#primaryimage" },
  "mainEntityOfPage": {
    "@type": "WebPage",
    "@id": "{siteUrl}/blog/{slug}"
  },
  "wordCount": 2400,
  "articleBody": "内容的前 200 个字符作为摘要..."
}
```

Google 的 Article 结构化数据文档没有定义必需的 Article 属性。在适用情况下包含 `headline`、`datePublished`、`author`、`publisher` 和 `image`，使用 Rich Results Test 进行验证，并将缺失的字段视为警告，除非目标表面需要它们。推荐属性：description、dateModified、mainEntityOfPage、wordCount、articleBody（摘要）。

### 第 3 步：生成 Person 模式

带有稳定 @id 以便交叉引用的作者模式：

```json
{
  "@type": "Person",
  "@id": "{siteUrl}/author/{author-slug}#person",
  "name": "作者姓名",
  "jobTitle": "角色或职位",
  "url": "{siteUrl}/author/{author-slug}",
  "sameAs": [
    "https://twitter.com/handle",
    "https://linkedin.com/in/handle",
    "https://github.com/handle"
  ]
}
```

可选属性（在可用时包含）：
- `alumniOf` - 教育机构（Organization 类型）
- `worksFor` - 雇主（如果实体相同，则引用 Organization @id）

### 第 4 步：生成 Organization 模式

博客的父组织实体：

```json
{
  "@type": "Organization",
  "@id": "{siteUrl}#organization",
  "name": "组织名称",
  "url": "{siteUrl}",
  "logo": {
    "@type": "ImageObject",
    "url": "{siteUrl}/logo.png",
    "width": 600,
    "height": 60
  },
  "sameAs": [
    "https://twitter.com/org",
    "https://linkedin.com/company/org",
    "https://github.com/org"
  ]
}
```

标志要求：使用有效的可爬取的图片 URL，并遵循目标表面的活动 Organization 和 Article 文档。除非项目或当前文档要求，否则不要凭空编造硬标志尺寸。

### 第 5 步：生成 BreadcrumbList

显示内容层级的导航面包屑模式：

```json
{
  "@type": "BreadcrumbList",
  "@id": "{siteUrl}/blog/{slug}#breadcrumb",
  "itemListElement": [
    {
      "@type": "ListItem",
      "position": 1,
      "name": "首页",
      "item": "{siteUrl}"
    },
    {
      "@type": "ListItem",
      "position": 2,
      "name": "分类名称",
      "item": "{siteUrl}/blog/category/{category-slug}"
    },
    {
      "@type": "ListItem",
      "position": 3,
      "name": "文章标题",
      "item": "{siteUrl}/blog/{slug}"
    }
  ]
}
```

如果没有分类可用，请将第二个面包屑项使用 "Blog"，并将 `{siteUrl}/blog` 作为 URL。

### 第 6 步：生成 FAQPage 实体模式

从博客文章的 FAQ 部分提取问答对：

```json
{
  "@type": "FAQPage",
  "@id": "{siteUrl}/blog/{slug}#faq",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "问题是什么？",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "完整的答案文本（40-60 个字，包含统计数据）。"
      }
    }
  ]
}
```

重要说明：Google 于 2026-05-07 停用所有网站的 FAQ 丰富结果。FAQPage 不是 Google 丰富结果路径。仅在存在可见的 FAQ 内容时才发出 FAQPage，并且至少包含一个有效的 `Question` 和匹配的可见答案。将其视为实体清晰度标记，而不是 Google 丰富结果承诺。Article/BlogPosting 模式仍然是博客搜索资格的优先级。

### 第 7 步：生成 VideoObject（如果存在视频）

对于帖子中嵌入的每个 YouTube 视频，生成一个 VideoObject 模式：

```json
{
  "@type": "VideoObject",
  "@id": "{siteUrl}/blog/{slug}#video-{index}",
  "name": "视频标题",
  "description": "视频描述摘要（前 200 个字符）",
  "thumbnailUrl": "https://img.youtube.com/vi/{videoId}/hqdefault.jpg",
  "uploadDate": "{ISO 8601 日期}",
  "contentUrl": "https://www.youtube.com/watch?v={videoId}",
  "embedUrl": "https://www.youtube.com/embed/{videoId}",
  "duration": "PT{M}M{S}S",
  "interactionStatistic": {
    "@type": "InteractionCounter",
    "interactionType": { "@type": "WatchAction" },
    "userInteractionCount": {viewCount}
  }
}
```

将每个 VideoObject 添加到 @graph 数组中。使用 `#video-1`、`#video-2` 等 @id 片段。从嵌入的 noscript 回退或通过 `blog-google` 从 YouTube Data API（如果可用）提取视频元数据。

### 第 7.5 步：生成 ImageObject

帖子的主要图片的封面图片模式：

```json
{
  "@type": "ImageObject",
  "@id": "{siteUrl}/blog/{slug}#primaryimage",
  "url": "https://cdn.pixabay.com/photo/.../image.jpg",
  "width": 1200,
  "height": 630,
  "caption": "与替代文本匹配的描述性标题"
}
```

图片要求：
- URL 必须可爬取且公开访问
- 宽度和高度应反映实际图片尺寸
- 标题应与图片替代文本匹配或紧密对齐
- 推荐尺寸：1200x630（OG 兼容）或 1920x1080

### 第 8 步：验证并警告

在推荐模式类型之前检查每个表面的支持情况：

| 类型 | Google 丰富结果状态 | 有效实体/上下文使用 |
|------|---------------------|---------------------|
| HowTo | 不是当前的 Google 丰富结果策略 | 当页面确实包含 how-to 内容时，是有效的 schema.org 类型 |
| Dataset | 不适用于通用博客丰富结果 | 适用于数据集页面和 Dataset Search 资格 |
| QAPage | 与 FAQPage 不同 | 当页面包含一个用户提交答案的问题时，是有效的 |
| SpecialAnnouncement、PracticeProblem、Sitelinks Search Box | 不推荐用于一般博客文章 | 仅在当前官方文档和页面内容匹配时使用 |

**验证检查：**
1. 所有 @id 引用都解析为 @graph 中的实体
2. dateModified 等于或晚于 datePublished
3. headline 简洁。当可能被截断或变得不清晰时发出警告
4. description 简洁、页面特定，并且在帖子之间不重复
5. 所有 URL 都是绝对的（不是相对的）
6. 图片尺寸是正整数
7. BreadcrumbList 位置从 1 开始顺序
8. 如果发出 FAQPage，则存在可见的 Q&A 内容，并且至少包含 1 个有效的 `Question`

**AI 引用优化说明：** 相关模式有助于实体清晰度和在支持的情况下丰富结果资格，但结构化数据不是 Google 生成式 AI 搜索可见性的必需项。优先考虑 Article/BlogPosting、Person、Organization 和 BreadcrumbList。当存在资产时添加 ImageObject 或 VideoObject，并且仅在存在可见的 FAQ 内容时添加 FAQPage。

### 第 9 步：输出

使用 @graph 模式将所有模式组合到一个 `<script>` 标签中：

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@graph": [
    { "@type": "BlogPosting", ... },
    { "@type": "Person", ... },
    { "@type": "Organization", ... },
    { "@type": "BreadcrumbList", ... },
    { "@type": "FAQPage", ... },
    { "@type": "VideoObject", ... },
    { "@type": "ImageObject", ... }
  ]
}
</script>
```

**@graph 模式的好处：**
- 单个 `<script>` 标签而不是多个 - 更干净的 HTML
- 通过稳定的 @id 引用进行实体链接（例如，作者通过 @id 引用 Person）
- Google 和 AI 系统正确解析 @graph 数组
- 更容易作为一个块进行维护和更新

**输出选项：**
- **嵌入式 HTML** - 准备粘贴到 `<head>` 或 `</body>` 之前
- **独立 JSON** - 用于 CMS 模式字段或 API 注入
- **MDX 组件** - 如果项目使用 MDX，将其包装在组件中

根据用户偏好将生成的模式保存到博客文章文件或单独的模式文件中。
