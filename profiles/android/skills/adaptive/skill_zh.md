## 前置条件

应用必须：

- 对所有屏幕使用 Compose。如果仍然使用 Fragments 或 Views，建议使用 XML to Compose 技巧迁移这些屏幕。
- 使用 Jetpack Navigation 3。如果没有，建议使用 Navigation 3 技巧迁移应用。

## 使应用自适应的工作流程

要使应用自适应，请按照以下步骤或根据任务需求选择其中一部分步骤进行操作。

- 第 1 步：验证当前 UI
- 第 2 步：使导航栏自适应
- 第 3 步：添加多面板布局
- 第 4 步：通过更改列数使垂直列表自适应
- 第 5 步：滚动时隐藏应用栏

## 第 1 步。验证当前 UI

确保存在截图测试，以验证在不同设备形态上的当前 UI。如果没有，请添加 [Compose 预览截图测试工具](references/android/develop/ui/compose/tooling/debug.md)。使用以下注解为所有主要设备形态创建预览。例如：


```kotlin
@Preview(name = "Phone", device = Devices.PHONE, showBackground = true)
@Preview(name = "Foldable", device = Devices.FOLDABLE, showBackground = true)
@Preview(name = "Tablet", device = Devices.TABLET, showBackground = true)
@Preview(name = "Desktop", device = Devices.DESKTOP, showBackground = true)
annotation class FormFactorPreviews

@PreviewTest
@FormFactorPreviews
@Composable
fun FeedScreenPreview() {
    SnippetsTheme {
        Box {
            Text("My Screen")
        }
    }
}
```

<br />

## 第 2 步。使导航栏自适应

底部导航栏在用户手持手机处于横屏模式时针对触摸输入进行了优化。在较大的手持设备（如平板电脑和未展开的折叠屏设备）上，导航区域必须从屏幕边缘（导航轨道）即可访问。

如果您需要为内容提供更多的屏幕空间，请隐藏导航区域。例如：

- 当用户向下滚动时隐藏导航栏，并在用户向上滚动时再次显示它。假设当用户向下滚动时，他们正在消费内容，但在向上滚动时，他们试图从该内容中导航。
- 当导航区域的内容令人分心时隐藏它。例如，在相机预览中或显示全屏照片时。

当详细屏幕在移动设备上以全屏模式显示时，在较大屏幕上必须禁用全屏模式。

迁移步骤：

- 定位现有的导航栏。
- 将每个项目转换为 `NavigationSuiteItem`。
- 确定导航栏的可见性是否发生变化。例如，如果它被 `AnimatedContent` 或 `AnimatedVisibility` composable 包裹。如果是，请遵循“控制导航区域可见性”中的指导。
- 使用 Material 3 自适应布局库中的 `NavigationSuiteScaffold` 替换包含导航栏的容器（通常是 `Scaffold`）。
- 使用 `NavigationSuiteScaffold` 的 `navigationItems` 参数提供导航项。

### 第 2.1. 控制导航区域可见性

如果导航栏的可见性发生变化（在某些情况下或某些屏幕上隐藏），则必须在自适应导航区域中保持此行为。这是通过使用 `NavigationSuiteScaffold` 的 `state` 参数完成的。

迁移步骤：

- 确定导航栏在哪些情况下被隐藏。这通常是通过一个用于可见性的布尔变量完成的。使用 `isNavBarVisible` 或 `shouldShowNavBar` 作为变量名。
- 使用 `rememberNavigationSuiteScaffoldState()` 创建一个 `NavigationSuiteScaffoldState` 实例，并将其传递给 `NavigationSuiteScaffold`。
- 当导航区域可见性发生变化时，使用 `LaunchedEffect` 调用 `NavigationSuiteScaffoldState` 上的 `show` 或 `hide`。

例如：


```kotlin
// 将此变量传递给需要控制导航区域可见性的任何 composable
var isNavBarVisible by remember { mutableStateOf(true) }
val scaffoldVisibilityState = rememberNavigationSuiteScaffoldState()

NavigationSuiteScaffold(
    navigationSuiteItems = navItems,
    state = scaffoldVisibilityState
) {
    // 主内容
}

LaunchedEffect(isNavBarVisible){
    if (isNavBarVisible) {
        scaffoldVisibilityState.show()
    } else {
        scaffoldVisibilityState.hide()
    }
}
```

<br />

## 第 3 步。使用 Navigation 3 Scenes 添加多面板布局

分析代码库，查找相关屏幕——在一个屏幕上点击某物会打开另一个显示与第一个屏幕相关的信息的屏幕。有两种标准的屏幕关系：列表-详细和辅助面板。

**重要提示**：您必须使用 Navigation 3 的 `SceneStrategy` 方法来实现多面板布局。不要使用 `ListDetailPaneScaffold` 或 `SupportingPaneScaffold`。

### 第 3.1. 列表-详细

#### 确定列表和详细屏幕

列表-详细布局显示一个项目列表（这是列表屏幕），点击项目会打开一个新屏幕，显示该项目的更多详细信息（详细屏幕）。

典型用法包括生产力应用，如电子邮件、笔记和消息。

除非明确要求，否则在详细内容需要大量屏幕空间时（例如，受益于全屏呈现的图像或媒体）避免使用此模式。

#### 添加 Material 列表-详细 SceneStrategy

- 添加 `androidx.compose.material3.adaptive:adaptive-navigation3` 库
- 使用 `rememberListDetailSceneStrategy` 创建一个 `androidx.compose.material3.adaptive.navigation3.ListDetailSceneStrategy`
- 使用 `NavDisplay` 的 `sceneStrategies` 参数将 `ListDetailSceneStrategy` 传递给 `NavDisplay`

#### 使用元数据识别列表和详细屏幕

- 使用 `ListDetailSceneStrategy.listPane(detailPlaceholder = { <placeholder composable> })` 为列表条目添加元数据，使用 `entry(metadata = ...)` 或 `NavEntry(metadata = ...)`。
- 使用 `detailPlaceholder` 参数在详细屏幕上未选择列表项时添加占位符。
- 使用 `ListDetailSceneStrategy.detailPane()` 为详细条目添加元数据。

#### 重要注意事项

- 当详细屏幕在移动设备上以全屏模式显示其内容（内容填满整个屏幕，条或轨道被隐藏）时，如果它是列表-详细布局的一部分，则必须禁用全屏模式。
- 在列表-详细布局上，详细屏幕不应显示返回箭头。

有关参考实现，请查看 [Nav3 **Material** 列表详细配方](references/android/guide/navigation/navigation-3/recipes/material-listdetail.md)。

### 第 3.2. 辅助面板

识别辅助面板屏幕，其中主屏幕显示单个项目，选择该项目会打开一个“辅助屏幕”以显示更多详细信息。辅助屏幕补充主屏幕，并在辅助面板中显示。

#### 添加 Material 辅助面板 `SceneStrategy`

- 如果尚未添加，请添加 `androidx.compose.material3.adaptive:adaptive-navigation3` 库
- 使用 `rememberSupportingPaneSceneStrategy` 创建一个 `androidx.compose.material3.adaptive.navigation3.SupportingPaneSceneStrategy`
- 使用 `NavDisplay` 的 `sceneStrategies` 参数将 `SupportingPaneSceneStrategy` 传递给 `NavDisplay`

#### 使用元数据识别主屏幕和辅助屏幕

- 使用 `entry(metadata = ...)` 或 `NavEntry(metadata = ...)` 为主条目添加元数据，使用 `SupportingPaneSceneStrategy.mainPane()`。
- 使用 `SupportingPaneSceneStrategy.supportingPane()` 为辅助条目添加元数据。

### 第 3.3. 运行截图测试

如果您进行了更改，请记录新的参考文件。要求用户视觉验证新布局是否正确。

## 第 4 步。通过更改列数使垂直列表自适应

### 第 4.1. 使懒加载列表自适应

查找以下垂直列表 composable：`LazyColumn`, `LazyVerticalGrid`, `LazyVerticalStaggeredGrid`。

迁移步骤：

- 选择一个合适的 dp 最小宽度作为列。项目必须在此宽度下对用户清晰可见。
- 对于 `LazyColumn`：更改为 `LazyVerticalGrid` 并遵循后面的说明
- 对于 `LazyVerticalGrid`：将 `columns` 参数更改为使用 `GridCells.Adaptive(<width>.dp)`
- 对于 `LazyVerticalStaggeredGrid`：将 `columns` 参数更改为使用 `StaggeredGridCells.Adaptive(<width>.dp)`

### 第 4.2. 将非懒加载列表迁移到 Grid

**警告**：Grid 是从 Compose 1.11.0-beta01 开始提供的实验性 API。请与用户确认他们是否愿意在代码库中使用实验性 API。

查找任何包含多个相同类型项目的 `Column` 并将其替换为 `Grid`。不要将其替换为 `LazyVerticalGrid` 或任何其他懒加载布局。不要将 `Grid` 放在现有的 `Column` 内。完全替换它。

`Grid` 通过向其 `config` 参数提供一个 lambda（`GridConfigurationScope` 上的扩展函数）进行配置。在 lambda 内，`constraints` 提供了网格容器的最小和最大尺寸，可用于根据可用大小更改行和列的数量。例如，以下代码配置 `Grid`，使得当可用宽度为：

- 小于 800dp 时，使用 2x4 网格
- 800dp 或更多时，使用 4x2 网格


```kotlin
Grid(
    config = {
        val maxWidthDp = constraints.maxWidth.toDp()
        val (cols, rows) = if (maxWidthDp < 800.dp){
            2 to 4
        } else{
            4 to 2
        }

        val gapSizeDp = 8.dp
        val cellSize = ((maxWidthDp - (gapSizeDp * (cols - 1))) / cols).coerceAtLeast(0.dp)
        repeat(cols) { column(cellSize) }
        repeat(rows) { row(cellSize) }
        gap(gapSizeDp)
    }
) { /** items **/ }
```

<br />

`Grid` 是一个实验性 API，因此将 `@OptIn(ExperimentalGridApi::class)` 注解添加到使用它的任何函数中。

## 第 5 步：滚动时隐藏应用栏

在一个具有多个顶级目的地的应用中，每个屏幕都必须独立管理其应用栏状态。有两种主要的滚动行为：

- `exitUntilCollapsedScrollBehavior`：向下滚动时隐藏，在向上滚动时保持隐藏，直到达到顶部（0 偏移量）。
- `enterAlwaysScrollBehavior`：向下滚动时隐藏，向上滚动时立即显示。

## 最后一步：构建和测试

构建应用并运行本地测试。如果项目有截图测试，请运行它们，但**不要**更新参考图像。提示用户在查看截图差异后进行此操作。

## 实验性自适应 API 的附加文档

从 Compose 1.11.0-beta01 开始，以下 API 可用。

### FlexBox

检查 FlexBox 文档：

- [概述](references/android/develop/ui/compose/layouts/adaptive/flexbox/index.md)
- [入门 - 设置](references/android/develop/ui/compose/layouts/adaptive/flexbox/get-started.md)
- [设置容器行为](references/android/develop/ui/compose/layouts/adaptive/flexbox/container-behavior.md)
- [设置项行为](references/android/develop/ui/compose/layouts/adaptive/flexbox/item-behavior.md)

## MediaQuery

当您需要查询设备的屏幕尺寸、指针精度、键盘类型、是否具有相机或麦克风以及其他设备功能时，请检查 [MediaQuery 文档](references/android/develop/ui/compose/layouts/adaptive/mediaquery/index.md)。

## Grid

当您需要以网格布局显示固定数量的项目时，请检查 Grid 文档：

- [概述](references/android/develop/ui/compose/layouts/adaptive/grid/index.md)
- [入门 - 设置](references/android/develop/ui/compose/layouts/adaptive/grid/get-started.md)
- [设置容器属性](references/android/develop/ui/compose/layouts/adaptive/grid/container-properties.md)
- [设置项属性](references/android/develop/ui/compose/layouts/adaptive/grid/item-properties.md)
