# 站内SEO：模式 / 结构化数据

指导 Schema.org 结构化数据（JSON-LD）的实现，用于丰富摘要、增强搜索结果和生成式引擎优化（GEO）。

**调用时**：在**首次使用**时，如果有助于理解，先用1-2句话说明此技能涵盖的内容及其重要性，然后提供主要输出。在**后续使用**或用户要求跳过时，直接进入主要输出。

## 范围（站内SEO）

- **模式标记**：Schema.org类型用于丰富结果、AI搜索可见性和机器可读内容
- **Schema.org与搜索引擎**：Schema.org定义了800多种类型；每个搜索引擎仅支持其中一小部分用于丰富结果

## Schema.org与搜索引擎支持

**Schema.org与Google结构化数据并非完全一致**。Schema.org是一个开放词汇表（800多种类型）；Google、Bing和其他引擎各自仅支持其中一小部分精选类型用于丰富结果。

| 引擎 | 支持 | 备注 |
|------|------|------|
| **Google** | 仅支持子集 | 仅Google搜索画廊中的类型会生成丰富结果。不在Google列表中的有效Schema.org标记不会产生增强摘要——即使从技术上讲是正确的。 |
| **Bing** | 子集；不同 | 支持JSON-LD、Microdata、RDFa、Open Graph。某些类型（例如Product、Offer）具有特定格式的支持。查看[Bing Webmaster文档](https://www.bing.com/webmasters/help/marking-up-your-site-with-structured-data-3a93e731)。 |
| **其他引擎** | 各不相同 | Yandex、DuckDuckGo、AI搜索工具（Perplexity等）即使不显示丰富结果，也可能使用Schema.org来理解内容。 |

**实际影响**：为您的内容类型实现Schema.org标记。如果Google不显示该类型的丰富结果，Bing或AI系统可能仍然会使用它。始终参考[Google开发者文档](https://developers.google.com/search/docs)以确定Google特定的丰富结果资格。

## 丰富结果：Google支持（2026年）

**高影响类型**：Product、Review摘要、Article/News、Video、Recipe、LocalBusiness、Event、Breadcrumb、Sitelinks searchbox、JobPosting。

**有限或依赖上下文**：FAQ（政府/健康网站用于许多查询）、Education Q&A、Course、SoftwareApplication、Speakable（新闻）、DiscussionForumPosting。

**已弃用**：HowTo（自2023年9月起对所有设备完全移除）、COVID数据面板、某些仅限AMP的格式、data-vocabulary.org。

**实现**：首选JSON-LD；包含`@context`、`@type`、稳定的`@id`；ISO 8601日期；将结构化数据与可见内容匹配。使用[丰富结果测试](https://search.google.com/test/rich-results)进行验证。丰富结果可提高CTR高达~35%，并改善AI引用。

## 模式 ↔ 搜索引擎结果页面（SERP）功能 ↔ 丰富结果（强相关）

**模式、SERP功能和丰富结果是强相关的**。模式是大多数丰富结果的**必要条件**。在针对SERP功能时，实现相应的模式类型。查看**serp-features**以获取完整的SERP功能列表和优化。

### 丰富结果与精选摘要

- **丰富结果**：由模式驱动的标准列表增强（星级、面包屑导航、FAQ下拉菜单、产品信息）。出现在有机位置；不需要前10名排名。
- **精选摘要**：Google提取的位置零处的答案框。不需要模式；内容结构很重要。模式（FAQPage、HowTo、Article）可以支持提取。

| 模式类型 | SERP功能 / 丰富结果 | 备注 |
|----------|----------------------|------|
| **FAQPage** | PAA、精选摘要 | FAQ下拉菜单；问答式摘要。对许多网站（例如政府/健康）的资格有限制 |
| **BreadcrumbList** | 面包屑导航 | 结果中的路径显示 |
| **AggregateRating、Review** | 评论 / 星级 | 星级评分 |
| **HowTo** | 曾是丰富结果（2023年9月弃用） | 不再生成Google丰富结果；Bing/AI可能仍然使用 |
| **Article** | 深入文章、摘要 | 文章丰富结果 |
| **VideoObject** | 视频 | 视频缩略图；参见**video-optimization** |
| **Product、Offer** | 购物、产品 | 产品/购物结果 |
| **Recipe** | 食谱 | 食谱丰富结果 |
| **JobPosting** | Google Jobs | 职位列表 |
| **Event** | 活动 | 活动丰富结果 |
| **WebSite + SearchAction** | Sitelinks searchbox | 品牌查询的站点链接 |
| **Organization、Person** | 知识面板 | 实体信息；参见**entity-seo** |

**工作流程**：1) 使用**serp-features**确定目标SERP功能；2) 在此表中查找模式类型；3) 实施并使用丰富结果测试进行验证。

## 生成式引擎优化（GEO）

**GEO** = 优化内容，使AI系统（Google AI Overviews、Perplexity、ChatGPT、Gemini）在生成答案时选择、引用并引用您的内容。结构化数据使内容机器可读；AI引擎更准确地提取和引用。GEO的关键模式类型：Organization、Person/Author、WebSite、WebPage、FAQPage、HowTo、Article、Product、AggregateRating。参见**generative-engine-optimization**以获取完整的GEO策略。

## 初始评估

**首先检查项目上下文**：如果存在`.claude/project-context.md`或`.cursor/project-context.md`，请阅读它以了解产品类型和内容。

识别：
1. **页面类型**：文章、产品、FAQ、组织、JobPosting、Event等
2. **内容**：要描述的实体
3. **目标**：丰富摘要、AI概述可见性、知识面板

## 模式类型分类

### 核心类型（通用使用）

| 类型 | 用例 |
|------|------|
| **Organization** | 全站；公司信息、logo、sameAs；参见下方位置说明 |
| **WebSite** | 全站；搜索动作、站点名称；在主页上与Organization配对 |
| **Article** | 博客文章、新闻、工具介绍 |
| **BreadcrumbList** | 面包屑导航 |
| **FAQPage** | FAQ部分；触发PAA式结果 |
| **Person** | 作者信息；与Article配对 |
| **ImageObject** | 用于丰富结果的图像元数据 |
| **HowTo** | 教程、分步指南。**注意**：Google对所有设备上的HowTo丰富结果已完全弃用（2023年9月）；Bing/AI可能仍然消费HowTo模式 |

### 专用类型（特定场景）

| 类型 | 用例 |
|------|------|
| **JobPosting** | 招聘网站、AI职位匹配 |
| **Product** | 电子商务产品页面 |
| **Event** | 活动页面、票务（非一般博客） |
| **SoftwareApplication** | 应用页面、工具页面 |
| **LocalBusiness** | 本地企业页面 |
| **Dataset** | 数据平台、数据集 |
| **DiscussionForumPosting** | 论坛、社区帖子 |
| **Quiz** | 教育、闪卡 |
| **MathSolver** | 数学工具 |
| **CaseStudy** | 案例研究页面 |
| **Recipe** | 食谱、餐计划、烹饪说明 |

**规则**：对于大多数网站，使用核心类型。仅在页面内容匹配时才使用专用类型（例如，不要在博客上使用Event；不要在产品页面上使用JobPosting）。

### Organization & WebSite模式位置

| 位置 | Organization | WebSite | 备注 |
|------|--------------|---------|------|
| **主页** | 最小 | 最小 | 至少在主页上添加Organization和WebSite。Organization描述拥有网站的实体；WebSite启用Sitelinks searchbox和站点标识。 |
| **根布局 / 全局** | 最佳 | 最佳 | 放置在站点全局布局中（例如`layout.tsx`、`_document`、全局头部/尾部），以便在每页上显示模式。Google使用找到的第一个实例；每个网站一个实例就足够了。 |
| **关于页面** | 无 | 无 | 关于页面使用**AboutPage**模式（页面特定：标题、描述、作者、关于）。Organization是实体级别的，不是页面级别的——不要将其限制在关于页面。参见**about-page-generator**。 |

**实现**：在`<head>`中插入JSON-LD；使用`@id`（例如`https://example.com/#organization`）将Organization ↔ WebSite ↔ WebPage链接起来以形成实体图。参见**entity-seo**以获取@id和知识面板。

## 行动：网站/产品类型 → 模式映射

**使用此表来推荐适合网站的专用模式类型**。将网站内容和产品类型与最相关的模式进行匹配。如有疑问，请从核心类型（Organization、WebSite、Article）开始；仅在内容明显匹配时才添加专用类型。

| 网站 / 产品类型 | 推荐的专用模式 | 原因 |
|------------------|-----------------|------|
| **AI餐计划、食谱网站、食品博客、烹饪应用** | **Recipe** | 食材、说明、烹饪时间、份量——与食品/餐内容高度相关。Google支持Recipe丰富结果。 |
| **招聘网站、招聘网站、职业页面** | **JobPosting** | 职位名称、公司、地点、薪资、雇佣类型。对Google Jobs是必需的。 |
| **活动平台、票务、网络研讨会、会议** | **Event** | 日期、地点、价格。仅在真实活动页面上使用。 |
| **SaaS、应用、Chrome扩展、工具、软件产品页面** | **SoftwareApplication** | 应用名称、类别、评分、价格、操作系统。适用于产品/功能页面。 |
| **电子商务产品页面** | **Product** | 价格、库存、品牌、评论。与Offer、AggregateRating一起使用。 |
| **论坛、社区、Reddit风格、问答** | **DiscussionForumPosting** | 帖子内容、作者、评论。用于用户生成讨论。 |
| **数据平台、数据集存储库、Scale AI / Surge AI** | **Dataset** | 数据集名称、创建者、许可、分发格式。用于数据目录页面。 |
| **教育网站、闪卡、Quizlet风格** | **Quiz** | 问题-答案对。用于教育问答内容。 |
| **数学求解器、计算器、方程工具** | **MathSolver** | 数学问题输入、解决方案输出。用于数学工具。 |
| **案例研究、客户故事页面** | **CaseStudy** | 客户、结果、方法。用于B2B案例研究。 |
| **FAQ页面、产品FAQ、支持FAQ** | **FAQPage** | 问题+接受答案对。触发PAA式结果。 |
| **教程、如何指南、分步指南** | **HowTo** | 步骤、工具、时间。**注意**：Google对所有设备上的HowTo丰富结果已完全弃用（2023年9月）；Bing/AI可能仍然消费该模式。考虑使用FAQPage作为替代方案 |
| **新闻文章、新闻稿** | **NewsArticle** | 使用Article代替用于新闻。 |
| **视频页面、播客节目** | **VideoObject** / **PodcastEpisode** | 用于视频/音频内容。参见**video-optimization**以获取VideoObject、缩略图、关键时刻。 |

**示例**：
- **AI餐计划**（例如，生成每周餐计划并包含食谱）→ 在每个食谱/餐页面添加**Recipe**模式；在着陆页上使用**Article**或**WebPage**
- **AI写作工具** → 产品页面上使用**SoftwareApplication**；博客上使用**Article**
- **招聘SaaS** → 在职位列表页面上使用**JobPosting**；在产品页面上使用**SoftwareApplication**
- **食谱博客** → 每个食谱帖子使用**Recipe**；非食谱帖子使用**Article**

**输出**：在推荐模式时，说明：(1) 哪些专用类型适合网站/产品，(2) 哪些页面类型使用哪种模式，(3) 全站添加的核心类型（Organization、WebSite、BreadcrumbList）。

### Article / BlogPosting / NewsArticle：类型选择与实现

选择与内容**最具体**的类型：

| 类型 | 用例 |
|------|------|
| **BlogPosting** | 非正式博客文章；单个作者；定期更新 |
| **Article** | 正式、常青内容；工具介绍；百科全书式 |
| **NewsArticle** | 时间敏感的新闻；知名出版商 |

**必需属性**：headline（最多110个字符）、image（最小1200px宽；绝对URL）、datePublished（ISO 8601）、author（Person或Organization）、publisher（Organization带logo）。

**推荐**：dateModified、description、mainEntityOfPage（规范URL）。

**日期显示用于CTR**：Google建议在页面上只显示**一个日期**。如果同时显示datePublished和dateModified，Google可能会为SERP选择错误的日期——Search Engine Land看到CTR下降了~22%。最佳实践：如果存在dateModified，则显示dateModified；否则显示datePublished。在JSON-LD中保留两者；规则适用于**可见**的日期。

**JSON-LD示例**（BlogPosting）：

```json
{
  "@context": "https://schema.org",
  "@type": "BlogPosting",
  "headline": "2025年SEO终极检查清单",
  "description": "一份完整的指南，用于优化博客文章以供搜索和AI使用。",
  "image": "https://example.com/image.jpg",
  "datePublished": "2025-01-15T09:00:00Z",
  "dateModified": "2025-02-01T14:30:00Z",
  "author": { "@type": "Person", "name": "Jane Doe", "url": "https://example.com/author/jane" },
  "publisher": { "@type": "Organization", "name": "Example", "logo": { "@type": "ImageObject", "url": "https://example.com/logo.png" } }
}
```

通过`<head>`中的`<script type="application/ld+json">`插入。对于文章页面，使用`og:type: article`与og:article:published_time、og:article:modified_time、og:article:author。参见**article-page-generator**、**open-graph**。

### BreadcrumbList

用于面包屑导航。模式必须与可见的面包屑完全匹配。参见**breadcrumb-generator**以获取UI、位置和语义HTML。

| 要求 | 指南 |
|------|------|
| **格式** | `<script type="application/ld+json">`中的JSON-LD |
| **URLs** | 每个项目使用绝对URL（https://） |
| **位置** | 从1开始的顺序整数 |
| **匹配** | 模式必须与可见的面包屑完全匹配 |

**JSON-LD示例**：

```json
{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    { "@type": "ListItem", "position": 1, "name": "Home", "item": "https://example.com/" },
    { "@type": "ListItem", "position": 2, "name": "Category", "item": "https://example.com/category/" },
    { "@type": "ListItem", "position": 3, "name": "当前页面", "item": "https://example.com/category/current-page/" }
  ]
}
```

**多个路径**：当页面可通过多个路径访问时（例如，在多个类别中的产品），Google支持同一页面上有多个BreadcrumbList对象。使用BreadcrumbList对象的数组。

## 最佳实践

| 原则 | 指南 |
|------|------|
| **准确性** | 数据必须与可见的页面内容匹配；永远不要添加不可见或误导性的数据 |
| **完整性** | 按每种类型包含所有必需属性 |
| **最具体类型** | 当适用时使用NewsArticle而不是Article |
| **JSON-LD** | 首选格式；放置在`<script type="application/ld+json">` |
| **@id for entities** | 使用@id为Organization、Person启用实体链接；参见**entity-seo** |
| **分阶段实施** | 首先添加必需属性；然后添加可选属性以进行优化 |
| **验证** | 使用丰富结果测试和Schema Markup Validator进行测试 |
| **inLanguage（多语言）** | 添加`"inLanguage": "en-US"`（IETF BCP 47）以匹配hreflang；为每个区域本地化名称、描述、FAQ以改善该语言的丰富摘要CTR |

### 多语言模式（inLanguage）

对于多语言网站，在JSON-LD中添加`inLanguage`以强化语言目标。与hreflang值保持一致（例如`"inLanguage": "zh-CN"`与`hreflang="zh-CN"`）。

**本地化模式数据**：为每个区域翻译结构化数据字段（名称、描述、FAQ acceptedAnswer等），以改善该语言的丰富摘要CTR。

**支持inLanguage的类型**：Article、BlogPosting、WebApplication、FAQPage、HowTo、Product、Organization。

## 实现工作流程

1. **分析**页面类型和内容；选择匹配的模式类型
2. **选择格式**——首选JSON-LD（Google、Bing、AI工具支持）
3. **编写**结构化数据；从必需属性开始
4. **验证**使用[丰富结果测试](https://search.google.com/test/rich-results)、[模式标记验证器](https://validator.schema.org/)
5. **部署和监控**通过Search Console增强报告

## 常见错误和修复

| 错误 | 修复 |
|------|------|
| **数据与可见内容不匹配** | 模式必须仅描述用户看到的内容 |
| **缺少必需属性** | 查看Google/Schema.org文档以获取每种类型的必需属性 |
| **页面类型错误** | 不要在非活动页面上使用Event；不要在产品页面上使用JobPosting |
| **格式/语法错误** | 验证JSON-LD；检查引号、括号、逗号 |
| **过度标记** | 仅标记相关内容；避免填充不相关的类型 |

## 实现细节

### Next.js（元数据）

```tsx
export const metadata = {
  other: {
    'script:ld+json': JSON.stringify({
      "@context": "https://schema.org",
      "@type": "Article",
      "headline": "...",
      "description": "...",
      "inLanguage": "en-US",
      "image": "https://example.com/image.jpg",
      "datePublished": "2024-01-01T00:00:00Z",
      "dateModified": "2024-01-15T00:00:00Z",
      "author": { "@type": "Person", "name": "..." },
      "publisher": { "@type": "Organization", "name": "...", "logo": { "@type": "ImageObject", "url": "..." } }
    }),
  },
};
```

### HTML（通用）

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "...",
  "description": "...",
  "inLanguage": "en-US",
  "author": { "@type": "Person", "name": "..." },
  "publisher": { "@type": "Organization", "name": "...", "logo": { "@type": "ImageObject", "url": "..." } }
}
</script>
```

## 验证工具

| 工具 | 目的 |
|------|------|
| [Google丰富结果测试](https://search.google.com/test/rich-results) | 检查Google是否可以生成丰富结果 |
| [模式标记验证器](https://validator.schema.org/) | 与Schema.org规范进行验证 |
| Search Console | 增强报告；监控随时间变化的有效性 |

## 输出格式

- **行动优先**：使用网站/产品类型→模式映射表来推荐适合网站的专用模式（例如，AI餐计划→Recipe；SaaS工具→SoftwareApplication）
- **模式类型推荐**（核心与专用）
- **页面级映射**：哪些页面使用哪种模式
- **JSON-LD**结构，包含必需属性
- **验证**步骤
- **参考**：[Schema.org](https://schema.org/)、[Google结构化数据](https://developers.google.com/search/docs/appearance/structured-data/intro-structured-data)、[Bing标记](https://www.bing.com/webmasters/help/marking-up-your-site-with-structured-data-3a93e731)

## 相关技能

- **article-page-generator**：文章结构；Article/BlogPosting/NewsArticle模式；日期显示
- **serp-features**：**强相关**——模式映射到SERP功能；参见上表映射
- **faq-page-generator**：FAQPage模式；FAQ内容结构
- **howto-section-generator**：HowTo部分组件（步骤、JSON-LD）；HowTo与FAQPage
- **breadcrumb-generator**：BreadcrumbList模式实现
- **featured-snippet**：FAQPage、HowTo用于摘要
- **video-optimization**：VideoObject、视频站点地图、缩略图、关键时刻
- **entity-seo**：Organization、Person用于实体识别；@id；知识面板
- **homepage-generator**：主页或根布局上的Organization + WebSite模式
- **indexing**：Google索引API用于JobPosting、BroadcastEvent
