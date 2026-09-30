---
name: migrate-mstest-v3-to-v4
description: 在使用此技能回答、规划或编辑任何 MSTest 3.x 到 4.x 升级或升级后故障之前，请使用该技能。触发条件包括“MSTest v4 的破坏性变更”；CS0507/CS0103/CS1061/CS1615；ExecuteAsync、CallerInfo、DisplayName 或自定义TestMethodAttribute；ClassCleanupBehavior；ContainsKey；ThrowsExactly 或 ExpectedException；IsInstanceOfType 输出参数；TestTimeout.Infinite；ManagedType；net6/net7 兼容性；TestCase.Id 历史；ClassInitialize 中的 TestName；TreatDiscoveryWarningsAsErrors；干净构建后的发现错误；以及 MSTest.Sdk/MTP 或 vstest.console 发现更改。不适用于 v1/v2 到 v3 的遗留问题、框架转换、仅运行器迁移或一般的 .NET 升级。
---

# MSTest v3 向 v4 迁移

将测试项目从 MSTest v3 迁移到 MSTest v4。结果是使用 MSTest v4 的项目，可以正常构建、通过测试，并涵盖所有源不兼容和行为变化。MSTest v4 与 MSTest v3 **不是二进制兼容**的——任何针对 v3 编译的库都必须针对 v4 重新编译。

## 首要操作

在搜索网络或凭记忆回答之前，检查提供的项目和源代码。将请求分类为专注的源修复、运行时行为变化、CI 发现问题、兼容性问题或完整迁移，然后按照下表匹配的行进行操作。干净的编译并不排除这项技能：发现失败、`TestContext` 生命周期异常和测试历史变化是运行时迁移失败。

## 何时使用

- 升级 `MSTest.TestFramework`、`MSTest.TestAdapter` 或 `MSTest` 元包从 3.x 到 4.x
- 升级 `MSTest.Sdk` 从 3.x 到 4.x
- 更新到 MSTest v4 包后修复构建错误
- 升级到 MSTest v4 后解决测试执行中的行为变化
- 更新用于 v4 的自定义 `TestMethodAttribute` 或 `ConditionBaseAttribute` 实现

## 何时不用

- 项目已经使用 MSTest v4 且构建正常——迁移已完成
- 从 MSTest v1 或 v2 升级——首先使用 `migrate-mstest-v1v2-to-v3`，然后返回这里
- 项目不使用 MSTest
- 在测试框架之间迁移（例如，MSTest 到 xUnit 或 NUnit）

## 输入

| 输入 | 是否必需 | 描述 |
|-------|----------|-------------|
| 项目或解决方案路径 | 否 | 包含 MSTest 测试项目的 `.csproj`、`.sln` 或 `.slnx` 入口点。**自行发现**通过通配符搜索工作目录；仅在未找到或选择确实模糊时才询问 |
| 构建命令 | 否 | 如何构建（例如，`dotnet build`，一个仓库构建脚本）。如果未提供，则自动检测 |
| 测试命令 | 否 | 如何运行测试（例如，`dotnet test`）。如果未提供，则自动检测 |

## 可能改变结果的决定

| 检测到的请求或状态 | 必需操作 |
|---|---|
| 当前工作区中提供了文件 | 在那里搜索并打开返回的原始路径。技能目录不是项目目录。如果一个工具拒绝一个有效路径，请尝试使用另一个可用的读取器/编辑器；不要向用户询问您可以发现的路径。 |
| 用户要求对提供的文件应用更改：“修复我的项目/文件”、“请更新此源代码”、“进行更改”或“然后构建和运行” | 编辑每个受影响的实例。针对实际包版本运行最窄的有意义的构建/测试命令；技能激活不是停止建议的理由。 |
| 用户询问“我应该期待什么？”、“我该如何修复这些更改？”、兼容性建议或计划 | 直接从实际项目状态回答，即使源代码可见。保持单症状回答集中；仅包含改变决策的相邻风险。 |
| 完整迁移中的不支持的 TFM | 首先更新 TFM，然后更新 MSTest 包，然后修复源代码中断。不要在发布说明清单中将此顺序隐藏。 |
| 自定义 `TestMethodAttribute` 子类 | 将 `ExecuteAsync`、CallerInfo 传播、显示名称处理和子类的重试/结果语义视为一个耦合迁移。修复实际类，而不是占位符示例。 |
| `MSTest.Sdk` v4 源/API 错误 (`ManagedType`、`TestTimeout`、`Contains`) | 提供确切的源替换，然后添加相邻的运行器警告：MTP 模式不再提供 `Microsoft.NET.Test.Sdk`；仅在 VSTest 发现仍然需要时才添加它。 |
| `MSTest.Sdk` v4 加 `vstest.console` | 这是 v4 的变化：MTP 模式不再包含 `Microsoft.NET.Test.Sdk`。保留 MTP 并添加该包以进行过渡的 VSTest 发现，选择 `UseVSTest`，或将 CI 切换到 `dotnet test`；说明该选择保留的运行器。 |

## 响应指南

- **始终首先识别当前版本**：在推荐任何迁移步骤之前，明确声明项目中检测到的 MSTest 版本（例如，“您的项目使用 MSTest v3 (3.8.0)）。这确认您已读取项目文件，并使迁移建议有依据。
- **解决目标版本，不要假设**：当用户询问“最新”时，查询项目的配置包源并选择执行时可用的最新稳定 MSTest v4 版本。永远不要在不检查的情况下将此技能的示例版本复制到结果中。保持所有 MSTest 包在同一解析版本上。
- **专注修复请求**（用户在升级后具有特定编译错误）：仅解决来自步骤 3 的相关破坏性更改。仅在请求交付是源更改时才进行编辑；“我该如何修复这些？”仍然是一个回答请求。**始终提供具体的修复代码**，使用用户的实际类型和方法名称。如果固定装置仍然引用 v3，请不要声称绿色的 v3 构建验证了 v4 兼容性；请求时更新包或声明验证边界。对于自定义 `TestMethodAttribute` 子类，显示完整的修复类，包括 CallerInfo 传播到基构造函数。提及任何可以在此之前捕获此问题的相关分析器（例如，MSTEST0006）。当项目使用 `MSTest.Sdk` 时，还说明 v4 MTP 模式不再提供 `Microsoft.NET.Test.Sdk`，以及这是否影响可见的运行器。不要逐步通过整个迁移工作流。
- **“应该期待什么？”问题**（用户在升级前询问）：呈现来自步骤 3 快速查找表的**所有**主要破坏性更改——不仅仅是当前代码中可见的更改。对于每个更改，提供一个单行修复摘要。还提及来自步骤 4 的关键行为变化（尤其是 TestCase.Id 历史影响和 TreatDiscoveryWarningsAsErrors 默认值）。如果项目代码可用，突出显示哪些更改直接适用。
- **完整迁移请求**（用户希望完整迁移）：遵循下面的完整工作流。
- **行为/运行时症状报告**（用户描述了测试执行差异而没有构建错误）：将描述的症状与步骤 4 中的行为变化表匹配。提供有针对性的、症状特定的建议。提及用户应关注的其他行为变化。除非用户也有构建错误，否则不要逐步通过源破坏性更改。
- **CI/测试发现问题**（测试未发现、`vstest.console` 停止工作、升级后 CI 管道失败）：专注于 4.5（MSTest.Sdk v4 不再在其默认 MTP 模式下包含 `Microsoft.NET.Test.Sdk`——它仍然需要用于 `vstest.console`）和 4.4（TreatDiscoveryWarningsAsErrors）。清楚地解释根本原因并给出所有三个路径：添加 `Microsoft.NET.Test.Sdk` 同时保留 MTP、将 `UseVSTest` 设置为切换项目运行器，或将 CI 切换到 MTP 本地 `dotnet test`。不要逐步通过完整迁移工作流。
- **解释性问题**（用户询问“这是一个已知更改吗？”、“我还应该注意什么？”）：解释相关更改并提供建议。提及用户可能接下来遇到的更改。不要规定完整的迁移程序。
- **结果证明**：在实施工作结束时，提供检测到的 v3 版本、解析的 v4 版本、运行器选择、更改的文件和实际的构建/测试计数。永远不要报告从推断得出的构建、VSTest 兼容性、发现或通过测试。

## 工作流

> **提交策略**：除非用户要求，否则不要创建提交。在 diff 中将包、源和行为变化逻辑分离，但完成并验证请求的迁移。

### 步骤 1：评估项目

1. 通过检查 `.csproj`、`Directory.Build.props` 或 `Directory.Packages.props` 中的 `MSTest`、`MSTest.TestFramework`、`MSTest.TestAdapter` 或 `MSTest.Sdk` 的包引用来识别当前的 MSTest 版本。
2. 确认项目位于 MSTest v3 (3.x)。如果位于 v1 或 v2，请首先使用 `migrate-mstest-v1v2-to-v3`。
3. 检查目标框架——MSTest v4 停止支持 .NET Core 3.1 到 .NET 7。支持的目标框架是：**net8.0**、**net9.0**、**net462**（.NET Framework 4.6.2+）、**uap10.0.16299**（UWP）、**net9.0-windows10.0.17763.0**（现代 UWP）和**net8.0-windows10.0.18362.0**（WinUI）。
4. 检查自定义 `TestMethodAttribute` 子类——这些需要在 v4 中进行更改。
5. 检查 `ExpectedExceptionAttribute` 的使用——v4 中已移除（自 v3 起已弃用，分析器 MSTEST0006）。
6. 检查 `Assert.ThrowsException` 的使用（已弃用）——v4 中已移除。
7. 运行一个干净的构建，以建立现有错误/警告的基线。

### 步骤 2：将包更新到 MSTest v4

首先从配置的包源解析最新稳定的 v4 版本。在元包、单个包、`MSTest.Sdk` 和中央包管理中始终固定该确切版本。

- 对于 `MSTest` 元包，更新其 `PackageReference` 到解析的确切版本。
- 对于单个包，将 `MSTest.TestFramework` 和 `MSTest.TestAdapter` 更新为同一版本。
- 对于 `MSTest.Sdk`，更新项目或 `global.json` 中的 SDK 版本到同一版本。

运行 `dotnet restore`，然后 `dotnet build`。收集所有错误以供步骤 3 处理。

### 步骤 3：解决源破坏性更改

系统地处理编译错误。使用此快速查找表识别所有适用的更改，然后应用每个修复：

| 错误 / 代码中的模式 | 破坏性更改 | 修复 |
|---|---|---|
| 自定义 `TestMethodAttribute` 重写 `Execute` | `Execute` 已移除 | 更改为 `ExecuteAsync` 返回 `Task<TestResult[]>`（3.1） |
| `[TestMethod("name")]` 或自定义属性构造函数 | 添加了 CallerInfo 参数 | 使用 `DisplayName = "name"` 命名参数；在子类中传播 CallerInfo（3.2） |
| `ClassCleanupBehavior.EndOfClass` | 枚举已移除 | 移除参数：只需 `[ClassCleanup]`（3.3） |
| `TestContext.Properties.Contains("key")` | `Properties` 是 `IDictionary<string, object>` | 更改为 `ContainsKey("key")`（3.4） |
| `[Timeout(TestTimeout.Infinite)]` | `TestTimeout` 枚举已移除 | 替换为 `[Timeout(int.MaxValue)]`（3.5） |
| `TestContext.ManagedType` | 属性已移除 | 使用 `FullyQualifiedTestClassName`（3.6） |
| `Assert.AreEqual(a, b, "msg {0}", arg)` | 消息+参数重载已移除 | 使用字符串插值：`$"msg {arg}"`（3.7） |
| `Assert.ThrowsException<T>(...)` | 已重命名 | 替换为 `Assert.ThrowsExactly<T>(...)` 或 `Assert.Throws<T>(...)`（3.7） |
| `Assert.IsInstanceOfType<T>(obj, out var t)` | 输出参数已移除 | 使用 `var t = Assert.IsInstanceOfType<T>(obj)`（3.7） |
| `[ExpectedException(typeof(T))]` | 属性已移除 | 将断言移入测试主体：`Assert.ThrowsExactly<T>(() => ...)`（3.8） |
| 项目目标为 net5.0、net6.0 或 net7.0 | TFM 已移除 | 更改为 net8.0 或 net9.0（3.9） |

> **重要**：在开始修复之前，扫描整个项目以查找上述所有模式。多个破坏性更改通常在同一项目中共存。

#### 3.1 TestMethodAttribute.Execute -> ExecuteAsync

如果您有自定义 `TestMethodAttribute` 子类重写 `Execute`，则更改为 `ExecuteAsync`。此更改的原因是 v3 同步的 `Execute` API 在测试代码使用 `async`/`await` 内部时会导致死锁——同步包装会阻塞线程，而异步操作需要该线程来完成。

```csharp
// v3（之前）
public sealed class MyTestMethodAttribute : TestMethodAttribute
{
    public override TestResult[] Execute(ITestMethod testMethod)
    {
        // 自定义逻辑
        return result;
    }
}

// v4（之后）——选项 A：用 Task.FromResult 包装同步逻辑
public sealed class MyTestMethodAttribute : TestMethodAttribute
{
    public override Task<TestResult[]> ExecuteAsync(ITestMethod testMethod)
    {
        // 同步自定义逻辑
        return Task.FromResult(result);
    }
}

// v4（之后）——选项 B：使其正确地异步
public sealed class MyTestMethodAttribute : TestMethodAttribute
{
    public override async Task<TestResult[]> ExecuteAsync(ITestMethod testMethod)
    {
        // 自定义异步逻辑
        return await base.ExecuteAsync(testMethod);
    }
}
```

当您的重写逻辑是纯同步时，使用 `Task.FromResult`。当您调用 `base.ExecuteAsync` 或其他异步方法时，使用 `async`/`await`。

#### 3.2 TestMethodAttribute CallerInfo 构造函数

`TestMethodAttribute` 现在使用 `[CallerFilePath]` 和 `[CallerLineNumber]` 参数在其构造函数中。

**如果您继承自 TestMethodAttribute**，请将调用者信息传播到基类：

```csharp
public class MyTestMethodAttribute : TestMethodAttribute
{
    public MyTestMethodAttribute(
        [CallerFilePath] string callerFilePath = "",
        [CallerLineNumber] int callerLineNumber = -1)
        : base(callerFilePath, callerLineNumber)
    {
    }
}
```

如果子类具有自己的显示名称构造函数，请不要将那个字符串传递给 v4 的基构造函数。仅传播调用者信息，并分配 `DisplayName` 属性：

```csharp
public sealed class NamedTestMethodAttribute : TestMethodAttribute
{
    public NamedTestMethodAttribute(
        string displayName,
        [CallerFilePath] string callerFilePath = "",
        [CallerLineNumber] int callerLineNumber = -1)
        : base(callerFilePath, callerLineNumber)
    {
        DisplayName = displayName;
    }
}
```

**如果您使用 `[TestMethodAttribute("Custom display name")]`**，切换到命名参数语法：

```csharp
// v3（之前）
[TestMethodAttribute("Custom display name")]

// v4（之后）
[TestMethodAttribute(DisplayName = "Custom display name")]
```

#### 3.3 ClassCleanupBehavior 枚举已移除

`ClassCleanupBehavior` 枚举已移除。在 v3 中，此枚举控制类清理是在类末尾运行 (`EndOfClass`) 还是在程序集末尾运行 (`EndOfAssembly`)。在 v4 中，类清理始终在类末尾运行。移除枚举参数：

```csharp
// v3（之前）
[ClassCleanup(ClassCleanupBehavior.EndOfClass)]
public static void ClassCleanup(TestContext testContext) { }

// v4（之后）
[ClassCleanup]
public static void ClassCleanup(TestContext testContext) { }
```

如果您之前使用 `ClassCleanupBehavior.EndOfAssembly`，请将清理逻辑移到 `[AssemblyCleanup]` 方法中。

#### 3.4 TestContext.Properties 类型更改

`TestContext.Properties` 已从 `IDictionary` 更改为 `IDictionary<string, object>`。更新任何 `Contains` 调用为 `ContainsKey`：

```csharp
// v3（之前）
testContext.Properties.Contains("key");

// v4（之后）
testContext.Properties.ContainsKey("key");
```

#### 3.5 TestTimeout 枚举已移除

`TestTimeout` 枚举（仅包含 `TestTimeout.Infinite`）已移除。替换为 `int.MaxValue`：

```csharp
// v3（之前）
[Timeout(TestTimeout.Infinite)]

// v4（之后）
[Timeout(int.MaxValue)]
```

#### 3.6 TestContext.ManagedType 已移除

`TestContext.ManagedType` 属性已移除。使用 `TestContext.FullyQualifiedTestClassName` 替代。

#### 3.7 Assert API 签名更改

- **消息+参数已移除**：接受 `message` 和 `object[]` 参数的 Assert 方法现在仅接受 `message`。使用字符串插值而不是格式字符串：

```csharp
// v3（之前）
Assert.AreEqual(expected, actual, "Expected {0} but got {1}", expected, actual);

// v4（之后）
Assert.AreEqual(expected, actual, $"Expected {expected} but got {actual}");
```

- **Assert.ThrowsException 重命名**：`Assert.ThrowsException` API 已重命名。使用 `Assert.ThrowsExactly`（严格类型匹配）或 `Assert.Throws`（接受派生异常类型）：

```csharp
// 之前 (v3)
Assert.ThrowsException<InvalidOperationException>(() => DoSomething());

// 之后 (v4) -- 精确类型匹配（与旧版 ThrowsException 行为相同）
Assert.ThrowsExactly<InvalidOperationException>(() => DoSomething());

// 之后 (v4) -- 也捕获派生异常类型
Assert.Throws<InvalidOperationException>(() => DoSomething());
```

- **Assert.IsInstanceOfType out 参数已更改**：`Assert.IsInstanceOfType<T>(x, out var t)` 更改为 `var t = Assert.IsInstanceOfType<T>(x)`：

```csharp
// 之前 (v3)
Assert.IsInstanceOfType<MyType>(obj, out var typed);

// 之后 (v4)
var typed = Assert.IsInstanceOfType<MyType>(obj);
```

将此赋值重写应用于每个出现的位置，保留具体的断言类型和后续对 typed 变量的所有使用。当源代码可用时，显示或编辑实际方法，而不是替换通用的 `MyType` 示例，然后验证项目是否可以编译。

- **Assert.AreEqual for IEquatable\<T\> 已移除**：如果您遇到泛型类型推断错误，请显式指定类型参数为 `object`。

#### 3.8 ExpectedExceptionAttribute 已移除

在 v4 中，`[ExpectedException]` 属性已移除。在 MSTest 3.2 中，引入了 `MSTEST0006` 分析器以标记 `[ExpectedException]` 的使用并建议在 v3 上迁移到 `Assert.ThrowsExactly`（这是一个非破坏性更改）。在 v4 中，该属性已完全移除。迁移到 `Assert.ThrowsExactly`：

```csharp
// 之前 (v3)
[ExpectedException(typeof(InvalidOperationException))]
[TestMethod]
public void TestMethod()
{
    MyCall();
}

// 之后 (v4)
[TestMethod]
public void TestMethod()
{
    Assert.ThrowsExactly<InvalidOperationException>(() => MyCall());
}
```

**当测试在抛出调用之前有设置代码时**，仅将抛出调用包装在 lambda 中——保持 Arrange/Act 分离清晰：

```csharp
// 之前 (v3)
[ExpectedException(typeof(ArgumentNullException))]
[TestMethod]
public void Validate_NullInput_Throws()
{
    var service = new ValidationService();
    service.Validate(null);  // 抛出在这里
}

// 之后 (v4)
[TestMethod]
public void Validate_NullInput_Throws()
{
    var service = new ValidationService();
    Assert.ThrowsExactly<ArgumentNullException>(() => service.Validate(null));
}
```

**对于异步测试方法**，使用 `Assert.ThrowsExactlyAsync`：

```csharp
// 之前 (v3)
[ExpectedException(typeof(HttpRequestException))]
[TestMethod]
public async Task FetchData_BadUrl_Throws()
{
    await client.GetAsync("https://localhost:0");
}

// 之后 (v4)
[TestMethod]
public async Task FetchData_BadUrl_Throws()
{
    await Assert.ThrowsExactlyAsync<HttpRequestException>(
        () => client.GetAsync("https://localhost:0"));
}
```

**如果 `[ExpectedException]` 使用了 `AllowDerivedTypes` 属性**，请使用 `Assert.ThrowsAsync<T>`（基类型匹配）而不是 `Assert.ThrowsExactlyAsync<T>`（精确类型匹配）。

对于专注迁移，将提供的源中的每个带属性的方法转换为，仅将预期抛出的语句包装，保留 lambda 外部的 arrange/setup 语句，并运行受影响的测试。当存在可编辑的项目文件时，纯文本 API 替换是不完整的。

#### 3.9 已移除目标框架

MSTest v4 支持 **.NET 8 及更高版本**和**.NET Framework 4.6.2 及更高版本**。平台特定的支持目标还包括**uap10.0.16299**（UWP），现代 UWP 和 WinUI 使用其对应的 Windows 特定 .NET TFMs。.NET Core 3.1 到 .NET 7 已被移除。

如果测试项目针对不受支持的框架，请更新 `TargetFramework`：

```xml
<!-- 之前 -->
<TargetFramework>net6.0</TargetFramework>

<!-- 之后 -->
<TargetFramework>net8.0</TargetFramework>
```

#### 3.10 Unfolding strategy 移动到 TestMethodAttribute

`UnfoldingStrategy` 属性（在 MSTest 3.7 中引入）已从单个数据源属性（`DataRowAttribute`、`DynamicDataAttribute`）移动到 `TestMethodAttribute`。

#### 3.11 ConditionBaseAttribute.ShouldRun 重命名

`ConditionBaseAttribute.ShouldRun` 属性重命名为 `IsConditionMet`。

#### 3.12 内部/已移除类型

某些以前公开的类型现在是内部的或已移除：

- `MSTestDiscoverer`、`MSTestExecutor`、`AssemblyResolver`、`LogMessageListener`
- `TestExecutionManager`、`TestMethodInfo`、`TestResultExtensions`
- `UnitTestOutcomeExtensions`、`GenericParameterHelper`
- `PlatformServices` 组合中的 `ITestMethod`（TestFramework 中的那个未更改）

如果您的代码引用了这些类型，请寻找替代方法或删除依赖项。

### 第 4 步：解决行为变化

这些更改不会导致构建错误，但可能会影响测试运行时行为。

| 症状 | 原因 | 解决方法 |
|---|---|---|
| 测试显示为新的 / 测试历史记录丢失 | `TestCase.Id` 生成方式已更改 (4.3) | 无代码修复；历史记录将重新基线 |
| `TestContext.TestName` 在 `[ClassInitialize]` 中抛出 | v4 强制生命周期范围 (4.2) | 将访问移动到 `[TestInitialize]` 或测试方法 |
| 测试未发现 / 发现失败 | `TreatDiscoveryWarningsAsErrors` 现在为 true (4.4) | 修复警告，或在 .runsettings 中设置为 false |
| 测试挂起而之前未挂起 | AppDomain 默认禁用 (4.1) | 在 .runsettings `RunConfiguration` 中将 `DisableAppDomain` 设置为 false |
| 升级到 v4 后 `vstest.console` 无法找到 MSTest.Sdk 测试 | MSTest.Sdk 默认为 MTP；v4 停止在 MTP 模式下添加 `Microsoft.NET.Test.Sdk` (4.5) | 显式添加兼容的 `Microsoft.NET.Test.Sdk` 包，同时保留 MTP，设置 `UseVSTest`，或切换 CI 到 `dotnet test` |
| 分析器发出新警告 | 分析器严重性升级 (4.6) | 修复警告或在 .editorconfig 中抑制 |

#### 4.1 DisableAppDomain 默认为 true

AppDomains 默认禁用。在 .NET Framework 中，在测试主机（`dotnet test` 和 VS 的默认设置）中，MSTest 自动重新启用 AppDomains。如果您需要显式控制 AppDomain 封装，请通过 `.runsettings` 设置它：

```xml
<RunSettings>
  <RunConfiguration>
    <DisableAppDomain>false</DisableAppDomain>
  </RunConfiguration>
</RunSettings>
```

#### 4.2 TestContext 在使用不当时报错

MSTest v4 现在会在错误的生命周期阶段访问测试特定属性时抛出：

- `TestContext.FullyQualifiedTestClassName` -- 不能在 `[AssemblyInitialize]` 中访问
- `TestContext.TestName` -- 不能在 `[AssemblyInitialize]` 或 `[ClassInitialize]` 中访问

**修复**：将任何访问 `TestContext.TestName` 的代码从 `[ClassInitialize]` 移动到 `[TestInitialize]` 或单独的测试方法，在这些地方可以访问每个测试的上下文。不要用 `FullyQualifiedTestClassName` 作为替代方案——它们具有不同的语义。

#### 4.3 TestCase.Id 生成方式已更改

`TestCase.Id` 的生成算法已更改以修复长期存在的错误。这可能影响 Azure DevOps 测试结果跟踪（例如，长时间内的测试失败跟踪）。无需代码修复，但要注意测试结果历史的连续性中断。

#### 4.4 TreatDiscoveryWarningsAsErrors 默认为 true

v4 使用更严格的默认值。发现警告现在被视为错误，这意味着之前尽管存在发现问题但仍运行的测试现在可能会完全失败。如果您在升级后看到意外的测试失败（不是构建错误，而是测试未被发现），请检查发现警告。为了在调查期间恢复 v3 行为：

```xml
<RunSettings>
  <MSTest>
    <TreatDiscoveryWarningsAsErrors>false</TreatDiscoveryWarningsAsErrors>
  </MSTest>
</RunSettings>
```

> **建议**：修复底层的发现警告，而不是抑制此设置。

#### 4.5 MSTest.Sdk 和 vstest.console 兼容性

MSTest.Sdk 默认为 Microsoft.Testing.Platform (MTP) 模式。MSTest.Sdk v3 仍在该模式下添加了 `Microsoft.NET.Test.Sdk`；v4 移除了不必要的引用。因此，在 v4 升级后立即调用 `vstest.console` 的 CI 管道可能会立即丢失所有发现的测试。

**选项 A -- 保留 MTP 和过渡性 VSTest 发现**：显式添加兼容的 `Microsoft.NET.Test.Sdk` 包。当 MTP 仍然是主要运行器，但还不能删除现有的 `vstest.console` 工作时，这是最不具破坏性的修复：

使用直接 `PackageReference` 并从配置的源中解析确切的兼容版本。在中央包管理中，在 `Directory.Packages.props` 中添加或更新 `Microsoft.NET.Test.Sdk` `PackageVersion`，并保持项目引用无版本。不要复制固定的示例版本。

使用实际的 `vstest.console` 命令进行验证；通过 `dotnet test` MTP 运行通过并不能证明 VSTest 发现。

**选项 B -- 将项目切换到 VSTest 模式**：设置 `UseVSTest`。MSTest.Sdk 然后添加 `Microsoft.NET.Test.Sdk`：

```xml
<PropertyGroup>
  <UseVSTest>true</UseVSTest>
</PropertyGroup>
```

保留从步骤 2 中解析的确切 `MSTest.Sdk` v4 插桩；此选项更改的是运行器，而不是选择的 MSTest 版本或目标框架。

**选项 C -- 将 CI 切换到 `dotnet test`**：将 CI 管道中的 `vstest.console` 调用替换为 `dotnet test`。这原生支持 MTP，并且是 MSTest.Sdk 项目的推荐长期方法。

不要说此行为早于 v4：在 MTP 模式中移除传递的 `Microsoft.NET.Test.Sdk` 引用是 v4 行为破坏性更改之一。

#### 4.6 分析器严重性更改

多个分析器已从 Info 升级到 Warning：

- MSTEST0001、MSTEST0007、MSTEST0017、MSTEST0023、MSTEST0024、MSTEST0025
- MSTEST0030、MSTEST0031、MSTEST0032、MSTEST0035、MSTEST0037、MSTEST0045

检查并修复任何新警告，或在 `.editorconfig` 中抑制它们（如果故意）。

### 第 5 步：验证

1. 运行 `dotnet build` -- 确认零错误并检查任何新警告
2. 运行 `dotnet test` -- 确认所有测试通过
3. 比较测试结果（通过/失败计数）与迁移前的基线
4. 如果使用 Azure DevOps 测试跟踪，请注意 `TestCase.Id` 变化可能会影响历史连续性
5. 确认没有由于更严格的发现而静默丢失的测试

## 验证

- [ ] 所有 MSTest 包更新到 4.x
- [ ] 项目构建零错误
- [ ] 所有测试通过 `dotnet test`
- [ ] 自定义 `TestMethodAttribute` 子类更新以支持 `ExecuteAsync` 和 CallerInfo
- [ ] `ExpectedExceptionAttribute` 替换为 `Assert.ThrowsExactly`
- [ ] `Assert.ThrowsException` 替换为 `Assert.ThrowsExactly`（或 `Assert.Throws`）
- [ ] `ClassCleanupBehavior` 枚举用法已移除
- [ ] `TestContext.Properties.Contains` 更新为 `ContainsKey`
- [ ] 所有目标框架为 net8.0+、net9.0、net462+、uap10.0.16299 或 WinUI
- [ ] 行为变化已审查并解决
- [ ] 迁移期间没有丢失测试（比较测试计数）

## 相关技能

- `writing-mstest-tests` -- 用于现代 MSTest v4 断言 API 和测试编写最佳实践
- `run-tests` -- 用于迁移后运行测试

## 常见陷阱

| 陷阱 | 解决方法 |
|---|---|
| 自定义 `TestMethodAttribute` 仍然覆盖 `Execute` | 更改为 `ExecuteAsync` 返回 `Task<TestResult[]>` |
| `TestMethodAttribute("display name")` 无法编译 | 使用 `TestMethodAttribute(DisplayName = "display name")` |
| `ClassCleanupBehavior` 枚举未找到 | 移除枚举参数；`[ClassCleanup]` 现在始终在类结束时运行。对于程序集级清理，使用 `[AssemblyCleanup]` |
| `TestContext.Properties.Contains` 缺失 | 使用 `ContainsKey` -- `Properties` 现在是 `IDictionary<string, object>` |
| `ExpectedException` 属性未找到 | 在测试体中替换为 `Assert.ThrowsExactly<T>(() => ...)` |
| `Assert.ThrowsException` 未找到 | 替换为 `Assert.ThrowsExactly`（或 `Assert.Throws` 用于派生类型） |
| `Assert.AreEqual` 使用格式字符串参数失败 | 使用字符串插值：`$"message {value}"` |
| 测试挂起而之前未挂起 | AppDomain 默认禁用；在 .NET Fx 的测试主机中它自动重新启用 |
| Azure DevOps 测试历史记录中断 | 预期——`TestCase.Id` 生成方式已更改；无需代码修复，结果将重新基线 |
| 发现警告现在导致运行失败 | `TreatDiscoveryWarningsAsErrors` 默认为 true；修复发现警告 |
| net6.0/net7.0 目标无法编译 | 更新到 net8.0 -- MSTest v4 支持 net8.0、net9.0、net462、uap10.0.16299、现代 UWP 和 WinUI |
