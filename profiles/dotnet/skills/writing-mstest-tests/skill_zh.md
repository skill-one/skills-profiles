# 编写 MSTest 测试

帮助用户编写有效的 MSTest 单元测试，同时不超出项目已安装测试堆栈的 API 级别或约定。

## 仓库覆盖层

对于每个仓库范围的任务，只要允许只读文件检查，就应在任何其他发现之前检查仓库根目录下的 `.agents/skill-overlays/dotnet-test/writing-mstest-tests.md`。这包括那些要求代码或建议但不进行编辑的请求；“不要执行”并不禁止读取覆盖层。如果存在，请在采取任何行动之前读取一次，并应用其特定于仓库的命名、布局、框架和政策绑定。要求其前言声明 `core: dotnet-test/writing-mstest-tests`、`binding-revision: "1"` 和 `mode: extend`。如果任何值缺失或不同，则报告不匹配，忽略覆盖层，并继续使用此技能的可移植指导。明确的用户指令和经过验证的项目约束优先于覆盖层；覆盖层优先于此技能中的可移植默认值和示例。如果文件存在但不可读或与仓库冲突，则报告问题，忽略覆盖层，并继续使用可移植指导，同时遵守经过验证的项目约束。如果它不存在，则继续正常操作。

仅当任务未绑定到仓库或用户明确禁止所有文件/工具访问时才跳过查找。覆盖层不能扩展工具权限或任务的范围。

## 何时使用

- 用户希望通过实施具体的修复来改进或现代化现有的 MSTest 测试
- 用户询问有关 MSTest 断言 API、数据驱动模式或测试生命周期的问题
- 用户要求将 `Assert.IsTrue` 替换为更具体的断言（集合、空值、类型、比较）
- 用户要求在测试中用类型检查断言替换硬类型转换
- 用户需要帮助修复特定的 MSTest 测试错误或失败的断言
- 用户要求修复或理解 MSTest 分析器诊断（`MSTESTxxxx` 警告/错误）

## 何时不使用

- 用户需要进行测试质量审计、反模式检测或不可靠测试调查（使用 `test-anti-patterns`）
- 用户需要运行或执行测试（使用 `run-tests` 技能）
- 用户需要从 MSTest v1/v2 升级到 v3（使用 `migrate-mstest-v1v2-to-v3`）
- 用户需要从 MSTest v3 升级到 v4（使用 `migrate-mstest-v3-to-v4`）
- 用户需要 CI/CD 管道配置
- 用户正在使用 xUnit、NUnit 或 TUnit（不是 MSTest）

## 输入

| 输入 | 是否必需 | 描述 |
|-------|----------|-------------|
| 要测试的代码 | 否 | 要测试的生产代码 |
| 现有的测试代码 | 否 | 要修复、更新或现代化的当前测试 |
| 测试场景描述 | 否 | 用户希望测试的行为 |

## 响应指南

- **具体的 API 或模式问题**（断言、数据驱动、生命周期）：直接跳转到相关的流程步骤。不要遵循完整的流程。
- **从头开始生成新测试**：将任务交接给 `code-testing-agent`；仅将此技能用作 MSTest API/版本指导的辅助。
- **审查和修复现有测试**：仅修复现有问题。不要添加不相关的改进。
- **断言转换**：显示正确的调用，然后在一句中说明语义原因。对于 `Assert.AreEqual`，首先命名 `expected`，然后是 `actual`，并解释这保留了预期/实际失败标签。
- **绑定/比较转换**：保留条件，并将预期的边界（s）放在前面，将观察到的值放在最后：`score > 0` -> `Assert.IsGreaterThan(0, score)`，`score < 100` -> `Assert.IsLessThan(100, score)`，以及 `score >= 60 && score <= 90` -> `Assert.IsInRange(60, 90, score)`。永远不要反转这些参数以模仿源表达式的从左到右顺序。
- **异常转换**：在 lambda 中范围化抛出操作，区分 `ThrowsExactly<T>`（确切类型）与 `Throws<T>`（类型或派生类型），并在属性（如 `ParamName`）是行为的一部分时捕获返回的异常。
- **提供的代码请求**：返回完整的代表性方法体，而不是仅注释的占位符。保留实际操作并显示对称的设置/清理，当生命周期或环境策略是请求的一部分时。

## 流程

### 第 1 步：确定项目设置

检查测试项目、`packages.config` 和汇编引用 `HintPath` 值，以确定 MSTest 的确切版本和项目系统：

- 如果使用 `MSTest.Sdk`：从项目 SDK 声明或 `global.json` `msbuild-sdks` 中解析其确切版本；不要假设最新的 API
- 如果使用 `MSTest` 通用包：解析其确切包版本
- 如果使用 `MSTest.TestFramework` + `MSTest.TestAdapter`：检查版本以确定功能可用性
- 如果使用经典的非 SDK XML（`ToolsVersion`、`Microsoft.CSharp.targets`、显式的 `<Compile Include>`）和/或 `packages.config`：保留该项目系统，并将每个新测试文件添加到 `<Compile Include>`。

还检查代表性测试以了解自定义基础固定件、辅助库、模拟语法、命名、设置和数据构建器。现有约定和安装版本优先于下面的示例。除非用户明确要求迁移，否则不要升级 MSTest、Moq、NBuilder 或项目格式。

### MSTest API 可用性

| API/模式 | 最低版本 | 兼容的回退 |
|---|---:|---|
| `Assert.ThrowsExactly*`，统一的 `Assert.Contains` / `HasCount` / `IsEmpty` / `IsNotEmpty` | 3.8 | `Assert.ThrowsException*`，`CollectionAssert`，`StringAssert` |
| `Assert.IsGreaterThan`，`IsLessThan`，`IsInRange`，`StartsWith`，`EndsWith`，`MatchesRegex` | 3.10 | `Assert.IsTrue` 带有明确的消息，或 `StringAssert` |
| 泛型 `Assert.IsInstanceOfType<T>(value, out var typed)` | 3.4-3.11 仅 | 非泛型断言然后在 3.0-3.3 上进行后断言转换；v4 直接返回类型化的值 |
| ValueTuple `DynamicData` | 3.7 | `IEnumerable<object[]>` |
| `TestContext` 的构造函数注入 | 3.6 | 实例 `TestContext` 属性 |
| `[Retry]`，`[OSCondition]` | 3.8 | 没有内置的重试/OS 条件；修复不可靠性或保留现有的条件机制 |
| `[CICondition]` | 3.10 | 现有的项目特定条件机制 |

例如，MSTest 3.5.x 不能接收 `Assert.ThrowsExactly`、`Assert.Contains`、ValueTuple `DynamicData` 或构造函数注入的 `TestContext`。

将其视为一个硬门槛：确定版本后，不要从此技能中复制一个较新版本的示例，除非其最低版本得到满足。

仅对真正新的项目推荐 MSTest.Sdk 或 MSTest 通用包：

```xml
<!-- 选项 1：MSTest SDK（最简单，推荐用于新项目） -->
<Project Sdk="MSTest.Sdk">
  <PropertyGroup>
    <TargetFramework>net9.0</TargetFramework>
  </PropertyGroup>
</Project>
```

使用 `MSTest.Sdk` 时，将版本放在 `global.json` 中而不是项目文件中，以便所有测试项目一起更新：

```json
{
  "msbuild-sdks": {
    "MSTest.Sdk": "3.8.2"
  }
}
```

```xml
<!-- 选项 2：MSTest 通用包 -->
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net9.0</TargetFramework>
  </PropertyGroup>
  <ItemGroup>
    <PackageReference Include="MSTest" Version="3.8.2" />
  </ItemGroup>
</Project>
```

### 第 2 步：遵循约定编写测试类

仅在没有与套件的现有基础类和生命周期冲突的地方应用这些结构约定：

- **用 `sealed` 封装测试类**以获得性能和设计清晰度
- 在类上使用 `[TestClass]`，在测试方法上使用 `[TestMethod]`
- 遵循 **Arrange-Act-Assert**（AAA）模式
- 使用 `MethodName_Scenario_ExpectedBehavior` 命名测试
- 使用单独的测试项目，命名约定为 `[ProjectName].Tests`

```csharp
[TestClass]
public sealed class OrderServiceTests
{
    [TestMethod]
    public void CalculateTotal_WithDiscount_ReturnsReducedPrice()
    {
        // Arrange
        var service = new OrderService();
        var order = new Order { Price = 100m, DiscountPercent = 10 };

        // Act
        var total = service.CalculateTotal(order);

        // Assert
        Assert.AreEqual(90m, total);
    }
}
```

### 第 3 步：使用与版本兼容的断言 API

选择安装的 MSTest 版本支持的最具体的断言。更具体的断言会产生更好的失败消息，并使测试意图更清晰，但不可编译的“现代化”断言比兼容的 `StringAssert`、`CollectionAssert` 或 `Assert.IsTrue` 调用更糟。

| 你正在测试的内容 | 断言 |
|---|---|
| 两个值相等 | `Assert.AreEqual(expected, actual)` |
| 相同的对象实例（引用身份） | `Assert.AreSame(expected, actual)` |
| 值为 null | `Assert.IsNull(value)` |
| 值不为 null | `Assert.IsNotNull(value)` |
| 集合为空 | `Assert.IsEmpty(collection)`（3.8+）或 `CollectionAssert` / 计数断言 |
| 集合不为空 | `Assert.IsNotEmpty(collection)`（3.8+）或计数断言 |
| 集合恰好有 N 个项 | `Assert.HasCount(N, collection)`（3.8+）或 `Assert.AreEqual` 对计数 |
| 集合包含一个项 | `Assert.Contains(item, collection)`（3.8+）或 `CollectionAssert.Contains` |
| 集合不包含一个项 | `Assert.DoesNotContain(item, collection)`（3.8+）或 `CollectionAssert.DoesNotContain` |
| 对象是特定类型 | `Assert.IsInstanceOfType<T>(value)` |
| 代码抛出异常 | `Assert.ThrowsExactly<T>`（3.8+）或 `Assert.ThrowsException<T>`（较早版本） |

在 MSTest 3.8+ 上，优先选择 `Assert` 类方法而不是 `StringAssert` 或 `CollectionAssert`（如果两者都存在）。较旧版本应保留兼容的专用类。
当请求多个独立的集合属性时，即使另一个断言碰巧暗示了它，也要保留每个语义检查的显式性。例如，当请求的诊断区分空/非空时，保留 `IsNotEmpty`，然后使用 `HasCount` 和 `ContainsSingle` 为其各自的基数保证。

#### 相等性、null 和引用检查

```csharp
Assert.AreEqual(expected, actual);      // 值相等
Assert.AreSame(expected, actual);       // 引用相等 -- 相同的对象实例
Assert.IsNull(value);
Assert.IsNotNull(value);
```

#### 异常测试

```csharp
// MSTest 3.8+
var ex = Assert.ThrowsExactly<ArgumentNullException>(() => service.Process(null));
Assert.AreEqual("input", ex.ParamName);

// 异步
var ex = await Assert.ThrowsExactlyAsync<InvalidOperationException>(
    async () => await service.ProcessAsync(null));
```

- `Assert.Throws<T>` 匹配 `T` 或任何派生类型
- `Assert.ThrowsExactly<T>` 仅匹配确切的类型 `T`

在 MSTest 3.7 及更早版本中，使用兼容的 API：

```csharp
var ex = Assert.ThrowsException<ArgumentNullException>(
    () => service.Process(null));
```

#### 集合断言

```csharp
// MSTest 3.8+
Assert.Contains(expectedItem, collection);
Assert.DoesNotContain(unexpectedItem, collection);
var single = Assert.ContainsSingle(collection);  // 返回单个元素
Assert.HasCount(3, collection);
Assert.IsEmpty(collection);
Assert.IsNotEmpty(collection);
```

在较旧版本中使用 `CollectionAssert.Contains`、`CollectionAssert.DoesNotContain` 和 `Assert.AreEqual(expectedCount, collection.Count)`。

用专门的断言替换泛型 `Assert.IsTrue` -- 它们会给出更好的失败消息：

| 代替 | 使用 |
|---|---|
| `Assert.IsTrue(list.Count > 0)` | `Assert.IsNotEmpty(list)` |
| `Assert.IsTrue(list.Count == 0)` | `Assert.IsEmpty(list)` |
| `Assert.IsTrue(list.Count() == 3)` | `Assert.HasCount(3, list)` |
| `Assert.IsTrue(x != null)` | `Assert.IsNotNull(x)` |
| `Assert.IsTrue(x == null)` | `Assert.IsNull(x)` |
| `Assert.AreEqual(a, b)` 对相同实例 | `Assert.AreSame(a, b)` -- 引用身份 |
| `Assert.IsTrue(!list.Contains(item))` | `Assert.DoesNotContain(item, list)` |
| `list.Single(predicate)` + `Assert.IsNotNull` | `Assert.ContainsSingle(list)` |
| `Assert.IsTrue(list.Contains(item))` | `Assert.Contains(item, list)` |

#### 字符串断言

```csharp
// MSTest 3.10+
Assert.Contains("expected", actualString);
Assert.StartsWith("prefix", actualString);
Assert.EndsWith("suffix", actualString);
Assert.MatchesRegex(@"\d{3}-\d{4}", phoneNumber);
```

在较旧版本中使用 `StringAssert.Contains`、`StringAssert.StartsWith`、`StringAssert.EndsWith` 和 `StringAssert.Matches`。

#### 类型断言

MSTest 3.x 不是单一的 API 级别。选择安装的次要版本支持的形式：

```csharp
// MSTest 3.0-3.3
Assert.IsInstanceOfType(result, typeof(MyHandler));
var typed = (MyHandler)result; // 安全，因为断言阻止了不匹配。
```

```csharp
// MSTest 3.4-3.11 -- out 参数
Assert.IsInstanceOfType<MyHandler>(result, out var typed);
typed.Handle();
```

```csharp
// MSTest 4.x -- 直接返回已证明的值
var typed = Assert.IsInstanceOfType<MyHandler>(result);
```

#### 比较断言

```csharp
Assert.IsGreaterThan(lowerBound, actual);
Assert.IsLessThan(upperBound, actual);
Assert.IsInRange(low, high, actual);
```

### 第 4 步：使用数据驱动测试进行多个输入

#### DataRow 用于行内值

```csharp
[TestMethod]
[DataRow(1, 2, 3)]
[DataRow(0, 0, 0, DisplayName = "Zeros"]
[DataRow(-1, 1, 0]
public void Add_ReturnsExpectedSum(int a, int b, int expected)
{
    Assert.AreEqual(expected, Calculator.Add(a, b));
}
```

#### DynamicData 与 ValueTuples（用于复杂数据的首选）

在 MSTest 3.7+ 上，优先选择 `ValueTuple` 返回类型而不是 `IEnumerable<object[]>` 以获得类型安全性。在较旧版本上保留 `IEnumerable<object[]>`。

元组元素命名记录了哪个位置映射到哪个测试参数，元组元素类型在编译时捕获不兼容的值。它们**不**使 `DynamicData` 位置无关，并且即使两个同类型的元素交换也可以编译。不要声称其他情况。当行需要自定义显示名称或元数据而不是仅类型化的位置数据时，在 MSTest 3.8+ 上使用 `TestDataRow<T>`。

```csharp
[TestMethod]
[DynamicData(nameof(DiscountTestData)]
public void ApplyDiscount_ReturnsExpectedPrice(decimal price, int percent, decimal expected)
{
    var result = PriceCalculator.ApplyDiscount(price, percent);
    Assert.AreEqual(expected, result);
}

// ValueTuple -- 首选（MSTest 3.7+）
public static IEnumerable<(decimal price, int percent, decimal expected)> DiscountTestData =>
[
    (100m, 10, 90m),
    (200m, 25, 150m),
    (50m, 0, 50m),
];
```

当您需要在 MSTest 3.8+ 上为每个测试用例提供元数据时，使用 `TestDataRow<T>`：

```csharp
public static IEnumerable<TestDataRow<(decimal price, int percent, decimal expected)>> DiscountTestDataWithMetadata =>
[
    new((100m, 10, 90m)) { DisplayName = "10% discount" },
    new((200m, 25, 150m)) { DisplayName = "25% discount" },
    new((50m, 0, 50m)) { DisplayName = "No discount" },
];
```

### 第 5 步：正确处理测试生命周期

- 当现有套件支持时，优先使用构造函数初始化；保留共享的 `FixtureBase<TSut>` 或已建立的 `[TestInitialize]` 生命周期，而不是偶然重写固定件架构。
- 仅用于异步初始化，并与构造函数结合使用同步部分
- 使用 `[TestCleanup]` 进行必须在失败时运行的清理
- 仅在 MSTest 3.6+ 上通过构造函数注入 `TestContext`；否则使用实例属性。

```csharp
[TestClass]
public sealed class RepositoryTests
{
    private readonly TestContext _testContext;
    private readonly FakeDatabase _db;  // readonly -- 由构造函数保证

    public RepositoryTests(TestContext testContext)
    {
        _testContext = testContext;
        _db = new FakeDatabase();  // 构造函数中的同步初始化
    }

    [TestInitialize]
    public async Task InitAsync()
    {
        // 仅用于异步设置，使用 TestInitialize
        await _db.SeedAsync();
    }

    [TestCleanup]
    public void Cleanup() => _db.Reset();
}
```

#### 执行顺序

1. `[AssemblyInitialize]` -- 每个程序集一次
2. `[ClassInitialize]` -- 每个类一次
3. 每个测试：
   - 使用 `TestContext` 属性注入：构造函数 -> 设置 `TestContext` 属性 -> `[TestInitialize]`
   - 使用构造函数注入 `TestContext`：构造函数（接收 `TestContext`）-> `[TestInitialize]`
4. 测试方法
5. `[TestCleanup]` -> `DisposeAsync` -> `Dispose` -- 每个测试
6. `[ClassCleanup]` -- 每个类一次
7. `[AssemblyCleanup]` -- 每个程序集一次

### 第 6 步：应用取消和超时模式

当安装的 MSTest 版本直接暴露令牌时（3.11+），使用 `TestContext.CancellationToken` 与 `[Timeout(milliseconds, CooperativeCancellation = true)]` 结合使用。在 MSTest 3.6.4-3.10 上，使用 `TestContext.CancellationTokenSource.Token` 与协作取消结合使用。普通的 `[Timeout]` 并不建立框架令牌将停止正在进行的工作的前提。在较旧版本中，使用测试拥有的 `CancellationTokenSource`，其中取消本身是测试的一部分。

```csharp
// MSTest 3.11+
[TestMethod]
[Timeout(5000, CooperativeCancellation = true)]
public async Task FetchData_ReturnsWithinTimeout()
{
    var result = await _client.GetDataAsync(_testContext.CancellationToken);
    Assert.IsNotNull(result);
}
```

### 第 7 步：在适当的地方使用高级功能

#### 重试不可靠的测试（MSTest 3.8+）

仅用于真正不可靠的外部依赖项（网络、文件系统），而不是用来掩盖竞态条件或共享状态问题。
对于外部服务，使用有界的尝试加上非零延迟/退避，以便重试策略不会立即猛烈冲击相同依赖项：

```csharp
[TestMethod]
[Retry(
    3,
    MillisecondsDelayBetweenRetries = 1_000,
    BackoffType = DelayBackoffType.Exponential)]
public async Task ExternalService_EventuallyResponds()
{
    var response = await WeatherClient.GetAsync();
    Assert.IsNotNull(response);
}
```

#### 条件执行

`OSCondition` 需要 MSTest 3.8+；`CICondition` 需要 MSTest 3.10+。

```csharp
[TestMethod]
[OSCondition(OperatingSystems.Windows)]
public void WindowsRegistry_ReadsValue() { }

[TestMethod]
[CICondition(ConditionMode.Exclude)]
public void LocalOnly_InteractiveTest() { }
```

属性替换测试体内的环境分支；它们不会替换正在测试的操作。在纠正提供的代码时，保留真实的注册/GPU/服务操作和具体的资源清理，而不是返回空方法或仅注释的占位符。
显示清理状态安全初始化和对称释放（包括当设置可能失败时使用 null 守卫）。一个仅包含策略的草图，省略了操作、断言或清理体，是不完整的。

#### 并行化

```csharp
[assembly: Parallelize(Workers = 4, Scope = ExecutionScope.MethodLevel)]

[TestClass]
[DoNotParallelize]  // 具体类排除
public sealed class DatabaseIntegrationTests { }
```

### 第 8 步：修复 MSTest 分析器诊断（MSTESTxxxx）

`MSTest.Analyzers` 包在构建期间和 IDE 中报告 `MSTESTxxxx` 诊断。分析器会自动随现代 `MSTest` 通用包和 `MSTest.Sdk`（`MSTest.TestFramework` 3.7+ 也捆绑了它们）；对于其他设置，仅在用户要求采用分析器时显式引用 `MSTest.Analyzers`。大多数规则在 Visual Studio 中都有自动代码修复（灯泡）。手动修复一个时，应用下面 idiomatic、与版本兼容的更改，而不是抑制规则。

当被要求“修复 MSTESTxxxx”时，在下面的常见诊断表中查找它，应用修复，并重新构建以确认诊断已消失。该表并不详尽——对于任何未列出的规则，请参考完整参考并应用记录的指导：<https://learn.microsoft.com/dotnet/core/testing/mstest-analyzers/overview>

#### 常见诊断及其修复

| 规则 | 问题 | 修复 |
|---|---|---|
| MSTEST0006 | 使用 `[ExpectedException]` | 在 3.8+ 上，用 `Assert.Throws<T>` / `Assert.ThrowsExactly<T>` 替换；否则使用 `Assert.ThrowsException<T>` |
| MSTEST0017 | `Assert.AreEqual` 参数顺序交换 | 将 `expected` 放在前面，`actual` 放在后面 |
| MSTEST0023 | 否定的布尔断言 (`Assert.IsTrue(!x)`) | 使用 `Assert.IsFalse(x)` |
| MSTEST0025 | 始终为假的断言 | 使用 `Assert.Fail("reason")` |
| MSTEST0032 | 始终为真的断言条件 | 移除或纠正断言 |
| MSTEST0037 | 亚优化的断言 (`IsTrue(x == null)`) | 使用具体的断言 (`Assert.IsNull`, `HasCount`, 等）（第 3 步） |
| MSTEST0038 | 在值类型上使用 `Assert.AreSame` | 使用 `Assert.AreEqual`（值类型装箱到不同的引用） |
| MSTEST0039 | 遗留的 `Assert.ThrowsException` | 在 3.8+ 上，使用 `Assert.Throws` / `Assert.ThrowsExactly` (+ `Async` 变体） |
| MSTEST0044 | 使用 `[DataTestMethod]` | 仅在版本支持数据行时用 `[TestMethod]` 替换 |
| MSTEST0046 | 使用 `StringAssert` | 在 3.10+ 上，使用等效的 `Assert` 方法 (`Assert.Contains`, `StartsWith`, ...) |
| MSTEST0052 | 显式的 `DynamicDataSourceType` | 删除它——源类型是推断的 |
| MSTEST0042 / MSTEST0060 | 重复的 `[DataRow]` / `[TestMethod]` | 删除重复的属性 |
| MSTEST0024 | 静态 `TestContext` 字段 | 使其实例成员（第 5 步） |
| MSTEST0045 / MSTEST0049 / MSTEST0054 | 超时/令牌不是协作的 | 将 `TestContext.CancellationToken` 流入预期的调用（第 6 步） |
| MSTEST0036 | 成员遮蔽了基类测试成员 | 重命名或使用 `override` 而不是 `new` |
| MSTEST0061 | 测试内部的运行时 OS 检查 | 使用 `[OSCondition(...)]`（第 7 步） |
| MSTEST0002 / MSTEST0003 / MSTEST0005 / MSTEST0007–0014 | 无效的测试类/方法/固定件/`TestContext`/数据源布局 | 修复规则命名的签名（例如，使其为公共的，修复返回类型和参数，在需要时添加 `static`） |

#### 调整哪些规则被强制执行

使用 `MSTestAnalysisMode` MSBuild 属性（MSTest 3.8+）来控制全局规则集：

```xml
<PropertyGroup>
  <!-- None | Default | Recommended | All -->
  <MSTestAnalysisMode>Recommended</MSTestAnalysisMode>
</PropertyGroup>
```

- `Recommended` 将信息级规则提升为警告，并且大多数项目应采用此模式。
- 一小部分规则是完全可选的（例如 MSTEST0015、MSTEST0019–0022）；当您希望强制执行约定时，可以通过 `.editorconfig` 按项目启用它们。
- 优先修复底层代码而不是抑制诊断。仅在记录的合理理由下抑制。

### 第 9 步：验证基于文件的修复

当用户请求仓库编辑且未禁止执行时，编辑后运行影响范围最窄的 `dotnet test` 命令。一个成功的进程且没有发现测试计数不是验证。要求预期的测试用例被发现并通过。

如果编译暴露了直接耦合的源问题，阻止了修复的现有套件运行（例如，在提供的生产文件中缺少命名空间导入），则仅进行最小修复并重新运行。不要升级包或扩大现代化范围。报告实际的测试计数和所做的修复；永远不要将未运行或无输出的测试作为通过呈现。
在最终交接时，将每个请求的现代化映射到确切的修复结构，并引用通过测试命令。不要依赖一个通用的“现代化”摘要，当预期/实际顺序、确切的类型检查、数据发现或类形状是明确要求时。
