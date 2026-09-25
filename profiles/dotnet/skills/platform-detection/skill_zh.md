# 测试平台和框架检测

确定项目使用**哪个测试平台**（VSTest 或 Microsoft.Testing.Platform）以及**哪个测试框架**（MSTest、xUnit、NUnit、TUnit）。

## 响应契约

尊重用户请求的标签和顺序，用实际分类替换每个占位符。首先给出结论：不要在结论之前放置标题、分析草稿、工具语法或重复的模板。接着用一句简洁的证据句子命名所需的存储库事实来证明每个请求的分类。当请求 `Framework` 时，命名标识它的包或项目 SDK。仅使用第二句来报告冲突、不完整的配置或目标框架特定的差异。

`Platform` 指的是实际执行测试的平台：**VSTest** 或 **MTP**。如果冲突或不完整的配置阻止执行，则报告为不可用，而不是编造一个成功的平台。

不要仅根据 `global.json` 的 `test.runner` 来分类执行的平台。该设置选择 `dotnet test` 命令模式；即使显式指定 `VSTest` 值也可以桥接到可执行的 MTP 应用程序。在写入 `Platform:` 之前，继续通过项目运行器、桥接器和输出形状信号。

在起草证据之前应用此范围门：

| 用户请求 | 包括的证据 | 忽略 |
|---------------|---------------------|------|
| 平台和框架 | 最终运行器选择器及其获胜来源；标识框架的包或项目 SDK；当需要时，使其可执行的属性 | 命令模式；常见 SDK 事实；`OutputType` 除非它缺失或冲突 |
| 单一决定信号 | 该运行器选择属性、其来源为何获胜以及为何竞争包不选择或暗示 VSTest；仍然命名标识请求框架的包或项目 SDK | 桥接器、`OutputType`、SDK 模式和无关的先决条件，当配置完整时 |
| 每个目标框架的平台 | 仅命名因目标而异的条件最终值 | 常见属性和项目范围的 SDK 评论 |
| 显式排除 | 最终 `UseVSTest` 值及其获胜来源 | 被覆盖的默认值，除非它们造成冲突 |
| `dotnet test` 模式 | 独立的命令模式和执行平台分类 | 无所请求的轴 |

如果请求的标签省略了 `dotnet test` 模式，则在整个响应中不要陈述或解释命令模式。一个精确的桥接属性可能仍然是决定性的平台证据，但不要将其变成 SDK 或 CLI 模式评论。当用户询问哪个单一信号决定显式运行器属性和 `Microsoft.NET.Test.Sdk` 之间的选择时，证据句子必须说明运行器属性选择 MTP，而 `Microsoft.NET.Test.Sdk` 不选择或暗示 VSTest。

当导入优先级决定属性时，说明获胜来源为何获胜（例如，它导入得更晚或其条件适用），而不仅仅是它包含最终值或覆盖另一个分配。

将解释保持在请求的轴上：

- `global.json` 中的 SDK 版本固定是上下文，不是平台选择器。仅在 `global.json` 的 `test.runner` 设置实际这样做时，才声称 `global.json` 选择 VSTest 或原生 MTP。
- 如果 `UseVSTest=true` 具有决定性，请直接说明。不要推测缺少 `test.runner` 或将 SDK 固定描述为额外的平台选择。
- 如果未请求命令模式，即使它内部需要来确定执行平台，也不要添加它。

当经典项目请求还要求命令系列时，添加直接行，例如 `Command family: MSBuild + vstest.console.exe`；不要将其变成可选替代或添加不必要的构建限定符。

对于基于文件的请求，一次枚举以下配置名称，然后以批量操作读取每个相关的文件：
`global.json`、`.csproj`、`packages.config`、`Directory.Build.props`、`Directory.Build.targets`、`Directory.Packages.props` 和显式导入的 `.props` / `.targets`。项目文件中缺失的设置可能由导入定义，因此永远不要从 `.csproj` 单独推断其最终值。当存储库配置足够时，不要搜索网络或检查无关文件。

按照实际的 MSBuild 导入顺序解析属性，而不是使用固定的“项目优先于 props”规则。对于每个适用的目标框架：

1. 跟随导入图和条件。较晚适用的分配获胜。`Directory.Build.props` 通常在项目主体之前导入，因此无条件的项目分配通常覆盖它；较后的 `.targets` 可以再次覆盖项目。
2. 记录 `UseVSTest`、框架运行器选择器、`TestingPlatformDotnetTestSupport` 和 `OutputType` 的最终值及其获胜来源。
3. 将 `Directory.Packages.props` 视为版本证据，除非它也包含相关属性。在应用版本相关的默认值之前解析包/SDK 版本。
4. 不要从包存在中推断属性。包或 SDK 默认仅在解析的版本实际提供它且没有后续分配覆盖它时才计算。

## 检测项目系统

在选择 CLI 之前对项目进行分类：

- 根 `Sdk` 属性或 `<Sdk>` 声明：SDK 风格。
- `ToolsVersion`、`Microsoft.Common.props` / `Microsoft.CSharp.targets` 导入、显式 `<Reference>` 和 `<Compile Include>` 项：经典非 SDK。
- `packages.config`：经典 NuGet 依赖管理。

经典项目仍然可以使用 VSTest 兼容的适配器，但 `dotnet test` 不会自动成为有效的调用。保留存储库脚本/CI 命令，通常是 MSBuild 后跟 `vstest.console.exe`。仅在存储库配置或文档建立该遗留运行器时才提及 `MSTest.exe`。

## 检测测试框架

读取 `.csproj`、相邻的 `packages.config` 以及 `Directory.Build.props` / `Directory.Packages.props`，并查找：

| 包或 SDK 引用 | 框架 |
|--------------------------|-----------|
| `MSTest` 元包、`<Project Sdk="MSTest.Sdk[/version]">` 或 `<Sdk Name="MSTest.Sdk">` | MSTest |
| `MSTest.TestFramework` + `MSTest.TestAdapter` | MSTest（也适用于 v3/v4） |
| `xunit`、`xunit.v3`、`xunit.v3.mtp-v1`、`xunit.v3.mtp-v2`、`xunit.v3.core.mtp-v1`、`xunit.v3.core.mtp-v2` | xUnit |
| `NUnit` + `NUnit3TestAdapter` | NUnit |
| `TUnit` | TUnit（仅限 MTP） |

在经典项目中，包 ID 和版本可能仅在 `packages.config` 中出现，而项目包含具有 `HintPath` 值的 assembly `<Reference>` 元素。使用这两个来源。

## 检测执行的测试平台

如果用户显式请求 `dotnet test` 模式，则在回答之前读取 [`references/command-mode.md`](references/command-mode.md)。对于仅请求平台/框架的请求，不要加载该参考或提及命令模式。

对于明确请求命令模式且没有有效桥接的 SDK 8/9 请求，在一个因果句子中陈述所有三个事实：运行器使项目 MTP 兼容，`dotnet test` 保持 VSTest 模式，并且缺失的桥接意味着 VSTest 实际执行测试。仅在它有助于解释该结果时，才提及原生 MTP 命令模式从 SDK 10 开始。

当允许执行且提示或 `global.json` 未识别 SDK 时，运行一次 `dotnet --version`。对于禁止执行的只读识别请求，不要探测安装的 SDK；使用存储库事实并声明任何必要的 SDK 假设。

在解析最终属性值后，按此顺序分类：

1. 最终 `UseVSTest=true` 选择 VSTest。如果 `global.json` 同时选择原生 MTP 命令模式，则报告 `Platform: unavailable`，因为命令模式和项目排除冲突。
2. `global.json` 中的原生 MTP 选择在 MTP 上执行具有最终 `OutputType=Exe` 的兼容 MTP 应用程序。仅 VSTest、库输出或排除的项目不可用。
3. 在 SDK 8/9 上，启用的 MTP 运行器加上最终 `TestingPlatformDotnetTestSupport=true` 加上最终 `OutputType=Exe` 在 MTP 上执行。
4. 如果运行器启用但桥接缺失或为假，双功能的 MSTest、NUnit 或 xUnit 项目保持 VSTest：运行器建立 MTP 兼容性，但 SDK 8/9 的 `dotnet test` 无法到达它，VSTest 适配器执行测试。如果桥接为真但没有运行器启用，项目也保持 VSTest。
5. 运行器和桥接具有非可执行输出，则不完整且不可用。无法通过所选 SDK 路径访问的 MTP 仅框架也是不可用的，不是 VSTest。

保持每个信号的角色精确：

- 运行器属性选择测试应用程序。
- `TestingPlatformDotnetTestSupport=true` 允许 SDK 8/9 的 `dotnet test` 到达该应用程序。
- `OutputType=Exe` 提供可执行主机形状。它**不**选择或启用 MTP。

不要将 `MSTest` 元包与 `MSTest.Sdk` 项目 SDK 混淆。`PackageReference Include="MSTest"` 加上 `EnableMSTestRunner=true` 启用 MSTest MTP 运行器，但它**不**隐式设置 `TestingPlatformDotnetTestSupport`。

`MSTest.Sdk` 默认启用 MTP 运行器。检查其解析版本和评估属性以确定桥接行为：版本 3.8 除非后续分配覆盖它，否则提供 `TestingPlatformDotnetTestSupport`，而较新的 .NET 10 SDK 可能期望原生 MTP 模式。`<UseVSTest>true</UseVSTest>` 重新选择 VSTest。

| 信号 | 含义 |
|--------|---------|
| `<Project Sdk="MSTest.Sdk...">` 且没有 `UseVSTest` | MTP 应用程序；检查解析的 SDK 版本和评估的桥接属性 |
| `MSTest` 元包 + `<EnableMSTestRunner>true>` | MTP 运行器启用；不隐含 VSTest 到 MTP 的桥接 |
| `<UseMicrosoftTestingPlatformRunner>true` | 决定 xUnit 运行器选择信号 |
| `<EnableMSTestRunner>true>` / `<EnableNUnitRunner>true>` | 决定 MSTest/NUnit 运行器选择信号 |
| `TestingPlatformDotnetTestSupport=true` | VSTest 到 MTP 桥接的执行先决条件，不是运行器选择信号 |
| `Microsoft.Testing.Platform` 包 | MTP 兼容的应用程序；本身不能决定 |
| `TUnit` | 仅限 MTP 的框架 |
| 最终评估的 `<OutputType>Exe</OutputType>` | 基于包的 MTP 应用程序所需的可执行主机形状 |

`Microsoft.NET.Test.Sdk` 单独不能决定；它可以在 MTP 启用的项目中保留以兼容。当显式覆盖决定结果时，命名最终覆盖及其来源，而不是被覆盖的默认值。
当运行器选择属性与 `Microsoft.NET.Test.Sdk` 竞争时，说明运行器属性选择 MTP，而 `Microsoft.NET.Test.Sdk` **不**选择或暗示 VSTest。它可以保留作为兼容性支持，但这次要。`TestingPlatformDotnetTestSupport=true` 是桥接先决条件，不是运行器选择信号；永远不要说这个属性单独启用桥接。对于请求哪个单一信号决定的请求，停止于此。当配置完整时，省略桥接或主机形状先决条件，仅在需要解释为何选定的运行器无法执行时才添加它们。
同样，当启用的运行器被覆盖或无法访问时，因果地陈述两个轴：运行器属性使项目 MTP 兼容，但最终的 `UseVSTest`/桥接/输出设置决定实际执行的平台。在命名运行器选择器之前使用包引用仅用于标识框架。

使用因果证据，而不是一堆信号。例如：

```text
Platform: MTP
Framework: NUnit

Directory.Build.props 提供最终 `EnableNUnitRunner=true` 和
`TestingPlatformDotnetTestSupport=true`，因此 NUnit 在 MTP 上执行。
```

对于不兼容的配置，在结论后给出一个最小的对齐选择，而不要修改文件：要么全局选择项目的配置平台，要么删除项目排除以使用全局选择的平台。

### 条件和每个目标框架属性

评估每个目标框架的运行器和桥接属性。如果条件产生不同的执行平台，请显式报告每个目标（例如，`net8.0: VSTest`，`net9.0: MTP`），而不是将项目折叠到一个全局平台。
