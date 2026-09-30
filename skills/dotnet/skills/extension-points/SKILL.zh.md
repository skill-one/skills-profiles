---
name: extension-points
description: MSBuild 扩展指南：CustomBefore/CustomAfter 钩子、字母顺序通配符导入、控制属性导入门控、NuGet 包构建扩展布局（build/buildTransitive）以及 MicrosoftCommonPropsHasBeenImported 保护机制。用途：诊断和修复 MSBuild 导入和钩子模式、审查和修复 Directory.Build 文件中的扩展点反模式、修复导致全新克隆失败的缺失 Exists() 保护、修复 NuGet 包钩子被静默丢弃而非追加、使构建目标对其他项目可扩展、向构建管道注入自定义逻辑、创建扩展构建的 NuGet 包、条件禁用导入。不适用：目标编写模式（使用 target-authoring）、属性与目标放置（使用 directory-build-organization）、通用反模式（使用 msbuild-antipatterns）、非 MSBuild 构建系统。
---

# MSBuild 扩展点

MSBuild 管道如何为 SDK、NuGet 包、存储库和用户提供钩子以注入自定义逻辑。

## CustomBefore / CustomAfter 钩子

每个主要的 `.targets` 文件都定义了导入钩子：

```xml
<PropertyGroup>
  <CustomBeforeMicrosoftCommonTargets Condition="'$(CustomBeforeMicrosoftCommonTargets)' == ''">
    $(MSBuildExtensionsPath)\v$(MSBuildToolsVersion)\Custom.Before.Microsoft.Common.targets
  </CustomBeforeMicrosoftCommonTargets>
</PropertyGroup>

<Import Project="$(CustomBeforeMicrosoftCommonTargets)"
    Condition="'$(CustomBeforeMicrosoftCommonTargets)' != '' and Exists('$(CustomBeforeMicrosoftCommonTargets)')"/>
<!-- ... 核心目标 ... -->
<Import Project="$(CustomAfterMicrosoftCommonTargets)"
    Condition="'$(CustomAfterMicrosoftCommonTargets)' != '' and Exists('$(CustomAfterMicrosoftCommonTargets)')"/>
```

### 规则

- 默认路径包括版本 (`v$(MSBuildToolsVersion)`)，用于并行安装。
- 始终检查 `Exists()`。该文件可能不在每台机器上都存在。
- **追加**到属性（不要覆盖），以链式多个钩子：

```xml
<PropertyGroup>
  <CustomBeforeMicrosoftCommonTargets>
    $(CustomBeforeMicrosoftCommonTargets);$(MSBuildThisFileDirectory)MyExtension.targets
  </CustomBeforeMicrosoftCommonTargets>
</PropertyGroup>
```

## 通配符导入目录

MSBuild 导入扩展目录中的所有文件，并按字母顺序排序：

```xml
<Import Project="$(MSBuildExtensionsPath)\$(MSBuildToolsVersion)\Imports\Microsoft.Common.props\ImportBefore\*"
    Condition="'$(ImportByWildcardBeforeMicrosoftCommonProps)' == 'true'
               and Exists('$(MSBuildExtensionsPath)\$(MSBuildToolsVersion)\Imports\Microsoft.Common.props\ImportBefore')" />
```

### 关键路径

| 属性 | 解析为 | 范围 |
|---|---|---|
| `$(MSBuildUserExtensionsPath)` | `%APPDATA%\Microsoft\MSBuild` | 每个用户 |
| `$(MSBuildExtensionsPath)` | MSBuild 安装目录 | 全局机器 |
| `$(MSBuildProjectExtensionsPath)` | `obj/` 目录 | 每个项目（NuGet） |

使用数字前缀命名文件以进行排序：`01-first.props`, `02-second.props`。

## 导入门控 — 控制属性

每个通配符导入都由一个布尔属性门控：

```xml
<PropertyGroup>
  <ImportByWildcardBeforeMicrosoftCommonProps
      Condition="'$(ImportByWildcardBeforeMicrosoftCommonProps)' == ''">true</ImportByWildcardBeforeMicrosoftCommonProps>
  <ImportDirectoryBuildProps
      Condition="'$(ImportDirectoryBuildProps)' == ''">true</ImportDirectoryBuildProps>
</PropertyGroup>
```

### 可用的控制属性

| 属性 | 禁用内容 |
|---|---|
| `ImportDirectoryBuildProps` | 目录.Build.props 自动发现 |
| `ImportDirectoryBuildTargets` | 目录.Build.targets 自动发现 |
| `ImportProjectExtensionProps` | NuGet 生成的 `*.props` 在 obj/ |
| `ImportProjectExtensionTargets` | NuGet 生成的 `*.targets` 在 obj/ |
| `ImportByWildcardBefore*` | 机器级 ImportBefore 扩展 |
| `ImportByWildcardAfter*` | 机器级 ImportAfter 扩展 |

## NuGet 包构建扩展布局

NuGet 包通过 `build/` 或 `buildTransitive/` 文件夹注入构建逻辑：

```text
MyPackage/
  build/
    MyPackage.props      ← 通过 *.props 通配符导入
    MyPackage.targets    ← 通过 *.targets 通配符导入
  buildTransitive/
    MyPackage.props      ← 由传递消费者导入
    MyPackage.targets
```

### 规则

- 文件名必须**完全匹配包 ID**。
- `build/` 仅影响直接消费者。`buildTransitive/` 影响整个依赖链。
- Props 在项目之前导入（早期），targets 在项目之后导入（晚期）。

### 传递链：`buildTransitive/` → `build/` → 共享

将 `buildTransitive/*.props` 和 `buildTransitive/*.targets` 通过其兄弟 `build/*.props` / `build/*.targets` 文件（链式 `buildTransitive → build → shared`）转发，而不是直接导入 `buildMultiTargeting/`。这使 `build/` 成为一个单一的真相来源，并具有清晰的拥有链，以便传递消费者与直接消费者保持同步，而不是两个布局分道扬镳。

当 `build/` 按每个 TFM 打包（`build/<tfm>/`，通过 `TfmSpecificPackageFile`、每个 TFM 的 `<PackagePath>` 或 SDK 约定）时，而 `buildMultiTargeting/` 没有打包，`buildTransitive/<tfm>/` 转发器**必须包含 TFM 段**——省略它将解析为不存在的包根 `build/MyPackage.props`，并导致传递消费者出现 **`MSB4019`**。从文件自己的文件夹中派生该段，绝不能使用 `$(TargetFramework)`（NuGet 最近匹配可以为 `net10.0` 消费者提供 `net9.0` 文件夹，因此 `$(TargetFramework)` 可能命名一个从未恢复的文件夹）：

```xml
<!-- buildTransitive/<tfm>/MyPackage.props -->
<Import Project="$(MSBuildThisFileDirectory)..\..\build\$([System.IO.Path]::GetFileName($([System.IO.Path]::GetDirectoryName('$(MSBuildThisFileDirectory)'))))\MyPackage.props" />
```

## 源树与打包布局

在审查一个 NuGet 构建扩展包时，存储库中的**源布局**可以合法地与生成的 `.nupkg` 内部的**打包布局**不同。这是“导入点在缺失文件处”的常见误报来源。

三种打包机制在打包时重塑布局：

1. **`.nuspec` `<file src=… target=…>` 映射** — 将单个源文件复制到多个每个 TFM 目标：

   ```xml
   <!-- 源树有一个共享文件：
          buildTransitive\common\MyAdapter.props
        打包将其重写为 .nupkg 内部的每个 TFM 目标：
          buildTransitive\net462\MyAdapter.props
          buildTransitive\net8.0\MyAdapter.props
          buildTransitive\net9.0\MyAdapter.props -->
   <files>
     <file src="buildTransitive\common\MyAdapter.props" target="buildTransitive\net462\MyAdapter.props" />
     <file src="buildTransitive\common\MyAdapter.props" target="buildTransitive\net8.0\MyAdapter.props" />
     <file src="buildTransitive\common\MyAdapter.props" target="buildTransitive\net9.0\MyAdapter.props" />
   </files>
   ```

   在 `<file>` 元素中，以 `\` 结尾的 `target` 被视为文件夹（保留从 `src` 的文件名）；以文件名结尾的 `target` 重命名文件。

2. **`.csproj` `<PackagePath>` 元数据** 在 `<None Update=…>` 或 `<Content Include=…>` 项目上 — 通过 SDK 打包实现相同效果。使用每个目标一个项目以保持映射的明确性：

   ```xml
   <ItemGroup>
     <None Include="buildTransitive\common\MyAdapter.props" Pack="true" PackagePath="buildTransitive\net8.0\MyAdapter.props" />
     <None Include="buildTransitive\common\MyAdapter.props" Pack="true" PackagePath="buildTransitive\net9.0\MyAdapter.props" />
   </ItemGroup>
   ```

   NuGet/SDK 打包也接受分号分隔的列表（`PackagePath="buildTransitive\net8.0\;buildTransitive\net9.0\"`）将单个源分发给多个目标，但上面的多项目形式更难误读。

3. **SDK 约定** — `IncludeBuildOutput`, `BuildOutputTargetFolder`, `IncludeContentInPack` 自动将构建输出放置在 `lib/<tfm>/` 或 `build/<tfm>/` 下。

### 对审查者的影响

在打包的 `build/net462/` 文件夹内类似于以下内容的转发器**不是**“缺失文件”错误，即使源树没有 `buildTransitive/net462/` 目录：

```xml
<!-- 在打包 build/net462/MyAdapter.props 中 -->
<Project>
  <Import Project="$(MSBuildThisFileDirectory)..\..\buildTransitive\net462\MyAdapter.props" />
</Project>
```

在标记 `build/<tfm>/` 或 `buildTransitive/<tfm>/` 文件夹内的未受保护的 `<Import>` 之前：

1. 在项目目录及其直接父目录中查找 `*.nuspec`（不要向上遍历）。阅读每个 `target=…` 的 `<file>`，其 `target` 与导入路径匹配。
2. 阅读 `.csproj` 中的 `<PackagePath>` 元数据 `<None>`/`<Content>` 项目。
3. 只有当目标路径在**源树和**预期的包布局中都缺失时，才标记导入。

另见 `msbuild-antipatterns` AP-13（“NuGet 包转发器”例外）。

## 导入门卫模式

`.targets` 文件确保 `.props` 使用门卫属性导入：

```xml
<!-- Microsoft.Common.props 的末尾 -->
<PropertyGroup>
  <MicrosoftCommonPropsHasBeenImported>true</MicrosoftCommonPropsHasBeenImported>
</PropertyGroup>

<!-- Microsoft.Common.CurrentVersion.targets 的开头 -->
<Import Project="Microsoft.Common.props"
    Condition="'$(MicrosoftCommonPropsHasBeenImported)' != 'true'" />
```

这处理仅导入 `.targets` 的项目。

## 目录.Build 发现

MSBuild 向上遍历目录树以查找最近的 `Directory.Build.props`：

```xml
<_DirectoryBuildPropsBasePath>
  $([MSBuild]::GetDirectoryNameOfFileAbove('$(MSBuildProjectDirectory)', 'Directory.Build.props'))
</_DirectoryBuildPropsBasePath>
```

只有**最近的**文件被发现。嵌套层次结构必须显式导入父级：

```xml
<!-- src/Directory.Build.props -->
<PropertyGroup>
  <_ParentPropsPath>$([MSBuild]::GetPathOfFileAbove('Directory.Build.props', '$(MSBuildThisFileDirectory)../'))</_ParentPropsPath>
</PropertyGroup>
<Import Project="$(_ParentPropsPath)" Condition="'$(_ParentPropsPath)' != ''" />
```

## 创建自己的扩展点

```xml
<!-- MySDK.targets -->
<Project>
  <Import Project="MySDK.props" Condition="'$(MySDKPropsImported)' != 'true'" />

  <PropertyGroup>
    <CustomBeforeMySDK Condition="'$(CustomBeforeMySDK)' == ''">$(MSBuildProjectDirectory)\MySDK.Before.targets</CustomBeforeMySDK>
    <CustomAfterMySDK Condition="'$(CustomAfterMySDK)' == ''">$(MSBuildProjectDirectory)\MySDK.After.targets</CustomAfterMySDK>
  </PropertyGroup>

  <Import Project="$(CustomBeforeMySDK)" Condition="Exists('$(CustomBeforeMySDK)')" />

  <PropertyGroup>
    <MySDKBuildDependsOn>BeforeMySDKBuild;CoreMySDKBuild;AfterMySDKBuild</MySDKBuildDependsOn>
  </PropertyGroup>
  <Target Name="MySDKBuild" DependsOnTargets="$(MySDKBuildDependsOn)" />
  <Target Name="BeforeMySDKBuild" />
  <Target Name="AfterMySDKBuild" />
  <Target Name="CoreMySDKBuild">
    <!-- 实现 -->
  </Target>

  <Import Project="$(CustomAfterMySDK)" Condition="Exists('$(CustomAfterMySDK)')" />
</Project>
```

## 常见陷阱

- **可选导入缺少 `Exists()`** 导致文件缺失时构建失败。**例外**：NuGet 包发布 `build/<tfm>/` 和 `buildTransitive/<tfm>/` 文件夹内的导入是包合同——打包布局保证目标（见“源树与打包布局”）。不要保护它们，也不要标记它们。
- **覆盖 Custom* 属性** 会导致先前钩子丢失。使用 `;` 分隔符追加。
- **NuGet 包文件名与包 ID 不匹配** 会静默跳过导入。
- **嵌套 Directory.Build.props** 而没有父级导入会丢失仓库根设置。
