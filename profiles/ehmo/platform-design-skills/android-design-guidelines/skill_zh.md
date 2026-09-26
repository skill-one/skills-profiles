# 安卓平台设计指南 — 材质设计 3

## 1. 材质你 & 主题 [关键]

### 1.1 动态颜色

启用基于用户壁纸的动态颜色。Android 12 及以上版本默认启用动态颜色，并应作为主要的主题策略。

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
- R1.1: 始终为低于 Android 12 的设备提供静态颜色方案回退。
- R1.2: 绝不将颜色十六进制值硬编码在组件中。始终从主题中引用颜色角色。
- R1.3: 使用至少 3 种不同的壁纸来验证动态颜色协调性。

### 1.2 颜色角色

材质 3 定义了一套结构化的颜色角色。按语义而非美学使用它们。

| 角色 | 用途 | 对角色 |
|------|-------|---------|
| `primary` | 关键操作、活动状态、FAB | `onPrimary` |
| `primaryContainer` | 较不突出的主要元素 | `onPrimaryContainer` |
| `secondary` | 辅助 UI、过滤器芯片 | `onSecondary` |
| `secondaryContainer` | 导航栏活动指示器 | `onSecondaryContainer` |
| `tertiary` | 强调、对比、互补 | `onTertiary` |
| `tertiaryContainer` | 输入字段、较不突出的强调 | `onTertiaryContainer` |
| `surface` | 背景、卡片、表单 | `onSurface` |
| `surfaceVariant` | 装饰元素、分隔线 | `onSurfaceVariant` |
| `error` | 错误状态、破坏性操作 | `onError` |
| `errorContainer` | 错误背景 | `onErrorContainer` |
| `outline` | 边框、分隔线 | — |
| `outlineVariant` | 微妙的边框 | — |
| `inverseSurface` | Snackbar 背景 | `inverseOnSurface` |

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
- R1.4: 每个前景元素都必须使用与其背景匹配的 `on` 颜色角色（例如，`onPrimary` 文本在 `primary` 背景上）。
- R1.5: 使用 `surface` 及其变体作为背景。永远不要将 `primary` 或 `secondary` 作为大面积背景区域使用。
- R1.6: 限制使用 `tertiary`，仅用于强调和互补对比。

### 1.3 亮色和暗色主题

支持亮色和暗色主题。默认情况下尊重系统设置。

```kotlin
// Compose: 检测系统主题
val darkTheme = isSystemInDarkTheme()
```

**规则：**
- R1.7: 始终支持亮色和暗色主题。永远不要仅支持亮色。
- R1.8: 暗色主题表面使用基于高度的色调映射，而不是纯黑色 (#000000)。使用处理此映射自动的颜色角色。
- R1.9: 在应用设置中提供手动主题覆盖（系统 / 亮色 / 暗色）。

### 1.4 自定义颜色种子

当品牌需要自定义颜色时，提供种子颜色并使用材质主题构建器生成色调调色板。

```kotlin
// 使用品牌种子生成的自定义颜色方案
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
- R1.11: 使用自定义颜色时，仍然将动态颜色作为默认值，并将自定义颜色作为回退使用。

---

## 2. 导航 [关键]

### 2.1 导航栏（底部）

适用于具有 3-5 个顶级目的地的手机的 PRIMARY 导航模式。

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
- R2.1: 在紧凑屏幕上使用导航栏，用于 3-5 个顶级目的地。永远不要用于少于 3 个或多于 5 个。
- R2.2: 始终在导航栏项上显示标签。不允许仅使用图标的导航栏。
- R2.3: 使用填充图标表示选中状态，使用轮廓图标表示未选中状态。
- R2.4: 活动指示器使用 `secondaryContainer` 颜色。不要覆盖此设置。

### 2.2 导航栏

适用于中等和扩展屏幕（平板电脑、折叠屏、桌面）。

```kotlin
// Compose: 用于较大屏幕的导航栏
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
- R2.5: 在中等（600-839dp）和扩展（840dp+）窗口大小上使用导航栏。在紧凑屏幕上配合导航栏使用。
- R2.6: 可选地包括 FAB 在栏头中，用于主要操作。
- R2.7: 栏上的标签是可选的，但建议使用以增强清晰度。

### 2.3 导航抽屉

适用于 5 个或更多目的地或复杂的导航层次结构，通常在扩展屏幕上。

```kotlin
// Compose: 用于较大屏幕的永久导航抽屉
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
- R2.9: 将抽屉项分组到具有分隔线和部分标题的各个部分。

### 2.4 预测返回手势

Android 13 及以上版本支持带动画预览的预测返回。

```kotlin
// Compose: 使用 BackHandler (androidx.activity.compose) 的预测返回
BackHandler(enabled = true) {
    // 当确认返回时调用；在您的导航控制器中返回
    navController.popBackStack()
}
```

```kotlin
// Compose: 使用 predictiveBackHandler 修饰符的预测返回进度动画
// (androidx.activity:activity-compose 1.8+)
Modifier.predictiveBackHandler(enabled = true) { progress ->
    progress.collect { backEvent ->
        animationState = backEvent.progress
    }
}
```

```xml
<!-- AndroidManifest.xml: 选择预测返回 -->
<application android:enableOnBackInvokedCallback="true">
```

**规则：**
- R2.10: 在清单中选择预测返回。在 **Compose** 应用中，使用 `BackHandler`（来自 `androidx.activity.compose`）来拦截返回事件。在 **基于 View** 的应用中，使用 `OnBackInvokedCallback`（API 33+）或 `OnBackPressedCallback`（AndroidX）而不是覆盖 `onBackPressed()`。
- R2.11: 系统返回手势在导航堆栈中导航。向上按钮（工具栏箭头）在应用层次结构中导航。这些可能不同。
- R2.12: 除非有未保存的用户输入，否则永远不要拦截系统返回以显示“确定吗？”对话框。
- R2.13: 不要抑制系统提供的返回预览动画。如果您实现了自定义进入/退出过渡，请使用 `BackEventCompat.progress`（0.0–1.0）进行插值，并尊重 `BackEventCompat.swipeEdge` (`EDGE_LEFT`/`EDGE_RIGHT`），以便退出屏幕缩放并朝向启动边缘移动，匹配系统动画。
- R2.14: 优先识别而不是召回。保持目的地标记，选中状态可见，并保留返回堆栈上下文，以便用户在每次导航步骤后都不必重新构建他们所在的位置。

```kotlin
// Compose: 从预测返回进度驱动自定义动画
Modifier.predictiveBackHandler(enabled = true) { progress ->
    progress.collect { backEvent ->
        // backEvent.progress: 0.0（手势开始）→ 1.0（提交）
        // backEvent.swipeEdge: BackEventCompat.EDGE_LEFT 或 EDGE_RIGHT
        exitScale = 1f - (backEvent.progress * 0.1f)
        exitOffsetX = if (backEvent.swipeEdge == BackEventCompat.EDGE_LEFT) -backEvent.progress * 32.dp.toPx() else backEvent.progress * 32.dp.toPx()
    }
}
```

### 2.5 导航组件选择

| 屏幕大小 | 3-5 目的地 | 5+ 目的地 |
|-------------|-------------------|-----------------|
| 紧凑 (< 600dp) | 导航栏 | 模态抽屉 + 导航栏 |
| 中等 (600-839dp) | 导航栏 | 模态抽屉 + 导航栏 |
| 扩展 (840dp+) | 导航栏 | 永久抽屉 |

---

## 3. 布局 & 响应式 [高]

### 3.1 窗口大小类别

使用窗口大小类别进行自适应布局，而不是原始像素断点。

```kotlin
// Compose: 窗口大小类别
val windowSizeClass = calculateWindowSizeClass(this)
when (windowSizeClass.widthSizeClass) {
    WindowWidthSizeClass.Compact -> CompactLayout()
    WindowWidthSizeClass.Medium -> MediumLayout()
    WindowWidthSizeClass.Expanded -> ExpandedLayout()
}
```

| 类 | 宽度 | 典型设备 | 列数 |
|-------|-------|----------------|---------|
| Compact | < 600dp | 手机竖屏 | 4 |
| Medium | 600-839dp | 平板竖屏、折叠屏 | 8 |
| Expanded | 840dp+ | 平板横屏、桌面 | 12 |

**规则：**
- R3.1: 始终使用 `WindowSizeClass` 从 `material3-window-size-class` 进行响应式布局决策。
- R3.2: 永远不要使用固定的像素断点。设备类别是流动的。
- R3.3: 支持所有三个宽度大小类别。至少支持紧凑和扩展。

### 3.2 材质网格

应用标准的材质网格边距和间隙。

| 大小类别 | 边距 | 间隙 | 列数 |
|------------|---------|---------|---------|
| Compact | 16dp | 8dp | 4 |
| Medium | 24dp | 16dp | 8 |
| Expanded | 24dp | 24dp | 12 |

**规则：**
- R3.4: 内容不应在扩展屏幕上跨越完整宽度。使用最大内容宽度约为 840dp 或列表-详情布局。
- R3.5: 应用与网格规范一致的水平和边距。

### 1.3 边缘到边缘显示

Android 15 及以上版本强制执行边缘到边缘。所有应用都应在系统栏后面绘制。

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
- R3.7: 使用 `WindowInsets` 将内容与系统栏隔开。`Scaffold` 自动处理顶部栏和底部栏内容的 inset。
- R3.8: 可滚动内容应滚动在透明的系统栏后面，并在列表的顶部和底部有适当的 inset 填充。

### 3.4 折叠设备支持

```kotlin
// Compose: 检测折叠姿势
val foldingFeatures = WindowInfoTracker.getOrCreate(context)
    .windowLayoutInfo(context)
    .collectAsState(initial = WindowLayoutInfo(emptyList()))
```

**规则：**
- R3.9: 检测铰链/折叠位置，并避免将关键内容放置在折叠处。
- R3.10: 使用 `ListDetailPaneScaffold` 或 `SupportingPaneScaffold` 从 Material3 自适应库中获取折叠感知布局。

---

## 4. 字体 [高]

### 4.1 材质类型比例

| 角色 | 默认大小 | 默认权重 | 用途 |
|------|-------------|----------------|-------|
| displayLarge | 57sp | 400 | 英雄文本、引导 |
| displayMedium | 45sp | 400 | 大型功能文本 |
| displaySmall | 36sp | 400 | 显著的显示 |
| headlineLarge | 32sp | 400 | 屏幕标题 |
| headlineMedium | 28sp | 400 | 章节标题 |
| headlineSmall | 24sp | 400 | 卡片标题 |
| titleLarge | 22sp | 400 | 顶部应用栏标题 |
| titleMedium | 16sp | 500 | 标签、导航 |
| titleSmall | 14sp | 500 | 副标题 |
| bodyLarge | 16sp | 400 | 主要正文 |
| bodyMedium | 14sp | 400 | 次要正文 |
| bodySmall | 12sp | 400 | 档案 |
| labelLarge | 14sp | 500 | 按钮突出显示的标签 |
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
- R4.2: 永远不要将正文设置低于 12sp。标签可降至 11sp 最小。
- R4.3: 从 `MaterialTheme.typography` 引用字体角色，而不是硬编码大小。
- R4.4: 支持动态类型缩放。在 200% 字体缩放下进行测试。确保没有文本被裁剪或重叠。
- R4.5: 行高应为字体大小的 1.2-1.5 倍，以提高可读性。

---

## 5. 组件 [高]

### 5.1 浮动操作按钮 (FAB)

浮动操作按钮代表屏幕上最重要的操作。

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
- R5.1: 每个屏幕最多使用一个 FAB。它代表主要操作。
- R5.2: 将 FAB 放置在屏幕的底部端。在具有导航栏的屏幕上，FAB 浮动在导航栏上方。
- R5.3: FAB 应使用 `primaryContainer` 颜色。在次要屏幕上使用 `tertiaryContainer`。
- R5.4: 建议使用带标签的 `ExtendedFloatingActionButton` 以提高清晰度。在滚动时折叠为仅图标（如果需要）。

### 5.2 顶部应用栏

```kotlin
// Compose: 顶部应用栏变体
// 小（默认）
TopAppBar(
    title = { Text("页面标题") },
    navigationIcon = {
        IconButton(onClick = { /* 导航向上 */ }) {
            Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "返回")
        }
    },
    actions = {
        IconButton(onClick = { /* 搜索 */ }) {
            Icon(Icons.Default.Search, contentDescription = "搜索")
        }
    }
)

// 中等 — 扩展标题区域
MediumTopAppBar(
    title = { Text("章节标题") },
    scrollBehavior = TopAppBarDefaults.enterAlwaysScrollBehavior()
)

// 大型 — 用于突出显示的标题
LargeTopAppBar(
    title = { Text("屏幕标题") },
    scrollBehavior = TopAppBarDefaults.exitUntilCollapsedScrollBehavior()
)
```

**规则：**
- R5.5: 使用 `TopAppBar`（小）用于大多数屏幕。使用 `MediumTopAppBar` 或 `LargeTopAppBar` 用于突出的章节或屏幕标题。
- R5.6: 将滚动行为连接到应用栏，以便它随着内容滚动而折叠/展开。
- R5.7: 限制操作图标为 2-3 个。将额外的操作放入更多菜单中。

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
- R5.8: 使用模态底部面板用于非关键补充内容。使用标准底部面板用于持久内容。
- R5.9: 底部面板必须有可见的拖动手柄以供发现。
- R5.10: 面板内容如果可以超出可见区域，必须可滚动。

### 5.4 对话框

```kotlin
// Compose: 警告对话框
AlertDialog(
    onDismissRequest = { showDialog = false },
    title = { Text("丢弃草稿？") },
    text = { Text("您将丢失未保存的更改。") },
    confirmButton = {
        TextButton(onClick = { /* 确认 */ }) { Text("丢弃") }
    },
    dismissButton = {
        TextButton(onClick = { showDialog = false }) { Text("取消") }
    }
)
```

**规则：**
- R5.11: 对话框中断用户。仅用于需要立即注意的决策。
- R5.12: 确认按钮使用文本按钮，而不是填充按钮。取消按钮始终在左侧。
- R5.13: 对话框标题应简洁的问题或陈述。正文文本提供上下文。

### 5.5 Snackbar

```kotlin
// Compose: 带操作的Snackbar
val snackbarHostState = remember { SnackbarHostState() }
Scaffold(snackbarHost = { SnackbarHost(snackbarHostState) }) {
    // 触发Snackbar
    LaunchedEffect(key) {
        val result = snackbarHostState.showSnackbar(
            message = "项目归档",
            actionLabel = "撤销",
            duration = SnackbarDuration.Short
        )
        if (result == SnackbarResult.ActionPerformed) { /* 撤销 */ }
    }
}
```

**规则：**
- R5.14: 使用 snackbars 用于简短、非关键的反馈。它们自动消失，不应包含关键信息。
- R5.15: snackbars 出现在屏幕底部，导航栏上方，FAB 下方。
- R5.16: 当操作可撤销时，包括一个操作（例如，“撤销”）。限制为最多一个操作。

### 5.6 芯片

```kotlin
// 过滤芯片
FilterChip(
    selected = isSelected,
    onClick = { isSelected = !isSelected },
    label = { Text("过滤") },
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
- R5.17: 使用 `FilterChip` 用于切换过滤器，`AssistChip` 用于智能建议，`InputChip` 用于用户输入的内容（标签），`SuggestionChip` 用于动态生成的建议。
- R5.18: 芯片应水平滚动排列在一行或流布局中，而不是垂直堆叠。
- R5.19: 立即显示等待状态。如果操作无法立即完成，请使用内联状态更改、进度或另一个可见响应，而不是让 UI 保持静态。

### 5.7 组件选择指南

| 需要 | 组件 |
|------|-------|
| 主要屏幕操作 | FAB |
| 简短反馈 | Snackbar |
| 关键决策 | 对话框 |
| 补充内容 | 底部面板 |
| 切换过滤器 | 过滤芯片 |
| 用户输入标签 | 输入芯片 |
| 智能建议 | 辅助芯片 |
| 内容组 | 卡片 |
| 垂直项目列表 | 带ListItem的LazyColumn |
| 分段选项（2-5） | SegmentedButton |
| 二进制切换 | Switch |
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

// 装饰元素
Icon(
    Icons.Default.Star,
    contentDescription = null // null 用于纯装饰
)

// 合并语义以供复合元素
Row(modifier = Modifier.semantics(mergeDescendants = true) {}) {
    Icon(Icons.Default.Event, contentDescription = null)
    Text("March 15, 2026")
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
- R6.1: 每个交互元素必须有 `contentDescription`（如果为纯装饰则 `null`）。
- R6.2: 内容描述必须描述操作或含义，而不是视觉外观。说“添加到收藏夹”而不是“心形图标”。
- R6.3: 使用 `mergeDescendants = true` 将相关元素组合成一个 TalkBack 聚焦单元（例如，列表项中的图标+文本+副标题）。
- R6.4: 为 TalkBack 用户提供 `customActions` 以访问滑动删除或长按操作。

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
    Icon(Icons.Default.Info, contentDescription = null, modifier = Modifier.size(24.dp))
}
```

**规则：**
- R6.5: 所有交互元素必须有 48x48dp 的最小触摸目标。材质 3 组件默认处理此设置。
- R6.6: 不要减少触摸目标以节省空间。如果视觉元素较小，请使用填充增加可触摸区域。

### 6.3 颜色对比和视觉

**规则：**
- R6.7: 文本对比度比率必须至少为 4.5:1（正常文本）和 3:1（18sp+ 或 14sp+ 粗体）与其背景。
- R6.8: 永远不要仅使用颜色来传达信息。与图标、文本或模式配对使用。
- R6.9: 支持粗体文本和高对比度辅助设置。使用 `Configuration.fontWeightAdjustment`（API 31+）检测用户的粗体文本偏好并相应地调整自定义字体权重。使用 `AccessibilityManager.isHighTextContrastEnabled()` 检测高对比度模式并替换为更高对比度的颜色值。材质 3 组件自动处理这两个设置；自定义文本渲染和颜色使用必须明确显式输入。

```kotlin
// 检测粗体文本偏好（API 31+）
val fontWeightAdjustment = resources.configuration.fontWeightAdjustment
val isBoldText = fontWeightAdjustment >= 700 // 等效于 FontWeight.Bold.weight
```

```kotlin
// 检测高对比度模式
val am = getSystemService(Context.ACCESSIBILITY_SERVICE) as AccessibilityManager
val isHighContrast = am.isHighTextContrastEnabled
```

```kotlin
// Compose: 使用 MaterialTheme.typography，它会自动尊重 fontWeightAdjustment
Text(
    text = "标签",
    style = MaterialTheme.typography.bodyLarge // 自动适应 fontWeightAdjustment
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
- R6.10: 聚焦顺序必须遵循逻辑阅读顺序（从上到下，从左到右）。除非默认顺序不正确，否则不要使用自定义 `focusOrder`。
- R6.11: 在导航或对话框关闭后，将焦点移动到最合理的目标元素。
- R6.12: 所有屏幕都必须可以使用 TalkBack、Switch Access 和外部键盘完全操作。

### 6.5 自定义画布视图

自定义 `View` 子类在画布上绘制内容（图表、自定义选择器、绘图表面）默认情况下对 TalkBack 不可见，因为它们没有子视图。使用 `ExploreByTouchHelper` 从 `androidx.customview.widget` 定义一个虚拟可访问性树。

- R6.13: 自定义画布绘制的视图必须使用 `ExploreByTouchHelper` 暴露虚拟可访问性树。覆盖 `getVirtualViewAt()` 以将触摸坐标映射到虚拟视图 ID，并使用 `onPopulateNodeForVirtualView()` 为每个虚拟节点提供文本、边界和操作。
