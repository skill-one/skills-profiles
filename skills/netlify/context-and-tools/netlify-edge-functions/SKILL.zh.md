---
name: netlify-edge-functions
description: 编写和配置 Netlify Edge Functions —— 在网络边缘运行的 Deno 运行时的 TypeScript/JavaScript 处理程序。用于添加身份验证中间件或身份验证重定向、地理位置或本地化逻辑、A/B 测试或个性化、请求/响应转换（重写/重定向）或 Netlify 网站的边缘服务器端渲染。触发于“添加边缘函数”、“边缘身份验证检查”、“按国家重定向访客”、“使用 Cookie 进行 A/B 测试”、“重写请求”、“按地理位置进行个性化”或“缓存边缘响应”等任务。涵盖配置导出、路径路由、上下文对象、响应缓存、环境变量以及边缘与服务器端无状态函数的选择。首先检查框架的适配器——只有当框架尚未生成边缘函数时，才手动编写边缘函数。
---

# Netlify Edge Functions

## 现代语法（推荐使用）

导出一个默认处理器以及 `config` 对象。从 `@netlify/edge-functions` 中导入 `Config`/`Context` 类型；`Request`/`Response`/`URL` 是全局的。

```ts
import type { Config, Context } from "@netlify/edge-functions";

export default async (request: Request, context: Context) => {
  return new Response("Hello world");
};

export const config: Config = {
  path: "/test",
};
```

**当你的框架的适配器已经为该任务生成中间件时，不要手动编写边缘函数** — 重复会导致冲突。请先检查框架适配器/参考。

**边缘 vs 无服务器：** 使用边缘函数进行低延迟的请求/响应操作、地理位置逻辑、身份验证检查/重定向和 A/B 个性化。使用无服务器函数进行长时间运行的工作（最长 15 分钟）、重型 Node.js 依赖项、数据库密集型操作、后台/计划任务或内存超过 512 MB。

## 文件位置

- 默认目录：`YOUR_BASE_DIRECTORY/netlify/edge-functions`。自定义：在 `netlify.toml` 中的 `[build]` 下 `edge_functions`（相对于基本目录的路径）。
- 将目录**保持在发布目录之外**，以便源文件不会被部署。
- 扩展名：`.js`、`.ts`、`.jsx`、`.tsx`（`.jsx`/`.tsx` 对于 SSR 很有用）。
- 同名冲突：如果 `my-function.ts` 和 `my-function.js` 都存在，则**TypeScript 文件会被忽略**，部署 JavaScript 文件。

## 路由 — 必须配置，否则函数将静默不运行

⚠️ **没有路由的边缘函数（没有导出 `config` 且没有在 `netlify.toml` 中声明）仍然会部署，但会静默不运行 — 没有构建错误，没有警告。** 当“我的边缘函数什么都没做”时，请先检查路由。

⚠️ **狭义地限定 `path`。** `path: "/*"` 会拦截所有请求，包括静态资源，为每个请求增加延迟并计费边缘调用。

边缘函数**不**自动分配 URL 路由。通过内联 `config` 或 `netlify.toml` 进行配置。

`path` 是一个 `URLPattern` 表达式，必须以 `/` 开头，可以是单个字符串或数组：

```ts
export const config: Config = {
  path: ["/", "/products/*"],
  excludedPath: ["/*.css", "/*.js"],
};
```

Config 属性：`path`、`excludedPath`、`pattern`（`path` 的正则表达式替代）、`excludedPattern`、`method`、`header`、`onError`、`cache`。

### netlify.toml 声明

使用 `[[edge_functions]]` 在一个路径上声明多个函数并控制顺序：

```toml
[[edge_functions]]
  path = "/admin"
  function = "auth"

[[edge_functions]]
  path = "/admin"
  function = "injector"
  cache = "manual"

[[edge_functions]]
  pattern = "/products/(.*)"
  excludedPattern = "/products/things/(.*)"
  function = "highlight"
```

属性：`function`、`path`、`excludedPath`、`pattern`、`excludedPattern`、`header`、`cache`。

**合并优先级：** 如果同一个函数在内联和 `netlify.toml` 中都声明了，配置会合并并被视为内联；内联会覆盖重复的字段。

### 通过请求头匹配

`header` 键是 HTTP 头名称（不区分大小写）；值是 `true`（存在）、`false`（不存在）或值上的字符串正则表达式。多个同名值会针对逗号连接的列表进行匹配。

```ts
export const config: Config = {
  header: { "x-required": true, "x-forbidden": false, "user-agent": "(iPhone|Android)" },
  path: "/*",
};
```

### 声明处理顺序

Netlify 会**两次**运行整个声明顺序：第一次只运行未配置缓存的边缘函数；第二次运行配置了缓存的边缘函数。在这个顺序中：

1. 框架生成的在配置文件中声明的函数。
2. 你的 `netlify.toml` 声明（自上而下顺序）。
3. 框架/集成生成的具有内联配置的函数。
4. 你的内联声明（**按函数文件名字母顺序**）。

要在多个路径上的函数之间控制顺序，请优先使用 `netlify.toml` 声明而不是内联。

所有函数运行后，Netlify 会评估重定向规则 — 除非某个函数返回了响应并结束了链。要自定义顺序，请使用 `netlify.toml`。

**顺序注意事项：**
- 返回的响应会结束链；该路径的重定向不会发生。
- 静态重写目标上的边缘函数**不会**为重写的请求执行。
- `fetch()` 用于内部请求或返回 `URL` 会启动**新的请求链**并重新运行匹配的边缘函数。使用 `context.next()` 来避免重新运行它们。

## 函数签名和返回值

处理器接收 `(request: Request, context: Context)`。返回以下之一：
- 一个 `Response` — 传递给客户端；**结束请求链**（该路径声明的重定向不会运行）。
- 一个 `URL` — 重定向到**同站** URL 并带有 200 状态；地址栏不变。仅同站 — 对于其他站点使用 `fetch`。
- `undefined` / 空的 `return;` — 跳过此函数，继续链。

作为中间件修改响应，通过等待 `context.next()`：

```ts
import type { Context } from "@netlify/edge-functions";

export default async (request: Request, context: Context) => {
  const url = new URL(request.url);
  if (url.searchParams.get("method") !== "transform") return;

  const response = await context.next();
  const text = await response.text();
  return new Response(text.toUpperCase(), response);
};
```

Netlify **不会**向边缘函数请求添加头 — 使用 `context` 获取客户端请求信息。

## 常见模式

**按地理位置和 Cookie 重定向：**
```ts
export default async (req: Request, { cookies, geo }: Context) => {
  if (geo.city === "Paris" && cookies.get("promo-code") === "15-for-followers") {
    return Response.redirect(new URL("/subscriber-sale", req.url));
  }
};
```

**重定向（同站，200）：**
```ts
export default async (request: Request, { geo }: Context) => {
  if (geo.city === "Paris") return new URL("/subscriber-sale", request.url);
};
```

**读取请求体然后继续** — 请求体只能读取一次，所以传递一个新的 `Request` 并带有未读取的请求体：
```ts
export default async (req: Request, context: Context) => {
  const body = await req.json();
  if (!isValid(body.access_token)) return new Response("forbidden", { status: 403 });
  return context.next(new Request(req, { body: JSON.stringify(body) }));
};
```

**条件请求：**
```ts
export default async (req: Request, { next }: Context) => {
  const res = await next({ sendConditionalRequest: true });
  if (res.status === 304) return res;
  const text = await res.text();
  return new Response(text.toUpperCase(), res);
};
```

**React SSR（`.tsx`）：**
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

## Context 对象

- **`geo`** — `city`、`country.{code,name}`、`subdivision.{code,name}`、`latitude`、`longitude`、`timezone`、`postalCode`。
- **`cookies`** — `get(name)`、`set(options)`（CookieStore.set 格式）、`delete(name|options)`。跨子域 Cookie 需要自定义域名 — 在 `netlify.app` 上不可能（公共后缀列表）。
- **`next(options?)`** / **`next(request, options?)`** — 调用链中的下一个项目；返回一个你可以修改的 `Promise<Response>`。`options.sendConditionalRequest: true` 用于条件请求。只有当你需要响应体时才调用 `next`。当你读取了请求体时传递一个明确的 `Request`。
- **`params`** — 路径参数，例如路径 `/pets/:name` + 请求 `/pets/winter` → `{name:"winter"}`。查询字符串：使用 `request.url`。
- **`ip`** — 客户端 IP 字符串。
- **`requestId`** — Netlify 请求 ID。
- **`account.id`**、**`site.{id,name,url}`**、**`server.region`**、**`deploy.{context,id,published,skewProtectionToken}`**。
- **`waitUntil(promise)`** — 延长执行以通过响应（分析、日志），而不会阻塞它。仍然受 CPU 限制。

**`Netlify` 全局：** `Netlify.context`（在处理器外为 null）、`Netlify.env.{get,has,set,delete,toObject}`。`Netlify.env.set`/`delete` 是**仅限于调用范围** — 它们不会持久化环境变量；使用 Netlify 环境变量 API 端点嵌入它们的值。

## 响应缓存

⚠️ **缓存需要同时选择加入和设置头 — 要么都做，要么都不做。** 在返回的 `Response` 上设置 `Cache-Control` 而没有 `cache: "manual"` 在配置中，反之亦然。默认（两者都缺失）：每个请求都会调用函数。

1. 选择加入：`cache: "manual"`（内联或 `netlify.toml`）。
2. 在函数代码中**内联**设置头（不在 `netlify.toml` 中）：

```ts
import type { Context, Config } from "@netlify/edge-functions";

export default async (req: Request, context: Context) => {
  return new Response("Hello world", {
    headers: { "cache-control": "public, s-maxage=3600" },
  });
};

export const config: Config = { cache: "manual", path: "/hello" };
```

支持的缓存头：`Cache-Control`、`CDN-Cache-Control`、`Netlify-CDN-Cache-Control`、`Expires`（被 `max-age`/`s-maxage` 覆盖）、`Vary`、`Netlify-Vary`。请参阅 https://docs.netlify.com/build/caching/caching-overview

**原子部署会使缓存失效：** `s-maxage`/`max-age`/`Expires` 会在同一部署上下文中的新部署中被丢弃，即使在生命周期中也是如此。

**何时缓存：** 端点响应可跨客户端重用（例如相同的 SSR HTML）。**不要缓存**中间件、路由/转换逻辑或按客户端个性化。

⚠️ **缓存函数始终会覆盖静态文件。** 在 `/*` 上的缓存函数会为 `/cat.png` 提供服务，而不是静态 `cat.png`。

## 错误处理（`onError`，仅内联）

- **`fail`**（默认）— 提供一个通用错误页面。
- **`/YOUR_CUSTOM_PATH`** — 重定向到同站路径（必须以 `/` 开头）；不会为该路径调用边缘函数来提供服务。
- **`bypass`** — 跳过出错的函数，继续链。

```ts
export const config: Config = { path: "/hello", onError: "/unavailable" };
```

关键逻辑（如身份验证）的**失败关闭**；`bypass`（失败开放）用于渐进式增强（如不错的本地化）。

## 环境变量

- 通过 UI/CLI/API 设置；范围**必须包括 Functions** 才能到达边缘运行时。
- `netlify.toml` 中的**环境变量对边缘函数不可用**。
- **构建范围变量在边缘运行时不可用** — 仅在构建步骤中使用。如果需要，在构建时嵌入它们的值。
- 修改需要**新的构建和部署**；每个部署在部署时间冻结值。
- 在运行时使用 `Netlify.env.get(key)` / `Netlify.env.toObject()` 访问。

```ts
export default async (request: Request, context: Context) => {
  const value = Netlify.env.get("MY_IMPORTANT_VARIABLE");
  return new Response(`Value: ${value}`);
};
```

Next.js 中间件注意：在 Next.js 上使用 Netlify Edge Functions for Middleware，`process.env` 也有效。

## 运行时和模块

基于 Deno。通过以下方式导入模块：
- **Node 内置模块：** `import { randomBytes } from "node:crypto";`
- **Deno/URL 导入：** `import React from "https://esm.sh/react";`
- **npm 包（beta）：** `npm install` 然后按名称导入。⚠️ Beta — 使用原生二进制（Prisma）或运行时动态导入（cowsay）的包可能会失败。

**导入映射**（模块名而不是 URL）— 使用一个单独的导入映射文件，在 `netlify.toml` 中声明：

```toml
[functions]
  deno_import_map = "./path/to/your/import_map.json"
```

支持的 Web API 包括 `fetch`/`Request`/`Response`/`URL`/`File`/`Blob`、`console`、`atob`/`btoa`、`TextEncoder`/`TextDecoder`（以及流变体）、Web Crypto（`randomUUID`、`getRandomValues`、`SubtleCrypto`）、WebSocket、计时器、Streams API、URLPattern、`Performance`。

## 本地开发和部署

```bash
npm install netlify-cli -g
netlify dev        # 在本地请求上运行边缘函数
# 访问 http://localhost:8888/test
```

- 调试：`netlify dev` 使用 `--edge-inspect` 或 `--edge-inspect-brk`（请参阅 https://cli.netlify.com/commands/dev/）。
- 地理位置模拟：`--geo=mock`（旧金山）或 `--geo=mock --country=XX`。
- ⚠️ **本地没有缓存** — 在本地测试中会忽略缓存头。
- 手动部署需要 **Netlify CLI 12.2.8+**（旧版本会报错）。
- 部署是**原子**的 — 旧的部署会保持旧行为，直到你发布一个新的生产部署。

**监控：** 生产日志在 Netlify UI **Cloud compute > Edge functions**。每个 `console.*` 日志都包括生成函数的名称。保留时间 ≥ 24 小时（某些计划为 7 天）。企业版上的日志排放口。

## 限制和功能差距

- **代码大小：** 20 MB 压缩（捆绑最大）。
- **内存：** 每组部署的边缘函数 512 MB。
- **CPU 时间：** 每个请求 50 ms（不包括等待时间；`waitUntil` 工作仍然计算在内）。
- **响应头超时：** 40 秒。
- 缓存的响应**不计入**调用次数。
- **分割测试**启用 → 边缘函数**不**运行。
- **自定义头**（包括基本身份验证）**不**适用于边缘函数。
- **预渲染**不适用于边缘服务的路径。
- 重定向**仅限于同站** — 对于其他/外部站点使用 `fetch`。
- 多个框架插件生成的边缘函数可能会冲突。
- **不**支持在 HIPAA 合规托管下使用。

请参阅概述 https://docs.netlify.com/build/edge-functions/overview.md 和完整示例库 https://edge-functions-examples.netlify.app/

<!-- system: agent-context/edge-functions/system.md — human-owned, merged by ctx-gen; edit system.md, not this section -->
# Netlify house rules (edge-functions)

这些是组织约定和实地学到的护栏，不是文档事实 — 它们被合并到渲染的技能中并由 ctx-gen 合并，并且永远不会生成。
从先前手写的 netlify-edge-functions 技能中提取；由技能维护者拥有。

1. 首先检查框架的适配器/参考：自定义边缘函数重复适配器生成的中间件会导致冲突。只有在框架没有为该任务生成中间件时，才手动编写边缘函数。
2. 狭义地限定 `path`。`path: "/*"` 会拦截所有请求 — 包括静态资源 — 为每个请求增加延迟并计费边缘调用。
3. 没有路由的边缘函数（没有导出 `config`，没有 `netlify.toml` 声明）仍然会部署，但会静默不运行：没有构建错误，没有警告。当“我的边缘函数什么都没做”时，请先检查路由。
4. 根据工作负载形状选择边缘 vs 无服务器：边缘函数用于低延迟的请求/响应操作、地理位置逻辑、身份验证检查/重定向和 A/B 个性化；无服务器函数用于长时间运行的工作（最长 15 分钟）、重型 Node.js 依赖项、数据库密集型操作、后台/计划任务或内存需求超过 512 MB。
5. 边缘响应上的缓存头在没有 `cache: "manual"` 在配置中时无效 — 要么都做，要么都不做。在返回的 `Response` 上设置 `Cache-Control` 没有在函数中也选择加入则无效。
6. 在解释声明处理顺序时，说明两次循环，而不仅仅是顺序：Netlify 会两次运行整个声明顺序 — 第一次只运行未配置缓存的边缘函数，第二次运行配置了缓存的边缘函数。“非缓存先于缓存”而没有循环框架是不完整的答案。
