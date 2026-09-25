# 选择 CopyToOutputDirectory 模式

## 概述

`CopyToOutputDirectory` 元数据（及其发布对应的 `CopyToPublishDirectory`）控制项目（`Content`、`None`、`EmbeddedResource` 或 `Compile`）是否复制到构建输出目录旁边，以及在何种条件下进行复制。选择错误的模式会导致 `bin/` 目录中出现过时文件，或造成不必要的每次构建性能损耗。

自 **MSBuild 17.13 / .NET SDK 9.0.2xx** 起，有四个值：

| 模式 | 在以下情况下复制 | 增量成本 | 典型用途 |
| --- | --- | --- | --- |
| `Never`（默认） | 从不 | 无 | 运行时不需要的文件 |
| `PreserveNewest` | 源文件比目标文件**新**（或目标文件缺失） | 低廉（时间戳检查） | 常见情况——你编辑的源文件 |
| `Always` | **每次构建**，无条件 | 昂贵——即使在无操作构建中也复制 | 遗留解决方案；避免（见下文） |
| `IfDifferent` | 源文件与目标文件**不同**（无论新或旧，或大小不同，或目标文件缺失） | 低廉（时间戳+大小检查） | 构建之间目标文件可能被修改 |

```xml
<ItemGroup>
  <None Include="appsettings.json" CopyToOutputDirectory="PreserveNewest" />
  <None Include="testdata\seed.db"  CopyToOutputDirectory="IfDifferent" />
</ItemGroup>
```

你可以使用上面显示的属性形式，或子元素形式：

```xml
<None Include="testdata\seed.db">
  <CopyToOutputDirectory>IfDifferent</CopyToOutputDirectory>
</None>
```

## 为什么 `Always` 通常不是正确的选择

`Always` 在**每次**构建时重新复制文件，包括其他情况下干净的增量/无操作构建。在包含许多或大内容文件的项目中，这是一个可测量的、重复的成本，并且是“为什么我的无操作构建不是即时？”报告的常见原因。

历史上 `Always` 是处理特定场景的唯一方法：**目标文件在构建之间可以改变**——例如 SQLite 数据库、存储/状态文件，或测试运行时修改的配置文件。使用 `PreserveNewest` 时，如果目标被修改（使其时间戳*比源文件新*），MSBuild 将*不会*恢复原始源文件，因为源文件不再新。人们使用 `Always` 来强制文件回到已知良好状态——作为副作用，每次构建都支付复制成本。

## `IfDifferent`：双向不同时复制

`IfDifferent` 是针对该场景的针对性修复。它会在 MSBuild 认为两个文件**不同**时复制源文件到目标文件——无论源文件比目标文件新*或*旧，无论大小是否不同，或目标文件缺失——并且在目标文件按 MSBuild 启发式方法未改变时跳过复制。

底层 `_CopyDifferingSourceItemsToOutputDirectory` 目标使用带有 `SkipUnchangedFiles="true"` 的 `Copy` 任务。这个“未改变”检查是一个**启发式方法**：它仅比较**最后写入时间戳和文件大小**——而不是内容哈希——因此，如果目标文件被编辑为与源文件相同的大小和时间戳，则被视为未改变，并且*不会*重新复制。实际上，这会在下一次构建中将已修改的目标恢复到源版本（这就是人们使用 `Always` 的原因），同时避免了无条件每次构建的复制。

在以下情况下使用 `IfDifferent`：

- 测试运行或应用程序本身写入复制的文件（数据库、缓存、状态/存储文件、可编辑配置），并且你希望每次构建都将其重置为源版本。
- 你使用 `Always` 仅仅是为了“保持输出与源同步”机制，而不是因为你确实需要在每个单一构建上都进行复制。

```xml
<ItemGroup>
  <!-- 每当测试用例数据库偏离源副本时重置，但不要在每次无操作构建中支付复制成本。 -->
  <None Include="fixtures\catalog.db" CopyToOutputDirectory="IfDifferent" />
</ItemGroup>
```

## 使用 `$(SkipUnchangedFilesOnCopyAlways)` 全局软化 `Always`

如果你有一个包含大量 `CopyToOutputDirectory="Always"` 项目的现有代码库，并且希望在不编辑每个项目的情况下获得性能收益，请设置属性：

```xml
<PropertyGroup>
  <SkipUnchangedFilesOnCopyAlways>true</SkipUnchangedFilesOnCopyAlways>
</PropertyGroup>
```

这会使 `_CopyOutOfDateSourceItemsToOutputDirectoryAlways` 目标将其 `Copy` 任务传递 `SkipUnchangedFiles="true"`，因此 `Always` 项目仅在它们实际不同时才被复制——实际上为 `Always` 提供了与 `IfDifferent` 相同的跳过未改变行为。

- 默认值为 `false` 以向后兼容（经典的 `Always` = 每次构建都复制）。
- 在 `Directory.Build.props` 中设置它，以一次性为整个代码库启用。
- 当你可以将单个项目转换为 `IfDifferent` 时，优先选择；使用此属性时，当更实际进行批量非侵入式启用时。

## 模式如何在构建中流转

`GetCopyToOutputDirectoryItems` 按其 `CopyToOutputDirectory` 值将每个项目分组。三个复制目标随后作为 `_CopySourceItemsToOutputDirectory`（本身由 `CopyFilesToOutputDirectory` 调用）的依赖项执行工作：

- `_CopyOutOfDateSourceItemsToOutputDirectory` — `PreserveNewest` 项目（通过 `Inputs`/`Outputs` 时间戳比较进行增量）。
- `_CopyOutOfDateSourceItemsToOutputDirectoryAlways` — `Always` 项目（除非 `$(SkipUnchangedFilesOnCopyAlways)` 为 `true`，否则无条件复制）。
- `_CopyDifferingSourceItemsToOutputDirectory` — `IfDifferent` 项目（`SkipUnchangedFiles="true"`）。

所有复制的文件都注册在 `FileWrites` 中，因此 `dotnet clean` 会删除它们。

**传递复制**：标记为 `Always`、`PreserveNewest` 或 `IfDifferent` 的项目也通过 `ProjectReference`（通过 `_CopyToOutputDirectoryTransitiveItems`）流到引用的项目。`Never` 项目不会。`IfDifferent` 与 `Always`/`PreserveNewest` 一起参与 ClickOnce 发布项目收集。

## 版本要求

`IfDifferent` 和 `$(SkipUnchangedFilesOnCopyAlways)` 需要 **MSBuild 17.13 或更高版本**（**.NET SDK 9.0.2xx+ / Visual Studio 2022 17.13+**）。在旧工具集上，该值不被识别：它不会匹配常见目标中的 `Always`/`PreserveNewest`/`IfDifferent` 条件，因此该项目将静默**不被复制**。如果你必须支持旧 SDK，请基于工具集锁定使用，或通过 `global.json` 要求最低 SDK。

## 快速决策指南

- 运行时不需要文件 → `Never`（或省略——它是默认值）。
- 你编辑的普通源文件 → `PreserveNewest`。
- 构建之间目标文件被修改且必须重置为源 → `IfDifferent`。
- 你确实需要在字面上每次构建都获得一个新鲜副本 → `Always`（罕见）。
- 被大量遗留 `Always` 卡住且希望在不编辑的情况下获得性能提升 → 保持 `Always` 但设置 `$(SkipUnchangedFilesOnCopyAlways)=true`。
