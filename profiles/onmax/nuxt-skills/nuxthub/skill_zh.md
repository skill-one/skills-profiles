# NuxtHub v0.10.6

全栈 Nuxt 框架，包含数据库、KV 存储、Blob 存储和缓存。支持多云环境（Cloudflare、Vercel、Deno、Netlify）。

**对于 Nuxt 服务器模式：** 使用 `nuxt` 技能（server.md）
**对于带数据库的内容：** 使用 `nuxt-content` 技能

## 文件加载

**根据您的任务考虑加载以下参考文件：**

- [ ] [references/wrangler-templates.md](references/wrangler-templates.md) - 如果手动配置 wrangler.jsonc 用于 Cloudflare 部署
- [ ] [references/providers.md](references/providers.md) - 如果部署到 Vercel、Netlify、Deno、AWS 或配置外部数据库/存储提供者

**不要一次性加载所有文件。** 仅加载与您当前任务相关的文件。

## 安装

```bash
npx nuxi module add hub
```

## 配置

```ts
// nuxt.config.ts
export default defineNuxtConfig({
  modules: ['@nuxthub/core'],
  hub: {
    db: 'sqlite', // 'sqlite' | 'postgresql' | 'mysql'
    kv: true,
    blob: true,
    cache: true,
    dir: '.data', // 本地存储目录
    remote: false // 在开发中使用生产绑定（v0.10+）
  }
})
```

### 高级配置

```ts
hub: {
  db: {
    dialect: 'postgresql',
    driver: 'postgres-js', // 可选：自动检测
    casing: 'snake_case',  // camelCase JS -> snake_case DB (v0.10.3+)
    migrationsDirs: ['server/db/custom-migrations/'],
    applyMigrationsDuringBuild: true, // 默认
    replica: { // 读取副本支持（v0.10.6+）
      connection: { connectionString: process.env.DATABASE_REPLICA_URL }
    }
  },
  remote: true // 在开发中使用生产 Cloudflare 绑定（v0.10+）
}
```

**remote 模式：** 启用时，在本地开发期间连接到生产 D1/KV/R2，而不是本地模拟。用于使用生产数据进行测试。

**数据库副本（v0.10.6+）：** 配置读取副本以分配数据库负载。查询自动使用副本，而写入则发送到主数据库。

## 数据库

通过 Drizzle ORM 进行类型安全的 SQL。`db` 和 `schema` 在服务器端自动导入。

### 模式定义

放置在 `server/db/schema.ts` 或 `server/db/schema/*.ts`：

```ts
// server/db/schema.ts (SQLite)
import { integer, sqliteTable, text } from 'drizzle-orm/sqlite-core'

export const users = sqliteTable('users', {
  id: integer().primaryKey({ autoIncrement: true }),
  name: text().notNull(),
  email: text().notNull().unique(),
  createdAt: integer({ mode: 'timestamp' }).notNull()
})
```

PostgreSQL 变体：

```ts
import { pgTable, serial, text, timestamp } from 'drizzle-orm/pg-core'

export const users = pgTable('users', {
  id: serial().primaryKey(),
  name: text().notNull(),
  email: text().notNull().unique(),
  createdAt: timestamp().notNull().defaultNow()
})
```

### 数据库 API

```ts
// db 和 schema 在服务器端自动导入
import { db, schema } from 'hub:db'

// 选择
const users = await db.select().from(schema.users)
const user = await db.query.users.findFirst({ where: eq(schema.users.id, 1) })

// 插入
const [newUser] = await db.insert(schema.users).values({ name: 'John', email: 'john@example.com' }).returning()

// 更新
await db.update(schema.users).set({ name: 'Jane' }).where(eq(schema.users.id, 1))

// 删除
await db.delete(schema.users).where(eq(schema.users.id, 1))
```

### 迁移

```bash
npx nuxt db generate                  # 从模式生成迁移
npx nuxt db migrate                   # 应用待处理的迁移
npx nuxt db sql "SELECT * FROM users" # 执行原始 SQL
npx nuxt db drop <TABLE>              # 删除特定表
npx nuxt db drop-all                  # 删除所有表（v0.10+）
npx nuxt db squash                    # 将迁移压缩为一个（v0.10+）
npx nuxt db mark-as-migrated [NAME]   # 标记为已迁移而不运行
```

迁移在 `npx nuxi dev` 和 `npx nuxi build` 期间自动应用。记录在 `_hub_migrations` 表中。

### 数据库提供者

| 语法    | 本地                | 生产                                                         |
| ------- | ------------------- | ------------------------------------------------------------------ |
| sqlite  | `.data/db/sqlite.db` | D1 (Cloudflare), Turso (`TURSO_DATABASE_URL`, `TURSO_AUTH_TOKEN`)  |
| postgresql | PGlite               | postgres-js (`DATABASE_URL`), neon-http (v0.10.2+, `DATABASE_URL`) |
| mysql   | -                    | mysql2 (`DATABASE_URL`, `MYSQL_URL`)                               |

## KV 存储

键值存储。`kv` 在服务器端自动导入。

```ts
import { kv } from 'hub:kv'

await kv.set('key', { data: 'value' })
await kv.set('key', value, { ttl: 60 }) // TTL 以秒为单位
const value = await kv.get('key')
const exists = await kv.has('key')
await kv.del('key')
const keys = await kv.keys('prefix:')
await kv.clear('prefix:')
```

限制：最大值 25 MiB，最大键 512 字节。

### KV 提供者

| 提供者      | 包          | 环境变量                                             |
| ----------- | ------------ | ---------------------------------------------------- |
| Upstash     | `@upstash/redis` | `UPSTASH_REDIS_REST_URL`, `UPSTASH_REDIS_REST_TOKEN` |
| Redis       | `ioredis`    | `REDIS_URL`                                          |
| Cloudflare KV | -            | `KV` 绑定在 wrangler.jsonc 中                       |
| Deno KV     | -            | Deno Deploy 自动启用                                  |
| Vercel      | -            | `KV_REST_API_URL`, `KV_REST_API_TOKEN`               |

## Blob 存储

文件存储。`blob` 在服务器端自动导入。

### Blob API

```ts
import { blob } from 'hub:blob'

// 上传
const result = await blob.put('path/file.txt', body, {
  contentType: 'text/plain',
  access: 'public', // 'public' | 'private' (v0.10.2+)
  addRandomSuffix: true,
  prefix: 'uploads'
})
// 返回：{ pathname, contentType, size, httpEtag, uploadedAt }

// 下载
const file = await blob.get('path/file.txt') // 返回 Blob 或 null

// 列出
const { blobs, cursor, hasMore, folders } = await blob.list({ prefix: 'uploads/', limit: 10, folded: true })

// 提供（带正确的头部）
return blob.serve(event, 'path/file.txt')

// 删除
await blob.del('path/file.txt')
await blob.del(['file1.txt', 'file2.txt']) // 多个

// 仅元数据
const meta = await blob.head('path/file.txt')
```

### 上传辅助函数

```ts
// 服务器：验证 + 上传处理
export default eventHandler(async (event) => {
  return blob.handleUpload(event, {
    formKey: 'files',
    multiple: true,
    ensure: { maxSize: '10MB', types: ['image/png', 'image/jpeg'] },
    put: { addRandomSuffix: true, prefix: 'images' }
  })
})

// 手动上传前验证
ensureBlob(file, { maxSize: '10MB', types: ['image'] })

// 大文件（>10MB）的多部分上传
export default eventHandler(async (event) => {
  return blob.handleMultipartUpload(event) // 路由：/api/files/multipart/[action]/[...pathname]
})
```

### Vue 组合式 API

```ts
// 简单上传
const upload = useUpload('/api/upload')
const result = await upload(inputElement)

// 带进度的多部分上传
const mpu = useMultipartUpload('/api/files/multipart')
const { completed, progress, abort } = mpu(file)
```

### Blob 提供者

| 提供者      | 包          | 配置                                                               |
| ----------- | ------------ | -------------------------------------------------------------------- |
| Cloudflare R2 | -            | `BLOB` 绑定在 wrangler.jsonc 中                                     |
| Vercel Blob   | `@vercel/blob` | `BLOB_READ_WRITE_TOKEN`                                              |
| S3            | `aws4fetch`    | `S3_ACCESS_KEY_ID`, `S3_SECRET_ACCESS_KEY`, `S3_BUCKET`, `S3_REGION` |

## 缓存

响应和函数缓存。

### 路由处理器缓存

```ts
export default cachedEventHandler((event) => {
  return { data: 'cached', date: new Date().toISOString() }
}, {
  maxAge: 60 * 60, // 1 小时
  getKey: event => event.path
})
```

### 函数缓存

```ts
export const getStars = defineCachedFunction(
  async (event: H3Event, repo: string) => {
    const data = await $fetch(`https://api.github.com/repos/${repo}`)
    return data.stargazers_count
  },
  { maxAge: 3600, name: 'ghStars', getKey: (event, repo) => repo }
)
```

### 缓存失效

```ts
// 删除特定
await useStorage('cache').removeItem('nitro:functions:getStars:repo-name.json')

// 按前缀清除
await useStorage('cache').clear('nitro:handlers')
```

缓存键模式：`${group}:${name}:${getKey(...args)}.json`（默认：group='nitro', name='handlers'|'functions'|'routes'）

## 部署

### Cloudflare

NuxtHub 从您的 hub 配置自动生成 `wrangler.json` - 无需手动 wrangler.jsonc：

```ts
// nuxt.config.ts
export default defineNuxtConfig({
  hub: {
    db: {
      dialect: 'sqlite',
      driver: 'd1',
      connection: { databaseId: '<database-id>' }
    },
    kv: {
      driver: 'cloudflare-kv-binding',
      namespaceId: '<kv-namespace-id>'
    },
    cache: {
      driver: 'cloudflare-kv-binding',
      namespaceId: '<cache-namespace-id>'
    },
    blob: {
      driver: 'cloudflare-r2',
      bucketName: '<bucket-name>'
    }
  }
})
```

**可观察性（推荐）：** 启用生产部署的日志记录：

```jsonc
// wrangler.jsonc (可选)
{
  "observability": {
    "logs": {
      "enabled": true,
      "head_sampling_rate": 1,
      "invocation_logs": true,
      "persist": true
    }
  }
}
```

通过 Cloudflare 仪表板或 CLI 创建资源：

```bash
npx wrangler d1 create my-db              # 获取 database-id
npx wrangler kv namespace create KV       # 获取 kv-namespace-id
npx wrangler kv namespace create CACHE    # 获取 cache-namespace-id
npx wrangler r2 bucket create my-bucket   # 获取 bucket-name
```

部署：创建 [Cloudflare Workers 项目](https://dash.cloudflare.com/?to=/:account/workers-and-pages/create)，链接 Git 仓库。绑定在构建时自动配置。

**环境：** 使用 `CLOUDFLARE_ENV=preview` 进行预览部署。

参考 [references/wrangler-templates.md](references/wrangler-templates.md) 获取手动 wrangler.jsonc 模式，以及 [references/providers.md](references/providers.md) 获取所有提供者配置。

### 其他提供者

参考 [references/providers.md](references/providers.md) 获取详细部署模式：

- **Vercel：** Postgres、Turso、Vercel Blob、Vercel KV
- **Netlify：** 外部数据库、S3、Upstash Redis
- **Deno Deploy：** Deno KV
- **AWS/自托管：** S3、RDS、自定义配置

### D1 over HTTP

从非 Cloudflare 主机查询 D1：

```ts
hub: {
  db: { dialect: 'sqlite', driver: 'd1-http' }
}
```

要求：`NUXT_HUB_CLOUDFLARE_ACCOUNT_ID`, `NUXT_HUB_CLOUDFLARE_API_TOKEN`, `NUXT_HUB_CLOUDFLARE_DATABASE_ID`

## 构建时钩子

```ts
// 扩展模式
nuxt.hook('hub:db:schema:extend', async ({ dialect, paths }) => {
  paths.push(await resolvePath(`./schema/custom.${dialect}`))
})

// 添加迁移目录
nuxt.hook('hub:db:migrations:dirs', (dirs) => {
  dirs.push(resolve('./db-migrations'))
})

// 迁移后查询（幂等）
nuxt.hook('hub:db:queries:paths', (paths, dialect) => {
  paths.push(resolve(`./seed.${dialect}.sql`))
})
```

## 类型共享

```ts
// shared/types/db.ts
import type { users } from '~/server/db/schema'

export type User = typeof users.$inferSelect
export type NewUser = typeof users.$inferInsert
```

## WebSocket / 实时

启用实验性 WebSocket：

```ts
// nuxt.config.ts
nitro: { experimental: { websocket: true } }
```

```ts
// server/routes/ws/chat.ts
export default defineWebSocketHandler({
  open(peer) {
    peer.subscribe('chat')
    peer.publish('chat', 'User joined')
  },
  message(peer, message) {
    peer.publish('chat', message.text())
  },
  close(peer) {
    peer.unsubscribe('chat')
  }
})
```

## 已弃用（v0.10）

移除 Cloudflare 特定功能：

- `hubAI()` -> 使用 Workers AI 提供者的 AI SDK
- `hubBrowser()` -> Puppeteer
- `hubVectorize()` -> Vectorize
- NuxtHub 管理 -> 2025 年 12 月 31 日停用
- `npx nuxhub deploy` -> 使用 wrangler deploy

## 快速参考

| 功能  | 导入                                | 访问                             |
| ------ | ------------------------------------- | ---------------------------------- |
| 数据库 | `import { db, schema } from 'hub:db'` | `db.select()`, `db.insert()`, 等. |
| KV     | `import { kv } from 'hub:kv'`         | `kv.get()`, `kv.set()`, 等.       |
| Blob   | `import { blob } from 'hub:blob'`     | `blob.put()`, `blob.get()`, 等.   |

所有在服务器端自动导入。

## 资源

- [安装](https://hub.nuxt.com/docs/getting-started/installation)
- [从 v0.9 迁移](https://hub.nuxt.com/docs/getting-started/migration)
- [数据库](https://hub.nuxt.com/docs/database)
- [Blob](https://hub.nuxt.com/docs/blob)
- [KV](https://hub.nuxt.com/docs/kv)
- [缓存](https://hub.nuxt.com/docs/cache)
- [部署](https://hub.nuxt.com/docs/getting-started/deploy)
