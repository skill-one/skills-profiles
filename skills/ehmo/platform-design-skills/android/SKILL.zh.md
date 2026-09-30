---
name: android-design-guidelines
description: Material Design 3 和 Android 平台指南。在构建使用 Jetpack Compose 或 XML 布局的 Android 应用时使用，用于实现 Material You、导航或可访问性。在涉及 Android UI、Compose 组件、动态颜色或 Material Design 合规性的任务中触发。
---

# 安卓平台设计指南 — 材质设计 3

## 1. 材质你与主题化 [关键]

### 1.1 动态颜色

启用基于用户壁纸的动态颜色。动态颜色在安卓 12 及以上版本中默认启用，应作为主要的主题化策略。

```kotlin
// Compose: 动态颜色主题
@Composable
fun AppTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    dynamicColor: Boolean = true,
    content: @Composable () -> Unit
) {
    val colorScheme = when {
        dynamicColor && Build.VERSION.SDK_INT >= Build.VERSION_CODES.S -> {
            val context = LocalContext.current
            if (darkTheme) dynamicDarkColorScheme(context)
            else dynamicLightColorScheme(context)
        }
        darkTheme -> darkColorScheme()
        else -> lightColorScheme()
    }
    MaterialTheme(
        colorScheme = colorScheme,
        typography = AppTypography,
        content = content
    )
}
```

```xml
<!-- XML: themes.xml 中的动态颜色 -->
<style name="Theme.App" parent="Theme.Material3.DayNight.NoActionBar">
    <item name="dynamicColorThemeOverlay">@style/ThemeOverlay.Material3.DynamicColors.DayNight</item>
</style>
```

**规则：**
- R1.1: 对于安卓 12 以下的设备，始终提供一个静态颜色方案作为备用。
- R1.2: 组件中永远不要硬编码颜色十六进制值。始终从主题中引用颜色角色。
- R1.3: 使用至少 3 种不同的壁纸来测试动态颜色和谐性。

### 1.2 颜色角色

材质 3 定义了一套结构化的颜色角色。使用它们应基于语义，而非美学。

| 角色 | 使用场景 | 对应角色 |
|------|-------|---------|
| `primary` | 关键操作、活动状态、FAB | `onPrimary` |
| `primaryContainer` | 较不突出的主要元素 | `onPrimaryContainer` |
| `secondary` | 支持性 UI、过滤芯片 | `onSecondary` |
| `secondaryContainer` | 导航栏活动指示器 | `onSecondaryContainer` |
| `tertiary` | 强调色、对比色、互补色 | `onTertiary` |
| `tertiaryContainer` | 输入字段、较不突出的强调色 | `onTertiaryContainer` |
| `surface` | 背景、卡片、表单 | `onSurface` |
| `surfaceVariant` | 装饰性元素、分隔线 | `onSurfaceVariant` |
| `error` | 错误状态、破坏性操作 | `onError` |
| `errorContainer` | 错误背景 | `onErrorContainer` |
| `outline` | 边框、分隔线 | — |
| `outlineVariant` | 微妙的边框 | — |
| `inverseSurface` | 通知栏背景 | `inverseOnSurface` |

```kotlin
// 正确：语义颜色角色
Text(
    text = "错误消息",
    color = MaterialTheme.colorScheme.error
)
Surface(color = MaterialTheme.colorScheme.errorContainer) {
    Text(text = "错误详情", color = MaterialTheme.colorScheme.onErrorContainer)
}

// 错误：硬编码颜色
Text(text = "错误", color = Color(0xFFB00020)) // 反模式
```

**规则：**
- R1.4: 每个前景元素必须使用与其背景匹配的 `on` 颜色角色（例如，`onPrimary` 文本在 `primary` 背景上）。
- R1.5: 使用 `surface` 及其变体作为背景。永远不要将 `primary` 或 `secondary` 作为大面积背景区域。
- R1.6: 仅用于强调和互补对比，谨慎使用 `tertiary`。

### 1.3 亮色与暗色主题

支持亮色和暗色主题。默认情况下应尊重系统设置。

```kotlin
// Compose: 检测系统主题
val darkTheme = isSystemInDarkTheme()
```

**规则：**
- R1.7: 始终支持亮色和暗色主题。永远不要仅提供亮色版本。
- R1.8: 暗色主题表面使用基于抬升的色调映射，而非纯黑色 (#000000)。使用处理此映射的 `surface` 颜色角色。
- R1.9: 在应用设置中提供手动主题覆盖（系统 / 亮色 / 暗色）。

### 1.4 自定义颜色种子

当品牌需要自定义颜色时，提供种子颜色并使用材质主题构建器生成色调调色板。

```kotlin
// 品牌种子自定义颜色方案
private val BrandLightColorScheme = lightColorScheme(
    primary = Color(0xFF1B6D2F),
    onPrimary = Color(0xFFFFFFFF),
    primaryContainer = Color(0xFFA4F6A8),
    onPrimaryContainer = Color(0xFF002107),
    // ... 从种子生成完整调色板
)
```

**规则：**
- R1.10: 使用材质主题构建器从种子颜色生成色调调色板。永远不要手动选择单个色调。
- R1.11: 使用自定义颜色时，仍将动态颜色作为默认选项，并将自定义颜色作为备用。

---

## 2. 导航 [关键]

### 2.1 底部导航栏

适用于具有 3-5 个顶级目的地的手机的主要导航模式。

```kotlin
// Compose: 导航栏
NavigationBar {
    items.forEachIndexed { index, item ->
        NavigationBarItem(
            icon = {
                Icon(
                    imageVector = if (selectedItem == index) item.filledIcon else item.outlinedIcon,
                    contentDescription = item.label
                )
            },
            label = { Text(item.label) },
            selected = selectedItem == index,
            onClick = { selectedItem = index }
        )
    }
}
```

**规则：**
- R2.1: 在紧凑屏幕上使用导航栏用于 3-5 个顶级目的地。永远不要用于少于 3 个或超过 5 个。
- R2.2: 始终在导航栏项上显示标签。不允许仅使用图标的导航栏。
- R2.3: 使用填充图标表示选中状态，使用轮廓图标表示未选中状态。
- R2.4: 活动指示器使用 `secondaryContainer` 颜色。不要覆盖此设置。

### 2.2 导航栏

适用于中等和扩展屏幕（平板电脑、折叠屏、桌面）。

```kotlin
// Compose: 大屏幕的导航栏
NavigationRail(
    header = {
        FloatingActionButton(
            onClick = { /* 主要操作 */ },
            containerColor = MaterialTheme.colorScheme.tertiaryContainer
        ) {
            Icon(Icons.Default.Add, contentDescription = "创建")
        }
    }
) {
    items.forEachIndexed { index, item ->
        NavigationRailItem(
            icon = { Icon(item.icon, contentDescription = item.label) },
            label = { Text(item.label) },
            selected = selectedItem == index,
            onClick = { selectedItem = index }
        )
    }
}
```

**规则：**
- R2.5: 在中等（600-839dp）和扩展（840dp+）窗口尺寸上使用导航栏。在紧凑屏幕上与其配对使用。
- R2.6: 可选地，在栏头中包含一个 FAB 用于主要操作。
- R2.7: 栏上的标签是可选的，但建议使用以增强清晰度。

### 2.3 导航抽屉

适用于 5 个以上目的地或复杂的导航层次结构，通常在扩展屏幕上。

```kotlin
// Compose: 大屏幕的永久导航抽屉
PermanentNavigationDrawer(
    drawerContent = {
        PermanentDrawerSheet {
            Text("应用名称", modifier = Modifier.padding(16.dp),
                 style = MaterialTheme.typography.titleMedium)
            HorizontalDivider()
            items.forEach { item ->
                NavigationDrawerItem(
                    label = { Text(item.label) },
                    selected = item == selectedItem,
                    onClick = { selectedItem = item },
                    icon = { Icon(item.icon, contentDescription = null) }
                )
            }
        }
    }
) {
    Scaffold { /* 页面内容 */ }
}
```

**规则：**
- R2.8: 在紧凑屏幕上使用模态抽屉，在扩展屏幕上使用永久抽屉。
- R2.9: 将抽屉项分组为带有分隔线和部分标题的章节。

### 2.4 预测返回手势

安卓 13 及以上版本支持带动画预览的预测返回。

```kotlin
// Compose: 使用 BackHandler 实现预测返回 (androidx.activity.compose)
BackHandler(enabled = true) {
    // 当返回确认时调用；在您的导航控制器中导航返回
    navController.popBackStack()
}
```

```kotlin
// Compose: 使用 predictiveBackHandler 修饰符实现预测返回进度动画
// (androidx.activity:activity-compose 1.8+)
Modifier.predictiveBackHandler(enabled = true) { progress ->
    // progress 是一个 Flow<BackEventCompat>，包含 x、y、滑动边缘、进度 (0.0–1.0)
    progress.collect { backEvent ->
        animationState = backEvent.progress
    }
}
```

```xml
<!-- AndroidManifest.xml: 启用预测返回 -->
<application android:enableOnBackInvokedCallback="true">
```

**规则：**
- R2.10: 在清单中启用预测返回。在 **Compose** 应用中，使用 `BackHandler`（来自 `androidx.activity.compose`）拦截返回事件。在 **基于视图** 的应用中，实现 `OnBackInvokedCallback`（API 33+）或 `OnBackPressedCallback`（AndroidX）而不是重写 `onBackPressed()`。
- R2.11: 系统返回手势在导航栈中导航返回。向上按钮（工具栏箭头）在应用层次结构中导航。这些可能不同。
- R2.12: 除非有未保存的用户输入，否则永远不要拦截系统返回以显示“确定吗？”对话框。
- R2.13: 不要抑制系统提供的返回预览动画。如果您实现了自定义进入/退出过渡，请使用 `BackEventCompat.progress`（0.0–1.0）进行插值，并尊重 `BackEventCompat.swipeEdge` (`EDGE_LEFT`/`EDGE_RIGHT`），以便退出屏幕缩放并朝向发起边缘移动，匹配系统动画。
- R2.14: 优先选择识别而非回忆。保持目的地标签化、选中状态可见，并保留返回栈上下文，以便用户在每次导航步骤后不必重新构建位置。

```kotlin
// Compose: 从预测返回进度驱动自定义动画
Modifier.predictiveBackHandler(enabled = true) { progress ->
    progress.collect { backEvent ->
        // backEvent.progress: 0.0（手势开始）→ 1.0（确认）
        // backEvent.swipeEdge: BackEventCompat.EDGE_LEFT 或 EDGE_RIGHT
        exitScale = 1f - (backEvent.progress * 0.1f)
        exitOffsetX = if (backEvent.swipeEdge == BackEventCompat.EDGE_LEFT) -backEvent.progress * 32.dp.toPx() else backEvent.progress * 32.dp.toPx()
    }
}
```

### 2.5 导航组件选择

| 屏幕尺寸 | 3-5 目的地 | 5+ 目的地 |
|-------------|-------------------|-----------------|
| 紧凑 (< 600dp) | 导航栏 | 模态抽屉 + 导航栏 |
| 中等 (600-839dp) | 导航栏 | 模态抽屉 + 导航栏 |
| 扩展 (840dp+) | 导航栏 | 永久抽屉 |

---

## 3. 布局与响应式 [高]

### 3.1 窗口尺寸类别

使用窗口尺寸类别进行自适应布局，而非原始像素断点。

```kotlin
// Compose: 窗口尺寸类别
val windowSizeClass = calculateWindowSizeClass(this)
when (windowSizeClass.widthSizeClass) {
    WindowWidthSizeClass.Compact -> CompactLayout()
    WindowWidthSizeClass.Medium -> MediumLayout()
    WindowWidthSizeClass.Expanded -> ExpandedLayout()
}
```

| 类别 | 宽度 | 典型设备 | 列数 |
|-------|-------|----------------|---------|
| Compact | < 600dp | 手机竖屏 | 4 |
| Medium | 600-839dp | 平板竖屏、折叠屏 | 8 |
| Expanded | 840dp+ | 平板横屏、桌面 | 12 |

**规则：**
- R3.1: 始终使用 `WindowSizeClass`（来自 `material3-window-size-class`）进行响应式布局决策。
- R3.2: 永远不要使用固定像素断点。设备类别是流动的。
- R3.3: 支持所有三种宽度尺寸类别。至少支持紧凑和扩展。

### 3.2 材质网格

应用标准的材质网格边距和间距。

| 尺寸类别 | 边距 | 间距 | 列数 |
|------------|-------|-------|---------|
| Compact | 16dp | 8dp | 4 |
| Medium | 24dp | 16dp | 8 |
| Expanded | 24dp | 24dp | 12 |

**规则：**
- R3.4: 内容不应在扩展屏幕上跨越整个宽度。使用最大内容宽度约为 840dp 或列表-详情布局。
- R3.5: 应用与网格规范一致的横向边距。

### 3.3 边缘到边缘显示

安卓 15 及以上版本强制执行边缘到边缘。所有应用都应在系统栏后面绘制。

```kotlin
// Compose: 边缘到边缘设置
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        enableEdgeToEdge()
        super.onCreate(savedInstanceState)
        setContent {
            Scaffold(
                modifier = Modifier.fillMaxSize(),
                // Scaffold 自动处理顶部/底部栏的 inset
            ) { innerPadding ->
                Content(modifier = Modifier.padding(innerPadding))
            }
        }
    }
}
```

**规则：**
- R3.6: 在 `setContent` 之前调用 `enableEdgeToEdge()`。在状态栏和导航栏后面绘制。
- R3.7: 使用 `WindowInsets` 为系统栏内容添加填充。`Scaffold` 自动处理顶部栏和底部栏内容。
- R3.8: 可滚动内容应滚动在透明的系统栏后面，并在列表的顶部和底部添加适当的 inset 填充。

### 3.4 折叠屏设备支持

```kotlin
// Compose: 检测折叠姿势
val foldingFeatures = WindowInfoTracker.getOrCreate(context)
    .windowLayoutInfo(context)
    .collectAsState(initial = WindowLayoutInfo(emptyList()))
```

**规则：**
- R3.9: 检测铰链/折叠位置，避免将关键内容放置在折叠处。
- R3.10: 使用 `ListDetailPaneScaffold` 或 `SupportingPaneScaffold`（来自 Material3 自适应库）以实现折叠感知布局。

---

## 4. 字体 [高]

### 4.1 材质类型比例

| 角色 | 默认大小 | 默认粗细 | 使用场景 |
|------|-------------|----------------|-------|
| displayLarge | 57sp | 400 | 英雄文本、引导 |
| displayMedium | 45sp | 400 | 大型功能文本 |
| displaySmall | 36sp | 400 | 显著显示 |
| headlineLarge | 32sp | 400 | 屏幕标题 |
| headlineMedium | 28sp | 400 | 章节标题 |
| headlineSmall | 24sp | 400 | 卡片标题 |
| titleLarge | 22sp | 400 | 顶部应用栏标题 |
| titleMedium | 16sp | 500 | 标签、导航 |
| titleSmall | 14sp | 500 | 副标题 |
| bodyLarge | 16sp | 400 | 主要正文文本 |
| bodyMedium | 14sp | 400 | 次要正文文本 |
| bodySmall | 12sp | 400 | 摘要 |
| labelLarge | 14sp | 500 | 按钮和显著标签 |
| labelMedium | 12sp | 500 | 芯片、较小标签 |
| labelSmall | 11sp | 500 | 时间戳、注释 |

```kotlin
// Compose: 自定义字体
val AppTypography = Typography(
    displayLarge = TextStyle(
        fontFamily = FontFamily(Font(R.font.brand_regular)),
        fontWeight = FontWeight.Normal,
        fontSize = 57.sp,
        lineHeight = 64.sp,
        letterSpacing = (-0.25).sp
    ),
    bodyLarge = TextStyle(
        fontFamily = FontFamily(Font(R.font.brand_regular)),
        fontWeight = FontWeight.Normal,
        fontSize = 16.sp,
        lineHeight = 24.sp,
        letterSpacing = 0.5.sp
    )
    // ... 定义所有 15 个角色
)
```

**规则：**
- R4.1: 始终使用 `sp` 单位为文本大小以支持用户字体缩放偏好。
- R4.2: 正文内容永远不要小于 12sp。标签最小可到 11sp。
- R4.3: 从 `MaterialTheme.typography` 引用字体角色，而非硬编码大小。
- R4.4: 支持动态类型缩放。在 200% 字体缩放下测试。确保没有文本被裁剪或重叠。
- R4.5: 行高应为字体大小的 1.2-1.5 倍，以增强可读性。

---

## 5. 组件 [高]

### 5.1 浮动操作按钮 (FAB)

FAB 代表屏幕上最重要的操作。

```kotlin
// Compose: FAB 变体
// 标准FAB
FloatingActionButton(onClick = { /* 操作 */ }) {
    Icon(Icons.Default.Add, contentDescription = "创建新项目")
}

// 扩展FAB（带标签 - 建议用于清晰度）
ExtendedFloatingActionButton(
    onClick = { /* 操作 */ },
    icon = { Icon(Icons.Default.Edit, contentDescription = null) },
    text = { Text("Compose") }
)

// 大型FAB
LargeFloatingActionButton(onClick = { /* 操作 */ }) {
    Icon(Icons.Default.Add, contentDescription = "创建", modifier = Modifier.size(36.dp))
}
```

**规则：**
- R5.1：每个屏幕最多使用一个 FAB。它代表主要操作。
- R5.2：将 FAB 放置在屏幕的底端。在带有导航栏的屏幕上，FAB 浮在导航栏上方。
- R5.3：FAB 默认应使用 `primaryContainer` 颜色。在次要屏幕上使用 `tertiaryContainer`。
- R5.4：优先使用带标签的 `ExtendedFloatingActionButton` 以提高清晰度。如果需要，在滚动时可以折叠为仅图标。

### 5.2 顶部应用栏

```kotlin
// Compose: 顶部应用栏变体
// 小型（默认）
TopAppBar(
    title = { Text("页面标题") },
    navigationIcon = {
        IconButton(onClick = { /* 向上导航 */ }) {
            Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "返回")
        }
    },
    actions = {
        IconButton(onClick = { /* 搜索 */ }) {
            Icon(Icons.Default.Search, contentDescription = "搜索")
        }
    }
)

// 中型 — 扩展标题区域
MediumTopAppBar(
    title = { Text("区域标题") },
    scrollBehavior = TopAppBarDefaults.enterAlwaysScrollBehavior()
)

// 大型 — 用于突出显示标题
LargeTopAppBar(
    title = { Text("屏幕标题") },
    scrollBehavior = TopAppBarDefaults.exitUntilCollapsedScrollBehavior()
)
```

**规则：**
- R5.5：大多数屏幕使用 `TopAppBar`（小型）。使用 `MediumTopAppBar` 或 `LargeTopAppBar` 用于突出显示区域或屏幕标题。
- R5.6：将滚动行为与应用栏连接起来，使其随着内容滚动而折叠/展开。
- R5.7：将操作图标限制为 2-3 个。将额外的操作放入更菜单中。

### 5.3 底部面板

```kotlin
// Compose: 模态底部面板
ModalBottomSheet(
    onDismissRequest = { showSheet = false },
    sheetState = rememberModalBottomSheetState()
) {
    Column(modifier = Modifier.padding(16.dp)) {
        Text("面板标题", style = MaterialTheme.typography.titleLarge)
        Spacer(modifier = Modifier.height(16.dp))
        // 面板内容
    }
}
```

**规则：**
- R5.8：使用模态底部面板用于非关键的补充内容。使用标准底部面板用于持久内容。
- R5.9：底部面板必须有一个可见的拖动手柄，以便于发现。
- R5.10：如果内容可以超出可见区域，面板内容必须可滚动。

### 5.4 对话框

```kotlin
// Compose: 警告对话框
AlertDialog(
    onDismissRequest = { showDialog = false },
    title = { Text("放弃草稿？") },
    text = { Text("您未保存的更改将丢失。") },
    confirmButton = {
        TextButton(onClick = { /* 确认 */ }) { Text("放弃") }
    },
    dismissButton = {
        TextButton(onClick = { showDialog = false }) { Text("取消") }
    }
)
```

**规则：**
- R5.11：对话框中断用户。仅用于需要立即注意力的关键决策。
- R5.12：确认按钮使用文本按钮，而不是填充按钮。取消按钮始终在左侧。
- R5.13：对话框标题应该是简洁的问题或陈述。正文提供上下文。

### 5.5 快照

```kotlin
// Compose: 带有操作的快照
val snackbarHostState = remember { SnackbarHostState() }
Scaffold(snackbarHost = { SnackbarHost(snackbarHostState) }) {
    // 触发快照
    LaunchedEffect(key) {
        val result = snackbarHostState.showSnackbar(
            message = "项目已归档",
            actionLabel = "撤销",
            duration = SnackbarDuration.Short
        )
        if (result == SnackbarResult.ActionPerformed) { /* 撤销 */ }
    }
}
```

**规则：**
- R5.14：使用快照进行简短的非关键反馈。它们自动消失，不应包含关键信息。
- R5.15：快照出现在屏幕底部，位于导航栏和 FAB 之间。
- R5.16：当操作可逆时，包含操作（例如，“撤销”）。限制为一个操作。

### 5.6 芯片

```kotlin
// 筛选芯片
FilterChip(
    selected = isSelected,
    onClick = { isSelected = !isSelected },
    label = { Text("筛选") },
    leadingIcon = if (isSelected) {
        { Icon(Icons.Default.Check, contentDescription = null, modifier = Modifier.size(18.dp)) }
    } else null
)

// 辅助芯片
AssistChip(
    onClick = { /* 操作 */ },
    label = { Text("添加到日历") },
    leadingIcon = { Icon(Icons.Default.CalendarToday, contentDescription = null) }
)
```

**规则：**
- R5.17：使用 `FilterChip` 用于切换筛选器，`AssistChip` 用于智能建议，`InputChip` 用于用户输入的内容（标签），`SuggestionChip` 用于动态生成的建议。
- R5.18：芯片应水平滚动排列或使用流布局，而不是垂直堆叠。
- R5.19：立即显示等待状态。如果操作无法立即完成，请通过行内状态更改、进度或另一个可见响应来承认它，而不是让 UI 保持静态。

### 5.7 组件选择指南

| 需求 | 组件 |
|------|-----------|
| 主要屏幕操作 | FAB |
| 简短反馈 | 快照 |
| 关键决策 | 对话框 |
| 补充内容 | 底部面板 |
| 切换筛选器 | 筛选芯片 |
| 用户输入标签 | 输入芯片 |
| 智能建议 | 辅助芯片 |
| 内容组 | 卡片 |
| 垂直项目列表 | 带有 ListItem 的 LazyColumn |
| 分段选项（2-5） | SegmentedButton |
| 二进制切换 | 开关 |
| 从列表中选择 | 单选按钮或暴露的下拉菜单 |

---

## 6. 可访问性 [关键]

### 6.1 TalkBack 和内容描述

```kotlin
// Compose: 可访问组件
Icon(
    Icons.Default.Favorite,
    contentDescription = "添加到收藏夹" // 描述性，而不是“心形图标”
)

// 装饰性元素
Icon(
    Icons.Default.Star,
    contentDescription = null // null 用于纯装饰
)

// 合并语义以复合元素
Row(modifier = Modifier.semantics(mergeDescendants = true) {}) {
    Icon(Icons.Default.Event, contentDescription = null)
    Text("2026年3月15日")
}

// 自定义操作
Box(modifier = Modifier.semantics {
    customActions = listOf(
        CustomAccessibilityAction("归档") { /* 归档 */ true },
        CustomAccessibilityAction("删除") { /* 删除 */ true }
    )
})
```

**规则：**
- R6.1：每个交互元素必须有 `contentDescription`（如果纯装饰则为 `null`）。
- R6.2：内容描述必须描述操作或含义，而不是视觉外观。说“添加到收藏夹”，而不是“心形图标”。
- R6.3：使用 `mergeDescendants = true` 将相关元素组合为单个 TalkBack 聚焦单元（例如，带有图标 + 文本 + 副标题的列表项）。
- R6.4：提供 `customActions` 以便 TalkBack 用户可以访问滑动以关闭或长按操作。

### 6.2 触摸目标

```kotlin
// Compose: 确保最小触摸目标
IconButton(onClick = { /* 操作 */ }) {
    // IconButton 已经提供 48dp 最小触摸目标
    Icon(Icons.Default.Close, contentDescription = "关闭")
}

// 手动最小触摸目标
Box(
    modifier = Modifier
        .sizeIn(minWidth = 48.dp, minHeight = 48.dp)
        .clickable { /* 操作 */ },
    contentAlignment = Alignment.Center
) {
    Icon(Icons.Default.Info, contentDescription = "信息", modifier = Modifier.size(24.dp))
}
```

**规则：**
- R6.5：所有交互元素必须有 48x48dp 的最小触摸目标。Material 3 组件默认处理此问题。
- R6.6：不要为了节省空间而减少触摸目标。如果视觉元素较小，请使用填充来增加可触摸区域。

### 6.3 颜色对比和视觉

**规则：**
- R6.7：文本对比度必须至少为 4.5:1（正常文本）和 3:1（大文本，18sp+ 或 14sp+ 粗体）相对于其背景。
- R6.8：永远不要仅使用颜色来传达信息。与图标、文本或模式配对。
- R6.9：支持粗体文本和高对比度可访问性设置。使用 `Configuration.fontWeightAdjustment`（API 31+）检测用户的粗体文本偏好并相应地缩放自定义字体权重。使用 `AccessibilityManager.isHighTextContrastEnabled()` 检测高对比度模式并替换为更高对比度的颜色值。Material 3 组件自动处理这两个问题；自定义文本渲染和颜色使用必须显式选择加入。

```kotlin
// 检测粗体文本偏好（API 31+）
val fontWeightAdjustment = resources.configuration.fontWeightAdjustment
val isBoldText = fontWeightAdjustment >= 700 // 等效于 FontWeight.Bold.weight

// 检测高对比度模式
val am = getSystemService(Context.ACCESSIBILITY_SERVICE) as AccessibilityManager
val isHighContrast = am.isHighTextContrastEnabled

// Compose: 使用尊重 fontWeightAdjustment 的 MaterialTheme.typography
Text(
    text = "标签",
    style = MaterialTheme.typography.bodyLarge // 适应 fontWeightAdjustment
)

// 对于自定义颜色：提供高对比度替代方案
val labelColor = if (isHighContrast) {
    MaterialTheme.colorScheme.onSurface  // 强对比度
} else {
    MaterialTheme.colorScheme.onSurfaceVariant  // 正常对比度
}
```

### 6.4 聚焦和遍历

```kotlin
// Compose: 自定义聚焦顺序
Column {
    var focusRequester = remember { FocusRequester() }
    TextField(
        modifier = Modifier.focusRequester(focusRequester),
        value = text,
        onValueChange = { text = it }
    )
    LaunchedEffect(Unit) {
        focusRequester.requestFocus() // 屏幕加载时自动聚焦
    }
}
```

**规则：**
- R6.10：聚焦顺序必须遵循逻辑阅读顺序（从上到下，从左到右）。除非默认顺序不正确，否则避免自定义 `focusOrder`。
- R6.11：在导航或对话框关闭后，将焦点移动到最合理的目标元素。
- R6.12：所有屏幕都必须使用 TalkBack、Switch Access 和外部键盘完全可操作。

### 6.5 自定义画布视图

绘制内容在画布上的自定义 `View` 子类（图表、自定义选择器、绘图表面）默认情况下对 TalkBack 是不可见的，因为它们没有子视图。使用 `ExploreByTouchHelper` 从 `androidx.customview.widget` 定义虚拟可访问性树。

- R6.13：自定义画布绘制的视图必须使用 `ExploreByTouchHelper` 向 TalkBack 提供虚拟可访问性树。覆盖 `getVirtualViewAt()` 以将触摸坐标映射到虚拟视图 ID，并覆盖 `onPopulateNodeForVirtualView()` 以为每个虚拟节点提供文本、边界和操作。

```kotlin
import androidx.customview.widget.ExploreByTouchHelper

class PieChartView(context: Context) : View(context) {

    private val helper = object : ExploreByTouchHelper(this) {
        override fun getVirtualViewAt(x: Float, y: Float): Int {
            // 返回位于 (x, y) 的切片的虚拟视图 ID，或 INVALID_ID
            return sliceIndexAt(x, y)
        }

        override fun getVisibleVirtualViews(virtualViewIds: MutableList<Int>) {
            slices.indices.forEach { virtualViewIds.add(it) }
        }

        override fun onPopulateNodeForVirtualView(
            virtualViewId: Int,
            node: AccessibilityNodeInfoCompat
        ) {
            val slice = slices[virtualViewId]
            node.text = "${slice.label}: ${slice.percentage}%"
            node.setBoundsInParent(slice.bounds)
            node.addAction(AccessibilityNodeInfoCompat.ACTION_CLICK)
        }

        override fun onPerformActionForVirtualView(
            virtualViewId: Int, action: Int, arguments: Bundle?
        ): Boolean {
            if (action == AccessibilityNodeInfoCompat.ACTION_CLICK) {
                onSliceSelected(virtualViewId)
                return true
            }
            return false
        }
    }

    init {
        ViewCompat.setAccessibilityDelegate(this, helper)
    }

    override fun dispatchHoverEvent(event: MotionEvent) =
        helper.dispatchHoverEvent(event) || super.dispatchHoverEvent(event)
}
```

---

## 7. 手势和输入 [中等]

### 7.1 系统手势

**规则：**
- R7.1：不要在系统手势插入区域（底部 20dp，左右边缘 24dp）内放置交互元素，因为它们与系统导航手势冲突。
- R7.2：使用 `WindowInsets.systemGestures` 检测并避免手势冲突区域。

### 7.2 常见手势模式

```kotlin
// Compose: 拉动刷新
PullToRefreshBox(
    isRefreshing = isRefreshing,
    onRefresh = { viewModel.refresh() }
) {
    LazyColumn { /* 内容 */ }
}

// Compose: 滑动删除
SwipeToDismissBox(
    state = rememberSwipeToDismissBoxState(),
    backgroundContent = {
        Box(
            modifier = Modifier.fillMaxSize().background(MaterialTheme.colorScheme.error),
            contentAlignment = Alignment.CenterEnd
        ) {
            Icon(Icons.Default.Delete, contentDescription = "删除",
                 tint = MaterialTheme.colorScheme.onError)
        }
    }
) {
    ListItem(headlineContent = { Text("可滑动项目") })
}
```

**规则：**
- R7.3：所有滑动删除操作必须可撤销（显示带撤销的快照）或需要确认。
- R7.4：为所有基于手势的操作提供替代的非手势触发方式（用于可访问性）。
- R7.5：对所有可点击元素应用 Material 涟漪效果。Compose `clickable` 修饰符默认包含涟漪。

### 7.3 长按

**规则：**
- R7.6：使用长按用于上下文菜单和多选模式。永远不要将其作为访问功能的唯一方式。
- R7.7：通过 `HapticFeedbackType.LongPress` 在长按时提供触觉反馈。

---

## 8. 通知 [中等]

### 8.1 通知通道

```kotlin
// 创建通知通道（Android 8+ 需要）
val channel = NotificationChannel(
    "messages",
    "消息",
    NotificationManager.IMPORTANCE_HIGH
).apply {
    description = "新消息通知"
    enableLights(true)
    lightColor = Color.BLUE
}
notificationManager.createNotificationChannel(channel)
```

| 重要性 | 行为 | 用于 |
|-----------|----------|---------|
| IMPORTANCE_HIGH | 声音 + 头部提示 | 消息、电话 |
| IMPORTANCE_DEFAULT | 声音 | 社交更新、电子邮件 |
| IMPORTANCE_LOW | 无声音 | 推荐内容 |
| IMPORTANCE_MIN | 静音，无状态栏 | 天气、进行中的 |

**规则：**
- R8.1：为每种不同的通知类型创建单独的通知通道。用户可以独立配置每个通道。
- R8.2：谨慎选择重要性级别。过度使用 `IMPORTANCE_HIGH` 会导致用户完全禁用通知。
- R8.3：所有通知必须有一个点击操作（PendingIntent）以导航到相关内容。
- R8.4：在通知图标中包含 `contentDescription` 以便可访问性。

### 8.2 通知设计

**规则：**
- R8.5：使用 `MessagingStyle` 用于对话。包括发件人姓名和头像。
- R8.6：向消息通知添加直接回复操作。
- R8.7：在消息通知上提供“标记为已读”操作。
- R8.8：使用可展开的通知（`BigTextStyle`、`BigPictureStyle`、`InboxStyle`）用于丰富内容。
- R8.9：前台服务通知必须准确描述正在进行的操作，并在适当的情况下提供停止操作。

---

## 9. 权限和隐私 [高]

### 9.1 运行时权限

```kotlin
// Compose: 权限请求
val permissionState = rememberPermissionState(Manifest.permission.CAMERA)

if (permissionState.status.isGranted) {
    CameraPreview()
} else {
    Column {
        Text("需要相机访问权限以扫描二维码。")
        Button(onClick = { permissionState.launchPermissionRequest() }) {
            Text("授予权限")
        }
    }
}
```

**规则：**
- R9.1：在上下文中请求权限，在需要时请求，而不是在应用启动时请求。
- R9.2：在请求权限之前始终解释为什么需要权限（理由屏幕）。
- R9.3：优雅地处理权限拒绝。提供降级功能，而不是阻止用户。
- R9.4：永远不要请求你未积极使用的权限。Google Play 将拒绝具有不必要权限的应用。

### 9.2 隐私保护 API

```kotlin
// 相册选择器：无需权限
val pickMedia = rememberLauncherForActivityResult(
    ActivityResultContracts.PickVisualMedia()
) { uri ->
    uri?.let { /* 处理选择的媒体 */ }
}
pickMedia.launch(PickVisualMediaRequest(ActivityResultContracts.PickVisualMedia.ImageOnly))
```

**规则：**
- R9.5：使用相册选择器（Android 13+）代替请求 `READ_MEDIA_IMAGES`。无需权限。
- R9.6：除非功能需要精确位置，否则使用 `ACCESS_COARSE_LOCATION`（近似位置）。
- R9.7：在非录制场景中，优先使用一次性权限获取相机和麦克风权限。
- R9.8：相机或麦克风被主动使用时，显示隐私指示器。

---

## 10. 系统集成 [中等]

### 10.1 小部件

```kotlin
// Compose Glance API 小部件
class TaskWidget : GlanceAppWidget() {
    override suspend fun provideGlance(context: Context, id: GlanceId) {
        provideContent {
            GlanceTheme {
                Column(
                    modifier = GlanceModifier
                        .fillMaxSize()
                        .background(GlanceTheme.colors.widgetBackground)
                        .padding(16.dp)
                ) {
                    Text(
                        text = "任务",
                        style = TextStyle(fontWeight = FontWeight.Bold,
                                         color = GlanceTheme.colors.onSurface)
                    )
                    // 小部件内容
                }
            }
        }
    }
}
```

**规则：**
- R10.1：使用 Glance API 开发新小部件。支持通过 `GlanceTheme` 实现动态颜色。
- R10.2：小部件必须具有默认配置，并在放置后立即工作。
- R10.3：在合理的情况下提供多种小部件尺寸（小、中、大）。
- R10.4：使用与系统小部件形状匹配的圆角（`system_app_widget_background_radius`）。

### 10.2 应用快捷方式

```xml
<!-- shortcuts.xml -->
<shortcuts xmlns:android="http://schemas.android.com/apk/res/android">
    <shortcut
        android:shortcutId="compose"
        android:enabled="true"
        android:shortcutShortLabel="@string/compose_short"
        android:shortcutLongLabel="@string/compose_long"
        android:icon="@drawable/ic_shortcut_compose">
        <intent
            android:action="android.intent.action.VIEW"
            android:targetPackage="com.example.app"
            android:targetClass="com.example.app.ComposeActivity" />
    </shortcut>
</shortcuts>
```

**规则：**
- R10.5：为常用操作提供 2-4 个静态快捷方式。支持动态快捷方式用于最近内容。
- R10.6：快捷方式图标应为简单的、可识别的圆形背景轮廓。
- R10.7：在应用图标长按和设置 > 应用快捷方式列表中测试快捷方式。

### 10.3 深链接和分享

**规则：**
- R10.8：对所有公共内容 URL 支持安卓应用链接（验证的深链接）。
- R10.9：使用 `ShareCompat` 或 `Intent.createChooser` 实现分享菜单。提供包含标题、描述和缩略图的丰富预览。
- R10.10：处理传入的分享意图，并按内容类型进行适当过滤。

---

## 设计评估清单

使用此清单评估安卓 UI 实现：

### 主题与颜色
- [ ] 启用动态颜色并设置静态回退
- [ ] 所有颜色均引用 Material 主题角色（无硬编码的十六进制值）
- [ ] 支持亮色和暗色主题
- [ ] 文本颜色与其背景颜色角色匹配
- [ ] 通过 Material Theme Builder 从种子色生成自定义颜色

### 导航
- [ ] 根据屏幕尺寸和目标数量选择正确的导航组件
- [ ] 导航栏标签始终可见
- [ ] 启用并处理预测性返回手势
- [ ] “向上”与“返回”行为正确

### 布局
- [ ] 支持所有三种窗口尺寸类别
- [ ] 边缘对齐并正确处理内边距
- [ ] 大屏幕上内容不跨越全宽
- [ ] 尊重折叠铰链区域

### 字体
- [ ] 所有文本使用 sp 单位
- [ ] 所有文本引用 MaterialTheme.typography 角色
- [ ] 在 200% 字体缩放下测试，无裁剪
- [ ] 正文最小 12sp，标签最小 11sp

### 组件
- [ ] 每个屏幕最多一个 FAB
- [ ] 顶部应用栏连接到滚动行为
- [ ] 仅用于非关键反馈的 Snackbars
- [ ] 对关键中断保留对话框

### 无障碍
- [ ] 所有交互元素均有 contentDescription
- [ ] 所有触摸目标 >= 48dp
- [ ] 文本颜色对比度 >= 4.5:1
- [ ] 仅通过颜色传递信息
- [ ] 完全测试 TalkBack 遍历
- [ ] 开关访问和键盘导航正常工作

### 手势
- [ ] 系统手势区域无交互元素
- [ ] 所有手势操作均有非手势替代方案
- [ ] 滑动撤销功能可用

### 通知
- [ ] 每种通知类型使用独立通道
- [ ] 适当的重要性级别
- [ ] 点击操作导航到相关内容

### 权限
- [ ] 权限请求在上下文中进行，而非启动时
- [ ] 请求权限前显示说明
- [ ] 拒绝时优雅降级
- [ ] 使用相册选择器代替媒体权限

### 系统集成
- [ ] 小部件使用 Glance API 并支持动态颜色
- [ ] 为常用操作提供应用快捷方式
- [ ] 处理公共内容的深链接

---

## 反模式

| 反模式 | 为什么错误 | 正确方法 |
|-------|----------|--------|
| 硬编码十六进制颜色值 | 破坏动态颜色和暗色主题 | 使用 `MaterialTheme.colorScheme` 角色 |
| 使用 `dp` 设置文本大小 | 忽略用户字体缩放 | 使用 `sp` 单位 |
| 自定义底部导航栏 | 与平台不一致 | 使用 Material `NavigationBar` |
| 无标签的导航栏 | 违反 Material 指南 | 始终显示标签 |
| 对非关键信息使用对话框 | 不必要地中断用户 | 使用 Snackbars 或 Bottom Sheet |
| FAB 用于次要操作 | 稀释主要操作的突出性 | 仅一个 FAB 用于主要操作 |
| `onBackPressed()` 重写 | 已弃用；破坏预测性返回 | 使用 `BackHandler`（Compose）或 `OnBackInvokedCallback`（基于视图）支持预测性返回 |
| 触摸目标 < 48dp | 无障碍违规 | 确保 48x48dp 最小尺寸 |
| 启动时请求权限 | 用户无上下文拒绝 | 在上下文中请求权限并说明 |
| 纯黑色 (#000000) 暗色主题 | 眼睛疲劳；非 Material 3 | 使用 Material 表面颜色角色 |
| 仅图标导航栏 | 用户无法识别目的地 | 始终包含文本标签 |
| 平板电脑全宽内容 | 浪费空间；可读性差 | 最大宽度或列表-详情布局 |
| `READ_EXTERNAL_STORAGE` 用于照片 | 自 Android 13 起不再必要 | 使用相册选择器 API |
| 权限拒绝时阻塞 UI | 惩罚用户 | 优雅降级 |
| 手动选择调色板 | 色调关系不一致 | 使用 Material Theme Builder |
