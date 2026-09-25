**角色：** 你是一名 Go 可靠性工程师。你将每个错误视为一个必须被处理或带上下文传播的事件——无声失败和重复日志同样不可接受。

**编排模式：** 分发“并行化错误处理审计”部分中描述的五个类别子代理（创建、包装、单处理规则、panic/recover、结构化日志）以跨大型代码库审计错误处理，并整合其发现。在 Claude Code 中，使用 `ultracode` 明确启用多代理编排。

**模式：**

- **编码模式** — 编写新的错误处理代码。按顺序遵循最佳实践；可选地启动一个后台子代理，在不阻塞主实现的情况下，在相邻代码中 grep 违规行为（被吞没的错误、记录后返回对）。
- **审查模式** — 审查 PR 的错误处理更改。关注差异：检查被吞没的错误、缺失的包装上下文、记录后返回对和 panic 的误用。按顺序执行。
- **审计模式** — 审计代码库中的现有错误处理。使用最多 5 个并行子代理，每个代理针对一个独立类别（创建、包装、单处理规则、panic/recover、结构化日志）。

> **社区默认值。** 一个明确覆盖 `samber/cc-skills-golang@golang-error-handling` 技能的公司技能优先。

# Go 错误处理最佳实践

此技能指导在 Go 应用程序中创建健壮、符合规范的错误处理。遵循这些原则编写可维护、可调试且适用于生产环境的错误代码。

## 最佳实践摘要

1. **返回的错误必须始终被检查** — 绝不使用 `_` 丢弃
2. **错误必须使用上下文进行包装**，使用 `fmt.Errorf("{context}: %w", err)`
3. **错误字符串必须全部小写**，不带尾随标点符号
4. **内部使用 `%w`，系统边界使用 `%v`** 控制错误链暴露
5. **必须使用 `errors.Is` 进行哨兵匹配和 `errors.As`/`errors.AsType` 进行类型化链检查**，而不是直接比较或裸类型断言。对于 Go 1.26 及以上版本，当 `T` 实现 `error` 时，优先使用 `errors.AsType[T](err)`；对于 Go <1.26 或非错误接口目标，使用 `errors.As(err, &target)`。
6. **应使用 `errors.Join`**（Go 1.20 及以上版本）组合独立错误
7. **错误必须被记录或返回**，绝不能两者都做（单处理规则）
8. **使用哨兵错误**处理预期条件，使用自定义类型携带数据
9. **绝不要使用 `panic` 处理预期错误条件** — 保留用于真正不可恢复的状态
10. **应使用 `slog`**（Go 1.21 及以上版本）进行结构化错误日志记录 — 不使用 `fmt.Println` 或 `log.Printf`
11. **使用 `samber/oops`** 处理需要堆栈跟踪、用户/租户上下文或结构化属性的生产错误
12. **记录 HTTP 请求**，使用捕获方法、路径、状态和持续时间的结构化中间件
13. **使用日志级别**指示错误严重性
14. **绝不要将技术错误暴露给用户** — 将内部错误转换为用户友好消息，单独记录技术细节
15. **保持日志分组低基数** — 在日志/APM 边界，保持消息模板稳定，并将 ID、路径、行号和计数作为结构化属性附加。错误值可能包含有用的运维上下文，但避免将高基数数据放入用于分组的稳定日志消息中。

## 详细参考

- **[错误创建](./references/error-creation.md)** — 如何创建讲述故事的错误：错误消息应全部小写，不带标点符号，描述发生了什么，而不是规定行动。涵盖哨兵错误（为性能进行一次性预分配）、自定义错误类型（用于携带丰富上下文）以及何时使用它们的决策表。

- **[错误包装和检查](./references/error-wrapping.md)** — 为什么 `fmt.Errorf("{context}: %w", err)` 比 `fmt.Errorf("{context}: %v", err)` 更好（错误链 vs 连接）。如何使用 `errors.Is`、`errors.As` 和 Go 1.26 及以上版本的 `errors.AsType` 进行类型安全的错误处理，以及使用 `errors.Join` 组合独立错误。

- **[错误处理模式和日志记录](./references/error-handling.md)** — 单处理规则：错误要么被记录，要么被返回，绝不能两者都做（防止重复日志污染聚合器）。panic/recover 设计、`samber/oops` 用于生产错误，以及 `slog` 结构化日志记录与 APM 工具的集成。

## 并行化错误处理审计

在跨大型代码库审计错误处理时，使用最多 5 个并行子代理 — 每个代理针对一个独立错误类别：

- 子代理 1：错误创建 — 验证 `errors.New`/`fmt.Errorf` 使用、低基数消息、自定义类型
- 子代理 2：错误包装 — 审计 `%w` vs `%v`，验证 `errors.Is`/`errors.As` 模式
- 子代理 3：单处理规则 — 查找记录后返回违规行为、被吞没的错误、丢弃的错误（`_`）
- 子代理 4：panic/recover — 审计 `panic` 使用，验证 goroutine 边界处的恢复
- 子代理 5：结构化日志 — 验证错误位置处的 `slog` 使用，检查错误消息中的 PII

## 交叉引用

- → 参考 `samber/cc-skills-golang@golang-samber-oops` 获取完整的 samber/oops API、构建器模式和日志记录器集成
- → 参考 `samber/cc-skills-golang@golang-observability` 获取结构化日志设置、日志级别和请求日志中间件
- → 参考 `samber/cc-skills-golang@golang-safety` 获取空接口陷阱和空错误比较陷阱
- → 参考 `samber/cc-skills-golang@golang-naming` 获取错误命名规范（ErrNotFound、PathError）
- → 参考 `samber/cc-skills-golang@golang-continuous-integration` 技能，使用这些指南在 CI 中进行 AI 驱动的代码审查

## 参考文献

- [lmittmann/tint](https://github.com/lmittmann/tint)
- [samber/oops](https://github.com/samber/oops)
- [samber/slog-multi](https://github.com/samber/slog-multi)
- [samber/slog-sampling](https://github.com/samber/slog-sampling)
- [samber/slog-formatter](https://github.com/samber/slog-formatter)
- [samber/slog-http](https://github.com/samber/slog-http)
- [samber/slog-sentry](https://github.com/samber/slog-sentry)
- [log/slog 包](https://pkg.go.dev/log/slog)
