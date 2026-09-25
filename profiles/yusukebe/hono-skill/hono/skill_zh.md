# Hono 技能

构建 Hono Web 应用。此技能为 AI 提供内联 API 知识。使用 `npx hono request` 测试端点。如果配置了 `hono-docs` MCP 服务器，请优先使用其工具获取最新文档，而不是内联参考。

## Hono CLI 使用

### 请求测试

无需启动 HTTP 服务器即可测试端点。内部使用 `app.request()`。

```bash
# GET 请求
npx hono request [文件] -P /path

# 带有 JSON 体的 POST 请求
npx hono request [文件] -X POST -P /api/users -d '{"name": "test"}'
```

**注意**：不要直接在 CLI 参数中传递凭证。使用环境变量处理敏感值。`hono request` 不支持 Cloudflare Workers 绑定（KV、D1、R2 等）。如果需要绑定，请使用 `workers-fetch`：

```bash
npx workers-fetch /path
npx workers-fetch -X POST -H "Content-Type:application/json" -d '{"name":"test"}' /api/users
```

---

## Hono API 参考

### App 构造函数

```ts
import { Hono } from 'hono'

const app = new Hono()

// 使用 TypeScript 泛型
type Env = {
  Bindings: { DATABASE: D1Database; KV: KVNamespace }
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

```ts
const value = await c.env.KV.get('key')
const db = c.env.DATABASE
c.executionCtx.waitUntil(promise)
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
c.req.queries('tags') // 多个值: ?tags=A&tags=B → ['A', 'B']
c.req.header('Authorization') // 请求头
c.req.header() // 所有头（键为小写）

// 请求体解析
await c.req.json() // 解析 JSON 请求体
await c.req.text() // 解析文本请求体
await c.req.formData() // 解析为 FormData
await c.req.parseBody() // 解析 multipart/form-data 或 urlencoded
await c.req.arrayBuffer() // 解析为 ArrayBuffer
await c.req.blob() // 解析为 Blob

// 验证数据（与验证器中间件一起使用）
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
import { csrf } from 'hono/csrf'
import { ipRestriction } from 'hono/ip-restriction'
import { bodyLimit } from 'hono/body-limit'
import { requestId } from 'hono/request-id'
import { methodOverride } from 'hono/method-override'
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

// 可重用（使用 createMiddleware）
import { createMiddleware } from 'hono/factory'

const auth = createMiddleware(async (c, next) => {
  const token = c.req.header('Authorization')
  if (!token) return c.json({ error: 'Unauthorized' }, 401)
  await next()
})

app.use('/api/*', auth)
```

### 中间件执行顺序

中间件按注册顺序执行。`await next()` 调用下一个中间件/处理程序，`next()` 之后的代码在返回时执行：

```
请求 → mw1 之前 → mw2 之前 → 处理程序 → mw2 之后 → mw1 之后 → 响应
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

或使用 pragma: `/** @jsxImportSource hono/jsx */`

**重要**：使用 JSX 的文件必须具有 `.tsx` 扩展名。重命名 `.ts` 为 `.tsx`，否则编译器将失败。

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

使用 `jsxRenderer` 中间件进行布局。详情请参阅 `npx hono docs /docs/middleware/builtin/jsx-renderer`。

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

// POST 带有 JSON
const res = await app.request('/posts', {
  method: 'POST',
  body: JSON.stringify({ title: 'Hello' }),
  headers: { 'Content-Type': 'application/json' }
})

// POST 带有 FormData
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

使用服务器和客户端之间共享类型进行类型安全的 API 客户端。

**重要**：路由必须链式化，以便类型推断正常工作。如果不链式化，客户端无法推断路由类型。

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

## 辅助工具

辅助工具是导入自 `hono/<工具名称>` 的实用函数：

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

可用辅助工具：Accepts、Adapter、ConnInfo、Cookie、css、Dev、Factory、html、JWT、Proxy、Route、SSG、Streaming、Testing、WebSocket。

详情请使用 `npx hono docs /docs/helpers/<工具名称>`。

### Factory

使用 `createFactory` 定义 `Env` 一次，并在应用、中间件和处理器之间共享：

```ts
import { createFactory } from 'hono/factory'

const factory = createFactory<Env>()

// 创建应用（Env 类型继承）
const app = factory.createApp()

// 创建中间件（Env 类型继承，无需传递泛型）
const mw = factory.createMiddleware(async (c, next) => {
  await next()
})

// 分别创建处理器（保留类型推断）
const handlers = factory.createHandlers(logger(), (c) => c.json({ message: 'Hello' }))
app.get('/api', ...handlers)
```

---

## 最佳实践

- 在路由定义中内联编写处理程序，以便正确推断路径参数的类型。
- 使用 `app.route()` 按功能组织大型应用，而不是 Rails 风格的控制器。
- 使用 `createFactory()` 在应用、中间件和处理器之间共享 Env 类型。
- 使用 `c.set()`/`c.get()` 在中间件和处理器之间传递数据。
- 链式验证多个请求部分（param + query + json）。
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
