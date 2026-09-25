# Schema Markup 分析与生成

## 检测

1. 使用 `"${CLAUDE_PLUGIN_ROOT}/scripts/claude-seo" run parse_html.py --url <url> --json` 提取 JSON-LD（或扫描页面源代码中的 `<script type="application/ld+json">`）。标记任何缺少 `@context` 或 `@type` 的块：Google 无法将其关联到实体（此类块中的评分无法到达产品）。
2. 检查 Microdata (`itemscope`, `itemprop`)
3. 检查 RDFa (`typeof`, `property`)
4. 始终推荐 JSON-LD 作为主要格式（Google 的明确偏好）

## 验证

- 检查每种模式类型所需的属性
- 验证 Google 支持的丰富结果类型
- 测试常见错误：
  - 缺少 @context
  - 无效的 @type
  - 错误的数据类型
  - 占位符文本
  - 相对 URL（应为绝对 URL）
  - 无效的日期格式
- 标记已弃用的类型（见下文）

## 模式类型状态（截至 2026 年 6 月）

阅读 `../seo/references/schema-types.md` 获取完整列表。关键规则：

### 活跃（可自由推荐）：
Organization（组织）、LocalBusiness（本地业务）、SoftwareApplication（软件应用）、WebApplication（网络应用）、Product（产品，截至 2025 年 4 月包含认证标记）、ProductGroup（产品组）、Offer（报价）、Service（服务）、Article（文章）、BlogPosting（博客发布）、NewsArticle（新闻文章）、Review（评论）、AggregateRating（综合评分）、BreadcrumbList（面包屑列表）、WebSite（网站）、WebPage（网页）、Person（个人）、ProfilePage（个人资料页）、ContactPage（联系页）、VideoObject（视频对象）、ImageObject（图像对象）、Event（活动）、JobPosting（职位发布）、Course（课程）、DiscussionForumPosting（讨论论坛发布）

### 视频 & 特殊（可自由推荐）：
BroadcastEvent（广播事件）、Clip（片段）、SeekToAction（跳转操作）、SoftwareSourceCode（软件源代码）

参考 `schema/templates.json` 获取这些类型的现成 JSON-LD 模板。

> **JSON-LD 和 JavaScript 渲染**：根据 Google 2025 年 12 月的 JS SEO 指导，通过 JavaScript 注入的结构化数据可能面临延迟处理。对于时效性标记（尤其是 Product、Offer），请在初始服务器渲染的 HTML 中包含 JSON-LD。

### 无丰富结果，如需使用则保留：
- **FAQPage**：Google 于 2026 年 5 月 7 日对所有网站停用 FAQ 丰富结果（取代 2023 年 8 月的 gov/health 限制）。无 Google SERP 丰富结果优势；将现有 FAQPage 标记为 Info（非 Critical）而非删除。对于真实的用户问答页面，使用 **QAPage**。

### 已弃用（切勿推荐）：
- **HowTo**：丰富结果于 2023 年 9 月移除
- **SpecialAnnouncement**：2025 年 7 月 31 日弃用
- **CourseInfo、EstimatedSalary、LearningVideo**：2025 年 6 月停用
- **ClaimReview**：自 2025 年 6 月起无搜索丰富结果。Google 的事实核查探索器仍使用该标记，因此事实核查发布者可以保留；切勿推荐用于 SERP 功能
- **VehicleListing**：2025 年 6 月从丰富结果中移除
- **Practice Problem**：弃用通知 2025-11-05；工具支持从 2026 年 1 月开始移除；文档于 2026-01-06 移除
- Search Console / Rich Results Test / appearance-filter 支持于 2025-09-09 移除（Search Console API 通过 2025 年 12 月）。

### 仍受支持（尽管有早期弃用通知）：
- **Book Actions**：未弃用。2025 年 6 月弃用横幅于 2025-11-05 移除，因为搜索功能仍使用该标记。

### 仅用于数据集搜索：
- **Dataset**：未停止；被 Google Dataset Search 消费，无 Google 搜索丰富结果界面。不要建议删除，好像它被终止了。

### 仍受支持（无需标记）：
- QAPage（2026-03-24 扩展评论线程属性）、DiscussionForumPosting、Education Q&A（Quiz / `eduQuestionType=Flashcard`）。对于电子商务，**hasAdultConsideration**（添加 2026-05-20；值 `https://schema.org/SexualContentConsideration`）对成人产品是必需的。`Product.category` 接受 `Text`、`CategoryCode` 或混合两者的数组。

## 生成

为页面生成模式时：
1. 通过内容分析识别页面类型
2. 选择适当的模式类型
3. 生成包含所有必需和推荐属性的合法 JSON-LD
4. 仅包含真实、可验证的数据。使用清晰标记供用户填写的占位符
5. 在展示前验证输出
6. 对于评论标记，拒绝虚假评论和未披露的激励性评论。激励必须清晰且突出地披露在页面上。

## 常见模式模板

### Organization（组织）
```json
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "[公司名称]",
  "url": "[网站 URL]",
  "logo": "[Logo URL]",
  "contactPoint": {
    "@type": "ContactPoint",
    "telephone": "[电话]",
    "contactType": "customer service"
  },
  "sameAs": [
    "[Facebook URL]",
    "[LinkedIn URL]",
    "[Twitter URL]"
  ]
}
```

### LocalBusiness（本地业务）
```json
{
  "@context": "https://schema.org",
  "@type": "LocalBusiness",
  "name": "[业务名称]",
  "address": {
    "@type": "PostalAddress",
    "streetAddress": "[街道]",
    "addressLocality": "[城市]",
    "addressRegion": "[州]",
    "postalCode": "[邮编]",
    "addressCountry": "US"
  },
  "telephone": "[电话]",
  "openingHours": "Mo-Fr 09:00-17:00",
  "geo": {
    "@type": "GeoCoordinates",
    "latitude": "[纬度]",
    "longitude": "[经度]"
  }
}
```

### Article/BlogPosting（文章/博客发布）
```json
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "[标题]",
  "author": {
    "@type": "Person",
    "name": "[作者名称]"
  },
  "datePublished": "[YYYY-MM-DD]",
  "dateModified": "[YYYY-MM-DD]",
  "image": "[图像 URL]",
  "publisher": {
    "@type": "Organization",
    "name": "[发布者]",
    "logo": {
      "@type": "ImageObject",
      "url": "[Logo URL]"
    }
  }
}
```

## 输出

- `SCHEMA-REPORT.md`：检测和验证结果
- `generated-schema.json`：现成可用的 JSON-LD 片段

### 验证结果
| 模式 | 类型 | 状态 | 问题 |
|------|------|------|------|
| ... | ... | ✅/⚠️/❌ | ... |

### 建议
- 缺少模式机会
- 需要验证的修复
- 实现生成的代码

## 错误处理

| 场景 | 操作 |
|------|------|
| URL 不可达 | 报告连接错误及状态码。建议验证 URL 并检查页面是否需要认证。 |
| 未发现模式标记 | 报告未检测到 JSON-LD、Microdata 或 RDFa。根据页面内容分析推荐适当的模式类型。 |
| 无效的 JSON-LD 语法 | 解析并报告具体的语法错误（缺少括号、尾随逗号、未加引号的键）。提供修正后的 JSON-LD 输出。 |
| 检测到已弃用的模式类型 | 标记已弃用类型及其停用日期。推荐当前替代类型或建议删除（如果无替代类型）。 |
