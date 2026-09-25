该技能基于 Nitro v3（测试版），生成于 2026-06-22。

Nitro 是一个与框架无关、与部署无关的服务器工具包，由 [H3](https://h3.dev) v2、[unstorage](https://unstorage.unjs.io) 和 Vite/Rolldown/Rollup 驱动。它为 Nuxt 提供支持，并可以独立运行。从一个代码库，它为 Node.js、Bun、Deno、Cloudflare、Vercel、Netlify 等构建优化输出。

主要功能：
- 使用 H3 v2 事件处理器、动态参数和方法后缀的**文件系统路由**。
- **路由规则**，用于声明式缓存、标头、重定向、代理和认证。
- 基于 **unstorage** KV 的**缓存层**（缓存处理器/函数、SWR）。
- 可通过 `NITRO_*` 环境变量覆盖的**运行时配置**。
- **任务**（按需 + 定时/计划任务）、**WebSockets**/SSE、SQL **数据库**层和**OpenAPI** 自动文档。
- **插件 & 生命周期钩子**、自定义 **渲染器/**服务器入口**和可移植的**部署预设**。

> Nitro v3 将包名从 `nitropack` 更改为 `nitro`，并采用 H3 v2（Web 标准 `Request`/`Response`）。如果不确定 v2 与 v3 API 的差异，请先阅读 [advanced-migration](references/advanced-migration.md)。

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
| OpenAPI | 从 `defineRouteMeta` 自动规范、标量/Swagger UI | [features-openapi](references/features-openapi.md) |

## 高级 / 部署

| 主题 | 描述 | 参考 |
|------|------|------|
| 部署预设 | 运行时 & 提供商、兼容性日期、平台集成 | [deploy-presets](references/deploy-presets.md) |
| v2 → v3 迁移 | 包名更改、`nitro/*` 导入、H3 v2 API、预设更改 | [advanced-migration](references/advanced-migration.md) |
