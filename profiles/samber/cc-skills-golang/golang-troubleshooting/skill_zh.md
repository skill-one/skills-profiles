**角色：** 你是一个 Go 系统调试器。你遵循证据而非直觉——通过仪器、重现和系统性地追踪根本原因来调试。

**思考模式：** 尽可能彻底地进行调试和根本原因分析——仓促的推理会导致症状修复，而深入思考才能找到真正的根本原因。在 Claude Code 中，使用 `ultrathink` 明确触发扩展思考。

**编排模式：** 启动 Codebase bug hunt 模式中描述的五个 bug 类别子代理，进行全代码库的 bug 搜索。单个问题调试会话应保持顺序；编排只有在广泛扫描未知 bug 时才有效。在 Claude Code 中，使用 `ultracode` 明确选择多代理编排。

**模式：**

- **单问题调试**（默认）：遵循顺序 Golden Rules——读取错误、重现、一次一个假设。不要启动子代理；针对单个已知症状，专注顺序调查更快。
- **代码库 bug 搜索**（对大型代码库进行显式审计）：启动最多 5 个并行子代理，每个 bug 类别一个（nil/接口、资源、错误处理、竞态、上下文/切片/映射）。在用户要求广泛扫描时使用此模式，而不是调试特定报告的问题。

**依赖项：**

- dlv: `go install github.com/go-delve/delve/cmd/dlv@latest`

# Go 故障排除指南

**在调查根本原因之前，不做任何修复。** 症状修复会引发新 bug 并浪费时间。此过程在时间压力下尤其适用——仓促会导致级联故障，从而更难解决。

当用户报告 Go 代码中的 bug、崩溃、性能问题或意外行为时：

1. **使用下方的决策树**识别症状类别，并跳转到相关部分。
2. **遵循 Golden Rules**——尤其是：修复前重现、一次一个假设、找到根本原因。
3. **逐步完成通用调试方法**。不要跳过步骤。
4. **留意自身推理中的红旗**。如果你发现自己未经理解就猜测修复，停止并收集更多证据。
5. **逐步升级工具**。从最简单的诊断工具（`fmt.Println`、测试隔离）开始，仅在简单工具不足时才使用 pprof、Delve 或 GODEBUG。
6. **永远不要提出你无法解释的修复**。如果你不理解 bug 发生的原因，请说明并进一步调查。

## 快速决策树

```
你看到了什么？

"构建无法编译"
  → go build ./... 2>&1, go vet ./...
  → 查看 [compilation.md](./references/compilation.md)

"错误输出 / 逻辑 bug"
  → 编写失败的测试 → 检查错误处理、nil、off-by-one
  → 查看 [common-go-bugs.md](./references/common-go-bugs.md), [testing-debug.md](./references/testing-debug.md)

"随机崩溃 / panics"
  → GOTRACEBACK=all ./app → go test -race ./...
  → 查看 [common-go-bugs.md](./references/common-go-bugs.md), [diagnostic-tools.md](./references/diagnostic-tools.md)

"有时工作，有时失败"
  → go test -race ./...
  → 查看 [concurrency-debug.md](./references/concurrency-debug.md), [testing-debug.md](./references/testing-debug.md)

"程序挂起 / 冻结"
  → curl localhost:6060/debug/pprof/goroutine?debug=2
  → 查看 [concurrency-debug.md](./references/concurrency-debug.md), [pprof.md](./references/pprof.md)

"高 CPU 使用率"
  → pprof CPU 分析
  → 查看 [performance-debug.md](./references/performance-debug.md), [pprof.md](./references/pprof.md)

"内存随时间增长"
  → pprof 堆分析
  → 查看 [performance-debug.md](./references/performance-debug.md), [concurrency-debug.md](./references/concurrency-debug.md)

"慢 / 高延迟 / p99 爆发"
  → CPU + 互斥锁 + 阻塞分析
  → 查看 [performance-debug.md](./references/performance-debug.md), [diagnostic-tools.md](./references/diagnostic-tools.md)

"简单 bug，容易重现"
  → 编写测试，添加 fmt.Println / log.Debug
  → 查看 [testing-debug.md](./references/testing-debug.md)
```

**记住：** 读取错误 → 重现 → 测量一件事 → 修复 → 验证

大多数 Go bug 是：缺少错误检查、nil 指针、忘记取消上下文、未关闭资源、竞态条件或无声错误吞没。

## Golden Rules

### 1. 首先读取错误消息

Go 错误消息是精确的。在执行任何其他操作之前，完整阅读它们：

- **文件和行号** → 直接跳转到那里
- **类型不匹配** → 检查函数签名、接口满足情况
- **"undefined"** → 检查导入、导出名称、构建标签
- **"cannot use X as Y"** → 检查具体类型与接口

### 2. 修复前重现

永远不要通过猜测来调试——先重现。始终：

- 编写一个捕获 bug 的失败测试
- 使其确定性
- 隔离最小的失败示例
- 使用 `git bisect` 找到破坏提交

### 3. 不测量就无法猜测

对于性能或并发 bug，永远不要依赖直觉：

- **pprof 胜过直觉**
- **race 检测器胜过推理**
- **基准测试胜过假设**

### 4. 一次一个假设

改变一件事，测量，确认。如果你同时改变三件事，你将一无所获。

### 5. 找到根本原因——不要使用临时方案

在编写修复之前，你必须理解 **为什么** bug 会发生。一个掩盖症状的临时方案会保留缺陷，所以它会在别处重现——通常离其根源更远，第二次追踪更难。

当你不理解问题时：

- **从症状反向追踪数据流** 到其起源。
- **质疑你的假设。** 你信任的代码可能错误。
- **问“为什么”五次。** 一直问，直到找到真正的根本原因。
- **执行更多故障排除检查。** 更多 fmt.Println，更多输出检查...

### 6. 研究代码库，而不仅仅是差异

在标记 bug 或提出修复之前，追踪数据流并检查上游处理。在隔离中看起来有问题的函数，在上下文中可能是正确的——调用者可能验证输入，中间件可能强制不变量，或周围代码可能保证函数依赖的条件。

1. **追踪调用者** — 谁调用这个函数以及使用什么值？调用站点可以使用代码搜索工具找到。→ 查看 `samber/cc-skills-golang@golang-gopls` 技能通过接口和嵌入解析实际符号——它找到间接调用站点，并跳过 plain grep 会分别遗漏或错误匹配的不相关的同名标识符。
2. **检查上游验证** — 输入解析、类型转换或链中的守卫子句可能使“bug”无法到达。
3. **阅读周围代码** — 中间件、拦截器或 init 函数可能设置函数依赖的状态。

**当上下文减轻严重性但并未消除问题时：** 仍然以降低的优先级报告，并附上说明哪些上游保证保护它的注释。添加简短的行内注释（例如，`// note: safe because caller validates via parseID() which returns uint`）以便为未来的审查者记录推理。

### 7. 从简单开始

有时 `fmt.Println` 就是本地调试的正确工具。仅在简单方法失败时才升级工具。永远不要在生产调试中使用 `fmt.Println`——使用 `slog`。

## 红旗：你正在错误地调试

如果发生以下任何情况，停止并返回步骤 1：

- **“先快速修复，以后再调查”** —— 没有“以后”。找到根本原因。
- **多个同时更改** — 一次一个假设。
- **提出未经理解原因的修复** — “也许我在这里添加一个 nil 检查……”是猜测，不是调试。
- **每个修复都揭示一个新问题** — 你在处理症状。真正的 bug 在别处。
- **同一问题尝试 3 次以上修复** — 你有错误的思维模型。从头开始重新阅读代码，追踪数据流。
- **“我的机器上可以工作”** — 你没有隔离环境差异。
- **责怪框架/stdlib/编译器** — 几乎不可能是 Go bug。先验证你的代码。

## 参考文件

- **[通用调试方法](./references/methodology.md)** — 系统的 10 步过程：定义症状、隔离重现、形成一个假设、测试它、验证根本原因，并防御回归。升级指南：何时从 `fmt.Println` 升级到日志到 pprof 到 Delve，以及如何避免同时更改多个假设的陷阱。

- **[常见 Go Bug](./references/common-go-bugs.md)** — 导致 Go 代码崩溃的 bug：nil 指针解引用、接口 nil 陷阱（类型 nil ≠ nil）、变量遮蔽、切片/映射/defer/错误/上下文陷阱、竞态条件、JSON 反序列化意外、未关闭资源。每个都有重现模式和修复。

- **[测试驱动调试](./references/testing-debug.md)** — 编写失败测试是调试的第一步。涵盖测试隔离技术、表格驱动测试组织以缩小失败、有用的 `go test` 标志（`-v`，`-run`，`-count=10` 用于不可靠测试），以及调试不可靠测试。

- **[并发调试](./references/concurrency-debug.md)** — 竞态条件、死锁、goroutine 泄漏。何时使用 race 检测器（`-race`），如何阅读 race 检测器输出，隐藏竞态条件的模式，使用 `goleak` 检测泄漏，分析堆栈转储以获取死锁线索。

- **[性能故障排除](./references/performance-debug.md)** — 当你的代码慢时：CPU 分析工作流、内存分析（堆 vs alloc_objects 分析，查找泄漏）、锁竞争（互斥锁分析）、I/O 阻塞（goroutine 分析）。如何阅读火焰图，识别热函数，以及使用基准测试测量改进。

- **[pprof 参考](./references/pprof.md)** — 完整的 pprof 手册。如何在生产中启用 pprof 端点（带认证），分析类型（CPU、堆、goroutine、互斥锁、阻塞、跟踪），本地和远程捕获分析，交互式分析命令（`top`，`list`，`web`），以及解释火焰图。

- **[诊断工具](./references/diagnostic-tools.md)** — 辅助工具用于特定症状。GODEBUG 环境变量（GC 跟踪、调度器跟踪），Delve 调试器用于断点调试，逃逸分析（`go build -gcflags="-m"` 查找未预期的堆分配），Go 的执行跟踪器用于理解 goroutine 调度。

- **[生产调试](./references/production-debug.md)** — 在不停止它们的情况下调试实时生产系统。生产清单，构建日志的可搜索性结构，安全启用 pprof（认证、网络隔离），从运行服务中捕获分析，网络调试（tcpdump、netstat），以及 HTTP 请求/响应检查。

- **[编译问题](./references/compilation.md)** — 构建失败：模块版本冲突、CGO 链接问题、`go.mod` 和安装的 Go 版本之间的版本不匹配、平台特定构建标签阻止交叉编译。

- **[代码审查红旗](./references/code-review-flags.md)** — 代码审查期间要警惕的潜在 bug 模式：未检查的错误、缺少 nil 检查、并发映射访问、没有明确退出条件的 goroutine、循环中的 defer 资源泄漏。

## 交叉引用

- → 查看 `samber/cc-skills-golang@golang-performance` 技能，在识别瓶颈后进行优化模式
- → 查看 `samber/cc-skills-golang@golang-observability` 技能，用于 Go 运行时监控的指标、告警和 Grafana 仪表板
- → 查看 `samber/cc-skills@promql-cli` 技能，在生产事件调查期间查询 Prometheus 指标
- → 查看 `samber/cc-skills-golang@golang-concurrency`，`samber/cc-skills-golang@golang-safety`，`samber/cc-skills-golang@golang-error-handling` 技能
