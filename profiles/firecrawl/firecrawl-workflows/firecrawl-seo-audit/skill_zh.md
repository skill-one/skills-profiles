# Firecrawl SEO Audit

使用此工具将网站转换为特定、优先级的SEO审计。

## Onboarding Interview

从上下文中推断网站、目标关键词和输出格式。如果网站明确，请立即进行。

如果遇到阻碍，最多只问1-3个简洁的问题，例如网站URL、所需的目标关键词，或是否特定页面/竞争对手集很重要。

## Firecrawl Collection Plan

1. 使用Firecrawl映射网站，以了解URL结构。
2. 抓取关键页面：主页、产品/服务页面、定价、文档、博客、关于页面和高价值落地页。
3. 提取标题标签、元描述、标题、内部链接、内容结构、可见的规范信号和可用的图像替代文本。
4. 如果提供目标关键词，请搜索；抓取排名靠前的页面进行比较。

## Parallel Work

如果合适，使用子代理或等效的并行任务运行器：

- 网站结构：URL模式、站点地图健康状况、内部链接、孤儿/断链页面。
- 页面SEO：标题、元描述、H1/H2层次结构、内容质量。
- 关键词和SERP：目标关键词、排名页面、竞争对手页面模式。
- 技术问题：断链、重复内容信号、缺失元数据。

## Final Deliverable

```markdown
# SEO Audit: [网站]

## Executive Summary
[主要风险和机会]

## Site Structure
[发现的页面、URL质量、站点地图/内部链接备注]

## On-Page SEO
[每页的标题、元数据、标题、内容、链接备注]

## Keyword Opportunities
[目标关键词、缺失页面、内容差距]

## Competitor/SERP Comparison
[哪些网站排名高于本站以及原因]

## Prioritized Recommendations
[高/中/低影响修复建议及具体修改]

## Sources
[抓取的URL和检查内容]

## Rerun Inputs
workflow: firecrawl-seo-audit
site: [url]
keywords: [列表]
output: [markdown/json]
```

## Quality Bar

- 建议要具体，不要泛泛而谈。
- 每个问题都要展示页面或来源。
- 将技术发现与内容策略猜测区分开来。
