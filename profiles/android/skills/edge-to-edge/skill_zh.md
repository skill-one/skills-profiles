## 前置条件

- 项目**必须**使用 Android Jetpack Compose。
- 项目**必须**针对 SDK 35 或更高版本。如果 SDK 版本低于 35，请将 SDK 提升至 35。

## 第 1 步：规划

1. 定位并分析所有 Activity 类，以检测哪些类已支持边缘到边缘（edge-to-edge）。对于没有边缘到边缘支持的 Activity，计划将其改为边缘到边缘。
2. 在每个 Activity 中，定位并分析所有列表和 FAB 组件，以检测哪些组件已支持边缘到边缘。对于没有边缘到边缘支持的组件，计划将其改为边缘到边缘。
3. 在每个 Activity 中，扫描 `TextField`、`OutlinedTextField` 或 `BasicTextField`。如果找到，则**必须**按照本技巧的 IME 部分验证输入法编辑器（IME）是否隐藏了输入字段。

## 第 2 步：添加边缘到边缘支持

1. 在每个未调用 `enableEdgeToEdge` 的 Activity 的 `onCreate` 中，在 `setContent` 之前添加 `enableEdgeToEdge`。
2. 在 AndroidManifest.xml 中为所有使用软键盘的 Activity 添加 `android:windowSoftInputMode="adjustResize"`。

## 第 3 步：应用内边距

- 应用**必须**应用系统内边距，或对齐标尺，以确保关键 UI 保持可点击。选择一种方法以避免双重内边距：

  1. **首选：** 当可用时，使用 `Scaffold` 并将 `PaddingValues` 传递给内容 lambda。

  ```kotlin
  Scaffold { innerPadding ->
      // innerPadding 考虑了系统栏和任何 Scaffold 组件
      LazyColumn(
          modifier = Modifier
              .fillMaxSize()
              .consumeWindowInsets(innerPadding),
          contentPadding = innerPadding
      ) { /* 内容 */ }
  }
  ```

  <br />

  1. **首选：** 当可用时，使用材料组件中的自动内边距处理或内边距修饰符。

     - Material 3 组件管理其自身组件的安全区域，包括：
       - `TopAppBar`
       - `SmallTopAppBar`
       - `CenterAlignedTopAppBar`
       - `MediumTopAppBar`
       - `LargeTopAppBar`
       - `BottomAppBar`
       - `ModalDrawerSheet`
       - `DismissibleDrawerSheet`
       - `PermanentDrawerSheet`
       - `ModalBottomSheet`
       - `NavigationBar`
       - `NavigationRail`
     - 对于 Material 2 组件，使用 `windowInsets` 参数手动为 `BottomAppBar`、`TopAppBar` 和 `BottomNavigation` 应用内边距。**不要**将内边距应用于父容器；相反，将内边距直接传递给 App Bar 组件。将内边距应用于父容器会阻止 App Bar 背景绘制到系统栏区域。例如，对于 `TopAppBar`，选择以下选项之一：
       1. **首选：** `TopAppBar(windowInsets = AppBarDefaults.topAppBarWindowInsets)`
       2. `TopAppBar(windowInsets = WindowInsets.systemBars.exclude(WindowInsets.navigationBars))`
       3. `TopAppBar(windowInsets = WindowInsets.systemBars.add(WindowInsets.captionBar))`
  2. 对于 Scaffold 外部的组件，使用内边距修饰符，例如 `Modifier.safeDrawingPadding()` 或 `Modifier.windowInsetsPadding(WindowInsets.safeDrawing)`。

     ```kotlin
     Box(
         modifier = Modifier
             .fillMaxSize()
             .safeDrawingPadding()
     ) {
         Button(
             onClick = {},
             modifier = Modifier.align(Alignment.BottomCenter)
         ) {
             Text("登录")
         }
     }
     ```

     <br />

  3. 对于具有过多内边距的深层嵌套组件，使用 `WindowInsetsRulers`（例如 `Modifier.fitInside(WindowInsetsRulers.SafeDrawing.current)`）。有关代码示例，请参阅 IME 部分。
  4. 当需要一个元素（例如自定义标题栏或装饰性遮罩）与系统栏的尺寸相同时，使用内边距大小修饰符（例如 `Modifier.windowInsetsTopHeight(WindowInsets.systemBars)`）。有关代码示例，请参阅列表部分。

## 自适应 Scaffold

- `NavigationSuiteScaffold` 管理其自身组件（如 `NavigationRail` 或 `NavigationBar`）的安全区域。然而，自适应 Scaffold（例如 `NavigationSuiteScaffold`、`ListDetailPaneScaffold`）不会将其内边距值传递给其内部内容。您**必须**按照第 3 步所述，对**单个**屏幕或组件（例如列表 `contentPadding` 或 FAB 内边距）应用内边距。**不要**将 `safeDrawingPadding` 或类似修饰符应用于 `NavigationSuiteScaffold` 的父级。这将导致裁剪并阻止边缘到边缘的屏幕。

## IME

- 对于每个使用软键盘的 Activity，检查 AndroidManifest.xml 中是否设置了 `android:windowSoftInputMode="adjustResize"`。**不要**使用 `SOFT_INPUT_ADJUST_RESIZE`，因为它已弃用。然后，保持输入字段的焦点。选择一种方法：
  - 1. **首选：** 将 `Modifier.fitInside(WindowInsetsRulers.Ime.current)` 添加到内容容器。这比 `imePadding()` 更好，因为它减少了由忘记在层次结构上游消耗内边距而导致的卡顿和额外内边距。
  - 2. 将 `imePadding` 添加到内容容器。内边距修饰符**必须**在 `Modifier.verticalScroll()` 之前放置。如果父级已使用 `contentWindowInsets` 考虑 IME（例如 `contentWindowInsets = WindowInsets.safeDrawing`），则**不要**使用 `Modifier.imePadding()`。这样做会导致双重内边距。

### 使用 Scaffold 的 IME 代码模式

#### 正确

RIGHT，因为 `contentWindowInsets` 包含 IME 内边距，这些内边距作为 `innerPadding` 传递给内容 lambda。

```kotlin
// RIGHT
Scaffold(contentWindowInsets = WindowInsets.safeDrawing) { innerPadding ->
    Column(
        modifier = Modifier
            .padding(innerPadding)
            .consumeWindowInsets(innerPadding)
            .verticalScroll(rememberScrollState())
    ) { /* 内容 */ }
}
```

<br />

*** ** * ** ***

RIGHT，因为 `fitInside` 无论 `contentWindowInsets` 如何，都将内容适配到 IME 内边距。

```kotlin
// RIGHT
Scaffold() { innerPadding ->
    Column(
        modifier = Modifier
            .padding(innerPadding)
            .consumeWindowInsets(innerPadding)
            .fitInside(WindowInsetsRulers.Ime.current)
            .verticalScroll(rememberScrollState())
    ) { /* 内容 */ }
}
```

<br />

*** ** * ** ***

RIGHT，因为默认的 `contentWindowInsets` 不包含 IME 内边距，而 `imePadding()` 应用 IME 内边距：

```kotlin
// RIGHT
Scaffold() { innerPadding ->
    Column(
        modifier = Modifier
            .padding(innerPadding)
            .consumeWindowInsets(innerPadding)
            .imePadding()
            .verticalScroll(rememberScrollState())
    ) { /* 内容 */ }
}
```

<br />

#### 错误

WRONG，因为 IME 打开时会出现多余的内边距。IME 内边距应用了两次，一次是 `innerPadding`，它包含从传递的 `contentWindowInsets` 值中获取的 IME 内边距，一次是 `imePadding`：

```kotlin
// WRONG
Scaffold(contentWindowInsets = WindowInsets.safeDrawing) { innerPadding ->
    Column(
        modifier = Modifier
            .padding(innerPadding)
            .imePadding()
            .verticalScroll(rememberScrollState())
    ) { /* 内容 */ }
}
```

<br />

*** ** * ** ***

WRONG，因为 IME 会遮挡内容。Scaffold 的默认 `contentWindowInsets` 不包含 IME 内边距。

```kotlin
// WRONG
Scaffold() { innerPadding ->
    Column(
        modifier = Modifier
            .padding(innerPadding)
            .verticalScroll(rememberScrollState())
    ) { /* 内容 */ }
}
```

<br />

### 不使用 Scaffold 的 IME 代码模式

#### 正确

以下代码示例**不会**导致多余的内边距。

```kotlin
// RIGHT
Box(
    // 消耗内边距
    modifier = Modifier.safeDrawingPadding() // 或 imePadding(), safeContentPadding(), safeGesturesPadding()
) {
    Column(
        modifier = Modifier.imePadding()
    ) { /* 内容 */ }
}
```

<br />

*** ** * ** ***

```kotlin
// RIGHT
Box(
    // 消耗内边距
    modifier = Modifier.windowInsetsPadding(WindowInsets.safeDrawing) // 或 WindowInsets.ime, WindowInsets.safeContent, WindowInsets.safeGestures
) {
    Column(
        modifier = Modifier.imePadding()
    ) { /* 内容 */ }
}
```

<br />

*** ** * ** ***

```kotlin
// RIGHT
Box(
    // 未消耗内边距，但由于 fitInside 无关紧要
    modifier = Modifier.padding(WindowInsets.safeDrawing.asPaddingValues()) // 或 WindowInsets.ime.asPaddingValues(), WindowInsets.safeContent.asPaddingValues(), WindowInsets.safeGestures.asPaddingValues()
) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .fitInside(WindowInsetsRulers.Ime.current)
    ) { /* 内容 */ }
}
```

<br />

#### 错误

以下代码示例**会导致**多余的内边距，因为 IME 内边距应用了两次：

```kotlin
// WRONG
Box(
    // 未消耗内边距
    modifier = Modifier.padding(WindowInsets.safeDrawing.asPaddingValues()) // 或 WindowInsets.ime.asPaddingValues(), WindowInsets.safeContent.asPaddingValues(), WindowInsets.safeGestures.asPaddingValues()
) {
    Column(
        modifier = Modifier.imePadding()
    ) { /* 内容 */ }
}
```

<br />

## 导航栏对比度 & 系统栏图标

- 如果 Activity 使用 `WindowCompat` 的 `enableEdgeToEdge`，则**必须**将 `isAppearanceLightNavigationBars` 和 `isAppearanceLightStatusBars` 设置为设备主题的相反值，以便支持亮色和暗色主题的应用中系统栏图标可读。建议在主题文件中执行此操作。如果 Activity 使用 `ComponentActivity` 的 `enableEdgeToEdge`，则**不要**这样做，因为它会自动处理图标颜色。

```kotlin
// 仅在从 `WindowCompat` 调用 `enableEdgeToEdge` 时使用。
// 应用于主题文件。
@Composable
fun MyTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    content: @Composable () -> Unit
) {
    val view = LocalView.current
    if (!view.isInEditMode) {
        SideEffect {
            val window = (view.context as? Activity)?.window ?: return@SideEffect
            val controller = WindowCompat.getInsetsController(window, view)

            // 暗色图标用于亮色模式 (!darkTheme)，亮色图标用于暗色模式
            controller.isAppearanceLightStatusBars = !darkTheme
            controller.isAppearanceLightNavigationBars = !darkTheme
        }
    }

    MaterialTheme(content = content)
}
```

<br />

- 如果任何屏幕使用 `Scaffold` 或 `NavigationSuiteScaffold` 并带有底部栏（例如 `BottomAppBar`、`NavigationBar`），请在相应的 Activity 中为 SDK 29+ 设置 `window.isNavigationBarContrastEnforced = false`。这可防止系统向导航栏添加半透明背景，从而确保您的底部栏颜色延伸至屏幕底部。

## 列表

- 将内边距（如 `Scaffold` 的 `innerPadding`）应用于可滚动组件（例如 `LazyColumn`、`LazyRow`）的 `contentPadding` 参数。**不要**将其作为 `Modifier.padding()` 应用于列表的父容器，因为这会裁剪内容并阻止其滚动到系统栏后面。
- 创建一个覆盖系统栏的半透明可组合项，以便图标仍然可读。

```kotlin
class SystemBarProtectionSnippets : ComponentActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // enableEdgeToEdge 设置 window.isNavigationBarContrastEnforced = true
        // 这用于为三键导航添加半透明遮罩
        enableEdgeToEdge()

        setContent {
            MyTheme {
                // 主内容
                MyContent()

                // 绘制主内容后，绘制状态栏保护
                StatusBarProtection()
            }
        }
    }
}

@Composable
private fun StatusBarProtection(
    color: Color = MaterialTheme.colorScheme.surfaceContainer,
) {
    Spacer(
        modifier = Modifier
            .fillMaxWidth()
            .height(
                with(LocalDensity.current) {
                    (WindowInsets.statusBars.getTop(this) * 1.2f).toDp()
                }
            )
            .background(
                brush = Brush.verticalGradient(
                    colors = listOf(
                        color.copy(alpha = 1f),
                        color.copy(alpha = 0.8f),
                        Color.Transparent
                    )
                )
            )
    )
}
```

<br />

## 对话框

如果以下两个条件都为真，则对话框将是全屏的，必须改为边缘到边缘：
1. `DialogProperties` 包含 `usePlatformDefaultWidth = false`。
2. 对话框调用 `Modifier.fillMaxSize()`。

要使全屏对话框边缘到边缘，请在 `DialogProperties` 中设置 `decorFitsSystemWindows = false`。

```kotlin
Dialog(
    onDismissRequest = { /* 处理关闭 */ },
    properties = DialogProperties(
        // 1. 允许对话框跨越屏幕的完整宽度
        usePlatformDefaultWidth = false,
        // 2. 允许对话框在状态栏和导航栏后面绘制
        decorFitsSystemWindows = false
    )
) { /* 内容 */ }
```

<br />

## 检查清单

- \[ \] 每个 `Activity` 是否调用 `enableEdgeToEdge()`？
- \[ \] `AndroidManifest.xml` 中是否设置了 `adjustResize`？
- \[ \] 每个 `TextField`、`OutlinedTextField` 或 `BasicTextField` 是否具有 `imePadding()`、`fitInside`、`Modifier.safeDrawingPadding()`、`Modifier.safeContentPadding()`、`Modifier.safeGesturesPadding()` 或 `contentWindowInsets` 设置为 `WindowInsets.safeDrawing` 或 `WindowInsets.ime` 的父级？
- \[\] 第一个和最后一个列表项是否通过将内边距传递给 `contentPadding` 而远离系统栏？
- \[\] FAB 是否通过位于 Scaffold 内部或应用 `Modifier.safeDrawingPadding()` 而绘制在导航栏上方？
- \[\] 项目是否可以构建？运行 `./gradlew build` 以确保可以构建。
