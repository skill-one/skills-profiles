# D1 Drizzle Schema

为 Cloudflare D1 生成正确的 Drizzle ORM 模式。D1 基于 SQLite，但存在重要差异，若使用标准 SQLite 模式会导致细微的 Bug。此技能生成的模式能够正确配合 D1 的约束使用。

## 关键 D1 差异

| 功能 | 标准SQLite | D1 |
|------|-----------|----|
| 外键 | 默认关闭 | **始终开启**（无法禁用） |
| 布尔类型 | 无 | 无 — 使用 `integer({ mode: 'boolean' })` |
| 日期时间类型 | 无 | 无 — 使用 `integer({ mode: 'timestamp' })` |
| 最大参数限制 | 约999 | **100**（影响批量插入） |
| JSON 支持 | 扩展 | **始终可用**（json_extract, ->, ->>） |
| 并发 | 多写入者 | **单线程**（一次一个查询） |

## 工作流程

### 第一步：描述数据模型

收集需求：需要哪些表、哪些关系、哪些需要索引。若基于现有描述工作，可直接推断模式。

### 第二步：生成 Drizzle 模式

使用 D1 正确的列模式创建模式文件：

```typescript
import { sqliteTable, text, integer, real, index, uniqueIndex } from 'drizzle-orm/sqlite-core'

export const users = sqliteTable('users', {
  // UUID 主键（D1推荐）
  id: text('id').primaryKey().$defaultFn(() => crypto.randomUUID()),

  // 文本字段
  name: text('name').notNull(),
  email: text('email').notNull(),

  // 枚举（存储为TEXT，在模式级别验证）
  role: text('role', { enum: ['admin', 'editor', 'viewer'] }).notNull().default('viewer'),

  // 布尔（D1无BOOL — 存储为0/1的INTEGER）
  emailVerified: integer('email_verified', { mode: 'boolean' }).notNull().default(false),

  // 时间戳（D1无DATETIME — 存储为Unix秒）
  createdAt: integer('created_at', { mode: 'timestamp' }).notNull().$defaultFn(() => new Date()),
  updatedAt: integer('updated_at', { mode: 'timestamp' }).notNull().$defaultFn(() => new Date()),

  // 带类型的JSON（存储为TEXT，Drizzle自动序列化）
  preferences: text('preferences', { mode: 'json' }).$type<UserPreferences>(),

  // 外键（D1始终强制执行）
  organisationId: text('organisation_id').references(() => organisations.id, { onDelete: 'cascade' }),
}, (table) => ({
  emailIdx: uniqueIndex('users_email_idx').on(table.email),
  orgIdx: index('users_org_idx').on(table.organisationId),
}))
```

参考 [references/column-patterns.md](references/column-patterns.md) 获取完整类型参考。

### 第三步：添加关系

Drizzle 关系是查询构建器辅助工具（与外键约束分离）：

```typescript
import { relations } from 'drizzle-orm'

export const usersRelations = relations(users, ({ one, many }) => ({
  organisation: one(organisations, {
    fields: [users.organisationId],
    references: [organisations.id],
  }),
  posts: many(posts),
}))
```

### 第四步：导出类型

```typescript
export type User = typeof users.$inferSelect
export type NewUser = typeof users.$inferInsert
```

### 第五步：设置 Drizzle 配置

将 [assets/drizzle-config-template.ts](assets/drizzle-config-template.ts) 复制到 `drizzle.config.ts` 并更新模式路径。

### 第六步：添加迁移脚本

添加到 `package.json`：
```json
{
  "db:generate": "drizzle-kit generate",
  "db:migrate:local": "wrangler d1 migrations apply DB --local",
  "db:migrate:remote": "wrangler d1 migrations apply DB --remote"
}
```

**测试前必须在本地和远程都运行。**

### 第七步：生成 DATABASE_SCHEMA.md

为未来会话记录模式：
- 表格、列、类型和约束
- 关系和外键
- 索引及其用途
- 迁移工作流程

## 批量插入模式

D1 限制绑定参数为100。计算批处理大小：

```typescript
const BATCH_SIZE = Math.floor(100 / COLUMNS_PER_ROW)
for (let i = 0; i < rows.length; i += BATCH_SIZE) {
  await db.insert(table).values(rows.slice(i, i + BATCH_SIZE))
}
```

## D1 运行时使用

```typescript
import { drizzle } from 'drizzle-orm/d1'
import * as schema from './schema'

// 在Worker fetch处理器中：
const db = drizzle(env.DB, { schema })

// 查询模式
const all = await db.select().from(schema.users).all()           // Array<User>
const one = await db.select().from(schema.users).where(eq(schema.users.id, id)).get()  // User | undefined
const count = await db.select({ count: sql`count(*)` }).from(schema.users).get()
```

## 参考文件

| 当使用时 | 阅读 |
|--------|------|
| D1 vs SQLite, JSON查询,限制 | [references/d1-specifics.md](references/d1-specifics.md) |
| Drizzle + D1的列类型模式 | [references/column-patterns.md](references/column-patterns.md) |

## 资产

| 文件 | 用途 |
|------|------|
| [assets/drizzle-config-template.ts](assets/drizzle-config-template.ts) | D1的起始drizzle.config.ts |
| [assets/schema-template.ts](assets/schema-template.ts) | 包含所有常见D1模式的示例模式 |
