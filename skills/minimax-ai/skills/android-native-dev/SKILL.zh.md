---
name: android-native-dev
description: Android原生应用开发与UI设计指南。涵盖Material Design 3、Kotlin/Compose开发、项目配置、无障碍访问及构建故障排除。在开始Android原生应用开发前，请先阅读此指南。
---

## 1. 项目场景评估

在开始开发之前，评估当前项目状态：

| 场景 | 特征 | 方法 |
|------|------|------|
| **空目录** | 不存在文件 | 需要完全初始化，包括 Gradle Wrapper |
| **存在 Gradle Wrapper** | 存在 `gradlew` 和 `gradle/wrapper/` | 直接使用 `./gradlew` 进行构建 |
| **Android Studio 项目** | 完整的项目结构，可能缺少 Wrapper | 检查 Wrapper，如有需要运行 `gradle wrapper` |
| **不完整项目** | 存在部分文件 | 检查缺失文件，完成配置 |

**关键原则**：
- 在编写业务逻辑之前，确保 `./gradlew assembleDebug` 成功
- 如果缺少 `gradle.properties`，先创建它并配置 AndroidX

### 1.1 必要文件清单

```
MyApp/
├── gradle.properties          # 配置 AndroidX 和其他设置
├── settings.gradle.kts
├── build.gradle.kts           # 根级别
├── gradle/wrapper/
│   └── gradle-wrapper.properties
├── app/
│   ├── build.gradle.kts       # 模块级别
│   └── src/main/
│       ├── AndroidManifest.xml
│       ├── java/com/example/myapp/
│       │   └── MainActivity.kt
│       └── res/
│           ├── values/
│           │   ├── strings.xml
│           │   ├── colors.xml
│           │   └── themes.xml
│           └── mipmap-*/       # 应用图标
```

---

## 2. 项目配置

### 2.1 gradle.properties

```properties
# 必要配置
android.useAndroidX=true
android.enableJetifier=true

# 构建优化
org.gradle.parallel=true
kotlin.code.style=official

# JVM 内存设置（根据项目大小调整）
# 小型项目：2048m，中型：4096m，大型：8192m+
# org.gradle.jvmargs=-Xmx4096m -Dfile.encoding=UTF-8
```

> **注意**：如果在构建过程中遇到 `OutOfMemoryError`，请增加 `-Xmx` 值。具有大量依赖的大型项目可能需要 8GB 或更多。

### 2.2 依赖声明标准

```kotlin
dependencies {
    // 使用 BOM 管理Compose版本
    implementation(platform("androidx.compose:compose-bom:2024.02.00"))
    implementation("androidx.compose.ui:ui")
    implementation("androidx.compose.material3:material3")
    
    // Activity & ViewModel
    implementation("androidx.activity:activity-compose:1.8.2")
    implementation("androidx.lifecycle:lifecycle-viewmodel-compose:2.7.0")
}
```

### 2.3 构建变体与产品风味

产品风味允许你创建应用的不同版本（例如，免费/付费，开发/测试/生产）。

**在 app/build.gradle.kts 中配置**：

```kotlin
android {
    // 定义风味维度
    flavorDimensions += "environment"
    
    productFlavors {
        create("dev") {
            dimension = "environment"
            applicationIdSuffix = ".dev"
            versionNameSuffix = "-dev"
            
            // 每个风味不同的配置值
            buildConfigField("String", "API_BASE_URL", "\"https://dev-api.example.com\"")
            buildConfigField("Boolean", "ENABLE_LOGGING", "true")
            
            // 不同的资源
            resValue("string", "app_name", "MyApp Dev")
        }
        
        create("staging") {
            dimension = "environment"
            applicationIdSuffix = ".staging"
            versionNameSuffix = "-staging"
            
            buildConfigField("String", "API_BASE_URL", "\"https://staging-api.example.com\"")
            buildConfigField("Boolean", "ENABLE_LOGGING", "true")
            resValue("string", "app_name", "MyApp Staging")
        }
        
        create("prod") {
            dimension = "environment"
            // 生产版本无后缀
            
            buildConfigField("String", "API_BASE_URL", "\"https://api.example.com\"")
            buildConfigField("Boolean", "ENABLE_LOGGING", "false")
            resValue("string", "app_name", "MyApp")
        }
    }
    
    buildTypes {
        debug {
            isDebuggable = true
            isMinifyEnabled = false
        }
        release {
            isDebuggable = false
            isMinifyEnabled = true
            proguardFiles(getDefaultProguardFile("proguard-android-optimize.txt"), "proguard-rules.pro")
        }
    }
}
```

**构建变体命名**：`{风味}{构建类型}` → 例如，`devDebug`，`prodRelease`

**Gradle 构建命令**：

```bash
# 列出所有可用的构建变体
./gradlew tasks --group="build"

# 构建特定变体（风味 + 构建类型）
./gradlew assembleDevDebug        # 开发风味，Debug 构建
./gradlew assembleStagingDebug    # 测试风味，Debug 构建
./gradlew assembleProdRelease     # 生产风味，Release 构建

# 构建特定风味的所有变体
./gradlew assembleDev             # 所有开发变体（debug + release）
./gradlew assembleProd            # 所有生产变体

# 构建特定构建类型的所有变体
./gradlew assembleDebug           # 所有风味，Debug 构建
./gradlew assembleRelease         # 所有风味，Release 构建

# 将特定变体安装到设备
./gradlew installDevDebug
./gradlew installProdRelease

# 一次性构建并安装
./gradlew installDevDebug && adb shell am start -n com.example.myapp.dev/.MainActivity
```

**在代码中访问 BuildConfig**：

> **注意**：从 AGP 8.0 开始，`BuildConfig` 默认不再生成。你必须在你的 `build.gradle.kts` 中显式启用它：
> ```kotlin
> android {
>     buildFeatures {
>         buildConfig = true
>     }
> }
> ```

```kotlin
// 在代码中使用 build config 值
val apiUrl = BuildConfig.API_BASE_URL
val isLoggingEnabled = BuildConfig.ENABLE_LOGGING

if (BuildConfig.DEBUG) {
    // 仅 Debug 代码
}
```

**风味特定源集**：

```
app/src/
├── main/           # 所有风味共享的代码
├── dev/            # 仅开发使用的代码和资源
│   ├── java/
│   └── res/
├── staging/        # 仅测试使用的代码和资源
├── prod/           # 仅生产使用的代码和资源
├── debug/          # Debug 构建类型的代码
└── release/        # Release 构建类型的代码
```

**多个风味维度**（例如，环境 + 层级）：

```kotlin
android {
    flavorDimensions += listOf("environment", "tier")
    
    productFlavors {
        create("dev") { dimension = "environment" }
        create("prod") { dimension = "environment" }
        
        create("free") { dimension = "tier" }
        create("paid") { dimension = "tier" }
    }
}
// 结果为：devFreeDebug, devPaidDebug, prodFreeRelease, 等
```

---

## 3. Kotlin 开发标准

### 3.1 命名约定

| 类型 | 约定 | 示例 |
|------|------|------|
| 类/接口 | PascalCase | `UserRepository`, `MainActivity` |
| 函数/变量 | camelCase | `getUserName()`, `isLoading` |
| 常量 | SCREAMING_SNAKE | `MAX_RETRY_COUNT` |
| 包 | 小写 | `com.example.myapp` |
| Composable | PascalCase | `@Composable fun UserCard()` |

### 3.2 代码标准（重要）

**空安全**：
```kotlin
// ❌ 避免：非空断言 !!（可能崩溃）
val name = user!!.name

// ✅ 推荐：安全调用 + 默认值
val name = user?.name ?: "Unknown"

// ✅ 推荐：let 处理
user?.let { processUser(it) }
```

**异常处理**：
```kotlin
// ❌ 避免：在业务层随机使用 try-catch 吞噬异常
fun loadData() {
    try {
        val data = api.fetch()
    } catch (e: Exception) {
        // 吞噬异常，难以调试
    }
}

// ✅ 推荐：异常向上传递，在适当层处理
suspend fun loadData(): Result<Data> {
    return try {
        Result.success(api.fetch())
    } catch (e: Exception) {
        Result.failure(e)  // 包装并返回，让调用者决定处理
    }
}

// ✅ 推荐：在 ViewModel 中统一处理
viewModelScope.launch {
    runCatching { repository.loadData() }
        .onSuccess { _uiState.value = UiState.Success(it) }
        .onFailure { _uiState.value = UiState.Error(it.message) }
}
```

### 3.3 线程 & 协程（关键）

**线程选择原则**：

| 操作类型 | 线程 | 描述 |
|----------|------|------|
| UI 更新 | `Dispatchers.Main` | 更新视图、状态、LiveData |
| 网络请求 | `Dispatchers.IO` | HTTP 调用、API 请求 |
| 文件 I/O | `Dispatchers.IO` | 本地存储、数据库操作 |
| 计算密集型 | `Dispatchers.Default` | JSON 解析、排序、加密 |

**正确用法**：
```kotlin
// 在 ViewModel 中
viewModelScope.launch {
    // 默认 Main 线程，可以更新 UI State
    _uiState.value = UiState.Loading
    
    // 切换到 IO 线程进行网络请求
    val result = withContext(Dispatchers.IO) {
        repository.fetchData()
    }
    
    // 自动返回 Main 线程，更新 UI
    _uiState.value = UiState.Success(result)
}

// 在 Repository（挂起函数应该是主线程安全的）
suspend fun fetchData(): Data = withContext(Dispatchers.IO) {
    api.getData()
}
```

**常见错误**：
```kotlin
// ❌ 错误：在 IO 线程上更新 UI
viewModelScope.launch(Dispatchers.IO) {
    val data = api.fetch()
    _uiState.value = data  // 可能崩溃或警告！
}

// ❌ 错误：在 Main 线程上执行耗时操作
viewModelScope.launch {
    val data = api.fetch()  // 阻塞 Main 线程！ANR
}

// ✅ 正确：IO 线程获取，Main 线程更新
viewModelScope.launch {
    val data = withContext(Dispatchers.IO) { api.fetch() }
    _uiState.value = data
}
```

### 3.4 可见性规则

```kotlin
// 默认是 public，需要时显式声明
class UserRepository {           // public
    private val cache = mutableMapOf<String, User>()  // 仅类内部可见
    internal fun clearCache() {} // 仅模块内可见
}

// data class 属性默认是 public，跨模块使用时需小心
data class User(
    val id: String,       // public
    val name: String
)
```

### 3.5 常见语法陷阱

```kotlin
// ❌ 错误：访问未初始化的 lateinit
class MyViewModel : ViewModel() {
    lateinit var data: String
    fun process() = data.length  // 可能崩溃
}

// ✅ 正确：使用可空或默认值
class MyViewModel : ViewModel() {
    var data: String? = null
    fun process() = data?.length ?: 0
}

// ❌ 错误：在 lambda 中使用 return
list.forEach { item ->
    if (item.isEmpty()) return  // 返回外部函数！
}

// ✅ 正确：使用 return@forEach
list.forEach { item ->
    if (item.isEmpty()) return@forEach
}
```

### 3.6 服务器响应数据类字段必须为可空

```kotlin
// ❌ 错误：字段声明为非空（服务器可能不返回它们）
data class UserResponse(
    val id: String = "",
    val name: String = "",
    val avatar: String = ""
)

// ✅ 正确：所有字段声明为可空
data class UserResponse(
    @SerializedName("id")
    val id: String? = null,
    @SerializedName("name")
    val name: String? = null,
    @SerializedName("avatar")
    val avatar: String? = null
)
```

### 3.7 生命周期资源管理

```kotlin
// ❌ 错误：仅添加 Observer，未移除
class MyView : View {
    override fun onAttachedToWindow() {
        super.onAttachedToWindow()
        activity?.lifecycle?.addObserver(this)
    }
    // 内存泄漏！
}

// ✅ 正确：配对添加和移除
class MyView : View {
    override fun onAttachedToWindow() {
        super.onAttachedToWindow()
        activity?.lifecycle?.addObserver(this)
    }

    override fun onDetachedFromWindow() {
        activity?.lifecycle?.removeObserver(this)
        super.onDetachedFromWindow()
    }
}
```

### 3.8 日志级别使用

```kotlin
import android.util.Log

// Info：正常流程中的关键检查点
Log.i(TAG, "loadData: started, userId = $userId")

// Warning：异常但可恢复的情况
Log.w(TAG, "loadData: cache miss, fallback to network")

// Error：失败/错误情况
Log.e(TAG, "loadData failed: ${error.message}")
```

| 级别 | 用法 |
|------|------|
| `i` (Info) | 正常流程、方法入口、关键参数 |
| `w` (Warning) | 可恢复异常、降级处理、空返回 |
| `e` (Error) | 请求失败、捕获异常、不可恢复错误 |

---

## 4. Jetpack Compose 标准

### 4.1 @Composable 上下文规则

```kotlin
// ❌ 错误：从非 Composable 函数调用 Composable
fun showError(message: String) {
    Text(message)  // 编译错误！
}

// ✅ 正确：标记为 @Composable
@Composable
fun ErrorMessage(message: String) {
    Text(message)
}

// ❌ 错误：在 LaunchedEffect 外部使用 suspend
@Composable
fun MyScreen() {
    val data = fetchData()  // 错误！
}

// ✅ 正确：使用 LaunchedEffect
@Composable
fun MyScreen() {
    var data by remember { mutableStateOf<Data?>(null) }
    LaunchedEffect(Unit) {
        data = fetchData()
    }
}
```

### 4.2 状态管理

```kotlin
// 基本状态
var count by remember { mutableStateOf(0) }

// 派生状态（避免冗余计算）
val isEven by remember { derivedStateOf { count % 2 == 0 } }

// 跨重组合持久化（例如，滚动位置）
val scrollState = rememberScrollState()

// ViewModel 中的状态
class MyViewModel : ViewModel() {
    private val _uiState = MutableStateFlow(UiState())
    val uiState: StateFlow<UiState> = _uiState.asStateFlow()
}
```

### 4.3 Compose 常见错误

```kotlin
// ❌ 错误：在 Composable 中创建对象（每次重组都会创建）
@Composable
fun MyScreen() {
    val viewModel = MyViewModel()  // 错误！
}

// ✅ 正确：使用 viewModel() 或 remember
@Composable
fun MyScreen(viewModel: MyViewModel = viewModel()) {
    // ...
}
```

---

## 5. 资源 & 图标

### 5.1 应用图标要求

必须提供多分辨率图标：

| 目录 | 尺寸 | 用途 |
|------|------|------|
| mipmap-mdpi | 48x48 | 基准 |
| mipmap-hdpi | 72x72 | 1.5x |
| mipmap-xhdpi | 96x96 | 2x |
| mipmap-xxhdpi | 144x144 | 3x |
| mipmap-xxxhdpi | 192x192 | 4x |

推荐：使用自适应图标（Android 8+）：

```xml
<!-- res/mipmap-anydpi-v26/ic_launcher.xml -->
<adaptive-icon>
    <background android:drawable="@color/ic_launcher_background"/>
    <foreground android:drawable="@mipmap/ic_launcher_foreground"/>
</adaptive-icon>
```

### 5.2 资源命名约定

| 类型 | 前缀 | 示例 |
|------|------|------|
| 布局 | layout_ | `layout_main.xml` |
| 图片 | ic_, img_, bg_ | `ic_user.png` |
| 颜色 | color_ | `color_primary` |
| 字符串 | - | `app_name`, `btn_submit` |

### 5.3 避免 Android 保留名称（重要）

变量名、资源 ID、颜色、图标和 XML 元素**必须**不使用 Android 保留词或系统资源名称。使用保留名称会导致构建错误或资源冲突。

**常见的保留名称要避免**：

| 类别 | 保留名称（不要使用） |
|------|----------------------|
| 颜色 | `background`, `foreground`, `transparent`, `white`, `black` |
| 图标/可绘制 | `icon`, `logo`, `image`, `drawable` |
| 视图 | `view`, `text`, `button`, `layout`, `container` |
| 属性 | `id`, `name`, `type`, `style`, `theme`, `color` |
| 系统 | `app`, `android`, `content`, `data`, `action` |

**示例**：

```xml
<!-- ❌ 错误：使用保留名称 -->
<color name="background">#FFFFFF</color>
<color name="icon">#000000</color>

<!-- ✅ 正确：添加前缀或特定命名 -->
<color name="app_background">#FFFFFF</color>
<color name="icon_primary">#000000</color>
```

```kotlin
// ❌ 错误：变量名与系统冲突
val icon = R.drawable.my_icon
val background = Color.White

// ✅ 正确：使用描述性名称
val appIcon = R.drawable.my_icon
val screenBackground = Color.White
```

```xml
<!-- ❌ 错误：可绘制名称冲突 -->
<ImageView android:src="@drawable/icon" />

<!-- ✅ 正确：添加前缀 -->
<ImageView android:src="@drawable/ic_home" />
```

---

## 6. 构建错误诊断 & 修复

### 6.1 常见错误快速参考

| 错误关键字 | 原因 | 解决方法 |
|-----------|------|---------|
| `未解析的引用` | 缺少导入或未定义 | 检查导入，验证依赖 |
| `类型不匹配` | 类型不兼容 | 检查参数类型，添加转换 |
| `无法访问` | 可见性问题 | 检查公共/私有/内部 |
| `@Composable 调用` | Composable 上下文错误 | 确保调用者也是 @Composable |
| `重复的类` | 依赖冲突 | 使用 `./gradlew dependencies` 调查 |
| `AAPT: 错误` | 资源文件错误 | 检查 XML 语法和资源引用 |

### 6.2 最佳实践修复

1. **先阅读完整的错误信息**：定位文件和行号
2. **检查最近的更改**：问题通常在最新修改中
3. **清理构建**：`./gradlew clean assembleDebug`
4. **检查依赖版本**：版本冲突是常见原因
5. **如有需要刷新依赖**：清除缓存并重建

### 6.3 调试命令

```bash
# 清理和构建
./gradlew clean assembleDebug

# 查看依赖树（调查冲突）
./gradlew :app:dependencies

# 查看详细错误
./gradlew assembleDebug --stacktrace

# 刷新依赖
./gradlew --refresh-dependencies
```

---

## 7. Material Design 3 指南

检查 Android UI 文件是否符合 Material Design 3 指南和 Android 最佳实践。

### 设计理念

#### M3 核心原则

| 原则 | 描述 |
|------|------|
| **个性化** | 基于用户偏好和壁纸的动态颜色 |
| **自适应** | 在所有屏幕尺寸和形态上响应式 |
| **表现力** | 粗犷的颜色和排版，具有个性 |
| **可访问性** | 为所有用户设计的包容性设计 |

#### M3 表现力（最新）

最新版本通过以下方式增加情感驱动的用户体验：
- 鲜艳、动态的颜色
- 直觉的运动物理
- 自适应组件
- 灵活的排版
- 对比形状（新增 35 种形状选项）

### 应用风格选择

**关键决策**：将视觉风格与应用类别和目标受众相匹配。

| 应用类别 | 视觉风格 | 关键特征 |
|----------|----------|----------|
| 工具/实用 | 极简主义 | 干净、高效、中性颜色 |
| 金融/银行 | 专业信任 | 保守颜色、安全导向 |
| 健康/养生 | 宁静自然 | 柔和颜色、有机形状 |
| 儿童（3-5 岁） | 活泼简单 | 明亮颜色、大目标（56dp+） |
| 儿童（6-12 岁） | 趣味吸引 | 鲜艳、游戏化反馈 |
| 社交/娱乐 | 表现力 | 品牌驱动、手势丰富 |
| 生产力 | 干净专注 | 极简、高对比度 |
| 电子商务 | 转化导向 | 清晰的 CTA、可扫描 |

见 [设计风格指南](references/design-style-guide.md) 获取详细的风格配置文件。

### 快速参考：关键规范

#### 颜色对比要求

| 元素 | 最小比例 |
|------|----------|
| 正文文本 | **4.5:1** |
| 大文本（18sp+） | **3:1** |
| UI 组件 | **3:1** |

#### 触摸目标

| 类型 | 尺寸 |
|------|------|
| 最小 | 48 × 48dp |
| 推荐（主要操作） | 56 × 56dp |
| 儿童应用 | 56dp+ |
| 目标之间的间距 | 最小 8dp |

#### 8dp 网格系统

| 令牌 | 值 | 使用 |
|------|------|------|
| xs | 4dp | 图标填充 |
| sm | 8dp | 紧凑间距 |
| md | 16dp | 默认填充 |
| lg | 24dp | 区块间距 |
| xl | 32dp | 大间隙 |
| xxl | 48dp | 屏幕边距 |

#### 排版比例（摘要）

| 类别 | 尺寸 |
|------|------|
| 显示 | 57sp, 45sp, 36sp |
| 标题 | 32sp, 28sp, 24sp |
| 标签 | 22sp, 16sp, 14sp |
| 正文 | 16sp, 14sp, 12sp |
| 标签 | 14sp, 12sp, 11sp |

#### 动画持续时间

| 类型 | 持续时间 |
|------|----------|
| 微（涟漪） | 50-100ms |
| 短（简单） | 100-200ms |
| 中（展开/收起） | 200-300ms |
| 长（复杂） | 300-500ms |

#### 组件尺寸

| 组件 | 高度 | 最小宽度 |
|------|------|----------|
| 按钮 | 40dp | 64dp |
| FAB | 56dp | 56dp |
| 文本字段 | 56dp | 280dp |
| 应用栏 | 64dp | - |
| 底部导航 | 80dp | - |

### 反模式（必须避免）

#### UI 反模式
- 底部导航项超过 5 个
- 同一屏幕上多个 FAB
- 触摸目标小于 48dp
- 间距不一致（非 8dp 的倍数）
- 缺少暗色主题支持
- 带有颜色背景的文本未进行对比度检查

#### 性能反模式
- 启动时间 > 2 秒且无进度指示器
- 帧率 < 60 FPS（> 16ms 每帧）
- 碰撞率 > 1.09%（Google Play 阈值）
- ANR 率 > 0.47%（Google Play 阈值）

#### 可访问性反模式
- 交互元素缺少 contentDescription
- 标签中包含元素类型（例如，“保存按钮”而不是“保存”）
- 儿童应用中使用复杂手势
- 为非阅读者使用纯文本按钮

### 审查清单

- [ ] 8dp 间距网格符合要求
- [ ] 48dp 最小触摸目标
- [ ] 正确使用排版比例
- [ ] 颜色对比符合要求（文本 4.5:1+）
- [ ] 暗色主题支持
- [ ] 所有交互元素都有 contentDescription
- [ ] 启动时间 < 2 秒或显示进度
- [ ] 视觉风格与应用类别匹配

### 设计参考

| 主题 | 参考 |
|------|------|
| 颜色、排版、间距、形状 | [视觉设计](references/visual-design.md) |
| 动画和过渡 | [运动系统](references/motion-system.md) |
| 可访问性指南 | [可访问性](references/accessibility.md) |
| 大屏幕和折叠屏 | [自适应屏幕](references/adaptive-screens.md) |
| Android Vitals 和性能 | [性能和稳定性](references/performance-stability.md) |
| 隐私和安全 | [隐私和安全](references/privacy-security.md) |
| 音频、视频、通知 | [功能需求](references/functional-requirements.md) |
| 按类别划分的应用风格 | [设计风格指南](references/design-style-guide.md) |

---

## 8. 测试

> **注意**：仅在用户明确要求测试时才添加测试依赖。

经过良好测试的 Android 应用使用分层测试：快速本地单元测试用于逻辑，仪器测试用于 UI 和集成，以及 Gradle 管理设备在任何机器上（包括 CI）可重复运行模拟器。

### 8.1 测试依赖

在添加测试依赖之前，检查项目的现有版本以避免冲突：

1. 检查 `gradle/libs.versions.toml` — 如果存在，使用项目的版本目录样式添加测试依赖
2. 检查现有的 `build.gradle.kts` 以查找已固定的依赖版本
3. 使用下表匹配版本系列

**版本对齐规则**：

| 测试依赖 | 必须与...对齐 | 如何检查 |
|----------|----------------|----------|
| `kotlinx-coroutines-test` | 项目的 `kotlinx-coroutines-core` 版本 | 在构建文件或版本目录中搜索 `kotlinx-coroutines` |
| `compose-ui-test-junit4` | 项目的 Compose BOM 或 `compose-compiler` | 在构建文件中搜索 `compose-bom` 或 `compose.compiler` |
| `espresso-*` | 所有 Espresso 工件必须使用相同版本 | 在构建文件中搜索 `espresso` |
| `androidx.test:runner`, `rules`, `ext:junit` | 应使用兼容的 AndroidX 测试版本 | 在构建文件中搜索 `androidx.test` |
| `mockk` | 必须支持项目的 Kotlin 版本 | 在根 `build.gradle.kts` 或版本目录中检查 `kotlin` 版本 |

**依赖参考** — 仅添加您需要的组：

```kotlin
dependencies {
    // --- 本地单元测试 (src/test/) ---
    testImplementation("junit:junit:<version>")                          // 4.13.2+
    testImplementation("org.robolectric:robolectric:<version>")          // 4.16.1+
    testImplementation("io.mockk:mockk:<version>")                      // 匹配 Kotlin 版本
    testImplementation("org.jetbrains.kotlinx:kotlinx-coroutines-test:<version>")  // 匹配 coroutines-core
    testImplementation("androidx.arch.core:core-testing:<version>")      // LiveData 的 InstantTaskExecutorRule
    testImplementation("app.cash.turbine:turbine:<version>")             // Flow/StateFlow 测试

    // --- 仪器测试 (src/androidTest/) ---
    androidTestImplementation("androidx.test.ext:junit:<version>")
    androidTestImplementation("androidx.test:runner:<version>")
    androidTestImplementation("androidx.test:rules:<version>")
    androidTestImplementation("androidx.test.espresso:espresso-core:<version>")
    androidTestImplementation("androidx.test.espresso:espresso-contrib:<version>")   // RecyclerView, Drawer
    androidTestImplementation("androidx.test.espresso:espresso-intents:<version>")   // Intent 验证
    androidTestImplementation("androidx.test.espresso:espresso-idling-resource:<version>")
    androidTestImplementation("androidx.test.uiautomator:uiautomator:<version>")

    // --- Compose UI 测试（仅当项目使用 Compose 时）---
    androidTestImplementation("androidx.compose.ui:ui-test-junit4")      // 从 Compose BOM 获取版本
    debugImplementation("androidx.compose.ui:ui-test-manifest")          // 创建 ComposeRule 所需
}
```

> **注意**：如果项目使用 Compose BOM，`ui-test-junit4` 和 `ui-test-manifest` 不需要显式版本 — BOM 管理它们。

在 `android` 块中启用 Robolectric 资源支持：

```kotlin
android {
    testOptions {
        unitTests.isIncludeAndroidResources = true  // Robolectric 所需
    }
}
```

### 8.2 按层级测试

| 层级 | 位置 | 运行在 | 速度 | 用于 |
|------|------|--------|------|------|
| 单元 (JUnit) | `src/test/` | JVM | ~ms | ViewModels, repos, mappers, validators |
| 单元 + Robolectric | `src/test/` | JVM + 模拟 Android | ~100ms | 需要上下文、资源、SharedPrefs 的代码 |
| Compose UI (本地) | `src/test/` | JVM + Robolectric | ~100ms | Composable 渲染和交互 |
| Espresso | `src/androidTest/` | 设备/模拟器 | ~秒 | 基于视图的 UI 流程、Intents、DB 集成 |
| Compose UI (设备) | `src/androidTest/` | 设备/模拟器 | ~秒 | 带有真实渲染的完整 Compose UI 流程 |
| UI Automator | `src/androidTest/` | 设备/模拟器 | ~秒 | 系统对话框、通知、多应用 |
| 管理设备 | `src/androidTest/` | Gradle 管理的 AVD | ~分钟（首次运行） | CI、跨 API 级别矩阵测试 |

见 [测试](references/testing.md) 获取详细示例、代码模式和 Gradle 管理设备配置。
