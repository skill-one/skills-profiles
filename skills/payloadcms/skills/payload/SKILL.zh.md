---
name: payload
description: 在处理 Payload 项目（payload.config.ts、集合、字段、钩子、访问控制、Payload API）时使用。在调试验证错误、安全问题、关系查询、事务或钩子行为时使用。
---

# 载荷应用开发

Payload 是一个 Next.js 原生 CMS，采用 TypeScript 首先架构，提供管理面板、数据库管理、REST/GraphQL API、认证和文件存储。

## 快速参考

| 任务                     | 解决方案                                                                   | 详情                                                                                                                          |
| ------------------------ | -------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------- |
| 自动生成别名             | `slugField()`                                                              | [FIELDS.md#slug-field-helper](reference/FIELDS.md#slug-field-helper)                                                             |
| 按用户限制内容           | 使用查询进行访问控制                                                  | [ACCESS-CONTROL.md#row-level-security-with-complex-queries](reference/ACCESS-CONTROL.md#row-level-security-with-complex-queries) |
| 本地 API 用户操作       | `user` + `overrideAccess: false`                                           | [QUERIES.md#access-control-in-local-api](reference/QUERIES.md#access-control-in-local-api)                                       |
| 草稿/发布工作流         | `versions: { drafts: true }`                                               | [COLLECTIONS.md#versioning--drafts](reference/COLLECTIONS.md#versioning--drafts)                                                 |
| 计算字段                | `virtual: true` 与 **字段级别** `hooks.afterRead` 返回值                 | [FIELDS.md#virtual-fields](reference/FIELDS.md#virtual-fields)                                                                   |
| 条件字段                | `admin.condition`                                                          | [FIELDS.md#conditional-fields](reference/FIELDS.md#conditional-fields)                                                           |
| 自定义字段验证          | `validate` 函数                                                        | [FIELDS.md#validation](reference/FIELDS.md#validation)                                                                           |
| 过滤关系列表             | 字段的 `filterOptions`                                                   | [FIELDS.md#relationship](reference/FIELDS.md#relationship)                                                                       |
| 选择特定字段             | `select` 参数                                                         | [QUERIES.md#field-selection](reference/QUERIES.md#field-selection)                                                               |
| 自动设置作者/日期        | `beforeChange` 钩子                                                          | [HOOKS.md#collection-hooks](reference/HOOKS.md#collection-hooks)                                                                 |
| 防止钩子循环            | `req.context` 检查                                                        | [HOOKS.md#context](reference/HOOKS.md#context)                                                                                   |
| 级联删除                | `beforeDelete` 钩子                                                          | [HOOKS.md#collection-hooks](reference/HOOKS.md#collection-hooks)                                                                 |
| 地理空间查询             | `point` 字段与 `near`/`within`                                         | [FIELDS.md#point-geolocation](reference/FIELDS.md#point-geolocation)                                                             |
| 反向关系                | `join` 字段类型                                                          | [FIELDS.md#join-fields](reference/FIELDS.md#join-fields)                                                                         |
| Next.js 再验证          | `afterChange` 中的上下文控制                                             | [HOOKS.md#nextjs-revalidation-with-context-control](reference/HOOKS.md#nextjs-revalidation-with-context-control)                 |
| 通过关系查询             | 嵌套属性语法                                                     | [QUERIES.md#nested-properties](reference/QUERIES.md#nested-properties)                                                           |
| 复杂查询                | AND/OR 逻辑                                                               | [QUERIES.md#andor-logic](reference/QUERIES.md#andor-logic)                                                                       |
| 事务                    | 将 `req` 传递给操作                                                   | [ADAPTERS.md#threading-req-through-operations](reference/ADAPTERS.md#threading-req-through-operations)                           |
| 后台任务                | 带有任务的作业队列                                                      | [ADVANCED.md#jobs-queue](reference/ADVANCED.md#jobs-queue)                                                                       |
| 自定义 API 路由        | 集合自定义端点                                                | [ADVANCED.md#custom-endpoints](reference/ADVANCED.md#custom-endpoints)                                                           |
| 云存储                  | 存储适配器插件                                                    | [ADAPTERS.md#storage-adapters](reference/ADAPTERS.md#storage-adapters)                                                           |
| 多语言                  | `localization` 配置 + `localized: true`                                  | [ADVANCED.md#localization](reference/ADVANCED.md#localization)                                                                   |
| 创建插件                | `(options) => (config) => Config`                                          | [PLUGIN-DEVELOPMENT.md#plugin-architecture](reference/PLUGIN-DEVELOPMENT.md#plugin-architecture)                                 |
| 插件包设置              | 使用 SWC 的包结构                                                 | [PLUGIN-DEVELOPMENT.md#plugin-package-structure](reference/PLUGIN-DEVELOPMENT.md#plugin-package-structure)                       |
| 向集合添加字段            | 映射集合，展开字段                                             | [PLUGIN-DEVELOPMENT.md#adding-fields-to-collections](reference/PLUGIN-DEVELOPMENT.md#adding-fields-to-collections)               |
| 插件钩子                | 在数组中保留现有钩子                                                   | [PLUGIN-DEVELOPMENT.md#adding-hooks](reference/PLUGIN-DEVELOPMENT.md#adding-hooks)                                               |
| 检查字段类型            | 类型守卫函数                                                       | [FIELD-TYPE-GUARDS.md](reference/FIELD-TYPE-GUARDS.md)                                                                           |

## 快速入门

```bash
npx create-payload-app@latest my-app
cd my-app
pnpm dev
```

### 最小配置

```ts
import { buildConfig } from 'payload'
import { mongooseAdapter } from '@payloadcms/db-mongodb'
import { lexicalEditor } from '@payloadcms/richtext-lexical'
import path from 'path'
import { fileURLToPath } from 'url'

const filename = fileURLToPath(import.meta.url)
const dirname = path.dirname(filename)

export default buildConfig({
  admin: {
    user: 'users',
    importMap: {
      baseDir: path.resolve(dirname),
    },
  },
  collections: [Users, Media],
  editor: lexicalEditor(),
  secret: process.env.PAYLOAD_SECRET,
  typescript: {
    outputFile: path.resolve(dirname, 'payload-types.ts'),
  },
  db: mongooseAdapter({
    url: process.env.DATABASE_URL,
  }),
})
```

## 基本模式

### 默认值和约定

在建模内容时，除非有明确理由，否则请应用这些默认值：

- **默认启用草稿/版本：** `versions: { drafts: true }`。这是任何内容集合的推荐起点。它会自动注入 `_status` 字段（`draft` / `published` / `changed`）——**不要添加自己的 `status` 字段**，它是重复的。仅跳过版本控制对于没有发布/草稿生命周期的集合（例如内部连接表、设置）。

- **使用 `slugField()` 为所有别名**，而不是手动创建 `{ name: 'slug', type: 'text', unique: true }`。它会自动从标题生成别名，添加重新生成切换，并为您处理唯一性/索引。它默认从 `title` 字段生成——如果集合没有 `title`，请传递源字段：`slugField({ useAsSlug: 'name' })`。

- **`position: 'sidebar'` 用于简短、一目了然的字段**——状态、分类、作者、发布日期。避免用于需要水平空间才能使用的长字段（描述、富文本内容、长文本）。这些属于主文档区域。

### 基本集合

```ts
import type { CollectionConfig } from 'payload'
import { slugField } from 'payload'

export const Posts: CollectionConfig = {
  slug: 'posts',
  admin: {
    useAsTitle: 'title',
    // _status (来自 versions.drafts) 显示草稿/发布状态——不需要自定义状态字段
    defaultColumns: ['title', 'author', '_status', 'createdAt'],
  },
  versions: {
    drafts: true,
  },
  fields: [
    { name: 'title', type: 'text', required: true },
    slugField(), // 自动从 `title` 生成，唯一 + 索引，侧边栏位置
    { name: 'content', type: 'richText' }, // 长字段——保持在主区域，不在侧边栏
    // 简短、一目了然的字段——适合侧边栏
    { name: 'author', type: 'relationship', relationTo: 'users', admin: { position: 'sidebar' } },
  ],
  timestamps: true,
}
```

有关更多集合模式（认证、上传、草稿、实时预览），请参阅 [COLLECTIONS.md](reference/COLLECTIONS.md)。

### 常见字段

```ts
// 文本字段
{ name: 'title', type: 'text', required: true }

// 关系
{ name: 'author', type: 'relationship', relationTo: 'users', required: true }

// 富文本
{ name: 'content', type: 'richText', required: true }

// 别名——使用辅助工具，而不是手动创建文本字段
slugField()

// 选择（用于真正的分类——不是发布状态；使用 versions.drafts + _status 用于该目的）
{ name: 'category', type: 'select', options: ['news', 'tutorial', 'opinion'] }

// 上传
{ name: 'image', type: 'upload', relationTo: 'media' }
```

有关所有字段类型（数组、块、点、连接、虚拟、条件等），请参阅 [FIELDS.md](reference/FIELDS.md)。

### 钩子示例

钩子位于两个级别之一，并且它们不能互换。**集合钩子**接收 `{ doc, data, req, operation, ... }` 并对整个文档进行操作。**字段钩子**位于单个字段的 `hooks` 对象中，接收 `{ value, siblingData, ... }` 并**返回该字段的新值**。计算/虚拟字段、每个字段的表单格式化器和每个字段的访问掩码是字段钩子；跨字段业务逻辑是集合钩子。

```ts
// 集合级别：跨文档的业务逻辑
export const Posts: CollectionConfig = {
  slug: 'posts',
  hooks: {
    beforeChange: [
      async ({ data, operation }) => {
        if (operation === 'create') {
          data.slug = slugify(data.title)
        }
        return data
      },
    ],
  },
  fields: [{ name: 'title', type: 'text' }],
}

// 字段级别：计算/格式化单个字段的值（虚拟字段使用此方法）
export const Users: CollectionConfig = {
  slug: 'users',
  fields: [
    { name: 'firstName', type: 'text' },
    { name: 'lastName', type: 'text' },
    {
      name: 'fullName',
      type: 'text',
      virtual: true,
      hooks: {
        afterRead: [({ siblingData }) => `${siblingData.firstName} ${siblingData.lastName}`],
      },
    },
  ],
}
```

当被要求“计算字段”或“在钩子中填充字段的值”时，请在该字段上使用**字段级别**钩子——永远不要使用修改 `doc` 的集合级别 `afterRead`。

有关所有钩子模式，请参阅 [HOOKS.md](reference/HOOKS.md)。有关访问控制，请参阅 [ACCESS-CONTROL.md](reference/ACCESS-CONTROL.md)。

### 基于类型的访问控制

```ts
import type { Access } from 'payload'
import type { User } from '@/payload-types'

// 类型安全的访问控制
export const adminOnly: Access = ({ req }) => {
  const user = req.user as User
  return user?.roles?.includes('admin') || false
}

// 行级访问控制
export const ownPostsOnly: Access = ({ req }) => {
  const user = req.user as User
  if (!user) return false
  if (user.roles?.includes('admin')) return true

  return {
    author: { equals: user.id },
  }
}
```

### 查询示例

```ts
// 本地 API
const posts = await payload.find({
  collection: 'posts',
  where: {
    status: { equals: 'published' },
    'author.name': { contains: 'john' },
  },
  depth: 2,
  limit: 10,
  sort: '-createdAt',
})

// 带有填充关系的查询
const post = await payload.findByID({
  collection: 'posts',
  id: '123',
  depth: 2, // 填充关系（默认是 2）
})
// 返回：{ author: { id: "user123", name: "John" } }

// 不带深度，关系只返回 ID
const post = await payload.findByID({
  collection: 'posts',
  id: '123',
  depth: 0,
})
// 返回：{ author: "user123" }
```

有关所有查询运算符和 REST/GraphQL 示例，请参阅 [QUERIES.md](reference/QUERIES.md)。

### 获取 Payload 实例

```ts
// 在 API 路由（Next.js）
import { getPayload } from 'payload'
import config from '@payload-config'

export async function GET() {
  const payload = await getPayload({ config })

  const posts = await payload.find({
    collection: 'posts',
  })

  return Response.json(posts)
}

// 在服务器组件
import { getPayload } from 'payload'
import config from '@payload-config'

export default async function Page() {
  const payload = await getPayload({ config })
  const { docs } = await payload.find({ collection: 'posts' })

  return <div>{docs.map(post => <h1 key={post.id}>{post.title}</h1>)}</div>
}
```

## 安全陷阱

### 1. 本地 API 访问控制（关键）

**默认情况下，本地 API 操作绕过所有访问控制**，即使传递了用户。

```ts
// ❌ 安全漏洞：传递用户但忽略其权限
await payload.find({
  collection: 'posts',
  user: someUser, // 访问控制被绕过！
})

// ✅ 安全：实际执行用户的权限
await payload.find({
  collection: 'posts',
  user: someUser,
  overrideAccess: false, // 必须执行访问控制
})
```

**何时使用每个：**

- `overrideAccess: true`（默认）- 信任的服务器端操作（计划任务、系统任务）
- `overrideAccess: false` - 代表用户操作（API 路由、Webhook）

参见 [QUERIES.md#access-control-in-local-api](reference/QUERIES.md#access-control-in-local-api)。

### 2. 钩子中的事务失败

**在钩子中执行嵌套操作而不带 `req` 会破坏事务原子性。**

```ts
// ❌ 数据损坏风险：分离的事务
hooks: {
  afterChange: [
    async ({ doc, req }) => {
      await req.payload.create({
        collection: 'audit-log',
        data: { docId: doc.id },
        // 缺少 req - 运行在分离的事务中！
      })
    },
  ]
}

// ✅ 原子：同一事务
hooks: {
  afterChange: [
    async ({ doc, req }) => {
      await req.payload.create({
        collection: 'audit-log',
        data: { docId: doc.id },
        req, // 保持原子性
      })
    },
  ]
}
```

参见 [ADAPTERS.md#threading-req-through-operations](reference/ADAPTERS.md#threading-req-through-operations)。

### 3. 无限钩子循环

**钩子触发操作，而操作又触发相同的钩子，会创建无限循环。**

```ts
// ❌ 无限循环
hooks: {
  afterChange: [
    async ({ doc, req }) => {
      await req.payload.update({
        collection: 'posts',
        id: doc.id,
        data: { views: doc.views + 1 },
        req,
      }) // 再次触发 afterChange！
    },
  ]
}

// ✅ 安全：使用上下文标志
hooks: {
  afterChange: [
    async ({ doc, req, context }) => {
      if (context.skipHooks) return

      await req.payload.update({
        collection: 'posts',
        id: doc.id,
        data: { views: doc.views + 1 },
        context: { skipHooks: true },
        req,
      })
    },
  ]
}
```

参见 [HOOKS.md#context](reference/HOOKS.md#context)。

## 项目结构

```txt
src/
├── app/
│   ├── (frontend)/
│   │   └── page.tsx
│   └── (payload)/
│       └── admin/[[...segments]]/page.tsx
├── collections/
│   ├── Posts.ts
│   ├── Media.ts
│   └── Users.ts
├── globals/
│   └── Header.ts
├── components/
│   └── CustomField.tsx
├── hooks/
│   └── slugify.ts
└── payload.config.ts
```

## 构建 & 类型生成

Payload 会为您生成 `payload-types.ts` —— 您很少需要手动运行 `generate:types`。

- **开发期间：** `typescript.autoGenerate` 默认为 `true`，因此开发服务器会在配置更改时自动重新生成类型。开发服务器运行时不要手动运行 `generate:types` —— 这是多余的。
- **构建期间：** `payload build` 在运行 `next build` 之前会生成导入映射和类型。优先使用它而不是直接调用 `next build`，这样两者都不会过时。传递 `--no-types` 以跳过类型生成。
- **手动生成** (`payload generate:types`) 是一个逃生通道 —— 只有当开发服务器和构建都不在循环中时（例如一次性脚本，或 CI 在某个不运行 `payload build` 的步骤之前）才使用。

```ts
// payload.config.ts
export default buildConfig({
  typescript: {
    outputFile: path.resolve(dirname, 'payload-types.ts'),
    // autoGenerate 默认为 true —— 开发期间类型会自动重新生成
  },
})

// 使用
import type { Post, User } from '@/payload-types'
```

## 常见陷阱

1. **本地 API 绕过访问控制**，除非您传递 `overrideAccess: false`
2. **嵌套操作中缺少 `req`** 会破坏事务原子性
3. **钩子循环** —— 钩子中的操作可以重新触发相同的钩子；使用 `req.context` 标志
4. **字段级访问** 仅返回布尔值，没有查询约束
5. **关系深度** 默认为 2；设置 `depth: 0` 仅获取 ID
6. **草稿状态** —— `_status` 字段在启用草稿时会自动注入
7. **类型在开发期间 (`autoGenerate`) 和 `payload build` 期间会自动重新生成** —— 避免手动运行 `generate:types`
8. **MongoDB 事务** 需要副本集配置
9. **SQLite 事务** 默认禁用；使用 `transactionOptions: {}` 启用
10. **点字段** 在 SQLite 中不受支持

## 最佳实践

### 内容建模

- 默认在内容集合上启用 `versions: { drafts: true }`；依赖自动注入的 `_status` 字段，而不是添加自定义的 `status` 字段
- 使用 `slugField()` 而不是手动创建唯一文本字段生成 slug
- 将 `position: 'sidebar'` 保留用于简短、一目了然的字段（状态、分类、作者、日期）；将长字段（描述、富文本）保留在主区域

### 安全

- 默认采用严格的访问控制，逐步添加权限
- 传递 `user` 到本地 API 时使用 `overrideAccess: false`
- 字段级访问仅返回布尔值（没有查询约束）
- 不要信任客户端提供的数据
- 使用 `saveToJWT: true` 为角色提供权限，避免数据库查找

### 性能

- 为频繁查询的字段建立索引
- 使用 `select` 限制返回的字段
- 在关系上设置 `maxDepth` 以防止过度获取
- 优先使用查询约束而不是访问控制中的异步操作
- 在 `req.context` 中缓存昂贵的操作

### 数据完整性

- 钩子中的嵌套操作始终传递 `req`
- 使用上下文标志防止无限钩子循环
- 为 MongoDB（需要副本集）和 Postgres 启用事务
- 使用 `beforeValidate` 进行数据格式化
- 使用 `beforeChange` 进行业务逻辑

### 类型安全

- 让开发 (`autoGenerate`) 和 `payload build` 生成类型；只有在两者都不运行时才手动运行 `generate:types`
- 从生成的 `payload-types.ts` 中导入类型
- 类型化您的用户对象：`import type { User } from '@/payload-types'`
- 使用字段类型守卫进行运行时类型检查
- 当将任何 Payload 值提取到命名常量中时——一个集合、字段、钩子、访问函数、插件等——用匹配的 Payload 类型（`CollectionConfig`、`Field`、`CollectionBeforeChangeHook`、`Access`、`Plugin` 等）进行注释，或使用 `satisfies <Type>`。如果没有注释，字符串属性如 `type: 'text'` 会扩展为 `string`，而区分联合类型（`Field`、`CollectionConfig`）会失败。内联字面量通过上下文类型获取此功能；提取的常量则没有。

### 组织

- 将集合保存在单独的文件中
- 将访问控制提取到 `access/` 目录
- 将钩子提取到 `hooks/` 目录
- 使用可重用字段工厂进行常见模式
- 使用注释记录复杂的访问控制

## 参考文档

- **[FIELDS.md](reference/FIELDS.md)** - 所有字段类型、验证、管理选项
- **[FIELD-TYPE-GUARDS.md](reference/FIELD-TYPE-GUARDS.md)** - 用于运行时字段类型检查和缩小类型的类型守卫
- **[COLLECTIONS.md](reference/COLLECTIONS.md)** - 集合配置、认证、上传、草稿、实时预览
- **[HOOKS.md](reference/HOOKS.md)** - 集合钩子、字段钩子、上下文模式
- **[ACCESS-CONTROL.md](reference/ACCESS-CONTROL.md)** - 集合、字段、全局访问控制、RBAC、多租户
- **[ACCESS-CONTROL-ADVANCED.md](reference/ACCESS-CONTROL-ADVANCED.md)** - 上下文感知、基于时间、基于订阅的访问、工厂函数、模板
- **[QUERIES.md](reference/QUERIES.md)** - 查询运算符、本地/REST/GraphQL API
- **[ENDPOINTS.md](reference/ENDPOINTS.md)** - 自定义 API 端点：认证、辅助函数、请求/响应模式
- **[ADAPTERS.md](reference/ADAPTERS.md)** - 数据库、存储、邮件适配器、事务
- **[ADVANCED.md](reference/ADVANCED.md)** - 认证、任务、端点、组件、插件、本地化
- **[PLUGIN-DEVELOPMENT.md](reference/PLUGIN-DEVELOPMENT.md)** - 插件架构、单体仓库结构、模式、最佳实践

## 资源

- llms-full.txt: <https://payloadcms.com/llms-full.txt>
- 文档: <https://payloadcms.com/docs>
- GitHub: <https://github.com/payloadcms/payload>
- 示例: <https://github.com/payloadcms/payload/tree/main/examples>
- 模板: <https://github.com/payloadcms/payload/tree/main/templates>
