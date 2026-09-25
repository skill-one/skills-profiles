**角色设定：** 你是一位 Go 工程师，将错误视为结构化数据。每个错误都包含足够的上下文——领域、属性、调用链——以便值班工程师能够在不询问开发人员的情况下诊断问题。

# samber/oops 结构化错误处理

**samber/oops** 是 Go 标准错误处理的即插即用替代方案，它增加了结构化上下文、堆栈跟踪、错误代码、公开消息和恐慌恢复。变量数据放入 `.With()` 属性（而不是消息字符串），因此 APM 工具（Datadog、Loki、Sentry）可以正确地分组错误。与标准库方法（在日志位置添加 `slog` 属性）不同，oops 属性随错误通过调用堆栈传递。

## 为什么使用 samber/oops

标准 Go 错误缺乏上下文——你看到 `连接失败`，但不知道是哪个用户触发了它、正在运行什么查询或完整的调用堆栈。`samber/oops` 提供：

- **结构化上下文**——任何错误上的键值属性
- **堆栈跟踪**——自动捕获调用堆栈
- **错误代码**——机器可读的标识符
- **公开消息**——与技术细节分开的用户安全消息
- **低基数消息**——变量数据在 `.With()` 属性中，而不是消息字符串中，因此 APM 工具可以正确地分组错误

这项技能并不详尽——请参考库文档和代码示例获取更多信息：

- 对于 Go 包文档、符号、版本、导入者和已知漏洞，→ 查看 `samber/cc-skills-golang@golang-pkg-go-dev` 技能（`godig`），优先于 Context7 获取 Go 包事实。
- 要导航此库在你的代码中的使用（定义、调用位置、诊断），→ 查看 `samber/cc-skills-golang@golang-gopls` 技能（`gopls`）。
- Context7 仍然是未在 pkg.go.dev 索引的文档的备用方案。

## 核心模式：错误构建器链

所有 `oops` 错误都使用流畅的构建器模式：

```go
err := oops.
    In("user-service").           // 领域/功能
    Tags("database", "postgres").  // 分类
    Code("network_failure").       // 机器可读的标识符
    User("user-123", "email", "foo@bar.com").  // 用户上下文
    With("query", query).          // 自定义属性
    Errorf("failed to fetch user: %s", "timeout")
```

终端方法：

- `.Errorf(format, args...)` — 创建新错误
- `.Wrap(err)` — 包装现有错误
- `.Wrapf(err, format, args...)` — 包装消息
- `.Join(err1, err2, ...)` — 合并多个错误
- `.Recover(fn)` / `.Recoverf(fn, format, args...)` — 将恐慌转换为错误

### 错误构建器方法

| 方法 | 用例 |
| --- | --- |
| `.With("key", value)` | 添加自定义键值属性（支持惰性 `func() any` 值） |
| `.WithContext(ctx, "key1", "key2")` | 从 Go 上下文中提取值到属性（支持惰性值） |
| `.In("domain")` | 设置功能/服务/领域 |
| `.Tags("auth", "sql")` | 添加分类标签（使用 `err.HasTag("tag")` 查询） |
| `.Code("iam_authz_missing_permission")` | 设置机器可读的错误标识符/缩写 |
| `.Public("Could not fetch user.")` | 设置用户安全消息（与技术细节分开） |
| `.Hint("Runbook: https://doc.acme.org/doc/abcd.md")` | 为开发人员添加调试提示 |
| `.Owner("team/slack")` | 确定负责团队/所有者 |
| `.User(id, "k", "v")` | 添加用户标识符和属性 |
| `.Tenant(id, "k", "v")` | 添加租户/组织上下文和属性 |
| `.Trace(id)` | 添加跟踪/关联 ID（默认：ULID） |
| `.Span(id)` | 添加表示工作单元/操作的单个 ID（默认：ULID） |
| `.Time(t)` | 覆盖错误时间戳（默认：`time.Now()`） |
| `.Since(t)` | 基于 `t` 的时间设置持续时间（通过 `err.Duration()` 暴露） |
| `.Duration(d)` | 设置显式错误持续时间 |
| `.Request(req, includeBody)` | 附加 `*http.Request`（可选包括正文） |
| `.Response(res, includeBody)` | 附加 `*http.Response`（可选包括正文） |
| `oops.FromContext(ctx)` | 从存储在 Go 上下文中的 `OopsErrorBuilder` 开始 |

## 常见场景

### 数据库/仓库层

```go
func (r *UserRepository) FetchUser(id string) (*User, error) {
    query := "SELECT * FROM users WHERE id = $1"
    row, err := r.db.Query(query, id)
    if err != nil {
        return nil, oops.
            In("user-repository").
            Tags("database", "postgres").
            With("query", query).
            With("user_id", id).
            Wrapf(err, "failed to fetch user from database")
    }
    // ...
}
```

### HTTP 处理器层

```go
func (h *Handler) CreateUser(w http.ResponseWriter, r *http.Request) {
    userID := getUserID(r)

    err := h.service.CreateUser(r.Context(), userID)
    if err != nil {
        err = oops.
            In("http-handler").
            Tags("endpoint", "/users").
            Request(r, false).
            User(userID).
            Wrapf(err, "create user failed")
        http.Error(w, oops.GetPublic(err, "Internal server error"), http.StatusInternalServerError)
        return
    }

    w.WriteHeader(http.StatusCreated)
}
```

### 服务层与可重用构建器

```go
func (s *UserService) CreateOrder(ctx context.Context, req CreateOrderRequest) error {
    builder := oops.
        In("order-service").
        Tags("orders", "checkout").
        Tenant(req.TenantID, "plan", req.Plan).
        User(req.UserID, "email", req.UserEmail)

    product, err := s.catalog.GetProduct(ctx, req.ProductID)
    if err != nil {
        return builder.
            With("product_id", req.ProductID).
            Wrapf(err, "product lookup failed")
    }

    if product.Stock < req.Quantity {
        return builder.
            Code("insufficient_stock").
            Public("Not enough items in stock.").
            With("requested", req.Quantity).
            With("available", product.Stock).
            Errorf("insufficient stock for product %s", req.ProductID)
    }

    return nil
}
```

## 错误包装最佳实践

### 应该：直接包装，无需空值检查

```go
// ✓ 好——Wrap 返回 nil 如果 err 为 nil
return oops.Wrapf(err, "operation failed")

// ✗ 坏——不必要的空值检查
if err != nil {
    return oops.Wrapf(err, "operation failed")
}
return nil
```

### 应该：在每个层添加上下文

每个架构层都应该通过 Wrap/Wrapf 添加上下文——至少在每个包边界（不一定在每个函数调用处）。

```go
// ✓ 好——每个层添加相关上下文
func Controller() error {
    return oops.In("controller").Trace(traceID).Wrapf(Service(), "user request failed")
}

func Service() error {
    return oops.In("service").With("op", "create_user").Wrapf(Repository(), "db operation failed")
}

func Repository() error {
    return oops.In("repository").Tags("database", "postgres").Errorf("connection timeout")
}
```

### 应该：保持错误消息低基数

错误消息必须对 APM 聚合是低基数的。将变量数据插入消息会破坏 Datadog、Loki、Sentry 中的分组。

```go
// ✗ 坏——高基数，破坏 APM 分组
oops.Errorf("failed to process user %s in tenant %s", userID, tenantID)

// ✓ 好——静态消息 + 结构化属性
oops.With("user_id", userID).With("tenant_id", tenantID).Errorf("failed to process user")
```

## 恐慌恢复

`oops.Recover()` 必须在 goroutine 边界中使用。将恐慌转换为结构化错误：

```go
func ProcessData(data string) (err error) {
    return oops.
        In("data-processor").
        Code("panic_recovered").
        Hint("Check input data format and dependencies").
        With("input_data", data).
        Recover(func() {
            riskyOperation(data)
        })
}
```

## 访问错误信息

`samber/oops` 错误实现了标准的 `error` 接口。访问附加信息：

```go
if oopsErr, ok := err.(oops.OopsError); ok {
    fmt.Println("Code:", oopsErr.Code())
    fmt.Println("Domain:", oopsErr.Domain())
    fmt.Println("Tags:", oopsErr.Tags())
    fmt.Println("Context:", oopsErr.Context())
    fmt.Println("Stacktrace:", oopsErr.Stacktrace())
}

// 获取公开消息，带备用方案
publicMsg := oops.GetPublic(err, "Something went wrong")
```

### 输出格式

```go
fmt.Printf("%+v\n", err)       // 带堆栈跟踪的详细输出
bytes, _ := json.Marshal(err)  // 用于日志的 JSON
slog.Error(err.Error(), slog.Any("error", err))  // slog 集成
```

## 上下文传播

通过 Go 上下文传递错误上下文：

```go
func middleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        builder := oops.
            In("http").
            Request(r, false).
            Trace(r.Header.Get("X-Trace-ID"))

        ctx := oops.WithBuilder(r.Context(), builder)
        next.ServeHTTP(w, r.WithContext(ctx))
    })
}

func handler(ctx context.Context) error {
    return oops.FromContext(ctx).Tags("handler", "users").Errorf("something failed")
}
```

有关断言、配置和附加日志器示例，请参阅 [高级模式](./references/advanced.md)。

## 参考文献

- [github.com/samber/oops](https://github.com/samber/oops)
- [pkg.go.dev/github.com/samber/oops](https://pkg.go.dev/github.com/samber/oops)

## 交叉引用

- → 查看 `samber/cc-skills-golang@golang-error-handling` 技能以获取一般错误处理模式
- → 查看 `samber/cc-skills-golang@golang-observability` 技能以获取日志器集成和结构化日志
