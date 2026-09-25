**角色：** 你是一位 Go 工程师，将测试视为可执行的规范。你编写测试来约束行为，而不是为了达成覆盖率目标。

**思考模式：** 对测试策略设计和失败分析进行尽可能彻底的推理——浅层推理会遗漏边缘情况，并产生脆弱的测试，这些测试今天通过，明天就会失败。在 Claude Code 中，使用 `ultrathink` 明确触发扩展思考。

**编排模式：** 对 Audit 模式中描述的三个子代理（单元质量和覆盖率差距、集成隔离、goroutine/竞态问题）进行发散，用于审计大型测试套件，并将它们的发现合并到一个差距报告中。在 Claude Code 中，使用 `ultracode` 明确选择多代理编排。

**模式：**

- **编写模式** — 为现有或新代码生成新的测试。按顺序处理要测试的代码；使用 `gotests` 框架化表格驱动测试，然后通过边缘情况和错误路径进行丰富。
- **审查模式** — 审查 PR 的测试更改。关注差异：检查新行为的覆盖率、断言质量、表格驱动结构以及是否存在不稳定的模式。按顺序进行。
- **审计模式** — 审计现有测试套件是否存在差距、不稳定性或不良模式（顺序依赖的测试、缺少 `t.Parallel()`、实现细节耦合）。启动最多 3 个并行子代理，按关注点划分：(1) 单元测试质量和覆盖率差距，(2) 集成测试隔离和构建标签，(3) goroutine 泄漏和竞态条件。
- **调试模式** — 测试失败或不稳定。按顺序处理：可靠地重现、隔离失败的断言、在生产代码或测试设置中追踪根本原因。

> **社区默认值。** 如果公司技能明确覆盖了 `samber/cc-skills-golang@golang-testing` 技能，则优先使用该技能。

**依赖项：**

- gotests: `go install github.com/cweill/gotests/gotests@latest`

# Go 测试最佳实践

此技能指导为 Go 应用程序创建可生产的测试。遵循这些原则编写可维护、快速且可靠的测试。

## 最佳实践摘要

1. 表格驱动测试必须使用命名的子测试——每个测试用例都需要将 `name` 字段传递给 `t.Run`。
2. 集成测试必须使用构建标签 (`//go:build integration`) 与单元测试分离。
3. 测试不得依赖于执行顺序——每个测试必须可以独立运行。
4. 独立测试在可能的情况下应使用 `t.Parallel()`。
5. 测试必须断言可观察的行为和公共 API 合约，而不是实现细节——与内部耦合的测试会使每次重构都变成重写测试，而无法证明合约。
6. 使用 goroutines 的包应在 `TestMain` 中使用 `goleak.VerifyTestMain` 来检测 goroutine 泄漏。
7. 使用 testify 作为辅助工具，而不是标准库的替代品。
8. 模拟接口，而不是具体类型。
9. 单元测试应保持快速（< 1ms），使用构建标签进行集成测试。
10. 在 CI 中使用竞态检测运行测试。
11. 将示例作为可执行的文档。
12. 测试文件必须以要测试的源文件命名，而不是以要测试的函数或方法命名。
13. 测试函数应按源文件中测试的函数/方法的顺序出现。

## 测试结构和组织

### 文件约定

```go
// package_test.go - 同一包中的测试（白盒，访问未导出内容）
package mypackage

// mypackage_test.go - 测试包中的测试（黑盒，仅公共 API）
package mypackage_test
```

以要测试的源文件命名测试文件，而不是以要测试的函数或方法命名。Go 的约定是每个源文件一个测试文件（`foo.go` -> `foo_test.go`），因为工具（`go test`、覆盖率报告、IDE“跳转到测试”导航、`gotests`）和审查者都按源文件解析测试，而不是按符号。一个源文件通常声明多个函数/方法；按符号名称拆分测试会将其分散到许多文件中，并破坏文件到文件的映射。

```
// ✓ 良好——每个源文件一个测试文件
helloworld.go       -> helloworld_test.go   // 包含 TestHelloWorld、TestAbcd、TestXyz、...

// ✗ 差——测试文件以函数/方法命名，而不是源文件
helloworld.go       -> abcd_test.go         // 错误：应该是 helloworld_test.go
```

例外：非常大的源文件可以按关注点拆分为多个 `_test.go` 文件（例如 `foo_test.go` + `foo_edgecases_test.go`），但每个拆分文件的名称必须仍然来自源文件名，而不是单个函数名。即使当文件很大时，也优先保持每个源文件一个 `_test.go` 文件——拆分会增加导航开销，很少值得；只有在单个文件变得真正难以浏览或审查时，才使用例外。

在测试文件内，按源文件中要测试的函数/方法的顺序排列测试函数。读者（人类或代理）滚动 `foo.go` 和 `foo_test.go` 时，可以按位置找到匹配的测试，而不是搜索；两种排序之间的偏差会随着每个文件的增长而累积。

### 命名约定

```go
func TestAdd(t *testing.T) { ... }               // 函数测试
func TestMyStruct_MyMethod(t *testing.T) { ... } // 方法测试
func BenchmarkAdd(b *testing.B) { ... }          // 基准测试
func ExampleAdd() { ... }                        // 示例
func FuzzAdd(f *testing.F) { ... }               // 混淆测试
```

## 表格驱动测试

表格驱动测试是 Go 测试多种场景的惯用方法。始终为每个测试用例命名。

```go
func TestCalculatePrice(t *testing.T) {
    tests := []struct {
        name     string
        quantity int
        unitPrice float64
        expected  float64
    }{
        {
            name:      "单个商品",
            quantity:  1,
            unitPrice: 10.0,
            expected:  10.0,
        },
        {
            name:      "批量折扣 - 100 件商品",
            quantity:  100,
            unitPrice: 10.0,
            expected:  900.0, // 10% 折扣
        },
        {
            name:      "零数量",
            quantity:  0,
            unitPrice: 10.0,
            expected:  0.0,
        },
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            got := CalculatePrice(tt.quantity, tt.unitPrice)
            if got != tt.expected {
                t.Errorf("CalculatePrice(%d, %.2f) = %.2f, want %.2f",
                    tt.quantity, tt.unitPrice, got, tt.expected)
            }
        })
    }
}
```

## 常见陷阱：断言作用域泄漏到子测试

绝对不要在父测试函数中创建一个 testify `assert`/`require` 实例并在 `t.Run` 闭包中重用它。`assert.New(t)` 捕获它被构建时使用的确切 `*testing.T`，所以如果该 `t` 属于父测试，子测试中的每个失败都会在 `go test` 输出中归因于_父测试_——失败的子测试本身仍然报告 `--- PASS`，默默地隐藏了哪个用例出错了。无论子测试是否调用 `t.Parallel()`，都会发生这种情况。

```go
// 错误——`is` 绑定到父的 t
func TestCalculatePrice(t *testing.T) {
    is := assert.New(t)
    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            is.Equal(tt.expected, CalculatePrice(tt.quantity, tt.unitPrice)) // 失败时错误归因
        })
    }
}

// 正确——每个子测试都从自己的 t 构建自己的实例
func TestCalculatePrice(t *testing.T) {
    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            is := assert.New(t)
            is.Equal(tt.expected, CalculatePrice(tt.quantity, tt.unitPrice))
        })
    }
}
```

使用故意损坏的用例进行验证：如果 `go test -v -run TestName` 显示 `--- FAIL: TestName`，但每个 `--- PASS: TestName/subtest_name` 行仍然说 PASS，则断言作用域正在泄漏。

## 单元测试

单元测试应该是快速的（< 1ms）、隔离的（没有外部依赖）并且确定性的。

## 测试 HTTP 处理程序

使用 `httptest` 进行具有表格驱动模式的处理程序测试。有关请求/响应体、查询参数、标头和状态码断言的示例，请参阅 [HTTP 测试](./references/http-testing.md)。

## 使用 goleak 检测 goroutine 泄漏

使用 `go.uber.org/goleak` 检测泄漏的 goroutine，特别是并发代码：

```go
import (
    "testing"
    "go.uber.org/goleak"
)

func TestMain(m *testing.M) {
    goleak.VerifyTestMain(m)
}
```

要排除特定的 goroutine 堆栈（对于已知泄漏或库 goroutine）：

```go
func TestMain(m *testing.M) {
    goleak.VerifyTestMain(m,
        goleak.IgnoreCurrent(),
    )
}
```

或每个测试：

```go
func TestWorkerPool(t *testing.T) {
    defer goleak.VerifyNone(t)
    // ... 测试代码 ...
}
```

## testing/synctest 用于确定性 goroutine 测试

`testing/synctest`（Go 1.25+）为 goroutines、计时器、截止日期和上下文取消提供确定性测试。时间仅在所有 goroutines 被阻塞时才会推进，因此顺序是可预测的。

何时使用 `synctest` 而不是真实时间：

- 测试具有基于时间的操作的并发代码（`time.Sleep`、`time.After`、`time.Ticker`）
- 当需要可复现的竞态条件时
- 当测试由于时间问题而不稳定时

```go
import (
    "context"
    "testing"
    "testing/synctest"
    "time"
)

func TestContextTimeout(t *testing.T) {
    synctest.Test(t, func(t *testing.T) {
        const timeout = 5 * time.Second

        ctx, cancel := context.WithTimeout(t.Context(), timeout)
        defer cancel()

        time.Sleep(timeout - time.Nanosecond)
        synctest.Wait()
        if err := ctx.Err(); err != nil {
            t.Fatalf("超时前: %v", err)
        }

        time.Sleep(time.Nanosecond)
        synctest.Wait()
        if err := ctx.Err(); err != context.DeadlineExceeded {
            t.Fatalf("超时后: 获得错误 %v, 想要 DeadlineExceeded", err)
        }
    })
}
```

在 Go 1.25+ 及更高版本中使用 `synctest.Test`。不要在 Go 1.25+ 代码中使用旧的 Go 1.24 实验性 `synctest.Run` API。如果模块明确针对 Go 1.24 并选择使用 `GOEXPERIMENT=synctest`，仅将旧 API 作为兼容性回退使用。

`synctest` 的关键区别：

- `time.Sleep` 在 goroutine 阻塞时立即推进合成时间
- `time.After` 在合成时间达到持续时间时触发
- 所有 goroutines 在时间推进前都运行到阻塞点
- 测试执行是确定性和可重复的
- Go 1.27+ 添加了 `synctest.Sleep(d)` 作为直接辅助函数来推进气泡的假时钟，相当于 `time.Sleep(d)` 后跟 `synctest.Wait()`，但不需要有阻塞的实 goroutine

Go 1.27+ 还添加了 `httptest.NewTestServer()`，它是 `httptest.NewServer` 的内存伪网络变体，可以与 `synctest` 组合——没有真实套接字，因此服务器测试可以在 `synctest.Test` 泡泡内运行，而不是需要 `httptest.NewServer` 加上真实计时器。

## 测试超时

对于可能挂起的测试，使用超时辅助工具，该工具会携带调用者位置抛出异常。有关详细信息，请参阅 [辅助工具](./references/helpers.md)。

## 基准测试

将基准测试作为子基准测试（每个变体使用 `b.Run`）编写，以便每个变体在输出中都有自己的名称——这是比较工具进行差异比较的名称。对于 Go 1.24+，使用 `b.Loop()` 而不是 `b.N` 循环。

→ 有关代码形状和大小参数化示例，请参阅 [测试套件中的基准测试](./references/benchmarks.md)。

→ 有关测量方法，请参阅 `samber/cc-skills-golang@golang-benchmark` 技能：`benchstat`、从基准测试进行剖析以及 CI 回归检测。

## Go 1.26+: 测试工件

当测试、基准测试或模糊目标需要持久化文件以供检查时，使用 `ArtifactDir()` 而不是临时路径或仓库本地输出。

```go
func TestRenderGoldenArtifact(t *testing.T) {
    dir := t.ArtifactDir()

    out := filepath.Join(dir, "rendered.json")
    if err := os.WriteFile(out, renderedBytes, 0o644); err != nil {
        t.Fatal(err)
    }

    t.Logf("工件写入: %s", out)
}
```

在 Go 1.26+ 的 `*testing.T`、`*testing.B` 和 `*testing.F` 上可用。

### Go 1.27+: `stdversion` 自动运行

`go test` 现在默认执行 `stdversion` vet 检查，标记模块 `go` 指令中任何使用比新 API 更新的 API。此检查的 CI 失败意味着 `go` 指令需要更新，或者代码需要停止使用较新的 API——它不是用来抑制检查的。

## 并行测试

使用 `t.Parallel()` 运行测试并行：

```go
func TestParallelOperations(t *testing.T) {
    tests := []struct {
        name string
        data []byte
    }{
        {"小数据", make([]byte, 1024)},
        {"中等数据", make([]byte, 1024*1024)},
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            t.Parallel()
            is := assert.New(t)

            result := Process(tt.data)
            is.NotNil(result)
        })
    }
}
```

## 模糊测试

使用模糊测试查找边缘情况和错误：

```go
func FuzzReverse(f *testing.F) {
    f.Add("hello")
    f.Add("")
    f.Add("a")

    f.Fuzz(func(t *testing.T, input string) {
        reversed := Reverse(input)
        doubleReversed := Reverse(reversed)
        if input != doubleReversed {
            t.Errorf("Reverse(Reverse(%q)) = %q, want %q", input, doubleReversed, input)
        }
    })
}
```

## 示例作为文档

`ExampleXxx` 函数是可执行的文档：`go test` 比较它们的 stdout 与 `// Output:` 注释，因此漂移的示例会失败构建，而不是误导读者。

→ 有关命名规则、`Unordered output` 和放置，请参阅 [示例作为文档](./references/examples.md)。

## 代码覆盖率

使用 `go test -coverprofile=coverage.out ./...` 生成一个配置文件，然后使用 `go tool cover -html=coverage.out` 读取未覆盖的行。覆盖率定位未测试的路径；它不衡量断言质量，因此应将百分比视为差距查找器，而不是目标。

→ 有关覆盖率模式、`-coverpkg` 和报告陷阱，请参阅 [代码覆盖率](./references/coverage.md)。

## 集成测试

使用构建标签将集成测试与单元测试分离：

```go
//go:build integration

package mypackage

func TestDatabaseIntegration(t *testing.T) {
    db, err := sql.Open("postgres", os.Getenv("DATABASE_URL"))
    if err != nil {
        t.Fatal(err)
    }
    defer db.Close()

    // 测试真实数据库操作
}
```

单独运行集成测试：

```bash
go test -tags=integration ./...
```

对于 Docker Compose 固定装置、SQL 模式和集成测试套件，请参阅 [集成测试](./references/integration-testing.md)。

## 模拟

模拟接口，而不是具体类型。在消费时定义接口，然后创建模拟实现。

有关模拟模式、测试固定装置和时间模拟，请参阅 [模拟](./references/mocking.md)。

## 使用 Linters 强制执行

许多测试最佳实践都由 linters 自动强制执行：`thelper`、`paralleltest`、`testifylint`。有关配置和使用，请参阅 `samber/cc-skills-golang@golang-lint` 技能。

## 参考链接

- → 有关详细的 testify API（断言、require、模拟、套件），请参阅 `samber/cc-skills-golang@golang-stretchr-testify` 技能。
- → 有关数据库集成测试模式，请参阅 `samber/cc-skills-golang@golang-database` 技能（testing.md）。
- → 有关使用 goleak 检测 goroutine 泄漏，请参阅 `samber/cc-skills-golang@golang-concurrency` 技能。
- → 有关 CI 测试配置和 GitHub Actions 工作流程，请参阅 `samber/cc-skills-golang@golang-continuous-integration` 技能。
- → 有关 testifylint 和 paralleltest 配置，请参阅 `samber/cc-skills-golang@golang-lint` 技能。
- → 有关使用这些指南在 CI 中使用 AI 驱动的代码审查，请参阅 `samber/cc-skills-golang@golang-continuous-integration` 技能。

## 快速参考

```bash
go test ./...                          # 所有测试
go test -run TestName ./...            # 按确切名称指定测试
go test -run TestName/subtest ./...    # 测试中的子测试
go test -run 'Test(Add|Sub)' ./...     # 多个测试（正则表达式 OR）
go test -run 'Test[A-Z]' ./...         # 以大写字母开头的测试
go test -run 'TestUser.*' ./...        # 匹配前缀的测试
go test -run '.*Validation.*' ./...    # 包含子字符串的测试
go test -run TestName/. ./...          # TestName 的所有子测试
go test -run '/(unit|integration)' ./... # 按子测试名称过滤
go test -race ./...                    # 竞态检测
go test -cover ./...                   # 覆盖率摘要
go test -bench=. -benchmem ./...       # 基准测试
go test -fuzz=FuzzName ./...           # 模糊测试
go test -tags=integration ./...        # 集成测试
```
