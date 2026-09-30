---
name: hono
description: 在构建 Hono Web 应用程序时，或当用户询问 Hono API、路由、中间件、JSX、验证、测试或流式传输时使用。当代码从 'hono' 或 'hono/*' 导入，或用户提及 Hono 时触发。使用 Hono CLI 检查和测试应用程序。
---

# Hono 技能

构建 Hono Web 应用。此技能为 AI 提供内联 API 知识。使用 Hono CLI 检查和测试应用。

## 最新文档

有关此内联参考之外的详细信息，请从 https://hono.dev 获取最新文档。从 `https://hono.dev/llms.txt` 获取文档页面的索引，然后使用 `Accept: text/markdown` 头获取它作为 Markdown：

```bash
curl -H "Accept: text/markdown" https://hono.dev/docs/helpers/cookie
```

## Hono CLI

使用 [Hono CLI](https://github.com/honojs/cli) 检查和测试应用。在项目中安装它，然后让 CLI 自我解释：

<!-- 在 0.2 版本中 TODO：将 @hono/cli@next 改为 @hono/cli -->

```bash
npm install -D @hono/cli@next
npx hono agent-context
```

遵循输出。它解释了每个命令（`routes`、`request`、`batch`、`snapshot`、`benchmark`、`optimize`、`ssg`），JSON 输出契约以及工作流程。

注意：

- `hono request` 使用 `app.request()` 发送请求——无需服务器。不要直接在 CLI 参数中传递凭证；使用环境变量来存储敏感值。
- 对于 Cloudflare Workers 绑定（KV、D1、R2 等），使用 `hono request /path --runtime workerd`。它使用项目的 wrangler 配置启动应用，因此本地绑定（`c.env`）是真实的。必须在项目中安装 wrangler。
- 对于多个请求，或一个保持状态（POST，然后使用返回的 ID）的流程，在一个 `hono batch -` 调用中运行它们。每行一个 JSON 对象；`save` 一个值并在后续步骤中将其用作 `{{id}}`。步骤共享一个应用实例。使用 `expect` 声明每个步骤的预期状态/正文（正文是深度部分匹配），并迭代直到摘要显示 `"failed": 0`：

  ```bash
  npx hono batch - <<'EOF'
  {"method":"POST","path":"/users","body":{"name":"Alice"},"save":{"id":".id"},"expect":{"status":201}}
  {"path":"/users/{{id}}","expect":{"status":200,"body":{"name":"Alice"}}}
  EOF
  ```

- 在更改现有路由之前，捕获当前行为：`npx hono snapshot` 以 batch JSONL 行打印它（真实响应成为 `expect`）。保留这些行，进行更改，然后使用 `npx hono batch -` 重新运行它们，直到 `"failed": 0`。
- 对于大型 API，使用 `npx hono snapshot --status-only` 和 `npx hono batch - --compact`——相同的循环，但输出更小。失败的步骤会携带 `diff`：修复它所命名的内容。

---

## Hono API 参考

### App 构造函数

```ts
import { Hono } from 'hono'

const app = new Hono()

// 使用 TypeScript 泛型
type Env = {
  Bindings: CloudflareBindings // 由 `npm run cf-typegen` 生成——参见“环境（Cloudflare Workers）”
  Variables: { user: User }
}
const app = new Hono<Env>()
```

### 路由方法

```ts
app.get('/path', handler)
app.post('/path', handler)
app.put('/path', handler)
app.delete('/path', handler)
app.patch('/path', handler)
app.options('/path', handler)
app.all('/path', handler) // 所有 HTTP 方法
app.on('PURGE', '/path', handler) // 自定义方法
app.on(['PUT', 'DELETE'], '/path', handler) // 多个方法
```

### 路由模式

```ts
// 路径参数
app.get('/user/:name', (c) => {
  const name = c.req.param('name')
  return c.json({ name })
})

// 多个参数
app.get('/posts/:id/comments/:commentId', (c) => {
  const { id, commentId } = c.req.param()
})

// 可选参数
app.get('/api/animal/:type?', (c) => c.text('Animal!'))

// 通配符
app.get('/wild/*/card', (c) => c.text('Wildcard'))

// 正则表达式约束
app.get('/post/:date{[0-9]+}/:title{[a-z]+}', (c) => {
  const { date, title } = c.req.param()
})

// 链式路由
app
  .get('/endpoint', (c) => c.text('GET'))
  .post((c) => c.text('POST'))
  .delete((c) => c.text('DELETE'))
```

### 路由分组

```ts
// 使用 route()
const api = new Hono()
api.get('/users', (c) => c.json([]))

const app = new Hono()
app.route('/api', api) // 映射到 /api/users

// 使用 basePath()
const app = new Hono().basePath('/api')
app.get('/users', (c) => c.json([])) // GET /api/users
```

### 错误处理

```ts
app.notFound((c) => c.json({ message: 'Not Found' }, 404))

app.onError((err, c) => {
  console.error(err)
  return c.json({ message: 'Internal Server Error' }, 500)
})
```

---

## Context (c)

### 响应方法

```ts
c.text('Hello') // text/plain
c.json({ message: 'Hello' }) // application/json
c.html('<h1>Hello</h1>') // text/html
c.redirect('/new-path') // 302 重定向
c.redirect('/new-path', 301) // 301 重定向
c.body('raw body', 200, headers) // 原始响应
c.notFound() // 404 响应
```

### Headers & Status

```ts
c.status(201)
c.header('X-Custom', 'value')
c.header('Cache-Control', 'no-store')
```

### 变量（请求范围数据）

```ts
// 在中间件中
c.set('user', { id: 1, name: 'Alice' })

// 在处理程序中
const user = c.get('user')
// 或
const user = c.var.user
```

### 环境（Cloudflare Workers）

绑定（KV、D1、R2、...）在 wrangler 配置中声明。生成它们的类型；不要手动编写 `Bindings` 类型，并且在 wrangler 配置的每次更改后重新运行。使用 `create-hono` 创建的项目有一个用于此的脚本：

```bash
npm run cf-typegen   # = wrangler types --env-interface CloudflareBindings
```

这将写入 `worker-configuration.d.ts`，它声明了 `CloudflareBindings` 以及 Workers 运行时类型。`@cloudflare/workers-types` 被 它取代：不要安装它。如果没有 `cf-typegen` 脚本，运行 `npx wrangler types` 并使用它声明的接口（`Env`，也作为 `Cloudflare.Env` 可用）。

```ts
const app = new Hono<{ Bindings: CloudflareBindings }>()

app.get('/', async (c) => {
  const value = await c.env.MY_KV.get('key')
  const db = c.env.MY_DB
  c.executionCtx.waitUntil(promise)
})
```

### 渲染器

```ts
app.use(async (c, next) => {
  c.setRenderer((content) =>
    c.html(
      <html><body>{content}</body></html>
    )
  )
  await next()
})

app.get('/', (c) => c.render(<h1>Hello</h1>))
```

---

## HonoRequest (c.req)

```ts
c.req.param('id') // 路径参数
c.req.param() // 所有路径参数作为对象
c.req.query('page') // 查询字符串参数
c.req.query() // 所有查询参数作为对象
c.req.queries('tags') // 多个值：?tags=A&tags=B → ['A', 'B']
c.req.header('Authorization') // 请求头
c.req.header() // 所有头（键为小写）

// 正文解析
await c.req.json() // 解析 JSON 正文
await c.req.text() // 解析文本正文
await c.req.formData() // 解析为 FormData
await c.req.parseBody() // 解析 multipart/form-data 或 urlencoded
await c.req.arrayBuffer() // 解析为 ArrayBuffer
await c.req.blob() // 解析为 Blob

// 验证数据（与验证中间件一起使用）
c.req.valid('json')
c.req.valid('query')
c.req.valid('form')
c.req.valid('param')

// 属性
c.req.url // 完整 URL 字符串
c.req.path // 路径名
c.req.method // HTTP 方法
c.req.raw // 底层 Request 对象
```

---

## 中间件

### 使用内置中间件

```ts
import { cors } from 'hono/cors'
import { logger } from 'hono/logger'
import { basicAuth } from 'hono/basic-auth'
import { prettyJSON } from 'hono/pretty-json'
import { secureHeaders } from 'hono/secure-headers'
import { etag } from 'hono/etag'
import { compress } from 'hono/compress'
import { poweredBy } from 'hono/powered-by'
import { timing } from 'hono/timing'
import { cache } from 'hono/cache'
import { bearerAuth } from 'hono/bearer-auth'
import { jwt } from 'hono/jwt'
import { jwk } from 'hono/jwk'
import { csrf } from 'hono/csrf'
import { ipRestriction } from 'hono/ip-restriction'
import { bodyLimit } from 'hono/body-limit'
import { timeout } from 'hono/timeout'
import { requestId } from 'hono/request-id'
import { methodOverride } from 'hono/method-override'
import { methodNotAllowed } from 'hono/method-not-allowed'
import { languageDetector } from 'hono/language'
import { some, every, except } from 'hono/combine'
import { contextStorage, getContext } from 'hono/context-storage'
import { trailingSlash, trimTrailingSlash } from 'hono/trailing-slash'

// 注册
app.use(logger()) // 所有路由
app.use('/api/*', cors()) // 特定路径
app.post('/api/*', basicAuth({ username: 'admin', password: 'secret' }))
```

### 自定义中间件

```ts
// 内联
app.use(async (c, next) => {
  const start = Date.now()
  await next()
  const elapsed = Date.now() - start
  c.res.headers.set('X-Response-Time', `${elapsed}ms`)
})

// 使用 createMiddleware 重用
import { createMiddleware } from 'hono/factory'

const auth = createMiddleware(async (c, next) => {
  const token = c.req.header('Authorization')
  if (!token) return c.json({ error: 'Unauthorized' }, 401)
  await next()
})

app.use('/api/*', auth)
```

### 中间件执行顺序

中间件按注册顺序执行。`await next()` 调用下一个中间件/处理程序，并且 `next()` 之后的代码在返回时运行：

```
请求 → mw1 before → mw2 before → 处理程序 → mw2 after → mw1 after → 响应
```

```ts
app.use(async (c, next) => {
  // 处理程序之前
  await next()
  // 处理程序之后
})
```

---

## 验证

验证目标：`json`、`form`、`query`、`header`、`param`、`cookie`。

### Zod 验证器

```ts
import { zValidator } from '@hono/zod-validator'
import { z } from 'zod'

const schema = z.object({
  title: z.string().min(1),
  body: z.string()
})

app.post('/posts', zValidator('json', schema), (c) => {
  const data = c.req.valid('json') // 完全类型化
  return c.json(data, 201)
})
```

### Valibot / 标准模式验证器

```ts
import { sValidator } from '@hono/standard-validator'
import * as v from 'valibot'

const schema = v.object({ name: v.string(), age: v.number() })

app.post('/users', sValidator('json', schema), (c) => {
  const data = c.req.valid('json')
  return c.json(data, 201)
})
```

---

## JSX

要使用它构建 UI（使用 `jsxRenderer` 的布局、Vite、客户端代码），请使用 `hono-jsx` 技能。本节仅涵盖语法。

### 设置

在 `tsconfig.json` 中：

```json
{
  "compilerOptions": {
    "jsx": "react-jsx",
    "jsxImportSource": "hono/jsx"
  }
}
```

或使用 pragma：`/** @jsxImportSource hono/jsx */`

**重要提示**：使用 JSX 的文件必须具有 `.tsx` 扩展名。将 `.ts` 重命名为 `.tsx`，否则编译器将失败。

### 组件

```tsx
import type { PropsWithChildren } from 'hono/jsx'

const Layout = (props: PropsWithChildren) => (
  <html>
    <head>
      <title>我的应用</title>
    </head>
    <body>{props.children}</body>
  </html>
)

const UserCard = ({ name }: { name: string }) => (
  <div class="card">
    <h2>{name}</h2>
  </div>
)

app.get('/', (c) => {
  return c.html(
    <Layout>
      <UserCard name="Alice" />
    </Layout>
  )
})
```

### jsxRenderer 中间件

使用 `jsxRenderer` 中间件进行布局。详细信息，请参阅 https://hono.dev/docs/middleware/builtin/jsx-renderer

### 异步组件

```tsx
const UserList = async () => {
  const users = await fetchUsers()
  return (
    <ul>
      {users.map((u) => (
        <li>{u.name}</li>
      ))}
    </ul>
  )
}
```

### 片段

```tsx
const Items = () => (
  <>
    <li>项目 1</li>
    <li>项目 2</li>
  </>
)
```

---

## 流式传输

```ts
import { stream, streamText, streamSSE } from 'hono/streaming'

// 基本流
app.get('/stream', (c) => {
  return stream(c, async (stream) => {
    stream.onAbort(() => console.log('Aborted'))
    await stream.write(new Uint8Array([0x48, 0x65]))
    await stream.pipe(readableStream)
  })
})

// 文本流
app.get('/stream-text', (c) => {
  return streamText(c, async (stream) => {
    await stream.writeln('Hello')
    await stream.sleep(1000)
    await stream.write('World')
  })
})

// 服务器发送事件
app.get('/sse', (c) => {
  return streamSSE(c, async (stream) => {
    let id = 0
    while (true) {
      await stream.writeSSE({
        data: JSON.stringify({ time: new Date().toISOString() }),
        event: 'time-update',
        id: String(id++)
      })
      await stream.sleep(1000)
    }
  })
})
```

---

## 使用 app.request() 进行测试

无需启动 HTTP 服务器即可测试端点：

```ts
// GET
const res = await app.request('/posts')
expect(res.status).toBe(200)
expect(await res.json()).toEqual({ posts: [] })

// POST with JSON
const res = await app.request('/posts', {
  method: 'POST',
  body: JSON.stringify({ title: 'Hello' }),
  headers: { 'Content-Type': 'application/json' }
})

// POST with FormData
const formData = new FormData()
formData.append('name', 'Alice')
const res = await app.request('/users', { method: 'POST', body: formData })

// 使用模拟环境（Cloudflare Workers 绑定）
const res = await app.request('/api/data', {}, { KV: mockKV, DATABASE: mockDB })

// 使用 Request 对象
const req = new Request('http://localhost/api', { method: 'DELETE' })
const res = await app.request(req)
```

---

## Hono Client (RPC)

使用服务器和客户端之间共享的类型进行类型安全的 API 客户端。

**重要提示**：路由必须链式化，以便类型推断才能工作。如果没有链式化，客户端无法推断路由类型。

```ts
// 服务器：路由必须链式化以保留类型
const route = app
  .post('/posts', zValidator('json', schema), (c) => {
    return c.json({ ok: true }, 201)
  })
  .get('/posts', (c) => {
    return c.json({ posts: [] })
  })
export type AppType = typeof route

// 客户端：使用 hc() 并导出类型
import { hc } from 'hono/client'
import type { AppType } from './server'

const client = hc<AppType>('http://localhost:8787/')
const res = await client.posts.$post({ json: { title: 'Hello' } })
const data = await res.json() // 完全类型化
```

类型工具：

```ts
import type { InferRequestType, InferResponseType } from 'hono/client'

type ReqType = InferRequestType<typeof client.posts.$post>
type ResType = InferResponseType<typeof client.posts.$post, 200>
```

---

## 辅助函数

辅助函数是从 `hono/<helper-name>` 导入的实用函数：

```ts
import { getConnInfo } from 'hono/conninfo'
import { getCookie, setCookie, deleteCookie } from 'hono/cookie'
import { css, Style } from 'hono/css'
import { createFactory } from 'hono/factory'
import { html, raw } from 'hono/html'
import { stream, streamText, streamSSE } from 'hono/streaming'
import { testClient } from 'hono/testing'
import { upgradeWebSocket } from 'hono/cloudflare-workers' // 或其他适配器
```

可用的辅助函数：Accepts、Adapter、ConnInfo、Cookie、css、Dev、Factory、html、JWT、Proxy、Route、SSG、Streaming、Testing、WebSocket。

详细信息，请参阅 `https://hono.dev/docs/helpers/<helper-name>`（使用 `Accept: text/markdown` 获取）。

### Factory

使用 `createFactory` 定义 `Env` 一次并在应用、中间件和处理器之间共享：

```ts
import { createFactory } from 'hono/factory'

const factory = createFactory<Env>()

// 创建应用（Env 类型被继承）
const app = factory.createApp()

// 创建中间件（Env 类型被继承，无需传递泛型）
const mw = factory.createMiddleware(async (c, next) => {
  await next()
})

// 分别创建处理程序（保留类型推断）
const handlers = factory.createHandlers(logger(), (c) => c.json({ message: 'Hello' }))
app.get('/api', ...handlers)
```

---

## 最佳实践

- 在路由定义中内联编写处理程序，以便正确推断路径参数的类型。
- 使用 `app.route()` 按功能组织大型应用，而不是 Rails 风格的控制器。
- 使用 `createFactory()` 在应用、中间件和处理器之间共享 Env 类型。
- 使用 `c.set()`/`c.get()` 在中间件和处理器之间传递数据。
- 链式多个请求部分的验证（param + query + json）。
- 导出应用类型用于 RPC：`export type AppType = typeof routes`
- 使用 `app.request()` 进行测试——无需启动服务器。

## 适配器

Hono 在多个运行时上运行。默认导出适用于 Cloudflare Workers、Deno 和 Bun。对于 Node.js，使用 Node 适配器：

```ts
// Cloudflare Workers / Deno / Bun
export default app

// Node.js
import { serve } from '@hono/node-server'
serve(app)
```
