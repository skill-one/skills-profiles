---
name: compose-expert
description: 用于共享可组合组件的高级跨平台 UI 模式。在处理视觉 UI 组件、状态管理模式（记住，derivedStateOf、produceState）、重组优化（@Stable/@Immutable 视觉使用）、Material3 主题、自定义 ImageVector 图标，或决定在 commonMain 共享 UI 还是保留平台特定时使用。将平台入口点（Activity、Window、托盘）委托给 android-expert/桌面专家；导航壳本身是共享 UI。与 kotlin-expert 协作（处理状态/注解的 Kotlin 语言方面）。
---

# 多平台专家

跨 Android 和桌面平台共享可组合组件的视觉 UI 模式。

## 何时使用此技能

- 创建或重构共享的 UI 组件
- 决定是否在 `commonMain` 中共享 UI 或保持平台特定
- 构建自定义 ImageVector 图标（robohash 模式）
- 状态管理：remember，derivedStateOf，produceState
- 重组优化：@Stable/@Immutable 的视觉使用
- Material3 主题和样式
- 性能：懒加载列表，图像加载

**委托给其他技能：**
- 导航结构 → `android-expert`，`desktop-expert`
- Kotlin 状态模式（StateFlow，sealed classes）→ `kotlin-expert`
- 构建配置 → `gradle-expert`

## 哲学：默认共享

**默认使用 `commonsUI/commonMain`**（共享可组合组件位于 `:commonsUI`，共享层的 Compose 部分；无头状态/ViewModels 停留在 `:commons`），除非平台专家指示否则。

### 总是共享

- **UI 组件**：按钮，卡片，列表，对话框，输入
- **状态可视化**：加载中，空，错误状态
- **自定义图标**：ImageVector 资产（robohash，自定义路径）
- **主题实用工具**：颜色计算，样式辅助工具
- **Material3 组件**：使用 Material 基本元素的任何 UI

**屏幕和导航也共享。** Android 也发布在笔记本电脑上，新的桌面应用程序渲染相同的 UI，因此屏幕，导航主机和底部栏/轨道/永久抽屉都属于 `commonsUI`。它们通过 `ScreenLayoutSpec` / `LocalScreenLayout` 适应窗口，而不是按平台。参见 `commons/plans/2026-09-27-one-ui-android-desktop.md`。

### 保持平台特定

- **入口点**：Android `Activity`/`Service`，桌面 `Window`，托盘，菜单栏
- **系统集成**：文件选择器，通知，共享表单，相机，media3，WebView
- **共享 UI 中的平台特定部分**：在 expect/actual 后面或 shim 填充的槽中

### 决策框架

1. **仅使用 Material3 基本元素？** → 共享在 `commonMain`
2. **需要平台系统 API？** → 平台特定
3. **纯视觉组件，没有导航？** → 共享在 `commonMain`
4. **需要平台 UX 模式？** → 询问 `android-expert` 或 `desktop-expert`

如有不确定，**默认共享** - 拆分比合并更容易。

## 共享可组合组件的结构

### 结构

```kotlin
@Composable
fun SharedComponent(
    // 状态参数（只读）
    data: DataClass，
    isLoading: Boolean，
    // 事件参数（只写）
    onAction: () -> Unit，
    // 视觉参数
    modifier: Modifier = Modifier，
    // 可选的自定义
    colors: ComponentColors = ComponentDefaults.colors()
) {
    // 实现
}
```

**模式**：状态向下，事件向上
- modifier 之上的参数 = 必要的状态/事件
- `modifier` 参数 = 布局控制
- modifier 之下的参数 = 可选的自定义

### 示例：AddButton

```kotlin
@Composable
fun AddButton(
    onClick: () -> Unit，
    modifier: Modifier = Modifier，
    text: String = "Add"，
    enabled: Boolean = true
) {
    OutlinedButton(
        modifier = modifier，
        enabled = enabled，
        onClick = onClick，
        shape = ActionButtonShape，
        contentPadding = ActionButtonPadding
    ) {
        Text(text = text, textAlign = TextAlign.Center)
    }
}

// 共享的常量用于一致性
val ActionButtonShape = RoundedCornerShape(20.dp)
val ActionButtonPadding = PaddingValues(vertical = 0.dp, horizontal = 16.dp)
```

**为什么这在所有平台上都有效：**
- Material3 基本元素（OutlinedButton，Text）
- 没有平台 API
- 通过参数进行配置
- 通过共享常量保持一致的样式

## 状态管理模式

### remember - 跨重组缓存

```kotlin
@Composable
fun ExpandableCard() {
    var isExpanded by remember { mutableStateOf(false) }

    Column {
        IconButton(onClick = { isExpanded = !isExpanded }) {
            Icon(
                if (isExpanded) Icons.Default.ExpandLess else Icons.Default.ExpandMore，
                contentDescription = if (isExpanded) "Collapse" else "Expand"
            )
        }

        if (isExpanded) {
            Text("Expanded content...")
        }
    }
}
```

**视觉模式**：切换按钮 → 状态更改 → UI 展开/收起
**用于**：简单的 UI 状态（切换，计数器，文本输入）

### derivedStateOf - 优化频繁更改

```kotlin
@Composable
fun ScrollToTopButton(listState: LazyListState) {
    // 仅在 showButton 更改时重组，而不是每个滚动像素
    val showButton by remember {
        derivedStateOf {
            listState.firstVisibleItemIndex > 0
        }
    }

    if (showButton) {
        FloatingActionButton(onClick = { /* scroll to top */ }) {
            Icon(Icons.Default.ArrowUpward, null)
        }
    }
}
```

**视觉模式**：滚动位置（0，1，2...）→ 布尔值（显示/隐藏）→ 按钮可见性
**用于**：输入频繁更改，派生结果很少更改
**性能**：防止每次滚动事件重组

### produceState - 异步到 Compose 状态

```kotlin
@Composable
fun LoadUserProfile(userId: String): State<User?> {
    return produceState<User?>(initialValue = null, userId) {
        value = repository.fetchUser(userId)
    }
}

@Composable
fun ProfileScreen(userId: String) {
    val user by LoadUserProfile(userId)

    when (user) {
        null -> LoadingState("Loading profile...")
        else -> ProfileCard(user!!)
    }
}
```

**视觉模式**：异步操作 → 状态更新 → UI 反映更改
**用于**：将 Flow，LiveData，回调转换为 Compose 状态
**生命周期**：当可组合组件离开组合时取消协程

对于 Kotlin 特定的状态模式（StateFlow，sealed classes），请参阅 `kotlin-expert`。

## 状态提升

将状态向上移动以使可组合组件可重用：

```kotlin
// ❌ 状态ful - 难以测试，无法外部控制
@Composable
fun BadSearchBar() {
    var query by remember { mutableStateOf("") }
    TextField(value = query, onValueChange = { query = it })
}

// ✅ 无状态 - 可重用，可测试
@Composable
fun GoodSearchBar(
    query: String，
    onQueryChange: (String) -> Unit，
    modifier: Modifier = Modifier
) {
    TextField(
        value = query，
        onValueChange = onQueryChange，
        modifier = modifier
    )
}

@Composable
fun SearchScreen() {
    var query by remember { mutableStateOf("") }

    Column {
        GoodSearchBar(query = query, onQueryChange = { query = it })
        SearchResults(query = query)
    }
}
```

**原则**：状态向上，事件向下
- 状态：`query: String`（只读参数）
- 事件：`onQueryChange: (String) -> Unit`（回调参数）

## 重组优化

### @Immutable 的视觉使用

在传递给可组合组件的数据类上使用 @Immutable：

```kotlin
@Immutable
data class UserProfile(val name: String, val avatar: String)

@Composable
fun ProfileCard(profile: UserProfile) {
    // 仅在 profile 实例更改时重组
    Row {
        RobohashImage(robot = profile.avatar)
        Text(profile.name, style = MaterialTheme.typography.titleMedium)
    }
}
```

**视觉效果**：当父级使用相同的数据重组时防止重组
**模式**：将参数数据类标记为 @Immutable
**注意**：有关 @Immutable 的 Kotlin 语言详细信息，请参阅 `kotlin-expert`

### Stable Parameters

```kotlin
// ✅ 稳定 - 除非颜色实例更改，否则不会触发重组
@Composable
fun ThemedCard(
    content: String，
    colors: CardColors = CardDefaults.colors()，
    modifier: Modifier = Modifier
) {
    Card(colors = colors, modifier = modifier) {
        Text(content)
    }
}
```

有关 @Stable 注释的详细信息，请参阅 `kotlin-expert`。

## Material3 主题

所有共享的可组合组件都使用 Material3 以保持一致性：

```kotlin
@Composable
fun ThemedComponent() {
    val bg = MaterialTheme.colorScheme.background
    val fg = MaterialTheme.colorScheme.onBackground
    val primary = MaterialTheme.colorScheme.primary

    Column(
        modifier = Modifier.background(bg)
    ) {
        Text(
            "Title",
            style = MaterialTheme.typography.headlineMedium，
            color = fg
        )
        Button(
            onClick = { /* ... */ }，
            colors = ButtonDefaults.buttonColors(containerColor = primary)
        ) {
            Text("Action")
        }
    }
}
```

**原则：**
- 颜色：`MaterialTheme.colorScheme.*`
- 字体：`MaterialTheme.typography.*`
- 形状：`MaterialTheme.shapes.*`

### 主题检测

```kotlin
@Composable
private fun isLightTheme(): Boolean {
    val background = MaterialTheme.colorScheme.background
    return (background.red + background.green + background.blue) / 3 > 0.5f
}

@Composable
fun ThemedIcon() {
    val isDark = !isLightTheme()
    val tint = if (isDark) Color.White else Color.Black
    Icon(Icons.Default.Face, null, tint = tint)
}
```

## 自定义图标：ImageVector 模式

Amethyst 使用 ImageVector 进行多平台图标。

### roboBuilder DSL

```kotlin
fun roboBuilder(block: Builder.() -> Unit): ImageVector {
    return ImageVector.Builder(
        name = "Robohash"，
        defaultWidth = 300.dp，
        defaultHeight = 300.dp，
        viewportWidth = 300f，
        viewportHeight = 300f
    ).apply(block).build()
}
```

### 构建图标

```kotlin
fun customIcon(fgColor: SolidColor, builder: Builder) {
    builder.addPath(pathData1, fill = fgColor, stroke = Black, strokeLineWidth = 1.5f)
    builder.addPath(pathData2, fill = Black, fillAlpha = 0.4f)
    builder.addPath(pathData3, fill = Black, fillAlpha = 0.2f)
}

private val pathData1 = PathData {
    moveTo(144.5f, 87.5f)
    reflectiveCurveToRelative(-51.0f, 3.0f, -53.0f, 55.0f)
    lineToRelative(16.0f, 16.0f)
    close()
}

@Composable
fun CustomIcon() {
    Image(
        painter = rememberVectorPainter(
            roboBuilder {
                customIcon(SolidColor(Color.Blue), this)
            }
        )，
        contentDescription = "Custom icon"
    )
}
```

**为什么使用 ImageVector？**
- 纯 Kotlin，无 XML
- 在 Android，桌面，iOS 上都有效
- GPU 加速
- 类型安全

### 缓存模式

```kotlin
object CustomIcons {
    private val cache = mutableMapOf<String, ImageVector>()

    fun get(key: String): ImageVector {
        return cache.getOrPut(key) {
            buildIcon(key)
        }
    }
}

@Composable
fun CachedIcon(key: String) {
    Image(imageVector = CustomIcons.get(key), contentDescription = null)
}
```

有关详细图标模式，请参阅 `references/icon-assets.md`。

## 常见视觉模式

### 状态可视化

```kotlin
@Composable
fun DataScreen(uiState: UiState) {
    when (uiState) {
        is UiState.Loading -> LoadingState("Loading...")
        is UiState.Empty -> EmptyState(
            title = "No data",
            onRefresh = { /* refresh */ }
        )
        is UiState.Error -> ErrorState(
            message = uiState.message，
            onRetry = { /* retry */ }
        )
        is UiState.Success -> ContentList(uiState.items)
    }
}
```

**组件**（全部位于 `commonsUI/commonMain`）：
- `LoadingState` - 进度指示器 + 消息
- `EmptyState` - 空消息 + 可选刷新按钮
- `ErrorState` - 错误消息 + 可选重试按钮

### Relay 状态（Amethyst 模式）

```kotlin
@Composable
fun RelayStatusIndicator(connectedCount: Int) {
    val statusColor = when {
        connectedCount == 0 -> RelayStatusColors.Disconnected
        connectedCount < 3 -> RelayStatusColors.Connecting
        else -> RelayStatusColors.Connected
    }

    Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
        Icon(
            imageVector = if (connectedCount > 0) Icons.Default.Check else Icons.Default.Close，
            tint = statusColor，
            modifier = Modifier.size(16.dp)
        )
        Text(
            "$connectedCount relay${if (connectedCount != 1) "s" else ""}"，
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
    }
}
```

**视觉映射**：
- 0 个中继 → 红色 + X 图标
- 1-2 个中继 → 黄色 + 检查图标
- 3 个以上中继 → 绿色 + 检查图标

### 占位符模式

```kotlin
@Composable
fun PlaceholderScreen(
    title: String，
    description: String，
    modifier: Modifier = Modifier
) {
    Column(modifier = modifier) {
        Text(title, style = MaterialTheme.typography.headlineMedium)
        Spacer(Modifier.height(16.dp))
        Text(description, color = MaterialTheme.colorScheme.onSurfaceVariant)
    }
}

// 具体实现
@Composable
fun SearchPlaceholder() = PlaceholderScreen(
    title = "Search"，
    description = "Search for users, notes, and hashtags."
)
```

**模式**：通用可组合组件 + 具有预设文本的特定包装器

## 性能

### 避免不必要的重组

```kotlin
// ❌ 坏 - 每次滚动时重组
@Composable
fun BadButton(scrollState: ScrollState) {
    if (scrollState.value > 100) {
        Button(onClick = {}) { Text("Top") }
    }
}

// ✅ 好 - 仅在可见性更改时重组
@Composable
fun GoodButton(scrollState: ScrollState) {
    val show by remember { derivedStateOf { scrollState.value > 100 } }
    if (show) {
        Button(onClick = {}) { Text("Top") }
    }
}
```

### 懒加载列表

```kotlin
@Composable
fun FeedList(items: List<Item>) {
    LazyColumn {
        items(items, key = { it.id }) { item ->
            FeedItem(item)
        }
    }
}
```

**关键原则**：使用 `key` 参数进行稳定的项身份

## 嵌套资源

- **references/shared-composables-catalog.md** - 完整的共享 UI 组件目录
- **references/state-patterns.md** - 带有视觉示例的状态管理模式
- **references/icon-assets.md** - 自定义 ImageVector 图标模式
- **references/rich-text-parsing.md** - `RichTextParser`，`UrlParser`，`GalleryParser`，`Patterns`，`MediaContentModels`；NIP-92 imeta 增强功能
- **scripts/find-composables.sh** - 在代码库中查找所有 @Composable 函数

## 快速参考

| 任务 | 模式 | 位置 |
|------|------|------|
| 可重用 UI | 状态提升 | commonsUI/commonMain |
| 简单状态 | remember { mutableStateOf() } | 可组合组件范围 |
| 派生状态 | derivedStateOf { } | remember 块 |
| 异步 → 状态 | produceState { } | 可组合函数 |
| 自定义图标 | roboBuilder + PathData | commonsUI/icons |
| 加载/错误 | LoadingState，ErrorState | commonsUI/ui/components |
| 主题颜色 | MaterialTheme.colorScheme | 任何 @Composable |
| 导航 | 委托给平台专家 | amethyst/，desktopApp/ |

## 常见工作流程

### 创建共享组件

1. 在 `commonsUI/src/commonMain/kotlin/.../ui/components/` 中开始
2. 仅使用 Material3 基本元素
3. 提升状态（数据参数，事件回调）
4. 添加 modifier 参数
5. 使用 MaterialTheme 进行颜色/字体
6. 在 Android 和桌面上进行测试

### 转换现有组件

1. 在 `amethyst/` 或 `desktopApp/` 中读取当前实现
2. 确定纯视觉逻辑（没有平台 API）
3. 在 `commonsUI/commonMain` 中创建，提升状态
4. 用共享组件替换平台实现
5. 如有必要，保留平台特定包装器

### 自定义图标

1. 从设计工具导出 SVG
2. 使用 Android Studio 将其转换为 PathData
3. 使用 roboBuilder 创建图标函数
4. 如有必要，添加缓存（如果动态生成）
5. 用 @Composable 包裹以方便使用

### 导航

导航外壳是共享的（`ScreenLayoutSpec` 通过窗口大小选择底部栏，轨道或永久抽屉），正在迁移到 `commonsUI` 与 `AppNavigation`。仅委托平台叶子：
- Activity / intent 管道 → `android-expert`
- Window，托盘，菜单栏，多窗口 → `desktop-expert`
- 旧的 `desktopApp` 侧边栏外壳 → `desktop-expert`（将被替换）

## 相关技能

- **kotlin-expert** - Kotlin语言方面 (@Immutable细节, StateFlow, 封装类)
- **android-expert** - Android导航, 平台API
- **desktop-expert** - 桌面导航, 窗口管理, 操作系统特定
- **kotlin-coroutines** - 异步模式, Flow集成
