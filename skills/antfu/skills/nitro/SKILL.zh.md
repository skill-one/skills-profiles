---
name: nitro
description: Nitro 是一个与框架无关的服务器工具包（为 Nuxt 提供支持），用于在任何地方构建和部署 Web 服务器。当您使用 `nitro.config`、服务器路由/事件处理程序、路由规则、缓存、存储、任务、WebSocket 或部署到 Node/Bun/Deno/Cloudflare/Vercel 时，请使用它。
---

技能基于 Nitro v3（测试版，3.0.260903），生成于 2026-09-25。

Nitro 是一个由 [H3](https://h3.dev) v2、[unstorage](https://unstorage.unjs.io) 和 Vite/Rolldown/Rollup 驱动的、与框架无关、与部署无关的服务器工具包。它为 Nuxt 提供支持，并且可以独立运行。从一个代码库，它可以构建针对 Node.js、Bun、Deno、Cloudflare、Vercel、Netlify 等的优化输出。

主要功能：
- 使用 H3 v2 事件处理器、动态参数和方法后缀的**文件系统路由**。
- **路由规则**，用于声明式缓存、标头、重定向、代理和 CORS。
- 在**unstorage** KV 层上方的**缓存**层（缓存的处理器/函数、SWR）。
- 可通过 `NITRO_*` 环境变量覆盖的**运行时配置**。
- **任务**（按需 + 定时/计划任务）、**WebSockets**/SSE、SQL **数据库**层和**OpenAPI** 自动文档。
- **插件 & 生命周期钩子**、自定义 **渲染器/**服务器入口**和可移植的**部署预设**。

> **v3 的主要变更**（与 `nitropack` v2 相比）：包名从 `nitropack` → `nitro`，并使用 H3 v2（Web 标准 `Request`/`Response`）；**自动导入已移除**（显式导入所有内容）；目录扫描通过 `serverDir` **可选**；`useStorage` → `useKV` (`nitro/kv`)，以及 `storage` 配置选项 → `kv`；缓存 `swr` 现在默认为 `false`。如果不确定 v2 与 v3 API 的差异，请先阅读 [advanced-migration](references/advanced-migration.md)。

## 核心

| 主题 | 描述 | 参考 |
|------|------|------|
| 路由 | 基于文件的路线、`defineHandler`、参数、中间件、路线规则、错误 | [core-routing](references/core-routing.md) |
| 配置 | `nitro.config.ts`、`defineConfig`、关键选项、运行时配置 | [core-configuration](references/core-configuration.md) |
| 存储 | unstorage KV、挂载点、驱动程序、动态挂载 | [core-storage](references/core-storage.md) |
| 缓存 | `defineCachedHandler`、`defineCachedFunction`、SWR、失效 | [core-cache](references/core-cache.md) |
| 资产 | 公共资产、压缩、通过存储的服务器资产 | [core-assets](references/core-assets.md) |
| 渲染 | 渲染器（HTML/SSR）、服务器入口、框架集成 | [core-rendering](references/core-rendering.md) |

## 功能

| 主题 | 描述 | 参考 |
|------|------|------|
| 插件 & 钩子 | `definePlugin`、运行时生命周期钩子、错误捕获 | [features-plugins](references/features-plugins.md) |
| 任务 | 按需 & 定时（计划任务）任务、`runTask` | [features-tasks](references/features-tasks.md) |
| WebSocket & SSE | `defineWebSocketHandler`、发布/订阅、命名空间、事件流 | [features-websocket](references/features-websocket.md) |
| 数据库 | 通过 db0 的内置 SQL 层、`useDatabase`、连接器 | [features-database](references/features-database.md) |
| OpenAPI | 从 `defineRouteMeta` 自动生成规范、标量/Swagger UI | [features-openapi](references/features-openapi.md) |

## 高级 / 部署

| 主题 | 描述 | 参考 |
|------|------|------|
| 部署预设 | 运行时 & 提供商、兼容性日期、平台集成 | [deploy-presets](references/deploy-presets.md) |
| v2 → v3 迁移 | 包名变更、`nitro/*` 导入、H3 v2 API、预设变更 | [advanced-migration](references/advanced-migration.md) |
