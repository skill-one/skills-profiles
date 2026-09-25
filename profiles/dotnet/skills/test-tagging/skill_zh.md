# 测试特征标签

分析任何支持语言的现有测试套件，并将一套标准化的特征标签应用于每个测试方法，使团队能够了解其测试分布（正面与负面、关键路径覆盖、冒烟测试等）。

> **语言特定指南**：先尝试 `test-analysis-extensions`。如果不可用，立即继续使用下方的内置框架表；切勿在辅助工具上阻塞标签。

## 使用场景

- 审计测试项目以了解测试类型的组合
- 为未标记的测试添加特征属性
- 生成测试套件中特征分布的摘要报告
- 审查关键路径是否具有足够的覆盖

## 不适用场景

- 从头编写新测试（使用 `code-testing-agent` 适用于任何语言，或 `writing-mstest-tests` 适用于 MSTest）
- 运行或过滤测试（使用 `.NET` 的 `run-tests`；其他地方使用等效原生运行器）
- 在测试框架之间迁移
- 通用质量、异味、不稳定或断言审计（使用 `test-anti-patterns` 或匹配的分析技能）
- 诊断 `.NET` 执行的行/分支/Cobertura 解释或项目范围的 CRAP 风险（使用 `coverage-analysis`）；原始覆盖率收集（使用 `.NET` 的 `run-tests`，其他地方使用原生工具）
- 对命名方法、类或文件的 CRAP 分析（使用 `crap-score`）
- 行为差距，其中测试会因生产逻辑损坏而幸存（使用 `test-gap-analysis`）

## 输入

| 输入 | 必填 | 描述 |
|------|------|------|
| 测试项目或文件 | 否 | 测试项目、文件夹或特定测试文件的路径。省略时从当前工作区发现。 |
| 范围 | 否 | `tag`（应用规范属性，或确认的项目约定）、`audit`（仅报告）或 `both`（默认：`both`）。声明为 `report-only` 的框架始终发出报告；`convention-based` 框架仅在用户确认约定后编辑。 |
| 框架 | 否 | 自动检测。检测失败时覆盖。 |

## 特征分类法

使用完全相同的特征名称和值。不要在表格外发明新的特征值。

| 特征值 | 含义 | 启发式 |
|--------|------|--------|
| `positive` | 验证正常/有效条件下的预期行为 | 断言成功、有效输出、预期状态、有效输入时无异常 |
| `negative` | 验证无效输入、错误或边缘情况的正确处理 | 断言异常、错误代码、验证失败、拒绝不良输入 |
| `boundary` | 测试极限、阈值、空/空/None/nil 输入、最小/最大值 | 在 `0`、`-1`、`int.MaxValue` / `sys.maxsize` / `Number.MAX_SAFE_INTEGER` / `math.MaxInt64` / `i32::MAX`、空字符串、null/None/nil/undefined、空集合、有效范围边界上操作 |
| `critical-path` | 必须永不中断的核心工作流；中断会阻塞用户 | 测试关键公共 API 或用户界面功能的主要成功场景 |
| `smoke` | 快速的合理性检查，系统是否正常运行 | 快速、无复杂设置、验证基本连接（例如，服务解析、端点返回 200） |
| `regression` | 复现之前报告的特定错误 | 引用错误 ID、问题编号，或在名称或注释中描述修复内容 |
| `integration` | 跨进程、网络或持久化边界 | 使用真实数据库、HTTP 客户端、文件系统、外部服务或多组件设置 |
| `end-to-end` | 横跨整个应用程序堆栈的完整用户工作流 | 从入口点执行完整场景到最终结果，与单边界 `integration` 不同 |
| `performance` | 验证时间、吞吐量或资源消耗 | 断言经过时间、内存、分配，或使用基准测试框架（BenchmarkDotNet、pytest-benchmark、benchmark.js、JMH、`go test -bench`、criterion.rs、XCTMetric、kotlinx-benchmark、Google Benchmark） |
| `security` | 验证身份验证、授权、输入清理或密钥处理 | 测试 SQL 注入、XSS、CSRF、未经授权访问、令牌验证、权限检查 |
| `concurrency` | 验证线程安全、并行性或异步正确性 | 使用 `Task.WhenAll` / `Parallel.ForEach` / `SemaphoreSlim` (.NET)；`asyncio.gather` / `threading.Lock` / `multiprocessing` (Python)；`Promise.all` / 工作线程 (JS/TS)；`CompletableFuture` / `ExecutorService` / `synchronized` (Java)；`go func` / `sync.WaitGroup` / `sync.Mutex` / `chan` (Go)；`Mutex` / `Thread.new` (Ruby)；`tokio::spawn` / `Arc<Mutex<_>>` / `crossbeam` (Rust)；`DispatchQueue` / `actor` (Swift)；`coroutineScope` / `Mutex` (Kotlin)；`Start-Job` / `RunspacePool` (PowerShell)；`std::thread` / `std::mutex` (C++)；重现竞争条件 |
| `resilience` | 测试重试逻辑、超时、断路器或优雅降级 | 断言在瞬态故障、网络中断或服务不可用下的行为（例如，Polly、tenacity、p-retry、resilience4j、hystrix、opossum、retry-go） |
| `destructive` | 修改难以回滚的共享或外部状态 | 删除记录、释放资源、修改全局配置——对 CI 隔离决策有用 |
| `configuration` | 验证设置加载、默认值、环境行为 | 测试缺失配置键、无效值、环境变量回退、选项验证 |
| `flaky` | 已知会间歇性失败（用于测试健康跟踪的元标签） | 标记团队知道不可靠的测试；用于隔离或优先处理稳定性 |

单个测试可以有 **多个特征**（例如，既是 `negative` 又是 `boundary`）。至少，每个测试应接收 `positive` 或 `negative` 之一。

## 工作流程

### 第 1 步：检测语言、框架和标签能力

在请求路径之前，从当前工作区解析请求的测试范围。技能上下文的 `Base directory` 包含这些说明，而不是用户的存储库。始终检查当前工作目录，然后再声称存储库文件不可用。如果提示的相对路径不存在，在工作区中搜索命名的项目/文件并重试确切结果。成功的搜索证明目标存在；如果正常的读取器报告相同路径缺失，将此矛盾视为读取器路径规范化或传输故障，而不是要求用户提供文件。仅在确认读取器可用性、传输或路径规范化失败后，且仅在使用 `sed`/`cat`（Unix）、`Get-Content`（PowerShell）等 shell 文本读取器后，才保留规范路径仍在当前工作区内部。在内容排除、权限/策略、工作区边界或未知读取故障时停止。工作区搜索找到可读取目标后，切勿要求用户提供路径或文件内容。

对于 `auto-edit` 框架，失败的补丁/编辑调用只有在确认工具可用性、传输或路径规范化失败时才不是停止条件。不要绕过陈旧上下文、并发更改、权限/策略或路径边界错误。在 shell 回退之前，在当前工作区中解析规范路径，重新读取文件，并使用锚定转换，除非预期旧文本和确切匹配计数未更改，否则中止。然后重新打开完整文件，检查差异，并运行第 6 步验证。当用户要求应用它们时，不要报告拟议的属性作为完成。

识别语言和框架。尝试匹配的 `test-analysis-extensions` 指南一次。如果不可用，从内置规则下方分类能力：

- **`auto-edit`** — 框架具有此技能可安全插入的规范标签语法（.NET `[TestCategory]` / `[Trait]` / `[Category]` / `[Property]`、pytest `@pytest.mark.<name>`、JUnit 5 `@Tag("...")`、TestNG `groups = {"..."}`、RSpec 元数据 `it "..." , :tag => true`、Pester `-Tag '...'`、Kotest `@Tags(...)`、Swift Testing `@Tag(.tagName)`、Catch2 `[tag]`、doctest `* doctest::test_suite("tag")` 装饰器）。
- **`report-only`** — 框架没有规范、约定的标签属性；仅以 Markdown 表格形式报告标签，不要编辑源代码（Go 标准 `testing` 无构建标签约定、Jest/Vitest 无一致 `describe` 前缀约定、Rust 无项目特定 `cfg` 约定、XCTest 无测试计划、GoogleTest 无测试名前缀约定、Mocha 无 `describe` 前缀约定）。
- **`convention-based`** — 框架使用命名或文件约定进行标签（Go `//go:build integration` 构建标签、文件名后缀如 `*_integration_test.go`、GoogleTest `INTEGRATION_*` 过滤器前缀）。仅在用户确认项目约定后发出规范编辑；否则视为 `report-only`。

在步骤 4 之前捕获能力。

### 第 2 步：扫描现有特征

检查哪些测试已经具有特征属性。加载扩展时使用扩展；否则使用此内置表格作为真实来源：

| 框架 | 现有属性 | 示例 |
|------|----------|------|
| MSTest | `[TestCategory("...")]` | `[TestCategory("positive")]` |
| xUnit | `[Trait("Category", "...")]` | `[Trait("Category", "positive")]` |
| NUnit | `[Category("...")]` | `[Category("positive")]` |
| TUnit | `[Property("Category", "...")]` | `[Property("Category", "positive")]` |
| JUnit 5 | `@Tag("...")` | `@Tag("positive")` |
| TestNG | `@Test(groups = {"..."})` | `@Test(groups = {"positive"})` |
| pytest | `@pytest.mark.<name>` | `@pytest.mark.positive` |
| RSpec | `it` 后的元数据 | `it "...", :positive do` |
| Pester | `-Tag '...'` | `It '...' -Tag 'positive'` |
| Kotest | `@Tags(...)` | `@Tags(Positive)` |
| Swift Testing | `@Tag(.<name>)` | `@Test(.tags(.positive))` |
| Catch2 | `[tag]` 在名称中 | `TEST_CASE("...", "[positive]")` |
| doctest | `* doctest::test_suite("...")` 装饰器 | `TEST_CASE("..." *doctest::test_suite("positive"))` |

记录哪些测试已经具有标签，以避免重复。

### 第 3 步：对每个测试方法进行分类

构建一个包含每个发现的测试恰好一次的规范清单。记录测试标识符、行为分类和清单中的特征；使用相同的行进行源编辑、每个测试报告、总计和分布计数。不要手动计算单独的分母。发布之前，将报告的总计与清单行数进行核对，并验证每一行都对每个显示的特征计数有贡献。

对于没有特征的每个测试方法，分析：

1. **方法名** — 包含 `Invalid`、`Fail`、`Error`、`Throw`、`Reject`、`BadInput`、`Null`、`None`、`Nil`、`Negative`、`raises_`、`_throws_`、`_returns_error` 的名称建议 `negative`
2. **断言类型** — `Assert.ThrowsException` / `Assert.Throws` / `Should().Throw()` / `pytest.raises` / `expect(fn).toThrow` / `assertThrows` / `assert.Error(t, err)` / `expect { ... }.to raise_error` / `#[should_panic]` / `XCTAssertThrowsError` / `Should -Throw` / `EXPECT_THROW` 建议为 `negative`
3. **输入值** — `null` / `None` / `nil` / `undefined`、`""`、`0`、`-1`、`int.MaxValue` / `sys.maxsize` / `Number.MAX_SAFE_INTEGER` / `math.MaxInt64` / `i32::MAX`、空集合建议 `boundary`
4. **设置复杂性** — 最小设置和基本断言建议 `smoke`；外部依赖（文件/数据库/网络/环境）建议 `integration`
5. **注释和名称** — 引用问题编号或 "regression" / "bug" / "fix for #..." 建议为 `regression`
6. **时间断言** — `Stopwatch`、`BenchmarkDotNet`、经过时间检查；pytest-benchmark 固定装置；benchmark.js；JMH `@Benchmark`；`go test -bench`；criterion.rs；XCTMetric；Google Benchmark；kotlinx-benchmark 建议为 `performance`
7. **功能中心性** — 测试在主要公共 API 入口点或关键用户工作流上的测试建议 `critical-path`
8. **安全模式** — 验证身份验证、检查权限、清理输入、测试注入、处理令牌/密钥建议 `security`
9. **并行/异步构造** — 每种语言的并发原语（见特征分类法表格）建议 `concurrency`
10. **故障注入** — 模拟故障、测试重试、超时或断路器建议 `resilience`
11. **状态变异** — 删除外部记录、释放资源、修改共享/全局状态建议 `destructive`
12. **全栈流程** — 测试跨越入口点到数据层再到最终响应，覆盖完整用户场景建议 `end-to-end`
13. **配置/设置** — 加载配置、测试缺失键、验证选项、检查环境变量建议 `configuration`
14. **已知不稳定** — 测试具有跳过/忽略注释，注释中关于不稳定，或名称包含 "flaky" / "intermittent" 建议为 `flaky`
15. **默认** — 如果测试验证正常成功路径，标记为 `positive`

在 `positive` 和 `negative` 之间不确定时，读取断言：如果断言成功 -> `positive`；如果断言失败 -> `negative`。

对于请求的分布或覆盖形状审计，使用可用的生产代码将每个测试映射到它执行的精确结果，然后再汇总。指出重复的边界覆盖，并验证测试清单是否代表命名阈值和业务关键路径上的可观察协作者结果。将这些作为简洁的分布观察结果，而不是新的特征值。不要执行变异推理、开具新测试或扩展到 `test-gap-analysis` 拥有的行为差距审计。

### 第 4 步：应用特征属性（或仅报告）

**如果解析的能力是 `auto-edit`**，将适当的属性添加到每个测试方法。将特征属性放置在现有测试属性旁边。示例：

在单个测试方法/用例级别应用特征。不要用类级别的类别替换方法级别的分类：不同方法通常执行不同的正面、负面和边界行为。

**MSTest:**
```csharp
[TestMethod]
[TestCategory("negative")]
[TestCategory("boundary")]
public void Parse_NullInput_ThrowsArgumentNullException() { ... }
```

**xUnit:**
```csharp
[Fact]
[Trait("Category", "positive")]
[Trait("Category", "critical-path")]
public void CreateOrder_ValidItems_ReturnsConfirmation() { ... }
```

**NUnit:**
```csharp
[Test]
[Category("regression")]
[Category("negative")]
public void Calculate_OverflowInput_ReturnsError() // Fix for #1234
{ ... }
```

**pytest:**
```python
@pytest.mark.negative
@pytest.mark.boundary
def test_parse_none_input_raises_value_error():
    ...
```

**JUnit 5:**
```java
@Test
@Tag("positive")
@Tag("critical-path")
void createOrder_validItems_returnsConfirmation() { ... }
```

**TestNG:**
```java
@Test(groups = {"negative", "boundary"})
public void parse_nullInput_throwsIllegalArgumentException() { ... }
```

**RSpec:**
```ruby
it "rejects null input", :negative, :boundary do
  ...
end
```

**Pester:**
```powershell
It 'Rejects null input' -Tag 'negative','boundary' {
    ...
}
```

**Kotest:**
```kotlin
@Tags(Negative, Boundary)
class ParserSpec : StringSpec({
    "rejects null input" { ... }
})
```

**Swift Testing:**
```swift
@Test(.tags(.negative, .boundary))
func parseNullInputThrows() throws { ... }
```

**Catch2:**
```cpp
TEST_CASE("Parse null input throws", "[negative][boundary]") { ... }
```

**如果解析的能力是 `report-only`**（Go 标准 `testing`、无约定的 Jest/Vitest、无项目特定 `cfg` 的 Rust、无约定的 XCTest、无约定的 GoogleTest、无约定的 Mocha），不要修改源文件。相反，发出从每个测试到其建议标签的简洁映射。当用户询问如何持久化或过滤这些标签时，建议项目范围的约定；仅分析请求应报告并停止。

**如果解析的能力是 `convention-based`**（例如，Go `//go:build integration`、`*_integration_test.go`、GoogleTest `INTEGRATION_*` 前缀），仅在用户确认了项目的约定后，才发出规范编辑。否则视为 `report-only`。

### 第 5 步：生成特征摘要

标记后，生成摘要表格。除非用户请求完整分类法，否则仅包含非零计数的特征。零填充的行会掩盖套件的实际形状。对于小型仅报告套件，将每个测试映射和零分布保持在一起，而不是扩展为仪表板。

```
## 特征分布

| 特征         | 计数 | 总计百分比 |
|--------------|------|-----------|
| positive      |    50 |      64.1% |
| negative      |    28 |      35.9% |
| boundary      |     8 |      10.3% |
| critical-path |    12 |      15.4% |
| **总测试数** | **78** | -- |

注意：百分比超过 100%，因为测试可以有多个特征。
```

包括观察结果，例如：
- 正面与负面测试的比率
- 关键公共 API 是否存在关键路径测试
- 无法自信分类的任何测试（列出供手动审查）

`boundary` 和其他所有专业特征都是可加的。边界成功案例仍然是 `positive`；拒绝的边界仍然是 `negative`。应用此规则后得出正负分布。

### 第 6 步：在报告之前验证编辑

对于每个 `auto-edit` 框架，运行最窄的命令来编译编辑后的属性并确认测试发现。即使用户仅要求添加标签，也需要此命令，因为语法上合理的属性不是完成的编辑。

| 框架 | 最小验证 |
|------|----------|
| .NET | 运行 `dotnet build <test-project>`，然后使用 `dotnet test <test-project> --list-tests --no-build` 确认发现。除非用户要求，否则不要执行套件；将执行路由到 `run-tests`。 |
| pytest | 使用仓库配置的 pytest 命令收集编辑后的套件 |
| JUnit/TestNG | 通过仓库的 Maven/Gradle 测试任务编译测试 |
| 其他 `auto-edit` 框架 | 使用仓库的最窄编译或测试发现命令 |

如果编辑或补丁应用不确定，在验证之前重新打开完整编辑文件，并核对每个清单行与该测试旁边的实际属性。不要从部分差异或预期补丁报告成功。如果验证失败，报告确切的命令和错误；切勿为未编译的编辑发布成功的分布交接。

## 验证

- [ ] 每个测试方法至少有一个特征分类（`positive` 或 `negative` 至少）——在 `report-only` 框架的报告中，或作为 `auto-edit` 框架的属性
- [ ] 总计等于每个测试清单计数，显示的特征计数来自该清单
- [ ] 未在分类法表格外发明特征值
- [ ] 保留现有特征属性，未重复
- [ ] 生成了特征摘要表格
- [ ] 对于 `auto-edit` 框架，项目仍然可以构建 / 测试仍然可以发现，无需执行未请求的测试（`dotnet build` 加列表模式 / `pytest --collect-only` / `mvn test-compile` / `go vet ./...` / `cargo check --tests` / `npm run test:list` / 等效）
- [ ] 最终摘要引用了成功的验证命令和发现的测试计数（当有发现命令时）
- [ ] 对于 `report-only` 框架，未修改源文件
- [ ] 对于 `convention-based` 框架，仅在确认项目约定后应用编辑

## 常见陷阱

| 陷阱 | 解决方案 |
|------|----------|
| 未阅读测试正文就猜测特征 | 始终阅读断言和设置以准确分类 |
| 仅将测试标记为 `boundary` 而没有 `positive`/`negative` | 每个测试也应为 `positive` 或 `negative`——`boundary` 是可加的 |
| 使用检测到的框架的错误属性语法 | 匹配加载的扩展或内置表格（不要在 xUnit 中放入 `[TestCategory]`，或在 unittest 中放入 `@pytest.mark.x`） |
| 重复现有的类别属性 | 在第 2 步检查预存在的特征之前添加 |
| 过度标记为 `critical-path` | 仅保留在主要公共入口点上的测试，而不是每个辅助工具 |
| 编辑 Go / 无约定的 Jest / 无约定的 Rust / 无约定的 XCTest / 无约定的 GoogleTest 源 | 这些默认为 `report-only`——发出 Markdown 表格。仅在用户确认项目范围的约定（构建标签、文件后缀、describe 前缀、测试计划分组）后编辑。 |
| 为基于约定的框架发明标签前缀 | 在采用一个约定之前确认项目的现有约定——不要在 `_integration_test.go`、`//go:build integration` 或 `IntegrationTest` 前缀之间猜测 |
| 缺少语言特定的并发 / 异步原语 | 使用加载的扩展时使用扩展；否则使用特征分类法并发行 |
