**角色设定：** 你是一名 Go GraphQL 工程师。你精心设计模式，批量访问数据库以防止 N+1 问题，并在生产环境中将查询复杂度限制视为非可选项。

**模式：**

- **构建模式** — 生成新的模式、解析器或服务器设置：遵循技能的顺序指令；在生成新代码前，启动后台代理以 grep 现有解析器模式和命名规范。
- **审查模式** — 审计 GraphQL 代码库或 PR：使用子代理并行扫描 N+1 解析器模式、缺失复杂度限制、全局 DataLoaders 以及生产环境中启用的内省，同时阅读业务逻辑。

> **社区默认设置。** 公司技能会明确覆盖 `samber/cc-skills-golang@golang-graphql` 技能。

# Go GraphQL 最佳实践

两个主要库都是模式优先：编写 SDL（`.graphql` 文件），绑定 Go 解析器。根据项目规模和团队偏好进行选择。

此技能并非详尽无遗 — 请参考每个库的官方文档和代码示例以获取当前 API 签名：

- 对于 Go 包文档、符号、版本、导入器和已知漏洞，→ 查看 `samber/cc-skills-golang@golang-pkg-go-dev` 技能（`godig`），优先于 Context7 以获取 Go 包事实。
- 要导航此库在你的代码中的使用（定义、调用位置、诊断），→ 查看 `samber/cc-skills-golang@golang-gopls` 技能（`gopls`）。
- Context7 仍然是未在 pkg.go.dev 索引的文档的回退选项。

## 库选择

| 库 | 方法 | 类型安全 | 构建步骤 | 适用于 |
| --- | --- | --- | --- | --- |
| `github.com/99designs/gqlgen` | 代码生成 | 编译时 | `go generate` | 大型模式、联合、严格类型 |
| `github.com/graph-gophers/graphql-go` | 反射 | 解析时 | 无 | 简单模式、快速迭代 |
| `github.com/graphql-go/graphql` | 模式优先 | 运行时 | 无 | **避免** — 繁琐、无 SDL |

选择 **gqlgen** 的情况：需要 Apollo 联合，模式较大（100+ 类型），或团队希望生成存根且无反射开销。

选择 **graph-gophers** 的情况：模式为小/中型，构建管道应保持简单，或需要动态模式。

有关每个库的深入探讨，请参阅 [gqlgen 参考](./references/gqlgen.md) 和 [graphql-go 参考](./references/graphql-go.md)。

## 模式设计

```graphql
# ✓ 良好 — 明确空值；ID 标量用于不透明的标识符
type User {
  id: ID!
  email: String! # 非空：服务器始终可以返回此值
  bio: String # 可空：可能未设置
  posts(first: Int = 10, after: String): PostConnection!
}

# ✗ 不良 — Int ID 泄露实现细节，破坏客户端缓存
type Post {
  id: Int!
}
```

**空值规则：** 仅当服务器始终可以返回值时，才标记字段 `!`。非空字段的解析器错误会使父对象为空，导致级联失败；可空字段仅使字段本身为空。

**分页：** 使用 Relay 光标连接（`Connection`/`Edge`/`PageInfo`）用于列表字段。避免在大型数据集上使用偏移量分页 — 光标在并发写入下是稳定的。

**变更：** 将结果包装在包类型中，以便客户端在部分结果中接收业务错误，而不会污染 GraphQL `errors` 数组：

```graphql
type CreateUserPayload {
  user: User
  errors: [UserError!]!
}
```

## 解析器模式

保持解析器精简 — 它将 GraphQL 输入转换为领域调用，并将领域响应转换为 GraphQL 输出。

```go
// ✓ 良好 — 解析器委托给服务层
func (r *mutationResolver) CreateUser(ctx context.Context, input model.CreateUserInput) (*model.CreateUserPayload, error) {
    user, err := r.userService.Create(ctx, input.Email, input.Name)
    if err != nil {
        return nil, formatError(err)
    }
    return &model.CreateUserPayload{User: toGQLUser(user)}, nil
}

// ✗ 不良 — 解析器中包含 SQL，无关注点分离
func (r *queryResolver) User(ctx context.Context, id string) (*model.User, error) {
    row := r.db.QueryRowContext(ctx, "SELECT * FROM users WHERE id = $1", id)
    // ...
}
```

使用按类型解析器结构（`userResolver`，`postResolver`）而不是所有字段的单个庞大解析器。

## N+1 防范（DataLoaders）

每个 `User.posts` 解析器为每个用户触发一个 SQL 查询而不进行批处理 — O(n) 数据库调用对于 n 个用户。DataLoaders 通过将每个字段的加载合并为单个批处理查询来解决这个问题。

**关键规则：DataLoaders 必须在 HTTP 中间件中按请求创建，绝不能全局创建。** 全局 DataLoader 会跨请求缓存 — 过期数据，潜在的用户间数据泄露。

```go
// ✓ 良好 — 中间件中的按请求 DataLoader
func DataLoaderMiddleware(db *sql.DB, next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        loaders := &Loaders{
            PostsByUserID: newPostsByUserIDLoader(r.Context(), db),
        }
        ctx := context.WithValue(r.Context(), loadersKey, loaders)
        next.ServeHTTP(w, r.WithContext(ctx))
    })
}

// ✗ 不良 — 全局 DataLoader 跨所有请求共享
var globalLoader = newPostsByUserIDLoader(context.Background(), db)
```

在 gqlgen 中，使用 `resolver: true` 在 `gqlgen.yml` 中标记批处理字段以强制执行专用解析器方法。有关完整的 DataLoader 连接，请参阅 [gqlgen 参考](./references/gqlgen.md)。

## 身份验证和授权

双层模型：

1. **HTTP 中间件** — 提取和验证令牌，将身份存储在 `context.Context` 中。
2. **模式指令**（gqlgen）或 **解析器检查**（graphql-go） — 强制执行按字段授权。

```go
// HTTP 中间件层（两个库）
func AuthMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        token := r.Header.Get("Authorization")
        user, err := validateToken(token)
        if err != nil {
            http.Error(w, "Unauthorized", http.StatusUnauthorized)
            return
        }
        ctx := context.WithValue(r.Context(), userKey, user)
        next.ServeHTTP(w, r.WithContext(ctx))
    })
}
```

在 gqlgen 中，使用 `@hasRole` 模式指令进行字段级授权 — 授权策略存在于模式中，而不是分散在解析器中。请参阅 [gqlgen 参考](./references/gqlgen.md)。

## 错误处理

绝不能返回原始内部错误 — 它们会向客户端泄露 SQL 消息、堆栈跟踪或服务内部细节。

```go
// gqlgen — 自定义 ErrorPresenter 删除内部细节
srv.SetErrorPresenter(func(ctx context.Context, err error) *gqlerror.Error {
    var gqlErr *gqlerror.Error
    if errors.As(err, &gqlErr) {
        return gqlErr // 已经格式化
    }
    // 在此处记录内部 err
    return gqlerror.Errorf("内部错误") // 安全的客户端消息
})

// 添加扩展代码以进行客户端错误处理
return nil, &gqlerror.Error{
    Message: "用户未找到",
    Extensions: map[string]any{"code": "NOT_FOUND"},
}
```

对于 graph-gophers，实现 `ResolverError` 接口以附加 `Extensions()`。请参阅 [graphql-go 参考](./references/graphql-go.md)。

使用 `graphql.AddError(ctx, err)` 在 gqlgen 中处理非致命字段错误，其中解析器仍可以返回部分数据。

有关错误包装模式，请参阅 `samber/cc-skills-golang@golang-error-handling` 技能。

## 订阅

订阅使用长连接 WebSocket。关键纪律：**始终尊重上下文取消** — 每个断开连接的客户端泄漏的 goroutine 会静默耗尽资源。

```go
// ✓ 良好 — 客户端断开连接时关闭通道
func (r *subscriptionResolver) MessageAdded(ctx context.Context, room string) (<-chan *model.Message, error) {
    ch := make(chan *model.Message, 1)
    sub := r.pubsub.Subscribe(room) // 在 goroutine 之前订阅一次
    go func() {
        defer close(ch) // 始终关闭；通知迭代停止
        for {
            select {
            case <-ctx.Done():
                return // 客户端断开连接
            case msg := <-sub:
                select {
                case ch <- msg:
                case <-ctx.Done():
                    return
                }
            }
        }
    }()
    return ch, nil
}

// ✗ 不良 — 客户端断开连接时 goroutine 泄漏
func (r *subscriptionResolver) MessageAdded(ctx context.Context, room string) (<-chan *model.Message, error) {
    ch := make(chan *model.Message, 1)
    go func() {
        for msg := range r.pubsub.Subscribe(room) {
            ch <- msg // 客户端消失后阻塞永久
        }
    }()
    return ch, nil
}
```

## 性能和安全

生产环境中的 GraphQL 服务器需要显式限制。如果没有限制，单个深度嵌套查询会耗尽 CPU 和内存。

```go
// gqlgen — 将这些连接到每个生产处理程序
srv := handler.NewDefaultServer(es)
srv.Use(extension.FixedComplexityLimit(200)) // 每个查询的最大成本

// 限制内省 — 仅在非生产环境中
if os.Getenv("ENV") != "production" {
    srv.Use(extension.Introspection{})
}
```

对于 graph-gophers：`graphql.MaxDepth(10)` 和 `graphql.MaxParallelism(10)` 选项在 `ParseSchema` 时设置。

**查询允许列表：** 在生产环境中，考虑持久化查询（gqlgen APQ 扩展）以拒绝任意查询字符串。

## 常见错误

| 错误 | 重要性 | 修复 |
| --- | --- | --- |
| 子解析器中的 N+1 查询 | 每个父行一个 SQL → O(n) 数据库调用 | 使用按请求 DataLoader |
| 全局 DataLoader | 跨请求缓存 — 过期数据，数据泄露 | 在请求中间件中创建 DataLoader |
| 直接编辑 `models_gen.go` | 下次 `go generate` 擦除手动编辑 | 使用 `autobind` 或 `models.<T>.model` 在 `gqlgen.yml` 中 |
| 模式更改后忘记 `go generate` | 编译时解析器接口不匹配 | 重新运行 `go tool gqlgen generate` |
| graph-gophers 解析器中的 `int` 字段 | 库要求 `int32` 用于 `Int` 标量 | 使用 `int32`（或 `float64` 用于 `Float`） |
| 生产环境中启用内省 | 向攻击者暴露完整模式 | 使用 `ENV` 检查进行限制 |
| 无复杂度限制 | 深度嵌套查询 → CPU/内存拒绝服务攻击 | `extension.FixedComplexityLimit(N)` |
| 从解析器泄漏 DB 错误 | 向客户端泄露 SQL 内部细节 | 包装在 `ErrorPresenter` / `ResolverError` 中 |
| 订阅 goroutine 泄漏 | 客户端断开连接 → goroutine 永久运行 | `defer close(ch)` + `select ctx.Done()` |
| 可空字段用于始终必需的数据 | 客户端必须到处进行空值检查 | 在模式中标记 `!`；解析器返回错误 |

## 深入探讨

- **[gqlgen 参考](./references/gqlgen.md)** — 代码生成工作流，`gqlgen.yml`，DataLoaders，联合 v2，指令
- **[graphql-go 参考](./references/graphql-go.md)** — 反射解析器模型，类型映射，跟踪
- **[测试](./references/testing.md)** — gqlgen 客户端套件，gqltesting，httptest 模式

## 交叉引用

- → 查看 `samber/cc-skills-golang@golang-context` 技能以获取解析器和订阅中的上下文传播
- → 查看 `samber/cc-skills-golang@golang-error-handling` 技能以获取错误包装和哨兵模式
- → 查看 `samber/cc-skills-golang@golang-testing` 技能以获取表格驱动和集成测试模式
- → 查看 `samber/cc-skills-golang@golang-observability` 技能以获取解析器中的跟踪和指标
- → 查看 `samber/cc-skills-golang@golang-security` 技能以获取输入验证和注入预防
- → 查看 `samber/cc-skills-golang@golang-database` 技能以获取 N+1 查询模式和数据库批处理
- → 查看 `samber/cc-skills-golang@golang-graphql` 技能以获取 GraphQL 代码库审查

## 参考

- [gqlgen](https://github.com/99designs/gqlgen)
- [graph-gophers/graphql-go](https://github.com/graph-gophers/graphql-go)
- [Relay 光标连接规范](https://relay.dev/graphql/connections.htm)

如果你在 gqlgen 中遇到错误或意外行为，请在新问题中打开 <https://github.com/99designs/gqlgen/issues>。

如果你在 graph-gophers/graphql-go 中遇到错误或意外行为，请在新问题中打开 <https://github.com/graph-gophers/graphql-go/issues>。
