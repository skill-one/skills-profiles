---
name: migrate-to-vinext
description: 将 Next.js 项目迁移至 vinext（基于 Vite 的 Next.js 重实现）。在要求迁移、转换或从 Next.js 切换至 vinext 时加载。处理兼容性扫描、包替换、Vite 配置生成、ESM 转换以及部署设置（原生 Cloudflare Workers，其他平台通过 Nitro）。
---

# 将 Next.js 迁移到 vinext

vinext 在 Vite 上重新实现了 Next.js 的 API 表面。现有的 `app/`、`pages/` 和 `next.config.js` 可以照常使用——迁移只是一个包替换、配置生成和 ESM 转换。无需修改应用程序代码。

## 首先：验证 Next.js 项目

确认 `next` 是否在 `package.json` 中的 `dependencies` 或 `devDependencies` 中。如果没有找到，停止——这项技能不适用。

从锁文件中检测包管理器：

| 锁文件                | 管理器 | 安装       | 卸载       |
| --------------------- | ------ | ---------- | ---------- |
| `pnpm-lock.yaml`      | pnpm   | `pnpm add`  | `pnpm remove` |
| `yarn.lock`           | yarn   | `yarn add`  | `yarn remove` |
| `bun.lockb` / `bun.lock` | bun    | `bun add`   | `bun remove`  |
| `package-lock.json` 或无 | npm    | `npm install` | `npm uninstall` |

检测路由器：如果根目录或 `src/` 下存在 `app/` 目录，则为 App Router。如果只有 `pages/` 目录存在，则为 Pages Router。两者可以共存。

## 快速参考

| 命令                          | 目的                                                         |
| ----------------------------- | ----------------------------------------------------------- |
| `vinext check`                | 扫描项目兼容性问题，生成评分报告                           |
| `vinext init`                 | 自动迁移——安装依赖、生成配置、转换为 ESM                 |
| `npx vite dev`                | 带热重载的开发服务器                                       |
| `npx vite build`              | 生产构建（App Router 的多环境）                           |
| `vinext start`                | 本地生产服务器                                               |
| `npx @vinext/cloudflare deploy` | 构建并部署到 Cloudflare Workers                           |
| `vp exec vinext-cloudflare deploy` | 使用 Vite+ 构建并部署到 Cloudflare Workers |

## 第一阶段：检查兼容性

运行 `vinext check`（如果需要，先通过 `npx vinext check` 安装 vinext）。查看评分报告。如果存在关键不兼容性，请在继续之前通知用户。

有关支持/不支持的功能和生态系统库状态的详细信息，请参阅 [references/compatibility.md](references/compatibility.md)。

## 第二阶段：自动迁移（推荐）

运行 `vinext init`。此命令：

1. 运行 `vinext check` 获取兼容性报告
2. 将 `vite` 作为 devDependency 安装（App Router 需要 `@vitejs/plugin-rsc`）
3. 在 `package.json` 中添加 `"type": "module"`
4. 将 CJS 配置文件重命名（例如，`postcss.config.js` → `.cjs`）以避免 ESM 冲突
5. 在 `package.json` 中添加 `dev:vinext` 和 `build:vinext` 脚本
6. 生成一个最小的 `vite.config.ts`
7. 将 `/dist/` 和 `.vinext/` 添加到 `.gitignore`

这是非破坏性的——现有的 Next.js 设置可以与 vinext 并存。使用 `dev:vinext` 脚本在完全切换之前进行测试。

如果 `vinext init` 成功，跳到第四阶段（验证）。如果失败或用户更喜欢手动控制，请继续到第三阶段。

## 第三阶段：手动迁移

当 `vinext init` 不起作用或用户希望完全控制时，使用此方法作为备用方案。

### 3a. 替换包

```bash
# 示例使用 npm:
npm uninstall next
npm install vinext
npm install -D vite
# 仅 App Router:
npm install -D @vitejs/plugin-rsc
```

### 3b. 更新脚本

替换 `package.json` 脚本中所有的 `next` 命令：

| 之前       | 之后        | 备注                      |
| ---------- | ----------- | ------------------------ |
| `next dev`  | `vite dev`  | 带热重载的开发服务器     |
| `next build` | `vite build` | 生产构建                 |
| `next start` | `vinext start` | 本地生产服务器            |
| `next lint`  | `vinext lint` | 委托给 eslint/oxlint     |

保留 Vite 兼容标志：`next dev --port 3001` → `vite dev --port 3001`。将 Next.js 专属构建标志转换为 `vite.config.ts` 中的 `vinext()` 选项，而不是转发给 Vite。

### 3c. 转换为 ESM

在 `package.json` 中添加 `"type": "module"`。重命名任何 CJS 配置文件：

- `postcss.config.js` → `postcss.config.cjs`
- `tailwind.config.js` → `tailwind.config.cjs`
- 任何使用 `module.exports` 的 `.js` 配置文件

### 3d. 生成 vite.config.ts

有关每个路由器和部署目标的配置变体，请参阅 [references/config-examples.md](references/config-examples.md)。

如果项目已经具有自定义 Vite 配置，编辑时优先使用 Vite 8 专属键：`oxc`、`optimizeDeps.rolldownOptions` 和 `build.rolldownOptions`。当前的 `esbuild` 和 `build.rollupOptions` 设置仍然有效，但迁移目标是它们。

**Pages Router（最小配置）：**

```ts
import vinext from "vinext";
import { defineConfig } from "vite";
export default defineConfig({ plugins: [vinext()] });
```

**App Router（最小配置）：**

```ts
import vinext from "vinext";
import { defineConfig } from "vite";
export default defineConfig({ plugins: [vinext()] });
```

vinext 在 App Router 中自动注册 `@vitejs/plugin-rsc`，除非 `rsc` 选项显式为 `false`。本地开发不需要手动 RSC 插件配置。

### 3e. 更新 .gitignore

确保忽略 vinext 生成的输出和缓存：

```gitignore
/dist/
.vinext/
```

## 第四阶段：部署（可选）

### 选项 A：Cloudflare Workers（推荐用于 Cloudflare）

如果用户希望部署到 Cloudflare Workers，请使用 `npx @vinext/cloudflare deploy`。使用 Vite+ 时，在运行本地安装的 bin 时使用 `vp exec vinext-cloudflare deploy`。它通过 wrangler 进行构建和部署。

对于手动设置或自定义 worker 条目，请参阅 [references/config-examples.md](references/config-examples.md)。

#### Cloudflare 绑定（D1、R2、KV、AI 等）

要访问 Cloudflare 绑定（D1、R2、KV、AI、队列、持久对象等），在服务器组件、路由处理程序或服务器动作中任何地方使用 `import { env } from "cloudflare:workers"`：

```tsx
import { env } from "cloudflare:workers";

export default async function Page() {
  const result = await env.DB.prepare("SELECT * FROM posts").all();
  return <div>{JSON.stringify(result)}</div>;
}
```

这之所以可行，是因为 `@cloudflare/vite-plugin` 在 workerd 中运行服务器环境，其中 `cloudflare:workers` 是一个原生模块。不需要自定义 worker 条目、`getPlatformProxy()` 或特殊配置。只需导入并使用即可。

绑定必须在 `wrangler.jsonc` 中定义。对于 TypeScript 类型，请运行 `wrangler types`。

**重要提示：** 不要使用 `getPlatformProxy()`、`getRequestContext()` 或自定义 worker 条目与 `fetch(request, env)` 来访问绑定。这些是旧模式。`cloudflare:workers` 是推荐方法，并且与 vinext 开箱即用。

### 选项 B：其他平台（通过 Nitro）

对于部署到 Vercel、Netlify、AWS、Deno Deploy 或任何其他 [Nitro 支持的平台](https://v3.nitro.build/deploy)，添加 Nitro Vite 插件：

```bash
npm install nitro
```

```ts
// vite.config.ts
import { defineConfig } from "vite";
import vinext from "vinext";
import { nitro } from "nitro/vite";

export default defineConfig({
  plugins: [vinext(), nitro()],
});
```

构建和部署：

```bash
NITRO_PRESET=vercel npx vite build    # Vercel
NITRO_PRESET=netlify npx vite build   # Netlify
NITRO_PRESET=deno_deploy npx vite build  # Deno Deploy
NITRO_PRESET=node npx vite build      # Node.js 服务器
```

Nitro 在大多数 CI/CD 环境中自动检测平台，因此预设通常是不必要的。

**注意：** 对于 Cloudflare Workers，Nitro 可以工作，但原生集成（`npx @vinext/cloudflare deploy` / `vp exec vinext-cloudflare deploy` / `@cloudflare/vite-plugin`）是推荐的，因为它提供了与 `cloudflare:workers` 绑定、KV 缓存和一键部署的最佳开发者体验。Nitro 对于 Cloudflare 是可行的，但原生设置是推荐的。

## 第五阶段：验证

1. 运行生成的 `dev:vinext` 脚本（或 `npx vite dev`）启动开发服务器
2. 确认服务器无错误启动
3. 导航关键路由并检查功能
4. 将结果报告给用户——如果出现错误，请共享完整输出

有关常见迁移错误的详细信息，请参阅 [references/troubleshooting.md](references/troubleshooting.md)。

## 已知限制

| 功能                       | 状态                                                                      |
| ----------------------------- | --------------------------------------------------------------------------- |
| `next/image` 优化         | 远程图像通过 @unpic；没有构建时优化                                        |
| `next/font/google`            | CDN 加载，不是自托管                                                   |
| 域名级 i18n                 | 不支持；路径前缀 i18n 工作                                             |
| `next/jest`                   | 不支持；使用 Vitest                                                   |
| Turbopack/webpack 配置      | 忽略；使用 Vite 插件代替                                               |
| `runtime` / `preferredRegion` | 位置忽略；边缘 App Router 页面在 `cacheComponents` 外跳过 ISR             |
| PPR（部分预渲染）    | 使用 `"use cache"` 指令代替（Next.js 16 方法）                           |

## 反模式

- **不要修改 `app/`、`pages/` 或应用程序代码。** vinext 对所有 `next/*` 导入进行 shimming——不需要导入重写。
- **不要在应用程序代码中重写 `next/*` 导入** 为 `vinext/*`。导入如 `next/image`、`next/link`、`next/server` 会自动解析。
- **不要将 webpack/Turbopack 配置** 复制到 Vite 配置中。使用 Vite 原生插件代替。
- **不要跳过兼容性检查。** 在迁移前运行 `vinext check` 以尽早暴露问题。
- **不要删除 `next.config.js`** 除非用 `next.config.ts` 或 `.mjs` 替换它。vinext 会读取它以进行重定向、重写、标题、basePath、i18n、图像和 env 配置。
- **不要使用 `getPlatformProxy()` 或自定义 worker 条目来访问绑定。** 使用 `import { env } from "cloudflare:workers"` 代替。这是现代模式，并且与 vinext 和 `@cloudflare/vite-plugin` 开箱即用。
- **对于 Cloudflare Workers，优先使用原生集成而不是 Nitro。** `npx @vinext/cloudflare deploy` / `vp exec vinext-cloudflare deploy` / `@cloudflare/vite-plugin` 提供了与 `cloudflare:workers` 绑定、KV 缓存和图像优化的最佳开发者体验。Nitro 对于 Cloudflare 是可行的，但原生设置是推荐的。
