# MSBuild 属性模式

MSBuild 存储库中的规范属性定义和操作模式。

## 条件默认值 — 基础模式

仅在属性**尚未设置**时设置属性，允许调用者覆盖：

```xml
<PropertyGroup>
  <Configuration Condition="'$(Configuration)' == ''">Debug</Configuration>
  <Platform Condition="'$(Platform)' == ''">AnyCPU</Platform>
  <BuildInParallel Condition="'$(BuildInParallel)' == ''">true</BuildInParallel>
</PropertyGroup>
```

### 规则

- 始终对两边加引号：`'$(Prop)' == ''`
- 在 `.props` 中：创建可覆盖的默认值。在 `.targets` 中：创建回退值。
- 没有条件的属性**不能被**早先的导入覆盖。

## 嵌套条件组

在共享条件下分组相关属性：

```xml
<PropertyGroup Condition="$(TargetFramework.StartsWith('net4'))">
  <DefineConstants>$(DefineConstants);FEATURE_APARTMENT_STATE</DefineConstants>
  <DefineConstants>$(DefineConstants);FEATURE_APM</DefineConstants>
  <FeatureAppDomain>true</FeatureAppDomain>
</PropertyGroup>

<PropertyGroup Condition="'$([MSBuild]::GetTargetFrameworkIdentifier('$(TargetFramework)'))' == '.NETCoreApp'">
  <NetCoreBuild>true</NetCoreBuild>
  <DefineConstants>$(DefineConstants);RUNTIME_TYPE_NETCORE</DefineConstants>
</PropertyGroup>
```

使用外部的 `Condition` 在 `PropertyGroup` 上，以避免在每个属性上重复相同的条件。

> **警告**：在单目标项目中的 `.props` 文件中，`$(TargetFramework)` 在项目主体评估之前为空。将 `TargetFramework`-条件化的属性组放在 `.targets` 文件（或项目文件本身）中，其中值始终可用。

## 组合 — 分号连接

存储列表的属性使用分号。追加时始终包含现有值：

```xml
<PropertyGroup>
  <DefineConstants>$(DefineConstants);MY_FEATURE</DefineConstants>
  <NoWarn>$(NoWarn);NU5131;IDE0005</NoWarn>
  <LibraryTargetFrameworks>$(FullFrameworkTFM);$(LatestDotNetCoreForMSBuild);netstandard2.0</LibraryTargetFrameworks>
</PropertyGroup>
```

## 路径规范化与尾部斜杠

```xml
<!-- 确保目录有尾部斜杠 -->
<PropertyGroup>
  <OutDir Condition="'$(OutDir)' != '' and !HasTrailingSlash('$(OutDir)')">$(OutDir)\</OutDir>
</PropertyGroup>

<!-- 跨平台规范化路径 -->
<PropertyGroup>
  <TargetRefPath>$([MSBuild]::NormalizePath('$(TargetDir)', 'ref', '$(TargetFileName)'))</TargetRefPath>
</PropertyGroup>

<!-- 将相对路径转换为绝对路径 -->
<PropertyGroup>
  <MSBuildProjectExtensionsPath
      Condition="'$([System.IO.Path]::IsPathRooted('$(MSBuildProjectExtensionsPath)'))' == 'false'">
    $([System.IO.Path]::Combine('$(MSBuildProjectDirectory)', '$(MSBuildProjectExtensionsPath)'))
  </MSBuildProjectExtensionsPath>
</PropertyGroup>
```

### 推荐的路径函数

| 函数 | 目的 |
|---|---|
| `$([MSBuild]::NormalizePath(...))` | 合并和规范化（跨平台） |
| `$([System.IO.Path]::Combine(...))` | 合并路径段 |
| `$([System.IO.Path]::IsPathRooted(...))` | 检查是否为绝对路径 |
| `HasTrailingSlash(...)` | 检查尾部斜杠 |
| `$([MSBuild]::GetDirectoryNameOfFileAbove(...))` | 向上遍历目录树 |
| `$(MSBuildThisFileDirectory)` | 当前文件的目录 |

## 目标框架检测辅助工具

```xml
<!-- 获取 TFM 标识符 -->
<PropertyGroup Condition="'$([MSBuild]::GetTargetFrameworkIdentifier('$(TargetFramework)'))' == '.NETCoreApp'">
  <NetCoreBuild>true</NetCoreBuild>
</PropertyGroup>

<!-- 检查 TFM 兼容性 -->
<PropertyGroup Condition="$([MSBuild]::IsTargetFrameworkCompatible('$(TargetFramework)', 'net472'))">
  <UseFrozenVersions>true</UseFrozenVersions>
</PropertyGroup>

<!-- 操作系统检测 -->
<PropertyGroup Condition="$([MSBuild]::IsOSPlatform('windows'))">
  <DefineConstants>$(DefineConstants);TEST_ISWINDOWS</DefineConstants>
</PropertyGroup>
```

## 保护属性

标记文件已被导入，以防止重复导入：

```xml
<!-- 在 MySDK.props 的末尾 -->
<PropertyGroup>
  <MySDKPropsImported>true</MySDKPropsImported>
</PropertyGroup>

<!-- 在 MySDK.targets 的开头 -->
<Import Project="MySDK.props" Condition="'$(MySDKPropsImported)' != 'true'" />
```

## 通过 MSBuild 版本进行功能开关

```xml
<PropertyGroup Condition="$([MSBuild]::AreFeaturesEnabled('17.10'))">
  <UseNewBehavior>true</UseNewBehavior>
</PropertyGroup>
```

## 回退链

首先通过主源设置，然后回退：

```xml
<PropertyGroup>
  <TlbExpPath>$([Microsoft.Build.Utilities.ToolLocationHelper]::GetPathToDotNetFrameworkSdkFile('tlbexp.exe'))</TlbExpPath>
  <TlbExpPath Condition="'$(TlbExpPath)' == ''">$(_NetFxToolsDir)TlbExp.exe</TlbExpPath>
</PropertyGroup>
```

## 最后写入者胜出 — 评估顺序

MSBuild 从上到下评估属性。最后一个赋值生效：

```xml
<!-- 文件 1（第一个导入） -->
<MyProp>value1</MyProp>        <!-- 设置为 value1 -->
<!-- 文件 2（第二个导入） -->
<MyProp>value2</MyProp>        <!-- 覆盖为 value2 -->
<!-- 文件 3（第三个导入） -->
<MyProp Condition="'$(MyProp)' == ''">value3</MyProp>  <!-- 未设置 — 已经是 value2 -->
```

`.targets` 中的属性（导入较晚）会覆盖 `.props` 中的属性（导入较早）和项目文件中的属性。

## 常见陷阱

- **未加引号的条件** (`$(X)==true`) 在属性为空时失败。始终对两边加引号。
- **覆盖 DefineConstants** (`<DefineConstants>MY_CONST</DefineConstants>`) 会丢弃所有先前的常量。始终使用 `$(DefineConstants);` 追加。
- **硬编码的绝对路径** 会破坏可移植性。使用 `$(MSBuildThisFileDirectory)` 或 `$([MSBuild]::NormalizePath(...))`。
- **默认值缺少 `Condition`** 使属性不可覆盖。为预期为默认值的属性添加 `Condition="'$(Prop)' == ''"`。
