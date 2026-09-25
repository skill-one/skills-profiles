Nuxt 是一个全栈 Vue 框架，提供服务器端渲染、基于文件的路由、自动导入以及强大的模块系统。它使用 Nitro 作为其服务器引擎，可在 Node.js、无服务器和边缘平台上进行通用部署。

> 该技能基于 Nuxt 4.x，生成于 2026-06-22。

> **Nuxt 4 注意事项：** 默认的 `srcDir` 是 `app/` — Vue 应用代码（`app.vue`、`components/`、`composables/`、`pages/` 等）位于 `app/` 下，而 `server/`、`shared/`、`public/`、`modules/`、`layers/` 和 `nuxt.config.ts` 则位于项目根目录。`~`/`@` 别名现在指向 `app/`；使用 `~~`/`@@` 指向根目录。

## 核心

| 主题               | 描述                                                                | 参考                                                          |
| ------------------- | -------------------------------------------------------------------------- | ------------------------------------------------------------------ |
| 目录结构           | Nuxt 4 `app/` srcDir、`shared/`、别名、约定                      | [core-directory-structure](references/core-directory-structure.md) |
| 配置               | `nuxt.config.ts`、`app.config.ts`、别名、`compatibilityVersion`、实验性功能 | [core-config](references/core-config.md)                           |
| CLI 命令           | 开发服务器、构建、生成、预览和实用工具命令                         | [core-cli](references/core-cli.md)                                 |
| 路由               | 基于文件的路由、动态路由、命名视图、布局属性、中间件                | [core-routing](references/core-routing.md)                         |
| 数据获取           | `useFetch`、`useAsyncData`、`$fetch`、`createUseFetch` 工厂、缓存          | [core-data-fetching](references/core-data-fetching.md)             |
| 模块               | 创建和使用 Nuxt 模块、Nuxt Kit 实用工具                        | [core-modules](references/core-modules.md)                         |
| 部署               | 使用 Nitro 的平台无关部署、Vercel、Netlify、Cloudflare             | [core-deployment](references/core-deployment.md)                   |

## 功能

| 主题                    | 描述                                                         | 参考                                                                      |
| ------------------------ | ------------------------------------------------------------------- | ------------------------------------------------------------------------------ |
| 组合式自动导入           | Vue/Nuxt 组合式、自定义组合式、`shared/`、`useAnnouncer`   | [features-composables](references/features-composables.md)                     |
| 组件自动导入             | 组件命名、懒加载、hydration 策略                            | [features-components-autoimport](references/features-components-autoimport.md) |
| 内置组件                | `NuxtLink`、`NuxtPage`、`NuxtLayout`、`NuxtAnnouncer`、`ClientOnly` 等 | [features-components](references/features-components.md)                       |
| 状态管理                 | `useState` 组合式、SSR 友好的状态、Pinia 集成          | [features-state](references/features-state.md)                                 |
| 服务器路由              | API 路由、服务器中间件、Nitro 服务器引擎                  | [features-server](references/features-server.md)                               |

## 渲染

| 主题           | 描述                                                       | 参考                                        |
| --------------- | ----------------------------------------------------------------- | ------------------------------------------------ |
| 渲染模式       | 通用（SSR）、客户端（SPA）、混合渲染、路由规则                | [rendering-modes](references/rendering-modes.md) |

## 最佳实践

| 主题                  | 描述                                                       | 参考                                                                  |
| ---------------------- | ----------------------------------------------------------------- | -------------------------------------------------------------------------- |
| 数据获取模式           | 高效获取、缓存、并行请求、错误处理    | [best-practices-data-fetching](references/best-practices-data-fetching.md) |
| SSR & Hydration        | 避免 context 泄漏、hydration 不匹配、组合式模式 | [best-practices-ssr](references/best-practices-ssr.md)                     |

## 高级

| 主题            | 描述                                                        | 参考                                                            |
| ---------------- | ------------------------------------------------------------------ | -------------------------------------------------------------------- |
| 层级             | 使用可重用层级扩展应用                        | [advanced-layers](references/advanced-layers.md)                     |
| 生命周期钩子  | 构建时、运行时和服务器钩子                              | [advanced-hooks](references/advanced-hooks.md)                       |
| 模块开发       | 使用 Nuxt Kit 发布模块、键组合式、依赖关系 | [advanced-module-authoring](references/advanced-module-authoring.md) |
