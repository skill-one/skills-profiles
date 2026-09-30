---
name: adaptive
description: 创建或更新应用程序UI的说明，使其能够适应不同的Android设备，包括手机、平板电脑、折叠屏、笔记本电脑、台式机、电视、汽车和XR设备。它包括如何使用Compose MediaQuery API处理不同的窗口尺寸、指向设备（如鼠标）和文本输入设备（如键盘）。它还涵盖了使用Navigation3 Scenes的多窗格布局、具有不同目标尺寸的自适应UI组件（如按钮）以及使用Compose Grid和FlexBox API的自适应布局（包括导航区域——导航轨道和导航栏）。
---

## 前置条件

应用必须：

- 对所有界面使用 Compose。如果仍在使用 Fragments 或 Views，建议使用 XML to Compose 技巧迁移这些界面。
- 使用 Jetpack Navigation 3。如果未使用，建议使用 Navigation 3 技巧迁移应用。

## 使应用自适应的工作流程

要使应用自适应，请按照以下步骤或根据任务需求选择其中部分步骤进行操作。

- 第 1 步：验证当前 UI
- 第 2 步：使导航栏自适应
- 第 3 步：添加多面板布局
- 第 4 步：通过更改列数使垂直列表自适应
- 第 5 步：滚动时隐藏应用栏

## 第 1 步。验证当前 UI

确保存在截图测试以验证不同设备形态上的当前 UI。如果不存在，请添加 [Compose 预览截图测试工具](references/android/develop/ui/compose/tooling/debug.md)。使用以下注解为所有主要设备形态创建预览。例如：

```kotlin
@Preview(name = "手机", device = Devices.PHONE, showBackground = true)
@Preview(name = "折叠屏", device = Devices.FOLDABLE, showBackground = true)
@Preview(name = "平板", device = Devices.TABLET, showBackground = true)
@Preview(name = "桌面", device = Devices.DESKTOP, showBackground = true)
annotation class FormFactorPreviews

@PreviewTest
@FormFactorPreviews
@Composable
fun FeedScreenPreview() {
    SnippetsTheme {
        Box {
            Text("我的界面")
        }
    }
}
```

<br />

## 第 2 步。使导航栏自适应

底部导航栏在用户手持手机横屏时针对触摸输入进行了优化。在较大屏幕手持设备（如平板和展开的折叠屏）上，导航区域必须从屏幕边缘（导航轨道）访问。

如果您需要为内容提供更多屏幕空间，请隐藏导航区域。示例包括：

- 当用户向下滚动时隐藏导航栏，并在用户向上滚动时再次显示它。假设当用户向下滚动时，他们正在消费内容，但在向上滚动时，他们试图离开该内容。
- 当导航区域的内容令人分心时隐藏导航区域。例如，在相机预览中或显示全屏照片时。

当详细界面在移动设备上以全屏模式显示时，在较大屏幕上必须禁用全屏模式。

迁移步骤：

- 定位现有的导航栏。
- 将每个项目转换为 `NavigationSuiteItem`。
- 确定导航栏的可见性是否发生变化。例如，如果它被 `AnimatedContent` 或 `AnimatedVisibility` composable 包裹。如果是，请遵循“控制导航区域可见性”中的指导。
- 使用 Material 3 自适应布局库中的 `NavigationSuiteScaffold` 替换包含导航栏的容器（通常是 `Scaffold`）。
- 使用 `NavigationSuiteScaffold` 的 `navigationItems` 参数提供导航项。

### 第 2.1. 控制导航区域可见性

如果导航栏的可见性发生变化（在某些情况下或某些屏幕上隐藏），则必须在自适应导航区域中保持此行为。这是通过使用 `NavigationSuiteScaffold` 的 `state` 参数完成的。

迁移步骤：

- 确定导航栏在哪些情况下被隐藏。这通常是通过一个布尔变量来完成的，用于可见性。使用 `isNavBarVisible` 或 `shouldShowNavBar` 作为变量名。
- 使用 `rememberNavigationSuiteScaffoldState()` 创建一个 `NavigationSuiteScaffoldState` 实例，并将其传递给 `NavigationSuiteScaffold`。
- 当导航区域可见性发生变化时，使用 `LaunchedEffect` 调用 `NavigationSuiteScaffoldState` 的 `show` 或 `hide`。

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

分析代码库，查找相关界面——在某个界面上点击某物会打开另一个显示与第一个界面相关信息的界面。有两种标准的界面关系：列表-详细和辅助面板。

**重要提示**：您必须使用 Navigation 3 的 `SceneStrategy` 方法来实现多面板布局。不要使用 `ListDetailPaneScaffold` 或 `SupportingPaneScaffold`。

### 第 3.1. 列表-详细

#### 确定列表和详细界面

列表-详细布局显示一个项目列表（这是列表界面），点击项目会打开一个新界面，显示该项目的更多详细信息（详细界面）。

典型用法包括生产力应用，如电子邮件、笔记和消息应用。

除非明确要求，否则当详细内容需要大量屏幕空间时（例如，受益于全屏展示的图像或媒体），请避免使用此模式。

#### 添加 Material 列表-详细 SceneStrategy

- 添加 `androidx.compose.material3.adaptive:adaptive-navigation3` 库
- 使用 `rememberListDetailSceneStrategy` 创建一个 `androidx.compose.material3.adaptive.navigation3.ListDetailSceneStrategy`
- 使用 `NavDisplay` 的 `sceneStrategies` 参数传递 `ListDetailSceneStrategy`

#### 使用元数据识别列表和详细界面

- 使用 `entry(metadata = ...)` 或 `NavEntry(metadata = ...)` 向列表条目添加元数据，使用 `ListDetailSceneStrategy.listPane(detailPlaceholder = {
  <placeholder composable> })`。
- 使用 `detailPlaceholder` 参数在详细界面上添加占位符，当没有选择列表项时显示。
- 使用 `ListDetailSceneStrategy.detailPane()` 向详细条目添加元数据。

#### 重要注意事项

- 当详细界面在移动设备上以全屏模式显示其内容时（内容填满整个屏幕，栏或轨道被隐藏），如果它是列表-详细布局的一部分，则必须禁用全屏模式。
- 在列表-详细布局上，详细界面不应显示返回箭头。

有关参考实现，请查看 [Nav3 **Material** 列表详细配方](references/android/guide/navigation/navigation-3/recipes/material-listdetail.md)。

### 第 3.2. 辅助面板

识别辅助面板界面，在这些界面上，主界面显示单个项目，选择该项目会打开一个“辅助界面”以显示更多详细信息。辅助界面补充主界面，并在辅助面板中显示。

#### 添加 Material 辅助面板 `SceneStrategy`

- 如果尚未添加，请添加 `androidx.compose.material3.adaptive:adaptive-navigation3` 库
- 使用 `rememberSupportingPaneSceneStrategy` 创建一个 `androidx.compose.material3.adaptive.navigation3.SupportingPaneSceneStrategy`
- 使用 `NavDisplay` 的 `sceneStrategies` 参数传递 `SupportingPaneSceneStrategy`

#### 使用元数据识别主界面和辅助界面

- 使用 `entry(metadata = ...)` 或 `NavEntry(metadata = ...)` 向主条目添加元数据，使用 `SupportingPaneSceneStrategy.mainPane()`
- 使用 `SupportingPaneSceneStrategy.supportingPane()` 向辅助条目添加元数据

### 第 3.3. 运行截图测试

如果您进行了更改，请记录新的参考文件。要求用户通过视觉验证新布局是否正确。

## 第 4 步。通过更改列数使垂直列表自适应

### 第 4.1. 使懒列表自适应

查找以下垂直列表 composable：`LazyColumn`、`LazyVerticalGrid`、`LazyVerticalStaggeredGrid`。

迁移步骤：

- 选择一个合适的 dp 最小宽度作为列。项目必须在此宽度下对用户清晰可见。
- 对于 `LazyColumn`：转换为 `LazyVerticalGrid` 并遵循后续说明
- 对于 `LazyVerticalGrid`：将 `columns` 参数更改为使用 `GridCells.Adaptive(<width>.dp)`
- 对于 `LazyVerticalStaggeredGrid`：将 `columns` 参数更改为使用 `StaggeredGridCells.Adaptive(<width>.dp)`

### 第 4.2. 将非懒列表迁移到 Grid

**警告**：Grid 是从 Compose 1.11.0-beta01 开始提供的实验性 API。请确认用户是否愿意在其代码库中使用实验性 API。

查找任何包含多个相同类型项目的 `Column` 并将其替换为 `Grid`。不要将其替换为 `LazyVerticalGrid` 或任何其他懒布局。不要将 `Grid` 放置在现有的 `Column` 内。完全替换它。

`Grid` 通过向其 `config` 参数提供 lambda（`GridConfigurationScope` 上的扩展函数）进行配置。在 lambda 内，`constraints` 提供网格容器的最小和最大尺寸，可用于根据可用大小更改行和列的数量。例如，以下代码配置 `Grid`，使得当可用宽度为：

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

`Grid` 是一个实验性 API，因此请将 `@OptIn(ExperimentalGridApi::class)` 注解添加到使用它的任何函数中。

## 第 5 步：滚动时隐藏应用栏

在具有多个顶级目的地的应用中，每个界面必须独立管理其应用栏状态。有两种主要的滚动行为：

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
- [设置项目行为](references/android/develop/ui/compose/layouts/adaptive/flexbox/item-behavior.md)

### MediaQuery

当您需要查询设备的屏幕尺寸、指针精度、键盘类型、是否具有相机或麦克风以及其他设备功能时，请检查 [MediaQuery 文档](references/android/develop/ui/compose/layouts/adaptive/mediaquery/index.md)。

### Grid

当您需要在网格布局中显示固定数量的项目时，请检查 Grid 文档：

- [概述](references/android/develop/ui/compose/layouts/adaptive/grid/index.md)
- [入门 - 设置](references/android/develop/ui/compose/layouts/adaptive/grid/get-started.md)
- [设置容器属性](references/android/develop/ui/compose/layouts/adaptive/grid/container-properties.md)
- [设置项目属性](references/android/develop/ui/compose/layouts/adaptive/grid/item-properties.md)
