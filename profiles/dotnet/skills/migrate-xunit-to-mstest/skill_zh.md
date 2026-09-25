# xUnit -> MSTest 迁移

将 xUnit.net v2 或 v3 测试转换为 MSTest v4，而不更改目标框架或测试平台。成功的迁移可以构建、发现相同的测试，并保留通过/失败结果和执行语义。

## 范围

仅在项目包含 xUnit 包或源代码，并且用户希望使用 MSTest 时使用此技能。如果项目已经使用 MSTest 且不包含 xUnit 测试，则报告不需要框架迁移，并且不进行任何更改。

不要将此框架转换与目标框架升级或 VSTest/MTP 迁移结合使用。完成并验证一个迁移后再开始另一个。

## 工作区契约

- 激活技能后继续。在当前工作目录中搜索已标记的项目和源；永远不会在此技能的基目录下搜索用户文件。
- 打开 glob 搜索返回的原始路径。如果某个读取器或修补工具拒绝刚刚找到的路径，则使用另一个可用的工具重试。在当前工作区发现耗尽之前，不要向用户请求路径。
- 根据请求的可交付成果进行分类："转换此项目"意味着编辑、构建和测试；"给我一个计划"或"我会如何转换它？"意味着回答。当文件存在时，不要用"请提供文件"替换执行。
- 最终响应必须声明源 xUnit 版本、保留的运行器、更改的文件、每个应用的高风险语义映射，以及实际测试计数。关于 fixture 生命周期、Owner 映射、取消或并行化的断言必须在结果源代码中可见，而不仅仅是文字。

## 响应模式

- **完整的迁移请求**：检查项目、进行编辑、构建并运行测试。在给出计划后不要停止。
- **聚焦编译错误或 API 问题**：检查相关代码并仅应用该映射。不要叙述整个工作流程。
- **不支持的目標框架**：在更改包之前停止。MSTest v4 需要 .NET 8+ 或 .NET Framework 4.6.2+ 用于测试应用程序；提供单独批准的 TFM 升级或 MSTest v3 作为中间目标。

## 更改结果的决策

在机械映射之前应用这些：

| 检测到的状态 | 需要的操作 |
|---|---|
| 没有剩余的 xUnit 包、命名空间、属性或 fixture | 停止。不进行文件更改，报告迁移不必要，并运行现有的 `dotnet test` 命令一次以证明已经-MSTest 项目是健康的。 |
| 源代码使用 VSTest | 保留现有的 VSTest 属性/配置。优先保留和更新源项目的显式 `Microsoft.NET.Test.Sdk` 锁定；故意依赖 MSTest 元包的传递依赖项的存储库可能会保留该约定。不要引入 MTP 属性。 |
| 源代码使用 MTP | 用 MSTest MTP 配置替换 xUnit 特定的 MTP 选择。优先使用 `MSTest.Sdk`；使用元包，设置 `EnableMSTestRunner=true` 和 `OutputType=Exe`。保留原生与桥接命令集成，不要添加 `<UseVSTest>true</UseVSTest>` 或其他 VSTest 特有的配置。 |
| 源代码依赖 xUnit 的默认并行化 | 当当前项目至少有两个独立可运行的测试类时，在编译的 `.cs` 文件中添加 `[assembly: Parallelize(Workers = 0, Scope = ExecutionScope.ClassLevel)]`。在一个没有显式并行设置的类项目中，由于类级并发不可观察，因此省略它。无论当前类计数如何，都要翻译显式的 `CollectionBehavior` 或 `xunit.runner.json` 设置。在报告完成之前，读取更改的文件并将其命名为结果中的名称。 |

有关详细映射和示例，搜索 [`references/mapping-cheatsheet.md`](references/mapping-cheatsheet.md) 以查找项目中实际存在的结构，并仅阅读匹配的章节。不要加载或重现整个参考。

## 快速路径

对于常规的项目迁移，在四个阶段中收敛：一次批量的发现读取/搜索、一次编辑传递、一次 `dotnet test` 和一次简洁的结果。不要：

- 列出目录，然后通过另一个工具重新读取相同的文件
- 将项目文件复制到加载的技能或其 `references/` 目录中；这些文件是只读的指导，不是编辑工作区
- 除非已知还原是当前的，否则尝试 `dotnet test --no-restore`
- 当 `dotnet test` 足够时，运行单独的还原、构建和测试命令
- 重新运行通过测试命令或检查未更改的文件以确认

使用现有的 CI/测试结果作为基准线，当可用时。当计数不可用时且迁移包含数据驱动测试、fixtures、跳过、自定义扩展、共享状态或其他无法从源代码中建立的行為时，运行新的预编辑基准线。

## 工作流程

### 1. 建立基线

1. 在一次发现传递中，批量读取测试项目、`Directory.Build.props`、`Directory.Packages.props`、`global.json` 和运行器配置，并在源代码中搜索以下高风险结构。
2. 声明检测到的源版本：
   - `xunit` 2.x 和相关包 -> xUnit v2
   - `xunit.v3` 或 `xunit.v3.*` -> xUnit v3
3. 从项目和存储库配置中识别 VSTest 或 MTP。仅在平台不明确时使用 `platform-detection`，并保留检测到的平台。
4. 记录目标框架，如果 MSTest v4 不支持它们则停止。
5. 如果快速路径需要新的基线，运行现有的测试命令一次并记录发现的、通过的、失败的和跳过的计数。
6. 在编辑之前，列出高风险结构：
   - `IClassFixture`、`ICollectionFixture`、`CollectionDefinition`、自定义 `FactAttribute`/`TheoryAttribute`/`DataAttribute`
   - `Assert.Throws`、`ThrowsAny`、`IsType`、`Record.Exception`、事件断言
   - `ITestOutputHelper`、`TestContext.Current`、`IAsyncLifetime`
   - `CollectionBehavior`、`xunit.runner.json`、共享静态或外部状态

### 2. 不切换运行器的情况下替换包

从项目文件和中央包文件中删除 xUnit 包。这包括 `xunit*`、`xunit.v3.*`、`xunit.runner.visualstudio`、`YTest.MTP.XUnit2` 和正在替换的 xUnit 特定的附属包。

默认使用 MSTest v4 元包进行增量转换：

```xml
<!-- 示例锁定：用从配置的包源解析的确切稳定 v4 版本替换。 -->
<PackageReference Include="MSTest" Version="4.1.0" />
```

元包包括 `Microsoft.NET.Test.Sdk`、`MSTest.TestAdapter`、`MSTest.TestFramework` 和 `MSTest.Analyzers`。当保留 VSTest 时，优先保留源项目的显式 `Microsoft.NET.Test.Sdk` 锁定，并将其更新为与所选 MSTest 版本兼容的版本；这保留了运行器/版本兼容性审查。故意依赖元包的传递依赖项的存储库可能会保留该约定。对于上面的示例锁定，MSTest 4.1.0 需要 Microsoft.NET.Test.Sdk 18.0.1+；不兼容的旧锁定可能导致 `NU1605`。

当保留 MTP 时，不要将 xUnit 的 `UseMicrosoftTestingPlatformRunner` 属性带入 MSTest 项目。优先使用 `MSTest.Sdk` 在解析的版本。如果存储库约定要求使用元包路线，则设置 `<EnableMSTestRunner>true</EnableMSTestRunner>` 和 `<OutputType>Exe</OutputType>`。仅当存储库继续通过 VSTest 命令模式调用 MTP 应用程序时，保留 `TestingPlatformDotnetTestSupport=true`；原生 .NET 10+ MTP 模式不需要它。当保留 VSTest 与 `MSTest.Sdk` 时，设置 `<UseVSTest>true</UseVSTest>`。

不要更改 `TargetFramework`。仅在移植其相关设置后删除 `xunit.runner.json`。

### 3. 执行机械转换

首先应用常见的重写：

| xUnit | MSTest |
|---|---|
| 没有类属性 | `[TestClass]` |
| `[Fact]` | `[TestMethod]` |
| `[Theory]` + `[InlineData]` | `[TestMethod]` + `[DataRow]` |
| `[MemberData]` | `[DynamicData]` |
| `[Fact(Skip = "...")]` | `[TestMethod]` + `[Ignore("...")]` |
| `[Trait("Category", value)]` | `[TestCategory(value)]` |
| `[Trait("Owner", value)]` | `[Owner(value)]` |
| 其他 `[Trait(key, value)]` | `[TestProperty(key, value)]` |
| `Assert.Equal` / `NotEqual` | `Assert.AreEqual` / `AreNotEqual` |
| `Assert.True` / `False` | `Assert.IsTrue` / `IsFalse` |
| `Assert.Null` / `NotNull` | `Assert.IsNull` / `IsNotNull` |

删除 `using Xunit;` 和 `using Xunit.Abstractions;`。对于元包选项，添加 `using Microsoft.VisualStudio.TestTools.UnitTesting;`；`MSTest.Sdk` 作为隐式全局 using 提供它。

保留现有的类继承。不要机械地密封类。

### 4. 解决语义映射

加载映射小册子以检查步骤 1 中发现的所有高风险结构。这些规则是强制性的：

- xUnit `Assert.Throws<T>` 是精确类型，映射到 MSTest `Assert.ThrowsExactly<T>`。
- xUnit `Assert.ThrowsAny<T>` 允许派生类型，映射到 MSTest `Assert.Throws<T>`。
- xUnit `Assert.IsType<T>` 是精确类型，映射到泛型 `Assert.IsExactInstanceOfType<T>`；`Assert.IsAssignableFrom<T>` 映射到泛型 `Assert.IsInstanceOfType<T>`。当 xUnit 断言的 typed 返回值是可分配的时，保留该分配并使用泛型 MSTest 重载，而不是非泛型 `Type` 重载。
- xUnit `Assert.Equal` 在序列上比较元素。在 MSTest 4.3+ 上使用 `Assert.AreSequenceEqual`，或在早期 v4 上使用 `CollectionAssert.AreEqual` 与材料化的列表；永远不要用基于引用的 `Assert.AreEqual` 替换序列相等。
- `[Ignore]` 和 `[Timeout]` 是修饰符；保留 `[TestMethod]` 以便测试被发现。
- `[DataRow]` 值必须与参数类型完全匹配。
- `TestContext.Current.CancellationToken` 映射到注入的 MSTest `TestContext.CancellationToken`；永远不要用 `CancellationToken.None` 或新的 `CancellationTokenSource` 替换它。
- `Owner` 是 VSTest 的保留属性。将 `[Trait("Owner", value)]` 映射到 `[Owner(value)]`，而不是 `[TestProperty("Owner", value)]`。
- 没有MSTest等效项的断言（`Assert.Collection`、`Assert.All`、`Assert.Equivalent`、`Record.Exception`、事件断言）需要显式手动重写。永远不要删除断言而不替换其验证。

在库存使所需的映射清晰时，在一次编辑传递中应用机械和语义重写。默认情况下不要运行中间构建；使用最终验证的编译器错误来驱动未解决的转换。

### 5. 保留生命周期、fixture 范围和并行化

- 保留有效的构造函数设置和 `IDisposable`/`IAsyncDisposable`。将 `IAsyncLifetime` 映射到 `[TestInitialize]`/`[TestCleanup]`。
- `IClassFixture<T>` 意味着每个测试类一个 fixture 实例，由该类中的所有方法共享。将其映射到由接受 `TestContext` 的静态 `[ClassInitialize]` 方法创建的静态 `T` 字段，并从静态 `[ClassCleanup]` 中一次释放它。永远不要使用 `[TestInitialize]`/`[TestCleanup]` 进行此映射，因为这将创建每个测试方法的 fixture。
- 对于 `ICollectionFixture<T>`，保留共享和序列化。优先使用由每个成员类使用的静态 `Lazy<T>` 辅助程序；仅在源集合禁用并行化时才添加 `[DoNotParallelize]`。仅在 fixture 真正为整个程序集范围时才使用程序集初始化。
- 用构造器注入或基于属性的 MSTest `TestContext` 替换 `ITestOutputHelper`，并将每个 `_output.WriteLine(...)` 调用替换为相应的 `TestContext.WriteLine(...)`。在最终结果中，明确命名 `TestContext` 注入/属性和 `WriteLine` 映射；"迁移输出"不足以证明一致性。

xUnit 默认并行运行类；MSTest 串行运行它们。当当前项目有两个或多个独立可运行的测试类时，使用以下代码保留有效行为：

```csharp
[assembly: Parallelize(Workers = 0, Scope = ExecutionScope.ClassLevel)]
```

对于一个没有显式 xUnit 并行设置的类项目，不要添加一个程序集策略：没有类级并发要保留。始终翻译显式的 `CollectionBehavior` 或 `xunit.runner.json` 设置。永远不要使用 `ExecutionScope.MethodLevel` 来模拟 xUnit。在应用 fixture 范围或并行化决策之前，声明源共享或序列化以及目标如何保留它。

### 6. 验证一致性

1. 使用与基线相同的平台、过滤器和配置运行测试一次。`dotnet test` 默认构建；仅在需要隔离编译失败时运行单独的构建。
2. 比较发现的、通过的、失败的和跳过的计数。
3. 在声明完成之前调查每个差异：
   - 缺失的情况 -> 发现属性、`DynamicData` 或 `DataRow` 字面类型
   - 更改的异常行为 -> 精确类型与派生类型断言映射
   - 共享状态失败或大持续时间变化 -> fixture 范围和并行化
   - 静默跳过的测试 -> 缺少 `[TestMethod]` 或不正确的运行时跳过转换
4. 确认除非明确记录为手动后续处理，否则不保留 xUnit 包、命名空间、属性、运行器配置或 fixture 接口。
5. 在最终通过测试后，读取实现高风险映射的每个更改文件，以及任何运行器或并行化配置。在结果中，命名文件和实现其生命周期、数据、跳过、输出、断言、fixture 范围或并行化行为的精确目标 API。保留类型参数和成员名称，例如 `[ClassInitialize]`、`TestContext.WriteLine` 和 `Assert.IsExactInstanceOfType<T>`；"转换属性"或"迁移输出"等泛型声明不是一致性的证据。

保持最终响应简洁并关注结果：

- **更改**：命名文件和应用的精确高风险映射。
- **验证**：给出最终测试命令和发现的/通过的/失败的/跳过的计数。
- **保留**：声明未更改的目标框架和测试平台，以及任何 fixture 或并行化范围决策。
- **剩余**：确定手动后续处理，或说没有。

## 完成标准

- 确定了当前 xUnit 版本和测试平台
- xUnit 包和源代码结构已转换
- 目标框架和测试平台保持不变
- fixture 范围和有效并行化决策是明确的，包括并发不可观察时的合理省略
- 构建成功
- 测试发现和结果计数与基线匹配
- 任何不支持的定制扩展点都明确指出，而不是近似

## 后续处理

如果用户也希望使用 MTP，请单独运行 `migrate-vstest-to-mtp`。仅在一致性建立后使用 `writing-mstest-tests` 来完善转换的 MSTest 代码。
