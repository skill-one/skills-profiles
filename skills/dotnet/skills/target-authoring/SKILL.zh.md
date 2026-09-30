---
name: target-authoring
description: 编写自定义 MSBuild 目标的规范模式。用途：诊断和修复自定义目标编写反模式；跨文件损坏的 SDK 目标链（例如，Directory.Build.targets 悄然重定义 SDK 目标）；替换 CompileDependsOn 而不是用 $(CompileDependsOn) 扩展的目标；查询目标因 Outputs 与 Returns 误用而返回陈旧结果；缺失的 Inputs/Outputs 导致不必要的重新构建；缺失的 FileWrites 注册。涵盖 DependsOnTargets 与 BeforeTargets 与 AfterTargets、Build→CoreBuild 三级模式，以及 $(XxxDependsOn) 链式扩展模式。不适用：增量构建调优（使用 incremental-build）、并行化（使用 build-parallelism）、通用反模式（使用 msbuild-antipatterns）、非 MSBuild 构建系统。
---

# 自定义目标编写模式

MSBuild 存储库中 `Microsoft.Common.CurrentVersion.targets` 的规范模式。

## 三级目标链

每个主要入口点（Build、Rebuild、Clean）都委托给一个**属性**来列出其依赖项，该属性通过 Before → Core → After 链接：

```xml
<PropertyGroup>
  <BuildDependsOn>
    BeforeBuild;
    CoreBuild;
    AfterBuild
  </BuildDependsOn>
</PropertyGroup>

<Target Name="Build"
    Condition=" '$(_InvalidConfigurationWarning)' != 'true' "
    DependsOnTargets="$(BuildDependsOn)"
    Returns="@(TargetPathWithTargetPlatformMoniker)" />

<!-- 空的扩展性目标 — 用户可以重写这些 -->
<Target Name="BeforeBuild" />
<Target Name="AfterBuild" />
```

`CoreBuild` 委托给 `$(CoreBuildDependsOn)` 并包含错误处理器：

```xml
<Target Name="CoreBuild" DependsOnTargets="$(CoreBuildDependsOn)">
  <OnError ExecuteTargets="_TimeStampAfterCompile;PostBuildEvent"
      Condition="'$(RunPostBuildEvent)' == 'Always'" />
  <OnError ExecuteTargets="_CleanRecordFileWrites" />
</Target>
```

### 规则

- 委托给属性 (`DependsOnTargets="$(MyTargetDependsOn)"`)，而不是硬编码的目标。
- `OnError` 放在编排目标内部，以确保即使在失败时也能运行清理操作。
- 空的 Before/After 目标是扩展性点。用户可以重写它们；SDK 从不向其中添加逻辑。

## 链接扩展 — 仅追加，永不覆盖

当向现有链添加自定义目标时，**追加**到 `DependsOn` 属性：

```xml
<!-- GOOD: 追加到现有链 -->
<PropertyGroup>
  <CompileDependsOn>$(CompileDependsOn);MyCodeGenTarget</CompileDependsOn>
</PropertyGroup>

<!-- BAD: 覆盖整个链，丢失 SDK 目标 -->
<PropertyGroup>
  <CompileDependsOn>MyCodeGenTarget</CompileDependsOn>
</PropertyGroup>
```

## DependsOnTargets vs BeforeTargets vs AfterTargets

| 机制 | 定义位置 | 最适用于 |
|---|---|---|
| `DependsOnTargets` | 需要依赖的目标 | 明确需要其他目标的目标 |
| `BeforeTargets` | 注入目标 | 在不属于你的目标之前插入 |
| `AfterTargets` | 注入目标 | 在不属于你的目标之后插入 |

验证目标使用 `BeforeTargets` 来拦截所有入口点：

```xml
<Target Name="_CheckForInvalidConfigurationAndPlatform"
    BeforeTargets="$(BuildDependsOn);Build;$(RebuildDependsOn);Rebuild;$(CleanDependsOn);Clean">
</Target>
```

**规则：**

- 当你的目标需要特定先决条件时，使用 `DependsOnTargets`。
- 当你注入不属于你的管道时，使用 `BeforeTargets`/`AfterTargets`。
- 当你不控制目标文件时，优先选择 `BeforeTargets="CoreCompile"` 覆盖 `$(CompileDependsOn)`。

## Returns vs Outputs

```xml
<!-- Build 返回供引用项目消费的项 -->
<Target Name="Build"
    DependsOnTargets="$(BuildDependsOn)"
    Returns="@(TargetPathWithTargetPlatformMoniker)" />

<!-- GetTargetPath 是一个轻量级查询目标 -->
<Target Name="GetTargetPath" Returns="@(TargetPathWithTargetPlatformMoniker)" />
```

- **`Returns`** 指定调用此项目时 MSBuild 任务接收的内容。用于跨项目通信。
- **`Outputs`** 在内部目标上用于增量性（时间戳检查）。用于检测最新状态。
- 永远不要混用这两个目的。查询目标（`GetTargetPath`，`GetTargetFrameworks`）应使用 `Returns`，而不是 `Outputs`。

## 目标命名约定

| 模式 | 含义 | 示例 |
|---|---|---|
| `_PrefixedName` | 内部/私有目标 | `_TimeStampBeforeCompile` |
| `CoreXxx` | 实际实现 | `CoreBuild`，`CoreCompile` |
| `BeforeXxx` / `AfterXxx` | 空的扩展性钩子 | `BeforeBuild`，`AfterCompile` |
| `PrepareXxx` | 设置/验证阶段 | `PrepareForBuild` |
| `ResolveXxx` | 发现/解析阶段 | `ResolveReferences` |
| `GetXxx` | 轻量级查询（无副作用） | `GetTargetPath` |

## 完整的自定义目标模板

```xml
<!-- 1. 定义用于扩展性的 DependsOn 链 -->
<PropertyGroup>
  <MyFeatureDependsOn>
    _ValidateMyFeatureInputs;
    BeforeMyFeature;
    CoreMyFeature;
    AfterMyFeature
  </MyFeatureDependsOn>
</PropertyGroup>

<!-- 2. 外部目标使用 Returns 进行跨项目通信 -->
<Target Name="MyFeature"
    DependsOnTargets="$(MyFeatureDependsOn)"
    Returns="@(MyFeatureOutput)" />

<!-- 3. 空的扩展性点 -->
<Target Name="BeforeMyFeature" />
<Target Name="AfterMyFeature" />

<!-- 4. 核心实现包含 Inputs/Outputs 用于增量性 -->
<Target Name="CoreMyFeature"
    Inputs="$(MSBuildAllProjects);@(MyFeatureInput)"
    Outputs="$(IntermediateOutputPath)myfeature.generated.cs">
  <Exec Command="my-tool.exe -o $(IntermediateOutputPath)myfeature.generated.cs" />
  <!-- 5. 注册输出用于清理跟踪 -->
  <ItemGroup>
    <Compile Include="$(IntermediateOutputPath)myfeature.generated.cs" />
    <FileWrites Include="$(IntermediateOutputPath)myfeature.generated.cs" />
  </ItemGroup>
</Target>

<!-- 6. 验证目标在依赖链中首先运行 -->
<Target Name="_ValidateMyFeatureInputs">
  <Error Text="MyFeatureInput 项是必需的。"
         Condition="'@(MyFeatureInput)' == ''" />
</Target>
```

## 常见陷阱

- **覆盖 `DependsOn` 属性** 会无声地丢失 SDK 目标。追加时始终包含 `$(ExistingProperty)`。
- **在查询目标上使用 `Outputs`** 会导致 MSBuild 在“最新”时跳过它们，返回过时数据。使用 `Returns`。
- **在 `.props` 中定义目标** 意味着 SDK 目标的 `BeforeTargets` 还没有可以挂钩的东西。将目标移到 `.targets`。
- **在编排目标中忘记 `OnError`** 意味着在构建错误时文件跟踪失败，会破坏后续的增量构建。
