# 使用 Directory.Build 文件组织构建基础设施

## Directory.Build.props 与 Directory.Build.targets

理解使用哪个文件至关重要。它们在评估过程中的**导入时机**有所不同：

**评估顺序：**

```
Directory.Build.props → SDK .props → YourProject.csproj → SDK .targets → Directory.Build.targets
```

| 使用 `.props` 用于 | 使用 `.targets` 用于 |
|---|---|
| 设置属性默认值 | 自定义构建目标 |
| 常用项定义 | 晚绑定属性覆盖 |
| 项目可覆盖的属性 | 构建后步骤 |
| 程序集/包元数据 | 对最终值的条件逻辑 |
| Analyzer PackageReferences | 依赖 SDK 定义属性的构建目标 |

**经验法则：** 属性和项放在 `.props` 中。自定义目标和晚绑定逻辑放在 `.targets` 中。

因为 `.props` 在项目文件之前导入，所以项目可以覆盖其中设置的任何值。因为 `.targets` 在所有内容之后导入，它有最终决定权——但项目无法覆盖 `.targets` 中的值。

### ⚠️ 重要：.props 与 .targets 中 TargetFramework 的可用性

**在 `.props` 文件中对 `$(TargetFramework)` 的属性条件在单目标项目中对属性进行静默失败**——在 `.props` 评估期间，该属性为空。将 TFM 条件属性移至 `.targets` 中。ItemGroup 和 Target 条件不受影响。

有关完整解释，请参阅 [targetframework-props-pitfall.md](references/targetframework-props-pitfall.md)。

## Directory.Build.props

良好候选者：语言设置、程序集/包元数据、构建警告、代码分析、常用分析器。

```xml
<Project>
  <PropertyGroup>
    <Nullable>enable</Nullable>
    <ImplicitUsings>enable</ImplicitUsings>
    <TreatWarningsAsErrors>true</TreatWarningsAsErrors>
    <EnforceCodeStyleInBuild>true</EnforceCodeStyleInBuild>
    <Company>Contoso</Company>
    <Authors>Contoso Engineering</Authors>
  </PropertyGroup>
</Project>
```

**不要放在这里：** 项目特定的 TFMs、项目特定的 PackageReferences、目标/构建逻辑，或依赖于 SDK 定义值的属性（在 `.props` 评估期间不可用）。

## Directory.Build.targets

良好候选者：自定义构建目标、晚绑定属性覆盖（依赖于 SDK 属性的值）、构建后验证。

```xml
<Project>
  <Target Name="ValidateProjectSettings" BeforeTargets="Build">
    <Error Text="所有库必须针对 netstandard2.0 或更高版本"
           Condition="'$(OutputType)' == 'Library' AND '$(TargetFramework)' == 'net472'" />
  </Target>

  <PropertyGroup>
    <!-- DocumentationFile 依赖于 OutputPath，该值由 SDK 设置 -->
    <DocumentationFile Condition="'$(IsPackable)' == 'true'">$(OutputPath)$(AssemblyName).xml</DocumentationFile>
  </PropertyGroup>
</Project>
```

## Directory.Packages.props (中央包管理)

中央包管理 (CPM) 为所有 NuGet 包版本提供了一个单一的事实来源。有关详细信息，请参阅 [https://learn.microsoft.com/en-us/nuget/consume-packages/central-package-management](https://learn.microsoft.com/en-us/nuget/consume-packages/central-package-management)。

**在仓库根目录的 `Directory.Packages.props` 中启用 CPM：**

```xml
<Project>
  <PropertyGroup>
    <ManagePackageVersionsCentrally>true</ManagePackageVersionsCentrally>
  </PropertyGroup>

  <ItemGroup>
    <PackageVersion Include="Microsoft.Extensions.Logging" Version="8.0.0" />
    <PackageVersion Include="Newtonsoft.Json" Version="13.0.3" />
    <PackageVersion Include="xunit" Version="2.9.0" />
    <PackageVersion Include="xunit.runner.visualstudio" Version="2.8.2" />
  </ItemGroup>

  <ItemGroup>
    <!-- GlobalPackageReference 适用于所有项目——非常适合分析器 -->
    <GlobalPackageReference Include="StyleCop.Analyzers" Version="1.2.0-beta.556" />
    <GlobalPackageReference Include="Microsoft.CodeAnalysis.NetAnalyzers" Version="8.0.0" />
  </ItemGroup>
</Project>
```

## Directory.Build.rsp

包含应用于目录树下所有构建的默认 MSBuild CLI 参数。

**示例 `Directory.Build.rsp`：**

```
/maxcpucount
/nodeReuse:false
/consoleLoggerParameters:Summary;ForceNoAlign
/warnAsMessage:MSB3277
```

- 在现代 .NET 版本中与 `msbuild` 和 `dotnet` CLI 都兼容
- 非常适合强制执行一致的 CI 和本地构建标志
- 每个参数都在单独的一行

## 多级 Directory.Build 文件

MSBuild 仅自动导入从项目目录向上遍历时找到的**第一个** `Directory.Build.props`（或 `.targets`）。要链接多个级别，请在内部文件的**顶部**显式导入父文件。有关完整文件示例，请参阅 [multi-level-examples](references/multi-level-examples.md)。

```xml
<Project>
  <Import Project="$([MSBuild]::GetPathOfFileAbove('Directory.Build.props', '$(MSBuildThisFileDirectory)../'))"
         Condition="Exists('$([MSBuild]::GetPathOfFileAbove('Directory.Build.props', '$(MSBuildThisFileDirectory)../'))')" />

  <!-- 内部级别的覆盖放在这里 -->
</Project>
```

**示例布局：**

```
repo/
  Directory.Build.props          ← 仓库级（语言版本、公司信息、分析器）
  Directory.Build.targets        ← 仓库级目标
  Directory.Packages.props       ← 中央包版本
  src/
    Directory.Build.props        ← src特定（导入仓库级，设置 IsPackable=true）
  test/
    Directory.Build.props        ← test特定（导入仓库级，设置 IsPackable=false，添加测试包）
```

## 资产输出布局 (.NET 8+)

在 `Directory.Build.props` 中设置 `<ArtifactsPath>$(MSBuildThisFileDirectory)artifacts</ArtifactsPath>`，以自动生成项目名分隔的 `bin/`、`obj/` 和 `publish/` 目录，这些目录位于单个 `artifacts/` 文件夹下，默认情况下避免了 `bin/obj` 冲突。有关目录布局和附加模式（按项目类型进行条件设置、打包后验证），请参阅 [common-patterns](references/common-patterns.md)。

## 工作流：组织构建基础设施

1. **审计所有 `.csproj` 文件**——跨解决方案目录列出每个 `<PropertyGroup>`、`<ItemGroup>` 和自定义 `<Target>`。注意哪些设置重复，哪些是项目特定的。
2. **创建根 `Directory.Build.props`**——将共享属性默认值（LangVersion、Nullable、TreatWarningsAsErrors、元数据）移至此处。这些是在项目文件之前导入的，因此项目可以覆盖它们。
3. **创建根 `Directory.Build.targets`**——将自定义构建目标、构建后验证以及任何依赖于 SDK 定义值的属性（例如，单目标项目的 `OutputPath`、`TargetFramework`）移至此处。这些是在 SDK 之后导入的，因此所有属性都可用。
4. **创建 `Directory.Packages.props`**——启用中央包管理 (`ManagePackageVersionsCentrally`)，列出所有 `PackageVersion` 条目，并在 `.csproj` 文件中删除 `PackageReference` 项中的 `Version=`。
5. **设置多级层次结构**——为 `src/` 和 `test/` 文件夹创建具有不同设置的内部 `Directory.Build.props` 文件。使用 `GetPathOfFileAbove` 链接到父文件。
6. **简化 `.csproj` 文件**——删除所有集中化属性、版本属性和重复的目标。每个项目应仅包含其独特的内容。
7. **验证**——运行 `dotnet restore && dotnet build` 并验证没有回归。如有需要，可以使用 `dotnet msbuild -pp:output.xml` 检查最终的合并视图。

## 故障排除

| 问题 | 原因 | 解决方法 |
|---|---|---|
| `Directory.Build.props` 没有被拾取 | 文件名大小写错误（Linux/macOS 上需要精确匹配） | 验证精确大小写：`Directory.Build.props`（大写 D、B） |
| 项目忽略了 `.props` 中的属性 | 项目在导入后设置了相同的属性 | 将属性移至 `Directory.Build.targets` 以在项目之后设置它 |
| 多级导入不起作用 | 内部文件中缺少 `GetPathOfFileAbove` 导入 | 在内部文件的顶部添加 `<Import>` 元素（见多级部分） |
| `.props` 中的 SDK 值属性为空 | SDK 属性在 `.props` 评估期间尚未定义 | 移至 `.targets`，它在 SDK 之后导入 |
| 未找到 `Directory.Packages.props` | 文件不在仓库根目录或名称不精确 | 必须命名为 `Directory.Packages.props` 并位于或高于项目目录 |
| `.props` 中的 `$(TargetFramework)` 属性条件不匹配 | 在单目标项目中的 `.props` 评估期间 `TargetFramework` 尚未设置 | 将属性移至 `.targets`，或使用 ItemGroup/Target 条件（这些条件在较晚时评估） |

**诊断：** 使用预处理的项目输出查看所有导入和最终属性值：

```bash
dotnet msbuild -pp:output.xml MyProject.csproj
```

这将展开所有导入，以便您可以看到每个属性是在哪里设置的以及最终评估的值是什么。
