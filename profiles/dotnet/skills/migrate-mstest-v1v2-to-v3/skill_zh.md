# MSTest v1/v2 -> v3 迁移

将测试项目从 MSTest v1（程序集引用）或 MSTest v2（NuGet 1.x-2.x）迁移到 MSTest v3。MSTest v3 与 v1/v2 **不是二进制兼容**的——针对 v1/v2 编译的库必须重新编译。

## 首要操作

检查提供的代码库并分类为 v1、v2、部分迁移的 v3 或已完成的 v3，然后再回答。不要先搜索网络或凭记忆回答。对于编辑请求，继续执行请求的源代码更改和验证；对于建议请求，回答后直接进行分类。

## 何时使用

- 项目引用 `Microsoft.VisualStudio.QualityTools.UnitTestFramework.dll`（MSTest v1）
- 项目使用 `MSTest.TestFramework` / `MSTest.TestAdapter` NuGet 1.x 或 2.x
- 更新 MSTest 包从 v1/v2 到 v3 后解决构建错误——包括当包已读取 3.x 而只有源代码或设置仍需修复时
- 用 `.runsettings` 替换 `.testsettings`
- 采用 MSTest.Sdk 或程序集内并行执行

## 何时不用

- 项目已在 MSTest v3 上，没有迁移相关的构建错误，且没有剩余的 `.testsettings` / `<LegacySettings>`（完全迁移）
- 从 v3 升级到 v4——使用 `migrate-mstest-v3-to-v4`
- 在框架之间迁移（MSTest 到 xUnit/NUnit）

## 边界门

在任何编辑之前检查包版本。如果所有 MSTest 引用都已为 3.x，没有报告 v1/v2 到 v3 的错误，且没有 `.testsettings` 或 `<LegacySettings>` 剩余，则说明迁移完成，无需进行更改。单独的 3.x 包版本并不能结束迁移——剩余的 v1/v2 时代设置文件或破坏性更改错误仍在范围内。不要将可用的 v3 包合并到元包中。如果请求验证，则仅运行现有测试。这会覆盖所有以下步骤。

## 输入

| 输入 | 是否必需 | 描述 |
|-------|----------|-------------|
| 项目或解决方案路径 | 否 | `.csproj`、`.sln` 或 `.slnx` 的入口点。在工作目录中通配符搜索它；如果没有找到或多个测试项目使目标不明确，则仅询问 |
| 构建命令 | 否 | 如何构建（例如，`dotnet build`，一个仓库构建脚本）。如果未提供，则自动检测 |
| 测试命令 | 否 | 如何运行测试（例如，`dotnet test`）。如果未提供，则自动检测 |

> **永远不要通过询问项目路径来打开**。用户用散文描述他们的项目是在提问，而不是隐藏文件——先从磁盘上查找。如果确实没有项目文件，请针对他们描述的设置回答，而不是仅回复一个问题。
>
> **按搜索返回的路径精确打开路径**。一个通配符返回 `./TestProject.csproj` 表示文件存在于工作目录中——在该路径上读取它。不要将其重建到本技能自己的基础目录下的绝对路径：该目录包含 `SKILL.md`，而不是用户的项目，因此读取失败，项目看起来就丢失了。如果你刚找到的文件无法打开，那么你构建的路径是错误的——用字面结果重试。在搜索仍在报告项目文件时，永远不要得出“磁盘上没有项目”的结论，也永远不要从散文描述中构建一个替代项目作为解决方案。

## 执行契约

- 技能激活不是停止点。继续在同一任务中执行工作区发现和请求的工作。
- 技能目录包含指导，而不是已标记的项目。搜索当前工作目录，打开搜索返回的精确路径，如果某个工具拒绝一个有效路径，则使用另一个可用的读取器/编辑器重试。
- 当通配符或目录搜索可以发现路径时，永远不要请求路径。只有在当前工作区搜索找到没有项目，或者多个项目确实使目标不明确时，才询问。
- 分类请求的交付成果，而不是孤立的动作：“进行编辑”、“更新此项目”或“然后构建和运行”意味着执行；“我需要更改什么？”、“我应该期待什么？”、“步骤是否相同？”或“显示给我”意味着回答，即使提示也说要升级或迁移。
- 更改文件后，指明检测到的 MSTest 版本和运行器，每个更改的文件，以及精确修复的调用/设置（例如，列出每个更改为 `AreEqual<object>`、`AreNotEqual<object>` 或 `AreSame<object>` 的断言）。报告干净的测试计数。不要在没有项目证据的情况下声称 VSTest 保留、构建或通过测试。

## 破坏性更改摘要

MSTest v3 引入了以下与 v1/v2 的破坏性更改。仅处理与项目相关的：

| 破坏性更改 | 影响 | 修复 |
|---|---|---|
| 移除了 `Assert.AreEqual(object, object)` 重载；仅保留 `AreEqual<T>(T?, T?)` | **`CS0411`**（类型参数不能被推断）或 `CS1503`——但仅当两个参数没有共同的推断类型时。两个 `object`-类型的参数仍然推断 `T = object` 并**编译不变** | 在失败的调用上添加显式的类型参数：`Assert.AreEqual<object>(expected, actual)`。对 `AreNotEqual`、`AreSame`、`AreNotSame` 也相同。保留已经可以编译的断言 |
| `DataRow` 严格类型匹配 | **不是编译错误。** 使用分析器警告 `MSTEST0014` 构建并运行时失败，提示“测试数据与方法参数不匹配”。扩展转换（`int` -> `long`）仍然绑定；窄化或不相关的类型（`1L` -> `int`，`1.0` -> `float`）不绑定 | 将字面量更改为确切的参数类型：`1` 对于 int，`1L` 对于 long，`1.0f` 对于 float。运行测试——绿色的构建在这里证明不了什么 |
| `DataRow` 限制为 16 个参数——**仅限 3.0.1 和 3.0.2** | 在这两个版本上 `CS1729`；限制在 3.0.3 中再次移除 | 在 3.0.3+（当前所有 3.x）上，更长的行是有效的——**保留它不变**。不要将多余的包装在数组中，转换为 `object`，或拆分测试。只有固定在 3.0.1/3.0.2 的项目需要操作：更新到 3.0.3+ |
| `.testsettings` / `<LegacySettings>` 不再支持 | 设置被静默忽略 | 删除 `.testsettings`，创建 `.runsettings` 并包含等效配置 |
| 超时行为在 .NET Core / Framework 上统一 | 具有 `[Timeout]` 的测试可能表现不同 | 验证超时值；如有必要，调整 |
| 已弃用目标框架：.NET 5、.NET Fx < 4.6.2、netstandard1.0、UWP < 16299、WinUI < 18362 | 构建错误 | 更新 TFM：.NET 5 -> net8.0（LTS）或 net6.0+，netfx -> net462+，netstandard1.0 -> netstandard2.0。注意：net6.0、net8.0、net9.0 都受支持 |
| 与 v1/v2 不二进制兼容 | 针对v1/v2编译的库必须重新编译 | 重新编译所有依赖项以针对 v3 |
| 测试 ID 生成已更改 | 播放列表、过滤器或 CI 历史按测试 ID 键控可能会重置 | 重新基线 ID 并验证受影响的过滤器 |
| `TargetInvocationException` 被解包 | 期望包装器的测试或基础设施观察到内部异常 | 更新异常处理以期望底层异常 |
| 初始化/清理消息现在附加到测试结果 | 第一个/最后一个测试输出可能会获得以前缺失的生命周期消息 | 更新日志处理并检查第一个/最后一个测试结果 |
| 部署目录行为在所有 TFM 上统一 | 具有硬编码部署路径的测试可能会失败 | 使用 `TestContext.DeploymentDirectory` 或部署项路径，而不是假设 |
| 可空注解已添加 | 可空启用的项目可能会获得警告 | 修复警告，不要抑制不相关的诊断 |

## 响应指南

- **始终首先识别当前版本**：在建议任何迁移步骤之前，明确声明项目中检测到的 MSTest 版本（例如，“您的项目使用 MSTest v2 (2.2.10)”或“这是一个使用 QualityTools 程序集引用的 MSTest v1 项目”）。这为迁移建议提供了基础，并确认您已读取项目文件。
- **要求项目证据，但自己收集**：不要仅凭措辞就假设 v1/v2——读取项目或中央包文件并将源代码分类为 QualityTools/v1、NuGet 1.x 或 NuGet 2.x。从工作目录中收集该证据，而不是询问用户。如果项目已在 v3+ 上且没有 v1/v2 剩余，则停止并将路由到适当的技能。
- **保留测试平台**：在框架升级期间保持 VSTest 或 MTP 不变，除非用户单独请求运行器迁移。
- **执行完整迁移**：当用户要求迁移或升级项目时，编辑文件、构建并运行测试。不要在列出破坏性更改后停止。仅建议的响应仅适用于用户询问要期待什么时。
- **集中的修复请求**（用户在升级后出现特定的编译错误）：仅解决上述表格中相关的破坏性更改。显示简洁的“之前/之后”修复。不要逐步执行完整迁移工作流。
- **DataRow 修复请求**：将每个提供的 `DataRow` 与其方法签名进行比较。不匹配可能仅构建为 `MSTEST0014` 并在测试执行期间失败。保留方法契约并通常修复字面量（`1L` -> `1` 对于 `int`），然后运行受影响的测试。**仅更改实际错误的行。** 参数计数本身在 3.0.3+ 上不是缺陷，所以除非编译器拒绝，否则保留长行。
- **在怀疑时不要更改——首先确认错误**：当您认为某个结构不受支持时，在编辑它之前构建并读取实际诊断。如果它可以编译，则此版本支持它并且不需要更改。将有效代码重写为躲避项目不适用于的限制的缺陷，而不是谨慎。
- **特定功能迁移**（用户询问一个方面，如 .testsettings、DataRow 或断言）：仅处理该功能，但处理提供的文件中的每个活动设置或受影响的用法。对于 `.testsettings`，将所有 MSTest 设置放在一个 `<MSTest>` 元素下，映射请求的部署、每个测试超时、数据收集器和其他活动配置，不要添加会话级超时。不要逐步执行无关的破坏性更改。
- **“要期待什么”问题**（用户在升级前询问）：首先声明达到 v3 所需的具体包更新，然后总结破坏性更改摘要中的每个类别，标记哪些直接适用于可见项目。将每个项目限制为一行，不要扩展到发布说明历史。
- **“要期待什么”的所需形状**：使用基于可见项目的 `Applies / Watch / No change` 表格，并涵盖破坏性更改摘要中的每一行。这种完整性是技能的价值；不要为了简洁而省略仅在运行时出现的类别。
- **完整迁移请求**（用户想要完整迁移）：遵循以下完整工作流。
- **比较问题**（用户询问 v1 与 v2 的区别）：简洁地解释——v1 使用程序集引用，必须先删除它们；v2 使用 NuGet，只需版本提升。两者都汇聚到相同的 v3 包和破坏性更改。

## 迁移路径

- **MSTest v1（程序集引用到 QualityTools）**：删除程序集引用（步骤 2），添加 v3 NuGet 包（步骤 3），修复破坏性更改（步骤 5）。
- **MSTest v2（NuGet 包 1.x-2.x）**：将包版本更新为 3.x（步骤 3），修复破坏性更改（步骤 5）。不需要删除程序集引用。

两条路径在步骤 3 处汇聚——无论起始版本如何，都应用相同的 v3 包和破坏性更改。

## 工作流

### 步骤 1：评估项目

1. 首先定位项目：在工作目录中通配符搜索 `*.csproj`、`*.sln`、`*.slnx`、`Directory.Build.props`、`Directory.Packages.props` 和 `*.testsettings`。在询问用户任何东西之前执行此操作，并打开搜索返回的精确路径（见输入下的注释）。
2. 在一次发现过程中，批量读取项目和中央配置文件，搜索受影响的 API/设置，并确定当前使用的 MSTest 版本：
   - **程序集引用**：查找项目引用中的 `Microsoft.VisualStudio.QualityTools.UnitTestFramework` -> MSTest v1
   - **NuGet 包**：检查 `MSTest.TestFramework` 和 `MSTest.TestAdapter` 包版本 -> 如果是 1.x，则为 v1；如果是 2.x，则为 v2
3. 检查目标框架是否在 v3 中被弃用（见步骤 4）。
4. 运行现有测试命令。记录发现的、通过的、失败的和跳过的计数作为基准线。

### 步骤 2：删除 v1 程序集引用（如果适用）

如果项目使用 MSTest v1 通过程序集引用：

1. 删除对 `Microsoft.VisualStudio.QualityTools.UnitTestFramework.dll` 的引用
   - 在 SDK 风格的项目中，从 `.csproj` 中删除 `<Reference>` 元素
   - 在非 SDK 风格的项目中，通过 Visual Studio 解决方案资源管理器 -> 引用 -> 右键单击 -> 删除来删除
2. 保存项目文件

### 步骤 3：更新包到 MSTest v3

使用一个包模型；不要留下重复的框架/适配器引用。

**默认——安装 MSTest 元包**：

删除单独的 `MSTest.TestFramework` 和 `MSTest.TestAdapter` 包引用，并用统一的 `MSTest` 元包替换：

```xml
<PackageReference Include="MSTest" Version="3.8.0" />
```

如果项目保持在 VSTest 上，请保留 `Microsoft.NET.Test.Sdk`，但将其更新为与所选 MSTest 发布兼容的版本。例如，`MSTest` 3.8.0 需要 `Microsoft.NET.Test.Sdk` 17.13.0 或更高版本；保留较旧的显式版本会导致 `NU1605`。如果包版本由中央管理，请更新 `Directory.Packages.props` 而不是添加内联版本。

**仅当用户请求或仓库已标准化使用 MSTest.Sdk（仅限 SDK 风格项目）时使用 MSTest.Sdk**：

将 `<Project Sdk="Microsoft.NET.Sdk">` 更改为 `<Project Sdk="MSTest.Sdk/3.8.0">`。MSTest.Sdk 自动提供 MSTest 框架、适配器和分析器。

> **重要**：MSTest.Sdk 默认为 Microsoft.Testing.Platform（MTP）。当项目本身必须保持在 VSTest 上时，设置 `<UseVSTest>true</UseVSTest>`。MSTest.Sdk v3 还在 MTP 模式下提供 `Microsoft.NET.Test.Sdk`，因此不需要单独的过渡性 `vstest.console` 调用即可更改主要运行器。不要仅仅因为框架升级而将运行器切换为副作用。

切换到 MSTest.Sdk 时，删除这些（SDK 自动提供它们）：

- **包**：`MSTest`、`MSTest.TestFramework`、`MSTest.TestAdapter`、`MSTest.Analyzers`、`Microsoft.NET.Test.Sdk`
- **属性**：`<EnableMSTestRunner>`、`<OutputType>Exe</OutputType>`、`<IsPackable>false</IsPackable>`、`<IsTestProject>true</IsTestProject>`

### 步骤 4：如有必要，更新目标框架

MSTest v3 支持 .NET 6+、.NET Core 3.1、.NET Framework 4.6.2+、.NET Standard 2.0、UWP 16299+ 和 WinUI 18362+。.NET Core 3.1 已结束生命，但 MSTest v3 仍然支持它；在此仅框架迁移期间保留它，并建议单独的运行时升级。如果项目针对 MSTest v3 弃用的框架版本，请更新为支持的一个：

| 弃用 | 推荐替换 |
|---------|----------|
| .NET 5 | .NET 8.0（当前 LTS）或 .NET 6+ |
| .NET Framework < 4.6.2 | .NET Framework 4.6.2 |
| .NET Standard 1.0 | .NET Standard 2.0 |
| UWP < 16299 | UWP 16299 |
| WinUI < 18362 | WinUI 18362 |

> **注意**：.NET 6、.NET 8 和 .NET 9 都受 MSTest v3 支持。不要更改已经受支持的 TFM。

### 步骤 5：解决构建错误和破坏性更改

首先搜索提供的文件并仅修复存在的破坏性更改。成功的构建并不能证明兼容性；一些错误仅在分析器警告或测试执行期间出现。

**断言重载**——MSTest v3 用泛型 `AreEqual<T>(T?, T?)` 替换了 `Assert.AreEqual(object, object)` 和 `AreNotEqual(object, object)`。这**仅**在 `T` 无法再推断时破坏，编译器报告为 `CS0411`（对于不相关的参数类型，报告为 `CS1503`）：

```csharp
// 破坏——string 和 int 没有共同的推断类型：
Assert.AreEqual(referenceCode, numericId);   // CS0411
// 修复——显式指定类型参数：
Assert.AreEqual<object>(referenceCode, numericId);
```

两个 `object`-类型的参数仍然推断 `T = object` 并编译不变，普通的类型断言如 `Assert.AreEqual("A-3", order.Reference)` 也相同。**仅修复编译器拒绝的调用**。将文件中的每个断言扩展到 `<object>` 也编译，因此没有任何东西会标记它——但这会丢弃 v3 添加的类型检查，而这正是此更改的整个目的。

**DataRow 严格类型匹配**——参数类型必须与参数类型完全匹配。这**不是**编译错误：行构建（带有 `MSTEST0014`）并在运行时失败，提示“测试数据与方法参数不匹配”。

```csharp
// 运行时失败：1L（long）不能绑定到 int 参数 -> 使用 1
// 运行时失败：1.0（double）不能绑定到 float 参数 -> 使用 1.0f
// 仍然绑定：1（int）到 long 参数——接受扩展转换
```

除非独立错误，否则保留方法参数类型。`dotnet build` 可能成功带有 `MSTEST0014`；运行测试以证明每行绑定并执行。

**超过 16 个参数的行**——保留它们，除非编译器实际发出 `CS1729`。上限仅存在于 3.0.1/3.0.2（在 3.0.3 中移除），所以将多余的包装在 `object[]`、转换为 `object` 或拆分方法只是重写了一个正确的测试。

**超时行为**——在 .NET Core 和 .NET Framework 上统一。验证 `[Timeout]` 值是否仍然有效。

### 步骤 6：替换 .testsettings 为 .runsettings

`.testsettings` 文件和 `<LegacySettings>` 在 MSTest v3 中不再支持。**删除 `.testsettings` 文件**，创建 `.runsettings` 文件——不要保留两者。将所有 MSTest 配置合并到 `<MSTest>` 元素下；不要创建 `<MSTestV2>` 部分。

关键映射：

| .testsettings | .runsettings 等效 |
|---|---|
| `TestTimeout` 属性 | `<MSTest><TestTimeout>30000</TestTimeout></MSTest>` |
| 部署配置 | `<MSTest><DeploymentEnabled>true</DeploymentEnabled></MSTest>` 或删除 |
| 程序集解析设置 | 删除——在现代 .NET 中不需要 |
| 数据收集器 | `<DataCollectionRunSettings><DataCollectors>` 部分 |

> **重要**：将超时映射到 `<MSTest><TestTimeout>`（每个测试），**不要**映射到 `<TestSessionTimeout>`（会话级）。完全删除 `<LegacySettings>`。

更新每个项目、CI 命令或 IDE 设置，这些设置明确选择了旧的 `.testsettings` 路径，以选择新的 `.runsettings` 路径。当 VSTest 项目必须保留行为但从未选择过旧文件时，使用 `RunSettingsFilePath` 使新文件生效。对于 MTP，使用框架支持的 `--settings` 路径或现有的 MTP 配置，而不是假设 VSTest MSBuild 属性被认可。

### 步骤 7：验证

1. 运行用于基线的相同测试命令、过滤器和配置。`dotnet test` 默认构建；仅运行单独的构建以隔离编译失败。
2. 比较发现的、通过的、失败的和跳过的计数与迁移前的基线。
3. 调查每个计数差异；不要接受无声丢弃的测试或数据行。
4. 确认没有 QualityTools 引用、1.x/2.x MSTest 包、`.testsettings` 或 `<LegacySettings>` 剩余。

## 验证

- [ ] MSTest v3 包（或 MSTest.Sdk）正确引用；v1/v2 引用已删除
- [ ] 项目构建无错误
- [ ] 所有测试通过 (`dotnet test`) -- 将通过/失败计数与迁移前基线比较
- [ ] `.testsettings` 替换为 `.runsettings`（如果适用）

## 下一步

v3 迁移后，使用 `migrate-mstest-v3-to-v4` 迁移到 MSTest v4。

## 常见陷阱

| 陷阱 | 解决方案 |
|---------|----------|
| 在工作区已经包含项目时回复“哪个项目？” | 通配符搜索 `*.csproj`/`*.sln`/`*.slnx` 并读取存在的内容 |
| 搜索后立即报告项目文件，“磁盘上没有项目” | 路径被重建到技能的基础目录下。使用搜索返回的精确结果打开；永远不要构建一个替代项目 |
| 重写具有超过 16 个参数的 `DataRow` | 在 3.0.3+ 上有效，这是当前所有 3.x。只有 3.0.1/3.0.2 拒绝它 |
| 非 MSTest.Sdk VSTest 项目缺少 `Microsoft.NET.Test.Sdk` | 添加 VSTest 发现的包引用 |
| MSTest.Sdk v3 项目必须将其主要运行器设置为 VSTest | 设置 `<UseVSTest>true</UseVSTest>`；不要仅仅因为存在过渡性的 `vstest.console` 任务而切换运行器 |
