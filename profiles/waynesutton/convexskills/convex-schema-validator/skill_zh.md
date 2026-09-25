# 凸函数模式验证器

在 Convex 中定义和验证数据库模式，包括正确的类型、索引配置、可选字段、联合类型以及模式迁移策略。

## 文档来源

在实施之前，不要假设；获取最新文档：

- 主要：https://docs.convex.dev/database/schemas
- 索引：https://docs.convex.dev/database/indexes
- 数据类型：https://docs.convex.dev/database/types
- 更广泛的背景：https://docs.convex.dev/llms.txt

## 说明

### 基本模式定义

```typescript
// convex/schema.ts
import { defineSchema, defineTable } from "convex/server";
import { v } from "convex/values";

export default defineSchema({
  users: defineTable({
    name: v.string(),
    email: v.string(),
    avatarUrl: v.optional(v.string()),
    createdAt: v.number(),
  }),
  
  tasks: defineTable({
    title: v.string(),
    description: v.optional(v.string()),
    completed: v.boolean(),
    userId: v.id("users"),
    priority: v.union(
      v.literal("low"),
      v.literal("medium"),
      v.literal("high")
    ),
  }),
});
```

### 验证器类型

| 验证器 | TypeScript 类型 | 示例 |
|-----------|----------------|---------|
| `v.string()` | `string` | `"hello"` |
| `v.number()` | `number` | `42`, `3.14` |
| `v.boolean()` | `boolean` | `true`, `false` |
| `v.null()` | `null` | `null` |
| `v.int64()` | `bigint` | `9007199254740993n` |
| `v.bytes()` | `ArrayBuffer` | 二进制数据 |
| `v.id("table")` | `Id<"table">` | 文档引用 |
| `v.array(v)` | `T[]` | `[1, 2, 3]` |
| `v.object({})` | `{ ... }` | `{ name: "..." }` |
| `v.optional(v)` | `T \| undefined` | 可选字段 |
| `v.union(...)` | `T1 \| T2` | 多种类型 |
| `v.literal(x)` | `"x"` | 精确值 |
| `v.any()` | `any` | 任何值 |
| `v.record(k, v)` | `Record<K, V>` | 动态键 |

### 索引配置

```typescript
export default defineSchema({
  messages: defineTable({
    channelId: v.id("channels"),
    authorId: v.id("users"),
    content: v.string(),
    sentAt: v.number(),
  })
    // 单字段索引
    .index("by_channel", ["channelId"])
    // 复合索引
    .index("by_channel_and_author", ["channelId", "authorId"])
    // 用于排序的索引
    .index("by_channel_and_time", ["channelId", "sentAt"]),
    
  // 全文搜索索引
  articles: defineTable({
    title: v.string(),
    body: v.string(),
    category: v.string(),
  })
    .searchIndex("search_content", {
      searchField: "body",
      filterFields: ["category"],
    }),
});
```

### 复杂类型

```typescript
export default defineSchema({
  // 嵌套对象
  profiles: defineTable({
    userId: v.id("users"),
    settings: v.object({
      theme: v.union(v.literal("light"), v.literal("dark")),
      notifications: v.object({
        email: v.boolean(),
        push: v.boolean(),
      }),
    }),
  }),

  // 对象数组
  orders: defineTable({
    customerId: v.id("users"),
    items: v.array(v.object({
      productId: v.id("products"),
      quantity: v.number(),
      price: v.number(),
    })),
    status: v.union(
      v.literal("pending"),
      v.literal("processing"),
      v.literal("shipped"),
      v.literal("delivered")
    ),
  }),

  // 用于动态键的记录类型
  analytics: defineTable({
    date: v.string(),
    metrics: v.record(v.string(), v.number()),
  }),
});
```

### 差异联合

```typescript
export default defineSchema({
  events: defineTable(
    v.union(
      v.object({
        type: v.literal("user_signup"),
        userId: v.id("users"),
        email: v.string(),
      }),
      v.object({
        type: v.literal("purchase"),
        userId: v.id("users"),
        orderId: v.id("orders"),
        amount: v.number(),
      }),
      v.object({
        type: v.literal("page_view"),
        sessionId: v.string(),
        path: v.string(),
      })
    )
  ).index("by_type", ["type"]),
});
```

### 可选与可空字段

```typescript
export default defineSchema({
  items: defineTable({
    // 可选：字段可能不存在
    description: v.optional(v.string()),
    
    // 可空：字段存在但可以是 null
    deletedAt: v.union(v.number(), v.null()),
    
    // 可选且可空
    notes: v.optional(v.union(v.string(), v.null())),
  }),
});
```

### 索引命名约定

始终在索引名称中包含所有索引字段：

```typescript
export default defineSchema({
  posts: defineTable({
    authorId: v.id("users"),
    categoryId: v.id("categories"),
    publishedAt: v.number(),
    status: v.string(),
  })
    // 良好：描述性名称
    .index("by_author", ["authorId"])
    .index("by_author_and_category", ["authorId", "categoryId"])
    .index("by_category_and_status", ["categoryId", "status"])
    .index("by_status_and_published", ["status", "publishedAt"]),
});
```

### 模式迁移策略

#### 添加新字段

```typescript
// 之前
users: defineTable({
  name: v.string(),
  email: v.string(),
})

// 之后 - 首先作为可选添加
users: defineTable({
  name: v.string(),
  email: v.string(),
  avatarUrl: v.optional(v.string()), // 新的可选字段
})
```

#### 填充数据

```typescript
// convex/migrations.ts
import { internalMutation } from "./_generated/server";
import { v } from "convex/values";

export const backfillAvatars = internalMutation({
  args: {},
  returns: v.number(),
  handler: async (ctx) => {
    const users = await ctx.db
      .query("users")
      .filter((q) => q.eq(q.field("avatarUrl"), undefined))
      .take(100);

    for (const user of users) {
      await ctx.db.patch(user._id, {
        avatarUrl: `https://api.dicebear.com/7.x/initials/svg?seed=${user.name}`,
      });
    }

    return users.length;
  },
});
```

#### 将可选字段设为必需

```typescript
// 第一步：填充所有 null 值
// 第二步：更新模式设为必需
users: defineTable({
  name: v.string(),
  email: v.string(),
  avatarUrl: v.string(), // 填充后设为必需
})
```

## 示例

### 完整的电子商务模式

```typescript
// convex/schema.ts
import { defineSchema, defineTable } from "convex/server";
import { v } from "convex/values";

export default defineSchema({
  users: defineTable({
    email: v.string(),
    name: v.string(),
    role: v.union(v.literal("customer"), v.literal("admin")),
    createdAt: v.number(),
  })
    .index("by_email", ["email"])
    .index("by_role", ["role"]),

  products: defineTable({
    name: v.string(),
    description: v.string(),
    price: v.number(),
    category: v.string(),
    inventory: v.number(),
    isActive: v.boolean(),
  })
    .index("by_category", ["category"])
    .index("by_active_and_category", ["isActive", "category"])
    .searchIndex("search_products", {
      searchField: "name",
      filterFields: ["category", "isActive"],
    }),

  orders: defineTable({
    userId: v.id("users"),
    items: v.array(v.object({
      productId: v.id("products"),
      quantity: v.number(),
      priceAtPurchase: v.number(),
    })),
    total: v.number(),
    status: v.union(
      v.literal("pending"),
      v.literal("paid"),
      v.literal("shipped"),
      v.literal("delivered"),
      v.literal("cancelled")
    ),
    shippingAddress: v.object({
      street: v.string(),
      city: v.string(),
      state: v.string(),
      zip: v.string(),
      country: v.string(),
    }),
    createdAt: v.number(),
    updatedAt: v.number(),
  })
    .index("by_user", ["userId"])
    .index("by_user_and_status", ["userId", "status"])
    .index("by_status", ["status"]),

  reviews: defineTable({
    productId: v.id("products"),
    userId: v.id("users"),
    rating: v.number(),
    comment: v.optional(v.string()),
    createdAt: v.number(),
  })
    .index("by_product", ["productId"])
    .index("by_user", ["userId"]),
});
```

### 在函数中使用模式类型

```typescript
// convex/products.ts
import { query, mutation } from "./_generated/server";
import { v } from "convex/values";
import { Doc, Id } from "./_generated/dataModel";

// 使用 Doc 类型用于完整文档
type Product = Doc<"products">;

// 使用 Id 类型用于引用
type ProductId = Id<"products">;

export const get = query({
  args: { productId: v.id("products") },
  returns: v.union(
    v.object({
      _id: v.id("products"),
      _creationTime: v.number(),
      name: v.string(),
      description: v.string(),
      price: v.number(),
      category: v.string(),
      inventory: v.number(),
      isActive: v.boolean(),
    }),
    v.null()
  ),
  handler: async (ctx, args): Promise<Product | null> => {
    return await ctx.db.get(args.productId);
  },
});
```

## 最佳实践

- 除非明确指示，否则不要运行 `npx convex deploy`
- 除非明确指示，否则不要运行任何 git 命令
- 始终定义明确的模式，而不是依赖推断
- 使用包含所有索引字段的描述性索引名称
- 添加新列时从可选字段开始
- 使用差异联合处理多态数据
- 在模式级别验证数据，而不仅仅是在函数中
- 根据查询模式规划索引策略

## 常见陷阱

1. **缺少查询索引** - 每个与 `withIndex` 需要相应的模式索引
2. **索引字段顺序错误** - 字段必须按定义的顺序查询
3. **过度使用 `v.any()`** - 失去类型安全优势
4. **未将新字段设为可选** - 破坏现有数据
5. **忘记系统字段** - `_id` 和 `_creationTime` 是自动生成的

## 参考

- Convex 文档：https://docs.convex.dev/
- Convex LLMs.txt：https://docs.convex.dev/llms.txt
- 模式：https://docs.convex.dev/database/schemas
- 索引：https://docs.convex.dev/database/indexes
- 数据类型：https://docs.convex.dev/database/types
