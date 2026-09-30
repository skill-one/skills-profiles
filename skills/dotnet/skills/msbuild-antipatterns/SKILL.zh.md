---
name: msbuild-antipatterns
description: 检测并修复项目及构建文件中的 MSBuild 反模式。在以下情况下使用：被要求评审、审计、格式化、清理或代码审查 .csproj/.vbproj/.fsproj/.props/.targets/.proj（或 Directory.Build.props/.targets）文件，当被问及“这个项目文件是否正确？”或“我的构建文件有什么问题？”时，或当追踪由项目编写方式引起的微妙构建错误时。每个反模式都包含一个症状和一个具体的 BAD→GOOD 修复方案。不适用于：非 MSBuild 构建系统（npm、Maven、CMake），或迁移项目到 SDK 风格（请使用 msbuild-modernization）。
---

# MSBuild 反模式目录

一个编号的常见 MSBuild 反模式目录。每个条目遵循以下格式：

- **气味**：要查找的内容
- **为什么不好**：对构建、可维护性或正确性的影响
- **修复**：具体的转换

在扫描项目文件以查找改进时使用此目录。

---

## AP-01：用于具有内置任务的操作 `<Exec>`

**气味**：`<Exec Command="mkdir ..." />`，`<Exec Command="copy ..." />`，`<Exec Command="del ..." />`

**为什么不好**：内置任务跨平台、支持增量构建、发出结构化日志记录并一致地处理错误。`<Exec>` 对 MSBuild 是不透明的。

```xml
<!-- BAD -->
<Target Name="PrepareOutput">
  <Exec Command="mkdir $(OutputPath)logs" />
  <Exec Command="copy config.json $(OutputPath)" />
  <Exec Command="del $(IntermediateOutputPath)*.tmp" />
</Target>

<!-- GOOD -->
<Target Name="PrepareOutput">
  <MakeDir Directories="$(OutputPath)logs" />
  <Copy SourceFiles="config.json" DestinationFolder="$(OutputPath)" />
  <Delete Files="@(TempFiles)" />
</Target>
```

**内置任务替代方案**：

| Shell 命令 | MSBuild 任务 |
|--------------|--------------|
| `mkdir` | `<MakeDir>` |
| `copy` / `cp` | `<Copy>` |
| `del` / `rm` | `<Delete>` |
| `move` / `mv` | `<Move>` |
| `echo text > file` | `<WriteLinesToFile>` |
| `touch` | `<Touch>` |
| `xcopy /s` | `<Copy>` 使用项模式 |

---

## AP-02：未加引号的条件表达式

**气味**：`Condition="$(Foo) == Bar"` — 比较的两侧都没有加引号。

**为什么不好**：如果属性为空或包含空格/特殊字符，条件将评估不正确或抛出解析错误。MSBuild 要求使用单引号字符串进行可靠的比较。

```xml
<!-- BAD -->
<PropertyGroup Condition="$(Configuration) == Release">
  <Optimize>true</Optimize>
</PropertyGroup>

<!-- GOOD -->
<PropertyGroup Condition="'$(Configuration)' == 'Release'">
  <Optimize>true</Optimize>
</PropertyGroup>
```

**规则**：始终用单引号将 `==` 和 `!=` 比较的**两侧**括起来。

---

## AP-03：硬编码的绝对路径

**气味**：项目文件中包含 `C:\tools\`、`D:\packages\`、`/usr/local/bin/` 等路径。

**为什么不好**：在其他机器上、CI 环境或其他操作系统上会中断。不可移动。

```xml
<!-- BAD -->
<PropertyGroup>
  <ToolPath>C:\tools\mytool\mytool.exe</ToolPath>
</PropertyGroup>
<Import Project="C:\repos\shared\common.props" />

<!-- GOOD -->
<PropertyGroup>
  <ToolPath>$(MSBuildThisFileDirectory)tools\mytool\mytool.exe</ToolPath>
</PropertyGroup>
<Import Project="$(RepoRoot)eng\common.props" />
```

**首选路径属性**：

| 属性 | 含义 |
|----------|---------|
| `$(MSBuildThisFileDirectory)` | 当前 .props/.targets 文件的目录 |
| `$(MSBuildProjectDirectory)` | .csproj 的目录 |
| `$([MSBuild]::GetDirectoryNameOfFileAbove(...))` | 向上查找标记文件 |
| `$([MSBuild]::NormalizePath(...))` | 合并和规范化路径段 |

---

## AP-04：重申 SDK 默认值

**气味**：属性设置为 .NET SDK 已经默认提供的值。

**为什么不好**：增加噪音，隐藏有意覆盖，并使识别实际自定义内容变得更加困难。当新 SDK 中的默认值发生变化时，冗余属性可能会无声地锁定旧行为。

```xml
<!-- BAD: 所有这些都已经是默认值 -->
<PropertyGroup>
  <OutputType>Library</OutputType>
  <EnableDefaultItems>true</EnableDefaultItems>
  <EnableDefaultCompileItems>true</EnableDefaultCompileItems>
  <RootNamespace>MyLib</RootNamespace>       <!-- 与项目名称匹配 -->
  <AssemblyName>MyLib</AssemblyName>         <!-- 与项目名称匹配 -->
  <AppendTargetFrameworkToOutputPath>true</AppendTargetFrameworkToOutputPath>
</PropertyGroup>

<!-- GOOD: 仅非默认值 -->
<PropertyGroup>
  <TargetFramework>net8.0</TargetFramework>
</PropertyGroup>
```

---

## AP-05：SDK 风格项目中手动文件列表

**气味**：SDK 风格项目中 `<Compile Include="File1.cs" />`，`<Compile Include="File2.cs" />`。

**为什么不好**：SDK 风格项目自动匹配 `**/*.cs`（以及其他文件类型）。显式列出是冗余的，会创建合并冲突，如果未将新文件添加到列表中，可能会意外遗漏。

```xml
<!-- BAD -->
<ItemGroup>
  <Compile Include="Program.cs" />
  <Compile Include="Services\MyService.cs" />
  <Compile Include="Models\User.cs" />
</ItemGroup>

<!-- GOOD: 完全删除 — SDK 默认包含所有 .cs 文件。
     仅在需要排除时使用 Remove/Exclude： -->
<ItemGroup>
  <Compile Remove="LegacyCode\**" />
</ItemGroup>
```

**例外**：非 SDK 风格（遗留）项目需要显式文件包含。如果迁移，请参阅 `msbuild-modernization` 技能。

**例外（F# / `.fsproj`）**：F# 编译是顺序相关的 — 编译器按顺序处理 `<Compile Include>` 项，并且文件只能引用在其之前声明的类型/模块。`.fsproj` 文件必须显式列出每个源文件，按依赖顺序（实用程序/叶模块在顶部，入口点如 `Program.fs` 在底部）。如果使用 `.fsi` 签名文件，它必须**立即位于**其伴生 `.fs` 实现文件之前。

---

## AP-06：使用 `<Reference>` 和 HintPath 为 NuGet 包

**气味**：`<Reference Include="..." HintPath="..\packages\SomePackage\lib\..." />`

**为什么不好**：这是遗留的 `packages.config` 模式。它不支持传递依赖项、版本冲突解决或自动还原。`packages/` 文件必须单独提交或还原。

```xml
<!-- BAD -->
<ItemGroup>
  <Reference Include="Newtonsoft.Json">
    <HintPath>..\packages\Newtonsoft.Json.13.0.3\lib\netstandard2.0\Newtonsoft.Json.dll</HintPath>
  </Reference>
</ItemGroup>

<!-- GOOD -->
<ItemGroup>
  <PackageReference Include="Newtonsoft.Json" Version="13.0.3" />
</ItemGroup>
```

**注意**：没有 HintPath 的 `<Reference>` 仍然适用于 .NET Framework GAC 程序集，如 `WindowsBase`、`PresentationCore` 等。

---

## AP-07：Analyzer/Tool 包缺少 `PrivateAssets="all"`

**气味**：`<PackageReference Include="StyleCop.Analyzers" Version="..." />` 没有 `PrivateAssets="all"`。

**为什么不好**：如果没有 `PrivateAssets="all"`，分析器和构建工具包将作为传递依赖项流向库的消费者。消费者会收到他们没有要求的不需要的分析器或构建时工具。

参见 [`references/private-assets.md`](references/private-assets.md) 以获取 BAD/GOOD 示例和需要此设置的全包列表。

---

## AP-08：跨多个 .csproj 文件复制粘贴属性

**气味**：相同的 `<PropertyGroup>` 块出现在 3 个或更多项目文件中。

**为什么不好**：维护负担 — 必须在所有文件中更改。随着时间的推移，不一致性会逐渐出现。

```xml
<!-- BAD: 在每个 .csproj 中重复 -->
<!-- ProjectA.csproj, ProjectB.csproj, ProjectC.csproj 都有: -->
<PropertyGroup>
  <Nullable>enable</Nullable>
  <TreatWarningsAsErrors>true</TreatWarningsAsErrors>
  <ImplicitUsings>enable</ImplicitUsings>
</PropertyGroup>

<!-- GOOD: 在仓库/src 根目录的 Directory.Build.props 中定义一次 -->
<!-- Directory.Build.props -->
<Project>
  <PropertyGroup>
    <Nullable>enable</Nullable>
    <TreatWarningsAsErrors>true</TreatWarningsAsErrors>
    <ImplicitUsings>enable</ImplicitUsings>
  </PropertyGroup>
</Project>
```

参见 `directory-build-organization` 技能以获取有关结构化 `Directory.Build.props` / `Directory.Build.targets` 的完整指导。

---

## AP-09：没有中央包管理器的分散的包版本

**气味**：`<PackageReference Include="X" Version="1.2.3" />` 在不同项目中具有相同包的不同版本。

**为什么不好**：版本漂移 — 不同项目使用相同包的不同版本，导致运行时不匹配、意外行为或菱形依赖冲突。

```xml
<!-- BAD: 在每个项目中指定版本，可能会漂移 -->
<!-- ProjectA.csproj -->
<PackageReference Include="Newtonsoft.Json" Version="13.0.1" />
<!-- ProjectB.csproj -->
<PackageReference Include="Newtonsoft.Json" Version="13.0.3" />
```

**修复**：使用中央包管理。有关详细信息，请参阅 [https://learn.microsoft.com/en-us/nuget/consume-packages/central-package-management](https://learn.microsoft.com/en-us/nuget/consume-packages/central-package-management)。

---

## AP-10：单体目标（一个目标中太多内容）

**气味**：一个 `<Target>` 包含 50 多行执行多个不相关的事情。

**为什么不好**：无法通过增量构建跳过单个步骤，难以调试，难以扩展，并且目标名称变得无意义。

```xml
<!-- BAD -->
<Target Name="PrepareRelease" BeforeTargets="Build">
  <WriteLinesToFile File="version.txt" Lines="$(Version)" Overwrite="true" />
  <Copy SourceFiles="LICENSE" DestinationFolder="$(OutputPath)" />
  <Exec Command="signtool sign /f cert.pfx $(OutputPath)*.dll" />
  <MakeDir Directories="$(OutputPath)docs" />
  <Copy SourceFiles="@(DocFiles)" DestinationFolder="$(OutputPath)docs" />
  <!-- ... 30 多行 ... -->
</Target>

<!-- GOOD: 单一职责目标 -->
<Target Name="WriteVersionFile" BeforeTargets="CoreCompile"
        Inputs="$(MSBuildProjectFile)" Outputs="$(IntermediateOutputPath)version.txt">
  <WriteLinesToFile File="$(IntermediateOutputPath)version.txt" Lines="$(Version)" Overwrite="true" />
</Target>

<Target Name="CopyLicense" AfterTargets="Build">
  <Copy SourceFiles="LICENSE" DestinationFolder="$(OutputPath)" SkipUnchangedFiles="true" />
</Target>

<Target Name="SignAssemblies" AfterTargets="Build" DependsOnTargets="CopyLicense"
        Condition="'$(SignAssemblies)' == 'true'">
  <Exec Command="signtool sign /f cert.pfx %(AssemblyFiles.Identity)" />
</Target>
```

---

## AP-11：缺少 `Inputs` 和 `Outputs` 的自定义目标

**气味**：`<Target Name="MyTarget" BeforeTargets="Build">` 没有 `Inputs` / `Outputs` 属性。

**为什么不好**：目标在每次构建时都会运行，即使没有更改。这会破坏增量构建并减慢无操作构建的速度。

参见 [`references/incremental-build-inputs-outputs.md`](references/incremental-build-inputs-outputs.md) 以获取 BAD/GOOD 示例和包含 FileWrites 注册的完整模式。

参见 `incremental-build` 技能以获取有关 Inputs/Outputs、FileWrites 和最新检查的深入指导。

---

## AP-12：在 .targets 而不是 .props 中设置默认值

**气味**：`.targets` 文件中包含默认值的 `<PropertyGroup>`。

**为什么不好**：`.targets` 文件是晚些时候导入的（在项目文件之后）。在它们设置默认值时，其他 `.targets` 文件可能已经使用了空/未定义的值。`.props` 文件是早期导入的，并且是设置默认值的地方。

```xml
<!-- BAD: custom.targets -->
<PropertyGroup>
  <MyToolVersion>2.0</MyToolVersion>
</PropertyGroup>
<Target Name="RunMyTool">
  <Exec Command="mytool --version $(MyToolVersion)" />
</Target>

<!-- GOOD: 分为 .props（默认值）+ .targets（逻辑） -->
<!-- custom.props (早期导入) -->
<PropertyGroup>
  <MyToolVersion Condition="'$(MyToolVersion)' == ''">2.0</MyToolVersion>
</PropertyGroup>

<!-- custom.targets (晚期导入) -->
<Target Name="RunMyTool">
  <Exec Command="mytool --version $(MyToolVersion)" />
</Target>
```

**规则**：`.props` = 默认值和设置（早期评估）。`.targets` = 构建逻辑和目标（晚期评估）。

---

## AP-13：没有 `Exists()` 守卫的导入

**气味**：`<Import Project="some-file.props" />` 没有使用 `Condition="Exists('...')"` 检查。

**为什么不好**：如果文件不存在（尚未创建、路径错误、已删除），构建会因令人困惑的错误而失败。可选导入应始终有守卫。

```xml
<!-- BAD -->
<Import Project="$(RepoRoot)eng\custom.props" />

<!-- GOOD: 守卫可选导入 -->
<Import Project="$(RepoRoot)eng\custom.props" Condition="Exists('$(RepoRoot)eng\custom.props')" />

<!-- ALSO GOOD: Sdk 属性导入不需要守卫（按设计是必需的） -->
<Project Sdk="Microsoft.NET.Sdk">
```

**例外 — 必需的导入**：*必需*的导入应快速失败 — 不要守卫那些。守卫可选的或环境特定的导入（例如，本地开发人员覆盖、CI 特定设置）。

**例外 — NuGet 包转发器**：NuGet 包的每个 TFM `build/` 或 `buildTransitive/` 文件夹中的 `.props`/`.targets` 文件例行导入兄弟文件 `buildTransitive/<tfm>/…` 而不使用 `Exists()` 守卫。这些是**包契约**：目标文件在还原的包中是保证存在的，即使它没有出现在源树中的该相对路径下。包布局通常由以下方式生成：

- 自定义 `.nuspec` 包含每个 TFM 的 `<file>` 条目 — 例如 `<file src="buildTransitive\common\MyAdapter.props" target="buildTransitive\net8.0\MyAdapter.props" />` — 在打包时将文件从单个源文件夹（例如 `buildTransitive/common/`）复制到每个 TFM 子文件夹中，或
- `<None Update="...">` / `<Content Include="...">` 项目中的 `<PackagePath>`（例如 `<PackagePath>buildTransitive/net8.0/</PackagePath>`），每个目标 TFM 声明一次，或
- SDK 规范（例如 `IncludeBuildOutput`、`BuildOutputTargetFolder`）将构建输出放置在 `build/<tfm>/` 下。

在标记 `build/` 或 `buildTransitive/` 文件夹中的未守卫的 `<Import>` 之前，**根据打包布局解决它** — 读取项目目录中的每个 `*.nuspec` **及其直接父目录**（在单体存储库中共享 nuspec 很常见；不要向上遍历），以及 `.csproj` 中 `<None>`/`<Content>` 项的任何 `<PackagePath>` 元数据。仅在**源树和投影的包布局**中都缺少目标路径时才标记。`dotnet-msbuild/extension-points` 技能 — *源树与打包布局* — 记录了完整的交叉检查程序。

**转发 `buildTransitive/` → `build/`**：通过兄弟 `build/*.props` / `build/*.targets` 文件转发（而不是直接转发到 `buildMultiTargeting/`）；当 `build/` 是按 TFM (`build/<tfm>/`) 时，包括从文件自己的文件夹派生的 TFM 段（而不是 `$(TargetFramework)`），否则递归消费者会遇到 `MSB4019`。有关规则和派生表达式，请参阅 `extension-points` 技能 — *转发链*。

---

## AP-14：路径中的反斜杠 — 哪里重要

**气味**：`.props`/`.targets` 文件中用于跨平台运行的路径分隔符中的反斜杠。

**在哪里是一个真正的错误（🔴 错误）** — MSBuild 不通过其路径规范化器路由的路径：

- `<Exec Command="...\tools\foo.exe ..." />` 中的原始 shell 字符串 — 逐字传递给 Unix 上的 `bash`/`sh`，其中 `\` 被视为转义字符。
- 反斜杠限定路径 — 嵌入在源文件中由 `<WriteLinesToFile>` 生成的 CDATA 块中，或为非 MSBuild 消费者（自定义脚本、响应文件、环境变量）构造的路径。
- 传递给直接调用 OS 文件 API 的自定义任务而不通过 MSBuild 路径工具的路径。

**在哪里只是一个样式偏好（🔵 样式）** — 通过 MSBuild 评估器路由的路径：`<Import Project="...">`，由 `<Copy>`/`<MakeDir>`/`<Delete>` 等内置任务消费的文件路径属性，项 `Include=`/`Exclude=` 模式：

MSBuild 的求值器在类 Unix 系统上解析路径前，会将 `\` 规范化为 `/`。参见 [`microsoft/msbuild` `src/Framework/FileUtilities.cs`](https://github.com/dotnet/msbuild/blob/main/src/Framework/FileUtilities.cs) 中的 `FileUtilities.MaybeAdjustFilePath` 和 `ConvertToUnixSlashes`。因此，当前 `<Import Project="$(MSBuildThisFileDirectory)..\..\build\common.props" />` 在 Linux/macOS 上可以正确解析。正斜杠仍然**优先用于保持一致性**，但导入不会因此中断，现有的反斜杠风格导入不应被标记为 🔴 **Error**。

```xml
<!-- 🔴 Error: 原始 shell 字符串中的 \ 在 Linux/macOS 上会出错 -->
<Exec Command="$(MSBuildThisFileDirectory)tools\release\sign.exe $(OutputPath)" />

<!-- 🔵 Style: Import 中的 \ 在 Unix 上会被规范化，但 / 更好 -->
<Import Project="$(MSBuildThisFileDirectory)..\..\build\common.props" />

<!-- ✅ 新代码中的推荐做法 -->
<Import Project="$(MSBuildThisFileDirectory)../../build/common.props" />
```

**校验规则**：在将反斜杠路径标记为 🔴 **Error** 之前，要问自己：*“这个字符串是经过 MSBuild 求值器处理，还是被原样传递给非 MSBuild 使用者？”* 只有后者才属于正确性缺陷。

**注意**：`$(MSBuildThisFileDirectory)` 本身已经以平台适当的分隔符结尾，因此 `$(MSBuildThisFileDirectory)tools/mytool` 在两个平台上都可以正常工作。

---

## AP-15：多个作用域中无条件的属性覆盖

**坏味道**：某个属性在 `Directory.Build.props` 和 `.csproj` 中都被无条件设置——后写入者静默胜出。

**为何有害**：难以追踪实际使用的是哪个值。会使构建变得脆弱，也让阅读项目文件的人感到困惑。

```xml
<!-- BAD: Directory.Build.props 设置该属性，csproj 静默覆盖 -->
<!-- Directory.Build.props -->
<PropertyGroup>
  <OutputPath>bin\custom\</OutputPath>
</PropertyGroup>
<!-- MyProject.csproj -->
<PropertyGroup>
  <OutputPath>bin\other\</OutputPath>
</PropertyGroup>

<!-- GOOD: 使用条件使覆盖具有明确意图 -->
<!-- Directory.Build.props -->
<PropertyGroup>
  <OutputPath Condition="'$(OutputPath)' == ''">bin\custom\</OutputPath>
</PropertyGroup>
<!-- MyProject.csproj 现在可以有意覆盖，或保留默认值 -->
```

---

对于其他反模式（AP-16 到 AP-23）以及快速参考清单，请参阅 [additional-antipatterns.md](references/additional-antipatterns.md)。
