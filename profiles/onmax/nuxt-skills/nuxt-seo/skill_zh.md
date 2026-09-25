# Nuxt SEO

```bash
npx nuxi module add @nuxtjs/seo
```

## 何时使用

用于：

- SEO 配置（网站 URL、名称、可索引性）
- robots.txt 和 sitemap.xml 的生成
- 动态 OG 图片的生成
- JSON-LD 结构化数据（schema.org）
- 面包屑和规范 URL

## 文件加载

**根据您的任务考虑加载以下参考文件：**

- [ ] [references/site-config.md](references/site-config.md) - 如果配置网站 URL、名称或 SEO 基础
- [ ] [references/crawlability.md](references/crawlability.md) - 如果设置 robots.txt 或 sitemap.xml
- [ ] [references/og-image.md](references/og-image.md) - 如果生成动态 OG 图片
- [ ] [references/schema-org.md](references/schema-org.md) - 如果添加 JSON-LD 结构化数据
- [ ] [references/utilities.md](references/utilities.md) - 如果处理面包屑、规范 URL 或链接检查

**不要一次性加载所有文件。** 仅加载与当前任务相关的文件。

## 网站配置

所有 SEO 模块的基础。在 `nuxt.config.ts` 中配置 `site`，通过 `useSiteConfig()` 访问。有关完整选项，请参阅 [references/site-config.md](references/site-config.md)。

## 模块概览

| 模块            | 目的         | 关键 API                       |
| ----------------- | --------------- | ----------------------------- |
| nuxt-site-config  | 共享配置   | `useSiteConfig()`             |
| @nuxtjs/robots    | robots.txt      | `useRobotsRule()`             |
| @nuxtjs/sitemap   | sitemap.xml     | `defineSitemapEventHandler()` |
| nuxt-og-image     | OG 图片       | `defineOgImage()`             |
| nuxt-schema-org   | JSON-LD         | `useSchemaOrg()`              |
| nuxt-seo-utils    | 元数据工具  | `useBreadcrumbItems()`        |
| nuxt-link-checker | 链接验证     | 构建时检查             |

## Nuxt Content v3

使用 `asSeoCollection()` 从 frontmatter 自动生成 sitemap、og-image 和 schema-org：

```ts
// content.config.ts
import { defineCollection, defineContentConfig } from '@nuxt/content'
import { asSeoCollection } from '@nuxtjs/seo/content'

export default defineContentConfig({
  collections: {
    posts: defineCollection(asSeoCollection({ type: 'page', source: 'posts/**' }))
  }
})
```

**重要提示：** 在模块数组中先加载 `@nuxtjs/seo`，再加载 `@nuxt/content`：

```ts
export default defineNuxtConfig({
  modules: ['@nuxtjs/seo', '@nuxt/content']
})
```

Frontmatter 字段：`ogImage`、`sitemap`、`robots`、`schemaOrg`。

## 相关技能

- [nuxt-content](../nuxt-content/SKILL.md) - 用于使用 SEO frontmatter 的 MDC 渲染

## 链接

- [文档](https://nuxtseo.com)
- [GitHub](https://github.com/harlan-zw/nuxt-seo)

## 令牌效率

主要技能：~250 令牌。每个子文件：~400-600 令牌。仅加载与当前任务相关的文件。
