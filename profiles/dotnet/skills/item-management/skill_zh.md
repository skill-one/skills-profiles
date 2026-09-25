# MSBuild 项目管理模式

来自 `Microsoft.Common.CurrentVersion.targets` 的标准项目组操作模式。

## 包含 / 移除 / 更新 — 三种操作

| 操作 | 目的 | 使用场景 |
|---|---|---|
| `Include` | 向项目组添加新项目 | 创建具有标识符 + 元数据的项 |
| `Remove` | 移除匹配模式的项目 | 排除文件或清空项目组 |
| `Update` | 修改现有项目的元数据 | 添加/更改元数据而不重新添加 |

### 包含 — 添加项目

```xml
<ItemGroup>
  <Compile Include="Generated\*.cs">
    <AutoGen>true</AutoGen>
  </Compile>
</ItemGroup>
```

### 移除 — 减去项目

```xml
<ItemGroup>
  <!-- 移除特定项目 -->
  <Reference Remove="$(AdditionalExplicitAssemblyReferences)" />

  <!-- 设置减法：先前的减当前 -->
  <_CleanOrphanFileWrites Include="@(_CleanPriorFileWrites)"
      Exclude="@(_CleanCurrentFileWrites)" />

  <!-- 清空整个项目组 -->
  <_Temporary Remove="@(_Temporary)" />
</ItemGroup>
```

### 更新 — 修改现有项目

```xml
<ItemGroup>
  <EmbeddedResource Update="@(EmbeddedResource)"
      Condition="'%(NuGetPackageId)' == 'Microsoft.CodeAnalysis.Collections'">
    <GenerateSource>true</GenerateSource>
    <ClassName>Microsoft.CodeAnalysis.Collections.SR</ClassName>
  </EmbeddedResource>
</ItemGroup>
```

`Update` 不会添加项目 — 它仅修改项目组中已有的项目。

## 项目批处理 — %(元数据)

当 `%(元数据)` 出现在目标属性或任务参数中时，MSBuild **按唯一元数据值批处理**执行。

### 目标级批处理（输出）

```xml
<Target Name="GenerateSatelliteAssemblies"
    Inputs="$(MSBuildAllProjects);@(_SatelliteAssemblyResourceInputs)"
    Outputs="$(IntermediateOutputPath)%(Culture)\$(TargetName).resources.dll">
  <!-- 对每个唯一的 Culture 值运行一次 -->
</Target>
```

### 任务级批处理

```xml
<Copy SourceFiles="@(_SourceItems)"
    DestinationFiles="@(_SourceItems->'$(OutDir)%(TargetPath)')">
</Copy>
```

### 基于项目的条件过滤

```xml
<ItemGroup>
  <_ResxOutput Include="@(EmbeddedResource->'%(OutputResource)')"
      Condition="'%(EmbeddedResource.WithCulture)' == 'false'" />
</ItemGroup>
```

### 批处理规则

- `%(元数据)` 在 `Condition` 或 `Outputs` 中 → 目标按唯一值批处理。
- `%(元数据)` 在任务参数中 → 任务按唯一值批处理。
- **不要在同一个表达式中混合来自不同项目组的 `%()`** — 这会导致交叉乘积（见常见陷阱）。

## 项目转换 — @(项目->'表达式')

转换通过将表达式应用于每个项目来创建新的项目列表：

```xml
<!-- 将文件路径转换为目标路径 -->
<Copy SourceFiles="@(IntermediateAssembly)"
    DestinationFiles="@(IntermediateAssembly->'$(OutDir)%(Filename)%(Extension)')"/>

<!-- 用于显示的分隔符转换 -->
<Message Text="文件： @(Compile->'%(Filename)', ', ')" />
```

## 排除模式 — 在包含上设置减法

```xml
<ItemGroup>
  <Compile Include="**\*.cs" Exclude="Generated\**;Tests\**" />
</ItemGroup>
```

`Exclude` 仅适用于 `Include` — 它不能与 `Update` 或 `Remove` 一起使用。

## 条件项目包含

```xml
<!-- 对 ItemGroup 进行条件 — 全有或全无 -->
<ItemGroup Condition="'$(NetCoreBuild)' == 'true'">
  <PackageReference Include="System.IO.Pipelines" />
</ItemGroup>

<!-- 对单个项目进行条件 -->
<ItemGroup>
  <PackageReference Include="System.IO.Pipelines"
      Condition="'$(NetCoreBuild)' == 'true'" />
</ItemGroup>
```

## Tool/Analyzer 包的 PrivateAssets

```xml
<ItemGroup>
  <PackageReference Include="Microsoft.CodeAnalysis.NetAnalyzers" PrivateAssets="all" />
  <PackageReference Include="StyleCop.Analyzers" PrivateAssets="all" />
</ItemGroup>
```

## 常见陷阱

### 交叉乘积批处理

从两个不同的项目组引用 `%(元数据)` 会导致 O(N×M) 执行：

```xml
<!-- BAD: @(Source) × @(Config) 的交叉乘积 -->
<Exec Command="process %(Source.Identity) with %(Config.Identity)" />

<!-- GOOD: 通过批处理引用一个组，通过属性引用另一个组 -->
<Exec Command="process %(Source.Identity) with $(ConfigFile)" />
```

### 源树中的生成文件

写入 `$(IntermediateOutputPath)`（obj/），而不是源目录。源树生成会污染版本控制并可能导致通过通配符重复编译。

### 缺失 FileWrites

目标创建的每个文件都必须添加到 `@(FileWrites)` 以支持 `dotnet clean`。
