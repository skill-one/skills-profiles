# Apollo Federation Schema Authoring

Apollo Federation 支持将多个 GraphQL API（子图）组合成一个统一的超图。

## Federation 2 Schema Setup

每个 Federation 2 子图都必须通过 `@link` 进行选择加入：

```graphql
extend schema
  @link(url: "https://specs.apollo.dev/federation/v2.12",
        import: ["@key", "@shareable", "@external", "@requires", "@provides"])
```

仅导入子图使用的指令。显示的版本 (`v2.12`) 是示例性的 — 在复制之前，请查看 [Federation 更新日志](https://www.apollographql.com/docs/graphos/schema-design/federated-schemas/reference/versions) 以获取当前支持的版本。

> 子图的 `@link` 版本是一个下限，而不是组合版本 — 请参阅 [Federation 版本](references/composition.md#federation-versions-floor-vs-composition) 获取完整说明。

## Core Directives Quick Reference

| 指令 | 目的 | 示例 |
|-----------|---------|---------|
| `@key` | 定义具有唯一键的实体 | `type Product @key(fields: "id")` |
| `@shareable` | 允许多个子图解析字段 | `type Position @shareable { x: Int! }` |
| `@external` | 引用来自另一个子图的字段 | `weight: Int @external` |
| `@requires` | 依赖于外部字段的计算字段 | `shippingCost: Int @requires(fields: "weight")` |
| `@provides` | 条件解析外部字段 | `@provides(fields: "name")` |
| `@override` | 将字段迁移到此子图 | `@override(from: "Products")` |
| `@inaccessible` | 隐藏于 API schema | `internalId: ID! @inaccessible` |
| `@interfaceObject` | 为实体接口添加字段 | `type Media @interfaceObject` |

## Reference Files

特定主题的详细文档：

- [指令](references/directives.md) - 所有联邦指令的语法、示例和规则
- [Schema Patterns](references/schema-patterns.md) - 多子图模式和配方
- [Composition](references/composition.md) - 组合规则、错误代码和调试

## Key Patterns

### 实体定义

```graphql
type Product @key(fields: "id") {
  id: ID!
  name: String!
  price: Int
}
```

### 跨子图的实体贡献

```graphql
# Products 子图
type Product @key(fields: "id") {
  id: ID!
  name: String!
  price: Int
}

# Reviews 子图
type Product @key(fields: "id") {
  id: ID!
  reviews: [Review!]!
  averageRating: Float
}
```

### 使用 @requires 的计算字段

```graphql
type Product @key(fields: "id") {
  id: ID!
  size: Int @external
  weight: Int @external
  shippingEstimate: String @requires(fields: "size weight")
}
```

### 使用 @shareable 的值类型

```graphql
type Money @shareable {
  amount: Int!
  currency: String!
}
```

### 实体占位符（无贡献的引用）

```graphql
type Product @key(fields: "id", resolvable: false) {
  id: ID!
}
```

## Ground Rules

- 始终使用 Federation 2.x 语法和 `@link` 指令
- 始终仅导入子图使用的指令
- 绝不使用 `@shareable` 而不确保所有子图对该字段的返回值相同
- 优先使用具有单个 ID 字段的 `@key` 进行简单实体识别
- 使用 `rover supergraph compose` 本地验证组合
- 使用 `rover subgraph check` 验证生产超图
