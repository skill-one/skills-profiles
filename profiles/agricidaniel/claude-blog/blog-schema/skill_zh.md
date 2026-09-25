# 博客模式：JSON-LD 结构化数据生成

使用 @graph 模式为博客文章生成完整、经过验证的 JSON-LD 模式标记。将多种模式类型组合到一个脚本标签中，并为实体链接提供稳定的 @id 引用。

## 工作流程

### 第 1 步：读取内容

读取博客文章并提取所有与模式相关的数据：
- **标题**（头条）
- **作者**（姓名、职位、社交链接、资质）
- **日期**（datePublished、dateModified / lastUpdated）
- **描述**（meta 描述）
- **常见问题解答（FAQ）部分**（问题和答案对）
- **图片**（封面图片 URL、尺寸、替代文本；内联图片）
- **组织信息**（网站名称、URL、标志）
- **字数**（从内容长度估算的大约字数）
- **标签/分类**（用于 BreadcrumbList 分类）
- **Slug**（从文件名或 frontmatter 获取）

### 第 2 步：生成 BlogPosting 模式

在适用情况下，使用推荐的属性完成 BlogPosting：

```json
{
  "@type": "BlogPosting",
  "@id": "{siteUrl}/blog/{slug}#article",
  "headline": "简洁的文章标题",
  "description": "简洁的页面特定 meta 描述",
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

Google 的 Article 结构化数据文档没有定义必需的 Article 属性。在适用情况下，包含 `headline`、`datePublished`、`author`、`publisher` 和 `image`，使用 Rich Results Test 进行验证，并将缺失的字段视为警告，除非目标表面需要它们。推荐属性：description、dateModified、mainEntityOfPage、wordCount、articleBody（摘要）。

### 第 3 步：生成 Person 模式

具有稳定 @id 以便跨引用的作者模式：

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
- `worksFor` - 雇主（如果与同一实体相同，则引用 Organization @id）

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

### 第 6 步：生成 FAQPage 实体模式（可选）

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
        "text": "完整的可见答案文本。"
      }
    }
  ]
}
```

Google 于 2026-05-07 停用所有网站的 FAQ 丰富结果。FAQPage 不是 Google 丰富结果或生成式 AI 优化路径，它不会获得 SEO 或 AI 准备度信用。只有在可见的 FAQ 真正帮助读者时才发出它，至少有一个有效的 `Question` 和匹配的可见答案。不要为了填充目标长度而填充答案，或者仅为了标记而添加 FAQ。

不要替代 QAPage。Google 支持QAPage用于一个用户可以提交答案的问题的页面。编辑式 FAQ、支持 FAQ 和博客问答部分不符合该模型。

### 第 7 步：生成 VideoObject（如果存在视频）

为帖子中嵌入的每个 YouTube 视频生成 VideoObject 模式：

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

将每个 VideoObject 添加到 @graph 数组中。使用 `#video-1`、`#video-2` 等。作为 @id 片段。从嵌入的 noscript 备用或从 YouTube Data API（如果通过 `blog-google` 可用）提取视频元数据。

### 第 7.5 步：生成 ImageObject

文章主要图片的封面图片模式：

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
- URL 必须可爬取且公开可访问
- 宽度和高度应反映实际图片尺寸
- 标题应与替代文本匹配或紧密对齐
- 推荐尺寸：1200x630（OG 兼容）或 1920x1080

### 第 8 步：验证和警告

在推荐模式类型之前检查每个表面的支持情况：

| 类型 | Google 搜索状态 | 有效实体/上下文使用 |
|------|----------------------|--------------------------|
| HowTo | 目前没有 Google 丰富结果体验 | 适用于真实的操作内容的有效 schema.org 类型 |
| Dataset | 由 Dataset Search 使用，不是 Google 搜索的通用丰富结果 | 仅适用于实际数据集 |
| QAPage | 支持一个用户提交答案的问题 | 不要用于编辑式 FAQ 内容 |
| Course | 课程列表仍然与已停用的 Course Info 体验区分开来 | 仅在当前 Course 列表文档和可见内容匹配时使用 |
| ClaimReview, SpecialAnnouncement, Course Info, Estimated Salary, Learning Video, Vehicle Listing | 曾是 Google 搜索体验；支持已停用 | 可能仍然是 schema.org 有效的，但永远不会为 Google 合格性推荐它们 |
| PracticeProblem | 已从 Google 搜索及其文档中移除 | 不要为 Google 合格性推荐 |
| Sitelinks Search Box | 没有专门的 Google 搜索视觉元素 | Google 按算法生成站点链接 |

**验证检查：**
1. 所有 @id 引用都解析为 @graph 中的实体
2. dateModified 等于或晚于 datePublished
3. headline 简洁。当它可能被截断或不清晰时发出警告
4. description 简洁、页面特定，并且不会在帖子之间重复
5. 所有 URL 都是绝对的（不是相对的）
6. 图片尺寸是正整数
7. BreadcrumbList 位置从 1 开始顺序
8. 如果发出 FAQPage，则存在可见的问答内容，并且至少包含一个有效的 `Question`

**生成式 AI 注意：** 结构化数据不是 Google 生成式 AI 搜索必需的，也没有特殊的 AI 模式。优先考虑准确、与可见内容一致的 Article/BlogPosting、Person、Organization 和 BreadcrumbList 实体。当资产存在时，添加 ImageObject 或 VideoObject。FAQPage 仍然是面向读者的可选标记，并且不会为 Google AI 带来优势。

### 第 9 步：输出

使用 @graph 模式将所有模式组合到一个 `<script>` 标签中：

安全要求：使用真实的 JSON 编码器构建 JSON-LD，永远不要使用字符串插值。在嵌入到 HTML 中之前，通过转义关闭脚本序列和字面量小于字符，例如将 `</` 替换为 `<\/`，将 `<` 替换为 `\u003c`。用户控制的字段（如 headline、description、作者姓名、图片 URL 和面包屑标签）必须作为 JSON 编码值进入块。

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
- 单个脚本标签而不是多个 - 更干净的 HTML
- 通过稳定的 @id 引用进行实体链接（例如，作者通过 @id 引用 Person）
- Google 和 AI 系统正确解析 @graph 数组
- 更容易作为一个单一块维护和更新

**输出选项：**
- **嵌入式 HTML** - 可以直接粘贴到 `<head>` 或 `</body>` 之前
- **独立 JSON** - 用于 CMS 模式字段或 API 注入
- **MDX 组件** - 如果项目使用 MDX，请将其包装在组件中

根据用户偏好将生成的模式保存到博客文章文件或单独的模式文件中。

Google 可以处理由 JavaScript 生成的 JSON-LD，当它存在于渲染的 DOM 中时。服务器渲染的标记对于非 Google 爬虫仍然更便携，但仅源 JSON-LD 不是 Google 的要求。对于动态标记，请验证渲染的 URL，确认值与可见内容匹配，并避免延迟或失败的客户端请求，这些请求会留下空的渲染 DOM。
