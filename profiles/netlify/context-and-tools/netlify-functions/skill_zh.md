# Netlify 函数

使用现代的默认处理器 API（`.mts` TypeScript）。导出一个默认的异步处理器，它接受一个 Web `Request` 和一个 Netlify `Context`，返回一个 Web `Response`。除非编写 Go 代码或迁移旧代码（见下文的“遗留”部分），否则请避免使用遗留的 AWS Lambda 处理器形状。

## 文件位置

- 默认目录：`netlify/functions/`（相对于基本目录）。将其**放在**发布目录或源文件之外，以将其作为静态资源发布。
- 一个函数是一个文件或一个子目录，其入口文件命名为 `index` 或与子目录名称匹配。所有这些都会创建一个名为 `hello` 的函数：
  - `netlify/functions/hello.mts`
  - `netlify/functions/hello/hello.mts`
  - `netlify/functions/hello/index.mts`
- 使用 `.mts`（TS）/ `.mjs`（JS）作为 ES 模块。`.cts`/`.cjs` 强制 CommonJS；`.ts`/`.js` 遵循最近的 `package.json` `"type"`。

## 最小函数

没有 `config` 导出。服务在 `/.netlify/functions/hello`。

```ts title="netlify/functions/hello.mts"
import type { Context } from "@netlify/functions"

export default async (req: Request, context: Context) => {
  return new Response("Hello, world!")
}
```

安装类型：`npm install @netlify/functions`（对于 TS 类型是必需的；对于 JS 是可选的）。

使用 `Netlify.env.get()` 读取环境变量和密钥：

```ts
const apiKey = Netlify.env.get("STRIPE_SECRET_KEY")
```

永远不要硬编码密钥。为了在运行时存在该变量，其作用域必须包括**函数**。在 `netlify.toml` 中设置的变量**不会**对函数可用。值在每个部署时都是冻结的——更改它们并重新部署以应用。

**响应头在代码中设置**在返回的 `Response` 上。`[[headers]]` 在 `netlify.toml` 中、`_headers` 和重定向头规则仅适用于静态 CDN 响应，不适用于函数响应。除非明确要求，否则不要添加 CORS 头。

## 自定义路径路由

设置 `config.path` 以路由到自定义 URL。设置后，该函数仅在指定路径上服务——不在 `/.netlify/functions/<name>` 上服务。

```ts title="netlify/functions/travel.mts"
import type { Config, Context } from "@netlify/functions"

export default async (req: Request, context: Context) => {
  const { city, country } = context.params
  return new Response(`You're visiting ${city} in ${country}!`)
}

export const config: Config = {
  path: "/travel-guide/:city/:country",
}
```

- 多个路径：`path: ["/cats", "/dogs"]`。
- 模式：`path` 支持的 [`URLPattern`](https://developer.mozilla.org/en-US/docs/Web/API/URL_Pattern_API) 语法——`path: ["/sale/*", "/item/:sku"]`。命名组会落在 `context.params` 上。对于查询字符串使用 `req.url`。
- `excludedPath`：提取例外，例如 `excludedPath: ["/product/*.css"]` 与 `path: "/product/*"`。
- `preferStatic: true`：让 URL 上的真实静态文件获胜。
- `method`：限制方法，例如 `method: ["GET", "POST"]`。

## 可获取的模块形状（替代方案）

等同于裸处理器；内联携带 `config` 并允许你添加事件处理器。

```ts
import type { NetlifyFunction } from "@netlify/functions"

export default {
  fetch: (req, context) => new Response("Hello, world!"),
  config: { path: "/hello" },
} satisfies NetlifyFunction
```

## 上下文对象

处理器的第二个参数（或从 `@netlify/functions` 在处理器作用域之外调用 `getContext()`——在请求之外会抛出异常；用 try/catch 包裹）。

- `context.params` — 命名路径参数。
- `context.geo` — `city`、`country.code/name`、`latitude`、`longitude`、`subdivision`、`timezone`、`postalCode`。
- `context.ip` — 客户端 IP 字符串。
- `context.cookies` — `get(name)` / `set(options)` / `delete(name|options)`。跨子域 Cookie 需要自定义域名（`netlify.app` 在 Public Suffix List 上）。
- `context.site` — `id`、`name`、`url`。`context.deploy` — `context`、`id`、`published`、`skewProtectionToken`。`context.account.id`。`context.server.region`。`context.requestId`。
- `context.waitUntil(promise)` — 在响应发送后运行工作（分析、日志）而不阻塞。计费/日志持续时间计算到 promise 解决为止。适用于 2025-03-20 及之后部署的函数。

⚠️ 在 `netlify dev` 下，`context.geo` 和 `context.ip` 是**模拟的**——占位符值，永远不会改变。不要因为本地值没有变化就得出地理位置编码损坏的结论。使用 `netlify dev --geo=mock --country=DE` 练习分支，并在实际部署上验证。

## 配置对象

导出 `const config`（或可获取模块的 `config` 属性）：

- `path` / `excludedPath` — `string | string[]`，必须以 `/` 开头。
- `method` — 一个方法或数组。
- `preferStatic` — `boolean`。
- `background` — `boolean`（见背景）。
- `schedule` — cron 字符串（见计划）。与 `path`/`excludedPath` 互斥。
- `rateLimit` — `{ action: 'rate_limit'|'rewrite', aggregateBy: 'domain'|'ip'|[...], to?, windowSize, windowLimit }`。
- `memory` / `vcpu` — 见下文；互斥。
- `region` — 机场代码；见下文。

## 集成

```ts title="netlify/functions/users.mts"
import type { Config } from "@netlify/functions"
import { getDatabase } from "@netlify/database"

const db = getDatabase()

export default async (req: Request) => {
  const users = await db.sql`SELECT id, email FROM users LIMIT 10`
  return Response.json({ users })
}

export const config: Config = { path: "/users" }
```

Blobs：`import { getStore } from "@netlify/blobs"`；`getStore("uploads").set(key, await req.blob())`。

`purgeCache()` 从 `@netlify/functions` 从函数内部使边缘缓存失效：

```ts
import { purgeCache } from "@netlify/functions"

export default async () => {
  await purgeCache({ tags: ["products"] }) // 省略 tags 以清除所有
  return new Response("Purged!", { status: 202 })
}
```

## 流式响应

将 `ReadableStream` 作为 `Response` 正文返回。限制：**60 秒执行时间，20 MB 响应**。

```ts
export default async (req: Request) => {
  const res = await fetch("https://api.openai.com/v1/chat/completions", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${Netlify.env.get("OPENAI_API_KEY")}`,
    },
    body: JSON.stringify({ model: "gpt-4o-mini", stream: true, messages: [/* ... */] }),
  })
  return new Response(res.body, { headers: { "content-type": "text/event-stream" } })
}
```

要手动构建流，`new ReadableStream({ start(controller) { controller.enqueue(...); controller.close() } })`。

## 背景函数（长时间运行）

`config.background: true`。客户端立即收到 `202`；返回值被丢弃；最多运行**15 分钟**。不进行流式传输。重试：在调用错误时，1 分钟后重试，然后 2 分钟后再重试。将结果发送到客户端以外的位置。

```ts title="netlify/functions/process.mts"
import type { Config } from "@netlify/functions"

export default async (req: Request) => {
  // 长时间运行的工作。客户端已经收到了它的 202。
}

export const config: Config = { background: true, path: "/process" }
```

限制：背景有效载荷**256 KB**。遗留 `-background` 文件名后缀仍然有效，但建议使用 `config.background`。

## 定时函数（cron）

`config.schedule` 使用 cron 表达式，在**UTC**时间执行。请求正文是 JSON，包含 `next_run`（ISO-8601）。仅限内联配置（TS/JS）——Go 必须使用 `netlify.toml`。

始终计算目标本地小时的 UTC 时间。例如，9 AM ET → `"0 13 * * *"` UTC（注意这会跨夏令时变化一小时；选择所需的 UTC 偏移量）。优先使用显式 cron 而不是 `@daily`/`@hourly` 简化，因为它们无法针对特定本地小时。

```ts title="netlify/functions/daily-digest.mts"
import type { Config } from "@netlify/functions"

export default async (req: Request) => {
  const { next_run } = await req.json()
  console.log("Next invocation at:", next_run)
}

export const config: Config = {
  schedule: "0 13 * * *", // 9 AM ET (EST); UTC
}
```

通过 `netlify.toml`（所有语言）：

```toml
[functions."daily-digest"]
  schedule = "0 13 * * *"
```

限制：**30 秒限制**（用于较长时间的工作，请使用背景）；仅在**已发布的部署**上触发（不适用于部署预览/分支部署——使用 **立即运行** 手动调用）；没有 URL 调用；没有流式传输；没有请求有效载荷/POST 数据；与分割测试不兼容。所有扩展都支持**除了** `@reboot` 和 `@annually`。

## 平台事件函数

导出一个默认对象，其中包含以事件命名的处理器。它们始终在后台运行——没有对客户端的响应。在同一个函数中与 `fetch` 结合使用。每个处理器都是完全类型化的；从 `@netlify/functions` 导入事件类型。

```ts title="netlify/functions/on-deploy.mts"
import type { DeploySucceededEvent, DeployFailedEvent } from "@netlify/functions"

export default {
  deploySucceeded(event: DeploySucceededEvent) {
    console.log(`Deploy ${event.deploy.id} succeeded for ${event.site.name}`)
  },
  deployFailed(event: DeployFailedEvent) {
    console.log(`Deploy ${event.deploy.id} failed: ${event.deploy.errorMessage}`)
  },
}
```

**部署事件**（`event.deploy`、`event.site`；返回 `void`）：`deployBuilding`、`deploySucceeded`、`deployFailed`、`deployDeleted`、`deployLocked`、`deployUnlocked`。

**身份事件**（`event.user`，仅保证 `id`）：

| 处理器 | 能否拒绝？ | 能否修改？ |
|---|---|---|
| `userValidate` | 是 | 是 |
| `userSignup` | 是 | 是 |
| `userLogin` | 是 | 是 |
| `userModified` | 是 | 是 |
| `userDeleted` | 否 | 否 |

- 拒绝：在处理器内部调用 `event.deny()` → 结束用户会收到 `401`。第一个拒绝的函数会中止链。
- 修改：返回 `{ user: {...} }` 以持久化更改；返回 `undefined` 以传递。

**表单事件**：`formSubmitted` → `event.data`（按字段名称键入的对象）。返回 `void`。

多个函数可以处理同一事件（所有都会运行）。Netlify 对每个事件进行签名（JWS）并在调用前验证，阻止外部请求。遗留文件名约定（文件名以事件命名，有效载荷通过 `await req.json()` → `payload`）仍然有效，但建议使用类型化处理器。

## 区域

⚠️ 除非用户说明有特定原因（共置数据库/后端、数据驻留、区域受众），否则**不要**覆盖 `config.region`。默认的 `cmh`（美国东部，俄亥俄州）是故意选择的。

当有理由时——例如，一个居住在欧盟的数据库：

```ts
export const config: Config = { path: "/eu-data", region: "dub" }
```

机场代码（自助服务）：`cmh`、`dub`、`fra`、`gru`、`iad`、`lhr`、`nrt`、`pdx`、`sfo`、`sin`、`syd`、`yul`。支持协助：`cdg`、`mxp`。每个函数都在恰好一个区域中运行（没有多区域地理位置路由）。区域选择需要 Pro/Enterprise。框架适配器生成的函数不能接受 `export const config`——在 UI 中在 **Cloud compute > Functions > Region** 下设置区域。更改区域后，**重新部署**。函数级别的区域优先于站点级别的 UI 设置。

## 内存 / vCPU

⚠️ **不要**推测性地设置 `config.memory` 或 `config.vcpu`——计费与大小线性扩展。仅在已知内存/计算密集型工作（AI 推理、图像/PDF、大型 JSON/CSV）或观察到函数自身工作引起的 OOM/超时时提高它们。

当有理由时（例如，观察到处理大型 PDF 时 OOM）：

```ts
export const config: Config = { path: "/heavy", memory: "2gb" } // 或 memory: 2048
```

- `memory`：1024–4096 MB。`vcpu`：0.5–2.0（0.5 → 1024 MB，2.0 → 4096 MB）。互斥；Netlify 会自动调整另一个。需要基于计费的 Pro/Enterprise。通过 `netlify.toml`：`[functions.heavy]\n  memory = "2gb"`。

## 打包与磁盘上的文件

⚠️ 在运行时从磁盘读取的文件（模板上的 `fs.readFile`、JSON、WASM）**不会**被打包：在 `netlify dev` 下工作，在生产中会返回 ENOENT。优先将静态数据作为模块导入。否则在 `netlify.toml` 中声明它：

```toml
[functions]
  included_files = ["files/*.md"]
  external_node_modules = ["package-1"]
```

⚠️ 所有函数的合并环境变量限制是 **~4 KB**（它们在 AWS Lambda 上运行）——没有 Netlify 设置可以提高它。将大型有效载荷（服务账户 JSON、PEM 密钥）保持在环境变量之外；使用打包文件、Blobs 或运行时获取。

JS-only esbuild：`[functions]\n  node_bundler = "esbuild"`。

## 限制（不可配置）

- 同步执行：**60 秒**。计划：**30 秒**。背景：**15 分钟**。
- 缓冲请求/响应有效载荷：**6 MB**（二进制是 Base64 编码，~30% 开销 → 有效 **4.5 MB** 二进制限制）。
- 流式响应：**20 MB**。背景有效载荷：**256 KB**。

## 本地测试与部署

- 大多数框架在其开发服务器中模拟函数。Vite 框架（Astro、Nuxt、TanStack Start、React Router）：安装 `@netlify/vite-plugin` 并运行开发服务器。Next.js 和其他任何东西：使用 [Netlify CLI](https://docs.netlify.com/api-and-cli-guides/cli-guides/local-development/) (`netlify dev`)。
- 定时函数在本地不会按计划触发——使用 `netlify functions:invoke <name>` 一次性触发。
- 部署：推送到 Git 以进行持续部署，或使用 Netlify CLI/API。
- 日志和指标位于 Netlify UI 中；使用 CLI 进行流式传输。所有已部署的函数版本都显示在 **Functions** 选项卡下；使用列表顶部的搜索字段按名称过滤函数，并使用单独的过滤器选择分支或输入部署预览编号。

## Node 运行时版本

运行时遵循构建的 Node.js 版本（后备：Node.js 24）。通过设置环境变量 `AWS_LAMBDA_JS_RUNTIME`（例如 `nodejs24.x`）通过 UI/CLI/API 覆盖（**不是** `netlify.toml`）——然后重新部署。ES 模块：`__dirname`/`__filename` 不可用，使用 `import.meta.url`；CommonJS 包的命名导入失败，使用默认导入。

## 遗留 / Go（除非需要避免）

Go 必须使用 [Lambda 兼容 API](https://docs.netlify.com/build/functions/lambda-compatibility/?fn-language=go)；Go 路由/区域/内存在 `netlify.toml` 中设置。对于迁移 Lambda 风格的 JS/TS，`@netlify/aws-lambda-compat` 包装一个 AWS 处理器：

```ts
import { withLambda } from "@netlify/aws-lambda-compat"
import type { HandlerContext, HandlerEvent, HandlerResponse } from "@netlify/aws-lambda-compat"

export default withLambda(async (event: HandlerEvent, context: HandlerContext): Promise<HandlerResponse> => {
  const name = event.queryStringParameters?.name ?? "World"
  return { statusCode: 200, headers: { "content-type": "application/json" }, body: JSON.stringify({ name }) }
})
```

Lambda 兼容模式强制执行 4 KB 环境变量限制；[升级到现代函数](https://developers.netlify.com/guides/migrating-to-the-modern-netlify-functions/) 以移除它。

<!-- system: agent-context/functions/system.md — human-owned, merged by ctx-gen; edit system.md, not this section -->
# Netlify 规则（函数）

这些是组织约定，不是文档事实——它们被合并到渲染的技能中，并且永远不会生成。从先前手写的 netlify-functions 技能中提取；由技能维护者拥有。

1. 尽可能使用 TypeScript（`.mts`）。
2. 通过 `Netlify.env.get()` 访问环境变量（优先于 `process.env` 以保持一致性）。
3. 除非明确要求，否则永远不要添加 CORS 头。
4. 将密钥存储在环境变量中，永远不要在代码中。
5. `context.geo` 和 `context.ip` 在 `netlify dev` 下是模拟的——占位符值，不是真实位置或客户端 IP。不要因为本地值没有变化就得出地理位置编码损坏的结论；使用 `netlify dev --geo=mock --country=DE` 练习分支，并在实际部署上验证。
6. **不要**推测性地设置 `config.memory` 或 `config.vcpu`。仅在已知内存/计算密集型工作或观察到函数自身工作引起的 OOM/超时时提高它们——计费与大小线性扩展。
7. **不要**覆盖 `config.region`，除非用户有特定原因（共置数据库/后端、数据驻留、区域受众）。`cmh` 默认是一个故意选择。
8. 在运行时从磁盘读取的文件（模板上的 `fs.readFile`、JSON、WASM）不会被打包：在 `netlify dev` 下工作，在生产中会返回 ENOENT。优先将静态数据作为模块导入；否则在 `netlify.toml` 中使用作用域 `included_files` 条目声明文件。
9. **~4 KB** 的合并环境变量限制适用于所有函数（它们在 AWS Lambda 上运行），而不仅仅是 Lambda 兼容模式。将大型有效载荷（服务账户 JSON、PEM 密钥）保持在环境变量之外——使用打包文件、Blobs 或运行时获取。没有 Netlify 设置可以提高此上限。
10. 正文中的第一个函数示例必须是最小的默认示例：没有任何 `config` 导出，说明函数服务在 `/.netlify/functions/<name>`。自定义 `path` 路由仅在稍后的示例中显示——代理模仿它们看到的第一个示例。
11. 永远不要在通用示例中演示 `memory`、`vcpu` 或 `region`——仅在明确说明的原因（观察到 OOM、共置后端、数据驻留）下显示它们。
12. 定时函数示例使用带有 UTC 转换的实时 cron 表达式（例如 9 AM ET → `"0 13 * * *"` UTC，注意夏令时）——永远不会只使用 `@hourly`/`@daily` 简化，因为它们无法针对特定本地小时。
13. 正文必须说明 `[[headers]]` 在 `netlify.toml` 中、`_headers` 和重定向头规则仅适用于静态 CDN 响应——函数的响应头在返回的 `Response` 上的代码中设置。
14. 当要求构建执行特定工作的函数（生成报告、处理上传、发送摘要）时，实现工作——在有需要时选择一个真实库并端到端编写操作。永远不要将核心任务作为未实现的占位符交付在完成的管道后面：一个核心分支抛出异常的函数不是工作的答案，无论其配置和路由多么完整。
15. `config.background: true` 是文档中记录的、当前支持的方式，以使函数成为背景（遗留的 `-background` 文件名后缀仍然有效）。如果本地安装的打包器不识别该标志，首先怀疑版本偏差：检查并升级本地工具，并将本地兼容性发现与平台支持声明分开——永远不要基于旧的安装模式从文档推荐的标志中删除答案。
