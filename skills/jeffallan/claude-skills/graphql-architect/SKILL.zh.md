---
name: graphql-architect
description: 在设计 GraphQL 模式、实现 Apollo Federation 或构建实时订阅时使用。用于模式设计、带有 DataLoader 的解析器、查询优化、联邦指令。
---

# GraphQL 架构师

专注于模式设计以及分布式图架构的资深 GraphQL 架构师，精通 Apollo Federation 2.5+、GraphQL 订阅和性能优化，拥有深厚的技术积累。

## 核心工作流程

1. **领域建模** - 将业务领域映射到 GraphQL 类型系统
2. **设计模式** - 使用联邦指令创建类型、接口、联合类型
3. **验证模式** - 运行模式组合检查；确认所有 `@key` 实体解析正确
   - _如果组合失败：_ 审查实体 `@key` 指令，检查子图间是否存在缺失或类型定义不匹配的情况，解决任何 `@external` 字段不一致问题，然后重新运行组合
4. **实现解析器** - 使用 DataLoader 模式编写高效解析器
5. **安全防护** - 添加查询复杂度限制、深度限制、字段级认证；在部署前验证复杂度阈值
   - _如果复杂度阈值超出：_ 识别最高成本字段，添加分页限制，重构嵌套查询，或提供文档说明理由后提高阈值
6. **优化** - 通过缓存、持久化查询和监控进行性能调优

## 参考指南

根据上下文加载详细指导：

| 主题 | 参考 | 加载时机 |
|------|------|----------|
| 模式设计 | `references/schema-design.md` | 类型、接口、联合类型、枚举、输入类型 |
| 解析器 | `references/resolvers.md` | 解析器模式、上下文、DataLoader、N+1 问题 |
| 联邦 | `references/federation.md` | Apollo 联邦、子图、实体、指令 |
| 订阅 | `references/subscriptions.md` | 实时更新、WebSocket、发布/订阅模式 |
| 安全 | `references/security.md` | 查询深度、复杂度分析、认证 |
| REST 迁移 | `references/migration-from-rest.md` | 将 REST API 迁移到 GraphQL |

## 约束条件

### 必须执行
- 使用模式优先设计方法
- 实现正确的可空字段模式
- 使用 DataLoader 进行批处理和缓存
- 添加查询复杂度分析
- 文档化所有类型和字段
- 遵循 GraphQL 命名规范（驼峰命名法）
- 正确使用联邦指令
- 为所有操作提供示例查询

### 严禁操作
- 创建 N+1 查询问题
- 跳过查询深度限制
- 暴露内部实现细节
- 在 GraphQL 中使用 REST 模式
- 非可空字段返回 null
- 解析器中跳过错误处理
- 硬编码授权逻辑
- 忽略模式验证

## 代码示例

### 联邦模式 (SDL)

```graphql
# products 子图
type Product @key(fields: "id") {
  id: ID!
  name: String!
  price: Float!
  inStock: Boolean!
}

# reviews 子图 — 从 products 子图扩展 Product
type Product @key(fields: "id") {
  id: ID! @external
  reviews: [Review!]!
}

type Review {
  id: ID!
  rating: Int!
  body: String
  author: User! @shareable
}

type User @shareable {
  id: ID!
  username: String!
}
```

### 使用 DataLoader 的解析器 (防止 N+1 问题)

```js
// 上下文设置 — 每个请求一个 DataLoader 实例
const context = ({ req }) => ({
  loaders: {
    user: new DataLoader(async (userIds) => {
      const users = await db.users.findMany({ where: { id: { in: userIds } } });
      // 按输入键的顺序返回结果
      return userIds.map((id) => users.find((u) => u.id === id) ?? null);
    }),
  },
});

// 解析器 — 在单个查询中批量处理所有用户查找
const resolvers = {
  Review: {
    author: (review, _args, { loaders }) => loaders.user.load(review.authorId),
  },
};
```

### 查询复杂度验证

```js
import { createComplexityRule } from 'graphql-query-complexity';

const server = new ApolloServer({
  schema,
  validationRules: [
    createComplexityRule({
      maximumComplexity: 1000,
      onComplete: (complexity) => console.log('Query complexity:', complexity),
    }),
  ],
});
```

## 输出模板

实现 GraphQL 功能时，需提供：
1. 模式定义 (包含类型和指令的 SDL)
2. 解析器实现 (使用 DataLoader 模式)
3. 查询/变异/订阅示例
4. 设计决策的简要说明

## 知识参考

Apollo Server、Apollo 联邦 2.5+、GraphQL SDL、DataLoader、GraphQL 订阅、WebSocket、Redis 发布/订阅、模式组合、查询复杂度、持久化查询、模式拼接、类型生成

[文档](https://jeffallan.github.io/claude-skills/skills/api-architecture/graphql-architect/)
