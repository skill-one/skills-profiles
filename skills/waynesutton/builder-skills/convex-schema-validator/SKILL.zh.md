---
name: convex-schema-validator
description: 设计凸面/模式.ts表、验证器、索引和关系，并在数据演变时保持模式的一致性。在创建表、添加字段、选择索引字段、建模关系或部署时出现验证器错误时使用。
---

# 凸包模式验证器

生成一个 `convex/schema.ts`，该文件对每个文档进行类型定义，对每个查询路径建立索引，并对数据库中已有的数据进行验证。唯一规则：函数中的每个 `withIndex` 都需要一个匹配的 `.index()`，其名称以字段命名，并按字段顺序查询。

## 何时使用此功能

- 创建新表或向现有表添加字段
- 查询使用 `.filter()` 但需要索引的情况
- 决定是否使用 `v.id` 嵌入对象或链接
- 建模形状多样的文档
- `npx convex dev` 因模式验证错误而失败

## 模式骨架

```typescript
// convex/schema.ts
import { defineSchema, defineTable } from "convex/server";
import { v } from "convex/values";

export default defineSchema({
  users: defineTable({
    name: v.string(),
    email: v.string(),
    avatarUrl: v.optional(v.string()),
  }).index("by_email", ["email"]),

  tasks: defineTable({
    userId: v.id("users"),
    title: v.string(),
    completed: v.boolean(),
    priority: v.union(v.literal("low"), v.literal("medium"), v.literal("high")),
  })
    .index("by_userId", ["userId"])
    .index("by_userId_and_completed", ["userId", "completed"]),
});
```

`defineTable` 接收字段验证器对象或单个 `v.union` 的 `v.object` 验证器（参见区分联合）。每个表都会免费获得 `_id` 和 `_creationTime`。不要声明它们。

## 验证器

| 验证器 | TypeScript 类型 | 备注 |
| --- | --- | --- |
| `v.string()` | `string` | UTF-8，小于 1 MB |
| `v.number()` | `number` | Float64。用于时间戳和计数 |
| `v.boolean()` | `boolean` | |
| `v.null()` | `null` | `undefined` 不是 Convex 值。返回 `null` 而不是 |
| `v.int64()` | `bigint` | 不是 `v.bigint()`，后者已弃用 |
| `v.bytes()` | `ArrayBuffer` | 小于 1 MB |
| `v.id("table")` | `Id<"table">` | 类型引用。Convex 不强制要求目标存在 |
| `v.array(t)` | `T[]` | 最多 8192 项 |
| `v.object({...})` | `{...}` | 最多 1024 个条目。键不能以 `$` 或 `_` 开头 |
| `v.record(k, t)` | `Record<K, T>` | 动态 ASCII 键。没有 `v.map` 或 `v.set` |
| `v.union(a, b)` | `A \| B` | 使用 `v.literal` 成员定义枚举 |
| `v.literal("x")` | `"x"` | |
| `v.optional(t)` | `T \| undefined` | 字段可能不存在 |
| `v.any()` | `any` | 万能方案。失去类型安全和验证 |

## 可选与可空

`v.optional` 表示文档中可能缺少该键。`v.union(t, v.null())` 表示键始终存在且可能为 `null`。它们在验证时是不同的。

```typescript
items: defineTable({
  description: v.optional(v.string()),           // 可能不存在
  deletedAt: v.union(v.number(), v.null()),       // 始终存在，可能为 null
  notes: v.optional(v.union(v.string(), v.null())), // 任意
}),
```

对于在表已有数据后添加的字段，使用 `v.optional`。当“显式清除”有意义时，使用 `v.union(..., v.null())`。

## 区分联合

对于文档形状多样的表，将 `v.union` 的 `v.object` 验证器传递给 `defineTable`。每个成员都有相同的字面量键，因此 TypeScript 会对其进行类型缩小。

```typescript
events: defineTable(
  v.union(
    v.object({
      kind: v.literal("signup"),
      userId: v.id("users"),
      email: v.string(),
    }),
    v.object({
      kind: v.literal("purchase"),
      userId: v.id("users"),
      orderId: v.id("orders"),
      amount: v.number(),
    }),
  ),
).index("by_kind", ["kind"]),
```

在联合表的任何索引中都应将区分条件（`kind`）放在第一位，以便查询可以针对一种形状进行范围限制。优先选择此方案，而不是一个包含大量 `v.optional` 字段的宽对象。

## 索引

### 命名和字段顺序

按字段顺序命名索引：`by_field1_and_field2`。查询必须遵循相同的顺序：对字段前缀进行等值过滤，然后对下一个字段进行最多一个范围的过滤。

```typescript
messages: defineTable({
  channelId: v.id("channels"),
  authorId: v.id("users"),
  sentAt: v.number(),
})
  .index("by_channelId", ["channelId"])
  .index("by_channelId_and_authorId", ["channelId", "authorId"])
  .index("by_channelId_and_sentAt", ["channelId", "sentAt"]),
```

```typescript
// 有效：对 channelId 进行等值过滤，对 sentAt 进行范围过滤
await ctx.db
  .query("messages")
  .withIndex("by_channelId_and_sentAt", (q) =>
    q.eq("channelId", args.channelId).gt("sentAt", args.since),
  )
  .order("desc")
  .take(50);
```

使用该索引无法跳过 `channelId` 而仅对 `sentAt` 进行过滤。如果存在该查询，请添加 `by_sentAt`。`_creationTime` 会自动追加到每个索引中，因此等值前缀内的结果按创建时间排序。

保留名称：`by_id` 和 `by_creation_time`。限制：每个表最多 32 个索引，每个索引最多 16 个字段。

### 何时添加索引

- 任何函数传递给 `withIndex`、`.eq` 或范围比较的字段
- 子表上的每个外键（`userId`、`channelId`、`orgId`）
- 分页列表的排序字段，以范围字段为前缀
- 仅在获取文档后读取的字段
- 对于小型表，使用 `.collect()` 然后在内存中过滤是合适的

如果查询使用 `.filter()`，则这是添加索引并切换到 `withIndex` 的信号。

## 关系

使用 `v.id("table")` 在子表上链接文档。不要在父表中嵌套不断增长的对象数组。

```typescript
// 良好：通过外键实现一对多
posts: defineTable({
  authorId: v.id("users"),
  title: v.string(),
}).index("by_authorId", ["authorId"]),

comments: defineTable({
  postId: v.id("posts"),
  authorId: v.id("users"),
  body: v.string(),
}).index("by_postId", ["postId"]),

// 多对多通过连接表实现
postTags: defineTable({
  postId: v.id("posts"),
  tagId: v.id("tags"),
})
  .index("by_postId", ["postId"])
  .index("by_tagId", ["tagId"]),
```

仅当数据有限、始终与父文档一起加载和更新时，才使用 `v.object` 或小 `v.array` 嵌入。用户的 `settings` 对象是一个好的嵌入。用户的 `posts` 数组不是：它会达到 8192 项的限制，并且每次编辑用户文档都会重写该数组。

## 系统字段

`_id: Id<"table">` 和 `_creationTime: number`（自纪元以来的毫秒数）存在于每个文档中。当函数返回整个文档时，在返回验证器中包含它们：

```typescript
returns: v.array(
  v.object({
    _id: v.id("tasks"),
    _creationTime: v.number(),
    userId: v.id("users"),
    title: v.string(),
    completed: v.boolean(),
  }),
),
```

除非你需要一个与插入时间不同的值，否则不要添加自己的 `createdAt`。

## 搜索和向量索引

像普通索引一样在表上声明。`filterFields` 必须是顶级字段。

```typescript
articles: defineTable({
  title: v.string(),
  body: v.string(),
  category: v.string(),
  embedding: v.array(v.number()),
})
  .searchIndex("search_body", {
    searchField: "body",
    filterFields: ["category"],
  })
  .vectorIndex("by_embedding", {
    vectorField: "embedding",
    dimensions: 1536,
    filterFields: ["category"],
  }),
```

在查询中使用 `withSearchIndex` 查询搜索索引。向量搜索仅在通过 `ctx.vectorSearch` 在动作中运行。

## 常见错误

| 错误 | 为什么会出错 | 应该怎么做 |
| --- | --- | --- |
| `withIndex("by_userId")` 而没有匹配的 `.index()` | 部署失败 | 首先在模式中声明索引 |
| 在 `["userId", "status"]` 上命名 `by_user` 的索引 | 隐藏了它覆盖的内容，容易误用 | `by_userId_and_status` |
| 在 `by_userId_and_status` 上查询 `status` 而没有 `userId` | 索引前缀规则 | 添加 `by_status` 或包含 `userId` |
| 向包含行的表添加 `newField: v.string()` | 现有文档验证失败 | `v.optional`，回填，然后要求 |
| `posts: v.array(v.object(...))` 在 `users` 上 | 8192 项限制，每次编辑都会产生写冲突 | 使用 `by_authorId` 的单独 `posts` 表 |
| `v.bigint()` | 已弃用 | `v.int64()` |
| 在 `defineTable` 中声明 `_id` 或 `_creationTime` | 被拒绝 | 它们是自动生成的 |
| `v.any()` 以快速前进 | 没有验证，没有类型 | 建模形状，或 `v.union` 的实际情况 |
| 使用 `v.union(v.string(), v.null())` 为新字段 | 旧文档完全缺少该键 | `v.optional(v.string())` |
| 存储一个 `Date` | 不是 Convex 值 | `v.number()` 毫秒时间戳 |

## 检查清单

- [ ] 模式位于 `convex/schema.ts` 并默认导出 `defineSchema(...)` 
- [ ] 每个表都有显式的字段验证器，除非有正当理由使用 `v.any()` 
- [ ] `convex/` 中的每个 `withIndex` 调用都有一个字段名称与 `.index()` 匹配的索引 
- [ ] 外键是 `v.id("table")`，子表上有索引 
- [ ] 父文档中没有无界对象数组 
- [ ] 添加到已有数据的表中的字段是 `v.optional` 
- [ ] 枚举和多态形状使用 `v.union` 的 `v.literal` 或 `v.object` 成员 
- [ ] 返回验证器在返回整个文档时包含 `_id` 和 `_creationTime` 
- [ ] `npx convex dev` 推送时没有模式验证错误

## 文档

- https://docs.convex.dev/llms.txt
- https://docs.convex.dev/database/schemas
- https://docs.convex.dev/database/indexes
- https://docs.convex.dev/database/types
- https://docs.convex.dev/database/reading-data
