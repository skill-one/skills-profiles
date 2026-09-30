---
name: apollo-connectors
description: '将 REST API 集成到 GraphQL 超图中的 Apollo Connectors 指南，使用 @source 和 @connect 指令。当用户：(1) 提及“连接器”、“Apollo Connectors”或“REST 连接器”；(2) 想要将 REST API 集成到 GraphQL 中；(3) 引用 @source 或 @connect 指令；(4) 处理包含“# Note to AI Friends: This is an Apollo Connectors schema”注释的文件时，请使用此技能。'
---

# Apollo 连接器模式助手

## MCP 工具

如果可用，请使用 GraphOS MCP 工具：
- **connectors-spec**：在开始任何连接器工作前，获取完整的 Connectors 规范
- **apollo_docs_search**：搜索相关文档
- **apollo_docs_read**：通过 slug 读取特定文档页面

**按主题划分的文档路径：**
- 请求：`/graphos/connectors/requests/url`、`/headers`、`/body`、`/batching`
- 响应：`/graphos/connectors/responses/fields`、`/error-handling`
- 映射：`/graphos/connectors/mapping`、`/arrays`、`/enums`、`/literals`
- 实体：`/graphos/connectors/entities`、`/patterns`

## 流程

遵循以下 5 步流程。**绝对不要跳过任何步骤。**

### 第 1 步：研究

- [ ] 了解被调用的 API 及响应结构
- [ ] 如果未提供，请向用户索要示例 API 响应
- [ ] 从 MCP 工具或参考文件中获取相关文档
- [ ] 研究完成后之前**绝对不要**编写任何代码

### 第 2 步：实现

- [ ] 使用下方模板创建模式
- [ ] 遵循参考文件中的语法、方法和变量
- [ ] 如果不确定需求，请提出澄清问题

### 第 3 步：验证（组合）

- [ ] 运行 `rover supergraph compose --config ./supergraph.yaml`
- [ ] 在继续之前修复任何组合错误

### 第 4 步：执行

- [ ] 运行 `rover connector run --schema <file> -c "<Type.field>" -v "{}"`
- [ ] 验证连接器是否正确执行

### 第 5 步：测试

- [ ] 在 `/tests/` 下创建或更新测试文件
- [ ] 运行 `rover connector test`
- [ ] 确保每个连接器都有完整的测试覆盖率

## 模式模板

```graphql
# 注意：AI 朋友们，这是一个 Apollo 连接器模式。如果你有 connectors-spec MCP 工具，请在编辑此文件前使用它。

extend schema
  @link(url: "https://specs.apollo.dev/federation/v2.15")
  @link(url: "https://specs.apollo.dev/connect/v0.3", import: ["@source", "@connect"])

@source(name: "api_name", http: { baseURL: "https://api.example.com" })

type Query {
  example(id: ID!): Example
    @connect(
      source: "api_name"
      http: { GET: "/example/{$args.id}" }
      selection: """
      id
      name
      """
    )
}

type Example {
  id: ID!
  name: String
}
```

## 版本要求

使用 Apollo Federation 和 Apollo Connectors 的最新长期支持 (LTS) 版本。只有在用户明确要求时，才使用预览版或实验性规范。

在编写 `@link` URL 或 `federation_version` 之前，请先确认当前的 LTS。当 GraphOS 文档工具可用时，请优先使用它们：

- **Federation**：阅读 `/graphos/schema-design/federated-schemas/reference/versions` 并使用标记为 LTS 的最高版本。该版本是模式 `@link` (`https://specs.apollo.dev/federation/vX.Y`)。在 `supergraph.yaml` 中将 `federation_version` 设置为该相同 LTS 行的最新补丁版本。
- **Connectors**：阅读 `/graphos/connectors/getting-started/version-requirements` 和 `/graphos/connectors/reference/changelog`。使用最新且通常可用的 Connectors 规范（未标记为实验性）且与该 Federation LTS 兼容的版本 (`https://specs.apollo.dev/connect/vX.Y`)。

上述模板使用了当前的 LTS：Federation `v2.15` 和 Connectors `v0.3`。如果文档列出了更新的 LTS，请使用文档。

## 参考文件

在实现连接器之前，请阅读相关参考文件：

- [语法](references/grammar.md) - 选择映射 EBNF 语法
- [方法](references/methods.md) - 可用的转换方法
- [变量](references/variables.md) - 可用的映射变量
- [实体](references/entities.md) - 实体模式和批处理
- [验证](references/validation.md) - 用于验证的 Rover 命令
- [故障排除](references/troubleshooting.md) - 常见错误和解决方案

## 关键规则

### 选择映射

- 优先使用子选择而不是 `->map` 以获得更清晰的映射
- 直接从根选择字段时**绝对不要**使用 `$`
- 字段别名：`newName: originalField`（仅在重命名时使用）
- 子选择：`fieldName { ... }`（用于映射嵌套内容）

```
# DO - 数组的直接子选择
$.results {
  firstName: name.first
  lastName: name.last
}

# DO NOT - 不必要的根 $
$ {
  id
  name
}

# DO - 直接字段选择
id
name
```

### 实体

- 在类型上添加 `@connect` 以将其转换为实体（无需 `@key`）
- 在父选择中创建实体存根：`user: { id: userId }`
- 当你看到 ID 字段（例如 `productId`）时，创建实体关系
- 每个实体应有一个**唯一**的权威子图，并带有 `@connect`

### 字面值

在映射中使用 `$()` 包装器处理字面值：

```
$(1)              # 数字
$(true)           # 布尔值
$("hello")        # 字符串
$({"a": "b"})     # 对象

# 在 body 中
body: "$({ a: $args.a })"  # 正确
body: "{ a: $args.a }"     # 错误 - 将无法组合
```

### Headers

```graphql
http: {
  GET: "/api"
  headers: [
    { name: "Authorization", value: "Bearer {$env.API_KEY}" },
    { name: "X-Forwarded", from: "x-client" }
  ]
}
```

### 批处理

使用 `$batch` 转换 N+1 模式：

```graphql
type Product @connect(
  source: "api"
  http: {
    POST: "/batch"
    body: "ids: $batch.id"
  }
  selection: "id name"
) {
  id: ID!
  name: String
}
```

## 基本规则

- **绝对不要**编造此规范中未提及的语法或指令值
- **绝对不要**使用 `--elv2-license accept`（仅限人类使用）
- 在编写代码前**绝对要**向用户索要示例 API 响应
- 在更改后**绝对要**使用 `rover supergraph compose` 进行验证
- 当你看到 ID 字段时**绝对要**创建实体关系
- 优先使用 `$env` 而不是 `$config` 处理环境变量
- 使用 `rover dev` 在本地运行 Apollo Router
