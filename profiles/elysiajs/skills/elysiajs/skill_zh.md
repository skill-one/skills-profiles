# ElysiaJS 开发技能

始终参考 [elysiajs.com/llms.txt](https://elysiajs.com/llms.txt) 获取代码示例和最新 API。

## 概述

ElysiaJS 是一个 TypeScript 框架，用于构建 Bun 首选（但不限于 Bun）的类型安全、高性能后端服务器。此技能为使用 Elysia 开发提供全面指导，包括路由、验证、认证、插件、集成和部署。

## 何时使用此技能

当用户询问以下内容时触发此技能：
- 创建或修改 ElysiaJS 路由、处理程序或服务器
- 使用 TypeBox 或其他模式库（Zod、Valibot）设置验证
- 实现认证（JWT、基于会话、宏、守卫）
- 添加插件（CORS、OpenAPI、静态文件、JWT）
- 与外部服务集成（Drizzle ORM、Better Auth、Next.js、Eden Treaty）
- 设置 WebSocket 端点以实现实时功能
- 为 Elysia 实例创建单元测试
- 将 Elysia 服务器部署到生产环境

## 快速入门
快速脚手架：
```bash
bun create elysia app
```

### 基本服务器
```typescript
import { Elysia, t, status } from 'elysia'

const app = new Elysia()
  	.get('/', () => 'Hello World')
   	.post('/user', ({ body }) => body, {
    	body: t.Object({
      		name: t.String(),
        	age: t.Number()
     	})
    })
    .get('/id/:id', ({ params: { id } }) => {
   		if(id > 1_000_000) return status(404, 'Not Found')
     
     	return id
    }, {
    	params: t.Object({
     		id: t.Number({
       			minimum: 1
       	})
     	}),
     	response: {
      	200: t.Number(),
        	404: t.Literal('Not Found')
      	}
    })
    .listen(3000)
```

## 基本用法

### HTTP 方法
```typescript
import { Elysia } from 'elysia'

new Elysia()
  .get('/', 'GET')
  .post('/', 'POST')
  .put('/', 'PUT')
  .patch('/', 'PATCH')
  .delete('/', 'DELETE')
  .options('/', 'OPTIONS')
  .head('/', 'HEAD')
```

### 路径参数
```typescript
.get('/user/:id', ({ params: { id } }) => id)
.get('/post/:id/:slug', ({ params }) => params)
```

### 查询参数
```typescript
.get('/search', ({ query }) => query.q)
// GET /search?q=elysia → "elysia"
```

### 请求体
```typescript
.post('/user', ({ body }) => body)
```

### 头部
```typescript
.get('/', ({ headers }) => headers.authorization)
```

## TypeBox 验证

### 基本类型
```typescript
import { Elysia, t } from 'elysia'

.post('/user', ({ body }) => body, {
  body: t.Object({
    name: t.String(),
    age: t.Number(),
    email: t.String({ format: 'email' }),
    website: t.Optional(t.String({ format: 'uri' }))
  })
})
```

### 嵌套对象
```typescript
body: t.Object({
  user: t.Object({
    name: t.String(),
    address: t.Object({
      street: t.String(),
      city: t.String()
    })
  })
})
```

### 数组
```typescript
body: t.Object({
  tags: t.Array(t.String()),
  users: t.Array(t.Object({
    id: t.String(),
    name: t.String()
  }))
})
```

### 文件上传
```typescript
.post('/upload', ({ body }) => body.file, {
  body: t.Object({
    file: t.File({
      type: 'image',              // image/* MIME 类型
      maxSize: '5m'               // 5 兆字节
    }),
    files: t.Files({              // 多个文件
      type: ['image/png', 'image/jpeg']
    })
  })
})
```

### 响应验证
```typescript
.get('/user/:id', ({ params: { id } }) => ({
  id,
  name: 'John',
  email: 'john@example.com'
}), {
  params: t.Object({
    id: t.Number()
  }),
  response: {
    200: t.Object({
      id: t.Number(),
      name: t.String(),
      email: t.String()
    }),
    404: t.String()
  }
})
```

## 标准模式（Zod、Valibot、ArkType）

### Zod
```typescript
import { z } from 'zod'

.post('/user', ({ body }) => body, {
  body: z.object({
    name: z.string(),
    age: z.number().min(0),
    email: z.string().email()
  })
})
```

## 错误处理

```typescript
.get('/user/:id', ({ params: { id }, status }) => {
  const user = findUser(id)
  
  if (!user) {
    return status(404, 'User not found')
  }
  
  return user
})
```

## 守卫（适用于多个路由）

```typescript
.guard({
  params: t.Object({
    id: t.Number()
  })
}, app => app
  .get('/user/:id', ({ params: { id } }) => id)
  .delete('/user/:id', ({ params: { id } }) => id)
)
```

## 宏

```typescript
.macro({
  hi: (word: string) => ({
    beforeHandle() { console.log(word) }
  })
})
.get('/', () => 'hi', { hi: 'Elysia' })
```

### 项目结构（推荐）
Elysia 采取无意见的立场，但根据用户请求。如果没有特定偏好，我们推荐基于功能驱动和领域驱动的文件夹结构，每个功能都有自己的文件夹，包含控制器、服务和模型。

```
src/
├── index.ts              # 主服务器入口
├── modules/
│   ├── auth/
│   │   ├── index.ts      # 认证路由（Elysia 实例）
│   │   ├── service.ts    # 业务逻辑
│   │   └── model.ts      # TypeBox 模式/DTO
│   └── user/
│       ├── index.ts
│       ├── service.ts
│       └── model.ts
└── plugins/
    └── custom.ts

public/                   # 静态文件（如果使用静态插件）
test/                     # 单元测试
```

每个文件都有自己的职责，如下所示：
- **控制器（index.ts）**：处理 HTTP 路由、请求验证和 Cookie。
- **服务（service.ts）**：处理业务逻辑，如果可能，与 Elysia 控制器解耦。
- **模型（model.ts）**：定义请求和响应的数据结构和验证。

## 最佳实践
Elysia 对设计模式无意见，但如果未提供，我们可以依赖 MVC 模式，并配合基于功能的文件夹结构。

- 控制器：
	- 倾向于将 Elysia 作为依赖 HTTP 的控制器使用
	- 对于非 HTTP 依赖，除非明确要求，否则倾向于使用服务
	- 使用 `onError` 处理本地自定义错误
	- 通过 `Elysia.models({ ...models })` 将模型注册到 Elysia 实例，并使用命名空间前缀 `Elysia.prefix('model', 'Namespace.')`
	- 倾向于通过 Elysia 提供的名称引用模型，而不是使用实际的 `Model.name`
- 服务：
	- 倾向于使用类（如果可能，使用抽象类）
	- 倾向于使用从 `Model` 派生的接口/类型
	- 返回 `status`（`import { status } from 'elysia'`）以处理错误
	- 倾向于使用 `return Error` 而不是 `throw Error`
- 模型：
	- 始终导出验证模型和验证模型的类型
	- 自定义错误应包含在模型中

## Elysia 关键概念
在使用 Elysia 之前，需要理解以下重要概念和规则。

## 封装 - 默认隔离

生命周期（钩子、中间件）**不会**在实例之间泄漏，除非作用域化。

**作用域级别：**
- `local`（默认）- 当前实例 + 子实例
- `scoped` - 父实例 + 当前实例 + 子实例  
- `global` - 所有实例

```ts
.onBeforeHandle(() => {}) // 仅当前实例
.onBeforeHandle({ as: 'global' }, () => {}) // 导出到所有实例
```

## 方法链 - 对类型是必需的

**必须链式调用**。每个方法返回新的类型引用。

❌ 不要：
```ts
const app = new Elysia()
app.state('build', 1) // 丢失类型
app.get('/', ({ store }) => store.build) // build 不存在
```

✅ 要：
```ts
new Elysia()
  .state('build', 1)
  .get('/', ({ store }) => store.build)
```

## 显式依赖

每个实例独立。**声明你使用的依赖。**

```ts
const auth = new Elysia()
	.decorate('Auth', Auth)
	.model(Auth.models)

new Elysia()
  .get('/', ({ Auth }) => Auth.getProfile()) // Auth 不存在

new Elysia()
  .use(auth) // 必须声明
  .get('/', ({ Auth }) => Auth.getProfile())
```

**全局作用域当：**
- 没有添加类型（cors、helmet）
- 全局生命周期（日志记录、跟踪）

**显式当：**
- 添加类型（state、models）
- 业务逻辑（auth、db）

## 去重

插件除非命名，否则会重新执行：

```ts
new Elysia() // 在 `.use` 上重新运行
new Elysia({ name: 'ip' }) // 在所有实例中运行一次
```

## 顺序重要

事件应用于**注册后**的路由。

```ts
.onBeforeHandle(() => console.log('1'))
.get('/', () => 'hi') // 有钩子
.onBeforeHandle(() => console.log('2')) // 不影响 '/'
```

## 类型推断

**仅对内联函数**进行准确类型推断。

对于控制器，在内联包装器中解构：

```ts
.post('/', ({ body }) => Controller.greet(body), {
  body: t.Object({ name: t.String() })
})
```

从模式获取类型：
```ts
type MyType = typeof MyType.static
```

## 引用模型
模型可以通过名称引用，特别适合记录 API
```ts
new Elysia()
	.model({
		book: t.Object({
			name: t.String()
		})
	})
	.post('/', ({ body }) => body.name, {
		body: 'book'
	})
```

模型可以通过使用 `.prefix` / `.suffix` 重命名
```ts
new Elysia()
	.model({
		book: t.Object({
			name: t.String()
		})
	})
	.prefix('model', 'Namespace')
	.post('/', ({ body }) => body.name, {
		body: 'Namespace.Book'
	})
```

一旦 `prefix`，模型名称将默认大写。

## 技术术语
以下是用作 Elysia 的技术术语：
- `OpenAPI Type Gen` - `@elysiajs/openapi` 的 `fromTypes` 函数名，用于从类型生成 OpenAPI，参见 `plugins/openapi.md`
- `Eden`, `Eden Treaty` - 用于从后端到前端共享类型的端到端类型安全 RPC 客户端

## 资源
按需使用以下参考。

建议查看 `route.md`，因为它包含最重要的基础构建块和示例。

`plugin.md` 和 `validation.md` 也很重要，但可以根据需要查看。

### references/
按主题细分的详细文档：
- `bun-fullstack-dev-server.md` - 使用 HMR 的 Bun 全栈开发服务器。无打包器的 React。
- `cookie.md` - 关于 Cookie 的详细文档
- `deployment.md` - 生产部署指南 / Docker
- `eden.md` - 用于从后端到前端共享类型的端到端类型安全 RPC 客户端
- `guard.md` - 一次性设置验证/生命周期
- `macro.md` - 将多个模式/生命周期作为可重用的 Elysia 通过键值对组合（推荐用于复杂设置，例如认证、授权、基于角色的访问控制）
- `plugin.md` - 将 Elysia 的一部分解耦为独立组件
- `route.md` - Elysia 基础构建块：路由、处理程序和上下文
- `testing.md` - 带有示例的单元测试
- `validation.md` - 设置输入/输出验证和所有自定义验证规则的列表
- `websocket.md` - 用于实时通信的 WebSocket

### plugins/ 
官方 Elysia 插件的详细文档、用法和配置参考：
- `bearer.md` - 为 Elysia 添加 Bearer 功能（`@elysiajs/bearer`）
- `cors.md` - CORS 的开箱即用配置（`@elysiajs/cors`）
- `cron.md` - 使用 Elysia 上下文运行 cron 作业（`@elysiajs/cron`）
- `graphql-apollo.md` - 集成 GraphQL Apollo（`@elysiajs/graphql-apollo`）
- `graphql-yoga.md` - 与 GraphQL Yoga 集成（`@elysiajs/graphql-yoga`）
- `html.md` - HTML 和 JSX 插件设置和用法（`@elysiajs/html`）
- `jwt.md` - JWT / JWK 插件（`@elysiajs/jwt`）
- `openapi.md` - OpenAPI 文档和 OpenAPI Type Gen / 从类型生成 OpenAPI（`@elysiajs/openapi`）
- `opentelemetry.md` - OpenTelemetry、instrumentation 和记录跨度实用工具（`@elysiajs/opentelemetry`）
- `server-timing.md` - 用于调试的服务器时间度量（`@elysiajs/server-timing`) 
- `static.md` - 为 Elysia 服务器提供静态文件/文件夹（`@elysiajs/static`）

### integrations/
将 Elysia 与外部库/运行时集成的指南：
- `ai-sdk.md` - 使用 Vercel AI SDK 与 Elysia
- `astro.md` - Elysia 在 Astro API 路由中
- `better-auth.md` - 将 Elysia 与 better-auth 集成
- `cloudflare-worker.md` - Cloudflare Worker 适配器上的 Elysia
- `deno.md` - Deno 上的 Elysia
- `drizzle.md` - 将 Elysia 与 Drizzle ORM 集成
- `expo.md` - Elysia 在 Expo API 路由中
- `nextjs.md` - Nextjs API 路由中的 Elysia
- `nodejs.md` - 在 Node.js 上运行 Elysia
- `nuxt.md` - API 路由中的 Elysia
- `prisma.md` - 将 Elysia 与 Prisma 集成
- `react-email.d` - 使用 React 和 Elysia 创建和发送电子邮件
- `sveltekit.md` - 在 Svelte Kit API 路由中运行 Elysia
- `tanstack-start.md` - 在 Tanstack Start / React Query 上运行 Elysia
- `vercel.md` - 将 Elysia 部署到 Vercel

### examples/ (可选)
- `basic.ts` - 基本Elysia示例
- `body-parser.ts` - 通过 `.onParse` 的自定义 body 解析示例
- `complex.ts` - Elysia 服务器的综合使用
- `cookie.ts` - 设置 Cookie
- `error.ts` - 错误处理
- `file.ts` - 从服务器返回本地文件
- `guard.ts` - 设置多个验证模式和生命周期
- `map-response.ts` - 自定义响应映射器
- `redirect.ts` - 重定向响应
- `rename.ts` - 重命名上下文的属性 
- `schema.ts` - 设置验证
- `state.ts` - 设置全局状态
- `upload-file.ts` - 带验证的文件上传
- `websocket.ts` - 用于实时通信的 WebSocket

### patterns/ (可选)
- `patterns/mvc.md` - 使用 Elysia 与 MVC 模式的详细指南
