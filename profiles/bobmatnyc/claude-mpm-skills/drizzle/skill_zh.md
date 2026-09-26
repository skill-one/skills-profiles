# Drizzle ORM

一个现代化的、TypeScript优先的ORM，零依赖、编译时类型安全，并具有类似SQL的语法。针对边缘运行时和服务端无服务器环境进行了优化。

## 快速入门

### 安装

```bash
# 核心ORM
npm install drizzle-orm

# 数据库驱动（选择一个）
npm install pg            # PostgreSQL
npm install mysql2        # MySQL
npm install better-sqlite3 # SQLite

# Drizzle Kit（迁移）
npm install -D drizzle-kit
```

### 基本设置

```typescript
// db/schema.ts
import { pgTable, serial, text, timestamp } from 'drizzle-orm/pg-core';

export const users = pgTable('users', {
  id: serial('id').primaryKey(),
  email: text('email').notNull().unique(),
  name: text('name').notNull(),
  createdAt: timestamp('created_at').defaultNow(),
});

// db/client.ts
import { drizzle } from 'drizzle-orm/node-postgres';
import { Pool } from 'pg';
import * as schema from './schema';

const pool = new Pool({ connectionString: process.env.DATABASE_URL });
export const db = drizzle(pool, { schema });
```

### 第一个查询

```typescript
import { db } from './db/client';
import { users } from './db/schema';
import { eq } from 'drizzle-orm';

// 插入
const newUser = await db.insert(users).values({
  email: 'user@example.com',
  name: 'John Doe',
}).returning();

// 选择
const allUsers = await db.select().from(users);

// 条件
const user = await db.select().from(users).where(eq(users.id, 1));

// 更新
await db.update(users).set({ name: 'Jane Doe' }).where(eq(users.id, 1));

// 删除
await db.delete(users).where(eq(users.id, 1));
```

## 模式定义

### 列类型参考

| PostgreSQL | MySQL | SQLite | TypeScript |
|------------|-------|--------|------------|
| `serial()` | `serial()` | `integer()` | `number` |
| `text()` | `text()` | `text()` | `string` |
| `integer()` | `int()` | `integer()` | `number` |
| `boolean()` | `boolean()` | `integer()` | `boolean` |
| `timestamp()` | `datetime()` | `integer()` | `Date` |
| `json()` | `json()` | `text()` | `unknown` |
| `uuid()` | `varchar(36)` | `text()` | `string` |

### 常用模式

```typescript
import { pgTable, serial, text, varchar, integer, boolean, timestamp, json, unique } from 'drizzle-orm/pg-core';

export const users = pgTable('users', {
  id: serial('id').primaryKey(),
  email: varchar('email', { length: 255 }).notNull().unique(),
  passwordHash: varchar('password_hash', { length: 255 }).notNull(),
  role: text('role', { enum: ['admin', 'user', 'guest'] }).default('user'),
  metadata: json('metadata').$type<{ theme: string; locale: string }>(),
  isActive: boolean('is_active').default(true),
  createdAt: timestamp('created_at').defaultNow().notNull(),
  updatedAt: timestamp('updated_at').defaultNow().notNull(),
}, (table) => ({
  emailIdx: unique('email_unique_idx').on(table.email),
}));

// 推断TypeScript类型
type User = typeof users.$inferSelect;
type NewUser = typeof users.$inferInsert;
```

## 关系

### 一对多

```typescript
import { pgTable, serial, text, integer } from 'drizzle-orm/pg-core';
import { relations } from 'drizzle-orm';

export const authors = pgTable('authors', {
  id: serial('id').primaryKey(),
  name: text('name').notNull(),
});

export const posts = pgTable('posts', {
  id: serial('id').primaryKey(),
  title: text('title').notNull(),
  authorId: integer('author_id').notNull().references(() => authors.id),
});

export const authorsRelations = relations(authors, ({ many }) => ({
  posts: many(posts),
}));

export const postsRelations = relations(posts, ({ one }) => ({
  author: one(authors, {
    fields: [posts.authorId],
    references: [authors.id],
  }),
}));

// 查询时使用关系
const authorsWithPosts = await db.query.authors.findMany({
  with: { posts: true },
});
```

### 多对多

```typescript
export const users = pgTable('users', {
  id: serial('id').primaryKey(),
  name: text('name').notNull(),
});

export const groups = pgTable('groups', {
  id: serial('id').primaryKey(),
  name: text('name').notNull(),
});

export const usersToGroups = pgTable('users_to_groups', {
  userId: integer('user_id').notNull().references(() => users.id),
  groupId: integer('group_id').notNull().references(() => groups.id),
}, (table) => ({
  pk: primaryKey({ columns: [table.userId, table.groupId] }),
}));

export const usersRelations = relations(users, ({ many }) => ({
  groups: many(usersToGroups),
}));

export const groupsRelations = relations(groups, ({ many }) => ({
  users: many(usersToGroups),
}));

export const usersToGroupsRelations = relations(usersToGroups, ({ one }) => ({
  user: one(users, { fields: [usersToGroups.userId], references: [users.id] }),
  group: one(groups, { fields: [usersToGroups.groupId], references: [groups.id] }),
}));
```

## 查询

### 过滤

```typescript
import { eq, ne, gt, gte, lt, lte, like, ilike, inArray, isNull, isNotNull, and, or, between } from 'drizzle-orm';

// 等于
await db.select().from(users).where(eq(users.email, 'user@example.com'));

// 比较
await db.select().from(users).where(gt(users.id, 10));

// 模式匹配
await db.select().from(users).where(like(users.name, '%John%'));

// 多个条件
await db.select().from(users).where(
  and(
    eq(users.role, 'admin'),
    gt(users.createdAt, new Date('2024-01-01'))
  )
);

// IN子句
await db.select().from(users).where(inArray(users.id, [1, 2, 3]));

// NULL检查
await db.select().from(users).where(isNull(users.deletedAt));
```

### 连接

```typescript
import { eq } from 'drizzle-orm';

// 内连接
const result = await db
  .select({
    user: users,
    post: posts,
  })
  .from(users)
  .innerJoin(posts, eq(users.id, posts.authorId));

// 左连接
const result = await db
  .select({
    user: users,
    post: posts,
  })
  .from(users)
  .leftJoin(posts, eq(users.id, posts.authorId));

// 多个连接与聚合
import { count, sql } from 'drizzle-orm';

const result = await db
  .select({
    authorName: authors.name,
    postCount: count(posts.id),
  })
  .from(authors)
  .leftJoin(posts, eq(authors.id, posts.authorId))
  .groupBy(authors.id);
```

### 分页与排序

```typescript
import { desc, asc } from 'drizzle-orm';

// 排序
await db.select().from(users).orderBy(desc(users.createdAt));

// Limit & offset
await db.select().from(users).limit(10).offset(20);

// 分页辅助函数
function paginate(page: number, pageSize: number = 10) {
  return db.select().from(users)
    .limit(pageSize)
    .offset(page * pageSize);
}
```

## 事务

```typescript
// 出错时自动回滚
await db.transaction(async (tx) => {
  await tx.insert(users).values({ email: 'user@example.com', name: 'John' });
  await tx.insert(posts).values({ title: 'First Post', authorId: 1 });
  // 如果任何查询失败，整个事务回滚
});

// 手动控制
const tx = db.transaction(async (tx) => {
  const user = await tx.insert(users).values({ ... }).returning();

  if (!user) {
    tx.rollback();
    return;
  }

  await tx.insert(posts).values({ authorId: user.id });
});
```

## 迁移

### Drizzle Kit配置

```typescript
// drizzle.config.ts
import type { Config } from 'drizzle-kit';

export default {
  schema: './db/schema.ts',
  out: './drizzle',
  dialect: 'postgresql',
  dbCredentials: {
    url: process.env.DATABASE_URL!,
  },
} satisfies Config;
```

### 迁移工作流

```bash
# 生成迁移
npx drizzle-kit generate

# 查看SQL
cat drizzle/0000_migration.sql

# 应用迁移
npx drizzle-kit migrate

# 反射现有数据库
npx drizzle-kit introspect

# Drizzle Studio（数据库GUI）
npx drizzle-kit studio
```

### 示例迁移

```sql
-- drizzle/0000_initial.sql
CREATE TABLE IF NOT EXISTS "users" (
  "id" serial PRIMARY KEY NOT NULL,
  "email" varchar(255) NOT NULL,
  "name" text NOT NULL,
  "created_at" timestamp DEFAULT now() NOT NULL,
  CONSTRAINT "users_email_unique" UNIQUE("email")
);
```

## 导航

### 详细参考

- **[🏗️ 高级模式](./references/advanced-schemas.md)** - 自定义类型、复合键、索引、约束、多租户模式。设计复杂数据库模式时加载。

- **[🔍 查询模式](./references/query-patterns.md)** - 子查询、CTE、原始SQL、预编译语句、批量操作。优化查询或处理复杂过滤时加载。

- **[⚡ 性能](./references/performance.md)** - 连接池、查询优化、N+1预防、预编译语句、边缘运行时集成。扩展或优化数据库性能时加载。

- **[🔄 vs Prisma](./references/vs-prisma.md)** - 功能比较、迁移指南、何时选择Drizzle而非Prisma。评估ORM或从Prisma迁移时加载。

## 警示

**如果出现以下情况，请停止并重新考虑：**
- 对JSON列使用`any`或`unknown`而不进行类型注解
- 不使用`sql`模板构建原始SQL字符串（SQL注入风险）
- 不使用事务进行多步骤数据修改
- 生产查询中不分页获取所有行
- 外键或频繁查询的列缺少索引
- 大型表使用`select()`而不指定列

## 与Prisma的性能对比

| 指标 | Drizzle | Prisma |
|------|---------|--------|
| **包体积** | ~35KB | ~230KB |
| **冷启动** | ~10ms | ~250ms |
| **查询速度** | 基线 | ~2-3倍慢 |
| **内存** | ~10MB | ~50MB |
| **类型生成** | 运行时推断 | 构建时生成 |

## 集成

- **typescript-core**: 使用`satisfies`进行类型安全的模式推断
- **nextjs-core**: 服务器动作、路由处理程序、中间件集成
- **数据库迁移**: 安全的模式演化模式

## 相关技能

使用Drizzle时，以下技能可提升工作流：
- **prisma**: 替代性ORM比较：Drizzle与Prisma的权衡
- **typescript**: 高级TypeScript模式，用于类型安全查询
- **nextjs**: Drizzle与Next.js服务器动作和API路由
- **sqlalchemy**: SQLAlchemy模式，供Python开发者学习Drizzle

[如果您的包中部署了这些技能，则提供完整文档]
