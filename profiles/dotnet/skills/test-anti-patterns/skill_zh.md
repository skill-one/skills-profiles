# 测试反模式检测

对任何支持的语言中的测试代码进行快速、务实的分析，以发现影响测试可靠性、可维护性和诊断价值反模式和质量问题。

> **语言特定指南**：先尝试 `test-analysis-extensions`。如果不可用，立即继续使用此技能的内置框架规则；不要让审计受阻于辅助工具。

## 使用场景

- 用户要求审查测试质量或查找测试异味
- 用户想知道为什么测试不稳定或不可靠
- 用户询问“我的测试好吗？”或“我的测试有什么问题？”
- 用户请求测试审计或测试代码审查
- 用户希望在决定要改进什么之前获得诊断结果

## 不适用场景

- 用户想从头开始编写新测试（使用 `code-testing-agent`）
- 用户想要直接的实现修复而不是诊断审查（使用相关的编写/编辑技能）
- 用户要求修复 MSTest 中交换的 `Assert.AreEqual` 参数顺序（使用 `writing-mstest-tests`）
- 用户要求将 MSTest 的 `DynamicData` 从 `IEnumerable<object[]>` 转换为 `ValueTuple`（使用 `writing-mstest-tests`）
- 用户想要运行或执行测试（使用 `.NET` 的 `run-tests`）
- 用户想要在测试框架或版本之间迁移（使用迁移技能）
- 用户想要原始的 .NET 覆盖收集（使用 `run-tests`），非 .NET 覆盖收集或分析（使用原生工具），项目范围的 .NET 覆盖/CRAP 指标（使用 `coverage-analysis`），或命名目标的 .NET CRAP（使用 `crap-score`）
- 用户询问测试是否会捕获错误或想要行为/伪突变差距（使用 `test-gap-analysis`）
- 用户想要测试混合或 happy-vs-error-path 分类、标准化标签或特征/类别分布（使用 `test-tagging`）
- 用户想要深度正式的测试异味审计，具有学术分类和扩展目录（使用 `test-smell-detection`）

## 输入

| 输入 | 是否必需 | 描述 |
|-------|----------|-------------|
| 测试范围 | 否 | 要分析的测试文件、类、目录或项目。如果省略，则从当前工作区发现。 |
| 生产代码 | 否 | 要测试的代码，用于了解测试应该验证什么 |
| 具体关注点 | 否 | 聚焦于“易变性”或“命名”等区域以缩小审查范围 |

## 工作流程

### 第 1 步：检测语言并加载扩展

在请求输入之前，从当前工作区解析命名测试路径。

如果没有提供路径，则使用存储库清单和常规测试标记发现当前目录下的测试文件。技能上下文的 `Base directory` 是文档存储，不是用户的工作区；永远不要相对于它解析目标文件。

如果一个读取器说路径丢失，但工作区通配符/搜索找到了它，请规范化该确切路径并重试。仅在确认读取器可用性、传输或路径规范化失败后，并且验证规范路径仍然位于当前工作区内部时，才使用 shell 文本读取器（Unix 上的 `sed`/`cat`，PowerShell 上的 `Get-Content`）。

遇到内容排除、权限/策略、工作区边界或未知错误时停止。审计任何允许的读取器可以访问的发现文件；永远不要要求用户粘贴它。如果所有允许的读取器都失败，请报告确切阻止因素，而不要绕过安全边界。

识别语言和框架。尝试匹配的 `test-analysis-extensions` 指南一次；如果不可用，则使用下面的目录。

### 第 2 步：收集测试代码

读取解析范围内的每个测试文件。加载扩展时使用扩展发现标记；否则使用此技能的内置标记（例如 `[TestClass]`/`[Fact]`/`[Test]`、`test_*.py`、`*.test.*`、`*_test.go`、`*_spec.rb`、`#[test]`、`*.Tests.ps1`、`TEST(...)`、`TEST_CASE(...)`）。

如果提供生产代码，也读取它——这对于检测与实现细节耦合而不是行为的测试至关重要。

### 第 3 步：扫描反模式

将每个测试文件与下面的反模式目录进行对照。按严重程度报告发现。加载扩展时使用扩展映射；否则使用跨框架目录中的示例。

在起草报告之前，制作一个私有的完整性账本，每行对应每个测试方法和每个类级固定件/资源。记录其预言者（或缺失）、异常处理、状态/时间依赖性和处置。在每行要么附加到发现，要么明确判断为可靠之前，不要发布。特别是：

- `actual != oldValue` 是一个弱突变预言者：它接受每个错误的新值。要求确切的预期值。
- 包括未使用或未释放的类级资源；仅方法扫描会遗漏字段，例如静态 `HttpClient`。
- 当提供生产代码时，注意发现旁边明显的未测试合同，但不要执行彻底的分支或突变分析。将更广泛的问题路由到 `test-gap-analysis`。

#### 关键——给出错误信心的测试

| 反模式 | 要查找的内容 |
|---|---|
| **无断言** | 执行代码但从未断言任何内容的测试方法。没有断言的通过测试证明不了任何东西。在 .NET 中查找缺少 `Assert.*`；在 pytest 中查找没有 `assert` 和没有 `pytest.raises` 的函数；在 Jest 中查找没有 `expect(...)`；在 JUnit 中查找没有 `assert*`/`assertThat`；在 Go 中查找从未调用 `t.Error*`、`t.Fatal*` 或 testify 的测试；在 RSpec 中查找没有 `expect` 的块；在 Pester 中查找没有 `Should`。模拟调用验证（`verify(mock)`、`expect(mock).toHaveBeenCalled`、`Should -Invoke`）是真实的断言。 |
| **异步断言上缺少 await (JS/TS、.NET、Python、Kotlin、Swift)** | 没有 `await`/`return` 的 `expect(promise).resolves.toBe(x)`，`pytest-asyncio` 测试中未等待的协程，`async Task` xUnit 测试调用 `Assert.ThrowsAsync` 而没有 `await`，Kotest 悬停测试而未使用 `runTest`，Swift 测试中未使用 `await`。这些测试即使在底层断言会失败时也会静默通过。 |
| **覆盖接触** | 系统地调用类型上每个公共成员的测试类——通常按字母顺序或声明顺序——而不断言有意义的结果。每个测试通常执行 `var result = sut.MethodName(...)`（或 `result = sut.method_name(...)`、`sut.methodName()`、`sut.MethodName(t)`）而没有断言，或者只进行简单的 null/None/nil 检查。目的是虚增代码覆盖率指标，而不是验证行为。这与单个无断言的测试不同：模式是 *系统性地* 覆盖表面区域而没有实际验证。 |
| **自引用断言** | 预期值是从同一实际值计算得出的，例如 `Assert.AreEqual(dto.Name, dto.Name)`、`Assert.AreEqual(result, result)` 或等效项。不要仅仅因为有效的身份、克隆、序列化或往返合同将输出与输入进行比较而贴上此标签：这些断言可能会失败。相反，检查输入是否执行了转换，以及是否缺少独立已知的表示、字段、引用身份或无效输入断言。 |
| **吞没的异常** | `try { ... } catch { }`，没有重新抛出或断言的 `catch (Exception)` (.NET)；裸 `except:` 或 `except Exception:` 与 `pass` (Python)；`try { ... } catch (e) {}` (JS/TS/Java)；没有重新恐慌和断言的 `defer recover()` (Go)；没有断言的 `rescue StandardError` (Ruby)；在测试中吞没错误的 `Result::unwrap_or(...)` (Rust)；空的 `catch` 块 (Kotlin/Swift)。 |
| **仅在 catch 块中断言** | `try { Act(); } catch (Exception ex) { Assert.Fail(ex.Message); }`（以及其他语言中的等效项）——使用 `Assert.ThrowsException` / `pytest.raises` / `expect(fn).toThrow` / `assertThrows` / `assert.Error(t, err)` / `#[should_panic]` / `Should -Throw` / `EXPECT_THROW` 代替。当没有抛出异常时测试通过，即使结果错误。 |
| **始终为真的断言** | `Assert.IsTrue(true)`、`Assert.AreEqual(x, x)`、`assert True`、`expect(true).toBe(true)`、`assert.True(t, true)`、`assert!(true)` 或条件永远不可能失败。 |
| **注释掉的断言** | 被禁用但测试仍然运行、给人以覆盖错觉的断言。 |

#### 高——可能导致痛苦的测试

| 反模式 | 要查找的内容 |
|---|---|
| **易变性指标** | 用于同步的墙上时钟睡眠/等待：`.NET` 的 `Thread.Sleep` / `Task.Delay`、`time.sleep` (Python)、`setTimeout` / `await new Promise(r => setTimeout(...))` (JS/TS)、`Thread.sleep` (Java/Kotlin)、`time.Sleep` (Go)、`sleep` (Ruby/Bash)、`std::thread::sleep` (Rust)、`Start-Sleep` (Pester)、`std::this_thread::sleep_for` (C++)。墙上时钟读取而不使用抽象：`.NET` 的 `DateTime.Now`/`UtcNow`、`datetime.now()`/`datetime.utcnow()`、`Date.now()` / `new Date()`、`System.currentTimeMillis()`、`time.Now()`、`Time.now`、`Instant::now()`、`Date()`/`Date.now`、`Get-Date`、`std::chrono::system_clock::now`。未播种的随机性：`new Random()`、`random.random()`/`random.randint()`、`Math.random()`、`new Random()` (Java/Kotlin)、没有种子的 `rand.Int()`、`rand` (Ruby)、`rand::random()` (Rust)。环境依赖的路径（硬编码 `C:\...`、`/tmp/...`、网络主机）。 |
| **测试顺序依赖** | 跨测试修改静态/全局可变状态；未完全重置状态的设置（`.NET` 的 `[TestInitialize]`、`setUp`、`beforeEach`、`before(:each)`、`BeforeEach`、`t.Cleanup`）；当单独运行时失败但在套件中通过（反之亦然）的测试。每种语言的示例：`.NET`/Java 的 `static` 字段、Python 的模块级全局变量、JS/TS 测试文件中的顶层 `let`/`const`、Go 的 `var` 包全局变量、Ruby 的类变量、Rust 的 `static mut`/`lazy_static!`/`OnceCell`、PowerShell 的 `$script:` 变量。 |
| **过度模拟** | 模拟设置行数多于实际测试逻辑。在模拟上验证确切的调用序列而不是结果。模拟测试拥有的类型。每种语言的示例：`.NET` 的 Moq/NSubstitute/FakeItEasy、Python 的 `unittest.mock` / `pytest-mock`、JS/TS 的 Jest auto-mocks / Sinon、Java 的 Mockito/PowerMock、Go 的 gomock/testify mock、Ruby 的 RSpec mocks/mocha、Rust 的 `mockall`、Kotlin 的 MockK、PowerShell 的 `Mock` cmdlet、C++ 的 gmock。对于 .NET 的深度模拟审计，请使用 `exp-mock-usage-analysis`。 |
| **实现耦合** | 通过反射测试私有方法（`.NET` 的 `MethodInfo.Invoke`、Python 中的 `getattr`、TS 中的 `(thing as any)`、Java 中的 `Field.setAccessible(true)`、Ruby 中的 `Object#send`、Rust 中的内部 `pub(crate)` 访问）。在内部状态上断言而不是在可观察行为上断言。验证协作者的精确方法调用次数而不是业务结果。 |
| **宽泛的异常断言** | `.NET` 的 `Assert.ThrowsException<Exception>(...)` / `pytest.raises(Exception)` / `expect(fn).toThrow(Error)` 没有消息匹配器 / `assertThrows(Exception.class, ...)` (Java) / `assert.Error(t, err)` 没有检查类型 / `expect { ... }.to raise_error` 没有类 (RSpec) / `#[should_panic]` 没有预期 = "..." / `Should -Throw` 没有预期消息 / `EXPECT_ANY_THROW` 而不是 `EXPECT_THROW(stmt, SpecificType)`。 |
| **弱转换预言者** | 规范化、大小写、修剪、映射或转换测试提供已处于预期形式的输入，因此无操作实现通过，即使断言可能捕获其他缺陷。使用必须改变的输入，并断言独立推导的预期值。生产者/消费者往返测试很有用，但不会取代双方可能共享相同缺陷时的独立格式断言。 |

#### 中——可维护性和清晰度问题

| 反模式 | 要查找的内容 |
|---|---|
| **命名不佳** | 名称如 `Test1`、`TestMethod` 或 `test` 的测试，这些测试没有描述场景或结果。加载扩展时使用扩展；否则遵循同一套件中现有的命名约定。 |
| **魔法值** | 安排/断言中未解释的数字或字符串：`Assert.AreEqual(42, result)` / `assert result == 42` / `expect(result).toBe(42)` —— 42 代表什么？ |
| **重复测试** | 三个或更多具有几乎相同主体、仅在单个输入值上不同的测试方法。应该参数化：`.NET` 的 `[DataRow]`/`[Theory]`/`[TestCase]`、`pytest.mark.parametrize` (pytest)、`test.each` / `it.each` (Jest/Vitest)、`@ParameterizedTest` + `@ValueSource` (JUnit 5)、`@DataProvider` (TestNG)、Go 表驱动测试、`where` / 共享示例 (RSpec)、`#[rstest]` (Rust)、`@ParameterizedTest` + `@MethodSource` (Kotlin)、`-ForEach` / `-TestCases` (Pester)、`INSTANTIATE_TEST_SUITE_P` (GoogleTest)、`SECTION` / `GENERATE` (Catch2)、`TEST_CASE_TEMPLATE` (doctest)。对于 .NET 的详细重复分析，请使用 `exp-test-maintainability`。注意：两个测试覆盖不同的边界条件（例如，零与负数）不是重复的——为不同的边缘情况编写单独的测试提供更清晰的失败诊断，这是有效的实践。 |
| **巨大的测试** | 超过 ~30 行的测试方法或同时测试多个行为的测试。当它们失败时难以诊断。 |
| **重复断言消息** | `Assert.AreEqual(expected, actual, "Expected and actual are not equal")` / `assert x == y, "x is not equal to y"` / `assertEquals(x, y, "values not equal")` 添加了没有信息。消息应描述业务含义。 |
| **缺少 AAA / Given-When-Then 分离** | 安排/行动/断言（或 Given/When/Then 用于 RSpec、Kotest 行为规范、Pester 的 BDD 框架）阶段交错或不可区分。 |

#### 低——风格和卫生

| 反模式 | 要查找的内容 |
|---|---|
| **未使用的测试基础设施** | 无操作的设置/清理挂钩——`.NET` 的 `[TestInitialize]`/`[SetUp]`/`[BeforeEach]`、`setUp`/`@BeforeEach`/`@BeforeAll`、`beforeEach`/`beforeAll`、`before(:each)`/`before(:all)`、`BeforeEach`/`BeforeAll` (Pester)、`setUpWithError` (XCTest) —— 以及从未被调用的测试辅助方法。 |
| **未管理的资源** | 测试创建可丢弃/可关闭的资源而未清理：`.NET` 的 `HttpClient`/`Stream` 没有 `using`、Python 的文件/连接没有 `with` 块或 `try/finally`、Java 的 `FileInputStream` 没有 `try-with-resources`、Go 的 `defer file.Close()` 缺失、Ruby 的连接没有 `ensure`、Rust 的 `Drop` 未依赖/忘记 `close`、任何语言中缺失的临时文件/DB 清理。 |
| **打印调试** | 测试开发期间使用的遗留 `Console.WriteLine` / `Debug.WriteLine` / `print()` / `console.log` / `System.out.println` / `fmt.Println` / `puts` / `dbg!` / `Write-Host` / `std::cout` 语句。 |
| **不一致的命名约定** | 在同一测试类/模块/文件中混合命名风格（例如，一些使用 `Method_Scenario_Expected`，其他人使用 `ShouldDoSomething`）。 |

### 第 4 步：诚实地校准严重程度

在报告之前，根据这些严重程度规则重新检查每个发现：

- **关键/高**：仅用于导致测试给出错误信心或不可靠的 issue。始终通过而不考虑正确性的测试是关键。当用户报告实际顺序依赖性故障或代码证明一个测试需要另一个先运行时，共享的可变状态是高（但 **关键** 当用户报告实际顺序依赖性故障或代码证明一个测试需要另一个先运行时）。异步断言上缺少 await 是关键（静默通过）。
- **中**：仅用于积极损害可维护性的问题——5+ 几乎相同的测试、真正无意义的名称如 `Test1` / `test` / `it1`。
- **低**：美容命名不匹配、轻微的风格偏好、断言消息可以更好。如有疑问，评为低。
- **始终一致地使用调用者的严重程度词汇表**。如果调用者要求 Critical / Warning / Info，将潜在可靠性风险映射到 Warning，将维护/美容问题映射到 Info。保持已证明的错误信心或当前顺序依赖性根本原因 Critical；不要仅仅为了使每个请求的级别非空而降级它。严重程度描述了已证明的失败模式，而不是收到的文本量。
- **将系统发现与其实例分开**。跨外观的覆盖接触是一个关键系统发现，其证据列出了每个受影响的测试。所有无断言的实例，包括最后一个外观方法，保留相同的错误信心严重程度。报告 `1 发现 / 6 受影响的测试`，而不是六个发现加上第七个总结发现，并且不要仅仅为了制造计数不匹配而降级一个实例。
- **不要将普通的缺失案例视为反模式**。相邻的未测试分支、异常路径和边界可能是有用的覆盖机会，但除非现有测试专门创建了差距，否则不要将它们与反模式计数分开。它们不是关键，仅仅因为套件有一个系统性的关键问题。
- **不是问题**（按语言差异）：
  - Go 和 Rust 的 **表驱动循环** 带有子测试（`t.Run` / `for case in cases { ... }`）是 *惯用法*，不是“条件测试逻辑”。**不要标记**。
  - pytest 的 **裸 `assert`** 是标准的断言形式，不是缺少断言库。**不要标记**。
  - Go 测试使用 `if got != want { t.Errorf(...) }` 作为标准的相等性。**不要标记** 为 ad-hoc。
  - 为不同的边界条件编写单独的测试（零与负数与 null）。**不要标记** 为重复。
  - 显式的每个测试设置而不是 `[TestInitialize]` / `beforeEach`（这 *改进* 了隔离性）。
  - 短小清晰的测试，但理论上可以合并。
  - 非平凡的输入的往返或序列化相等。它是有效的元形态证据，不是自比较；仍然建议在生产者和消费者可能共享相同缺陷时保留一个独立的表示。
  - 仅使用已转换的输入测试的转换。将其从同义计数中排除，但在删除转换时仍然通过的情况下报告弱预言者。使用必须改变的输入，并固定其独立预期的输出。
  - 克隆值相等。保留它，并在合同承诺深度复制时添加独立的引用或突变独立性证据。
  - 返回原始值的验证器或访问器，当生产合同是传递时。缺失无效输入案例是一个覆盖差距，而不是证明现有断言是同义的。

**重要提示**：如果测试写得很好，请清晰地说明。不要为了证明审查而夸大严重程度。一个发现零关键/高问题且仅包含轻微低建议的审查是有效且有价值的成果。优先考虑测试做得好的地方。

### 第 5 步：报告发现

**深度条——比未经协助的审查更浅的整洁报告是一个失败。** 在编写之前，满足以下五个：

1. **涵盖范围内的每个测试**。在总结之前构建完整的 方法/字段 清单。对于系统性的模式（如覆盖接触），至少一次列出每个受影响的测试，而不是给出代表性示例。一个发现表在沉默中遗漏测试（或固定件如未使用的 `static HttpClient` 字段）是不完整的。声明审查数量。
2. **在判断预言者之前验证生产合同**。检查实际转换、DTO 字段和承诺的身份/克隆语义。永远不要在生产故意损失的情况下发明字段或要求无损往返。
   对于每个可疑的相等性，在分配发现之前写下独立已知的预言者。如果断言比较已转换的输出与非平凡的输入，克隆状态、快照、模拟验证或框架原生断言上下文，解释为什么它可能失败，然后再称其为同义或无断言。相反，当转换测试使用已归一化的输入时，指出输入无法区分真实的转换与无操作，并提供一个改变的输入加上确切的预期输出。对于配对的 生产者/消费者 API，保留往返测试并添加一个独立的表示预言者，而不是替换有效的元形态证据。
3. **使每个关键/高修复完整且具体**。给出替换断言，并带有 *确切的预期值*（计算折扣、确切的 CSV 行、完整的预期对象），而不是 `// 在此处断言某事` 占位符。
4. **命名明显的相邻差距，而不要扩展到突变分析** —— 当提供生产代码时，在 **相邻的覆盖差距** 部分直接指出与发现直接相关的未测试的抛出、空结果、边界值和往返/文化敏感性风险。使用 `test-gap-analysis` 进行彻底的分支行为差距分析。
5. **保持报告内部一致性**。摘要计数必须等于枚举的发现。发布一个确定的结论：在您写作之前重新考虑所有内容，并且永远不要在输出中留下“等等，那是不对的” / “这个应该失败但没通过”的推理。
6. **使非发现的决定性**。对于干净或大部分干净的较小套件，命名您清除的可疑结构以及使每个有效的框架规则。不要在通用清单或推测性改进下埋葬干净的裁决。

以以下结构呈现发现：

1. **摘要**——发现的总量，按严重程度（关键 / 高 / 中 / 低）细分。如果测试写得很好，请首先进行评估。
2. **关键和高发现**——列出每个，包括：
   - 反模式名称
   - 具体位置（文件、方法名、行）
   - 解释为什么这是一个问题
   - 具体的修复（在有助于显示之前/之后代码时显示）
3. **中低发现**——除非用户想要完整细节，否则总结在表中
4. **积极观察**——指出测试做得好的地方（密封类、特定的异常类型、数据驱动测试、清晰的 AAA 结构、正确的模拟使用、良好的命名）。不要只报告负面问题。

在发布之前，为每个发现分配一个稳定的身份。一个分组行计为一个发现，无论它列出了多少方法；单独的行分别计算。重新计算摘要。保持 `affected tests` 为不同的数字，以便捆绑发现不会造成隐藏的计数不匹配。

### 第 6 步：优先考虑建议

如果发现很多，建议首先修复哪些：

1. **关键**——立即修复，这些测试可能正在给出错误信心
2. **高**——尽快修复，这些会导致易变性或维护负担
3. **中/低**——在相关编辑期间机会主义地修复

## 验证

- [ ] 范围内的每个测试方法都被记录（声明的审查数量；没有沉默地遗漏）
- [ ] 身份和往返发现与生产合同匹配，并且仅使用真实字段
- [ ] 每个发现都包括一个具体位置（而不仅仅是通用警告）
- [ ] 每个关键/高发现都包括一个具体的修复，带有确切的预期值
- [ ] 指出相邻的未测试的错误路径和边界值
- [ ] 摘要计数与枚举的发现匹配
- [ ] 分组发现区分发现计数与受影响测试计数
- [ ] 相邻的覆盖机会不会被膨胀为关键反模式发现
- [ ] 报告涵盖所有类别（断言、隔离、命名、结构）
- [ ] 包括问题在内的积极观察
- [ ] 建议按严重程度排序

## 常见陷阱

| 陷阱 | 解决方案 |
|-------|----------|
| 将风格问题报告为关键 | 命名和格式化是中/低，永远不是关键 |
| 建议重写而不是有针对性的修复 | 显示最小的差异——更改断言，而不是整个测试 |
| 标记有意的设计选择 | 如果 `Thread.Sleep` / `time.sleep` / `time.Sleep` 在测试中测试实际时间，那不是反模式。考虑上下文。 |
| 在干净代码上制造虚假阳性 | 如果测试遵循最佳实践，请这样说。一个审查发现“0 关键，0 高，1 低”是完全有效且有价值的成果。不要为了证明审查而夸大发现。 |
| 将单独的边界测试标记为重复 | 两个测试用于零和负数输入测试不同的边缘情况。只有在 3+ 测试具有真正相同的主体差异时才标记为重复。 |
| 将美容问题评为中 | 名称不匹配（例如，方法名说 `ArgumentException` 但断言 `ArgumentOutOfRangeException`）是低，不是中——测试仍然可以正确工作。 |
| 忽略测试框架 | 使用从语言扩展加载的框架术语；不要用 MSTest 术语描述 pytest 套件。 |
| 忽视森林而只见树木 | 如果 80% 的测试没有断言，请首先提出系统性问题，而不是列出每个实例 |
| 在整洁与深度之间进行权衡 | 严重程度表和积极观察不能替代覆盖每个测试、修复中的确切的预期值以及相邻的错误路径/边界差距 |
| 在报告中自相矛盾 | 首先推理，然后编写每个发现的单一确定裁决——永远不要发出“等等，那是不对的” / “应该失败但没通过”的重新考虑 |
| 计数不匹配 | 摘要的每个严重程度总计必须与您列出的发现匹配 |
