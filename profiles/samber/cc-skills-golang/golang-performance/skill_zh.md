**角色设定：** 你是一名 Go 性能工程师。你从不进行无先验分析就进行优化——测量、假设、改变一个因素、再测量。

**思考模式：** 尽可能彻底地进行性能优化思考——浅层分析会误判瓶颈，而深层推理能确保将正确的优化应用于正确的问题。在 Claude Code 中，使用 `ultrathink` 明确触发扩展思考。

**编排模式：** 将 Review 模式（架构）中描述的三个子代理（架构分配和内存布局、I/O 和并发、算法复杂性和缓存）发散开来，进行全面的架构性能审查。单个热点路径审查保持顺序执行；发散仅在包/服务范围内有效。在 Claude Code 中，使用 `ultracode` 明确选择多代理编排。

**模式：**

- **Review 模式（架构）** — 对包或服务进行结构反模式（缺少连接池、无界 goroutine、错误数据结构）的广泛扫描。使用最多 3 个并行子代理按关注点划分：(1) 分配和内存布局，(2) I/O 和并发，(3) 算法复杂性和缓存。
- **Review 模式（热点路径）** — 对调用者识别的单个函数或紧密循环进行聚焦分析。顺序工作；一个子代理就足够。
- **优化模式** — 通过性能分析已识别瓶颈。按迭代循环（定义指标 → 基线 → 诊断 → 改进 → 比较）顺序执行——一次一个变化是纪律。

**依赖项：**

- benchstat: `go install golang.org/x/perf/cmd/benchstat@latest`

# Go 性能优化

## 核心理念

1. **优化前先进行性能分析** — 对瓶颈的直觉判断有 80% 的情况是错误的。使用 pprof 找到实际的热点（→ See `samber/cc-skills-golang@golang-troubleshooting` 技能）
2. **减少分配能带来最大的投资回报** — Go 的 GC 很快但并非免费。减少每个请求的分配通常比微调 CPU 更重要
3. **记录优化** — 添加代码注释解释为什么某种模式更快，并在有可用时附上基准数据。未来的读者需要背景信息以避免撤销“不必要的”优化

## 首先排除外部瓶颈

在优化 Go 代码之前，验证瓶颈是否在你的流程中——如果 90% 的延迟是慢的数据库查询或 API 调用，减少分配将无济于事。

**诊断：** 1- `fgprof` — 捕获 CPU 和非 CPU（I/O 等待）时间；如果非 CPU 占主导，瓶颈是外部的 2- `go tool pprof`（goroutine 配置文件）— 许多 goroutine 被阻塞在 `net.(*conn).Read` 或 `database/sql` = 外部等待 3- 分布式追踪（OpenTelemetry）— 跨度分解显示哪个上游较慢

**外部瓶颈时：** 优化该组件——查询调优、缓存、连接池、断路器（→ See `samber/cc-skills-golang@golang-database` 技能，[缓存模式](references/caching.md)）。

## 迭代优化方法

### 循环：定义目标 → 基准测试 → 诊断 → 改进 → 基准测试

1. **定义你的指标** — 延迟、吞吐量、内存或 CPU？没有目标，优化是随机的
2. **编写原子基准测试** — 每个基准测试隔离一个函数以避免结果污染（→ See `samber/cc-skills-golang@golang-benchmark` 技能）
3. **测量基线** — `go test -bench=BenchmarkMyFunc -benchmem -count=6 ./pkg/... | tee /tmp/report-1.txt`
4. **诊断** — 使用每个深度分析部分的 **诊断** 行选择正确的工具
5. **改进** — 一次应用一个优化并附有解释性注释
6. **比较** — `benchstat /tmp/report-1.txt /tmp/report-2.txt` 以确认统计显著性
7. **提交** — 将 benchstat 输出粘贴到提交信息中，以便审查者和未来读者看到确切的改进；遵循 `perf(scope): summary` 提交类型
8. **重复** — 增加报告编号，处理下一个瓶颈

在发明自定义解决方案之前，参考库文档以了解已知模式。保留所有 `/tmp/report-*.txt` 文件作为审计轨迹。

当多个候选优化竞争同一瓶颈时，通过单独的子代理在隔离的工作树中实现每个优化——然后 → See `samber/cc-skills-golang@golang-benchmark` 技能比较变体及其串行测量注意事项（共享 CPU 上的并发基准测试会污染结果，即使实现本身是并行构建的）。

## 决策树：时间花在哪里？

| 瓶颈 | 信号（来自 pprof） | 操作 |
| --- | --- | --- |
| 分配过多 | 堆配置文件中 `alloc_objects` 高 | [内存优化](references/memory.md) |
| CPU 密集型热点循环 | 函数在 CPU 配置文件中占主导 | [CPU 优化](references/cpu.md) |
| GC 暂停 / OOM | GC 百分比过高，容器限制 | [运行时调优](references/runtime.md) |
| 网络 / I/O 延迟 | goroutine 被阻塞在 I/O 上 | [I/O & 网络编程](references/io-networking.md) |
| 重复昂贵的工作 | 多次进行相同的计算/获取 | [缓存模式](references/caching.md) |
| 算法错误 | 存在 O(n) 时使用 O(n²) | [算法复杂性](references/caching.md#algorithmic-complexity) |
| 锁竞争 | mutex/阻塞配置文件热点 | → See `samber/cc-skills-golang@golang-concurrency` 技能 |
| 慢查询 | 数据库时间在追踪中占主导 | → See `samber/cc-skills-golang@golang-database` 技能 |

## 常见错误

| 错误 | 修复 |
| --- | --- |
| 无先验分析就优化 | 首先使用 pprof 进行分析——直觉判断有 80% 的情况是错误的 |
| 默认 `http.Client` 而无 Transport | `MaxIdleConnsPerHost` 默认为 2；设置为匹配你的并发级别 |
| 热点循环中记录日志 | 记录调用会阻止内联并分配，即使级别被禁用。使用 `slog.LogAttrs` |
| 使用 `panic`/`recover` 作为控制流 | panic 分配一个堆栈跟踪并展开堆栈；使用错误返回 |
| 无基准证明就使用 `unsafe` | 仅在性能分析显示在验证的热路径中改进 >10% 时才合理 |
| 容器中无 GC 调优 | 将 `GOMEMLIMIT` 设置为容器内存的 80-90% 以防止 OOM 杀死 |
| 生产中使用 `reflect.DeepEqual` | 比类型比较慢 50-200 倍；使用 `slices.Equal`，`maps.Equal`，`bytes.Equal` |

## 深入分析

- [内存优化](references/memory.md) — 分配模式、后备数组泄漏、sync.Pool、结构体对齐
- [CPU 优化](references/cpu.md) — 内联、缓存局部性、虚假共享、ILP、反射避免
- [I/O & 网络编程](references/io-networking.md) — HTTP 传输配置、流式传输、JSON 性能、cgo、批量操作
- [运行时调优](references/runtime.md) — GOGC、GOMEMLIMIT、GC 诊断、GOMAXPROCS、PGO
- [缓存模式](references/caching.md) — 算法复杂性、编译模式、singleflight、工作避免
- [生产可观察性](references/observability.md) — Prometheus 指标、PromQL 查询、持续性能分析、告警规则

## CI 回归检测

在 CI 中自动化基准测试比较，以在它们到达生产之前捕获回归。→ See `samber/cc-skills-golang@golang-benchmark` 技能的 `benchdiff` 和 `cob` 设置。

## 交叉引用

- → See `samber/cc-skills-golang@golang-benchmark` 技能进行基准测试方法、`benchstat` 和 `b.Loop()`（Go 1.24+）
- → See `samber/cc-skills-golang@golang-troubleshooting` 技能进行 pprof 工作流、逃逸分析诊断和性能调试
- → See `samber/cc-skills-golang@golang-data-structures` 技能进行切片/映射预分配和 `strings.Builder`
- → See `samber/cc-skills-golang@golang-concurrency` 技能进行工作池、`sync.Pool` API、goroutine 生命周期和锁竞争
- → See `samber/cc-skills-golang@golang-safety` 技能进行循环中的 defer、切片后备数组别名
- → See `samber/cc-skills-golang@golang-database` 技能进行连接池调优和批量处理
- → See `samber/cc-skills-golang@golang-observability` 技能进行生产中的持续性能分析
