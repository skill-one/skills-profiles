> **社区默认值。** 公司技能中明确覆盖 `samber/cc-skills-golang@golang-context` 技能的技能优先级更高。

# Go context.Context 最佳实践

`context.Context` 是 Go 用于跨 API 边界和 goroutine 传播取消信号、截止日期和请求范围值的机制。将其视为请求的“会话”——它将属于同一工作单元的所有操作联系在一起。

## 最佳实践摘要

1.  在整个请求生命周期中传递相同的上下文：HTTP 处理程序 → 服务 → 数据库 → 外部 API — 任何启动新上下文的链接在客户端消失后仍然有效。
2.  将 `ctx` 作为第一个参数，命名为 `ctx context.Context` — 固定位置使上下文感知 API 一目了然，并且 linter 会检查。
3.  通过函数参数传递上下文，而不是将其存储在结构体中 — 结构体比填充它的请求存活时间更长，因此后续调用会重用已经取消或属于其他人的上下文。
4.  使用 `context.TODO()` 而不是 `nil` 上下文 — `nil` 在第一次调用 `Done()` 或 `Value()` 时会引发恐慌，远在传递它的调用者之外。
5.  在所有控制流路径上调用 `cancel()`，除非上下文和取消函数的所有权明确返回或转移 — 未调用的 `cancel()` 会将子上下文保留在其父上下文中，直到父上下文完成，从而泄漏其计时器。
6.  仅在顶层入口点（main、init、测试）创建 `context.Background()`。在调用链深处——尤其是在请求中途——它会将工作与调用者的截止日期和取消分离，显示以下传播中断。
7.  当需要上下文但尚无上下文时，使用 `context.TODO()` 作为占位符——它标记了后续修复的间隙，而不是在看似故意的 `Background()` 后面隐藏它。
8.  将上下文值键声明为未导出的类型——使用普通的 `string` 键时，两个包使用 `"user"` 会无声地互相覆盖。
9.  在上下文值中仅携带请求范围元数据，绝不在函数参数中——通过 `Value()` 获取的值会丢失编译时类型并从函数签名中消失。
10. 当启动必须比父请求存活的后台工作时，使用 `context.WithoutCancel`（Go 1.21+）——否则返回的处理程序会取消刚刚开始的审计日志或清理工作。

## 创建上下文

| 情况 | 使用 |
| --- | --- |
| 入口点（main、init、测试） | `context.Background()` |
| 函数需要上下文但调用者尚未提供 | `context.TODO()` |
| 在 HTTP 处理程序内部 | `r.Context()` |
| 需要取消控制 | `context.WithCancel(parentCtx)` |
| 需要截止日期/超时 | `context.WithTimeout(parentCtx, duration)` |

## 上下文传播：核心原则

最重要的规则：**在整个调用链中传播相同的上下文**。当你正确传播时，取消父上下文会自动取消所有下游工作。

```go
// ✗ 坏的——创建新的上下文，破坏了链
func (s *OrderService) Create(ctx context.Context, order Order) error {
    return s.db.ExecContext(context.Background(), "INSERT INTO orders ...", order.ID)
}

// ✓ 好的——传递调用者的上下文
func (s *OrderService) Create(ctx context.Context, order Order) error {
    return s.db.ExecContext(ctx, "INSERT INTO orders ...", order.ID)
}
```

## 深入探讨

- **[取消、超时与截止日期](./references/cancellation.md)** — 取消如何传播：`WithCancel` 用于手动取消，`WithTimeout` 用于在持续时间后自动取消，`WithDeadline` 用于绝对时间截止日期。并发代码中监听 (`<-ctx.Done()`) 的模式，`AfterFunc` 回调，以及 `WithoutCancel` 用于必须比父请求存活的操作（例如，审计日志）。

- **[上下文值与跨服务跟踪](./references/values-tracing.md)** — 安全的上下文值模式：未导出的键类型以防止命名空间冲突，何时使用上下文值（请求 ID、用户 ID）与函数参数。跟踪上下文传播：OpenTelemetry 跟踪头、用于日志聚合的关联 ID，以及跨服务边界序列化/反序列化上下文。

- **[HTTP 服务器与服务调用中的上下文](./references/http-services.md)** — HTTP 处理程序上下文：`r.Context()` 用于请求范围取消、中间件集成以及传播到服务。HTTP 客户端模式：`NewRequestWithContext`、客户端超时，以及具有上下文感知的重试。数据库操作：始终使用 `*Context` 变体（`QueryContext`、`ExecContext`）以尊重截止日期。

## 跨参考

- → 参考使用上下文进行 goroutine 取消模式的 `samber/cc-skills-golang@golang-concurrency` 技能
- → 参考上下文感知数据库操作的 `samber/cc-skills-golang@golang-database` 技能（`QueryContext`、`ExecContext`）
- → 参考使用 OpenTelemetry 进行跟踪上下文传播的 `samber/cc-skills-golang@golang-observability` 技能
- → 参考使用超时和弹性模式的 `samber/cc-skills-golang@golang-design-patterns` 技能

## 使用 Linter 强制执行

许多上下文陷阱会自动被 linter 捕获：`govet`、`staticcheck`。→ 参考使用上下文 Linter 的 `samber/cc-skills-golang@golang-lint` 技能进行配置和使用。
