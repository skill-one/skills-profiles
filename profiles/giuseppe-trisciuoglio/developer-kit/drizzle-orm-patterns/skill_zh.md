# Drizzle ORM 模式

## 概述

Drizzle ORM 构建类型安全数据库应用的专家指南。涵盖所有支持数据库的架构定义、关系、查询、事务和迁移。

## 使用场景

- 使用表、列和约束定义数据库架构
- 在表之间创建关系（一对一、一对多、多对多）
- 编写类型安全的 CRUD 查询
- 实现复杂的连接和聚合
- 使用回滚管理数据库事务
- 使用 Drizzle Kit 设置迁移
- 使用 PostgreSQL、MySQL、SQLite、MSSQL 或 CockroachDB

## 快速参考

| 数据库 | 表函数 | 导入 |
|----------|---------------|--------|
| PostgreSQL | `pgTable()` | `drizzle-orm/pg-core` |
| MySQL | `mysqlTable()` | `drizzle-orm/mysql-core` |
| SQLite | `sqliteTable()` | `drizzle-orm/sqlite-core` |
| MSSQL | `mssqlTable()` | `drizzle-orm/mssql-core` |

| 操作 | 方法 | 示例 |
|-----------|--------|---------|
| 插入 | `db.insert()` | `db.insert(users).values({...})` |
| 选择 | `db.select()` | `db.select().from(users).where(eq(...))` |
| 更新 | `db.update()` | `db.update(users).set({...}).where(...)` |
| 删除 | `db.delete()` | `db.delete(users).where(...)` |
| 事务 | `db.transaction()` | `db.transaction(async (tx) => {...})` |

## 说明

1. **确定您的数据库方言** - 选择 PostgreSQL、MySQL、SQLite、MSSQL 或 CockroachDB
2. **定义您的架构** - 使用适当的表函数（pgTable、mysqlTable 等）
3. **设置关系** - 使用 `relations()` 或 `defineRelations()` 定义关系
4. **初始化数据库客户端** - 使用正确的凭证创建您的 Drizzle 客户端
5. **编写查询** - 使用查询构建器进行类型安全的 CRUD 操作
6. **处理事务** - 当需要时将多步操作包装在事务中
7. **设置迁移** - 配置 Drizzle Kit 进行架构管理

## 示例

### 示例 1：基本架构和查询

```typescript
import { pgTable, serial, text } from 'drizzle-orm/pg-core';
import { drizzle } from 'drizzle-orm/node-postgres';
import { eq } from 'drizzle-orm';

export const users = pgTable('users', {
  id: serial('id').primaryKey(),
  name: text('name').notNull(),
  email: text('email').notNull().unique(),
});

const db = drizzle(process.env.DATABASE_URL);

const [user] = await db.select().from(users).where(eq(users.id, 1));
```

### 示例 2：CRUD 操作

```typescript
import { eq } from 'drizzle-orm';

// 插入
const [newUser] = await db.insert(users).values({
  name: 'John',
  email: 'john@example.com',
}).returning();

// 更新
await db.update(users)
  .set({ name: 'John Updated' })
  .where(eq(users.id, 1));

// 删除
await db.delete(users).where(eq(users.id, 1));
```

### 示例 3：带回滚的事务

```typescript
await db.transaction(async (tx) => {
  const [from] = await tx.select().from(accounts)
    .where(eq(accounts.userId, fromId));

  if (from.balance < amount) {
    tx.rollback();
  }

  await tx.update(accounts)
    .set({ balance: sql`${accounts.balance} - ${amount}` })
    .where(eq(accounts.userId, fromId));
});
```

有关高级事务模式的更多信息，请参阅 [references/transactions.md](references/transactions.md)。

## 最佳实践

1. **类型安全**：始终使用 TypeScript 并利用 `$inferInsert` / `$inferSelect`
2. **关系**：使用 relations() API 定义关系以进行嵌套查询
3. **事务**：使用事务处理必须一起成功的多步操作
4. **迁移**：在生产中使用 `generate` + `migrate`，在开发中使用 `push`
5. **索引**：在经常查询的列和外键上添加索引
6. **软删除**：尽可能使用 `deletedAt` 时间戳而不是硬删除
7. **分页**：对大型数据集使用基于游标的分页
8. **查询优化**：使用 `.limit()` 和 `.where()` 仅获取所需数据

## 约束和警告

- **外键约束**：始终使用箭头函数 `() => table.column` 定义引用，以避免循环依赖问题
- **事务回滚**：调用 `tx.rollback()` 会抛出异常 - 如有需要请使用 try/catch
- **返回子句**：并非所有数据库都支持 `.returning()` - 检查您的方言兼容性
- **批量操作**：大型批量插入可能会达到数据库限制 - 分块为较小的批次
- **生产中的迁移**：在应用到生产之前，始终在预发布环境中测试迁移

## 参考

### 核心概念
- **[references/schema-definition.md](references/schema-definition.md)** - 所有数据库（PostgreSQL、MySQL、SQLite）的完整架构定义、列类型、索引和约束
- **[references/relations.md](references/relations.md)** - 一对一、一对多、多对多关系，v1 和 v2 语法
- **[references/queries-joins-aggregations.md](references/queries-joins-aggregations.md)** - CRUD 操作、查询运算符、连接、聚合和分页

### 高级主题
- **[references/transactions.md](references/transactions.md)** - 事务模式、回滚处理、嵌套事务
- **[references/migrations.md](references/migrations.md)** - Drizzle Kit 配置、CLI 命令、迁移工作流
- **[references/common-patterns.md](references/common-patterns.md)** - 软删除、upsert、批量操作、全文搜索、审计跟踪
