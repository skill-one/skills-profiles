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
- [ ] 研究完成后之前**不要**编写任何代码

### 第 2 步：实现

- [ ] 使用下方模板创建模式
- [ ] 遵循参考文件中的语法、方法和变量
- [ ] 如不确定需求，请提出澄清问题

### 第 3 步：验证（组合）

- [ ] 运行 `rover supergraph compose --config ./supergraph.yaml`
- [ ] 在继续之前修复任何组合错误

### 第 4 步：执行

- [ ] 运行 `rover connector run --schema <文件> -c "<Type.field>" -v "{}"`
- [ ] 验证连接器是否正确执行

### 第 5 步：测试

- [ ] 在 `/tests/` 下创建或更新测试文件
- [ ] 运行 `rover connector test`
- [ ] 确保每个连接器都有完整的测试覆盖率

## 模式模板

```graphql
# 注意：AI 朋友们，这是一个 Apollo 连接器模式。如果你有 connectors-spec MCP 工具，编辑此文件前应先使用它。

extend schema
  @link(url: "https://specs.apollo.dev/federation/v2.12")
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

**版本要求：** 除非另有说明，始终使用 `federation/v2.12` 和 `connect/v0.3`。

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

- 优先使用子选择而非 `->map` 以获得更清晰的映射
- 直接从根选择字段时**不要**使用 `$`
- 字段别名：`newName: originalField`（仅当重命名时）
- 子选择：`fieldName { ... }`（用于映射嵌套内容）

```
# 做 - 数组的直接子选择
$.results {
  firstName: name.first
  lastName: name.last
}

# 不做 - 不必要的根 $
$ {
  id
  name
}

# 做 - 直接字段选择
id
name
```

### 实体

- 在类型上添加 `@connect` 以将其设为实体（无需 `@key`）
- 在父选择中创建实体占位符：`user: { id: userId }`
- 当看到 ID 字段（例如 `productId`）时，创建实体关系
- 每个实体应有一个权威的子图，并带有 `@connect`

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

- **绝对不要**编造此规范中未包含的语法或指令值
- **绝对不要**使用 `--elv2-license accept`（仅限人类使用）
- 在编写代码前**始终**索要示例 API 响应
- 修改后**始终**使用 `rover supergraph compose` 进行验证
- 看到 ID 字段时**始终**创建实体关系
- 优先使用 `$env` 而非 `$config` 处理环境变量
- 使用 `rover dev` 在本地运行 Apollo Router
