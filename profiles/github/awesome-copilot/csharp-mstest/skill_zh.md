# MSTest 最佳实践 (MSTest 3.x/4.x)

你的目标是帮助我使用现代 MSTest 编写有效的单元测试，使用当前的 API 和最佳实践。

## 项目设置

- 使用单独的测试项目，命名约定为 `[ProjectName].Tests`
- 引用 MSTest 3.x+ NuGet 包（包含分析器）
- 考虑使用 MSTest.Sdk 进行简化的项目设置
- 使用 `dotnet test` 运行测试

## 测试类结构

- 使用 `[TestClass]` 属性为测试类
- 默认情况下**密封测试类**以优化性能和设计清晰度
- 使用 `[TestMethod]` 为测试方法（优先于 `[DataTestMethod]`）
- 遵循 Arrange-Act-Assert (AAA) 模式
- 使用模式 `MethodName_Scenario_ExpectedBehavior` 命名测试

```csharp
[TestClass]
public sealed class CalculatorTests
{
    [TestMethod]
    public void Add_TwoPositiveNumbers_ReturnsSum()
    {
        // Arrange
        var calculator = new Calculator();

        // Act
        var result = calculator.Add(2, 3);

        // Assert
        Assert.AreEqual(5, result);
    }
}
```

## 测试生命周期

- **优先使用构造函数而不是 `[TestInitialize]`** - 支持只读字段并遵循标准 C# 模式
- 使用 `[TestCleanup]` 为即使测试失败也必须执行的清理操作
- 当需要异步设置时，将构造函数与异步 `[TestInitialize]` 结合使用

```csharp
[TestClass]
public sealed class ServiceTests
{
    private readonly MyService _service;  // 构造函数启用只读字段

    public ServiceTests()
    {
        _service = new MyService();
    }

    [TestInitialize]
    public async Task InitAsync()
    {
        // 仅用于异步初始化
        await _service.WarmupAsync();
    }

    [TestCleanup]
    public void Cleanup() => _service.Reset();
}
```

### 执行顺序

1. **程序集初始化** - `[AssemblyInitialize]`（每个测试程序集一次）
2. **类初始化** - `[ClassInitialize]`（每个测试类一次）
3. **测试初始化**（每个测试方法）:
   1. 构造函数
   2. 设置 `TestContext` 属性
   3. `[TestInitialize]`
4. **测试执行** - 运行测试方法
5. **测试清理**（每个测试方法）:
   1. `[TestCleanup]`
   2. `DisposeAsync`（如果实现）
   3. `Dispose`（如果实现）
6. **类清理** - `[ClassCleanup]`（每个测试类一次）
7. **程序集清理** - `[AssemblyCleanup]`（每个测试程序集一次）

## 现代断言 API

MSTest 提供三个断言类：`Assert`、`StringAssert` 和 `CollectionAssert`。

### Assert 类 - 核心断言

```csharp
// 等价性
Assert.AreEqual(expected, actual);
Assert.AreNotEqual(notExpected, actual);
Assert.AreSame(expectedObject, actualObject);      // 引用等价
Assert.AreNotSame(notExpectedObject, actualObject);

// 空值检查
Assert.IsNull(value);
Assert.IsNotNull(value);

// 布尔值
Assert.IsTrue(condition);
Assert.IsFalse(condition);

// 失败/不完整
Assert.Fail("Test failed due to...");
Assert.Inconclusive("Test cannot be completed because...");
```

### 异常测试（优先于 `[ExpectedException]`）

```csharp
// Assert.Throws - 匹配 TException 或派生类型
var ex = Assert.Throws<ArgumentException>(() => Method(null));
Assert.AreEqual("Value cannot be null.", ex.Message);

// Assert.ThrowsExactly - 仅匹配确切类型
var ex = Assert.ThrowsExactly<InvalidOperationException>(() => Method());

// 异步版本
var ex = await Assert.ThrowsAsync<HttpRequestException>(async () => await client.GetAsync(url));
var ex = await Assert.ThrowsExactlyAsync<InvalidOperationException>(async () => await Method());
```

### 集合断言（Assert 类）

```csharp
Assert.Contains(expectedItem, collection);
Assert.DoesNotContain(unexpectedItem, collection);
Assert.ContainsSingle(collection);  // 恰好一个元素
Assert.HasCount(5, collection);
Assert.IsEmpty(collection);
Assert.IsNotEmpty(collection);
```

### 字符串断言（Assert 类）

```csharp
Assert.Contains("expected", actualString);
Assert.StartsWith("prefix", actualString);
Assert.EndsWith("suffix", actualString);
Assert.DoesNotStartWith("prefix", actualString);
Assert.DoesNotEndWith("suffix", actualString);
Assert.MatchesRegex(@"\d{3}-\d{4}", phoneNumber);
Assert.DoesNotMatchRegex(@"\d+", textOnly);
```

### 比较断言

```csharp
Assert.IsGreaterThan(lowerBound, actual);
Assert.IsGreaterThanOrEqualTo(lowerBound, actual);
Assert.IsLessThan(upperBound, actual);
Assert.IsLessThanOrEqualTo(upperBound, actual);
Assert.IsInRange(actual, low, high);
Assert.IsPositive(number);
Assert.IsNegative(number);
```

### 类型断言

```csharp
// MSTest 3.x - 使用 out 参数
Assert.IsInstanceOfType<MyClass>(obj, out var typed);
typed.DoSomething();

// MSTest 4.x - 直接返回类型化结果
var typed = Assert.IsInstanceOfType<MyClass>(obj);
typed.DoSomething();

Assert.IsNotInstanceOfType<WrongType>(obj);
```

### Assert.That (MSTest 4.0+)

```csharp
Assert.That(result.Count > 0);  // 自动捕获表达式在失败消息中
```

### StringAssert 类

> **注意：** 当可用时，优先使用 `Assert` 类的等效方法（例如，`Assert.Contains("expected", actual)` 而不是 `StringAssert.Contains(actual, "expected")`）。

```csharp
StringAssert.Contains(actualString, "expected");
StringAssert.StartsWith(actualString, "prefix");
StringAssert.EndsWith(actualString, "suffix");
StringAssert.Matches(actualString, new Regex(@"\d{3}-\d{4}"));
StringAssert.DoesNotMatch(actualString, new Regex(@"\d+"));
```

### CollectionAssert 类

> **注意：** 当可用时，优先使用 `Assert` 类的等效方法（例如，`Assert.Contains`）。

```csharp
// 包含
CollectionAssert.Contains(collection, expectedItem);
CollectionAssert.DoesNotContain(collection, unexpectedItem);

// 等价（相同元素，相同顺序）
CollectionAssert.AreEqual(expectedCollection, actualCollection);
CollectionAssert.AreNotEqual(unexpectedCollection, actualCollection);

// 等效（相同元素，任意顺序）
CollectionAssert.AreEquivalent(expectedCollection, actualCollection);
CollectionAssert.AreNotEquivalent(unexpectedCollection, actualCollection);

// 子集检查
CollectionAssert.IsSubsetOf(subset, superset);
CollectionAssert.IsNotSubsetOf(notSubset, collection);

// 元素验证
CollectionAssert.AllItemsAreInstancesOfType(collection, typeof(MyClass));
CollectionAssert.AllItemsAreNotNull(collection);
CollectionAssert.AllItemsAreUnique(collection);
```

## 数据驱动测试

### DataRow

```csharp
[TestMethod]
[DataRow(1, 2, 3)]
[DataRow(0, 0, 0, DisplayName = "Zeros")]
[DataRow(-1, 1, 0, IgnoreMessage = "Known issue #123")]  // MSTest 3.8+
public void Add_ReturnsSum(int a, int b, int expected)
{
    Assert.AreEqual(expected, Calculator.Add(a, b));
}
```

### DynamicData

数据源可以返回以下类型之一：

- `IEnumerable<(T1, T2, ...)>`（ValueTuple）- **优先**，提供类型安全（MSTest 3.7+）
- `IEnumerable<Tuple<T1, T2, ...>>` - 提供类型安全
- `IEnumerable<TestDataRow>` - 提供类型安全并支持测试元数据控制（显示名称、类别）
- `IEnumerable<object[]>` - **最不优先**，无类型安全

> **注意：** 创建新的测试数据方法时，优先使用 `ValueTuple` 或 `TestDataRow` 而不是 `IEnumerable<object[]>`。`object[]` 方法不提供编译时类型检查，可能导致运行时类型不匹配错误。

```csharp
[TestMethod]
[DynamicData(nameof(TestData))]
public void DynamicTest(int a, int b, int expected)
{
    Assert.AreEqual(expected, Calculator.Add(a, b));
}

// ValueTuple - 优先（MSTest 3.7+）
public static IEnumerable<(int a, int b, int expected)> TestData =>
[
    (1, 2, 3),
    (0, 0, 0),
];

// TestDataRow - 当需要自定义显示名称或元数据时
public static IEnumerable<TestDataRow<(int a, int b, int expected)>> TestDataWithMetadata =>
[
    new((1, 2, 3)) { DisplayName = "Positive numbers" },
    new((0, 0, 0)) { DisplayName = "Zeros" },
    new((-1, 1, 0)) { DisplayName = "Mixed signs", IgnoreMessage = "Known issue #123" },
];

// IEnumerable<object[]> - 新代码避免使用（无类型安全）
public static IEnumerable<object[]> LegacyTestData =>
[
    [1, 2, 3],
    [0, 0, 0],
];
```

## TestContext

`TestContext` 类提供测试运行信息、取消支持以及输出方法。
参考 [TestContext 文档](https://learn.microsoft.com/dotnet/core/testing/unit-testing-mstest-writing-tests-testcontext) 获取完整参考。

### 访问 TestContext

```csharp
// 属性（MSTest 抑制 CS8618 - 不要使用可空或 = null！）
public TestContext TestContext { get; set; }

// 构造函数注入（MSTest 3.6+）- 优先用于不可变性
[TestClass]
public sealed class MyTests
{
    private readonly TestContext _testContext;

    public MyTests(TestContext testContext)
    {
        _testContext = testContext;
    }
}

// 静态方法接收它作为参数
[ClassInitialize]
public static void ClassInit(TestContext context) { }

// 清理方法可选（MSTest 3.6+）
[ClassCleanup]
public static void ClassCleanup(TestContext context) { }

[AssemblyCleanup]
public static void AssemblyCleanup(TestContext context) { }
```

### 取消令牌

始终使用 `TestContext.CancellationToken` 与 `[Timeout]` 协作取消：

```csharp
[TestMethod]
[Timeout(5000)]
public async Task LongRunningTest()
{
    await _httpClient.GetAsync(url, TestContext.CancellationToken);
}
```

### 测试运行属性

```csharp
TestContext.TestName              // 当前测试方法名称
TestContext.TestDisplayName       // 显示名称（3.7+）
TestContext.CurrentTestOutcome    // 通过/失败/进行中
TestContext.TestData              // 参数化测试数据（3.7+, 在 TestInitialize/Cleanup 中）
TestContext.TestException         // 测试失败时异常（3.7+, 在 TestCleanup 中）
TestContext.DeploymentDirectory   // 部署项目录
```

### 输出和结果文件

```csharp
// 写入测试输出（用于调试）
TestContext.WriteLine("Processing item {0}", itemId);

// 附加文件到测试结果（日志、截图）
TestContext.AddResultFile(screenshotPath);

// 跨测试方法存储/检索数据
TestContext.Properties["SharedKey"] = computedValue;
```

## 高级功能

### 对于不稳定测试的重试（MSTest 3.9+）

```csharp
[TestMethod]
[Retry(3)]
public void FlakyTest() { }
```

### 条件执行（MSTest 3.10+）

根据操作系统或 CI 环境跳过或运行测试：

```csharp
// 操作系统特定测试
[TestMethod]
[OSCondition(OperatingSystems.Windows)]
public void WindowsOnlyTest() { }

[TestMethod]
[OSCondition(OperatingSystems.Linux | OperatingSystems.MacOS)]
public void UnixOnlyTest() { }

[TestMethod]
[OSCondition(ConditionMode.Exclude, OperatingSystems.Windows)]
public void SkipOnWindowsTest() { }

// CI 环境测试
[TestMethod]
[CICondition]  // 仅在 CI 中运行（默认：ConditionMode.Include）
public void CIOnlyTest() { }

[TestMethod]
[CICondition(ConditionMode.Exclude)]  // CI 中跳过，本地运行
public void LocalOnlyTest() { }
```

### 并行化

```csharp
// 程序集级别
[assembly: Parallelize(Workers = 4, Scope = ExecutionScope.MethodLevel)]

// 为特定类禁用
[TestClass]
[DoNotParallelize]
public sealed class SequentialTests { }
```

### 工作项可追溯性（MSTest 3.8+）

在测试报告中将测试链接到工作项以实现可追溯性：

```csharp
// Azure DevOps 工作项
[TestMethod]
[WorkItem(12345)]  // 链接到工作项 #12345
public void Feature_Scenario_ExpectedBehavior() { }

// 多个工作项
[TestMethod]
[WorkItem(12345)]
[WorkItem(67890)]
public void Feature_CoversMultipleRequirements() { }

// GitHub 问题（MSTest 3.8+）
[TestMethod]
[GitHubWorkItem("https://github.com/owner/repo/issues/42")]
public void BugFix_Issue42_IsResolved() { }
```

工作项关联出现在测试结果中，可用于：

- 追踪测试覆盖率到需求
- 将修复与回归测试链接
- 在 CI/CD 管道中生成可追溯性报告

## 常见错误避免

```csharp
// ❌ 错误的参数顺序
Assert.AreEqual(actual, expected);
// ✅ 正确
Assert.AreEqual(expected, actual);

// ❌ 使用 ExpectedException（已过时）
[ExpectedException(typeof(ArgumentException))]
// ✅ 使用 Assert.Throws
Assert.Throws<ArgumentException>(() => Method());

// ❌ 使用 LINQ Single() - 不明确的异常
var item = items.Single();
// ✅ 使用 ContainsSingle - 更好的失败消息
var item = Assert.ContainsSingle(items);

// ❌ 硬转换 - 不明确的异常
var handler = (MyHandler)result;
// ✅ 使用类型断言 - 失败时显示实际类型
var handler = Assert.IsInstanceOfType<MyHandler>(result);

// ❌ 忽略取消令牌
await client.GetAsync(url, CancellationToken.None);
// ✅ 流测试取消
await client.GetAsync(url, TestContext.CancellationToken);

// ❌ 使 TestContext 可空 - 导致不必要的空值检查
public TestContext? TestContext { get; set; }
// ❌ 使用 null! - MSTest 已抑制 CS8618
public TestContext TestContext { get; set; } = null!;
// ✅ 声明而不带可空或初始化器 - MSTest 处理警告
public TestContext TestContext { get; set; }
```

## 测试组织

- 按功能或组件分组测试
- 使用 `[TestCategory("Category")]` 进行过滤
- 使用 `[TestProperty("Name", "Value")]` 为自定义元数据（例如，`[TestProperty("Bug", "12345")]`）
- 使用 `[Priority(1)]` 为关键测试
- 启用相关的 MSTest 分析器（MSTEST0020 用于构造函数优先）

## Mocking 和隔离

- 使用 Moq 或 NSubstitute 进行模拟依赖项
- 使用接口以促进模拟
- 模拟依赖项以隔离测试单元
