---
name: check-bin-obj-clash
description: 检测存在冲突的 OutputPath 或 IntermediateOutputPath 的 MSBuild 项目。适用于：构建失败时出现“无法创建已存在的文件”、“进程无法访问正在被另一个进程使用的文件”、重试后成功的间歇性构建失败，或在多项目或多目标构建中 bin/obj（或 project.assets.json）冲突导致输出缺失或被覆盖的情况。常见原因：共享的 OutputPath、缺少 AppendTargetFrameworkToOutputPath、额外的全局属性（例如 PublishReadyToRun），或对单目标项目设置 ProjectReference 时的 SetTargetFramework。不适用于：与 MSBuild 无关的文件访问错误（如操作系统级锁定）、单项目单-TFM 构建、非 MSBuild 构建系统。
---

# 检测 OutputPath 和 IntermediateOutputPath 冲突

## 概述

这项技能有助于识别多个 MSBuild 项目评估共享相同的 `OutputPath` 或 `IntermediateOutputPath` 的情况。这是导致构建失败的常见原因，包括：

- 并行构建期间的文件访问冲突
- 输出文件丢失或被覆盖
- 间歇性构建失败
- "文件正在使用中" 错误
- **NuGet 还原错误，例如 `Cannot create a file when that file already exists`** - 这强烈表明多个项目共享相同的 `IntermediateOutputPath`，其中 `project.assets.json` 被写入

冲突可能发生在：

- **不同项目** 共享相同的输出目录
- **多目标构建**（例如 `TargetFrameworks=net8.0;net9.0`）其中路径不包含目标框架
- **多个解决方案构建** 其中同一个项目从不同的解决方案在单个构建中被构建

**注意：** 具有属性 `BuildProjectReferences=false` 的项目实例在分析冲突时应被**忽略** - 这些是 P2P 引用解析构建，它们仅查询元数据（通过 `GetTargetPath`）并且实际上不会写入输出目录。

## 何时使用此技能

**在看到以下情况时立即调用此技能：**
- NuGet 还原期间出现 `Cannot create a file when that file already exists` 错误
- `The process cannot access the file because it is being used by another process` 错误
- 间歇性构建失败但在重试时成功
- 输出文件丢失或意外覆盖

## 第 1 步：生成二进制日志

使用 `binlog-generation` 技能生成具有正确命名约定的二进制日志。

## 主要工作流 — binlog MCP

MCP 服务器提供了用于检查 `.binlog` 的结构化工具，而无需解析文本日志。直接调用它们，而不是将 binlog 重放为文本文件。如果您不确定哪些工具可用，请先调用 `tools/list`。

**重要约束：**
- `.binlog` 文件是**二进制格式** — 不要尝试 `cat`、`head`、`strings` 或直接读取它。仅使用 MCP 工具查询它。
- **边进行边综合分析结果。** 不要花费所有可用时间进行调查 — 一旦有足够的证据，就呈现您的结论。

### 第 2 步：获取概述并列出项目

使用 MCP 概述和项目工具来了解构建并列出所有参与的项目。

### 第 3 步：检查评估和全局属性

使用 MCP 的 `evaluations` 和 `evaluation_global_properties` 工具查找每个项目的所有评估。查找：

- 同一项目的多个评估（表明多目标或多个构建配置）
- 评估之间的全局属性差异（`TargetFramework`、`Configuration`、`RuntimeIdentifier`、`SolutionFileName`、`PublishReadyToRun` 等）

### 第 4 步：获取每个评估的输出路径

使用 MCP 属性工具查询每个项目评估的 `OutputPath`、`IntermediateOutputPath`、`BaseOutputPath` 和 `BaseIntermediateOutputPath`。

### 第 5 步：检查重复写入

如果可用，使用 MCP 的 `double_writes` 工具 — 它直接检测由多个项目实例写入的文件。

### 第 6 步：识别冲突

跨所有评估比较 `OutputPath` 和 `IntermediateOutputPath` 值：
1. **规范化路径** - 转换为绝对路径并规范化分隔符
2. **按路径分组** - 查找共享相同 OutputPath 或 IntermediateOutputPath 的评估
3. **过滤非构建评估** - 排除 `BuildProjectReferences=false` 实例（P2P 查询）
4. **报告冲突** - 任何包含超过一个评估的组都表示存在冲突

## 备用工作流 — 文本日志重放（当 MCP 不可用时）

仅在无法启动 MCP 服务器时使用此方法。

将 binlog 重放为诊断文本日志，然后使用 MCP 工具显示的相同信号进行 `grep`：

```bash
dotnet msbuild build.binlog -noconlog -fl -flp:v=diag;logfile=full.log
```

然后提取冲突信号：

- **项目 & 评估** — 列出评估开始并按项目计数：`grep 'Evaluation started' full.log | grep -oiE '"[^"]+\.[a-z]+proj"' | sort | uniq -c`。匹配完整的**引号路径**可以区分不同目录中同名的项目（并容忍路径中的空格）；路径计数 ≥ 2 表示评估了多次（多目标或额外的全局属性）。（`grep -c` 仅计算整个日志中的评估总数，因此无法揭示按项目重复的情况。）
- **输出路径** — `grep -iE 'OutputPath[[:space:]]*=|IntermediateOutputPath[[:space:]]*=|BaseOutputPath[[:space:]]*=|BaseIntermediateOutputPath[[:space:]]*=' full.log | sort -u`，或者直接查询项目：`dotnet msbuild MyProject.csproj -getProperty:OutputPath`（以及 `IntermediateOutputPath`、`BaseIntermediateOutputPath`）。
- **区分全局属性** — `grep -iE 'TargetFramework|Configuration|Platform|RuntimeIdentifier|SolutionFileName|PublishReadyToRun' full.log`。请参阅 [比较评估时的全局属性](#global-properties-to-check-when-comparing-evaluations) 表格，了解哪些属性影响路径，哪些属性仅分叉冗余实例。
- **佐证证据（可选）** — `grep 'Target "CopyFilesToOutputDirectory"' full.log` 加上 `grep 'SkipUnchangedFiles' full.log` 显示第二个实例写入（或跳过掩码写入）到相同路径；长与 ~0 ms 的 `CoreCompile` 区分实际构建与冗余实例。

**然后识别冲突：** 将路径规范化为绝对路径，按 `OutputPath` 和 `IntermediateOutputPath` 分组评估，并排除 `BuildProjectReferences=false`（P2P 查询） — 对于 `OutputPath` 仅，排除 `MSBuildRestoreSessionId` 还原评估。任何包含超过一个剩余评估的组都是冲突。

## 常见原因和修复方法

### 路径中缺少 TargetFramework 的多目标构建

**问题：** 项目使用 `TargetFrameworks` 但 OutputPath 没有因框架而变化。

```xml
<!-- BAD: 所有框架使用相同路径 -->
<OutputPath>bin\$(Configuration)\</OutputPath>
```

**修复：** 将 TargetFramework 包含在路径中：

```xml
<!-- GOOD: 路径因框架而变化 -->
<OutputPath>bin\$(Configuration)\$(TargetFramework)\</OutputPath>
```

或者依赖 SDK 默认值，它们会自动处理此问题：

```xml
<AppendTargetFrameworkToOutputPath>true</AppendTargetFrameworkToOutputPath>
<AppendTargetFrameworkToIntermediateOutputPath>true</AppendTargetFrameworkToIntermediateOutputPath>
```

### 项目间共享输出目录（使用 AppendTargetFramework 无法修复）

**问题：** 多个项目显式设置相同的 `BaseOutputPath` 或 `BaseIntermediateOutputPath`。

```xml
<!-- Project A - Directory.Build.props -->
<BaseOutputPath>..\SharedOutput\</BaseOutputPath>
<BaseIntermediateOutputPath>..\SharedObj\</BaseIntermediateOutputPath>

<!-- Project B - Directory.Build.props -->
<BaseOutputPath>..\SharedOutput\</BaseOutputPath>
<BaseIntermediateOutputPath>..\SharedObj\</BaseIntermediateOutputPath>
```

**重要：** 即使 `AppendTargetFrameworkToOutputPath=true`，这仍然会冲突！.NET 会将某些文件直接写入 `IntermediateOutputPath` 而不包含 TargetFramework 后缀，包括：

- `project.assets.json`（NuGet 还原输出）
- 其他 NuGet 相关文件

这会导致并行还原期间出现 `Cannot create a file when that file already exists` 错误。

**修复：** 每个项目必须具有唯一的 `BaseIntermediateOutputPath`。不要跨项目共享中间输出目录：

```xml
<!-- Project A -->
<BaseIntermediateOutputPath>..\obj\ProjectA\</BaseIntermediateOutputPath>

<!-- Project B -->
<BaseIntermediateOutputPath>..\obj\ProjectB\</BaseIntermediateOutputPath>
```

或者简单地使用 SDK 默认值，它们将 `obj` 放在每个项目目录内。

### RuntimeIdentifier 构建冲突

**问题：** 为多个 RID 构建而路径中不包含 RID。

**修复：** 确保 RuntimeIdentifier 在路径中：

```xml
<AppendRuntimeIdentifierToOutputPath>true</AppendRuntimeIdentifierToOutputPath>
```

### 多个解决方案构建同一个项目

**问题：** 单个构建调用多个解决方案（例如，通过 MSBuild 任务或命令行）其中包含相同的项目。每个解决方案构建独立评估和构建项目，具有不同的 `Solution*` 全局属性，这些属性不会影响输出路径。

**如何检测：** 比较同一项目的评估中的 `SolutionFileName` 和 `CurrentSolutionConfigurationContents`。不同的值表示多解决方案构建。例如：

| 属性 | 来自解决方案 A 的评估 | 来自解决方案 B 的评估 |
|---|---|---|
| `SolutionFileName` | `BuildAnalyzers.sln` | `Main.slnx` |
| `CurrentSolutionConfigurationContents` | 1 个项目条目 | ~49 个项目条目 |
| `OutputPath` | `bin\Release\netstandard2.0\` | `bin\Release\netstandard2.0\` ← **冲突** |

**示例：** 仓库构建脚本构建 `BuildAnalyzers.sln` 然后构建 `Main.slnx`，并且两个解决方案都包含 `SharedAnalyzers.csproj`。两个构建都写入 `bin\Release\netstandard2.0\`。第一个构建编译；第二个跳过编译但仍运行 `CopyFilesToOutputDirectory`。

**修复：** 选项包括：
1. **合并解决方案** - 确保每个项目在单个构建中仅从一个解决方案构建
2. **使用不同的配置** - 使用不同的 `Configuration` 值构建解决方案，以产生不同的输出路径
3. **排除重复项目** - 使用解决方案过滤器或条件项目包含来避免两次构建同一个项目

### 额外的全局属性创建冗余项目实例

**问题：** 由于额外的全局属性（例如 `PublishReadyToRun=false`）导致同一解决方案内项目被多次构建，这些属性创建不同的 MSBuild 项目实例。这些属性不会影响输出路径，但会阻止 MSBuild 跨实例缓存结果，导致冗余目标执行。

**如何检测：** 比较同一解决方案内同一项目的全局属性（相同的 `SolutionFileName`）。查找不同的属性但不会导致路径差异的属性：

| 属性 | 评估 A（来自 Razor.slnx） | 评估 B（来自 Razor.slnx） |
|---|---|---|
| `PublishReadyToRun` | *(未设置)* | `false` |
| `OutputPath` | `bin\Release\netstandard2.0\` | `bin\Release\netstandard2.0\` ← **冲突** |

对于项目中的额外属性没有效果（例如，`netstandard2.0` 类库上的 `PublishReadyToRun` 不使用 ReadyToRun 编译）的项目，这种情况尤其浪费。

**修复：** 选项包括：
1. **移除额外的全局属性** - 调查哪个父目标/任务注入了属性，并阻止它传递给不需要它的项目
2. **使用 `RemoveGlobalProperties` 元数据** - 在 `ProjectReference` 项目上使用 `RemoveGlobalProperties="PublishReadyToRun"` 在构建引用项目之前移除属性
3. **条件属性** - 仅对实际使用它的项目设置属性（例如，仅对可执行项目，而不是类库）

### 显式的 `<MSBuild>` 构建/发布带有额外全局属性（自身或跨项目）

**问题：** 目标使用 `<MSBuild>` 任务构建或发布项目带有额外全局属性，最常见的是“构建时发布”目标。违规调用可以在目标项目本身**或**在消耗它的另一个项目中（例如，测试或布局项目发布工具）：

```xml
<!-- (a) 同一项目（构建时发布） -->
<Target Name="PublishOnBuild" AfterTargets="Build">
  <MSBuild Projects="$(MSBuildProjectFullPath)" Targets="Publish" Properties="_IsPublishing=true" />
</Target>

<!-- (b) 项目 A 发布它消耗的项目 B -->
<MSBuild Projects="..\tool\tool.csproj" Targets="Publish" Properties="_IsPublishing=true" />
```

无论哪种方式，这都会分叉目标项目的不同实例（`path` + `{_IsPublishing=true}`），它共享与解决方案/图已构建的实例相同的 `OutputPath`/`IntermediateOutputPath`。两者都写入相同的文件 — 对于 NativeAOT 这包括 `*.sourcelink` 中间文件，这在并行构建下会导致 `SourceLinkWriter` / "文件正在使用中" 失败。

**如何检测：** 按照上述主要工作流进行 — `evaluations` 和 `evaluation_global_properties` 工具显示两个共享相同 `OutputPath`/`IntermediateOutputPath` 的目标项目评估，但仅通过 `_IsPublishing` 等路径中性发布标志（如 `_IsPublishing`）不同，并且 `double_writes` 工具直接标记生成的共享文件写入。要区分情况 (a) 和 (b)，请查看构建树中 `{_IsPublishing=true}` 评估运行*在*哪个项目下（从概述/项目工具）：目标项目本身为 (a)，或调用了 `<MSBuild>` 任务的消费者项目为 (b)。

**修复：** 取决于调用位置：

- **同一项目 (a)：** 您无法使用 `RemoveGlobalProperties` 移除属性（项目注入它给自己）。将标志设置为**静态**（非全局）属性，并通过 `DependsOnTargets`/`CallTarget` 在**相同**实例中运行目标，并防止发布作为入口点时的目标循环：

```xml
<PropertyGroup>
  <_PublishWasInvokedDirectly Condition="'$(_IsPublishing)' == 'true'">true</_PublishWasInvokedDirectly>
  <_IsPublishing>true</_IsPublishing>
</PropertyGroup>
<Target Name="PublishOnBuild"
        AfterTargets="Build"
        DependsOnTargets="Publish"
        Condition="'$(_PublishWasInvokedDirectly)' != 'true'" />
```

- **跨项目 (b)：** 消费者不得使用路径中性全局属性分叉生产者。让生产者在自己的构建中发布（*其*项目中的 (a) 修复），然后让消费者**顺序**它并读取其输出而不是重新发布它：

```xml
<ItemGroup>
  <ProjectReference Include="..\tool\tool.csproj" ReferenceOutputAssembly="false" />
</ItemGroup>
<!-- 消费者读取工具的发布目录；它不调用工具的 Publish -->
```

请参阅 `msbuild-antipatterns` 技能（AP-22）以了解编写时的气味和推理。

### `SetTargetFramework` 重新注入单目标项目自己的 TFM 到 `ProjectReference`

**问题：** `ProjectReference` 设置 `SetTargetFramework="TargetFramework=<tfm>"` 元数据指向一个**单目标**项目（使用单一的 `<TargetFramework>` 而不是 `<TargetFrameworks>`），其中注入的 `<tfm>` **等于**项目已经目标的 TFM。`SetTargetFramework` 将 `TargetFramework` 作为**全局属性**注入到引用项目的构建中。

```xml
<!-- BAD: Tool.csproj 单目标 net8.0，我们注入相同的 net8.0 -->
<ProjectReference Include="..\Tool\Tool.csproj" SetTargetFramework="TargetFramework=net8.0" />
```

注入项目已经目标的 TFM 是**路径中性的** — 项目已经解析到 `bin\<config>\net8.0\` 和 `obj\<config>\net8.0\`。因此它不会改变输出路径；它仅分叉一个不同的实例 `(project, {TargetFramework=net8.0})`。解决方案/图构建的是同一个项目 `(project, {})`。两者共享相同的 `OutputPath`/`IntermediateOutputPath`，因此同一个项目被**两次**构建到同一位置 — 并行构建下的 bin/obj 冲突。

**如何检测：** 按照上述主要工作流进行。`evaluations` 和 `evaluation_global_properties` 工具显示两个共享相同 `OutputPath`/`IntermediateOutputPath` 的引用项目评估，它们仅通过 `TargetFramework` 全局属性不同，而项目本身是单目标的（其自己的 `TargetFramework` 等于注入值）。`double_writes` 工具直接标记生成的共享文件写入。

**注意：** P2P 协议本身**不**为非多目标引用注入 `TargetFramework` — 冲突专门来自显式的 `SetTargetFramework` 元数据覆盖了安全默认值。

**修复：** 当 `SetTargetFramework` 仅重复项目自身的单一 TFM 时，移除冗余的 `SetTargetFramework`：

```xml
<!-- 良好 -->
<ProjectReference Include="..\Tool\Tool.csproj" />
```

**当 `SetTargetFramework` 合法（不冲突）时：**

- **多目标引用** — 被引用的项目使用 `<TargetFrameworks>`，而你需要特定的 TFM。每个 TFM 都有独特的输出路径，因此不会冲突。
- **覆盖为 *不同* TFM** — 你可以在单目标项目上使用 `SetTargetFramework`，使其在不同于其声明的 TFM 下构建。由于注入的 TFM 会改变输出路径 (`obj\<config>\<different-tfm>\`)，该实例不再与 `(项目, {})` 冲突。只有 *相同-TFM* 的情况是路径中性的且会冲突。
- **框架不兼容引用** — 每当引用项目和被引用项目目标 **不兼容的框架**（例如，一个 `.NETFramework` 项目引用一个 `.NETCoreApp` 项目，反之亦然）— **无论单目标或多目标** — 设置 `SkipGetTargetFrameworkProperties="true"`（否则 P2P `GetTargetFrameworkProperties` 协商会失败）和 `ReferenceOutputAssembly="false"`（为不兼容框架构建的程序集不能作为引用使用 — 你只想触发/序列构建）：

  ```xml
  <ProjectReference Include="..\Tool\Tool.csproj"
                    SkipGetTargetFrameworkProperties="true"
                    ReferenceOutputAssembly="false" />
  ```

  使用 `SkipGetTargetFrameworkProperties="true"`，协商不再阻止**引用**项目的自身 `TargetFramework` 全局属性（在构建特定 TFM 时存在，例如它是多目标的）流入被引用项目。对于**单目标**的被引用项目，这会强制它使用错误的 TFM / 输出路径。通过设置 `SetTargetFramework="TargetFramework=<tfm>"`（固定 TFM）**或** `UndefineProperties="TargetFramework"`（移除继承的全局属性，使项目按其声明构建）来阻止这种情况 — 选择其一，不要同时使用：

  ```xml
  <ProjectReference Include="..\Tool\Tool.csproj"
                    SkipGetTargetFrameworkProperties="true"
                    UndefineProperties="TargetFramework"
                    ReferenceOutputAssembly="false" />
  ```

参考 `msbuild-antipatterns` 技能（AP-23）了解编写时的异味和原因。

## 小贴士

- SDK 默认路径包含 `$(TargetFramework)` — 当项目覆盖这些默认值时，冲突经常发生；在比较前将相对路径规范化为绝对路径。
- **跨项目的 `IntermediateOutputPath` 冲突不能通过 `AppendTargetFrameworkToOutputPath` 修复** — 类似 `project.assets.json` 的文件直接写入中间路径。对于同一项目内的多目标冲突，`AppendTargetFrameworkToOutputPath=true` 是正确的修复方法。
- 指示路径冲突的错误消息：`Cannot create a file when that file already exists`（NuGet 还原）、`The process cannot access the file because it is being used by another process`，或重试时成功的间歇性失败。

### 比较评估时需要检查的全局属性

当多个评估共享输出路径时，比较这些全局属性以了解原因：

| 属性 | 影响输出路径？ | 备注 |
|------|----------------|-------|
| `TargetFramework` | 是 | 不同 TFM 应该有不同路径。**例外：** 重新注入 *单目标* 项目的自身 TFM（例如，通过 `SetTargetFramework` 使用相同值）是路径中性的 — 它分叉一个冗余实例共享输出路径（见 "`SetTargetFramework` 重新注入...`"） |
| `RuntimeIdentifier` | 是 | 不同 RID 应该有不同路径 |
| `Configuration` | 是 | Debug vs Release |
| `Platform` | 是 | AnyCPU vs x64 等 |
| `SolutionFileName` | 否 | 标识构建项目的解决方案 — 不同值表示多解决方案冲突 |
| `SolutionName` | 否 | 解决方案名称（不含扩展名） |
| `SolutionPath` | 否 | 解决方案文件的完整路径 |
| `SolutionDir` | 否 | 包含解决方案文件的目录 |
| `CurrentSolutionConfigurationContents` | 否 | 包含项目条目的 XML — 条目数量揭示解决方案 |
| `BuildProjectReferences` | 否 | `false` = P2P 查询，不是实际构建 - 忽略这些 |
| `MSBuildRestoreSessionId` | 否 | 存在 = 还原阶段评估 |
| `PublishReadyToRun` | 否 | 发布设置，不会改变构建输出路径，但会创建独特的项目实例 |
| `_IsPublishing` | 否 | 发布标志；带有此设置的 `<MSBuild>` Build/Publish 调用（在此项目或另一个消耗它的项目中）分叉一个共享构建输出路径的发布实例（见 "显式的 `<MSBuild>` Build/Publish 带有额外全局属性"） |

## 测试修复

修复路径冲突后，进行清理和重建以验证。参考 `binlog-generation` 技能的 "清理仓库" 部分了解如何清理仓库同时保留 binlog 文件。
