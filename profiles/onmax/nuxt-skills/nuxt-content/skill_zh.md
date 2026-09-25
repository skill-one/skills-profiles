# Nuxt 内容

## 工作流程

1.  检查已安装的 `@nuxt/content` 版本、`content.config.ts`、`content/` 下匹配的文件以及使用它们的 Nuxt 表面。当集合、源 glob、模式和使用者一致时，就会理解分支。
2.  打开下方最小的匹配指南。仅将 Nuxt 内容指导应用于内容拥有的 API；当那些包拥有剩余表面时，使用 Nuxt、Nuxt Studio、Nuxt UI 或 Vue 的指导。
3.  使用带类型集合和基于负载的 Nuxt 数据加载进行实现。当集合类型解析、预期查询返回预期文档形状、渲染路由在目标渲染模式下工作时，更改即完成。

## 路由

| 任务                                                                                 | 打开                                     |
| ------------------------------------------------------------------------------------ | ---------------------------------------- |
| 集合类型、模式、索引、本地/远程源或区域前缀         | [集合](references/collections.md)         |
| 过滤、排序、分页、导航、周边或搜索                  | [查询](references/querying.md)           |
| Markdown、MDC、`ContentRenderer`、文本组件或代码高亮             | [渲染](references/rendering.md)         |
| 数据库适配器、Markdown 处理、渲染器别名或部署存储      | [配置](references/config.md)            |
| 钩子、转换器、自定义源、原始内容、调试或 Content v2 迁移 | [高级](references/advanced.md)          |
| 可视化编辑、认证、媒体、草稿或 Git 发布                     | `nuxt-studio` 技能                      |
| 编写或重构文档文本                                         | `document-writer` 技能                  |

## 基线

```ts
// content.config.ts
import { defineCollection, defineContentConfig } from '@nuxt/content'
import { z } from 'zod'

export default defineContentConfig({
  collections: {
    docs: defineCollection({
      type: 'page',
      source: 'docs/**',
      schema: z.object({
        updatedAt: z.date().optional(),
      }),
    }),
  },
})
```

```vue
<script setup lang="ts">
const route = useRoute()
const { data: page } = await useAsyncData(route.path, () => {
  return queryCollection('docs').path(route.path).first()
})
</script>

<template>
  <ContentRenderer v-if="page" :value="page" />
</template>
```

使用 `npx nuxi typecheck` 验证生成的集合类型。当查询为空时，在更改查询逻辑之前，确认其集合源是否包含文件——特别是 `.navigation.yml`。
