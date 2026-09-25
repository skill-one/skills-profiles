## 概述

TanStack DB 是一个基于差分数据流构建的客户端嵌入式数据库层。它维护规范化集合，使用增量计算进行实时查询，提供自动乐观突变，并与 TanStack Query 集成以进行数据获取。即使有 10 万+ 行数据，也能实现亚毫秒级更新。

**包名：** `@tanstack/react-db`
**查询集成：** `@tanstack/query-db-collection`
**状态：** Beta (v0.5)

## 安装

```bash
npm install @tanstack/react-db @tanstack/query-db-collection
```

## 核心概念

- **集合 (Collections)**：包装数据源（TanStack Query、Electric 等）的规范化数据存储
- **实时查询 (Live Queries)**：带有 SQL 样式查询构建器的响应式订阅
- **乐观突变 (Optimistic Mutations)**：失败时回滚的自动即时 UI 更新
- **差分数据流 (Differential Dataflow)**：仅在变化时重新计算受影响的查询结果

## 集合

### 创建集合

```typescript
import { createCollection } from '@tanstack/react-db'
import { queryCollectionOptions } from '@tanstack/query-db-collection'

const todoCollection = createCollection(
  queryCollectionOptions({
    queryKey: ['todos'],
    queryFn: async () => api.todos.getAll(),
    getKey: (item) => item.id,
    schema: todoSchema,
    onInsert: async ({ transaction }) => {
      await Promise.all(
        transaction.mutations.map((mutation) =>
          api.todos.create(mutation.modified)
        )
      )
    },
    onUpdate: async ({ transaction }) => {
      await Promise.all(
        transaction.mutations.map((mutation) =>
          api.todos.update(mutation.modified)
        )
      )
    },
    onDelete: async ({ transaction }) => {
      await Promise.all(
        transaction.mutations.map((mutation) =>
          api.todos.delete(mutation.original.id)
        )
      )
    },
  })
)
```

### 同步模式

```typescript
// 主动加载 (默认)：预先加载整个集合。适用于 <10k 行。
const smallCollection = createCollection(
  queryCollectionOptions({ syncMode: 'eager', /* ... */ })
)

// 按需加载：仅加载查询请求的内容。适用于 >50k 行，搜索。
const largeCollection = createCollection(
  queryCollectionOptions({
    syncMode: 'on-demand',
    queryFn: async (ctx) => {
      const params = parseLoadSubsetOptions(ctx.meta?.loadSubsetOptions)
      return api.getProducts(params)
    },
  })
)

// 渐进式加载：立即加载查询子集，后台进行完整同步。
const collaborativeCollection = createCollection(
  queryCollectionOptions({ syncMode: 'progressive', /* ... */ })
)
```

## 实时查询

### 基本查询

```typescript
import { useLiveQuery } from '@tanstack/react-db'
import { eq } from '@tanstack/db'

function TodoList() {
  const { data: todos } = useLiveQuery((query) =>
    query
      .from({ todos: todoCollection })
      .where(({ todos }) => eq(todos.completed, false))
  )

  return <ul>{todos.map(todo => <li key={todo.id}>{todo.text}</li>)}</ul>
}
```

### 查询构建器 API

```typescript
const { data } = useLiveQuery((q) =>
  q
    .from({ t: todoCollection })
    .where(({ t }) => eq(t.status, 'active'))
    .orderBy(({ t }) => t.createdAt, 'desc')
    .limit(10)
)
```

### 连接 (Joins)

```typescript
const { data } = useLiveQuery((q) =>
  q
    .from({ t: todoCollection })
    .innerJoin(
      { u: userCollection },
      ({ t, u }) => eq(t.userId, u.id)
    )
    .innerJoin(
      { p: projectCollection },
      ({ u, p }) => eq(u.projectId, p.id)
    )
    .where(({ p }) => eq(p.id, currentProject.id))
)
```

### 过滤运算符

```typescript
import { eq, lt, and } from '@tanstack/db'

// 等于
eq(field, value)

// 小于
lt(field, value)

// AND
and(eq(product.category, 'electronics'), lt(product.price, 100))
```

### 带排序和限制

```typescript
const { data } = useLiveQuery((q) =>
  q
    .from({ product: productsCollection })
    .where(({ product }) =>
      and(eq(product.category, 'electronics'), lt(product.price, 100))
    )
    .orderBy(({ product }) => product.price, 'asc')
    .limit(10)
)
```

## 乐观突变

### 插入

```typescript
todoCollection.insert({
  id: uuid(),
  text: 'New todo',
  completed: false,
})
// 立即更新：所有引用此集合的实时查询都会更新
// 后台：调用 onInsert 处理器与服务器同步
// 失败：自动回滚
```

### 无需手动样板代码

| 之前 (仅 TanStack Query) | 之后 (TanStack DB) |
|-------------------------------|---------------------|
| 手动 `onMutate` 乐观状态 | 自动 |
| 手动 `onError` 回滚逻辑 | 自动 |
| 每次突变缓存失效 | 所有实时查询自动更新 |

## 查询驱动同步 (按需加载)

实时查询自动生成优化的网络请求：

```typescript
// 这个实时查询...
useLiveQuery((q) =>
  q.from({ product: productsCollection })
    .where(({ product }) => and(eq(product.category, 'electronics'), lt(product.price, 100)))
    .orderBy(({ product }) => product.price, 'asc')
    .limit(10)
)

// ...自动生成：
// GET /api/products?category=electronics&price_lt=100&sort=price:asc&limit=10
```

### 谓词映射

```typescript
queryFn: async (ctx) => {
  const { filters, sorts, limit } = parseLoadSubsetOptions(ctx.meta?.loadSubsetOptions)

  const params = new URLSearchParams()
  filters.forEach(({ field, operator, value }) => {
    if (operator === 'eq') params.set(field.join('.'), String(value))
    else if (operator === 'lt') params.set(`${field.join('.')}_lt`, String(value))
  })
  if (limit) params.set('limit', String(limit))

  return fetch(`/api/products?${params}`).then(r => r.json())
}
```

## 性能

| 操作 | 延迟 |
|-----------|---------|
| 单行更新 (10 万排序集合) | ~0.7 ms |
| 同步后的后续查询 | <1 ms |
| 集合间连接 | 亚毫秒 |

## 支持的集合类型

- **查询集合 (Query Collection)** - TanStack Query 集成
- **Electric 集合 (Electric Collection)** - Electric SQL 实时同步
- **TrailBase 集合 (TrailBase Collection)** - TrailBase 后端
- **RxDB 集合 (RxDB Collection)** - RxDB 集成
- **PowerSync 集合 (PowerSync Collection)** - PowerSync 同步
- **LocalStorage 集合 (LocalStorage Collection)** - 浏览器持久化
- **LocalOnly 集合 (LocalOnly Collection)** - 仅内存

## API 摘要

```typescript
import { createCollection, useLiveQuery } from '@tanstack/react-db'
import { queryCollectionOptions } from '@tanstack/query-db-collection'
import { eq, lt, and, parseLoadSubsetOptions } from '@tanstack/db'
```

## 最佳实践

1. **在模块级别定义集合** - 它们是单例的
2. **选择正确的同步模式**：`eager` (<10k), `on-demand` (>50k), `progressive` (协作式)
3. **使用连接代替特定视图的 API** - 一次性加载规范化集合
4. **让 TanStack Query 处理获取** - DB 是 Query 的增强，而非替代
5. **使用 `parseLoadSubsetOptions`** 将实时查询谓词映射到 API 参数
6. **依赖自动乐观更新** - 不要手动管理乐观状态
7. **使用模式 (schemas)** 进行运行时验证和 TypeScript 推断
8. **利用增量计算** - 让引擎处理过滤与手动 `.filter()` 的区别

## 常见陷阱

- 在组件内创建集合 (应该是模块级别的)
- 尝试完全替换 TanStack Query (DB 是在其之上构建的)
- 在渲染中使用手动 `.filter()` 而不是实时查询 `where` 子句
- 未提供 `getKey` 以进行规范化
- 忘记突变处理器 (`onInsert`, `onUpdate`, `onDelete`) 以同步服务器
