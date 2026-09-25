# Next.js SEO 优化

Next.js 应用路由应用的全面 SEO 指南。

## 从证据和有用内容开始

在更改框架代码之前，先阅读已安装的 Next.js 版本和相关的 `node_modules/next/dist/docs/` 指南；当本地文档不可用时，使用当前的官方文档。当可用时，使用 Vercel MCP 文档搜索平台行为，但请检查检索到的示例与已安装的框架是否一致。不要从搜索片段中复制一个遗留的缓存 API 到更新的应用程序中。

- 首先解决读者的任务。一个简短有用的页面不需要填充。
  给 H1、副标题和章节标题不同的任务；不要在每个标题中重复相同的短语以进行 SEO。保持 UI 复制简洁、具体和有用。
- 不要添加通用的介绍、关键词块、装饰性徽章、常见问题解答或 TL;DR 只是为了让页面看起来经过优化。只有当它回答一个真实的问题时才添加内容。保留必要的解释和披露。
- 只有当每个页面都提供独特、可维护的价值时，才创建团队、位置或类别页面。一个交换的名称/标志和重复的列表是不够的。
- 从当前数据描述季节、可用性和更新时间。不要在活跃的服务上留下预发布副本，也不要更改时间戳以保持新鲜。
- 分离证据：一个搜索控制台性能导出显示查询和流量，而不是索引状态、Google 的规范选择或 CWV。使用相关的报告或 URL 检查；将不可用的检查标记为未验证。
- 在预测影响之前报告发现和验证。没有排名、索引、丰富结果或 AI 引用的保证。

## 快速 SEO 审计

对任何 Next.js 项目运行此检查清单：

1. **检查 robots.txt**: `curl https://your-site.com/robots.txt`
2. **检查 sitemap**: `curl https://your-site.com/sitemap.xml`
3. **检查元数据**: 查看页面源代码，搜索 `<title>` 和 `<meta name="description">`
4. **检查 JSON-LD**: 查看页面源代码，搜索 `application/ld+json`
5. **检查核心网络指标**: 使用 PageSpeed Insights (pagespeed.web.dev) 和搜索控制台的 CWV 报告获取字段数据 — Lighthouse 仅是实验室诊断，无法测量 INP

## 必要文件

### app/layout.tsx - 根元数据

```typescript
import type { Metadata, Viewport } from 'next';

// Viewport 必须是单独导出 — `themeColor`、`colorScheme` 和
// `viewport` 在 `metadata` 对象中已弃用（自 v14：今天仍然发出警告，但不保证会保持）。
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
  // ~150-160 个字符是一个指南，不是一个限制 — Google 会根据设备/查询截断
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
  // 每页设置 alternates.canonical；根 '/' 会被子页面继承。
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

`lastModified` 必须反映内容的实际最后更改（CMS `updatedAt`、文件 mtime、git 提交日期）— Google 仅在它始终准确时使用 `lastmod`，并且 `new Date()` 在每次构建上标记所有内容为“刚刚更改”，这会教 Google 忽略它。跳过 `changeFrequency` 和 `priority`：Google 忽略两者。

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
        // 不要禁止 /_next/ — 蜘蛛需要渲染关键 CSS/JS
        // 不要添加特定机器人的规则（Googlebot、Bingbot）除非覆盖通配符 —
        // 如果你这样做，请重复所有禁止：命名组不会继承 `*` 规则
        // (RFC 9309 §2.2.1；Google 永远不会将特定组与 `*` 合并)
      },
    ],
    sitemap: `${baseUrl}/sitemap.xml`,
  };
}
```

> `host` 是故意省略的 — 它是一个非标准指令，Google 会忽略。使用规范 URL / 301 来声明首选主机。参见 [references/sitemap-robots.md](references/sitemap-robots.md)。

### app/manifest.ts - Web 应用程序清单

与站点地图/机器人相同的 `MetadataRoute` 家族，放置在 `app/` 的根目录下。**不是 SEO 要求** — 一个 PWA 完整性的小细节，没有排名效果；除非网站是（或可能成为）PWA，否则跳过它。完整示例在 [references/metadata-api.md](references/metadata-api.md#web-app-manifest--icon-file-conventions)。

### OG / Twitter 图片

设置社交图片的三种方法 — 喜欢文件约定而不是在元数据对象中手动同步 URL：

1. **元数据中的外部 URL**（上面 `openGraph.images` / `twitter.images` 的示例）— 适用于外部托管的图像。
2. **静态文件约定（推荐默认）**：将 `opengraph-image.(png|jpg|gif)` 和/或 `twitter-image.*` 放入路由段（根为 `app/opengraph-image.png`，`/blog` 为 `app/blog/opengraph-image.png`）。Next.js 会自动发出 `og:image`/`twitter:image` + `:type/:width/:height`。更深、更具体的图像会覆盖上面的图像。使用兄弟 `opengraph-image.alt.txt` 添加替代文本。如果文件超过 8 MB（OG）/ 5 MB（Twitter），构建会失败。
3. **使用 `ImageResponse` 动态生成**（每页/每篇帖子图像）：路由段中的 `opengraph-image.tsx` 导出 `alt`、`size`、`contentType` 和默认 `Image({ params })`（params 是 v16 中的 Promise）返回 `new ImageResponse(<jsx/>, { ...size })`。通过 Satori 渲染 — **仅 flexbox，不能 `display: grid`**；除非它读取请求时间数据，否则在构建时静态优化。完整示例、字体、`generateImageMetadata` 和 favicon/`icon.tsx`/`apple-icon` 约定：[references/metadata-api.md](references/metadata-api.md)。

## 关键原则

### 缓存组件与 SEO

使用 `cacheComponents: true` 时，对于可以共享且其新鲜度要求允许缓存的组件/数据，使用 `"use cache"`。静态内容不需要额外的缓存指令仅用于 SEO：

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

从产品的最新鲜度要求和使用中的 Next.js 文档中选择 `cacheLife`。不要从页面类别推断缓存生命周期；营销和法律页面也需要及时发布和失效。

**关键规则：**
- `"use cache"` 必须是函数体内的第一个语句（或对于文件级缓存，在文件顶部）
- 在纯 `"use cache"` 范围内不要使用 `cookies()`/`headers()`/运行时 `searchParams`。将公共内容与个性化数据分开；不要意外地为所有用户缓存私人信息。在使用实验性私人缓存之前，请查看已安装的文档。
- 在 Server Action 中使用 `updateTag("hero")` 使其失效（读取您的写入；在其中一个之外会抛出），或从 Route Handler / webhook 使用 `revalidateTag("hero", "max")`（传递配置文件 — 单参数形式是遗留行为）— 喜欢这些而不是 `export const revalidate`
- 从实际新鲜度要求中选择缓存生命周期，而不是对长缓存进行 SEO 偏好。验证 `next build`、提供的内容和发布时失效。使用缓存组件时，遗留路由选项（如 `revalidate`）将被禁用；如果没有它，请遵循已安装版本的受支持缓存模型。
- 数据库读取本身并不能在部署后更新站点地图。配置并验证其刷新/失效路径。元数据可以是静态的或运行时依赖的；检查路由而不是假设。

### SEO 渲染策略

| 策略 | 使用条件 | SEO 影响 |
|------|----------|------------|
| "use cache" | 共享具有定义刷新策略的数据 | 可以将内容包含在预渲染的 shell 中 |
| SSG (静态) | 构建时已知的内容 | 内容在 HTML 中可用；计划更新 |
| SSR | 需要在请求时获取的内容 | 内容在响应中可用；测量延迟 |
| CSR | 交互式或经过身份验证的功能 | 避免依赖仅浏览器获取的关键公共内容 |

这些是渲染权衡，不是排名等级。客户端组件仍然可以服务器预渲染；`"use client"` 并不意味着其内容在 HTML 中不存在。

### 核心网络指标目标

| 指标 | 目标 | 影响 |
|--------|--------|--------|
| LCP (Largest Contentful Paint) | < 2.5s | 加载速度 |
| INP (Interaction to Next Paint) | < 200ms | 交互性 |
| CLS (Cumulative Layout Shift) | < 0.1 | 视觉稳定性 |

- 使用按设备分段的字段测量的 75 个百分位数。单独评估每个指标；这不意味着同一 75% 的访问同时通过所有三个指标。Lighthouse 是实验室诊断，不是 INP 字段分数。
- 好的 CWV 并不保证排名。相关内容、可爬性和准确元数据仍然是必要的；避免发明数字排名权重。
- 保持移动内容、元数据和结构化数据与桌面等效。验证作者身份和资格，而不是生成它们。

## 参考

- **元数据 API** — [references/metadata-api.md](references/metadata-api.md)：编写 `generateMetadata`、OG/图标文件、`ImageResponse`、清单或当流式传输元数据 / `htmlLimitedBots` 在使用时阅读
- **站点地图 & 机器人** — [references/sitemap-robots.md](references/sitemap-robots.md)：用于 `generateSitemaps`、图像/视频站点地图、多组机器人规则、静态 `robots.txt`/`sitemap.xml` 文件时阅读
- **JSON-LD 结构化数据** — [references/json-ld.md](references/json-ld.md)：添加任何模式类型之前阅读；有支持的/弃用的丰富结果列表和 `@graph` 模式
- **AI 搜索 (GEO/AEO) & AI 蜘蛛** — [references/ai-search.md](references/ai-search.md)：决定 GPTBot/OAI-SearchBot/ClaudeBot 等机器人的 robots 规则时阅读，或当询问关于 llms.txt 或 AI 概览时阅读
- **SEO 审计检查清单** — [references/checklist.md](references/checklist.md)：当需要端到端审计网站时阅读
- **故障排除** — [references/troubleshooting.md](references/troubleshooting.md)：当页面从 Google 中丢失、卡在“已发现/爬取 — 目前未索引”或索引良好但从未水合时阅读

## 常见错误

1. **混合 next-seo 与 Metadata API** - 在应用路由中仅使用 Metadata API
2. **缺少规范 URL** - 当存在重复/参数化 URL 风险时，设置自引用的 `alternates.canonical`；它是一个提示，不是一个要求 — Google 可能选择自己的规范
3. **使用 CSR 进行 SEO 页面** - 使用 SSG/SSR 进行可索引内容
4. **在 robots.txt 中阻止 `/_next/`** - 蜘蛛需要渲染关键 CSS/JS；永远不要禁止 `/_next/`
5. **缺少 metadataBase** - 对于元数据中的相对 URL 是必需的
6. **元数据中的 Viewport** - 必须是单独导出
7. **混合元数据对象和 generateMetadata** - 在同一路由段中只使用其中一个
8. **在元数据和文件约定中重复图标** - 喜欢 `favicon.ico`/`icon.*`/`opengraph-image.*` 文件约定；它们会自动发出标签并覆盖元数据对象
9. **全面阻止 AI 蜘蛛** - `GPTBot disallow: /` 阻止训练但将您置于 AI 搜索中；不要意外阻止引用机器人（OAI-SearchBot、PerplexityBot）。参见 [references/ai-search.md](references/ai-search.md)
10. **为 Google 添加 `keywords` 元标签** - Google 完全忽略它（没有索引或排名效果）；它只是噪音，不是信号
11. **假设命名 robots.txt 组继承 `*` 规则** - 根据 RFC 9309 §2.2.1，`*` 组仅在没有任何组匹配时适用，并且 Google 永远不会将特定组与 `*` 合并。`{ userAgent: 'OAI-SearchBot', allow: '/' }` 组会删除通配符的 `/api/`/`/admin/` 禁止 — 在每个命名组中重复它们
12. **信任浏览器视图进行机器人元数据** - 检查状态、标头和 Googlebot 和相关 HTML-limited 机器人的完整生产响应。流式传输可能会将元数据放置在初始 head 之外。一个伪造的 User-Agent 测试响应行为，而不是 Google 的实际爬取访问或索引；在可用时使用 URL 检查和验证的机器人日志。
13. **假设索引良好的路由也 *工作*** - 一个 PPR 路由（构建输出中的 `◐`）可以提供完美的 SEO HTML，而其 `<Suspense>` 边界在直接加载时不会水合。在浏览器中直接加载路由并与之交互；观察和检查在 [references/troubleshooting.md](references/troubleshooting.md#ppr-route-serves-perfect-seo-html-but-client-components-never-hydrate)。

## 快速修复

### 向页面添加 noindex

```typescript
export const metadata: Metadata = {
  robots: {
    index: false,
    follow: true,
  },
};
```

保持页面可爬取，以便 `noindex` 被看到。Robots disallow 不是索引删除或访问控制机制。预览保护和 noindex 是分开的问题；参见 [references/sitemap-robots.md](references/sitemap-robots.md)。

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
