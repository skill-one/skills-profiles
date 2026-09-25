# VSTest -> Microsoft.Testing.Platform 迁移

将 .NET 测试解决方案从 VSTest 迁移到 Microsoft.Testing.Platform (MTP)。结果是一个所有测试项目都在 MTP 上运行、`dotnet test` 正常工作且 CI/CD 管道已更新的解决方案。

## 首要操作

在搜索网络或凭记忆回答之前，检查提供的项目、`Directory.Build.props`、`global.json` 和 CI 文件。首先解决框架和 SDK 模式：.NET 9 及更早版本使用兼容性属性加上 `--` 分隔符；.NET 10 原生 MTP 使用 `global.json`、移除该属性并通过分隔符传递 MTP 参数。对于中央属性，在 `Directory.Build.props` 中永远不要基于 `IsTestProject` 进行条件化；使用那里已经存在的属性，例如 `MSBuildProjectName`。

> **重要**：不要在同一个解决方案或运行配置中混合基于 VSTest 和基于 MTP 的 .NET 测试项目——这是一个不受支持的场景。

## 何时使用

- 从 VSTest 切换到 Microsoft.Testing.Platform 以支持任何测试框架
- 为测试项目启用 `dotnet run` / `dotnet watch` / 直接可执行文件执行
- 启用原生 AOT 或修剪测试执行
- 在 MTP 上用 `dotnet test` 替换 `vstest.console.exe`
- 将 CI/CD 管道从 VSTest 任务更新为 .NET Core CLI 任务
- 将 `dotnet test` 参数从 VSTest 语法更新为 MTP 语法

## 何时不用

- 项目已经在 Microsoft.Testing.Platform 上运行，并且没有剩余的 MTP 行为差异需要解决（例如，发现零测试的退出代码 8）
- 在测试框架之间迁移（例如，MSTest 到 xUnit.net）——完全是不同的工作量
- 项目构建 UWP 或打包的 WinUI 测试项目——MTP 目前不支持这些
- 解决方案混合了 .NET 和非 .NET 测试适配器（例如，JavaScript 或 C++ 适配器）——需要 VSTest
- 升级 MSTest 版本——使用 `migrate-mstest-v1v2-to-v3` 或 `migrate-mstest-v3-to-v4`

## 输入

| 输入 | 是否必需 | 描述 |
|-------|----------|-------------|
| 项目或解决方案路径 | 否 | 包含测试项目的 `.csproj`、`.sln` 或 `.slnx` 入口点。**自行发现**通过通配符搜索工作目录；仅在未找到或选择确实模棱两可时才询问 |
| 测试框架 | 否 | MSTest、NUnit、xUnit.net v2 或 xUnit.net v3。从包引用自动检测 |
| .NET SDK 版本 | 否 | 确定 `dotnet test` 集成模式。优先使用存储库的 `global.json` 或明确声明的 CI SDK；仅在存储库未固定或声明时才使用主机 `dotnet --version` |
| CI/CD 管道文件 | 否 | 调用 `vstest.console` 或 `dotnet test` 的管道定义路径 |

## 执行和回答协议

- 在当前工作目录中发现项目、props、`global.json` 和管道文件。打开字面搜索结果；技能目录不是用户的存储库。激活技能后继续，不要询问可发现路径。
- 对于实现请求，编辑文件，然后验证有效的 MSBuild 属性、翻译的命令、测试计数和请求的工件。对于问题，提供针对检测到的 SDK 和框架的精确命令/配置，而不是近似等效项的菜单。
- 保留所有构建参数并避免引入 `--no-build`、新的设置文件或不相关的包升级。除非该文件存在，否则永远不要保留 `--settings <file>`。
- 对于 .NET 9 及更早版本，显示 `--` 分隔符。对于 .NET 10 原生 MTP 模式，明确说明要移除它。
- 当有意抑制退出代码 8 时，警告广泛抑制可能会隐藏由不良过滤器导致的无意空运行；将其范围限制为已知的零测试项目/配置。
- 对于退出代码 8 的问题，显示所有三个具体形式：`--ignore-exit-code 8`、`TestingPlatformCommandLineArguments` 和 `TESTINGPLATFORM_EXITCODE_IGNORE=8`。
- 对于 xUnit v3 过滤器，提供可直接使用的 `--filter-class`/`--filter-method`/`--filter-trait` 命令并解释 AND 行为。当解析的 xUnit 版本支持它时，包括 `--filter-query` 路径语法以用于复杂表达式，并链接 xUnit 查询过滤器文档。
- 在翻译报告器、覆盖率或转储时，在回答中命名每个必需的包；一个看起来正确的选项而没有其拥有的扩展包是不完整的。
- 最终结果必须命名框架运行器选择、存储库选择的 SDK 集成模式、精确翻译的命令、扩展包和验证证据。

## 工作流程

### 第 1 步：评估解决方案

1. 确定每个测试项目的测试框架——参见 `platform-detection` 技能以了解包到框架的映射。关键指标：
   - **MSTest**：引用 `MSTest` 或 `MSTest.TestAdapter`，或使用 `MSTest.Sdk`（`<IsTestApplication>` 未设置为 `false`）。注意：`MSTest.TestFramework` 仅是库依赖项，不是测试项目。
   - **NUnit**：引用 `NUnit3TestAdapter`
   - **xUnit.net**：引用 `xunit` 和 `xunit.runner.visualstudio`
2. 从 `global.json` 或明确用户上下文解决存储库/CI 使用的 SDK。仅在两者都不存在时才回退到 `dotnet --version`；代理主机 SDK 不能无声地覆盖声明的 .NET 8/9 CI 目标。
3. 检查解决方案或存储库根目录是否存在 `Directory.Build.props` 文件——所有 MTP 属性都应放在那里以保持一致性
4. 检查 CI 脚本或管道定义中是否使用 `vstest.console.exe`
5. 检查 CI 脚本中的 VSTest 特定 `dotnet test` 参数：`--filter`、`--logger`、`--collect`、`--settings`、`--blame*`
6. 运行 `dotnet test` 以建立测试通过/失败的基线计数

### 第 2 步：设置 Directory.Build.props

> **关键**：尽可能在解决方案或存储库根目录的 `Directory.Build.props` 中设置 MTP 运行器属性，而不是每个项目。这可以防止不一致的配置，其中一些项目使用 VSTest，而其他项目使用 MTP（这是一个不受支持的场景）。
> **注意**：MTP 还要求测试项目具有 `<OutputType>Exe</OutputType>`。只有 `MSTest.Sdk` 会自动设置此属性。对于所有其他设置（MSTest NuGet 包带有 `EnableMSTestRunner`、NUnit 带有 `EnableNUnitRunner`、xUnit.net 带有 `YTest.MTP.XUnit2`），请在 `Directory.Build.props` 中集中设置 `<OutputType>Exe</OutputType>`，并使用仅针对测试项目的条件。如果您无法从 `Directory.Build.props` 可靠地仅针对测试项目，则按项目设置 `<OutputType>Exe</OutputType>` 是一个可接受的例外。
>
> **`Directory.Build.props` 中的条件化**：**不要**使用 `Condition="'$(IsTestProject)' == 'true'"`——`IsTestProject` 是在评估后期由测试 SDK 目标设置的，在 `Directory.Build.props` 导入时不可用。使用早期可用的属性（例如 `MSBuildProjectName`）来通过命名约定定位测试项目。例如，如果所有测试项目都以 `.Tests` 结尾：
>
> ```xml
> <PropertyGroup Condition="$(MSBuildProjectName.EndsWith('.Tests'))">
>   <OutputType>Exe</OutputType>
> </PropertyGroup>
> ```
>
> 调整条件（例如，`.EndsWith('Tests')`、`.Contains('.Test')`）以匹配存储库中使用的测试项目命名约定。
>
> 将每个适用的中央属性放在同一个条件中：`OutputType`、框架运行器选择，以及 .NET 9 及更早版本的 `TestingPlatformDotnetTestSupport`。不要留下无条件的运行器属性，它仍然会影响生产项目。

### 第 3 步：启用特定于框架的 MTP 运行器

每个框架都有自己的选择属性。在 `Directory.Build.props` 中添加这些以保持一致性。

#### MSTest

**选项 A -- MSTest NuGet 包（3.2.0+）：**

```xml
<PropertyGroup>
  <EnableMSTestRunner>true</EnableMSTestRunner>
  <OutputType>Exe</OutputType>
</PropertyGroup>
```

确保项目引用 MSTest 3.2.0 或更高版本。如果版本已经是 3.2.0+，则不需要为 MTP 迁移升级 MSTest 版本。

**选项 B -- MSTest.Sdk：**

当使用 `MSTest.Sdk` 时，MTP 会自动启用——不需要 `EnableMSTestRunner` 或 `OutputType Exe` 属性（SDK 会自动设置这两个属性）。唯一的操作是：如果项目有 `<UseVSTest>true</UseVSTest>`，则**移除它**。该属性强制项目使用 VSTest 而不是 MTP。

#### NUnit

需要 `NUnit3TestAdapter` **5.0.0** 或更高版本。

1. 更新 `NUnit3TestAdapter` 到 5.0.0+：

```xml
<PackageReference Include="NUnit3TestAdapter" Version="5.0.0" />
```

1. 启用 NUnit 运行器：

```xml
<PropertyGroup>
  <EnableNUnitRunner>true</EnableNUnitRunner>
  <OutputType>Exe</OutputType>
</PropertyGroup>
```

#### xUnit.net

添加对 `YTest.MTP.XUnit2` 的引用——此包为 xUnit.net v2 项目提供 MTP 支持，而无需升级到 xunit.v3。您还必须将 `OutputType` 设置为 `Exe`：

```xml
<PackageReference Include="YTest.MTP.XUnit2" Version="0.4.0" />
```

```xml
<PropertyGroup>
  <OutputType>Exe</OutputType>
</PropertyGroup>
```

> **注意**：`YTest.MTP.XUnit2` 保留了 VSTest 的 `--filter` 语法，因此无需为 xUnit.net v2 迁移过滤器。它还支持 `--settings` 用于 runsettings（仅 xunit 特定的配置）、`xunit.runner.json`、通过 `--report-trx` 的 TRX 报告，以及 `--treenode-filter`。

#### xUnit.net v3

xUnit.net v3 (`xunit.v3` 包) 具有内置的 MTP 支持。使用以下方式启用它：

```xml
<PropertyGroup>
  <UseMicrosoftTestingPlatformRunner>true</UseMicrosoftTestingPlatformRunner>
</PropertyGroup>
```

> **重要**：xUnit.net v3 在 MTP 上**不支持** VSTest 的 `--filter` 语法。您必须将过滤器转换为 xUnit.net v3 的原生过滤器选项（见第 5 步）。

### 第 4 步：配置 dotnet test 集成

`dotnet test` 集成取决于 .NET SDK 版本。

#### .NET 10 SDK 及更高版本（推荐）

通过在 `global.json` 中添加 `test` 部分来使用原生 MTP 模式：

```json
{
  "sdk": {
    "version": "10.0.100"
  },
  "test": {
    "runner": "Microsoft.Testing.Platform"
  }
}
```

在此模式下，`dotnet test` 参数直接传递——例如，`dotnet test --report-trx`。

> **重要**：`global.json` 不支持尾随逗号。确保 JSON 严格有效。

#### .NET 9 SDK 及更早版本

使用 `dotnet test` 命令的 VSTest 模式来运行 MTP 测试项目，在 `Directory.Build.props` 中添加此属性：

```xml
<PropertyGroup>
  <TestingPlatformDotnetTestSupport>true</TestingPlatformDotnetTestSupport>
</PropertyGroup>
```

> **重要**：在此模式下，您必须使用 `--` 来分隔 `dotnet test` 构建参数和 MTP 参数。例如：`dotnet test --no-build -- --list-tests`。

### 第 5 步：更新 dotnet test 命令行参数

必须将 VSTest 特定参数转换为 MTP 等效项。构建相关参数（`-c`、`-f`、`--no-build`、`--nologo`、`-v` 等）保持不变。

| VSTest 参数 | MTP 等效项 | 备注 |
|-----------------|----------------|-------|
| `--test-adapter-path` | 不适用 | MTP 不使用外部适配器发现 |
| `--blame` | 不适用 | |
| `--blame-crash` | `--crashdump` | 需要 `Microsoft.Testing.Extensions.CrashDump` NuGet 包 |
| `--blame-crash-dump-type <TYPE>` | `--crashdump-type <TYPE>` | 需要 CrashDump 扩展 |
| `--blame-hang` | `--hangdump` | 需要 `Microsoft.Testing.Extensions.HangDump` NuGet 包 |
| `--blame-hang-dump-type <TYPE>` | `--hangdump-type <TYPE>` | 需要 HangDump 扩展 |
| `--blame-hang-timeout <TIMESPAN>` | `--hangdump-timeout <TIMESPAN>` | 需要 HangDump 扩展 |
| `--collect "Code Coverage;Format=cobertura"` | `--coverage --coverage-output-format cobertura` | 每个扩展的参数 |
| `-d\|--diag <LOG_FILE>` | `--diagnostic` | |
| `--filter <EXPRESSION>` | `--filter <EXPRESSION>` | MSTest、NUnit 和 xUnit.net v2（使用 `YTest.MTP.XUnit2`）具有相同的语法。对于 xUnit.net v3，见过滤器迁移下方 |
| `-l\|--logger trx` | `--report-trx` | 需要 `Microsoft.Testing.Extensions.TrxReport` NuGet 包 |
| `--results-directory <DIR>` | `--results-directory <DIR>` | 相同 |
| `-s\|--settings <FILE>` | `--settings <FILE>` | MSTest 和 NUnit 仍然支持 `.runsettings` |
| `-t\|--list-tests` | `--list-tests` | 相同 |
| `-- <RunSettings args>` | `--test-parameter` | 仅适用于 MSTest 和 NUnit |

#### 过滤器迁移

**MSTest、NUnit 和 xUnit.net v2（使用 `YTest.MTP.XUnit2`）**：VSTest `--filter` 语法在 VSTest 和 MTP 上相同。无需更改。

**xUnit.net v3（原生 MTP）**：xUnit.net v3 在 MTP 上**不支持** VSTest 的 `--filter` 语法。您必须将过滤器转换为 xUnit.net v3 的原生过滤器选项。

#### xUnit.net v3 过滤器标志

| 标志 | 描述 |
|------|-------------|
| `--filter-class "name"` | 运行给定类中的所有测试。支持通配符（`*`）。 |
| `--filter-not-class "name"` | 排除给定类中的所有测试 |
| `--filter-method "name"` | 运行特定测试方法 |
| `--filter-not-method "name"` | 排除特定测试方法 |
| `--filter-namespace "name"` | 运行命名空间中的所有测试 |
| `--filter-not-namespace "name"` | 排除命名空间中的所有测试 |
| `--filter-trait "name=value"` | 运行具有匹配特性的测试 |
| `--filter-not-trait "name=value"` | 排除具有匹配特性的测试 |

多个值可以指定为一个标志：`--filter-class Foo Bar`。

#### VSTest → xUnit.net v3 过滤器转换表

| VSTest `--filter` 语法 | xUnit.net v3 MTP 等效项 | 备注 |
|---|---|---|
| `FullyQualifiedName~ClassName` | `--filter-class *ClassName*` | 通配符需要用于子字符串匹配 |
| `FullyQualifiedName=Ns.Class.Method` | `--filter-method Ns.Class.Method` | 完全匹配方法 |
| `Name=MethodName` | `--filter-method *MethodName*` | 通配符用于子字符串匹配 |
| `Category=Value` (特性) | `--filter-trait "Category=Value"` | 通过特性名称/值对过滤 |
| 复杂表达式 | `--filter-query "expr"` | 使用 xUnit.net 查询过滤器语言（见下方） |

#### xUnit.net v3 查询过滤器语言

对于复杂表达式，使用 `--filter-query` 并使用路径段语法：

```text
/<assemblyFilter>/<namespaceFilter>/<classFilter>/<methodFilter}[traitName=traitValue]
```

每个段匹配：程序集名称、命名空间、类名、方法名。在任意段中使用 `*` 表示“匹配所有”。文档：<https://xunit.net/docs/query-filter-language>

当直接对应的 `--filter-class` / `--filter-method` /
`--filter-trait` 标志可以表达原始过滤器时，优先使用它们。仅在通过 `--list-tests` 验证查询后使用 `--filter-query`；一个语法接受的查询如果选择零测试则不是成功的转换。

#### 转换示例

```shell
# VSTest
dotnet test --filter "FullyQualifiedName~IntegrationTests&Category=Smoke"

# xUnit.net v3 MTP -- 使用单独的过滤器（AND 行为）
dotnet test -- --filter-class *IntegrationTests* --filter-trait "Category=Smoke"

# xUnit.net v3 MTP -- 使用查询语言（程序集/命名空间/类/方法[特性]）
dotnet test -- --filter-query "/*/*/*IntegrationTests*/*[Category=Smoke]"
```

> **注意**：当组合 `--filter-class` 和 `--filter-trait` 时，两者都必须匹配（AND 行为）。对于复杂表达式，使用 `--filter-query` 并使用路径段语法。参见 [xUnit.net 查询过滤器语言文档](https://xunit.net/docs/query-filter-language) 获取完整参考。

### 第 6 步：安装 MTP 扩展包（如果需要）

如果 CI 脚本使用 TRX 报告、崩溃转储、挂起转储或覆盖率，请添加相应的包。在中央包管理下，项目的引用是：

```xml
<ItemGroup>
  <PackageReference Include="Microsoft.Testing.Extensions.TrxReport" />
  <PackageReference Include="Microsoft.Testing.Extensions.CrashDump" />
  <PackageReference Include="Microsoft.Testing.Extensions.HangDump" />
  <PackageReference Include="Microsoft.Testing.Extensions.CodeCoverage" />
</ItemGroup>
```

在 `Directory.Packages.props` 中添加匹配的 `PackageVersion` 条目。如果没有中央包管理，请将配置源中解析的确切版本放在这些引用上。保持与选择的 MTP 堆栈兼容的版本；不要从迁移指南中复制固定的版本。

### 第 7 步：更新 CI/CD 管道

#### Azure DevOps

**如果使用 VSTest 任务 (`VSTest@3`)**：用 .NET Core CLI 任务 (`DotNetCoreCLI@2`) 替换：

```yaml
# Before (VSTest task)
- task: VSTest@3
  inputs:
    testAssemblyVer2: '**/*Tests.dll'
    runSettingsFile: 'test.runsettings'

# After (.NET Core CLI task)
- task: DotNetCoreCLI@2
  displayName: Run tests
  inputs:
    command: 'test'
    arguments: '--no-build --configuration Release'
```

**如果已经使用 DotNetCoreCLI@2**：根据第 5 步的转换更新参数。记住 .NET 9 及更早版本上的 `--` 分隔符：

```yaml
- task: DotNetCoreCLI@2
  displayName: Run tests
  inputs:
    command: 'test'
    arguments: '--no-build -- --report-trx --results-directory $(Agent.TempDirectory)'
```

#### GitHub Actions

更新工作流文件中的 `dotnet test` 调用，使用与第 5 步相同的参数转换。

#### 替换 vstest.console.exe

如果任何脚本直接调用 `vstest.console.exe`，请将其替换为 `dotnet test`。测试项目现在是可执行文件，也可以直接运行。

### 第 8 步：处理行为差异

#### 零测试退出代码

VSTest 在发现零测试时静默成功。MTP 使用退出代码 8 失败。选项：

- 运行测试时传递 `--ignore-exit-code 8`
- 在 `Directory.Build.props` 中添加：

```xml
<PropertyGroup>
  <TestingPlatformCommandLineArguments>$(TestingPlatformCommandLineArguments) --ignore-exit-code 8</TestingPlatformCommandLineArguments>
</PropertyGroup>
```

- 使用环境变量：`TESTINGPLATFORM_EXITCODE_IGNORE=8`

### 第 9 步：移除仅 VSTest 需要的包（可选）

迁移完成后并验证后，移除仅 VSTest 需要的包：

- `Microsoft.NET.Test.Sdk` —— 不需要用于 MTP（MSTest.Sdk v4 默认不包含它）
- `xunit.runner.visualstudio` —— 仅用于 VSTest 发现 xUnit.net（在使用 `YTest.MTP.XUnit2` 时不需要）
- `NUnit3TestAdapter` VSTest 仅有的功能 —— 适配器仍然需要，但仅用于 MTP 运行器

> **注意**：如果您需要在过渡期间保持 VSTest 兼容性，请保留这些包。

### 第 10 步：验证

1. 运行 `dotnet build` —— 确认零错误
2. 运行 `dotnet test` —— 确认所有测试通过
3. 比较测试通过/失败计数与迁移前的基线
4. 直接运行测试可执行文件（例如，`./bin/Debug/net8.0/MyTests.exe`）——确认它正常工作
5. 验证 CI 管道生成预期的测试结果工件（TRX 文件、代码覆盖率、崩溃转储）
6. 测试 Visual Studio (17.14+) 或 VS Code 中的 Test Explorer 发现并运行测试

## 验证

- [ ] 所有测试项目使用 MTP 运行器（没有剩余的 VSTest 仅配置）
- [ ] `dotnet build` 完成时零错误
- [ ] `dotnet test` 通过所有测试，测试计数与迁移前基线匹配
- [ ] 测试可执行文件直接运行（例如，`./bin/Debug/net8.0/MyTests.exe`）
- [ ] CI 管道生成预期的测试结果工件（TRX 文件、代码覆盖率、崩溃转储）
- [ ] Visual Studio 或 VS Code 中的 Test Explorer 发现并运行测试
- [ ] CI 脚本中不再有 `vstest.console.exe` 调用
- [ ] `<OutputType>Exe</OutputType>` 为所有非 MSTest.Sdk 测试项目设置

## 常见陷阱

| 陷阱 | 解决方案 |
|---------|----------|
| 在同一个解决方案中混合 VSTest 和 MTP 项目 | 一起迁移所有测试项目——混合模式不受支持 |
| .NET 9 及更早版本上的 `dotnet test` 参数被忽略 | 使用 `--` 分隔构建参数和 MTP 参数：`dotnet test -- --report-trx` |
| CI 中没有失败但退出代码为 8 | MTP 在零测试运行时失败；使用 `--ignore-exit-code 8` 或修复测试发现 |
| MSTest.Sdk v4 + vstest.console 不再工作 | MSTest.Sdk v4 不再添加 `Microsoft.NET.Test.Sdk` —— 显式添加它或切换到 `dotnet test` |
| 缺少 `<OutputType>Exe</OutputType>` | 对于所有设置（除了 MSTest.Sdk 会自动设置它）都需要 |
| 在 `Directory.Build.props` 中使用 `Condition="'$(IsTestProject)' == 'true'"` | `IsTestProject` 在 `Directory.Build.props` 评估时尚未定义——使用 `$(MSBuildProjectName.EndsWith('.Tests'))`（或类似的基于名称的检查）代替 |

## 下一步

- 使用 `run-tests` 在新的 MTP 平台上运行测试
- 使用 `mtp-hot-reload` 在 MTP 上使用热重载进行迭代测试修复

## 更多信息

- [测试平台概述](https://learn.microsoft.com/dotnet/core/testing/test-platforms-overview)
- [从 VSTest 迁移到 Microsoft.Testing.Platform](https://learn.microsoft.com/dotnet/core/testing/migrating-vstest-microsoft-testing-platform)
- [Microsoft.Testing.Platform 概述](https://learn.microsoft.com/dotnet/core/testing/microsoft-testing-platform-intro)
- [使用 dotnet test 进行测试](https://learn.microsoft.com/dotnet/core/testing/unit-testing-with-dotnet-test)
- [Microsoft.Testing.Platform CLI 选项](https://learn.microsoft.com/dotnet/core/testing/microsoft-testing-platform-cli-options)
- [Microsoft.Testing.Platform 扩展](https://learn.microsoft.com/dotnet/core/testing/unit-testing-platform-extensions)
