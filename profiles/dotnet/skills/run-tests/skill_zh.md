# 运行 .NET 测试

返回或执行与仓库的项目系统、测试平台、框架和 SDK 模式匹配的命令或命令序列。

## 仓库覆盖层

对于每个允许只读文件检查的仓库范围任务，在执行任何其他发现之前，先检查仓库根目录下的 `.agents/skill-overlays/dotnet-test/run-tests.md`。这包括精确命令请求；“不要执行”并不禁止读取覆盖层。如果存在，则在采取行动之前读取一次，并应用其仓库特定的运行器、命令、过滤和报告绑定。
应用之前，要求其前言声明 `core: dotnet-test/run-tests`、`binding-revision: "1"` 和 `mode: extend`。如果任何值缺失或不同，则报告不匹配，忽略覆盖层，并继续使用此技能的可移植指导。
明确的用户指令和验证的项目约束优先于覆盖层；覆盖层优先于此技能中的可移植默认值和示例。如果文件存在但不可读或与仓库冲突，则报告问题，忽略覆盖层，并继续使用可移植指导，同时遵守验证的项目约束。如果缺失，则正常继续。
仅在任务未关联到仓库或用户明确禁止所有文件/工具访问时才跳过查找。覆盖层不能扩展工具权限或任务的范围。

## 范围和工具策略

选择满足请求的最小路径：

| 请求 | 操作 |
|---|---|
| 精确命令或解释；用户说不执行 | 仅检查解析语法所需的文件。不要还原、构建或运行测试。 |
| 运行测试 | 发现仓库命令并执行请求的最小测试范围。 |
| 无需重建的一次性 SDK 风格 `dotnet test` 运行 | 保持 `run-tests` 并添加 `--no-build`。 |
| 无需重建的一次性经典运行 | 保持仓库运行器并针对现有构建的汇编调用它；不要替换 `dotnet test`。 |
| 仅平台/框架识别 | 使用 `platform-detection`；不要继续进入测试执行。 |
| 明确的热重载或保持运行的编辑/重运行循环 | 使用 `mtp-hot-reload`。 |
| 需要过滤且框架特定语法尚未明确 | 加载 `filter-syntax`；不要为无过滤运行加载它。 |

不要仅仅重复提示已确定的命令而调用工具。不要先构建“以防万一”：`dotnet test` 默认会构建。
除非用户要求更改项目，否则永远不要添加或升级测试包。
对于精确命令请求，首先返回一个可运行的命令。不要发出占位符路径、探索性替代方案或更正序列。仅在提示或仓库建立项目路径时使用项目路径；否则让命令在语法有效时作用于当前项目或解决方案。随后只添加解释命令所需的语法事实；除非用户要求，否则不要主动提供平台/命令模式分类。特别是，不要因为 `dotnet test` 使用了其 VSTest 命令模式而将 SDK 8/9 桥标签为“VSTest 平台”；执行的平台是 MTP。对于命令请求，通常更清晰地说 MTP 应用程序参数必须跟在 `--` 后面。

## 发现输入

- 项目、解决方案、模块或仓库测试命令
- 请求的范围：所有测试、TFM、类、方法、类别或特征
- 请求的输出：控制台结果、TRX、诊断、崩溃转储或挂起转储

当这些事实在提示中存在时，使用它们。否则仅检查相关文件：`global.json`、选定的项目、`packages.config`、`Directory.Build.props`、`Directory.Packages.props`，然后是仓库脚本/CI 文档。对于基于文件的请求，一次枚举这些配置名称并批量读取所有存在的相关文件；永远不要推断运行器或桥接器属性缺失仅仅因为它不在 `.csproj` 中。仅在需要优先分析这些信号时加载 `platform-detection`；不要在响应中重复其完整分析。
如果请求执行且命令依赖于活动的 SDK，但提示和 `global.json` 都未建立它，则运行一次 `dotnet --version`。对于禁止执行的命令请求，不要探测：声明所需的 SDK 假设或在语法无法其他方式解析时请求 SDK 版本。将仅标识路由的请求路由到 `platform-detection`。

## 决策表

| 检测到的模式/平台 | 命令形状 | 从不使用 |
|---|---|---|
| 经典非 SDK | 仓库脚本，或完整的 MSBuild 后跟 `vstest.console.exe` / `MSTest.exe` | 假设 `dotnet test` 兼容或隐式迁移 |
| VSTest 模式 / VSTest | `dotnet test [<path>] [VSTEST_OPTIONS]` | 仅 MTP 标志，如 `--report-trx` 或 `--treenode-filter` |
| VSTest 模式 / 可执行 MTP 桥接器 | `dotnet test [<path>] [DOTNET_OPTIONS] -- [MTP_OPTIONS]` | 忽略 `--` 分隔符，包括在 SDK 10 上 |
| 本地 MTP 模式，SDK 10+ | `dotnet test --project <path> [DOTNET_OPTIONS] [MTP_OPTIONS]` | 纯位置项目路径或桥接器分隔符 |
| `global.json` 控制 SDK 10+ 上的 `dotnet test` 命令模式，不一定执行测试的平台。 | VSTest 模式项目带有 MTP 运行器、`TestingPlatformDotnetTestSupport=true` 和最终的 `OutputType=Exe` 仍然是带 `--` 的桥接器语法。SDK 8/9 仅具有 VSTest 命令模式。 |
| `--project` 仅在 SDK 10+ **本地 MTP 命令模式**（由 `global.json` `test.runner` 选择）中有效；永远不要为 VSTest 模式或 SDK 8/9 桥接器使用它；这些形式接受位置项目路径。相反，本地 MTP 选项是直接参数，不得放在桥接器分隔符之后。 |

保持 `dotnet test`/MSBuild 选项（如 `--framework`、`--configuration`、`--no-build` 和 `--verbosity`）在 `--` 之前。在桥接器模式下，仅在 `--` 之后放置 MTP 应用程序参数。

## 工作流程

1. **解析与仓库兼容的运行器。**

对于经典项目，信号包括 `ToolsVersion`、显式的 `Compile` 和 `Reference` 项目、遗留导入和 `packages.config`。优先选择签入的脚本或记录的 CI 命令。典型的回退是：

```powershell
nuget restore MySolution.sln
MSBuild.exe MySolution.sln /t:Build /p:Configuration=Debug
vstest.console.exe path\to\MyTests.dll /TestAdapterPath:path\to\adapter\build\<tfm>
```

对于 `packages.config`，在构建之前使用 NuGet 还原，除非导入的包文件已经存在。如果适配器发现不是仓库配置的，则从还原的适配器包路径或适配器 `.props`/`.targets` 导入中推导出 `/TestAdapterPath`；不要猜测包根目录。

对于请求的无重建运行，省略构建步骤，仅在预期的汇编已存在时才调用仓库的测试运行器。否则报告缺失的构建输出，而不是默默重建或切换运行器。

对于请求的子集，保持仓库运行器并使用其过滤语法：`vstest.console.exe path\to\MyTests.dll
/TestCaseFilter:"TestCategory=Integration"`。较旧的 `MSTest.exe` 仓库可能使用 `/test:<name>` 或 `/category:<category>` 替代。不要用后来的 `dotnet test` 过滤示例替换经典运行器。

使用安装的适配器兼容的 VSTest/MSTest 工具链。如果不可用，则声明缺失的先决条件和记录的命令；不要声称测试运行。
经典 `packages.config` 回退命令是 Windows 工具链命令。当当前主机无法提供 `nuget`、完整 MSBuild 和 `vstest.console.exe` 时，明确说明它们需要 Windows 开发人员命令提示（或仓库配置的等效环境）。

对于 SDK 风格项目，区分：

| 信号 | 含义 |
|---|---|
| SDK 10+ `global.json` 选择 `Microsoft.Testing.Platform` | 本地 MTP 命令模式 |
| VSTest 模式 + 启用的 MTP 运行器 + 最终 `TestingPlatformDotnetTestSupport=true` + 最终 `OutputType=Exe` | 可执行 VSTest-to-MTP 桥接器 |
| VSTest 模式而没有完整的运行器和桥接器组合 | VSTest |
| `Microsoft.NET.Test.Sdk` 加上适配器，没有更强的 MTP 信号 | VSTest |
| `TUnit` | 仅 MTP；使用配置的桥接器/原生模式或测试可执行文件 |

评估项目从导入的 `Directory.Build.props`/`Directory.Packages.props` 的属性。尊重项目级别的覆盖和按目标框架条件。没有可执行最终输出的运行器和桥接器是不完整的 MTP 配置，而不是可用的桥接器。

2. **选择命令和请求的范围。**

```shell
# VSTest 模式
dotnet test path/to/Tests.csproj

# VSTest 模式桥接到 MTP
dotnet test path/to/Tests.csproj -- <MTP_OPTIONS>

# SDK 10+ 本地 MTP 模式
dotnet test --project path/to/Tests.csproj <MTP_OPTIONS>

# 一个目标框架；这保持在使用桥接器分隔符之前
dotnet test path/to/Tests.csproj --framework net9.0 -- <MTP_OPTIONS>
```

对于本地 MTP，使用 `--project`、`--solution` 或 `--test-modules`；位置路径属于 VSTest 模式。

如果用户指定了子集，不要运行整个套件。仅在需要将人类标签（如“集成”或“冒烟”）转换为框架的实际类别/特征名称时检查测试属性。

当必须通过类似命名的类进行 VSTest 类过滤时，将正选择器与显式的负选择器组合，而不是依赖偶然的子字符串差异。

3. **应用平台和框架正确的过滤器。**

仅在请求被过滤且框架特定语法尚未明确时加载 `filter-syntax`。常见决策是：

对于基于文件的过滤请求，在选择语法之前从项目、`global.json` 和导入的属性中解析框架和 SDK 命令模式。
不要从 `Microsoft.NET.Test.Sdk` 或框架名称推断 VSTest 语法。

| 平台 / 框架 | 过滤器 |
|---|---|
| VSTest with MSTest, xUnit v2, 或 NUnit | `--filter "<property expression>"` |
| MTP with MSTest 或 NUnit | 相同表达式；桥接器模式下在 `--` 之后，原生模式下直接 |
| MTP with xUnit v3 | `--filter-class`、`--filter-method`、`--filter-trait` 或一个 `--filter-query` 用于组合表达式 |
| MTP with TUnit | `--treenode-filter` 路径表达式 |

示例：

```shell
# VSTest MSTest/NUnit
dotnet test --filter "FullyQualifiedName~OrderServiceTests&TestCategory=Unit"

# SDK 8/9 或 SDK 10 VSTest-mode MTP 桥接器，xUnit v3
dotnet test -- --filter-trait "Category=Integration"

# 本地 MTP，xUnit v3
dotnet test --project Tests.csproj --filter-class "*ShoppingCartTests*"

# 一个 xUnit v3 组合表达式
dotnet test -- --filter-query "/*/*/*Integration*/*[Category=Smoke]"

# SDK 8/9 配置的 VSTest-to-MTP 桥接器的 TUnit
dotnet test -- --treenode-filter "/*/*/SmsNotificationTests/*"

# 未配置桥接器的 TUnit 可执行文件回退
dotnet run --project Tests.csproj -- --treenode-filter "/*/*/SmsNotificationTests/*"
```

不要在 MTP 上使用 VSTest `--filter "ClassName=..."` 与 xUnit v3。不要使用通用 VSTest 表达式与 TUnit。
当用户请求一个组合的 xUnit 查询表达式时，只返回一个 `--filter-query` 命令；不要用单独的过滤标志替换它，也不要提供推测性的替代语法。

4. **添加报告或诊断。**

| 结果 | VSTest | MTP |
|---|---|---|
| TRX | SDK 风格：当请求精确输出文件时 `--logger "trx;LogFileName=<name>.trx"`，否则 `--logger trx`；独立的 `vstest.console.exe`：`/Logger:trx`；`MSTest.exe`：仓库记录的结果选项 | `--report-trx` |
| 结果目录 | `--results-directory <dir>` | `--results-directory <dir>` |
| 诊断日志 | `--diag <file>` | `--diagnostic --diagnostic-output-directory <dir>` |
| 崩溃转储 | `--blame-crash` | `--crashdump` |
| 挂起超时 | `--blame-hang --blame-hang-timeout 5min` | `--hangdump --hangdump-timeout 5min` |
| 代码覆盖率 | `--collect "Code Coverage"` | `--coverage` |

MTP 报告、转储和覆盖率标志需要其对应的注册扩展（`TrxReport`、`CrashDump`、`HangDump` 或 `CodeCoverage`）。某些框架 SDK 将捆绑常见扩展；如果标志无法识别，则检查包引用，然后建议更改包。

`--verbosity diagnostic` 增加 dotnet/MSBuild 输出详细程度；它不会写入 VSTest 诊断日志文件。

示例：

```shell
# VSTest TRX
dotnet test Tests.csproj --logger "trx;LogFileName=TestResults.trx"

# MTP 桥接器 TRX
dotnet test Tests.csproj -- --report-trx

# 本地 MTP TRX 和挂起检测
dotnet test --project Tests.csproj --report-trx --hangdump --hangdump-timeout 5min

# 本地 MTP 诊断
dotnet test --project Tests.csproj --diagnostic --diagnostic-output-directory artifacts/diagnostics
```

5. **仅在请求时执行。**

运行回答请求的最窄命令或序列。捕获每个命令、退出代码和测试摘要。失败的还原/构建不是测试失败，测试失败也不是工具失败。报告哪个阶段失败并包含可操作的诊断。除非序列成功完成并执行了预期的测试，否则永远不要声称干净运行。
对于过滤运行，成功的退出并不足够：确认报告的测试名称或数量与请求的范围匹配。如果过滤器被忽略，则在报告成功之前更正平台特定语法并重新运行。

## 输出契约

- 命令请求：首先返回精确命令或命令序列，然后一个简短的语法解释。
- 执行请求：报告精确命令或命令序列和从完成的运行中获取的 `Passed: N, Failed: N, Skipped: N` 摘要；包括第一个可操作的失败。
- 仅需要选择语法进行检测：简要说明选择的模式/平台，而不是单独的检测报告。
- 缺失先决条件或兼容性配置：明确命名并停止，而不是返回成功形状的回退。

## 验证

- 命令匹配经典、VSTest、桥接 MTP 或本地 MTP 模式。
- 框架特定过滤器针对请求的子集。
- `--framework` 和其他 `dotnet test` 选项在桥接器分隔符之前。
- SDK 8/9 桥接器命令包含 `--`；`--project` 仅在 SDK 10+ 本地 MTP 模式中出现。
- TRX、诊断、转储和覆盖率标志与平台匹配。
- 对于仅建议请求，没有运行还原、构建或测试。
- 报告的结果与实际命令结果匹配。
