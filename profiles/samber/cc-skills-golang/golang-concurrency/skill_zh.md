**角色：** 你是一位 Go 并发工程师。你假设每个 goroutine 都是一笔负债，直到被证明是必要的——正确性和无泄漏性优先于性能。

**编排模式：** 分发“并发审计并行化”部分中描述的五个子代理，用于跨大型代码库审计并发代码，并将它们的发现结果汇总到一个报告中。在 Claude Code 中，使用 `ultracode` 明确启用多代理编排。

**模式：**

- **写入模式** — 实现并发代码（goroutine、通道、同步原语、工作池、管道）。遵循以下顺序指令。
- **审查模式** — 审查 PR 的并发代码更改。关注差异：检查 goroutine 泄漏、缺少上下文传播、所有权违规和保护不足的共享状态。顺序执行。
- **审计模式** — 审计代码库中的现有并发代码。使用“并发审计并行化”部分中描述的最多 5 个并行子代理。

> **社区默认值。** 一个明确覆盖 `samber/cc-skills-golang@golang-concurrency` 技能的公司技能优先。

# Go 并发最佳实践

Go 的并发模型基于 goroutine 和通道。Goroutine 很便宜，但不是免费的——你每个启动的 goroutine 都是一个你必须管理的资源。目标是结构化并发：每个 goroutine 都有明确的所有者、可预测的退出和正确的错误传播。

## 核心原则

1. **每个 goroutine 必须有明确的退出** — 没有关闭机制（上下文、done 通道、WaitGroup），它们会泄漏并累积，直到进程崩溃
2. **通过通信共享内存** — 通道明确转移所有权；互斥锁保护共享状态，但使所有权隐式化
3. **通道上发送副本，而不是指针** — 发送指针会创建看不见的共享内存，从而破坏通道的目的
4. **只有发送者关闭通道** — 从接收者端关闭会引发恐慌，如果发送者在关闭后写入
5. **指定通道方向** (`chan<-`, `<-chan`) — 编译器在构建时防止误用
6. **默认使用无缓冲通道** — 较大的缓冲区会掩盖背压；仅在有充分理由时使用它们
7. **在 select 中始终包含 `ctx.Done()`** — 没有它，goroutine 在调用者取消后会泄漏
8. **避免在热循环中重复 `time.After`** — 每次调用都会分配一个计时器并创建不必要的波动；对于长时间运行的循环，使用 `time.NewTimer` + `Reset`
9. **使用 `go.uber.org/goleak` 在测试中跟踪 goroutine 泄漏**

有关详细的通道/选择代码示例，请参阅 [通道和选择模式](references/channels-and-select.md)。

## 通道 vs 互斥锁 vs 原子操作

| 场景 | 使用 | 原因 |
| --- | --- | --- |
| 在 goroutine 之间传递数据 | 通道 | 通信所有权转移 |
| 协调 goroutine 生命周期 | 通道 + 上下文 | 清洁的退出，使用 select |
| 保护共享结构字段 | `sync.Mutex` / `sync.RWMutex` | 简单的临界区 |
| 简单计数器、标志 | `sync/atomic` | 无锁，较低开销 |
| 多个读取者、少量写入者对映射 | `sync.Map` | 优化读取密集型工作负载。**并发映射读写会导致硬崩溃** |
| 缓存昂贵计算 | `sync.Once` / `singleflight` | 执行一次或去重 |

## WaitGroup vs errgroup

| 需求 | 使用 | 原因 |
| --- | --- | --- |
| 等待 goroutine，不需要错误 | `sync.WaitGroup` | 瞬发 |
| 等待 + 收集第一个错误 | `errgroup.Group` | 错误传播 |
| 等待 + 出错时取消兄弟 | `errgroup.WithContext` | 上下文出错时取消 |
| 等待 + 限制并发 | `errgroup.SetLimit(n)` | 内置工作池 |

## 同步原语快速参考

| 原语 | 用例 | 关键点 |
| --- | --- | --- |
| `sync.Mutex` | 保护共享状态 | 保持临界区简短；不要跨 I/O 持有 |
| `sync.RWMutex` | 多个读取者、少量写入者 | 不要将 RLock 升级为 Lock（死锁） |
| `sync/atomic` | 简单计数器、标志 | 优先使用类型化的原子操作（Go 1.19+）：`atomic.Int64`, `atomic.Bool` |
| `sync.Map` | 并发映射，读取密集型 | 无显式锁定；当写入占主导地位时使用 `RWMutex`+映射 |
| `sync.Pool` | 重用临时对象 | 在 `Put()` 之前始终 `Reset()`；减少 GC 压力 |
| `sync.Once` | 一次性初始化 | Go 1.21+: `OnceFunc`, `OnceValue`, `OnceValues` |
| `sync.WaitGroup` | 等待简单的 goroutine | Go 1.25+: 优先使用 `wg.Go(func(){ ... })` 用于瞬发等待任务，这些任务不会恐慌，也不需要错误传播。对于 Go <1.25 使用 `Add`/`Done`。对于错误/取消/限制，使用 `errgroup` 与上下文一起使用。 |
| `x/sync/singleflight` | 去重并发调用 | 防止缓存雪崩 |
| `x/sync/errgroup` | goroutine 组 + 错误 | `SetLimit(n)` 替代手动的工人池 |

有关详细示例和反模式，请参阅 [同步原语深入解析](references/sync-primitives.md)。

## 并发检查清单

在启动 goroutine 之前回答：

- [ ] **它将如何退出？** — 上下文取消、通道关闭或显式信号
- [ ] **我能让它停止吗？** — 传递 `context.Context` 或 done 通道
- [ ] **我能等待它吗？** — `sync.WaitGroup` 或 `errgroup`
- [ ] **谁拥有通道？** — 创建者/发送者拥有并关闭
- [ ] **这个应该改为同步吗？** — 不要在没有充分理由的情况下添加并发

## 管道和工作池

有关管道模式（扇出/扇入、有界工作池、生成器链、Go 1.23+ 迭代器、`samber/ro`），请参阅 [管道和工作池](references/pipelines.md)。

## 并发审计并行化

在跨大型代码库审计并发时，使用最多 5 个并行子代理：

1. 查找所有 goroutine 启动（`go func`, `go method`）并验证关闭机制
2. 搜索可变全局变量和没有同步的共享状态
3. 审计通道使用——所有权、方向、关闭、缓冲区大小
4. 查找循环中的 `time.After`、select 中缺少 `ctx.Done`、无界启动
5. 检查互斥锁使用、`sync.Map`、原子操作和线程安全文档

## 常见错误

| 错误 | 修复 |
| --- | --- |
| 瞬发 goroutine | 提供停止机制（上下文、done 通道） |
| 从接收者关闭通道 | 只有发送者关闭 |
| 热循环中的 `time.After` | 重用 `time.NewTimer` + `Reset` |
| select 中缺少 `ctx.Done()` | 始终在上下文中选择以允许取消 |
| 无界 goroutine 启动 | 使用 `errgroup.SetLimit(n)` 或信号量 |
| 通过通道共享指针 | 发送副本或不可变值 |
| `wg.Add` 在 goroutine 内部 | 在 `go` 之前调用 `Add` — 否则 `Wait` 可能提前返回 |
| 忘记在 CI 中添加 `-race` | 始终运行 `go test -race ./...` |
| 跨 I/O 持有互斥锁 | 保持临界区简短 |

## 跨参考

- → 查看 `samber/cc-skills-golang@golang-performance` 技能以了解伪共享、缓存行填充、`sync.Pool` 热路径模式
- → 查看 `samber/cc-skills-golang@golang-context` 技能以了解取消传播和超时模式
- → 查看 `samber/cc-skills-golang@golang-safety` 技能以了解并发映射访问和竞争条件预防
- → 查看 `samber/cc-skills-golang@golang-troubleshooting` 技能以调试 goroutine 泄漏和死锁
- → 查看 `samber/cc-skills-golang@golang-design-patterns` 技能以了解优雅关闭模式
- → 查看 `samber/cc-skills-golang@golang-continuous-integration` 技能以了解使用这些指南在 CI 中进行自动 AI 驱动的代码审查

### Goroutine 泄漏分析

Goroutine 泄漏分析（在 Go 1.26 中通过 `GOEXPERIMENT=goroutineleakprofile` 可用）自 Go 1.27 起通常在 `runtime/pprof` 中可用——不需要构建标志。它是有用的生产导向泄漏信号，与以下现有工具一起使用。

```bash
curl http://localhost:6060/debug/pprof/goroutineleak?debug=2
go tool pprof http://localhost:6060/debug/pprof/goroutineleak
```

保留现有工具：

- 测试：`go.uber.org/goleak`
- 运行时计数：`runtime.NumGoroutine()`
- 栈转储：`/debug/pprof/goroutine?debug=2`
- 竞争检查：`go test -race ./...`

## 参考

- [Go 并发模式：管道](https://go.dev/blog/pipelines)
- [有效 Go：并发](https://go.dev/doc/effective_go#concurrency)
