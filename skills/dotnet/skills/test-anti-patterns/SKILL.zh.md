---
name: test-anti-patterns
description: 审计测试文件或测试套件；生成按严重程度排序的诊断报告。始终用于验证无内容、缺失/冗余断言、被吞没/宽泛异常、不稳定/依赖顺序的测试、重复或魔法值。多语言支持。不应用于直接编辑：writing-mstest-tests 拥有提供的 MSTest 断言/属性/生命周期；code-testing-agent 拥有新的测试。排除运行测试、迁移、断言指标（断言质量）、原始 .NET 覆盖率收集（run-tests）、非 .NET 覆盖率收集/分析（原生工具）、项目级 .NET 覆盖率/CRAP（覆盖率分析）、命名目标 .NET CRAP（crap-score）、行为/伪变异差距（test-gap-analysis）、测试混合/成功与错误分类和特征分布（test-tagging），或 testsmells.org 目录（test-smell-detection）。
---

# 测试反模式检测

对任何支持的语言中的测试代码进行快速、务实的分析，以发现破坏测试可靠性、可维护性和诊断价值反模式和质量问题。

> **语言特定指南**：尝试一次 `test-analysis-extensions`。如果不可用，立即继续使用此技能的内置框架规则；切勿因辅助工具而阻塞审计。

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
- 用户要求将 MSTest `DynamicData` 从 `IEnumerable<object[]>` 转换为 `ValueTuple`（使用 `writing-mstest-tests`）
- 用户想要运行或执行测试（使用 `.NET 的 `run-tests`）
- 用户想要在测试框架或版本之间迁移（使用迁移技能）
- 用户想要原始的 .NET 覆盖率收集（使用 `run-tests`），非 .NET 覆盖率收集或分析（使用原生工具），项目范围的 .NET 覆盖率/CRAP 指标（使用 `coverage-analysis`），或命名目标的 .NET CRAP（使用 `crap-score`）
- 用户询问测试是否会捕获错误或想要行为/伪变异差距（使用 `test-gap-analysis`）
- 用户想要测试混合或快乐路径与错误路径分类、标准化标签或特征/类别分布（使用 `test-tagging`）
- 用户想要进行深度正式测试异味审计，具有学术分类和扩展目录（使用 `test-smell-detection`）

## 输入

| 输入 | 是否必需 | 描述 |
|-------|----------|-------------|
| 测试范围 | 否 | 要分析的测试文件、类、目录或项目。如果省略，则从当前工作区发现。 |
| 生产代码 | 否 | 要测试的代码，用于提供测试应验证的上下文 |
| 特定关注点 | 否 | 聚焦区域，如“不稳定性”或“命名”，以缩小审查范围 |

## 工作流程

### 第 1 步：检测语言并加载扩展

在请求输入之前，从当前工作区解析命名测试路径。

如果没有提供路径，则使用存储库清单和常规测试标记从当前目录下发现测试文件。技能上下文的 `Base directory` 是文档存储，不是用户的工作区；切勿相对于它解析目标文件。

如果一个读取器说路径缺失，但工作区通配符/搜索找到了它，请规范化该确切路径并重试。仅在确认读取器可用性、传输或路径规范化失败后，并且验证规范路径仍然位于当前工作区内部时，才使用 shell 文本读取器（Unix 上的 `sed`/`cat`，PowerShell 上的 `Get-Content`）仅用于内容排除、权限/策略、工作区边界或未知失败。停止在内容排除、权限/策略、工作区边界或未知失败时。审计任何允许的读取器可以访问的发现的文件；切勿要求用户粘贴它。如果所有允许的读取器都失败，请报告确切的阻止因素，而不要绕过安全边界。

识别语言和框架。尝试匹配的 `test-analysis-extensions` 指南一次；如果不可用，则使用下面的目录。

### 第 2 步：收集测试代码

在读取正文之前，清点已解析的范围。对于单个文件或类，直接读取该范围。对于项目或套件，一次发现测试文件，在工具允许的情况下批量读取独立内容，并且在每个发现的测试和类级固定装置都具有账本状态时停止。

加载扩展时使用扩展发现标记；否则使用此技能的内置标记（例如 `[TestClass]`/`[Fact]`/`[Test]`、`test_*.py`、`*.test.*`、`*_test.go`、`*_spec.rb`、`#[test]`、`*.Tests.ps1`、`TEST(...)`、`TEST_CASE(...)`）。

不要批量读取无关的生产代码。打开与每个可疑测试对应的每个生产符号，以决定断言、转换、身份合同或相邻差距是否真实。对于系统外观/表面区域模式，每个调用的成员都相关：读取整个小的生产类型或检查每个调用的成员，然后将每个弱测试映射到它应该验证的确切可观察结果、异常、状态变化或边界。

### 第 3 步：扫描反模式

将每个测试文件与下面的反模式目录进行对照。按严重程度分组报告发现。加载扩展时使用扩展映射；否则使用目录中的跨框架示例。

在起草报告之前，制作一个私有的完整性账本，其中每行对应每个测试方法和每个类级固定装置/资源。记录其预言（或缺失）、异常处理、状态/时间依赖性、并发安全性、前提/断言顺序和状态。在每一行都连接到发现或明确判断为可靠之前，不要发布。特别是：

- `actual != oldValue` 是一个弱变异预言：它接受每个错误的新值。要求确切的预期值。
- 包括未使用或未释放的类级资源；仅扫描方法会遗漏字段，例如静态 `HttpClient`。
- 将未同步的静态/全局集合视为既顺序耦合又并行不安全的，当测试读取和写入它时。还标记在断言之前解除引用可空结果。

#### 关键 -- 给出错误自信的测试

| 反模式 | 查找内容 |
|---|---|
| **无断言** | 执行代码但从未断言任何内容的测试方法。没有断言的通过测试证明不了任何东西。在 .NET 中查找缺少 `Assert.*`；在 pytest 中查找没有 `assert` 和没有 `pytest.raises` 的函数；在 Jest 中查找没有 `expect(...)`；在 JUnit 中查找没有 `assert*`/`assertThat`；在 Go 中查找从未调用 `t.Error*`、`t.Fatal*` 或 testify 的测试；在 RSpec 中查找没有 `expect` 的块；在 Pester 中查找没有 `Should`。模拟调用验证（`verify(mock)`、`expect(mock).toHaveBeenCalled`、`Should -Invoke`）是真实的断言。 |
| **异步断言上缺少 await (JS/TS、.NET、Python、Kotlin、Swift)** | `expect(promise).resolves.toBe(x)` 没有 `await`/`return`，`pytest-asyncio` 测试中未等待的协程，`async Task` xUnit 测试调用 `Assert.ThrowsAsync` 而没有 `await`，Kotest 悬停测试而未 `runTest`，Swift 测试异步测试而未 `await`。这些测试即使在底层断言会失败时也会静默通过。 |
| **覆盖率接触** | 系统地调用类型上每个公共成员的测试类——通常按字母顺序或声明顺序——而不断言有意义的结果。每个测试通常执行 `var result = sut.MethodName(...)`（或 `result = sut.method_name(...)`、`sut.methodName()`、`sut.MethodName(t)`）而没有断言，或者只有简单的 null/None/nil 检查。目的是虚增代码覆盖率指标，而不是验证行为。与单个无断言的测试不同：该模式是 *系统性地* 覆盖表面区域，而没有实际验证。 |
| **自引用断言** | 预期值是从相同的实际值计算得出的，例如 `Assert.AreEqual(dto.Name, dto.Name)`、`Assert.AreEqual(result, result)` 或等效项。不要仅仅因为有效的身份、克隆、序列化或往返合同将输出与输入进行比较而应用此标签：这些断言可能会失败。相反，检查输入是否执行了转换，以及是否缺少独立已知的表示、字段、引用身份或无效输入断言。 |
| **被吞没的异常** | `try { ... } catch { }`，没有重新抛出或断言的 `catch (Exception)` (.NET)；裸 `except:` 或 `except Exception:` 与 `pass` (Python)；`try { ... } catch (e) {}` (JS/TS/Java)；`defer recover()` 而没有重新恐慌和没有断言 (Go)；`rescue StandardError` 没有断言 (Ruby)；`Result::unwrap_or(...)` 在测试中吞没错误 (Rust)；空的 `catch` 块 (Kotlin/Swift)。 |
| **仅在 catch 块中断言** | `try { Act(); } catch (Exception ex) { Assert.Fail(ex.Message); }`（以及其他语言中的等效项）——使用 `Assert.ThrowsException` / `pytest.raises` / `expect(fn).toThrow` / `assertThrows` / `assert.Error(t, err)` / `#[should_panic]` / `Should -Throw` / `EXPECT_THROW`。测试在没有抛出异常时通过，即使结果错误。 |
| **始终为真的断言** | `Assert.IsTrue(true)`、`Assert.AreEqual(x, x)`、`assert True`、`expect(true).toBe(true)`、`assert.True(t, true)`、`assert!(true)`，或条件永远无法失败。 |
| **注释掉的断言** | 被禁用但测试仍然运行的断言，给人以覆盖的错觉。 |

#### 高 -- 可能导致痛苦的测试

| 反模式 | 查找内容 |
|---|---|
| **不稳定性指标** | 墙上时钟睡眠/等待用于同步：`.NET 的 `Thread.Sleep` / `Task.Delay`、`time.sleep` (Python)、`setTimeout` / `await new Promise(r => setTimeout(...))` (JS/TS)、`Thread.sleep` (Java/Kotlin)、`time.Sleep` (Go)、`sleep` (Ruby/Bash)、`std::thread::sleep` (Rust)、`Start-Sleep` (Pester)、`std::this_thread::sleep_for` (C++)。墙上时钟读取而不抽象：`DateTime.Now`/`UtcNow`、`datetime.now()`/`datetime.utcnow()`、`Date.now()` / `new Date()`、`System.currentTimeMillis()`、`time.Now()`、`Time.now`、`Instant::now()`、`Date()`/`Date.now`、`Get-Date`、`std::chrono::system_clock::now`。未播种的随机性：`new Random()`、`random.random()`/`random.randint()`、`Math.random()`、`new Random()` (Java/Kotlin)、`rand.Int()` 而没有种子、`rand` (Ruby)、`rand::random()` (Rust)。环境依赖的路径（硬编码 `C:\...`、`/tmp/...`、网络主机）。 |
| **测试顺序依赖** | 跨测试修改的静态/全局可变状态；没有完全重置状态的设置（`.NET 的 `[TestInitialize]`、`setUp`、`beforeEach`、`before(:each)`、`BeforeEach`、`t.Cleanup`）；当单独运行时失败但在套件中通过（反之亦然）的测试。每种语言的示例：`.NET/Java 的静态字段`、`Python 的模块级全局变量`、测试文件中的顶层 `let`/`const` (JS/TS)、`Go 的 var 包全局变量`、`Ruby 的类变量`、`Rust 的静态 mut`/`lazy_static!`/`OnceCell`、`PowerShell 的 $script:` 变量。 |
| **过度模拟** | 模拟设置行数多于实际测试逻辑。在模拟上验证确切的调用序列而不是结果。模拟测试拥有的类型。每种语言的示例：`.NET 的 Moq/NSubstitute/FakeItEasy`、`Python 的 `unittest.mock` / `pytest-mock`、`JS/TS 的 Jest auto-mocks / Sinon`、`Java 的 Mockito/PowerMock`、`Go 的 gomock/testify mock`、`Ruby 的 RSpec mocks/mocha`、`Rust 的 `mockall`、`Kotlin 的 MockK`、`PowerShell 的 `Mock` cmdlet`、`C++ 的 gmock`。对于 .NET 中的深度模拟审计，使用 `exp-mock-usage-analysis`。 |
| **实现耦合** | 通过反射测试私有方法（`.NET 的 `MethodInfo.Invoke`、Python 的 `getattr`、TS 中的 `(thing as any)`、Java 中的 `Field.setAccessible(true)`、Ruby 中的 `Object#send`、Rust 中的内部 `pub(crate)` 访问）。在内部状态上断言而不是可观察的行为。验证协作者的精确方法调用次数而不是业务结果。 |
| **宽泛的异常断言** | `.NET 的 `Assert.ThrowsException<Exception>(...)` / `pytest.raises(Exception)` / `expect(fn).toThrow(Error)` 没有消息匹配器 / `assertThrows(Exception.class, ...)` (Java) / `assert.Error(t, err)` 没有检查类型 / `expect { ... }.to raise_error` 没有类 (RSpec) / `#[should_panic]` 没有预期 = "..." / `Should -Throw` 没有预期消息 / `EXPECT_ANY_THROW` 而不是 `EXPECT_THROW(stmt, SpecificType)`。 |
| **弱转换预言** | 规范化、大小写转换、修剪、映射或转换测试提供已处于预期形式的输入，因此无操作实现通过，即使断言可能会捕获其他缺陷。使用必须改变的输入并断言独立派生的预期值。生产者/消费者往返是有用的，但当双方都可能共享相同缺陷时，并不能替代独立的格式断言。 |

#### 中 -- 可维护性和清晰度问题

| 反模式 | 查找内容 |
|---|---|
| **命名不佳** | 像测试1、TestMethod 或 test 这样的测试名称，它们不能描述场景或结果。加载扩展时使用；否则遵循同一套件中现有的命名约定。 |
| **魔法值** | 安排/断言中未解释的数字或字符串：`.NET 的 `Assert.AreEqual(42, result)` / `assert result == 42` / `expect(result).toBe(42)` —— 42 是什么意思？ |
| **重复测试** | 三个或更多具有近乎相同正文但仅输入值不同的测试方法。应该参数化：`.NET 的 `[DataRow]`/`[Theory]`/`[TestCase]`、`pytest 的 `@pytest.mark.parametrize`、`Jest/Vitest 的 `test.each` / `it.each`、`JUnit 5 的 `@ParameterizedTest` + `@ValueSource`、`TestNG 的 `@DataProvider`、Go 表格驱动测试、`RSpec 的 `where` / shared examples`、`Rust 的 `#[rstest]`、`Kotlin 的 `@ParameterizedTest` + `@MethodSource`、`Pester 的 `-ForEach` / `-TestCases`、`GoogleTest 的 `INSTANTIATE_TEST_SUITE_P`、`Catch2 的 `SECTION` / `GENERATE`、`doctest 的 `TEST_CASE_TEMPLATE`。对于 .NET 中的详细重复分析，使用 `exp-test-maintainability`。注意：两个测试覆盖不同的边界条件（例如，零与负数）不是重复的——为不同的边缘情况提供单独的测试提供更清晰的失败诊断，并且是有效的实践。 |
| **巨大的测试** | 超过 ~30 行的测试方法或同时测试多个行为的测试。当它们失败时难以诊断。 |
| **重复断言消息** | `.NET 的 `Assert.AreEqual(expected, actual, "Expected and actual are not equal")` / `assert x == y, "x is not equal to y"` / `assertEquals(x, y, "values not equal")` 添加了没有信息。消息应描述业务含义。 |
| **缺少 AAA / Given-When-Then 分离** | 安排/执行/断言（或 Given/When/Then 用于 RSpec、Kotest 行为规范、Pester 等行为驱动开发框架）阶段交错或不可区分。 |

#### 低 -- 风格和卫生

| 反模式 | 查找内容 |
|---|---|
| **未使用的测试基础设施** | 无操作的设置/清理钩子——`.NET 的 `[TestInitialize]`/`[SetUp]`/`[BeforeEach]`、`setUp`/`@BeforeEach`/`@BeforeAll`、`beforeEach`/`beforeAll`、`before(:each)`/`before(:all)`、`BeforeEach`/`BeforeAll` (Pester)、`setUpWithError` (XCTest) ——以及从未调用的测试辅助方法。 |
| **未管理的资源** | 测试创建可丢弃/可关闭资源而未清理：`.NET 的 `HttpClient`/`Stream` 没有 `using`、Python 的文件/连接没有 `with` 块或 `try/finally`、Java 的 `FileInputStream` 没有 `try-with-resources`、Go 的 `defer file.Close()` 缺失、Ruby 的连接没有 `ensure`、Rust 的 `Drop` 未依赖/忘记 `close`、任何语言中缺失临时文件/DB 的清理。 |
| **打印调试** | 测试开发期间使用的遗留 `Console.WriteLine` / `Debug.WriteLine` / `print()` / `console.log` / `System.out.println` / `fmt.Println` / `puts` / `dbg!` / `Write-Host` / `std::cout` 语句。 |
| **不一致的命名约定** | 在同一测试类/模块/文件中混合命名风格（例如，一些使用 `Method_Scenario_Expected`，另一些使用 `ShouldDoSomething`）。 |

### 第 4 步：诚实地校准严重程度

在报告之前，重新检查每个发现是否符合这些严重程度规则：

- **严重/高**: 仅适用于导致测试产生虚假信心或不稳定的问题。一个无论正确与否始终通过的测试是严重的。当共享可变状态存在潜在的隔离风险时，它是高的；但当用户报告了实际的顺序依赖性故障或代码证明某个测试需要另一个测试先运行时，它是严重的。异步断言中的缺失等待（missing-await）是严重的（静默通过）。
- **中等**: 仅适用于主动损害可维护性的问题——5个以上的几乎相同的测试、真正无意义的名称，如 `Test1` / `test` / `it1`。
- **低**: 容饰性命名不匹配、轻微的风格偏好、断言消息可以更好。如有疑问，评为低。
- **始终使用调用者的严重性词汇表保持一致性**。如果调用者要求 Critical / Warning / Info，将潜在的可靠性风险映射到 Warning，将维护性/容饰性问题映射到 Info。保留已证明的虚假信心或当前顺序依赖性根本原因的严重性为 Critical；不要仅仅为了使每个请求的级别非空而降级它。严重性描述的是已证明的故障模式，而不是发现收到的文本量。
- **将系统性发现与其实例分开**。跨越外观的覆盖率是一个严重的系统性发现，其证据列表列出了每个受影响的测试。所有无断言的实例，包括最后一个外观方法，保留相同的虚假信心严重性。报告 `1 个发现 / 6 个受影响的测试`，而不是六个发现加上第七个总结发现，并且不要仅仅为了制造多个级别而降级一个实例。
- **不要将普通缺失案例作为反模式进行严重性排序**。相邻的未测试分支、异常路径和边界可能是有用的覆盖率机会，但除非一个现有的弱测试特别创建了这种差距，否则将它们与反模式计数分开列出。仅仅因为套件存在系统性的严重问题，它们并不是严重的。
- **不是问题**（按语言差异）：
  - Go 和 Rust 的 **表格驱动循环**（`t.Run` / `for case in cases { ... }`）是 *惯用法*，不是“条件测试逻辑”。不要标记。
  - pytest 的 **裸 `assert`** 是标准的断言形式，不是缺失断言库。不要标记。
  - Go 测试使用 `if got != want { t.Errorf(...) }` 作为标准的等价性。不要作为临时性标记。
  - 为不同的边界条件编写单独的测试（零与负数与空）。不要标记为重复。
  - 显式的每个测试设置而不是 `[TestInitialize]` / `beforeEach`（这 *改进* 了隔离性）。
  - 短小清晰的测试，但理论上可以合并。
  - 往返或序列化等价性，输入非平凡。这是有效的元变形证据，不是自我比较；仍然建议在生产者和消费者可能共享缺陷时使用一个独立的表示形式。
  - 仅使用已转换输入测试的转换。将其从同义反复计数中排除，但在移除转换时仍然通过，请报告弱预言机。使用必须改变的输入并固定其独立预期的输出。
  - 克隆值等价性。保留它，并在合同承诺深度复制时添加不同的引用或突变独立性证据。
  - 验证器或访问器在生产合同中返回原始值时通过传递。缺失无效输入案例是覆盖率差距，而不是证明现有断言是同义反复的证据。

重要提示：如果测试写得很好，请清晰地说明这一点。不要夸大严重性来证明审查。一个发现零个严重/高问题且仅提出轻微低建议的审查是一个有效且有价值的结果。优先考虑测试做得好的地方。

### 第 5 步：报告发现

**深度条——比非协助审查更简洁的报告是一个失败**。在编写之前，满足所有五个条件：

1. **涵盖范围内的每个测试**。在总结之前构建完整的方法/字段清单。对于覆盖率跨越这样的系统性模式，至少一次列出每个受影响的测试，而不是给出代表性示例。一个在测试（或类似未使用的 `static HttpClient` 字段）中沉默跳过测试的发现表是不完整的。说明审查数量。
2. **在判断预言机之前验证生产合同**。检查实际转换、DTO 字段和承诺的身份/克隆语义。永远不要在生产是故意有损的情况下发明字段或要求无损往返。
   对于每个可疑的等价性，在分配发现之前写下独立已知的预言机。如果断言将转换的输出与非平凡输入进行比较，则解释为什么它在调用它为同义反复或无断言之前会失败。相反，当转换测试使用已归一化的输入时，指出输入无法区分真实的转换与无操作，并提供一个变化的输入加上精确的预期输出。对于成对的生产者/消费者 API，保留往返测试并添加一个独立的表示形式预言机，而不是替换有效的元变形证据。
3. **使每个严重/高修复完整和具体**。给出替换断言与 *精确预期值*（计算折扣、精确 CSV 行、完整预期对象），而不是 `// 在这里断言某事` 占位符。
4. **命名明显的相邻差距，而不要扩展到突变分析**——当提供生产代码时，直接注意相关的未测试抛出、空结果、边界值和往返/文化敏感性风险，在 **相邻覆盖率差距** 部分中。使用 `test-gap-analysis` 进行彻底的逐分支行为差距。
5. **保持报告内部一致性**。摘要计数必须等于列出的发现。发布一个确定的结论：在编写之前重新考虑所有内容，并且永远不要在输出中留下“等等，那是不对的” / “这应该失败但没通过”的推理。
6. **使非发现决定性**。对于干净或大部分干净的较小套件，命名你清除的可疑结构以及使每个有效的框架规则。不要在通用清单或推测性改进下掩盖干净的裁决。

以这种结构呈现发现：

1. **摘要**——发现的总量，按严重性（严重/高/中/低）细分。如果测试写得很好，请首先进行评估。
2. **严重和高发现**——列出每个，包括：
   - 反模式的名称
   - 具体的位置（文件、方法名、行）
   - 简要解释为什么它是问题
   - 具体的修复（在有帮助时显示前后代码）
3. **中低发现**——除非用户想要完整细节，否则总结在表中
4. **积极观察**——指出测试做得好的地方（密封类、特定异常类型、数据驱动测试、清晰的 AAA 结构、正确的假人使用、好的命名）。不要只报告负面问题。

在发布之前，为每个发现分配一个稳定的身份。一个分组行计为一个发现，无论它列出了多少方法；单独的行分别计算。从这些行重新计算摘要。保持 `affected tests` 作为不同的数字，以便一个捆绑的发现不会造成隐藏的计数不匹配。

### 第 6 步：优先推荐建议

如果有许多发现，建议首先修复哪些：

1. **严重**——立即修复，这些测试可能正在产生虚假信心
2. **高**——尽快修复，这些导致不稳定或维护负担
3. **中/低**——在相关编辑期间机会主义修复

## 验证

- [ ] 范围内的每个测试方法都被涵盖（说明审查数量；没有沉默跳过）
- [ ] 身份和往返发现与生产合同匹配，并且只使用实际字段
- [ ] 每个发现都包括具体位置（不仅仅是通用警告）
- [ ] 每个严重/高发现都包括具体的修复和精确预期值
- [ ] 相邻的未测试错误路径和边界值被指出
- [ ] 摘要计数与列出的发现匹配
- [ ] 分组发现区分发现计数与受影响测试计数
- [ ] 相邻的覆盖率机会没有被夸大为严重的反模式发现
- [ ] 报告涵盖所有类别（断言、隔离性、命名、结构）
- [ ] 积极观察与问题一起包含
- [ ] 建议按严重性优先排序

## 常见陷阱

| 陷阱 | 解决方案 |
|------|----------|
| 将样式问题报告为严重 | 命名和格式是中/低，永远不会严重 |
| 建议重写而不是有针对性的修复 | 显示最小的差异——更改断言，而不是整个测试 |
| 标记有意的设计选择 | 如果 `Thread.Sleep` / `time.sleep` / `time.Sleep` 在集成测试中测试实际时间，那不是反模式。考虑上下文 |
| 在干净代码上制造虚假阳性 | 如果测试遵循最佳实践，请这样说。一个审查发现“0 严重，0 高，1 低”是完全有效的。不要夸大发现来证明审查 |
| 标记单独的边界测试为重复 | 两个测试用于零和负数输入测试不同的边缘情况。只有在 3 个或更多测试具有真正相同的主体且仅由单个值不同时才标记为重复 |
| 将容饰性问题评为中 | 命名不匹配（例如，方法名说 `ArgumentException` 但断言 `ArgumentOutOfRangeException`）是低，不是中——测试仍然正确工作 |
| 忽略测试框架 | 使用从语言扩展加载的框架的术语；不要用 MSTest 术语描述 pytest 套件 |
| 忽视森林而只看树木 | 如果 80% 的测试没有断言，请首先提出系统性问题，而不是列出每个实例 |
| 用整洁性换取深度 | 严重性表和积极观察不能替代涵盖每个测试、修复中的精确预期值和相邻错误路径/边界差距 |
| 在报告中自相矛盾 | 首先推理，然后为每个发现写一个确定的裁决——永远不要发出“等等，那是不对的” / “应该失败但没通过”的重新考虑 |
| 计数不匹配 | 摘要的每个严重性总计必须与您列出的发现匹配 |
