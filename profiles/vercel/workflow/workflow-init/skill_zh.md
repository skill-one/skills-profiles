# workflow-init

在安装 `workflow` 之前，对 Vercel Workflow SDK 进行初始设置。获取用户所用框架的官方入门指南。

## 决策流程

### 0) 健康检查
读取 `package.json`。如果 `workflow` 已经是依赖项，则告知用户使用 `/workflow`（它从 `node_modules/workflow/docs/` 读取版本化文档）。只有当 `workflow` 缺失时才继续。

### 1) 确定框架
**非交互式：** 如果用户在提示中指定了框架，则直接使用。

**自动检测：** 检查 `package.json` 依赖项和配置文件。使用第一个匹配项：

1. **Next.js** - `next` 依赖项或 `next.config.*`
2. **Nuxt** - `nuxt` 依赖项或 `nuxt.config.*`
3. **SvelteKit** - `@sveltejs/kit` 依赖项或 `svelte.config.*`
4. **Astro** - `astro` 依赖项或 `astro.config.*`
5. **NestJS** - `@nestjs/core` 依赖项或 `nest-cli.json`
6. **Nitro** - `nitro` 依赖项或 `nitro.config.*`
7. **Express** - `express` 依赖项
8. **Fastify** - `fastify` 依赖项
9. **Hono** - `hono` 依赖项
10. **Vite** - `vite` 依赖项（且不在上述匹配项中）

如果没有匹配项或多个匹配项，则要求用户选择。

### 2) 获取并遵循入门指南
获取以下 URL 中的**一个**并按步骤进行：

| 框架 | URL |
|-------|-----|
| Next.js | https://workflow-sdk.dev/docs/getting-started/next |
| Express | https://workflow-sdk.dev/docs/getting-started/express |
| Hono | https://workflow-sdk.dev/docs/getting-started/hono |
| Fastify | https://workflow-sdk.dev/docs/getting-started/fastify |
| NestJS | https://workflow-sdk.dev/docs/getting-started/nestjs |
| Nitro | https://workflow-sdk.dev/docs/getting-started/nitro |
| Nuxt | https://workflow-sdk.dev/docs/getting-started/nuxt |
| Astro | https://workflow-sdk.dev/docs/getting-started/astro |
| SvelteKit | https://workflow-sdk.dev/docs/getting-started/sveltekit |
| Vite | https://workflow-sdk.dev/docs/getting-started/vite |

每个指南涵盖：安装依赖项、配置框架、创建第一个工作流、创建路由处理器、运行并验证。

### 3) 验证设置
- 按指南启动开发服务器。
- 使用提供的 `curl` 触发示例端点。
- 确认日志显示工作流和步骤正在执行。
- 可选：`npx workflow web` 或 `npx workflow inspect runs`。

### 4) 尚未选择框架？
如果不存在框架，则询问用户希望创建什么：
- **Web 应用**：Next.js / Nuxt / SvelteKit / Astro
- **API 服务器**：Express / Fastify / Hono
- **最小化服务器**：Nitro 或 Vite

然后遵循所选指南的“创建您的项目”部分。

## 概念问题（预安装）
如果用户在安装前提出概念问题，则获取：
- https://workflow-sdk.dev/docs/foundations/workflows-and-steps
- https://workflow-sdk.dev/cookbook

## 交接
当设置完成后，告知用户：**使用 `/workflow` 进行持续开发** - 它读取捆绑在 `node_modules/workflow/docs/` 中的版本化文档。
