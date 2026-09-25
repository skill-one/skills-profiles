# xunit.v3 迁移

将 .NET 测试项目从 xUnit.net v2 迁移到 xUnit.net v3。结果是一个解决方案，其中所有测试项目都引用 `xunit.v3.*` 包，可以正常编译，并且所有测试在迁移后都能以与迁移前相同的结果通过。

## 何时使用

- 将 `xunit`（v2）包升级到 `xunit.v3`
- 更新 xunit 包引用到 v3 后解决编译错误

## 何时不用

- 在测试框架之间迁移（例如，从 MSTest 或 NUnit 迁移到 xUnit.net）—— 完全是不同的工作量
- 从 VSTest 迁移到 Microsoft.Testing.Platform —— 使用 `migrate-vstest-to-mtp`
- 项目已经引用了 `xunit.v3` —— 迁移已完成

## 输入

| 输入 | 是否必需 | 描述 |
|-------|----------|-------------|
| 测试项目或解决方案 | 否 | 在当前工作目录中发现 `.csproj`、`.sln`、`.slnx`、中心属性和源代码；如果没有找到或目标不明确，则询问 |

## 工作区和完成契约

- 技能激活不是完成。对于迁移/修复/更新请求，检查暂存文件，编辑它们，并在同一任务中运行测试。
- 技能基本目录只包含指导。搜索当前工作目录并按返回的路径精确打开。如果工具拒绝刚刚搜索到的路径，请尝试使用另一个可用的读取器/编辑器，而不是得出文件缺失的结论。
- 当工作区发现可以找到路径时，不要要求用户提供路径。
- 一次遍历库存项目/中心包文件和所有受影响的源。当 v2 仅 API 保持存在时，包仅迁移是不完整的。
- 以检测到的源版本和运行器结束，精确设置包兼容性，更改的文件，发现的/通过的/失败的/跳过的计数，以及任何平台特定结果。没有测试发现的构建不是成功。
- 包的有效性是经验性的：记录配置的源查询或解析的包图，以及成功的还原。在最终结果中，说明如何证明所选的精确版本是可用的；不要仅仅命名一个版本，并让判断者或用户推断它是否存在。

## 工作流程

> **提交策略**：除非用户要求，否则不要创建提交。在差异中保持项目配置和源编辑逻辑上分离，但完成并验证整个请求的迁移。

> **优先级**：步骤 1-5 是每个迁移都必需的。步骤 6-12 是有条件的——仅应用与项目代码模式相关的步骤。跳过不相关的步骤。

### 改变结果的决策

在编辑之前运行此预检：

| 检测到的状态 | 必需的操作 |
|---|---|
| 项目引用 `xunit.v3`，具有必需的可执行程序/运行器配置，不包含任何剩余的 v2 包或 v2 仅 API 模式，并且现有的测试命令通过 | 停止：迁移已经完成。不要更新版本，创建 props 文件，或修改源。报告经过验证的无操作结果。如果任何必需的 v3 适配仍然存在，请仅进行该修复，而不是将包引用单独视为完成。 |
| xUnit v2 使用 `YTest.MTP.XUnit2` | 保留 MTP：删除该 shim，设置 `UseMicrosoftTestingPlatformRunner=true`，并且不要添加 `xunit.runner.visualstudio` 或 `IsTestingPlatformApplication=false`。 |
| xUnit v2 不使用 MTP shim | 保留 VSTest：保留/更新 `xunit.runner.visualstudio` 并设置 `IsTestingPlatformApplication=false`。 |
| 自定义类型派生自 `BeforeAfterTestAttribute` | 保留该继承及其行为。将 `IXunitTest` 参数添加到两个重写中，并将其传递给 `base.Before`/`base.After`；不要用直接接口实现替换子类。 |
| 基于类型的集合/排序器属性指向自定义类型 | 迁移属性语法和引用类型的 v3 合约。对于集合工厂，实现所需的 xUnit v3 `IXunitTestCollectionFactory` 行为；在保留空的工厂的同时编译属性不是完整的迁移。 |
| 伴生包存在 | 从配置的源中解析 `xunit.v3`、Xunit.Combinatorial 和 Xunit.StaFact 作为一套兼容的包。如果最新 xunit.v3 主要版本在这些源上没有兼容的稳定伴生包，请选择最新的兼容 xunit.v3 主要版本并解释固定。验证发现，而不仅仅是编译。 |
| `OutputType=Exe` 使 `net*-windows` 项目在非 Windows 主机上失败 | 当打算进行跨平台构建时，添加 `EnableWindowsTargeting=true`，然后重新运行。不要将此迁移引起的失败视为预存在的。 |

从配置的包源解析包版本。不要从产品的“v3”名称猜测版本或更新无关的包。仅更改包含适用规则所需的包、属性或源结构的文件。

编辑中心包管理项目后，读取回 `Directory.Packages.props` 和项目文件。确认 `PackageVersion` 拥有版本，重命名的 `PackageReference` 是无版本的，并且 `OutputType=Exe` 有效。

### 步骤 1：识别 xUnit.net 项目并验证兼容性

搜索引用 xUnit.net v2 包的测试项目：

- `xunit`
- `xunit.abstractions`
- `xunit.assert`
- `xunit.core`
- `xunit.extensibility.core`
- `xunit.extensibility.execution`
- `xunit.runner.visualstudio`

确保检查项目文件、MSBuild props 和目标文件中的包引用，例如 `Directory.Build.props`、`Directory.Build.targets` 和 `Directory.Packages.props`。

验证目标框架兼容性：xUnit.net v3 需要 **.NET 8+** 或 **.NET Framework 4.7.2+**。对于测试库项目，.NET Standard 2.0 也受支持。如果任何测试项目具有不兼容的目标框架，请在此停止——告诉用户先升级目标框架。还要验证项目使用 SDK 格式。

### 步骤 2：更新包引用

1. 根据以下映射更新任何 `PackageReference` 或 `PackageVersion` 项目，使用新的包名称：

    - `xunit` → `xunit.v3`
    - `xunit.abstractions` → 完全删除
    - `xunit.assert` → `xunit.v3.assert`
    - `xunit.core` → `xunit.v3.core`
    - `xunit.extensibility.core` 和 `xunit.extensibility.execution` → `xunit.v3.extensibility.core`（如果项目中有两个包引用，则合并为一个条目，因为这两个包已合并）

2. 查询配置的包源并固定实际存在的最新稳定版本。仅对 VSTest 项目更新 `xunit.runner.visualstudio`；不要将其添加到 MTP 项目。

### 步骤 3：将 `OutputType` 设置为 `Exe`

在每个测试项目（不包括测试库项目）中，在项目文件中将 `OutputType` 设置为 `Exe`：

```xml
<PropertyGroup>
  <OutputType>Exe</OutputType>
</PropertyGroup>
```

根据您手中的解决方案，可能有一个集中位置可以添加此设置。例如：

- 如果所有测试项目共享（或可以共享）一个共同的 `Directory.Build.props`，则在那里添加 `<OutputType>Exe</OutputType>` 属性。注意 OutputType 不应添加到 `Directory.Build.targets`。
- 如果所有测试项目共享名称模式（例如，`*.Tests.csproj`），则在 `Directory.Build.props` 中添加一个仅适用于这些项目的条件属性组，例如 `<OutputType Condition="$(MSBuildProjectName.EndsWith('.Tests'))">Exe</OutputType>`。根据需要调整条件以仅针对测试项目。
- 否则，将 `<OutputType>Exe</OutputType>` 属性添加到每个测试项目文件中。

### 步骤 4：配置测试平台

保留与 xUnit.net v2 使用的相同测试平台。xUnit.net v2 总是使用 VSTest，除非项目使用 `YTest.MTP.XUnit2`。

- 如果项目引用了 `YTest.MTP.XUnit2`：
  - 完全删除对 `YTest.MTP.XUnit2` 的引用。
  - 在现有的共享 `Directory.Build.props` 中设置 `<UseMicrosoftTestingPlatformRunner>true</UseMicrosoftTestingPlatformRunner>`，或者在没有共享 props 文件的情况下在测试项目中设置。
  - 不要添加 `xunit.runner.visualstudio`；它是 VSTest 运行器，并削弱平台保留。
- 如果项目没有引用 `YTest.MTP.XUnit2`（常见情况）：
  - 在现有的共享 `Directory.Build.props` 中设置 `<IsTestingPlatformApplication>false</IsTestingPlatformApplication>`，或者在不存在共享 props 文件的情况下直接在测试项目中设置。不要仅为单个项目创建一个仓库范围的 props 文件。这使项目保留在 VSTest 上。

### 步骤 5：删除 `Xunit.Abstractions` using

在 C# 文件中查找任何 `using Xunit.ITestOutputHelper;` 指令并完全删除它们。

### 步骤 6：处理 `async void` 的破坏性变更（如果适用）

在 xUnit.net v3 中，`async void` 测试方法不再受支持，并且将无法编译。搜索任何使用 `async void` 声明的测试方法，并将它们更改为 `async Task`。可以通过 `[Fact]` 或 `[Theory]` 属性或其他测试属性识别测试方法。

在最终结果中，说明为什么源已更改：xUnit.net v3 拒绝 `async void` 测试，因此每个受影响的方法现在返回 `Task`。不要仅报告机械替换。还要说明如何从配置的源解析精确的包版本。

### 步骤 7：处理属性破坏性变更（如果适用）

在 xUnit.net v3 中，某些属性已更新，以便它们接受 `System.Type` 而不是两个字符串（完全限定类型名和程序集名）。这些属性是：

- `CollectionBehaviorAttribute`
- `TestCaseOrdererAttribute`
- `TestCollectionOrdererAttribute`
- `TestFrameworkAttribute`

例如，`[assembly: CollectionBehavior("MyNamespace.MyCollectionFactory", "MyAssembly")]` 必须转换为 `[assembly: CollectionBehavior(typeof(MyNamespace.MyCollectionFactory))]`。

### 步骤 8：从 FactAttribute 或 TheoryAttribute 继承（如果适用）

识别是否有任何自定义属性继承自 `FactAttribute` 或 `TheoryAttribute`。这些自定义用户定义属性必须现在提供源信息。例如，如果属性看起来像这样：

```csharp
internal sealed class MyFactAttribute : FactAttribute
{
    public MyFactAttribute()
    {
    }
}
```

它必须更改为这样：

```csharp
internal sealed class MyFactAttribute : FactAttribute
{
    public MyFactAttribute(
        [CallerFilePath] string? sourceFilePath = null,
        [CallerLineNumber] int sourceLineNumber = -1
    ) : base(sourceFilePath, sourceLineNumber)
    {
    }
}
```

在报告完成之前，读取回每个受影响的 `FactAttribute`-和 `TheoryAttribute`-派生的构造函数。命名每个类型，并确认两个调用信息参数和相应的 `base(sourceFilePath, sourceLineNumber)` 转发都存在。单独通过通过的测试不能证明源信息已传播。

### 步骤 9：从 BeforeAfterTestAttribute 继承（如果适用）

识别是否有任何自定义属性继承自 `BeforeAfterTestAttribute`。这些自定义用户定义属性必须更新其方法签名。以前，它们将具有如下所示的 `Before`/`After` 重写：

```csharp
    public override void Before(MethodInfo methodUnderTest)
    {
        // 可能有一些自定义逻辑在这里
        base.Before(methodUnderTest);
        // 可能有一些自定义逻辑在这里
    }

    public override void After(MethodInfo methodUnderTest)
    {
        // 可能有一些自定义逻辑在这里
        base.After(methodUnderTest);
        // 可能有一些自定义逻辑在这里
    }
```

它必须更改为这样：

```csharp
    public override void Before(MethodInfo methodUnderTest, IXunitTest test)
    {
        // 可能有一些自定义逻辑在这里
        base.Before(methodUnderTest, test);
        // 可能有一些自定义逻辑在这里
    }

    public override void After(MethodInfo methodUnderTest, IXunitTest test)
    {
        // 可能有一些自定义逻辑在这里
        base.After(methodUnderTest, test);
        // 可能有一些自定义逻辑在这里
    }
```

保留 `BeforeAfterTestAttribute` 基类，保留重写修饰符，并保留现有的基调用及其相对于自定义逻辑的顺序。直接实现 `IBeforeAfterTestAttribute` 可能会编译，但它不是机械的 v2 到 v3 迁移，并且可能会丢弃基类行为。

在报告完成之前，读取结果属性文件并引用实际的 `Before(MethodInfo, IXunitTest)` 和 `After(MethodInfo, IXunitTest)` 签名。明确确认 `base.Before` 和 `base.After` 都接收相同的 `IXunitTest` 参数；重述重写已更新的通用声明是不充分的证据。

### 步骤 10：处理新的 xUnit 分析器警告（如果适用）

xunit.v3 引入了新的分析器警告。最值得注意的是 xUnit1051（使用 `TestContext.Current.CancellationToken` 为接受 `CancellationToken` 的方法）。如果存在，请处理这些警告。

### 步骤 11：迁移 `Xunit.SkippableFact`（如果适用）

如果存在任何对 `Xunit.SkippableFact` 的包引用，请完全删除这些包引用。

然后，按照以下步骤消除来自已删除包引用的 API 的使用：

- 将任何 `SkippableFact` 属性更新为常规的 `Fact` 属性。
- 将任何 `SkippableTheory` 属性更新为常规的 `Theory` 属性。
- 将 `Skip.If` 方法调用更改为 `Assert.SkipWhen`。
- 将 `Skip.IfNot` 方法调用更改为 `Assert.SkipUnless`。

在实用的情况下，验证两个分支：默认条件应报告预期的跳过原因，而启用条件应执行并通过。grep 加上通用的通过运行不能证明运行时跳过语义已保留。

将此转换限制在现有的项目/中心包文件和包含这些 API 的源文件中。不要仅为执行此伴生包迁移而创建新的 `Directory.Build.props`；任何必需的运行器属性属于没有现有共享 props 文件时存在的测试项目。

### 步骤 12：更新伴生包（如果适用）

- 查询配置的源以获取相互兼容的包集，而不是独立解析每个包。`Xunit.Combinatorial` 1.x 移动到 2.x 或更高版本，而 `Xunit.StaFact` 1.x 移动到与所选 `xunit.v3` 主要版本兼容的行。
- 不要从产品名称或匹配的主要编号推断伴生兼容性。使用包依赖约束和配置源上可用的版本，然后通过测试发现证明所选的包集。
- 在从 Linux/macOS 转换到可执行输出后构建的 `net*-windows` 项目中，如果打算进行跨平台构建，请设置 `EnableWindowsTargeting=true`。
- 运行测试并单独确认预期的平台跳过（例如 Linux 上的 STA 测试）与失败分开。

### 步骤 13：构建和验证

构建解决方案并修复任何剩余的编译错误。运行 `dotnet test` 以验证所有测试在迁移后都能以与迁移前相同的结果通过。
