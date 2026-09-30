---
name: nextjs-seo
description: Next.js 应用路由器 SEO 优化和审核。在 Next.js 应用中实现或修复 SEO 时使用——元数据与 generateMetadata、视口/主题色、Open Graph 和 og/twitter 图片（文件规范 + ImageResponse）、网页应用清单、图标/favicons、sitemap.xml、robots.txt、规范 URL、hreflang/i18n 替代、JSON-LD 结构化数据与丰富结果、核心网页性能（LCP/INP/CLS）、AI 搜索/GEO 和 AI 爬虫规则（GPTBot、OAI-SearchBot），或诊断 Google 索引问题（搜索控制台，“已发现/爬取 - 目前未索引”）。也用于运行 SEO 审核清单。不适用于与 SEO 无关的通用 Next.js 功能工作。
---

# Next.js SEO 优化

## 从证据和实用内容开始

在修改框架代码之前，先阅读已安装的 Next.js 版本以及相关的 `node_modules/next/dist/docs/` 指南；当本地文档不可用时，使用当前的官方文档。当可用时，使用 Vercel MCP 文档搜索平台行为，但请检查检索到的示例与已安装的框架是否一致。不要从搜索片段中复制遗留缓存 API 到更新的应用程序中。

- 首先解决读者的任务。一个简短有用的页面不需要填充内容。给 H1、副标题和章节标题分配不同的任务；不要在每个标题中重复相同的短语以进行 SEO。保持 UI 复制简洁、具体和有用。
- 不要为了使页面看起来经过优化而添加通用的介绍、关键词块、装饰性徽章、常见问题解答或 TL;DR。只有当它回答一个真实的问题时才添加内容。保留必要的解释和披露。
- 只有当每个页面都提供独特、可维护的价值时，才创建团队、位置或分类页面。一个交换的名称/标志和重复的列表是不够的。
- 描述季节、可用性和更新时间，使用当前数据。不要在活跃服务上留下预发布副本，也不要更改时间戳以保持新鲜度。
- 分离证据：一个 Search Console 性能导出显示查询和流量，而不是索引状态、Google 的规范选择或 CWV。使用相关的报告或 URL 检查；将不可用的检查标记为未验证。
- 在预测影响之前报告发现和验证。没有排名、索引、丰富结果或 AI 引用的保证。

## 快速 SEO 审计

为任何 Next.js 项目运行此清单：

1. **检查 robots.txt**: `curl https://your-site.com/robots.txt`
2. **检查 sitemap**: `curl https://your-site.com/sitemap.xml`
3. **检查元数据**: 查看页面源代码，搜索 `<title>` 和 `<meta name="description">`
4. **检查 JSON-LD**: 查看页面源代码，搜索 `application/ld+json`
5. **检查核心网络指标**: 使用 PageSpeed Insights (pagespeed.web.dev) 和 Search Console CWV 报告获取字段数据 — Lighthouse 仅是实验室诊断，无法测量 INP

## 必要文件

### app/layout.tsx - 根元数据

```typescript
import type { Metadata, Viewport } from 'next';

// Viewport 必须是单独导出的。`themeColor`、`colorScheme` 和
// `viewport` 在 `metadata` 中被丢弃：Next.js 16 没有发出标签，只发出
// "不支持的元数据" 构建警告。
export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
  maximumScale: 5,
  userScalable: true,
  themeColor: [
    { media: '(prefers-color-scheme: light)', color: '#ffffff' },
    { media: '(prefers-color-scheme: dark)', color: '#0a0a0a' },
  ],
};

export const metadata: Metadata = {
  metadataBase: new URL('https://your-site.com'),
  title: {
    default: '网站标题 - 主要关键词',
    template: '%s | 网站名称',
  },
  // ~150-160 个字符是一个指南，不是一个限制 — Google 会根据设备/查询进行截断
  description: '引人入胜的描述，包含目标关键词',
  // 没有 `keywords` 字段：Google 完全忽略关键词元标签
  openGraph: {
    type: 'website',
    locale: 'en_US',
    url: 'https://your-site.com',
    siteName: '网站名称',
    title: '网站标题',
    description: '用于社交分享的描述',
    images: [{ url: '/og-image.png', width: 1200, height: 630, alt: '网站预览' }],
  },
  twitter: {
    card: 'summary_large_image',
    title: '网站标题',
    description: '用于 Twitter 的描述',
    images: ['/og-image.png'],
  },
  // 按页面设置 alternates.canonical；根 '/' 会被子页面继承。
  robots: {
    index: true,
    follow: true,
  },
};
```

### app/sitemap.ts - 动态站点地图

```typescript
import type { MetadataRoute } from 'next';

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const baseUrl = 'https://your-site.com';
  const posts = await getPosts(); // 你的 CMS/DB

  return [
    {
      url: baseUrl,
      images: [`${baseUrl}/og-image.png`], // 图像站点地图条目
    },
    { url: `${baseUrl}/about` },
    ...posts.map((post) => ({
      url: `${baseUrl}/blog/${post.slug}`,
      lastModified: post.updatedAt, // 实际内容时间戳
    })),
  ];
}
```

`lastModified` 必须反映内容的实际最后更改 (CMS `updatedAt`、文件 mtime、git 提交日期) — Google 仅在它始终准确时使用 `lastmod`，并且 `new Date()` 在每次构建上标记所有内容为“刚刚更改”，这会导致 Google 忽略它。跳过 `changeFrequency` 和 `priority`：Google 忽略两者。

### app/robots.ts - 机器人配置

```typescript
import type { MetadataRoute } from 'next';

export default function robots(): MetadataRoute.Robots {
  const baseUrl = 'https://your-site.com';

  return {
    rules: [
      {
        userAgent: '*',
        allow: '/',
        disallow: ['/api/', '/admin/'],
        // 从不禁止 /_next/: 爬虫需要渲染关键 CSS/JS。
        // 命名组 (Googlebot, OAI-SearchBot…) 忽略这些规则；参见错误 11。
      },
    ],
    sitemap: `${baseUrl}/sitemap.xml`,
  };
}
```

> `host` 是有意省略的 — 它是一个非标准指令，Google 会忽略。使用规范 URL / 301 来声明首选主机。参见 [references/sitemap-robots.md](references/sitemap-robots.md)。

### app/manifest.ts - Web 应用程序清单

与 sitemap/robots 相同的 `MetadataRoute` 家族，放置在 `app/` 的根目录下。**不是 SEO 要求** — 一个 PWA 完整性的小细节，没有排名效果；除非网站（或可能成为）PWA，否则跳过它。完整示例在 [references/metadata-api.md](references/metadata-api.md#web-app-manifest--icon-file-conventions)。

### OG / Twitter 图片

设置社交图片的三种方法 — 喜欢文件约定胜过在元数据对象中手动同步 URL：

1. **元数据中的外部 URL**（上面 `openGraph.images` / `twitter.images` 的示例） — 适用于外部托管的图像。
2. **静态文件约定（推荐默认）**：将 `opengraph-image.(jpg|jpeg|png|gif)` 和/或 `twitter-image.*` 放入路由段（根为 `app/opengraph-image.png`，`/blog` 为 `app/blog/opengraph-image.png`）。Next.js 自动发出 `og:image`/`twitter:image` + `:type/:width/:height`。更深、更具体的图像会覆盖上面的图像。使用兄弟 `opengraph-image.alt.txt` 添加替代文本。如果文件超过 8 MB (OG) / 5 MB (Twitter)，构建会失败。
3. **使用 `ImageResponse` 动态生成**（每页/每篇帖子图像）：路由段中的 `opengraph-image.tsx` 导出 `alt`、`size`、`contentType` 和默认 `Image({ params })`（params 是 v16 中的 Promise）返回 `new ImageResponse(<jsx/>, { ...size })`。通过 Satori 渲染 — **仅限 flexbox，不能 `display: grid`**，500 KB 打包限制（JSX、字体、图像），字体 `ttf`/`otf`/`woff` 仅限；除非它读取请求时间数据，否则在构建时静态优化。完整示例、字体、`generateImageMetadata` 和 favicon/`icon.tsx`/`apple-icon` 约定：[references/metadata-api.md](references/metadata-api.md)。

## 关键原则

### 缓存组件与 SEO

使用 `cacheComponents: true` 时，对于可以共享且其新鲜度要求允许缓存的组件/数据，使用 `"use cache"`。静态内容不需要仅为 SEO 而添加额外的缓存指令：

```typescript
// app/(home)/sections/hero-section.tsx
import { cacheLife, cacheTag } from "next/cache";

export async function HeroSection() {
  "use cache";
  cacheLife("hours");   // SEO 内容每天更改几次；参见下面的配置文件
  cacheTag("hero");     // 通过 Server Action 中的 updateTag("hero") 使其失效

  const data = await fetchData();
  return <div>{/* SEO 可见内容 */}</div>;
}
```

从产品的最新鲜度要求中选择 `cacheLife`，并参考已安装的 Next.js 文档。不要从页面类别推断缓存生命周期；营销和法律页面也需要及时发布和失效。

**关键规则:**
- `"use cache"` 必须是函数体内的第一个语句（或对于文件级缓存，在文件顶部）
- 在纯 `"use cache"` 范围内没有 `cookies()`/`headers()`/运行时 `searchParams`。将公共内容与个性化数据分开；不要意外地为所有用户缓存私人信息。在使用实验性私人缓存之前，请检查已安装的文档。
- 在 Server Action 中使用 `updateTag("hero")` 使其失效（读取您的写入；在其中一个之外会抛出异常），或从 Route Handler / webhook 使用 `revalidateTag("hero", "max")`（一个参数的形式已弃用）
- 启用缓存组件时，路由段会导出 `revalidate`、`dynamic` 和 `fetchCache` 错误。如果没有启用，请遵循已安装版本的缓存模型。验证 `next build`、服务内容以及发布时失效。
- 数据库读取本身并不能使部署后的站点地图更新。配置并验证其刷新/失效路径。元数据可以是静态的或运行时依赖的；检查路由，而不是假设。

### SEO 渲染策略

| 策略 | 使用场景 | SEO 影响 |
|----------|----------|------------|
| "use cache" | 共享数据具有定义的刷新策略 | 可以将内容包含在预渲染的 shell 中 |
| SSG (静态) | 构建时已知的内容 | 内容在 HTML 中可用；计划更新 |
| SSR | 请求时需要的内容 | 内容在响应中可用；测量延迟 |
| CSR | 交互式或认证功能 | 避免依赖浏览器仅获取的公共内容 |

这些是渲染权衡，不是排名等级。客户端组件仍然可以服务器预渲染；`"use client"` 并不意味着其内容不在 HTML 中。

### 核心网络指标目标

| 指标 | 目标 | 影响 |
|--------|--------|--------|
| LCP (Largest Contentful Paint) | ≤ 2.5s | 加载速度 |
| INP (Interaction to Next Paint) | ≤ 200ms | 交互性 |
| CLS (Cumulative Layout Shift) | ≤ 0.1 | 视觉稳定性 |

- 使用按设备分段的字段测量的 75 个百分位数。单独评估每个指标；这不意味着 75% 的访问同时通过所有三个指标。Lighthouse 是实验室诊断，不是 INP 字段分数。
- 好的 CWV 并不保证排名。相关内容、可爬性和准确元数据仍然是必要的；避免发明数字排名权重。
- 保持移动内容、元数据和结构化数据与桌面版本相同。验证作者身份和资质，而不是生成它们。

## 参考

- **元数据 API** — [references/metadata-api.md](references/metadata-api.md)：编写 `generateMetadata`、OG/图标文件、`ImageResponse`、清单或当流式传输元数据 / `htmlLimitedBots` 处于活动状态时阅读
- **站点地图 & 机器人** — [references/sitemap-robots.md](references/sitemap-robots.md)：用于 `generateSitemaps`、图像/视频站点地图、多组机器人规则、静态 `robots.txt`/`sitemap.xml` 文件时阅读
- **JSON-LD 结构化数据** — [references/json-ld.md](references/json-ld.md)：添加任何 schema 类型之前阅读；有支持的/弃用的丰富结果列表和 `@graph` 模式
- **AI 搜索 (GEO/AEO) & AI 爬虫** — [references/ai-search.md](references/ai-search.md)：决定 GPTBot/OAI-SearchBot/ClaudeBot 等的机器人规则时阅读，或当询问关于 llms.txt 或 AI 概览时阅读
- **SEO 审计清单** — [references/checklist.md](references/checklist.md)：当需要端到端审计网站时阅读
- **故障排除** — [references/troubleshooting.md](references/troubleshooting.md)：当页面从 Google 中丢失、卡在“已发现/已爬取 — 目前未索引”或索引良好但从未水合时阅读
- **常见错误** — [references/troubleshooting.md](references/troubleshooting.md)：当页面从 Google 中丢失、卡在“已发现/已爬取 — 目前未索引”或索引良好但从未水合时阅读

## 避免常见错误

1. **混合 next-seo 与 Metadata API** - 在 App Router 中仅使用 Metadata API
2. **缺少规范 URL** - 当存在重复/参数化 URL 风险时，设置自引用的 `alternates.canonical`；它是一个提示，不是要求 — Google 可能选择自己的规范
3. **使用 CSR 进行 SEO 页面** - 使用 SSG/SSR 进行可索引内容
4. **在 robots.txt 中阻塞 `/_next/`** - 爬虫需要渲染关键 CSS/JS；永远不要禁止 `/_next/`
5. **缺少 metadataBase** - 不是构建错误：相对 OG/Twitter 图像 URL 会回退到 Vercel 部署 URL 或 `http://localhost:3000` 仅带警告，并且相对规范/hreflang URL 保持相对（Google 要求绝对 hreflang URL）
6. **元数据中的 Viewport** - `themeColor`/`colorScheme`/`viewport` 在 `metadata` 中被忽略；使用 `export const viewport`
7. **混合元数据对象与 generateMetadata** - 在同一路由段中仅使用其中一个
8. **在元数据 + 文件约定中重复图标** - 喜欢使用 `favicon.ico`/`icon.*`/`opengraph-image.*` 文件约定；它们自动发出标签并覆盖元数据对象
9. **全面阻止 AI 爬虫** - `GPTBot disallow: /` 阻止训练但将您置于 AI 搜索中；不要意外地阻止搜索爬虫（OAI-SearchBot、Claude-SearchBot、PerplexityBot）。参见 [references/ai-search.md](references/ai-search.md)
10. **为 Google 添加 `keywords` 元标签** - Google 完全忽略它（没有索引或排名效果）；它只是噪音，不是信号
11. **假设命名 robots.txt 组继承 `*` 规则** - 根据 RFC 9309 §2.2.1，`*` 组仅在没有任何组匹配时适用，并且 Google 永远不会将特定组与 `*` 合并。一个 `{ userAgent: 'OAI-SearchBot', allow: '/' }` 组会忽略通配符的 `/api/`/`/admin/` 禁止 — 在每个命名组中重复它们
12. **信任浏览器视图以获取机器人元数据** - 检查状态、标头和 Googlebot 和相关 HTML-limited 爬虫的完整生产响应。流式传输可能会将元数据放在初始 head 之外。一个伪造的 User-Agent 测试响应行为，而不是 Google 的实际爬取访问或索引；在可用的情况下使用 URL 检查和验证的机器人日志。
13. **假设索引良好的路由也 *工作*** - 一个 PPR 路由（构建输出中的 `◐`）可以提供完美的 SEO HTML，而其 `<Suspense>` 边界在直接加载时不会水合。在浏览器中直接加载路由并与之交互；观察和检查在 [references/troubleshooting.md](references/troubleshooting.md#ppr-route-serves-perfect-seo-html-but-client-components-never-hydrate)。

## 快速修复

### 为页面添加 noindex

```typescript
export const metadata: Metadata = {
  robots: {
    index: false,
    follow: true,
  },
};
```

保持页面可爬取，以便 `noindex` 被看到。Robots disallow 不是移除索引或访问控制机制。预览保护和 noindex 是分开的问题；参见 [references/sitemap-robots.md](references/sitemap-robots.md)。

### 每页动态元数据

```typescript
type Props = { params: Promise<{ id: string }> };

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { id } = await params;            // params 是当前 Next.js 中的 Promise
  const product = await getProduct(id);
  return {
    title: product.name,
    description: product.description,
  };
}
```

### 动态路由的规范

```typescript
type Props = { params: Promise<{ slug: string }> };

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { slug } = await params;
  return {
    alternates: {
      canonical: `/products/${slug}`,
    },
  };
}
```
