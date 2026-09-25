将特定于路由框架的深度工作引导至此技能中的指南：`references/astro.md`、`references/nextjs.md`、`references/nuxt.md`、`references/sveltekit.md`、`references/tanstack.md`、`references/vite.md`。

## 环境变量：现代规则（首先阅读）

环境变量值在**构建时**注入。任何更改（客户端或服务器端）都需要**重新部署**——在 UI/CLI 中编辑变量不会使实时站点或已部署的函数更新，直到新的构建运行。

**永远不要使用客户端前缀来存储秘密。** 客户端前缀的变量会被内联到浏览器包中：
`VITE_`、`NEXT_PUBLIC_`、`PUBLIC_`、`NUXT_PUBLIC_`、`REACT_APP_`、`GATSBY_`、`VUE_APP_`。

框架的客户端嵌入前缀：CRA `REACT_APP_`，Gatsby `GATSBY_`，Next `NEXT_PUBLIC_`，Nuxt `NUXT_ENV_`，Vue CLI `VUE_APP_`。

**作用域：** 构建时访问需要**构建**作用域；SSR/DSG 运行时访问需要**函数和构建**。`netlify.toml` 仅在构建时读取——函数在运行时无法读取它；在 UI/CLI/API 中设置运行时变量。

Netlify 构建变量不能用作 UI 或 `netlify.toml` 环境部分的值。在构建命令之前内联设置它们：
```toml
[build]
  command = "REACT_APP_CONTEXT=$CONTEXT npm run build"
```

## SPA 重定向和 SSR 通用陷阱

SPAs（React、Vue CLI、Vite、Nuxt 的 SPA 模式）需要重定向以提供 `index.html` 用于 `pushState`：
```
/* /index.html 200
```

**在采用 SSR 适配器时移除任何 SPA 通用重定向。** 剩余的 `/* → /index.html 200` 静默地提供静态 `index.html` 用于 SSR 页面和 API 路由——用户重定向会覆盖适配器生成的路由。

## 本地开发与平台模拟（无需 Netlify CLI）

基于 Vite 的框架在开发服务器中模拟 Netlify 基本功能（函数、边缘函数、块、Netlify 数据库、缓存 API、图像 CDN、重定向/重写、标头、环境变量、AI 网关）：

| 框架 | 插件/模块 | 运行 |
|-------|-----------|-----|
| Astro (5.12+) | 内置（Netlify Vite 插件自动加载） | `astro dev` |
| Nuxt | `@netlify/nuxt` | `nuxt dev` |
| React Router | `@netlify/vite-plugin` | `react-router dev` |
| SolidStart 2 | `@netlify/vite-plugin` | `vite dev` |
| TanStack Start | `@netlify/vite-plugin-tanstack-start` | (vite) |
| Vite | `@netlify/vite-plugin` | `npx vite` |

仍然需要 `netlify dev`（Netlify CLI）：Gatsby 生成的函数（首先运行 `netlify build`），Angular SSR 本地测试（`netlify serve`），以及没有 Vite 插件的框架。

**`netlify dev` 陷阱：** 在 `[dev]` 中同时存在自定义 `command` 和 `targetPort`，你必须设置 `framework = "#custom"`——否则检测器会运行，而你的自定义命令会被静默忽略。

## 按框架的构建设置

| 框架 | 构建命令 | 发布 |
|-------|-----------|-----|
| Angular (标准) | `ng build --prod` | `dist/YOUR_PROJECT_NAME` |
| Astro | `astro build` | `dist` |
| Create React App | `react-scripts build` | `build` |
| Eleventy | `eleventy` | `_site` |
| Gatsby | `gatsby build` | `public` |
| Hugo | `hugo` | `public` |
| Hydrogen | `remix vite:build` | `dist/client` |
| Next.js (SSR/混合) | `next build` | `.next` |
| Next.js (静态导出) | `next build && next export` | `out` (`NETLIFY_NEXT_PLUGIN_SKIP=true`) |
| Nuxt 3 | `nuxt build` | `dist` |
| Nuxt 2 | `nuxt generate` | `dist` |
| React Router | `react-router build` | `build/client` |
| Remix (Vite) | `remix vite:build` | `build/client` |
| SolidStart 2 (Vite 插件) | `vite build` | `dist/client` |
| SolidStart 2 (Nitro) | `vite build` | `dist` |
| SolidStart 1.x | `vinxi build` | `dist` |
| SvelteKit | `vite build` | `build` |
| TanStack Start (1.132.0+) | `vite build` | `dist/client` |
| Vite | `vite build` | `dist` |
| Vue CLI | `vue-cli-service build` | `dist` |

检测建议这些；在 `netlify.toml` 或 UI（项目配置 > 构建 & 部署 > 持续部署 > 构建 设置）中覆盖。

## SSR / 适配器设置

### Astro
`npx astro add netlify` 安装适配器并编辑 `astro.config.mjs`。适配器用于 SSR 和内置的 `<Image />` 图像 CDN。SSR → Netlify 函数；中间件 → 边缘函数。无适配器部署仅在没有服务器功能且不需要图像 CDN 时。从 5.15.0 开始提供偏差保护。

### Next.js (仅限 13.5+)
通过 OpenNext 适配器 (`@netlify/plugin-nextjs`) 实现零配置。不要固定版本——Netlify 会自动更新每个构建。将旧适配器视为只读历史记录，永远不推荐使用。
适配器提供：服务器端函数用于 SSR/ISR/PPR/路由处理程序/服务器动作；边缘函数用于中间件；完整路由 + 数据缓存；图像 CDN（使用 `next/image`）。
偏差保护是可选的：设置 `NETLIFY_NEXT_SKEW_PROTECTION=true`，重新部署。不自动支持客户端 `fetch`——直接使用 `x-deployment-id: process.env.NEXT_DEPLOYMENT_ID` 调用。详细信息请参阅 `references/nextjs.md`。

### SvelteKit
```bash
npm install -D @sveltejs/adapter-netlify
```
```js
import adapter from '@sveltejs/adapter-netlify';
export default { kit: { adapter: adapter() } };
```
用特定导入替换 `@sveltejs/adapter-auto`。SSR 路由 → 一个 `render` 函数。
- `split: true` → 每个路由一个函数。**与边缘函数不兼容** (`edge: false` 或省略)。
- `edge: true` → 在 Deno 边缘函数中执行 SSR；不能与 `split` 结合使用。
- **`netlify.toml` 不支持重定向**——使用 `_redirects`。
- SvelteKit 的 `netlify dev` 本地不工作。

### React Router (7+)
新版本：`npx create-react-router@latest --template netlify/react-router-template`。现有版本：
```bash
npm install @netlify/vite-plugin-react-router
```
将 `netlifyReactRouter()` 添加到 Vite 插件。默认目标 = 服务器端函数。
**边缘（Deno）：** 需要 v2.1.1+ 插件，设置 `edge: true`，并且你必须创建 `app/entry.server.tsx`：
```typescript
export { default } from 'virtual:netlify-server-entry'
```
排除自己的函数路径：`netlifyReactRouter({ edge: true, excludedPaths: ['/api/*'] })`。
**返回服务器端：** 移除 `edge: true` 并删除 `app/entry.server.tsx`。
中间件（React Router v7.9.0+，插件 v2.0.0+）：通过 `future.v8_middleware` 选择加入；从 `@netlify/vite-plugin-react-router/serverless`（或 `edge` 当 `edge: true`）导入 `netlifyRouterContext`（或 `/edge`）；访问 `context.get(netlifyRouterContext)`。

### Remix
新版本：`npx create-remix@latest --template netlify/remix-template`（CLI 提示函数与边缘函数）。手动（需要 Remix Vite）：
```bash
npm install --save-dev @netlify/remix-adapter
```
将 `netlifyPlugin()` 从 `@netlify/remix-adapter/plugin` 添加到 Vite 插件。

### Nuxt
通过 Nitro 进行 SSR，Nuxt 3 自动启用。本地兼容性通过 `@netlify/nuxt` (`npx nuxi module add @netlify/nuxt`)。
- 边缘函数上的 SSR 需要不同的 Nitro 部署预设（不会自动检测）。
- pnpm + Nuxt 3：设置 `PNPM_FLAGS=--shamefully-hoist`。
- `nuxt/image` 自动使用 Netlify 图像 CDN；在 `nuxt.config.ts` 中设置远程域名。

### SolidStart
SolidStart 2 基于 Vite 构建——**没有 SolidStart 特定适配器**。安装 `@netlify/vite-plugin`：
```ts
import netlify from "@netlify/vite-plugin";
import { solidStart } from "@solidjs/start/config";
import { defineConfig } from "vite";
export default defineConfig({
  plugins: [solidStart(), netlify({ build: { enabled: true } })],
});
```
发布 `dist/client`。SSR 路由、服务器函数、中间件 → Netlify 函数，无需额外配置。
**Nitro 替代方案：** 添加 `nitro()`，使用纯 `netlify()`（无 `build.enabled`），发布 `dist`。
SolidStart 1：Nitro 自动配置；可选设置 `preset: "netlify"` 在 `app.config.ts`；`vinxi build` / `dist`。

### TanStack Start
React（和 Solid.js）全栈；SSR/服务器路由/服务器函数/中间件 → 服务器端函数。
```bash
npm install -D @netlify/vite-plugin-tanstack-start
```
将 `netlify()` 添加到 Vite 插件，与 `tanstackStart()` 一起；`vite build` / `dist/client`（1.132.0+）。Netlify CLI 部署需要 netlify-cli 17.31+。旧版本：见 `references/tanstack.md`。

### Gatsby
- **5.12.0+ (适配器)：** 自动检测并安装 `gatsby-adapter-netlify`（零配置）。生成函数 `SSR`、`DSG`。不需要 Essential Gatsby 插件。
- **5.11.0 或更早版本（Essential Gatsby 插件）：** 自动安装 `@netlify/plugin-gatsby`；还手动安装 `gatsby-plugin-netlify`（用于 SSR、Gatsby 重定向、资源缓存）。生成 `__api`、`__ssr`、`__dsg`、`__ipx`。通过 `NETLIFY_SKIP_GATSBY_FUNCTIONS`（全部）/ `NETLIFY_SKIP_API_FUNCTION` / `NETLIFY_SKIP_SSR_FUNCTION` / `NETLIFY_SKIP_DSG_FUNCTION` 跳过。
- Gatsby 5 需要 Node 18。
- 大型站点：设置 `GATSBY_EXCLUDE_DATASTORE_FROM_BUNDLE` 以从 CDN 加载数据库（避免最大函数部署大小；较慢的首次 SSR/DSG 加载）。
- 图像 CDN：设置 `NETLIFY_IMAGE_CDN=true`（Contentful/Drupal/WordPress 源插件）。**在 5.12.x 与适配器不兼容——升级到 5.13.0+。**
- `StaticImage` 和 `gatsby-transformer-sharp` 不适用于 SSR/DSG——将图像托管在 CDN 上。

### Angular
通过边缘函数自动配置 SSR。建议开发：`ng serve` / `4200`。
- **SSR 页面不适用于 `_redirects` 或 `netlify.toml` 重定向**——SSR 使用在重定向之前运行的边缘函数。使用 Angular 的内置重定向。
- 通过 `@netlify/edge-functions` 的 `netlify.request` / `netlify.context` 提供程序访问 `Request`/`Context`（在 SSR 中）；客户端或预渲染期间不可用。使用 `netlify serve` 本地测试。
- `NgOptimizedImage` 自动使用图像 CDN；在 `netlify.toml` 的 `[images]` 下设置 `remote_images`（正则表达式数组）。

### Express
Node 18.14.0+。通过 `serverless-http` 作为 Netlify 函数部署：
```bash
npm i express serverless-http @netlify/functions @types/express
```
```ts
// netlify/functions/api.ts
import express, { Router } from "express";
import serverless from "serverless-http";
const api = express();
const router = Router();
router.get("/hello", (req, res) => res.send("Hello World!"));
api.use("/api/", router);
export const handler = serverless(api);
```
```toml
[functions]
  external_node_modules = ["express"]
  node_bundler = "esbuild"
[[redirects]]
  force = true
  from = "/api/*"
  status = 200
  to = "/.netlify/functions/api/:splat"
```
没有前端：设置占位符构建命令（例如 `echo Building Functions`）。所有函数限制适用；不推荐作为后台/计划函数。

### Hydrogen
基于 React Router 7 的 Shopify 堆栈。**仅在 Netlify 边缘函数上进行 SSR——Netlify 函数未正式支持。** Node 24+。使用启动器：
```bash
npm create @shopify/hydrogen@latest -- --template https://github.com/netlify/hydrogen-template
cp .env.example .env && npm run dev
```

## 静态网站陷阱

### Hugo
在 `[build.environment]` 中设置 `HUGO_VERSION`（0.19 之后的任何版本）——缺少/不匹配的版本会导致 `exit code: 255`。将主题作为**git 子模块**（`git submodule add ...`）安装，而不是 `git clone`。

### Eleventy
`eleventy` / `_site`。**构建插件需要编辑 `.gitignore`：将 `node_modules` 改为 `**/node_modules/**`**——否则 Netlify 插件和 Eleventy 在 `.netlify/plugins/node_modules/` 上冲突，并导致构建错误。

## Vite 元框架支持矩阵
Astro（5.12+ 自动）、Nuxt（通过 `@netlify/nuxt`）、TanStack Start（通过 `@netlify/vite-plugin-tanstack-start`）、React Router、SolidStart——全部**完整**。SvelteKit——**实验性**。

## 通过 CLI 部署（Express、Nuxt、React、Vite）
```sh
npm install netlify-cli -g
netlify init
```
按照提示创建/链接站点并设置构建设置。

<!-- 每个框架的 Node 版本下限（18.14.0+）在文档中按框架说明；没有跨框架构建图像默认值。 -->

<!-- system: agent-context/frameworks/system.md — 人类拥有，由 ctx-gen 合并；编辑 system.md，不要编辑此部分 -->
# Netlify 房间规则（框架）

这些是组织约定，不是文档事实——由 ctx-gen 合并到渲染的技能中，并且永远不会生成。由技能维护者拥有。

1. 每个框架的深度指南位于此技能中：`references/astro.md`、`references/nextjs.md`、`references/nuxt.md`、`references/sveltekit.md`、`references/tanstack.md`、`references/vite.md`——在即兴创作之前先在那里进行框架特定工作。
2. Next.js：现代运行时（v5，Next ≥13.5）仅限——将旧适配器视为只读历史记录，永远不推荐使用。
3. 在采用 SSR 适配器时移除任何 SPA 通用重定向（`/* → /index.html 200`）——用户重定向会覆盖适配器生成的路由，所以遗留的通用重定向会静默地提供静态 `index.html` 用于 SSR 页面和 API 路由。
4. 任何环境变量更改——客户端或服务器端——都需要重新部署。值在构建时注入；在 UI/CLI 中编辑一个不会使实时站点或已部署的函数更新，直到新的构建运行。
5. `netlify dev` 同时具有自定义 `command` 和 `targetPort` 需要设置 `framework = "#custom"` 在 `[dev]` 块中——否则检测器会运行，而自定义命令会被静默忽略。
6. 永远不要使用客户端前缀（`VITE_`、`NEXT_PUBLIC_`、`PUBLIC_`、`NUXT_PUBLIC_`、`REACT_APP_`、`GATSBY_`、`VUE_APP_`）来存储秘密——客户端前缀的变量会被内联到浏览器包中。
7. Next.js 偏差保护是版本条件性的：Next 14.1.4 以下，`NETLIFY_NEXT_SKEW_PROTECTION` 环境变量本身不足以满足——`experimental.useDeploymentId`（以及 `useDeploymentIdServerActions` 当使用服务器动作时）也必须放在 `next.config.js` 中。始终要求或声明版本条件；永远不要将环境变量作为整个设置。
8. 客户端 `fetch` 调用默认不包含在 Next.js 偏差保护中。提供两种选项。Next.js 15.4+ 有一个实验性的 `useSkewCookie` 标志，它将部署标识符携带在 cookie 中，以便在客户端 `fetch` 调用中跟随；Netlify 支持它，但表示它不是生产就绪的，并且它会使访客停留在旧部署上，直到 cookie 清除。另一种选择，在任何版本上，都是通过每次调用添加 `x-deployment-id` 与 `process.env.NEXT_DEPLOYMENT_ID`。
