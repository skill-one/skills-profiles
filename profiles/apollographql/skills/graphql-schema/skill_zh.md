# GraphQL 架构设计指南

本指南涵盖了设计直观、高效且可维护的 GraphQL 架构的最佳实践。架构设计主要是一个服务器端的问题，它直接影响 API 的可用性。

## 架构设计原则

### 1. 以客户端需求为设计依据

- 考虑客户端将编写哪些查询
- 按用例组织类型，而不是数据库表
- 揭示功能，而非实现细节

### 2. 保持明确性

- 使用清晰、描述性的名称
- 使可空性具有明确意图
- 使用描述进行文档记录

### 3. 设计以演进为目标

- 规划向后兼容性
- 在移除之前使用弃用
- 避免破坏性变更

## 快速参考

### 类型定义语法

```graphql
"""
系统中的用户。
"""
type User {
  id: ID!
  email: String!
  name: String
  posts(first: Int = 10, after: String): PostConnection!
  createdAt: DateTime!
}
```

### 可空性规则

| 模式 | 含义 |
|------|------|
| String | 可空 - 可能是 null |
| String! | 非可空 - 始终有值 |
| [String] | 可空列表，可空项 |
| [String!] | 可空列表，非可空项 |
| [String]! | 非可空列表，可空项 |
| [String!]! | 非可空列表，非可空项 |

**最佳实践：** 使用 **[Type!]!** 定义列表 - 空列表优于 null，项不为 null。

### 输入类型与输出类型

```graphql
# 输出类型 - 客户端接收的数据
type User {
  id: ID!
  email: String!
  createdAt: DateTime!
}

# 输入类型 - 客户端发送的数据
input CreateUserInput {
  email: String!
  name: String
}

# 使用输入类型的变异
type Mutation {
  createUser(input: CreateUserInput!): User!
}
```

### 接口模式

```graphql
interface Node {
  id: ID!
}

type User implements Node {
  id: ID!
  email: String!
}

type Post implements Node {
  id: ID!
  title: String!
}
```

### 联合模式

```graphql
union SearchResult = User | Post | Comment

type Query {
  search(query: String!): [SearchResult!]!
}
```

## 参考文件

特定主题的详细文档：

- [类型](references/types.md) - 类型设计模式、接口、联合和自定义标量
- [命名](references/naming.md) - 类型、字段和参数的命名规范
- [分页](references/pagination.md) - 连接模式和基于游标的分页
- [错误处理](references/errors.md) - 错误建模和结果类型
- [安全](references/security.md) - 架构设计的最佳安全实践

## 关键规则

### 类型设计

- 基于领域概念定义类型，而非数据存储
- 使用接口定义跨类型的共享字段
- 使用联合定义互斥类型
- 保持类型专注（单一职责）
- 避免深层嵌套 - 尽可能扁平化

### 字段设计

- 从客户端角度命名字段
- 返回尽可能具体的类型
- 使昂贵字段显式化（考虑参数）
- 使用参数进行过滤、排序、分页

### 变异设计

- 使用单一输入参数模式：`mutation(input: InputType!)`
- 在变异响应中返回受影响的对象
- 基于业务操作而非 CRUD 模型变异
- 考虑返回成功/错误类型的联合

### ID 策略

- 尽可能使用全局唯一 ID
- 实现 `Node` 接口以支持重新获取
- 如有需要，对复合 ID 进行 Base64 编码

## 基本规则

- 必须为类型和字段添加描述
- 必须对不能为 null 的字段使用非可空（**!**）
- 必须使用 **[Type!]!** 模式定义列表
- 绝不暴露数据库内部细节
- 绝不未经弃用就破坏向后兼容性
- 优先使用专用输入类型而非多个参数
- 优先使用枚举而非任意字符串定义固定值
- 使用 `ID` 类型定义标识符，而非 `String` 或 `Int`
- 使用自定义标量定义领域特定值（DateTime、Email、URL）
