---
name: golang-samber-ro
description: 使用samber/ro在Golang中实现响应式流和事件驱动编程 — ReactiveX实现，包含150+类型安全的操作符、冷/热可观察对象、5种主题类型（发布、行为、重播、异步、单播）、通过Pipe实现的声明式管道、40+插件（HTTP、cron、fsnotify、JSON、日志记录）、自动背压、错误传播以及Go上下文集成。适用于使用或采用samber/ro时、当代码库导入github.com/samber/ro时，或构建Go中的异步事件驱动管道、实时数据处理、流或响应式架构。不适用于有限切片转换（→参见`samber/cc-skills-golang@golang-samber-lo`技能）。
---

**角色设定：** 当数据异步或无限流动时，你是一位 Go 工程师，会使用反应式流。你使用 samber/ro 来构建声明式管道，而不是手动进行 goroutine/channel 的连接，但你清楚何时一个简单的切片 + samber/lo 就足够了。

**思考模式：** 在设计高级反应式管道或选择冷/热可观察对象、主题以及组合运算符时，尽可能彻底地思考——错误的架构会导致资源泄漏或错过事件。在 Claude Code 中，使用 `ultrathink` 明确触发扩展思考。

# samber/ro — Go 的反应式流

ReactiveX 的 Go 实现。泛型优先、类型安全的可组合管道，用于异步数据流，具有自动背压、错误传播、上下文集成和资源清理功能。150+ 运算符，5 种主题类型，40+ 插件。

**官方资源：**

- [github.com/samber/ro](https://github.com/samber/ro)
- [ro.samber.dev](https://ro.samber.dev)
- [pkg.go.dev/github.com/samber/ro](https://pkg.go.dev/github.com/samber/ro)

这项技能并不详尽——请参考库文档和代码示例获取更多信息：

- 对于 Go 包文档、符号、版本、导入者和已知漏洞，→ 查看 `samber/cc-skills-golang@golang-pkg-go-dev` 技能（`godig`），优先于 Context7 获取 Go 包事实。
- 要导航此库在你自己的代码中的使用（定义、调用位置、诊断），→ 查看 `samber/cc-skills-golang@golang-gopls` 技能（`gopls`）。
- Context7 仍然是未在 pkg.go.dev 索引的文档的备用方案。

## 为什么使用 samber/ro（流 vs 切片）

Go 通道 + goroutine 在复杂的异步管道中变得难以管理：手动通道关闭、冗长的 goroutine 生命周期、嵌套 select 中的错误传播以及不可组合的运算符。`samber/ro` 通过声明式、可链式流运算符解决这个问题。

**何时使用哪种工具：**

| 场景 | 工具 | 原因 |
| --- | --- | --- |
| 转换切片（map、filter、reduce） | `samber/lo` | 有限、同步、急切——不需要流开销 |
| 简单的 goroutine 扇出（带错误处理） | `errgroup` | 标准库，轻量级，足以处理有界并发 |
| 无限事件流（WebSocket、计时器、文件监视器） | `samber/ro` | 带有背压、重试、超时、组合的声明式管道 |
| 从多个异步源实时数据丰富 | `samber/ro` | CombineLatest/Zip 组合依赖流，无需手动 select |
| 多个消费者共享一个源的发布/订阅 | `samber/ro` | 热可观察对象（Share/Subjects）原生支持多播 |

**lo 与 ro 的主要区别**

| 方面 | `samber/lo` | `samber/ro` |
| --- | --- | --- |
| 数据 | 有限切片 | 无限流 |
| 执行 | 同步、阻塞 | 异步、非阻塞 |
| 评估 | 急切（分配中间切片） | 懒惰（按到达顺序处理） |
| 时间 | 立即 | 时间感知（延迟、节流、间隔、超时） |
| 错误模型 | 每次调用返回 `(T, error)` | 错误通道通过管道传播 |
| 用例 | 集合转换 | 事件驱动、实时、异步管道 |

## 安装

```bash
go get github.com/samber/ro
```

## 核心概念

四个构建模块：

1. **可观察对象** — 随时间发出值的数源。默认为冷：每个订阅者从零开始独立执行
2. **观察者** — 具有三个回调的消费者：`onNext(T)`、`onError(error)`、`onComplete()`
3. **运算符** — 将一个可观察对象转换为另一个可观察对象的函数，通过 `Pipe` 链接
4. **订阅** — 可观察对象和观察者之间的连接。调用 `.Wait()` 阻塞或 `.Unsubscribe()` 取消

```go
observable := ro.Pipe2(
    ro.RangeWithInterval(0, 5, 1*time.Second),
    ro.Filter(func(x int) bool { return x%2 == 0 }),
    ro.Map(func(x int) string { return fmt.Sprintf("even-%d", x) }),
)

observable.Subscribe(ro.NewObserver(
    func(s string) { fmt.Println(s) },      // onNext
    func(err error) { log.Println(err) },    // onError
    func() { fmt.Println("Done!") },         // onComplete
))
// 输出: "even-0", "even-2", "even-4", "Done!"

// 或者同步收集：
values, err := ro.Collect(observable)
```

## 冷 vs 热 可观察对象

**冷**（默认）：每个 `.Subscribe()` 从零开始独立执行。安全且可预测——默认使用。

**热**：多个订阅者共享单个执行。当源昂贵（WebSocket、DB 轮询）或订阅者必须看到相同事件时使用。

| 转换方式 | 行为 |
| --- | --- |
| `Share()` | 冷 → 热，带引用计数。最后一个取消订阅时销毁 |
| `ShareReplay(n)` | 与 Share 相同 + 缓存最后 N 个值供晚到的订阅者使用 |
| `Connectable()` | 冷 → 热，但等待显式的 `.Connect()` 调用 |
| 主题 | 原生热——直接调用 `.Send()`、`.Error()`、`.Complete()` |

| 主题 | 构造函数 | 回放行为 |
| --- | --- | --- |
| `PublishSubject` | `NewPublishSubject[T]()` | 无——晚到的订阅者会错过过去的事件 |
| `BehaviorSubject` | `NewBehaviorSubject[T](initial)` | 重播最后一个值给新订阅者 |
| `ReplaySubject` | `NewReplaySubject[T](bufferSize)` | 重播最后 N 个值 |
| `AsyncSubject` | `NewAsyncSubject[T]()` | 仅在完成时发出最后一个值 |
| `UnicastSubject` | `NewUnicastSubject[T](bufferSize)` | 仅有一个订阅者 |

有关主题细节和热可观察对象模式，请参阅 [主题指南](./references/subjects-guide.md)。

## 运算符快速参考

| 类别 | 关键运算符 | 目的 |
| --- | --- | --- |
| 创建 | `Just`、`FromSlice`、`FromChannel`、`Range`、`Interval`、`Defer`、`Future` | 从各种源创建可观察对象 |
| 转换 | `Map`、`MapErr`、`FlatMap`、`Scan`、`Reduce`、`GroupBy` | 转换或累积流值 |
| 过滤 | `Filter`、`Take`、`TakeLast`、`Skip`、`Distinct`、`Find`、`First`、`Last` | 选择性发出值 |
| 组合 | `Merge`、`Concat`、`Zip2`–`Zip6`、`CombineLatest2`–`CombineLatest5`、`Race` | 合并多个可观察对象 |
| 错误处理 | `Catch`、`OnErrorReturn`、`OnErrorResumeNextWith`、`Retry`、`RetryWithConfig` | 从错误中恢复 |
| 时间控制 | `Delay`、`DelayEach`、`Timeout`、`ThrottleTime`、`SampleTime`、`BufferWithTime` | 控制发出时间 |
| 侧效应 | `Tap`/`Do`、`TapOnNext`、`TapOnError`、`TapOnComplete` | 观察，但不改变流 |
| 终端 | `Collect`、`ToSlice`、`ToChannel`、`ToMap` | 将流消耗为 Go 类型 |

使用带泛型的 `Pipe2`、`Pipe3` ... `Pipe25` 在运算符链中实现编译时类型安全。未带泛型的 `Pipe` 使用 `any` 并丢失类型检查。

有关完整的运算符目录（150+ 运算符及其签名），请参阅 [运算符指南](./references/operators-guide.md)。

## 常见错误

| 错误 | 原因 | 修复 |
| --- | --- | --- |
| 未使用错误处理器的 `ro.OnNext()` | 错误被静默丢弃——生产环境中的错误隐藏 | 使用 `ro.NewObserver(onNext, onError, onComplete)` 并提供所有三个回调 |
| 使用未带泛型的 `Pipe()` 而不是 `Pipe2`/`Pipe3` | 丢失编译时类型安全，错误在运行时出现 | 使用 `Pipe2`、`Pipe3`...`Pipe25` 进行带泛型的运算符链 |
| 忘记无限流上的 `.Unsubscribe()` | Goroutine 泄漏——可观察对象永远运行 | 使用 `TakeUntil(signal)`、上下文取消或显式 `Unsubscribe()` |
| 当冷足够时使用 `Share()` | 不必要的复杂性，生命周期更难推理 | 仅在多个消费者需要相同流时使用热可观察对象 |
| 使用 `samber/ro` 进行有限切片转换 | 流开销（goroutines、订阅）用于同步操作 | 使用 `samber/lo`——它更简单、更快，专为切片设计 |
| 未在管道中传播上下文以取消 | 流忽略关闭信号，终止时导致资源泄漏 | 在管道中链式 `ContextWithTimeout` 或 `ThrowOnContextCancel` |

## 最佳实践

1. **始终处理所有三个事件** — 使用 `NewObserver(onNext, onError, onComplete)`，而不仅仅是 `OnNext`。未处理的错误会导致静默数据丢失
2. **使用 `Collect()` 进行同步消费** — 当流有限且你需要 `[]T` 时，`Collect` 会阻塞直到完成并返回切片 + 错误
3. **优先使用带泛型的 Pipe 函数** — `Pipe2`、`Pipe3`...`Pipe25` 在编译时捕获类型不匹配。将未带泛型的 `Pipe` 用于动态运算符链
4. **有界无限流** — 使用 `Take(n)`、`TakeUntil(signal)`、`Timeout(d)` 或上下文取消。无界流泄漏 goroutines
5. **使用 `Tap`/`Do` 进行可观察性** — 记录、跟踪或计量发射，但不改变流。链式 `TapOnError` 进行错误监控
6. **优先使用 `samber/lo` 进行简单转换** — 如果数据是有限切片，并且你需要 Map/Filter/Reduce，使用 `lo`。当数据随时间到达、来自多个源或需要重试/超时/背压时，使用 `ro`

## 插件生态系统

40+ 插件通过特定领域的运算符扩展 ro：

| 类别 | 插件 | 导入路径前缀 |
| --- | --- | --- |
| 编码 | JSON、CSV、Base64、Gob | `plugins/encoding/...` |
| 网络 | HTTP、I/O、FSNotify | `plugins/http`、`plugins/io`、`plugins/fsnotify` |
| 调度 | Cron、ICS | `plugins/cron`、`plugins/ics` |
| 可观察性 | Zap、Slog、Zerolog、Logrus、Sentry、Oops | `plugins/observability/...`、`plugins/samber/oops` |
| 速率限制 | Native、Ulule | `plugins/ratelimit/...` |
| 数据 | Bytes、Strings、Sort、Strconv、Regexp、Template | `plugins/bytes`、`plugins/strings`、等 |
| 系统 | Process、Signal | `plugins/proc`、`plugins/signal` |

有关完整的插件目录、导入路径和使用示例，请参阅 [插件生态系统](./references/plugin-ecosystem.md)。

有关现实世界中的反应式模式（重试+超时、WebSocket 扇出、优雅关闭、流组合），请参阅 [模式](./references/patterns.md)。

如果你在 samber/ro 中遇到错误或意外行为，请在 [github.com/samber/ro/issues](https://github.com/samber/ro/issues) 打开问题。

## 交叉引用

- → 查看 `samber/cc-skills-golang@golang-samber-lo` 技能，用于有限切片转换（Map、Filter、Reduce、GroupBy）——当数据已经在一个切片中时使用 lo
- → 查看 `samber/cc-skills-golang@golang-samber-mo` 技能，用于单子类型（Option、Result、Either），可与 ro 管道组合
- → 查看 `samber/cc-skills-golang@golang-samber-hot` 技能，用于内存缓存（也作为 ro 插件提供）
- → 查看 `samber/cc-skills-golang@golang-concurrency` 技能，用于 goroutine/channel 模式，当反应式流过于复杂时
- → 查看 `samber/cc-skills-golang@golang-observability` 技能，用于监控生产环境中的反应式管道
