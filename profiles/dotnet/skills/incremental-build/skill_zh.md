## MSBuild 增量构建的工作原理

MSBuild 的增量构建机制允许在输出已更新的情况下跳过目标，从而在后续运行中显著减少构建时间。

- **具有 `Inputs` 和 `Outputs` 属性的目标**：MSBuild 会比较 `Inputs` 中列出的所有文件的最后修改时间与 `Outputs` 中列出的所有文件。如果每个输出文件都比每个输入文件更新，则完全跳过该目标。
- **没有 `Inputs`/`Outputs`**：每次构建调用时都会运行目标。这是默认行为，也是最常见导致增量构建缓慢的原因。
- **目标上的 `Incremental` 属性**：目标可以显式地选择启用或禁用增量行为。设置 `Incremental="false"` 会强制目标始终运行，即使指定了 `Inputs` 和 `Outputs`。
- **基于时间戳的比较**：MSBuild 使用文件系统时间戳（最后修改时间）来确定文件是否过时。它不使用内容哈希。这意味着修改文件（更新时间戳而不改变内容）将触发重新构建。

```xml
<!-- 此目标具有增量行为：如果输出比所有输入更新，则跳过 -->
<Target Name="Transform"
        Inputs="@(TransformFiles)"
        Outputs="@(TransformFiles->'$(OutputPath)%(Filename).out')">
  <!-- 工作内容 -->
</Target>

<!-- 此目标始终运行，因为它没有 Inputs/Outputs -->
<Target Name="PrintMessage">
  <Message Text="This runs every build" />
</Target>
```

## 增量构建为何失败（常见原因）

1. **自定义目标缺少 Inputs/Outputs** — 缺少这两个属性，目标将始终运行。这是导致不必要的重新构建的最常见原因。

2. **输出路径中的易变属性** — 如果输出路径包含在构建之间会变化的元素（例如时间戳、构建编号或随机 GUID），MSBuild 将永远不会找到以前的输出，并且将始终重新构建。

3. **在跟踪的 Outputs 之外写入文件** — 如果目标写入未列在其 `Outputs` 中的文件，MSBuild 将不知道这些文件。目标可能会被跳过（因为其声明的输出已更新），但下游目标仍可能被触发。

4. **缺少 FileWrites 注册** — 在构建期间创建但未在 `FileWrites` 项目组中注册的文件不会被 `dotnet clean` 清理。随着时间的推移，过时的文件可能会混淆增量检查。

5. **Glob 变化** — 当添加或删除源文件时，项目集（例如 `@(Compile)）会发生变化。由于这些项目会传递到 `Inputs`，输入集会发生变化并触发重新构建。这是预期行为，但可能会令人惊讶。

6. **属性变化** — 传递到 `Inputs` 或 `Outputs` 路径的属性（例如 `$(Configuration)`、`$(TargetFramework)）在更改时会触发重新构建。在 Debug 和 Release 之间切换按设计会进行完整重新构建。

7. **NuGet 包更新** — 更改包版本会更新 `project.assets.json` 并可能更新许多解析的程序集路径。这会更改 `ResolveAssemblyReferences` 和 `CoreCompile` 的输入，触发重新构建。

8. **构建服务器 VBCSCompiler 缓存失效** — Roslyn 编译器服务器（`VBCSCompiler`）缓存了编译状态。如果服务器被回收（超时、崩溃或手动杀死），下一个构建可能会变慢，即使 MSBuild 的增量检查通过，因为编译器必须重新填充其内存缓存。

## 诊断“为何重新构建？”

使用二进制日志（binlogs）来了解目标为何运行而不是被跳过的原因。

### 使用 binlog 的分步方法

1. **使用 binlogs 构建两次** 以捕获增量构建行为：
   ```shell
   dotnet build /bl:first.binlog
   dotnet build /bl:second.binlog
   ```
   第一次构建建立基线。第二次构建是你希望进行增量构建的构建。分析 `second.binlog`。

### 主要：binlog MCP（首选）

使用 **binlog MCP 服务器**（`Microsoft.AITools.BinlogMcp`，在 `binlog` MCP 命名空间下提供）来分析第二个 binlog：

1. 使用概览工具检查整体构建状态和持续时间。
2. 使用搜索工具查找执行了哪些目标而哪些目标被跳过 — 搜索 "Building target completely"、"Building target incrementally"、"Skipping target"。
3. 使用搜索工具查找 "is newer than output" 消息，这些消息会揭示哪个输入文件触发了重新构建。
4. 使用与目标相关的工具（target_reasons、project_targets）来检查特定目标为何运行。
5. 使用 expensive_targets 工具查找第二次构建中消耗时间最多的目标 — 这些是你的优化目标。

### 备用：文本日志重放（当 MCP 不可用时）

2. **重放第二个 binlog** 到一个诊断文本日志：
   ```shell
   dotnet msbuild second.binlog -noconlog -fl -flp:v=diag;logfile=second-full.log;performancesummary
   ```
   然后搜索实际执行了哪些目标：
   ```bash
   grep 'Building target\|Target.*was not skipped' second-full.log
   ```
   在完美的增量构建中，大多数目标应该被跳过。

3. **通过在诊断日志中查找其执行消息来检查未跳过的目标**。查找 "out of date" 消息，这些消息会指示目标为何运行。

4. **在 binlog 中查找关键消息**：
   - `"Building target 'X' completely"` — 意味着 MSBuild 没有找到输出或所有输出都丢失；这是完整的目标执行。
   - `"Building target 'X' incrementally"` — 意味着某些（但不是所有）输出已过时。
   - `"Skipping target 'X' because all output files are up-to-date"` — 目标被正确跳过。

5. **搜索 "is newer than output"** 消息以找到触发重新构建的特定输入文件：
   ```bash
   grep "is newer than output" second-full.log
   ```
   这会揭示哪个输入文件的时间戳导致 MSBuild 认为目标过时。

### 其他诊断技术

- 在 MSBuild 结构化日志查看器中并排比较 `first.binlog` 和 `second.binlog` 以查看发生了什么变化。
- 使用 `grep 'Target Performance Summary' -A 30 second-full.log` 来查看第二次构建中消耗时间最多的目标 — 这些是你的优化目标。
- 检查运行了但持续时间为零的目标 — 它们可能有不必要的依赖项导致它们执行。

## FileWrites 和清理构建

`FileWrites` 项目组是 MSBuild 跟踪构建期间生成的文件的机制。它为 `dotnet clean` 提供支持，并有助于保持正确的增量行为。

- **`FileWrites` 项目**：注册自定义目标创建的任何文件，以便 `dotnet clean` 知道要删除它们。没有这个，生成的文件会跨构建累积，并可能混淆增量检查。
- **`FileWritesShareable` 项目**：用于跨多个项目共享的文件（例如共享生成的代码）。这些文件会被跟踪，但如果其他项目仍然引用它们，则不会被删除。
- **如果未注册**：文件会累积在输出和中间目录中。`dotnet clean` 不会删除它们，并且它们可能会导致过时数据问题或混淆最新检查。

### 注册生成文件的模式

在创建它们的目标内部将生成文件添加到 `FileWrites`：

```xml
<Target Name="MyGenerator" Inputs="..." Outputs="$(IntermediateOutputPath)generated.cs">
  <!-- 生成文件 -->
  <WriteLinesToFile File="$(IntermediateOutputPath)generated.cs" Lines="@(GeneratedLines)" />

  <!-- 注册用于清理 -->
  <ItemGroup>
    <FileWrites Include="$(IntermediateOutputPath)generated.cs" />
  </ItemGroup>
</Target>
```

## Visual Studio 快速最新检查

Visual Studio 有自己的最新检查（快速最新检查，或 FUTDC）与 MSBuild 的 `Inputs`/`Outputs` 机制分离。理解差异对于诊断“在 VS 中重新构建但在命令行中不重新构建”问题至关重要。

- **VS FUTDC 更快**，因为它在进程内运行，并且不调用 MSBuild 就检查已知的项目集。它比较已知项目类型（Compile、Content、EmbeddedResource 等）的时间戳与项目的主要输出。
- **它可能会出错**，如果您的项目使用自定义构建动作、生成文件的自定义目标或 FUTDC 不了解的非标准项目类型。
- **禁用 FUTDC** 以强制 Visual Studio 使用 MSBuild 的完整增量检查：
  ```xml
  <PropertyGroup>
    <DisableFastUpToDateCheck>true</DisableFastUpToDateCheck>
  </PropertyGroup>
  ```
- **诊断 FUTDC 决策**：通过在 VS 的输出窗口中查看：转到 **工具 → 选项 → 项目和解决方案 → SDK-Style Projects**，并将 **Up-to-date Checks** 日志级别设置为 **Verbose** 或更高。FUTDC 将记录它认为过时的文件。
- **常见的 VS FUTDC 问题**：
  - 未在 FUTDC 系统中注册的自定义构建动作
  - `CopyToOutputDirectory` 项目比上次构建更新
  - FUTDC 不会评估的由目标动态添加的项目
  - `Content` 或 `None` 项目具有 `CopyToOutputDirectory="PreserveNewest"` 且已修改

## 使自定义目标增量

以下是一个结构良好的增量自定义目标的完整示例：

```xml
<Target Name="GenerateConfig"
        Inputs="$(MSBuildProjectFile);@(ConfigInput)"
        Outputs="$(IntermediateOutputPath)config.generated.cs"
        BeforeTargets="CoreCompile">
  <!-- 仅在输入更改时生成文件 -->
  <WriteLinesToFile File="$(IntermediateOutputPath)config.generated.cs" Lines="..." />
  <ItemGroup>
    <FileWrites Include="$(IntermediateOutputPath)config.generated.cs" />
    <Compile Include="$(IntermediateOutputPath)config.generated.cs" />
  </ItemGroup>
</Target>
```

**此示例中的关键点**：

- **`Inputs` 包括 `$(MSBuildProjectFile)`**：这确保如果项目文件本身发生变化（例如，修改了影响生成的属性），目标会重新运行。
- **`Inputs` 包括 `@(ConfigInput)`**：实际驱动生成的源文件。
- **`Outputs` 使用 `$(IntermediateOutputPath)`**：生成的文件位于 `obj/` 目录中，由 MSBuild 的清理基础设施管理，并且会自动清理。
- **`BeforeTargets="CoreCompile"`**：生成的文件在编译器运行之前可用。
- **`FileWrites` 注册**：确保 `dotnet clean` 删除生成的文件，并防止过时文件累积。
- **`Compile` 包含**：将生成的文件添加到编译，而无需它在评估时存在。

### 要避免的常见错误

```xml
<!-- BAD：没有 Inputs/Outputs — 每次构建都会运行 -->
<Target Name="BadTarget" BeforeTargets="CoreCompile">
  <Exec Command="generate-code.exe" />
</Target>

<!-- BAD：易变输出路径 — 永远找不到以前的输出 -->
<Target Name="BadTarget2"
        Inputs="@(Compile)"
        Outputs="$(OutputPath)gen_$([System.DateTime]::Now.Ticks).cs">
  <Exec Command="generate-code.exe" />
</Target>

<!-- GOOD：稳定路径，注册的输出 -->
<Target Name="GoodTarget"
        Inputs="@(Compile)"
        Outputs="$(IntermediateOutputPath)generated.cs"
        BeforeTargets="CoreCompile">
  <Exec Command="generate-code.exe -o $(IntermediateOutputPath)generated.cs" />
  <ItemGroup>
    <FileWrites Include="$(IntermediateOutputPath)generated.cs" />
    <Compile Include="$(IntermediateOutputPath)generated.cs" />
  </ItemGroup>
</Target>
```

## 性能摘要和预处理

MSBuild 提供内置工具来了解正在运行什么以及为何运行。

- **`/clp:PerformanceSummary`** — 在构建结束时附加摘要，显示在每个目标和任务上花费的时间。使用此工具可以快速识别最昂贵的操作：
  ```shell
  dotnet build /clp:PerformanceSummary
  ```
  这显示了按累积时间排序的目标表，可以轻松发现不应在增量构建中运行的目标。

- **`/pp:preprocess.xml`** — 生成一个包含所有导入的 XML 文件，显示完全评估的项目。这对于了解定义了哪些目标、属性和项目以及它们来自哪里非常有价值：
  ```shell
  dotnet msbuild /pp:preprocess.xml
  ```
  在预处理输出中搜索，以查找任何目标的 `Inputs` 和 `Outputs` 的定义，或了解完整的导入链。

- 使用这两个工具一起了解正在运行什么（`PerformanceSummary`）和导入什么（`/pp`），然后与 binlog 分析交叉引用，以获得完整图景。

## 常见修复方法

- **始终为自定义目标添加 `Inputs` 和 `Outputs`** — 这是影响增量构建性能的最具影响力的更改。没有这两个属性，目标每次都会运行。
- **使用 `$(IntermediateOutputPath)` 为生成文件** — `obj/` 中的文件由 MSBuild 的清理基础设施跟踪，并且不会在配置之间泄漏。
- **在 `FileWrites` 中注册生成文件** — 确保 `dotnet clean` 删除它们，并防止过时文件累积。
- **避免构建中的易变数据** — 不要在文件路径或生成内容中嵌入时间戳、随机值或构建计数器，除非你有明确的策略来管理过时性。如果你必须使用易变数据，将其隔离到对下游影响最小的单个文件中。
- **使用 `Returns` 而不是 `Outputs`，当你需要传递项目而不影响增量构建依赖项时** — `Outputs` 具有双重作用：它定义增量检查，并且是目标返回的值。如果你只需要将项目传递给调用目标而不影响增量性，请使用 `Returns` 而不是 `Outputs`：
  ```xml
  <!-- Outputs：影响增量检查 AND 返回值 -->
  <Target Name="GetFiles" Outputs="@(DiscoveredFiles)">...</Target>

  <!-- Returns：仅影响返回值，不影响增量检查 -->
  <Target Name="GetFiles" Returns="@(DiscoveredFiles)">...</Target>
  ```
