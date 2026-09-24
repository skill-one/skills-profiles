# Prisma Client API 参考

Prisma Client 的完整 API 参考。本技能为当前 Prisma 项目中的模型查询、过滤、关联以及客户端方法提供指导。

## 适用场景

参考本技能时，请满足以下条件：
- 使用 Prisma Client 编写数据库查询
- 执行 CRUD 操作（创建、读取、更新、删除）
- 对数据进行过滤和排序
- 处理关联关系
- 使用事务
- 配置客户端选项

## 按优先级划分的规则类别

| Priority | Category | Impact | Prefix |
|----------|----------|--------|--------|
| 1 | 客户端构建 | HIGH | `constructor` |
| 2 | 模型查询 | CRITICAL | `model-queries` |
| 3 | 查询结构 | HIGH | `query-options` |
| 4 | 过滤 | HIGH | `filters` |
| 5 | 关联 | HIGH | `relations` |
| 6 | 事务 | CRITICAL | `transactions` |
| 7 | 原始 SQL | CRITICAL | `raw-queries` |
| 8 | 客户端方法 | MEDIUM | `client-methods` |

## 快速参考

- `constructor` - `PrismaClient` 配置、适配器连接、日志记录以及 SQL 注释器插件
- `model-queries` - CRUD 操作和批量操作
- `query-options` - `select`、`include`、`omit`、排序、分页
- `filters` - 标量与逻辑过滤运算符
- `relations` - 关联读取与嵌套写入
- `transactions` - 数组与交互式事务模式
- `raw-queries` - `$queryRaw` 和 `$executeRaw` 的安全性
- `client-methods` - 生命周期方法、扩展，以及 `prisma-client` 的 `satisfies` 模式

## 客户端实例化

```typescript
import { PrismaClient } from '../generated/client'
import { PrismaPg } from '@prisma/adapter-pg'

const adapter = new PrismaPg({
  connectionString: process.env.DATABASE_URL
})

const prisma = new PrismaClient({ adapter })
```

## 模型查询方法

| 方法 | 描述 |
|--------|-------------|
| `findUnique()` | 通过唯一字段查找一条记录 |
| `findUniqueOrThrow()` | 查找一条记录或抛出错误 |
| `findFirst()` | 查找第一条匹配记录 |
| `findFirstOrThrow()` | 查找第一条或抛出错误 |
| `findMany()` | 查找多条记录 |
| `create()` | 创建一条新记录 |
| `createMany()` | 创建多条记录 |
| `createManyAndReturn()` | 创建多条并返回它们 |
| `update()` | 更新一条记录 |
| `updateMany()` | 更新多条记录 |
| `updateManyAndReturn()` | 更新多条并返回它们 |
| `upsert()` | 更新或创建记录 |
| `delete()` | 删除一条记录 |
| `deleteMany()` | 删除多条记录 |
| `count()` | 统计匹配记录数 |
| `aggregate()` | 聚合数值（sum、avg 等） |
| `groupBy()` | 分组并聚合 |

## 查询选项

| 选项 | 描述 |
|--------|-------------|
| `where` | 过滤条件 |
| `select` | 要包含的字段 |
| `include` | 要加载的关联 |
| `omit` | 要排除的字段 |
| `orderBy` | 排序顺序 |
| `take` | 限制结果数 |
| `skip` | 跳过结果（分页） |
| `cursor` | 游标分页 |
| `distinct` | 仅唯一值 |

## 客户端方法

| 方法 | 描述 |
|--------|-------------|
| `$connect()` | 显式连接到数据库 |
| `$disconnect()` | 与数据库断开连接 |
| `$transaction()` | 执行事务 |
| `$queryRaw()` | 执行原始 SQL 查询 |
| `$executeRaw()` | 执行原始 SQL 命令 |
| `$on()` | 订阅事件 |
| `$extends()` | 添加扩展 |

## 快速示例

### 查找记录

```typescript
// 通过唯一字段查找
const user = await prisma.user.findUnique({
  where: { email: 'alice@prisma.io' }
})

// 带过滤条件查找
const users = await prisma.user.findMany({
  where: { role: 'ADMIN' },
  orderBy: { createdAt: 'desc' },
  take: 10
})
```

### 创建记录

```typescript
const user = await prisma.user.create({
  data: {
    email: 'alice@prisma.io',
    name: 'Alice',
    posts: {
      create: { title: 'Hello World' }
    }
  },
  include: { posts: true }
})
```

### 更新记录

```typescript
const user = await prisma.user.update({
  where: { id: 1 },
  data: { name: 'Alice Smith' }
})
```

### 删除记录

```typescript
await prisma.user.delete({
  where: { id: 1 }
})
```

### 事务

```typescript
const [user, post] = await prisma.$transaction([
  prisma.user.create({ data: { email: 'alice@prisma.io' } }),
  prisma.post.create({ data: { title: 'Hello', authorId: 1 } })
])
```

## 规则文件

详细的 API 文档：

```
references/constructor.md        - PrismaClient constructor options
references/model-queries.md      - CRUD operations
references/query-options.md      - select, include, omit, where, orderBy
references/filters.md            - Filter conditions and operators
references/relations.md          - Relation queries and nested operations
references/transactions.md       - Transaction API
references/raw-queries.md        - $queryRaw, $executeRaw
references/client-methods.md     - $connect, $disconnect, $on, $extends
```

## 过滤运算符

| 运算符 | 描述 |
|----------|-------------|
| `equals` | 完全匹配 |
| `not` | 不相等 |
| `in` | 在数组中 |
| `notIn` | 不在数组中 |
| `lt`, `lte` | 小于 |
| `gt`, `gte` | 大于 |
| `contains` | 字符串包含 |
| `startsWith` | 字符串以...开头 |
| `endsWith` | 字符串以...结尾 |
| `mode` | 大小写敏感性 |

## 关联过滤

| 运算符 | 描述 |
|----------|-------------|
| `some` | 至少有一条关联记录匹配 |
| `every` | 所有关联记录都匹配 |
| `none` | 没有关联记录匹配 |
| `is` | 关联记录匹配（一对一） |
| `isNot` | 关联记录不匹配 |

## 资源

- [Prisma Client API 参考](https://www.prisma.io/docs/orm/reference/prisma-client-reference)
- [CRUD 操作](https://www.prisma.io/docs/orm/prisma-client/queries/crud)
- [过滤与排序](https://www.prisma.io/docs/orm/prisma-client/queries/filtering-and-sorting)

## 使用方法

从上述表格中选取类别，然后打开对应的参考文件，查看具体实现细节和示例。
