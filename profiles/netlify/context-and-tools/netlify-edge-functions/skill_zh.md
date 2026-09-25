# Netlify 边缘函数

**推荐使用（现代方式）：** 默认导出处理器 + 内联 `config` 导出，使用狭义范围的 `path`。从 `@netlify/edge-functions` 导入类型。

```ts
import type { Config, Context } from "@netlify/edge-functions";

export default async (request: Request, context: Context) => {
  // 返回 Response | URL (重写) | undefined (继续链)
};

export const config: Config = { path: "/products/*" };
```

**避免：** `deno.json` 中的导入映射（不受支持 — 使用 `deno_import_map` 指向单独文件）。不要手动编写你的框架适配器已经生成的函数（Next.js、Astro、Remix、SvelteKit、Nuxt 等） — 首先检查框架适配器/参考；重复适配器中间件会导致冲突。

## 文件位置

- 默认目录：`YOUR_BASE_DIRECTORY/netlify/edge-functions`。
- 自定义目录：`netlify.toml` 中 `[build]` 下 `edge_functions` 键。保持它**在发布目录之外**，以便源文件不会被部署。
- 支持 `.js`/`.ts`/`.jsx`/`.tsx`。如果 `.ts` 和 `.js` 文件同名，则忽略 `.ts`，部署 `.js`。

## ⚠️ 没有路由的函数将静默不运行

边缘函数**不会**自动分配 URL。没有 `config` 导出且没有 `netlify.toml` 声明 = 部署干净，无构建错误，无警告，永远不会执行。如果“我的边缘函数什么也不做”，请先检查路由。

## 请求处理模式

处理器接收 `(request: Request, context: Context)`。返回以下之一：
- `Response` — 直接响应（结束链；路径声明的重定向不运行）
- `URL` — 重写到 **同站** URL，状态码为 200（地址栏不变）
- `undefined` / 空的 `return;` — 跳过此函数，继续链

Netlify 不会为边缘请求添加任何头部 — 使用 `context` 获取客户端信息。

### 重定向

```ts
export default async (req: Request, { cookies, geo }: Context) => {
  if (geo.city === "Paris" && cookies.get("promo-code") === "15-for-followers") {
    return Response.redirect(new URL("/subscriber-sale", req.url));
  }
};
```

### 重写（仅限同站）

```ts
export default async (request: Request, { geo }: Context) => {
  if (geo.city === "Paris") return new URL("/subscriber-sale", request.url);
};
```

要访问其他站点或外部内容，请使用 `fetch()` — 通过 `URL` 重写仅限于同站。

### 中间件转换

```ts
import type { Context } from "@netlify/edge-functions";

export default async (request: Request, context: Context) => {
  const response = await context.next();
  const text = await response.text();
  return new Response(text.toUpperCase(), response);
};
```

`context.next()` 运行链的其余部分并返回原始 `Response`。除非需要响应体（否则会增加延迟），否则不要调用它。

要转换**不同**的路径，请使用 `fetch()` — 但这会启动一个**新的**请求链并重新运行匹配该路径的任何边缘函数。使用 `context.next()` 在相同内部路径上访问静态资源/服务器less函数，而不会重新运行边缘函数。

### 读取请求体

请求体只能读取一次。如果你读取了它，请将一个新请求传递给 `next()`：

```ts
export default async (req: Request, context: Context) => {
  const body = await req.json();
  if (!isValid(body.access_token)) return new Response("forbidden", { status: 403 });
  return context.next(new Request(req, { body: JSON.stringify(body) }));
};
```

### 条件请求

`next()` 通常强制完整响应。用于客户端缓存控制：

```ts
const res = await next({ sendConditionalRequest: true });
if (res.status === 304) return res;
```

## `Context` 对象

- **`geo`** — `city`、`country {code,name}`、`subdivision {code,name}`、`latitude`、`longitude`、`timezone`、`postalCode`。
- **`cookies`** — `get(name)`、`set(options)`、`delete(name|options)`（CookieStore Web 标准）。⚠️ 跨子域 Cookie 需要一个**自定义域名** — `netlify.app` 在 Public Suffix List 中。
- **`next(options?)` / `next(request, options?)`** — 继续链；`options.sendConditionalRequest`。
- **`params`** — 路径参数，例如 `/pets/:name` → `{ name: "winter" }`。查询字符串：使用 `request.url`。
- **`ip`**、**`requestId`**、**`server.region`**。
- **`site`** — `id`、`name`、`url`。**`account.id`**。**`deploy`** — `context`、`id`、`published`、`skewProtectionToken`。
- **`waitUntil(promise)`** — 在响应发送后运行工作（分析、日志），而不会阻塞它。仍然受 CPU 时间限制。

`Netlify.context` 在处理器内部提供相同的上下文（处理器外部为 `null`）。

## 环境变量

通过 `Netlify.env.get(name)` 访问（也支持 `has`、`set`、`delete`、`toObject`）。`set`/`delete` 仅在调用作用域内有效 — 它们**不会**持久化；使用 Netlify 环境API更新。

```ts
const value = Netlify.env.get("MY_IMPORTANT_VARIABLE");
```

⚠️ **注意点：**
- `netlify.toml` 中的变量**不**可用于边缘函数。
- 范围必须包括**函数**才能访问运行时。**构建**作用域的变量仅限构建 — 如果需要，请在构建时嵌入它们。
- 值在部署时冻结。更改变量 → 需要新部署。部署预览/分支部署使用其部署时的值。

## 配置 / 路由

通过内联 `config` 导出或 `netlify.toml` 进行配置。属性：
- **`path`** — `URLPattern` 字符串或数组；必须以 `/` 开头。例如 `["/", "/products/*"]`。
- **`excludedPath`** — 从 `path` 排除路由；必须以 `/` 开头。例如 `["/*.css", "/*.js"]`。
- **`pattern`** / **`excludedPattern`** — `path`/`excludedPath` 的正则表达式替代方案。
- **`method`** — 字符串或 HTTP 方法数组（仅限内联）。
- **`header`** — 头部条件的对象：`true`（存在）、`false`（不存在），或值上的正则表达式字符串。名称不区分大小写；多个同名值匹配为逗号分隔列表。
- **`cache`** — `"manual"` 以选择进入缓存。
- **`onError`** — 错误处理（见下文）。

### ⚠️ 狭义范围 `path`

`path: "/*"` 拦截**所有**请求，包括静态资源 — 为每个请求增加延迟并**为每个请求计费边缘调用**。仅匹配您需要的路径。

### netlify.toml（用于排序 / 同一路径上的多个函数）

```toml
[[edge_functions]]
  path = "/admin"
  function = "auth"

[[edge_functions]]
  path = "/admin"
  function = "injector"
  cache = "manual"
```

头部匹配使用 `[edge_functions.header]` 子表。

### 执行顺序

配置文件声明在内联之前运行；框架生成的在用户之前；非缓存的在缓存之前。在 `netlify.toml` 中：自上而下。在内联中：按**文件名字母顺序**。为了控制顺序，请优先使用 `netlify.toml`。如果同一个函数在内联和 toml 中都声明了，它们会合并，内联字段优先。

**两遍循环：** Netlify 运行整个声明顺序**两次** — 第一次遍历仅运行未配置缓存的边缘函数，第二次遍历运行配置了缓存的边缘函数。因此，缓存的函数始终在相同路径上的每个非缓存函数之后运行，无论声明位置如何 — 那就是为什么在两个非缓存函数之间声明的缓存函数仍然在它们之后运行。

注意事项：目标为静态重写的函数**不会**为重写请求运行。如果函数返回 `Response`，则该路径的重定向会被跳过。

## 响应缓存（选择进入）

### ⚠️ 两部分或都不
在 `Response` 上的缓存头在没有 `cache: "manual"` 在配置中 — 并且 `cache: "manual"` 没有头仍然不缓存。你需要**两者**：

```ts
import type { Config, Context } from "@netlify/edge-functions";

export default async (req: Request, context: Context) => {
  return new Response("Hello world", {
    headers: { "cache-control": "public, s-maxage=3600" },
  });
};

export const config: Config = { cache: "manual", path: "/hello" };
```

- 仅对跨客户端可重用的端点式响应使用缓存（例如共享 SSR HTML）。**永远**不要用于中间件、路由或客户端个性化。
- 缓存的响应**不**计入调用。
- ⚠️ 缓存的函数**会隐藏真实的静态文件**：`cache:"manual"` 在 `/*` 上会使 `/cat.png` 请求函数，而不是静态文件。
- 支持的头部：`Cache-Control`、`CDN-Cache-Control`、`Netlify-CDN-Cache-Control`、`Expires`、`Vary`、`Netlify-Vary`。头部必须在代码中内联设置。
- 同一上下文中的新部署会使 `s-maxage`/`max-age`/`Expires` 失效（原子部署）。
- 没有本地缓存 — 缓存头在 `netlify dev` 下被忽略。

## 错误处理（`onError`，仅内联）

- **`"fail"`**（默认）— 通用错误页面，停止链。
- **`"/custom-path"`** — 重写到同站路径（以 `/` 开头），无需调用该路径的边缘函数。
- **`"bypass"`** — 跳过出错的函数，继续链。

指导：关键逻辑（认证）**封闭**失败；渐进增强（本地化）**开放**失败（`bypass`）。

## 运行时 & 模块

Deno 运行时，包含许多标准 Web API（`fetch`/`Request`/`Response`/`URL`、`console`、`atob`/`btoa`、`TextEncoder`/`Decoder`(`Stream`)、Web Crypto `crypto.randomUUID/getRandomValues/subtle`、`WebSocket`、计时器、Streams API、`URLPattern`、`Performance`）。

- **Node 内建模块：** `import { randomBytes } from "node:crypto"`（`node:` 前缀）。
- **Deno 模块：** URL 导入，例如 `import React from "https://esm.sh/react"`。
- **npm 包（Beta）：** `npm install` 然后按名称导入。⚠️ 需要原生二进制文件（Prisma）或运行时动态导入（cowsay）的包可能会失败 — 优先使用 `node:` 内建模块 / Deno URL。
- **导入映射：** 仅单独文件（不是 `deno.json`），通过 `[functions]` 中的 `deno_import_map` 声明。

### 边缘上的 SSR (.tsx)

```tsx
import React from "https://esm.sh/react";
import { renderToReadableStream } from "https://esm.sh/react-dom/server";
import type { Config, Context } from "@netlify/edge-functions";

export default async function handler(req: Request, context: Context) {
  const stream = await renderToReadableStream(
    <html><body><h1>Hello {context.geo.country?.name}</h1></body></html>
  );
  return new Response(stream, { status: 200, headers: { "Content-Type": "text/html" } });
}

export const config: Config = { path: "/hello" };
```

## 边缘与服务器less

边缘用于低延迟请求/响应操作、地理位置、认证检查/重定向、A/B 个性化。服务器less用于长时间运行工作（长达 15 分钟）、重型 Node 依赖、数据库密集型操作、后台/计划任务，或内存需求超过 512 MB。

## 限制

- 代码大小：**20 MB** 压缩（打包）。
- 内存：**512 MB** 每个部署集。
- CPU 执行：**50 ms** 每个请求（不包括等待资源；`waitUntil` 工作仍然计入）。
- 响应头部超时：**40 s**。
- 每月调用次数因计划而异；缓存的响应不计入。

## 本地开发、部署、监控

```bash
npm install netlify-cli -g
netlify dev      # 在本地请求 :8888 上运行边缘函数
```
- 地理位置模拟：`--geo=mock`（旧金山）或 `--geo=mock --country=XX`。调试：`--edge-inspect` / `--edge-inspect-brk`。
- 手动部署需要 CLI **12.2.8+**（旧版本会报错）。部署是原子性的。
- 日志：**云计算 > 边缘函数** 在 UI 中；每个 `console` 日志命名发出函数。按名称/路径（glob）和时间筛选。保留时间 ≥24h（某些计划为 7 天）。

## 功能限制

- Split Testing 启用 → 边缘函数**不**运行。
- 自定义头部（包括基本认证头部）**不**适用于边缘函数。
- 预渲染**不**适用于由边缘函数服务的路径。
- 生成边缘函数的多个框架插件可能会冲突。
- 不属于 Netlify 的 HIPAA 合规方案的一部分。

<!-- system: agent-context/edge-functions/system.md — human-owned, merged by ctx-gen; edit system.md, not this section -->
# Netlify 规则（边缘函数）

这些是组织约定和实地学习到的护栏，不是文档事实 — 它们被合并到渲染的技能中，并且永远不会生成。
从之前的 `netlify-edge-functions` 技能中提取；由技能维护者拥有。

1. 首先检查框架的适配器/参考：自定义边缘函数如果重复适配器生成的中间件会导致冲突。仅在框架没有为该任务生成函数时才手动编写边缘函数。
2. 狭义范围 `path`。`path: "/*"` 拦截所有请求 — 包括静态资源 — 为每个请求增加延迟并计费边缘调用。
3. 没有路由的边缘函数仍然部署，但静默不运行：无构建错误，无警告。当“我的边缘函数什么也不做”时，请先检查路由。
4. 根据工作负载形状选择边缘与服务器less：边缘函数用于低延迟请求/响应操作、地理位置逻辑、认证检查/重定向和 A/B 个性化；服务器less函数用于长时间运行工作（长达 15 分钟）、重型 Node.js 依赖、数据库密集型操作、后台/计划任务，或内存需求超过 512 MB。
5. 边缘响应上的缓存头在没有 `cache: "manual"` 在配置中 — 两者或都不。在返回的 `Response` 上设置 `Cache-Control` 没有效果，除非函数也选择进入。
6. 解释声明处理顺序时，说明两遍循环，而不仅仅是排序：Netlify 运行整个声明顺序**两次** — 第一次遍历仅运行未配置缓存的边缘函数，第二次遍历运行配置了缓存的边缘函数。“非缓存之前缓存”没有循环框架是不完整的答案。
