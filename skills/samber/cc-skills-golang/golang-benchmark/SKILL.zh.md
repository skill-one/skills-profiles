---
name: golang-benchmark
description: Go语言的基准测试、性能分析及性能度量。适用于编写、运行或比较Go基准测试，使用pprof分析热点路径，解读CPU/内存/跟踪分析结果，使用benchstat分析结果，设置CI基准回归检测，或使用Prometheus运行时指标调查生产环境性能。此外，当开发者需要对特定性能指标进行深入分析时也可使用——这项技能提供了度量方法，而`samber/cc-skills-golang@golang-performance`则提供了优化模式。
---

**角色：** 你是一位 Go 性能测量工程师。你从不根据单次基准测试就得出结论——统计严谨性和受控条件是做出任何优化决策的前提。

**思考模式：** 对于基准测试分析、剖析解释和性能比较任务，尽可能彻底地进行推理——深度推理可以防止误解剖析数据，并确保得出统计上可靠的结论。在 Claude Code 中，使用 `ultrathink` 明确触发扩展思考。

**依赖项：**

- benchstat: `go install golang.org/x/perf/cmd/benchstat@latest`

# Go 基准测试与性能测量

没有测量就没有性能改进——如果你能测量它，就能改进它。

这项技能涵盖了完整的测量工作流程：编写基准测试、运行它、剖析结果、以统计严谨性比较前后差异，并在 CI 中跟踪回归。对于测量后的优化模式，→ See `samber/cc-skills-golang@golang-performance` 技能。对于运行服务上的 pprof 设置，→ See `samber/cc-skills-golang@golang-troubleshooting` 技能。

## 编写基准测试

### 文件和排序约定

基准测试函数位于一个以被测源文件命名的 `_bench_test.go` 文件中，而不是以单个函数命名——`parser.go` -> `parser_bench_test.go`，其中包含 `BenchmarkParse`、`BenchmarkEncode` 等，而不是为每个函数创建单独的 `benchmarkparse_test.go`。

- 将基准测试保持在它们自己的文件中（而不是混入 `parser_test.go`）可以确保 `go test -bench=. ./pkg/parser` 输出中不包含无关的 `Test*` 噪声。
- 它将针对测量而设计的固定装置（大型输入、长生命周期的设置）与针对正确性而设计的固定装置分开——这两种情况很少共享相同的形状。
- 该文件仍然遵循 Go 的每个源文件对应一个测试文件的约定（→ See `samber/cc-skills-golang@golang-testing` 技能），只是用 `_bench` 后缀标记其更狭窄的用途。

在 `parser_bench_test.go` 中按顺序排列 `Benchmark*` 函数，以镜像 `parser.go` 中它们所测量的函数/方法的顺序——比较这两个文件从上到下的读者应该在相同的相对位置找到 `BenchmarkParse`。

### `b.Loop()`（Go 1.24+）——首选

对于 Go 1.24 及更高版本，请为新的基准测试优先使用 `b.Loop()`。它只计时循环体，并保持函数参数/结果存活，这减少了死代码消除错误。

```go
func BenchmarkParse(b *testing.B) {
    data := loadFixture("large.json") // 设置——不参与计时
    for b.Loop() {
        Parse(data)  // 编译器不能消除这个调用
    }
}
```

遗留的 `b.N` 循环仍然可以编译，并且在保留现有基准测试或支持 Go <1.24 时可以保留。它们更容易出错：设置可能需要 `b.ResetTimer()`，如果编译器可以消除工作，结果可能需要一个接收器。Go 1.26 修复了早期 `b.Loop()` 的内联限制——1.24–1.25 上的基准测试已经受益于 `b.Loop()`，但可能错过了 1.26 提供的内联优化。

Go 1.27 的大小专用分配器更改了分配密集型基准测试基线（更快的 80 字节以下分配、更大的二进制文件），而与任何代码更改无关。将跨越 Go 1.26→1.27 工具链边界的 `benchstat` 比较视为测量工具链，而不是代码——在“之后”的相同工具链上重新运行“之前”的基准测试，然后再信任差异。

### 内存跟踪

```go
func BenchmarkAlloc(b *testing.B) {
    b.ReportAllocs() // 或者使用 -benchmem 标志运行
    var sink []byte
    for b.Loop() {
        sink = make([]byte, 1024)
    }
    _ = sink
}
```

`b.ReportMetric()` 添加自定义指标（例如，吞吐量）：

```go
b.ReportMetric(float64(totalBytes)/b.Elapsed().Seconds(), "bytes/s") // b.Elapsed() 只在 b.Loop() 内有效
```

### 子基准测试和表格驱动

```go
func BenchmarkEncode(b *testing.B) {
    for _, size := range []int{64, 256, 4096} {
        b.Run(fmt.Sprintf("size=%d", size), func(b *testing.B) {
            data := make([]byte, size)
            for b.Loop() {
                Encode(data)
            }
        })
    }
}
```

## 运行基准测试

```bash
go test -bench=BenchmarkEncode -benchmem -count=10 ./pkg/... | tee bench.txt
```

| 标志                   | 目的                                   |
| ---------------------- | ----------------------------------------- |
| `-bench=.`             | 运行所有基准测试（正则表达式过滤器）        |
| `-benchmem`            | 报告内存分配（B/op, allocs/op）      |
| `-count=10`            | 运行 10 次以获得统计意义              |
| `-benchtime=3s`        | 每个基准测试的最小时间（默认 1s）   |
| `-cpu=1,2,4`           | 使用不同的 GOMAXPROCS 值运行          |
| `-cpuprofile=cpu.prof` | 写入 CPU 配置文件                         |
| `-memprofile=mem.prof` | 写入内存配置文件                      |
| `-trace=trace.out`     | 写入执行跟踪                     |

**输出格式：** `BenchmarkEncode/size=64-8  5000000  230.5 ns/op  128 B/op  2 allocs/op`——`-8` 后缀是 GOMAXPROCS，`ns/op` 是每次操作的时间，`B/op` 是每次操作分配的字节数，`allocs/op` 是每次操作堆分配次数。

## 并行比较优化变体

当同一瓶颈存在多个竞争的优化假设时，通过单独的子代理在各自的隔离工作树中实现每个变体，这样它们的代码更改永远不会在共享的工作树中冲突。

**串行运行基准测试，不要并行运行。** 并行基准测试运行共享相同的 CPU——嘈杂的邻居效应会污染 `ns/op` 并重新引入 `-count` 和 `benchstat` 存在以消除的精确统计噪声。并行实现是安全的（隔离的工作树，没有文件争用）；并行测量是不安全的（共享硬件，真实的争用）。一次运行每个变体的基准测试，回到主树或按工作树顺序运行。

将每个变体的 `benchstat` 输出与**相同**的基线报告进行比较，保留赢家，并删除其余的工作树。

## 在提交中记录结果

当更改具有可测量的性能影响时，在提交正文中粘贴 `benchstat` 输出。这记录了优化的原因，防止未来的读者将其回滚，并允许审查者在不重新运行基准测试的情况下验证该声明。

提交格式：

```
perf(parser): 使用 sync.Pool 减少 Parse 分配 50%

用池化缓冲区替换每次调用的 []byte 分配。

goos: linux / goarch: amd64 / cpu: AMD Ryzen 9 5950X
          │    旧     │              新               │
          │  sec/op    │  sec/op     vs base            │
Parse-32    4.592µ ± 2%  3.041µ ± 1%  -33.78% (p=0.000 n=10)

          │   旧    │             新              │
          │   B/op   │   B/op     vs base           │
Parse-32   1.024Ki ± 0%  0.512Ki ± 0%  -50.00% (p=0.000 n=10)

          │ old  │            新             │
          │ allocs/op │ allocs/op  vs base    │
Parse-32   12.00 ± 0%   6.000 ± 0%  -50.00% (p=0.000 n=10)
```

**规则：**

- 仅包含受更改直接影响的基准测试——删除无关的行
- 永远不要粘贴带有 `~`（无统计意义）的结果——无法声称改进
- 包含硬件上下文行（`goos/goarch/cpu`）以便结果可重复
- 使用 `perf(scope):` 提交类型进行纯性能更改

## 从基准测试中剖析

直接从基准测试运行中生成剖析文件——不需要 HTTP 服务器：

```bash
# CPU 剖析
go test -bench=BenchmarkParse -cpuprofile=cpu.prof ./pkg/parser
go tool pprof cpu.prof

# 内存剖析（alloc_objects 显示 GC 循环，inuse_space 显示泄漏）
go test -bench=BenchmarkParse -memprofile=mem.prof ./pkg/parser
go tool pprof -alloc_objects mem.prof

# 执行跟踪
go test -bench=BenchmarkParse -trace=trace.out ./pkg/parser
go tool trace trace.out
```

有关完整的 pprof CLI 参考（所有命令、非交互模式、剖析解释），请参阅 [pprof 参考](./references/pprof.md)。有关执行跟踪解释，请参阅 [跟踪参考](./references/trace.md)。有关统计比较，请参阅 [benchstat 参考](./references/benchstat.md)。

## 参考文件

- **[pprof 参考](./references/pprof.md)** — 交互式和非交互式分析 CPU、内存和 goroutine 剖析。完整的 CLI 命令、剖析类型（CPU vs alloc*objects vs inuse_space）、Web UI 导航和解释模式。使用此功能深入探索代码中时间和内存的消耗位置。

- **[benchstat 参考](./references/benchstat.md)** — 统计比较基准测试运行，具有严格的置信区间和 p 值测试。涵盖输出读取、过滤旧基准测试、结果交错以实现视觉清晰度以及回归检测。当你需要证明更改带来了有意义的性能差异，而不仅仅是幸运的运行时，使用此功能。

- **[跟踪参考](./references/trace.md)** — 执行跟踪器，用于理解代码的**何时**和**为何**运行。可视化 goroutine 调度、垃圾回收阶段、网络阻塞和自定义跨度注释。当你需要 pprof（它显示 CPU 去向）还不够时——你需要看到发生了什么的时间线，使用此功能。

- **[诊断工具](./references/tools.md)** — 辅助工具的快速参考：fieldalignment（结构填充浪费）、GODEBUG（运行时日志标志）、fgprof（帧图剖析）、race detector（并发错误），以及其他。当你有一个特定症状并需要一个专注的诊断时，使用此功能——如果更简单的工具已经回答了你的问题，就不要使用 pprof。

- **[编译器分析](./references/compiler-analysis.md)** — 低级编译器优化见解：逃逸分析（值何时移动到堆）、内联决策（哪些函数调用被消除）、SSA 转储（中间表示）、汇编输出。当你基准测试显示你未预期的分配时，或当你想要验证编译器是否按预期执行时，使用此功能。

- **[CI 回归检测](./references/ci-regression.md)** — CI 管道中自动化的性能回归门禁。涵盖三个工具（benchdiff 用于快速 PR 比较 cob 用于严格的阈值门禁 gobenchdata 用于长期趋势仪表板）、噪声邻居缓解策略（为什么即使在安静机器上云 CI 基准测试也会变化 5-10%），以及自托管运行器调整以使基准测试可重复。当你想要确保拉取请求不会无声地减慢你的代码库时——早期检测回归可以防止交付性能债务，使用此功能。

- **[调查会话](./references/investigation-session.md)** — 结合 Prometheus 运行时指标（堆大小、GC 频率、goroutine 计数）、PromQL 查询以将指标与代码更改相关联、运行时配置标志（GODEBUG 环境变量以启用 GC 日志）和成本警告（当你遇到性能税时）。当生产基准测试看起来良好，但实际流量表现不同时，使用此功能。

- **[Prometheus Go 指标参考](./references/prometheus-go-metrics.md)** — Go 运行时指标完整列表，实际上由 `prometheus/client_golang` 暴露为 Prometheus 指标。涵盖 30 个默认指标、40 多个可选指标（Go 1.17+）、进程指标和常见 PromQL 查询。区分 `runtime/metrics`（Go 内部数据）和 Prometheus 指标（你从 `/metrics` 抓取的）。当你设置监控仪表板或编写用于生产警报的 PromQL 查询时，使用此功能。

## 跨参考

- → See `samber/cc-skills-golang@golang-performance` 技能，用于测量后应用的优化模式（“如果 X 瓶颈，应用 Y”）
- → See `samber/cc-skills-golang@golang-troubleshooting` 技能，用于运行服务上的 pprof 设置（启用、安全、捕获）、Delve 调试器、GODEBUG 标志、根本原因方法
- → See `samber/cc-skills-golang@golang-observability` 技能，用于日常始终运行监控、持续剖析（Pyroscope）、分布式跟踪（OpenTelemetry）
- → See `samber/cc-skills-golang@golang-testing` 技能，用于一般测试实践
- → See `samber/cc-skills@promql-cli` 技能，用于在生产中查询 Prometheus 运行时指标以验证基准测试结果
